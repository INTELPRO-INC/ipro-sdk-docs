---
title: "LE Audio 入門"
description: IPRO7AI Reef EVK で LE Audio ユニキャストヘッドセット ipro_le_audio_headset を実行し、LE Audio 対応スマートフォンとペアリングし、キーで VCP の音量を変え、テストトーンでオーディオ出力を確認します。主な設定と、本リリースで検証済みの範囲も説明します。
migrate_from:
  - "tutorials.html — 教學 4"
---

# LE Audio 入門

このチュートリアルを終えると、IPRO7AI Reef EVK で `ipro_le_audio_headset` が動作します。ボードは `IPRO-LE-Audio` としてアドバタイズし、LE Audio 対応スマートフォンとペアリングして、PACS、ASCS、CAS、VCP などのサービスを提供します。ボードのキーで VCP の音量を変え、テストトーンでスピーカーとヘッドホンの出力を確認し、LE Audio アプリケーションに必要な設定を学びます。

!!! warning "本リリースで検証済みの範囲"
    アプリケーションの README によると、このアプリケーションはプロファイルと ISO データパスの立ち上げ段階のものであり、完成したオーディオ製品ではありません。
    
    - 検証済み：スマートフォンによるスキャン、接続、ペアリング（セキュリティレベル 4）、LE Audio サービス（`1853`、`1850`、`184e`、`1844`）の検出、VCP による音量制御。
    - 未検証：スマートフォンからの音楽ストリーミング。現在、Android はこのファームウェアに対して接続中のオーディオチャネルがないと報告します。デコードした LC3 オーディオの再生と、音響面の検証もまだ完了していません。
    
    `test_tone` コマンドは、LE Audio ストリームを経由せずに DAC を直接駆動します。

## 前提条件 { #prerequisites }

- SW8 を PWR にし、USB-C から給電した IPRO7AI Reef EVK。U6 に IPRO Debug Probe または 3.3 V USB-UART ケーブルを接続します（115200 8N1。配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照）。J2 のヘッドホンは任意です。
- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了し、IntelProCube v0.6.3 のコマンドライン書き込みツール（別途入手）を用意していること。
- コマンドを入力できるシリアルターミナル（[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)を参照）。
- LE Audio に対応し、LE Audio を有効にした Android スマートフォン。アプリケーションの README に記録されているスマートフォンは、Android 17 を搭載した Pixel 10 Pro です。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **Reef 構成をビルドします。**

    ```bash
    make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef
    ```

    出力は `apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin` です。この構成は 2 MB の Flash 向けにリンクされます（`CONFIG_IPRO7_FLASH_2M=y`）。`DEFCONFIG=` を付けずに `make` だけを実行すると、IPRO7 EVB 版がビルドされます。

