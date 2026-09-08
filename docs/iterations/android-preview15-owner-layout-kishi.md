# Preview 15: owner touch layout and Kishi readiness

2026-09-07. Original Android-only source checkpoint, followed by physical acceptance.

## Final owner acceptance

The owner tested Original Grand Prix with Yoshi/bike/manual drift using Razer
Kishi, confirmed touch controls hide when connected, and reported working
controls/gameplay. They accepted this runtime for the first Android community
release and explicitly authorized merging Android into main and publishing it.
Earlier in the session they reported Retro Rewind 6.12.7 Retro WFC login,
worldwide matchmaking and live race play at 3x over Wi-Fi. No completed results/
reconnect, Kishi rumble/hotplug matrix, or sustained 60 FPS claim follows.

Private logs preserve a startup interval at 19.11 FPS with 1,409 pipelines queued,
recovering to 59.43 FPS once the queue emptied. Later windows were roughly
50–59 FPS with zero pipelines queued and intermittent presentation delays;
thermal status 2 and battery temperature 42.3 C were observed. The 30-second
user-cycle profile captured 19,227 samples with zero lost. Compilation is a
strong startup correlate; later CPU/presentation/thermal contributions and any
network lag remain distinct questions. Raw logs/profiles stay private.

All no-publication and hardware-unattached statements below describe earlier
checkpoints and are superseded by this acceptance. See
`../releases/v0.4.10-android.1.md` for the public artifact boundary.

## Owner acceptance and remaining performance work

The owner restarted Preview 14, completed a race, and reported substantially
better gameplay. Fill Screen Experimental was acceptable. They observed about
56 FPS, tried 4x resolution (more slowdown with little perceived visual benefit),
then selected 3x. Menu dips remain. This is valuable hands-on evidence, not
sustained-60-FPS or full-parity acceptance, and it does not isolate which change
caused the improvement.

The restarted app's private logcat capture remains local. Early intervals show
roughly 51–56 FPS with OS thermal status 0. Later mixed gameplay/menu/layout-editor
intervals include about 42 FPS and thermal status 1. Some presentation windows
increase to 8–12 ms, then return toward 1–2 ms. Exact resolution/time attribution
needs the health-journal export; do not ascribe every dip to the same cause.
A 30-second profile has 16,436 samples, none lost, but a screenshot shows the
paused layout editor during that window. It is explicitly a mixed-session
profile, not a clean active-race benchmark.

## New phone defaults

Captured from the owner's visible controls and accessibility bounds at 2244x1008,
with safe insets left 149, top 54, right 0, bottom 54:

| Control | Center in safe frame (normalized) | Individual size |
| --- | --- | --- |
| Movement pickup | 0.12649165, 0.77888889 | unchanged |
| X | 0.11336516, 0.49777778 | 1.20 |
| Y | 0.04773270, 0.55944444 | 1.24 |
| Start | 0.93651551, 0.19111111 | unchanged |

Start is upper right, below the three-dot menu. Default-only spacing protects the
menu on shorter phones. Other controls retain their positions, the idle movement
stick remains floating/invisible, and the D-pad remains hidden. Existing custom
origins, sizes, visibility, resolution and aspect preferences always win. No
layout reset or preference migration is performed. Android tablet defaults remain
unchanged. Pixel-derived centers are accurate to screenshot/accessibility pixel
rounding, not a direct extraction of private preference floats.

## Kishi readiness, not hardware certification

The pinned SDL **3.4.4** contains an Android mapping for Razer Kishi in its
[upstream database](https://github.com/libsdl-org/SDL/blob/release-3.4.4/src/joystick/SDL_gamepad_db.h#L803).
This does not prove every Kishi generation, firmware or USB connection works.
No Kishi/gamepad is currently attached. Do not invent a device mapping without
observing the actual controller.

KartPad's existing standard SDL path maps A/B/X/Y, left stick, D-pad and Start;
left shoulder maps to Z, left trigger to L, and right shoulder/right trigger to R.
Existing remaps still apply. Host tests pass for button and axis mapping, trigger
thresholds, neutral disconnect, invalid mapping fallback, and four independent
controller slots. The actual prepared-source probe confirms repeated connectivity
checks do not consume short button edges, and verifies suspension/disconnect
isolation. These are not physical Kishi tests.

When attached, check:

1. Recognition in KartPad and touch controls hiding without leaving A locked.
2. A/B menu navigation, Start pause, left-stick steering and D-pad navigation.
3. Simultaneous A + steering + R, then Z and L separately; trigger release must
   return to neutral. Check both Original and Retro Rewind.
4. Disconnect/reconnect, HOME/Recents, screen lock/resume, and touch reappearance.
5. Rumble only if the attached controller supports it; do not equate phone
   vibration with controller rumble.

If attaching Kishi occupies the phone's USB data connection, do not treat loss
of wired ADB as an app failure. The private runtime/health logs remain on-device
and can be exported locally after reconnecting. Never clear data to set up this
test, and never publish an unreviewed diagnostic archive.

## Candidate and validation

Private `0.4.10-android-preview.15`, code **20**, full dual-runtime AAB and locally
debug-identity-signed universal ARM64 APK. Unchanged package audits pass:
`dev.kartpad.android`, min API 28, target SDK 36, non-debuggable, profileable.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| AAB | 91,220,835 | `913d30114a00c807960d0efa1185c402427c8acf50bdf09a2a9ad98f549cdadc` |
| APK | 110,323,026 | `50e02a5719398192e5028d59345daf88f87702027968262513bda831156d7dd0` |

134 Python contracts, native touch-input tests, native gamepad contract and
prepared-source controller probe pass. The layout build is verified, but its
default geometry has not yet been exercised on a clean emulator profile.
Do not reset the owner's customized phone to do that test.

Installation completed after the owner unlocked the phone. The guarded code 20
update passed, both selector profiles remain present, and Original launches.
Fresh post-race save exports before and after update match byte-for-byte
(2,867,200 bytes). No uninstall, clearing, downgrade or preference reset occurred.
The game was returned to the owner for testing, with UID-scoped logging active.
The new full physical checklist and explicit health-journal ZIP export remain
open. No Android merge to main or package publication is authorized.
