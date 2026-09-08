# iPhone/iPad 0.4.11 published verification

PR #97 merged at `7f53ea0ef4942f10650f413ad53d7d331b0ef3d2`; the annotated
`v0.4.11` tag points to that exact source. A fresh full dual native ARM64 build
and post-merge rebuild passed the iOS app audit as 0.4.11/build 26.

The linked `SCGetProductSN_HLE` contains `REV w8,w20` and `STR w8,[x11]`, with
the guarded `MemoryInline::Write32Slow` fallback. This verifies the corrected
numeric four-byte write in the actual executable. Host regression tests cover
old collisions, distinct fixed serials, malformed input, byte order, bounds and
canaries; 140 Python tests and pinned-source/repository-safety checks passed.

- IPA: `KartPad-v0.4.11-ios-unsigned.ipa`, **42,420,756 bytes**.
- IPA SHA-256: `9b1df4a45743ebb6ff1716324afbfa459dd01d664eebd7ee59d8c5e0290701fa`.
- Executable SHA-256: `ad5ef4a98c3e1854c74fd2edc090a588a900059f74a53850e9191a34903f1328`.

Two independent packages matched byte-for-byte. The exact IPA audit passed.
Only the IPA and SHA256SUMS were uploaded. Fresh unauthenticated downloads
matched the local bytes, passed the checksum and passed the extracted-IPA
audit against the release commit.

The packaging/content model is unchanged from v0.4.10: unsigned translated
logic, no disc image, extracted retail assets, Retro pack, saves, account state,
signing identity or provisioning profile. Notices and exact-source provenance
remain included. These are package checks, not new legal clearance.

No device data was modified for this release. No new physical online-race or
server-history-remediation success is claimed. Re-sign using the existing
identity and update in place after backing up saves; do not uninstall to update.
