#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

V6_FILENAME = "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V6.py"
V7_SIGNATURE = "TAM_JOIN_US_WORDPRESS_V7"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(
        description="Build Join Us -> WordPress migration V7 by adding cache-aware LiteSpeed purge controls to verified V6 output."
    )
    ap.add_argument("--v5-builder", required=True)
    ap.add_argument("--v6-builder", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--htaccess", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    v6 = Path(args.v6_builder)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not v6.is_file():
        raise SystemExit(f"V6 builder not found: {v6}")
    if v6.name != V6_FILENAME:
        raise SystemExit(f"Expected V6 builder filename {V6_FILENAME}, got {v6.name}")

    subprocess.run([
        sys.executable, str(v6),
        "--v5-builder", args.v5_builder,
        "--index", args.index,
        "--video", args.video,
        "--htaccess", args.htaccess,
        "--output-dir", str(out),
    ], check=True)

    manifest_path = out / "manifest.json"
    page_path = out / "page-join-us.php"
    if not manifest_path.is_file() or not page_path.is_file():
        raise SystemExit("V6 output incomplete")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("builder") != "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V6.py":
        raise SystemExit("Unexpected base manifest builder")
    if manifest.get("page_signature") != "TAM_JOIN_US_WORDPRESS_V6":
        raise SystemExit("Unexpected V6 page signature")
    if manifest.get("template_meta_strategy") != "DELETE_DURING_PREPARE_AND_ACTIVATE;RESTORE_PREVIOUS_VALUE_ON_ROLLBACK":
        raise SystemExit("V6 template-meta safety strategy missing")

    helper_name = manifest.get("helper_filename")
    if not helper_name:
        raise SystemExit("V6 manifest missing helper_filename")
    helper_path = out / helper_name
    if not helper_path.is_file():
        raise SystemExit("Generated V6 helper missing")

    helper = helper_path.read_text(encoding="utf-8")
    required = [
        "join-us-wp-bootstrap-v6-",
        "delete_post_meta($pageId, '_wp_page_template');",
        "delete_post_meta($p->ID, '_wp_page_template');",
        "failed_to_clear_stale_page_template_meta_prepare",
        "failed_to_clear_stale_page_template_meta_activate",
        "if ($action === 'cleanup') {",
        "flush_rewrite_rules(false);",
    ]
    missing = [marker for marker in required if marker not in helper]
    if missing:
        raise SystemExit(f"Unexpected V6 helper revision; missing markers: {missing}")

    # Add small helper functions immediately before runtime theme inspection.
    runtime_anchor = "$theme = (string) get_option('stylesheet');"
    if helper.count(runtime_anchor) != 1:
        raise SystemExit("Unexpected runtime anchor count")

    cache_functions = r'''function ju_cache_capabilities() {
    return [
        'litespeed_purge_url_hook' => (has_action('litespeed_purge_url') !== false),
        'litespeed_purge_post_hook' => (has_action('litespeed_purge_post') !== false),
        'litespeed_purge_all_hook' => (has_action('litespeed_purge_all') !== false),
        'litespeed_defined' => defined('LSCWP_V'),
    ];
}
function ju_purge_join_us_targeted($pageId = 0) {
    $caps = ju_cache_capabilities();
    $url = home_url('/join-us/');
    $triggered = [];
    if ($caps['litespeed_purge_url_hook']) {
        do_action('litespeed_purge_url', $url);
        $triggered[] = 'litespeed_purge_url';
    }
    if ($pageId > 0 && $caps['litespeed_purge_post_hook']) {
        do_action('litespeed_purge_post', (int) $pageId);
        $triggered[] = 'litespeed_purge_post';
    }
    if ($pageId > 0) clean_post_cache((int) $pageId);
    return ['capabilities' => $caps, 'url' => $url, 'triggered' => $triggered];
}
function ju_purge_litespeed_all() {
    $caps = ju_cache_capabilities();
    $triggered = false;
    if ($caps['litespeed_purge_all_hook']) {
        do_action('litespeed_purge_all', 'Tamiyouz Join Us migration V7 validation');
        $triggered = true;
    }
    return ['capabilities' => $caps, 'triggered' => $triggered];
}
'''
    helper = helper.replace(runtime_anchor, cache_functions + runtime_anchor, 1)

    # Make inspect expose cache capability only (no mutation).
    inspect_anchor = "        'state_exists' => (get_option($stateKey, null) !== null),"
    if helper.count(inspect_anchor) != 1:
        raise SystemExit("Unexpected inspect anchor count")
    helper = helper.replace(
        inspect_anchor,
        inspect_anchor + "\n        'cache_capabilities' => ju_cache_capabilities(),",
        1,
    )

    # Purge the specific Join Us URL/post immediately after activate+rewrite flush.
    activate_anchor = """    flush_rewrite_rules(false);
    clean_post_cache($p->ID);
    ju_out(['success' => true, 'action' => 'activate', 'page' => ju_snapshot(get_post($p->ID)), 'url_to_postid' => (int) url_to_postid(home_url('/join-us/'))]);"""
    activate_replacement = """    flush_rewrite_rules(false);
    clean_post_cache($p->ID);
    $cachePurge = ju_purge_join_us_targeted((int) $p->ID);
    ju_out(['success' => true, 'action' => 'activate', 'page' => ju_snapshot(get_post($p->ID)), 'url_to_postid' => (int) url_to_postid(home_url('/join-us/')), 'cache_purge' => $cachePurge]);"""
    if helper.count(activate_anchor) != 1:
        raise SystemExit("Unexpected activate cache anchor count")
    helper = helper.replace(activate_anchor, activate_replacement, 1)

    # Add explicit cache actions. purge_cache is targeted; purge_all_cache is fallback only.
    cleanup_anchor = "if ($action === 'cleanup') {"
    if helper.count(cleanup_anchor) != 1:
        raise SystemExit("Unexpected cleanup anchor count")
    cache_actions = r'''if ($action === 'purge_cache') {
    $p = ju_page();
    $pageId = $p ? (int) $p->ID : 0;
    ju_out(['success' => true, 'action' => 'purge_cache', 'cache_purge' => ju_purge_join_us_targeted($pageId)]);
}
if ($action === 'purge_all_cache') {
    ju_out(['success' => true, 'action' => 'purge_all_cache', 'cache_purge' => ju_purge_litespeed_all()]);
}
'''
    helper = helper.replace(cleanup_anchor, cache_actions + cleanup_anchor, 1)

    helper = helper.replace("join-us-wp-bootstrap-v6-", "join-us-wp-bootstrap-v7-", 1)
    helper = helper.replace("_tamiyouz_join_us_migration_v6_", "_tamiyouz_join_us_migration_v7_", 1)

    new_helper_name = helper_name.replace("join-us-wp-bootstrap-v6-", "join-us-wp-bootstrap-v7-", 1)
    if new_helper_name == helper_name:
        raise SystemExit("Failed to derive V7 helper filename")
    new_helper_path = out / new_helper_name
    helper_path.unlink()
    new_helper_path.write_text(helper, encoding="utf-8")

    page = page_path.read_text(encoding="utf-8")
    if page.count("TAM_JOIN_US_WORDPRESS_V6") != 1:
        raise SystemExit("Expected exactly one V6 signature")
    page = page.replace("TAM_JOIN_US_WORDPRESS_V6", V7_SIGNATURE, 1)
    page_path.write_text(page, encoding="utf-8")

    v7_helper = new_helper_path.read_text(encoding="utf-8")
    checks = [
        "has_action('litespeed_purge_url')",
        "has_action('litespeed_purge_post')",
        "has_action('litespeed_purge_all')",
        "do_action('litespeed_purge_url', $url);",
        "do_action('litespeed_purge_post', (int) $pageId);",
        "do_action('litespeed_purge_all', 'Tamiyouz Join Us migration V7 validation');",
        "if ($action === 'purge_cache') {",
        "if ($action === 'purge_all_cache') {",
        "delete_post_meta($pageId, '_wp_page_template');",
        "delete_post_meta($p->ID, '_wp_page_template');",
    ]
    absent = [marker for marker in checks if marker not in v7_helper]
    if absent:
        raise SystemExit(f"V7 helper verification failed: {absent}")

    manifest["builder"] = "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V7.py"
    manifest["base_builder"] = V6_FILENAME
    manifest["helper_filename"] = new_helper_name
    manifest["helper_sha256"] = sha256_bytes(v7_helper.encode("utf-8"))
    manifest["page_file_sha256"] = sha256_bytes(page_path.read_bytes())
    manifest["page_file_bytes"] = len(page_path.read_bytes())
    manifest["page_signature"] = V7_SIGNATURE
    if isinstance(manifest.get("state_key"), str):
        manifest["state_key"] = manifest["state_key"].replace(
            "_tamiyouz_join_us_migration_v6_", "_tamiyouz_join_us_migration_v7_", 1
        )
    manifest["cache_strategy"] = (
        "TARGETED_LITESPEED_PURGE_URL_AND_POST_ON_ACTIVATE;"
        "EXPLICIT_TARGETED_RETRY;OPTIONAL_PURGE_ALL_FALLBACK"
    )
    manifest["changes"] = list(manifest.get("changes", [])) + [
        "Expose LiteSpeed purge-hook availability during inspect.",
        "Trigger LiteSpeed purge_url + purge_post for Join Us immediately after activation when hooks are registered.",
        "Provide explicit targeted purge_cache action for retry before rollback.",
        "Provide purge_all_cache only as a last-resort LiteSpeed fallback.",
        "Use inert V7 route signature TAM_JOIN_US_WORDPRESS_V7.",
    ]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    redacted = dict(manifest)
    if "one_time_token" in redacted:
        redacted["one_time_token"] = "REDACTED"
    print(json.dumps(redacted, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
