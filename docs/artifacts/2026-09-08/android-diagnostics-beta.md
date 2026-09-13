# Android fullscreen/diagnostics beta acceptance — 8 September 2026

[Release: v0.4.12-android.2](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.12-android.2)
from merged source `ea53d067e9e18d972c6b1046527990177a285f51` ([PR #121](https://github.com/chrissotraidis/kartpad/pull/121)).
Version 0.4.12-android.2/code 23, ARM64 Android 9/API 28+ with Vulkan.
This is an Android APK. No iPadOS, macOS or tvOS binary was released in this pass.

## Exact artifacts

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| Public APK | `278ae2ec19108540d38fbbdabe4f525ee1ea6542d38849c8d5218b82c9b89a68` | 110331218 |
| Public notices ZIP | `f1b018540c999780483c07bb2c0adaf6489fe604c8ddcab365adaf1962b3cdc0` | 90648 |
| Local AAB, not uploaded | `904fe457f87c120e2ca2a63f8610af36e79ed90b29cc8d4209595ce0e09446c9` | — |

Release certificate SHA-256:
`c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.
The existing public signer was retained. Two independent APK derivations were
byte-identical. Rebuilding the exact merged source produced the tested AAB
bytes. Public and locally signed test APK payloads match excluding signature
metadata. The 26-entry notices/provenance archive contains only its allowlist.

Unauthenticated downloads of all three public assets (APK, notices ZIP,
SHA256SUMS) matched local files byte for byte. The downloaded APK passed the
release audit. The release tag resolves to the merged source above, the release
is a prerelease, and stable latest remains `v0.4.11`.

## Validation

- 140 Python tests; Android save/profile/identity host tests; Kotlin exit history,
  privacy, API fallback, invalid state and interrupted atomic-setting tests.
- Actual prepared Dawn toggle block compiled in debug and release against five
  environment values. Freshly prepared sources matched the compiled tree.
- Android release lint and APK/AAB/repository safety audits passed.
- Disposable API 36 ARM64 emulator on host Vulkan/Apple M3 Max: the actual OS
  force-stop fixture passed build 23/base attribution and bounded production ZIP
  export after restart. The fixture is debug-only and absent from release.
- Bundle-derived non-debuggable universal and four-part split installations
  passed Original startup, rendering, process stability and durable test-data
  preservation with renderer validation off and on. Locally owned game data
  was seeded in this disposable install; this was not a new import-flow test.
- Actual startup logs reported normal and validation-and-robustness modes.
  Health samples confirmed false/true. The chooser's durable setting survived
  cold restart; disabling it again was reflected in the next game process.
- On the release candidate, system bars initially visible in the earlier build
  were hidden during Original rendering. Visual checks covered entry, game-menu
  dismissal, Home/return, transient edge-swipe visibility and subsequent hiding.
  Window insets confirmed status/navigation sources invisible after return.

## Limits and follow-up

#119 has a reproduced Android correction; reporter/device acceptance is still
open. #102/#104/#120 received the beta and one focused actual-game comparison.
No Adreno graphics correction, sustained-performance result or physical Android
acceptance is claimed. The tablet's successful 4:3/internal-storage race changed
two variables and does not isolate a cause. Validation is off by default and may
reduce performance when enabled.

#105 supplied source versions, an existing shared-NAND rating file, matching
friend codes and a completed race without rating parity. The guidance now
accounts for the configured NAND location. Save/rating companion transfer and
network rating synchronization are separate next investigations; this beta
contains neither complete Retro migration nor automatic Syncthing support.

macOS PR #112's revised head `271fdc1` has a separately audited local Apple
Silicon candidate. Its trigger and native-layout corrections pass local tests;
physical controller/race/Retro acceptance and portable contribution notes remain
open. See [the macOS review record](macos-pr112-review.md). No new iPadOS fix
was established for the external-output report, so no new IPA was generated.
