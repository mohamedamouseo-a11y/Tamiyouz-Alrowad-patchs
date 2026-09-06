#!/usr/bin/env bash
set -euo pipefail

WP_ROOT="${WP_ROOT:-$(pwd)}"
PLUGIN_FILE="$WP_ROOT/wp-content/plugins/tamiyouz-developer-hub/tamiyouz-developer-hub.php"

if [[ ! -f "$WP_ROOT/wp-config.php" || ! -d "$WP_ROOT/wp-content" ]]; then
  echo "ERROR: WP_ROOT does not look like a WordPress root: $WP_ROOT" >&2
  exit 2
fi

if [[ ! -f "$PLUGIN_FILE" ]]; then
  echo "ERROR: Tamiyouz Developer Hub plugin file not found: $PLUGIN_FILE" >&2
  exit 3
fi

python3 - "$PLUGIN_FILE" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

required = [
    "const VERSION = '1.2.0';",
    ": WP_CONTENT_DIR;",
    "A repository with zero branches is a valid first-bootstrap target.",
    "!/themes/thegem-elementor/**",
    "!/plugins/tamiyouz-developer-hub/**",
]
for marker in required:
    if marker not in s:
        raise SystemExit(f"ERROR: V1.2 marker missing; refusing unknown revision: {marker}")

s = s.replace(" * Version: 1.2.0", " * Version: 1.3.0", 1)
s = s.replace("const VERSION = '1.2.0';", "const VERSION = '1.3.0';", 1)


def replace_block(text, start_marker, end_marker, new_block):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: patch start marker not found: {start_marker}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: patch end marker not found: {end_marker}")
    return text[:start] + new_block.rstrip() + "\n\n" + text[end:]

new_git = r'''    private function git($args, $token = '', $allow_failure = false, $timeout = 120) {
        $root = $this->repo_root();
        $command = array_merge(['git', '-C', $root], array_values($args));
        $descriptors = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];
        $process = proc_open($command, $descriptors, $pipes, $root, $this->git_env($token), ['bypass_shell' => true]);
        if (!is_resource($process)) {
            return new WP_Error('git_start_failed', 'Unable to start Git.', ['status' => 500]);
        }
        fclose($pipes[0]);
        stream_set_blocking($pipes[1], false);
        stream_set_blocking($pipes[2], false);
        $stdout = '';
        $stderr = '';
        $start = microtime(true);
        $last_status = null;
        do {
            $stdout .= stream_get_contents($pipes[1]);
            $stderr .= stream_get_contents($pipes[2]);
            $status = proc_get_status($process);
            $last_status = $status;
            if (!$status['running']) {
                break;
            }
            if ((microtime(true) - $start) > $timeout) {
                proc_terminate($process, 9);
                fclose($pipes[1]);
                fclose($pipes[2]);
                proc_close($process);
                return new WP_Error('git_timeout', 'Git operation timed out.', ['status' => 504]);
            }
            usleep(20000);
        } while (true);
        $stdout .= stream_get_contents($pipes[1]);
        $stderr .= stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);

        // Some PHP/hosting combinations return -1 from proc_close() after
        // proc_get_status() already captured the real process exit code.
        // Prefer the captured non-negative exit code so harmless Git stderr
        // hints (for example the default-branch hint from git init) are not
        // misclassified as command failures.
        $close_exit = proc_close($process);
        $exit = $close_exit;
        if (is_array($last_status) && isset($last_status['exitcode']) && intval($last_status['exitcode']) >= 0) {
            $exit = intval($last_status['exitcode']);
        }

        if ($exit !== 0 && !$allow_failure) {
            $safe_error = preg_replace('/(github_pat_|ghp_)[A-Za-z0-9_]+/', '$1***', trim($stderr ?: $stdout));
            return new WP_Error('git_failed', $safe_error ?: 'Git command failed.', ['status' => 409]);
        }
        return [
            'exit' => $exit,
            'stdout' => trim($stdout),
            'stderr' => trim($stderr),
        ];
    }'''

