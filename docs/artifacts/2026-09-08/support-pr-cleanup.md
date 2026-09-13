# Support review and completed-PR cleanup — 8 September 2026

## Repository cleanup

All 36 open maintainer Android development-stack PR heads were verified with
`git merge-base --is-ancestor` against main
`6973c450a6d3ba7467e168fded05399cc866989f`. Their current remote heads were
rechecked before closing. They were closed as integrated, with explanatory
comments, retaining branches/history:

18, 19, 20, 22, 24, 25, 26, 27, 28, 29, 30, 34, 36, 39, 41, 43, 44, 45,
46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 68, 70.

The remaining community PR is Aedan Pilkington's macOS #112. The corrected
`271fdc1` candidate remains local and unapproved pending controller/race tests.
The portable guide is prepared in maintainer commit `05674ab`; it can be included
at integration without waiting on the contributor to rewrite machine-local notes.

## New evidence and responses

#123 reports Pixel 8 Pro / Android 17 API 37 online-menu freezes, while offline
play, spectating and a reached race work. The supplied archive identifies
Mali-G715. Its newest code-23 health samples show configured 4x, validation on,
4:3, power saver off and thermal status 0; this differs from the report's 1x
setting. Previous code-21/22 sessions are mixed into the archive. The eight exit
entries are user-requested/self exits, with unknown build/profile attribution.
They do not establish a crash/ANR or exclude a freeze. The only crash-text file
is an earlier missing-DVD-root startup and is not attributed to online menus.

The newest capture has no queued pipelines in later samples while slowdown is
still reported. Sampled presentation/worker timings are not multi-second, but
the intervals are aggregated and incomplete: this is not proof that networking
or guest scheduling is the cause. Existing code already defers DNS and nonzero
socket polls, so another blanket off-thread rewrite is not justified. Ask for
one fresh 1x/4:3 validation-off comparison, including whether audio and the native
game menu also freeze. The reporter was asked to remove the raw private archive;
no private logs, accounts, paths, packet data or assets are committed here.

The Android report now includes configured resolution/aspect and actual active
validation mode in both Share Report and the GitHub form. GitHub also gets the
device/API and game context in their correct fields, replacing the previous
runtime-profile-only performance field. This is source for a later candidate;
no new APK/IPA is published by this pass.

#105's tester confirmed current app and backups. No additional files or rated
races are needed while checked save/rating companion transfer is developed.
External output across Apple and Android is now an accepted priority with a
[concrete test plan](../../EXTERNAL-DISPLAYS.md), retaining separate mirroring
and dedicated-view acceptance. No formal new IPA before owner testing.

## Pixel follow-up at 06:19 UTC

The reporter [confirmed validation was off](https://github.com/chrissotraidis/kartpad/issues/123#issuecomment-5580249044)
during the fresh 1x Native / Original 4:3 reproduction. Their preceding reply
reports audio stalling and catching up while the native three-dot menu remains
responsive. The earlier archive settings no longer leave that comparison open.
Do not ask for it again or request another full private archive.

These symptoms justify measuring synchronous host calls made by the guest,
without establishing which call caused the reported stall. Existing deferred
DNS and poll work does not make every receive or TLS operation asynchronous.
A timing diagnostic must retain current socket semantics and avoid recording
addresses, payloads or account identifiers. A candidate needs affected-Pixel
reproduction before any claim that these freezes are fixed.
