---
title: "BLE スループットテスト"
description: 2 枚の IPRO7AI Reef EVK ボードで ipro_throughput_test を実行し、1M PHY と 2M PHY で BLE のスループットを測定して、SDK 自身の数値と比較します。
migrate_from:
  - "tutorials.html — 教學 3"
---

# BLE スループットテスト

2 枚の IPRO7AI Reef EVK ボードで同じ `ipro_throughput_test` ファームウェアを実行します。一方をスレーブ（ペリフェラル）、もう一方をマスター（セントラル）とし、カスタム GATT サービスを通じて互いにデータを連続送信します。最終的に 1M PHY と 2M PHY での双方向のスループット値が得られ、同じ条件での SDK の測定値（Reef 間、2M PHY で 1.34 Mbps、1M PHY で 747 kbps）と比較できます。

## 前提条件 { #prerequisites }

- 2 枚の IPRO7AI Reef EVK ボード。それぞれ SW8 を PWR にして USB-C から給電し、U6 に IPRO Debug Probe（または 3.3 V USB-UART ケーブル）を接続します。配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照してください。
- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了し、IntelProCube v0.6.3 のコマンドライン書き込みツール（別途入手）を用意していること。
- ボードごとに、コマンドを入力できるシリアルターミナルを 1 つ（115200 8N1。[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)を参照）。

!!! tip "2 つのシリアルポートを区別する"
    IPRO Debug Probe は `IPRO7 CMSIS_DAP` として認識され、2 つのシリアルポートを持ちます。名前が `02` で終わるポートがボードのコンソール（Reef の UART0）で、`04` は CCI ブリッジです。まず 1 枚目のボードのプローブだけを接続して、現れたポートを控えます（macOS では `ls /dev/cu.*`、Linux では `ls /dev/ttyACM* /dev/ttyUSB*`、Windows ではデバイス マネージャーの COM ポート）。それから 2 枚目を接続します。以下では、2 枚のボードをスレーブボード、マスターボードと呼びます。それぞれにラベルを貼っておくと便利です。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **Reef 構成をビルドします。**

    ```bash
    make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef
    ```

    出力は `apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin` です。リンカーのメモリ使用量の表には、Flash が約 360 KB、224 KB の OCRAM 領域のうち約 205 KB と表示されます。

