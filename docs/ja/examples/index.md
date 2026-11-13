---
title: "サンプル"
description: V2.3.0 の 41 個の FreeRTOS アプリケーションです。IPRO7AI Reef EVK で動作する 9 個にはそれぞれ手順ページがあり、その他は必要なボードを記載しています。
migrate_from:
  - "applications.html"
not_migrated:
  - "applications.html#ipro-ble-img-capture"
---

# サンプル

SDK には 41 個の FreeRTOS アプリケーションが同梱されています。IPRO7 / IPRO7AI 用が 38 個、IPRO6S 用が 3 個です。それぞれ `apps/` 以下の独立したディレクトリで、`.config`、`CMakeLists.txt`、`Makefile` を持っています。[IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) で動作する 9 個のアプリケーションには、ビルド、書き込み、実行の手順を記載したページがあります。その他は別のボードが必要で、[他のボード用のアプリケーション](#other-boards) に一覧を掲載しているだけです。

## Reef 向けのビルド { #overview }

ほとんどのアプリケーションのデフォルトの `.config` は別のボードを対象にしています。Reef では、`DEFCONFIG=` でアプリケーションの Reef 用設定を選択します。

```bash
make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
```

| 項目 | ルール |
|---|---|
| ビルドディレクトリ | `DEFCONFIG=defconfig_<name>` は `build_<name>/` にビルドし、`.config` は変更しません。`DEFCONFIG=` を付けない場合は `build/` にビルドします |
| イメージ | `<build directory>/build_out/<app>_IPRO7.bin`（IPRO6S アプリケーションは `_IPRO6.bin`） |
| 単純な `make` で Reef 向けにビルドされるもの | `ipro7ai_reef_demo`、`ipro_reef_teach`、`ipro_agora_sentino` のみ。その他のアプリケーションは、`DEFCONFIG=` を付けないと IPRO7 EVB または IPRO7AI EVK 向けにビルドされます |
| 書き込み | `--chipname ipro7 --chip-variant IPRO7AI`。パーティションテーブル、boot2、mfg ペイロードは各アプリケーションのページのとおり |
| コンソール | U6 の UART0：Reef 用の設定はすべて 115200 baud。例外は `ipro7_jpeg_decode`（921600） |
| 一括実行 | `./build_freertos.sh -d defconfig_reef build flash monitor ipro_throughput_test` は `--chip-variant IPRO7AI` を自動で選び、`-P` でパーティションテーブルを受け取ります。boot2 や mfg ペイロードは書き込めません（[ツールのコマンドライン](../reference/tools.md) を参照） |

ダウンロードモード、コンソールの配線、最初の書き込みは [Reef のクイックスタート](../hardware/boards/reef-evk.md#quick-start) で説明しています。

## Reef EVK のサンプル { #reef }

<!-- BEGIN generated: examples-reef -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro7ai_reef_demo`](ipro7ai_reef_demo.md) | Reef の出荷時ファームウェア：RGB LED、キー、スピーカーとヘッドセット、PDM マイクとヘッドセットマイク、microSD、OV5640 カメラごとにシェルコマンド群があります。`mic usb` でボードが USB マイクになり、`mic sdrec` で SD カードに WAV ファイルを録音します | Reef（`.config`）、Reef＋IPRO6S FIN カード（`defconfig_wifi_ipro6s`：Wi-Fi と RTSP カメラストリーミング） | UART 115200 |
| [`ipro_reef_teach`](ipro_reef_teach.md) | Reef の Edge AI ファームウェア：1 つのイメージに 3 つの Teach ツール、`image`（USB カメラ＋画像分類）、`voice`（声紋認識）、`sensor`（センサー分類）を収録し、起動時に Flash に保存されたモードで 1 つを選んで実行します。操作は IPRO AI Studio から行います。詳しい手順は [IPRO AI Teach](../teach/index.md) を参照してください | Reef（`.config`）、`image` モードには OV5640 カメラが必要 | UART 115200 |
| [`ipro_ble_remote`](ipro_ble_remote.md) | GATT リファレンス：LED、キー、環境、UART、カメラ画像、画像アップロードの各サービス。Reef 版では Reef ハードウェアサービスと BLE A/B OTA が加わります。Android デモアプリ `ipro_remote_demo.apk` が付属します。チュートリアル：[最初の BLE アプリケーション](../tutorials/first-ble-app.md) | Reef（`defconfig_reef`：WS2812、カメラ、SD カード、オーディオ、BLE A/B OTA）、`.config` と `defconfig` は IPRO7 EVB 用 | UART 115200 |
| [`ipro_throughput_test`](ipro_throughput_test.md) | 2 枚のボードによる BLE スループットテスト：1M／2M／Coded PHY、DLE、ATT MTU 247。チュートリアル：[BLE スループットテスト](../tutorials/ble-throughput.md) | Reef 2 枚（`defconfig_reef`）、`.config` は IPRO7 EVB 用 | UART 115200 |
| [`ipro_le_audio_headset`](ipro_le_audio_headset.md) | LE Audio ユニキャストヘッドセット：BAP unicast server、PACS、ASCS、CAP、CSIP、VCP。LC3 をデコードして DAC に出力します。チュートリアル：[LE Audio 入門](../tutorials/le-audio.md) | Reef（`defconfig_reef`：DAC 出力をヘッドセットジャックとスピーカーへ）、`.config`、`DAC.config`、`UAC.config` は IPRO7 EVB 用 | UART 115200 |
| [`ipro7_uvc_cam`](ipro7_uvc_cam.md) | USB ウェブカメラ：OV5640、ISP、ハードウェア MJPEG、USB Video Class。もう 1 つの Reef 構成では NPU でじゃんけんを行い、その結果を映像に描画します。チュートリアル：[USB ウェブカメラとじゃんけん](../tutorials/usb-webcam.md) | Reef（`defconfig_reef_ov5640`：ウェブカメラ、`defconfig_reef_rps`：じゃんけん）、`.config` は IPRO7 EVB と SC101IOT の組み合わせ用 | Reef：UART 115200<br>`.config`：UART 921600 |
| [`ipro7_jpeg_decode`](ipro7_jpeg_decode.md) | ソフトウェア（TJpgDec）による JPEG から RGB565／RGB888 へのデコード。フォーマット判定、内蔵テスト画像、ホストツール付き。IPRO7 の MJPEG ブロックはエンコード専用です | Reef（`defconfig_reef`）、`.config` は IPRO7AI EVK 用 | UART **921600** |
| [`ipro_ai_link`](ipro_ai_link.md) | IPRO AI Studio の「Run on board」用ボード側ファームウェア：microSD（`sd:/`）から `.inm` モデルと入力を読み込み、NPU で実行して生の出力を表示します。コンソールから手動でも操作できます | Reef（`defconfig_reef`）、`.config` は IPRO7 EVB 用 | UART 115200（USB CDC ポートでも使用可） |
| [`ipro_agora_sentino`](ipro_agora_sentino.md) | Sentino クラウド AI 音声対話：BLE によるプロビジョニング、IPRO6S FIN カード経由の Wi-Fi、MQTT ログイン、Agora RTC 音声。Sentino デバイストリプルと AOSL コアが別途必要です | Reef＋IPRO6S FIN カード（`.config`、`make` または `make BOARD=reef`）、`BOARD=evk` は IPRO7AI EVK 用（ビルドは可能、ボード上では未検証） | Reef：UART 115200 |
<!-- END generated: examples-reef -->

## 他のボード用のアプリケーション { #other-boards }

これらのアプリケーションには Reef 用の設定がなく、記載のボードが必要です。アプリケーション名は GitHub 上のソースにリンクしています。これらのボードについては INTELPRO にお問い合わせください。

### BLE { #ble }

<!-- BEGIN generated: examples-ble -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro_ble_transparent`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/bluetooth/ble/ipro_ble_transparent) | AT コマンド（USB CDC 経由）で設定する UART／BLE 透過ブリッジ | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_ble_hid_keyboard`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/bluetooth/ble/ipro_ble_hid_keyboard) | HID over GATT キーボード | IPRO7 EVB が必要 | UART 115200 |
<!-- END generated: examples-ble -->

### オーディオと音声 { #audio }

<!-- BEGIN generated: examples-audio -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro_pdm_mic_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/multimedia/ipro_pdm_mic_demo) | PDM マイクによる収音、DAC 再生、BLE 経由の LC3 ストリーミング、SMP ペアリング、PDS31 スリープとボンディング済みデバイスへの再接続。Android コンパニオンアプリのソースは `tools/android/IproMicDemo/` にあります。Reef では `ipro7ai_reef_demo` の `mic` コマンドを使用します | IPRO7 EVB（`.config`）または IPRO7AI EVK（`make BOARD=evk`）が必要 | EVB：UART 115200<br>EVK：UART 921600 |
<!-- END generated: examples-audio -->

### プラットフォームとボード { #platform }

<!-- BEGIN generated: examples-platform -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro7_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7_demo) | チップ全体のリファレンス：PWM、SPI、I2S、LCD、オーディオ ADC／DAC、USB デバイス（CDC、HID、MSC、UAC、UVC）、ファイルシステム、TRNG、DSP など。それぞれにシェルコマンドがあります | IPRO7 EVB が必要。`defconfig_boot2_nopsram`、`defconfig_boot2_ota`、`defconfig_nist_fulltest`、`defconfig_security_cert` もあります | UART 115200 |
| [`ipro7ai_evk_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_evk_demo) | IPRO7AI EVK のブリングアップ：LCD、カメラ、マイク、スピーカー、SD カード。`config_bt` で BLE と LE Audio が加わります | IPRO7AI EVK が必要 | `.config`：UART 921600<br>`config_*`：UART 115200 |
| [`ipro7ai_evk_launcher`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_evk_launcher) | カメラ、LCD、マイク、スピーカーを 1 つのイメージに統合し、NPU で認識したハンドジェスチャーでページを切り替えます | IPRO7AI EVK が必要 | UART 921600 |
| [`ipro7ai_sensor_tag_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_sensor_tag_demo) | 6 軸 IMU、燃料ゲージ、ボタンを読み取り、LED とブザーを制御します。ボード自身の USB から毎秒 20 行の `名前:値` を出力し、IPRO Workbench 0.2.0 のセンサーダッシュボードが `dashboard.yaml` に従って表示します。書き込みはボードの USB から `tools/ipro_dl.py` で行います | IPRO7AI Sensor Tag が必要 | ボードの USB（CDC） |
<!-- END generated: examples-platform -->

### AI と画像認識 { #ai-vision }

<!-- BEGIN generated: examples-ai-vision -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro7ai_evk_person_detect`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro7ai_evk_person_detect) | カメラのプレビューを LCD に表示し、NPU で実行した YOLOv8 による人物／ペットの枠を重ねます | IPRO7AI EVK が必要 | UART 115200 |
| [`ipro7ai_evk_rps`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro7ai_evk_rps) | NPU 上の int8 CNN とじゃんけん。モデルと学習スクリプト付き。Reef での同じゲームは `ipro7_uvc_cam` の `defconfig_reef_rps` です | IPRO7AI EVK が必要 | UART 921600 |
| [`ipro_speaker_recog`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro_speaker_recog) | NPU による話者認識。モデルは mfg パーティションに格納します。Reef での話者認識は `ipro_reef_teach` の `voice` モードです | IPRO7 EVB が必要 | UART 921600 |
<!-- END generated: examples-ai-vision -->

