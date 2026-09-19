# Android character graphics comparison source delivery

This delivery corresponds to experimental Android code 91, app version
`0.4.21-matrix.1`, release tag `v0.4.21-android-matrix.1`. Its compiled KartPad
source is `62798c932eb1320f1ed392c0cc61e06d23cc616c`. The outer
`SOURCE-MANIFEST.json` binds the public APK hash, application source, supplemental
metadata commit and every delivered file. Documentation added after compilation
is a supplement; it does not change the compiled source identity.

## Delivered inputs

The bundle contains the exact KartPad Git snapshot, pinned WiiCompiled
`1912292c804ff9b1b79938de89369ec4496f9fff`, Dolphin
`4f8af23db516d8b6e9cd00e7b261a65b026514a8`, configured dependency source
snapshots/manifests, profile tools, and the prepared Android runtime. Native,
Dawn and Maven dependency selections are unchanged from code 85; retained
archives are checked against their source manifests before assembly.

The prepared runtime has 880 files and fingerprint
`45919ad2ea6abd481575252b7ecb375c7fd81d6b353935481edfdad2f2b3aff8`
using `scripts/write-build-provenance.py`'s tree algorithm. Compared with the
immutable code 85 source delivery, exactly three prepared files differ:

- `aurora-main/lib/gx/gx.hpp`
- `aurora-main/lib/gx/shader.cpp`
- `aurora-main/lib/gx/command_processor.cpp`

These changes are represented by `patches/aurora-android-targeted-pnmtx.patch`
in the compiled Git snapshot and included in Android runtime preparation.
No translated game functions, game images, extracted assets, downloaded packs,
saves, device logs, or signing credentials are included. Public upstream source
snapshots retain their own source resources and test fixtures.

## Reconstruction

Verify the published checksum and the outer manifest before extracting. Restore
the inner Git snapshots with their included `restore-source-git.py`, then place
the upstream sources and Dolphin submodules as recorded in `dependencies.lock.json`
and `dolphin-dependency-layout.json`. Use the adjacent
[Android source reconstruction guide](../2026-09-13/android-source-reconstruction.md)
for dependency setup and independently supplied supported game inputs.

Regenerate the translation with the delivered translator patches rather than an
older generated graph. Prepare a fresh dual runtime with
`scripts/prepare-android-game-runtime.sh <translation-root> <fresh-runtime-source> <fresh-runtime-build> dual`.
The prepared-runtime files in this delivery are the exact software comparison
reference; inspect any fingerprint difference before building. The pipeline test
patch is already in the preparation sequence and must not be applied twice.

Build the dual Android graph following `android/README.md`, explicitly selecting
`KARTPAD_ANDROID_VERSION_NAME=0.4.21-matrix.1`,
`KARTPAD_ANDROID_VERSION_CODE=91`, `KARTPAD_ANDROID_PACKAGE_FORMAT=aab`, and
`KARTPAD_ANDROID_PROFILEABLE=0`. Audit the AAB, produce an APK with your own
signing identity, and audit its metadata. The maintainer's key is not supplied;
a different signer does not permit overwriting an installed Community Release
app. Byte-identical builds on arbitrary toolchains are not claimed.

Normal leaves `KARTPAD_RENDERER_CONST_PNMTX` unset. The original-index comparison
uses `0`, and the compatibility-index comparison uses `1`. The app stores the
selection across processes and applies it once at native-process startup;
changing the selection requires fully closing and reopening KartPad. The two
comparison modes share bounded diagnostics and draw behavior. They are not FPS
benchmarks, and package/source validation does not establish a graphics fix on
an affected device.

## Fresh preparation verification

A fresh full ordered Android preparation passed after packaging. All three
modified renderer files match the compiled runtime exactly. The whole-tree
fingerprint differs because current preparation also carries Apple-only
SafariServices link entries in `cmake/PublicProducts.cmake` and patch `.orig`
backup files. Those are not compiled Android changes. The delivered prepared
runtime remains the exact reference used for code91; an arbitrary fresh tree
is not claimed to have the same all-file fingerprint.
