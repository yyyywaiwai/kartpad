#!/usr/bin/env bash
set -euo pipefail
repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
test_dir="$(mktemp -d "${TMPDIR:-/tmp}/kartpad-subnative.XXXXXX")"
trap 'rm -rf "$test_dir"' EXIT
"${CXX:-c++}" -std=c++20 -Wall -Wextra -Werror \
  -I"$repo_root/vendor/runtimes/android/aurora-main/include" \
  "$repo_root/runtime/tests/android_subnative_resolution_tests.cpp" \
  -o "$test_dir/subnative"
"$test_dir/subnative"
