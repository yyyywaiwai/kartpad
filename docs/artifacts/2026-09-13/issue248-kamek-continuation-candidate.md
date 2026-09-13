# Issue 248: isolated Kamek continuation candidate

Status: **624 translator tests, exact-profile generation, focused Android compilation, and the complete incremental native runtime link pass.** Private code-81 packaging and APK audit also pass. Actual item-change/Item Rain gameplay remains open. The owner disconnected the phone before installation; no candidate install, public artifact replacement, or merge was performed. Earlier sections preserve the evidence and corrections that led to this candidate; the current native result is recorded at the end.

## Evidence

KartPad main `1fe6364` still prepares WiiCompiled `1912292` with six translator patches; none includes upstream [PR 182](https://github.com/patchzyy/Wiicompiled/pull/182), merge `25c69ae28e46a127d87db8d394f857e34da54f99`. Comparing the prepared translator confirms `linkedHookLrBasesByTarget` only includes RetroWFC hooks, and its LR-offset scanner only recognizes `mtctr`/`bctr`, not `mtlr`/`blr`.

Android 80's release CMake cache at `/private/tmp/kartpad-android-017-device/android/app/.cxx/RelWithDebInfo/3r384b1v/arm64-v8a/CMakeCache.txt` selects `private/translation-main-017/build_shards/shards.cmake` and prepared source `build/verify-fps-runtime-source-20260913-111027-final2`. That manifest includes both inspected Retro mod shards.

The compiled-graph input contains an item-window hook call at `0x807EF168` to `0x8183ADD8` with LR `0x807EF16C`. There is no generated resume label or registration for `0x807EF16C`. However, this exact hook's generated body returns normally or tail-calls `0x80860AF0`; absence of a resume label alone does **not** reproduce the reporter's abort. Upstream issue 83 originally concerns Deluxe X Blue, and issue 248's reporter has not run KartPad. Do not describe that exact crash as confirmed on KartPad.

There is a separate concrete skip-return defect in the actual graph: `rr_kamek_8180C6E4` saves incoming LR `0x807A1A58` in r31, tests the callback via `func_800213E4`, adds 20 when absent, restores LR from r31, and returns. Its caller in `shard_36c0daa3778847680f24436e.cpp` ignores changed LR and continues into the callback call at `0x807A1A68`, rather than skipping to `0x807A1A6C`. This matches PR 182's Item Rain cause at source level; runtime triggering remains untested.

## Candidate and regression

`patches/wiicompiled-kamek-skip-return.patch` is the exact upstream PR 182 diff, including its tests. `prepare-patched-translator.sh` applies it after existing KartPad translator patches. It applies cleanly to KartPad's prepared translator. The upstream planner handles path-sensitive LR offsets and saved-register restoration; CLI wiring includes Kamek BranchLink targets in continuation discovery and caller dispatch.

In an isolated translator copy, the original CLI scanner was exposed in Core with only a signature adapter (`FunctionTranslationResult` to its instruction list) so the upstream regression tests could exercise the old implementation. Result: **20 failed, 13 passed** LR-relative tests, including saved nonvolatile LR surviving a helper call. This was a behavioral failure, not merely the expected missing-API compilation failure. After the actual backport, the first staging-copy suite passed 607 tests, but exact-profile regeneration exposed that the staging source lacked KartPad's existing Kamek-v2 patch. That preliminary result is superseded by a fresh reconstruction from the pinned upstream translator plus all six patches in `prepare-patched-translator.sh` order, followed by this candidate: **622 passed, 0 failed**. The signature-adapted original scanner was rerun in this fresh stack and again produced **20 failures, 13 passes**. The fixed source was restored and its full suite rerun. Test fixture project configuration was copied into the isolated tree so root-discovery tests could run; no game binaries were copied into the patch or commit.

Fresh logs: `/private/tmp/kartpad-issue248-graph/exact-old-tests.log` and `/private/tmp/kartpad-issue248-graph/exact-tests.log`. Fresh translator: `/private/tmp/kartpad-issue248-exact-translator`. The preliminary logs remain separately preserved; they do not establish current-stack verification.

## Exact-profile regeneration result

The fresh translator regenerated only the mod and shard graph, reading the frozen Android 80 base manifest, functions, metadata, Code.pul, and saved Retro-WFC payload. Output was isolated under `/private/tmp/kartpad-issue248-graph`; no original translation or runtime source was regenerated. The Code.pul SHA-256 is `88cd25ff08121f7c4ddb40538703f40c270f414f2dbc55a6b4b6767e62db7253`, matching the released base-awareness record. Region is P and module guest base is `0x81800000`. Native shard registration input was the exact configured runtime source's `src` directory. The frozen base is valid to reuse because this backport changes mod continuation planning and leaves base translation unchanged.

Translation completed with **4,101 mod functions and zero C++ failures**, versus 4,095 mod functions in the released shard manifest. Six continuation functions were added. The planner reported 81 continuations. The candidate explicitly checks LR after the collision hook and includes local dispatch to `0x807A1A6C`, plus a standalone `rr_continue_807A1A6C`. It also emits `case 0x807EF16Cu: goto loc_807EF16C` and the local resume label. These are generated-source results, not gameplay acceptance.

| Measurement | Android 80 graph | Candidate graph |
| --- | ---: | ---: |
| Retro mod shards | 48 | 48 |
| Retro mod C++ lines | 1,430,752 | 2,021,781 (+41.3%) |
| Retro mod C++ bytes | 34,304,688 | 50,313,490 (+46.7%) |
| Largest Retro shard lines | 48,875 | 183,361 (3.75x) |
| All shard C++ lines | 10,931,923 | 11,522,976 (+5.4%) |
| All shard C++ bytes | 288,511,425 | 304,522,059 (+5.5%) |

The biggest individual overlay, `rr_overlay_8062C3A4`, expands from 25,675 to 154,388 lines (6.0x); `rr_overlay_8056F7F0` expands from 16,483 to 82,323. Moving functions between shards cannot remove this single-function growth. The correctness dispatch gate passed, but the growth gate failed. No native compilation was attempted.

Reproduction uses the fresh CLI's `translate-mod` with the frozen release base manifest/metadata, exact Code.pul, saved local payload, `--emit-cpp --threads 2`, then `emit-build-shards` with the frozen base functions and selected runtime native sources. The private project file, complete commands' outputs, and numeric comparisons are at `/private/tmp/kartpad-issue248-graph/{project.yml,translate.log,shards.log,released-stats.json,candidate-stats.json,function-growth.json}`. Generated sources and game-derived inputs must remain private.

## Gate after the unmitigated backport (historical)

Do not merge or release this candidate based on unit tests alone. Upstream [PR 218](https://github.com/patchzyy/Wiicompiled/pull/218) reports PR 182 increases Retro Rewind generated mod size by roughly 42%, with pathological compilation in an aggregate shard. PR 218 is open, and the issue 83 commenter reports its filtering removes the `0x807EF16C` resume point. Neither a broad pin bump nor unexamined adoption of PR 218 is justified.

The exact-profile regeneration now confirms both dispatch behavior and the substantial growth risk. Before merge, develop and regression-test narrower continuation code generation that preserves both addresses and all six added continuations; simply increasing the shard count is insufficient for the largest expanded function. Only after graph review should a native build and item-change/Item Rain gameplay check become the acceptance gate. The current Android 80 runtime has not been changed by this investigation.


## Shared-dispatch mitigation

A follow-up `wiicompiled-shared-lr-dispatch.patch` addresses the multiplication directly without adopting upstream PR 218's target filter. When a function contains multiple continuation-aware calls, each call retains its register reload and normal-return LR guard, but changed LR branches to one shared dispatch tail. That tail preserves the complete local address switch and registered external continuation fallback. Single-call code generation remains unchanged. The shared tail is outside block-local scopes and after an explicit return, preventing accidental normal fallthrough.

Fresh exact-profile regeneration under `/private/tmp/kartpad-issue248-shared-graph` yields:

| Measurement | Released | PR 182 alone | Shared dispatch |
| --- | ---: | ---: | ---: |
| Retro mod lines | 1,430,752 | 2,021,781 | 1,666,963 |
| Retro mod bytes | 34,304,688 | 50,313,490 | 39,915,562 |
| Largest Retro shard lines | 48,875 | 183,361 | 65,837 |
| Overlay `8062C3A4` lines | 25,675 | 154,388 | 37,286 |

Remaining mod line growth is **16.5%**, down from 41.3%. The formerly sixfold overlay expansion is now 45.2%; the largest shard is 34.7% larger than the released graph. This reduces the pathological expansion without claiming native compilation cost is proven acceptable.

All **4,101** generated function names and their distinct case-address sets match the PR 182-only graph. All **107** emitted `rr_continue` symbols are preserved, including the six additions over the released graph. The planner still reports 81 continuations, and both `0x807A1A6C` and `0x807EF16C` have local dispatch cases. Translation reports zero C++ failures.

Two new binary-free regression cases exercise 2 and 20 continuation calls: both fail against PR 182 alone and pass with shared dispatch. They require one switch, a guard and shared-tail jump for every call, preserved local and external dispatch, and normal fallthrough before the dispatch tail. The full fresh translator suite passes **624 tests**. Patch reverse-application and preparation-script syntax checks pass.

The generated two-call synthetic function was also compiled with Clang C++17 at both `-O0` and `-O2`, using `-Wall -Wextra -Werror` and minimal runtime stubs. Each binary executed nine scenarios covering normal return, skipping at the first or second call, local resumption, registered external dispatch, and an unregistered external return. Assertions checked call counts and final register state. Both binaries passed. Synthetic harness and logs remain in the isolated graph directory; no real game code was compiled in this check.

At this mitigation stage, focused native compilation was next. Its results and the completed native link follow below. Actual item-change/Item Rain gameplay remains necessary.


## Focused Android native compilation

The largest shard from each graph was compiled serially with the retained Android 80 `compile_commands.json` entry. Only the input C++ path and isolated output object path changed. The command retained NDK 29.0.14206865, `aarch64-none-linux-android28`, release `-O2`, actual runtime headers, definitions, and the existing validated PCH. `/usr/bin/time -l` measured each invocation. The shared candidate's largest shard includes the previously inflated `8062C3A4` overlay.

| Largest-shard probe | Lines | Wall time | Maximum RSS | Result |
| --- | ---: | ---: | ---: | --- |
| Released | 48,875 | 3.29 s | 315,621,376 bytes | Compiled |
| PR 182 alone | 183,361 | 87.78 s | 971,735,040 bytes | Compiled |
| Shared dispatch | 65,837 | 9.56 s | 439,566,336 bytes | Compiled |

These are single serial probes on a machine doing other build work, with different shard membership, not controlled performance benchmarks. They show the real worst-shard compile completes and materially improves over the unmitigated candidate; they do not establish runtime performance or full-link success. Original source, objects, PCH, and released artifacts were read only. Probe command arrays, timing logs, and isolated objects are at `/private/tmp/kartpad-issue248-shared-graph/native-probe`.

The focused native gate passed. The subsequent full native link result follows; packaging and gameplay are still open.


## Complete incremental Android native build and link

The final candidate native runtime linked successfully at `/private/tmp/kartpad-issue248-shared-graph/full-native/libmain.so`. It is an **ELF64 AArch64 shared object**, SONAME `libmain.so`, **863,123,344 bytes** including retained debug information, SHA-256 `4524a4d84e9db364b3e8ebbe8f9b54dc32a285976ae1fcaf19ed077b329a55a5`. This private native artifact is not an APK, installed build, or gameplay result.

The build used the retained Android 80 `RelWithDebInfo` command database: NDK `29.0.14206865`, `aarch64-none-linux-android28`, `-O2`, `-g`, `-DNDEBUG`, `-fno-fast-math`, `-ffp-contract=off`, and `-fno-slp-vectorize`. Actual runtime include paths, definitions, language mode, ABI, PCH, and full original linker flags were retained; only changed generated-source and output-object paths were substituted. Two compiler jobs ran concurrently. All **65 changed mod/registration/dispatch objects** compiled and the complete runtime link passed.

For safe cache reuse, the original frozen base-common boundary map was supplied to shard generation: **all 72 common-base sources became byte-identical**, allowing the original shared archive to remain read only. Another **65 linked generated objects** had byte-identical source and were reused. The **167 cached link inputs** were hashed before compilation and verified unchanged after linking. The actual PCH and wrapper hashes, every compile argument array, link argument array, source/object identities, and results are recorded under the private `full-native` directory. This was a complete incremental runtime build and link, not a clean rebuild of third-party dependencies.

Integration inspection found the earlier isolated graph's `--mod-root .../input` produced a DVD-root registration named `input`. Before native linking, mod generation was repeated with an isolated root named `RetroRewind6`, retaining the exact frozen Code.pul and WFC payload. The corrected generated data-initializer wrapper and both data blobs are byte-identical to the released inputs. The package-name correction does not change the function-count, dispatch, or code-growth findings. Final mod/shard inputs are `native-mod` and `native-shards` within the isolated graph directory.

Shared-tail control flow was reviewed during compilation: callee-state reload and normal-return guards remain at each call; the common switch sits outside block-local scopes and after an explicit return. Jumps target the same pre-block labels, so no local initialization is bypassed. External continuation fallback and return behavior are unchanged. No target filtering or new flush behavior was introduced. The full actual C++ compilation additionally checks label-scope validity across the changed graph.

Free disk was about 15.9 GiB before compilation and remains approximately 15 GiB. Original sources, objects, PCH, app artifacts, and devices were unchanged. Next acceptance gate is candidate packaging and actual item-change/Item Rain gameplay; no runtime acceptance is claimed.

## Private package follow-up

The newly linked runtime was stripped and packaged through the retained Android wrapper using isolated JNI inputs and explicit private version overrides (`0.4.17-issue248.1`, code 81). Embedded provenance records source `19e2d78`, the native build manifest and both runtime hashes. This is a debug-signed private candidate; public code 80 remains unchanged.

The standard APK audit and signature verification passed. APK SHA-256 is `56b43e305b54aecfd89f542ca12784a3bd7b7878673557c219e1ba081b0e105a`; packaged native SHA-256 is `d4f0281b7d9b1b9761492fd3a5f735769c70c7fbb1829969e46fa5a729ba10be`. Its signer matches the installed private code-79 APK on the Pixel. The owner disconnected the phone during backup before any install. A fresh, fully verified backup and pre/post protected-data comparison are required when it returns; the interrupted archive is not valid restoration evidence.

The remaining gate is exact-candidate device installation, affected item/Item Rain gameplay, race and relaunch acceptance. Keep this PR draft until that outcome supports merging the runtime change.
