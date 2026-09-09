#!/usr/bin/env python3
import argparse
import hashlib
import sys
from pathlib import Path

PATCH_ID = "JOIN_US_REFERENCE_EXACT_V3_9"
HOTFIX_MARKER = "TAM_JOIN_US_V3_9_MEDIA_FALLBACK"
V38_GIT_BLOB_SHA1 = "bfc078a0188a8194f66941c1b87bb30b44965565"
V38_OLD_HOTFIX_MARKER = "TAM_JOIN_US_V3_8_MEDIA_FALLBACK"
V38_CSS_MARKER_LINE = "/* TAM_JOIN_US_V3_8_MEDIA_FALLBACK */"

def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()

def load_v38(path: Path):
    raw = path.read_bytes()
    blob = git_blob_sha1(raw)
    if blob != V38_GIT_BLOB_SHA1:
        raise SystemExit(f"V3.8 Git blob SHA1 mismatch: {blob}; expected {V38_GIT_BLOB_SHA1}")
    ns = {"__name__": "tamiyouz_v38_runtime_hotfixed_v39", "__file__": str(path)}
    exec(compile(raw.decode("utf-8"), str(path), "exec"), ns, ns)
    for required in ["main", "PATCH_ID", "PATCH_MARKER", "HOTFIX_MARKER", "EXTRA_CSS"]:
        if required not in ns:
            raise SystemExit(f"V3.8 symbol missing: {required}")
    if ns["HOTFIX_MARKER"] != V38_OLD_HOTFIX_MARKER:
        raise SystemExit("Unexpected V3.8 hotfix marker")
    css = ns["EXTRA_CSS"]
    if css.count(V38_CSS_MARKER_LINE) != 1:
        raise SystemExit(f"Expected exactly one V3.8 CSS hotfix marker line, found {css.count(V38_CSS_MARKER_LINE)}")
    ns["EXTRA_CSS"] = css.replace(V38_CSS_MARKER_LINE, "", 1)
    ns["PATCH_ID"] = PATCH_ID
    ns["HOTFIX_MARKER"] = HOTFIX_MARKER
    if V38_OLD_HOTFIX_MARKER in ns["EXTRA_CSS"]:
        raise SystemExit("Old V3.8 marker remains in CSS")
    if HOTFIX_MARKER in ns["EXTRA_CSS"]:
        raise SystemExit("V3.9 marker must not be in CSS")
    if ns["PATCH_MARKER"] in HOTFIX_MARKER:
        raise SystemExit("V3.9 marker contains base marker substring")
    return ns, blob

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v38-script", required=True)
    ap.add_argument("--base-script", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--manifest")
    ap.add_argument("--asset-dir")
    args = ap.parse_args()
    ns, _ = load_v38(Path(args.v38_script))
    forwarded = [ns["__file__"], "--base-script", args.base_script, "--source", args.source, "--output", args.output]
    if args.manifest:
        forwarded += ["--manifest", args.manifest]
    if args.asset_dir:
        forwarded += ["--asset-dir", args.asset_dir]
    old_argv = sys.argv[:]
    try:
        sys.argv = forwarded
        ns["main"]()
    finally:
        sys.argv = old_argv

if __name__ == "__main__":
    main()
