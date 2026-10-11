# Release handoff prompt — KartPad 0.5.1 (Android + iPhone/iPad), 25 September 2026

Copy everything below the line into the release bot.

---

You are finishing tonight's KartPad 0.5.1 release for Android and iPhone/iPad.
Prepare everything up to publication, verify it, then stop and ask the owner for
an explicit "publish" before creating the GitHub release. Work carefully; this is
a public release to players who keep saves in the app.

## Where things are

- Repository: https://github.com/chrissotraidis/kartpad
- Working checkout (shared, keep it): `/Users/chrissotraidis/.codex/worktrees/kartpad-stabilization-20260918`,
  branch `codex/upstream-all-platforms-20260922` (draft PR #317).
- The owner's uncommitted edit `docs/artifacts/2026-09-22/clean-rc2.md` must be preserved.
  Never reset, stash-drop, checkout or delete it. Ask the owner whether to commit it
  or build from a clean worktree under `~/.codex/worktrees`.
- Root HEAD is the commit that added this prompt. Everything after `397a3af` (PR #317's
  pushed head) is local only; list it with `git log --oneline 397a3af..HEAD`.
  `0e0c23b` pins the Android runtime to `c1c9cff`.
- Android runtime submodule `vendor/runtimes/android` (repo chrissotraidis/wiicompiled):
  `c1c9cff` sits on local branches `codex/android-review-20260925` and
  `codex/android-retained-208-dma`; **it is not on any remote yet.**
- iOS runtime pin `36e5f73` (unchanged). Dawn Android `b0fd045` / package `c6b4efde…`.
- Read first: `docs/RELEASE-CHECKLIST.md`, `docs/RELEASING_ANDROID.md`, `docs/BUILDING.md`,
  `docs/SUPPORT-AGENTS.md`, and the dated records
  `docs/artifacts/2026-09-25/android-second-review.md` and `android-code219-ipad72.md`.

## Last public versions

- Android: v0.5.0, version code 135, APK signer
  `c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`.
- iPhone/iPad and Mac: v0.5.1-experimental.1, build 60 (prerelease). v0.5.0/build59 is "Latest".

## What 0.5.1 contains

Android, code135 → runtime `c1c9cff` (146 runtime commits):
- Stability: clean fatal-exit shutdown, rejection of incompatible game code (REL hash
  check), upstream WiiCompiled 8346376 fixes (Item Rain crash, stranded sleep timers,
  z-fighting, controller input leaking through the exit prompt, empty save treated as
  missing), safer console-identity/NAND initialization, socket send-error fix.
- Performance: native-rate FIFO presentation, Android Performance Hint (API 33+),
  course-scoped shader replay, faster DVD reads/Yaz0/file handles, cheaper GX
  display-list processing, persisted Dawn pipeline cache, display-rate hint.
- New in this review: #321 fix (no Vulkan debug labels in release command buffers),
  pipeline workers on physical Android 9/10 (#320), pipeline id in stall logging.
- Label: "Touch auto-accelerate" (controllers still have no auto-accelerate, #319).

iPhone/iPad, build 60 → iOS runtime `36e5f73` (128 commits): the same shared performance
and stability work ported to iOS, the same upstream merge, opt-in native-rate FIFO (off
by default). The three Android-only fixes do not apply.

Do **not** add the deferred network-receive change, controller auto-accelerate, or any
other new code tonight.

## Gate 0 — owner play sessions (stop if missing or failed)

Ask the owner for these results before building release artifacts:
1. Pixel 9 Pro XL on private code219: one offline race and one Retro online race.
2. iPad Pro on private build 72: one Original race and one Retro race, passing through
   character select (open report #322 freezes there on build 60).
Record pass/fail per item. Any crash, freeze, lost save or broken login stops the release.

## Gate 1 — publish the source

1. Push the Android runtime commit: from `vendor/runtimes/android`, push
   `codex/android-review-20260925` (head `c1c9cff`) to origin, and confirm
   `git branch -r --contains c1c9cff` shows it.
2. Push the root branch so HEAD (or your final release commit) is on origin.
   Merging PR #317 to main is the owner's call; ask.
3. Run `python3 -B scripts/test-android-debug-labels.py`,
   `python3 -B scripts/test-android-pipeline-workers.py`,
   `python3 -B scripts/test-shared-runtime-parity.py` and the checks named in the checklist.

## Gate 2 — Android release package

Follow `docs/RELEASING_ANDROID.md` exactly.
- Version name `0.5.1`, version code **220** (above every private code, including 219).
- Build the AAB from the pushed source with fresh runtime paths:
  `KARTPAD_DISCIO_JNI_ROOT=/Users/chrissotraidis/GitHub/kartpad/build/dolphin-android-discio-jni`
  (the same disc-reader build as 218/219, `694b9e41…`),
  `KARTPAD_ANDROID_PACKAGE_FORMAT=aab`, `KARTPAD_ANDROID_VERSION_NAME=0.5.1`,
  `KARTPAD_ANDROID_VERSION_CODE=220`, translation
  `private/android-gx-direct-20260925/translation` (the translation 219 was built and tested with;
  record its fingerprint and review it against `RIGHTS_AND_LICENSES.md`).
- Derive the APK with `scripts/derive-android-release-apk.sh` and the **existing** release
  keystore (`KARTPAD_ANDROID_KEYSTORE`, `KARTPAD_ANDROID_KEY_ALIAS`,
  `KARTPAD_ANDROID_PASSWORD_FILE`). Get the location from the owner. If the key is
  unavailable, stop: never create or rotate a key, and never publish the debug-signed
  `work/kartpad-code219-review.apk` (signer `61dfb514…`; players could only install it by
  uninstalling, which deletes saves).
- Verify the certificate is `c1dbe0a0…`, repeat derivation for identical bytes, and audit
  with `KARTPAD_ANDROID_EXPECTED_VERSION_NAME=0.5.1`, `KARTPAD_ANDROID_EXPECTED_VERSION_CODE=220`,
  `KARTPAD_ANDROID_REQUIRE_RELEASE=1`. Confirm `libmain.so` lacks the string
  `Aurora: Dear Imgui` and contains `persistent=%d ref=0x`.
- **Update-path test on a disposable emulator:** install public v0.5.0 (downloaded
  anonymously), add game data, then `adb install -r` the new APK and confirm the game is
  still "Ready to play" and reaches gameplay. Use a fresh or disposable AVD; do not touch
  the owner's phone, which carries the debug signer.
- Package notices/provenance with `scripts/package-android-release-notices.py`
  (`--certificate-sha256 c1dbe0a0…`), plus the source archive and `SHA256SUMS`.

## Gate 3 — iPhone/iPad and Mac packages

- Build 72 was compiled from dirty source (`source_dirty=true`, `30596c1`), so it must not be
  published. Rebuild from the pushed commit as **0.5.1 build 73** with
  `KARTPAD_DIAGNOSTIC_CANDIDATE=NO`, run `scripts/audit-ios-game-app.sh`, then package and
  audit with `scripts/package-public-unsigned-ipa.py` / `scripts/audit-public-unsigned-ipa.py`.
  Confirm `KartPadDiagnosticsCandidate=NO` in the final Info.plist and a matching dSYM UUID.
- Mac: include only if rebuilt from the same commit and audited
  (`scripts/package-public-macos.py`, `scripts/audit-macos-package.sh`); otherwise leave the
  Mac download at build 60 and say so in the notes.
- Optional, owner's choice: install build 73 in place on the iPad Pro
  (UDID `00008112-001D485114DBC01E`) using the backup/readback method in
  `work/ios72-install-20260925/` (`ipad_container.py` via `uvx --from pymobiledevice3`).
  Another task (AgePad) sometimes runs `devicectl` sessions on this iPad; wait until
  none is running and never interrupt it.

## Gate 4 — owner approval, then publish

Show the owner: version/build numbers, source commits, every asset's SHA-256 and size,
the APK signer, Gate 0 results and the release notes. Publish only after an explicit yes.
- Release notes: `docs/releases/v0.5.1.md`. List changes plainly, installation steps
  (Android updates in place over 0.5.0; do not uninstall), and known limits:
  Adreno character geometry (#104/#193/#211/#316/#308) unresolved; controller
  auto-accelerate (#319) not implemented; low-end phone performance still limited;
  online can freeze for up to about a second while waiting on the server; the #321 and
  #320 fixes are unverified on those phones.
- Tag the exact audited commit. Decide with the owner whether 0.5.1 is "Latest" or a
  prerelease; do not replace Apple downloads with an Android-only release.
- Afterwards: download every asset anonymously, compare hashes and bytes, re-audit the
  APK signature and IPA mode, then update README downloads, STATUS and the maintenance
  board together.

## After publication (only then)

Reply once, briefly, on #321 (asks whether the game now launches on the ROG Phone 7S)
and #320 (same first course, FPS and one diagnostic export) following
`docs/SUPPORT-AGENTS.md`. Do not ask other reporters for retests. Never post game data,
logs from the owner's devices or signing details.

## Never

Publish a debug-signed APK; create or rotate a signing key; uninstall or clear data on any
device; discard `clean-rc2.md`; commit private logs, saves, game images or translated source;
push to Google Play or any store; add untested code tonight.

## Report back

Final commits (root and runtime), tag, release URL, each asset's name/bytes/SHA-256,
APK certificate, iOS build number/UUID, audit and emulator update-path results, Gate 0
results, anything skipped, and every remaining gate stated plainly.
