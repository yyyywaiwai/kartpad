# Separate split-screen interpolation history by viewport

9 September 2026, based on main `1e10db7`. Investigated while following
[macOS two-player rendering report #127](https://github.com/chrissotraidis/kartpad/issues/127),
which used experimental 120 FPS interpolation. This reproduces a renderer defect
with synthetic transforms; it does not yet establish the cause of the reporter's
entire visual failure or replace their requested same-scene comparison.

## Reproduced behavior

The exact and material-only draw-history keys omit the viewport. Two split-screen
cameras rendering the same geometry/material therefore enter the same matching
bucket, although their model-view matrices describe different camera spaces.
Spatial matching can assign the other player's previous transform. The indexed
matrix palette's sibling-sharing fallback also groups equal matrix bytes across
viewports, mixing or rejecting otherwise valid histories.

In the regression fixture, the top camera moves a transform from x=0 to x=90;
the bottom camera moves from x=100 to x=10. Current draws are submitted in reverse
order. Correct half-frame positions are bottom=55 and top=45. The unpatched
implementation instead produces 5 and 95. Both ordinary rigid draws and indexed
palettes fail, including the material fallback used when geometry changes.

`aurora-viewport-interpolation.patch` scopes exact matching, material matching and
palette sibling sharing to the logical guest viewport, including its depth
range. It preserves spatial matching within one camera and prevents a newly
introduced viewport from borrowing the old camera's history. Using logical
coordinates avoids making render scale part of the identity. GPU uniform layouts
and the requested presentation rate are unchanged.

The patch also supplies two missing test stubs (the local logger and a null SDL
window getter) required to build the pinned renderer test suite. Those stubs are
test-only. The fix is applied by the Mac and iOS preparation scripts; tvOS and
Android inherit the common iOS preparation stack. Work remains isolated from the
active Android optimization checkout. Android preparation passes, but no Android
runtime or performance acceptance is claimed.

## Validation

- Seven applicable new native regression cases pass on Apple Silicon macOS.
  One parameterized rigid-draw palette case is explicitly inapplicable/skipped.
- Five of those cases fail against the unpatched renderer, establishing negative
  controls for exact/material matching, camera changes and palette sibling
  sharing. The two within-camera reorder controls pass with either version.
- The new cases also pass with `-O3`, AddressSanitizer and UndefinedBehaviorSanitizer.
- The full GX suite runs 245 cases: patched 242 pass, one skip and two failures;
  unpatched 237 pass, one skip and seven failures. The two unchanged baseline
  failures are `FrameInterpolationContract.IndexedPaletteHistoryKeepsAbsoluteVertexSlots`
  (its zero-staged-range expectation disagrees with existing sibling staging)
  and `TevRegisterLivenessContract.PacksOneUniformWhenBothHalvesNeedInitialValue`.
  This is not a claim that the full suite is green.
- The corrected translation unit compiles with the physical iOS build command
  and with the corresponding iOS simulator and tvOS SDK/target substitutions.
  These are compilation checks, not full app builds or gameplay tests.
- Fresh iOS, tvOS and Android preparation completes. Their corrected interpolation
  source matches the tested Mac source: SHA-256
  `8492e7a101086167a1b1e1f39c49a765c2288b510a2afcb876957c748caf37ef`.
- The checked-in native CMake entry point configures successfully against a fresh
  prepared source. Tests contain only synthetic matrices and uniforms.

## Reproduction

After preparing a runtime, configure the isolated host tests with:

```sh
cmake -S tests/native/viewport_interpolation -B build/viewport-tests -G Ninja \
  -DKARTPAD_AURORA_SOURCE="$PWD/build/your-prepared-source/aurora-main" \
  -DAURORA_DAWN_PROVIDER=package -DAURORA_SDL3_PROVIDER=vendor \
  -DAURORA_DAWN_PACKAGE_URL="file://$PWD/build/dependency-cache/dawn-darwin-arm64-v20260603.191052.tar.gz" \
  -DAURORA_DAWN_PACKAGE_URL_HASH=SHA256=084ffd2ef500d614e443e3d494738272134628867bad3270d67ee8b0fb5f0838 \
  -DKARTPAD_TEST_SANITIZERS=ON
cmake --build build/viewport-tests --target gx_fifo_tests --parallel 3
build/viewport-tests/aurora-tests/gx_fifo_tests --gtest_filter='*AppleViewportInterpolation*'
```

Dependencies can be supplied from existing copies using CMake's
`FETCHCONTENT_SOURCE_DIR_*` options. To run the negative control, reverse only the
`lib/gx/frame_interpolation.cpp` hunks in a disposable source copy, retain the
test stubs, then rebuild and rerun. Never edit the pinned reference checkout.

## Remaining acceptance

The reporter's exact two-player scene still needs comparison on their Mac,
including 60 versus 120 FPS. This correction does not claim to resolve every
character/vehicle artifact, the iPhone Fill Screen report #101, or external-display
black video #100. No release or hardware app containing this viewport change has
been installed. The attached iPad's separate Metal-recovery candidate and its
data-preserving installation are recorded in the Metal-recovery workstream.
