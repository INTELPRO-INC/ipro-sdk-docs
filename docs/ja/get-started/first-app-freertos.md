---
title: "最初の FreeRTOS アプリケーション"
description: IPRO7AI Reef EVK のスイッチを設定してコンソールを接続し、出荷時ファームウェア ipro7ai_reef_demo をビルド、書き込み、実行して、reef selftest でボードを確認します。
migrate_from:
  - "getting-started.html#freertos-quickstart"
  - "getting-started.html#first-build"
---

# 最初の FreeRTOS アプリケーション

出荷時ファームウェア `ipro7ai_reef_demo` をビルドして IPRO7AI Reef EVK V4.0 に書き込み、コンソールを開いて `reef selftest` を実行し、LED、スピーカー、SD スロット、カメラを確認します。最後には、コンソールに `ipro />` プロンプトが表示され、ボード上の各ブロックがシェルコマンドに応答するようになります。

## 前提条件 { #prerequisites }

- [開発環境の準備](environment.md) が完了していること：`./build_freertos.sh ipro7ai_reef_demo` でビルドでき、IntelProCube の `--help` が実行できる。Windows では [Windows のセットアップと VS Code](windows.md) も参照してください。
- IPRO7AI Reef EVK V4.0、USB-C ケーブル、コンソールケーブル（3.3 V USB-UART 変換アダプターまたは IPRO Debug Probe）。
- オプション：OV5640 FLEX-24 カメラモジュール、microSD カード、J_SPK に接続する 8 Ω スピーカー。これらがない場合、セルフテストの該当する行には「見つからない」という結果が表示されます。
- コマンドライン例は macOS を使っています。Linux では `/dev/ttyUSB0` と `ipro_iot_tool_linux` を使い、Windows では各手順の Windows タブに従ってください。

## スイッチの設定とボードの接続 { #connect }

<div class="ipro-steps" markdown>

