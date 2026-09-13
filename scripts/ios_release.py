"""Identity and provenance checks for the accepted iOS community release."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import subprocess

RELEASE_TAG = "v0.4.17-ios.1"
APP_VERSION = "0.4.17"
APP_BUILD = "39"
COMPILED_SOURCE = "cf47944d1a841f60e7e774dd44e44dc99341fd92"
EXECUTABLE_SHA256 = "4d3035a322538c88f5d9412439fa8d7b471623cc9ef38c5fe637eecdaf077811"
RUNTIME_SHA256 = "8351179cbf2e3f6a89599448a3109d3a8d880c06bc7717f4362e6a81fda9c1c2"
TRANSLATION_SHA256 = "f5b67171325d4b98ccee74752268d689952d054f78f001b9083e42507dff8e0b"
# Compare production inputs, excluding release notes and packaging-only changes.
PRODUCTION_PATHS = (
    "apple/ios", "apple/mobile", "apple/shared", "apple/third_party",
    "runtime", "builder", "CMakeLists.txt",
    "scripts/prepare-ios-game-runtime.sh", "scripts/build-ios-device-game-app.sh",
    "scripts/inject-retro-rel-report-guard.py", "scripts/write-build-provenance.py",
    "scripts/generate-ios-icon-assets.sh", "scripts/verify-sunpad-overlay-snapshot.sh",
)
# The preparation script is itself compared, so its patch list must also match.
PRODUCTION_PATHS += tuple(
    "patches/" + name for name in sorted(set(re.findall(
        r"[A-Za-z0-9_-]+\.patch",
        (Path(__file__).parent / "prepare-ios-game-runtime.sh").read_text(),
    )))
)


def accepted_build(app: Path) -> dict:
    """Reject stale candidates while retaining the original compilation manifest."""
    manifest = json.loads((app / "kartpad-build.json").read_text())
    if manifest.get("source_revision") != COMPILED_SOURCE or manifest.get("source_dirty") is not False:
        raise ValueError("expected the clean accepted compilation source")
    if manifest.get("prepared_runtime", {}).get("sha256") != RUNTIME_SHA256:
        raise ValueError("unexpected prepared runtime hash")
    if manifest.get("translation", {}).get("sha256") != TRANSLATION_SHA256:
        raise ValueError("unexpected translation hash")
    if hashlib.sha256((app / "KartPad").read_bytes()).hexdigest() != EXECUTABLE_SHA256:
        raise ValueError("expected the hardware-accepted unsigned executable")
    return {
        "compiledSourceCommit": COMPILED_SOURCE,
        "preparedRuntimeSHA256": RUNTIME_SHA256,
        "translationSHA256": TRANSLATION_SHA256,
        "compilationManifestSHA256": hashlib.sha256((app / "kartpad-build.json").read_bytes()).hexdigest(),
        "productionInputPaths": list(PRODUCTION_PATHS),
        "productionInputsEquivalent": True,
    }


def verify_source_equivalence(repo: Path, packaging_commit: str) -> None:
    changed = subprocess.check_output(
        ["git", "-C", str(repo), "diff", "--name-only", COMPILED_SOURCE,
         packaging_commit, "--", *PRODUCTION_PATHS], text=True,
    ).strip()
    if changed:
        raise ValueError(f"production inputs differ from accepted compilation: {changed}")
