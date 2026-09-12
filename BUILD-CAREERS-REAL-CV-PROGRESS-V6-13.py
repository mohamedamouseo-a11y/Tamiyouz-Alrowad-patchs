#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.12'
TARGET_VERSION='V6.13'
PATCH_ID='CAREERS_REAL_CV_PROGRESS_V6_13'
PATCH_MARKER='TAM_CAREERS_REAL_CV_PROGRESS_V6_13'
REQUIRED_V612='TAM_CAREERS_PRIORITY_DATE_CV_PROGRESS_V6_12'
REQUIRED_V5='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
STABLE_V5_BUNDLE='index-RpV5h8Ns.js'
NEW_CSS='index-VisualV613.css'

CSS=r'''/* TAM_CAREERS_REAL_CV_PROGRESS_V6_13 */
/* Focused visual treatment for the existing REAL V5 XHR CV upload progress. */
#tam-cv-progress{
  margin-top:14px!important;
  padding:14px 15px!important;
  border:1px solid rgba(242,184,39,.30)!important;
  border-radius:14px!important;
  background:linear-gradient(180deg,rgba(13,32,53,.96),rgba(8,22,38,.96))!important;
  box-shadow:0 14px 34px rgba(1,8,18,.24),inset 0 1px 0 rgba(255,255,255,.025)!important;
}
#tam-cv-progress[hidden]{display:none!important}
#tam-cv-progress .tam-cv-progress-head{
  margin-bottom:9px!important;
  color:#eaf0f7!important;
  font-size:12px!important;
  font-weight:800!important;
}
#tam-cv-progress-percent{
  color:#f6c84c!important;
  font-size:12px!important;
  font-weight:900!important;
  font-variant-numeric:tabular-nums!important;
  direction:ltr!important;
}
#tam-cv-progress .tam-cv-progress-track{
  height:10px!important;
  overflow:hidden!important;
  border-radius:999px!important;
  background:#071a2d!important;
  border:1px solid rgba(242,184,39,.14)!important;
}
#tam-cv-progress-bar{
  height:100%!important;
  width:0%;
  border-radius:inherit!important;
  background:linear-gradient(90deg,#bd8106 0%,#f2b827 50%,#ffe07a 100%)!important;
  box-shadow:0 0 20px rgba(242,184,39,.34)!important;
  transition:width .12s linear!important;
}
#tam-cv-progress[data-state="success"]{border-color:rgba(74,222,128,.34)!important}
#tam-cv-progress[data-state="success"] #tam-cv-progress-percent{color:#86efac!important}
#tam-cv-progress[data-state="error"]{border-color:rgba(248,113,113,.42)!important}
#tam-cv-progress[data-state="error"] #tam-cv-progress-percent{color:#fca5a5!important}
@media(prefers-reduced-motion:reduce){#tam-cv-progress-bar{transition:none!important}}
'''

LEGACY_CONTROL_PATTERNS=(
    r'<script[^>]+src=["\'][^"\']*careers-controls-v64\.js[^"\']*["\'][^>]*></script>\s*',
    r'<script[^>]+src=["\'][^"\']*careers-controls-v6[0-9]+\.js[^"\']*["\'][^>]*></script>\s*',
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--stable-v5-bundle',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    ip=Path(a.index); cp=Path(a.css); bp=Path(a.stable_v5_bundle)
    index=ip.read_text(encoding='utf-8')
    css=cp.read_text(encoding='utf-8')
    bundle=bp.read_text(encoding='utf-8')

    if REQUIRED_V612 not in css and REQUIRED_V612 not in index:
        raise SystemExit('V6.12 baseline marker missing')
    if REQUIRED_V5 not in css:
        raise SystemExit('V5 real progress CSS marker missing')
    if bp.name!=STABLE_V5_BUNDLE:
        raise SystemExit('Stable V5 bundle filename mismatch')
    if REQUIRED_V5 not in bundle:
        raise SystemExit('V5 progress bundle marker missing')
    if 'xhr.upload.onprogress' not in bundle or 'e.loaded/e.total' not in bundle:
        raise SystemExit('REAL xhr upload progress code missing from stable V5 bundle')
    if 'FormData' not in bundle:
        raise SystemExit('FormData signature missing from stable V5 bundle')
    if cp.name not in index:
        raise SystemExit('Current CSS reference mismatch')
    if PATCH_MARKER in css or PATCH_MARKER in index:
        raise SystemExit('V6.13 already present')

    # Keep the V6.12 premium date picker asset untouched; remove only legacy V6 custom-control scripts
    # that can interfere with Step 1/Step 2 and are not required for the CV progress path.
    new_index=index
    removed=[]
    for pat in LEGACY_CONTROL_PATTERNS:
        before=new_index
        new_index=re.sub(pat,'',new_index,flags=re.I)
        if new_index!=before:
            removed.append(pat)

    # Force the known stable V5 form bundle that contains REAL xhr.upload.onprogress.
    module_matches=list(re.finditer(r'(<script[^>]+type=["\']module["\'][^>]+src=["\'])([^"\']+)(["\'][^>]*></script>)',new_index,re.I))
    if len(module_matches)!=1:
        raise SystemExit(f'Expected exactly one module script, found {len(module_matches)}')
    m=module_matches[0]
    stable_src=re.sub(r'[^/]+$',STABLE_V5_BUNDLE,m.group(2))
    new_index=new_index[:m.start()]+m.group(1)+stable_src+m.group(3)+new_index[m.end():]

    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=new_index.replace(cp.name,NEW_CSS,1)

    guards={
      'v612_preserved':REQUIRED_V612 in new_css or REQUIRED_V612 in new_index,
      'v5_progress_css_preserved':REQUIRED_V5 in new_css,
      'stable_v5_bundle_selected':STABLE_V5_BUNDLE in new_index,
      'real_xhr_progress_verified':'xhr.upload.onprogress' in bundle and 'e.loaded/e.total' in bundle,
      'formdata_preserved':'FormData' in bundle,
      'progress_dom_contract_preserved':'tam-cv-progress' in bundle,
      'new_css_referenced':NEW_CSS in new_index,
      'old_css_reference_removed':cp.name not in new_index,
      'v612_priority_asset_preserved':'careers-priority-v612.js' in new_index,
      'legacy_v64_removed':'careers-controls-v64.js' not in new_index,
      'css_marker_once':new_css.count(PATCH_MARKER)==1,
      'no_endpoint_change':'fetch(' not in CSS and 'XMLHttpRequest' not in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad:
        raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,
      'base_version':BASE_VERSION,
      'target_version':TARGET_VERSION,
      'patch':PATCH_ID,
      'patch_marker':PATCH_MARKER,
      'strategy':'preserve_v612_date_picker_restore_stable_v5_real_cv_upload_progress_remove_legacy_v64_control_script',
      'stable_v5_bundle':STABLE_V5_BUNDLE,
      'new_css':NEW_CSS,
      'files_changed':['index.html',NEW_CSS],
      'legacy_control_scripts_removed':len(removed),
      'upload_endpoint_changed':False,
      'formdata_changed':False,
      'file_field_changed':False,
      'real_progress_formula':'loaded / total * 100',
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,
      'functional_qa_required':True,
      'git_mutations_by_runner':False,
    }
    if a.manifest:
        Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
