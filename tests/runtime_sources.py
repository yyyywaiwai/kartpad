"""Read the maintained runtime that preparation actually stages, never patch archives."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ("macos", "ios", "android", "tvos")


def runtime_source(platform: str, *paths: str) -> str:
    return "\n".join((ROOT / "vendor/runtimes" / platform / path).read_text() for path in paths)


def assert_runtime_staging(test, platform: str) -> None:
    common = (ROOT / "scripts/prepare-ios-game-runtime.sh").read_text()
    if platform == "macos":
        script = (ROOT / "scripts/prepare-g7-game-runtime.sh").read_text()
        test.assertIn("stage-maintained-runtime.py", script)
        test.assertIn("macos", script)
    else:
        test.assertIn("stage-maintained-runtime.py", common)
        test.assertIn("KARTPAD_PREPARE_PLATFORM", common)
        if platform != "ios":
            script = (ROOT / f"scripts/prepare-{platform}-game-runtime.sh").read_text()
            test.assertIn("prepare-ios-game-runtime.sh", script)
            test.assertIn(f"KARTPAD_PREPARE_PLATFORM={platform}", script)
