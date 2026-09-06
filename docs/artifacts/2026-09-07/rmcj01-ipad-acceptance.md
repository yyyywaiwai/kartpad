# RMCJ01 iPad acceptance (2026-09-07)

## 最新判定（03:49 JST read-only refresh）

- **確認済み（実機 UI）**: root 所有 UI で cold chooser → 正規 Retro Rewind ZIP installer → RR title/menu/license、通常 Retro WFC の同意/Permit、MOTD と `Server Status: ONLINE`、Mac friend code の登録完了ダイアログ (`root-ipad-friend-register-result.png`) まで確認済み。Friend Roster は `1/1` 表示であり、`root-ipad-find-friend.png`（`?` アイコン）は相互登録待ちの途中状態。後続の `root-ipad-roster-mutual.png` では Mii カードと `I'm on Retro WFC!` が表示されるが、相互登録の最終判定は root の最新 UI 状態を基準に更新する。
- **read-only readback（03:29--03:30）**: `devicectl device copy from` が成功し、端末 Documents の `rmcj01-live-trace.csv` を `private/rmcj01/mobile/ipad-live-trace-20260907.csv` に保存。サイズ 187 bytes、CSV header 1 行・データ行 0（RR レース完走の trace ではない）、SHA-256 `147a2702944bcf6a630d021b1611aa22e310dfeb7b9943e564d6fab461e1bcb7`。
- **Original cold save readback**: `Library/Application Support/KartPad/NAND/title/00010004/524d434a/data/rksys.dat` を cold 後に再取得。サイズ 2,867,200 bytes、`RKSD0006`、保存 CRC `0xe4a9a2bf` (decimal `3836322495`) と先頭 `0x27ffc` bytes の独立計算が一致、SHA-256 `ca7c0072c496225b2c55d242912f9c3e6da3375c8776e7a52c2406d0f5309bec`。cold 前スナップショットと byte-identical（CRC/SHA/size 一致）。
- **RR redirected save readback**: ライブログ記載の redirect 配下 `Library/Application Support/KartPad/RetroRewind/riivolution/save/RetroWFC/RMCJ/rksys.dat` を端末から read-only 取得。`RMCJ/rksys.dat` (2,867,200 bytes) と `banner.bin` (29,344 bytes) の存在を `device info files` で確認し、`rksys.dat` は `RKSD0006`、保存/計算 CRC `0x4003406f` (decimal `1073954927`) 一致、SHA-256 `ea0b3e78736bbbafeff7885cfd6c65ec9bed2439e3cdeaf9c72805bee71c1e36`。Original NAND save とは別内容（byte-identical ではない）。
- **未確認の境界**: Original Luigi スタッフ ghost replay の 3 周完走/本人記録保存、quit 後のコースセレクト帰還、RR 代表 replay 完走、Mac private room 参加と online レース。上記 readback は保存形式と redirect 先の存在/整合性を示すが、これらの UI 完走を代替しない。
- **signed-local-network 更新後**: root の `signed-local-network` IPA 更新に伴う `devicectl terminate-existing` → cold 起動の `signal 9` は計画済みプロセス置換であり、クラッシュではない。新 live log の実行コンテナは `[private container identifier omitted]`、旧 trace 環境変数は `[private container identifier omitted]` を指し、`state-trace unable to open` が記録されている。新 trace のデータ行は取得できず、RR 完走 trace の証拠はない。

## 対象と境界

- 対象端末: iPad Air (M2), UDID `[private device identifier omitted]`、iPadOS 27.0、物理 iPad。
- アプリ: `dev.kartpad.rmcj01.ios`、日本版 Original + Retro Rewind 6.12.7 dual。Original 側の実行時設定は `widescreen=false`、`window=1180x820`、`native=2360x1640`、`presentAspect=4:3`、`dvd_root=GameData`。RR 側の profile/root は後続時刻節に記録する。
- Original の bounded 実行ログ: `private/rmcj01/mobile/agent-device-auto/sessions/rmcj-ipad/app.log`（**02:51:51 JST 時点の履歴スナップショット** 1,689 行 / 298,596 bytes）。RR 実行は後続の `private/rmcj01/mobile/ipad-traced-live.log` に分離して記録している。
- **02:51:51 JST 時点の Original-only 履歴**では、Retro Rewind ZIP の Files installer、RR 起動、TT のコース選択、スタッフ ghost replay、3 周完走、pause/restart/quit、保存 readback、cold 起動維持は未確認だった。後続の RR/保存/WFC 実証は下記各時刻節および「最新判定」に記録し、この履歴記述を上書きする。
- UI 所有権はこの記録作成時点で root に移管済み。以下は既存ファイルを実画像で確認した read-only 記録であり、ファイル名から成功を推測していない。

