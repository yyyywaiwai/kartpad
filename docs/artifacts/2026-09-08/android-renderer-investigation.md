# Android geometry investigation and synthetic probe

September 8, 2026. Issues #102 and #104 remain open. No renderer fix or new
playable KartPad APK/IPA is established by this investigation.

## New evidence

[#102's reply](https://github.com/chrissotraidis/kartpad/issues/102#issuecomment-5576923553)
identifies Vulkan, Adreno 840, Qualcomm driver branch 512.842.19, build 21,
and Retro Rewind 6.12.7. Its runtime line shows 1x, widescreen off, fit/4:3.
The reporter tried both folded/unfolded states and all resolution/aspect
settings. Corruption therefore is not confined to Fill Screen. A [follow-up](https://github.com/chrissotraidis/kartpad/issues/102#issuecomment-5577732200)
confirms identical corruption in Original, no logged WebGPU/pipeline/device-loss
errors, reported 60 FPS, and all four synthetic checks passing on this Adreno. The earlier
S25+ comment does not establish that its adapter/driver matches the Fold.

## Source review

- Aurora's storage/uniform allocation uses device-reported alignment limits.
  The Fold's 256/64-byte values alone do not establish a defect.
- The release renderer enables `skip_validation` and `disable_robustness`.
  Missing validation errors in its logs cannot establish valid buffer use.
- Packed attributes are decoded in generated WGSL. Matrix arrays and offsets
  use a compact uniform layout. These are useful isolation targets, but no
  concrete arithmetic/layout defect was demonstrated by source inspection.
- The pinned Dawn source already contains Qualcomm workarounds, including
  passing matrices by pointer. No broad driver workaround or dependency
  upgrade was applied speculatively.

## Probe and evidence boundaries

[Source and build instructions](../../../tools/renderer-probe/README.md).
The probe extracts the actual pinned Aurora helper functions and compares
synthetic GPU readbacks to independent CPU expectations. Four variants cover
scalar/vector-packed uniform arrays with bounds protection disabled/enabled;
WebGPU validation is enabled throughout. This is a compute-stage test, not
an actual GX vertex/fragment, texture, presentation, or gameplay replay.

Extracted helper SHA-256:
`9bda5e7e86d65a0cf5875a036427f9f958da3265978664f555dbdbd5f3294813`.

- Apple M3 Max / Metal: all four variants pass, 4,096 values each.
- Physical Pixel 9 Pro XL / Mali-G715 Vulkan: all four variants pass using
  the Android command-line target compiled from the same probe. The adapter
  reports uniform alignment 16 and storage alignment 64. This weakens an
  alignment-value-only explanation; it does not test the affected Adreno.
- Negative control: deliberately adding one to the shader's byte result causes
  256 mismatches in each of the four variants and a nonzero CLI exit. This
  checks that the GPU/CPU comparison actually detects wrong results.
- Disposable API 36 emulator with host Vulkan: the non-debuggable, release-signed
  APK completes all four variants; Run and Share Results work. The sharesheet
  contains the full result text; no destination was selected or message sent.
- The pinned Dawn aborts in device-toggle setup on SwiftShader. The probe now
  rejects software adapters before device creation instead of calling that
  path or reporting a pass. This is a probe limitation, not #102's root cause.
- Android release build, Android lint, source pins, and patch hunk checks pass.
  No KartPad game code, save/identity storage, or runtime settings were changed.

The probe has a separate package (`dev.kartpad.rendererprobe`), no permissions,
and no game-data inputs. A separate candidate was installed on the Pixel;
KartPad itself was not installed over, uninstalled, cleared, or migrated.
The physical phone remained locked, so APK UI acceptance is from the emulator;
the Pixel result is the native command-line probe, not a gameplay claim.

The affected Adreno passes all 16,384 comparisons. The next investigation is
on our side: actual draw streams, vertex/fragment stages, texture handling and
resource lifetime. No repeat settings sweep or general logs are needed from
#102 at this stage; the compute pass does not establish gameplay correctness.

## Published diagnostic

[Renderer Check 0.1.0](https://github.com/chrissotraidis/kartpad/releases/tag/renderer-probe-v0.1.0)
is a prerelease, not GitHub's latest game release. PR #109 merged to
`2774827a77695afe141e7b3c15b969075fdc7771`; the annotated diagnostic tag points
to that exact source. Rebuilt from merged source; two release-signing outputs
match byte-for-byte. The published APK's Java, JNI library and manifest match
the emulator-tested candidate exactly (only notice formatting changed).

- APK: `KartPad-Renderer-Check-0.1.0-arm64.apk`, 14,722,620 bytes.
- SHA-256: `2bc8f507bc0646088d1ec350d77e05e38d6bd3d521ec846e130973fc8c53f0db`.
- JNI library SHA-256: `3484a5d946f28efb0cad8c65c19a2acace7174798e2828690d0a33c175d16292`.
- Public release certificate SHA-256:
  `c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.

Only the APK, source/dependency provenance JSON and checksums were uploaded.
Fresh anonymous downloads match all three local artifacts byte-for-byte; the
downloaded APK passes the standalone audit (package, no permissions,
non-debuggable, signer, exact notice assets, ARM64/16 KiB, content scan).
The verified download also updates the separate probe package on the Pixel;
KartPad itself is untouched. The latest game release remains `v0.4.11`.

Reporters in #102 and #104 received the link and a Run/Share request. #102
returned the passing Adreno results above; #104 is still pending. No issue was closed and no playable APK/IPA
was released by this investigation.

## Graphics-stage follow-up in source 0.2.0

After #102's passing compute result, the separate diagnostic now adds four
indexed-draw variants alongside the original four compute variants. Each draw
variant compares 4,096 channel values over four queued frames, exercising packed
vertex indices, signed positions, the current 80-byte uniform prefix, 20 indexed
position matrices, dynamic uniform offsets, RGBA8 texture loads and shared
buffer/texture updates. The detailed scope is in the probe README.

- Mac M3 Max / Metal: all eight variants pass, 32,768 comparisons total.
- API 36 ARM64 emulator / host Vulkan: the release-signed 0.2.0 candidate passes
  all eight variants. Run and Share Results work; the sharesheet includes all
  results and no destination was selected.
- Negative control: a private copy deliberately flips one red-channel bit in
  the fragment shader. All four draw variants fail with 1,024 mismatches each;
  compute variants still pass, and the CLI exits 1.
- Android CLI and release APK compile. Standalone APK audit passes. The physical
  Pixel disconnected before this expanded probe could be run; the earlier
  Pixel result applies only to version 0.1.0's compute tests.

These are synthetic graphics stages, not a replay of GX-generated game shaders,
compressed textures, actual staging-buffer use, multithreaded encoding or
presentation. No renderer correction is claimed. Version 0.2.0 publication and
affected-device results remain pending at this source checkpoint.

## Version 0.2.0 publication and additional replies

[Published diagnostic](https://github.com/chrissotraidis/kartpad/releases/tag/renderer-probe-v0.2.0),
source `d07d819e912ce2c8af730a3ddc1e965f7b659284`. APK is 14,739,004 bytes,
SHA-256 `1d37bed8c7f4178ecbd2815fdcb537271df29fcf3c9222d0b61f978518578500`.
The merged-source rebuild/sign matches the emulator-tested candidate exactly.
Fresh anonymous APK/provenance/checksum downloads match their local artifacts;
the downloaded APK passes the standalone audit. This remains a diagnostic
prerelease, not the latest game release.

Two further version-0.1.0 results arrived: Adreno 750 driver 512.762.39 in
[#102](https://github.com/chrissotraidis/kartpad/issues/102#issuecomment-5577877999)
and 512.762.41 in
[#104](https://github.com/chrissotraidis/kartpad/issues/104#issuecomment-5578103113).
Both pass all four compute checks, with uniform/storage alignment 256/64.
Both threads received the expanded diagnostic, with its additional scope and
limitations explained. No game saves or general private logs were requested.

## Build-23 Fold comparison and Turnip question

At 07:45 UTC, [#102 confirmed](https://github.com/chrissotraidis/kartpad/issues/102#issuecomment-5581255824)
actual-game validation/robustness enabled, no crash, and unchanged corruption
compared with validation off. The supplied steady-state interval presents near
60 FPS with no queued pipelines. This is not geometry correctness or a
whole-session performance result. No validation failure appears in the excerpt.
The dropped SetViewport line follows input suspension/backgrounding in that
sequence; it does not establish the cause of earlier visible corruption.
Further repeated off/on runs or full logs are not needed now. A failing draw,
its character transforms/generated shaders, and vendor behavior remain targets.

The #104 reporter reimported without resolving corruption and asked about
Turnip. KartPad has no custom-driver loader or driver ZIP picker. An alternate
driver comparison is a possible future investigation, not a present workaround
or verified correction. The reporter received a Portuguese explanation and
clarification that each `base_...` directory is a separate run's console log.
