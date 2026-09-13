# Candidate 63 source-package assessment

**Historical assessment:** the gaps below were subsequently addressed by the
[fresh source reconstruction](android-source-reconstruction.md) and
[actual source delivery](android-source-delivery.md). Retained here to explain
why the initial repository-only archive was insufficient.

This is a bounded technical inventory, not a complete source-distribution or
rights certification. It does not change the APK, game settings or phone state.
The candidate APK and its 28-entry notices package remain those recorded in
[the verification record](android-release63-verification.md).

## What was verified

The local repository archive for application commit
`6a2dffc30f8f0d55a7eb928c614c88e054240d14` has SHA-256
`2e9c689f0b4b7aad4130c2a6f268f112d7e2bc5af663ec6224201da211db00c5`.
All **1,117 archived files** exactly match their Git blob identities at that
commit; none are added from the working tree or ignored build directories.
The archive includes existing tracked documentation images and the Gradle
wrapper JAR as well as application source, patches, recipes and dependency pins.

Path checks found no private/build/bootstrap paths, traversal, links, or game,
package and signing-file extensions. A focused content scan found no structured
private-key blocks, GitHub/AWS credential patterns, or ELF binaries. This narrow
scan is not a guarantee that arbitrary secrets or rights-sensitive content are
absent. The archive remains outside the proposed APK/notices download directory.

## What the repository archive does not contain

The actual release CMake compilation database contains the following command
groups. These count translation-unit compile commands, not total source files
or a complete inventory of headers, generated includes and linked libraries.

| Source group | Compile commands | Repository archive coverage |
| --- | ---: | --- |
| Tracked KartPad integration | 14 | Source included |
| Prepared upstream/runtime | 244 | Upstream checkouts omitted; tracked patches/recipe included |
| CMake dependency source | 267 | Dependency checkouts omitted |
| Bootstrapped dependency source | 127 | Dependency checkouts omitted |
| Private translation/game-derived generated input | 237 | Generated graph omitted |
| Generated compilation wrappers | 17 | Origins mapped below; transitive inputs and source delivery remain separate |

The embedded build provenance separately fingerprints 877 prepared-runtime
files and 30,030 translation-input files. A pin or fingerprint identifies an
input; it does not supply its contents. Prebuilt Dawn, SDL and the retained
DiscIO dependency also need their source/build provenance considered outside
this main-library compilation database. The normal build guide reconstructs
inputs using the pinned bootstrap and an owner's supported game image; that
recipe has not been independently reproduced from this source archive alone.

## Generated wrapper origins

The Android owner and an independent Astra Medium reviewer completed a read-only
classification of all 17 wrappers, checking their hashes and one compilation
entry per wrapper. No builds, device actions or binary payload reads were needed.

- Four CMake precompiled-header wrappers use forced sibling headers that lead to
  `mkw_pch.h`.
- Eleven unity wrappers follow the pinned runtime's `cmake/PublicProducts.cmake`
  grouping recipe. Their 73 distinct source includes comprise 41 byte-identical
  upstream files, 30 modified files with corresponding tracked patch headers,
  and two private generated inputs. Matching patch headers do not establish a
  fresh successful patch replay.
- Two assembly wrappers exactly match the Android section-name rewrite of their
  generated originals. Their 13 binary-include paths exist locally; this review
  did not read or hash those binary contents.

The upstream revision is `1912292c804ff9b1b79938de89369ec4496f9fff`.
Preparation uses `scripts/prepare-ios-game-runtime.sh` and
`scripts/prepare-android-game-runtime.sh`; translator preparation and generation
use `scripts/prepare-patched-translator.sh`, `scripts/translate-retro-rewind.sh`
and `scripts/generate-g8-full-title.sh`. The two private unity inputs are
`guest_symbol_table.cpp` and `data_sections_init.cpp`.

This resolves the 17-wrapper classification. Wrapper identities bind reference
text, not all historical transitive build inputs. Exact dependency/prebuilt
provenance, source delivery and independent reconstruction remain open. Do not
repeat this classification or upload private generated inputs to close those gaps.

## Concrete remaining work

1. Bind transitive generated inputs and every linked dependency to retained
   source, tracked modifications and the exact build recipe. Do not substitute
   an upstream version merely because its name matches.
2. Determine the complete source delivery required for this binary, then supply
   the missing covered source through the project's documented distribution
   process. Do not upload private game-derived inputs to resolve the gap by
   assumption. The existing [rights/source policy](../../../RIGHTS_AND_LICENSES.md)
   remains applicable.
3. Verify reconstruction from the proposed source delivery with independently
   supplied supported game inputs where the recipe requires them. Keep this
   distinct from repeating the APK derivation, which already passed.

This turns the generic source-review gate into an explicit inventory. It does
not add an FPS improvement, clear physical acceptance, or authorize publication.
No phone input, install, build, emulator restart or public message was needed
for this assessment. Private machine-readable evidence is retained locally in
`build/release-final/repository-source-content-audit.json`.
