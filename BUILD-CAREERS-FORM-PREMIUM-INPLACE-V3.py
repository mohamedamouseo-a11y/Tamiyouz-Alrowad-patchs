#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PATCH_ID='CAREERS_FORM_PREMIUM_INPLACE_V3'
PATCH_MARKER='TAM_CAREERS_FORM_PREMIUM_INPLACE_V3'
CURRENT_BUNDLE='index-Bz9Kp2mQ.js'
NEW_BUNDLE='index-DkV3m8Qr.js'
NEW_CSS='index-DkV3m8Qr.css'
OUTER='container mx-auto px-4 pb-24'
HEADING='text-2xl md:text-3xl font-bold mb-2 gold-text text-center'
FORM='space-y-5'
NEXT='flex-[2] gold-gradient text-primary-foreground font-semibold py-3.5 rounded-xl text-base hover:opacity-90 transition-opacity disabled:opacity-50'

CSS=r'''/* TAM_CAREERS_FORM_PREMIUM_INPLACE_V3 */
.tam-premium-root{direction:rtl!important;position:relative!important;max-width:900px!important;margin:0 auto!important;padding:38px 42px 40px!important;border-radius:30px!important;border:1px solid rgba(242,184,39,.30)!important;background:linear-gradient(180deg,rgba(16,31,53,.98),rgba(10,23,40,.99))!important;box-shadow:0 28px 80px rgba(0,0,0,.34),0 0 42px rgba(242,184,39,.08)!important;overflow:hidden!important;animation:tamPremiumV3In .48s cubic-bezier(.2,.75,.2,1) both}
.tam-premium-root:before{content:"";position:absolute;inset:0 0 auto 0;height:2px;background:linear-gradient(90deg,transparent,#f2b827,transparent);opacity:.95;pointer-events:none}
.tam-premium-root:after{content:"";position:absolute;width:240px;height:240px;top:-150px;left:-90px;border-radius:50%;background:radial-gradient(circle,rgba(242,184,39,.11),transparent 68%);pointer-events:none}
.tam-premium-heading{font-size:clamp(28px,3vw,40px)!important;line-height:1.25!important;letter-spacing:-.02em!important;color:#f8fafc!important;margin-bottom:10px!important}
.tam-premium-root p{color:#91a2b8!important}
.tam-premium-root [class*="border-primary/30"]{border-color:rgba(242,184,39,.34)!important;background:rgba(17,34,57,.92)!important;box-shadow:0 6px 22px rgba(0,0,0,.16)!important;transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease!important}
.tam-premium-root [class*="border-primary/30"]:hover{border-color:rgba(242,184,39,.62)!important;box-shadow:0 8px 28px rgba(242,184,39,.10)!important}
.tam-premium-form label{color:#eef3f8!important;font-weight:700!important}
.tam-premium-form input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]),.tam-premium-form select,.tam-premium-form textarea,.tam-premium-form [role="combobox"]{min-height:54px!important;border-radius:13px!important;border:1px solid rgba(124,151,183,.34)!important;background:linear-gradient(180deg,#1a304a,#152941)!important;color:#f8fafc!important;box-shadow:inset 0 1px rgba(255,255,255,.03)!important;transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease,background .2s ease!important}
.tam-premium-form input::placeholder,.tam-premium-form textarea::placeholder{color:#8193aa!important;opacity:1!important}
.tam-premium-form input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]):hover,.tam-premium-form select:hover,.tam-premium-form textarea:hover,.tam-premium-form [role="combobox"]:hover{border-color:rgba(242,184,39,.46)!important}
.tam-premium-form input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]):focus,.tam-premium-form select:focus,.tam-premium-form textarea:focus,.tam-premium-form [role="combobox"]:focus{outline:none!important;border-color:#f2b827!important;background:#192f4a!important;box-shadow:0 0 0 3px rgba(242,184,39,.12),0 10px 26px rgba(0,0,0,.14)!important;transform:translateY(-1px)!important}
.tam-premium-form input[type="radio"]{accent-color:#f2b827!important}
.tam-premium-next{width:100%!important;min-height:56px!important;border-radius:13px!important;background:linear-gradient(100deg,#ffd45c,#f2b827)!important;color:#111923!important;border:1px solid rgba(255,226,123,.95)!important;box-shadow:0 12px 30px rgba(242,184,39,.24),inset 0 1px rgba(255,255,255,.2)!important;font-weight:800!important;transition:transform .2s ease,filter .2s ease,box-shadow .2s ease!important}
.tam-premium-next:hover{transform:translateY(-2px)!important;filter:brightness(1.04)!important;box-shadow:0 16px 36px rgba(242,184,39,.28)!important}
.tam-premium-next:active{transform:translateY(0)!important}
@keyframes tamPremiumV3In{from{opacity:0;transform:translateY(12px) scale(.995)}to{opacity:1;transform:none}}
@media(max-width:760px){.tam-premium-root{max-width:calc(100% - 18px)!important;padding:26px 16px 28px!important;border-radius:22px!important}}
@media(prefers-reduced-motion:reduce){.tam-premium-root,.tam-premium-root *{animation:none!important;transition:none!important}}
'''

