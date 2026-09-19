"""Exact identities for the accepted incremental iOS community release."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

RELEASE_TAG = "v0.4.24-ios.1"
APP_VERSION = "0.4.24"
APP_BUILD = "49"
COMPILED_SOURCE = "91aaedc7cff6c4e801cfe0636d5c3a4aa3b9bc2d"
EXECUTABLE_SHA256 = "f55c8b5853100c9a0ed156d93accd7c2b1818cae9f9ae485906ad4f138cb08f8"
RUNTIME_SHA256 = "9e82b15f855b7c2a6ff39b908f768a18a58e72a623bc8ddc3f7f8bb7b3f6f125"
TRANSLATION_SHA256 = "f5b67171325d4b98ccee74752268d689952d054f78f001b9083e42507dff8e0b"
COMPOSITION_SHA256 = "8f86f5db4804ca78f7d00ec3f7f09f23f5451bd4f8f296dfd425bb18b647dcf2"
REFRESHED_INPUTS_SHA256 = "612bce5bc068c02fd3e5775eb2149047ce9c0c37398665c1d8288f7066cd1a05"
FPS_RUNTIME_SHA256 = "ebd52bdf068382d0e3bcfad218c6116b854d8594d452dc00622f4bc6bfdbc16a"
PRODUCTION_PATHS = ("apple/ios", "apple/mobile", "apple/shared", "apple/third_party", "runtime/include")


def accepted_build(app: Path) -> dict:
    manifest = json.loads((app / "kartpad-build.json").read_text())
    composition_bytes = (app / "kartpad-ui-composition.json").read_bytes()
    composition = json.loads(composition_bytes)
    if hashlib.sha256(composition_bytes).hexdigest() != COMPOSITION_SHA256:
        raise ValueError("unexpected incremental compilation manifest")
    if manifest != composition["base_manifest"]:
        raise ValueError("base compilation manifest changed")
    if manifest.get("source_revision") != COMPILED_SOURCE or manifest.get("source_dirty") is not False:
        raise ValueError("expected the clean accepted base compilation source")
    if manifest.get("prepared_runtime", {}).get("sha256") != RUNTIME_SHA256:
        raise ValueError("unexpected prepared runtime hash")
    if manifest.get("translation", {}).get("sha256") != TRANSLATION_SHA256:
        raise ValueError("unexpected translation hash")
    if hashlib.sha256((app / "KartPad").read_bytes()).hexdigest() != EXECUTABLE_SHA256:
        raise ValueError("unexpected refreshed executable")
    return {
        "compiledBaseSourceCommit": COMPILED_SOURCE,
        "preparedRuntimeSHA256": RUNTIME_SHA256,
        "translationSHA256": TRANSLATION_SHA256,
        "compilationManifestSHA256": hashlib.sha256((app / "kartpad-build.json").read_bytes()).hexdigest(),
        "incrementalCompilationManifestSHA256": COMPOSITION_SHA256,
        "compilationScope": composition["scope"],
        "refreshedInputPaths": list(PRODUCTION_PATHS),
        "refreshedInputsEquivalent": True,
        "fullSourceRebuild": False,
    }


def verify_source_equivalence(repo: Path, packaging_commit: str) -> None:
    names = subprocess.check_output(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", packaging_commit, "--", *PRODUCTION_PATHS], text=True).splitlines()
    inputs = {name: hashlib.sha256(subprocess.check_output(["git", "-C", str(repo), "show", packaging_commit + ":" + name])).hexdigest() for name in names}
    actual = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if actual != REFRESHED_INPUTS_SHA256:
        raise ValueError("refreshed production inputs differ from compilation")

    runtime_source = repo / "vendor/runtimes/ios/runtime/src/settings_overlay.cpp"
    if hashlib.sha256(runtime_source.read_bytes()).hexdigest() != FPS_RUNTIME_SHA256:
        raise ValueError("FPS runtime source differs from compilation")
