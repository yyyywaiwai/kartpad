# Issue #123 closed-state reconciliation

GitHub was refreshed on 12 September 2026. `gh issue view 123 --json state,stateReason,closedAt`
reports `CLOSED`, `COMPLETED`, and `2026-09-12T07:41:52Z`. The issue is no longer an
active maintenance assignment, so the committed priority queue now contains #206 as
the only active Android online-session card.

This is a process and support-state correction, not a claim that the online path is
technically fixed. The final reporter observation says disabling Retro music mostly
removed menu lag while online races still dropped to about 20 FPS; the maintainer
response records that as separate evidence. It does not establish a common cause,
race acceptance, reconnect acceptance, or release acceptance.

The selector must not spend another cycle on #123 unless GitHub reopens it with new
evidence. #206 remains independently gated on the already requested Wi-Fi endurance
confirmation beyond the prior four/five-race window.
