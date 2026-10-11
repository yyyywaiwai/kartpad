# Feature follow-up from the overnight plan

## Retro Rewind ghost transfer (#295)

The reporter already confirmed Original export. Current Android UI intentionally
selects Original licences, reads the Original `rksys.dat` bitfields, and transfers
one of32 native course slots. Its pending import rebases onto the latest Original
save and keeps a backup. Changing only a profile/path would not implement Retro.

The retained rr-pulsar research checkout at
`93ba8c8a486bd771c97ffc8b68fd504f47f742b5` shows why:
`PulsarEngine/Ghost/GhostManager.cpp` enumerates separate RKG files under a track
folder and time-trial mode; `SlotExpansion/CupsConfig.cpp::GetTrackGhostFolder`
uses different regular/custom course keys and variant subfolders;
`PulsarSystem.cpp` defines150/200/150F/200F mode directories. Saving also updates
leaderboard and trophy metadata. This research checkout is architectural evidence,
not proof of the exact installed6.12.8 filesystem contract.

Next implementation should first map the shipped profile's regular/custom track,
variant and mode identity, then add read-only export with validated RKG files and
unambiguous labels. Import additionally needs safe collision policy, restart
application, backup and preservation checks for leaderboard/favourite state.
Do not reinterpret Retro data as Original32-slot save offsets or request another
Original export test. Settings documentation now explicitly includes original Wii
courses played inside Retro in the unsupported scope. No Retro support claimed.

## Android shake-to-trick

`KartPadMotionSteering.kt` currently consumes TYPE_GRAVITY (or raw accelerometer
fallback) for calibrated tilt. It publishes only a steering axis and yields to a
physical controller. iOS's `apple/mobile/KartPadMotionSteering.mm` instead detects
shake from CoreMotion gravity-removed acceleration in g, with0.35g rearm,
1.35g trigger and0.45-second cooldown, then consumes a one-shot action.

A direct copy of those thresholds onto Android's existing gravity stream would
be incorrect. A useful implementation needs a gravity-removed acceleration
source or tested fallback, unit/time conversion, one-shot consumption and clearing
on pause, sensor disable and physical-controller takeover. It also needs an
independent disabled-by-default preference and physical false-trigger/trick checks.
The existing tilt tests do not establish those behaviours. No shake feature was
silently enabled or claimed from simulated samples during this loop.

Both follow-ups remain concrete feature work. The overnight Android candidate's
measured runtime reductions and RVZ import are independent of these features.
