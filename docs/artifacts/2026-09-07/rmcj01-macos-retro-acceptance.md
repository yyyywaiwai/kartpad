# RMCJ01 / Retro Rewind 6.12.7 — macOS execution acceptance (local)

## Scope

This note records hands-on execution of the Japanese `RMCJ01` Retro Rewind
development app on the Apple Silicon macOS host.  It is a local acceptance
record only: it is not a release claim, physical-device result, public Retro
WFC compatibility claim, or full-catalog/full-mode coverage claim.  The source
ISO and `data/` tree were read only; no game input was edited.

- App under test: `private/rmcj01/retro/run/KartPad-Japan.app`
- Bundle: `dev.kartpad.rmcj01.development`
- Window: `Retro Rewind`
- Runtime profile: `retro_rewind` (Japanese `RMCJ01` revision 0)
- Portable user data: `private/rmcj01/retro/run/UserData`
- Retro Rewind data: `private/rmcj01/retro/pack/RetroRewind6`
- Config: `network.enabled = true`; `dvd_root` points to `data`
- State trace environment: `KARTPAD_STATE_TRACE` only; no `KARTPAD_RKG_INPUT_V2`,
  `KARTPAD_RKG_FORCE_FINISH_V2`, or other RKG/force-finish variable was set.

The executable was the already-running incremental-copy/ad-hoc-signed app.  A
separate final package is maintained by the parent task; this report does not
re-sign, commit, or push anything.

## Menu and mode path exercised

Using CUA keyboard controls (`u` = A/confirm, `m` = B/back, `Up`/`Down`/`Left`/
`Right` for menu navigation, `space` for pause), the following path was
visible and completed:

1. Existing `KartPad` license selected (the first attempt intentionally backed
   out of the `NEW` slot; no new license was retained).
2. `Single Player` → `150cc TTs`.
3. Character: `Luigi`.
4. Vehicle: `Sprinter`.
5. Transmission: `Inside`.
6. Drift: `Hybrid`.
7. Retro Rewind course list: `SNES Mario Circuit 1`, then its `Ghosts` page.

The course page visibly reported `150cc Time Trials: 0 trophies / 209`, and
the ghost card showed `SNES Mario Circuit 1`, `01:34.086`, ghost name `ZPL`,
`Rewind`, Mario, and a bike.  The mode menu also exposed `Multiplayer` and
`Retro WFC` (1-player and 2-player entries); those entries were not yet used
in the single-client evidence below.

## Pure native replay result

From the ghost page, `Replay` was selected and the `Start Race` confirmation
was accepted.  The native game rendered the SNES Mario Circuit 1 race and
advanced through the five-lap Retro Rewind ghost playback.  The screen showed
the ghost timer `01:34.086`, lap splits, the chequered-flag finish camera, and
`A ghost has been created for KartPad!` / `NEW RECORD!` before returning through
the replay pause menu.

The runtime trace was captured without diagnostic input injection.  A bounded
copy of the first completed replay session is retained at:

`private/rmcj01/retro/rr-snes-mario-circuit-1-replay-trace.csv`

SHA-256 of that copy:

`d001e97784ae13cde7bc6235d2b559e12654dd82f293e8006c090da515e0aaa1`

The copy contains samples 0–16437 (header plus 16438 data rows).  The trace
state transitions are:

- stage `0` (menu) through sample 225;
- stage `1` (countdown) samples 226–465;
- stage `2` (race) begins at sample 466 with `race_time=240`;
- stage `4` (finish/result camera) begins at sample 6068 with
  `race_time=5880`;
- stage `0` (returned to course menu) begins at sample 16438.

`scripts/summarize-mkw-state-trace.py --require-complete` accepts the long
continuous race span ending at `race_time=5879` and marks `reached_finish=true`.
The early race span has several missing samples while the object graph is
being brought up; those gaps are retained in the evidence rather than filled
or presented as a bit-exact input count.

The live run log contains the matching native markers (`New race started`,
`Scene Exit`), repeated `StaticR.rel verification successful (matched region
2)`, host audio startup (`32000 Hz`, stereo), non-silent PCM, and 60-FPS GX
telemetry.  The observed audio queue reported nine dropped blocks / 3456
bytes during later repeated diagnostics; this is an audible-output check, not
an all-frames/perfect-audio SLA.

