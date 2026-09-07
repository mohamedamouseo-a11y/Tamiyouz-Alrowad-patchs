#!/usr/bin/env bash
set -euo pipefail

WP_ROOT="${WP_ROOT:-$(pwd)}"
WP_CONTENT="$WP_ROOT/wp-content"
PLUGIN_FILE="$WP_CONTENT/plugins/tamiyouz-developer-hub/tamiyouz-developer-hub.php"
GITIGNORE="$WP_CONTENT/.gitignore"

if [[ ! -f "$WP_ROOT/wp-config.php" || ! -d "$WP_CONTENT" ]]; then
  echo "ERROR: WP_ROOT does not look like the Tamiyouz WordPress root: $WP_ROOT" >&2
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
    "const VERSION = '1.3.0';",
    ": WP_CONTENT_DIR;",
    "recoveredPartialInit",
    "A repository with zero branches is a valid first-bootstrap target.",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f"ERROR: V1.3 marker missing; refusing unknown revision: {marker}")

s = s.replace(" * Version: 1.3.0", " * Version: 1.4.0", 1)
s = s.replace("const VERSION = '1.3.0';", "const VERSION = '1.4.0';", 1)


def replace_block(text, start_marker, end_marker, new_block):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: start marker not found: {start_marker}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: end marker not found: {end_marker}")
    return text[:start] + new_block.rstrip() + "\n\n" + text[end:]

allowed_helpers = r'''    private function version_control_allowed($path) {
        $normalized = ltrim(str_replace('\\\\', '/', (string) $path), '/');
        if ($normalized === '.gitignore') return true;
        if (strpos($normalized, 'themes/thegem-elementor/') === 0) return true;
        if (strpos($normalized, 'plugins/tamiyouz-developer-hub/') === 0) return true;
        if ($normalized === 'mu-plugins' || strpos($normalized, 'mu-plugins/') === 0) return true;
        return false;
    }

    private function version_control_pathspecs() {
        $paths = ['.gitignore', 'themes/thegem-elementor', 'plugins/tamiyouz-developer-hub'];
        if (is_dir($this->repo_root() . DIRECTORY_SEPARATOR . 'mu-plugins')) {
            $paths[] = 'mu-plugins';
        }
        return $paths;
    }'''

# Insert helpers before changed_files if not already present.
if "private function version_control_allowed(" not in s:
    marker = "    private function changed_files() {"
    pos = s.find(marker)
    if pos < 0:
        raise SystemExit("ERROR: changed_files marker not found")
    s = s[:pos] + allowed_helpers + "\n\n" + s[pos:]

new_changed = r'''    private function changed_files() {
        $status = $this->git(['status', '--porcelain=v1', '-z', '--untracked-files=all', '--', '.gitignore', 'themes/thegem-elementor', 'plugins/tamiyouz-developer-hub', 'mu-plugins'], '', true);
        if (is_wp_error($status)) return $status;
        $raw = $status['stdout'];
        if ($raw === '') return [];
        $parts = explode("\\0", $raw);
        $files = [];
        for ($i = 0; $i < count($parts); $i++) {
            $entry = $parts[$i];
            if ($entry === '' || strlen($entry) < 4) continue;
            $code = substr($entry, 0, 2);
            $path = substr($entry, 3);
            if ($code[0] === 'R' || $code[0] === 'C') {
                $original = $path;
                $next = $parts[$i + 1] ?? '';
                if ($next !== '') {
                    $path = $next;
                    $i++;
                }
                if (!$this->version_control_allowed($path)) continue;
                $files[] = ['status' => trim($code), 'path' => $path, 'originalPath' => $original, 'direction' => 'local'];
            } else {
                if (!$this->version_control_allowed($path)) continue;
                $files[] = ['status' => trim($code) ?: 'M', 'path' => $path, 'direction' => 'local'];
            }
        }
        return $files;
    }'''

s = replace_block(
    s,
    "    private function changed_files() {",
    "    private function remote_changed_files($remote_ref) {",
    new_changed,
)

