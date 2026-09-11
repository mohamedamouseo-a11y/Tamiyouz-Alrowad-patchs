#!/usr/bin/env python3
import argparse, hashlib, json, os
from pathlib import Path

PATCH_ID='CAREERS_FORM_PREMIUM_BUNDLE_V2'
PATCH_MARKER='TAM_CAREERS_FORM_PREMIUM_BUNDLE_V2'
CURRENT_BUNDLE='index-Bz9Kp2mQ.js'
NEW_BUNDLE='index-CpV2a7Qx.js'
TARGET_CALL='b.jsx(zO,{})'

CSS='''/* TAM_CAREERS_FORM_PREMIUM_BUNDLE_V2 */
.tam-premium-card{direction:rtl;width:min(900px,calc(100vw - 32px));margin:0 auto;padding:1px;border-radius:30px;background:linear-gradient(135deg,rgba(255,212,92,.95),rgba(255,255,255,.18) 20%,rgba(47,71,101,.4) 58%,rgba(242,184,39,.9));box-shadow:0 30px 80px rgba(0,0,0,.36),0 0 48px rgba(242,184,39,.10);animation:tamPremiumIn .5s cubic-bezier(.2,.75,.2,1) both}
.tam-premium-card>*{border-radius:29px!important;background:linear-gradient(180deg,#101f35 0%,#0b182a 100%)!important;padding:42px 44px 36px!important;box-sizing:border-box!important;overflow:hidden!important}
.tam-premium-card h1,.tam-premium-card h2,.tam-premium-card h3{color:#f8fafc!important;letter-spacing:-.02em!important}.tam-premium-card h1,.tam-premium-card h2{text-align:center!important}
.tam-premium-card p{color:#93a3b8!important}
.tam-premium-card form{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:20px 18px!important;width:100%!important}
.tam-premium-card form>*{min-width:0!important}.tam-premium-card form>*:has(input[name*=name]),.tam-premium-card form>*:has(input[name*=address]){grid-column:1/-1!important}
.tam-premium-card label{color:#eef3f8!important;font-weight:700!important;margin-bottom:8px!important}
.tam-premium-card input,.tam-premium-card select,.tam-premium-card textarea{width:100%!important;min-height:54px!important;border-radius:13px!important;border:1px solid rgba(124,151,183,.34)!important;background:linear-gradient(180deg,#1b304b,#162941)!important;color:#f8fafc!important;box-shadow:inset 0 1px rgba(255,255,255,.03)!important;transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease,background .2s ease!important}
.tam-premium-card input::placeholder,.tam-premium-card textarea::placeholder{color:#8294aa!important;opacity:1!important}
.tam-premium-card input:hover,.tam-premium-card select:hover,.tam-premium-card textarea:hover{border-color:rgba(242,184,39,.48)!important}
.tam-premium-card input:focus,.tam-premium-card select:focus,.tam-premium-card textarea:focus{outline:none!important;border-color:#f2b827!important;background:#192f4a!important;box-shadow:0 0 0 3px rgba(242,184,39,.13),0 10px 26px rgba(0,0,0,.14)!important;transform:translateY(-1px)!important}
.tam-premium-card input[type=radio]{width:18px!important;height:18px!important;min-height:18px!important;accent-color:#f2b827!important}
.tam-premium-card button{min-height:56px!important;border-radius:13px!important;font-weight:800!important;transition:transform .2s ease,filter .2s ease,box-shadow .2s ease!important}.tam-premium-card button:hover{transform:translateY(-2px)!important;filter:brightness(1.05)!important}
.tam-premium-card button:last-of-type{background:linear-gradient(100deg,#ffd45c,#f2b827)!important;color:#111923!important;border:1px solid rgba(255,226,123,.95)!important;box-shadow:0 12px 30px rgba(242,184,39,.24),inset 0 1px rgba(255,255,255,.2)!important}
@keyframes tamPremiumIn{from{opacity:0;transform:translateY(12px) scale(.994)}to{opacity:1;transform:none}}
@media(max-width:760px){.tam-premium-card{width:min(100%,calc(100vw - 18px));border-radius:22px}.tam-premium-card>*{padding:26px 16px 24px!important;border-radius:21px!important}.tam-premium-card form{grid-template-columns:1fr!important;gap:16px!important}.tam-premium-card form>*{grid-column:1!important}}
@media(prefers-reduced-motion:reduce){.tam-premium-card,.tam-premium-card *{animation:none!important;transition:none!important}}
'''


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bundle',required=True)
    ap.add_argument('--index',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    args=ap.parse_args()

    bundle=Path(args.bundle).read_text(encoding='utf-8')
    index=Path(args.index).read_text(encoding='utf-8')

    if CURRENT_BUNDLE not in index:
        raise SystemExit(f'Expected current bundle reference missing: {CURRENT_BUNDLE}')
    if 'CAREERS_FORM_ONLY_PATCHED' not in bundle:
        raise SystemExit('Form-only bundle marker missing')
    if PATCH_MARKER in bundle:
        raise SystemExit('V2 already present')
    if bundle.count(TARGET_CALL)!=1:
        raise SystemExit(f'Expected exactly one {TARGET_CALL}, found {bundle.count(TARGET_CALL)}')

    css_js=json.dumps(CSS,ensure_ascii=False,separators=(',',':'))
    replacement='b.jsxs("div",{className:"tam-premium-card",children:[b.jsx("style",{children:'+css_js+'}),'+TARGET_CALL+']})'
    patched=bundle.replace(TARGET_CALL,replacement,1)
    patched_index=index.replace(CURRENT_BUNDLE,NEW_BUNDLE,1)

    guards={
        'patch_marker_once':patched.count(PATCH_MARKER)==1,
        'premium_wrapper_once':patched.count('className:"tam-premium-card"')==1,
        'form_component_preserved':patched.count(TARGET_CALL)==1,
        'form_only_marker_preserved':'CAREERS_FORM_ONLY_PATCHED' in patched,
        'old_bundle_ref_removed':CURRENT_BUNDLE not in patched_index,
        'new_bundle_ref_once':patched_index.count(NEW_BUNDLE)==1,
        'reduced_motion_present':'prefers-reduced-motion:reduce' in patched,
        'step_logic_untouched':bundle.count('form.step1.title')==patched.count('form.step1.title'),
        'postmessage_untouched':bundle.count('formSubmission')==patched.count('formSubmission'),
    }
    failed=[k for k,v in guards.items() if not v]
    if failed: raise SystemExit('Guard failed: '+', '.join(failed))

    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    bundle_out=out/NEW_BUNDLE
    index_out=out/'index.html'
    bundle_out.write_text(patched,encoding='utf-8')
    index_out.write_text(patched_index,encoding='utf-8')

    manifest={
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,'current_bundle':CURRENT_BUNDLE,'new_bundle':NEW_BUNDLE,
      'strategy':'bundle_render_tree_wrapper_plus_scoped_premium_css_no_root_or_body_mutation',
      'bundle_sha256_before':hashlib.sha256(bundle.encode()).hexdigest(),
      'bundle_sha256_after':hashlib.sha256(patched.encode()).hexdigest(),
      'index_sha256_after':hashlib.sha256(patched_index.encode()).hexdigest(),
      'bundle_output':str(bundle_out),'index_output':str(index_out),
      'guards':guards,'form_logic_changed':False,'backend_changed':False,'git_mutations_by_patch_runner':False,
      'visual_qa_required':True,'functional_qa_required':True
    }
    if args.manifest: Path(args.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
