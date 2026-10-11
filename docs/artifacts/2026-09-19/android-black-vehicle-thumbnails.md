# Android black vehicle thumbnails — September 20, 2026

## Report and acceptance boundary

Owner screenshots at 10:40:33 and 10:42:44 show enabled vehicle thumbnails as
black silhouettes in the installed Android 0.5.0/code134 candidate. Some
thumbnails and the selected 3D vehicle render normally. This blocks release.
Original captures remain private in Downloads; no game images are committed.

On the unchanged code134 installation, re-entering the Retro Rewind offline
100cc Yoshi vehicle menu after compilation had warmed showed all twelve
thumbnails colored correctly. No game assets, saves, settings or cache were
replaced to obtain that observation. This supports a transient rendering/bake
failure rather than a missing asset file. It does not by itself identify which
submission produced each original black thumbnail; there is no GPU trace of
those original frames.

## Independently reproduced renderer defects

1. **New staging-capacity submission omitted ordinary-EFB protection.**
   `split_staging_batch` waited for unfinished pipelines only when the renderer
   was inside an explicit offscreen target. The game can instead render into
   the ordinary EFB and issue `GXCopyTex` after a capacity split. The already
   submitted prefix could skip draws before that later copy declared its
   persistent destination. Waiting at the copy was then too late. This defect
   is in Android `ee05ec7`, introduced by the new capacity handling; the other
   maintained runtimes had the same condition.
2. **Repeated-address copies were incorrectly considered disposable.**
   `GXCopyTex` treated a destination written in the same or previous frame as
   recurring, allowing missing pipelines. Address reuse does not prove a later
   redraw. The final write can become a retained thumbnail; depth copies were
   also excluded from the required-pipeline path. This heuristic predates the
   new capacity changes. Bounded prewarming makes correctness with genuinely
   unfinished demand shaders especially important.

These defects affect generated textures, potentially including other cached
menu images, minimaps and effects. They do not establish corruption of the
source assets or prove that every unrelated GPU report has the same cause.

## Correction

- All capacity-submitted prefixes require their draw pipelines, including the
  ordinary EFB. The next guest command can copy those pixels into a texture.
- Every `GXCopyTex` requires complete source draws, regardless of destination
  reuse or depth/color format. Required readiness is monotonic for a pass.
- Display presentation can still skip unfinished shaders. No global shader
  skipping switch was disabled and no game data/cache reset was added.
- Identical corrections are maintained in Android, iOS, macOS and tvOS. A first
  use may wait for compilation instead of permanently retaining incomplete
  pixels. This is a correctness repair, not a universal FPS improvement claim.

## Verification

The ROM-free `aurora_batch_probe` links the actual maintained renderer. Its
new modes use real FIFO geometry, real `GXCopyTex`, and GPU tiled-RGBA readback.
A test-only compiler gate deliberately prevents a cold shader from completing
until a required draw waits for it. The gate is linked only with `--copy-gate`;
there is no hook or delay in application binaries. Dawn validation is enabled.

- Old code: consecutive-destination copy fails its independently expected
  pixels (exit 4).
- Old code: ordinary-EFB capacity prefix followed by copy fails its expected
  pixels (exit 4).
- Fixed code: both cases pass (exit 0), with separate fresh private caches.
- Fixed code: full existing renderer suite passes **with shader skipping
  enabled**, covering resolve/snapshot, downsample/readback, forced capacity,
  offscreen preservation, invalidated arrays, interpolation and frame worker.
  Earlier suite runs disabled skipping, leaving this important gap.

Machine-readable outcomes: [GPU comparison](android-thumbnail-gpu-comparison.json).
Private executables, source overrides and logs are retained under
`work/android-thumbnails-20260920/` in the integration worktree.

Reproduction from the prepared maintained Mac build:

```sh
python3 prototypes/stabilization/build-aurora-probe.py \
  build/stabilization-20260919/macos-build work/thumbnail-probe/probe \
  --validation --copy-gate
work/thumbnail-probe/probe work/thumbnail-probe/fresh-copy --copy-only
work/thumbnail-probe/probe work/thumbnail-probe/fresh-capacity --capacity-copy
work/thumbnail-probe/probe work/thumbnail-probe/fresh-full
```

Use a new cache directory for each cold-shader case. This is actual Metal
renderer evidence, not a substitute for Vulkan first-entry acceptance on the
phone. Code135 is now installed in place with exact APK readback verified.
Its first post-update Retro Rewind offline 100cc Yoshi menu shows all twelve
vehicle thumbnails colored. No cache reset was used. Original-mode and full
race checks remain pending. Apple build59 packages contain the same correction
but have not replaced the currently installed iPad build58. All three CI checks
and four-platform staging/readback sanitizer regressions pass.

[Current artifact identities and acceptance](release-050-code135-build59.json).
