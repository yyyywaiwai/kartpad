# Overnight maintenance and Android performance work

Final validation on September 22, after overnight work beginning September 21 at 23:25 JST. Public Android is
still **0.5.0 / code135**. None of the private profiling APKs below is a public
performance release. Apple build60 is a separate diagnostic-overhead mitigation.

## Issue review

All **63 open issues** have been read, classified and individually answered:
39 Android, 10 Apple, and 14 cross-platform/features or insufficient platform
detail. Follow-up evidence is being reviewed as it arrives. The
[issue inventory](open-issue-inventory.md) contains categories and reply links.
No ticket is closed on source tests alone, and repeated reporter evidence is
not being requested without a specific unresolved decision.

## Retained changes

| Change | Evidence | Remaining boundary |
|---|---|---|
| Android RVZ import through the picker descriptor | Full Zstd RVZ system-picker import on Pixel; all 2,043 extracted file hashes match; both saves and five preferences unchanged; descriptor/malformed-input probes pass | Normal167 Original/Retro course, short input and Retro background/resume checks pass; broader device/provider coverage remains |
| Bind internal native functions locally | Internal function jump slots reduced from 10,873 to zero; external imports and exports retained | No isolated FPS claim |
| Persist Dawn cache on backgrounding | Physical flush/relaunch and cache-hit evidence | Broader device/lifecycle coverage |
| Avoid unused vertex-format snapshot construction | 16,416 sanitizer-checked restore cases; physical profiles remove constructor samples | Small timing differences are workload-specific |
| Cache display-list CP-write effects | Same restore tests; ordered CP writes and cache invalidation retained | No independent overall FPS gain established |
| Resolve the audio sample TLS window once per voice | 786,432 sanitizer comparisons; ARM disassembly and two physical profiles remove per-sample TLS lookups | No general FPS or subjective audio-quality claim |
| Skip clocks for unused synthetic keys | 73,728 sanitizer-checked input comparisons; inactive 512-key poll uses zero clocks | Does not establish a fix for reported stale controller input |

Source is reviewable in [KartPad PR #315](https://github.com/chrissotraidis/kartpad/pull/315)
and [Android runtime PR #2](https://github.com/chrissotraidis/wiicompiled/pull/2).
The last source-changing root revision passed all three required CI jobs.

## Physical evidence and limits

Staff replay comparisons and short touch-driven Grand Prix movement were
recorded separately. Neither is represented as a human-completed race.
A private offline fixture subsequently completed a twelve-CPU Luigi Circuit
race and two Moo Moo Meadows races, with visible movement, items, lap progress
and results/post-race screens. Its cinematic camera differs from normal player
control. Code162's stationary-grid attempt is rejected.

The heavier fixture profiles expose roughly 13% of sampled self cycles in
scalar floating-point flag handling and roughly 5% in emulated TLS plus
`pthread_getspecific`. These are profiling shares, not attainable FPS gains.
Floating-point exception semantics remain unchanged. API28 remains the default;
fresh API29 and API28 CPU-fixture measurements overlap prior variation and
differ in thermal state, so no TLS-model speedup is established. A small audio
change resolves its existing thread-local sample window once per voice
instead of once per byte. Its 786,432 sanitizer-checked sample/state comparisons
pass; two physical captures remove the targeted lookup samples while whole-frame
timing remains within control variation.

The primary checkout and private game data are preserved. Private APKs, symbols,
recordings and save backups remain local. The CPU-driver marker has been removed. Normal code170 is now installed with
debugging and shell profiling disabled; its native library is identical to167.
The separate function-layout experiment did not establish a benefit and is not
included in170. Post-import save/settings readback
passed before that install. Normal167 loads Original and Retro licences/menus,
with short Original/Retro acceleration/pause/quit checks and a61-second Retro
background/resume cycle; this is not a completed
human-driven race or reporter-device acceptance.

For exact hashes, run counts, rejected candidates and current measurements, see
the [evidence ledger](evening-goal-loop.md). For the next engineering actions,
see the [Android handoff](../../ANDROID-PERFORMANCE-HANDOFF.md).

The [feature follow-up](feature-follow-up.md) records the remaining shake and Retro
ghost engineering scope; neither is claimed as implemented.

## Final normal-build checks

Normal170 is installed and its installed APK SHA-256 matches the audited local
artifact. Its DiscIO library is byte-identical to the one that passed the full
RVZ import. Original's ten-minute staff-replay observation kept the same process
and thermal status 0. In the retained final main-log segment (07:04:20–07:06:57), median reported
FPS was 60.015, but two intervals fell to
46.20/46.11 FPS with p99 frame times 125.52/129.76 ms. Their cause remains
unresolved. A 61.49-second Home/resume cycle returned to replay rendering with
the same process.

Retro loaded its existing licence and played the selected Rooster Island staff
ghost to its 2:42.292 results screen. Subsequent checkpoints show that
results overlay with the course scene still animating; this is not ten minutes of active racing. The game displayed a
ghost-created message. No fresh save readback is available from the final
non-debuggable build, and no byte-unchanged-save claim is made for this session.

The private function-layout experiment reduced the selected functions' static
page footprint but produced overlapping CPU medians (12.673/12.684 ms). It was
rejected as a default and is absent from normal170. No broad FPS improvement,
reporter-device resolution, or completed human-driven race is claimed.

The full Retro observation kept the same process and thermal status 0 for ten
minutes, including the results-overlay period. The phone was then returned to
a fresh launcher with both profiles ready and Ask Every Time preserved.
