---
title: "ツールのコマンドライン"
description: SDK V2.3.0 のホストツール（build_freertos.sh、make、IntelProCube 書き込みツール、serial_monitor.py、create_ota.py、Reef の Teach ツールと OTA ツール）のコマンド、オプション、使用例と、同梱されていないツールの一覧です。
migrate_from:
  - "tools-debugging.html#overview"
  - "tools-debugging.html#build-cli"
  - "tools-debugging.html#zephyr-tools"
  - "tools-debugging.html#automated-testing"
  - "tools-debugging.html#size-analysis"
  - "tools-debugging.html#dev-workflow"
---

# ツールのコマンドライン

SDK に同梱されているホストツールのコマンド構文、オプション、使用例です。例は IPRO7AI Reef EVK V4.0 を対象にしています。書き込みとコンソールの手順は [書き込みとシリアルコンソール](../get-started/flash-and-monitor.md) を参照してください。

## ツール一覧 { #overview }

| ツール | パス | 用途 | 提供状況 |
|---|---|---|---|
| `build_freertos.sh` | SDK ルート | ビルド、クリーン、書き込み、コンソール、サイズレポート、自動テスト | 同梱 |
| `make` + `project.build` | 各アプリケーションの `Makefile` | 1 つのアプリケーションをビルド | 同梱 |
| `serial_monitor.py` | `tools/` | コンソール出力の読み取り。最初に 1 つのコマンドを送信し、パターンを待ち、ログを保存することも可能（macOS、Linux。対話型ターミナルではありません） | 同梱 |
| `create_ota.py` | `tools/` | IntelProCube の結合イメージを boot2 OTA パッケージにまとめる | 同梱 |
| `ipro_dl.py` | `tools/` | boot2 の USB ダウンローダー経由でボードに書き込みます。Python 標準ライブラリだけで動きます（macOS、Linux）。IPRO7AI Sensor Tag の `ipro7ai_sensor_tag_demo` はこれでボードの USB から書き込み、IPRO Workbench 0.2.0 も macOS でボードの USB から書き込むときに使っていました（0.2.1 からは不要です）。V2.3.0 から | 同梱 |
| ブラウザー版の画像 Teach | `tools/teach_web/` | Chrome または Edge で画像を収集し、分類器を学習して `ipro_reef_teach` にデプロイ | 同梱 |
| `mfg_payload.py` | `apps/ai/ipro_reef_teach/` | `ipro_reef_teach` の `--mfg` 内容（起動モードと声紋モデル）を生成 | 同梱 |
| Reef BLE OTA ツール | `apps/bluetooth/ble/ipro_ble_remote/tools/` | `make_reef_ota.sh`、`reef_ota.py`、`reef_ble_test.py`、および Android デモアプリ `ipro_remote_demo.apk`（アプリケーションディレクトリ内） | 同梱 |
| `parse_kconfig_dynamic.py` | `tools/script/` | Kconfig ツリーを JSON で出力（kconfiglib が必要。ビルドでは使用しない） | 同梱 |
| CMake 3.15 | `tools/cmake/` | `PATH` に `cmake` がない場合の代替。Linux x86-64 専用 | 同梱 |
| Zephyr スクリプト | `tools/zephyr/` | Zephyr のワークスペース、ビルド、書き込み、コンソール（`ipro7_evb` ボードと `ipro7ai_evk` ボード） | 同梱 |
| IntelProCube 0.7.0.1 コマンドライン書き込みツール | `ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | シリアルポート経由でファームウェア、パーティションテーブル、boot2、`mfg` 内容を書き込み | V2.3.0 には含まれていません。[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) からダウンロードします |
| RISC-V ツールチェーン | `/opt/toolchain/riscv_ipro7/` | コンパイラー（GCC 14、`riscv64-unknown-elf-`） | V2.3.0 には含まれていません。INTELPRO にお問い合わせください |
| IPRO AI Studio | — | IPRO AI Teach、モデル変換とデプロイ | SDK には含まれていません。[GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) からダウンロードしてください |
| OpenOCD / GDB の接続設定、ボードテストスクリプト `tools/board_test.sh`、クラッシュダンプ用ホストツール | — | オンターゲットデバッグ、ボードの自動テスト、`==DUMP_READY:` 後のメモリ読み出し | V2.3.0 には含まれていません。INTELPRO にお問い合わせください |
| `tools/kconfig/menuconfig.py`、defconfig ディレクトリ `configs/`、OTA 署名用の `ota_products.py` | — | `make menuconfig`、`make defconfig`、`create_ota.py --sign-key` | V2.3.0 には含まれていません |

本リリースには、JTAG / GDB によるオンターゲットデバッグの設定や手順はありません。デバッグはシリアルコンソール、ログ、オフラインの `addr2line` で行います。[デバッグとトラブルシューティング](debugging.md) を参照してください。

## 環境変数 { #environment }

| 変数 | 使用するツール | 効果 |
|---|---|---|
| `IPRO_FLASH_TOOL` | `build_freertos.sh`、`make_reef_ota.sh`、`tools/zephyr/flash.sh`、`west flash` | IntelProCube コマンドラインツールのパス。未設定の場合、OS に対応するツール名を `PATH` から探します |
| `IPRO_SERIAL_PORT` | `build_freertos.sh`、`tools/zephyr/` のスクリプト、`west flash` | デフォルトのシリアルポート。未設定で `-p` も指定しない場合、接続されている唯一の USB シリアルポートを使用します |
| `IPRO_CHIP_VARIANT` | `build_freertos.sh flash` | 書き込み時の `--chip-variant`（`IPRO7` または `IPRO7AI`）。未設定の場合はアプリケーションの設定から選択します。[build_freertos.sh](#build-cli) を参照してください |
| `IPRO_FLASH_PT` | `build_freertos.sh flash` | 書き込み時の `--pt` パーティションテーブル。未設定の場合は `--pt` を渡さず、ツールのデフォルトテーブルが使われます |
| `IPRO_PROBE_PORT` | `west flash` | IPRO Debug Probe の UART ブリッジ。デフォルトは `--port` |
| `CROSS_COMPILE` | `make`、`build_freertos.sh build` | ツールチェーンのプレフィックス。環境変数またはコマンドラインで指定すると、`.config` の `CONFIG_CROSS_COMPILE` より優先されます |
| `IPRO_TOOLCHAIN` | `tools/zephyr/bootstrap.sh` | Zephyr ワークスペースで使うツールチェーンのディレクトリ。デフォルトは `/opt/toolchain/riscv_ipro7` |
| `IPRO_ZEPHYR_WS` | `tools/zephyr/build.sh`、`ci_build.sh` | Zephyr ワークスペースの場所。デフォルトは `<SDK>/zephyr-workspace` |

## build_freertos.sh { #build-cli }

```text
./build_freertos.sh [actions...] [options] <project>
```

アクションは連結でき、指定した順に実行されます。失敗した時点で停止します。アクションを指定しない場合は `build` を実行します。macOS と Linux 用の bash スクリプトです。

| アクション | 動作 |
|---|---|
| `build` | `make -C <app>` を実行し、ログを `<build dir>/build.log` に保存します。成功時は `.bin` のパスとサイズを、失敗時はログの最後の 30 行を表示します |
| `clean` | ビルドディレクトリを削除します |
| `flash` | アプリケーションのコンソールボーレートで `reboot_dl` を送信し、2 秒待ってから IntelProCube ツールで書き込みます：`--chipname ipro7 --chip-variant <auto> --baudrate 921600`、`-P` を指定した場合は `--pt` も付けます。ツールの出力に `[All Success]` 行があれば成功です。事前のビルドは行いません |
| `monitor` | アプリケーションのコンソールボーレートで `serial_monitor.py` を開き、最初に `reboot` を送信し、`-t` 秒後に終了します |
| `size` | ELF に対して `size` と `size -A` を実行します（セクション行は先頭 30 行） |
| `test` | ビルドと書き込みを行い、`reboot` を送信して `ALL TESTS PASSED` または `SOME TESTS FAILED` を待ちます。終了コードは 0 が成功、1 が失敗、2 がタイムアウト |

コンソールのボーレートは、使用する設定ファイルの `CONFIG_PLATFORM_UART_BAUDRATE` です。未設定の場合は 115200 です。

| オプション | 意味 | デフォルト |
|---|---|---|
| `-p, --port PORT` | シリアルポート | `$IPRO_SERIAL_PORT`、なければ唯一の USB シリアルポート |
| `-t, --timeout SEC` | `monitor` と `test` の秒数 | `30` |
| `-w, --wait-for PAT` | `monitor` が待つ正規表現 | — |
| `-d, --defconfig FILE` | アプリケーションディレクトリ内の別の設定ファイルを使い、`build_<name>/` にビルドします（`defconfig_reef` → `build_reef/`） | — |
| `-c, --chip-variant V` | 書き込み時の `--chip-variant`：`IPRO7` または `IPRO7AI` | `$IPRO_CHIP_VARIANT`。なければ、設定に `CONFIG_IPRO7AI_REEF=y` または `CONFIG_IPRO7AI_EVK=y` があれば `IPRO7AI`、それ以外は `IPRO7` |
| `-P, --pt TABLE` | 書き込み時のパーティションテーブル：`.toml` のパス（絶対パスとしてツールに渡されます）、またはツールの `chips/ipro7/partition/` にあるテーブル名 | `$IPRO_FLASH_PT`、なければ指定なし |
| `-j, --jobs N` | 外側の `make` の並列ジョブ数。内側の CMake ビルドは常に `-j4` | — |
| `-v, --verbose` | ビルド出力をすべて表示 | — |
| `-l, --list` | `apps/` 以下の 41 個のプロジェクトをカテゴリー別に一覧表示 | — |
| `-h, --help` | ヘルプ | — |

`<project>` にはアプリケーション名（`ipro7ai_reef_demo`）または `apps/` 以下のパス（`platform/ipro7ai_reef_demo`）を指定します。名前があいまいな場合や不明な場合は候補を表示します。`-l` の説明列は `.config` の最初のコメント行から取られ、アプリケーションによっては空欄です。

Reef でビルド、書き込み、コンソール表示を一度に行います（最初の書き込み前はボードに SDK ファームウェアがなく `reboot_dl` に応答しないため、手動で [ダウンロードモードに入って](debugging.md#download-mode) ください）。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

次の順に表示されます。

```text
→ Entering download mode...
→ Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
...
✓ Flash succeeded (…)
→ Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
```

`-d` で Reef 用の別の設定を選べます。例：

```bash
./build_freertos.sh -d defconfig_reef build ipro_ble_remote          # build_reef/build_out/ に出力
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam
./build_freertos.sh -l                                              # 41 個のプロジェクトを一覧表示
./build_freertos.sh size ipro7ai_reef_demo
```

出力先は `<app>/build/build_out/`（`-d` 指定時は `build_<name>/build_out/`）で、`<app>_<chip>.bin`、`.elf`、`.map` が生成されます。チップ名は `CONFIG_CHIP` から決まります（IPRO7 アプリケーションは `_IPRO7`、IPRO6S アプリケーションは `_IPRO6`）。

!!! warning "build_freertos.sh の制限"
    - `flash` は常に `--chipname ipro7` を渡します。IPRO6S アプリケーション（FIN カードのファームウェア `ipro6_if_wifi` など）は、IntelProCube の `--chipname ipro6` で直接書き込んでください。
    - `--boot2`、`--mfg`、`--skip-ota` は渡せません。`ipro_ble_remote` の初回書き込み（boot2 + A/B テーブル）と `ipro_reef_teach`（専用テーブルと `mfg` 内容）は、[IntelProCube ツール](#flash-tool) で直接書き込んでください。
    - `BOARD=` オプションはありません。`config_<board>` ファイルは `-d config_evk` のように指定でき、`build_config_evk/` にビルドされます。
    - 書き込みツールはカレントディレクトリで実行されます。`-P` には `.toml` のフルパスを指定してください。
    - `size` は常に `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size` を使い、`CROSS_COMPILE` を無視します。

## make ターゲット { #make-targets }

各アプリケーションの `Makefile` は SDK ルートの `project.build` を呼び出します（`Unix Makefiles` ジェネレーターで CMake を実行し、続けて `make -j4`）。

| コマンド | 動作 |
|---|---|
| `make -C apps/<category>/<app>` | `.config` で `build/` にビルド |
| `make -C apps/<category>/<app> clean` | ビルドディレクトリを削除（`DEFCONFIG=` を付けると対応する `build_<name>/`） |
| `make -C apps/<category>/<app> DEFCONFIG=defconfig_<name>` | 別の設定を `build_<name>/` にビルド。`.config` は変更されません |
| `make -C apps/<category>/<app> CROSS_COMPILE=<dir>/bin/riscv64-unknown-elf-` | ツールチェーンのプレフィックスを指定。`.config` の `CONFIG_CROSS_COMPILE` より優先されます |
| `make -C apps/multimedia/ipro_agora_sentino BOARD=evk` | `BOARD=` を読むのは `ipro_agora_sentino`（デフォルト `reef` = `.config`）と `ipro_pdm_mic_demo`（デフォルト `evb`）だけです。`config_<board>` を選択し、`build_config_<board>/` にビルドします |

- CMake：まず `PATH` 上の `cmake`、次に `tools/cmake/`（Linux x86-64）を使います。どちらもない場合、ビルドは `No cmake found` で停止します。
- ビルドのたびに、エディター用に `compile_commands.json` が SDK ルートにコピーされます。
- `make menuconfig` には `tools/kconfig/menuconfig.py` が必要ですが、同梱されていません。一部の `Makefile` の `defconfig` と `list-defconfigs` ターゲットが参照する `configs/` ディレクトリも同梱されていません。`.config` を直接編集するか、コピーを `defconfig_<name>` として保存し、`DEFCONFIG=` でビルドしてください。

## IntelProCube 書き込みツール { #flash-tool }

書き込みには IntelProCube のコマンドラインツールを使います。このツールは V2.3.0 には含まれていません。[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) から 0.7.0.1 をダウンロードし、[開発環境の準備](../get-started/environment.md#intelprocube)に従ってインストールしてください。ツールはチップファイルを自身の `chips/` ディレクトリから読み込むため、IntelProCube のディレクトリで実行してください。この表は SDK 内の README とスクリプトからまとめたものです。全オプションについてはツール自体が正となります。

| オプション | 意味 |
|---|---|
| `--chipname ipro7` | IPRO7 / IPRO7AI（Reef）。IPRO6S（FIN カードなど）は `--chipname ipro6` を使います |
| `--chip-variant IPRO7AI` | Flash ピンの設定：IPRO7AI（Reef、QFN56）は `IPRO7AI`（`0x9`）、IPRO7 EVB は `IPRO7`（`0x2`）。ツールはこの値を自身の `chips/ipro7/eflash_loader/eflash_loader_cfg.ini` に書き込むため、ボードを切り替えたときは必ず再指定してください |
| `--port` | シリアルポート：USB-UART ケーブル、または IPRO Debug Probe の名前が `02` で終わるポート |
| `--baudrate 921600` | 書き込みのボーレート。アプリケーションのコンソールボーレートとは無関係です |
| `--firmware` | 書き込む `.bin` |
| `--pt` | パーティションテーブル（`.toml`）：ツールディレクトリからの相対パス（例：`chips/ipro7/partition/partition_cfg_2M.toml`）またはフルパス。省略するとツールのデフォルトテーブルを使います |
| `--boot2` | boot2 イメージも書き込みます（例：ツールの `chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin`）。Reef で `ipro_ble_remote` の OTA を使うときに必要です |
| `--mfg` | `mfg` パーティションに書き込むファイル（AI モデル、`ipro_reef_teach` の起動モードと声紋モデル） |
| `--skip-ota` | アプリケーション専用のパーティションテーブルと組み合わせて使います（例：`ipro_reef_teach`） |
| `--build` | 書き込まずに結合イメージ `chips/ipro7/img_create_iot/whole_img.bin` だけを生成します。[`create_ota.py`](#ota-package) の入力になります |

Reef の出荷時ファームウェアを書き込みます（先に [ダウンロードモードに入って](debugging.md#download-mode) ください）。

```bash
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 \
    --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

