---
title: "トラブルシューティング"
description: IPRO Workbench のメッセージ、ツールバーとサイドバーの状態の意味と対処、macOS と Windows 固有の問題、問題を報告するときに添付するものを説明します。
---

# トラブルシューティング

IPRO Workbench 0.2.0 で表示されるメッセージと状態の原因と対処を、表示される場所ごとにまとめています。

## 画面に表示されるメッセージ { #messages }

ステップが失敗すると、IDE は対処用のボタンとともに説明を表示します。次の表に、メッセージごとの原因と対処を示します。

| 画面のメッセージ | 原因 | 対処 |
|---|---|---|
| The board did not answer on … | プローブのケーブルが正しく接続されていない、ボードに電源が入っていない、または間違ったポートが選択されている | ケーブルと電源を確認し、**Select Port** または **Retry** を押す |
| Another program has … open, so IntelProCube cannot use it | 別のシリアルモニターやターミナルが同じポートを開いている | そのプログラムを閉じてから **Retry** を押す |
| … has not been built yet. | 書き込むファームウェアがまだない | **Build and Flash** を押す |
| Flashing needs IntelProCube, and it was not found. | IntelProCube がインストールされていない | **Install IntelProCube** を押すか、**Browse…** で既存のものを指定する |
| … did not compile. First error at … | コードにエラーがある | **Go to Error** を押す。**Problems** ビューにすべてのエラーが一覧表示される。**Ask AI to Fix** を押すこともできる |
| CMake could not configure … | `.config` または `CMakeLists.txt` に誤りがある | **IPRO Build** の出力を読んで問題を修正し、**Reconfigure and Build** を押す |
| The toolchain or the build tools are missing. | 開発環境がまだ整っていない | **Fix Environment** を押す |
| pins.yaml of … has errors, so app_pins.c was not generated. | ピン設定が競合している、または信号がそのピンで使用できない | **Open Pin Configuration** を押し、**Problems** の項目を 1 つずつ修正してから **Save and Generate** を押す |
| The board started firmware built …, not the … just flashed. | 書き込みが実際にはボードに届いていない | **IPRO Flash** の出力を確認し、**Flash Again** を押す |
| … is over its memory budget | メモリ領域が `ipro.build.memoryBudget` で設定した上限を超えている | **Memory Map** を押してサイズの大きいシンボルを探すか、**Budget Settings** を押して上限を調整する |
| The partition table of … reaches …, but the board on this probe has … of flash | 選択したパーティションテーブルがボードの Flash より大きい | **Partition Table** を押して別のテーブルを選ぶか、`.config` の Flash サイズを確認する |
| IntelProCube has no …, the partition table … flashes with. Without one the board would not boot. | この IntelProCube のバージョンに、ボードに必要なパーティションテーブルがない（IPRO6S EVK には 0.7.0.1 以降の `partition_cfg_fw_direct.toml` が必要） | **Install IntelProCube** を押すか、**Environment** の IntelProCube の行で 0.7.0.1 以降のバージョンを選択してから、もう一度書き込む |
| `mfg uses the same space as FW …`（**Partition Table** ビューと **AI Model** ビューのチェック結果） | 1M パーティションテーブルには AI モデル用の独立した領域がない | **Partition Table** で、独立した mfg パーティションを持つテーブル（例：アプリケーションに同梱されているもの）を選択する |
| The board did not answer. Is it running the MFG firmware? | RF テスト中に、ボードが MFG ファームウェアを実行していない、またはモニターが開いていない | MFG ファームウェアを書き込み、モニターを開いてから **Check Firmware** を押す |
| **Testing** ビューに結果が表示されない | ボードが再起動していない、またはアプリケーションが Unity テストフレームワークを使用していない | モニターがプローブの UART ポートで開いていることを確認し、**Run Tests on Board** を押す |
| The board did not answer wifi_state. Flash an application with the Wi-Fi shell and iperf… | Wi-Fi スループット：ボード上のアプリケーションに Wi-Fi シェルがない、またはモニターが別のポートで開いている | IPRO6S EVK には `platform/ipro6_demo` を書き込む。ツールページの **Board** で、このボードのポートを選択する |
| The network name must be 1 to 32 characters without spaces… / The password must be 8 to 63 characters without spaces. | ボードのシェルがスペースを受け付けない | スペースを含まないネットワーク名とパスワードを使用する（必要に応じて、アクセスポイントに別のネットワークを設定する） |
| The board did not join …. Check the name and password. | 名前またはパスワードの入力ミス、またはネットワークが 2.4 GHz でない | 修正して、もう一度 **Join Network** を押す |
| This PC has no address on the board's network (…). | コンピューターとボードが同じ Wi-Fi ネットワークにない | コンピューターを同じネットワーク（アクセスポイントモードでは、ボードが作成したネットワーク）に接続してから、**Run Test** を押す |
| The board did not connect to this PC on TCP port 5001. A firewall on this PC may block incoming connections… | ボードが送信してコンピューターが受信する場合に、コンピューターのファイアウォールが受信接続をブロックしている（Windows のデフォルト） | ファイアウォールで TCP 5001 の受信を許可する（[テストを実行する](measure.md#iperf-run)を参照）。または、コンピューターからボードへ送信する方向に切り替える |
| This PC could not reach the board's iperf server… / An earlier iperf is still running on the board… | ボードの iperf サーバーがまだ接続を待ち受けている | **Reset Board** を押す。ボードが再起動したら、もう一度ネットワークに参加する |
| The board did not restart. Is the monitor on the console port of an IPRO Debug Probe? | モニターが CCI または別のポートで開いている | ツールバーのボードをクリックし、**Select Port…** でプローブの UART に切り替える |
| … is not connected. Check the cable to the board, or pick another port. | 選択したポートがなくなった（ボードが取り外された、またはその USB ポートの名前が変わった） | ケーブルを確認し、ツールバーのボードをクリックして **Select Port…** でポートを選択し直す |
| The setting ipro.board.port keeps the port at …. Clear the setting to use …? | `ipro.board.port` の設定が、使いたいポートとは別のポートを指定している | **Use …** を押して設定をクリアする。設定を残す場合はキャンセルする |
| The board on … answered, but its flash did not: it was flashed as …, and the flash pins of that board are not this one's. | ツールバーで選択したボードが接続しているボードと異なるため、誤った Flash ピンが使われた | **Select Board** を押して接続しているボードを選択し、**Retry** を押す |
| … is laid out for boot2, and this IntelProCube has no boot2 image for …. | パーティションテーブルに boot2 が必要だが、IntelProCube にそのチップ用の boot2 がない | **Install IntelProCube** を押して更新するか、**Partition Table** でファームウェアを直接起動するテーブルを選択する |
| IntelProCube … is too old for …: a board flashed with it does not start. | IPRO6S EVK には IntelProCube 0.7.0.1 以降が必要 | **Install IntelProCube** を押すか、**Browse…** で新しいものを指定する |
| The board did not start boot2's USB downloader. … | [ボード自身の USB から書き込む](flash.md#usb-flash)ときに、ボードがダウンローダーで再起動しなかった（例：USB コンソールのないファームウェア） | もう一度 **Flash** を押し、20 秒以内にボードの USB ケーブルを抜いて差し直す |
| … is the board's own USB port. Flashing over it is not available on Windows yet… | Windows 版はボード自身の USB から書き込めない | macOS から書き込むか、IPRO Debug Probe を接続してその UART を選択する |
| … is the board's own USB port, and this SDK has no tools/ipro_dl.py to flash over it. | SDK が V2.3.0 より古い | IPRO SDK V2.3.0 を使用するか、IPRO Debug Probe 経由で書き込む |
| The default partition table comes with IntelProCube, and IntelProCube was not found. / This IntelProCube has no …. | **Partition Table** がデフォルトのテーブルを見つけられない | **Install IntelProCube** を押すか、**Flash with** で別のテーブルを選択する |
| The partition table's FW partition has one slot. An OTA needs a table with a second FW slot… / This partition table is a layout without boot2… | **OTA Package**：パーティションテーブルが boot2 用の A/B レイアウトではない | **Partition Table** で、boot2 用の領域と 2 つ目の FW スロットを持つテーブル（例：`ipro_ble_remote` の `partition_cfg_2M_remote_ab.toml`）を選択する。[OTA パッケージ](flash.md#ota)を参照 |
| boot2 OTA packages are for IPRO7 applications; this one is built for the …. | **OTA Package** は IPRO6S のアプリケーションに対応していない | なし。IPRO6S には boot2 用の OTA パッケージはない |
| The board did not answer the ota_uart command. Its application needs CONFIG_IPRO_OTA=y and CONFIG_IPRO_OTA_UART=y… | ボード上のアプリケーションに `ota_uart` コマンドがない、またはポートがそのコンソールではない | IPRO SDK V2.3.0 で、この 2 つの設定をオンにしてビルドと書き込みを行い、もう一度送信する |
| The board refused the package: the partition table on the board has no second FW slot. … | ボードにまだ A/B テーブルが書き込まれていない | まず A/B テーブルと boot2 でアプリケーションを書き込む（[OTA パッケージ](flash.md#ota)の手順 2 と 3） |
| The board refused the package: its SHA-256 does not match: the file is damaged, or the line dropped data. | 転送中にデータが失われた | **Check on Board** でもう一度試す。それでも失敗する場合は、パッケージを作成し直す |
| The board did not list any network (no answer to wifi_scan). | Wi-Fi スループット：ボードがスキャンに応答しない | ボード上のアプリケーションに Wi-Fi シェルがあること（例：`ipro6_demo`）を確認し、**Scan** を押す |
| The Wi-Fi stack did not start (no answer to stack_wifi). | ボードが `stack_wifi` に応答しない | ボードをリセットし、もう一度 **Join Network** を押す |

## ツールバーとサイドバーの状態 { #status }

| 表示される状態 | 対処 |
|---|---|
| ツールバーに琥珀色で「no probe」と表示される | IDE が IPRO Debug Probe を見つけられません。USB ケーブルを確認し、可能であればプローブをコンピューターに直接接続します。接続すると、数秒以内に自動的に表示されます。 |
| ステータスバーに「Setup: N」と表示される | クリックして IPRO Home を開き、バナーの **Fix Environment** を押します。 |
| **Board** に「Runs other firmware」と表示される | ボードは現在のアプリケーションの最新ビルドを実行していません。現在のプログラムを実行するには、書き込みを行います。 |
| IPRO6S EVK で、**Board** に「Runs …」の行がない | IPRO SDK 2.2.1 以前では正常です。これらのバージョンの IPRO6 ファームウェアは起動時にビルド時刻を出力しないため、IDE はボード上のファームウェアを確認できません。**IPRO Flash** の `[All Success]` とモニターの起動メッセージで確認してください。IPRO SDK V2.3.0 からはこの行が表示されます（[IPRO7 シリーズとの違い](flash.md#ipro6s-differences)を参照）。 |
| ステータスバーに構成（歯車と `.config`）が表示されない | 正常です。`defconfig_*` や `config_*` などのほかの構成ファイルがあるアプリケーションでだけ表示されます（[別構成](develop.md#configurations)を参照）。 |

## macOS の問題 { #macos }

| 状況 | 対処 |
|---|---|
| 初回起動時に、開発元を検証できないと表示される | 「システム設定 → プライバシーとセキュリティ」を開き、**このまま開く** をクリックします（[IPRO Workbench のインストール](install.md#install)を参照）。 |
| **Environment** に **macOS quarantine** が表示される | ツールがブラウザーやチャットアプリでダウンロードされたため、実行時に macOS が停止させます。その行の鍵アイコンをクリックし、確認するとフラグが削除されます。 |
| CMake またはビルドプログラムがないと表示される | macOS では、IDE はビルドツールをインストールしません。ターミナルで `xcode-select --install` と `brew install cmake ninja` を実行し、**Check Again** を押します。 |
| 書き込みが途中で `Device not configured` により失敗する | プローブが USB から切断されました（ケーブル、ハブ、または電源が原因）。ケーブルを交換するか、プローブをコンピューターに直接接続してから、**Retry** を押します。 |

## Windows の問題 { #windows }

| 状況 | 対処 |
|---|---|
| インストール時に「Windows によって PC が保護されました」と表示される | **詳細情報** をクリックし、アプリ名が IPRO-Workbench であることを確認してから **実行** をクリックします。 |
| 別のシリアルツールから COM ポートを開けない | Windows では、1 つの COM ポートを同時に使用できるのは 1 つのプログラムだけです。別のツールを開く前に IPRO Monitor を閉じます。また、IDE で書き込めるよう、使い終わったらそのツールを閉じます。 |
| **SDK for this toolchain** に調整が必要と表示される | IPRO SDK 2.2.1 以前を Windows でビルドするには、ホスト側の修正がいくつか必要です。**Fix Environment**（またはその行の **Prepare the SDK for this toolchain**）を押すと、IDE が自動的に対処します。 |
| Wi-Fi スループット：ボードが送信してコンピューターが受信する場合に結果が出ない | Windows のファイアウォールは、デフォルトで受信接続をブロックします。TCP ポート 5001 を許可する受信の規則を追加するか（[テストを実行する](measure.md#iperf-run)を参照）、コンピューターからボードへ送信する方向に切り替えます。 |
| RISC-V ツールチェーン 13.1.1 でビルドするとリンクに失敗する | Windows では、IPRO SDK を RISC-V ツールチェーン 14.2.1 でビルドしてください。13.1.1 では SDK のビルド済みライブラリをリンクできません。**Fix Environment** を押して 14.2.1 をインストールするか、**Environment** のツールチェーンの行で 14.2.1 を選択します。 |
| ボード自身の USB ポートを選択すると書き込みに失敗する | Windows 版は、まだボード自身の USB から書き込めません。IPRO Debug Probe を接続し、その UART を選択します。 |
| Python の行に kconfiglib がないと表示される | コマンドプロンプトで `python -m pip install kconfiglib windows-curses` を実行し、**Check Again** を押します。 |
| コードエディターで clangd のダウンロードを求められる | コードナビゲーションには clangd を使用します。表示に従ってダウンロードするか、**Environment** の clangd の行で Fix を押します。 |

## 問題の情報を収集する { #collect }

INTELPRO に問題を報告するときは、次のものを添付してください。

1. IDE のバージョン：**Help → About** を選択します。
2. 失敗したステップの出力：**Output** パネルで **IPRO Build**、**IPRO Flash**、**IPRO Setup** のいずれかを選択し、すべて選択してコピーします。
3. ボードの出力：IPRO Monitor タブで **Save Monitor Output…** を押すか、`build/logs` にあるモニターログを添付します。
4. クラッシュの場合は、`build/crash` にあるクラッシュダンプのフォルダーを添付します。
