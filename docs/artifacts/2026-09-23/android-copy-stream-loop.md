# Follow-up loop: texture-copy stalls and GPU memory — September 23

Status: in progress. Starts from private build 195 and the
[overnight ledger](android-optimization-loop.md). The owner reports that build
195 still stutters in Original and Retro Rewind without an observed regression.
The attached Pixel was not visible to adb when this loop began, so the first
cycles use retained logs, source review and the ROM-free Mac renderer probe.

**Correction (emulator evidence, below):** the streaming-copy exemption built
into 196 to 198 reproduces black vehicle thumbnails and is withdrawn in 199.
Copy textures are also not the source of the 2.5 GB GPU memory. The sections
that follow record the original reasoning; the emulator section supersedes
their conclusions.

## Findings from retained build 195 evidence

1. **Every gameplay pipeline stall comes from a texture-copy pass.** Ordinary
   passes skip unready shaders (try_pipeline); only passes marked
   requireReadyPipelines block. All logged waits report persistent=1
   (for example 123 ms Original, 97 ms and 105 ms Retro).
2. **KartPad made every GXCopyTex persistent.** Upstream WiiCompiled lets a
   destination copied in consecutive frames skip unready shaders. The code134
   black-thumbnail repair (see
   [thumbnail investigation](../2026-09-19/android-black-vehicle-thumbnails.md))
   correctly removed that because a scratch target reused for a few frames can
   be retained. Side effect: any per-frame copy of the gameplay scene now turns
   each new shader into a whole-frame compile stall.
3. **The 906 ms pipeline-cache flush is not a gameplay hitch.** It ran on
   WILL_ENTER_BACKGROUND during the Home/resume check.
4. **Runtime pipeline creation is served from the Dawn disk cache** (775/775
   hits), yet only 128 of 1,199 cached recipes are prewarmed and 244 to 353 more
   are created during play. Each still costs driver time.
5. **Post-battle app memory is about 2.9 GB, of which about 2.5 GB is GPU
   memory** (GL mtrack 2.51 to 2.58 GB across four candidates; native heap about
   72 MB). The fixed per-frame buffers total about 150 MB.
6. **The copy-texture pool never forgets a key.** acquire_copy_texture keeps up
   to three textures per (destination, size, format) key for the process
   lifetime unless the guest later flushes that exact range. This is a likely,
   still unmeasured, contributor to item 5. The file is byte-identical in the
   Android, iOS, macOS and tvOS runtimes.
7. **Staging-capacity splits are not reported.** A split marks every queued
   pass required-ready and waits for the frame worker; its counter existed but
   was never logged.

## Changes (all four maintained runtimes)

- Copy-texture pool: release a pooled spare only when nothing else references
  it and no copy has requested it for 300 frames. Spares are reuse-only, so
  release cannot change pixels.
- Streaming copies: a color copy produced in each of at least 120 consecutive
  frames may skip an unready shader for one frame. One-shot copies, shorter
  runs, size changes and all depth copies still wait.
- Android telemetry line KartPadGpuResources each telemetry interval: copy-pool
  entries and approximate MiB, released spares, persistent versus streaming
  copies and cumulative staging splits. Relaxed atomic counters only; no Dawn
  call from the game thread.
- Host unit-test stubs gained the four staging-capacity functions they were
  missing, so gx_fifo_tests links again (test-only).

## Verification so far

ROM-free real-renderer probe (Metal, Dawn validation, deterministic cold-shader
gate), fresh cache per case:

| Case | Result |
|---|---|
| Consecutive-destination copy (code134 regression) | pass |
| Capacity prefix followed by copy (code134 regression) | pass |
| Full renderer suite with shader skipping enabled | pass |
| New: 130 consecutive copies, then cold shader | skipped one frame without waiting; recovered next frame |
| Control: 60 consecutive copies, then cold shader | waited for the shader, as required |

The host gx_fifo_tests suite is stale independently of this change: with the
original copy code it fails the same three tests and crashes at the same two
points (a GXCopyTex stub path and an absl insert). It is not a usable gate until
repaired; the real-renderer probe is the gate used here.

