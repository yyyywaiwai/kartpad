# Maintenance readiness correction — 13 September 2026

The maintenance audit found correct execution routing but a queue with no selectable
engineering work. This correction adds bounded local actions; it does not change
scheduling, build an application, deliver a diagnostic or accept a reported bug.

## Observed process state

The local `kartpad-coordinated-maintenance` heartbeat was paused and its existing
target task, **Update Kartpad bots and releases**, was idle. The last five recorded
turn contexts used `secondary/gpt-5.6-luna` with medium reasoning. The shared action
ledger contained 29 completed receipts, no pending actions and no current owner.
There was no evidence of a stuck receipt lock or incorrect coordinator model.

The heartbeat's configured checkout had an untracked, older priorities file that
still described resolved signing/preparation gates. Reviewed main `1fe6364` already
recorded the published corrected iOS candidate and available Android signing
capability. Before another wake, reconcile the checkout with reviewed main while
preserving local records and other owners' work. Do not overwrite the dirty tree
or treat a prompt's desired model as execution proof. Resuming the paused heartbeat
is a separate owner decision, not an effect of this documentation change.

`scripts/maintenance-loop.py::select_work` only selects `ready-local` cards. All six
existing cards were awaiting an external actor, even where their next action still
included locally executable preparation. The stall counter tracks selected work;
it cannot repair these readiness classifications. The new preparation cards and
their waiting acceptance cards describe phases of the same reports, not additional
affected users. Do not sum their counts.

## Bounded next actions

- **#248 continuation handling:** retain the existing release-task investigator;
  reconcile its ownership and result before assigning any engineer. The inspected
  code80 graph lacks the reported `0x807EF16C` resume point, but that actual hook
  returns normally, so the exact reported KartPad abort is unproven. A separate
  skip-return control-flow defect was identified: hook `0x8180C6E4` changes LR from
  `0x807A1A58` by 20 bytes when a callback is absent, while the caller continues
  toward the callback at `0x807A1A68`. Review the narrow upstream PR182 backport,
  old-fail/new-pass regression, generated coverage and code growth. Compilation and
  actual item-change/Item Rain acceptance remain subsequent gates. Source report:
  [#248](https://github.com/chrissotraidis/kartpad/issues/248).
- **#197 menu input:** the reporter supplied in-game track/online-room menus and
  both touch and ipega Xbox-mode input after controller use. Inspect shared held
  input and detach/handoff state, with a discriminator against mapping alone.
  Default-mode A/B behavior and auto-acceleration remain separate. Reuse the
  [answered details and outstanding offline touch-only comparison](https://github.com/chrissotraidis/kartpad/issues/197#issuecomment-5649623350);
  do not request the same facts again or call #184 a fix for this issue.
- **Adreno and warmed performance:** inspect retained source, APK and symbols before
  assuming validity; prepare the compatible signing/build/audit recipe and test
  card locally. The available public signer does not prove an old diagnostic is
  correct. Private transfer and the affected-device experiment/capture remain
  explicitly waiting gates. Respect host build/device ownership and do not publish
  diagnostics or manipulate live app data.

Android code80 release materials were prepared during this review. This note does
not assert publication; verify the actual release separately. Earlier physical
code78/code79 observations do not accept Adreno geometry, sustained performance,
#197 handoff behavior or #248 continuation behavior.
