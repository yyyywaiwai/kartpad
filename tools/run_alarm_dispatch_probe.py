#!/usr/bin/env python3
"""Exercise the actual prepared alarm dispatch guard at a synthetic fiber seam."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile
from run_hle_sleep_probe import function

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("prepared", type=Path)
parser.add_argument("--expect-blocked", action="store_true")
args = parser.parse_args()
tools = Path(__file__).resolve().parent
source = args.prepared / "src/hle/os"
alarm = (source / "os_alarm.cpp").read_text()
print("os_alarm.cpp", hashlib.sha256(alarm.encode()).hexdigest(), flush=True)
header = "\n".join(line for line in (source / "os_internal.h").read_text().splitlines()
                   if not line.startswith('#include "') and line != "#pragma once")
shim = (tools / "hle_sleep_probe_shim.hpp").read_text().split("namespace TranslatedFunctionRegistry")[0]
prefix = r'''
#include <mutex>
namespace RuntimeConfig { constexpr uint32_t SDA1_BASE = 0x8038c000; }
namespace TranslatedFunctionRegistry { bool FindByAddressPtr(uint32_t) { return true; } }
bool insideSwitch = false, nestedPumped = false, throwCallback = false, nestedRefused = false, retraceActive = false;
bool insideCallback = false, callbackPumped = false, outerPumped = false, switchSawOuterPump = false;
unsigned switches = 0;
bool VI_HLE_IsAdvancingRetrace() { return retraceActive; }
namespace OsHleInternal {
uint64_t ReadSystemTime() { return 100; }
}
bool Network_HLE_ProcessCompletions(CpuContext*) {
  if (insideCallback) callbackPumped = true;
  if (!insideCallback && !insideSwitch) outerPumped = true;
  if (insideSwitch) nestedPumped = true;
  return false;
}
bool NandProcessPendingCallbacks(CpuContext*, int) {
  if (insideCallback) callbackPumped = true;
  return false;
}
void func_801A0620(CpuContext*) { throw std::runtime_error("unexpected periodic alarm"); }
extern "C" void SelectThread_801a9c08(CpuContext* cpu) {
  if (Memory::Read32(kSchedulerIdleFlagAddr)) return;
  ++switches;
  switchSawOuterPump = outerPumped;
  Memory::Write32(kSchedulerReschedCounterAddr, 0);
  insideSwitch = true;
  ProcessAlarmQueue(cpu, 1); // A selected fiber immediately services its pending completion.
  insideSwitch = false;
}
void InvokeIndirectCpu(uint32_t, CpuContext* cpu) {
  if (throwCallback) throw std::runtime_error("synthetic callback exception");
  insideCallback = true;
  nestedRefused = !ProcessAlarmQueue(cpu, 1); // Same-callback recursion must stay suppressed.
  insideCallback = false;
  Memory::Write32(kSchedulerReschedCounterAddr, 1); // Callback wakes a runnable thread.
}
'''
scope = alarm[alarm.index("constexpr uint32_t kAlarmPrevOffset"):alarm.index("// Translated code can leave")]
parts = [shim, header, prefix, scope]
for signature in ("void EnsureSda1Base(", "void IncrementSchedulerDisableCount(",
                  "void DecrementSchedulerDisableCount(", "void RunDeferredReschedule(",
                  "void SanitizeAlarmQueue("):
    parts.append(function(alarm, signature))
parts.append(alarm[alarm.index("constexpr uint32_t kAlarmHandlerOffset"):alarm.index("bool IsLikelyCodeAddress")])
parts.append("namespace OsHleInternal {\n" + function(alarm, "bool ProcessAlarmQueue(CpuContext* cpu, int maxToProcess)\n{") + "\n}")
parts.append(r'''
void setup() {
  Memory::bytes.clear(); persistent = {};
  persistent.gpr[13] = RuntimeConfig::SDA1_BASE;
  const auto queue = RuntimeConfig::SDA1_BASE - kAlarmQueueOffsetFromR13;
  const uint32_t alarm = 0x80021000;
  Memory::Write32(queue, alarm); Memory::Write32(queue + 4, alarm);
  Memory::Write32(alarm, 0x80022000);
  insideSwitch = nestedPumped = throwCallback = nestedRefused = retraceActive = false; switches = 0;
  insideCallback = callbackPumped = outerPumped = switchSawOuterPump = false;
}
int main(int argc, char**) {
  try {
  setup();
  if (!ProcessAlarmQueue(&persistent, 1) || switches != 1 || !nestedRefused || callbackPumped)
    throw std::runtime_error("alarm callback/selection/reentry fixture not exercised");
  if (nestedPumped == (argc > 1)) throw std::runtime_error("unexpected completion progress");
  if (switchSawOuterPump == (argc > 1)) throw std::runtime_error("unexpected completion/switch order");
  std::cout << (nestedPumped ? "PASS selected fiber can pump completion\n" : "REPRO selected fiber completion blocked by live alarm guard\n");
  if (g_alarmProcessDepth != 0 || Memory::Read32(kSchedulerIdleFlagAddr) != 0)
    throw std::runtime_error("guard/count leaked");
  setup(); throwCallback = true;
  bool caught = false;
  try { ProcessAlarmQueue(&persistent, 1); } catch (const std::runtime_error&) { caught = true; }
  if (!caught || g_alarmProcessDepth != 0 || Memory::Read32(kSchedulerIdleFlagAddr) != 0 || switches)
    throw std::runtime_error("exception cleanup failed");
  std::cout << "PASS callback recursion blocked; exception unwinds guard/count\n";
  setup(); Memory::Write32(kSchedulerIdleFlagAddr, 1);
  ProcessAlarmQueue(&persistent, 1);
  if (switches || g_alarmProcessDepth || Memory::Read32(kSchedulerIdleFlagAddr) != 1 ||
      Memory::Read32(kSchedulerReschedCounterAddr) != 1)
    throw std::runtime_error("outer scheduler guard not preserved");
  setup(); retraceActive = true;
  ProcessAlarmQueue(&persistent, 1);
  if (switches || g_alarmProcessDepth || Memory::Read32(kSchedulerReschedCounterAddr) != 1)
    throw std::runtime_error("retrace guard not preserved");
  std::cout << "PASS outer scheduler/retrace guards keep reschedule pending\n";
  } catch (const std::exception& error) {
    std::cerr << "FAIL " << error.what() << '\n'; return 1;
  }
}
''')
with tempfile.TemporaryDirectory(prefix="kartpad-alarm-dispatch-") as directory:
    cpp, exe = Path(directory) / "probe.cpp", Path(directory) / "probe"
    cpp.write_text("\n\n".join(parts))
    subprocess.run(["clang++", "-std=c++20", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                    "-Wno-unused-const-variable", "-fsanitize=address,undefined", str(cpp), "-o", str(exe)], check=True)
    subprocess.run([str(exe)] + (["blocked"] if args.expect_blocked else []), check=True, timeout=10)
