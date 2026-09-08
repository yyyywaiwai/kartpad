# iPad layout and navigation iteration — 0.4.10 build 24

Build 24 was installed as a private physical-acceptance candidate without an
IPA. The maintainer subsequently exercised menu navigation, switching after
reopening, and Retro Rewind license deletion and creation on iPad, and requested
the [build 25 clarity update](ipad-identity-build25.md) and a new IPA. The latest
published GitHub release remains 0.4.9.

The iPad defaults now match the maintainer's edited physical iPad layout captured
on 2026-09-07, including per-button sizes. Fresh iPad defaults and Reset This
Device Layout use these values. Existing custom layouts and iPhone defaults are
preserved.

The three-dot menu gains **Return to KartPad Menu**. At the guest event-pump
boundary, KartPad suspends guest execution, pauses its audio output, clears touch
holds, and displays the native game chooser. Selecting the active game resumes
that same in-memory session. Selecting the other game can save a next-launch
choice; the dialog explicitly requires closing and reopening KartPad. Both
Original and Retro Rewind next-launch choices are consumed once. This does not
reset/reinitialize the emulator in process. An online connection may time out
while guest execution is suspended.

Original Mario Kart Wii no longer offers Private Friend Rooms instructions. Its
Multiplayer dialog explicitly says that Nintendo WFC is closed and private
online rooms are unavailable in this build. Retro Rewind retains its in-game
Retro WFC friend-room guidance. The server editor and saved-setting confirmation
explain that this is an experimental override for an already-running compatible
server; another iPad's IP address or shared Wi-Fi does not create that service.

MeleePad's native lobby is coupled to ModernGekko/Dolphin NetPlay, including
compatibility fingerprints, synchronized controller input, boot/session state,
traversal and game start/stop. KartPad's WiiCompiled WFC path does not provide
those runtime interfaces. Copying that lobby UI does not provide a working race
transport. Full private-room implementation and safe in-process game switching
remain separate work, deferred by the maintainer in favor of this iteration.

Validation before device installation:

- 68 Python tests and 17 native tests passed; the prepared-runtime controller
  probe regression still passes.
- Fresh runtime preparation reproduces the patched build source.
- Full physical iOS/iPadOS build and app audit passed.
- A fresh iPad Simulator's saved default origins and size scales exactly match
  the captured physical iPad layout.
- Live Original game → three-dot menu → KartPad chooser → Resume succeeded in
  two cycles, including background/foreground while paused. Frame counters were
  unchanged while the chooser was open. The game remained live after resuming.
- Other-profile selection shows next-launch guidance; cancellation returns to
  the chooser. Original Multiplayer has no friend-room instruction action.

Android remains paused. Its existing top-level **Switch Game Version…** path
already restarts to its separate launcher process. When Android work resumes,
rename that entry to **Return to KartPad Menu** for consistent wording and retain
its existing process restart mechanism; do not copy the iOS suspended-guest loop.
No Android source, APK, or device state was changed in this iteration.

Physical touch placement, audio after resume, both game profiles, controller
reconnection, and repeated navigation remain the maintainer's acceptance checks.
