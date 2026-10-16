---
title: IPRO7AI Reef EVK
description: IPRO7AI Reef EVK on-board features, jumpers, quick start, out-of-box firmware, supported examples and pin map
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK

<span class="ipro-badge">Recommended</span>

The IPRO7AI Reef EVK has an IPRO7AI (QFN56) soldered straight onto the carrier, with an OmniVision FLEX-24 camera connector (OV5640 / OV2640), DAC speaker and headphone outputs, three audio inputs, a WS2812 RGB LED, keys and an SD card slot; the slot also takes the IPRO6S FIN card for Wi-Fi. There is no LCD and no battery. The quick starts and examples on this site use this board by default.

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>SoC (QFN56, soldered on the carrier)</span></div>
<div><strong>1 / 2 MB</strong><span>In-package flash, depending on the part</span></div>
<div><strong>U6</strong><span>UART console, 115200 baud</span></div>
<div><strong>OV5640</strong><span>Camera (OV2640 also supported), DVP</span></div>
<div><strong>USB-C</strong><span>The only power input</span></div>
</div>

## On-board features { #features }

| Block | Contents |
|---|---|
| Core | IPRO7AI (QFN56), 32 MHz crystal; PCB antenna or u.FL connector (one of the two, selected with a 0 Ω resistor) |
| Memory | 8 MB PSRAM in the package; in-package flash of 1 MB or 2 MB depending on the part |
| Debug and flashing | U6 (SH1.0, 6 pins): UART0 (GPIO20 TX / GPIO21 RX), with DTR to BOOT and RTS to RESET so an auto-download cable works; SW1 is BOOT, SW2 is RESET |
| USB | USB-C for power and USB device (GPIO8 / 9) |
| Camera | 24-pin 0.5 mm FPC with the OmniVision FLEX-24 pinout (OV5640 / OV2640 modules); 8-bit DVP, SCCB on I2C0 |
| Audio out | DAC channel A (GPIO23) feeds both the class-D speaker amplifier (J_SPK) and the 3.5 mm headphone jack J2; the headphone output is mono |
| Audio in | PDM microphone (GPIO16 / 17), headset microphone (AIN7 / AIN6, differential), 3.5 mm AUX-IN J1 (AIN4 / AIN5) |
| LED and keys | WS2812 RGB LED (GPIO24), power LED; user keys SW3, SW4, SW5, plus SW1 (BOOT), which firmware can read after boot |
| Storage and Wi-Fi | SD slot (SDH controller, GPIO28–33, 4-bit) with card detect on GPIO15 and a supply switch on GPIO14; the same slot takes the IPRO6S FIN card |
| Expansion | J_IO 2×12 (2.54 mm): supplies, RESET, BOOT, UART, the SDIO lines and GPIO14 / 15 / 18 / 19 / 27 |

### Jumpers { #jumpers }

| Jumper | Setting |
|---|---|
| JP1 | VDDIO1 supply (GPIO0–9, GPIO36–41: camera, USB, BOOT): 1-2 = 3.3 V, 2-3 = 2.8 V. **Must be fitted** |
| JP2 | 1-2: 3V3 from the on-board buck converter. R40 (0 Ω) does the same job; fit one of the two |
| JP3 | SD_VDD: 1-2 = always on; 2-3 = switched by GPIO14. Use 2-3 with the IPRO6S FIN card so that `fin cycle` can power-cycle it |

!!! warning "Before power-on"
    - Fit JP1. Without it the VDDIO1 bank (camera, USB, BOOT) has no supply.
    - Power the board from USB-C only. The WS2812 LED and the speaker amplifier run from VBUS, so with a current-limited supply on 3V3 alone the LED and speaker stay dead.

## Quick start { #quick-start }

<div class="ipro-steps" markdown>

1. **Connect**: set the jumpers as above, plug in USB-C for power and connect a USB-to-UART cable to U6.

2. **Build the out-of-box firmware**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    Output: `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`

3. **Enter download mode**: hold SW1 (BOOT), tap SW2 (RESET), then release SW1. With an auto-download cable on U6 you can skip the keys; if firmware is already running, you can also type `reboot_dl` at the console.

