# Android v0.4.10 parity and performance audit

Started 2026-09-07 JST. Android-only development, not release acceptance.
Baseline: Preview 8/code 13 on Pixel 9 Pro XL, API 37, ARM64, 4096-byte pages.
Apple source reviewed: `d0c67b2..8ebefc9` (v0.4.9 and v0.4.10).
Main was merged **into the Android branch**, never the reverse.

## Parity inventory

| Apple change | Android action / verification needed |
| --- | --- |
| Non-consuming WPAD controller probes; immediate input sampling | Replace Android's consuming connection read; test a short press surviving probes. Android already caches SDL events immediately. |
| Visible Player 1–4 assignment and face-button remapping | Existing Android controls cover both; retain them and update PlayStation-position guidance. Physical multi-controller registration remains untested. |
| Local split-screen and Retro friend-room guidance | Replace the old online-only dialog; do not offer unusable Original friend-room instructions. |
| Experimental private Wii-server hostname | Reuse shared validated, service-scoped routing; add persisted next-launch Android settings. No server is started and ordinary TLS remains validated. |
| Maintainer-accepted iPad touch geometry | Update Android tablet defaults only; preserve phone defaults and custom layouts. |
| Paused chooser with Resume and next-launch game selection | Reuse Android chooser above the existing SDL activity; do not start a second runtime in-process. Pending changes apply only on cold launch. |
| Mii identity versus profile/slot-specific license editing | Added JNI reuse of portable save/Mii semantics. Stage one intent, re-read latest saves at cold launch, preserve before/after backups and recover interrupted multi-file edits before SDL starts. Physical mutation acceptance remains open; owner licenses were not edited or deleted for QA. |
| Mac icon refresh and Apple packaging/docs | Shared Android artwork already matches. Apple-only signing, entitlements and packaging changes do not transfer to Android. |

## Performance investigation

- Retained Preview 8 logs and a new on-device CPU profile are private/ignored.
- The initial visible surface was the chooser, not gameplay. A chooser sample
  is not used as game performance evidence; Original was launched separately.
- The new Original CPU sample again shows floating-point exception operations
  (`feclearexcept` 9.08%, `fetestexcept` 2.06%) and emulated TLS lookup (3.30%)
  among significant leaf costs. These are CPU sample shares, not frame-time
  percentages or a complete explanation of slowness.
- The renderer uses the Vulkan/Dawn path. Pixel GPU utilization counters are
  permission-restricted; no root or permission workaround is authorized or used.
  GPU saturation cannot be inferred from CPU profiling alone.
- Separate CPU work, shader compilation, GPU submission/presentation waits,
  frame pacing, resolution sensitivity and thermal state. Compare the same
  scene/configuration before and after; intro movies and emulator FPS are not
  substitutes for actual Pixel gameplay.

### New evidence and rejected optimization

- The retained native log identifies **Vulkan, Mali-G715 integrated GPU**, driver
  54.3.0, Mailbox presentation. This is not a software rendering fallback.
- Startup prewarming took 18.6 seconds for 2,010 pipelines despite 4,453/4,454
  Dawn cache hits. Startup compilation is a real cost, but warm slow intervals
  also occur with no pipelines queued.
- Preview 9 adds bounded `KartPadGPU` adapter logging and `KartPadCPU` main-thread
  CPU-time/wall-time occupancy once per 300 presents. Occupancy does not measure
  GPU saturation or distinguish kinds of off-thread waiting.
- A new 30-second Pixel profile (14,919 samples) includes `feclearexcept` 10.52%,
  `fetestexcept` 2.11%, scalar FP completion 3.62%, emulated TLS lookup 3.17%,
  current CPU context lookup 2.94%, and GX display-list processing 4.85% leaf
  CPU-cycle shares. This is a title/attract sample, not a matched user race.
- A four-view rendered attract sequence reached 26.67–32.09 presents/s with
  77.4–81.4% main-thread occupancy and zero queued pipelines. Other title/movie
  samples were near 60. The four-view sequence is not evidence that a 60 Hz
  single-player race runs at the same rate; its intended cadence is unverified.
