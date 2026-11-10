---
title: "IPRO6S"
description: IPRO6S の仕様、V2.2.1 に含まれる 3 個の Wi-Fi 6 アプリケーションとその構成、ビルドと書き込み、IPRO7AI Reef EVK の FIN Wi-Fi カードとしての役割
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S

IPRO6S は Wi-Fi 6 を内蔵した RISC-V SoC です。IPRO7 と同じ SDK ツリー、同じツールチェーンでビルドします。V2.2.1 には IPRO6S の Wi-Fi アプリケーションが 3 個含まれます。単体でネットワークに接続する `ipro6_demo`、SDIO または USB でホストプロセッサーに Wi-Fi をブリッジする `ipro6_if_wifi`、Linux ホスト用の FullMAC ファームウェアである `ipro6_fmac` です。IPRO7AI Reef EVK では、IPRO6S は microSD スロットに挿す FIN Wi-Fi カードで、SDIO を通じて IPRO7AI にネットワーク接続を提供します。

<div class="ipro-facts" markdown>
<div><strong>Wi-Fi 6</strong><span>チップに内蔵</span></div>
<div><strong>RV32IMAFC</strong><span>IPRO7 と同じツールチェーン</span></div>
<div><strong>3</strong><span>IPRO6S アプリケーション</span></div>
<div><strong>ipro6</strong><span>書き込み時の <code>--chipname</code></span></div>
</div>

## チップの仕様 { #ipro6s }

| 項目 | IPRO6S |
|---|---|
| コア | DSP 拡張付き RISC-V RV32IMAFC |
| ワイヤレス | Wi-Fi 6 内蔵 |
| NPU / ISP | なし |
| RTOS | FreeRTOS V11 |
| リファレンスボード | IPRO6S EVK（INTELPRO にお問い合わせください）、Reef の FIN カード |

| 領域 | サイズ | ベースアドレス | 備考 |
|---|---|---|---|
| Flash | 2 MB | `0x13000000` | |
| TCM RAM | 320 KB | `0x11000000` | コードとデータ。縮小レイアウトでは 280 KB |
| Wi-Fi RAM | 160 KB | `0x21050000` | |
| HBN RAM | 4 KB | `0x20090000` | |

IPRO6S アプリケーションは次の設定でチップを選択します。イメージにはチップ接尾辞 `IPRO6` が付きます。

```ini title="apps/platform/ipro6_if_wifi/defconfig_ipro6_sdio（抜粋）"
CONFIG_IPRO6=y
CONFIG_CHIP="IPRO6"
CONFIG_CPU_ID="intelpro_ipro7"     # IPRO7 と同じツールチェーン
CONFIG_FREERTOS_SUPPORT=y
```

## 本リリースでの SDK サポート { #status }

