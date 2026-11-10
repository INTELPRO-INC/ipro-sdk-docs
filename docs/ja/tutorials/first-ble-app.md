---
title: "最初の BLE アプリケーション"
description: IPRO7AI Reef EVK で ipro_ble_remote を実行します。boot2 と A/B パーティションテーブルを使った初回の書き込み、スマートフォンからの GATT サービスの操作、デバイス名の変更、接続時のビープ音の追加、BLE OTA による更新を行います。
migrate_from:
  - "tutorials.html — 教學 1"
---

# 最初の BLE アプリケーション

このチュートリアルを終えると、IPRO7AI Reef EVK で SDK の GATT リファレンスアプリケーション `ipro_ble_remote` が動作し、スマートフォンからボード上の RGB LED を点灯させ、キーの通知を受け取り、ボードとテキストをやり取りできるようになります。続いて、ボードが `IPRO-Hello` としてアドバタイズし、スマートフォンが接続したときにビープ音を鳴らすようにコードを変更し、最後にケーブルを使わずに BLE OTA で新しいファームウェアをボードに送ります。

## 前提条件 { #prerequisites }

- SW7 を CAM、SW8 を PWR にし、USB-C から給電した IPRO7AI Reef EVK。U6 に IPRO Debug Probe または 3.3 V USB-UART ケーブルを接続します（115200 8N1。配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照）。写真撮影機能を使う場合は、OV5640 FLEX-24 カメラモジュールと microSD カードを用意します（任意）。
- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了していること。ツールチェーンが `/opt/toolchain/riscv_ipro7/` にあり、`make` で SDK のアプリケーションをビルドできます。
- [開発環境の準備](../get-started/environment.md#intelprocube)に従ってインストールした IntelProCube 0.7.0.1。コマンドライン書き込みツール `ipro_iot_tool_macos`、`ipro_iot_tool_linux`、または `ipro_iot_tool.exe` と、付属の boot2 イメージ `chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin` を使います。
- 次のいずれかを用意したスマートフォン。
    - Android：アプリケーションディレクトリに含まれるデモアプリ `apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk`。
    - Android または iOS：nRF Connect や LightBlue など、GATT キャラクタリスティックを読み書きできる BLE ツールアプリ。以下の手順ではこのようなツールを使います。
- BLE OTA（手順 10～12）用に、Bluetooth LE、Python 3、`bleak` パッケージを備えた macOS または Linux のコンピューター。

!!! note "Reef ビルドは 2 MB の Flash、boot2、A/B パーティションテーブルを使います"
    `ipro_ble_remote` の Reef 構成 `defconfig_reef` は 2 MB の Flash 向けにリンクし（`CONFIG_IPRO7_FLASH_2M=y`）、BLE OTA を有効にします（`CONFIG_IPRO_BLE_REMOTE_OTA=y`）。書き込みでは、boot2 とアプリケーション独自の A/B テーブル `partition_cfg_2M_remote_ab.toml` も書き込む必要があります。FW A（0x12000、824 KB）は実行スロットで、FW B（0xE0000、512 KB）は OTA パッケージを保持します。`build_freertos.sh` は `--boot2` を渡せないため、このチュートリアルでは書き込みツールを直接実行します。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **Reef 構成をビルドします。** SDK のルートから次を実行します。

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    `DEFCONFIG=` を使うと `.config` は変更されず、`build_reef/` にビルドされます。ビルドに成功すると、最後にリンカーのメモリ表が表示されます（flash の行に `2 MB` と表示されます）。出力は `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin` です。`DEFCONFIG=` を付けずに `make` だけを実行すると IPRO7 EVB 版がビルドされ、これは Reef では動作しません。

2. **Reef をダウンロードモードにします。** SW1（BOOT）を押したまま SW2（RESET）を短く押し、SW1 を離します。シェル付きのファームウェアがすでにボードで動作している場合は、コンソールで `reboot_dl` と入力しても同じです。ダウンロードモードではコンソールに何も表示されません。

3. **boot2、A/B テーブル、ファームウェアを書き込みます。** IntelProCube のディレクトリから次を実行します。

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin `
            --pt <SDK>\apps\bluetooth\ble\ipro_ble_remote\partition_cfg_2M_remote_ab.toml `
            --firmware <SDK>\apps\bluetooth\ble\ipro_ble_remote\build_reef\build_out\ipro_ble_remote_IPRO7.bin
        ```

    `--chip-variant IPRO7AI` は Reef（QFN56）の Flash ピンを選択します。このツールは失敗しても終了コード 0 で終了するため、出力に `[All Success]` があることを確認してください。IPRO Debug Probe を使う場合、ポートは名前が `02` で終わるものです。A/B レイアウトの整合性を保つため、このアプリケーションを再書き込みするときは毎回この完全なコマンドを使います。

4. **コンソールを開いてリセットします。** U6 のポートを 115200 ボーで開き（[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)を参照）、SW2（RESET）を短く押します。最初に boot2 が、続いてアプリケーションが出力します（各行の先頭にあるレベルと時刻のフィールドは省略しています）。

    ```text
    [BOOT2] IPRO7 Boot2 v0.6.0
    ...
    REMOTE_APP: [BLE] Initialized
    REMOTE_APP: [BLE] All services initialized
    REMOTE_APP: [BLE] Advertising: IPRO-Remote
    ```

5. **スマートフォンから接続します。**
    - 付属の Android アプリを使う場合：`ipro_remote_demo.apk` をスマートフォンにコピーし、開いてインストールします（提供元不明のアプリのインストールを許可します）。または、コンピューターで `adb install apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk` を実行します。
    - BLE ツールアプリを使う場合：`IPRO-Remote` をスキャンして接続します。

    コンソールに次のように表示されます。

    ```text
    REMOTE_APP: Connected! Peer: <スマートフォンのアドレス>
    ```

6. **GATT サービスを使います。** BLE ツールアプリで次のキャラクタリスティックを探します。

    | 操作 | キャラクタリスティック | ボード上の結果 |
    |---|---|---|
    | `01` を書き込む | LED State `0xFF11` | WS2812 LED が点灯し（デフォルトは白）、コンソールに `[LED] State: ON` と表示されます |
    | `00 FF 00` を書き込む | LED Colour `0xFF81` | LED が緑になります（3 バイト：R、G、B） |
    | 通知を有効にして SW3 を押す | Button State `0xFF21` | スマートフォンが `01`（押下）と `00`（解放）を受信します |
    | 通知を有効にする | UART TX `0xFF41` | スマートフォンが `Welcome to IPRO Remote!` を受信します |
    | テキスト `hello` を書き込む | UART RX `0xFF42` | コンソールに `[UART RX] hello` と表示され、スマートフォンが `Echo: hello` を受信します |
    | `E8 03 2C 01 1E` を書き込む | Tone `0xFF84` | スピーカー（または J2 のヘッドホン）で 1 kHz の音が 300 ms 鳴ります（周波数と長さはリトルエンディアンの u16、最後のバイトは音量 %） |

    SW1（BOOT）を短く押すとアプリケーションが写真を撮影するため（カメラが必要。microSD カードがあれば `sd:/REMOTE/` にも保存されます）、キーのテストには SW3、SW4、SW5 を使います。コンソールコマンド `reef status` で、ボード、LED、カメラ、温度の状態を確認できます。

7. **コードを変更します。** `apps/bluetooth/ble/ipro_ble_remote/src/app/remote_app.c` の 3 か所を編集します。

    ファイルの先頭では、すでに `CONFIG_IPRO7AI_REEF` ブロック内で `remote_reef.h` をインクルードしています。その下に、`reef_hw_tone()` を宣言している `reef_hw.h` を追加します。

    ```c title="src/app/remote_app.c"
    #if defined(CONFIG_IPRO7AI_REEF)
    #include "remote_reef.h"
    #include "reef_hw.h"
    #endif
    ```

    アドバタイズ名を変更します。

    ```c title="src/app/remote_app.c"
    #define DEVICE_NAME "IPRO-Hello"
    ```

    `connected_cb()` 内の `Connected! Peer` のログ行の後に、ビープ音を追加します。

    ```c title="src/app/remote_app.c"
        IPRO_LOGI(LOG_TAG, "Connected! Peer: %s", addr_str);

    #if defined(CONFIG_IPRO7AI_REEF)
        /* スマートフォン接続時に、スピーカーとヘッドホンジャックで 1 kHz、150 ms のビープ音を鳴らす */
        (void)reef_hw_tone(1000, 150, 30);
    #endif
    ```

    `reef_hw_tone()` は Reef のハードウェアを管理するタスクに要求をキューイングしてすぐに戻るため、BLE の接続コールバックから安全に呼び出せます。このアプリケーションは `-Werror` でコンパイルされるため、警告が 1 つでもあるとビルドが失敗します。

8. **再ビルドして書き込みます。** 手順 1 のビルドコマンドを再度実行し（変更したファイルだけが再コンパイルされます）、コンソールで `reboot_dl` と入力して、手順 3 のコマンドで書き込みます。

9. **再度接続します。** SW2 を短く押すと、コンソールに `REMOTE_APP: [BLE] Advertising: IPRO-Hello` と表示されます。スマートフォンで再度スキャンして `IPRO-Hello` に接続すると、接続の確立時に Reef がビープ音を鳴らします。

10. **OTA ツールを準備します。** ここからは更新を BLE で行うため、U6 は不要です。SDK のルートで、`bleak` を入れた Python 仮想環境を作成します。

    ```bash
    python3 -m venv .venv
    .venv/bin/pip install bleak
    ```

    先にスマートフォンの接続を切断してください。Reef ビルドは 1 つの接続しか許可しません（`CONFIG_BT_CONN=1`）。

11. **OTA パッケージをビルドします。** 小さな変更を加え（例：ビープ音を `reef_hw_tone(2000, 150, 30)` に変更）、再ビルド（手順 1）してから、ビルド結果を boot2 OTA パッケージにまとめます。スクリプトは IntelProCube に結合イメージを作成させ、SDK の `tools/create_ota.py` で圧縮します。スクリプトは IntelProCube フォルダー内の最新の boot2（0.7.0.1 では v0.6.0）を使います。

    === "macOS"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    === "Linux"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    出力は `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota`（約 345 KB）です。OTA が受け付けるのはこの `.xz.ota` パッケージだけで、`.bin` は受け付けません。

12. **BLE で送信して確認します。** `reef_ota.py` はデフォルトで `IPRO-Remote` という名前のデバイスを探します。ボードの名前は変更済みなので、`REMOTE_NAME` を設定します。

    ```bash
    REMOTE_NAME=IPRO-Hello .venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py \
        apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota
    ```

    ツールは、ボードの現在のバージョン、パッケージのサイズと CRC32、転送時間、`verified, slot switched; rebooting` を表示します。ボードの再起動後に再接続し、新しいバージョンを表示します。

    ```text
    running: <カメラ、SD カード、ビルド日時>
    ipro_ble_remote_reef.xz.ota: <バイト数> bytes, CRC32 <値>, <ペイロード> bytes/packet
    sent in <秒数> s (<速度> KB/s)
    verified, slot switched; rebooting
    running: <カメラ、SD カード、ビルド日時>
    ```

    その間、ボードのコンソールには `[OTA] START: …`、`[OTA] CRC32 OK! Switching partition...`、`[OTA] Ready to reboot` が表示され、再起動時に boot2 が `[BOOT2] IPRO7 Boot2 v0.6.0` と `[BOOT2] OTA pending` を表示し、パッケージの SHA256 を確認して FW A に展開し、`[BOOT2] OTA ok` を表示してからアプリケーションを起動します。チップの eFuse に署名鍵が書き込まれていない場合は `[OTA] no eFuse key, package unverified` という行も表示されます。これは署名を検証しないという意味です。`running:` のビルド日時は `src/board/reef_hw.c` から取られるため、`remote_app.c` だけを変更した場合は変わりません。INTELPRO の測定では、macOS、MTU 247 で 345 KB のパッケージの送信に 13～17 秒かかりました。付属の Android デモアプリでも同じ `.xz.ota` パッケージを送信できます。

</div>

!!! danger "標準のパーティションテーブルで OTA を行わないでください"
    Reef では、OTA は `partition_cfg_2M_remote_ab.toml` でのみ動作します。IntelProCube の標準 `partition_cfg_2M.toml` で書き込んだボードでは、OTA はそのテーブルの FW B（0x12A000）に書き込んでそちらに切り替えます。その後、ボードは何も出力しなくなり、ダウンロードモードで再書き込みする以外に復旧できません。

## 動作確認 { #verify }

- コンソールのアドバタイズの行に `IPRO-Hello` と表示され、スマートフォンのスキャン一覧にも同じ名前が表示されます。
- スマートフォンが接続するとボードがビープ音を鳴らし、コンソールに `Connected! Peer: …` と表示されます。
- 手順 6 の LED、キー、UART の操作が引き続き動作します。
- 再起動時にコンソールに `[BOOT2] OTA ok` が表示され、次に接続したときに手順 11 で変更したビープ音が聞こえます。

`main.c` の起動バナーにある `Device Name: 'IPRO-Remote'` は固定文字列で、アドバタイズ名には影響しません。

## 仕組み { #how-it-works }

`main.c` はプラットフォームを初期化して `BLERemote` タスクを作成し、そのタスクが `remote_app_init()` を呼び出します。BLE は決まった順序で起動します。まずコントローラータスク、次に HCI ドライバー、最後に Zephyr ホストです（`src/app/remote_app.c` より）。

```c title="src/app/remote_app.c"
err = ipro_ble_ctlr_controller_init(configMAX_PRIORITIES - 1);  /* IPRO BLE コントローラー */
vTaskDelay(pdMS_TO_TICKS(50));
err = hci_driver_ipro_ble_ctlr_init();                           /* HCI ドライバー */
vTaskDelay(pdMS_TO_TICKS(50));
err = bt_enable(bt_ready_cb);                                    /* Zephyr ホスト */
```

ホストの準備ができると、`bt_ready_cb()` が `bt_set_name(DEVICE_NAME)` を呼び出し、`bt_conn_cb_register(&conn_callbacks)` で接続コールバックを登録し、GATT サービスを初期化して、接続可能なアドバタイズを開始します。サービスは `src/services/remote_services.c` で `BT_GATT_SERVICE_DEFINE()` により静的に定義されています。アドバタイズデータとパラメーターは次のとおりです。`DEVICE_NAME` はアドバタイズデータと `bt_set_name()` の両方に使われます。

```c title="src/app/remote_app.c"
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
};

