---
title: "引脚与外设对照"
description: IPRO7 GPIO 功能选择、UART／SPI／SDIO／I2S 引脚、复用功能表，以及 IPRO7AI Reef EVK 的默认引脚与扩展排针接线
migrate_from:
  - "hardware.html — 腳位定義、GPIO Function Select、UART／SPI／SDIO／I2S Pin Assignment、GPIO0~GPIO31 Alternate Function、周邊連接指南"
---

# 引脚与外设对照

IPRO7 的每个 GPIO 由 GLB 引脚复用器选择功能：在 `GLB_GPIO_Cfg_Type` 中填入引脚、功能值（0–27）、模式、上下拉、驱动强度与施密特触发，再调用 `GLB_GPIO_Init()`。本页的表格依据 `bsp/drivers/ipro7_soc/std_drv/inc/drv_gpio.h`、`drv_glb.h` 与 Reef 的板级配置文件 `bsp/board/ipro7/ipro7ai_reef_board_config.h` 整理；板上的完整接线与 40-pin 排针见 [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)。

```c title="配置一个引脚"
/* 字段顺序：{ pin, function, mode, pull, drive, smt } */
GLB_GPIO_Cfg_Type cfg = { GLB_GPIO_PIN_20, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 };
GLB_GPIO_Init(&cfg);
```

## GPIO 功能选择 { #pinout }

| 值 | 功能（`GPIO_FUN_*`） | 说明 |
|---|---|---|
| 0 | `CLK_OUT` | 时钟输出 |
| 1 | `BT_COEXIST` | 蓝牙共存信号 |
| 2 | `FLASH_PSRAM`（`QSPI`） | Flash／PSRAM／QSPI |
| 3 | `I2S` | I2S 音频 |
| 4 | `SPI` | SPI0 |
| 5 | `PDM` | PDM 数字麦克风 |
| 6 | `I2C` | I2C0 |
| 7 | `UART` | UART（经 UART signal 路由，见下节） |
| 8 | `PWM` | PWM |
| 9 | `CAM` | 摄像头 DVP |
| 10 | `ANALOG` | ADC／DAC 等模拟功能 |
| 11 | `GPIO` | 通用 IO |
| 12 | `RF_TEST` | 内部测试用 |
| 13 | `SCAN` | 内部测试用 |
| 14 | `MCU_JTAG` | JTAG 调试 |
| 15 | `DEBUG` | 调试信号 |
| 16 | `EXTERNAL_PA` | 外接 PA／LNA 控制 |
| 17 | `USB_TRANCEIVER` | USB PHY |
| 18 | `USB_CONTROLLER` | USB 控制器 |
| 19 | `ETHER_MAC`（`EMAC`） | 以太网 RMII |
| 20 | `QDEC` | 正交解码器 |
| 21 | `KEY_SCAN_IN`（`KEY_SCAN_ROW`） | 键盘扫描行输入 |
| 22 | `KEY_SCAN_DRIVE`（`KEY_SCAN_COL`） | 键盘扫描列驱动 |
| 23 | `CAM_MISC` | 摄像头 PWDN／RESET／参考时钟 |
| 24 | `PIO` | 可编程 IO |
| 25 | `I2C1` | I2C1 |
| 26 | `SPI1` | SPI1 |
| 27 | `SDC` | SD 卡（SDIO） |

## UART 引脚 { #uart-pins }

UART 采用两级复用，因此可以放在大多数 GPIO 上：

1. 把 GPIO 设为功能 7，这个引脚就成为 UART signal N，N = GPIO 编号 mod 12（`GLB_UART_SIG_0`–`GLB_UART_SIG_11`）。
2. 用 `GLB_UART_Fun_Sel()` 把该 signal 映射到 UART0／UART1 的 TXD、RXD、CTS 或 RTS。

编号除以 12 余数相同的引脚共用同一个 signal，不能同时担任不同的 UART 信号。

Reef 的控制台在 UART0：GPIO20（`GLB_UART_SIG_8` → TXD）与 GPIO21（`GLB_UART_SIG_9` → RXD），接到调试插座 U6 的第 3／4 脚与 J_IO 的第 8／10 脚。GPIO20／21 也是 Boot ROM UART 下载使用的引脚。控制台波特率由应用的 `CONFIG_PLATFORM_UART_BAUDRATE` 决定，未设置时为 115200。

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

