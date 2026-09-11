#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID = "JOIN_US_HERO_VIDEO_CENTER_V3_21"
PATCH_MARKER = "TAM_JOIN_US_V3_21_HERO_VIDEO_CENTER"
STYLE_ID = "tamiyouz-join-us-v321-hero-video-center"

STYLE = r'''<style id="tamiyouz-join-us-v321-hero-video-center">
/* TAM_JOIN_US_V3_21_HERO_VIDEO_CENTER */
@media (min-width: 901px){
  .lux-hero-media video{
    position:absolute!important;
    top:50%!important;
    left:50%!important;
    width:min(76vw,1200px)!important;
    height:100%!important;
    max-width:none!important;
    object-fit:cover!important;
    object-position:center center!important;
    transform:translate(-50%,-50%) scale(1.035)!important;
    transform-origin:center center!important;
  }
}
@media (max-width: 900px){
  .lux-hero-media video{
    position:absolute!important;
    top:50%!important;
    left:50%!important;
    width:100%!important;
    height:100%!important;
    max-width:none!important;
    object-fit:cover!important;
    object-position:center center!important;
    transform:translate(-50%,-50%) scale(1.035)!important;
    transform-origin:center center!important;
  }
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
        'TAM_JOIN_US_LUXURY_V1',
        'class="lux-hero-media"',
        '.lux-hero-media video{',
        '/assets/join-us/video-header.mp4?v=6',
        '</head>'
    ]
    for token in required:
        if token not in source:
            raise SystemExit(f'Missing required baseline token: {token}')

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit('V3.21 already present')

    result = source.replace('</head>', STYLE + '\n</head>', 1)

    guards = {
        'patch_marker_once': result.count(PATCH_MARKER) == 1,
        'style_id_once': result.count(STYLE_ID) == 1,
        'hero_video_preserved': '/assets/join-us/video-header.mp4?v=6' in result,
        'hero_markup_preserved': 'class="lux-hero-media"' in result,
        'desktop_center_rule_present': 'width:min(76vw,1200px)!important;' in result,
        'center_position_present': 'left:50%!important;' in result and 'translate(-50%,-50%)' in result,
        'object_position_center': 'object-position:center center!important;' in result,
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
        'strategy': 'center_existing_hero_video_window_only_keep_hero_content_and_form_unchanged',
        'desktop_video_width': 'min(76vw,1200px)',
        'desktop_video_center': '50%/50%',
        'mobile_video_width': '100%',
        'form_logic_changed': False,
        'hero_copy_changed': False,
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
