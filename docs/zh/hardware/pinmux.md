---
title: "腳位與周邊對照"
description: IPRO7 GPIO 功能選擇、UART／SPI／SDIO／I2S 腳位、替代功能表，以及 IPRO7AI Reef EVK 的預設腳位與擴充排針接線
migrate_from:
  - "hardware.html — 腳位定義、GPIO Function Select、UART／SPI／SDIO／I2S Pin Assignment、GPIO0~GPIO31 Alternate Function、周邊連接指南"
---

# 腳位與周邊對照

IPRO7 每支 GPIO 由 GLB 腳位多工器選擇功能：在 `GLB_GPIO_Cfg_Type` 填入腳位、功能值（0–27）、模式、上下拉、驅動強度與 Schmitt 觸發，再呼叫 `GLB_GPIO_Init()`。本頁的表格依 `bsp/drivers/ipro7_soc/std_drv/inc/drv_gpio.h`、`drv_glb.h` 與 Reef 的板級設定檔 `bsp/board/ipro7/ipro7ai_reef_board_config.h` 整理；板上的完整接線與 40-pin 排針見 [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)。

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

Reef 的主控台在 UART0：GPIO20（`GLB_UART_SIG_8` → TXD）與 GPIO21（`GLB_UART_SIG_9` → RXD），接到除錯排座 U6 的第 3／4 腳與 J_IO 的第 8／10 腳。GPIO20／21 也是 Boot ROM UART 下載使用的腳位。主控台鮑率由應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200。

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

```c title="UART1：GPIO2 為 TXD、GPIO3 為 RXD（Reef J_IO 第 40／38 腳，SW7＝GPIO）"
GLB_GPIO_Cfg_Type uart_pins[] = {
    { GLB_GPIO_PIN_2, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
    { GLB_GPIO_PIN_3, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
};
GLB_GPIO_Init(&uart_pins[0]);
GLB_GPIO_Init(&uart_pins[1]);

/* GPIO2 → SIG_2、GPIO3 → SIG_3（GPIO 編號 mod 12） */
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

Reef 的 WS2812 資料線在 GPIO24（mod 4 = 0），以 SPI0 MOSI 驅動，需要 `pin_swap_enable = 0`。J_IO 上的 SPI 腳位見 [Reef 擴充排針的周邊](#peripherals)。

```c title="SPI0 使用 GPIO4–7 這一組（pin_swap_enable = 0）"
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

## SDIO／SD 卡腳位 { #sdio-pins }

SD 主控（SDH，功能 27）固定使用 GPIO28–33。這組腳位也接到外接 Flash（SF2／SF3）：定義 `CONFIG_DISABLE_SDC_PINMUX` 時，GPIO28–33 改給外接 Flash，不能同時使用 SD 卡。Reef 的 microSD 卡座接在這組腳位上，插入 IPRO6S FIN 卡時，IPRO7AI 也經這組腳位以 SDIO 驅動卡片。

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

Reef 的卡片偵測在 GPIO15（卡片插入時為 0），卡座電源由 GPIO14 控制（JP3 在 GPIO 時，低準位＝有電）。CMD 與 DAT 線沒有外部上拉電阻，SDK 的板級設定開啟 IPRO7AI 的內部上拉。以 GPIO14 關閉卡座電源前，先把 GPIO28–33 設為低準位或輸入。

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

Reef 的 OV5640 相機接線（SW7 必須在 CAM）：

| 訊號 | GPIO |
|---|---|
| D0–D7 | GPIO0–7 |
| PCLK | GPIO38 |
| VSYNC | GPIO39 |
| HSYNC／HREF | GPIO40 |
| XCLK（`CAM_MISC` 參考時脈，由 IPRO7AI 輸出） | GPIO22 |
| RESETB | GPIO34 |
| PWDN | GPIO35 |
| SCCB SCL／SDA（I2C0） | GPIO36／GPIO37 |

VDDIO1 電源域涵蓋 GPIO0–9 與 GPIO36–41（相機、USB 與 BOOT 腳位）。I2C0 的角色由腳位奇偶決定：偶數為 SCL，奇數為 SDA。SW7 撥到 GPIO 時，這 16 支腳改接到 J_IO，相機的 2.8 V 與 1.5 V 穩壓器關閉。

## 開發板預設腳位 { #board-default-pins }

### IPRO7AI Reef EVK { #reef-default-pins }

