# Pixel online log review

[#123 reporter excerpt](https://github.com/chrissotraidis/kartpad/issues/123#issuecomment-5588528774)
was reviewed by Astra Medium against published cecd69c diagnostic semantics.
Reporter says 0.4.13; the excerpt itself omits exact build/provenance/settings,
so this session is not independently identified as build28. Earlier confirmed
Pixel/profile/settings remain historical context.

| elapsed_ms | FPS window | CPU interval | Queued pipelines |
| --- | --- | --- | --- |
| 11931421 | 48.74 FPS,50 samples,p95 26.20ms,worst156.83ms | 46.7% over6.831s | 43 |
| 11939444 | 37.90 FPS,41 samples,p95 59.69ms,worst149.94ms | 70.8% over8.022s | 0 |

Presentation statistics cover timestamped intervals in the last second,
sampled after another300presentations. CPU is calling-thread time/wall time in
a separate interval, not measured network latency. Phase windows also differ;
cpu_ms=-1 means unavailable, not GPU time. Zero queued pipelines at the second
snapshot does not exclude earlier compilation or all graphics waits.

Scheduler recovery warnings are present but do not establish a repeated busy
loop or the reported multi-second freeze. Failed-park warning frequency is
limited per guest thread. No definite defect or root cause is established.

No NetWait/NetStall or health samples appear in this selected paste. Network tags
are emitted through the same console/stderr mirror as performance metrics,
not into android-health.log. Completed >=100ms and active >=1s timers each have
32-record budgets; active tracking holds8calls and samples about once a second.
Guest scheduler waits are outside them. Absence from a selected excerpt cannot
clear the network path.

[Requested existing-file excerpts](https://github.com/chrissotraidis/kartpad/issues/123#issuecomment-5589280002):
same-session console network tags and health samples around elapsed_ms11920000
through11950000. No new run or full archive requested. An overlapping timed
host call with wall time far exceeding CPU would guide network investigation;
otherwise confirmed context plus scheduler/producer evidence guides the next
bounded experiment. No code change, build or device operation in this review.

## Superseding definitive capture

[Replacement attachment and health](https://github.com/chrissotraidis/kartpad/issues/123#issuecomment-5589711600)
supersede the earlier paste. They establish build28/API37, Retro,1x/4:3,
validation ON, Vulkan/Mali-G715, thermal0,battery30.4–31.1C, unplugged and
power-save off. This is separate from the prior validation-off reproduction;
thermal samples alone do not prove unrestricted clocks.

At elapsed52362329,15 presentation samples include worst2222.337ms and5.546FPS.
The window selects intervals ending in the preceding second; interval starts
can precede it. Assuming clock alignment, long-gap start lies approximately
52359107–52360107 and end52361329–52362329; these are inferred bounds.

Three IOCTLV_SO_RECVFROM(command12) records finish at52358804,52367420,52372668,
with wall112.205/228.193/110.337ms and CPU0.081/0.551/0.136ms respectively.
None overlaps the inferred long gap. No NetWait record appears; completed-call
budget remains29. This does not exclude untracked calls, repeated short waits
or guest scheduler delays. Do not add these separate receive durations into a
single stall. Whole-handler timing does not identify an internal syscall/mode.

CPU64.7% over12.818s and the nearby300-operation phase batch do not classify the
gap itself as busy/blocked. Measured present max7.948ms and worker max15.580ms
exclude neither time between jobs nor all producer waits. Prewarm completes
nearby; queue0 is after completion, not proof against prior contention.
Later59.01FPS at52378797 describes only the final sampled second after16.467s
for300morepresents, not uninterrupted smoothness.

OSSleepThread failed-switch/retry warning lacks the optional nonzero scheduler
nesting suffix. Inspect the post-SelectThread rollback/refusal path, without
assuming this untimed warning caused the gap. Existing guest_scheduler_tests
cover another abstraction and do not validate this exact HLE path.

Astra Medium completed a host harness around actual prepared os_sleep and
os_scheduler control flow: enabled/runnable completion yield-resume, invalid
context/no-peer/disabled rollback integrity, and deferred-completion retries.
All six bounded sanitizer cases pass, and a deliberately broken queue rollback
is rejected. No valid-state starvation was reproduced. See the [probe and its
limits](issue-123-hle-sleep-probe.md). Next inspect actual producer/deferred
completion context restoration; no speculative runtime rewrite or further
reporter run is justified by this test.
