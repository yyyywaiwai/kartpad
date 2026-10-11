# Private build status — 25 September 2026

Latest Android update: [Pixel build 218 completed Retro race and remaining Android issues](../2026-09-25/android-code218-pixel.md).
Android performance is the current work priority; Apple validation is deferred.

This records what the current unpublished builds have actually proved. It is
not a release note or a claim of device acceptance across platforms.

| Platform | Current private build | Evidence | Remaining gate |
|---|---|---|---|
| Android | Pixel installed build: `0.5.1-gx-nodraw.2`, code 218, updated in place from code 208 on 25 September. Code 208 remains the archived measured baseline. | Code 208's archived APK and the copy pulled after its in-place Pixel 9 Pro XL install have the same SHA-256, `a8b0d1867fe654d373b6044687b3b1e9593160163881c9be13aaa6f28e167579`. Candidate 203, whose source was rebuilt as 208, ran an active stationary 12-kart Cookie Land battle on that Pixel: 12.652 ms game-thread CPU per presented frame versus 14.70–14.79 ms for build 195 in comparable runs. Codes 209–211 passed release APK audits and each reached an active Luigi Circuit race on the API 36 ARM64 emulator. Code 212 passed a fatal-exit check; code 213 rejected a modified REL. Code 214 booted Original on the emulator and Android accepted a 60 Hz surface request. Code 215 passed its private release APK audit and XF burst host test but was not booted. Code 216 reached Original's animated title. Code 218 passed its release APK audit and reached the title and animated course background on the emulator after an in-place install over code 217; its retained config and game files kept the same hashes. | Owner confirmed one completed physical Pixel build-218 Retro online race on 25 September, with fewer glitches and improved stability reported. Bounded logs/audio were retained; no fatal/crash/disconnect lines were found. This is not a matched speedup measurement. Adreno launch/geometry reports, lower-end performance, controller auto-acceleration, notification slowdown, and broader online endurance remain unresolved. Exact save/identity byte readback was unavailable. No further owner testing is requested; do not ask external users to retest before publishing an updated APK. |
| iPadOS | Installed: `0.5.1` build 70, signed development app. Latest candidate: unsigned build 72; no IPA packaged. | Build 66 passed the physical iOS app audit and strict signing check and installed in place over build 65. Builds 67–72 compiled from newer iOS runtimes and passed full-game app audits; each executable and matching dSYM share a UUID. Build 70 includes the REL validator, #196 diagnostic, and an opt-in native-rate FIFO presentation experiment. It was signed with the same team and installed in place over build 66 on the paired iPad Pro. The 2.6 GB game image and 34 other app-data files were backed up before and read back byte-identical after installation. Build 70 launched on the physical iPad: the native launcher showed Original and Retro as “Ready to play,” its process transcript identified build 70, and the config and console identity matched their post-install copies. Build 71 includes the GX display-list change compiled from the regenerated graph; build 72 adds the bounded register-only display-list classification cache. | Neither Original nor Retro was started in build 70. Builds 71–72 have not been installed or launched. WFC, replay, and performance still need physical gameplay checks. |
| macOS | Latest private candidate: `0.4.21` build 44, ad hoc signed dual app. | Runtime `10360ad` includes course-scoped pipeline replay. The translated arm64 dual runtime linked, and the package audit passed with explicit expected version/build values. Using isolated portable data, the app reached an active Original 100cc Luigi Circuit VS race with 12 racers. Its first load logged zero recorded/queued pipelines; the cache subsequently contained 266 links for that course. A fresh process revisited the same course, found 266 recorded pipelines, queued 91, and reached the active race. | No driven lap, completed race, or matched performance comparison. Retro remains unverified. |
| tvOS | Latest private candidate: unsigned `0.5.1` build 62 dual app; no IPA packaged. | Runtime `686a573` includes course-scoped replay. The physical tvOS SDK build and full-game app audit passed; the binary targets TVOS arm64 with a tvOS 17.0 minimum. | The app has not been installed or played. Course revisit, Original, Retro, and performance remain unverified on Apple TV. |

