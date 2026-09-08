# Apple v0.4.9 release verification

- Implementation PR: https://github.com/chrissotraidis/kartpad/pull/86
- Release source: `8dd79d50b681a89fea9741f3da219332fa6c2196`
- Version: 0.4.9; iPhone/iPad and Mac build 23; Apple TV build 8.
- Release: https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.9

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| KartPad-v0.4.9-ios-unsigned.ipa | 40,798,003 | `e7d16c1c3b84f263b531c02c107f467993946f5f253dc1e09f0ef2dbc794c3f3` |
| KartPad-v0.4.9-macos-arm64.zip | 39,152,156 | `81b9f56a7866fcf90881cec7dd58441fac18d3e9bf424d6b128afe449ca810e3` |
| KartPad-v0.4.9-tvos-unsigned.ipa | 39,411,824 | `dccf2a00edd755ba861ceb987423ddd00e63c97ffb48239d96c4660d75ea763e` |

All three packages were built from the merged source and generated twice with
identical bytes. The iOS, tvOS and Mac prepared runtime sources matched fresh
preparations of the committed patch stack (ignoring patch backup files).
Fresh anonymous GitHub downloads matched the local archives byte-for-byte and
passed their complete extracted-app and public-distribution audits.
Full app audits and public-distribution audits passed, including game-data,
private-path, signing-material, version, and source-provenance checks.
The Mac package audit also checks that the bundled ICNS matches the current
export; its decoded 1024-pixel artwork matches the shipped iPhone/iPad icon.

Validation: 68 Python tests and 17 native tests passed. The actual WPAD probe
regression fails against the released 0.4.8 prepared source and passes with the
fix under both iOS and tvOS platform guards. Apple snapshot-controller fixtures
cover four stable slots, short A presses, non-consuming probes, disconnect and
reconnect. These are not physical two-/three-controller gameplay evidence.

An isolated Mac app was checked live for Multiplayer navigation, private-server
text entry, invalid-address rejection and cancellation. A disposable iPhone
Simulator ran Original Mario Kart Wii through the new Multiplayer entry,
Controller Setup, face-button remapping with safe A/B swapping, reset
confirmation and return to the game. An alert-dismissal transition defect and
landscape layout problems found during that review were fixed before merge.
The final server editor was visually checked with the landscape keyboard open;
Save and Cancel are both visible. The Simulator UI inspection connection later
stopped returning its window; a direct simulator capture confirmed the final
layout, and the disposable simulator was shut down after testing.

Private-server routing is experimental client configuration. No server was
hosted or deployed, and no exact private backend login, friend-room race or
reconnect was accepted here. Original Mario Kart Wii compatibility remains
unverified. MeleePad room codes, native host/join, traversal, ready state and
chat were not ported. The release includes the controller/server FAQ and the
precise supported paths in `MULTIPLAYER.md`.

No physical app installation was performed in this update. Original GameCube
USB adapter support on iPad was not added. Apple TV remains experimental.
The paused Android checkout remained clean at `0d8d19f` on
`codex/android-a4-touch-settings`; it was not merged or built. Its shared-patch
handoff and controller conflict resolution are documented.

Issue #85 received a release-linked explanation of the root cause, regression
evidence and exact-hardware limitations, and was closed as completed.

This evidence note follows the release source commit and does not change the
source identity or provenance embedded in the published archives.
