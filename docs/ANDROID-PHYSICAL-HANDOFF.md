# Android physical-phone handoff

This is the authoritative handoff for moving Android KartPad testing from the
current development Mac to another machine and then to one physical Android
phone.

## Current: first Android community release authorized, 2026-09-07

The owner accepted Preview 15/code 20 Original gameplay with Razer Kishi and
automatic touch hiding, after reporting Retro Rewind 6.12.7 worldwide online
race play. They authorized merging Android into main and publishing the first
Android release. This supersedes all earlier no-merge/no-publication checkpoints.
See [installation and signing-transition safety](INSTALL_ANDROID.md),
[release notes](releases/v0.4.10-android.1.md), and the source-build guide in
`android/README.md`. Do not install a differently signed public APK over the
owner's working preview or remove its data. Warm/startup performance and broader
device/controller coverage remain open; acceptance is not a 60 FPS guarantee.

## Historical: Preview 14–15 installation checkpoints

Installation follow-up: Preview 15/code 20 is now installed and Original launches.
Fresh post-race save exports match byte-for-byte. The owner is testing with
UID-scoped capture active; the pending-install paragraph below is historical.

Latest owner session: gameplay is reported substantially better, with remaining
menu dips; the owner selected 3x/Fill Screen and customized the touch layout.
Preview 15/code 20 captures that layout as phone defaults and passes both
package audits, but installation awaits unlocking and a fresh post-race save
export. See `docs/iterations/android-preview15-owner-layout-kishi.md` for hashes
and Kishi testing. Do not reset the owner's layout or reuse a pre-race save as
the current update backup.

Private `0.4.10-android-preview.14`, code 19, is installed in place on the
Pixel 9 Pro XL (API 37, 4096-byte pages). Fresh Original save exports match
byte-for-byte across the updates. Android now recognizes KartPad as a game;
renderer phase timing is exportable, and a differential-tested scalar FPSR
fast path avoids redundant register writes. Actual race profiling confirms
substantial CPU bookkeeping costs, but sustained 60 FPS and complete physical
parity are **not** established. Current hashes, tests and measurement limits:
`docs/iterations/android-preview14-phase-performance.md`. Do not merge to main
or publish Android packages.

## Historical: Preview 12 on 2026-09-07

Private `0.4.10-android-preview.12`, code 17, is installed on the Pixel 9 Pro XL
in place. A fresh Original save export is byte-identical before and after the
update; owned data and installed Retro Rewind remain. Actual user race play on
Preview 11 confirmed severe warm slowdown, not sustained 60 FPS. Preview 12
retains the correctness-tested CPU candidate and adds exportable frame-time,
CPU/GPU and bounded thermal/display-setting history. See
`docs/iterations/android-preview12-warm-performance.md` for current hashes,
evidence and open acceptance, and `docs/iterations/android-v0410-parity-performance.md`
for Apple parity. Do not merge into main or publish Android packages.

## Historical: resumed development on 2026-09-06

After Apple v0.4.8 shipped, Android development resumed on this branch. Private
Preview 8 (code 13) is installed in-place with the shared Apple icon, opt-in local
profiling and a tested Android scalar-mode optimization. Post-update Original
launch and byte-identical save export pass. Rendered attract mode still dips to
approximately 39 FPS; matched menu/race testing and the severe slowdown remain
open. Preview 6 previously verified real picker
WBFS import, Original boot, Retro Rewind 6.12.7 play and byte-identical Original
save preservation. Full physical and player-identity parity remain incomplete.
Do not merge this branch to `main` or publish its packages. See
`docs/artifacts/2026-09-06/android/preview8-performance-iteration.md`
for historical evidence and guarded resumption commands. Preview 5's pre-install
checkpoint remains historical. The earlier pause record remains
at `docs/artifacts/2026-09-06/android/a6-physical-phone-pause.md`.

## Historical Preview 3 source checkpoint

The remaining Preview 3 commands and hashes below are historical; use the
Preview 14 checkpoint above for the current candidate and explicit version guards.

- Branch: `codex/android-a4-touch-settings`
- Audited product base commit: `cdc96af`
- Handoff checkout: the remote branch tip containing this runbook
- Preview identity: `0.4.0-android-preview.3`, version code 8
- Unsigned AAB SHA-256:
  `85a7e12d8ebccbaa313dc2740e86137a26c24d02ac47c7835d6019a60f1335d7`
- Locally test-signed universal APK SHA-256:
  `b709d5e42b08be0e276c2fc07ed25b1f34a58c31282c049d6505a390ee647707`
- APK byte count: `90,502,311`

The APK is a private hardware-test build signed with the local Android debug
identity. It is non-debuggable but is not release-key signed and must not be
published or represented as a public release.

