import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("ios_release", Path(__file__).resolve().parents[1] / "scripts/ios_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class SourceEquivalenceTests(unittest.TestCase):
    def test_documentation_allowed_but_runtime_change_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            def git(*args):
                return subprocess.check_output(["git", "-C", temp, *args], stderr=subprocess.DEVNULL, text=True).strip()
            git("init")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            (repo / "runtime").mkdir()
            (repo / "runtime/code.cpp").write_text("accepted")
            git("add", "."); git("commit", "-m", "accepted")
            original = release.COMPILED_SOURCE
            release.COMPILED_SOURCE = git("rev-parse", "HEAD")
            try:
                (repo / "README.md").write_text("release notes")
                git("add", "."); git("commit", "-m", "documentation")
                release.verify_source_equivalence(repo, "HEAD")
                (repo / "runtime/code.cpp").write_text("changed")
                git("add", "."); git("commit", "-m", "runtime")
                with self.assertRaisesRegex(ValueError, "production inputs differ"):
                    release.verify_source_equivalence(repo, "HEAD")
            finally:
                release.COMPILED_SOURCE = original


if __name__ == "__main__":
    unittest.main()
