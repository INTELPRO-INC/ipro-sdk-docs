---
title: "Release Notes"
description: Release dates, additions, exclusions and known limitations of each official IPRO SDK release, newest first.
migrate_from:
  - "changelog.html"
---

# Release Notes

Official IPRO SDK releases, newest first; the current release is V2.3.0. Downloads and the release notes of each version are on [GitHub Releases](https://github.com/INTELPRO-INC/IPRO-SDK/releases); the SDK package itself is described in the `README.md` at its root. The Windows online installer, Online Setup, is listed here too (currently 3.6.0); it is downloaded from [ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest).

## IPRO-SDK-V2.3.0 { #v2-3-0 }

<span class="ipro-badge">Latest</span> Released 2026-11-13 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.3.0)

IPRO7 / IPRO7AI and IPRO6S release: one OTA component for every transport, an open example for the IPRO7AI Sensor Tag with flashing over the board's own USB, and the IPRO6S build line. 41 FreeRTOS applications: 38 for IPRO7, 3 for IPRO6S. Use it with [IPRO Workbench 0.2.1](https://github.com/INTELPRO-INC/ipro-workbench/releases/tag/v0.2.1) (see [IPRO Workbench](../workbench/index.md)) and IntelProCube 0.7.0.1 or later.

| Download | Size | SHA-256 |
|---|---|---|
| `IPRO-SDK-V2.3.0.tar.gz` | 163.4 MB | `0f39c1d2551be0aa748bfee6613ec3c8cb5cfa6b1cea310780f9d58ce216574b` |

**New and changed**

- **OTA component** `components/sys/ipro_ota` (`CONFIG_IPRO_OTA`): one package check for every transport. It reads the 512-byte OTA header, checks the SHA-256 of the image written to flash before the board switches to it, and erases each flash sector just before it is written. Two transports use it:
    - **OTA over the console UART**: the shell command `ota_uart <bytes> [noapply]` (`CONFIG_IPRO_OTA_UART`). IPRO Workbench 0.2.0 sends a package to the board with it (OTA Package → Send to Board).
    - **BLE OTA service** (UUID 0xFF60, `CONFIG_IPRO_OTA_BLE`): the service `ipro_ble_remote` had, now in the component. `ipro_ble_remote` (`defconfig_reef`) refuses a package whose SHA-256 does not match, and starts receiving in under half a second instead of about four (it no longer erases the whole slot first).

    See `components/sys/ipro_ota/README.md`; the steps are in [OTA Updates](../guides/ota.md).
- **`ipro7ai_sensor_tag_demo`** for the IPRO7AI Sensor Tag board: IMU (ISM330BX: acceleration, rotation, temperature), fuel gauge (CW2015), button, two LEDs and buzzer. It prints 20 lines a second of `name:value` pairs over the board's own USB, which the Sensor Dashboard of IPRO Workbench 0.2.0 lays out with the application's `dashboard.yaml`; shell commands `stream`, `rate`, `led`, `beep`. See [Examples](../examples/index.md).
- **`tools/ipro_dl.py`**: flashes a board through boot2's USB downloader (Python standard library only, macOS and Linux). The Sensor Tag example is flashed with it; IPRO Workbench 0.2.0 on macOS uses it when Flash targets the board's own USB port (from 0.2.1 Workbench speaks the downloader protocol itself and no longer needs it).
- **IPRO6S**: the boot prints a `Build:` line with the build date and time, as IPRO7 does, so IPRO Workbench can tell which firmware the board runs.
- **IPRO6S Wi-Fi**: `wifi_ap_start -b 1 -o 1` keeps a 2.4 GHz access point on its 40 MHz channel even when neighbouring networks overlap it (`-b 1` alone still falls back to 20 MHz, as before).
- **Fixed**: with DTIM power save, an access point whose beacon is sometimes late behind a neighbour's made the IPRO6S open its receiver too late and miss beacons; the receive window now stays on the on-time beacon.
- `ipro6_demo` ships the configurations its prebuilt archives build: `defconfig_ipro6_lpwifi` and `defconfig_ipro6_lp`. `defconfig_ipro6_lpwifi_ping` (in V2.2.x) is no longer in the package: it needs the Wi-Fi library sources.
- Package README: IPRO6S is described as Wi-Fi.

