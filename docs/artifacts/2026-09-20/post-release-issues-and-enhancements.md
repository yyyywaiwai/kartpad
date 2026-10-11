# Post-release issue and enhancement audit — 20 September 2026

Reviewed 61 open issues and the closed issue titles, with source checks for the
feature requests and relevant closed enhancements (#162, #184, #188). Baseline:
main `f0db8df`, release v0.5.0 (Android135 / Apple59), compiled source `a2f41d5`.
This is an issue/source audit, not another binary release or device test.

## New reporter outcomes

- **#104 remains broken on the actual release.** The [new report](https://github.com/chrissotraidis/kartpad/issues/104#issuecomment-5747752652)
  identifies S24 Ultra / SM-S928B, Android API36, Adreno750, Original,
  0.5.0/code135, 1x and Normal. Its selected session confirms successful Vulkan
  initialization and rendering, including frame samples with no queued pipelines.
  The reporter still sees character corruption. The log contains an older
  chooser low-memory exit; it must not be assigned to the selected game session.
  The selected session ends with a recorded self-exit, not a native crash trace.
  Thumbnail correctness is not character-geometry acceptance. Engineering owns
  an actual failing-draw reproduction; no repeated settings or log request.
- **#198 has no new performance result.** The [reporter is waiting](https://github.com/chrissotraidis/kartpad/issues/198#issuecomment-5747306346)
  for a CPU-specific change. Their acknowledgment is not a passing retest.
- There are no new positive reporter confirmations in the recent open-issue
  replies reviewed here. Source/package checks and owner Pixel thumbnail
  acceptance remain valid within their previously recorded scope.

## Request-by-request coverage

| Request | Current evidence | Next useful work |
| --- | --- | --- |
| #305 Auto-accelerate off | Shipped Android135/Apple59; persisted switch and ordinary hold/release path. Android `KartPadActivity.kt:1814`; Apple `KartPadRuntimeOverlayHost.mm:1960`. | Observe specific feedback; no replacement build just to repeat the switch. |
| #297 / closed #184 shared button actions, D-pad/triggers, L1 items | Mobile UI exposes shared bindings and the item preset; already shipped before 0.5.0 and retained. `KartPadActivity.kt:977,1017`. | Controller-specific failures belong with input lifecycle/mapping, not an unimplemented-menu claim. |
| #299 one release for platform downloads | All six public v0.5.0 assets independently verified. | Catalog integration feedback only. |
| #302 self-build payload size | Pin is 28,992 bytes / SHA256 `099097a0f85a97c348123d91438438b24b112362f1fb23c94df6a343c5366471` in compiled source and main; live endpoint still matches. 4,102-function graph gate retained. | Missed release follow-up corrected. Full self-build launcher remains distinct from its separately verified stages. |
| #295 ghost transfer | Original import/export exists; release explains invalid records. Reporter still reports empty discovery. Retro custom-track ghosts unsupported. | Build a known-good Original save/ghost fixture and verify discovery through the actual parser and UI before calling this solved. Clearer errors alone do not solve missing ghosts. |
| Closed #162 tilt + shake tricks; #273 unspecified motion regression | Apple has `shakeTricksEnabled` and `consumeShakeTrick`; Android `KartPadMotionSteering.kt` has only a steering callback and tilt calculation. Android UI has no shake option. | **Small concrete parity gap:** optional Android shake-to-trick, with threshold/re-arm, one-shot input, persistence and pause/resume clearing. Do not assert it fixes unspecified #273. |
| #197 ipega menu/A/B behavior | New Android assignment fixes shipped; reporter's earlier default-mode mapping failure and online menu behavior are separate. | Verify button press/release, controller/touch handoff and default-mode mappings; avoid claiming Android fixes repair Mac controllers. |
| #306 Mac Wiimote + Classic Pro | Delays and D-pad/remapping still open; Mac has its own SDL mapping/capture path in `KartPadControllers.inc.mm`. | Trace raw device events into mapping and disconnect/resume state; test the Classic extension path. Not merely a missing menu switch. |
| #5 Mii appearance and direct Wii controllers | Mac has Mii import/appearance UI; closed #188 has reporter-confirmed import on Android. Full Mii editor and physical Wiimote acceptance are separate. | Preserve existing imports; track Wii-controller behavior under the concrete controller work. |
| #119 / #202 system bars and handheld insets | Existing immersive handling shipped; AYN report distinguishes navigation insets from the temporary startup border. | Focused surface/inset regression through launch, menu, Home/resume. No generic aspect-ratio toggling. |
| #101 Fill Screen distortion | Projection/HUD comparison remains unresolved. | Separate 3D projection from 2D layout; not a label-only fix. |
| #203 NAND export/import; #234 incomplete save/identity restoration | Raw save/rating and Mii operations exist; they are not a complete NAND/identity/country migration. | Explicit atomic backup/restore design, preview, rollback and unchanged identity. This is not a quick file-copy button. |
| #203 USA RMCE01 | Header inspection helper exists; no USA translation profile. | Separate executable/translation compatibility work. |
| #203 Original cheats | No user-facing cheat-code workflow found in current host code. | Define a narrow offline-only supported scope and save preservation before implementation; keep separate from RMCE01/NAND. |
| #100 / #199 external display/AirPlay | Accepted product request, still no hardware-verified output fix. | First repair reliable system mirroring; dedicated TV game view is additional work. |
| #91 DSU phone controllers | Not implemented; named tvOS/phone target exists. | Optional protocol/input source with disconnect/stale-input clearing; not a small settings-only enhancement. |
| #90 Original Wiimmfi | Not implemented. | Reproducible executable patch/translation and identity/service acceptance. A server-address field is insufficient. |
| #300 older Apple OS versions | iOS16+/macOS14+ remain declared minima. | App plus SDL/Dawn availability/build audit and matching hardware checks. |

## Focused next batch

1. Continue the S24 actual-draw investigation and warmed CPU attribution from
   existing evidence. These are the largest unresolved user outcomes; no general
   GPU/FPS improvement is established by 0.5.0.
2. Finish a small Android shake-to-trick parity change, independently from the
   unidentified motion regression. Reuse the Apple behavior and bound the input
   pulse; do not rewrite the input system.
3. Reproduce/fix Original ghost discovery; validate known personal-best and
   downloaded slots plus empty/corrupt saves through the production parser.
4. Investigate the Mac Classic-controller event/mapping path and Android ipega
   handoff as separate cases. Advance only with a discriminating input test.
5. Keep full save/identity migration, Retro ghost expansion, DSU, external
   displays, USA translation, cheats and older-OS support explicitly scoped.
   They should not disappear inside broad issue threads or be called quick wins.

The maintenance queue and board had stale pre-release instructions, including
code123/126 package work that is already superseded. This audit updates the
relevant active entries and adds explicit feature follow-ups. It does not mark
all requests fixed, close issues or alter the published binaries.

## Verified follow-up replies

- [#104: record code135 negative result, no repeated capture](https://github.com/chrissotraidis/kartpad/issues/104#issuecomment-5748112647).
- [#302: correct the missed release follow-up](https://github.com/chrissotraidis/kartpad/issues/302#issuecomment-5748112849).
