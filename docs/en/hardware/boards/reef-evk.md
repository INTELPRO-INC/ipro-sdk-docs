---
title: IPRO7AI Reef EVK
description: IPRO7AI Reef EVK (V4.0 board) on-board features, switches and jumpers, quick start, out-of-box firmware, supported examples and pin map
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK

<span class="ipro-badge">Recommended</span>

The IPRO7AI Reef EVK is built around an IPRO7AI (QFN56) with its flash and PSRAM inside the chip package. The board carries an OV5640 camera connector, a PDM digital microphone, a headset jack and a speaker amplifier, a microSD socket, an RGB LED, keys, and a 40-pin expansion header in the same position and pin order as on a Raspberry Pi. It is powered from USB-C only and has no LCD and no battery. This page covers the V4.0 board (silkscreen "IPRO7AI REEF EVK V4.0"); the quick starts and examples on this site use this board by default.

<figure>
  <img src="/ipro-sdk-docs/assets/images/reef-v4-top.jpg" alt="Top side of the IPRO7AI Reef EVK V4.0: the 40-pin header J_IO along the top edge, SW1, SW2 and the PCB antenna at the top right, SW7, U6 and the microSD socket on the left edge, and JP3, the speaker connector, the headset jack, SW8, JP2 and USB-C along the bottom edge" width="1500" height="1011" loading="lazy">
  <figcaption>IPRO7AI Reef EVK V4.0, top side</figcaption>
</figure>

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>SoC (QFN56) with NPU, ISP, BLE and IEEE 802.15.4</span></div>
<div><strong>2 MB + 8 MB</strong><span>In-package flash and PSRAM</span></div>
<div><strong>40-pin</strong><span>J_IO, Raspberry Pi position and pin order, 3.3 V</span></div>
<div><strong>U6</strong><span>UART console, 115200 baud</span></div>
<div><strong>USB-C</strong><span>The only power input</span></div>
</div>

## On-board features { #features }

| Block | Contents |
|---|---|
| Core | IPRO7AI (U1, QFN56): RISC-V RV32IMAFC, NPU, ISP, 2.4 GHz radio (BLE, IEEE 802.15.4); 32 MHz crystal (X1) |
| Memory | 2 MB flash and 8 MB PSRAM in the package; 256 KB OCRAM on the chip |
| Antenna | PCB antenna E1 (default); move the 0 Ω resistor from R2 to R1 to use the u.FL connector RF1 instead |
| Camera | FPC1: 24-pin, 0.5 mm pitch vertical FPC connector with the OV5640 FLEX-24 pinout, 8-bit DVP; the camera's 2.8 V and 1.5 V come from on-board regulators |
| Camera / GPIO switch | SW7 routes the 16 camera pins to J_IO through four SN74CB3Q3257 switches; in the GPIO position the camera supply is off |
| Audio in | PDM digital microphone MK1; headset microphone from jack J2 into analog inputs AIN6 and AIN7 |
| Audio out | The IPRO7AI GPDAC drives the headphone stage (TLV9061) to jack J2 (3.5 mm, CTIA), and the PAM8302A class-D amplifier to the speaker connector J_SPK (1.25 mm, 2 pins, for an 8 Ω speaker) |
| Storage | microSD socket CARD1 (push-push), 4-bit SD interface; card detect and socket power each on a GPIO |
| USB | USB-C (USB1): 5 V power and USB 2.0 Full-Speed device |
| Debug | U6: 6-pin, 1.0 mm pitch (SH1.0) with the console UART, BOOT and RESET; connects to the IPRO Debug Probe |
| Keys and LEDs | SW1 BOOT, SW2 RESET, user keys SW3 / SW4 / SW5 (side-actuated); LED1 RGB LED (WS2812B-2020), LED2 power LED (green) |
| Expansion | J_IO: 2 × 20, 2.54 mm header in the same position and pin order as the Raspberry Pi 40-pin header; all signals are 3.3 V |
| Current measurement | SW8 (PWR / MEAS) and JP2 measure the IPRO7AI's 3.3 V current |
| Size | 85 × 56 mm, 1.6 mm thick, six layers; four Ø2.75 mm mounting holes on a 58 × 49 mm pitch, placed relative to the 40-pin header as on a Raspberry Pi, for M2.5 standoffs |

