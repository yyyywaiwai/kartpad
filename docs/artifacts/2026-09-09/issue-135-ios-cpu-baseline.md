# Physical iOS CPU baseline investigation

Issue 135 comment 5591053958 is an AI-generated crash summary, not an original
crash report. Its attribution to an unsupported instruction remains unverified.
An independent audit nevertheless found a concrete release compatibility defect:
the physical iOS runtime targets were compiled with `-mcpu=apple-m2`, despite an
arm64/iOS 16 deployment contract that includes older devices.

## Exact released executable

The locally inspected v0.4.11 executable matches the previously verified public
executable SHA-256 `ad5ef4a98c3e1854c74fd2edc090a588a900059f74a53850e9191a34903f1328`.
Mach-O UUID: `E054E565-ABDD-3AC4-8629-53C553AC52B4`.

`RegisterStaticIndirectDispatchTable` starts at unslid address `0x10004513c`.
At `0x100045160` (function +36, image offset `0x45160`) it executes
`LDAPRB w8, [x8]`, encoding `0x38bfc108`, before its table-validation branches.
Further LDAPRB loads occur at `0x10004517c`, `0x1000451a4`, and elsewhere.
The generated static initializer at `0x100043974` calls this function at
`0x100043984`. This is an ordinary atomic/static-guard load, not a deliberate
trap instruction or evidence that the dispatch table is malformed.

The source does have explicit abort paths for late registration, missing profile
and duplicate profile; a raw fault address is necessary to distinguish them.
The initializer's symbol name alone cannot establish a table defect.

Arm documents LDAPRB as requiring FEAT_LRCPC:
https://documentation-service.arm.com/static/67e40f3398aa3c3b6eea6a85
Current Apple clang rejects that instruction for its `apple-a10` target with
`instruction requires: rcpc`. The same atomic-acquire C probe compiles to LDAPRB
for `apple-m2`, and LDARB for the proposed generic/no-RCpc baseline. This is a
compiler/object-disassembly reproduction, not an A10X device crash reproduction.

## Focused correction

The iOS preparation stack applies a final target-options patch after the dual
product target patches. Physical iOS SDK names/paths select the existing generic
ARM64 baseline with RCpc explicitly disabled. macOS and iOS Simulator retain their
existing target; tvOS retains its existing baseline. All runtime/common and
translated targets in `MKW_ALL_BUILD_TARGETS` receive the device correction.
The physical device build entry point rejects older prepared source before any
build or signing-residue changes, requiring fresh preparation.

Four focused tests pass: actual compiled-object disassembly with M2 negative
control and A10 assembler rejection; six CMake platform-selection cases;
preparation ordering; and refusal of stale prepared device source. Fresh
prepare-only execution of the complete current iOS patch stack also passes.
Shell syntax and whitespace checks pass. No full runtime/IPA build or device
operation was performed.

## Dependency and acceptance limits

The device Dawn archive remains pinned at SHA-256
`a361fcca75929fa5c766cfcde979c010a6da7d805e5db8e15c75e73fd8260e78`.
A bounded disassembly scan of the local v0.4.11 `libwebgpu_dawn.a` and the local
physical-iOS `libdiscio.a` found zero LDAPR/LDAPUR-family instructions. This is
not a complete ISA audit, nor proof that every linked static library supports
A10X. Target compile options do not retrofit prebuilt libraries. A fresh complete
binary and dependency audit plus physical acceptance remain required; no corrected
IPA or verified issue-135 fix is claimed.

Request the original report's exact app version/build, exception type/subtype and
codes, termination reason, crashed-thread frames (including symbol offsets), PC,
and KartPad Binary Images UUID/load address/range. For JSON .ips reports, retain
the matching usedImages entry and imageOffset; ARM ESR is useful if present.
Those fields distinguish the instruction above from abort/assert/loader failures
without requiring personal identifiers, saves or a full diagnostics archive.

## Cross-platform review correction

Independent review found that Android invokes the shared iOS preparation first.
Its later `wiicompiled-android-runtime.patch` still expected the old tvOS-only
conditional and rejected the target-options hunk. The follow-up updates that
hunk's context while preserving its `elseif(APPLE)` delta: Android gets no Apple
CPU flags; physical iOS retains the new baseline; Simulator/macOS remain as
before. A regression now replays the real Android hunk onto the iOS patch
postimage and evaluates the resulting Android condition. Five focused tests pass.
Fresh complete iOS and Android preparation both pass, with separate local logs
`build/cross-ios-prepare.log` and `build/cross-android-prepare.log`. No full game
build is involved.

The stale-source guard checks a preparation marker only. It does not prove the
configured or compiled flags. Before accepting a new physical iOS candidate,
the release owner must inspect generated build settings/actual compile commands
for every runtime/translated target and audit the final executable, including
this initializer's disassembly, for the intended baseline. Imported libraries
still need separate ISA consideration. The small compiled-object test establishes
the compiler behavior for its input only, not whole-application compatibility.