**Applications**

- 41 in all: 38 for IPRO7, 3 for IPRO6S. New since V2.2.1: `ipro7ai_sensor_tag_demo`.
- Upgrading from V2.2.x: unpack the new package and rebuild your applications.

Built and checked from the package before release: 37 FreeRTOS applications (`ipro_agora_sentino` once AOSL is fetched), all 7 shipped IPRO6S configurations, and the Zephyr sample matrix and `twister --build-only` for `ipro7_evb` and `ipro7ai_evk`. On boards: an IPRO6S EVK ran `ipro6_demo` (`defconfig_ipro6_lpwifi`) built with IPRO Workbench 0.2.0 and flashed with IntelProCube 0.7.0.1 (`partition_cfg_fw_direct.toml`), printed its `Build:` line and scanned the access points around it; an IPRO7AI Reef EVK V4.0 passed `reef selftest` with `ipro7ai_reef_demo` flashed with IntelProCube 0.7.0.1; an IPRO7AI Sensor Tag ran `ipro7ai_sensor_tag_demo` flashed over the board's own USB (from its console and from boot2's downloader, with `tools/ipro_dl.py` and with IPRO Workbench 0.2.0) and streamed its sensors at 20 lines a second.

### Known issues { #v2-3-0-known-issues }

- The [V2.2.0 known issues and notes](#v2-2-0-known-issues) still apply, except that `ipro6_demo/defconfig_ipro6_lpwifi_ping` is no longer in the package; `ipro6_fmac/defconfig_ipro6_fmac_ap` still has no prebuilt library set.
- **Flashing over the board's own USB**: IPRO Workbench 0.2.0 supports it on macOS only. Use IPRO Workbench 0.2.1 or later, which flashes over the board's own USB on Windows 11 too; see [Flash over the board's own USB](../workbench/flash.md#usb-flash).

## IPRO-SDK-V2.2.1 { #v2-2-1 }

Released 2026-11-10 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.1)

Patch release of V2.2.0 with the same 40 FreeRTOS applications. The download is `IPRO-SDK-V2.2.1.tar.gz`; its SHA-256 is on the release page. The rest of the [V2.2.0 notes](#v2-2-0), its known issues included, applies to V2.2.1.

**Fixed**

- **IPRO6S soft-AP**: on parts without a factory MAC address, such as the IPRO6S EVK, `wifi_ap_start` failed without a message. The station and the access point now share one random address per boot, the access point's with the lowest bit flipped. The fix is in the prebuilt `libipro_os_adapter.a` of `ipro6_demo` (`defconfig_ipro6_lpwifi`) and `ipro6_if_wifi` (`defconfig_ipro6_sdio`, `defconfig_ipro6_usb`). The steps are on [IPRO6S](../hardware/chips/ipro6s.md#flashing).
- **`make_reef_ota.sh`** in `ipro_ble_remote` takes the newest boot2 in the IntelProCube folder (v0.6.0 in 0.7.0.1), or the file in `IPRO_BOOT2`; the script no longer needs changing first.
- **Package README**: IntelProCube 0.7.0.1 from GitHub with download and checksum steps, and the IPRO6S EVK flash command (`--chip-variant IPRO6S`, `partition_cfg_fw_direct.toml`).
- **Zephyr**: `zephyr/subsys/net/ipro_wifi/net_al_zephyr.c` matches the L2 socket interface of the lwIP port in the package; IPRO6S is still not supported under Zephyr.

Built and checked from the package before release: the 36 IPRO7 FreeRTOS applications, seven IPRO6S configurations and the Zephyr samples. On the boards: the IPRO6S EVK scans and runs a soft-AP that a computer joins and gets a DHCP lease from, built and flashed on macOS and on Windows; `reef selftest` passes on the IPRO7AI Reef EVK.

### Known issues { #v2-2-1-known-issues }

- **IPRO Workbench 0.1.0 and IPRO6S**: Workbench flashes IPRO6S images without the IPRO6S partition table, and the board does not boot. Use IPRO Workbench 0.1.1 or later (see [IPRO6S EVK](../workbench/flash.md#ipro6s)), or flash IPRO6S with the IntelProCube command line, as on [IPRO6S](../hardware/chips/ipro6s.md#flashing).

## IPRO-SDK-V2.2.0 { #v2-2-0 }

Released 2026-11-03 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0)

Dual-chip release for IPRO7 / IPRO7AI and IPRO6S, replacing V2.1.0. 40 FreeRTOS applications: 37 for IPRO7, 3 for IPRO6S. The download is `IPRO-SDK-V2.2.0.tar.gz`; its SHA-256 is on the release page.

**New and changed**

- **IPRO6S applications are back**: `ipro6_demo` (Wi-Fi station / soft-AP, DTIM low power), `ipro6_if_wifi` (Wi-Fi bridge to a host over SDIO or USB) and `ipro6_fmac` (FullMAC firmware and its flash loader). The Wi-Fi MAC, coexistence and RF libraries are prebuilt once per shipped `defconfig_*`, so each configuration links the libraries built for it. The firmware of the Reef's FIN Wi-Fi card is `ipro6_if_wifi` with `defconfig_ipro6_sdio`; see [IPRO6S](../hardware/chips/ipro6s.md).
- **New application `ipro_reef_teach`**: Edge AI firmware for the IPRO7AI Reef EVK with three Teach tools: `image` (USB camera and classifier), `voice` (who is speaking) and `sensor` (any sensor). One mode is picked at boot, each with its own USB identity, driven from IPRO AI Studio; `tools/teach_web/` does image Teach in the browser. IPRO AI Studio is downloaded from [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest).
- **IPRO Edge AI platform V2.0** in `components/ai`: runtime, a model store with one slot per tool, input sources, preprocessing and an application framework; a bounded NPU wait that resets the block and enters a fail-closed fault state; the Edge AI firmware arms the AON watchdog (download mode turns it off). The CPU layer graph no longer reads past the last layer record.
- **Whole-chip reset**: `hal_reboot_full()` resets the whole chip through the AON watchdog, always-on domain included; with `CONFIG_APP_WATCHDOG`, `platform_init()` arms the watchdog from the start of the boot. `ipro_reef_teach` switches tools with it, which fixes a Reef with a camera hanging on the next boot after leaving `image` mode until it was reset.
- **New application `ipro7_jpeg_decode`**: JPEG to RGB565 / RGB888 in software (TJpgDec), with a format probe and support for camera MJPEG frames without Huffman tables; IPRO7's MJPEG block only encodes. On the Reef use `defconfig_reef`; the console runs at 921600 baud.
- **`ipro7ai_reef_demo`**: `mic usb` turns the Reef into a USB microphone (16 kHz, rate-converted from the PDM clock); `mic sdrec` records WAV files to the SD card.
- **`build_freertos.sh`**: `flash` picks `--chip-variant` from the configuration (`IPRO7AI` for the Reef and the IPRO7AI EVK), overridable with `-c` or `IPRO_CHIP_VARIANT`; `-P` or `IPRO_FLASH_PT` passes a partition table; the `reboot_dl` that `flash` sends, `monitor` and `test` use the application's own console baud rate. See [Tool Command Lines](tools.md#build-cli).
- **BLE controller**: the 16 IPRO7 prebuilt libraries are rebuilt from this release's source; `ipro_ble_ctlr_heap_watermarks()` and `ipro_ble_ctlr_link_diag_start()`, already declared in the header, now link.
- **USB device**: fixes an RX FIFO overflow, detaches on de-init, fixes CDC-ECM framing, and the USB console attaches reliably. **lwIP**: `sys_mbox_trypost` from an interrupt takes the FromISR path. Opus builds against its own `arch.h`.
- **BSP**: PLL-off system clocks for BLE-only applications; `CONFIG_OCRAM_NORET_SCRATCH_ONLY` keeps RAM state inside the PDS-retained 64 KB; `hal_lp_enter_fastboot()` enters HBN; security engine HAL v2 with a PSA accelerator driver.
- The sample applications carry no built-in network credentials.

**Applications**

- 40 in all: 37 for IPRO7, 3 for IPRO6S. Compared with V2.1.0, `ipro_reef_teach`, `ipro7_jpeg_decode`, `ipro6_demo`, `ipro6_if_wifi` and `ipro6_fmac` are new, and the speaker-recognition application of V2.1.0 is renamed `ipro_speaker_recog`.
- Nine applications have configurations for the IPRO7AI Reef EVK; the list and build commands are in the [FAQ](faq.md#reef-apps) and on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples).

Built and checked from the package before release: the 36 IPRO7 FreeRTOS applications (`ipro_agora_sentino` needs the AOSL core first), seven IPRO6S configurations, and the Zephyr samples for `ipro7_evb` and `ipro7ai_evk`.

**Not included**

- The IntelProCube flash tool: download 0.7.0.1 from [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases); see [Set Up Your Host](../get-started/environment.md#intelprocube).
- The RISC-V toolchain: contact INTELPRO.
- IPRO AI Studio, which includes the model converter: download it from [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest).
- An IPRO6S BLE controller library and BLE / BR/EDR applications for IPRO6S; the IPRO6S applications are Wi-Fi only.
- Matter; Thread for FreeRTOS applications (Thread is available under Zephyr).
- Setup for on-target debugging (OpenOCD / GDB), a crash-dump host tool, the board test script, `menuconfig`.
- Zephyr: no Reef board; IPRO6S is not supported; no low-power modes and no drivers for the display, camera, audio codec, USB, SD host, Ethernet or NPU.
- The AOSL core and the Sentino device triple that `ipro_agora_sentino` needs: AOSL comes from GitHub, as the application's README describes.

### Known issues and notes { #v2-2-0-known-issues }

- **Comments in the Reef board header**: the comments in `bsp/board/ipro7/ipro7ai_reef_board_config.h` describe the expansion header and jumpers of the earlier (V3.0) carrier; the pin definitions match V4.0. For the V4.0 header, switches and jumpers, [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) on this site is the reference.
- **Two IPRO6S configurations have no prebuilt library set**: `ipro6_demo/defconfig_ipro6_lpwifi_ping` and `ipro6_fmac/defconfig_ipro6_fmac_ap` ship in the package but do not set `CONFIG_WIRELESS_LIB_VARIANT`, and they are not among the configurations checked for the release. Use the configurations listed on the [IPRO6S](../hardware/chips/ipro6s.md) page.
- **`ipro_le_audio_headset`**: the application's README marks audio rendering as currently disabled and media streaming as not yet validated; read its status section before relying on audio output.
- **`ipro_throughput_test` documents**: the README and `OPERATION_MANUAL.md` mention a demo application, an Android app and controller build options (such as `CONFIG_BTBLECONTROLLER_LIB` and `link8`) that are not in this release; build and flash as in the README's Build / Flash sections and [BLE Throughput Test](../tutorials/ble-throughput.md).
- **Waiting after a crash**: `ipro7ai_reef_demo` and `ipro_reef_teach` set `CONFIG_EXCEPTION_DUMP=y`, so after a crash they keep printing `==DUMP_READY:2000000==` while waiting for a host tool that does not ship; save the diagnostics and press SW2, or set it to `n`. See [Crash analysis](debugging.md#crash-analysis).
- **`build_freertos.sh` flashes IPRO7 only**: it always passes `--chipname ipro7` and cannot pass `--boot2` or `--mfg`; flash IPRO6S images, the OTA build of `ipro_ble_remote` and `ipro_reef_teach` with IntelProCube directly.
- **Items named in READMEs but not shipped**: some component and application READMEs refer to applications, tools or documents that are not in this release (for example the board user guide and the Edge AI programming guide). Documents are available from INTELPRO; see [Documents](../documents/index.md).

## Online Setup 3.6.0 { #tools-3-6-0 }

Released 2026-11-04 · [Download the installer](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.6.0)

The Windows online installer. When it installs SDK V2.2.0 it fixes the SDK's Windows build issues: recognising the IPRO toolchain (the probe compiled `/dev/null`, so every Windows build fell back to the standard GCC flags and the non-DSP prebuilt libraries), the build message that breaks Ninja under CMake 4, and the serial console; it also adds `build_freertos.ps1` for PowerShell. SDK only and Full now install the same SDK, prepared for the toolchain it is built with. An SDK or a toolchain can be added to an existing environment without overwriting anything. The toolchain is still GCC 13.1.1 and the Extension stays at 3.3.0. See [Windows Setup & VS Code](../get-started/windows.md).

## IPRO-SDK-V2.1.0 { #v2-1-0 }

Released 2026-10-16 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0)

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

- IPRO6S applications, BLE controller libraries and `ipro6_rf`: the package README still mentions IPRO6S, but this release has none of it; for IPRO6S development V2.0.1 was the release to use then; from V2.2.0 the IPRO6S applications are back, see [IPRO6S](../hardware/chips/ipro6s.md).
- The IPRO6S-side Wi-Fi firmware, including the Reef's FIN card; contact INTELPRO.
- Matter; Thread for FreeRTOS applications (Thread is available under Zephyr); model conversion tools.
- The IntelProCube flash tool and the RISC-V toolchain, which are obtained separately.

**Known limitations**

- `ipro_ble_remote/defconfig_lowpower` switches the BLE controller to a source build and cannot be built from this package.
- `build_freertos.sh flash` passes neither `--chip-variant` nor `--pt`, and `monitor` always uses 115200 baud; for IPRO7AI boards and 921600-baud applications use the tools directly. Improved in V2.2.0; see [IPRO-SDK-V2.2.0](#v2-2-0).
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

## Online Setup 3.5.0 { #tools-3-5-0 }

Released 2026-09-10 · [Download the installer](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.5.0)

Discovers the official IPRO-SDK releases on every run, accepts `.tar.gz` SDK archives, and prepares the prebuilt libraries for the older Windows linker in full installs.

## IPRO-SDK-V2.0.1 { #v2-0-1 }

Released 2026-09-09 · [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)

Maintenance release for continuous BLE audio, following the V2.0 expansion to IPRO6S and 31 application projects.

- Fixes Bluetooth host queue publication atomicity during sustained transfers.
- PDM recording supports up to 4 logical hours with a 240-second PSRAM ring and automatic 30-second chunks; Android keeps a high connection priority between chunks.
- PDM uses a `link2` controller, a one-connection host and 2M PHY; EVB / EVK configurations and Android companion source are included.
- Adds IPRO6S Wi-Fi / BR/EDR references, both SDIO link endpoints, NPU / TFLM examples and bundled `.inm` / `.tflite` models.
- Includes `ipro_unit_test` and Linux x86-64 CMake; `serial_monitor.py` and `PREBUILT-ARCHIVES-STRIPPED.txt` from 1.2.1 are absent.

The published release reports 31/31 application builds and a five-minute recording test with a Pixel 7a and an IPRO7AI board: ten 960,000-byte chunks, no lost packets or sequence gaps, a successful ring wrap, and steady transfer at 84.2–91.2 KB/s. These results apply to that test setup and are not a guarantee for every board or phone.

## Online Installer 3.4.0 { #tools-3-4-0 }

[Download the installer](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.4.0)

Adds a dynamic public catalog, independent package versions, compatibility selection for full installs, and cached offline installation. The Extension stays at 3.3.0. This version installs only the SDKs registered in its catalog (1.2.1 is stable); to install SDK V2.2.0, use 3.6.0, see [Windows Setup & VS Code](../get-started/windows.md).

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
