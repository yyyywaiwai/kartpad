# KartPad status

[Coordinator runbook and implementation plan](MAINTENANCE-AUTOMATION.md) ·
[Canonical active queue](MAINTENANCE-BOARD.md).

Updated: 13 September 2026. This page summarizes acceptance, not a full test log.
Use the [maintenance board](MAINTENANCE-BOARD.md) for candidate ownership and
next actions, and [known issues](KNOWN-ISSUES.md) for current reports.

## Published packages

| Platform | Package | Acceptance boundary |
| --- | --- | --- |
| Android | [0.4.17 Android 1, code 80](releases/v0.4.17-android.1.md) | Owner accepted preceding candidate Retro single-player/touch; new FPS sizing and D-pad editor passed physical Pixel UI checks. Exact release-payload checks are recorded in release provenance; online and affected-controller acceptance remain open |
| iPhone / iPad | [0.4.17, build 39](releases/v0.4.17-ios.1.md) | Corrected compiled REL guard, owner-accepted bounded iPhone 14 trial and preserved saves/configuration; iPhone 17 Pro Max/iOS 27 and online acceptance remain open |
| Apple Silicon Mac | [0.4.17, build 39](releases/v0.4.17-macos.1.md) | Fresh build, viewport/REL checks and isolated Original/Retro rendering, audio and keyboard smoke; exact reporter two-player scene, full races and controller overhaul remain unaccepted |
| Apple TV experimental | [0.4.11, build 9](releases/v0.4.11-tvos.1.md) | Published identity-fix and compiler-hardened package; exact-build hardware acceptance remains open |

[Download and install](../README.md#downloads). All listed packages include the
issue #94 console-serial correction. Updating does not clear old server-side
identity history or bans. Older affected packages should stay offline.

The September 10 releases include the [joint source delivery](artifacts/2026-09-10/android-source-delivery.md)
and [verified download ledger](artifacts/2026-09-10/platform-release-verification.md).
Historical local candidates are retained in their dated records.

## Current device acceptance

The owner accepted the bounded iPhone 14 trial of **0.4.17/build 39** on
13 September. Saves, identity and configuration were preserved during the
in-place upgrade. The unsigned IPA delivers that executable with the original compilation
manifest retained. This does not close the iPhone 17 Pro Max/iOS 27 report. See the [candidate handoff](artifacts/2026-09-13/platform-candidate-handoff.md).

The owner also considers iPad and Mac good to release. That is owner acceptance;
this pass's recorded physical Apple trial was on iPhone 14. Android code 78
passed the owner's random Retro single-player race and touch-settings trial.
Code 79 adds FPS text sizing and a responsive touch editor; Large persistence
and D-pad Hide/Show passed physical Pixel UI checks. Save and identity file
hashes were unchanged during that trial; only the new FPS preference changed
among touch settings. Two Android licenses are being preserved as requested;
their presence does not prove that an update created an identity. Possible
Retro WFC menu slowdown remains under investigation. See the
[controls and acceptance audit](artifacts/2026-09-13/android-controls-request-audit.md).

## Established results and remaining limits

- **Android:** the owner accepted Original Grand Prix with Kishi and automatic
  touch hiding, and reported Retro WFC login, worldwide matchmaking and live
  racing. These apply to the tested runtime, not every later preview. Graphics
  corruption, online-menu stalls, cup crashes and warm slowdown remain open.
- **iPhone/iPad:** the owner accepted build 32 on the M2 iPad after controller
  gameplay, reporting/menu and chooser checks. Build 33 publishes those app
  changes with updated version metadata. All 32 protected save/settings files
  were preserved across the build-32 update. The A10X reporter confirms build-29
  startup and Original/Retro loading; their lower FPS remains a separate issue.
  Touch gameplay, custom remapping, external displays and complete production
  online behavior are not newly accepted by these results.
- **Mac:** the original correctness and offline test program includes all 32
  retail tracks, race/save cycles, two-player results and representative audio
  continuity. New two-player rendering reports and controller changes need
  their own regression evidence; see the maintenance board.
- **tvOS:** the reporter accepted the 0.4.1 storage repair on Apple TV 4K
  (3rd generation). That [specific result](artifacts/2026-09-04/tvos-v0.4.1-storage-acceptance.md)
  does not establish A12 compatibility, purge recovery or current-build performance.
- **Online:** isolated WFC race/results tests and Android owner reports have
  different scopes. Complete distributed-build results/reconnect, Original
  private-server gameplay and native room hosting remain open. See [ONLINE.md](ONLINE.md).
- **Performance and peripherals:** sustained frame pacing, long soaks, full
  three/four-player coverage, motion/audio refinements and external displays
  remain incomplete. See [performance](PERF.md), [controllers](MULTIPLAYER.md)
  and [external displays](EXTERNAL-DISPLAYS.md).

## Evidence and requirements

- [Release notes](releases/) and [dated artifacts](artifacts/) record exact
  source revisions, checksums, procedures and observed outcomes.
- [Product requirements](PRD.md) retain the engineering acceptance matrix.
  A historical checked row does not accept a later package automatically.
- [Release checklist](RELEASE-CHECKLIST.md) applies to new candidates.
- [Historical status ledger](archive/status-through-2026-09-07.md),
  [journal](archive/JOURNAL.md) and [iterations](iterations/) preserve earlier
  results. Their machine state and next steps are not current work assignments.
