# Android 63 source delivery

The release source archive supplies the source used by application commit
`6a2dffc30f8f0d55a7eb928c614c88e054240d14`, rather than only links to dependency
names. `SOURCE-MANIFEST.json` identifies every delivered file by SHA-256.

## Contents

- Exact Git snapshots of KartPad, WiiCompiled (including the complete translator
  and Aurora), Dolphin, the configured Dolphin dependency submodules, Retro
  Pulsar, the WFC patcher and Wiimms extraction tools. Each snapshot includes
  original commit metadata and per-file Git/SHA-256 identities, without history,
  credentials or machine configuration. `kartpad-apple` is the separately
  pinned Apple 0.4.15/build-34 source at
  `d3d300bb0364298b264378b13ba5561b42ca783d`.
- The actual 877-file modified Android runtime, including its headers, original
  dependency notices and preparation recipes in the KartPad snapshot. The
  companion Apple snapshots supply the 863-file iOS and 860-file macOS prepared
  runtimes. Their upstream runtime resource seeds are byte-identical to the
  pinned public WiiCompiled source; no device state is copied into them.
- Original hash-verified CMake and bootstrap dependency source archives, SDL
  3.4.4 source, Dawn source at `13abc3bc8ea2d3c2050f9e77a12d012108ceee24`, its
  build workflow at `03c49787b5634194bbee5fa448926a8e797ee49f`, and all 19 source
  dependencies selected by that Dawn revision's dependency-fetch recipe.
- Sources for all 38 code-bearing Maven runtime components. The 39th resolved
  component is the Kotlin coroutines BOM, which supplies version constraints
  rather than executable code. The dependency manifest records this distinction.
- The reviewed shard partition map, reconstruction instructions and packaging
  tools. Reusable software in generated output is supplied in the translator
  emitters and tracked injections, with fresh output equivalence verified.

No disc image, extracted retail assets, translated game functions, locally generated
game-data blobs, privately supplied mod payload, saves, device logs or private signing identity is
included. Public upstream source archives retain their upstream test fixtures
and license material; they are not copied from an owner's game or device.
The exact public `rr-pulsar` snapshot retains its tracked
`PulsarPackCreator/Resources/Code.pul` resource. No owner's downloaded Retro
pack or separately supplied WFC payload is copied into this archive.

## Restore source identities

After verifying the release's `SHA256SUMS`, extract the outer source archive.
Extract the three `KartPad-*-source.tar.gz` snapshot archives into one empty
directory. Their `source/` and `metadata/` entries have distinct names.

```sh
mkdir restored
for archive in KartPad-android63-core-source.tar.gz \
  KartPad-dolphin-dependency-source.tar.gz KartPad-profile-tool-source.tar.gz; do
  tar -xzf "$archive" -C restored
done
cd restored
for manifest in metadata/*.json; do
  python3 restore-source-git.py "$manifest"
done
```

The helper verifies source contents and reconstructs the original commit and
tree objects locally as a shallow repository. It refuses an existing `.git`;
it does not fetch, install or restore personal Git configuration. This matters
because the pinned build scripts check exact source commits and clean trees.

Place the restored `wiicompiled`, `dolphin`, `rr-pulsar`, `wfc-patcher-wii` and
`wiimms-iso-tools` trees at the paths in KartPad's `dependencies.lock.json`
(`Wiicompiled` has that capitalization). Move each `dolphin-Externals-*` tree
into the `destination` recorded in `dolphin-dependency-layout.json`, replacing
only the empty submodule directory created by restoration. Keep other Dolphin
submodules uninitialized: their code is not used by the configured DiscIO build.
The snapshots preserve the pins for them as well.

Copy the supplied `supplement/tools/android63-base-common-shards.json` into the
restored KartPad `tools/` directory. This supplementary partition metadata was
recorded after application compilation; it reproduces the existing generated
graph without changing application code. The original snapshot's source commit
remains the compiled application identity.

## Rebuild and modify

Use the snapshot's `android/README.md`, `scripts/build-user-ipa.sh bootstrap`
and `scripts/bootstrap-android-host.sh` for the macOS ARM64 host prerequisites.
The translator currently requires Homebrew .NET 8 at its documented path.
Host SDK/toolchain downloads and the user's independently supplied supported
game image are still required; the source archive is not a preinstalled SDK.

Use the [reconstruction recipe](android-source-reconstruction.md) with the
supported RMCP01 revision-0 image, matching Retro 6.12.7 pack and explicit WFC
payload. Their identities and acquisition checks are in the delivered profile
and bootstrap scripts. The current extraction script accepts one exact image
hash; do not infer that every differently packed image is supported.

Build the complete dual application with explicit metadata:

```sh
KARTPAD_ANDROID_VERSION_NAME=0.4.14-android-preview.1 \
KARTPAD_ANDROID_VERSION_CODE=63 KARTPAD_ANDROID_PACKAGE_FORMAT=aab \
  scripts/build-android-game-app.sh private/self-build/retro-rewind/translation
```

The source archives permit rebuilding dependencies instead of reusing their
prebuilt distributions. Dawn's included workflow records its Android NDK,
host-protoc build, CMake cache files and install/strip steps. Its included
`DEPS` and source-dependency manifest map each source archive to its destination.
SDL's source archive contains its Android build instructions. Dolphin is built
with `scripts/build-android-discio-probe.sh`, which applies the delivered patch
pair and uses the delivered JNI integration. The CMake, Maven and bootstrap
source manifests retain the exact versions resolved for this release.

For Apple, use the `kartpad-apple` snapshot with the same pinned upstream trees
and its platform build guides (`docs/BUILDER.md`, `docs/INSTALL_MACOS.md`).
The supplied Dawn source/build workflow covers the separately hash-pinned iOS
and macOS prebuilt distributions. SDL and the other native source versions are
shared. The Apple DiscIO source changes are the three tracked patches
`dolphin-ios-discio.patch`, `dolphin-ios-discio-coreless.patch` and
`dolphin-curl-ios-pipe2.patch`; fresh patch replay matched the configured source.
All ten configured Apple DiscIO submodule pins occur in the delivered Dolphin
dependency snapshots. The prepared source folders identify the platform-specific
runtime differences; use each platform's own preparation/build recipe.

For a modified dependency, point the existing build's dependency-root/provider
settings at your rebuilt install directory. The default bootstrap intentionally
continues to verify the published prebuilt hashes. Do not bypass those checks
and mistake a modified dependency for the original release input.

Sign your own build with your own identity using the supplied derivation script
and explicit expected version name/code. Public and private test certificates
are different; do not delete an existing installation to circumvent a mismatch.
The maintainer's signing key is not part of source delivery.

## Validation boundary

Fresh reconstruction matched the candidate's runtime, translator, Original
function source, Retro translated source, initialization and complete shard
graph, with documented path relocation. Exact Git restoration was independently
tested for KartPad, WiiCompiled and Dolphin. These results close the earlier
unexplained-source gaps; the old repository-only archive was insufficient.

This is not a claim that every dependency was rebuilt again or that arbitrary
new host toolchains produce a byte-identical APK. Existing native compilation,
package verification and repeat-derivation results remain separate evidence.
The rights and licenses in each source tree continue to apply; supplying
software source does not grant rights to the owner's separate game inputs.