### ネットワークと IPRO6S { #networking }

<!-- BEGIN generated: examples-networking -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro7_sdio_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7_sdio_wifi) | IPRO7 を SDIO ホスト、IPRO6S を Wi-Fi 無線として使用し、lwIP ネットワークインターフェース `iproeth0` と DHCP を提供します。Reef での同じ機能は `ipro7ai_reef_demo` の `defconfig_wifi_ipro6s` です | IPRO7 EVB と IPRO6S が必要 | UART 115200 |
| [`ipro6_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro6_demo) | シェル付きの IPRO6S Wi-Fi station／soft-AP。`defconfig_ipro6_lpwifi` で DTIM 省電力が加わり、`defconfig_ipro6_lp` は低消費電力のデモです | IPRO6S EVK が必要（[IPRO6S](../hardware/chips/ipro6s.md) を参照） | UART 115200 |
| [`ipro6_if_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro6_if_wifi) | SDIO（`defconfig_ipro6_sdio`。Reef の FIN カードのファームウェアでもあります）または USB（`defconfig_ipro6_usb`）でホストに接続する IPRO6S Wi-Fi ブリッジ | IPRO6S EVK、FIN カード（`defconfig_ipro6_sdio`。`--chipname ipro6` で書き込み。[IPRO6S](../hardware/chips/ipro6s.md) を参照） | UART 115200 |
| [`ipro6_fmac`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro6_fmac) | Linux cfg80211 ホスト向けの FullMAC ファームウェア（`defconfig_ipro6_fmac`）とその Flash ローダー（`defconfig_ipro6_fmac_loader`）。Linux ドライバーは SDK に含まれません | IPRO6S EVK が必要 | UART 115200 |
<!-- END generated: examples-networking -->

