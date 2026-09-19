"""Offline regression checks for runtime source identity and release snapshots."""
from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "builder"))
from kartpad_builder.pipeline import source_fingerprint
from kartpad_builder.errors import BuildError
from kartpad_builder.bootstrap import _prepare_runtime_sources

spec = importlib.util.spec_from_file_location("package_source", ROOT / "scripts/package-release-source.py")
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode().strip()


def repository(root):
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.name", "Source test")
    git(root, "config", "user.email", "test@example.invalid")
    (root / "source.cpp").write_text("baseline\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "baseline")


class SourceSubmoduleInputs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        leaf, child, self.root = [self.base / name for name in ("leaf", "child", "parent")]
        for root in (leaf, child, self.root):
            repository(root)
        git(child, "-c", "protocol.file.allow=always", "submodule", "add", str(leaf), "nested")
        git(child, "commit", "-qam", "nested source")
        git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(child), "vendor/runtime")
        git(self.root, "commit", "-qam", "runtime source")
        git(self.root, "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--recursive")
        self.child = self.root / "vendor/runtime"
        self.leaf = self.child / "nested"

    def archive(self):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w") as archive:
            packager.snapshot(self.root, "HEAD", "kartpad", archive)
        output.seek(0)
        return output

    def test_successive_tracked_edits_and_nested_edits_change_fingerprint(self):
        baseline = source_fingerprint(self.root)
        file = self.child / "source.cpp"
        file.write_text("first edit\n")
        first = source_fingerprint(self.root)
        file.write_text("second edit\n")
        second = source_fingerprint(self.root)
        git(self.child, "add", "source.cpp")
        staged = source_fingerprint(self.root)
        (self.leaf / "source.cpp").write_text("nested edit\n")
        nested = source_fingerprint(self.root)
        self.assertEqual(len({baseline, first, second, staged, nested}), 5)
        (self.child / "private-save.bin").write_bytes(b"private")
        self.assertEqual(nested, source_fingerprint(self.root))

    def test_missing_submodule_fails_fingerprint_and_snapshot(self):
        shutil.rmtree(self.leaf)
        with self.assertRaisesRegex(BuildError, "Missing initialized source submodule"):
            source_fingerprint(self.root)
        with self.assertRaisesRegex(ValueError, "Missing initialized source submodule"):
            self.archive()

    def test_bootstrap_initializes_only_missing_runtime_source(self):
        dependency = {"platformPaths": {"test": "vendor/runtime"}}
        git(self.root, "submodule", "deinit", "-f", "--", "vendor/runtime")
        with self.assertRaisesRegex(BuildError, "run .* bootstrap"):
            _prepare_runtime_sources(self.root, dependency, False)
        commands = []
        def local_run(command):
            commands.append(command)
            subprocess.run([command[0], "-c", "protocol.file.allow=always", *command[1:]], check=True, capture_output=True)
        with patch("kartpad_builder.bootstrap.run", side_effect=local_run):
            _prepare_runtime_sources(self.root, dependency, True)
            (self.child / "source.cpp").write_text("developer work\n")
            _prepare_runtime_sources(self.root, dependency, True)
            _prepare_runtime_sources(self.root, dependency, False)
        self.assertEqual(len(commands), 1)
        self.assertEqual((self.child / "source.cpp").read_text(), "developer work\n")

    def test_bootstrap_preserves_checkout_when_gitlink_mismatches(self):
        dependency = {"platformPaths": {"test": "vendor/runtime"}}
        (self.child / "source.cpp").write_text("developer commit\n")
        git(self.child, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qam", "local work")
        head = git(self.child, "rev-parse", "HEAD")
        for install in (False, True):
            with self.assertRaisesRegex(BuildError, "does not match its staged gitlink"):
                _prepare_runtime_sources(self.root, dependency, install)
            self.assertEqual(git(self.child, "rev-parse", "HEAD"), head)
        git(self.root, "add", "vendor/runtime")
        _prepare_runtime_sources(self.root, dependency, False)

    def test_snapshot_fails_when_pinned_commit_is_unavailable(self):
        git(self.root, "update-index", "--cacheinfo", "160000," + "1" * 40 + ",vendor/runtime")
        git(self.root, "commit", "-qm", "unavailable source pin")
        with self.assertRaises(subprocess.CalledProcessError):
            self.archive()

    def test_plain_repository_keeps_existing_snapshot_restore_api(self):
        plain = self.base / "plain"
        repository(plain)
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w") as archive:
            summary = packager.snapshot(plain, "HEAD", "plain", archive)
        self.assertEqual(summary["files"], 1)
        destination = self.base / "plain-extracted"
        destination.mkdir()
        with tarfile.open(fileobj=io.BytesIO(output.getvalue())) as archive:
            archive.extractall(destination)  # Trusted fixture source.
        subprocess.run([sys.executable, str(ROOT / "scripts/restore-source-git.py"), str(destination / "metadata/plain.json")], check=True, capture_output=True)
        self.assertEqual(git(destination / "source/plain", "rev-parse", "HEAD"), git(plain, "rev-parse", "HEAD"))

    def test_archive_uses_pins_and_restores_nested_source_offline(self):
        baseline_fingerprint = source_fingerprint(self.root)
        parent_sha = git(self.root, "rev-parse", "HEAD")
        child_sha = git(self.child, "rev-parse", "HEAD")
        leaf_sha = git(self.leaf, "rev-parse", "HEAD")
        (self.child / "source.cpp").write_text("later committed source\n")
        git(self.child, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qam", "later")
        (self.leaf / "source.cpp").write_text("dirty source\n")
        (self.child / "private-save.bin").write_bytes(b"not source")
        first = self.archive().getvalue()
        self.assertEqual(first, self.archive().getvalue())
        destination = self.base / "extracted"
        destination.mkdir()
        with tarfile.open(fileobj=io.BytesIO(first)) as archive:
            self.assertFalse(any("private-save" in name or "/.git/" in name for name in archive.getnames()))
            archive.extractall(destination)  # Trusted archive made from these local fixture repos.
        restored = destination / "source/kartpad"
        self.assertEqual((restored / "vendor/runtime/source.cpp").read_text(), "baseline\n")
        self.assertEqual((restored / "vendor/runtime/nested/source.cpp").read_text(), "baseline\n")
        subprocess.run([sys.executable, str(ROOT / "scripts/restore-source-git.py"), str(destination / "metadata/kartpad.json")], check=True, capture_output=True)
        for path, sha in ((restored, parent_sha), (restored / "vendor/runtime", child_sha), (restored / "vendor/runtime/nested", leaf_sha)):
            self.assertEqual(git(path, "rev-parse", "HEAD"), sha)
            self.assertEqual(git(path, "status", "--porcelain"), "")
        self.assertEqual(source_fingerprint(restored), baseline_fingerprint)


if __name__ == "__main__":
    unittest.main()