| Signal 功能（`GLB_UART_SIG_FUN_*`） | 说明 | Signal 功能 | 说明 |
|---|---|---|---|
| `UART0_TXD` | UART0 发送 | `UART1_TXD` | UART1 发送 |
| `UART0_RXD` | UART0 接收 | `UART1_RXD` | UART1 接收 |
| `UART0_RTS` | UART0 Request To Send | `UART1_RTS` | UART1 Request To Send |
| `UART0_CTS` | UART0 Clear To Send | `UART1_CTS` | UART1 Clear To Send |

`GLB_UART_Sig_Swap_Set()` 可对 GPIO0–7、GPIO8–15、GPIO16–22 三组分别启用交换，把该组的 `uart_sig[0:3]` 与 `uart_sig[4:7]` 对调。启动代码设置为 `UART_SIG_SWAP_NONE`（不交换），上表即为此默认值。

```c title="UART1：GPIO2 为 TXD、GPIO3 为 RXD（Reef J_IO 第 40／38 脚，SW7＝GPIO）"
GLB_GPIO_Cfg_Type uart_pins[] = {
    { GLB_GPIO_PIN_2, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
    { GLB_GPIO_PIN_3, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
};
GLB_GPIO_Init(&uart_pins[0]);
GLB_GPIO_Init(&uart_pins[1]);

/* GPIO2 → SIG_2、GPIO3 → SIG_3（GPIO 编号 mod 12） */
GLB_UART_Fun_Sel(GLB_UART_SIG_2, GLB_UART_SIG_FUN_UART1_TXD);
GLB_UART_Fun_Sel(GLB_UART_SIG_3, GLB_UART_SIG_FUN_UART1_RXD);
```

## SPI 引脚 { #spi-pins }

SPI0（功能 4）以 4 个 GPIO 为一组，角色由引脚编号 mod 4 决定：0 = MOSI、1 = MISO、2 = SS、3 = SCLK（`pin_swap_enable = 0` 时）。`pin_swap_enable = 1` 会交换 MOSI 与 MISO；SDK 的默认值（`bsp/board/ipro7/peripheral_config.h`）为 1。

| 组 | MOSI（swap = 0）／MISO（swap = 1） | MISO（swap = 0）／MOSI（swap = 1） | SS | SCLK |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

SPI1（功能 26）是独立的第二组 SPI，引脚分组规则与 SPI0 相同。

| 项目 | SPI0 | SPI1 |
|---|---|---|
| 默认时钟 | 18 MHz | 18 MHz |
| 数据宽度 | 8／16／24／32 位 | 8／16／24／32 位 |
| 模式 | 主／从 | 主／从 |
| CPOL／CPHA | 可配置（默认 CPOL 低、第一个边沿采样） | 可配置 |
| 默认 DMA 通道 | TX：DMA_CH3，RX：DMA_CH4 | — |
| 引脚交换 | MOSI／MISO 可交换 | MOSI／MISO 可交换 |