- Android thermal status was 0 at the sampled checkpoint. This does not close
  sustained 15/30-minute race thermal acceptance.
- `tools/android_fenv_probe.cpp` is an isolated, source-only diagnostic, **not a
  game optimization**. On Pixel, 32,768 status-register/mask comparisons passed,
  but replacing public fenv calls with inline FPSR assembly lost arithmetic
  flags with production optimization settings. Disassembly shows division moved
  before the clear despite an assembly memory clobber. The probe rejects that
  path; no such replacement or fast-math relaxation is in the APK.
- A second source-only prototype keeps an out-of-line call boundary and combines
  flag capture/clear. Its synthetic loop retained flags and ran at 0.57–0.84 of
  baseline time in four alternating-order rounds. Governor/warmup variance is
  visible; this is not game FPS evidence or sufficient arithmetic acceptance.
  It is not integrated into the runtime.
- The physical resolution picker confirmed the retained setting was **2×**.
  A temporary 1× interval (10:41:21 until restoration around 10:46 JST) still
  showed title/movie stalls and a later rendered-attract interval at 27–29 FPS.
  Scene selection differs, so this is not a controlled before/after speedup.
  The original 2× preference was restored. GPU load is not ruled out, but
  reducing resolution alone did not eliminate all low-cadence samples.

## Preview 9 build and physical checkpoint

- Source baseline: Android merge `92798f8` includes main `8ebefc9`; local parity
  changes are described above. Product `0.4.10-android-preview.9`, code **14**.
- Complete dual AAB: **91,411,444 bytes**, SHA-256
  `1c775496d0db1f92d75225ab4455037fe960bb425dd96918f620ee8d01e62e29`.
- Locally debug-signed universal APK: **110,503,250 bytes**, SHA-256
  `0270eb47dcffeef68262883bac9a19edb212e9f03860d89b52ca74f03c49c768`.
- Both unchanged audits pass with the candidate's expected version-name
  override: `dev.kartpad.android`, ARM64, min API 28, target SDK 36,
  non-debuggable, profileable private candidate. The repository scans found no
  forbidden raw game inputs or signing material; this is not a rights-clearance
  claim. This is not a published or production Android release.
- The guarded update installed code 14 without uninstalling or clearing data.
  Its first selector post-check was blocked by screen lock; after user unlock,
  selector visibility and Original boot were verified independently. Capture
  was started after unlock. Existing Retro Rewind **6.12.7** remains installed.
- Fresh Original save exports immediately before/after update compare
  byte-identical. ISO/runtime inputs remained usable; no reimport was needed.
- Paused chooser shows Resume and next-launch selection; resuming retains the
  same runtime PID. SDL logs pause/resume and performance reporting stops while
  the chooser is visible. The process identifier is not a device identifier.
- Mii enumeration succeeds. The rename dialog remains laid out without overlap;
  typing two characters and deleting one leaves the IME shown. Cancel leaves
  identity unchanged. Actual owner rename/delete was deliberately not exercised.
- Original multiplayer menu exposes split-screen/controller/private-server
  settings, not Retro-only friend rooms. An empty server hostname is rejected
  without dismissing/saving; settings were cancelled and no service contacted.
- The next-launch choice was verified end-to-end: selecting Retro from the
  paused chooser kept the old runtime alive; a cold restart automatically
  launched the translated `retro_rewind` profile and showed the Retro title.
  Native diagnostics confirm non-silent PCM reached the host audio queue.
  Audible speaker/headphone output remains a hands-on check.
- A native input sample confirms an injected A reached KPAD as core `0x800`,
  classic `0x10`; title advancement was not observed. This narrows the input
  investigation beyond just Android hit testing, but does not identify the
  cause. A physical short-press/controller check remains open.
- Host tests: **132** source/builder contracts pass, including the pending-import
  selection guard; actual prepared Android four-slot non-consuming controller
  probe and Apple physical-controller probe pass. JNI identity host tests pass
  latest-progress preservation, profile isolation, linked-Mii rename, interrupted
  multi-file recovery, slot deletion isolation, validation and retained backups.
