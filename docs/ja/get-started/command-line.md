---
title: "macOS／Linux のコマンドライン"
description: macOS または Linux で make と build_freertos.sh を使って FreeRTOS アプリケーションをビルド、クリーン、書き込み、モニターするための完全なリファレンスです。IPRO7AI Reef EVK の例を含みます。
migrate_from:
  - "getting-started.html#installation"
  - "getting-started.html#directory-structure"
  - "tools-debugging.html#macos-notes"
---

# macOS／Linux のコマンドライン

macOS と Linux では、FreeRTOS アプリケーションを `make -C` でビルドするか、ビルド、書き込み、モニターを 1 行でつなげて実行できる `build_freertos.sh` でビルドします。このページは両方のリファレンスです。ビルドディレクトリと出力、別構成、クリーン、`build_freertos.sh` のアクション、オプション、環境変数、制限事項を、IPRO7AI Reef EVK の例とともに説明します。ツールのインストールは [開発環境の準備](environment.md) にあります。

## 前提条件 { #prerequisites }

- [開発環境の準備](environment.md) が完了していること：ツールチェーン、CMake、make、Python、IntelProCube。
- 以下のコマンドはすべて SDK ルートで実行します。
- 書き込みを行う場合は、[スイッチの設定とボードの接続](first-app-freertos.md#connect) のとおりにボードを接続しておきます。

## ディレクトリ構成 { #directory-structure }

| パス | 内容 |
|---|---|
| `apps/<category>/<app>/` | アプリケーション：`.config`、代替の `defconfig_*` ファイル、`CMakeLists.txt`、`Makefile`、ソース。カテゴリは `ai`、`bluetooth`、`multimedia`、`platform`、`test` |
| `bsp/` | ボード設定とリンカースクリプト、SoC ドライバー、HAL |
| `components/` | FreeRTOS、BLE、ネットワーク、オーディオ、AI、USB、ファイルシステムなど。一部はビルド済みライブラリ |
| `cmake/` | ツールチェーンとビルドマクロ |
| `tools/` | `serial_monitor.py`、`create_ota.py`、`teach_web/`、`zephyr/`、同梱の CMake（Linux x86-64） |
| `zephyr/` | Zephyr モジュール（IPRO7 EVB と IPRO7AI EVK のボード） |
| `build_freertos.sh`、`project.build`、`VERSION.txt` | ビルドのフロントエンド、make と CMake をつなぐグルー、バージョン情報 |

コンポーネントについては [システムアーキテクチャ](../guides/architecture.md) で説明しています。

## make でビルドする { #make }

```bash
make -C apps/<category>/<app>                            # .config を build/ にビルド
make -C apps/<category>/<app> DEFCONFIG=defconfig_<name>  # 別構成を build_<name>/ にビルド
```

- **ビルドディレクトリ：** `DEFCONFIG=` を指定すると、`build_` の後ろにファイル名から `defconfig_` プレフィックスを除いたものを付けた名前になります。例：`defconfig_reef` → `build_reef/`、`defconfig_wifi_ipro6s` → `build_wifi_ipro6s/`。代替ファイルは `build_<name>/.config` にコピーされ、アプリケーション自身の `.config` は変更されません。編集するのはコピーではなく、アプリケーションディレクトリにある元のファイルです。
- **出力：** `<build dir>/build_out/<app>_IPRO7.bin`（書き込み用）、`.elf`（デバッグシンボル付き）、`.map`（メモリマップ）。`<build dir>/include/generated/autoconf.h` には、設定から生成されたマクロが入ります。また、ビルドのたびに、エディターのインデックス作成用として `compile_commands.json` が SDK ルートにコピーされます。
- **ツールチェーン：** `make -C … CROSS_COMPILE=<dir>/bin/riscv64-unknown-elf-` または同名の環境変数で、`.config` の `CONFIG_CROSS_COMPILE` を上書きします。
- **並列ビルド：** 内側の CMake ビルドは常に `-j4` で実行されます。
- **`BOARD=`：** `ipro_agora_sentino`（デフォルトは `reef`）と `ipro_pdm_mic_demo` だけが使います。その他のアプリケーションは `DEFCONFIG=` でボードを選びます。

`ipro7ai_reef_demo` をビルドすると次のように表示されます（抜粋）：

```text
[INFO] Build Path: <SDK>/apps/platform/ipro7ai_reef_demo/build
CPU: intelpro_ipro7
...
-- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
-- Generated autoconf header: <SDK>/apps/platform/ipro7ai_reef_demo/build/include/generated/autoconf.h
...
-- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
-- IPRO7 flash: 1M (default, on-chip)
-- AI disabled: OCRAM=256KB
...
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
[100%] Built target ipro7ai_reef_demo_IPRO7.elf
```

`[board] IPRO7AI Reef` の行は、ビルドが Reef 向けであることを示します。この行がない場合、その設定は別のボード向けです。

### Reef 用のビルド設定 { #reef-configs }

以下の設定は Reef 向けです。表に `DEFCONFIG=` があるアプリケーションでは、単に `make` を実行すると、別のボード向けであるアプリケーションの `.config` がビルドされます。

| アプリケーション | ビルドコマンド | ビルドディレクトリ | コンソール |
|---|---|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` | `build/` | 115200 |
| `ipro7ai_reef_demo` + Wi-Fi | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | `build_wifi_ipro6s/` | 115200 |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` | `build/` | 115200 |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro7_uvc_cam` ウェブカメラ | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | `build_reef_ov5640/` | 115200 |
| `ipro7_uvc_cam` じゃんけん | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | `build_reef_rps/` | 115200 |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | `build_reef/` | 921600 |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` | `build/` | 115200 |

各アプリケーションの書き込みに使うパーティションテーブルと、boot2 や `mfg` データが必要なアプリケーション：[書き込みとシリアルコンソール：パーティションテーブル](flash-and-monitor.md#partition-tables)。

## クリーン { #clean }

```bash
make -C apps/platform/ipro7ai_reef_demo clean                                   # build/ を削除
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s clean   # build_wifi_ipro6s/ を削除
```

`clean` は対応するビルドディレクトリだけを削除します。`.config` や別構成を変更したら、クリーンしてからビルドしてください。

## build_freertos.sh { #build-script }

```text
./build_freertos.sh [actions...] [options] <project>
```

アクションはつなげて指定でき、順に実行されます。最初に失敗した時点で残りは実行されず、複数のアクションを指定した場合は最後に各結果のサマリーが表示されます。アクションを指定しない場合は `build` が実行されます。プロジェクトは名前（`ipro7ai_reef_demo`）または `apps/` 以下のパス（`platform/ipro7ai_reef_demo`）で指定します。

### アクション { #actions }

| アクション | 動作 |
|---|---|
| `build` | `make -C <app> [DEFCONFIG=…]` を実行します。出力全体は `<build dir>/build.log` に保存されます。成功すると `✓ Build succeeded`、`Binary:` のパスとサイズを、失敗するとログの最後の 30 行を表示します |
| `clean` | `make -C <app> clean` を実行し、ビルドディレクトリを削除します |
| `flash` | `reboot_dl` を送信してから、ビルドしたイメージを IntelProCube で書き込みます。[書き込みとシリアルコンソール](flash-and-monitor.md#build-script) を参照してください |
| `monitor` | アプリケーションのコンソールのボーレートでポートを開き、まず `reboot` を送信してから `-t` 秒間読み取ります。出力の表示のみで、入力はできません |
| `size` | `riscv64-unknown-elf-size` で `.elf` の合計サイズとセクションごとのサイズを表示します |
| `test` | ビルドと書き込みのあと `reboot` を送信し、`ALL TESTS PASSED` または `SOME TESTS FAILED` を待ちます。終了コードは 0 が合格、1 が不合格、2 がタイムアウトです |

### オプション { #options }

| オプション | 意味 |
|---|---|
| `-p`, `--port PORT` | シリアルポート。デフォルトは `IPRO_SERIAL_PORT`、未設定の場合は接続されている唯一の USB シリアルポート |
| `-t`, `--timeout SEC` | `monitor` と `test` の読み取り時間。デフォルトは 30 秒。`0` を指定すると ++ctrl+c++ まで実行 |
| `-w`, `--wait-for PAT` | この正規表現に一致すると `monitor` が停止します。一致したテキストに `PASSED` が含まれる場合のみ成功とみなされます |
| `-d`, `--defconfig FILE` | 別構成。`build_<name>/` にビルドされ、`flash` と `size` もそこでイメージを探します |
| `-c`, `--chip-variant V` | 書き込み時の `--chip-variant`。デフォルトは `IPRO_CHIP_VARIANT`、未設定の場合は IPRO7AI EVK と Reef の設定では `IPRO7AI`、それ以外は `IPRO7` |
| `-P`, `--pt TABLE` | 書き込み時のパーティションテーブル。`.toml` のパス、またはツールの `chips/ipro7/partition/` 以下のファイル名。デフォルトは `IPRO_FLASH_PT`、未設定の場合は `--pt` なし |
| `-j`, `--jobs N` | 外側の `make` の並列ジョブ数（内側のビルドは常に `-j4`） |
| `-v`, `--verbose` | ビルドの出力全体を画面に表示 |
| `-l`, `--list` | すべてのプロジェクトをカテゴリ別に一覧表示 |
| `-h`, `--help` | ヘルプ |

### 環境変数 { #environment }

| 変数 | 効果 |
|---|---|
| `IPRO_FLASH_TOOL` | IntelProCube のコマンドラインツールのパス。未設定の場合は `PATH` から `ipro_iot_tool_macos` / `ipro_iot_tool_linux` を探します |
| `IPRO_SERIAL_PORT` | デフォルトのシリアルポート（`-p` が優先） |
| `IPRO_CHIP_VARIANT` | デフォルトの `--chip-variant`（`-c` が優先） |
| `IPRO_FLASH_PT` | デフォルトのパーティションテーブル（`-P` が優先） |
| `CROSS_COMPILE` | `make` に渡され、`.config` のツールチェーンプレフィックスを上書きします |

### プロジェクトの一覧 { #list }

```bash
./build_freertos.sh -l
```

`apps/` 以下のプロジェクトをカテゴリ別に一覧表示し、各 `.config` の 1 行目を説明として表示します（抜粋）：

```text
ai
  ipro7ai_evk_person_detect           IPRO7AI EVK person detection: SC101IOT camera -> ISP -> NPU (YOLOv8) with
  ipro7ai_evk_rps                     IPRO7AI EVK rock-paper-scissors: SC101IOT camera -> ISP -> NPU classifier,
  ipro_reef_teach
  ipro_speaker_recog

bluetooth/ble
  ipro_ble_hid_keyboard
  ipro_ble_remote
  ipro_ble_transparent
  ipro_throughput_test
...
platform
  ...
  ipro7ai_reef_demo                   IPRO7AI Reef carrier board demo.
```

一覧にはすべてのボードのアプリケーションが含まれます。Reef 用の設定は [上の表](#reef-configs) にあるものです。

## Reef の例 { #examples }

最初に一度だけ環境を設定します（macOS の例）：

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
PT2M=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
```

```bash
# 出荷時ファームウェア：ビルド、書き込み、起動メッセージを 30 秒間表示
./build_freertos.sh -P $PT2M build flash monitor ipro7ai_reef_demo

# Wi-Fi 版をクリーンしてから再ビルド
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo

# USB ウェブカメラ：ビルドして書き込み
./build_freertos.sh -d defconfig_reef_ov5640 -P $PT2M build flash ipro7_uvc_cam

# 921600 baud のアプリケーション：monitor は設定のボーレートを使用
./build_freertos.sh -d defconfig_reef build flash monitor ipro7_jpeg_decode

# ビルドのみ（初回の書き込みには boot2 が必要なので、ツールを直接実行する）
./build_freertos.sh -d defconfig_reef build size ipro_ble_remote
```

`build` が成功すると次のように表示されます：

```text
Project: ipro_ble_remote  (bluetooth/ble/ipro_ble_remote)
Defconfig: defconfig_reef

→ Building ipro_ble_remote...
✓ Build succeeded (19s)
  Binary: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin (561 KB)
  Log: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build.log
```

## 制限事項 { #limits }

- **IPRO7 のみ：** `flash` は常に `--chipname ipro7` を渡すため、IPRO6S のイメージは書き込めません。
- **`--boot2`、`--mfg`、`--skip-ota` は使えません：** `ipro_ble_remote` の初回書き込みと `ipro_reef_teach` の `mfg` データは、IntelProCube を直接実行して書き込みます。[書き込みとシリアルコンソール](flash-and-monitor.md#boot2-ab) を参照してください。
- **ツールはカレントディレクトリで実行されます：** `-P` には `.toml` のフルパスを指定してください。
- **`reboot_dl` にはシェルが必要です：** シェルのないファームウェアやハングしたファームウェアの場合は、先にボタンでダウンロードモードに入ります。
- **`monitor` は対話型のターミナルではありません：** コマンドを入力するにはターミナルプログラムを使います。[対話型ターミナル](flash-and-monitor.md#terminal) を参照してください。タイムアウト（終了コード 2）や `PASSED` を含まない一致（終了コード 1）は失敗とみなされ、後続のアクションが実行されなくなるため、`monitor` は最後に指定してください。
- **`size` はデフォルトのツールチェーンパスを使います：** 常に `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size` を呼び出します。
- **`BOARD=` オプションはありません：** 別構成は `-d` で選びます。
- **macOS と Linux のみ：** スクリプトには bash が必要で、ポートの自動検出は `/dev/*` の名前にしか対応していません。

## 動作確認 { #verify }

```bash
./build_freertos.sh -l                      # プロジェクトを一覧表示
./build_freertos.sh ipro7ai_reef_demo       # ✓ Build succeeded と Binary: のパスを表示
ls apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

## macOS での注意点 { #macos-notes }

- シリアルポートは `/dev/tty.*` ではなく `/dev/cu.*`（例：`/dev/cu.usbserial-XXXX`）を使ってください。`/dev/tty.*` はキャリア検出を待つため、ハングします。
- `tools/cmake/` に同梱の CMake は Linux 用のバイナリです。ビルドは `PATH` 上の `cmake` を優先するため、macOS では Homebrew の CMake だけで十分です。
- `tools/serial_monitor.py` は Python 標準ライブラリ（termios）のみを使い、pyserial は不要です。921600 などの高いボーレートも macOS 上で自ら設定するため、そのまま使えます。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| `✗ Project '…' not found. Did you mean:` | 名前が不完全 | `-l` で表示される完全な名前を使います |
| `✗ Multiple projects match '…':` | 同じ名前が複数のカテゴリにある | パスを使います（例：`platform/ipro7ai_reef_demo`） |
| `✗ Build failed` で、最後の 30 行に `No cmake found` がある | `PATH` に `cmake` がない | CMake 3.15 以降をインストールします |
| ビルドログで `riscv64-unknown-elf-gcc` が見つからない | ツールチェーンが `/opt/toolchain/riscv_ipro7/` にない | `CROSS_COMPILE` を設定します |
| ビルド出力に `[board] IPRO7AI Reef` の行がない | 設定が別のボード向け | [Reef 用のビルド設定](#reef-configs) のとおり `DEFCONFIG=` または `-d` を追加します |
| `-d` でビルドしたあと、`flash` や `size` で `Binary not found` や `ELF not found` が出る | `-d` がないとスクリプトは `build/` を探す | 同じ `-d` を追加します |
| `✗ Flash tool not found: ipro_iot_tool_macos` | IntelProCube が見つからない | `IPRO_FLASH_TOOL` を設定します |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | USB シリアルポートが複数ある | `-p` または `IPRO_SERIAL_PORT` でポートを指定します |
| `size` が `riscv64-unknown-elf-size` を見つけられない | ツールチェーンがデフォルトのパスにない | `<toolchain dir>/bin/riscv64-unknown-elf-size <elf>` を直接実行します |

## 次のステップ { #next-steps }

- [最初の FreeRTOS アプリケーション](first-app-freertos.md)：Reef で `ipro7ai_reef_demo` をビルド、書き込み、実行します。
- [ビルドと書き込みの流れ](../tutorials/build-and-flash.md)：日常的な編集、ビルド、書き込み、モニターのサイクル。
- [ビルドシステムと設定](../guides/build-system.md)：`.config` のキー、リンカースクリプト、メモリレイアウト。
