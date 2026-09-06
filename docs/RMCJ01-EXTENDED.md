# RMCJ01 extended acceptance — user-accepted scope

This ledger extends `RMCJ01.md`. The latest user acceptance below supersedes
the earlier open testing gates; historical observations are not rewritten as passes.
Apple TV physical-device acceptance was explicitly excluded by the user on
7 September 2026. The user subsequently deferred iPhone acceptance as well;
the active device scope is **iPad and macOS only**. The installed iPhone test
app/data are retained without further testing. No original ISO/DATA file is
modified by these workflows.

## Latest user scope update (2026-09-07)

The user explicitly said that course verification is not needed. Per-course
coverage and filling the 386-row/465-archive runtime matrix are therefore no
longer acceptance requirements. Existing static/replay evidence is retained as
historical evidence, not converted into passes. The additional Donut Plains 1
attempt was stopped at variant selection before any race started (the current
Mac trace still contains only its header).

The user subsequently reported that validation was complete on their side and
requested a source fork, commit, and push. Additional device testing is stopped.
The final requested regions are **RMCP01 (PAL/Europe) and RMCJ01 (Japan)**;
"America" was explicitly corrected to RMCP01, so RMCE01 is not added.
The iPad/macOS scope is accepted on the user's report, not a claim that the
assistant independently completed every previously open online/gameplay test.
iPhone, Apple TV, and course-by-course testing remain excluded.

The existing PAL product and the separate Japanese development build paths
are retained. The generic Personal IPA Builder remains PAL-only: changing its
capability flag would not implement the Japanese runtime preparation path.
All sections below are historical checkpoints, including any "open" or
"in progress" statements. They preserve observed limitations and are not
instructions to resume testing.

Latest installed iPad diagnostic candidate: `mobile/signed-udp-trace/KartPad-Japan.ipa`.
Latest running Mac diagnostic candidate: `retro/wfc-trace-candidate/KartPad-Japan.app`.
See the timestamped continuation sections below for hashes and evidence.

## Earlier candidate checkpoints

- Japanese Original + Retro Rewind 6.12.7 dual graph: 29,655 translated base
  functions, 27,691 shared base functions, and 4,189 mod functions. The mod
  selects the actual J chunk in the pinned combined `Code.pul`.
- Official Japanese `RMCJD00` payload: 28,992 bytes, SHA-256
  `5a97dbe12aa9c41ce529d32830740d1eabb970474a3125be4bab5f4600ae29e7`.
  Payload magic, game identity, size, hash, production RSA signature, patch records, and the static
  consumer descriptor are validated; the PAL payload is not relabeled.
- Exact assets and XML still use the PAL profile's shared 6.12.7 release pins.
  The official version feed reported 6.12.7 during this run.
- Native iOS 16.0+ arm64 app builds and passes the Japanese package audit.
  Dedicated app identifier: `dev.kartpad.rmcj01.ios`. This does not replace the
  existing `dev.kartpad.app` installation or share its container.
- Signed corrected candidate (private, not a public release):
  `private/rmcj01/mobile/signed-jlink/KartPad-Japan.ipa`, SHA-256
  `942767ff492caa8b8d08793a6433669f1104de11b01c9cfea0a014ea9d62013d`.
  Its development provisioning profile covers the selected iPad and iPhone 15.
  The IPA contains no ROM/DATA, saves, or private signing key.
- A fresh `ios-repro` build completed through `build-rmcj01-ios.sh` without
  manual staging edits. Its entire unsigned executable is byte-identical to
  the corrected `ios-dual` build: SHA-256
  `4959b168dd198346d916cbb8342c221a75409f990e4192b33617a36ccdba21ab`.
  The comparison is recorded in `mobile/ios-repro-comparison.json`.
- The independently repackaged corrected macOS app is under
  `private/rmcj01/retro/verified-package/KartPad-Japan.app`. Its 14 `__TEXT`
  sections match the running corrected app exactly; the package audit passes.

## Runtime findings

1. The first RR candidate reproducibly stopped with `Error 429`. It still
   used PAL's module compatibility link base `0x803992E0`.
2. At Japanese guest address `0x806013D4`, the compatibility view held branch
   `0x4BD98030` (target `0x80399404`). The J module accepts `0x4BD979B0`
   (target `0x80398D84`): exactly the same module offset `0x124` relative to
   Japan's link base `0x80398C60`.
3. The manifest now derives and checks `0x80398C60` from the pinned address
   map. The actual translated module remains at `0x81800000`. No compatibility
   check was disabled. Regeneration changed three mod output files and the
   incremental native build passed.
