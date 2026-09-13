#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.15'
TARGET_VERSION='V6.16'
PATCH_ID='JOIN_US_PARENT_HEADER_GUARD_V6_16'
PATCH_MARKER='TAM_JOIN_US_PARENT_HEADER_GUARD_V6_16'

OLD="""window.addEventListener('scroll', function() {
      var header = document.getElementById('siteHeader');
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });"""

NEW="""window.addEventListener('scroll', function() {
      var header = document.getElementById('siteHeader');
      if (!header) return; /* TAM_JOIN_US_PARENT_HEADER_GUARD_V6_16 */
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });"""

REQUIRED=(
  'id="careersFrame"',
  "e.data.type === 'formSubmission'",
  "fetch('/join-us/notify.php'",
  'https://careers.tamiyouzplaform.com/api/v1/rakan/chat',
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    srcp=Path(a.source)
    src=srcp.read_text(encoding='utf-8')

    for token in REQUIRED:
        if token not in src:
            raise SystemExit('Protected integration missing: '+token)

    if PATCH_MARKER in src:
        raise SystemExit('V6.16 already present')

    count=src.count(OLD)
    if count!=1:
        raise SystemExit(f'Expected exactly one vulnerable siteHeader scroll block, found {count}')

    out=src.replace(OLD,NEW,1)

    guards={
      'patched_once':out.count(PATCH_MARKER)==1,
      'siteHeader_guard_present':"var header = document.getElementById('siteHeader');\n      if (!header) return;" in out,
      'careers_iframe_preserved':'id="careersFrame"' in out,
      'form_submission_handler_preserved':"e.data.type === 'formSubmission'" in out,
      'notify_hook_preserved':"fetch('/join-us/notify.php'" in out,
      'rakan_api_preserved':'https://careers.tamiyouzplaform.com/api/v1/rakan/chat' in out,
      'source_only_target':True,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad:
        raise SystemExit('Guard failed: '+', '.join(bad))

    Path(a.output).write_text(out,encoding='utf-8')
    manifest={
      'project':PROJECT,
      'base_version':BASE_VERSION,
      'target_version':TARGET_VERSION,
      'patch':PATCH_ID,
      'patch_marker':PATCH_MARKER,
      'strategy':'surgical_null_guard_for_parent_siteHeader_scroll_handler_only',
      'files_changed':['page-join-us.php'],
      'api_changed':False,
      'careers_iframe_changed':False,
      'form_logic_changed':False,
      'notify_hook_changed':False,
      'rakan_backend_changed':False,
      'guards':guards,
      'output_sha256':hashlib.sha256(out.encode()).hexdigest(),
      'git_mutations_by_runner':False,
    }
    if a.manifest:
        Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
