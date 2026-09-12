#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PROJECT='CAREERS'
BASE_VERSION='V6.3'
TARGET_VERSION='V6.4'
PATCH_ID='CAREERS_FORM_ISOLATED_CONTROLS_V6_4'
PATCH_MARKER='TAM_CAREERS_FORM_ISOLATED_CONTROLS_V6_4'
CURRENT_BUNDLE='index-CcV63s9Rt.js'
STABLE_V5_BUNDLE='index-RpV5h8Ns.js'
CURRENT_CSS='index-CcV61p7Ks.css'
NEW_CONTROL_JS='careers-controls-v64.js'
V5_MARKER='TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'

JS=r'''/* TAM_CAREERS_FORM_ISOLATED_CONTROLS_V6_4 */
(function(){
'use strict';
var doc=document, portal=null, opener=null;
function ar(){return ((doc.documentElement.dir||'').toLowerCase()==='rtl'||(doc.documentElement.lang||'').toLowerCase().indexOf('ar')===0)}
function q(s,r){return (r||doc).querySelector(s)}
function qa(s,r){return Array.prototype.slice.call((r||doc).querySelectorAll(s))}
function addClass(el,name){var c=(el.getAttribute('class')||'').split(/\s+/).filter(Boolean);if(c.indexOf(name)<0)c.push(name);el.setAttribute('class',c.join(' '))}
function closePortal(){if(portal&&portal.parentNode)portal.parentNode.removeChild(portal);portal=null;if(opener)opener.setAttribute('aria-expanded','false');opener=null}
function placePortal(node,btn){doc.body.appendChild(node);var r=btn.getBoundingClientRect(),w=Math.max(r.width,Math.min(340,window.innerWidth-20));node.style.width=w+'px';node.style.left=Math.min(Math.max(10,r.left),Math.max(10,window.innerWidth-w-10))+'px';var h=Math.min(node.scrollHeight||360,380),top=r.bottom+8;if(top+h>window.innerHeight-10)top=Math.max(10,r.top-h-8);node.style.top=top+'px'}
function openPortal(btn,node){closePortal();portal=node;opener=btn;btn.setAttribute('aria-expanded','true');placePortal(node,btn)}
function fire(el){el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))}
function setNativeValue(el,value){var proto=el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;var d=Object.getOwnPropertyDescriptor(proto,'value');var old=el.value;if(d&&d.set)d.set.call(el,value);else el.value=value;if(el._valueTracker&&el._valueTracker.setValue)el._valueTracker.setValue(old);fire(el)}
function makeShell(el,kind,index){addClass(el,'tam-native-hidden');el.setAttribute('aria-hidden','true');el.tabIndex=-1;var shell=doc.createElement('div');shell.setAttribute('class','tam-control-shell');shell.setAttribute('data-kind',kind);var btn=doc.createElement('button');btn.type='button';btn.setAttribute('class','tam-control-button');btn.setAttribute('data-tam-control',kind);btn.setAttribute('data-tam-control-index',String(index));btn.setAttribute('aria-haspopup',kind==='select'?'listbox':'dialog');btn.setAttribute('aria-expanded','false');el.insertAdjacentElement('afterend',shell);shell.appendChild(btn);return {shell:shell,btn:btn}}
function enhanceSelect(el,index){var next=el.nextElementSibling;if(el.getAttribute('data-tam-v64')==='1'&&next&&next.className&&String(next.className).indexOf('tam-control-shell')>=0)return;el.setAttribute('data-tam-v64','1');var x=makeShell(el,'select',index),btn=x.btn;function sync(){var o=el.options&&el.selectedIndex>=0?el.options[el.selectedIndex]:null,txt=o?String(o.textContent||'').trim():'';if(el.value)btn.textContent=txt||el.value;else btn.innerHTML='<span class="tam-control-placeholder">'+(txt||(ar()?'اختر':'Select'))+'</span>'}sync();el.addEventListener('change',sync);btn.addEventListener('click',function(){var p=doc.createElement('div');p.id='tam-control-portal';p.dir=ar()?'rtl':'ltr';p.innerHTML='<div class="tam-select-menu" role="listbox"></div>';var box=q('.tam-select-menu',p);Array.prototype.forEach.call(el.options||[],function(o,i){var b=doc.createElement('button');b.type='button';b.setAttribute('class','tam-select-option');b.setAttribute('role','option');b.setAttribute('aria-selected',String(i===el.selectedIndex));b.textContent=o.textContent||'';b.disabled=!!o.disabled;b.addEventListener('click',function(){setNativeValue(el,o.value);sync();closePortal()});box.appendChild(b)});openPortal(btn,p)})}
function pad(n){return String(n).padStart(2,'0')}
function iso(y,m,d){return y+'-'+pad(m+1)+'-'+pad(d)}
function parse(s){return /^\d{4}-\d{2}-\d{2}$/.test(s||'')?new Date(Number(s.slice(0,4)),Number(s.slice(5,7))-1,Number(s.slice(8,10))):null}
function enhanceDate(el,index){var next=el.nextElementSibling;if(el.getAttribute('data-tam-v64')==='1'&&next&&next.className&&String(next.className).indexOf('tam-control-shell')>=0)return;el.setAttribute('data-tam-v64','1');var x=makeShell(el,'date',index),btn=x.btn;function sync(){if(el.value)btn.textContent=el.value;else btn.innerHTML='<span class="tam-control-placeholder">'+(el.getAttribute('placeholder')||'yyyy-mm-dd')+'</span>'}sync();el.addEventListener('change',sync);btn.addEventListener('click',function(){var current=parse(el.value)||new Date(),y=current.getFullYear(),m=current.getMonth(),min=parse(el.min),max=parse(el.max),today=new Date();var p=doc.createElement('div');p.id='tam-control-portal';p.dir=ar()?'rtl':'ltr';p.innerHTML='<div class="tam-date-picker" role="dialog"><div class="tam-date-head"><button type="button" class="tam-date-nav tam-prev">‹</button><div class="tam-date-title"></div><button type="button" class="tam-date-nav tam-next">›</button></div><div class="tam-date-week"></div><div class="tam-date-grid"></div></div>';function render(){var selected=parse(el.value);q('.tam-date-title',p).textContent=new Intl.DateTimeFormat(ar()?'ar-EG':'en-US',{month:'long',year:'numeric'}).format(new Date(y,m,1));var wk=q('.tam-date-week',p);wk.innerHTML='';(ar()?['ح','ن','ث','ر','خ','ج','س']:['Su','Mo','Tu','We','Th','Fr','Sa']).forEach(function(n){var s=doc.createElement('span');s.textContent=n;wk.appendChild(s)});var grid=q('.tam-date-grid',p);grid.innerHTML='';var first=new Date(y,m,1).getDay(),days=new Date(y,m+1,0).getDate(),prevDays=new Date(y,m,0).getDate();for(var cell=0;cell<42;cell++){var yy=y,mm=m,dd=cell-first+1,muted=false;if(dd<1){mm=m-1;if(mm<0){mm=11;yy--}dd=prevDays+dd;muted=true}else if(dd>days){dd-=days;mm=m+1;if(mm>11){mm=0;yy++}muted=true}var d=new Date(yy,mm,dd),b=doc.createElement('button'),cn='tam-date-day';b.type='button';if(muted)cn+=' is-muted';if(today.toDateString()===d.toDateString())cn+=' is-today';if(selected&&selected.toDateString()===d.toDateString())cn+=' is-selected';b.setAttribute('class',cn);b.textContent=String(dd);if((min&&d<min)||(max&&d>max))b.disabled=true;(function(yyy,mmm,ddd){b.addEventListener('click',function(){setNativeValue(el,iso(yyy,mmm,ddd));sync();closePortal()})})(yy,mm,dd);grid.appendChild(b)}}q('.tam-prev',p).addEventListener('click',function(){m--;if(m<0){m=11;y--}render()});q('.tam-next',p).addEventListener('click',function(){m++;if(m>11){m=0;y++}render()});render();openPortal(btn,p)})}
function enhance(){var si=0,di=0;qa('form select').forEach(function(el){try{enhanceSelect(el,si++)}catch(e){console.error('[TAM V6.4 SELECT]',e)}});qa('form input[type="date"]').forEach(function(el){try{enhanceDate(el,di++)}catch(e){console.error('[TAM V6.4 DATE]',e)}});doc.documentElement.setAttribute('data-tam-v64-selects',String(qa('.tam-control-shell[data-kind="select"] .tam-control-button').length));doc.documentElement.setAttribute('data-tam-v64-dates',String(qa('.tam-control-shell[data-kind="date"] .tam-control-button').length))}
doc.addEventListener('click',function(e){if(portal&&opener&&!portal.contains(e.target)&&!opener.contains(e.target))closePortal()},true);doc.addEventListener('keydown',function(e){if(e.key==='Escape')closePortal()});window.addEventListener('resize',closePortal);window.addEventListener('scroll',closePortal,true);new MutationObserver(enhance).observe(doc.documentElement,{subtree:true,childList:true});if(doc.readyState==='loading')doc.addEventListener('DOMContentLoaded',enhance,{once:true});else enhance();setTimeout(enhance,300);setTimeout(enhance,1200);setTimeout(enhance,2500);doc.documentElement.setAttribute('data-tam-v64-loaded','1');
})();
'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--stable-v5-bundle',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()
    index=Path(a.index).read_text(encoding='utf-8')
    v5p=Path(a.stable_v5_bundle); cp=Path(a.css)
    v5=v5p.read_text(encoding='utf-8'); css=cp.read_text(encoding='utf-8')
    if CURRENT_BUNDLE not in index: raise SystemExit('V6.3 bundle ref missing from current index')
    if v5p.name!=STABLE_V5_BUNDLE: raise SystemExit('Stable V5 bundle filename mismatch')
    if V5_MARKER not in v5 or 'xhr.upload.onprogress' not in v5 or 'e.loaded/e.total' not in v5: raise SystemExit('Stable V5 real upload progress baseline missing')
    if cp.name!=CURRENT_CSS or CURRENT_CSS not in index: raise SystemExit('Current CSS baseline mismatch')
    if 'tam-select-option' not in css or 'tam-date-picker' not in css or 'tam-native-hidden' not in css: raise SystemExit('Required custom control CSS missing')
    if PATCH_MARKER in index: raise SystemExit('V6.4 already present')
    new_index=index.replace(CURRENT_BUNDLE,STABLE_V5_BUNDLE,1)
    tag=f'<script src="/assets/{NEW_CONTROL_JS}?v=64" defer data-version="{TARGET_VERSION}" data-marker="{PATCH_MARKER}"></script>'
    if '</body>' not in new_index: raise SystemExit('Missing </body> in index')
    new_index=new_index.replace('</body>',tag+'\n</body>',1)
    guards={
      'v5_bundle_restored':STABLE_V5_BUNDLE in new_index,
      'v63_bundle_removed':CURRENT_BUNDLE not in new_index,
      'isolated_script_ref':NEW_CONTROL_JS in new_index,
      'v64_marker_once':new_index.count(PATCH_MARKER)==1,
      'v5_progress_preserved':V5_MARKER in v5 and 'xhr.upload.onprogress' in v5 and 'e.loaded/e.total' in v5,
      'css_preserved':CURRENT_CSS in new_index,
      'custom_select_code':'tam-select-option' in JS,
      'custom_date_code':'tam-date-picker' in JS,
      'no_classList_in_v64':'classList' not in JS,
      'react_value_tracker_support':'_valueTracker' in JS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/NEW_CONTROL_JS).write_text(JS,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')
    manifest={
      'project':PROJECT,'base_version':BASE_VERSION,'target_version':TARGET_VERSION,
      'patch':PATCH_ID,'patch_marker':PATCH_MARKER,
      'strategy':'restore_stable_v5_main_bundle_and_run_custom_controls_as_separate_deferred_asset',
      'main_bundle':STABLE_V5_BUNDLE,'control_asset':NEW_CONTROL_JS,'css':CURRENT_CSS,
      'files_changed':['index.html',NEW_CONTROL_JS],
      'api_changed':False,'form_logic_changed':False,'css_changed':False,
      'real_upload_progress_preserved':True,'guards':guards,
      'control_js_sha256':hashlib.sha256(JS.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,'git_mutations_by_runner':False
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
