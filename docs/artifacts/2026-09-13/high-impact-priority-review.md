# High-impact priority review — 13 September 2026

Three independent reviews covered Android performance, Android stability/graphics, and Apple issues against current comments and source. The refresh found 46 open issues after reopening #196, and no open pull requests. This is a prioritization decision, not a new fix or performance claim.

## Recommended focus

| Order | Work | Why it matters | First discriminating step |
| --- | --- | --- | --- |
| 1 | Sustained frame time | #198 reports 25–29 FPS after pipeline compilation, 94–97% main-thread occupancy; #167 reports 15–20 FPS despite the completed resolution sweep. #103 needs high power/heat to reach 60 FPS. | Refresh current-code83 profileable packaging and symbols; capture one warmed driven slowdown and identify guest, GX CPU or wait cost before patching. |
| 2 | Android missing/stretched geometry | Seven reports: #102, #104, #120, #137, #166, #193, #211. Prior initialization work did not resolve all affected character draws. | Recover the actual-draw PNMTX comparison, preserve draw identity, compile generated shaders, and test dynamic/literal/dynamic on an affected device. |
| Alternative 2 | Apple external-display recovery | #100/#199 describe a black/chooser output with audio on wired/AirPlay paths. Existing Metal view recreation checks do not prove full gameplay output. | Test chooser → race and wired connect/disconnect with actual drawable/presentation evidence, then AirPlay separately. |

Actionable data loss or classified launch crashes override these priorities. #169's ordinary-exit loss remains unclassified. #215 and #236 already confirm Android-home exits; what is missing is the actual native/Java/OS exit class. Avoid another destination question. #206 awaits the existing Wi-Fi endurance comparison; do not invent a common carrier/runtime cause.

## Apple scope

#135's A10X startup fix is accepted, while approximately 30–35 FPS remains open. Include that device in performance work without assuming an Android cause. #196's build39 matching-device retest still fails on iPhone17 Pro Max/iOS27. The issue was reopened because there was no corrective build or passing result behind its completed closure. New analytics were absent; the in-app report fallback was already requested. A duplicate IPA would not resolve that failure.

Mac VSync is source-merged and startup-verified. Physical tearing and warmed pacing/audio remain unverified; one FIFO startup logged an audio queue warning. Complete those checks before describing it as a finished Mac release improvement.

## What is already shipped

Android 0.4.18/code83 is public, including Preferred Game and continuation handling. D-pad/FPS changes shipped earlier in code80. Owner general gameplay acceptance came from private code82; it does not establish the exact Item Rain report or online endurance. No extra APK is necessary merely to deliver those changes again. Apple downloads remain 0.4.17/build39.

## Next release condition

For performance, compare matched warmed baseline/candidate runs, preferably three each, with frame-time tails, audio, cadence and comparable thermal/power state. Ship only a measured gain beyond baseline variation with correctness and data-preserving lifecycle checks. For geometry, require an actual failing-draw comparison followed by affected-device and known-working-device acceptance. Publish exact platform-specific changes and remaining limits; neither a build nor an issue closure proves all-device support.

The [Android handoff](../../ANDROID-PERFORMANCE-HANDOFF.md) records execution details. The owner selected Android impact over external-display and A10X work. Drive sustained Android performance first without assuming continuous phone access; keep actual-draw geometry as the next workstream.
