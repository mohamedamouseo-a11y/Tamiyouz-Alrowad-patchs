# Join Us Post-V8 Cleanup V1

Purpose: remove only stale migration leftovers after confirmed V8 success, without touching the working WordPress Join Us implementation.

## Preconditions

Require all of the following before cleanup:

- `https://tamiyouzalrowad.com/join-us/` returns HTTP 200.
- Rendered HTML contains `TAM_JOIN_US_WORDPRESS_FORCE_V1`.
- `/public_html/wp-content/themes/thegem-elementor/functions.php` contains exactly one `BEGIN TAMIYOUZ JOIN US FORCE TEMPLATE V1` block.
- `/public_html/wp-content/themes/thegem-elementor/page-join-us.php` exists.
- `/public_html/wp-content/themes/thegem-elementor/assets/join-us/video-header.mp4` exists and its public URL returns HTTP 200.
- `/public_html/join-us` physical legacy directory is absent.
- The protected V8 legacy backup remains present and HTTP-protected.

If any precondition fails, stop with no changes.

## Stale paths to clean

Only these known stale migration artifacts are eligible:

1. `/public_html/template-join-us.php`
2. `/public_html/wp-content/themes/thegem-elementor/page-templates/template-join-us.php`

Do not delete them permanently. Move any existing stale file to a new protected cleanup backup directory:

`/public_html/.tamiyouz-private-backups/<NEW_CLEANUP_RUN_ID>/stale/`

Use the same deny-all `.htaccess` protection used by the successful migration backup and verify the backup is not publicly readable (HTTP 403 or 404) before moving files.

Preserve original filenames in backup. If both exist and would collide, preserve their source hierarchy under `stale/root/` and `stale/theme-page-templates/`.

If `/public_html/wp-content/themes/thegem-elementor/page-templates/` becomes empty after moving the stale file, it may be removed. Never remove it if any other file remains.

## Forbidden changes

Do not modify or remove:

- `/public_html/wp-content/themes/thegem-elementor/functions.php`
- `/public_html/wp-content/themes/thegem-elementor/page-join-us.php`
- `/public_html/wp-content/themes/thegem-elementor/assets/join-us/video-header.mp4`
- `/public_html/.htaccess`
- WordPress page ID 38574 or its metadata/status
- THRS, careers system, email/SMTP, Rakan
- the protected V8 legacy backup
- any plugin or active theme setting

No Git mutations: no add/commit/push/pull/reset/stash.

## Post-cleanup validation

Require:

- both stale paths above are absent from their original locations (when they existed before cleanup)
- Join Us route still HTTP 200
- rendered HTML still contains `TAM_JOIN_US_WORDPRESS_FORCE_V1`
- homepage HTTP 200
- migrated video HTTP 200
- force filter count remains exactly 1
- page ID 38574 remains publish, slug `join-us`, `_wp_page_template` empty
- protected cleanup backup returns HTTP 403 or 404 for moved files

If any post-cleanup validation fails, move stale files back to their original locations and restore the exact pre-cleanup state.

Return a compact result with: `CLEANUP_RUN_ID`, `STALE_ROOT_TEMPLATE_FOUND`, `STALE_THEME_TEMPLATE_FOUND`, `STALE_ROOT_TEMPLATE_MOVED`, `STALE_THEME_TEMPLATE_MOVED`, `EMPTY_PAGE_TEMPLATES_DIR_REMOVED`, `CLEANUP_BACKUP_PROTECTED`, `ROUTE_SIGNATURE_PRESENT`, `TARGET_HTTP_STATUS`, `VIDEO_HTTP_STATUS`, `HOMEPAGE_HTTP_STATUS`, `FORCE_FILTER_COUNT`, `PAGE_STATUS`, `PAGE_TEMPLATE_META`, `GIT_MUTATIONS`, `ROLLBACK_USED`, `BLOCKERS`, `STATUS`.
