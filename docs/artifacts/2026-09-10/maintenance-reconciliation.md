# Maintenance reconciliation and coordinator validation

Reviewed10September2026 against main `26d1aa2`, all 23 open issues (including new
#184), both open PRs, latest public release metadata and prior task evidence.
This pass changes documentation and coordination tooling, not the game runtime.

## Evidence reconciled

- Android 63 and Apple 34 are published; source delivery and owner Android acceptance
  are complete. Older public-hold/local 29/device25 instructions are superseded.
- #135 startup and #105 offline rating restore have reporter confirmation. Remaining
  FPS, Mii and sync concerns remain separately queued.
- PR #112 latest `a332264` source/harness clearance is distinct from old physical tests;
  PR #157's reproduced viewport defect still needs attributable game acceptance.
- PR #173 pack replacement save preservation does not resolve #169 ordinary-exit loss.
- Fifteen of the23 open issues concern Android, including #184. Seven missing
  Android labels were added after checking supplied platform evidence (#131/#137/
  #143/#166/#167/#169/#184); #184 is also an enhancement.
- The former two local schedules were deleted before this work. The replacement
  uses the [current runbook](../../MAINTENANCE-AUTOMATION.md), not the historical
  prompts. Actual enabled schedule/next-run state belongs to the desktop scheduler;
  private activation and ownership receipts supplement this source record.

## First support pass

- [#184 initial answer](https://github.com/chrissotraidis/kartpad/issues/184#issuecomment-5613974997):
  current remapping excludes D-pad/right shoulder. Scoped the feature, no unrelated
  logs or release date requested/promised.
- [#123 code 63 comparison](https://github.com/chrissotraidis/kartpad/issues/123#issuecomment-5613975589):
  published scheduling correction, familiar online menu and offline control;
  freeze causality remains unconfirmed.
- [#104 code 63 comparison](https://github.com/chrissotraidis/kartpad/issues/104#issuecomment-5613975903):
  relevant initial render-state correction, same character selection/grid;
  no Adreno fix claim or repeated validation/import test.

The test ledger marks both comparisons pending. Each public action was begun and
completed through the local receipt helper with its actual URL. Repeating all
three action keys returned `dispatch:false`; no duplicate comments were sent.

## Tool validation

The standard-library helper serializes local mutations, requires persisted owner
tokens, and records pending before an external action. Explicit recovery rotates
tokens; verified-not-posted retry uses an exact prior-attempt timestamp. Neither
elapsed time nor shell exit releases ownership. It does not execute remote actions
or guarantee exactly-once delivery across GitHub and the filesystem.

All11 CLI tests passed in the implementation and independent review runs:
competing claims, competing begins, stale owner rejection, pending survival,
immutable completed receipts, explicit retry and competing retries, corrupt-state
rejection, required evidence/absolute shared path, and safe token arguments.
Independent validation caught URL-safe random tokens beginning with a dash;
claim/recover now prefix them and a deterministic regression covers both paths.

The [PR185 CI run](https://github.com/chrissotraidis/kartpad/actions/runs/34444011448)
passed the same 11 tests on Ubuntu/Python3.12 at source `9c61f35`.
A small GitHub PR workflow runs only these portable coordinator tests. It is not
native build, storage-fixture, physical-device, gameplay or cross-platform acceptance.
Markdown links and diff whitespace are checked before integration. The earlier
Android handoff is retained under docs/archive with relative links adjusted.

## Runtime and release boundary

No app runtime correction, new package, game benchmark, device operation or X post
was performed in this pass. The X draft quotes earlier local rendering-mode
comparisons: conservative 15.7% warm-menu and 1.36% stationary-scene FPS differences.
These do not compare old/new public APKs or establish an across-device speedup.
Scheduled IPA publication remains prohibited. New APK/Mac publication in the
pilot also requires a separate explicit manual release assignment.

Current work, candidate identities and test requests: [maintenance board](../../MAINTENANCE-BOARD.md).
Exact released artifacts: [platform verification](platform-release-verification.md).
