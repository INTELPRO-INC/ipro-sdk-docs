---
title: "Pinout & Peripheral Mapping"
description: IPRO7 GPIO function select, UART / SPI / SDIO / I2S pins, alternate-function tables, and the IPRO7AI Reef EVK's default pins and expansion-header wiring
migrate_from:
  - "hardware.html — 腳位定義、GPIO Function Select、UART／SPI／SDIO／I2S Pin Assignment、GPIO0~GPIO31 Alternate Function、周邊連接指南"
---

# Pinout & Peripheral Mapping

Each IPRO7 GPIO gets its role from the GLB pin multiplexer: fill a `GLB_GPIO_Cfg_Type` with the pin, a function value (0–27), the mode, pull, drive strength and Schmitt trigger, then call `GLB_GPIO_Init()`. The tables on this page come from `bsp/drivers/ipro7_soc/std_drv/inc/drv_gpio.h`, `drv_glb.h` and the Reef's board configuration header `bsp/board/ipro7/ipro7ai_reef_board_config.h`; for the board's full wiring and its 40-pin header see [IPRO7AI Reef EVK](boards/reef-evk.md#pinout).

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

The Reef's console is on UART0: GPIO20 (`GLB_UART_SIG_8` → TXD) and GPIO21 (`GLB_UART_SIG_9` → RXD), wired to pins 3 / 4 of the U6 debug connector and pins 8 / 10 of J_IO. GPIO20 / 21 are also the Boot ROM's UART download pins. The console baud rate comes from the application's `CONFIG_PLATFORM_UART_BAUDRATE`, 115200 when unset.

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

```c title="UART1: TXD on GPIO2, RXD on GPIO3 (Reef J_IO pins 40 / 38, SW7 on GPIO)"
GLB_GPIO_Cfg_Type uart_pins[] = {
    { GLB_GPIO_PIN_2, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
    { GLB_GPIO_PIN_3, GPIO_FUN_UART, GPIO_MODE_AF, GPIO_PULL_UP, 0, 1 },
};
GLB_GPIO_Init(&uart_pins[0]);
GLB_GPIO_Init(&uart_pins[1]);

/* GPIO2 -> SIG_2, GPIO3 -> SIG_3 (GPIO number mod 12) */
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

The Reef's WS2812 data line is on GPIO24 (mod 4 = 0) and is driven from SPI0 MOSI, which needs `pin_swap_enable = 0`. For SPI on J_IO see [Peripherals on the Reef's expansion header](#peripherals).

```c title="SPI0 on the GPIO4–7 group (pin_swap_enable = 0)"
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

## SDIO / SD card pins { #sdio-pins }

The SD host (SDH, function 27) always uses GPIO28–33. The same pins also reach the external flash (SF2 / SF3): with `CONFIG_DISABLE_SDC_PINMUX` defined, GPIO28–33 go to the external flash and the SD card cannot be used. The Reef's microSD slot is wired to these pins; with the IPRO6S FIN card in the slot, the IPRO7AI drives the card over SDIO on the same pins.

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

On the Reef, card detect is GPIO15 (0 when a card is seated) and GPIO14 switches the slot's supply (with JP3 on GPIO, low = on). CMD and DAT have no external pull-ups; the SDK's board configuration turns on the IPRO7AI's internal pull-ups. Before you switch the slot off with GPIO14, drive GPIO28–33 low or make them inputs.

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
- CH0–CH4 in the PWM rows are the signal names of the GPIO function definitions (`drv_gpio.h`); the PWM driver (`drv_pwm.h`) provides CH0–CH3 only, so pins routed to CH4 have no driver.

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

The Reef's OV5640 camera wiring (SW7 must be on CAM):

| Signal | GPIO |
|---|---|
| D0–D7 | GPIO0–7 |
| PCLK | GPIO38 |
| VSYNC | GPIO39 |
| HSYNC / HREF | GPIO40 |
| XCLK (`CAM_MISC` reference clock, driven by the IPRO7AI) | GPIO22 |
| RESETB | GPIO34 |
| PWDN | GPIO35 |
| SCCB SCL / SDA (I2C0) | GPIO36 / GPIO37 |

The VDDIO1 power domain covers GPIO0–9 and GPIO36–41 (camera, USB and BOOT pins). I2C0 roles follow pin parity: even is SCL, odd is SDA. With SW7 on GPIO these 16 pins go to J_IO instead, and the camera's 2.8 V and 1.5 V regulators are off.

## Board default pins { #board-default-pins }

### IPRO7AI Reef EVK { #reef-default-pins }

From `bsp/board/ipro7/ipro7ai_reef_board_config.h`, set at boot. The Reef has no JTAG connector; the camera, audio and analog pins are set by their drivers when enabled.

| GPIO | Function | Setting | Purpose |
|---|---|---|---|
| GPIO14 | GPIO (11) | Output, low | microSD slot supply switch (with JP3 on GPIO, low = on) |
| GPIO15 | GPIO (11) | Input, pull-up | microSD card detect |
| GPIO20 | UART (7) | Pull-up | Console TX |
| GPIO21 | UART (7) | Pull-up | Console RX |
| GPIO24 | GPIO (11) | Output, low | WS2812 data line, held low so the LED stays dark at power-up |
| GPIO25 | GPIO (11) | Output, pull-down, amplifier off | Speaker amplifier enable (active high) |
| GPIO28–33 | SDC (27) | Pull-ups on DAT and CMD, drive strength 2 | microSD slot / FIN card |

The default pins of the other boards (IPRO7 EVB, IPRO7AI EVK) are in their board configuration headers in `bsp/board/ipro7/`; contact INTELPRO for these boards.

## Pin conflicts and design notes { #pin-conflicts }

- **GPIO20 / 21**: used by the Boot ROM's UART download and by the console; keep them connected to U6.
- **GPIO0–7, GPIO22, GPIO34–40**: the Reef's camera pins. With SW7 on CAM the camera uses them; with SW7 on GPIO they go to J_IO and the camera is off.
- **GPIO10, GPIO11, GPIO27**: the Reef's keys SW3, SW5 and SW4 (low when pressed); also brought out to J_IO.
- **GPIO12, GPIO13**: the Reef's headset-microphone analog inputs (AIN6, AIN7).
- **GPIO17–22**: carry flash (SF) functions. Whether they are free depends on the package, the flash configuration and the schematic, not on the number alone.
- **GPIO23–28**: shared with the external flash (SF2). On the Reef, GPIO23 is the GPDAC speaker output, GPIO24 the WS2812, GPIO25 the amplifier enable and GPIO26 the headset-detect input.
- **GPIO28–33**: SD card or external flash (SF2 / SF3), chosen with `CONFIG_DISABLE_SDC_PINMUX`; the Reef uses them for the microSD slot.
- **GPIO18 / 19**: the 32 kHz crystal pins. The Reef has no crystal fitted; these two pins are the I2C on J_IO (4.7 kΩ pull-ups on the board).
- **I/O voltage**: every IO on the Reef V4.0 is 3.3 V; never connect 5 V signals.
- **Schmitt trigger**: per pin (the last field of `GLB_GPIO_Cfg_Type`).

## Peripheral connection guide { #peripherals }

The Reef's 40-pin expansion header J_IO follows the Raspberry Pi's position and pin order. The table lists interfaces that the IPRO7's pin functions allow on J_IO. The SDK has no Reef example configuration for them; set the pin functions as described in the sections above. Interfaces marked SW7 on GPIO use camera pins, and the camera is off while they do.

| Interface | J_IO pins | GPIO and function | Condition |
|---|---|---|---|
| I2C | 3 SDA, 5 SCL | GPIO19, GPIO18, I2C0 (function 6) | 4.7 kΩ pull-ups on the board; SW7 in either position |
| SPI0 | 19 MOSI, 21 MISO, 23 SCLK, 24 SS | GPIO4, GPIO5, GPIO7, GPIO6, group 1 (function 4) | SW7 on GPIO; `pin_swap_enable = 0` |
| I2S0 | 12 BCLK, 35 FS, 40 DO, 38 DI | GPIO0, GPIO1, GPIO2, GPIO3, group 0 (function 3) | SW7 on GPIO |
| UART1 | 40 TXD, 38 RXD | GPIO2 (SIG_2), GPIO3 (SIG_3), function 7 | SW7 on GPIO; either this or I2S0 |
| Second I2C position (ID EEPROM) | 27 SDA, 28 SCL | GPIO37, GPIO36 | SW7 on GPIO |
| Console UART0 | 8 TXD, 10 RXD | GPIO20, GPIO21 | Taken by the console |

Pins 1 and 17 of J_IO are 3.3 V outputs; pins 2 and 4 output USB 5 V through a diode and cannot power the board. The full pin table is on [IPRO7AI Reef EVK](boards/reef-evk.md#j-io).

### I2C sensor { #i2c-sensor }

| J_IO | IPRO7AI | Sensor |
|---|---|---|
| 1 | 3.3 V | VDD |
| 3 | GPIO19 (function 6, I2C0_SDA) | SDA |
| 5 | GPIO18 (function 6, I2C0_SCL) | SCL |
| 6 | GND | GND |

The board already has 4.7 kΩ pull-ups; add none. I2C1 (function 25) is a separate second I2C controller.

### SPI peripheral (LCD / sensor) { #spi-peripheral }

| J_IO | IPRO7AI | Peripheral |
|---|---|---|
| 19 | GPIO4 (function 4, SPI0_MOSI) | SDI / MOSI |
| 21 | GPIO5 (function 4, SPI0_MISO) | SDO / MISO |
| 23 | GPIO7 (function 4, SPI0_SCLK) | SCK |
| 24 | GPIO6 (function 4, SPI0_SS) | CS# |

Needs SW7 on GPIO and `pin_swap_enable = 0`; for where MOSI and MISO land, see [SPI pins](#spi-pins).

### I2S audio codec { #codec }

| J_IO | IPRO7AI | Codec |
|---|---|---|
| 12 | GPIO0 (function 3, I2S0_BCLK) | BCLK |
| 35 | GPIO1 (function 3, I2S0_FS) | LRCLK / WS |
| 40 | GPIO2 (function 3, I2S0_DO) | DIN |
| 38 | GPIO3 (function 3, I2S0_DI) | DOUT |

Needs SW7 on GPIO. Connect the codec's control interface to the I2C on J_IO (pins 3 and 5). Each group of four is BCLK, FS, DO, DI in order; see [I2S pins](#i2s-pins).

### UART expansion { #uart-expansion }

UART1 can sit on most GPIOs; on J_IO use GPIO2 (pin 40, TXD) and GPIO3 (pin 38, RXD) with SW7 on GPIO, configured as in the example under [UART pins](#uart-pins). GPIO20 / 21 stay reserved for the Boot ROM's UART download and the console.

### SD card { #sd-card }

The Reef's microSD slot always uses GPIO28–33; these pins do not reach J_IO:

| IPRO7AI | SD card |
|---|---|
| GPIO28 (function 27, SDC_DAT1) | DAT1 |
| GPIO29 (function 27, SDC_DAT0) | DAT0 |
| GPIO30 (function 27, SDC_CLK) | CLK |
| GPIO31 (function 27, SDC_CMD) | CMD |
| GPIO32 (function 27, SDC_DAT3) | DAT3 |
| GPIO33 (function 27, SDC_DAT2) | DAT2 |

### PDM microphone { #pdm-mic }

PDM microphones are captured through the audio ADC (AUADC); pin roles follow parity: even is PDM_CLK, odd is PDM_DATA. The Reef's on-board PDM microphone MK1 is on CLK GPIO16 and DATA GPIO17; `mic rec pdm` in `ipro7ai_reef_demo` records from it.

### Antenna { #antenna }

Choosing a 2.4 GHz antenna:

| Type | Characteristics |
|---|---|
| PCB antenna | Low cost; needs a keep-out area |
| Chip antenna | Small; needs a matching network |
| External antenna | Best performance; needs a U.FL connector |

Put a π matching network between the RF output and the antenna: a shunt capacitor to ground at the RF side, a series inductor, and another shunt capacitor to ground at the antenna side. The Reef uses the PCB antenna E1 by default; move the 0 Ω resistor from R2 to R1 to use the u.FL connector RF1 instead.

## Related documents { #documents }

- [IPRO7AI Reef EVK](boards/reef-evk.md#pinout): on-board wiring, J_IO and U6 pin tables.
- [IPRO7](chips/ipro7.md#interfaces): peripheral counts and specifications.
- [Power & Current Measurement](power.md): how the Reef is powered and how to measure current.
- IPRO7 datasheet and hardware design guide (pin definitions, GPIO multiplexing): see [Documents](../documents/index.md).
