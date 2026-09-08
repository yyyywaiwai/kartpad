# Experimental tvOS 0.4.11 release and issue triage

Release: [v0.4.11-tvos.1](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.11-tvos.1).
Implementation/support PR: [#106](https://github.com/chrissotraidis/kartpad/pull/106).
Exact source and dereferenced annotated tag:
`e38f2b33779a47042e7f35535ca68da5d1879733`.
App: tvOS 17+ ARM64, 0.4.11/build 9, `dev.kartpad.tv`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| KartPad-v0.4.11-tvos.1-unsigned.ipa | 41,072,508 | `e8f58d70635a86bfd107ec79d4bb90ed1fec7640c4f8355162fb7f8dc5e6e7ad` |
| KartPad executable | — | `e436b81ba9e9135a3e9e576bc0278e76150e1f406cabef0fbeee198c467fd48b` |

Fresh dual runtime preparation included patchzyy's credited issue #94 numeric
serial backport. After merge, a second fresh prepared source tree matched the
build source recursively; the exact-main rebuild passed the full app audit.
The linked `SCGetProductSN_HLE` contains `rev w8, w20` followed by `str w8,
[x11]`, plus the checked `MemoryInline::Write32Slow` path. It no longer writes
the serial as a string into the guest's four-byte output.

Validation passed: 140 Python tests (including the old/new serial harness),
20 freshly built native tests, pinned references/input verification, patch
hunks, repository safety and the byte-identical SunPad donor snapshot. An
initial Python invocation omitted the builder import path; rerunning with
`PYTHONPATH=builder` passed. The old native test directory had missing binaries;
the recorded 20-test result comes from a new Debug build, not that stale tree.
The Android documentation contract was corrected to reflect the implemented
Original-only save picker rather than require the inaccurate both-profile claim.

Two unsigned IPA packages from merged source were byte-identical. The exact
IPA passed version, source provenance, ZIP, required notices (including root
GPLv3), private-data/signing/path and extracted-app/RCpc audits. Only the IPA
and `SHA256SUMS` were published. Both were downloaded anonymously to a fresh
directory and matched local bytes. The downloaded IPA passed the full audit
again; its provenance and the remote annotated tag resolve to the source above.
The release is a prerelease and does not replace the main iPhone/iPad latest
release or any other platform's assets.

No physical Apple TV installation/gameplay, production-online results,
server-history repair, Android renderer fix, AirPlay/external-output fix, DSU
implementation, or save-transfer parity is claimed. The tvOS cache storage,
Extended Gamepad requirement, local re-signing and experimental acceptance
boundary remain explicit. Existing device data was not modified.

## Support review

All 11 open issues and recently updated closed threads were reviewed; the
repository had no discussions. Replies addressed #5, #90, #91, #94 and
#100–#105, plus the unanswered GitHub/X contact follow-up in closed #62.
#92 already had the merged licensing correction and an unanswered request for
upstream review, so it was left open without a duplicate nudge. Reporter-
accepted fixes in #1, #72 and #85 were retained; no issue was closed on a build
result alone. See the [issue ledger](../../KNOWN-ISSUES.md).

The new bug form was checked on live GitHub without submitting a test issue:
title plus all seven fields sent by the mobile apps populated correctly.
The separate question/feature form rendered correctly. YAML, unique field IDs
and changed guide links were also checked. Android Original save transfer,
its missing Retro Rewind coverage, and the difference between the short report
and private renderer-log export are now documented in the
[support guide](../../SUPPORT.md).
