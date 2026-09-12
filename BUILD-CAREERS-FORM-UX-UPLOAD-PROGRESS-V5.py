#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PATCH_ID = 'CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
PATCH_MARKER = 'TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5'
CURRENT_BUNDLE = 'index-Bz9Kp2mQ.js'
REQUIRED_CSS_MARKER = 'TAM_CAREERS_FORM_PREMIUM_CSS_V4'
NEW_BUNDLE = 'index-RpV5h8Ns.js'
NEW_CSS = 'index-RpV5h8Ns.css'

CSS = r'''/* TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5 */
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select,
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]{
  color-scheme:dark!important;
  background-color:#182e48!important;
  border-color:rgba(242,184,39,.24)!important;
  color:#f8fafc!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select{
  cursor:pointer!important;
  scrollbar-color:#d6a51f #102239!important;
  scrollbar-width:thin!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select option{
  background:#142942!important;
  color:#f8fafc!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form select option:checked{
  background:#b9890c!important;
  color:#07111d!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form input[type="date"]::-webkit-calendar-picker-indicator{
  opacity:.82!important;
  cursor:pointer!important;
  filter:invert(87%) sepia(44%) saturate(1358%) hue-rotate(343deg) brightness(101%) contrast(91%)!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form label:has(input[type="file"]){
  border:1px dashed rgba(242,184,39,.48)!important;
  border-radius:16px!important;
  background:linear-gradient(180deg,rgba(24,48,74,.78),rgba(15,34,55,.92))!important;
  min-height:112px!important;
  padding:22px!important;
  transition:border-color .2s ease,box-shadow .2s ease,transform .2s ease!important;
}
.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form label:has(input[type="file"]):hover{
  border-color:#f2b827!important;
  box-shadow:0 10px 28px rgba(242,184,39,.10)!important;
  transform:translateY(-1px)!important;
}
#tam-cv-progress{margin-top:12px;padding:13px 14px;border:1px solid rgba(242,184,39,.24);border-radius:13px;background:rgba(9,22,37,.78);box-shadow:inset 0 1px rgba(255,255,255,.025)}
#tam-cv-progress[hidden]{display:none!important}
.tam-cv-progress-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px;color:#e9eef5;font-size:12px;font-weight:700}
#tam-cv-progress-percent{color:#f2b827;font-variant-numeric:tabular-nums;direction:ltr}
.tam-cv-progress-track{height:8px;overflow:hidden;border-radius:999px;background:#0b1d31;border:1px solid rgba(126,154,184,.20)}
#tam-cv-progress-bar{height:100%;width:0%;border-radius:inherit;background:linear-gradient(90deg,#b98208,#ffd45c);box-shadow:0 0 16px rgba(242,184,39,.28);transition:width .14s linear}
#tam-cv-progress[data-state="success"]{border-color:rgba(74,222,128,.34)}
#tam-cv-progress[data-state="success"] #tam-cv-progress-percent{color:#86efac}
#tam-cv-progress[data-state="error"]{border-color:rgba(248,113,113,.42)}
#tam-cv-progress[data-state="error"] #tam-cv-progress-percent{color:#fca5a5}
@media(prefers-reduced-motion:reduce){#tam-cv-progress-bar,.container.mx-auto.px-4.pb-24>.max-w-2xl.mx-auto>.glass form label:has(input[type="file"]){transition:none!important;transform:none!important}}
'''