成功すると最後に `[All Success]` が表示されます。ツールは失敗しても終了コード 0 を返すため、この行で判断してください。Linux では `./ipro_iot_tool_linux`、Windows では `ipro_iot_tool.exe` と `COM5` などのポートを使います。Reef の各アプリケーションに必要なパーティションテーブル、`--boot2`、`--mfg` は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples) に記載しています。

## serial_monitor.py { #serial-monitor }

```text
python3 tools/serial_monitor.py <port> [--baud 115200] [--timeout 30]
                                [--send CMD] [--wait-for PATTERN] [--log FILE]
```

Python 標準ライブラリの termios でポートを開くため、pyserial は不要です。macOS と Linux で動作し、Windows では動作しません。出力を読み取るだけで（最初に 1 つのコマンドを送信することは可能）、対話型ターミナルではありません。コマンドを 1 行ずつ入力するには、`screen`、`minicom` などのシリアルターミナルソフトウェアを使ってください。

| オプション | 意味 | デフォルト |
|---|---|---|
| `--baud` | ボーレート。921600 や 2000000 などの高速レートも macOS と Linux で使えます | `115200` |
| `--timeout` | 監視する秒数。`0` にすると Ctrl-C まで実行します | `30` |
| `--send` | 監視の前に送信する 1 つのコマンド。例：`reboot`、`reboot_dl`、`reef selftest` | — |
| `--wait-for` | 正規表現。最初に一致した時点でモニターが終了します | — |
| `--log` | 生の出力をファイルにも保存します | — |

