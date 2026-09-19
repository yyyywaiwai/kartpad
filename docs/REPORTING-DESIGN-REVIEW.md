# Reporting review — 14 September 2026

## Decision

Use one reporting policy for macOS, iOS, iPadOS and Android. Do not infer the
owner from a symptom category. The creator's stated concern is discovery of
WiiCompiled and reports about defects within it, not a request to forward every
in-game failure. Visible credit alone does not provide an effective report path.

The current mobile preview is exploratory. It does not demonstrate macOS or
iPad layouts, and its game-rules-to-upstream default is not a validated ownership
rule. Do not port that rule into native clients.

## Smallest useful next iteration

1. Keep the short description and strongly recommended diagnostic log.
2. Make both destinations visible, with one sentence: “KartPad uses WiiCompiled.
   You can report directly to either project.” Do not hide upstream behind Change.
3. Provide “Search reports in both projects” using GitHub's multi-repository
   issue search. Avoid a growing hard-coded issue catalog or a classification
   service. Keep any curated examples narrowly scoped to verified conditions.
4. Let users add logs directly to an existing matching issue. A similar title is
   only a comparison lead; platform, trigger and error details still matter.
5. For a new report, offer KartPad for this port/device or uncertain problems,
   and WiiCompiled for a known upstream problem. Explain the distinction beside
   the two choices without requiring the user to diagnose source code. Preserve
   the description and collected evidence when changing destination.
6. Include the failed session's platform, device/OS, KartPad build, native
   revision, upstream baseline when recorded, renderer, game/pack and runtime
   logs. Unknown metadata stays unknown. App version must not masquerade as the
   upstream runtime version; an old session must not inherit today's build ID.

Search URL:
https://github.com/search?q=is%3Aissue+repo%3Achrissotraidis%2Fkartpad+repo%3Apatchzyy%2FWiicompiled&type=issues

Keep closed results discoverable: a resolved upstream issue may already be
backported, or may identify an outdated build. Linking an upstream report is
not proof that an installed KartPad build contains or lacks the fix.

## Boundary that UI cannot remove

The live upstream in-game bug form requires latest-WiiCompiled and
not-on-Dolphin/Wii confirmations and asks for Windows information. Modified
KartPad users must not be told to check unverified statements. Existing-issue
comments offer a direct evidence path; new reports must respect upstream intake.
Do not bypass its forms, duplicate every issue, silently upload logs, or promise
acceptance. Unknown new failures still need investigation somewhere. Zero
manual triage and reliable automatic ownership cannot both be guaranteed.

No ongoing maintainer coordination is required for links, useful logs or direct
existing-issue participation. A change to upstream's own intake would require
its maintainer's agreement. Do not represent that agreement as obtained.

## Native scope and verification gates

| Platform | Scope | Acceptance still required |
| --- | --- | --- |
| Android | Same policy, native report screen and failed-session export | Actual report-to-browser/share round trip, permission failure, crash/relaunch session selection |
| iOS | Same policy, native report sheet and share/browser handoff | iPhone layout, return/cancel, saved description, correct failed-session metadata |
| iPadOS | Same policy using Apple implementation | iPad sheet/popover presentation and actual log/browser round trip |
| macOS | Same policy, Help menu and save/browser handoff | Desktop layout, saved log, actual draft opening and return |

The reporting source changes are merged in PR #279. Android code90 and Apple
build42 are separate reporting prereleases; physical flow acceptance remains
pending. The browser prototype is exploratory and is not the native product.

## Implementation priorities from source review

- Android: replace the private-ZIP/extract/select-file burden with one directly
  shareable reviewed runtime text report for normal intake. Keep private
  diagnostics separate.
- Apple: stop opening the upstream non-crash bug form for every report type;
  choose the appropriate form or upstream chooser without making preflight claims.
- macOS: preserve runtime startup/version headers as well as bounded failure
  tails and connect saved diagnostics to the reporting handoff.
- All platforms: keep one vocabulary and preserve answers across cancel, retry
  and changing project. Test these actual native flows before claiming parity.

## Fork decision

Keep repository identity for this reporting change. Forks have separate issue
trackers; a fork badge will not forward reports or logs. A genuine new fork is
supported but entails a migration, not conversion via a documented public API.
An optional Support inquiry is not a guaranteed attachment mechanism. See
[FORK-OPTIONS.md](FORK-OPTIONS.md). Do not rename/delete/recreate KartPad merely
to obtain the badge.

## Evidence

- [Android vertex corruption #102](https://github.com/chrissotraidis/kartpad/issues/102): Samsung/Adreno-specific reports; symptom does not prove upstream ownership.
- [Upstream Android support #54](https://github.com/patchzyy/Wiicompiled/issues/54): upstream Android support remains an open feature request at review.
- [Upstream bug form](https://github.com/patchzyy/Wiicompiled/blob/main/.github/ISSUE_TEMPLATE/2-bug-report.yml): required confirmations and platform fields checked live.
- [GitHub issue search](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests): supported multi-repository search.
