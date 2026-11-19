#!/usr/bin/env python3
"""Record the immutable input for the published production dataset."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = "data/airports.json"
MANIFEST = ROOT / "data/production-manifest.json"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def production_manifest(commit):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Use the full commit SHA from upstream main")
    git("merge-base", "--is-ancestor", commit, "origin/main")
    data = git("show", f"{commit}:{DATASET}")
    dataset = json.loads(data)
    package = json.loads(git("show", f"{commit}:package.json"))
    if dataset["dataVersion"] != package["version"]:
        raise ValueError("Package and data versions disagree")
    return {
        "dataVersion": dataset["dataVersion"],
        "schemaVersion": dataset["schemaVersion"],
        "commit": commit,
        "queryHorizon": json.loads(git("show", f"{commit}:src/query-horizon.json")),
        "files": {DATASET: {"sha256": hashlib.sha256(data).hexdigest()}},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--commit", help="Full SHA of the reviewed commit on main")
    mode.add_argument("--check", action="store_true", help="Verify the committed pointer")
    args = parser.parse_args()
    previous = json.loads(MANIFEST.read_bytes()) if MANIFEST.exists() else None
    if args.check and previous is None:
        parser.error("Production manifest is missing")
    manifest = production_manifest(previous["commit"] if args.check else args.commit)
    if args.check:
        if previous != manifest:
            parser.error("Production manifest differs from the immutable source")
    elif previous and manifest != previous:
        old_version = tuple(map(int, previous["dataVersion"].split(".")))
        new_version = tuple(map(int, manifest["dataVersion"].split(".")))
        if new_version <= old_version:
            parser.error("Advance dataVersion to publish a different production dataset")
    if not args.check:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Production manifest v{manifest['dataVersion']} at {manifest['commit']}")


if __name__ == "__main__":
    main()
