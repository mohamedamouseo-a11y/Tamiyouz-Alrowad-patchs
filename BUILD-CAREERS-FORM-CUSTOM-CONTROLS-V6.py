#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID='CAREERS_FORM_CUSTOM_CONTROLS_V6'
PATCH_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6'
OLD_BUNDLE='index-RpV5h8Ns.js'
OLD_CSS='index-RpV5h8Ns.css'
NEW_BUNDLE='index-CcV6n2Qs.js'
NEW_CSS='index-CcV6n2Qs.css'
REQUIRED_V5='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'

CSS=r'''/* TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6 */
.tam-native-hidden{position:absolute!important;opacity:0!important;pointer-events:none!important;width:1px!important;height:1px!important;min-height:0!important;margin:0!important;padding:0!important;border:0!important;clip:rect(0 0 0 0)!important;clip-path:inset(50%)!important;overflow:hidden!important}
.tam-control-shell{position:relative;width:100%;min-width:0}
.tam-control-button{width:100%;min-height:54px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:0 14px;border-radius:13px;border:1px solid rgba(124,151,183,.34);background:linear-gradient(180deg,#1a304a,#152941);color:#f8fafc;font:inherit;text-align:inherit;cursor:pointer;box-shadow:inset 0 1px rgba(255,255,255,.03);transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease}
.tam-control-button:hover,.tam-control-button[aria-expanded="true"]{border-color:#f2b827;box-shadow:0 0 0 3px rgba(242,184,39,.10),0 10px 26px rgba(0,0,0,.14)}
.tam-control-button:after{content:"⌄";color:#f2b827;font-size:18px;line-height:1;flex:0 0 auto}
.tam-control-shell[data-kind="date"] .tam-control-button:after{content:"▣";font-size:14px}
.tam-control-button .tam-control-placeholder{color:#8193aa}
#tam-control-portal{position:fixed;z-index:2147483000;min-width:220px;max-width:min(92vw,420px);border:1px solid rgba(242,184,39,.38);border-radius:15px;background:linear-gradient(180deg,#142a43,#0f2238);box-shadow:0 22px 60px rgba(0,0,0,.48),0 0 28px rgba(242,184,39,.08);overflow:hidden;color:#f8fafc;font-family:inherit}
.tam-select-menu{max-height:310px;overflow:auto;padding:7px;scrollbar-width:thin;scrollbar-color:#c89518 #102239}
.tam-select-option{width:100%;display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:40px;padding:9px 11px;border:0;border-radius:9px;background:transparent;color:#eef3f8;font:inherit;text-align:inherit;cursor:pointer}
.tam-select-option:hover,.tam-select-option:focus-visible{outline:none;background:rgba(242,184,39,.10);color:#ffd45c}
.tam-select-option[aria-selected="true"]{background:linear-gradient(90deg,rgba(242,184,39,.20),rgba(242,184,39,.08));color:#ffd45c;font-weight:800}
.tam-select-option[disabled]{opacity:.45;cursor:not-allowed}
.tam-date-picker{padding:12px;width:min(330px,92vw)}
.tam-date-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px}
.tam-date-title{flex:1;text-align:center;color:#ffd45c;font-weight:800;font-size:14px}
.tam-date-nav{width:34px;height:34px;border:1px solid rgba(242,184,39,.25);border-radius:9px;background:#182e48;color:#ffd45c;cursor:pointer;font-size:18px;line-height:1}
.tam-date-nav:hover{border-color:#f2b827;background:#1c3552}
.tam-date-week,.tam-date-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:4px}
.tam-date-week{margin-bottom:4px;color:#91a2b8;font-size:11px;text-align:center;font-weight:700}
.tam-date-day{aspect-ratio:1;border:0;border-radius:9px;background:transparent;color:#eef3f8;cursor:pointer;font:inherit;font-size:12px}
.tam-date-day:hover{background:rgba(242,184,39,.12);color:#ffd45c}
.tam-date-day.is-muted{opacity:.28}
.tam-date-day.is-today{box-shadow:inset 0 0 0 1px rgba(242,184,39,.55)}
.tam-date-day.is-selected{background:linear-gradient(135deg,#ffd45c,#d79b0d);color:#07111d;font-weight:900}
.tam-date-day:disabled{opacity:.18;cursor:not-allowed}
@media(max-width:760px){#tam-control-portal{max-width:calc(100vw - 20px)}.tam-date-picker{width:min(320px,calc(100vw - 20px))}}
@media(prefers-reduced-motion:reduce){.tam-control-button{transition:none!important}}
'''

