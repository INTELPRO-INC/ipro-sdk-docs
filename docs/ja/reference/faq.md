---
title: "よくある質問"
description: IPRO7AI Reef EVK でのビルド、書き込みとコンソール、BLE、プラットフォームとネットワーク、デバッグに関するよくある質問への簡潔な回答と、詳細ページへのリンクです。
migrate_from:
  - "faq.html"
---

# よくある質問

各回答は結論から始まります。操作が必要な場合は、コマンドと表示される内容を示し、詳細ページへリンクしています。例は IPRO7AI Reef EVK V4.0 を対象にしています。エラーメッセージの一覧は [デバッグとトラブルシューティング](debugging.md#troubleshooting) を参照してください。

## ビルド { #build }

### SDK、書き込みツール、ツールチェーンはどこで入手できますか？ { #get-tools }

- **SDK V2.2.0**：[GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) から `IPRO-SDK-V2.2.0.tar.gz` をダウンロードし、同じページの SHA-256 と照合してから展開します。

    ```bash
    shasum -a 256 IPRO-SDK-V2.2.0.tar.gz      # Linux では sha256sum。リリースページの値と一致すること
    tar xzf IPRO-SDK-V2.2.0.tar.gz
    cat IPRO-SDK-V2.2.0/VERSION.txt
    ```

    `VERSION.txt` には `IPRO7: IPRO-SDK-V2.2.0`、`IPRO6: IPRO-SDK-V2.2.0`、`Release Date: 2026-11-03` と表示されます。
- **RISC-V ツールチェーン**：V2.2.0 には含まれていません。INTELPRO にお問い合わせください。デフォルトで `/opt/toolchain/riscv_ipro7/` にインストールされます。
- **IntelProCube コマンドライン書き込みツール**（`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe`）：V2.2.0 には含まれていません。[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) から 0.7.0.1 をダウンロードしてください。[開発環境の準備](../get-started/environment.md#intelprocube)を参照してください。
- **Windows オンラインインストーラー 3.6.0 と VS Code 拡張機能 3.3.0**：最新版です。インストーラーは [ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest) からダウンロードします。SDK V2.2.0 と Windows 用ツールチェーンを直接インストールします。[Windows のセットアップと VS Code](../get-started/windows.md) を参照してください。
- **IPRO AI Studio**：SDK には含まれていません。[GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) からダウンロードしてください。

### build_freertos.sh と make -C の違いは何ですか？ { #build-cli-vs-make }

`make -C apps/<category>/<app>` は 1 つのアプリケーションをビルドし、フルパスが必要です。`build_freertos.sh` は `clean`、`flash`、`monitor`、`size`、`test` を追加し、アプリケーション名だけを受け取り、アクションを連結できます。

```bash
make -C apps/platform/ipro7ai_reef_demo
./build_freertos.sh clean build ipro7ai_reef_demo
```

どちらも `<app>/build/build_out/` に同じ出力を生成します。`build_freertos.sh flash` は Reef 用の設定に対して自動で `--chip-variant IPRO7AI` を選び、`-P` でパーティションテーブルを受け取ります。`monitor` はアプリケーション自身のボーレートでコンソールを開きます。`--boot2` や `--mfg` は渡せず、IPRO6S の書き込みもできません。これらには IntelProCube ツールを直接使ってください。[ツールのコマンドライン](tools.md#build-cli) を参照してください。

### Reef で動くアプリケーションと、選ぶべき設定は？ { #reef-apps }

40 個のアプリケーションのうち 9 個に Reef 用の設定があります。単純な `make` で Reef 向けにビルドされるのは `ipro7ai_reef_demo`、`ipro_reef_teach`、`ipro_agora_sentino` だけです。それ以外のアプリケーションの `.config` は IPRO7 EVB または IPRO7AI EVK を対象にしているため、`DEFCONFIG=` で Reef 用の設定を選択します。

| アプリケーション | ビルドコマンド（SDK ルートで実行） |
|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` |
| `ipro7ai_reef_demo`（Wi-Fi と RTSP） | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` |
| `ipro7_uvc_cam`（ウェブカメラ） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` |
| `ipro7_uvc_cam`（じゃんけん） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef`（コンソール 921600） |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` |

`DEFCONFIG=defconfig_<name>` は `build_<name>/build_out/` にビルドし（例：`defconfig_reef` なら `build_reef/build_out/`）、`.config` は変更しません。設定ファイルが Reef 用かどうかを確認するには：

```bash
grep CONFIG_IPRO7AI_REEF apps/bluetooth/ble/ipro_ble_remote/defconfig_reef
```

Reef 用の設定であれば `CONFIG_IPRO7AI_REEF=y` と表示されます。各アプリケーションのパーティションテーブル、`--boot2`、`--mfg`、USB ID は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples) に、その他のアプリケーションに必要なボードは [サンプル](../examples/index.md) にあります。

### .config を変更しましたが、依存するオプションが反映されません。なぜですか？ { #kconfig }

ビルドは `.config` を書かれたとおりに読み、`cmake/generate_autoconf.cmake` でそこから `autoconf.h` を生成します。Kconfig ファイルはオプションを説明しているだけで、`select`、`depends on`、デフォルト値は適用されません。そのため、依存するオプションは自分で `.config` に書く必要があります。例えば、`CONFIG_AI_SUPPORT=y` には `CONFIG_USE_PSRAM=y` も必要です。唯一の例外は Reef の水晶発振子調整値で、設定に `CONFIG_IPRO7_XTAL_CAPCODE` がない場合はビルドが 95 を追加します。

`make menuconfig` には `tools/kconfig/menuconfig.py` が、`make defconfig` には `configs/` ディレクトリが必要ですが、どちらも同梱されていません。`.config` を直接編集するか、コピーを `defconfig_<name>` として保存し、`DEFCONFIG=` でビルドしてください。[ビルドシステムと設定](../guides/build-system.md) を参照してください。

### ツールチェーンが見つからない、またはデフォルトのパスにない { #toolchain }

ツールチェーンのプレフィックスは、次の順で決まります：環境変数またはコマンドラインの `CROSS_COMPILE`、設定ファイルの `CONFIG_CROSS_COMPILE`、`project.build` のデフォルト `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-`（Windows にはデフォルトはありません）。40 個の `.config` のうち 30 個が `CONFIG_CROSS_COMPILE` を設定しています。ツールチェーンが別の場所にある場合：

```bash
export CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-
make -C apps/platform/ipro7ai_reef_demo
```

構成時に `[toolchain] Vendor toolchain detected …` と表示されれば、INTELPRO ツールチェーンが見つかっています。`.config` の `CONFIG_CPU_ID="intelpro_ipro7"` はそのままにしてください。`build_freertos.sh size` は常にデフォルトのパスにある `size` を使います。

### Windows でビルドできますか？ { #windows }

はい。IPRO SDK Online Setup でインストールした SDK は Windows でのビルドの問題が修正され、PowerShell 版の `build_freertos.ps1` が追加されているため、PowerShell や VS Code でビルド、書き込み、コンソールの表示ができます。[Windows のセットアップと VS Code](../get-started/windows.md) を参照してください。

GitHub からダウンロードしたパッケージをそのまま使う場合、コマンドラインの手順は macOS と Linux が対象です。`build_freertos.sh` は bash スクリプトで、`tools/serial_monitor.py` は termios を使うため、どちらも Windows では動作しません。`project.build` には Windows 用の分岐があり、次の条件があります。

- Windows にはデフォルトのツールチェーンパスがなく、`.config` の `CONFIG_CROSS_COMPILE` は Unix のパスなので、ビルドのたびに `CROSS_COMPILE` を渡します：`make -C apps/platform/ipro7ai_reef_demo CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-`。
- `cmake` と `python`（`python3` ではない）が `PATH` 上にある必要があります。同梱の `tools/cmake/` は Linux 専用です。
- 書き込みは `ipro_iot_tool.exe` と `COM5` などのポートで行います。コンソールは Windows の任意のシリアルターミナルで開きます。

Windows でどのシェルや `make` を使うかは、パッケージ自体には記載されていません。Online Setup でインストールした環境を使ってください。

### Flash または RAM が足りない { #memory }

まずビルドの最後にリンカーが表示するメモリ領域の使用量を確認し、`./build_freertos.sh size <app>` と `.map` ファイルで最も大きな使用箇所を探します。[サイズとメモリの解析](tools.md#size-analysis) を参照してください。OCRAM は 256 KB で、BLE コントローラーの Exchange Memory（`CONFIG_EM_SIZE`）はこの中から確保されます。`CONFIG_AI_SUPPORT` と `CONFIG_MM_SUPPORT` の両方を有効にすると、OCRAM 領域は 64 KB または 48 KB に縮小します。不要なコンポーネントを無効にするか、大きなバッファーを PSRAM（`CONFIG_USE_PSRAM=y`）に移してください。Flash はデフォルトで 1 MB のレイアウトでリンクされます。`CONFIG_IPRO7_FLASH_2M=y` で 2 MB のレイアウトを選択します。Reef の各設定で使われる値は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#bsp) にあります。

## 書き込みとコンソール { #flash-console }

### 書き込みに失敗します。何を確認すればよいですか？ { #flashing }

次の順に確認してください。

1. **判定行**：ツールの出力に `[All Success]` がありますか。ツールは失敗しても終了コード 0 を返します。
2. **チップの設定**：Reef では `--chip-variant IPRO7AI` を使います。ツールは前回の設定を記憶しているため、ボードを切り替えたときは必ず再指定してください。出力に `flash jedec id: 00000000` または `IPRO FLASH MATCH TYPE FAIL` がある場合は、これが原因です。
3. **ダウンロードモード**：SW1（BOOT）を押したまま SW2（RESET）を押して離し、SW1 を離します。コンソールには何も表示されないはずです。またはコンソールで `reboot_dl` と入力すると、`reboot to download mode` と表示されます。その他の方法は [ダウンロードモードに入る](debugging.md#download-mode) にあります。
4. **シリアルポート**：他のモニターを閉じます。macOS では `/dev/cu.*` を使います。IPRO Debug Probe では名前が `02` で終わるポートを使います。
5. **パーティションテーブル**：`ipro7ai_reef_demo` と `ipro7_uvc_cam` は `--pt chips/ipro7/partition/partition_cfg_2M.toml` を使います。`ipro_ble_remote` の OTA ビルドは、初回に `--boot2` と `partition_cfg_2M_remote_ab.toml` が必要です。`ipro_reef_teach` は専用の `partition_reef_teach.toml` を `--skip-ota` と `--mfg` とともに使います。各アプリケーションの一覧は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples) にあります。

書き込み後、SW2 を押してリセットします。コンソールにアプリケーションの起動メッセージが表示されれば成功です。手順の全体は [書き込みとシリアルコンソール](../get-started/flash-and-monitor.md) にあります。

### コンソールが文字化けする、または何も表示されない { #console }

文字化けの原因はたいていボーレートの不一致です。ボーレートは設定ファイルの `CONFIG_PLATFORM_UART_BAUDRATE` で、未設定の場合は 115200 です。Reef 用の設定はすべて 115200 で、例外は `ipro7_jpeg_decode` の `defconfig_reef`（921600）だけです。`build_freertos.sh monitor` はアプリケーションのボーレートを自動で使います。自分でポートを開く場合は `--baud` を指定します。

```bash
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0
```

何も表示されない場合：ボードがまだダウンロードモードになっている（SW2 を押す）、U6 の TX / RX が逆になっている（U6 のピン 3 が Reef の TX）、またはプローブの `04` ポートを開いている可能性があります。`serial_monitor.py` は出力の読み取りと 1 つのコマンドの送信しかできません。コマンドを 1 行ずつ入力するには、`screen /dev/cu.usbserial-XXXX 115200` などのシリアルターミナルを使ってください。

### macOS の /dev/cu.* と /dev/tty.* の違いは何ですか？ { #macos-serial }

macOS は同じシリアルデバイスに対して 2 つのノードを作成します。`/dev/cu.*` はすぐに開けますが、`/dev/tty.*` はキャリア検出（DCD）信号を待つため、プログラムが止まってしまいます。常に `/dev/cu.*` を使ってください。

`Resource busy` は、別のプログラム（別のモニター、IDE、`stty -f` など）がポートを使用していることを示します。`lsof /dev/cu.usbserial-XXXX` で特定して閉じ、モニターは常に 1 つだけ開くようにしてください。

## BLE { #ble }

### どの BLE コントローラーライブラリを使えばよいですか？ { #ble-variant }

ライブラリは `.config` の 3 つの設定で選択します：`CONFIG_IPRO_BLE_CTLR_LIB`（`link1_periph` はペリフェラルとブロードキャスター専用。セントラルや複数リンクには `link1`、`link2`、`link4` を使います）、`CONFIG_IPRO_BLE_CTLR_FEATURE`（`bt54_iso2` は ISO / LE Audio を追加し、`CONFIG_EM_SIZE=32` が必要）、`CONFIG_IPRO_BLE_CTLR_CFG_DBG`（未設定で `_release` ライブラリを選択）。`CONFIG_BT_CONN` はライブラリのリンク数を超えてはいけません。構成時に CMake が表示する `[ipro_ble_controller] Using prebuilt <file>` が、実際にリンクされたライブラリです。詳しい規則は [BLE 開発](../guides/ble.md) にあります。最も近い Reef 用の設定（例：`ipro_ble_remote/defconfig_reef`）から始めてください。

### BLE コントローラーのソースは入手できますか？ { #ble-prebuilt }

いいえ。IPRO BLE コントローラーは `components/wireless/bluetooth/ipro_ble_controller/lib/` のビルド済みライブラリとしてのみ提供されます。IPRO7 用のライブラリは 16 個で、4 つのリンク構成 × 2 つの機能プロファイル × debug / release です。本リリースには IPRO6S 用の BLE コントローラーライブラリはなく、IPRO6S アプリケーションは Wi-Fi のみです。

次の設定はコントローラーをソースからビルドするため、このパッケージではビルドできません：`CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`。別のライブラリの組み合わせやこれらの機能が必要な場合は、INTELPRO にお問い合わせください。

### リセット後にボンディング情報が失われる { #ble-bonding }

ボンディングのキーはホストの Settings に保存されます。`ipro_le_audio_headset` の `defconfig_reef` を参考にしてください。

```ini title=".config"
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_EASYFLASH4=y
```

`bt_enable()` の ready コールバックで、まず `ipro_ble_ctlr_hcitl_host_ready()` を呼び出し、アドバタイズを開始する前に `settings_load_subtree("bt")` を呼び出して戻り値を確認します。先にアドバタイズすると、ボンディング済みのスマートフォンが接続したときにキーが見つからず、再度ペアリングすることになります。`ipro_ble_remote` の設定はボンディング情報を保存しません。ボードからボンディング情報が失われたのにスマートフォンに古い情報が残っている場合は、スマートフォンの Bluetooth 設定でデバイスを削除してから再度ペアリングしてください。

### BLE のスループットはどのくらいですか？ { #ble-throughput }

2 台の IPRO7AI Reef EVK 間で `ipro_throughput_test` を使って測定した結果（ビルド済み `link2` コントローラー、ATT MTU 247、DLE 251 バイト、244 バイトのパケット、接続間隔 50 ms、`CONFIG_IPRO7_BLE_HOTCODE=y`、片方向 8 秒間）：2M PHY で約 1.34 Mbps、1M PHY で約 747 kbps。この数値はこの条件でのものであり、あらゆる状況に当てはまるものではありません。

大量のデータには、2M PHY、30–50 ms の接続間隔、244 バイトのパケットを使ってください。手順と全結果は [BLE スループットテスト](../tutorials/ble-throughput.md) にあります。

### ファームウェアを無線で更新するには？ { #ota }

Reef では、`ipro_ble_remote` の `defconfig_reef` が BLE OTA（GATT サービス `0xFF60`）を提供します。boot2 と A/B パーティションテーブル `partition_cfg_2M_remote_ab.toml` が必要です。

1. 初回は `--boot2` と `--pt …/partition_cfg_2M_remote_ab.toml` で書き込みます。起動メッセージは `[BOOT2] IPRO7 Boot2 v0.6.0` から始まります。
2. `make_reef_ota.sh` で `build_reef/build_out/ipro_ble_remote_reef.xz.ota` を生成します。V2.2.0 では、先にスクリプトの boot2 のパスを v0.6.0 に書き換えます（[OTA アップデート](../guides/ota.md#hands-on)の手順 4）。
3. `reef_ota.py` または Android デモアプリ `ipro_remote_demo.apk` でパッケージを送信します。再起動後、ボードは新しいファームウェアで動作します。

標準の `partition_cfg_2M.toml` で書き込んだ Reef では、絶対に OTA を実行しないでください。ボードがまったく応答しなくなり、ダウンロードモードから書き込み直す必要があります。コマンドは [Reef OTA ツール](tools.md#reef-ota-tools) に、全体の流れは [OTA アップデート](../guides/ota.md) にあります。

## プラットフォームとネットワーク { #platform }

### V2.2.0 は IPRO6S に対応していますか？ { #ipro6s }

はい、Wi-Fi について対応しています。V2.2.0 には IPRO6S 用のアプリケーションが 3 つあります：`ipro6_demo`（Wi-Fi 6 ステーション / ソフト AP）、`ipro6_if_wifi`（SDIO または USB 経由でホストに接続する Wi-Fi ブリッジ）、`ipro6_fmac`（Linux ホスト用の FullMAC ファームウェア）。本リリースには IPRO6S 用の BLE コントローラーライブラリはなく、IPRO6S 用の BLE や BR/EDR のアプリケーションもありません。

Reef では、IPRO6S は microSD スロットに挿す FIN Wi-Fi カードで、そのファームウェアは `ipro6_if_wifi` の SDIO 用設定です。

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

出力は `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin` です。IPRO6S のイメージは IntelProCube の `--chipname ipro6` で書き込みます。`build_freertos.sh flash` は使えません。対応する設定と書き込み方法は [IPRO6S](../hardware/chips/ipro6s.md) にあります。

### IPRO7 はどのようにネットワークに接続しますか？ { #wifi }

IPRO7 は外部の無線チップを介して Wi-Fi に接続します。Reef では SDIO 経由の IPRO6S FIN カードです。

- **IPRO6S（SDIO）**：IPRO7 側のコンポーネント `components/network/ipronet_host` と、lwIP ネットワークインターフェース `iproeth0`。Reef では FIN カードがこれにあたり、`ipro7ai_reef_demo` の `defconfig_wifi_ipro6s`（RTSP カメラストリーム付き）と `ipro_agora_sentino` で使います。手順は [Wi-Fi と RTSP カメラストリーミング](../tutorials/wifi-rtsp.md) にあります。
- **その他**：ATBM6162（SDIO）、AIC8800（SDIO）、ESP32（UART AT コマンド）用のコンポーネントもパッケージに含まれています。
- **有線**：EMAC（RMII）ドライバー（`CONFIG_ETHERNET`）。

[ネットワーク](../guides/networking.md) を参照してください。

### SDK が対応している RTOS は？ BLE ホストは Zephyr ですか？ { #rtos }

40 個のアプリケーションはすべて FreeRTOS（カーネル V11.1.0）です：IPRO7 用 37 個、IPRO6S 用 3 個。BLE ホストは Zephyr v4.4.0 のもので、SDK の移植レイヤーを介して FreeRTOS 上で動作します。アプリケーションは Zephyr をインストールせずに Zephyr の `bt_*` API を使います。

SDK は `ipro7_evb` と `ipro7ai_evk` のボードを持つ Zephyr v4.4.0 モジュールでもあり、Reef のボード定義はありません。SoC の Kconfig ヘルプには、`ipro7_evb` のイメージを Reef で実行する場合は `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` が必要と記載されています。[Zephyr RTOS](../guides/zephyr.md) を参照してください。

### Thread や Matter は使えますか？ { #thread-matter }

Thread は Zephyr でのみ使えます。Zephyr の IEEE 802.15.4 ドライバーと OpenThread を組み合わせ、Zephyr の `samples/net/openthread/shell` を SDK の `zephyr/samples/ieee802154_shell/ot.conf` と `app.overlay` でビルドします。FreeRTOS アプリケーションには Thread はなく、本リリースには Matter もありません。[Thread と Matter](../guides/thread-matter.md) を参照してください。

### 水晶発振子の周波数オフセット（CFO）を調整するには？ { #xtal-capcode }

`.config` で `CONFIG_IPRO7_XTAL_CAPCODE=<1–255>` を設定します。起動時に `board_init()` がこの値を適用して `[XTAL] capcode <boot value> -> <set value>` を表示し、RF の初期化のたびに再読み込みされます。0 の場合、最初の RF 初期化で ROM のデフォルト値 85 が読み込まれるまで、起動時の値が維持されます。Reef では未設定の場合に 95 が使われ、CMake は構成時に `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` を表示します。

値を大きくすると周波数が下がります。周波数が高い（正のオフセット）場合は値を上げ、低い場合は下げます。これはボードごとの値であり、量産時には個体ごとの校正が必要です。コードから `AON_Set_Xtal_CapCode()` と `AON_Get_Xtal_CapCode()`（`bsp/drivers/ipro7_soc/std_drv/inc/drv_aon.h`）を呼び出すこともできます。

## デバッグ { #debug }

### デバッグログを有効にするには？ { #debug-log }

`.config` で整数のレベルを設定し、再ビルドします。

```ini title=".config"
CONFIG_IPRO_LOG_ENABLE=y
CONFIG_LOG_DEFAULT_LEVEL=4    # 1 エラー、2 警告、3 情報、4 デバッグ、5 詳細
```

コードは整数の `CONFIG_LOG_DEFAULT_LEVEL` を読みます。`CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y` のようなオプションを設定しても効果はなく、`CONFIG_BT_DEBUG` でもホストのログは有効になりません。実行時にレベルを変更するには `ipro_log_set_level()` を使います。[API リファレンス](api/index.md#log-api) を参照してください。

### クラッシュやスタックオーバーフローを解析するには？ { #crash }

CPU 例外が発生すると、ファームウェアは `MCAUSE`、`MEPC`、例外を起こしたタスク、バックトレースを表示します。同じビルドの `.elf` に対してツールチェーンの `addr2line` を実行すると、関数とソース行がわかります。スタックオーバーフローでは `[!] Stack overflow: <task>` が表示されます。`xTaskCreate()` のスタックサイズ（ワード単位）を増やしてください。クラッシュ後、`ipro7ai_reef_demo` と `ipro_reef_teach` は同梱されていないホストツールを待って `==DUMP_READY:2000000==` を表示し続けます。診断情報を保存し、SW2 を押してリセットしてください。本リリースには、オンターゲットデバッガー（JTAG / GDB）の設定はありません。[クラッシュの解析](debugging.md#crash-analysis) を参照してください。
