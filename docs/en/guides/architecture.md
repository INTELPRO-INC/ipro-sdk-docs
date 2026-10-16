---
title: "Architecture"
description: IPRO SDK layers, the FreeRTOS and Zephyr build paths, components and directory layout, where the BLE stack sits, and the BSP
migrate_from:
  - "architecture.html#overview"
  - "architecture.html#rtos-paths"
  - "architecture.html#components"
  - "architecture.html#directory"
  - "architecture.html#ble-stack"
  - "architecture.html#bsp"
---

# Architecture

One source tree gives you two ways to develop: 35 FreeRTOS applications under `apps/`, and a Zephyr v4.4.0 module. Both share the HAL, the SoC drivers and the prebuilt libraries. The build flow and memory layout are in [Build System & Configuration](build-system.md).

!!! abstract "At a glance"
    - Layers: applications (`apps/`) → components (`components/`) → RTOS (FreeRTOS V11.1.0 or Zephyr v4.4.0) → BSP (`bsp/`) → chip.
    - The core is RISC-V RV32IMAFC with DSP extensions. For networking, use Ethernet or add an IPRO6S over SDIO.
    - The BLE controller, RF driver, low-power framework, AI inference runtime, ISP algorithms and LC3 codec ship as prebuilt libraries; everything else is source.
    - Every FreeRTOS application in V2.1.0 targets IPRO7 (`CONFIG_IPRO7=y`).

## System overview { #overview }

<div class="ipro-stack">
  <div class="l-app"><strong>Applications apps/</strong><span>ai · bluetooth · multimedia · platform · test</span></div>
  <div class="l-host"><strong>Components components/</strong><span>BLE host · lwIP · mbedTLS · CherryUSB · audio · ai · fs · shell</span></div>
  <div class="l-hci"><strong>RTOS</strong><span>FreeRTOS V11.1.0 · Zephyr v4.4.0 (module)</span></div>
  <div class="l-ctlr"><strong>BSP bsp/</strong><span>HAL · SoC drivers · board configuration · linker scripts</span></div>
  <div style="--layer: #64748b"><strong>Chip</strong><span>IPRO7 series: RISC-V RV32IMAFC · BLE 5.4 · ISP · NPU</span></div>
</div>

| Layer | Location | Role |
|---|---|---|
| Applications | `apps/<category>/<app>/` | Each application has its own `.config`, `CMakeLists.txt` and `Makefile` and builds on its own |
| Components | `components/` | Middleware and libraries, pulled into the build by the `CONFIG_*` keys in the application's `.config` |
| RTOS | `components/os/`, `zephyr/` | FreeRTOS scheduling, queues and timers plus the shared `freertos_app_hooks`; or the Zephyr kernel |
| BSP | `bsp/` | HAL API, registers and SoC drivers, board headers, linker script generator |

Prebuilt libraries ship with their public headers and are linked automatically; nothing has to be configured to use them. Debug information is stripped but symbol names are kept, so map files and `nm` still work.

## FreeRTOS and Zephyr { #rtos-paths }

```mermaid
flowchart TB
  A["FreeRTOS applications in apps/"] -->|"make / build_freertos.sh"| C["bsp/hal · SoC drivers · prebuilt libraries"]
  B["zephyr/samples and Zephyr samples"] -->|"west build"| D["zephyr/drivers · zephyr/hal_glue"]
  D --> C
```

