---
title: "デバッグとトラブルシューティング"
description: IPRO7AI Reef EVK でのシリアルコンソールとログによるデバッグ、ダウンロードモードへの移行、クラッシュ出力の読み方、ビルドの解析、オンボードセルフテストの実行と、ビルド・書き込み・コンソール・実行時のよくある問題の対処表です。
migrate_from:
  - "tools-debugging.html#gdb-debugging"
  - "tools-debugging.html#crash-analysis"
  - "getting-started.html#debugging"
  - "getting-started.html#troubleshooting"
  - "getting-started.html#board-testing"
  - "getting-started.html#next-steps"
---

# デバッグとトラブルシューティング

IPRO7 の FreeRTOS アプリケーションはシリアルコンソールでデバッグします。シェルコマンドとログでその時点の状態を確認でき、クラッシュ時にはファームウェア自身が例外の解析結果とコールスタックを表示します。このページの手順は IPRO7AI Reef EVK V4.0 を対象にしています。

## シリアルコンソール { #debugging }

Reef のコンソールは U6 デバッグコネクターの UART0（GPIO20 TX / GPIO21 RX）です。書き込みにも同じ UART を使います。U6 からはボードに給電されません。給電は USB-C から行います。配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#debug-connector) にあります。

| 接続方法 | ホスト側のポート |
|---|---|
| 3.3 V USB-UART ケーブル（U6 のピン 2、3、4 に接続） | macOS は `/dev/cu.usbserial-XXXX`、Linux は `/dev/ttyUSB0`、Windows は `COM5` などのポート |
| IPRO Debug Probe（ピン配列を反転したケーブルで U6 に接続） | `IPRO7 CMSIS_DAP` として認識され、2 つの CDC ポートが現れます。名前が `02` で終わるポートが Reef のコンソール（例：`/dev/cu.usbmodemXXXX02`）、`04` は CCI ブリッジです |

ボーレートは、アプリケーションの設定ファイルの `CONFIG_PLATFORM_UART_BAUDRATE` です。未設定の場合は 115200 です。Reef 用の設定はすべて 115200 で、例外は `ipro7_jpeg_decode` の `defconfig_reef`（921600）だけです。他のボード用の設定では、`ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro_speaker_recog`、`ipro7_uvc_cam`、`ipro7_jpeg_decode`、`ipro_epd_el036` の `.config` も 921600 を使います。フレーム形式は 8N1、フロー制御なしです。

<div class="ipro-steps" markdown>

1. **コンソールを開きます**。シリアルターミナルソフトウェアであれば何でも使えます。macOS / Linux で `screen` を使う場合：

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    Enter キーを押すとシェルのプロンプトが表示されます。`screen` を終了するには、Ctrl-A を押してから K を押します。

2. **コマンドを一覧表示します**：`help` と入力します。組み込みコマンドと、アプリケーションが登録したコマンドが表示されます。

