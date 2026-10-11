# Evening issue and Android optimization loop

Started 2026-09-21 JST. Owner: Codex task `01a0c45b-6553-7c03-82bf-ab9d6d0fcf25`.
The user requested sustained useful work for eight or more hours, all-open-issue
review and replies, small tested fixes, and Android optimization informed by
the prior DriftDroid audit. The active task goal retains the full request.

## Baseline and ownership

- Current fetched main: `0d657f3`; latest stable release: 0.5.0.
- Apple build60 experimental release disables accidental forced diagnostics;
  it is a mitigation awaiting matched device evidence, not a proven FPS fix.
- Initial GitHub snapshot: 62 open issues, including new #313 and #314.
- Reuse the clean existing `kartpad-stabilization-20260918` worktree on
  `codex/evening-android-20260921`. Preserve the dirty primary checkout.
- Android maintained runtime starts at `295f4507fe1fd706f2edfa09055b815f425ed919`.
- Pixel 9 Pro XL is attached. No race or performance observation has yet been
  made by this task. Private device identifiers stay out of tracked evidence.

## Repeated cycle

1. Read every open issue and its comments; classify platform, symptom, supplied
   evidence, shipped scope, next engineering action and remaining acceptance.
   Reply specifically, acknowledge existing evidence, avoid repeated log requests,
   and record the actual comment URL. Refresh edited/new reports before posting.
2. Check recent task findings and release source before selecting one candidate.
   Prioritize actionable regressions and safe small enhancements alongside the
   sustained Android CPU work; do not substitute repeated audits for changes.
3. State one falsifiable hypothesis. Preserve a hashed baseline and relevant
   settings/data. Make the smallest source change and run meaningful checks.
4. Inspect the emitted artifact. Use matched control/candidate measurements on
   the attached device when feasible; retain scene screenshots and exact settings.
   Distinguish chooser, menus, attract/demo footage, gameplay and completed races.
5. Keep improvements with supporting evidence; reject or defer candidates with
   recorded reasons. Never convert symbol counts or microbenchmarks into FPS.
6. Update this evidence record and the existing maintenance records, commit
   reviewable changes, and continue the next useful cycle. Build/package success
   and affected-reporter acceptance remain separate. No automatic issue closure.

## Initial engineering sequence

- Verify current release linkage; test function-only local binding without
  changing Android's minimum supported API or scalar FP semantics.
- Verify Dawn cache persistence and add a safe explicit flush if still missing.
- Independently evaluate API29 native TLS; retain API28 compatibility by default
  until an explicit supported-release decision and real measurements exist.
- Review small display-list cache-copy reductions with ownership/invalidation
  checks; reprofile before selecting deeper scalar or asynchronous GX work.
- Investigate Android shake-to-trick and ghost discovery as bounded feature work.

Track actual elapsed work and outcomes. Eight hours is a requested working
window, not evidence of completion or justification for idle polling. Missing
one device or reporter does not stop other available engineering work.

## Completed first cycle

- Reviewed and replied to all 62 open issues; a fresh post-reply snapshot found
  no missing or newly opened tickets. Reply receipts are linked in the inventory.
  No issues were closed automatically. Maintenance queue tests: 65 passed.
- Commit `fe83144` adds Android RVZ picker-descriptor support. The actual Android
  DiscIO probe passed ISO plus uncompressed/Zstd RVZ byte equality, borrowed
  descriptor lifetime/offset preservation, and truncated-input rejection on the
  attached Pixel. Fixtures are synthetic; no actual game RVZ import is claimed.
- Re-linked the exact retained code135 objects as an unchanged control and with
  function-only local binding. The unchanged control reproduces the public native
  BuildID `ce82326003e7b0db832e931282f3f815195e60f2`. Candidate BuildID is
  `e27f23dbfca8367520ae8fd205787dbccd18c07a`.
- Internal jump slots fall from 10,873 to zero; remaining external slots: 610.
  Defined dynamic exports match. Stripped native size falls from 99,942,816 to
  99,168,352 bytes. Android API28 and scalar floating-point semantics are retained.
  These artifact changes do not establish a gameplay speed improvement.
- Built and audited 0.5.1-evening.1/code136 containing both changes. The attached
  device's code135 APK has identical ZIP entry contents and native digest to the
  published control, but uses the existing private test signer. A separate copy
  of code136 was signed with that verified matching identity and installed with
  `adb install -r`; installation succeeded without removing app data. Both game
  profiles still show Ready to play afterward. Public signing copy is separate.
- Physical control observations so far: Original title screen and automatic
  attract footage. The overlay visibly accepts a held A press, but the title
  screen did not advance. No user-controlled race or FPS gain has been verified.
  Input-path diagnosis and matched scene measurements remain in progress.

Private build products are under `build/evening-20260921/` in the retained
worktree; raw screenshots, reports and receipts remain ignored task-local data.
No APK release has been published by this loop.

### Continued device navigation and review

Draft PR: https://github.com/chrissotraidis/kartpad/pull/315 (receipts CI passed).
A broader Android contract selection also passed: 65 tests.

A private, temporary code137 input probe confirmed that a held A press reaches
both the JNI publisher and native consumer with matching state. A fresh run
advanced through the existing license, Single Player and VS selection screens.
The earlier failed presses are not an established source defect; their cause
remains undetermined. Temporary logging was restored out of tracked source.
Uninstrumented code138 reproduces the exact code136 native SHA256
`719c336fa56c12185c4b2e33ded09e40583a9449f3d801b651ab674a936df002`.
No race measurement has yet been made. Continue matched scene work before
making any speed claim.

### Second cycle: physical scene and cache candidate

- Uninstrumented code138 navigated through license, Single Player, VS, Mario,
  Standard Kart M, manual drift, and Luigi Circuit. Rules were read without
  changing them: 100cc, Normal CPUs, all vehicles, recommended items, four races.
  Existing resolution scale is 2x.
- Started an offline race and left the player stationary at the grid while CPUs
  circulated. Screenshots show the course introduction, lap1/time16.930, and
  eventually 12th-place results after CPUs finished. This is not a driven or
  player-completed race. Results returned to course selection successfully.
- Initial 50-second capture: nine FPS samples, median57.23 (43.63–59.66),
  ten main-thread CPU samples median14.4065ms/present, all sampled shader queues
  empty. Thermal status changed from1 before the race to2 during/after it.
  A later capture crossed toward automatic results, so it cannot support a
  matched race comparison. No linker speedup is established from these numbers.
- Built code139 with the unchanged native control; its native SHA256 exactly
  reproduces public code135 (`fd457f61e1e4ef1884ee876f8d6fc7cebd2807bcbaf002ef3f16d2a5b36a475d`).
  Installed in place. Title-screen A presses initially failed again. Returning to the native menu
  and resuming allowed input to advance; this remains an unresolved lifecycle/input
  observation, not a proven linker fix.
- Runtime branch `codex/android-evening-20260921`, commit `802bee0`, adds the
  missing static-Dawn Android Vulkan idle flush and a renderer-mutex-serialized
  background event-pump flush. Existing startup prewarm limits remain unchanged.
  Both modified files compiled with the current Android toolchain; the full native
  build completed successfully. Packaging/device cache validation is in progress. Idle-flush timing/blob-store counters will support real
  cache validation. A GitHub504 archive fetch was recovered using retained
  dependency archives and their existing CMake hash checks, then native configure.

- Control code139 reached the same stationary Luigi Circuit 100cc scene. The
  first capture had 11 FPS samples (median60.01, range36.89–60.47) and 12 CPU
  samples (median14.2935ms/present). Screenshots at race times3.018 and29.575
  confirm stationary race state. Thermal status was3 before and after, versus
  candidate1→2; captures include different amounts of loading/countdown time.
  These sequential, thermally unmatched samples establish no performance win.

