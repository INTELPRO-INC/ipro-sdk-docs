---
title: IPRO7AI Reef EVK V4.0
description: IPRO7AI Reef EVK V4.0 のオンボード機能、スイッチとジャンパー、クイックスタートとダウンロードモード、出荷時ファームウェア、IPRO6S FIN カード経由の Wi-Fi、対応サンプル、USB 識別情報、ピンマップ
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK V4.0

<span class="ipro-badge">V4.0</span>

IPRO7AI Reef EVK は、Flash と PSRAM をチップパッケージに内蔵した IPRO7AI（QFN56）を中心に構成されたボードです。OV5640 カメラコネクター、PDM デジタルマイク、ヘッドセットジャックとスピーカーアンプ、microSD ソケット、RGB LED、キー、Raspberry Pi と同じ位置とピン順の 40 ピン拡張ヘッダーを搭載しています。電源は USB-C からのみ供給され、LCD とバッテリーはありません。このページは V4.0 ボード（シルク印刷「IPRO7AI REEF EVK V4.0」）を対象としており、このサイトの手順はすべてこのボード向けに書かれています。

<figure>
  <img src="/ipro-sdk-docs/assets/images/reef-v4-top.jpg" alt="IPRO7AI Reef EVK V4.0 の表面。上端に 40 ピンヘッダー J_IO、右上に SW1、SW2 と PCB アンテナ、左端に SW7、U6 と microSD ソケット、下端に JP3、スピーカーコネクター、ヘッドセットジャック、SW8、JP2、USB-C" width="1500" height="1011" loading="lazy">
  <figcaption>IPRO7AI Reef EVK V4.0 の表面</figcaption>
</figure>

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>NPU、ISP、BLE、IEEE 802.15.4 を搭載した SoC（QFN56）</span></div>
<div><strong>2 MB + 8 MB</strong><span>パッケージ内蔵の Flash と PSRAM</span></div>
<div><strong>40 ピン</strong><span>J_IO、Raspberry Pi と同じ位置とピン順、3.3 V</span></div>
<div><strong>U6</strong><span>UART コンソール、115200 baud</span></div>
<div><strong>USB-C</strong><span>唯一の電源入力</span></div>
</div>

## オンボード機能 { #features }

| ブロック | 内容 |
|---|---|
| コア | IPRO7AI（U1、QFN56）：RISC-V RV32IMAFC、NPU、ISP、2.4 GHz 無線（BLE、IEEE 802.15.4）。32 MHz 水晶振動子（X1） |
| メモリ | パッケージ内蔵の 2 MB Flash と 8 MB PSRAM。チップ上の 256 KB OCRAM |
| アンテナ | PCB アンテナ E1（デフォルト）。0 Ω 抵抗を R2 から R1 に移すと、代わりに u.FL コネクター RF1 を使えます |
| カメラ | FPC1：24 ピン、0.5 mm ピッチの縦型 FPC コネクター。OV5640 FLEX-24 のピン配置、8 ビット DVP。カメラの 2.8 V と 1.5 V はオンボードのレギュレーターから供給されます |
| カメラ / GPIO 切り替え | SW7 は 4 個の SN74CB3Q3257 スイッチを通じて、カメラの 16 ピンを J_IO に接続します。GPIO 位置ではカメラの電源はオフです |
| 音声入力 | PDM デジタルマイク MK1。ヘッドセットのマイクはジャック J2 からアナログ入力 AIN6 と AIN7 に入ります |
| 音声出力 | IPRO7AI の GPDAC が、ヘッドホン段（TLV9061）を経由してジャック J2（3.5 mm、CTIA）を駆動し、PAM8302A D 級アンプを経由してスピーカーコネクター J_SPK（1.25 mm、2 ピン、8 Ω スピーカー用）を駆動します |
| ストレージ | microSD ソケット CARD1（プッシュプッシュ式）、4 ビット SD インターフェース。カード検出とソケット電源はそれぞれ GPIO に接続されています |
| USB | USB-C（USB1）：5 V 給電と USB 2.0 Full-Speed デバイス |
| デバッグ | U6：6 ピン、1.0 mm ピッチ（SH1.0）。コンソール UART、BOOT、RESET を備え、IPRO Debug Probe に接続します |
| キーと LED | SW1 BOOT、SW2 RESET、ユーザーキー SW3 / SW4 / SW5（サイド操作）。LED1 RGB LED（WS2812B-2020）、LED2 電源 LED（緑） |
| 拡張 | J_IO：2 × 20、2.54 mm ヘッダー。Raspberry Pi の 40 ピンヘッダーと同じ位置とピン順で、信号はすべて 3.3 V です |
| 電流測定 | SW8（PWR / MEAS）と JP2 で IPRO7AI の 3.3 V の電流を測定します |
| サイズ | 85 × 56 mm、厚さ 1.6 mm、6 層。Ø2.75 mm の取り付け穴 4 個（58 × 49 mm ピッチ）は、Raspberry Pi と同様に 40 ピンヘッダーを基準に配置されており、M2.5 スペーサーに対応します |

