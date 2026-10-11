# Clean RC2 — captured socket-send errors

Android code175 (0.5.1-rc.2), iOS/iPadOS build64 and macOS build64 compiled from
clean source f8e295a2fce61a1649768840f6f051e564f8e5f3. All prepared runtimes were
verified against their maintained pins before compilation. Both hosted CI jobs
pass for this source revision.

These candidates include the [socket send-error correction](socket-send-error.md).
Android uses the existing public release signer and passes bundle/APK audits.
The unsigned Apple app and Mac app pass their platform audits. Package ZIP CRCs
pass. Matching Android unstripped symbols and iOS dSYM are retained privately.

The public IPA publication script remains pinned to an older accepted release and
correctly rejects build64. The same local-candidate packaging path used for RC1
was used here; no public acceptance gate was relaxed. No release was published.

The coordinated source packager verifies the clean APK/IPA source fingerprint and
Mac source commit against the recursive core snapshot. Independent readback then
verified SHA256 and size for all 84 listed payload members (85 total including the
source manifest). The previously audited native and Maven dependency sources are
unchanged. Final APK, IPA, Mac ZIP, full source and notices checksums pass readback.

Local artifacts are in build/release-051-rc2-20260922. Exact hashes and the shared
source fingerprint are recorded in [clean-rc2-packages.json](clean-rc2-packages.json).
RC1 and its symbols remain intact as comparison artifacts.

## Exact-package follow-up

The isolated API36 ARM64 emulator accepted the exact public-signer APK as an
in-place174-to175 update. App UID and all four synthetic identity, Original-save,
Retro-save and preference sentinels remained unchanged through chooser launch.
After that check, the two byte-asserted synthetic save files were removed only
from the disposable emulator so they could not act as invalid game saves.
Previously staged private owned game data remained in place; this was not an
importer test. The game reached the Original title and then attract-mode scenes
without injected game input during a60-second observation. The same process
remained alive at all five checkpoints. Screenshots were inspected directly;
this is not a driven race or a physical GPU benchmark.

An exact copy of the packaged Mac app was started alongside isolated portable
userdata with networking disabled. It seeded managed NAND settings from the
synthetic legacy serial123456789, kept ConsoleIdentity.txt unchanged, stayed alive
20seconds and exited with status0. This checks migration/startup, not online play.
The test fixtures are outside the release directory; the public archives were
not modified. Private evidence is under work/mobile-network-repair-20260922.

GitHub's latest issue activity remains #216 on September21; no new reporter
result supports closing the renderer tickets. Both hosted CI jobs passed at the
preceding documentation revision bbe7ddf.

## Acceptance still required

The corrected code has host sanitizer coverage for send-error preservation;
these offline package checks do not identify or resolve the owner's iPad WFC94020
failure. Android geometry and Moto G85 idle reports remain unresolved. Neither
unavailable physical device was accessed. The emulator was shut down after the
observation. Keep the WFC publication hold and retain RC1 as a comparison artifact.

## Version-matched Retro startup on Mac

Downloaded the pinned6.12.8 archive into a private test fixture; verified its
1,859,035,109-byte size and SHA256, expanded-size/path safety, and the pinned
Code.pul/XML sizes and hashes. The exact Mac64 packaged executable (hash compared
with the test copy) then selected the retro_rewind translated profile and applied
4,878 overlay registrations. The Retro Rewind title was visually observed through
the native app screenshot. The save redirect resolved under the disposable
fixture's sd/riivolution/save/RetroWFC/RMCP; networking remained disabled.

The first environment-only attempt selected Original because the Mac shell reads
its saved profile selection. That attempt is not Retro evidence. The successful
attempt used the app's Game menu and a restart. The prior Original selection was
restored through the same menu afterward, and the app exited with status0.
No owner saves, online login or driven race were used. Android/iOS exact-candidate
Retro acceptance remains separate from this Mac result. Private receipt:
work/mobile-network-repair-20260922/mac64-retro-receipt.json.

## Version-matched Retro startup on Android emulator

The exact public-signer code175 APK also visibly reaches the Retro Rewind title
in the disposable API36 ARM64 emulator. All3,643 staged Retro6.12.8 files were
hashed on the emulator and matched the verified local fixture. The launcher
validated the installed pack and populated its relative root in Config.toml;
the normal runtime-profile intent selected retro_rewind. The runtime log records
requested=retro_rewind and installed=valid. Networking and Discord were disabled.
The same game process remained alive at three checkpoints over30seconds; the
title was inspected directly. This is startup evidence, not a driven race or WFC
login test, and staging files does not test the in-app downloader/importer.

The first staging attempt exhausted the emulator's6GB data partition. Generated
data for three unused emulator apps (Google search, Android System Intelligence
and Messaging) was cleared; KartPad data was retained. The resumed copy was then
fully hash-verified before launch. No physical device was accessed. The emulator
was shut down after the observation. Private receipts/logs are under
work/mobile-network-repair-20260922/emulator175-retro-files.json and
emulator-retro175/.
