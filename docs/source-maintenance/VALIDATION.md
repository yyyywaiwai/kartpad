# Migration validation ledger

Status: source migration merged in PR #287. Public 0.4.22 packages use the
owner-accepted gameplay scope and audited release inputs. See the publication
[publication receipt](../artifacts/2026-09-15/source-migration-release-verification.md) for hosted-artifact verification.

- Baseline main: `dd79c936e5f32dde2d5a003798163cf615935c0d`.
- Upstream remains `1912292c804ff9b1b79938de89369ec4496f9fff`.
- Full local APFS backup verified: 1,136 tracked/non-ignored files matched SHA-256
  and mode. Git bundle restoration succeeded in an independent repository.
  This is local rollback protection, not an off-device disaster backup.
- Translator preparation: all 1,108 files match the previous preparation.
- Translator Release build and 624 tests passed. The full PPC semantic script
  passed, including differential, sanitizer and Dolphin float-oracle checks.
- Fresh Original translation: 29,637 generated functions and 72 base_common
  compiled shards match the old translator output byte-for-byte.
- Runtime preparation parity passed: macOS 850 files, iOS/iPadOS 849,
  Android 853, tvOS 849. Only patch-utility `.orig`/`.rej` debris was excluded.
  These comparisons used Original for macOS/iOS/Android and dual for tvOS.
- Tracked staging tests: runtime 10 passed; translator 3 passed. They cover stale
  output refusal, pinned identity and tracked edits rather than untracked source.
- Recursive source fingerprint/archive/offline-restore tests: 7 passed.
- Build provenance tests, including submodule source coverage: 3 passed.
- Runtime contracts: 110 passed. Focused Metal/CPU/serial/REL checks: 21 passed.
- Maintenance loop: 54 passed. Builder: 25 run, one existing skip, no failures.
- macOS controller, VSync/config and Apple guest-memory checks passed.
- Translator consumer revert, synthetic subtree update and focused upstream
  contribution rehearsal passed in disposable worktrees.
- Runtime integration commit `6b034975dd4191c1bcec313bbf137018fd67e7a2`
  reverted cleanly in a disposable worktree; all four old preparers matched exactly.
- The real 61,378,201-byte candidate source archive restored offline to that
  exact KartPad commit and all four exact runtime commits. Archive SHA-256:
  `3d1559416378374151fb596551e26029c332cc2764d717da5be7fe8a5f464d4e`.
- macOS native dual build, final incremental build, staging verification and
  final package audit passed. Runtime bytes stayed unchanged across the final
  incremental build. The audit's stale log-size expectation was corrected to
  match the unchanged baseline implementation.
- iOS/iPadOS native dual build and full app audit passed. The audit parser was
  corrected to read the platform field rather than matching the word in a path.
  A private unsigned IPA was packaged and its ZIP integrity verified.
- Android native dual build, final clean-source incremental build, APK package
  audit and APK signature verification passed. Candidate version code is 92.
- The old-preparer translator independently generated 4,101 Retro Rewind records;
  its entire source bundle matches the migrated translator byte-for-byte
  (`e9c09b39f3cf21b8fed8bbe578bd706244a77761bc04d4f2a091870aadbb264a`).
  The stale 4,095 builder guard was corrected; 11 guard tests and validation of
  the actual fresh graph passed. This changes validation, not generated code.
- Retired all 99 migrated patches after source parity and native build checks.
  No active script, test, builder or workflow references those patch filenames.
  Builder (25, one existing skip) and maintenance tests (54) still pass.
- A full rollback rehearsal through retirement commit `a938d8a` restored the
  exact pre-runtime-integration tree, then reverted the translator consumer.
  All 99 patch files and all five original preparers were restored exactly.
- Source preparation's product selection only chooses the build target; it does
  not select different runtime patches. Dual native candidates cover Original
  and Retro Rewind code; per-product gameplay remains a separate hardware gate.

## Private candidate artifacts

These are development artifacts, not accepted public releases or installation proof.
Paths are relative to the isolated checkout's `build/source-migration/` directory.

| Platform | Artifact | SHA-256 / source evidence |
|---|---|---|
| Android | `KartPad-source-migration-android.apk` | `4ff90de21de40cfc237837b3cca9ab33f2baea0f9db607abe0ff50c5b036d547`; clean source `a938d8a` |
| iOS/iPadOS | `KartPad-source-migration-ios-unsigned.ipa` | `858c8ff39809e6a7affe1a275846fceecdab110289f144b23cc2ddb158ddf321`; clean compiled source `43a1661` |
| macOS | `final/KartPad.app` | unsigned runtime `c375c03a319d3076daaf32555fa853b63079753a6e4f402d53c09dbe3e5d1ef1`; final staging and package audit passed |

## Acceptance boundaries and follow-up

- Owner accepted loading/running/game-start checks as the release gameplay scope.
  Completed races, save/relaunch and online race/reconnect remain unverified
  limitations rather than additional owner-required release gates.
