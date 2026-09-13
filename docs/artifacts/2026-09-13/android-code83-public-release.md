# Android 0.4.18 code 83 public release

Published 2026-09-13 at 09:37:50 UTC: [v0.4.18-android.1](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.18-android.1).

- Clean compiled source: `c9d8a7fba9e5798e311570a605c61f336eab1169`.
- Final release/tag packaging source: `2cea47f0ae32719fe2f8557f2bbd4251f4317304`.
- Native libraries match the owner-accepted private code 82 candidate. Release wrapper sources are the same; version, release BuildConfig, manifest/provenance and packaging differ. A debug-signed release twin has all 155 ZIP entries byte-identical to the public APK, with only the signature block differing. The twin was not installed on the phone.
- Public community signer matches earlier public APKs. The owner’s phone remains on matching-private-signer code 82; do not uninstall to force a public-signature transition.

| Public asset | Bytes | SHA-256 |
| --- | ---: | --- |
| APK | 112625049 | `6eefdbe1d39627014595b9a6d50a79d0aab920eaf732a39ed8f6c5be362e9c9e` |
| Notices ZIP | 93972 | `319d396c25e41bbf58a55a0abf21c6121db824b42ca5da95325eafbaa5c01dce` |
| Source archive | 363778867 | `8d76c6fb45651cb6c5999176e6684ae4fa63c172a7a512627180aa2c274b2002` |
| SHA256SUMS | 312 | `bae8afbb8d636c4543c6017b280f70a34e36e827712e59d0065b8079caca4057` |

All four server-side asset sizes/digests matched before publication. Standard local APK/AAB audits, public signer verification, repeat byte-identical APK derivation, source-component hashes and allowlisted notices packaging passed. The AAB is local only and is not a published asset.

GitHub pull-request creation repeatedly returned server errors. After reviewing the complete release branch and passing the seven focused release tests, the branch was fast-forwarded to main through a normal Git push; GitHub branch rules remained in force. No required check was bypassed. Documentation acceptance PR #268 and continuation PR #252 had already merged.

See [code82 physical evidence](android-code82-device-candidate.md) for the verified backup, preserved data, startup/UI checks and owner’s general gameplay acceptance. No specific Item Rain or online result is inferred; #248 remains open. All four hosted assets were then downloaded without authentication and matched their expected bytes and SHA-256 values. The downloaded APK passed the standard release APK audit again. Local verification receipts are retained under the release worktree’s `build/hosted83-verification`; only public-safe results are recorded here.
