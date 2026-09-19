from __future__ import annotations

from runtime_sources import runtime_source, assert_runtime_staging, PLATFORMS
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class AuroraViewportPolicyWindowGuardTests(unittest.TestCase):
    def test_policy_change_defers_viewport_reapply_until_window_exists(self) -> None:
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                patch = runtime_source(platform, "aurora-main/lib/dolphin/gx/GXAurora.cpp")
                self.assertIn(
                    "if (changed && aurora::window::get_sdl_window() != nullptr)",
                    patch,
                )
                self.assertIn("aurora::gx::set_logical_viewport", patch)
                self.assertIn("aurora::gx::set_logical_scissor", patch)

    def test_runtime_preparation_applies_window_guard(self) -> None:
        for script_name in (
            "prepare-g7-game-runtime.sh",
            "prepare-ios-game-runtime.sh",
        ):
            script = (REPO / "scripts" / script_name).read_text()
            assert_runtime_staging(self, "macos" if "g7" in script_name else "ios")


if __name__ == "__main__":
    unittest.main()
