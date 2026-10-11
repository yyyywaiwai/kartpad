# KartPad deep review and handoff — 24 September 2026 (expanded)

Audience: the next agent continuing KartPad Android/iOS work. Read the whole
file before acting. This is a source, log, profile and compiler review. Nothing
here was installed or played on a device, no public reply or release was made,
and no product source was changed. Measured numbers are labelled with their
source; everything else is marked as a hypothesis.

For the exact unpublished build status and acceptance limits, see
[Private build status](current-private-builds.md). The conclusions below are
review hypotheses unless tied to a named measurement or source check.

## 0. Plain-English summary

1. **The game thread is the largest measured CPU user in one Pixel battle.** It
   accounts for 80% of sampled app CPU. About a quarter of that thread is
   KartPad's own Wii-graphics front end (decoding the game's GX command stream
   and building draws), which real hardware and Dolphin do on a separate
   GPU-side thread. Another ~14% is emulating PowerPC floating-point status
   bits the game never reads. Other CPU cores sit mostly idle.
2. **The Adreno character corruption may be tied to per-vertex matrix
   selection.** Each vertex of a skinned character picks its own matrix from a
   uniform array. The generated shader appears valid, but there is no isolated
   Adreno reproduction yet. CPU skinning or draw splitting are proposed tests.
3. **Phone imports appear to accept modified game images.** The inspected import
   paths check disc ID and revision, not the code-file hashes in the builder
   profile. A modified image causing a specific startup crash is still a
   hypothesis; validate it before making that claim to users.
