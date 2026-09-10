"""Stage the Japanese Android host without changing the PAL application."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile

from .errors import BuildError
from .profiles import load_profiles
from .rmcj01 import JAPAN_WFC_PAYLOAD_SHA256


def audit_region(apk: Path) -> None:
    with ZipFile(apk) as archive:
        for name in archive.namelist():
            content = archive.read(name)
            # Upstream's WC24 seed contains two historical PAL download records,
            # not import gates. Exempt only the exact pinned resource bytes.
            if (name == "assets/wii/shared2/wc24/nwc24dl.bin" and
                    hashlib.sha256(content).hexdigest() ==
                    "057b6f840c19b41ce080318bc7e717e2b910965ce72ab781a7e319017636c38e"):
                continue
            if any(marker in content for marker in (
                b"RMCP01", b"RMCPD00", b"524d4350",
                b"80d18895b39c63bd80f457398bfcbb91b7d16ac116a41a88967e954080155b05",
            )):
                raise BuildError(f"Japanese APK retains a PAL import/save contract: {name}")


def validate_translation(translation: Path) -> None:
    report = json.loads((translation.parent / "preparation.json").read_text())
    config = (translation / "RuntimeConfig.h").read_text().upper()
    if report.get("region") != "J" or not all(
        re.search(rf"\b{name}\s*=\s*0X{address}U?\s*;", config)
        for name, address in (("SDA1_BASE", "8038C580"), ("SDA2_BASE", "8038E920"))
    ):
        raise BuildError("Expected a prepared Japanese translation graph and SDA bases")
    shards = (translation / "build_shards/shards.cmake").read_text()
    if "set(MKW_HAVE_RETRO_REWIND_SHARDS ON)" in shards:
        manifest = (translation.parent / "retro.yml").read_text()
        if "region: J" not in manifest or "module_link_base: 0x80398C60" not in manifest:
            raise BuildError("Expected Japanese Retro Rewind region and module link base")


def stage_android(repo: Path, output: Path, translation: Path) -> Path:
    validate_translation(translation)
    if not output.resolve().is_relative_to((repo / "private").resolve()):
        raise BuildError("Japanese Android host must stay in private/")
    host = output / "host/android"
    if host.exists():
        raise BuildError("Android host already exists; choose a fresh build tag")
    profiles = load_profiles(repo / "builder/profiles")
    pal = next(p.data for p in profiles if p.id == "mkwii-rmcp01-rev0")
    japan = next(p.data for p in profiles if p.id == "mkwii-rmcj01-rev0")
    replacements = {
        "RMCP": "RMCJ", "rmcp01": "rmcj01", "(PAL)": "(Japan)",
        "524d4350": "524d434a", "524D4350": "524D434A",
        pal["extraction"]["executables"]["dol"]["sha256"]:
            japan["extraction"]["executables"]["dol"]["sha256"],
        pal["retroRewind"]["payload"]["sha256"]: JAPAN_WFC_PAYLOAD_SHA256,
        f'PAYLOAD_BYTES = {pal["retroRewind"]["payload"]["bytes"]}L':
            "PAYLOAD_BYTES = 28992L",
        'applicationId = "dev.kartpad.android"':
            'applicationId = "dev.kartpad.rmcj01.android"',
        '<string name="app_name">KartPad</string>':
            '<string name="app_name">KartPad Japan</string>',
        '"${CMAKE_CURRENT_LIST_DIR}/../../../../.." ABSOLUTE)':
            f'"{repo}" ABSOLUTE)',
    }
    shutil.copytree(repo / "android", host, ignore=shutil.ignore_patterns(
        "build", ".gradle", ".kotlin", ".cxx", "local.properties", "libs"))
    for path in host.rglob("*"):
        if path.name == "CMakeLists.txt" or path.suffix in (".kt", ".kts", ".java", ".cpp", ".h", ".xml"):
            source = path.read_text()
            for old, new in replacements.items():
                source = source.replace(old, new)
            path.write_text(source)
    # Dependency preparation owns the pinned AAR; don't copy stale binaries.
    (host / "app/libs").symlink_to(repo / "android/app/libs", target_is_directory=True)
    return host


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--translation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        validate_translation(args.translation.resolve())
    else:
        stage_android(Path(__file__).resolve().parents[2], args.output.resolve(),
                      args.translation.resolve())


if __name__ == "__main__":
    main()
