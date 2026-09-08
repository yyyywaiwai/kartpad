# Android Preview 6: physical import and gameplay checkpoint

Date: 2026-09-06 (JST). Android-only development on
`codex/android-a4-touch-settings`; no merge to `main` or package publication.
This is partial physical evidence, not full parity or performance acceptance.

## Exact candidate

Built from `e3fdce86c7976652ba00c8235b48da9a7bc0839c` plus the importer correction
in the commit introducing this document. The base contains stable Apple v0.4.8.
The existing authorized, ignored `private/g8-full-translation` supplies the
complete native runtime. No game data, generated source, saves, device identifiers,
signing material or private captures are committed.

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| Unsigned release AAB | `e02a9c6936347f269e6cebfaceadd2e21c0a0a07a95baacbd1ca3af0924348b8` | 90,404,646 |
| Local test-signed universal APK | `08c290a319244f7a4b5f99390d2fab820d36c04633442ca4aa9acf8ed182a8fb` | 109,507,751 |

Package `dev.kartpad.android`, version `0.4.8-android-preview.6`, code 11,
ARM64 only, minimum API 28, target SDK 36, non-debuggable. Both unchanged
repository audits passed. Pinned bundletool 1.18.1 derived the APK from the AAB
using only the local Android debug identity. It is not a production release.

Local APK:
`.android-bootstrap/hardware-preview/KartPad-0.4.8-android-preview.6-v11-arm64.apk`.
AAB: `android/app/build/outputs/bundle/release/app-release.aab` (rebuilds replace it).

## Import correction and preservation

Preview 5's real picker reached successful native extraction but still reported
that the image could not be opened. JNI returns null on success. Kotlin's trailing
Elvis operator was checking the result of `use`, not just the descriptor, so it
threw after successful extraction and storage discarded staging.

The correction checks the descriptor for null before entering `use`; successful
null JNI results now complete normally, and native errors still throw. A focused
source-contract regression was added. All 128 Python host tests pass.

Exactly one physical Google Pixel 9 Pro XL passed preflight: API 37, ARM64,
4096-byte pages, Vulkan support and sufficient free storage. No emulator was
running. Before updating, the current Original save was exported through the
app's real save UI to private preservation storage. Guarded `adb install -r`
succeeded with the calculated SHA and explicit version guards. No uninstall,
clear-data, downgrade or signing-identity replacement occurred.

On Preview 6, the real Android document picker imported the owner's supported
RMCP01 WBFS already on the phone. The app displayed **Game Data Imported**.
After restart to the selector, Original booted using the imported data. A fresh
Original save export compared byte-for-byte with the pre-update export. The
existing Retro license remained visible; Retro save bytes were not independently
exported/compared. Later user gameplay can legitimately change current saves.

## Physical checks observed

- Original/Retro selector, three-dot menu and touch settings appear.
- Retro Rewind 6.12.7 cold launch, retained license and offline Grand Prix work.
  Actual race: SNES Mario Circuit 1, 100cc, Mario, Standard Kart M, Inside,
  Manual. The owner played and reported good visuals with remaining slowdowns.
- A short press navigates. A 2.2-second hold visibly engages the cyan lock and
  continues acceleration after release; a later A tap unlocks it.
- Steering while A is locked shows the floating movement control under the
  contact; release hides it again. This does not prove simultaneous raw
  multi-finger A/R/Z handling. Start opens the in-game pause menu.
- HOME/Recents followed by foreground return recreated the surface and resumed
  the same game process. The exact card-return gesture was not attributable
  because the owner was also using the phone.
- AAudio opened stereo playback and started successfully. Audible quality,
  haptics and controller acceptance still require direct human confirmation.
- System bars remain visible and overlap the performance overlay: polish defect.

Not yet accepted: both landscape orientations, lock/unlock, R/Z combinations,
all move/resize/hide/reset settings, controllers/reconnect, motion steering,
completed race/results and newly changed save surviving cold relaunch. Android's
Apple-style player-name/license-management feature parity is not yet implemented.
The earlier code-9 post-installer SIGSEGV did not recur in these clean launches;
its cause remains unproven, not fixed by assumption.

## Performance and thermal evidence

Measured with the retained 2x render-resolution setting. Cold title rendering
settled near 60 FPS, but Retro 3D menus dropped to roughly 26–34 FPS even with
zero queued shader pipelines. Race samples ranged from about 25–60 FPS.
For example, at 22:06 a sample reported 27.60 FPS, p50 31.95 ms, p95 56.00 ms,
p99 59.18 ms, with the shader queue empty. Later samples returned to 60 FPS.
These are rolling samples, not a complete-race average.

At approximately 16 minutes elapsed since race start, the device reported thermal
status 1 (light), virtual skin 38.83 C, battery 37.7 C and BIG CPU 62 C. At about
25 minutes, virtual skin was 39.30 C and battery 38.5 C; CPU cooling-device state
was nonzero. The session included menus, pauses, HOME/Recents, user play and idle
on-track time, while USB-connected and charging. It is not a controlled continuous
15-minute performance pass or a battery-drain measurement. At 22:21 (about
30 minutes elapsed), thermal status remained 1, virtual skin was 39.11 C,
battery 38.2 C, BIG CPU 50 C and GPU 48 C, with nonzero CPU cooling state.
Nearby samples were approximately 25–35 FPS with no queued shaders. This is a
mixed-session 30-minute observation, not continuous-race acceptance.

A requested 10-second private Perfetto scheduler trace retained 8.11 seconds.
The primary SDL game thread ran for 6.961 seconds (about 86% of that interval),
with approximately 0.427 seconds runnable and 0.488 seconds sleeping. Most runtime
was on CPUs 4–7; CPU 7's observed frequency peaked at 1.885 GHz in this capture.
This supports investigating CPU-side work and thermal limits, but does not
identify a hot function or exclude GPU/driver costs. One overlapping graphics
slice was dropped by the parser; reported scheduler loss counters were zero.
The trace was processed locally with the official
[Perfetto trace processor](https://perfetto.dev/docs/analysis/trace-processor),
never uploaded. Hardware-counter profiling was denied by the production device;
no root, security bypass or debuggable replacement was used.

The fixed-schema session summarizer was run and remains **not passed**: the
required controller and non-silent audio signal matrix is incomplete. Retained
UID logs provide surface lifecycle and frame telemetry, without a new fatal
signature in this Preview 6 session. Missing signals are not proof of a broken
feature. No audit or summarizer requirement was weakened.

## Safe continuation

Do not replace the running app while its owner is playing. Preserve fresh saves
again before the next update; the earlier backup predates subsequent play.
Use the normal pinned build/audit/bundletool flow with explicit version name/code.
For this exact APK only, the guarded installer requires:

```sh
apk=.android-bootstrap/hardware-preview/KartPad-0.4.8-android-preview.6-v11-arm64.apk
apk_sha=$(shasum -a 256 "$apk" | awk '{print $1}')
KARTPAD_ANDROID_EXPECTED_PREVIEW_SHA256="$apk_sha" \
KARTPAD_ANDROID_EXPECTED_VERSION_CODE=11 \
KARTPAD_ANDROID_EXPECTED_VERSION_NAME=0.4.8-android-preview.6 \
KARTPAD_ANDROID_ALLOW_PREVIEW_UPDATE=1 \
  ./scripts/install-android-hardware-preview.sh "$apk"
```

Next performance work needs a repeatable route and CPU/GPU timing (or an explicit
private profiling build), plus controlled 1x/2x and cool/warm comparisons. Do not
claim a fix from an initial title frame, from compiling, or from an idle race.
