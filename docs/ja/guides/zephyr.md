---
title: "Zephyr RTOS"
description: Zephyr v4.4.0 モジュールとしての IPRO SDK — ボード、ワークスペース、west によるビルドと書き込み、サンプル、ビルド済みコンポーネント、本リリースの Zephyr で対応していない範囲
migrate_from:
  - "zephyr-rtos.html#overview"
  - "zephyr-rtos.html#boards"
  - "zephyr-rtos.html#features"
  - "zephyr-rtos.html#samples"
  - "zephyr-rtos.html#prebuilt"
  - "zephyr-rtos.html#limitations"
  - "getting-started.html#zephyr-quickstart"
  - "zephyr-rtos.html#setup"
  - "zephyr-rtos.html#build-flash"
---

# Zephyr RTOS

IPRO SDK は Zephyr v4.4.0 のモジュールでもあります。SDK の HAL と SoC ドライバーが Zephyr のデバイスドライバー API の背後にあるため、FreeRTOS の代わりに Zephyr でアプリケーションを作成できます。このページは Zephyr 側のリファレンスで、ボード、ワークスペース、`west` によるビルドと書き込み、サンプル、制限事項を扱います。FreeRTOS アプリケーションとそのビルドは変わりません。

!!! abstract "要点"
    - ボード：`ipro7_evb`（IPRO7 EVB）と `ipro7ai_evk`（IPRO7AI EVK）。**V2.2.0 には IPRO7AI Reef EVK 用の Zephyr ボード定義がありません**。Reef では FreeRTOS アプリケーションを使用してください。
    - 利用できるもの：一般的な周辺機能のドライバー、BLE（ビルド済みの IPRO BLE コントローラー上の Zephyr ホスト）、OpenThread を使う IEEE 802.15.4、MCUboot と BLE 経由の MCUmgr による更新。
    - 利用できないもの：低消費電力モード、カメラ、オーディオコーデック、USB、SD ホスト、イーサネット、NPU の Zephyr ドライバー。
    - コンソール：UART0、2,000,000 baud。ホストに必要なもの：venv を使える Python 3、git、GitHub へのネットワークアクセス、CMake 3.20 以降。
    - 最初のビルド：[ワークスペース](#workspace)、次に[ビルド、書き込み、コンソール](#flash-console)。

## 概要 { #overview }

| ファイル／ディレクトリ | 役割 |
|---|---|
| `west.yml` | SDK は west のマニフェストリポジトリです。Zephyr v4.4.0 を固定し、許可リストにあるモジュールだけをインポートします |
| `zephyr/module.yml` | SDK を Zephyr モジュールとして、ボード、SoC、devicetree バインディング、`west flash` のランナーとともに登録します |
| `zephyr/boards/`、`soc/`、`dts/` | ボード定義、SoC 定義、devicetree バインディング |
| `zephyr/drivers/`、`hal_glue/`、`include/` | Zephyr ドライバーと、SDK の HAL とのグルーコード |
| `zephyr/patches.yml`、`patches/` | SDK による Zephyr への 2 つのパッチ。ワークスペースの作成時に適用されます |
| `zephyr/samples/`、`zephyr/tests/` | SDK のサンプルとテストスイート |
| `tools/zephyr/` | ワークスペースの作成、ビルド、書き込み、コンソールを開くためのスクリプト |

Zephyr ドライバーは SDK の HAL を呼び出し、HAL は `bsp/` から直接コンパイルされます。BLE は Zephyr のホストと IPRO BLE コントローラーのアーカイブを使います。IEEE 802.15.4 は Zephyr のドライバーインターフェースと OpenThread を使います。

## 対応ボード { #boards }

| Zephyr ボード | ハードウェア | Flash（devicetree） | PSRAM | `west flash` のデフォルト |
|---|---|---|---|---|
| `ipro7_evb` | IPRO7 EVB | 2 MB | なし | `--pt=partition_cfg_2M.toml`、IPRO7 CMSIS-DAP プローブ経由でダウンロードモード |
| `ipro7ai_evk` | IPRO7AI EVK | 1 MB | 8 MB | `--pt=partition_cfg_1M_boot2.toml`、`--boot=shell` |

- どちらのボードも、コンソールは UART0、2,000,000 baud です。
- パーティションテーブルの名前は、IntelProCube の `chips/ipro7/partition/` 以下のファイルを指します。
- `ipro6s_evb` のボードファイルは SDK に同梱されていますが、本リリースでは IPRO6S は Zephyr でサポートされていません。

!!! info "IPRO7AI Reef EVK"
    V2.2.0 には Reef 用の Zephyr ボードも、Reef のカメラ、オーディオ、LED、microSD ソケットの devicetree もありません。本リリースでは、Reef での Zephyr イメージの動作は検証されていません。Reef で Zephyr が必要な場合は、INTELPRO にお問い合わせください。

## ワークスペース { #workspace }

`tools/zephyr/bootstrap.sh` は SDK ルートに `zephyr-workspace/` を作成します。初回の実行時に、Zephyr とそのモジュールを GitHub からダウンロードします。

```bash
tools/zephyr/bootstrap.sh              # zephyr-workspace/ を作成
source zephyr-workspace/env.sh         # ZEPHYR_BASE、CROSS_COMPILE を設定し、west を PATH に追加
```

スクリプトは次の処理を行います。

1. `zephyr-workspace/.venv` を作成し、west をインストールします。
2. SDK の `west.yml` から west を初期化し、`west update` を実行します（デフォルトは shallow）。
3. `zephyr/patches.yml` のパッチを適用します。
4. Zephyr と MCUboot の Python 依存パッケージをインストールします。
5. `env.sh` を書き出します：`ZEPHYR_TOOLCHAIN_VARIANT=cross-compile`、`CROSS_COMPILE`、`ZEPHYR_BASE`、`PATH`。

| オプション／変数 | 意味 |
|---|---|
| `-w DIR` | 別のワークスペースディレクトリを使用 |
| `--full` | Zephyr とモジュールを全履歴付きで取得 |
| `IPRO_TOOLCHAIN` | ツールチェーンのディレクトリ。デフォルトは `/opt/toolchain/riscv_ipro7` |

`west.yml` がインポートするのは `mbedtls`、`tf-psa-crypto`、`openthread`、`picolibc`、`segger`、`mcuboot`、`liblc3`、`zcbor` だけです。

!!! warning "bootstrap の再実行"
    bootstrap は更新の前に、パッチが変更する Zephyr のファイルを固定リビジョンの状態に戻します。それらのファイルへのローカルな編集は破棄されます。

Zephyr には CMake 3.20 以降が必要です。`tools/cmake/` の CMake は Linux x86-64 用の 3.15 で、FreeRTOS のビルド専用です。

## ビルド、書き込み、コンソール { #flash-console }

`source env.sh` の後、`zephyr-workspace/` で次を実行します。

```bash
west build -b ipro7_evb zephyr/samples/hello_world                       # Zephyr のサンプル
west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke     # SDK のサンプル
west flash -d build/smoke
../tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX                  # コンソール、2,000,000 baud
```

SDK ルートからは、`tools/zephyr/build.sh [-b ipro7_evb|ipro7ai_evk] [-d DIR] [-p] APP [-- cmake args]` が `west build` をラップしており、SDK のサンプルを名前で指定できます（`tools/zephyr/build.sh -b ipro7ai_evk periph_smoke`）。

`west flash` は SDK の `ipro` ランナー（`zephyr/scripts/runners/ipro.py`）を使います。ランナーはボードをダウンロードモードにし、IntelProCube のコマンドラインツールで `zephyr.bin` を書き込み、ボードをリセットします。

| ランナーのオプション | 意味 |
|---|---|
| `--boot probe` / `shell` / `manual` | ボードをダウンロードモードにする方法：IPRO7 CMSIS-DAP プローブ（デフォルト）、動作中のイメージの `reboot_dl`、または手動 |
| `--port`、`--probe-port` | 書き込み用 UART とプローブのブリッジのポート。デフォルトは `$IPRO_SERIAL_PORT`、`$IPRO_PROBE_PORT` |
| `--tool` | IntelProCube の CLI バイナリ。デフォルトは `$IPRO_FLASH_TOOL`、または `PATH` 上のツール |
| `--pt` | パーティションテーブル：`.toml` のパス、またはツールの `chips/<chip>/partition/` 以下のテーブル名 |
| `--baudrate`、`--console-baud` | 書き込みのボーレートと、`--boot shell` で使うコンソールのボーレート。どちらもデフォルトは 2000000 |
| `--no-reset`、`--attempts`、`--tool-arg` | ダウンロードモードのままにする。再試行回数（3）。ツールへの追加引数 |

ランナーのオプションは `--` の後に渡します。例：`west flash -- --boot shell --port /dev/cu.usbserial-XXXX`。

- `west flash` は `--chip-variant` を渡しません。IntelProCube は、その `chips/ipro7/eflash_loader/eflash_loader_cfg.ini` に保存されている flash pin の設定を使います。
- MCUboot を含む sysbuild のイメージでは、`west flash` がまず `tools/zephyr/merge_mcuboot.py` で MCUboot と署名済みアプリケーションを 1 つのイメージに結合します。
- `tools/zephyr/flash.sh` は `reboot_dl` を 115200 baud で送信しますが、動作中の Zephyr イメージ（2,000,000 baud）はこれを受信しません。先に手動でダウンロードモードに入れるか、`west flash` を使用してください。

## 機能 { #features }

| 分野 | Zephyr での対応 |
|---|---|
| ドライバー | GPIO、UART（非同期を含む）、SPI、I2C、PWM、ADC、DAC、counter/RTC、ウォッチドッグ、Flash、DMA、entropy、hwinfo、I2S/PDM |
| ディスプレイ | Zephyr 自身の ST7789V ドライバーによる IPRO7AI EVK の LCD |
| Bluetooth LE | `components/wireless/bluetooth/ipro_ble_controller/lib/` の IPRO BLE コントローラーのアーカイブ上で動く Zephyr ホスト |
| IEEE 802.15.4 / Thread | Zephyr の IEEE 802.15.4 ドライバーと OpenThread。[Thread と Matter](thread-matter.md) を参照 |
| ブートと更新 | sysbuild による MCUboot。MCUmgr SMP による BLE 経由のイメージのアップロード。[OTA アップデート](ota.md)を参照 |

Zephyr では、BLE コントローラーのアーカイブを次のキーで選択し、devicetree オーバーレイで `bt_hci` ノードを有効にします（`zephyr/samples/bt_peripheral_hr/ipro7.overlay`）。

```ini title="zephyr/samples/bt_peripheral_hr/ipro7.conf（抜粋）"
CONFIG_IPRO7_EM_SIZE_KB=16
CONFIG_BT_IPRO_CTLR_LIB="link1_periph"
CONFIG_BT_IPRO_CTLR_FEATURE="bt52"
CONFIG_BT_MAX_CONN=1
CONFIG_ENTROPY_GENERATOR=y
```

ISO と LE Audio には `zephyr/samples/bt_le_audio/iso.conf`（`link1`、`bt54_iso2`、`CONFIG_IPRO7_EM_SIZE_KB=32`）を使います。アーカイブの組み合わせについては [BLE 開発](ble.md)で説明しています。

## サンプル { #samples }

| サンプル（`zephyr/samples/`） | ボード | 内容 |
|---|---|---|
| `periph_smoke` | `ipro7_evb` | 各ドライバーを動かします：GPIO、UART、SPI、I2C、PWM、Flash、DMA、counter、ウォッチドッグ、TRNG |
| `mcuboot_app` | `ipro7_evb`、`ipro7ai_evk` | boot2 → MCUboot → イメージのブートチェーンを確認します |
| `ble_ota` | `ipro7_evb`、`ipro7ai_evk` | MCUboot + MCUmgr SMP。BLE で更新します |
| `bap_broadcast_source` | `ipro7_evb`、`ipro7ai_evk` | LE Audio のブロードキャストソース（LC3） |
| `bap_broadcast_sink` | `ipro7ai_evk` | LE Audio のブロードキャストシンク。EVK のスピーカーで再生します |
| `le_audio_headset` | `ipro7ai_evk` | LE Audio のユニキャストヘッドセット（CAP acceptor） |
| `evk_demo` | `ipro7ai_evk` | EVK の LCD、マイク、スピーカー、カメラプレビュー用の `evk` シェルコマンド |
| `ieee802154_shell` | `ipro7_evb` | IEEE 802.15.4 シェル。OpenThread 用の `ot.conf` と `csl.conf` も含みます |
| `bt_peripheral_hr`、`bt_le_audio` | – | Zephyr 自身のサンプル用の設定フラグメント |

SDK のフラグメントを使った Zephyr 自身のサンプル（`zephyr-workspace/` で実行）：

```bash
west build -b ipro7_evb zephyr/samples/bluetooth/peripheral_hr -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.overlay
west build -b ipro7_evb zephyr/samples/net/openthread/shell -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/ieee802154_shell/ot.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/ieee802154_shell/app.overlay
```

`zephyr/tests/` には、15 のドライバーテストスイート（`zephyr/tests/drivers/`）と 3 つの SoC テストスイート（`camclk`、`psram`、`reboot`）があり、標準の ztest スイートとして書かれています。

## ビルド済みコンポーネント { #prebuilt }

Zephyr のビルドは、HAL を含む SDK のすべてのコードをソースからコンパイルします。例外は次のとおりです。

| コンポーネント | 場所 |
|---|---|
| IPRO BLE コントローラー | `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| RF ドライバー | `components/wireless/rf/ipro7_rf/lib/zephyr/`（`libipro_rf_core.a`、`libipro_rf_core_short_enums.a`） |
| IEEE 802.15.4 MAC | `components/wireless/ieee802154/lib/zephyr/`（`libipro_ieee802154_core.a`、`libipro_ieee802154_core_short_enums.a`） |

BLE コントローラーをリンクする場合、イメージ全体が `-fshort-enums` でコンパイルされ、ビルドは対応する RF と 802.15.4 のバリアントを選びます。

## 本リリースの制限事項 { #limitations }

- IPRO7AI Reef EVK 用の Zephyr ボードはありません。IPRO6S は Zephyr でサポートされていません。
- 低消費電力モード：Zephyr の `pm_state` は PDS にも HBN にも入らず、BLE コントローラーはスリープしません。低消費電力が必要な場合は FreeRTOS を使用してください。[低消費電力](low-power.md)を参照してください。
- カメラ、オーディオコーデック、USB、SD ホスト、イーサネット、NPU の Zephyr ドライバーはありません。ディスプレイは IPRO7AI EVK の LCD のみです。
- Zephyr では IPRO7 で Wi-Fi を使用できません。`zephyr/drivers/wifi` は IPRO6S のオンチップドライバーです。
- これらの機能が必要な製品では、FreeRTOS アプリケーションを使用します。

## 関連ドキュメント { #related }

- [Thread と Matter](thread-matter.md)：OpenThread の設定と最初のテスト。
- [OTA アップデート](ota.md)：MCUboot と MCUmgr。
- [BLE 開発](ble.md)：コントローラーのアーカイブと BLE API。
- [ツールのコマンドライン](../reference/tools.md)：`tools/zephyr/` のスクリプト。