## 実画像で確認したメニュー状態

画像は `private/rmcj01/mobile/` に保存されている。

| 証拠 | 実画像で確認した状態 | 判定 |
|---|---|---|
| `ipad2-current-state.png` | トップメニュー。シングルプレイ、マルチプレイ、Wi-Fi、マリオカートチャンネルのタイルが表示され、GP 停止画面ではない。 | トップメニュー到達のみ |
| `ipad2-after-top-A.png` | 「シングルプレイ」内。4 行メニューで「グランプリ」が拡大・白/黄文字の選択状態。 | Single Player → Grand Prix 選択を確認 |
| `ipad2-timeattack-highlight.png` | 「VS」行が拡大・白/黄文字の選択状態。タイムアタックではない。 | **誤選択** |
| `ipad2-after-tt-A.png` | VS のサブ画面で「個人戦」「チーム戦」が表示され、「個人戦」が選択状態。 | 誤選択後の A 入力、TT ではない |
| `ipad2-single-after-back.png` | B でシングルプレイへ戻った状態。「VS」行がなお選択状態。 | 戻りを確認 |
| `ipad2-tt-highlight.png` | 「タイムアタック」行が拡大し、白/黄文字の選択状態。直前に短い上方向 pan (120 ms) を 1 回行った後の画像。 | **正しい TT 選択を画像確認（A 前）** |

前任の命名と内容が一致しないファイルも明記する。

- `ipad-41-original-tt-ghost-list.png` は実画像では「50cc キノコカップ 1st レース」の GP 開始画面。
- `ipad-42-original-tt-course-setup.png` は実画像では 12th の GP ライブ画面。

したがって、上の 2 ファイルは TT 到達・ghost 選択の証拠として扱わない。

## 操作上の再現知見

- Move stick の論理中心は (153,660) 付近。前回の 400 ms 下方向 pan はキーリピートで 2 項目以上進み、グランプリから VS まで移動した。
- これは操作のリピート/ホールド長による overshoot として観測されたもので、ゲームの選択ロジック不具合を示す証拠ではない。
- 100--150 ms 程度の短い pan を 1 回だけ行い、解放後に実画像で行の拡大・白/黄文字を確認してから A を送る必要がある。`ipad2-tt-highlight.png` はこの手順で得た正しい A 前状態。

## app.log の bounded 集計

02:51:51 JST のファイルを読み取り、テレメトリ行だけを集計した。

- `[gx] present telemetry`: 1,102 サンプル。`total` は 300--330,644。fps は min 29.986 / max 60.182 / 平均 59.9107 / 中央値 60.002。末尾のサンプルは 59.997 fps、frame p95 16.772 ms、worst 16.788 ms。
- `[input] sample`: 118 行、28 種類。キー入力（core/classic）と stick の値は記録されているが、この証拠集合には完走・finish・replay 保存を示す記録はない。
- Scene ログは `1 Scene Exit` 16 回、`2 Scene Exit` 6 回、`2 Scene Restart` 2 回。メニュー遷移を含む実行が続いていることは分かるが、race 完走の証拠にはしない。
- `crash`、`fatal`、`abort`、`segfault` は該当行 0。観測された既知の警告は `sysctlbyname failed` 1 回、`OSExceptionInit: skipped exception vector setup` 1 回、`NANDOpen: FAILED to open` 2 回、`Unbalanced calls to begin/end appearance transitions` 2 回。これらをクラッシュとは分類しない。
- 起動時には Aurora Metal (Apple M2 GPU) 初期化、1207 pipeline prewarm、`GameData` の disc index (1989 files / 2020 FST entries) が記録されている。

## 02:51時点の判定（履歴）

