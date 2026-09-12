#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.2'
TARGET_VERSION='V6.3'
PATCH_ID='CAREERS_FORM_CUSTOM_CONTROLS_CLEAN_REBUILD_V6_3'
PATCH_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_3'
V5_MARKER='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
V6_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6'
V61_MARKER='TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_1'
V62_MARKER='TAM_CAREERS_FORM_RUNTIME_FIX_V6_2'
OLD_BUNDLE='index-CcV62q4Ms.js'
OLD_CSS='index-CcV61p7Ks.css'
NEW_BUNDLE='index-CcV63s9Rt.js'
CUT_TOKEN=';/* TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6 */'

JS=r''';/* TAM_CAREERS_FORM_CUSTOM_CONTROLS_V6_3 */
(()=>{
  'use strict';
  const doc=document;
  const q=(s,r=doc)=>r.querySelector(s);
  const qa=(s,r=doc)=>Array.from(r.querySelectorAll(s));
  const ar=()=>((doc.documentElement.dir||'').toLowerCase()==='rtl'||(doc.documentElement.lang||'').toLowerCase().startsWith('ar'));
  let portal=null, opener=null;

  const safeClass=(el,name)=>{
    const cur=(el.getAttribute('class')||'').split(/\s+/).filter(Boolean);
    if(!cur.includes(name))cur.push(name);
    el.setAttribute('class',cur.join(' '));
  };
  const closePortal=()=>{
    if(portal&&portal.parentNode)portal.parentNode.removeChild(portal);
    portal=null;
    if(opener)opener.setAttribute('aria-expanded','false');
    opener=null;
  };
  const placePortal=(node,btn)=>{
    doc.body.appendChild(node);
    const r=btn.getBoundingClientRect();
    const desired=Math.max(r.width,Math.min(340,window.innerWidth-20));
    node.style.width=desired+'px';
    const left=Math.min(Math.max(10,r.left),Math.max(10,window.innerWidth-desired-10));
    node.style.left=left+'px';
    const h=Math.min(node.scrollHeight||360,380);
    let top=r.bottom+8;
    if(top+h>window.innerHeight-10)top=Math.max(10,r.top-h-8);
    node.style.top=top+'px';
  };
  const openPortal=(btn,node)=>{
    closePortal();
    portal=node;opener=btn;
    btn.setAttribute('aria-expanded','true');
    placePortal(node,btn);
  };
  const fire=(el)=>{
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  };
  const setNativeValue=(el,value)=>{
    const proto=el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
    const d=Object.getOwnPropertyDescriptor(proto,'value');
    if(d&&d.set)d.set.call(el,value);else el.value=value;
    fire(el);
  };
  const makeShell=(el,kind,index)=>{
    safeClass(el,'tam-native-hidden');
    el.setAttribute('aria-hidden','true');
    el.tabIndex=-1;
    const shell=doc.createElement('div');
    shell.setAttribute('class','tam-control-shell');
    shell.setAttribute('data-kind',kind);
    const btn=doc.createElement('button');
    btn.type='button';
    btn.setAttribute('class','tam-control-button');
    btn.setAttribute('data-tam-control',kind);
    btn.setAttribute('data-tam-control-index',String(index));
    btn.setAttribute('aria-haspopup',kind==='select'?'listbox':'dialog');
    btn.setAttribute('aria-expanded','false');
    el.insertAdjacentElement('afterend',shell);
    shell.appendChild(btn);
    return {shell,btn};
  };

  const enhanceSelect=(el,index)=>{
    if(el.getAttribute('data-tam-v63')==='1')return;
    el.setAttribute('data-tam-v63','1');
    const {btn}=makeShell(el,'select',index);
    const sync=()=>{
      const o=el.options&&el.selectedIndex>=0?el.options[el.selectedIndex]:null;
      const txt=o?(o.textContent||'').trim():'';
      if(el.value){btn.textContent=txt||el.value;}
      else{btn.innerHTML='<span class="tam-control-placeholder">'+(txt||(ar()?'اختر':'Select'))+'</span>';}
    };
    sync();
    el.addEventListener('change',sync);
    btn.addEventListener('click',()=>{
      const p=doc.createElement('div');
      p.id='tam-control-portal';
      p.dir=ar()?'rtl':'ltr';
      p.innerHTML='<div class="tam-select-menu" role="listbox"></div>';
      const box=q('.tam-select-menu',p);
      Array.from(el.options||[]).forEach((o,i)=>{
        const b=doc.createElement('button');
        b.type='button';
        b.setAttribute('class','tam-select-option');
        b.setAttribute('role','option');
        b.setAttribute('aria-selected',String(i===el.selectedIndex));
        b.textContent=o.textContent||'';
        b.disabled=!!o.disabled;
        b.addEventListener('click',()=>{
          setNativeValue(el,o.value);
          sync();
          closePortal();
        });
        box.appendChild(b);
      });
      openPortal(btn,p);
    });
  };

  const pad=n=>String(n).padStart(2,'0');
  const iso=(y,m,d)=>y+'-'+pad(m+1)+'-'+pad(d);
  const parse=s=>/^\d{4}-\d{2}-\d{2}$/.test(s||'')?new Date(Number(s.slice(0,4)),Number(s.slice(5,7))-1,Number(s.slice(8,10))):null;

  const enhanceDate=(el,index)=>{
    if(el.getAttribute('data-tam-v63')==='1')return;
    el.setAttribute('data-tam-v63','1');
    const {btn}=makeShell(el,'date',index);
    const sync=()=>{
      if(el.value)btn.textContent=el.value;
      else btn.innerHTML='<span class="tam-control-placeholder">'+(el.getAttribute('placeholder')||'yyyy-mm-dd')+'</span>';
    };
    sync();
    el.addEventListener('change',sync);
    btn.addEventListener('click',()=>{
      const current=parse(el.value)||new Date();
      let y=current.getFullYear(),m=current.getMonth();
      const min=parse(el.min),max=parse(el.max),today=new Date();
      const p=doc.createElement('div');
      p.id='tam-control-portal';p.dir=ar()?'rtl':'ltr';
      p.innerHTML='<div class="tam-date-picker" role="dialog"><div class="tam-date-head"><button type="button" class="tam-date-nav tam-prev">‹</button><div class="tam-date-title"></div><button type="button" class="tam-date-nav tam-next">›</button></div><div class="tam-date-week"></div><div class="tam-date-grid"></div></div>';
      const render=()=>{
        const selected=parse(el.value);
        q('.tam-date-title',p).textContent=new Intl.DateTimeFormat(ar()?'ar-EG':'en-US',{month:'long',year:'numeric'}).format(new Date(y,m,1));
        const wk=q('.tam-date-week',p);wk.innerHTML='';
        (ar()?['ح','ن','ث','ر','خ','ج','س']:['Su','Mo','Tu','We','Th','Fr','Sa']).forEach(n=>{const s=doc.createElement('span');s.textContent=n;wk.appendChild(s)});
        const grid=q('.tam-date-grid',p);grid.innerHTML='';
        const first=new Date(y,m,1).getDay(),days=new Date(y,m+1,0).getDate(),prevDays=new Date(y,m,0).getDate();
        for(let cell=0;cell<42;cell++){
          let yy=y,mm=m,dd=cell-first+1,muted=false;
          if(dd<1){mm=m-1;if(mm<0){mm=11;yy--}dd=prevDays+dd;muted=true}
          else if(dd>days){dd-=days;mm=m+1;if(mm>11){mm=0;yy++}muted=true}
          const d=new Date(yy,mm,dd);
          const b=doc.createElement('button');b.type='button';
          let cn='tam-date-day';if(muted)cn+=' is-muted';if(today.toDateString()===d.toDateString())cn+=' is-today';if(selected&&selected.toDateString()===d.toDateString())cn+=' is-selected';
          b.setAttribute('class',cn);b.textContent=String(dd);
          if((min&&d<min)||(max&&d>max))b.disabled=true;
          b.addEventListener('click',()=>{setNativeValue(el,iso(yy,mm,dd));sync();closePortal()});
          grid.appendChild(b);
        }
      };
      q('.tam-prev',p).addEventListener('click',()=>{m--;if(m<0){m=11;y--}render()});
      q('.tam-next',p).addEventListener('click',()=>{m++;if(m>11){m=0;y++}render()});
      render();openPortal(btn,p);
    });
  };

  const enhance=()=>{
    let si=0,di=0;
    qa('form select').forEach(el=>{try{enhanceSelect(el,si++)}catch(e){console.error('[TAM V6.3 SELECT]',e)}});
    qa('form input[type="date"]').forEach(el=>{try{enhanceDate(el,di++)}catch(e){console.error('[TAM V6.3 DATE]',e)}});
    doc.documentElement.setAttribute('data-tam-v63-selects',String(qa('.tam-control-shell[data-kind="select"] .tam-control-button').length));
    doc.documentElement.setAttribute('data-tam-v63-dates',String(qa('.tam-control-shell[data-kind="date"] .tam-control-button').length));
  };

  doc.addEventListener('click',e=>{if(portal&&opener&&!portal.contains(e.target)&&!opener.contains(e.target))closePortal()},true);
  doc.addEventListener('keydown',e=>{if(e.key==='Escape')closePortal()});
  window.addEventListener('resize',closePortal);window.addEventListener('scroll',closePortal,true);
  new MutationObserver(()=>enhance()).observe(doc.documentElement,{subtree:true,childList:true});
  if(doc.readyState==='loading')doc.addEventListener('DOMContentLoaded',enhance,{once:true});else enhance();
  setTimeout(enhance,250);setTimeout(enhance,1200);
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

    if bp.name!=OLD_BUNDLE or OLD_BUNDLE not in index: raise SystemExit('V6.2 JS baseline mismatch')
    if cp.name!=OLD_CSS or OLD_CSS not in index: raise SystemExit('V6.2 CSS baseline mismatch')
    for marker in (V5_MARKER,V6_MARKER,V61_MARKER,V62_MARKER):
        if marker not in bundle: raise SystemExit(f'Missing baseline marker: {marker}')
    if V5_MARKER not in css or V6_MARKER not in css or V61_MARKER not in css: raise SystemExit('Required CSS markers missing')
    if PATCH_MARKER in bundle: raise SystemExit('V6.3 already present')
    if bundle.count(CUT_TOKEN)!=1: raise SystemExit(f'Expected exactly one V6 cut token, found {bundle.count(CUT_TOKEN)}')

    cut=bundle.index(CUT_TOKEN)
    base=bundle[:cut].rstrip()
    if V5_MARKER not in base or 'xhr.upload.onprogress' not in base or 'e.loaded/e.total' not in base:
        raise SystemExit('V5 upload progress not preserved before cut point')
    new_bundle=base+JS+'\n'
    new_index=index.replace(OLD_BUNDLE,NEW_BUNDLE,1)

    guards={
      'v5_progress_preserved':V5_MARKER in new_bundle and 'xhr.upload.onprogress' in new_bundle and 'e.loaded/e.total' in new_bundle,
      'broken_v6_js_removed':V6_MARKER not in new_bundle,
      'broken_v61_js_removed':V61_MARKER not in new_bundle,
      'broken_v62_js_removed':V62_MARKER not in new_bundle,
      'v63_marker_once':new_bundle.count(PATCH_MARKER)==1,
      'no_classList_usage':'classList' not in JS,
      'custom_select_present':'data-tam-control\',kind' not in JS and 'tam-select-option' in JS,
      'custom_date_present':'tam-date-picker' in JS,
      'react_value_setter_present':'Object.getOwnPropertyDescriptor' in JS,
      'new_bundle_ref':NEW_BUNDLE in new_index,
      'old_bundle_ref_removed':OLD_BUNDLE not in new_index,
      'css_unchanged':OLD_CSS in new_index,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'remove_all_broken_v6_v61_v62_runtime_js_and_rebuild_custom_controls_cleanly_on_v5_baseline',
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
