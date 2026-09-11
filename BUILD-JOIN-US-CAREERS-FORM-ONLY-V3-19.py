#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

PATCH_ID = "JOIN_US_CAREERS_FORM_ONLY_V3_19"
PATCH_MARKER = "TAM_JOIN_US_V3_19_CAREERS_FORM_ONLY"
STYLE_ID = "tamiyouz-join-us-v319-careers-form-only-cleanup"

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

OVERRIDE = r'''<style id="tamiyouz-join-us-v319-careers-form-only-cleanup">
/* TAM_JOIN_US_V3_19_CAREERS_FORM_ONLY */

/*
 V3.19 final cleanup.
 The Careers origin now renders ONLY the application form.
 Retire all parent-page iframe cropping/overscan/shield experiments by overriding
 them with one simple, natural, scrollable iframe viewport.
*/
.ref3-form-shell{
  width:100%!important;
  max-width:none!important;
  overflow:visible!important;
  isolation:auto!important;
}

.ref3-form-mask{
  position:relative!important;
  width:100%!important;
  height:1080px!important;
  min-height:1080px!important;
  max-height:none!important;
  overflow:hidden!important;
  background:#0b1b2b!important;
}

.ref3-form-mask iframe#careersFrame{
  display:block!important;
  position:relative!important;
  z-index:1!important;
  left:auto!important;
  right:auto!important;
  top:auto!important;
  bottom:auto!important;
  width:100%!important;
  max-width:100%!important;
  height:1080px!important;
  min-height:1080px!important;
  max-height:none!important;
  margin:0!important;
  padding:0!important;
  transform:none!important;
  border:0!important;
  pointer-events:auto!important;
  overflow:auto!important;
  background:#0b1b2b!important;
}

/* Permanently retire earlier visual workaround layers. */
.ref3-form-mask::after{
  content:none!important;
  display:none!important;
  pointer-events:none!important;
}
.ref3-iframe-widget-shield{
  display:none!important;
  pointer-events:none!important;
  width:0!important;
  height:0!important;
}

/* V3.17 direct-apply fallback is no longer needed because Careers itself is form-only. */
.ref3-apply-fallback{
  display:none!important;
}

@media(max-width:980px){
  .ref3-form-mask,
  .ref3-form-mask iframe#careersFrame{
    height:1180px!important;
    min-height:1180px!important;
  }
}

@media(max-width:620px){
  .ref3-form-mask,
  .ref3-form-mask iframe#careersFrame{
    height:1320px!important;
    min-height:1320px!important;
  }
}
</style>'''

IFRAME_RE = re.compile(r'<iframe\b(?=[^>]*\bid=["\']careersFrame["\'])[^>]*>', re.I | re.S)


def ensure_scrolling_yes(source: str):
    matches = list(IFRAME_RE.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one careersFrame opening tag, found {len(matches)}")
    old = matches[0].group(0)
    if re.search(r'\bscrolling\s*=\s*["\'][^"\']*["\']', old, re.I):
        new = re.sub(r'\bscrolling\s*=\s*["\'][^"\']*["\']', 'scrolling="yes"', old, count=1, flags=re.I)
    else:
        new = old[:-1] + ' scrolling="yes">'
    result = source[:matches[0].start()] + new + source[matches[0].end():]
    return result, new


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
        raise SystemExit("V3.19 already present in source")

    if source.count('id="careersFrame"') != 1:
        raise SystemExit(f"Expected exactly one careersFrame, found {source.count('id=\"careersFrame\"')}")

    if "</head>" not in source:
        raise SystemExit("Missing </head> anchor")

    result, iframe_tag = ensure_scrolling_yes(source)
    result = result.replace("</head>", OVERRIDE + "\n</head>", 1)

    guards = {
        "patch_marker_once": result.count(PATCH_MARKER) == 1,
        "style_id_once": result.count(STYLE_ID) == 1,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "iframe_scrolling_enabled": 'scrolling="yes"' in iframe_tag,
        "natural_iframe_width": "width:100%!important;" in OVERRIDE and "max-width:100%!important;" in OVERRIDE,
        "desktop_viewport_1080": "height:1080px!important;" in OVERRIDE,
        "no_transform": "transform:none!important;" in OVERRIDE,
        "no_offsets": "left:auto!important;" in OVERRIDE and "right:auto!important;" in OVERRIDE,
        "iframe_interactive": "pointer-events:auto!important;" in OVERRIDE,
        "old_pseudo_shield_disabled": ".ref3-form-mask::after" in OVERRIDE and "content:none!important;" in OVERRIDE,
        "real_shield_disabled": ".ref3-iframe-widget-shield" in OVERRIDE and "display:none!important;" in OVERRIDE,
        "fallback_hidden": ".ref3-apply-fallback" in OVERRIDE and "display:none!important;" in OVERRIDE,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_endpoint_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "v3_preserved": "TAM_JOIN_US_REFERENCE_EXACT_V3" in result,
        "v39_preserved": "TAM_JOIN_US_V3_9_MEDIA_FALLBACK" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
    }

    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit("V3.19 guard failed: " + ", ".join(failed))

    Path(args.output).write_text(result, encoding="utf-8")

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "style_id": STYLE_ID,
        "strategy": "final_natural_iframe_after_careers_origin_form_only_cleanup",
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "guards": guards,
        "visual_qa_required": True,
        "functional_qa_required": True,
        "git_mutations_by_patch_runner": False,
    }

    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
