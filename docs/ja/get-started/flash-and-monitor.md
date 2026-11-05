---
title: "書き込みとシリアルコンソール"
description: IPRO7AI Reef EVK の書き込みとコンソールのリファレンスです。ダウンロードモードに入る 4 つの方法、IntelProCube のオプションとパーティションテーブル、boot2 と mfg データ、build_freertos.sh flash、コンソール、シリアルポートの見分け方を扱います。
migrate_from:
  - "getting-started.html#flashing"
  - "getting-started.html#serial-monitor"
  - "tools-debugging.html#flash-tool"
  - "tools-debugging.html#serial-monitor"
---

# 書き込みとシリアルコンソール

FreeRTOS アプリケーションは IntelProCube のコマンドラインツールで UART0 経由で書き込み、コンソールも同じ UART で動作します。IPRO7AI Reef EVK では、どちらもデバッグコネクター U6 を経由します。このページでは、Reef に書き込むすべての方法、各アプリケーションに必要なパーティションテーブルと追加のイメージ、コンソールの開き方、シリアルポートの見分け方を説明します。初めて実行する場合は、[最初の FreeRTOS アプリケーション](first-app-freertos.md) に従ってください。

## 前提条件 { #prerequisites }

- IntelProCube v0.6.3：`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、または `ipro_iot_tool.exe`。[開発環境の準備](environment.md#intelprocube) を参照してください。
- ビルド済みのイメージ：`apps/<category>/<app>/build/build_out/<app>_IPRO7.bin`。`DEFCONFIG=defconfig_<name>` でビルドした場合は `build_<name>/build_out/` にあります。
- U6 に接続したコンソールケーブル。[スイッチの設定とボードの接続](first-app-freertos.md#connect) を参照してください。ポートは `/dev/cu.usbserial-XXXX`（macOS）、`/dev/ttyUSB0`（Linux）、`COM5`（Windows）と表記します。

## 書き込みツール { #flash-tool }

コマンドラインツールは IntelProCube のディレクトリで実行してください。チップ設定を `chips/` から読み込み、`--pt chips/...` などの相対パスもそこを基準に解決されます。Reef で使うオプションは次のとおりです：

| オプション | Reef での値 | 意味 |
|---|---|---|
| `--chipname` | `ipro7` | IPRO7 と IPRO7AI |
| `--chip-variant` | `IPRO7AI` | Flash ピンの設定：`IPRO7AI` は `0x9`（Reef の QFN56）、`IPRO7` は `0x2`。ツールはこれを `<IntelProCube>/chips/ipro7/eflash_loader/eflash_loader_cfg.ini` に書き込みます |
| `--port` | コンソールポート | U6 に接続したアダプター、または Debug Probe の末尾が `02` のポート |
| `--baudrate` | `921600` | 書き込み速度。アプリケーションのコンソールのボーレートとは無関係です |
| `--firmware` | アプリケーションの `.bin` | ビルドで生成されたイメージ |
| `--pt` | パーティションテーブル | `.toml` のパス、または `chips/ipro7/partition/` 以下のファイル名。[パーティションテーブル](#partition-tables) を参照してください |
| `--boot2` | boot2 イメージ | boot2 を使うアプリケーション（`ipro_ble_remote`）用。[ipro_ble_remote の初回書き込み](#boot2-ab) を参照してください |
| `--mfg` | `mfg` パーティションのデータ | AI モデルと Teach モードのデータ（`ipro_reef_teach`）。[ipro_reef_teach](#mfg) を参照してください |
| `--skip-ota` | — | OTA ファイルの生成をスキップします。`ipro_reef_teach` 独自のテーブルで使います |

`--help` ですべてのオプションが表示されます。

!!! warning "出力で判断してください"
    ツールは書き込みに失敗しても終了コード 0 で終了します。最後に `[All Success]` の行が表示された場合のみ成功です。

## ダウンロードモードに入る { #download-mode }

書き込みの前に、IPRO7AI をブート ROM のダウンロードモードにする必要があります。その後、次にリセットするまでコンソールには何も表示されません。

| 方法 | 操作 | 使用する場面 |
|---|---|---|
| ボタン | **SW1 (BOOT)** を押したまま **SW2 (RESET)** を押して離し、SW1 を離す | 常に使用可能。ファームウェアがハングしている場合やシェルがない場合にも使えます |
| `reboot_dl` | コンソールで `reboot_dl` と入力すると、`reboot to download mode` と表示される | ボードでシェル付きの SDK ファームウェアが動作している場合。`build_freertos.sh flash` はこの方法を使います |
| 自動ダウンロードケーブル | アダプターの DTR を U6 のピン 5（BOOT）、RTS をピン 6（RESET）に接続する。ボード上でそれぞれ 1 kΩ を介して GPIO41 とリセットピンにつながるため、このケーブルならボタンを使わずにダウンロードモードに入れる | DTR と RTS を備えたアダプター |
| IPRO Debug Probe | プローブの末尾が `02` のポートで制御キーワードを送信する（下記参照） | Debug Probe が U6 に接続されている場合 |

Debug Probe でダウンロードモードに入る手順（macOS の例、SDK ルートで実行）：

<div class="ipro-steps" markdown>

1. **BOOT を有効にしてリセットします：** `IPRODL_1` を送信してから、`IPRORST_RESET` を送信します。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    各コマンドは `[serial_monitor] Sent: …` と `[serial_monitor] TIMEOUT after 1s`（`--wait-for` を指定しない場合の通常の終わり方）を表示し、その後コンソールには何も表示されなくなります。

2. **書き込みます：** BOOT を有効にしたまま、同じ `02` ポートで [書き込み手順](#flashing) を実行します。

3. **BOOT を解除してリセットします：** `IPRODL_0` と `IPRORST_RESET` を送信すると、ボードが新しいファームウェアで起動します。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 3
    ```

