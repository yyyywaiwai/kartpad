# Android Preview 3 physical-phone pause

Date: 2026-09-06

Status: **paused; not accepted for merge or release**

Android work is paused until the iOS version is stable. Preview 3 is already
behind the current iOS runtime and Retro Rewind fixes, and the maintainer
observed major slowdowns during phone testing. The slowdown observation was not
quantified before the session ended.

## Source and package evidence

- Branch: `codex/android-a4-touch-settings`
- Tested source checkpoint: `a3747a4988180277d6788e3693270a36b041f1e9`
- Product identity: `0.4.0-android-preview.3`, version code 8
- Audited local AAB SHA-256:
  `6dea55a38b9992fcbb687bad362e0ef5c5858b2f13323de36807bf408bceda74`
- Audited local test-signed universal APK SHA-256:
  `f6aac32fa22714ae98ec0116349f86a34925ea2fded73ec1018391328919b764`
- APK byte count: `109851815`

The APK used only the local Android debug identity. It was not published and
must not be represented as a production release. A later clean rebuild was
stopped at the maintainer's request, after its clean step had removed the AAB;
the hashes above identify the earlier locally rebuilt and audited artifacts,
not a completed clean reproducibility comparison.

## Phone and installation

- Google Pixel 9 Pro XL
- Android API 37, ARM64, 4 KiB page size
- Exactly one authorized physical target and no emulator were present
- Fresh install succeeded without uninstalling, clearing data, or downgrading
- Installed identity was `0.4.0-android-preview.3` version code 8
- The Original and Retro Rewind selector appeared

No phone serial, private game data, saves, credentials, signing material, or
generated translated runtime was added to Git.

## Partial runtime results

- The supported user-owned WBFS was copied privately to the phone and its
  on-device checksum matched the authorized local source.
- Direct ISO/WBFS picker import failed after the DiscIO JNI library loaded:
  Dolphin could not read the selected image. This remains a product failure.
- Importing the supported extracted RMCP01 folder succeeded, and Original
  started the real ARM64 translated runtime.
- The three-dot menu, Controls submenu, and Touch Control Settings appeared.
  Control opacity, sizing, C-stick mode, move, reset, and done actions were
  visible.
- HOME/Recents and lock/unlock returned to the running process with the touch
  overlay visible.
- Runtime logs showed the SDL entry point, surface creation, and low-latency
  audio initialization. Audible quality and latency were not manually accepted.
- Retro Rewind did not reach gameplay. The installer reported that upstream
  6.12.7 requires a newer KartPad build; this preview still targets 6.12.5.

## Incomplete acceptance gates

The final capture summary did not pass its automated signal matrix. No
controller was attached, and the final capture window contained no new audio,
controller, or lifecycle events. The following remain unaccepted:

- direct ISO/WBFS import;
- Retro Rewind installation and gameplay;
- both landscape orientations and full touch multitasking;
- A hold/lock, R/Z behavior, and complete move/resize/hide/reset checks;
- audio quality, haptics, controllers, rumble, and motion steering;
- save mutation and persistence;
- warm gameplay performance and thermals at 15 and 30 minutes.

The physical capture helper was updated for Android multi-user package output
by resolving the current Android user before requesting the package UID. This
is a tooling compatibility fix only and does not change the product result.

Do not merge this branch to `main`, publish either package, or delete installed
application data. Resume from this evidence after the iOS version is stable.
