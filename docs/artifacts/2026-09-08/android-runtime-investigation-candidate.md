# Local Android runtime investigation candidate

Source implementation: `34b3de0c1a8588d0851df2a9225745fa00d8a4ad`, branch
`codex/runtime-investigation` in `/private/tmp/kartpad-runtime-investigation`.
Based on main `87c9ab4`; includes rating importer via `96bf634` / `dd72167`,
unfinished-network-call sampling `2506ca6`, Android/iOS context `198ae00`,
actual-draw diagnostics `9985008`, and process-context correction `34b3de0`.
Later documentation commits do not change the candidate implementation.

## Exact artifact

- APK: `/private/tmp/kartpad-runtime-investigation/build/investigation/candidates/0.4.13-local.34b3de0.apk`
- Version: `0.4.13-local.34b3de0`, code 24, debug, ARM64, Android API 28+.
- SHA-256: `08d6def393edf963ed51f8a613228f22e6d385b2986f144e74ecac882681f6ae`
- libmain.so SHA-256: `1c6d125e0edb5944c7a3becf222e8647a7123929d2568a36d3dbc5e4704c3612`
- Adjacent `.provenance.json` records the source commit, builder profile, prepared
  runtime tree and translated shard tree digests. It is private build evidence.

Local test package only. No public release/version reservation, release signing,
or compatibility with an existing production installation's signing key is claimed.
Do not uninstall an existing user installation to try this APK. The coordinator
retains integration/public release ownership and should prepare the eventual
owner-test package through the existing signing/data-preservation workflow.

## What actually changed

Android can import matching Retro rating companions after save restoration, with
staging/backups and selective merging. Mii migration and server synchronization
are not solved by this importer. Network diagnostics can observe an unfinished
host call from the health worker, rather than waiting for it to return. Renderer
Validation samples actual matrix indices and selected matrices before submitted
draws, including merged draws; independent normal/anomaly budgets bound log volume.
Android and iPhone/iPad reports add bounded version/content/clock context. Export
context correctly distinguishes a saved setting from the active game-process
setting, which is unknown in the chooser. No gameplay/performance fix is claimed.

## Verified results

- Full fresh dual native Android debug build + release lint: success in 9m14s.
  Final report-only correction rebuild + lint: success in 22 seconds, 70 tasks
  (29 executed, 41 up-to-date). Final native library exactly matches the first
  candidate that ran on the emulator. Both candidates are retained.
- Final APK allowlist/privacy/resources/dependencies/16-KiB alignment audit passes.
  Final APK signature verification passes (v2; one signer).
- Final 66 Android contracts pass in 5.372 seconds. Android/Apple executable
  context tests pass in 6.588 seconds including configured-on/active-off versus
  unknown-active coverage. Identity/save host tests and 52 rating format +
  64 rating storage checks passed after integration.
- Draw helper ASan/UBSan tests cover every index byte, invalid extents/strides,
  unaligned NaN/Inf and budgets. Actual command processor ARM64/API28 compilation
  and complete fresh source patch preparation pass. Prior unfinished-network
  tests observe a deliberately blocked local socket receive before release.
- Disposable API36 ARM64 emulator, host Vulkan on Apple Silicon: final APK
  installs; same native library reaches original title/license selection, opens
  the native menu and returns to the chooser. Health sampling runs with no
  missing-network-hook warning. Validation-on produces 15 actual draw records
  in the captured sample, with zero detected matrix anomalies. This does not
  reproduce Adreno corruption or measure affected-phone performance.
- Actual chooser > Export Private Diagnostics > DocumentsUI succeeds. Final ZIP
  integrity passes, eight entries; context identifies this exact version,
  configured validation true and active validation null. Crash memory dumps are
  excluded. No upload or GitHub report was sent.
- Initial manually copied disc fixture lacked dvd_root and exited with a clear
  configuration error. Adding the normal fixture configuration resolved startup;
  this was not an importer test. Disc input was copied read-only from local files.
- iPhone/iPad: context formatter host execution and full overlay compilation to
  an IOS/minOS16 object passed earlier, with two existing warnings. No IPA,
  Apple runtime acceptance, or macOS/tvOS diagnostic integration is claimed.

## Remaining tests and investigation

1. Christopher: production-compatible signed Android candidate, preserving data;
   cold launch, original and Retro gameplay, pause/resume, and matched real save
   plus rating restoration with backup verification. No uninstall workaround.
2. Affected Pixel: reproduce online-menu stall on the same settings and correlate
   NetWait/NetStall with phase/audio evidence. Neither networking nor GPU/guest
   scheduling is established as the cause. Successful online races remain a
   separate acceptance requirement.
3. Affected Adreno: same character scene with Renderer Validation on, capture
   bounded DrawCheck and renderer errors if any, then turn validation off for
   normal use. Valid finite matrices alone cannot rule out bad CPU data or GPU
   translation/driver behavior. A reduced failing replay is still outstanding.
4. iPhone/iPad: real report/share formatting and privacy verification on device;
   no formal IPA until Christopher tests and approves it.
5. Retro version pins and static online payload lowering are verified locally,
   but future server compatibility needs its own release/device acceptance.
   Richer session/compiled-source provenance inside reports remains follow-up;
   the external provenance manifest does not supply historical log attribution.
6. New macOS #127 two-player character offsets are separate reporter evidence.
   Do not claim a shared Android cause without a matched reproduction.

The disposable emulator is stopped and its synthetic data retained. Its durable
validation setting remains enabled for diagnostic continuation; physical devices,
existing worktrees/builds and user saves remain untouched. Build/runtime logs,
private ZIPs and screenshots stay under this worktree's ignored
`build/investigation/`. The broader investigation goal remains active.

## Owner-authorized physical installation checkpoint

Christopher subsequently offered the attached Pixel for testing. Read-only checks
identified Pixel 9 Pro XL / Android17 API37, preview.15 code20, chooser foreground
and no active game process. The installed certificate matched the audited local
candidate, so `adb install -r` updated in place successfully. No uninstall, data
clear, signing change or rebuild was performed. This remains a debug test build.

Before gameplay, a private state archive was read and verified: 429 tar entries,
15,319,552 bytes, covering settings, identity, NAND, Retro saves and ghosts. This
backup was taken after package installation enabled run-as, not before the
package update. A second capture after the attempted startup confirms all 406
regular files byte-identical, zero removed/changed and zero new state files.
Private backups and the prior installed APK are retained in ignored hardware
evidence; do not publish them.

The game activity launch returned successfully but immediately paused as the
phone locked. A bounded app-process log capture completed, and a fresh window
query still reports keyguard showing. There is no completed physical gameplay,
freeze reproduction or renderer acceptance from this attempt. Christopher has
been asked to unlock and leave KartPad visible; no further installation is needed.
The next useful physical observation requires that interaction.