## Replay pause/restart/exit

While replaying, `space` opened the native menu:

`Continue Replay` · `Restart Replay` · `Start Race` · `Quit Replay`.

`Continue Replay` resumed the playback.  `Restart Replay` restarted the race
at lap 1.  `Quit Replay` opened `Return to the Courses screen?`; the default
`No` was changed to `Yes` with `Up`, confirmed with `u`, and the visible
`Courses` screen returned.  This validates pause, resume, restart and the
retail callback/return path.  The replay can loop when left running; the
bounded trace above isolates the first completed session.

## Normal race start and pause/restart menu

From the same `Ghosts` page, `Solo Time Trials` was opened and its `Start
Race` dialog accepted.  A normal Luigi/Sprinter race rendered at the starting
grid without RKG fixture variables.  `space` opened the retail game menu:

`Continue Game` · `Restart` · `Change Course` · `Change Character` · `Quit Game`.

`Continue Game` resumed the race and `Restart` returned to the starting grid.
The operator then used `Quit Game` and returned to the Retro Rewind mode menu.
Manual steering was deliberately not treated as completion evidence: the
short attempt left the first corner into sand and was exited without claiming
a natural finish.  No force-finish or race-result memory path was used.

## Save/reload evidence

Retro Rewind's Riivolution redirect is the save path for this run.  The
runtime log states:

`[riivolution] savegame redirect: private/rmcj01/retro/pack/riivolution/save/RetroWFC/RMCJ (clone)`.

The redirected RR save
`private/rmcj01/retro/pack/riivolution/save/RetroWFC/RMCJ/rksys.dat`
is a separate regular file (inode `84470566`, mtime `2026-09-07 02:15:42`),
2,867,200 bytes, header `RKSD0006`, SHA-256
`b2f5cd2ea27d3de36e3a910240522bf81b8a041f765661d9bf2f7d18cb8decff`.  The
matching original-NAND file under
`run/UserData/NAND/title/00010004/524d434a/data/rksys.dat` has a different
inode (`84313595`) and an older mtime (`2026-09-07 01:01:54`), so it is not
used as the RR write target.  Its SHA-256 remains
`e0f66b9f1fec2fc7798eb990719ff15d68f204834cfc2175279ec24ec76bdddd`; the two
files differ at 34 byte offsets and have distinct inodes.  The RR digest
changed from the initial clone before the cold relaunch/online flow; this
report does not attribute that delta to a particular menu action.  A bounded
comparison is retained at
`private/rmcj01/retro/rr-save-readback-comparison.json`.
`banner.bin` matches as expected for the cloned save container.

The replay ghost card (`SNES Mario Circuit 1` / `ZPL` / `01:34.086`) and
`KartPad` license were both visible again after a process-cold relaunch when
the RR redirect was still configured.  The cold-readback snapshot is recorded
in
`private/rmcj01/retro/cold-relaunch-after.json`:
the redirected save SHA-256 was unchanged before/after relaunch
(`b2f5cd2e…`), and the UI again showed the title screen, KartPad license, and
the SNES Mario Circuit 1 ghost card.  This is persistence/readback evidence
for the cloned RR save and selected license/ghost display; it is not a claim
that the replay overlay itself wrote a new record.

A second, trace-enabled cold relaunch was then used for the final online
readback.  The app process was started at `2026-09-07 02:25:29 JST` as PID
`81599` (the only process running the packaged `KartPad` executable).  The
bounded evidence is recorded in
`private/rmcj01/retro/cold2-readback.json`; the
corresponding run log is
`private/rmcj01/retro/native-jlink-cold2-run.log`
and the trace path is
`private/rmcj01/retro/native-jlink-cold2-trace.csv`.
The trace contains only its header because no race was started during this
cold online pass.  The UI readback sequence was `Press the A Button` →
`KartPad` license → `Retro WFC (1P)` lobby → `Friends` → `Create a Room` →
`Retro Rewind — Waiting for friends...`; the consent pages were not shown
again.  The process, paths, current RR/original hashes, and private identity
artifact digest are kept in the JSON snapshot (raw friend code is omitted).

