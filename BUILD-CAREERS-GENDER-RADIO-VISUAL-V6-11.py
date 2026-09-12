#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.10'
TARGET_VERSION='V6.11'
PATCH_ID='CAREERS_GENDER_RADIO_VISUAL_V6_11'
PATCH_MARKER='TAM_CAREERS_GENDER_RADIO_VISUAL_V6_11'
REQUIRED_BASE='TAM_CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_10'
NEW_CSS='index-VisualV611.css'

CSS=r'''/* TAM_CAREERS_GENDER_RADIO_VISUAL_V6_11 */
/* CSS-only visual polish for gender radio controls. No behavior/function changes. */
html body form input[type="radio"]{
  appearance:none!important;
  -webkit-appearance:none!important;
  width:18px!important;
  height:18px!important;
  min-width:18px!important;
  border-radius:50%!important;
  border:1px solid rgba(242,184,39,.42)!important;
  background:#152a43!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 0 0 1px rgba(255,255,255,.015)!important;
  cursor:pointer!important;
  vertical-align:middle!important;
  transition:border-color .16s ease,box-shadow .16s ease,background .16s ease,transform .16s ease!important;
}

html body form input[type="radio"]:hover{
  border-color:rgba(242,184,39,.78)!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.08)!important;
}

html body form input[type="radio"]:focus-visible{
  outline:none!important;
  border-color:#f2b827!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.14)!important;
}

html body form input[type="radio"]:checked{
  border-color:#f2b827!important;
  background:radial-gradient(circle at center,#f2b827 0 4px,#152a43 4.5px 100%)!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.08),inset 0 1px 0 rgba(255,255,255,.05)!important;
}

html body form input[type="radio"]:checked:hover{
  box-shadow:0 0 0 4px rgba(242,184,39,.10),inset 0 1px 0 rgba(255,255,255,.05)!important;
}

@media(prefers-reduced-motion:reduce){
  html body form input[type="radio"]{transition:none!important;transform:none!important}
}
'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    index=Path(a.index).read_text(encoding='utf-8')
    cp=Path(a.css)
    css=cp.read_text(encoding='utf-8')

    if REQUIRED_BASE not in css: raise SystemExit('V6.10 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.11 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v610_preserved':REQUIRED_BASE in new_css,
      'v611_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'radio_visual_only':'input[type="radio"]' in CSS,
      'checked_state':'input[type="radio"]:checked' in CSS,
      'focus_state':'input[type="radio"]:focus-visible' in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'css_only_gender_radio_visual_polish',
      'files_changed':['index.html',NEW_CSS],
      'js_changed':False,'function_changed':False,'form_logic_changed':False,'api_changed':False,'backend_changed':False,
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
