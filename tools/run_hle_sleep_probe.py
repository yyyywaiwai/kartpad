#!/usr/bin/env python3
"""Compile actual prepared HLE bodies against explicit synthetic host seams.

No preparation, translated code, game data, or device operations. Prepared source
is read-only. Function bodies are copied verbatim, not reimplemented.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile


def function(text, signature):
    start = text.index(signature)
    opening = text.index("{", start)
    assert ";" not in text[start:opening], signature
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    parser.add_argument("--negative-control", action="store_true",
                        help="also verify rejection of a deliberately broken rollback")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    source = args.prepared / "src/hle/os"
    files = {name: (source / name).read_text() for name in
             ("os_sleep.cpp", "os_scheduler.cpp", "os_thread.cpp", "os_internal.h")}
    header = "\n".join(line for line in files["os_internal.h"].splitlines()
                       if not line.startswith('#include "') and line != "#pragma once")
    parts = [root.joinpath("hle_sleep_probe_shim.hpp").read_text(), header,
             root.joinpath("hle_sleep_probe_seams.inc").read_text()]
    helpers = [
        ("os_thread.cpp", "void UpdatePendingMaskForQueue(", True),
        ("os_thread.cpp", "void InsertThreadIntoQueueByPriority(", True),
        ("os_thread.cpp", "void RemoveThreadFromQueue(", True),
        ("os_scheduler.cpp", "void LinkThreadOnRunQueue(", False),
        ("os_scheduler.cpp", "void MarkRunQueuePending(", False),
        ("os_scheduler.cpp", "uint32_t PopThreadQueueHead(", False),
        ("os_scheduler.cpp", "static void TryInvokeSwitchCallback(", False),
        ("os_scheduler.cpp", 'extern "C" void SelectThread_801a9c08(CpuContext* ctx)\n{', False),
        ("os_scheduler.cpp", "static void WakeupThreadQueue(", False),
        ("os_scheduler.cpp", 'extern "C" void OSWakeupThread_HLE_801aaaa4(CpuContext* ctx)\n{', False),
        ("os_scheduler.cpp", "void OS_HLE_WakeupThreadNoReschedule(", False),
        ("os_sleep.cpp", "bool SchedulerCanSwitchAway(", False),
        ("os_sleep.cpp", "void ReportUnparkableSleep(", False),
        ("os_sleep.cpp", 'extern "C" void OSSleepThread_HLE_801aa9b8(CpuContext* ctx)\n{', False),
    ]
    for name, signature, internal in helpers:
        body = function(files[name], signature)
        parts.append(("namespace OsHleInternal {\n" if internal else "") + body +
                     ("\n}" if internal else ""))
    parts.append(root.joinpath("hle_sleep_probe_cases.inc").read_text())
    for name, contents in files.items():
        print(name, hashlib.sha256(contents.encode()).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory(prefix="kartpad-hle-sleep-") as temporary:
        cpp = Path(temporary) / "probe.cpp"
        exe = Path(temporary) / "probe"
        combined = "\n\n".join(parts)
        cpp.write_text(combined)
        command = ["clang++", "-std=c++20", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                   "-Wno-unused-const-variable", "-fsanitize=address,undefined",
                   str(cpp), "-o", str(exe)]
        subprocess.run(command, check=True)
        subprocess.run([str(exe)], check=True, timeout=15)
        if args.negative_control:
            clear = "            ::Memory::Write32(currentThread + kThreadQueueOffset, 0);"
            assert combined.count(clear) == 1
            cpp.write_text(combined.replace(clear, "/* deliberately broken rollback */"))
            subprocess.run(command, check=True)
            result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=15)
            assert result.returncode != 0 and "FAIL caller queue link leaked" in result.stderr
            print("PASS negative control: stale rollback link rejected", flush=True)


if __name__ == "__main__":
    main()