Specifications follow the V4.0 design files (schematic and bill of materials).

### Switches and jumpers { #jumpers }

| Ref | Position | Function |
|---|---|---|
| SW7 | CAM (default) | Camera pins go to the IPRO7AI and the camera supply is on. Keep it on CAM whenever you use the camera |
| | GPIO | The 16 camera pins go to J_IO (the pins marked * in the [header table](#j-io)); both camera regulators are off |
| SW8 | PWR | Normal use: the IPRO7AI's 3.3 V comes straight from the board supply |
| | MEAS | Measurement: the IPRO7AI's 3.3 V comes through JP2, which must carry an ammeter or an external 3.3 V supply |
| JP3 | ON | The microSD socket is always powered |
| | GPIO | GPIO14 switches the socket supply: on while low or undriven, off while high |
| JP2 | — | 3 pins: 1 = 3V3 (board 3.3 V), 2 = SOC (the IPRO7AI's 3.3 V), 3 = GND; used only with SW8 on MEAS |

To measure the IPRO7AI's current, unplug USB-C, connect an ammeter between JP2 pins 1 and 2 (or an external 3.3 V supply across pins 2 and 3), slide SW8 to MEAS, then plug USB-C back in. When you are done, unplug USB-C, slide SW8 back to PWR and only then remove the ammeter. The reading covers the IPRO7AI's 3.3 V pins with their decoupling capacitors and the boot-strap pull-ups, not the peripherals.

!!! warning "Before power-on"
    - Power the board from USB-C only. The 5 V pins on J_IO (pins 2 and 4) are outputs; you cannot power the board through them.
    - All I/O is at 3.3 V; do not connect 5 V signals.
    - Unplug USB-C before you connect or disconnect the camera cable.
    - Leave SW8 on PWR. With SW8 on MEAS, do not plug in USB-C unless JP2 carries an ammeter or an external 3.3 V supply: the IPRO7AI would be unpowered while the peripherals' 3.3 V back-feeds it through the I/O pins.

## Quick start { #quick-start }

<div class="ipro-steps" markdown>

1. **Connect**: check that SW7 is on CAM and SW8 on PWR. Connect the IPRO Debug Probe to U6 (a 3.3 V USB-to-UART cable also works; the pinout is under [Debug connector U6](#debug-connector)), then plug in USB-C for power. U6 supplies no power; the board runs from its own USB-C.

2. **Build the out-of-box firmware**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    Output: `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`

3. **Enter download mode**: hold SW1 (BOOT), tap SW2 (RESET), then release SW1. With the IPRO Debug Probe connected, the probe drives download mode through the BOOT and RESET lines on U6; if firmware is already running, you can also type `reboot_dl` at the console.

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
| RGB LED | `led <r> <g> <b>`, `led rainbow`, `led off` | Set a color (0–255) or a rainbow effect |
| Keys | `btn status`, `btn watch` | Debounced state and press counts; live press / release events |
| Speaker and headphones | `spk tone <hz> <ms>`, `hp` | Sine wave from the GPDAC; add `hp` to a command to keep the amplifier muted and use the headphones only. On its own, `hp` reads the level of GPIO26 (headset plug detect) |
| Audio input | `mic rec <source> <s>`, `mic play`, `mic loop` | Source is `pdm` (on-board microphone) or `headset`; record at 16 kHz into PSRAM (up to 10 s) and play back, or monitor live |
| SD card | `sd mount`, `sd ls`, `sd test`, `sd bench`, `sd power` | FatFS mounted at `sd:`; write, read back and verify; with JP3 on GPIO, `sd power` switches the socket supply through GPIO14 |
| FIN card | `fin`, `fin cycle` | Status of the IPRO6S Wi-Fi card in the socket; power-cycle the card when JP3 is on GPIO |
| Camera | `cam probe`, `cam start`, `cam status`, `cam snap`, `cam bar on` | OV5640 in YUV422 1280×720 through ISP channel 0; frame count, frame rate and error counters, ASCII thumbnail, sensor color bars |

Bring the camera up in this order (SW7 on CAM):

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

The `defconfig_wifi_ipro6s` build connects through an IPRO6S Wi-Fi card (FIN card) on the SDIO interface of the microSD socket and serves the camera as an RTSP MJPEG stream (`rtsp://<ip>:8554/av0_0`), using the SDK components `components/network/ipronet_host` and `components/network/rtsp_server` on the IPRO7 side.

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # output in build_wifi_ipro6s/build_out/
```

The connection and streaming steps, the command table and the `ipronet_host` API are in [Networking](../../guides/networking.md#wifi-ipro6). With JP3 on GPIO, `fin cycle` power-cycles the card.

!!! info "Obtain separately"
    The IPRO6S Wi-Fi card (FIN card) and its firmware are not included in V2.1.0; contact INTELPRO.

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
| UART0 console | TX GPIO20, RX GPIO21 (U6 pins 3 / 4; J_IO pins 8 / 10) |
| USB device | D+ GPIO8, D− GPIO9 |
| Camera DVP | Data GPIO0–7, PCLK GPIO38, VSYNC GPIO39, HREF GPIO40, XCLK GPIO22 (driven by the IPRO7AI), RESETB GPIO34, PWDN GPIO35 |
| Camera SCCB | SIOC GPIO36, SIOD GPIO37 (I2C0; the pull-ups are on the camera module) |
| Speaker | GPDAC GPIO23 → PAM8302A; enable on GPIO25, high = on, off at power-up |
| Headset jack J2 | Headphones share GPDAC GPIO23 with the speaker; microphone on AIN6 (GPIO12) and AIN7 (GPIO13); plug detect on GPIO26 (GPADC) |
| PDM microphone | CLK GPIO16, DATA GPIO17 |
| RGB LED | WS2812B DI on GPIO24, driven from SPI0 MOSI (needs `pin_swap_enable = 0`) |
| Keys | SW1 BOOT GPIO41 (pulled down, high when pressed); SW3 GPIO10, SW4 GPIO27, SW5 GPIO11 (low when pressed) |
| microSD | CLK GPIO30, CMD GPIO31, DAT0 GPIO29, DAT1 GPIO28, DAT2 GPIO33, DAT3 GPIO32; card detect GPIO15; socket power GPIO14 (with JP3 on GPIO, low = on) |
| I2C on J_IO | SDA GPIO19, SCL GPIO18 (4.7 kΩ pull-ups on the board) |

The microSD CMD and DAT lines have no external pull-ups, so enable the IPRO7AI's internal pull-ups (the SDK board configuration does). Before you switch the socket off with GPIO14, drive GPIO28–33 low or make them inputs. These pins go to the socket only, not to J_IO.

### 40-pin expansion header J_IO { #j-io }

J_IO is a 2 × 20, 2.54 mm vertical header in the same position and pin order as the Raspberry Pi 40-pin header: power, ground, I2C and UART are where you expect them. Odd pins are in the inner row, even pins along the board edge. All signals are 3.3 V, and every signal pin has ESD protection.

- Pins marked * go through the camera switches: they reach the IPRO7AI only with SW7 on GPIO and carry no signal with SW7 on CAM.
- The 5 V on pins 2 and 4 is USB 5 V through a diode. It is present only while USB-C is plugged in, and you cannot power the board through it.
- Pins 16 and 18 (BOOT, RESET) are not connected by default; fit 0 Ω resistors at R92 and R93 if you need them.
- Pins 27 and 28 are a second I2C bus; with SW7 on GPIO you can use them to read an ID EEPROM on an add-on board.

| Pin | Signal | Notes | Pin | Signal | Notes |
|---|---|---|---|---|---|
| 1 | 3.3 V | Power output | 2 | 5 V | Output (USB 5 V through a diode) |
| 3 | GPIO19 | I2C SDA (4.7 kΩ pull-up) | 4 | 5 V | Output (same as pin 2) |
| 5 | GPIO18 | I2C SCL (4.7 kΩ pull-up) | 6 | GND | |
| 7 | GPIO27 | SW4 key | 8 | GPIO20 | UART0 TX (console) |
| 9 | GND | | 10 | GPIO21 | UART0 RX (console) |
| 11 | GPIO10 | SW3 key | 12 | GPIO0 * | |
| 13 | GPIO14 | microSD power control | 14 | GND | |
| 15 | GPIO15 | microSD card detect | 16 | BOOT | Not connected by default |
| 17 | 3.3 V | Power output | 18 | RESET | Not connected by default |
| 19 | GPIO4 * | | 20 | GND | |
| 21 | GPIO5 * | | 22 | GPIO35 * | |
| 23 | GPIO7 * | | 24 | GPIO6 * | |
| 25 | GND | | 26 | GPIO34 * | |
| 27 | GPIO37 * | Second I2C SDA | 28 | GPIO36 * | Second I2C SCL |
| 29 | GPIO22 * | | 30 | GND | |
| 31 | GPIO39 * | | 32 | GPIO40 * | |
| 33 | GPIO38 * | | 34 | GND | |
| 35 | GPIO1 * | | 36 | GPIO11 | SW5 key |
| 37 | NC | Not connected | 38 | GPIO3 * | |
| 39 | GND | | 40 | GPIO2 * | |

### Debug connector U6 { #debug-connector }

U6 is a 6-pin, 1.0 mm pitch right-angle connector (SH1.0) with the console UART and the BOOT and RESET lines, for flashing and for the boot log. The console is UART0, which is also the flashing UART: 115200 baud, 8N1, no flow control (921600 baud while flashing).

| Pin | Signal | Notes |
|---|---|---|
| 1 | NC | Not connected |
| 2 | GND | Ground |
| 3 | TX (GPIO20) | Reef output (console out) |
| 4 | RX (GPIO21) | Reef input (console in) |
| 5 | BOOT | To GPIO41 through 1 kΩ; high when reset is released = download mode |
| 6 | RESET | To the IPRO7AI reset pin through 1 kΩ; low = reset |

Connect the CN_UART connector of the IPRO Debug Probe to U6 with a cable whose pin order is reversed end to end: probe pin n goes to U6 pin 7 − n (probe RST to RESET, DL to BOOT, TXD to RX, RXD to TX, GND to GND, and the probe's 3V3 lands on the unconnected pin).

!!! warning "Cable direction"
    Do not use a straight cable (pin 1 to pin 1): the UART and control lines end up on the wrong pins, and the probe's 3.3 V on its pin 6 reaches RESET on U6.

## SDK board support { #bsp }

- **Board configuration**: put `CONFIG_IPRO7AI_REEF=y` and `CONFIG_BOARD="IPRO7AI_REEF"` in `.config`; the header is `bsp/board/ipro7/ipro7ai_reef_board_config.h`. The build does not apply Kconfig `select`, so also write `CONFIG_USE_PSRAM=y` explicitly.
- **Pin definitions**: the header's `BOARD_*` pins for the console, USB, camera, speaker, microphones, LED, keys and SD card match this page. The comments in the header and the jumper, expansion-header and audio-input notes in the `ipro7ai_reef_demo` README describe the previous carrier board; for V4.0, follow this page.
- **Crystal trim**: when `.config` does not set `CONFIG_IPRO7_XTAL_CAPCODE`, `bsp/board/ipro7/CMakeLists.txt` applies 95 for the Reef; write another value in `.config` to override it (0 = keep the value from boot).
- **Flash layout**: `ipro7ai_reef_demo` links the 1 MB layout by default. The V4.0 board has 2 MB of in-package flash; add `CONFIG_IPRO7_FLASH_2M=y` to give the linker the whole part. The `defconfig_reef` files of `ipro_ble_remote`, `ipro_le_audio_headset` and `ipro_ai_link`, and `ipro_agora_sentino`, already select 2 MB.
- **Zephyr RTOS**: this release has no Zephyr board for the Reef. The SoC's Kconfig help says the Reef runs `ipro7_evb` images with `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` set.

## Related documents { #documents }

- `apps/platform/ipro7ai_reef_demo/README.md`: all commands and camera troubleshooting.
- `bsp/board/ipro7/ipro7ai_reef_board_config.h`: the pin definitions the SDK uses.
- [IPRO AI Teach 2.0](../../guides/edge-ai-teach.md): IPRO AI Teach 2.0 on this board, teaching it to recognize images, voices and sensor signals from IPRO AI Studio.
- [Pinout & Peripheral Mapping](../pinmux.md), [IPRO7AI](../chips/ipro7ai.md).
- IPRO7AI Reef Development Kit User Guide (V4.0 board hardware, interfaces and power) and IPRO Debug Probe Board User Guide: available on request, see [Documents](../../documents/index.md).
