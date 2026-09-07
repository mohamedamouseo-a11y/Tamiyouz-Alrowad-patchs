#!/usr/bin/env bash
set -euo pipefail

WP_ROOT="${WP_ROOT:-$(pwd)}"
WP_CONTENT="$WP_ROOT/wp-content"
PLUGIN_FILE="$WP_CONTENT/plugins/tamiyouz-developer-hub/tamiyouz-developer-hub.php"

if [[ ! -f "$WP_ROOT/wp-config.php" || ! -d "$WP_CONTENT" ]]; then
  echo "ERROR: invalid WordPress root: $WP_ROOT" >&2
  exit 2
fi
if [[ ! -f "$PLUGIN_FILE" ]]; then
  echo "ERROR: Developer Hub plugin not found: $PLUGIN_FILE" >&2
  exit 3
fi

python3 - "$PLUGIN_FILE" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')

required = [
    "const VERSION = '1.5.0';",
    "private function version_control_allowed",
    "private function version_control_pathspecs",
    "bootstrapBranchRepair",
    "Generic secret detection is intentionally high-confidence only",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f"ERROR: V1.5 marker missing; refusing unknown revision: {marker}")

s = s.replace(" * Version: 1.5.0", " * Version: 1.6.0", 1)
s = s.replace("const VERSION = '1.5.0';", "const VERSION = '1.6.0';", 1)


def replace_block(text, start_marker, end_marker, new_block):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: start marker missing: {start_marker}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: end marker missing: {end_marker}")
    return text[:start] + new_block.rstrip() + "\n\n" + text[end:]

remote_helpers = r'''    private function remote_allowed_paths($remote_ref) {
        $tree = $this->git(['ls-tree', '-r', '--name-only', $remote_ref], '', true);
        if (is_wp_error($tree)) return $tree;
        if (($tree['exit'] ?? 1) !== 0 || trim($tree['stdout']) === '') return [];
        $allowed = [];
        foreach (preg_split('/\R/', trim($tree['stdout'])) as $path) {
            $path = trim($path);
            if ($path !== '' && $this->version_control_allowed($path)) {
                $allowed[] = $path;
                if (count($allowed) >= 50) break;
            }
        }
        return $allowed;
    }

    private function histories_related($remote_ref) {
        $head = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);
        if (is_wp_error($head) || ($head['exit'] ?? 1) !== 0) return false;
        $base = $this->git(['merge-base', 'HEAD', $remote_ref], '', true);
        return !is_wp_error($base) && ($base['exit'] ?? 1) === 0 && trim($base['stdout']) !== '';
    }'''

marker = "    private function ahead_behind($remote_ref) {"
pos = s.find(marker)
if pos < 0:
    raise SystemExit('ERROR: ahead_behind marker missing')
if "private function remote_allowed_paths(" not in s:
    s = s[:pos] + remote_helpers + "\n\n" + s[pos:]

new_ahead = r'''    private function ahead_behind($remote_ref) {
        $local_head = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);
        $has_head = !is_wp_error($local_head) && ($local_head['exit'] ?? 1) === 0;
        $remote_exists = $this->remote_exists($remote_ref);
        if (!$has_head) {
            return [
                'localAhead' => 0,
                'remoteAhead' => 0,
                'hasHead' => false,
                'remoteExists' => $remote_exists,
                'historiesRelated' => false,
            ];
        }
        if (!$remote_exists) {
            return [
                'localAhead' => 1,
                'remoteAhead' => 0,
                'hasHead' => true,
                'remoteExists' => false,
                'historiesRelated' => true,
            ];
        }
        $related = $this->histories_related($remote_ref);
        if (!$related) {
            return [
                'localAhead' => 0,
                'remoteAhead' => 0,
                'hasHead' => true,
                'remoteExists' => true,
                'historiesRelated' => false,
            ];
        }
        $count = $this->git(['rev-list', '--left-right', '--count', 'HEAD...' . $remote_ref], '', true);
        if (is_wp_error($count) || ($count['exit'] ?? 1) !== 0) {
            return [
                'localAhead' => 0,
                'remoteAhead' => 0,
                'hasHead' => true,
                'remoteExists' => true,
                'historiesRelated' => true,
            ];
        }
        $parts = preg_split('/\s+/', trim($count['stdout']));
        return [
            'localAhead' => intval($parts[0] ?? 0),
            'remoteAhead' => intval($parts[1] ?? 0),
            'hasHead' => true,
            'remoteExists' => true,
            'historiesRelated' => true,
        ];
    }'''

