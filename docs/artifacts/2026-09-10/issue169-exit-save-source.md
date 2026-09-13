# Issue #169: ordinary-exit save source map

Source-only review on main `0c1b5153`; reporter context remains POCO F6 Pro,
Android 15, public build 21. **No local ordinary-exit loss reproduction or
reporter cause was established. No runtime change is proposed.** PR #173 fixes
pack replacement; it does not establish or fix the reported ordinary-exit case.

## Source boundary

Compared build-21 tag `v0.4.10-android.1` (`c9e62085`) with published code-63
app source `6a2dffc` and current main. Their dependency lock retains Wiicompiled
`1912292c804ff9b1b79938de89369ec4496f9fff`. Read existing prepared Android
source and the corresponding upstream source/patches; no native build, package,
emulator, device session or public action. This establishes source behavior,
not the installed reporter payload or its actual selected pack options.

The Android private-path, NAND-open, Mii-seed and Apple-runtime patches that
supply these storage paths are unchanged between build 21 and code 63. The
relevant NAND/IOS operations below are therefore not a new code-63 exit fix.
The Android selector's explicit process-exit sequence is also present in build 21.

## Persistence and profile routing

Paths below are relative to Android `filesDir/KartPad`, without user data.

| Data | Default destination / routing |
| --- | --- |
| Original license/progress | `NAND/title/00010004/524d4350/data/rksys.dat` |
| Retro license/progress | `RetroRewind/riivolution/save/RetroWFC/RMCP/rksys.dat` |
| Retro Separate Save license/progress | `RetroRewind/riivolution/save/RetroWFC2/RMCP/rksys.dat` |
| Pulsar records/ghosts/ratings | `NAND/shared2/Pulsar/RetroRewind6/`; rating file `RRRating.pul` |

`KartPadActivity.onCreate` exports Context-derived directories before SDL loads;
`wiicompiled-android-private-paths.patch` makes ApplicationDataDirectory use that
root. `include/nand_path.h::DiscoverNandRootPath` uses configured `[paths]
`nand_root` if present, otherwise managed `NAND`. Configuration can therefore
change NAND/Pulsar routing; the Kotlin identity/save-management destinations are
fixed default paths (`KartPadIdentityStorage.paths`). The rating importer
explicitly rejects custom NAND configuration. This distinction is a hypothesis
to check only if configuration actually changed, not evidence that it did.

Native `src/hle/storage/riivolution.cpp` selects the active XML savegame patch;
`nand_fs.cpp::ResolveRiivolutionSaveHostPath` redirects the title's data directory,
not all NAND paths. A clone-enabled redirect copies an original only when the
redirected file is missing. Redirect and NAND-root resolution are cached once
per process. Android's runtime selection (`base` / `retro_rewind`) is distinct
from the pack's Separate Save option and the chosen in-game license slot.
Reopening a different one can show different progress without deleting a file.
No automatic ordinary-resume save-directory deletion was identified.

## Write completion and exit ordering

- `nand_async.cpp` runs the synchronous NAND operation **before** enqueueing its
  guest completion callback. `ios.cpp` likewise performs NAND IOS read/write/close
  before queueing completion. The queue contains callbacks, not deferred host
  write buffers. A generic claim that completed host writes wait until app exit
  to flush is unsupported. A callback can still trigger the guest's *next* save
  step, so stopping a multi-step transaction before its close remains possible.
- `nand_api.cpp::NANDWrite_HLE` calls fwrite then fflush. NAND plain/safe close
  reaches `nand_async.cpp::CommitAndCloseFd`: writable file fflush and fsync,
  fclose, then atomic replacement for a shadow. Failed flush/replace returns an
  error and retains the previous target for shadow-backed handles. Plain NANDOpen
  can fall back to in-place writes; that path cannot restore the previous target
  after a flush failure. An uncommitted `.nandsafe.tmp` is
  discarded when next opened; it is not proof of a completed new save. Do not
  publish unfinished shadows automatically during shutdown.
- `nand_isfs.cpp::NAND_IOS_Write_HLE` writes directly and calls fflush;
  `NAND_IOS_Close_HLE` uses `nand_fs.cpp::CloseFd` / fclose, without the NAND
  shadow commit or explicit fsync. Both write APIs ignore the fflush return,
  and this IOS close ignores fclose's return. These are existing I/O-error
  reporting/durability concerns, not an established ordinary-exit defect or
  evidence of a queued-write loss. No fault-injection test was added in this pass.
- `KartPadActivity.onPause` clears input/stops activity helpers then delegates to
  SDL. It contains no explicit guest-save completion barrier. The app does not
  override onDestroy with one. `restartToGameSelector` launches the chooser and
  schedules `exitProcess(0)` after a fixed delay, without a save acknowledgment.
  This is a concrete possible interruption boundary if the reporter used it;
  it does not demonstrate that a save was in flight.
- Prepared native `src/main.cpp` normal guest-return cleanup shuts down guest
  fibers, flushes window placement, shuts down the adapter/Aurora and transcript.
  There is no explicit NAND transaction drain in that sequence. Activity pause,
  selector restart, guest return and OS termination must not be treated as one
  interchangeable exit path. A flush alone cannot finish unissued guest steps.

## Next distinguishing evidence

The coordinator already requested the necessary reporter clarification; do not
send another request merely because this source pass finished. Consume:

1. **What disappeared:** license/Mii identity, cup records/unlocks, ghosts, or
   rating; whether all old progress or only the latest change vanished.
2. **Exact transition:** Home/background, Recents dismissal, native Restart to
   Selector, or in-game exit; last save/race/menu milestone before it.
3. **Same destination:** Original/Retro, Separate Save state and license slot
   before/after; any pack activation or manually changed NAND configuration.
4. Any already available narrow NAND save-error excerpt for that transition,
   with paths/identities redacted. No raw log or save upload is required here.

A missing license in only one redirect points first to profile/path/activation;
latest progress missing after interruption points to an incomplete guest save;
IOS-only rating/record loss with retained license points to the separate Pulsar
path. A same-profile, completed-save, ordinary-exit failure would justify a
focused owned reproduction. Existing source alone cannot choose among these.
No additional synthetic passing test would establish that reporter sequence.

Independent Medium source review confirmed the callback ordering and exit/close
paths; it corrected the prior-target guarantee to shadow-backed handles only.
