#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID='CAREERS_FORM_RUNTIME_FIX_V6_2'
PATCH_MARKER='TAM_CAREERS_FORM_RUNTIME_FIX_V6_2'
BASE_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_1'
V6_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6'
V5_MARKER='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
OLD_BUNDLE='index-CcV61p7Ks.js'
OLD_CSS='index-CcV61p7Ks.css'
NEW_BUNDLE='index-CcV62q4Ms.js'

OLD_MAKESHELL="el.classList.add('tam-native-hidden')"
NEW_MAKESHELL="el.setAttribute('class',((el.getAttribute('class')||'')+' tam-native-hidden').trim())"

OLD_DATE_CLASSES="if(today.toDateString()===d.toDateString())b.classList.add('is-today');if(selected&&selected.toDateString()===d.toDateString())b.classList.add('is-selected');"
NEW_DATE_CLASSES="if(today.toDateString()===d.toDateString())b.className+=' is-today';if(selected&&selected.toDateString()===d.toDateString())b.className+=' is-selected';"

OLD_ENHANCE="const enhance=()=>{document.querySelectorAll('form select').forEach(enhanceSelect);document.querySelectorAll('form input[type=\"date\"]').forEach(enhanceDate)};"
NEW_ENHANCE="const enhance=()=>{document.querySelectorAll('form select').forEach(el=>{try{enhanceSelect(el)}catch(e){console.error('[TAM V6.2 select enhance]',e)}});document.querySelectorAll('form input[type=\"date\"]').forEach(el=>{try{enhanceDate(el)}catch(e){console.error('[TAM V6.2 date enhance]',e)}})};"

TAIL=""";/* TAM_CAREERS_FORM_RUNTIME_FIX_V6_2 */
(()=>{
  const verify=()=>{
    const form=document.querySelector('form');
    if(!form)return;
    const selects=[...form.querySelectorAll('select')];
    const dates=[...form.querySelectorAll('input[type=\"date\"]')];
    const customSelects=document.querySelectorAll('.tam-control-shell[data-kind=\"select\"] .tam-control-button').length;
    const customDates=document.querySelectorAll('.tam-control-shell[data-kind=\"date\"] .tam-control-button').length;
    document.documentElement.dataset.tamV62Selects=String(customSelects);
    document.documentElement.dataset.tamV62Dates=String(customDates);
    document.documentElement.dataset.tamV62NativeSelects=String(selects.length);
    document.documentElement.dataset.tamV62NativeDates=String(dates.length);
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(verify,0),{once:true});
  else setTimeout(verify,0);
  setTimeout(verify,1000);
})();
"""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--bundle',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    index=Path(a.index).read_text(encoding='utf-8')
    bp=Path(a.bundle); cp=Path(a.css)
    bundle=bp.read_text(encoding='utf-8'); css=cp.read_text(encoding='utf-8')

    if bp.name!=OLD_BUNDLE or OLD_BUNDLE not in index: raise SystemExit('V6.1 JS baseline mismatch')
    if cp.name!=OLD_CSS or OLD_CSS not in index: raise SystemExit('V6.1 CSS baseline mismatch')
    for marker in (BASE_MARKER,V6_MARKER,V5_MARKER):
        if marker not in bundle: raise SystemExit(f'Missing baseline marker in JS: {marker}')
    if BASE_MARKER not in css or V6_MARKER not in css or V5_MARKER not in css: raise SystemExit('Required CSS baseline markers missing')
    if PATCH_MARKER in bundle: raise SystemExit('V6.2 already present')

    if bundle.count(OLD_MAKESHELL)!=1: raise SystemExit(f'Expected exactly one makeShell classList.add, found {bundle.count(OLD_MAKESHELL)}')
    if bundle.count(OLD_DATE_CLASSES)!=1: raise SystemExit(f'Expected exactly one date classList sequence, found {bundle.count(OLD_DATE_CLASSES)}')
    if bundle.count(OLD_ENHANCE)!=1: raise SystemExit(f'Expected exactly one V6 enhance function, found {bundle.count(OLD_ENHANCE)}')

    new_bundle=bundle.replace(OLD_MAKESHELL,NEW_MAKESHELL,1)
    new_bundle=new_bundle.replace(OLD_DATE_CLASSES,NEW_DATE_CLASSES,1)
    new_bundle=new_bundle.replace(OLD_ENHANCE,NEW_ENHANCE,1)
    new_bundle=new_bundle.rstrip()+TAIL+'\n'
    new_index=index.replace(OLD_BUNDLE,NEW_BUNDLE,1)

    guards={
      'base_v61_preserved':BASE_MARKER in new_bundle,
      'v6_preserved':V6_MARKER in new_bundle,
      'v5_progress_preserved':V5_MARKER in new_bundle and 'xhr.upload.onprogress' in new_bundle and 'e.loaded/e.total' in new_bundle,
      'problematic_makeShell_add_removed':OLD_MAKESHELL not in new_bundle,
      'date_classList_add_removed':OLD_DATE_CLASSES not in new_bundle,
      'safe_class_assignment_present':NEW_MAKESHELL in new_bundle,
      'enhance_try_catch_present':"[TAM V6.2 select enhance]" in new_bundle and "[TAM V6.2 date enhance]" in new_bundle,
      'diagnostic_marker_once':new_bundle.count(PATCH_MARKER)==1,
      'new_bundle_ref':NEW_BUNDLE in new_index,
      'old_bundle_ref_removed':OLD_BUNDLE not in new_index,
      'css_unchanged':OLD_CSS in new_index,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':'CAREERS','base_version':'V6.1','target_version':'V6.2',
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'remove_failing_classList_add_paths_and_isolate_custom_control_enhancement_errors',
      'old_bundle':OLD_BUNDLE,'new_bundle':NEW_BUNDLE,'css':OLD_CSS,
      'files_changed':['index.html',NEW_BUNDLE],
      'css_changed':False,'api_changed':False,'form_logic_changed':False,
      'real_upload_progress_preserved':True,
      'guards':guards,
      'bundle_sha256':hashlib.sha256(new_bundle.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
