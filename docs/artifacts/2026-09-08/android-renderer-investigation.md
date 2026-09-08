# Android geometry investigation and synthetic probe

September 8, 2026. Issues #102 and #104 remain open. No renderer fix or new
playable KartPad APK/IPA is established by this investigation.

## New evidence

[#102's reply](https://github.com/chrissotraidis/kartpad/issues/102#issuecomment-5576923553)
identifies Vulkan, Adreno 840, Qualcomm driver branch 512.842.19, build 21,
and Retro Rewind 6.12.7. Its runtime line shows 1x, widescreen off, fit/4:3.
The reporter tried both folded/unfolded states and all resolution/aspect
settings. Corruption therefore is not confined to Fill Screen. Original versus
Retro Rewind and errors after startup still need clarification. The earlier
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

The next useful evidence is an affected-device probe result. A mismatch narrows
which helper/layout to isolate; a pass means the remaining draw stream, shader
stages, resource lifetime and driver interaction still need investigation.
