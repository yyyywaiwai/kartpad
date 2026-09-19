# Next-build backlog audit — 2026-09-16

Reviewed the49 open issue titles/bodies and recent repository comments. Scope is
candidate work and evidence, not closure of unresolved hardware reports.

## Feature priorities

| Issue | Finding | Next-build decision |
|---|---|---|
|297,184 controller mapping|Android already ships one-to-one D-pad Up remapping.297 asks for simultaneous actions and triggers.|Local114 adds optional shared assignments for existing seven buttons. Default swap and old mappings preserved. Other directions/triggers and Apple parity remain open.|
|250 Mac VSync|Merged255 and present in downloadable0.4.22 Mac build43.|Reporter given verified download and restart instructions; physical tearing acceptance remains open.|
|295 RKG import/export|Existing inspection/debug fixtures are not a user feature.|Prefer export of an explicitly selected Original personal ghost first; import requires bounded decompression, checksum/header validation, course/license matching and overwrite backup. RR custom-course association requires separate validation. No UI implementation yet.|
|203 RMCE01, NAND transfer, cheats|Three separate capabilities; product code alone does not establish translation compatibility.|Not quick fixes. Full backup/restore overlaps234; no promise of automatic identity repair.|
|234 serial/country/Mii restoration|Raw save/rating export omits console identity, Mii database and country state; public0.4.22 notes existing-license22005 remains unresolved.|Do not conflate recent license-name repair with console/server identity repair. A coherent backup manifest and transactional restore are prerequisites.|
|100 external display;199 freeze|Reporter says freeze also occurs on local screen, so an AirPlay-only fix is unsupported.|Investigate display/surface lifecycle with event breadcrumbs; not a quick feature checkbox.|
|91 DSU input|New network input source with disconnect/motion/slot semantics.|Larger feature; defer behind existing controller correctness.|
|90 Wiimmfi|Identity, server compatibility and connection establishment.|Not a cosmetic setting. Keep distinct from206 cellular matchmaking.|
|5 Mii/controller setup|Partly overlaps existing license/Mii selection and controller support.|Do not mark resolved without checking requested custom-Mii creation and hardware pairing behavior.|
|119 system bars|Activity already reapplies immersive system-bar behavior on focus.|No justified new fix from existing report alone.|

## Actual local change and verification

Android candidate114: “Keep other actions on this button” in physical assignment
picker. Defaults remain swapping; checked option allows R plus D-pad Up from one
shoulder. Version3 preference migration validates old permutations and preserves
v1/v2 stores. Native mapping accepts repeated in-range sources and releases all
outputs when the source releases. Existing analog triggers and other directions
remain direct. Apple mapping has a distinct five-button adapter and is unchanged.

Kotlin migration/shared/reset/invalid tests pass, including validv2 preservation.
C++ input contract passes with warnings-as-errors. Full APK build and package
audit pass. Test runner repaired to exclude sources/javadoc jars after Gradle
populated those artifacts and exposed ambiguous jar selection.

Private APK: build/android-full-race/KartPad-114-shared-controls-test.apk
SHA256:a983cbcc0706f0a2c4ca5b38c9ee3b2cad43fed15381776a160472573f056aae
Not installed, published or hardware accepted. Includes prior113 diagnostic/cache
candidate; it must not be described as a public performance improvement.

## Performance and diagnostic decisions

Current113 owner capture confirms live lap2 with opponents/items and logs53.68FPS,
p9932.82ms,worst39.70ms at2x with shader queue0. CPU sample share for scalar
clear/capture is7.92% of app CPU, approximately14.4% of game-thread samples.
No matched baseline/candidate speedup or GPU execution measurement exists.
Retro menu evidence earlier reached50.04FPS, but no menu CPU sample profile was
captured. Race profiles do not resolve that menu slowdown.

Do not remove the pre-operation clear based on the previous capture clearing
flags: FinishScalarFp performs single rounding afterward, and can set new host
flags; guest/host work may intervene as well. The correctness-repaired combined
kernel already regressed double operations and only slightly helped synthetic
single operations. Repeating it without a different hypothesis is not justified.
A future translator-level optimization must prove flag liveness across guest
instructions and calls, with exact FPSCR/host-state tests; no unsafe arithmetic
change is in114.

Highest-value logging gaps:
1. Android ANR thread stacks and native tombstones, associated with exact library
   build ID and retained symbols. Existing ExitDiagnostics only records metadata.
   Android exposes getTraceInputStream onAPI30; native tombstone protobuf onAPI31.
   Optional traces may be absent/overwritten. Collect on explicit diagnostic export
   off the UI thread with bounds and a private review path, not continuous logging.
2. Session context separating chooser/menu/live race/results; synchronize slow-frame
   timestamps with CPU, render-worker, GPU and thermal evidence. Current rolling
   FPS window differs from the300-present CPU interval and cannot identify one frame.
3. Apple surface/display lifecycle and correlated hang/crash evidence for199/100.
   Generic FPS logging alone cannot diagnose lost presentation or a deadlocked thread.
4. Keep vertex corruption102/104/137/166 separate: reporters still see it at1x,
   and prior draw checks can report finite/valid indices despite visible corruption.
   Require affected-device rendering proof, not a Pixel-only success claim.

Official API reference: https://developer.android.com/reference/android/app/ApplicationExitInfo
Native trace format: https://developer.android.com/ndk/guides/debug

## Public replies completed

297: https://github.com/chrissotraidis/kartpad/issues/297#issuecomment-5693987065
250: https://github.com/chrissotraidis/kartpad/issues/250#issuecomment-5693987462
206: https://github.com/chrissotraidis/kartpad/issues/206#issuecomment-5693987788

206 now reports VPN working on mobile data. This supports connection-path
investigation; it does not prove a specific NAT cause or an app-side fix. Existing
reporters275/198 have already supplied useful evidence and are waiting; no repeat
log requests were posted. No issues closed.

Mac public ZIP SHA256:a2689d3832f004a938b78162ce15cc5940d030dcd152553b5dadaf5b1dbb168a
Matches GitHub asset digest; executable contains VSync preference and restart
message. Tag ancestry includes255. This verifies availability, not physical tearing.
