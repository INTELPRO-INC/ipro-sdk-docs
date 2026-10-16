---
title: "Pinout & Peripheral Mapping"
description: IPRO7 GPIO function select, UART / SPI / SDIO / I2S pins, alternate-function tables, board default pins and peripheral wiring examples
migrate_from:
  - "hardware.html — 腳位定義、GPIO Function Select、UART／SPI／SDIO／I2S Pin Assignment、GPIO0~GPIO31 Alternate Function、周邊連接指南"
---

# Pinout & Peripheral Mapping

Each IPRO7 GPIO gets its role from the GLB pin multiplexer: fill a `GLB_GPIO_Cfg_Type` with the pin, a function value (0–27), the mode, pull, drive strength and Schmitt trigger, then call `GLB_GPIO_Init()`. The tables on this page come from `bsp/drivers/ipro7_soc/std_drv/inc/drv_gpio.h`, `drv_glb.h` and the board configuration headers; for the full wiring of each board see [IPRO7AI Reef EVK](boards/reef-evk.md#pinout), [IPRO7AI EVK](boards/ipro7ai-evk.md#pinout) and [IPRO7 EVB](boards/ipro7-evb.md#default-pins).

```c title="Configure one pin"
/* field order: { pin, function, mode, pull, drive, smt } */
GLB_GPIO_Cfg_Type cfg = { GLB_GPIO_PIN_20, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 };
GLB_GPIO_Init(&cfg);
```

## GPIO function select { #pinout }

| Value | Function (`GPIO_FUN_*`) | Description |
|---|---|---|
| 0 | `CLK_OUT` | Clock output |
| 1 | `BT_COEXIST` | Bluetooth coexistence signals |
| 2 | `FLASH_PSRAM` (`QSPI`) | Flash / PSRAM / QSPI |
| 3 | `I2S` | I2S audio |
| 4 | `SPI` | SPI0 |
| 5 | `PDM` | PDM digital microphone |
| 6 | `I2C` | I2C0 |
| 7 | `UART` | UART (routed through UART signals, see below) |
| 8 | `PWM` | PWM |
| 9 | `CAM` | Camera DVP |
| 10 | `ANALOG` | ADC / DAC and other analog functions |
| 11 | `GPIO` | General-purpose IO |
| 12 | `RF_TEST` | Internal test |
| 13 | `SCAN` | Internal test |
| 14 | `MCU_JTAG` | JTAG debug |
| 15 | `DEBUG` | Debug signals |
| 16 | `EXTERNAL_PA` | External PA / LNA control |
| 17 | `USB_TRANCEIVER` | USB PHY |
| 18 | `USB_CONTROLLER` | USB controller |
| 19 | `ETHER_MAC` (`EMAC`) | Ethernet RMII |
| 20 | `QDEC` | Quadrature decoder |
| 21 | `KEY_SCAN_IN` (`KEY_SCAN_ROW`) | Key scan row input |
| 22 | `KEY_SCAN_DRIVE` (`KEY_SCAN_COL`) | Key scan column drive |
| 23 | `CAM_MISC` | Camera PWDN / RESET / reference clock |
| 24 | `PIO` | Programmable IO |
| 25 | `I2C1` | I2C1 |
| 26 | `SPI1` | SPI1 |
| 27 | `SDC` | SD card (SDIO) |

## UART pins { #uart-pins }

UART uses a two-stage multiplexer, so it can sit on most GPIOs:

1. Set the GPIO to function 7. The pin becomes UART signal N, where N = GPIO number mod 12 (`GLB_UART_SIG_0`–`GLB_UART_SIG_11`).
2. Map that signal to TXD, RXD, CTS or RTS of UART0 / UART1 with `GLB_UART_Fun_Sel()`.

Pins whose numbers leave the same remainder modulo 12 share one signal and cannot carry different UART signals at the same time.

All three boards have the console on UART0: GPIO20 (`GLB_UART_SIG_8` → TXD) and GPIO21 (`GLB_UART_SIG_9` → RXD). GPIO20 / 21 are also the Boot ROM's UART download pins. The console baud rate comes from the application's `CONFIG_PLATFORM_UART_BAUDRATE`, 115200 when unset.

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

| Signal function (`GLB_UART_SIG_FUN_*`) | Description | Signal function | Description |
|---|---|---|---|
| `UART0_TXD` | UART0 transmit | `UART1_TXD` | UART1 transmit |
| `UART0_RXD` | UART0 receive | `UART1_RXD` | UART1 receive |
| `UART0_RTS` | UART0 Request To Send | `UART1_RTS` | UART1 Request To Send |
| `UART0_CTS` | UART0 Clear To Send | `UART1_CTS` | UART1 Clear To Send |

`GLB_UART_Sig_Swap_Set()` can enable a swap separately for the groups GPIO0–7, GPIO8–15 and GPIO16–22; it exchanges `uart_sig[0:3]` and `uart_sig[4:7]` within the group. The startup code sets `UART_SIG_SWAP_NONE` (no swap), which is what the table shows.

```c title="UART1: TXD on GPIO14, RXD on GPIO15"
GLB_GPIO_Cfg_Type uart_pins[] = {
    { GLB_GPIO_PIN_14, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
    { GLB_GPIO_PIN_15, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
};
GLB_GPIO_Init(&uart_pins[0]);
GLB_GPIO_Init(&uart_pins[1]);

/* GPIO14 -> SIG_2, GPIO15 -> SIG_3 (GPIO number mod 12) */
GLB_UART_Fun_Sel(GLB_UART_SIG_2, GLB_UART_SIG_FUN_UART1_TXD);
GLB_UART_Fun_Sel(GLB_UART_SIG_3, GLB_UART_SIG_FUN_UART1_RXD);
```

## SPI pins { #spi-pins }

SPI0 (function 4) works in groups of four GPIOs, and the role follows the pin number mod 4: 0 = MOSI, 1 = MISO, 2 = SS, 3 = SCLK (with `pin_swap_enable = 0`). `pin_swap_enable = 1` swaps MOSI and MISO; the SDK default (`bsp/board/ipro7/peripheral_config.h`) is 1.

| Group | MOSI (swap = 0) / MISO (swap = 1) | MISO (swap = 0) / MOSI (swap = 1) | SS | SCLK |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

SPI1 (function 26) is a separate second SPI with the same grouping rule.

| Item | SPI0 | SPI1 |
|---|---|---|
| Default clock | 18 MHz | 18 MHz |
| Data width | 8 / 16 / 24 / 32 bit | 8 / 16 / 24 / 32 bit |
| Mode | Master / slave | Master / slave |
| CPOL / CPHA | Configurable (default: CPOL low, sample on the first edge) | Configurable |
| Default DMA channels | TX: DMA_CH3, RX: DMA_CH4 | — |
| Pin swap | MOSI / MISO swappable | MOSI / MISO swappable |

On the boards: the Reef's WS2812 data line is on GPIO24 (mod 4 = 0) and is driven from SPI0 MOSI, which needs `pin_swap_enable = 0`; the IPRO7AI EVK's LCD uses GPIO15 (SCLK) and GPIO16 (MOSI), with CS, DC and RST as plain GPIOs.

```c title="SPI0 on the GPIO12–15 group"
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

## SDIO / SD card pins { #sdio-pins }

The SD host (SDH, function 27) always uses GPIO28–33. The same pins also reach the external flash (SF2 / SF3): with `CONFIG_DISABLE_SDC_PINMUX` defined, GPIO28–33 go to the external flash and the SD card cannot be used. An IPRO6S Wi-Fi companion connected over SDIO uses these pins too.

| GPIO | SDC signal | Pull | Drive | Description |
|---|---|---|---|---|
| GPIO28 | SDC_DAT1 | Pull-up | 2 | Data bit 1 |
| GPIO29 | SDC_DAT0 | Pull-up | 2 | Data bit 0 |
| GPIO30 | SDC_CLK | None | 2 | Clock |
| GPIO31 | SDC_CMD | Pull-up | 2 | Command line |
| GPIO32 | SDC_DAT3 | Pull-up | 2 | Data bit 3 |
| GPIO33 | SDC_DAT2 | Pull-up | 2 | Data bit 2 |

| Item | Specification |
|---|---|
| Bus width | 1-bit / 4-bit |
| Clock source | `GLB_SDH_CLK_DLL_64M` / `GLB_SDH_CLK_PLL_96M` |
| Board default | PLL_96M, `div = 1` (48 MHz) |
| Protocol | SD 3.0 / SDIO |

Card detect and the slot supply switch are board-specific: detect on GPIO15 and supply on GPIO14 on the Reef; supply on GPIO27 and detect on GPIO34 on the IPRO7AI EVK.

## I2S pins { #i2s-pins }

I2S0 (function 3) works in groups of four GPIOs with fixed positions. The third pin is DIO / DO and the fourth is RCLK_O / DI: in full duplex DO is the output and DI the input; in half duplex DIO carries data both ways.

| Group | BCLK | FS (LRCLK) | DIO / DO | RCLK_O / DI |
|---|---|---|---|---|
| 0 | GPIO0 | GPIO1 | GPIO2 | GPIO3 |
| 1 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
| 2 | GPIO8 | GPIO9 | GPIO10 | GPIO11 |
| 3 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
| 4 | GPIO16 | GPIO17 | GPIO18 | GPIO19 |
| 5 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
| 6 | GPIO24 | GPIO25 | GPIO26 | GPIO27 |
| 7 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |

| Item | I2S0 |
|---|---|
| Mode | Master / slave |
| Format | Standard I2S, left-justified, right-justified, DSP-A, DSP-B |
| Sample rate | 8 kHz–96 kHz |
| Frame / data size | 8 / 16 / 24 / 32 bit |
| Channels | Mono, stereo; up to 4 channels in DSP formats |
| FIFO depth | 8 entries |
| Default DMA channels | TX: DMA_CH5 / DMA_CH6 |
| MCLK output | On the RCLK_O pin |
| SDK default | Master, left-justified, 16 kHz, mono, 16-bit |

## GPIO0–GPIO31 alternate functions { #alt-functions }

Only functions that matter for peripheral design are listed; every GPIO also has GPIO (11), JTAG (14) and DEBUG (15). Rows that are all "—" are left out.

- MOSI\* / MISO\*: swapped by `pin_swap_enable`.
- Sn in the UART row is UART signal n (no swap).
- QDEC row: Qn_A / Qn_B are the A / B phases of QDECn, Qn_LED is its LED drive.
- CHn in the ADC row is a GPADC channel; DAC_A / DAC_B are the two GPDAC outputs.
- The PWM driver (`drv_pwm.h`) provides CH0–CH3.

### GPIO0–GPIO7 { #alt-gpio0-7 }

| Function | GPIO0 | GPIO1 | GPIO2 | GPIO3 | GPIO4 | GPIO5 | GPIO6 | GPIO7 |
|---|---|---|---|---|---|---|---|---|
| 3 I2S | BCLK | FS | DIO/DO | RCLK/DI | BCLK | FS | DIO/DO | RCLK/DI |
| 4 SPI0 | MOSI\* | MISO\* | SS | SCLK | MOSI\* | MISO\* | SS | SCLK |
| 6 I2C0 | SCL | SDA | SCL | SDA | SCL | SDA | SCL | SDA |
| 7 UART | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 |
| 8 PWM | CH0 | CH1 | CH2 | CH3 | CH4 | CH0 | CH1 | CH2 |
| 10 ADC / DAC | — | — | — | — | — | — | — | CH6 / DAC external reference |
| 19 RMII | REF_CLK | TXD0 | TXD1 | — | — | — | — | RXD0 |
| 20 QDEC | Q0_A | Q0_B | Q0_LED | Q1_A | Q1_B | Q1_LED | Q2_A | Q2_B |

### GPIO8–GPIO15 { #alt-gpio8-15 }

| Function | GPIO8 | GPIO9 | GPIO10 | GPIO11 | GPIO12 | GPIO13 | GPIO14 | GPIO15 |
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

| Function | GPIO16 | GPIO17 | GPIO18 | GPIO19 | GPIO20 | GPIO21 | GPIO22 | GPIO23 |
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

| Function | GPIO24 | GPIO25 | GPIO26 | GPIO27 | GPIO28 | GPIO29 | GPIO30 | GPIO31 |
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

## DVP camera pins { #camera-pins }

Camera wiring on the two IPRO7AI boards:

| Signal | IPRO7AI EVK | IPRO7AI Reef EVK |
|---|---|---|
| D0–D7 | GPIO0–7 | GPIO0–7 |
| PCLK | GPIO38 | GPIO38 |
| VSYNC | GPIO39 | GPIO39 |
| HSYNC / HREF | GPIO40 | GPIO40 |
| MCLK (`CAM_MISC` reference clock) | GPIO41 | GPIO22 |
| RESET | GPIO35 | GPIO34 |
| PWDN | — | GPIO35 |
| SCCB SCL / SDA (I2C0) | GPIO36 / GPIO37 | GPIO36 / GPIO37 |

All camera pins are in the VDDIO1 bank (GPIO0–9, GPIO36–41). I2C0 roles follow pin parity: even pins are SCL, odd pins SDA.

## Board default pins { #board-default-pins }

### IPRO7 EVB { #evb-default-pins }

From `bsp/board/ipro7/ipro7_evb_board_config.h`:

| GPIO | Function | Signal | Pull | Drive | Notes |
|---|---|---|---|---|---|
| GPIO0 | JTAG (14) | TMS / TCK | Pull-up | 0 | Debug |
| GPIO1 | JTAG (14) | TDI / TDO | Pull-up | 0 | Debug |
| GPIO2 | JTAG (14) | TCK / TMS | Pull-up | 0 | Debug |
| GPIO11 | JTAG (14) | TDO / TDI | Pull-up | 0 | Debug |
| GPIO15 | GPIO (11) | Output | Pull-down | 2 | Software controlled |
| GPIO20 | UART (7) | UART0_TXD | Pull-up | 0 | Console TX |
| GPIO21 | UART (7) | UART0_RXD | Pull-up | 0 | Console RX |
| GPIO28 | SDC (27) | SDC_DAT1 | Pull-up | 2 | SD card |
| GPIO29 | SDC (27) | SDC_DAT0 | Pull-up | 2 | SD card |
| GPIO30 | SDC (27) | SDC_CLK | None | 2 | SD card |
| GPIO31 | SDC (27) | SDC_CMD | Pull-up | 2 | SD card |
| GPIO32 | SDC (27) | SDC_DAT3 | Pull-up | 2 | SD card |
| GPIO33 | SDC (27) | SDC_DAT2 | Pull-up | 2 | SD card |

GPIOs the EVB leaves free by default: GPIO3–10, GPIO12–19, GPIO22–27, GPIO34–41.

### IPRO7AI Reef EVK { #reef-default-pins }

From `bsp/board/ipro7/ipro7ai_reef_board_config.h`. The Reef has no JTAG header; camera, audio and analog pins are set up by their drivers when the peripheral starts.

| GPIO | Function | Setting | Notes |
|---|---|---|---|
| GPIO14 | GPIO (11) | Output, low | SD_VDD switch (low = on) |
| GPIO15 | GPIO (11) | Input, pull-up | SD card detect |
| GPIO20 | UART (7) | Pull-up | Console TX |
| GPIO21 | UART (7) | Pull-up | Console RX |
| GPIO24 | GPIO (11) | Output, low | WS2812 data line, held low so the LED does not latch noise at power-up |
| GPIO25 | GPIO (11) | Output, pull-down, amplifier off | Speaker amplifier enable |
| GPIO28–33 | SDC (27) | As on the EVB | SD card / FIN card |

## Pin conflicts and design notes { #pin-conflicts }

- **GPIO20 / 21**: the Boot ROM downloads over these pins; keep their board connection. The console after boot is set by the board and the application.
- **GPIO0–2, GPIO11**: JTAG by default on the EVB; a product can free them. The IPRO7AI boards use GPIO0–7 as camera data lines.
- **GPIO17–22**: have flash (SF) functions. Whether you can use them depends on the package, the flash configuration and the schematic, not on the pin number alone.
- **GPIO23–28**: shared with the external flash (SF2).
- **GPIO28–33**: the SD card and the external flash (SF2 / SF3) exclude each other; `CONFIG_DISABLE_SDC_PINMUX` selects which.
- **GPIO18 / 19**: the 32 kHz crystal pads. The Reef fits no crystal, so they are free GPIOs; the IPRO7AI EVK uses them for the PDM microphone.
- **I/O voltage**: set by each VDDIO bank. VDDIO1 (GPIO0–9, GPIO36–41) is 3.3 V or 2.8 V on the Reef (JP1) and 2.8 V on the IPRO7AI EVK.
- **Schmitt trigger**: can be enabled per pin (the last field of `GLB_GPIO_Cfg_Type`).

## Peripheral connection guide { #peripherals }

### I2S audio codec { #codec }

An external audio codec takes audio over I2S group 1 (GPIO4–7) and control over I2C0:

| IPRO7 | Function | Codec |
|---|---|---|
| GPIO4 (function 3, I2S0_BCLK) | Bit clock | BCLK |
| GPIO5 (function 3, I2S0_FS) | Frame sync | LRCLK / WS |
| GPIO6 (function 3, I2S0_DO) | Data out | DIN |
| GPIO7 (function 3, I2S0_DI) | Data in | DOUT |
| GPIO12 (function 6, I2C0_SCL) | I2C clock | SCL |
| GPIO13 (function 6, I2C0_SDA) | I2C data | SDA |

Any other group (0–7) works too; each group's four pins are BCLK, FS, DO and DI in order, see [I2S pins](#i2s-pins).

### SPI peripheral (LCD / sensor) { #spi-peripheral }

SPI0 on group 3 (GPIO12–15):

| IPRO7 | Function | Peripheral |
|---|---|---|
| GPIO15 (function 4, SPI0_SCLK) | Clock | SCK |
| GPIO12 (function 4, SPI0_MOSI) | Master out, slave in | SDI / MOSI |
| GPIO13 (function 4, SPI0_MISO) | Master in, slave out | SDO / MISO |
| GPIO14 (function 4, SPI0_SS) | Chip select | CS# |

Which pin is MOSI and which is MISO depends on `pin_swap_enable`, see [SPI pins](#spi-pins).

### SD card { #sd-card }

The SD card always uses GPIO28–33:

| IPRO7 | SD card |
|---|---|
| GPIO28 (function 27, SDC_DAT1) | DAT1 |
| GPIO29 (function 27, SDC_DAT0) | DAT0 |
| GPIO30 (function 27, SDC_CLK) | CLK |
| GPIO31 (function 27, SDC_CMD) | CMD |
| GPIO32 (function 27, SDC_DAT3) | DAT3 |
| GPIO33 (function 27, SDC_DAT2) | DAT2 |

### I2C sensor { #i2c-sensor }

I2C0 works on any adjacent even / odd GPIO pair (even = SCL, odd = SDA):

| IPRO7 | Function | Sensor |
|---|---|---|
| GPIO4 (function 6, I2C0_SCL) | I2C clock | SCL |
| GPIO5 (function 6, I2C0_SDA) | I2C data | SDA |
| GPIO10 (function 11, GPIO) | Interrupt (optional) | INT |
| 3V3 | Power | VDD |
| GND | Ground | GND |

The I2C bus needs external pull-up resistors (4.7 kΩ, for example); the chip's internal pull-ups are too weak for a standard I2C bus. I2C1 (function 25) is a separate second I2C.

### UART expansion { #uart-expansion }

UART1 can sit on most GPIOs, for example GPIO14 / 15:

| IPRO7 | Function | Peripheral |
|---|---|---|
| GPIO14 (function 7, UART_SIG2) | UART1_TXD | RXD |
| GPIO15 (function 7, UART_SIG3) | UART1_RXD | TXD |

GPIO20 / 21 stay reserved for Boot ROM download and the console, see [UART pins](#uart-pins).

### PDM microphone { #pdm-mic }

A PDM microphone is captured through the audio ADC (AUADC), and the pin role follows parity: even pins are PDM_CLK, odd pins PDM_DATA. Wiring used in the SDK:

| Board | CLK | DATA | Example |
|---|---|---|---|
| IPRO7AI Reef EVK | GPIO16 | GPIO17 | `ipro7ai_reef_demo` |
| IPRO7AI EVK | GPIO18 | GPIO19 | `ipro7ai_evk_launcher`, `ipro7ai_evk_demo` |
| IPRO7 EVB (external module) | GPIO0 | GPIO1 | `ipro_pdm_mic_demo` |

### Antenna { #antenna }

Choosing a 2.4 GHz antenna:

| Type | Characteristics |
|---|---|
| PCB antenna | Low cost; needs a keep-out area |
| Chip antenna | Small; needs a matching network |
| External antenna | Best performance; needs a U.FL connector |

Put a π matching network between the RF output and the antenna: a shunt capacitor to ground at the RF side, a series inductor, and another shunt capacitor to ground at the antenna side. The Reef follows the π network with a 0 Ω resistor that selects either the PCB antenna or the u.FL connector.

## Related documents { #documents }

- [IPRO7AI Reef EVK](boards/reef-evk.md#pinout), [IPRO7AI EVK](boards/ipro7ai-evk.md#pinout), [IPRO7 EVB](boards/ipro7-evb.md#default-pins): the full wiring of each board.
- [IPRO7](chips/ipro7.md#interfaces): peripheral counts and specifications.
- [Power & Current Measurement](power.md): VDDIO power domains and the power tree of each board.
- IPRO7 datasheet and hardware design guide (pin definitions, GPIO multiplexing): see [Documents](../documents/index.md).
