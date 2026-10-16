---
title: "IPRO7 EVB"
description: IPRO7 EVB on-board features, connectors, default pins, quick start, supported examples and SDK board support
migrate_from:
  - "hardware.html — 評估板 (EVB)／IPRO7-SEVB V1、IPRO7-SEVB 電源架構、EVB 預設 Pin 配置總覽"
not_migrated:
  - "hardware.html#evb — 開發用驗證平台卡片"
---

# IPRO7 EVB

The IPRO7 EVB is the evaluation board for IPRO7: a QFN56 chip socket, 12 V DC input, Ethernet, JTAG, USB, a DVP camera connector and GPIO expansion headers. Most application `.config` files use it as their default board (`CONFIG_EVB=y`), and the Zephyr board `ipro7_evb` targets it as well.

<div class="ipro-facts" markdown>
<div><strong>IPRO7</strong><span>QFN56 socket</span></div>
<div><strong>12 V</strong><span>DC input (J1)</span></div>
<div><strong>J19</strong><span>UART console</span></div>
<div><strong>J23</strong><span>JTAG</span></div>
<div><strong>RJ45</strong><span>10/100 Mbps Ethernet</span></div>
</div>

## On-board features { #evb }

| Block | Contents |
|---|---|
| Power | 12 V DC input (J1); regulators generate 5 V, 3.3 V, 1.8 V, 1.5 V and 0.9 V; TVS protection on the input |
| Core | IPRO7 QFN56 socket, 32 MHz crystal |
| Antenna | On-board PCB antenna; U.FL connectors (J118–J122) |
| Debug | JTAG (J23, GPIO0 / 1 / 2 / 11), UART console (J19, UART0 on GPIO20 / 21), USB 2.0 (J40) |
| Camera | DVP connector (J27), 8-bit data (D0–D7), PCLK / VSYNC / HSYNC |
| Audio | DAC speaker output with the amplifier enable on GPIO22 (low = on); I2S interface |
| Network | RJ45 Ethernet, 10/100 Mbps |
| Storage | micro-SD (GPIO28–33) |
| Expansion | GPIO expansion headers (J56–J63); PWM and motor-control interface |

### Main connectors { #connectors }

| Connector | Use |
|---|---|
| J1 | 12 V DC power input |
| J2 | System power output |
| J12, J13, J17 | USB |
| J19 | UART console |
| J23 | JTAG debug |
| J27 | DVP camera |
| J40 | USB 2.0 |
| J56–J63 | GPIO expansion |
| J118–J122 | U.FL antenna connectors |
| RJ45 | Ethernet |

