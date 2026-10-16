---
title: "IPRO7AI EVK"
description: IPRO7AI EVK on-board features, J6 wiring, quick start, launcher and board demo firmware, supported examples and SDK board support
migrate_from:
  - "applications.html#ipro7ai-evk-demo"
  - "applications.html#ipro7ai-evk-launcher"
---

# IPRO7AI EVK

The IPRO7AI EVK is a development kit with an IPRO7AI module on a sub-board that carries a 2.4" LCD, an SC101IOT camera, a PDM microphone, a speaker, a micro-SD slot and a Li-ion charger, for vision AI and user-interface work. It is a different board from the [IPRO7AI Reef EVK](reef-evk.md): the Reef has no LCD, and its camera and audio are set up differently.

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>Module on the EVK sub-board</span></div>
<div><strong>1 MB</strong><span>In-package flash</span></div>
<div><strong>2.4"</strong><span>ST7789P3 LCD, 240 × 320</span></div>
<div><strong>SC101IOT</strong><span>Camera, 1280 × 720 DVP</span></div>
<div><strong>J6</strong><span>Wire VDDIO1 before power-on</span></div>
</div>

## On-board features { #features }

| Block | Contents |
|---|---|
| Core | IPRO7AI: NPU, 8 MB PSRAM and 1 MB flash in the package |
| Display | HEM LCM-T2D4BP-084: 2.4" IPS, 240 × 320, ST7789P3, 4-wire SPI (SPI0), 3.3 V |
| Camera | SmartSens SC101IOT, 1280 × 720 DVP, SCCB address 0x68, on FPC CN5 |
| Speaker | On-chip DAC (GPIO23) → TPA2037D1 mono class-D amplifier → J1 |
| Microphone | Infineon IM69D129 PDM microphone into the AUADC |
| Storage | micro-SD slot (SDH controller, 4-bit, switched supply), FatFS at `sd:/` |
| Power | USB-C (CN1) for power and USB device; Li-ion battery connector CN4 and charger |
| Debug | UART0 console (GPIO20 / 21); JTAG pins; RST key (SW1, the only key on the board) |

### Pins { #pinout }

| Block | Pins |
|---|---|
| Display | CS GPIO10, backlight GPIO12, RST GPIO14, SCLK GPIO15, MOSI GPIO16, DC GPIO17 |
| Camera | D0–D7 = GPIO0–7, SCL GPIO36, SDA GPIO37, PCLK GPIO38, VSYNC GPIO39, HSYNC GPIO40, MCLK GPIO41, RST GPIO35 |
| Speaker | DAC GPIO23; amplifier enable on GPIO22, high = on |
| Microphone | CLK GPIO18, DAT GPIO19 |
| micro-SD | Supply GPIO27, D1 GPIO28, D0 GPIO29, CLK GPIO30, CMD GPIO31, D3 GPIO32, D2 GPIO33, detect GPIO34 |
| Console | UART0 TX GPIO20, RX GPIO21 |
| JTAG | TMS GPIO24, TDI GPIO25, TCK GPIO26, TDO GPIO11 |
| Spare | GPIO13 (on J3 only) |

GPIO22 is also DAC channel B on the chip; the EVK uses it as the amplifier enable, so audio output is mono. GPIO41 is both the boot strap and the camera MCLK.

