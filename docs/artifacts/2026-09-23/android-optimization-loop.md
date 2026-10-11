# Android stutter optimization loop

Completed window: September 23, 2026, 00:15–08:15 JST. Optimization stopped
at the authorized deadline. The existing stabilization worktree retains the
reviewable source and private artifacts; the dirty primary checkout and RC2
artifacts are preserved. No release was published. See the
[morning report](android-morning-report.md) for final acceptance and limitations.

## Initial evidence

Attached Pixel still has RC2 code175. Initial system logs were captured before
any restart, but had rolled past the game session. Exported the latest retained
app session through Help → Export Private Diagnostics, without uploading it.
Private archive latest-session7035.zip passes ZIP integrity. Evidence is under
work/android-optimization-20260923. Renderer validation was visibly Off.

The retained session has16 frame diagnostic intervals: median reported FPS
59.6575, minimum21.229, maximum sampled frame188.354ms, four intervals with
sampled frames over50ms. All16 report zero queued pipelines. The slowest interval
(present1800) reports p95=117.357ms and p99=176.522ms. This proves uneven reported
cadence, not the scene or its cause; loading/menu transitions must be separated
from active gameplay before comparison. Startup prewarm finished in0.7s with
303/303 Dawn blob hits. Resolution setting2x. No performance improvement claimed.

## Next cycles

1. Preserve the preceding retained session (PID2947) as well; correlate scene
transitions in logs and owner feedback. Keep private identifiers out of docs.
2. Review pinned DriftDroid audit in the primary checkout at
docs/artifacts/2026-09-20/driftdroid-audit/REPORT.md. Refresh upstream changes;
do not redo already integrated local-binding/cache/audio-TLS work or promote
inconclusive API29 experiments as wins.
3. Investigate long-frame causes as well as average CPU. Prior loop's normal170
replay showed125–130ms tails despite empty shader queues. Inspect timing, cache
maintenance, background work, logging and presentation, and capture attributable
thread/scheduler data where feasible.
4. Test a bounded source optimization with semantic regression coverage, then
compare the same scene/settings and thermal state. Scalar helpers still resolve
CPU context per operation; passing the existing generated context is an untested
candidate, not permission to weaken FP semantics.
5. Build/install only signer-compatible in-place candidates, preserve data, and
record exact source and artifact identities. Distinguish title, replay, stationary
race, driven race and user acceptance. Update this ledger after each cycle.

Morning report must separate measured gains, rejected hypotheses, remaining
limits and what is actually installed. Do not keep working past08:15 without
renewed instruction.

## 00:25 — Scene attribution and first scalar candidate

The188ms interval overlaps Scene Exit / Scene Restart, with the pipeline-created
count increasing206→383. Thus zero queued pipelines at the reporting instant
does not exclude compile stalls. Worker overlap encoding's interval maximum is
443.486ms. Separate transition/loading evidence from steady gameplay before
assigning a cause. Later sampled hitches of58.969–85.807ms also remain.

Live GitHub API confirms DriftDroid android-port still resolves to the audited
d12ccb522667716a4a25a3c4a03e72f1dee85588. No new upstream optimization was found.

Added an experimental explicit-context overload to14 Android scalar helpers,
retaining existing call signatures and the exact null/guest-stack validation.
The overload uses the supplied context rather than Android emulated TLS.
Arithmetic evaluation and FPSCR/writeback semantics are unchanged. Changes are
currently uncommitted in vendor/runtimes/android; no game candidate uses them yet.
The differential runner accepts --explicit-context and passes the caller context
into both baseline/candidate adapters (baseline ignores it). On the physical Pixel,
two concurrent runs each passed224,000 cases covering random/edge values, four
rounding modes, FPSCR, host flags, destination-write decisions and nested context
restoration. The tiny add benchmark favored the candidate in all six alternating
pairs, but large clock warmup drift prevents a reliable speedup estimate. This
is not a game-FPS measurement. The first compile attempt found a missed benchmark
call-site signature update; corrected before the successful run.

A follow-up edit removes redundant validation in the legacy wrapper by forwarding
TryGetCpuContext() to the validating overload; rerun the adapter tests before
building. Next: prove generated caller context validity, integrate explicit calls
through a reproducible translator/candidate path with cross-platform compatibility,
and run a matched game measurement. Do not edit prepared RC2 source in place.

The follow-up adapter rerun passed another448,000 cases on the Pixel. Benchmark
warmup drift remains substantial and one alternating pair favored baseline; no
percentage improvement is asserted. Both root and runtime diff checks pass.
Installed game remains RC2 code175; the experiment has only run as a standalone
/data/local/tmp executable and has not touched app data.

## 00:35 — Reproducible generated candidate

Translator project setting explicit_scalar_context is opt-in and defaults false;
the CLI propagates it into14 supported scalar adapters. Default/Apple generation
remains unchanged. Full generation initially caught a state-free ABI violation: a
clone without a ctx parameter retained the new argument. Fixed by retaining legacy
adapters for functions selected for state-free clones, with a regression fixture.
This leaves those functions as a later optimization target rather than weakening
the ABI guard. All671 translator tests pass, including the added boundary test.
Two reflection-based test callers also needed the new private parameter supplied.

Separate private/android-context-20260923 graph generation succeeds for Original
and Retro. Base output contains45,164 explicit-context calls in3,367 functions.
Retro module output has zero: its separate emission path still uses the legacy
policy. Both profiles execute base code, but this is not a claim of optimizing all
Retro module arithmetic. Do not lose that scope in later documentation.

Code176,0.5.1-context.1, profileable release candidate build is running via unified
exec session89927; log work/android-optimization-20260923/build176.log. Runtime
source build/android-context-20260923/runtime; generated graph above. An initial
build tried to rebuild DiscIO from a dirty third-party checkout and stopped; the
retry explicitly uses the retained evening-20260921/discio-jni library, as RC2
did. No third-party dirt was reset. This build is not installed yet.

Reclaimed10,036,380,256 bytes by deleting only4,716 .o files from six explicitly
identified inactive old .cxx caches. Preserved every library/package/symbol/source
and the RC2 object cache; file receipt is private. No native compiler was active
before removal. Available space increased12→21GiB.

Exported previous session2947 through the app; preceding-session2947.zip passes
integrity. Its largest984ms sampled stall overlaps289–804ms socket ioctl waits
during WFC requests. Across328 samples,305 have no logged scene/network event or
newly-created pipeline in the corresponding log interval; their worst sample is
57.63ms. This filtering is indicative, not reliable scene identification or proof
of zero network work (network logging is capped). Private cadence JSONs retain
all events and samples. Current installed game remains175.

## 00:48 — Reddit intake and physical replay baseline

Reviewed the supplied first-Android-community-release Reddit comments. These
reports lack exact package versions and are mostly 9–15 days old; they are
investigation leads, not confirmed regressions in code175.

| Report | Current disposition / next evidence |
| --- | --- |
| Poco X6 Pro: 40→20fps on later play; restart sometimes helps; 1–3x similar | Prioritize sustained CPU/thermal/pacing capture across repeat workloads; cannot diagnose another chipset from Pixel results. |
| OnePlus Ace 3: 60→40fps after one race | Same sustained-performance investigation; include transition and thermal evidence. |
| Retroid Pocket 5: Retro below60 even actively cooled | Cooling alone is not sufficient explanation; compare CPU/render costs and preserve accurate FP semantics when comparing DriftDroid. |
| Resolution change freezes until pause/resume | Reproduce current shell lifecycle and resolution change independently of scalar optimization. Settings are consumed on runtime thread; review render target/surface synchronization next. |
| Ayn Thor / Pocket 6 fullscreen and status bar | Current Activity already hides system bars on focus and exposes aspect modes; verify on available phone, avoid claiming those handhelds fixed. |
| Trigger/D-pad/stick button mapping; Shield stick behavior | Current UI advertises button/D-pad/trigger remapping; sticks and Start remain direct. Audit remaining source inputs before promising parity. |
| Fold startup/geometry report | Unreproduced, device/build unspecified; do not infer generic shader fix. |
| Old Retro import and compressed-disc confusion | Check current in-app download/import guidance; do not reproduce links to unauthorized game downloads. |

Code175 physical baseline: selected the existing Original profile, Time Trials,
Luigi Circuit, Watch Replay, and the built-in Nin★sato staff ghost. Screenshots
at30/60/90/120 seconds and stable process identity accompany a122.5-second capture.
This is an observed staff-ghost replay, not a manually driven race or multiplayer
acceptance. No profile was created. Resolution remained2x.

Private evidence: work/android-optimization-20260923/baseline175-replay1/.
24 periodic timing reports; excluding the initial three startup reports leaves21:
median reported FPS59.97, minimum59.74, median reported p99 window21.70ms,
maximum sampled worst29.05ms. These are periodic last60-frame windows, not
whole-session quantiles. Capturing screenshots can perturb presentation; candidate
comparison must use the same observation method. Thermal service status is0 in
both snapshots, but cached sensor values repeat exactly, so they are not proof
that temperature stayed constant. This light track does not reproduce the user's
worst stutter and cannot establish that the build is generally smooth.

## 00:54 — Current resolution lifecycle check and candidate176

On code175, switched2x→1x during the Luigi Circuit staff replay and observed30s,
then switched1x→2x and observed another30s. Same process remained alive and frame
counters advanced at the selected resolution in both captures. No persistent
freeze or pause/resume recovery was observed. The first transition included a
sampled57.84ms spike. This does not settle reports on other GPUs/builds. Restored
the original2x preference before candidate comparison. Source already queues
resize work to the render worker's ordered frame boundary.

Candidate176 build succeeded in17m56s. Package audit passes (API28, arm64, release
non-debuggable, expected identity/version and package-content rules). SHA256:
90da13fb1b93b349e2b213ba71d60d567d795c315e2ea9dd910f21e9e959bda0.
Private artifact and unstripped symbols copied into work/android-optimization-20260923.
Pulled the actually installed175 APK and verified its signing certificate matches
176 before starting adb install -r. No uninstall/clear-data operation used.
Private app files remain inaccessible on the non-debuggable package, so this is
an in-place package-preservation procedure, not proof from before/after file hashes.

Install176 completed successfully. Fresh package inspection confirms176 /
0.5.1-context.1; launcher still reports both Original and Retro Ready to play.
Original launches to the rendered title screen with the retained FPS overlay.
Next: enter the existing license and reproduce the same staff replay, collect
candidate timing/CPU profiles, then build a profileable control using legacy
call generation for a matched comparison. RC2 prepared source is intentionally
unchanged and cannot pass current stage verification after maintained source
edits; do not bypass that guard or overwrite it. Use a freshly staged control
source with the current additive helper API and a legacy-call graph to isolate
the translator optimization. Candidate176 private symbols are preserved.

## 01:01 — Candidate replay and matched control underway

Candidate176 opens the retained Original license and completes the same120-second
staff-replay observation with stable process identity. Median sampled FPS59.96,
median reported p99 window21.99ms, sampled worst57.52ms, median main CPU time per
present13.369ms. Code175 values were59.97 /21.70ms /29.05ms /13.3315ms. This first
comparison shows no measurable benefit; candidate had a larger sampled hitch.
Conditions are not thermally matched and screenshots disturb timing, so neither
a regression nor a win is established. The hitch interval includes118.345ms
maximum presentation call and116.245ms worker sealing wall time, while the main
CPU interval falls to11.604ms/present: continue investigating waits/scheduling,
not just arithmetic throughput.

Control graph generated with explicit_scalar_context:false using the same current
translator. Compared all29,637 base C++ files: after removing the45,164 explicit
context arguments and normalizing generated state_free_result temporary names,
there are zero remaining differences and identical filenames. Fresh control
runtime uses identical maintained source (including additive adapters). Code177
profileable release build is live, exec8121, log build177.log. No overwrite of
RC2 prepared source or source-verification bypass.

Separate30-second profileable-app CPU-cycle sample of176 replay succeeds:
17,151 samples, zero lost. Kernel symbols restricted; did not alter security
settings. Private data and report saved under work/android-optimization-20260923.
Top self costs include display-list processing and scalar flag clear/capture;
explicit-context Fmuls/Fadds appear in the installed native profile, confirming
that the candidate path is executing. Do not equate sampled shares with total
runtime savings. Matched control profile is still required.

## 01:12 — Actual compositor pacing evidence

Captured a30-second Perfetto trace using the app's existing trace scopes plus
scheduler/frequency/graphics events. Official trace_processor v58.2 wrapper from
https://get.perfetto.dev/trace_processor; local analysis, no upload. The64MiB ring
wrapped, overwriting7,589,888 bytes; retained trace covers27.13s. Largest retained
worker-overlap scope15.161ms, no repeat of the large hitch. Main thread21.53s CPU,
worker5.94s, presenter2.46s across the retained interval. Main runnable-delay max
2.878ms; worker9.599ms; presenter6.975ms. Generic frame-timeline table does not
include app surface entries, so do not use its1513 system entries as game frames.

SurfaceFlinger --latency for the observed native BLAST SurfaceView yields actual
presentation timestamps. Completed60-poll capture without screenshot/simpleperf
records a283.279ms gap plus two~50ms gaps. The corresponding private log interval
has127.378ms worker-seal max and128.817ms present-call max, with no new pipeline
count. FPS overlay's later last60-frame window still reports60.09, demonstrating
why sampled FPS alone misses visible hitches. Polling overhead is not ruled out;
next capture should correlate a hitch with scheduler/render trace and repeat on
control177. Retain all raw evidence privately. Do not claim a proven root cause.

