#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID='CAREERS_FORM_CUSTOM_CONTROLS_V6_1'
PATCH_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_1'
BASE_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6'
V5_MARKER='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
OLD_BUNDLE='index-CcV6n2Qs.js'
OLD_CSS='index-CcV6n2Qs.css'
NEW_BUNDLE='index-CcV61p7Ks.js'
NEW_CSS='index-CcV61p7Ks.css'

CSS=r'''/* TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_1 */
/* Hard-disable native popup controls visually while preserving their values/state. */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select.tam-native-hidden,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"].tam-native-hidden{
  display:none!important;
  appearance:none!important;
  -webkit-appearance:none!important;
}

/* Premium trigger */
.tam-control-shell{position:relative!important;width:100%!important;min-width:0!important}
.tam-control-button{
  position:relative!important;
  width:100%!important;
  min-height:54px!important;
  padding:0 16px!important;
  border-radius:14px!important;
  border:1px solid rgba(152,174,201,.24)!important;
  background:linear-gradient(180deg,#1b314b 0%,#162a42 100%)!important;
  color:#f7f9fc!important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.035),0 8px 20px rgba(0,0,0,.08)!important;
  cursor:pointer!important;
  transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease,background .18s ease!important;
}
.tam-control-button:hover{
  border-color:rgba(242,184,39,.62)!important;
  background:linear-gradient(180deg,#1e3857,#182f4a)!important;
}
.tam-control-button[aria-expanded="true"]{
  border-color:#f2b827!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.11),0 14px 30px rgba(0,0,0,.18)!important;
  transform:translateY(-1px)!important;
}
.tam-control-button:after{
  content:"⌄"!important;
  display:grid!important;
  place-items:center!important;
  width:28px!important;
  height:28px!important;
  border-radius:9px!important;
  background:rgba(242,184,39,.09)!important;
  border:1px solid rgba(242,184,39,.18)!important;
  color:#f5c33d!important;
  font-size:17px!important;
  line-height:1!important;
  flex:0 0 28px!important;
}
.tam-control-shell[data-kind="date"] .tam-control-button:after{
  content:"◫"!important;
  font-size:14px!important;
}
.tam-control-button .tam-control-placeholder{color:#93a4ba!important;font-weight:500!important}

/* Floating portal */
#tam-control-portal{
  position:fixed!important;
  z-index:2147483000!important;
  overflow:hidden!important;
  border:1px solid rgba(242,184,39,.38)!important;
  border-radius:18px!important;
  background:linear-gradient(180deg,#122842 0%,#0d2035 100%)!important;
  color:#f8fafc!important;
  box-shadow:0 26px 70px rgba(0,0,0,.50),0 0 0 1px rgba(255,255,255,.02),0 0 34px rgba(242,184,39,.08)!important;
  backdrop-filter:blur(16px)!important;
  -webkit-backdrop-filter:blur(16px)!important;
}
#tam-control-portal:before{
  content:""!important;
  display:block!important;
  height:2px!important;
  background:linear-gradient(90deg,transparent,#f2b827 48%,transparent)!important;
  opacity:.9!important;
}

/* Select */
.tam-select-menu{
  max-height:330px!important;
  overflow:auto!important;
  padding:8px!important;
  scrollbar-width:thin!important;
  scrollbar-color:#c99718 #0f2238!important;
}
.tam-select-menu::-webkit-scrollbar{width:7px!important}
.tam-select-menu::-webkit-scrollbar-track{background:#0f2238!important}
.tam-select-menu::-webkit-scrollbar-thumb{background:#b78716!important;border-radius:999px!important}
.tam-select-option{
  position:relative!important;
  width:100%!important;
  min-height:42px!important;
  padding:10px 13px!important;
  border:1px solid transparent!important;
  border-radius:11px!important;
  background:transparent!important;
  color:#eaf0f7!important;
  font:inherit!important;
  font-size:14px!important;
  font-weight:600!important;
  text-align:right!important;
  cursor:pointer!important;
  transition:background .15s ease,color .15s ease,border-color .15s ease,transform .15s ease!important;
}
.tam-select-option:hover,.tam-select-option:focus-visible{
  outline:none!important;
  background:rgba(242,184,39,.10)!important;
  border-color:rgba(242,184,39,.18)!important;
  color:#ffd65e!important;
  transform:translateX(-2px)!important;
}
.tam-select-option[aria-selected="true"]{
  background:linear-gradient(90deg,rgba(242,184,39,.18),rgba(242,184,39,.08))!important;
  border-color:rgba(242,184,39,.28)!important;
  color:#ffd65e!important;
  font-weight:800!important;
}
.tam-select-option[aria-selected="true"]:after{
  content:"✓"!important;
  color:#f2b827!important;
  font-weight:900!important;
  margin-inline-start:10px!important;
}
.tam-select-option[disabled]{opacity:.38!important;cursor:not-allowed!important;transform:none!important}

/* Date picker */
.tam-date-picker{padding:14px!important;width:min(340px,calc(100vw - 24px))!important}
.tam-date-head{
  display:grid!important;
  grid-template-columns:38px 1fr 38px!important;
  align-items:center!important;
  gap:9px!important;
  margin:2px 0 13px!important;
}
.tam-date-title{
  text-align:center!important;
  color:#ffd45c!important;
  font-size:15px!important;
  font-weight:900!important;
  letter-spacing:.01em!important;
}
.tam-date-nav{
  width:38px!important;
  height:38px!important;
  border:1px solid rgba(242,184,39,.24)!important;
  border-radius:11px!important;
  background:#17304c!important;
  color:#ffd45c!important;
  cursor:pointer!important;
  font-size:20px!important;
  box-shadow:inset 0 1px rgba(255,255,255,.03)!important;
}
.tam-date-nav:hover{border-color:#f2b827!important;background:#1c3959!important}
.tam-date-week,.tam-date-grid{display:grid!important;grid-template-columns:repeat(7,minmax(0,1fr))!important;gap:5px!important}
.tam-date-week{
  margin-bottom:6px!important;
  padding-bottom:6px!important;
  border-bottom:1px solid rgba(255,255,255,.055)!important;
  color:#8fa2b9!important;
  font-size:11px!important;
  text-align:center!important;
  font-weight:800!important;
}
.tam-date-day{
  aspect-ratio:1!important;
  min-width:0!important;
  border:1px solid transparent!important;
  border-radius:10px!important;
  background:transparent!important;
  color:#edf2f8!important;
  cursor:pointer!important;
  font:inherit!important;
  font-size:12px!important;
  transition:background .14s ease,border-color .14s ease,color .14s ease,transform .14s ease!important;
}
.tam-date-day:hover{
  background:rgba(242,184,39,.10)!important;
  border-color:rgba(242,184,39,.18)!important;
  color:#ffd65e!important;
  transform:translateY(-1px)!important;
}
.tam-date-day.is-muted{opacity:.26!important}
.tam-date-day.is-today{border-color:rgba(242,184,39,.55)!important;color:#ffd65e!important}
.tam-date-day.is-selected{
  background:linear-gradient(135deg,#ffd45c,#d89c0e)!important;
  border-color:#ffd45c!important;
  color:#08111c!important;
  font-weight:900!important;
  box-shadow:0 7px 16px rgba(242,184,39,.18)!important;
}
.tam-date-day:disabled{opacity:.15!important;cursor:not-allowed!important;transform:none!important}

@media(max-width:760px){
  #tam-control-portal{max-width:calc(100vw - 20px)!important;border-radius:15px!important}
  .tam-date-picker{width:min(326px,calc(100vw - 20px))!important;padding:11px!important}
}
@media(prefers-reduced-motion:reduce){
  .tam-control-button,.tam-select-option,.tam-date-day{transition:none!important;transform:none!important}
}
'''

