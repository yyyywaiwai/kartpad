# macOS issue #250: VSync candidate and acceptance boundary

Status: 2026-09-13. The opt-in candidate is implemented, all three native products have built, and local packages passed audit. Actual native settings actions and layout passed an isolated harness. No public build was released, no game app was launched, and physical pacing/tearing acceptance remains open. See the [build and native UI follow-up](macos-vsync255-build-native-ui.md).

## Intake and integration identity

- [Issue #250](https://github.com/chrissotraidis/kartpad/issues/250): Mac mini M4, macOS Tahoe 26.4, KartPad 0.4.17 Mac build 39; reporter describes tearing after shader compilation and requests VSync.
- [Our existing response](https://github.com/chrissotraidis/kartpad/issues/250#issuecomment-5651006229) already requests monitor/refresh, window mode, phone-camera evidence, present-mode startup line, and interpolation comparison. No later reporter response was present at review. Do not repeat that request.
- [Issue #101](https://github.com/chrissotraidis/kartpad/issues/101) concerns iPhone Fill Screen distortion and projection/HUD comparisons. It is independent of this presentation setting.
- Public Mac build 39 source is `5079710`; the candidate starts from PR #254 correction head `d59b100`. Pinned Wiicompiled reference inspected: `1912292c804ff9b1b79938de89369ec4496f9fff`.
- PR #112 head reviewed for settings integration: `74fe75c8e7c4fdbb9ca68546ca683e5f4a803dc9`. It owns the native Graphics page. The candidate includes its PR #254 preparation corrections and adds one option to that page. No second ImGui settings panel is restored.

## Source findings

`aurora-main/lib/webgpu/gpu.cpp::best_present_mode()` chooses Immediate for Metal when supported, then FIFO. The unmodified `AuroraConfig` explicitly has no VSync field. The existing startup log reports the chosen mode.

`refresh_surface()` forces `resize_swapchain()` but preserves the cached `surfaceConfiguration.presentMode`. A settings reload followed only by a reconfigure request would therefore leave the old presentation mode active. Live changes also require the renderer-owned mutation path to drain the presenter and acquire surface ownership before renderer ownership; calling Dawn Configure from the AppKit settings action would violate that ownership.

The selector warns that FIFO can cap presentation and affect guest pacing. Current `enqueue_presentations()` drops stale queued jobs instead of blocking the producer, so that comment does not establish that the current guest necessarily slows down. FIFO still changes acquire/present blocking, queue drops and deadline behavior. These require measurement, especially with 120/180 FPS interpolation on a slower display. Surface mutation also waits for the presenter to become idle.

## Implemented startup candidate

Use a macOS-only, opt-in, restart-required setting first:

1. Persist `[video] vsync = false` (or true when selected) through the existing `RuntimeConfigFile::WriteSetting`/boolean parser, with missing or invalid values retaining the current off default. Preserve unrelated settings and user data.
2. Add one checkbox to PR #112's native Graphics page: “VSync — experimental (requires restart)”. Reuse its existing save-error handling and restart-required status pattern. Leave room in the scrollable page and verify no overlapping rows or lost controls. Show the saved preference; do not describe it as currently active until relaunch.
3. Carry the parsed preference into a zero-initialized Aurora startup configuration field before `aurora_initialize`. Apply the patch only in the macOS preparation path, leaving iOS/tvOS/Android source preparation unchanged. Rebuild all native consumers of the changed struct together.
4. When requested on Metal, choose FIFO from the surface capabilities; otherwise retain the existing selector. If the requested mode cannot be selected, log the fallback and requested-versus-selected state rather than claiming VSync is active. Keep the existing selected-mode startup log.
5. Do not modify live reload, interpolation targets, resolution limits, guest clocks, or presenter queue policy in this initial candidate. A later live-toggle implementation needs an explicit renderer-thread mode update before Configure, not just a pending reconfigure flag.

The restart boundary avoids additional presenter synchronization work. It does not remove the need to test FIFO itself. The source candidate implements this boundary with two macOS preparation patches, the native checkbox, and a native test runner. Local full builds and package audits subsequently passed, as did the isolated native settings harness. Those results support source review but do not establish acceptable physical Metal presentation behavior.

## Source validation completed

- Fresh source-only preparation from pinned Wiicompiled using the candidate macOS patch sequence passed, including PR #254 corrections. This checks patch application, not full game compilation.
- `python3 scripts/test-macos-vsync.py build/vsync-runtime-source` passed: actual selector function compiled against fake capabilities; actual runtime-config header exercised through separate processes using an isolated portable directory. Checked off/on, missing/malformed values, unrelated key preservation, failed writes, backend defaults and FIFO-unavailable fallback.
- Existing `test-macos-settings-runtime.py` passed on this prepared source. Existing native controller profiles/input harness passed with the candidate headers.
- `KartPadMacShell.mm`, including the actual native settings page, passed Objective-C++ syntax checking against the prepared headers and SDL headers (one existing nullability warning at `windowWillClose:nil`).
- `git diff --check` passed. No device or game data was read or changed.

## Follow-up validation

[Full builds and actual native settings verification](macos-vsync255-build-native-ui.md) subsequently passed for source correction `cdeb4a4`, including a compact-window scroll fix and all three local package audits. The dedicated native settings harness bypasses game startup and Mii handling; it does not prove integrated game launch or applied Metal presentation mode.

## Validation still required before release

- Independently proven isolated full-app startup and confirmation of requested-versus-selected Metal mode after restart. The normal Mii-manager path must not reach owner data during that test; see the follow-up isolation finding.
- Physical Mac comparison with the same build, course/camera, monitor and window mode: off/on, interpolation off first, then 120/180 where supported; 60 Hz and high refresh if available. Compare game time to wall time, audio continuity, queue-drop/presentation timing logs, resize, minimize/restore, fullscreen transitions and monitor changes.
- Use a phone-camera clip to assess physical tearing; software capture alone is insufficient. Keep #250 open until this evidence supports the outcome. If FIFO causes pacing regressions, keep the candidate unreleased and investigate the producer/presenter interaction before release.

Next action is review of the built candidate, then an independently isolated full-app launch and physical pacing/tearing comparison. Reporter details already requested remain useful for matching the eventual physical comparison, not a reason to repeat an unanswered comment.
