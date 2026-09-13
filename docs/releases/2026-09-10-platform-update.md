# KartPad September 10 update

New Android, iPhone/iPad and Apple Silicon Mac packages are available, with
checksums, notices and a shared source bundle containing the exact runtime,
dependency and translator source plus verified reconstruction instructions.

- **Android 0.4.14 preview 1 / code 63:** refreshed chooser and setup help,
  native frame overlap, safer UI snapshots during resize, first graphics-state
  initialization correction, reviewed-log reporting and save preservation when
  replacing a Retro Rewind pack. The owner accepted the tested payload on a
  physical Pixel. Existing public installations retain the same signing identity.
- **iPhone/iPad 0.4.15 / build 34:** review the actual diagnostic log before
  opening GitHub, explicitly acknowledge reviewing it, or explain why it cannot
  be attached. The newer chooser/help remains included. Logs are attached
  manually; nothing uploads automatically.
- **macOS 0.4.15 / build 34:** fixes graphics-view ownership during Metal view
  recreation. The separate keyboard/controller UI work is not included.

## Android measurements

Local controlled rendering-mode tests on a Pixel 9 Pro XL at 2x/Fill measured:

| Scene | Change disabled | Change enabled | Conservative gain |
| --- | --- | --- | --- |
| Warm Grand Prix menu | 39.52–49.96 FPS | 57.80–58.58 FPS | 15.7% |
| Stationary Retro scene | 51.363–54.157 FPS | 54.894–55.728 FPS | 1.36% |

These compare the rendering mode in earlier local builds, not the old public
APK against the final public APK. They support smoother animation in the tested
menu; they do not establish an across-device speedup. Main Menu to Single Player
transitions still took 2.580–2.732 seconds. Adreno graphics corruption, cup/awards
crashes and other device-specific reports remain open. No new Apple gameplay FPS
improvement is claimed.

## Downloads

- [Android APK](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.14-android-preview.1)
- [iPhone/iPad IPA](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.15-ios.1)
- [Apple Silicon Mac ZIP](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.15-macos.1)

Update in place using the same signing identity. The IPA requires re-signing;
macOS uses an ad-hoc signed app. The shared source archive is for rebuilding and
modification; it is not required to install the app. No game image is supplied.

[Artifact verification](../artifacts/2026-09-10/platform-release-verification.md)
