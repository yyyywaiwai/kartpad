# Active runtime investigation goal

Local worktree `/private/tmp/kartpad-runtime-investigation`, branch
`codex/runtime-investigation`, based on merged main `87c9ab4`. GitHub triage
and replies remain with the hourly coordinator. No published candidate yet.

## Goal and remaining work

1. Reproduce runtime waits locally, observe operations while blocked, and correct
   only demonstrated semantic defects. Build a local Android candidate with the
   verified diagnostic and rating changes.
2. Trace actual character draw inputs/generated shader/matrix selection; design
   a bounded opt-in capture or reduced replay that reproduces the failure. Keep
   renderer correctness separate from validation and FPS.
3. Improve shared Android/Apple report context: exact source/runtime/content
   provenance, monotonic timelines, bounded diagnostic output and privacy.
4. Audit Retro update compatibility across installation, launch, in-game updates
   and reports. Test old/new/mismatched/unavailable content without touching saves.
5. Audit the resulting candidate; report exact tests and remaining owner/reporter
   hardware acceptance. No formal IPA before Christopher tests and approves it.

## First result: observing unfinished network calls

Prior `KartPadNetStall` records appear only after a host call returns. The new
fixed-size shared `diagnostics/active_calls.h` primitive tracks eight concurrent
calls, using a monotonic token to protect slot reuse. No pointers, hostnames,
socket descriptors, payloads or account data are retained. A short mutex guards
metadata only and is never held during network I/O or logging.

Android's existing health worker samples once per second while the activity is
resumed. `KartPadNetWait` reports an observed in-progress call after at least
one second, once per call, capped at 32 reports/process independently of the
completed-call budget. Fields: operation (0 scalar socket, 1 vector socket,
2 SSL vector), command, observed age, remaining budget, number of calls that
could not fit in the tracker, and a process-local call token. The completed
record carries the same token. Coverage excludes deferred guest waits. Sampling
can be delayed by scheduling/health work, is stopped on activity pause, and can
miss shorter calls or process death. Absence is not proof of no network wait.
This is an Android integration of a reusable primitive, not Apple parity yet.

A synthetic local socketpair experiment holds a receiver blocked until another
thread observes the active record, then releases one byte and verifies removal.
This proves observation before completion without using any online service; it
does not reproduce #123 or establish that networking causes its freeze.

Validation: active registry tests with ASan/UBSan pass (threshold, stale token,
slot reuse, saturation, report budget, blocked receiver). Completed-call harness
passes with active logging after its completion budget is exhausted. All 66
Android Python contracts pass (4.983 seconds before final token/callback polish).
Android ARM64 NDK API-28 syntax check of diagnostic_log.cpp passes with warnings
as errors. Android Kotlin compilation passes. Full native linkage, APK runtime
sampler acceptance and affected-device reproduction are still required.

## Initial Retro audit finding

Android's release contract is generated from the Builder profile and pins
6.12.7 plus archive, Code.pul and XML hashes. Its installer checks the official
version manifest and refuses a newer required version. Android installed-tree
validation checks version and code/XML hashes; Apple's installer has analogous
checks. This weakens the premise that installers blindly fetch incompatible
latest content. Remaining audit: whether every launch and in-game updater path
honors the same contract, what older installs see after a new Retro release,
and whether reports identify content/runtime mismatch precisely.

## Other work preserved

The rating importer remains on `codex/rating-companion-validation` at `ab1f88b`.
No changes were made to existing candidate builds, app containers or signing
material. Only ignored dependency copies/build outputs are created here.

## Second result: report context and compatibility-path audit

Android short reports and private ZIPs now include structured schema-1 context;
iPhone/iPad technical reports use the same field semantics. Supported Retro
version and installed version are distinct, with absent/invalid/mismatched versus
version-only-match states. Reading is bounded to 129 bytes and only numeric
version text can enter the report. This deliberately does not label a matching
version file as a code/hash or online-compatibility check. Captured Unix time and
named platform-monotonic clocks provide correlation anchors. Export-time context
does not claim to describe every historical log. Android export README explains
unfinished versus completed network records and their limits.

The iPhone/iPad performance-report string also no longer claims every runtime
is "full-retail-simulator"; it reports the actual selected profile and configured
resolution/aspect. No macOS/tvOS report integration is claimed in this step.
Build-source/compiled-runtime provenance, historical session identifiers and
cross-platform runtime watchdog integration remain goal work.

Executable Android/Kotlin and Apple/Foundation formatter tests pass against
missing/current/newer/oversized/malformed private-text fixtures. Both reject raw
private text and omit paths. Android Kotlin compilation and release lint pass.
66 Android contract tests pass in 4.571 seconds. Retro Java version, installed
content and recovery suites compile with warnings-as-errors and pass. These
exercise malformed/version responses, numeric version ordering, mismatched
code/hash inputs, unsafe paths and storage recovery using synthetic inputs.

