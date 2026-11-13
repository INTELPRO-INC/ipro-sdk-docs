---
title: "ショートカット、コマンド、設定"
description: IPRO Workbench 0.2.1 のリファレンスです。キーボードショートカット、IPRO コマンド、ipro.* 設定、MCP ツール、IDE が使用するファイルとフォルダーをまとめています。
---

# ショートカット、コマンド、設定

IPRO Workbench 0.2.1 のキーボードショートカット、コマンド、設定、MCP ツール、ファイルの場所です。

## キーボードショートカット { #shortcuts }

| 操作 | macOS | Windows |
|---|---|---|
| ビルド、書き込み、モニター | `Cmd+Alt+R` | `Ctrl+Alt+R` |
| ビルド | `Cmd+Alt+B` | `Ctrl+Alt+B` |
| 書き込み | `Cmd+Alt+U` | `Ctrl+Alt+U` |
| シリアルモニター | `Cmd+Alt+M` | `Ctrl+Alt+M` |
| コマンドパレット | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| 設定を開く | `Cmd+,` | `Ctrl+,` |
| 保存（設定、ピン、GATT、ファイル） | `Cmd+S` | `Ctrl+S` |

## IPRO コマンド { #commands }

以下のコマンドはすべて、コマンドパレットに `IPRO` と入力すると見つかります。ほとんどのコマンドは、IPRO メニュー、ツールバー、コンテキストメニューにもあります。

