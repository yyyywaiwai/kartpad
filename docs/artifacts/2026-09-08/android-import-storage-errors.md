# Android disc-import storage failure

8 September 2026. Discovered during fresh-install acceptance for issue #105's
save-transfer candidate; not a reporter diagnosis of the graphics issues.

## Reproduction and cause

On a fresh API 36 ARM64 emulator with its default 6 GiB data partition, the
release-signed code-22 candidate exhausted space while importing the supported
local WBFS. Java logged `ENOSPC` writing the staged runtime configuration, but
the UI showed only “The selected game data could not be imported.” Failed
staging was removed; the selected source remained available.

Source inspection found a second related defect: Dolphin's `ExportDirectory`
returns void and continues after individual `ExportFile` failures. Counting its
progress callbacks therefore could treat a partially copied tree as successful.
The existing validation checks critical files, not every game asset.

## Correction

- Inspect the disc's total file size and entry count, then check available
  destination space before extraction. Reserve room for system files,
  allocation overhead and atomic configuration. Report the additional MiB
  needed instead of beginning an import that cannot fit.
- Export directories through a bounded traversal that checks every
  `DiscIO::ExportFile` return value and stops on failure. Reject path components
  that escape their destination. Java continues to remove only this import's
  staging directory when extraction fails.
- Translate a later Java ENOSPC error into an actionable storage message, so a
  concurrent loss of free space is not hidden behind the generic error.

## Validation so far

Pinned Android DiscIO JNI rebuild and full release AAB/APK audits pass. Updating
the same fresh emulator to the corrected, release-signed code-22 candidate and
selecting the same WBFS now fails before extraction with “Free at least 982 MiB
more and try again.” No reinstall, source deletion or device-storage clearing
was used. On a second disposable emulator with a 12 GiB data partition, the same
corrected APK imports the complete supported WBFS successfully. A truncated
copy is rejected without replacing the installed data. For the mid-extraction
failure case, a temporary 2.5 GiB filler was allocated only after system-file
extraction began, exhausting space during asset copying. The importer stopped
with its extraction-failure message and removed the new staging tree. The
entire prior GameData tar digest remained identical before and after both
failed replacements. The injected filler was removed immediately afterward.
All 140 Python tests and the repository safety audit pass.

Release packaging distinguishes the JNI build output from the stripped APK
library. Applying the pinned NDK's `llvm-strip --strip-unneeded` to the tested
JNI output reproduces the packaged library SHA-256
`0e5bd27501b1aee71db63364f0673682e0cca3c0234d560d4c54ac87e01c0d0b`.
The notices packager checks that APK hash. The merged-source APK is byte-identical
to the import-fixed emulator candidate and to a second signed derivation:
`ce42a501c9e14d616e096511fc17329541fbc6e31dc2ab9e6d0f9066094b0c56`.
