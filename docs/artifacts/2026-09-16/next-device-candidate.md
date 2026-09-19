# Android 115 / iPhone 47 private candidates

Both installed in place on September 16. Android 0.4.24-next-test (115); iPhone 0.4.24 (47). Signing identities match accepted prior builds. Android package audit passes. Before first launch, hashes matched all 36 backed-up Android state files and 26 iPhone files (saves, identities and preferences). Private evidence is under `build/next-device-state`; it must not be published.

## Changes

- Physical controller mappings include all D-pad directions and triggers; optional shared actions and L1-for-items preset. Old mappings migrate; reset persists defaults.
- Original time-trial `.rkg` import/export. Import stages a comparison ghost, backs up the save, patches only the chosen downloaded slot on restart, and preserves intervening progress, identity and personal-best records. Pending imports can be cancelled. Retro custom-track association is not supported.
- Explicit Android private diagnostic ZIP exports include retained OS ANR/native crash traces, bounded to three traces and 1 MiB each, with availability and attribution metadata. Public issue metadata does not include raw traces.
- Apple logs include lifecycle, display, memory-warning and thermal transitions.

## Verification

Host tests pass: Android mapping migration/sharing, native gamepad contract, Apple controller bridge/release behavior, both identity/save suites with pending-ghost progress preservation, compressed and uncompressed RKG roundtrip with ASan/UBSan, and Android trace export compatibility/bounds/null/read/output failures. Android APK audit and iOS strict code-sign verification pass.

On Pixel, launcher and Original boot render, mapping menus scroll through all D-pad/trigger entries, and sharing A with D-pad Up retains A acceleration. Original default mapping restored through UI and verified in saved preferences. The Original ghost menu lists the real license and opens import/export actions; export correctly reports no saved ghosts. No extended controller is attached, so physical button acceptance remains pending.

QuickTime mirror verified iPhone build47 rendering a race with touch controls. Device logs confirm build47 startup and new thermal/foreground/background events. This is rendering and telemetry evidence, not a comparative performance result. Thermal state reached serious (2); no causal FPS conclusion follows from that alone.

Neither phone has saved Original ghost slots. Parser and staging tests therefore use synthetic fixtures; real ghost import/export/replay acceptance remains pending.

## Performance and scope

No FPS gain is claimed. The correctness-repaired floating-point boundary experiment regressed double-precision microbenchmarks and is excluded. Existing Android display-list front-cache experiment remains a candidate without matched demanding-race A/B acceptance. Serial identity repair, geometry/crash reports and Mac-specific work are not resolved by this build.

The iOS candidate is a private relink of current launcher/controller/identity/diagnostic units against the cached build43 runtime and translated objects, retaining the accepted interface assets. Exact source/object provenance is in `build/ios-next47/composition.json`. It is not a full latest-main release. No public release was published.
