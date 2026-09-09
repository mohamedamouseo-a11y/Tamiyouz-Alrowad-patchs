#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

PATCH_ID = "JOIN_US_REFERENCE_EXACT_V3_8"
PATCH_MARKER = "TAM_JOIN_US_REFERENCE_EXACT_V3"
HOTFIX_MARKER = "TAM_JOIN_US_V3_8_MEDIA_FALLBACK"
V1_MARKER = "TAM_JOIN_US_LUXURY_V1"
V2_MARKER = "TAM_JOIN_US_LUXURY_V2_FIDELITY"

BASE_V3_RAW_SHA256 = "c7fe45099e2c8d8285de8c9848024c8c3e6428ae857276bb74d6c94fb0c18687"
BASE_V3_GIT_BLOB_SHA1 = "49e7a98a5e8402073724948a00825cf0da8d3165"

TEAM_1 = "https://tamiyouzalrowad.com/wp-content/uploads/2019/07/14-thegem-person.jpg.webp"
TEAM_2 = "https://tamiyouzalrowad.com/wp-content/uploads/2023/12/17-thegem-person.jpg"
TEAM_3 = "https://tamiyouzalrowad.com/wp-content/uploads/2024/04/%D8%B5%D9%88%D8%B1-09-thegem-person.jpg"

BASE_MAIN_MARKER = "<!-- TAM_JOIN_US_REFERENCE_EXACT_V3 -->"
LEGACY_MAIN_RE = re.compile(r'<main class="lux-page".*?</main>', re.S)
VIDEO_RE = re.compile(r'<video\b.*?</video>', re.S | re.I)

HERO_ASSET_CSS = "background-image:url('<?php echo esc_url(get_stylesheet_directory_uri() . \"/assets/join-us/reference-v3/hero-reference.webp\"); ?>');"
CULTURE_ASSET_CSS = "background-image:linear-gradient(90deg,transparent,rgba(6,18,30,.24)),url('<?php echo esc_url(get_stylesheet_directory_uri() . \"/assets/join-us/reference-v3/culture-reference.webp\"); ?>');"
CTA_ASSET_CSS = "background-image:url('<?php echo esc_url(get_stylesheet_directory_uri() . \"/assets/join-us/reference-v3/cta-reference.webp\"); ?>');"

EXTRA_CSS = r'''
/* TAM_JOIN_US_V3_8_MEDIA_FALLBACK */
.ref3-hero-visual{background-image:none!important;overflow:hidden}
.ref3-hero-visual video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;filter:saturate(.78) contrast(1.08) brightness(.82);transform:scale(1.03)}
.ref3-culture-photo{background-image:none!important;display:grid;grid-template-columns:repeat(3,1fr);overflow:hidden;padding:0;gap:0}
.ref3-culture-photo img{width:100%;height:100%;min-height:355px;object-fit:cover;object-position:center top;display:block;filter:saturate(.76) contrast(1.06) brightness(.86);transition:transform .6s ease,filter .5s ease}
.ref3-culture-photo img:nth-child(2){transform:translateY(18px) scale(1.03)}
.ref3-culture-photo:hover img{filter:saturate(.92) contrast(1.06) brightness(.92);transform:scale(1.05)}
.ref3-culture-photo:hover img:nth-child(2){transform:translateY(18px) scale(1.07)}
.ref3-final-bg{background-image:none!important;background:
 radial-gradient(540px 120px at 50% 110%,rgba(231,179,58,.28),transparent 72%),
 linear-gradient(180deg,rgba(13,31,47,.20),rgba(4,14,23,.10)),
 linear-gradient(135deg,#102a40,#071521)!important;filter:none!important}
.ref3-final-bg::before{content:"";position:absolute;inset:auto 4% 0;height:66%;opacity:.30;background:
 linear-gradient(90deg,transparent 0 4%,#d7a839 4% 7%,transparent 7% 10%,#d7a839 10% 13%,transparent 13% 18%,#d7a839 18% 22%,transparent 22% 27%,#d7a839 27% 31%,transparent 31% 36%,#d7a839 36% 39%,transparent 39% 45%,#d7a839 45% 50%,transparent 50% 55%,#d7a839 55% 60%,transparent 60% 65%,#d7a839 65% 69%,transparent 69% 74%,#d7a839 74% 78%,transparent 78% 84%,#d7a839 84% 88%,transparent 88% 100%);clip-path:polygon(0 100%,0 72%,4% 72%,4% 46%,7% 46%,7% 66%,10% 66%,10% 34%,13% 34%,13% 74%,18% 74%,18% 52%,22% 52%,22% 78%,27% 78%,27% 40%,31% 40%,31% 67%,36% 67%,36% 22%,39% 22%,39% 72%,45% 72%,45% 50%,50% 50%,50% 76%,55% 76%,55% 43%,60% 43%,60% 69%,65% 69%,65% 28%,69% 28%,69% 72%,74% 72%,74% 48%,78% 48%,78% 74%,84% 74%,84% 39%,88% 39%,88% 70%,100% 70%,100% 100%)}
@media(max-width:620px){.ref3-culture-photo{grid-template-columns:1fr}.ref3-culture-photo img{min-height:220px}.ref3-culture-photo img:nth-child(2){transform:none}.ref3-culture-photo:hover img,.ref3-culture-photo:hover img:nth-child(2){transform:none}}
'''


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def load_base(base_script: Path):
    raw = base_script.read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    blob_sha = git_blob_sha1(raw)
    if raw_sha != BASE_V3_RAW_SHA256:
        raise SystemExit(f"Base V3 raw SHA256 mismatch: {raw_sha}")
    if blob_sha != BASE_V3_GIT_BLOB_SHA1:
        raise SystemExit(f"Base V3 git blob SHA1 mismatch: {blob_sha}")

    ns = {"__name__": "tamiyouz_v3_base_v38", "__file__": str(base_script)}
    exec(compile(raw.decode("utf-8"), str(base_script), "exec"), ns, ns)
    for required in ["transform", "MAIN", "CSS"]:
        if required not in ns:
            raise SystemExit(f"Base V3 symbol missing: {required}")
    if PATCH_MARKER in HOTFIX_MARKER:
        raise SystemExit("Hotfix marker must not contain base V3 marker substring")
    return ns, raw_sha, blob_sha


