# Maintenance selector correction for Android issue #123

The hourly selector previously assigned issue #123 to
`scripts/test-android-network-receive-window.sh`. That was stale work: the
Android-only 500 ms receive-window candidate reached the Retro WFC dashboard,
then still disconnected before a Retro VS race. Its host contract can pass
without changing the unresolved lobby-to-race boundary.

The selector now reports #123 as externally blocked and points only to the
fresh-source trace and physical Retro VS session gate recorded in
`EXTERNAL_NEXT_ACTIONS`. It no longer returns an executable local test plan for
the obsolete receive-window candidate.

Validation:

- `python3 -B -m unittest -v tests.test_maintenance_loop.PriorityExecutionTests.test_issue123_does_not_repeat_obsolete_receive_window_plan`
- `python3 -B -m unittest -v tests.test_maintenance_loop`

This is a maintenance-process correction, not an Android network fix. The
issue remains open until a fresh trace attributes the lobby-to-race transition
and the same candidate passes physical WFC race, results, return and re-entry.