## 01:18 — Correlated hitch and control177

A65-second trace with192MiB buffer has zero overwritten bytes or reported parser
errors. Concurrent SurfaceFlinger sampling catches another283.401ms gap. Converted
SurfaceFlinger CLOCK_MONOTONIC timestamps into trace CLOCK_BOOTTIME using the
trace's clock_snapshot table (offset265893117116021ns), rather than aligning the
raw clock values directly. During this event QueuePresentKHR/queueBuffer waits
about127ms, with a GPU-completion wait128.4ms and render-worker seal wait120.8ms.
The preceding worker encoding scope costs57.8ms. This supports a GPU completion/
presentation stall; its initiating cause is still unknown. Main-thread CPU-only
optimization does not explain or resolve the full event. Private SQL and output
are saved as trace176-hitch-boot and trace176-long-slices.

The independent no-trace compositor capture, excluding initial historical ring,
contains3336 unique presentations over58.979s (56.55 presentations/s),189 intervals
above25ms, three above40ms. The concurrent-trace capture records55.12/s,270 above
25ms and four above40ms. Profiling perturbs the latter, so do not compare them as
build variants. Both show that app-side successful Present calls do not imply
60 visibly distinct frames each second.

Control177 compiled successfully in15m51s; package audit passes and private signer
matches176. SHA256 c90f16c0b8b53b35390984fd002be3c4d4c1bbaac71b4c2aa3ca96268e5ed92b.
Preserved APK and native symbols; CMake cache2v4r5e2j. Same-signer in-place install
is running, exec40445. Next verify install then repeat Original staff replay,
simpleperf and compositor capture on control with equivalent warmup/settings.

Control177 install returned Success; package readback confirms177 /
0.5.1-context-control.1. Started launcher for next measurement. Neither uninstall
nor app-data clear used. Candidate176 remains preserved for a later alternating
comparison, with a new monotonic version code if needed for in-place installation.

## 01:27 — Control result and isolated render scheduling experiment

Control177 completed the same staff replay capture. Periodic windows: median FPS
59.96, minimum44.25, median p99 window21.30ms, sampled worst176.91ms, median main
CPU13.4385ms/present. Separate30s simpleperf has17,147 samples and54.044B sampled
cycles versus176's17,151 /53.772B; this single noisy pair does not establish a win.
Same warm-replay SurfaceFlinger method:3341 new distinct presentations in58.978s,
56.63/s,201 intervals>25ms, none>40ms in that minute. Candidate176's analogous
capture56.55/s. Both show regular missed display intervals. The large hitch not
appearing in this minute does not prove it absent. No accepted scalar-context
performance improvement; keep the translator option disabled by default.

Refetched only the relevant DriftDroid source files at the audited d12ccb pin into
work/android-optimization-20260923/driftdroid-source. best_present_mode and
wait_until_precise function bodies match KartPad exactly. DriftDroid also pins
frame/presenter workers to faster CPU tiers and raises frame-worker priority.
Physical control threads already show nice-4 for guest/frame/presenter (inherited),
so adding the high-priority call alone is not justified as a fix.

Implemented a private render-affinity candidate inspired by the tier idea, with
independent conservative selection: intersects inherited affinity; excludes only
the lowest known maximum-frequency tier; keeps original policy for homogeneous,
unknown allowed-CPU topology, empty candidate or unchanged mask. Applies to frame
worker/presenter at startup; no explicit guest/audio/shader changes. OS-inherited
affinity of any subsequently spawned child threads is a measurement consideration.
Failure logs and leaves the existing mask. Eight host policy cases pass, including
restricted masks and incomplete topology. No promise of sustained thermal benefit.

Candidate178,0.5.1-render-policy.1 build running exec11678, log build178.log, using
control's legacy-call generated graph and fresh runtime build/android-render-policy-20260923.
This isolates scheduling from the explicit-context generator option. Source changes
are uncommitted and experimental. Next verify actual masks on device, compare
compositor/cycles/thermals and lifecycle, then retain or reject based on evidence.

## 01:37 — Replay-transition attribution and thermal correction

Triggered screenshots after the recurring ~266ms compositor gap show the staff
replay returning to the starting grid and then its countdown. Similar large gaps
recur about100.25s apart. Classify this event as a replay restart/loading transition,
not proven steady racing stutter. The earlier correlated GPU/presentation waits
remain valid observations of that transition. Regular ~33ms presentation intervals
between transitions remain a separate pacing concern. Two post-trigger screenshots
perturb a short interval in the long control capture; exclude that interval from
clean comparisons. Evidence: control177-hitch-trigger.json and hitch-after images.

Thermal service output contains both stale cached values and fresh Current
 temperatures from HAL. Use the latter: before175 GPU48C/skin35.372C/battery33.9C;
before176 GPU51C/skin37.606C/battery36.5C; before177 GPU50C/skin37.567C/battery36.6C;
long177 start GPU51C/skin38.078C/battery37.1C. Thermal status0. The176/177 starts are
roughly matched;175 is cooler. Cached81C readings are not current measurements.

Official Android scheduling guidance recommends PerformanceHintManager/ADPF over
manual affinity: https://developer.android.com/android-performance-analyzer/analyze/thread-sched
and https://developer.android.com/games/optimize/adpf . Candidate178 is a bounded
scheduling experiment, not an accepted production policy. Evaluate sustained
thermal behavior and lifecycle, and prefer dynamic hints if equivalent gains can
be established. No scheduling benefit has yet been measured.

Completed ten-minute control177 capture:34,008 new frames over599.010s,56.772/s,
p95 interval33.201ms,p9933.347ms,1858 intervals>25ms,15>40ms. Secondary analysis
excludes -1s/+3s around each>100ms replay-restart gap and +5s after the screenshot
trigger: retained571.221s,56.924/s,1779 intervals>25ms,one>40ms(max49.966ms).
Full-run result is retained; exclusions are explicit in steady-summary.json.
Eight poll boundaries lack an overlapping timestamp but the intervening gap is
only16.51–16.69ms, consistent with adjacent frames; retain this coverage caveat.
After capture current HAL GPU/MID51C, skin38.431C versus38.078C before. No sustained
thermal performance improvement can be inferred yet. No user input during capture
apart from the two documented trigger screenshots.

## 01:43 — Scheduling candidate packaged

Candidate178 build completed in16m24s. APK audit passes, API28 retained, private
signer matches installed177. SHA256:
f502aa9e795de808bb47aee77ea9406b42a06ff47a09f64f558c5c43975f6b17.
Retained APK and unstripped libmain.so under private evidence; native cache4j6x5x2c.
Before installation, short control177 1x compositor check is running; restore2x
before matched candidate measurement. No new source change during compilation.

Control177 short1x run:58.45 displayed frames/s across58.976s,81 intervals>25ms,
p9516.803ms,p9933.314ms, one224.9ms replay restart. This suggests rendering workload
influences pacing, but a single minute at a different resolution is not an
optimization result. Screenshot confirms1x selected. Restored2x before in-place
178 installation (exec83085). Repeat at2x for all source candidate comparisons.

178 same-signer in-place install returned Success; package readback confirms178.
Launcher screenshot shows both installed games Ready to play; existing Original
license retained remains visible. Runtime logs confirm resolution_scale=2.00.
PID25503, guest25565, frame-worker25594, presenter25595. /proc readback confirms
worker/presenter affinity4-7 while UI thread remains0-7. Presenter inherits the
worker's mask and correctly logs that it retains its inherited mask. Preserve
this nuance when interpreting the startup log. APK remains profileable/nondebuggable.

178 observed same Luigi Circuit staff replay through120s, stablePID25503. Applying
identical first-three-report exclusion to all candidates: median reportedFPS59.99,
median periodic p9918.58ms (control21.30ms), sampledworst46.90ms(control176.91ms),
medianmainCPU13.2415ms(control13.4385ms). These remain sparse application windows,
not compositor results or statistically established improvement. Full and filtered
summaries are retained in replay-comparison.json; startup includes708ms worst.
Current HAL temperatures are higher:178 beforeGPU53/MID53/skin38.488/battery37.5C;
afterGPU53/MID55/skin38.851/battery37.7C. Sustained thermal tradeoff still open.
Thread-mask sweep shows only frame-worker/presenter4-7; guest, audio, shader and
Mali compiler threads observed0-7. No blanket claim about threads created later.

First178 no-trace compositor minute:58.826 actual presentations/s,54 intervals
above25ms, p9516.761ms versus177's56.631/s,201 above25ms,p9533.268ms. The178 minute
includes a274.9ms replay restart, so that loading transition remains. This is a
promising measured scheduling result, not yet sustained/alternating confirmation.
Next:30s cycle profile, ten-minute sustained capture, then reverse the scheduling
policy in a monotonically versioned control to check causality without data reset.

178 sustained600s compositor capture started exec43613 with thermal/battery
before snapshots. No screenshots or profiler during this capture. Reversal control179
build started exec62089 using exactly the same staged runtime and generated graph;
only the root scheduling entry point immediately returns, leaving OS policy intact.
This avoids a downgrade/uninstall and isolates policy application. The178 helper
and root/runtime diffs are preserved privately. Current root helper contains the
explicit179 control return; restore the preserved178 implementation only after
179 compilation finishes. No public/release-default decision has been made.

178 separate30s cycle profile:15,266 samples,0lost,45.672B sampled cycles versus
177's17,147/54.044B. CPU core selection/frequency and replay phase affect these
counts, so do not present their difference as a percentage speedup or energy saving.
Exact symbolization retained; biggest named self samples remain display lists and
scalar flag bookkeeping. Kernel symbols are restricted; no security setting changed.

Control179 built in1m14s via existing cache; package audit passes, signer matches.
SHA2563d5564c1916bf058372452b7eaab75b8d7b5e3629568a6131cabc62b112ca4b6.
Disassembly verifies KartPadAndroidConfigureRenderThread is exactly a return.
Retained179 APK, symbols and helper source. Restored178 helper byte-for-byte after
build completion; code180 (same enabled policy, incremented version for later
in-place A/B/A confirmation) now building, build180.log. No phone installation
while178 sustained capture runs. Root source currently has policy enabled again.

Further CPU lead for later isolated measurement: warm178 display-list diagnostics
show~180–190k probes per5s, only~34–35k front-cache hits, with~113–117k validated
hits and~1985 records. Current direct-mapped front is256 entries. A bounded larger
front cache might avoid repeated unordered_map lookups while preserving all content/
write-generation validation. Do not infer speedup from hit rate; profile and compare
before accepting. Layout hash already has a dirty-bit cache, so recomputing its
entire state every call is not the current behavior. No display-list edit yet.

Candidate180 rebuilt successfully with enabled policy; audit passes, signer matches.
SHA25654585acafad2186026104644a2d9c22265de90296e44dac58b0bf88f2e1b1f3e.
APK/symbols retained; disassembly confirms policy code restored (not the179 ret).
Both179 reversal and180 repeat candidates are ready for same-signer in-place
updates after178 sustained/lifecycle checks. Current phone remains178; sustained
capture exec43613 still live. No installation may interrupt that capture.

## 02:01 — Independent display-list front-cache candidate

Implemented a private2048-entry direct-mapped front-cache candidate (previous256),
adding28KiB of storage per cache owner on64-bit. Index mask derives from array size;
identity/digest/write-generation checks and full-cache invalidation remain unchanged.
This targets measured front misses, not a relaxation of cache correctness. Existing
ASan/UBSan vertex snapshot suite passes16,416 full/partial restoration cases.
Candidate181 build started exec61055, build181.log, fresh staged runtime
build/android-dl-front-20260923/runtime, same control translation graph and enabled
render scheduling. Compare181 only against enabled-policy180 to isolate cache size.
Current vendor source includes this experimental cache enlargement; previously
prepared178/179/180 source no longer matches staging verification and must not be
rebuilt against changed vendor source without a deliberate source restoration.
The already-audited179/180 packages are unaffected and ready for reversal tests.

Read-only follow-up: cached GX display-list path still copies five index arrays
into local arrays before passing const references onward. The prior improvement
changed function parameter passing; it did not remove these remaining local
copies. A future reference-selection experiment must preserve cached-record
lifetime across state application and miss/eviction paths. Do not change this in
181, which isolates front-cache size. Broader-scene validation remains necessary;
Luigi Circuit staff replay alone cannot establish Retro or complex-track gains.

## 02:07 — Sustained result contradicts the initial scheduling win

178 completed600 polls/599.011s with56.418 displayed frames/s,p9533.268ms,
p9933.351ms,2055 intervals>25ms,15>40ms. Secondary restart-excluded result56.597/s,
1968>25ms versus17756.924/s,1779>25ms. Do NOT accept the short58.83/s result as a
sustained performance improvement. Per-minute rates range55.50–56.90; the poorer
cadence is already present in the first long-run minute. A separate30s simpleperf
run occurred between the short and long samples, so180 should repeat short/long
without intervening profiling. Masks remained4-7 for render/presenter; guest0-7.
HAL before long:GPU57/MID57/BIG56/skin39.074/battery38.0C;after52/52/51/38.587/37.6C.
Global thermal status1 after (versus0 in earlier control), but exposed CPU/GPU
cooling-device values0. This is a confound, not proof of thermal causality.
Snapshot after capture still shows live staff replay. Starting background/resume
check through Home and Recents, then179 reversal. Keep all negative evidence.