Reef 的 WS2812 数据线在 GPIO24（mod 4 = 0），由 SPI0 MOSI 驱动，需要 `pin_swap_enable = 0`。J_IO 上的 SPI 引脚见 [Reef 扩展排针上的外设](#peripherals)。

```c title="SPI0 使用 GPIO4–7 这一组（pin_swap_enable = 0）"
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

## SDIO／SD 卡引脚 { #sdio-pins }

SD 主控（SDH，功能 27）固定使用 GPIO28–33。这组引脚也连接外接 Flash（SF2／SF3）：定义 `CONFIG_DISABLE_SDC_PINMUX` 时，GPIO28–33 改给外接 Flash 使用，不能同时使用 SD 卡。Reef 的 microSD 卡座接在这组引脚上，插入 IPRO6S FIN 卡时，IPRO7AI 也经这组引脚以 SDIO 驱动卡片。

| GPIO | SDC 信号 | 上下拉 | 驱动强度 | 说明 |
|---|---|---|---|---|
| GPIO28 | SDC_DAT1 | 上拉 | 2 | 数据位 1 |
| GPIO29 | SDC_DAT0 | 上拉 | 2 | 数据位 0 |
| GPIO30 | SDC_CLK | 无 | 2 | 时钟 |
| GPIO31 | SDC_CMD | 上拉 | 2 | 命令线 |
| GPIO32 | SDC_DAT3 | 上拉 | 2 | 数据位 3 |
| GPIO33 | SDC_DAT2 | 上拉 | 2 | 数据位 2 |

| 项目 | 规格 |
|---|---|
| 总线宽度 | 1-bit／4-bit |
| 时钟源 | `GLB_SDH_CLK_DLL_64M`／`GLB_SDH_CLK_PLL_96M` |
| 开发板默认 | PLL_96M，`div = 1`（48 MHz） |
| 协议 | SD 3.0／SDIO |

Reef 的卡检测在 GPIO15（插入卡片时为 0），卡座电源由 GPIO14 控制（JP3 在 GPIO 时，低电平＝有电）。CMD 与 DAT 线没有外部上拉电阻，SDK 的板级配置开启了 IPRO7AI 的内部上拉。用 GPIO14 关闭卡座电源前，先把 GPIO28–33 设为低电平或输入。

## I2S 引脚 { #i2s-pins }

I2S0（功能 3）以 4 个 GPIO 为一组，信号按位置固定。第 3 个为 DIO／DO 双功能，第 4 个为 RCLK_O／DI 双功能：全双工时 DO 输出、DI 输入；半双工时 DIO 双向传输。

| 组 | BCLK | FS（LRCLK） | DIO／DO | RCLK_O／DI |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

| 项目 | I2S0 |
|---|---|
| 模式 | 主／从 |
| 格式 | 标准 I2S、左对齐、右对齐、DSP-A、DSP-B |
| 采样率 | 8 kHz–96 kHz |
| 帧长／数据长度 | 8／16／24／32 位 |
| 声道 | 单声道、立体声；DSP 格式最多 4 声道 |
| FIFO 深度 | 8 级 |
| 默认 DMA 通道 | TX：DMA_CH5／DMA_CH6 |
| MCLK 输出 | 经 RCLK_O 引脚 |
| SDK 默认 | 主模式、左对齐、16 kHz、单声道、16 位 |

## GPIO0–GPIO31 复用功能 { #alt-functions }

只列出与外设设计相关的功能；每个 GPIO 也都有 GPIO（11）、JTAG（14）与 DEBUG（15）功能，此处省略。全部为“—”的行不列出。

- MOSI\*／MISO\*：随 `pin_swap_enable` 交换。
- UART 行中的 Sn 表示 UART signal n（默认不交换）。
- QDEC 行：Qn_A／Qn_B 为 QDECn 的 A／B 相，Qn_LED 为 QDECn 的 LED 驱动。
- ADC 行中的 CHn 为 GPADC 通道；DAC_A／DAC_B 为 GPDAC 两个通道的输出。
- PWM 行的 CH0–CH4 是 GPIO 功能定义（`drv_gpio.h`）中的信号名称；PWM 驱动（`drv_pwm.h`）只提供 CH0–CH3，连接到 CH4 的引脚没有驱动可用。

### GPIO0–GPIO7 { #alt-gpio0-7 }

| 功能 | GPIO0 | GPIO1 | GPIO2 | GPIO3 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
|---|---|---|---|---|---|---|---|---|
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
| 8 PWM | CH0 | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 | CH2 |
| 10 ADC／DAC | — | — | — | — | — | — | — | CH6／DAC 外部参考 |
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

## DVP 摄像头引脚 { #camera-pins }

Reef 的 OV5640 摄像头接线（SW7 必须在 CAM）：

| 信号 | GPIO |
|---|---|
| D0–D7 | GPIO0–7 |
| PCLK | GPIO38 |
| VSYNC | GPIO39 |
| HSYNC／HREF | GPIO40 |
| XCLK（`CAM_MISC` 参考时钟，由 IPRO7AI 输出） | GPIO22 |
| RESETB | GPIO34 |
| PWDN | GPIO35 |
| SCCB SCL／SDA（I2C0） | GPIO36／GPIO37 |

VDDIO1 电源域涵盖 GPIO0–9 与 GPIO36–41（摄像头、USB 与 BOOT 引脚）。I2C0 的角色由引脚编号的奇偶决定：偶数为 SCL，奇数为 SDA。SW7 拨到 GPIO 时，这 16 个引脚改接到 J_IO，摄像头的 2.8 V 与 1.5 V 稳压器关闭。

## 开发板默认引脚 { #board-default-pins }

### IPRO7AI Reef EVK { #reef-default-pins }

依据 `bsp/board/ipro7/ipro7ai_reef_board_config.h`，启动时配置下列引脚。Reef 没有 JTAG 接口；摄像头、音频与模拟引脚由驱动在启用时配置。

| GPIO | 功能 | 设置 | 说明 |
|---|---|---|---|
| GPIO14 | GPIO（11） | 输出，低电平 | microSD 卡座电源开关（JP3 在 GPIO 时，低电平＝有电） |
| GPIO15 | GPIO（11） | 输入，上拉 | microSD 卡检测 |
| GPIO20 | UART（7） | 上拉 | 控制台 TX |
| GPIO21 | UART（7） | 上拉 | 控制台 RX |
| GPIO24 | GPIO（11） | 输出，低电平 | WS2812 数据线，避免上电时 LED 误动作 |
| GPIO25 | GPIO（11） | 输出，下拉，功放关闭 | 扬声器功放使能（高电平开启） |
| GPIO28–33 | SDC（27） | DAT 与 CMD 上拉，驱动强度 2 | microSD 卡座／FIN 卡 |

其他开发板（IPRO7 EVB、IPRO7AI EVK）的默认引脚在 `bsp/board/ipro7/` 下的板级配置文件中；这些开发板的供货请联系 INTELPRO。

## 引脚冲突与设计注意事项 { #pin-conflicts }

- **GPIO20／21**：Boot ROM UART 下载与控制台使用这两个引脚，请保留它们与 U6 的连接。
- **GPIO0–7、GPIO22、GPIO34–40**：Reef 的摄像头引脚。SW7＝CAM 时由摄像头使用；SW7＝GPIO 时接到 J_IO，摄像头关闭。
- **GPIO10、GPIO11、GPIO27**：Reef 的 SW3、SW5、SW4 按键（按下为低电平），也引出到 J_IO。
- **GPIO12、GPIO13**：Reef 的耳麦麦克风模拟输入（AIN6、AIN7）。
- **GPIO17–22**：具有 Flash（SF）功能。是否可用取决于封装、Flash 配置与原理图，不能只凭编号判断。
- **GPIO23–28**：与外接 Flash（SF2）共用。Reef 的 GPIO23 是 GPDAC 扬声器输出，GPIO24 是 WS2812，GPIO25 是功放使能，GPIO26 是耳麦插入检测。
- **GPIO28–33**：SD 卡与外接 Flash（SF2／SF3）互斥，由 `CONFIG_DISABLE_SDC_PINMUX` 选择；Reef 用作 microSD。
- **GPIO18／19**：32 kHz 晶振引脚。Reef 没有安装晶振，这两个引脚是 J_IO 的 I2C（板上 4.7 kΩ 上拉）。
- **I/O 电压**：Reef V4.0 的所有 IO 都是 3.3 V 电平，不可接 5 V 信号。
- **施密特触发**：每个引脚可单独开启（`GLB_GPIO_Cfg_Type` 的最后一个字段）。

## 外设连接指南 { #peripherals }

Reef 的 40-pin 扩展排针 J_IO 位置与引脚排列同树莓派。下表列出按 IPRO7 的引脚功能可以配置在 J_IO 上的接口；SDK 没有为它们提供 Reef 的示例配置，使用前按前面各节配置引脚功能。标注 SW7＝GPIO 的接口使用摄像头引脚，此时摄像头关闭。

| 接口 | J_IO 引脚 | GPIO 与功能 | 条件 |
|---|---|---|---|
| I2C | 3 SDA、5 SCL | GPIO19、GPIO18，I2C0（功能 6） | 板上 4.7 kΩ 上拉；SW7 在任一位置都可用 |
| SPI0 | 19 MOSI、21 MISO、23 SCLK、24 SS | GPIO4、GPIO5、GPIO7、GPIO6，第 1 组（功能 4） | SW7＝GPIO；`pin_swap_enable = 0` |
| I2S0 | 12 BCLK、35 FS、40 DO、38 DI | GPIO0、GPIO1、GPIO2、GPIO3，第 0 组（功能 3） | SW7＝GPIO |
| UART1 | 40 TXD、38 RXD | GPIO2（SIG_2）、GPIO3（SIG_3），功能 7 | SW7＝GPIO；与 I2S0 二选一 |
| 第二组 I2C 位置（ID EEPROM） | 27 SDA、28 SCL | GPIO37、GPIO36 | SW7＝GPIO |
| 控制台 UART0 | 8 TXD、10 RXD | GPIO20、GPIO21 | 已被控制台占用 |

J_IO 的 1、17 脚是 3.3 V 电源输出，2、4 脚是 USB 5 V 经二极管的输出，不能从这里给开发板供电。完整引脚表见 [IPRO7AI Reef EVK](boards/reef-evk.md#j-io)。

### I2C 传感器 { #i2c-sensor }

| J_IO | IPRO7AI | 传感器 |
|---|---|---|
| 1 | 3.3 V | VDD |
| 3 | GPIO19（功能 6，I2C0_SDA） | SDA |
| 5 | GPIO18（功能 6，I2C0_SCL） | SCL |
| 6 | GND | GND |

板上已有 4.7 kΩ 上拉电阻，无需再外接。I2C1（功能 25）是独立的第二组 I2C。

### SPI 外设（LCD／传感器） { #spi-peripheral }

| J_IO | IPRO7AI | 外设 |
|---|---|---|
| 19 | GPIO4（功能 4，SPI0_MOSI） | SDI／MOSI |
| 21 | GPIO5（功能 4，SPI0_MISO） | SDO／MISO |
| 23 | GPIO7（功能 4，SPI0_SCLK） | SCK |
| 24 | GPIO6（功能 4，SPI0_SS） | CS# |

需要 SW7＝GPIO 与 `pin_swap_enable = 0`；MOSI 与 MISO 的位置见 [SPI 引脚](#spi-pins)。

### I2S 音频编解码器 { #codec }

| J_IO | IPRO7AI | 编解码器 |
|---|---|---|
| 12 | GPIO0（功能 3，I2S0_BCLK） | BCLK |
| 35 | GPIO1（功能 3，I2S0_FS） | LRCLK／WS |
| 40 | GPIO2（功能 3，I2S0_DO） | DIN |
| 38 | GPIO3（功能 3，I2S0_DI） | DOUT |

需要 SW7＝GPIO。编解码器的控制接口接 J_IO 的 I2C（3、5 脚）。每组 4 个引脚依次为 BCLK、FS、DO、DI，见 [I2S 引脚](#i2s-pins)。

### UART 扩展 { #uart-expansion }

UART1 可以放在大多数 GPIO 上；在 J_IO 上可用 GPIO2（第 40 脚，TXD）与 GPIO3（第 38 脚，RXD），需要 SW7＝GPIO，配置方法见 [UART 引脚](#uart-pins)中的示例。GPIO20／21 保留给 Boot ROM UART 下载与控制台。

### SD 卡 { #sd-card }

Reef 的 microSD 卡座固定使用 GPIO28–33，没有引出到 J_IO：

| IPRO7AI | SD 卡 |
|---|---|
| GPIO28（功能 27，SDC_DAT1） | DAT1 |
| GPIO29（功能 27，SDC_DAT0） | DAT0 |
| GPIO30（功能 27，SDC_CLK） | CLK |
| GPIO31（功能 27，SDC_CMD） | CMD |
| GPIO32（功能 27，SDC_DAT3） | DAT3 |
| GPIO33（功能 27，SDC_DAT2） | DAT2 |

### PDM 麦克风 { #pdm-mic }

PDM 麦克风经音频 ADC（AUADC）采集，引脚角色按奇偶区分：偶数为 PDM_CLK，奇数为 PDM_DATA。Reef 的板载 PDM 麦克风 MK1 接在 CLK GPIO16、DATA GPIO17，`ipro7ai_reef_demo` 的 `mic rec pdm` 用它录音。

### 天线 { #antenna }

2.4 GHz 天线的选择：

| 类型 | 特点 |
|---|---|
| PCB 天线 | 成本低，需保留净空区 |
| 芯片天线 | 体积小，需要匹配电路 |
| 外接天线 | 性能最佳，需 U.FL 接头 |

RF 输出与天线之间使用 π 型匹配电路：RF 输出端并联一颗电容到地，串联一颗电感，天线端再并联一颗电容到地。Reef 默认使用 PCB 天线 E1；把 R2 的 0 Ω 电阻移到 R1，改接 u.FL 天线座 RF1。

## 相关文档 { #documents }

- [IPRO7AI Reef EVK](boards/reef-evk.md#pinout)：板上接线、J_IO 与 U6 引脚表。
- [IPRO7](chips/ipro7.md#interfaces)：外设接口的数量与规格。
- [电源与功耗测量](power.md)：Reef 的供电方式与电流测量。
- IPRO7 数据手册与硬件设计指南（引脚定义、GPIO 引脚复用）：见[文档下载](../documents/index.md)。
