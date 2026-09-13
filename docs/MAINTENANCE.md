# KartPad maintenance operating model

This is the operating contract for maintaining KartPad from GitHub reports to
verified releases. It exists to prevent a growing issue list from turning into
unbounded diagnostics, duplicate fixes, or release claims that the evidence does
not support.

Start at the [support-agent hub](SUPPORT-AGENTS.md) for intake, useful diagnostics,
test requests and the evidence decision. The canonical records are:

- [MAINTENANCE-BOARD.md](MAINTENANCE-BOARD.md): the current public queue,
  family assignment, state, owner, evidence and next gate.
- [maintenance-priorities.json](maintenance-priorities.json): the small executable
  priority list. This owns work ordering, local/external readiness and the next
  acceptance gate; the board links to it instead of creating a second order.
- [KNOWN-ISSUES.md](KNOWN-ISSUES.md): the public symptom and limitation index.
- [COMPATIBILITY-MATRIX.md](COMPATIBILITY-MATRIX.md): the canonical
  device/OS/GPU/build/path evidence ledger and per-target next gate.
- `docs/artifacts/YYYY-MM-DD/`: dated evidence, experiments and corrections.
- `build/maintenance/CURRENT.md`: the local artifact/build handoff; it may
  contain ignored paths but never private game data, saves, credentials or raw
  diagnostics.
- `build/maintenance/coordinator/loop-state.json`: the scheduler's durable
  cursor and repeat guard. It is not a substitute for the tracked board.
- `build/maintenance/coordinator/PRIORITIES.md`: the generated context sheet,
  printed by every selection and refreshed by normal runs. Edit the JSON source,
  not this derived view. Reload it after compaction, intake and completed work.
- [MAINTENANCE-AUTOMATION.md](MAINTENANCE-AUTOMATION.md): the coordinator
  ownership, atomic action-receipt and dispatch handoff contract.

## The unit of work is an issue family

GitHub issues are reports, not automatically separate engineering projects.
Reports are grouped only when they share a testable source boundary and a
useful acceptance gate. The current family map is:

| Family | Representative reports | Closure question |
| --- | --- | --- |
| Android launch/exit | #143, #200, #205, #208–210 | Does the selected profile reach and remain in gameplay on the affected Android build, with an identified exit class if it does not? |
| Android online session | #206 (with #123 historical evidence) | Can the current matching pack enter a real lobby, race, results and reconnect sequence on the affected target? Closed issue state is not technical acceptance. |
| Retro installation/version | #192, #194 | Does the exact supported pack import and launch on the identified Android or Mac build? Updater design is separate. |
| Android cup transition | #128, #131 | Does the classified final-race/awards boundary survive on the affected target? |
| Android renderer/geometry | #102, #104, #120, #137, #166, #193, #211 | Does the affected scene render correctly on the affected GPU with a correlated draw/shader explanation? |
| Android performance | #103, #167, #169, #195, #198, #204, #207 | After warmup, which measured hot path causes the slowdown, and does one controlled change improve it on the same target? Keep save loss and exits separate. |
| Apple aggregate-shard crash | #196 | Does a signed corrected shard survive the matching iOS 27 device path with existing data? |
| Apple A10X performance | #135 | Does the compatible iPad build remain stable and meet the reporter's performance boundary? |
| External-display recovery | #100, #199 | Does local gameplay survive the exact wired/wireless display transition and recover its surface? |
| Android input/system UI | #119, #184, #197 | Does the affected input or bar behavior work on the affected physical device, including persistence and handoff? |
| Save/rating lifecycle | #105, #169 | Does the operation preserve the correct real save/profile through the requested lifecycle? |
| Feature/compatibility requests | #90, #91, #203 | Is there a bounded, legally and technically valid scope before implementation? |
| Apple input/projection/multiplayer | #5, #91, #101, #127 | Does the specific controller, framing or two-player boundary pass on the named Apple target? |
| Project/licensing governance | #92 | Is the request documented and owned without mixing it into runtime acceptance? |

New reports must be assigned to an existing family or explicitly marked
`unclustered` with a reason. Similar wording is not enough to merge causes:
Mali, Adreno, Apple, online, renderer, and performance reports remain separate
until a controlled comparison supports a shared boundary.

## State machine and closure gates

Every family has one state, one owner, one next action and one completion
condition. The allowed states are:

1. `new` — report received; no reliable boundary yet.
2. `needs-reply` — the maintainer owes a concise question or answer.
3. `ready-local` — a safe local reproduction, source review, fixture or test can
   change the evidence now.