2. **書き込みます。** Reef をダウンロードモードにしてから（SW1 を押したまま SW2 を短く押し、SW1 を離します。シェル付きのファームウェアが動作している場合は `reboot_dl` でも同じです）、IntelProCube のディレクトリから次を実行します。

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --firmware <SDK>\apps\bluetooth\le_audio\ipro_le_audio_headset\build_reef\build_out\ipro_le_audio_headset_IPRO7.bin
        ```

    このツールは失敗しても終了コード 0 で終了するため、出力に `[All Success]` があることを確認してください。

3. **コンソールを開いてリセットします。** コンソールを 115200 ボーで開き、SW2 を短く押します。起動ログには次の行が含まれます（レベル、時刻、スレッドのフィールドは省略）。

    ```text
    MAIN: IPRO LE Audio Headset v2.0 (Zephyr blestack)
    ...
    BLE_INIT: Advertising started: IPRO-LE-Audio
    KEYS: Keys: SW3 vol-, SW4 vol+, SW5 mute (GPIO<n>/<n>/<n>)
    ```

4. **オーディオ出力を確認します。** 次のコマンドを入力すると、1 kHz のテストトーンが 3 秒間鳴ります。J2 にヘッドホンを挿している場合、スピーカーアンプはオフになり、トーンはヘッドホンからのみ聞こえます。

    ```text
    test_tone 3
    ```

5. **スマートフォンをペアリングします。** スマートフォンの Bluetooth 設定で新しいデバイスとペア設定し、`IPRO-LE-Audio` を選びます。コンソールに次のように表示されます。

    ```text
    BLE_INIT: Connected: <スマートフォンのアドレス>
    BLE_INIT: Security requested: level 2
    BLE_INIT: Security changed: <スマートフォンのアドレス> level <n>
    BLE_INIT: [SMP] Pairing complete: <スマートフォンのアドレス>, bonded=1
    ```

    スマートフォンには、ボードが LE Audio デバイスとして表示されます。ボンディング情報は Flash に保存され、再起動後も保持されます。

6. **キーで音量を変えます。** SW4 で音量を上げ、SW3 で下げ、SW5 でミュートを切り替えます。キー操作は VCP の Volume Renderer を経由するため、接続中のスマートフォンの音量スライダーも連動します。コンソールに次のように表示されます。

    ```text
    VCP_SERVER: Volume state changed: volume=<0-255> mute=<0|1>
    ```

    `vol` と入力すると、現在の音量が表示されます。

7. **状態を確認します。**

    ```text
    leaudio_status
    ```

    `BLE Ready`、受信およびデコードしたオーディオフレームの数、現在のサンプルレート、出力先（`DAC (Speaker)`）が表示されます。

</div>

!!! info "スマートフォンからの音楽ストリーミング"
    本リリースでは、スマートフォンからのストリーミングは検証されていません（このページの冒頭を参照）。お使いのソースがストリームを確立した場合は、コンソールに `Stream … started (Streaming state)` と表示され、`leaudio_status` の `Frames Received` が増え続けます。結果は実際の測定で判断してください。

## 動作確認 { #verify }

- コンソールに `Advertising started: IPRO-LE-Audio` と表示され、`test_tone 3` の音が聞こえます。
- スマートフォンとペアリングでき、コンソールに `Pairing complete: …, bonded=1` と表示されます。スマートフォンが検出するサービスには、CAS（`0x1853`）、PACS（`0x1850`）、ASCS（`0x184E`）、VCS（`0x1844`）が含まれます。
- SW3、SW4、SW5 を押すとコンソールに `Volume state changed` と表示され、スマートフォンの音量スライダーも連動して動きます。

## 主な設定 { #configuration }

LE Audio には、ISO に対応したコントローラーライブラリと、より大きな Exchange Memory が必要です。ホスト側では、役割に応じたプロファイルを有効にします。以下は `defconfig_reef` からの抜粋です。

```ini title="apps/bluetooth/le_audio/ipro_le_audio_headset/defconfig_reef（抜粋）"
# コントローラー：ペリフェラル ACL と 2 本の ISO ストリーム、Bluetooth 5.4 の機能セット
CONFIG_IPRO_BLE_CTLR_LIB="link1_periph"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt54_iso2"
CONFIG_IPRO_BLE_CTLR_CFG_DBG=y
CONFIG_EM_SIZE=32
CONFIG_BT_CONN=1

# ペアリングとボンディング
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_BT_BONDABLE=y

# LE Audio プロファイル
CONFIG_BT_AUDIO=y
CONFIG_BT_AUDIO_RX=y
CONFIG_BT_BAP_UNICAST_SERVER=y
CONFIG_BT_PACS=y
CONFIG_BT_ASCS=y
CONFIG_BT_VCP_VOL_REND=y
CONFIG_BT_CAP_ACCEPTOR=y
CONFIG_BT_CSIP_SET_MEMBER=y

# ISO チャネル
CONFIG_BT_ISO=y
CONFIG_BT_ISO_RX=y
CONFIG_BT_ISO_PERIPHERAL=y

