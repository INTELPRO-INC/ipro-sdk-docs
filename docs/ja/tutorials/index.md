---
title: "チュートリアル"
description: IPRO7AI Reef EVK 上で最初から最後まで実際に動かすハンズオンチュートリアルです。ビルドと書き込み、独自アプリケーションの作成とテストから、BLE、LE Audio、USB ウェブカメラ、IPRO6S FIN カード経由の Wi-Fi による RTSP ストリーミングまでを扱います。
migrate_from:
  - "tutorials.html#next-steps"
---

# チュートリアル

各チュートリアルは IPRO7AI Reef EVK 上で一歩ずつ進め、入力するコマンドと期待される出力を示します。ツールチェーンと IntelProCube 書き込みツールを準備するため、先に[はじめに](../get-started/index.md)を完了してください。

<div class="grid cards" markdown>

-   **[ビルドと書き込みの流れ](build-and-flash.md)**

    ---

    日々の開発ループです。`build_freertos.sh` のアクションの連結、`DEFCONFIG=` による別構成、クリーンビルド、メモリ使用量の読み方を扱います。

-   **[最初の独自アプリケーションを作る](first-own-app.md)**

    ---

    空のディレクトリから独自アプリケーションを書きます。RGB LED の点滅、キーの読み取り、シェルコマンドの追加、ログ API の使い方を扱います。

-   **[アプリケーションのテスト](testing.md)**

    ---

    コンソールでの手動確認、判定結果を出力するセルフテスト、`serial_monitor.py` と `build_freertos.sh test` による自動化、ホスト側のユニットテストを扱います。

-   **[最初の BLE アプリケーション](first-ble-app.md)**

    ---

    Reef 上で `ipro_ble_remote` を実行し、スマートフォンから GATT サービスを操作し、コードを変更して BLE OTA で更新します。

-   **[BLE スループットテスト](ble-throughput.md)**

    ---

    2 枚の Reef ボードで `ipro_throughput_test` を実行し、1M PHY と 2M PHY のスループットを測定して SDK 自身の数値と比較します。

-   **[LE Audio 入門](le-audio.md)**

    ---

    LE Audio ユニキャストヘッドセット `ipro_le_audio_headset` を実行してスマートフォンとペアリングし、キーで音量を変え、本リリースで検証済みの範囲を確認します。

-   **[USB ウェブカメラとじゃんけん](usb-webcam.md)**

    ---

    `ipro7_uvc_cam` は Reef をドライバー不要の USB ウェブカメラにします。別の構成では NPU でじゃんけんを行い、その結果を映像に描画します。

-   **[Wi-Fi と RTSP カメラストリーミング](wifi-rtsp.md)**

    ---

    microSD スロットの IPRO6S FIN カード経由で Wi-Fi に接続し、カメラ映像を RTSP でストリーミングし、FIN カードのファームウェアを更新します。

</div>

## 各チュートリアルに必要なもの { #requirements }

どのチュートリアルにも IPRO7AI Reef EVK、USB-C ケーブル、U6 に接続する IPRO Debug Probe または 3.3 V USB-UART ケーブルが必要です。そのほかに次のものが必要です。

| チュートリアル | Reef ボード | スマートフォン | カメラ | FIN カード | microSD カード | その他 |
|---|---|---|---|---|---|---|
| [ビルドと書き込みの流れ](build-and-flash.md) | 1 | — | — | — | — | — |
| [最初の独自アプリケーションを作る](first-own-app.md) | 1 | — | — | — | — | — |
| [アプリケーションのテスト](testing.md) | 1 | — | — | — | — | 自動化の部分には macOS または Linux |
| [最初の BLE アプリケーション](first-ble-app.md) | 1 | Android または iOS | 任意（写真撮影） | — | 任意（写真の保存） | BLE OTA 用に Bluetooth を搭載した macOS または Linux コンピューター |
| [BLE スループットテスト](ble-throughput.md) | 2 | — | — | — | — | ボードごとにデバッグケーブル 1 本 |
| [LE Audio 入門](le-audio.md) | 1 | LE Audio 対応の Android | — | — | — | 任意でヘッドホン（J2） |
| [USB ウェブカメラとじゃんけん](usb-webcam.md) | 1 | — | OV5640 | — | — | データ通信対応の USB-C ケーブル |
| [Wi-Fi と RTSP カメラストリーミング](wifi-rtsp.md) | 1 | — | OV5640 | 必須 | — | Wi-Fi アクセスポイント、VLC または `ffplay` をインストールしたコンピューター |

独自の AI モデルを学習させて Reef にデプロイするには、[IPRO AI Teach](../teach/index.md) を参照してください。