new_remote_changed = r'''    private function remote_changed_files($remote_ref) {
        $head = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);
        if (is_wp_error($head) || ($head['exit'] ?? 1) !== 0) return [];
        $diff = $this->git(['diff', '--name-status', '-z', 'HEAD..' . $remote_ref, '--', '.gitignore', 'themes/thegem-elementor', 'plugins/tamiyouz-developer-hub', 'mu-plugins'], '', true);
        if (is_wp_error($diff) || ($diff['exit'] ?? 1) !== 0 || $diff['stdout'] === '') return [];
        $parts = explode("\\0", $diff['stdout']);
        $files = [];
        for ($i = 0; $i < count($parts);) {
            $status = trim($parts[$i++] ?? '');
            if ($status === '') continue;
            $path = $parts[$i++] ?? '';
            if ($path === '') continue;
            if ($status[0] === 'R' || $status[0] === 'C') {
                $new = $parts[$i++] ?? '';
                if ($new !== '' && $this->version_control_allowed($new)) {
                    $files[] = ['status' => $status, 'path' => $new, 'originalPath' => $path, 'direction' => 'remote'];
                }
            } elseif ($this->version_control_allowed($path)) {
                $files[] = ['status' => $status, 'path' => $path, 'direction' => 'remote'];
            }
        }
        return $files;
    }'''

s = replace_block(
    s,
    "    private function remote_changed_files($remote_ref) {",
    "    private function blocked_path_reason($path) {",
    new_remote_changed,
)

new_gitignore = r'''    private function write_devhub_gitignore() {
        $root = $this->repo_root();
        $path = $root . DIRECTORY_SEPARATOR . '.gitignore';
        $begin = '# BEGIN Tamiyouz Developer Hub managed scope';
        $end = '# END Tamiyouz Developer Hub managed scope';
        $rules = $begin . "\\n"
            . "/*\\n"
            . "!/.gitignore\\n"
            . "!/themes/\\n"
            . "/themes/*\\n"
            . "!/themes/thegem-elementor/\\n"
            . "!/themes/thegem-elementor/**\\n"
            . "!/plugins/\\n"
            . "/plugins/*\\n"
            . "!/plugins/tamiyouz-developer-hub/\\n"
            . "!/plugins/tamiyouz-developer-hub/**\\n"
            . "!/mu-plugins/\\n"
            . "!/mu-plugins/**\\n"
            . "/uploads/\\n/cache/\\n/upgrade/\\n/backups/\\n/ai1wm-backups/\\n/wflogs/\\n/boost-cache/\\n"
            . "*.sql\\n*.sql.gz\\n*.log\\n.env\\n.env.*\\n*.pem\\n*.key\\n*.p12\\n*.pfx\\n.DS_Store\\n"
            . $end . "\\n";

        $current = file_exists($path) ? (string) file_get_contents($path) : '';

        // Remove every older Developer Hub managed safety block so stale V1/V1.1
        // rules cannot expand the working tree again.
        $current = preg_replace('/\\n?# Tamiyouz Developer Hub safety rules.*?(?=\\n# BEGIN Tamiyouz Developer Hub managed scope|\\z)/s', '', $current);
        $current = preg_replace('/\\n?# BEGIN Tamiyouz Developer Hub managed scope.*?# END Tamiyouz Developer Hub managed scope\\n?/s', '', $current);
        $next = rtrim((string) $current) . ($current !== '' ? "\\n\\n" : '') . $rules;
        $written = file_put_contents($path, $next, LOCK_EX);
        if ($written === false) {
            return new WP_Error('gitignore_write_failed', 'Unable to write Developer Hub Git scope rules.', ['status' => 500]);
        }
        return true;
    }'''

s = replace_block(
    s,
    "    private function write_devhub_gitignore() {",
    "    private function require_ready() {",
    new_gitignore,
)

# Make init propagate gitignore repair errors.
old = "        $this->write_devhub_gitignore();\n\n        $token = $this->decrypt_token();"
new = "        $gitignore = $this->write_devhub_gitignore();\n        if (is_wp_error($gitignore)) return $gitignore;\n\n        $token = $this->decrypt_token();"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("ERROR: init gitignore call target not found")

# Restrict staging to the exact allowlist instead of `git add -A .`.
old_add = "                $add = $this->git(['add', '-A', '--', '.'], '', false, 180);"
new_add = "                $add_args = array_merge(['add', '-A', '--'], $this->version_control_pathspecs());\n                $add = $this->git($add_args, '', false, 180);"
if old_add in s:
    s = s.replace(old_add, new_add, 1)
