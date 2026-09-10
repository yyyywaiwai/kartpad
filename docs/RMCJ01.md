# RMCJ01 revision 0: port status

## Current boundary

**A separate Japanese ARM64 macOS development runtime now builds and boots.**
The supplied DATA partition passed Japanese menu, license creation,
save/reload, two completed three-lap time trials, restart/results, and host
audio checks. The final app also completed a retail staff-ghost replay at the
expected 5,615-input-frame boundary without diagnostic input overrides.
The additional Japanese dual-mode IPA builds and has user-reported iPad acceptance;
the region-J Retro Rewind candidate also reaches its title and license screens.
See [extended acceptance](RMCJ01-EXTENDED.md) for the current iPad/macOS scope,
the corrected mod link base, and historical runtime/online evidence limits.
The Personal IPA Builder remains gated with
`capabilities.build = false`; this flag is not the macOS development build flag.

The PAL profile and Apple import gates remain unchanged. Changing the disc ID
or accepting another DOL hash in the PAL app would leave its generated code,
native overrides, globals, and injected hooks at the wrong guest addresses.

## Verified local input (2026-09-06)

The supplied `MarioKartWii [RMCJ01].iso` and existing `data/` partition were
read, not patched or re-extracted. The ISO and extracted boot headers both
identify `RMCJ01`, disc 0, revision 0, Wii magic `5d1c9ea3`.

| Input | SHA-256 |
| --- | --- |
| ISO (4,699,979,776 bytes) | `78cb026411171d531bfbfa60e5e2d8ee94d73e855551de1c23d7231f34b8733a` |
| `sys/main.dol` | `1b9621ef7c5d97dada103e50e5389730e67f3c2545dda592edd4b5843655af91` |
| `files/rel/StaticR.rel` | `88539012d357a1420724e51dc7e351192ce696da4b0045994895518a3fad6fae` |

Decoded directly from the Japanese DOL:

- entry point: `0x800060A4`;
- r13 / `_SDA_BASE_`: `0x8038C580`;
- r2 / `_SDA2_BASE_`: `0x8038E920`.

The REL load address `0x8050FC60` was confirmed by the running Japanese
runtime's relocation report. Text is `0x8050FD34..0x8088EA6C`, constructors
`0x8088EA6C..0x8088ED70`, and BSS `0x809BC740..0x809C3FF0`. The DOL startup
sets the stack/arena boundary to `0x80398B00`. These are Japanese addresses,
not a claim that a fixed delta applies to the entire image.

The accepted image hash pins this one container. Recognizing an extension does
not automatically accept all Japanese dumps. DOL/REL hash validation proves
the critical executables match; it does not hash every course, sound, or other
asset in a user-supplied extraction.

## Commands from the repository root

```sh
./scripts/build-user-ipa.sh profiles

./scripts/build-user-ipa.sh inspect 'MarioKartWii [RMCJ01].iso' \
  --extracted-data data

./scripts/build-user-ipa.sh prepare 'MarioKartWii [RMCJ01].iso' \
  --extracted-data data

./scripts/build-user-ipa.sh audit-region \
  --profile mkwii-rmcj01-rev0 \
  --extracted-data data \
  --output private/rmcj01/audit.json

./scripts/test-kartpad-builder.sh
PYTHONPATH=builder python3 -m unittest discover -s tests -v
```

`prepare --extracted-data` does not copy, rename, patch, or add a manifest to
the supplied partition. The audit writes only a new report outside it; an
existing output file is rejected. Choose a fresh report name when rerunning.

The audit requires the WiiCompiled and Retro Rewind Pulsar source checkouts at
the commits recorded in `dependencies.lock.json`. This checkout has them under
`ref/upstream/`. The profile independently pins SHA-256 for both `MAP.txt` and
Pulsar `GameSource/versions.txt`; drift is rejected. The report fingerprints
the inspected native source content too. The audit needs no .NET, Dawn, game
translation output, Retro Rewind archive, or network payload.

## Address audit

Using the pinned WiiCompiled map and Pulsar `[J]` address intervals:

- 29,792 source map entries;
- 29,750 have a candidate address in the supplied intervals;
- 42 entries are outside those intervals;
- no destination collisions among the mapped entries;
- 788 native/translated registration markers across 583 distinct addresses
  have candidate mappings;
- 6 distinct `0x80......` literals in runtime `src/` and `include/` remain
  outside the intervals and need manual review.

The map contains both code and data symbols; **42 entries does not mean 42
missing executable functions**. Gaps include `RelStart`, ending/title movie
activation, and option-page paths as well as data symbols. Native coverage is
not proof that the replacement C++ bodies, globals, or ABI are region-neutral.
The literal inventory also includes comments and non-address constants, so it
is a review list, not an automatic replacement script. Addresses inside an
interval still need semantic review before changing runtime source.

No mapping is extrapolated across a gap. The audit is deliberately not emitted
as a translator manifest, and the Japanese profile has no PAL function map,
injectors, expected function counts, or PAL Retro-WFC payload attached.

## Development build and local acceptance

### Android ARM64

The dedicated Android entrypoint uses the existing Japanese translation graph
and address-porting workflow, then stages a separate Android host. It does not
enable Japanese input in the PAL app or the generic Personal IPA Builder.

