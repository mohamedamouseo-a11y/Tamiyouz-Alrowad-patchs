#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

V5_FILENAME = "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V5.py"
V6_SIGNATURE = "TAM_JOIN_US_WORDPRESS_V6"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Build Join Us -> WordPress migration V6 by hardening verified V5 output against stale _wp_page_template meta.")
    ap.add_argument("--v5-builder", required=True)
    ap.add_argument("--index", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--htaccess", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    v5 = Path(args.v5_builder)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not v5.is_file():
        raise SystemExit(f"V5 builder not found: {v5}")
    if v5.name != V5_FILENAME:
        raise SystemExit(f"Expected V5 builder filename {V5_FILENAME}, got {v5.name}")

    subprocess.run([
        sys.executable, str(v5),
        "--index", args.index,
        "--video", args.video,
        "--htaccess", args.htaccess,
        "--output-dir", str(out),
    ], check=True)

    manifest_path = out / "manifest.json"
    page_path = out / "page-join-us.php"
    if not manifest_path.is_file() or not page_path.is_file():
        raise SystemExit("V5 output incomplete")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    helper_name = manifest.get("helper_filename")
    if not helper_name:
        raise SystemExit("V5 manifest missing helper_filename")
    helper_path = out / helper_name
    if not helper_path.is_file():
        raise SystemExit("Generated V5 helper missing")

    helper = helper_path.read_text(encoding="utf-8")
    required = [
        "page_template_meta' => (string) get_post_meta($p->ID, '_wp_page_template', true)",
        "$state = ['had_existing_page' => (bool) $existing, 'before' => ju_snapshot($existing), 'created_page_id' => null];",
        "if (!add_option($stateKey, $state, '', false)) ju_out(['success' => false, 'error' => 'failed_to_save_migration_state'], 500);",
        "$r = wp_update_post(['ID' => $p->ID, 'post_name' => 'join-us', 'post_status' => 'publish'], true);",
        "if (($b['page_template_meta'] ?? '') !== '') update_post_meta($id, '_wp_page_template', $b['page_template_meta']); else delete_post_meta($id, '_wp_page_template');",
    ]
    missing = [x for x in required if x not in helper]
    if missing:
        raise SystemExit(f"Unexpected V5 helper revision; missing markers: {missing}")

    prepare_anchor = "    if (!add_option($stateKey, $state, '', false)) ju_out(['success' => false, 'error' => 'failed_to_save_migration_state'], 500);"
    prepare_insert = """    delete_post_meta($pageId, '_wp_page_template');
    if ((string) get_post_meta($pageId, '_wp_page_template', true) !== '') {
        ju_out(['success' => false, 'error' => 'failed_to_clear_stale_page_template_meta_prepare'], 500);
    }
    if (!add_option($stateKey, $state, '', false)) ju_out(['success' => false, 'error' => 'failed_to_save_migration_state'], 500);"""
    if helper.count(prepare_anchor) != 1:
        raise SystemExit("Unexpected prepare anchor count")
    helper = helper.replace(prepare_anchor, prepare_insert, 1)

    activate_anchor = """    if (is_wp_error($r)) ju_out(['success' => false, 'error' => 'page_activate_failed', 'message' => $r->get_error_message()], 500);
    flush_rewrite_rules(false);"""
    activate_insert = """    if (is_wp_error($r)) ju_out(['success' => false, 'error' => 'page_activate_failed', 'message' => $r->get_error_message()], 500);
    delete_post_meta($p->ID, '_wp_page_template');
    if ((string) get_post_meta($p->ID, '_wp_page_template', true) !== '') {
        ju_out(['success' => false, 'error' => 'failed_to_clear_stale_page_template_meta_activate'], 500);
    }
    flush_rewrite_rules(false);"""
    if helper.count(activate_anchor) != 1:
        raise SystemExit("Unexpected activate anchor count")
    helper = helper.replace(activate_anchor, activate_insert, 1)

    helper = helper.replace("join-us-wp-bootstrap-v5-", "join-us-wp-bootstrap-v6-", 1)
    helper = helper.replace("_tamiyouz_join_us_migration_v5_", "_tamiyouz_join_us_migration_v6_", 1)

    new_helper_name = helper_name.replace("join-us-wp-bootstrap-v5-", "join-us-wp-bootstrap-v6-", 1)
    new_helper_path = out / new_helper_name
    helper_path.unlink()
    new_helper_path.write_text(helper, encoding="utf-8")

    page = page_path.read_text(encoding="utf-8")
    if page.count("TAM_JOIN_US_WORDPRESS_V5") != 1:
        raise SystemExit("Expected exactly one V5 signature")
    page = page.replace("TAM_JOIN_US_WORDPRESS_V5", V6_SIGNATURE, 1)
    page_path.write_text(page, encoding="utf-8")

    v6_helper = new_helper_path.read_text(encoding="utf-8")
    checks = [
        "delete_post_meta($pageId, '_wp_page_template');",
        "delete_post_meta($p->ID, '_wp_page_template');",
        "failed_to_clear_stale_page_template_meta_prepare",
        "failed_to_clear_stale_page_template_meta_activate",
        "update_post_meta($id, '_wp_page_template', $b['page_template_meta'])",
    ]
    if any(marker not in v6_helper for marker in checks):
        raise SystemExit("V6 helper verification failed")

    manifest["builder"] = "BUILD-JOIN-US-WORDPRESS-FTP-MIGRATION-V6.py"
    manifest["base_builder"] = V5_FILENAME
    manifest["helper_filename"] = new_helper_name
    manifest["helper_sha256"] = sha256_bytes(v6_helper.encode("utf-8"))
    manifest["page_file_sha256"] = sha256_bytes(page_path.read_bytes())
    manifest["page_file_bytes"] = len(page_path.read_bytes())
    manifest["page_signature"] = V6_SIGNATURE
    if isinstance(manifest.get("state_key"), str):
        manifest["state_key"] = manifest["state_key"].replace("_tamiyouz_join_us_migration_v5_", "_tamiyouz_join_us_migration_v6_", 1)
    manifest["template_meta_strategy"] = "DELETE_DURING_PREPARE_AND_ACTIVATE;RESTORE_PREVIOUS_VALUE_ON_ROLLBACK"
    manifest["changes"] = list(manifest.get("changes", [])) + [
        "Clear stale _wp_page_template during prepare after snapshot.",
        "Clear and verify _wp_page_template again during activate.",
        "Rollback restores the previous _wp_page_template value.",
        "Use inert V6 route signature TAM_JOIN_US_WORDPRESS_V6.",
    ]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    redacted = dict(manifest)
    if "one_time_token" in redacted:
        redacted["one_time_token"] = "REDACTED"
    print(json.dumps(redacted, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
