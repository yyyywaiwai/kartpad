# September 10 platform release verification

The owner explicitly authorized publication and confirmed the Android hardware
checks complete. The manual release task published these packages; the scheduled
maintenance coordinator reviewed/merged source and did not publish them.

## Published releases

| Platform | Release | Published (UTC) |
| --- | --- | --- |
| Android ARM64 | [v0.4.14-android-preview.1](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.14-android-preview.1) | 2026-09-10T05:07:20Z |
| iPhone / iPad | [v0.4.15-ios.1](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.15-ios.1) | 2026-09-10T05:07:23Z |
| Apple Silicon Mac | [v0.4.15-macos.1](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.15-macos.1) | 2026-09-10T05:07:22Z |

Android is version 0.4.14 preview 1 / code 63; Apple packages are 0.4.15 / build 34.
The iPhone/iPad release is the repository's latest release. Android and Mac are
normal published community releases without replacing that latest-release link.

## Anonymous download verification

All ten hosted assets were downloaded using curl with user configuration disabled
and no authorization header. Every byte count and SHA-256 matched the audited
local artifact; all checksum rows passed. Apple references the identical shared
source download hosted once in the Android release. Verification completed at
2026-09-10T05:08:02.080069+00:00.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| [KartPad-v0.4.14-android-preview.1-arm64.apk](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.14-android-preview.1/KartPad-v0.4.14-android-preview.1-arm64.apk) | 110355865 | `4e27897b9bb89e7b24fbe0b2e3dc66fae4efd549edaadf2f748ca22f376d87ff` |
| [KartPad-v0.4.14-android-preview.1-notices.zip](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.14-android-preview.1/KartPad-v0.4.14-android-preview.1-notices.zip) | 98704 | `d0dd7c3f126e9497c08e1efa53e6116fd3f6c85dee0f58b2aeb86a0a00e8e29c` |
| [KartPad-2026-09-10-source.tar.gz](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.14-android-preview.1/KartPad-2026-09-10-source.tar.gz) | 413259687 | `555b840673d06d8db0aae3e02faebc854cc7e9a37286567963bbfa1587613a9d` |
| [SHA256SUMS](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.14-android-preview.1/SHA256SUMS) | 321 | `64efbc609a19ab303c3e0dfcd3283614fec72c2c68f8024d709abb01b9a91cb9` |
| [KartPad-v0.4.15-ios.1-notices.zip](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.15-ios.1/KartPad-v0.4.15-ios.1-notices.zip) | 69049 | `2918d395b1104c55f8a906875ae346238d334d825ca6ccea0316b218f8c93461` |
| [SHA256SUMS](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.15-ios.1/SHA256SUMS) | 300 | `ece050d85dce68e3ff9b6a04fe973647f159d3b5205ab43fbc072602b04d8d9f` |
| [KartPad-v0.4.15-ios.1-unsigned.ipa](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.15-ios.1/KartPad-v0.4.15-ios.1-unsigned.ipa) | 45077843 | `48d0f0fb95ee0f8f1135cbe94f01fecf4636850adb595fe7ba4bd7ef6a16e4bc` |
| [KartPad-v0.4.15-macos.1-notices.zip](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.15-macos.1/KartPad-v0.4.15-macos.1-notices.zip) | 69504 | `9233aa98f5e8a8422c4da8ab66ad316718e221c42c3bb6f8fca8d122d55b9b38` |
| [KartPad-v0.4.15-macos.1-arm64.zip](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.15-macos.1/KartPad-v0.4.15-macos.1-arm64.zip) | 40807313 | `ffaf113fa7a794824e6506e727842c08204c7f4276ccad76f33401cabffc8023` |
| [SHA256SUMS](https://github.com/chrissotraidis/kartpad/releases/download/v0.4.15-macos.1/SHA256SUMS) | 301 | `4c6471f9b9e8c71e0b05c80766ee893766c94994686b0929e1ef0af12df485c1` |

The downloaded APK, IPA and Mac ZIP passed their full platform archive audits.
The downloaded APK retains the public signing certificate
`c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.
The IPA is unsigned for personal re-signing; the Mac application is ad-hoc signed.
All three app packages were independently packaged/derived twice with identical
archive bytes before upload. No phone or Apple-device installation was performed
by this publication pass.

## Source and reconstruction

- Android application: `6a2dffc30f8f0d55a7eb928c614c88e054240d14`.
- Android tag/notices packaging: `7811b038` (reviewed and merged in PR #182).
- Apple application/tag: `d3d300bb0364298b264378b13ba5561b42ca783d` (PR #180–181).
- Shared source archive metadata: `47e21b2`; source descriptions and packaging
  identity are distinct from the compiled application commits.

The source bundle contains 27 exact Git snapshots, 14 native dependency source
archives, 19 Dawn dependency source archives, 38 Maven source archives, three
modified platform runtime trees and the reconstruction recipes. All nested Git
blob/tree/commit identities and the runtime fingerprints were independently
verified. The 39th Maven component is a version-constraint BOM without code.
Fresh Android reconstruction matched all 877 runtime files, 1,105 translator
source files, 29,637 base function files, Retro source and initialization. Shard
source matches with the supplied partition map and documented path relocation.
iOS records the same 30,030-file translation fingerprint as Android.

The final source archive was assembled twice with identical bytes. The notices
packager pins that exact archive hash before checking its complete file manifest;
a forged empty manifest was rejected before any output. A broken source-guide
link and imprecise wording about an upstream tracked Code.pul resource were
corrected before publication. No private generated source, owner pack, WFC
payload, saves, raw device logs or signing secrets were uploaded.

[Source delivery](android-source-delivery.md) ·
[Reconstruction details](android-source-reconstruction.md)

## Acceptance and remaining limits

Android's non-debuggable private-signer hardware variant has all 155 ZIP payload
entries identical to the public APK; only its signing block differs. The owner
accepted this payload. Public-signer emulator updates preserved the protected
fixtures and exercised Original/Retro startup, controls and bounded lifecycle
paths. A new controlled old-public-versus-new-public performance comparison was
not performed.

Earlier local Pixel 9 Pro XL 2x/Fill mode comparisons measured warm-menu FPS
39.52–49.96 with overlap disabled versus 57.80–58.58 enabled (conservative 15.7%
gain). A stationary Retro scene measured 51.363–54.157 versus 54.894–55.728
(conservative 1.36%). Transitions still took 2.580–2.732 seconds. These are not
across-device or sustained driven-race gains. Adreno geometry and cup/awards
reports remain open.

Apple passed full builds and archive audits, 23 iOS source contracts, the actual
Metal helper regression, and 12 actual-source UIKit report checks at standard
and largest accessibility text sizes. No new full-game physical Apple acceptance,
macOS game launch, external-display fix, tearing fix or Apple FPS gain is claimed.
The new report gate is iPhone/iPad and Android; macOS/tvOS reporting parity and
PR #112's controller/keyboard work remain separate.

The README and installation guides point to these verified releases. Source
delivery and owner Android acceptance are complete. The two local schedules were
later deleted at the owner's request; subsequent coordination uses the
[current runbook](../../MAINTENANCE-AUTOMATION.md) and
[active board](../../MAINTENANCE-BOARD.md), not historical release checkpoints.
X text is a
[draft](../../releases/2026-09-10-x-draft.md); no X post was sent.
