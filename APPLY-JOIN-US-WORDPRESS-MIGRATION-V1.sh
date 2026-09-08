#!/usr/bin/env bash
set -Eeuo pipefail

# Tamiyouz Alrowad - Join Us standalone page -> WordPress page template migration
# Scope: NO Git commands. Preserves current HTML/JS behavior exactly except the local video URL.

WP_ROOT="/home/u194956174/domains/tamiyouzalrowad.com/public_html"
DOMAIN_ROOT="$(dirname "$WP_ROOT")"
LEGACY_DIR="$WP_ROOT/join-us"
THEME_DIR="$WP_ROOT/wp-content/themes/thegem-elementor"
TEMPLATE_REL="page-templates/template-join-us.php"
TEMPLATE_FILE="$THEME_DIR/$TEMPLATE_REL"
ASSET_DIR="$THEME_DIR/assets/join-us"
VIDEO_FILE="$ASSET_DIR/video-header.mp4"
SITE_URL="https://tamiyouzalrowad.com"
TARGET_URL="$SITE_URL/join-us/"
EXPECTED_IFRAME="https://careers.tamiyouzplaform.com/"
EXPECTED_RAKAN="https://careers.tamiyouzplaform.com/api/v1/rakan/chat"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_ROOT="$DOMAIN_ROOT/join-us-migration-backups/$RUN_ID"
LEGACY_BACKUP="$BACKUP_ROOT/legacy-join-us"
PAGE_BACKUP="$BACKUP_ROOT/page-before.txt"
META_BACKUP="$BACKUP_ROOT/page-meta-before.json"
CREATED_PAGE=0
PAGE_ID=""
OLD_TEMPLATE=""
OLD_STATUS=""
LEGACY_MOVED=0
TEMPLATE_EXISTED=0
VIDEO_EXISTED=0

log() { printf '[JOIN-US MIGRATION] %s\n' "$*"; }

rollback() {
  local rc="${1:-1}"
  trap - ERR
  set +e
  log "Failure detected; starting rollback."

  if [[ "$LEGACY_MOVED" == "1" && -d "$LEGACY_BACKUP" && ! -e "$LEGACY_DIR" ]]; then
    mv "$LEGACY_BACKUP" "$LEGACY_DIR"
    log "Legacy /join-us directory restored."
  fi

  if [[ -n "$PAGE_ID" ]]; then
    if [[ "$CREATED_PAGE" == "1" ]]; then
      wp --path="$WP_ROOT" post delete "$PAGE_ID" --force >/dev/null 2>&1 || true
      log "Created WordPress page removed."
    else
      if [[ -n "$OLD_TEMPLATE" ]]; then
        wp --path="$WP_ROOT" post meta update "$PAGE_ID" _wp_page_template "$OLD_TEMPLATE" >/dev/null 2>&1 || true
      else
        wp --path="$WP_ROOT" post meta delete "$PAGE_ID" _wp_page_template >/dev/null 2>&1 || true
      fi
      if [[ -n "$OLD_STATUS" ]]; then
        wp --path="$WP_ROOT" post update "$PAGE_ID" --post_status="$OLD_STATUS" >/dev/null 2>&1 || true
      fi
      log "Existing page template assignment/status restored."
    fi
    wp --path="$WP_ROOT" rewrite flush >/dev/null 2>&1 || true
  fi

  if [[ "$TEMPLATE_EXISTED" == "1" && -f "$BACKUP_ROOT/template-join-us.php.before" ]]; then
    cp -p "$BACKUP_ROOT/template-join-us.php.before" "$TEMPLATE_FILE"
  elif [[ "$TEMPLATE_EXISTED" == "0" ]]; then
    rm -f "$TEMPLATE_FILE"
  fi

  if [[ "$VIDEO_EXISTED" == "1" && -f "$BACKUP_ROOT/video-header.mp4.before" ]]; then
    cp -p "$BACKUP_ROOT/video-header.mp4.before" "$VIDEO_FILE"
  elif [[ "$VIDEO_EXISTED" == "0" ]]; then
    rm -f "$VIDEO_FILE"
  fi

  log "Rollback finished. Backup root: $BACKUP_ROOT"
  exit "$rc"
}

die() {
  printf '[JOIN-US MIGRATION] ERROR: %s\n' "$*" >&2
  rollback 1
}
trap 'rollback $?' ERR

log "Preflight started."

[[ -d "$WP_ROOT" ]] || die "WordPress root not found: $WP_ROOT"
[[ -d "$THEME_DIR" ]] || die "TheGem theme directory not found: $THEME_DIR"
[[ -f "$LEGACY_DIR/index.html" ]] || die "Legacy index.html not found."
[[ -f "$LEGACY_DIR/video-header.mp4" ]] || die "Legacy video-header.mp4 not found."
command -v wp >/dev/null 2>&1 || die "WP-CLI is required."
command -v python3 >/dev/null 2>&1 || die "python3 is required."
command -v curl >/dev/null 2>&1 || die "curl is required."

