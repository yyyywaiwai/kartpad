#!/usr/bin/env bash
# Compare Android scalar FP semantics with and without KARTPAD_ANDROID_UNOBSERVED_FP_STATUS.
# Usage: tests/native/fp_status_differential/run.sh <baseline-git-rev> [cases]
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"
out="$(mktemp -d)"
git -C "$repo" show "${1:?baseline revision}:runtime/include/kartpad/semantics/ppc_semantics.h" > "$out/baseline_ppc_semantics.h"
here="$repo/tests/native/fp_status_differential"
flags=(-std=c++20 -O2 -fno-fast-math -ffp-contract=off -fno-slp-vectorize -DKARTPAD_ANDROID_COMBINED_FENV=1)
clang++ "${flags[@]}" -DVARIANT_HEADER="\"$out/baseline_ppc_semantics.h\"" -DVARIANT_FN=baseline_eval \
  -Dsemantics=baseline_semantics -c "$here/variant.cpp" -o "$out/baseline.o"
clang++ "${flags[@]}" -DKARTPAD_ANDROID_UNOBSERVED_FP_STATUS=1 \
  -DVARIANT_HEADER="\"$repo/runtime/include/kartpad/semantics/ppc_semantics.h\"" -DVARIANT_FN=candidate_eval \
  -Dsemantics=candidate_semantics -c "$here/variant.cpp" -o "$out/candidate.o"
clang++ -std=c++20 -O2 -fno-fast-math "$here/main.cpp" "$out/baseline.o" "$out/candidate.o" -o "$out/fpdiff"
"$out/fpdiff" "${2:-3000000}"
