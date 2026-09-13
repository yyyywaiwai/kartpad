# macOS VSync: isolated Original startup comparison

2026-09-13. The experimental VSync source is merged through PR #255. PR #260 subsequently aligned the macOS Mii manager with the runtime's portable root. This record establishes startup mode selection, not gameplay quality or a tearing fix. No new public Mac release is published.

**Open pacing/audio gate:** the FIFO-on run logged `output queue full (15012/15360 bytes); dropping blocks to preserve continuity`. Do not describe this candidate as audio-clean, stable, or release-ready from these startup runs. The off/on test is too short and uncontrolled to attribute that warning to FIFO.

## Exact local candidate

- Source: `57d92c2198316b0dcc734d960e486510208271f1` (main with PR #260).
- All three native products were rebuilt after the Mii correction. The Original package passed the normal package audit before creating a separate launch clone.
- Packaged unsigned Original runtime SHA-256: `8972428982171ca32fe1758061f26ac62f5d46edbac2a6665a2954a4b3f9c37a`.
- The local audit package retains 0.4.17/build-39 metadata to exercise the package contract. The separately re-signed launch clone uses the unique bundle identifier `dev.kartpad.vsynctest.20260913`; its fingerprint identifies the newer source. Neither artifact replaces the installed app or the public build 39 download.

## Isolation established before launch

The app and extracted Original disc were copied into a fresh temporary root using APFS copy-on-write cloning. Every disc file had an independent inode and there were no symlinks; no writable hard links or owner save data were used. A `portable.txt` marker, fresh `UserData/Config.toml`, isolated working directory and temporary directory were created. The configuration used only the cloned Original disc, disabled networking and interpolation, and omitted custom NAND, overlay and Retro roots.

A production-code path probe inside the cloned app verified the actual runtime data/cache roots and Mii-manager root all resolve into the isolated tree. It also verified the unique bundle preferences domain, absent profile/private-server/Wiimote preferences, no pending Mii changes, and the fresh config values. The app was then launched with a minimal environment rather than inheriting diagnostic/path overrides.

An operating-system sandbox denied network access and all direct file writes outside the isolated root. A permitted in-root write and a rejected out-of-root write were checked before launch. The unique bundle domain separately isolates AppKit preferences handled by system services.

Thirty normal application-support/preference files were hashed before the comparison. After both launches every hash matched and there were no new normal application-support files. No owner app, save, identity or preference change was observed.

## Bounded results

Each Original launch ran for 18 seconds, then received a requested termination and exited with status 0. No race, input sequence, monitor change or fullscreen transition was exercised.

| Saved preference | Actual startup evidence |
| --- | --- |
| Off | `Using surface format BGRA8Unorm, present mode Immediate` |
| On, after restart | `VSync requested: selecting Fifo (restart required to change)` followed by `Using surface format BGRA8Unorm, present mode Fifo` |

Both reached non-silent PCM delivery and approximately 60 presentation samples per second during startup. These counters are not listening checks or game-time pacing acceptance. The off run also reported that the fresh NAND lacked `wc24dl.vff`; the on run reported the audio queue-full/drop warning above. Shader compilation was still active, so this is not a warmed comparison.

## Remaining gate

Keep #250 open. Physical phone-camera tearing evidence, warmed gameplay/game-time comparison, listening checks, interpolation above monitor refresh, window/surface recovery and monitor transitions remain unverified. Retro was built but not launched in this comparison: its Riivolution save redirect can target the virtual SD root, so a future test must independently clone and verify that writable root too.

Private local evidence is retained in the candidate worktree's `build/launch-path-probe.log`, `build/isolated-startup-result.log`, `build/normal-data-before.json`, `build/audit-mii-fixed.log`, and the isolated root's `startup-off.log`/`startup-on.log`. The normal-data manifest and game-derived artifacts are private and must not be attached to public issues.