178 background/resume recovered the replay in the same process and advanced
through30s of observed frames. Important lifecycle limitation: immediate background
readback still showed4-7, but after resume BOTH worker/presenter masks were0-7.
Android resets the affinity across this lifecycle transition. The startup-only
policy is therefore not a complete production implementation even if later A/B
confirms benefit. Any retained policy needs a measured resume strategy; do not
blindly fight OS scheduling every frame. Reversal179 installation now running
exec32028, after completion of sustained/resume captures.

Next presentation experiment prepared as PRIVATE PATCH ONLY (fifo182-planned.patch),
not applied during181 compilation: Android/Vulkan FIFO instead of Mailbox. Khronos
spec confirms Mailbox replaces a pending presentation while FIFO queues in order:
https://docs.vulkan.org/refpages/latest/refpages/source/VkPresentModeKHR.html .
This offers a testable explanation for app60 vs display57 despite ample average
throughput, not proof of causality. Measure guest/replay wall-clock speed, actual
presentations, queue waits and latency; do not adopt unconditionally for interpolation
or targets exceeding panel refresh. Existing desktop policy remains unchanged in
planned patch. Compare against181 with all other settings/source held constant.

179 install/readback verified. Existing license and both game installs remain
visible; same Luigi staff replay selected at2x. PID3297; all50 observed thread
masks0-7, confirming reversal control does not apply the fast-tier restriction.
Replay capture exec33812 is running. Added host UTC start/end milliseconds to
future compositor receipts for reliable log-window alignment; polling cadence
and workload are unchanged. Earlier captures retain their original receipts.

179 reversal120s observed replay stayed inPID3297. Filtered app windows:median
FPS59.93,p9922.335ms,worst33.03ms,mainCPU13.173ms/present. Short compositor capture:
57.122 displayed/s,156 intervals>25ms,p9516.891ms,p9933.337ms,266.6ms replay restart.
This is between177 and178 short samples, underscoring the need for sustained A/B/A.
179 ten-minute capture now live exec10443; thermal/battery before files saved.
No simpleperf between179 short and long capture. Keep phone untouched until done.
181 native build remains live exec61055 (two activeclang processes verified).

## 02:18 — Presentation-pacing candidate building

181 completed in16m35s; package audit passes and private signer matches. SHA256
94b6597f73733accf95609065f31adeba647f08505c6ba6dde947750039c3224.
Retained APK, unstripped symbols(cache205l6ni4), runtime diff and display-list source.
Applied the previously reviewed Android/Vulkan-only FIFO patch after181 completed.
182 build now running exec14561, build182.log, fresh source
build/android-fifo-pacing-20260923/runtime. It differs from181 only in preferred
present mode. Desktop/Metal policy is untouched. Private test only: no production
assumption for interpolation, high-refresh targets or input latency. Phone remains
179 for its uninterrupted control capture(exec10443).182 source is a new staged
variant; earlier staged runtimes must not be mutated or verification bypassed.

Analysis guard: the secondary >100ms-gap exclusion is a transparent heuristic,
not automatic scene identification. Only interpret it as restart exclusion where
screenshots/periodic replay evidence supports that attribution. Any novel long
stall in later variants must remain a possible regression; full-run results always
include it. Updated helper description to prevent a future candidate's unrelated
stall from being silently presented as normal loading.

## 02:24 — Fresh issue evidence changes workload priority

Live GitHub refresh returned63 open issues. New reporter comment on#195 at
2026-09-22T15:44:49Z says recent updates still drop to~41fps in Original/Retro VS
and online matches, while Time Trials retain60fps. Exact latest package is not
specified. This is stronger workload discrimination than the initial generic
S25 Ultra report. #204 separately describes GCN Cookie Land battle at20–50fps
while prior time trials are smooth even4x. Next physical profiling must include
opponent/arena work; another harder time-trial track alone is insufficient.
https://github.com/chrissotraidis/kartpad/issues/195
https://github.com/chrissotraidis/kartpad/issues/204

After179 sustained control and local health export, keep179 installed long enough
to capture an offline CPU-opponent workload, ideally Cookie Land. Stationary
observation can expose AI/runtime costs but is not a driven/completed race or full
visual coverage. Record actual mode, arena, opponents/rules, settings and evidence;
compare the same configuration on later candidates. #169 retains separate save,
display and heat concerns; do not infer that performance tests close save reports.
No public response or resolution claim posted during this read-only refresh.

Fresh upstream API check still reports83463764b8acda394e058b0c689a10b8561fc380
(September18) as WiiCompiled default-branch HEAD, matching dependencies.lock.json
and the September22 all-platform integration baseline. No newer upstream change
was silently omitted during this loop. API response retained privately.
https://github.com/patchzyy/Wiicompiled/commit/83463764b8acda394e058b0c689a10b8561fc380

Repository G10 records establish the relevant retail battle setup: Single Player
→ Battle → Balloon Battle,6-v-6,Mario/Standard Kart M/Manual. Those August29 checks
were native Metal and do not prove Android performance. Reuse only their menu/
workload information when setting up the new physical Android observation.

## 02:34 — Sustained reversal and additional community evidence

179 ten-minute reversal control completed: 598.985s, 56.965 actual presentations/s,
1,725 intervals >25ms,18 >40ms,p95 33.073ms,p99 33.339ms,max308.367ms.
This compares with178 sustained56.418/s and177 sustained56.772/s; early178 short
improvement did not establish a sustained win. A133.311ms179 gap is outside the
regular staff-replay restart cadence and remains an unexplained hitch, not loading.
Private local diagnostic export verified ZIP integrity; no upload. Journal tail
contains15 late178 samples and106 samples179, all thermal_status1. Headroom ranges
178:0.763–0.789;179:0.738–0.771. Earlier178 short/long windows are not retained in
this bounded tail, so this does not retrospectively establish their thermal state.
Both tested sessions can experience mild thermal pressure; avoid claiming affinity
alone caused the long-run reversal. Full measurements and private journal retained.

Reviewed user-supplied r/decomps thread text. Added priorities: slowdown after first
race/repeated runs on both Dimensity8300U and Snapdragon8Gen2; little benefit from
lowering1–3x resolution; actively cooled Snapdragon865 also reported slow Retro.
These are old unversioned reports, useful hypotheses rather than current repros.
Resolution-change freezing relieved by pause/resume suggests a separate lifecycle/
surface path to recheck. Fullscreen/status-bar, ellipsis visibility, triggers/stick
button mapping and import discoverability are separate enhancement/support themes.
Do not claim modern fixes cover them without checking current implementation.
No external comments posted and no third-party download instructions followed.

182 FIFO package completed in16m05s; release/profileable audit passed, matching
private signer verified. SHA256 cad067d4ae98ede805e1f53e02929e6248929bbc5b270796be4e6e89c867f48b.
Saved APK and unstripped symbols(cache223g4w6e). Not installed yet;179 remains
installed for opponent workload baseline. No active native build after182.

## 02:40 — Opponent workload started

179 original game, existing license: Single Player→Battle→Balloon Battle, Mario,
red team of6 vs6blue, Standard Kart M, Manual, Retro Stages→GCN Cookie Land.
Started private observed210s capture(control179-cookie-observed,exec81305). Inputs
are menu navigation only; kart will remain stationary. Periodic30s screenshots
and app logs establish opponent/timer/render behavior, not a clean compositor
benchmark or a driven match. Follow with matched controlled captures/profiling.
Current resolution2x,Fill Screen,validationoff,existing FPS overlay retained.
182 ready but not installed. Next candidates180/181/182 still require device tests.

Current source already has immersive system-bar hiding on focus, three aspect
modes and controller button/D-pad/trigger remapping. Reddit enhancements therefore
need current behavior/device-specific checking, not duplicate implementation.

60s screenshot confirms Cookie Land battle in progress, six-v-six map, score9–9,
timer2:17.628, stationary Mario. App windows near60 but guestCPU~14.8ms/present
(vs~13.2–13.4ms Luigi replay); opponent cost visible without reproducing reporter's
20–50FPS yet. Started30s simpleperf during this observed run; mark this run as
profiled, not clean timing. Remaining candidate comparisons need matching scenes.

CookieLand179 simpleperf30s:19,333samples,72.42Bcycles. Top sampled functions are
KartPadAndroidClearScalarFlags8.32%,CaptureScalarFlags6.35%,FinishScalarFp3.45%,
FmulsStateInline2.06%;display-list1.85%,emulatedTLS1.62%. This differs materially
from Luigi replay (~3%clear/~2.5%capture). Percentages are sampled shares, not
potential FPS gains, and workload/thermal changes confound raw cycles. Prioritize
correctness-preserving scalar flag/context cost investigation for opponent scenes;
never simply disable floating-point semantics to mimic a faster implementation.
Private report and data retained;30s profiling complete, observed210s capture still
running exec81305. Source182 is built and safe to inspect while no compile active.

02:43 observed CookieLand179 run completed210s, samePID3297. Final screenshot
shows match results27–30 and stationary player0points. This is an observed full
CPU-opponent match, not a driven race.41 sampled app windows including loading,
profiling and results:median59.74fps,min50.93,median p9924.85ms,worst156.36ms,
median guestCPU14.6355ms/present. These mixed windows are not a clean comparison.
No active build/profile/capture remains. Phone remains179 atbattle results.
NEXT: repeat CookieLand on179 with a clean middle120s compositor window and no
screenshots/profiling during it; then180 affinity repeat,181cache,182FIFO matched.
Retain loading and gameplay separately using observed timer evidence. Verify new
SurfaceView layer after resume (old layer may have been recreated). Scalar flag
cost from opponent profile deserves follow-up after these prepared candidates.

02:47 clean179 CookieLand repeat live(exec1448). Helper confirms known OK dialog,
waits25s, saves one before screenshot, then polls actualSurfaceView every1s for120s
without screenshots/profiling during timing; afterward saves screenshot/thermals.
Layer refreshed to167912 after diagnostic-export resume. Navigation initially
selected wrong arena; cancelled before starting and visually confirmedCookieLand.

Re-read prior evening handoff: floating-flag cost was also seen in12-CPU-race
fixture (~7.79%clear/5.90%capture). Current battle profile corroborates that prior
finding, not a newly discovered category. EarlierAPI29 nativeTLS failed to isolate
a benefit; do not repeat it without a stronger discriminatory hypothesis. Explicit
context176 was tested on lightTT only this evening, so heavy-mode contextcomparison
remains useful before rejecting it broadly. ExistingForceSingle can raise hostflags
aftercapture; deleting next preclear would not preserve existingsemantics.

02:49 clean179 battle timing:118.991s,56.500 actualpresentations/s,415>25ms,
5>40ms,max66.556ms,p95/p9933.290/33.343ms. Aligned22 appwindows median59.875fps,
minimum55.40,medianwindowp9922.105ms,worst54.4ms,guestCPU14.709ms/present.
Beforetimer2:50.009,after0:49.784, consistent roughlyreal-timeguestprogress;
CPU AI knocked/respawned stationary kart so camera position varies. No input
or CPU profiler during measured120polls. This is a same-mode stochastic workload,
not exact deterministic race equivalence. Full120sample/receipt retained.

183 explicit-context heavy comparison build started(exec94358,build183.log):
0.5.1-context-heavy.1, current182 stagedruntime and private explicitcontext graph,
freshnativebuild/android-context-heavy-20260923/native. Isolatesgraphcontextchange
against182 when tested, not against179. No source edits during activecompile.

180 installedinplaceafter179 battle reachedresults;adbSuccess,package readback
code180/0.5.1-render-policy.2/API28. BothOriginal/RetroReadyvisible. Launched
Original foraffinitycomparison;no uninstall/containerclear.183compile remainslive
exec94358.180sameprivatecert auditedpreviously;installedAPKretainedwithhash.

180PID15344 startup confirmsrenderworker/presenter4–7(two threads),46others0–7.
Existingretainedlicensevisible. Battleteamsare newly randomizedafterprocessrestart:
180Marioisblue (179wasred);same12charactersbutdifferentteammembership/order.
This is a confound in stationarybattlecross-buildcomparisons;retaincolor/camera
and do notpresentonepairasdeterministicmatchedreplay. Settings/mode/arenaheld.
179cleanthermalsstatus0→1,HALGPU61→59,MID59→63,skin38.62→39.63,battery37.6→38.5.

02:55 candidate180 cleanCookieLand capturestarted(exec handle recordedinthread).
Samehelper25sloadingdelay,120polls,2x,FillScreen,11CPUplayers,blueMario/StandardM/
Manual. Layer167957,PID15344. No phoneactions/profiling untilcapturefinishes.
Compare179/180appsummaryandactualSurfaceFlinger separately and inspecttimerimages.
183buildcontinuesexec94358;181/182readyuninstalled. Next181samebattle,then182FIFO;
183explicitcontexton182base follows afterbuilt/audited. Do notoverwritepackages.

03:00 180 firstCookieLandclean complete:56.795actualFPS,348>25ms,13>40ms,
max158.204ms,p95/p9933.205/33.342ms. App23alignedwindowsmedian59.91fps,min49.72,
medianwindowp9925.13ms,worst146ms,guestCPU14.79ms/present. Timer2:51.926→0:52.266
across~119s compositorcapture. Pipelinecreatedcount stillrises317→336early,
where179warmrepeatheld474 initially. Need180warmrepeatbeforeanyfaircomparison;
first-usehitchescannotbecredited/chargedentirelytoscheduling. Fullresultretained.
No improvementclaim. Candidate183compilelive94358. Privateplannedcacheborrow
patchwritten(dl-borrow-planned.patch),NOTapplied;reviewlifetime/testsafter183build.

