# Tamiyouz Alrowad — Developer Hub V1

WordPress Developer Hub modeled on the TCRM Developer Hub GitHub workflow.

## What V1 adds

- WordPress Admin → **Developer Hub**.
- Access limited to Multisite Super Admin, or the top `manage_options` administrator on single-site WordPress.
- Encrypted GitHub PAT storage using AES-256-GCM and WordPress salts.
- GitHub account verification, repository listing, branch listing and saved selection.
- Local repository status: branch, short SHA, dirty/clean state and project root.
- Mandatory secure preview before every Push / Pull / Full Sync.
- Review fingerprint: execution is rejected if the project changes after review.
- Secret/path blocker for `wp-config.php`, `.env*`, keys/certs, DB dumps, uploads, cache/backups, GitHub tokens, private keys and likely embedded credentials.
- Dedicated Git remote named `tamiyouz-devhub`; existing `origin` is not overwritten.
- Pull uses `--ff-only`; diverged histories are blocked for manual resolution.
- Git initialization is never automatic during patch install. It is an explicit Super Admin action inside the Hub.
- No front-end/theme changes.

## Install

```bash
WP_ROOT=/path/to/wordpress bash APPLY-DEVELOPER-HUB-V1.sh
```

Then open **WP Admin → Developer Hub**.

## Optional repository root override

By default the local Git repository root is `ABSPATH`. To target a different code root, define before WordPress loads the plugin:

```php
define('TAR_DEVHUB_REPO_PATH', '/absolute/path/to/project');
```

## Safety model

The plugin deliberately blocks automatic merges and never force-pushes. If both local and GitHub histories changed, the operation is stopped and must be reconciled manually outside the Hub.
