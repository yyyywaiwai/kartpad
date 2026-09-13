# Platform candidate handoff — 13 September 2026

## iPhone and iPad candidate

KartPad 0.4.17/build 39 was installed in place on the owner's iPhone 14 running
iOS 26.6.2. The owner answered the Original/Retro race-and-relaunch request with
“it works its fine”; a live race was also visually observed. This establishes
owner acceptance of this bounded trial, not measured performance or online
race/reconnect acceptance. The iPad was not changed in this pass.

The executable was compiled from cf47944d1a841f60e7e774dd44e44dc99341fd92.
Comparison against packaging source 1bfccebb531ba9407227829c6871048427c32de6
verified identical Apple/runtime/patch/profile/build inputs. The original
compilation manifest was retained, and a separate equivalence manifest records
the version-only packaging update. The corrected compiled REL guard and
viewport interpolation source are included.

The same app identifier and signing team were retained. Existing game data
was already present, so no image replacement was needed. Protected saves,
identity, Mii, rating and preferences were backed up and read back: 25 of 26
files were identical; the configuration file only changed formatting and
parsed to identical values. No app uninstall, data reset or identity migration
was performed.

The initial private handoff was packaged twice byte-identically; the official
release is packaged separately with current notes, source guidance and licenses.
The exact public checksum is recorded in the release's SHA256SUMS-ios file.
The original compilation manifest is retained, and the release scripts reject
an unexpected executable or changed production source inputs.

Issue #196 still needs the affected iPhone 17 Pro Max/iOS 27 test; the iPhone 14
result does not close it. The older public build 36 release notes were corrected
to disclose its incomplete aggregate-shard guard.

## macOS

Version 0.4.17/build 39 includes the viewport interpolation and compiled REL
corrections. A fresh build, strict app audit, focused regressions and isolated
Original/Retro rendering, audio and keyboard-navigation checks passed. The
package was produced twice byte-identically. Full races, the reporter's exact
two-player scene and the separate PR #112 controller overhaul are not accepted
by this smoke test.

During smoke setup, a defaults command changed the live app's last-selected
profile to Original despite the intended isolation. No save data was touched;
the previous selection was not captured, so it was not guessed or restored.
The remaining smoke test used a separate app identity and portable data.

## Android

The code-78 device candidate is built from current reviewed production source,
with the PR #240 correction to duplicate test-stub patch application. This
build preparation correction leaves production rendering code unchanged.
Public Android remains 0.4.16 Android 2/code 65 until an accepted,
community-signed successor is published. The owner's test APK uses the same
debug signer as their installed app to preserve its data; it is separate from
the community-signed public update. Code 78 was installed in place on the Pixel 9 Pro XL, retaining package UID
and first-install time. The before/after inventory has the same 6,593 paths;
a shell-quoting error means these are path listings, not verified byte hashes.
Both games visibly show Ready to Play after launch, with no observed launch
crash. Gameplay, save contents and controller behavior await the owner trial.
Fresh preparation from merged PR #240 differs from the compiled candidate only
in test stubs and patch backup files, not production-runtime files. The embedded
source-dirty flag remains disclosed; this candidate is not a public release.