180warmrepeatstartedafterobservedCookieLandOKdialog,samePID15344/layer167957,
sameblueMario+CPUteams;25swait+120polls. No profilingorUIactionsduringcapture.
Helperallowsnewlabels;candidate180-cookie-warm outputprivate. Candidate183still
compiling(no restart). Cacheborrowplannedpatchpreserveszero-initializedmissarrays,
usesconstreferencesonlyduringarraysetup;noneareusedbyParseDisplayListfallback.
Beforeapplying, verifyallcalledGXsetterscannotreenterthisHLEcache and exercise
hit/miss/fallback paths;existingvertexsnapshottestdoesnotcoverborrowlifetime.

Cacheborrowlifetime review: DlScanCache isthread_local;Store isonlycalledonmiss,
whichchooseslocalarrays. CachedpathusesstateCPwrites thenGXsetters. GXSetVtxDesc/
SourceVtxDesc/AttrFmt updateGXstate only;GXSetArray writesprivateAuroraFIFO,whose
write_data/write_data_grow append/reallocate theFIFO buffer,notHLEcache. No guest
callback/cacheinsertion occursduringarraysetup. FallbackParseDisplayListoccurs
afterallborrowedarrayuses. Existingflattenedbytesalreadyborrowthissamerecord
throughlaterGXCallDisplayList. Patchremainsondiskonlyuntil183compilecompletes.

03:04 180warmCookieLand120polls:119.023s,57.628displayedFPS,287>25ms,zero>40ms,
max33.700ms,p9516.805,p9933.335. App23windowsmedian59.96,min58.59,p99median24.97,
worst40.04,guestCPU14.824ms/present. Betterthanfirst180and179sample,butthermal,
team/cameraandrunvariationremain;repeat/sustainedacceptanceoutstanding.

183built13m51s;APK auditpasses,privatecertmatches. SHA256
cba62d2697daccfeda81c3fd79f78c8c4caf1dd24717ed895cdab4531819bb98.
Symbolsretained(cache6fa4b5r3). Aftercompletionappliedreviewedcacheborrowpatchto
Androidvendor. ExistingASan/UBSan16,416snapshotcasespass;thesecheckstatecontract,
notborrowlifetime/performance.184buildstartedexec43727,0.5.1-dl-borrow.1,fresh
build/android-dl-borrow-20260923/{runtime,native},explicitcontextgraphsameas183.
184differsfrom183onlyborrowedscanarrays. MustinspectactualARMcopyremoval and
comparegraphics/cadencebeforeadoption.181/182/183packagesreadyuninstalled.

181installedinplacesuccessfullyafter180completedbattle;readbackcode181/name
0.5.1-dl-front.1/API28. BothgamesReadyvisible;Originallaunchrequested. Next:
verifyexistinglicense/threadmasks,setupCookieLandfirstandwarmcaptures(same
battle-capture.py),compare180warm. Then182FIFO,183explicitcontext,184borrow.
184buildliveexec43727;do noteditactivecompiledsources. No capturecurrentlylive.
180warmthermalstatus1→1,GPU64→61,MID61→63,skin40.21→40.94,battery39.0→39.9.
This is warmerthan179;keepthermalconfoundratherthanclaimingschedulerwin.


### 03:09 JST — current acceptance boundary

The opponent-heavy test is Original Mario Kart Wii, Balloon Battle on GCN Cookie Land, Mario in a Standard Kart M, manual drift, 2× resolution and Fill Screen. The kart remains stationary while 11 CPU players run the battle. Team assignment, items and camera movement can differ between launches, so these are comparable workload observations, not deterministic race replays.

Build 181 is installed in place. The existing retained license is visible, and both game entries remained Ready before launch. PID 19147 has two threads restricted to cores 4–7 and 48 threads allowed on cores 0–7. This verifies that the private scheduling experiment is active for this launch; it does not establish a performance benefit or preservation of every private file.

The warmed build 180 observation delivered 57.628 displayed frames/s with no intervals over 40 ms during 119.023 seconds. The previous warmed build 179 observation delivered 56.500 frames/s, but different thermal conditions and stochastic battle behavior prevent attributing the difference to scheduling alone. Earlier ten-minute time-trial testing failed to sustain the short scheduling gain. Scheduling remains unaccepted.

Next comparisons isolate: build 181's larger display-list front cache, build 182's FIFO presentation, build 183's explicit scalar context, and build 184's borrowed cached scan arrays. Build 184 is still compiling. Each needs observed runtime correctness and repeated timing before selection. No public release or resolved performance claim is justified yet.


03:15 JST: build 181 first Cookie Land capture is active (exec 72962), using SurfaceView BLAST #168003. The start confirmation showed GCN Cookie Land selected. No screenshots or CPU sampling occur inside the 120-poll timing window. Build 184 remains active (exec 43727). Baseline build 183 ARM disassembly was saved privately as `code183-display-list-disassembly.txt`; its array setup calls pass stack-local arrays. Compare the exact cache-hit path against 184 after linking, rather than counting every unrelated memcpy in the function range.


03:16 JST: build 181 first battle capture completed: 118.982 seconds, 55.798 displayed frames/s, 472 intervals over 25 ms, 12 over 40 ms, maximum 158.242 ms. The 23 aligned app windows had median 59.6 FPS, minimum 48.0, median p99 27.15 ms, worst 154.08 ms and median guest CPU 14.718 ms/present. This first-use observation does not demonstrate improvement. A warmed repeat is next; do not compare it directly with warmed 180 as proof of regression either. The faster front lookup fraction rose from roughly 23% (180 warm) to 36% (181 first), but cache population and first-use pipeline work differ. Build 184 remains compiling (43727).


03:20 JST: build 181 warmed repeat is active (exec 53934), same process and surface. Before confirming, the screen again showed GCN Cookie Land selected. First-run thermal HAL status stayed 1; GPU 61→59°C, MID 58→60°C, BIG 68→68°C, skin 38.56→39.98°C, battery 37.6→38.8°C. `analyze-battle.py` now aligns phase and cache reports to the same capture window as app FPS, discarding the first boundary-overlapping five-second report. First-run aligned front-hit fraction is 36.0%, cache entries 1288→1654; median presentation total is 1.265 ms, maximum 12.243 ms. These numbers describe the mechanism and do not establish a user-visible improvement.


03:24 JST: warmed build 181 completed 120 polls over 118.974 seconds: 56.432 displayed frames/s, 427 intervals over 25 ms, one over 40 ms (66.784 ms maximum). App windows: median 59.92 FPS, minimum 58.12, median p99 22.985 ms, worst 32.69 ms, guest CPU 14.736 ms/present. Aligned front-hit fraction was 35.1%, cache entries 2952→3175. The final screenshot shows the battle still active with 50.124 seconds remaining. This does not support adopting the larger front cache as a stutter fix. It remains in subsequent already-built variants solely to isolate their differences; a final candidate must remove unproven changes or verify them separately.

Build 184 completed successfully in 15m45s. Package audit passed; signer matches the existing private install. APK SHA256: d9d7def8d16205123cc4f2b76dd9e7cb7c567b863ae466f1730680f99f023339. Unstripped symbols retained from native cache 6w3z523z. ARM source-line disassembly confirms build 183 executes vector loads/stores for cached arrays around 0x1310fc8 onward; build 184 removes those copies from the hit branch. Overall function size changes only 6372→6364 bytes, so size alone would have been a poor verification metric. Device correctness and timing remain outstanding.

After observing build 181 at its completed-battle Next screen, began an in-place install of build 182 (exec 73258), the FIFO presentation experiment. Build 184 is ready, not installed. No builds are currently running.


Build 182 in-place install succeeded; readback confirms code 182 / 0.5.1-fifo-pacing.1 / API28. Both games remain Ready in the launcher. Original is running as PID 22731 on SurfaceView BLAST #168049, Vulkan / Mali-G715 confirmed in logcat. The private FIFO selection message uses Aurora's file logger and is absent from logcat; capture an exported console log later to verify the selected present mode. Directly starting the non-exported game activity was correctly denied by Android; launched through the exported KartPadLaunchActivity and visible Play Game button instead. Navigation exec 11639 finished at the title screen; exec  current `a a a` advances through the existing license to Single Player. No timing capture is active yet. Next: confirm mode menu, select Cookie Land, measure 182 first/warm, then compare 183 and 184. Build 184 audit exec 10241 is complete and passed.


03:29 JST: build 182 first Cookie Land measurement is active (exec 27384), PID 22731 / surface #168049, blue Mario this launch. Existing boot pipeline prewarm is capped at 128 earliest-use recipes, with one background compiler and priority first-use workers. That explains why a first battle can create more pipelines even after the boot queue reaches zero; it does not establish a cache persistence failure. The cap explicitly prevents retaining thousands of unused driver pipelines on mobile. No cap increase is justified from the present evidence, and no cache flush appeared in the recorded 181 battle windows. Warm persistent missed frames remain a separate target.


### 03:34 JST — FIFO first observation and cleaner control

Build 182 first battle: 118.986 seconds, 59.352 displayed frames/s, 62 intervals over 25 ms, nine over 40 ms, maximum 149.905 ms. Displayed interval p95/p99 are 16.742/16.935 ms. The screenshots show timer 2:51.902→0:51.974 (119.928 game seconds), consistent with approximately real-time progression across the capture plus screenshot overhead. App median 60.02 FPS, minimum 50.85, median p99 23.35 ms, worst 119.84 ms, guest CPU 14.727 ms/present. First-use hitches remain.

FIFO increases presentation-side waiting: aligned median acquisition 2.428 ms and total presentation 3.701 ms, compared with roughly 0.2 ms acquisition and 1.3 ms total in the previous Mailbox observation. These are submission timings, not input-to-photon latency. Thermal HAL GPU 61→61°C, MID 62→63°C, BIG 71→68°C, skin 39.49→40.78°C and battery 38.6→39.8°C. This is promising cadence evidence on this Pixel, not general device acceptance. Warm repeat is active (98216), same PID/surface.

Build 185 started (38863), `0.5.1-fifo-control.1`, using the legacy generated graph and fresh `build/android-fifo-control-20260923/{runtime,native}`. It removes the larger front cache and cached-array borrowing, and disables the private affinity helper, while retaining FIFO. Added Android-only enqueue-to-dequeue age and positive deadline-lateness metrics to the existing bounded phase collector. These are queue/schedule diagnostics, not end-to-end input latency. This control can establish whether the cadence benefit needs the unproven scheduler/cache changes. A corresponding Mailbox reversal with the same diagnostics will still be needed for a close comparison.

The complete 184 vendor diff and enabled affinity helper were saved privately before source changes (`candidate184-vendor.patch`, `candidate184-render-thread-policy.cpp`); packages and symbols for 181–184 remain retained. Do not mutate current compiled sources while 185 is live.


03:36 JST: build 182 warm repeat completed: 118.969 seconds, 59.923 displayed frames/s, 13 intervals over 25 ms, one over 40 ms (49.990 ms maximum), p95/p99 16.720/16.803 ms. App median 59.97 FPS, minimum 58.98, median p99 21.30 ms, worst 29.45 ms; guest CPU 14.779 ms/present. Median acquisition/total presentation 2.141/3.596 ms. Screenshots show 2:49.584→0:48.383 (121.201 game seconds across capture plus screenshot overhead), no gross slowdown. The warmed cadence result supports further FIFO evaluation; it does not prove latency, sustained-session, interpolation, Retro Rewind or other-device acceptance.

Build 185 remains compiling (38863). Build 182 remains installed; timing capture 98216 is complete. Next export its private console to verify actual selected mode, then compare 183 explicit context and 184 borrowed cache arrays, and test 185 FIFO without affinity/cache enlargement.


03:41 JST: exported the exact build 182 / PID 22731 console through Report a Problem → Save Diagnostic Log to local Downloads, then pulled the completed 440,709-byte file privately. UI confirmed log saved; nothing uploaded. The file explicitly confirms “Private Android pacing candidate selects FIFO”. Boot prewarm rebuilt 126 pipelines in 0.7 s with 303/303 Dawn blob-cache hits, zero stores and 19.1 MiB loaded. This rules out an empty Dawn cache for this session; later first-use pipeline objects can still cost time. No “fell behind”, “Presentation job took”, device-loss, uncaptured-error or surface-rebuild message was found in this exported session. Queue-age/input-latency proof still needs the new instrumentation; absence of warnings is not proof of zero delay.

Phone is currently on the Report a Problem page after local export. This has paused/resumed surfaces, so refresh layer and CPU masks before any further 182 capture. Prefer installing 183 next for its isolated heavy-scene comparison. Build 185 remains active (38863); do not restart or edit compiled inputs.


03:43 JST: build 183 installed in place successfully (28973 complete). Readback code 183 / 0.5.1-context-heavy.1 / API28; both games still Ready. Original Play selected. Next navigation should inspect the current title/license state rather than assume a particular number of button presses. This build differs from 182 by the explicit scalar-context generated graph. Build 185 remains live (38863), expected around 03:50; no source mutations until completion.


03:50 JST: build 183 first Cookie Land capture active (34722), PID 27946 / BLAST #168143. Existing retained license visible; two render threads on cores 4–7 and 49 other threads on 0–7 before timing. The workload is blue Mario, as in 182, though AI/item behavior remains stochastic.

