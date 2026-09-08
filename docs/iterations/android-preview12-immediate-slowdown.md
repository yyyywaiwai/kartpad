# Preview 12: immediate slowdown reproduction

2026-09-07, approximately 14:35–14:51 JST. Installed code 17, source `d057da9`.
This is a diagnostic checkpoint, not a new build or performance acceptance.
The user's short Original session reproduced the problem; a 15/30-minute test
is not a prerequisite for investigating it.

## Preserved evidence

The current run's explicit private diagnostic ZIP passed integrity verification.
Native performance records were correlated with nearby health samples using
elapsed time from the same device boot and this specific runtime process.
The raw ZIP, app-scoped logcat, screenshots, CPU profiles and system snapshots
remain in ignored local storage. Nothing was uploaded. No serial is recorded here.

| Interval ending (JST) | 300-present interval rate | Main CPU ms per presented frame | Nearby OS thermal status |
| --- | ---: | ---: | ---: |
| 14:35:35.701 | 36.67/s | 20.50 | 0 |
| 14:36:05.710 | 54.85/s | 15.70 | 0 |
| 14:36:56.607 | 32.48/s | 26.57 | 1 |
| 14:37:18.520 | 25.59/s | 32.98 | 1 |
| 14:37:30.251 | 25.57/s | 33.16 | 1 |

The app's rolling one-second counter reached 24.98 FPS. The table instead divides
the present-count increment by the matching CPU telemetry interval; it does not
mix that longer interval with the rolling FPS estimate. CPU ms is measured main
thread CPU-time delta divided by successful presents, not GPU time or a direct
measurement of each guest simulation tick. Its minimum useful 60 Hz comparison
is the 16.67 ms wall-time budget, but it must not be treated as proof that all
guest ticks and presents have an identical one-to-one relationship.

Severe slowdown already appears with OS status 0 and battery 36.6 C. Later status
1 accompanies battery 37.6 C and headroom around 0.80–0.82. Therefore the evidence
does not support overheating as the sole explanation. Status 0 also does not
prove the CPU/GPU clocks were unrestricted. The device was charging.

## What profiling narrows down

A separate 30-second **guest-paused** sample retained 15,293 samples, none lost.
Approximately 72.84% of app user-cycle samples were on the main runtime thread,
19.35% on the graphics worker. Significant main-thread leaf shares of the entire
sample include GX display-list processing 4.10%, scalar flag capture 3.49%,
`feclearexcept` 3.36%, emulated TLS 2.91%, GX FIFO processing 2.39%, current CPU
context lookup 2.30%, and scalar FP completion 2.07%. These paused leaf shares
are not a breakdown of the preceding active race or proof of one culprit.

The same paused camera was compared at the unchanged 2x render resolution:

- Original 4:3: 1,800 presents / 43.562 s = 41.32/s.
- Fill Screen: 2,100 presents / 47.180 s = 44.51/s.
- Separate equally instrumented 25-second samples reported main-thread
  cycle/runtime estimates of 1.329 and 1.338 GHz, respectively. These are not
  evidence of a fixed clock cap or a promise that forcing a different core works.
- The health worker consumed approximately 4–5 ms CPU over 25 seconds. Its new
  coarse background logging is not a substantial source of the measured load.

This sequential comparison does not establish that fill-screen is faster. Both
modes miss 60 FPS; removing experimental fill-screen alone is not a remedy.
The user's Fill Screen preference was restored at 14:49:13 and screenshot-checked.

## Renderer and audio limits

Vulkan/Mali-G715 remains active, and the slow intervals above have zero queued
pipelines. There are no recorded presenter-backlog drops, surface-present
failures or surface-rebuild stalls in this run. However, source inspection finds
the presentation-stall warning threshold is **250 ms**. Its absence does not
exclude ordinary 20–40 ms renderer waits. `record_successful_present` currently
discards the supplied acquire/encode/finish/submit/present durations. Preserving
those existing measurements, and separating guest/GX CPU work from renderer
waits, is the next targeted diagnostic change; the precise 60 FPS fix is not yet
identified. GPU utilization counters remain inaccessible without elevated access.

QuickTime was not running. Android reported unmuted media routed to its speaker
at volume 9/25. Native logs report stereo 32 kHz playback with gain 1 and non-silent
PCM reaching the host; queue telemetry reported no dropped blocks. These checks
do not prove audible sound at the speaker or explain a listener's silence report.

The original runtime process and the user's paused race remained alive throughout.
No reinstall, restart, save mutation, game-data transfer or system performance
configuration change was performed. No new APK or 60 FPS fix is claimed.