s = replace_block(
    s,
    "    private function ahead_behind($remote_ref) {",
    "    private function remote_exists($remote_ref) {",
    new_ahead,
)

# Add explicit legacy-remote detection after counts/local files are known.
needle = """        $remote_files = $counts['remoteExists'] ? $this->remote_changed_files($remote_ref) : [];\n        foreach ($local_files as $file) {\n"""
replacement = """        $remote_files = ($counts['remoteExists'] && !empty($counts['historiesRelated'])) ? $this->remote_changed_files($remote_ref) : [];\n        $legacy_remote_adoption = false;\n        $legacy_remote_allowed = [];\n        if ($counts['remoteExists'] && empty($counts['historiesRelated'])) {\n            $legacy_remote_allowed = $this->remote_allowed_paths($remote_ref);\n            if (is_wp_error($legacy_remote_allowed)) return $legacy_remote_allowed;\n            if (!empty($legacy_remote_allowed)) {\n                $blocked[] = [\n                    'path' => '(remote history)',\n                    'reason' => 'GitHub already contains files inside the managed WordPress scope. Manual reconciliation is required before push.',\n                ];\n            } else {\n                $legacy_remote_adoption = true;\n            }\n        }\n        foreach ($local_files as $file) {\n"""
if needle in s:
    s = s.replace(needle, replacement, 1)
elif replacement not in s:
    raise SystemExit('ERROR: legacy remote insertion target missing')

# Replace expected-action decision block.
start = s.find("        $expected = 'noop';")
end = s.find("        if ($blocked) $expected = 'blocked';", start)
if start < 0 or end < 0:
    raise SystemExit('ERROR: expected-action block markers missing')
end_line = s.find("\n", end)
old_block = s[start:end_line+1]
new_block = r'''        $expected = 'noop';
        if ($legacy_remote_adoption) {
            if ($action === 'pull') {
                $blocked[] = ['path' => '(history)', 'reason' => 'Remote history is unrelated to this WordPress repository. Pull is not safe; use reviewed push/sync to preserve legacy history and publish the current managed source.'];
                $expected = 'blocked';
            } elseif ($dirty) {
                $expected = 'commit_merge_history_push';
            } else {
                $expected = 'merge_history_push';
            }
        } elseif ($action === 'push') {
            if ($remote_ahead > 0) {
                $blocked[] = ['path' => '(history)', 'reason' => 'GitHub contains commits that are not local. Pull/review first.'];
                $expected = 'blocked';
            } elseif ($dirty) $expected = 'commit_and_push';
            elseif ($local_ahead > 0) $expected = 'push';
        } elseif ($action === 'pull') {
            if ($dirty) {
                $blocked[] = ['path' => '(working tree)', 'reason' => 'Local changes must be committed or removed before pull.'];
                $expected = 'blocked';
            } elseif ($local_ahead > 0 && $remote_ahead > 0) {
                $blocked[] = ['path' => '(history)', 'reason' => 'Local and GitHub histories both changed. Manual reconciliation is required.'];
                $expected = 'blocked';
            } elseif ($remote_ahead > 0) $expected = 'fast_forward';
        } else {
            if ($remote_ahead > 0 && ($dirty || $local_ahead > 0)) {
                $blocked[] = ['path' => '(history)', 'reason' => 'Changes exist both locally and on GitHub. Resolve manually before full sync.'];
                $expected = 'blocked';
            } elseif ($remote_ahead > 0) $expected = 'fast_forward';
            elseif ($dirty) $expected = 'commit_and_push';
            elseif ($local_ahead > 0) $expected = 'push';
        }
        if ($blocked) $expected = 'blocked';
'''
s = s[:start] + new_block + s[end_line+1:]