| コマンド | 用途 |
|---|---|
| **IPRO Home** | IPRO Home を開く |
| **Open SDK…** / **Install SDK from GitHub…** | IPRO SDK を開く／インストールする |
| **Check Environment** / **Fix Environment** | 開発環境を再チェックする／不足している項目をインストールする |
| **Select Application…** / **New Application…** / **Copy as New Application…** | アプリケーションを管理する |
| **Select Configuration…** | アプリケーションのビルド元の構成（`.config`、`defconfig_*`、`config_*`）を選択する。[別構成](develop.md#configurations)を参照 |
| **Select Board…** / **Select Port…** | ボードまたはシリアルポートを変更する |
| **Select Toolchain…** / **Select IntelProCube…** | このコンピューターにすでにあるツールを代わりに使用する |
| **Build, Flash and Monitor** / **Build** / **Flash** / **Stop** | 実行と停止 |
| **Reconfigure and Build** / **Clean** | CMake の構成をやり直す／ビルド結果を削除する |
| **Reset Board** | プローブを介してボードをリセットする |
| **Serial Monitor** / **Open Monitor on Another Port…** | モニターを開く |
| **Filter Monitor Output…** / **Show Monitor Timestamps** / **Save Monitor Output…** | モニター出力の表示と保存 |
| **Serial Plotter** | ボードが出力した数値を曲線としてプロットする |
| **Sensor Dashboard** | ボードが出力した `name:value` の行をダッシュボードとして表示する。[センサーダッシュボード](monitor.md#dashboard)を参照 |
| **Settings (Kconfig)…** / **Menuconfig** / **Open .config** | アプリケーションの設定を変更する |
| **Pin Configuration…** | ピンを設定し、コードを生成する |
| **GATT Configuration…** | BLE のサービスとキャラクタリスティックを定義し、コードを生成する |
| **Memory Map** | メモリを使っているものを確認する |
| **Partition Table** / **AI Model…** | パーティションテーブルの表示／NPU モデルのチェックと書き込み |
| **OTA Package…** | boot2 用の OTA パッケージを作成してボードに送る。[OTA パッケージ](flash.md#ota)を参照 |
| **Run Tests on Board** | ボードをリセットし、Unity テストの結果を収集する |
| **RF Test (DTM)…** / **Wi-Fi Throughput (iperf)…** / **Power…** | RF、Wi-Fi スループット、消費電力の測定 |
| **Crash Dumps…** | 以前に収集したクラッシュダンプを開く |
| **Register Reference** | 周辺機能、レジスター、フィールドを参照する |
| **Ask AI About the Last Crash** / **Connect an AI Assistant (MCP)…** | AI アシスタント |

## 設定 { #settings }

設定を開いて `ipro` を検索すると、次の項目が表示されます。

| 設定 | 説明 |
|---|---|
| `ipro.sdk.path` | 開いているフォルダーが SDK でない場合に使用する IPRO SDK フォルダー |
| `ipro.tools.base` | IDE がツールをインストールする場所。空の場合はホームフォルダーの `IPRO/tools` |
| `ipro.toolchain.prefix` | クロスコンパイルのプレフィックス。空の場合は自動検出 |
| `ipro.flashTool.path` | IntelProCube のフォルダーまたは実行ファイル。空の場合は自動検出 |
| `ipro.build.profile` | ビルドプロファイル：Debug、Release、MinSizeRel |
| `ipro.build.generator` | CMake ジェネレーター：auto、Unix Makefiles、Ninja |
| `ipro.build.memoryBudget` | ビルドが使用できる各メモリ領域の最大割合（パーセント）。例：`{ "flash": 90 }` |
| `ipro.build.failOverBudget` | メモリバジェットを超えたビルドを失敗させる |
| `ipro.board.id` | ボード。auto の場合はアプリケーションの `.config` に従う |
| `ipro.board.port` | 書き込みとモニターに使用するシリアルポート。空の場合はプローブの UART を選択 |
| `ipro.flash.baudRate` | IntelProCube のボーレート |
| `ipro.run.openMonitor` | 書き込みに成功した後でシリアルモニターを開く。デフォルトでオン |
| `ipro.monitor.baudRate` | シリアルモニターのコンソールのボーレート。デフォルトは 115200 |
| `ipro.monitor.timestamps` | モニターの各行の先頭に受信時刻を付ける |
| `ipro.monitor.filter` | この正規表現に一致するモニターの行だけを表示する |
| `ipro.monitor.logToFile` | すべてのモニターセッションの全内容を、アプリケーションの `build/logs` に保存する |
| `ipro.mcp.enabled` / `ipro.mcp.port` | IDE の外部の AI アシスタント向けの MCP サーバー。デフォルトでオン、ポート 41730 |
| `ipro.ai.assistant` | **Ask AI to Fix** などのリクエストの送り先：`ipro`（IPRO アシスタント。言語モデルが必要。デフォルト）または `claudeCode`（Claude Code アシスタント。Claude Code のログインを使い、MCP 経由で IPRO のツールを使用する） |
| `ipro.macos.probeDownloadMode` | macOS：書き込み中に IPRO Debug Probe のダウンロードストラップを保持する |
| `ipro.macos.checkQuarantine` | macOS：起動時にツールの quarantine フラグをチェックする |

## MCP ツール { #mcp-tools }

IDE の外部の AI アシスタントからは、MCP を通じて次のツールが利用できます（名前は MCP のツール名です）。内蔵の IPRO AI アシスタントも同じツール群を使用します。アシスタントの接続方法は[AI アシスタント](ai.md#mcp)を参照してください。

| ツール | 用途 |
|---|---|
| `ipro_get_target` | SDK、現在のアプリケーション、ボード、シリアルポート、環境の問題、最後のビルド結果 |
| `ipro_open_folder` | IPRO SDK のフォルダーを開く。アプリケーションのフォルダーを指定した場合は、その SDK を開いてそれを現在のアプリケーションにする |
| `ipro_list_applications` | SDK 内のすべてのアプリケーションを一覧表示する |
| `ipro_select_application` | 現在のアプリケーションを切り替える |
| `ipro_list_configurations` / `ipro_select_configuration` | 現在のアプリケーションの構成を一覧表示する／ビルド元の構成を選択する |
| `ipro_list_boards` / `ipro_select_board` | IDE が認識しているボードと使用中のボードを一覧表示する／ボードを選択する、または auto に戻す |
| `ipro_list_ports` / `ipro_select_port` | このコンピューターのシリアルポート（プローブの UART と CCI、その他）を一覧表示する／書き込み、モニター、リセットに使うポートを選択する |
| `ipro_build` | 現在のアプリケーションをビルドする。エラー、警告、メモリ使用量を返す |
| `ipro_get_build_output` | IPRO Build または IPRO Flash の最新の出力を読み取る |
| `ipro_flash` | 最新のビルドを書き込み、モニターを開く |
| `ipro_reset_board` | プローブを介してボードをリセットする |
| `ipro_open_monitor` / `ipro_close_monitor` | 使用中のポートでシリアルモニターを開く（ボードの再起動も可能）／モニターを閉じてポートを解放する |
| `ipro_read_monitor` | ボードがモニターに出力した最新の行を読み取る |
| `ipro_write_monitor` | ボードのコンソールに 1 行入力し、その後にボードが出力した内容を返す |
| `ipro_board_tests` | ボードが前回起動したファームウェアと、Unity テストの結果 |
| `ipro_get_settings` / `ipro_set_settings` | アプリケーションの Kconfig 設定を読み取る／変更する |
| `ipro_get_pins` / `ipro_set_pins` | ピン設定を読み取る／変更してコードを生成する |
| `ipro_get_gatt` / `ipro_set_gatt` | GATT サービスを読み取る／変更してコードを生成する（ドライランでは書き込まずにチェックだけを行う） |
| `ipro_memory_map` | 各メモリ領域の使用量と、サイズの大きいライブラリとオブジェクトファイル |
| `ipro_partition_table` | 書き込み時に書き込まれるパーティションテーブルと、そのチェック結果 |
| `ipro_ai_model` | NPU モデルがアプリケーションとそのパーティションテーブルに収まるかをチェックする |
| `ipro_crash_dump` | 最新のクラッシュダンプの例外とコールチェーン |
| `ipro_decode_addresses` | コードアドレスを関数、ファイル、行番号にデコードする |
| `ipro_lookup_register` | 名前またはアドレスでレジスターを検索する |

## ファイルの場所 { #file-locations }

| 場所 | 内容 |
|---|---|
| ホームフォルダーの `IPRO/tools/<tool>/<version>` | **Fix Environment** がインストールしたツール（Windows では `%USERPROFILE%\IPRO\tools`） |
| ホームフォルダーの `IPRO/SDK/<version>` | **Install SDK from GitHub…** がインストールした SDK |
| ホームフォルダーの `.ipro-ide` | IDE の設定と MCP のアクセストークン（`mcp.json`） |
| `apps/<category>/<name>/build` | アプリケーションのビルド結果（ファームウェア、ELF、マップファイル） |
| `apps/<category>/<name>/build_<configuration>` | `defconfig_<configuration>` からのビルド結果（`config_<configuration>` の場合は `build_config_<configuration>`）。`make DEFCONFIG=<file>` と同じ |
| `apps/<category>/<name>/build/build_out/<name>.xz.ota` | **OTA Package** が作成した boot2 用の OTA パッケージ（構成を選択している場合は、その構成のビルドフォルダー内） |
| `apps/<category>/<name>/build/logs` | モニターの全ログ（**Log To File** がオンの場合） |
| `apps/<category>/<name>/build/crash` | 収集したクラッシュダンプ |
| `apps/<category>/<name>/pins.yaml` | ピン設定。`app_pins.h` と `app_pins.c` はこのファイルから生成される |
| `apps/<category>/<name>/gatt.yaml` | GATT サービス。`app_gatt.h` と `app_gatt.c` はこのファイルから生成される |
| `apps/<category>/<name>/dashboard.yaml` | Sensor Dashboard のレイアウト |