2. **両方のボードに書き込みます。** 同じファイルを、各ボードにそれぞれのポートから 1 枚ずつ書き込みます。まずボードをダウンロードモードにします。SW1（BOOT）を押したまま SW2（RESET）を短く押し、SW1 を離します。シェル付きのファームウェアがすでにボードで動作している場合は、そのコンソールで `reboot_dl` と入力しても同じです。次に、IntelProCube のディレクトリから以下を実行します。

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --firmware <SDK>\apps\bluetooth\ble\ipro_throughput_test\build_reef\build_out\ipro_throughput_test_IPRO7.bin
        ```

    どちらの実行でも `[All Success]` が表示される必要があります（このツールは失敗しても終了コード 0 で終了します）。書き込みの前に、ポートを使用しているターミナルを閉じます。

3. **両方のコンソールを開いてリセットします。** 両方のターミナルを 115200 ボーで開き、各ボードの SW2 を短く押します。リセットから約 7 秒後に、コンソールに `BLE initialized` と表示されます。Reef には 32.768 kHz の水晶がないため、コントローラーはまず 32 kHz クロック源を評価し、`XTAL32K rejected` と表示して RC32K に切り替えるので、少し時間がかかります。以下のメッセージでは、各行の先頭にあるレベル、時刻、スレッドのフィールドを省略しています。

4. **ボードを接続します。** スレーブで次のように入力します。

    ```text
    tp slave
    ```

    ```text
    TP_APP: Slave started - advertising as 'IPRO-TP-TEST'
    ```

    次に、マスターで入力します。

    ```text
    tp master
    ```

    マスターは `IPRO-TP-TEST` をスキャンして自動的に接続します。マスターに最後の行が表示されるまで待ってから先に進みます。

    ```text
    TP_APP: Found target: IPRO-TP-TEST RSSI:<信号強度> Addr:<アドレス>
    TP_APP: Connected: <アドレス>
    ...
    TP_APP: MTU exchange complete: MTU=247
    ...
    TP_APP: Notifications enabled - ready for test
    ```

5. **接続間隔と PHY を設定します。** マスターで次のように入力します（`tp conn` の単位は 1.25 ms なので、40 は 50 ms です）。

    ```text
    tp conn 40 40
    tp phy 2
    tp status
    ```

    両方のボードに `Connection params updated: interval=40 …` と `PHY updated: TX=2 RX=2` が表示され、`tp status` には `Connection Interval: 50.00 ms` と `PHY: 2M` が表示されます。

6. **ダウンリンク（スレーブからマスター、Notification）を測定します。** マスターで `tp stats` と入力して RX バイト数を控えてから、スレーブで次のように入力します。

    ```text
    tp start 244 10
    ```

    テスト中、スレーブは 1 秒ごとに 1 行を表示し、10 秒後にサマリーを表示します。

    ```text
    [TP] TX: <パケット数> pkts, <バイト数> bytes, <速度> Kbps | RX: 0 pkts, 0 bytes, 0.0 Kbps | Err: 0
    ...
    === Throughput Test Statistics ===
    Duration: <ミリ秒> ms
    TX: <パケット数> packets, <バイト数> bytes, <速度> Kbps (<速度> KBps)
    RX: 0 packets, 0 bytes, 0.00 Kbps (0.00 KBps)
    Errors: 0
    Connection: interval=50.00ms, PHY=2M
    ==================================
    ```

    テストが終わったら、マスターで再度 `tp stats` と入力します。

7. **アップリンク（マスターからスレーブ、Write Without Response）を測定します。** 逆の操作を行います。スレーブで `tp stats`、マスターで `tp start 244 10` と入力し、終了後にスレーブで `tp stats` と入力します。

8. **1M PHY で繰り返します。** マスターで `tp phy 1` と入力し、手順 6 と 7 を繰り返します。双方向を同時に測定するには、両方のボードで同時に `tp start 244 10` と入力します。

</div>

## 動作確認 { #verify }

送信側のサマリーにある TX レートは、ホストスタックが受け付けたパケットを数えたもので、実際に届いた量との差は数パケット以内です。受信側の RX カウンターはテストをまたいで累積するため、受信側のサマリーにある RX レートには意味がありません。到達速度を求めるには、受信側の 2 回の `tp stats` の値から RX バイト数の差をとります。

```text
到達速度 (kbps) = (RX バイト数の差 × 8) ÷ テスト時間 (ms)
```

結果を次のセクションの参考値と比較します。大きく下回る場合は、`tp status` で接続間隔と PHY を確認し、[スループットを制限する要因](#tuning)を参照してください。

## 参考値 { #benchmarks }

以下は `ipro_throughput_test` の README（2026-10-07）に掲載されている測定値です。条件は、2 枚の IPRO7AI Reef EVK ボード、ビルド済みの `link2` コントローラーライブラリ、ATT MTU 247、DLE 251 オクテット、244 バイトのペイロード、8 秒間の連続送信で、速度は受信側が実際に受け取ったパケットから算出しています。「ダウン」はスレーブからマスターへの Notification、「アップ」はマスターからスレーブへの Write Without Response です。

| PHY | 接続間隔 | ダウン／アップ、`CONFIG_IPRO7_BLE_HOTCODE=y`（同梱の構成） | ダウン／アップ、オプション無効 |
|---|---|---|---|
| 2M | 7.5 ms | 1055 / 1056 kbps | 891 / 957 kbps |
| 2M | 15 ms | 1180 / 1180 kbps | 921 / 930 kbps |
| 2M | 30 ms | 1315 / 1315 kbps | 737 / 788 kbps |
| 2M | 50 ms | **1342 / 1333 kbps** | 593 / 642 kbps |
| 1M | 7.5 ms | 526 / 525 kbps | 437 / 492 kbps |
| 1M | 15 ms | 656 / 656 kbps | 559 / 554 kbps |
| 1M | 30 ms | 722 / 721 kbps | 584 / 551 kbps |
| 1M | 50 ms | **747 / 746 kbps** | 535 / 568 kbps |

双方向同時（`CONFIG_IPRO7_BLE_HOTCODE=y`、方向ごとの速度）では、2M PHY で 50 ms のとき 782 / 783 kbps、30 ms のとき 719 / 719 kbps、15 ms のとき 653 / 654 kbps、1M PHY で 50 ms のとき 389 / 390 kbps です。1M PHY で 20 バイトのペイロード（MTU 23 に合わせたサイズ）の場合は約 165 kbps、Coded S8 PHY ではダウンリンクで約 34 kbps です。

## スループットを制限する要因 { #tuning }

- **エアタイム**：251 オクテットのデータ PDU 1 つに、空の確認応答と 2 つのフレーム間隔を加えると、2M PHY で約 1.39 ms、1M PHY で約 2.47 ms かかります。そのため、244 バイトのペイロードでの上限は、2M で約 1.40 Mbps、1M で約 790 kbps です。
- **コネクションイベントの長さ**：コントローラーは次のコネクションイベントをスケジュールできるよう、各イベントを早めに終了します。接続間隔が短いほど、失われる割合が大きくなります。7.5 ms の間隔では 2M のパケットを約 4 つ（約 1.05 Mbps）しか運べないため、大量転送には 30～50 ms の間隔が適しています。レイテンシが重要な場合でも、15 ms なら 2M で 1.18 Mbps が得られます。
- **CPU**：コードを Flash から実行すると、各パケットの処理にかかる時間がパケットのエアタイムより長くなり、CPU がスループットを決めます。同梱の構成の `CONFIG_IPRO7_BLE_HOTCODE=y` は、BLE のパケットごとの処理パスを OCRAM から実行します。約 88 KB の OCRAM が必要で、AI+MM メモリレイアウトや低消費電力設定（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_*`、`CONFIG_OCRAM_NORET_SPLIT`）とは併用できません。
- **バッファーを変更する前に CPU を確認する**：送信側で `tp cpu` と入力してからテストを開始し、終了後に再度 `tp cpu` と入力します。`IDLE` の割合が 50 % を大きく下回る場合は CPU が制限要因であり、ホストやコントローラーのバッファーを増やしても効果はありません。
- **小さいパケット**：ATT MTU が 23（20 バイトのペイロード）の場合、接続間隔はほとんど影響しません。1M PHY で約 165 kbps が目安です。
- **Coded PHY は調整されていない**：アプリケーションは最大 TX 時間として 2120 µs を要求しますが、Coded S8 ではこの時間に PDU あたり約 27 オクテットしか収まりません。