JS_HELPER = r''';/* TAM_CAREERS_FORM_UX_UPLOAD_PROGRESS_V5 */
(()=>{
  const nativeFetch=window.fetch.bind(window);
  const ar=()=>((document.documentElement.dir||'').toLowerCase()==='rtl'||(document.documentElement.lang||'').toLowerCase().startsWith('ar'));
  const ensureProgress=()=>{
    let box=document.getElementById('tam-cv-progress');
    if(box)return box;
    const input=document.querySelector('input[type="file"][name="cv"],input[type="file"][accept*=".pdf"]');
    if(!input)return null;
    const anchor=input.closest('label')||input.parentElement;
    if(!anchor||!anchor.parentElement)return null;
    box=document.createElement('div');
    box.id='tam-cv-progress';
    box.hidden=true;
    box.setAttribute('aria-live','polite');
    box.innerHTML='<div class="tam-cv-progress-head"><span id="tam-cv-progress-label"></span><strong id="tam-cv-progress-percent">0%</strong></div><div class="tam-cv-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div id="tam-cv-progress-bar"></div></div>';
    anchor.insertAdjacentElement('afterend',box);
    return box;
  };
  const setProgress=(pct,state)=>{
    const box=ensureProgress(); if(!box)return;
    const p=Math.max(0,Math.min(100,Math.round(Number(pct)||0)));
    const bar=box.querySelector('#tam-cv-progress-bar');
    const percent=box.querySelector('#tam-cv-progress-percent');
    const label=box.querySelector('#tam-cv-progress-label');
    const track=box.querySelector('[role="progressbar"]');
    box.hidden=false; box.dataset.state=state||'uploading';
    if(bar)bar.style.width=p+'%';
    if(percent)percent.textContent=p+'%';
    if(track)track.setAttribute('aria-valuenow',String(p));
    if(label)label.textContent=state==='success'?(ar()?'تم رفع السيرة الذاتية':'CV uploaded'):state==='error'?(ar()?'تعذر رفع السيرة الذاتية':'CV upload failed'):(ar()?'جاري رفع السيرة الذاتية':'Uploading CV');
  };
  window.__tamUploadFetch=(input,init={})=>{
    const body=init&&init.body;
    if(!(body instanceof FormData))return nativeFetch(input,init);
    const fileInput=document.querySelector('input[type="file"][name="cv"],input[type="file"][accept*=".pdf"]');
    const hasCv=!!(fileInput&&fileInput.files&&fileInput.files.length);
    return new Promise((resolve,reject)=>{
      const xhr=new XMLHttpRequest();
      const url=input instanceof Request?input.url:String(input);
      const method=(init.method||'GET').toUpperCase();
      xhr.open(method,url,true);
      if(init.credentials==='include')xhr.withCredentials=true;
      try{
        const headers=new Headers(init.headers||{});
        headers.forEach((v,k)=>{if(k.toLowerCase()!=='content-type')xhr.setRequestHeader(k,v)});
      }catch(e){}
      if(init.signal){
        if(init.signal.aborted){reject(new DOMException('Aborted','AbortError'));return;}
        init.signal.addEventListener('abort',()=>xhr.abort(),{once:true});
      }
      if(hasCv){setProgress(0,'uploading');xhr.upload.onprogress=e=>{if(e.lengthComputable&&e.total>0)setProgress((e.loaded/e.total)*100,'uploading')}}
      xhr.onload=()=>{
        if(hasCv)setProgress(100,'success');
        const raw=xhr.getAllResponseHeaders().trim().split(/[\r\n]+/); const headers=new Headers();
        raw.forEach(line=>{const i=line.indexOf(':');if(i>0)headers.append(line.slice(0,i).trim(),line.slice(i+1).trim())});
        const noBody=[204,205,304].includes(xhr.status);
        resolve(new Response(noBody?null:xhr.responseText,{status:xhr.status,statusText:xhr.statusText,headers}));
      };
      xhr.onerror=()=>{if(hasCv)setProgress(0,'error');reject(new TypeError('Network request failed'))};
      xhr.onabort=()=>{if(hasCv)setProgress(0,'error');reject(new DOMException('Aborted','AbortError'))};
      xhr.send(body);
    });
  };
})();
'''


