import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import json

spec = importlib.util.spec_from_file_location(
    "provenance", Path(__file__).resolve().parents[1] / "scripts/write-build-provenance.py")
provenance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provenance)


class BuildProvenanceTests(unittest.TestCase):
    def test_source_changes_and_privacy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            git("init")
            (root / "source.cpp").write_text("private fixture content")
            (root / ".gitignore").write_text("build/\n")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-m", "fixture")
            first = provenance.manifest(root)
            self.assertFalse(first["source_dirty"])
            self.assertIsNone(first["prepared_runtime"])
            self.assertIsNone(first["translation"])
            self.assertEqual(first, provenance.manifest(root))
            text = json.dumps(first)
            for private in (directory, "source.cpp", "private fixture content"):
                self.assertNotIn(private, text)
            (root / "build").mkdir()
            (root / "build/noise").write_text("ignored build output")
            self.assertEqual(first, provenance.manifest(root))
            (root / "source.cpp").write_text("modified source")
            second = provenance.manifest(root)
            self.assertTrue(second["source_dirty"])
            self.assertEqual(first["source_revision"], second["source_revision"])
            self.assertNotEqual(first["kartpad_source"], second["kartpad_source"])
            (root / "new.cpp").write_text("untracked new source")
            self.assertNotEqual(second["kartpad_source"], provenance.manifest(root)["kartpad_source"])
            (root / "source.cpp").unlink()
            self.assertTrue(provenance.manifest(root)["source_dirty"])

    def test_tree_is_location_independent_and_detects_input_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("a", "b"):
                (root / name).mkdir()
                (root / name / "input").write_bytes(b"same input")
            self.assertEqual(provenance.tree(root / "a"), provenance.tree(root / "b"))
            (root / "b/input").rename(root / "b/renamed")
            self.assertNotEqual(provenance.tree(root / "a"), provenance.tree(root / "b"))
            (root / "b/link").symlink_to(root / "a", target_is_directory=True)
            with self.assertRaises(ValueError):
                provenance.tree(root / "b")
            with self.assertRaises(ValueError):
                provenance.tree(root / "missing")


if __name__ == "__main__":
    unittest.main()
