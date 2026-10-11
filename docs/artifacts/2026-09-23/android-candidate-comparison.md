# Android candidate comparison — September 23, 2026

These are completed private Android experiments, not release notes or a claim that stutter is fixed. The final candidate is build195; Original measurements below extend through07:38JST, with separate Retro checks through07:55JST in the morning report.

## Workload and limits

Attached Pixel 9 Pro XL, Original Mario Kart Wii, GCN Cookie Land Balloon Battle, 2× rendering, Fill Screen, Mario / Standard Kart M / manual drift. The player remains stationary while 11 CPU players run the battle. These are **stationary battle observations**, not driven races. Teams, item activity and camera positions vary; thermal conditions and cache population are not identical. Online service acceptance is outside these measurements.

Private capture names containing `clean` denote a run without concurrent profiling, not cleared app data or shader caches. First-battle and warmed-battle observations are kept separate.

Each window uses 120 SurfaceFlinger polls, approximately 119 seconds of deduplicated displayed-frame timestamps. Screenshots occur before and after, not within the timed window. No CPU profiler runs during these captures. App FPS and compositor delivery are separate measurements.

## Warm battle observations

| Build | Difference | Displayed FPS | Intervals >25 ms | Intervals >40 ms | Display p99 (ms) | App median FPS | Guest CPU ms/present |
|---|---|---:|---:|---:|---:|---:|---:|
| 179 | Mailbox, default CPU scheduling | 56.500 | 415 | 5 | 33.343 | 59.88 | 14.709 |
| 180 | Mailbox, faster render cores | 57.628 | 287 | 0 | 33.335 | 59.96 | 14.824 |
| 181 | 180 + larger front cache | 56.432 | 427 | 1 | 33.342 | 59.92 | 14.736 |
| 182 | 181 + FIFO presentation | 59.923 | 13 | 1 | 16.803 | 59.97 | 14.779 |
| 183 | 182 + explicit scalar context | 59.831 | 25 | 0 | 16.829 | 60.06 | 14.865 |
| 184 | 183 + borrowed cached arrays | 59.864 | 21 | 0 | 16.838 | 60.01 | 14.726 |
| 185 | FIFO, baseline CPU/cache behavior | 59.181 | 102 | 0 | 33.305 | 59.86 | 14.731 |
| 186 | Matching 185 control, Mailbox | 56.592 | 403 | 2 | 33.340 | 59.88 | 14.798 |
| 188 | Guarded FIFO, wait diagnostics, baseline CPU/cache | 59.276 | 90 | 1 | 33.292 | 59.82 | 14.696 |
| 189 | 188 + faster render cores | 59.502 | 64 | 0 | 16.931 | 59.97 | 14.708 |
| 190 | 188 + 256-pipeline prewarm | 59.652 | 45 | 1 | 16.861 | 59.97 | 14.708 |
| 191 | 190 + inlined exact-input scalar path | 59.667 | 44 | 0 | 16.814 | 59.94 | 14.829 |
| 192 | 190 + outlined zero-aware scalar path | 59.403 | 75 | 1 | 33.239 | 59.91 | 14.833 |
| 193 | Original arithmetic, preserve_all helpers, 128 prewarm | 59.285 | 87 | 2 | 33.281 | 59.76 | 14.664 |
| 194 | Matching 193 control, original calling convention | 59.318 | 83 | 3 | 33.262 | 59.91 | 14.768 |
| 195 | Final normal candidate; after restored 2x resolution | 59.066 | 109 | 2 | 33.299 | 59.69 | 14.698 |
| 195 repeat | Following live resize and Home/resume checks | 59.419 | 74 | 0 | 33.234 | 59.71 | 14.785 |

App median FPS summarizes roughly 60-frame snapshots emitted every five seconds. Those snapshots leave gaps and can miss hitches; they are not whole-session statistics. Guest CPU is measured thread CPU time, not GPU execution time.

## Current decisions