IPRO6S アプリケーションは `--chipname ipro6` で書き込みます。ビルドと設定は [IPRO6S](../hardware/chips/ipro6s.md) のページにあります。

### テストと立ち上げ用のプログラム { #test-apps }

<!-- BEGIN generated: examples-test-apps -->
| アプリケーション | 用途 | ボードと設定 | コンソール |
|---|---|---|---|
| [`ipro_unit_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_unit_test) | HAL と共通コンポーネントのユニットテスト。最後に `ALL TESTS PASSED` または `SOME TESTS FAILED` を表示します | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_ai_bench`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_ai_bench) | モデル全体の推論時間の NPU と CPU での比較 | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_npu_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_npu_yolo) | NPU による YOLOv8 の人物／ペット検出 | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_tflm_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_tflm_test) | NMSIS-NN カーネルを使用した TensorFlow Lite Micro のモデルベンチマーク | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_tflm_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_tflm_yolo) | TensorFlow Lite Micro による CPU 上での YOLOv8 | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_nmsis_nn_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_nmsis_nn_test) | NMSIS-NN 演算子のテスト | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_tinymaix_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_tinymaix_demo) | TinyMaix INT8 MNIST 推論（`nn_info`、`nn_run`、`nn_benchmark`） | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_gh7007_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_gh7007_test) | GH7007 5 インチ SPI LCD のブリングアップ | IPRO7 EVB が必要 | USB CDC |
| [`ipro_gh7007_video`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_gh7007_video) | SD カードの動画を GH7007 パネルで再生します | IPRO7 EVB が必要 | USB CDC |
| [`ipro_epd_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_epd_test) | GDEY0213F52 2.13 インチ電子ペーパーのブリングアップ | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_epd_el036`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_epd_el036) | EL036MF1 電子ペーパーのブリングアップ | IPRO7 EVB が必要 | UART 921600 |
| [`kw307_radar_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/kw307_radar_test) | UART 接続の KW307 24 GHz レーダーモジュール | IPRO7AI EVK が必要 | UART 115200 |
| [`mpu6500_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/mpu6500_test) | I2C 接続の MPU-6500 IMU（`mpu_init`、`mpu_read`、`mpu_stream`） | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_enc28j60_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_enc28j60_test) | ENC28J60 SPI イーサネットのブリングアップ。生フレームを送受信します | IPRO7 Arduino ボードが必要 | USB CDC |
| [`ipro_pio_sdh_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_pio_sdh_test) | ソフトウェア（PIO）SD ホストとハードウェア SDH を同時にマウントしたファイルシステムテスト | IPRO7 EVB が必要 | USB CDC |
| [`ipro_sdio_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_sdio_probe) | SDIO ホストの基本テスト | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_atbm_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_atbm_probe) | ATBM6162 SDIO Wi-Fi モジュールのブリングアッププローブ | IPRO7 EVB が必要 | UART 115200 |
| [`ipro_lp_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_lp_test) | PDS31 への移行と復帰、RTC ウェイクアップのテスト（`lp` コマンド） | IPRO7 EVB が必要 | UART 115200 |
<!-- END generated: examples-test-apps -->

## 次のステップ { #next-steps }

- [ビルドと書き込みの流れ](../tutorials/build-and-flash.md)：Reef でのビルド、書き込み、コンソール表示までの一連の流れ。
- [最初の独自アプリケーションを作る](../tutorials/first-own-app.md)：Reef の `.config` から新しいアプリケーションを始めます。
- [ビルドシステムと設定](../guides/build-system.md)：`DEFCONFIG=`、`BOARD=`、設定ファイル。
- [Zephyr RTOS](../guides/zephyr.md)：`zephyr/samples/` にある Zephyr サンプル（本リリースには Reef 用の Zephyr ボードはありません）。
