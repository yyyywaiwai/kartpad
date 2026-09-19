#!/usr/bin/env python3
"""Stage tracked translator source, preserving only the destination's build caches."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


def stage(repo: Path, destination: Path) -> None:
    source = repo / "vendor/wiicompiled"
    names = subprocess.check_output(
        ["git", "-C", str(source), "ls-files", "--cached", "-z", "--", "."]
    ).decode().split("\0")
    # A complete filtered tree lets rsync --delete remove source dropped since
    # the previous stage. A files-from list alone does not provide that contract.
    with tempfile.TemporaryDirectory(prefix="kartpad-translator-source-") as temporary:
        filtered = Path(temporary)
        for name in filter(None, names):
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe tracked translator path: {name}")
            if any(part in (".git", "bin", "obj") for part in relative.parts):
                continue
            original = source / relative
            if not original.exists() and not original.is_symlink():
                continue  # A tracked working-tree deletion must disappear downstream.
            target = filtered / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if original.is_symlink():
                target.symlink_to(original.readlink())
            else:
                shutil.copy2(original, target)
        if not (filtered / "translator/src/Translator.Cli/Translator.Cli.csproj").is_file():
            raise ValueError("missing tracked WiiCompiled translator source")
        destination.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "rsync", "-a", "--delete", "--exclude", ".git", "--exclude", "bin", "--exclude", "obj",
            str(filtered) + "/", str(destination) + "/",
        ], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    stage(Path(__file__).resolve().parents[1], args.destination)


if __name__ == "__main__":
    main()