The source branches and submodules have moved beyond the physical-device
artifacts. Guarded DVD DMA bulk copies are in all four runtime submodules and
passed C++ syntax checks. Android code 209 includes that change and a
scene-generation fix in its Android runtime. The fix invalidates both GX
pipeline memos when a course load begins, allowing previously seen recipes to
reach the scene recorder again. All four runtime sources now have the fix. The
iPad build 66 includes the iOS changes through the GX scene-generation repair,
but has not been driven into either game.

On 25 September, macOS runtime `10360ad` and tvOS runtime `686a573`
received the Android/iOS course-scoped recipe recorder, replay queue, and GX
scene-generation invalidation. A course archive read now selects its scene;
the next visit can queue recorded pipelines during loading. Each changed
Aurora implementation file and the DVD read source passed a focused macOS
host C++ syntax check using current runtime headers. A later tvOS SDK build
and app audit also passed. The macOS build later entered an Original race and recorded course links,
and a fresh process replayed its recorded pipelines during a same-course
revisit. Both Mac and Android emulator now have completed revisit checks;
neither check establishes a measured performance gain.

The new private macOS dual app is
`build/macos-replay-20260925/KartPad-build44.app`. Its unsigned runtime SHA-256
is `0e32180ab6e3c2fc0d0cbef4ff3b042039647dde8ce6211ed78e16ea41cc66d5`;
the packaged executable SHA-256 is
`63c0d3ff52c5d14b647047068a181a8afa717a67166bae9c667db5e8c1e765da`.
The audit's bundle-content hash is
`9b5a5df499a0ff0bae9435959985e665788509f28eb37a8b4e6ca8f47314d4b0`.
The app is ad hoc signed, has no team identifier, and was built from the staged
macOS runtime pin `10360ad`; the package fingerprint records root commit
`1947d26` before these gitlink and ledger updates. The private compile log is
`work/macos-replay-build-20260925.log`. On a later isolated launch, the app
used `work/mac44-first-launch/home` for its config, NAND, logs and cache while
reading the existing extracted game files. It reached Original's animated
opening on the physical Mac. The on-screen overlay showed 60.0 FPS; later
intro telemetry in `work/mac44-first-launch/stdout.log` reported about 59–60
FPS, with occasional 33 ms worst intervals. The app exited cleanly after a
normal Quit. That opening check did not measure sustained gameplay performance.

A subsequent portable-mode session used `portable.txt` and `UserData` beside
the candidate app, preserving the normal user data directory. A new test
licence reached an active Original 100cc Luigi Circuit VS race with 12 racers,
then returned to the menu and quit cleanly. Mario remained at the starting
area; no driven lap or completed race was recorded.
`work/mac44-first-launch/race-attempt.log` logged scene `c245398c16435baa`
with zero recorded and zero queued pipelines on its first load. Read-only
SQLite inspection subsequently found 266 pipeline links for that scene.
A second process retained this cache. After the attract sequence and menu
navigation, `work/mac44-first-launch/revisit.log` line 377 logged the same
Luigi Circuit scene with **266 recorded, 91 queued**. The 100cc VS race
reached active gameplay with 12 racers; Mario remained at the starting area.
The observed overlay showed 59 FPS, and later stationary samples were around
60 FPS. The process exited normally with code 0 after Quit. This verifies
persistent course recording and replay queueing on Metal, not a loading-time
or frame-time improvement. No lap, completed race, Retro or WFC was tested.
The portable test licence and cache are retained beside the private app.
A regenerable iOS72 `libmkw_base_shared.a` link archive was removed to recover
disk space during this check; the iOS72 app and matching dSYM remain intact.

The new private physical-tvOS app is under
`build/tvos-replay-20260925/xcode/Release-appletvos/KartPad.app`. Its bundle
reports `0.5.1` build 62, above the retained build 61 artifact. The executable
SHA-256 is
`60ffbe57dbbf44a5fabaad3da5f98b1bf2640ff5dbcc159a84b9b94e7e5679a2`,
with Mach-O UUID `DB7A81A1-66BB-307A-BBA9-759A082A16F4`. The maintained
source stage verified tvOS runtime `686a573`, and the private build log is
`work/tvos-replay-build-20260925.log`. The build script now accepts explicit
private candidate version values without changing the runtime defaults. No
dSYM was emitted. This unsigned app has not been packaged as an IPA, installed,
launched, played or measured.

