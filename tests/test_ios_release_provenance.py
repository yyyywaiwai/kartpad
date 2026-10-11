import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("ios_release", Path(__file__).resolve().parents[1] / "scripts/ios_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class SourceEquivalenceTests(unittest.TestCase):
    def test_documentation_allowed_but_refreshed_source_header_or_asset_change_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            def git(*args):
                return subprocess.check_output(["git", "-C", temp, *args], stderr=subprocess.DEVNULL, text=True).strip()
            git("init"); git("config", "user.name", "Test"); git("config", "user.email", "test@example.invalid")
            names = ["apple/ios/UI.mm", "runtime/include/identity.h", "apple/ios/Assets.xcassets/icon.png"]
            for name in names:
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("accepted")
            original = release.COMPILED_SOURCE
            try:
                (repo / "README.md").write_text("release notes")
                git("add", "."); git("commit", "-m", "baseline")
                release.COMPILED_SOURCE = git("rev-parse", "HEAD")
                (repo / "docs").mkdir()
                (repo / "docs/release.md").write_text("notes")
                git("add", "."); git("commit", "-m", "documentation")
                release.verify_source_equivalence(repo, "HEAD")
                for name in names:
                    with self.subTest(name=name):
                        (repo / name).write_text("changed")
                        git("add", "."); git("commit", "-m", "changed input")
                        with self.assertRaisesRegex(ValueError, "changes inputs"):
                            release.verify_source_equivalence(repo, "HEAD")
                        (repo / name).write_text("accepted")
                        git("add", "."); git("commit", "-m", "restore")
            finally:
                release.COMPILED_SOURCE = original

    def test_tampered_full_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            app = Path(temp)
            (app / "kartpad-build.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "exact clean audited full build"):
                release.accepted_build(app)


if __name__ == "__main__":
    unittest.main()
