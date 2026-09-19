# Source migration release verification — 15 September 2026

KartPad 0.4.22 is published for Android (code 93), iPhone/iPad (build 43), and macOS (build 43). All three release tags resolve to merged commit `516c57245b53ce7bb0c30fb8c0ca2b23603b4ae2` from [PR #287](https://github.com/chrissotraidis/kartpad/pull/287).

All eight assets below were downloaded without authentication and matched their audited local files. The APK download used HTTP byte ranges; the assembled file matched the full SHA-256. Package audits were rerun successfully on the downloaded APK, unsigned IPA, and Mac ZIP. Uploaded checksum files also matched.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `KartPad-v0.4.22-android.1-arm64.apk` | 112612761 | `ed81b26dffe407b7ca430505756db194456dacb28c5789c9bcdda3b587459a78` |
| `KartPad-v0.4.22-android.1-notices.zip` | 93924 | `4e129510c02f49edb645b95b4b7568563be682aaff8f3bb25bee90dd6011ca7b` |
| `KartPad-v0.4.22-source.tar.gz` | 572927172 | `9ec41dd5def8ba046ce6661f93ec1a51febd02625efeeb6f5c71c0a132d57e31` |
| `SHA256SUMS` | 302 | `e57bff75175ac5fe8269b033f21dc129694b66ef1afcd1aa6644ae3a7467b334` |
| `KartPad-v0.4.22-ios.1-unsigned.ipa` | 45810937 | `37e480982d24d7a381b8601ea54364ac7c61badcc602bcbf2d414d2cf93fe7bd` |
| `SHA256SUMS-ios` | 197 | `92ea1c8ec04475eac3abdadf29a3b2654d58595124676e06e31cdec4de078ae8` |
| `KartPad-v0.4.22-macos.1-arm64.zip` | 41492337 | `a2689d3832f004a938b78162ce15cc5940d030dcd152553b5dadaf5b1dbb168a` |
| `SHA256SUMS-macos` | 196 | `d7cf0cb44915b4b7a042955dd2b6cc6b68e4e8f15cbc34ac40eb0c8ce608f762` |

## Scope and provenance

- Android: fresh release build from `42122cebbb6e0af4f4d803050f376996878548aa`, code 93, existing public signing certificate retained. Release path normalization changed native binary bytes without changing gameplay source. The shared source bundle contains the exact Android compile snapshot, runtime sources, and dependency delivery described in [source and rebuild details](../../releases/v0.4.22-source.md).
- iPhone/iPad: build 43 retains the tested iPad executable, with updated public version metadata. Original compilation provenance is preserved. The unsigned IPA requires user signing.
- macOS: build 43 retains the tested native payload, with updated public version metadata and ad-hoc signing that preserves Bluetooth entitlement.
- The owner accepted loading, running, and starting games on Android and iPad, and explicitly waived completed-race testing as another release gate. Mac smoke reached a race and pause/resume. This does not establish sustained gameplay, all-device compatibility, or online race/reconnect acceptance.
- New-license Retro WFC login succeeded on iPad. The old-license 22005 failure reproduced on both previous and migration builds. No license, save, or console identity was reset or repaired by this release.
- Hardware testing used private candidates; this record does not claim that the public IPA/APK was installed on those devices.
- Unfinished save/Mii export changes are excluded. tvOS has no new binary. The original working checkout and rollback backup were preserved.

See the [validation ledger](../../source-maintenance/VALIDATION.md) for source parity and rollback evidence, and the [other-project procedure](../../source-maintenance/OTHER_PROJECTS.md) for subsequent migrations. Other projects were not migrated in this release.
