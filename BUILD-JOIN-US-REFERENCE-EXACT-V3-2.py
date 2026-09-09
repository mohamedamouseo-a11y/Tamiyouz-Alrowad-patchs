#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

PATCH_ID = "JOIN_US_REFERENCE_EXACT_V3_2"
PATCH_MARKER = "TAM_JOIN_US_REFERENCE_EXACT_V3"
HOTFIX_MARKER = "TAM_JOIN_US_REFERENCE_EXACT_V3_2_HOTFIX"

BASE_SCRIPT_RAW_SHA256 = "c7fe45099e2c8d8285de8c9848024c8c3e6428ae857276bb74d6c94fb0c18687"
BASE_SCRIPT_GIT_BLOB_SHA1 = "49e7a98a5e8402073724948a00825cf0da8d3165"

EXPECTED_ASSETS = {
    "hero-reference.webp": ("15b7ba9c9ba02a660e4d0bd157ed09ce4cbd0ecb76a12cf20e49e9e63675f514", 29968),
    "culture-reference.webp": ("117d9e92cd4cb2d358dfde74bdd2959b9fe6be2beefd8fbc5f6c5b160be51384", 17452),
    "cta-reference.webp": ("a55a907e0a2e91c32deae546068c2c7afdabd383ad7f7c265403ad154f18a2ee", 4832),
}

OLD_MAIN_PREFIX = (
    "MAIN = '<main class=\"ref3-page\" id=\"main-content\">\\n"
    "  <!-- TAM_JOIN_US_REFERENCE_EXACT_V3 -->\\n"
)
NEW_MAIN_PREFIX = (
    "MAIN = '<main class=\"ref3-page\" id=\"main-content\">\\n"
    "  <!-- TAM_JOIN_US_LUXURY_V1 -->\\n"
    "  <!-- TAM_JOIN_US_LUXURY_V2_FIDELITY -->\\n"
    "  <!-- TAM_JOIN_US_REFERENCE_EXACT_V3 -->\\n"
    "  <!-- TAM_JOIN_US_REFERENCE_EXACT_V3_2_HOTFIX -->\\n"
)


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def load_fixed_base(base_script: Path):
    raw = base_script.read_bytes()
    raw_digest = raw_sha256(raw)
    blob_digest = git_blob_sha1(raw)

    if raw_digest != BASE_SCRIPT_RAW_SHA256:
        raise SystemExit(
            f"Base V3 raw SHA256 mismatch: {raw_digest}; "
            f"expected {BASE_SCRIPT_RAW_SHA256}"
        )
    if blob_digest != BASE_SCRIPT_GIT_BLOB_SHA1:
        raise SystemExit(
            f"Base V3 git blob SHA1 mismatch: {blob_digest}; "
            f"expected {BASE_SCRIPT_GIT_BLOB_SHA1}"
        )

    text = raw.decode("utf-8")
    count = text.count(OLD_MAIN_PREFIX)
    if count != 1:
        raise SystemExit(f"Expected exactly one V3 MAIN prefix, found {count}")

    fixed = text.replace(OLD_MAIN_PREFIX, NEW_MAIN_PREFIX, 1)

    ns = {
        "__name__": "tamiyouz_v3_base_hotfixed_v32",
        "__file__": str(base_script),
    }
    exec(compile(fixed, str(base_script), "exec"), ns, ns)

    for required in ["transform", "write_asset", "HERO_B64", "CULTURE_B64", "CTA_B64"]:
        if required not in ns:
            raise SystemExit(f"Base V3 symbol missing after hotfix load: {required}")

    return ns, raw_digest, blob_digest


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

    ns, base_raw_sha256, base_blob_sha1 = load_fixed_base(base_script)
    source = source_path.read_text(encoding="utf-8")

    result, base_guards = ns["transform"](source)

    final_guards = {
        "v1_preserved": "TAM_JOIN_US_LUXURY_V1" in result,
        "v2_preserved": "TAM_JOIN_US_LUXURY_V2_FIDELITY" in result,
        "v3_marker_once": result.count(PATCH_MARKER) == 1,
        "hotfix_marker_once": result.count(HOTFIX_MARKER) == 1,
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
                "ref3-header",
                "ref3-hero",
                "ref3-application",
                "ref3-stats",
                "ref3-why",
                "ref3-roles",
                "ref3-testimonials",
                "ref3-final-cta",
                "ref3-footer",
            ]
        ),
    }
    failed = [k for k, v in final_guards.items() if not v]
    if failed:
        raise SystemExit("V3.2 post-transform guard failed: " + ", ".join(failed))

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
            "Preserve V1/V2 lineage markers in replacement V3 main.",
            "Verify original V3 using both raw file SHA256 and canonical Git blob SHA1 instead of comparing unlike hash formats.",
        ],
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