3. **コマンドを 1 つ送信して応答を読みます**（対話型ターミナルは不要です）：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "free" --timeout 3
    ```

    ヒープの合計、空き容量、過去最小の空き容量が表示され、3 秒後に終了します。

</div>

`CONFIG_SHELL=y` のアプリケーションには、次の組み込みコマンドがあります。

| コマンド | 用途 |
|---|---|
| `help` | 全コマンドを一覧表示 |
| `ps` | タスク一覧と CPU 使用率 |
| `free` | ヒープの合計、空き容量、過去最小の空き容量 |
| `time` | 起動からの経過時間 |
| `p <addr> [count] [width]` | メモリの読み出し（幅は 1、2、4 バイト、デフォルト 4） |
| `m <addr> <value> <width>` | メモリへの書き込み |
| `memtrace <addr> [count]`、`memtrace <addr> <value> <count>` | 32 ビットワード単位でメモリを読み出し、または埋める（アドレスは 16 進数） |
| `reboot` | 再起動 |
| `reboot_dl` | ダウンロードモードで再起動。`reboot to download mode` と表示されます |
| `reboot_usb [code]` | boot2 の USB ダウンロードモードで再起動（boot2 付きで書き込んだイメージのみ）。[ダウンロードモードに入る](#download-mode) を参照してください |
| `watchdog`、`watchdog test` | `CONFIG_APP_WATCHDOG` を有効にしたアプリケーション（`ipro_reef_teach` など）で使用：AON ウォッチドッグの状態を表示します。`test` はウォッチドッグのリフレッシュを止め、タイムアウト後にボードが再起動します |
| `ls`、`cat`、`hexdump`、`pwd`、`cd`、`mkdir`、`rm`、`cp` | ファイルシステムコマンド。設定に `CONFIG_EVFS`、`CONFIG_EVFS_POSIX`、`CONFIG_IPRO_OSAL` がある場合のみ使えます |

ログは `IPRO_LOGx` マクロを使います（[API リファレンス](api/index.md#log-api) を参照）。デバッグレベルのログを出すには、`.config` で `CONFIG_LOG_DEFAULT_LEVEL=4` を設定して再ビルドします。値は整数で、同梱のアプリケーションは 3（info）を使っています。

知っておくと役立つ起動メッセージ：

| メッセージ | 意味 |
|---|---|
| `[XTAL] capcode <boot value> -> <set value>` | `CONFIG_IPRO7_XTAL_CAPCODE` の水晶発振子調整値が適用されました。Reef では未設定の場合のデフォルトは 95 です |
| `[PSRAM] WARNING: init failed` | アプリケーションは `CONFIG_USE_PSRAM` を有効にしていますが、PSRAM が初期化されませんでした |
| `[BOOT2] IPRO7 Boot2 v0.6.0` | イメージは boot2 付きで書き込まれています（例：`ipro_ble_remote` の Reef OTA ビルド）。boot2 が先に実行され、その後アプリケーションを起動します |

## ダウンロードモードに入る { #download-mode }

書き込みの前に、Reef をダウンロードモードにする必要があります。ダウンロードモードではコンソールに何も表示されません。書き込み後、SW2（RESET）を 1 回押すと通常起動します。

| 方法 | 使う場面 |
|---|---|
| SW1 + SW2 ボタン | 常に使えます。初回の書き込みやファームウェアが停止した場合も含みます |
| コンソールで `reboot_dl` | シェル付きの SDK ファームウェアがボードで動作している場合 |
| U6 に接続した DTR / RTS 自動ダウンロードケーブル | DTR と RTS を U6 のピン 5 と 6 に配線した USB-UART ケーブルを使う場合 |
| IPRO Debug Probe のキーワード | プローブが U6 に接続されている場合 |

<div class="ipro-steps" markdown>

1. **ボタン**：SW1（BOOT）を押したまま SW2（RESET）を押して離し、その後 SW1 を離します。コンソールに何も表示されなければ、ボードはダウンロードモードです。

2. **コンソールコマンド**：シェルで `reboot_dl` と入力するか、ホストで次を実行します。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
    ```

    `reboot to download mode` と表示され、その後は何も表示されません。`build_freertos.sh flash` は、アプリケーションのコンソールボーレートでこのコマンドを自動的に送信します。

3. **自動ダウンロードケーブル**：U6 のピン 5（BOOT）とピン 6（RESET）は、それぞれ 1 kΩ を介して GPIO41 とリセットピンにつながっています。USB-UART ケーブルの DTR をピン 5 に、RTS をピン 6 に接続すると、DTR / RTS を制御するホストプログラムでボタンを使わずにボードをダウンロードモードにできます。BOOT が High の状態で RESET を解除します。

4. **IPRO Debug Probe**：名前が `02` で終わるプローブのポートに `IPRODL_1`、続いて `IPRORST_RESET` を送信します。書き込み中は DL を High に保ちます。書き込み後、`IPRODL_0` と `IPRORST_RESET` を送信すると通常起動します。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    # --port /dev/cu.usbmodemXXXX02 で書き込み、[All Success] を確認
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    最後の行を実行すると、アプリケーションの起動メッセージがコンソールに表示されます。

</div>

**boot2 の USB ダウンロードモード**：boot2 付きで書き込んだイメージ（例：`ipro_ble_remote` の Reef OTA ビルド）は、`reboot_usb [code]` で boot2 の USB ダウンロードモードに再起動できます。`reboot to boot2 USB download (HBN_RSV3=0x555342FF)` と表示されます。`code` は boot2 の待ち時間を指定します（`0x01` で 2 秒、`0x02` で 5 秒、`0xFF` で無期限。デフォルトは `0xFF`）。OTA パッケージの検証に失敗した場合も、boot2 はこの USB レスキューモードで停止します。SDK には USB 経由で書き込むためのホストツールは含まれていません。書き直すには、上記の UART による方法のいずれかでダウンロードモードに入ってください。

