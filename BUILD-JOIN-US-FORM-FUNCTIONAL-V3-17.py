#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_FUNCTIONAL_V3_17"
PATCH_MARKER = "TAM_JOIN_US_V3_17_FORM_FUNCTIONAL"
STYLE_ID = "tamiyouz-join-us-v317-form-functional"
FALLBACK_CLASS = "ref3-apply-fallback"
CAREERS_URL = "https://careers.tamiyouzplaform.com/"

REQUIRED = [
    "TAM_JOIN_US_REFERENCE_EXACT_V3",
    "TAM_JOIN_US_V3_9_MEDIA_FALLBACK",
    "TAM_JOIN_US_V3_16_FORM_FUNCTIONAL",
    'id="careersFrame"',
    "ref3-form-shell",
    "ref3-form-mask",
    CAREERS_URL,
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
]

FALLBACK_HTML = f'''<div class="{FALLBACK_CLASS}" role="note">
  <div>
    <strong>أكمل طلبك بسهولة</strong>
    <span>املأ جميع الحقول المطلوبة داخل النموذج. وإذا واجهتك مشكلة في الانتقال بين الخطوات، افتح نموذج التقديم الكامل مباشرة.</span>
  </div>
  <a href="{CAREERS_URL}" target="_blank" rel="noopener">فتح نموذج التقديم الكامل</a>
</div>'''

OVERRIDE = r'''<style id="tamiyouz-join-us-v317-form-functional">
/* TAM_JOIN_US_V3_17_FORM_FUNCTIONAL */

/* V3.17: application completion first. No clipping, no shields, clear full-form fallback. */
.ref3-application{
  max-width:1660px!important;
  grid-template-columns:180px minmax(820px,1040px) 180px!important;
  gap:28px!important;
  align-items:start!important;
  padding-inline:24px!important;
}
.ref3-form-shell{
  width:100%!important;
  max-width:none!important;
  overflow:visible!important;
  isolation:auto!important;
}
.ref3-apply-fallback{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:18px;
  padding:16px 18px;
  background:linear-gradient(135deg,rgba(231,179,58,.14),rgba(10,29,45,.98));
  border-bottom:1px solid rgba(231,179,58,.28);
  color:#e9edf2;
}
.ref3-apply-fallback>div{display:flex;flex-direction:column;gap:4px;min-width:0}
.ref3-apply-fallback strong{color:#f4c84f;font-size:15px}
.ref3-apply-fallback span{color:#b8c2cc;font-size:11px;line-height:1.7}
.ref3-apply-fallback a{
  flex:0 0 auto;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-height:42px;
  padding:0 16px;
  border-radius:10px;
  text-decoration:none;
  font-size:12px;
  font-weight:800;
  color:#101010;
  background:linear-gradient(180deg,#f6cd5a,#dda52b);
  border:1px solid #f3cc66;
  box-shadow:0 9px 26px rgba(231,179,58,.20);
}
.ref3-form-mask{
  position:relative!important;
  width:100%!important;
  height:2600px!important;
  min-height:2600px!important;
  overflow:visible!important;
  background:#0b1b2b!important;
}
.ref3-form-mask iframe#careersFrame{
  display:block!important;
  position:relative!important;
  z-index:1!important;
  left:auto!important;
  right:auto!important;
  width:100%!important;
  max-width:100%!important;
  height:2600px!important;
  min-height:2600px!important;
  margin:0!important;
  transform:none!important;
  border:0!important;
  background:#0b1b2b!important;
  pointer-events:auto!important;
}

/* Disable every previous parent-page shield. */
.ref3-form-mask::after{content:none!important;display:none!important;pointer-events:none!important}
.ref3-iframe-widget-shield{display:none!important;pointer-events:none!important;width:0!important;height:0!important}

@media(max-width:1180px){
  .ref3-application{grid-template-columns:140px minmax(700px,860px) 140px!important;gap:18px!important}
}
@media(max-width:980px){
  .ref3-application{grid-template-columns:1fr!important;max-width:920px!important}
  .ref3-form-mask,.ref3-form-mask iframe#careersFrame{height:2700px!important;min-height:2700px!important}
}
@media(max-width:620px){
  .ref3-application{padding-inline:10px!important}
  .ref3-apply-fallback{flex-direction:column;align-items:stretch;text-align:center}
  .ref3-apply-fallback a{width:100%}
  .ref3-form-mask,.ref3-form-mask iframe#careersFrame{height:2900px!important;min-height:2900px!important}
}
</style>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest")
    args = ap.parse_args()

    source = Path(args.source).read_text(encoding="utf-8")
    for marker in REQUIRED:
        if marker not in source:
            raise SystemExit(f"Required live marker missing: {marker}")

    if PATCH_MARKER in source or STYLE_ID in source or FALLBACK_CLASS in source:
        raise SystemExit("V3.17 already present in source")
    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected exactly one careersFrame, found {source.count('id=\"careersFrame\"')}")
    if source.count('<div class="ref3-form-mask">') != 1:
        raise SystemExit("Expected exactly one ref3-form-mask opening tag")
    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    result = source.replace('<div class="ref3-form-mask">', FALLBACK_HTML + '\n      <div class="ref3-form-mask">', 1)
    result = result.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": result.count(PATCH_MARKER) == 1,
        "style_id_once": result.count(STYLE_ID) == 1,
        "fallback_once": result.count(FALLBACK_CLASS) == 1,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "direct_apply_link_once": result.count(f'href="{CAREERS_URL}" target="_blank" rel="noopener"') == 1,
        "natural_iframe_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "full_height": "height:2600px!important;" in OVERRIDE,
        "no_negative_margin": "margin:0!important;" in OVERRIDE,
        "no_transform": "transform:none!important;" in OVERRIDE,
        "pointer_interaction": "pointer-events:auto!important;" in OVERRIDE,
        "old_pseudo_shield_disabled": ".ref3-form-mask::after" in OVERRIDE and "content:none!important" in OVERRIDE,
        "real_shield_disabled": ".ref3-iframe-widget-shield" in OVERRIDE and "display:none!important" in OVERRIDE,
        "careers_preserved": CAREERS_URL in result,
        "rakan_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "v3_preserved": "TAM_JOIN_US_REFERENCE_EXACT_V3" in result,
        "v39_preserved": "TAM_JOIN_US_V3_9_MEDIA_FALLBACK" in result,
        "v316_preserved": "TAM_JOIN_US_V3_16_FORM_FUNCTIONAL" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
    }
    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.17 guard failed: " + ", ".join(failed))

    Path(args.output).write_text(result, encoding="utf-8")
    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "fallback_class": FALLBACK_CLASS,
        "strategy": "full_height_iframe_plus_guaranteed_direct_application_fallback",
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "guards": guards,
        "functional_qa_required": True,
        "visual_qa_required": True,
        "git_mutations_by_patch_runner": False,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
