---
title: "IPRO7"
description: IPRO7 チップの公開仕様、メモリマップ、本リリースでの SDK サポート、搭載ボード
migrate_from:
  - "hardware.html — IPRO7 晶片概覽、無線規格詳細、AI 與多媒體、介面規格"
---

# IPRO7

IPRO7 は INTELPRO の 2.4 GHz 低消費電力ワイヤレス SoC です。192 MHz の RISC-V RV32IMAFC コア、LE Audio 対応の Bluetooth 5.4、IEEE 802.15.4 無線、ISP、ハードウェア MJPEG を搭載しています。本 SDK リリースの 40 個のアプリケーションのうち 37 個が IPRO7 を対象としています。NPU を有効にしたバリアントである [IPRO7AI](ipro7ai.md) は、IPRO7AI Reef EVK のメインチップです。

<div class="ipro-facts" markdown>
<div><strong>192 MHz</strong><span>RISC-V RV32IMAFC</span></div>
<div><strong>256 KB</strong><span>OCRAM</span></div>
<div><strong>8 MB</strong><span>PSRAM（オプション、IPRO7AI は内蔵）</span></div>
<div><strong>BLE 5.4</strong><span>LE Audio、802.15.4</span></div>
<div><strong>42</strong><span>GPIO（QFN56）</span></div>
</div>

## 概要 { #chip-overview }

