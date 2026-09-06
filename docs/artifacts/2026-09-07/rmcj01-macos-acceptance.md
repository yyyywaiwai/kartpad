# RMCJ01 revision 0 — local macOS acceptance

## Scope and environment

This is acceptance of the **Japanese original-game ARM64 macOS development
product**, not a release of the PAL/Retro Rewind dual product, a Japanese IPA,
or a physical iPhone/iPad/Apple TV result. The original ISO/DATA are private.

- Apple M5 Pro, 24 GB RAM; native Metal, not Dolphin or a simulator.
- Xcode 26.6 (17F113), .NET SDK 8.0.424, CMake/Ninja.
- WiiCompiled source: `1912292c804ff9b1b79938de89369ec4496f9fff`.
- Pulsar address-map source: `93ba8c8a486bd771c97ffc8b68fd504f47f742b5`.
- Pinned macOS Dawn archive SHA-256:
  `084ffd2ef500d614e443e3d494738272134628867bad3270d67ee8b0fb5f0838`.
- Final app: `private/rmcj01/verified/run/KartPad-Japan.app`.
- Final executable SHA-256:
  `a4d2b77fbf14e387c9883a9b3786f3932e979c59e0a4f9f386783986a555b6e2`.

## Build and package

The fresh-tag `build-rmcj01-macos.sh` invocation translated, compiled, linked,
packaged, ad-hoc signed and verified the app. It emitted 29,655 functions with
**zero unsupported instructions and zero invalid SSA functions**. The native
shared graph contains 29,083 functions in 72 shards. The Japanese app passed
the region-aware macOS package audit, including architecture, dependency
closure, data separation, native host contracts and signature checks.

All 14 sections of the final executable's `__TEXT` segment, including `__text`,
constants, strings, exception tables and unwind information, are byte-identical
to the development executable used for the two complete time trials. Whole
file/segment hashes differ because packaging changes Mach-O headers/signatures.
The final app was also launched independently, without RKG fixture variables.

## Runtime evidence

| Check | Observed result |
| --- | --- |
| First boot | Japanese intro/title, default first-run NAND/VFF initialization |
| Menus | License, main, single-player, character, vehicle, drift, cup, course and ghost screens |
| License persistence | `KartPad` license created normally and displayed after process restart |
| Race | Luigi Circuit, Luigi/Sprinter, automatic drift, all three laps and normal finish |
| Results | Retail post-race menu, including restart, course/character change, replay and quit choices |
| Restart | “もういちど” created a new race; second normal finish reached |
| Save | Valid `RKSD0006` save, matching CRC; real stored RKG at `0x28000` |
| Record reload | Final app displayed `01:56.585` and `KartPad` ghost after restart |
| Host sound | App-scoped ScreenCaptureKit capture, 814,080 samples over 8 s, peak −2.75 dBFS, RMS −17.12 dBFS |
| Final native replay | Staff ghost completed via the retail controller path at the exact expected input-frame boundary; no diagnostic input overrides |
| Replay exit | Confirmed Yes callback, next section `0x4a`, MenuScene `1`, and visible return to course selection |

Two completed race-state spans were recorded: `race_time=240..7228` (6,989
samples) and `240..17533` (17,294 samples), each followed by finish stage 4.
These are **RKG-assisted then keyboard-finished local time trials**, not claims
of two unattended, bit-exact staff-ghost finishes. No force-finish variable was
set and no race-result memory or save bytes were patched. The long second run
includes stationary time while audio/package diagnostics were performed.

Separately, the final package's unmodified retail staff replay completed the
consecutive span **`race_time=240..5614` (5,375 race samples), followed by stage
4**, matching all **5,615 input frames** including countdown. This passes
`summarize-mkw-state-trace.py --require-complete --expected-input-frames 5615`.
The retail replay subsequently looped; its normal pause and exit menus were
also exercised. This separates the external fixture timing limitation from
the game's own Japanese ghost playback and race-completion implementation.
An initially ambiguous exit attempt was followed through the retail callback
and scene-manager request rather than inferred from an animation. The final
screen is the course-selection menu. Diagnostic debugger sessions were detached.

