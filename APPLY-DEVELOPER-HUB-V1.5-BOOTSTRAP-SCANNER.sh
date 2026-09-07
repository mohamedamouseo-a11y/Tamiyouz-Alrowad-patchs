#!/usr/bin/env bash
set -euo pipefail

WP_ROOT="${WP_ROOT:-$(pwd)}"
WP_CONTENT="$WP_ROOT/wp-content"
PLUGIN_FILE="$WP_CONTENT/plugins/tamiyouz-developer-hub/tamiyouz-developer-hub.php"
GITIGNORE="$WP_CONTENT/.gitignore"

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
    "const VERSION = '1.4.1';",
    ": WP_CONTENT_DIR;",
    "private function version_control_allowed",
    "private function version_control_pathspecs",
    "recoveredPartialInit",
    "A repository with zero branches is a valid first-bootstrap target.",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f"ERROR: V1.4.1 marker missing; refusing unknown revision: {marker}")

s = s.replace(" * Version: 1.4.1", " * Version: 1.5.0", 1)
s = s.replace("const VERSION = '1.4.1';", "const VERSION = '1.5.0';", 1)


def replace_block(text, start_marker, end_marker, new_block):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: start marker missing: {start_marker}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: end marker missing: {end_marker}")
    return text[:start] + new_block.rstrip() + "\n\n" + text[end:]

helpers = r'''    private function version_control_allowed($path) {
        $normalized = ltrim(str_replace(chr(92), '/', (string) $path), '/');
        if ($normalized === '.gitignore') return true;
        if (strpos($normalized, 'themes/thegem-elementor/') === 0) return true;
        if (strpos($normalized, 'plugins/tamiyouz-developer-hub/') === 0) return true;
        return false;
    }

    private function version_control_pathspecs() {
        return ['.gitignore', 'themes/thegem-elementor', 'plugins/tamiyouz-developer-hub'];
    }'''

s = replace_block(
    s,
    "    private function version_control_allowed($path) {",
    "    private function changed_files() {",
    helpers,
)

scanner = r'''    private function scan_file_for_secrets($path) {
        $reason = $this->blocked_path_reason($path);
        if ($reason) return $reason;
        $full = $this->repo_root() . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $path);
        if (is_link($full)) return 'Symlinked files require manual review outside Developer Hub.';
        if (!is_file($full) || !is_readable($full)) return '';
        $size = filesize($full);
        if ($size === false || $size === 0 || $size > self::MAX_SCAN_BYTES) return '';
        $content = file_get_contents($full);
        if (!is_string($content) || strpos($content, "\0") !== false) return '';

        // High-confidence credential signatures remain hard blockers.
        $hard_patterns = [
            '/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/' => 'Private key material detected.',
            '/\bgithub_pat_[A-Za-z0-9_]{20,}\b/' => 'GitHub token detected.',
            '/\bgh[pousr]_[A-Za-z0-9]{20,}\b/' => 'GitHub token detected.',
            '/\bAKIA[0-9A-Z]{16}\b/' => 'AWS access key detected.',
        ];
        foreach ($hard_patterns as $pattern => $message) {
            if (preg_match($pattern, $content)) return $message;
        }

        // Generic secret detection is intentionally high-confidence only.
        // This avoids blocking normal WordPress/theme source containing words
        // such as token/password in validation rules, labels or templates.
        $lines = preg_split('/\R/', $content);
        foreach ($lines as $line) {
            if (!preg_match('/\b(password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token)\b\s*(?:=>|=|:)\s*[\'\"]([^\'\"\r\n]{12,})[\'\"]/i', $line, $match)) {
                continue;
            }
            $value = trim($match[2]);
            if ($value === '') continue;
            if (preg_match('/(?:example|placeholder|changeme|change-me|your[_-]?|dummy|sample|test|replace[_-]?me|insert[_-]?here)/i', $value)) continue;
            if (preg_match('#^(?:https?://|/|\\\\)#i', $value)) continue;
            if (preg_match('/[\$\{\}\(\)\[\]<>]/', $value)) continue;

            $classes = 0;
            if (preg_match('/[a-z]/', $value)) $classes++;
            if (preg_match('/[A-Z]/', $value)) $classes++;
            if (preg_match('/[0-9]/', $value)) $classes++;
            if (preg_match('/[^A-Za-z0-9]/', $value)) $classes++;
            $unique = count(array_unique(str_split($value)));
            $looks_hex = strlen($value) >= 24 && preg_match('/^[A-Fa-f0-9]+$/', $value);
            if ($unique >= 8 && ($looks_hex || strlen($value) >= 24 || $classes >= 3)) {
                return 'Possible embedded credential detected.';
            }
        }
        return '';
    }'''

s = replace_block(
    s,
    "    private function scan_file_for_secrets($path) {",
    "    private function ahead_behind($remote_ref) {",
    scanner,
)

