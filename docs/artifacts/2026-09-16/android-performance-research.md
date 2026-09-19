# Android performance: research and decision, 2026-09-16

## Decision

Prioritize removal of repeated CPU bookkeeping in translated floating-point operations. First test the existing context-reuse candidate (PR #289) against current release code in demanding races. This is a concrete, portable change with correctness evidence, not a demonstrated gameplay speedup. Do not repeat the native-TLS experiment or describe memory recovery as an FPS fix.

Owner decision after this review: defer profile-guided optimization. Pursue CPU-context reuse and optional below-native resolution. Compare CPU reuse at a fixed resolution first, then compare resolution choices within the same binary.

There is still no evidence supporting a promised major across-device speedup. The strongest evidence identifies a CPU optimization direction; it does not prove that a small helper change can rescue a 10 FPS device.

## Evidence combined

| Observation | Meaning and limitation |
|---|---|
| Helio G85 report #198: warm 25–29 FPS, main occupancy 94–97%, present around 2.3–2.6 ms, compilation queue empty | Supports investigating CPU work. Occupancy is not a scheduler trace and present duration is not total GPU execution time. |
| POCO X3 #275: 10–11 FPS after compilation, present around 4 ms | More shader prewarming cannot explain or fix the whole sustained slowdown. Existing diagnostic log is sufficient to establish that distinction. |
| Earlier Pixel full-race capture: 23.87 FPS, p95 50.69 ms, queue empty | A real demanding workload exists. An accompanying profile shows floating-point bookkeeping, context access and hashing costs, but does not isolate that exact slow interval. |
| Earlier paused-camera comparison: 1× 45.1 versus 2× 44.7 presents/sec | Resolution alone did not restore speed there. Sequential, thermally unmatched measurements cannot exclude GPU bottlenecks elsewhere. |
| Builds 97/98/99 TLS A/B/A: 59.73/59.87/59.85 FPS in Boo Cinema replay | No useful speedup established; workload was already capped. Replacing TLS machinery is not equivalent to removing repeated lookups. |
| Manual memory probe: approximately 376 MiB allocator reservation and 397 MiB PSS reclaimed, live allocation unchanged | Real memory improvement; no demonstrated FPS or crash improvement. Retest course transitions and long sessions before automatic use. |
| New #296: POCO X7 Pro, build85, Wild Woods, 1×, first race, no attached log | Add this course to coverage; no defensible CPU/GPU/driver diagnosis yet. Requested a second-race diagnostic once. |

Source evidence: `docs/artifacts/2026-09-08/pixel-hardware-cpu-profile.md`, `docs/iterations/android-preview12-warm-performance.md`, and private retained `build/android-tls-comparison-20260915/hardware/{hardware-report,followup-20260915}.md` in the primary checkout. Public release 104 does not include the private manual memory probe. Older CPU profiles require refresh against current code before attributing current cost to a previously optimized function.

## What other Android games do, and what applies here

| Technique | KartPad assessment | Priority |
|---|---|---|
| Reduce repeated CPU work and improve data access | Current `runtime/include/ppc_runtime.h` scalar adapters fetch context for evaluation and again for commit. Reuse a single pointer across an operation, preserving all FPSCR and exception semantics. PR #289 already explores this; reuse its work rather than reinvent it. | First controlled candidate |
| Profile-guided compilation | No PGO configuration found in maintained runtime CMake. Train on full races, then compare an optimized, uninstrumented build. Preserve strict translated FP flags and opaque exception helpers. | Next independent experiment |
| Lower internal resolution | Android currently exposes and clamps 1×–4×. Try explicit 0.75× and 0.5× options. They render 56.25% and 25% of the 1× pixel count respectively, not equivalent promised FPS gains. Helps GPU-limited scenes; cannot remove guest CPU work. | Useful user option, conditional speed benefit |
| Resource budgets and release of unused reservations | Measured reclaim is credible. Release only at safe transitions after relevant GPU work completes. Avoid constant eviction and reallocation during races. | Stability candidate, separate acceptance |
| Cache textures and avoid redundant hashes | Already implemented: guest-write generations, static texture/palette caches, front-end cache and cached bind-group keys. Old XXH samples do not prove these fixes remain missing. | Profile current misses before further changes |
| Avoid synchronous readback | Depth snapshots are already requested/throttled and use asynchronous mapping. A generic “make readback async” change duplicates existing work. | Only investigate measured stalls |
| Shader caching/prewarming | Helps first encounters; cannot fix reports that remain slow with an empty queue. | Keep, not the main warm-race fix |
| Add worker threads | Safe independent jobs can help, but translated guest state, command ordering and readbacks impose dependencies. Need a trace showing a separable expensive job and synchronization cost first. | Do not globally parallelize guest execution |
| Frame pacing | Can improve cadence/latency. Swappy needs integration with Dawn's presentation ownership; cannot eliminate a 40–100 ms CPU workload. | Secondary |
| Thermal adaptation / scheduling hints | Potential sustained-load benefit; gate by OS support and actual thermal/scheduling evidence. Hints do not create CPU capacity. | Secondary, device-dependent |
| Frame skipping / lower frame cap | Must preserve simulation, audio, input, network and GPU side effects. A simple cap can slow game time. | Not a quick safe fix |
| Aggressive graphics accuracy shortcuts | EFB and texture shortcuts in other Wii implementations can break game behavior or graphics. Existing missing-character reports make correctness especially important. | Avoid blanket defaults |

### Exact implementation boundaries

Runtime inspected: Android gitlink `b57c59b89a059e0f7f93b18f86cc44d58f8e9adb` under `vendor/runtimes/android`.

- Context repetition: `runtime/include/ppc_runtime.h:25,52–65`. Compare helpers already reuse a context pointer. Retain guest exception enable handling, destination suppression, NI and status flags; do not replace semantics with fast math.
- Build: `runtime/cmake/PublicProducts.cmake` already uses O2 for translated code and O3 for common native code. This is not an unoptimized O0 build. Translated code deliberately retains `-fno-fast-math -ffp-contract=off`.
- Resolution: shell `KartPadActivity.kt:824`, preference `KartPadTouchSettings.kt:88`, native `runtime/src/main.cpp:1259` and `settings_overlay.cpp:1053,1077`. A UI-only change will be clamped away. Verify EFB copies, scissor rectangles, readback coordinates, HUD and touch input when changing actual scaling.
- Texture validation: `aurora-main/lib/gx/gx.cpp` uses write-generation validation before digesting sources. Depth readback: `aurora-main/lib/gfx/depth_peek.cpp` uses requested snapshots and asynchronous mapping.
- Resolve snapshot storage: `aurora-main/lib/gfx/common.cpp` retains grow-only per-frame-slot images. This is a bounded reuse strategy, not proof of a leak or explanation for all observed graphics memory. Measure dimensions, live bytes and reserved bytes separately.
- Automatic memory policy cannot depend solely on running-low-memory notifications: Android stopped delivering several running trim levels at API34. Use safe lifecycle opportunities and measured budgets, accounting for a paused game thread.

## Next comparison that can actually decide something

1. Freeze current baseline source, settings, package signer, game profile and asset versions. Preserve saves and install in place. Reproduce a slow full race before measuring a candidate.
2. Use Original N64 Sherbet Land with full opponents, Retro Rewind Wild Woods, and a holdout course. Keep a light replay only as a regression check. Separate cold shader compilation from warm repeated laps.
3. Capture current baseline scheduler trace and symbolized CPU samples alongside raw frame intervals, game speed, queue depth, memory, temperature and clocks. Distinguish running work from blocking; do not equate main occupancy with pure CPU execution or presents/sec with simulation speed.
4. Compare context reuse alone with baseline in alternating A/B/A order, several matched runs. Retain existing differential correctness tests and check gameplay, audio and geometry. A predefined target is at least 10% lower demanding-scene CPU/frame time or p95 without regressions; this is a decision threshold, not a prediction. Smaller reproducible wins can still be worthwhile but are not a breakthrough.
5. Train PGO separately on the representative corpus; merge profiles with the matching toolchain and compare the resulting uninstrumented build. Do not report the instrumented training build's FPS as candidate performance. Check a course excluded from training.
6. Independently compare 1×/0.75×/0.5×. A flat result deprioritizes resolution for that scene/device. A clear gain supports exposing the option while retaining the user's choice. Do not require every reporter to repeat tests before a local candidate demonstrates value.
7. Evaluate memory trimming across repeated course changes and a sustained session. A lower footprint earns a memory claim; only reduced stutters or eliminated reproduced failures earns a performance/stability claim.

If context reuse is negligible, stop iterating on TLS and use the current demanding-scene trace to select the next largest removable CPU cost. Do not keep testing a capped replay to justify a release.

## Primary research

- [Android optimization tips](https://developer.android.com/games/optimize/optimization-tips): select CPU versus GPU techniques from the bottleneck; lower rendering resolution addresses GPU work, not arbitrary game-thread cost.
- [Android profiling overview](https://developer.android.com/games/optimize): scheduler and workload evidence should guide optimization.
- [Google PGO guidance](https://developer.android.com/games/agde/pgo-overview): representative gameplay can guide compilation, but algorithm/data-layout improvements generally come first. Google's approximate 5% CPU-cost example is not a KartPad forecast; instrumented builds can be substantially slower.
- [Android frame pacing](https://developer.android.com/games/sdk/frame-pacing): presentation timing and queue behavior are separate from reducing simulation cost.
- [Android memory monitoring](https://developer.android.com/games/optimize/memory-monitoring) and [ComponentCallbacks2 reference](https://developer.android.com/reference/android/content/ComponentCallbacks2): lifecycle cleanup is useful; running trim notifications cannot be assumed on modern Android.
- [Performance Hint Manager](https://developer.android.com/ndk/reference/group/a-performance-hint) and [thermal adaptation](https://developer.android.com/games/optimize/adpf/thermal): scheduling and thermal feedback are conditional tools, not universal speed switches.
- [Dolphin performance guide](https://dolphin-emu.org/docs/guides/performance-guide/): resolution, CPU/GPU synchronization, shaders and accuracy tradeoffs are distinct. Its EFB and cache warnings demonstrate why shortcuts require game-specific validation. KartPad is a static recompiler, so Dolphin's emulated-clock and dual-core switches are not drop-in features.

## GitHub follow-through

Posted concise replies under the owner's account, using the existing evidence and avoiding unsupported fix claims:

- [#296 Wild Woods / POCO X7 Pro](https://github.com/chrissotraidis/kartpad/issues/296#issuecomment-5689422656): requested one second-race diagnostic, kept diagnosis open.
- [#295 ghost import/export](https://github.com/chrissotraidis/kartpad/issues/295#issuecomment-5689422989): clarified requested Original/RR coverage; no feature ETA.
- [#198 Helio G85](https://github.com/chrissotraidis/kartpad/issues/198#issuecomment-5689423404): explained negative TLS result and memory/FPS distinction; no duplicate log request.
- [#275 POCO X3](https://github.com/chrissotraidis/kartpad/issues/275#issuecomment-5689423762): acknowledged persistent post-compilation slowdown; no unsupported release recommendation.
- [#206 cellular online error86420](https://github.com/chrissotraidis/kartpad/issues/206#issuecomment-5689424206): distinguished successful login from later peer-connection failure; did not assign an unproven carrier or app cause.

Local receipts and exact bodies are retained under ignored `build/android-research-20260916/`. No new gameplay performance result, product-code change or APK is claimed by this research pass.
