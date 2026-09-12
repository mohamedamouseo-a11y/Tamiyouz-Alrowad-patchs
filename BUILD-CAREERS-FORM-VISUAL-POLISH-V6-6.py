#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.5'
TARGET_VERSION='V6.6'
PATCH_ID='CAREERS_FORM_VISUAL_POLISH_V6_6'
PATCH_MARKER='TAM_CAREERS_FORM_VISUAL_POLISH_V6_6'
REQUIRED_BASE='TAM_CAREERS_FORM_VISUAL_POLISH_V6_5'
NEW_CSS='index-VisualV66.css'

CSS=r'''/* TAM_CAREERS_FORM_VISUAL_POLISH_V6_6 */
/* CSS-only refinement of existing controls. No behavior/function changes. */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  min-height:58px!important;
  border-radius:16px!important;
  border:1px solid rgba(211,169,52,.28)!important;
  background-color:#1a304b!important;
  color:#f5f8fc!important;
  font-size:14px!important;
  font-weight:650!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.04),0 10px 24px rgba(0,0,0,.10)!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:hover,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]:hover{
  border-color:rgba(242,184,39,.60)!important;
  background-color:#1d3857!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:focus,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]:focus{
  outline:none!important;
  border-color:#f2b827!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.11),0 14px 30px rgba(0,0,0,.16)!important;
}

/* Governorate field: force visible gold chevron in RTL without touching select behavior. */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select{
  appearance:none!important;
  -webkit-appearance:none!important;
  padding-inline-start:16px!important;
  padding-inline-end:54px!important;
  cursor:pointer!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Crect x='1' y='1' width='30' height='30' rx='10' fill='%23F2B827' fill-opacity='.10' stroke='%23F2B827' stroke-opacity='.35'/%3E%3Cpath d='M10.5 13.25 16 18.75l5.5-5.5' fill='none' stroke='%23F2B827' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-size:32px 32px!important;
  background-position:left 14px center!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select option{
  background:#152a43!important;
  color:#f1f5f9!important;
}

/* Date field: keep native click behavior, recolor native icon gold, and polish segment focus. */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  color-scheme:dark!important;
  padding-inline:16px!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-calendar-picker-indicator{
  opacity:1!important;
  cursor:pointer!important;
  filter:invert(78%) sepia(86%) saturate(716%) hue-rotate(347deg) brightness(102%) contrast(94%)!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit-fields-wrapper{
  color:#f5f8fc!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit-month-field:focus,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit-day-field:focus,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit-year-field:focus{
  background:rgba(242,184,39,.16)!important;
  color:#ffd45c!important;
  border-radius:6px!important;
  outline:none!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::selection{
  background:rgba(242,184,39,.22)!important;
  color:#ffd45c!important;
}

@media(max-width:760px){
  .container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
  .container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
    min-height:54px!important;
    border-radius:14px!important;
  }
}
@media(prefers-reduced-motion:reduce){
  .container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
  .container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
    transition:none!important;
    transform:none!important;
  }
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

    if REQUIRED_BASE not in css: raise SystemExit('V6.5 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.6 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v65_preserved':REQUIRED_BASE in new_css,
      'v66_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'select_chevron_rule':'background-position:left 14px center!important' in CSS,
      'date_gold_indicator':'calendar-picker-indicator' in CSS and 'filter:invert' in CSS,
      'date_segment_focus':'datetime-edit-month-field:focus' in CSS,
      'reduced_motion':'prefers-reduced-motion:reduce' in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'css_only_visual_refinement_chevron_calendar_icon_and_date_segment_focus',
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