> この節は 02:51:51 JST の Original-only bounded snapshot に対する当時の判定である。最新の実機/readback 判定は文書冒頭の「最新判定」を優先する。

- **確認済み**: iPad で Original のトップメニュー、Single Player、Grand Prix 行、誤った VS 行、VS サブ画面、戻る操作、短い pan による正しい「タイムアタック」選択（A 前）、約 60 fps の安定描画、クラッシュなし（bounded log）。
- **当時の未確認**: TT A 後の Luigi 選択、スタッフ ghost の「リプレイ」、純正 3 周完走、pause/restart/quit、本人記録の保存/readback（スタッフ ghost 表示との混同なし）、cold 起動での license 維持、RR 正規 ZIP installer/RR 起動、RR 代表 replay、Retro WFC の Mac private room 参加。後続の root 操作と read-only readback は上記「最新判定」および時刻付き後続節に記録する。
- 当時の次手は root が `ipad2-tt-highlight.png` を画像確認した状態から A を 1 回だけ行うことだった。完走や保存は、実画面・ログ・readback の三者が揃うまで成功と記載しない、という基準は現在も維持する。


## root 操作で追加された TT 到達と接続境界（02:54--02:59 JST）

root が UI 所有権を引き継いだ後、次の画像を実画像で確認した。

- `root-ipad-menu.png`: 「タイムアタック」行が拡大した正しい選択状態。
- `root-ipad-tt-character.png`: キャラクターセレクトでマリオを選択。
- `root-ipad-tt-vehicle.png` / `root-ipad-tt-vehicle-settled.png`: 車体選択を通過。
- `root-ipad-tt-cup.png`: キノコカップ。
- `root-ipad-tt-courses.png`: ルイージサーキット。
- `root-ipad-tt-ghosts.png`: ゴースト 1/1、Luigi Circuit `01:29.670`、`Nin★sato` / Nintendo のスタッフカード。
- `root-ipad-replay-selected.png`: `リプレイをみる` 行が拡大・白/黄文字で選択。
- `root-ipad-replay-confirm.png`: 「レースをはじめます」確認ダイアログの `OK`。
- `root-ipad-replay-start.png`: ルイージサーキット上で Luigi のスタッフゴーストが自走し、画面に `Nin★sato` が表示されたリプレイ開始状態。

この画像列から **TT の正規設定、スタッフゴーストカード表示、`リプレイをみる` 選択、確認、リプレイ開始までは Pass** とする。`root-ipad-replay-start.png` は開始直後の走行画面であり、3 周完走・完走画面・記録保存を示さない。

同時刻の `private/rmcj01/mobile/agent-device-auto/sessions/rmcj-ipad/runner.log` には、iPad の接続待ち境界が記録されている。

- `Device is busy (Connecting to iPad Air M2)` により xcodebuild の destination 待ちタイムアウトが発生。
- 02:57:40 に runner 自体は起動し screenshot/snapshot/tap を受理・完了したが、02:58:40 の idle keepalive 後、02:59:12 の xcodebuild は `BUILD INTERRUPTED`。以後の XCTest screenshot は接続タイムアウトとして扱う。
- これは端末接続/runner 状態の証拠であり、ゲームのリプレイ完走失敗やクラッシュとは分類しない。root はケーブル再接続・端末ロック解除を確認中で、再接続後の完走画像が得られるまで完走判定を保留する。


## 再接続後の replay / pause / quit 状態（02:59 以降）

端末再接続後、root が取得した画像を実画像で確認した。

- `root-ipad-reconnected.png` は Luigi Circuit 上の走行画面で、Luigi の車体と `Nin★sato` 表示が見える。ゴーストの走行/勝利モーションらしき一時状態は確認できるが、完走カウンタ・完走画面・保存の証拠ではない。
- `root-ipad-replay-pause.png` は replay 中のポーズメニュー（`リプレイをつづける` が選択状態）。したがって pause 画面への遷移自体は確認済み。
- `root-ipad-replay-quit-selected.png` は `リプレイをやめる` 行の選択状態。
- `root-ipad-replay-quit-confirm.png` / `root-ipad-quit-yes.png` は「コースセレクトにもどります。よろしいですか？」確認画面で、後者は `はい` の選択状態を実画像で確認できる。
- `root-ipad-tt-return-final.png` は確認で `はい` を送った後もコースセレクトへ戻らず、replay メニュー（`リプレイをつづける` / `はじめからリプレイ` / `レースをはじめる` / `リプレイをやめる`）に留まった状態。

