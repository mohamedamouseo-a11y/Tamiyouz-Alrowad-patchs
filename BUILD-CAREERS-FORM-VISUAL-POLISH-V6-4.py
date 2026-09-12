#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.3'
TARGET_VERSION='V6.4'
PATCH_ID='CAREERS_FORM_VISUAL_POLISH_V6_4'
PATCH_MARKER='TAM_CAREERS_FORM_VISUAL_POLISH_V6_4'
NEW_CSS='index-VisualV64.css'

CSS=r'''/* TAM_CAREERS_FORM_VISUAL_POLISH_V6_4 */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  min-height:56px!important;
  border-radius:15px!important;
  border:1px solid rgba(242,184,39,.24)!important;
  background-color:#182f49!important;
  color:#f7f9fc!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 10px 24px rgba(0,0,0,.10)!important;
  transition:border-color .18s ease,box-shadow .18s ease,background .18s ease,transform .18s ease!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:hover,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]:hover{
  border-color:rgba(242,184,39,.58)!important;
  background-color:#1b3552!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:focus,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]:focus{
  outline:none!important;
  border-color:#f2b827!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.11),0 14px 30px rgba(0,0,0,.16)!important;
  transform:translateY(-1px)!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select{
  appearance:none!important;
  -webkit-appearance:none!important;
  padding-inline-start:16px!important;
  padding-inline-end:46px!important;
  cursor:pointer!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%23f2b827' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-size:18px 18px!important;
  background-position:left 15px center!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select option{
  background:#142941!important;
  color:#eef3f8!important;
  padding:10px!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  color-scheme:dark!important;
  padding-inline:16px!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-calendar-picker-indicator{
  cursor:pointer!important;
  opacity:.95!important;
  filter:invert(78%) sepia(91%) saturate(661%) hue-rotate(347deg) brightness(101%) contrast(91%)!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form label:has(+ select),
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form label:has(+ input[type="date"]){
  letter-spacing:.01em!important;
}
@media(prefers-reduced-motion:reduce){
  .container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
  .container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{transition:none!important;transform:none!important}
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

    if PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V6.4 already present')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')
    if 'form select' not in css or 'input[type="date"]' not in css: raise SystemExit('Expected form control CSS baseline not found')

    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(cp.name,NEW_CSS,1)

    guards={
      'visual_only_css_append':PATCH_MARKER in new_css,
      'new_css_ref':NEW_CSS in new_index,
      'old_css_ref_removed':cp.name not in new_index,
      'no_js_reference_changes':re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)==re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I),
      'no_form_logic':'fetch(' not in CSS and 'XMLHttpRequest' not in CSS and 'FormData' not in CSS,
      'select_visual_rules':'appearance:none!important' in CSS,
      'date_visual_rules':'color-scheme:dark!important' in CSS,
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
      'strategy':'css_only_visual_polish_existing_select_and_date_fields',
      'files_changed':['index.html',NEW_CSS],
      'js_changed':False,'form_logic_changed':False,'api_changed':False,'backend_changed':False,
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
