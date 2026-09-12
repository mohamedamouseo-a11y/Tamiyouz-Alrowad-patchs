#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

PATCH_ID = "JOIN_US_HERO_VIDEO_FOCAL_CENTER_V3_22"
PATCH_MARKER = "TAM_JOIN_US_V3_22_HERO_VIDEO_FOCAL_CENTER"
STYLE_ID = "tamiyouz-join-us-v322-hero-video-focal-center"

STYLE = r'''<style id="tamiyouz-join-us-v322-hero-video-focal-center">
/* TAM_JOIN_US_V3_22_HERO_VIDEO_FOCAL_CENTER */
@media (min-width: 901px){
  .lux-hero-media video{
    object-position:68% 50%!important;
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
        'TAM_JOIN_US_V3_21_HERO_VIDEO_CENTER',
        'tamiyouz-join-us-v321-hero-video-center',
        'class="lux-hero-media"',
        '/assets/join-us/video-header.mp4?v=6',
        'object-position:center center!important;',
        'id="careersFrame"',
        "e.data.type === 'formSubmission'",
        "fetch('/join-us/notify.php'",
        '</head>'
    ]
    for token in required:
        if token not in source:
            raise SystemExit(f'Missing required baseline token: {token}')

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit('V3.22 already present')

    result = source.replace('</head>', STYLE + '\n</head>', 1)

    guards = {
        'patch_marker_once': result.count(PATCH_MARKER) == 1,
        'style_id_once': result.count(STYLE_ID) == 1,
        'v321_preserved': 'TAM_JOIN_US_V3_21_HERO_VIDEO_CENTER' in result,
        'hero_video_preserved': '/assets/join-us/video-header.mp4?v=6' in result,
        'desktop_focal_rule_present': 'object-position:68% 50%!important;' in result,
        'mobile_center_rule_preserved': result.count('object-position:center center!important;') >= 2,
        'form_iframe_preserved': 'id="careersFrame"' in result,
        'form_submission_preserved': "e.data.type === 'formSubmission'" in result,
        'notify_hook_preserved': "fetch('/join-us/notify.php'" in result,
    }
    failed = [k for k,v in guards.items() if not v]
    if failed:
        raise SystemExit('Guard failed: ' + ', '.join(failed))

    Path(a.output).write_text(result, encoding='utf-8')

    manifest = {
        'patch': PATCH_ID,
        'patch_marker': PATCH_MARKER,
        'style_id': STYLE_ID,
        'strategy': 'desktop_focal_point_shift_only_after_v321_video_center',
        'desktop_object_position': '68% 50%',
        'mobile_object_position': 'center center (preserved)',
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
