---
title: "腳位與周邊對照"
description: IPRO7 GPIO 功能選擇、UART／SPI／SDIO／I2S 腳位、替代功能表、開發板預設腳位與周邊接線範例
migrate_from:
  - "hardware.html — 腳位定義、GPIO Function Select、UART／SPI／SDIO／I2S Pin Assignment、GPIO0~GPIO31 Alternate Function、周邊連接指南"
---

# 腳位與周邊對照

IPRO7 每支 GPIO 由 GLB 腳位多工器選擇功能：在 `GLB_GPIO_Cfg_Type` 填入腳位、功能值（0–27）、模式、上下拉、驅動強度與 Schmitt 觸發，再呼叫 `GLB_GPIO_Init()`。本頁的表格依 `bsp/drivers/ipro7_soc/std_drv/inc/drv_gpio.h`、`drv_glb.h` 與各開發板的設定檔整理；各板的完整接線見 [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)、[IPRO7AI EVK](boards/ipro7ai-evk.md#pinout) 與 [IPRO7 EVB](boards/ipro7-evb.md#default-pins)。

```c title="設定一支腳位"
/* 欄位順序：{ pin, function, mode, pull, drive, smt } */
GLB_GPIO_Cfg_Type cfg = { GLB_GPIO_PIN_20, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 };
GLB_GPIO_Init(&cfg);
```

## GPIO 功能選擇 { #pinout }

| 值 | 功能（`GPIO_FUN_*`） | 說明 |
|---|---|---|
| 0 | `CLK_OUT` | 時脈輸出 |
| 1 | `BT_COEXIST` | 藍牙共存訊號 |
| 2 | `FLASH_PSRAM`（`QSPI`） | Flash／PSRAM／QSPI |
| 3 | `I2S` | I2S 音訊 |
| 4 | `SPI` | SPI0 |
| 5 | `PDM` | PDM 數位麥克風 |
| 6 | `I2C` | I2C0 |
| 7 | `UART` | UART（經 UART signal 繞線，見下節） |
| 8 | `PWM` | PWM |
| 9 | `CAM` | 相機 DVP |
| 10 | `ANALOG` | ADC／DAC 等類比功能 |
| 11 | `GPIO` | 一般用途 IO |
| 12 | `RF_TEST` | 內部測試用 |
| 13 | `SCAN` | 內部測試用 |
| 14 | `MCU_JTAG` | JTAG 除錯 |
| 15 | `DEBUG` | 除錯訊號 |
| 16 | `EXTERNAL_PA` | 外接 PA／LNA 控制 |
| 17 | `USB_TRANCEIVER` | USB PHY |
| 18 | `USB_CONTROLLER` | USB 控制器 |
| 19 | `ETHER_MAC`（`EMAC`） | 乙太網路 RMII |
| 20 | `QDEC` | 正交解碼器 |
| 21 | `KEY_SCAN_IN`（`KEY_SCAN_ROW`） | 鍵盤掃描列輸入 |
| 22 | `KEY_SCAN_DRIVE`（`KEY_SCAN_COL`） | 鍵盤掃描行驅動 |
| 23 | `CAM_MISC` | 相機 PWDN／RESET／參考時脈 |
| 24 | `PIO` | 可程式化 IO |
| 25 | `I2C1` | I2C1 |
| 26 | `SPI1` | SPI1 |
| 27 | `SDC` | SD 卡（SDIO） |

## UART 腳位 { #uart-pins }

UART 採兩段式多工，所以可以放在多數 GPIO 上：

1. 把 GPIO 設為功能 7，這支腳就成為 UART signal N，N = GPIO 編號 mod 12（`GLB_UART_SIG_0`–`GLB_UART_SIG_11`）。
2. 以 `GLB_UART_Fun_Sel()` 把該 signal 對應到 UART0／UART1 的 TXD、RXD、CTS 或 RTS。

編號除以 12 餘數相同的腳位共用同一個 signal，不能同時擔任不同的 UART 訊號。

三塊開發板的主控台都在 UART0：GPIO20（`GLB_UART_SIG_8` → TXD）與 GPIO21（`GLB_UART_SIG_9` → RXD）。GPIO20／21 也是 Boot ROM UART 下載使用的腳位。主控台鮑率由應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200。

| GPIO | Signal | GPIO | Signal | GPIO | Signal |
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

| Signal 功能（`GLB_UART_SIG_FUN_*`） | 說明 | Signal 功能 | 說明 |
|---|---|---|---|
| `UART0_TXD` | UART0 傳送 | `UART1_TXD` | UART1 傳送 |
| `UART0_RXD` | UART0 接收 | `UART1_RXD` | UART1 接收 |
| `UART0_RTS` | UART0 Request To Send | `UART1_RTS` | UART1 Request To Send |
| `UART0_CTS` | UART0 Clear To Send | `UART1_CTS` | UART1 Clear To Send |

`GLB_UART_Sig_Swap_Set()` 可對 GPIO0–7、GPIO8–15、GPIO16–22 三組分別啟用交換，把該組的 `uart_sig[0:3]` 與 `uart_sig[4:7]` 對調。啟動程式設定為 `UART_SIG_SWAP_NONE`（不交換），上表即為此預設值。

```c title="UART1：GPIO14 為 TXD、GPIO15 為 RXD"
GLB_GPIO_Cfg_Type uart_pins[] = {
    { GLB_GPIO_PIN_14, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
    { GLB_GPIO_PIN_15, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
};
GLB_GPIO_Init(&uart_pins[0]);
GLB_GPIO_Init(&uart_pins[1]);

/* GPIO14 → SIG_2、GPIO15 → SIG_3（GPIO 編號 mod 12） */
GLB_UART_Fun_Sel(GLB_UART_SIG_2, GLB_UART_SIG_FUN_UART1_TXD);
GLB_UART_Fun_Sel(GLB_UART_SIG_3, GLB_UART_SIG_FUN_UART1_RXD);
```

## SPI 腳位 { #spi-pins }

SPI0（功能 4）以 4 支 GPIO 為一組，角色由腳位編號 mod 4 決定：0 = MOSI、1 = MISO、2 = SS、3 = SCLK（`pin_swap_enable = 0` 時）。`pin_swap_enable = 1` 會交換 MOSI 與 MISO；SDK 的預設值（`bsp/board/ipro7/peripheral_config.h`）為 1。

| 組 | MOSI（swap = 0）／MISO（swap = 1） | MISO（swap = 0）／MOSI（swap = 1） | SS | SCLK |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

SPI1（功能 26）是獨立的第二組 SPI，腳位分組規則與 SPI0 相同。

| 項目 | SPI0 | SPI1 |
|---|---|---|
| 預設時脈 | 18 MHz | 18 MHz |
| 資料寬度 | 8／16／24／32 位元 | 8／16／24／32 位元 |
| 模式 | 主／從 | 主／從 |
| CPOL／CPHA | 可設定（預設 CPOL 低、第一個邊緣取樣） | 可設定 |
| 預設 DMA 通道 | TX：DMA_CH3，RX：DMA_CH4 | — |
| 腳位交換 | MOSI／MISO 可交換 | MOSI／MISO 可交換 |

開發板實例：Reef 的 WS2812 資料線在 GPIO24（mod 4 = 0），以 SPI0 MOSI 驅動，需要 `pin_swap_enable = 0`；IPRO7AI EVK 的 LCD 使用 GPIO15（SCLK）與 GPIO16（MOSI），CS、DC、RST 為一般 GPIO。

```c title="SPI0 使用 GPIO12–15 這一組"
GLB_GPIO_Cfg_Type spi_pins[] = {
    { GLB_GPIO_PIN_12, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_NONE, 1, 1 }, /* MOSI */
    { GLB_GPIO_PIN_13, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_NONE, 1, 1 }, /* MISO */
    { GLB_GPIO_PIN_14, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_UP,   1, 1 }, /* SS */
    { GLB_GPIO_PIN_15, GPIO_FUN_SPI, GPIO_MODE_AF, GPIO_PULL_NONE, 1, 1 }, /* SCLK */
};
for (int i = 0; i < 4; i++) {
    GLB_GPIO_Init(&spi_pins[i]);
}
```

## SDIO／SD 卡腳位 { #sdio-pins }

SD 主控（SDH，功能 27）固定使用 GPIO28–33。這組腳位也接到外接 Flash（SF2／SF3）：定義 `CONFIG_DISABLE_SDC_PINMUX` 時，GPIO28–33 改給外接 Flash，不能同時使用 SD 卡。IPRO7 經 SDIO 連接 IPRO6S Wi-Fi 夥伴晶片時，也使用這組腳位。

| GPIO | SDC 訊號 | 上下拉 | 驅動強度 | 說明 |
|---|---|---|---|---|
| GPIO28 | SDC_DAT1 | 上拉 | 2 | 資料位元 1 |
| GPIO29 | SDC_DAT0 | 上拉 | 2 | 資料位元 0 |
| GPIO30 | SDC_CLK | 無 | 2 | 時脈 |
| GPIO31 | SDC_CMD | 上拉 | 2 | 命令線 |
| GPIO32 | SDC_DAT3 | 上拉 | 2 | 資料位元 3 |
| GPIO33 | SDC_DAT2 | 上拉 | 2 | 資料位元 2 |

| 項目 | 規格 |
|---|---|
| 匯流排寬度 | 1-bit／4-bit |
| 時脈來源 | `GLB_SDH_CLK_DLL_64M`／`GLB_SDH_CLK_PLL_96M` |
| 開發板預設 | PLL_96M，`div = 1`（48 MHz） |
| 協定 | SD 3.0／SDIO |

卡片偵測與電源開關由各板自行配置：Reef 為偵測 GPIO15、電源 GPIO14；IPRO7AI EVK 為電源 GPIO27、偵測 GPIO34。

## I2S 腳位 { #i2s-pins }

I2S0（功能 3）以 4 支 GPIO 為一組，訊號依位置固定。第 3 支為 DIO／DO 雙功能，第 4 支為 RCLK_O／DI 雙功能：全雙工時 DO 輸出、DI 輸入；半雙工時 DIO 雙向傳輸。

| 組 | BCLK | FS（LRCLK） | DIO／DO | RCLK_O／DI |
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
| 模式 | 主／從 |
| 格式 | 標準 I2S、左對齊、右對齊、DSP-A、DSP-B |
| 取樣率 | 8 kHz–96 kHz |
| 框長／資料長度 | 8／16／24／32 位元 |
| 聲道 | 單聲道、立體聲；DSP 格式可到 4 聲道 |
| FIFO 深度 | 8 筆 |
| 預設 DMA 通道 | TX：DMA_CH5／DMA_CH6 |
| MCLK 輸出 | 經 RCLK_O 腳位 |
| SDK 預設 | 主模式、左對齊、16 kHz、單聲道、16 位元 |

## GPIO0–GPIO31 替代功能 { #alt-functions }

只列與周邊設計相關的功能；每支 GPIO 也都有 GPIO（11）、JTAG（14）與 DEBUG（15）功能，此處省略。全部為「—」的列不列出。

- MOSI\*／MISO\*：依 `pin_swap_enable` 交換。
- UART 列的 Sn 代表 UART signal n（預設不交換）。
- QDEC 列：Qn_A／Qn_B 為 QDECn 的 A／B 相，Qn_LED 為 QDECn 的 LED 驅動。
- ADC 列的 CHn 為 GPADC 通道；DAC_A／DAC_B 為 GPDAC 兩個通道的輸出。
- PWM 驅動（`drv_pwm.h`）提供 CH0–CH3。

### GPIO0–GPIO7 { #alt-gpio0-7 }

| 功能 | GPIO0 | GPIO1 | GPIO2 | GPIO3 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
|---|---|---|---|---|---|---|---|---|
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
| 8 PWM | CH0 | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 | CH2 |
| 10 ADC／DAC | — | — | — | — | — | — | — | CH6／DAC 外部參考 |
| 19 RMII | REF_CLK | TXD0 | TXD1 | — | — | — | — | RXD0 |
| 20 QDEC | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B | Q1_LED | Q2_A | Q2_B |

### GPIO8–GPIO15 { #alt-gpio8-15 }

| 功能 | GPIO8 | GPIO9 | GPIO10 | GPIO11 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
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

| 功能 | GPIO16 | GPIO17 | GPIO18 | GPIO19 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
|---|---|---|---|---|---|---|---|---|
| 2 Flash | — | SF_IO0 | SF_IO1 | SF_CS | SF_IO3 | SF_CLK | SF_IO2 | SF2_IO2 |
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 |
| 8 PWM | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 | CH2 | CH3 |
| 10 ADC／DAC | — | CH2 | CH8 | CH9 | CH10 | CH11 | DAC_B | DAC_A |
| 19 RMII | — | — | MDC | MDIO | RXERR | TX_EN | RX_DV | — |
| 20 QDEC | Q2_B | Q2_LED | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B | Q1_LED |

### GPIO24–GPIO31 { #alt-gpio24-31 }

| 功能 | GPIO24 | GPIO25 | GPIO26 | GPIO27 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |
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

## DVP 相機腳位 { #camera-pins }

兩塊 IPRO7AI 開發板的相機接線：

| 訊號 | IPRO7AI EVK | IPRO7AI Reef EVK |
|---|---|---|
| D0–D7 | GPIO0–7 | GPIO0–7 |
| PCLK | GPIO38 | GPIO38 |
| VSYNC | GPIO39 | GPIO39 |
| HSYNC／HREF | GPIO40 | GPIO40 |
| MCLK（`CAM_MISC` 參考時脈） | GPIO41 | GPIO22 |
| RESET | GPIO35 | GPIO34 |
| PWDN | — | GPIO35 |
| SCCB SCL／SDA（I2C0） | GPIO36／GPIO37 | GPIO36／GPIO37 |

相機腳位都在 VDDIO1 電源域（GPIO0–9、GPIO36–41）。I2C0 的角色由腳位奇偶決定：偶數為 SCL，奇數為 SDA。

## 開發板預設腳位 { #board-default-pins }

### IPRO7 EVB { #evb-default-pins }

依 `bsp/board/ipro7/ipro7_evb_board_config.h`：

| GPIO | 功能 | 訊號 | 上下拉 | 驅動強度 | 說明 |
|---|---|---|---|---|---|
| GPIO0 | JTAG（14） | TMS／TCK | 上拉 | 0 | 除錯 |
| GPIO1 | JTAG（14） | TDI／TDO | 上拉 | 0 | 除錯 |
| GPIO2 | JTAG（14） | TCK／TMS | 上拉 | 0 | 除錯 |
| GPIO11 | JTAG（14） | TDO／TDI | 上拉 | 0 | 除錯 |
| GPIO15 | GPIO（11） | 輸出 | 下拉 | 2 | 軟體控制 |
| GPIO20 | UART（7） | UART0_TXD | 上拉 | 0 | 主控台 TX |
| GPIO21 | UART（7） | UART0_RXD | 上拉 | 0 | 主控台 RX |
| GPIO28 | SDC（27） | SDC_DAT1 | 上拉 | 2 | SD 卡 |
| GPIO29 | SDC（27） | SDC_DAT0 | 上拉 | 2 | SD 卡 |
| GPIO30 | SDC（27） | SDC_CLK | 無 | 2 | SD 卡 |
| GPIO31 | SDC（27） | SDC_CMD | 上拉 | 2 | SD 卡 |
| GPIO32 | SDC（27） | SDC_DAT3 | 上拉 | 2 | SD 卡 |
| GPIO33 | SDC（27） | SDC_DAT2 | 上拉 | 2 | SD 卡 |

EVB 預設沒有佔用的 GPIO：GPIO3–10、GPIO12–19、GPIO22–27、GPIO34–41。

### IPRO7AI Reef EVK { #reef-default-pins }

依 `bsp/board/ipro7/ipro7ai_reef_board_config.h`。Reef 沒有 JTAG 接頭；相機、音訊與類比腳位由驅動在啟用時設定。

| GPIO | 功能 | 設定 | 說明 |
|---|---|---|---|
| GPIO14 | GPIO（11） | 輸出，低電位 | SD_VDD 開關（低 = 開） |
| GPIO15 | GPIO（11） | 輸入，上拉 | SD 卡偵測 |
| GPIO20 | UART（7） | 上拉 | 主控台 TX |
| GPIO21 | UART（7） | 上拉 | 主控台 RX |
| GPIO24 | GPIO（11） | 輸出，低電位 | WS2812 資料線，避免上電時 LED 誤動作 |
| GPIO25 | GPIO（11） | 輸出，下拉，擴大機關閉 | 喇叭擴大機致能 |
| GPIO28–33 | SDC（27） | 與 EVB 相同 | SD 卡／FIN 卡 |

## 腳位衝突與設計注意事項 { #pin-conflicts }

- **GPIO20／21**：Boot ROM UART 下載使用這兩支腳，保留板上的連接；應用啟動後的主控台設定由板級與應用決定。
- **GPIO0–2、GPIO11**：EVB 預設為 JTAG，產品可以釋放使用。IPRO7AI 開發板把 GPIO0–7 用作相機資料線。
- **GPIO17–22**：具 Flash（SF）功能。是否可用取決於封裝、Flash 配置與電路圖，不能只看編號判斷。
- **GPIO23–28**：與外接 Flash（SF2）共用。
- **GPIO28–33**：SD 卡與外接 Flash（SF2／SF3）互斥，由 `CONFIG_DISABLE_SDC_PINMUX` 選擇。
- **GPIO18／19**：32 kHz 晶體腳位。Reef 沒有裝晶體，可作一般 GPIO；IPRO7AI EVK 用來接 PDM 麥克風。
- **I/O 電壓**：由各 VDDIO 電源域決定。VDDIO1（GPIO0–9、GPIO36–41）在 Reef 可用 JP1 選 3.3 V 或 2.8 V，在 IPRO7AI EVK 為 2.8 V。
- **Schmitt 觸發**：每支腳可個別開啟（`GLB_GPIO_Cfg_Type` 的最後一個欄位）。

## 周邊連接指南 { #peripherals }

### I2S 音訊編解碼器 { #codec }

外部音訊編解碼器使用 I2S 第 1 組（GPIO4–7）傳輸音訊，I2C0 控制：

| IPRO7 | 功能 | 編解碼器 |
|---|---|---|
| GPIO4（功能 3，I2S0_BCLK） | 位元時脈 | BCLK |
| GPIO5（功能 3，I2S0_FS） | 框同步 | LRCLK／WS |
| GPIO6（功能 3，I2S0_DO） | 資料輸出 | DIN |
| GPIO7（功能 3，I2S0_DI） | 資料輸入 | DOUT |
| GPIO12（功能 6，I2C0_SCL） | I2C 時脈 | SCL |
| GPIO13（功能 6，I2C0_SDA） | I2C 資料 | SDA |

也可以使用其他組（0–7），每組 4 支依序為 BCLK、FS、DO、DI，見 [I2S 腳位](#i2s-pins)。

### SPI 周邊（LCD／感測器） { #spi-peripheral }

SPI0 使用第 3 組（GPIO12–15）：

| IPRO7 | 功能 | 周邊 |
|---|---|---|
| GPIO15（功能 4，SPI0_SCLK） | 時脈 | SCK |
| GPIO12（功能 4，SPI0_MOSI） | 主出從入 | SDI／MOSI |
| GPIO13（功能 4，SPI0_MISO） | 主入從出 | SDO／MISO |
| GPIO14（功能 4，SPI0_SS） | 晶片選擇 | CS# |

MOSI 與 MISO 的位置依 `pin_swap_enable` 而定，見 [SPI 腳位](#spi-pins)。

### SD 卡 { #sd-card }

SD 卡固定使用 GPIO28–33：

| IPRO7 | SD 卡 |
|---|---|
| GPIO28（功能 27，SDC_DAT1） | DAT1 |
| GPIO29（功能 27，SDC_DAT0） | DAT0 |
| GPIO30（功能 27，SDC_CLK） | CLK |
| GPIO31（功能 27，SDC_CMD） | CMD |
| GPIO32（功能 27，SDC_DAT3） | DAT3 |
| GPIO33（功能 27，SDC_DAT2） | DAT2 |

### I2C 感測器 { #i2c-sensor }

I2C0 可用任一組相鄰的偶數／奇數 GPIO（偶數為 SCL、奇數為 SDA）：

| IPRO7 | 功能 | 感測器 |
|---|---|---|
| GPIO4（功能 6，I2C0_SCL） | I2C 時脈 | SCL |
| GPIO5（功能 6，I2C0_SDA） | I2C 資料 | SDA |
| GPIO10（功能 11，GPIO） | 中斷（選用） | INT |
| 3V3 | 電源 | VDD |
| GND | 地 | GND |

I2C 匯流排需要外接上拉電阻（例如 4.7 kΩ），晶片內部上拉不足以驅動標準 I2C 匯流排。I2C1（功能 25）是獨立的第二組 I2C。

### UART 擴充 { #uart-expansion }

UART1 可以放在多數 GPIO 上，例如 GPIO14／15：

| IPRO7 | 功能 | 周邊 |
|---|---|---|
| GPIO14（功能 7，UART_SIG2） | UART1_TXD | RXD |
| GPIO15（功能 7，UART_SIG3） | UART1_RXD | TXD |

GPIO20／21 保留給 Boot ROM UART 下載與主控台，見 [UART 腳位](#uart-pins)。

### PDM 麥克風 { #pdm-mic }

PDM 麥克風經音訊 ADC（AUADC）擷取，腳位角色依奇偶：偶數為 PDM_CLK，奇數為 PDM_DATA。SDK 中的接法：

| 開發板 | CLK | DATA | 範例 |
|---|---|---|---|
| IPRO7AI Reef EVK | GPIO16 | GPIO17 | `ipro7ai_reef_demo` |
| IPRO7AI EVK | GPIO18 | GPIO19 | `ipro7ai_evk_launcher`、`ipro7ai_evk_demo` |
| IPRO7 EVB（外接模組） | GPIO0 | GPIO1 | `ipro_pdm_mic_demo` |

### 天線 { #antenna }

2.4 GHz 天線的選擇：

| 類型 | 特點 |
|---|---|
| PCB 天線 | 成本低，需保留淨空區 |
| 晶片天線 | 體積小，需要匹配電路 |
| 外接天線 | 效能最佳，需 U.FL 接頭 |

RF 輸出與天線之間使用 π 型匹配電路：RF 輸出端並聯一顆電容到地，串聯一顆電感，天線端再並聯一顆電容到地。Reef 在 π 型匹配後以 0 Ω 電阻選擇 PCB 天線或 u.FL 天線座。

## 相關文件 { #documents }

- [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)、[IPRO7AI EVK](boards/ipro7ai-evk.md#pinout)、[IPRO7 EVB](boards/ipro7-evb.md#default-pins)：各板的完整接線。
- [IPRO7](chips/ipro7.md#interfaces)：周邊介面的數量與規格。
- [電源與功耗量測](power.md)：VDDIO 電源域與各板電源架構。
- IPRO7 資料手冊與硬體設計指南（腳位定義、GPIO 腳位多工）：見[文件下載](../documents/index.md)。
