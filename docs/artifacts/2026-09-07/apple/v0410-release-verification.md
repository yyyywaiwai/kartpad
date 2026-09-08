# iPhone/iPad v0.4.10 release verification

- Implementation and documentation PR: https://github.com/chrissotraidis/kartpad/pull/88
- Merged source and release tag: `33d828350fc4812391d00ff692771b52a80db956`.
- Version: 0.4.10, iPhone/iPad build 25.
- Published release: https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.10

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| KartPad-v0.4.10-ios-unsigned.ipa | 40,800,315 | `b99283c24fd9c5a9a244c7075ca87321edc2a0e3d50dfbd96372c47757eb55cc` |

The maintainer accepted build 25 on physical iPad after checking Retro Rewind
launch, Game Data & Saves, and navigation to Friends inside the Retro WFC menu.
Earlier checks covered license deletion/creation, chooser navigation, and
reopening to switch games. The maintainer accepted the current Mac, iPhone and
iPad builds for general use and authorized this merge and publication.

The app was rebuilt from the exact merged source. All 21 files in the unsigned
app bundle match the physically accepted build byte-for-byte, including its
executable SHA-256 `249ac741997fc7e9fd22171d5e9d239f35b6f01d415ed3d57837ad29a20ea38b`.
No runtime or device-state changes were made during release preparation.
The release IPA differs from the earlier local candidate because it includes
updated installation/release documentation and merged-source provenance.

Two release packages were byte-identical. The exact IPA passed the complete
unsigned audit, including version, source provenance, ZIP integrity, required
notices, private-data exclusion, signing-material exclusion, private-path
exclusion, and the extracted iOS app audit. Uploaded asset sizes and SHA-256
values matched locally. Fresh anonymous downloads of the IPA and SHA256SUMS
matched their local files byte-for-byte; the downloaded IPA passed the same
complete audit. The release tag resolves to the merged source above. The
maintainer's Downloads copy was updated to the verified published IPA.

The 68 Python checks passed before merge, and the existing 17 native tests
passed for build 25. Fresh runtime preparation reproduced the build source.
Simulator checks verified the identity labels, name editor, and scheduled-edit
confirmation. Prior chooser/resume checks are recorded in the iteration notes.

The accepted Mac ZIP remains in v0.4.9, as does the experimental Apple TV IPA.
Android remains paused at `0d8d19f` on `codex/android-a4-touch-settings`, with no
source changes, build, or device installation in this release. Native private
room transport, safe in-process game switching, and complete production-online
race verification remain separate work. Navigating to Friends is not evidence
of a completed online race.

This evidence note follows the release source and does not alter the source
identity or provenance embedded in the published IPA.
