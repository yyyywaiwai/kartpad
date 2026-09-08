# iPad identity clarity — 0.4.10 build 25

The maintainer tested build 24 on iPad and reported that returning to the chooser,
reopening to switch games, and deleting and creating Retro Rewind licenses
worked. The remaining confusion concerned identity versus license editing,
slot numbering, and applying pending changes.

Build 25 renames the iPhone/iPad actions to **Rename or Delete Licenses…** and
**Edit Mii Name…**. The identity summary and empty-license state explain that a
Mii supplies a name and appearance, while a game license stores progress and a
friend code. New licenses are created through **New** inside the game.
Deletion affects only its selected slot; other licenses retain their slots.

Pending-change messages explicitly require fully closing KartPad from the app
switcher and reopening it. Returning to the KartPad menu and resuming does not
apply them. Identity result alerts now use the existing transition-aware alert
presenter so their confirmation waits for the previous alert to dismiss.

Validation:

- 68 Python checks and 17 native tests passed.
- Fresh preparation reproduced the runtime source, with only the intended
  build-number increment from 24 to 25.
- Physical iOS/iPadOS compilation and the full app audit passed. The audit's
  expected name-editor label was updated to **Edit Mii Name**.
- The rebuilt iPad Simulator showed the new identity action labels, explanatory
  text, and Mii name editor. Saving the unchanged test Mii name displayed the
  **Mii Name Scheduled** confirmation with the full-close/reopen instruction.
- Build 25 was signed locally, installed in place on the attached iPad, and
  relaunched. The installed version and live process were verified. All 407
  protected files were byte-identical after installation. After launch, saves
  and preferences still matched; Config.toml was rewritten with equivalent
  values. No earlier save backup was restored over the maintainer's new license.

The new IPA is an unsigned iPhone/iPad artifact. Mac and experimental Apple TV
remain on 0.4.9, and Android development remains paused. Native private-room
transport and safe in-process game switching remain separate unfinished work.

## IPA evidence

- Source: `404b74c319267126a44c5ae1e4a07a04cf3a213d`.
- Artifact: `KartPad-v0.4.10-ios-unsigned.ipa` (40,800,024 bytes).
- SHA-256: `cd7221b87447a638f8ea131d6581563301cd31fb1f7ca23c1e57ccb7e9bc4063`.
- Two packages were byte-identical. The exact IPA passed ZIP, provenance,
  signing-material, private-data, executable-path, and full app audits.
- The local artifact was copied to the maintainer's Downloads folder and its
  hash rechecked. No GitHub release or hosted-download verification was performed.

## Maintainer acceptance

On 2026-09-07 the maintainer accepted the current Mac, iPhone and iPad builds
for general use and authorized merging and publishing. The latest physical
check was build 25 on iPad: Retro Rewind launched, Game Data & Saves was clear,
and the Retro WFC menu allowed scrolling to Friends. This observation does
not establish a completed production-online race. The accepted app behavior
is frozen for the release; only documentation and release provenance change.

## Published release

The accepted app was released from merged main as v0.4.10. The release package
updates documentation and provenance while preserving every app file from the
accepted build. See [hosted release verification](../artifacts/2026-09-07/apple/v0410-release-verification.md)
for its final checksum and anonymous-download audit. The earlier IPA evidence
above describes the pre-merge local candidate.
