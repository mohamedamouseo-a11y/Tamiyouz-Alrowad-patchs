#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

PATCH_ID = "JOIN_US_REFERENCE_EXACT_V3_6"
PATCH_MARKER = "TAM_JOIN_US_REFERENCE_EXACT_V3"
HOTFIX_MARKER = "TAM_JOIN_US_V3_6_LINEAGE_HOTFIX"
V1_MARKER = "TAM_JOIN_US_LUXURY_V1"
V2_MARKER = "TAM_JOIN_US_LUXURY_V2_FIDELITY"

BASE_SCRIPT_RAW_SHA256 = "c7fe45099e2c8d8285de8c9848024c8c3e6428ae857276bb74d6c94fb0c18687"
BASE_SCRIPT_GIT_BLOB_SHA1 = "49e7a98a5e8402073724948a00825cf0da8d3165"

EXPECTED_ASSETS = {
    "hero-reference.webp": ("15b7ba9c9ba02a660e4d0bd157ed09ce4cbd0ecb76a12cf20e49e9e63675f514", 29968),
    "culture-reference.webp": ("117d9e92cd4cb2d358dfde74bdd2959b9fe6be2beefd8fbc5f6c5b160be51384", 17452),
    "cta-reference.webp": ("a55a907e0a2e91c32deae546068c2c7afdabd383ad7f7c265403ad154f18a2ee", 4832),
}

BASE_MAIN_MARKER = "<!-- TAM_JOIN_US_REFERENCE_EXACT_V3 -->"
LEGACY_MAIN_RE = re.compile(r'<main class="lux-page".*?</main>', re.S)


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def load_base(base_script: Path):
    raw = base_script.read_bytes()
    raw_digest = raw_sha256(raw)
    blob_digest = git_blob_sha1(raw)

    if raw_digest != BASE_SCRIPT_RAW_SHA256:
        raise SystemExit(
            f"Base V3 raw SHA256 mismatch: {raw_digest}; expected {BASE_SCRIPT_RAW_SHA256}"
        )
    if blob_digest != BASE_SCRIPT_GIT_BLOB_SHA1:
        raise SystemExit(
            f"Base V3 git blob SHA1 mismatch: {blob_digest}; expected {BASE_SCRIPT_GIT_BLOB_SHA1}"
        )

    ns = {
        "__name__": "tamiyouz_v3_base_hotfixed_v36",
        "__file__": str(base_script),
    }
    exec(compile(raw.decode("utf-8"), str(base_script), "exec"), ns, ns)

    for required in ["transform", "write_asset", "HERO_B64", "CULTURE_B64", "CTA_B64", "MAIN"]:
        if required not in ns:
            raise SystemExit(f"Base V3 symbol missing after load: {required}")

    if PATCH_MARKER in HOTFIX_MARKER:
        raise SystemExit("Hotfix marker must not contain the base V3 patch marker substring")

    return ns, raw_digest, blob_digest


def marker_location_counts(marker: str, old_main: str, outside: str):
    return {
        "total_before": old_main.count(marker) + outside.count(marker),
        "inside_count": old_main.count(marker),
        "outside_count": outside.count(marker),
    }


