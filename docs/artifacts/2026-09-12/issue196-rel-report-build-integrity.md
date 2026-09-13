# #196: REL report guard and compiled-shard integrity

The source/build defect is corrected by this change. The iPhone 17 Pro Max / iOS 27 issue remains open and awaits a new signed candidate and matching physical-device acceptance. No APK, IPA, installed app, save, simulator or device was changed during this pass.

## Verified defect

The [published build audit](https://github.com/chrissotraidis/kartpad/issues/196#issuecomment-5642179928) established that v0.4.16-ios.2/build 36 retained the faulting aggregate-shard load. Reviewing `TranslatedBuildShardEmitter.ReadBaseFunctions` explains why modifying a standalone function was insufficient: it prefers its cached source bundle when present. The emitted aggregate is a separate source boundary.

A second defect was independently reproduced in the existing private aggregate on September 12: its old guard repair had removed `r29 = 0; goto loc_8000A510;`. The standalone retained those statements. Without the initial count check, a zero-section report could dereference an unused table pointer, while a valid report could use the caller's old loop counter. The old verifier accepted that broken control flow.

These findings establish a build-integrity failure and an unsafe diagnostic path. They do not establish why the original REL pointer was invalid, or a shared cause for Android exit, online, graphics or performance reports.

## Correction

- Add the narrow `TryGetRelReportSectionTable` helper to common Apple/Android preparation and macOS preparation. Check header/table alignment, guest-memory membership and arithmetic before flat reads. Preserve valid reports and zero-section behavior.
- Apply the same transformation to standalone and aggregate definitions after emission. Preserve loop initialization, initial count check and the generated epilogue. Reject old/partial guards and require regeneration; do not repair them by deleting control flow.
- Inspect the literal compiled sources in `shards.cmake`. Require exactly one compiled definition; an unused guarded file cannot substitute for an unguarded compiled one.
- Enforce the guard before iOS device/simulator, tvOS, Android and macOS builds and before personal-builder cache reuse. Base, online, Retro and legacy generation entry points guard emitted output too.
- Run portable compiled regressions and builder checks in GitHub CI. Public fixtures are synthetic and contain no game-derived source/data.

## Validation and limits

Ten focused tests pass. Compiled C++ tests under ASan/UBSan exercise 14 cases: valid and empty tables; null, unmapped, unaligned, truncated and wrapping headers/tables; failed safe reads; count overflow; and the last valid table entry. Assertions check iteration count/data and stack, link and callee-saved register restoration.

Five compiled negative controls fail as expected: original unchecked header/table reads; missing initial loop check on empty and valid tables; and an early-return guard that fails stack restoration. Fresh-generation and cached-builder regressions reproduce the cached-bundle/standalone mismatch. Missing/duplicate graph definitions, guarded decoys and partial guards are rejected without modifying input. The helper patch applies with zero fuzz to the pinned runtime after its existing dual-profile patch.

Independently compiled the actual private generated function with guest report calls stubbed, under ASan/UBSan: all 14 cases pass. Its old aggregate fails the empty-table and valid-iteration negative controls. Fresh injection into a temporary unguarded copy reproduces the tested corrected function exactly. Private inputs remained unchanged. The local check script is `build/maintenance/check-private-rel-control-flow.py` in the isolated worktree; private generated inputs and temporary binaries are not committed.

Builder suite: 25 tests, 24 passed and one private-payload test skipped in the isolated checkout. Existing generated-link contract passes; changed shell scripts pass syntax checks.

This is host control-flow/build-input evidence. It is not a full application build, new simulator acceptance, physical-device acceptance or a release. Earlier simulator passes remain historical observations of that executable; the newly demonstrated aggregate defect means that candidate must not be promoted as the final corrected build.

## Exact next gate

Use a clean checkout containing this change, regenerate translation into a fresh private output, and prepare a fresh runtime. An old translation that fails verification must not be bypassed or relabelled. Record the immutable source commit, generated/compiled shard verification, unique build version, binary hash and signing identity in the private handoff. Verify the guard and preserved control flow in the compiled candidate before delivery. Preserve existing app data during installation.

The matching iPhone 17 Pro Max / iOS 27 tester must then accept Original and Retro Rewind 6.12.8 launch, race and relaunch. Online login/lobby/race/results/repeat/reconnect and release acceptance remain separate gates. Do not close #196 from host tests or repeat requests already answered by the reporter.
