#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.7'
TARGET_VERSION='V6.8'
PATCH_ID='CAREERS_FORM_OPEN_PICKERS_VISUAL_V6_8'
PATCH_MARKER='TAM_CAREERS_FORM_OPEN_PICKERS_VISUAL_V6_8'
REQUIRED_BASE='TAM_CAREERS_FORM_VISUAL_POLISH_V6_7'
NEW_CSS='index-VisualV68.css'

CSS=r'''/* TAM_CAREERS_FORM_OPEN_PICKERS_VISUAL_V6_8 */
/* CSS-only. No JS/functions/form logic. Focus: OPEN select picker + best-possible native date picker theming. */

/* ---------- Governorate OPEN picker: modern Chromium customizable select ---------- */
@supports (appearance: base-select) {
  html body form select,
  html body form select::picker(select) {
    appearance: base-select!important;
    -webkit-appearance:base-select!important;
  }

  html body form select::picker(select) {
    margin-top:8px!important;
    min-width:100%!important;
    max-height:330px!important;
    overflow:auto!important;
    border:1px solid rgba(242,184,39,.34)!important;
    border-radius:16px!important;
    background:linear-gradient(180deg,#132a44 0%,#0d2035 100%)!important;
    color:#eef3f8!important;
    box-shadow:0 22px 54px rgba(0,0,0,.46),0 0 0 1px rgba(255,255,255,.025),0 0 26px rgba(242,184,39,.07)!important;
    padding:8px!important;
    scrollbar-width:thin!important;
    scrollbar-color:#b98a19 #10243a!important;
  }

  html body form select::picker(select)::-webkit-scrollbar{width:7px!important}
  html body form select::picker(select)::-webkit-scrollbar-track{background:#10243a!important;border-radius:999px!important}
  html body form select::picker(select)::-webkit-scrollbar-thumb{background:#b98a19!important;border-radius:999px!important}

  html body form select option {
    min-height:42px!important;
    padding:10px 13px!important;
    border:1px solid transparent!important;
    border-radius:10px!important;
    background:transparent!important;
    color:#eaf0f7!important;
    font-size:14px!important;
    font-weight:600!important;
    text-align:right!important;
    cursor:pointer!important;
  }

  html body form select option:hover,
  html body form select option:focus-visible {
    outline:none!important;
    background:rgba(242,184,39,.10)!important;
    border-color:rgba(242,184,39,.18)!important;
    color:#ffd45c!important;
  }

  html body form select option:checked {
    background:linear-gradient(90deg,rgba(242,184,39,.18),rgba(242,184,39,.08))!important;
    border-color:rgba(242,184,39,.26)!important;
    color:#ffd45c!important;
    font-weight:800!important;
  }

  html body form select option::checkmark {
    color:#f2b827!important;
  }

  html body form select::picker-icon {
    color:#f2b827!important;
  }
}

/* Fallback for browsers that still expose native option painting. */
html body form select {
  color-scheme:dark!important;
  accent-color:#f2b827!important;
}
html body form select option {
  background-color:#142941!important;
  color:#eef3f8!important;
}
html body form select option:checked {
  background-color:#253d58!important;
  color:#ffd45c!important;
}

/* ---------- Date OPEN popup: browser-native popup cannot be fully authored by page CSS. ---------- */
/* Force the strongest CSS-only dark/gold hints supported by Chromium/OS without changing behavior. */
html {
  color-scheme:dark!important;
}
html body form input[type="date"] {
  color-scheme:dark!important;
  accent-color:#f2b827!important;
}
html body form input[type="date"]::-webkit-calendar-picker-indicator {
  cursor:pointer!important;
  opacity:1!important;
  filter:invert(79%) sepia(85%) saturate(690%) hue-rotate(347deg) brightness(102%) contrast(94%)!important;
}
html body form input[type="date"]::-webkit-datetime-edit,
html body form input[type="date"]::-webkit-datetime-edit-fields-wrapper,
html body form input[type="date"]::-webkit-datetime-edit-text {
  color:#f5f8fc!important;
  background:transparent!important;
}
html body form input[type="date"]::-webkit-datetime-edit-month-field:focus,
html body form input[type="date"]::-webkit-datetime-edit-day-field:focus,
html body form input[type="date"]::-webkit-datetime-edit-year-field:focus {
  background:rgba(242,184,39,.16)!important;
  color:#ffd45c!important;
  -webkit-text-fill-color:#ffd45c!important;
  border-radius:6px!important;
  outline:none!important;
}

@media(prefers-reduced-motion:reduce){
  html body form select,html body form input[type="date"]{transition:none!important;transform:none!important}
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

    if REQUIRED_BASE not in css: raise SystemExit('V6.7 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.8 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v67_preserved':REQUIRED_BASE in new_css,
      'v68_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'customizable_select_picker':'::picker(select)' in CSS and 'appearance: base-select' in CSS,
      'select_open_menu_visual_rules':'option:checked' in CSS and 'scrollbar-color' in CSS,
      'date_css_only_dark_hint':'input[type="date"]' in CSS and 'color-scheme:dark' in CSS,
      'date_gold_indicator':'calendar-picker-indicator' in CSS and 'filter:invert' in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'css_only_customizable_select_open_picker_plus_native_date_dark_gold_hints',
      'files_changed':['index.html',NEW_CSS],
      'js_changed':False,'function_changed':False,'form_logic_changed':False,'api_changed':False,'backend_changed':False,
      'native_behavior_changed':False,
      'date_popup_full_customization_possible_css_only':False,
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
