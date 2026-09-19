# KartPad source maintenance migration

Baseline: `dd79c936e5f32dde2d5a003798163cf615935c0d` (main, 2026-09-14).
Upstream stays at `1912292c804ff9b1b79938de89369ec4496f9fff`.

## Scope

Keep the existing KartPad repository, public history, issues, releases, attribution,
application identities, signing, user data and supported platform behavior.
Work in an isolated checkout. Do not overwrite the concurrent dirty checkout.
The migration changes source maintenance; it does not update the upstream version.

Import WiiCompiled as a squashed Git subtree at `vendor/wiicompiled`, recording the
exact upstream base and preserving its notices. Convert translator changes first,
then compare runtime/Aurora preparations for macOS, iOS/iPadOS, Android and tvOS.
Do not use one platform's prepared source as the others' source.

Runtime review found 59 platform-dependent paths, including unguarded behavior
changes. The runtime migration therefore uses one proper WiiCompiled fork with
four source branches and ordinary pinned Git submodules at `vendor/runtimes/`.
This replaces replay without unifying platform behavior in the same change.
The existing translator subtree and its native-registration source stay separate.
Gitlinks pin runtime revisions; branch names are development destinations, not
floating build dependencies.

## Gates and sequence

1. Preserve a full local checkout copy, Git history bundle, dirty/index diffs and
   source manifest. Verify bundle restoration and working-source checksums.
2. Import the pinned source. Audit imported files, preserve upstream notices and
   demonstrate a subtree update and upstream-only change export in a disposable
   checkout. No production source selection changes in the import commit.
3. Materialize the eight translator patches as ordinary source changes. Compare
   every translator source file and the staged native-registration source against
   the old preparation path. Build and run translator tests; compare generated
   output from identical available inputs. Keep the public helper path stable.
4. Inventory runtime preparation order, conditional patches, copied/generated
   inputs and platform differences. Compare fresh baseline preparations before
   changing any runtime build source. Migrate common/platform code in bounded
   commits, with each supported product and platform retained.
5. Update cache/provenance inputs, release-input accounting, source packaging,
   tests and contributor instructions with each consumer change.
6. Require affected native builds and in-place device/gameplay acceptance before
   promoting a runtime migration. Missing hardware or build capacity is an open
   gate, never a successful validation. Retire active patches only after parity.
7. Rehearse the next upstream update separately. Write the other-project plan
   from demonstrated KartPad results only after migration acceptance; include
   real upstream/fork relationships, source pins, contribution routes, licenses
   and attribution rather than treating a fork badge as sufficient.

## Rollback

The original checkout and stable releases remain available throughout. Each
migration stage is a separate commit; stop using the candidate checkout to return
immediately to the original working setup. Record import and migration commit IDs
in the local evidence ledger. Before merging, test reverting the consumer change
in a disposable branch and confirm it selects the original source again.

If patch retirement has landed, revert that cleanup commit first so the old
preparers can find their inputs. Then revert runtime integration and, if needed,
the translator consumer change. The source import itself may remain inert.

After a shared-branch merge, revert the consumer commits normally; do not reset
or force-push shared history. Revert a subtree merge with its correct mainline only
if removal is necessary and all consumers have already been restored. Never delete
unrelated concurrent work. For a published build regression, release a correction
with the same identity and a higher build/version code; do not uninstall or wipe
user data to force a downgrade.

The full rollback rehearsal used the candidate-only range
`a3f90eb..a938d8a` with `git revert --no-commit`, followed by a normal commit.
Its index tree exactly matched `a3f90eb`. Reverting `a3f90eb` afterward restored
the translator preparer as well. This range is an evidence record: on a later
shared branch, select only the migration commits after checking intervening work.
Do not blindly revert an open-ended range containing unrelated changes.

## Acceptance status

This document is the implementation plan, not a claim of completed migration.
Validation evidence and remaining gates belong in `VALIDATION.md` as work proceeds.