Build 185 completed in 13m44s; release/package audit passed (30597 complete), private signer matches. APK SHA256 674758a78808dc81bf6a951b84a4a480224ea4b576bd6a7d869d83ae01e6b397. Symbols retained from cache 616spq3i. Disassembly of the affinity helper is saved to verify the control does not set CPU masks.

Preserved 185 vendor diff and FIFO block before starting build 186 (7038), `0.5.1-mailbox-control.1`, fresh `build/android-mailbox-control-20260923/{runtime,native}` with legacy generated graph. Its only runtime difference from 185 is removal of the private FIFO preference; baseline cache/copy behavior, disabled affinity and queue diagnostics match. This is the intended close presentation-mode reversal. Current source therefore has Mailbox preference, baseline 256 front cache, copied scan arrays, disabled affinity, and queue diagnostics. Do not mutate it during 186 compilation.

A readable [candidate comparison](android-candidate-comparison.md) now records the warm battle table and explicitly unaccepted changes. Earlier scalar-FP flag shortcuts were rechecked: Capture clears exceptions, but subsequent single rounding can raise host flags, so dropping the next pre-operation clear remains incorrect. No such shortcut was introduced.


03:53 JST: build 183 first battle completed: 118.970 seconds, 59.897 displayed FPS, 17 intervals over 25 ms, none over 40 ms, maximum 33.385 ms. App median 59.985, minimum 58.77, p99 median 22.51 ms, worst 28.50 ms; guest CPU 14.8735 ms/present. This first-use run is smoother than 182's first-use run, but 182 exported after warming the scene and flushed Dawn's cache on activity background; the cross-process cache state is consequently a confound. No explicit-context CPU win is established.

Shipping-policy follow-up identified: runtime_config supports experimental interpolation and InitializeRuntimeSettings applies its target after renderer initialization. Guarding FIFO only at initial best_present_mode() would miss a later target change. A final native-rate-only FIFO policy must request ordered surface reconfiguration when that target changes and recompute mode there, preserving Mailbox for interpolation. Current private 185/186 comparison deliberately leaves this policy refinement out to isolate the observed native-60 behavior. No implementation change during active 186 build.


### 04:00 JST — cadence versus delay, and explicit-context result

Build 183 warmed battle completed: 118.968 seconds, 59.831 displayed FPS, 25 intervals over 25 ms, none over 40 ms, maximum 33.477 ms. App median 60.06 FPS, minimum 58.01, window-p99 median 22.34 ms, worst 37.3 ms, guest CPU 14.865 ms/present. Before/after screenshots confirm active Cookie Land with timer 2:49.801 to 0:49.102. Compared with 182 warm (14.779 ms), explicit context has no demonstrated CPU advantage; it remains unaccepted.

AOSP FrameTracker.cpp defines latency columns as desiredPresentTime, actualPresentTime, frameReadyTime: https://android.googlesource.com/platform/frameworks/native/+/master/services/surfaceflinger/FrameTracker.cpp . Deduplicating by actual presentation, excluding the first historical ring and invalid timestamps, the warm 181 Mailbox run had median desired-to-actual 25.521 ms and ready-to-actual 23.293 ms. Warm 182 FIFO measured 41.246 ms and 33.639 ms respectively; warm 183 FIFO measured 39.150 ms and 32.938 ms. This exposes a material buffering tradeoff behind the smoother cadence. These are compositor timing proxies, not measured input-to-photon latency. Raw derived results are private compositor-delay-comparison.json. The simpler 185/186 reversal is still needed before selecting a shipping policy.

Started same-signer in-place install of already-audited 184 after the 183 timed window ended; no data clearing or uninstall. Build 186 remains compiling.


04:04 JST: build 184 installed successfully in place; package readback confirms version 184 / 0.5.1-dl-borrow.1. Both launcher game entries remained Ready. Navigated existing Original license to observed Cookie Land confirmation. First battle capture is active as exec 30817, PID 31762, SurfaceView BLAST #168189, label candidate184-cookie-clean. No screenshots/profiling inside timing window. Next: analyze first capture, warmed repeat, then simpler 185 FIFO / 186 Mailbox controls. Build 186 remains active exec 7038. Disk headroom about 12 GiB; preserve artifacts/symbols and only clean known inactive object caches if needed.

Source review confirms native-rate present deadlines use the previous schedule boundary plus 6.5 ms, while late frames free-run; queue and deadline diagnostics in 185/186 will determine whether this policy is effective under opponent load. FIFO policy must account for interpolation target changes after renderer initialization; existing ordered reconfigure path drains presenter and owns surface before GPU mutex. No source mutation during 186 build.


04:08 JST: build 186 completed in 14m15s. Package audit passed and private signer matches installed identity. SHA256 156e86f25e9fd4633593565f272dd61d4f9941efaa45992b98043f0a5cd2d386; APK and unstripped symbols retained (cache 2l4e6pj2). No builds active.

Build 184 first capture completed: 118.988 seconds, 59.435 displayed FPS, 68 intervals over 25 ms, two over 40 ms (83.260 ms maximum). App median 59.87, minimum 51.27, p99-window median 23.53 ms, worst 84.99 ms; guest CPU 14.770 ms/present. Present-ready-to-actual median 32.138 ms. Final screenshot shows active battle with 50.233 seconds remaining. First-run encoding peak 77.183 ms indicates a hitch outside the small array-copy optimization; not proof of its cause. Warm comparison pending.

Private analyze-surface.py now includes validated desired/ready-to-actual compositor delays, excluding invalid fences and historical first-poll frames. Settings source review confirms Android consumes display settings on the runtime path, and resolution changes publish nativeResizePending before waking SDL; the render worker drains presentation and owns surface then GPU mutex. This is source evidence only; physical resolution/resume verification remains outstanding.


04:11 JST: started build 187 (exec 6736), native-pacing guarded candidate, fresh build/android-native-pacing-20260923/{runtime,native}, legacy graph, baseline cache/copies, affinity disabled. Preserved candidate186-vendor.patch beforehand. Android Vulkan now prefers FIFO only while interpolation target is zero; other modes retain prior selection. The interpolation setter compares effective zero/nonzero targets and requests existing ordered surface reconfiguration on transitions. resize_swapchain recomputes present mode and can reconfigure unchanged-size surfaces without reallocating offscreen targets. Whitespace check passed; build/runtime/interpolation verification outstanding. This remains a candidate pending the 185/186 timing and delay reversal, not an accepted default. Do not mutate source while 187 builds.

Build 184 warmed Cookie Land capture started (exec assigned by tool; label candidate184-cookie-warm), same PID31762 / surface168189, after visually confirming Cookie Land OK. The preceding results screen showed existing retained profile.


04:13 JST: active build187 uses cache4567r4b3, verified by CMake cache and running ninja command. Removed only 2,364 regenerable .o files from finished experiment caches223g4w6e/6fa4b5r3/6w3z523z after verifying each retained APK and unstripped library. Reclaimed 8,109,987,568 bytes; receipt inactive-object-cleanup-0412.json. Source snapshots, link/configuration receipts, packages, symbols, traces and screenshots retained. Warm184 capture exec33391 remains active.


Warmed184 completed (capture receipt ends 04:11:37 JST): 118.985 seconds, 59.864 displayed FPS, 21 intervals over25ms, zero over40ms, max33.415ms. App median60.01, minimum58.84, medianwindowp99 23.48ms, worst31.53ms, guestCPU14.726ms/present. Desired-to-actual median41.242ms, ready-to-actual34.035ms. Final screenshot shows active Cookie Land, timer49.272seconds. Compared183warm CPU14.865, this is a small stochastic observation, not a proven copy-optimization win. Warm cadence is essentially equal. Keeping simpler baseline arrays for the presentation controls. Started same-signer185 in-place update after capture ended.


Build185 same-signer install succeeded; readback185 / 0.5.1-fifo-control.1. Launcher still shows both games Ready. Original launched PID4970, SurfaceView BLAST168235. Navigation underway, no timed185 capture yet. Resolution source follow-up: RefreshHostSettings is called only after FrameReadyForOverlay waits for the frame worker DONE phase, so the non-atomic scale variable alone is not evidence of a settings race. Preserve this synchronization; do not add an unsupported race fix.


04:16 JST: simpler FIFO185 first capture active exec89640, PID4970 / surface168235, label candidate185-cookie-clean. Observed red Mario / Cookie Land OK before start. Warm repeat then186 Mailbox reversal are next. Guarded187 still compiling exec6736, cache4567r4b3.

First-use hitch follow-up: in184, pipeline count rises344→345 in the04:06:07–04:06:12 report window, which also contains77.183ms maximum encoding and84.99ms app frame. This is consistent with a pipeline-related stall but not direct proof. The startup recipe replay is intentionally capped128 to avoid thousands of unused mobile driver objects; do not remove that bound indiscriminately. Next useful diagnostic would time actual ordered pipeline waits, then evaluate a bounded prewarm change with launch time and memory as well as hitch counts. Source currently has no per-wait timing; existing Tracy zone alone was not captured.


04:18 JST: private test-present-mode.py compiles the actual best_present_mode function extracted from the current candidate source with minimal host API stubs. Twelve behavior cases passed with Android enabled and the same twelve passed without it: native FIFO selection,120/180/240 interpolation keeping Mailbox, unsupported-FIFO fallback, missing-Mailbox Immediate path, FIFO-only capability, and existing Metal/OpenGLES selection. This covers selection, not driver behavior, setter/reconfiguration ordering, or physical interpolation acceptance. Full187 build remains active.


04:20 JST: first185 capture completed:119.007seconds,59.736 displayedFPS,30 intervals>25ms,one>40ms (133.269ms). Screenshot activeCookieLand49.708seconds. App snapshot median59.965, minimum58.82, windowp99median22.09ms, sampledworst38.4ms, guestCPU14.669ms. Important sampling distinction: periodic app reports cover roughly60 frames every5seconds, so they missed the133ms display hitch. Updated analyzer note and comparison wording to state these gaps; do not use sampledworst as a whole-run maximum.

185 queue age median-of-window-means0.101ms,maximum5.917ms; deadline lateness4.987ms,maximum116.494ms. Compositor ready-to-actual median33.935ms, desired-to-actual41.263ms. The extra delay is not explained by a growing application presenter queue in this test. Encoder peak113.455ms overlaps a pipeline-count increase349→350 around04:17:49, supporting targeted pipeline-wait instrumentation next. Warm185 remains required. Captured meminfo only after timing ended.


04:22 JST: warm185 capture active exec66411, same process/surface. Drafted private pipeline-wait-diagnostic.patch and verified it applies, but did not mutate active187 source. The diagnostic times only actual blocking waits, reports waits at least8ms at most once persecond, and writes after releasing the pipeline mutex. It changes no wait timeout or draw correctness behavior. Plan188 is instrumentation-only on guarded187 with the existing128-recipe limit, before considering a bounded prewarm change. A lack of log lines will not prove absence of every slow wait because reporting is rate limited.

185 post-battle meminfo: TOTAL PSS2,913,329KiB, RSS3,072,204KiB, swapPSS35,357KiB. This is a single after-scene snapshot, not a memory regression comparison. Keep memory cost in the prewarm acceptance criteria.


04:23 JST: live GitHub read-only refresh of newest updated open issues shows no updates since #195 at15:44:49UTC; #316 and #314 remain next. No new issue evidence changes the active performance sequence. No issue replies, closure, or release publication made during this check.


04:25 JST: warm185 completed118.958seconds,59.181displayedFPS,102 intervals>25ms,zero>40ms,max33.495ms. App median59.86,min57.93,p99median22.43ms,sampledworst30.05ms,CPU14.731ms. Queueage mean-median0.119ms,max9.166ms; deadline lateness6.777ms,max20.355ms. Compositor desired-to-actual39.473ms,ready-to-actual32.606ms. This is less consistent than182warm; do not round it to a locked60.

Visual caveat: warm185 after screenshot shows transient horizontal black bars near lower HUD while Mario is hidden; before screenshot is clear. A follow-up at1.639secondsremaining shows Mario and no bars (candidate185-followup-clear.png). Do not dismiss the bars as invulnerability or claim visual acceptance; compare186 and latercaptures. No capture-time screenshots were taken.

187 built in13m48s, auditpassed, private signer matches; SHA256b15868316a761ec674093db01965885952bb8fbe34d629c750801ebd59f37ec6. APK/symbolsretained. Preserved candidate187-vendor.patch then applied pipelinewaitdiagnostic; build188activeexec12345, freshbuild/android-pipeline-timing-20260923/{runtime,native}, legacygraph,prewarm128unchanged. Do not mutate188source. Started186same-signerupdate for the matchingMailboxreversal after185measurement.


04:27 JST:186 in-place install succeeded; readback186/0.5.1-mailbox-control.1, both games Ready, existingretained profile visible. Navigating to firstCookieLand capture.188activecache6t3w666e. Cleanup deferred until188 finishes: remove unaccepted explicit-context translator/API experiment and unused affinity helper/hooks from final source after preserving patches; restore two leftover equivalent front-cache edits (stale2048comment and size-derived mask) to baseline. Current185/186 masks remain baseline256 despite that stale comment; compile semantics unchanged. No source mutation during188.


04:28 JST: before removing affinity permanently, isolate it once with the selected FIFO policy and baseline256 cache/legacygraph. Warm185 baseline placement encoded at6.064ms mean-median versus182/183 faster-core variants5.273/4.518ms; previous longMailbox comparison could have been dominated by compositor misses. Those runs also differ in cache and thermal conditions, so they do not establish causality. Proposed189 changes only the currently disabled affinity helper relative188 (same pipelinewaitdiagnostic and guardedFIFO), then requires sustained comparison and resume behavior. Affinity remains unaccepted; cleanup is deferred until this interaction is checked, rather than treating the earlierMailbox result as dispositive for FIFO.


