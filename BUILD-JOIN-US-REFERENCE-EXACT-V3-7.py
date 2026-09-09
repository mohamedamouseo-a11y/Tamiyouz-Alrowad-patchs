#!/usr/bin/env python3
import argparse
import base64
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

PATCH_ID = "JOIN_US_REFERENCE_EXACT_V3_7"
PATCH_MARKER = "TAM_JOIN_US_REFERENCE_EXACT_V3"
HOTFIX_MARKER = "TAM_JOIN_US_V3_7_ASSET_AUTH_HOTFIX"

BASE_V3_RAW_SHA256 = "c7fe45099e2c8d8285de8c9848024c8c3e6428ae857276bb74d6c94fb0c18687"
BASE_V3_GIT_BLOB_SHA1 = "49e7a98a5e8402073724948a00825cf0da8d3165"
V36_GIT_BLOB_SHA1 = "74f82fd7617387b48b0c281fadf65d045f24124c"

ASSET_SYMBOLS = {
    "hero-reference.webp": "HERO_B64",
    "culture-reference.webp": "CULTURE_B64",
    "cta-reference.webp": "CTA_B64",
}


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def verify_script(path: Path, expected_blob_sha1: str, expected_raw_sha256=None):
    raw = path.read_bytes()
    blob_sha1 = git_blob_sha1(raw)
    raw_sha256 = hashlib.sha256(raw).hexdigest()
    if blob_sha1 != expected_blob_sha1:
        raise SystemExit(
            f"Git blob SHA1 mismatch for {path.name}: {blob_sha1}; expected {expected_blob_sha1}"
        )
    if expected_raw_sha256 and raw_sha256 != expected_raw_sha256:
        raise SystemExit(
            f"Raw SHA256 mismatch for {path.name}: {raw_sha256}; expected {expected_raw_sha256}"
        )
    return raw, raw_sha256, blob_sha1


def exec_script(raw: bytes, path: Path, name: str):
    ns = {"__name__": name, "__file__": str(path)}
    exec(compile(raw.decode("utf-8"), str(path), "exec"), ns, ns)
    return ns


