#!/usr/bin/env python3
"""Restore a packaged source snapshot's exact shallow Git identity, offline.

Run from an extracted package: python3 restore-source-git.py metadata/NAME.json
Only use with the source package whose checksums you have verified.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

metadata_path = Path(sys.argv[1]).resolve()
metadata = json.loads(metadata_path.read_text())
root = metadata_path.parent.parent / "source" / metadata["label"]
if (root / ".git").exists():
    raise SystemExit("Refusing to replace an existing Git repository")

def git(*args, data=None):
    return subprocess.check_output(["git", "-C", str(root), *args], input=data)

# Validate every file before writing repository metadata.
for entry in metadata["entries"]:
    if entry.get("submodule"):
        (root / entry["path"]).mkdir(parents=True, exist_ok=True)
        continue
    path = root / entry["path"]
    data = os.readlink(path).encode() if entry["mode"] == "120000" else path.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"Source differs from packaged manifest: {entry['path']}")
git("init", "-q")
index = []
for entry in metadata["entries"]:
    if not entry.get("submodule"):
        path = root / entry["path"]
        data = os.readlink(path).encode() if entry["mode"] == "120000" else path.read_bytes()
        oid = git("hash-object", "-w", "--stdin", data=data).decode().strip()
        assert oid == entry["gitObject"]
    index.append(f"{entry['mode']} {entry['gitObject']}\t{entry['path']}\0")
git("update-index", "-z", "--index-info", data="".join(index).encode())
tree = git("write-tree").decode().strip()
assert metadata["commitObject"].splitlines()[0] == "tree " + tree
commit = git("hash-object", "-w", "-t", "commit", "--stdin", data=metadata["commitObject"].encode()).decode().strip()
assert commit == metadata["commit"]
(root / ".git/shallow").write_text(commit + "\n")
git("update-ref", "refs/heads/source-snapshot", commit)
git("symbolic-ref", "HEAD", "refs/heads/source-snapshot")
git("fsck", "--no-reflogs", "--connectivity-only")
print(f"Restored {metadata['label']} at {commit}; no network or signing material used")