struct bt_le_adv_param adv_param = {
    .id = BT_ID_DEFAULT,
    .options = BT_LE_ADV_OPT_CONN,
    .interval_min = 160,  /* 100ms (N * 0.625ms) */
    .interval_max = 320,  /* 200ms */
};
int err = bt_le_adv_start(&adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
```

Reef ビルドでは 2 つのサービスが追加されます。OTA `0xFF60`（制御 `0xFF61`、データ `0xFF62`、ステータス `0xFF63`）と、Reef ハードウェアサービス `0xFF80`（LED Colour `0xFF81`、Key Event `0xFF82`、Sound Level `0xFF83`、Tone `0xFF84`、Board Info `0xFF85`）です。LED、キー、スピーカー、SD カード、カメラのドライバーは、出荷時ファームウェアの `apps/platform/ipro7ai_reef_demo/src` にあるソースを元の場所のまま使っています。そのハードウェアに触れるタスクは `src/board/reef_hw.c` だけで、BLE のコールバックはそのタスクに要求を送るだけです。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| 書き込みツールの出力に `[All Success]` がない、または `flash jedec id: 00000000` と表示される | ボードがダウンロードモードになっていない、または Flash ピンが正しくない | 先にダウンロードモードに入ります。コマンドに `--chip-variant IPRO7AI` があることを確認します |
| 書き込みは成功するが、コンソールに何も表示されない | boot2 と A/B テーブルが書き込まれていない、またはボーレートが正しくない | 手順 3 の完全なコマンドで再書き込みします。コンソールを 115200 に設定します |
| スマートフォンに `IPRO-Remote` と表示されたままになる | スマートフォンが古い名前をキャッシュしている | コンソールで `IPRO-Hello` としてアドバタイズしていることを確認してから、スマートフォンの Bluetooth をオフにしてオンに戻し、再度スキャンします |
| LED が点灯しない、またはビープ音が鳴らない | WS2812 とスピーカーアンプは USB VBUS で動作する。J2 にヘッドホンを挿すとスピーカーはミュートされる | 3.3 V だけで給電せず、USB-C から給電します。ヘッドホンを抜くか、ヘッドホンで聞きます |
| 警告でビルドが失敗する | アプリケーションは `-Werror` でコンパイルされる | `#include "reef_hw.h"` は `CONFIG_IPRO7AI_REEF` ブロック内に、呼び出しは関数内に置きます |
| `make_reef_ota.sh` が `IntelProCube tool not found` を表示する | `IPRO_FLASH_TOOL` が未設定で、書き込みツールが PATH 上にない | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`（または `_linux`）を設定します |
| `make_reef_ota.sh` が `build first: …` を表示する | `build_reef/` にまだビルド結果がない | 先に手順 1 を実行します |
| `make_reef_ota.sh` が `boot2 image not found` を表示する | `IPRO_FLASH_TOOL` が指す IntelProCube フォルダーに `chips/ipro7/builtin_imgs/boot2_v*` がない | `IPRO_FLASH_TOOL` を IntelProCube 0.7.0.1 フォルダー内のツールに向けるか、`IPRO_BOOT2` で boot2 の `.bin` を指定します |
| `reef_ota.py` が `IPRO-Remote not found` を表示する | ボードの名前が変更されている、スマートフォンが接続している、またはコンピューターの Bluetooth がオフか使用を許可されていない | `REMOTE_NAME=IPRO-Hello` を設定します。スマートフォンの接続を切断します。macOS では、ターミナルに Bluetooth の使用を許可します |
| `reef_ota.py` が `device error …` を表示する | ボードがパッケージを拒否した、または書き込みに失敗した | `.xz.ota` を送信したことを確認します。コンソールの `[OTA]` 行を確認します |
| OTA 後にボードが復帰しない | boot2 はパッケージを拒否すると USB レスキューモードのままになる | ダウンロードモードに入り、手順 3 のコマンドで再書き込みします |

## 次のステップ { #next-steps }

- [BLE スループットテスト](ble-throughput.md)：2 枚の Reef ボード間のデータレートを測定します。
- [LE Audio 入門](le-audio.md)：Reef で LE Audio ヘッドセットのサンプルを実行します。
- [BLE 開発](../guides/ble.md)：コントローラーライブラリの選択、ホストの構成、API。
- [OTA アップデート](../guides/ota.md)：パーティションテーブル、OTA パッケージの形式、boot2 の更新フロー。