Launch-path findings: Android validates the installed contract in both chooser
and runtime launch. Its official-newer-version check runs in the installer,
not on each normal launch. iPhone/iPad checks the official manifest before Retro
launch, offers the installed validated version if that check fails, and requires
a newer KartPad build when the feed identifies a newer Retro release. This is a
platform behavior difference, not evidence that either installer silently
replaces compiled code with an arbitrary latest pack. No new launch blocker or
network dependency was introduced. Remaining audit: the intended offline/online
policy for newer releases and actual compiled guest update paths.

The current full iOS overlay source compiles to an IOS/minOS-16.0 object using
Xcode 26.5's iPhoneOS SDK and the current audio header. Two pre-existing warnings
remain (deprecated UI idiom helper and nullable mapping argument). The historical
check script initially failed due to stale include paths/audio API, so its old
response file was supplemented with current shared/mobile/runtime includes.
All output is isolated; this is compilation, not an IPA build or device test.

## Third result: actual submitted draw checks

Android Renderer Validation now opts into CPU matrix-selection checks in both
raw and FIFO draw submission, before the merge early return. The fixed palette
checker records out-of-range indices and nonfinite selected position/normal
matrices. Normal samples are limited to 32 distinct pipeline hashes; anomalies
have an independent 64-record allowance per process. No vertex values, models,
textures or saves are exported, and no rendering inputs are changed. Scanning
still adds validation-only CPU work after log budgets are exhausted. Valid finite
matrices can still be wrong; a clean result does not clear the CPU or GPU.

ASan/UBSan tests pass across all 256 index bytes, truncated/invalid strides,
unaligned NaN/Inf inputs and independent budgets (1 test, 1.114 seconds).
All 66 Android contracts pass (6.656 seconds). Actual ARM64/API-28 NDK syntax
compilation of the patched command processor passes. Patch apply/recount checks
and the complete fresh dual-runtime preparation pass; shell syntax and diff
checks pass. This is diagnostic instrumentation, not a corruption fix or device
reproduction. Apple renderer integration is not included.

The local candidate source was freshly prepared under build/investigation;
existing prepared sources/builds remain untouched. About 23 GiB was free before
preparation, compared with roughly 2.7 GiB per existing native build directory.

## Fourth result: online payload update boundary and combined candidate

The source trace reaches the guest executable-download path in Pulsar WiiLink.cpp:
it normally authenticates a downloaded payload and calls its entry point. KartPad's
builder instead supplies a size/hash/signature-validated pinned payload to the
translator, configures `retro_wfc_legacy_bootstrap_hook`, and the translator
requires/removes exactly that branch before static lowering. The candidate's
existing generated payload matches the profile's size and SHA-256. Its generated
mod code registers RunRetroWfcInitializer; its authentication overlay begins with
the normal stack prologue, not the old bootstrap branch. The overlay still has
a dispatch entry, which by itself is not evidence that downloading remains active.

This supports a fixed compiled online-code contract, not arbitrary live executable
updates. It does not guarantee that future servers accept this older client or
that all non-code downloads remain compatible. A future Retro code/server change
still needs a coordinated translation/build and physical online acceptance. No
server protocol or authentication behavior was changed in this investigation.

Combined local source is `dd72167`, incorporating the rating importer after
`9985008`. Fresh dual native Android build is running separately with code 24
and version `0.4.13-local.dd72167`; those are local candidate identifiers, not a
public version reservation. Release lint passed. After integration, executable
identity/save tests and 52 rating-format + 64 rating-storage checks pass; both
Android/Apple context formatter tests pass (5.281 seconds). Full link, APK audit
and disposable runtime checks remain. The attached physical phone is untouched.

## Candidate runtime checkpoint and process-context correction

The full dual Android debug candidate linked and lint passed in 9m14s. Package
audit passed, v2 signature verified, and the new JNI sampler symbol is exported.
Initial candidate SHA-256: 010622a51eae636769fc83dcf09e60990d46f9654cb1f358687d92bcd56f844a.
Disposable API36 ARM64/host-Vulkan emulator reaches the original title screen,
opens/returns through the native menu, and writes health samples with no missing
sampler warning. The first manually seeded launch lacked dvd_root and exited;
adding the fixture's normal GameData configuration resolved it. No importer
regression is claimed from that incomplete fixture setup.

Actual DocumentsUI private export succeeds: seven entries, structured current
version/content context, and no crash memory dumps. Testing exposed a process
boundary ambiguity: the chooser cannot observe the game's static active renderer
flag. The formatter now takes an explicitly supplied active flag for in-game
reports; exported context uses null and separately reports the durable configured
next-launch setting. Host tests cover configured-on/active-off and unknown active
state; both platform formatter tests pass in 6.588 seconds. A refreshed APK is
required to include this correction; the initial candidate is retained privately.
