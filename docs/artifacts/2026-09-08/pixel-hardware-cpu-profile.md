# Physical Pixel slowdown capture

Christopher offered the attached Pixel and then directly reported freezing /
slowdowns while playing the installed local 34b3de0 candidate. Installation,
state backup and certificate evidence remain in the runtime-investigation
worktree; no data was cleared and all 406 captured pre-game state files matched.

Pixel 9 Pro XL, Android17 API37, Vulkan, base profile, resolution1x, Fill Screen
(aspect mode2), renderer validation off. A captured interval reaches23.87 FPS,
p50 43.30ms, p95 50.69ms, p99 51.94ms with pipelines_queued=0. Prewarm completed
in45.1s. Early lower-FPS intervals also overlap compilation, but compilation
does not account for every low-FPS interval. No NetWait/NetStall entries occurred
in the captured console. Latest sampled thermal status1, battery39.3C; these
do not independently establish throttling or its causal contribution.

A20-second 99Hz cpu-clock simpleperf recording captured2,984 samples, zero lost.
Kernel symbols were restricted; no root or system setting was changed. Local
symbolization uses the exact candidate native build outputs. CPU distribution:
SDLThread67.96%, Thread-3 18.36%, app thread4.96%, RenderThread3.75%. Top self
costs include feclearexcept4.59%, XXH3 NEON accumulation3.55%, scalar flag capture
3.52%, emulated TLS lookup3.12%, pthread_getspecific2.51%. These percentages are
of sampled on-CPU work across threads, not wall time, GPU time or a direct
explanation of all stutters. The stack sample follows the owner report; it is
not claimed to isolate the exact24-FPS interval.

Verified build flags: command_processor and scalar helper O3; translated shards
O2 with no-fast-math and no-SLP-vectorize. The debug package is not equivalent
to an O0 native build; release/physical comparisons remain distinct.

Next bounded local investigation: semantically equivalent exception-clear
bookkeeping using the existing 520,000-case differential harness and FPSR/QC
tests, plus comparative benchmarks before integration. Do not remove IEEE or
guest FPSCR behavior based on sample cost alone. TLS/resource hashing remain
separate leads. No optimization is implemented or accepted at this checkpoint.

Evidence stays private under `/private/tmp/kartpad-runtime-investigation/build/investigation/hardware/`:
slowdown-console.log, slowdown-health.log, perf.data, cpu-report.txt,
cpu-threads.txt and build/source comparison output. Owner retains phone controls;
the fixed-duration host profiler has finished. No release or GitHub reply.

## Conditional exception clear experiment

Android ARM64 now uses a separate, opaque helper for pre-operation exception
clearing. It reads FPSR, masks only FE_ALL_EXCEPT and skips the write when
already clear, preserving QC and FPCR. Other platforms retain libc clearing.
The helper remains outside the arithmetic translation unit with no inlining.

On the physical Pixel, while the game was stopped at Christopher's request:
520,000 differential cases passed across four rounding modes (values, guest
FPSCR, destination writes and host flags); 512 FPSR states passed clearing and
capture with QC preservation. Apple Silicon host semantics passed 250,227
checks, state hash 0xccd5757c4c0643d4.

Six alternating-order microbenchmarks found clean-state clearing faster
(baseline 9.03–15.91 ns, candidate 6.60–8.36 ns) but dirty-state clearing
slower (baseline 11.54–13.91 ns, candidate 12.29–14.10 ns). A separate matched
Android baseline/candidate operation benchmark, four alternating-order rounds
of 100,000 operations each, measured median reductions of 6.1–8.7% for ten
common operations excluding the conversion, which improved 15.9%; double sqrt
was flat and single sqrt was 3.7% slower. These synthetic finite-input cases
are not a game instruction distribution or evidence of an FPS improvement.
Phone locked during the operation benchmark; thermal/frequency drift remains
a limitation despite alternating order. Raw data is retained privately in
`build/fenv-experiment/`. A matched game build and owner-controlled scene test
remain necessary; existing installed candidate remains unchanged at this point.

## Installed comparison candidate

Implementation a850ada, local debug 0.4.13-local.a850ada code25, ARM64 API28+.
Full fresh dual native build + release lint passed in10m6s (70 tasks,37executed,
18fromcache,15up-to-date). Initial attempt failed because the fresh worktree
lacked ignored SDL AAR; copying the same retained dependency resolved setup.
Prepared runtime source matches the prior candidate byte-for-byte; native helper
and translated compilation use this worktree, O3/O2 respectively, no LTO.
Package privacy/dependency/alignment audit and v2 signature verification passed.
APK SHA256 c68a3e8a0a7e7d27f5c2769490fe28a65896881512c4974591dd758adfe48eb7.
Retained in `build/fenv-experiment/candidates/` with exact input/test provenance.

Verified Pixel chooser with no game process, matched existing signing certificate,
and backed up429 state entries before in-place installation. Installation
succeeded; all406 regular state files remain identical immediately afterwards.
Package manager confirms code25 and exact version. Chooser reopened; Christopher
was asked to replay the same scene. No gameplay improvement is established yet.
App-only UID-filtered180-second log capture started; owner retains controls.
No public release, GitHub response, root/system setting change or IPA.

Linked ARM64 disassembly confirms PpcFmulsStateInline calls the new clear
helper before arithmetic and the existing capture helper afterward. The helper
contains MRS FPSR, exception-mask comparison and conditional MSR FPSR. It also
confirms two CurrentCpuContext calls per multiply (before evaluation and before
commit), matching a concrete follow-up to sampled TLS/context costs. This is
a separate lead; no context-lookup change was added to the comparison build.
Raw disassembly remains in `build/fenv-experiment/`.
