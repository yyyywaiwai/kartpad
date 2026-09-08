# Android Preview 12: warm slowdown and exportable metrics

2026-09-07 JST. Private development on `codex/android-a4-touch-settings`.
Apple v0.4.10 (`8ebefc9`) remains included; no merge into main or Android release.
Source starts from `7dc9786` plus the changes recorded here. See the
[parity inventory](android-v0410-parity-performance.md); this is not a claim of
100% behavioral parity or sustained 60 FPS.

## What the physical session established

- Google Pixel 9 Pro XL, API 37, ARM64, 4096-byte pages. Emulators were stopped
  before physical work. No device identifier is recorded here.
- Preview 11/code 16 launched Original using retained owned data. The user
  physically entered and played an N64 Sherbet Land race, then paused it.
  This establishes real race/input execution, not just title/attract playback.
- Early race telemetry around 13:31–13:32 reported 50.67–57.73 FPS, with p95
  frame times around 24.68–31.56 ms. Later 13:36 intervals reported 26.48–37.28
  FPS. The exact user pause boundary was not instrumented; later intervals
  must not all be labeled active-race measurements.
- Android's global thermal status rose from 0 to 1. Current HAL skin readings
  were approximately 38.8–39.2 C, battery about 37.5 C. The phone was USB charging.
  This supports thermal pressure as a contributor, not proof of the sole cause.
- Vulkan on Mali-G715 is confirmed. Warm slow intervals had zero queued
  pipelines. Neither software rendering nor active shader compilation explains
  those intervals. GPU counters remain permission-restricted; no root, governor,
  affinity, fixed-performance or thermal-policy changes were made.
- At the same guest-paused camera, 1x was selected at 13:41:02 and the user's
  original 2x restored at 13:46:19. After settling, present-count deltas were
  about **45.1 presents/s at 1x** (13:42:03.745–13:45:49.929) and **44.7 at 2x**
  (13:46:30.189–13:49:38.257). This sequential warm test is not a randomized
  thermal-controlled benchmark. It shows that lowering resolution alone did
  not restore 60 FPS in that paused scene; it does not rule out GPU costs.

## CPU investigation and bounded optimization

The 30-second Preview 11 race profile retained 20,382 samples, none lost. Leaf
CPU-cycle shares include combined scalar flag capture/clear 5.85%, remaining
`feclearexcept` 5.63%, scalar completion 3.72%, emulated TLS 3.53%, current CPU
context lookup 2.98%, and GX display-list processing 2.95%. These are sample
shares, not frame-time percentages. Frame-pointer call chains were incomplete;
they are not used to attribute inclusive costs.

The main guest thread can run on all eight CPUs and belongs to the top-app
cpuset. A paused 1x counter interval measured approximately 1.62 GHz averaged
over its running time. Instantaneous frequency/core observations do not prove
a fixed frequency cap or exclusion from the prime core.

Preview 11 introduced an Android-only out-of-line ARM64 helper combining the
post-arithmetic exception read and clear. The pre-arithmetic clear remains;
there is no fast-math relaxation. The helper preserves FPCR and non-exception
FPSR bits and must remain opaque to callers (no LTO/inlining). Actual disassembly
was inspected. Preview 12 retains this candidate; a matched before/after race
speedup has **not** been established.

`scripts/test-android-fenv.sh` compares 520,000 cases across all four rounding
modes, special values and seeded random inputs: values, FPSCR, exceptions,
destination writes, host flags and rounding match. Separate comparisons against
the original pre-change header also passed on the Pixel and on macOS ARM64.
These tests are substantial evidence, not an exhaustive proof for all game code.

## New diagnostics in Preview 12

- `KartPadPerf`, `KartPadCPU` and `KartPadGPU` now also reach the existing private
  per-launch console transcript, not just ADB logcat. Metrics remain coarse
  (approximately once per 300 presents); no per-instruction logging was added.
