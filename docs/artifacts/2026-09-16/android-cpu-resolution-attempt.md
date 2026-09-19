# CPU-context reuse and subnative resolution attempt

The owner selected CPU work reduction and lower resolution, and deferred PGO.
This experiment preserves Android API28 support and the existing 1× default.

## Changes

- Android scalar floating-point adapters reuse one validated CPU context across
  evaluation and commit. This adopts the earlier `535924a` experiment, with
  arithmetic and guest exception semantics unchanged. Local runtime commit:
  `5ced89d`.
- Android's Render Resolution menu adds 0.75× and 0.5×. Existing 1×–4× choices
  remain available. Preferences preserve valid existing values and reject
  non-finite values. The per-frame Android settings consumer now permits scales
  down to 0.5×. Local runtime commit: `a8b6889`.
- Apple runtime pins and Apple settings paths are unchanged. No PGO, native TLS,
  automatic memory trimming, worker-count or floating-point accuracy change.

Source inspection confirmed that framebuffer sizing, viewport/scissor mapping,
EFB-copy destination sizing and depth snapshot coordinates use target/logical
dimensions rather than requiring an integer scale. EFB RAM copies resample back
to guest dimensions. This supports the experiment but does not replace visual
and gameplay checks, especially effects and fine HUD detail at 0.5×.

## Executed checks

On the attached Pixel 9 Pro XL, the actual baseline/candidate scalar adapter
harness passed 448,000 differential cases, including special/random values,
guest FPSCR, host flags, rounding, suppressed writes, nested contexts and two
concurrent threads. The API28 ARM64 test executable uses O2 with strict FP flags.

A six-round alternating-order single-add microbenchmark reported paired time
reductions of 19.43%, -1.10%, 15.97%, 4.10%, 10.04% and 9.67% (median 9.86%).
This is one synthetic operation, not a game instruction mix, not thermally
controlled, and not an FPS result. One round was slower. It supports taking the
candidate into a game comparison, not advertising a 10% gameplay improvement.

The new executable framebuffer test exercises the actual renderer sizing code
at every offered scale, wide and portrait aspects, fractional rounding, tiny
dimensions and allocation limits. All 35 existing touch-overlay contracts pass.
The scalar harness also builds without modifying the maintained runtime tree;
it uses the preparation cache's SHA-256-verified sse2neon dependency.

Reproduce sizing checks with `scripts/test-android-subnative-resolution.sh`.
Reproduce scalar checks with `scripts/test-android-scalar-context.py`, supplying
the baseline header saved before the patch and an explicitly authorized ADB
target only when execution is intended. Raw private evidence stays under
`build/android-cpu-resolution/`.

## Comparison requirements

First compare baseline and CPU candidate at the same 1× resolution in a full,
demanding race. Builds must match native configuration, API target, settings,
assets and workload; the older API29 release-style private103 package is not a
matched control for an API28 debug candidate. Do not count a capped 60 FPS replay
as evidence that demanding races improved.

Then compare 1×, 0.75× and 0.5× within one binary, including a return to 1× to
expose temperature/cache drift. Capture actual render dimensions, warm shader
queue, game speed, frame-time windows, temperature and memory. Preserve the
owner's settings and saves. The phone was connected but locked during the
initial build; an unlock request was sent while independent work continued.

No new full-race performance gain is established by the checks above.

## Built and installed outcome

Private code105, `0.4.23-cpu-resolution-test`, is installed in place on the
attached Pixel. APK SHA-256:
`17075d5fb44d23971fc94502458c1a299c2b371c068d08204de3d740aaf6641e`.
The embedded provenance records clean KartPad source
`1012b27590b411197e08d3bbe20803c64022d1a8` and the prepared maintained runtime.
The full dual-game native target and Android application built successfully.
Package privacy/dependency/ABI/alignment audit and certificate verification
passed; the certificate matches the installed private103 preview. No uninstall
or app-data clear occurred.

This is an API28 debug test package, not a public release or a valid unmatched
FPS comparison against the older API29 release-style build. After installation,
before its first launch, 35 save, identity and settings files were archived and
their individual hashes verified against the phone. That verifies the current
backup, not a pre-install/post-install byte comparison. Existing NAND, Retro
Rewind save, identities and preferences are present. Game assets were not removed.

At the initial handoff the screen was behind the keyguard. The owner subsequently
unlocked it; see the hardware follow-up below for actual gameplay observations. Build artifacts,
package receipts, existing-package backup and private state archive are in
`build/android-cpu-resolution/`. No binary or runtime change was published.


## Unlocked hardware follow-up

The owner unlocked the Pixel and private105 launched Retro Rewind successfully.
Wild Woods 200cc VS with 12 racers rendered and accepted touch acceleration and
steering, but mostly ran near the 60 FPS cap in the observed warm interval. This
did not reproduce the slower-device reports. Two later captures named
`candidate-1x-stationary` and `candidate-half-stationary` had already reached the
post-race menu; both are excluded from performance conclusions.

A repeatable workload uses the bundled Wild Woods 150cc ghost replay, following
the moving racer through the track. Screenshots during and at the end of each
accepted capture establish that these measurements concern a moving race rather
than a menu. This is one racer, not a substitute for a demanding 12-racer test.

Matched control private106 was built with the same API28/debug configuration,
dependencies, translation and fractional-resolution changes. Its maintained
runtime is `1e9d397`, reverting only the CPU context change from `a8b6889`;
`ppc_runtime.h` is the only maintained-runtime file different between variants.
Control APK SHA-256:
`16ae274c9c38ee55f2c7af3cf462d7763f0e088ccded122cc3b5adcb92f1dfb2`.

Candidate private107 returns to runtime `a8b6889`, with source provenance
`390e11d4fad54156f3c4f9eadd5cfdf2952f43c4` (documentation-only change from the
private105 source). Its package audit passed. APK SHA-256:
`4476f3324d9ff089ab65e86e02547aeb6ac19becc36ac54a68ad18769c14fe84`.
Both updates installed in place successfully without clearing application data.


### Rejected performance workload

The owner correctly rejected the ghost workload: it omits the opponents and
item activity relevant to the reported slowdown. The ghost measurements are
functional checks only and must not be used to accept the CPU optimization or
claim improvement on slower devices. The initial two 1x captures were both
approximately 59.9 FPS; the return candidate was also capped. No meaningful
Android performance improvement is established. Additional ghost measurements
were stopped. The owner's original 2x resolution was restored through the UI.

Before further build comparisons, reproduce sustained slowdown in an actual
full race at the owner's settings and retain its course, mode, opponent count,
items, route and warm shader state. The historical Original N64 Sherbet Land
owner session is a lead, not a current reproduction: old logs recorded about
25-33 main-thread CPU ms per present in slow intervals, but subsequent runtime
changes prevent treating that old profile as today's bottleneck. Obtain a new
profile of a genuinely slow full-race interval before selecting another patch.
