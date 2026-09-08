#!/usr/bin/env bash
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
source "$repo/scripts/android-toolchain-versions.sh"
sdk="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-$HOME/Library/Android/sdk}}"
cxx="$sdk/ndk/$KARTPAD_ANDROID_NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android28-clang++"
adb="$sdk/platform-tools/adb"
out="$repo/.android-bootstrap/fenv-tests"
mkdir -p "$out"
flags=(-std=c++20 -O2 -fno-fast-math -ffp-contract=off -fno-slp-vectorize -I"$repo/runtime/include")
"$cxx" "${flags[@]}" -Dkartpad=reference -DTEST_ENTRY=ReferenceFp \
  -c "$repo/runtime/tests/android_fenv_case.cpp" -o "$out/reference.o"
"$cxx" "${flags[@]}" -DKARTPAD_ANDROID_COMBINED_FENV=1 -DTEST_ENTRY=CandidateFp \
  -c "$repo/runtime/tests/android_fenv_case.cpp" -o "$out/candidate.o"
"$cxx" "${flags[@]}" -static-libstdc++ \
  "$repo/runtime/tests/android_fenv_differential.cpp" \
  "$repo/runtime/src/android/scalar_fenv.cpp" "$out/reference.o" "$out/candidate.o" \
  -o "$out/differential"
# No root, system settings, package changes, saves or game inputs are involved.
"$repo/scripts/check-android-physical-device.sh" >/dev/null
"$adb" -d push "$out/differential" /data/local/tmp/kartpad-fenv-differential >/dev/null 2>&1
"$adb" -d shell /data/local/tmp/kartpad-fenv-differential
"$cxx" "${flags[@]}" -static-libstdc++ \
  "$repo/runtime/tests/android_fenv_capture_tests.cpp" \
  "$repo/runtime/src/android/scalar_fenv.cpp" -o "$out/capture-tests"
"$adb" -d push "$out/capture-tests" /data/local/tmp/kartpad-fenv-capture-tests >/dev/null 2>&1
"$adb" -d shell /data/local/tmp/kartpad-fenv-capture-tests