# First bootstrap: an unborn local repository may still report master (or another
# symbolic branch) before the first commit. Do not block review solely for that.
old_preview = """        $current = $this->current_branch();\n        $blocked = [];\n        if ($current !== $branch) {\n            $blocked[] = ['path' => '(branch)', 'reason' => 'Selected GitHub branch must match the current local branch.'];\n        }\n"""
new_preview = """        $current = $this->current_branch();\n        $blocked = [];\n        $head_check = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);\n        $has_local_head = !is_wp_error($head_check) && ($head_check['exit'] ?? 1) === 0;\n        $bootstrap_branch_repair = !$has_local_head && $current !== $branch;\n        if ($current !== $branch && !$bootstrap_branch_repair) {\n            $blocked[] = ['path' => '(branch)', 'reason' => 'Selected GitHub branch must match the current local branch.'];\n        }\n"""
if old_preview in s:
    s = s.replace(old_preview, new_preview, 1)
elif new_preview not in s:
    raise SystemExit('ERROR: preview branch block target missing')

old_fp = """            'state' => $state, 'expected' => $expected, 'localAhead' => $local_ahead, 'remoteAhead' => $remote_ahead,\n            'files' => $files, 'blocked' => $blocked,\n"""
new_fp = """            'state' => $state, 'expected' => $expected, 'localAhead' => $local_ahead, 'remoteAhead' => $remote_ahead,\n            'bootstrapBranchRepair' => $bootstrap_branch_repair,\n            'files' => $files, 'blocked' => $blocked,\n"""
if old_fp in s:
    s = s.replace(old_fp, new_fp, 1)
elif new_fp not in s:
    raise SystemExit('ERROR: fingerprint bootstrap marker target missing')

# Normalize the symbolic branch only at execution time, after the reviewed
# fingerprint has been validated and only when there is still no local commit.
needle = """        $branch = $settings['branch'];\n        $remote_ref = self::REMOTE . '/' . $branch;\n        $expected = $preview['expectedAction'];\n        $logs = [];\n"""
replacement = """        $branch = $settings['branch'];\n        $remote_ref = self::REMOTE . '/' . $branch;\n        $expected = $preview['expectedAction'];\n        $logs = [];\n\n        $head_check = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);\n        $has_local_head = !is_wp_error($head_check) && ($head_check['exit'] ?? 1) === 0;\n        if (!$has_local_head && $this->current_branch() !== $branch) {\n            $set_branch = $this->git(['symbolic-ref', 'HEAD', 'refs/heads/' . $branch], '', false);\n            if (is_wp_error($set_branch)) return $set_branch;\n            $logs[] = ['type' => 'info', 'message' => 'Initial local branch normalized to ' . $branch . '.'];\n        }\n"""
if needle in s:
    s = s.replace(needle, replacement, 1)
elif replacement not in s:
    raise SystemExit('ERROR: execute bootstrap branch target missing')

# Remove mu-plugins from the managed scope because the observed files are
# Hostinger/Elementor runtime integrations, not Tamiyouz-owned source.
old_mu_rules = """            . \"!/mu-plugins/\\n!/mu-plugins/**\\n\"\n"""
new_mu_rules = """            . \"/mu-plugins/\\n\"\n"""
if old_mu_rules in s:
    s = s.replace(old_mu_rules, new_mu_rules, 1)
elif new_mu_rules not in s:
    raise SystemExit('ERROR: mu-plugins scope target missing')

p.write_text(s, encoding='utf-8')
PY

# Repair the managed ignore block on disk. No Git command is executed.
python3 - "$GITIGNORE" <<'PY'
from pathlib import Path
import re, sys
p = Path(sys.argv[1])
current = p.read_text(encoding='utf-8') if p.exists() else ''
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
/mu-plugins/
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
current = re.sub(r'\n?# BEGIN Tamiyouz Developer Hub managed scope.*?# END Tamiyouz Developer Hub managed scope\n?', '', current, flags=re.S)
p.write_text(current.rstrip() + ('\n\n' if current.strip() else '') + rules, encoding='utf-8')
PY

php -l "$PLUGIN_FILE"

grep -Fq "const VERSION = '1.5.0';" "$PLUGIN_FILE"
grep -Fq "bootstrapBranchRepair" "$PLUGIN_FILE"
grep -Fq "Initial local branch normalized" "$PLUGIN_FILE"
grep -Fq "Generic secret detection is intentionally high-confidence only" "$PLUGIN_FILE"
grep -Fq "return ['.gitignore', 'themes/thegem-elementor', 'plugins/tamiyouz-developer-hub'];" "$PLUGIN_FILE"
grep -Fq "/mu-plugins/" "$GITIGNORE"

echo "PLUGIN_VERSION=1.5.0"
echo "BOOTSTRAP_BRANCH_NORMALIZATION=SUPPORTED"
echo "SECRET_SCANNER_FALSE_POSITIVE_HARDENING=YES"
echo "STRICT_REVIEW_ALLOWLIST=themes/thegem-elementor,plugins/tamiyouz-developer-hub,.gitignore"
echo "MU_PLUGINS_EXCLUDED=YES"
echo "GIT_MUTATIONS_BY_PATCH=NONE"
echo "FRONT_END_CHANGED=NO"
echo "STATUS=READY"
