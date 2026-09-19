# Full-race profiling follow-up

No valid slow full-race profile or gameplay speedup has been established in this
iteration. The previous capped time-trial ghost captures remain excluded from
performance acceptance. Source changes below are private test instrumentation,
not a proposed performance release.

## What changed

Remote touch steering could not keep the player with the opponents. A debug-only
Android marker, `KartPad/Diagnostics/FullRaceCpu.enable`, enables a native offline
VS test hook. For a verified one-human/eleven-CPU lineup, it converts the first
menu-scenario slot to the game's CPU type. The intended workload retains twelve
racers and the normal race simulation. Whether the actual camera, items and
full course remain representative must still be verified on hardware.

The lookup uses the PAL RaceConfig singleton at `0x809bd728`, menu settings at
5976 (course) and 5984 (mode), and twelve 0xf0-byte player records with type at
`0xc28 + i * 0xf0`. The source reference is
[doldecomp/mkw](https://github.com/doldecomp/mkw/tree/94585b8a8fd7a2a52f30640ccff316e57880b6c1),
`config/RMCP01/module/symbols.txt` and `src/system/RaceConfig.hpp`.
The earlier diagnostic's `0x809bd70c` points to KPadDirector, not RaceConfig.
The first iterations inherited that wrong pointer; their guard did not activate.
They are not valid CPU-driven benchmarks. Existing RKG diagnostic pointer uses
are a separate audit item, outside this performance test.

The hook is reached from both KPADRead and KPADGetUnifiedWpadStatus. Release
Kotlin cannot enable the marker. Host tests of the extracted actual helper pass:
disabled mode makes no writes; enabled mode converts only offline VS; other
modes, incomplete lineups and absent memory make no writes. These tests establish
guard behavior, not physical race correctness.

## Device and artifacts

Private code111, `0.4.23-full-race-profile`, was installed in place. SHA-256:
`87095788968fd6a359d2d445bf246a31aa021185553111a4336855c6a2902fc2`.
Package audit passed. All 26 allocated native ELF sections match retained
unstripped symbols. The build uses the CPU-context/resolution candidate plus
the explicitly dirty diagnostic patch; it is not the unchanged public build.
Private patches, APKs, exact symbols and captures are under
`build/android-full-race/`. NAND and preferences were archived before code108;
no uninstall, data clear, asset replacement or release occurred.

Original Sherbet Land 100cc VS with twelve racers was entered at the owner's 2x
setting, but remote steering failed to traverse the course. Do not treat its
start-grid/respawn observations as a representative performance benchmark.
The first profiler attempt rejected kernel sampling; the monitor now requests
`cpu-clock:u` at 99 Hz for 20 seconds. No successful profile has yet been accepted.

Local macOS Vision OCR was added to the ignored navigation helper. Its first
state classifier confused Main Menu's descriptive Grand Prix text with the
Single Player mode menu and reached WFC setup. The classifier now prioritizes
Main Menu, refuses network prompts and stops on unrecognized screens. That
corrected navigation path remains unverified on the phone.

ADB disconnected during setup and a fresh device listing was empty. At that
boundary code111 and the debug marker remained installed. The marker must be
removed and the app restarted before returning the phone to ordinary gameplay;
it could not be removed after disconnection. No successful full-race CPU-driver
activation is claimed. The user has been asked to reconnect; the investigation
goal remains active.

## Next executable gate

On reconnect, verify device/package identity, navigate with screen readback to
Original offline VS, and confirm twelve CPU slots actually move through Sherbet
Land with ordinary item activity. Stop on any missing racers, stationary camera,
network menu or changed simulation mode. Capture a genuinely slow segment with
matching exact symbols, then classify guest CPU, GX CPU and rendering waits.
Do not build another optimization or perform another capped ghost comparison
before obtaining that workload evidence. Remove the temporary marker and
restart before normal owner play.