!!! warning "Wire J6 before power-on"
    Pin 3 of J6 (2×5) is the supply input of VDDIO1, which powers GPIO0–9 and GPIO36–41 (the camera's DVP and SCCB) and the in-package flash. Connect **pin 3 to pin 7 (2.8 V)** with a jumper wire; the pins are not adjacent, so a jumper cap does not fit. If VDDIO1 is unpowered at reset, the chip cannot read its flash and enters download mode instead of booting.

## Quick start { #quick-start }

This walk-through uses `ipro7ai_evk_launcher`: one image that runs the camera, LCD, microphone and speaker together and flips pages with hand gestures recognized on the NPU.

<div class="ipro-steps" markdown>

1. **Connect**: wire J6 pin 3 to pin 7 as described above, plug in USB-C and connect a USB-to-UART cable to UART0 (GPIO20 TX / GPIO21 RX).

2. **Build**

    ```bash
    make -C apps/platform/ipro7ai_evk_launcher
    ```

    Output: `apps/platform/ipro7ai_evk_launcher/build/build_out/ipro7ai_evk_launcher_IPRO7.bin`

3. **Prepare the flash tool**: the EVK needs flash-pin setting `0x9`. When you run the IntelProCube command-line tool directly with `--chip-variant IPRO7AI`, the tool writes `flash_pin = 0x9` into its settings file `chips/ipro7/eflash_loader/eflash_loader_cfg.ini`. The application's `flash.sh` does not pass `--chip-variant` and uses whatever the settings file holds. If the loader reads flash JEDEC ID `00000000` and stops with `IPRO FLASH MATCH TYPE FAIL`, the pin setting is wrong; the board is fine.

4. **Enter download mode**: if firmware is running, `flash.sh` sends `reboot_dl` for you. For a new board, or when the firmware does not run:

    1. Move the wire on J6 pin 3 from pin 7 to pin 1 (or just pull it off), so that VDDIO1 is unpowered.
    2. Press RST (SW1).
    3. Put the wire back on pin 3 – pin 7; writing the flash needs VDDIO1.

    A board in download mode prints nothing on the console; that is expected.

5. **Flash the partition table, firmware and gesture model**: use `--full` the first time, and no argument when you only update the firmware.

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube dir>/ipro_iot_tool_macos
        cd apps/platform/ipro7ai_evk_launcher
        PORT=/dev/cu.usbserial-XXXX ./flash.sh --full
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube dir>/ipro_iot_tool_linux
        cd apps/platform/ipro7ai_evk_launcher
        PORT=/dev/ttyUSB0 ./flash.sh --full
        ```

    === "Windows"

        `flash.sh` is a bash script; on Windows run the tool directly from the IntelProCube directory:

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI --port COM5 --baudrate 921600 --skip-ota `
            --pt <SDK>\apps\platform\ipro7ai_evk_launcher\partition_cfg_1M_launcher.toml `
            --firmware <SDK>\apps\platform\ipro7ai_evk_launcher\build\build_out\ipro7ai_evk_launcher_IPRO7.bin `
            --mfg <SDK>\apps\ai\ipro7ai_evk_rps\model\rps_v3.inm
        ```

    `flash.sh` looks for `[All Success]` in the tool output. Press RST afterwards.

6. **Verify**: the console runs at 921600 baud.

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --send "app status" --timeout 10
    ```

    The LCD shows the camera preview; hold an open hand (PAPER) in the box for about half a second to move to the next page.

</div>

## Launcher firmware ipro7ai_evk_launcher { #ipro7ai-evk-launcher }

Two models share the one NPU: a gesture classifier (the rock-paper-scissors model) flips pages, and YOLOv8 detects people and pets.

| Page | Shows | ROCK | SCISSORS |
|---|---|---|---|
| 1 CAMERA | Live preview, the gesture box and the recognized class | Freeze / resume the preview | Mirror on / off |
| 2 DETECT | Live preview with person (green) / pet (yellow) boxes | Pet boxes on / off | Mirror on / off |
| 3 VOICE | Microphone waveform and peak level (dBFS) | Record 5 s, then play it through the speaker | Replay the last clip |
| 4 ABOUT | Status of every block: model sources, NPU and camera rates, microphone, speaker, SD card, memory | — | — |

PAPER moves to the next page. Without a camera, the shell commands `app next`, `app select` and `app alt` stand in for the gestures.

Model sources:

| File on the card | Source in the SDK | Role |
|---|---|---|
| `sd:/models/gesture.inm` | `apps/ai/ipro7ai_evk_rps/model/rps_v3.inm` | Optional; the same model as in the `mfg` partition, and the card wins when present |
| `sd:/models/person.inm` | `apps/platform/ipro7_demo/demo/ai/ai_model/person_pet_detect.inm` | Required for the DETECT page; it does not fit in the `mfg` partition, so it must be on the SD card |

Flash layout (`partition_cfg_1M_launcher.toml`): 320 KB of firmware from `0x3000` and a 688 KB `mfg` partition from `0x53000`. `ipro7ai_evk_person_detect` and `ipro7ai_evk_rps` use the same layout, so the three swap freely. This image uses the NPU and has no Bluetooth.

Useful shell commands:

```text
app status               status of every block
app page <1..4>          jump to a page
app rec [seconds]        record and play back (VOICE page)
spk tone [hz] [ms]       test the speaker on its own
mic level [seconds]      test the microphone on its own (peak / RMS in dBFS)
sd ls [path]             list the SD card
```

## Board demo ipro7ai_evk_demo { #ipro7ai-evk-demo }

`ipro7ai_evk_demo` is the EVK's board demo and bring-up tool, with a shell command per block: `lcd` (display), `cam` (camera), `spk` (speaker), `mic` (microphone), `vbat` and `adc` (the SoC's own supply voltage and a generic GPADC reader), `sd` (micro-SD), `vid` (video playback from the SD card), and `bt` (BLE and an LE Audio unicast sink) in the `config_bt` build.

