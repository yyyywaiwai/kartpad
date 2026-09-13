# PR #112 integration correction — 13 September 2026

Reviewed contributor head `74fe75c8e7c4fdbb9ca68546ca683e5f4a803dc9`, whose parents are the previously reviewed `a332264` and main `615225b`. GitHub reports the PR mergeable. This correction descends directly from that contributor merge and retains contributor attribution.

Fresh source preparation exposed two integration failures:

- The merge omitted the patch invocation before `aurora-viewport-interpolation.patch`; the shell would execute the non-executable patch file instead of applying it.
- `wiicompiled-macos-unified-settings.patch` still expected `DrawFpsOverlay` immediately after the removed graphics settings. Main now inserts an Android FPS-scale declaration there, so one of twelve hunks failed.

Restore the missing invocation and refresh the second patch's context while preserving the Android conditional declaration. No native UI or controller behavior is changed by these corrections.

## Validation

The exact preparation script's source-copy and patch section was executed against fresh disposable copies of the locally pinned upstream runtime and Aurora. All patches applied successfully after both corrections. This check stops before dependency downloads, translation, CMake, linking and packaging.

Passed against that fresh corrected source:

- Native controller/profile harness, including keyboard cancellation, Escape, close/reopen, focus loss, alternate character layouts, ISO/special keys, repeat/invalid handling, virtual SDL input and corrupt-profile preservation. Five existing harness/dependency warnings remain.
- Controller assignment and displacement, cached fallback, unassignment and player four.
- Native graphics/audio settings bridge, coalescing, fullscreen failure fallback and resolution limits.
- All 200 final PADStatus trigger output combinations.
- All eight `test_macos*.py` contract tests.
- Diff whitespace validation.

Contributor Original gameplay evidence is recorded at `a332264` in PR #112; the latest comment says ready to merge without giving a new Retro result. These host checks do not establish owner gameplay acceptance or Retro gameplay. No app was installed, published or relabelled as a public release, and no owner settings/saves were used. Two-player rendering issue #127 and VSync request #250 remain separate.

## Full dual build and isolated package follow-up

The full ARM64 macOS dual runtime then compiled and linked successfully from exact source `d59b100`, including the actual native Mac shell and Original/Retro generated graphs. The only subsequent commit changes this evidence record. This closes the fresh build/link requirement; it does not claim gameplay acceptance.

The existing owned translation was privately cloned; only absolute paths in its shard manifest were relocated. No translated game code was regenerated. The exact `prepare-g7-game-runtime.sh` completed with fresh `build/linked-source` and `build/linked-runtime`, locally cached Dawn/sse2neon and normal pinned dependencies. Existing duplicate-library linker warnings remain.

The local `build/PR112-local-audit.app` was packaged and passed the dual macOS package audit, strict signature verification and designated requirement. This private audit copy carries the source defaults 0.4.17/build 39; it is distinguished by commit/hashes and is not the published build 39. It was never launched or installed. The existing public artifact was unchanged.

- Worktree: `/private/tmp/kartpad-pr112-review-20260913`.
- Unsigned runtime: `build/linked-runtime/KartPadDual`.
- Unsigned executable SHA-256: `83c5c0c56036b9324272314e9be2f79d005be5ef3e92f2034716edfa857aa069`.
- Locally signed app executable SHA-256: `3afff31e8a2e497a564e1cc6b132160e38bb69394f19f8f8b774ff73489cc7db`.
- Audited bundle content hash: `5895673b91404ff8fa6d9dc05332776134a8f267f9e43c6ba0e584e07d0919e1`.
- Private logs: `build/full-dual-build.log`, `build/local-package.log`, `build/local-audit.log`.
