# 0.5.1 release confidence

## Decision

Post-RC1 source correction: [socket send errors](socket-send-error.md) now survive
diagnostic logging across all four runtimes. RC1 does not contain that correction.
[Clean RC2](clean-rc2.md) now contains it and passes compilation/package/source
audits. Exact-package emulator upgrade/title/attract observation and isolated Mac
identity-migration/startup checks also pass; online acceptance remains unresolved.

Hold formal publication until the observed iPad Retro WFC login failure is
reproduced with diagnostics and either corrected or shown not to be a regression.
Do not require every enhancement or a universal Android performance improvement.
The second Android profile alone is not proof of an upgrade regression: the owner
reports that the first profile reaches Retro WFC. Do not switch the shared console
identity automatically and risk that working profile.

## Verified

- All four maintained runtimes preserve valid legacy console identities when
  initializing the new managed NAND settings. Existing settings remain unchanged.
- All four NAND settings suites pass with ASan/UBSan.
- Android identity recovery, save/profile isolation and interrupted-transaction
  host suites pass. Recovery is explicit and was not invoked on the owner device.
- Android code173 passed the APK audit and installed in place. Owner reports
  profile 1 reaches Retro WFC; profile 2 still rejects its registered serial.
- iPad build62 passed the iOS package audit and installed with matching signing
  entitlements. All 35 backed-up identity/save/preference files matched readback.
- iOS receive semantics tests pass, including delayed loopback response. Opt-in
  TCP trace tests verify payload exclusion, disabled-by-default behavior and EOF.
- macOS build62 rebuilt with the migration correction and passed its package audit.
  The exact packaged executable initialized settings from a synthetic old serial,
  kept the legacy file unchanged, remained alive for 20 seconds and exited cleanly.
  This is offline startup/upgrade evidence, not a race or online acceptance test.

## Remaining evidence

1. Retry iPad profile 2 with the installed diagnostic build. The first collected
   build62 session contains no WFC attempt. An error code alone does not establish
   server failure, packet loss, or a client defect.
2. Verify Original and Retro startup on the final candidates and confirm usable
   iPad online login after the diagnosed correction. Physical iPhone acceptance
   has not been established separately from the shared iOS/iPadOS binary.
3. Reconcile and merge the reviewed source PRs and finalize release metadata
   before promotion. Clean local RC2 packages, public Android signing and source
   archive validation are now complete; see [RC2 evidence](clean-rc2.md) and
   [exact hashes](clean-rc2-packages.json). Earlier build61/code171 assets are
   historical and must not be published as identity-safe upgrades. Later test
   and documentation commits do not change the recorded compilation revision.

Private evidence: work/mobile-network-repair-20260922. Do not publish its backups,
logs or device identifiers. Current candidates are local and unreleased.

## Device-free follow-up

See [device-free review](device-free-release-review.md) for the fresh issue review,
Classic driver contract tests, and corrected public-signing Android candidate.
The private APK is not a public upgrade asset. The new public-signer APK passed
an isolated emulator update from public135 with unchanged byte sentinels and
app UID; this does not replace physical gameplay or iPad WFC acceptance.
The final code174 APK also passed an in-place update from public-signer173 and
an offline emulator title/attract-mode idle observation. The new host event-service
regression passed with ASan/UBSan. Neither result closes the Moto G85 freeze or
physical GPU geometry reports.
