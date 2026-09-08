#!/usr/bin/env python3
"""Run the actual prepared SC override regression as ARM64 on a disposable emulator."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo))
from tests.test_sc_serial import HARNESS

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("prepared_source", type=Path)
parser.add_argument("--emulator", required=True)
args = parser.parse_args()
if not re.fullmatch(r"emulator-[0-9]+", args.emulator):
    parser.error("this fixture accepts only an explicitly selected disposable emulator")
sdk = Path(os.environ.get("ANDROID_SDK_ROOT", str(Path.home() / "Library/Android/sdk")))
adb = [str(sdk / "platform-tools/adb"), "-s", args.emulator]
if subprocess.check_output(adb + ["shell", "getprop", "ro.kernel.qemu"], text=True).strip() != "1":
    parser.error("target is not an emulator")
source = (args.prepared_source / "src/hle/sc.cpp").read_text()
override = re.search(r'extern "C" uint32_t SCGetProductSN_HLE\(uint32_t serialAddress\)\n\{.*?\n\}', source, re.S)
if override is None or "RuntimeScSerial::Write" not in override.group():
    parser.error("prepared source does not contain the fixed actual override")
compiler = sdk / "ndk/29.0.14206865/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android28-clang++"
with tempfile.TemporaryDirectory(prefix="kartpad-sc-serial-") as temporary:
    stage = Path(temporary)
    (stage / "test.cpp").write_text(HARNESS.replace("@OVERRIDE@", override.group()))
    binary = stage / "sc-serial-test"
    subprocess.run([str(compiler), "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-static-libstdc++", "-I", str(args.prepared_source / "include"),
                    str(stage / "test.cpp"), "-o", str(binary)], check=True)
    target = "/data/local/tmp/kartpad-sc-serial-test"
    subprocess.run(adb + ["push", str(binary), target], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(adb + ["shell", target], check=True)
    probe = subprocess.check_output(adb + ["shell", target, "--probe"], text=True)
    if probe.splitlines() != ["788600001", "788699999"]:
        raise SystemExit("ERROR: Android numeric serial probe did not preserve distinct identities")
    subprocess.run(adb + ["shell", "rm", target], check=True)
print("PASS: Android ARM64 prepared serial override; no app data or identity changed")
