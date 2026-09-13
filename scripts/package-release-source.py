#!/usr/bin/env python3
"""Create a deterministic source snapshot from explicitly selected Git commits.

No working-tree or ignored files are read. The companion metadata can restore
the exact shallow Git identity required by the existing pinned build scripts.
This packages selected inputs; the release owner must establish coverage.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def snapshot(root: Path, revision: str, label: str, archive: tarfile.TarFile) -> dict:
    commit = git(root, "rev-parse", revision + "^{commit}").decode().strip()
    records = git(root, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")
    entries = []
    # One cat-file process, rather than one process for every source file.
    blobs = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert blobs.stdin and blobs.stdout
    try:
        for record in records:
            if not record:
                continue
            descriptor, raw_name = record.split(b"\t", 1)
            mode, kind, oid = descriptor.decode().split()
            name = raw_name.decode()
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
                raise ValueError(f"unsafe tracked path: {name}")
            entry = {"path": name, "mode": mode, "gitObject": oid}
            if kind == "commit":
                entry["submodule"] = True
                entries.append(entry)
                continue
            if kind != "blob":
                raise ValueError(f"unexpected Git type: {kind}")
            blobs.stdin.write((oid + "\n").encode()); blobs.stdin.flush()
            response = blobs.stdout.readline().decode().split()
            if response[:2] != [oid, "blob"]:
                raise ValueError("cat-file identity mismatch")
            data = blobs.stdout.read(int(response[2]))
            assert blobs.stdout.read(1) == b"\n"
            assert hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == oid
            info = tarfile.TarInfo(f"source/{label}/{name}")
            info.mtime = 0
            info.mode = 0o755 if mode == "100755" else 0o644
            if mode == "120000":
                target = data.decode()
                # Preserve source-tree symlinks only when they stay in that tree.
                parts = list(path.parent.parts)
                if PurePosixPath(target).is_absolute():
                    raise ValueError("absolute source symlink")
                for part in PurePosixPath(target).parts:
                    if part == "..":
                        if not parts:
                            raise ValueError("escaping source symlink")
                        parts.pop()
                    elif part != ".":
                        parts.append(part)
                info.type = tarfile.SYMTYPE; info.linkname = target
                archive.addfile(info)
            else:
                info.size = len(data); archive.addfile(info, io.BytesIO(data))
            entry.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            entries.append(entry)
    finally:
        blobs.stdin.close()
        if blobs.wait() != 0:
            raise RuntimeError("cat-file failed")
    metadata = {"schemaVersion": 1, "label": label, "commit": commit,
                "commitObject": git(root, "cat-file", "commit", commit).decode(), "entries": entries}
    data = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode()
    info = tarfile.TarInfo(f"metadata/{label}.json"); info.size = len(data); info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))
    return {"label": label, "commit": commit, "files": len(entries),
            "metadataSHA256": hashlib.sha256(data).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", action="append", nargs=3, metavar=("LABEL", "PATH", "REVISION"), required=True)
    args = parser.parse_args()
    labels = [item[0] for item in args.repo]
    if len(set(labels)) != len(labels) or any(not label.replace("-", "").replace("_", "").isalnum() for label in labels):
        parser.error("labels must be unique simple names")
    with args.output.open("xb") as output, gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w|") as archive:
            manifest = [snapshot(Path(path), revision, label, archive) for label, path, revision in args.repo]
            for name in ("restore-source-git.py",):
                data = Path(__file__).with_name(name).read_bytes()
                info = tarfile.TarInfo(name); info.size = len(data); info.mode = 0o755
                archive.addfile(info, io.BytesIO(data))
    print(json.dumps({"archives": manifest, "bytes": args.output.stat().st_size,
                      "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
