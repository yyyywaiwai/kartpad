# Android code 82 combined device candidate

Private version `0.4.17-candidate.2` / code 82 combines merged Preferred Game (#266) with draft continuation handling (#252). It is distinct from published code 80, which already shipped the D-pad editor and FPS sizing changes. Closing #238 did not produce another APK.

## Artifact and checks

- Combined clean source: `68608a8df327ee27a7c27d0d5730b145d0d6ed9c`.
- APK SHA-256: `08c3490e56615e1cca4d6d681a5dcc70b451db2b3a8794a60fb9b9d6a82a9a84`; 118,773,014 bytes.
- Packaged native runtime SHA-256: `d4f0281b7d9b1b9761492fd3a5f735769c70c7fbb1829969e46fa5a729ba10be`, native source lineage `19e2d78`.
- All four native libraries match audited private code 81. Changes from code 81 are DEX, manifest and embedded provenance; Preferred Game classes/UI are present in the DEX.
- Version/name are explicit private packaging overrides recorded in provenance. Actual Kotlin/Java compilation, assembly, storage/startup tests, standard APK audit and signature verification passed.

The attached Pixel 9 Pro XL started on private code 79, already containing the previously tested D-pad/FPS UI changes. The code-82 signer matches that installation. A fresh 6,319-file protected-data inventory and full backup were captured. Every archive entry matched the inventory before installation. Matching-signer `adb install -r` succeeded; the installed version is code 82. All 6,319 protected files were unchanged immediately after installation, before launch.

## Release boundary

This candidate has not replaced public code 80. Installation/startup and preference UI checks do not establish Item Rain gameplay, completed-race/relaunch, or online acceptance. A public-signed package and its source/notices/checksums must be prepared and verified only after the exact candidate receives the required gameplay acceptance. Never uninstall or reset identities to move between private and public signing identities.

## Physical Pixel UI/startup checks

- Fresh launch with the default Ask Every Time preference reached the chooser; both existing profiles validated.
- Opened Preferred Game on the actual phone, selected Original, and verified changing the option did not immediately launch. After force-stop/relaunch, Original reached its title screen. The saved Original radio choice persisted.
- Used the actual game menu’s Return to KartPad Menu action; the paused chooser remained visible despite the preferred game.
- Selected Retro Rewind, restarted, and reached the Retro title screen. Its saved radio choice persisted; Return to KartPad Menu again stayed at the chooser.
- Restored Ask Every Time through the UI and restarted; the phone was left at the chooser for owner gameplay testing.
- The native preference dialog and labels were visually inspected. The D-pad and large FPS display remained present during both startup checks. This does not substitute for gameplay or controller acceptance.

After these UI/startup checks, no save, license, Mii/identity, game-data, or existing settings file changed. Differences were log rotation/new logs, the installed-profile marker, WorkManager WAL/shared-memory state, and the new `PreferredGame` file. Full private manifests and the verified backup remain local; they are not public attachments.

The owner was asked to test an Original race, a Retro race, relaunch, and Item Rain if available. They subsequently reported: “the game works.” This is recorded as general physical gameplay acceptance of installed code 82 and authorization to proceed with the public package. No exact course, completed-race count, Item Rain coverage or online result was supplied, so none is inferred. #248 remains open for its specific affected-path result. The phone runs private code 82, not the prior code 79 or public code 80.

The continuation source is merged in #252 after its translator/native checks, physical startup checks and owner gameplay acceptance. Public 0.4.18/code 83 packaging is being prepared with the same tested Android wrapper and native runtime; exact published-artifact verification is a separate gate.