Apple source revision `2a9a548` additionally ports Android's shared Aurora
render-mode lock, frame-owned debug marker/depth-peek mapping, GX GEN_MODE
first-write initialization, and alarm reschedule ordering to iOS, macOS and
tvOS. The six changed files match across the Apple runtimes; the three Aurora
implementation files passed a macOS host syntax check, and the alarm source
passed a separate syntax check. Android's surface-loss copy path was examined
but not ported because Apple's overlay draw has a different return contract.
Build 67 was compiled from the later iOS runtime revision `b07c4f3`, which
includes these ports and the guarded Yaz0 decoder. Its unsigned app is under
`build/ios67-20260924/xcode/Release-iphoneos/KartPad.app`; the maintained-source
stage verified against that runtime revision. The full-game iOS app audit
passed, `CFBundleVersion` is 67, and the executable SHA-256 is
`f839c613e1ca247cc7aab0160c7aa494c41cc1091969e1d5b7c6149a6f76805a`.
The executable and dSYM share Mach-O UUID
`0C713647-680E-3AB4-9A05-832C06609AD1`. The build log is private at
`work/ios67-build-20260924.log`. Build 66 predates these changes; build 67 has
not been installed or played, so neither validates the new decoder or ports on
an iPad.

Code 209 was built from Android runtime `f1677be`, with the private translated
shards, as `work/android-replaygen-20260924/kartpad-code209-replaygen.apk`.
SHA-256: `e34fc03afdb821dc641641323b8b017921b04a6c9cc5c52ad77a13f42f50cc61`.
The release audit verified version code 209/name `0.5.1-replaygen.1`; its APK
signer SHA-256 is `61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
The emulator retained its app data through `adb install -r`. In one console
session, the first Luigi Circuit course load logged scene `c245398c16435baa`
with **213 recorded, 172 queued**. Selecting Change Course and the same Luigi
Circuit again logged the **same scene** with **342 recorded, 0 queued**; the
second race reached active gameplay. Restart within the race did not log a new
scene load, so it is not a replay-path check. The emulator already held a cache
from prior builds, and an empty second queue does not establish a startup or
frame-time improvement. The console and screenshots are in the same private
`work/android-replaygen-20260924/` directory.

Code 210 was built from Android runtime `97cdc9a`, with the same private
translated shards, as `work/android-yaz0-20260924/kartpad-code210-yaz0.apk`.
SHA-256: `8d1bbd8495579e54f3e8bb88cf94886a45530f51368ed3d3b439936b531df570`.
The release audit verified version code 210/name `0.5.1-yaz0.1`; its signer
SHA-256 is `61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
It adds a guarded host-buffer Yaz0 decode to all four runtime source copies.
The host path requires mapped contiguous input/output, checks for protected
executable writes and deferred reads, and notifies GX of the completed write;
otherwise it uses the former scalar guest-memory path. An actual-source host
harness passed literal and back-reference cases on both paths plus checked
memory, executable-guard and deferred-read fallbacks. The four runtime source
files matched by hash, and all passed C++ syntax checks. These checks do not
measure a load-time or frame-time gain.

On the existing API 36 ARM64 emulator, code 210 kept app data through
`adb install -r`, opened Original, and loaded Luigi Circuit through Time Trials
to an active race. The private `work/android-yaz0-20260924/` directory holds
the audited APK, build log, console transcript and countdown/running-race
screenshots. The transcript identifies build 210 and shows no fatal or abort
through that run. The emulator was stopped without wiping its data. No physical
Android device was connected for code 210. Apple build 66 predates this Yaz0
change; the newer build 71 includes it but has not run on the iPad.

