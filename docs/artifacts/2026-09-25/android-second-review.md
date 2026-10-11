# Android second review — 25 September 2026

Scope: Android only. Evidence: public code135 (root `a2f41d5`, Android runtime
`295f450`), private code218 (root `b7560a6`/`397a3af`, runtime `27074c2`),
live GitHub issues and their attachments, and the private Pixel build-218 Retro
capture. Both builds link the same Dawn (`b0fd045`, package
`c6b4efde…`). Nothing was installed, published or requested from players.

## Issue and evidence matrix

| Issue | Device / build / evidence | 135 → 218 disposition |
|---|---|---|
| #321 | ROG Phone 7S, Adreno 740, driver 512.676 (10/06/22), Android 13, code135. Two native exits 2 s after launch: SIGSEGV and SIGABRT, identical libmain path. | **Unresolved in 218; source-corrected by patch 1.** Crash is inside `vkCmdEndDebugUtilsLabelEXT`, reached from the overlay's `PopDebugGroup()`. 218 has the same overlay code and Dawn. |
| #320 | Huawei STK-LX3 (Kirin 710, Mali-G51), Android 10/API 29, code135. Game CPU 20 ms/frame in menus, 41–158 ms in races; FPS 2–14 at 0.5×; no pipeline workers; later `VK_ERROR_DEVICE_LOST` after backgrounding. | Performance: **source-corrected in part by patch 2**; no 135→218 change applies (Performance Hint needs API 33). CPU cost remains large on this class of phone. Device loss after background: **unresolved**, separate subcase. |
| #313 | Honor X7c, 0.5.0, ~15 FPS in races; no log. | Plausibly helped by 218 CPU work; API level unknown, so patch 2 may or may not apply. Not verified. |
| #195 | S25 Ultra, API 36: VS 41 FPS, Time Trials 60. | Plausibly helped: 218 reports game-thread work to the Performance Hint API (API 33+) and adds FIFO/GX CPU reductions. Not measured on this phone. |
| #316, #308, #104, #211 | Adreno character-vertex displacement; #316 screenshot confirms model corruption at 1×/Normal. | **Unresolved.** No 135→218 commit targets vertex/skinning; upstream `452b478` fixes depth z-fighting, not displacement. Card remains blocked on the prepared character-draw comparison build. |
| #319 | Retroid Pocket 6 controller, auto-accelerate. | **Unresolved feature gap.** 218 only relabels the setting "Touch auto-accelerate"; the latch lives in `KartPadOverlayView.kt` and no controller path exists in the app or runtime. |
| #322 | iPad | Out of Android scope. |

## Finding 1 — #321 crash is a debug-label call, not shader compilation

The code135 library is stripped, but its exported Dawn symbols name the crashing
thread: `NativeQueueSubmit → QueueBase::APISubmit → vulkan::Queue::SubmitImpl →
CommandBuffer::RecordCommands → RecordRenderPass → vulkan.adreno.so`. The call
site loads `fn+0x3b20` after checking instance extension index 8
(`InstanceExt::DebugUtils`) and passes only the command buffer. Its neighbours
`+0x3b18` and `+0x3b28` both build `VK_STRUCTURE_TYPE_DEBUG_UTILS_LABEL_EXT`
(`0x3b9cbe02`), matching Dawn's Begin/End/Insert order, so the faulting call is
`vkCmdEndDebugUtilsLabelEXT`. Other threads were in `CreateRenderPipeline` and the
driver's LLVM compiler at the time; that is concurrent work, not the fault.

Android release builds do not define `AURORA_GFX_DEBUG_GROUPS`, and Dawn never
pushes groups internally. The only in-pass group is the ImGui overlay's
unconditional `PushDebugGroup("Aurora: Dear Imgui")`/`PopDebugGroup()`, which runs
on every presented frame (the reporter's config has `showFps=1`, and the pair is
recorded even when the draw list is empty). This differs from #301/#303, where
the debug-label entry points were missing entirely.

## Finding 2 — physical Android 9/10 phones never get pipeline workers

`pipeline_workers_supported()` returns false for API ≤ 29. The archived bring-up
record limits that decision to the API 29 **emulator's** Goldfish Vulkan
deadlock ("not a physical API 29 or vendor-GPU claim"). On phones it forces every
new pipeline onto the frame path. #320's log has no "Enabled N priority pipeline
compilation workers" line, its queue is always zero, and its worst interval
(158 ms game CPU/present, 2.2 FPS) is the one in which pipelines created rose
218 → 404. The 24 September deep review read "zero queued pipelines" as
excluding pipelines; with no workers, nothing can queue, so that inference is
withdrawn. Game CPU remains high between compile bursts (80–113 ms), so this is
one cause of the collapse, not the whole low-end gap.

## Finding 3 — Pixel waits are first-use compiles and a blocking TCP receive

Each in-capture persistent wait (106.558 ms, 128.542 ms) coincides with exactly
one newly created pipeline (682 → 684) and a matching presentation-lateness
maximum (123 ms, 131 ms). They are correct waits for a persistent texture pass;
the metric does not say which recipe missed, so patch 3 records its stable hash.

The 1,014 ms `KartPadNetStall` is `IOCTLV_SO_RECVFROM` on a logically blocking TCP
socket. Both sync and async `IOS_Ioctlv` fall through to the direct handler,
which calls `poll()` for up to 5,000 ms on the emulation thread and freezes every
guest thread plus frame production. `remaining=25` from a budget of 32 shows it
was the seventh ≥100 ms stall of that process; the other six predate the retained
logs. `network_deferred.cpp` already parks blocking `SO_CONNECT`/`SO_POLL`
callers and probes them with zero-timeout polls from the scheduler pump. The
correct follow-up is the same shape for receive: try `recvfrom` at submission,
park only would-block blocking-stream calls with the existing 5,000 ms deadline,
probe readability per pump, perform the receive and guest write on the emulation
thread, and return the unchanged would-block result on expiry. It needs a pump
harness and a local-WFC login/race run before release; no patch is supplied.

