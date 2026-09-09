#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

PATCH_ID = "JOIN_US_FORM_SHIELD_V3_15"
PATCH_MARKER = "TAM_JOIN_US_V3_15_FORM_SHIELD"
STYLE_ID = "tamiyouz-join-us-v315-form-shield"
SHIELD_CLASS = "ref3-iframe-widget-shield"

REQUIRED = [
    "TAM_JOIN_US_REFERENCE_EXACT_V3",
    "TAM_JOIN_US_V3_9_MEDIA_FALLBACK",
    "TAM_JOIN_US_V3_13_FORM_RECOVERY",
    "TAM_JOIN_US_V3_14_FORM_MASK",
    'id="careersFrame"',
    "ref3-form-shell",
    "ref3-form-mask",
    "https://careers.tamiyouzplaform.com/",
    "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
    "fetch('/join-us/notify.php'",
    "e.data.type === 'formSubmission'",
]

OVERRIDE = r'''<style id="tamiyouz-join-us-v315-form-shield">
/* TAM_JOIN_US_V3_15_FORM_SHIELD */

/* V3.15: real DOM shield + materially taller visible form viewport. */
.ref3-application{
  max-width:1660px!important;
  grid-template-columns:180px minmax(860px,1040px) 180px!important;
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
  height:2600px!important;
  min-height:2600px!important;
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
  height:4600px!important;
  min-height:4600px!important;
  margin:-80px 0 0!important;
  transform:none!important;
  border:0!important;
  background:#0b1b2b!important;
}

/* Neutralize the older V3.14 pseudo shield; use a real DOM element instead. */
.ref3-form-mask::after{
  content:none!important;
  width:0!important;
  pointer-events:none!important;
}

/* Cross-origin internal widget shield. Lives ONLY inside the form iframe viewport. */
.ref3-iframe-widget-shield{
  position:absolute!important;
  z-index:2147483000!important;
  top:0!important;
  right:0!important;
  bottom:0!important;
  width:132px!important;
  display:block!important;
  background:#0b1b2b!important;
  box-shadow:-18px 0 32px rgba(11,27,43,.96)!important;
  pointer-events:auto!important;
  user-select:none!important;
}

@media(max-width:1180px){
  .ref3-application{
    grid-template-columns:120px minmax(760px,900px) 120px!important;
    gap:18px!important;
  }
  .ref3-iframe-widget-shield{width:118px!important}
}
@media(max-width:980px){
  .ref3-application{grid-template-columns:1fr!important;max-width:940px!important}
  .ref3-form-mask{height:2750px!important;min-height:2750px!important}
  .ref3-form-mask iframe#careersFrame{
    width:100%!important;
    max-width:100%!important;
    height:4800px!important;
    min-height:4800px!important;
    margin-top:-70px!important;
    transform:none!important;
  }
  .ref3-iframe-widget-shield{width:96px!important}
}
@media(max-width:620px){
  .ref3-application{padding-inline:8px!important}
  .ref3-form-mask{height:3000px!important;min-height:3000px!important}
  .ref3-form-mask iframe#careersFrame{
    left:auto!important;
    right:auto!important;
    width:100%!important;
    max-width:100%!important;
    height:5100px!important;
    min-height:5100px!important;
    margin:-60px 0 0!important;
    transform:none!important;
  }
  .ref3-iframe-widget-shield{
    width:64px!important;
    box-shadow:-10px 0 20px rgba(11,27,43,.96)!important;
  }
}
</style>'''

IFRAME_RE = re.compile(r'(<iframe\b[^>]*\bid="careersFrame"[^>]*>.*?</iframe>)', re.S | re.I)


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

    if PATCH_MARKER in source or STYLE_ID in source or SHIELD_CLASS in source:
        raise SystemExit("V3.15 already present in source")
    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected one careersFrame, found {source.count('id=\"careersFrame\"')}")
    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    matches = list(IFRAME_RE.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one complete careers iframe element, found {len(matches)}")

    shield = '<div class="ref3-iframe-widget-shield" aria-hidden="true"></div>'
    result = IFRAME_RE.sub(lambda m: m.group(1) + shield, source, count=1)
    result = result.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": result.count(PATCH_MARKER) == 1,
        "style_id_once": result.count(STYLE_ID) == 1,
        "shield_element_once": result.count(f'class="{SHIELD_CLASS}"') == 1,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "v3_preserved": "TAM_JOIN_US_REFERENCE_EXACT_V3" in result,
        "v39_preserved": "TAM_JOIN_US_V3_9_MEDIA_FALLBACK" in result,
        "v313_preserved": "TAM_JOIN_US_V3_13_FORM_RECOVERY" in result,
        "v314_preserved": "TAM_JOIN_US_V3_14_FORM_MASK" in result,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_endpoint_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
        "wide_form_column": "minmax(860px,1040px)" in OVERRIDE,
        "natural_iframe_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "overscan_cancelled": "transform:none!important;" in OVERRIDE and "left:auto!important;" in OVERRIDE,
        "desktop_mask_height": "height:2600px!important;" in OVERRIDE,
        "desktop_iframe_height": "height:4600px!important;" in OVERRIDE,
        "old_pseudo_shield_neutralized": "content:none!important;" in OVERRIDE,
        "real_widget_shield": ".ref3-iframe-widget-shield" in OVERRIDE and "width:132px!important;" in OVERRIDE,
        "shield_blocks_clicks": "pointer-events:auto!important;" in OVERRIDE,
        "shield_high_z": "z-index:2147483000!important;" in OVERRIDE,
        "no_global_widget_hide": all(x not in OVERRIDE for x in [".rakan", ".whatsapp", "visibility:hidden"]),
    }

    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.15 guard failed: " + ", ".join(failed))

    Path(args.output).write_text(result, encoding="utf-8")
    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "shield_class": SHIELD_CLASS,
        "strategy": "real_dom_right_gutter_shield_plus_extended_form_viewport",
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
