#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.11'
TARGET_VERSION='V6.12'
PATCH_ID='CAREERS_PRIORITY_DATE_CV_PROGRESS_V6_12'
PATCH_MARKER='TAM_CAREERS_PRIORITY_DATE_CV_PROGRESS_V6_12'
REQUIRED_CSS_MARKER='TAM_CAREERS_GENDER_RADIO_VISUAL_V6_11'
REQUIRED_PROGRESS_CSS='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
REQUIRED_STABLE_BUNDLE_MARKER='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
STABLE_V5_BUNDLE='index-RpV5h8Ns.js'
NEW_CSS='index-VisualV612.css'
NEW_UI_JS='careers-priority-v612.js'

CSS=r'''/* TAM_CAREERS_PRIORITY_DATE_CV_PROGRESS_V6_12 */
/* Priority UI: premium custom DOB calendar + preserved real V5 CV upload progress. */
.tam-v612-date-popover{
  position:absolute;z-index:2147481000;display:none;width:min(340px,calc(100vw - 28px));
  padding:14px;border:1px solid rgba(242,184,39,.38);border-radius:18px;
  background:linear-gradient(180deg,#132b45 0%,#0d2035 100%);
  box-shadow:0 24px 64px rgba(1,8,18,.55),0 0 0 1px rgba(255,255,255,.025) inset;
  color:#f8fafc;direction:rtl;font-family:inherit
}
.tam-v612-date-popover[data-open="1"]{display:block}
.tam-v612-date-head{display:grid;grid-template-columns:42px 1fr 42px;align-items:center;gap:8px;margin-bottom:12px}
.tam-v612-date-title{text-align:center;color:#f6c84c;font-size:14px;font-weight:800;letter-spacing:.01em}
.tam-v612-date-nav{height:38px;border:1px solid rgba(242,184,39,.22);border-radius:11px;background:#172f4a;color:#f6c84c;font-size:20px;line-height:1;cursor:pointer;transition:.16s ease}
.tam-v612-date-nav:hover,.tam-v612-date-nav:focus-visible{outline:none;border-color:#f2b827;background:#1d3a59;box-shadow:0 0 0 3px rgba(242,184,39,.08)}
.tam-v612-week,.tam-v612-days{display:grid;grid-template-columns:repeat(7,1fr);gap:5px}
.tam-v612-week{margin-bottom:6px;color:#88a0bb;font-size:11px;font-weight:700;text-align:center}
.tam-v612-week span{padding:4px 0}
.tam-v612-day{aspect-ratio:1;border:1px solid transparent;border-radius:10px;background:transparent;color:#e9eef5;font:700 12px/1 inherit;cursor:pointer;transition:.14s ease}
.tam-v612-day:hover,.tam-v612-day:focus-visible{outline:none;border-color:rgba(242,184,39,.45);background:rgba(242,184,39,.10);color:#ffd45c}
.tam-v612-day[data-out="1"]{opacity:.26}
.tam-v612-day[data-today="1"]{border-color:rgba(242,184,39,.42);color:#f6c84c}
.tam-v612-day[data-selected="1"]{background:linear-gradient(135deg,#f5c744,#d89a0b);border-color:#ffd967;color:#07121f;box-shadow:0 6px 16px rgba(218,158,13,.22)}
.tam-v612-day:disabled{opacity:.18;cursor:not-allowed;background:transparent;color:#8a9bae}
.tam-v612-date-foot{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:12px;padding-top:10px;border-top:1px solid rgba(138,160,184,.13)}
.tam-v612-date-action{border:0;background:transparent;color:#aabbd0;font:700 11px/1 inherit;cursor:pointer;padding:7px 8px;border-radius:8px}
.tam-v612-date-action:hover,.tam-v612-date-action:focus-visible{outline:none;color:#f6c84c;background:rgba(242,184,39,.08)}
input[type="date"][data-tam-v612="1"]{cursor:pointer!important}
input[type="date"][data-tam-v612="1"]::-webkit-calendar-picker-indicator{pointer-events:none!important}
#tam-cv-progress{overflow:hidden}
#tam-cv-progress:not([hidden]){animation:tamV612ProgressIn .2s ease both}
#tam-cv-progress .tam-cv-progress-track{height:10px!important;background:#091a2c!important;border-color:rgba(242,184,39,.16)!important}
#tam-cv-progress-bar{background:linear-gradient(90deg,#c58a0a 0%,#f2b827 52%,#ffdb6e 100%)!important;box-shadow:0 0 18px rgba(242,184,39,.32)!important}
@keyframes tamV612ProgressIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@media(max-width:640px){.tam-v612-date-popover{width:min(324px,calc(100vw - 20px));padding:12px}.tam-v612-day{border-radius:9px}}
@media(prefers-reduced-motion:reduce){.tam-v612-date-nav,.tam-v612-day,#tam-cv-progress{transition:none!important;animation:none!important}}
'''

