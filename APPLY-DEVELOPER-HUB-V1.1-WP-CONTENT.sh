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

replacements = [
    (
        " * Version: 1.0.0",
        " * Version: 1.1.0",
    ),
    (
        "const VERSION = '1.0.0';",
        "const VERSION = '1.1.0';",
    ),
    (
        "$root = defined('TAR_DEVHUB_REPO_PATH') && TAR_DEVHUB_REPO_PATH ? TAR_DEVHUB_REPO_PATH : ABSPATH;",
        "$root = defined('TAR_DEVHUB_REPO_PATH') && TAR_DEVHUB_REPO_PATH ? TAR_DEVHUB_REPO_PATH : WP_CONTENT_DIR;",
    ),
    (
        '$rules = "\\n{$marker}\\nwp-config.php\\n.env\\n.env.*\\n*.pem\\n*.key\\n*.p12\\n*.pfx\\n*.sql\\n*.sql.gz\\n*.log\\nwp-content/uploads/\\nwp-content/cache/\\nwp-content/upgrade/\\nwp-content/backups/\\nwp-content/ai1wm-backups/\\nnode_modules/\\nvendor/\\n.DS_Store\\n";',
        '$rules = "\\n{$marker}\\n# wp-content is the repository root. Track only site-specific code.\\n/*\\n!/.gitignore\\n!/themes/\\n/themes/*\\n!/themes/thegem-elementor/\\n!/themes/thegem-elementor/**\\n!/plugins/\\n/plugins/*\\n!/plugins/tamiyouz-developer-hub/\\n!/plugins/tamiyouz-developer-hub/**\\n!/mu-plugins/\\n!/mu-plugins/**\\n/uploads/\\n/cache/\\n/upgrade/\\n/backups/\\n/ai1wm-backups/\\n/wflogs/\\n*.sql\\n*.sql.gz\\n*.log\\n.env\\n.env.*\\n*.pem\\n*.key\\n*.p12\\n*.pfx\\nnode_modules/\\nvendor/\\n.DS_Store\\n";',
    ),
    (
        "'#^wp-content/uploads/#' => 'Media uploads are excluded from source control.',",
        "'#^uploads/#' => 'Media uploads are excluded from source control.',",
    ),
    (
        "'#^wp-content/(?:cache|upgrade|backups|ai1wm-backups)/#' => 'Runtime/cache/backup content is excluded.',",
        "'#^(?:cache|upgrade|backups|ai1wm-backups|wflogs)/#' => 'Runtime/cache/backup content is excluded.',",
    ),
]

for old, new in replacements:
    if old in s:
        s = s.replace(old, new, 1)
    elif new not in s:
        raise SystemExit(f"ERROR: expected patch target not found: {old[:100]}")

p.write_text(s, encoding="utf-8")
PY

php -l "$PLUGIN_FILE"

if grep -Fq ": WP_CONTENT_DIR;" "$PLUGIN_FILE"; then
  ROOT_POLICY="WP_CONTENT_DIR"
else
  echo "ERROR: wp-content root policy not installed" >&2
  exit 4
fi

if grep -Fq "!/themes/thegem-elementor/**" "$PLUGIN_FILE" \
  && grep -Fq "!/plugins/tamiyouz-developer-hub/**" "$PLUGIN_FILE"; then
  ALLOWLIST_POLICY="PASS"
else
  echo "ERROR: allowlist policy not installed" >&2
  exit 5
fi

echo "PLUGIN_VERSION=1.1.0"
echo "DEVHUB_DEFAULT_ROOT=$WP_ROOT/wp-content"
echo "ROOT_POLICY=$ROOT_POLICY"
echo "ALLOWLIST_POLICY=$ALLOWLIST_POLICY"
echo "TRACKED_SCOPE=themes/thegem-elementor,plugins/tamiyouz-developer-hub,mu-plugins"
echo "GIT_INITIALIZED_BY_PATCH=NO"
echo "GIT_OPERATIONS_PERFORMED=NO"
echo "FRONT_END_CHANGED=NO"
echo "STATUS=READY"
