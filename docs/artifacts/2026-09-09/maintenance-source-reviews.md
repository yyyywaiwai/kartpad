# Maintenance source reviews — 9 September 2026 (Japan time)

## iPad opening failure #135

Independent Astra Medium inspection of public v0.4.11/build26 IPA
SHA-256 `9b1df4a45743ebb6ff1716324afbfa459dd01d664eebd7ee59d8c5e0290701fa`
confirms ARM64/ALL, minimum iOS16 in both executable and plist, arm64/metal
capabilities and iPhone/iPad families. No A10X compatibility is established.

Exact-release startup presents the first-launch/chooser host before guest memory
and Aurora GPU initialization. A nil available window scene can log and return
without opening the chooser; the non-Windows runtime fatal popup only logs.
These are source-level diagnostic limitations, not reproduced causes of #135.
The reporter was asked for one exact IPA, whether the chooser appears, and a
matching system exception/termination/backtrace; no repeat installation needed.
[Request](https://github.com/chrissotraidis/kartpad/issues/135#issuecomment-5587432967).
The install guide now states the actual minimum OS and unverified A10X boundary.
No source fix, Apple build or device acceptance occurred in this review.

## Android scalar multiply context reuse

Independent Astra Medium review clears implementation `a396eda` in frozen
`e7cdf6a` for its narrow source-correctness scope. The validated CPU context is
retained only across synchronous scalar arithmetic/fenv work with no guest
callback or scheduling path. FPSCR, NI, destination suppression and return order
are preserved. Generated change is Android PpcFmulsStateInline only; Apple
preparation is unchanged. Linked probe has one context lookup instead of two.

Reviewed owner evidence: 2704 physical differential cases across four rounding
modes, exceptional operands and NI/VE settings; sanitizer checks; 66 Android
contract tests; fresh preparation differing only in the tested header. Reviewer
independently reran the sanitized executable: 2704 cases pass with no sanitizer
diagnostics. This is not exhaustive exception/nested-context coverage, exact
game-linkage acceptance or a gameplay benchmark. No blocker found in scope.

Next: verify exact generated/linked candidate identity and compare against
preview source `cecd69c` with only this helper changed, using the same scene,
settings/device, warm-up, alternating order, comparable temperatures, gameplay
correctness and frame-time distributions. The prototype multiply-only 7–8%
timing reduction is not an FPS result. No new APK, device operation or code
integration was performed; published preview1 remains unchanged.
