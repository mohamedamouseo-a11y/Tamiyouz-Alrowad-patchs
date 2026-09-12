#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.4'
TARGET_VERSION='V6.5'
PATCH_ID='CAREERS_FORM_VISUAL_POLISH_V6_5'
PATCH_MARKER='TAM_CAREERS_FORM_VISUAL_POLISH_V6_5'
REQUIRED_BASE='TAM_CAREERS_FORM_VISUAL_POLISH_V6_4'
NEW_CSS='index-VisualV65.css'

CSS=r'''/* TAM_CAREERS_FORM_VISUAL_POLISH_V6_5 */
/* Visual-only refinement. No behavior/function changes. */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  min-height:58px!important;
  border-radius:16px!important;
  border:1px solid rgba(215,171,46,.30)!important;
  background:linear-gradient(180deg,#1d3551 0%,#172b43 100%)!important;
  color:#f7f9fc!important;
  font-size:14px!important;
  font-weight:650!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.045),0 10px 26px rgba(0,0,0,.12)!important;
  transition:border-color .18s ease,box-shadow .18s ease,background .18s ease,transform .18s ease!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:hover,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]:hover{
  border-color:rgba(242,184,39,.68)!important;
  background:linear-gradient(180deg,#203b5b,#19314d)!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 14px 30px rgba(0,0,0,.14)!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:focus,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]:focus{
  outline:none!important;
  border-color:#f2b827!important;
  background:linear-gradient(180deg,#213f60,#1a324e)!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.12),0 16px 36px rgba(0,0,0,.18)!important;
  transform:translateY(-1px)!important;
}

/* Governorate/select field */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select{
  appearance:none!important;
  -webkit-appearance:none!important;
  padding-inline-start:16px!important;
  padding-inline-end:52px!important;
  cursor:pointer!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'%3E%3Crect x='1' y='1' width='28' height='28' rx='9' fill='%23f2b827' fill-opacity='.08' stroke='%23f2b827' stroke-opacity='.22'/%3E%3Cpath d='m10 12 5 5 5-5' fill='none' stroke='%23f2b827' stroke-width='2.1' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-size:30px 30px!important;
  background-position:left 14px center!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select option{
  background:#142941!important;
  color:#eef3f8!important;
}

/* Date field: replace black native icon visually with premium gold icon, preserving native click behavior. */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  color-scheme:dark!important;
  padding-inline-start:16px!important;
  padding-inline-end:52px!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'%3E%3Crect x='1' y='1' width='28' height='28' rx='9' fill='%23f2b827' fill-opacity='.08' stroke='%23f2b827' stroke-opacity='.22'/%3E%3Crect x='9' y='10' width='12' height='11' rx='2' fill='none' stroke='%23f2b827' stroke-width='1.8'/%3E%3Cpath d='M11 8v4M19 8v4M9 14h12' stroke='%23f2b827' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-size:30px 30px!important;
  background-position:right 14px center!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-calendar-picker-indicator{
  opacity:0!important;
  cursor:pointer!important;
  width:38px!important;
  height:38px!important;
  margin:0!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-datetime-edit-fields-wrapper{
  color:#f4f7fb!important;
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

    if REQUIRED_BASE not in css: raise SystemExit('V6.4 visual baseline marker missing')
    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.5 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)
    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)

    guards={
      'base_v64_preserved':REQUIRED_BASE in new_css,
      'v65_marker_once':new_css.count(PATCH_MARKER)==1,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'scripts_unchanged':scripts_before==scripts_after,
      'css_only_no_fetch':'fetch(' not in CSS,
      'css_only_no_xhr':'XMLHttpRequest' not in CSS,
      'css_only_no_formdata':'FormData' not in CSS,
      'select_visual_only':'appearance:none!important' in CSS,
      'date_visual_only':'calendar-picker-indicator' in CSS,
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
      'strategy':'css_only_visual_refinement_of_existing_governorate_and_date_fields',
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
