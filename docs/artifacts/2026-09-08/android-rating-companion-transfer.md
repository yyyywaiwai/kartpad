# Android rating companion transfer — local implementation

Continues the #105 prerequisite in `codex/rating-companion-validation`, based
on main `7878986` and helper commit `45f9428`. This is not a public migration
release. The public Android .2 APK does not contain this UI.

## Workflow and behavior

Manage Saves now offers **Restore Retro Ratings…** for both Retro profiles.
First restore the raw save, restart, and let Retro create its local rating file.
Then choose the matching PC `RRRating.pul`. The confirmation explains shared
ratings, backups, offline verification, and the separate Mii/server boundaries.
The existing saved picker-profile state also covers this action across activity
recreation; invalid/missing state rejects the result.

The helper validates the whole raw save's existing core checksum and reads
online IDs from active RKPD licenses at `8 + slot * 0x8cc0 + 0x40 + 0x1c`.
Zero IDs are skipped; empty, duplicate, negative or reserved IDs fail. All online
IDs in the selected save must have source ratings. This is local matching, not
proof of server ownership or a claim of successful online synchronization.

Staging writes only a private request with source bytes and matched IDs. Pending
raw-save and identity edits exclude rating staging, and a pending rating restore
excludes raw-save/identity changes. At cold start, before SDL loads, save IDs
must still match. The latest destination ratings are merged, backed up to a
unique file under `SaveBackups`, then atomically published. Any failure prevents
gameplay and retains the request and backups. Retries preserve unrelated records
written since staging; no input save, Mii or identity is replaced by this action.
The cold chooser offers cancellation of a staged request, preserving current
ratings and backups. Cancellation does not undo an already completed restore.

This intentionally uses two stopped-game steps instead of a partially applied
combined raw-save/rating transaction. Full Mii migration remains unimplemented.

## Runtime path evidence

Pinned Pulsar `93ba8c8a486bd771c97ffc8b68fd504f47f742b5` reads marker
`0x800017D8` in `PulsarSystem.cpp` to force NAND IO. Prepared Android runtime
`src/system_bridge.cpp` sets that marker to 1. `NANDIO.cpp` prefixes the mod path
with `/shared2/Pulsar`. `nand_fs.cpp` redirects only the title data directory;
shared2 stays in managed NAND. Thus both Retro save modes share
`KartPad/NAND/shared2/Pulsar/RetroRewind6/RRRating.pul`.

The importer requires that destination already exist and validate; it does not
invent a path or create the runtime's initial rating file. Explicit `nand_root`
configuration is refused, including a manually specified default path. Broader
custom-path support requires a shared runtime resolver and is not implemented.

## Validation

- 52 pure rating checks plus 64 synthetic storage checks pass on the host.
  Both Retro modes cover ID mismatch, identity/raw-save conflicts, backup failure,
  publication failure/retry, latest unrelated records, retained backups,
  unchanged save bytes, missing destination and custom-NAND refusal.
- Existing executable JNI identity and three-profile save suites pass.
- All 66 Android Python contract tests pass.
- Debug APK assembly and release lint pass in the isolated checkout, using a
  copy of the existing SDL AAR and read-only installed dependencies. This APK is
  a source-only fixture, not a playable game candidate.
- Disposable API 36 ARM64 emulator: real Android AtomicFile fixture passes for
  both Retro profiles, including retained backups and unrelated rating records.

- Actual Manage Saves UI and DocumentsUI pass on that emulator with host graphics.
  With “Don't keep activities” enabled, selecting a synthetic rating file returns
  to a confirmation naming Retro Rewind; the staged profile, IDs and bytes match.
  The chooser cancellation button removes the request without changing ratings.
  The lifecycle setting was removed after testing. Screenshots and logs stay in
  the isolated checkout's ignored `.android-bootstrap` directory.
- Software graphics mode initially aborted in the source-only Dawn device setup;
  host graphics passed. This is recorded as a fixture/environment limitation,
  not treated as evidence about the reported Adreno or Pixel game failures.
- `git diff --check` passes. Latest complete debug build/lint: 5 seconds;
  Android contract suite: 66 tests in 5.270 seconds.

Remaining: playable candidate build, Christopher's real-save offline verification,
Mii migration, and separately controlled online login/rating synchronization.
No physical phone data was touched. No public response, push, APK release or IPA
publication was performed. Apple code and device acceptance are unchanged.
