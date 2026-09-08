# Android Preview 5 development checkpoint — not physical acceptance

Date: 2026-09-06. Keep this work on `codex/android-a4-touch-settings`, separate
from `main`. No Android packages or private inputs were published.

## Source and candidate

The candidate was built from Android base
`12fe0990bd05b830e7bf03b4b0681f61717c3536` plus the Android implementation changes
in the commit introducing this document. That base contains stable Apple v0.4.8
and release-evidence main commit `d0c67b2fbefdc958e60dd1e9e9958f3a407c1fe4`.
The build uses the existing authorized ignored `private/g8-full-translation`.

- Package: `dev.kartpad.android`
- Version: `0.4.8-android-preview.5`, code `10`
- ARM64 only, minimum API 28, target/compile SDK 36, non-debuggable
- Unsigned AAB: `android/app/build/outputs/bundle/release/app-release.aab`
- AAB SHA-256: `667e413bca76c6022a3f781c730e2fd6619f507e4a84533ad1817c3d2cd8018d`
- AAB bytes: `90,404,604`
- Universal APK: `.android-bootstrap/hardware-preview/KartPad-0.4.8-android-preview.5-v10-arm64.apk`
- APK SHA-256: `12602827e144b080acd0f8593f972a666e3bcc740ec54cd5143c85bb6484bdfc`
- APK bytes: `109,507,751`

Pinned bundletool 1.18.1 derived the universal APK from the AAB, signed only
with the local Android debug identity. This is a private test build, not a
production release. Both repository package audits passed unchanged, using the
explicit expected version name. ARM64 ELF alignment checks passed. No game image,
saves, generated source, credentials or signing material were committed.

## Changes and checks

- Brought shared stable runtime fixes and Retro Rewind 6.12.7 release metadata
  into the Android development branch.
- Replaced pathname reopening of picker-granted descriptors with owned
  descriptor duplication. WBFS no longer probes descriptor-looking sibling
  filenames as split images. The Java caller retains descriptor ownership.
- Matched current Apple phone/tablet touch defaults, including X/Y left,
  L/R right, digital R, hidden-by-default D-pad, and tablet Start near L.
  Existing position preferences remain intact. Movement is invisible while
  idle and anchors under its owning finger; release, cancellation and resizing
  neutralize input. Layout editing still shows the movement control.
- Added bounded release frame-time/shader telemetry and explicit local-only
  diagnostic export. Export warnings require private handling and review;
  nothing is uploaded automatically.
- Version-guarded preview installation and emulator-only protection for the
  destructive touch hit-map fixture. Never run other destructive fixtures on
  a physical phone without checking their guards.
- Pinned bootstrap and host checks passed without accepting licenses or
  changing unrelated system configuration.
- All 127 Python host tests passed, including 55 Android tests; physical
  preflight fake-ADB contract passed 13 cases; Retro version check passed.
- Full release build passed. `lintRelease`: 0 errors, 49 warnings, including
  existing localization, accessibility and dependency-update warnings.
- Updated visual/hit-map fixtures have not been rerun in an emulator during
  this physical-device phase. Static checks are not touch acceptance.

## Actual phone evidence

Exactly one authorized physical Google Pixel 9 Pro XL: API 37, ARM64, 4096-byte
pages, declared Vulkan support. No emulator is running. Device identifiers are
omitted. No gamepad/joystick is currently visible to Android's input inventory.

The phone still has `0.4.7-android-preview.4` code 9. **Preview 5 has not been
installed**: Android reports its lock screen active and does not dismiss it.
The prior update was in-place; the original save was backed up privately.
No uninstall, clear-data or downgrade was performed.

The user's existing WBFS at `Download/KartPad/Mario Kart Wii.wbfs` matches the
authorized source image byte-for-byte by SHA-256. On the physical phone the new
standalone descriptor probe reports:

```text
descriptor-import=passed source-readable=1 legacy-open=0
```

This proves the reader correction against the real image in a shell probe;
it does **not** prove the product's Storage Access Framework picker flow.

Earlier code-9 evidence: selector appeared; Retro Rewind 6.12.7 installation
completed; Original title/demo showed roughly 58–60 FPS while cold pipelines
compiled. The first Retro launch after installation crashed with SIGSEGV on
SDLThread, fault address 0x50. A clean-process reproduction and useful stack are
still needed. The capture summary records the crash and does not pass the full
physical signal matrix. Missing audio/controller signals are missing evidence,
not proof those features are broken.

## Resume with the user present

1. Unlock the Pixel and leave KartPad open. Verify and preserve current saves
   before any update; do not assume the earlier backup includes later play.
2. Re-run `scripts/check-android-physical-device.sh`. Require exactly one
   physical device, no emulators and matching signing identity.
3. For the audited APK above, calculate its SHA-256 and run the guarded
   installer with `KARTPAD_ANDROID_EXPECTED_PREVIEW_SHA256` set to that digest,
   `KARTPAD_ANDROID_EXPECTED_VERSION_CODE=10`,
   `KARTPAD_ANDROID_EXPECTED_VERSION_NAME=0.4.8-android-preview.5`, and
   `KARTPAD_ANDROID_ALLOW_PREVIEW_UPDATE=1` only after the save-preservation step.
   Never uninstall on a signing conflict.
4. Start `scripts/capture-android-a2-session.sh start`, test actual image import,
   then cold-launch each profile separately. Capture the Retro crash/stack and
   fix its cause before claiming parity.
5. Verify both landscapes, floating/multitouch input, A hold/lock, R/Z, control
   edits/reset, menu parity, HOME/Recents and lock/unlock, audio, haptics,
   controllers, motion steering, save persistence and a complete race.
6. Measure warm gameplay and thermals at 15 and 30 minutes. Report frame-time
   percentiles and shader-queue context; initial title FPS is insufficient.
7. Run `scripts/capture-android-a2-session.sh summarize` and retain private logs.

Android player-name/license-management parity with Apple v0.4.8 remains to be
implemented. The runtime crash, sustained slowdowns and all new physical touch
checks remain open. This checkpoint is not completion of the Android objective.
