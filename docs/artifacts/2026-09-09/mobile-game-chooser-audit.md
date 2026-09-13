# Mobile game chooser: iPad-first review

9 September 2026. Stacked on the iOS reporting/menu cleanup in PR #159.

## Findings and changes

1. **Choose a game — improved; owner accepted build 32.** The actual M2 iPad
   chooser had two small central buttons, a large decorative gradient, and no
   setup-help entry. The native replacement uses quiet bordered cards, the
   existing KartPad mark and platform icons, explicit imported/required/ready
   status, and a visible Help button. Paused games retain Resume and next-launch
   switching. Runtime profile selection and import/download callbacks are retained.
2. **Understand setup — improved; native help exercised.** Help explains the
   supported owned PAL (Europe) Mario Kart Wii ISO/WBFS (RMCP01 revision 0),
   extracted DATA alternative and RVZ conversion requirement. It then explains
   adding Retro Rewind through KartPad after importing the base game. Required
   pack version comes from the existing installer. The two sections avoid implying
   that a separate Retro Rewind disc is required.
3. **Find support — working in the native UI fixture.** Setup and troubleshooting
   buttons open the actual GitHub INSTALL_IPA.md and SUPPORT.md pages. Help's Done
   control returns to the chooser. Version/build details remain available in Help.
   No report was posted and no device data was uploaded.
4. **Fit iPhone landscape — corrected after owner review.** The first candidate
   still placed the support footer below the phone viewport. The owner rejected
   that scrolling layout. The revision keeps the brand, Help and both game cards
   together and moves supplementary guidance into Help on compact screens.
   Shorter action labels retain the game name in their accessibility labels.
   iPad retains the fuller descriptions and support footer.

## Research grounding

The current [Android community thread](https://www.reddit.com/r/decomps/comments/1w9wf66/kartpad_wiicompiled_first_android_community/)
includes confusion about finding the built-in Retro Rewind download, importing a
Retro folder and choosing the supported game region. Those are setup-order and
requirements-discovery problems; this pass makes that information available
before importing. It does not claim to resolve every installation failure.
The recent GitHub issue list was also reviewed, including closed issue #142's
presentation feedback. No community reply was sent as part of this work.

## Validation

- Initial source commit `8812843`; compact-phone correction `2e46881`.
- Complete dual-profile physical iOS app builds and its unsigned bundle audit
  passes after both changes. The compact correction passes all 18 matching
  `test_ios_*contract.py` tests; the initial pass also passed 23 focused existing
  contracts and 25 builder tests.
- A temporary UIKit fixture compiles the exact chooser class from the source.
  Only installed-data state and the terminal game-selection callback are stubbed.
  Actual taps invoke base and Retro callbacks; Help/Done and both real GitHub
  destinations were exercised. This fixture does not establish gameplay,
  fresh disc import, network pack installation or VoiceOver acceptance.
- The final native scroll geometry is checked in missing-data, ready and paused
  states on iPhone 17 Pro and iPhone SE (3rd generation) simulators. All six cases
  have zero vertical overflow: content equals viewport (750 x 382 and 667 x 375
  points respectively). The iPhone 17 Pro screenshot confirms all primary
  controls are visible together. Accessibility text sizes intentionally retain
  scrolling rather than shrinking or truncating the text; the largest size was
  inspected for header/help access, not a complete accessibility certification.
- Initial full build 31 was installed in place on the physical M2 iPad and
  launched Retro Rewind using the owner's preserved next-launch choice. All
  32 protected files (19,871,359 bytes) were byte-identical between fresh pre-
  and post-install snapshots, including preferences. No restore was performed.
- Private full build 32 contains the compact-phone correction and passes strict
  signing verification. At the owner's request it was subsequently installed
  in place on the hardware iPad and launched without a debugger. Device inventory
  confirms build 32. All 32 protected files (19,871,308 bytes) are byte-identical
  between fresh build-32 pre/post-install snapshots. Neither candidate is a
  published IPA. Build numbers are overridden only in
  the private staged bundles; public release metadata is unchanged.

## Review evidence and remaining scope

Private screenshots, exact-source fixture, geometry results and build logs are
under `build/chooser-review`; installation/signing evidence is under
`build/ipad-physical`. The accepted before screenshot is
`01-ipad-current-menu.png`; the revised phone screenshot is
`09-iphone-no-scroll.png`; help is `04-iphone-help-preview.png`. Intermediate
letterboxed/rotated simulator captures are not the final visual handoff.

The owner subsequently accepted the full build-32 candidate on the hardware
iPad and requested its official release. An initial full-app Retro Rewind launch
was observed; no physical after-menu screenshot is claimed. The owner feedback
is recorded separately from screenshots and simulator evidence. Full fresh
setup on physical hardware was not tested because its existing game data was
preserved. Android chooser propagation follows this iPad review as requested;
this branch does not change Android's chooser or use its owner's hardware.
The accepted changes are published in [0.4.14/build 33](ios-v0414-release.md).

Build 32 source: `2e46881f6694423c896288fccaddfa53f1b4dcce`.
Private signed executable SHA-256:
`66f097da4dd0f1d947e1c49b88d3f07f616043d73025aab48d3f6d18d053d9e5`.