</div>

## 書き込み手順 { #flashing }

<div class="ipro-steps" markdown>

1. **シリアルポートを解放します：** コンソールポートを開いているターミナルプログラムをすべて閉じます。

2. **ダウンロードモードに入ります：** [ダウンロードモードに入る](#download-mode) のいずれかの方法を使います。コンソールには何も表示されなくなります。

3. **書き込みます**（IntelProCube のディレクトリで実行）。例は `ipro7ai_reef_demo` です。その他のアプリケーションでは、[パーティションテーブル](#partition-tables) に従って `--pt` を変更し、オプションを追加します。

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    出力は今回の実行の設定から始まり、検証で終わります（抜粋、タイムスタンプは省略）：

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    [...] - Firmware is <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

4. **リセットしてコンソールを開きます：** SW2 (RESET) を押して新しいファームウェアを起動し、アプリケーションのボーレートで [コンソール](#serial-monitor) を開きます。

</div>

## パーティションテーブル { #partition-tables }

パーティションテーブルは、ファームウェア、`mfg` データ（AI モデル）、その他のデータを Flash 上に配置します。IntelProCube には、`<IntelProCube>/chips/ipro7/partition/` に `partition_cfg_2M.toml` などの汎用テーブルが付属しています。特別なレイアウトが必要なアプリケーションは、アプリケーションディレクトリに独自の `.toml` を持っています。

| アプリケーション（Reef 用の設定） | `--pt` | その他のオプション |
|---|---|---|
| `ipro7ai_reef_demo`（`.config`、`defconfig_wifi_ipro6s`） | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro7_uvc_cam`（`defconfig_reef_ov5640`、`defconfig_reef_rps`） | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro_ble_remote`（`defconfig_reef`） | `<SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml` | 初回の書き込み時は `--boot2`。[次のセクション](#boot2-ab) を参照してください |
| `ipro_reef_teach`（`.config`） | `<SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml` | `--skip-ota`。初回の書き込み時は `--mfg` も指定します。[ipro_reef_teach](#mfg) を参照してください |
| その他の Reef アプリケーション | アプリケーションの README のとおり | — |

`ipro7ai_reef_demo` はデフォルトで 1 MB の Flash レイアウトでリンクされ、どちらのパッケージ内 Flash 部品にも収まります。起動ログに JEDEC `0xEF4015`（2 MB）と表示された場合は、`.config` に `CONFIG_IPRO7_FLASH_2M=y` を追加すると、リンカーが Flash 全体を使えるようになります。

## ipro_ble_remote の初回書き込み（boot2 と A/B テーブル） { #boot2-ab }

`ipro_ble_remote` の Reef 用設定は BLE OTA に対応しており、boot2 と A、B の 2 つのファームウェアスロットが必要です。最初に有線で書き込むときは、boot2 とアプリケーション独自のテーブルを一緒に書き込みます：

<div class="ipro-steps" markdown>

1. **ビルドします：**

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    イメージは `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin` です。

2. **ダウンロードモードに入って書き込みます。** boot2 イメージは SDK ではなく IntelProCube に付属しています。

    ```bash
    cd <IntelProCube>
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
        --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
        --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
    ```

    出力は `[All Success]` で終わります。

3. **確認します：** SW2 を押します。115200 baud のコンソールに boot2 のバナー `[BOOT2] IPRO7 Boot2 v0.5.2` が表示され、続いてアプリケーションが `[BLE] Advertising: IPRO-Remote` を出力します。

</div>

!!! warning "partition_cfg_2M.toml のまま OTA を行わないでください"
    `ipro_ble_remote` を標準の `partition_cfg_2M.toml` で Reef に書き込んだ場合、OTA アップデートは boot2 が起動しないスロット（0x12A000）に書き込まれます。OTA を行う場合は、必ず上記のとおり boot2 と `partition_cfg_2M_remote_ab.toml` で書き込んでください。OTA の手順：[OTA アップデート](../guides/ota.md)。

## ipro_reef_teach（mfg データ） { #mfg }

Edge AI ファームウェア `ipro_reef_teach` は独自のパーティションテーブルを使い、その `mfg` パーティションにモード設定と声紋モデルが格納されます。初回の書き込みでは `mfg` データも書き込みます：

```bash
make -C apps/ai/ipro_reef_teach
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 --skip-ota \
    --pt <SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml \
    --firmware <SDK>/apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin \
    --mfg <SDK>/reef_teach_mfg.bin
```

リセット後、コンソール（115200）に `RTCH:   mode: image …` と表示され、USB-C に USB カメラとシリアルポート（`3896:0705`）が現れます。ファームウェアだけを更新する場合は `--mfg` を省きます。モードとモデルはそのまま残ります。モードの切り替えと IPRO AI Studio の使い方：[IPRO AI Teach](../teach/firmware.md)。

## build_freertos.sh での書き込み { #build-script }

macOS と Linux では、`build_freertos.sh` の `flash` アクションは次の順序で動作します：

1. `build/` から、`-d defconfig_<name>` を指定した場合は `build_<name>/` からイメージを探します。見つからない場合は `Run 'build' first.` と表示して停止します。
2. ツールを探します：`IPRO_FLASH_TOOL`、未設定の場合は `PATH` 上の `ipro_iot_tool_macos` / `ipro_iot_tool_linux`。
3. ポートを探します：`-p`、指定がなければ `IPRO_SERIAL_PORT`、それもなければ接続されている唯一の `/dev/cu.usbmodem*`、`/dev/cu.usbserial*`、`/dev/ttyACM*`、`/dev/ttyUSB*`。
4. アプリケーションのコンソールのボーレート（`CONFIG_PLATFORM_UART_BAUDRATE`、未設定の場合は 115200）で `reboot_dl` を送信し、2 秒待ちます。
5. `<tool> --chipname ipro7 --chip-variant <variant> --port <port> --firmware <bin> --baudrate 921600 [--pt <table>]` を実行します。バリアント：`-c`、指定がなければ `IPRO_CHIP_VARIANT`、それもなければ設定から決定（Reef の設定では `IPRO7AI`）。テーブル：`-P`、指定がなければ `IPRO_FLASH_PT`、それもなければ `--pt` なし。
6. 出力に `[All Success]` が含まれていれば `✓ Flash succeeded`、含まれていなければ `✗ Flash failed` を表示します。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

`-P` には `.toml` のフルパスを指定してください。スクリプトはツールを IntelProCube のディレクトリではなく、カレントディレクトリで実行します。

!!! note "スクリプトでできないこと"
    - `--boot2`、`--mfg`、`--skip-ota` を渡せません。`ipro_ble_remote` の初回書き込みと `ipro_reef_teach` の `mfg` データは、ツールを直接実行して書き込みます。
    - `--chipname` は `ipro7` に固定されているため、IPRO6S のイメージは書き込めません。
    - シェルのないファームウェアやハングしたファームウェアは `reboot_dl` を受け付けません。先にボタンでダウンロードモードに入ってください。
    - `flash` はビルドを行いません。`build` と `flash` を別々に実行する場合は、両方に同じ `-d` を指定してください。

## シリアルコンソール { #serial-monitor }

コンソールは UART0（GPIO20 TX / GPIO21 RX、U6 のピン 3 / 4）、8N1、フロー制御なしです。ボーレートはアプリケーションの設定の `CONFIG_PLATFORM_UART_BAUDRATE` で決まり、未設定の場合は 115200 です：

| ボーレート | Reef 用の設定 |
|---|---|
| 115200 | `ipro7ai_reef_demo`（両方）、`ipro_reef_teach`、`ipro_ble_remote`、`ipro_throughput_test`、`ipro_le_audio_headset`、`ipro7_uvc_cam`（Reef 用の 2 つの設定）、`ipro_ai_link`、`ipro_agora_sentino` |
| 921600 | `ipro7_jpeg_decode`（`defconfig_reef`） |

設定ファイルを確認するには、次を実行します（何も表示されなければ未設定、つまり 115200 です）：

```bash
grep CONFIG_PLATFORM_UART_BAUDRATE apps/multimedia/ipro7_jpeg_decode/defconfig_reef
```

### 対話型ターミナル { #terminal }

シェルコマンドを入力するには、対話型のターミナルプログラムを使います：

=== "macOS"

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    終了するには、++ctrl+a++、++k++ を押し、`y` と答えます。`minicom` や `picocom`（Homebrew で入手可能）も使えます。

=== "Linux"

    ```bash
    picocom -b 115200 /dev/ttyUSB0
    ```

    終了するには、++ctrl+a++、++ctrl+x++ を押します。`minicom -D /dev/ttyUSB0 -b 115200` や `screen` も使えます。

=== "Windows"

    PuTTY：Connection type を **Serial**、Serial line を `COM5`、Speed を `115200` に設定し、**Open** をクリックします。Tera Term や VS Code Extension の `IPRO: Serial Monitor` も使えます。

書き込みの前にターミナルプログラムを閉じてください。開いたままだと、ツールがポートを開けません。

### tools/serial_monitor.py { #serial-monitor-py }

スクリプトや自動化に使う、SDK の非対話型コンソールツールです（macOS／Linux。Python 標準ライブラリの termios のみを使い、pyserial は不要）。ポートを開き、必要に応じて 1 行を送信してから、タイムアウトするかパターンに一致するまで読み取ります。

```text
python3 tools/serial_monitor.py <port> [--baud 115200] [--timeout 30] [--send CMD] [--wait-for REGEX] [--log FILE]
```

| オプション | 意味 |
|---|---|
| `--baud` | ボーレート。デフォルトは 115200 |
| `--timeout` | 読み取る秒数。デフォルトは 30。`0` を指定すると ++ctrl+c++ まで読み取り |
| `--send` | 読み取りの前に送信する 1 行（CR LF を付加） |
| `--wait-for` | この正規表現に一致したら停止 |
| `--log` | 生の出力をファイルにも保存 |

| 終了コード | 意味 |
|---|---|
| 0 | `--wait-for` に一致したテキストに `PASSED` が含まれる |
| 1 | 一致したテキストに `PASSED` が含まれない |
| 2 | 一致しないままタイムアウト（`--wait-for` を指定しない場合は常に 2） |
| 3 | ポートのオープンまたは送信に失敗 |

```bash
# コマンドを送信して 10 秒間読み取る
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# 再起動してシェルの準備完了を待ち、ログを保存する
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot --wait-for "shell ready" --timeout 15 --log boot.log
```

### macOS のシリアルポート { #macos-cu }

macOS では、シリアルポートごとに `/dev/cu.*` と `/dev/tty.*` の 2 つの名前があります。常に `/dev/cu.*` を使ってください。`/dev/tty.*` はキャリア検出を待つため、何も出力されないままハングします。

## ポートの見分け方 { #ports }

| 接続 | macOS | Linux | Windows |
|---|---|---|---|
| U6 に接続した USB-UART 変換アダプター | `/dev/cu.usbserial-XXXX`（アダプターによって異なる） | 通常は `/dev/ttyUSB0` | デバイス マネージャーに新しい COM ポートが現れる |
| IPRO Debug Probe | `/dev/cu.usbmodem…` ポートが 2 つ。末尾が `02` のものがコンソール（UART ブリッジ）、`04` が CCI ブリッジ | `/dev/ttyACM*` ポートが 2 つ | COM ポートが 2 つ |

IPRO Debug Probe は、USB 上では `IPRO7 CMSIS_DAP` として認識されます。Linux と Windows で 2 つのポートを見分けるには、それぞれを 115200 で開いて SW2 を押します。起動メッセージが表示される方がコンソールです。

Reef の USB-C はコンソールではありません。一部のアプリケーションでは、ボードが USB-C 上で INTELPRO の VID `0x3896` を持つ USB デバイスとして認識されます：

| アプリケーション | VID:PID | ホストから見えるもの |
|---|---|---|
| `ipro_reef_teach`、画像モード | `3896:0705` | USB カメラとシリアルポート（ブラウザーでの名前は「IPRO7 UVC Cam」） |
| `ipro_reef_teach`、音声モード | `3896:0720` | シリアルポート（CDC-ACM） |
| `ipro_reef_teach`、センサーモード | `3896:0721` | シリアルポート（CDC-ACM） |
| `ipro7_uvc_cam` | `3896:0701` | USB カメラ |
| `ipro_ai_link` | `3896:0704` | シリアルポート（CDC） |
| `mic usb` 実行中の `ipro7ai_reef_demo` | `3896:0003` | USB マイク（UAC） |
| `ipro_agora_sentino` | `3896:0138`、`3896:0104` | USB ネットワークインターフェース（NCM）、シリアルポート（CDC） |
| `ipro_le_audio_headset` | `3896:0001` | USB オーディオ（UAC、テスト用 PID） |

ホストで USB デバイスを一覧表示するには、macOS では `system_profiler SPUSBDataType`、Linux では `lsusb`（例：`ID 3896:0705`）を使います。Windows では、デバイス マネージャーでデバイスのプロパティ → **詳細** → **ハードウェア ID** を開きます（例：`USB\VID_3896&PID_0705`）。

## 動作確認 { #verify }

- 書き込み出力の最後の行が `[All Success]` になっています。
- SW2 を押すと、アプリケーションのボーレートでコンソールに起動メッセージが表示されます。シェルのあるアプリケーションでは、++enter++ を押すと `ipro />` が表示され、`help` でコマンドの一覧が表示されます。
- USB を使うアプリケーションは、上の表の VID:PID でホストに認識されます。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| ツールが `[All Success]` を表示せずにハンドシェイクで止まる | ボードがダウンロードモードになっていない、またはターミナルプログラムがポートを使用している | ターミナルを閉じ、ボタンでダウンロードモードに入ってから再試行します |
| `flash jedec id: 00000000` と `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` が `IPRO7AI` でないため、Flash ピンが誤っている | `--chip-variant IPRO7AI` を追加します |
| ツールがパーティションテーブルや boot2 ファイルを見つけられない | 相対パスが IntelProCube のディレクトリを基準に解決されていない | 先に `cd <IntelProCube>` を実行します。SDK 内のファイルはフルパスで指定します |
| `✗ Flash tool not found: ipro_iot_tool_macos` | `IPRO_FLASH_TOOL` が未設定で、ツールが `PATH` にない | `export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` を実行します |
| `✗ Binary not found: …` と `Run 'build' first.` | `flash` はビルドを行わない、またはビルド時に使った `-d` が指定されていない | `flash` の前に `build` を追加します。同じ `-d` を追加します |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | USB シリアルポートが複数ある（Debug Probe だけで 2 つ） | `-p` または `IPRO_SERIAL_PORT` でコンソールポートを指定します |
| `No serial port found: pass -p PORT or set IPRO_SERIAL_PORT` | USB シリアルポートが検出されない | アダプターとそのドライバーを確認します。[開発環境の準備](environment.md#usb-serial) を参照してください |
| 書き込みは成功したが、リセット後もコンソールに何も表示されない | ダウンロードモードのまま（DTR またはプローブが BOOT を保持している）、ボーレートの誤り、または RX と TX が逆 | BOOT を解除し（プローブに `IPRODL_0` を送信）、SW2 を押します。ボーレートを確認します。RX と TX を入れ替えます |
| コンソールが文字化けする | ボーレートの誤り | [シリアルコンソール](#serial-monitor) に記載のボーレートで開き直します |
| macOS でターミナルが固まる | `/dev/tty.*` を使った | `/dev/cu.*` を使います |
| `ipro_reef_teach` が `NO MFG PARTITION` と表示する | ボードに `partition_reef_teach.toml` のレイアウトが書き込まれていない | [ipro_reef_teach](#mfg) のとおり、アプリケーションのテーブルと `--mfg` を指定して書き込み直します |

## 次のステップ { #next-steps }

- [ビルドと書き込みの流れ](../tutorials/build-and-flash.md)：日常的な編集、ビルド、書き込み、モニターのサイクル。
- [macOS／Linux のコマンドライン](command-line.md)：`build_freertos.sh` のすべてのアクションとオプション。
- [デバッグとトラブルシューティング](../reference/debugging.md)