依 `bsp/board/ipro7/ipro7ai_reef_board_config.h`，開機時設定下列腳位。Reef 沒有 JTAG 接頭；相機、音訊與類比腳位由驅動在啟用時設定。

| GPIO | 功能 | 設定 | 說明 |
|---|---|---|---|
| GPIO14 | GPIO（11） | 輸出，低準位 | microSD 卡座電源開關（JP3 在 GPIO 時，低準位＝有電） |
| GPIO15 | GPIO（11） | 輸入，上拉 | microSD 卡片偵測 |
| GPIO20 | UART（7） | 上拉 | 主控台 TX |
| GPIO21 | UART（7） | 上拉 | 主控台 RX |
| GPIO24 | GPIO（11） | 輸出，低準位 | WS2812 資料線，避免上電時 LED 誤動作 |
| GPIO25 | GPIO（11） | 輸出，下拉，擴大機關閉 | 喇叭擴大機致能（高準位開啟） |
| GPIO28–33 | SDC（27） | DAT 與 CMD 上拉，驅動強度 2 | microSD 卡座／FIN 卡 |

其他開發板（IPRO7 EVB、IPRO7AI EVK）的預設腳位在 `bsp/board/ipro7/` 的板級設定檔中；這些板子的供應請洽 INTELPRO。

## 腳位衝突與設計注意事項 { #pin-conflicts }

- **GPIO20／21**：Boot ROM UART 下載與主控台使用這兩支腳，保留它們與 U6 的連接。
- **GPIO0–7、GPIO22、GPIO34–40**：Reef 的相機腳位。SW7＝CAM 時由相機使用；SW7＝GPIO 時接到 J_IO，相機關閉。
- **GPIO10、GPIO11、GPIO27**：Reef 的 SW3、SW5、SW4 按鍵（按下為低準位），也引到 J_IO。
- **GPIO12、GPIO13**：Reef 的耳麥麥克風類比輸入（AIN6、AIN7）。
- **GPIO17–22**：具 Flash（SF）功能。是否可用取決於封裝、Flash 配置與電路圖，不能只看編號判斷。
- **GPIO23–28**：與外接 Flash（SF2）共用。Reef 的 GPIO23 是 GPDAC 喇叭輸出，GPIO24 是 WS2812，GPIO25 是擴大機致能，GPIO26 是耳麥插入偵測。
- **GPIO28–33**：SD 卡與外接 Flash（SF2／SF3）互斥，由 `CONFIG_DISABLE_SDC_PINMUX` 選擇；Reef 用作 microSD。
- **GPIO18／19**：32 kHz 晶體腳位。Reef 沒有裝晶體，這兩支腳是 J_IO 的 I2C（板上 4.7 kΩ 上拉）。
- **I/O 電壓**：Reef V4.0 的所有 IO 都是 3.3 V 準位，不可接 5 V 訊號。
- **Schmitt 觸發**：每支腳可個別開啟（`GLB_GPIO_Cfg_Type` 的最後一個欄位）。

## 周邊連接指南 { #peripherals }

Reef 的 40-pin 擴充排針 J_IO 位置與腳序同樹莓派。下表列出依 IPRO7 的腳位功能可以設定在 J_IO 上的介面；SDK 沒有為它們提供 Reef 的範例設定，使用前依前面各節設定腳位功能。標示 SW7＝GPIO 的介面使用相機腳位，此時相機關閉。

| 介面 | J_IO 腳位 | GPIO 與功能 | 條件 |
|---|---|---|---|
| I2C | 3 SDA、5 SCL | GPIO19、GPIO18，I2C0（功能 6） | 板上 4.7 kΩ 上拉；SW7 任一位置都可用 |
| SPI0 | 19 MOSI、21 MISO、23 SCLK、24 SS | GPIO4、GPIO5、GPIO7、GPIO6，第 1 組（功能 4） | SW7＝GPIO；`pin_swap_enable = 0` |
| I2S0 | 12 BCLK、35 FS、40 DO、38 DI | GPIO0、GPIO1、GPIO2、GPIO3，第 0 組（功能 3） | SW7＝GPIO |
| UART1 | 40 TXD、38 RXD | GPIO2（SIG_2）、GPIO3（SIG_3），功能 7 | SW7＝GPIO；與 I2S0 擇一 |
| 第二組 I2C 位置（ID EEPROM） | 27 SDA、28 SCL | GPIO37、GPIO36 | SW7＝GPIO |
| 主控台 UART0 | 8 TXD、10 RXD | GPIO20、GPIO21 | 主控台已使用 |