def find_upload_fetch(bundle: str):
    positions=[m.start() for m in re.finditer(r'(?<![\w$])fetch\(',bundle)]
    candidates=[]
    for pos in positions:
        ctx=bundle[max(0,pos-4500):min(len(bundle),pos+4500)]
        score=0
        for token in ('FormData','window.location.hostname','cv'):
            if token in ctx: score+=1
        if score==3:
            candidates.append(pos)
    if len(candidates)!=1:
        raise SystemExit(f'Expected exactly one CV submit fetch candidate, found {len(candidates)}')
    return candidates[0], len(positions)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',required=True)
    ap.add_argument('--bundle',required=True)
    ap.add_argument('--css',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest')
    a=ap.parse_args()

    index_p=Path(a.index); bundle_p=Path(a.bundle); css_p=Path(a.css); out=Path(a.output_dir)
    index=index_p.read_text(encoding='utf-8')
    bundle=bundle_p.read_text(encoding='utf-8')
    css=css_p.read_text(encoding='utf-8')

    if CURRENT_BUNDLE not in index: raise SystemExit('Current JS bundle reference mismatch')
    if bundle_p.name!=CURRENT_BUNDLE: raise SystemExit('Bundle filename mismatch')
    if 'CAREERS_FORM_ONLY_PATCHED' not in bundle: raise SystemExit('Form-only baseline marker missing')
    if REQUIRED_CSS_MARKER not in css: raise SystemExit('Premium CSS V4 baseline marker missing')
    if css_p.name not in index: raise SystemExit('Current CSS reference mismatch')
    if PATCH_MARKER in bundle or PATCH_MARKER in css or PATCH_MARKER in index: raise SystemExit('V5 already present')
    if '.pdf,.doc,.docx' not in bundle: raise SystemExit('CV accept signature missing')
    if 'FormData' not in bundle: raise SystemExit('FormData signature missing')

    pos, total_fetches=find_upload_fetch(bundle)
    old='fetch('
    if bundle[pos:pos+len(old)]!=old: raise SystemExit('Fetch candidate boundary mismatch')
    new_bundle=bundle[:pos]+'window.__tamUploadFetch('+bundle[pos+len(old):]
    new_bundle=new_bundle.rstrip()+JS_HELPER+'\n'
    new_css=css.rstrip()+'\n'+CSS+'\n'

    new_index=index.replace(CURRENT_BUNDLE,NEW_BUNDLE,1).replace(css_p.name,NEW_CSS,1)

    guards={
      'upload_fetch_replaced_once':new_bundle.count('window.__tamUploadFetch(')==2,
      'helper_marker_once':new_bundle.count(PATCH_MARKER)==1,
      'css_marker_once':new_css.count(PATCH_MARKER)==1,
      'form_only_marker_preserved':'CAREERS_FORM_ONLY_PATCHED' in new_bundle,
      'cv_accept_preserved':'.pdf,.doc,.docx' in new_bundle,
      'formdata_preserved':'FormData' in new_bundle,
      'real_xhr_progress_present':'xhr.upload.onprogress' in new_bundle and 'e.loaded/e.total' in new_bundle,
      'fetch_response_compatibility':'new Response(' in new_bundle,
      'current_bundle_reference_removed':CURRENT_BUNDLE not in new_index,
      'new_bundle_referenced':NEW_BUNDLE in new_index,
      'new_css_referenced':NEW_CSS in new_index,
      'premium_v4_preserved':REQUIRED_CSS_MARKER in new_css,
      'dark_controls_present':'color-scheme:dark!important' in new_css,
      'progress_css_present':'#tam-cv-progress' in new_css,
      'no_root_css':'#root' not in CSS,
      'no_body_css':'body{' not in CSS,
    }
    bad=[k for k,v in guards.items() if not v]
    if bad: raise SystemExit('Guard failed: '+', '.join(bad))

    out.mkdir(parents=True,exist_ok=True)
    (out/NEW_BUNDLE).write_text(new_bundle,encoding='utf-8')
    (out/NEW_CSS).write_text(new_css,encoding='utf-8')
    (out/'index.html').write_text(new_index,encoding='utf-8')

    manifest={
      'patch':PATCH_ID,
      'patch_marker':PATCH_MARKER,
      'strategy':'premium_native_controls_plus_real_xhr_upload_progress_on_existing_final_form_submit',
      'old_bundle':CURRENT_BUNDLE,
      'new_bundle':NEW_BUNDLE,
      'old_css':css_p.name,
      'new_css':NEW_CSS,
      'total_fetch_calls_before':total_fetches,
      'cv_fetch_candidate_offset':pos,
      'upload_transport_before':'fetch',
      'upload_transport_after':'XMLHttpRequest via scoped helper',
      'upload_endpoint_changed':False,
      'formdata_changed':False,
      'file_field_changed':False,
      'real_progress_formula':'loaded / total * 100',
      'guards':guards,
      'bundle_sha256':hashlib.sha256(new_bundle.encode()).hexdigest(),
      'css_sha256':hashlib.sha256(new_css.encode()).hexdigest(),
      'index_sha256':hashlib.sha256(new_index.encode()).hexdigest(),
      'visual_qa_required':True,
      'functional_qa_required':True,
      'final_submit_required_to_observe_real_upload_progress':True,
      'git_mutations_by_runner':False,
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
