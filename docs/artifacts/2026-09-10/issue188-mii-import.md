# Issue 188: exported Mii header rejected as invalid

Base: `fd9b3fd` (`origin/main`). Source fix only; no release or physical acceptance.

[Issue 188](https://github.com/chrissotraidis/kartpad/issues/188) reports Android
0.4.14 preview 1 on AYN Thor / Android 13 rejecting 74-byte exports from both
rfl_mii_extractor and WheelWizard. The reporter subsequently supplied the
[marked-as-invalid error](https://github.com/chrissotraidis/kartpad/issues/188#issuecomment-5620334831).

## Cause and correction

`ValidateMii` interpreted header mask `0x8000` as an invalid flag. It is
`RFLiCharData::padding0`. The public RFL reconstruction defines that field as
padding and omits it when converting raw data into the character info used for
validation:

- [RFL field layout](https://github.com/koopthekoopa/RFL/blob/2a5a571f30100c70e855f882e55a53136bc101b3/include/internal/RFLi_Types.h)
- [Raw-to-character conversion](https://github.com/koopthekoopa/RFL/blob/2a5a571f30100c70e855f882e55a53136bc101b3/src/RFL_Database.c)
- [Character validation](https://github.com/koopthekoopa/RFL/blob/2a5a571f30100c70e855f882e55a53136bc101b3/src/RFL_DataUtility.c)

[rfl_mii_extractor](https://github.com/SuperFromND/rfl_mii_extractor/blob/3aa73b7a592ed09e6ff2aa6a643ece6b586b0ce9/src/main.go)
copies each 74-byte record directly from the database starting at offset 4;
it preserves this bit. No reporter Mii/database was obtained or used.

Remove only the false invalid-flag rejection in the shared Apple/Android importer.
Keep size, empty-file, metadata, name, creation-ID, body-size and database-CRC
checks. Imported bytes remain unchanged. No save or controller behavior changes.
The CMake Mii test target now keeps assertions enabled in release configurations,
matching the existing Apple identity test target.

## Reproduction and verification

- New synthetic export fixture fails against the original validator.
- The same Kotlin harness with the baseline production JNI library throws
  `IllegalArgumentException: The selected Mii is marked invalid.` With the
  corrected JNI library it imports, lists, stages and applies the record, retaining
  a byte-identical backup of the original database.
- C++ tests cover both padding values and both gender values, unchanged imported
  bytes and existing slots, CRC, duplicate rejection, and malformed inputs.
- Three focused CTest targets pass in `RelWithDebInfo`: Mii database, seed database,
  and Apple player identity. The database test also passes AddressSanitizer and
  UndefinedBehaviorSanitizer with warnings treated as errors.
- `scripts/test-android-identity-host.sh` passes, including the new JNI import
  regression plus existing rating, save/profile isolation, identity transaction
  recovery and backup checks. This is host JVM/JNI testing, not Android UI testing.
- `test_experimental_mii_wiimote_contract.py`: four checks pass.

Reproduce the C++ portion with:

```sh
cmake -S . -B build/issue188/cmake -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build/issue188/cmake --target kartpad_mii_database_tests kartpad_seed_mii_database_tests kartpad_player_identity_tests
ctest --test-dir build/issue188/cmake --output-on-failure -R 'kartpad_mii_database_tests|kartpad.mii.'
```

## Remaining acceptance

Review and package this source before asking the reporter to retry. On the
affected AYN Thor, import the same export, fully close/reopen KartPad, and verify
the name and appearance in the game's Mii picker. Existing Miis/licenses/progress
must remain intact. The synthetic reproduction establishes the false rejection;
the private export may still expose a separate validation or rendering problem.
Keep #188 open until that result is known. No private Mii upload is needed.

## Independent review and source integration, 11 September Japan time

PR190 exact `cb4d765` cleared independent Medium source review and merged as
`d145819`. Reviewer confirmed pinned RFL padding semantics and independently
passed three RelWithDebInfo CTests, ASan/UBSan strict-warning Mii tests and the
Android host JNI/identity/save/rating suites. No reporter export or device was
tested. Shared importer source is corrected; per-platform packaging and
AYN Thor UI/appearance/restart acceptance remain. Keep issue188 open.
