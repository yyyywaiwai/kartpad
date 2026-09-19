from __future__ import annotations

from runtime_sources import runtime_source, assert_runtime_staging
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class IOSLowLatencyAudioContractTests(unittest.TestCase):
    def test_audio_policy_uses_the_maintained_ios_runtime(self) -> None:
        assert_runtime_staging(self, "ios")

    def test_policy_is_ios_only_and_keeps_the_existing_fallback(self) -> None:
        patch = runtime_source('ios', 'runtime/src/audio_backend.cpp')

        self.assertIn("#if TARGET_OS_IOS", patch)
        self.assertIn('SDL_HINT_AUDIO_DEVICE_SAMPLE_FRAMES, "512"', patch)
        self.assertIn("constexpr uint32_t queueMs = 60", patch)
        self.assertIn("constexpr uint32_t queueMs = 120", patch)


if __name__ == "__main__":
    unittest.main()