Not yet established: whether gameplay copies reach the streaming threshold, how
much of the 2.5 GB the pool holds, and any frame-time change on the phone. Those
need build 196 on the Pixel.

## Private candidates (not installed; phone not visible to adb)

| Build | Version | APK SHA-256 | Contents |
|---|---|---|---|
| 196 | 0.5.1-android-nightly.2 | 62137ab8824e52d0601ae8d1d80cfb8899678f21c6ebba6660f0a2f39ee8e0de | pool release, streaming copies, pool/copy/split telemetry |
| 197 | 0.5.1-android-nightly.3 | f01a59599462102e4f875df09a1362a0fedc13091b40ca400a5ce72ec6453328 | 196 plus live copy-cache count and size |
| 198 | 0.5.1-android-nightly.4 | 59100c76b205e248db9f523f02a1b29415f65d1a1d9592b16919223e6bf3449d | 197 plus unobserved FP status (section below) |
| 199 | 0.5.1-android-nightly.5 | 65700ffd045ca01217e989febc15c053b6b8acfea28c3afe388c568f093fd9c4 | 198 without the streaming-copy exemption (current candidate) |
| 200 | 0.5.1-android-nightly.6 | 01912ece029a3f9ea94e738b63b9c8c54a59399fa164feddc23f9618a6f829b0 | 199 plus course-scoped pipeline replay (Android runtime c59e33b) |
| 202 | 0.5.1-android-nightly.8 | c868696edef8e5f387045af385a07437e5c654e5156e500eae951d456061b176 | 200 plus FLAG_FORCE_NOT_FULLSCREEN cleared when hiding bars (#119/#202 candidate); current candidate |
| 203 | 0.5.1-android-nightly.9 | ec7a4bd7a84ea7f9bedb507cac292c02436470c115f99484880793e49e557101 | 202 plus game-thread Performance Hint session; current candidate |

196 to 198 are superseded: their streaming exemption reproduces black thumbnails.

Both pass the release package audit and carry the same signing certificate as
build 195 (SHA-256 61dfb514…3afaf), so an in-place install keeps app data. 197 is
the intended device candidate. Runtime commits: Android 0cca4d2, iOS 890e84f,
macOS 7de7da2, tvOS 0905167. Build 197's prepared source matches the committed
Android file. APKs and build/audit logs are private under
work/android-optimization-20260923; they contain game-derived code and are not
release assets.

## Device plan when the Pixel is reconnected

1. Preserve current logs, then adb install -r build 197 (no uninstall or data
   clear); read back version and both games Ready.
2. Repeat the build 195 stationary Original Cookie Land battle windows (2x, 11
   CPUs, first and warmed) and the Retro Chain Chomp Wheel pair.
3. Compare displayed FPS, intervals over 25/40 ms, maximum interval and
   KartPadPipelineWait counts against 195. Read copies_streaming to confirm
   gameplay copies actually reach the threshold.
4. Capture dumpsys meminfo after the same battle; compare GL mtrack with 195's
   2.51 to 2.58 GB and with the pool and live-copy telemetry.
5. Owner check: vehicle/character select thumbnails on first entry after the
   update, and any one-frame missing objects during races.

## CPU: unobserved floating-point status (candidate 198)

Retained build 194 battle profile: flag clear 5.78%, capture 4.16%, finish
1.97% of cycles; TLS lookups (emutls, pthread_getspecific, CurrentCpuContext)
about 5.3% more. Earlier candidates 191 to 193 reduced capture samples without
lowering total guest CPU, but all of them still read and wrote the host FPSR
around every operation.

What the guest can observe. The 29,637 translated functions contain six mffs
reads in four functions and no mcrfs. 801A1D40 and 801A24A4 store FPSCR into an
OS thread context. 801A278C and 801A2A14 (the only callers of 8012E5E8) enable
the FPU and mask/restore FPSCR in OS FPU-exception handling. 800209E8, called
from 80020A30, stores FPSCR to memory in what appears to be the crash-dump path.
None is race logic. The Retro Rewind mod sources contain no mffs.

What host flags affect. In the scalar, square-root and fused evaluators, host
overflow/underflow/inexact flags only add the sticky OX/UX/XX bits (and FX).
They can change a result or register write only if the guest sets OE/UE/XE.

Change: with KARTPAD_ANDROID_UNOBSERVED_FP_STATUS (Android app only), those
three evaluators skip the pre-clear and capture while the current FPSCR has
OE, UE and XE clear. With any of them set, the unchanged exact path runs.

Verification: tests/native/fp_status_differential/run.sh compiles the previous
and new headers into one binary and compares them over random, special,
subnormal, near-overflow and single-precision operands, all four rounding
modes, NI, random enable bits and arbitrary pre-set host flags.

| Run | Cases | Result |
|---|---|---|
| Enable bit set: exact comparison | 656,715 | 0 mismatches |
| Enables clear: all bits except FX/OX/UX/XX | 2,343,285 | 0 mismatches |
| Control: exact status required everywhere | 300,000 | 164,765 mismatches (detected) |

Input FPSCR summaries are generated consistently (VX and FEX recomputed), as
the architecture maintains them; inconsistent random summaries otherwise
differ because the old path recomputes them on every recorded exception.

Limits: this is host (Apple Silicon) arithmetic with host stand-ins for the two
Android helpers; the Android build compiles the same header. The whole-game
CPU effect is unmeasured until 198 is compared with 197 on the Pixel.

Build confirmation: the translated code only sets NI (mtfsb1 29) and restores
whole saved values (mtfsf 255), so OE/UE/XE stay clear during play. In build
198's unstripped library, PpcFmulsStateInline now tests the guest FPSCR against
0x68 (OE|UE|XE) and branches around both helper calls; build 197's calls the
clear helper unconditionally. Build 198 passes the release package audit with
the same signer.

Remaining limits: the change is inert if the guest ever enables OE/UE/XE, and a
whole-game gain is not established until the matched 197/198 comparison.
The first-loop decision not to import DriftDroid's reduced arithmetic stands:
results are unchanged here.

## Emulator validation (supersedes the streaming conclusions)

Environment: development AVD KartPad_API_36_ARM64 (host GPU, gfxstream), not
release evidence and not the owner's device. Its previous private build (code
99, same signer) had no game data. Build 198 was installed in place; the local
extracted game files were staged as in the earlier emulator procedure; config
offline, 1x, FPS overlay. A new licence was created in this disposable emulator.