# LC3 コーデック（ビルド済み）と DAC 出力
CONFIG_COMPONENTS_LC3_ENABLE=y
CONFIG_BSP_USING_DAC=y
```

- `bt54_iso2` には 32 以上の `CONFIG_EM_SIZE` が必要です。満たさない場合、ビルドは configure 段階で停止します。
- `CONFIG_IPRO_BLE_CTLR_CFG_DBG=y` はデバッグ版のコントローラーライブラリを選択します。指定しない場合は `_release` ライブラリが使われます。
- このアプリケーションは、メディア制御（MCP）や通話制御（CCP）を有効にしていません。

Reef では `defconfig_reef` だけを使います。DAC がスピーカーと J2 のヘッドホンジャックを駆動し（J2 にヘッドホンを挿すとスピーカーアンプはオフになります）、SW3、SW4、SW5 は VCP を通じて音量を変えます。`dac os 0|1|2` は DAC の出力パスを選択し（Reef のデフォルトは `1` で、512 kHz、ノイズシェーピングあり）、`dac spk <dB>` はスピーカーパスのゲインを設定します。アプリケーションの `.config`、`DAC.config`、`UAC.config` は IPRO7 EVB 用の構成です。

## LE Audio の用語 { #concepts }

| 用語 | 意味 | `ipro_le_audio_headset` での扱い |
|---|---|---|
| CIS | 1 対 1 の接続型アイソクロナスストリーム。ヘッドセットで使われる | 受信側 |
| BIS | 1 対多のブロードキャストアイソクロナスストリーム（Auracast） | 使用しない |
| BAP | オーディオストリームの確立と管理 | 2 つのシンク ASE を持つユニキャストサーバー |
| PACS | 対応するコーデック能力の公開 | LC3：16 / 32 / 48 kHz、7.5 / 10 ms、モノラル、フレームあたり 26～155 オクテット |
| ASCS | オーディオストリームエンドポイント（ASE）の構成と状態 | 有効 |
| VCP | 音量制御 | Volume Renderer |
| CAP / CSIP | 共通オーディオプロファイル／協調セット | CAP Acceptor と CSIP Set Member |
| LC3 | LE Audio の標準コーデック | ビルド済みライブラリ |

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| スマートフォンの Bluetooth 一覧に `IPRO-LE-Audio` が表示されない | スマートフォンで LE Audio が無効になっている、またはボードがすでに別のデバイスに接続している | スマートフォンで LE Audio を有効にします。このアプリケーションは一度に 1 つのリンクしか受け付けず、接続中はアドバタイズを停止します |
| 再書き込み後にペアリングに失敗する | スマートフォンまたはボードが古いボンディング情報を保持している | コンソールで `leaudio_unpair` と入力してボンディング情報を消去し、スマートフォンでデバイスを削除してから、再度ペアリングします |
| `test_tone` の音が出ない | J2 にヘッドホンを挿しているとスピーカーはオフになる。アンプは USB VBUS で動作する | ヘッドホンを抜くか、ヘッドホンで聞きます。USB-C からボードに給電します |
| キーを押すと `volume control not up yet` と表示される | VCP の初期化が完了していない | 起動メッセージが終わるまで待ちます |
| ビルドが configure 段階で `CONFIG_EM_SIZE` に関するメッセージを出して停止する | `bt54_iso2` にはより大きな Exchange Memory が必要 | `CONFIG_EM_SIZE=32` を設定します |

## 次のステップ { #next-steps }

- [オーディオと LE Audio](../guides/audio.md)：オーディオフレームワーク、DAC、PDM、LC3。
- [BLE 開発](../guides/ble.md)：コントローラーライブラリの選択とホストの設定。
- [最初の BLE アプリケーション](first-ble-app.md)：Reef で GATT アプリケーションを変更し、BLE OTA で更新します。
