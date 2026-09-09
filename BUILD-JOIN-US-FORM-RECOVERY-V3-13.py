#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_RECOVERY_V3_13"
PATCH_MARKER = "TAM_JOIN_US_V3_13_FORM_RECOVERY"
STYLE_ID = "tamiyouz-join-us-v313-form-recovery"

REQUIRED = [
    "TAM_JOIN_US_REFERENCE_EXACT_V3",
    "TAM_JOIN_US_V3_9_MEDIA_FALLBACK",
    'id="careersFrame"',
    "ref3-form-shell",
    "ref3-form-mask",
    "https://careers.tamiyouzplaform.com/",
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
]

OVERRIDE = r'''<style id="tamiyouz-join-us-v313-form-recovery">
/* TAM_JOIN_US_V3_13_FORM_RECOVERY */

/* Actual live base recovery: V3.9 + deployed V3.10 visual override. */
.ref3-application{
  max-width:1480px!important;
  grid-template-columns:190px minmax(720px,880px) 190px!important;
  gap:28px!important;
  align-items:start!important;
  padding-inline:24px!important;
}
.ref3-form-shell{
  width:100%!important;
  max-width:none!important;
  overflow:hidden!important;
  isolation:isolate!important;
}
.ref3-form-mask{
  position:relative!important;
  width:100%!important;
  height:1320px!important;
  min-height:1320px!important;
  overflow:hidden!important;
  background:#0b1b2b!important;
}
.ref3-form-mask iframe#careersFrame{
  display:block!important;
  position:relative!important;
  left:auto!important;
  right:auto!important;
  width:100%!important;
  max-width:100%!important;
  height:2600px!important;
  min-height:2600px!important;
  margin:-120px 0 0!important;
  transform:none!important;
  border:0!important;
  background:#0b1b2b!important;
}

/* Intentionally no parent-page hiding rules for Rakan/WhatsApp. The tall iframe
   pushes bottom-fixed iframe widgets below the visible crop while preserving the form. */
@media(max-width:1180px){
  .ref3-application{
    grid-template-columns:140px minmax(650px,760px) 140px!important;
    gap:18px!important;
  }
}
@media(max-width:980px){
  .ref3-application{grid-template-columns:1fr!important;max-width:820px!important}
  .ref3-form-mask{height:1380px!important;min-height:1380px!important}
  .ref3-form-mask iframe#careersFrame{
    width:100%!important;
    max-width:100%!important;
    height:2750px!important;
    min-height:2750px!important;
    margin-top:-110px!important;
    transform:none!important;
  }
}
@media(max-width:620px){
  .ref3-application{padding-inline:10px!important}
  .ref3-form-mask{height:1500px!important;min-height:1500px!important}
  .ref3-form-mask iframe#careersFrame{
    left:auto!important;
    right:auto!important;
    width:100%!important;
    max-width:100%!important;
    height:2900px!important;
    min-height:2900px!important;
    margin:-95px 0 0!important;
    transform:none!important;
  }
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

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit("V3.13 already present in source")
    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected one careersFrame, found {source.count('id=\"careersFrame\"')}")
    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    result = source.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": result.count(PATCH_MARKER) == 1,
        "style_id_once": result.count(STYLE_ID) == 1,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "v3_preserved": "TAM_JOIN_US_REFERENCE_EXACT_V3" in result,
        "v39_preserved": "TAM_JOIN_US_V3_9_MEDIA_FALLBACK" in result,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_endpoint_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
        "wide_form_column": "minmax(720px,880px)" in OVERRIDE,
        "natural_iframe_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "overscan_cancelled": "transform:none!important;" in OVERRIDE and "left:auto!important;" in OVERRIDE,
        "desktop_mask_height": "height:1320px!important;" in OVERRIDE,
        "desktop_iframe_height": "height:2600px!important;" in OVERRIDE,
        "no_v311_dependency": "TAM_JOIN_US_V3_11_FORM_WIDGET_FIX" not in REQUIRED,
        "no_global_widget_hide": all(x not in OVERRIDE for x in [".rakan", ".whatsapp", "display:none", "visibility:hidden"]),
    }
    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.13 guard failed: " + ", ".join(failed))

    Path(args.output).write_text(result, encoding="utf-8")
    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "strategy": "wide_natural_iframe_plus_tall_bottom_widget_isolation",
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "guards": guards,
        "visual_qa_required": True,
        "git_mutations_by_patch_runner": False,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
