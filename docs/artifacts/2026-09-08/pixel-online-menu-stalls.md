# Pixel online-menu stall investigation — 8 September 2026

Issue #123's follow-up confirms 1x native, Original 4:3, renderer validation off,
and stalled/catch-up game audio while the native three-dot menu remains responsive.
Offline play, reached races and spectating work. The earlier mixed archive's
configured 4x/validation-on samples no longer justify requesting that comparison
again. This narrows the stalled surface to the game/runtime, but does not identify
networking versus rendering or guest scheduling.

## Source trace

The prepared Android runtime's `src/hle/net/network_deferred.cpp` already defers
DNS, nonzero poll and guest-blocking connect. Its socket dispatch still has a
250 ms `WaitForReadable` fallback in `HandleIpTopIoctlv` for guest-blocking TCP
receive without a source-address output. `HandleSslIoctlv` switches its socket
to blocking mode at SSL_CONNECT and sets 15-second host send/receive timeouts.
Android handshake/read/write invoke the mbedTLS backend directly; Retro plaintext
SSL read/write also operate inline. These are plausible stalls, not evidence that
the affected menu actually calls them. Removing the waits or returning EAGAIN
without matching guest completion/retry semantics is not an accepted correction.

## Small diagnostic candidate

`wiicompiled-android-network-stall.patch` measures completed host calls at socket
scalar/vector and SSL vector dispatch. `network_stall.h` records wall duration
and host thread CPU time only when wall duration reaches 100 ms. It emits at most
32 records per process through the existing private console/logcat metrics path.
Fields are fixed operation name, numeric command, wall/CPU duration and remaining
budget. No socket, address, hostname, payload, identity or guest-buffer content
is captured. Deferred guest waits do not count as host call time.

A later owner-tested Android candidate can use just the `KartPadNetStall` lines
around an online-menu freeze to identify whether a completed network call blocked
and which dispatch command ran. No full raw archive is required. The existing
phase metrics remain needed if no network stall appears. A permanently stuck call
or process killed before return will not produce a completed-call record; absence
of a record cannot exonerate networking. The record's CPU time includes all work
on that host thread during the scope, and is not GPU execution time. The cap can
be exhausted before a later freeze, so its `remaining` field matters.

Validation: the C++17 host harness compiled with warnings as errors, verified the
fast-call threshold, 32-record process cap, command metadata and unavailable CPU
sentinel. Patch normal/recount checks and application pass against the existing
prepared Android diagnostic source. Shell syntax and diff whitespace checks pass.
The patched socket/SSL files also pass an ARM64 Android NDK syntax check in
the existing network unity compilation, using an isolated copy and the existing
Android compiler flags. No complete APK build, Pixel runtime reproduction,
gameplay fix, or release is claimed. This change leaves guest networking behavior intact.

Integration verification: all 66 Android Python tests pass, including the
compiled timing harness and existing Android TLS contracts. The #104 follow-up
also clarifies console/health/exit file selection in the guide and export README.