```sh
./scripts/bootstrap-android-host.sh
KARTPAD_RMCJ_BUILD_TAG=android-japan \
  ./scripts/build-rmcj01-android.sh "$PWD/private/rmcj01/retro/translation" "$PWD/data"
```

Pass `private/rmcj01/verified/translation` for the original-game-only graph;
the wrapper automatically selects the dual product when the graph includes
Retro Rewind. These private graphs must already have been prepared by the
Japanese workflows; they are not included in the repository. Use a fresh tag.

The default result is a locally debug-signed APK at
`private/rmcj01/<tag>/host/android/app/build/outputs/apk/debug/app-debug.apk`.
The application ID is `dev.kartpad.rmcj01.android`, displayed as **KartPad Japan**.
It can coexist with PAL without sharing application data. JNI/Kotlin namespaces
stay unchanged, while the disc importer, exact DOL hash, original/Retro save
paths, and pinned `RMCJD00` download contract are Japanese-specific. DiscIO is
rebuilt separately, rather than reusing the PAL importer library.

The build command runs the APK package audit with `KARTPAD_ANDROID_AUDIT_REGION=J`.
It checks Japanese import/save contracts in addition to the existing ARM64,
16 KiB alignment, native dependencies, permissions and asset allowlists.
`KARTPAD_ANDROID_PACKAGE_FORMAT=aab` produces an unsigned AAB only; the existing
PAL release derivation/publication scripts are not a Japanese release lane.
Neither successful compilation nor package auditing proves Android gameplay,
controller behavior, save/reload, or Retro WFC networking on physical devices.
The iPad/macOS acceptance above is not Android acceptance.

`PYTHONPATH=builder python3 -m unittest tests.test_rmcj01_android` checks staged
Japanese contracts, PAL source preservation, and rejection of wrong-region
graphs, SDA bases, Retro module link bases, and reused/public output paths.

### macOS

The private development path is `scripts/build-rmcj01-macos.sh`. It validates
the original DATA input, stages pinned runtime sources, ports address-bearing
source tokens including `.inc` registrations, and keeps public PAL host sources
unchanged. It maps only executable seeds, adds actual Japanese REL relocation
targets and DOL code pointers, and recursively generates **29,655 functions**
from **29,636 seeds**. The emitted native graph has **29,083 shared base
functions in 72 shards**. Six selection/input/camera hooks are installed before
the shard bodies are materialized.

The runtime preserves the non-address division constant `0x80808081`. DOL/REL
section tables and exact relocation records supply the constructor boundaries
and movie audio table missing from the address intervals. Region-specific
functions are not fabricated by extrapolating a neighboring interval.

```sh
# Requires pinned source checkouts, .NET 8, CMake, Ninja and the pinned
# macOS Dawn archive in build/dependency-cache (see dependency scripts).
KARTPAD_RMCJ_BUILD_TAG=my-japan-build ./scripts/build-rmcj01-macos.sh "$PWD/data"
```

Use a fresh tag each time. Outputs stay under `private/rmcj01/<tag>` and
`build/rmcj01-<tag>-*`; the original DATA tree is never modified. A portable
marker and a new Config.toml beside the app isolate development saves/caches
from an installed PAL app. The config references the validated input folder.
The build script restores the previous `build/generated` symlink on exit.

The macOS acceptance report is
[RMCJ01 local macOS acceptance](artifacts/2026-09-07/rmcj01-macos-acceptance.md).
It records exact package/runtime evidence and separates normal retail replay
from diagnostic-input-assisted trials. Physical Apple device tests and the
Japanese Retro Rewind/Retro-WFC workflow are tracked in the separate
[extended ledger](RMCJ01-EXTENDED.md), not retroactively added to that original
base-game acceptance report.

```sh
KARTPAD_MACOS_AUDIT_REGION=J ./scripts/audit-macos-package.sh \
  "$PWD/private/rmcj01/my-japan-build/run/KartPad-Japan.app"
```

### Diagnostic findings

- The default `network.enabled = true` is needed for inherited local IOS
  WiiConnect24 VFF initialization. Setting it to false on a fresh private NAND
  produced the retail read/write error screen. Restoring the default allowed
  the unmodified save path to create a valid `RKSD0006` save with matching CRC.
  This test did not sign in to an online game service.
- The inherited opt-in RKG harness initially consumed input for all four Wii
  controllers and kept capturing menu input after the race. The Japanese
  development script applies a diagnostic-only primary-controller/lifecycle
  correction. Ordinary launches without RKG environment variables preserve
  the original controller implementation. A presentation-deduplicated trial
  reached lap three but diverged before finishing, so it is not completion
  evidence.
- Merely editing generated `functions/*.cpp` after shard emission has no
  effect: shard files contain copied bodies. Always inject first, then emit
  shards, compile and package.

The focused tests cover exact profile selection, wrong region/revision/magic,
missing files, tampered DOL/REL, read-only extraction reuse, CLI behavior,
incomplete-build guards (including direct pipeline entrypoints), address-map
gaps/overlaps, native marker scanning, and startup register decoding. A local
real-DATA test runs when the supplied `data/sys/main.dol` exists; it is skipped
on clean checkouts without game data. No copyrighted executable bytes or
translated game code are included in these tests.