- Runtime cache change is reviewable in [wiicompiled PR2](https://github.com/chrissotraidis/wiicompiled/pull/2),
  stacked on the previously pinned maintained runtime. Code140 `0.5.1-cache.1`
  completed the native build and release bundle/package audit. Native SHA256:
  `9baeca49234bc808fe21500c2d47cac5a47a0552d18e0fe0f05cb3a94214f119`.
  Private device APK SHA256:
  `45654d257d6280d528dc0b8306efde99d80056c7604b1651e404136ca9f9b2a2`.
  This is a private test artifact, not a published release.
- Refreshed all-open-issue snapshot: still62. New #215 startup success and #211
  S24 Ultra/A32 comparison were acknowledged and added to the inventory/queue.
  All65 maintenance tests passed after those updates.

### Cache lifecycle correction found by physical testing

Code140 launched with both installed profiles retained. Boot-prewarm idle flush
ran in9.989ms and recorded one blob-store callback. This confirms execution and a
store attempt, not yet successful database persistence/reuse. Home/resume worked
but two observed transitions produced no background flush.

SDL3.4.4 `SDL_SendAppEvent` dispatches application lifecycle events only to event
watchers, never to the normal event queue. The first candidate's normal event
handler was therefore unreachable. Runtime commit `3850952` moves only this
infrequent idle flush into the Android background watcher under the renderer
mutex, before the Android event pump blocks. It does not reconfigure surfaces.
It also includes cumulative blob lookup/hit counts for warm-relaunch validation.
Code141 is building; lifecycle success is not yet claimed.

Source evidence: [SDL events](https://github.com/libsdl-org/SDL/blob/release-3.4.4/src/events/SDL_events.c)
and [Android event pump](https://github.com/libsdl-org/SDL/blob/release-3.4.4/src/video/android/SDL_androidevents.c).

### Verified cache boundaries and TLS experiment preparation

Code141 `0.5.1-cache.2` passed clean build, unsigned-bundle and release-APK
audits. Its native SHA256 is
`f0176ca0fde6f072c7f844da338618739b7cbe9d0e784b9dc814b360129cc04b`;
private APK SHA256 is
`d2da47df7e21b65918dfa9aabd819078ffb4d1a1c780f66164aa0c40af3a4867`.
The first wrapper run had a post-Gradle syntax error because its script was edited
while running; rerunning the unchanged wrapper succeeded in25s with cached native
outputs. Do not edit active build scripts.

Physical code141 evidence:
- Both installed profiles remained present. Boot completed with303/303 Dawn blob
  lookups hitting; idle flush0.338ms, zero new store callbacks.
- Home at01:03:13 was followed by a background flush at01:03:14, before resume
  at01:03:18. Flush0.007ms, no new store callback. Screenshots confirm Android
  Home and a restored game title, not a race.
- After navigating into game menus, Home triggered a154.370ms flush and one
  blob-store callback (785hits/800lookups), followed by successful resume.
  This validates the corrected hook and demonstrates warm cache reads plus
  new-store activity; no isolated load-time/FPS improvement is claimed.
- A1200ms title A hold advanced but engaged the existing gas-lock feature. A
  subsequent short press released that lock before navigation. Earlier shorter
  title-input observations remain ambiguous; no input fix is claimed.

Code142 is a non-debuggable, shell-profileable API28 control. Its native hash
exactly matches code141; the profiler audit verifies every allocated ELF section
against retained unstripped symbols and verifies the device-compatible signer.

Commit `c36187b` adds an explicit, default-off API29 native-TLS experiment. Both
manifest minimum and native target change together; test version names must
contain `-native-tls`. Invalid switch/name combinations fail before building,
and the API29 package audit correctly rejects the API28 control. Ordinary builds
remain API28. Code143 is compiling in a separate native configuration; all236
translated-shard commands target Android29 without forcing emulated TLS. Final
ELF/package and physical measurements are still pending.


### Native TLS artifact and initial CPU attribution

Code143 `0.5.1-native-tls.1` completed the full build and passed bundle, APK,
profileability, signer and allocated-symbol-section audits. Native SHA256:
`06b454d263d187b3807c857b810a466c56587c802fc79befa67223725c20286d`.
Private APK SHA256:
`7006a823ef95dd783d097000c5485898d44d233fd8d99a678277392c05d4d49b`.
The ELF Android note reports API29, with `.tdata`/`.tbss` and 152 TLSDESC
relocations. The API28 control has no TLS sections or TLSDESC relocations.
This proves the intended compiler/linker change, not a performance gain.
Code143 installed in place with the existing signing identity; no app data was
cleared. Physical runtime validation is next.

Code142's exported session confirms 128 pipeline recipes warmed in 0.8 seconds,
with 303/303 blob hits, zero stores and 4.7 MiB loaded. The same session contains
native KPAD A-button edges despite intermittent title-screen navigation failure.
No input fix is claimed. Its debug-only RKG fixture path is unavailable in this
non-debuggable release candidate.

A 19.987-second code142 **title/attract sequence** simpleperf capture recorded
1,822 CPU-cycle samples with zero samples lost. This is not a race benchmark.
Build-ID-matched unstripped symbols identify the largest self-costs as translated
functions `801B4DA8` (13.02%), `801B5234` (5.83%) and `801B5B74` (4.43%).
Emulated TLS lookup was 1.41%, with `pthread_getspecific` at 1.09%; these are
sampled shares in this sequence, not predicted whole-game speedups. Frame-pointer
unwinding reported 30.4% erroneous callchains, so inclusive/caller attribution is
not reliable enough for conclusions. Self samples provide the next investigation
targets. The supported `simpleperf record --app` path works without rooting or
changing kernel security settings.

A separate uncommitted display-list experiment replaces five per-hit array copies
with const references to the thread-local cache record. Cache insertion/eviction
remains confined to the miss branch, which uses local scratch arrays. Both versions
compile with the production API28 flags; the affected function's machine code is
7,216 bytes before and 7,172 bytes after. Runtime correctness and performance are
still pending; this experiment is not in a pinned candidate or public release.


Code143 physical follow-up: both profiles remained ready, Original launched and
rendered the title/attract sequence, and a second 19.986-second CPU profile captured
1,817 samples with zero lost. The same three translated functions were largest
self costs (17.94%, 9.46%, 4.47%). Emulated TLS lookup fell to two samples/0.10%
and `pthread_getspecific` had no self samples in this capture. Scene timing,
thermal conditions and sample counts are insufficient to infer a whole-game
speedup. Callchain errors were 2.37% in this capture, versus 30.4% in code142;
do not attribute that difference to TLS without a controlled unwinding test.
Title A navigation remained intermittent with both 500 ms and 1,200 ms presses;
the latter's intentional cyan gas lock was cleared with a short tap. No race
was reached on codes142/143. The next optimization work should retain this
boundary while investigating the measured translated CPU hotspots.


### Profile interpretation corrected before optimization

The public [RMCP01 symbol map](https://github.com/doldecomp/mkw/blob/main/config/RMCP01/symbols.txt)
identifies the three title-profile hotspots as `__THPInverseDCTNoYPos`,
`__THPInverseDCTY8`, and `__THPHuffDecodeDCTCompY`. They decode the THP movie;
they are not evidence of the race simulation bottleneck. Keep this profile as
startup/movie attribution and obtain an actual race or explicit retail replay
profile before selecting gameplay optimizations.

The existing September 3 Android replay investigation also rejects assuming
that injected RKG player input naturally completes a race: it diverged on three
courses. Retail Watch Replay was useful rendering evidence but did not prove
player results/save. An optimized private capture build is being prepared for
input inspection and repeatable scene selection, preserving the normal native
runtime and installed data. The display-list array experiment was saved to an
ignored patch and removed from the maintained source while building this control,
so it cannot confound the input/TLS investigation.


### Diagnostic build and rejected debugger capture

Code144 `0.5.1-native-tls-input-capture` built successfully with optimized native
flags. Package identity, API29 minimum, ARM64/alignment checks and the existing
private signer passed. Every allocated native section matches retained symbols.
APK SHA256 `98a3036595bf42df96359a54c65f5494fe6b6bdd1c274a4cab37572f80a63fbc`;
native SHA256 `0dc3f97b77247e6c65177ff23b2e0046f625919bab075a1474925be44c8c2459`.
It is deliberately debuggable, so it is not a public release or a substitute for
the non-debuggable profiler acceptance gate. Installation preserved both ready
profiles. Before further diagnostics, both existing `rksys.dat` saves and all
five preference files were copied to a private host backup with per-file hashes.
No fixture or steering marker was present, and none was installed.

A bounded LLDB input trace attached without root and observed one Unified WPAD
read followed by one KPAD read in the same presentation frame. It then encountered
a Vulkan device loss (`vkQueueSubmit` / `VK_ERROR_DEVICE_LOST`) after debugger
pauses. The backtrace reaches Aurora's device-loss fatal path; the debugger was
detached and its port forwarding removed. Reject this run as stability,
performance or input-fix proof. The two neutral samples do not establish the
input-loss hypothesis. Further input tracing must avoid stop-the-world pauses.


Code145 adds bounded, private, marker-enabled logging without debugger pauses.
It passed the package audit and device-signer check and installed in place.
A 500 ms title A press was observed by both Unified and KPAD readers from
presentation frame1436 onward. KPAD generated Classic A trigger `0x10` at1436,
then reported A held through1458 and released at1462. The title did not advance.
Thus a consumed short edge does not explain this held-press failure; the next
trace observes the guest controller's stored raw state and UI output. No input
behavior has been changed. These transient diagnostics remain outside the PR.

Fresh preparation preserved file timestamps only after byte-for-byte equality
checks against the retained control: 857 unchanged files, with `kpad.cpp` alone
changed. Source verification still runs normally. This lets the native build
recompile the actual changed input unit without rebuilding unchanged translated
shards; it does not reuse changed source or weaken the preparation check.


Code146's additional read-only trace shows the guest controller connected and
retaining raw Classic A (`0x10`) across the held press. The title still does not
advance. UI fields sampled at the start of controller calculation are zero, but
the caller may clear those outputs before calculation; that is not evidence of
lost input. A further private trace samples the completed UI state at presentation
instead. This narrows the investigation beyond Android delivery and raw KPAD
consumption without introducing a speculative input fix.


Code147 samples after controller calculation at presentation. During the 500 ms
press it observes mapped UI A (`0x0001`) and raw Classic A (`0x0010`) through
frames1617–1644, then release at1645. The title still ignores the press. The
private trace initially named UI offset6 `trigger`; inspection of the translated
Classic controller shows that field copies raw buttons. It is not a trigger or
proof that the page handler received an edge. The next trace corrects that label
and inspects controller registration. No behavior fix or gameplay improvement
is claimed from these title-only runs.


Code148 passes the package/signature checks and installs in place. Its title
trace confirms the UI state is marked valid (`0x80`) while A is held, and the
player-one registration passes the game's current/expected-controller equality
check. The registered controller proxy still needs to be followed to its
selected pad; merely seeing A in the separately calculated Wii pad does not
prove it is the pad the menu reads. Latest PR checks at `70aeda9` all pass
(boundaries, receipts, regression).

Code149 follows the registered player-one proxy to its selected pad. It points
to the same Wii/Classic pad previously traced, with mapped A1, raw A16 and
valid128. Reject wrong-controller selection as the explanation for this run.
A subsequent private trace inspects active pages rather than changing the
Android button route. Codes148/149/150 are transient optimized debug captures,
not public binaries or FPS evidence.


### Apparent title input failure resolved as a test-state mistake

Code150's active-page trace reveals OpeningMovie (page89) above Title (page87),
although the screenshot still shows the title artwork. The held A press causes
page transitions and removes the movie page; it does not represent an ignored
button. Three short 300 ms A presses separated by 800 ms then reach the main
menu, with intervening screenshots retained privately. This corrects the earlier
claim that the title was ignoring A: delivery, selected-pad state, and page
transition all worked. No input behavior change is warranted from this run.

All private traces were saved as ignored patches and removed from maintained
source. The task-created InputTrace marker was removed. A normal non-debuggable
API29/TLS profiling candidate is rebuilding so title diagnostics cannot confound
the next gameplay measurement.

Preservation readback after150 matches all seven backed-up files byte-for-byte:
both saves and all five preference files. Code151 passes the non-debuggable
profiler audit, exact-symbol allocated-section comparison, API29 package audit,
and recipient-signer check. Its native SHA256 is identical to code143
(`06b454d263d187b3807c857b810a466c56587c802fc79befa67223725c20286d`),
confirming the private input instrumentation is absent. APK SHA256:
`b8dade7d86e4ede910c268dd584764ddc91a7f607ecc971d4ec5c5a6882e8adb`.


### Moving retail replay profile

Code151 reached Original → Time Trials → Luigi Circuit → Nin★sato 1:29.670 →
Watch Replay. Screenshots before and during capture show the translucent Luigi
ghost at different course positions. This is retail replay validation, not
human driving or player completion/save proof. At2x resolution, a29.9884-second
profile recorded3,394 samples with0 lost. Both thermal snapshots reported3.
Six five-second telemetry samples within the capture window gave median60.00FPS
and9.146ms main-thread CPU per present (range9.018–9.797ms). Window endpoints
are inferred from the recorder's completion timestamp, so this is initial
attribution rather than a precisely synchronized A/B benchmark.

Largest named self costs: GX display-list call4.33%, scalar-flag clear2.79%,
Aurora FIFO processing2.46%, scalar-flag capture2.32%, native TLS resolver2.16%.
The sample attribution supports testing the saved display-list array-reference
change. It does not justify changing floating-point semantics. Code152 builds
that single runtime change on the same API29/TLS configuration; source review
confirms cache-hit references are consumed before drawing/possible recursion,
and cache stores/evictions occur only in the miss branch before binding them.

Code152 passes the same release/profileability/symbol/signer audits and renders
the moving staff replay. Native SHA256:
`4453dd56927573fe69c4dc3b542f9821b47733fc8f35b2f8947b5e128fdf6ff9`.
Its29.9863-second capture has3,424 samples,0 lost. Thermal remains3. Seven
telemetry samples give median59.95FPS and9.540ms CPU/present, versus9.146ms
for151 in a different replay window. No performance benefit is established.
The display-list self share is4.11% versus4.33%; this difference alone is not
a speedup measurement. The array-reference change remains an uncommitted
experiment pending stronger evidence.

Mapping sampled instruction addresses to the exact retained152 symbols locates
substantial work in hash-bucket lookup and vertex-snapshot construction, rather
than assuming the five copies dominate. Cache telemetry shows about760 records
and only roughly22% front-table hits. Code153 is testing1,024 direct-lookup
slots instead of256 (12KiB additional thread-local storage), retaining full
identity/content validation and clearing the front table on eviction. It is
not yet accepted or included in the maintained runtime pin.


### Larger front-table measurement (September22, 02:52 JST)

Code153 passed release-package, non-debuggable shell-profileability, exact
allocated-section/symbol and recipient-signer audits, then installed in place.
The same Luigi Circuit staff replay rendered at2x before and after a29.98-second
capture:3,567 samples,0 lost, thermal status3 at both endpoints. Seven telemetry
samples in the device-timestamp window gave median59.98FPS and9.693ms CPU per
present (9.392–9.739ms). The front-hit fraction increased to47.19% from roughly22%
with256 slots, but GX display-list self cost remained4.08% and no CPU improvement
is established. These different replay windows do not constitute matched A/B
acceptance. Neither display-list experiment is included in the maintained pin.

APK SHA256: `3e4519b269dfdf3e4c726cf8b17956171cf869605c5bb1eec201bf4b851c258b`.
Exact native symbols and private screenshots/profile/thermal logs are retained
locally. Next: remove unnecessary vertex-snapshot default construction with
explicit state-restoration tests, then compare synchronized replay windows.
PR315 boundaries, receipts and regression checks all passed at this checkpoint.


### Vertex snapshot candidate (September22, 03:01 JST)

Code154 returns to the maintained256-slot/cache-array-copy behavior and changes
only vertex snapshots: format/array storage holds object bytes without default
constructing208 formats, and capture fills its destination directly. Descriptor
storage stays typed because the fallback vertex submitter reads it directly;
the full Android compiler caught that dependency in the first draft, which was
corrected before packaging. Partial restoration still uses the original presence
flags and format-row mask. Trivially-copyable assertions guard the copied types.

The production capture/restore functions pass16,416 isolated state cases under
ASan/UBSan:32 state patterns, full restoration, every CP register, and all256
format-row combinations including duplicate writes and empty writes. This does
not substitute for renderer acceptance. Full dual-runtime Android build passes,
as do release/signer/profileability/exact-symbol audits. The ARM64 display-list
function is0x1a3c bytes. Code154 is installed in place and reaches the menus;
longer replay performance comparison remains pending. Fourth issue refresh still
shows62 open issues and no new reporter update since the previous review cycle.

APK SHA256: `fed37223970738e7c25a2ceb5147481b4e7d603180d22e1145e6bbd925c6acff`.
Native SHA256: `bb13961dd3f9ec7302c3fa4e8ddba48856ebdcbf113fdb97a615bb25bff7b224`.
Runtime change and the new contract test remain local experiments pending device
comparison; the maintained child pin is unchanged.


Code154's89.9943-second retail staff replay capture records12,186 samples,0 lost.
Before/during/after screenshots show the ghost at different course positions.
Excluding the first6 seconds of telemetry to avoid a partial initial interval,
17 samples give median59.88FPS and9.828ms CPU/present (8.666–10.471ms), with
thermal status3 before/after. GX display-list self share is3.20%. This is a
longer attribution capture, not yet evidence of an overall speedup. The exact
function shrinks from0x1c9c bytes in151 to0x1a3c bytes in154.

Control155 is built and audited, with native SHA256 byte-identical to151. Its
APK SHA256 is `67f8678e4374c74cc49b13ed4bbc98488dbbf8a2686b7f1deee99e615eb6c53c`.
It is not installed at this checkpoint. The child checkout is temporarily back
at its clean maintained source for that control build; the154 candidate source,
patch, prepared tree, symbols and package are retained locally. The contract
test is pending alongside that experiment and expects the candidate signatures.
Next step: install155 in place and collect the same longer staff-replay profile,
then repeat the candidate before accepting or rejecting it.


### Snapshot candidate/control/repeat (September22, 03:15 JST)

All three runs use Original, the same Luigi Circuit staff ghost,2x resolution,
API29 native TLS, non-debuggable profileable packaging, and thermal status3 at
both endpoints. Each records90 seconds at99Hz. Telemetry excludes the initial6
seconds to avoid counting an initial partial five-second interval. The replay
loops; these are retail staff-replay observations, not driven races or save proof.

| Build | Native behavior | CPU median ms/present | FPS median | GX DL self share | Samples/lost |
| --- | --- | ---: | ---: | ---: | ---: |
|154|Snapshot candidate|9.828|59.88|3.20%|12186/0|
|155|Original snapshot control|10.070|59.99|3.86%|10636/0|
|156|Byte-identical candidate repeat|9.947|59.89|2.76%|9883/0|

The control's45 samples in vertex-format default constructors disappear in both
candidate captures. Estimated sampled display-list cycles fall from6.260 billion
in the control to5.243 billion in154;156 again has lower display-list self cost.
The source change removes that work rather than changing guest state semantics.
CPU medians are1.2–2.4% lower in the two candidate runs, but this is a small local
observation with unsynchronized replay phase, variable scheduling/clocks, and
one device/course. It is not a general Android FPS improvement claim. Whole-game,
Retro Rewind and reporter-device acceptance remain outside this evidence.

Retain the snapshot optimization in the Android runtime pin, with the16,416-case
ASan/UBSan restoration test wired into shared-runtime CI. The earlier array-reference
and1,024-slot experiments remain excluded. Code156 APK SHA256:
`920e8047eb97f1bb678fe5a4700034a1ffc55670c631f3aa852ebbdc9cc1c3c5`;
its native SHA256 is identical to154. Next measure the retained change in the
API28/default build and separate native-TLS effects using the same replay method.


The retained Android runtime is nowb864121, integrated in root0dae4bf. All three
PR checks pass, including the new snapshot test on Linux CI. PR315 and childPR2
descriptions now include the actual replay results and limitations. Code157
builds the retained optimization with the normal API28 minimum/native target;
release, profileability, signer and exact allocated-section audits pass. APK:
`a76da8c2ea689c6d547c707137ff99893c2dca1616c957dd91a8f1d49d40e491`. Native:
`a408a49316dc5c7b596be2b40c3acf31c4c25396daed07d50df9ef03d19a26b3`. It is retained locally and not yet installed;156 remains
on the phone. Next: API28 replay comparison against156's native-TLS snapshot.


### Default API28 replay (September 22, 03:27 JST)

Code157 installed in place and rendered the same Original Luigi Circuit staff
replay at 2x. The native Android identity note reports API28 (0x1c), matching the
manifest minimum. This ran on the attached Android17 phone, not Android9 hardware.
A 90.0104-second capture recorded 10,259 samples with zero lost. Thermal status
was 3 before and after. Seventeen telemetry intervals after the six-second
initial exclusion give median CPU 9.975ms/present and FPS 59.94. The previous
API29 snapshot repeat gave 9.947ms: this comparison does not establish a useful
native-TLS whole-frame improvement. Default API28 support stays intact.

Do not hide the outlier: one FPS telemetry sample was 44.18, p99 149.03ms, worst
175.16ms. The neighboring present-phase aggregate reports present_call maximum
173.387ms and main CPU 8.860ms/present. No pipelines were queued. This locates a
presentation stall in that interval but does not prove its cause or attribute it
to the TLS configuration. Replay phase is not synchronized across builds.

API28 self samples include emutls 2.17%, pthread_getspecific 1.04% (not exclusively
attributable to emutls), and GX display-list 3.31%. Code158 is built and passes
release/profileability/signer/exact-symbol audits; its native library is byte-for-
byte identical to156. APK SHA256:
`95cd9f1d52b349c6b9074fac45b427efb59afc3f047e2789853cfa693f46f934`.
It is not installed at this checkpoint;157 remains on the phone. Next install158
for the API29 repeat, then investigate remaining profiled GX costs with the same
state-preservation and device-evidence requirements.


### API29 repeat and CP-effects candidate (September 22, 03:40 JST)

Code158, native-byte-identical to156, rendered the same staff replay at2x.
The89.98-second capture recorded10,072 samples with zero lost; thermal status3
before and after. Seventeen telemetry intervals give CPU median9.461ms/present
and FPS60.01 (lowest interval56.67). This is5.2% below the intervening API28
code157 median, but earlier identical API29 code156 gave9.947ms. That within-build
variation prevents attributing the difference to TLS. Default API28 remains
unchanged; native TLS stays opt-in. Screenshots show staff replay movement, not
human driving or a completed player race.

Candidate159 computes the CP-write effect mask once when storing a validated
display-list cache record, avoiding the classification loop on subsequent hits.
It still replays every CP write in order. Identity, digest/generation validation,
eviction and nested-list exclusion are unchanged. The summary adds8 bytes per
record, at most64KiB for8,192 entries. The16,416-case ASan/UBSan state restoration
test passes; the full API28 Android build and package/profileability/signer/exact
allocated-section audits pass. APK SHA256:
`93fca44e28d3956486be31a9c94f0be4d8bb1e6c640b27a552fdfc44b2bc7ea7`;
native SHA256:
`5eebfc9548bbe7389df5911313c28e04b03f26713e2c53d5d1aca857ba558ead`.
The experiment remains uncommitted pending physical comparison with API28 code157.


A follow-up attribution of code158's clock samples identifies68 under
`IsKeyDown` (KPAD keyboard polling),101 under VI `SleepPreciselyUntil`, and21
under diagnostic thread-CPU sampling. The KPAD path scans all SDL scancodes
and compares every synthetic expiry against `SDL_GetTicksNS()`, even when
its atomic expiry is zero. A zero-expiry short circuit is the next bounded
experiment; no input behavior change or issue197 fix is claimed. VI waiting
samples are not automatically a useful-work bottleneck and will not be removed
merely to reduce the sampled percentage. Private attribution is retained as
`tls158-clock-callers.json`.


### CP-effects replay and keyboard candidate (September 22, 03:47 JST)

Code 159 installed in place with verified version/minimum and rendered the
Original Luigi Circuit staff replay at 2x. The 89.9967-second capture recorded
10,368 samples, zero lost, thermal status 3 before/after. Seventeen telemetry
intervals give CPU median 9.535ms/present and FPS median 60.03 (minimum 59.75).
GX display-list self share is 3.25%, 242 samples. The old classification loop
no longer appears; the preserved CP-write replay loop still accounts for 32
samples. Total GX cost is close to API28 code 157's 3.31%, and unsynchronized
phase/clock variation still prevents a broad performance claim. Captured frames
show no obvious geometry failure; this is bounded staff-replay validation.

The separate code 160 candidate adds an inactive synthetic-key expiry short
circuit. A held physical key returns immediately. A zero synthetic expiry skips
the clock; nonzero expiries retain the exact strict-greater-than comparison and
atomic acquire load. Synthetic stick scale is unchanged. An extracted-production
ASan/UBSan test passes 73,728 key/axis comparisons, including exact expiry, maximum
timestamps, physical input, both stick scales and an event arriving between
polls. A fresh inactive 512-scancode sweep makes zero clock reads. Full Android
packaging is in progress; no device result or issue197 resolution is claimed.
Both experiments remain uncommitted at this checkpoint.


Code160 full build finished successfully in58s. Package, minimum API28, private
signer, profileability and exact-symbol audits pass. APK SHA256:
`600b0a0d641da6d8c3d623ee7a042e196857623b558ad001b9b9b94fe6c39cc0`;
native SHA256:
`1fb20d16901c1535d58f0b4a0ea4628042f2c9b695dab00e2842e21c74ef7aec`.
It is retained locally, not yet installed. Code159 remains on the phone in
staff replay. Next install160 in place, test menu input and replay CPU/clock
samples, then broaden to moving multi-kart and Retro Rewind scenarios.

The03:48 issue refresh found63 open tickets. New316 has been reviewed and
answered with one decision-specific screenshot request;275's latest reply is
an acknowledgment. The inventory now contains63 individual response links.
The8+ hour goal remains active, with about4h25 elapsed at this checkpoint.


### Input clock avoidance accepted (September 22, 03:55 JST)

Code160 installed in place, with version160/minimum28 confirmed. Short touch
presses navigated the normal menus into the same Luigi Circuit staff replay.
The89.9839-second sample recorded10,202 samples, zero lost, thermal status3
before/after. Seventeen intervals give CPU median9.397ms/present and FPS60.08
(minimum59.82), versus code159's9.535ms/60.03. That1.4% timing difference remains
a single-device, unsynchronized-phase observation, not a broad FPS claim.

The targeted mechanism is directly visible:57 sampled clock calls attributed
to `IsKeyDown` in159 become zero in160. VI pacing clock samples remain102/103,
which is consistent with specifically removing unnecessary input polling work.
The production-function test passes73,728 comparisons under ASan/UBSan; existing
controller-routing tests pass3/3. Normal menu touch input and the staff replay
remain functional. Physical keyboard/controller and broader race acceptance
remain separate. No issue197 fix is claimed.

Retain the CP-effects summary as childb0e3349 and keyboard clock avoidance as
child51b4c45. Both retainAPI28 and guest state/input semantics. The snapshot and
keyboard contract tests are wired into CI. The built160 native source matches
these changes; source receipts still reflect its pre-commit build. Next broaden
physical validation to multi-kart and Retro Rewind scenes before final packaging.


Root integration e43c208 pins Android51b4c45. All three CI checks pass, including
the new keyboard sanitizer test on Linux. RootPR315 and childPR2 now describe
the CP-summary and input changes,63 issue responses, and the inconclusive TLS
comparison. Both worktrees are clean. Code160 remains installed; the staff
replay/menu navigation is being exited for the next broader scene. No completed
player race or broader acceptance is claimed at this checkpoint.


### Replay-exit acceptance boundary (September 22, 04:01 JST)

After profiling160, touch Start opens the replay menu and Down/left-stick input
visibly selects End Replay. A subsequent short touch A returns selection to
Continue Replay without leaving the replay. This was observed repeatedly and
is not accepted as successful exit. Earlier controls were replaced in place
between captures, so their replay-exit behavior has not been established.
Next compare this exact operation on the earlier maintained baseline before
attributing it to either new optimization. Preserve this observation rather
than claiming broader input acceptance from successful main-menu navigation.
Private screenshots `input160-replay-exit-select.png` and
`input160-exit-selected.png` retain the before/after selection. Code160 remains
installed in that replay menu; no profiler or build is running.


### Replay-exit correction (September 22, 04:05 JST)

A12-second screen recording captures the full interaction: Start opens the
menu, three Down presses select End Replay, and A opens the confirmation
“Return to the course selection screen?” with No selected. Up then A returns
to Select Course on code160 (`input160-exit-yes.png`). The earlier screenshot-only
attempts did not establish an exit failure; the confirmation step was missed.
This corrects the previous unresolved interpretation. Exit is now physically
observed on the candidate, with no runtime patch needed.

A control161 was built while investigating, with the two new source changes
reverted locally during staging/build and then restored exactly to maintained
HEAD. Its native SHA256 is byte-identical to API28 control157:
`a408a49316dc5c7b596be2b40c3acf31c4c25396daed07d50df9ef03d19a26b3`.
APK SHA256 `d137425f75aa7aa6a0574314efeec390e9a3a2ecdee51faf1407223093872d03`.
Full build and package/profile/signer/symbol audits pass. It remains retained
and uninstalled; code160 is still on the phone. Source worktrees are clean.
The currently prepared tree contains161 control source and must be refreshed
from maintained HEAD before building another candidate.


### Touch-controlled 150cc movement check (September 22, 04:10 JST)

On code160, Original150cc Mushroom Cup/Luigi Circuit with Mario/Standard Kart
was entered via normal menus. A22-second recording shows the player initially
stationary in12th, then accelerating from the grid, collecting an item, turning
in response to floating-stick swipes, leaving the track and colliding with a
signpost. Acceleration lock visibly turns cyan and clears after a shortA press.
Start opens the race pause menu; Quit followed by Up/Yes/A returns to Main Menu.
No completed race is claimed. This is a movement/input/item/rendering check, not
a representative or controlled performance measurement; screen recording was
active and the player did not stay with the opponents. Video and exact injected
event times are retained privately as `input160-gp-movement.*`.

The existing private offline CPU-driver hook is the next repeatability gate.
Current extracted-production guard checks pass with ASan/UBSan: disabled mode,
12 mode values, every malformed/missing player slot, null/absent singleton; only
enabled offlineVS with the expected1-human/11-CPU lineup may write player-zero
type. This proves bounds, not that the fixture actually drives on hardware.
A private debuggable code162 build is in progress with the maintained candidate
native source. The fixture must be visually/log verified before measurements
are accepted and removed before returning to a normal build. No marker has
yet been enabled and code160 remains installed at Main Menu.


Code162 uses version `0.5.1-fullcpu-capture`, profileable1 and frame-capture1
(the script correctly rejected an initial name without the required-capture
suffix before building). It selects native configuration6q100252/API28 and is
rebuilding translated shards; the process is verified active. This package will
be debuggable for the private fixture and must not be mislabeled as a release
profiler. Retain exact symbols from that configuration and audit manifest,
signer and allocated sections explicitly. Do not reuse the API28 non-debug
configuration's symbols. No hardware installation or fixture activation yet.


### Private CPU fixture package and follow-up (September 22, 04:30 JST)

Code162 completed in9m28s. Its private debug audit confirms API28, target36,
shell profileability, expected in-place signer and exact allocated native
sections against6q100252 unstripped symbols. APK SHA256
`ce4bb79bc008d54fc29857b2517c50e86ef6feca6debbd2077275e449f526f0b`;
native SHA256 `f6dc5b43133579e62e8503c6094c83aebdaa37325c83312a26a7d725bbf1cace`.
The local audit initially rejected its own aapt2 spelling/namespace assumptions
(minSdkVersion and fully qualified android:shell); those checks were corrected.
The package had installed in place before that supplemental audit completed;
no fixture/game launch occurred until the corrected audit passed.
All7 preserved save/settings files are still byte-identical to the144 backup,
and a fresh private tar/readback was retained. No diagnostic enable marker
existed; onlyFullRaceCpu.enable was then created for this experiment.
Hardware fixture activation and driving remain unverified at this point.

#216 supplied the requested correct APK filename and installed119, plus a slow
download. Responded with the verified official asset URL/111,773,259-byte size
and a fresh-download/in-place-update check, without diagnosing corruption as
fact or requesting repeated logs. Reply:
https://github.com/chrissotraidis/kartpad/issues/216#issuecomment-5766243862


Code162 fixture acceptance failed: a25-second video shows the local Mario
stationary at the grid while opponents drive away; no full-race activation or
probe appears in its console transcript. Excluded from CPU-driving/performance
acceptance. The mode was Original100cc VS/Luigi Circuit. No completed race.
Code163 adds only private native enable/pointer logging to distinguish the
fixture launch flag from unavailable RaceConfig. Built in57s; exact signer and
allocated-section audit passes. APK SHA256
`4c331c5e28e171ee96301206014231aec7ee9e8776c3c4782665fdcca2c2e305`.
The private patch and artifacts are retained; maintained source was restored
exactly after build. The prepared tree still contains the private probe and
must be refreshed before a normal candidate build. Code163's launch transcript
confirms the flag equals1 and RaceConfig is nonzero, with mode0 at menus.
This narrows the probe on this launch; the162 activation discrepancy remains
unexplained. No CPU-driving acceptance yet.


### First verified twelve-CPU run (September22, 04:42 JST)

Code163 private instrumentation confirms flag1, nonzero RaceConfig and guarded
offlineVS conversion. A40-second video independently shows Mario driving
through corners, collecting/using a golden mushroom, position changes and lap2
with opponents present. Subsequent screenshots show lap3 and the normal results
table with all12 racers, Mario fifth. This is a completed CPU-controlled
Original100cc Luigi Circuit race, **not human gameplay**. The camera alternates
cinematic angles, so it is also not the ordinary player-camera workload.

After video recording stopped, a separate29.9516-second simpleperf capture
recorded4,447 samples,0lost, thermal status3 before/after. Five steady
intervals show median CPU14.544ms and FPS56.8 (53.52–58.96), compared with
this evening's lighter capped ghost workload. No cross-workload speedup claim.
Self-cycle shares: scalar clear7.79%, scalar capture5.90%, GX display list3.85%,
emulatedTLS3.62%, pthread_getspecific2.12%. Exact symbols match code163.
Private files: probe163-proof.mp4/contact, probe163-finish.png, cpu163-luigi.*.

Code164/API29 private debug TLS comparison initially failed to link an obsolete
private input-trace symbol from an older cached506165y6 object. Timestamp
preservation across different native configurations was unsafe here. All858
prepared regular files were touched and a full native rebuild started; no
failed/stale164 package was installed. Future configuration switches must
refresh source mtimes or prove that configuration's own previous source identity,
rather than copying timestamps from the most recently used different config.
The default API28 compatibility remains unchanged.


The same code163 fixture subsequently traversed Moo Moo Meadows100cc with
nearby opponents and reached the post-race Next Race/Quit menu. A20-second
video verifies the driving start; a separate89.9385-second profile has13,167
samples,0lost, thermal status3. Fifteen steady intervals have medianCPU14.943ms
andFPS55.93; CPU range14.069–21.577ms, FPS39.87–60.21. The two early slow
intervals had zero sampled queued pipelines, but newly created pipeline totals
increased598→599, so this is not a clean fully-warmed comparative run.
Self-cycle shares repeat the heavier pattern: clear7.42%, capture5.94%,
emulatedTLS3.27%, pthread_getspecific1.85%, GX display list3.01%.
Luigi profile clock attribution has no inactive-keyboard caller samples.
Code164 full API29 debug recompilation remains active in506165y6. No164
artifact/install/performance claim yet. Current device remains163 with the
FullRaceCpu marker enabled for ongoing private tests; remove it before normal
owner play. Saves/settings backup162 remains retained.


### TLS comparison preparation and new screenshot (04:55 JST)

Code164 full recompilation completed in9m11s, without the obsolete private
input-trace symbol or163 probe logging. APK SHA256
`c5e1ae598e75fe9f00b0395286693d42ea9508a7efab4af4eddf6ab80816ac5d`;
native SHA256 `2690dc048c631124790f3c5152f8e7529ab72963b885e6434dbfc9fb627b8231`;
BuildID `afd3a5570f1fdcd5ae7dab2191665de4678f38a6`. Private debug audit passes:
API29 manifest/native note,152TLSDESC relocations, expected signer and all
allocated sections matched to506165y6 symbols. An API28 code165 control from
the same source is now rebuilding with all prepared source timestamps refreshed.

A second163 Moo Moo Meadows90-second run completed with13,687 samples,0lost,
medianCPU15.927ms andFPS52.67 across14 steady intervals. Both thermal status3;
this differs from the first14.943ms/55.93 run, so small differences must not be
called a TLS improvement. Results table observed afterward.

#316 provided the requested screenshot. Browser visual inspection shows huge
displaced Mario-preview surfaces while menu text/icons remain intact. This
confirms model geometry corruption rather than simple aspect stretching.
Acknowledged without a repeat screenshot/settings/log request:
https://github.com/chrissotraidis/kartpad/issues/316#issuecomment-5766561305

### 05:15 JST — API 28 control and an audio TLS candidate

- Fresh code 165 uses exactly the same native and symbols bytes as code 162. Its already-present private FullRaceCpu marker activated correctly this time. The Original 100cc Mario/Standard Moo Moo Meadows capture visibly advanced from course intro to lap 2; this remains a CPU-controlled fixture with cinematic cameras, not human gameplay.
- `cpu165-moo`, 90 seconds: 17 retained diagnostic intervals, median CPU 14.383 ms (14.072–15.818), median FPS 60.04 (49.91–60.44), thermal status 1 before/after. The preceding API 29 code 164 was thermal status 2, and code 163 status 3: these are not matched thermal controls and do not establish a TLS-model win. This capture began during course intro, earlier than code 164; the six-second exclusion does not make their race phases identical.
- Address attribution from code 164's TLS resolver samples points most frequently to `Accelerator::ReadSample` at its sample-byte fetch (217 samples) and ADPCM header fetch (15), ahead of individual scalar helper sites. Inspection found the inline byte accessor resolves a static thread-local ARAM window per byte.
- A 13-line experimental patch retrieves that same thread-local window once when a stack-local voice accelerator is constructed. It retains per-byte range and generation checks, the same page resolver and single-byte fallback, and the same cache shared across sequential voices on a thread. No audio math, memory mapping, thread ownership, or API baseline changed.
- New `scripts/test-android-aram-window.py`: 786,432 production sample/output-state comparisons against uncached reads passed ASan/UBSan across formats, loop/stream settings, boundary addresses, partial-page fallback, and mapping-generation changes during a voice. Checks also confirm separate windows across threads and reuse across sequential voices. This is semantic fixture evidence, not an audio-quality or performance claim.
- Code 166 API 28 private debug/profileable build is running with the experimental audio change. Acceptance requires exact package/symbol audits and physical profiling; the change is not yet committed as accepted.
- Code 165 recording completed 89.9524 seconds, 13,191 samples, zero lost. A later screenshot shows the completed 12-racer results table, Mario fifth. Its TLS attribution independently identifies sample-byte/header fetches (107 and 8 samples); code 166 therefore targets a hotspot observed in both API baselines.
- The code 165 repeat uses a fixed 20-second delay after the course-start navigation helper finishes. Its before screenshot shows race time 00:04.549, lap 1, Mario sixth. `cpu165-moo-repeat`: median CPU 14.649 ms (13.943–17.703), median FPS 58.02 (44.23–60.03), 15 steady diagnostic intervals, thermal status 1 before/after. Use this capture timing for code 166, with additional repeats if the effect is within variation. Experimental patch SHA-256: `fe4e90fbc73494ba43458618d2f338388c0209ff521ccc5d246a90bed79ca75b`.
- Live issue refresh remains 63. The only timestamp change since 04:48 is the already-recorded maintainer reply on #316; no new reporter comment is awaiting response.

### 05:24 JST — audio candidate built and audited

- Code 166 (`0.5.1-aram-capture`, API28) built successfully in 9m02s. Package audit and the private debug/profileable audit passed: expected signer, version, minimum/target SDK, allowed package contents, and exact allocated-section match to retained unstripped symbols. Installed in place successfully after code 165 returned to Main Menu.
- APK SHA-256 `831ae711159ee23576b8444d43409ff337acfb94d8eba7900cbf78ae8f08a9bb`; native `e7280bf77a2d072fe94cd9f4c28151cfa73ceeca656366ebc9fabd3266c7a3d3`; symbols `d7cef72543d87fefc24eac36d19435b0d199016f6538ea326ffaa103c3e68e23`.
- ARM disassembly of `Accelerator::ReadAram8` shows the control's `bl __emutls_get_address@plt` is absent in code 166. Both retain `ResolveAramWindow` and `ReadAramByteSlow`. Inspecting only `ReadSample` would miss this: it calls the separate byte accessor in both builds. Physical comparison remains pending.
- The code 165 repeat completed to its twelve-racer result table (Mario fourth, +8 points), then returned normally to the main menu. Its 89.9745-second profile recorded 14,386 samples and zero lost.
- First code 166 comparison (`aram166-moo`) recorded 89.9323 seconds, 13,498 samples, zero lost. Start screenshot: race time 00:03.894, lap 1, Mario tenth; after screenshot: 01:29.587, lap 3. Median CPU 14.7135 ms (14.191–17.835), median FPS 54.195 (38.96–60.22), 16 steady intervals, thermal status 1 before/after. This is not an overall timing win versus code 165 repeat's 14.649 ms / 58.02 FPS.
- The intended local effect is independently present: TLS samples attributed to `Accelerator::ReadSample` dropped from 172 (1.453 billion sampled cycles) in code 165 repeat to zero in code 166. Overall emulated-TLS/get-specific shares were 3.31%/1.90% versus 2.70%/1.65%. No audio queue telemetry appears in these logs, so they cannot establish underrun/audio-quality acceptance. A repeat remains required before retaining the candidate.
- First code 166 run reached the post-race results animation, then normal course selection. Per-thread sampled cycles were 14.199 billion for `KartPadAXMix` in code 165 repeat versus 12.706 billion in code 166; changing race events/voice activity and CPU frequencies prevent calling this an isolated audio speedup. A second code 166 Moo Moo Meadows capture is running with the same fixed start delay.

### 05:35 JST — retain bounded audio overhead reduction

- Code 166 repeat: 89.9326 seconds, 13,662 samples, zero lost; start screenshot 00:04.572/lap1. Median CPU14.466ms (13.891–17.841), FPS57.865 (42.98–60.21), 16 steady intervals, thermal status1 before/after. Per-sample audio TLS attribution is again zero. The two candidate CPU medians bracket the14.649ms control, and do not establish a general frame-rate gain.
- Retained the13-line change as Android runtime `7560a3b`: correctness fixtures, preserved cache ownership/invalidation, actual ARM call removal, and repeated physical removal of that overhead support the narrow optimization. No audio arithmetic or guest floating-point semantics changed. Human audio-quality and other-device acceptance remain unproven.
- Rechecked the actual native compile commands: runtime unity groups already compile with final `-O3`, as does the scalar-flag source. A missing release optimization level does not explain the remaining cost; no speculative global compiler-flag change was made.
- Root `fbf95d9` pins runtime `7560a3b`; both review branches are pushed and PR descriptions updated. All three CI jobs pass at that root head (boundaries, receipts, regression).
- Code 166 repeat reached the normal Next Race/Quit screen and returned to Main Menu. The app's Return to KartPad Menu → Use on Next Launch → close from Recents → reopen flow successfully launched Retro Rewind's title screen without reinstalling or clearing data. On this rotated Pixel Recents UI, a leftward swipe dismisses the card; the initial upward swipe merely moved the card. Process absence was verified after dismissal. Retro title launch is not yet Retro race acceptance.

### 05:55 — Retro CPU fixture completed; normal candidate built

Private code 166 completed Retro Rewind offline VS on Rooster Island, 200cc, Yoshi/Mach Bike/Manual. Screenshots showed the moving race at 00:04.753, lap 2 at 2:02.841, lap 3 at 2:56.669, and then the Next Race/Quit Game screen. Quit returned to the Retro main menu. This was the explicit debug CPU-controlled fixture, not human driving. The 89.9419-second profile recorded 12,366 samples, zero lost; 17 post-warmup intervals had median CPU 14.488 ms (14.015–14.749), median reported FPS 60.01 (58.98–60.20), thermal status 1 before/after. Per-sample audio TLS callers remained absent. There is no matched Retro control or claimed FPS improvement.

Normal code 167 (`0.5.1-evening`, API 28, debug/profile/capture disabled) built successfully in 8m59s. Full RVZ picker acceptance remains in progress: a local Dolphin CLI was built from existing research source, but its direct WBFS conversion asserts because WBFS size is an upper bound. The existing nodtool converter is being used for the intermediate ISO instead. All conversion inputs/outputs remain private.

Before the normal install/import, seven current save/settings files were backed up and read back byte-for-byte. Both game saves changed naturally during these completed VS fixtures; five preferences were unchanged from the earlier backup. The old saves were not restored. Our FullRaceCpu.enable marker was removed.

Normal 167 package audit passed, with exact allocated-section match to retained symbols and the existing private install signer. APK SHA-256 `0ffc47d633577460f892a92a7f9df8e0a40f4df36b5f6513a29f783c62d9b606`; native `c5ded75b90367aedba27b66a67c1ec3f04377348190c177913213be2470d64a0`; symbols `92597108fbc654065828fb4953f950da9bd37b1b2ae415be9020bbfba59f1a09`. Manifest independently confirms non-debuggable, no shell profiling, API 28. This private-signed package is not a public release.

The full private RVZ test image was successfully generated via nodtool ISO conversion followed by Dolphin Zstandard level 5 / 128 KiB RVZ conversion. Header reports RMCP01, PAL, revision 0. The image is 2,613,096,212 bytes and was transferred to the attached phone. The WBFS-derived ISO is not a Redump match; acceptance here is the project's supported DOL/REL identity, not a clean-disc preservation claim. Full Android import and post-import checks remain pending.

### 06:07 — Full RVZ picker/import acceptance

On private code166, selected the full 2.61 GB Zstandard RVZ through Android ACTION_OPEN_DOCUMENT. The app displayed Game Data Imported. All 2,043 extracted files match the previous working GameData hashes exactly, with no additions/removals/changes. Both current saves and all five backed-up preferences read back byte-identically after import. Private evidence: `rvz166-import-progress.png`, `rvz166-gamedata-comparison.json`, and preservation166's RVZ readback receipt. Thus the full-game picker boundary is now passed on this Pixel; this does not establish other device/provider support or reduce extracted storage. [Reporter update](https://github.com/chrissotraidis/kartpad/issues/314#issuecomment-5767498720). Normal code167 in-place installation is next, after the removed CPU-driver marker and verified current backups. All three CI checks pass at root7691054.

### Normal code167 post-import launch and input checks

In-place install succeeded; installed package reports code167/version0.5.1-evening/API28 and no DEBUGGABLE flag. Original loaded the existing licence, main menu, character/course selection and Luigi Circuit100cc VS. A bounded touch-input check moved Mario from the grid (00:00.963) to the first turn with an item (00:09.927), then off-track (00:12.432); pause and Quit returned to Main Menu. Acceleration and pause are verified, not successful steering or a completed player-driven race. Gas lock was cleared before pausing. The default player camera confirms this is distinct from the debug CPU fixture.

Return to KartPad Menu, select Retro for next launch, dismiss from Recents (verified no runtime PID), and reopen successfully reached Retro title and the existing licence's main menu on normal167. No online mode was entered. The seven-file exact readback occurred after RVZ import while166 remained debuggable; after167 installation normal app loading is evidence, not another shell readback claim. No AndroidRuntime/KartPadDiscImport errors were returned by the bounded tag check. All three CI jobs pass at a5019dd.

The derived4.38GiB intermediate ISO and this test's phone RVZ copy/folder were removed after successful import and comparison; original WBFS and local RVZ/receipt remain private. No owner data or previous artifact was removed.

### 06:16 — Remaining scalar path review and new reporter acceptance

Inspected the exact code167 ARM implementation of FinishScalarFp (about3% sampled self cycles in the heavier fixture). It already branches directly around exception summary/enable work when exception==0. An extra C++ zero-exception fast path would duplicate an optimization already present in the artifact and is rejected without another build. Clear/Capture helpers already skip redundant FPSR writes while preserving unrelated QC state and keep opaque ordering boundaries; removing those boundaries is not a semantics-neutral quick fix. No scalar source change made. The review uses retained machine code, not source appearance alone.

New #216 reporter reply confirms code135 re-download/install and Original startup on A9+; remaining missing-body geometry and lag are retained. Replied with accepted subcase and no repeated evidence request. Latest inventory still63 open.

The remaining memcpy/memmove samples were attributed with the exact166 symbols: 155 samples had a libmain caller, of which107 were draw vertex/index/array staging paths. Array uploads already reuse unchanged backing data/size/endian state; explicit guest vertex-cache invalidation clears those ranges and breaks merging. No unsafe copy-elision change was made. This is sampled attribution, not a measured avoidable bandwidth cost.

Normal167 Retro loaded Rooster Island200cc VS with the player camera, Yoshi/Mach Bike/Manual. Short touch acceleration moved from the grid at00:28.037 to a wall at00:36.582, then gas lock was cleared and the game paused. This is a movement/control smoke check, not successful course navigation or a completed race. Backgrounded through Android Home for61.34seconds; the runtime PID survived, foregrounding restored the same pause menu, Continue resumed the game timer (00:42.667), and Start paused again. This verifies one normal-build lifecycle cycle.

### 06:35 — Bounded profile-derived function placement experiment

Normal167 source passed all three CI jobs at fcae362. Built profileable, non-debuggable API28 control168 from the same source; its packaged native hash is byte-identical to167. This changes profiling access/version identity only. Installed168 in place on the same signer; owner data was not cleared.

Derived a private512-symbol order from our exact166 Original Moo and Retro Rooster profiles:17,330 native samples mapped to function ranges,470 did not. Replayed the existing native link command with an ordering file and separate output/dependency paths. All512 selected functions moved; common function sizes remain identical. Symbol-name differences are exclusively linker-generated Cortex-A53 workaround stubs. This proves layout changed, not performance improved. The ordering file and translated symbols remain private.

The first169 package attempt reused Gradle's old merged-native intermediate; the exact allocated-section audit rejected it before installation. Retained that rejected artifact separately, then rebuilt the private ZIP with the ordered/stripped native library,16KiB alignment and the same local debug signer. Corrected169 passes non-debuggable/profileable/version/signer and all-allocated-section symbol matching. The normal native build output was restored. This manually packaged experiment is not a public release artifact or a source-default change; device comparison remains pending.

layout168: APK `3a3ef20cc4baff302c78a68c6aa90a3a42191a20ec4e0332549ebb6fceb8b6e6`; native `c5ded75b90367aedba27b66a67c1ec3f04377348190c177913213be2470d64a0`; symbols `92597108fbc654065828fb4953f950da9bd37b1b2ae415be9020bbfba59f1a09`.

layout169: APK `848a51913c5681e3b81d79752bf94aa1dfe60b8709cf4df17faab2c7aa45496b`; native `b5e8f6bbc83e63d7bde8c9cfba1c63a87a92306a05c35723745c2af3fe7b872f`; symbols `f19087028571e7bf5b3e591a5c637f17f4c2ba911c25652142c541c64ab64d2c`.

Static follow-up: all19,702 dynamic export names are preserved. The512 ordered functions occupy760 distinct4KiB address pages versus1,139 before; top16 occupy9 versus23. These are static layout counts, not measured cache misses or performance gains. Private package comparison finds changed manifest/version-bearing DEX/profile, native library and signing metadata; game/runtime assets are identical.

Control168 Luigi Circuit staff replay:90.0045seconds,12,063 samples,0lost,17 post-six-second-warmup intervals. Main-thread CPU median12.673ms per present(range11.951–12.814), FPS median60.02(range59.07–60.31), thermal0→0. Screenshots show the staff ghost moving around the course; no manual driving claim. Ordered169 comparison pending. Fresh issue snapshot remains63open with no new reporter update since the addressed#216 reply.

Ordered169 Luigi staff replay:90.0192seconds,11,846 samples,0lost,16 post-warmup intervals. CPU median12.684ms(range12.167–12.866), FPS59.96(range59.06–60.34), thermal0→0. Before/during/after screenshots show the same staff ghost/course and no obvious geometry failure. This first matched-workload pair is effectively unchanged from168(12.673ms); no layout default is retained, and no cache-miss/FPS improvement is claimed. Further layout work needs a stronger representative profile and repeatable benefit, not just denser addresses.

Documentation audit found android/README.md still presentedv0.4.17 as current. Live release lookup confirms publicv0.5.0; the older build recipe is now explicitly historical rather than silently substituting newer dependency inputs. One launcher import hint omitted RVZ while the detailed import help included it; the candidate label now lists ISO/WBFS/RVZ. A new normal package will validate that UI-only edit; native runtime remains unchanged.

Normal170 with the corrected RVZ hint builds and passes package/signer/allocated-section audits: non-debuggable, shell profiling disabled, API28. APK `638acca411e30b0c03ed6a51160f513333dbdbaba99f4f94cedaa224bada8fa5`; native `c5ded75b90367aedba27b66a67c1ec3f04377348190c177913213be2470d64a0` (identical to167); symbols `92597108fbc654065828fb4953f950da9bd37b1b2ae415be9020bbfba59f1a09`. Not installed yet; phone remains on169 while checking the replay-exit uncertainty.

Replay-exit recheck on169: Start, select End Replay, A opens a Yes/No confirmation defaulting to No. One bundled Up/A attempt returned to the replay menu. Repeated with separate observation after Up: screenshot verifies Yes highlighted; the subsequent A returned to Time Trials course selection. Therefore the earlier160 input sequence did not establish a runtime exit defect. No code fix is attributed to this successful UI navigation, and no controller-report acceptance is inferred.

### 06:55 — Live issue-reply audit and remaining feature assessment

Read all63 linked comment IDs back from GitHub:63 exist, all belong to their
intended issue, all have nonempty bodies, and all are authored by the maintainer.
This verifies publication/association, not issue resolution. Installed package
reports normal170/API28/0.5.1-evening without DEBUGGABLE, and both profiles remain
Ready to play. Exact package audit already confirms shell profiling disabled.

The initial shake/ghost investigation items now have an explicit
[feature follow-up](feature-follow-up.md) based on current app code, the iOS
motion implementation and a pinned retained rr-pulsar research checkout. Neither
is a simple switch to existing input/save paths. Settings copy now correctly
states that Retro ghost transfer excludes original Wii courses played in Retro,
not only custom tracks. No extra reporter data was requested.

### 07:03 — Installed artifact identity and remaining scalar cost

Read the installed base APK through ADB and hashed the bytes without retaining
another APK copy: SHA256 exactly matches normal170's audited
`638acca411e30b0c03ed6a51160f513333dbdbaba99f4f94cedaa224bada8fa5`.
All three CI jobs pass at eff41eb. Normal-build replay observation is live;
its six-minute checkpoint has the same process and thermal status0.

Reviewed the generator/runtime scalar-context boundary against exact166 TLS
caller attribution. Multiply/add/subtract account for63/34/22 observed TLS
samples in the heavy Moo repeat. Wrappers already reuse their resolved pointer
within an operation; eliminating the remaining lookup requires passing the
existing generated-function context through the helper interface, preserving
validation and FP semantics. A concrete next experiment is recorded in the
Android handoff. No incompatible generator/runtime change was slipped into170.

Normal170 source provenance: root build revision
`06970877194e1d1b11b5523e2baa63e87c442b24`, maintained Android runtime
`7560a3be16f15633f048db3e5c3be7b90721d93f`. The build log verifies that prepared
runtime revision and the pinned dependency digests. All subsequent root changes
through1809655 are documentation only. The native payload also matches167
exactly, confirming the rejected function layout is absent from the installed
normal package.

### 07:09 — Normal170 Original extended observation

Ten-minute staff-replay observation completed600.004seconds with11 minute
checkpoints and the same process throughout. Thermal status was0 at all
checkpoints. PSS varied1,950,876–2,094,084KiB and ended2,065,722KiB; this is not
a leak-free claim. The retained main log covers07:04:20–07:06:57, not the whole ten-minute
observation; an earlier system-buffer entry does not extend main-log coverage.
It contains32 CPU/cadence intervals: CPU median12.6975ms(range11.394–13.074), FPS median60.015
(range46.11–60.62). Two intervals fell below55FPS(46.20 and46.11), with
p99 frame times125.52/129.76ms and no queued pipelines. Their cause was not
isolated; these tails remain visible rather than being called uniformly smooth.
No fatal-exception/signal, CRITICAL, runtime-fatal or device-lost matches occurred
in the bounded log. Periodic screenshots show the staff ghost/course; no
continuous visual, manual-driving, audio-quality or comparative speed claim.

Sent Android Home while replay was running, waited61.49seconds, and returned.
The process survived and the screenshot shows replay rendering again. This is
an additional normal-build lifecycle cycle after the earlier paused Retro check.

Normal170's DiscIO JNI library is byte-identical to the library that performed
the full RVZ import on166:
`2e330c3c80095c0df393416e276fd317d8c8cad026c58ce64cccd7c3913a5286`.
SDL3 and libc++ also match between those packages. The game native library differs
because166 was the debug-fixture build; normal170 instead matches normal167.
This carries the exact tested importer into the final package without pretending
the full import was repeated after disabling debugging.

At07:16, normal170 successfully loaded Retro's existing licence and selected the
Rooster Island150cc staff ghost(blarn., Bowser,02:42.292) through Replay. A separate
ten-minute normal-build observation is running. This is staff replay playback,
not a player-driven time trial or a Retro ghost-import/export test.

### 07:28 — Final observation and acceptance

The eight-hour threshold passed at07:25:19 JST. Retro observation finished
600.004seconds,11 checkpoints, same process and thermal status0 throughout.
PSS ranged1,730,694–1,794,866KiB. The selected staff replay reached its
02:42.292 result; checkpoints180 onward display the results overlay while the
course scene continues animating. This is not ten minutes of active racing.
The game displayed a ghost-created message; no final non-debuggable save
readback was possible, so this session is not claimed to leave saves unchanged.
The retained main-log tail starts07:23:49 and contains no fatal-exception/signal,
CRITICAL, runtime-fatal or device-lost matches. That bounded tail does not prove
absence of all earlier errors or leak-free operation.

Returned through KartPad's menu, dismissed the task through Android Recents,
verified the old game process exited, then relaunched the selector. Both
profiles show Ready to play and Ask Every Time remains selected. No game-data
clear, uninstall, save restore or online session was performed.

Final GitHub refresh still contains the same63 open issues, with no changed
issue update timestamps since the previous refresh. All63 replies were read
back earlier. Live main remains0d657f3. Both draft PRs remain open, Android's
pinned head is7560a3b, and all three CI checks pass at3da4b24. Final changes
following that checkpoint are documentation only. The normal170 build and its
exact symbols remain private in the retained worktree; source is pushed.
