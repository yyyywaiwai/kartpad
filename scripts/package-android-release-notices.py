#!/usr/bin/env python3
"""Package allowlisted public notices/provenance beside the separately signed APK."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile

TAG = "v0.4.18-android.1"
VERSION = "0.4.18-android.1"
CODE = 83
# Exact candidate; changing notes must not relabel its compiled source as HEAD.
APPROVED_SOURCE = "c9d8a7fba9e5798e311570a605c61f336eab1169"
APPROVED_APK = "6eefdbe1d39627014595b9a6d50a79d0aab920eaf732a39ed8f6c5be362e9c9e"
APPROVED_AAB = "d351edf5a55ff9b61d262333a55bc1671951fa0da5f172bf37be0ba612a221ee"
APPROVED_SOURCE_ARCHIVE = "8d76c6fb45651cb6c5999176e6684ae4fa63c172a7a512627180aa2c274b2002"
APPROVED_NATIVE = {
    "lib/arm64-v8a/libSDL3.so": "d7a17c375adcb71818210581b885f59832d5f95b663aa7a7d493484a00a94753",
    "lib/arm64-v8a/libc++_shared.so": "c4c2fe5cbcb1fba0003a31fc7ab29a9bb12df6cc187ec45a806462540e83d93b",
    "lib/arm64-v8a/libkartpad_discio.so": "1d6c9fde69a3e4117987422bb6f0ebf41a40ec2de4945ebb7539b8a4b8e89207",
    "lib/arm64-v8a/libmain.so": "d4f0281b7d9b1b9761492fd3a5f735769c70c7fbb1829969e46fa5a729ba10be"
}
REPO = Path(__file__).resolve().parents[1]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("aab", type=Path, help="Audited local bundle; never copied to output")
    parser.add_argument("native_build", type=Path, help="Exact arm64-v8a CMake build containing _deps")
    parser.add_argument("--certificate-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, help="Write notices/checksums here without changing the APK directory")
    parser.add_argument("--source-archive", type=Path, required=True, help="Reviewed source delivery archive published beside the APK")
    args = parser.parse_args()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO, text=True).strip():
        parser.error("release packaging requires a clean source tree")
    if not re.fullmatch(r"[0-9a-f]{64}", args.certificate_sha256):
        parser.error("expected lowercase SHA-256 certificate fingerprint")
    if args.apk.name != f"KartPad-{TAG}-arm64.apk":
        parser.error("unexpected APK filename")
    if sha(args.apk.read_bytes()) != APPROVED_APK or sha(args.aab.read_bytes()) != APPROVED_AAB:
        parser.error("APK/AAB do not match the independently audited candidate")
    if sha(args.source_archive.read_bytes()) != APPROVED_SOURCE_ARCHIVE:
        parser.error("source archive does not match the independently reviewed delivery")
    with tarfile.open(args.source_archive, "r:gz") as source:
        members = source.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or any(not member.isfile() or member.name.startswith("/")
                                               or ".." in Path(member.name).parts for member in members):
            parser.error("unsafe or duplicate source archive member")
        source_manifest = json.load(source.extractfile("SOURCE-MANIFEST.json"))
        if source_manifest["applicationSources"]["android"] != APPROVED_SOURCE or source_manifest["androidAPK_SHA256"] != APPROVED_APK:
            parser.error("source delivery is not bound to the approved candidate")
        expected_files = source_manifest["files"]
        if set(names) != set(expected_files) | {"SOURCE-MANIFEST.json"}:
            parser.error("source delivery manifest coverage mismatch")
        for name, expected in expected_files.items():
            content = source.extractfile(name).read()
            if len(content) != expected["bytes"] or sha(content) != expected["sha256"]:
                parser.error("source delivery file differs from reviewed manifest")
    env = dict(os.environ, KARTPAD_ANDROID_EXPECTED_VERSION_NAME=VERSION,
               KARTPAD_ANDROID_EXPECTED_VERSION_CODE=str(CODE), KARTPAD_ANDROID_REQUIRE_RELEASE="1")
    env["JAVA_HOME"] = str(REPO / ".android-bootstrap/jdk-17.0.20.1+1/Contents/Home")
    for script, path in (("audit-android-bundle.sh", args.aab), ("audit-android-package.sh", args.apk)):
        subprocess.run([str(REPO / "scripts" / script), str(path.resolve())], env=env, check=True)
    sdk = Path(env.get("ANDROID_SDK_ROOT", env.get("ANDROID_HOME", str(Path.home() / "Library/Android/sdk"))))
    cert = subprocess.check_output([str(sdk / "build-tools/36.0.0/apksigner"), "verify",
                                    "--print-certs", str(args.apk)], env=env, text=True)
    fingerprints = re.findall(r"Signer #\d+ certificate SHA-256 digest: ([0-9a-f]+)", cert)
    if fingerprints != [args.certificate_sha256] or "CN=Android Debug" in cert:
        parser.error("signature does not match the single approved release identity")
    deps = args.native_build / "_deps"
    entries = {
        "LICENSE": REPO / "LICENSE",
        "INSTALL_ANDROID.md": REPO / "docs/INSTALL_ANDROID.md",
        "BUILD_ANDROID.md": REPO / "android/README.md",
        "RELEASE_NOTES.md": REPO / f"docs/releases/{TAG}.md",
        "SOURCE_DELIVERY.md": REPO / "docs/artifacts/2026-09-13/android-source-delivery.md",
        "SOURCE_RECONSTRUCTION.md": REPO / "docs/artifacts/2026-09-13/android-source-reconstruction.md",
        "RIGHTS_AND_LICENSES.md": REPO / "RIGHTS_AND_LICENSES.md",
        "THIRD_PARTY_NOTICES.md": REPO / "THIRD_PARTY_NOTICES.md",
        "dependencies.lock.json": REPO / "dependencies.lock.json",
        "LICENSES/GPL-3.0.txt": REPO / "LICENSES/GPL-3.0.txt",
        "ThirdPartyLicenses/Aurora-MIT.txt": REPO / "ref/upstream/Wiicompiled/aurora-main/LICENSE",
        "ThirdPartyLicenses/WiiCompiled-GPL-3.0.txt": REPO / "ref/upstream/Wiicompiled/LICENSE",
        "ThirdPartyLicenses/Dolphin-COPYING.txt": REPO / "ref/upstream/dolphin/COPYING",
        "ThirdPartyLicenses/Dolphin-Externals.md": REPO / "ref/upstream/dolphin/Externals/licenses.md",
        "ThirdPartyLicenses/Apache-2.0.txt": REPO / "ref/upstream/dolphin/Externals/Vulkan-Headers/LICENSES/Apache-2.0.txt",
        "ThirdPartyLicenses/Mbed-TLS.txt": REPO / ".android-bootstrap/dependencies/mbedtls-4.1.1/LICENSE",
        "ThirdPartyLicenses/Minizip-NG.txt": REPO / ".android-bootstrap/dependencies/minizip-ng-55db144e03027b43263e5ebcb599bf0878ba58de/LICENSE",
        "ThirdPartyLicenses/Dawn-BSD.txt": REPO / ".android-bootstrap/dependencies/Dawn-13abc3bc-LICENSE.txt",
    }
    for label, filename in {
        "Abseil-Apache-2.0.txt": "abseil-cpp-src/LICENSE",
        "FreeType.txt": "freetype-src/LICENSE.TXT",
        "FreeType-FTL.txt": "freetype-src/docs/FTL.TXT",
        "Tracy-BSD-3-Clause.txt": "tracy-src/LICENSE",
        "fmt-MIT.txt": "fmt-src/LICENSE",
        "imgui-MIT.txt": "imgui-src/LICENSE.txt",
        "libpng.txt": "png-src/LICENSE",
        "xxHash-BSD-2-Clause.txt": "xxhash-src/LICENSE",
        "zstd-BSD.txt": "zstd-src/LICENSE",
    }.items():
        entries[f"ThirdPartyLicenses/{label}"] = deps / filename
    data = {name: path.read_bytes() for name, path in entries.items()}
    data["ThirdPartyLicenses/FreeType-Credit.txt"] = (
        b"KartPad uses FreeType (https://freetype.org), under the included FreeType Project License.\n")
    if sha(data["ThirdPartyLicenses/Dawn-BSD.txt"]) != "e2908f7576fb12be5bdb8480cddb0be62badb498cadb821d043aeaf01b0b0899":
        parser.error("Dawn license does not match the release's pinned source")
    with zipfile.ZipFile(REPO / ".android-bootstrap/dependencies/SDL3-devel-3.4.4-android.zip") as sdl:
        data["ThirdPartyLicenses/SDL3-Zlib.txt"] = sdl.read("LICENSE.txt")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    with zipfile.ZipFile(args.apk) as apk:
        native = {n: sha(apk.read(n)) for n in apk.namelist() if n.startswith("lib/") and n.endswith(".so")}
    if native != APPROVED_NATIVE:
        parser.error("native libraries do not match the approved stripped candidate")
    with zipfile.ZipFile(args.apk) as apk, zipfile.ZipFile(args.aab) as aab:
        build = json.loads(apk.read("assets/kartpad-build.json"))
        if build.get("source_revision") != APPROVED_SOURCE or build.get("source_dirty") is not False:
            parser.error("candidate does not identify the approved clean source")
        for name in apk.namelist():
            if name.startswith(("lib/", "assets/")) and not name.startswith("assets/dexopt/"):
                if apk.read(name) != aab.read("base/" + name):
                    parser.error("APK payload differs from the audited AAB")
            elif re.fullmatch(r"classes(?:[0-9]+)?\.dex", name):
                if apk.read(name) != aab.read("base/dex/" + name):
                    parser.error("APK DEX differs from the audited AAB")
    # A later release tag may include notes and this packager, not changed app code.
    changed = subprocess.check_output(["git", "diff", "--name-only", APPROVED_SOURCE, commit],
                                      cwd=REPO, text=True).splitlines()
    packaging_files = ("README.md", "android/README.md", "scripts/package-android-release-notices.py",
                       "scripts/package-release-source.py", "scripts/restore-source-git.py",
                       "tools/android63-base-common-shards.json",
                       "tests/test_android_public_release_contract.py",
                       "scripts/audit-android-bundle.sh", "tests/test_android_bundle_audit_contract.py",
                       "tests/test_android_update_in_place_contract.py")
    if any(not name.startswith("docs/") and name not in packaging_files
           for name in changed):
        parser.error("packaging source differs from candidate beyond documentation/packager")
    provenance = {
        "schemaVersion": 2, "releaseTag": TAG, "sourceCommit": APPROVED_SOURCE,
        "packagingSourceCommit": commit, "embeddedBuildProvenance": build,
        "appVersion": VERSION, "versionCode": CODE, "package": "dev.kartpad.android",
        "apkSHA256": sha(args.apk.read_bytes()), "apkBytes": args.apk.stat().st_size,
        "aabSHA256": sha(args.aab.read_bytes()), "aabBytes": args.aab.stat().st_size,
        "signingCertificateSHA256": args.certificate_sha256, "nativeLibraries": native,
        "containsTranslatedGameCode": True, "containsGameData": False,
        "containsPrivateSigningMaterial": False, "maintainerAuthorizedFreeCommunityRelease": True,
        "upstreamRightsConfirmed": False, "profileableByShell": False, "debuggable": False,
        "physicalAcceptance": "Private code82 passed Preferred Game startup, persistence and return-to-menu checks on the owner phone; all 6319 protected files matched immediately after the in-place update. The owner then reported general gameplay works. Code83 retains identical native libraries and Android wrapper sources with release/version metadata changes. No Item Rain-specific, exact 0x807EF16C crash, completed-race count, online or affected-controller acceptance is inferred.",
        "sourceArchive": {"filename": args.source_archive.name, "bytes": args.source_archive.stat().st_size,
                          "sha256": sha(args.source_archive.read_bytes()),
                          "reconstruction": "Exact current Git snapshots, prepared Android runtime and pinned dependency source archives are supplied. Private translated game functions are regenerated from user-supplied inputs using delivered emitters and recipes. No new independent second-host or bit-identical rebuild claim."},
        "releaseTwin": "A private debug-signed twin of code83 has all 155 ZIP entries byte-identical to the public APK; only the signing block differs. This package comparison is not gameplay acceptance. No new code83 emulator result is claimed here.",
        "noticesSHA256": {n: sha(b) for n, b in sorted(data.items())},
    }
    data["PROVENANCE.json"] = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode()
    output_dir = args.output_dir or args.apk.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"KartPad-{TAG}-notices.zip"
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name, content in sorted(data.items()):
            if b"/Users/" in content or len(content) > 2_000_000:
                parser.error(f"unexpected private path or oversized notice: {name}")
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, content)
    with zipfile.ZipFile(output) as package:
        assert sorted(package.namelist()) == sorted(data) and package.testzip() is None
        for name, content in data.items():
            assert package.read(name) == content
    checksum_path = output_dir / "SHA256SUMS"
    with checksum_path.open("x") as checksums:
        for artifact in (args.apk, output, args.source_archive):
            checksums.write(f"{sha(artifact.read_bytes())}  {artifact.name}\n")
    print(f"Packaged {len(data)} allowlisted notices/provenance entries; no private inputs copied.")
    print(output)


if __name__ == "__main__":
    main()
