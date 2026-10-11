# Overnight Android handoff (ends 06:00 JST, September 24, 2026)

Goal: make the Android build measurably faster and smoother on the attached
Pixel 9 Pro XL. First measure the private candidates we already have, then try
the DriftDroid ideas we have not yet tried, one at a time, each against the
same phone scene. By 06:00 JST leave one clearly identified build installed and
a written record of what helped, what did not, and why.

## Hard rules

- Stop starting new work at 05:30 JST. Use the last 30 minutes to leave the phone
  at the KartPad launcher with no game running, then update the ledger and write
  a short report.
- Never uninstall, clear data or `pm clear`. Install in place only
  (`adb install -r`). The phone holds the owner's game data, saves, licences and
  console identity.
- **Downgrades are not possible.** These are non-debuggable release builds on a
  user phone, so `adb install -d` fails without an uninstall. To go back to an
  earlier build's code, rebuild it with a higher version code and install that.
  Plan version codes so every install is an upgrade (next free code: 206).
- Do not publish releases, post on GitHub or Discord, or push to a public branch.
- Report honestly. Emulator, host and title-screen results are not phone
  gameplay evidence. Tapping through the phone has been unreliable before:
  confirm every step with a screenshot, and never claim a race or battle happened
  unless a screenshot shows it.
- One change per candidate. Keep a change only if it beats the baseline by more
  than the baseline's run-to-run spread, with no new faults, graphics errors or
  lifecycle problems. Otherwise record it as rejected and move on.
- Leave the unrelated dirty file `docs/artifacts/2026-09-22/clean-rc2.md` alone.
  Put third-party research clones under `work/`, never in `~/GitHub`.

## Where things are

- Worktree: `/Users/chrissotraidis/.codex/worktrees/kartpad-stabilization-20260918`,
  branch `codex/upstream-all-platforms-20260922`. Android runtime submodule:
  `vendor/runtimes/android` (commit changes there first; the build stages the
  committed submodule).
- Pixel adb serial: `47181FDAS005KL` (check `adb devices -l`; it was absent all
  of September 23 afternoon). adb: `~/Library/Android/sdk/platform-tools/adb`.
- APKs, same private signer (SHA-256 `61dfb514…3afaf`), in
  `work/android-optimization-20260923/`:

| Code | File | SHA-256 | What it adds |
|---|---|---|---|
| 195 | KartPad-code195-private.apk | 3c929e6a6de15e6455754bfc5dcb52d13e8d3ac70ffe21e0dcb627b84744ea32 | last phone-tested build; believed installed |
| 203 | KartPad-code203-private.apk | ec7a4bd7a84ea7f9bedb507cac292c02436470c115f99484880793e49e557101 | copy-texture pool release, FP status skip, course-scoped pipeline replay, system-bar fix, game-thread Performance Hint |
| 205 | kartpad-205-nightly11.apk | 2491fb4e3cfa4d247df85a85be07a2b27051855161f51ac8eace91235616f23d | 203 plus game-thread context slot (removes emulated TLS lookups) |

Skip 204 (the compiler kept the TLS call). Details: [copy-stream ledger](../2026-09-23/android-copy-stream-loop.md).

## DriftDroid: what is already done, and what is left

DriftDroid (github.com/dorPXP/driftdroid, audited at `d12ccb522667716a4a25a3c4a03e72f1dee85588`)
is a separate Android port of the same WiiCompiled base. The full audit is
`/Users/chrissotraidis/GitHub/kartpad/docs/artifacts/2026-09-20/driftdroid-audit/REPORT.md`.
Before using anything, check whether upstream has moved:
`gh api repos/dorPXP/driftdroid/commits/android-port --jq .sha`. If it has, read the
new commits for performance work before starting Phase B.

| DriftDroid idea | Status in KartPad | Do not redo |
|---|---|---|
| `-Wl,-Bsymbolic-functions` local binding | Done (android/app/src/main/cpp/CMakeLists.txt) | yes |
| Dawn Vulkan cache flush (PerformIdleTasks) | Done (aurora-main/lib/webgpu/gpu.cpp) | yes |
| Native TLS (API 29) | Tried, no reliable gain; 205 removes the hot TLS on API 28 instead | yes |
| Reduced scalar FP bookkeeping | Done safely: FP status skip (203), proven equal by differential test | do not drop FP semantics |
| Thread-role CPU affinity | Tried (178, 180), no reliable gain, removed; 203 adds Performance Hint instead | yes, unless a Pixel profile shows core placement problems |
| Borrowed display-list cache arrays | Tried, no gain, removed | yes |
| Function ordering | Tried, placement changed, no gain | yes |
| Display refresh matching | **Not done.** KartPad never asks for a 60 Hz display mode | Phase B1 |
| Asynchronous GX command decoding (GX worker) | **Not done.** Decoding runs on the game thread | Phase B2 |
| Thermal resolution scaling | **Not done.** KartPad only logs thermal headroom | Phase B3 |

