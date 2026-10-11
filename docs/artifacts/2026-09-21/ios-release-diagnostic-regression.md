# iOS 0.5.0 diagnostic-mode release defect

## Evidence

[Issue #310](https://github.com/chrissotraidis/kartpad/issues/310#issuecomment-5752315236)
reports significantly worse busy-scene/POW performance on iPad 9th generation in
0.5.0 than 0.4.23/0.4.24, plus continuing exits after approximately ten minutes.
The claimed crash screenshots did not arrive in the GitHub comment. A direct
attachment of the existing redacted excerpt was requested; no repeat crash or
reinstall was requested. Crash attribution remains open.

The public release IPA was downloaded directly from GitHub, and its SHA-256
matches GitHub's asset digest:
`7c64144ea996f438aab853e700c8ffa3b8b9db205fdb8033714b07ca6186cadf`.
Its Info.plist identifies version 0.5.0/build59 and
`KartPadDiagnosticsCandidate = YES`.

The pinned iOS runtime's PublicProducts.cmake sets that Xcode attribute to YES;
the build wrappers previously did not override it. KartPadSystemDiagnosticsStart
reads the plist with Foundation boolValue and sets KARTPAD_RENDERER_VALIDATION=1
and KARTPAD_FUNCTION_TIMING=1. The renderer consequently enables validation and
robustness; function timing and draw diagnostics also become active. This is a
confirmed unintended configuration in the stable release, not yet a quantified
cause of the reporter's slowdown.

## Correction and isolation

Both iOS build wrappers now explicitly pass NO to Xcode by default, overriding
an existing generated project's YES. Diagnostic builds remain available through
`KARTPAD_DIAGNOSTIC_CANDIDATE=YES`. The app audit requires its plist to match this
explicit choice; normal auditing rejects diagnostic mode and unresolved values.

A private control IPA changes only the public IPA's candidate flag to NO.
Every other ZIP entry is byte-identical, including the executable with SHA-256
`297d598974993e60109cc125667a4b8c6ac8d463c424b50c207a09b7a0647098`.
The control retains build59 identification, is explicitly labeled as an isolation
control, and is not a new public release or installed/accepted build.

Validation performed:

- Foundation host harness reading the actual public/control app plists and using
  the startup condition: public enables both environment flags; control leaves
  both unset. This verifies configuration activation, not physical gameplay.
- New default audit rejects the actual public IPA's extracted app.
- Full iOS app audit passes for the flag-only control, preserving binary identity.
- Shell syntax checks pass for both build wrappers and the audit.

Next acceptance check is the same warmed Retro scene/settings on the affected
iPad, including the POW trigger, comparing the public package with this control
using the same signing identity and in-place installation. Do not remove data.
If substantial slowdown remains with diagnostics off, investigate the newly
mandatory texture-copy pipeline waits and bounded 128-recipe shader prewarm.
Do not revert texture correctness repairs merely to regain FPS.

The ten-minute crash requires the matching exception/termination/frames; neither
this packaging finding nor older build51 cleanup crashes establish its cause.

## Other current evidence

The latest #301 response confirms Moto G85 startup recovery, but invisible
character parts and idle/input-related slowdown remain. A matching current
session excerpt was requested. #104's code135 supplied log runs in normal
renderer mode and reaches approximately 60 FPS while character corruption
persists, so it is not evidence for this Apple configuration defect. Existing
#198/#275 code119 diagnostic logs remain evidence for their separate Android
main-thread slowdown, with their diagnostic overhead explicitly retained.
