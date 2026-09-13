# iOS reporting and touch-settings cleanup

9 September 2026. Follow-up to the Apple Metal surface candidate in PR #156.

## Owner feedback on the previous candidate

The owner reported smooth controller gameplay at 60 FPS on the attached M2
12.9-inch iPad Pro, a working three-dot menu, and no visible problems in
Original 4:3, 16:9 or Fill Screen. This is controller gameplay feedback, not
touch-input acceptance or confirmation of custom controller remapping. The
feedback did not establish a separate Original/Retro test matrix, external
TV/AirPlay output, or the affected A10X device's startup behavior.

## Changes

- iPhone/iPad Report a Problem uses two short paragraphs. The GitHub action
  creates the existing bounded report, then gives numbered attachment steps
  with its actual filename and the device-specific Files location. The
  prefilled issue also reminds the reporter to attach the log; a report ID
  does not upload it. Share Report continues to use the system share sheet.
- Render resolution is removed from Touch Control Settings. Display retains
  its resolution choices and the saved resolution is unchanged. The KartPad
  subclass removes the inherited row; the pinned SunPad snapshot is unchanged.
- Android has the same duplicate row removed in a separate commit. Its
  existing visual and persistence checks now expect touch settings only and
  verify that changing touch settings preserves display resolution. No Android
  hardware, optimization worktree, or runtime optimization was changed.

## Validation

- 23 existing iOS contracts pass; 34 Android touch-overlay contracts pass.
- Android `:app:compileDebugKotlin` passes. Existing deprecation warnings remain.
  Android device/emulator interaction was intentionally left to its owning task.
- The pinned SunPad snapshot verifier passes.
- A temporary UIKit fixture compiles the exact changed methods with the real
  pinned overlay, settings, input mixer and diagnostics. This fixture uses the
  inherited SunPad controls, not the complete KartPad control adaptations; it
  cannot validate the current gameplay control appearance. It was removed
  from both simulators after the owner identified that visual mismatch.
  iPhone 17 Pro and
  iPad Pro 13-inch (M5) simulators exercise the native views. Runtime assertions
  verify the duplicate row is absent, a saved 3x setting remains 3x, and opacity
  and size controls remain present. Screenshots inspect the shorter iPad form,
  iPhone attachment instructions, and iPad touch-settings panel. The narrow
  iPhone landscape alert retains UIKit's scrolling form behavior.
- The GitHub preparation path creates the expected diagnostic file with
  KartPad branding and current/previous session sections before showing help.
  No GitHub issue was submitted and no diagnostic file was uploaded.

Private UI-review sources, screenshots and logs are in
`build/menu-ui-review`; physical build/update evidence is in
`build/ipad-physical`. These fixtures do not establish full-game acceptance.

## Private device candidate

The complete dual-profile physical-iOS app builds from `fc6ee29` and passes
its unsigned bundle audit. The development-signed copy uses **0.4.13 / build
30**, with the build number changed only in the private staged bundle so it
can be distinguished from the earlier build 29. Its executable SHA-256 is
`ef6fdfb2cb883190e7a1aeafdac0670eceac16dca7b4d3844f43d1ef1a36d84a`.
The signature passes strict verification. This signed copy contains the local
development profile and is not a public release artifact.

The public bundle audit intentionally rejects a development profile; its
passing result applies to the unsigned source app before signing. The full
app retains KartPad's actual control adaptations, unlike the temporary menu
fixture. No controller-mapping behavior or renderer algorithm is changed by
this follow-up.

The candidate was installed in place and launched without a debugger. Device
inventory confirms 0.4.13 / build 30. All 32 protected files (19,871,307 bytes)
are byte-identical between fresh pre-install and post-install snapshots,
including the owner's current preferences. The older baseline differs only in
preferences following the owner's settings changes; nothing was restored.
The new full-game menu appearance awaits the owner's in-game check.
