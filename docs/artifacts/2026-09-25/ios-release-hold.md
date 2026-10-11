# Apple release hold — 25 September 2026

The owner withdrew release approval after severe iPad menu/loading stutter.
Do not publish the prepared 0.5.1 assets. Build73 package audits do not resolve
this report; its iOS runtime is the same pin as installed build72.

Read-only device inspection confirmed 0.5.1 build72 on the physical iPad Pro.
Latest captured session selected the base game, Metal/M2, Immediate presentation,
interpolation off, normal renderer diagnostics, nominal thermal status and
power-save off. The displayed resolution scale was 4.0. No configuration or
save data was changed during collection.

The runtime logs only a one-second rolling timing window every 300 presents.
Consequently one 300-present interval lasted 11.250 seconds while the sampled
window reported 60.003 FPS. Other intervals lasted 6.819 and 6.517 seconds.
These intervals include loading/pause time and are not isolated race benchmarks.
The logs cannot attribute their full duration to a particular subsystem.
Pipeline creation increased during transitions; shader waits are a hypothesis,
not an established root cause. No fix or gameplay acceptance is claimed.

Next private candidate adds rate-limited long-present and pipeline-wait logging
without enabling expensive renderer validation. Preserve the launcher's sun/moon
and filled Retro button changes. Identify the blocking path before changing
pipeline scheduling, rendering correctness, or user settings.

Private evidence: release worktree `work/ipad-stutter-20260925/`.
Do not publish the device logs, configuration, or app inventory.

## Private build74 prepared

Clean compilation source `90f3b7b504d5c22181679f854614f1b80b42edf5`; iOS runtime
`a4b49deed7b31149475783644c21397ac890f271`. Physical iOS build and app audit
passed, diagnostics candidate NO, executable/dSYM UUID
`E274789B-09C9-3C79-B8FF-8EC2A9F07BDB`. Unsigned executable SHA-256:
`6abff0bf868e4a8470434a0c1b57348f688c8a18f3a947b5472c7a5d11bc5157`. Existing development profile and exact
certificate reused; strict signature check passed. This is a measurement build,
not a verified performance fix.

Installation is pending: an active AgePad device console session holds the same
physical iPad. Do not interrupt it. Once free, back up/read back KartPad user
data and install build74 in place. Capture the reported menu sequence and correlate
long-present messages with persistent pipeline waits before choosing a fix.

Launcher changes: compact sun/moon appearance control and filled blue Retro
action beside the red Original action. UIKit compilation and Android release
Kotlin/resource compilation passed. Existing Android game-data and artwork
contract checks passed (7 cases). Setup (Apple/Android), Support and Reporting
GitHub destinations all returned HTTP 200. Visual/device behavior still needs
verification; an updated Android APK has not been packaged during the iPad hold.