At approximately `2026-09-07 03:10 JST`, a later process change was observed
without an intentional Mac restart by this operator or the parent task.  PID
`81599` was no longer present and PID `23126` (PPID `1`) was the only process
running the same executable.  The cause (CUA app-manager relaunch, external
operation, or prior-process exit) is not determined and is not attributed to
the parent.  During the transition the UI briefly showed a black loading frame
and then the title screen.  The trace/log files at the shared cold2 paths had
also been extended by that later run; before further UI input they were
preserved as the unattributed snapshots
`private/rmcj01/retro/native-jlink-03-10-unattributed-trace.csv`
(5,616 data rows; stages `0/1/2/4`; final `stage=4`, `race_time=4422`,
SHA-256 `2c45296c9414adcabfb123b417b935f5354c309b91b7aa4ed963ce65610a1855`)
and
`private/rmcj01/retro/native-jlink-03-10-unattributed-run.log`
(SHA-256 `2f4f259226a46987cf5fdb7cef4afc6d29fe325b85ceed2e56bb08a7422f72ba`).
Those rows are provenance-separated and are not used as evidence for the
earlier cold2 replay or assigned to a particular operator.  The sole PID
`23126` was then navigated back through the normal login path and left at the
same private-room waiting screen; the consent pages were not re-prompted.

## Boundaries / next checks

- Only one RR course (`SNES Mario Circuit 1`) and one 150cc ghost were run.
  The 209-course list, other cups, Grand Prix/VS/Battle, 200cc, and broader
  RR catalog remain unverified here.
- A normal race was started and its pause/restart/quit menus were exercised,
  but this operator did not complete a naturally steered race; the pure replay
  result above must not be relabeled as a human race.
- No public ranking submission, credential disclosure, or physical iPhone/iPad
  claim is made.  Retro WFC lobby reachability and a private-room waiting state
  were observed on this single Mac client; matchmaking, room pairing, race,
  and reconnect remain unverified.  If a new Terms/legal-consent or payment
  dialog appears in a later path, stop and report it before accepting.

## Retro WFC consent boundary and lobby result

From the Retro Rewind mode menu, `Retro WFC` → `1 Player` was opened.  Before
any login or network action, the native UI presented a disclosure page titled
`Retro WFC (1P)` with a `Next` button.  Its text states that playing via Retro
WFC automatically sends the player's **Mii and nickname** and **records and
ghost data** to Retro WFC, and that this data may also be shared with other
players on Retro WFC.  The user approved that exact sharing scope; `Next` was
then accepted, followed by the privacy reminder and the explicit
`Will you allow game data to be sent to Retro WFC?` choice (`Permit`, changed
from the default `Prohibit`).  No additional contract or payment prompt
appeared.

The app reached the native `Retro WFC (1P)` lobby, where `VS Worldwide`,
`Other Worldwide`, `Battle Worldwide`, `Friends`, and `VR Leaderboard` were
visible.  The lobby showed `Rank: 0`, `Score: 0`, `380 Players`, and a
message-of-the-day status of `Server Status: ONLINE`.  Native logs recorded
the expected Retro WFC hostname rewrites to `*.play.rwfc.net`, server-date
responses, and QR2 single-player kick orders.  Raw PIDs are kept out of this
report and were redacted in
`private/rmcj01/retro/native-jlink-rwfc-sanitized.log`.
This establishes single-client lobby reachability.  A private-room waiting
state was also exercised below; matchmaking, room pairing, race and reconnect
remain unverified.

The lobby's `Friends` page was also opened.  It visibly exposed
`Create a Room`, `Find a Friend`, and `Register a Friend`, plus the test Mii
`KartPad` and its friend code.  The raw code is stored only in the private
artifact `private/rmcj01/retro/mac-rwfc-identity.json`
(not in this report or in parent messages); its SHA-256 is
`2f36adb10744c3ddeed6a6d2fba06210a765c90dfce43382435b80d66945afad`.
After a cold relaunch/re-login (the consent pages were not shown again),
`Friends` → `Create a Room` was activated.  The native screen now reads
`Retro Rewind — Waiting for friends...` with `Message` and `Back` controls.
The Mac client is left in that private-room waiting state for the iPad peer;
no public `VS Worldwide` queue was entered.  The current waiting-state process
is the single PID `23126`; the preceding PID `81599` and the process-change
provenance are captured separately above.
