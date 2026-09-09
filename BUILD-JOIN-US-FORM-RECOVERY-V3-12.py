#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_RECOVERY_V3_12"
PATCH_MARKER = "TAM_JOIN_US_V3_12_FORM_RECOVERY"
STYLE_ID = "tamiyouz-join-us-v312-form-recovery"

REQUIRED = [
    "TAM_JOIN_US_REFERENCE_EXACT_V3",
    "TAM_JOIN_US_V3_9_MEDIA_FALLBACK",
    "TAM_JOIN_US_V3_11_FORM_WIDGET_FIX",
    'id="careersFrame"',
    "ref3-form-shell",
    "ref3-form-mask",
    "https://careers.tamiyouzplaform.com/",
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
]

OVERRIDE = r'''<style id="tamiyouz-join-us-v312-form-recovery">
/* TAM_JOIN_US_V3_12_FORM_RECOVERY */

/*
 V3.12 recovery:
 - Cancel V3.11 horizontal overscan completely.
 - Restore the iframe to its natural 100% width so the application form keeps its
   intended responsive scale and readable field widths.
 - Make the iframe itself much taller than the visible form window. Embedded
   bottom-fixed support widgets then sit below the visible crop instead of over
   the active form area.
 - Keep page-level support widgets untouched.
*/
.ref3-application{
  align-items:start!important;
  grid-template-columns:190px minmax(520px,620px) 190px!important;
}
.ref3-form-shell{
  width:100%!important;
  overflow:hidden!important;
  isolation:isolate!important;
}
.ref3-form-mask{
  position:relative!important;
  width:100%!important;
  height:1450px!important;
  min-height:1450px!important;
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
  margin:-170px 0 0!important;
  transform:none!important;
  border:0!important;
  background:#0b1b2b!important;
}

@media(max-width:1180px){
  .ref3-application{grid-template-columns:150px minmax(500px,600px) 150px!important}
}

@media(max-width:980px){
  .ref3-application{grid-template-columns:1fr!important;max-width:690px!important}
  .ref3-form-mask{height:1500px!important;min-height:1500px!important}
  .ref3-form-mask iframe#careersFrame{
    width:100%!important;
    max-width:100%!important;
    height:2750px!important;
    min-height:2750px!important;
    margin-top:-160px!important;
    transform:none!important;
  }
}

@media(max-width:620px){
  .ref3-application{padding-inline:12px!important}
  .ref3-form-mask{height:1600px!important;min-height:1600px!important}
  .ref3-form-mask iframe#careersFrame{
    left:auto!important;
    width:100%!important;
    max-width:100%!important;
    height:2900px!important;
    min-height:2900px!important;
    margin:-145px 0 0!important;
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

    source_path = Path(args.source)
    output_path = Path(args.output)
    source = source_path.read_text(encoding="utf-8")

    for marker in REQUIRED:
        if marker not in source:
            raise SystemExit(f"Required live marker missing: {marker}")

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit("V3.12 already present in source")

    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected exactly one careersFrame, found {source.count('id=\"careersFrame\"')}")
    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    result = source.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": result.count(PATCH_MARKER) == 1,
        "style_id_once": result.count(STYLE_ID) == 1,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "v3_preserved": "TAM_JOIN_US_REFERENCE_EXACT_V3" in result,
        "v39_preserved": "TAM_JOIN_US_V3_9_MEDIA_FALLBACK" in result,
        "v311_preserved": "TAM_JOIN_US_V3_11_FORM_WIDGET_FIX" in result,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
        "natural_iframe_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "overscan_cancelled": "transform:none!important;" in OVERRIDE and "left:auto!important;" in OVERRIDE,
        "desktop_mask_height": "height:1450px!important;" in OVERRIDE,
        "desktop_iframe_height": "height:2600px!important;" in OVERRIDE,
        "no_global_widget_hide": all(x not in OVERRIDE for x in [".rakan", ".whatsapp", "display:none", "visibility:hidden"]),
    }

    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.12 guard failed: " + ", ".join(failed))

    output_path.write_text(result, encoding="utf-8")

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "strategy": "natural_width_plus_tall_iframe_bottom_widget_isolation",
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
