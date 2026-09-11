#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PATCH_ID='CAREERS_FORM_PREMIUM_CSS_V4'
PATCH_MARKER='TAM_CAREERS_FORM_PREMIUM_CSS_V4'
CURRENT_BUNDLE='index-Bz9Kp2mQ.js'
NEW_CSS='index-LxV4p9Nz.css'

CSS=r'''/* TAM_CAREERS_FORM_PREMIUM_CSS_V4 */
.container.mx-auto.px-4.pb-24{max-width:980px!important;padding-left:16px!important;padding-right:16px!important;padding-bottom:56px!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto{max-width:860px!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass{position:relative!important;overflow:hidden!important;border-radius:30px!important;padding:42px 44px 38px!important;border:1px solid rgba(242,184,39,.30)!important;background:linear-gradient(180deg,rgba(16,31,53,.98),rgba(10,23,40,.99))!important;box-shadow:0 28px 80px rgba(0,0,0,.34),0 0 42px rgba(242,184,39,.09)!important;animation:tamCareersV4In .48s cubic-bezier(.2,.75,.2,1) both}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass:before{content:"";position:absolute;inset:0 0 auto;height:2px;background:linear-gradient(90deg,transparent,#f2b827,transparent);opacity:.95;pointer-events:none}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass:after{content:"";position:absolute;width:240px;height:240px;top:-150px;left:-90px;border-radius:50%;background:radial-gradient(circle,rgba(242,184,39,.11),transparent 68%);pointer-events:none}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass h1,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass h2{font-size:clamp(28px,3vw,40px)!important;line-height:1.25!important;letter-spacing:-.02em!important;color:#f8fafc!important;text-align:center!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass p{color:#91a2b8!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass [class*="border-primary/30"]{border-color:rgba(242,184,39,.34)!important;background:rgba(17,34,57,.92)!important;box-shadow:0 6px 22px rgba(0,0,0,.16)!important;transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass [class*="border-primary/30"]:hover{border-color:rgba(242,184,39,.62)!important;box-shadow:0 8px 28px rgba(242,184,39,.10)!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form label{color:#eef3f8!important;font-weight:700!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]),.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form textarea,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form [role="combobox"]{min-height:54px!important;border-radius:13px!important;border:1px solid rgba(124,151,183,.34)!important;background:linear-gradient(180deg,#1a304a,#152941)!important;color:#f8fafc!important;box-shadow:inset 0 1px rgba(255,255,255,.03)!important;transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease,background .2s ease!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input::placeholder,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form textarea::placeholder{color:#8193aa!important;opacity:1!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]):focus,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select:focus,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form textarea:focus,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form [role="combobox"]:focus{outline:none!important;border-color:#f2b827!important;background:#192f4a!important;box-shadow:0 0 0 3px rgba(242,184,39,.12),0 10px 26px rgba(0,0,0,.14)!important;transform:translateY(-1px)!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="radio"]{accent-color:#f2b827!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form button:last-of-type{min-height:56px!important;border-radius:13px!important;background:linear-gradient(100deg,#ffd45c,#f2b827)!important;color:#111923!important;border:1px solid rgba(255,226,123,.95)!important;box-shadow:0 12px 30px rgba(242,184,39,.24),inset 0 1px rgba(255,255,255,.2)!important;font-weight:800!important;transition:transform .2s ease,filter .2s ease,box-shadow .2s ease!important}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form button:last-of-type:hover{transform:translateY(-2px)!important;filter:brightness(1.04)!important;box-shadow:0 16px 36px rgba(242,184,39,.28)!important}
@keyframes tamCareersV4In{from{opacity:0;transform:translateY(12px) scale(.995)}to{opacity:1;transform:none}}
@media(max-width:760px){.container.mx-auto.px-4.pb-24{padding-left:9px!important;padding-right:9px!important}.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass{padding:26px 16px 28px!important;border-radius:22px!important}}
@media(prefers-reduced-motion:reduce){.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass *{animation:none!important;transition:none!important}}
'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--assets-dir',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()
    index_p=Path(a.index); assets=Path(a.assets_dir); out=Path(a.output_dir)
    index=index_p.read_text(encoding='utf-8')
    if CURRENT_BUNDLE not in index: raise SystemExit('Current bundle reference mismatch')
    if PATCH_MARKER in index: raise SystemExit('V4 already present in index')
    m=re.search(r'href=["\']([^"\']*/assets/([^/"\']+\.css))["\']',index,re.I)
    if not m: raise SystemExit('CSS asset reference not found')
    old_css_name=m.group(2); old_css_p=assets/old_css_name
    if not old_css_p.exists(): raise SystemExit(f'CSS asset missing: {old_css_p}')
    old_css=old_css_p.read_text(encoding='utf-8')
    if PATCH_MARKER in old_css: raise SystemExit('V4 already present in CSS')
    new_css=old_css.rstrip()+"\n"+CSS+"\n"
    new_index=index.replace(old_css_name,NEW_CSS,1)
    guards={
      'bundle_unchanged':CURRENT_BUNDLE in new_index,
      'new_css_referenced':NEW_CSS in new_index,
      'marker_once':new_css.count(PATCH_MARKER)==1,
      'no_js_change':'.js' in index and index.count(CURRENT_BUNDLE)==new_index.count(CURRENT_BUNDLE),
      'no_root_selector':'#root' not in CSS,
      'no_body_selector':'body{' not in CSS,
      'no_html_selector':'html{' not in CSS,
      'card_selector_present':'.max-w-2xl.mx-auto>.glass' in CSS,
      'reduced_motion':'prefers-reduced-motion:reduce' in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))
    out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')
    manifest={
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'existing_live_dom_selectors_plus_new_static_css_asset_only_no_js_no_root_body',
      'current_bundle':CURRENT_BUNDLE,'old_css':old_css_name,'new_css':NEW_CSS,
      'files_changed':['index.html',NEW_CSS],
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'guards':guards,'form_logic_changed':False,'js_changed':False,
      'visual_qa_required':True,'functional_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
