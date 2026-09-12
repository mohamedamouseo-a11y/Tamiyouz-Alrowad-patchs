#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID = "JOIN_US_HERO_VIDEO_SHIFT_LEFT_V3_24"
PATCH_MARKER = "TAM_JOIN_US_V3_24_HERO_VIDEO_SHIFT_LEFT"
STYLE_ID = "tamiyouz-join-us-v324-hero-video-shift-left"

STYLE = r'''<style id="tamiyouz-join-us-v324-hero-video-shift-left">
/* TAM_JOIN_US_V3_24_HERO_VIDEO_SHIFT_LEFT */
@media (min-width: 901px){
  .lux-hero-media video{
    left:30%!important;
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
        'TAM_JOIN_US_V3_23_HERO_VIDEO_FOCAL_CENTER',
        'tamiyouz-join-us-v323-hero-video-focal-center',
        'object-position:90% 50%!important;',
        'TAM_JOIN_US_V3_21_HERO_VIDEO_CENTER',
        'class="lux-hero-media"',
        '/assets/join-us/video-header.mp4?v=6',
        'id="careersFrame"',
        "e.data.type === 'formSubmission'",
        "fetch('/join-us/notify.php'",
        '</head>'
    ]
    for token in required:
        if token not in source:
            raise SystemExit(f'Missing required baseline token: {token}')

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit('V3.24 already present')

    result = source.replace('</head>', STYLE + '\n</head>', 1)

    guards = {
        'patch_marker_once': result.count(PATCH_MARKER) == 1,
        'style_id_once': result.count(STYLE_ID) == 1,
        'v323_preserved': 'TAM_JOIN_US_V3_23_HERO_VIDEO_FOCAL_CENTER' in result,
        'v321_preserved': 'TAM_JOIN_US_V3_21_HERO_VIDEO_CENTER' in result,
        'desktop_left_rule_once': result.count('left:30%!important;') == 1,
        'focal_90_preserved': 'object-position:90% 50%!important;' in result,
        'hero_video_preserved': '/assets/join-us/video-header.mp4?v=6' in result,
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
        'strategy': 'desktop_video_element_shift_left_only_after_v323_focal_tuning',
        'desktop_video_left_before': '50%',
        'desktop_video_left_after': '30%',
        'desktop_object_position': '90% 50% (preserved)',
        'mobile_position_changed': False,
        'video_size_changed': False,
        'hero_copy_changed': False,
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