elif new_add not in s:
    raise SystemExit("ERROR: git add target not found")

# Ensure execute also repairs the managed ignore block before staging.
old_exec = "                $this->write_devhub_gitignore();\n                $add_args = array_merge(['add', '-A', '--'], $this->version_control_pathspecs());"
new_exec = "                $gitignore = $this->write_devhub_gitignore();\n                if (is_wp_error($gitignore)) return $gitignore;\n                $add_args = array_merge(['add', '-A', '--'], $this->version_control_pathspecs());"
if old_exec in s:
    s = s.replace(old_exec, new_exec, 1)
elif new_exec not in s:
    raise SystemExit("ERROR: execute gitignore repair target not found")

p.write_text(s, encoding='utf-8')
PY

# Repair the existing wp-content/.gitignore now. This is a file-scope repair only;
# it performs no git init/add/commit/push/pull/reset/stash operation.
python3 - "$GITIGNORE" <<'PY'
from pathlib import Path
import re, sys
p = Path(sys.argv[1])
current = p.read_text(encoding='utf-8') if p.exists() else ''
begin = '# BEGIN Tamiyouz Developer Hub managed scope'
end = '# END Tamiyouz Developer Hub managed scope'
rules = '''# BEGIN Tamiyouz Developer Hub managed scope
/*
!/.gitignore
!/themes/
/themes/*
!/themes/thegem-elementor/
!/themes/thegem-elementor/**
!/plugins/
/plugins/*
!/plugins/tamiyouz-developer-hub/
!/plugins/tamiyouz-developer-hub/**
!/mu-plugins/
!/mu-plugins/**
/uploads/
/cache/
/upgrade/
/backups/
/ai1wm-backups/
/wflogs/
/boost-cache/
*.sql
*.sql.gz
*.log
.env
.env.*
*.pem
*.key
*.p12
*.pfx
.DS_Store
# END Tamiyouz Developer Hub managed scope
'''
current = re.sub(r'\n?# Tamiyouz Developer Hub safety rules.*?(?=\n# BEGIN Tamiyouz Developer Hub managed scope|\Z)', '', current, flags=re.S)
current = re.sub(r'\n?# BEGIN Tamiyouz Developer Hub managed scope.*?# END Tamiyouz Developer Hub managed scope\n?', '', current, flags=re.S)
next_text = current.rstrip() + ('\n\n' if current.strip() else '') + rules
p.write_text(next_text, encoding='utf-8')
PY

php -l "$PLUGIN_FILE"

if ! grep -Fq "const VERSION = '1.4.0';" "$PLUGIN_FILE"; then
  echo "ERROR: V1.4 version marker missing" >&2
  exit 4
fi
if ! grep -Fq "private function version_control_allowed" "$PLUGIN_FILE"; then
  echo "ERROR: strict allowlist helper missing" >&2
  exit 5
fi
if ! grep -Fq "version_control_pathspecs" "$PLUGIN_FILE"; then
  echo "ERROR: strict stage pathspecs missing" >&2
  exit 6
fi
if ! grep -Fq "BEGIN Tamiyouz Developer Hub managed scope" "$GITIGNORE"; then
  echo "ERROR: managed .gitignore scope missing" >&2
  exit 7
fi
if ! grep -Fq "/wflogs/" "$GITIGNORE" || ! grep -Fq "/boost-cache/" "$GITIGNORE"; then
  echo "ERROR: runtime exclusions missing" >&2
  exit 8
fi

echo "PLUGIN_VERSION=1.4.0"
echo "DEVHUB_ROOT=$WP_CONTENT"
echo "STRICT_REVIEW_ALLOWLIST=YES"
echo "STRICT_STAGE_ALLOWLIST=YES"
echo "GITIGNORE_MANAGED_SCOPE=REPAIRED"
echo "TRACKED_SCOPE=.gitignore,themes/thegem-elementor,plugins/tamiyouz-developer-hub,mu-plugins"
echo "RUNTIME_EXCLUSIONS=wflogs,boost-cache,uploads,cache,backups,logs"
echo "GIT_MUTATIONS_BY_PATCH=NONE"
echo "FRONT_END_CHANGED=NO"
echo "STATUS=READY"