JS=r'''/* TAM_CAREERS_PRIORITY_DATE_CV_PROGRESS_V6_12 */
(()=>{
  if(window.__tamV612Loaded)return;window.__tamV612Loaded=true;
  const isAr=()=>((document.documentElement.lang||'').toLowerCase().startsWith('ar')||(document.documentElement.dir||'').toLowerCase()==='rtl');
  const pad=n=>String(n).padStart(2,'0');
  const iso=d=>`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const parse=s=>{if(!/^\d{4}-\d{2}-\d{2}$/.test(s||''))return null;const [y,m,d]=s.split('-').map(Number),x=new Date(y,m-1,d);return x.getFullYear()===y&&x.getMonth()===m-1&&x.getDate()===d?x:null};
  const monthNamesAr=['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];
  const monthNamesEn=['January','February','March','April','May','June','July','August','September','October','November','December'];
  const weekAr=['س','ح','ن','ث','ر','خ','ج'];
  const weekEn=['Su','Mo','Tu','We','Th','Fr','Sa'];

  function enhance(input){
    if(!input||input.dataset.tamV612==='1')return;
    input.dataset.tamV612='1';
    input.setAttribute('aria-haspopup','dialog');
    const pop=document.createElement('div');pop.className='tam-v612-date-popover';pop.dataset.open='0';
    const id='tam-v612-date-'+Math.random().toString(36).slice(2);pop.id=id;input.setAttribute('aria-controls',id);input.setAttribute('aria-expanded','false');
    const ar=isAr();
    pop.innerHTML=`<div class="tam-v612-date-head"><button type="button" class="tam-v612-date-nav tam-v612-prev" aria-label="${ar?'الشهر السابق':'Previous month'}">‹</button><div class="tam-v612-date-title"></div><button type="button" class="tam-v612-date-nav tam-v612-next" aria-label="${ar?'الشهر التالي':'Next month'}">›</button></div><div class="tam-v612-week"></div><div class="tam-v612-days"></div><div class="tam-v612-date-foot"><button type="button" class="tam-v612-date-action tam-v612-clear">${ar?'مسح':'Clear'}</button><button type="button" class="tam-v612-date-action tam-v612-today">${ar?'اليوم':'Today'}</button></div>`;
    document.body.appendChild(pop);
    let selected=parse(input.value), view=selected?new Date(selected):new Date();
    const min=parse(input.min),max=parse(input.max);
    const title=pop.querySelector('.tam-v612-date-title'),week=pop.querySelector('.tam-v612-week'),days=pop.querySelector('.tam-v612-days');
    week.innerHTML=(ar?weekAr:weekEn).map(x=>`<span>${x}</span>`).join('');

    const allowed=d=>(!min||d>=min)&&(!max||d<=max);
    const render=()=>{
      const names=ar?monthNamesAr:monthNamesEn;title.textContent=`${names[view.getMonth()]} ${view.getFullYear()}`;days.innerHTML='';
      const first=new Date(view.getFullYear(),view.getMonth(),1);const offset=first.getDay();const start=new Date(view.getFullYear(),view.getMonth(),1-offset);
      const today=new Date();today.setHours(0,0,0,0);
      for(let i=0;i<42;i++){
        const d=new Date(start);d.setDate(start.getDate()+i);d.setHours(0,0,0,0);
        const b=document.createElement('button');b.type='button';b.className='tam-v612-day';b.textContent=String(d.getDate());
        b.dataset.out=d.getMonth()===view.getMonth()?'0':'1';
        if(d.getTime()===today.getTime())b.dataset.today='1';
        if(selected&&iso(d)===iso(selected))b.dataset.selected='1';
        if(!allowed(d))b.disabled=true;
        b.addEventListener('click',()=>{selected=d;input.value=iso(d);input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));close();});
        days.appendChild(b);
      }
    };
    const position=()=>{const r=input.getBoundingClientRect();const w=Math.min(340,window.innerWidth-28);let left=Math.max(14,Math.min(window.innerWidth-w-14,r.right-w));let top=r.bottom+8;if(top+390>window.innerHeight)top=Math.max(10,r.top-390);pop.style.left=(left+window.scrollX)+'px';pop.style.top=(top+window.scrollY)+'px';};
    const open=()=>{selected=parse(input.value);view=selected?new Date(selected):new Date();render();position();pop.dataset.open='1';input.setAttribute('aria-expanded','true');};
    const close=()=>{pop.dataset.open='0';input.setAttribute('aria-expanded','false');};
    const toggle=()=>pop.dataset.open==='1'?close():open();
    input.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();input.focus({preventScroll:true});toggle();});
    input.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '||e.key==='ArrowDown'){e.preventDefault();open()}else if(e.key==='Escape')close()});
    pop.querySelector('.tam-v612-prev').addEventListener('click',()=>{view=new Date(view.getFullYear(),view.getMonth()-1,1);render()});
    pop.querySelector('.tam-v612-next').addEventListener('click',()=>{view=new Date(view.getFullYear(),view.getMonth()+1,1);render()});
    pop.querySelector('.tam-v612-clear').addEventListener('click',()=>{input.value='';selected=null;input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));close()});
    pop.querySelector('.tam-v612-today').addEventListener('click',()=>{const d=new Date();d.setHours(0,0,0,0);if(allowed(d)){input.value=iso(d);selected=d;input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));close()}});
    document.addEventListener('pointerdown',e=>{if(pop.dataset.open==='1'&&e.target!==input&&!pop.contains(e.target))close()},true);
    window.addEventListener('resize',()=>{if(pop.dataset.open==='1')position()});window.addEventListener('scroll',()=>{if(pop.dataset.open==='1')position()},{passive:true});
  }

  const scan=()=>document.querySelectorAll('input[type="date"]').forEach(enhance);
  scan();new MutationObserver(scan).observe(document.documentElement,{childList:true,subtree:true});
})();
'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--stable-v5-bundle',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    ip=Path(a.index);cp=Path(a.css);bp=Path(a.stable_v5_bundle)
    index=ip.read_text(encoding='utf-8');css=cp.read_text(encoding='utf-8');bundle=bp.read_text(encoding='utf-8')
    if REQUIRED_CSS_MARKER not in css: raise SystemExit('V6.11 CSS baseline marker missing')
    if REQUIRED_PROGRESS_CSS not in css: raise SystemExit('V5 real progress CSS marker missing from current visual CSS chain')
    if bp.name!=STABLE_V5_BUNDLE: raise SystemExit('Stable V5 bundle filename mismatch')
    if REQUIRED_STABLE_BUNDLE_MARKER not in bundle: raise SystemExit('Stable V5 progress marker missing')
    if 'xhr.upload.onprogress' not in bundle or 'e.loaded/e.total' not in bundle: raise SystemExit('Stable V5 real upload progress code missing')
    if 'CAREERS_FORM_ONLY_PATCHED' not in bundle: raise SystemExit('Stable form-only marker missing')
    if cp.name not in index: raise SystemExit('Current CSS reference mismatch')
    if PATCH_MARKER in index or PATCH_MARKER in css: raise SystemExit('V6.12 already present')

    scripts_before=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',index,re.I)
    module_matches=list(re.finditer(r'(<script[^>]+type=["\']module["\'][^>]+src=["\'])([^"\']+)(["\'][^>]*></script>)',index,re.I))
    if len(module_matches)!=1: raise SystemExit(f'Expected exactly one module script, found {len(module_matches)}')
    m=module_matches[0]
    stable_src=re.sub(r'[^/]+$',STABLE_V5_BUNDLE,m.group(2))
    new_index=index[:m.start()]+m.group(1)+stable_src+m.group(3)+index[m.end():]
    if '</body>' not in new_index.lower(): raise SystemExit('Closing body tag missing')
    inject=f'<script defer src="/assets/{NEW_UI_JS}"></script>\n'
    new_index=re.sub(r'</body>',inject+'</body>',new_index,count=1,flags=re.I)
    new_css=css.rstrip()+'\n'+CSS+'\n'
    new_index=new_index.replace(cp.name,NEW_CSS,1)

    scripts_after=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',new_index,re.I)
    guards={
      'v611_visual_chain_preserved':REQUIRED_CSS_MARKER in new_css,
      'v5_progress_css_preserved':REQUIRED_PROGRESS_CSS in new_css,
      'stable_v5_bundle_selected':STABLE_V5_BUNDLE in new_index,
      'real_progress_code_verified':'xhr.upload.onprogress' in bundle and 'e.loaded/e.total' in bundle,
      'form_only_baseline_verified':'CAREERS_FORM_ONLY_PATCHED' in bundle,
      'priority_js_injected':NEW_UI_JS in new_index,
      'new_css_referenced':NEW_CSS in new_index,
      'old_css_reference_removed':cp.name not in new_index,
      'date_ui_marker_once':JS.count(PATCH_MARKER)==1,
      'css_marker_once':new_css.count(PATCH_MARKER)==1,
      'no_endpoint_change':'fetch(' not in JS and 'XMLHttpRequest' not in JS,
      'date_value_sync':"dispatchEvent(new Event('change'" in JS,
      'native_date_input_preserved':'input[type="date"]' in JS,
      'existing_extra_scripts_preserved':all(s in scripts_after or re.search(r'index-[^/]+\.js$',s) for s in scripts_before),
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/NEW_UI_JS).write_text(JS,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'priority_1':'premium custom date picker bound to existing native date value',
      'priority_2':'restore verified stable V5 form bundle with real xhr upload progress',
      'stable_bundle':STABLE_V5_BUNDLE,
      'upload_progress_real':True,
      'upload_progress_formula':'loaded / total * 100',
      'upload_endpoint_changed':False,
      'formdata_changed':False,
      'backend_changed':False,
      'files_changed':['index.html',NEW_CSS,NEW_UI_JS],
      'guards':guards,
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'ui_js_sha256':hashlib.sha256(JS.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,
      'functional_qa_required':True,
      'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