| 終了コード | 意味 |
|---|---|
| 0 | 一致し、一致したテキストに `PASSED` が含まれる |
| 1 | 一致したが、一致したテキストに `PASSED` が含まれない |
| 2 | 一致しないままタイムアウト |
| 3 | ポートを開けない、またはコマンドを送信できない |
| 130 | Ctrl-C で停止 |

```bash
# Reef コンソール（115200）：セルフテストを実行し、10 秒後に終了
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# ipro7_jpeg_decode の Reef 用設定（921600）：Ctrl-C まで監視し、ログを保存
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0 --log console.log

# 実行中のファームウェアをダウンロードモードで再起動（"reboot to download mode" と表示される）
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
```

macOS では `/dev/cu.*` を使ってください。`/dev/tty.*` はキャリア検出を待つため止まってしまいます。書き込みの前にモニターを終了し、ポートを解放してください。

## create_ota.py { #ota-package }

IntelProCube が生成する結合イメージを boot2 OTA パッケージにまとめます。デフォルトでは XZ 圧縮して `<input name>.xz.ota` として書き出し、`--raw` を付けると非圧縮の `<input name>.ota` になります。入力は `IPNP` で始まるブートヘッダーを持つ結合イメージ（ツールの `chips/ipro7/img_create_iot/whole_img.bin`）でなければならず、SDK ビルドの `.bin` は使えません。それ以外の形式ではスクリプトが停止します。