1. **スイッチを設定します：** SW7 を **CAM**、SW8 を **PWR** にします。SW7 が GPIO 側だとカメラに電源が供給されず、SW8 が MEAS 側だと IPRO7AI には JP2 経由で電源が供給されます。[スイッチとジャンパー](../hardware/boards/reef-evk.md#jumpers) を参照してください。

2. **コンソールケーブルを U6 に接続します**（ボードの電源はまだ入れません）：

    | U6 ピン | 信号 | USB-UART 変換アダプター |
    |---|---|---|
    | 1 | NC | — |
    | 2 | GND | GND |
    | 3 | TX（GPIO20、Reef の出力） | RX |
    | 4 | RX（GPIO21、Reef の入力） | TX |
    | 5 | BOOT（1 kΩ を介して GPIO41） | オプション：DTR |
    | 6 | RESET（1 kΩ、アクティブ Low） | オプション：RTS |

    IPRO Debug Probe は、CN_UART からピン順が逆のケーブルで接続します。プローブのピン n を U6 のピン 7 − n に接続します。

    !!! warning "ケーブルの向き"
        Debug Probe をストレートケーブルで接続しないでください。UART と制御線が誤ったピンにつながり、プローブの 3.3 V が U6 の RESET にかかります。

3. **電源を入れます：** USB-C を接続します。緑色の電源 LED（LED2）が点灯します。U6 からはボードに電源が供給されません。電源は USB-C からのみ供給されます。

4. **シリアルポートを確認します：** アダプターまたはプローブをコンピューターに接続し、ポートが現れることを確認します。例：macOS では `/dev/cu.usbserial-XXXX`、Linux では `/dev/ttyUSB0`、Windows では `COM5`。Debug Probe の場合は、名前が `02` で終わるポートを使います。[ポートの見分け方](flash-and-monitor.md#ports) を参照してください。

</div>

## ビルド { #first-build }

<div class="ipro-steps" markdown>

1. **出荷時ファームウェアをビルドします**（SDK ルートで実行）。Windows では代わりに、VS Code Extension の `IPRO: Build`（[VS Code Extension のセットアップ](windows.md#installation) を参照）または PowerShell の `build_freertos.ps1`（[コマンドラインでのビルド](windows.md#command-line) を参照）を使います。

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    configure の段階で Reef のボード設定が表示され、ビルドの最後にメモリ使用量とイメージのパスが表示されます（抜粋）：

    ```text
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

    数値はツールチェーンのバージョンによって多少異なります。

2. **出力を確認します：**

    ```bash
    ls apps/platform/ipro7ai_reef_demo/build/build_out/
    ```

    ```text
    ipro7ai_reef_demo_IPRO7.bin    書き込み用のイメージ
    ipro7ai_reef_demo_IPRO7.elf    デバッグシンボル付き
    ipro7ai_reef_demo_IPRO7.map    メモリマップ
    lib/
    ```

</div>

## 書き込みと実行 { #flash-and-run }

<div class="ipro-steps" markdown>

1. **シリアルポートを解放します：** ポートを開いているターミナルプログラムをすべて閉じます。書き込みとコンソールは同じ UART を使います。

2. **ダウンロードモードに入ります：** **SW1 (BOOT)** を押したまま **SW2 (RESET)** を押して離し、SW1 を離します。ダウンロードモード中、コンソールには何も表示されません。

    ボードですでに SDK のファームウェア（工場で書き込まれた出荷時ファームウェアなど）が動作している場合は、コンソールで `reboot_dl` と入力しても同じ状態になります。`reboot to download mode` と表示され、その後は何も表示されなくなります。DTR/RTS 自動ダウンロードケーブルや Debug Probe を使う場合は、[ダウンロードモードに入る](flash-and-monitor.md#download-mode) を参照してください。

3. **書き込みます**（IntelProCube のディレクトリで実行）。`--chip-variant IPRO7AI` は Reef の Flash ピンを選択し、`--pt` は IntelProCube に付属するパーティションテーブルを指定します。

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

    ツールは進行状況を 1 行ずつ表示します（抜粋、タイムスタンプは省略）：

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

    最後に `[All Success]` が表示された場合のみ成功です。ツールは書き込みに失敗しても終了コード 0 で終了するため、終了コードでは判断できません。

4. **コンソールを開きます：** 同じポートを 115200 baud、8N1、フロー制御なしで開きます：

    === "macOS"

        ```bash
        screen /dev/cu.usbserial-XXXX 115200
        ```

        `screen` を終了するには、++ctrl+a++ を押してから ++k++ を押し、`y` と答えます。

    === "Linux"

        ```bash
        picocom -b 115200 /dev/ttyUSB0
        ```

        `picocom` を終了するには、++ctrl+a++ を押してから ++ctrl+x++ を押します。必要に応じて `sudo apt install picocom` でインストールします。

    === "Windows"

        PuTTY で **Serial** を選び、Serial line を `COM5`、Speed を `115200` に設定して **Open** をクリックします。VS Code Extension の `IPRO: Serial Monitor` も使えます。

5. **リセットします：** **SW2 (RESET)** を押します。RGB LED が青色で 1 回ゆっくり明滅して消え、コンソールに起動メッセージが表示されます（抜粋。`(…)` はタイムスタンプ）：

    ```text
    I (…) REEF: ==========================================
    I (…) REEF:   IPRO7AI Reef carrier demo
    I (…) REEF:   UART0 TX=20 RX=21  RGB=G24  SPK_EN=G25(hi)
    I (…) REEF:   CAM: FLEX-24 D0-7=G0-7 XCLK=G22 RST=G34 PWDN=G35
    ...
    I (…) REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    ```

    ++enter++ を押すと `ipro />` プロンプトが表示されます。

</div>

## 動作確認 { #verify }

<div class="ipro-steps" markdown>

1. **キーを確認します：** SW3、SW4、SW5、SW1 (BOOT) を順に押します。RGB LED が赤、緑、青、白に点灯します。

2. **セルフテストを実行します：** コンソールで `reef selftest` と入力します。約 3 秒以内に LED が赤、緑、青と切り替わり、スピーカーから 1 kHz の短いトーンが鳴り、コンソールに次のように表示されます（OV5640 を装着し、SD カードなしの場合）：

    ```text
    ipro />reef selftest
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: __rti_name_ov5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    | 行 | 確認内容 | その他の結果 |
    |---|---|---|
    | `[3/4] SD slot` | カードが挿入されているか、スロットの電源 | カードを挿入すると `something seated` |
    | `[4/4] camera bus` | SCCB で見つかったカメラセンサーとそのアドレス | カメラなしでは `no sensor`、OV2640 では `__rti_name_ov2640 at 0x30` |

3. **コマンドを一覧表示します：** `help` と入力します。`reboot` と `reboot_dl` を含むすべてのシェルコマンドが表示されます。

</div>

### 出荷時ファームウェアのコマンド { #commands }

| コマンド | 動作 |
|---|---|
| `reef status`, `reef selftest` | ボードの状態（ピン、キー、LED、アンプ、検出線）、セルフテスト |
| `led <r> <g> <b>`, `led rainbow`, `led off` | RGB LED の色（0–255。例：`led 40 0 0`）、レインボー効果、消灯 |
| `btn status`, `btn watch` | キーの状態と押された回数、押下と解放のイベントのリアルタイム表示 |
| `spk tone <hz> <ms>`, `hp` | スピーカーで正弦波トーンを再生、ヘッドセット検出のレベル |
| `mic rec pdm <s>`, `mic rec headset <s>`, `mic play`, `mic loop` | オンボードの PDM マイクまたはヘッドセットから PSRAM に録音（最大 10 秒）して再生、またはリアルタイムでモニター |
| `mic sdrec <src> <name> <s>`, `mic usb <src>` | `sd:/rec/<name>.wav` に録音。`mic stop` まで、ボードを USB-C 上の USB マイクとして動作させる |
| `sd mount`, `sd ls`, `sd test` | microSD カード（`sd:` の FatFS） |
| `cam probe`, `cam start`, `cam status`, `cam snap`, `cam bar on`, `cam bar off` | OV5640 カメラ（SW7 を CAM に設定） |
| `reboot`, `reboot_dl` | 再起動、ダウンロードモードで再起動 |

各ブロックの詳細とカメラの立ち上げ手順：[IPRO7AI Reef EVK：出荷時ファームウェア](../hardware/boards/reef-evk.md#reef-demo)。

## 1 つのコマンドで実行：build_freertos.sh { #one-command }

macOS と Linux では、`build_freertos.sh` でビルド、書き込み、モニターをつなげて実行できます。アプリケーションの設定を読み取り、`--chip-variant IPRO7AI` を渡し、アプリケーション自身のボーレートでコンソールを開きます。ボードですでにシェル付きの SDK ファームウェアが動作している場合は、`reboot_dl` を送信してダウンロードモードに入ります。初回は、上記のとおり手動でダウンロードモードに入ってください。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

成功すると `✓ Build succeeded`、ツールの書き込み出力、`✓ Flash succeeded` が表示され、続いて起動メッセージが 30 秒間表示されます。`monitor` は読み取り専用で、コマンドを入力することはできません。最後は `[serial_monitor] TIMEOUT after 30s` で終わり、スクリプトはこれを失敗とみなしますが、これは想定どおりの動作です。すべてのオプション：[macOS／Linux のコマンドライン](command-line.md#build-script)。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| 緑色の電源 LED2 が点灯しない | USB-C がしっかり挿さっていない、または電源から給電されていない | USB-C ケーブルまたは電源を交換します。電源入力は USB-C のみです |
| `[All Success]` が表示されず、ツールがハンドシェイクで止まる | ボードがダウンロードモードになっていない、またはターミナルプログラムがポートを使用している | ターミナルを閉じ、SW1 を押したまま SW2 を押して SW1 を離し、もう一度書き込みます |
| `flash jedec id: 00000000` と `IPRO FLASH MATCH TYPE FAIL` | Flash ピンの設定が誤っている | コマンドに `--chip-variant IPRO7AI` を追加します |
| ツールが `chips/...` のパーティションテーブルを見つけられない | IntelProCube のディレクトリで実行していない | 先に `cd <IntelProCube>` を実行します |
| 書き込みは成功したが、コンソールに何も表示されない | ボードがダウンロードモードのまま、ボーレートやポートの誤り、または RX と TX が逆 | SW2 を押します。115200 で開きます。macOS では `/dev/cu.*` を使います。アダプターの RX と TX を入れ替えます |
| コンソールが文字化けする | ボーレートが 115200 でない | 115200、8N1 で開き直します |
| 出力は表示されるが、入力したコマンドに応答がない | アダプターの TX が U6 のピン 4 に届いていない | U6 のピン 4（RX）への配線を確認します |
| `[4/4] camera bus: no sensor` | カメラがない、ケーブルが挿さっていない、または SW7 が CAM になっていない | USB-C を抜いてからカメラケーブルを挿し直し、SW7 を CAM にします |
| スピーカーから音が出ない | スピーカーがない、またはプラグが緩んでいる | J_SPK に 8 Ω スピーカーを接続します |
| カードを挿入しても `[3/4] SD slot: empty` と表示される | カードが奥まで挿さっていない | カードをロックされるまで押し込みます |
| ビルドでコンパイラーが見つからない | ツールチェーンがデフォルトのパスにない | `CROSS_COMPILE` を設定します。[開発環境の準備](environment.md#toolchain) を参照してください |

書き込みとコンソールに関するその他の問題：[書き込みとシリアルコンソール](flash-and-monitor.md#troubleshooting)。

## 次のステップ { #next-steps }

- [ビルドと書き込みの流れ](../tutorials/build-and-flash.md)：変更後の再ビルド、再書き込み、モニター。
- [最初の独自アプリケーションを作る](../tutorials/first-own-app.md) と [アプリケーションのテスト](../tutorials/testing.md)。
- [書き込みとシリアルコンソール](flash-and-monitor.md)：ダウンロードモードに入るその他の方法、パーティションテーブル、boot2、`mfg` データ。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：すべてのスイッチ、ピン、カメラの立ち上げ手順。
