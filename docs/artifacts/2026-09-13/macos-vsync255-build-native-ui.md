# macOS VSync candidate: full builds and native settings verification

2026-09-13. Follow-up for draft PR #255 and issue #250. No release was published and no tearing or physical pacing result is claimed.

## Source and build identity

Started with exact PR head `502e31a`. A fresh source tree was prepared from the pinned runtime using its complete macOS patch sequence, then configured with the existing PR #254 translation and dependency source caches. Separate source/build outputs were used; no dependency build outputs or owner checkout were modified. Original (`WiiCompiled`), Retro Rewind (`RetroRewind`), and the dual launcher (`KartPadDual`) all compiled and linked successfully (1018 Ninja steps).

Native UI validation exposed a compact-window regression: the Graphics document grew to 795 pixels to hold VSync, but both initial/tab-change scroll paths still used a fixed 740-pixel height. The real native settings harness failed its document-top visibility assertion. The two paths now use the actual document height. All three affected native shells were rebuilt and linked after this correction. Source commit: `cdeb4a4923f157e95906ac518e94c084c2079622`.

The standalone Retro package audit also incorrectly required selectors/preferences that the shell compiles only for the dual launcher. The audit now skips those three dual-only markers for both standalone products; every other audit check remains active. This is an audit scope correction, not a game runtime change.

## Checks completed

- Fresh source preparation and full Original, Retro Rewind and dual native builds with the real Dawn headers/libraries.
- All three corrected local packages passed the package audit: arm64 identity, deployment target, native shell contracts, bundled dependency closure, private/writable-state exclusions, signature/entitlement checks and resources.
- `test-macos-vsync.py` passed on the newly prepared source: real mode selector capability cases and real config persistence/default/malformed/error behavior.
- `test-macos-settings-runtime.py` passed on the newly prepared source: existing graphics/audio reload behavior.
- `test-macos-vsync-ui.sh` passed: actual AppKit settings implementation and config parser, actual checkbox `performClick:` and adjacent control actions, failed-save feedback, close/reopen, second-process persistence, compact-window tab scrolling and row visibility/non-overlap. The test failed before the scroll correction and passed afterward.
- A capture of the harness's actual native window was inspected: the VSync row is legible and separated, and the saved/restart-required status is visible. This is native UI evidence, not an image mockup.

The UI harness deliberately replaces controller/backend entry points and bypasses the game startup path, Mii manager and user-defaults code. It asserts the portable test root and `UserData` path before opening any UI. All test preferences are temporary isolated files. This validates the actual settings page and actions, not an integrated running game or an applied Metal presentation mode.

## Local package identity

Each local package fingerprint names source commit `cdeb4a4923f157e95906ac518e94c084c2079622`. These retain the existing 0.4.17/build-39 package metadata solely to exercise the package contract; their names and fingerprints distinguish them from public build 39. They have not been installed over an existing app or published.

| Product | Local app | Packaged unsigned runtime SHA-256 |
| --- | --- | --- |
| Original | `build/VSync-verified-Original.app` | `489689429b1f4b66be8683893b04b86afa5709b3edc7cb10f2b72a3e568a8475` |
| Retro Rewind | `build/VSync-verified-Retro.app` | `5f4b72b78dd9380fa4ecfffaf558341184f590efd7d08110694091c0b5681efd` |
| Dual | `build/VSync-verified-Dual.app` | `79af51f26086bd6adc346cba86067f11ed08b0405305fff16a04c5f17bf35b84` |

## Remaining acceptance and isolation boundary

No full game app was launched. Prelaunch inspection found that the shared Mii manager's production `SupportRoot()` still resolves the owner's normal Application Support directory, and startup calls `KartPadApplyPendingMiiDatabase()` before game-data validation. A portable marker and unique bundle ID alone would therefore not isolate that launch. This separate path was not changed in the VSync PR; the dedicated settings harness safely bypasses it.

Before a public build or a tearing-fix claim, complete an independently proven isolated full-app startup, confirm the requested versus selected Metal mode after restart, then compare FIFO off/on on physical hardware. Check game time against wall time, audio, queue drops, interpolation above display refresh, window resize/minimize/fullscreen and monitor transitions. Use phone-camera evidence for physical tearing. Issue #250 remains open.

Local evidence lives under the candidate worktree's `build/`: `preparation-502e31a.log`, `configure-502e31a.log`, `full-502e31a.log`, `full-scroll-corrected.log`, `audit-verified-{original,retro,dual}.log`, `native-ui-final.log`, and `native-ui-final/settings-vsync.png`. Full build inputs and game-derived artifacts stay local.