Code 211 was built from Android runtime `0ce6a52`, with the same private
translated shards, as `work/android-dvd-cache-20260924/kartpad-code211-dvdcache.apk`.
SHA-256: `21fd4b127bdf3e1df303d5b00eedfad8b8fac13e27383eadef65732c04889b13`.
The release audit verified version code 211/name `0.5.1-dvdcache.1`; its signer
SHA-256 is `61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
All four runtime copies now use a bounded eight-handle, per-thread DVD file
cache for repeated exact reads. It checks modification time on reuse and
evicts the least recently used handle; the read bounds and output-on-success
contract remain in place. An actual-source host harness passed repeated,
zero-length, boundary, replacement, truncation, deletion, eviction and
concurrent-caller cases. A synthetic host benchmark of 20,000 local 4 KiB
reads took 224.708 ms with fresh opens versus 39.7558 ms with the cache. That
measures host file-open overhead, not game frame time.

On the existing API 36 ARM64 emulator, code 211 installed over 210 with
`adb install -r`; app files remained at 2.5 GB and 2,107 files. Original
booted, the saved license and menus opened, and a 50cc Luigi Circuit Grand
Prix race reached active gameplay. The private directory above holds the
audited APK, build log, console transcript and race screenshot. The transcript
identifies build 211 and showed no fatal or abort through the race check. The
emulator was stopped without wiping app data. No physical Android device was
connected, and this run is not a matched performance comparison. Apple build
67 predates the file-cache change; build 71 includes it but has not run on
device.

On 25 September, all four runtime copies gained a central `RuntimeTerminate`
path for the named fatal exits, including missing guest targets, OS panic and
reset, guest exit, DVD/NAND root failures, and malformed Yaz0. It records a
reason, writes fallback artifacts if needed, stops audio and Aurora workers,
closes the transcript pump, flushes streams and exits without running static
thread-owning destructors. Other low-level abort sites remain outside this
change. The GX batching suggestion was inspected but not implemented: HLE
applies CP/BP state immediately while Aurora defers XF/INDX work, so batching
requires an explicit ordering contract at each synchronization point.

Android code 212 (`0.5.1-exit.1`) was built from the new runtime and private
translation into `work/android-termination-20260925/kartpad-code212-exit.apk`.
SHA-256: `4526f6f029aacced47fb6bcdea0dbe7d80fe41b9f67b85ad5c939166e7808a26`.
The release audit passed; signer SHA-256 remains
`61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
On the existing API 36 ARM64 emulator, `adb install -r` preserved 2,109 app
files, 2.5 GB of data, and the exact `Config.toml` hash. Original booted into
the game's running attract sequence. A temporary invalid DVD root, launched
directly through `KartPadActivity`, produced `crash_dvd_root.txt`, an exit-1
reason in `console.log`, and `[runtime] process transcript ended`. The original
config was restored and read back with SHA-256
`e1e85a1693ebf504679f7d54123f38568e3a217ae315b0c214277ce9f04fe63f`.
The emulator was stopped without a wipe. This checks one fatal path, not all
fatal paths or an active race; code 212 was not installed on a physical phone.

Unsigned iOS build 68 was compiled from the same termination change and the
newer file-cache runtime at
`build/ios68-termination-20260925/xcode/Release-iphoneos/KartPad.app`.
Its full-game app audit passed, `CFBundleVersion` is 68, executable SHA-256 is
`b6d3cb66fb29b4226ec994ce5346ac5abcdf30d8f5703d2508506f59aaa76dde`,
and executable/dSYM UUID is `0A4C83E0-8F09-3F9C-8662-76EA46A50B37`.
Build 68 has not been signed, packaged as an IPA, installed or played on iPad.

The handoff's claim that extracted-folder imports do not hash executable game
files was incomplete: Android, iOS, macOS and tvOS already checked `main.dol`
in their game-data readiness paths. The actual gap was `StaticR.rel` on all
four platforms. The same readiness paths validate extracted staging after a
disc-image import, so the Android and iOS disc-image paths also gain the REL
check without duplicating hashing inside the extractors. The profile's pinned
REL hash matched the retained emulator's clean file. Rather than keep a
size/time cache that could accept a changed file, the readiness check hashes
the 4.9 MB REL on launch alongside the existing DOL check. No frame-loop hash
was added.

