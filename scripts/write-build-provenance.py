#!/usr/bin/env python3
"""Write deterministic, path-free fingerprints for diagnostic build matching."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def fingerprint(root, names):
    digest = hashlib.sha256()
    count = 0
    for name in sorted(names):
        path = root / name
        if path.is_symlink():
            # Never traverse a link into an unrelated private directory.
            raise ValueError("source fingerprint requires regular files, not symlinks")
        if not path.is_file():
            raise ValueError("source fingerprint input is not a regular file")
        content = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                content.update(chunk)
        encoded = name.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(content.digest())
        count += 1
    return {"files": count, "sha256": digest.hexdigest()}


def tree(root):
    if not root.is_dir():
        raise ValueError("source fingerprint directory is unavailable")
    names = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("source fingerprint does not traverse symlinks")
        if path.is_file():
            names.append(path.relative_to(root).as_posix())
    if not names:
        raise ValueError("source fingerprint directory is empty")
    return fingerprint(root, names)


def manifest(repo, runtime=None, translation=None):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL)
    revision = git("rev-parse", "HEAD").decode().strip()
    dependencies = []
    def tracked_names(root, prefix=""):
        records = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "-z"]).split(b"\0")
        names = set()
        for record in filter(None, records):
            descriptor, raw_name = record.split(b"\t", 1)
            mode, _, index_stage = descriptor.decode().split()
            name = raw_name.decode()
            if index_stage != "0":
                raise ValueError("source fingerprint requires resolved index entries")
            path = root / name
            if mode == "160000":
                if path.is_symlink() or not (path / ".git").exists():
                    raise ValueError("source fingerprint requires initialized source submodules")
                commit = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"]).decode().strip()
                dirty = bool(subprocess.check_output(["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"]))
                dependencies.append({"commit": commit, "dirty": dirty})
                names.update(tracked_names(path, prefix + name + "/"))
            elif path.exists() or path.is_symlink():
                names.add(prefix + name)
        return names
    names = tracked_names(repo)
    # Preserve the existing parent-working-tree diagnostic coverage. Maintained
    # submodules contribute tracked files only, matching runtime staging.
    names.update(name for name in git("ls-files", "-z", "--others", "--exclude-standard").decode().split("\0") if name)
    return {
        "schema": 1,
        "source_revision": revision,
        "source_dirty": bool(git("status", "--porcelain", "--untracked-files=normal")),
        "kartpad_source": fingerprint(repo, names),
        "source_dependencies": dependencies,
        "prepared_runtime": tree(runtime.resolve()) if runtime else None,
        "translation": tree(translation.resolve()) if translation else None,
        "scope": "source_inputs_only_not_dependency_or_binary_identity",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--translation", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = (json.dumps(manifest(args.repo.resolve(), args.runtime, args.translation),
                       sort_keys=True, separators=(",", ":")) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Avoid touching an unchanged resource, so incremental compilation can reuse it.
    if not args.output.exists() or args.output.read_bytes() != data:
        args.output.write_bytes(data)


if __name__ == "__main__":
    main()
