---
title: "Release Notes"
description: Release dates, additions, exclusions and known limitations of each official IPRO SDK release, newest first.
migrate_from:
  - "changelog.html"
---

# Release Notes

Official IPRO SDK releases, newest first. Downloads and the release notes of each version are on [GitHub Releases](https://github.com/INTELPRO-INC/IPRO-SDK/releases); the SDK package itself is described in the `README.md` at its root.

## IPRO-SDK-V2.1.0 { #v2-1-0 }

<span class="ipro-badge">Latest</span> Released 2026-10-16 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0)

Adds Zephyr RTOS support; the FreeRTOS applications target IPRO7, 35 in all.

**New and changed**

- **Zephyr RTOS**: the SDK is also a Zephyr v4.4.0 module (`zephyr/module.yml`, `west.yml`) for `ipro7_evb` and `ipro7ai_evk`: drivers for GPIO, UART, SPI, I2C, PWM, ADC, DAC, counter and RTC, watchdog, flash, DMA, entropy, I2S / PDM and more; Bluetooth LE (Zephyr host on the IPRO BLE controller prebuilt libraries); IEEE 802.15.4 and OpenThread; MCUboot through sysbuild; and image upload over BLE (MCUmgr SMP). Start with `tools/zephyr/bootstrap.sh`; see [Zephyr RTOS](../guides/zephyr.md).
- The RF driver and the IEEE 802.15.4 MAC ship as prebuilt libraries for Zephyr (`components/wireless/rf/ipro7_rf/lib/zephyr/`, `components/wireless/ieee802154/lib/zephyr/`).
- **New application `ipro_agora_sentino`**: Sentino cloud AI voice on the IPRO7AI Reef EVK, with BLE provisioning, Wi-Fi through the IPRO6S FIN card, MQTT and Agora RTC. It ships with the prebuilt Agora RTC SDK and the IPRO7 port of AOSL; the AOSL core, the device triple issued by the Sentino platform and the FIN card firmware are obtained separately, as the application's README describes.
- **IPRO7AI Reef EVK crystal trim**: Reef builds set the RF crystal capcode to 95 by default and apply it at boot and at every RF init (`CONFIG_IPRO7_XTAL_CAPCODE`; an explicit value in the application config wins). The prebuilt RF and IEEE 802.15.4 libraries take the value from the application. Under Zephyr, set `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` on the Reef.
- **Tools**: adds `tools/serial_monitor.py` (`--timeout 0` runs until Ctrl-C; high baud rates also work on Linux) and `tools/zephyr/`. `build_freertos.sh` and the Zephyr scripts take the serial port from `-p` / `IPRO_SERIAL_PORT`, or use the only USB serial port present; the flash tool comes from `IPRO_FLASH_TOOL` or `PATH`.
- The 16 IPRO7 prebuilt libraries of the IPRO BLE controller are updated.

**Applications**

- 35 FreeRTOS applications. Compared with V2.0.9, `ipro_agora_sentino` is new.
- Compared with V2.0.1, seven are new: `ipro7ai_reef_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_person_detect`, `ipro7ai_evk_rps`, `ipro7_uvc_cam`, `ipro_ai_link` and `ipro_agora_sentino`; the three IPRO6S applications (`ipro6_btdm_phyrf`, `ipro6_demo`, `ipro6_if_wifi`) are no longer provided.

**Not included**

- IPRO6S applications, BLE controller libraries and `ipro6_rf`: the package README still mentions IPRO6S, but this release has none of it; for IPRO6S development use V2.0.1, see [IPRO6S (V2.0.1)](../hardware/chips/ipro6s.md).
- The IPRO6S-side Wi-Fi firmware, including the Reef's FIN card; contact INTELPRO.
- Matter; Thread for FreeRTOS applications (Thread is available under Zephyr); model conversion tools.
- The IntelProCube flash tool and the RISC-V toolchain, which are obtained separately.

**Known limitations**

- `ipro_ble_remote/defconfig_lowpower` switches the BLE controller to a source build and cannot be built from this package.
- `build_freertos.sh flash` passes neither `--chip-variant` nor `--pt`, and `monitor` always uses 115200 baud; for IPRO7AI boards and 921600-baud applications use the tools directly; see [Flashing & Serial Console](../get-started/flash-and-monitor.md#build-script).
- Zephyr has no low-power modes yet and no drivers for the display, camera, audio codec, USB, SD host, Ethernet or NPU, and no board definition for the IPRO7AI Reef EVK.

The build and on-board checks done for the release are listed on its GitHub release page.

## IPRO-SDK-V2.0.9 { #v2-0-9 }

Released 2026-10-15 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.9)

The IPRO7 release before V2.1.0: 34 applications, no Zephyr.