4. The corrected macOS candidate reaches the Retro Rewind title and license
   screens, initializes the Japanese WFC payload, renders, and produces
   non-silent audio. Its native ZPL staff replay on SNES Mario Circuit 1
   completes five laps and reaches stage 4 without RKG injection or forced
   finish. Replay pause/resume/restart/quit and normal Time Trial
   start/pause/resume/restart/quit pass. A manually steered finish, cold save
   readback, other RR courses and online remain separate gates; see
   `artifacts/2026-09-07/rmcj01-macos-retro-acceptance.md`.
5. iPad Air M2 (iPadOS 27 beta): the separate app was installed; its first-run
   UI identifies RMCJ01, imports the supplied extracted folder via the actual
   in-app importer, and starts Original Mario Kart Wii with the touch overlay.
   The corrected signed candidate subsequently installed the official RR 6.12.7 ZIP through its native picker/installer, displayed the RR title and cloned KartPad license, and completed the normal Retro WFC login and approved consent flow. Mac friend-code registration was confirmed through the game UI. Gameplay completion, save readback and a two-client online race remain separate gates.
6. XCTest setup initially timed out until the user authenticated with Touch
   ID. Use the private agent-device wrapper with the development team on
   every invocation; a daemon started without that environment caches the
   tool's unrelated default signing team.

## Coverage gates still open

- Corrected IPA: gameplay completion, reliable replay quit, pause/restart/results, save/reload and RR race remain open. Installation, native Original import/boot, touch-menu navigation, RR ZIP installation/title/license and WFC login are observed on the physical iPad. Original Luigi staff replay visibly starts, but its completion was not traced; a quit confirmation returned to the replay menu rather than the course screen and is not marked passed.
- Online: login, matchmaking, two distinct client identities, a complete
  race, results, and reconnect. Compiling a payload is not online acceptance.
  The corrected macOS RR candidate has now reached the public Retro WFC
  1-player lobby through its normal login flow. The user explicitly approved
  the displayed Mii/nickname/record/ghost sharing consent before `Permit`
  was selected. The lobby exposes Worldwide, Battle, Friends and leaderboard
  entries. This closes only the macOS login gate, not matchmaking/race/results
  or full iPad online acceptance. The iPad later reached the same lobby and registered the Mac friend code through the normal UI; mutual registration and room joining are in progress.
  A subsequent cold process restart preserved the RR license/save and skipped
  the already-approved consent screens; normal login succeeded again and a
  Friends room reached `Waiting for friends...`. The run has a separate
  `native-jlink-cold2` log/trace. This proves cold re-login and room creation,
  not recovery from a mid-race disconnect or a two-client race.
- Historical course coverage (now excluded from the goal): the 32 retail staff ghosts pass structural coverage,
  but structural coverage is not runtime coverage. On the original macOS
  candidate, Luigi Circuit (5,615 input frames) and Moo Moo Meadows (6,106)
  complete through the unmodified retail replay path with exact trace spans.
  Other courses and modes are not marked passed yet.
  The expanded course ledger now covers 386 logical rows and 465 archive
  variants, all passing the static archive checks. Three config diagnostics
  are retained: one header variant-count mismatch that the source recomputes,
  and two sets of unused FILE keys that the source bounds check ignores.
  These are not missing archives. Three macOS staff-replay rows are verified;
  the other 383 logical rows remain runtime-pending. See
  `artifacts/2026-09-07/rmcj01-course-coverage.md` for variant counts and limits.

## Reproduction entry points

- `scripts/translate-rmcj01-retro.sh DATA RETRO_ROOT JAPANESE_PAYLOAD`
- `scripts/build-rmcj01-ios.sh TRANSLATION DATA [base|retro-rewind|dual]`
- `KARTPAD_RMCJ_BUILD_TAG` selects fresh private/build output paths.
- iOS host mirrors include the repository's CMake integration scripts;
  each iOS build has its own parent `generated` link, separate from macOS.
- Public PAL importer and audit defaults remain strict and unchanged.

Private logs and screenshots are under `private/rmcj01/mobile/`,
`private/rmcj01/ios-dual/`, and `private/rmcj01/retro/`. They are not published.
The shared regression checkpoint has 103 Python tests (102 passed, one missing
cached-PAL-payload test skipped), checked guest-memory tests including
ASan/UBSan, and the installed/portable storage-layout contract passing.
The Darwin host portability graph also passes all 16 CTest cases, including
guest scheduling/memory, network waits/TLS/local routing, Mii seeding and
mobile input/controller/motion contracts. These are host contract tests,
not a substitute for physical iPad gameplay.
The Japanese production payload passes signature validation and a mutated
payload is rejected even when its hash pin is recomputed. The old PAL payload
cache could not be populated from its mutable URL because the response exceeds
the pinned size; the downloader rejected it without updating any release pin.
These checks do not replace game-flow acceptance.

