# Combined scalar binary boundary experiment — rejected

Motivation: owner-controlled Peach Beach profile on build111 found clear/capture
helpers at8.44% of all app CPU samples, approximately15.7% of the game thread.
This was active lap3 with opponents/items and some53.75FPS intervals, not a ghost.

An isolated ARM64 assembly block combined clearing FPSR, arithmetic, reading
flags and clearing again. Production source and the installed app were unchanged.
Test artifacts are private under build/android-binary-kernel/.

Initial out-of-line and inline variants passed the original520,000-case
value/FPSCR/exception/destination/host-flags/rounding differential test and showed
synthetic gains. Stronger testing seeded host FPSR including QC, varied FPCR.FZ,
and preserved rounding. It caught host-flag regressions. Disassembly showed
Clang converting signaling-NaN classification to FCMP, which can set IDC after
the new capture boundary when FZ is enabled.

The corrected variant uses opaque integer bit extraction for classification,
keeps the original implementation for subnormal divisors, and clears the rare
NaN path. It passes520,000 seeded-register differential cases including full
FPSR equality and unchanged FPCR. This is evidence within the test distribution,
not proof for every arithmetic environment.

Six alternating-order finite-input rounds,200,000 operations per case, compared
the current implementation with the corrected candidate on the attached Pixel.
Median per-round changes (negative is faster):

| Operation | Double | Single |
|---|---:|---:|
| Add | +4.90% | -2.16% |
| Subtract | +4.04% | -2.42% |
| Multiply | +5.65% | -2.54% |
| Divide | +5.96% | -0.97% |

Decision: reject general integration. These synthetic gains/regressions do not
justify a gameplay build or an FPS claim. Earlier5-8% inline gains belonged to
an incorrect variant and are invalid for acceptance. No application update,
data reset, controls, or release occurred. The user may have kept the game open;
no thermal matching or CPU affinity was imposed, so percentages are provisional.
The magnitude and regression direction are sufficient to avoid shipping it.

Next investigation should use the existing current profile to examine another
cost rather than repeating this boundary experiment or capped replay tests.