def analyze_source_lineage(source: str):
    matches = list(LEGACY_MAIN_RE.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one legacy lux-page main, found {len(matches)}")

    match = matches[0]
    old_main = match.group(0)
    outside = source[:match.start()] + source[match.end():]

    v1 = marker_location_counts(V1_MARKER, old_main, outside)
    v2 = marker_location_counts(V2_MARKER, old_main, outside)

    for name, data in [("V1", v1), ("V2", v2)]:
        if data["total_before"] < 1:
            raise SystemExit(f"{name} marker missing from live source")
        if data["outside_count"] > 1:
            raise SystemExit(
                f"{name} marker has {data['outside_count']} copies outside replaced main; "
                "cannot safely normalize preserved regions"
            )

    lineage = {
        "v1_inside_count": v1["inside_count"],
        "v1_outside_count": v1["outside_count"],
        "v2_inside_count": v2["inside_count"],
        "v2_outside_count": v2["outside_count"],
        "v1_inside_replaced_main": v1["inside_count"] > 0,
        "v1_outside_replaced_main": v1["outside_count"] > 0,
        "v2_inside_replaced_main": v2["inside_count"] > 0,
        "v2_outside_replaced_main": v2["outside_count"] > 0,
    }

    counts = {
        "v1_total_before": v1["total_before"],
        "v2_total_before": v2["total_before"],
        "v1_inside_count": v1["inside_count"],
        "v1_outside_count": v1["outside_count"],
        "v2_inside_count": v2["inside_count"],
        "v2_outside_count": v2["outside_count"],
    }

    return counts, lineage


def patch_runtime_main(ns, lineage):
    base_main = ns["MAIN"]
    if base_main.count(BASE_MAIN_MARKER) != 1:
        raise SystemExit(
            f"Expected exactly one V3 marker in original base MAIN, found {base_main.count(BASE_MAIN_MARKER)}"
        )
    if V1_MARKER in base_main or V2_MARKER in base_main:
        raise SystemExit("Unexpected V1/V2 lineage marker already present in original V3 MAIN")
    if HOTFIX_MARKER in base_main:
        raise SystemExit("V3.6 hotfix marker already present in original V3 MAIN")

    # The original V3 transform replaces the whole legacy lux-page main.
    # Every marker inside that old main will disappear. Markers outside survive.
    # Reinject exactly one marker only when no outside copy survives.
    inject_v1 = lineage["v1_outside_count"] == 0 and lineage["v1_inside_count"] >= 1
    inject_v2 = lineage["v2_outside_count"] == 0 and lineage["v2_inside_count"] >= 1

    injected = []
    if inject_v1:
        injected.append(f"<!-- {V1_MARKER} -->")
    if inject_v2:
        injected.append(f"<!-- {V2_MARKER} -->")
    injected.append(BASE_MAIN_MARKER)
    injected.append(f"<!-- {HOTFIX_MARKER} -->")

    replacement = "\n  ".join(injected)
    ns["MAIN"] = base_main.replace(BASE_MAIN_MARKER, replacement, 1)

    patched_main = ns["MAIN"]
    if patched_main.count(PATCH_MARKER) != 1:
        raise SystemExit("V3 marker count is not exactly 1 in patched runtime MAIN")
    if patched_main.count(HOTFIX_MARKER) != 1:
        raise SystemExit("V3.6 hotfix marker count is not exactly 1 in patched runtime MAIN")
    if patched_main.count(V1_MARKER) != (1 if inject_v1 else 0):
        raise SystemExit("V1 runtime MAIN injection count mismatch")
    if patched_main.count(V2_MARKER) != (1 if inject_v2 else 0):
        raise SystemExit("V2 runtime MAIN injection count mismatch")

    return {
        "v1_reinjected": inject_v1,
        "v2_reinjected": inject_v2,
        "v1_preserved_outside": lineage["v1_outside_count"] == 1,
        "v2_preserved_outside": lineage["v2_outside_count"] == 1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-script", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--asset-dir", required=True)
    ap.add_argument("--manifest")
    args = ap.parse_args()

    base_script = Path(args.base_script)
    source_path = Path(args.source)
    output_path = Path(args.output)
    asset_dir = Path(args.asset_dir)

    ns, base_raw_sha256, base_blob_sha1 = load_base(base_script)
    source = source_path.read_text(encoding="utf-8")

    source_counts, lineage = analyze_source_lineage(source)
    lineage_actions = patch_runtime_main(ns, lineage)

    result, base_guards = ns["transform"](source)

    if not all(base_guards.values()):
        failed_base = [k for k, v in base_guards.items() if not v]
        raise SystemExit("V3 base guard failed: " + ", ".join(failed_base))

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
        "no_jobposting": (
            '"@type":"JobPosting"' not in result
            and '"@type": "JobPosting"' not in result
        ),
        "reduced_motion": "prefers-reduced-motion:reduce" in result,
        "reference_sections": all(
            x in result
            for x in [
                "ref3-header", "ref3-hero", "ref3-application", "ref3-stats",
                "ref3-why", "ref3-roles", "ref3-testimonials",
                "ref3-final-cta", "ref3-footer",
            ]
        ),
    }
    failed = [k for k, v in final_guards.items() if not v]
    if failed:
        raise SystemExit("V3.6 post-transform guard failed: " + ", ".join(failed))

    output_path.write_text(result, encoding="utf-8")

    asset_results = {}
    for filename, symbol in [
        ("hero-reference.webp", "HERO_B64"),
        ("culture-reference.webp", "CULTURE_B64"),
        ("cta-reference.webp", "CTA_B64"),
    ]:
        digest, size = ns["write_asset"](asset_dir / filename, ns[symbol])
        expected_digest, expected_size = EXPECTED_ASSETS[filename]
        if digest != expected_digest or size != expected_size:
            raise SystemExit(
                f"Asset validation failed for {filename}: sha={digest} bytes={size}; "
                f"expected sha={expected_digest} bytes={expected_size}"
            )
        asset_results[filename] = {"sha256": digest, "bytes": size}

    manifest = {
        "patch": PATCH_ID,
        "patch_marker": PATCH_MARKER,
        "hotfix_marker": HOTFIX_MARKER,
        "base_v3_raw_sha256": base_raw_sha256,
        "base_v3_git_blob_sha1": base_blob_sha1,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "files_changed": [
            "themes/thegem-elementor/page-join-us.php",
            "themes/thegem-elementor/assets/join-us/reference-v3/hero-reference.webp",
            "themes/thegem-elementor/assets/join-us/reference-v3/culture-reference.webp",
            "themes/thegem-elementor/assets/join-us/reference-v3/cta-reference.webp",
        ],
        "bugs_fixed": [
            "Accept legitimate duplicate lineage markers when copies exist both inside and outside the legacy main.",
            "Use inside/outside counts instead of requiring total lineage count to equal one before transform.",
            "Reinject a lineage marker only when no outside copy survives the original V3 main replacement.",
            "Refuse unsafe cases with more than one preserved outside copy instead of silently normalizing preserved regions.",
            "Use a hotfix marker that does not contain the original V3 patch marker substring.",
            "Verify original V3 independently with raw file SHA256 and canonical Git blob SHA1.",
        ],
        "base_main_patch_mode": "runtime_namespace_dual_location_lineage",
        "source_marker_counts": source_counts,
        "lineage_analysis": lineage,
        "lineage_actions": lineage_actions,
        "final_marker_counts": final_counts,
        "base_guards": base_guards,
        "final_guards": final_guards,
        "assets": asset_results,
        "integrations_preserved": True,
        "seo_schema_preserved": True,
        "git_mutations_by_patch_runner": False,
    }

    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