- **Helper calling convention rejected for this candidate.** The 193/194 comparison does not establish a consistent whole-game gain beyond earlier variation. Final source retains the original calling convention.
- **Exact-input scalar fast paths rejected.** Builds 191 and 192 reduced time attributed to flag capture but did not improve total guest CPU or the warmed battle. Both grew native text by about 9 MB. Candidate 193 restores the original arithmetic.
- **CPU affinity rejected.** Build189 under FIFO was worse in its first battle and modestly better warmed; this does not establish a reliable gain. Home/resume again reset the masks. Removed helper and hooks from final source, retaining private experiments.
- **Larger display-list front cache is unaccepted.** It raises the direct lookup hit fraction, but build 181 did not demonstrate smoother delivery. Subsequent already-built packages retain it only to isolate their other changes.
- **256-pipeline prewarm rejected for the default.** Compared with 128, it adds startup work (3.2 versus 1.0 seconds in exported consoles) without a clear repeatable game gain. Final source returns to 128.
- **FIFO merits further testing.** First and warmed battle observations improved delivery on this Pixel. The exported build 182 console confirms FIFO was selected. Startup prewarm had 303/303 Dawn cache hits and rebuilt 126 pipelines in 0.7 seconds. Warm acquisition/total presentation averaged approximately 2.14/3.60 ms across report windows; these are not input-to-photon latency measurements.
- **Explicit scalar context, larger front cache and borrowed arrays rejected.** They did not establish gameplay improvement and have been removed from final source. Private comparisons remain reproducible.

Build 185 removes affinity, cache enlargement and borrowed arrays, retains FIFO and adds queue-age/deadline-lateness diagnostics. It uses the legacy generated graph. The matching Mailbox reversal in build 186 is complete. Warm FIFO delivered 59.181 FPS versus 56.592 with Mailbox, with 102 versus 403 display intervals over 25 ms. These are stochastic battle observations on one device, not a universal speedup.

## Buffering tradeoff

Warm 181 Mailbox had median desired-to-actual presentation delay 25.521 ms and frame-ready-to-actual delay 23.293 ms. Warm 182 FIFO measured 41.246 ms and 33.639 ms respectively. The improved cadence therefore comes with additional compositor buffering in these observations. This is not input-to-photon latency measurement, and the simpler 185/186 reversal confirms the same tradeoff: median frame-ready-to-actual delay was 32.606 ms with FIFO and 23.913 ms with Mailbox, a difference of approximately 8.7 ms.

A warm-185 screenshot also showed transient horizontal black bars near the lower HUD; before and later screenshots were clear. A later visual-only Mailbox186 recording reproduced the same bars during respawn transitions (verified in decoded frame4052). They are therefore not unique to FIFO; the large central blackout caught in 193 also reproduces in Mailbox186 frame4075. Whether their exact appearance matches original-game behavior has not been established. Do not claim a new FIFO rendering regression from this screenshot alone.

195 retains a **133.243 ms** displayed hitch, coinciding with a **123.000 ms persistent-pass pipeline wait** and 128.072 ms encoding maximum. Its warm capture followed a results-screen 2x-to-1x-to-2x change; it is not an uninterrupted-cache comparison. Native-rate FIFO improves cadence but does not eliminate graphics-pipeline stalls.

## Final candidate acceptance

Build195 was installed in place and its installed APK hash matches the archive. Three Original timing windows and two separate Retro offline battle windows completed. Original pause/resume, Home/resume and live resolution changes passed the bounded visual checks. Profiles opened and visible preferences were retained. Retro still has major pipeline-related hitches; see the [morning report](android-morning-report.md). Physical interpolation-mode changes, driven races, audio quality, other GPUs and subjective controller latency remain unaccepted. No public release follows from this loop.

Exact package hashes, source variants, build receipts, private evidence locations and chronological decisions are recorded in [the optimization ledger](android-optimization-loop.md). Private logs, symbols, screenshots, game data and device identifiers are not release attachments.
