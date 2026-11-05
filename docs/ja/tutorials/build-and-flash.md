---
title: "ビルドと書き込みの流れ"
description: IPRO7AI Reef EVK 上での編集、ビルド、書き込み、モニターのループです。1 回の反復を build_freertos.sh の 1 行で行い、別構成、クリーンビルド、メモリ使用量の読み方も扱います。
migrate_from:
  - "tutorials.html — Tutorial 2"
---

# ビルドと書き込みの流れ

日々の開発は、編集、ビルド、書き込み、コンソールの確認というループです。このチュートリアルでは、IPRO7AI Reef EVK の出荷時ファームウェア `ipro7ai_reef_demo` の起動バナーを変更し、`build_freertos.sh` の 1 行でビルド、書き込み、モニターを行って、コンソールに自分のテキストが表示されることを確認します。続いて構成の切り替え、クリーンビルド、メモリ使用量の読み方を扱います。初めてのインストールと書き込みについては、先に[最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了してください。

## 前提条件 { #prerequisites }

- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了していること。ボード上で `ipro7ai_reef_demo` が動作し、コンソールが `reef selftest` に応答します。
- macOS または Linux。`build_freertos.sh` には bash が必要です。Windows では PowerShell で `build_freertos.ps1`（アクションとオプションは同じ）を使うか、[Windows のセットアップと VS Code](../get-started/windows.md#command-line) のとおり VS Code Extension でビルドと書き込みを行います。ループは同じです。
- すべてのコマンドは SDK のルートから実行します。例は macOS のものです。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **環境を設定します。** このターミナルウィンドウで一度だけ設定すれば、以降のコマンドはすべてこの設定を使います。

    ```bash
    export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
    export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
    export IPRO_FLASH_PT=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
    ```

    Linux では `ipro_iot_tool_linux` と `/dev/ttyUSB0` を使います。`IPRO_FLASH_PT` はこのウィンドウでのすべての `flash` に適用されます。独自のパーティションテーブルを持つアプリケーションに移るときは、`unset IPRO_FLASH_PT` で解除するか、`-P` で上書きします。

2. **コードを編集します。** `apps/platform/ipro7ai_reef_demo/main.c` を開き、`main()` 内の起動バナーに自分のテキストを追加します。

    ```c title="apps/platform/ipro7ai_reef_demo/main.c"
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **ビルド、書き込み、モニターを行います。** ポートを使用しているターミナルプログラムを閉じてから、次を実行します。

    ```bash
    ./build_freertos.sh -t 15 build flash monitor ipro7ai_reef_demo
    ```

    実行中のファームウェアが `reboot_dl` を受け取って自動的にダウンロードモードに入るため、ボタン操作は不要です。出力は順に次のとおりです（抜粋）。

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    → Building ipro7ai_reef_demo...
    ✓ Build succeeded (14s)
      Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
      Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
    → Entering download mode...
    reboot to download mode
    → Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
    [...] - Chip name is ipro7
    ...
    [...] - [All Success]
    ✓ Flash succeeded (…)
    → Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
    [serial_monitor] Sent: reboot
    ...
    I (…) REEF:   IPRO7AI Reef carrier demo - my build
    ...
    [serial_monitor] TIMEOUT after 15s
    ✗ Action 'monitor' failed — stopping.

    Summary:
      ✓ build
      ✓ flash
      ✗ monitor (exit 2)
    ```

    `monitor` は `-t` で指定した秒数だけ読み取って終了コード 2 で終わるため、スクリプトはこれを失敗として表示します。これは想定どおりです。`build` と `flash` に ✓ が付いていれば、新しいファームウェアがボード上で動作しています。

4. **対話的に試します。** ターミナルプログラム（例：`screen /dev/cu.usbserial-XXXX 115200`）でコンソールを開き、`reef status` または `led 0 40 0` と入力して、新しいファームウェアが応答することを確認します。次の書き込みの前にターミナルを閉じます。

5. **繰り返します。** 変更するたびに手順 3 を再度実行します。コードがコンパイルできるかどうかだけを確認するには、`build` だけを実行します。

    ```bash
    ./build_freertos.sh build ipro7ai_reef_demo
    ```

</div>

## 動作確認 { #verify }

- `Summary` で `build` と `flash` に ✓ が表示されます。
- コンソールの起動メッセージに `IPRO7AI Reef carrier demo - my build` が含まれます。
- SW3、SW4、SW5 で引き続き LED が赤、緑、青に点灯し、`reef selftest` の出力は変更前と同じです。

## build_freertos.sh のアクションとオプション { #actions }

このチュートリアルでは `build`、`flash`、`monitor` を、`-t`（モニター時間）、`-d`（別構成）、`-P`（パーティションテーブル）とともに使います。アクションは順に実行され、最初の失敗で停止します。その他のアクション（`clean`、`size`、`test`）と、すべてのオプションおよび環境変数については、[macOS／Linux のコマンドライン](../get-started/command-line.md#build-script)を参照してください。

## 別構成とビルドディレクトリ { #variants }

1 つのアプリケーションが複数の構成ファイルを持つことがあります。`-d` で別構成を選ぶと、`build_<名前>/` にビルドされ、アプリケーションの `.config` は変更されません。

```bash
./build_freertos.sh -d defconfig_wifi_ipro6s build ipro7ai_reef_demo        # build_wifi_ipro6s/ にビルド
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam       # USB ウェブカメラ
```

- `flash` と `size` はイメージを見つけるのに `-d` を使います。別々に実行する場合は、それぞれに同じ `-d` を指定します。
- ビルドは構成を `build_<名前>/.config` にコピーします。編集はアプリケーションディレクトリにある元のファイルに対して行います。
- `ipro7_uvc_cam` を `defconfig_reef_ov5640` で書き込み、OV5640 を取り付けると、Reef の USB-C に USB カメラ（`3896:0701`）が現れ、コンピューター上の任意のカメラアプリケーションで映像を表示できます。
- Reef のすべての構成とそのビルドコマンドは [Reef のビルド構成](../get-started/command-line.md#reef-configs)にあります。初回の書き込みで boot2 や `mfg` データが必要なアプリケーションについては、[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md#partition-tables)を参照してください。

## クリーンビルド { #clean-build }

`.config` や別構成を変更した後、特に Flash サイズ、PSRAM、AI、BLE コントローラーのオプションを変更した後は、ビルドの前にクリーンを行います。`clean` は対応するビルドディレクトリだけを削除します。

```bash
./build_freertos.sh clean build ipro7ai_reef_demo                            # build/ を削除して再ビルド
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo   # build_wifi_ipro6s/ を削除して再ビルド
```

完了すると、`clean` は `✓ Clean complete` を出力します。

## メモリ使用量の読み方 { #memory-usage }

リンク工程では、各メモリ領域の使用量が出力されます。`make` ではターミナルに表示され、`build_freertos.sh` では `build.log` に書き込まれます。

```bash
grep -A5 "Memory region" apps/platform/ipro7ai_reef_demo/build/build.log
```

デフォルト構成の `ipro7ai_reef_demo` では次のようになります。

```text
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
```

- `flash` はリンク時に使われる Flash の上限です。`ipro7ai_reef_demo` はデフォルトで 1 MB のレイアウトでリンクされます（configure 段階で `-- IPRO7 flash: 1M (default, on-chip)` と出力されます）。Reef のパッケージ内 Flash が JEDEC `0xEF4015`（2 MB）を返す場合は、`.config` に `CONFIG_IPRO7_FLASH_2M=y` を追加すると全容量を使えます。
- `flash` の割合が 100 未満でも、イメージがファームウェアパーティションに収まるとは限りません。`Binary:` の後に表示される `.bin` のサイズを、書き込みに使うテーブルのファームウェアパーティションと比較してください。`partition_cfg_2M.toml` では 1180 KB です。
- `ocram` はオンチップの OCRAM です。AI が無効の場合、この領域は 256 KB から BLE が使う `CONFIG_EM_SIZE` を引いたサイズで、configure 段階で `-- AI disabled: OCRAM=256KB` のような行が出力されます。AI が有効の場合はレイアウトが異なります。各領域のサイズを決める設定については、[ビルドシステムと設定](../guides/build-system.md)を参照してください。

`size` アクションは、`.elf` の合計サイズとセクションごとのサイズを一覧表示します。

```bash
./build_freertos.sh size ipro7ai_reef_demo
```

```text
→ Size report for ipro7ai_reef_demo_IPRO7.elf

   text    data     bss     dec     hex filename
 235928   14008   49588  299524   49204 <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf
...
```

これらの数値は V2.2.0 のビルドによるもので、ツールチェーンのバージョンや変更内容によって変わります。

## スクリプトが自動で設定する値 { #script-defaults }

`build_freertos.sh` は書き込みパラメーターをアプリケーションの構成から読み取るため、Reef では追加の指定は不要です。

| パラメーター | 取得元 |
|---|---|
| `--chip-variant` | 構成に `CONFIG_IPRO7AI_REEF=y` がある場合は `IPRO7AI`。`-c` または `IPRO_CHIP_VARIANT` で上書きできます |
| `--pt` | `-P` または `IPRO_FLASH_PT`。どちらもない場合は `--pt` を渡さず、ツール自身のデフォルトテーブルが使われます |
| `reboot_dl` と `monitor` のボーレート | 構成の `CONFIG_PLATFORM_UART_BAUDRATE`。未設定の場合は 115200（`ipro7_jpeg_decode` の Reef 構成では 921600） |
| 書き込みのボーレート | 常に 921600 |

スクリプトは boot2 や `mfg` データを渡せず、`--chipname` は `ipro7` に固定されています。それらが必要な場合は IntelProCube を直接実行してください。[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md#build-script)を参照してください。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| `✗ Build failed` と、最後の 30 行にコンパイラーエラーが出る | コードのエラー | メッセージに従って修正します。完全なログは `build.log` にあります |
| `✗ Flash failed`。ツールがハンドシェイクで止まる | ファームウェアが `reboot_dl` に反応しなかった（シェルがない、ハングしている、またはボーレートが異なる）、またはターミナルプログラムがポートを使用している | ターミナルを閉じ、SW1 を押したまま SW2 を押して SW1 を離し、`flash` だけを実行します |
| `✗ Flash tool not found: …` | `IPRO_FLASH_TOOL` が設定されていない新しいターミナルウィンドウ | 手順 1 をやり直すか、`export` 行をシェルの起動ファイルに追加します |
| `✗ Binary not found: …` | `flash` の前にビルドしていない、または `-d` を指定していない | `build` を追加するか、ビルド時に使った `-d` を指定します |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | `IPRO_SERIAL_PORT` が未設定で、複数のポートがある | `IPRO_SERIAL_PORT` を設定するか、`-p` を追加します |
| コンソールに自分のテキストが表示されない | 書き込みに失敗した、または古い出力を見ている | `Summary` で `flash` に ✓ があることを確認し、手順 3 を再度実行します |
| `.config` の変更が反映されない | 古いビルド結果が残っている | `clean build` を実行します |
| 別のアプリケーションの書き込みや起動に失敗する | `IPRO_FLASH_PT` が前のアプリケーションのテーブルを指したままになっている | `unset IPRO_FLASH_PT` を実行し、`-P` で正しいテーブルを指定します。[パーティションテーブル](../get-started/flash-and-monitor.md#partition-tables)を参照してください |

## 次のステップ { #next-steps }

- [最初の独自アプリケーションを作る](first-own-app.md)：独自のアプリケーションを作り始めます。
- [アプリケーションのテスト](testing.md)：アプリケーションの出力を自動でチェックします。
- [macOS／Linux のコマンドライン](../get-started/command-line.md)：`build_freertos.sh` のすべてのアクション、オプション、制限。
- [ビルドシステムと設定](../guides/build-system.md)：`.config` のキー、リンカースクリプト、メモリレイアウト。
