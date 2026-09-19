# Android code91 publication

Code91 is published as the [character graphics comparison prerelease](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.21-android-matrix.1). Stable Android code85 remains the general release. PR282 merged the native/UI comparison; PR283 binds its release materials. No graphics issue is closed by publication.

- App version: `0.4.21-matrix.1`, code91, arm64.
- Compiled source: `62798c932eb1320f1ed392c0cc61e06d23cc616c`, clean.
- Packaging source: `eb77f44944b5ab817bf2bede35003d2bb1f460ad`.
- APK SHA256: `31467e4cf59461e0786ac642877eb318ad1115da6d093ee9f1351961500f1188` (112645529 bytes).
- Notices SHA256: `4be06219617d3385ed91b6353979fbe497d22de0aeef679942b64b7ce97fcf6c`.
- Source archive SHA256: `cf4566bf87fb30d0f0786cc1dd19813edcb27498e2d8c50e1b400e1417d00fbe`.
- SHA256SUMS SHA256: `ba4c59c52a015d0f2f48f46b09e69aff4e5f422f84a68c00d811fc9624b95451`.

Release/server hashes match the four allowlisted local artifacts. All four anonymous public downloads were independently fetched and matched their local byte counts and SHA256 hashes. An independent APK audit confirms the Community Release signer, non-debuggable build, clean provenance, exact native hash and AAB payload equality. Host actual-shader validation and durable-setting/recreation tests pass; affected-device rendering remains unverified. Do not infer a speedup from either comparison mode.

The separate iOS anonymous-memory change is merged in PR284. Its audited unsigned build43 is local; signed-device launch and complete source-delivery preparation remain open. It does not establish resolution of #196’s missing-function fatal.