The NPU and BLE do not fit in OCRAM together, so pick a configuration for the job:

| Configuration | Contents | Console |
|---|---|---|
| `.config` (default) | SD-card video kiosk, no Bluetooth, no NPU, no autoplay | 921600 |
| `config_ai` | NPU, camera, display, audio, SD card; no Bluetooth | 115200 |
| `config_bt` | BLE and LE Audio, camera, display, audio, SD card; no NPU | 115200 |
| `config_autoplay` | As `config_bt`, and plays videos at boot | 115200 |
| `config_video` | SD-card video kiosk with autoplay | 115200 |

```bash
make -C apps/platform/ipro7ai_evk_demo DEFCONFIG=config_bt   # output in build_config_bt/build_out/
```

You can also switch the default with `cp config_bt .config && make clean && make`. Flash with `--chip-variant IPRO7AI`; the flashing command in the application README uses a retired tool and no longer applies.

A first bring-up runs these checks in order:

```text
lcd id          read the panel ID back over SPI
lcd bars        color bars
cam probe       scan SCCB for the sensor
cam start       live preview
spk tone 1000 2 1 kHz sine: DAC, amplifier and speaker
mic rec 3       record 3 s
mic stats       peak and RMS
mic play        play it back
```

## Supported examples { #examples }

| Example | EVK configuration | Contents |
|---|---|---|
| `apps/platform/ipro7ai_evk_launcher` | default `.config` | Gesture-driven all-in-one demo, see above |
| `apps/platform/ipro7ai_evk_demo` | `.config`, `config_*` | Board demo and bring-up, see above |
| `apps/ai/ipro7ai_evk_person_detect` | default `.config` | Camera preview with YOLOv8 person / pet boxes; `flash.sh --full` writes the model; console 115200 |
| `apps/ai/ipro7ai_evk_rps` | default `.config` | Rock-paper-scissors against the NPU; model linked into the firmware, training scripts included; console 921600 |
| `apps/test/kw307_radar_test` | default `.config` | 24 GHz radar module over UART |
| `apps/multimedia/ipro_pdm_mic_demo` | `make BOARD=evk` (`config_evk`) | PDM recording, DAC playback, BLE transfer and USB audio; output in `build_config_evk/`, console 921600 |

Zephyr RTOS supports the `ipro7ai_evk` board; the SDK sample `zephyr/samples/evk_demo` uses the LCD, microphone, speaker and camera preview.

## SDK board support { #bsp }

- **Board configuration**: `CONFIG_IPRO7AI_EVK=y`, `CONFIG_BOARD="IPRO7AI_EVK"`, and write `CONFIG_USE_PSRAM=y` explicitly. The header is `bsp/board/ipro7/ipro7ai_evk_board_config.h`; wiring, power and download-mode notes are in `bsp/board/ipro7/IPRO7AI_EVK.md`.
- **Board library** `components/board/ipro7ai_evk`: `#include "evk.h"`, call `evk_begin()`, then use `evk_gfx_*` (panel), `evk_cam_*` (camera), `evk_mic_*` / `evk_spk_*` (audio) and `evk_sd_*` (SD card). Add to `.config` what you need:

    ```ini title=".config (excerpt)"
    CONFIG_COMPONENTS_IPRO7AI_EVK_ENABLE=y   # panel, graphics and PCM helpers; always
    CONFIG_EVK_CAMERA=y                      # also needs CONFIG_MM_SUPPORT, CONFIG_COMPONENTS_SENSOR_ENABLE, CONFIG_USE_PSRAM
    CONFIG_EVK_AUDIO=y                       # also needs CONFIG_AUDIO_OUTPUT, CONFIG_DMA_CHANNEL_ALLOCATOR
    CONFIG_EVK_SDCARD=y                      # also needs the EVFS and FatFS keys, see the component README
    CONFIG_EVK_SHELL=y                       # only if the app has no lcd / cam / mic / spk / sd commands of its own
    ```

- **Zephyr RTOS**: board `ipro7ai_evk`; `west flash` defaults to `--boot=shell` (the running image sends `reboot_dl`) and `partition_cfg_1M_boot2.toml` for this board.

## Related documents { #documents }

- `bsp/board/ipro7/IPRO7AI_EVK.md`: J6, power tree and download mode.
- `components/board/ipro7ai_evk/README.md`: board library API and configuration.
- The README in each example directory: build, flashing and commands.
- [Power & Current Measurement](../power.md#evk-power): the EVK power tree.
- [IPRO7AI](../chips/ipro7ai.md), [Pinout & Peripheral Mapping](../pinmux.md).
