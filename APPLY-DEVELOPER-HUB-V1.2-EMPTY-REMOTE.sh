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

if ": WP_CONTENT_DIR;" not in s:
    raise SystemExit("ERROR: V1.1 wp-content root policy is missing; refusing to patch unknown revision")
if "!/themes/thegem-elementor/**" not in s or "!/plugins/tamiyouz-developer-hub/**" not in s:
    raise SystemExit("ERROR: V1.1 allowlist policy is missing; refusing to patch unknown revision")

s = s.replace(" * Version: 1.1.0", " * Version: 1.2.0", 1) if " * Version: 1.1.0" in s else s
s = s.replace("const VERSION = '1.1.0';", "const VERSION = '1.2.0';", 1) if "const VERSION = '1.1.0';" in s else s
if " * Version: 1.2.0" not in s or "const VERSION = '1.2.0';" not in s:
    raise SystemExit("ERROR: unable to establish Developer Hub V1.2 version markers")

def replace_block(text, start_marker, end_marker, new_block):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"ERROR: patch start marker not found: {start_marker}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"ERROR: patch end marker not found: {end_marker}")
    return text[:start] + new_block.rstrip() + "\n\n" + text[end:]

rest_branches = r'''    public function rest_branches(WP_REST_Request $request) {
        $repo = $this->validate_repo_slug($request->get_param('repo'));
        if (is_wp_error($repo)) {
            return $repo;
        }
        $token = $this->decrypt_token();
        if ($token === '') {
            return new WP_Error('not_connected', 'Connect GitHub first.', ['status' => 409]);
        }
        $parts = explode('/', $repo, 2);
        $repo_path = rawurlencode($parts[0]) . '/' . rawurlencode($parts[1]);
        $branches = $this->github_request('GET', '/repos/' . $repo_path . '/branches?per_page=100', $token);
        if (is_wp_error($branches)) {
            return $branches;
        }
        if (empty($branches)) {
            $repo_data = $this->github_request('GET', '/repos/' . $repo_path, $token);
            if (is_wp_error($repo_data)) {
                return $repo_data;
            }
            $default_branch = sanitize_text_field($repo_data['default_branch'] ?? '');
            if ($default_branch === '') {
                $default_branch = 'main';
            }
            return rest_ensure_response([
                'branches' => [$default_branch],
                'remoteEmpty' => true,
            ]);
        }
        return rest_ensure_response([
            'branches' => array_values(array_filter(array_map(function ($item) {
                return is_array($item) && isset($item['name']) ? sanitize_text_field($item['name']) : '';
            }, $branches))),
            'remoteEmpty' => false,
        ]);
    }'''

rest_selection = r'''    public function rest_selection(WP_REST_Request $request) {
        $repo = $this->validate_repo_slug($request->get_param('repo'));
        if (is_wp_error($repo)) return $repo;
        $branch = $this->validate_branch($request->get_param('branch'));
        if (is_wp_error($branch)) return $branch;
        $token = $this->decrypt_token();
        if ($token === '') return new WP_Error('not_connected', 'Connect GitHub first.', ['status' => 409]);

        $parts = explode('/', $repo, 2);
        $repo_path = rawurlencode($parts[0]) . '/' . rawurlencode($parts[1]);
        $repo_data = $this->github_request('GET', '/repos/' . $repo_path, $token);
        if (is_wp_error($repo_data)) return $repo_data;

        $branch_data = $this->github_request('GET', '/repos/' . $repo_path . '/branches/' . rawurlencode($branch), $token);
        $remote_empty = false;
        if (is_wp_error($branch_data)) {
            $error_data = $branch_data->get_error_data();
            $error_status = is_array($error_data) ? intval($error_data['status'] ?? 0) : 0;
            if (!in_array($error_status, [404, 409], true)) {
                return $branch_data;
            }
            $branches = $this->github_request('GET', '/repos/' . $repo_path . '/branches?per_page=1', $token);
            if (is_wp_error($branches)) return $branches;
            if (!empty($branches)) {
                return $branch_data;
            }
            $remote_empty = true;
        }

        $permission = '';
        if (!empty($repo_data['permissions']['admin'])) $permission = 'admin';
        elseif (!empty($repo_data['permissions']['maintain'])) $permission = 'maintain';
        elseif (!empty($repo_data['permissions']['push'])) $permission = 'push';
        elseif (!empty($repo_data['permissions']['pull'])) $permission = 'pull';
        if (!in_array($permission, ['admin', 'maintain', 'push'], true)) {
            return new WP_Error('insufficient_repo_permission', 'The selected repository requires write permission.', ['status' => 403]);
        }
        $this->save_settings(['repo' => $repo, 'branch' => $branch, 'permission' => $permission]);
        if ($this->git_available()) {
            $remote = $this->ensure_remote($repo, $token);
            if (is_wp_error($remote)) return $remote;
        }
        return rest_ensure_response([
            'ok' => true,
            'repo' => $repo,
            'branch' => $branch,
            'permission' => $permission,
            'remoteEmpty' => $remote_empty,
        ]);
    }'''