`defconfig_reef` は、`.config` の `CONFIG_EVB=y` を Reef のボード選択に置き換えたもので、BLE の設定は同じです。

```ini title="apps/bluetooth/ble/ipro_throughput_test/defconfig_reef（抜粋）"
CONFIG_IPRO_BLE_CTLR_LIB="link2"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt52"
CONFIG_BT_CONN=2
CONFIG_EM_SIZE=32
CONFIG_BT_L2CAP_TX_BUF_COUNT=10
CONFIG_BT_CONN_TX_MAX=10
CONFIG_IPRO7_BLE_HOTCODE=y
CONFIG_FREERTOS_TIMER_TASK_STACK_WORDS=1024
```

## コマンドリファレンス { #commands }

| コマンド | 説明 |
|---|---|
| `tp slave` | ペリフェラルとして開始し、`IPRO-TP-TEST` をアドバタイズします |
| `tp master [addr]` | セントラルとして開始し、スキャンして接続します。アドレス `XX:XX:XX:XX:XX:XX` を指定することもできます |
| `tp start [size] [sec] [interval_ms]` | このボードから送信を開始します |
| `tp stop` | テストを停止します。アイドル時は切断します |
| `tp stats` | 統計を表示します |
| `tp status` | ロール、状態、接続間隔、PHY を表示します |
| `tp phy <1\|2\|3>` | 1M、2M、または Coded PHY を要求します |
| `tp conn <min> <max>` | 1.25 ms 単位で接続間隔を要求します（レイテンシ 0、スーパービジョンタイムアウト 1 秒） |
| `tp interval <ms>` | 実行中のテストの TX 間隔を変更します |
| `tp cpu` | 前回の `tp cpu` 以降のタスクごとの CPU 使用率と、各タスクのスタック空き容量の最小値を表示します |
| `tp help` | コマンドのヘルプを表示します |

`tp start` のパラメーター：`size` のデフォルトは 244（20～244 バイト）です。`sec` のデフォルトは 10 で、`0` を指定すると `tp stop` まで実行します。`interval_ms` を省略するとフラッドモード（連続送信）になり、指定する場合はパケット間の間隔を 1～1000 ms で指定します。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| 書き込み中に `flash jedec id: 00000000` または `IPRO FLASH MATCH TYPE FAIL` が表示される | Flash ピンの設定が正しくない、またはボードがダウンロードモードになっていない | コマンドに `--chip-variant IPRO7AI` があることを確認し、先にダウンロードモードに入ります |
| 書き込みツールがポートを開けない | ターミナルがまだ同じポートを使用している | 書き込みの前にターミナルを閉じます |
| 再試行のたびに `IPRO FLASH WRITE CHECK FAIL` が表示される | 一部のイメージで発生する | IntelProCube の ini で `decompress_write = false` を設定して書き込み、その後元に戻します |
| マスターが別のボードに接続する | 近くで複数の `IPRO-TP-TEST` がアドバタイズしている | 他のテストボードの電源を切るか、スレーブのアドレスを指定します（`tp master XX:XX:XX:XX:XX:XX`） |
| `Cannot start test - notifications not enabled by client` | 接続後のサービスディスカバリが完了していない | マスターに `Notifications enabled - ready for test` が表示されるまで待ちます |
| 速度が参考値を大きく下回る | 接続間隔や PHY が想定と異なる、または CPU の負荷が高い | `tp status` で接続間隔と PHY を確認し、続いて送信側の `tp cpu` を確認します |
| `tp phy 3` の約 1 秒後にリンクが切断される（reason 0x08） | Coded PHY への切り替え時にまれに発生する | 再接続して再度切り替えます |

## 次のステップ { #next-steps }

- [BLE 開発](../guides/ble.md)：コントローラーライブラリ（`link1_periph`、`link1`、`link2`、`link4`）とホストの設定。
- [LE Audio 入門](le-audio.md)：Reef で LE Audio ヘッドセットのサンプルを実行します。
- [サンプル](../examples/index.md)：その他の BLE アプリケーションとその Reef 構成。
- [アプリケーションのテスト](testing.md)：`serial_monitor.py` で各ボードにコマンドを送って結果を待ち、測定をスクリプト化します。
