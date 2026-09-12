#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID = "JOIN_US_INLINE_LOGO_VISUAL_FIT_V3_27"
PATCH_MARKER = "TAM_JOIN_US_V3_27_INLINE_LOGO_VISUAL_FIT"
STYLE_ID = "tamiyouz-join-us-v327-inline-logo-visual-fit"

STYLE = r'''<style id="tamiyouz-join-us-v327-inline-logo-visual-fit">
/* TAM_JOIN_US_V3_27_INLINE_LOGO_VISUAL_FIT */
/* Source WebP is 300x300 but actual mark occupies only the narrow center area.
   Zoom/crop the transparent canvas visually without changing the embedded image. */
header img[src^="data:image/webp;base64,"],
.site-header img[src^="data:image/webp;base64,"],
.lux-header img[src^="data:image/webp;base64,"]{
  width:64px!important;
  height:64px!important;
  max-width:none!important;
  object-fit:contain!important;
  clip-path:inset(19% 36% 19% 36%)!important;
  transform:scale(1.55)!important;
  transform-origin:center center!important;
  display:block!important;
}
footer img[src^="data:image/webp;base64,"],
.site-footer img[src^="data:image/webp;base64,"],
.lux-footer img[src^="data:image/webp;base64,"]{
  width:70px!important;
  height:70px!important;
  max-width:none!important;
  object-fit:contain!important;
  clip-path:inset(19% 36% 19% 36%)!important;
  transform:scale(1.5)!important;
  transform-origin:center center!important;
  display:block!important;
}
</style>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--manifest')
    a = ap.parse_args()

    source = Path(a.source).read_text(encoding='utf-8')

    required = [
        'TAM_JOIN_US_V3_26_INLINE_LOGO',
        'data:image/webp;base64,',
        'alt="تميز الرواد"',
        'id="careersFrame"',
        "e.data.type === 'formSubmission'",
        "fetch('/join-us/notify.php'",
        '</head>'
    ]
    for token in required:
        if token not in source:
            raise SystemExit(f'Missing required baseline token: {token}')

    if source.count('data:image/webp;base64,') < 2:
        raise SystemExit('Expected at least two inline WebP logo references')

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit('V3.27 already present')

    result = source.replace('</head>', STYLE + '\n</head>', 1)

    guards = {
        'patch_marker_once': result.count(PATCH_MARKER) == 1,
        'style_id_once': result.count(STYLE_ID) == 1,
        'v326_preserved': 'TAM_JOIN_US_V3_26_INLINE_LOGO' in result,
        'inline_logo_preserved': result.count('data:image/webp;base64,') >= 2,
        'header_zoom_rule_present': 'transform:scale(1.55)!important;' in result,
        'footer_zoom_rule_present': 'transform:scale(1.5)!important;' in result,
        'transparent_canvas_crop_present': 'clip-path:inset(19% 36% 19% 36%)!important;' in result,
        'form_iframe_preserved': 'id="careersFrame"' in result,
        'form_submission_preserved': "e.data.type === 'formSubmission'" in result,
        'notify_hook_preserved': "fetch('/join-us/notify.php'" in result,
    }
    failed = [k for k, v in guards.items() if not v]
    if failed:
        raise SystemExit('Guard failed: ' + ', '.join(failed))

    Path(a.output).write_text(result, encoding='utf-8')

    manifest = {
        'patch': PATCH_ID,
        'patch_marker': PATCH_MARKER,
        'style_id': STYLE_ID,
        'strategy': 'visually_crop_and_zoom_transparent_inline_logo_canvas_only',
        'source_natural_size': '300x300',
        'source_visible_bbox_observed': 'x116..184 y64..236',
        'header_scale': 1.55,
        'footer_scale': 1.5,
        'image_source_changed': False,
        'form_logic_changed': False,
        'section_layout_changed': False,
        'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'output_sha256': hashlib.sha256(result.encode()).hexdigest(),
        'guards': guards,
        'visual_qa_required': True,
        'git_mutations_by_runner': False,
    }
    if a.manifest:
        Path(a.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
