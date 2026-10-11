#!/usr/bin/env python3
"""Keep a small set of intentionally shared runtime files identical on all pins."""

from pathlib import Path

root = Path(__file__).resolve().parents[1] / "vendor/runtimes"
platforms = ("android", "ios", "macos", "tvos")
shared_files = (
    "runtime/include/hle/dvd_contract.h",
    "runtime/src/hle/egg_decomp.cpp",
    "runtime/src/hle/gx/gx_fifo.cpp",
    "runtime/src/hle/os/os_init.cpp",
    "runtime/src/hle/os/os_reset.cpp",
)

for relative in shared_files:
    contents = [(root / platform / relative).read_bytes() for platform in platforms]
    if any(data != contents[0] for data in contents[1:]):
        raise SystemExit(f"Shared runtime drift: {relative} differs across {', '.join(platforms)}")

print(f"PASS: {len(shared_files)} shared runtime files match across all four pins")
