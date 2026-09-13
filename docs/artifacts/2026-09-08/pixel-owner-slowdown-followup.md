# Owner slowdown follow-up and process-check correction

Christopher reports base-game menus/countdown/gameplay still slow, possibly
somewhat improved, with graphics looking good in this run. This is not
affected-Adreno acceptance or a quantified performance improvement.

Latest captured session base_1788868807_pid3452, installed code25a850ada.
34 performance records include20.06FPS with519pipelines queued, then35.94–
58.39FPS samples after queue reaches zero. Last sample48.20FPS,p95frame34.54ms.
No NetWait/NetStall markers in this captured session. Settings1x,FillScreen2,
validation off. Android reports thermal_status3 (severe) during the latest
health samples; battery44.0C in those records and44.6C in the live dump.
Earlier capture had thermal_status1/battery39.3C. Heat is a material confound;
these unmatched scenes/conditions cannot yield a defensible percentage gain.

A fresh20s CPU-clock99Hz simpleperf capture records2,667samples,zero lost.
Top sampled self costs: XXH3 accumulation5.17%,new clear helper3.49%,capture
helper3.15%. These percentages are on-CPU samples, not FPS or totalwall time.
No root/kernel-setting change. Profiler completed; controls left to Christopher.
Private archive, per-session consoles,health/thermal and CPU profile retained
in pixel-fenv/build/fenv-experiment/owner-live-20260908-210340.

Correction: earlier checks looked for dev.kartpad.android:game. Actual game
process is dev.kartpad.android; chooser is :launcher. Therefore earlier
no-game-process statements were not reliable, and must not be used to infer
no gameplay occurred. Saved logs include an intervening base session with
76,500frames. No logs were lost. The claim that the loop had no new gameplay
evidence was premature. Future checks must inspect actual process/activity
and log session identity, not assume a :game suffix.

Read-only GitHub refresh:15openissues,latest new report#128Retro end-of-cup
crash/systembars,already handled by coordinator. Only#94closed today. Merged
implementation PRs include#111save transfer,#114incomplete imports,#121immersive
mode; merges/support replies do not establish all reporter problems resolved.
No independent replies or release. No formal IPA before owner test/approval.

Chooser-logo request implemented in report-provenance source: Android uses
existing kartpad_app_icon without tint; iPhone/iPad uses KartPadLogo catalog
image with original colors. Image bytes match app icon exactly. Android Kotlin
compile14s pass; iphoneos actool pass. No rebuilt/installed logo candidate or
physical chooser visual acceptance yet. Both platform layouts remain unchanged.
