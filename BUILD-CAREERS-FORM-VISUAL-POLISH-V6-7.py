#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.6'
TARGET_VERSION='V6.7'
PATCH_ID='CAREERS_FORM_VISUAL_POLISH_V6_7'
PATCH_MARKER='TAM_CAREERS_FORM_VISUAL_POLISH_V6_7'
REQUIRED_BASE='TAM_CAREERS_FORM_VISUAL_POLISH_V6_6'
NEW_CSS='index-VisualV67.css'

CSS=r'''/* TAM_CAREERS_FORM_VISUAL_POLISH_V6_7 */
/* Final CSS-only visual override for governorate/date fields. No behavior changes. */
html body form select,
html body form input[type="date"]{
  border-radius:16px!important;
  border:1px solid rgba(218,176,55,.30)!important;
  background-color:#1b314c!important;
  color:#f6f8fb!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 10px 24px rgba(0,0,0,.11)!important;
}
html body form select:focus,
html body form input[type="date"]:focus{
  outline:none!important;
  border-color:#f2b827!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.11),0 14px 30px rgba(0,0,0,.16)!important;
}

/* Governorate: force a visible gold chevron using a broadly scoped CSS background. */
html body form select{
  appearance:none!important;
  -webkit-appearance:none!important;
  padding-inline-start:16px!important;
  padding-inline-end:56px!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='34' height='34' viewBox='0 0 34 34'%3E%3Crect x='1' y='1' width='32' height='32' rx='11' fill='%23F2B827' fill-opacity='.11' stroke='%23F2B827' stroke-opacity='.38'/%3E%3Cpath d='M11 14l6 6 6-6' fill='none' stroke='%23F2B827' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-size:34px 34px!important;
  background-position:left 12px center!important;
}
html[dir="rtl"] body form select,
body[dir="rtl"] form select{
  background-position:left 12px center!important;
}
html body form select option{
  background:#152a43!important;
  color:#f1f5f9!important;
}

/* Date: hide the dark native glyph visually and paint a premium gold calendar icon. */
html body form input[type="date"]{
  color-scheme:dark!important;
  padding-inline-start:16px!important;
  padding-inline-end:54px!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Crect x='1' y='1' width='30' height='30' rx='10' fill='%23F2B827' fill-opacity='.10' stroke='%23F2B827' stroke-opacity='.35'/%3E%3Crect x='9' y='10' width='14' height='13' rx='2.5' fill='none' stroke='%23F2B827' stroke-width='1.9'/%3E%3Cpath d='M12 8v4M20 8v4M9 14h14' stroke='%23F2B827' stroke-width='1.9' stroke-linecap='round'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-size:32px 32px!important;
  background-position:right 12px center!important;
}
html[dir="rtl"] body form input[type="date"],
body[dir="rtl"] form input[type="date"]{
  background-position:right 12px center!important;
}
html body form input[type="date"]::-webkit-calendar-picker-indicator{
  opacity:0!important;
  width:40px!important;
  height:40px!important;
  cursor:pointer!important;
  margin:0!important;
}
html body form input[type="date"]::-webkit-datetime-edit,
html body form input[type="date"]::-webkit-datetime-edit-fields-wrapper,
html body form input[type="date"]::-webkit-datetime-edit-text{
  color:#f5f8fc!important;
  background:transparent!important;
}
html body form input[type="date"]:focus::-webkit-datetime-edit-month-field,
html body form input[type="date"]:focus::-webkit-datetime-edit-day-field,
html body form input[type="date"]:focus::-webkit-datetime-edit-year-field,
html body form input[type="date"]::-webkit-datetime-edit-month-field:focus,
html body form input[type="date"]::-webkit-datetime-edit-day-field:focus,
html body form input[type="date"]::-webkit-datetime-edit-year-field:focus{
  background:rgba(242,184,39,.14)!important;
  color:#ffd45c!important;
  -webkit-text-fill-color:#ffd45c!important;
  border-radius:6px!important;
  outline:none!important;
}
html body form input[type="date"]::selection{
  background:rgba(242,184,39,.16)!important;
  color:#ffd45c!important;
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

    if REQUIRED_BASE not in css: raise SystemExit('V6.6 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.7 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v66_preserved':REQUIRED_BASE in new_css,
      'v67_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'forced_select_chevron':'background-image:url("data:image/svg+xml' in CSS and 'form select{' in CSS,
      'date_native_icon_hidden':'calendar-picker-indicator' in CSS and 'opacity:0!important' in CSS,
      'date_focus_override':'datetime-edit-month-field:focus' in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'css_only_broad_visual_override_for_chevron_calendar_icon_and_date_focus',
      'files_changed':['index.html',NEW_CSS],
      'js_changed':False,'function_changed':False,'form_logic_changed':False,'api_changed':False,'backend_changed':False,
      'native_popup_behavior_changed':False,
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
