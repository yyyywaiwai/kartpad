"""Tracked-source staging with actual Git and rsync, without invoking dotnet."""
import importlib.util
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/stage-maintained-translator.py"
SPEC = importlib.util.spec_from_file_location("translator_staging", SCRIPT)
STAGING = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STAGING)


class MaintainedTranslatorStagingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name) / "repo"
        self.source = self.repo / "vendor/wiicompiled"
        self.source.mkdir(parents=True)
        self.destination = Path(temporary.name) / "stage"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.project = "translator/src/Translator.Cli"
        self.write(f"{self.project}/Translator.Cli.csproj", "<Project/>\n")
        self.write(f"{self.project}/Main.cs", "original\n")
        self.write("runtime/src/native_registration.cpp", "native baseline\n")
        self.write("translator/generate.sh", "#!/bin/sh\n")
        (self.source / "translator/generate.sh").chmod(0o755)
        self.add()

    def write(self, relative, text):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def add(self):
        subprocess.run(["git", "-C", str(self.repo), "add", "vendor/wiicompiled"], check=True)

    def test_untracked_source_and_private_files_are_excluded(self):
        self.write(f"{self.project}/Unexpected.cs", "untracked code\n")
        self.write("private.key", "private material\n")
        STAGING.stage(self.repo, self.destination)
        self.assertFalse((self.destination / self.project / "Unexpected.cs").exists())
        self.assertFalse((self.destination / "private.key").exists())
        self.assertEqual((self.destination / "runtime/src/native_registration.cpp").read_text(), "native baseline\n")

    def test_dirty_and_newly_added_source_and_modes_are_preserved(self):
        self.write(f"{self.project}/Added.cs", "added\n")
        self.add()
        self.write(f"{self.project}/Main.cs", "working tree edit\n")
        STAGING.stage(self.repo, self.destination)
        self.assertEqual((self.destination / self.project / "Main.cs").read_text(), "working tree edit\n")
        self.assertEqual((self.destination / self.project / "Added.cs").read_text(), "added\n")
        self.assertEqual(stat.S_IMODE((self.destination / "translator/generate.sh").stat().st_mode), 0o755)

    def test_removed_source_is_cleaned_and_existing_build_caches_survive(self):
        self.write("translator/old/Removed.cs", "obsolete\n")
        self.add()
        STAGING.stage(self.repo, self.destination)
        # Include a cache under a removed source directory, a current project,
        # and a stale untracked C# file from the old whole-directory copier.
        caches = ["translator/old/bin/old.dll", f"{self.project}/bin/Release/app.dll",
                  f"{self.project}/obj/project.assets.json"]
        for relative in caches:
            path = self.destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("keep cache\n")
        stale = self.destination / self.project / "UntrackedFromOldStage.cs"
        stale.write_text("stale source\n")
        (self.source / "translator/old/Removed.cs").unlink()
        (self.source / self.project / "Main.cs").unlink()
        # One deletion remains unstaged, the other is reflected in the Git index.
        subprocess.run(["git", "-C", str(self.repo), "add", "-u", "vendor/wiicompiled/translator/old"], check=True)
        STAGING.stage(self.repo, self.destination)
        for relative in ("translator/old/Removed.cs", f"{self.project}/Main.cs", f"{self.project}/UntrackedFromOldStage.cs"):
            self.assertFalse((self.destination / relative).exists(), relative)
        for relative in caches:
            self.assertEqual((self.destination / relative).read_text(), "keep cache\n", relative)


if __name__ == "__main__":
    unittest.main()
