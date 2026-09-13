# PR #112 current-main source integration — 10 September 2026

Local acceptance integration only; no public merge, package, full native build,
device operation or acceptance claim.

## Exact source and delta

- Main parent: `c14408e` (full parent identity is retained in the merge).
- Contributor parent: `a33226479b0b31c202938e972f7f0d17f30a2126`, unchanged.
- Integrated source merge: `0194d5cad9e1402ac026fa71b93f09f53b62c29a`.
- Branch: `codex/pr112-current-integration` in the isolated
  `kartpad-pr112-current-integration` worktree.
- Zero conflicts and zero manual source resolutions. Relative to main: 29 files,
  2,284 insertions and 229 deletions. Contributor ancestry/attribution is retained.
- Automatic merges affected README, INSTALL_MACOS, audit-macos-package and
  package-macos-runtime. Later main's 0.4.15/build 34 package/audit/fingerprint
  values survive; contributor product selection and native-settings checks survive.
- Native Mac shell/includes, Mac input patches and Mac preparation script are
  byte-identical to the contributor head. Later main's dual-target patch differs
  only in iOS version/build constants. Android storage/report changes and iOS
  overlay work survive unchanged. No older runtime/app is relabelled as this merge.

## Focused integrated validation

Source preparation used the actual integrated preparation script's prefix through
all patches (stopping before sse2neon/download/configuration/build), immutable
local pinned upstream references and fresh ignored output. All patches applied
without fuzz, offsets or failures. This is source-stack validation, not a build.

Passed against that fresh source:

- `scripts/test-macos-controller-profiles.sh`: actual native class, virtual SDL
  input, profile round trip, legacy/shared bindings, dead zones, clear,
  corrupt-profile preservation, Xbox labels; keyboard cancel/Escape/close/reopen,
  deactivation, alternate character layouts, special/ISO keys, repeats and invalid
  keys. Temporary profile data only. Four toml11 deprecation warnings and one
  existing harness `windowWillClose:nil` nonnull warning remain.
- `scripts/test-macos-controller-assignment.py`: assignment, displaced controller,
  cached-index fallback, unassignment and player 4.
- `scripts/test-macos-settings-runtime.py`: live graphics/audio bridge, coalescing,
  fullscreen failure fallback, resolution limit and redundant F10 UI removal.
- `scripts/test-macos-trigger-output.py`: all 200 final PADStatus cases.
- `tests/macos/settings_shortcut.cpp`: compiled with the pinned SDL include path
  and ran successfully. Initial invocation omitted that include and was corrected.
- Actual `KartPadMacShell.mm` compiled for all three existing product definitions,
  using retained dependency libraries and fresh integrated source/header paths;
  outputs stay in the isolated worktree. No full link was run.
- Diff whitespace validation passed.

The eight `test_macos*py` contracts give **7 pass / 1 fail** on both this integration
and untouched main `c14408e`. `test_public_macos_release_contract_is_versioned`
expects `v0.4.11-macos.1`, while current packaging is `v0.4.15-macos.1`.
This is reproduced pre-existing contract drift, not an integration regression;
it was not changed in this bounded assignment. Focused checks found no new
integration regression. They do not establish physical input or gameplay behavior.

Private local logs are in this worktree's ignored `build/`: source-preparation.log,
native-profiles.log and shell-compile.log. Generated source and object files are
not committed. The Sep 9 [keyboard record](../2026-09-09/macos-keyboard-capture-correction.md)
explains the already-reviewed corrections; this pass does not repeat that review.

## Next attributable candidate dependency

Independent Medium review found no source integration blocker: automatic remerge
is identical, Mac input source matches the reviewed contributor, and later Android/iOS
changes are retained. Assign a single owned native build slot for the next step. Use the exact reviewed source commit, fresh output
paths and pinned locally owned Original/Retro translation inputs. The retained
old `271fdc1` app is stale and cannot close this acceptance gate. No physical
candidate for `0194d5c` exists yet.

From this isolated worktree, the next full-runtime command (NOT run here) is:

```sh
scripts/prepare-g7-game-runtime.sh   /absolute/path/to/owned/retro-translation   build/pr112-candidate-source build/pr112-candidate-runtime dual
```

Dependencies: local `ref` points to pinned upstream references; the ignored
`build/dependency-cache` points to the retained pinned cache. The existing
source-only fixture `build/integrated-runtime-source` is deliberately not reused
as candidate output. The preparation command includes CMake and a full build;
check host ownership/processes before executing it. Then a separately assigned
local package/audit step must capture source commit, unsigned executable SHA-256,
bundle hash, version/build, strict signature check and an isolated owner test copy.
An evidence-only descendant must be recorded as such if it becomes the packaging
HEAD. Preserve owner's data and distinguish this candidate from released build 34.

## Christopher's physical acceptance card

Record exact candidate commit/hash, Mac/OS, controller model/connection and actual
keyboard layout; report pass, failure or unavailable for each row.

| Test | Required observation |
| --- | --- |
| Original, cold launch with controller connected | Expected player assignment; menu navigation and one race with steer, accelerate, item and drift. |
| Retro Rewind, cold launch and race | Same actions in a real Retro race; profile restored on relaunch. |
| Trigger remapping | Explicit drift binding isolates the unassigned analogue trigger; intended button/trigger works without unintended drift. |
| Disconnect/reconnect | Disconnect and reconnect during menus and a race; same intended assignment restored, no stuck input; repeat with a second controller if available. |
| Native settings/layout | Cmd-comma and F10; every tab; right-hand Clear controls reachable at default and reduced window height; windowed/fullscreen return, notch/exclusive where available. |
| Real keyboard layout | Switch actual OS keyboard layout; capture physical position including ISO/special keys; confirm runtime polling matches. Cancel/Escape/tab change/focus loss must leave later keys unbound. |
| Persistence | Close/reopen app and verify controller/keyboard profile and settings retained, with Original and Retro data intact. |

No save clear, identity reset or overwrite of the installed public app is required.
No acceptance row is marked passed by the source harness. Rendering report #127
and PR #157 remain separate. Public merge/release remains coordinator-owned.