- **処理とメモリ**：DSP 拡張付きの RV32IMAFC、256 KB の OCRAM、ハイバネート中も保持される 4 KB の RAM を備え、コードは Flash 上で直接実行（execute in place）します。8 MB のパッケージ内蔵 PSRAM はオプションです（IPRO7AI バリアントは内蔵）。
- **ワイヤレス**：統合された 2.4 GHz RF トランシーバーで、LE Audio 対応の Bluetooth 5.4 LE と IEEE 802.15.4 に対応します。
- **画像と音声**：DVP カメラインターフェース、ISP、MJPEG コーデック、オーディオ ADC、GPDAC、I2S を備えます。
- **ネットワーク**：有線ネットワークはオンチップの EMAC（RMII）を使います。無線ネットワークは SDIO または UART で接続した外部無線チップを使います（例：SDIO 接続の IPRO6S）。[ネットワーク接続](#networking)を参照してください。

## 主な仕様 { #key-specs }

### プロセッサーとシステム { #cpu-memory }

| 項目 | 仕様 |
|---|---|
| CPU | DSP 拡張付き RISC-V RV32IMAFC、192 MHz |
| キャッシュ | L1 命令キャッシュ 16 KB / データキャッシュ 16 KB |
| OCRAM | 256 KB |
| ハイバネート RAM | 4 KB（HBN RAM） |
| ROM | 128 KB |
| eFuse | 2 Kb |
| PSRAM | オプション、パッケージ内蔵 8 MB（IPRO7AI バリアントは内蔵）。QFN32 にはなし |
| Flash | Flash 上で直接実行。SDK はデフォルトで 1 MB のレイアウトをリンクし、`CONFIG_IPRO7_FLASH_2M` とその同系オプションで 2 / 4 / 8 MB を選択します |
| 時間管理 | RTC、タイマー 2 個、ウォッチドッグ（WDT） |
| DMA | 8 チャネル |
| クロック | ボード上は 32 MHz の水晶振動子。PLL で 192 MHz のシステムクロックを生成します |

### ワイヤレス { #wireless }

| 項目 | 仕様 |
|---|---|
| Bluetooth | Bluetooth 5.4 LE。1M / 2M PHY と Long Range（Coded PHY、500 / 125 kbps） |
| LE Audio | CIS / BIS アイソクロナスチャネル。BLE コントローラーの `bt54_iso2` ビルドが必要です |
| 接続数 | 本リリースのビルド済みコントローラー（`link1_periph` / `link1` / `link2` / `link4`）で最大 4 |
| IEEE 802.15.4 | 802.15.4 無線。SDK は Zephyr RTOS 上でドライバーと OpenThread を提供します |
| RF | バランと PA / LNA を内蔵した 2.4 GHz トランシーバー。外部 PA / LNA 用の制御信号あり |

### ネットワーク接続 { #networking }

有線ネットワークはオンチップの EMAC（RMII）を使います。無線ネットワークは SDIO または UART で接続した外部無線チップを使います。SDK には次のドライバーが含まれています。

| 無線チップ | インターフェース | SDK 内の場所 |
|---|---|---|
| IPRO6S（Wi-Fi 6） | SDIO、lwIP ネットワークインターフェース `iproeth0` | `components/network/ipronet_host`。Reef では microSD スロットの FIN カードです。[IPRO6S](ipro6s.md) を参照 |
| ATBM6162 | SDIO | `components/wireless/wifi_atbm6162`、`ipro_atbm_probe` |
| AIC8800 | SDIO（ベンダー提供のビルド済みライブラリ） | `components/wireless/wifi_aic8800`、`ipro_agora_sentino` の `config_evk` |
| ESP32 | UART AT コマンド | `components/network/esp32_wifi_at`、`ipro7_demo`（`CONFIG_ESP32_WIFI_AT`） |

### マルチメディアと AI { #ai-multimedia }

| 項目 | 仕様 |
|---|---|
| カメラ | 8 ビット DVP と SPI のカメラインターフェース、ISP |
| 映像 | ハードウェア MJPEG エンコーダーとデコーダー |
| ディスプレイ | DBI / SPI ディスプレイインターフェース |
| 音声入力 | PDM デジタルマイクとアナログマイク用のオーディオ ADC（AUADC）。ドライバーは 16 ビットと 20 ビットの分解能に対応します |
| 音声出力 | GPDAC（2 チャネル、10 ビット）、I2S |
| NPU | 0.1 TOPS。IPRO7AI バリアントで有効です。[IPRO7AI](ipro7ai.md) を参照 |

### セキュリティ { #security }

| 項目 | 仕様 |
|---|---|
| ブートとデバッグ | Secure Boot、Secure Debug |
| 暗号エンジン | AES（ECB / CTR / CBC / XTS）、GMAC、SHA-1 / 224 / 256 / 384 / 512、MD5 |
| 公開鍵 | PKA（RSA / ECC アクセラレーション） |
| 乱数 | TRNG |
| Flash 保護 | Flash のオンザフライ AES 復号（OTFAD） |

### 周辺機能インターフェース { #interfaces }

| インターフェース | 数 / 仕様 | 備考 |
|---|---|---|
| GPIO | 42（QFN56） | 各 GPIO は機能値 0–27 で役割を選択します。[ピン配置と周辺機能マッピング](../pinmux.md)を参照 |
| UART | 2 | TX / RX / CTS / RTS は UART 信号を経由して GPIO に割り当てられます |
| SPI | 2 | マスター / スレーブ、8 / 16 / 24 / 32 ビットデータ |
| I2C | 2 | マスター / スレーブ |
| I2S | 1 | マスター / スレーブ。標準、左詰め、右詰め、DSP フォーマット |
| PWM | 4 チャネル | チャネルごとに相補 H / L 出力 |
| GPADC | 外部 12 チャネル | 12 ビット。ハードウェア平均化による 14 ビット / 16 ビット出力にも対応 |
| GPDAC | 2 チャネル | 10 ビット。チャネル A は GPIO23、チャネル B は GPIO22 |
| QDEC | 3 | 直交デコーダー（マウス、ロータリーノブ） |
| KYS | 1 | キースキャン |
| IR | 1 | 赤外線リモコン受信 |
| USB | 1 | USB 2.0 フルスピード、デバイス / ホスト |
| SD / SDIO | 1 | SD ホスト（SDH）、1 / 4 ビット、GPIO28–33 に固定 |
| Ethernet | 1 | RMII 対応の EMAC |
| PIO | 1 | プログラマブル IO |

### パッケージ { #packages }

| パッケージ | GPIO | 備考 |
|---|---|---|
| QFN56（7 × 7 mm） | 42（GPIO0–41） | 標準パッケージ。USB は GPIO8 / 9 |
| QFN32 | より少ない（例：GPIO41 なし） | パッケージ内蔵 PSRAM なし、NPU なし |

## メモリマップ { #memory-map }

| 領域 | サイズ | ベースアドレス | 備考 |
|---|---|---|---|
| Flash | 1 MB | `0x13000000` | Flash 上で直接実行。`CONFIG_IPRO7_FLASH_2M` とその同系オプションで 2 / 4 / 8 MB を選択します |
| PSRAM | 8 MB | `0x1e000000` | AI / NPU と ISP のアプリケーションで必要です。`.config` に `CONFIG_USE_PSRAM=y` を明示的に設定してください |
| OCRAM | 256 KB | `0x11010000` | スタック、割り込み処理、タイミングがクリティカルなコード。BLE コントローラーの Exchange Memory は上端から確保されます。PDS31 スリープでは先頭 64 KB だけが保持され、残りは MISC 電源ドメインがオンのままの場合にのみ保持されます |
| HBN RAM | 4 KB | `0x20090000` | ハイバネート中も保持されます |

AI と画像処理の両方を有効にすると（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）、リンカーは OCRAM を 64 KB に制限します。[IPRO7AI](ipro7ai.md#memory) を参照してください。

## 本リリースでの SDK サポート { #sdk-support }

| 項目 | V2.2.1 |
|---|---|
| FreeRTOS アプリケーション | 40 個のうち 37 個が IPRO7 対象：`CONFIG_IPRO7=y`、`CONFIG_CHIP="IPRO7"`、`CONFIG_CPU_ID="intelpro_ipro7"`。イメージは `<app>_IPRO7.bin` |
| Zephyr RTOS | Zephyr v4.4.0 モジュール。ボードは `ipro7_evb` と `ipro7ai_evk`。本リリースには Reef 用の Zephyr ボードはありません |
| ツールチェーン | RISC-V GCC（`riscv64-unknown-elf-`、`rv32imafc` / `ilp32f`）。SDK には含まれていないため、INTELPRO から入手してください |
| BLE | Zephyr v4.4.0 ホスト（ソース）を IPRO BLE コントローラー（ビルド済みライブラリ、IPRO7 用 16 ビルド：`link1_periph` / `link1` / `link2` / `link4` × `bt52` / `bt54_iso2` × debug / `_release`）上で使用 |
| IEEE 802.15.4 / Thread | Zephyr RTOS のみ：IEEE 802.15.4 ドライバーと OpenThread |
| Matter、Zigbee | V2.2.1 には含まれていません。INTELPRO にお問い合わせください。 |
| 書き込み | IntelProCube 0.7.0.1 コマンドラインツール（[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases)）：`--chipname ipro7`。Reef などの IPRO7AI ボードでは `--chip-variant IPRO7AI` を追加します |

## IPRO7 搭載ボード { #boards }

| ボード | チップ | ボード設定 |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | IPRO7AI（QFN56、ボードに実装） | `CONFIG_IPRO7AI_REEF=y`、`CONFIG_BOARD="IPRO7AI_REEF"` |

IPRO7 EVB（`CONFIG_EVB=y`）と IPRO7AI EVK（`CONFIG_IPRO7AI_EVK=y`）は、多くのアプリケーションの `.config` でデフォルトのボードです。これらのボードについては INTELPRO にお問い合わせください。

## 関連ドキュメント { #documents }

- [IPRO7AI](ipro7ai.md)：NPU と AI サンプル。
- [ピン配置と周辺機能マッピング](../pinmux.md)、[電源と電流測定](../power.md)。
- IPRO7 データシートとハードウェア設計ガイド：[ドキュメント](../../documents/index.md)を参照してください。
