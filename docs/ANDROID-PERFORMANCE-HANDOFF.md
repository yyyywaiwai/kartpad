# Android investigation handoff

Current public baseline: **Android 0.4.18/code 83**. Its APK, source, notices and checksums are published and independently downloaded/verified. See the [release evidence](artifacts/2026-09-13/android-code83-public-release.md), [priority review](artifacts/2026-09-13/high-impact-priority-review.md) and [maintenance board](MAINTENANCE-BOARD.md). Older code63/code73 assignments are historical.

## First: sustained frame time

#198 already supplied three captures and agreed to a profiler handoff. Its Helio G85 report is 25–29 FPS after the pipeline queue reaches zero, with 94–97% main-thread occupancy and 2.3–2.6 ms measured presentation. This supports CPU sampling; it does not identify the expensive function. GX CPU work outside the presentation timer remains a possibility.

Prepare a current, non-debuggable, shell-profileable diagnostic with exact native symbols and a compatible signer. The release signing key location is resolved. The retained code73 Debug-signed profiler cannot update a Community-signed installation. Confirm the recipient's installed version/signer and concrete private delivery route before handing off a diagnostic. Keep credentials, symbols and private game inputs out of public artifacts.

Capture a bounded approximately 20-second, 99-Hz symbolized sample during a warmed driven slowdown. Separate guest execution, GX CPU preparation and waits before choosing one correction. Use the owner's phone for a local baseline when available; it cannot establish Helio acceptance. Do not repeat #198's willingness/log requests, #167's completed resolution/aspect sweep or #103's already supplied build/settings questions. #204 is Cookie Land **battle**, not time trial. #135 A10X performance is an Apple comparison with no proven shared cause.

For baseline/candidate, hold scene, settings, normal power mode and thermal range comparable. Record frame-time tails and gaps, effective cadence, audio and health; separate cold shader compilation. Prefer three matched runs per artifact. Improvement must exceed baseline variation without graphics, audio, save or lifecycle regressions. Finish with profiling disabled.

## Second: actual failing character draw

Recover the retained PNMTX experiment into a clean current-code83 source tree. Preserve selected-draw and pipeline identity, disable diagnostic draw merging and compile the actual generated vertex shaders. Old scratch APK names are not provenance. Finite CPU matrices and generic passing probes do not validate the failing shader.

Use an affected device for dynamic → selected literal → dynamic comparison on the same observed character draw. A Pixel pass cannot accept S24/Adreno840 corruption. Only after the comparison discriminates the cause should a narrow correction be tested on affected and known-working hardware.

## Ownership and release gate

Refresh issue comments and current build/device ownership before acting. One operator owns native builds and the device session. Preserve saves, profiles, identities and signing; never uninstall or clear data to cross a signer mismatch. Keep source-only experiments isolated from concurrent work.

Every handoff identifies source, version/code, APK hash, native payload, signer, exact operation and completion condition. Host checks, installation, startup, driven gameplay and online endurance are distinct evidence. Build a new public release only for a verified correction; a diagnostic is not a performance-fix release.

[Build instructions](../android/README.md) · [Physical procedures](ANDROID-PHYSICAL-HANDOFF.md) · [Performance notes](PERF.md)