Android code 213 (`0.5.1-imagecheck.1`) built from this source, passed the
release APK audit, and has SHA-256
`ac0888f54f6e47657a0bd1f6590bffc9d4cb0ab26290df8e3f7994903b124f9f`.
Its signer remains
`61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
On the existing API 36 ARM64 emulator, `adb install -r` preserved 2,114 app
files, `Config.toml`, and the clean REL hashes. The launcher showed “Ready to
play” and Original began booting. A one-byte modified REL, staged only after
pulling a byte-identical backup, changed the launcher to “Setup needed” and
displayed the clean-dump message. Restoring the backup read back to SHA-256
`16d9d146112541fefea701ecb5bc1a496f9d50e4a752fbb5b6778e7c6399f67d`
and restored “Ready to play.” Screenshots, build/audit logs and the private
APK are under `work/android-imagecheck-20260925/`. The emulator was stopped
without wiping data. This is a launcher/boot check, not a driven race or a
physical-device test. The macOS and tvOS source checks have not yet been built
or run.

Unsigned physical-iOS build 69 compiled the iOS REL validator from runtime
`4eab579` and the pinned translation into
`build/ios69-imagecheck-20260925/xcode/Release-iphoneos/KartPad.app`. The
full-game app audit passed, `CFBundleVersion` is 69, executable SHA-256 is
`fb855175603064281da2125b146bcc4fe870bd8f99e17f391eb4013f6e425028`,
and executable/dSYM UUID is `6A0F8393-834C-38B4-BD04-B71FA6EA1358`. The
build log confirms `KartPadRuntimeOverlayHost.mm` compiled, and the binary
contains the modified-data message. Its `kartpad-build.json` records the four
runtime commits and translation fingerprint; `source_dirty=true` reflects the
owner's unrelated dirty document plus the staged iOS gitlink at build time.
The app is unsigned and has no IPA. It has not been installed or played on an
iPad; compilation does not prove the new rejection flow on Apple hardware.

After build 69, the four runtime copies gained a narrow diagnostic for the
missing-target failure at `ModuleLinker::CallModule`'s return address
`0x8000A42C`. The fatal transcript and crash artifact now label the module
index (`r4`), module base (`r3`), and failed REL prolog target, alongside the
registered StaticR prolog address. The translated call site confirms those
register meanings; this change does not alter module loading or dispatch.
Build 69 predates the diagnostic. Build 70 compiles it, but its first physical
launch did not enter either game runtime or exercise the diagnostic. The cause
of #196 remains unproven until a game run supplies those values.

Unsigned iPhoneOS build 70 compiles the #196 diagnostic and a private
presentation experiment from iOS runtime `73d4962`. `video.vsync = true` in
`Config.toml` requests Metal FIFO at native rate when the surface supports it;
the default retains the existing present-mode policy. Aurora checks the active
interpolation target when selecting or reconfiguring the surface, so an
interpolated target uses the existing non-FIFO policy. The chosen mode and
mode changes are logged. This is a way to compare presentation and audio
pacing on the same iPad, not evidence that FIFO improves them.

The maintained-source stage and full-game app audit passed. The private app
is at `build/ios70-fifo-20260925/xcode/Release-iphoneos/KartPad.app`, with
`CFBundleVersion` 70, executable SHA-256
`3f86c8d05cc465d24812578c93b9ff037bdf27aa9124d9f8734f05e88b219576`,
and matching executable/dSYM UUID `BB9B3CA7-73FA-3365-9B94-E27D864F8CA8`.
The manifest records all four runtime commits and the translation fingerprint;
`source_dirty=true` reflects the staged iOS gitlink and the owner's unrelated
document. The build log is `work/ios70-fifo-build-20260925.log`. The original
build artifact is unsigned and has no IPA. A separate private copy at
`work/ios70-install-20260925/signed/Payload/KartPad.app` was signed with the
same development team and provision as build 66, then passed strict signature
verification. Its signed executable SHA-256 is
`8f91d07ecfc751f5a2aca38176af47b27fc2e9dd48171933df2e64b6e4b83cf6`;
its UUID still matches the retained dSYM. An in-place install over build 66
succeeded on the paired iPad Pro, and the device reports build 70. AFC copies
of all 35 files matched byte-for-byte before and after installation, including
the game image at
`fc035e60610842da6860d23d4a30c1f1c0f019d492469deb8a2ac25ef5822331`.
The two temporary game-image readback copies were removed after the hash check;
an identical full backup remains at `work/ios66-install-20260924/ipad-before/game-full.wbfs`.
The 34 other before/after files and the verification receipt remain under
`work/ios70-install-20260925/`.
The first QuickTime mirror showed OpenTS1 active, so no KartPad session was
interrupted at install time. On a later first-launch check, `devicectl`
launched installed build 70 as PID 1527; the private receipt is
`work/ios70-first-launch-20260925/launch.json`. The physical iPad screen
showed the KartPad launcher with Original and Retro both “Ready to play.” Its
`console.log` under the same receipt directory identifies build 70 and has
health samples without a fatal or abort in the observed interval. A subsequent
process listing still showed PID 1527 alive in the background. AFC readback of
`Config.toml` and `ConsoleIdentity.txt` matched the post-install copies
byte-for-byte (SHA-256 `054e0efd78183d66599489490dc9c3b4645b51f731d7ff143ce481b177055fa4`
and `5f36ed4ce8976ede1cb0be21e9a1ffa154fdc411871be3233b71d7077cb4600c`).
No game mode was selected and no recording was made. This launch supplies no
iOS frame-time, frame-tail, audio, input, replay, or WFC comparison.

Source after build 70 labels the Android and iOS auto-accelerate setting
"Touch auto-accelerate," matching the existing one-second touch A latch;
physical controller input still uses its normal button path. No controller
behavior changed and no app with the new label has been built. A focused host
test passed the iOS present-mode selector's default, FIFO opt-in,
interpolation, unsupported-mode and backend cases. The local CI workflow is
configured to check five intentionally identical runtime files across Android,
iOS, macOS and tvOS;
the macOS VSync test was updated for iOS's new opt-in policy. These source
and CI checks do not establish iPad pacing or controller acceptance.

The build 66 iPad receipt is in `work/ios66-install-20260924/`. It was built
from a fresh stage of iOS runtime `0df334c` plus the build-number change later
committed as `e5902c8`. The unsigned executable SHA-256 is
`09d7af226fa11ec53d4228fdea1e5077896ff164d955b2a241da9e3ce6373db9`;
its Mach-O UUID is `4459EAE6-B408-301E-A257-D2E2FD3D5E85`. The existing
development profile and signing identity were reused. A fresh pre-install
backup and post-install readback matched for the 2.6 GB game file (SHA-256
`fc035e60610842da6860d23d4a30c1f1c0f019d492469deb8a2ac25ef5822331`)
and all 34 other files. The build 66 process transcript confirms PID 999 and
version `0.5.1` build 66, but contains no game boot. A wired mirror displayed
another app in the foreground, so KartPad was left undisturbed pending an
available iPad session.

The handoff's GX, Adreno and floating-point proposals remain
hypotheses or bounded experiments. In particular, the available shader evidence
does not prove an Adreno driver defect, and a lower game-thread CPU number does
not by itself establish smoother presentation.

The 25 September GX source check narrowed the proposed first batching step.
`GX__CallDisplayList_80172f64` does not rescan every list on every call: it
has a bounded scan cache keyed by guest address, bytes and vertex layout, with
write-generation and content-digest validation; register-only lists bypass the
index scan. The retained Pixel log shows 203,218 probes and 73,144 validated
hits in one five-second interval, with no eviction. `HleFifoWrite` applies
CP/BP writes immediately, while XF/INDX packets are sent to Aurora and draws
depend on the resulting order. Any batch across those boundaries needs a
separate ordering proof and matched gameplay measurement; no GX batching was
shipped from this source review.

Android code 214 (`0.5.1-framerate.1`) requests the output rate on its native
window at surface creation and reconfiguration: 60 Hz normally, or the selected
interpolation target. It loads `ANativeWindow_setFrameRate` dynamically so
API 28–29 remain supported. The pinned NDK header recommends default
compatibility for game content; the handoff's fixed-source suggestion is for
video. The private release APK passed the package audit, retains the code 213
signer, and has SHA-256
`e6d71a721b4aaf5ddb00cf5c055fc9ae6687d27958bb8c97c27c2ae49bd044fc`.
`adb install -r` over 213 preserved 2,115 app files and the same config and
REL hashes. On the API 36 ARM64 emulator, Original reached its opening
sequence and the session transcript recorded
`Android surface frame-rate request 60 Hz: 0` followed by Vulkan FIFO mode.
The zero return shows Android accepted the hint; it does not prove that a
physical display switched rates or that gameplay became smoother. The private
APK, build/audit logs, transcript and screenshot are under
`work/android-frame-rate-20260925/`. A matched 120 Hz Samsung race and Pixel
battle comparison remain necessary before retaining this as a performance
improvement.

Android code 215 (`0.5.1-gx-xf.1`) is a private candidate for a narrower GX
batching step. Within one direct FIFO burst, consecutive complete XF register
loads now enter Aurora in one display-list call. CP/BP writes, draws, truncated
packets, recording and later HLE calls keep their existing boundaries. The
same source change is committed in all four maintained runtime copies:
Android `b435655`, iOS `e13474a`, macOS `0814a6b`, tvOS `3c9e969`.
`scripts/test-gx-fifo-burst.py` compiles the production packet walker with a
small ordered-packet harness and passes; shared-runtime parity also passes.
The code 215 private release APK built from the Android pin and passed the
package audit. Its SHA-256 is
`bb3d12691b00dc65bca40e57af40c3fb700cff12158478fc9acfa484eb5d7706`;
its signing certificate SHA-256 matches code 214,
`61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
The APK is `work/kartpad-code215-gx-xf.apk`; build and audit logs are private
under `work/`. Its embedded provenance names the four runtime commits above
and the exact translation hash. It records the pre-commit root revision
`4493afb` as dirty because the package preceded root commit `3ec00a8`.
No device was attached for this build, and code 215 has not been installed,
booted, played or measured.
In particular, the host test proves packet ordering in the direct walker, not
a gameplay speedup; HLE's per-word FIFO path and cross-call batching are still
unchanged. Apple build 70 predates this source change.

