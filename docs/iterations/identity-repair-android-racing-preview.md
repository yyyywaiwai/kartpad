# License identity repair and Android racing launcher preview

## Confirmed failure

The iPhone rename changed the selected Original license name and checksum correctly. Its linked Mii was absent from the device Mii database, as was the Retro license link. These missing links predated the launcher update. The game displays the linked Mii identity; changing only the saved license name did not resolve the reported Player display. Original and Retro use separate saves, and the Original rename left Retro unchanged.

## Change

Both mobile menus flag missing Mii links and offer Choose Mii. The user selects an existing Mii and schedules the repair for the next full app launch. The operation revalidates both identities at application time and preserves the latest progress, account data, other licenses, other profiles, and the Mii database. A save backup precedes publication. Ordinary rename remains available for valid links. Identity guidance is shorter.

Android now uses the shared HD racing mark, matching dark-by-default launcher, persistent light/dark toggle, preferred game selector, Help, and existing import/setup/play paths. Physical testing found that setting both message and list items on Android AlertDialog hid the identity actions; the top-level identity menu now displays its list directly, with detail under About Player Identity.

## Validation and private hardware artifacts

- Apple identity staging, pending preview, backup and preservation host tests passed.
- Android identity JNI/storage tests passed, including missing-link repair, stale selected Mii rejection, latest progress, profile isolation, and transaction recovery.
- Six focused menu/save source contract tests passed. The separate runtime Nunchuk source test was not run successfully because this worktree lacks its vendor runtime fixture.
- iPhone 14: private build45 installed in place and launched. Wired visual check confirms approved dark launcher. All 23 protected NAND and Retro save files read back byte-identical to the pre-install identity investigation snapshot.
- Pixel 9 Pro XL: private version 0.4.22-racing-preview build103 installed in place. Matching existing signer; package audit passed. On-device dark/light persistence, Help, Retro launch, identity actions, license listing, and rename editor checked. No license edits submitted. Existing imported games and licenses remain available; release sandbox prevents fresh full private data readback through adb.
- Android APK SHA-256: b5f2bc089f1cf17543a5b50ee0f5ec7413195eb1eb68efcb786aa48d8987eb69.

These are private compositions: iPhone reuses the cached build43 runtime with newly compiled UI and identity manager; Android retains the previous private TLS/graphics-memory experiment runtime and adds this UI/identity work. Neither is a clean public release from current main. No new performance or cross-device stability claim follows from these installs.

## Remaining acceptance

On iPhone, choose the intended game profile and license under Game Data & Saves → Player Identity → Rename or Delete Licenses → Choose Mii. Select the desired existing Mii, save for next launch, fully close the app from the app switcher, then reopen. Actual in-game name confirmation after that selection is still pending. The operation was tested on synthetic files; device identities were not silently reassigned.
