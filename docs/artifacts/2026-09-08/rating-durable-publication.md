# Rating importer review corrections

Isolated branch codex/rating-durable-publication, based on f1338f6. No game
build, device install, Pixel command or user-state mutation performed.

## P1: checked publication barriers

AtomicFile.finishWrite may log sync/rename failure without throwing. Rating
writes now call checked Os.fsync on the output descriptor before finishWrite,
verify the final bytes/length and absence of .new/.bak recovery files, and
sync the containing directory. The parent entry for SaveBackups is synced as
well, including on retry after mkdir. The backup must complete these barriers
before live publication starts. The request is deleted only after live
publication passes. Failures keep the request and completed backups; gameplay
remains blocked. If the live rename succeeds but directory sync fails, live
bytes may already be replaced, but the durable original backup and pending
request remain. No false all-or-nothing claim is made.

Host AtomicFile models nonthrowing rename failure (all .pul, backup-only,
live-only and pending-stage targets) and a logged failure of its redundant
sync. Checked file/parent/directory fsync failure injection covers the earlier
barrier. A redundant AtomicFile sync failure can succeed only after the
explicit checked data sync already succeeded. Tests also retain normal merge,
latest unrelated records, cancellation, identity guards and backup recovery.

## P2: refuse unresolved configuration syntax

The importer retains default-NAND-only policy. Instead of a regex that misses
valid TOML keys, it accepts only simple bare-key/scalar configuration lines and
bare section names. It refuses custom nand_root, quoted/dotted keys, inline
tables, multiline values and other unsupported syntax, at both stage and
apply time. This conservative policy can refuse valid manually formatted
configuration even without a NAND override; it explains that restriction and
never edits configuration or guesses a destination. Normal shell-generated
scalar configuration/comments remain supported. Full TOML configuration
resolution is deliberately not duplicated in Kotlin.

Eight quoted/literal/dotted/inline/escaped-key examples were compiled and
parsed with the runtime's toml11 header; every one resolves paths.nand_root
to the alternate directory. All are rejected by the importer. A config change
after staging also stops apply while retaining request/live data.

## Validation

- 178 rating-storage checks and52 companion-format checks pass in the focused
  identity JNI/host suite, along with all existing save/identity cases.
- Running the new harness with the pre-fix RatingStorage source fails at the
  silent pending-publication regression (expected failure).
- Runtime toml11 probe:8/8pass; four existing deprecated-literal warnings.
- Android compileDebugKotlin passes in12s,19tasks(2executed,17up-to-date). Initial
  compile found O_DIRECTORY absent from public SDK; corrected to checked
  directory + O_RDONLY. No native/full game build.
- Diff/shell checks pass. Evidence retained under build/rating-fix.

Physical filesystem-failure/restore acceptance remains untested; do not offer
rating-restore device testing until coordinator review/integration. The prior
no-game-process claims in investigation-acceptance-checkpoint.md are explicitly
marked superseded by the PID correction and thermal-confounded owner run.
