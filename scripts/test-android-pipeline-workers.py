#!/usr/bin/env python3
"""Run the real Android pipeline-worker gate against emulator and phone cases.

The API 29 emulator (Goldfish Vulkan) deadlocks when pipeline creation races
submission, so it keeps synchronous pipelines. Physical Android 9/10 phones must
keep compile workers; without them every new pipeline builds on the frame path
(issue #320, Mali-G51/API 29).

usage: test-android-pipeline-workers.py [ANDROID_RUNTIME_ROOT]
"""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
runtime = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / "vendor/runtimes/android"
source = (runtime / "aurora-main/lib/gfx/pipeline_cache.cpp").read_text()
start = source.index("static bool pipeline_workers_supported() {")
end = source.index("\n}\n", start) + 3
gate = source[start:end]

program = r'''
#define __ANDROID__ 1
#define PROP_VALUE_MAX 92
#include <cstdio>
#include <cstring>
static int g_api = 0;
static const char* g_hardware = "";
static int android_get_device_api_level() { return g_api; }
[[maybe_unused]] static int __system_property_get(const char* name, char* value) {
  if (std::strcmp(name, "ro.hardware") != 0) { value[0] = 0; return 0; }
  std::strncpy(value, g_hardware, PROP_VALUE_MAX - 1);
  return static_cast<int>(std::strlen(value));
}
''' + gate + r'''
struct Case { int api; const char* hardware; bool expected; };
int main() {
  const Case cases[] = {
    {29, "ranchu", false}, {29, "goldfish", false}, {28, "ranchu", false},
    {29, "kirin710", true}, {28, "mt6765", true}, {29, "", true},
    {30, "ranchu", true}, {33, "qcom", true},
  };
  int failures = 0;
  for (const Case& c : cases) {
    g_api = c.api; g_hardware = c.hardware;
    const bool actual = pipeline_workers_supported();
    if (actual != c.expected) {
      std::printf("FAIL api=%d hardware=%s expected=%d actual=%d\n", c.api, c.hardware, c.expected, actual);
      ++failures;
    }
  }
  if (!failures) std::printf("PASS: %zu pipeline-worker gate cases\n", sizeof(cases) / sizeof(cases[0]));
  return failures != 0;
}
'''

with tempfile.TemporaryDirectory() as directory:
    cpp = Path(directory) / "gate.cpp"
    exe = Path(directory) / "gate"
    cpp.write_text(program)
    subprocess.run(["c++", "-std=c++20", "-Wall", "-Werror", str(cpp), "-o", str(exe)], check=True)
    sys.exit(subprocess.run([str(exe)]).returncode)