## Pull the Android source on the other machine

```bash
git fetch origin codex/android-a4-touch-settings
git switch --track origin/codex/android-a4-touch-settings
git pull --ff-only
git rev-parse --short HEAD
```

If the branch already exists locally, use
`git switch codex/android-a4-touch-settings` before `git pull --ff-only`.
The resulting branch tip must contain both `cdc96af` and this runbook. Do not
stop at `cdc96af`, because that product commit predates the cross-machine
instructions.

## Transfer boundary

The APK is deliberately ignored by Git and was not uploaded. A Git pull alone
does not provide the complete build. Transfer this exact file privately from
the current Mac to the other machine:

```text
.android-bootstrap/hardware-preview/KartPad-0.4.0-android-preview.3-v8-arm64.apk
```

Place it at the same repository-relative path on the other machine, or pass its
absolute path to the installer. Verify before installation:

```bash
shasum -a 256 .android-bootstrap/hardware-preview/KartPad-0.4.0-android-preview.3-v8-arm64.apk
```

The digest must exactly match the value above. Do not transfer game data,
saves, credentials, signing material, or generated private translation inputs
through Git.

Building the complete product from source on a clean second machine is a
separate workflow: it requires the pinned Android/JDK dependencies plus the
authorized ignored translated-runtime inputs. Prefer transferring the already
audited APK for this first phone session.

## Prepare the phone

1. Use an ARM64 phone running Android 9/API 28 or newer with Vulkan support.
2. Enable Developer Options and USB debugging, unlock the phone, and accept its
   USB-debugging authorization prompt.
3. Ensure at least 6 GiB is free on `/data`.
4. Stop or disconnect every emulator and connect exactly one physical phone.
5. If another KartPad test build is installed, export/preserve its test save
   before allowing an update. Never uninstall or clear package data merely to
   make installation pass.

Run the read-only preflight:

```bash
./scripts/check-android-physical-device.sh
```

It must report a physical ARM64 target, supported API/page size, declared
Vulkan features, enough free space, and a redacted ADB serial.

## Install and start capture

For a fresh install or when the exact preview is already present:

```bash
./scripts/install-android-hardware-preview.sh
```

If a different KartPad test build is present and its save has been preserved,
explicitly permit an update-in-place:

```bash
KARTPAD_ANDROID_ALLOW_PREVIEW_UPDATE=1 \
  ./scripts/install-android-hardware-preview.sh
```

The installer audits the exact APK, rejects emulators and ambiguous targets
before mutation, uses only `adb install -r`, verifies version 8 and the
Original/Retro selector, and starts the UID-scoped capture window. It never
uninstalls, clears app data, or permits a downgrade.

## First physical acceptance session

Use only user-owned supported RMCP01 game data. Test both Original and the
installed/downloaded Retro Rewind 6.12.5 profile where available.

Record these observations without capturing private game imagery or data:

- cold launch, selector, Original boot, Retro boot, and clean relaunch;
- existing license/save visibility and a save mutation surviving relaunch;
- all touch controls, multi-touch steering plus A/R/Z, one-second A lock and
  unlock, haptic events, control move/resize/hide/show/reset, and menu parity;
- both landscape directions, cutout/system-bar containment, HOME/Recents
  resume, lock/unlock, and repeated surface recreation;
- audible audio quality and latency, controller connect/input/disconnect/
  reconnect, assignment, and tactile rumble where hardware is available;
- motion steering in both directions and inverted mode;
- warm gameplay FPS/frame pacing, obvious shader stutter, device temperature,
  and battery behavior after 15 and 30 minutes; and
- Wi-Fi online/local-server behavior only when the matching bounded test flow
  is intentionally being exercised.

Emulator FPS is not physical performance evidence. A physical result should
include phone manufacturer/model, Android/API version, 4 KiB or 16 KiB page
size, and pass/fail observations, but never its ADB serial or other device
identifier.

At the end, generate the fixed-schema sanitized summary:

```bash
./scripts/capture-android-a2-session.sh summarize
```

If it fails the signal matrix, preserve the printed sanitized result and the
human observations; do not weaken the checker. Leave the package and app data
installed for follow-up unless the owner explicitly requests removal.

## Current acceptance boundary

Preview 3 passes clean reproducible AAB production, strict APK/AAB privacy and
package audits, universal and four-part device-split installation, selector,
real Original runtime rendering, and durable-state preservation on API 36 ARM64
emulation. Earlier checkpoints cover API 29 and 16 KiB runtime execution and
repeated debug-runtime lifecycle behavior.

Physical vendor Vulkan, real touch/audio/haptics/controllers/motion, OEM
lifecycle, performance, thermals, battery, and production online behavior are
not yet accepted. Those are the purpose of the next-machine phone session.
