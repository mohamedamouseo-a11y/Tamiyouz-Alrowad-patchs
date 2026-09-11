#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "CAREERS_FORM_PREMIUM_V1"
PATCH_MARKER = "TAM_CAREERS_FORM_PREMIUM_V1"
STYLE_ID = "tam-careers-form-premium-v1"
SCRIPT_ID = "tam-careers-form-premium-v1-script"
EXPECTED_BUNDLE = "index-Bz9Kp2mQ.js"

STYLE = r'''<style id="tam-careers-form-premium-v1">
/* TAM_CAREERS_FORM_PREMIUM_V1 */
:root{
  --tam-bg:#0b172a;
  --tam-card:#0e1c30;
  --tam-card-2:#101f35;
  --tam-field:#162941;
  --tam-field-2:#1a2f4a;
  --tam-text:#f7f8fb;
  --tam-muted:#92a2b8;
  --tam-gold:#f2b827;
  --tam-gold-2:#ffd45c;
  --tam-line:#334963;
  --tam-error:#ff5d5d;
}
html,body{
  min-height:100%;
  background:
    radial-gradient(circle at 50% 6%,rgba(242,184,39,.08),transparent 28%),
    linear-gradient(180deg,#0c172a 0%,#0a1425 100%)!important;
}
body{
  margin:0!important;
  overflow-x:hidden!important;
  color:var(--tam-text)!important;
}
#root{
  min-height:100vh!important;
  display:flex!important;
  align-items:flex-start!important;
  justify-content:center!important;
  padding:28px 20px 40px!important;
  box-sizing:border-box!important;
}
.tam-careers-card{
  direction:rtl!important;
  position:relative!important;
  width:min(860px,100%)!important;
  margin:0 auto!important;
  padding:42px 46px 34px!important;
  box-sizing:border-box!important;
  border-radius:28px!important;
  background:
    linear-gradient(180deg,rgba(17,33,56,.98),rgba(11,24,42,.985))!important;
  border:1px solid rgba(242,184,39,.26)!important;
  box-shadow:
    0 26px 70px rgba(0,0,0,.34),
    0 0 0 1px rgba(255,255,255,.025) inset,
    0 0 42px rgba(242,184,39,.08)!important;
  overflow:hidden!important;
  animation:tamCardReveal .55s cubic-bezier(.2,.75,.2,1) both!important;
}
.tam-careers-card:before{
  content:"";
  position:absolute;
  inset:0 0 auto 0;
  height:2px;
  background:linear-gradient(90deg,transparent,var(--tam-gold),transparent);
  opacity:.95;
  pointer-events:none;
}
.tam-careers-card:after{
  content:"";
  position:absolute;
  width:220px;
  height:220px;
  top:-110px;
  left:-80px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(242,184,39,.10),transparent 67%);
  pointer-events:none;
}
.tam-careers-card h1,.tam-careers-card h2,.tam-careers-card h3{
  color:var(--tam-text)!important;
  letter-spacing:-.02em!important;
}
.tam-careers-card h1,.tam-careers-card h2{
  font-size:clamp(28px,3vw,40px)!important;
  line-height:1.25!important;
  margin-bottom:8px!important;
  text-align:center!important;
}
.tam-careers-card h1 strong,.tam-careers-card h2 strong{
  color:var(--tam-gold-2)!important;
}
.tam-careers-card p{
  color:var(--tam-muted)!important;
}
.tam-careers-stepper{
  direction:rtl!important;
  display:flex!important;
  align-items:flex-start!important;
  justify-content:center!important;
  gap:68px!important;
  position:relative!important;
  margin:28px auto 34px!important;
  max-width:520px!important;
}
.tam-careers-stepper:before{
  content:"";
  position:absolute;
  top:19px;
  right:23%;
  left:23%;
  height:1px;
  background:linear-gradient(90deg,var(--tam-line),rgba(242,184,39,.9));
  z-index:0;
}
.tam-step-personal,.tam-step-professional{
  position:relative!important;
  z-index:1!important;
  min-width:150px!important;
  text-align:center!important;
}
.tam-step-personal{order:1!important}
.tam-step-professional{order:2!important}
.tam-careers-card form{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:20px 18px!important;
  width:100%!important;
}
.tam-careers-card form > *{min-width:0!important}
.tam-careers-card label{
  display:block!important;
  margin:0 0 8px!important;
  color:#eef3f8!important;
  font-size:14px!important;
  font-weight:700!important;
  line-height:1.4!important;
}
.tam-careers-card label .text-destructive,
.tam-careers-card label [class*="destructive"]{
  color:var(--tam-error)!important;
}
.tam-careers-card input,
.tam-careers-card select,
.tam-careers-card textarea{
  width:100%!important;
  min-height:54px!important;
  box-sizing:border-box!important;
  border-radius:12px!important;
  border:1px solid rgba(125,150,180,.34)!important;
  background:linear-gradient(180deg,var(--tam-field-2),var(--tam-field))!important;
  color:var(--tam-text)!important;
  box-shadow:0 1px 0 rgba(255,255,255,.03) inset!important;
  transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease,background .2s ease!important;
}
.tam-careers-card input::placeholder,
.tam-careers-card textarea::placeholder{
  color:#8394aa!important;
  opacity:1!important;
}
.tam-careers-card input:hover,
.tam-careers-card select:hover,
.tam-careers-card textarea:hover{
  border-color:rgba(242,184,39,.42)!important;
}
.tam-careers-card input:focus,
.tam-careers-card select:focus,
.tam-careers-card textarea:focus{
  outline:none!important;
  border-color:var(--tam-gold)!important;
  background:#182d48!important;
  box-shadow:0 0 0 3px rgba(242,184,39,.12),0 8px 24px rgba(0,0,0,.14)!important;
  transform:translateY(-1px)!important;
}
.tam-careers-card input[type="radio"]{
  width:18px!important;
  height:18px!important;
  min-height:18px!important;
  accent-color:var(--tam-gold)!important;
}
.tam-careers-card button{
  min-height:56px!important;
  border-radius:12px!important;
  font-weight:800!important;
  letter-spacing:.01em!important;
  transition:transform .2s ease,box-shadow .2s ease,filter .2s ease!important;
}
.tam-careers-card button[type="submit"],
.tam-careers-card .tam-primary-action{
  background:linear-gradient(100deg,var(--tam-gold-2),var(--tam-gold))!important;
  color:#111923!important;
  border:1px solid rgba(255,224,117,.9)!important;
  box-shadow:0 10px 28px rgba(242,184,39,.22),0 0 0 1px rgba(255,255,255,.12) inset!important;
}
.tam-careers-card button:hover{
  transform:translateY(-2px)!important;
  filter:brightness(1.04)!important;
}
.tam-careers-card button:active{transform:translateY(0)!important}
.tam-careers-card .tam-full-row{grid-column:1/-1!important}
.tam-careers-card .tam-primary-action{grid-column:1/-1!important;width:100%!important}
.tam-careers-card .tam-field-focus{animation:tamFieldIn .28s ease both!important}
@keyframes tamCardReveal{
  from{opacity:0;transform:translateY(14px) scale(.992)}
  to{opacity:1;transform:none}
}
@keyframes tamFieldIn{
  from{opacity:.75;transform:translateY(4px)}
  to{opacity:1;transform:none}
}
@media(max-width:760px){
  #root{padding:14px 10px 24px!important}
  .tam-careers-card{padding:28px 18px 24px!important;border-radius:22px!important}
  .tam-careers-card form{grid-template-columns:1fr!important;gap:16px!important}
  .tam-careers-card form > *{grid-column:1!important}
  .tam-careers-stepper{gap:22px!important;margin:24px auto 28px!important}
  .tam-step-personal,.tam-step-professional{min-width:120px!important}
}
@media(prefers-reduced-motion:reduce){
  .tam-careers-card,.tam-careers-card *{animation:none!important;transition:none!important;scroll-behavior:auto!important}
}
</style>'''

