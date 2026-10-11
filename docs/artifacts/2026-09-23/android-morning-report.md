# Android overnight optimization — September 23

Status: the authorized overnight loop is closed at the 08:15 JST deadline. Private build 195 is installed; bounded device validation and evidence preservation are complete. Remaining stutter and release gates are recorded below.

## Result

The strongest change is steadier Vulkan presentation at the game's native frame rate. In the matching FIFO/Mailbox comparison on the attached Pixel 9 Pro XL, warmed stationary Cookie Land battles delivered **59.181 versus 56.592 displayed FPS**, with **102 versus 403 intervals longer than 25 ms** over approximately 119 seconds. That is about 75% fewer long display intervals in this comparison. Other FIFO observations support the direction, but their additional experimental changes make them less clean comparisons.

This is a frame-delivery improvement, not evidence that the game simulation became substantially faster. It also adds approximately **8.7 ms of frame-ready-to-display buffering** in the matching comparison. That measurement is not controller input latency. Subjective responsiveness still needs the owner's assessment.

## What changed

- Prefer FIFO only for Android Vulkan with frame interpolation disabled and FIFO supported. Retain the prior selection policy for interpolated output and other backends.
- Reconfigure the surface when interpolation changes between enabled and disabled, using the existing worker/presenter synchronization.
- Record presentation queue age and missed presentation deadlines separately.
- Report graphics-pipeline waits of at least 8 ms, at most once per second and after releasing the cache mutex. Pipeline waits still occur; the diagnostics make them attributable.

## Experiments not retained

The explicit scalar-context generator change, larger display-list front cache, borrowed cache metadata, startup CPU affinity, doubled pipeline prewarming and exact-input arithmetic shortcuts did not establish a reliable overall game improvement. Their source variants, artifacts and measurements are retained privately. The original arithmetic and 128-pipeline prewarm limit remain the conservative baseline. The helper calling-convention prototype passed correctness tests, but its comparison with the original convention remained within prior game-timing variation. It is excluded from the final private build.

DriftDroid was revisited against the previously audited source revision. Previously integrated caching/linking/audio work is not counted as new progress. Native TLS and more aggressive floating-point shortcuts were not promoted without evidence of benefit and preserved behavior.

## Community reports

The supplied Reddit comments informed sustained-performance and resolution-change checks. On this Pixel, changing 2× to 1× during an active battle continued rendering without pause/resume; 2× was restored and verified. This does not close the reported freeze on another device. Existing full-screen/aspect and controller-remapping features were checked before treating requests as missing features.

The latest read-only GitHub review found no newer issue activity than the already-reviewed Samsung slowdown, OnePlus geometry and RVZ reports. No issue is closed from these single-device results, and no new public build was published by this loop.

## Evidence and acceptance limits

Measurements use the existing Original profile, 2× rendering, and stationary Balloon Battles with 11 CPU opponents. They are not manually driven races. Screenshots bracket timing windows; separate CPU profiles are excluded from those windows. Item activity, teams, cache population and thermal conditions vary. App snapshot FPS, measured guest CPU and displayed cadence are reported separately.

All candidate installations used the existing signer and `adb install -r`; no uninstall or app-data clear was used. Existing game readiness, profile access and visible preferences were checked. Final readback retains 2× rendering, Fill Screen, Normal character graphics and Ask Every Time on launch; no identity reset or save import was performed. The non-debuggable app does not permit a full before/after private-container hash audit, so that stronger preservation claim is not made.

Retained source is saved locally in root commit `0b7ecaffd52e0b4e14e81e29cfe27ccac424477c` and Android runtime commit `8a9e885508d80d43ef4b6da88151b049b2079560`. These commits have not been pushed. The existing stabilization worktree holds the source and private artifacts; unrelated primary-checkout and RC2 documentation changes are preserved.

## Exact final-artifact observations

Build 195 completed three stationary Original Cookie Land timing windows at 2×. Each covers approximately 119 seconds. The latter two followed the documented resolution/lifecycle checks, so they are acceptance repeats with different cache history, not independent matched controls.