| | FreeRTOS | Zephyr |
|---|---|---|
| Applications and samples | 35 applications under `apps/` | SDK samples in `zephyr/samples/` and upstream Zephyr samples; driver tests in `zephyr/tests/` |
| Build | `make -C apps/<category>/<app>` or `./build_freertos.sh` | Create a workspace with `tools/zephyr/bootstrap.sh`, then `west build` |
| Boards | IPRO7 EVB, IPRO7AI EVK, IPRO7AI Reef EVK | `ipro7_evb`, `ipro7ai_evk` |
| BLE | Zephyr v4.4 host running on FreeRTOS through a port layer, with the IPRO BLE controller (prebuilt library) | Zephyr's host with the same controller archives |
| IEEE 802.15.4 / Thread | Not provided | Zephyr IEEE 802.15.4 driver and OpenThread |
| Low power, display, camera, audio codec, USB, SD host, Ethernet, NPU | Provided | Not yet; the IPRO7AI EVK LCD works through Zephyr's ST7789V driver |
| Console | Per application, `CONFIG_PLATFORM_UART_BAUDRATE`; 115200 when unset | UART0 at 2000000 baud |

Products that need low power, a camera, audio or the NPU should use the FreeRTOS path. Zephyr boards, samples and flashing are covered in [Zephyr RTOS](zephyr.md).

## Components { #components }

All paths below are under `components/`.

| Area | Path | Contents |
|---|---|---|
| Bluetooth | `wireless/bluetooth/ipro_bt_host/` | BLE host, port of Zephyr v4.4.0 (source) |
| | `wireless/bluetooth/ipro_ble_controller/` | IPRO BLE controller (prebuilt library) |
| Radio | `wireless/rf/ipro7_rf/` | IPRO7 RF driver (prebuilt library) |
| | `wireless/ieee802154/` | IEEE 802.15.4 MAC for Zephyr (prebuilt library) |
| Networking | `network/lwip/` | lwIP 2.1.2 |
| | `network/ipronet_host/` | IPRO7-side host for Wi-Fi through an IPRO6S over SDIO (netif `iproeth0`) |
| | `network/rtsp_server/` | RTSP MJPEG video streaming |
| Security | `crypto/mbedtls/` | mbedTLS 2.28.2 |
| OS | `os/freertos/` | FreeRTOS V11.1.0 kernel and shared hooks (`freertos_app_hooks`) |
| | `os/freertos_posix/`, `os/ipro_osal/` | POSIX layer, OS abstraction layer |
| System services | `sys/shell/`, `sys/ipro_event/`, `sys/ipro_pm/` | Shell, event framework, power management |
| | `utils/` | Logging (`ipro_log.h`) and shared utilities |
| Audio | `audio/` | Audio capture and output (DAC, I2S, UAC), resampling, speaker EQ, MP3 decoding |
| AI | `ai/` | NPU inference runtime (`lib/libai.a` and headers) |
| Imaging | `isp_firmware/`, `isp_algorithm/`, `isp_iq_param/`, `isp_iq_cmd/` | ISP control, ISP algorithms (prebuilt), IQ parameters |
| | `sensor/` | Camera sensor drivers |
| Board library | `board/ipro7ai_evk/` | IPRO7AI EVK LCD, camera, microphone, speaker and SD card (`evk.h`) |
| USB | `cherryusb/` | USB device classes: CDC, CDC-ECM, HID, MSC, UAC, UVC |
| File systems | `fs/` | FatFS, LittleFS, EasyFlash4, EVFS, ROMFS |
| Third party | `3rdparty/` | LC3 (prebuilt), SBC, Opus, minimp3, TensorFlow Lite Micro, NMSIS-NN, TinyMaix, cJSON, xz, zmodem, Agora RTC SDK (prebuilt) and more |

External Wi-Fi modules and the IPRO6S host components are covered in [Networking](networking.md).

## Directory layout { #directory }

```text
IPRO-SDK-V2.1.0/
├── apps/                    FreeRTOS applications (35)
│   ├── ai/                  NPU examples
│   ├── bluetooth/ble/       BLE examples
│   ├── bluetooth/le_audio/  LE Audio headset
│   ├── multimedia/          USB webcam, PDM recording, cloud voice
│   ├── platform/            chip and board references; common/ holds shared OTA code
│   └── test/                driver tests, hardware bring-up and benchmarks (19)
├── bsp/                     HAL, SoC drivers, board configuration, linker scripts
├── components/              middleware and libraries
├── cmake/                   toolchain detection, build macros, autoconf.h generator
├── tools/                   serial_monitor.py, create_ota.py, zephyr/ scripts, Android example app source
├── zephyr/                  Zephyr module: boards, soc, dts, drivers, samples, tests
├── build_freertos.sh        front end for FreeRTOS build, flash and monitor
├── project.build            build driver called by every application Makefile
├── west.yml                 Zephyr west manifest
├── CMakeLists.txt
├── Kconfig
└── VERSION.txt
```

