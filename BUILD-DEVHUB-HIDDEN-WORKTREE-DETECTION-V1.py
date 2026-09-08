#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

PATCH_ID = "DEVHUB_HIDDEN_WORKTREE_DETECTION_V1"
SOURCE_VERSION = "1.6.0"
TARGET_VERSION = "1.6.1"
MARKER = "TAM_DEVHUB_HIDDEN_WORKTREE_V1"

HELPERS = r'''
    // TAM_DEVHUB_HIDDEN_WORKTREE_V1
    private function worktree_blob_hash($full, $algo = 'sha1') {
        if (!in_array($algo, ['sha1', 'sha256'], true)) return '';
        if (is_link($full)) {
            $target = readlink($full);
            if (!is_string($target)) return '';
            return hash($algo, 'blob ' . strlen($target) . "\0" . $target);
        }
        if (!is_file($full) || !is_readable($full)) return '';
        $size = filesize($full);
        if ($size === false) return '';
        $ctx = hash_init($algo);
        hash_update($ctx, 'blob ' . $size . "\0");
        if (!hash_update_file($ctx, $full)) return '';
        return hash_final($ctx);
    }

    private function hidden_tracked_changes() {
        $pathspecs = $this->version_control_pathspecs();
        $flag_args = array_merge(['ls-files', '-v', '-z', '--'], $pathspecs);
        $stage_args = array_merge(['ls-files', '-s', '-z', '--'], $pathspecs);
        $flagged = $this->git($flag_args, '', true);
        $staged = $this->git($stage_args, '', true);
        if (is_wp_error($flagged) || is_wp_error($staged)) return [];
        if (($flagged['exit'] ?? 1) !== 0 || ($staged['exit'] ?? 1) !== 0) return [];

        $index = [];
        foreach (explode("\0", (string) $staged['stdout']) as $entry) {
            if ($entry === '') continue;
            if (!preg_match('/^[0-7]{6}\s+([0-9a-fA-F]{40,64})\s+[0-3]\t(.*)$/s', $entry, $m)) continue;
            $path = $m[2];
            if (!$this->version_control_allowed($path)) continue;
            $index[$path] = strtolower($m[1]);
        }

        $files = [];
        foreach (explode("\0", (string) $flagged['stdout']) as $entry) {
            if ($entry === '' || strlen($entry) < 3) continue;
            $flag = substr($entry, 0, 1);
            $path = substr($entry, 2);
            if ($path === '' || !$this->version_control_allowed($path)) continue;

            // git ls-files -v lower-cases tags for assume-unchanged entries;
            // S/s identifies skip-worktree. These flags can hide real FTP edits
            // from ordinary git status, so compare worktree content to the index.
            $lowercase = ($flag >= 'a' && $flag <= 'z');
            $skip_worktree = strtoupper($flag) === 'S';
            if (!$lowercase && !$skip_worktree) continue;
            if (!isset($index[$path])) continue;

            $full = $this->repo_root() . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $path);
            if (!file_exists($full) && !is_link($full)) {
                $files[] = [
                    'status' => 'D',
                    'path' => $path,
                    'direction' => 'local',
                    'trackingFlag' => $flag,
                ];
                continue;
            }

            $index_blob = $index[$path];
            $algo = strlen($index_blob) === 64 ? 'sha256' : 'sha1';
            $worktree_blob = $this->worktree_blob_hash($full, $algo);
            if ($worktree_blob !== '' && !hash_equals($index_blob, strtolower($worktree_blob))) {
                $files[] = [
                    'status' => 'M',
                    'path' => $path,
                    'direction' => 'local',
                    'trackingFlag' => $flag,
                ];
            }
        }
        return $files;
    }

    private function normalize_hidden_tracking_flags($files) {
        $paths = [];
        foreach ((array) $files as $file) {
            if (!is_array($file) || ($file['direction'] ?? '') !== 'local') continue;
            if (empty($file['trackingFlag'])) continue;
            $path = (string) ($file['path'] ?? '');
            if ($path === '' || !$this->version_control_allowed($path)) continue;
            $paths[$path] = true;
        }
        if (!$paths) return 0;

        foreach (array_keys($paths) as $path) {
            $assume = $this->git(['update-index', '--no-assume-unchanged', '--', $path], '', true);
            if (is_wp_error($assume) || ($assume['exit'] ?? 1) !== 0) {
                return new WP_Error('tracking_flag_repair_failed', 'Unable to normalize assume-unchanged state for reviewed file: ' . $path, ['status' => 409]);
            }
            $skip = $this->git(['update-index', '--no-skip-worktree', '--', $path], '', true);
            if (is_wp_error($skip) || ($skip['exit'] ?? 1) !== 0) {
                return new WP_Error('tracking_flag_repair_failed', 'Unable to normalize skip-worktree state for reviewed file: ' . $path, ['status' => 409]);
            }
        }
        return count($paths);
    }

'''

