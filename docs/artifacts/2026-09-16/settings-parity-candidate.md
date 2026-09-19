# Settings parity candidates — Android 116 / iPhone 49

Both private test builds installed in place. Matching main-menu order: Return to KartPad Menu, Multiplayer, Show FPS Counter, Controls, Display, Game Data & Saves, Report a Problem.

Controls: Controller Button Mapping, Touch Control Settings, Controller Player Setup, Motion Steering, Experimental Wii Remote + Nunchuk. Mapping now opens mappings directly on iOS instead of entering controller setup first.

Display: Aspect Ratio, Render Resolution, FPS Counter Size. Small/Medium/Large use 1.0/1.5/2.0 font scales in both runtimes. The iOS setting updates an atomic value read by the FPS overlay, with a default preserving its previous size. Android-specific character rendering experiments remain under Android Graphics Diagnostics; they are not represented as working iOS features.

Game Data & Saves: Player Identity, Time Trial Ghosts (.rkg), Manage Saves, Manage Retro Rewind, Import or Reimport Wii Disc Image, Import from Extracted Folder, Remove Stored Game Data. iOS extracted-folder import now opens a folder picker. Existing import validation/removal confirmation is retained. iOS save export/restore was added with checksum/size validation, per-profile application on restart, a backup, pending-change conflict rejection and cancellation. Retro pack management retains platform-specific workflows: the iOS management page shows installed/required versions and routes through the game chooser to install/update.

The iOS report alert is replaced by a scrollable form constrained above the keyboard; labels/fields and actions have explicit spacing/minimum touch sizes. Diagnostic review uses a fixed-height scrollable log pane. The physical iPhone mirror verifies the landscape form's readable layout. Keyboard interaction and every subsequent report action still need owner acceptance; nothing was submitted publicly.

Hardware evidence: Android launcher/main/Controls/Display/Game Data hierarchies captured locally; ghost entry and remove-data row verified. iPhone49 rendered the new report form on the attached iPhone. Initial in-place state readback matched 37 Android and 26 iPhone files. Controller mapping, OS trace export and Apple identity/save tests passed, including new raw-restore isolation/backups/cancellation/conflict checks. APK audit and strict iOS signature verification pass.

Private APK and development-signed IPA are in `build/next-device-state`, with hashes in `settings-candidate-receipt.json`. iOS runtime/translation reuse and FPS-unit rebuild are recorded in `build/ios-next49/composition.json`. No public publication or FPS improvement is claimed. Real ghost replay and physical controller input remain pending.

Cumulative release copy is in `release-notes-next-draft.md`, checked against September 15 public iOS and Android 0.4.23 release notes.