!!! note "Power"
    Connect a 12 V DC adapter to J1. For the voltage and purpose of each rail, see [Power & Current Measurement](../power.md#evb-power).

## Default pins { #default-pins }

At boot the board configuration sets up the pins below. All other pins stay at their reset state until an application or driver configures them:

| Pins | Use |
|---|---|
| GPIO0, GPIO1, GPIO2, GPIO11 | JTAG (function 14) |
| GPIO15 | GPIO output, low at boot; `ipro7_sdio_wifi` uses it to switch the supply of the SDIO Wi-Fi companion |
| GPIO20, GPIO21 | UART0 TX / RX (console) |
| GPIO28–GPIO33 | SD card (function 27); with `CONFIG_DISABLE_SDC_PINMUX` they go to an external SF3 flash instead |

For pulls and drive strengths per pin and the list of free GPIOs, see [Pinout & Peripheral Mapping](../pinmux.md#evb-default-pins).

## Quick start { #quick-start }

This walk-through uses the BLE reference application `ipro_ble_remote`.

<div class="ipro-steps" markdown>

1. **Connect**: 12 V DC to J1 and a USB-to-UART cable to J19.

2. **Point to the flash tool**: `build_freertos.sh` finds the IntelProCube command-line tool through `IPRO_FLASH_TOOL` or `PATH`.

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube dir>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube dir>/ipro_iot_tool_linux
        ```

3. **Build, flash and open the console**

    ```bash
    ./build_freertos.sh build flash monitor -p /dev/cu.usbserial-XXXX ipro_ble_remote
    ```

    `flash` first sends `reboot_dl` on the console at 115200 baud to put the board in download mode (if no responding firmware is on the board, enter download mode with the BOOT strap instead), flashes at 921600 baud and checks the output for `[All Success]`; `monitor` opens the console at 115200 baud.

    `build_freertos.sh` passes no `--chip-variant`, so the flash pins come from the tool's settings file. The EVB uses `IPRO7` (`flash_pin` `0x2`). If the same IntelProCube was last used with `--chip-variant IPRO7AI` for a Reef or an EVK, flash once directly from the IntelProCube directory (macOS shown; for other systems see [Flashing & Serial Console](../../get-started/flash-and-monitor.md#flashing)):

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7 \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build/build_out/ipro_ble_remote_IPRO7.bin
    ```

4. **Verify**: the console shows the boot log, and a BLE scanner app on your phone lists `IPRO-Remote`.

</div>

## Supported examples { #examples }

Applications whose `.config` defaults to the EVB:

| Category | Examples |
|---|---|
| Platform references | `ipro7_demo` (whole-chip peripheral and system demo), `ipro7_sdio_wifi` (Wi-Fi host for an IPRO6S companion over SDIO) |
| BLE | `ipro_ble_remote`, `ipro_ble_transparent`, `ipro_ble_hid_keyboard`, `ipro_throughput_test` |
| Audio | `ipro_le_audio_headset`, `ipro_pdm_mic_demo` (external PDM microphone on GPIO0 / 1) |
| Camera | `ipro7_uvc_cam` (SC101IOT sensor, ISP, hardware MJPEG, USB Video Class) |
| AI | `ipro_npu_yolo`, `ipro_ai_bench`, `ipro_ai_link`, `ipro_tflm_test`, `ipro_tflm_yolo`, `ipro_nmsis_nn_test`, `ipro_tinymaix_demo` |
| Displays and sensors | `ipro_gh7007_test`, `ipro_gh7007_video`, `ipro_epd_test`, `ipro_epd_el036`, `mpu6500_test` |
| Storage and low power | `ipro_pio_sdh_test`, `ipro_lp_test` |
| Unit tests | `ipro_unit_test` |

## SDK board support { #bsp }

- **Board configuration**: `CONFIG_EVB=y`, `CONFIG_BOARD="EVB"`; the header is `bsp/board/ipro7/ipro7_evb_board_config.h`. The system clock is the 32 MHz crystal multiplied to 192 MHz by the PLL.
- **Flash layout**: 1 MB by default (`CONFIG_IPRO7_FLASH_1M`). With an external SF3 flash, select 2 / 4 / 8 MB with `CONFIG_IPRO7_FLASH_2M` and its siblings, and set `CONFIG_DISABLE_SDC_PINMUX` to hand GPIO28–33 to the flash.
- **PSRAM**: applications that need PSRAM write `CONFIG_USE_PSRAM=y` in `.config`.
- **Speaker amplifier**: the EVB's amplifier enable is active low (`BOARD_SPK_EN_ACTIVE` defaults to 0), and the DAC output of `components/audio` uses GPIO22 by default.
- **Zephyr RTOS**: board `ipro7_evb`, console at 2000000 baud; `west flash` uses `partition_cfg_2M.toml` for this board by default.

## Related documents { #documents }

- [Pinout & Peripheral Mapping](../pinmux.md): function select, alternate functions and EVB default pins.
- [Power & Current Measurement](../power.md#evb-power): EVB power rails.
- [IPRO7](../chips/ipro7.md): chip specifications.
- Board user guide and IPRO7 hardware design guide: see [Documents](../../documents/index.md).
