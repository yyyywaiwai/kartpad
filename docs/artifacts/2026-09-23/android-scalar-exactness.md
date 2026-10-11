# Android scalar experiments — acceptance record

**Status:** both exact-input fast paths (191 and 192) are rejected. Their warmed battles did not improve total guest CPU versus 190, despite reducing samples attributed to exception capture. Candidate 192 outlines the evaluator and admits signed-zero operands; its first and warmed game comparisons did not establish a gain. Candidate 193 restored the original arithmetic and tested only the helper calling convention; that experiment is also excluded from the final candidate.

Candidate 191 adds an Android-only shortcut in `EvaluatePpcScalarBinary`. It retains the original opaque exception pre-clear, result finishing, guest FPSCR handling, rounding and destination-write rules. It skips the post-operation exception capture only when the binary64 arithmetic is provably exact. It does not use fast-math.

## Exactness argument

Both operands must be normal binary32 values represented exactly as binary64: encoded exponent 897 through 1150 inclusive, and all 29 low binary64 fraction bits zero. Each operand therefore has at most 24 significant bits. Their product needs at most 48 bits. Addition/subtraction with exponent difference at most 28 needs at most 53 bits including an addition carry. These fit binary64 exactly in every rounding mode. The operand exponent range prevents binary64 overflow or underflow, including cancellation; exact cancellation can produce signed zero.

Division, non-binary32 inputs, zero/subnormal inputs, NaN/infinity and wider addition/subtraction exponent gaps retain the unchanged fallback. Binary32 result rounding still occurs in the existing `FinishScalarFp`; the shortcut only proves the preceding binary64 operation exact. The compile guard is the existing Android full-runtime combined-FENV feature flag, so Apple semantics are unchanged.

## Validation and cost

The maintained differential test renames both adapter symbols and evaluator namespaces so the linker cannot silently coalesce the two variants. Physical tests compare result bits, guest FPSCR, destination-write decisions, host exception flags, raw ARM64 FPSR including QC preservation, nested CPU context and all four host rounding modes. Two concurrent test threads cover 2,240,000 cases per run with random binary64/binary32 values and boundary exponent gaps. The final maintained test passed on the attached Pixel. The macro-off portable arm64 contract also passed 250,227 checks.

Six alternating 10-million-call microbenchmark pairs favor eligible Add/Multiply, while wide-gap fallback adds a small cost. These are not game-FPS results. The generated library text grows 9,003,724 bytes, approximately 6.1 percent, versus 190. The completed warmed comparison showed 14.829 versus 14.708 ms of guest CPU per present, with essentially equal displayed FPS. This does not establish an overall improvement; the fast path has been removed from candidate 193.

## Outlined variant and helper calling convention

192 additionally accepts signed-zero operands, retaining actual arithmetic to preserve the sign rules, and prevents evaluator inlining on Android. It passed the same 2,240,000-case differential against the frozen original semantics. Native text still grew to 157,708,960 bytes, so outlining did not solve the code-size cost.

193 uses the original scalar arithmetic. Only the two opaque flag helpers use Clang’s AArch64 `preserve_all` calling convention, with matching declarations and definitions. The private prototype uses distinct baseline/candidate helper objects and passed 2,240,000 physical differential cases. The maintained test also passed. Exact-library disassembly confirms direct local helper calls and no dynamic relocations for them. The maintained FENV suite additionally passes 520,000 cases and 512 exception/QC states. A type-only generic benchmark hit Clang calling-convention template-mangling behavior; the archived candidate patch uses function-value templates for those standalone benchmarks. Production helper calls are direct. Full-game timing did not establish a reliable benefit. Candidate 193 first-battle guest CPU was 14.760 ms/present versus 14.725 for the matching original-calling-convention control 194; displayed FPS was 59.268 versus 59.309. Its warmed guest CPU difference remained within earlier run variation. Final candidate 195 retains the original arithmetic and calling convention. The experimental patch and corrected standalone tests remain private; the maintained differential coverage improvements remain in source.

## Reproduce the differential

The script compares the current checkout against the supplied baseline. To reproduce a historical experiment, first use its archived candidate header/source; running the script on the final checkout does not recreate 191.

Use the pre-change semantics header from root commit 927e01c and runtime adapter header from the maintained Android runtime commit 8a8f1c68b866bd8a87b6246fbe324d49a3d7ba3f as frozen baseline files. Prepare the pinned Android dependencies first, then run:

```sh
python3 scripts/test-android-scalar-context.py \
  --baseline-header /absolute/path/to/baseline-ppc_runtime.h \
  --baseline-semantics /absolute/path/to/baseline-ppc_semantics.h \
  --output build/exact-scalar-differential
```

Omitting `--serial` only builds. Supplying an explicitly authorized Android serial runs the standalone differential, without opening the game. Do not run it during game timing captures. Baseline files, test executable, compiler output and physical output for this loop are retained privately under `work/android-optimization-20260923`.