Findings on 198:

- **Black thumbnail reproduced.** On first entry to Mario's vehicle select, the
  Classic Dragster thumbnail was a black silhouette and stayed black; re-entry
  showed it in colour. After moving only the Dawn and pipeline caches aside
  (the bundled seed cache and saves retained), a second cold first entry
  reproduced the same black thumbnail.
- **Why:** menus make about 12 texture copies per frame and races about 10, all
  to recurring destinations. Thumbnail bakes therefore passed the 120-frame
  threshold and were allowed to skip cold shaders, and the incomplete result was
  retained. A long run of copies to one destination does not prove the same
  content is redrawn. The streaming exemption is withdrawn in all four runtimes;
  every copy waits for its shaders again, as in 195.
- **Copy memory is small.** In a Luigi Circuit race: pool 57 entries (5.4 MiB),
  51 live copies (3.9 MiB) at 1x. Even scaled to 2x this is tens of MB, not the
  2.5 GB measured on the Pixel. The idle-spare release is kept (correct, cheap)
  but is not a meaningful memory fix. The large allocation is elsewhere (Dawn or
  driver heaps, static textures or pipeline objects) and still needs device
  attribution.
- **Race-start stalls confirmed:** persistent pipeline waits of 392, 210, 67,
  218, 121, 45, 178 and 83 ms while the race loaded and started from a cold
  Dawn cache. Emulator timing is distorted (a build was compiling on the host),
  so only the pattern, not the durations, is evidence.