04:30 JST: matchingMailbox186 firstCookieLand capture started, PID9531 / SurfaceViewBLAST168281, redMario. Same legacygraph, baselinecache/copies, disabled affinity and queue diagnostics as185; only presentation preference differs. Warmrepeat next, then guarded188 diagnostics/retained187 candidate checks.188 stillcompilingexec12345. Warm185 ended hotter (skin42.516C,battery41.5C,BIG76C) than183/184; this is a comparison confound, not proof of throttling or explanation of the result.


04:35 JST:186firstMailbox completed119.024seconds,56.879displayedFPS,373intervals>25ms,three>40ms,max50.007ms. Appmedian59.7,min55.69,p99median24.275ms,sampledworst52.13ms,CPU14.753ms. Queueage0.1325msmean-median,max4.806ms; encode6.101msmean-median,max29.398ms; compositorready-to-actual23.606ms,desired-to-actual25.626ms. This matching reversal supports the cadence/buffering tradeoff, pendingwarmrepeat. End screenshot is clear (timer50.413seconds).

A separate private binary-fenv-prototype combines the arithmetic and its existing pre-clear/capture/post-clear in one opaque call, aiming to reduce call/register-spill cost without dropping flags. Nativeoperation occurs inside strict-FP helper; NaNclassification receives a finalclear to preserve baselinehostflags. Not applied to root/runtime sources or188build. Differential compiles baseline/candidate evaluator namespaces separately to avoid weak-symbol coalescing; physical correctness, hostflags, rounding and benchmark checks must pass before consideration.


04:39 JST: initial privatebinaryFENVprototype failed differential hostflags: ARM64 operand classification raisedIDC(0x80) after combinedcapture; resultbits/FPSCRmatched but hoststate did not. Keptfailedlogs. Addedrare-pathpostclassificationclear for subnormaloperands/results andNaNresults in privateheader. Rerunpassed448,000cases(two224,000threads), includingresultbits,FPSCR,hostFEflags,writedestination,nestedcontextandfourroundingmodes. Pairedmicrobenchmarks vary widely and do not establish a speedgain. No game/sourceintegration justified yet; prototype remains private. No physicaltimingcapture overlapped these standaloneexecutables.

Warm186capture activeexec56475, samedevicePID9531/surface168281, afterobservedCookieLandOK. Standalonetests completed before25secondload/countdownwait and measurement began.


04:41 JST:188completed13m48s,auditpassed,signermatches. SHA256591661bc44cc2e290899b2908c9321322714fc856a8867f47dd8763895a0fc9c. APK/symbolsretained(cache6t3w666e). Started189exec92305 with identical prepared188runtime and legacygraph, only removing earlyreturn from existingrootrender_thread_policy.cpp to enable faster-coreplacement. Preserved188helpercopy. This isolates affinity with guardedFIFO and pipelinewaitdiagnostic; no largerfrontcache or explicitgraph. Must measure and verify threadmasks; resume-reset limitation remains.


04:43 JST: warm186Mailbox completed118.992seconds,56.592displayedFPS,403intervals>25ms,two>40ms,max116.644ms. Appmedian59.88,min57.71,p99median23.71ms,sampledworst37.35ms,CPU14.798ms. Queueage0.125msmean-median,max5.776ms; encode5.977msmean-median,max102.938ms; compositorready-to-actual23.913ms,desired-to-actual25.739ms. End screenshotclear,49.961secondsremaining. Warm185FIFO had59.181FPS/102intervals>25ms/32.606msready-to-actual: repeatablecadencetradeoff onthisphone,notinputlatencyproof.

Beforeinstall188, captureanadditional186battle asvisual-onlyscreenrecord to investigateblackbarobservation; recordingoverhead makes itunsuitable forperformancecomparison. Then188first/warmdiagnosticcaptures andFIFOvisualrepeat.


189buildcompleted1m15s; APK/symbolsretainedfromsamecache6t3w666e. SHA256dcf5f75d4cf138c0cef4336c7c53e7bc479742897194c1fd712eb656b68bca40. Auditcompleted; signerreadbackinprivatefile. No activebuild. Device186reachedend-of-matchawardsequence aftertwo battles; visual-onlythirdbattle requiresreturningthroughmenus, notassumingNext meansNextBattle.


04:57 JST: Completed an additional 180-second visual-only Cookie Land recording on Mailbox186 (candidate186-visual.mp4). Five-second contact-sheet samples show battle activity, respawn, ink effects and the finish; no broad black HUD bars are apparent in those samples. An all-frame heuristic scan is running; neither sampling nor that heuristic proves visual correctness. Recording overhead excludes this run from the performance table.

The separate whole-binary-fenv-prototype moved the entire original binary evaluator into an opaque strict-FP helper and replaced only its internal flag calls. Physical differential testing immediately failed host exception-state equality for NaN/invalid cases despite matching result/FPSCR. Preserved device-test.txt; rejected for integration. This illustrates why opaque boundaries cannot be removed based on a microbenchmark alone. No production source changes from this prototype.

Build188 installed in place successfully, readback188/0.5.1-pipeline-timing.1; launcher shows both games Ready. Guarded FIFO selection host tests again passed12 Android and12 non-Android cases, and both root/vendor diffs pass whitespace checks. These checks do not substitute for physical lifecycle testing.


05:02 JST: The all-frame visual186 scan found68 candidate frames among9,726 decoded frames, in five short clusters. Corrected the detector to pass frames through without ffmpeg frame-rate duplication; the first scan used a different frame index basis. Extracted original decoded frame4052 and visually confirmed the same wide horizontal black bars seen in185, during a respawn transition. This is not unique to FIFO. Exact vanilla-game equivalence remains unverified; avoid inventing a rendering fix from that observation. Private color frame and full video retained.

Preserved complete pre-cleanup root/vendor binary patches, then reverse-applied only this loop's rejected explicit-context translator/API/test changes and the leftover front-cache comment/index changes. Copied private FP test adapter sources into their prototype directories so the rejected tests remain reproducible. Unrelated clean-rc2.md changes untouched; affinity helper and hooks remain pending189. Prepared188/189 artifacts and runtime snapshots were not modified.

188 startup diagnostics already observed actual persistent-pipeline waits of73.290,87.953 and80.845ms during menu initialization/navigation; timed battle correlation remains next. These are direct waits rather than pipeline-count inference.


05:05 JST: guarded FIFO188 first Cookie Land capture completed118.969seconds:59.890 displayedFPS,18 intervals over25ms,none over40ms,max33.378ms,p99 16.818ms. App snapshot median60.04,min58.45,p99median21.06ms,sampledworst28.93ms; guestCPU14.706ms. Ready-to-actual median33.505ms,desired-to-actual41.090ms. Queueage mean-median0.097ms/max3.859ms; encoder5.128ms mean-median/max27.879ms. A direct persistent pipeline wait24.821ms was logged at05:03:42.896, within this capture. End screenshot shows activebattle49.203seconds, no bars in that frame. Warm repeat remains next.

Started private190 build (exec76258): same guarded FIFO and diagnostics, affinitydisabled, Android prewarm cap256 versus128; otherplatform cap remains128. Retains one background compiler and priority first-use work. This is a bounded experiment motivated by direct waits, not an accepted change. Measure startup/prewarm duration and memory as well as first-use/warm frames. Root/vendor source remains fixed while build runs. Uses fresh build/android-prewarm-256-20260923/{runtime,native} and legacygraph; rejected explicit-context APIs have been removed from this source, leaving their equivalent baseline adapters.


05:12 JST:188 warmed battle completed118.969seconds,59.276displayedFPS,90 intervals over25ms,one over40ms,max49.925ms,p99 33.292ms. Appmedian59.82,min57.2,p99median22.79ms,sampledworst42.01ms,guestCPU14.696ms. Queueage0.109ms mean-median/max4.873ms; encode5.485ms/max20.571ms; ready-to-actual33.094ms. A direct pipelinewait18.296ms appears in the window; no claim that it explains the largest display gap without timestamp correlation. Beforewarm timing, every observed SDLthread, includingframe14409/presenter14410, had CPUmask0–7. FirstbattlepostscenePSS3,024,136KiB/RSS3,210,020KiB/swap37,291KiB. More pipelines were populated than185/186, likely reflecting different pre-battle activity; memory snapshots are not exact paired startup comparisons.

Private exact-float-fenv-prototype takes a different approach: preserve opaque preclear and original fallback, omit the post-arithmetic capture only for provably exact binary64 arithmetic on two normal binary32 inputs (Add/Sub exponent gap<=28, or Multiply). Normal binary32 range prevents binary64 overflow/underflow; exceptional, zero, subnormal and other inputs retain the baseline path. It passed2,240,000 physical differential cases across14 adapters, fourroundingmodes, arbitrary guestFPSCR, seededhostexceptions, nestedcontexts, randomdouble/float inputs and exactnessboundarygaps. Six alternating10million-call pairs onCPU7 measured20.61–22.11ns baseline versus12.63–13.70ns candidate for a simple Fadds case. This is a hot-path microbenchmark, not gameplay proof. Broader slow-path cost and rawFPSR/QC coverage remain before integration. Prototype is private and did not overlap either188timedcapture.

Inactive symbol files176–187 were gzip-compressed only after decompressed SHA256 verification, preserving all12 exact symbol artifacts while reclaiming12,788,467,921bytes. Receipt inactive-symbol-compression.json. Active188/189symbols retained unpacked.


05:22 JST:190 build completed13m38s, APK audit passed and signer matches installed private candidates. SHA25673db8a1ce4c5e98490e6d4e8b455d798b0a0f9096b24b13f6097c7703fcca2b9. Preserved APK and unstripped lib from cache5w1m164g. Not installed yet. Exported188 console through the app to a uniquely named local Downloads file, then pulled527,668bytes privately; nothing uploaded. It confirms Fifo,128 prewarmed pipelines in1.0seconds,303/303 Dawnblobhits,zero stores,20.0MiBloaded.

The exact-float prototype's expanded test compares rawFPSR and verifies QC preservation, still2,240,000cases per run. Reordered its fast-path guard to bypass Divide before checking input bits. The third private run passed; six alternating10million-call pairs measured Add19.84–20.18ns baseline versus12.26–12.60candidate, Multiply20.40–21.12 versus12.45–12.86, non-binary32Add32.20–33.24 versus32.33–33.29, wide-exponent-gapAdd30.00–30.10 versus30.41–30.56, Divide20.33–20.78 versus20.38–20.91. Game benefit remains unproven.

Started191 build(exec9244),0.5.1-exact-scalar.1:190 plus this exact-input shortcut behind the existing Android combined-FENV compile flag. Original fallback remains unchanged. Frozen baseline headers retained privately. Reused prepared190runtime without modifying it; root portable semantics is an independently compiled input. No game-source mutation while191 builds. Maintained scalar differential now accepts an optional frozen baseline semantics header and renames both evaluator namespaces to prevent weak-symbol coalescing; the expanded rawFPSR/boundary test is checked into the working diff. Its physical rerun is active separately, outside gameplay timing.

189 same-signer in-place install succeeded/readback189/0.5.1-fifo-render-policy.1. Launcher is ready for the isolated FIFO+affinity comparison against188. This comparison uses prewarm128 and no exact-float shortcut.


05:29 JST: maintained exact-scalar test physically passed the same2,240,000cases, including rawFPSR/QC equality, and replicated fast-path savings with small fallback overhead. Later test-only formatting and richer mismatch diagnostics compiled successfully; no game code changed while191 builds. Android generated-shard compile commands confirm-fno-fast-math,-ffp-contract=off,-fno-slp-vectorize, matching the differential's FP policy. Portable arm64 semantics contract (Android feature macro absent) passed250,227checks, stateHash0xccd5757c4c0643d4.

189 physical readback: frameworker19894 andpresenter19895 usecores4–7, otherobserved SDL/guest/audio threads0–7. Presenter inherited the restricted worker mask, explaining its 'retains inherited' startup message. FirstCookieLand capture activeexec56231, PID19811/surface168400, redMario. No profiling, microbenchmark or screenshots inside its timedwindow.

Read-only GitHub refresh still shows#195 updated15:44:49UTC as the latest open issue activity, followed by#316/#314. No new report changes the comparison sequence; no public replies or closures sent.


05:31 JST:189 first battle completed118.938seconds,59.300displayedFPS,86intervals over25ms,two over40ms,max49.859ms,p99 33.270ms. Appmedian59.965,min55.13,p99median20.545ms,sampledworst41.4ms; guestCPU14.726ms. Encoder mean-median5.567ms/max24.661ms; queueage0.187ms/max5.305ms; ready-to-actual33.462ms. This first result does not show an affinity gain over188first; warm comparison and resume are pending. End screenshot shows active CookieLand50.547seconds.


05:41 JST:189 warm completed119.021seconds,59.502displayedFPS,64intervals>25ms,none>40ms,max33.419ms,p9916.931ms. Appmedian59.97,min56.93,p99median23.33ms,sampledworst30.94ms,guestCPU14.708ms. Encoder5.236ms mean-median/max16.745ms,queueage0.151/max12.967ms,ready-to-actual32.022ms. End screenshot confirms activebattle49.141seconds with ink effects. Modest warm improvement versus188 is offset by worse first battle and stochastic variation; no reliable affinity gain established. Home then launcher resume succeeded visually, but every observedSDLthread mask reset to0–7 again. Reject startup-only affinity; preserve private experiment and remove hooks/helper from final source.

