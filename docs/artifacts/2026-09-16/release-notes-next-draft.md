# KartPad next release — draft, pending hardware acceptance

## Shared updates from September 15–16

- Racing K icon and refreshed Original/Retro Rewind game chooser.
- Dark mode by default, a saved light/dark toggle, preferred game on launch, and a return-to-launcher action.
- License rename and Choose Mii repairs for missing Mii links, preserving progress and friend codes.
- Matching main-menu and shared settings ordering, with consistent import/removal labels and Time Trial Ghosts directly under Game Data & Saves.
- Physical controller remapping includes D-pad directions and triggers. Keep multiple actions on one button, or use the L1-for-items preset.
- Original time-trial `.rkg` import/export. Imported comparison ghosts apply on restart with a backup, preserving personal-best records and intervening progress. Retro custom-track ghost association is not supported.
- Save backup/restore for Original and both Retro save profiles. Miis and console identity are separate from raw saves.
- Small, Medium and Large FPS counter sizes on both mobile platforms.

## Reporting and platform details

- iOS: a scrollable, keyboard-aware reporting form replaces the crowded alert; diagnostic review has a bounded log pane. Logs record lifecycle, thermal, display and memory-warning events.
- Android: explicit private diagnostic exports can include retained OS ANR and native-crash traces. Missing or oversized traces are identified. Raw traces are not put into public issue metadata automatically.
- Android-only character-rendering experiments are labeled Android Graphics Diagnostics. Controller pairing and Retro installation workflows still follow platform capabilities; identical menu labels do not imply identical OS support.

## Performance and validation

No measured general FPS improvement is claimed. These are interface, control, save-management and diagnostic changes. Existing crashes, visual corruption, online/serial-identity reports and slow Android races are not declared fixed.

Private candidates: Android 116; iPhone 49. Build/package and host safety checks pass; in-place state preservation is verified separately. Real controller-button and ghost-replay acceptance remain pending. Public APK/IPA release signing and final publication are separate from these private device builds.

The iPhone candidate retains cached translated modules and most of the accepted runtime; it recompiles the launcher, controller, save/identity and diagnostics units plus the FPS overlay runtime unit. It is not a full latest-main rebuild.

## Short Discord draft

KartPad's next update brings the racing launcher and icon, clearer license/Mii controls, consistent settings menus, shared controller mappings, Original time-trial ghost import/export, save backups, and better problem reporting on iPhone/iPad and Android. Android performance work is still ongoing—this update does not promise an FPS boost. Please include the course, device, settings and reviewed logs when reporting a problem.