4. `candidate` — a private build or patch exists for one named comparison.
5. `awaiting-device`, `awaiting-reporter` or `awaiting-owner` — the next action
   genuinely belongs to the named external party. Finish available candidate,
   signing-feasibility and delivery preparation before using these states.
6. `verified-fix` — the affected symptom is absent under the family’s closure
   test, with source and artifact identity recorded.
7. `released` — the reviewed artifact passed release gates and was explicitly
   authorized for publication.
8. `closed` — the issue is confirmed fixed, superseded with a linked fix, or
   rejected with a documented reason.

An issue is not resolved merely because a contract test passes, a build
compiles, a simulator launches, a dashboard loads, or a reporter thanks the
maintainer. A family reaches `verified-fix` only when all applicable evidence is
present:

- the original failing boundary is reproduced or a justified equivalent is
  documented;
- the source change is narrow, reviewed and covered by a focused regression;
- the exact package/binary provenance and audit pass;
- the affected platform/device acceptance gate passes; and
- the reporter confirmation or release-level acceptance is recorded.

If a required device, private handoff, signing step or reporter result is
missing, the state is `awaiting-device` or `awaiting-reporter`, not fixed.

## Current evidence

Read the [board](MAINTENANCE-BOARD.md) and [device matrix](COMPATIBILITY-MATRIX.md)
for current failures, accepted subscopes and next gates. This operating contract
is stable guidance; do not turn it into another dated status ledger. Online
readiness requires each platform/profile's recorded acceptance sequence.

## One maintenance cycle

The objective is fewer affected-user failures and completed candidate handoffs.
Replies, tests, builds and audit pages are supporting work, not the success metric.
Use this priority order from `maintenance-priorities.json`:

