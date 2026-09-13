# Android 63 source reconstruction

The candidate built from `6a2dffc30f8f0d55a7eb928c614c88e054240d14`
has now passed a fresh runtime preparation and translation replay. This is source
reconstruction evidence; it does not replace physical testing, establish Apple
artifact identity, or constitute a new native build.

## Measured results

| Reconstructed input | Result |
| --- | --- |
| Android prepared runtime | All 877 files byte-identical; no extra or missing files |
| Patched WiiCompiled translator source | All 1,105 files byte-identical, excluding build outputs and Git metadata |
| Retro-aware base translation | All 29,637 function files byte-identical after tracked injections |
| RuntimeConfig.h, guest_symbol_table.cpp, data_sections_init.cpp | All three byte-identical |
| Retro translated source bundle | Byte-identical |
| mod_data_patches.cpp | Byte-identical |
| Resolved dispatch profile | Identical after relocation of source paths |
| Complete generated shard directory | 371 of 372 files byte-identical; shards.cmake identical after source/output-path relocation |
| Both binary-reference assembly wrappers | Identical after path relocation and the tracked Mach-O symbol aliases |

Fresh base translation took 40.10 seconds with two workers. Before applying the
tracked injection scripts, exactly six function files differed; afterward none
differed. There were no unexplained hand-edited base-function deltas. Mod replay
used the matching 6.12.7 pack and explicit locally supplied Retro-WFC payload.
The replay did not publish game inputs, generated game source or binary payloads.

## Reproduction recipe

Restore the delivered source snapshots and upstream locations using the source
package instructions, including the exact dependency pins. Supply the supported
disc and matching Retro pack/payload through the existing local Builder workflow.
The public manifest used for this candidate is
`tools/mkwii-rmcp01-retro-rewind.yml`. The historical `private/g8-full-mkwii.yml`
is not required: the candidate's `private/g8-full-translation` path was an alias
to the Retro-aware translation directory.

Before the translation command's final shard-emission step, seed the reviewed
partition map:

```sh
mkdir -p private/self-build/retro-rewind/translation/build_shards
cp tools/android63-base-common-shards.json \
  private/self-build/retro-rewind/translation/build_shards/base_common_shard_map.json
scripts/translate-retro-rewind.sh \
  --image /path/to/supported-game.wbfs \
  --retro-root /path/to/RetroRewind6 \
  --payload /path/to/payload.RMCPD00.bin
scripts/prepare-android-game-runtime.sh \
  private/self-build/retro-rewind/translation \
  build/reconstructed-android/source build/reconstructed-android/build dual
```

The last command prepares source only. Use the Android build instructions and
delivered dependency inputs for compilation. Choose fresh output directories.
`scripts/translate-retro-rewind.sh` rebuilds the patched translator, applies all
six tracked hook injections, creates the base manifest, translates the mod,
generates initialization code, and emits the dual graph.

`tools/android63-base-common-shards.json` contains only a build-format identifier,
version, partition name, shard count and 72 hexadecimal shard-start addresses.
It contains no instructions, function bodies, assets, paths or personal data.
The emitter deliberately retains existing partition boundaries across incremental
builds. Without this map, a clean emission produces a different valid partition;
with it, the candidate's complete shard source is reconstructed. It is delivered
as reviewed build metadata, not as game source.

The existing extractor currently requires one exact whole-image SHA-256 in
addition to validating the extracted DOL/REL. Its accepted file-extension list
does not mean every container of the same game revision is accepted. The matching
Retro-WFC payload is also an input; omitting it changes the generated program.

## Reusable software in generated outputs

Deliver the full patched translator, including `TranslatedBuildShardEmitter.cs`,
`ModDataPatchWriter.cs`, `DataSectionGenerator.cs`, `RuntimeConfigGenerator.cs`
and the CLI's guest-symbol emitter. These contain the reusable registration,
dispatch, initialization and patch helpers embedded in generated outputs.
Deliver the tracked translator patches and injection scripts as well. Excluding
private generated files is not a reason to omit this reusable software source.

Local replay evidence is retained under `build/release63-runtime-replay/` and
`build/release63-translation-replay/`. These ignored directories contain private
outputs and must not be added to release source archives. The retained-partition
comparison was repeated using freshly reconstructed base and mod outputs, rather
than merely rewrapping the candidate's old generated functions.