| Window | Displayed FPS | Intervals >25 ms | Maximum display interval | Guest CPU ms/present |
|---|---:|---:|---:|---:|
| First | 59.357 | 81 | 33.440 ms | 14.674 |
| Warm after resolution restoration | 59.066 | 109 | 133.243 ms | 14.698 |
| Repeat after lifecycle checks | 59.419 | 74 | 33.490 ms | 14.785 |

Pause/Continue and Home/resume returned to progressing gameplay with the same process. Live 2×→1×→2× changes continued rendering without a pause/resume workaround; 2× selection was read back afterward. The exported final console confirms FIFO and the original 128-pipeline prewarm, completed in 0.7 seconds with 303/303 Dawn blob-cache hits. No claim of subjective audio/input quality follows from screenshots and logs.

Retro Rewind also loaded the existing profile and ran two stationary offline Wii Chain Chomp Wheel battles with Yoshi/standard bike and 11 CPU opponents. These are a different workload, with no matching Mailbox control. First/warmed displayed FPS was **59.449/58.433**, with maximum gaps **116.605/133.215 ms**. The warmed run had 169 intervals over 25 ms and ten over 40 ms. Required-pipeline waits of 105.040 ms and 97.110 ms occurred in the respective timing windows. These results validate that the game runs, and expose remaining hitching; they do not establish a Retro performance improvement.

## Private candidate identity

Build **195 / 0.5.1-android-nightly.1** is installed in place on the attached Pixel. Its release package audit and same-signer check pass. It is non-debuggable and shell profiling is disabled. Both games remain ready in the launcher. Original gameplay/lifecycle checks and two offline Retro Rewind battles have completed. Retro Pause/Continue also returned to progressing gameplay. The installed APK hash exactly matches the archived candidate. The phone is left at the launcher with no game running.

APK SHA256: `3c929e6a6de15e6455754bfc5dcb52d13e8d3ac70ffe21e0dcb627b84744ea32`.

Exact unstripped native-library SHA256: `509743a84e11bce05a6966eccf633841f1f13bcd9ef45194f0d7ab7b5eaf99d2`.

The private APK and symbols are retained with build, package, install and measurement receipts under `work/android-optimization-20260923` in the existing stabilization worktree. Both final Original and Retro consoles and full captured logcat are retained privately; no native fatal, ANR or device-loss marker was found in these captured final logs. All three changed runtime source files match their prepared build copies byte-for-byte. The packaged native library and archived unstripped symbols share ELF build ID `1859b4bfef703349544978d9f3a92731f8f1c503`. This package contains private game-derived material and is **not a public release asset**.

## Remaining limits

The final artifact still shows a **133 ms displayed hitch**, coinciding with a **123 ms required graphics-pipeline wait** and 128 ms encoding maximum. A later queue snapshot was zero, so zero queued pipelines alone cannot rule out this cause. This is a concrete remaining stutter source, not a fixed issue. The next focused experiment should identify the required pipeline/configuration and separate queue delay from driver compilation, then test earlier preparation. The current cache rebuilds at most 128 recipes ordered by earliest use; simply doubling that limit was already tested and rejected. Dropping the persistent-pass wait risks corrupting its resolved texture and is not an acceptable workaround.

A transient central blackout and narrow black bars during battle respawn transitions also reproduce in the Mailbox control; neither FIFO nor the experimental helper calling convention is required to reproduce them. Exact visual equivalence with original console behavior is unresolved.

This loop does not establish an Adreno geometry fix, improved performance on lower-end phones, online-service stability, or Apple-platform acceptance. Physical interpolation-mode changes were not exercised; the production selector's native/interpolated/backend capability combinations have 24 passing host cases. Owner-driven races, audio assessment and subjective controller responsiveness remain necessary before promoting this Android behavior broadly. A public release also requires the established public signing and packaging process.

See the [comparison table](android-candidate-comparison.md), [scalar experiment record](android-scalar-exactness.md), and [complete optimization ledger](android-optimization-loop.md). Raw device logs, screenshots, symbols and game-derived artifacts remain private.