- New IPRO7AI Reef EVK out-of-box firmware `ipro7ai_reef_demo`: LED, keys, speaker and headphone, microphone, SD card and OV5640 / OV2640 camera; `defconfig_wifi_ipro6s` adds Wi-Fi through the IPRO6S FIN card and an RTSP camera stream.
- New IPRO7AI EVK applications `ipro7ai_evk_launcher`, `ipro7ai_evk_rps` and `ipro7ai_evk_person_detect`, built on the new EVK board library `components/board/ipro7ai_evk`.
- New `ipro7_uvc_cam` (USB UVC camera) and `ipro_ai_link` (Run on board for IPRO AI Studio).
- The AI library `libai.a` can load models from the SD card; prebuilt libraries contain no build-machine paths.
- IPRO7 applications only; for IPRO6S development use V2.0.1.

## IPRO-SDK-V2.0.1 { #v2-0-1 }

Released 2026-09-09 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)

Maintenance release for continuous BLE audio, following the V2.0 expansion to IPRO6S and 31 application projects.

- Fixes Bluetooth host queue publication atomicity during sustained transfers.
- PDM recording supports up to 4 logical hours with a 240-second PSRAM ring and automatic 30-second chunks; Android keeps a high connection priority between chunks.
- PDM uses a `link2` controller, a one-connection host and 2M PHY; EVB / EVK configurations and Android companion source are included.
- Adds IPRO6S Wi-Fi / BR/EDR references (see [IPRO6S (V2.0.1)](../hardware/chips/ipro6s.md)), both SDIO link endpoints, NPU / TFLM examples and bundled `.inm` / `.tflite` models.
- Includes `ipro_unit_test` and Linux x86-64 CMake; `serial_monitor.py` and `PREBUILT-ARCHIVES-STRIPPED.txt` from 1.2.1 are absent.

The published release reports 31/31 application builds and a five-minute recording test with a Pixel 7a and an IPRO7AI board: ten 960,000-byte chunks, no lost packets or sequence gaps, a successful ring wrap, and steady transfer at 84.2–91.2 KB/s. These results apply to that test setup and are not a guarantee for every board or phone.

## Online Installer 3.4.0 { #tools-3-4-0 }

[Download the installer](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/online-installer-v3.4.0)

Adds a dynamic public catalog, independent package versions, compatibility selection for full installs, and cached offline installation. The Extension stays at 3.3.0. As checked on 2026-10-16, the catalog's stable SDK is still 1.2.1 and has no V2.x entry; download SDK V2.x from its release page, as described in [Windows Setup & VS Code](../get-started/windows.md#sdk-2-1-0).

## Development tools: Windows installer / Extension 3.3.0 { #tools-3-3-0 }

The installer and the Extension are versioned independently; this release goes with SDK V1.2.1. The Windows wizard offers Full, Extension only and SDK only modes. The Extension adds component updates from VSIX, SDK ZIP / folder and Git snapshots, alongside Control Center and its built-in Windows serial monitor. See [Windows Setup & VS Code](../get-started/windows.md) and [VS Code Extension](../guides/vscode.md).

## IPRO-IPRO7-SDK-V1.2.1 { #v1-2-1 }

Released 2026-09-08 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/v1.2.1)

- Zephyr 4.4 host in `ipro_bt_host`; IPRO BLE controller (prebuilt library) in `ipro_ble_controller`.
- 16 controller archives: four ACL variants × two feature profiles × debug / release. Controller sources are not included.
- IPRO7-side `ipronet_host` and `sdiowifi` components, plus `ipro7_sdio_wifi`; the matching IPRO6S firmware is obtained separately.
- AI inference ships as `components/ai/lib/libai.a` with headers; no `.blai` model files are included.
- `tools/serial_monitor.py` is included; the flash tool, board-test script, crash parser and OpenOCD configuration are separate.
- Per `PREBUILT-ARCHIVES-STRIPPED.txt`, debug information was removed from the AI, ISP, RF, LC3 and low-power framework archives for compatibility with binutils older than 2.41; source-level stepping inside those libraries is not possible.

| Application | Path | Description |
|---|---|---|
| `ipro_ble_remote` | `apps/bluetooth/ble/ipro_ble_remote/` | GATT services, image transfer and OTA |
| `ipro_ble_transparent` | `apps/bluetooth/ble/ipro_ble_transparent/` | UART / BLE transparent transfer |
| `ipro_throughput_test` | `apps/bluetooth/ble/ipro_throughput_test/` | Bidirectional BLE throughput test |
| `ipro_ble_hid_keyboard` | `apps/bluetooth/ble/ipro_ble_hid_keyboard/` | HID over GATT keyboard |
| `ipro_le_audio_headset` | `apps/bluetooth/le_audio/ipro_le_audio_headset/` | LE Audio headset with DAC / USB audio output configurations |
| `ipro_pdm_mic_demo` | `apps/multimedia/ipro_pdm_mic_demo/` | PDM microphone capture, BLE transfer and LC3 compression |
| `ipro7_demo` | `apps/platform/ipro7_demo/` | Peripheral, imaging, audio and Ethernet demo |
| `ipro7_sdio_wifi` | `apps/platform/ipro7_sdio_wifi/` | IPRO7 SDIO host with an IPRO6S as the Wi-Fi radio |
| `ipro7ai_evk_demo` | `apps/platform/ipro7ai_evk_demo/` | IPRO7AI EVK display, camera, audio and AI / BLE configurations |