fetch_remote = r'''    private function fetch_remote($settings, $token) {
        $remote = $this->ensure_remote($settings['repo'], $token);
        if (is_wp_error($remote)) return $remote;

        $parts = explode('/', $settings['repo'], 2);
        if (count($parts) !== 2) {
            return new WP_Error('invalid_repo', 'Repository must be in owner/name format.', ['status' => 400]);
        }
        $repo_path = rawurlencode($parts[0]) . '/' . rawurlencode($parts[1]);
        $branches = $this->github_request('GET', '/repos/' . $repo_path . '/branches?per_page=1', $token);
        if (is_wp_error($branches)) return $branches;

        // A repository with zero branches is a valid first-bootstrap target.
        // Do not treat the missing remote branch as a fetch failure in this one case.
        if (empty($branches)) {
            return [
                'exit' => 0,
                'stdout' => '',
                'stderr' => '',
                'remoteEmpty' => true,
            ];
        }

        $branch = $settings['branch'];
        return $this->git([
            'fetch', '--prune', self::REMOTE,
            '+refs/heads/' . $branch . ':refs/remotes/' . self::REMOTE . '/' . $branch,
        ], $token, false, 180);
    }'''

s = replace_block(
    s,
    "    public function rest_branches(WP_REST_Request $request) {",
    "    public function rest_selection(WP_REST_Request $request) {",
    rest_branches,
)

s = replace_block(
    s,
    "    public function rest_selection(WP_REST_Request $request) {",
    "    public function rest_disconnect() {",
    rest_selection,
)

s = replace_block(
    s,
    "    private function fetch_remote($settings, $token) {",
    "    private function current_branch() {",
    fetch_remote,
)

p.write_text(s, encoding="utf-8")
PY

php -l "$PLUGIN_FILE"

if ! grep -Fq "const VERSION = '1.2.0';" "$PLUGIN_FILE"; then
  echo "ERROR: V1.2 version marker missing" >&2
  exit 4
fi
if ! grep -Fq "A repository with zero branches is a valid first-bootstrap target." "$PLUGIN_FILE"; then
  echo "ERROR: empty-remote bootstrap policy missing" >&2
  exit 5
fi
if ! grep -Fq "'remoteEmpty' => true" "$PLUGIN_FILE"; then
  echo "ERROR: empty-remote branch response missing" >&2
  exit 6
fi
if ! grep -Fq ": WP_CONTENT_DIR;" "$PLUGIN_FILE"; then
  echo "ERROR: wp-content root policy was lost" >&2
  exit 7
fi
if ! grep -Fq "!/themes/thegem-elementor/**" "$PLUGIN_FILE" \
  || ! grep -Fq "!/plugins/tamiyouz-developer-hub/**" "$PLUGIN_FILE"; then
  echo "ERROR: allowlist policy was lost" >&2
  exit 8
fi

echo "PLUGIN_VERSION=1.2.0"
echo "EMPTY_REMOTE_BOOTSTRAP=SUPPORTED"
echo "BRANCHLESS_REMOTE_SELECTION=SUPPORTED"
echo "STRICT_FETCH_NONEMPTY_REMOTE=YES"
echo "ROOT_POLICY=WP_CONTENT_DIR"
echo "ALLOWLIST_POLICY=PASS"
echo "GIT_INITIALIZED_BY_PATCH=NO"
echo "GIT_OPERATIONS_PERFORMED=NONE"
echo "FRONT_END_CHANGED=NO"
echo "STATUS=READY"