4. **Flash**: run the command-line tool from the IntelProCube directory. `--chip-variant IPRO7AI` selects the QFN56 flash pins and `--pt` uses the partition table from the Reef application READMEs. The macOS command is shown; the Linux and Windows commands are in [Flashing & Serial Console](../../get-started/flash-and-monitor.md#flashing):

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    The tool exits with 0 even when it fails; check the output for `[All Success]`. The `flash` action of `build_freertos.sh` passes neither `--chip-variant` nor `--pt`, so do not use it for the Reef.

5. **Open the console and run the self-test**: reset with SW2, then send `reef selftest` on U6 at 115200 baud (8N1). On Windows, open `COM5` in any serial terminal and type the command.

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10
    ```

    At power-on the LED breathes blue once; SW3, SW4, SW5 and BOOT light it red, green, blue and white. `reef selftest` checks the LED, a 1 kHz speaker tone, SD card detection and the camera probe in about 3 seconds; the output is explained in [First FreeRTOS Application](../../get-started/first-app-freertos.md#verify).

</div>

## Out-of-box firmware ipro7ai_reef_demo { #reef-demo }

Each block on the board has its own set of shell commands. The Reef has no LCD; check the camera from the shell.

| Block | Shell commands | Description |
|---|---|---|
| Status and self-test | `reef status`, `reef selftest` | Pins, key states, LED, amplifier and detect lines; the whole self-test in one go |
| RGB LED (WS2812) | `led <r> <g> <b>`, `led rainbow`, `led off` | Set a color (0–255) or a rainbow effect |
| Keys | `btn status`, `btn watch` | Debounced state and press counts; live press / release events |
| Speaker and headphones | `spk tone <hz> <ms>`, `hp` | Sine wave from DAC A; add `hp` to a command to keep the amplifier muted and use the headphones only. `hp` reads headphone detection (GPIO26) |
| Audio input | `mic rec <source> <s>`, `mic play`, `mic loop` | Source is `pdm`, `headset` or `aux`; record at 16 kHz into PSRAM (up to 10 s) and play back, or monitor live |
| SD card | `sd mount`, `sd ls`, `sd test`, `sd bench`, `sd power` | FatFS mounted at `sd:`; write, read back and verify; switch SD_VDD when JP3 is on 2-3 |
| FIN card | `fin`, `fin cycle` | Slot status; power-cycle the FIN card when JP3 is on 2-3 |
| Camera | `cam probe`, `cam start`, `cam status`, `cam snap`, `cam bar on` | OV5640 / OV2640 in YUV422 1280×720 through ISP channel 0; frame count, frame rate and error counters, ASCII thumbnail, sensor color bars |

Bring the camera up in this order:

```text
cam probe        read the sensor ID over SCCB
cam start        start capture
cam status       run twice a second apart: frames climb, errors stay flat
cam bar on       switch to color bars
cam snap         the ASCII thumbnail shows vertical bands
cam bar off
cam snap         the real scene
```

## Wi-Fi and RTSP camera streaming { #wifi-rtsp }

The `defconfig_wifi_ipro6s` build connects through an IPRO6S FIN card in the slot (SDIO) and serves the camera as an RTSP MJPEG stream (`rtsp://<ip>:8554/av0_0`), using the SDK components `components/network/ipronet_host` and `components/network/rtsp_server` on the IPRO7 side.

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # output in build_wifi_ipro6s/build_out/
```

The connection and streaming steps, the command table and the `ipronet_host` API are in [Networking](../../guides/networking.md#wifi-ipro6). With JP3 on 2-3, `fin cycle` power-cycles the FIN card.

!!! info "Obtain separately"
    The IPRO6S firmware for the FIN card is not included in V2.1.0; contact INTELPRO.

## Supported examples { #examples }

| Example | Reef configuration | Contents |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` | default `.config`; `defconfig_wifi_ipro6s` | Out-of-box firmware; adds Wi-Fi and RTSP streaming |
| `apps/bluetooth/ble/ipro_ble_remote` | `defconfig_reef` | GATT services on the Reef hardware (LED, keys, camera, microphone, speaker, SD card) and BLE OTA. OTA needs boot2 and `partition_cfg_2M_remote_ab.toml`, not the standard `partition_cfg_2M.toml`; see the application README |
| `apps/bluetooth/ble/ipro_throughput_test` | `defconfig_reef` | BLE throughput test between two boards |
| `apps/bluetooth/le_audio/ipro_le_audio_headset` | `defconfig_reef` | LE Audio unicast headset, DAC output variant |
| `apps/multimedia/ipro7_uvc_cam` | `defconfig_reef_ov5640`, `defconfig_reef_rps` | USB webcam; the second configuration draws NPU rock-paper-scissors results into the video |
| `apps/test/ipro_ai_link` | `defconfig_reef` | Board firmware for IPRO AI Studio "Run on board" |
| `apps/multimedia/ipro_agora_sentino` | default `.config` | Cloud AI voice chat: BLE provisioning, FIN-card Wi-Fi, Agora RTC. Needs a device triple, the FIN-card firmware and the AOSL submodule; see the application README |

Select a Reef configuration with `DEFCONFIG=`. The output goes to `build_<name>/`, where the name is the file name without `defconfig_`:

```bash
make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef   # output in build_reef/build_out/
```

Every Reef configuration in the table uses a 115200-baud console.

## Pin map { #pinout }

| Block | Pins |
|---|---|
| UART0 console | TX GPIO20, RX GPIO21 (U6; J_IO 13 / 15) |
| USB device | DP GPIO8, DM GPIO9 |
| Camera DVP | D0–D7 = GPIO0–7, PCLK GPIO38, VSYNC GPIO39, HREF GPIO40, XCLK GPIO22, RESETB GPIO34, PWDN GPIO35 |
| Camera SCCB | SCL GPIO36, SDA GPIO37 (I2C0) |
| Speaker | DAC A GPIO23 → class-D amplifier; enable on GPIO25, high = on |
| Headphones | Same DAC A as the speaker; plug detect on GPIO26, low = plugged in |
| PDM microphone | CLK GPIO16, DATA GPIO17 |
| Headset microphone | AIN7 (GPIO13) positive, AIN6 (GPIO12) negative |
| AUX-IN | AIN4 (GPIO10) left, AIN5 (GPIO11) right |
| RGB LED | WS2812 DI on GPIO24, driven from SPI0 MOSI (needs `pin_swap_enable = 0`) |
| Keys | SW1 BOOT GPIO41 (active high), SW3 GPIO10, SW4 GPIO27, SW5 GPIO11 (active low) |
| SD slot | D1 GPIO28, D0 GPIO29, CLK GPIO30, CMD GPIO31, D3 GPIO32, D2 GPIO33; detect GPIO15 (low = card present); supply GPIO14 (low = on) |

GPIO10 / 11 are both AUX-IN and SW3 / SW5, so at any one time each pin is either an analog input or a key. GPIO22 is also DAC channel B on the chip; the Reef uses it as the camera clock.

J_IO (2×12) pinout:

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | 3V3 | 2 | GND |
| 3 | VBUS | 4 | GND |
| 5 | VDDIO1 | 6 | SDIO_DAT1 (GPIO28) |
| 7 | 1V8 | 8 | SDIO_DAT0 (GPIO29) |
| 9 | SYS_RESET | 10 | SDIO_CLK (GPIO30) |
| 11 | GPIO41 (BOOT) | 12 | SDIO_CMD (GPIO31) |
| 13 | GPIO20 (UART TX) | 14 | SDIO_DAT3 (GPIO32) |
| 15 | GPIO21 (UART RX) | 16 | SDIO_DAT2 (GPIO33) |
| 17 | GPIO18 | 18 | GPIO14 (SD_PWR_EN) |
| 19 | GPIO19 | 20 | GPIO15 (SD_DET) |
| 21 | GPIO27 (SW4) | 22–24 | GND |

GPIO18 / 19 are the 32 kHz crystal pads; the Reef fits no crystal there, so they are free GPIOs.

## SDK board support { #bsp }

- **Board configuration**: put `CONFIG_IPRO7AI_REEF=y` and `CONFIG_BOARD="IPRO7AI_REEF"` in `.config`; the header is `bsp/board/ipro7/ipro7ai_reef_board_config.h`. The build does not apply Kconfig `select`, so also write `CONFIG_USE_PSRAM=y` explicitly.
- **Crystal trim**: when `.config` does not set `CONFIG_IPRO7_XTAL_CAPCODE`, `bsp/board/ipro7/CMakeLists.txt` applies 95 for the Reef; write another value in `.config` to override it (0 = keep the value from boot).
- **Flash layout**: `ipro7ai_reef_demo` links the 1 MB layout by default, which fits both in-package parts. If the boot log reports JEDEC ID `0xEF4015` (2 MB), add `CONFIG_IPRO7_FLASH_2M=y`. The `defconfig_reef` files of `ipro_ble_remote`, `ipro_le_audio_headset` and `ipro_ai_link`, and `ipro_agora_sentino`, already select 2 MB.
- **Zephyr RTOS**: this release has no Zephyr board for the Reef. The SoC's Kconfig help says the Reef runs `ipro7_evb` images with `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` set.

## Related documents { #documents }

- `apps/platform/ipro7ai_reef_demo/README.md`: all commands and camera troubleshooting.
- `bsp/board/ipro7/ipro7ai_reef_board_config.h`: the source notes on pins, power tree and jumpers.
- [Power & Current Measurement](../power.md#reef-power): the Reef power tree.
- [Pinout & Peripheral Mapping](../pinmux.md), [IPRO7AI](../chips/ipro7ai.md).
- IPRO7AI Reef EVK user guide (pin diagram, power tree, jumpers): see [Documents](../../documents/index.md).
