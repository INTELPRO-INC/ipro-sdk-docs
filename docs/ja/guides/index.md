---
title: "開発ガイド"
description: 機能分野ごとの IPRO SDK 開発ガイド。アーキテクチャ、ビルド、BLE、オーディオ、カメラ、AI、ネットワーク、Zephyr、Thread、低消費電力、OTA、VS Code を扱い、IPRO7AI Reef EVK でのハンズオン手順を含みます
migrate_from: []
---

# 開発ガイド

機能分野ごとに、SDK が提供するもの、それを有効にする `CONFIG_*` キー、IPRO7AI Reef EVK でのハンズオン手順をまとめています。SDK を初めて使う場合は、まず[最初の独自アプリケーションを作る](../tutorials/first-own-app.md)で独自のアプリケーションをビルドしてください。

<div class="grid cards" markdown>

-   :material-layers-triple:{ .lg } **[システムアーキテクチャ](architecture.md)**

    ---

    レイヤー構成、FreeRTOS と Zephyr の 2 つの経路、コンポーネント、ディレクトリ構成と BSP を、出荷時ファームウェアに沿って説明します。

-   :material-hammer-wrench:{ .lg } **[ビルドシステムと設定](build-system.md)**

    ---

    ビルドの流れ、`.config` と `autoconf.h`、Reef 用の構成、メモリレイアウト、新しいアプリケーションの作成。

-   :material-bluetooth:{ .lg } **[BLE 開発](ble.md)**

    ---

    IPRO7 BLE コントローラー上の Zephyr v4.4.0 ホスト。アーカイブの選択、初期化の順序、Reef での GATT。

-   :material-headphones:{ .lg } **[オーディオと LE Audio](audio.md)**

    ---

    PDM マイクとヘッドセットマイク、スピーカーとヘッドホン、USB マイク、SD カードへの録音、LE Audio と LC3。

-   :material-camera:{ .lg } **[カメラと画像処理](camera.md)**

    ---

    Reef の OV5640 カメラ。DVP、ISP、ハードウェア MJPEG、USB ウェブカメラ、RTSP、ソフトウェアによる JPEG デコード。

-   :material-brain:{ .lg } **[AI と NPU](ai-npu.md)**

    ---

    ビルド済みの推論ランタイム、モデルの格納と読み込み、Reef の AI アプリケーション。

-   :material-school:{ .lg } **[IPRO AI Teach](../teach/index.md)**

    ---

    画像認識、声紋認識、センサー認識を 1 つの Reef ファームウェアで実現します。IPRO AI Studio からデータの収集、学習、デプロイを行います。

-   :material-lan:{ .lg } **[ネットワーク](networking.md)**

    ---

    lwIP と mbedTLS、SDIO 接続の IPRO6S FIN カードによる Reef の Wi-Fi、RMII イーサネット。

-   :material-cube-outline:{ .lg } **[Zephyr RTOS](zephyr.md)**

    ---

    Zephyr v4.4.0 モジュール、`ipro7_evb` と `ipro7ai_evk` ボード、west によるビルドと書き込み。

-   :material-access-point-network:{ .lg } **[Thread と Matter](thread-matter.md)**

    ---

    Zephyr 上の IEEE 802.15.4 と OpenThread、Matter の対応状況。

-   :material-battery-charging:{ .lg } **[低消費電力](low-power.md)**

    ---

    WFI、PDS、HBN、低消費電力フレームワーク、スリープを使う BLE、Reef での電流測定。

-   :material-update:{ .lg } **[OTA アップデート](ota.md)**

    ---

    boot2 の OTA パッケージと A/B パーティション、BLE による Reef の更新、Wi-Fi による FIN カードの更新、Zephyr での MCUboot。

-   :material-microsoft-visual-studio-code:{ .lg } **[VS Code Extension](vscode.md)**

    ---

    SDK V2.2.1 に対応する Extension 3.3.0。ビルド、Reef への書き込み、シリアルモニター、メモリ解析。

</div>