仕様は V4.0 の設計ファイル（回路図と部品表）に基づいています。

### スイッチとジャンパー { #jumpers }

| 部品記号 | 位置 | 機能 |
|---|---|---|
| SW7 | CAM（デフォルト） | カメラのピンは IPRO7AI に接続され、カメラの電源はオンです。カメラを使うときは常に CAM にしてください |
| | GPIO | カメラの 16 ピンは J_IO に接続されます（[ヘッダー表](#j-io)で * の付いたピン）。カメラ用レギュレーターは 2 つともオフです |
| SW8 | PWR | 通常使用：IPRO7AI の 3.3 V はボード電源から直接供給されます |
| | MEAS | 測定：IPRO7AI の 3.3 V は JP2 を経由して供給されます。JP2 には電流計または外部 3.3 V 電源を接続する必要があります |
| JP3 | ON | microSD ソケットには常に給電されます |
| | GPIO | GPIO14 でソケットの電源を切り替えます。Low または非駆動のときはオン、High のときはオフです |
| JP2 | — | 3 ピン：1 = 3V3（ボードの 3.3 V）、2 = SOC（IPRO7AI の 3.3 V）、3 = GND。SW8 が MEAS のときのみ使用します |

IPRO7AI の電流を測定するには、USB-C を外し、JP2 の 1 番ピンと 2 番ピンの間に電流計を接続し（または 2 番ピンと 3 番ピンの間に外部 3.3 V 電源を接続し）、SW8 を MEAS にスライドしてから USB-C を接続し直します。測定が終わったら USB-C を外し、SW8 を PWR に戻してから電流計を取り外します。測定値には IPRO7AI の 3.3 V ピンとそのデカップリングコンデンサー、ブートストラップのプルアップが含まれ、周辺回路は含まれません。

!!! warning "電源投入前に"
    - ボードへの給電は USB-C からのみ行ってください。J_IO の 5 V ピン（2 番、4 番ピン）は出力であり、ここからボードに給電することはできません。
    - I/O はすべて 3.3 V です。5 V の信号を接続しないでください。
    - カメラケーブルの抜き差しは USB-C を外してから行ってください。
    - SW8 は PWR のままにしてください。SW8 が MEAS のときは、JP2 に電流計または外部 3.3 V 電源を接続していない限り USB-C を接続しないでください。IPRO7AI に電源が供給されない状態で、周辺回路の 3.3 V が I/O ピンを通じて逆流します。

## クイックスタート { #quick-start }

この手順を終えると、ボード上で出荷時ファームウェア `ipro7ai_reef_demo` が動作し、コンソールで `reef selftest` に応答するようになります。ホストには RISC-V ツールチェーン（INTELPRO から入手）、IntelProCube 0.7.0.1（[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) からダウンロード）、CMake 3.15 以降、GNU make、Python 3.8 以降が必要です。[はじめに](../../get-started/index.md)を参照してください。

<div class="ipro-steps" markdown>

1. **スイッチを設定して接続する**：SW7 を CAM に、SW8 を PWR にスライドします。コンソールケーブルを U6 に接続します。3.3 V の USB-UART ケーブル（ピン配置は[デバッグコネクター U6](#debug-connector) を参照）を使うか、ピン順を反転したケーブルで IPRO Debug Probe を接続します。USB-C は最後に接続します。

    緑色の電源 LED（LED2）が点灯します。U6 からはボードに給電されません。給電は USB-C からのみ行われます。

2. **シリアルポートを確認する**：ホスト上のシリアルポートを一覧表示します。

    ```bash
    ls /dev/cu.usb*                # macOS
    ls /dev/ttyUSB* /dev/ttyACM*   # Linux
    ```

    USB-UART ケーブルは 1 つのポートとして認識されます（例：`/dev/cu.usbserial-XXXX`）。IPRO Debug Probe は 2 つのポートとして認識されます（デバイス名 `IPRO7 CMSIS_DAP`）。末尾が `02` のポートが Reef のコンソール、末尾が `04` のポートが CCI ブリッジです。Windows では「デバイス マネージャー」で `COM` 番号を確認します。

3. **出荷時ファームウェアをビルドする**：SDK のルートで実行します。

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    ビルドの最後に Flash と RAM の使用量が表示されます。イメージは `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin` です。

4. **ダウンロードモードに入る**：SW1（BOOT）を押したまま SW2（RESET）を押して離し、次に SW1 を離します。

    コンソールの出力が止まります。ほかの方法は[ダウンロードモード](#download-mode)を参照してください。IPRO Debug Probe で接続している場合は、この手順を省略できます。IntelProCube 0.7.0.1 がプローブ経由でチップをダウンロードモードにし、書き込み後に自動でリセットします。

5. **書き込む**：IntelProCube のディレクトリで実行します（Linux では `./ipro_iot_tool_linux`、Windows では `ipro_iot_tool.exe`）。

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    出力の最後が `[All Success]` の場合にのみ、書き込みは成功しています。このツールは失敗しても終了コード 0 で終了します。`--chip-variant IPRO7AI` は QFN56 の Flash ピンを選択します。

6. **起動してセルフテストを実行する**：SW2 を押し、115200 baud（8N1、フロー制御なし）でコンソールを開いて、`reef selftest` と入力します。

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    ブートログに `IPRO7AI Reef carrier demo` と `shell ready - ...` が表示され、RGB LED が青色で 1 回、呼吸するように点灯します。約 3 秒以内に `reef selftest` が次のように出力します。

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: OV5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    3 行目はカードが挿入されているかどうかで変わります。カメラがない場合、4 行目は `no sensor` になります。SW3、SW4、SW5、SW1 を押すと、LED がそれぞれ赤、緑、青、白に点灯します。

</div>

手順に慣れたら、`build_freertos.sh` でビルド、書き込み、コンソールの起動を一度に実行できます。このスクリプトはアプリケーションの構成から `--chip-variant IPRO7AI` を選択し、アプリケーション自身のボーレートでコンソールを開きます。SDK のファームウェアがすでに動作している場合は先に `reboot_dl` を送信します。最初の書き込みでは、キーでダウンロードモードに入ってください。

```bash
export IPRO_FLASH_TOOL=<ICUBE>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <ICUBE>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

このスクリプトは boot2 や mfg ペイロードを書き込めません。`ipro_ble_remote` の最初のイメージと `ipro_reef_teach` は、IntelProCube で直接書き込んでください。オプションは[ツールのコマンドライン](../../reference/tools.md)に記載されています。

## ダウンロードモード { #download-mode }

書き込みを行うには、IPRO7AI がリセット解除時に BOOT（GPIO41）を High として検出する必要があります。このとき IPRO7AI は ROM のダウンロードモードに入ります。ダウンロードモードではコンソールに何も出力されません。書き込み後は SW2 を押して通常起動します。

| 方法 | 操作 | 使用する場面 |
|---|---|---|
| キー | SW1（BOOT）を押したまま SW2（RESET）を押して離し、SW1 を離す | 常に使用可能（ファームウェアが応答しない場合も含む） |
| コンソールコマンド | コンソールで `reboot_dl` と入力 | SDK のファームウェアが動作しているとき。`build_freertos.sh flash` は自動で送信します |
| 自動ダウンロードケーブル | U6 の 5 番ピン（BOOT）と 6 番ピン（RESET）は、それぞれ 1 kΩ を介して IPRO7AI に接続されています。これらを USB-UART ケーブルの DTR と RTS に配線すると、ホストから制御できます | DTR と RTS を引き出したケーブルを使う場合 |
| IPRO Debug Probe | 末尾が `02` のプローブポートに `IPRODL_1`、続いて `IPRORST_RESET` を送信します。書き込み後は `IPRODL_0`、続いて `IPRORST_RESET` を送信します | IPRO Debug Probe を使う場合 |

Debug Probe 経由でダウンロードモードに入ります（1 行に 1 キーワード）。

```bash
python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
```

書き込み後、同じ方法で `IPRODL_0` と `IPRORST_RESET` を送信すると、ボードが通常起動します。

boot2 を使うイメージ（例：`ipro_ble_remote` の Reef 用ビルド）には `reboot_usb [code]` もあります。これは boot2 の USB ダウンロードモードで再起動します（デフォルトでは無期限に待機）。OTA パッケージが検証に失敗した場合も、boot2 はこの USB レスキューモードで停止します。

## 出荷時ファームウェア ipro7ai_reef_demo { #reef-demo }

ボード上の各ブロックには専用のシェルコマンド群があり、`help` ですべて一覧表示できます。Reef には LCD がないため、カメラはシェルから確認します。

| ブロック | シェルコマンド | 動作 |
|---|---|---|
| 状態とセルフテスト | `reef status`、`reef selftest` | ピン、キー、LED、アンプ、検出信号の状態。1 回限りのセルフテスト |
| RGB LED | `led <r> <g> <b>`、`led rainbow`、`led off` | 色（0–255）の設定、またはレインボー効果 |
| キー | `btn status`、`btn watch` | チャタリング除去後の状態と押下回数。押下 / 解放イベントのリアルタイム表示 |
| スピーカーとヘッドセット | `spk tone <hz> <ms>`、`hp` | GPDAC から正弦波を出力します。コマンドに `hp` を付けるとアンプがミュートされ、ヘッドセットのみから再生されます。`hp` 単独ではヘッドセット検出（GPIO26）を読み取ります |
| 音声入力 | `mic rec <source> <s>`、`mic play`、`mic loop` | ソースは `pdm`（オンボードマイク）または `headset`。16 kHz で PSRAM に録音（最大 10 秒）して再生するか、リアルタイムでモニターします |
| SD への録音 | `mic sdrec <source> <name> <s>` | `sd:/rec/<name>.wav` に書き込みます |
| USB マイク | `mic usb <source>` | ボードが USB-C 上の 16 kHz USB マイクになります |
| SD カード | `sd mount`、`sd ls`、`sd test`、`sd bench`、`sd power` | FatFS を `sd:` にマウントします。書き込み、読み戻し、検証。JP3 が GPIO のとき、`sd power` で GPIO14 を通じてソケットの電源を切り替えます |
| FIN カード | `fin`、`fin cycle` | ソケット内の IPRO6S FIN カードの状態。JP3 が GPIO のとき、カードの電源を再投入します |
| カメラ | `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on` | ISP チャネル 0 経由で YUV422 1280×720 の OV5640 を扱います。フレーム、フレームレート、エラーのカウンター、ASCII サムネイル、センサーのカラーバー |

アプリケーションの README にある AUX-IN 入力（`mic rec aux`）は、以前のキャリアボードのものです。V4.0 には AUX-IN ジャックはありません。

カメラの立ち上げ手順（SW7 は CAM）：

```text
cam probe        SCCB 経由でセンサー ID を読み取る
cam start        キャプチャを開始する
cam status       1 秒間隔で 2 回実行する：フレーム数は増え、エラー数は変わらない
cam bar on       カラーバーに切り替える
cam snap         ASCII サムネイルに縦の帯が表示される
cam bar off
cam snap         実際の映像
```

## Wi-Fi と RTSP カメラストリーム { #wifi-rtsp }

IPRO6S FIN カードを microSD ソケットに挿すと、Reef は SDIO 経由で Wi-Fi に接続し、カメラの MJPEG ストリームを RTSP（`rtsp://<ip>:8554/av0_0`）で配信します。

- **FIN カードのファームウェア**：IPRO6S アプリケーション `ipro6_if_wifi` を `defconfig_ipro6_sdio` でビルドしたものです。

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio   # build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin
    ```

    更新方法は [IPRO6S](../chips/ipro6s.md) のページにあります。カードが Wi-Fi に接続されていれば、Reef のコンソールで `ipro6s_ota <http url>` を実行して更新できます。

- **Reef のファームウェア**：`ipro7ai_reef_demo` を `defconfig_wifi_ipro6s` でビルドしたものです。

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # build_wifi_ipro6s/build_out/
    ```

- **スイッチ**：`fin cycle` でカードの電源を再投入できるように、JP3 を GPIO にします。

コンソールで `ipronet_up <ssid> <psk>`、続いて `rtsp_cam on` と入力し、RTSP プレーヤーで `rtsp://<ip>:8554/av0_0` を開きます。詳しい手順は [Wi-Fi と RTSP カメラストリーム](../../tutorials/wifi-rtsp.md)を参照してください。

## 対応サンプル { #examples }

次の 9 個のアプリケーション（11 構成）は Reef でビルドして実行できます。それぞれに書き込みと実行の手順を記載した[サンプルページ](../../examples/index.md#reef)があります。`ipro7ai_reef_demo`、`ipro_reef_teach`、`ipro_agora_sentino` 以外は、単に `make` を実行すると別のボード向けにビルドされるため、Reef 向けには `DEFCONFIG=` を追加してください。

| アプリケーション | ビルドコマンド（SDK のルートで実行） | コンソール | 書き込みの注意 |
|---|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `make -C apps/platform/ipro7ai_reef_demo` | 115200 | `--pt chips/ipro7/partition/partition_cfg_2M.toml` |
| `ipro7ai_reef_demo`（Wi-Fi） | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | 115200 | `ipro6_if_wifi` を実行する FIN カードが必要。JP3 は GPIO |
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `make -C apps/ai/ipro_reef_teach` | 115200 | 独自のテーブル `partition_reef_teach.toml`、`--skip-ota` と `--mfg`。[Edge AI ファームウェアの書き込み](../../teach/firmware.md)を参照 |
| [`ipro_ble_remote`](../../examples/ipro_ble_remote.md) | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | 115200 | 最初の書き込みには `--boot2` と `partition_cfg_2M_remote_ab.toml` が必要。OTA はこの A/B テーブルでのみ可能 |
| [`ipro_throughput_test`](../../examples/ipro_throughput_test.md) | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | 115200 | ボードが 2 枚必要 |
| [`ipro_le_audio_headset`](../../examples/ipro_le_audio_headset.md) | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | 115200 | — |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | 115200 | `--pt chips/ipro7/partition/partition_cfg_2M.toml` |
| `ipro7_uvc_cam`（じゃんけん） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | 115200 | 同上。モデルはファームウェアにリンクされています |
| [`ipro7_jpeg_decode`](../../examples/ipro7_jpeg_decode.md) | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | **921600** | — |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | 115200 | microSD カードが必要 |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `make -C apps/multimedia/ipro_agora_sentino` | 115200 | 先に AOSL コアを取得してください。FIN カードと Sentino のデバイストリプルが必要 |

`DEFCONFIG=` を指定したビルドは `build_<name>/build_out/` に出力されます。name はファイル名から `defconfig_` を除いたものです。たとえば `defconfig_reef` は `build_reef/` にビルドされます。

## USB 識別情報 { #usb-ids }

Reef の USB-C には IPRO7AI の USB 2.0 Full-Speed デバイスが接続されており、ホストからの見え方はファームウェアによって異なります。すべてのアプリケーションが VID `0x3896`（INTELPRO INC.）を使います。

| PID | アプリケーションとモード | ホストからの見え方 |
|---|---|---|
| `0x0705` | `ipro_reef_teach`、`image` モード | UVC カメラ + CDC シリアルポート |
| `0x0720` | `ipro_reef_teach`、`voice` モード | CDC シリアルポート |
| `0x0721` | `ipro_reef_teach`、`sensor` モード | CDC シリアルポート |
| `0x0701` | `ipro7_uvc_cam` | UVC カメラ「IPRO7 UVC Cam」 |
| `0x0704` | `ipro_ai_link` | 2 つの CDC シリアルポート（データ、コンソール） |
| `0x0003` | `ipro7ai_reef_demo`、`mic usb` | USB オーディオデバイス（マイク） |

`ipro_ble_remote`、`ipro_throughput_test`、`ipro_le_audio_headset`、`ipro7_jpeg_decode`、`ipro_agora_sentino`、および `ipro7ai_reef_demo` の `defconfig_wifi_ipro6s` ビルドは USB デバイスを使いません。USB-C はボードへの給電にのみ使われます。

## ピンマップ { #pinout }

| ブロック | ピン |
|---|---|
| UART0 コンソール | TX GPIO20、RX GPIO21（U6 の 3 / 4 番ピン、J_IO の 8 / 10 番ピン） |
| USB デバイス | D+ GPIO8、D− GPIO9 |
| カメラ DVP | データ GPIO0–7、PCLK GPIO38、VSYNC GPIO39、HREF GPIO40、XCLK GPIO22（IPRO7AI が駆動）、RESETB GPIO34、PWDN GPIO35 |
| カメラ SCCB | SIOC GPIO36、SIOD GPIO37（I2C0。プルアップはカメラモジュール側） |
| スピーカー | GPDAC GPIO23 → PAM8302A。イネーブルは GPIO25 で、High = オン、電源投入時はオフ |
| ヘッドセットジャック J2 | ヘッドホンはスピーカーと GPDAC GPIO23 を共有。マイクは AIN6（GPIO12）と AIN7（GPIO13）。挿入検出は GPIO26（GPADC） |
| PDM マイク | CLK GPIO16、DATA GPIO17 |
| RGB LED | WS2812B の DI は GPIO24。SPI0 MOSI で駆動（`pin_swap_enable = 0` が必要） |
| キー | SW1 BOOT GPIO41（プルダウン、押すと High）。SW3 GPIO10、SW4 GPIO27、SW5 GPIO11（押すと Low） |
| microSD | CLK GPIO30、CMD GPIO31、DAT0 GPIO29、DAT1 GPIO28、DAT2 GPIO33、DAT3 GPIO32。カード検出 GPIO15。ソケット電源 GPIO14（JP3 が GPIO のとき、Low = オン） |
| J_IO の I2C | SDA GPIO19、SCL GPIO18（ボード上に 4.7 kΩ プルアップ） |

microSD の CMD と DAT の信号線には外部プルアップがないため、IPRO7AI の内部プルアップを有効にしてください（SDK のボード設定で有効になっています）。GPIO14 でソケットの電源を切る前に、GPIO28–33 を Low に駆動するか入力にしてください。これらのピンはソケットにのみ接続されており、J_IO には出ていません。

### 40 ピン拡張ヘッダー J_IO { #j-io }

J_IO は 2 × 20、2.54 mm の縦型ヘッダーで、Raspberry Pi の 40 ピンヘッダーと同じ位置とピン順です。電源、グラウンド、I2C、UART は想定どおりの位置にあります。奇数ピンが内側の列、偶数ピンがボードの端側の列です。信号はすべて 3.3 V で、すべての信号ピンに ESD 保護があります。

- \* の付いたピンはカメラスイッチを経由します。SW7 が GPIO のときにのみ IPRO7AI に接続され、SW7 が CAM のときは信号がありません。
- 2 番、4 番ピンの 5 V は、ダイオードを介した USB の 5 V です。USB-C が接続されているときにのみ出力され、ここからボードに給電することはできません。
- 16 番、18 番ピン（BOOT、RESET）はデフォルトでは接続されていません。必要な場合は R92 と R93 に 0 Ω 抵抗を実装してください。
- 27 番、28 番ピンは 2 つ目の I2C バスです。SW7 が GPIO のとき、拡張ボード上の ID EEPROM の読み取りに使えます。

| ピン | 信号 | 備考 | ピン | 信号 | 備考 |
|---|---|---|---|---|---|
| 1 | 3.3 V | 電源出力 | 2 | 5 V | 出力（ダイオードを介した USB 5 V） |
| 3 | GPIO19 | I2C SDA（4.7 kΩ プルアップ） | 4 | 5 V | 出力（2 番ピンと同じ） |
| 5 | GPIO18 | I2C SCL（4.7 kΩ プルアップ） | 6 | GND | |
| 7 | GPIO27 | SW4 キー | 8 | GPIO20 | UART0 TX（コンソール） |
| 9 | GND | | 10 | GPIO21 | UART0 RX（コンソール） |
| 11 | GPIO10 | SW3 キー | 12 | GPIO0 * | |
| 13 | GPIO14 | microSD 電源制御 | 14 | GND | |
| 15 | GPIO15 | microSD カード検出 | 16 | BOOT | デフォルトでは未接続 |
| 17 | 3.3 V | 電源出力 | 18 | RESET | デフォルトでは未接続 |
| 19 | GPIO4 * | | 20 | GND | |
| 21 | GPIO5 * | | 22 | GPIO35 * | |
| 23 | GPIO7 * | | 24 | GPIO6 * | |
| 25 | GND | | 26 | GPIO34 * | |
| 27 | GPIO37 * | 2 つ目の I2C SDA | 28 | GPIO36 * | 2 つ目の I2C SCL |
| 29 | GPIO22 * | | 30 | GND | |
| 31 | GPIO39 * | | 32 | GPIO40 * | |
| 33 | GPIO38 * | | 34 | GND | |
| 35 | GPIO1 * | | 36 | GPIO11 | SW5 キー |
| 37 | NC | 未接続 | 38 | GPIO3 * | |
| 39 | GND | | 40 | GPIO2 * | |

### デバッグコネクター U6 { #debug-connector }

U6 は 6 ピン、1.0 mm ピッチのライトアングルコネクター（SH1.0）で、コンソール UART と BOOT、RESET 信号を備え、書き込みとブートログの確認に使います。コンソールは UART0 で、書き込み用の UART も兼ねています。設定は 115200 baud、8N1、フロー制御なしです（書き込み時は 921600 baud）。

| ピン | 信号 | 備考 |
|---|---|---|
| 1 | NC | 未接続 |
| 2 | GND | グラウンド |
| 3 | TX（GPIO20） | Reef からの出力（コンソール出力） |
| 4 | RX（GPIO21） | Reef への入力（コンソール入力） |
| 5 | BOOT | 1 kΩ を介して GPIO41 に接続。リセット解除時に High = ダウンロードモード |
| 6 | RESET | 1 kΩ を介して IPRO7AI のリセットピンに接続。Low = リセット |

IPRO Debug Probe の CN_UART コネクターと U6 は、両端でピン順が反転したケーブルで接続します。プローブの n 番ピンは U6 の 7 − n 番ピンにつながります（プローブの RST は RESET に、DL は BOOT に、TXD は RX に、RXD は TX に、GND は GND につながり、プローブの 3V3 は未接続のピンに当たります）。

!!! warning "ケーブルの向き"
    ストレートケーブル（1 番ピン同士を接続）は使わないでください。UART と制御信号が誤ったピンに接続され、プローブの 6 番ピンの 3.3 V が U6 の RESET に加わります。

## SDK のボードサポート { #bsp }

- **ボードの選択**：`.config` で `CONFIG_IPRO7AI_REEF=y` と `CONFIG_BOARD="IPRO7AI_REEF"` を設定します。ピン定義は `bsp/board/ipro7/ipro7ai_reef_board_config.h` にあります。同じ構成で `CONFIG_EVB=y` も設定しないでください。両方を設定すると、IPRO7 EVB 向けにビルドされます。
- **PSRAM**：ビルドは Kconfig の `select` を適用しないため、すべての Reef 用構成で `CONFIG_USE_PSRAM=y` を明示的に記述しています（PSRAM をオフのままにしている `ipro_throughput_test` の `defconfig_reef` を除く）。新しいアプリケーションは `apps/platform/ipro7ai_reef_demo/.config` のコピーから始めてください。
- **ピン定義**：コンソール、USB、カメラ、スピーカー、マイク、LED、キー、SD カードの `BOARD_*` ピンはこのページの内容と一致しています。同ファイル内の拡張ヘッダーとジャンパーに関するコメントは、以前の（V3.0）キャリアボードについての記述です。V4.0 についてはこのページを正としてください。
- **水晶振動子のトリミング**：`.config` で `CONFIG_IPRO7_XTAL_CAPCODE` を設定しない場合、ビルドは Reef 用に 95 を適用します。上書きするには `.config` に別の値を設定します（0 を指定すると起動時の値をそのまま使います）。ブートログの `[XTAL] capcode` 行に使用中の値が表示されます。
- **Flash レイアウト**：`ipro7ai_reef_demo`、`ipro7_uvc_cam`、`ipro7_jpeg_decode`、`ipro_throughput_test` の Reef 用構成は、どちらのパッケージ内蔵 Flash にも収まる 1 MB のレイアウトをリンクします。`ipro_reef_teach` と `ipro_agora_sentino` の `.config`、および `ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` の `defconfig_reef` は `CONFIG_IPRO7_FLASH_2M=y` を設定しています。1 MB レイアウトのアプリケーションで 2 MB の Flash 全体を使うには、その構成に `CONFIG_IPRO7_FLASH_2M=y` を追加します。
- **Zephyr RTOS**：本リリースには Reef 用の Zephyr ボードはありません。SoC の Kconfig には、Reef で `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` を指定すれば `ipro7_evb` のイメージを実行できると記載されていますが、この使い方は検証されていません。

## 関連ドキュメント { #documents }

- [IPRO AI Teach](../../teach/index.md)：IPRO AI Studio を使って、画像、声、センサー信号をこのボードに学習させます。
- [サンプル](../../examples/index.md#reef)：Reef で動作するアプリケーション。それぞれにビルド、書き込み、実行の手順があります。
- [ピン配置と周辺機能マッピング](../pinmux.md)、[電源と電流測定](../power.md)、[IPRO7AI](../chips/ipro7ai.md)、[IPRO6S](../chips/ipro6s.md)。
- `apps/platform/ipro7ai_reef_demo/README.md`：出荷時ファームウェアの全コマンドと、カメラのデバッグに関する注意事項。
- IPRO7AI Reef 開発キットユーザーガイド（V4.0 ボードのハードウェア、インターフェース、電源）と IPRO Debug Probe ユーザーガイド：INTELPRO から入手できます。[ドキュメント](../../documents/index.md)を参照してください。
