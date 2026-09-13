# Alarm dispatch guard across guest scheduling

Following the actual-HLE sleep probe, inspection found a separate progress defect
in prepared `os_alarm.cpp`: after an alarm handler wakes a runnable thread,
`ProcessAlarmQueue` calls `RunDeferredReschedule` while `AlarmProcessScope` is still
alive. A selected guest fiber runs on the same host thread and sees
`g_alarmProcessDepth != 0`, so its calls to `ProcessAlarmQueue` return before
servicing alarms, network completions or NAND/IOS callbacks. Progress then depends
on returning to the suspended outer alarm dispatcher.

This is a reproducible source-control-flow defect. It is not proof that it caused
the 2.222-second gap in issue 123's replacement capture. That capture's validation
setting was on; the earlier validation-off symptom report remains separate.

## Trace and scope

Network DNS/poll/connect completion commits run on the scheduler thread from
`ProcessAlarmQueue`; synchronous results wake a waiter without immediate
rescheduling, while asynchronous results enter the NAND/IOS callback queue.
NAND callback dispatch copies the caller CPU context and makes that copy ambient.
The completion reschedule already occurs after the alarm-depth guard unwinds.
The remaining early reschedule was inside the alarm-handler loop itself.

Deferred VI/alarm/audio entry points use private interrupt register contexts and
suppress guest scheduling while host callback ownership remains active. Those
guards and their exception cleanup are preserved. The candidate does not change
CPU-context copying, socket behavior, native fibers, NAND drain recursion, DVD
completion behavior, or renderer state. Those paths are not generally cleared by
this targeted result.

## Change

The Android preparation patch removes the per-handler reschedule and marks the
existing final reschedule as needed when an alarm was handled. Selection happens
after the bounded alarm batch and existing network/NAND completion drains, with
the alarm-depth guard inactive. This intentionally batches rescheduling instead
of switching after each handler. Scheduler-disable and active-retrace gates still
leave the request pending. A future alarm with no handled work does not introduce
a new scheduling request.

Only Android preparation applies this patch. Apple preparation is unchanged;
macOS/iPhone/iPad/tvOS runtime behavior has not been changed or validated here.
Any shared/upstream application needs its own review and platform evidence.

## Regression evidence

`tools/run_alarm_dispatch_probe.py` extracts verbatim `ProcessAlarmQueue` and its
guard/reschedule helpers from an existing prepared source. Guest memory, callback
invocation and the fiber-selection boundary are synthetic. At that boundary a
selected fiber immediately invokes the real `ProcessAlarmQueue` to process an
available completion. No generated or translated function body is committed.

Baseline prepared SHA-256 for `os_alarm.cpp`:
`b4a85f06972355b57055da55b52344a45bf3f4a09147619ba0beefab2d7bf901`.
Candidate SHA-256:
`95429cc2381cda0f1db50307b72d225569a116fd77beb4107844fd40f4245712`.

```sh
# Baseline fails the completion-progress assertion; this option recognizes it:
python3 tools/run_alarm_dispatch_probe.py /path/to/baseline --expect-blocked
# Freshly prepared candidate passes:
python3 tools/run_alarm_dispatch_probe.py /path/to/candidate
```

ASan/UBSan tests establish that the baseline blocks the selected fiber's pump,
while the candidate permits it. They also verify no network/NAND drain occurs in
same-callback recursion, the candidate drains outer completions before selection,
callback exceptions unwind depth and disable counts, and enclosing scheduler or
retrace guards retain a pending reschedule without switching.

Normal and recount patch checks pass. Fresh Android source preparation applies
the ordered stack and final patch successfully; the probe passes against that
fresh result. Shell syntax and whitespace checks pass. There is no full-game
build, APK, device acceptance or measured gameplay improvement. Independent Astra Medium review reran both probes and verified the exact
prepared-source delta, guard/drain semantics and source hashes; no integration
blocker found. Real fiber switching, periodic reinsertion, multi-alarm fairness
and device gameplay remain outside this probe. A matched game test is required
before describing this as an issue-123 correction.
