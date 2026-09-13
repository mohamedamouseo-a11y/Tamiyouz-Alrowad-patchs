#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.13'
TARGET_VERSION='V6.15'
PATCH_ID='CAREERS_SUBMIT_C_ADD_GUARD_V6_15'
PATCH_MARKER='TAM_CAREERS_SUBMIT_C_ADD_GUARD_V6_15'
CURRENT_BUNDLE='index-RpV5h8Ns.js'
NEW_BUNDLE='index-RpV615c4.js'
REQUIRED_V5='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
REQUIRED_V613='TAM_CAREERS_REAL_CV_PROGRESS_V6_13'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--bundle',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    ip=Path(a.index); bp=Path(a.bundle); cp=Path(a.css)
    index=ip.read_text(encoding='utf-8')
    bundle=bp.read_text(encoding='utf-8')
    css=cp.read_text(encoding='utf-8')

    if bp.name!=CURRENT_BUNDLE:
        raise SystemExit('Expected live V6.13 stable bundle '+CURRENT_BUNDLE)
    if CURRENT_BUNDLE not in index:
        raise SystemExit('Current stable V5/V6.13 bundle reference missing from index')
    if REQUIRED_V5 not in bundle:
        raise SystemExit('V5 real progress marker missing from bundle')
    if 'xhr.upload.onprogress' not in bundle or 'e.loaded/e.total' not in bundle:
        raise SystemExit('Real XHR upload progress code missing')
    if 'FormData' not in bundle:
        raise SystemExit('FormData signature missing')
    if REQUIRED_V613 not in css:
        raise SystemExit('V6.13 CSS baseline marker missing')
    if cp.name not in index:
        raise SystemExit('Current V6.13 CSS reference missing')
    if PATCH_MARKER in bundle or PATCH_MARKER in index:
        raise SystemExit('V6.15 already present')

    # OpenHands inspection identified the crashing minified receiver as c.add(...),
    # not .classList.add(...). Guard only this exact minified call shape.
    c_add_count=len(re.findall(r'(?<![\w$])c\.add\(',bundle))
    if c_add_count < 1:
        raise SystemExit('Expected minified c.add( pattern not found')
    if c_add_count > 20:
        raise SystemExit(f'Refusing broad patch: found {c_add_count} c.add occurrences')

    # Optional chaining is behavior-preserving whenever c/add exist, and only
    # prevents the known undefined.add crash when the receiver is missing.
    new_bundle=re.sub(r'(?<![\w$])c\.add\(', 'c?.add?.(', bundle)
    new_bundle=new_bundle.rstrip()+f'\n/* {PATCH_MARKER} guarded_c_add_count={c_add_count} */\n'
    new_index=index.replace(CURRENT_BUNDLE,NEW_BUNDLE,1)

    guards={
      'v5_marker_preserved':REQUIRED_V5 in new_bundle,
      'real_xhr_progress_preserved':'xhr.upload.onprogress' in new_bundle and 'e.loaded/e.total' in new_bundle,
      'formdata_preserved':'FormData' in new_bundle,
      'fetch_call_count_preserved':new_bundle.count('fetch(')==bundle.count('fetch('),
      'xhr_constructor_count_preserved':new_bundle.count('new XMLHttpRequest')==bundle.count('new XMLHttpRequest'),
      'original_c_add_removed':len(re.findall(r'(?<![\w$])c\.add\(',new_bundle))==0,
      'guarded_c_add_count':new_bundle.count('c?.add?.(')==c_add_count,
      'new_bundle_referenced':NEW_BUNDLE in new_index,
      'old_bundle_reference_removed':CURRENT_BUNDLE not in new_index,
      'v613_css_reference_preserved':cp.name in new_index,
      'v612_date_asset_preserved':'careers-priority-v612.js' in new_index,
      'patch_marker_once':new_bundle.count(PATCH_MARKER)==1,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad:
        raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,
      'base_version':BASE_VERSION,
      'target_version':TARGET_VERSION,
      'patch':PATCH_ID,
      'patch_marker':PATCH_MARKER,
      'strategy':'surgical_optional_chain_guard_for_exact_minified_c_add_crash_while_preserving_v5_real_xhr_progress',
      'old_bundle':CURRENT_BUNDLE,
      'new_bundle':NEW_BUNDLE,
      'c_add_occurrences_guarded':c_add_count,
      'css_changed':False,
      'api_changed':False,
      'upload_endpoint_changed':False,
      'formdata_changed':False,
      'file_field_changed':False,
      'real_progress_formula':'loaded / total * 100',
      'guards':guards,
      'bundle_sha256':hashlib.sha256(new_bundle.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'functional_qa_required':True,
      'visual_qa_required':True,
      'git_mutations_by_runner':False,
    }
    if a.manifest:
        Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
