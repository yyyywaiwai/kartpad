# Reconstruct the Android 0.4.18 source inputs

Start with the checksum-verified source delivery. Restore the inner Git snapshots
with their included `restore-source-git.py` and metadata. Preserve the exact
pinned revisions when placing upstream trees under `ref/upstream`.

The delivered dependency manifests bind the native, Dawn and Maven source
archives. Their build recipes permit rebuilding those dependencies; the normal
bootstrap separately verifies its prebuilt distributions. A successful source
archive audit is not a claim that every dependency was rebuilt on a second host.

Use the delivered profile for the supported RMCP01 revision-0 game image,
Retro Rewind 6.12.8 and its exact WFC payload. Supply those inputs independently.
Run `scripts/prepare-patched-translator.sh` before the current translation
workflow. This release includes the Kamek continuation and shared LR dispatch
patches from PR #252; reusing an older translator omits those corrections.
Verify both the standalone REL guard
and the compiled aggregate shards. Do not reuse the historical Android63 shard
partition map as evidence for the current graph.

Prepare a fresh Android runtime with the delivered patches and compare its
fingerprint with `SOURCE-MANIFEST.json` before building. The supplied prepared
runtime is the comparison reference. The snapshot includes translator emitters,
patches and injection scripts rather than privately generated game functions.

Build the dual graph as an AAB with explicit `KARTPAD_ANDROID_VERSION_NAME`,
`KARTPAD_ANDROID_VERSION_CODE`, `KARTPAD_ANDROID_PACKAGE_FORMAT=aab` and
`KARTPAD_ANDROID_PROFILEABLE=0`, following `android/README.md`. Audit the AAB,
derive an APK with your own signer and explicit expected metadata, then audit
that APK. Changes to toolchains or dependencies need their own validation;
byte-identical rebuilds on arbitrary hosts are not claimed.
