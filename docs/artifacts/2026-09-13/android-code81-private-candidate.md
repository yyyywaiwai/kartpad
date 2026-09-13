# Android code 81 private continuation candidate

This private candidate packages draft PR #252 after 624 translator tests, generated-continuation coverage checks, and a complete incremental Android native build/link. It is not a replacement public release or confirmation of Item Rain gameplay.

- Package: `dev.kartpad.android`, version `0.4.17-issue248.1`, code 81, debug signed.
- Source lineage: `19e2d78`; version/name are explicit Gradle packaging overrides recorded in embedded `private_candidate` provenance.
- APK SHA-256: `56b43e305b54aecfd89f542ca12784a3bd7b7878673557c219e1ba081b0e105a` (118,772,946 bytes).
- Packaged native runtime SHA-256: `d4f0281b7d9b1b9761492fd3a5f735769c70c7fbb1829969e46fa5a729ba10be`.
- Unstripped native runtime SHA-256: `4524a4d84e9db364b3e8ebbe8f9b54dc32a285976ae1fcaf19ed077b329a55a5`.

Packaging uses the retained Android wrapper and dependency inputs, an isolated JNI directory containing the newly linked/stripped runtime, and a private Gradle init script disabling native recompilation. The installed-facing version and embedded provenance were inspected. The normal APK audit passed, including native ABI/packaging, permission and private-asset checks; signature verification passed. The stable public code-80 APK/AAB were not modified.

The connected Pixel 9 Pro XL had private code 79. Its pulled installed APK and this candidate have matching signing certificates, permitting an in-place update. The pre-install inventory hashed 6,319 protected files. The owner then disconnected the phone for other use before installation. The backup transfer returned a truncated archive: local validation found only 2,781 entries and a tar read error. It is **not a valid restore backup**. No installation or candidate launch occurred; the phone remains on code 79.

On reconnection, take a fresh inventory and complete backup, validate every backup entry against that inventory, then perform the matching-signer in-place install and compare protected files before launch. Do not reuse the old inventory as current state after the owner uses the phone. The private incomplete backup and manifests stay local.

Remaining acceptance: affected Retro Rewind item/Item Rain paths, a complete race and relaunch, and controller/touch regression checks on the exact candidate. The reported `0x807EF16C` crash was not reproduced in KartPad; the concrete generated-code defect and its limits are documented in the PR. No online stability claim follows from this build.
