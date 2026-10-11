# Android build 218 — owner completed Retro online race on Pixel

## Current state

On 25 September 2026 at 09:19 JST, private build 218
(`0.5.1-gx-nodraw.2`) installed successfully over build 208 on the Pixel 9 Pro
XL using `adb install -r`. No uninstall, data clear, downgrade or identity
reset was performed. The package retains its original first-install date.
The owner authorized the update for testing. Work is now focused on Android;
Apple build and gameplay work is deferred.

The APK pulled from the phone after installation matches the audited candidate:
`601f6e57479546af14fafb3b9c069a1ddae41e962164612c0813cfa8e018ee1f`.
Its signing certificate matches installed build 208:
`61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`.
The old installed APK was archived before replacement with SHA-256
`a8b0d1867fe654d373b6044687b3b1e9593160163881c9be13aaa6f28e167579`.

The release app denies `run-as`, so no fresh private save/config/identity
backup or byte-for-byte readback was obtained. The phone was in active use;
its screen was left alone during installation. In-place package replacement
is verified; game-data readiness, the existing licence, and identity continuity
were not byte-verified. The owner subsequently launched Retro, joined online
and confirmed completion of a race. This establishes gameplay for that session;
it does not establish exact save/identity continuity or a matched speedup.

## Changes since 208

| Builds | Change | Intended benefit |
|---|---|---|
| 209 | Guarded block DVD copies; course-generation pipeline recording | Reduce copying overhead and record pipelines for subsequent course visits |
| 210 | Guarded host-buffer Yaz0 decoding | Reduce asset decompression overhead |
| 211 | Eight-handle per-thread DVD file cache | Avoid repeated opens for reads of the same files |
| 212 | Ordered fatal-exit handling | Preserve the original error and stop workers without a secondary destructor abort |
| 213 | StaticR module hash validation | Reject incompatible game code before launching |
| 214 | Native Android display-rate hint | Request a display rate matching the selected game output |
| 215 | Adjacent XF loads batched within a direct burst | Reduce graphics-command call overhead while preserving ordering boundaries |
| 216 | Direct handling of the translated three-write display-list command | Reduce calls in the graphics path identified in the Pixel profile |
| 217–218 | Bounded register-only list classification cache; expanded entry limit | Avoid repeating classification scans; retain an 8 MiB copied-command limit |

Source also adds module-prolog failure context for #196 and clarifies the
setting label as Touch auto-accelerate. Neither is a performance improvement.

## Verification and limits

The exact APK passed the release package audit again immediately before
installation. Shared runtime parity and the production GX burst host test
passed again. Earlier emulator checks established races for 209–211, an
ordered fatal exit for 212, modified-module rejection for 213, acceptance of
the rate hint for 214, and title rendering/cache reuse for 216–218.
Those checks do not establish a physical Android speedup or an Adreno fix.

Private receipts are under `work/android-pixel-comparison-20260925/`:
`install-receipt.json`, `package-after.txt`, `code218-audit.log`, and the
before/after installed APKs. The candidate is
`work/kartpad-code218-gx-nodraw-bound.apk`, built from Android runtime `27074c2`.
No public release or merge was performed.

## Physical Retro session and remaining issues

The owner reported fewer glitches and improved stability, then confirmed one
completed Retro online race on this physical Pixel. Active lap-three gameplay
was also observed. No additional owner testing is requested for this work.
There was no matched old-build comparison, so the improvement is an owner
assessment rather than a measured speedup.

The 120-second capture starting 09:47:18.615 JST contains 21 one-second FPS
samples (logged every 300 presents), ranging from 39.22 to 60.06, median 52.28.
These are not whole-race FPS statistics. Game CPU samples range from 14.474 to
19.682 ms/present. Two persistent pipeline waits inside the actual capture were
106.558 and 128.542 ms. Buffered earlier history is excluded from these counts.
No fatal/crash/disconnect lines were found in the bounded capture. Thermal
status was 1 before and after, and the display-list cache reported no evictions.

The 119.726-second playback audio capture decodes correctly, with no silence
longer than 100 ms midway through capture at the -50 dB threshold. This is not
a listening-based claim that all crackle or glitches are absent.

A final log entry at 09:49:21.596 reports a 1,014 ms blocking socket receive on
the game thread, near the capture boundary. Its exact scene is unconfirmed.
Investigate deferred/cooperative completion while preserving guest network
semantics; blindly shortening the timeout could break authentication.

Private evidence: `owner-retro-online-094718-analysis.md`, matching log, audio,
receipt and thermal snapshots under `work/android-pixel-comparison-20260925/`.

## Android issue disposition and support

Current reports were reviewed on 25 September. None of the following is closed
by the Pixel result:

- #321: ROG Phone 7S / Adreno 740 native launch crash; attached driver stack
  requires analysis. No demonstrated correction in build 218.
- #316 and related geometry reports: displaced character vertices on OnePlus
  and other Adreno devices; CPU optimizations do not establish a renderer fix.
- #320: Huawei Y9 Prime 2019 severe race slowdown, including an input-related
  zero-FPS report. Supplied diagnostics need analysis; Pixel timings do not
  establish improvement on this phone.
- #319: physical-controller auto-acceleration on Retroid Pocket 6. Current
  latch implementation belongs to the touch overlay. The clearer setting
  label does not implement controller latching.
- Discord notification-triggered slowdown remains unverified.

Discord replies were posted and visibly verified in the RP6 thread
(1550722646394536006) and notification-performance thread
(1550583968964018227), correcting earlier fix expectations and requesting no
new tests or logs. General and KartPad channel histories were reviewed too;
this is not a claim that every historical support post has been processed.

The owner explicitly requires publication of an updated APK before asking
other users for targeted retests. Build 218 remains private. Next engineering
work should analyze the existing Adreno crash/geometry evidence alongside the
captured pipeline and network waits. Further Apple work remains deferred.

## Second review handoff

See [Android second-review prompt](android-second-review-prompt.md). As of this
handoff, two Discord replies were sent; no new GitHub issue replies were posted
in this session. The latest public APK remains v0.5.0/code135. Performance
comparisons cited in earlier records compare intermediate candidates, not a
matched public-code135 versus private-code218 run.

The [second review](android-second-review.md) supersedes two claims above:
#321's stack is a crash in `vkCmdEndDebugUtilsLabelEXT` from the overlay debug
group, still present in 218; #320 is a Mali-G51/API 29 phone that ran without
pipeline workers. Both have proposed runtime patches, not device acceptance.