188warm largest49.925ms display gap first appears in the05:09:52.586 poll; the18.296ms pipelinewait at05:08:19.463 is a different event and does not explain it.

191 build finished, APK/symbols preserved, package auditpassed, private signer receipt retained. SHA2568765bdbd05cf68141169ec18590db90dbd99cbc0b6dda84bd6093fd7dec1a7f5.190 same-signer update succeeded next; measurements pending.


05:45 JST: Removed rejected affinity helper/header/test and two startup hooks, preserving private source copies and earlier fullpatches. RootCMake is restored to its prior source list. No active build was modified. Maintained scripts/test-android-present-mode.py now reproduces24 selector cases against the actual vendor function, Android/non-Android; passed. Existing phase-metrics tests passed. These are policy/aggregation checks, not physical interpolation acceptance.

190 first battle is active, PID24969/surface168449, blueMario. Bothgames were Ready after install, version190 readbackcorrect. Startup logcat observed13.037/10.555ms waits, but console export is needed for fullcache/startup comparison.

191 arithmetic shortcut increases ELF text from148,329,604 to157,333,328bytes (+9,003,724, approximately6.1percent). Data stays8,905,008bytes. This inlining cost is another reason to require measured game benefit, not promote standalone nanoseconds alone.


05:47 JST: 190 first battle completed118.892seconds,59.407displayedFPS,74intervals>25ms,one>40ms,max50.111ms,p9933.173ms. Appmedian59.92,min55.26,p99median21.095ms,sampledworst39.64ms,guestCPU14.7665ms. Encoder6.043ms mean-median/max34.475ms,queueage0.128/max11.618ms,ready-to-actual32.683ms. End screenshot shows activebattle50.643seconds and overlay53.7FPS; snapshot timing differs from the wholly-contained app windows. Direct pipelinewaits continue, including25.170ms during the timedwindow; more prewarming did not eliminate them. Memory PSS2,889,897KiB,RSS3,008,720KiB,swapPSS61,823KiB; lower than188 snapshot but scene/cache differences prevent a causal memory claim.

Verified both frozen differential baseline files exactly match the documented root/runtime commits. Added exactness argument and reproduction instructions in android-scalar-exactness.md.


05:52 JST:190 warm completed119.007seconds,59.652displayedFPS,45intervals>25ms,one>40ms,max49.988ms,p9916.861ms. Appmedian59.97,min57.06,p99median21.76ms,sampledworst46.82ms,guestCPU14.708ms. Encoder4.958ms mean-median/max14.799ms,queueage0.104/max4.511ms,ready-to-actual32.085ms. End screenshot shows activebattle49.289seconds. Started a separate30second CPU-cycle profile afterward, outside the completed timing capture; it must not be mixed into timing statistics.

Inactive188/189symbols were losslessly gzip-compressed with decompressedSHA256verification, preserving exact files and reclaiming approximately2.13GB.190/191symbols remain unpacked for direct profiling.


05:54 JST:190 separate30second CPU profile recorded20,359samples,zero lost,73.897Bsampledcycles. Symbolized against matching190libmain: ClearScalarFlags8.05percent,CaptureScalarFlags6.09percent,FinishScalarFp3.55percent,emulatedTLS2.66percent,Fmuls2.13percent. Profile finished05:51:47; the screenshot taken25seconds later shows results. It sampled near the battle-end boundary, so treat it as attribution evidence, not a matched steady-state timing run.

Exported190 console privately through SaveDiagnosticLog; no upload/draft. It confirmsFifo and255 prewarmed pipelines in3.2seconds,534/534Dawnblobhits,one store,23.3MiBloaded versus188's128in1.0seconds/20.0MiB. Larger prewarm has not established a clear game gain, and adds startup work. Keep128 for final candidate unless stronger evidence changes the decision.191 installation started for an isolated arithmetic comparison against190; both comparison artifacts still use256.


05:57 JST:191 same-signer update succeeded; readback191/0.5.1-exact-scalar.1. Both games Ready, existing Original profile used. First CookieLand capture started, PID29805/surface168519, redMario. No profiler during timing. Final source has restored128prewarm; prepared190/191sources remain untouched for their comparison.


05:59 JST:191 early windows do not yet show lower guestCPU. Building a separate private outlined-exact-scalar prototype that prevents inlining only the exact-input binary evaluator, retaining the same opaque flag helpers. This targets191's9MB code-growth cost; no production source change and no device standalone execution during timing. It must pass differential tests and game comparison before consideration.


06:01 JST:191 first battle completed118.976seconds,59.104displayedFPS,108intervals>25ms,three>40ms,max49.986ms,p9933.307ms. Appmedian58.82,min49.22,p99median23.63ms,sampledworst49.95ms,guestCPU14.783ms. Encoder6.120ms mean-median/max25.834ms,ready-to-actual33.242ms. End screenshot activebattle51.129seconds. This does not improve190first (59.407displayedFPS,14.7665msguestCPU); no arithmetic performance claim accepted. Warmrepeat and separateprofile pending.


06:04 JST: read-only GitHub refresh still shows no new issue activity after#19515:44:49UTC/#31615:40:10/#31415:39:58. No public responses or closures. Private outlined evaluator prototype now additionally admits signed-zero operands alongside normal binary32 inputs: Add/Sub bypass the exponent-gap test when either operand is zero, Multiply remains exact. Actual arithmetic is retained to preserve signed-zero rounding. Random differential inputs now inject both signs of zero frequently. This is uninstalled research, not accepted source; physical validation pending after191timing.


06:06 JST:191 warm completed118.960seconds,59.667displayedFPS,44intervals>25ms,none>40ms,max33.508ms,p9916.814ms. Appmedian59.935,min57.07,p99median20.445ms,sampledworst31.87ms,guestCPU14.829ms. Encoder6.223ms mean-median/max14.891ms,queueage0.123/max14.672ms,ready-to-actual33.189ms. End screenshot activebattle49.345seconds. Versus190warm59.652FPS/45intervals/14.708msguestCPU, this establishes no overall gain; inlined191 remains unaccepted. Separate30second profile started after timing.


06:09 JST:191 profile recorded23,242samples,zero lost,79.669Bsampledcycles. ClearScalarFlags7.93percent,CaptureScalarFlags2.64percent,FinishScalarFp1.45percent,new evaluator4.61percent. Capture work decreased, but total guestCPU did not; no overall speedup claim. Thermal snapshots differ (190warm lastBIG67C versus19179C, skin43.190/43.236C), another comparison confound.

First private outlined-prototype run aborted before differential output because its copied adapter retained the rejected explicit-context test ABI while the new runner used the maintained ABI. This is a test-harness mismatch, not a diagnosed arithmetic failure. Corrected private case.cpp from the maintained adapter and rebuilt before rerunning. Production/game sources were unaffected.


06:12 JST: corrected private outlined/zero-aware evaluator passed2,240,000 differential cases against191 semantics, including frequent signed zeros and rawFPSR/QC. Its paired microbenchmarks are slightly slower than191's inlined path; absolute times differ from earlier runs because phone scheduling/clocks differ. Whole-game code-layout impact remains unproven. Integrated as unaccepted192source, with noinline guarded to Android only, and started maintained differential directly against frozen pre191baseline.192 retains256prewarm to keep the arithmetic comparison aligned; final128default remains the intended decision. Removed affinity hooks stay removed. No fullbuild has started yet.


06:13 JST: maintained outlined/zero-aware differential passed2,240,000cases directly against the frozen pre191baseline. Started192fullbuild(exec83150),0.5.1-outlined-scalar.1, fresh build/android-outlined-exact-20260923/{runtime,native}, legacygeneratedgraph,256prewarm for comparison. Source remains fixed during build.191 remains installed for lifecycle/resize investigation; these observations will be distinguished from192 acceptance. Performance handoff and maintenance board now link this loop and record rejected hypotheses.


06:19 JST:191 Original CookieLand changed2x→1x during an active battle without invoking pause/resume. Screenshots3seconds and10seconds later show timer1:23.266→1:11.324 and different opponent/item states; log reports resolution_scale1.00 with ongoing frames. The reported freeze was not reproduced on this Pixel. At results, selected2x again; finalreadback remains to be checked. This is191 lifecycle evidence, not192 acceptance or a reporter-device fix.

Started private preserve-all-fenv prototype research with original pre191arithmetic. Clang's official calling-convention documentation supports AArch64 preserve_all for leaf runtime helpers, preserving additional caller registers; https://clang.llvm.org/docs/AttributeReference.html#preserve-all . Candidate and baseline helpers use separate symbol names/objects with identical original flag operations. Candidate disassembly uses onlyX8/X16(andW0return), with no extra stack save. Adapter object text11593→11473bytes; this is not a game gain. Physical differential is running outside gameplaytiming; production192sources untouched.


06:32 JST: verified 191's resolution dialog had 2x selected after the live resize check. Original returned to the launcher and Retro Rewind launched into the existing profile and offline battle setup. This was menu/lifecycle evidence only; no Retro battle timing was taken on 191.

192 built successfully in 14m20s, archived with symbols and passed package/signature audit. APK SHA256 b62808fb535f4b15b75aa7b0a4bf00dff0cfe7664ef2304f4d36e50b6bbf7f46. Native text is 157,708,960 bytes: outlining did not reduce the artifact size versus 191. Same-signer in-place installation succeeded; game comparison pending.

Private preserve_all helper prototype passed 2,240,000 differential cases with original pre-191 arithmetic. Small standalone operation timings improved modestly, with outliers; these are not gameplay evidence. Started candidate 193 (0.5.1-scalar-abi.1) using original arithmetic, matching preserve_all helper declarations/definitions, guarded FIFO, pipeline diagnostics, and the original 128-pipeline prewarm cap. Source is frozen during its fresh build. The maintained differential has also been built and is running on the physical device before gameplay timing. Full-library direct-call/relocation inspection remains required before accepting this calling-convention change.


06:37 JST: 192 first stationary Cookie Land battle covered 118.970 seconds: 59.309 displayed FPS, 86 intervals over 25 ms, one over 40 ms, maximum 49.973 ms and p99 33.277 ms. App median 59.94 FPS, minimum 55.32, sampled p99 median 22.78 ms, worst 43.0 ms and guest CPU 14.794 ms/present. Encoder median mean 5.805 ms (maximum 26.677); queue age 0.125 ms (maximum 8.741); ready-to-actual median 32.587 ms. End screenshot shows 50.410 seconds remaining, blue Mario with 11 CPU players. This does not establish improvement over 190. A separate 30-second profile started after the timed capture.

Maintained preserve_all differential passed 2,240,000 cases on the phone before 192 gameplay. Its helper-specific test declarations were updated to match the calling convention. A first generic function-pointer benchmark template hit Clang's calling-convention type mangling collision; using a function-value template fixed compilation. This affected the standalone test only. Production 193 source remains unchanged during its build. The additional 512-state physical test is deferred until no game timing is running.

Inactive 190/191 symbol archives were losslessly gzip-compressed; decompressed SHA256 matched before removing the original and its private profiling hardlink. Receipts retain hashes and sizes; approximately 2.18 GB was reclaimed. APKs and profile data remain available.


06:42 JST: 192 warmed stationary battle covered 119.018 seconds: 59.403 displayed FPS, 75 intervals over 25 ms, one over 40 ms, maximum 49.956 ms and p99 33.239 ms. App median 59.91 FPS, minimum 57.97, sampled p99 median 20.56 ms, worst 36.77 ms, guest CPU 14.833 ms/present. Encoder median mean 6.262 ms (maximum 21.140), queue age 0.129 ms (maximum 3.828), ready-to-actual median 33.807 ms. End screenshot shows active battle with 49.695 seconds remaining. No reliable gain versus 190; reject both exact-input arithmetic candidates and retain their evidence privately.

192's separate profile recorded 20,022 samples, zero lost, 72.955 billion sampled cycles. Clear 7.91%, evaluator 5.74%, Capture 0.99%, emulated TLS 3.00%. The after-profile screenshot shows results, so this remains near-boundary attribution rather than a steady-state comparison. Moved the game to Home only after both timing captures completed, to run the maintained FENV test outside gameplay timing.


06:46 JST: 193 built in 14m54s, archived and passed the package and same-signer audits. APK SHA256 be644861a278abe143431afb18e7e1018e8befad3662144a6717023fc21000e7. Native text 148,329,464 bytes is back near the original arithmetic size. Exact-library inspection found no dynamic relocations for either flag helper, and Add/Multiply adapters branch directly to them; helper assembly uses only permitted volatile registers and has no extra stack spills.

The maintained FENV differential passed 520,000 cases. The first capture benchmark then crashed: its generic lambda instantiated two calling-convention pointer types that Clang does not distinguish in template symbol mangling, and the generated benchmark had an invalid fall-through after a clock call. Changed that standalone benchmark to a function-value template, matching the earlier clear benchmark correction. The corrected maintained suite passed all 520,000 differential cases and 512 FPSR/QC states. No production source changed for this correction. The game helpers are direct calls, not such template/function-pointer uses.

Archived the complete 193 calling-convention patch. Started 194 (0.5.1-fifo-control.1), an otherwise matching 128-prewarm FIFO control with original calling convention and arithmetic. This permits a cleaner 193/194 comparison; no further game-source edits during the build. 193 same-signer installation is in progress. A read-only GitHub refresh still has no newer issue activity; latest public release remains v0.5.0 from September 20. No public mutation.