MERGE_HIDDEN = r'''        $hidden = $this->hidden_tracked_changes();
        $seen = [];
        foreach ($files as $file) {
            if (!empty($file['path'])) $seen[$file['path']] = true;
        }
        foreach ($hidden as $file) {
            if (empty($file['path']) || isset($seen[$file['path']])) continue;
            $files[] = $file;
            $seen[$file['path']] = true;
        }
        return $files;
'''

NORMALIZE_EXECUTE = r'''                $normalized_flags = $this->normalize_hidden_tracking_flags($preview['files'] ?? []);
                if (is_wp_error($normalized_flags)) return $normalized_flags;
                if ($normalized_flags > 0) {
                    $logs[] = ['type' => 'info', 'message' => 'Normalized hidden Git tracking flags for ' . $normalized_flags . ' reviewed managed file(s).'];
                }
                $gitignore = $this->write_devhub_gitignore();
'''


def transform(source: str) -> str:
    if MARKER in source:
        raise SystemExit("Source already contains patch marker; refusing duplicate application.")
    if "Version: 1.6.0" not in source or "const VERSION = '1.6.0';" not in source:
        raise SystemExit("Source is not expected Developer Hub v1.6.0 baseline.")
    required = [
        "private function changed_files() {",
        "$args = array_merge(['status', '--porcelain=v1', '-z', '--untracked-files=all', '--'], $this->version_control_pathspecs());",
        "if ($raw === '') return [];",
        "private function remote_changed_files($remote_ref) {",
        "if (in_array($expected, ['commit_and_push', 'commit_merge_history_push'], true)) {",
        "$gitignore = $this->write_devhub_gitignore();",
    ]
    for needle in required:
        if needle not in source:
            raise SystemExit(f"Required baseline signature missing: {needle}")

    out = source.replace("Version: 1.6.0", "Version: 1.6.1", 1)
    out = out.replace("const VERSION = '1.6.0';", "const VERSION = '1.6.1';", 1)

    anchor = "    private function changed_files() {\n"
    out = out.replace(anchor, HELPERS + anchor, 1)

    old_empty = "        if ($raw === '') return [];\n        $parts = explode(\"\\0\", $raw);\n"
    new_empty = "        $parts = $raw === '' ? [] : explode(\"\\0\", $raw);\n"
    if old_empty not in out:
        raise SystemExit("Unable to patch changed_files empty-status branch.")
    out = out.replace(old_empty, new_empty, 1)

    return_anchor = "        return $files;\n    }\n\n    private function remote_changed_files($remote_ref) {"
    if return_anchor not in out:
        raise SystemExit("Unable to locate changed_files return anchor.")
    out = out.replace(return_anchor, MERGE_HIDDEN + "    }\n\n    private function remote_changed_files($remote_ref) {", 1)

    execute_anchor = "            if (in_array($expected, ['commit_and_push', 'commit_merge_history_push'], true)) {\n                $gitignore = $this->write_devhub_gitignore();\n"
    if execute_anchor not in out:
        raise SystemExit("Unable to locate commit-and-push execution anchor.")
    out = out.replace(
        execute_anchor,
        "            if (in_array($expected, ['commit_and_push', 'commit_merge_history_push'], true)) {\n" + NORMALIZE_EXECUTE,
        1,
    )

    checks = {
        "target_version": "Version: 1.6.1" in out and "const VERSION = '1.6.1';" in out,
        "marker_once": out.count(MARKER) == 1,
        "hidden_detector": "private function hidden_tracked_changes()" in out,
        "flag_normalizer": "private function normalize_hidden_tracking_flags($files)" in out,
        "status_no_early_empty_return": "if ($raw === '') return [];" not in out,
        "hidden_merge": "$hidden = $this->hidden_tracked_changes();" in out,
        "execute_normalize": "$this->normalize_hidden_tracking_flags($preview['files'] ?? [])" in out,
        "scope_preserved": "return ['.gitignore', 'themes/thegem-elementor', 'plugins/tamiyouz-developer-hub'];" in out,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise SystemExit("Post-transform guard failed: " + ", ".join(failed))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--manifest')
    args = ap.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)
    source = source_path.read_text(encoding='utf-8')
    result = transform(source)
    output_path.write_text(result, encoding='utf-8')

    manifest = {
        'patch': PATCH_ID,
        'source_version': SOURCE_VERSION,
        'target_version': TARGET_VERSION,
        'marker': MARKER,
        'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'output_sha256': hashlib.sha256(result.encode()).hexdigest(),
        'files_changed': ['plugins/tamiyouz-developer-hub/tamiyouz-developer-hub.php'],
        'git_mutations_by_patch_runner': False,
        'preview_behavior': 'read-only hidden tracked change detection via ls-files metadata + worktree blob hashing',
        'execute_behavior': 'clear assume-unchanged/skip-worktree only for reviewed hidden local files immediately before normal staging',
        'managed_scope_unchanged': True,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
