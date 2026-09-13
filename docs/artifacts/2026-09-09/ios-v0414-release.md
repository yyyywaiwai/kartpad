# iPhone/iPad 0.4.14 build 33 release evidence

Manual owner release authorized after physical acceptance of build 32 on
9 September 2026. PRs #156, #159 and #161 are merged. Build 33 retains the
accepted app changes and updates iOS release metadata to 0.4.14/build 33.
The owner explicitly keeps Android's performance work independent.

## Acceptance and scope

The owner accepted controller gameplay, menus and the final chooser candidate
on the M2 iPad. The build-32 in-place update preserved all 32 protected files,
19,871,308 bytes, byte-for-byte. This is not touch-gameplay, custom-remapping,
external-display or broad-device acceptance. See the [chooser audit](mobile-game-chooser-audit.md)
and [Metal view reproduction](apple-metal-surface-recovery.md).

The compact iPhone chooser has zero vertical overflow in six exact-source
UIKit fixture cases: missing-data, ready and paused on iPhone 17 Pro and SE 3.
Help, Done, selection callbacks and both GitHub destinations were exercised.
The pinned SunPad overlay snapshot is unchanged. Pre-release source validation
passes 153 Python tests with one skip; final version/package results follow.

## Cross-platform handoff

- The duplicate Render row removal is already on main for Android as isolated
  commit `fc6ee29`. Its settings persistence/visual contracts and Kotlin compile
  passed during PR #159; Android device acceptance belongs to its build owner.
- The Metal ownership fix applies to Apple preparation paths; it is not an
  Android Vulkan optimization. macOS and tvOS binaries are not republished here.
- The new chooser/help remains Apple-only pending Android adaptation by its
  owner. Android's reviewed-log acknowledgement/inability path is also a
  distinct reporting follow-up; build 33 provides attachment guidance and does
  not claim complete parity with that newer Android flow.
- PR #157 viewport interpolation and Android CPU/frame-pacing experiments stay
  separate until their own acceptance. No unmeasured optimization is imported
  into this owner-accepted Apple release.

## Publication evidence

Published as the latest non-prerelease GitHub release
[`v0.4.14-ios.1`](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.14-ios.1).
The release tag points to merged main source
`de4ea58dc6c354bfb35443de1613de08a4d03ba4` (release metadata PR #163).

- IPA: `KartPad-v0.4.14-ios.1-unsigned.ipa`, **45,068,854 bytes**.
- SHA-256: `8892b7e148a4f0604735f5b6b6a5ddf69d8349a344b1b561eb1d400ab457dcaa`.
- Native executable: `ae83eba1fa67f9f1cad9bc5de91e822996bf2aeed82921366532da704db06f46`,
  byte-identical to the unsigned build-32 candidate executable. There is no app
  source difference between the accepted candidate and release source; iOS
  version/build metadata and the generated diagnostic/release records change.
- Architecture/families/minimum OS: ARM64, iPhone and iPad, iOS/iPadOS 16.
- Final Python suite: 153 tests pass, one skip. Fresh pinned runtime patch
  preparation, three changed patch hunks and the unchanged SunPad snapshot pass.
- Full main-source iOS build and unsigned app audit pass. Two independently
  generated IPAs are byte-identical; the complete public IPA/provenance audit
  passes. No signing profile, signing identity or private game data is included.
- All six hosted assets were downloaded anonymously with curl (no credentials or
  curl configuration), compared byte-for-byte with local files, and verified
  against SHA256SUMS. The downloaded IPA passed its full audit again with the
  exact source commit supplied. The hosted tag and latest-release state match.
- README, install guide, status, maintenance board and versioned notes identify
  this release. Eighty local document links pass and all 18 README FAQ sections
  remain. Android's owner received the scoped cross-platform handoff directly.

The hardware iPad retains the accepted private 0.4.13/build-32 installation;
this public 0.4.14/build-33 IPA requires the user's own re-signing. Public package
verification is separate from the recorded private-device acceptance.
