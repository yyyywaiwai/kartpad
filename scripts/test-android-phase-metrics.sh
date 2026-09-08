#!/usr/bin/env bash
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
out="$repo/.android-bootstrap/phase-metrics-tests"
mkdir -p "$repo/.android-bootstrap"
"${CXX:-clang++}" -std=c++20 -I"$repo/runtime/include" \
  "$repo/runtime/tests/android_phase_metrics_tests.cpp" -o "$out"
"$out"
