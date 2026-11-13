---
title: "Zephyr RTOS"
description: The IPRO SDK as a Zephyr v4.4.0 module — boards, workspace, building and flashing with west, samples, prebuilt components and what Zephyr does not cover in this release
migrate_from:
  - "zephyr-rtos.html#overview"
  - "zephyr-rtos.html#boards"
  - "zephyr-rtos.html#features"
  - "zephyr-rtos.html#samples"
  - "zephyr-rtos.html#prebuilt"
  - "zephyr-rtos.html#limitations"
  - "getting-started.html#zephyr-quickstart"
  - "zephyr-rtos.html#setup"
  - "zephyr-rtos.html#build-flash"
---

# Zephyr RTOS

The IPRO SDK is also a Zephyr v4.4.0 module: the SDK's HAL and SoC drivers sit behind Zephyr's device driver API, so you can write applications on Zephyr instead of FreeRTOS. This page is the reference for the Zephyr side: boards, workspace, `west` build and flash, samples and limits. The FreeRTOS applications and their build are unchanged.

!!! abstract "At a glance"
    - Boards: `ipro7_evb` (IPRO7 EVB) and `ipro7ai_evk` (IPRO7AI EVK). **V2.3.0 has no Zephyr board definition for the IPRO7AI Reef EVK**; on the Reef, use the FreeRTOS applications.
    - Available: the common peripheral drivers, BLE (Zephyr host on the prebuilt IPRO BLE controller), IEEE 802.15.4 with OpenThread, MCUboot with MCUmgr updates over BLE.
    - Not available: low-power modes, and Zephyr drivers for the camera, audio codec, USB, SD host, Ethernet and NPU.
    - Console: UART0 at 2,000,000 baud. Host needs: Python 3 with venv, git, network access to GitHub, CMake 3.20 or later.
    - First build: [Workspace](#workspace), then [Building, flashing and console](#flash-console).

## Overview { #overview }

| File / directory | Role |
|---|---|
| `west.yml` | The SDK is the west manifest repository: it pins Zephyr v4.4.0 and imports only allow-listed modules |
| `zephyr/module.yml` | Registers the SDK as a Zephyr module with its boards, SoC, devicetree bindings and the `west flash` runner |
| `zephyr/boards/`, `soc/`, `dts/` | Board definitions, SoC definition, devicetree bindings |
| `zephyr/drivers/`, `hal_glue/`, `include/` | Zephyr drivers and their glue to the SDK HAL |
| `zephyr/patches.yml`, `patches/` | The SDK's two patches to Zephyr, applied when the workspace is created |
| `zephyr/samples/`, `zephyr/tests/` | SDK samples and test suites |
| `tools/zephyr/` | Scripts to create the workspace, build, flash and open the console |

The Zephyr drivers call the SDK HAL, which is compiled straight from `bsp/`. BLE uses Zephyr's host with the IPRO BLE controller archives; IEEE 802.15.4 uses Zephyr's driver interface and OpenThread.

## Supported boards { #boards }

| Zephyr board | Hardware | Flash (devicetree) | PSRAM | `west flash` defaults |
|---|---|---|---|---|
| `ipro7_evb` | IPRO7 EVB | 2 MB | None | `--pt=partition_cfg_2M.toml`, download mode through the IPRO7 CMSIS-DAP probe |
| `ipro7ai_evk` | IPRO7AI EVK | 1 MB | 8 MB | `--pt=partition_cfg_1M_boot2.toml`, `--boot=shell` |

- Both boards put the console on UART0 at 2,000,000 baud.
- The partition table names refer to files under `chips/ipro7/partition/` in IntelProCube.
- The `ipro6s_evb` board files ship with the SDK, but IPRO6S is not supported under Zephyr in this release.

!!! info "IPRO7AI Reef EVK"
    V2.3.0 has no Zephyr board for the Reef and no devicetree for its camera, audio, LED or microSD socket. Running Zephyr images on the Reef has not been validated for this release. Contact INTELPRO if you need Zephyr on the Reef.

## Workspace { #workspace }

`tools/zephyr/bootstrap.sh` creates `zephyr-workspace/` in the SDK root. The first run downloads Zephyr and its modules from GitHub.

```bash
tools/zephyr/bootstrap.sh              # creates zephyr-workspace/
source zephyr-workspace/env.sh         # ZEPHYR_BASE, CROSS_COMPILE, west on PATH
```

The script:

1. Creates `zephyr-workspace/.venv` and installs west.
2. Initializes west from the SDK's `west.yml` and runs `west update` (shallow by default).
3. Applies the patches in `zephyr/patches.yml`.
4. Installs the Python requirements of Zephyr and MCUboot.
5. Writes `env.sh`: `ZEPHYR_TOOLCHAIN_VARIANT=cross-compile`, `CROSS_COMPILE`, `ZEPHYR_BASE`, `PATH`.

| Option / variable | Meaning |
|---|---|
| `-w DIR` | Use another workspace directory |
| `--full` | Fetch Zephyr and the modules with full history |
| `IPRO_TOOLCHAIN` | Toolchain directory, default `/opt/toolchain/riscv_ipro7` |

`west.yml` imports only `mbedtls`, `tf-psa-crypto`, `openthread`, `picolibc`, `segger`, `mcuboot`, `liblc3` and `zcbor`.

!!! warning "Running bootstrap again"
    Before updating, bootstrap restores the Zephyr files its patches touch to the pinned revision, discarding local edits to those files.

Zephyr needs CMake 3.20 or later. The CMake in `tools/cmake/` is 3.15 for Linux x86-64 and serves only the FreeRTOS build.

## Building, flashing and console { #flash-console }

Run these in `zephyr-workspace/` after `source env.sh`:

```bash
west build -b ipro7_evb zephyr/samples/hello_world                       # a Zephyr sample
west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke     # an SDK sample
west flash -d build/smoke
../tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX                  # console, 2,000,000 baud
```

From the SDK root, `tools/zephyr/build.sh [-b ipro7_evb|ipro7ai_evk] [-d DIR] [-p] APP [-- cmake args]` wraps `west build` and accepts an SDK sample by name (`tools/zephyr/build.sh -b ipro7ai_evk periph_smoke`).

`west flash` uses the SDK's `ipro` runner (`zephyr/scripts/runners/ipro.py`): it puts the board in download mode, writes `zephyr.bin` with the IntelProCube command-line tool and resets the board.

| Runner option | Meaning |
|---|---|
| `--boot probe` / `shell` / `manual` | How the board enters download mode: IPRO7 CMSIS-DAP probe (default), the running image's `reboot_dl`, or by hand |
| `--port`, `--probe-port` | Flash UART and probe bridge port; defaults `$IPRO_SERIAL_PORT`, `$IPRO_PROBE_PORT` |
| `--tool` | IntelProCube CLI binary; default `$IPRO_FLASH_TOOL`, or the tool on `PATH` |
| `--pt` | Partition table: a `.toml` path or a table name under the tool's `chips/<chip>/partition/` |
| `--baudrate`, `--console-baud` | Flash baud and console baud for `--boot shell`; both 2000000 by default |
| `--no-reset`, `--attempts`, `--tool-arg` | Stay in download mode; retries (3); extra argument for the tool |

Pass runner options after `--`, for example `west flash -- --boot shell --port /dev/cu.usbserial-XXXX`.

- `west flash` does not pass `--chip-variant`; IntelProCube uses the flash-pin setting stored in its `chips/ipro7/eflash_loader/eflash_loader_cfg.ini`.
- For a sysbuild image with MCUboot, `west flash` first merges MCUboot and the signed application into one image with `tools/zephyr/merge_mcuboot.py`.
- `tools/zephyr/flash.sh` sends `reboot_dl` at 115200 baud, which a running Zephyr image (2,000,000 baud) does not receive; enter download mode by hand first, or use `west flash`.

## Features { #features }

| Area | Under Zephyr |
|---|---|
| Drivers | GPIO, UART (including async), SPI, I2C, PWM, ADC, DAC, counter/RTC, watchdog, flash, DMA, entropy, hwinfo, I2S/PDM |
| Display | The IPRO7AI EVK LCD, through Zephyr's own ST7789V driver |
| Bluetooth LE | Zephyr host on the IPRO BLE controller archives in `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| IEEE 802.15.4 / Thread | Zephyr's IEEE 802.15.4 driver and OpenThread; see [Thread & Matter](thread-matter.md) |
| Boot and update | MCUboot through sysbuild; image upload over BLE with MCUmgr SMP; see [OTA Updates](ota.md) |

Under Zephyr the BLE controller archive is selected with these keys, and a devicetree overlay enables the `bt_hci` node (`zephyr/samples/bt_peripheral_hr/ipro7.overlay`):

```ini title="zephyr/samples/bt_peripheral_hr/ipro7.conf (excerpt)"
CONFIG_IPRO7_EM_SIZE_KB=16
CONFIG_BT_IPRO_CTLR_LIB="link1_periph"
CONFIG_BT_IPRO_CTLR_FEATURE="bt52"
CONFIG_BT_MAX_CONN=1
CONFIG_ENTROPY_GENERATOR=y
```

For ISO and LE Audio use `zephyr/samples/bt_le_audio/iso.conf` (`link1`, `bt54_iso2`, `CONFIG_IPRO7_EM_SIZE_KB=32`). The archive matrix is explained in [BLE Development](ble.md).

## Samples { #samples }

| Sample (`zephyr/samples/`) | Boards | What it does |
|---|---|---|
| `periph_smoke` | `ipro7_evb` | Exercises each driver: GPIO, UART, SPI, I2C, PWM, flash, DMA, counter, watchdog, TRNG |
| `mcuboot_app` | `ipro7_evb`, `ipro7ai_evk` | Proves the boot chain boot2 → MCUboot → image |
| `ble_ota` | `ipro7_evb`, `ipro7ai_evk` | MCUboot + MCUmgr SMP, updated over BLE |
| `bap_broadcast_source` | `ipro7_evb`, `ipro7ai_evk` | LE Audio broadcast source (LC3) |
| `bap_broadcast_sink` | `ipro7ai_evk` | LE Audio broadcast sink, played on the EVK speaker |
| `le_audio_headset` | `ipro7ai_evk` | LE Audio unicast headset (CAP acceptor) |
| `evk_demo` | `ipro7ai_evk` | `evk` shell commands for the EVK's LCD, microphone, speaker and camera preview |
| `ieee802154_shell` | `ipro7_evb` | IEEE 802.15.4 shell; also carries `ot.conf` and `csl.conf` for OpenThread |
| `bt_peripheral_hr`, `bt_le_audio` | – | Configuration fragments for Zephyr's own samples |

Zephyr's own samples with the SDK fragments (in `zephyr-workspace/`):

```bash
west build -b ipro7_evb zephyr/samples/bluetooth/peripheral_hr -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.overlay
west build -b ipro7_evb zephyr/samples/net/openthread/shell -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/ieee802154_shell/ot.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/ieee802154_shell/app.overlay
```

`zephyr/tests/` holds 15 driver suites (`zephyr/tests/drivers/`) and 3 SoC suites (`camclk`, `psram`, `reboot`), written as standard ztest suites.

## Prebuilt components { #prebuilt }

A Zephyr build compiles all SDK code, including the HAL, from source except:

| Component | Location |
|---|---|
| IPRO BLE controller | `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| RF driver | `components/wireless/rf/ipro7_rf/lib/zephyr/` (`libipro_rf_core.a`, `libipro_rf_core_short_enums.a`) |
| IEEE 802.15.4 MAC | `components/wireless/ieee802154/lib/zephyr/` (`libipro_ieee802154_core.a`, `libipro_ieee802154_core_short_enums.a`) |

When the BLE controller is linked, the whole image is compiled with `-fshort-enums`, and the build picks the matching RF and 802.15.4 variants.

## Limitations in this release { #limitations }

- No Zephyr board for the IPRO7AI Reef EVK; IPRO6S is not supported under Zephyr.
- Low-power modes: Zephyr's `pm_state` does not enter PDS or HBN, and the BLE controller does not sleep. For low power, use FreeRTOS; see [Low Power](low-power.md).
- No Zephyr drivers for the camera, audio codec, USB, SD host, Ethernet or NPU; the only display is the IPRO7AI EVK LCD.
- No Wi-Fi for IPRO7 under Zephyr: `zephyr/drivers/wifi` is the IPRO6S on-chip driver.
- Products that need these features use the FreeRTOS applications.

## Related documents { #related }

- [Thread & Matter](thread-matter.md): OpenThread configuration and a first test.
- [OTA Updates](ota.md): MCUboot and MCUmgr.
- [BLE Development](ble.md): controller archives and the BLE API.
- [Tool Command Lines](../reference/tools.md): the `tools/zephyr/` scripts.
