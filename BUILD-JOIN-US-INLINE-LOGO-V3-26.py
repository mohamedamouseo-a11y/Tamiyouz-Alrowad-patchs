#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

PATCH_ID = "JOIN_US_INLINE_LOGO_V3_26"
PATCH_MARKER = "TAM_JOIN_US_V3_26_INLINE_LOGO"
STYLE_ID = "tamiyouz-join-us-v326-inline-logo"
LOGO_SHA256 = "125076399fb8a764796fc60ee99979343e924f9fd83f569fb6abfb12d417d9d7"
LOGO_MIME = "image/webp"
DATA_URI = "data:image/webp;base64,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"

STYLE = r"""<style id="tamiyouz-join-us-v326-inline-logo">
/* TAM_JOIN_US_V3_26_INLINE_LOGO */
.site-header img[src^="data:image/webp;base64,"],
.lux-header img[src^="data:image/webp;base64,"] {
  object-fit: contain !important;
}
.site-footer img[src^="data:image/webp;base64,"],
.lux-footer img[src^="data:image/webp;base64,"] {
  object-fit: contain !important;
}
</style>"""

def replace_first_img_src(region, label):
    m = re.search(r'<img\b[^>]*>', region, flags=re.I|re.S)
    if not m:
        raise SystemExit(f'No img tag found in {label}')
    tag = m.group(0)
    srcm = re.search(r'\bsrc\s*=\s*(["\']).*?\1', tag, flags=re.I|re.S)
    if not srcm:
        raise SystemExit(f'No src attribute found in {label} image')
    new_tag = tag[:srcm.start()] + 'src="' + DATA_URI + '"' + tag[srcm.end():]
    return region[:m.start()] + new_tag + region[m.end():], tag, new_tag

def slice_region(source, start_pattern, end_pattern, label):
    sm = re.search(start_pattern, source, flags=re.I|re.S)
    if not sm:
        raise SystemExit(f'{label} start not found')
    em = re.search(end_pattern, source[sm.start():], flags=re.I|re.S)
    if not em:
        raise SystemExit(f'{label} end not found')
    start = sm.start()
    end = sm.start() + em.end()
    return start, end, source[start:end]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--manifest')
    a = ap.parse_args()

    source = Path(a.source).read_text(encoding='utf-8')

    required = [
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
        raise SystemExit('V3.26 already present')

    hs, he, header = slice_region(source, r'<header\b[^>]*>', r'</header\s*>', 'header')
    new_header, old_header_img, new_header_img = replace_first_img_src(header, 'header')

    result = source[:hs] + new_header + source[he:]

    fs, fe, footer = slice_region(result, r'<footer\b[^>]*>', r'</footer\s*>', 'footer')
    new_footer, old_footer_img, new_footer_img = replace_first_img_src(footer, 'footer')
    result = result[:fs] + new_footer + result[fe:]

    result = result.replace('</head>', STYLE + '\n</head>', 1)

    guards = {
        'patch_marker_once': result.count(PATCH_MARKER) == 1,
        'style_id_once': result.count(STYLE_ID) == 1,
        'inline_logo_exactly_twice': result.count(DATA_URI) == 2,
        'header_inline_logo': DATA_URI in new_header,
        'footer_inline_logo': DATA_URI in new_footer,
        'hero_preserved': 'id="join-us-title"' in result,
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
        'strategy': 'embed_user_supplied_webp_as_data_uri_in_header_and_footer_logo_img_only',
        'logo_mime': LOGO_MIME,
        'logo_sha256': LOGO_SHA256,
        'logo_bytes': 4520,
        'inline_logo_count': result.count(DATA_URI),
        'header_logo_changed': True,
        'footer_logo_changed': True,
        'hero_changed': False,
        'form_logic_changed': False,
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