The stored record is `1:56.585`, course 8, vehicle 16, character 7. Save CRC
`3359402095` matches the independently computed CRC. The save SHA-256 after
the two races is
`e0f66b9f1fec2fc7798eb990719ff15d68f204834cfc2175279ec24ec76bdddd`.

The app commonly sustained 60 presentations/s in these observations, but
cold pipelines, compilation, UI operations and debugger attachment caused
transient stalls. The final session initially recorded three dropped audio
blocks (1,152 bytes), with zero empty-before-push checks. This is audible-output
and functional acceptance, **not an all-frames/perfect-audio performance SLA**.

## Problems found and handled

1. Native `.inc` registrations require the same address port as `.cpp` and
   headers. Missing them initially caused compilation failure; they are now
   included in the preparation pass.
2. Shards materialize function bodies. Injecting afterward silently leaves
   old code in the build; the reproducible script injects all six hooks first.
3. The opt-in RKG test path initially advanced for all four Wii controllers.
   The diagnostic-only correction restricts it to channel 0, permits disarming,
   and restores normal handling outside countdown/race stages. External input
   playback still diverged before the last corner; keyboard input completed
   both races normally. This is not represented as bit-exact replay evidence.
4. `network.enabled=false` also disables inherited local WiiConnect24 IOS
   services needed by fresh-save VFF creation. The acceptance uses the existing
   default `true`. No online-service login, matchmaking or ranking submission
   was performed. Disabling this setting on fresh NAND is a known limitation.
5. The installed audio probe returned “silent” because its PCM buffer had zero
   `frameLength` at copy time, producing CoreMedia `-12731`. The scoped probe
   sets frame length **before** copying, counts actual samples and fails a
   zero-sample capture. It stores only metrics, not audio or screen pixels.

## Reproduction and private evidence

```sh
KARTPAD_RMCJ_BUILD_TAG=fresh-name ./scripts/build-rmcj01-macos.sh "$PWD/data"
KARTPAD_MACOS_AUDIT_REGION=J ./scripts/audit-macos-package.sh \
  "$PWD/private/rmcj01/fresh-name/run/KartPad-Japan.app"
PYTHONPATH=builder python3 -m unittest discover -s tests -v

swiftc -parse-as-library scripts/probe-macos-game-audio.swift -o /tmp/kartpad-audio-probe
/tmp/kartpad-audio-probe PID
```

The full builder test discovery passed **91 tests, one skipped** (the cached
production RWFC payload was absent). Shell syntax checks and `git diff --check`
passed. Final input hashing reconfirmed the exact ISO, DOL and REL identities
listed in [the region documentation](../../RMCJ01.md). The original game input
was not modified; saves and caches stayed in isolated portable directories.

Private evidence under `private/rmcj01/`:

- `verified-build.log`, `verified/build.log`, `translation-quality.json`;
- `verified-package-audit.log`, `runtime-code-comparison.json`;
- `race-primary-run.log`, `race-primary-trace.csv`, `race-primary-summary.json`;
- `save-before-restart.json`, `save-after-two-races.json`;
- `final-native-run.log`, `final-native-trace.csv`, `final-host-audio.json`;
- `final-native-summary.json` (strict expected-input-frame check);
- `final-host-audio-current.json` (second app-scoped probe, 798,720 samples,
  peak −0.33 dBFS, no capture errors), `menu-callbacks.jsonl`;
- `final-input-sha256.txt`, `tests-final.log`, `final-preflight.log`.

No commit, push, public upload, device installation, or game-asset distribution
was part of this acceptance. Full course/mode coverage, multiplayer, online
play, Japanese Retro Rewind and physical Apple device support remain separate.
