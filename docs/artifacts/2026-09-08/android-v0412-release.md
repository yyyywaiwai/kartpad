# Android 0.4.12-android.1 testing release

Published 8 September 2026 as a prerelease, without changing GitHub's latest
release (v0.4.11). [Download](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.12-android.1).

Source tag `v0.4.12-android.1` resolves to
`6d686882778dcdef8d3ec6979005265a3228d37b`. Version code 22; package
`dev.kartpad.android`; ARM64, API 28 minimum / API 36 target; non-debuggable,
shell profiling disabled. Public signer retained:
`c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.

| Published file | Bytes | SHA-256 |
| --- | ---: | --- |
| KartPad-v0.4.12-android.1-arm64.apk | 110327122 | `ce42a501c9e14d616e096511fc17329541fbc6e31dc2ab9e6d0f9066094b0c56` |
| KartPad-v0.4.12-android.1-notices.zip | 89991 | `f78fcc9f23c5c1425715bc4bdd8aea06f5a747954ea225f310717e82b345ea5d` |
| SHA256SUMS | 206 | `1818a32dde377739c9e87e5bb2e373db41559eaff8bb36ba9991cf1f96046ca6` |

The private AAB is 91,226,535 bytes, SHA-256
`7bb38696ee8e19f5f244972d811773bc09159e17ef3ec18dfe475a1669284d2c`.
It is not uploaded. Rebuilding the final merged source reproduces that bundle;
two signed APK derivations match each other and the tested playable candidate.
All three public assets were downloaded anonymously to a fresh local directory
and compared byte-for-byte. The downloaded APK passes the package audit and
signature verification. Hosted provenance identifies the exact tag commit,
APK/native-library hashes and pending physical acceptance correctly.

The notices ZIP contains 26 allowlisted text/license/provenance entries. It was
inspected before publication and read back afterward. No disc image, extracted
game assets, Retro pack, save, private translated source, signing material or
device identifiers are included. Compiled translated game logic is included
under the existing community distribution boundary; upstream rights remain
unresolved.

Validation: all 140 Python tests, host Kotlin save/identity tests, Android
release lint, source-pin checks, repository safety, bundle/package alignment and
content audits. Signed playable emulator acceptance covers full disc import,
Original startup, profile-specific save restore/cold-start application and
preservation of old data when extraction fails. See
[save transfer](android-profile-save-transfer.md) and
[import failure](android-import-storage-errors.md) for the exact cases.
Disposable emulators created for this pass were stopped and removed; the
pre-existing emulator and physical phone installations were preserved.

The release is for reporter testing. Physical acceptance and the PC WiiCompiled
Retro Rewind/PAL migration remain open. No renderer, frame-pacing, Fill Screen
or external-output fix is claimed. The [separate graphics diagnostic](android-renderer-followup.md)
continues that investigation. The new macOS controller/settings PR #112 received
a confirmed profile-preservation review finding; it was not merged in this pass.
