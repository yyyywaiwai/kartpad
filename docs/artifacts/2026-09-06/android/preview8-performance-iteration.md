# Android Preview 8: measured slowdown and first CPU-side iteration

Date: 2026-09-06 (JST). Android branch only; no merge to `main`, Android release,
package publication or private-data commit. Base source:
`4221ef4894248d7d3135bb289c9318660db4456b`, plus the changes accompanying this note.

Owner paused testing until tomorrow (2026-09-07 JST). Implementation checkpoint
`c987a26755d5f02877784567b65173f571ab7a9d` is pushed to the Android branch.
Host-side app logging was stopped; existing private captures and phone data are
retained. Resume with physical A-button confirmation and the same slow Single
Player menu/race, then collect a matched performance sample. No scheduled restart.

## Current installed artifact

- Package `dev.kartpad.android`, version `0.4.8-android-preview.8`, code 13.
- ARM64, minimum API 28, target SDK 36, non-debuggable.
- AAB SHA-256: `0f6b0e4d94dab84ba21f820245971065b0a8d7588d8223e6e70e6c8d526eeabc`.
- AAB bytes: 91,380,063.
- Universal APK SHA-256: `d6b3ac85117feeed44d3fb1dad4d4b304d84eb034707994e304c2f65d70d2637`.
- APK bytes: 110,466,386.
- APK path: `.android-bootstrap/hardware-preview/KartPad-0.4.8-android-preview.8-v13-arm64.apk`.

The complete release AAB uses the existing authorized private translated graph.
Pinned bundletool 1.18.1 derives the APK, signed only with the local debug
identity. Both unchanged repository package audits pass. Guarded update-in-place
installation and selector verification pass on one Google Pixel 9 Pro XL,
API 37, ARM64, 4096-byte pages. No emulator was running. No uninstall, clear-data,
downgrade, root, security bypass or unrelated system configuration change occurred.

## Captured failure and diagnosis

The owner reported severe Original Mario Kart Wii menu/Grand Prix slowdowns,
including after reducing render resolution from 2x to 1x. The existing session
was captured before restarting it. Samples around 22:35–22:37 report approximately
22–41 FPS, often with p95 frame times around 35–57 ms and zero queued shader
pipelines. These are rolling samples, not a race average. The resolution change
is owner-reported, not an independently controlled comparison.

A private 9.993-second Perfetto scheduler baseline shows the main SDL thread
running for 6.742 seconds, with other app/renderer threads also active. This
does not by itself prove a GPU or CPU bottleneck. Light thermal status was also
reported; it does not explain every slowdown by itself.

Preview 7 (code 12) added opt-in local profiling and the icon but retained the
exact same native game-library bytes as Preview 6. This provided function-level
sampling of the existing runtime without changing its arithmetic or optimization
flags. A warm Original title/demo sample attributed these shares of sampled
CPU cycles across the app to the main game thread:

| Function/path | Sampled share |
| --- | ---: |
| `feclearexcept` | 9.52% |
| emulated TLS lookup | 5.11% |
| `pthread_getspecific` | 2.93% |
| `CurrentCpuContext` | 2.83% |
| `fetestexcept` | 2.32% |

These are leaf sample shares, not frame-time fractions or proof that these paths
explain all menu/race slowdowns. Cold startup samples separately show substantial
Mali driver/compiler work; do not confuse cold shader preparation with the warm
CPU-side costs. All raw logs, screenshots, samples and symbol caches remain
ignored and private. Nothing was uploaded to a profiling service.

## Narrow change and correctness checks

The state-aware scalar adapters unconditionally reapplied host NI mode after
each arithmetic/compare/estimate result. Those operations normally change only
FPSCR exception/status bits, leaving NI unchanged. Reapplying the mode still
reads host FP controls and writes multiple emulated thread-local variables.

The Android-only patch now compares the old/new NI bit before overwriting FPSCR
and reapplies host mode only on an actual transition. True NI transitions,
context-switch synchronization, exception handling, result bits and destination
suppression remain intact. No `feclearexcept`/`fetestexcept` calls were removed,
no fast-math shortcut was enabled, and Apple preparation is unchanged.

