# Owner-controlled Android captures

Private build111 remained installed during all captures. No controls were sent
by the agent. The full-race CPU driver marker was removed before owner play.

## Verified full-race evidence

Peach Beach lap3: owner-20260916-141718, 20 seconds of cpu-clock:u at99Hz,
3,090 samples. Exact build111 symbols are retained separately. All eight
screenshots were visually reviewed: moving active race, opponents, items,
timer1:25.730 to1:48.155. OCR falsely rejected TIME as TIMES/TIME8; original
rejection is retained alongside manual review. Log intervals:60.09,56.57,
58.84,53.75FPS; final interval p95=27.22ms,p99=32.38ms; compilation queue0.
This is a real gameplay dip, not the previously excluded finish sequence.
It is not a reproduction of the most severe10-29FPS reporter cases.

CPU self samples, separated by thread ID (percent of all app sampled CPU):
- Guest/game thread53.92%; scalar clear4.01% and capture4.43% combined8.44%
  of app samples, about15.7% of this thread's sampled work.
- Renderer worker19.26%.
- Audio worker10.13%, already separate from the game thread. Its inherited
  SDLThread name initially obscured that distinction. ProcessVoice2.94%,
  ReadSample1.91%, CurrentRawSample1.59% are on that audio worker.
- Presentation thread3.50%.

A prior20-second owner capture (141557) produced3,022 samples and similar scalar
costs; only its start/end screenshots have been manually reviewed so far.
Do not claim a matched baseline/candidate speedup. Screenshots and sampling can
perturb timings; no uninstrumented control or GPU execution trace was collected.

## Retro Rewind

UID-filtered logcat and timestamped screenshots cover Retro VS waiting/menu,
transition, and Luigi Circuit racing under retro-session-20260916-142314.
The console confirms retro_rewind profile,2x render scale, and audio worker start.
The waiting-screen interval at14:23:40 was50.04FPS,p95=29.71ms,p99=59.44ms,
queue0,main-thread occupancy74.0%. This rules out an active shader queue in that
interval; it does not identify whether network waiting, pacing, scheduling,
rendering, or another cost caused the dip. No menu CPU sample profile was taken.

Auto-triggered race profile owner-20260916-142445 produced2,623 samples.
Start/end screenshots show active Luigi Circuit lap1,timer4.546 to27.913,
with items and another opponent. Logged race intervals stayed59.73-60.24FPS.
This lighter online race is not equivalent to the12-racer Peach Beach workload;
do not infer a vanilla-versus-RR speed difference from them.

## Logging changes built locally

Build112 adds interval present count and main CPU milliseconds per present,
render scale, frame-statistics window sample count,worst-frame time,jitter,
and names the audio worker KartPadAXMix on Android. Existing metric fields
remain. No per-instruction probes or game-state writes were added.
Build112 passed and was superseded by build113, which includes these metrics.
Build113 is now installed and the new fields have been observed in owner logs.
See android-display-list-front-cache.md for its continued slow intervals.

These fields address a demonstrated ambiguity, not the performance defect.
Next: obtain a menu CPU profile if that screen slows again; measure where the
main-thread scalar cost can be removed without changing guest floating-point
semantics. Audio is already parallel and must not be proposed as a missing
worker. Raw assets,screenshots,profiles and logs remain private under build/.

## Build113 owner captures at16:26 and16:28

owner-20260916-162642:20sec,2978samples,zero lost. Start/end screenshots
show countdown to22.518sec, opponents and items. Logged low55.51FPS.
This includes race start and is not a steady-state matched benchmark.

owner-20260916-162813:20sec,2994samples,zero lost. All8screenshots manually
reviewed: active lap2,1:27.420 to1:51.079, opponents/items and player movement.
OCR rejection is a false negative; separate MANUAL-REVIEW.md preserves that
distinction. Log reaches53.68FPS,p99=32.82ms,worst39.70ms,queue0 at2x.
The slowest logged interval is adjacent to the profiler endpoint, so aggregate
CPU shares do not identify the cost of that individual slow frame.

Current-build symbols verified against all24 file-backed allocated ELF sections
in the APK. In the second profile, rounded CPU self-sample totals are game55.18%,
renderer18.55%,audio8.15%,presentation3.70%. Scalar clear/capture together7.92%
of app CPU samples, approximately14.4% of game-thread samples. Display-list
call self2.10%. Game CPU interval averages14.24-14.96ms per present.
These reinforce scalar bookkeeping as a substantial CPU cost, but the earlier
semantics-correct combined-kernel experiment did not provide a general speedup.
Do not reinstate its rejected version or call these unmatched runs proof that
front-cache build113 improved performance. GPU time remains unmeasured.
Both captures are terminal and saved; no controls/settings/build changes made.