このため、**pause 画面到達、quit 行選択、quit 確認ダイアログと `はい` 選択までは Pass** とするが、`リプレイをやめる` の実際のコースセレクト帰還は未解決（Pass と記載しない）。同じ状態が複数回再現しており、メニュー背後のゴースト走行/勝利/次カウントダウンのループが続く。入力干渉か scene transition かは trace 付きの再起動診断が必要で、現時点ではゲーム不具合とも操作ミスとも断定しない。

この 02:59 前後の再接続スパンでは 3 周完走画面、本人記録保存/readback、cold 起動維持は取得されていなかった。**当時の状態**として RR installer/RR 起動と Mac private room 参加も未実行だったが、RR installer/RR 起動と WFC ログインは後続時刻節で実証している。


## cold chooser と Retro Rewind 正規 ZIP installer（03:05--03:09 JST の履歴）

root が replay 状態から cold 起動し、次の実画像を取得した。

- `root-ipad-cold-chooser.png`: cold 起動後の KartPad chooser。「Mario Kart Wii / Original game」と「Retro Rewind / Download 6.12.7・Extra content + Retro WFC」の 2 選択肢が表示された。chooser 表示だけでは license 維持やゲーム起動を判定しない。
- `root-ipad-rr-files.png`: システム Files picker の「最近使った項目」。
- `root-ipad-rr-localfiles.png`: Files の「この iPad 内」一覧で `KartPad Japan` フォルダを表示。
- `root-ipad-rr-zip.png`: `KartPad Japan` 内に `RetroRewind-6.12.7-full.zip`（表示 1.86 GB）と `RMCJ01-DATA` が見える。
- `root-ipad-rr-install.png`: 正規 `Choose Full-Download ZIP…` ルートで ZIP を選択後、「Installing Retro Rewind / Installing Retro Rewind content… 20%」の進捗ダイアログ。

この時点で **cold chooser 表示、Files の正規フォルダ/ZIP 選択、installer 実行開始（20% 表示）は Pass**。当時は展開完了、RR chooser からの実起動、RR 代表 replay 完走、Retro WFC 接続を未確認としていた。後続の「Retro Rewind boot」「Retro WFC consent」節と最新判定で、展開後の RR title/menu/license と WFC MOTD/ONLINE 表示を別途実画像確認している。20% 画像だけから成功を推測しない。

この RR プロセスのライブ stdout は旧 `private/rmcj01/mobile/agent-device-auto/sessions/rmcj-ipad/app.log` ではなく `private/rmcj01/mobile/ipad-traced-live.log` に切り替えられた。`KARTPAD_STATE_TRACE` は端末上の `/private/var/mobile/Containers/Data/Application/[private container identifier omitted]/Documents/rmcj01-live-trace.csv` のみ有効。RKG 生成・forcefinish・メモリ操作は行っていない。RR 起動後の判定は新しい live stdout と trace の対応を確認してから行う。


## Retro Rewind boot 後の実画像と live stdout（03:10--03:15 JST の履歴）

正規 ZIP installer 後、root が取得した実画像を確認した。

- `root-ipad-rr-startup.png`: `MARIOKART RETRO REWIND` タイトルと `Press the A Button`。
- `root-ipad-rr-menu.png`: Retro Rewind のメインメニュー（`Single Player`、`Multiplayer`、`Retro WFC`）が表示。
- `root-ipad-rr-license.png`: RR の license settings 画面で `KartPad` Mii、識別表示 `93ba8c8a`、500/200/150/100cc 行が見える。RR 起動後に license 画面まで到達した実画像だが、cold 前後の hash/readback 比較ではない。

したがって、**ZIP 展開後の RR タイトル、RR メインメニュー、RR license settings 表示は Pass** とする。この時点で RR 代表 replay のコース選択・走行・3 周完走、Retro WFC の Mac private room 参加は未確認であり、後続 read-only save/trace と WFC ログイン画面の確認を別境界として扱う。

RR 専用ライブ stdout `private/rmcj01/mobile/ipad-traced-live.log` の起動境界は次の通り。

