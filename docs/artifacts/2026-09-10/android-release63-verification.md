# Android release candidate 63 verification

Final disposition: **published** as Android 0.4.14 preview 1/code 63 on 10September2026,
with owner hardware acceptance and anonymous download verification recorded in
[the final platform ledger](platform-release-verification.md). This supersedes
the earlier unpublished/local 62/handover-pending checkpoint. Current assignments
and issue-specific tests live in the [maintenance board](../../MAINTENANCE-BOARD.md).

The sections below retain the staged candidate and later acceptance evidence.
Intermediate package/notices identities are historical where the final ledger
supersedes them; they are not instructions to repeat completed release work.

## Exact artifacts

- Version: `0.4.14-android-preview.1`, code 63, `dev.kartpad.android`.
- Source: merged `6a2dffc30f8f0d55a7eb928c614c88e054240d14`, clean at build.
- Reviewed premerge source: `8336948b88641e75e2a3434ea173de942eb866f7`.
  The two Git trees are identical; PR #174 merged after source review and runtime
  smoke checks. No application code changed for final packaging.
- Final APK SHA-256:
  `4e27897b9bb89e7b24fbe0b2e3dc66fae4efd549edaadf2f748ca22f376d87ff`.
  Size: 110,355,865 bytes.
- Final private AAB SHA-256:
  `7d49f7dd7706b1b1f89fbaa4933f7ae4ac4a79c42ab96c567023b5646238f273`.
- Existing public certificate SHA-256:
  `c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.
- Stripped `libmain.so` SHA-256:
  `1502c10b591809d3117b1e057d2273b53ec81fe76bf87d06d31dd1114286cf42`.
- Premerge tested APK SHA-256:
  `cc0eca11878a57c1e2664f0c778492383894a09aee06fd97c3dbc21ebe2cc80e`.
  Final APK ZIP payload differs only in `assets/kartpad-build.json`; all native
  libraries, DEX, resources and game payload are identical.
- Final APK repeated derivation is byte-identical. The companion ZIP contains
  28 allowlisted notices/provenance entries; SHA-256
  `da5d5ce9eb8095f654645146ff408fade531d4c174c9df7cdf9ef789fac315c0`.
  Both distribution files verify against `SHA256SUMS`. Packaging documentation
  source is `37ce92d`; exact native/source/APK/AAB allowlists remain enforced.

The native configuration is RelWithDebInfo with `-O2 -DNDEBUG`. Disassembly of
the linked overlap policy is `mov w0, #1; ret`; its debug-property string is
absent from the APK native library. Actual emulator logs contain overlap encode
phase reports while the debug property is empty. This establishes release-path
activation, not a new matched public-build performance percentage.

## Checks and observations

- Fresh Android preparation and five extracted-source bounds/ownership/mapping/
  concurrency harnesses passed ASan/UBSan/TSan as applicable. These are not a
  sanitizer run of the complete game engine.
- 66 Android Python contracts passed. Executable Kotlin report/evidence and
  bounded-export checks passed. Retro storage regression covered 13 cases plus
  pipeline/content/space checks. Release compile and lintVital passed.
- AAB/APK content, signature and alignment audits passed unchanged. The initial
  AAB marker-count audit rejected reused stripped DiscIO input because its symbol
  metadata was absent. The original unstripped dependency restored that metadata;
  its stripped library exactly matches the existing public library. No key leak
  or runtime dependency change was established, and the audit was not weakened.
- Isolated API 36 ARM64 software-GPU emulator, 1280x720, 1x/4:3, validation off,
  audio disabled. Private owned-game fixtures were seeded directly; this is not
  an import/install-transaction test. No owner saves or identities were copied.
- Exact public28 to premerge63 update used `install -r`: all 19 protected fixture
  files identical. Final merged63 update also used `install -r`: all 25 protected
  files identical, including the newly created Retro redirected-save fixture.
  No uninstall, data clear or downgrade occurred.
- Original: 50cc, Mario, Standard Kart M, Automatic, Luigi Circuit. Intro,
  countdown, acceleration and steering worked. Home return, Report a Problem
  return and live 1440x900/1280x720 resize kept the same game process. Game time
  advanced beyond six minutes, much of it parked at a wall; no completed lap,
  race or sustained driven-performance benchmark is claimed.
- Retro: Mario, Standard Kart M, Hybrid, SNES Mario Circuit 1. Actual race intro
  says 200cc, correcting an earlier inferred 100cc label. Countdown, acceleration,
  steering and same-process Home return worked. A fresh KartPad license visibly
  reloaded after full app restart. This is not saved cup/awards acceptance.
- Captured Original console: 203 overlap reports; Retro: 133. No renderer
  error/fatal lines in those captures; crash buffer empty. Counts are diagnostic
  windows, not a frame-rate benchmark or proof of no unlogged defect.
- Real public-APK report flow blocked sharing without an evidence choice, then
  blocked an unreviewed selected text file. Review confirmation opened the share
  sheet with one harmless test file. No recipient was chosen. GitHub manual-
  attachment confirmation was inspected and canceled; no report was submitted.
  A stale inline validation message remained after review selection (cosmetic).

## Rejected inferences

Single title presses separated by long tool/model delays can overlap the attract
movie. A bounded adjacent-press test reached title, retained license and main.
Earlier stale screenshots do not establish lost native input or a controller
fix. A report-screen scroll accidentally invoked the Android Home gesture;
process/crash checks and successful return distinguish it from an app crash.
The previous local 62 title trial overlapped owner gameplay and remains rejected.

The historical hashing improvement is not a new public gain. Passing Pixel
vertex probes do not resolve affected Adreno geometry. Save preservation is not
an FPS change or proof that ordinary-exit progress loss is fixed. See the
[release notes](../../releases/v0.4.14-android-preview.1.md) for scene-specific
numbers and the remaining 2.580–2.732-second menu transitions.

## Release decision and source delivery

On 10 September 2026 the owner confirmed the Android hardware checks were
complete and explicitly authorized publication with the Apple updates. The
installed non-debuggable code-63 private-signer APK has all 155 ZIP payload
entries byte-identical to the public APK; only the signing block differs.
The in-place update retained the Android app ID and recognized both existing
game installations. A fresh 409-file state backup was retained before updating.
The final non-debuggable app disallows run-as, so a full post-update private-file
hash comparison is not claimed. Owner acceptance does not invent separate
completed-cup, audio, online or affected-Adreno results.

The earlier repository-only archive has been superseded by actual upstream,
dependency, translator and modified-runtime source delivery. Fresh replay
reproduces the candidate's Original/Retro generated software and source graph;
see [reconstruction](android-source-reconstruction.md) and
[source delivery](android-source-delivery.md). No unexplained handwritten
translation changes remain. Packaging and hosted download verification are
recorded separately from the compiled application source.

Raw captures, logs, game fixtures, private AAB and signing material remain in
ignored local `build/release-candidate` and `build/release-final` directories.
Only sanitized measurements and artifact fingerprints belong in this record.
