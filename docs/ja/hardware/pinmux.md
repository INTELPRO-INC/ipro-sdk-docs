---
title: "ピン配置と周辺機能マッピング"
description: IPRO7 の GPIO 機能選択、UART / SPI / SDIO / I2S のピン、代替機能表、IPRO7AI Reef EVK のデフォルトピンと拡張ヘッダーの配線
migrate_from:
  - "hardware.html — 腳位定義、GPIO Function Select、UART／SPI／SDIO／I2S Pin Assignment、GPIO0~GPIO31 Alternate Function、周邊連接指南"
---

# ピン配置と周辺機能マッピング

IPRO7 の各 GPIO は、GLB ピンマルチプレクサーで役割が決まります。`GLB_GPIO_Cfg_Type` にピン、機能値（0–27）、モード、プル、駆動能力、シュミットトリガーを設定し、`GLB_GPIO_Init()` を呼び出します。このページの表は `bsp/drivers/ipro7_soc/std_drv/inc/drv_gpio.h`、`drv_glb.h`、Reef のボード設定ヘッダー `bsp/board/ipro7/ipro7ai_reef_board_config.h` に基づいています。ボード全体の配線と 40 ピンヘッダーについては [IPRO7AI Reef EVK](boards/reef-evk.md#pinout) を参照してください。

```c title="1 本のピンを設定する"
/* フィールドの順序：{ pin, function, mode, pull, drive, smt } */
GLB_GPIO_Cfg_Type cfg = { GLB_GPIO_PIN_20, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 };
GLB_GPIO_Init(&cfg);
```

## GPIO の機能選択 { #pinout }

| 値 | 機能（`GPIO_FUN_*`） | 説明 |
|---|---|---|
| 0 | `CLK_OUT` | クロック出力 |
| 1 | `BT_COEXIST` | Bluetooth 共存信号 |
| 2 | `FLASH_PSRAM`（`QSPI`） | Flash / PSRAM / QSPI |
| 3 | `I2S` | I2S オーディオ |
| 4 | `SPI` | SPI0 |
| 5 | `PDM` | PDM デジタルマイク |
| 6 | `I2C` | I2C0 |
| 7 | `UART` | UART（UART 信号を経由して割り当て。後述） |
| 8 | `PWM` | PWM |
| 9 | `CAM` | カメラ DVP |
| 10 | `ANALOG` | ADC / DAC などのアナログ機能 |
| 11 | `GPIO` | 汎用 IO |
| 12 | `RF_TEST` | 内部テスト |
| 13 | `SCAN` | 内部テスト |
| 14 | `MCU_JTAG` | JTAG デバッグ |
| 15 | `DEBUG` | デバッグ信号 |
| 16 | `EXTERNAL_PA` | 外部 PA / LNA 制御 |
| 17 | `USB_TRANCEIVER` | USB PHY |
| 18 | `USB_CONTROLLER` | USB コントローラー |
| 19 | `ETHER_MAC`（`EMAC`） | Ethernet RMII |
| 20 | `QDEC` | 直交デコーダー |
| 21 | `KEY_SCAN_IN`（`KEY_SCAN_ROW`） | キースキャンの行入力 |
| 22 | `KEY_SCAN_DRIVE`（`KEY_SCAN_COL`） | キースキャンの列駆動 |
| 23 | `CAM_MISC` | カメラの PWDN / RESET / リファレンスクロック |
| 24 | `PIO` | プログラマブル IO |
| 25 | `I2C1` | I2C1 |
| 26 | `SPI1` | SPI1 |
| 27 | `SDC` | SD カード（SDIO） |

## UART のピン { #uart-pins }

UART は 2 段のマルチプレクサーを使うため、ほとんどの GPIO に配置できます。

1. GPIO を機能 7 に設定します。そのピンは UART 信号 N になります。N = GPIO 番号 mod 12 です（`GLB_UART_SIG_0`–`GLB_UART_SIG_11`）。
2. `GLB_UART_Fun_Sel()` で、その信号を UART0 / UART1 の TXD、RXD、CTS、RTS のいずれかに割り当てます。

12 で割った余りが同じ番号のピンは 1 つの信号を共有するため、それぞれに異なる UART 信号を同時に割り当てることはできません。

Reef のコンソールは UART0 で、GPIO20（`GLB_UART_SIG_8` → TXD）と GPIO21（`GLB_UART_SIG_9` → RXD）を使い、U6 デバッグコネクターの 3 / 4 番ピンと J_IO の 8 / 10 番ピンに接続されています。GPIO20 / 21 は Boot ROM の UART ダウンロード用ピンでもあります。コンソールのボーレートはアプリケーションの `CONFIG_PLATFORM_UART_BAUDRATE` で決まり、未設定の場合は 115200 です。

| GPIO | 信号 | GPIO | 信号 | GPIO | 信号 |
|---|---|---|---|---|---|
| 0 | SIG_0 | 12 | SIG_0 | 24 | SIG_0 |
| 1 | SIG_1 | 13 | SIG_1 | 25 | SIG_1 |
| 2 | SIG_2 | 14 | SIG_2 | 26 | SIG_2 |
| 3 | SIG_3 | 15 | SIG_3 | 27 | SIG_3 |
| 4 | SIG_4 | 16 | SIG_4 | 28 | SIG_4 |
| 5 | SIG_5 | 17 | SIG_5 | 29 | SIG_5 |
| 6 | SIG_6 | 18 | SIG_6 | 30 | SIG_6 |
| 7 | SIG_7 | 19 | SIG_7 | 31 | SIG_7 |
| 8 | SIG_8 | 20 | SIG_8 | 32 | SIG_8 |
| 9 | SIG_9 | 21 | SIG_9 | 33 | SIG_9 |
| 10 | SIG_10 | 22 | SIG_10 | | |
| 11 | SIG_11 | 23 | SIG_11 | | |

| 信号機能（`GLB_UART_SIG_FUN_*`） | 説明 | 信号機能 | 説明 |
|---|---|---|---|
| `UART0_TXD` | UART0 送信 | `UART1_TXD` | UART1 送信 |
| `UART0_RXD` | UART0 受信 | `UART1_RXD` | UART1 受信 |
| `UART0_RTS` | UART0 Request To Send | `UART1_RTS` | UART1 Request To Send |
| `UART0_CTS` | UART0 Clear To Send | `UART1_CTS` | UART1 Clear To Send |

`GLB_UART_Sig_Swap_Set()` では、GPIO0–7、GPIO8–15、GPIO16–22 の各グループで個別にスワップを有効にでき、グループ内で `uart_sig[0:3]` と `uart_sig[4:7]` を入れ替えます。スタートアップコードは `UART_SIG_SWAP_NONE`（スワップなし）を設定しており、表はこの状態を示しています。

```c title="UART1：TXD を GPIO2、RXD を GPIO3 に割り当て（Reef の J_IO 40 / 38 番ピン、SW7 は GPIO）"
GLB_GPIO_Cfg_Type uart_pins[] = {
    { GLB_GPIO_PIN_2, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
    { GLB_GPIO_PIN_3, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
};
GLB_GPIO_Init(&uart_pins[0]);
GLB_GPIO_Init(&uart_pins[1]);

/* GPIO2 -> SIG_2、GPIO3 -> SIG_3（GPIO 番号 mod 12） */
GLB_UART_Fun_Sel(GLB_UART_SIG_2, GLB_UART_SIG_FUN_UART1_TXD);
GLB_UART_Fun_Sel(GLB_UART_SIG_3, GLB_UART_SIG_FUN_UART1_RXD);
```

## SPI のピン { #spi-pins }

SPI0（機能 4）は 4 本の GPIO を 1 グループとして使い、役割はピン番号 mod 4 で決まります。0 = MOSI、1 = MISO、2 = SS、3 = SCLK です（`pin_swap_enable = 0` の場合）。`pin_swap_enable = 1` にすると MOSI と MISO が入れ替わります。SDK のデフォルト（`bsp/board/ipro7/peripheral_config.h`）は 1 です。

| グループ | MOSI（swap = 0）/ MISO（swap = 1） | MISO（swap = 0）/ MOSI（swap = 1） | SS | SCLK |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

SPI1（機能 26）は独立した 2 つ目の SPI で、グループ分けの規則は同じです。

| 項目 | SPI0 | SPI1 |
|---|---|---|
| デフォルトクロック | 18 MHz | 18 MHz |
| データ幅 | 8 / 16 / 24 / 32 ビット | 8 / 16 / 24 / 32 ビット |
| モード | マスター / スレーブ | マスター / スレーブ |
| CPOL / CPHA | 設定可能（デフォルト：CPOL Low、1 番目のエッジでサンプリング） | 設定可能 |
| デフォルトの DMA チャネル | TX：DMA_CH3、RX：DMA_CH4 | — |
| ピンスワップ | MOSI / MISO を入れ替え可能 | MOSI / MISO を入れ替え可能 |

Reef の WS2812 のデータ線は GPIO24（mod 4 = 0）にあり、SPI0 MOSI で駆動するため、`pin_swap_enable = 0` が必要です。J_IO での SPI については [Reef の拡張ヘッダーでの周辺機器](#peripherals)を参照してください。

```c title="GPIO4–7 グループの SPI0（pin_swap_enable = 0）"
GLB_GPIO_Cfg_Type spi_pins[] = {
    { GLB_GPIO_PIN_4, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_NONE, 1, 1 }, /* MOSI */
    { GLB_GPIO_PIN_5, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_NONE, 1, 1 }, /* MISO */
    { GLB_GPIO_PIN_6, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_UP,   1, 1 }, /* SS */
    { GLB_GPIO_PIN_7, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_NONE, 1, 1 }, /* SCLK */
};
for (int i = 0; i < 4; i++) {
    GLB_GPIO_Init(&spi_pins[i]);
}
```

## SDIO / SD カードのピン { #sdio-pins }

SD ホスト（SDH、機能 27）は常に GPIO28–33 を使います。これらのピンは外部 Flash（SF2 / SF3）にもつながっています。`CONFIG_DISABLE_SDC_PINMUX` を定義すると、GPIO28–33 は外部 Flash に割り当てられ、SD カードは使えなくなります。Reef の microSD スロットはこれらのピンに配線されています。IPRO6S FIN カードをスロットに挿した場合、IPRO7AI は同じピンで SDIO によりカードを制御します。

| GPIO | SDC 信号 | プル | 駆動能力 | 説明 |
|---|---|---|---|---|
| GPIO28 | SDC_DAT1 | プルアップ | 2 | データビット 1 |
| GPIO29 | SDC_DAT0 | プルアップ | 2 | データビット 0 |
| GPIO30 | SDC_CLK | なし | 2 | クロック |
| GPIO31 | SDC_CMD | プルアップ | 2 | コマンドライン |
| GPIO32 | SDC_DAT3 | プルアップ | 2 | データビット 3 |
| GPIO33 | SDC_DAT2 | プルアップ | 2 | データビット 2 |

| 項目 | 仕様 |
|---|---|
| バス幅 | 1 ビット / 4 ビット |
| クロックソース | `GLB_SDH_CLK_DLL_64M` / `GLB_SDH_CLK_PLL_96M` |
| ボードのデフォルト | PLL_96M、`div = 1`（48 MHz） |
| プロトコル | SD 3.0 / SDIO |

Reef では、カード検出は GPIO15（カードが挿入されていると 0）で、GPIO14 がスロットの電源を切り替えます（JP3 が GPIO のとき、Low = オン）。CMD と DAT には外部プルアップがなく、SDK のボード設定で IPRO7AI の内部プルアップを有効にしています。GPIO14 でスロットの電源を切る前に、GPIO28–33 を Low に駆動するか入力にしてください。

## I2S のピン { #i2s-pins }

I2S0（機能 3）は 4 本の GPIO を 1 グループとして使い、各ピンの位置は固定です。3 番目のピンは DIO / DO、4 番目のピンは RCLK_O / DI です。全二重では DO が出力、DI が入力になり、半二重では DIO で双方向にデータを転送します。

| グループ | BCLK | FS（LRCLK） | DIO / DO | RCLK_O / DI |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

| 項目 | I2S0 |
|---|---|
| モード | マスター / スレーブ |
| フォーマット | 標準 I2S、左詰め、右詰め、DSP-A、DSP-B |
| サンプリングレート | 8 kHz–96 kHz |
| フレーム / データサイズ | 8 / 16 / 24 / 32 ビット |
| チャネル | モノラル、ステレオ。DSP フォーマットでは最大 4 チャネル |
| FIFO の深さ | 8 エントリ |
| デフォルトの DMA チャネル | TX：DMA_CH5 / DMA_CH6 |
| MCLK 出力 | RCLK_O ピン |
| SDK のデフォルト | マスター、左詰め、16 kHz、モノラル、16 ビット |

## GPIO0–GPIO31 の代替機能 { #alt-functions }

周辺機能の設計に関係する機能のみを示します。すべての GPIO には、このほかに GPIO（11）、JTAG（14）、DEBUG（15）があります。すべて「—」の行は省略しています。

- MOSI\* / MISO\*：`pin_swap_enable` によって入れ替わります。
- UART 行の Sn は UART 信号 n です（スワップなし）。
- QDEC 行：Qn_A / Qn_B は QDECn の A 相 / B 相、Qn_LED はその LED 駆動です。
- ADC 行の CHn は GPADC のチャネルです。DAC_A / DAC_B は 2 つの GPDAC 出力です。
- PWM 行の CH0–CH4 は GPIO 機能定義（`drv_gpio.h`）の信号名です。PWM ドライバー（`drv_pwm.h`）が提供するのは CH0–CH3 だけで、CH4 に割り当てたピンにはドライバーがありません。

### GPIO0–GPIO7 { #alt-gpio0-7 }

| 機能 | GPIO0 | GPIO1 | GPIO2 | GPIO3 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
|---|---|---|---|---|---|---|---|---|
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
| 8 PWM | CH0 | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 | CH2 |
| 10 ADC / DAC | — | — | — | — | — | — | — | CH6 / DAC 外部リファレンス |
| 19 RMII | REF_CLK | TXD0 | TXD1 | — | — | — | — | RXD0 |
| 20 QDEC | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B | Q1_LED | Q2_A | Q2_B |

### GPIO8–GPIO15 { #alt-gpio8-15 }

| 機能 | GPIO8 | GPIO9 | GPIO10 | GPIO11 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
|---|---|---|---|---|---|---|---|---|
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S8 | S9 | S10 | S11 | S0 | S1 | S2 | S3 |
| 8 PWM | CH3 | CH4 | CH0 | CH1 | CH2 | CH3 | CH4 | CH0 |
| 10 ADC | CH0 | CH7 | MICBIAS | CH3 | CH4 | — | CH5 | CH1 |
| 19 RMII | RXD1 | — | — | — | — | — | — | — |
| 20 QDEC | Q2_LED | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B | Q1_LED | Q2_A |

### GPIO16–GPIO23 { #alt-gpio16-23 }

| 機能 | GPIO16 | GPIO17 | GPIO18 | GPIO19 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
|---|---|---|---|---|---|---|---|---|
| 2 Flash | — | SF_IO0 | SF_IO1 | SF_CS | SF_IO3 | SF_CLK | SF_IO2 | SF2_IO2 |
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 |
| 8 PWM | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 | CH2 | CH3 |
| 10 ADC / DAC | — | CH2 | CH8 | CH9 | CH10 | CH11 | DAC_B | DAC_A |
| 19 RMII | — | — | MDC | MDIO | RXERR | TX_EN | RX_DV | — |
| 20 QDEC | Q2_B | Q2_LED | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B | Q1_LED |

### GPIO24–GPIO31 { #alt-gpio24-31 }

| 機能 | GPIO24 | GPIO25 | GPIO26 | GPIO27 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |
|---|---|---|---|---|---|---|---|---|
| 2 Flash | SF2_IO1 | SF2_CS | SF2_IO3 | SF2_CLK | SF2_IO0 | — | — | — |
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
| 8 PWM | CH4 | CH0 | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 |
| 19 RMII | MDC | MDIO | RXERR | TX_EN | RX_DV | — | — | — |
| 20 QDEC | Q2_A | Q2_B | Q2_LED | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B |
| 27 SDC | — | — | — | — | DAT1 | DAT0 | CLK | CMD |

## DVP カメラのピン { #camera-pins }

Reef の OV5640 カメラの配線です（SW7 は CAM にする必要があります）。

| 信号 | GPIO |
|---|---|
| D0–D7 | GPIO0–7 |
| PCLK | GPIO38 |
| VSYNC | GPIO39 |
| HSYNC / HREF | GPIO40 |
| XCLK（`CAM_MISC` のリファレンスクロック、IPRO7AI が駆動） | GPIO22 |
| RESETB | GPIO34 |
| PWDN | GPIO35 |
| SCCB SCL / SDA（I2C0） | GPIO36 / GPIO37 |

VDDIO1 電源ドメインは GPIO0–9 と GPIO36–41（カメラ、USB、BOOT のピン）を含みます。I2C0 の役割はピン番号の偶奇で決まり、偶数が SCL、奇数が SDA です。SW7 が GPIO のときは、これら 16 ピンは代わりに J_IO に接続され、カメラの 2.8 V と 1.5 V のレギュレーターはオフになります。

## ボードのデフォルトピン { #board-default-pins }

### IPRO7AI Reef EVK { #reef-default-pins }

`bsp/board/ipro7/ipro7ai_reef_board_config.h` の内容で、起動時に設定されます。Reef には JTAG コネクターはありません。カメラ、オーディオ、アナログのピンは、有効にしたときに各ドライバーが設定します。

| GPIO | 機能 | 設定 | 用途 |
|---|---|---|---|
| GPIO14 | GPIO（11） | 出力、Low | microSD スロットの電源スイッチ（JP3 が GPIO のとき、Low = オン） |
| GPIO15 | GPIO（11） | 入力、プルアップ | microSD カード検出 |
| GPIO20 | UART（7） | プルアップ | コンソール TX |
| GPIO21 | UART（7） | プルアップ | コンソール RX |
| GPIO24 | GPIO（11） | 出力、Low | WS2812 のデータ線。電源投入時に LED が点灯しないよう Low に保持します |
| GPIO25 | GPIO（11） | 出力、プルダウン、アンプはオフ | スピーカーアンプのイネーブル（アクティブ High） |
| GPIO28–33 | SDC（27） | DAT と CMD はプルアップ、駆動能力 2 | microSD スロット / FIN カード |

その他のボード（IPRO7 EVB、IPRO7AI EVK）のデフォルトピンは、`bsp/board/ipro7/` にある各ボードの設定ヘッダーに記載されています。これらのボードについては INTELPRO にお問い合わせください。

## ピンの競合と設計上の注意 { #pin-conflicts }

- **GPIO20 / 21**：Boot ROM の UART ダウンロードとコンソールで使用します。U6 に接続したままにしてください。
- **GPIO0–7、GPIO22、GPIO34–40**：Reef のカメラ用ピンです。SW7 が CAM のときはカメラが使い、GPIO のときは J_IO に接続されてカメラはオフになります。
- **GPIO10、GPIO11、GPIO27**：Reef のキー SW3、SW5、SW4（押すと Low）です。J_IO にも引き出されています。
- **GPIO12、GPIO13**：Reef のヘッドセットマイク用アナログ入力（AIN6、AIN7）です。
- **GPIO17–22**：Flash（SF）機能を持ちます。空いているかどうかは番号だけでは決まらず、パッケージ、Flash の構成、回路図によって決まります。
- **GPIO23–28**：外部 Flash（SF2）と共用です。Reef では GPIO23 が GPDAC のスピーカー出力、GPIO24 が WS2812、GPIO25 がアンプのイネーブル、GPIO26 がヘッドセット検出入力です。
- **GPIO28–33**：SD カードまたは外部 Flash（SF2 / SF3）に使い、`CONFIG_DISABLE_SDC_PINMUX` で選択します。Reef では microSD スロットに使っています。
- **GPIO18 / 19**：32 kHz 水晶振動子のピンです。Reef では水晶振動子は実装されておらず、この 2 本は J_IO の I2C です（ボード上に 4.7 kΩ プルアップ）。
- **I/O 電圧**：Reef V4.0 の IO はすべて 3.3 V です。5 V の信号は絶対に接続しないでください。
- **シュミットトリガー**：ピンごとに設定します（`GLB_GPIO_Cfg_Type` の最後のフィールド）。

## 周辺機器の接続ガイド { #peripherals }

Reef の 40 ピン拡張ヘッダー J_IO は、Raspberry Pi と同じ位置とピン順です。表には、IPRO7 のピン機能によって J_IO で使えるインターフェースを示します。SDK にはこれらの Reef 用サンプル構成はありません。前のセクションの説明に従ってピン機能を設定してください。条件が「SW7 が GPIO」のインターフェースはカメラのピンを使うため、その間カメラはオフになります。

| インターフェース | J_IO のピン | GPIO と機能 | 条件 |
|---|---|---|---|
| I2C | 3 SDA、5 SCL | GPIO19、GPIO18、I2C0（機能 6） | ボード上に 4.7 kΩ プルアップ。SW7 はどちらの位置でも可 |
| SPI0 | 19 MOSI、21 MISO、23 SCLK、24 SS | GPIO4、GPIO5、GPIO7、GPIO6、グループ 1（機能 4） | SW7 が GPIO。`pin_swap_enable = 0` |
| I2S0 | 12 BCLK、35 FS、40 DO、38 DI | GPIO0、GPIO1、GPIO2、GPIO3、グループ 0（機能 3） | SW7 が GPIO |
| UART1 | 40 TXD、38 RXD | GPIO2（SIG_2）、GPIO3（SIG_3）、機能 7 | SW7 が GPIO。I2S0 とはどちらか一方のみ |
| 2 つ目の I2C の位置（ID EEPROM） | 27 SDA、28 SCL | GPIO37、GPIO36 | SW7 が GPIO |
| コンソール UART0 | 8 TXD、10 RXD | GPIO20、GPIO21 | コンソールが使用 |

J_IO の 1 番、17 番ピンは 3.3 V 出力です。2 番、4 番ピンはダイオードを介して USB の 5 V を出力し、ボードへの給電には使えません。ピン表の全体は [IPRO7AI Reef EVK](boards/reef-evk.md#j-io) にあります。

### I2C センサー { #i2c-sensor }

| J_IO | IPRO7AI | センサー |
|---|---|---|
| 1 | 3.3 V | VDD |
| 3 | GPIO19（機能 6、I2C0_SDA） | SDA |
| 5 | GPIO18（機能 6、I2C0_SCL） | SCL |
| 6 | GND | GND |

ボードにはすでに 4.7 kΩ のプルアップがあるため、追加しないでください。I2C1（機能 25）は独立した 2 つ目の I2C コントローラーです。

### SPI 周辺機器（LCD / センサー） { #spi-peripheral }

| J_IO | IPRO7AI | 周辺機器 |
|---|---|---|
| 19 | GPIO4（機能 4、SPI0_MOSI） | SDI / MOSI |
| 21 | GPIO5（機能 4、SPI0_MISO） | SDO / MISO |
| 23 | GPIO7（機能 4、SPI0_SCLK） | SCK |
| 24 | GPIO6（機能 4、SPI0_SS） | CS# |

SW7 を GPIO にし、`pin_swap_enable = 0` にする必要があります。MOSI と MISO の位置については [SPI のピン](#spi-pins)を参照してください。

### I2S オーディオコーデック { #codec }

| J_IO | IPRO7AI | コーデック |
|---|---|---|
| 12 | GPIO0（機能 3、I2S0_BCLK） | BCLK |
| 35 | GPIO1（機能 3、I2S0_FS） | LRCLK / WS |
| 40 | GPIO2（機能 3、I2S0_DO） | DIN |
| 38 | GPIO3（機能 3、I2S0_DI） | DOUT |

SW7 を GPIO にする必要があります。コーデックの制御インターフェースは J_IO の I2C（3 番、5 番ピン）に接続します。4 本ずつのグループは順に BCLK、FS、DO、DI です。[I2S のピン](#i2s-pins)を参照してください。

### UART の拡張 { #uart-expansion }

UART1 はほとんどの GPIO に配置できます。J_IO では、SW7 を GPIO にして GPIO2（40 番ピン、TXD）と GPIO3（38 番ピン、RXD）を使い、[UART のピン](#uart-pins)のサンプルのように設定します。GPIO20 / 21 は Boot ROM の UART ダウンロードとコンソール用に予約したままにしてください。

### SD カード { #sd-card }

Reef の microSD スロットは常に GPIO28–33 を使います。これらのピンは J_IO には出ていません。

| IPRO7AI | SD カード |
|---|---|
| GPIO28（機能 27、SDC_DAT1） | DAT1 |
| GPIO29（機能 27、SDC_DAT0） | DAT0 |
| GPIO30（機能 27、SDC_CLK） | CLK |
| GPIO31（機能 27、SDC_CMD） | CMD |
| GPIO32（機能 27、SDC_DAT3） | DAT3 |
| GPIO33（機能 27、SDC_DAT2） | DAT2 |

### PDM マイク { #pdm-mic }

PDM マイクはオーディオ ADC（AUADC）で取り込みます。ピンの役割は番号の偶奇で決まり、偶数が PDM_CLK、奇数が PDM_DATA です。Reef のオンボード PDM マイク MK1 は CLK が GPIO16、DATA が GPIO17 で、`ipro7ai_reef_demo` の `mic rec pdm` でこのマイクから録音できます。

### アンテナ { #antenna }

2.4 GHz アンテナの選択：

| 種類 | 特徴 |
|---|---|
| PCB アンテナ | 低コスト。キープアウト領域が必要 |
| チップアンテナ | 小型。整合回路が必要 |
| 外部アンテナ | 性能が最も高い。U.FL コネクターが必要 |

RF 出力とアンテナの間に π 型整合回路を入れます。RF 側にグラウンドへのシャントコンデンサー、直列インダクター、アンテナ側にもう 1 つのグラウンドへのシャントコンデンサーを配置します。Reef はデフォルトで PCB アンテナ E1 を使います。0 Ω 抵抗を R2 から R1 に移すと、代わりに u.FL コネクター RF1 を使えます。

## 関連ドキュメント { #documents }

- [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)：オンボードの配線、J_IO と U6 のピン表。
- [IPRO7](chips/ipro7.md#interfaces)：周辺機能の数と仕様。
- [電源と電流測定](power.md)：Reef の給電方法と電流の測定方法。
- IPRO7 データシートとハードウェア設計ガイド（ピン定義、GPIO マルチプレクス）：[ドキュメント](../documents/index.md)を参照してください。