- `capture-android-a2-session.sh summarize` did not pass the automated signal
  matrix: native file-backed audio/input events are absent from its logcat-only
  input. The zero counts are missing evidence, not proof of absent playback or
  working controllers. Direct SDL/CPU/GPU logs and private native exports are
  retained separately. No audit or signal requirement was relaxed.

## Emulator continuation

At the user's request, phone interaction and its host logcat process stopped
before the phone left for the gym. Local continuation does not require it.

- `test-android-menu-parity.sh phone` passes the fixture's 8 top-level rows,
  5 control rows, 2 display rows, 6 data rows and 16 destinations. Opposite
  landscape retains the correct cutout/status/navigation safe bounds.
- The walker now resolves exactly one authorized emulator and exports that
  target before any mutation or cleanup trap. It will not rotate/install onto
  a connected physical phone. Its Retro version assertion uses the pinned
  release constant rather than a stale 6.12.5 literal.
- This run used a temporary read-only view of the existing API 36 AVD; its saved
  image was not overwritten. A separate API 36 ARM64 phone AVD with 24 GB data
  capacity is prepared for full owned-data import/runtime iteration.
- Emulator rendering, timings and synthetic inputs are not Pixel GPU/FPS,
  controller or physical-touch acceptance.

### Preview 10 emulator identity iteration

- The separate API 36 ARM64 AVD imported the supported local user-owned WBFS
  through Android's real document picker and Dolphin extraction successfully.
  Original booted, created a fresh emulator-only license and reached Single
  Player, Grand Prix, class and character selection via touch controls. No owner
  saves were copied to this AVD. Retro Rewind is not yet installed in this AVD.
- Found and fixed a concrete Apple parity omission: Android license-specific
  rename previously changed only `rksys.dat`. It now also renames the matching
  Mii by create ID, in the same latest-data, recoverable transaction. It does
  not directly rewrite other profile saves. Delete still leaves the Mii intact.
  The confirmation explains that other licenses can share this Mii.
- Host JNI/Kotlin tests now cover matching-Mii rename, preservation of a newer
  appearance edit, interruption between license and Mii publication, roll-forward
  recovery, other-profile byte preservation and deletion/Mii isolation. These
  tests and all **132** source/builder contracts pass.
- Private `0.4.10-android-preview.10`, code **15**, complete dual AAB:
  **91,411,824 bytes**, SHA-256
  `cb9f0654fcf7f5026110f30786a3618be8479348e388b1fe64c723c97d809c63`.
- Locally debug-signed universal APK: **110,503,250 bytes**, SHA-256
  `ef5a3409b50574cee113409bc14169af6095e962ad4b2ef4baba023223158552`.
  Both unchanged audits pass: ARM64, API 28 minimum, target 36,
  non-debuggable, profileable private candidate. No package was published.
- Code 15 was installed with `adb install -r` onto the dedicated emulator only.
  Its save was byte-identical across installation. The Pixel remains on code 14.
- Through the actual identity UI, renamed the disposable license to `EmuRacer`,
  cold-restarted, and visually confirmed that name in the game's Select Licence
  screen. Original save and Mii database comparisons found **zero changed bytes
  outside their name fields and checksums**. Private evidence remains ignored
  under `.android-bootstrap/v15-emulator-*`; no screenshots or saves are in Git.
- The landscape keyboard obscured the dialog's Save hit target during synthetic
  interaction; dismissing the keyboard allowed Save. A one-second A hold
  advanced the title after shorter injected presses did not visibly advance it;
  the hold activated A-lock, subsequently released. Short-press/title timing and
  keyboard-visible dialog ergonomics remain explicit follow-up checks.
- No new floating-point optimization is integrated. Emulator FPS does not close
  the severe Pixel performance issue. The emulator was left at the paused
  KartPad chooser; no further phone interaction occurred.

## Acceptance gates

Fresh runtime preparation, host contracts, arithmetic equivalence, pinned full
AAB build, unchanged APK/AAB audits, locally signed update-in-place, retained
save comparison, selector/Original/Retro launch, physical input and matched
performance sampling are required. Broad performance/thermal and online race
acceptance must remain open when not measured. No game data, raw traces, saves,
signing material or device identifiers belong in Git.