1. Confirmed/actionable data loss overrides everything.
2. Finish the corrected iOS 27 startup handoff (#196); classify and resolve
   actionable Android launch/cup exits. These share urgency, not a root cause.
   Park already requested missing exit evidence without speculative builds.
3. Complete supported online play through race/results/repeat/reconnect, starting
   with the known Android session failure. Keep Apple physical acceptance visible.
4. Finish the affected-Adreno character experiment and correction.
5. Deliver the Helio profiler safely and pursue one measured slow-scene cost.

Preserve one active objective across cycles until its next gate has a result or
a specific external owner/action. Only a newly actionable data-loss, startup
or online blocker preempts lower-priority work. Features and general audits do
not displace this list. Track Original and Retro separately: Original Wiimmfi
is unimplemented, and no platform inherits another platform's online acceptance.

Each hourly wake starts a work session, not a one-action allowance:

1. Refresh the open GitHub issue list, comments and relevant PR state.
2. Delegate the separate support inbox when changed reports exist, including
   content edits to older comments. Continue owned engineering while intake runs.
   Record a disposition for the exact displayed revision using `--review-issue`,
   `--review-revision` and `--review-evidence`. A maintainer comment alone does
   not mark all older questions handled. Ask only for a missing discriminator;
   do not repeat existing requests or run a host test because a comment arrived.
3. Assign each report to a family and update the board with evidence, state,
   owner, next action and closure condition. Update the compatibility matrix
   when the report adds or changes a device/build/path row.
4. Continue the selected objective's next action. Artifact retention, signer
   comparison, capture instructions and delivery preparation are real local
   work. After preparation, external states require a named owner and exact
   missing action in the priority record. Then select the next ready item.
5. Finish one discriminating experiment, narrow correction or candidate handoff.
   Define before running it
   what observation would support or reject the hypothesis.
6. Verify the changed source, focused tests, package identity and relevant
   runtime path. Do not use a green host test as device acceptance.
7. Record the result in the board and a dated artifact. If the gate is external,
   name the person/device/action and stop that family until new evidence arrives.
8. Reload the full priority context after a result or intake update. Continue the
   next useful step in this wake, on the same family when possible or the next
   ready family when blocked. Stop for a real dependency, an owned process safely
   handed over, or the execution/resource limit. Do not stop merely because one
   selector invocation finished; do not repeat unchanged tests or requests.

If every current card is externally blocked, check the existing board for a
genuinely ready known issue once and add its bounded action to the priority source.
If none exists, retain the named dependencies and wait quietly for changed evidence.

The sheet includes every priority's next gate, dependency and independent issue
author count. Counts deduplicate known duplicate cases (#209/#210 under #208);
they exclude maintainer/bot authors and are not total affected users. Comment-only
corroboration needs reviewed evidence, and counts across overlapping families must
not be added. Reprioritize on new severity, affected targets, reproduction and
closure feasibility; record the evidence and reason in the JSON. Popularity alone
does not override a concrete blocker. Intake outside the six cards remains visible
as unassigned and must be classified, then linked or given a justified new card.

The loop is allowed to end a cycle with a dependency checkpoint, but that is a
verified wait, not goal completion. A quiet acknowledgement such as “I will
wait for the private handoff” does not reopen the family. A reply containing a
new crash, build, measured result or reproduction does.

## Aggregation and progress accounting

The maintenance script (`scripts/maintenance-loop.py`) is a selector and
repeat guard, not an autonomous code fixer. It must:

- display the family beside every ranked issue;
- record local results at both issue and family level;
- suppress duplicate family contracts only when the command identity also
  matches the recorded result;
- turn a failed local contract into a durable `repair-required` action instead
  of silently re-running or mislabeling the failure as an external wait;
- keep external dependencies in the durable checkpoint; and
- distinguish unanswered evidence from coordination-only acknowledgements.

The scheduled job reports progress in these terms only:

- a failing boundary reproduced;
- a confirmed source defect corrected;
- a candidate built and audited for a named test;
- a physical/reporter acceptance gate passed; or
- a specific external dependency recorded with owner and next action.

Reply count, number of builds, elapsed time and “agent was used” are not
progress measures.

## Model and delegation policy

Scheduled coordination uses the secondary `gpt-5.6-luna` account at medium
reasoning by default; high is reserved for unusually ambiguous issue intake.
Luna owns GitHub replies, family assignment, prioritization, documentation and
loop state.

The active `kartpad-coordinated-maintenance` automation is an hourly heartbeat
attached to the continuing KartPad coordinator task. Each wake resumes that task's
goal, context and ownership; do not replace it with standalone project runs.
The heartbeat inherits the target task's model, so keep that task on
`secondary/gpt-5.6-luna` with medium reasoning. The heartbeat configuration alone
does not prove model routing; verify the actual execution identity at every wake.
Retain an unfinished goal and continue its next executable gate. A dependency
checkpoint is not completion of a goal to fix the affected product path.

At the start of every scheduled run, record the actual model, reasoning level
and account route in the local cycle artifact. If the run is not actually on
secondary Luna at medium/high, stop before GitHub replies, source edits or
tests and record a routing mismatch for manual correction. The prompt is a
routing request, not proof that the runtime honored it.

Use a secondary `gpt-6-astra` agent at medium reasoning only for a bounded hard
source, device, build, computer-use or independent-verification task. Give the
worker one question and one output; review its result locally. Never use a
primary Astra agent for scheduled maintenance. When fresh intake exists, use one
separate secondary Luna Medium intake worker if that model is callable, otherwise
secondary `gpt-5.6-sol` Medium. If neither is callable, the coordinator handles
intake directly. Do not route routine intake to Astra. Intake returns exact
reporter revisions, evidence, duplicate/subcase assignments, priority proposals
and concise reply drafts. Luna reviews and posts authorized replies using shared
receipts, then records their actual URLs. Luna alone edits priority/state records.
At most one intake worker and one engineering worker run alongside the coordinator;
no nested delegation, duplicate investigation or parallel heavy build/device work.

Workers do not publish releases, request credentials, expose private
diagnostics, or clear device data. Preserve unrelated dirty work and use
in-place installs with before/after data checks.

## Release gates

The scheduled loop may build and audit a private candidate but never publishes
an IPA/APK or distribution-feed update. A manual release task is separate and
must include:

- the reviewed source revision and clean intended diff;
- deterministic package/bundle audit, version identity and SHA-256;
- the exact corrected-path runtime test on the target platform;
- data-preserving in-place upgrade evidence;
- physical-device or reporter acceptance where the issue requires it; and
- updated README/release notes that state remaining limits.

Never publish ROMs, saves, generated game assets, private diagnostics, signing
material or credentials. Do not call a build stable when only a simulator,
emulator, host contract or login/dashboard boundary has passed.

## Commands

Normal selection is read/plan/checkpoint only and never runs product tests:

```sh
python3 -B scripts/maintenance-loop.py \
  --max-iterations 1 \
  --state-file build/maintenance/coordinator/loop-state.json
```

Use `--preview` for a read-only selection check. An optional registered contract
requires `--execute-tests --issue NUMBER --hypothesis "Changed evidence and the
decision this test changes"`; the same source/command result remains reusable
even after a new reply. Multiple-issue test sweeps are rejected.

After meaningful progress, update the selected priority's action/checkpoint or
external dependency and the linked board row. Do not append an audit for an
unchanged cycle. After two hourly wake windows at the same gate, finish it or record the
specific dependency; another general audit is not an outcome. A queue of parked
dependencies is a checkpoint, never a declaration that the product is fixed.
Notify the user only for an accepted correction, delivered candidate, failure,
or a concrete decision they must make; otherwise remain quiet.