Code 216 handles complete nine-byte GX display-list
calls directly in the burst walker. The shared translator now folds only the
three-store `0x40` command/address/length pattern; other three-store packets
keep their existing path. When direct parsing is unavailable, the runtime
replays the original 1/4/4 writes. A private retranslation of the real
`ResShp::CallPrePrimitiveDisplayList` function emitted two such bursts in place
of six FIFO calls; 11 bursts were added across the regenerated graph. All 14
focused translator tests, the production walker host test, and shared-runtime
parity pass. The private release APK passed the package audit and has SHA-256
`2f364a883d449853fe9304838bbb13eb31aed2121fa430f1281e0b4e1b1259b0`;
its signing certificate SHA-256 matches code 215,
`61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
It was installed in place over code 214 on the API 36 ARM64 emulator. Before
and after installation, the app had 2,116 files, and `Config.toml`,
`StaticR.rel`, and the disc manifest read back byte-identical. The launcher
offered Original, which reached the animated title and kept rendering for over
nine minutes without a fatal message in the session transcript. Input attempts
did not reach a menu or race. This is an emulator boot and data-preservation
check, not a gameplay or performance comparison. The Pixel remains on code
208; no physical Android device was attached. The private APK, translation,
build/audit logs, screenshots and
session transcript are under `work/kartpad-code216-gx-direct.apk`,
`work/gx-direct-dl-translation-20260925/` and
`work/android-gx-direct-20260925-*`.

Unsigned physical-iOS build 71 compiles the same GX display-list change from
the regenerated code 216 translation graph, with the iOS-specific data-section
aliases retained. Only seven translated function files differ from the earlier
Apple graph. It uses iOS runtime `fe44bf8` and build number 71. The dual app
build and full-game app audit passed; the executable SHA-256 is
`1f6a40855675485689589f67cab74d7a432366281ae91ad324df07e37df3fc08`,
and the executable and dSYM both have UUID
`6C788A83-724A-3791-9DA4-D68B1D0E7CE3`. The embedded source-input record
names translation SHA-256
`9e0b11d3bb1fe97f6cccecd8420008b24450297e337ba29506f10ff262b2f1b3`;
`source_dirty=true` reflects the staged iOS gitlink and the owner's unrelated
dirty document at build time. The app and dSYM are under
`build/ios71-gx-direct-20260925/xcode/Release-iphoneos/`; the private build log
is `work/ios71-gx-direct-build-20260925.log`. Build 71 is unsigned and has not
been packaged as an IPA, installed, launched, played or measured. The paired
iPad still has build 70 installed; a mirror showed OpenTS1 in the foreground,
so no KartPad session was interrupted. This compiler/package result does not
establish a device speedup or clear Original, Retro or WFC gameplay.

The next GX source change caches the answer for register-only display lists
whose outer bytes contain no nested call. Previously those lists bypassed the
index scan but repeated the classification walk on every call. The entry uses
the existing guest-write generation and digest validation; Aurora still
receives the list on every call. Lists with nested calls remain uncached so a
rewritten callee cannot make the outer classification stale. Identical patches
are committed in all four maintained runtimes.

Android code 217 (`0.5.1-gx-nodraw.1`) compiled this change and passed the
private release APK audit. It installed in place over code 216 on the API 36
ARM64 emulator; the checked config, REL and disc manifest retained their hashes.
Original reached its title, but overlay A input did not reach a menu or race.
In three busy title windows the cache reported 645,662 validated hits from
652,674 probes, with 7,068 entries and no eviction. That showed reuse but also
put the cache close to its former 8,192-entry bound before a race. The bounded
entry limit was raised to 16,384 in all four runtimes; copied command bytes
remain capped at 8 MiB.

Android code 218 (`0.5.1-gx-nodraw.2`) compiled that bound from Android runtime
`27074c2` and the same private translation graph. Its audited private release
APK is `work/kartpad-code218-gx-nodraw-bound.apk`, SHA-256
`601f6e57479546af14fafb3b9c069a1ddae41e962164612c0813cfa8e018ee1f`.
Its signing certificate SHA-256 matches code 217,
`61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
Its embedded source-input record names translation SHA-256
`b9b4d447e8a1d5dc27132fb229e9dbfb1491468e4fbbf2904c0ac73271ee03e0`;
`source_dirty=true` reflects the staged runtime gitlinks and the owner's
unrelated dirty document at build time.
It installed in place over 217 on the emulator; the checked config, REL and
disc manifest remained byte-identical. The app's total file count changed
from 2,142 to 2,141 during installation. Original reached the animated title
and course background. Five busy windows recorded 1,421,619 validated hits
from 1,429,800 probes, 9,685 maximum entries and zero evictions. The private
build, audit, install and screenshot receipts are under `work/android-gx-nodraw-*`
and `work/android-gx-nodraw-bound-*`. This shows the old entry cap would have
been crossed in this emulator title session; it does not measure a CPU or
smoothness improvement. No race was reached, the Pixel remains on code 208,
and Apple build 72 includes this cache change but has not run on a device.

