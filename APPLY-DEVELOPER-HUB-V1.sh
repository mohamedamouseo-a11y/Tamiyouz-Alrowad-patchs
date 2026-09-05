#!/usr/bin/env bash
set -euo pipefail

PATCH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WP_ROOT="${WP_ROOT:-$(pwd)}"
PLUGIN_DIR="$WP_ROOT/wp-content/plugins/tamiyouz-developer-hub"

if [[ ! -f "$WP_ROOT/wp-config.php" || ! -d "$WP_ROOT/wp-content" ]]; then
  echo "ERROR: WP_ROOT does not look like a WordPress root: $WP_ROOT" >&2
  exit 2
fi

mkdir -p "$PLUGIN_DIR/assets"
cp "$PATCH_ROOT/tamiyouz-developer-hub/tamiyouz-developer-hub.php" "$PLUGIN_DIR/tamiyouz-developer-hub.php"
cp "$PATCH_ROOT/tamiyouz-developer-hub/assets/admin.js" "$PLUGIN_DIR/assets/admin.js"
cp "$PATCH_ROOT/tamiyouz-developer-hub/assets/admin.css" "$PLUGIN_DIR/assets/admin.css"

# V1 hardening: secure review must fail closed if the remote fetch cannot refresh.
python3 - "$PLUGIN_DIR/tamiyouz-developer-hub.php" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
old = "        ], $token, true, 180);\n    }\n\n    private function current_branch()"
new = "        ], $token, false, 180);\n    }\n\n    private function current_branch()"
if old not in s:
    raise SystemExit("ERROR: strict-fetch hardening target not found; refusing to install an unknown plugin revision")
p.write_text(s.replace(old, new, 1), encoding="utf-8")
PY

php -l "$PLUGIN_DIR/tamiyouz-developer-hub.php"

if command -v node >/dev/null 2>&1; then
  node --check "$PLUGIN_DIR/assets/admin.js" >/dev/null
  JS_CHECK="PASS"
else
  JS_CHECK="SKIPPED_NO_NODE"
fi

if command -v wp >/dev/null 2>&1; then
  (cd "$WP_ROOT" && wp plugin activate tamiyouz-developer-hub --quiet) || true
fi

echo "PLUGIN_PATH=$PLUGIN_DIR"
echo "PHP_LINT=PASS"
echo "JS_CHECK=$JS_CHECK"
echo "STRICT_REMOTE_FETCH=YES"
echo "FRONT_END_CHANGED=NO"
echo "GIT_INITIALIZED_BY_PATCH=NO"
echo "STATUS=READY"