SCRIPT = r'''<script id="tam-careers-form-premium-v1-script">
(function(){
  const norm = s => (s || '').replace(/\s+/g,' ').trim();
  function findByText(root,text){
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT);
    let n;
    while((n=walker.nextNode())){
      if(norm(n.textContent)===text) return n;
    }
    return null;
  }
  function commonAncestor(a,b){
    if(!a||!b) return null;
    const seen=new Set();
    for(let n=a;n;n=n.parentElement) seen.add(n);
    for(let n=b;n;n=n.parentElement) if(seen.has(n)) return n;
    return null;
  }
  function enhance(){
    const root=document.getElementById('root');
    if(!root) return false;
    const form=root.querySelector('form');
    if(!form) return false;

    const heading=[...root.querySelectorAll('h1,h2,h3,div,p')].find(el=>norm(el.textContent).includes('فرصتك تبدأ معنا اليوم'));
    let card=heading?commonAncestor(heading,form):form.parentElement;
    if(!card) card=form.parentElement;
    while(card && card!==root && card.getBoundingClientRect().width<520) card=card.parentElement;
    if(card && card!==root) card.classList.add('tam-careers-card');

    const personal=findByText(root,'البيانات الشخصية');
    const professional=findByText(root,'البيانات المهنية');
    if(personal&&professional){
      let stepper=commonAncestor(personal,professional);
      if(stepper&&stepper!==root){
        stepper.classList.add('tam-careers-stepper');
        let p=personal; while(p.parentElement!==stepper&&p.parentElement){p=p.parentElement}
        let r=professional; while(r.parentElement!==stepper&&r.parentElement){r=r.parentElement}
        p.classList.add('tam-step-personal');
        r.classList.add('tam-step-professional');
      }
    }

    [...form.querySelectorAll('input,select,textarea')].forEach(el=>{
      const holder=el.closest('div');
      if(holder) holder.classList.add('tam-field-focus');
    });

    const buttons=[...form.querySelectorAll('button')];
    buttons.forEach(btn=>{
      const t=norm(btn.textContent);
      if(t.includes('التالي')||t.includes('إرسال')||t.includes('تقديم')) btn.classList.add('tam-primary-action');
    });

    const controls=[...form.querySelectorAll('input,select,textarea')];
    controls.forEach(el=>{
      const holder=el.closest('div');
      if(!holder) return;
      const txt=norm(holder.textContent);
      if(txt.includes('الاسم')||txt.includes('العنوان الحالي')) holder.classList.add('tam-full-row');
    });

    return true;
  }
  let tries=0;
  const timer=setInterval(()=>{tries++; if(enhance()||tries>80) clearInterval(timer)},100);
  const obs=new MutationObserver(()=>enhance());
  obs.observe(document.documentElement,{subtree:true,childList:true});
})();
</script>'''


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--manifest')
    args=ap.parse_args()

    source=Path(args.source).read_text(encoding='utf-8')

    required=['<div id="root"',EXPECTED_BUNDLE,'</head>','</body>']
    for token in required:
        if token not in source:
            raise SystemExit(f'Required current Careers baseline missing: {token}')

    if PATCH_MARKER in source or STYLE_ID in source or SCRIPT_ID in source:
        raise SystemExit('CAREERS_FORM_PREMIUM_V1 already present')

    result=source.replace('</head>',STYLE+'\n</head>',1)
    result=result.replace('</body>',SCRIPT+'\n</body>',1)

    guards={
      'patch_marker_once': result.count(PATCH_MARKER)==1,
      'style_id_once': result.count(STYLE_ID)==1,
      'script_id_once': result.count(SCRIPT_ID)==1,
      'root_preserved': '<div id="root"' in result,
      'bundle_reference_preserved': EXPECTED_BUNDLE in result,
      'premium_card_css_present': '.tam-careers-card{' in result,
      'stepper_rtl_present': '.tam-careers-stepper{' in result and 'direction:rtl!important;' in result,
      'personal_step_order_right': '.tam-step-personal{order:1!important}' in result,
      'professional_step_order_left': '.tam-step-professional{order:2!important}' in result,
      'premium_field_focus_present': 'box-shadow:0 0 0 3px rgba(242,184,39,.12)' in result,
      'primary_action_present': '.tam-primary-action' in result,
      'reduced_motion_present': '@media(prefers-reduced-motion:reduce)' in result,
      'no_bundle_mutation': source.count(EXPECTED_BUNDLE)==result.count(EXPECTED_BUNDLE),
    }
    failed=[k for k,v in guards.items() if not v]
    if failed:
        raise SystemExit('Patch guard failed: '+', '.join(failed))

    Path(args.output).write_text(result,encoding='utf-8')
    manifest={
      'patch':PATCH_ID,
      'patch_marker':PATCH_MARKER,
      'style_id':STYLE_ID,
      'script_id':SCRIPT_ID,
      'strategy':'premium_css_plus_non_destructive_dom_tagging_on_form_only_careers_build',
      'expected_bundle':EXPECTED_BUNDLE,
      'files_changed':['/var/www/careers/index.html'],
      'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
      'output_sha256':hashlib.sha256(result.encode()).hexdigest(),
      'guards':guards,
      'form_logic_changed':False,
      'bundle_changed':False,
      'visual_qa_required':True,
      'functional_qa_required':True,
      'git_mutations_by_patch_runner':False,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
