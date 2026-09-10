from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from kartpad_builder.errors import BuildError
from kartpad_builder.rmcj01 import JAPAN_WFC_PAYLOAD_SHA256
from kartpad_builder.rmcj01_android import audit_region, stage_android, validate_translation


REPO = Path(__file__).resolve().parents[1]


class JapaneseAndroidTests(unittest.TestCase):
    def test_region_audit_rejects_pal_code_and_modified_seed(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / "test.apk"
            with ZipFile(apk, "w") as archive:
                archive.writestr("classes.dex", b"RMCJ01 524d434a")
            audit_region(apk)
            for name in ("classes.dex", "lib/arm64-v8a/libkartpad_discio.so",
                         "assets/wii/shared2/wc24/nwc24dl.bin"):
                with ZipFile(apk, "w") as archive:
                    archive.writestr(name, b"RMCP01")
                with self.assertRaises(BuildError):
                    audit_region(apk)

    def test_isolated_host_and_translation_guards(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            shutil.copytree(REPO / "android", repo / "android", ignore=shutil.ignore_patterns(
                "build", ".gradle", ".kotlin", ".cxx", "libs"))
            shutil.copytree(REPO / "builder/profiles", repo / "builder/profiles")
            graph = repo / "private/translation-source/translation"
            (graph / "build_shards").mkdir(parents=True)
            report = graph.parent / "preparation.json"
            report.write_text(json.dumps({"region": "J"}))
            config = graph / "RuntimeConfig.h"
            config.write_text("SDA1_BASE = 0x8038C580u; SDA2_BASE = 0x8038E920u;")
            shards = graph / "build_shards/shards.cmake"
            shards.write_text("set(MKW_HAVE_RETRO_REWIND_SHARDS OFF)\n")
            output = repo / "private/android-test"
            host = stage_android(repo, output, graph)
            sources = host / "app/src/main/java/dev/kartpad/android"
            storage = (sources / "KartPadGameDataStorage.kt").read_text()
            self.assertIn('"RMCJ01".toByteArray()', storage)
            self.assertIn("1b9621ef7c5d97dada103e50e5389730e67f3c2545dda592edd4b5843655af91", storage)
            for name in ("KartPadSaveStorage.kt", "KartPadIdentityStorage.kt"):
                self.assertIn("524d434a/data/rksys.dat", (sources / name).read_text())
            self.assertIn("RetroWFC/RMCJ/rksys.dat", (sources / "KartPadIdentityStorage.kt").read_text())
            release = (sources / "RetroRewindRelease.java").read_text()
            self.assertIn("payload?g=RMCJD00", release)
            self.assertIn(JAPAN_WFC_PAYLOAD_SHA256, release)
            self.assertIn("PAYLOAD_BYTES = 28992L", release)
            native = (host / "app/src/main/cpp/kartpad_discio_jni.cpp").read_text()
            self.assertIn('GetGameID(partition) != "RMCJ01"', native)
            self.assertIn("Java_dev_kartpad_android_", native)
            gradle = (host / "app/build.gradle.kts").read_text()
            self.assertIn('applicationId = "dev.kartpad.rmcj01.android"', gradle)
            self.assertIn('namespace = "dev.kartpad.android"', gradle)
            self.assertIn(f'"{repo}" ABSOLUTE)', (host / "app/src/main/cpp/CMakeLists.txt").read_text())
            self.assertEqual((host / "app/libs").readlink(), repo / "android/app/libs")
            for path in host.rglob("*"):
                if path.suffix in (".kt", ".java", ".cpp"):
                    self.assertNotIn("RMCP", path.read_text(), str(path))
            # The checked-in PAL app is byte-for-byte unchanged by staging.
            for path in (repo / "android").rglob("*"):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (REPO / path.relative_to(repo)).read_bytes())
            with self.assertRaises(BuildError):
                stage_android(repo, output, graph)
            with self.assertRaises(BuildError):
                stage_android(repo, repo / "public", graph)
            report.write_text(json.dumps({"region": "P"}))
            with self.assertRaises(BuildError):
                validate_translation(graph)
            report.write_text(json.dumps({"region": "J"}))
            config.write_text("SDA1_BASE = 0x8038CC00; SDA2_BASE = 0x8038EFA0;")
            with self.assertRaises(BuildError):
                validate_translation(graph)
            config.write_text("SDA1_BASE = 0x8038C580u; SDA2_BASE = 0x8038E920u;")
            shards.write_text("set(MKW_HAVE_RETRO_REWIND_SHARDS ON)\n")
            manifest = graph.parent / "retro.yml"
            manifest.write_text("region: J\nmodule_link_base: 0x803992E0\n")
            with self.assertRaises(BuildError):
                validate_translation(graph)
            manifest.write_text("region: J\nmodule_link_base: 0x80398C60\n")
            validate_translation(graph)


if __name__ == "__main__":
    unittest.main()
