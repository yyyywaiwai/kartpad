# Clean release candidate 1 — 22 September 2026

All candidates identify clean source `2886684b7ec994e685dc0bc9f097dbbdc953551e`.
Android code174 (0.5.1-rc.1), iOS/iPadOS build63 and macOS build63 compile and
pass package audits. Android uses the existing community release certificate;
Apple IPA remains unsigned. No attached mobile device was accessed.

Android and iOS embed the same recursive source fingerprint:
`cb5fa319707713a03c2c1e0c1a08ce75fa2749cabe2f137e93d42c481201db00`,
covering 7,346 files, with source_dirty=false. Mac packaging records the same
compilation revision. Every prepared runtime was checked against its maintained
source; an outdated staged Mac test was synchronized before that check passed.

The coordinated source packager verified the clean APK/IPA fingerprints and Mac
revision against the recursive core snapshot before composing the 85-member
source delivery. All delivery-member hashes/sizes and final asset checksums were
then independently read back. The archive includes the verified dependency
source delivery and current rebuild instructions, not just the core snapshot.

29 fetched CMake dependency source trees across Android, iOS and Mac were compared
file-by-file against archived dependency sources. All match except the expected
iOS SDL UIKit text observer correction. Applying the tracked
cmake/PatchSDLUIKitTextFocus.cmake to the archived SDL source reproduces that
built file exactly. Apple/Android use SDK zlib rather than the unused upstream
zlib source-download fallback. Android's separately supplied SDL AAR remains
3.4.4, with corresponding source in the delivery.

The offline Gradle releaseRuntimeClasspath resolves 39 external Maven components,
exactly matching the source-delivery manifest. All 38 archived source JARs match
the cached originals byte-for-byte and pass ZIP CRC validation. The remaining
component is the Kotlin coroutines BOM (metadata only). WorkManager's KTX2.11.1
source JAR contains only metadata/licensing; its matching AAR contains no class
files, so this is an empty compatibility artifact, not missing implementation.
The local SDL AAR is covered separately above. See
[maven-source-audit.json](maven-source-audit.json) for the per-component hashes.

Artifacts live in the ignored build/release-051-rc1-20260922 directory: public-
signer APK, unsigned IPA, Mac ZIP, complete source archive, notices ZIP and
SHA256SUMS.txt. Matching Android symbols, iOS dSYM and the unsigned AAB are
retained privately. Exact hashes and executable comparisons are in
[clean-rc1-packages.json](clean-rc1-packages.json).

## Acceptance boundary and next work

This resolves the dirty-source packaging/provenance gap, not the iPad 94020
login failure or reporter-specific Android geometry/performance defects.
Previous emulator135-to173 preservation evidence and Mac62 synthetic migration
proof remain separately labelled; neither is presented as a physical174/63 race.

## Final APK follow-up

The exact public-signer code174 APK was installed in place over public-signer
code173 on an isolated API36 ARM64 emulator. The app UID and four synthetic
identity, Original-save, Retro-save and preference byte sentinels stayed unchanged
through installation and chooser launch. This supplements the previous public135
to173 test; synthetic sentinels are not playable saves.

After that preservation check, only the two asserted synthetic save files were
removed from the disposable emulator. Existing private extracted game data was
staged there and Original started offline with SwiftShader. Nine screenshots over
120 seconds show title/attract-mode scene changes without injected game input;
the process remained alive. The first screenshot still has Android's fullscreen
education overlay, later screenshots do not. At 90 and 105 seconds the attract
scene visibly advances; the 120-second image is black, and a later follow-up again shows an attract scene. This is a
bounded idle observation, not a driven race, importer test, physical GPU benchmark
or evidence that Moto G85 issue #301 is fixed.

The actual Android event-service functions also pass a new host ASan/UBSan test:
guest-fiber requests defer native polling, pending requests coalesce, polling runs
with no input events, and a request made during service survives for the next
scheduler service. Aurora and Fiber interfaces are stubs; this does not establish
SDL/driver behavior. The test is included in shared-runtime CI.

GitHub was refreshed again: the latest issue activity remains #216 on September
21. No new reporter evidence justifies closing #301 or the geometry tickets.
The supplied #301 log identifies public135 and Adreno619; emulator SwiftShader
cannot reproduce that driver environment. Continue investigating rendering/input
progress separately from FPS counters and retain the iPad WFC publication hold.