### Online continuation checkpoint

Mac room waiting subsequently displayed communication error 83337 with its process still alive. This is retained as an open stability finding, not suppressed by the earlier login/room-creation pass. A separate 03:10 Mac process change and its trace have unknown provenance and are excluded from accepted course runs. The iPad currently has a dedicated on-device state trace with no RKG input or forced-finish environment enabled. See the platform acceptance reports for evidence paths.

### iPad local-network declaration correction

After normal mutual friend registration and presence discovery, iPad `Meet Up`
remained in `Joining a friend...` and ended with the game's normal failure
message. Both clients continued rendering; no online race was accepted.
The iOS runtime plist lacked `NSLocalNetworkUsageDescription`. This declaration
is required for direct local-peer communication by Apple TN3179
(https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy).
It is now declared in both iOS plists and required by the package audit, with a
focused contract regression test. This fixes a packaging omission, not yet a
proven root cause of the room timeout.

The actual Japanese host plist was refreshed and Xcode rebuilt the app.
Unsigned executable SHA remains `4959b168dd198346d916cbb8342c221a75409f990e4192b33617a36ccdba21ab`;
`NSLocalNetworkUsageDescription` is the only changed processed plist key.
The newly signed local candidate is
`private/rmcj01/mobile/signed-local-network/KartPad-Japan.ipa`, SHA
`ef1c94489c5b0e1b3dd35d5da232df98f4ff48815e3ffcea389434a790c528fe`.
It passes strict signing verification and ZIP/content inspection and was
installed as an update on iPad. Cold launch retained installed RR 6.12.7,
license/friend code, and normal WFC re-login without repeated consent.
Its live log is `mobile/ipad-local-network-live.log`; the old process's signal 9
was caused by this explicit install/relaunch, not an observed spontaneous crash.
The new room-join attempt and local-network authorization remain under test.

Original save cold readback is byte-identical to the pre-cold file and its
stored CRC matches independent CRC32. The RR redirected save has a separate
valid CRC and differs from Original. This establishes persistence/separation,
not a newly completed race record; see the iPad acceptance report.

### Trace-only diagnostic checkpoint

The declaration-only iPad update still timed out joining the Mac room; no
local-network permission alert was observed during that attempt. No causal fix
is claimed. Both platform package scripts now declare local-network usage.

A default-off `KARTPAD_WFC_TEST_TRACE=1` switch now enables the existing bounded
UDP metadata logging without setting any host or port override. The RR-only
and unchanged-destination contracts pass the native regression tests. The
Japanese iPad diagnostic IPA is `mobile/signed-udp-trace/KartPad-Japan.ipa`, SHA
`c75fc5c890ec6c86c830f503592f0462c94d0dab4567d898be232526d11d4775`.
Its unsigned executable SHA is
`f8e0edb8972dc5212bf1249a45e76b2d92eb69c6f71d69cbc4c386ea66404435`.
The Mac diagnostic candidate is `retro/wfc-trace-candidate/KartPad-Japan.app`.

Mac dual-product startup reads its saved Game-menu profile and overwrites the
profile environment value. Root explicitly selected Retro Rewind through Game
and restarted; `retro/mac-udp-rr-live.log` proves the actual `retro_rewind`
profile. The earlier `mac-udp-live.log` was a base-profile startup and is not RR
evidence. The prior Mac console identity was copied into the new candidate's
private UserData before online login; the displayed Mac friend code matches.

UDP metadata now proves request/response exchange with the WFC master service.
The iPad diagnostic log also records three successful native sends to the NAT
negotiation service on UDP 27901, without a recorded reply in that bounded log.
Logging is bounded, so absence is not a complete packet-capture assertion.
No two-client joined room, race or result has yet been verified. iPad's process
later exited with code 0 and the next UI showed the chooser; this transition is
not accepted as a successful online result. At 04:21 the iPad battery displayed
9%, and the user was asked to connect a charger before extended device runs.

Current regression checkpoint: 104 Python tests, 103 passed and one old PAL
payload-cache test skipped; 16/16 host portability CTests pass. The first broad
Python invocation lacked PYTHONPATH and failed collection in two modules; the
corrected toolchain/PYTHONPATH invocation is the reported full-suite result.

Mac diagnostic continuation: root observed normal Close the room → Yes → Friends, then Disconnect from Retro WFC → Yes → the RR main menu. No forced process termination was used for these transitions. The pre-race checkpoint log is `retro/mac-udp-room-completed.log`.
