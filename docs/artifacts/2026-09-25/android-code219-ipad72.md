# Android code219 and iPad build 72 — 25 September 2026

## Android code219 (`0.5.1-review.1`)

Built from root `0e0c23b` with Android runtime `c1c9cff` (218's runtime
`27074c2` plus the three patches in [the second review](android-second-review.md)),
the same private translation as 218, Dawn `c6b4efde…` and the same disc-reader
library as 218 (`694b9e41…`, from the primary checkout's
`build/dolphin-android-discio-jni`).

- APK `work/kartpad-code219-review.apk`, SHA-256
  `a2018265238f982f5d62756c6b2cdaddb432923acf423be97cac3abcddf0724d`; release
  audit passed for version code 219. Signer
  `61dfb51411efe50b2e7fb8d280fcfbba766792c275d1024013940760caa3afaf`, identical to
  the Pixel's installed 218, so an in-place `adb install -r` is possible.
- Packaged `libmain.so` BuildID `dba28068…`: the overlay debug-group label is
  absent, and the pipeline-wait `ref=` field and the `ro.hardware` check are present.
- API 36 emulator: installed in place over 218 (first-install date unchanged);
  the chooser still showed Mario Kart Wii ready; Original's opening ran with the
  FPS overlay drawing, about 50 FPS and 8.4 ms game CPU per frame on the software
  renderer; no crash, fatal or restart in the log. No race was driven.
- Not run: the API 29 emulator (no image installed; the gate's emulator cases are
  covered by `scripts/test-android-pipeline-workers.py`).
- Pixel 9 Pro XL (`47181FDAS005KL`), 13:39 JST: the installed APK pulled first
  matched archived 218 (`601f6e57…`) and had the same signer. `adb install -r`
  succeeded with no uninstall, data clear or downgrade. The APK pulled afterward
  matches code219 exactly; the original first-install date (6 September), data
  directory and app user ID are unchanged, and the launcher shows Mario Kart Wii
  and Retro Rewind "Ready to play". The release app denies `run-as`, so saves,
  licence and identity were not byte-verified. No game was started on the phone.
  Receipts: `work/android-pixel-code219-20260925/`.

## iPad Pro build 72

Build 72 (unchanged runtime `36e5f73`; executable/dSYM UUID
`FCE926BB-3193-3F1A-89E3-F31F09BBEA23`) was signed with the same Apple Development
certificate, team `VKDH2T9UTF`, entitlements and profile as build 70, and passed
strict verification with diagnostics mode `NO`. Before installation, 34 user-data
files (NAND, Retro saves, config, console identity, preferences, save and Mii
backups) were copied off the iPad, and the game image was hashed in place:
`fc035e60610842da6860d23d4a30c1f1c0f019d492469deb8a2ac25ef5822331`, matching the
24 September full backup. `devicectl` installed build 72 over 70 in place; the
device reports `0.5.1` build 72. Readback: 34/34 files identical, none missing or
extra, and the game image hash unchanged. Build 72 was not launched or played.
Private receipts are under `work/ios72-install-20260925/`.

An AgePad task was running device sessions on the same iPad; the KartPad
copies were paused while it held the device, and it was not interrupted.
