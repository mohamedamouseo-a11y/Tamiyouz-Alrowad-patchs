#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import secrets
from pathlib import Path

EXPECTED_INDEX_BYTES = 42325
EXPECTED_INDEX_SHA256 = "9ffd152f68e1b377ef72377fcbc340f40759e3ee9945035fec87a2332addc045"
EXPECTED_VIDEO_BYTES = 1034533
EXPECTED_VIDEO_SHA256 = "1207773ab6194f8b29ed03e08d184dce7dfe3140ebbc8235dedf00e9c8067fc7"
EXPECTED_IFRAME = "https://careers.tamiyouzplaform.com/"
EXPECTED_RAKAN = "https://careers.tamiyouzplaform.com/api/v1/rakan/chat"
EXPECTED_VIDEO = "/join-us/video-header.mp4?v=6"
EXPECTED_NOTIFY = "fetch('/join-us/notify.php'"
EXPECTED_FORM = "e.data.type === 'formSubmission'"
THEME_SLUG = "thegem-elementor"
PAGE_FILE = "page-join-us.php"
SIGNATURE = "TAM_JOIN_US_WORDPRESS_V5"

DENY_HTACCESS = """Options -Indexes
<IfModule mod_authz_core.c>
    Require all denied
</IfModule>
<IfModule !mod_authz_core.c>
    Order Allow,Deny
    Deny from all
</IfModule>
"""

