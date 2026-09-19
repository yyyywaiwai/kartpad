# Issue #193: actual character-shader comparison candidate

This Android-only diagnostic targets pipeline recipes `58866e32bada1f83` and
`33c5ff18d5c180e0`, recovered from the public code85 pipeline cache and named in
reporter logs. It is not a confirmed Adreno fix or a performance improvement.

The candidate retains each vertex's matrix selection. The literal variant
replaces dynamic position/normal array indexing with a switch whose cases use
literal indices: all 20 position slots and all 10 normal slots. Projection,
lighting, textures, vertex fetches, uniforms and other shader state remain
identical. Invalid indices use a zero fallback; no equivalence claim is made
for out-of-range inputs. Other pipeline recipes are untouched.

## Process-start controls

`KARTPAD_RENDERER_CONST_PNMTX` is read once per game process:

- Unset or invalid: normal rendering, unchanged shader and merge behavior.
- `0`: dynamic control, diagnostic draw merging disabled.
- `1`: literal variant for the two eligible target pipelines; the same merge guard.

Use dynamic → literal → dynamic, restarting the game process between changes.
Both experimental modes disable merging equally so an early merged-draw return
cannot bypass selected pipeline evidence. Do not compare their FPS against
normal mode. `KartPadPNMTX draw_binding` reports original pipeline, bound variant
pipeline, shader hash and vertex count for the first eight draws per target.
No matching draw-binding evidence means the experiment did not reach a target.

The shader flag occupies a previously zero padding bit. PipelineConfig remains
2768 bytes, and off-mode recipes preserve their original hashes. Variant shaders
and pipelines therefore receive distinct cache identities without clearing
normal caches or any user data.

## Completed local checks

- Both actual dynamic WGSL outputs are byte-identical to public85.
- `scripts/test-android-targeted-pnmtx.py` verifies full literal palette coverage
  and that reversing just the two matrix operations restores the entire original
  WGSL. Wrong-matrix and unrelated-shader mutations are rejected.
- All four actual shaders pass Dawn/Tint compilation-info validation on host
  Metal with zero errors. This is not Adreno/Vulkan compilation or gameplay proof.
- NDK29 compiles the changed shader and command-processor translation units.
- Native relink succeeds after verifying every inherited code85 link-input hash.

Local build records retain generated shaders, the build recipe, and a native
receipt recording input hashes and the link command. Stripped `libmain.so` SHA256 is
`8611660ddae96cc33748b15938be1bad4c52f383d2d2f76b827a1408ea208347`.

No local SPIR-V CLI was available, so retention of literal accesses in Vulkan
backend output remains unverified. The next acceptance is matching target
binding logs plus the affected reporter's same character/scene comparison.
A positive result warrants a narrower production change and unaffected-device
checks before any general compatibility claim or issue closure.