Where to read DriftDroid's versions (fetch into `work/driftdroid-<date>/`, for
example with `gh api` or a shallow clone at the pin):

- Refresh matching: `android/app/src/main/kotlin/com/driftdroid/android/MainActivity.kt` (search `preferredDisplayModeId`).
- GX worker: `aurora-main/lib/gx/fifo.cpp` and commit `fd3b01d3d32329601b38353f96d2ad9ab212765b` (design and bug history).
- Thermal scaling: `runtime/include/thermal_quality.h`, `android/app/src/main/kotlin/com/driftdroid/android/ThermalMonitor.kt`, and commit `444dabf` (it is off by default there).

Take ideas and narrow code with attribution in the commit message; do not import
DriftDroid's APK, translated code or whole files.

## Measurement tools (Pixel-specific, already written)

In `work/android-optimization-20260923/`:

- `battle-capture.py <label> <layer>`: with a battle already started and
  confirmed on screen, waits 25 s, screenshots, captures 120 s of compositor frame
  timing via `capture-surface.py`, screenshots again and records thermal state.
  Output: `<label>/summary.json` (presented FPS, intervals over 25 and 40 ms,
  max) and `<label>/app-summary.json` (`median_cpu_ms_per_present` = game-thread CPU).
- Find the layer with `adb shell dumpsys SurfaceFlinger --list | grep SurfaceView`
  once the game is running; it changes after resume.
- Hands off the phone during the 120 s window: no screenshots or profiling.
- Start each capture at a similar thermal state (check `dumpsys thermalservice`);
  let the phone cool if it is hotter than the baseline's.

## Baseline to beat (build 195, warmed stationary Cookie Land battle, 2x)

| Run | Presented FPS | Intervals > 25 ms | > 40 ms | Max | Game CPU/present |
|---|---|---|---|---|---|
| 195 warm | 59.07 | 109 | 2 | 133 ms | 14.70 ms |
| 195 repeat | 59.42 | 74 | 0 | 33 ms | 14.79 ms |
| 195 Retro chain warm | 58.43 | 169 | 10 | 133 ms | 14.75 ms |

At about 14.7 ms of a 16.7 ms frame, the game thread has little slack, so any
spike becomes a visible stutter. Lowering game-thread CPU is the main lever;
reducing long intervals is the main visible result.

## Phase A: measure what exists (target: done by about 02:00)

1. **Check the phone.** Confirm it is visible and record the installed version
   (`dumpsys package dev.kartpad.android | grep version`) and the installed APK's
   hash (`pm path`, pull, hash). If it is not 195, work out the right baseline
   before installing anything.
2. **Install 203 in place.** Check version and hash readback, launch, and confirm
   the launcher shows both games Ready with the existing licence.
3. **203 Cookie Land battle**, same scene and settings as the baseline: one
   warm-up battle so course replay records the scene, then two clean captures.
4. **Install 205 in place** and repeat. The emulator showed no timing difference
   between 203 and 205, so the phone decides. 205 stays the base for Phase B
   unless it is worse than 203; if it is worse, rebuild 203's source as 206.
5. **One profile.** Build the Phase A winner as a profileable variant
   (`KARTPAD_ANDROID_PROFILEABLE=1`, next code), install, and take one 30 s
   `simpleperf record --app dev.kartpad.android -e cpu-cycles -g` during a battle.
   Split by thread (`--sort tid`) and symbolize the game thread with the matching
   unstripped `libmain.so` under
   `android/app/build/intermediates/cxx/RelWithDebInfo/*/obj/arm64-v8a/` (match
   the build ID). Report the GX share (`fifo::process`, `GX__CallDisplayList`,
   `handle_bp`, `build_uniform`, `resolve_*`, `gfx::push`) of the game thread.
   On the emulator that share is about 15 to 18%. Profiling runs are not timing runs.
6. **Retro Rewind replay check** (can be combined with a Phase A battle): play the
   same Retro track or battle twice, export the log (Help → Report a Problem →
   Save Diagnostic Log) and look for `Pipeline scene replay` lines. This has
   never been seen on a Retro track.

## Phase B: DriftDroid-informed optimizations (about 02:00 to 05:30)

Each item is its own candidate with its own version code, measured with the same
battle capture against the Phase A winner.

