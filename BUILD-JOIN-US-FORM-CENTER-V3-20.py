#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_CENTER_V3_20"
PATCH_MARKER = "TAM_JOIN_US_V3_20_FORM_CENTER"
STYLE_ID = "tamiyouz-join-us-v320-form-center"

REQUIRED = [
    "TAM_JOIN_US_REFERENCE_EXACT_V3",
    "TAM_JOIN_US_V3_9_MEDIA_FALLBACK",
    "TAM_JOIN_US_V3_19_CAREERS_FORM_ONLY",
    'id="careersFrame"',
    "ref3-form-shell",
    "ref3-form-mask",
    "https://careers.tamiyouzplaform.com/",
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
]

OVERRIDE = r'''<style id="tamiyouz-join-us-v320-form-center">
/* TAM_JOIN_US_V3_20_FORM_CENTER */

/*
 V3.20 scope: CENTERING ONLY.
 The Careers origin already renders the form only.
 Keep the existing V3.19 height and functionality untouched; center the embedded
 Careers viewport horizontally inside the large application card.
*/
.ref3-form-shell{
  width:100%!important;
  max-width:none!important;
}

.ref3-form-mask{
  width:100%!important;
  display:flex!important;
  justify-content:center!important;
  align-items:flex-start!important;
}

.ref3-form-mask iframe#careersFrame{
  display:block!important;
  flex:0 1 760px!important;
  width:min(760px, 100%)!important;
  max-width:760px!important;
  margin-left:auto!important;
  margin-right:auto!important;
  transform:none!important;
  left:auto!important;
  right:auto!important;
  pointer-events:auto!important;
}

@media(max-width:820px){
  .ref3-form-mask iframe#careersFrame{
    flex-basis:100%!important;
    width:100%!important;
    max-width:100%!important;
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
        raise SystemExit("V3.20 already present in source")

    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected exactly one careersFrame, found {source.count('id=\"careersFrame\"')}")

    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    result = source.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": result.count(PATCH_MARKER) == 1,
        "style_id_once": result.count(STYLE_ID) == 1,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "v319_preserved": "TAM_JOIN_US_V3_19_CAREERS_FORM_ONLY" in result,
        "mask_is_flex": "display:flex!important;" in OVERRIDE,
        "horizontal_centering_enabled": "justify-content:center!important;" in OVERRIDE,
        "iframe_desktop_width_760": "width:min(760px, 100%)!important;" in OVERRIDE,
        "iframe_max_width_760": "max-width:760px!important;" in OVERRIDE,
        "iframe_auto_margins": "margin-left:auto!important;" in OVERRIDE and "margin-right:auto!important;" in OVERRIDE,
        "no_transform": "transform:none!important;" in OVERRIDE,
        "no_offsets": "left:auto!important;" in OVERRIDE and "right:auto!important;" in OVERRIDE,
        "iframe_interactive": "pointer-events:auto!important;" in OVERRIDE,
        "mobile_full_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_endpoint_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
    }

    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.20 guard failed: " + ", ".join(failed))

    Path(args.output).write_text(result, encoding="utf-8")

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "strategy": "center_natural_careers_iframe_inside_existing_application_card",
        "desktop_iframe_width": "760px",
        "height_changed": False,
        "form_logic_changed": False,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "guards": guards,
        "visual_qa_required": True,
        "functional_qa_required": False,
        "git_mutations_by_patch_runner": False,
    }

    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