new_init = r'''    public function rest_git_init() {
        $root = $this->repo_root();
        if (!is_dir($root) || !is_writable($root)) {
            return new WP_Error('root_not_writable', 'Configured project root is not writable.', ['status' => 409]);
        }

        $already_initialized = $this->git_available();
        if (!$already_initialized) {
            $result = $this->git(['init'], '', false);
            if (is_wp_error($result)) return $result;
            if (!$this->git_available()) {
                return new WP_Error('git_init_incomplete', 'Git init returned but .git was not created.', ['status' => 500]);
            }
        }

        $settings = $this->settings();
        $branch = $settings['branch'] ?: 'main';

        // Recovery-safe behavior: if this is a partially initialized repo with
        // no commits yet, complete the requested initial branch setup. If a
        // real history already exists, never rewrite its branch implicitly.
        $head = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);
        $has_head = !is_wp_error($head) && ($head['exit'] ?? 1) === 0;
        if ($has_head) {
            $current = $this->current_branch();
            if ($current !== '' && $current !== $branch) {
                return new WP_Error(
                    'existing_branch_mismatch',
                    'Existing Git history uses branch ' . $current . '; refusing to rewrite it automatically to ' . $branch . '.',
                    ['status' => 409]
                );
            }
        } else {
            $set_branch = $this->git(['symbolic-ref', 'HEAD', 'refs/heads/' . $branch], '', false);
            if (is_wp_error($set_branch)) return $set_branch;
        }

        $this->write_devhub_gitignore();

        $token = $this->decrypt_token();
        if (!empty($settings['repo']) && $token !== '') {
            $remote = $this->ensure_remote($settings['repo'], $token);
            if (is_wp_error($remote)) return $remote;
        }

        return rest_ensure_response([
            'ok' => true,
            'branch' => $branch,
            'alreadyInitialized' => $already_initialized,
            'recoveredPartialInit' => $already_initialized && !$has_head,
        ]);
    }'''

s = replace_block(
    s,
    "    private function git($args, $token = '', $allow_failure = false, $timeout = 120) {",
    "    private function ensure_remote($repo, $token) {",
    new_git,
)

s = replace_block(
    s,
    "    public function rest_git_init() {",
    "    private function write_devhub_gitignore() {",
    new_init,
)

p.write_text(s, encoding="utf-8")
PY

php -l "$PLUGIN_FILE"

if ! grep -Fq "const VERSION = '1.3.0';" "$PLUGIN_FILE"; then
  echo "ERROR: V1.3 version marker missing" >&2
  exit 4
fi
if ! grep -Fq "proc_close() after" "$PLUGIN_FILE"; then
  echo "ERROR: proc_close exit-code recovery missing" >&2
  exit 5
fi
if ! grep -Fq "recoveredPartialInit" "$PLUGIN_FILE"; then
  echo "ERROR: partial-init recovery missing" >&2
  exit 6
fi
if ! grep -Fq "existing_branch_mismatch" "$PLUGIN_FILE"; then
  echo "ERROR: existing-history protection missing" >&2
  exit 7
fi
if ! grep -Fq ": WP_CONTENT_DIR;" "$PLUGIN_FILE"; then
  echo "ERROR: wp-content root policy was lost" >&2
  exit 8
fi
if ! grep -Fq "A repository with zero branches is a valid first-bootstrap target." "$PLUGIN_FILE"; then
  echo "ERROR: empty-remote bootstrap support was lost" >&2
  exit 9
fi
if ! grep -Fq "!/themes/thegem-elementor/**" "$PLUGIN_FILE" \
  || ! grep -Fq "!/plugins/tamiyouz-developer-hub/**" "$PLUGIN_FILE"; then
  echo "ERROR: allowlist policy was lost" >&2
  exit 10
fi

echo "PLUGIN_VERSION=1.3.0"
echo "PROC_EXIT_CODE_FIX=YES"
echo "PARTIAL_GIT_INIT_RECOVERY=YES"
echo "EXISTING_HISTORY_PROTECTION=YES"
echo "EMPTY_REMOTE_BOOTSTRAP=SUPPORTED"
echo "ROOT_POLICY=WP_CONTENT_DIR"
echo "ALLOWLIST_POLICY=PASS"
echo "GIT_MUTATIONS_BY_PATCH=NONE"
echo "FRONT_END_CHANGED=NO"
echo "STATUS=READY"
