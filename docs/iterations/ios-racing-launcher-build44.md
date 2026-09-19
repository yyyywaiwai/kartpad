# iOS racing launcher preview — build 44

The native launcher now uses the approved red racing K and stacked game rows. Dark mode is enabled on first use; the visible switch remembers the user's selection. The home-screen icon and transparent in-app mark are 1024px assets generated above their final resolution, then downsampled.

The existing import, setup, play, resume, and next-launch actions remain connected to the original runtime host. Help still contains the installation and troubleshooting guides. The new persistent On launch chooser supports Ask every time, Mario Kart Wii, and Retro Rewind. A one-shot next-launch selection has priority. Returning from a running game always opens the paused chooser, irrespective of the preferred game.

## Private hardware preview

Installed version 0.4.22, build 44, on the attached iPhone 14 running iOS 26.6.2. Signed in-place installation and launch succeeded. The launcher was visually checked through the wired mirror. All 29 protected files read back with identical hashes: NAND, backups, configuration, identity, preferences, and Retro Rewind save files.

This is a private UIKit relink using the cached build43 anonymous-memory runtime and translation, plus the launcher source in this branch. It is **not** a fresh full-runtime build from latest main or a public release. The local composition receipt records source/object/asset hashes and cached provenance. No Android APK was installed or performance conclusion changed.

## Validation

- Compiled the real Objective-C++ runtime host and linked the full device app.
- UIKit simulator checks: default dark mode; light/dark persistence across controller recreation; original/Retro callbacks; resume/next-launch labels; preference display.
- Native simulator interactions: theme toggle, persisted preference after relaunch, Help opening/closing, and Resume callback.
- Corrected a launch-preference wrapping defect after visual comparison.
- Physical iPhone: installed version, live launcher, both imported games ready, preserved data.

Game feel, physical touch acceptance, and the full return/resume cycle in this new build are not claimed as tested. Android launcher theme parity is separate work.