- `retro_rewind` profile、`retro_rewind_root=RetroRewind/RetroRewind6`、Riivolution overlay root、`RetroRewind6.xml: 1 active patch(es), 157 mapping(s)`。
- disc index `1989 disc file(s), 4878 overlay registration(s) from 1 root(s)`、`6927 FST entries`。RR の overlay/patch root が読み込まれたことをログで確認。
- `New race started` マーカーは 1 件あるが、対応する完走画面・finish カウンタ・本人記録保存は取得していないため、race/replay 完走の証拠にはしない。
- 起動直後の一時的な fps 低下後、連続する `[gx] present telemetry` は概ね 60 fps（`59.9--60.1` 付近）。audio worker は non-silent PCM を host playback へ到達させている。これは描画/音声パスのログ証拠であり、主観的な音質判定ではない。
- RR ログでは `crash` / `fatal` / `abort` / `segfault` は見つかっていない。`NANDOpen`/`IOS_Open` の未作成 trophy・設定ファイル警告、`/dev/usb/hid` unknown device、音声 queue drop は観測事実として保持するが、クラッシュとは分類しない。
- ライブログ末尾には時刻情報なしで `App terminated due to signal 9.` が 1 行ある。後続確認では root が signed-local-network 更新時に `devicectl terminate-existing` で旧プロセスを置換したものと特定され、計画済み cold 起動でありクラッシュではない。RR race 完走判定には使わない。

このプロセスで `KARTPAD_STATE_TRACE` は端末上の `/private/var/mobile/Containers/Data/Application/[private container identifier omitted]/Documents/rmcj01-live-trace.csv` のみ有効。RKG 生成、forcefinish、メモリ書換えは行っていない。RR replay の次回判定は screenshot、live stdout、trace の同一区間を対応付けて行う。


## Retro WFC consent とログイン状態（03:20 前後の履歴）

root が取得した WFC 画面を実画像で確認した。

- `root-ipad-wfc-consent1.png`: Retro WFC (1P) の送信内容説明（Mii/ニックネーム、records、ghost data、他プレイヤーとの共有）と Next。
- `root-ipad-wfc-consent2.png`: プライバシー注意（実名を含む Mii ニックネームを変更する案内）と Next。
- `root-ipad-wfc-permit.png` → `root-ipad-wfc-permit-selected.png`: 「Will you allow game data to be sent to Retro WFC?」で Permit/Prohibit を表示し、後者で `Permit` の選択状態を実画像確認。ユーザーの共有同意は既取得の指示に対応。
- `root-ipad-wfc-connect.png`: `Connecting to Retro WFC.`。
- `root-ipad-wfc-status.png`: `Current message of the day is: Welcome to Retro WFC!`、`Server Status: [笑顔] - ONLINE`、`2x VR Multiplier Active`。背景に player/rank/score パネルも表示。

この列により、**通常 Retro WFC の同意 UI、Permit 選択、接続、MOTD と Server ONLINE 表示までは Pass**。この節の時点では Mac private room への参加、online matchmaking、オンラインレース開始/完走、相互 friend code 登録を未検証としていた。後続の friend-code UI キャプチャは次節に分離する。`ONLINE` 表示を room 参加やレース成立と混同しない。

RR live stdout には同時刻に `WWFC_INFO` の `*.gs.nintendowifi.net -> *.gs.play.rwfc.net` ホスト変換、`NHTTPi_FixHostHeader`、ServerDateTime、Sake storage URL 設定、複数の `QR2: Received kick order` が記録されている。これはサーバー接続/バックグラウンド管理のログ証拠であり、特定ルーム参加の証拠ではない。friend code、Mii の実値、個人識別値はこの公開レポートに書かない。

## Friend-code UI と roster 状態（03:22--03:32 JST）