- `tools/android_scalar_ni_probe.cpp`, built for Android API 28, passed 676
  real-Pixel differential cases, including NaNs, signed zeros, overflow,
  underflow, NI on/off and suppressed destination writes. It also checks
  explicit NI transitions and the thread-local mode mirror.
- The initial 500,000-operation microbenchmark measured 51.870 ms before and
  44.919 ms after (about 13% lower time). Repeats were also faster but varied
  with device conditions. This is **not** a measured game-FPS improvement.
- The broader semantics contract passed 250,227 checks on both Mac ARM64 and
  Pixel ARM64, with identical state hash `0xccd5757c4c0643d4`.
- All 131 Python host tests pass. The new patch reverse-checks exactly against
  the prepared native header. Full AAB rebuild and both package audits pass.

## Icon and profiling scope

Android now uses the exact shipped Apple `KartPadIcon-1024.png`, copied by Gradle
into generated resources rather than maintaining duplicate artwork. An adaptive
icon supplies the Android mask and inset. Generated input bytes compare exactly
with the Apple asset, and the installed artwork was visually verified in the
Pixel's app-info screen. The notification glyph remains a separate small icon.

`KARTPAD_ANDROID_PROFILEABLE=1` explicitly opts a local build into shell profiling;
the default is off. This particular private candidate is profileable but still
non-debuggable and release-optimized. Android supports this distinction through
the [profileable manifest element](https://developer.android.com/guide/topics/manifest/profileable-element).
Use the installed system `simpleperf` for the app only; no ADB-root workaround is
needed. Captures may contain private stack data and must remain private.

## Preservation and remaining gate

A fresh validated 2,867,200-byte Original save was exported through the real app
UI before the Preview 7/8 updates, after the owner's latest gameplay. Both updates
used only the guarded installer's `adb install -r`; no later license/race was
entered during the intervening title/demo profiling. The WBFS and installed
profiles were not replaced. After the owner unlocked the phone, a fresh validated
save export from Preview 8 compared byte-for-byte with that pre-update backup.
This verifies Original's save bytes, not an independent Retro save comparison.

The phone initially locked after installation; the owner subsequently unlocked
it. Preview 8's chooser showed Original and the retained Retro Rewind 6.12.7
profile, and Original launched its native runtime successfully at 23:39 JST.
The intro movie ran mostly around 57–60 FPS. Actual rendered attract-mode races
still showed a 38.96 FPS sample (p95 37.42 ms) at 23:41:26, with zero pipelines
queued. These scenes are not a matched replay of the owner's Grand Prix route.
Do not treat the smoother movie as proof of improved gameplay.

A separate 15-second rendered-attract sample recorded 7,701 CPU samples. Leaf
shares included `feclearexcept` 10.84%, emulated TLS lookup 3.20%,
`CurrentCpuContext` 2.55%, `fetestexcept` 1.88% and `pthread_getspecific` 1.76%.
TLS shares are lower than in the earlier sample, but scene and timing differ;
this is not a controlled speedup measurement. Floating-point exception tracking
remains a substantial measured CPU cost and needs further correctness-preserving
investigation. The contemporaneous global thermal status was 0; this does not
establish 15/30-minute thermal acceptance.

Injected A presses reached the overlay but did not advance the title/attract
screen on either Preview 7 or Preview 8. Physical input confirmation and the
owner's same slow menu/race comparison are pending. Do not classify this as a
proven new input regression without reproducing it with the owner.

The fixed-schema capture summary was requested; it does not pass the physical
signal matrix: save-export round-trip pause/resume signals were observed, with
no fatal signatures in that capture, but controller/audio matrix signals were
missing. **The severe FPS issue remains open.** Enter the same slow menu/race at
the same resolution,
then capture matched before/after CPU samples and frame times. Broader warm
performance, touch/controller/audio/motion and Apple identity parity remain open.

For this exact candidate use version guards 13 / `0.4.8-android-preview.8` and
the SHA above. Preserve current saves again if the owner plays before another
update. Never uninstall on a signing conflict or downgrade to obtain a baseline.