The V1.0.1 image-capture, standalone BIS source / sink, cloud audio gateway and voice-assistant applications are not included in this release.

## IPROREL-IPRO7-V1.0.1 { #v1-0-1 }

Released 2026-03-13 · Platform: IPRO7 (RISC-V RV32IMAFC)

The full IPRO7 SDK delivery package combining platform, BLE, ISP and LE Audio, with 9 reference applications, a Zephyr-based BLE host, prebuilt linkN controller libraries and a unified build system.

| Category | Application | Description |
|---|---|---|
| bluetooth/ble | `ipro_ble_remote` | GATT services demo (LED, Button, UART, OTA, image transfer) |
| bluetooth/ble | `ipro_ble_transparent` | BLE transparent data transfer with an AT command interface |
| bluetooth/ble | `ipro_ble_img_capture` | Image capture with a BLE image upload service (includes OTA) |
| bluetooth/ble | `ipro_throughput_test` | Bidirectional BLE throughput test (2M PHY + DLE) |
| bluetooth/le_audio | `ipro_le_audio_headset` | GAF / BAP unicast and broadcast headset (LC3) |
| bluetooth/le_audio | `ipro_le_audio_bis_source` | Auracast-compatible BIS broadcast source |
| bluetooth/le_audio | `ipro_le_audio_bis_sink` | BIS broadcast sink (BASE parsing and audio resampling) |
| multimedia | `ipro_agora_sentino` | Agora RTC cloud audio streaming gateway (network via Ethernet / USB NCM) |
| platform | `ipro7_demo` | IPRO7 platform peripheral demo |

- BLE stack: Zephyr-based host (GAP, GATT, L2CAP, SMP, ISO, LE Audio); IPRO BLE controller prebuilt libraries in standard BLE (`link1_periph`, `link1`–`link8`), LE Audio (`link1_leaudio`, `link2_leaudio`), BLE 5.4 + LE Audio (`link1_leaudio_53_54`, `link2_leaudio_53_54`, `link4_leaudio_53_54`) and BLE 5.3 / 5.4 (`link1_53`, `link1_54`, `link2_54`) variants.
- Prebuilt libraries: `isp_algorithm` (ISP image processing), `ipro7_rf` (RF driver), `liblc3` (LC3 codec), `lp_framework` (low-power framework).
- Known limitations: BLE controller sources are not included, only the prebuilt linkN variants; `CONFIG_BLE_FORCE_SOURCE_BUILD` is not supported.

## IPRO-BLE-SDK-V0.0.1 { #v0-0-1 }

Released 2026-02-12 · Platform: IPRO7 (RISC-V RV32IMAFC)

The first official release of the IPRO BLE SDK: a BLE 5.4 and LE Audio development environment with 10 applications, a Zephyr-based BLE host, prebuilt controller libraries and a unified build system.

- BLE applications: BLE Remote (GATT services demo), Throughput Test (bidirectional throughput), HID Keyboard (HOGP), Transparent Data (transparent transfer with AT commands).
- LE Audio applications: LE Audio Headset (GAF / BAP unicast and broadcast), BIS Broadcast Source (Auracast-compatible), BIS Broadcast Sink (BASE parsing and resampling), Walkie-Talkie (BIS-based push-to-talk).
- ESL applications: ESL Tag (Bluetooth ESL Profile tag), ESL Gateway (access point for ESL tags).
- BLE stack: IPRO BLE controller prebuilt libraries (linkN variants; `link2_54` added in this release), prebuilt RF driver (`ipro7_rf`) and LC3 codec (`liblc3`); the legacy btprofile component was removed and applications use the Zephyr `bt_*` APIs throughout.
- Build system: unified CLI `./build_freertos.sh <app> build flash monitor`, automatic detection of vendor and standard GCC toolchains, Kconfig-based configuration.
- Requirements: RISC-V toolchain in `/opt/toolchain/riscv_ipro7/`, CMake 3.19 or later, Ninja, Python 3.8 or later.
- Known limitations: controller sources are not included; `ipro_blecontroller_test` (UART HCI mode) is not included because it needs controller sources; `CONFIG_BLE_FORCE_SOURCE_BUILD` is not supported.
