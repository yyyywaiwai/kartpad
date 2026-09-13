# Android issue #197: A input investigation

Status: unresolved. This is a maintainer test plan, not a device acceptance
record or a claim that Android build 80 fixes the report.

[Report and follow-up](https://github.com/chrissotraidis/kartpad/issues/197):
Moto g200 5G, reported 0.4.16, ipega controller in Xbox mode; A stops activating
track-selection and online-room menu actions on both controller and touch after
controller use. Gameplay still responds, with automatic acceleration observed.
Default-mode A/B failures are a separate mapping observation. The reporter has
already been asked for a fresh offline touch-only comparison; do not duplicate
that request.

## Source evidence at cf1f59a

- `KartPadOverlayView.beginGasPress` deliberately locks touch A after 1,000 ms.
  The A control turns cyan; another touch A press unlocks it. This state publishes
  A continuously. It is not evidence that the reporter enabled it.
- `clearTouchInput` cancels the hold generation, clears the lock and pointer
  owners, and calls native clear, which also clears pending touch edges.
  `KartPadActivity` calls this on pause/focus loss and when controller handoff
  detects a connected game controller. Android's device count is not proof of
  SDL assignment or a delivered SDL detach event.
- `wiicompiled-android-touch-input.patch` ORs touch and physical classic buttons
  into the same hold mask. The KPAD trigger calculation introduced in
  `wiicompiled-apple-runtime.patch` uses `classicHold & ~previousClassic`.
  A continuously held from either source can therefore suppress a fresh A edge
  from the other source. This mechanism fits the two symptoms but does not
  establish their cause on the reported device.
- `aurora-android-gamepad-event-cache.patch` retains button-down state until
  button-up, samples SDL state at add/remap, and erases the controller on removal.
  The lifecycle suspension masks snapshots and stops rumble but does not reset
  cached button state. A missed release across focus loss is a candidate to
  reproduce; ordinary delivered down/up and detach should recover. Clearing
  cached state blindly could instead lose correctly held controls on resume.

## Maintainer reproduction and negative controls

Use an authorized test device and the exact recorded APK/profile/controller
mode. Follow [the physical handoff runbook](ANDROID-PHYSICAL-HANDOFF.md) for
artifact identity and capture. Work offline first; do not interrupt an online
session to run this matrix. Keep saves, installation and controller mappings.

| Trial | Action | Observation that distinguishes the path |
| --- | --- | --- |
| Baseline | With no controller attached, use short touch A taps in the same offline track menu. | Record whether A works before any controller use. This is the already-requested reporter comparison. |
| Intentional touch lock | Hold touch A over one second, note cyan A, then test short taps; unlock with another A press. | Establish the visible lock signature and recovery. A matching signature supports the touch-lock path; absence alone does not prove the SDL path. |
| Normal controller use | In Xbox mode, repeatedly press and fully release A, then tap touch A with the overlay visible. | Both sources should produce new menu activations after release. This controls for button mapping without lifecycle changes. |
| Held versus released focus loss | Compare background/foreground after A is fully released with background while A is held, release while away, then return. | Failure only in the latter isolates a possible lost-release boundary. Record whether a fresh controller A press/release recovers it. |
| Held versus released detach | Compare unplug/disconnect after release with disconnect while holding A; wait for handoff before touch A. | A delivered SDL removal erases cached state. Persistent failure after real removal points away from that controller cache alone. |
| Default mode | Separately check A and B in the controller configuration screen, then the same offline menu. | Capture the exact ipega model and recognized SDL button behavior before changing mappings; do not combine this with Xbox-mode results. |

For each failure, record menu item, input sequence, cyan-lock visibility,
controller presence, whether acceleration persists, and which recovery works:
touch unlock, physical A down/up, disconnect, or cold relaunch. Record the
first successful recovery rather than applying all of them before observing.
Controller reconnect and focus loss also clear touch input, so recovery by
those actions alone cannot identify which source was held.

Only if a maintainer capture reproduces a stale physical A should a runtime
fix be selected. Its regression test should cover a lost release at the actual
boundary plus normal held input, short taps between guest samples, and detach.
Host touch/contract tests validate their own code paths; they do not reproduce
this ipega report or prove menu acceptance.

## Host cache experiment (2026-09-13)

Run `python3 scripts/test-android-controller-lifecycle.py PREPARED_RUNTIME`.
Like the controller-probe harness, this compiles the actual prepared Aurora
functions against a synthetic controller store. It also extracts the prepared
KPAD classic-trigger expression. SDL device/OS delivery is outside this harness.

Candidate 80 prepared source at `615225b` passed; relevant cache, lifecycle,
assignment, snapshot and controller-probe patches are unchanged at `975ed07`.
The existing controller-probe harness also passed on that source.

- Short press/release survives exactly one sample.
- A genuinely held button survives suspend/resume; a subsequent release clears it.
- A release delivered while suspended clears A before resume.
- A short tap delivered entirely during suspension is deferred for one sample,
  then clears; this does not reproduce indefinite acceleration.
- Deliberately omitting release reproduces held A for 20 samples and suppresses
  merged touch A triggers. A fresh physical down/up restores neutral after its
  one retained edge. This proves the consequence of injected loss, not actual
  event loss on Android or the reporter's device.
- Actual `remove_controller` erases held and pending state while suspended;
  resume and a late release remain disconnected and neutral.

No runtime fix follows from these results: normal event delivery and removal
recover correctly. Clearing on resume without reconciling physical state would
break the genuinely-held negative control. The next narrow investigation is
whether Android/SDL 3.4.4 drops A key-up across focus loss or mode change before
`update_standard_gamepad_button` receives it. Distinguish Android input-device
removal from SDL gamepad removal; the two notifications are not interchangeable.

## Exact bundled SDL event path (2026-09-13)

The local and candidate-80 `SDL3-3.4.4.aar` both hash to
`8652e2b16a7644fb6a755f9a12590f87ae1932f46755485f96c5bd5a4555ce7e`.
The locked SDL Android ZIP records upstream commit
`5848e584a1b606de26e3dbd1c7e4ecbc34f807a6`. `javap -c -p` on its
`classes.jar` established these paths without substituting a newer SDL:

- KartPadActivity has no key overrides. SDLActivity delegates key dispatch to
  Android Activity; the SDLSurface OnKeyListener invokes `handleKeyEvent`.
- `handleKeyEvent` calls native pad-down and pad-up symmetrically, conditional
  on `SDLControllerManager.isDeviceSDLJoystick(deviceId)` at each event.
- Focus changes send a native window-focus event and transition SDL's native
  state. They do not explicitly release gamepad buttons in the Java hook.
- KartPad's menu is a focusable PopupWindow and its dialogs own focus. A release
  routed to that window need not visit the SDLSurface listener. That Android
  window-dispatch route remains untested; the host harness does not simulate it.

The pinned [native Android driver](https://github.com/libsdl-org/SDL/blob/5848e584a1b606de26e3dbd1c7e4ecbc34f807a6/src/joystick/android/SDL_sysjoystick.c)
forwards both down and up to `SDL_SendJoystickButton`; its periodic update is
empty. The pinned [joystick event code](https://github.com/libsdl-org/SDL/blob/5848e584a1b606de26e3dbd1c7e4ecbc34f807a6/src/joystick/SDL_joystick.c)
explicitly permits releases without focus. Host test:

```sh
python3 scripts/test-android-sdl-button-focus.py \
  /path/to/pinned/SDL/src/joystick/SDL_joystick.c \
  /path/to/pinned/SDL/src/joystick/android/SDL_sysjoystick.c
```

This compiles those actual three functions with controlled focus, registry and
mapping stand-ins. It passed release while unfocused, ignored background down,
normal foreground down/up, and symmetric unopened-pad keyboard fallback.
Consequently SDL's native focus filter itself does not drop the release.

Remaining narrow routes are release reaching a different Android window, or
input-device identity/source changing between down and up before SDL dispatch.
The latter gate rechecks current InputDevice sources; it is not fixed by changing
A/B mapping alone. Neither route is established as this report's trigger, and
no state-clearing workaround is justified by the successful negative controls.
