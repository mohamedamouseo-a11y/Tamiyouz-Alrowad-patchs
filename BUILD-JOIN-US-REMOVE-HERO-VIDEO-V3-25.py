#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PATCH_ID = "JOIN_US_REMOVE_HERO_VIDEO_V3_25"
PATCH_MARKER = "TAM_JOIN_US_V3_25_REMOVE_HERO_VIDEO"
STYLE_ID = "tamiyouz-join-us-v325-remove-hero-video"

STYLE = r'''<style id="tamiyouz-join-us-v325-remove-hero-video">
/* TAM_JOIN_US_V3_25_REMOVE_HERO_VIDEO */
.lux-hero-media{
  background:#070f18!important;
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
        'class="lux-hero-media"',
        '/assets/join-us/video-header.mp4?v=6',
        'id="join-us-title"',
        'id="careersFrame"',
        "e.data.type === 'formSubmission'",
        "fetch('/join-us/notify.php'",
        '</head>'
    ]
    for token in required:
        if token not in source:
            raise SystemExit(f'Missing required baseline token: {token}')

    if PATCH_MARKER in source or STYLE_ID in source:
        raise SystemExit('V3.25 already present')

    # Remove only the hero <video> element; keep the media container and overlays intact.
    hero_start = source.find('<div class="lux-hero-media"')
    if hero_start < 0:
        raise SystemExit('Hero media container not found')
    hero_end = source.find('</div>', hero_start)
    if hero_end < 0:
        raise SystemExit('Hero media container end not found')

    hero_chunk = source[hero_start:hero_end + 6]
    videos = re.findall(r'<video\b[^>]*>.*?</video>', hero_chunk, flags=re.S | re.I)
    if len(videos) != 1:
        raise SystemExit(f'Expected exactly one hero video, found {len(videos)}')

    new_hero_chunk = re.sub(r'\s*<video\b[^>]*>.*?</video>\s*', '\n', hero_chunk, count=1, flags=re.S | re.I)
    result = source[:hero_start] + new_hero_chunk + source[hero_end + 6:]
    result = result.replace('</head>', STYLE + '\n</head>', 1)

    guards = {
        'patch_marker_once': result.count(PATCH_MARKER) == 1,
        'style_id_once': result.count(STYLE_ID) == 1,
        'hero_media_preserved': 'class="lux-hero-media"' in result,
        'hero_video_removed': '/assets/join-us/video-header.mp4?v=6' not in result,
        'no_video_tag_in_hero': '<video' not in new_hero_chunk.lower(),
        'hero_title_preserved': 'id="join-us-title"' in result,
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
        'strategy': 'remove_hero_video_element_only_keep_media_container_and_page_layout',
        'hero_video_removed': True,
        'hero_media_container_preserved': True,
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