| 項目 | V2.2.1 |
|---|---|
| アプリケーション | `ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`（`apps/platform/`） |
| Wi-Fi 6 | MAC（`components/wireless/macsw`）、fhost API、wpa_supplicant と lwIP アダプター（`components/wireless/wifi6`）、RF ドライバー（`components/wireless/rf/ipro6_rf`）。いずれもアプリケーション構成ごとにビルド済みです |
| 低消費電力 | DTIM 低消費電力ファームウェアイメージ `bsp/hal/lp_framework/ipro6/prebuilt/ipro6_lpfw.bin`。低消費電力構成に組み込まれます |
| Bluetooth | IPRO6S の Bluetooth コントローラーライブラリとデュアルモード（BR/EDR）アプリケーションは V2.2.1 には含まれていません。INTELPRO にお問い合わせください。本リリースの IPRO6S アプリケーションは Wi-Fi のみを使います |
| Zephyr RTOS | `ipro6s_evb` のボードファイルは含まれていますが、本リリースでは Zephyr 上の IPRO6S はサポートされていません |
| 書き込み | [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 以降のコマンドラインツールで `--chipname ipro6` を指定します。`build_freertos.sh` の `flash` アクションは IPRO7 にのみ対応しています |

## アプリケーションと構成 { #apps }

各 IPRO6S アプリケーションは `DEFCONFIG=` で構成を選択します。表にはビルド検証済みの構成を示します。アプリケーションの `.config` は、最初の構成のコピーです。

| アプリケーション | 構成 | 内容 |
|---|---|---|
| `ipro6_demo` | `defconfig_ipro6_lpwifi` | Wi-Fi 6 ステーションとソフト AP、lwIP、シェル、DTIM 省電力 |
| | `defconfig_ipro6_lp` | Wi-Fi を使わない低消費電力デモ |
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 6 ブリッジ。ホストプロセッサーからは SDIO 経由の Ethernet 風インターフェースとして見えます。Reef の FIN カードのファームウェアです |
| | `defconfig_ipro6_usb` | 同じ機能を USB 経由で提供 |
| | `defconfig_ipro6_lp` | Wi-Fi を使わない低消費電力デモ |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | Linux cfg80211 ホスト用の FullMAC ファームウェア（イメージ `ipro6s_fmac.img`）。`make` のデフォルト |
| | `defconfig_ipro6_fmac_loader` | SDIO または USB で FullMAC ファームウェアを受け取る Flash ローダー |

- `ipro6_demo/defconfig_ipro6_lpwifi_ping` と `ipro6_fmac/defconfig_ipro6_fmac_ap` は `CONFIG_WIRELESS_LIB_VARIANT` を設定しておらず、検証済みの構成には含まれません。使用する前に INTELPRO にお問い合わせください。
- `ipro6_fmac` 用の Linux ホストドライバーは V2.2.1 には含まれていません。
- 3 つのアプリケーションは IPRO6S EVK（`CONFIG_BOARD="EVB"`）を対象としています。Reef では、`ipro6_if_wifi` の `defconfig_ipro6_sdio` だけが FIN カード上で動作します。

## ビルド { #build }

SDK のルートで実行します。FIN カードのファームウェアを例にします。

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

ビルドの最後にリンカーが Flash と RAM の使用量を表示し、イメージは `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin` に出力されます。出力ディレクトリの名前は、`build_` の後ろに構成名から `defconfig_` を除いたものを付けたものです。`ipro6_fmac` の Makefile はデフォルトで `DEFCONFIG=defconfig_ipro6_fmac` を渡すため、そこで単に `make` を実行しても `build_ipro6_fmac/` にビルドされます。`build_freertos.sh -d defconfig_ipro6_sdio build ipro6_if_wifi` でもビルドできますが、IPRO6S への書き込みはできません。

### Wi-Fi ライブラリとカスタム構成 { #wifi-libs }

Wi-Fi の MAC、fhost、wpa_supplicant、lwIP アダプター、RF ドライバーは、アプリケーション構成ごとに 1 つずつビルド済みで各コンポーネントの `lib/<app>-<config>/` に置かれており、構成の `CONFIG_WIRELESS_LIB_VARIANT` で選択されます。`defconfig_ipro6_sdio` の場合は次のとおりです。

```ini
CONFIG_WIFI6=y
CONFIG_USE_MACSW=y
CONFIG_WIRELESS_LIB_VARIANT="ipro6_if_wifi-ipro6_sdio"
```

カスタム構成を作る場合は、上記のいずれかの構成の Wi-Fi オプションとその `CONFIG_WIRELESS_LIB_VARIANT` をそのまま使ってください。ビルド済みライブラリはそれらの構成に対してのみ用意されています。

`ipro6_demo` では、`CONFIG_WIFI_MEM_PROFILE_PERF`（デフォルト）、`_BALANCED`、`_APP` のいずれかで、Wi-Fi バッファーとアプリケーションのヒープへの RAM の配分を選択します。切り替えるには構成に 1 行追加し、ビルドディレクトリを削除してから再度ビルドします。各プロファイルの空きヒープとスループットは `apps/platform/ipro6_demo/profile_selection_readme.md` に記載されています。

## 書き込みとボードでの動作確認 { #flashing }

ここでは IPRO6S EVK と IPRO Debug Probe を使い、`ipro6_demo` をビルドして書き込み、コンソールで Wi-Fi スキャンの結果を確認するまでを説明します。IPRO6S のイメージは IntelProCube のコマンドラインツールで `--chipname ipro6` を指定して書き込みます。`build_freertos.sh` の `flash` アクションは使用できません。

必要なもの：

- IPRO6S EVK、2.4 GHz アンテナ、IPRO Debug Probe とその UART ケーブル、USB-C 電源。
- [開発環境の準備](../../get-started/environment.md)に従ってインストールしたツールチェーンと SDK V2.2.1（以下 `<SDK>`）。
- [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 以降。[README](https://github.com/INTELPRO-INC/ipro-cube#readme) に従ってダウンロードし、SHA-256 を確認して新しいフォルダーに展開します（以下 `<IntelProCube>`）。0.7.0 で書き込んだイメージは起動しません。[書き込みは成功するが起動しない](#ipro6s-no-boot)を参照してください。

<div class="ipro-steps" markdown>

1. **ビルド**：`<SDK>` のルートで次を実行します。

    ```bash
    make -C apps/platform/ipro6_demo DEFCONFIG=defconfig_ipro6_lpwifi
    ```

    終了時にリンカーが各メモリー領域の使用量を表示します。`flash` の行はおよそ次のとおりです。

    ```text
               flash:     1092656 B         2 MB     52.10%
    ```

    イメージは `apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin` に出力されます。

2. **接続**：EVK の RF1（u.FL）にアンテナを接続します。IPRO Debug Probe の UART ケーブルを EVK の J_UART に接続し、プローブを USB でコンピューターに接続します。EVK に USB-C で給電すると LED1 が点灯します。

3. **シリアルポートを確認**：`<IntelProCube>` で次を実行します（Linux では `./ipro_iot_tool_linux`、Windows では `ipro_iot_tool.exe`。以下同様）。

    ```bash
    ./ipro_iot_tool_macos --list-ports
    ```

    プローブのポートは 2 つ表示されます。`(IPRO_U)` が付いた、名前が `02` で終わるポートが UART で、書き込みとコンソールの両方に使います。`(IPRO_C)` はチップのデバッグポートです。macOS では `/dev/tty.` で始まる名前が表示されるので、`/dev/cu.` で始まる同じ名前のポート（例：`/dev/cu.usbmodemXXXX02`）を使ってください。

4. **書き込み**：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro6 --chip-variant IPRO6S \
        --port /dev/cu.usbmodemXXXX02 --baudrate 2000000 \
        --pt chips/ipro6/partition/partition_cfg_fw_direct.toml \
        --firmware <SDK>/apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin
    ```

    ツールはプローブ経由でチップをダウンロードモードにし、イメージを書き込んでベリファイした後、チップをリセットします。所要時間は約 15 秒です。出力の最後に `[All Success]` が表示された場合だけが成功です。ツールは失敗しても終了コード 0 で終了します。`partition_cfg_fw_direct.toml` はファームウェアを boot2 なしで Flash アドレス 0x0 に置き、パーティションテーブルを最後の 2 セクターに置きます。

5. **起動を確認**：同じポートを 115200 baud（8N1、フロー制御なし）で開き、EVK の RESET（SW2）を押します。

    ```bash
    screen /dev/cu.usbmodemXXXX02 115200
    ```

    起動メッセージの最後は次のとおりです。

    ```text
    [OS] Starting OS Scheduler...
    [EVENT] Event loop initialized
    [EVENT] WiFi event handler registered
    Init Shell (RT-Thread FinSH based)
    ipro />
    ```

6. **Wi-Fi を確認**：`stack_wifi` を入力し、`CODE_WIFI_ON_MGMR_DONE` が表示されたら `wifi_scan` を入力します。

    ```text
    ipro />stack_wifi
    ...
    [APP] [EVT] CODE_WIFI_ON_INIT_DONE
    ...
    [APP] [EVT] CODE_WIFI_ON_MGMR_DONE
    ipro />wifi_scan
    [APP] [EVT] CODE_WIFI_ON_SCAN_DONE
    ...
    index[00]: channel 01, bssid XX:XX:XX:XX:XX:XX, rssi -20, ... auth WPA2-PSK, cipher: AES, SSID <ssid>
    ```

    周辺のアクセスポイントが 1 行ずつ表示されます（最大 50 行。未使用の行は `empty`）。アクセスポイントが表示されれば、RF と Wi-Fi スタックは正常に動作しています。`stack_wifi` は起動ごとに 1 回だけ実行します。

7. **soft-AP を確認**：アクセスポイントを起動します。キーは 8〜63 文字です。

    ```text
    ipro />wifi_ap_start -s IPRO6S_AP -k <key> -c 6
    [WPA] AP-ENABLED
    [APP] [EVT] CODE_WIFI_ON_AP_STARTED
    ```

    コンピューターやスマートフォンからそのキーで `IPRO6S_AP` に接続すると、ボード（192.168.169.1）から 192.168.169.0/24 のアドレスが割り当てられ、コンソールに `AP-STA-CONNECTED` とその機器の MAC アドレスが表示されます。`wifi_ap_stop` でアクセスポイントを停止します。

</div>

### 手動でダウンロードモードにする { #ipro6s-download-mode }

ツールはプローブの DL 線でダウンロードモードに入ります。一般的な USB-UART ケーブルを使う場合や、ツールがハンドシェイクの失敗を報告した場合は、手動でダウンロードモードにしてから書き込みコマンドを実行します。BOOT（SW1）を押したまま RESET（SW2）を押し、BOOT を離します。ダウンロードモードではコンソールに何も出力されません。書き込み後に RESET を押すと通常どおり起動します。書き込みの前に、シリアルポートを開いているターミナルプログラム（`screen` など）を閉じてください。閉じないと、ツールがポートを開けません。

### 書き込みは成功するが起動しない { #ipro6s-no-boot }

IntelProCube 0.7.0 の IPRO6 ブートヘッダーのタイミング設定は、2 MB の Flash を内蔵した IPRO6S に適合しません。出力は `[All Success]` で終わりますが、リセット後もコンソールには何も表示されず、チップはダウンロードモードのままです。0.7.0.1 以降を新しいフォルダーに展開して使用してください。使用済みの 0.7.0 のフォルダーに 0.7.0.1 を上書き展開した場合は、先に `chips/ipro6/img_create_iot/efuse_bootheader_cfg.ini` を削除してください。このファイルは初回実行時にテンプレートから作成され、その後は更新されません。IPRO SDK Online Setup 3.6.0 以前がインストールする IntelProCube は 0.7.0 です。IPRO6S に書き込む場合は 0.7.0.1 を別途インストールしてください。

## Reef の FIN Wi-Fi カード { #dual-chip }

FIN カードは、SD カード形状のエッジに IPRO6S を載せたカードです。Reef の microSD スロットに挿して SDIO スレーブとして動作し、スロットの SD_VDD から給電されます。IPRO7AI はメイン SoC で、アプリケーション、AI、BLE、オーディオ、IP スタックを実行します。カード上の IPRO6S は `ipro6_if_wifi`（`defconfig_ipro6_sdio`）を実行し、無線リンクを提供します。

```mermaid
flowchart LR
    A["IPRO7AI（Reef）<br/>アプリケーション + ipronet_host + lwIP"] -- "SDIO 4-bit（microSD スロット）" --> B["IPRO6S FIN カード<br/>ipro6_if_wifi"]
    B -- "Wi-Fi 6" --> C["アクセスポイント"]
```

IPRO7AI 側では、ホストコンポーネント `components/network/ipronet_host` が SD ホスト（GPIO28–33）を通じてカードを制御し、リンクを lwIP ネットワークインターフェース `iproeth0` として提供します。これを使う Reef アプリケーションは次のとおりです。

| アプリケーション | 構成 | 内容 |
|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `defconfig_wifi_ipro6s` | Wi-Fi 接続と RTSP カメラストリーム（`rtsp://<ip>:8554/av0_0`） |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `.config` | Sentino クラウド音声チャット。FIN カード経由でオンラインに接続します |

JP3 を GPIO にすると、GPIO14 でスロットの電源を切り替えられ、`fin cycle` でカードの電源を再投入できます。接続とストリーミングの手順は [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp) と [Wi-Fi と RTSP ストリーミング](../../tutorials/wifi-rtsp.md)を参照してください。

### FIN カードのファームウェアを更新する { #fin-update }

`ipro7ai_reef_demo` の `defconfig_wifi_ipro6s` ビルドには 2 つの方法があります。

<div class="ipro-steps" markdown>

1. **Wi-Fi 経由で更新**：FIN ファームウェア（`defconfig_ipro6_sdio` は `CONFIG_RNM_OTA=y` を設定）は、IntelProCube で作成した IPRO6 OTA パッケージ `FW_OTA.bin.xz.ota` を受け付けます。Reef からアクセスできる HTTP サーバーにパッケージを置きます。たとえば、パッケージのあるディレクトリで次を実行します。

    ```bash
    python3 -m http.server 8000
    ```

2. **Reef のコンソールから接続して更新**：

    ```text
    ipronet_up <ssid> <psk>
    ipro6s_ota http://<host-ip>:8000/FW_OTA.bin.xz.ota
    ```

    カードはパッケージをファームウェアパーティションに書き込み、SHA-256 で検証してから再起動し、boot2 がインストールします。所要時間は約 30–60 秒です。成功するとコンソールに `[ota] RESULT OK` と表示され、失敗すると `[ota] RESULT ERR rc=…` と失敗したフェーズが表示されます。`http://` にのみ対応しています。

</div>

もう 1 つの方法は、Reef のコンソールで `ipro6_dl` を実行することです。カードの電源を切り、SD_D0（GPIO29）のダウンロードストラップを High にしてから電源を再投入するため、IPRO6S は BROM ダウンロードモードで起動します。その後の書き込みは IPRO6S の UART を通じて `--chipname ipro6` で行います。FIN カード上のこの UART への接続方法は本リリースのドキュメントでは扱っていないため、INTELPRO にお問い合わせください。`ipro6_rst` はカードの電源を再投入して通常起動に戻し、`ipro6_pwr 0|1` はカードの電源を手動で切り替えます。

## 関連ドキュメント { #documents }

- [IPRO7](ipro7.md#networking)：IPRO7 のネットワーク接続方法。
- [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp)：FIN カード、JP3、Wi-Fi コマンド。
- [ネットワークガイド](../../guides/networking.md)：lwIP、Ethernet、SDIO Wi-Fi ホスト。
- `components/network/ipronet_host/README.md`：ホスト API と OTA の流れ。
