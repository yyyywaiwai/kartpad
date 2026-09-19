from __future__ import annotations

import pathlib
from runtime_sources import runtime_source, assert_runtime_staging
import unittest


REPO = pathlib.Path(__file__).resolve().parents[1]


class MacOSCursorVisibilityContractTests(unittest.TestCase):
    def test_runtime_patch_removes_timer_hide_and_restores_cursor_for_settings(self) -> None:
        patch = runtime_source('macos', 'runtime/src/settings_overlay.cpp')
        self.assertIn("SDL_ShowCursor();", patch)
        self.assertNotIn("SDL_HideCursor();", patch)
        self.assertNotIn("UpdateCursorAutoHide();", patch)
        self.assertIn("SDL_ShowCursor();", patch)

    def test_macos_runtime_preparation_applies_cursor_patch(self) -> None:
        prepare = (REPO / "scripts/prepare-g7-game-runtime.sh").read_text()
        assert_runtime_staging(self, 'macos')


if __name__ == "__main__":
    unittest.main()
