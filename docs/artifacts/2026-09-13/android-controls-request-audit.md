# Android controls and device acceptance — 13 September 2026

The owner accepts code78 after a playable random Retro single-player race and
reports touch settings working. The owner sees two online licenses and explicitly
accepts leaving them intact. No license deletion, merge or identity reset is
justified. Retro WFC menus may feel slower than before, but this is uncertain,
not a measured regression or online race/results/reconnect acceptance.

| Request | Actual state and next action |
| --- | --- |
| #184 shoulder to D-pad Up | PR219 merged and delivered in public code80. General race acceptance is not a physical remapping test. |
| #238 Show D-pad control | PR245 replaces the fixed-width editor. Physical code79 D-pad Hide/Show passed with both actions visible; delivered in public code80, affected reporter trial remains open. |
| FPS size | PR245 adds Small/Medium/Large. Physical code79 Large display and restart persistence passed, without changing render resolution or touch scale; delivered in public code80. |
| #119 notification/navigation bars | Correction shipped since build23, reporter acceptance pending. Verify launch/menu/resume; do not advertise as newly implemented. |
| #202 Thor fullscreen | Surface/inset boundary remains unresolved, distinct from transient bars. No projection change without reproduction. |
| #197 ipega menu input | Touch/controller failure after controller use remains open. Needs touch-only to controller-use/disconnect to touch handoff test. |
| #5 and #91 | Mainly Mac Wii controllers and tvOS DSU; separate from Android touch editor scope. |
| #162 motion steering | Reporter closed after finding existing setting. No new feature needed. |

## Signing correction

The established community release identity was located and its certificate
matches the published Android signer. Earlier missing-key reports were wrong:
the search omitted PKCS12 files. Credential contents and paths remain private.
Public APK derivation can proceed once the final candidate is accepted and its
clean release provenance, signer, archive and notices checks pass.

The code78 pre/post inventory checked identical paths, not byte hashes.
Preserve that distinction in any release notes. Two observed licenses alone do
not establish a new identity created by this upgrade.

## Menu-latency artifact comparison

The retained exact code77/pixel5 APK has SHA-256
`f6fa7ac91230f159fc2f1c34e99ff3244d4014df55dd714b5cf9cfbf0650af5c`.
Its matched native executable contains the private deferred-receive path,
including pending-receive cancellation and a direct nonblocking receive.
It is not accurately described as merely a500ms wait variant.

The accepted code78/device.1 APK has SHA-256
`c0006af78a7c59960f227592f062acda1282912fd53645ed4c0966949404a0fb`.
Its matched native executable loads5000ms before WaitForReadable for an empty
logically blocking TCP receive, consistent with reviewed main. This difference
is a plausible source of perceived menu latency, not a measured regression.
The prior private experiment lacks demonstrated delayed-response, EOF/error,
cancellation and descriptor-reuse acceptance; do not silently add it to the
FPS/editor release.

Next measurement, when the owner is not playing: one same-profile Wi-Fi WFC
entry, correlating visible frame gaps with receive-wait durations. Preserve
licenses and saves and do not log network payloads. Only if multi-second waits
correlate should a narrow lower-wait candidate be compared, including slow-login
success; keep networking changes separate from HUD sizing.

The next networking candidate also needs stronger host coverage: immediate and
partial data, delayed data on both sides of the proposed wait, timeout/EAGAIN,
EOF, readiness followed by error, and preservation of nonblocking/UDP behavior.
The current blocking-stream tests cover the policy constant and flag combinations
only. Any deferred receive experiment additionally needs cancellation, descriptor
generation/reuse and exactly-once completion checks before hardware comparison.
A shorter timeout that rejects a slow valid response is not a latency fix.
