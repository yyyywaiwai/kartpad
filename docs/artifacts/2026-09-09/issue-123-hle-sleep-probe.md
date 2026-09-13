# Issue 123: bounded HLE sleep/rollback probe

The replacement [reporter capture](https://github.com/chrissotraidis/kartpad/issues/123#issuecomment-5589711600)
contains a 2.222-second presentation gap and an unparkable `OSSleepThread`
warning. The three recorded receive waits do not temporally explain that gap.
This experiment checks whether the actual HLE wait/rollback control flow loses
a valid completion or corrupts its wait queue under a small set of synthetic
states. It does not reproduce the reporter's game session.

## Method and boundary

Run from the repository root with an existing prepared runtime:

```sh
python3 tools/run_hle_sleep_probe.py /path/to/prepared/runtime --negative-control
```

The runner reads the prepared source without changing it. It extracts verbatim
function bodies for `OSSleepThread`, `SelectThread`, wakeup, queue operations,
and refusal reporting, together with the original internal declarations. Bodies
are assembled into a temporary translation unit at execution time; generated
source is not committed. There is no translated function or game-data input.

Synthetic seams provide sparse big-endian guest memory, CPU registers, interrupt
state, context save/load boundaries, and fiber switching. The switch seam invokes
a test completion callback; real HLE wakeup and selection then select the caller
again. This checks actual selection/queue control flow, not native stack switching.
Timer/alarm/retrace/translated callbacks are not implemented. One idle audio-poll
seam can deliver a controlled completion. The no-completion case stops after 100
idle polls, rather than claiming that intentional waiting is a deadlock.

The source reader is deliberately narrow: it locates named definitions and
balanced braces in the inspected source, without a general C++ parser. Source
changes require reviewing the extracted boundaries and reported hashes.

## Result

All six cases pass on the Apple Silicon host using Clang C++20, ASan/UBSan and
warnings as errors (unused constants from the shared header are excluded):

1. Matching contexts, enabled scheduler and runnable peer: caller waits, peer
   delivers completion, real wakeup/select restores the caller.
2. Context mismatch: post-selection rollback leaves the caller running, queue
   and links empty, suspension unchanged, and the runnable peer preserved.
3. Disabled scheduler: early refusal preserves the same integrity conditions.
4. No runnable peer: the actual idle loop accepts a completion at its third poll
   and resumes the caller. No-peer alone is therefore not a rollback case.
5. No peer or completion: bounded observation leaves a valid waiter in the idle
   loop, which is the expected condition rather than a failure.
6. One thousand mismatched-context retries: no linkage/suspension corruption;
   they do not execute peer completion or idle polling. Once matching context is
   restored, the runnable peer completes and resumes the caller normally.

The negative control removes only the rollback's queue-pointer clear in the
temporary source. The harness rejects it with `caller queue link leaked`.
Neither the prepared source nor runtime patches are modified by that control.

This is a negative result for corruption or valid-state completion starvation
within these seams. Repeated refusal can prevent progress if a surrounding caller
keeps retrying from an unswitchable context, but the fixture intentionally creates
that context. It does not show that the game entered it during the measured gap.
No runtime fix follows from this result.

## Source identity and next discriminator

Probe branch starts at `cecd69c`. The inspected prepared files have these SHA-256s:

| File | SHA-256 |
| --- | --- |
| os_sleep.cpp | 6ec755b8613cf87b88f04b2d3a62630b26ee6af39e43db600c654cbcb0bdbc68 |
| os_scheduler.cpp | 12fbb3f74a7900d0d00b408b0b7309baf2b8aa14f12c8a329c6c5758f358bfa5 |
| os_thread.cpp | d2bad5cb3b8c0f5c4d07d41903beee1ea1fa99304fc61ab3f9aeaff1a644d646 |
| os_internal.h | 1c22fbac007b504740d2cc0a638d843ba04228fcec64528a9379445490c2a344 |

Next inspect the actual producer/deferred-completion call sites and context
restoration surrounding the unparkable wait. The missing nesting-count suffix in
the capture suggests checking post-selection refusal first. The useful question
is whether a real callback returns to a guest retry loop while its completion
requires a producer boundary that cannot execute. Demonstrating that needs the
actual callback/context boundary, not more synthetic scheduler cases or a
speculative rollback rewrite. Native fiber switching, asynchronous timer races,
GPU compilation contention and the reporter's timing remain unevaluated here.

No APK/full-game build, device run, Apple release operation, or public log upload
was performed. This source-only probe is independent of every runtime package.
