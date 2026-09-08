#!/usr/bin/env python3
import argparse
import hashlib
import json
import secrets
from pathlib import Path

EXPECTED_IFRAME = "https://careers.tamiyouzplaform.com/"
EXPECTED_RAKAN = "https://careers.tamiyouzplaform.com/api/v1/rakan/chat"
EXPECTED_VIDEO = "/join-us/video-header.mp4?v=6"
EXPECTED_NOTIFY = "fetch('/join-us/notify.php'"
EXPECTED_FORM = "e.data.type === 'formSubmission'"
TEMPLATE_REL = "page-templates/template-join-us.php"
THEME_SLUG = "thegem-elementor"

DENY_HTACCESS = """Options -Indexes
<IfModule mod_authz_core.c>
    Require all denied
</IfModule>
<IfModule !mod_authz_core.c>
    Order Allow,Deny
    Deny from all
</IfModule>
"""

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def php_string(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

def main():
    ap = argparse.ArgumentParser(description="Build FTP/HTTP migration assets for Join Us -> WordPress V3.")
    ap.add_argument("--index", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--expected-index-bytes", type=int, default=42325)
    ap.add_argument("--expected-index-sha256", default="9ffd152f68e1b377ef72377fcbc340f40759e3ee9945035fec87a2332addc045")
    ap.add_argument("--token", default=None)
    args = ap.parse_args()

    src = Path(args.index)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = src.read_bytes()
    actual_sha = sha256_bytes(raw)

    if len(raw) != args.expected_index_bytes:
        raise SystemExit(f"Refusing source size mismatch: expected {args.expected_index_bytes}, got {len(raw)}")
    if actual_sha.lower() != args.expected_index_sha256.lower():
        raise SystemExit(f"Refusing source SHA256 mismatch: expected {args.expected_index_sha256}, got {actual_sha}")

    html = raw.decode("utf-8")
    required = {
        "careers_iframe": EXPECTED_IFRAME,
        "rakan_endpoint": EXPECTED_RAKAN,
        "video_url": EXPECTED_VIDEO,
        "legacy_notify_hook": EXPECTED_NOTIFY,
        "form_submission_postmessage": EXPECTED_FORM,
    }
    counts = {name: html.count(marker) for name, marker in required.items()}
    bad = {k: v for k, v in counts.items() if v < 1}
    if bad:
        raise SystemExit(f"Required integration marker(s) missing: {bad}")
    if counts["video_url"] != 1:
        raise SystemExit(f"Expected exactly one legacy video URL occurrence, found {counts['video_url']}")

    wp_video = "<?php echo esc_url(get_template_directory_uri() . '/assets/join-us/video-header.mp4?v=6'); ?>"
    transformed = html.replace(EXPECTED_VIDEO, wp_video, 1)
    header = """<?php
/*
Template Name: Tamiyouz Join Us
Template Post Type: page
*/
defined('ABSPATH') || exit;
?>
"""
    template = (header + transformed).encode("utf-8")
    template_path = out / "template-join-us.php"
    template_path.write_bytes(template)

    token = args.token or secrets.token_urlsafe(48)
    nonce = secrets.token_hex(8)
    helper_name = f"join-us-wp-bootstrap-{nonce}.php"
    state_key = f"_tamiyouz_join_us_migration_{nonce}"

    helper = f'''<?php
// Tamiyouz Join Us one-time WordPress migration bootstrap V3. DELETE immediately after migration.
header('Content-Type: application/json; charset=utf-8');
$expectedToken = {php_string(token)};
$providedToken = isset($_GET['token']) ? (string) $_GET['token'] : '';
if ($providedToken === '' || !hash_equals($expectedToken, $providedToken)) {{
    http_response_code(403);
    echo json_encode(['success' => false, 'error' => 'forbidden']);
    exit;
}}
require_once __DIR__ . '/wp-load.php';
$stateKey = {php_string(state_key)};
$templateRel = {php_string(TEMPLATE_REL)};
$expectedTheme = {php_string(THEME_SLUG)};
$action = isset($_GET['action']) ? (string) $_GET['action'] : 'inspect';
function ju_out($payload, $status = 200) {{
    http_response_code($status);
    echo wp_json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}}
function ju_find_page() {{
    $posts = get_posts([
        'name' => 'join-us', 'post_type' => 'page',
        'post_status' => ['publish','future','draft','pending','private','trash'],
        'numberposts' => 5, 'orderby' => 'ID', 'order' => 'ASC', 'suppress_filters' => false,
    ]);
    if (count($posts) > 1) ju_out(['success' => false, 'error' => 'multiple_join_us_pages', 'ids' => array_map(fn($p) => $p->ID, $posts)], 409);
    return count($posts) === 1 ? $posts[0] : null;
}}
function ju_snapshot($p) {{
    if (!$p) return null;
    return [
        'ID' => (int) $p->ID,
        'post_status' => (string) $p->post_status,
        'post_name' => (string) $p->post_name,
        'post_title' => (string) $p->post_title,
        'page_template' => (string) get_post_meta($p->ID, '_wp_page_template', true),
    ];
}}
$theme = get_option('stylesheet');
$blogId = function_exists('get_current_blog_id') ? get_current_blog_id() : 1;
if ($action === 'inspect') {{
    $p = ju_find_page();
    ju_out(['success' => true, 'action' => 'inspect', 'theme' => $theme, 'expected_theme' => $expectedTheme, 'theme_ok' => ($theme === $expectedTheme), 'blog_id' => $blogId, 'is_multisite' => is_multisite(), 'page' => ju_snapshot($p), 'state_exists' => (get_option($stateKey, null) !== null)]);
}}
if ($theme !== $expectedTheme) ju_out(['success' => false, 'error' => 'unexpected_active_theme', 'theme' => $theme, 'expected' => $expectedTheme], 409);
if ($action === 'prepare') {{
    if (get_option($stateKey, null) !== null) ju_out(['success' => false, 'error' => 'migration_state_already_exists'], 409);
    $existing = ju_find_page();
    $state = ['had_existing_page' => (bool) $existing, 'before' => ju_snapshot($existing), 'created_page_id' => null];
    if ($existing) {{
        $pageId = (int) $existing->ID;
        if ($existing->post_status === 'trash') {{
            $restore = wp_untrash_post($pageId);
            if (!$restore) ju_out(['success' => false, 'error' => 'failed_to_untrash_existing_page'], 500);
        }}
        $r = wp_update_post(['ID' => $pageId, 'post_name' => 'join-us', 'post_status' => 'draft'], true);
        if (is_wp_error($r)) ju_out(['success' => false, 'error' => 'existing_page_prepare_failed', 'message' => $r->get_error_message()], 500);
    }} else {{
        $pageId = wp_insert_post(['post_type' => 'page', 'post_title' => 'انضم لفريقنا', 'post_name' => 'join-us', 'post_status' => 'draft'], true);
        if (is_wp_error($pageId)) ju_out(['success' => false, 'error' => 'page_create_failed', 'message' => $pageId->get_error_message()], 500);
        $state['created_page_id'] = (int) $pageId;
    }}
    update_post_meta($pageId, '_wp_page_template', $templateRel);
    if (!add_option($stateKey, $state, '', false)) ju_out(['success' => false, 'error' => 'failed_to_save_migration_state'], 500);
    clean_post_cache($pageId);
    ju_out(['success' => true, 'action' => 'prepare', 'page_id' => (int) $pageId, 'page_status' => get_post_status($pageId), 'template' => get_post_meta($pageId, '_wp_page_template', true)]);
}}
if ($action === 'activate') {{
    $state = get_option($stateKey, null);
    if (!is_array($state)) ju_out(['success' => false, 'error' => 'missing_migration_state'], 409);
    $id = !empty($state['created_page_id']) ? (int) $state['created_page_id'] : (int) ($state['before']['ID'] ?? 0);
    $p = $id ? get_post($id) : null;
    if (!$p) ju_out(['success' => false, 'error' => 'page_missing_during_activate'], 409);
    $result = wp_update_post(['ID' => $p->ID, 'post_name' => 'join-us', 'post_status' => 'publish'], true);
    if (is_wp_error($result)) ju_out(['success' => false, 'error' => 'page_activate_failed', 'message' => $result->get_error_message()], 500);
    update_post_meta($p->ID, '_wp_page_template', $templateRel);
    flush_rewrite_rules(false);
    clean_post_cache($p->ID);
    ju_out(['success' => true, 'action' => 'activate', 'page' => ju_snapshot(get_post($p->ID))]);
}}
if ($action === 'rollback') {{
    $state = get_option($stateKey, null);
    if (!is_array($state)) ju_out(['success' => true, 'action' => 'rollback', 'message' => 'no_state_nothing_to_rollback']);
    if (!empty($state['had_existing_page']) && !empty($state['before']['ID'])) {{
        $b = $state['before']; $id = (int) $b['ID'];
        if (($b['post_status'] ?? '') === 'trash') {{
            wp_trash_post($id);
        }} else {{
            $r = wp_update_post(['ID' => $id, 'post_status' => $b['post_status'], 'post_name' => $b['post_name'], 'post_title' => $b['post_title']], true);
            if (is_wp_error($r)) ju_out(['success' => false, 'error' => 'rollback_page_restore_failed', 'message' => $r->get_error_message()], 500);
        }}
        if (($b['page_template'] ?? '') !== '') update_post_meta($id, '_wp_page_template', $b['page_template']); else delete_post_meta($id, '_wp_page_template');
    }} elseif (!empty($state['created_page_id'])) {{
        wp_delete_post((int) $state['created_page_id'], true);
    }}
    delete_option($stateKey);
    flush_rewrite_rules(false);
    ju_out(['success' => true, 'action' => 'rollback']);
}}
if ($action === 'cleanup') {{
    delete_option($stateKey);
    ju_out(['success' => true, 'action' => 'cleanup', 'delete_this_helper_via_ftp' => basename(__FILE__)]);
}}
ju_out(['success' => false, 'error' => 'unknown_action'], 400);
'''
    helper_path = out / helper_name
    helper_path.write_text(helper, encoding="utf-8")

    deny_path = out / "backup-deny.htaccess"
    deny_path.write_text(DENY_HTACCESS, encoding="utf-8")

    manifest = {
        "builder": "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V3.py",
        "source_index_bytes": len(raw),
        "source_index_sha256": actual_sha,
        "template_bytes": len(template),
        "template_sha256": sha256_bytes(template),
        "template_relative_path": TEMPLATE_REL,
        "theme_asset_video_relative_path": "assets/join-us/video-header.mp4",
        "helper_filename": helper_name,
        "helper_sha256": sha256_bytes(helper.encode("utf-8")),
        "backup_deny_filename": "backup-deny.htaccess",
        "backup_deny_sha256": sha256_bytes(DENY_HTACCESS.encode("utf-8")),
        "integration_marker_counts": counts,
        "only_intentional_html_change": "replace exactly one /join-us/video-header.mp4?v=6 URL with theme asset URL",
        "one_time_token": token,
        "state_key": state_key,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    redacted = dict(manifest)
    redacted["one_time_token"] = "REDACTED"
    print(json.dumps(redacted, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