def analyze_source(source: str):
    matches = list(LEGACY_MAIN_RE.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one legacy lux-page main, found {len(matches)}")
    match = matches[0]
    old_main = match.group(0)
    outside = source[:match.start()] + source[match.end():]

    def counts(marker):
        return {
            "total": source.count(marker),
            "inside": old_main.count(marker),
            "outside": outside.count(marker),
        }

    v1 = counts(V1_MARKER)
    v2 = counts(V2_MARKER)
    for name, data in [("V1", v1), ("V2", v2)]:
        if data["total"] < 1:
            raise SystemExit(f"{name} marker missing")
        if data["outside"] > 1:
            raise SystemExit(f"Unsafe {name} outside marker count: {data['outside']}")

    videos = VIDEO_RE.findall(old_main)
    if len(videos) != 1:
        raise SystemExit(f"Expected exactly one live V2 hero video inside replaced main, found {len(videos)}")
    video = videos[0]
    if "<source" not in video and " src=" not in video:
        raise SystemExit("Live V2 hero video has no usable source")

    lineage = {
        "v1_total_before": v1["total"],
        "v1_inside_count": v1["inside"],
        "v1_outside_count": v1["outside"],
        "v2_total_before": v2["total"],
        "v2_inside_count": v2["inside"],
        "v2_outside_count": v2["outside"],
    }
    return lineage, video


def patch_runtime(ns, lineage, video):
    base_main = ns["MAIN"]
    if base_main.count(BASE_MAIN_MARKER) != 1:
        raise SystemExit("Original V3 MAIN marker count is not exactly 1")

    inject_v1 = lineage["v1_outside_count"] == 0 and lineage["v1_inside_count"] >= 1
    inject_v2 = lineage["v2_outside_count"] == 0 and lineage["v2_inside_count"] >= 1

    marker_lines = []
    if inject_v1:
        marker_lines.append(f"<!-- {V1_MARKER} -->")
    if inject_v2:
        marker_lines.append(f"<!-- {V2_MARKER} -->")
    marker_lines.append(BASE_MAIN_MARKER)
    marker_lines.append(f"<!-- {HOTFIX_MARKER} -->")
    base_main = base_main.replace(BASE_MAIN_MARKER, "\n  ".join(marker_lines), 1)

    hero_placeholder = '<div class="ref3-hero-visual" aria-hidden="true"></div>'
    if base_main.count(hero_placeholder) != 1:
        raise SystemExit("V3 hero placeholder mismatch")
    base_main = base_main.replace(
        hero_placeholder,
        '<div class="ref3-hero-visual" aria-hidden="true">' + video + '</div>',
        1,
    )

    culture_placeholder = '<div class="ref3-culture-photo ref3-reveal" role="img" aria-label="فريق تميز الرواد يعمل معًا"></div>'
    if base_main.count(culture_placeholder) != 1:
        raise SystemExit("V3 culture placeholder mismatch")
    culture_markup = (
        '<div class="ref3-culture-photo ref3-reveal" role="group" aria-label="فريق تميز الرواد يعمل معًا">'
        f'<img src="{TEAM_1}" alt="فريق تميز الرواد" loading="lazy">'
        f'<img src="{TEAM_2}" alt="فريق تميز الرواد" loading="lazy">'
        f'<img src="{TEAM_3}" alt="فريق تميز الرواد" loading="lazy">'
        '</div>'
    )
    base_main = base_main.replace(culture_placeholder, culture_markup, 1)
    ns["MAIN"] = base_main

    css = ns["CSS"]
    for label, old in [
        ("hero", HERO_ASSET_CSS),
        ("culture", CULTURE_ASSET_CSS),
        ("cta", CTA_ASSET_CSS),
    ]:
        if css.count(old) != 1:
            raise SystemExit(f"V3 {label} local asset CSS anchor mismatch: {css.count(old)}")
        css = css.replace(old, "background-image:none;", 1)

    if "</style>" not in css:
        raise SystemExit("V3 CSS closing style anchor missing")
    css = css.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    ns["CSS"] = css

    return {
        "v1_reinjected": inject_v1,
        "v2_reinjected": inject_v2,
        "v1_preserved_outside": lineage["v1_outside_count"] == 1,
        "v2_preserved_outside": lineage["v2_outside_count"] == 1,
        "hero_media_source": "preserved_live_v2_video",
        "culture_media_source": "existing_site_team_portraits",
        "cta_media_source": "css_cinematic_skyline",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-script", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--asset-dir")
    args = ap.parse_args()

    base_script = Path(args.base_script)
    source_path = Path(args.source)
    output_path = Path(args.output)

    ns, base_raw_sha, base_blob_sha = load_base(base_script)
    source = source_path.read_text(encoding="utf-8")
    lineage, video = analyze_source(source)
    actions = patch_runtime(ns, lineage, video)

    result, base_guards = ns["transform"](source)
    if not all(base_guards.values()):
        failed = [k for k, v in base_guards.items() if not v]
        raise SystemExit("Original V3 base guard failed: " + ", ".join(failed))

    final_counts = {
        "v1": result.count(V1_MARKER),
        "v2": result.count(V2_MARKER),
        "v3": result.count(PATCH_MARKER),
        "hotfix": result.count(HOTFIX_MARKER),
    }

    final_guards = {
        "v1_marker_once": final_counts["v1"] == 1,
        "v2_marker_once": final_counts["v2"] == 1,
        "v3_marker_once": final_counts["v3"] == 1,
        "hotfix_marker_once": final_counts["hotfix"] == 1,
        "force_template_preserved": "TAM_JOIN_US_WORDPRESS_FORCE_V1" in result,
        "careers_iframe_once": result.count('id="careersFrame"') == 1,
        "careers_preserved": "https://careers.tamiyouzplaform.com/" in result,
        "rakan_preserved": "https://careers.tamiyouzplaform.com/api/v1/rakan/chat" in result,
        "form_submission_preserved": "e.data.type === 'formSubmission'" in result,
        "notify_preserved": "fetch('/join-us/notify.php'" in result,
        "visible_h1_once": result.count('<h1 id="join-us-title">') == 1,
        "collection_schema": '"@type":"CollectionPage"' in result,
        "website_schema": '"@type":"WebSite"' in result,
        "organization_schema": '"@type":"Organization"' in result,
        "breadcrumb_schema": '"@type":"BreadcrumbList"' in result,
        "no_jobposting": ('"@type":"JobPosting"' not in result and '"@type": "JobPosting"' not in result),
        "reduced_motion": "prefers-reduced-motion:reduce" in result,
        "reference_sections": all(x in result for x in [
            "ref3-header", "ref3-hero", "ref3-application", "ref3-stats",
            "ref3-why", "ref3-roles", "ref3-testimonials", "ref3-final-cta", "ref3-footer",
        ]),
        "live_v2_video_preserved": video in result,
        "culture_team_1": TEAM_1 in result,
        "culture_team_2": TEAM_2 in result,
        "culture_team_3": TEAM_3 in result,
        "no_local_hero_asset_ref": "hero-reference.webp" not in result,
        "no_local_culture_asset_ref": "culture-reference.webp" not in result,
        "no_local_cta_asset_ref": "cta-reference.webp" not in result,
    }
    failed = [k for k, v in final_guards.items() if not v]
    if failed:
        raise SystemExit("V3.8 final guard failed: " + ", ".join(failed))

    output_path.write_text(result, encoding="utf-8")

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "hotfix_marker": HOTFIX_MARKER,
        "base_v3_raw_sha256": base_raw_sha,
        "base_v3_git_blob_sha1": base_blob_sha,
        "asset_mode": "no_local_reference_assets",
        "media_strategy": actions,
        "lineage_analysis": lineage,
        "lineage_actions": actions,
        "base_guards": base_guards,
        "final_guards": final_guards,
        "final_marker_counts": final_counts,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": ["themes/thegem-elementor/page-join-us.php"],
        "integrations_preserved": True,
        "seo_schema_preserved": True,
        "git_mutations_by_patch_runner": False,
    }
    if args.manifest:
        Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