06:49 JST: 193 installed successfully in place; package readback confirms code 193 / 0.5.1-scalar-abi.1. Both games remain ready in the launcher and the existing Original profile opens. Preparing the same red-Mario Cookie Land workload. The pinned Dawn SurfaceConfiguration header has no exposed maximum-frame-latency setting; reducing the measured FIFO buffering would require additional renderer/backend work, not a justified settings toggle. No dependency or device system setting was changed.


06:53 JST: 193 first stationary Cookie Land capture covered 118.984 seconds: 59.268 displayed FPS, 89 intervals over 25 ms, three over 40 ms, maximum 49.992 ms, p99 33.282 ms. App median 59.73 FPS, minimum 55.64, sampled p99 median 21.35 ms, worst 37.64 ms, guest CPU 14.760 ms/present. Encoder median mean 6.070 ms (maximum 27.208), queue age 0.129 ms (maximum 5.275), ready-to-actual median 34.324 ms. End screenshot shows 50.986 seconds remaining, active opponents/items. No speedup accepted. Separate 30-second profiling started after timing; warmed capture and 194 control remain pending.


06:55 JST: 193 separate profile recorded 18,949 samples, zero lost, 69.559 billion sampled cycles. Clear 6.52%, Capture 5.04%, Finish 2.45%, emulated TLS 2.46%. Lower sample fractions alone do not prove improvement; total timed guest CPU remained 14.760 ms. The after-profile screenshot is already at Next Battle, so retain the near-battle-end attribution limit. Host phase-aggregation and nested-tracing tests pass, including enable/disable changes.


06:59 JST: 193 warmed stationary capture covered 118.968 seconds: 59.285 displayed FPS, 87 intervals over 25 ms, two over 40 ms, maximum 66.648 ms, p99 33.281 ms. App median 59.76 FPS, minimum 56.99, sampled p99 median 21.95 ms, worst 32.52 ms, guest CPU 14.664 ms/present. Encoder median mean 5.797 ms with a 71.444 ms maximum; queue age 0.125 ms (maximum 7.525), ready-to-actual median 33.438 ms. App snapshots missed the full compositor hitch, reinforcing the distinction between metrics. This does not yet establish a reliable whole-game gain. Matching 194 control is still compiling.


07:02 JST: 193 warmed end screenshot caught a large central black region; the follow-up screenshot was clear at the results menu. Re-scanned the existing visual-only Mailbox 186 recording without changing the phone. Its decoded frame 4075 reproduces a matching central blackout during the same earlier respawn cluster as the narrow bars. The scan found 158 mostly-dark central frames across 9,726 decoded frames; this heuristic is not visual correctness proof. FFmpeg reported duplicate output timestamps during raw-frame extraction; no timing statistics are derived from that scan. Frame extraction uses source-frame selection and passthrough. This visual behavior also occurs with Mailbox and the original scalar calling convention; neither new behavior is necessary to reproduce it. Exact comparison with original console behavior remains unresolved.

194 built in 13m49s and passed package/signature audits. APK SHA256 9fa51e1d543b6147543d60b476d499fd0b5a244721f70c2d020c600ef8a53d24. APK and exact native symbols are archived. Same-signer in-place install succeeded; matching control measurements follow.


07:05 JST: saved retained presentation/diagnostic source in local commits: root 0b7ecaffd52e0b4e14e81e29cfe27ccac424477c, Android runtime 8a9e885508d80d43ef4b6da88151b049b2079560. No push or public release. Existing unrelated clean-rc2.md changes remain untouched. Started normal, non-profileable candidate 195 (0.5.1-android-nightly.1) from this committed code using fresh preparation/build paths. It retains original arithmetic/calling convention and 128 prewarm. The tiny 193 warmed CPU difference remains within prior variation and does not justify the experimental calling convention; the 194 comparison continues as a final check while 195 builds. Source stays fixed during the build.


07:10 JST: 194 first stationary Cookie Land capture covered 118.971 seconds: 59.309 displayed FPS, 86 intervals over 25 ms, one over 40 ms, maximum 50.020 ms, p99 33.279 ms. App median 59.94 FPS, minimum 57.03, sampled p99 median 21.37 ms, worst 35.13 ms and guest CPU 14.725 ms/present. Encoder median mean 6.044 ms (maximum 26.096), queue age 0.130 ms (maximum 5.290), ready-to-actual median 32.104 ms. End screenshot shows 51.315 seconds remaining with opponents/items. This matching control is slightly better than 193 first, not evidence for retaining preserve_all. Separate post-timing 30-second profile started to mirror the candidate procedure; warmed control follows.


07:19 JST: 194 warmed control covered 118.935 seconds: 59.318 displayed FPS, 83 intervals over 25 ms, three over 40 ms, maximum 49.985 ms and p99 33.262 ms. App median 59.91 FPS, minimum 56.10, sampled p99 median 20.74 ms, worst 45.95 ms, guest CPU 14.768 ms/present. Encoder median mean 6.030 ms (maximum 20.608), queue age 0.138 ms (maximum 17.911), ready-to-actual median 34.656 ms. Screenshot confirms ongoing battle at 50.194 seconds. The 193 calling-convention candidate does not establish a consistent whole-game benefit; retain original calling convention. Separate 194 profile had 17,732 samples, zero lost, 66.630 billion sampled cycles; Clear 5.78%, Capture 4.16%, TLS 2.82%, Finish 1.97%. Profile screenshot is at Next Battle, so the same near-boundary attribution limit applies.


07:21 JST: Final normal private candidate 195 (0.5.1-android-nightly.1) built in 14m24s. APK SHA256 3c929e6a6de15e6455754bfc5dcb52d13e8d3ac70ffe21e0dcb627b84744ea32; exact unstripped library SHA256 509743a84e11bce05a6966eccf633841f1f13bcd9ef45194f0d7ab7b5eaf99d2. Source root 0b7ecaffd52e0b4e14e81e29cfe27ccac424477c / Android runtime 8a9e885508d80d43ef4b6da88151b049b2079560. Package audit passes; manifest explicitly disables shell profiling and is not debuggable. Signer matches the installed private lineage. In-place adb install -r succeeded; package readback confirms code195, API28 minimum and version name. Both games remain Ready to play in the launcher. Beginning exact-artifact Original/Retro and lifecycle checks. No release or public upload.


07:27 JST: Exact normal artifact 195 first Cookie Land battle covered 118.941 seconds: 59.357 displayed FPS, 81 intervals over 25 ms, none over 40 ms, maximum 33.440 ms and p99 33.279 ms. App median 59.555 FPS, minimum 58.12, sampled p99 median 22.96 ms, worst 33.95 ms and guest CPU 14.674 ms/present. Encoder median mean 5.764 ms (maximum 30.717), queue age 0.126 ms (maximum 7.907), ready-to-actual median 33.784 ms. Screenshots show blue Mario, active opponents and timer progression from 2:50.414 to 0:50.043. No external profiler was enabled. After timing, the settings dialog confirmed 2x. A 1x resize continued rendering through the results sequence, but screenshots were already at results; this is not sufficient active-battle resize proof. Restored 2x and will repeat the resize check earlier in a separate battle.


07:33 JST: Normal195 warmed battle covered 118.986 seconds: 59.066 displayed FPS, 109 intervals over 25 ms, two over 40 ms, maximum 133.243 ms and p99 33.299 ms. App median 59.69 FPS, minimum 52.39, sampled p99 median 22.55 ms, worst 136.23 ms, guest CPU 14.698 ms/present. Encoder median mean 5.689 ms with a 128.072 ms maximum; queue age 0.125 ms (maximum 18.697), ready-to-actual median 33.198 ms. This capture followed a 2x-to-1x-to-2x results-screen resize, so cache state differs from an uninterrupted warm run.

The 07:30:12.241 log reports a 123.000 ms persistent-pass pipeline wait. The same reporting interval has the 128.072 ms encoder maximum, 136.23 ms app frame and pipeline count 356 to 357, despite the later snapshot reporting zero queued pipelines. This strongly attributes one remaining major hitch to waiting for a required graphics pipeline; it does not establish all hitch causes or compilation-only duration. Do not claim stutter fixed. Skipping this wait could permanently corrupt a resolved texture; retaining correctness takes precedence over hiding the stall.

After the timing window, paused and resumed the battle. An actual in-battle 2x-to-1x-to-2x check continued rendering: timer 34.145 seconds after resume, 26.880 at 1x, changing opponents/items in the next screenshot, then 13.719 at restored2x. No pause/resume workaround was used between resolution changes. An unrelated phone notification briefly obscured the later 1x timer; that private screenshot is not published. Preparing Home/resume verification.


07:44 JST: Home/resume retained the same process and returned to the paused battle; Continue resumed rendered gameplay with timer 9.770 to 3.173 seconds and changing score/opponents. Final195 third stationary Cookie Land capture then covered 119.003 seconds: 59.419 displayed FPS, 74 intervals over 25 ms, none over 40 ms, maximum 33.490 ms and p99 33.234 ms. App median 59.71 FPS, minimum 57.89, sampled p99 median 20.74 ms, worst 35.80 ms, guest CPU 14.785 ms/present. Encoder median mean 6.132 ms (maximum 14.421), queue age 0.120 ms (maximum 5.116), ready-to-actual median 33.682 ms. Screenshot shows battle still active at 49.361 seconds. This third capture follows the live resize and Home/resume checks; retain that provenance. The earlier 133 ms hitch remains part of acceptance, not discarded as an outlier.

Verified 2x remained selected. Exported the exact195 Original diagnostic console locally; it confirms Fifo, six priority pipeline workers with one background prewarm worker, and 128 pipelines prewarmed in 0.7 seconds with 303/303 Dawn blob hits. Full Original logcat preserved before the process was restarted from completed results to select Retro Rewind. Both games remain Ready to play. Retro offline validation follows; no online-service conclusion.


07:48 JST: Read-only GitHub refresh again found no newer open-issue updates: #195 at 15:44:49 UTC (Samsung S25 Ultra slowdown), #316 at 15:40:10 (OnePlus geometry), #314 at 15:39:58 (RVZ), with existing PR317/315 unchanged. No public response, closure or release. Source review of the remaining pipeline stall confirms urgent requests already promote queued work and compilation runs outside the cache mutex. The wait protects persistent resolved textures. The retained prewarm policy uses earliest first-use order and a 128-recipe cap; a future targeted experiment needs the specific pipeline/configuration and queue-versus-driver timing, rather than another unmeasured global worker/cap increase.


07:51 JST: Final195 Retro Rewind opened the existing profile and completed an offline stationary Wii Chain Chomp Wheel Balloon Battle capture with Yoshi/standard bike/manual and 11 CPU opponents. This is a different game/course workload, not a matched comparison to Original. Covered119.009seconds: 59.449 displayed FPS, 62 intervals over25ms, two over40ms (116.605 and83.256ms), p9916.842ms. App median59.97, minimum58.51, sampled p99median21.23ms, worst30.86ms and guestCPU14.650ms/present. Encoder median mean5.417ms, maximum108.955; queueage0.131ms, maximum5.872. Screenshot confirms battle at50.984seconds with opponents. The app snapshots miss the larger compositor hitches. At07:48:59.030 a105.040ms persistent pipeline wait occurs in the capture, consistent with the encoder spike. A172.904ms wait occurred during the earlier loading/settling interval and is not included in the119second summary. No crash or online test; a warmed Retro repeat follows.


07:57 JST: Final195 warmed Retro Chain Chomp Wheel capture covered118.992seconds: 58.433displayedFPS,169 intervals over25ms,10 over40ms, maximum133.215ms andp9933.315ms. Appmedian59.575,min41.06,sampled p99median22.03ms,worst124.91ms,guestCPU14.754ms/present. Encodermedianmean5.621ms,max101.521; queueage0.127ms,max4.854; ready-to-actualmedian34.198ms. A97.110ms persistent pipeline wait is reported at07:55:11.129. This warmed run is less consistent than its first run and retains serious hitching; no general Retro performance improvement or release-readiness claim. Pause menu responded after the capture; Continue verification follows.


08:04 JST: Retro Continue resumed active gameplay (timer25.061 to17.823seconds, changing opponents). Preserved its final console and full logcat locally; FIFO and128-pipeline prewarm are confirmed again (0.8seconds,303/303Dawn hits). No native fatal, ANR or device-loss marker found in captured final Original/Retro logs. Installed base.apk SHA256 exactly matches archived195. Packaged libmain and archived symbols share ELF build ID1859b4bfef703349544978d9f3a92731f8f1c503. Final settings readback confirms Fill Screen and Normal character graphics; earlier2x readback retained. After completed battle results, stopped the game process and reopened the launcher: both games Ready to play, Ask Every Time unchanged. No game remains running; no uninstall, data clear, console identity reset or save import. Final documentation and local reviewable commit follow; no further candidate or public release is being prepared.


08:15 JST: Authorized optimization deadline reached. No build, game capture or profiler remains active. Final candidate195 remains installed; the phone is at the launcher. Source is saved in root0b7ecaf/runtime8a9e885; the documentation is committed locally with this closure. The recurring heartbeat is being disabled. Remaining graphics-pipeline stalls, manual race/audio/input acceptance, physical interpolation and other-device validation are explicit follow-up work requiring a new request after this bounded loop. No public release or issue closure.
