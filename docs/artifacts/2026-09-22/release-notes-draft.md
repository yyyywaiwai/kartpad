# 0.5.1 release notes — draft, not approved for publication

Publication is held for the unresolved iPad Retro WFC login failure. Update this
draft after that gate is resolved; do not present it as an available release.

## Changes from 0.5.0

- Update the shared WiiCompiled base across Android, iOS/iPadOS and macOS to
  upstream revision 83463764b8ac, retaining KartPad's platform adaptations.
- Preserve a valid legacy console identity when creating the new NAND settings.
  Existing settings are kept. This prevents one identified upgrade path from
  assigning a new serial to existing online profiles; it cannot repair every
  previously registered profile or migrate a profile between different consoles.
- Preserve captured socket-send errors across diagnostic logging on all maintained
  platforms. Host tests reproduce the old error substitution; this is not proof
  of a fix for the reported WFC login failure.
- Add Android RVZ import, validated with a complete private disc extraction and
  file comparison. Users supply their own supported game image.
- Reduce repeated runtime work in vertex-state handling, command summaries,
  inactive input timing and audio memory lookup. Android also retains native
  binding and pipeline-cache improvements. These changes do not establish a
  universal FPS gain or resolve every device-specific rendering defect.

## Known limitations

- Missing or displaced character geometry remains reported on several Android
  GPUs. Moto G85 idle freezes and transition stalls remain under investigation.
- iPad Retro WFC error94020 remains unresolved. Do not describe this candidate as
  an online fix. One Android profile's successful login does not validate others.
- Retro Rewind ghost transfer and Android shake-to-trick are not added here.
  Original ghost transfer and Apple's existing motion features are separate.
- Mac Wii Remote/Classic Pro latency and physical D-pad behavior remain open.

## Candidate assets and validation

Local RC2 is Android code175, unsigned iOS/iPadOS build64, and macOS ARM64 build64.
All share compilation revision f8e295a. The Android APK uses the existing public
release certificate and passed isolated emulator in-place upgrade preservation
checks. The IPA requires signing for installation. No game images, saves or
private test logs belong in the release assets.

Package/source checks and bounded emulator observations are recorded in
[clean-rc2.md](clean-rc2.md); exact hashes are in
[clean-rc2-packages.json](clean-rc2-packages.json). These are preparation results,
not final physical-device or online acceptance.