CAREERS_BLOCK_RE = re.compile(
    r"(?ms)^# BEGIN Careers Page\s*\r?\n.*?^# END Careers Page\s*(?:\r?\n)?"
)
CAREERS_RULE_RE = re.compile(r"(?m)^\s*RewriteRule\s+\^join-us/\?\$\s+/join-us/index\.html\s+\[L\]\s*$")
WP_FRONT_RE = re.compile(r"(?m)^\s*RewriteRule\s+\.\s+index\.php\s+\[L\]\s*$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def php_string(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main():
    ap = argparse.ArgumentParser(description="Build Join Us -> WordPress migration V5 with safe .htaccess cutover.")
    ap.add_argument("--index", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--htaccess", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--token", default=None)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    index_raw = Path(args.index).read_bytes()
    video_raw = Path(args.video).read_bytes()
    ht_raw = Path(args.htaccess).read_bytes()

    if len(index_raw) != EXPECTED_INDEX_BYTES:
        raise SystemExit(f"index.html size mismatch: expected {EXPECTED_INDEX_BYTES}, got {len(index_raw)}")
    if sha256_bytes(index_raw) != EXPECTED_INDEX_SHA256:
        raise SystemExit("index.html SHA256 mismatch")
    if len(video_raw) != EXPECTED_VIDEO_BYTES:
        raise SystemExit(f"video size mismatch: expected {EXPECTED_VIDEO_BYTES}, got {len(video_raw)}")
    if sha256_bytes(video_raw) != EXPECTED_VIDEO_SHA256:
        raise SystemExit("video SHA256 mismatch")

    html = index_raw.decode("utf-8")
    required = {
        "careers_iframe": EXPECTED_IFRAME,
        "rakan_endpoint": EXPECTED_RAKAN,
        "video_url": EXPECTED_VIDEO,
        "legacy_notify_hook": EXPECTED_NOTIFY,
        "form_submission_postmessage": EXPECTED_FORM,
    }
    counts = {k: html.count(v) for k, v in required.items()}
    if any(v < 1 for v in counts.values()):
        raise SystemExit(f"Required integration marker missing: {counts}")
    if counts["video_url"] != 1:
        raise SystemExit(f"Expected exactly one legacy video URL, found {counts['video_url']}")

    ht_text = ht_raw.decode("utf-8")
    blocks = CAREERS_BLOCK_RE.findall(ht_text)
    if len(blocks) != 1:
        raise SystemExit(f"Expected exactly one '# BEGIN Careers Page' block, found {len(blocks)}")
    block = blocks[0]
    if not CAREERS_RULE_RE.search(block):
        raise SystemExit("Careers Page block does not contain the exact join-us rewrite rule")
    if not WP_FRONT_RE.search(ht_text):
        raise SystemExit("WordPress front-controller RewriteRule . index.php [L] not found; refusing .htaccess change")

    new_ht = CAREERS_BLOCK_RE.sub("", ht_text, count=1)
    if CAREERS_RULE_RE.search(new_ht):
        raise SystemExit("join-us legacy rewrite rule still present after transform")
    if not WP_FRONT_RE.search(new_ht):
        raise SystemExit("WordPress front-controller rule was lost during transform")

    wp_video = "<?php echo esc_url(get_stylesheet_directory_uri() . '/assets/join-us/video-header.mp4?v=6'); ?>"
    transformed = html.replace(EXPECTED_VIDEO, wp_video, 1)
    page_php = (
        "<?php\n"
        "defined('ABSPATH') || exit;\n"
        "?>\n"
        f"<!-- {SIGNATURE} -->\n"
        + transformed
    ).encode("utf-8")
    (out / PAGE_FILE).write_bytes(page_php)
    (out / ".htaccess.after").write_text(new_ht, encoding="utf-8")
    (out / "backup-deny.htaccess").write_text(DENY_HTACCESS, encoding="utf-8")

    token = args.token or secrets.token_urlsafe(48)
    nonce = secrets.token_hex(8)
    helper_name = f"join-us-wp-bootstrap-v5-{nonce}.php"
    state_key = f"_tamiyouz_join_us_migration_v5_{nonce}"

    helper = f'''<?php
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
$expectedTheme = {php_string(THEME_SLUG)};
$pageFile = {php_string(PAGE_FILE)};
$action = isset($_GET['action']) ? (string) $_GET['action'] : 'inspect';
function ju_out($payload, $status = 200) {{
    http_response_code($status);
    echo wp_json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}}
function ju_pages() {{
    return get_posts([
        'name' => 'join-us', 'post_type' => 'page',
        'post_status' => ['publish','future','draft','pending','private','trash'],
        'numberposts' => 10, 'orderby' => 'ID', 'order' => 'ASC', 'suppress_filters' => true,
    ]);
}}
function ju_page() {{
    $posts = ju_pages();
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
        'page_template_meta' => (string) get_post_meta($p->ID, '_wp_page_template', true),
    ];
}}
$theme = (string) get_option('stylesheet');
$template = (string) get_option('template');
$stylesheetDir = get_stylesheet_directory();
$templateDir = get_template_directory();
$located = locate_template([$pageFile], false, false);
if ($action === 'inspect') {{
    $p = ju_page();
    ju_out([
        'success' => true,
        'action' => 'inspect',
        'theme' => $theme,
        'template_option' => $template,
        'expected_theme' => $expectedTheme,
        'theme_ok' => ($theme === $expectedTheme),
        'blog_id' => function_exists('get_current_blog_id') ? get_current_blog_id() : 1,
        'is_multisite' => is_multisite(),
        'home_url' => home_url('/'),
        'site_url' => site_url('/'),
        'stylesheet_directory' => $stylesheetDir,
        'template_directory' => $templateDir,
        'page_file_exists_stylesheet' => file_exists(trailingslashit($stylesheetDir) . $pageFile),
        'page_file_exists_template' => file_exists(trailingslashit($templateDir) . $pageFile),
        'page_file_located' => $located,
        'page' => ju_snapshot($p),
        'url_to_postid' => (int) url_to_postid(home_url('/join-us/')),
        'state_exists' => (get_option($stateKey, null) !== null),
    ]);
}}
if ($theme !== $expectedTheme) ju_out(['success' => false, 'error' => 'unexpected_active_stylesheet', 'theme' => $theme], 409);
if (!$located || basename($located) !== $pageFile) ju_out(['success' => false, 'error' => 'page_join_us_not_locatable', 'located' => $located], 409);
if ($action === 'prepare') {{
    if (get_option($stateKey, null) !== null) ju_out(['success' => false, 'error' => 'migration_state_already_exists'], 409);
    $existing = ju_page();
    $state = ['had_existing_page' => (bool) $existing, 'before' => ju_snapshot($existing), 'created_page_id' => null];
    if ($existing) {{
        $pageId = (int) $existing->ID;
        if ($existing->post_status === 'trash' && !wp_untrash_post($pageId)) ju_out(['success' => false, 'error' => 'failed_to_untrash_existing_page'], 500);
        $r = wp_update_post(['ID' => $pageId, 'post_name' => 'join-us', 'post_status' => 'draft'], true);
        if (is_wp_error($r)) ju_out(['success' => false, 'error' => 'existing_page_prepare_failed', 'message' => $r->get_error_message()], 500);
    }} else {{
        $pageId = wp_insert_post(['post_type' => 'page', 'post_title' => 'انضم لفريقنا', 'post_name' => 'join-us', 'post_status' => 'draft'], true);
        if (is_wp_error($pageId)) ju_out(['success' => false, 'error' => 'page_create_failed', 'message' => $pageId->get_error_message()], 500);
        $state['created_page_id'] = (int) $pageId;
    }}
    if (!add_option($stateKey, $state, '', false)) ju_out(['success' => false, 'error' => 'failed_to_save_migration_state'], 500);
    clean_post_cache($pageId);
    ju_out(['success' => true, 'action' => 'prepare', 'page' => ju_snapshot(get_post($pageId))]);
}}
if ($action === 'activate') {{
    $state = get_option($stateKey, null);
    if (!is_array($state)) ju_out(['success' => false, 'error' => 'missing_migration_state'], 409);
    $id = !empty($state['created_page_id']) ? (int) $state['created_page_id'] : (int) ($state['before']['ID'] ?? 0);
    $p = $id ? get_post($id) : null;
    if (!$p) ju_out(['success' => false, 'error' => 'page_missing_during_activate'], 409);
    $r = wp_update_post(['ID' => $p->ID, 'post_name' => 'join-us', 'post_status' => 'publish'], true);
    if (is_wp_error($r)) ju_out(['success' => false, 'error' => 'page_activate_failed', 'message' => $r->get_error_message()], 500);
    flush_rewrite_rules(false);
    clean_post_cache($p->ID);
    ju_out(['success' => true, 'action' => 'activate', 'page' => ju_snapshot(get_post($p->ID)), 'url_to_postid' => (int) url_to_postid(home_url('/join-us/'))]);
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
        if (($b['page_template_meta'] ?? '') !== '') update_post_meta($id, '_wp_page_template', $b['page_template_meta']); else delete_post_meta($id, '_wp_page_template');
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
    (out / helper_name).write_text(helper, encoding="utf-8")

    manifest = {
        "builder": "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V5.py",
        "source_index_bytes": len(index_raw),
        "source_index_sha256": sha256_bytes(index_raw),
        "source_video_bytes": len(video_raw),
        "source_video_sha256": sha256_bytes(video_raw),
        "htaccess_before_bytes": len(ht_raw),
        "htaccess_before_sha256": sha256_bytes(ht_raw),
        "htaccess_after_bytes": len(new_ht.encode('utf-8')),
        "htaccess_after_sha256": sha256_bytes(new_ht.encode('utf-8')),
        "removed_careers_block_sha256": sha256_bytes(block.encode('utf-8')),
        "page_file": PAGE_FILE,
        "page_file_bytes": len(page_php),
        "page_file_sha256": sha256_bytes(page_php),
        "page_signature": SIGNATURE,
        "helper_filename": helper_name,
        "helper_sha256": sha256_bytes(helper.encode('utf-8')),
        "backup_deny_sha256": sha256_bytes(DENY_HTACCESS.encode('utf-8')),
        "integration_marker_counts": counts,
        "changes": [
            "Remove exactly one '# BEGIN Careers Page' ... '# END Careers Page' .htaccess block containing RewriteRule ^join-us/?$ /join-us/index.html [L]",
            "Preserve WordPress front-controller rule",
            "Use page-join-us.php in active stylesheet directory",
            "Replace exactly one local legacy video URL with theme asset URL",
            "Add inert V5 HTML signature comment",
        ],
        "one_time_token": token,
        "state_key": state_key,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    redacted = dict(manifest)
    redacted["one_time_token"] = "REDACTED"
    print(json.dumps(redacted, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
