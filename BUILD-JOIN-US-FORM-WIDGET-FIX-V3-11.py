#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_WIDGET_FIX_V3_11"
PATCH_MARKER = "TAM_JOIN_US_V3_11_FORM_WIDGET_FIX"
STYLE_ID = "tamiyouz-join-us-v311-form-widget-fix"

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

OVERRIDE = r'''<style id="tamiyouz-join-us-v311-form-widget-fix">
/* TAM_JOIN_US_V3_11_FORM_WIDGET_FIX */

/*
 V3.11 strategy:
 - The careers iframe is cross-origin, so its internal floating support widgets cannot
   be styled directly from the parent page.
 - Keep the form centered while widening the iframe viewport symmetrically beyond
   the visible mask. This pushes right-edge fixed widgets completely outside the
   visible crop without moving the centered form itself.
 - Increase the visible mask height so the first-step form is not cut off.
*/
.ref3-application{align-items:start!important}
.ref3-form-shell{
  overflow:hidden!important;
  isolation:isolate!important;
}
.ref3-form-mask{
  position:relative!important;
  height:1040px!important;
  min-height:1040px!important;
  overflow:hidden!important;
  background:#0b1b2b!important;
}
.ref3-form-mask iframe#careersFrame{
  display:block!important;
  position:relative!important;
  left:50%!important;
  width:calc(100% + 520px)!important;
  max-width:none!important;
  height:1600px!important;
  min-height:1600px!important;
  margin:-190px 0 0!important;
  transform:translateX(-50%)!important;
  border:0!important;
  background:#0b1b2b!important;
}

/* Keep the overscan centered and large enough to crop embedded right-edge widgets. */
@media(max-width:980px){
  .ref3-form-mask{
    height:1100px!important;
    min-height:1100px!important;
  }
  .ref3-form-mask iframe#careersFrame{
    width:calc(100% + 420px)!important;
    height:1700px!important;
    min-height:1700px!important;
    margin-top:-180px!important;
  }
}

@media(max-width:620px){
  .ref3-form-mask{
    height:1180px!important;
    min-height:1180px!important;
  }
  .ref3-form-mask iframe#careersFrame{
    width:calc(100% + 340px)!important;
    height:1800px!important;
    min-height:1800px!important;
    margin-top:-170px!important;
  }
}
</style>'''


def transform(source: str):
    for marker in REQUIRED:
        if marker not in source:
            raise SystemExit(f"Required live marker missing: {marker}")

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit("V3.11 patch already present")

    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected exactly one careersFrame, found {source.count('id=\"careersFrame\"')}")

    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    out = source.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": out.count(PATCH_MARKER) == 1,
        "style_id_once": out.count(STYLE_ID) == 1,
        "careers_iframe_once": out.count('id="careersFrame"') == 1,
        "form_shell_present": "ref3-form-shell" in out,
        "form_mask_present": "ref3-form-mask" in out,
        "desktop_height_override": "height:1040px!important" in out,
        "desktop_iframe_height": "height:1600px!important" in out,
        "desktop_overscan": "width:calc(100% + 520px)!important" in out,
        "iframe_centered": "transform:translateX(-50%)!important" in out,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in out,
        "rakan_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in out,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in out,
        "notify_preserved": "fetch('/join-us/notify.php'" in out,
        "v3_preserved": "TAM_JOIN_US_REFERENCE_EXACT_V3" in out,
        "v39_preserved": "TAM_JOIN_US_V3_9_MEDIA_FALLBACK" in out,
        "visible_h1_once": out.count('<h1 id="join-us-title">') == 1,
        "no_global_widget_hide": all(x not in OVERRIDE for x in [
            ".rakan-widget", ".whatsapp-widget", "#rakan", "#whatsapp",
            "display:none", "visibility:hidden", "opacity:0"
        ]),
    }

    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.11 guard failed: " + ", ".join(failed))

    return out, guards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest")
    args = ap.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)

    source = source_path.read_text(encoding="utf-8")
    result, guards = transform(source)
    output_path.write_text(result, encoding="utf-8")

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "strategy": "centered_iframe_overscan_plus_uncropped_height",
        "form_viewport_height_desktop": 1040,
        "iframe_height_desktop": 1600,
        "iframe_horizontal_overscan_desktop": 520,
        "embedded_widget_isolation": "cross_origin_right_edge_widgets_pushed_outside_visible_mask",
        "page_level_widgets_modified": False,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "guards": guards,
        "git_mutations_by_patch_runner": False,
    }

    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