JS=r''';/* TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_1 */
(()=>{
  const harden=()=>{
    document.querySelectorAll('form select.tam-native-hidden,form input[type="date"].tam-native-hidden').forEach(el=>{
      el.tabIndex=-1;
      el.setAttribute('aria-hidden','true');
      el.setAttribute('data-tam-native-disabled','1');
    });
    document.querySelectorAll('.tam-control-shell[data-kind="select"] .tam-control-button').forEach((b,i)=>{
      b.setAttribute('data-tam-control','select');
      b.setAttribute('data-tam-control-index',String(i));
    });
    document.querySelectorAll('.tam-control-shell[data-kind="date"] .tam-control-button').forEach((b,i)=>{
      b.setAttribute('data-tam-control','date');
      b.setAttribute('data-tam-control-index',String(i));
    });
  };
  new MutationObserver(harden).observe(document.documentElement,{subtree:true,childList:true,attributes:false});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',harden,{once:true});else harden();
})();
'''

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

    if bp.name!=OLD_BUNDLE or OLD_BUNDLE not in index: raise SystemExit('V6 JS baseline mismatch')
    if cp.name!=OLD_CSS or OLD_CSS not in index: raise SystemExit('V6 CSS baseline mismatch')
    if BASE_MARKER not in bundle or BASE_MARKER not in css: raise SystemExit('V6 marker missing')
    if V5_MARKER not in bundle or V5_MARKER not in css: raise SystemExit('V5 upload progress marker missing')
    if PATCH_MARKER in bundle or PATCH_MARKER in css: raise SystemExit('V6.1 already present')

    new_bundle=bundle.rstrip()+JS+'\n'
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(OLD_BUNDLE,NEW_BUNDLE,1).replace(OLD_CSS,NEW_CSS,1)

    guards={
      'base_v6_preserved':BASE_MARKER in new_bundle and BASE_MARKER in new_css,
      'v5_progress_preserved':V5_MARKER in new_bundle and 'xhr.upload.onprogress' in new_bundle and 'e.loaded/e.total' in new_bundle,
      'v61_js_marker_once':new_bundle.count(PATCH_MARKER)==1,
      'v61_css_marker_once':new_css.count(PATCH_MARKER)==1,
      'native_popup_hard_disabled':'display:none!important' in CSS,
      'select_premium_css':'tam-select-option[aria-selected="true"]' in CSS,
      'date_premium_css':'.tam-date-day.is-selected' in CSS,
      'qa_select_hook':'data-tam-control\',\'select' in JS,
      'qa_date_hook':'data-tam-control\',\'date' in JS,
      'new_js_ref':NEW_BUNDLE in new_index,
      'new_css_ref':NEW_CSS in new_index,
      'old_js_removed':OLD_BUNDLE not in new_index,
      'old_css_removed':OLD_CSS not in new_index,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8')
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':'CAREERS','base_version':'V6','target_version':'V6.1',
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'force_native_controls_hidden_plus_premium_custom_select_calendar_visual_polish',
      'old_bundle':OLD_BUNDLE,'new_bundle':NEW_BUNDLE,
      'old_css':OLD_CSS,'new_css':NEW_CSS,
      'api_changed':False,'form_logic_changed':False,'native_values_preserved':True,
      'real_upload_progress_preserved':True,
      'guards':guards,
      'bundle_sha256':hashlib.sha256(new_bundle.encode()).hexdigest(),
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
