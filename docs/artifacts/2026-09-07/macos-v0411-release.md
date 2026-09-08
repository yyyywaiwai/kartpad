# macOS 0.4.11 release verification

PR #98 merged at `0c700618e91eda0eac86cd134e3130c8f4fc37a0`. The annotated
`v0.4.11-macos.1` tag records that exact source; existing iPhone/iPad and Android
tags are unchanged. The Mac app is 0.4.11/build 26, ARM64, macOS 14+.

## Native build and local smoke

Fresh source preparation applied the pinned runtime patch stack and credited
issue #94 backport, then compiled both Original and Retro Rewind profiles.
The linked `SCGetProductSN_HLE` contains numeric byte reversal and a four-byte
store, with the guarded slow-write path. All 140 Python tests, repository safety
checks and the native Apple subsystem smoke passed. No dependency pin was
blindly advanced.

An isolated portable copy used the owner's existing authorized extracted data.
Original reached the Wii startup and animated title screen. The on-screen
counter read about 60 FPS; presentation samples were generally 59–60 FPS after
initial pipeline work. Non-silent PCM reached playback; telemetry recorded
zero empty-before-push checks and four startup-dropped blocks, not a claim of
zero audio drops. Native Command-Q exited with status 0. Installed save, Mii
database and configuration checksums were unchanged before/after the smoke.

The first smoke invocation mistakenly supplied a command-line profile option;
the runtime rejected it as unsupported. Retrying normally, with no arguments,
passed. No application code or audit was weakened to accommodate the test.
This was an Original startup/normal-close check, not a fresh Retro Rewind race,
production-online acceptance, controller hardware acceptance or long soak.

## Exact package

The post-merge build required no native recompilation. Candidate and final
unsigned packaged runtime hashes matched:
`d9ea55be400904d9c3ca106810241b8d0e2693cf2e29f31a98cdf2c9d90e0f68`.
The final signed executable hash is
`592463af4105364af176ab677c3173cd2ddebee9a7cfc61ae4962ddfb83c8562`.
Its ad-hoc signature also seals the updated exact-source build fingerprint.

- ZIP: `KartPad-v0.4.11-macos.1-arm64.zip`, **40,807,721 bytes**.
- SHA-256: `a20d7c3ea6afcfe63352d48ffad077cc5b4c2e86c0e210b26460e1213a71f383`.

Two independently packaged ZIPs matched. The extracted-package audit preserved
the required runtime symlinks and passed strict deep codesign verification.
The package contains pinned dependency notices, GPL text and exact-source
provenance, but not the portable smoke state, raw logs, user-owned data, saves,
account state or private signing material. The existing compiled-translated-logic
publication boundary is unchanged.

## Published and anonymously verified

Only the Mac ZIP and SHA256SUMS were uploaded. Fresh unauthenticated downloads
matched the local files, passed SHA256SUMS, and passed the full extracted-ZIP
audit against the tagged commit, including strict deep signature verification.
No older tag or asset was replaced. README, installation instructions and the
maintainer's #94 response identify the corrected platform downloads and retain
the old-tvOS/server-history limitations.