def once_replace(s, old, new, label):
    c=s.count(old)
    if c!=1: raise SystemExit(f'{label} expected once, found {c}')
    return s.replace(old,new,1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bundle',required=True)
    ap.add_argument('--index',required=True)
    ap.add_argument('--assets-dir',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()
    bundle_p=Path(a.bundle); index_p=Path(a.index); assets=Path(a.assets_dir); out=Path(a.output_dir)
    bundle=bundle_p.read_text(encoding='utf-8'); index=index_p.read_text(encoding='utf-8')
    if 'CAREERS_FORM_ONLY_PATCHED' not in bundle: raise SystemExit('Missing form-only baseline marker')
    if PATCH_MARKER in bundle or PATCH_MARKER in index: raise SystemExit('V3 already present')
    if CURRENT_BUNDLE not in index: raise SystemExit('Current bundle reference mismatch')
    m=re.search(r'href=["\']([^"\']*/assets/([^/"\']+\.css))["\']',index,re.I)
    if not m: raise SystemExit('CSS asset reference not found in index.html')
    old_css_name=m.group(2); css_p=assets/old_css_name
    if not css_p.exists(): raise SystemExit(f'CSS asset missing: {css_p}')
    css=css_p.read_text(encoding='utf-8')
    if PATCH_MARKER in css: raise SystemExit('V3 CSS already present')
    if bundle.count(OUTER)!=1: raise SystemExit(f'Outer class expected once, found {bundle.count(OUTER)}')
    if bundle.count(HEADING)!=1: raise SystemExit(f'Heading class expected once, found {bundle.count(HEADING)}')
    if bundle.count(FORM)!=1: raise SystemExit(f'Form class expected once, found {bundle.count(FORM)}')
    if bundle.count(NEXT)!=1: raise SystemExit(f'Next class expected once, found {bundle.count(NEXT)}')
    new_bundle=once_replace(bundle,OUTER,OUTER+' tam-premium-root','outer')
    new_bundle=once_replace(new_bundle,HEADING,HEADING+' tam-premium-heading','heading')
    new_bundle=once_replace(new_bundle,FORM,FORM+' tam-premium-form','form')
    new_bundle=once_replace(new_bundle,NEXT,NEXT+' tam-premium-next','next')
    new_css=css.rstrip()+"\n"+CSS+"\n"
    new_index=index.replace(CURRENT_BUNDLE,NEW_BUNDLE,1).replace(old_css_name,NEW_CSS,1)
    guards={
      'form_only_preserved':'CAREERS_FORM_ONLY_PATCHED' in new_bundle,
      'premium_marker_once':new_css.count(PATCH_MARKER)==1,
      'outer_marker_once':new_bundle.count('tam-premium-root')==1,
      'heading_marker_once':new_bundle.count('tam-premium-heading')==1,
      'form_marker_once':new_bundle.count('tam-premium-form')==1,
      'next_marker_once':new_bundle.count('tam-premium-next')==1,
      'no_wrapper_added':new_bundle.count('b.jsx(zO,{})')==bundle.count('b.jsx(zO,{})'),
      'no_root_body_selectors':'#root{' not in CSS and '\nbody{' not in CSS and '\nhtml{' not in CSS,
      'index_new_js':NEW_BUNDLE in new_index,
      'index_new_css':NEW_CSS in new_index,
      'postmessage_count_preserved':new_bundle.count('formSubmission')==bundle.count('formSubmission'),
      'reduced_motion':'prefers-reduced-motion:reduce' in new_css,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))
    out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8')
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')
    manifest={
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'in_place_zO_class_markers_plus_scoped_static_css_asset_no_wrapper_no_runtime_dom',
      'current_bundle':CURRENT_BUNDLE,'new_bundle':NEW_BUNDLE,'old_css':old_css_name,'new_css':NEW_CSS,
      'files_changed':['index.html',NEW_BUNDLE,NEW_CSS],
      'bundle_sha256':hashlib.sha256(new_bundle.encode()).hexdigest(),
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'guards':guards,'form_logic_changed':False,'visual_qa_required':True,'functional_qa_required':True,
      'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