- No staging splits occurred in menus or the race (staging_splits=0).

Probe change: the --stream-copy case is replaced by --long-copy-run, which
requires a 130-frame run of copies to one destination to still wait for a cold
shader and keep every pixel. With the exemption removed, copy-only,
capacity-copy, long-copy-run and the full suite pass.

Next direction for item 1: since every copy pass must wait, stalls can only be
removed by having shaders ready before they are needed — for example preparing
the recipes a course used previously during its loading screen. The 256-recipe
global prewarm was already rejected; a scene-targeted prewarm has not been tried.

Matched control on 199: the same cold procedure (Dawn and pipeline caches moved
aside, seed cache and saves kept, identical input timing) shows all three
vehicle thumbnails in colour on first entry, at both 10 and 15 seconds. 198
showed the black Classic Dragster in both of its cold runs. 199 then started
and ran a Luigi Circuit race at 60 FPS in the emulator with correct HUD and
minimap and no fatal signal in the log. This is emulator correctness evidence,
not Pixel performance; 199 passes the release package audit with the same
signer and is the only candidate intended for the Pixel.

## Course-scoped pipeline replay (candidate 200)

Because every texture-copy pass must wait for its pipelines, the remaining lever
for item 1 is compiling them before they are needed. The global 128-recipe
prewarm covers boot and menus; race pipelines were compiled on demand.

Design (Android runtime c59e33b):

- A game read of a .szs archive in a directory named Course (vanilla
  Race/Course) or Tracks (Retro Rewind Tracks, CT/Tracks, BT/Tracks) sets the
  renderer's current scene to a stable FNV-1a hash of that path.
- Each pipeline used while a scene is active is linked to it once per scene visit
  in a new pipeline_scene table (scene, type, hash, frames since scene start). It
  is created with CREATE TABLE IF NOT EXISTS, so existing recipes are kept; a
  future schema reset drops it with the recipe table.
- When a scene is set, the writer thread (which owns the database) queues up to
  384 linked recipes, in first-use order, that are neither ready nor pending, on
  the priority workers. The session log records "Pipeline scene replay: scene X,
  N recorded, M queued".
- Replay only compiles pipelines early through the existing preload path. It
  never skips or alters a draw, so it cannot reproduce the thumbnail defect.

Emulator evidence (same fixed route, Luigi Circuit, fresh process each time, warm
Dawn and pipeline disk caches):

| Run | Replay log | Pipelines created during loading | Created after race start | Pipeline waits logged |
|---|---|---|---|---|
| 199 | none | 209 to about 350 | about 60 (350 to 411) | 22 and 11 ms |
| 200, first visit | 0 recorded (two course archives) | 209 to 344 | about 60 | 18 ms |
| 200, second visit | 194 recorded / 188 queued; 13 / 5 | 209 to 405 | 5 | none |

The race rendered correctly with HUD and minimap. The emulator driver compiles
cached pipelines far faster than the Pixel's Mali driver (the retained Pixel
logs showed 97 to 133 ms waits with a warm cache), so this shows the mechanism
moves race pipeline creation into the loading screen; it does not measure the
Pixel stutter reduction.

Limits: the first visit to each course after installing still compiles on
demand. Retro Rewind was not set up in the emulator, so its track paths are
covered by the rule but untested. Loading may take slightly longer because the
workers compile during it. Apple runtimes have different pipeline_cache.cpp and
dvd.cpp files and do not have this change yet.

## Issue audit: Android system bars (#119, #202)

