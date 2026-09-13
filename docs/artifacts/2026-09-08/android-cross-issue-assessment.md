# Android cross-issue assessment — 8 September 2026

This is a read-only issue/source synthesis, not a new runtime fix or device test.
The coordinator retains public replies and integration. Existing builds and
installed Pixel code25 remain unchanged.

## Evidence and distinct failure paths

- #102: corruption in Original and Retro at 1x/4:3, roughly 60 FPS; synthetic
  compute/indexed draws pass, actual validation/robustness comparison unchanged.
  Investigate actual game draw inputs, generated shaders and resource lifetime.
- #104: S24 Ultra/Adreno750 character corruption already in vehicle selection,
  persists at 1x/4:3; karts/track recognizable. Both probe suites pass. Reimport
  did not help. Actual-game validation result remains outstanding. Do not
  request repeated probes, imports or broad archives. Character transforms and
  generated character shaders are the narrower starting point; shared cause
  with #102 is not established.
- #120: stretched geometry on OnePlus; retain as a separate observation until
  actual renderer evidence identifies a common mechanism.
- #123: Pixel8Pro online menus stall, audio catches up, Android menu responsive;
  offline/racing/spectating can work. 1x/4:3/validation off already confirmed.
  Inline network waits are an architectural lead, not a confirmed diagnosis.
  Completed-call diagnostics alone miss indefinitely blocked operations; local
  candidate adds in-progress observations. Preserve guest retry/completion rules.
- #103: S25+ clean graphics, frame dips; changing both Game Booster power mode
  and resolution confounds the reported improvement. Low GPU utilization does
  not identify the waiting subsystem.
- Owner Pixel9ProXL: base gameplay queue-zero samples35.94–58.39FPS, severe
  thermal status and44–44.6C battery. Earlier capture was cooler. No defensible
  percentage FPS improvement; no basis to explain #123 with this thermal result.
- #128: Retro end-of-cup crash is a distinct transition failure. Need matching
  exit/transition evidence already requested by coordinator, not repeated cups.
- #119: immersive-mode fix passes emulator checks; persistent AYN Thor bars
  mean affected-device acceptance remains open.

## What changed versus what is demonstrated

Public Android build23 includes profile-aware save targeting, failed-restore
startup protection, incomplete-import/storage-exhaustion handling, immersive
mode correction, actual renderer validation and OS exit records. It does not
establish fixes for corruption, online freezes or sustained full-speed play.

Private Pixel code25 includes conditional exception clearing:520,000 physical
semantic cases and512 flag states pass. Ten synthetic operations improved
6.1–8.7%, conversion15.9%; single sqrt regressed3.7%. These are not FPS gains.
Later source adds report provenance for Android/iPhone/iPad, matched chooser
artwork, and rating-import durability/config corrections. Rating changes need
coordinator review before integration; no existing APK contains5652a7f.

## Next local work, in priority order

1. Reduce profiled CPU overhead with a narrowly verified experiment: actual
   prepared ppc_runtime.h reads CurrentCpuContext before scalar evaluation and
   again in PpcCommitScalarFpInline. The checked-in source of these adapters is
   patches/wiicompiled-apple-runtime.patch, not the host translation shim.
   Cache the context only within a single operation after establishing that
   evaluation cannot switch guest context. Require equivalence/NI tests and
   linked ARM64 lookup-count evidence before considering an APK. Do not edit
   generated headers alone or replace thread-local context globally.
2. Trace an actual character draw and its matrix/palette indexing, shader and
   buffer ownership. Passing generic GPU probes does not validate those paths.
   Prefer a reduced deterministic reproduction over another generic log switch.
3. Use existing in-progress wait diagnostics to distinguish #123 inline blocking
   from guest scheduling/render stalls; do not change socket semantics speculatively.

No additional broad log submission is required from Christopher to continue
source work. Later acceptance requires a cooled same-scene Pixel comparison,
affected Adreno character validation, online-menu testing and the separate cup
transition result. Apple report/share and chooser changes require iPhone/iPad
acceptance; no macOS/tvOS performance improvement follows from Android results.
Android packages are APKs; an IPA is an iPhone/iPad package. No formal IPA before
Christopher tests and approves it.
