# Android rating companion validation prerequisite — issue #105

Source base: merged main `7878986af648f6d7a0bb96cfc459ac4031bead62`.
Implementation branch: `codex/rating-companion-validation`.

Follow-up: [local picker and stopped-game transfer](android-rating-companion-transfer.md)
implements callers for this helper; it is still not a public release.

This initial step was a pure byte-validation and merge helper, not a completed importer or a
fix shipped in an APK. No app UI or storage path calls it yet. It deliberately
has no filesystem, logging, identity mutation or network operations.

## Source contract

Reviewed local `ref/upstream/rr-pulsar` at
`93ba8c8a486bd771c97ffc8b68fd504f47f742b5`:

- `PulsarEngine/Network/Rating/RatingSave.cpp`: big-endian `RRRT`, version 1,
  100 records of signed profile ID / IEEE float VR / IEEE float BR / flags,
  with an 8-byte header and the writer's 32-byte tail (1640 bytes). Production
  profile IDs must be positive and below 1000000000. IDs, not license slots,
  select ratings. A new entry can have one rating still zero.
- `PlayerRating.hpp`: maximum rating 10000; the loader also sees ratings
  initialized from original integer points divided by 100. The helper accepts
  finite values from 0 through 10000 without rounding or adjusting them.
- `RatingSync.cpp`: login downloads and reports are separate network work.
- `IO/NANDIO.cpp`: NAND paths prepend `/shared2/Pulsar`; selecting the actual
  Android runtime path is still integration work.
- `GameSource/MarioKartWii/RKSYS/RKPD.hpp` and
  `GameSource/core/rvl/DWC/DWCAccount.hpp`: save licenses carry `gsProfileId`.
  Extracting and verifying those IDs is still caller/integration work.

The helper accepts only the pinned writer's complete version-1 shape. Although
upstream's loader tolerates shorter counts/truncated reads, the migration helper
rejects those inputs rather than silently migrating partial data. Unknown flags,
duplicate active IDs, reserved IDs and invalid active ratings are rejected in
both source and destination. Inactive entry payloads remain opaque.

The caller explicitly selects one to four profile IDs. All must have source
ratings. Matching destination records are replaced; new records use inactive
slots; insufficient capacity fails without evicting any unrelated profile.
Every unrelated destination byte, including the tail, remains unchanged. A
missing destination starts an empty version-1 file. Inputs are never mutated.
Error messages contain no profile identifiers or rating values.

## Verification

`KARTPAD_TEST_JDK=/Users/chrissotraidis/GitHub/kartpad/.android-bootstrap/jdk-17.0.20.1+1/Contents/Home scripts/test-android-identity-host.sh`
passes: 52 synthetic rating checks, plus the existing executable JNI identity
and three-profile save suites (including backups and interrupted publication).
The optional JDK override lets an isolated checkout reuse the installed JDK
while placing compiled tests and generated fixtures in its own directory.

Rating checks cover reordered matching IDs, selective first import, idempotence,
input immutability, unrelated bytes/tail preservation, malformed headers/lengths,
duplicates, reserved IDs, unknown flags, NaN/infinities/range limits, missing
matches, empty/oversized selections, full-table rejection and update, and opaque
inactive slots. All inputs are synthetic, not reporter files.

The Android Python contract suite also passes: 66 tests in 5.580 seconds.
`bash -n scripts/test-android-identity-host.sh` and `git diff --check` pass.

## Remaining implementation and acceptance

Before UI integration: extract and validate IDs from matching saves, resolve the
actual shared runtime rating path for both Retro save profiles, stage a combined
save/rating transaction with prior-file backups and recoverable publication,
exclude identity edits, and apply only before runtime starts. Mii migration is
separate. These prerequisites are not bypassed by this helper.

No APK/IPA was built or published; no physical device or real save was accessed.
Only Android Kotlin source and host tests are affected; Apple builds are unchanged.
After integration, test Android DocumentsUI recreation, stopped-game restart,
interrupted recovery and unrelated-profile preservation on emulator and device,
then Christopher's offline license/Mii/rating checks and separately controlled
online synchronization. The reporter's PC migration remains unaccepted. Apple
save UI parity and Apple device tests are not provided by this change.