**B1. Display refresh matching (small, try first).** The Pixel panel runs up to
120 Hz while the game presents at 60. Uneven compositor cadence is one plausible
source of the 25 ms intervals. Ask Android for a mode that fits 60 FPS:
`Surface.setFrameRate(60f, FRAME_RATE_COMPATIBILITY_FIXED_SOURCE)` on the game
SurfaceView (API 30+), or `WindowManager.LayoutParams.preferredDisplayModeId` for
the lowest same-resolution mode that is a multiple of 60, as DriftDroid does.
Apply when the game surface is created and after resume. Check the actual refresh
with `adb shell dumpsys display | grep -i refresh` or SurfaceFlinger during
play. Keep only if long intervals drop and nothing else regresses (menus,
launcher, pause overlay, resume). Also note whether the phone runs cooler.

**B2. GX command decoding off the game thread (the big one, experimental).**
DriftDroid's author attributed about 19% of their game thread to GX decoding.
Even if all of it moved, the best case is about 1.2x for that thread. Only start
this if the Phase A profile shows a GX share of 10% or more on the Pixel and at
least 2.5 hours remain. Rules from the audit and DriftDroid's own bug history:

- Behind a setting or build flag, off by default. The existing frame worker
  already owns encode/submit/present; this adds decode, not a second submitter.
- Batch work (DriftDroid landed at 32 KiB batches; per-primitive handoff dropped
  them to about 20 FPS). Give the queue a byte budget with backpressure.
- Synchronize at direct-state operations, frame boundaries, readbacks and EFB
  copies. Copy submitted display-list bytes, and check that guest vertex and
  texture memory referenced by index cannot change before decode (the scan
  cache and write-tracking granules in `runtime/src/hle/gx/gx_dl.cpp` matter here).
- Test second launch (DriftDroid had a second-launch deadlock), background and
  resume while work is queued, and shutdown. Compare screenshots of the same
  scene against the flag-off build for graphics differences.

If it is not clearly working and measured by 04:30, stop, commit it as an
off-by-default experiment with notes, and do not leave it installed.

**B3. Thermal resolution scaling (only if time remains).** Relevant to reports of
FPS falling after several races (Poco X6 Pro, OnePlus Ace 3). Needs a 15 to
20 minute sustained run to evaluate, and it lowers render resolution, which does
not reduce game-thread CPU. Off by default if added.

**Also allowed** if the profile points there: another narrow CPU change on the
game thread's top functions, with a correctness test first. Do not touch FP
results or exception semantics.

## Build command (about 15 minutes per native build)

```
KARTPAD_DISCIO_JNI_ROOT=$PWD/build/evening-20260921/discio-jni \
KARTPAD_ANDROID_VERSION_CODE=<N> \
KARTPAD_ANDROID_VERSION_NAME=0.5.1-android-nightly.<X> \
KARTPAD_ANDROID_PACKAGE_FORMAT=apk-release \
bash scripts/build-android-game-app.sh private/android-context-control-20260923/translation \
  build/<fresh>/runtime build/<fresh>/native
```

Then run `scripts/audit-android-package.sh <apk>` with
`KARTPAD_ANDROID_EXPECTED_VERSION_NAME`, `KARTPAD_ANDROID_EXPECTED_VERSION_CODE`
and `KARTPAD_ANDROID_REQUIRE_RELEASE=1` set. Copy each APK to
`work/android-optimization-20260923/` before the next build overwrites it. Check
the compiled result for a hot-path change (for example with `llvm-objdump
--disassemble-symbols=`): candidate 204 compiled but did nothing. Disk is tight
(about 130 GiB free), and each fresh native build adds a large
`android/app/.cxx` directory; delete old ones only if they belong to APKs already
archived.

The emulator (`KartPad_API_36_ARM64`, see the copy-stream ledger for the
command and `work/copy-stream-20260923/race-route.sh`) is useful for crash and
correctness checks while the phone is busy, not for timing claims.

## Context worth knowing

- #195 (S25 Ultra): 60 FPS in time trials, about 41 in VS, Original and Retro.
  Twelve karts nearly double game-thread CPU on the emulator. A Pixel result
  cannot prove a Samsung fix.
- Apple build 65 (replay and FP skip) is on the iPad with data verified but has
  not launched yet (iPad was locked). Not part of this session.
- Background: [ANDROID-PERFORMANCE-HANDOFF.md](../../ANDROID-PERFORMANCE-HANDOFF.md).

## Finish

Append a dated section to the copy-stream ledger: each installed build and hash,
each capture's numbers against the 195 rows, what was kept or rejected and why,
and what was not verified. Commit docs and code on the branch (private captures
stay under `work/`). End with a short plain-language report for Chris: what is
installed, what got measurably better on the phone, what did not, and what still
needs his hands.
