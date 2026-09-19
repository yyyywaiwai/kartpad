# Android 0.4.19 / code85 release verification

Compiled application source: `97261697df1c3f4f4908533a5a7e3cfdbee967f0`. Release packaging source: `afed655cff4ea77acb4d04f5a00838bfc7b56a5e`. Release metadata merged through PR #274. PR #271 supplies the startup isolation, active-install recovery protection and packed-vertex read correction.

The ARM64 native runtime was relinked after rebuilding the corrected shader source; inherited graph inputs were verified unchanged. The release APK/AAB audits pass. Public signing certificate matches preceding Community APKs; debugging and shell profiling are disabled. Android release compilation/lint passed. Seventeen real filesystem cases and actual separate-process pipeline tests pass. Native boundary/shader validation is recorded in the linked source review; no fresh physical Android gameplay or measured speedup is claimed.

The corresponding-source archive contains the exact current core source and prepared runtime, with 973 outer members and 8,979 core members verified against manifests. The companion notices bundle contains 30 allowlisted entries. No private inputs or signing material are published.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `KartPad-v0.4.19-android.1-source.tar.gz` | 363801902 | `f6e4007e674f4e3d11343b65c2ecc8d7088d6a4889f314bd4b360e151827a01d` |
| `KartPad-v0.4.19-android.1-arm64.apk` | 112625049 | `49e5942eb7651e8457c28e5fd5125f19e00c95d1dde701bef8236e01981fa59f` |
| `SHA256SUMS` | 312 | `5704b725289e5d66bb29771827cd24e9a2a7a2af1392f8c6ff3ab93869890c4c` |
| `KartPad-v0.4.19-android.1-notices.zip` | 93881 | `fee5492206571303e32a33043a94934f8b36aeb4f91c821c4914d8e937eaebf4` |

Published at 2026-09-13 14:39:51 UTC. All four assets were downloaded anonymously and match the expected sizes and SHA-256 values above. The source archive was available immediately; brief initial 404s for the other URLs cleared on retry. See the [release](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.19-android.1). The hosted APK passes the release audit.

Focused release follow-ups target install/startup reports #192/#200 and graphics reports #102/#104/#120/#137/#166/#193/#211. They request the same affected path/scene on code85 and explicitly leave unresolved report causes open. No physical phone was used for this release.