- Broader macOS interactive acceptance remains unverified. Android and iPad
  candidates were installed in place; see the device pass below.
- Public metadata and packages were prepared from clean committed source.
  Unfinished file-export feature changes remain separate and are not included.
- Experimental tvOS native/device acceptance is not established.
- The [other-project procedure](OTHER_PROJECTS.md) is now available. Other
  repositories have not been migrated by this release pass.

Local evidence is under the isolated checkout's ignored
`build/source-migration/` directory. Private inputs and device identifiers are not
part of the public source or this ledger.

## September 15 physical-device pass

- Pixel 9 Pro XL (Android 17/API 37): installed private
  `0.4.19-source-migration` code 92 from clean source `a37e605`.
  APK SHA-256 `31e6e4abc6c3cdf27fa46be49c16827ae8532db452e86ea319f2204ec2ac69a7`.
  Signing identity matches the prior app. All four native libraries match the
  earlier migration APK; the private version label was clarified through the
  existing build override. Verified a full non-cache backup (6,522 entries) and
  413 unchanged durable file hashes immediately after installation.
- Android hands-on result: the user reported “android version works”; an actual
  Original Luigi Circuit race was observed. Retro title/connection screens were
  seen, but a complete Retro race, online match, and save/relaunch cycle are not
  separately accepted by that observation.
- iPad Pro (iPad14,5, iPadOS 26.6.2): installed private build 42 / 0.4.19 using
  the existing app identity and authorized development profile. Native code is
  the audited migration candidate; only private installation metadata/signing
  differs. All 32 selected save/settings hashes matched before/after installation.
- The iPad had a pre-existing Retro 6.12.7 content pack, incompatible with the
  compiled 6.12.8 runtime. Staged 3,643 matching content files separately,
  compared every file size and the required Code.pul/XML hashes, retained the
  complete old content directory, and preserved the sibling Retro save directory.
  Both Retro save files matched before/after content activation. The chooser now
  displays 6.12.8. This prerequisite content update is separate from source migration.
- macOS on-machine smoke reached an actual Original Luigi Circuit race; pause
  and resume responded after focusing the game canvas. A fresh 25-file data
  backup was verified; after a clean quit only three log files changed. Sustained
  driving, a completed race, audio, Retro and multiplayer remain unverified.
- iPad owner reports build 42 works. One existing Retro license returns the
  exact console-serial mismatch message, error 22005. A controlled in-place
  reinstall of preserved build 41 reproduced the same error; the owner
  confirmed it and the screen was independently observed. Restored build 42.
  Across the reinstall comparison, console identity, NAND and Retro saves stayed
  unchanged; configuration differences were formatting only, and runtime logs
  changed normally. A separate 34-file private recovery snapshot was verified.
- On restored build 42 the owner created a new license and reports successful
  entry to Retro WFC. This establishes login success for that license and shows
  the old-profile failure is not specific to the migration build. It does not
  establish completed online race/results/reconnect or repair the old profile.
  Keep both licenses intact; no slot move, license deletion or identity reset
  was performed by the agent.

Private backups, signing receipts, logs and artifact records remain under ignored
`build/source-migration/device-validation/20260915/`; they must not be published.

### File-sharing verification

Both iOS source plists and the exact installed iPad build 42 have
`UIFileSharingEnabled=true` and `LSSupportsOpeningDocumentsInPlace=true`.
The existing iOS package audit enforces both keys. Documents is created at
first-launch and exposed through the Files/Finder sharing feature. This does not
expose live saves or Miis under Application Support. See the Files access section
in `docs/INSTALL_IPA.md`. Android uses its existing system document pickers;
macOS exposes Application Support through its data menu. These iOS keys are not
an Android/macOS file-access implementation, nor a tvOS Files browser.

## 0.4.22 public packaging checks

The owner explicitly accepts loading, running and game starts for this release;
completed races and reconnect remain outside the claimed evidence. Public Apple
version metadata is 0.4.22/build 43, with iOS code identical to the accepted
unsigned executable and macOS code identical after stripping signing data.
Android code 93 rebuilds from clean source and adds only external runtime path
normalization to avoid disclosing checkout paths in the public library.

The dedicated clean release checkout excludes the uncommitted save/Mii export
work. All nine retained native dependency archive pins were compared with the
current runtime. The recursive source restoration test passed for the initial
release source snapshot, including all four maintained runtime gitlinks.

The broader legacy verify-sources.sh reference checks passed at the pinned
commits after isolating a clean Dolphin reference. Its supplied-WBFS container
size fixture does not match the current local image container; that historical
fixture was not weakened. The generated game-code parity and previously audited
profile inputs remain the migration evidence, not a claim that this fixture passed.

The final Android AAB and public APK audits passed after path normalization.
Repeated release signing produced identical APK bytes, using the established
certificate. Final core source 42122ce restored offline with all four maintained
runtime gitlinks. The complete shared source delivery is 572,927,172 bytes,
SHA-256 `9ec41dd5def8ba046ce6661f93ec1a51febd02625efeeb6f5c71c0a132d57e31`.
