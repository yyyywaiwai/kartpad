# Preview 28 graphics evidence boundary

Issue #137 identifies the exact released `cecd69c` source and fingerprints,
Original/base with Retro not installed, Android16 and SM-S948B. GPU/driver is
not inferred from that model. Similar symptoms link #102/#104/#120 without
establishing a shared cause. Existing settings/reimport tests should not repeat.

Astra Medium verified the current draw audit patch is present in preview28,
including ordinary and merged/raw GX draws. The helper passes its focused
ASan/UBSan test. Existing affected-session console excerpts are the next input:
Graphics adapter information (API/device/full driver), renderer diagnostic mode,
KartPadDrawCheck lines and any relevant pipeline/device-loss error.

Draw checks cover direct PNMTXIDX only. Per-process budgets allow 32 distinct
normal pipelines and 64 anomalies. Selected-matrix nonfinite counts do not
inspect vertex attributes; pn_outside means a selected palette slot outside ten
slots, and incomplete spans fail the scanner. pn_nonmultiple alone does not
set anomaly. Positive findings can direct investigation before GPU execution.
Clean/absent samples cannot exclude finite-but-wrong transforms, vertex inputs,
uniform/upload lifetime or unsampled draws, and do not prove a driver defect.

No new instrumentation or reproduction test is justified until these existing
samples are examined. For flagged pipelines compare selected slots with shader
layout; clean samples require isolating an actual character draw/upload/shader
boundary rather than another broad settings or standalone-probe sweep.
No game build, device action or verified graphics correction in this review.
