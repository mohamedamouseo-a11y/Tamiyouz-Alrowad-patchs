#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.9'
TARGET_VERSION='V6.10'
PATCH_ID='CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_10'
PATCH_MARKER='TAM_CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_10'
REQUIRED_BASE='TAM_CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_9'
NEW_CSS='index-VisualV610.css'

CSS=r'''/* TAM_CAREERS_GOVERNORATE_OPEN_MENU_VISUAL_V6_10 */
/* CSS-only. No behavior/function changes. Correct Chromium customizable-select picker syntax. */

@supports (appearance: base-select) {
  html body form select,
  ::picker(select) {
    appearance: base-select !important;
    -webkit-appearance: base-select !important;
  }

  ::picker(select) {
    margin-top: 10px !important;
    max-height: 340px !important;
    overflow: auto !important;
    padding: 8px !important;
    border: 1px solid rgba(242,184,39,.34) !important;
    border-radius: 18px !important;
    background: linear-gradient(180deg,#142b45 0%,#0d2035 100%) !important;
    color: #eef3f8 !important;
    box-shadow: 0 24px 60px rgba(0,0,0,.48), 0 0 0 1px rgba(255,255,255,.025), 0 0 30px rgba(242,184,39,.07) !important;
    scrollbar-width: thin !important;
    scrollbar-color: #c99520 #0f2238 !important;
  }

  ::picker(select)::-webkit-scrollbar { width: 7px !important; }
  ::picker(select)::-webkit-scrollbar-track { background:#0f2238 !important; border-radius:999px !important; }
  ::picker(select)::-webkit-scrollbar-thumb { background:linear-gradient(#d8a625,#9d7314) !important; border-radius:999px !important; }

  html body form select option {
    min-height: 44px !important;
    padding: 10px 13px !important;
    margin: 2px 0 !important;
    border: 1px solid transparent !important;
    border-radius: 11px !important;
    background: transparent !important;
    color: #edf3f8 !important;
    font-size: 14px !important;
    font-weight: 650 !important;
    line-height: 1.35 !important;
    text-align: right !important;
    cursor: pointer !important;
  }

  html body form select option:hover,
  html body form select option:focus-visible {
    outline: none !important;
    background: linear-gradient(90deg,rgba(242,184,39,.14),rgba(242,184,39,.06)) !important;
    border-color: rgba(242,184,39,.22) !important;
    color: #ffd45c !important;
  }

  html body form select option:checked {
    background: linear-gradient(90deg,rgba(242,184,39,.24),rgba(242,184,39,.10)) !important;
    border-color: rgba(242,184,39,.34) !important;
    color: #ffd45c !important;
    font-weight: 800 !important;
  }

  html body form select option::checkmark {
    color: #f2b827 !important;
    font-weight: 900 !important;
  }

  html body form select::picker-icon {
    color: #f2b827 !important;
  }
}

/* Fallback: retain dark/gold hints only when browser doesn't support customizable select. */
html body form select { color-scheme:dark !important; accent-color:#f2b827 !important; }
html body form select option { background-color:#142941 !important; color:#eef3f8 !important; }
html body form select option:checked { background-color:#263f5b !important; color:#ffd45c !important; }

@media(prefers-reduced-motion:reduce){
  html body form select option { transition:none !important; transform:none !important; }
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

    if REQUIRED_BASE not in css: raise SystemExit('V6.9 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.10 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v69_preserved':REQUIRED_BASE in new_css,
      'v610_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'correct_picker_selector':'::picker(select)' in CSS,
      'base_select_opt_in':'appearance: base-select' in CSS,
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
      'strategy':'css_only_correct_chromium_customizable_select_picker_selector_and_premium_open_menu',
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