## GDB とデバッグプローブ { #gdb-debugging }

!!! info "V2.2.0 には含まれていません"
    JTAG によるオンターゲットデバッグ用の OpenOCD 設定と手順は V2.2.0 には含まれていません。INTELPRO にお問い合わせください。

- **ELF にはデバッグ情報があります**：デフォルトのビルドは `-g3 -Os` でコンパイルするため、`<build dir>/build_out/<app>_IPRO7.elf` はツールチェーンの `riscv64-unknown-elf-addr2line` や `riscv64-unknown-elf-gdb` でオフライン解析に使えます。書き込む `.bin` にはシンボルがありません。
- **ビルド済みライブラリにはデバッグ情報がありません**：IPRO BLE コントローラー、RF、AI、ISP、LC3、低消費電力フレームワークのライブラリはデバッグ情報が削除され、シンボル名だけが残っています。そのため、これらのソースをステップ実行することはできません。
- **IPRO Debug Probe**：Reef ではコンソールのブリッジとダウンロードモードの制御に使います（[ダウンロードモードに入る](#download-mode) を参照）。プローブのファームウェアは SDK には含まれていません。ハードウェアと配線は [ドキュメント](../documents/index.md) の Debug Probe ユーザーマニュアルにあります。

## クラッシュの解析 { #crash-analysis }

CPU 例外が発生すると、デフォルトの例外ハンドラーがコンソールに次のブロックを表示します。

| ブロック | 内容 |
|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` | `MCAUSE`、`MEPC`、`MTVAL` と例外の種類（例：`Illegal Instruction`、`Load Access Fault`） |
| `=== ADDRESS ANALYSIS ===` | 例外が発生した PC の領域（FLASH / PSRAM / OCRAM）、戻りアドレス `ra`、スタックポインター `sp` が範囲内かどうか |
| `=== FAULTING TASK ===` | 例外を起こした FreeRTOS タスクとそのスタックの最高水位（0 はスタックオーバーフローを示します） |
| レジスターダンプ | 例外発生時の汎用レジスター |
| `=== STACK BACKTRACE ===` | フレームポインター（`s0`）をたどった呼び出し履歴。1 レベルにつき 1 つの戻りアドレス |

<div class="ipro-steps" markdown>

1. **出力を保存します**：コンソールをファイルに記録します。例：`python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0 --log crash.log`。問題を再現してから Ctrl-C を押します。

2. **アドレスをソース行に変換します**：例外が発生した PC（`MEPC`）、`ra`、バックトレースのアドレスを、同じビルドの `.elf` で調べます。

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-addr2line -f -C \
        -e apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf \
        0x1301c148 0x13004a2e
    ```

    各アドレスについて、関数名と `file:line` の 2 行が表示されます。`??:0` は、そのアドレスがこの ELF にないか、ELF が別のビルドのものであることを示します。

3. **ボードをリセットします**：SW2（RESET）を 1 回押します。

</div>

!!! warning "`==DUMP_READY:2000000==` が繰り返し表示される"
    `ipro7ai_reef_demo` と `ipro_reef_teach` の `.config` は `CONFIG_EXCEPTION_DUMP=y` を設定しています。上記の診断情報の後、ホストツールがメモリを読み出すのを待つため、コンソールには `==DUMP_READY:2000000==` が約 10 秒ごとに最大 5 分間表示されます。このホストツールは V2.2.0 には含まれていません。上に表示された診断情報を保存してから SW2 を押してリセットしてください。待機が不要な場合は、`.config` で `CONFIG_EXCEPTION_DUMP=n` を設定して再ビルドしてください。

| 設定 | 効果 |
|---|---|
| `CONFIG_ENABLE_FRAME_POINTER=y` | `-fno-omit-frame-pointer` でコンパイルし、バックトレースに呼び出し履歴全体が出るようにします。これがないと、通常は例外が発生した PC と `ra` しか得られません |
| `CONFIG_EXCEPTION_AUTO_REBOOT=y` | 診断情報を表示した後、リセット要因 `HAL_RST_REASON_EXCEPTION` で再起動します。量産時に便利ですが、開発中は無効にしておくのが無難です |
| `CONFIG_EXCEPTION_DUMP=y` | 診断情報の後にホストツールを待ちます（上記の注意を参照） |

`.config` は書かれたとおりに読み込まれ、Kconfig のデフォルトは適用されません。これらは明示的に設定してください。

その他の致命的なメッセージは [FreeRTOS フック](api/index.md#rtos-platform) から出力されます。

| メッセージ | 原因 | 対処 |
|---|---|---|
| `[!] Stack overflow: <task>` | そのタスクのスタックが不足しました | `xTaskCreate()` のスタックサイズ（ワード単位）を増やします。続いて表示される `[STACKS]` 一覧で各タスクの余裕を確認できます |
| `[!] Malloc failed, requested: …` | ヒープ不足 | `free` で空きヒープを監視し、確保量を減らすか PSRAM を有効にします。`caller` のアドレスを `addr2line` で調べます |
| `[!] ASSERT <file>:<line>` | `configASSERT()` が失敗しました | そのファイルと行の条件を確認します。`Caller` のアドレスを `addr2line` で調べます |

## ビルドの解析 { #build-analysis }

`build_freertos.sh` では、出力全体が `<build dir>/build.log` に保存され、失敗時には最後の 30 行だけが表示されます。すべて表示するには `-v` を付けます。次の CMake 構成時のメッセージから、ビルドで何が使われたかがわかります。

| メッセージ | 意味 |
|---|---|
| `[toolchain] Vendor toolchain detected …` | INTELPRO ツールチェーンが見つかり、IPRO7 の DSP 拡張とチューニングが有効になっています。`Standard toolchain detected` は汎用の RISC-V GCC を示します |
| `[bluetooth] Using unified Zephyr 4.4 host (ipro_bt_host)` | BLE ホストがビルドに含まれています |
| `[ipro_ble_controller] Using prebuilt …` | 実際にリンクされた BLE コントローラーライブラリ。`CONFIG_IPRO_BLE_CTLR_*` の設定と一致しているか確認してください |
| `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` | Reef ビルドで水晶発振子調整値のデフォルトが追加されました。この行がない場合は、設定に `CONFIG_IPRO7AI_REEF=y` があるか確認してください |
| `AI disabled: OCRAM=240KB (256-16)`、`AI+MM (EM=0): OCRAM=64KB …` | このビルドの OCRAM 領域のサイズ：AI なしの場合は 256 KB から `CONFIG_EM_SIZE` を引いた値、AI と画像処理の両方を有効にした場合は 64 KB または 48 KB |

リンカーはビルドの最後に各メモリ領域の使用量を表示します。メモリ不足の解析は [サイズとメモリの解析](tools.md#size-analysis) を参照してください。

## オンボードセルフテスト { #board-testing }

Reef の出荷時ファームウェア `ipro7ai_reef_demo` にはセルフテストが組み込まれています。ボードの受け取り時、配線の変更後、書き込み後に便利です。SW7 を CAM に、SW8 を PWR に設定してください。

<div class="ipro-steps" markdown>

1. **起動を確認します**：SW2（RESET）を押します。RGB LED が青色で 1 回フェードイン・フェードアウトして消灯し、コンソールにシェルのプロンプトが表示されます。

2. **セルフテストを実行します**

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10
    ```

    約 3 秒以内に LED が赤、緑、青の順に点灯し、スピーカーから 1 kHz のトーンが鳴り、コンソールに次のように表示されます（3 行目と 4 行目はボードの状態によって変わります）。

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: <sensor name> at 0x<address>
    done - keys: press any and run `btn status`
    ```

    microSD カードを挿入している場合、3 行目は `something seated` になります。4 行目の `no sensor` はカメラが見つからなかったことを示します。

3. **ボタンを確認します**：SW3、SW4、SW5、BOOT を押します。LED がそれぞれ赤、緑、青、白に点灯します。続いて `btn status` を送信すると、各ボタンの状態と押された回数が表示されます。

4. **ボードの状態**：`reef status` を送信すると、コンソールのピン、ボタン、LED、スピーカー、ヘッドセット検出、SD スロット、カメラの状態が表示されます。

</div>

`ipro_unit_test`（HAL と共通コンポーネントのユニットテスト、`./build_freertos.sh test ipro_unit_test`）には IPRO7 EVB が必要です。

## トラブルシューティング { #troubleshooting }

### ビルド { #troubleshooting-build }

| 症状 | 原因 | 対処 |
|---|---|---|
| `No cmake found`、または macOS で `tools/cmake` が実行できない | システムに CMake がありません。同梱の `tools/cmake/` は Linux x86-64 のバイナリです | CMake 3.15 以降（Zephyr では 3.20 以降。例：`brew install cmake`）をインストールして `PATH` に追加し、`cmake --version` で確認します |
| `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc` が見つからない | ツールチェーンが未インストール、または別の場所にインストールされています | ツールチェーンは INTELPRO から入手してください。別の場所にある場合は `export CROSS_COMPILE=<path>/bin/riscv64-unknown-elf-` を実行します |
| `[ipro_ble_controller] CONFIG_EM_SIZE must match …` | `.config` に `CONFIG_EM_SIZE` がありません | `CONFIG_EM_SIZE` を追加します（同梱のアプリケーションは 16 または 32 を使用） |
| `bt54_iso2 needs at least 32 KB EM` | LE Audio の設定で EM が 16 KB になっています | `CONFIG_EM_SIZE=32` を設定します |
| `unsupported variant` または `unsupported feature profile` | コントローラーの設定が同梱の組み合わせにありません | `CONFIG_IPRO_BLE_CTLR_LIB` には `link1_periph`、`link1`、`link2`、`link4` のいずれか、`CONFIG_IPRO_BLE_CTLR_FEATURE` には `bt52` または `bt54_iso2` を使います |
| `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED` を設定した後、`ipro_ble_controller` で構成に失敗する | これらの設定は BLE コントローラーをソースからビルドしますが、パッケージにはビルド済みライブラリしかありません | これらを削除してください。これらの機能が必要な場合は INTELPRO にお問い合わせください |
| リンクエラー `undefined reference to adc_ioctl` | `adc_channel_start()` などの ADC 簡易マクロを使用しました | `hal_adc_ioctl()` を使います |
| `CONFIG_AI_SUPPORT` などの機能を有効にしたが、依存する設定が有効になっていない | ビルドは `.config` を書かれたとおりに読み、Kconfig の `select` や `depends on` を適用しません | 依存する設定を明示的に設定します。例：AI には `CONFIG_USE_PSRAM=y`。[ビルドシステムと設定](../guides/build-system.md) を参照してください |
| 単純な `make` でビルドしたイメージが Reef で何もしない | ほとんどのアプリケーションの `.config` は別のボードを対象にしています | `DEFCONFIG=defconfig_reef…` で Reef 用の設定をビルドします。[よくある質問](faq.md#reef-apps) を参照してください |
| リンカーがメモリ領域のオーバーフローを報告する | コードまたはデータが `flash`、`ocram` などの領域を超えています | [サイズとメモリの解析](tools.md#size-analysis) の方法で最も大きな使用箇所を探します。AI と画像処理の両方を有効にすると OCRAM は 64 KB または 48 KB しかありません |

### 書き込み { #troubleshooting-flash }

| 症状 | 原因 | 対処 |
|---|---|---|
| `[All Success]` が出ず、出力に `flash jedec id: 00000000` または `IPRO FLASH MATCH TYPE FAIL` がある | `--chip-variant` がボードと一致していません。ツールが前回の設定を再利用しました | Reef では `--chip-variant IPRO7AI` を指定して書き込み直します |
| ツールがボードと通信できない | ボードがダウンロードモードになっていないか、別のプログラムがシリアルポートを使用しています | [ダウンロードモードに入り](#download-mode)、シリアルモニターをすべて閉じてから再試行します |
| `build_freertos.sh flash` で `Flash tool not found` と表示される | IntelProCube ツールが見つかりません | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` を設定するか、ツールのディレクトリを `PATH` に追加します |
| `No serial port found` または `Several serial ports` | USB シリアルポートがない、または複数あります | `-p` を指定するか、`IPRO_SERIAL_PORT` を設定します |
| IPRO6S アプリケーションで `build_freertos.sh flash` が失敗する | スクリプトは常に `--chipname ipro7` を渡します | IntelProCube のディレクトリから `--chipname ipro6` で書き込みます。[IPRO6S](../hardware/chips/ipro6s.md) を参照してください |
| IPRO6S の書き込みが `[All Success]` で終わるのに、リセット後にコンソールに何も表示されない | IntelProCube 0.7.0 の IPRO6 ブートヘッダーのタイミング設定が 2 MB Flash の IPRO6S に適合しない | IntelProCube 0.7.0.1 以降を使用します。[IPRO6S](../hardware/chips/ipro6s.md#ipro6s-no-boot) を参照してください |
| BLE OTA の後、Reef がまったく応答しない | 標準の `partition_cfg_2M.toml` で書き込んだボードで OTA を実行しました | ダウンロードモードに入り、boot2 と `partition_cfg_2M_remote_ab.toml` で書き込み直します。[ipro_ble_remote](../examples/ipro_ble_remote.md) を参照してください |

### コンソール { #troubleshooting-console }

| 症状 | 原因 | 対処 |
|---|---|---|
| 文字化けする | ボーレートが違います | アプリケーションの `CONFIG_PLATFORM_UART_BAUDRATE` を使います。Reef 用の設定の多くは 115200、`ipro7_jpeg_decode` の `defconfig_reef` は 921600 です |
| 何も表示されない | ボードがダウンロードモードになっている、TX / RX が逆になっている、またはプローブの `04` ポートを開いています | SW2 を押してリセットします。U6 のピン 3（TX）がケーブルの RX に、ピン 4 が TX に接続されているか確認します。プローブでは `02` で終わるポートを使います |
| macOS でプログラムが何も表示せず止まる | `/dev/tty.*` を開いています | `/dev/cu.*` を使います |
| `Resource busy`、または `serial_monitor.py` が終了コード 3 で終了する | 別のプログラムがポートを使用しています | 他のターミナルやモニターを閉じます。`lsof /dev/cu.usbserial-XXXX` で使用中のプログラムを特定します |
| `cat` で出力の一部しか表示されない | macOS では `cat` がシリアル入力をバッファリングします | `tools/serial_monitor.py` または他のシリアルターミナルを使います |
| `==DUMP_READY:2000000==` が繰り返し表示される | クラッシュ後にダンプツールを待っています | [クラッシュの解析](#crash-analysis) を参照してください |

### 実行時と BLE { #troubleshooting-runtime }

| 症状 | 原因 | 対処 |
|---|---|---|
| コンソールに `=== ENHANCED EXCEPTION ANALYSIS ===` が表示される | CPU 例外 | [クラッシュの解析](#crash-analysis) のとおりに読み解きます |
| `[!] Stack overflow`、`[!] Malloc failed`、`[!] ASSERT` | スタックまたはヒープの不足、あるいはアサーションの失敗 | [クラッシュの解析](#crash-analysis) の表を参照してください |
| `[PSRAM] WARNING: init failed` | ビルドで PSRAM が有効になっていますが、PSRAM が初期化されませんでした | Reef 用の設定（`CONFIG_IPRO7AI_REEF=y`）でビルドしたか確認します。解決しない場合は INTELPRO にお問い合わせください |
| `cam probe` または `reef selftest` が `no sensor` を報告する | SW7 が CAM になっていないか、カメラケーブルが正しく挿さっていません | SW7 を CAM にします。USB-C を抜き、ケーブルを挿し直してから再度電源を入れます |
| リセット後にボンディング情報が失われ、スマートフォンで再ペアリングが必要になる | ボンディング情報の保存が無効か、アドバタイズの前にボンディング情報が読み込まれていません | [よくある質問](faq.md#ble-bonding) を参照してください |
| BLE のスループットが予想よりはるかに低い | 接続パラメーター、PHY、または CPU 負荷 | [BLE スループットテスト](../tutorials/ble-throughput.md) を参照してください |

## 次のステップ { #next-steps }

- [ツールのコマンドライン](tools.md)：ビルド、書き込み、モニターの各ツールの全オプション。
- [アプリケーションのテスト](../tutorials/testing.md)：Reef で独自のアプリケーションをテストする方法。
- [API リファレンス](api/index.md)：プラットフォーム、BLE、HAL、ログの API。
- [よくある質問](faq.md)：ビルド、BLE、ネットワーク、RTOS に関するよくある質問。
