# KartPad rights and licenses

KartPad is an independent, unofficial community project. It is not affiliated
with or endorsed by Nintendo. Mario Kart Wii, its executable code, game data,
characters, names, and other copyrighted material remain the property of their
respective owners.

## Community-preview release boundary

The maintainer authorized publication of the KartPad integration source and a
free, unsigned iPhone/iPad community-preview IPA on 1 September 2026. The IPA
contains KartPad's Apple integration and an ahead-of-time ARM64 translation of
the supported game executable. It does not contain a disc image, extracted
courses, textures, audio, saves, Apple signing identity, or provisioning
profile. Users must provide their own legally obtained supported PAL `RMCP01`
revision 0 game image after installation.

On 3 September 2026, the maintainer extended that same free, unsigned preview
authorization to the separate `v0.4.0-preview.1` iPhone/iPad and tvOS IPAs. The
tvOS artifact is explicitly a physically unaccepted hardware-bring-up build;
publication is intended to obtain that missing external evidence, not to claim
supported Apple TV functionality.

The previews include ahead-of-time Retro Rewind integration and an optional
official-pack installer. The downloadable IPAs do not contain the Retro Rewind
asset pack; KartPad downloads and verifies the matching official pack only when
the user selects that mode.

This release decision does not establish or grant rights in Nintendo material,
the translated game logic, WiiCompiled inputs, or third-party projects. It
records the same limited free community-preview posture used for the project's
other static-recompilation releases. Upstream and game-code redistribution
rights remain unresolved.

KartPad should therefore be described as source-available community software,
not as an official or broadly relicensed open-source release of Mario Kart Wii.
Paid access, commercial licensing, TestFlight, App Store, or other official
store distribution requires a separate decision and independent rights review.

On 7 September 2026, the fork owner requested a GitHub community release of
macOS and iOS packages for RMCP01 (PAL) and RMCJ01 (Japan). The Japanese
preview follows the same asset/signing exclusion boundary, with user-supplied
matching Japanese game data. PAL downloads preserve the original v0.4.8
upstream release bytes. This request does not alter the unresolved rights
boundary stated above.

## Third-party software

KartPad incorporates GPL-covered WiiCompiled and Dolphin-derived code plus
Aurora, Dawn, SDL, and other dependencies under their respective terms. The
public IPAs include the available license and notice files collected from the
exact pinned build inputs. The corresponding integration source, patches,
dependency pins, and build instructions are published with the release.

Nothing in this document relicenses third-party or Nintendo material. This is
an engineering and release-policy record, not legal advice.
