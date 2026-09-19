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
            inputs = {name: hashlib.sha256(b"accepted").hexdigest() for name in names}
            runtime_file = repo / "vendor/runtimes/ios/runtime/src/settings_overlay.cpp"
            runtime_file.parent.mkdir(parents=True)
            runtime_file.write_text("accepted")
            original_fps = release.FPS_RUNTIME_SHA256
            release.FPS_RUNTIME_SHA256 = hashlib.sha256(b"accepted").hexdigest()
            original = release.REFRESHED_INPUTS_SHA256
            release.REFRESHED_INPUTS_SHA256 = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            try:
                (repo / "README.md").write_text("release notes")
                git("add", "."); git("commit", "-m", "baseline")
                release.verify_source_equivalence(repo, "HEAD")
                for name in names:
                    with self.subTest(name=name):
                        (repo / name).write_text("changed")
                        git("add", "."); git("commit", "-m", "changed input")
                        with self.assertRaisesRegex(ValueError, "production inputs differ"):
                            release.verify_source_equivalence(repo, "HEAD")
                        (repo / name).write_text("accepted")
                        git("add", "."); git("commit", "-m", "restore")
                runtime_file.write_text("changed")
                with self.assertRaisesRegex(ValueError, "FPS runtime source differs"):
                    release.verify_source_equivalence(repo, "HEAD")
            finally:
                release.FPS_RUNTIME_SHA256 = original_fps
                release.REFRESHED_INPUTS_SHA256 = original

    def test_tampered_composition_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            app = Path(temp)
            (app / "kartpad-build.json").write_text("{}")
            (app / "kartpad-ui-composition.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "incremental compilation manifest"):
                release.accepted_build(app)


if __name__ == "__main__":
    unittest.main()
