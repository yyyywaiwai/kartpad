# 0.5.1 release preparation — 25 September 2026

## State

**SUPERSEDED: release withdrawn after the owner reported severe iPad stutter.
See [the release hold](ios-release-hold.md). Do not publish these assets.**

Prepared, audited, not published. No release tag, GitHub release URL, store upload,
main merge, or post-release reporter replies exist from this preparation.
Android code220 and iPhone/iPad build73 are clean full builds. Mac was skipped;
its current public download is unchanged. No owner device was modified.

## Source and identity

- Compilation source: `353aea5eb61895350fe7186a7ba3a46b0e8177a3`.
- Android runtime: `c1c9cfffce278164fffe5aa913ce3e5bb7f90732` (pushed to `codex/android-review-20260925`).
- iOS runtime: `36e5f73646a3bf14fcf52e5575fd2cbce940641d`.
- IPA packaging-only source: `161fa612803de82ac66b8ca01b17725f0ca940bf`.
- Android notices packaging-only source: `a7fe3865092b26d78c62679cdb420407edeed3fe`.
- Final preparation commit: the commit containing this report, retained on
  `codex/release-051-20260925` and reconciled into PR #317's branch.
- APK certificate: `c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.
- iOS version 0.5.1, build73; diagnostics NO; executable/dSYM UUID
  `B096BDE2-5B3A-3B09-8B3F-D89D7DF744C5`.

Packaging commits change release scripts, tests and documentation only. They do
not relabel the native compilation. The source archive includes the exact
compilation snapshot and verified retained dependencies; current release
packaging scripts are also available from the final preparation Git commit.

## Assets

Local asset directory: `artifacts/release-051/` in the clean release worktree.
SHA256SUMS covers all four release assets; its own identity is recorded here.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `KartPad-v0.5.1-arm64.apk` | 169109067 | `d2e4104dfd01cd64d8589601ae2983f353da9a24446c28645898c7f68a5af58c` |
| `KartPad-v0.5.1-ios-unsigned.ipa` | 64859506 | `a824e463e529915e5626fb967f137e1b95b232937d670fe49400f1803607fce9` |
| `KartPad-v0.5.1-notices.zip` | 96745 | `2b6b0c2209b11a49e2772683eed9f418576f9e59fe79291b33d815719aff787e` |
| `KartPad-v0.5.1-source.tar.gz` | 362906821 | `26a41f8911b8cc945ef26b0b058a97430679a7978dc67fe17cada470dc714770` |
| `SHA256SUMS` | 377 | `7a509ce7ebba7323920e260323dfe9010714810570b049b41dd42c148da22f49` |

The unsigned AAB is retained locally, not a public download:
`217f160435f3ae2ed6f5d78eaa9c81f277210a301e6f28ab620585812628705b`.

## Verification

- Android AAB and release APK audits passed; public signer matches v0.5.0.
- Repeated APK derivation produced identical bytes.
- Stripped libmain lacks `Aurora: Dear Imgui` and contains `persistent=%d ref=0x`.
- iOS app and unsigned IPA audits passed; diagnostics NO and matching dSYM UUID.
- Full source archive coverage, member hashes and embedded APK/IPA source
  fingerprints matched. Retained dependency identities were checked against
  the current pins. Private translation, game images, saves, device logs and
  signing material are excluded from the delivery.
- Debug-label, eight worker-gate cases and five-file shared-runtime parity
  checks passed. Source verification, repository safety, host portability,
  guest memory/scheduler, PPC differential/translator, native subsystem and
  controller mapping checks passed during preparation.
- Original controller-lifecycle harness failed to compile against current
  declarations. A private harness using the production declarations passed;
  this is not a claim that the unchanged historical harness passed.
- Four Android release contract tests and two iOS provenance tests passed.

## Update-path result and remaining gate

A fresh disposable API36 arm64 emulator installed the anonymously downloaded
public code135 APK, then updated using `adb install -r` to the signed code220 APK.
All 2,044 staged game files were byte-identical after update. Application ID,
first-install time and data-directory inodes were preserved. No uninstall or
clear-data operation was used.

**Ready to play and gameplay were not verified.** The emulator mirror did not
respond reliably to UI automation, despite normal boot and successful package
installation. The complete update-path gate remains open. These checks do not
establish save-game correctness or physical-device performance.

Gate 0: the owner waived private Pixel219 offline/Retro-online and iPad72
Original/Retro play-session results to proceed. All four are **unverified, not
passed**. The earlier code218 Retro race is separately documented and does not
substitute for them.

## Remaining publication steps

1. Complete the emulator Ready to play/gameplay gate, or obtain an explicit
   owner decision about that remaining gate; the earlier waiver covered Gate 0.
2. Owner chooses Latest or prerelease and explicitly says publish after reviewing
   these assets and `docs/releases/v0.5.1.md`. Main merge is not assumed.
3. Tag the exact reviewed preparation commit, publish only the reviewed assets,
   then anonymously download and byte/hash/signature/IPA-mode verify each.
4. Update README downloads, STATUS and maintenance board together after publication.
5. Only then reply once on #321 and #320. No other reporter retests are requested.

## Preserved work and local evidence

The original stabilization worktree and its uncommitted `clean-rc2.md` edit are
preserved. The clean worktree `kartpad-release-051-20260925` remains under the
Codex worktrees directory because it holds release assets, dSYM, native symbols
and private audit records. It must not be removed until those are archived.
Only this preparation's regenerable intermediates were removed for disk space;
cleanup receipts are retained under `work/`. No older build or owner data was
removed. The host has very little free disk space; avoid another full rebuild.

Private logs: `work/android220-build.log`, `work/android220-notices.log`,
`work/android220-binary-check.json`, `work/ios73-build.log`,
`work/ios73-package-final-audit.log`, `work/release051-source-package.log`,
`work/emulator-update-result.json` and before/after file hashes.