# Add history-adoption metadata to reviewed fingerprint.
old_fp = """            'bootstrapBranchRepair' => $bootstrap_branch_repair,\n            'files' => $files, 'blocked' => $blocked,\n"""
new_fp = """            'bootstrapBranchRepair' => $bootstrap_branch_repair,\n            'legacyRemoteAdoption' => $legacy_remote_adoption,\n            'legacyRemoteAllowedPaths' => $legacy_remote_allowed,\n            'files' => $files, 'blocked' => $blocked,\n"""
if old_fp in s:
    s = s.replace(old_fp, new_fp, 1)
elif new_fp not in s:
    raise SystemExit('ERROR: fingerprint legacy metadata target missing')

# Teach execution how to preserve unrelated remote history without importing its old tree.
needle_exec = """        if ($expected === 'fast_forward') {\n            $logs[] = ['type' => 'info', 'message' => 'Applying fast-forward update from GitHub.'];\n            $merge = $this->git(['merge', '--ff-only', $remote_ref], $token, false, 180);\n            if (is_wp_error($merge)) return $merge;\n            $logs[] = ['type' => 'success', 'message' => 'GitHub updates pulled successfully.'];\n        } else {\n            if ($expected === 'commit_and_push') {\n"""
replacement_exec = """        if ($expected === 'fast_forward') {\n            $logs[] = ['type' => 'info', 'message' => 'Applying fast-forward update from GitHub.'];\n            $merge = $this->git(['merge', '--ff-only', $remote_ref], $token, false, 180);\n            if (is_wp_error($merge)) return $merge;\n            $logs[] = ['type' => 'success', 'message' => 'GitHub updates pulled successfully.'];\n        } else {\n            if (in_array($expected, ['commit_and_push', 'commit_merge_history_push'], true)) {\n"""
if needle_exec in s:
    s = s.replace(needle_exec, replacement_exec, 1)
elif replacement_exec not in s:
    raise SystemExit('ERROR: execute commit branch target missing')

# Insert legacy merge just before push.
push_needle = """            $push = $this->git(['push', self::REMOTE, 'HEAD:refs/heads/' . $branch], $token, false, 240);\n"""
push_replacement = """            if (in_array($expected, ['merge_history_push', 'commit_merge_history_push'], true)) {\n                $merge_history = $this->git([\n                    '-c', 'user.name=Tamiyouz Developer Hub',\n                    '-c', 'user.email=developer-hub@tamiyouz.local',\n                    'merge', '--allow-unrelated-histories', '-s', 'ours', '--no-edit', $remote_ref,\n                ], '', false, 180);\n                if (is_wp_error($merge_history)) return $merge_history;\n                $logs[] = ['type' => 'success', 'message' => 'Legacy GitHub history preserved without importing obsolete remote files into the managed WordPress tree.'];\n            }\n            $push = $this->git(['push', self::REMOTE, 'HEAD:refs/heads/' . $branch], $token, false, 240);\n"""
if push_needle in s:
    s = s.replace(push_needle, push_replacement, 1)
elif push_replacement not in s:
    raise SystemExit('ERROR: push insertion target missing')

p.write_text(s, encoding='utf-8')
PY

php -l "$PLUGIN_FILE"

grep -Fq "const VERSION = '1.6.0';" "$PLUGIN_FILE"
grep -Fq "private function remote_allowed_paths" "$PLUGIN_FILE"
grep -Fq "private function histories_related" "$PLUGIN_FILE"
grep -Fq "commit_merge_history_push" "$PLUGIN_FILE"
grep -Fq "Legacy GitHub history preserved without importing obsolete remote files" "$PLUGIN_FILE"
grep -Fq "--allow-unrelated-histories" "$PLUGIN_FILE"

echo "PLUGIN_VERSION=1.6.0"
echo "UNRELATED_HISTORY_DETECTION=YES"
echo "LEGACY_REMOTE_SCOPE_GUARD=YES"
echo "LEGACY_HISTORY_PRESERVATION=YES"
echo "FORCE_PUSH_USED=NO"
echo "GIT_MUTATIONS_BY_PATCH=NONE"
echo "FRONT_END_CHANGED=NO"
echo "STATUS=READY"