Unsigned physical-iOS build 72 (`0.5.1`) compiles the bounded GX cache from
iOS runtime `36e5f73` with the same private translation graph used for build
71. Its full-game app audit passed. The executable SHA-256 is
`585b586a456532c0e2f4be7d7df2374f99da04f7056b82997f3fdc1fe5234753`;
the executable and dSYM both have UUID
`FCE926BB-3193-3F1A-89E3-F31F09BBEA23`. Its embedded source-input record
names iOS runtime `36e5f73` and translation SHA-256
`9e0b11d3bb1fe97f6cccecd8420008b24450297e337ba29506f10ff262b2f1b3`.
`source_dirty=true` reflects the staged iOS gitlink and the owner's unrelated
dirty document at build time. The app and dSYM are under
`build/ios72-gx-nodraw-20260925/xcode/Release-iphoneos/`; the private build
log is `work/ios72-gx-nodraw-build-20260925.log`. Build 72 is unsigned and
has not been packaged as an IPA, installed, launched, played or measured. The
paired iPad still has build 70 installed; its screen showed OpenTS1 active, so
KartPad was left untouched. This compiler and package result does not establish
a device speedup or clear Original, Retro or WFC gameplay.

Evidence: [Pixel comparison](../2026-09-23/android-copy-stream-loop.md),
[Android build 195 baseline](../2026-09-23/android-morning-report.md), and
[deep review](deep-review-handoff.md). The private receipts and APK are under
`work/android-optimization-20260923/`; the iPad install/readback receipts are
under `work/ios65-install-20260923/` and `work/ios66-install-20260924/`.
Those directories contain private or
game-derived material and are not release assets.
