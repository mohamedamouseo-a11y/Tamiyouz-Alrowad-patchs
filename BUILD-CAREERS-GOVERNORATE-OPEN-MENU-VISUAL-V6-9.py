#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.8'
TARGET_VERSION='V6.9'
PATCH_ID='CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_9'
PATCH_MARKER='TAM_CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_9'
REQUIRED_BASE='TAM_CAREERS_FORM_OPEN_PICKERS_VISUAL_V6_8'
NEW_CSS='index-VisualV69.css'

CSS=r'''/* TAM_CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_9 */
/* CSS-only: premium styling for the OPEN governorate picker itself. No behavior changes. */

@supports selector(select::picker(select)) {
  html body form select,
  html body form select::picker(select){
    appearance:base-select!important;
    -webkit-appearance:base-select!important;
  }

  html body form select::picker(select){
    margin-top:10px!important;
    min-width:100%!important;
    max-height:340px!important;
    overflow:auto!important;
    padding:8px!important;
    border:1px solid rgba(242,184,39,.34)!important;
    border-radius:18px!important;
    background:linear-gradient(180deg,#142b45 0%,#0c2035 100%)!important;
    box-shadow:0 24px 60px rgba(0,0,0,.48),0 0 0 1px rgba(255,255,255,.025),0 0 30px rgba(242,184,39,.07)!important;
    color:#eef3f8!important;
    scrollbar-width:thin!important;
    scrollbar-color:#bd8d1d #102239!important;
  }

  html body form select::picker(select)::-webkit-scrollbar{width:7px!important}
  html body form select::picker(select)::-webkit-scrollbar-track{background:#102239!important;border-radius:999px!important}
  html body form select::picker(select)::-webkit-scrollbar-thumb{background:linear-gradient(#d8a625,#9d7314)!important;border-radius:999px!important}

  html body form select option{
    min-height:44px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:10px!important;
    margin:2px 0!important;
    padding:10px 12px!important;
    border:1px solid transparent!important;
    border-radius:11px!important;
    background:transparent!important;
    color:#eef3f8!important;
    font-size:14px!important;
    font-weight:650!important;
    line-height:1.35!important;
    text-align:right!important;
    cursor:pointer!important;
    transition:background .14s ease,border-color .14s ease,color .14s ease,transform .14s ease!important;
  }

  html body form select option:hover,
  html body form select option:focus-visible{
    outline:none!important;
    background:linear-gradient(90deg,rgba(242,184,39,.13),rgba(242,184,39,.06))!important;
    border-color:rgba(242,184,39,.22)!important;
    color:#ffd45c!important;
    transform:translateX(-1px)!important;
  }

  html body form select option:checked{
    background:linear-gradient(90deg,rgba(242,184,39,.22),rgba(242,184,39,.09))!important;
    border-color:rgba(242,184,39,.32)!important;
    color:#ffd45c!important;
    font-weight:800!important;
  }

  html body form select option::checkmark{
    color:#f2b827!important;
    font-weight:900!important;
  }

  html body form select::picker-icon{
    color:#f2b827!important;
  }
}

/* Fallback keeps only dark/gold hints when customizable select is unavailable. */
html body form select{color-scheme:dark!important;accent-color:#f2b827!important}
html body form select option{background-color:#142941!important;color:#eef3f8!important}
html body form select option:checked{background-color:#263f5b!important;color:#ffd45c!important}

@media(prefers-reduced-motion:reduce){
  html body form select option{transition:none!important;transform:none!important}
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

    if REQUIRED_BASE not in css: raise SystemExit('V6.8 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.9 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v68_preserved':REQUIRED_BASE in new_css,
      'v69_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'picker_visual_rules':'select::picker(select)' in CSS,
      'option_hover_rules':'option:hover' in CSS,
      'option_selected_rules':'option:checked' in CSS,
      'scrollbar_rules':'scrollbar-color' in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'css_only_premium_open_governorate_picker_visual_polish',
      'files_changed':['index.html',NEW_CSS],
      'js_changed':False,'function_changed':False,'form_logic_changed':False,'api_changed':False,'backend_changed':False,
      'native_behavior_changed':False,
      'date_popup_changed':False,
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
