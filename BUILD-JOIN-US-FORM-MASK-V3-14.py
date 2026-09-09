#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_MASK_V3_14"
PATCH_MARKER = "TAM_JOIN_US_V3_14_FORM_MASK"
STYLE_ID = "tamiyouz-join-us-v314-form-mask"

REQUIRED = [
    "TAM_JOIN_US_REFERENCE_EXACT_V3",
    "TAM_JOIN_US_V3_9_MEDIA_FALLBACK",
    "TAM_JOIN_US_V3_13_FORM_RECOVERY",
    'id="careersFrame"',
    "ref3-form-shell",
    "ref3-form-mask",
    "https://careers.tamiyouzplaform.com/",
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
]

OVERRIDE = r'''<style id="tamiyouz-join-us-v314-form-mask">
/* TAM_JOIN_US_V3_14_FORM_MASK */

/*
 V3.14 visual recovery:
 - Keep iframe at its natural 100% width (no overscan, no scaling tricks).
 - Increase the visible form viewport so the application flow is not vertically cropped.
 - Because the Careers iframe is cross-origin, its internal Rakan/WhatsApp DOM cannot
   be styled safely from the parent page. Instead, mask ONLY the narrow right-edge
   support-widget lane INSIDE the form viewport. This does not touch page-level widgets.
*/
.ref3-application{
  max-width:1540px!important;
  grid-template-columns:190px minmax(780px,920px) 190px!important;
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
  height:1780px!important;
  min-height:1780px!important;
  overflow:hidden!important;
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
  height:3300px!important;
  min-height:3300px!important;
  margin:-105px 0 0!important;
  transform:none!important;
  border:0!important;
  background:#0b1b2b!important;
}

/* Local cross-origin widget shield: ONLY inside the iframe viewport. */
.ref3-form-mask::after{
  content:"";
  position:absolute;
  z-index:40;
  top:32%;
  right:0;
  bottom:0;
  width:82px;
  background:#0b1b2b;
  box-shadow:-16px 0 28px rgba(11,27,43,.94);
  pointer-events:auto;
}

@media(max-width:1180px){
  .ref3-application{
    grid-template-columns:140px minmax(690px,820px) 140px!important;
    gap:18px!important;
  }
}
@media(max-width:980px){
  .ref3-application{grid-template-columns:1fr!important;max-width:860px!important}
  .ref3-form-mask{height:1850px!important;min-height:1850px!important}
  .ref3-form-mask iframe#careersFrame{
    width:100%!important;
    max-width:100%!important;
    height:3450px!important;
    min-height:3450px!important;
    margin-top:-95px!important;
    transform:none!important;
  }
  .ref3-form-mask::after{width:72px;top:34%}
}
@media(max-width:620px){
  .ref3-application{padding-inline:10px!important}
  .ref3-form-mask{height:1980px!important;min-height:1980px!important}
  .ref3-form-mask iframe#careersFrame{
    left:auto!important;
    right:auto!important;
    width:100%!important;
    max-width:100%!important;
    height:3600px!important;
    min-height:3600px!important;
    margin:-85px 0 0!important;
    transform:none!important;
  }
  .ref3-form-mask::after{width:58px;top:36%;box-shadow:-10px 0 20px rgba(11,27,43,.94)}
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
        raise SystemExit("V3.14 already present in source")
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
        "v313_preserved": "TAM_JOIN_US_V3_13_FORM_RECOVERY" in result,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_endpoint_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
        "wide_form_column": "minmax(780px,920px)" in OVERRIDE,
        "natural_iframe_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "overscan_cancelled": "transform:none!important;" in OVERRIDE and "left:auto!important;" in OVERRIDE,
        "desktop_mask_height": "height:1780px!important;" in OVERRIDE,
        "desktop_iframe_height": "height:3300px!important;" in OVERRIDE,
        "local_widget_shield": ".ref3-form-mask::after" in OVERRIDE and "width:82px;" in OVERRIDE,
        "shield_blocks_clicks": "pointer-events:auto;" in OVERRIDE,
        "no_global_widget_hide": all(x not in OVERRIDE for x in [".rakan", ".whatsapp", "display:none", "visibility:hidden"]),
    }
    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.14 guard failed: " + ", ".join(failed))

    Path(args.output).write_text(result, encoding="utf-8")
    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "strategy": "natural_width_plus_tall_viewport_plus_local_right_edge_widget_shield",
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
