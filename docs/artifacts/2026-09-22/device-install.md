# Upstream candidate device installation — 2026-09-22

## iPad

Installed 0.5.1 build 61 in place over build 60 using the existing bundle ID,
entitlements and a valid matching development provisioning profile. Strict code
signature verification passed. The source IPA is the exact upstream.1 candidate
listed in candidate-packages.json.

Before installation, backed up 33 functional files: the full 2,778,726,400-byte
WBFS image, Original and Retro saves, NAND identity/settings, preferences and
existing save/Mii backups. All 33 size/SHA-256 pairs matched the post-install
readback before first launch. Extracted game/Retro asset trees were retained in
place; no claim of an exhaustive asset-tree hash. Launch succeeded. Wired
QuickTime preview showed Original and Retro both ready in the chooser. No race,
performance, audio or new-build gameplay acceptance is claimed. No preferences
were intentionally changed. No recording was made.

## Android

Preserved the installed code170 APK locally and confirmed its signing certificate
matches the new private release candidates. In-place install of code171 succeeded;
its launcher recognized both existing games. Starting Original then aborted on
the SDL thread, immediately after Android SELinux denied a hard link for NAND
setting.txt. Code171 is rejected for device use; its AAB has the same affected
native payload. These artifacts are historical evidence, not release-ready.

The maintained Android runtime now publishes new NAND identity settings through
renameat2(RENAME_NOREPLACE), retaining atomic first-writer-wins behavior without
requiring prohibited hard links. Existing valid or damaged identities are never
overwritten. The existing NAND settings suite passes on the macOS host and as an
NDK arm64/API28 executable on the attached Android device, including concurrent
creation and preservation cases. The shell test is not an app-sandbox test.

Code172 (0.5.1-upstream.2) was rebuilt, passed the release APK audit and installed
in place. Package manager confirms code172. Exact native BuildID matches retained
private symbols. After unlocking the device, Original reached the actual Mario Kart Wii title
screen. This verifies the corrected startup in the app sandbox; it does not
establish race performance, Retro gameplay or complete feature acceptance.
ADB-injected A presses did not establish entry into licence selection; title/demo
continued rendering. Physical touch acceptance remains explicitly unverified.

Android private app data is not readable by ADB because the release is not
debuggable. No private save hash comparison or complete Android backup is claimed.
No uninstall, clear-data, profile replacement or cross-device save transfer occurred.
The package identity and OS-managed data container were retained.

## Feature parity

The installed iOS/iPadOS code already has an independent shake-tricks preference
under Motion Steering → Enable Shake Tricks/Wheelies, with one-shot input wiring.
Android shake-to-trick remains unimplemented. Implement equivalent behavior using
gravity-removed acceleration, matching units, rearm/cooldown and lifecycle clearing;
do not apply the iOS thresholds directly to Android gravity measurements.

Retro ghost transfer should use shared file validation, track/variant/mode identity
and collision/backup rules across Android, iOS/iPadOS and macOS, with host-native
pickers. It remains unimplemented in these installed builds. Retro ghosts are
separate RKG files with associated metadata, not Original rksys 32-slot offsets.
See ../2026-09-21/feature-follow-up.md for the existing research and implementation
boundary. Do not present either parity follow-up as newly delivered here.

Private receipts/backups are retained in the working checkout at
work/upstream-device-install-20260922. Do not publish its signing material,
identifiers, game data, saves or screenshots containing personal content.

## Subsequent identity regression

Owner testing found a serial mismatch on both iPad profiles despite the byte-preserved
saves. See [confirmed cause, iPad recovery and cross-platform migration fix](console-identity-migration.md).
Earlier startup evidence is not profile compatibility acceptance.