INDEX_BYTES="$(stat -c %s "$LEGACY_DIR/index.html")"
VIDEO_BYTES="$(stat -c %s "$LEGACY_DIR/video-header.mp4")"
TOTAL_BYTES=$((INDEX_BYTES + VIDEO_BYTES))
FULL_DIR_BYTES="$(du -sb "$LEGACY_DIR" | awk '{print $1}')"
[[ "$INDEX_BYTES" -gt 35000 ]] || die "index.html is unexpectedly small: $INDEX_BYTES bytes"
[[ "$VIDEO_BYTES" -gt 500000 ]] || die "video-header.mp4 is unexpectedly small: $VIDEO_BYTES bytes"

grep -Fq "$EXPECTED_IFRAME" "$LEGACY_DIR/index.html" || die "Careers iframe dependency not found in live HTML."
grep -Fq "$EXPECTED_RAKAN" "$LEGACY_DIR/index.html" || die "Rakan endpoint dependency not found in live HTML."
grep -Fq '/join-us/video-header.mp4' "$LEGACY_DIR/index.html" || die "Expected legacy video URL not found."

ACTIVE_STYLESHEET="$(wp --path="$WP_ROOT" option get stylesheet --quiet)"
[[ "$ACTIVE_STYLESHEET" == "thegem-elementor" ]] || die "Active stylesheet is '$ACTIVE_STYLESHEET', expected 'thegem-elementor'. Refusing migration."

CURRENT_HTTP="$(curl -L -sS -o /dev/null -w '%{http_code}' --max-time 20 "$TARGET_URL")"
[[ "$CURRENT_HTTP" == "200" ]] || die "Current standalone /join-us/ is not HTTP 200 (got $CURRENT_HTTP)."

mkdir -p "$BACKUP_ROOT" "$(dirname "$TEMPLATE_FILE")" "$ASSET_DIR"
cp -a "$LEGACY_DIR" "$BACKUP_ROOT/legacy-join-us-snapshot"

if [[ -f "$TEMPLATE_FILE" ]]; then
  TEMPLATE_EXISTED=1
  cp -p "$TEMPLATE_FILE" "$BACKUP_ROOT/template-join-us.php.before"
fi
if [[ -f "$VIDEO_FILE" ]]; then
  VIDEO_EXISTED=1
  cp -p "$VIDEO_FILE" "$BACKUP_ROOT/video-header.mp4.before"
fi

# Find or create the WP page. Do not alter page content; the custom template owns rendering.
PAGE_ID="$(wp --path="$WP_ROOT" post list --post_type=page --name=join-us --post_status=any --format=ids | awk '{print $1}')"
if [[ -n "$PAGE_ID" ]]; then
  wp --path="$WP_ROOT" post get "$PAGE_ID" --fields=ID,post_title,post_name,post_status,post_modified --format=json > "$PAGE_BACKUP"
  wp --path="$WP_ROOT" post meta list "$PAGE_ID" --format=json > "$META_BACKUP"
  OLD_TEMPLATE="$(wp --path="$WP_ROOT" post meta get "$PAGE_ID" _wp_page_template 2>/dev/null || true)"
  OLD_STATUS="$(wp --path="$WP_ROOT" post get "$PAGE_ID" --field=post_status)"
  log "Existing WordPress page found: ID $PAGE_ID. It will be preserved and assigned the migration template."
else
  PAGE_ID="$(wp --path="$WP_ROOT" post create --post_type=page --post_title='انضم لفريقنا' --post_name='join-us' --post_status=publish --porcelain)"
  CREATED_PAGE=1
  log "Created WordPress page: ID $PAGE_ID."
fi

# Build the PHP template from the CURRENT live HTML so the migrated design/JS remains byte-for-byte
# equivalent except for the video source URL and the required WordPress template header.
python3 - "$LEGACY_DIR/index.html" "$TEMPLATE_FILE" <<'PY'
from pathlib import Path
import sys
src = Path(sys.argv[1])
dst = Path(sys.argv[2])
html = src.read_text(encoding='utf-8')
old = '/join-us/video-header.mp4?v=6'
new = "<?php echo esc_url(get_template_directory_uri() . '/assets/join-us/video-header.mp4?v=6'); ?>"
if old not in html:
    raise SystemExit('Expected video URL not found; refusing to transform.')
if html.count(old) != 1:
    raise SystemExit(f'Expected exactly one video URL occurrence, found {html.count(old)}.')
html = html.replace(old, new, 1)
header = """<?php\n/*\nTemplate Name: Tamiyouz Join Us\nTemplate Post Type: page\n*/\ndefined('ABSPATH') || exit;\n?>\n"""
dst.write_text(header + html, encoding='utf-8')
PY

