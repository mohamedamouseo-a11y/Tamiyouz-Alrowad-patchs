<?php
/**
 * Plugin Name: Tamiyouz Developer Hub
 * Description: Super-admin-only Developer Hub for secure GitHub connection, review, push, pull and synchronization from WordPress.
 * Version: 1.0.0
 * Author: Tamiyouz
 */

if (!defined('ABSPATH')) {
    exit;
}

final class TAR_Developer_Hub {
    const VERSION = '1.0.0';
    const OPTION_KEY = 'tar_developer_hub_settings';
    const REST_NS = 'tar-devhub/v1';
    const REMOTE = 'tamiyouz-devhub';
    const MAX_SCAN_BYTES = 2097152;

    private static $instance = null;

    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', [$this, 'admin_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_assets']);
        add_action('rest_api_init', [$this, 'register_routes']);
    }

    public static function can_access() {
        if (!is_user_logged_in()) {
            return false;
        }
        if (is_multisite()) {
            return is_super_admin(get_current_user_id());
        }
        return current_user_can('manage_options');
    }

    public function admin_menu() {
        if (!self::can_access()) {
            return;
        }
        add_menu_page(
            'Developer Hub',
            'Developer Hub',
            'manage_options',
            'tamiyouz-developer-hub',
            [$this, 'render_page'],
            'dashicons-editor-code',
            81
        );
    }

    public function enqueue_assets($hook) {
        if ($hook !== 'toplevel_page_tamiyouz-developer-hub' || !self::can_access()) {
            return;
        }
        $base = plugin_dir_url(__FILE__);
        wp_enqueue_style('tar-developer-hub', $base . 'assets/admin.css', [], self::VERSION);
        wp_enqueue_script('tar-developer-hub', $base . 'assets/admin.js', [], self::VERSION, true);
        wp_localize_script('tar-developer-hub', 'TARDevHub', [
            'rest' => esc_url_raw(rest_url(self::REST_NS . '/')),
            'nonce' => wp_create_nonce('wp_rest'),
            'isRtl' => is_rtl(),
        ]);
    }

    public function render_page() {
        if (!self::can_access()) {
            wp_die(esc_html__('You do not have permission to access this page.', 'tamiyouz-developer-hub'));
        }
        ?>
        <div class="wrap tar-devhub" id="tar-devhub-app">
            <div class="tar-devhub__hero">
                <div class="tar-devhub__hero-icon"><span class="dashicons dashicons-editor-code"></span></div>
                <div class="tar-devhub__hero-copy">
                    <h1>Developer Hub</h1>
                    <p>Connect GitHub and securely review, push, pull, or synchronize this WordPress project.</p>
                </div>
                <div class="tar-devhub__hero-badges">
                    <span class="tar-badge" id="tar-connection-badge">Disconnected</span>
                    <span class="tar-badge tar-badge--muted" id="tar-login-badge" hidden></span>
                </div>
            </div>

            <div class="tar-grid tar-grid--stats">
                <div class="tar-stat"><span>Local branch</span><strong id="tar-stat-branch">—</strong></div>
                <div class="tar-stat"><span>Commit</span><strong id="tar-stat-sha">—</strong></div>
                <div class="tar-stat"><span>Working tree</span><strong id="tar-stat-dirty">—</strong></div>
                <div class="tar-stat"><span>Git repository</span><strong id="tar-stat-git">—</strong></div>
            </div>

            <div class="tar-grid tar-grid--two">
                <section class="tar-card">
                    <div class="tar-card__head">
                        <div>
                            <h2><span class="dashicons dashicons-admin-network"></span> Connection &amp; Repository</h2>
                            <p>Verify the GitHub account, then select the repository and branch for this project.</p>
                        </div>
                    </div>
                    <div class="tar-card__body tar-stack">
                        <label class="tar-field">
                            <span>GitHub Personal Access Token</span>
                            <div class="tar-inline">
                                <input id="tar-token" type="password" autocomplete="new-password" placeholder="github_pat_..." />
                                <button class="button button-secondary" type="button" id="tar-toggle-token">Show</button>
                                <button class="button button-primary" type="button" id="tar-connect">Verify</button>
                            </div>
                            <small>Token is encrypted before storage and is never returned to the browser.</small>
                        </label>

                        <label class="tar-field">
                            <span>Repository</span>
                            <div class="tar-inline">
                                <select id="tar-repo"><option value="">Select repository</option></select>
                                <button class="button button-secondary" type="button" id="tar-refresh-repos">Refresh</button>
                            </div>
                        </label>

                        <label class="tar-field">
                            <span>Branch</span>
                            <div class="tar-inline">
                                <select id="tar-branch"><option value="">Select branch</option></select>
                                <button class="button button-secondary" type="button" id="tar-refresh-branches">Refresh</button>
                            </div>
                        </label>

                        <div class="tar-inline tar-inline--wrap">
                            <button class="button button-primary" type="button" id="tar-save-selection">Save Selection</button>
                            <button class="button" type="button" id="tar-disconnect">Disconnect</button>
                        </div>

                        <div class="tar-grid tar-grid--mini">
                            <div class="tar-mini"><span>Saved repository</span><strong id="tar-saved-repo">—</strong></div>
                            <div class="tar-mini"><span>Saved branch</span><strong id="tar-saved-branch">—</strong></div>
                        </div>
                    </div>
                </section>

                <section class="tar-card">
                    <div class="tar-card__head">
                        <div>
                            <h2><span class="dashicons dashicons-update-alt"></span> Synchronization Status</h2>
                            <p>Review differences before changing the WordPress project or GitHub.</p>
                        </div>
                    </div>
                    <div class="tar-card__body tar-stack">
                        <div class="tar-grid tar-grid--mini">
                            <div class="tar-mini"><span>Sync state</span><strong id="tar-sync-state">Not reviewed</strong></div>
                            <div class="tar-mini"><span>Local ahead</span><strong id="tar-local-ahead">—</strong></div>
                            <div class="tar-mini"><span>Remote ahead</span><strong id="tar-remote-ahead">—</strong></div>
                        </div>

                        <label class="tar-field">
                            <span>Commit message</span>
                            <input id="tar-commit-message" type="text" maxlength="180" placeholder="Developer Hub sync" />
                        </label>

                        <div class="tar-actions">
                            <button class="button button-primary tar-action" type="button" data-action="push">↑ Review Push</button>
                            <button class="button button-secondary tar-action" type="button" data-action="pull">↓ Review Pull</button>
                            <button class="button button-secondary tar-action" type="button" data-action="sync">⇄ Review Full Sync</button>
                        </div>

                        <div class="tar-progress" hidden id="tar-progress-wrap"><div id="tar-progress-bar"></div></div>
                        <p class="tar-step" id="tar-current-step">No operation running.</p>

                        <div class="tar-alert tar-alert--warning" id="tar-git-init-box" hidden>
                            <strong>Local Git repository not initialized.</strong>
                            <p>The Developer Hub will not initialize or rewrite Git automatically. Initialize only after confirming the intended repository root.</p>
                            <button class="button" type="button" id="tar-init-git">Initialize Git in configured project root</button>
                        </div>
                    </div>
                </section>
            </div>

            <section class="tar-card" id="tar-review-card" hidden>
                <div class="tar-card__head tar-card__head--row">
                    <div>
                        <h2><span class="dashicons dashicons-visibility"></span> Secure Review</h2>
                        <p id="tar-review-summary">Review the exact files before execution.</p>
                    </div>
                    <button class="button button-primary" type="button" id="tar-execute" disabled>Execute Reviewed Action</button>
                </div>
                <div class="tar-card__body">
                    <div id="tar-blockers"></div>
                    <div class="tar-table-wrap">
                        <table class="widefat striped tar-table">
                            <thead><tr><th>Status</th><th>Path</th><th>Direction</th></tr></thead>
                            <tbody id="tar-review-files"></tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section class="tar-card">
                <div class="tar-card__head tar-card__head--row">
                    <div>
                        <h2><span class="dashicons dashicons-editor-code"></span> Operation Log</h2>
                        <p>Developer Hub events are shown here. Secrets are never logged.</p>
                    </div>
                    <button class="button" type="button" id="tar-clear-log">Clear</button>
                </div>
                <div class="tar-terminal" id="tar-terminal" aria-live="polite"></div>
            </section>

            <div class="tar-path">Project root: <code id="tar-repo-path">—</code></div>
        </div>
        <?php
    }

    public function register_routes() {
        $routes = [
            ['status', 'GET', 'rest_status'],
            ['github/connect', 'POST', 'rest_connect'],
            ['github/repos', 'GET', 'rest_repos'],
            ['github/branches', 'GET', 'rest_branches'],
            ['github/selection', 'POST', 'rest_selection'],
            ['github/disconnect', 'DELETE', 'rest_disconnect'],
            ['git/init', 'POST', 'rest_git_init'],
            ['git/preview', 'POST', 'rest_preview'],
            ['git/execute', 'POST', 'rest_execute'],
        ];
        foreach ($routes as $route) {
            register_rest_route(self::REST_NS, '/' . $route[0], [
                'methods' => $route[1],
                'callback' => [$this, $route[2]],
                'permission_callback' => [$this, 'rest_permission'],
            ]);
        }
    }

    public function rest_permission() {
        return self::can_access();
    }

    private function repo_root() {
        $root = defined('TAR_DEVHUB_REPO_PATH') && TAR_DEVHUB_REPO_PATH ? TAR_DEVHUB_REPO_PATH : ABSPATH;
        $real = realpath($root);
        return $real ? rtrim($real, DIRECTORY_SEPARATOR) : rtrim($root, DIRECTORY_SEPARATOR);
    }

    private function default_settings() {
        return [
            'token' => '',
            'repo' => '',
            'branch' => '',
            'login' => '',
            'permission' => '',
            'verified_at' => '',
            'updated_at' => '',
        ];
    }

    private function settings() {
        return wp_parse_args(get_option(self::OPTION_KEY, []), $this->default_settings());
    }

    private function save_settings($partial) {
        $settings = array_merge($this->settings(), $partial, ['updated_at' => gmdate('c')]);
        update_option(self::OPTION_KEY, $settings, false);
        return $settings;
    }

    private function crypto_key() {
        return hash('sha256', wp_salt('auth') . '|' . wp_salt('secure_auth'), true);
    }

    private function encrypt_token($plain) {
        if ($plain === '') {
            return '';
        }
        if (!function_exists('openssl_encrypt')) {
            return new WP_Error('crypto_unavailable', 'OpenSSL is required to store the GitHub token securely.', ['status' => 500]);
        }
        $iv = random_bytes(12);
        $tag = '';
        $cipher = openssl_encrypt($plain, 'aes-256-gcm', $this->crypto_key(), OPENSSL_RAW_DATA, $iv, $tag, 'tar-devhub-v1');
        if ($cipher === false) {
            return new WP_Error('encrypt_failed', 'Unable to encrypt GitHub token.', ['status' => 500]);
        }
        return base64_encode(json_encode([
            'v' => 1,
            'iv' => base64_encode($iv),
            'tag' => base64_encode($tag),
            'data' => base64_encode($cipher),
        ]));
    }

    private function decrypt_token($stored = null) {
        $stored = $stored === null ? $this->settings()['token'] : $stored;
        if (!$stored) {
            return '';
        }
        if (!function_exists('openssl_decrypt')) {
            return '';
        }
        $payload = json_decode(base64_decode($stored, true), true);
        if (!is_array($payload) || ($payload['v'] ?? 0) !== 1) {
            return '';
        }
        $plain = openssl_decrypt(
            base64_decode($payload['data'] ?? '', true),
            'aes-256-gcm',
            $this->crypto_key(),
            OPENSSL_RAW_DATA,
            base64_decode($payload['iv'] ?? '', true),
            base64_decode($payload['tag'] ?? '', true),
            'tar-devhub-v1'
        );
        return is_string($plain) ? $plain : '';
    }

    private function github_request($method, $endpoint, $token, $body = null) {
        $url = 'https://api.github.com' . $endpoint;
        $args = [
            'method' => $method,
            'timeout' => 20,
            'redirection' => 2,
            'headers' => [
                'Accept' => 'application/vnd.github+json',
                'Authorization' => 'Bearer ' . $token,
                'X-GitHub-Api-Version' => '2022-11-28',
                'User-Agent' => 'Tamiyouz-Developer-Hub/' . self::VERSION,
            ],
        ];
        if ($body !== null) {
            $args['headers']['Content-Type'] = 'application/json';
            $args['body'] = wp_json_encode($body);
        }
        $response = wp_remote_request($url, $args);
        if (is_wp_error($response)) {
            return $response;
        }
        $code = wp_remote_retrieve_response_code($response);
        $data = json_decode(wp_remote_retrieve_body($response), true);
        if ($code < 200 || $code >= 300) {
            $message = is_array($data) && !empty($data['message']) ? $data['message'] : 'GitHub API request failed.';
            return new WP_Error('github_api_error', $message, ['status' => $code ?: 502]);
        }
        return is_array($data) ? $data : [];
    }

    private function validate_repo_slug($repo) {
        $repo = trim((string) $repo);
        if (!preg_match('#^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$#', $repo)) {
            return new WP_Error('invalid_repo', 'Repository must be in owner/name format.', ['status' => 400]);
        }
        return $repo;
    }

    private function validate_branch($branch) {
        $branch = trim((string) $branch);
        if ($branch === '' || strlen($branch) > 200 || preg_match('/[\x00-\x20~^:?*\[\\]/', $branch) || strpos($branch, '..') !== false || substr($branch, -1) === '.' || substr($branch, -1) === '/') {
            return new WP_Error('invalid_branch', 'Invalid Git branch.', ['status' => 400]);
        }
        return $branch;
    }

    private function git_available() {
        $root = $this->repo_root();
        return is_dir($root . DIRECTORY_SEPARATOR . '.git');
    }

    private function git_env($token = '') {
        $env = [
            'PATH' => getenv('PATH') ?: '/usr/local/bin:/usr/bin:/bin',
            'HOME' => getenv('HOME') ?: sys_get_temp_dir(),
            'GIT_TERMINAL_PROMPT' => '0',
            'GIT_CONFIG_NOSYSTEM' => '1',
        ];
        if ($token !== '') {
            $auth = base64_encode('x-access-token:' . $token);
            $env['GIT_CONFIG_COUNT'] = '1';
            $env['GIT_CONFIG_KEY_0'] = 'http.https://github.com/.extraheader';
            $env['GIT_CONFIG_VALUE_0'] = 'AUTHORIZATION: basic ' . $auth;
        }
        return array_merge($_ENV, $env);
    }

    private function git($args, $token = '', $allow_failure = false, $timeout = 120) {
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
        do {
            $stdout .= stream_get_contents($pipes[1]);
            $stderr .= stream_get_contents($pipes[2]);
            $status = proc_get_status($process);
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
        $exit = proc_close($process);
        if ($exit !== 0 && !$allow_failure) {
            $safe_error = preg_replace('/(github_pat_|ghp_)[A-Za-z0-9_]+/', '$1***', trim($stderr ?: $stdout));
            return new WP_Error('git_failed', $safe_error ?: 'Git command failed.', ['status' => 409]);
        }
        return [
            'exit' => $exit,
            'stdout' => trim($stdout),
            'stderr' => trim($stderr),
        ];
    }

    private function ensure_remote($repo, $token) {
        $url = 'https://github.com/' . $repo . '.git';
        $exists = $this->git(['remote', 'get-url', self::REMOTE], '', true);
        if (is_wp_error($exists)) {
            return $exists;
        }
        if (($exists['exit'] ?? 1) === 0) {
            return $this->git(['remote', 'set-url', self::REMOTE, $url], $token);
        }
        return $this->git(['remote', 'add', self::REMOTE, $url], $token);
    }

    private function git_status_info() {
        $info = [
            'gitAvailable' => $this->git_available(),
            'repoPath' => $this->repo_root(),
            'branch' => '',
            'shortSha' => '',
            'lastCommit' => '',
            'isDirty' => false,
        ];
        if (!$info['gitAvailable']) {
            return $info;
        }
        $branch = $this->git(['branch', '--show-current'], '', true);
        $sha = $this->git(['rev-parse', '--short=10', 'HEAD'], '', true);
        $last = $this->git(['log', '-1', '--pretty=%s'], '', true);
        $dirty = $this->git(['status', '--porcelain=v1'], '', true);
        $info['branch'] = !is_wp_error($branch) ? trim($branch['stdout']) : '';
        $info['shortSha'] = !is_wp_error($sha) && ($sha['exit'] ?? 1) === 0 ? trim($sha['stdout']) : '';
        $info['lastCommit'] = !is_wp_error($last) && ($last['exit'] ?? 1) === 0 ? trim($last['stdout']) : '';
        $info['isDirty'] = !is_wp_error($dirty) && trim($dirty['stdout']) !== '';
        return $info;
    }

    public function rest_status() {
        $settings = $this->settings();
        return rest_ensure_response(array_merge($this->git_status_info(), [
            'githubTokenSet' => $this->decrypt_token($settings['token']) !== '',
            'githubRepo' => $settings['repo'],
            'githubBranch' => $settings['branch'],
            'githubLogin' => $settings['login'],
            'githubPermission' => $settings['permission'],
            'githubVerifiedAt' => $settings['verified_at'],
            'githubConnectionStatus' => ($settings['login'] && $settings['repo'] && $settings['branch']) ? 'verified' : ($settings['login'] ? 'incomplete' : 'disconnected'),
        ]));
    }

    public function rest_connect(WP_REST_Request $request) {
        $token = trim((string) $request->get_param('token'));
        if ($token === '') {
            return new WP_Error('missing_token', 'Enter a GitHub token.', ['status' => 400]);
        }
        if (strlen($token) < 20 || strlen($token) > 255 || preg_match('/\s/', $token)) {
            return new WP_Error('invalid_token', 'Invalid GitHub token format.', ['status' => 400]);
        }
        $user = $this->github_request('GET', '/user', $token);
        if (is_wp_error($user)) {
            return $user;
        }
        $encrypted = $this->encrypt_token($token);
        if (is_wp_error($encrypted)) {
            return $encrypted;
        }
        $this->save_settings([
            'token' => $encrypted,
            'login' => sanitize_text_field($user['login'] ?? ''),
            'verified_at' => gmdate('c'),
        ]);
        return rest_ensure_response(['ok' => true, 'login' => sanitize_text_field($user['login'] ?? '')]);
    }

    public function rest_repos() {
        $token = $this->decrypt_token();
        if ($token === '') {
            return new WP_Error('not_connected', 'Connect GitHub first.', ['status' => 409]);
        }
        $repos = $this->github_request('GET', '/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member', $token);
        if (is_wp_error($repos)) {
            return $repos;
        }
        $out = [];
        foreach ($repos as $repo) {
            if (!is_array($repo) || empty($repo['full_name'])) {
                continue;
            }
            $permission = '';
            if (!empty($repo['permissions']['admin'])) $permission = 'admin';
            elseif (!empty($repo['permissions']['maintain'])) $permission = 'maintain';
            elseif (!empty($repo['permissions']['push'])) $permission = 'push';
            elseif (!empty($repo['permissions']['pull'])) $permission = 'pull';
            $out[] = [
                'fullName' => sanitize_text_field($repo['full_name']),
                'private' => !empty($repo['private']),
                'defaultBranch' => sanitize_text_field($repo['default_branch'] ?? 'main'),
                'permission' => $permission,
                'updatedAt' => sanitize_text_field($repo['updated_at'] ?? ''),
            ];
        }
        return rest_ensure_response(['repositories' => $out]);
    }

    public function rest_branches(WP_REST_Request $request) {
        $repo = $this->validate_repo_slug($request->get_param('repo'));
        if (is_wp_error($repo)) {
            return $repo;
        }
        $token = $this->decrypt_token();
        if ($token === '') {
            return new WP_Error('not_connected', 'Connect GitHub first.', ['status' => 409]);
        }
        $parts = explode('/', $repo, 2);
        $branches = $this->github_request('GET', '/repos/' . rawurlencode($parts[0]) . '/' . rawurlencode($parts[1]) . '/branches?per_page=100', $token);
        if (is_wp_error($branches)) {
            return $branches;
        }
        return rest_ensure_response(['branches' => array_values(array_filter(array_map(function ($item) {
            return is_array($item) && isset($item['name']) ? sanitize_text_field($item['name']) : '';
        }, $branches)))]);
    }

    public function rest_selection(WP_REST_Request $request) {
        $repo = $this->validate_repo_slug($request->get_param('repo'));
        if (is_wp_error($repo)) return $repo;
        $branch = $this->validate_branch($request->get_param('branch'));
        if (is_wp_error($branch)) return $branch;
        $token = $this->decrypt_token();
        if ($token === '') return new WP_Error('not_connected', 'Connect GitHub first.', ['status' => 409]);

        $repo_data = $this->github_request('GET', '/repos/' . $repo, $token);
        if (is_wp_error($repo_data)) return $repo_data;
        $branch_data = $this->github_request('GET', '/repos/' . $repo . '/branches/' . rawurlencode($branch), $token);
        if (is_wp_error($branch_data)) return $branch_data;
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
        return rest_ensure_response(['ok' => true, 'repo' => $repo, 'branch' => $branch, 'permission' => $permission]);
    }

    public function rest_disconnect() {
        $this->save_settings([
            'token' => '', 'repo' => '', 'branch' => '', 'login' => '', 'permission' => '', 'verified_at' => '',
        ]);
        return rest_ensure_response(['ok' => true]);
    }

    public function rest_git_init() {
        if ($this->git_available()) {
            return rest_ensure_response(['ok' => true, 'alreadyInitialized' => true]);
        }
        $root = $this->repo_root();
        if (!is_dir($root) || !is_writable($root)) {
            return new WP_Error('root_not_writable', 'Configured project root is not writable.', ['status' => 409]);
        }
        $result = $this->git(['init'], '', false);
        if (is_wp_error($result)) return $result;
        $settings = $this->settings();
        $branch = $settings['branch'] ?: 'main';
        $this->git(['symbolic-ref', 'HEAD', 'refs/heads/' . $branch], '', true);
        $this->write_devhub_gitignore();
        if ($settings['repo'] && $this->decrypt_token()) {
            $this->ensure_remote($settings['repo'], $this->decrypt_token());
        }
        return rest_ensure_response(['ok' => true, 'branch' => $branch]);
    }

    private function write_devhub_gitignore() {
        $root = $this->repo_root();
        $path = $root . DIRECTORY_SEPARATOR . '.gitignore';
        $marker = '# Tamiyouz Developer Hub safety rules';
        $rules = "\n{$marker}\nwp-config.php\n.env\n.env.*\n*.pem\n*.key\n*.p12\n*.pfx\n*.sql\n*.sql.gz\n*.log\nwp-content/uploads/\nwp-content/cache/\nwp-content/upgrade/\nwp-content/backups/\nwp-content/ai1wm-backups/\nnode_modules/\nvendor/\n.DS_Store\n";
        $current = file_exists($path) ? file_get_contents($path) : '';
        if (strpos((string) $current, $marker) === false) {
            file_put_contents($path, rtrim((string) $current) . $rules, LOCK_EX);
        }
    }

    private function require_ready() {
        if (!$this->git_available()) {
            return new WP_Error('git_not_initialized', 'Local Git repository is not initialized.', ['status' => 409]);
        }
        $settings = $this->settings();
        $token = $this->decrypt_token($settings['token']);
        if ($token === '' || !$settings['repo'] || !$settings['branch']) {
            return new WP_Error('github_incomplete', 'Connect GitHub and save a repository and branch first.', ['status' => 409]);
        }
        return [$settings, $token];
    }

    private function fetch_remote($settings, $token) {
        $remote = $this->ensure_remote($settings['repo'], $token);
        if (is_wp_error($remote)) return $remote;
        $branch = $settings['branch'];
        return $this->git([
            'fetch', '--prune', self::REMOTE,
            '+refs/heads/' . $branch . ':refs/remotes/' . self::REMOTE . '/' . $branch,
        ], $token, true, 180);
    }

    private function current_branch() {
        $branch = $this->git(['branch', '--show-current'], '', true);
        return is_wp_error($branch) ? '' : trim($branch['stdout']);
    }

    private function changed_files() {
        $status = $this->git(['status', '--porcelain=v1', '-z', '--untracked-files=all'], '', true);
        if (is_wp_error($status)) return $status;
        $raw = $status['stdout'];
        if ($raw === '') return [];
        $parts = explode("\0", $raw);
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
                $files[] = ['status' => trim($code), 'path' => $path, 'originalPath' => $original, 'direction' => 'local'];
            } else {
                $files[] = ['status' => trim($code) ?: 'M', 'path' => $path, 'direction' => 'local'];
            }
        }
        return $files;
    }

    private function remote_changed_files($remote_ref) {
        $head = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);
        if (is_wp_error($head) || ($head['exit'] ?? 1) !== 0) return [];
        $diff = $this->git(['diff', '--name-status', '-z', 'HEAD..' . $remote_ref], '', true);
        if (is_wp_error($diff) || ($diff['exit'] ?? 1) !== 0 || $diff['stdout'] === '') return [];
        $parts = explode("\0", $diff['stdout']);
        $files = [];
        for ($i = 0; $i < count($parts);) {
            $status = trim($parts[$i++] ?? '');
            if ($status === '') continue;
            $path = $parts[$i++] ?? '';
            if ($path === '') continue;
            if ($status[0] === 'R' || $status[0] === 'C') {
                $new = $parts[$i++] ?? '';
                if ($new !== '') {
                    $files[] = ['status' => $status, 'path' => $new, 'originalPath' => $path, 'direction' => 'remote'];
                }
            } else {
                $files[] = ['status' => $status, 'path' => $path, 'direction' => 'remote'];
            }
        }
        return $files;
    }

    private function blocked_path_reason($path) {
        $normalized = ltrim(str_replace('\\', '/', $path), '/');
        $lower = strtolower($normalized);
        $blocked = [
            '#(^|/)wp-config\.php$#' => 'WordPress configuration must never be committed.',
            '#(^|/)\.env(?:\.|$)#' => 'Environment files must never be committed.',
            '#(^|/)\.htpasswd$#' => 'Password files must never be committed.',
            '#(^|/)(?:id_rsa|id_ed25519)(?:\.|$)#' => 'Private SSH keys must never be committed.',
            '#\.(?:pem|key|p12|pfx|crt|cer|sql|sqlite|sqlite3|log)$#' => 'Sensitive credential/database/runtime file is blocked.',
            '#^wp-content/uploads/#' => 'Media uploads are excluded from source control.',
            '#^wp-content/(?:cache|upgrade|backups|ai1wm-backups)/#' => 'Runtime/cache/backup content is excluded.',
            '#(^|/)(?:node_modules|vendor)/#' => 'Generated dependency directory is excluded.',
            '#^\.git/#' => 'Git metadata is never included.',
        ];
        foreach ($blocked as $pattern => $reason) {
            if (preg_match($pattern, $lower)) return $reason;
        }
        return '';
    }

    private function scan_file_for_secrets($path) {
        $reason = $this->blocked_path_reason($path);
        if ($reason) return $reason;
        $full = $this->repo_root() . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $path);
        if (is_link($full)) return 'Symlinked files require manual review outside Developer Hub.';
        if (!is_file($full) || !is_readable($full)) return '';
        $size = filesize($full);
        if ($size === false || $size === 0 || $size > self::MAX_SCAN_BYTES) return '';
        $content = file_get_contents($full);
        if (!is_string($content) || strpos($content, "\0") !== false) return '';
        $patterns = [
            '/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/' => 'Private key material detected.',
            '/\bgithub_pat_[A-Za-z0-9_]{20,}\b/' => 'GitHub token detected.',
            '/\bgh[pousr]_[A-Za-z0-9]{20,}\b/' => 'GitHub token detected.',
            '/\bAKIA[0-9A-Z]{16}\b/' => 'AWS access key detected.',
            '/(?:password|passwd|secret|api[_-]?key|token)\s*[=:]\s*[\'\"][^\'\"]{12,}[\'\"]/i' => 'Possible embedded credential detected.',
        ];
        foreach ($patterns as $pattern => $message) {
            if (preg_match($pattern, $content)) return $message;
        }
        return '';
    }

    private function ahead_behind($remote_ref) {
        $local_head = $this->git(['rev-parse', '--verify', 'HEAD'], '', true);
        if (is_wp_error($local_head) || ($local_head['exit'] ?? 1) !== 0) {
            return ['localAhead' => 0, 'remoteAhead' => 0, 'hasHead' => false, 'remoteExists' => $this->remote_exists($remote_ref)];
        }
        $remote_exists = $this->remote_exists($remote_ref);
        if (!$remote_exists) {
            return ['localAhead' => 1, 'remoteAhead' => 0, 'hasHead' => true, 'remoteExists' => false];
        }
        $count = $this->git(['rev-list', '--left-right', '--count', 'HEAD...' . $remote_ref], '', true);
        if (is_wp_error($count) || ($count['exit'] ?? 1) !== 0) {
            return ['localAhead' => 0, 'remoteAhead' => 0, 'hasHead' => true, 'remoteExists' => true];
        }
        $parts = preg_split('/\s+/', trim($count['stdout']));
        return [
            'localAhead' => intval($parts[0] ?? 0),
            'remoteAhead' => intval($parts[1] ?? 0),
            'hasHead' => true,
            'remoteExists' => true,
        ];
    }

    private function remote_exists($remote_ref) {
        $check = $this->git(['show-ref', '--verify', '--quiet', 'refs/remotes/' . $remote_ref], '', true);
        return !is_wp_error($check) && ($check['exit'] ?? 1) === 0;
    }

    private function preview_action($action) {
        if (!in_array($action, ['push', 'pull', 'sync'], true)) {
            return new WP_Error('invalid_action', 'Invalid synchronization action.', ['status' => 400]);
        }
        $ready = $this->require_ready();
        if (is_wp_error($ready)) return $ready;
        [$settings, $token] = $ready;
        $branch = $settings['branch'];
        $current = $this->current_branch();
        $blocked = [];
        if ($current !== $branch) {
            $blocked[] = ['path' => '(branch)', 'reason' => 'Selected GitHub branch must match the current local branch.'];
        }

        $fetch = $this->fetch_remote($settings, $token);
        if (is_wp_error($fetch)) return $fetch;
        $remote_ref = self::REMOTE . '/' . $branch;
        $counts = $this->ahead_behind($remote_ref);
        $local_files = $this->changed_files();
        if (is_wp_error($local_files)) return $local_files;
        $remote_files = $counts['remoteExists'] ? $this->remote_changed_files($remote_ref) : [];
        foreach ($local_files as $file) {
            $reason = $this->scan_file_for_secrets($file['path']);
            if ($reason) $blocked[] = ['path' => $file['path'], 'reason' => $reason];
        }
        $dirty = count($local_files) > 0;
        $local_ahead = $counts['localAhead'];
        $remote_ahead = $counts['remoteAhead'];
        $state = 'synced';
        if ($local_ahead > 0 || $dirty) $state = 'local_changes';
        if ($remote_ahead > 0 && !$dirty && $local_ahead === 0) $state = 'remote_changes';
        if ($remote_ahead > 0 && ($dirty || $local_ahead > 0)) $state = 'both_changes';

        $expected = 'noop';
        if ($action === 'push') {
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
        $files = array_slice(array_merge($local_files, $remote_files), 0, 2000);
        $fingerprint_data = [
            'action' => $action, 'repo' => $settings['repo'], 'branch' => $branch, 'currentBranch' => $current,
            'state' => $state, 'expected' => $expected, 'localAhead' => $local_ahead, 'remoteAhead' => $remote_ahead,
            'files' => $files, 'blocked' => $blocked,
        ];
        $fingerprint = hash_hmac('sha256', wp_json_encode($fingerprint_data), wp_salt('auth'));
        return array_merge($fingerprint_data, [
            'syncState' => $state,
            'expectedAction' => $expected,
            'fileCount' => count($local_files) + count($remote_files),
            'truncated' => (count($local_files) + count($remote_files)) > 2000,
            'fingerprint' => $fingerprint,
        ]);
    }

    public function rest_preview(WP_REST_Request $request) {
        $action = sanitize_key($request->get_param('action'));
        $preview = $this->preview_action($action);
        if (is_wp_error($preview)) return $preview;
        return rest_ensure_response(['preview' => $preview]);
    }

    public function rest_execute(WP_REST_Request $request) {
        $action = sanitize_key($request->get_param('action'));
        $fingerprint = trim((string) $request->get_param('fingerprint'));
        $message = sanitize_text_field((string) $request->get_param('message'));
        $preview = $this->preview_action($action);
        if (is_wp_error($preview)) return $preview;
        if (!hash_equals($preview['fingerprint'], $fingerprint)) {
            return new WP_Error('review_expired', 'Project state changed after review. Run review again.', ['status' => 409]);
        }
        if (!empty($preview['blocked']) || $preview['expectedAction'] === 'blocked') {
            return new WP_Error('operation_blocked', 'Security review blocked this operation.', ['status' => 409, 'blocked' => $preview['blocked']]);
        }
        $ready = $this->require_ready();
        if (is_wp_error($ready)) return $ready;
        [$settings, $token] = $ready;
        $branch = $settings['branch'];
        $remote_ref = self::REMOTE . '/' . $branch;
        $expected = $preview['expectedAction'];
        $logs = [];
        if ($expected === 'noop') {
            return rest_ensure_response(['ok' => true, 'message' => 'Project is already synchronized.', 'logs' => [['type' => 'success', 'message' => 'No changes required.']]]);
        }
        if ($expected === 'fast_forward') {
            $logs[] = ['type' => 'info', 'message' => 'Applying fast-forward update from GitHub.'];
            $merge = $this->git(['merge', '--ff-only', $remote_ref], $token, false, 180);
            if (is_wp_error($merge)) return $merge;
            $logs[] = ['type' => 'success', 'message' => 'GitHub updates pulled successfully.'];
        } else {
            if ($expected === 'commit_and_push') {
                $this->write_devhub_gitignore();
                $add = $this->git(['add', '-A', '--', '.'], '', false, 180);
                if (is_wp_error($add)) return $add;
                $staged = $this->git(['diff', '--cached', '--quiet'], '', true);
                if (!is_wp_error($staged) && ($staged['exit'] ?? 0) !== 0) {
                    $commit_message = $message !== '' ? $message : 'Developer Hub sync ' . gmdate('Y-m-d H:i:s') . ' UTC';
                    $commit = $this->git([
                        '-c', 'user.name=Tamiyouz Developer Hub',
                        '-c', 'user.email=developer-hub@tamiyouz.local',
                        'commit', '-m', $commit_message,
                    ], '', false, 180);
                    if (is_wp_error($commit)) return $commit;
                    $logs[] = ['type' => 'success', 'message' => 'Local changes committed after security review.'];
                }
            }
            $push = $this->git(['push', self::REMOTE, 'HEAD:refs/heads/' . $branch], $token, false, 240);
            if (is_wp_error($push)) return $push;
            $logs[] = ['type' => 'success', 'message' => 'Push to GitHub completed successfully.'];
        }
        return rest_ensure_response(['ok' => true, 'message' => 'Operation completed successfully.', 'logs' => $logs, 'status' => $this->git_status_info()]);
    }
}

TAR_Developer_Hub::instance();
