# Android source failure review — 13 September 2026

This pass prioritized executable local reproductions over another hardware profiling dependency. No physical phone was used.

## Corrections implemented

- Original startup currently invokes Retro transaction recovery even when Original was selected. A malformed Retro installed/rollback path can throw before SDL initialization, despite the chooser allowing valid Original data. Recovery is now gated by the selected runtime profile; Retro validation remains intact.
- Chooser recovery and background extraction run independently. Recovery deletes staging directories without ownership coordination, so reopening the chooser during extraction can invalidate the live installation. A nonblocking lock now protects the complete extraction/activation transaction across processes; recovery defers while it is owned.

These defects are in the launch/install paths represented by #200 and #192. They are not established causes of every black-screen/native-exit report. The reviewed launch reports mostly contain descriptions rather than native crash signatures; issue numbers are investigation links, not confirmed duplicates.

## Paths ruled out

A real Android 16/API36 emulator window-dispatch harness tested #197's focusable popup/dialog hypothesis. Android sends canceled ACTION_UP to the original surface when focus moves. Public83's exact SDL3-3.4.4 AAR forwards that release. Ordinary surface, popup and dialog trials delivered one down/one up; manual modal forwarding duplicated the up. No cache reset or key-forwarding patch follows from this result. Controller identity/source changes and touch gas lock remain separate possibilities.

Official Dawn already contains Qualcomm/ARM workaround selection, and the pinned source has the relevant split-pass, clamp and pack/unpack workarounds. A generic driver-toggle addition would duplicate existing behavior. See [Dawn's Vulkan device workarounds](https://dawn.googlesource.com/dawn/+/579447cf71643bde5652e5bd5e81eb55538e1ba0/src/dawn/native/vulkan/PhysicalDeviceVk.cpp). Device-model names alone do not justify an override.

## Validation

- Seventeen real-filesystem storage cases pass, including invalid optional Retro state, existing-save preservation, symlink refusal and lock cleanup.
- The real install pipeline passes success, cancellation and invalid-content cases. A second JVM attempting recovery during extraction and between the two activation moves cannot delete staging or restore rollback. Forced owner-process death releases the lock and allows stale recovery.
- Same-process contention is rejected before opening another descriptor, preventing POSIX descriptor-close behavior from releasing an existing process lock.
- Android debug Kotlin and Java compilation passed. No phone was used.
- The independent [packed vertex read-width correction](packed-vertex-read-width.md) removes a four-byte fetch for three-byte attributes. Extracted boundary tests and actual WGSL execution through pinned Dawn pass; it is not established as the missing-character reports' cause.

These are source corrections for the next candidate, not changes to the already published code83 APK. The unrelated delayed startup/native-exit and device geometry reports remain open. No universal driver-support claim follows from this review.