## Patches for integration

Android runtime branch `codex/android-review-20260925` (base `27074c2`, worktree
`~/.codex/worktrees/kartpad-android-review-20260925-runtime`):

1. `420b828` Gate the overlay debug group behind `AURORA_GFX_DEBUG_GROUPS`
   (`aurora-main/lib/imgui.cpp`). The original and patched files compiled with
   the exact release NDK command; the original object imports
   `wgpuRenderPassEncoderPush/PopDebugGroup`, the patched object imports neither.
   No rendering change: labels are diagnostic only.
2. `c1c9cff` Keep pipeline workers on physical API ≤ 29; retain the synchronous
   fallback for `ro.hardware` `ranchu`/`goldfish`, matching the app's existing
   emulator check (`pipeline_cache.cpp`). Release-flag object compile passes.
   Risk: vendor Android 9/10 drivers now see concurrent pipeline creation, which
   API 30+ devices already do.
3. `c773537` Add `ref=0x…` to the existing rate-limited `KartPadPipelineWait`
   metric. No script parses that line.

Root branch `codex/android-second-review-20260925` (base `397a3af`) adds:

- `scripts/test-android-debug-labels.py [runtime]`: fails on `27074c2` at
  `imgui.cpp:218/220`; passes on the patch (6 gated calls, macro undefined).
- `scripts/test-android-pipeline-workers.py [runtime]`: runs the real gate over
  eight emulator/phone/API cases; `27074c2` fails the three physical API 28/29
  cases; the patch passes all eight.

Build implications: the Android runtime gitlink must move to the new branch and a
new APK be built. Apple runtimes are untouched; `imgui.cpp` and
`pipeline_cache.cpp` are not in the shared-parity set.

## Remaining gates

No patch has run in a packaged APK or on a device. #321 needs an Adreno 740 with
that driver (or reporter confirmation after a public build) before "fixed"; if
the crash persists without labels, the concurrent compiler threads become the
next suspect. Patch 2 needs a physical Android 9/10 gameplay check and an API 29
emulator regression boot. #320's device loss after backgrounding, the geometry
family and #319's controller design (a separate controller setting, default off,
so existing controller play is unchanged) remain open. Per owner instruction, no
retest is requested before a public APK exists.

## Stale or corrected claims

- 24 September deep review: #320 "zero queued pipelines" does not exclude
  pipeline cost (Finding 2).
- `android-code218-pixel.md`: #321 "attached driver stack requires analysis" is
  superseded by Finding 1; #320 is Mali-G51/API 29, not Adreno.
- `MAINTENANCE-BOARD.md` line 63 lists Auto-accelerate as "already implemented";
  it is touch-only (#319). Coordinator-owned records were not edited.
- The archived API 29 note ("fixed the stall") is correct for the emulator only.

Private evidence (not committed): `work/android-second-review-20260925/`
(attachments, compiled objects) in the stabilization worktree.

## Cross-report pass

All 20 diagnostic attachments on open and closed issues were re-read.

- **Build 218 carries the #321 path.** The unstripped 218 library (BuildID
  `8c2aab86`, `android/app/build/intermediates/cxx/RelWithDebInfo/422i1s3a`) shows
  `aurora::imgui::render` calling `wgpuRenderPassEncoderPushDebugGroup`,
  `ImGui_ImplWGPU_RenderDrawData` and `wgpuRenderPassEncoderPopDebugGroup`
  unconditionally. Keep that library; it symbolizes any 218 crash exactly.
- **#321's signature is unique.** The other native exits are different known
  failures: #216 (build 119, startup abort in KartPad code), #304 (PowerVR
  limit abort) and #137 (build 119, abort 25 s in). Patch 1 targets #321 only.
- **Patch 2 reaches one known reporter.** Only #320 is API ≤ 29 among the
  attachments; all others report API 31–36 and six or seven workers.
- **The blocking receive recurs in a public report.** #123 (Mali-G715, Retro
  online) logged three `socket_ioctlv command=12` stalls (112, 228, 110 ms) during
  NAS/GPCM login, beside an interval with a 2,222 ms worst frame. That interval
  also contains a 1,596-pipeline prewarm, so network is one contributor, not the
  whole freeze. The same log shows `OSSleepThread … scheduler could not switch
  away`; a deferred receive must fall back where parking is impossible, as
  deferred connect/poll already do.
- **The geometry blocker is stale.** The board's `adreno-geometry` card awaits
  delivery of the dynamic/literal character-draw comparison, but that comparison
  already ran: #193 (build 121) posted `KartPadPNMTX draw_binding` lines proving
  both `variant=literal` and `variant=dynamic` reached the targeted pipelines
  `58866e32…`/`33c5ff18…`, with corruption unchanged in every mode; #102 also
  reported no change. Matrix-index selection is excluded for those draws. Every
  affected GPU is Adreno (6xx #216, 7xx #104/#211, 8xx #102/#308/#316), while all
  Mali devices render characters correctly. The next discriminator should target
  vertex position fetch and decoding, not matrix indexing. No candidate was built.
- **Integration base is current.** `27074c2` is the published head of
  `origin/codex/upstream-android-20260922`, and PR #317's head is `397a3af`; both
  branches stack without conflict. Both changed runtime files also compile with
  the 25 September release configuration (`6d6p27d4`, debug groups undefined).