- `root-ipad-friend-register.png` → `root-ipad-friend-registered.png` は登録入力と確認ダイアログ、`root-ipad-friend-register-result.png` は「The friend code below has been registered.」の完了画面。コードの実値はこの公開レポートに記載しない。
- `root-ipad-find-friend.png` は `Friend Roster` の `1/1` 表示だが、スロット画像が `?` の状態。これは相手側の登録待ち（相互登録待ち）の途中キャプチャであり、Mac room 参加や相互確認の証拠ではない。
- 後続 `root-ipad-roster-recovered.png` / `root-ipad-roster-sync.png` も同じ `1/1` スロットの回復・同期途中を示す。`root-ipad-roster-mutual.png` は `1/1`、Mii カードと `I'm on Retro WFC!` が表示された状態で、Mii 表示の到達は確認できるが、相手 Mac 側の roster 反映を含む最終的な相互登録完了とは分離して扱う。
- **判定**: iPad 側の friend code 入力・登録完了 UI と roster 表示遷移は Pass。相互 friend roster の最終同期、Mac private room への実参加、online レース開始/完走は未確認。UI 背景の `1/1` と `ONLINE` は room 成立と混同しない。

## signed-local-network 更新後の cold/login と room 結果（03:41--03:49 JST）

root が signed-local-network 更新版をインストールし、既存プロセスを `devicectl terminate-existing` で計画的に置換して cold 起動した。旧 `ipad-traced-live.log` の `App terminated due to signal 9.` はこの操作に対応するもので、クラッシュには分類しない。

- 更新 IPA: `private/rmcj01/mobile/signed-local-network/KartPad-Japan.ipa`、SHA-256 `ef1c94489c5b0e1b3dd35d5da232df98f4ff48815e3ffcea389434a790c528fe`。root の比較では unsigned executable は byte-identical で、追加変更は `NSLocalNetworkUsageDescription` plist と署名差分。
- `root-ipad-localnet-title.png` は Retro Rewind title、`root-ipad-localnet-main.png` は RR main menu（Single Player / Multiplayer / Retro WFC、右上 license icon）。`root-ipad-localnet-license.png` では `KartPad` license と既存表示を確認。chooser の Installed 6.12.7 表示を含む cold 起動後の RR 選択・license 維持は root の実画像確認済み。
- `root-ipad-localnet-friends.png` は Friends メニュー（Create a Room / Find a Friend / Register a Friend）、`root-ipad-localnet-roster.png` は Friend Roster `1/1` だが `?` スロット。既存 friend code 登録 UI は保持されているが、このキャプチャ時点でも相互 roster 同期は確定しない。
- `root-ipad-localnet-friend-card.png` / `root-ipad-localnet-join-recovered.png` は friend card 上に 2 件の `KartPad`、`0 wins`、`Meet Up`、`I have an open room!` を表示する状態。これは相手 open room の表示/Meet Up 選択到達であり、実際の room 内参加や online race を示す画面とは分離する。
- 旧 join 試行の `root-ipad-room-join-result.png` / `root-ipad-room-join60.png` は `Joining a friend...`、`root-ipad-room-join-timeout.png` は「You couldn't meet up with this friend. Please wait and try again later.」を実画像で確認。少なくともこの試行は **join 失敗**。root が再試行した結果の room 内レースは未確認。
- `root-ipad-localnet-wfc.png` は cold 後の通常 Retro WFC login/readback で `Welcome to Retro WFC!`、`Server Status: ONLINE`、`2x VR Multiplier Active` を表示。login/MOTD は Pass、Mac private room 参加・online race は未確認。
- signed-local-network 更新後の appDataContainer でも `Library/Application Support/KartPad/RetroRewind/riivolution/save/RetroWFC/RMCJ/{rksys.dat,banner.bin}` を `device info files`（結果 JSON: `private/rmcj01/mobile/ipad-localnet-rr-save-list-20260907.json`）で再列挙し、`rksys.dat` を `private/rmcj01/mobile/ipad-localnet-rr-redirected-save-20260907.dat` に read-only コピー（結果 JSON: `private/rmcj01/mobile/ipad-localnet-rr-save-copy-20260907.json`）。サイズ/header/保存・計算 CRC `0x4003406f`/SHA-256 `ea0b3e78…` は更新前の RR readback と byte-identical で、redirect save の cold 更新後保持を確認した（新しい race/record 書き込みの証拠ではない）。
- 同じ更新後に Original NAND `.../NAND/title/00010004/524d434a/data/rksys.dat` も `private/rmcj01/mobile/ipad-localnet-original-save-20260907.dat`（結果 JSON: `private/rmcj01/mobile/ipad-localnet-original-save-copy-20260907.json`）へ read-only コピー。`RKSD0006`、CRC `0xe4a9a2bf`、SHA-256 `ca7c0072…` は cold 前後の Original readback と byte-identical。これは chooser/license/FC 表示維持と整合するが、画面表示の代替ではない。

