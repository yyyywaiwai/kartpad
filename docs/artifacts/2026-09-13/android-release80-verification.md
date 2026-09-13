# Android 0.4.17 / code 80 published verification

Published as [v0.4.17-android.1](https://github.com/chrissotraidis/kartpad/releases/tag/v0.4.17-android.1), a normal public release. Tag `1fe6364ac5ba95b9bbcd7196218da865552ff0f2` contains release metadata; the clean compiled application revision remains `615225b3f0e0507ca76d4c715c921d0a1caa9956`. The platform download table distinguishes this APK from the already published Apple build 39 packages.

All four public assets were downloaded without authentication and matched their audited local bytes and GitHub digests:

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| KartPad-v0.4.17-android.1-arm64.apk | 110224793 | `13b68c84a0a52960007fda5e3d33eafad1c1d9d567d7544586ced2ce23c1e833` |
| KartPad-2026-09-13-android-source.tar.gz | 363676559 | `57be7d71dc5c6683c4000ca858030b5ab5a0b2c60f718a58a1b921a965627c5e` |
| KartPad-v0.4.17-android.1-notices.zip | 93158 | `32bcc40c5f0a99a8726cacc01917596d674d64b6e5194ab67db293f62366b851` |
| SHA256SUMS | 313 | `06fdf9e1c8a761055ccb8ba5a92b250a188675550934f4851e45e43ab7c2bc94` |

The community certificate remains `c1dbe0a0d72d830a5779476b346a750d0a37515adef992cad2f3863058f7f2f2`. Package and bundle audits passed; source and notices reproduced byte for byte. The APK is non-debuggable. All 155 ZIP payload entries match the separately signed release test twin.

The owner accepted Retro single-player racing and touch on code 78. Code 79 passed physical Large FPS display, restart persistence and D-pad Hide/Show checks. Its touch-layout settings were restored, retaining only the new `fps_size=2` preference; save/game/license/Mii/identity file hashes were unchanged during the UI trial. Code 80's test twin passed emulator selector checks only. The phone disconnected before its physical installation; the owner explicitly authorized publication after that limitation was disclosed. The phone remains on code 79 with its existing signing identity and licenses.

The release delivers FPS sizing, the responsive touch editor and shoulder-to-D-pad remapping. It does not establish fixes for WFC latency, affected-controller handoff, Adreno corruption, sustained performance or the new translator report. Issue replies #184, #238 and #235 link the verified download; #248 and #250 received focused technical follow-up. The issue count at this pass is 47, after two new reports arrived.

Draft [PR #252](https://github.com/chrissotraidis/kartpad/pull/252) is separate: fresh translator tests and exact-profile generation pass, but 41.3% Retro generated-code growth blocks adopting the continuation backport. [PR #251](https://github.com/chrissotraidis/kartpad/pull/251) makes local investigation/preparation selectable without conflating it with external acceptance. Neither that queue correction nor publication resumes the paused maintenance heartbeat.
