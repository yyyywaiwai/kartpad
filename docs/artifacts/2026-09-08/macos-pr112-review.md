# macOS PR #112 local review — 8 September 2026

Reviewed contributor head `ab9561197ed44692884a80ade8d1b4ccc067ee46`
from [aedanpilkington's PR #112](https://github.com/chrissotraidis/kartpad/pull/112).
This is local acceptance work, not a release or merge approval.

## Verified

- Full ARM64 Original + Retro Rewind dual runtime built with the pinned
  translation inputs. Package audit and strict local signature verification passed.
- Assignment/cached-index, native settings bridge, controller-profile and
  virtual-input tests passed, including unreadable-profile preservation.
- Settings shortcut host test passed.
- An isolated app copy with separate bundle identifier, portable data and
  networking disabled reached the Original title screen with locally owned data.
  Cmd-comma and F10 opened native settings. All five tabs opened; graphics/audio
  changes persisted to the isolated configuration and were reflected on reopening
  the panel. Compatibility Tools opened the intended legacy overlay.

The original audited app's unsigned runtime SHA-256 is
`ca5a83528da0d96f7c9bfeb73194f4906a1a2b56bd396651c26151b940042796`.
The later trigger-corrected runtime is a different local artifact.

## Required corrections

1. Trigger-axis isolation clears `PADStatus.triggerLeft/Right` before subsequent
   assignments overwrite them. A fully pressed RT still outputs 255 with an
   explicit Drift button binding. The [review](https://github.com/chrissotraidis/kartpad/pull/112#pullrequestreview-5137141071)
   requests changes. Local correction zeros `tl/tr` before final assignment.
   `scripts/test-macos-trigger-output.py` compiles the prepared runtime's actual
   trigger block and verifies 200 combinations of both bindings, both axes and
   trigger emulation. It fails against the contributor head and passes with the
   correction. Corrected Original and dual executables rebuild successfully.
   Correction commit: `9b3ea0b` on `codex/pr112-local-validation`.
2. At the default native settings size, the Controllers tab clips the rightmost
   Clear buttons. The document's fixed width and mapping columns need to fit
   the visible scroll viewport or provide suitable scrolling/resizing behavior.

## Remaining acceptance

No physical controller was connected for these checks. Cold launch with a pad
already connected, hotplug/reconnect, both trigger bindings in a race, profile
restore across app launches, multiple controllers, full-screen transitions and
Retro Rewind gameplay still require acceptance. A dual compile does not prove
those paths. No contributor build has been approved, merged or released here.

Recheck the final contributor head against current main before integration;
retain contributor attribution. Source-local build notes are not a substitute
for a portable upstream support guide.

## Second local pass

The maintainer's `codex/pr112-local-validation` branch now includes the trigger
correction and `f2bc5b6`, which widens the settings viewport and provides a
horizontal-scrolling fallback. Visual inspection confirms the right-hand Clear
buttons fit the default native window. Windowed → borderless fullscreen →
windowed rendering and F10 settings access in fullscreen also pass locally.
Reduced-height resize and the notch/exclusive variants remain unaccepted.

A local **macOS 0.4.12/build 27** dual candidate was packaged from `f2bc5b6`.
Its unsigned runtime SHA-256 is
`bacfc8cf7893340cae8a3c2c9f27f3b3b51391c18b403556b95979be4a4cf0c7`.
The package audit passes with explicit version/build expectations; profile
and 200-case trigger-output tests pass. These changes were sent to the author.
At that point PR #112 remained at the initial reviewed contributor head and
was not approved.
This Mac candidate does not change Android, iPadOS or tvOS. It is not published.

## Revised contributor head

Contributor head `271fdc135a03e4e067778f7683176c581ad2b75f` incorporates the
maintainer trigger correction as `3b97827` and a different, narrower layout.
The full Original/Retro dual runtime rebuilt successfully. The actual prepared
trigger-output block passes all 200 cases; controller-profile tests pass.

A fresh local 0.4.12/build 27 app passes strict signature and package checks.
For its version assertions only, the audit uses the maintainer's explicit
version/build override support from `b561626`; the author script still defaults
to 0.4.11/build 26. Unsigned runtime SHA-256:
`669f1520b07fbb4e0d265aac0a6dd39b81854cad2e430ad30d51e3b7fb25e4c2`.
Bundle content hash:
`fc9542e6bf2ffdab7d3dd4ecc19b71fbe4d419c5ccb1b591da6cf52311f41a52`.

An isolated, separately identified app launched Original with networking off.
Cmd-comma opened native settings and visual inspection confirms all right-hand
Clear buttons fit the default window. Physical controllers were absent. The
earlier fullscreen result belongs to the maintainer candidate; it is not
relabelled as a final-head hardware test. Final-head controller/race/Retro and
small-height/notch acceptance remain open, as does replacing author-local paths
in the support notes. PR #112 remains unapproved and this candidate is local.