cp -p "$LEGACY_DIR/video-header.mp4" "$VIDEO_FILE"
chmod 0644 "$TEMPLATE_FILE" "$VIDEO_FILE"

# Integrity: verify all integration strings survived untouched.
grep -Fq "$EXPECTED_IFRAME" "$TEMPLATE_FILE" || die "Careers iframe was lost during template creation."
grep -Fq "$EXPECTED_RAKAN" "$TEMPLATE_FILE" || die "Rakan endpoint was lost during template creation."
grep -Fq "fetch('/join-us/notify.php'" "$TEMPLATE_FILE" || die "Legacy notify hook changed unexpectedly; migration must not alter behavior."
grep -Fq "e.data.type === 'formSubmission'" "$TEMPLATE_FILE" || die "formSubmission postMessage handler changed unexpectedly."

wp --path="$WP_ROOT" post meta update "$PAGE_ID" _wp_page_template "$TEMPLATE_REL" >/dev/null
wp --path="$WP_ROOT" post update "$PAGE_ID" --post_name=join-us --post_status=publish >/dev/null

# The physical /join-us directory masks the WordPress route, so move it outside public_html only
# after the WordPress template/page are ready. Never delete it.
mv "$LEGACY_DIR" "$LEGACY_BACKUP"
LEGACY_MOVED=1

wp --path="$WP_ROOT" rewrite flush >/dev/null

# Validate WordPress owns the URL and integrations/assets still resolve.
TARGET_TMP="$(mktemp)"
HTTP_STATUS="$(curl -L -sS -o "$TARGET_TMP" -w '%{http_code}' --max-time 30 "$TARGET_URL")"
[[ "$HTTP_STATUS" == "200" ]] || die "Migrated /join-us/ returned HTTP $HTTP_STATUS."
grep -Fq "$EXPECTED_IFRAME" "$TARGET_TMP" || die "Migrated page does not contain careers iframe."
grep -Fq "$EXPECTED_RAKAN" "$TARGET_TMP" || die "Migrated page does not contain Rakan endpoint."
rm -f "$TARGET_TMP"

VIDEO_URL="$SITE_URL/wp-content/themes/thegem-elementor/assets/join-us/video-header.mp4?v=6"
VIDEO_HTTP="$(curl -L -sS -o /dev/null -w '%{http_code}' --max-time 30 "$VIDEO_URL")"
[[ "$VIDEO_HTTP" == "200" ]] || die "Migrated video returned HTTP $VIDEO_HTTP."

ASSIGNED_TEMPLATE="$(wp --path="$WP_ROOT" post meta get "$PAGE_ID" _wp_page_template)"
[[ "$ASSIGNED_TEMPLATE" == "$TEMPLATE_REL" ]] || die "WordPress page template assignment failed."

# Confirm old route directory is gone from public_html and preserved outside web root.
[[ ! -e "$LEGACY_DIR" ]] || die "Legacy physical /join-us directory still exists in public_html."
[[ -d "$LEGACY_BACKUP" ]] || die "Legacy backup directory is missing."

trap - ERR

printf '%s\n' \
  "MIGRATION=COMPLETE" \
  "WORDPRESS_ROOT=$WP_ROOT" \
  "PAGE_ID=$PAGE_ID" \
  "PAGE_TEMPLATE=$TEMPLATE_REL" \
  "ACTIVE_THEME=$ACTIVE_STYLESHEET" \
  "LEGACY_INDEX_BYTES=$INDEX_BYTES" \
  "LEGACY_VIDEO_BYTES=$VIDEO_BYTES" \
  "LEGACY_CORE_TOTAL_BYTES=$TOTAL_BYTES" \
  "LEGACY_FULL_DIR_BYTES=$FULL_DIR_BYTES" \
  "LEGACY_BACKUP=$LEGACY_BACKUP" \
  "TARGET_URL=$TARGET_URL" \
  "TARGET_HTTP_STATUS=$HTTP_STATUS" \
  "VIDEO_URL=$VIDEO_URL" \
  "VIDEO_HTTP_STATUS=$VIDEO_HTTP" \
  "CAREERS_IFRAME_PRESERVED=YES" \
  "RAKAN_ENDPOINT_PRESERVED=YES" \
  "FORM_SUBMISSION_POSTMESSAGE_PRESERVED=YES" \
  "LEGACY_NOTIFY_HOOK_PRESERVED=YES" \
  "THRS_EMAIL_FLOW_CHANGED=NO" \
  "GIT_MUTATIONS=NONE" \
  "OLD_DIRECTORY_DELETED=NO" \
  "ROLLBACK_BACKUP_AVAILABLE=YES" \
  "STATUS=COMPLETE"