KartPad never requests a fullscreen SDL window on Android (startFullscreen is
unset; only Apple sets SDL_WINDOW_FULLSCREEN). SDLActivity.onCreate therefore
applies its non-fullscreen style: FLAG_FORCE_NOT_FULLSCREEN, visible system UI,
and no SDL re-hiding. KartPadActivity hides the bars through the insets
controller on focus, but never cleared that flag. On Android 15+ enforced
edge-to-edge masks this; on older Android the status-bar area can stay reserved,
matching the persistent top band on the AYN Thor (#202) and the visible bar in
#119.

Change in 202: hideGameSystemBars() also clears FLAG_FORCE_NOT_FULLSCREEN and is
called from onResume as well as focus gain.

A first attempt (201) additionally set FLAG_FULLSCREEN and re-assigned the
window's cutout mode; on the API 36 emulator it made the status bar visible over
the game, so it was discarded. 202 on the same emulator (with the corner cutout
overlay) keeps a full 2400x1080 window with bars hidden, identical to 200, at
title and after returning to the game through the launcher.

Not verified: the intended improvement on Android 14 and earlier. Only Android
15/16 system images are installed here, and both enforce edge-to-edge. #119 and
#202 remain open pending a report from an affected device.

## Item 2: time trial versus multi-racer CPU (emulator)

Same emulator, build family 200/202 (identical native code), Luigi Circuit,
player idle at the start line, telemetry KartPadCPU main_cpu_ms_per_present over
5-second windows once racing:

| Mode | Karts | Game-thread CPU per frame |
|---|---|---|
| Time Trial against the staff ghost | 2 | 4.2 to 4.4 ms (7 windows) |
| Grand Prix 50cc | 12 | 7.6 to 8.1 ms steady (8 windows) |

Eleven CPU racers raise game-thread work about 1.8x. The retained Pixel 11-CPU
battle measurements were about 14.7 ms per frame at 2x, just inside the 16.7 ms
budget. A device that runs this thread even modestly slower than the Pixel
crosses the budget in VS while time trials stay far below it, which matches the
S25 Ultra report (60 FPS in time trials, about 41 in VS, Original and Retro) and
the S25+ battle report. The S25 Ultra's large cores are faster than the Pixel's,
so the more likely explanation is that the thread is not running on, or not
clocked like, a large core. KartPad does not use the Android Performance Hint
API, sustained performance mode or thread placement; the DriftDroid audit found
DriftDroid pins its guest and frame threads to faster cores.

Candidate 203 adds an Android Performance Hint session (API 33+, loaded with
dlsym) for the game thread: target is the VI retrace interval, and each paced
frame reports the thread's CPU time since the previous frame. This affects only
scheduling and clocks. Whether it helps Samsung devices requires a Samsung
report; the Pixel and emulator can only show that it is inert or harmless.

Emulator check of 203: the hint session reports active (target 16,666,000 ns);
a Luigi Circuit Grand Prix runs at 60 FPS with game-thread CPU 7.7 to 8.4 ms,
in line with 200; course replay still prepares pipelines during loading; no
fatal signal. This shows the hint is present and harmless here, not that it
helps Samsung devices.

## Second iteration (September 23, 15:50 to 18:40 JST)

### Apple build 65: course replay and FP status skip ported

The Apple runtime (vendor/runtimes/ios 059d193) now carries the same
course-scoped pipeline replay as Android c59e33b and the unobserved FP status
skip, enabled for Apple by KARTPAD_UNOBSERVED_FP_STATUS in the runtime
CMakeLists. The FP differential test passes with the Apple define (3 million
cases, 0 mismatches; the strict control still detects differences). It also
includes the copy-texture pool release already in the iOS submodule. Build
number 65 (PublicProducts.cmake), marketing version 0.5.1.

Built incrementally in build/stabilization-ios-20260919 after restaging the
verified runtime (stage-maintained-runtime.py --verify passes at 059d193); the
build-64 tree is kept as an APFS clone in build/stabilization-ios-20260919-build64-clone,
and the RC2 IPA remains in build/release-051-rc2-20260922. Unsigned executable
SHA-256 546b64d5435d387c13bf9b63781f1a265e98ea086d31a3219c43c49ed5add79f.

iPad Pro 12.9 (6th gen): 35 owner files (WBFS, NAND, Retro saves, Config.toml,
ConsoleIdentity.txt, Preferences, SaveBackups, MiiBackups) backed up with
afcclient and hashed; signed with the existing development identity, profile
and entitlements; codesign --verify --deep --strict passes; installed in place
(installed version 0.5.1 build 65); all 35 files read back byte-identical.
Launch was refused twice because the iPad was locked, so there is no startup,
replay or gameplay evidence for build 65 yet. Receipts are in
work/ios65-install-20260923 (private).

### Android: emulated TLS on the game thread (candidates 204 and 205)

With the FP status skip in place, a 30-second cpu-clock profile of a 12-kart
Grand Prix on build 203 (emulator, game thread only, symbolized) no longer
shows the flag clear/capture helpers. Thread-local lookups lead instead:
__emutls_get_address 6.1%, pthread_getspecific 2.9%, CurrentCpuContext 2.2%.
Android API 28 lowers thread_local to emulated TLS, and the scalar FP helpers
read the current CPU context once per guest operation; the indirect-dispatch
memo is also thread_local.

Change (Android runtime 88c922d, dbe7661): the game thread registers itself in
RuntimeMain; it then reads its context and dispatch memos from plain slots that
only it writes, identified by the tpidr_el0 thread pointer. Other threads keep
the thread_local values, and the slot is released if its thread exits.
tests/native/primary_cpu_context checks on the arm64 emulator that the slot
always equals the thread_local value through nested scopes, a second thread and
owner exit (passes).

Build 204 is a dud: disassembly showed the compiler hoisted the
__emutls_get_address call above the owner check and selected the result, so
the cost stayed. Build 205 moves the fallback into cold out-of-line functions;
its CurrentCpuContext is now mrs, load, compare, branch, load. A profile of 205
confirms __emutls_get_address fell from 6.1% to 0.9% of game-thread samples.

Matched timing (same route, idle host, KartPadCPU main_cpu_ms_per_present, median of
the last six 5-second windows in the race):

| Build | Runs | Mean |
|---|---|---|
| 203 | 8.12, 7.67, 8.37, 8.31 | 8.12 ms |
| 205 | 7.90, 8.10, 8.45, 8.01 | 8.12 ms |

No measurable change on this emulator: the removed samples did not turn into
less wall time here, and the expected size (about 0.5 ms) is within run
spread. The Pixel's TLS share (about 5% of cycles in the build-194 battle
profile) may behave differently, but that is untested. 205 stays a separate
candidate for a Pixel comparison; 203 remains the current candidate.

