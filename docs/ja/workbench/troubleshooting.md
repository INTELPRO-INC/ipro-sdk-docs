---
title: "トラブルシューティング"
description: IPRO Workbench のメッセージ、ツールバーとサイドバーの状態の意味と対処、macOS と Windows 固有の問題、問題を報告するときに添付するものを説明します。
---

# トラブルシューティング

IPRO Workbench 0.1.1 で表示されるメッセージと状態の原因と対処を、表示される場所ごとにまとめています。

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

## ツールバーとサイドバーの状態 { #status }

| 表示される状態 | 対処 |
|---|---|
| ツールバーに琥珀色で「no probe」と表示される | IDE が IPRO Debug Probe を見つけられません。USB ケーブルを確認し、可能であればプローブをコンピューターに直接接続します。接続すると、数秒以内に自動的に表示されます。 |
| ステータスバーに「Setup: N」と表示される | クリックして IPRO Home を開き、バナーの **Fix Environment** を押します。 |
| **Board** に「Runs other firmware」と表示される | ボードは現在のアプリケーションの最新ビルドを実行していません。現在のプログラムを実行するには、書き込みを行います。 |
| IPRO6S EVK で、**Board** に「Runs …」の行がない | 正常です。IPRO6 シリーズのボードは起動時にビルド時刻を出力しないため、IDE はボード上のファームウェアを確認できません。**IPRO Flash** の `[All Success]` とモニターの起動メッセージで確認してください。 |

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
| **SDK for this toolchain** に調整が必要と表示される | IPRO SDK 2.2 を Windows でビルドするには、ホスト側の修正がいくつか必要です。**Fix Environment**（またはその行の **Prepare the SDK for this toolchain**）を押すと、IDE が自動的に対処します。 |
| Wi-Fi スループット：ボードが送信してコンピューターが受信する場合に結果が出ない | Windows のファイアウォールは、デフォルトで受信接続をブロックします。TCP ポート 5001 を許可する受信の規則を追加するか（[テストを実行する](measure.md#iperf-run)を参照）、コンピューターからボードへ送信する方向に切り替えます。 |
| Python の行に kconfiglib がないと表示される | コマンドプロンプトで `python -m pip install kconfiglib windows-curses` を実行し、**Check Again** を押します。 |
| コードエディターで clangd のダウンロードを求められる | コードナビゲーションには clangd を使用します。表示に従ってダウンロードするか、**Environment** の clangd の行で Fix を押します。 |

## 問題の情報を収集する { #collect }

INTELPRO に問題を報告するときは、次のものを添付してください。

1. IDE のバージョン：**Help → About** を選択します。
2. 失敗したステップの出力：**Output** パネルで **IPRO Build**、**IPRO Flash**、**IPRO Setup** のいずれかを選択し、すべて選択してコピーします。
3. ボードの出力：IPRO Monitor タブで **Save Monitor Output…** を押すか、`build/logs` にあるモニターログを添付します。
4. クラッシュの場合は、`build/crash` にあるクラッシュダンプのフォルダーを添付します。