JS=r''';/* TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6 */
(()=>{
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
  const isAr=()=>((document.documentElement.dir||'').toLowerCase()==='rtl'||(document.documentElement.lang||'').toLowerCase().startsWith('ar'));
  let portal=null, opener=null;
  const close=()=>{if(portal){portal.remove();portal=null}if(opener){opener.setAttribute('aria-expanded','false');opener=null}};
  const place=(node,btn)=>{document.body.appendChild(node);const r=btn.getBoundingClientRect();const w=Math.max(r.width,Math.min(330,window.innerWidth-20));node.style.width=w+'px';let left=Math.min(Math.max(10,r.left),window.innerWidth-w-10);node.style.left=left+'px';const h=Math.min(node.scrollHeight||330,360);let top=r.bottom+7;if(top+h>window.innerHeight-10)top=Math.max(10,r.top-h-7);node.style.top=top+'px'};
  const openPortal=(btn,node)=>{close();portal=node;opener=btn;btn.setAttribute('aria-expanded','true');place(node,btn)};
  const fire=(el)=>{el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))};
  const makeShell=(el,kind)=>{const shell=document.createElement('div');shell.className='tam-control-shell';shell.dataset.kind=kind;const btn=document.createElement('button');btn.type='button';btn.className='tam-control-button';btn.setAttribute('aria-haspopup',kind==='select'?'listbox':'dialog');btn.setAttribute('aria-expanded','false');el.classList.add('tam-native-hidden');el.insertAdjacentElement('afterend',shell);shell.appendChild(btn);return {shell,btn}};
  const enhanceSelect=(el)=>{
    if(el.dataset.tamV6)return;el.dataset.tamV6='1';
    const {btn}=makeShell(el,'select');
    const sync=()=>{const o=el.options[el.selectedIndex];const txt=o?o.textContent.trim():'';btn.textContent=txt|| (isAr()?'اختر':'Select');if(!el.value)btn.innerHTML='<span class="tam-control-placeholder">'+(txt|| (isAr()?'اختر':'Select'))+'</span>'};
    sync();
    btn.addEventListener('click',()=>{
      const menu=document.createElement('div');menu.id='tam-control-portal';menu.dir=isAr()?'rtl':'ltr';menu.innerHTML='<div class="tam-select-menu" role="listbox"></div>';const box=$('.tam-select-menu',menu);
      Array.from(el.options).forEach((o,i)=>{const b=document.createElement('button');b.type='button';b.className='tam-select-option';b.textContent=o.textContent;b.disabled=o.disabled;b.setAttribute('role','option');b.setAttribute('aria-selected',String(i===el.selectedIndex));b.addEventListener('click',()=>{el.selectedIndex=i;fire(el);sync();close()});box.appendChild(b)});
      openPortal(btn,menu);
    });
    el.addEventListener('change',sync);
  };
  const pad=n=>String(n).padStart(2,'0');
  const iso=(y,m,d)=>y+'-'+pad(m+1)+'-'+pad(d);
  const parse=s=>/^\d{4}-\d{2}-\d{2}$/.test(s||'')?new Date(Number(s.slice(0,4)),Number(s.slice(5,7))-1,Number(s.slice(8,10))):null;
  const enhanceDate=(el)=>{
    if(el.dataset.tamV6)return;el.dataset.tamV6='1';
    const {btn}=makeShell(el,'date');
    const sync=()=>{btn.textContent=el.value||el.getAttribute('placeholder')||'yyyy-mm-dd';if(!el.value)btn.innerHTML='<span class="tam-control-placeholder">'+(el.getAttribute('placeholder')||'yyyy-mm-dd')+'</span>'};sync();el.addEventListener('change',sync);
    btn.addEventListener('click',()=>{
      const base=parse(el.value)||new Date();let y=base.getFullYear(),m=base.getMonth();
      const min=parse(el.min),max=parse(el.max);const selected=parse(el.value);const today=new Date();
      const p=document.createElement('div');p.id='tam-control-portal';p.dir=isAr()?'rtl':'ltr';p.innerHTML='<div class="tam-date-picker" role="dialog" aria-modal="false"><div class="tam-date-head"><button type="button" class="tam-date-nav tam-prev">‹</button><div class="tam-date-title"></div><button type="button" class="tam-date-nav tam-next">›</button></div><div class="tam-date-week"></div><div class="tam-date-grid"></div></div>';
      const render=()=>{
        $('.tam-date-title',p).textContent=new Intl.DateTimeFormat(isAr()?'ar-EG':'en-US',{month:'long',year:'numeric'}).format(new Date(y,m,1));
        const wk=$('.tam-date-week',p);wk.innerHTML='';const names=isAr()?['ح','ن','ث','ر','خ','ج','س']:['Su','Mo','Tu','We','Th','Fr','Sa'];names.forEach(n=>{const s=document.createElement('span');s.textContent=n;wk.appendChild(s)});
        const grid=$('.tam-date-grid',p);grid.innerHTML='';const first=new Date(y,m,1).getDay(),days=new Date(y,m+1,0).getDate(),prevDays=new Date(y,m,0).getDate();
        for(let cell=0;cell<42;cell++){let yy=y,mm=m,dd=cell-first+1,muted=false;if(dd<1){mm=m-1;if(mm<0){mm=11;yy--}dd=prevDays+dd;muted=true}else if(dd>days){dd-=days;mm=m+1;if(mm>11){mm=0;yy++}muted=true}const d=new Date(yy,mm,dd);const b=document.createElement('button');b.type='button';b.className='tam-date-day'+(muted?' is-muted':'');b.textContent=String(dd);if(today.toDateString()===d.toDateString())b.classList.add('is-today');if(selected&&selected.toDateString()===d.toDateString())b.classList.add('is-selected');if((min&&d<min)||(max&&d>max))b.disabled=true;b.addEventListener('click',()=>{el.value=iso(yy,mm,dd);fire(el);sync();close()});grid.appendChild(b)}
      };
      $('.tam-prev',p).addEventListener('click',()=>{m--;if(m<0){m=11;y--}render()});$('.tam-next',p).addEventListener('click',()=>{m++;if(m>11){m=0;y++}render()});render();openPortal(btn,p);
    });
  };
  const enhance=()=>{document.querySelectorAll('form select').forEach(enhanceSelect);document.querySelectorAll('form input[type="date"]').forEach(enhanceDate)};
  document.addEventListener('click',e=>{if(portal&&opener&&!portal.contains(e.target)&&!opener.contains(e.target))close()},true);
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  window.addEventListener('resize',close);window.addEventListener('scroll',close,true);
  new MutationObserver(enhance).observe(document.documentElement,{subtree:true,childList:true});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',enhance);else enhance();
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
    bundle_p=Path(a.bundle);css_p=Path(a.css)
    bundle=bundle_p.read_text(encoding='utf-8');css=css_p.read_text(encoding='utf-8')
    if bundle_p.name!=OLD_BUNDLE or OLD_BUNDLE not in index: raise SystemExit('V5 JS baseline mismatch')
    if css_p.name!=OLD_CSS or OLD_CSS not in index: raise SystemExit('V5 CSS baseline mismatch')
    if REQUIRED_V5 not in bundle or REQUIRED_V5 not in css: raise SystemExit('V5 markers missing')
    if PATCH_MARKER in bundle or PATCH_MARKER in css: raise SystemExit('V6 already present')
    new_bundle=bundle.rstrip()+JS+'\n';new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=index.replace(OLD_BUNDLE,NEW_BUNDLE,1).replace(OLD_CSS,NEW_CSS,1)
    guards={
      'v5_js_preserved':REQUIRED_V5 in new_bundle,
      'v5_css_preserved':REQUIRED_V5 in new_css,
      'v6_js_marker_once':new_bundle.count(PATCH_MARKER)==1,
      'v6_css_marker_once':new_css.count(PATCH_MARKER)==1,
      'custom_select_present':'tam-select-option' in new_bundle and 'form select' in new_bundle,
      'custom_date_present':'tam-date-picker' in new_bundle and 'input[type="date"]' in new_bundle,
      'native_controls_preserved':'tam-native-hidden' in new_bundle and 'tam-native-hidden' in new_css,
      'change_events_synced':"new Event('change',{bubbles:true})" in new_bundle,
      'real_progress_preserved':'xhr.upload.onprogress' in new_bundle and 'e.loaded/e.total' in new_bundle,
      'new_js_ref':NEW_BUNDLE in new_index,
      'new_css_ref':NEW_CSS in new_index,
      'old_js_ref_removed':OLD_BUNDLE not in new_index,
      'old_css_ref_removed':OLD_CSS not in new_index,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8');(out/NEW_CSS).write_text(new_css,encoding='utf-8');(out/'index.html').write_text(new_index,encoding='utf-8')
    manifest={'patch':PATCH_ID,'patch_marker':PATCH_MARKER,'strategy':'custom_select_and_custom_datepicker_visual_layer_syncing_existing_native_controls','old_bundle':OLD_BUNDLE,'new_bundle':NEW_BUNDLE,'old_css':OLD_CSS,'new_css':NEW_CSS,'form_logic_changed':False,'api_changed':False,'native_values_preserved':True,'real_upload_progress_preserved':True,'guards':guards,'bundle_sha256':hashlib.sha256(new_bundle.encode()).hexdigest(),'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),'visual_qa_required':True,'functional_qa_required':True,'git_mutations_by_runner':False}
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