4. **The iPhone 17 crash (#196) is now decoded:** it dies at the boot screen
   when the game calls StaticR's start routine through the module linker. It
   needs one log line to finish.
5. **Every fatal exit on mobile turns into an abort** and can lose its own
   error message.
6. **Four runtime copies have drifted.** Several correctness/thread-safety
   fixes exist only on Android.
7. **The best measured Android improvements are not public**, and several
   ready changes sit in unmerged PRs.
8. **Low-end phones (Helio G85, Kirin 710 class) cannot reach 60 FPS** with any
   change listed here; they need 5–10× less CPU per frame.

## 1. Where things stand (verified 24 Sep 2026)

| Item | State |
|---|---|
| Public builds | Android 0.5.0/code135; Apple 0.5.1-experimental.1/build60 |
| Primary checkout `/Users/chrissotraidis/GitHub/kartpad` | Old branch, 381 commits behind origin/main, ~100 dirty files. Owner's; do not use or clean. |
| Working tree | `/Users/chrissotraidis/.codex/worktrees/kartpad-stabilization-20260918`, branch `codex/upstream-all-platforms-20260922` = PR #317. Remote head `927e01c`; ~19 local commits unpushed. `docs/artifacts/2026-09-22/clean-rc2.md` is dirty and not ours. |
| Runtime clones | `vendor/runtimes/{android,ios,macos,tvos}` are four clones of `chrissotraidis/wiicompiled` at detached HEADs **not on any remote**: android `a193cf4` (5 unpushed: FIFO presentation `8a9e885`, copy-spare release, streaming-copy withdrawal, course replay `c59e33b`, performance hint), ios `059d193` (3), macos `d4d7459` (2), tvos `39cf763` (2). |
| PR #317 | Mergeable. Contains the WiiCompiled upgrade **and the console-identity migration** (`ConsoleIdentity.txt` → NAND `setting.txt`), which is exactly the iPad profile-2 WFC gate still being verified. |
| PR #315 | Android RVZ import (#314), Vulkan cache persistence. **Already fully contained in #317's branch** (head `2ed6016` is an ancestor). Close as superseded when #317 merges. |
| PRs #289, #291, #292 | Stale; #289/#291 conflict. #292 (opt-in Dawn memory inspector) is still useful for §3.8. |
| Open issues | 62. Reporter-confirmed working: #215 ("It's working now"), #216 (Retro now loads; geometry/lag remain). |

## 2. Measured evidence gathered in this review

### 2.1 Pixel game-thread profile, symbolized (build 207 = retained 203/208 runtime, 12-kart Cookie Land battle, 30 s)

Source: `work/android-optimization-20260923/kartpad-207-cookie30.perf.data`, symbolized with the exact unstripped library (BuildID `8b94787d8c35…` at `android/app/build/intermediates/cxx/RelWithDebInfo/4j4vz4o5/obj/arm64-v8a/libmain.so`) and the game's own symbol table (`private/android-context-20260923/translation/guest_symbol_table.cpp`). Scripts: `work/deep-review-20260924/analyze_stacks.py`, `name_stacks.py`; stacks dump `stacks207.txt`.

Threads (share of all app CPU samples): game thread 80.4%, Aurora frame worker 10.0%, presenter 3.6%, audio mix worker 3.3%.

Game thread, exclusive attribution (each sample counted once, event-weighted):

| Bucket | Share of game thread | ≈ ms at 12.65 ms/frame |
|---|---|---|
| Translated game code (real work) | 45.8% | 5.8 |
| GX front end (HLE + Aurora decode/draw building) | **26.3%** (inclusive) | **3.3** |
| Scalar FP status emulation (`PpcF*StateInline`, `FinishScalarFp`) | **13.9%** | **1.8** |
| Emulated TLS outside FP | 5.6% | 0.7 |
| Dispatch glue (indirect calls, registry) | 4.4% | 0.55 |
| Locks/syscalls | 2.4% | 0.3 |

Named game work (inclusive): `EGG::SceneManager::calc` 48% (`Kart::Manager::Update` 18%, `ScnMgr::CalcAll` 9.7%, `Kart::Player::ApplyPhysics` 7.6%, `ObjectsMgr::Update` 6.2%); `EGG::SceneManager::draw` 41% (`RendererRaceModels::Draw` 33%, `nw4r::g3d::detail::LoadMaterial` 20.9%, `nw4r::g3d::ResShp::CallPrePrimitiveDisplayList` 8.5%). Hottest self: `PSMTXConcat`, collision (`KCLController::IsCollidingImpl`), `ModelDirector::Update`.

Emulated TLS callers: 36% via `CurrentCpuContext()` from FP helpers (this translation calls the context-less overloads at 18,062 sites), ~11% from indirect dispatch (`ScopedTranslatedExecutionAddress` and `inline thread_local` memo entries in `abi_bridge.h`), rest from inlined code. Note: candidate 204/205 already removed most TLS on the Pixel with no timing gain; treat TLS as tested.

### 2.2 How the GX front end is actually driven

- Translated NW4R code writes every GX word through the write-gather pipe; each word calls `HleFifoWrite` (`runtime/src/hle/gx/gx_fifo.cpp` ~L348), which appends then tries to parse. Each XF load and indexed XF load becomes its **own** `GXCallDisplayList` into Aurora on a 5–100 byte packet; BP writes apply one by one. 51% of `HleFifoWrite` time comes from `ResShp::CallPrePrimitiveDisplayList`/`LoadMaterial` chains.
- `GX__CallDisplayList_80172f64` (`gx_dl.cpp`) pre-scans every display list (max indices, CP writes, flattening; cached) only to size array uploads, then Aurora parses the same list again in `aurora::gx::fifo::process`. Two parses per list.

### 2.3 The failing character shader compiled for Vulkan

Tint was built locally from the pinned Dawn source (`work/deep-review-20260924/tint-host/tint`). Recipe `58866e32bada1f83` (from `kartpad-diagnostics-20260917/build/platform-investigation/actual-shaders/`) compiled with `--disable-robustness true` → `work/deep-review-20260924/spirv/58866.dyn.vs.norobust.spvasm`:
- The whole `Uniform` struct is lowered to one `array<vec4<u32>,208>` (3,328 bytes). Matrices are rebuilt by a helper from a byte offset: position `144 + index×48`, normal `1104 + index×48`. The relaxed-layout `array<u32,12>` is not a layout risk on Vulkan.
- Byte extraction is plain shift-and-mask (`OpShiftRightLogical`+`OpBitwiseAnd`), `/4` and `/3` go through Tint's safe-division helper, 7 `OpBitFieldUExtract` in other fetch helpers. The shader is valid, ordinary SPIR-V.
- The build121 "literal" variant really is an `OpSwitch` over 20 cases with constant-index loads, yet still failed on the S24. Compilers commonly fold such a switch back into an indexed load.
- Bindings: `vbuf`/`abuf` bind the whole 3 MB / 8 MB shared buffers; the uniform uses full `MaxUniformSize` with dynamic offsets. Undersized-binding reads are ruled out.

The only structural difference between broken skinned parts and working rigid parts (eyes, karts, tracks) is a **per-vertex, non-uniform index into the uniform matrix array**. Outside evidence: Bevy #24926 reports skinned-mesh corruption on Adreno 730 Vulkan when bone data came from a storage buffer (uniform path worked); the pattern of "Adreno compiler mishandles per-vertex matrix selection, workaround by avoiding it" fits both. This is strong circumstantial evidence, not a reproduction.

Device evidence: broken on Adreno 619 (#301, #216 Tab A9+), 750 (driver 512.762.41), 829 (512.842.36), 840 (512.842.19), OnePlus 15, Red Magic 11 Pro, Fold 8. Reported fine: Adreno 650/730/732/740/830 reports mention only performance; Mali phones fine; #211's reporter sees correct characters on a Galaxy A32 (Mali) with the same game file.

### 2.4 #196 iPhone 17 Pro Max crash, decoded

The reporter's build60 `.ips` matches the retained dSYM (UUID `4BD45C7C…`, `build/experimental-051-20260921/KartPad-build60.app.dSYM`). Named chain:
`__start → RKSystem::Main → RKSystem::Run → EGG::SceneManager::calc → StrapScene::calc (0x800079D0) → ModuleLinker::CallModule (0x8000A3F8, module index 1 = StaticR) → InvokeIndirectCpu → FatalMissingGuestTarget`, then `exit → ~ProcessTranscriptState → std::terminate → abort`.
`CallModule` calls the pointer at module header offset `0x34` (the REL prolog). KartPad expects StaticR at `0x805102E0` with prolog `0x8055531C` (registered native). The runtime preloads StaticR data at that address, but the game's translated `ModuleLinker` loads and relocates StaticR from the user's disc files into its heap; the prolog only matches if that heap placement is identical. Rejected: Code.pul mismatch (hash-checked every launch), silent guest-memory alias failure (throws), device-language-dependent layout (no locale mapping exists; SYSCONF comes from the user's NAND).

### 2.5 Other code facts verified

- **Image import:** iOS (`apple/ios/KartPadDiscExtractor.mm` ~L60–104) and Android (`android/app/src/main/cpp/kartpad_discio_jni.cpp` ~L70–102) check only `RMCP01`, revision 0 and that `StaticR.rel` exists. `builder/profiles/mkwii-rmcp01-rev0.json` already holds SHA-256 for `sys/main.dol` (`80d18895…`) and `files/rel/StaticR.rel` (`16d9d146…`).
- **Fatal exits:** `ProcessTranscriptState` (ios `runtime/src/main.cpp` ~L171; all four runtimes) is a static with two joinable threads. `std::exit` without `ShutdownProcessTranscript()` in `FatalMissingGuestTarget` (~L812), OS panic/`OSResetSystem`/guest `exit` (`hle/os/os_reset.cpp` ~L52/115/130/149), `os_init.cpp` L78, `dvd.cpp` L138, `nand_path.h` L49, `abi_bridge.h` L642 → terminate → SIGABRT. `hle/egg_decomp.cpp` calls `std::abort()` directly. `OSResetSystem` unmaps guest memory before exiting while workers may run.
- **Disc I/O:** "async" DVD reads are synchronous with immediate callbacks (`dvd.cpp` ~L958–1039); guest threads are cooperative fibers on the one game thread, so every read (course loads, music-stream refills) blocks the frame. `DvdReadContract::ReadExact` (`include/hle/dvd_contract.h` ~L290) opens a new `ifstream` and allocates a vector per read. `CopyToGuestAsDma` (`dvd.cpp` ~L110) copies **one byte at a time** through `Memory::Write8`. The Yaz0 decoder (`hle/egg_decomp.cpp`) also works byte-by-byte through guest accessors.
- **Pipeline replay recording gap:** course links are written only in `find_pipeline_impl` (`gfx/pipeline_cache.cpp` ~L499), reached only on a miss in the fifo's 1,024-entry `cached_pipeline_state` memo (`gx/command_processor.cpp` ~L2072), which persists across scenes. Pipelines first used earlier in a session are never linked to later courses; this partly explains "0 recorded" on Retro. Pipelines and shader modules are never evicted during a session.
- **Memory:** fixed GPU buffers ≈150 MB (37 MB shared + 3×37 MB staging). Static texture caches are count-bounded (512/256 source entries, 1,024 object entries), not byte-bounded. Pixel measured ~2.5 GB GPU memory after a battle.
- **Presentation:** Android public builds use Mailbox; FIFO exists only in unpushed `8a9e885` (Pixel: 102 vs 403 intervals >25 ms). iOS logs show `present mode Immediate` (#135). No build calls `ANativeWindow_setFrameRate`/`Surface.setFrameRate`. The performance hint (`runtime/src/hle/vi.cpp` ~L70–110) covers only the game thread, reports CPU time, API 33+ only.
- **Auto-accelerate:** touch overlay only (`KartPadOverlayView.kt` ~L1223–1240); physical controllers never get it (#319). #197's Ipega default mapping (A and B both accelerate) is a separate mapping bug.
- **Low-end logs (#320, Kirin 710/Mali-G51, public 135):** 40–160 ms game CPU per frame, zero queued pipelines, 0.5× resolution no help, 2.2–2.4 s spikes at scene loads, 128-pipeline prewarm took 11 s, audio blocks dropped.

### 2.6 Runtime drift, classified (android vs ios, every differing file)

| Class | Files / change |
|---|---|
| Correctly Android-only | mbedTLS/networking fixtures (`network_ssl.cpp`, `network_deferred.cpp`), FIFO presentation and Vulkan cache flush (`webgpu/gpu.cpp`), PNMTX diagnostic (`command_processor.cpp`, `shader.cpp`), scheduler event service (`fiber_manager.cpp`), Android logging, `guest_flat_memory_apple.cpp` (platform memory) |
| **Neutral fixes stranded on Android — port to Apple** | `dolphin/vi/vi.cpp` render-mode mutex (iOS reads/writes `g_renderMode` unlocked across threads; #310 crashes at race-selection transitions — plausible, unproven); `gfx/common.cpp` per-frame debug label lists (race dormant today: nothing pushes markers); `gfx/depth_peek` per-frame mapping; `gx.hpp` GEN_MODE first-write fix; `hle/os/os_alarm.cpp` deferred reschedule after alarm guard; `hle/gx/gx_copy.cpp` surface-loss present handling; `hle/storage/nand_api.cpp` removal of create-on-open (Android-only since 4 Sep as a "Wii open semantics" fix; upstream and all Apple runtimes still create files on a failed write-mode open) |
| Needs owner decision | NAND open semantics above (affects save/identity creation paths) |
| iOS long-term risk | iOS TLS uses deprecated SecureTransport (`SSLCreateContext`, TLS ≤1.2); Retro WFC hosts use a plaintext reroute on both platforms, so not a current blocker |

## 3. What to change, ranked

### 3.1 Ship what is already measured (Android)
Push the four runtime HEADs to `wiicompiled` branches, push the KartPad commits to PR #317, verify the iPad profile-2 WFC result with #317's migration, merge #317 (closes #315), and publish Android with FIFO + 203/208 + replay as a clearly labelled release. If the iPad gate still blocks, ship Android separately. Close #289/#291 after merge; keep #292 as a tool.

### 3.2 Fatal-exit fix (all runtimes, small)
Add one `[[noreturn]] RuntimeTerminate(int code, reason)`: flush, `ShutdownProcessTranscript()`, stop Aurora/audio workers, then `_Exit`. Route every path in §2.5 through it, including Yaz0 `std::abort`. On Apple, put reason, target and LR into the abort message or crash annotation so the `.ips` users paste contains them. Make `OSResetSystem` stop workers before unmapping memory. Host test: trigger each path, assert exit code and transcript tail.

### 3.3 Reject modified game images (small, high value)
Hash `sys/main.dol` and `files/rel/StaticR.rel` at import on iOS and Android against the profile's SHA-256; cache the verdict; show "This image is modified (for example Wiimmfi-patched or pre-patched). Please use a clean RMCP01 dump." Re-check cheaply at launch (size + cached hash). This can explain part of the "crashes at start on every version" family (#143, #200, #205, #208, #235, #236, #257) and #196's original "both games crash". Do not publish hashes of game files beyond what the builder already ships.

### 3.4 #196 finish
With §3.2 in place, add one boot log at `ModuleLinker::CallModule` (HLE wrapper or pre-call hook): module index, module base, prolog value, expected `0x805102E0`/`0x8055531C`. If the base differs, fail with a clear "StaticR relocated to an unexpected address" message and dump the heap/arena state; then fix the allocation determinism (arena seeds in `system_bridge.cpp` "low-memory defaults") or pin StaticR's load address in the HLE loader. Send the reporter the #317 build and ask only whether Retro/Original open.

### 3.5 Adreno character corruption (revised order)
1. **Get a Snapdragon 8 Gen 3 / 8 Elite (Gen 5) phone.** Pixel is Mali.
2. Diagnostic APK with a restart-only selector for draws that have `PNMTXIDX` direct and more than one matrix slot:
   - **D, CPU pre-skinning (primary, shippable):** in the Aurora draw path, read each vertex's matrix index and position/normal (direct or indexed), transform with the XF matrices already in `g_gxState`, emit direct F32 view-space vertices, draw with identity current matrix and no PNMTXIDX. Per-vertex texture-matrix texgens (env maps via `in_texmtxidx`) must be precomputed too, or kept in model space; handle both before shipping.
   - **E, per-vertex matrix in the vertex stream:** CPU writes the selected position/normal matrix rows per vertex into the storage stream; shader reads them linearly like any attribute. Keeps texgen semantics.
   - **F, split draws by matrix set** where triangles share one matrix.
   - **C, matrix palette in a storage/texel buffer** (last; the Bevy report shows storage-buffer skinning failing on Adreno 730).
3. Automatic self-test: render recipe `58866e32bada1f83` once offscreen with a synthetic 7-byte skinned mesh, write clip-space position to a float target, read back, compare with a CPU reference; log pass/fail with GPU and driver; enable D automatically on failure.
4. Optional: opt-in custom-driver loading for Adreno (the Dolphin Android approach) to separate driver regressions from KartPad bugs.

### 3.6 Take the GX front end off the game thread (largest CPU lever)
1. **No threads first:** coalesce consecutive BP/CP/XF/INDX packets from `HleFifoWrite` into one buffer and hand Aurora one batch at draw/GXEnd/flush/display-list boundaries; let Aurora size array ranges during its own parse so the HLE pre-scan in `GX__CallDisplayList` can go. Measure game CPU/present on the Pixel battle against 208.
2. **Then a GX thread** with a bounded ring. Faithful to hardware (the Wii GPU reads memory asynchronously) provided every sync point makes it catch up: GXDrawDone/draw-sync tokens, EFB peeks and CPU-read EFB copies, XFB/VI copy, FIFO status reads, display-list memory writes (existing snapshot/notify hooks), background/shutdown. Off by default, then per-device default after matched measurements. Budget: up to ~3.3 ms/frame on the Pixel battle.
3. Acceptance: matched Pixel battle + one Samsung flagship 12-racer VS race; p95/p99; no regressions in select thumbnails, minimap, results, EFB effects, Home/resume.

### 3.7 Scalar FP bookkeeping (one bounded experiment)
14% of the game thread. Earlier exact fast paths 191–193 gave no reliable gain and grew code 6%. Untried: translator-level value-exact emission (plain register arithmetic with Force25Bit, single rounding and NI kept; NaN/denormal slow path; no `volatile`, no FPRF/FPCC, no redundant `(void)PpcCompareStateInline` before `SetCRFloatResident`). Preconditions: prove no record-form FP instructions, keep the six OS-context `mffs` sites exact, pass the existing 300k-case differential on value bits. Ghost/online determinism depends on exact values, so values must stay bit-identical.

### 3.8 Memory and I/O
- Replace byte-wise `CopyToGuestAsDma` with one `memcpy` into `Memory::GetPointer(dest,size)` plus one write notification (keep executable-range guard semantics); keep a small open-file cache in `ReadExact`; make the Yaz0 decoder work on host pointers after one bounds check.
- Longer term: real async DVD (host I/O worker, completion posted to the guest scheduler) so music streaming and background loads stop blocking frames (#123 "turning off Retro music fixed lag", #320 load spikes).
- Use PR #292's Dawn memory inspector on the Pixel after a battle to attribute the ~2.5 GB (textures vs buffers vs pipelines); then add byte-budgeted LRU for static texture caches and a pipeline/shader-module retention bound scaled to device RAM. Bound background compilation memory (Pixel code125 Scudo OOM).
- iOS: log `os_proc_available_memory()` and memory warnings in the transcript; evaluate the increased-memory-limit entitlement with sideloading tools before adding it.

### 3.9 Frame pacing and scheduling
- Declare the frame rate on Android (`ANativeWindow_setFrameRate` 60 or interpolation target, FIXED_SOURCE) — relevant to steady 41 FPS on Samsung 120 Hz (#195).
- A/B native-rate FIFO on iOS/iPadOS (currently Immediate) — the same change cut long gaps ~75% on Android; relevant to #135/#310.
- Performance hint: add frame worker, presenter and audio mix threads; report wall-clock work per frame; consider raising game-thread priority.

### 3.10 Correctness items
- Port the stranded fixes in §2.6 to iOS/macOS/tvOS; decide NAND open semantics once for all runtimes; add a CI diff check on shared directories.
- Pipeline replay: give memo entries a scene generation so the first hit after a scene change still records the course link.
- Auto-accelerate for physical controllers (native pad path) or label it "Touch controls only"; fix Ipega default mapping (#197).
- Cup-end crash (#128/#131): nobody has reproduced it. Complete one 50cc cup on the Pixel or Mac build (about 8 minutes) with §3.2 in place; the exit reason will then be recorded.

## 4. Rejected in this review
- Dawn device-wide lock serialising background compilation (create calls are "no autolock").
- Frame interpolation as the Android character cause (off by default; menu previews also broken).
- Undersized storage-buffer bindings (whole buffers bound).
- Relaxed uniform layout as a Vulkan risk (Tint flattens to vec4 array).
- Code.pul mismatch, guest-memory alias failure, device-language layout for #196.
- #309 iPad 9 crash as the exit-path bug (it is the fixed ImGui cleanup after graphics-startup failure).
- Audio as a game-thread bottleneck on the Pixel (mixing is on its own thread, 3.3% of app CPU).

## 5. Order for the next agent
1. §3.1 push/merge/ship (owner approval for publication).
2. §3.2 fatal exits and §3.3 image hashes (host-testable, small).
3. §3.4 StaticR log for #196.
4. §3.10 port stranded fixes; replay generation; auto-accelerate.
5. §3.5 Adreno variant APK + self-test; get an Adreno phone.
6. §3.6 step 1 (packet coalescing), measure; then GX thread.
7. §3.8 I/O copies and memory attribution; §3.9 pacing A/Bs.
8. §3.7 FP experiment only after the above.

## 6. Tools and artefacts produced (private; contain game-derived data — do not publish)
- `work/deep-review-20260924/tint-host/tint` (host Tint from pinned Dawn source), `spirv/*.spvasm`.
- `work/deep-review-20260924/stacks207.txt`, `analyze_stacks.py`, `name_stacks.py`, `symdir/` (symlink to the exact unstripped library), `symfs/`.
- Host simpleperf: `~/Library/Android/sdk/ndk/29.0.14206865/simpleperf/` (`report_sample.py --symfs <symdir> --tid <game thread>`).

## 7. Standing constraints
- Never uninstall, clear data, downgrade or reset identity on devices; in-place installs with higher version codes; back up and read back data.
- Report physical-device evidence separately from emulator/host/package/compiler evidence.
- Specific, privacy-bounded reporter asks only; no public replies or releases without owner approval.
- Keep the primary checkout untouched. Do not suggest Figma.