```text
python3 tools/create_ota.py <whole_img.bin> [--raw] [-o OUTPUT] [--hw-ver STR] [--fw-ver STR]
```

| オプション | 意味 |
|---|---|
| `--raw` | 圧縮しない |
| `-o, --output` | 出力ファイル |
| `--hw-ver` | ヘッダー内のハードウェアバージョン文字列。デフォルトに頼らず明示的に指定してください |
| `--fw-ver` | ヘッダー内のファームウェアバージョン文字列（デフォルト `OTA_V1.0.0`） |
| `--sign-key`、`--product` などの署名オプション | 同梱されていない `ota_products.py` が必要です。V2.3.0 では使用できません |

Reef では、`ipro_ble_remote` の `make_reef_ota.sh` がツールの `--build` とこのスクリプトを自動で実行します。[Reef アプリケーション用のホストツール](#reef-tools) を参照してください。OTA の全体の流れは [OTA アップデート](../guides/ota.md) にあります。

## Reef アプリケーション用のホストツール { #reef-tools }

### ブラウザー版の画像 Teach：tools/teach_web { #teach-web }

IPRO AI Studio をインストールせずに、Chrome または Edge で Reef のカメラから画像を収集し、分類器を学習して USB 経由でデプロイします。ボードは `ipro_reef_teach` を `image` モードで実行している必要があります。ホストには Python 3.8 以降が必要です。

<div class="ipro-steps" markdown>

1. **Web サーバーを起動します**

    ```bash
    python3 tools/teach_web/serve.py
    ```

    ブラウザーで `http://localhost:8780` が開きます（デフォルトのブラウザーが Chrome または Edge でない場合は、どちらかにアドレスを貼り付けてください）。

2. **ボードを接続します**：カメラへのアクセスを許可します。**Connect…** または最初の **Deploy** で、シリアルポート **IPRO7 UVC Cam** を選択します。

3. **オフラインのコンピューター**：オンライン時に一度 `python3 tools/teach_web/serve.py --fetch-runtime` を実行します。LiteRT.js ランタイム（約 22 MB）がローカルに保存されます。

</div>

### ipro_reef_teach の mfg 内容：mfg_payload.py { #mfg-payload }

`ipro_reef_teach` の初回書き込みでは、起動モードと声紋モデルを `--mfg` で書き込みます。

```bash
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
```

`--mode` は `image`、`voice`、`sensor` のいずれかです。生成された `reef_teach_mfg.bin` を IntelProCube に `--mfg` で渡します。書き込みコマンドは [サンプルページ](../examples/ipro_reef_teach.md) にあります。ファームウェアだけを更新する場合は `--mfg` を省略してください。

### ipro_ble_remote の Reef OTA ツール { #reef-ota-tools }

| ツール | コマンド | 結果 |
|---|---|---|
| `make_reef_ota.sh` | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh` | 先に `DEFCONFIG=defconfig_reef` のビルドが必要です。`build_reef/build_out/ipro_ble_remote_reef.xz.ota`（約 345 KB）を生成します。boot2 は IntelProCube フォルダー内の最新版、または `IPRO_BOOT2` で指定したファイルを使います |
| `reef_ota.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py <package.xz.ota>` | BLE（bleak）で `IPRO-Remote` という名前のボードにパッケージを送信し、進捗と状態を表示します |
| `reef_ble_test.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ble_test.py` | bleak セントラルとして Reef の GATT サービスをテストします（`info led env sound tone img`。`keys` と `motion` はボードのそばで操作する人が必要）。取得した JPEG はスクリプトと同じ場所に保存されます |
| `ipro_remote_demo.apk` | Android スマートフォンにインストール | `ipro_ble_remote` 用のデモアプリ。`.xz.ota` パッケージを送信できます |

どちらの Python スクリプトにも bleak が必要です：`python3 -m venv .venv && .venv/bin/pip install bleak`。OTA は boot2 と `partition_cfg_2M_remote_ab.toml` で書き込んだボードでのみ動作します。標準の `partition_cfg_2M.toml` で書き込んだ Reef では、絶対に OTA を実行しないでください。

### その他の Reef アプリケーションのツール { #reef-app-tools }

| ツール | 用途 |
|---|---|
| `apps/multimedia/ipro7_jpeg_decode/host/jpeg_check.py photo.jpg [--fix out.jpg]` | IPRO7 が JPEG をデコードできるかを PC で確認し、必要なら変換します |
| `apps/multimedia/ipro7_jpeg_decode/host/jdec_host.py -p <port> upload photo.jpg --go 565` | コンソール経由で JPEG をボードに送ってデコードさせ、比較用に結果を取得します |
| `apps/multimedia/ipro7_jpeg_decode/host/run_host_tests.py` | PC 上でデコーダーを libjpeg と比較して検証します（`cc`、`djpeg` が必要） |
| `apps/multimedia/ipro_agora_sentino/setup_ncm_nat.sh` | macOS で USB-NCM 接続の NAT を設定します |

## Zephyr スクリプト { #zephyr-tools }

`tools/zephyr/`（`bootstrap.sh`、`build.sh`、`flash.sh`、`monitor.sh`、`ci_build.sh`）は Zephyr ボード `ipro7_evb` と `ipro7ai_evk` 用です。本リリースには Reef 用の Zephyr ボードはありません。使い方は [Zephyr RTOS](../guides/zephyr.md) を参照してください。

## サイズとメモリの解析 { #size-analysis }

| 方法 | コマンドまたは場所 | 表示内容 |
|---|---|---|
| リンカーのメモリレポート | 各ビルドの最後の数行（`build_freertos.sh` では `build.log` 内） | 各メモリ領域（`flash`、`ocram`、有効な場合は `psram`）の使用量と使用率 |
| `size` アクション | `./build_freertos.sh size <app>` | text / data / bss の合計とセクションサイズ |
| マップファイル | `<build dir>/build_out/<app>_IPRO7.map` | すべてのオブジェクトファイルとライブラリのアドレスとサイズ |
| サイズ順のシンボル | `riscv64-unknown-elf-nm --size-sort -S <ELF>` | 最も大きい関数と変数 |
| 逆アセンブル | `.config` に `CONFIG_GENERATE_ASM=y` | `<app>_IPRO7.asm` も出力されます |

```bash
./build_freertos.sh size ipro7ai_reef_demo
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-nm --size-sort -S \
    apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf | tail -20
```

`CONFIG_AI_SUPPORT` と `CONFIG_MM_SUPPORT` の両方を有効にすると、リンカースクリプトは OCRAM 領域を 64 KB（`CONFIG_EM_SIZE` が 0）または 48 KB（`CONFIG_EM_SIZE` が 0 より大きい）に縮小し、CMake は構成時に `AI+MM …: OCRAM=…` を表示します。メモリマップは [IPRO7](../hardware/chips/ipro7.md) に、OCRAM の配分は [ビルドシステムと設定](../guides/build-system.md) にあります。

## 自動テスト { #automated-testing }

`./build_freertos.sh test ipro_unit_test` はビルドと書き込みを行い、`ALL TESTS PASSED` または `SOME TESTS FAILED` を待ちます。`ipro_unit_test` には IPRO7 EVB が必要です。Reef のオンボードセルフテストは出荷時ファームウェアの `reef selftest` です。[デバッグとトラブルシューティング](debugging.md#board-testing) を参照してください。

## その他のツール { #other-tools }

| ツール | 動作 |
|---|---|
| `tools/script/parse_kconfig_dynamic.py Kconfig [PROJECT_SYMBOL]` | Kconfig ツリーを JSON で出力します。kconfiglib が必要です。ビルドでは使用しません：`cmake/generate_autoconf.cmake` が `.config` を直接読み取って `autoconf.h` を生成します |
| `components/audio/tools/gen_asrc_coef.py` | オーディオのサンプリングレート変換器の係数を生成します |
| `*/test_host/run.sh` | PC 上で実行するユニットテスト。例：`components/audio/test_host/run.sh`、`apps/ai/ipro_reef_teach/sensor/test_host/run.sh` |
| 他のボード用のツール | IPRO7AI EVK サンプルの `flash.sh` と `enter_dl.py`、`ipro6_fmac` の `tools/mkimg.py`（IPRO6S EVK）、`tools/android/IproMicDemo/`（`ipro_pdm_mic_demo`）：それぞれのボードが必要です |

## 開発の流れ { #dev-workflow }

Reef での編集、ビルド、書き込み、コンソールの繰り返しは [ビルドと書き込みの流れ](../tutorials/build-and-flash.md) にあります。独自のアプリケーションを始めるには [最初の独自アプリケーションを作る](../tutorials/first-own-app.md) を参照してください。デバッグとよくあるエラーは [デバッグとトラブルシューティング](debugging.md) にあります。
