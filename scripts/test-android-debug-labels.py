#!/usr/bin/env python3
"""Keep Vulkan debug-utils labels out of release Android command buffers.

Issue #321: an Adreno 740 driver (512.676) faults inside
vkCmdEndDebugUtilsLabelEXT, reached from Aurora's overlay PopDebugGroup().
Every WebGPU debug-group/marker call must stay behind AURORA_GFX_DEBUG_GROUPS,
and no Android build input may define that macro.

usage: test-android-debug-labels.py [ANDROID_RUNTIME_ROOT]
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
runtime = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / "vendor/runtimes/android"
lib = runtime / "aurora-main/lib"
MACRO = "AURORA_GFX_DEBUG_GROUPS"
CALL = re.compile(r"\.(PushDebugGroup|PopDebugGroup|InsertDebugMarker)\(|"
                  r"wgpu\w*Encoder(PushDebugGroup|PopDebugGroup|InsertDebugMarker)\(")

failures = []
checked = 0
for path in sorted(lib.rglob("*.cpp")):
    stack = []  # one entry per open #if: does it require MACRO?
    for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        directive = line.strip()
        if directive.startswith("#if"):
            stack.append(MACRO in directive and "!" not in directive)
        elif directive.startswith("#el"):
            if stack:
                stack[-1] = False
        elif directive.startswith("#endif"):
            if stack:
                stack.pop()
        elif CALL.search(line):
            checked += 1
            if not any(stack):
                failures.append(f"{path.relative_to(runtime)}:{number}: {directive}")

for build_file in [root / "android/app/build.gradle.kts", root / "android/app/CMakeLists.txt",
                   runtime / "aurora-main/CMakeLists.txt"]:
    if build_file.exists() and MACRO in build_file.read_text():
        failures.append(f"{build_file}: defines or references {MACRO}")

if checked == 0:
    failures.append("no debug-group calls found; the scan no longer matches the source")
if failures:
    raise SystemExit("Ungated debug-utils label recording:\n" + "\n".join(failures))
print(f"PASS: {checked} debug-group/marker calls are gated by {MACRO}; Android builds do not define it")