Run `./build_freertos.sh -l` for the full list of applications, or see [Examples](../examples/index.md).

## BLE stack { #ble-stack }

<div class="ipro-stack">
  <div class="l-app"><strong>Application</strong><span>Zephyr bt_* API</span></div>
  <div class="l-host"><strong>BLE host (Zephyr v4.4.0)</strong><span>ipro_bt_host: GAP · GATT · L2CAP · SMP · ISO · LE Audio</span></div>
  <div class="l-hci"><strong>On-chip HCI</strong><span>in-memory byte stream (ipro_ble_ctlr_hcitl)</span></div>
  <div class="l-ctlr"><strong>IPRO BLE controller (prebuilt library)</strong><span>ipro_ble_controller/lib/ · RF driver ipro7_rf</span></div>
</div>

The host ships as source and runs on FreeRTOS through the `ipro_bt_host/port/` layer; there is no UART HCI between the host and the controller. Three `.config` keys pick one of 16 controller archives to link. Archive selection, bring-up order and API usage are in [BLE Development](ble.md).

## BSP and drivers { #bsp }

| Path | Contents |
|---|---|
| `bsp/hal/` | HAL API (`inc/hal_*.h`, `src/hal_*.c`) |
| `bsp/hal/lp_framework/ipro7/` | Low-power (PDS) framework, prebuilt `liblp_framework.a` |
| `bsp/drivers/ipro7_soc/` | Register definitions, startup code (`startup/`), standard drivers (`std_drv/`), prebuilt NMSIS-DSP libraries (`DSP/`) |
| `bsp/drivers/soc_common/` | Drivers shared across chips |
| `bsp/board/ipro7/` | Board headers and `board.c`; `board_config.h` picks the board header from `CONFIG_EVB`, `CONFIG_IPRO7AI_EVK` or `CONFIG_IPRO7AI_REEF` |
| `bsp/board/linker/` | Linker script generator (template and `configs/ipro7_flash.cmake`) |
| `bsp/common/platform_utils/` | Platform init, console UART baud rate |

Peripherals covered by the HAL:

| Area | HAL |
|---|---|
| Communication | UART, SPI, I2C, I2S, SDIO |
| Storage | SPI flash, PSRAM, SD host (SDH), PIO software SD host |
| Analog and timing | ADC, DAC, AUADC (audio ADC), analog comparator, PWM, timer, RTC, watchdog |
| Input | GPIO, QDEC, keyscan |
| Imaging and AI | DVP camera, ISP, MJPEG encode and decode, NPU |
| Networking | EMAC Ethernet, lwIP netif, Ethernet PHY |
| Security | AES, SHA, ECDSA, P-256, GMAC, TRNG |
| System | DMA, clocks, power management, boot2 partition table |

Board pin assignments, speaker enable and similar definitions are in `bsp/board/ipro7/*_board_config.h`; the full pin map is in [Pinout & Peripheral Mapping](../hardware/pinmux.md).

## Related documents { #related }

- [Build System & Configuration](build-system.md): build flow, `.config`, memory layout, new applications
- [BLE Development](ble.md): archive selection, bring-up order, GATT example
- [Zephyr RTOS](zephyr.md): Zephyr boards, samples and flashing
- [Networking](networking.md): Ethernet, lwIP, Wi-Fi through an IPRO6S over SDIO
- [IPRO7](../hardware/chips/ipro7.md), [IPRO7AI](../hardware/chips/ipro7ai.md): chip specifications