| Build | Version | APK SHA-256 | Contents |
|---|---|---|---|
| 204 | 0.5.1-android-nightly.10 | 68eeea8900875bd20c05bd0dcfbd51567399edf3834fe68c54ecd9017e9000d2 | 203 plus context slot (ineffective: TLS call hoisted) |
| 205 | 0.5.1-android-nightly.11 | 2491fb4e3cfa4d247df85a85be07a2b27051855161f51ac8eace91235616f23d | 203 plus working context slot and game-thread dispatch memos |

Both pass the release package audit with the same signer. The Pixel was never
visible to adb during this iteration.

Lifecycle check of 205 on the emulator: one process (same PID throughout) ran
the Luigi Circuit Grand Prix for more than three minutes at 60 FPS, was sent
home and resumed, and kept rendering (race timer advanced from 3:06 to 3:18).
Its renderer log shows course replay working ("Pipeline scene replay: scene
c245398c16435baa, 213 recorded, 205 queued"). No fatal signal. The idle kart
never finishes, so a course change within one session was not exercised.

Retro Rewind: its track archives are .szs files under RetroRewind6/Tracks,
CT/Tracks and BT/Tracks, which the scene rule matches by directory name.
Whether the redirected DVD entry carries that path at runtime still needs a
Retro race; Retro is not set up on the emulator.

### New issue evidence

#195 (S25 Ultra) now reports 60 FPS in time trials and about 41 FPS in VS,
Original and Retro, after recent updates. This matches the emulator's 1.8x
game-thread cost for 12 karts, and makes the S25 a multi-racer CPU or
scheduling case; 203's Performance Hint is the candidate aimed at it.

## Pixel 9 Pro XL overnight handoff (September 24, 2026 JST)

### Plain-English outcome

This session tested the existing 195, 203 and 205 Android candidates on the
physical Pixel. It did not create a new performance fix. The useful result was
choosing which candidate to keep and leaving a verified build of it installed.

- **Supported on this Pixel:** in the comparable Cookie Land battle, 203 used
  about 2.05–2.14 ms less game-thread CPU per presented frame than the two 195
  baselines (12.652 ms versus 14.70–14.79 ms). This is a measured reduction in
  CPU work for this scene, not proof of a general FPS increase.
- **Rejected:** 205's extra game-thread context change did not improve on 203
  in the clean captures (12.691–12.711 ms versus 12.652 ms). The 203 source
  was retained.
- **Unproven:** a clean 203 run had fewer intervals over 25 ms, but still had
  two over 40 ms; the 195 repeat had none. Retro Rewind's replay hook logged
  zero pipelines recorded and zero queued on the tested track. Neither
  overall smoothness nor a Retro replay benefit was established.
- **Working on this Pixel:** Home/resume kept the same process and returned to
  an active battle; pause/continue resumed rendering. A 30-second CPU profile
  identified current costs but was not a timing comparison or optimization.
- **Handoff state:** version code 208 is a normal release rebuilt from the
  retained 203 source. Its installed hash was checked after an in-place
  install. The phone was left at KartPad's launcher with both games Ready to
  play and no game running. No phone data was cleared or public release made.

Next time, the S25 Ultra reporter needs to try the same 12-kart VS/Retro case
that was reported near 41 FPS. The Pixel result cannot establish whether that
Samsung issue is fixed. A Retro replay claim also needs a run whose diagnostic
log shows pipelines actually recorded and queued on a repeat visit.

The attached Pixel (adb serial `47181FDAS005KL`) began on build 195. Its
installed APK was pulled and hashed before changing it; the SHA-256 was
`3c929e6a6de15e6455754bfc5dcb52d13e8d3ac70ffe21e0dcb627b84744ea32`.
Builds 203 and 205 were installed in place with `adb install -r`, and each
installed version and pulled APK hash matched its archived candidate. The
launcher continued to show Mario Kart Wii and Retro Rewind as Ready to play,
and the existing Kah'ris licence appeared in the game. No app data was cleared.

The comparison used an idle Mario in Balloon Battle on GCN Cookie Land, with
the same vehicle, team and drift setting. Before and after screenshots show
active gameplay for each listed capture. Compositor intervals cover roughly
120 seconds per run; game CPU is the median of app reports within that window.

| Build and run | Presented FPS | Intervals >25 ms | >40 ms | Max interval | Game CPU/present | Thermal context |
|---|---:|---:|---:|---:|---:|---|
| 195 warm baseline | 59.07 | 109 | 2 | 133 ms | 14.70 ms | Prior baseline |
| 195 repeat baseline | 59.42 | 74 | 0 | 33 ms | 14.79 ms | Prior baseline |
| 203 repeat 1 | 58.22 | 211 | 5 | 49.98 ms | 13.834 ms | CPU cooling active; status rose 1→2 |
| 203 repeat 2 | 51.07 | 1048 | 19 | 50.14 ms | 17.870 ms | Status 2, stronger cooling; exclude from code comparison |
| 203 after cooling | 59.70 | 39 | 2 | 49.98 ms | 12.652 ms | Status 1, CPU/GPU cooling 0 |
| 205 warm | 59.53 | 61 | 0 | 33.75 ms | 12.787 ms | CPU cooling active; status rose 1→2 |
| 205 after cooling | 59.54 | 57 | 1 | 66.62 ms | 12.711 ms | Status 1, CPU/GPU cooling 0 |
| 205 after cooling, repeat | — | — | — | — | 12.691 ms | Status 1, CPU/GPU cooling 0; compositor layer argument was incomplete, so those timestamps are invalid |

The clean 203 capture reduced median game CPU by 2.05–2.14 ms versus the two
195 baseline runs and had fewer intervals above 25 ms. It still had two
intervals above 40 ms, versus zero on the 195 repeat. The clean 205 CPU
captures did not beat 203: they were 0.039–0.059 ms higher, below the 0.09 ms
spread of the 195 baseline pair, and the complete 205 run had more intervals
above 25 ms than the clean 203 run. Stationary battle AI and item effects vary;
these runs do not prove a precise causal speedup or a Samsung fix. The 203
runtime was therefore selected for retention. The root checkout now points to
Android runtime `a193cf432a06bc019e5db2b0d68f5a4a953745d4` (the 203 source),
committed in `8640064`. A release APK was built as version code 206,
`0.5.1-android-nightly.12`, because Android would not install 203 over 205.
The APK passed `audit-android-package.sh`, was installed with `adb install -r`,
and the installed APK was pulled back and matched SHA-256
`68f28bfe3df61d1b36bacc0445821bce721425490ea1bb2460b51ab355b679ab`.
Both games remained Ready to play, and the existing Kah'ris licence loaded.

On build 206, Retro Rewind's N64 Wario Stadium loaded and ran twice. The
second visit used the in-race Restart action; screenshots show active racing
on both visits. The in-app diagnostic export for that session contains one
`Pipeline scene replay` entry: scene `78b6ec656e1284da`, **0 recorded,
0 queued**. The log contains three `New race started` events, but no later
replay entry with queued pipelines. This establishes that the replay hook ran
in a Retro session; it does not establish that it warmed any pipelines or
reduced repeat-visit stalls on that course. The private exported log and
screenshots remain under `work/android-optimization-20260923/`.

The retained build's lifecycle check used an active Cookie Land Balloon
Battle. Before Home, the app PID was 8526. Home showed the Android launcher;
opening KartPad and choosing Play Game returned to the same battle with its
timer advanced, and PID remained 8526. The in-game Pause -> Continue path
also returned to active rendering. The battle was then quit through the game
menu; the app was closed and reopened to the KartPad launcher, which showed
both games Ready to play and no game running. This checks process continuity
and rendering for this Pixel session, not save persistence through a kill.

Remaining gates: a repeat Retro course with recorded/queued replay pipelines,
and reporter gameplay on the S25 Ultra (especially 12-kart VS/Retro) to see
whether the Pixel CPU gain helps the reported 41 FPS case. The Pixel evidence
does not validate that Samsung result.

The optional CPU profile used a private profileable release variant of the
same retained 203 source: version code 207, name
`0.5.1-android-nightly.13-profile`, SHA-256
`d381248672b1bed0e942c74a7208c9c76995ab9ce1b0aa56e983e8b57e3ac439`.
The profiler audit confirmed a non-debuggable, shell-profileable APK and a
matching unstripped `libmain.so`. A screenshot confirmed active Cookie Land
gameplay before the successful 30-second `simpleperf record --app` capture.
It recorded 21,622 CPU-cycle samples with none lost; the symbolized report is
private under `work/android-optimization-20260923/profile207-cookie30-report.txt`.
Of the samples attributed to `SDLThread`, the largest named self costs were
`FinishScalarFp` (3.96%), `GX__CallDisplayList_80172f64` (3.76%),
`__emutls_get_address` (3.12%), `PpcFmulsStateInline` (3.01%), and
`aurora::gx::fifo::process` (2.28%). These are sampling shares, not frame-time
or candidate comparison measurements. The first 30-second attempt wrote to
shared Downloads and produced an empty file despite reporting samples; the
successful capture wrote under `/data/local/tmp` and was pulled from there.

**Final phone state:** the profileable variant was replaced in place with a
normal, non-debuggable, non-profileable release built from the retained 203
source: version code 208, name `0.5.1-android-nightly.14`, SHA-256
`a8b0d1867fe654d373b6044687b3b1e9593160163881c9be13aaa6f28e167579`.
The package audit passed, the manifest has `profileable android:shell=false`,
the installed version matched, and a pulled installed APK matched that hash.
The Pixel was left at the KartPad launcher with both Mario Kart Wii and Retro
Rewind showing Ready to play and no game running. No uninstall or data clear
was performed.