def authenticated_asset_metadata(base_ns):
    metadata = {}
    expected_assets = {}

    for filename, symbol in ASSET_SYMBOLS.items():
        if symbol not in base_ns:
            raise SystemExit(f"Authenticated base V3 missing asset symbol: {symbol}")

        encoded = base_ns[symbol]
        if not isinstance(encoded, str) or not encoded:
            raise SystemExit(f"Authenticated base V3 asset symbol is not a non-empty string: {symbol}")

        try:
            raw = base64.b64decode(encoded.encode("ascii"), validate=True)
        except Exception as exc:
            raise SystemExit(f"Invalid base64 for authenticated {symbol}: {exc}")

        if len(raw) < 12 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
            raise SystemExit(f"Authenticated {filename} is not a valid RIFF/WEBP payload")

        riff_declared_total = int.from_bytes(raw[4:8], "little") + 8
        if riff_declared_total != len(raw):
            raise SystemExit(
                f"Authenticated {filename} RIFF length mismatch: header={riff_declared_total}, actual={len(raw)}"
            )

        sha256 = hashlib.sha256(raw).hexdigest()
        metadata[filename] = {
            "symbol": symbol,
            "sha256": sha256,
            "bytes": len(raw),
            "riff_total_bytes": riff_declared_total,
            "magic": "RIFF/WEBP",
        }
        expected_assets[filename] = (sha256, len(raw))

    return metadata, expected_assets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-script", required=True)
    ap.add_argument("--v36-script", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--asset-dir", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()

    base_path = Path(args.base_script)
    v36_path = Path(args.v36_script)
    manifest_path = Path(args.manifest)

    base_raw, base_raw_sha256, base_blob_sha1 = verify_script(
        base_path,
        BASE_V3_GIT_BLOB_SHA1,
        BASE_V3_RAW_SHA256,
    )
    v36_raw, v36_raw_sha256, v36_blob_sha1 = verify_script(
        v36_path,
        V36_GIT_BLOB_SHA1,
    )

    base_ns = exec_script(base_raw, base_path, "tamiyouz_v3_asset_authority_v37")
    asset_metadata, expected_assets = authenticated_asset_metadata(base_ns)

    # V3.6 already contains the validated dual-location lineage logic.
    # Load the exact pinned V3.6 blob, then override only runtime metadata that
    # identifies this hotfix and the stale asset expectations.
    v36_ns = exec_script(v36_raw, v36_path, "tamiyouz_v36_runtime_for_v37")

    for required in ["main", "EXPECTED_ASSETS", "PATCH_ID", "HOTFIX_MARKER"]:
        if required not in v36_ns:
            raise SystemExit(f"Pinned V3.6 symbol missing: {required}")

    if PATCH_MARKER in HOTFIX_MARKER:
        raise SystemExit("V3.7 hotfix marker must not contain the V3 patch marker substring")

    v36_ns["PATCH_ID"] = PATCH_ID
    v36_ns["HOTFIX_MARKER"] = HOTFIX_MARKER
    v36_ns["EXPECTED_ASSETS"] = expected_assets

    old_argv = sys.argv[:]
    captured = io.StringIO()
    try:
        sys.argv = [
            str(v36_path),
            "--base-script", str(base_path),
            "--source", str(Path(args.source)),
            "--output", str(Path(args.output)),
            "--asset-dir", str(Path(args.asset_dir)),
            "--manifest", str(manifest_path),
        ]
        with contextlib.redirect_stdout(captured):
            v36_ns["main"]()
    finally:
        sys.argv = old_argv

    if not manifest_path.exists():
        raise SystemExit("V3.6 runtime did not create the requested manifest")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("patch") != PATCH_ID:
        raise SystemExit(f"Unexpected manifest patch id: {manifest.get('patch')}")
    if manifest.get("hotfix_marker") != HOTFIX_MARKER:
        raise SystemExit(f"Unexpected manifest hotfix marker: {manifest.get('hotfix_marker')}")

    generated_assets = manifest.get("assets") or {}
    for filename, trusted in asset_metadata.items():
        generated = generated_assets.get(filename) or {}
        if generated.get("sha256") != trusted["sha256"]:
            raise SystemExit(
                f"Generated {filename} SHA256 differs from authenticated V3 asset: "
                f"{generated.get('sha256')} != {trusted['sha256']}"
            )
        if generated.get("bytes") != trusted["bytes"]:
            raise SystemExit(
                f"Generated {filename} byte count differs from authenticated V3 asset: "
                f"{generated.get('bytes')} != {trusted['bytes']}"
            )

    manifest["asset_authority_mode"] = "authenticated_original_v3_embedded_assets"
    manifest["authenticated_base_v3_assets"] = asset_metadata
    manifest["v36_runtime_git_blob_sha1"] = v36_blob_sha1
    manifest["v36_runtime_raw_sha256"] = v36_raw_sha256
    manifest["asset_expectations_derived_not_hardcoded"] = True
    manifest["asset_integrity_checks"] = {
        "base_v3_raw_sha256_verified": base_raw_sha256 == BASE_V3_RAW_SHA256,
        "base_v3_git_blob_sha1_verified": base_blob_sha1 == BASE_V3_GIT_BLOB_SHA1,
        "v36_git_blob_sha1_verified": v36_blob_sha1 == V36_GIT_BLOB_SHA1,
        "base64_strict_decode": True,
        "riff_webp_magic_verified": True,
        "riff_declared_length_matches_actual": True,
        "generated_matches_authenticated_base": True,
    }
    manifest.setdefault("bugs_fixed", []).append(
        "Derive asset SHA256 and byte expectations directly from the authenticated original V3 embedded base64 assets instead of stale hard-coded metadata."
    )

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
