# Console identity upgrade regression

## Confirmed cause

The owner reported both existing iPad profiles rejecting the console serial after
installing upstream.1 build61. Before the upstream integration, KartPad read the
persisted nine-digit serial from Application Support/KartPad/ConsoleIdentity.txt.
The new upstream runtime reads NAND setting.txt instead. That file did not exist
in the pre-install backup, so first launch generated a different serial. Preserved
save bytes alone were insufficient to preserve the registered console identity.

Readback confirmed the old identity file was unchanged, the old NAND had no
setting.txt, and the new settings serial differed from the preserved old serial.
The same source-level migration gap affected all four platform runtime branches.
This is an integration regression, not evidence that the owner's saves are bad.

## iPad recovery

Stopped the app and took a fresh backup of functional state. Generated the encrypted
256-byte settings using the runtime's tested encoder and the preserved old serial.
Decoded comparison confirmed every settings field except SERNO stayed identical.
Kept the generated settings as an on-device backup and a private local backup,
then replaced only setting.txt. Readback verified the restored bytes and that all
32 other checked files, including Original/Retro saves and preferences, were
unchanged. Relaunched the installed build61. The owner subsequently reported that the second profile passed the serial check,
but stalled entering Retro WFC with error 94020 before matchmaking. This is not
complete online acceptance; no race is claimed.

## Cross-platform prevention

All four maintained runtime branches now seed a missing managed-NAND setting.txt
from a valid existing ConsoleIdentity.txt. The legacy file is retained unchanged.
Malformed/unreadable legacy identities fail with a recovery error rather than
silently minting a new serial. Unmanaged/imported NAND keeps its own initialization,
and existing settings are never overwritten automatically.

Added regression coverage for registered-serial migration, migration with an invalid
clock, byte preservation, existing settings precedence, malformed legacy identity
and unmanaged NAND isolation. The complete NAND settings suite passes with
ASan/UBSan for all four maintained source trees on the host and as an NDK API28
arm64 executable on the attached Android device. The latter is a shell test,
not app-sandbox or profile-login acceptance.

The earlier build61/code171 distribution packages do not contain these corrections.
Corrected local candidates now include Android code173 and Apple build62; see
[release confidence](release-confidence.md) for verification and remaining gates.
Users already booted on the faulty upstream candidates may have a generated
setting.txt; the preventative migration deliberately does not overwrite it.
They need a backup-backed reconciliation against their preserved legacy identity,
like the verified iPad repair. Do not release the earlier candidates as upgrade-safe.

Private receipts: work/identity-repair-20260922 and
work/upstream-device-install-20260922/identity-regression.json. They contain private
identities and saves and must not be published.

## Retro ghost release scope

Recommend a subsequent feature release, after this identity regression is resolved.
Read-only Retro RKG export is the smaller part. Complete import must preserve the
track, variant and time-trial mode identity plus leaderboard/favourite/trophy
relationships. Implement shared validation/transfer rules for Android, iOS/iPadOS,
macOS and other supported hosts, with platform-specific file pickers. Existing
Original rksys slot transfer cannot simply be pointed at Retro files. Neither
Retro transfer nor Android shake-to-trick is delivered by this repair.

## Follow-up device evidence

Android code173 adds an explicit, backup-backed previous-console-identity recovery
action. Host tests cover staging without mutation, settings replacement, unchanged
save bytes, retained backups, repeat requests, concurrent changes and noncanonical
settings rejection. The release APK passed packaging checks and installed in place.
The owner then reported that the first Android profile reaches Retro WFC while the
second still fails. Recovery has **not** been invoked: a global identity change could
affect the working profile. Do not infer that both profiles were registered against
the same serial, or that the second profile was already broken before these builds.

iPad build62 adds opt-in TCP event diagnostics for WFC control ports. It records
operation, byte count, host error and a fixed protocol-command label, not packet
payloads, tokens, serials or profile identifiers. Installed with the same signing
entitlements; all 35 backed-up identity, save and preference files matched after
installation. Launched with tracing enabled for a fresh owner login attempt.
The 94020 cause and fix remain unverified; this build is diagnostic, not a claimed
network repair. Private evidence is under work/mobile-network-repair-20260922.
