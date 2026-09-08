# Preview 13–14: renderer timing and scalar status-register work

2026-09-07. Android branch only; neither a public release nor 60 FPS acceptance.
Source includes Apple v0.4.10 main `8ebefc9`; the full parity inventory remains
`android-v0410-parity-performance.md`. These changes are layered on `d057da9`.

## What changed

- Preview 13 (code 18) declares `android:appCategory="game"`. Before this,
  `cmd game list-modes` explicitly rejected KartPad as not a game. After the
  in-place update, Android recognizes it in standard mode. No game-mode,
  frequency, CPU-affinity, thermal, or global system override was applied.
- Native diagnostics now preserve acquire, encode, finish, submit, scheduled
  wait, present and total presentation durations. Worker encode/preparation
  and producer wait attempts additionally measure thread CPU time. Fixed-size
  windows log every 300 samples into logcat and the existing private console
  export. Wall-only measurements use `cpu_ms=-1`; these are not GPU execution
  timings. Wait-attempt windows are not necessarily frame windows.
- Preview 14 (code 19) avoids writing FPSR when exception bits are already
  clear. It still captures the same exception flags and preserves unrelated
  status bits. No fast-math, exception suppression, guest timing, or Apple
  arithmetic change is included.

## Evidence before the scalar change

Preview 13 reached an actual Original 50cc Luigi Circuit race using the retained
license. Injected 200 ms A presses progressed the menus, and a long A press
enabled acceleration lock. The kart reached the barrier; this was not a complete
controlled driving lap. Do not compare that camera's later near-60 FPS against
the user's more demanding driving session as proof of a fix.

A 30-second active-race user-cycle profile retained 18,390 samples. Leaf shares
of the entire app profile: scalar flag capture 7.14%, `feclearexcept` 6.83%,
scalar FP completion 4.79%, emulated TLS 4.22%, current CPU context lookup 3.60%,
and GX display-list processing 3.63%. This identifies substantial CPU bookkeeping
cost, not a complete account of every slowdown or GPU utilization.

During the race transition/early race, worker seal/encode windows were around
5–6 ms wall time (roughly 4.5–5.8 ms CPU), whereas presentation total was usually
about 1–2 ms. One transition had a 138 ms presentation outlier. Later windows
varied with the scene. Presentation is not uniformly stalled for tens of
milliseconds, but average timings do not rule out spikes or GPU backpressure.
The earlier user's 25–55 FPS reproduction remains documented separately in
`android-preview12-immediate-slowdown.md`.

## Correctness and packaging

- Physical ARM64 arithmetic differential: 520,000 cases pass, including values,
  FPSCR, exceptions, destination writes, host exception flags and rounding modes.
- Additional 512 FPSR states pass, including preservation of the unrelated QC bit.
- Clear-state microbenchmark: candidate 6.27–10.81 ns/call versus baseline
  8.44–20.63 ns/call across four sequential pairs. Device clocks warmed up over
  the test. This supports the exact-operation fast path, not a measured overall
  race speedup.
- Phase aggregation tests and 133 Python contracts pass (`PYTHONPATH=builder`).
- Fresh complete Android patch preparation passes; the prepared Aurora source
  matches the source consumed by the build.
- Unchanged AAB and APK audits pass. ARM64, min API 28, target SDK 36,
  `dev.kartpad.android`, non-debuggable. Local profiling is enabled explicitly.

## Installed private candidate

`0.4.10-android-preview.14`, version code **19**, locally debug-identity signed.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| AAB | 91,220,618 | `1aeb7de5ab214ce35402499bf4b2fc2c4bd47776a4fb790132778544865c0e45` |
| APK | 110,323,026 | `d0951840d2e20c912c50be3a137bd25895cf91cf9cad61cc4e9bb260b0e1e1c2` |

Local APK: `.android-bootstrap/hardware-preview/KartPad-0.4.10-android-preview.14-v19-arm64.apk`.
The unsigned AAB is `android/app/build/outputs/bundle/release/app-release.aab`.
These artifacts must not be committed, uploaded, or published.

Phone: Google Pixel 9 Pro XL, API 37, ARM64, 4096-byte pages. Exactly one
authorized physical target, no emulator. Guarded update-in-place passes.
Fresh 2,867,200-byte Original save exports match byte-for-byte before and after
code 18 and code 19. No uninstall, data clearing, downgrade, license editing,
or game-input replacement occurred. The installed Retro Rewind 6.12.7 profile
remains visible in the selector.

## Open acceptance

Post-update Original boots and reaches the same 50cc Luigi Circuit race. Menu
rolling samples still dip to roughly 45–53 FPS with no queued pipelines. The
race later reports approximately 56–60 FPS at the barrier/grass camera; reverse,
steering, acceleration-lock release and guest pause respond to injected touches.
This is still not a controlled lap or proof of stable driving performance.
The phone reports thermal status 1 during this warm test. A second 30-second
race profile has 17,469 samples and zero lost samples: scalar flag capture 5.79%,
`feclearexcept` 7.61%, scalar completion 2.67%, emulated TLS 3.99%, current context
2.41%. These relative shares come from sequential, non-identical scenes and
must not be presented as a causal overall speedup.

Sustained 60 FPS, matched cold/warm races, full touch/controller/motion behavior,
physical audible audio/haptics and complete Apple parity remain open. The capture
summary has not passed the complete physical signal matrix; missing controller
and lifecycle/audio evidence is not waived. Raw logs, diagnostic exports, CPU
profiles, screenshots and saves remain ignored and local. Do not merge Android
to main or publish packages on the basis of these checks.
