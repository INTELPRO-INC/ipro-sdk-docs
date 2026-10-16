---
title: "First FreeRTOS Application"
description: Build and flash the out-of-box firmware ipro7ai_reef_demo on the IPRO7AI Reef EVK and check the board with reef selftest.
migrate_from:
  - "getting-started.html#freertos-quickstart"
  - "getting-started.html#first-build"
---

# First FreeRTOS Application

Build the out-of-box firmware `ipro7ai_reef_demo`, flash it to the IPRO7AI Reef EVK, open the console and run `reef selftest` to check the LED, speaker, SD slot and camera. For the IPRO7AI EVK and IPRO7 EVB, see [Other boards](#other-boards).

## Prerequisites { #prerequisites }

- A working build environment from [Windows](windows.md) or [macOS / Linux](command-line.md).
- The IntelProCube v0.6.3 command-line tool: not included in V2.1.0; contact INTELPRO.
- An IPRO7AI Reef EVK, a USB-C cable (the Reef is powered from USB-C only) and a USB-to-UART cable for the U6 console connector (SH1.0).
- Optional: a FLEX-24 camera module (OV5640 or OV2640) and an SD card, to exercise the camera and slot steps of the self-test.

!!! warning "Before power-on"
    **JP1 must be fitted** (VDDIO1: 1-2 = 3.3 V, 2-3 = 2.8 V); without it the VDDIO1 bank that carries the camera, USB and BOOT has no supply. Fit JP2 on 1-2 (R40 0 Ω is the same link; fit one of the two). For the other jumpers, see [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md).

## Build { #first-build }

<div class="ipro-steps" markdown>

1. **Build the out-of-box firmware**: from the SDK root, run either command. On Windows, use `IPRO: Build` in the VS Code Extension instead (see [Windows Setup & VS Code](windows.md#installation)).

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    # or
    ./build_freertos.sh ipro7ai_reef_demo
    ```

2. **Check the output**: the linker prints flash and RAM usage at the end of the build. The output is in:

    ```text
    apps/platform/ipro7ai_reef_demo/build/build_out/
    ├── ipro7ai_reef_demo_IPRO7.bin    image to flash
    ├── ipro7ai_reef_demo_IPRO7.elf    with debug symbols
    └── ipro7ai_reef_demo_IPRO7.map    memory map
    ```

</div>

## Flash and run { #flash-and-run }

<div class="ipro-steps" markdown>

1. **Connect and enter download mode**: connect USB-C and the USB-to-UART cable on U6. Hold **SW1 (BOOT)**, tap **SW2 (RESET)**, then release SW1. U6's DTR and RTS lines also reach BOOT and RESET, so with an auto-download cable you can skip the buttons.

2. **Flash**: run the command-line tool from the IntelProCube directory. `--chip-variant IPRO7AI` selects the Reef's flash pin setting, and `--pt` gives the partition table that the Reef application READMEs use.

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    The tool exits with 0 even when flashing fails; it has only succeeded if the output contains `[All Success]`.

3. **Open the console and reset**: the console is on U6 at 115200 baud (8N1). On macOS / Linux, start the SDK's `tools/serial_monitor.py` first (`--timeout 0` keeps reading until you press ++ctrl+c++), then press SW2 (RESET). On Windows, use the Extension's Serial Monitor or another serial terminal.

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 115200 --timeout 0
    ```

4. **Run the self-test**: stop the previous monitor with ++ctrl+c++, then send `reef selftest`. In an interactive serial terminal, just type it.

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 5
    ```

</div>

## Verify { #verify }

At power-on the RGB LED breathes blue once and goes dark, the console shows the `IPRO7AI Reef carrier demo` banner and a `shell ready` message, followed by the `ipro />` prompt. Pressing SW3, SW4 and SW5 lights the LED red, green and blue.

`reef selftest` takes about 3 seconds and prints:

```text
[1/4] RGB LED: red, green, blue
[2/4] speaker: 1 kHz, 300 ms, 20%
[3/4] SD slot: <empty | something seated>, supply <on | off>
[4/4] camera bus: <sensor> at 0x<SCCB address>
done - keys: press any and run `btn status`
```

- Step 1: the LED shows red, green, then blue.
- Step 2: the speaker plays a short 1 kHz tone.
- Step 3: whether a card is seated, and whether the slot supply is on.
- Step 4: the camera sensor found on the bus, or `no sensor` without a camera.

Type `help` to list every command; the commands for each block are described on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md).

## Other boards { #other-boards }

The steps are the same; the suggested application, `--chip-variant`, partition table, download-mode method and console baud rate differ:

- **IPRO7AI EVK**: start with `apps/platform/ipro7ai_evk_launcher` and flash the partition table, firmware and gesture model with `./flash.sh --full` from the application directory; the console runs at 921600 baud. Wire J6 before power-on; the steps are on [IPRO7AI EVK](../hardware/boards/ipro7ai-evk.md#quick-start).
- **IPRO7 EVB**: the steps, using `ipro_ble_remote` as the example, are on [IPRO7 EVB](../hardware/boards/ipro7-evb.md#quick-start); the console runs at 115200 baud.

The `--chip-variant`, partition table and download mode for each board are collected in [Flashing & Serial Console](flash-and-monitor.md#board-settings).

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| No `[All Success]`; the handshake fails | The board is not in download mode | Hold SW1 (BOOT), tap SW2 (RESET) and flash again |
| The handshake passes, then `flash jedec id: 00000000` and `IPRO FLASH MATCH TYPE FAIL` | The flash pin setting is `0x2`; the Reef and IPRO7AI EVK need `0x9` | Add `--chip-variant IPRO7AI` to the flash command |
| No console output after flashing | The board is still in download mode (the boot ROM prints nothing), or the baud rate or port is wrong | Press SW2 (RESET); `ipro7ai_reef_demo` runs at 115200; use `/dev/cu.*` on macOS; check that JP1 is fitted |
| Console works, but the LED stays dark and the speaker is silent | The WS2812 and the speaker amplifier run from VBUS | Power the board from USB-C, not from 3V3 alone |
| `[4/4] camera bus: no sensor` | No camera, or the cable is not seated | Seat the FLEX-24 camera module |
| The build cannot find the compiler | The toolchain is not at the default path | Set `CROSS_COMPILE`; see [macOS / Linux Command Line](command-line.md#troubleshooting) |

## Next steps { #next-steps }

- [Flashing & Serial Console](flash-and-monitor.md): flash tool options, per-board settings, `build_freertos.sh flash` and console baud rates.
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md): every shell command, the jumpers, and Wi-Fi with RTSP streaming through the IPRO6S FIN card.
- [Your First BLE Application](../tutorials/first-ble-app.md)
- [Examples](../examples/index.md)