新 live stdout `private/rmcj01/mobile/ipad-local-network-live.log` の実行コンテナは `[private container identifier omitted]` で、`RetroRewind` redirect と `retro_rewind` profile が記録される。一方 `KARTPAD_STATE_TRACE` は旧 `[private container identifier omitted]/Documents/rmcj01-local-network-trace.csv` を指し、ログに `[state-trace] unable to open ...` が 1 行ある。`devicectl copy from` も当該新名ファイルで CoreDeviceError 7000（file node 不在）となり、Documents 列挙 (`ipad-local-network-documents-list-20260907.json`) は旧 `rmcj01-live-trace.csv` 187 bytes のみを示す。従ってこの更新版で新 trace/finish data は得られておらず、`New race started` 1 行だけを完走証拠にしない。

## Read-only device artifact refresh（03:29--03:30 JST）

端末 UI/プロセスを操作せず、接続済み iPad の appDataContainer から `devicectl device copy from` と `device info files` のみを実行した。入力元データは変更していない。

- Trace: `Documents/rmcj01-live-trace.csv` → `private/rmcj01/mobile/ipad-live-trace-20260907.csv`（結果 JSON: `private/rmcj01/mobile/ipad-live-trace-copy-20260907.json`）。コピー結果は成功、187 bytes、CSV header 1 行・データ行 0、SHA-256 `147a2702944bcf6a630d021b1611aa22e310dfeb7b9943e564d6fab461e1bcb7`。同時刻の `Documents` 列挙（結果 JSON: `private/rmcj01/mobile/ipad-documents-list-20260907.json`）でも端末ファイル 187 bytes / mtime 03:10 を確認。この時点のファイルは race/finish trace ではない。
- Original cold readback: `Library/Application Support/KartPad/NAND/title/00010004/524d434a/data/rksys.dat` → `private/rmcj01/mobile/ipad-original-save-after-cold-20260907.dat`（結果 JSON: `private/rmcj01/mobile/ipad-original-save-after-cold-copy-20260907.json`）。直後の `device info files`（結果 JSON: `private/rmcj01/mobile/ipad-original-save-list-after-cold-20260907.json`）でも `rksys.dat` 2.7 MB と `banner.bin` 29 KB を列挙し、端末 mtime は 03:02。サイズ 2,867,200 bytes、header `RKSD0006`、保存 CRC（offset `0x27ffc`）`0xe4a9a2bf` (decimal `3836322495`) と `Crc32(bytes[:0x27ffc])` が一致。SHA-256 `ca7c0072c496225b2c55d242912f9c3e6da3375c8776e7a52c2406d0f5309bec` で、cold 前 `private/rmcj01/mobile/ipad-original-save-before-cold.dat` と byte-identical。
- RR redirect path listing: `Library/Application Support/KartPad/RetroRewind/riivolution/save/RetroWFC` を `device info files --recurse` で確認し、`RMCJ/rksys.dat` (2,867,200 bytes) と `RMCJ/banner.bin` (29,344 bytes) を列挙（結果 JSON: `private/rmcj01/mobile/ipad-rr-save-parent-list-20260907.json`）。ライブログの redirect 文字列にある `RMCJ (clone)` ではなく、appDataContainer 内の実体は `RMCJ` ディレクトリ。
- RR save readback: 上記 `RMCJ/rksys.dat` を `private/rmcj01/mobile/ipad-rr-redirected-save-20260907.dat` に read-only コピー（結果 JSON: `private/rmcj01/mobile/ipad-rr-redirected-save-copy-20260907.json`）。サイズ 2,867,200 bytes、header `RKSD0006`、保存/計算 CRC `0x4003406f` (decimal `1073954927`) 一致、SHA-256 `ea0b3e78736bbbafeff7885cfd6c65ec9bed2439e3cdeaf9c72805bee71c1e36`。Original NAND save とは異なる byte 列だが、両方とも形式/CRC は有効。
