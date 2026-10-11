# Android second-review prompt — 25 September 2026

Review KartPad's latest Android candidate and propose the next concrete fixes
for reported Android compatibility and performance problems. Work only on
Android. Return your findings and any tested patches to the coordinating bot
for incorporation into the next build; do not publish, merge, install on the
phone, or contact reporters yourself.

## Starting point

- Repository: https://github.com/chrissotraidis/kartpad
- Existing working checkout: `/Users/chrissotraidis/.codex/worktrees/kartpad-stabilization-20260918`
- Branch: `codex/upstream-all-platforms-20260922`, draft PR #317.
- Evidence baseline: root commit `b7560a6`; Android runtime
  `27074c26ac4f630b88814851db58cd81bb52e5c4`.
- Latest public Android: v0.5.0/code135, compiled source `a2f41d5`.
  Current private Pixel candidate: code218, `0.5.1-gx-nodraw.2`.
- Read repository instructions and `docs/SUPPORT-AGENTS.md`. Preserve unrelated
  edits, especially `docs/artifacts/2026-09-22/clean-rc2.md`. Coordinate before
  editing the shared checkout; use a worktree under `~/.codex/worktrees` if needed.

## Read first

Relative to the working checkout:

1. `docs/artifacts/2026-09-25/android-code218-pixel.md` — current acceptance,
   issue disposition, limitations and support replies.
2. `docs/artifacts/2026-09-24/current-private-builds.md` — build chronology.
3. `docs/artifacts/2026-09-23/android-morning-report.md` and
   `docs/artifacts/2026-09-21/README.md` — earlier measured changes.
4. `work/android-pixel-comparison-20260925/owner-retro-online-094718-analysis.md`
   and its matching raw log/receipt/audio. These are private local evidence.

The owner completed a Retro online race on Pixel build218 and reported better
stability. No more owner testing is requested. This is not proof of an Adreno
fix or a measured code135-to218 speedup. Older documentation may be stale;
reconcile it against current source, dated receipts and live issue discussions.

## Investigation

Refresh GitHub issues and read existing attachments and complete conversations.
Prioritize #321 (Adreno740 launch SIGSEGV), #316/#308/#104/#211 (geometry),
#320/#195 and related performance reports, and #319 (physical-controller
acceleration; current latch is touch-only). Use supplied evidence before asking
for more. Group by actual device/GPU/build/profile/symptom and stack signature;
do not assume all Android or all Adreno failures share one cause.

Compare code135 with218 and classify each report: directly addressed,
plausibly helped, unrelated, or unresolved. Explain each correlation using
source and log evidence. Distinguish fixes to public bugs from regressions
introduced and repaired during private development.

Investigate the Pixel's remaining 106/129 ms pipeline waits and 1,014 ms game-thread
socket receive near the capture boundary. FPS logs are sparse snapshots, not
whole-race statistics; buffered pre-capture lines must be separated. Preserve
network authentication semantics and texture-copy correctness. Avoid speculative
GPU workarounds, timeout reductions, or broad rewrites without a reproducer.

## Return to the coordinating bot

Provide a concise issue/evidence matrix, the top 1–3 actionable improvements,
exact source locations, and focused reproduction/validation results. If a fix
is well supported, supply a small tested patch or commit with risks and remaining
device gates. Update dated documentation for new findings and identify stale
claims. Keep private logs/game data out of commits. Report exact root/runtime
commits and build implications. Do not claim untested devices are fixed or ask
users for targeted retests before an updated APK is publicly available.
