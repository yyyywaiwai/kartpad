# iPad build57 shader-compilation crash — September 20

Owner testing found a real failure after installation. At 09:58:06 +0900,
KartPad 0.5.0/build57 terminated with SIGABRT. The crash UUID matches the
retained build57 symbols. This is an app crash; the report records about
410,000 seconds of device uptime and the retrieved inventory has no matching
new panic or Jetsam report.

The faulting pipeline worker entered operator new, threw through __cxa_throw,
and reached the C++ terminate handler. Its callers are Tint uniformity graph
construction, Dawn shader-module creation, Aurora build_shader/create_pipeline,
and compile_pending_pipeline. This establishes an unhandled allocation failure
while compiling a shader, not the previously corrected partial-startup cleanup
fault.

The session enabled six background compilation workers. Physical footprint grew
from 1,633,896,416 to 2,518,289,000 bytes over ten seconds; the last frame sample
still had 777 pipelines queued. The failure therefore occurred during continued
background compilation, even if the visible loading screen had finished.
Parallel compilation pressure is a strong lead, not yet a proven complete cause.

The subsequent session completed 2,244 prewarm pipelines in 2.6 seconds, reported
5,152 cache hits, and recorded approximately 60 presentation FPS for over a
minute. This is consistent with a warmer cache making the retry less expensive;
it does not clear the failed initial-start case or establish race performance.

The prepared physical-iOS source retains six background workers on this device;
only Simulator worker count is capped to one there. Android has separate bounded
prewarm controls. The next correction should bound physical-iOS speculative
compilation and verify a cold-cache launch without changing the owner's saves,
settings or active session. Do not treat a warm retry as the regression test.

Build57 is blocked from release pending correction and verification. Raw device
reports and logs are private in work/ipad-build57-20260920/incident. No app,
cache, save, configuration or running session was changed during this inspection.

## Subsequent gameplay crashes and correction

Two further build57 reports at 10:00:04 and 10:05:12 +0900 are a different
failure. Both abort through the WebGPU error callback during TexCopyConv Blit
in asynchronous EFB RAM readback. The destination attachment is RGBA8Unorm,
but the blit pipeline was created for the BGRA8Unorm presentation surface.
These sessions had already completed prewarm. Their failures cannot be cleared
by the successful warm startup observation above.

The existing Release Mac probe disabled Dawn validation, unlike physical iOS.
Rebuilding its GPU initialization with only skip_validation removed reproduces
the exact attachment mismatch and abort using the old renderer. The original
pixel-only passing result did not validate this pipeline contract.

All four maintained runtimes now create RGBA and BGRA blit variants and select
by the actual destination texture format. Initialization builds both before
worker use; rendering only reads them. Apple runtimes also adopt the already
implemented Android 128-recipe shared prewarm budget, one background compiler,
and demand-promotion wakeups. Cache files and demand compilation remain intact.

The validation-enabled real Metal probe now passes the formerly failing native
readback plus all existing independent-pixel, offscreen, capacity, interpolation
and frame-worker cases. A separate empty-Dawn-cache run seeded with the actual
1,199-row bundled recipe database completes bounded prewarm and the full probe
in 7.25 seconds; host maximum RSS is 355,926,016 bytes and reported peak memory
footprint is 786,433,296 bytes. This is host renderer evidence, not an iPad memory
or gameplay measurement. The SQLite/admission/worker production-function test
passes under ASan/UBSan for all four runtime pins and is now included in CI.

Artifacts and commands are private under work/ipad-repeat-fixes-20260920.
Replacement app builds and physical gameplay acceptance remain pending.

## Build58 installed for owner testing

Clean source e8f2363 produced audited iPhoneOS build58. Its dSYM matches the
app; a development-signed copy passed signature verification and was installed
in place after the owner explicitly confirmed readiness. A fresh backup and
post-install readback match all 30 save/settings files, including the current
license/save data. The existing WBFS and extracted data remain. The app was
launched and confirmed running. No owner cache was cleared. See
release-050-build58-ipad.json for identities and remaining acceptance limits.

Build58 is a replacement for testing, not release approval. Android code133 and
Mac build57 have not been replaced by new app packages in this iPad handoff.