J_IO 的 1、17 腳是 3.3 V 電源輸出，2、4 腳是 USB 5 V 經二極體的輸出，不能由此對板子供電。完整腳位表見 [IPRO7AI Reef EVK](boards/reef-evk.md#j-io)。

### I2C 感測器 { #i2c-sensor }

| J_IO | IPRO7AI | 感測器 |
|---|---|---|
| 1 | 3.3 V | VDD |
| 3 | GPIO19（功能 6，I2C0_SDA） | SDA |
| 5 | GPIO18（功能 6，I2C0_SCL） | SCL |
| 6 | GND | GND |

板上已有 4.7 kΩ 上拉電阻，不必再外接。I2C1（功能 25）是獨立的第二組 I2C。

### SPI 周邊（LCD／感測器） { #spi-peripheral }

| J_IO | IPRO7AI | 周邊 |
|---|---|---|
| 19 | GPIO4（功能 4，SPI0_MOSI） | SDI／MOSI |
| 21 | GPIO5（功能 4，SPI0_MISO） | SDO／MISO |
| 23 | GPIO7（功能 4，SPI0_SCLK） | SCK |
| 24 | GPIO6（功能 4，SPI0_SS） | CS# |

需要 SW7＝GPIO 與 `pin_swap_enable = 0`；MOSI 與 MISO 的位置見 [SPI 腳位](#spi-pins)。

### I2S 音訊編解碼器 { #codec }

| J_IO | IPRO7AI | 編解碼器 |
|---|---|---|
| 12 | GPIO0（功能 3，I2S0_BCLK） | BCLK |
| 35 | GPIO1（功能 3，I2S0_FS） | LRCLK／WS |
| 40 | GPIO2（功能 3，I2S0_DO） | DIN |
| 38 | GPIO3（功能 3，I2S0_DI） | DOUT |

需要 SW7＝GPIO。編解碼器的控制介面接 J_IO 的 I2C（3、5 腳）。每組 4 支依序為 BCLK、FS、DO、DI，見 [I2S 腳位](#i2s-pins)。

### UART 擴充 { #uart-expansion }

UART1 可以放在多數 GPIO 上；在 J_IO 上可用 GPIO2（第 40 腳，TXD）與 GPIO3（第 38 腳，RXD），需要 SW7＝GPIO，設定方式見 [UART 腳位](#uart-pins)的範例。GPIO20／21 保留給 Boot ROM UART 下載與主控台。

### SD 卡 { #sd-card }

Reef 的 microSD 卡座固定使用 GPIO28–33，沒有引到 J_IO：

| IPRO7AI | SD 卡 |
|---|---|
| GPIO28（功能 27，SDC_DAT1） | DAT1 |
| GPIO29（功能 27，SDC_DAT0） | DAT0 |
| GPIO30（功能 27，SDC_CLK） | CLK |
| GPIO31（功能 27，SDC_CMD） | CMD |
| GPIO32（功能 27，SDC_DAT3） | DAT3 |
| GPIO33（功能 27，SDC_DAT2） | DAT2 |

### PDM 麥克風 { #pdm-mic }

PDM 麥克風經音訊 ADC（AUADC）擷取，腳位角色依奇偶：偶數為 PDM_CLK，奇數為 PDM_DATA。Reef 的板上 PDM 麥克風 MK1 接在 CLK GPIO16、DATA GPIO17，`ipro7ai_reef_demo` 的 `mic rec pdm` 以它錄音。

### 天線 { #antenna }

2.4 GHz 天線的選擇：

| 類型 | 特點 |
|---|---|
| PCB 天線 | 成本低，需保留淨空區 |
| 晶片天線 | 體積小，需要匹配電路 |
| 外接天線 | 效能最佳，需 U.FL 接頭 |

RF 輸出與天線之間使用 π 型匹配電路：RF 輸出端並聯一顆電容到地，串聯一顆電感，天線端再並聯一顆電容到地。Reef 預設使用 PCB 天線 E1；把 R2 的 0 Ω 電阻移到 R1，改接 u.FL 天線座 RF1。

## 相關文件 { #documents }

- [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)：板上接線、J_IO 與 U6 腳位表。
- [IPRO7](chips/ipro7.md#interfaces)：周邊介面的數量與規格。
- [電源與功耗量測](power.md)：Reef 的供電方式與電流量測。
- IPRO7 資料手冊與硬體設計指南（腳位定義、GPIO 腳位多工）：見[文件下載](../documents/index.md)。
