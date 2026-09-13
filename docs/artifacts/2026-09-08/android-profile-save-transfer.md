# Android profile save transfer — issue #105

8 September 2026. Source implementation; a playable release and the reporter's
PC WiiCompiled → Android Retro Rewind/PAL acceptance are still pending.

## Change

Manage Saves explicitly selects Original Mario Kart Wii, Retro Rewind, or
Retro Rewind (Separate Save). Targets reuse the identity manager's existing
path map. Exports and restores name the selected profile. The document-picker
target is saved with the activity state; missing/invalid restored state fails
closed instead of defaulting to Original. Import confirmation names the target.

Pending saves have separate fixed filenames; the legacy Original `rksys.dat`
staging path is retained. Restores check exact length, magic and core CRC,
apply before SDL starts, and back up the selected prior save. Identity edits
and pending restores exclude one another. An already staged profile cannot
be silently replaced by a second import. A failed startup restore now prevents
game startup through SDL's existing initialization-error handling instead of
merely logging and continuing with an unapplied restore.

## Validation

- Host Kotlin tests execute the actual storage and identity classes against
  synthetic saves, with a host AtomicFile adapter that injects publication
  failure. All three targets, exact export/staging/application, untouched other
  profiles/Miis, prior-save backups, legacy pending files, invalid profile/size/
  header/CRC, both directions of identity conflict, first import, corrupt staged
  input and multiple pending profiles pass. Interrupted publication retains
  the old target and staged replacement and succeeds after retry.
- The debug-only synthetic fixture passes on an API 36 ARM64 emulator using
  Android's real AtomicFile for all three profiles. It operates inside its
  own cache directory, with no gameplay or online acceptance claim.
- The actual Manage Saves UI and Android DocumentsUI were exercised in a
  read-only emulator session. Importing a synthetic Retro Rewind save with
  “Don't keep activities” enabled returns to a confirmation naming Retro
  Rewind. The pending Retro file matches the selected bytes; no Original or
  Separate Save pending file is created. Exporting the synthetic Retro target
  through DocumentsUI with the same lifecycle setting produces identical bytes
  and a confirmation naming Retro Rewind. The pending restore button is disabled
  for that profile. The lifecycle setting is removed afterward.
- All 140 Python tests, Android release lint, source-pin verification and the
  repository safety audit pass. Debug Android fixture build passes. The existing document-picker runner is
  updated for profile selection and confirmation, but its real-game round trip
  was not run in this pass.

All save inputs above are generated test data. The attached physical phone's
KartPad installation and data were untouched. No APK from the game-free debug
fixture is a playable test build. Apple save UI, automatic synchronization,
preferred-game startup and a renderer correction are separate work.

## Signed playable candidate follow-up

The code 22 public-signed candidate completed a full owned WBFS import and
Original startup on a new disposable API 36 ARM64 Vulkan emulator. Using the
actual save initialized by that fresh emulator game, DocumentsUI restored a
copy to **Retro Rewind**. After Restart Now returned to the chooser, launching
Original applied the pending Retro restore before gameplay. The resulting
Retro save exactly matched the chosen bytes; the Original save remained
byte-identical, and the pending file was removed. This proves the public
candidate's targeting and cold-start application, not the reporter's PC save
compatibility or Retro gameplay. No user phone data was accessed.

The corresponding Android testing release is
[`v0.4.12-android.1`](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.12-android.1).
Its physical and reporter acceptance remain pending.