- A background worker samples OS thermal status/headroom, battery temperature,
  charging connection, power-save state, runtime profile, resolution and aspect
  mode every 10 seconds while the game activity is resumed. The local numeric
  journal is capped at 1 MiB and starts a new window when full.
- Both streams carry `elapsed_ms` since boot for correlation. Missing headroom
  is null, not zero. Sampling stops on activity pause; the game's own pause menu
  can still render and is not automatically identified as a paused race.
- Existing **Export Private Diagnostics…** includes these files. No analytics
  service, background upload, new permission, system-log scrape, serial, player
  name, save contents or game input is added by the new health logger. Existing
  native logs remain private and must be reviewed before sharing.
- Health guidance follows Android's
  [thermal API documentation](https://developer.android.com/games/optimize/adpf/thermal):
  headroom requests are spaced at least ten seconds apart and unavailable values
  are not interpreted as a cool device.

## Audited private artifacts

| Candidate | Unsigned AAB SHA-256 / bytes | Local test-signed APK SHA-256 / bytes |
| --- | --- | --- |
| Preview 11, code 16 | `17b3e593a0982083d8236bf832d684c213998a176f93485558af6064b3ac3cb0` / 91,217,777 | `d7fff2e3a194c2e63fc3db4a603087a4e4d29b3bc6918fec7d77385f6954a4f6` / 110,323,026 |
| Preview 12, code 17 | `f22643f62cd42e43e88adceb74fff9d386971e67d7594fd2a4b1b85852eaa6da` / 91,225,943 | `a44cbcc4cf784615b596df4849bdd753d3a0a7fed27a7850aff0cf406f5417c8` / 110,323,026 |

Current version: `0.4.10-android-preview.12`. APK:
`.android-bootstrap/hardware-preview/KartPad-0.4.10-android-preview.12-v17-arm64.apk`.
AAB: `android/app/build/outputs/bundle/release/app-release.aab`.
Both unchanged audits pass: `dev.kartpad.android`, ARM64, min API 28, target SDK
36, non-debuggable, locally profileable. Pinned bundletool 1.18.1 and the existing
local Android debug identity were used. No forbidden raw inputs/signing material
were found by the audits; that is not a public-distribution rights clearance.

The guarded code-17 update passed with the newly calculated APK hash and explicit
version guards. A fresh validated Original save was exported privately before
the update. No uninstall, clear-data, downgrade, reimport or owner-license edits
were performed. The selector retained Original and installed Retro Rewind 6.12.7.
Original booted without reimport, and its validated post-update save export is
byte-identical to the fresh pre-update export.

The real phone's explicit diagnostic export was pulled only into ignored private
storage and ZIP integrity checked. Its newest console contains the native
`KartPadPerf`, `KartPadCPU` and `KartPadGPU` records, and `android-health.log`
contains code-17 samples with the expected 2x preference, profile `base`, thermal
status 1, battery 37.5 C and unavailable-safe headroom readings. This verifies
file-backed collection, not just logcat output. No export was uploaded.

The required A2 capture summarizer was run. Its strict signal matrix still fails
because file-backed audio/input events are not in its logcat-only input; no fatal
signature was reported. The check was not weakened and this is not an A2 pass.
The private ZIP now preserves additional performance evidence independently.

Validation: 132 Python source/builder contracts pass with `PYTHONPATH=builder`;
JNI/Kotlin identity transaction tests and the new bounded-journal executable
tests pass. A fresh full Android patch preparation passes and the two modified
prepared native files match the sources consumed by the built candidate exactly.

## Acceptance still required

Sustained 60 FPS is not achieved. The next useful test is a repeatable Original
race and a Retro race, recording cold, 15-minute and 30-minute behavior, scene
and pause boundaries, resolution, charging state, audible audio and tactile
haptics. Export private diagnostics after the slowdown. Do not treat a title
counter or a brief fast interval as warm gameplay acceptance.

Physical multi-controller, motion, both orientations, complete save/relaunch,
Retro long-race behavior and full feature parity remain open. No controller was
attached in this session. Android must remain separate from main and unpublished.
