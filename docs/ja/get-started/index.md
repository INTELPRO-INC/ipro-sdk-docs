---
title: "はじめに"
description: まっさらなコンピューターと IPRO7AI Reef EVK から、ボードが動作するまで。準備するハードウェアとツール、そしてコンソールが応答するまで出荷時ファームウェアをビルドして書き込む手順です。
migrate_from: []
---

# はじめに

以下のページを順に進めると、まっさらなコンピューターから、IPRO7AI Reef EVK V4.0 上で出荷時ファームウェア `ipro7ai_reef_demo` を動かし、`reef selftest` で確認するところまで到達できます。このサイトの手順はすべてこのボード向けです。IPRO7 EVB、IPRO7AI EVK、IPRO6S EVK、IPRO7 Arduino ボード向けのアプリケーションにはそれぞれのボードが必要です。INTELPRO にお問い合わせください。

## 必要なもの { #what-you-need }

| 項目 | 備考 | 入手先 |
|---|---|---|
| IPRO7AI Reef EVK V4.0 | シルク印刷「IPRO7AI REEF EVK V4.0」 | INTELPRO |
| USB-C ケーブル | ボード唯一の電源入力です。データ通信対応のケーブルを使用してください（ボードの USB デバイスポートを使うアプリケーションがあります） | ご自身で用意 |
| コンソールケーブル（いずれか） | U6 用の SH1.0 6 ピンプラグ付き 3.3 V USB-UART 変換アダプター、またはピン順が逆のケーブルで U6 に接続する IPRO Debug Probe | アダプター：ご自身で用意、Debug Probe：INTELPRO |
| ホスト | macOS または Linux（bash）では SDK のすべてのコマンドラインツールが動作します。Windows ではインストーラー、VS Code Extension、`build_freertos.ps1` を使います | — |
| RISC-V ツールチェーン | GCC 14（Windows では GCC 13.1.1）、`riscv64-unknown-elf-gcc` | macOS／Linux：INTELPRO、Windows：Online Setup がインストール |
| IntelProCube 0.7.0.1 | 書き込みツール：`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | [GitHub Release](https://github.com/INTELPRO-INC/ipro-cube/releases)。Windows では Online Setup もインストールします |
| SDK | `IPRO-SDK-V2.2.0.tar.gz` | [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) |
| オプション | OV5640 FLEX-24 カメラモジュール、microSD カード、8 Ω スピーカー（J_SPK に接続）、ヘッドホン | ご自身で用意。セルフテストのカメラ、スロット、スピーカーの項目がすべて確認できます |

コンソールケーブルの接続方法：[IPRO7AI Reef EVK：デバッグコネクター U6](../hardware/boards/reef-evk.md#debug-connector)。

!!! tip "グラフィカルな開発環境"
    IPRO Workbench（Apple シリコン搭載の macOS、Windows 11）では、ツールのセットアップ、ビルド、書き込み、シリアルモニターをひとつのウィンドウで行えます。[IPRO Workbench](../workbench/index.md) を参照してください。

## 進める順序 { #path }

<div class="grid cards" markdown>

-   :material-tools:{ .lg } **1. [開発環境の準備](environment.md)**

    ---

    SDK をダウンロードして検証し、CMake、make、Python、RISC-V ツールチェーン、IntelProCube をインストールして、1 回のビルドで環境を確認します。

-   :material-microsoft-windows:{ .lg } **2. [Windows のセットアップと VS Code](windows.md)**

    ---

    Windows のみ：Online Setup で SDK、ツール、VS Code Extension を一括でインストールし、VS Code または `build_freertos.ps1` でビルドと書き込みを行います。

-   :material-developer-board:{ .lg } **3. [最初の FreeRTOS アプリケーション](first-app-freertos.md)**

    ---

    スイッチを設定してコンソールを接続し、`ipro7ai_reef_demo` をビルド、書き込み、実行して、`reef selftest` で LED、スピーカー、SD スロット、カメラを確認します。

-   :material-usb-port:{ .lg } **4. [書き込みとシリアルコンソール](flash-and-monitor.md)**

    ---

    リファレンス：ダウンロードモードに入る 4 つの方法、IntelProCube のオプションとパーティションテーブル、boot2 と `mfg` データ、コンソール、ポートの見分け方。

-   :material-console:{ .lg } **5. [macOS／Linux のコマンドライン](command-line.md)**

    ---

    リファレンス：`make -C`、`DEFCONFIG=`、ビルドディレクトリと出力、`build_freertos.sh` のアクション、オプション、環境変数。

</div>

## 次のステップ { #next-steps }

ボードで出荷時ファームウェアが動作したら、次の 3 つのハンズオンチュートリアルに進みます。

- [ビルドと書き込みの流れ](../tutorials/build-and-flash.md)：日常的な編集、ビルド、書き込み、モニターのサイクル。
- [最初の独自アプリケーションを作る](../tutorials/first-own-app.md)：独自のアプリケーションを作成し、Reef で実行します。
- [アプリケーションのテスト](../tutorials/testing.md)：アプリケーションをホスト上とボード上でテストします。

ボードの詳しいリファレンス（スイッチ、ピン、拡張ヘッダー）は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) にあります。本リリースの Zephyr ボードは IPRO7 EVB と IPRO7AI EVK で、Reef ボードはありません。[Zephyr RTOS](../guides/zephyr.md) を参照してください。
