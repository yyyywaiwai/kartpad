from __future__ import annotations

from runtime_sources import runtime_source, assert_runtime_staging, PLATFORMS
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class OfflineKdServicesContractTests(unittest.TestCase):
    def test_patch_gates_only_internet_devices(self) -> None:
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                patch = runtime_source(platform, 'runtime/src/hle/net/network_core.cpp')

                for local_service in (
                    '"/dev/net/kd/request"',
                    '"/dev/net/ncd/manage"',
                ):
                    self.assertIn(local_service, patch)
                self.assertIn("KD request/time and NCD are local Wii system services", patch)
                self.assertIn("if ((isIpTop || isSsl) && !RuntimeConfigFile::NetworkEnabled(true))", patch)
                self.assertNotIn("    if (!RuntimeConfigFile::NetworkEnabled(true))", patch)

    def test_common_runtime_preparation_applies_patch(self) -> None:
        for script_name in (
            "prepare-ios-game-runtime.sh",
            "prepare-g7-game-runtime.sh",
        ):
            script = (REPO / "scripts" / script_name).read_text()
            assert_runtime_staging(self, "macos" if "g7" in script_name else "ios")

        android_script = (REPO / "scripts/prepare-android-game-runtime.sh").read_text()
        self.assertIn("prepare-ios-game-runtime.sh", android_script)


if __name__ == "__main__":
    unittest.main()
