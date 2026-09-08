# KartPad support

Use the [platform downloads](../README.md#platform-overview) and include the
exact app version/build in a report. Update over the existing installation;
do not uninstall or clear storage to troubleshoot. Follow the platform's
backup instructions before changing saves or signing identities.

## Android save transfer

KartPad stores saves in Android's **internal app-private storage**, so its save
folder is not exposed through a normal file manager under `Android/data`.
Root access is not needed for the built-in Original save transfer:

1. Copy the PC's raw Mario Kart Wii `rksys.dat` to Downloads on the phone.
   Use a copy and keep the PC original. A Wii `data.bin`, ghost `.rkg`, save
   state, or whole NAND archive is not the supported input.
2. Open Original Mario Kart Wii, then **••• → Game Data & Saves → Manage
   Saves…**. If you have existing progress, use **Export Save Backup…** first.
   Export is enabled once an initialized, valid save exists.
3. Choose **Restore Save Backup…** and select the copied `rksys.dat`.
   KartPad validates its size, header, and checksum before staging it.
4. Choose **Restart Now** to apply it before gameplay starts. KartPad also
   retains a backup of the previous save. Check the expected licenses and
   progress offline before continuing.

**Current limit:** Android `0.4.10-android.1` Manage Saves always targets the
Original PAL save, even when opened while playing Retro Rewind. It does not
export or restore Retro Rewind's separate save files. Do not use it expecting
a Retro Rewind migration. The confirmed PC WiiCompiled → Android KartPad
Retro Rewind/PAL transfer is tracked in
[#105](https://github.com/chrissotraidis/kartpad/issues/105). Explicit profile
selection and separate-save backup/restore still need implementation and tests;
there is no supported Retro Rewind transfer route in the current APK.

The importer accepts a raw 2,867,200-byte `RKSD0006` save with a valid core
checksum. That validation does not prove cross-region, cross-mod, or online
identity compatibility. A save transfer does not transfer the Mii database or
console identity. If the source is Dolphin, another WiiCompiled build, or
Retro Rewind, name it and the game region when asking for migration help.
Never post the save or NAND publicly.

On Mac, **Data → Show KartPad Data** opens KartPad's support directory. Quit
the game before backing it up. On Apple TV, use
[`backup-tvos-state.sh`](../scripts/backup-tvos-state.sh) as described in the
[testing guide](TVOS-TESTING.md); its cache storage can be purged by tvOS.
Android's save-picker instructions do not imply the same UI exists on Apple.

## Display and performance

**Original 4:3** and **Widescreen 16:9 (Experimental)** fit the selected aspect
inside the display; black bars can be expected. **Fill Screen (Experimental)**
uses the actual surface aspect and dynamic game projection. It is intended to
expand the view, but some scenes or HUD elements may still distort. It is not
a guarantee that every screen renders correctly at a phone's wider aspect.

For a stretched image, compare 16:9 and Fill Screen on the same track and
camera view. Include both screenshots, app/OS version, and whether it affects
the 3D world, menus/HUD, or both. Use 4:3 or 16:9 as a temporary workaround.
See [#101](https://github.com/chrissotraidis/kartpad/issues/101).

For Android geometry/texture corruption, try a repeat of the same race at
**1x Native / Original 4:3** and report whether the defect persists. Include
phone/OS details, Original versus Retro Rewind, track and character/vehicle,
and startup renderer information plus warnings from the logs below. On a
foldable, include the screen in use and whether folding/resizing preceded the
failure. Similar GPU names do not establish identical drivers or a root cause.
See [#102](https://github.com/chrissotraidis/kartpad/issues/102) and
[#104](https://github.com/chrissotraidis/kartpad/issues/104).

For frame drops, enable KartPad's **Show FPS Counter** and compare a cold and
repeat run of the same course. Record resolution, aspect, game/battery mode,
time since launch, charging state, and whether audio also stutters. Samsung
Game Booster/Game Booster+ battery-saver settings affected the report in
[#103](https://github.com/chrissotraidis/kartpad/issues/103). Compare settings
one at a time; higher resolution is not an established performance fix.
Low GPU utilization alone cannot distinguish CPU, shader compilation,
presentation, or power/thermal limits.

AirPlay mirroring and a dedicated external-display game view are different
paths. Neither is currently accepted as supported iPhone/iPad output.
For black video with working audio, report the phone/tablet and OS, TV/monitor,
cable/adapter or AirPlay receiver, whether the device itself keeps rendering,
and whether connecting before versus after game launch changes the result.
See [#100](https://github.com/chrissotraidis/kartpad/issues/100).

## Collect a useful report

**Android:** **••• → Report a Problem… → Share Report…** produces a short
version/device/profile summary and your answers. It does **not** include the
runtime/renderer log history. For that history, reproduce once, fully close
KartPad from Recents, reopen to the Original/Retro Rewind chooser, and choose
**Export Private Diagnostics… → Save Locally…**. Open the ZIP locally; review
its `README.txt` and relevant `Logs/` text. Share only the startup renderer
lines, warnings/errors and a short interval around the failure. For performance,
include matching `KartPadPerf`/CPU/GPU and `android-health.log` intervals where
available; these use elapsed time since boot. Unavailable metrics are not zero.

The private ZIP can contain local paths and personal details. Do not upload it
raw. Remove usernames, private paths, IP/MAC addresses, console/account IDs,
friend codes, tokens, and other personal data from excerpts. Do not clear logs
or app storage before collecting them. No USB debugging or root is needed.

**iPhone/iPad:** **••• → Report a Problem… → Share Report…** creates the bounded
technical report. Review it and attach it to the existing issue with a
screenshot if relevant. **Report on GitHub** prefills the form but does not
attach the report file; its report ID alone is not a log upload.

**Mac:** **Help → Save Diagnostics Report…** creates a bounded report with
settings and current/previous session tails. Review it before attaching.

**Apple TV:** follow [`collect-tvos-diagnostics.sh`](../scripts/collect-tvos-diagnostics.sh)
and the [testing guide](TVOS-TESTING.md), then share reviewed, relevant excerpts.

For any platform, a report should say what happened, what you expected, how
to repeat it, and the exact version and hardware. Game images, extracted game
files, saves, complete app containers/NAND, signing material, and identities
do not belong in a public issue.
