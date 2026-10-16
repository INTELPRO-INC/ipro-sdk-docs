---
title: "Zephyr RTOS"
description: The IPRO SDK as a Zephyr v4.4.0 module — supported boards, workspace, flashing and console, features, samples, prebuilt components and limitations
migrate_from:
  - "zephyr-rtos.html#overview"
  - "zephyr-rtos.html#boards"
  - "zephyr-rtos.html#features"
  - "zephyr-rtos.html#samples"
  - "zephyr-rtos.html#prebuilt"
  - "zephyr-rtos.html#limitations"
---

# Zephyr RTOS

<span class="ipro-badge">New in V2.1.0</span>

The IPRO SDK is also a Zephyr v4.4.0 module: the SDK's HAL and SoC drivers are exposed through Zephyr's device driver API, so you can write applications directly on Zephyr. FreeRTOS applications and their build flow are unchanged. Low power, camera, USB, the NPU and some other features are available to FreeRTOS applications only, so check the [limitations](#limitations) before you choose.

!!! abstract "At a glance"
    - Boards: `ipro7_evb` (IPRO7 EVB) and `ipro7ai_evk` (IPRO7AI EVK). The IPRO7AI Reef EVK has no Zephyr board definition.
    - Supported: common peripheral drivers, BLE (Zephyr host + IPRO BLE controller, prebuilt library), IEEE 802.15.4 with OpenThread, MCUboot with MCUmgr updates over BLE.
    - Not supported: low-power modes, and Zephyr drivers for the camera, audio codec, USB, SD host, Ethernet and NPU.
    - Console: UART0 at 2000000 baud.
    - For your first build, follow [First Zephyr Application](../get-started/first-app-zephyr.md).

## Overview { #overview }

| File / directory | Role |
|---|---|
| `west.yml` | The SDK is the west manifest repository: it pins Zephyr v4.4.0 and imports only allow-listed modules |
| `zephyr/module.yml` | Registers the SDK as a Zephyr module (name `ipro_sdk`) with boards, SoC, devicetree and the `west flash` runner |
| `zephyr/boards/`, `soc/`, `dts/` | Board definitions, SoC definition and devicetree bindings |
| `zephyr/drivers/`, `hal_glue/`, `include/` | Zephyr drivers and the glue to the SDK HAL |
| `zephyr/patches.yml`, `patches/` | The SDK's 2 patches to Zephyr, applied when the workspace is created |
| `zephyr/samples/`, `zephyr/tests/` | SDK samples and tests |
| `tools/zephyr/` | Scripts to create the workspace, build, flash and open the console |

The Zephyr drivers sit on top of the SDK HAL, which is compiled straight from `bsp/` rather than copied. BLE uses Zephyr's host with the IPRO BLE controller (prebuilt library); IEEE 802.15.4 uses Zephyr's driver interface and OpenThread.

## Supported boards { #boards }

| Zephyr board | Hardware | Flash (devicetree) | PSRAM | `west flash` defaults |
|---|---|---|---|---|
| `ipro7_evb` | IPRO7 EVB | 2 MB | None | `--pt=partition_cfg_2M.toml`, download mode through the CMSIS-DAP probe |
| `ipro7ai_evk` | IPRO7AI EVK | 1 MB | 8 MB | `--pt=partition_cfg_1M_boot2.toml`, `--boot shell` |

- On both boards the console is on UART0 at 2000000 baud. The IPRO7AI EVK's LCD works through Zephyr's own ST7789V driver.
- The partition table names refer to files under `chips/ipro7/partition/` in IntelProCube.
- The `ipro6s_evb` board files ship with the SDK, but IPRO6S is not supported under Zephyr in this release. For IPRO6S see [IPRO6S (V2.0.1)](../hardware/chips/ipro6s.md).

!!! note "IPRO7AI Reef EVK"
    This release has no Zephyr board definition for the Reef, and the Reef's camera, audio and LED have no devicetree description, so FreeRTOS applications are recommended. The SoC Kconfig help notes that a Reef can run `ipro7_evb` images with `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` (the Reef's RF crystal trim). The `ipro7_evb` devicetree describes a board with 2 MB of flash and no PSRAM; make sure that matches your Reef before relying on it.

## Workspace { #workspace }

`tools/zephyr/bootstrap.sh` creates `zephyr-workspace/` under the SDK root; the first run needs access to GitHub. For the step-by-step procedure see [First Zephyr Application](../get-started/first-app-zephyr.md).

```bash
tools/zephyr/bootstrap.sh              # creates zephyr-workspace/
source zephyr-workspace/env.sh         # ZEPHYR_BASE, CROSS_COMPILE, west
```

The bootstrap script:

1. Creates `.venv` and installs west.
2. Initializes west from the SDK's `west.yml` and runs `west update` (shallow by default; `--full` fetches full history).
3. Applies the patches in `zephyr/patches.yml` with `west patch apply`.
4. Installs the Python packages for Zephyr and MCUboot (imgtool).
5. Writes `env.sh`: `ZEPHYR_TOOLCHAIN_VARIANT=cross-compile`, `CROSS_COMPILE`, `ZEPHYR_BASE`, `PATH`.

| Option / variable | Meaning |
|---|---|
| `-w DIR` | Use another workspace directory |
| `--full` | Fetch Zephyr and the modules in full (shallow by default) |
| `IPRO_TOOLCHAIN` | Toolchain directory, default `/opt/toolchain/riscv_ipro7` |

`west.yml` imports only these modules: `mbedtls`, `tf-psa-crypto`, `openthread`, `picolibc`, `segger`, `mcuboot`, `liblc3`, `zcbor`.

!!! warning "Running bootstrap again"
    Before updating, bootstrap restores the Zephyr files its patches touch to the pinned revision, discarding any local edits to those files.

The SDK samples and tests need CMake 3.20 or later. The CMake bundled in `tools/cmake/` is version 3.15 for Linux x86-64 and cannot be used for Zephyr.

## Flashing and console { #flash-console }

```bash
cd zephyr-workspace
west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke
west flash -d build/smoke
```

`west flash` uses the SDK's `ipro` runner, which writes the image with the IntelProCube command-line tool (download baud rate 2000000). `--boot` selects how the board enters download mode: `probe` (IPRO7 CMSIS-DAP probe, the default on `ipro7_evb`), `shell` (the running firmware's `reboot_dl`, the default on `ipro7ai_evk`) or `manual` (hold BOOT, then reset). For example, without a probe: `west flash -- --boot shell --port /dev/cu.usbserial-XXXX`.

- The flash pin setting comes from IntelProCube's configuration file; `west flash` does not pass `--chip-variant`. See [Flashing & Serial Console](../get-started/flash-and-monitor.md#flash-tool).
- For a sysbuild image with MCUboot, `west flash` first merges MCUboot and the signed application into one FW image with `tools/zephyr/merge_mcuboot.py`, then flashes it.
- The console is UART0 at 2000000 baud: `tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX`.
- `tools/zephyr/flash.sh` sends `reboot_dl` at 115200 baud, which a running Zephyr image does not receive; enter download mode by hand first, or use `west flash`.

Every `west flash` option and the usage of each `tools/zephyr/` script are listed in [Tool Command Lines](../reference/tools.md#zephyr-tools).

## Features { #features }

| Area | Support under Zephyr |
|---|---|
| Drivers | GPIO, UART (including async), SPI, I2C, PWM, ADC, DAC, counter/RTC, watchdog, flash, DMA, entropy, hwinfo, I2S/PDM |
| Display | The IPRO7AI EVK LCD (Zephyr's own ST7789V driver) |
| Bluetooth LE | Zephyr host with the IPRO BLE controller (prebuilt library, the same `components/wireless/bluetooth/ipro_ble_controller/lib/` as FreeRTOS) |
| IEEE 802.15.4 / Thread | Zephyr's IEEE 802.15.4 driver and OpenThread; see [Thread & Matter](thread-matter.md) |
| Boot and update | MCUboot through sysbuild; image upload over BLE with MCUmgr SMP; see [OTA Updates](ota.md) |

Under Zephyr the BLE controller is selected with these keys, and a devicetree overlay must enable the `bt_hci` node (`zephyr/samples/bt_peripheral_hr/ipro7.overlay`):

```ini title="zephyr/samples/bt_peripheral_hr/ipro7.conf"
CONFIG_IPRO7_EM_SIZE_KB=16
CONFIG_BT_IPRO_CTLR_LIB="link1_periph"
CONFIG_BT_IPRO_CTLR_FEATURE="bt52"
CONFIG_BT_MAX_CONN=1
CONFIG_ENTROPY_GENERATOR=y
```

For ISO and LE Audio use `zephyr/samples/bt_le_audio/iso.conf` (`link1`, `bt54_iso2`, `CONFIG_IPRO7_EM_SIZE_KB=32`). Controller variants are explained in [BLE Development](ble.md).

## Samples { #samples }

| Sample (`zephyr/samples/`) | Boards | What it does |
|---|---|---|
| `periph_smoke` | `ipro7_evb` | Exercises each driver (GPIO, UART, SPI, I2C, PWM, flash, DMA, counter, watchdog, TRNG) |
| `mcuboot_app` | `ipro7_evb`, `ipro7ai_evk` | Proves the boot chain boot2 → MCUboot → image-0 |
| `ble_ota` | `ipro7_evb`, `ipro7ai_evk` | MCUboot + MCUmgr SMP, updated over BLE |
| `bap_broadcast_source` | `ipro7_evb`, `ipro7ai_evk` | LE Audio broadcast source (LC3) |
| `bap_broadcast_sink` | `ipro7ai_evk` | LE Audio broadcast sink, played on the EVK speaker |
| `le_audio_headset` | `ipro7ai_evk` | LE Audio unicast headset (CAP acceptor) |
| `evk_demo` | `ipro7ai_evk` | `evk` shell commands for the LCD, microphone and speaker; camera preview needs `CONFIG_EVK_DEMO_CAMERA=y` |
| `ieee802154_shell` | `ipro7_evb` | IEEE 802.15.4 shell; also carries `ot.conf` and `csl.conf` for OpenThread |
| `bt_peripheral_hr`, `bt_le_audio` | – | Configuration fragments for Zephyr's own samples |

Zephyr's own samples with the SDK fragments (run in `zephyr-workspace/`):

```bash
west build -b ipro7_evb zephyr/samples/bluetooth/peripheral_hr -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.overlay
west build -b ipro7_evb zephyr/samples/net/openthread/shell -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/ieee802154_shell/ot.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/ieee802154_shell/app.overlay
```

`zephyr/tests/` holds 15 driver test suites (`zephyr/tests/drivers/`) and 3 SoC suites (`camclk`, `psram`, `reboot`), written as standard Zephyr ztest suites.

## Prebuilt components { #prebuilt }

In a Zephyr build, all SDK code including the HAL is compiled from source except:

| Component | Location |
|---|---|
| IPRO BLE controller | `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| RF driver | `components/wireless/rf/ipro7_rf/lib/zephyr/` (`libipro_rf_core.a`, `libipro_rf_core_short_enums.a`) |
| IEEE 802.15.4 MAC | `components/wireless/ieee802154/lib/zephyr/` (`libipro_ieee802154_core.a`, `libipro_ieee802154_core_short_enums.a`) |

When the BLE controller is linked, the whole image is compiled with `-fshort-enums`, and the build picks the matching RF and 802.15.4 library variants automatically.

## Limitations in this release { #limitations }

- Low-power modes: Zephyr's `pm_state` does not enter PDS or HBN, and the BLE controller does not sleep either. For low power use FreeRTOS; see [Low Power](low-power.md).
- No Zephyr drivers for the camera, audio codec, USB, SD host, Ethernet or NPU; the only display is the IPRO7AI EVK LCD (ST7789V). The camera preview in `evk_demo` uses the SDK HAL directly inside the sample.
- IPRO7 has no Wi-Fi under Zephyr; `zephyr/drivers/wifi` is the IPRO6S driver, which this release does not support.
- No IPRO7AI Reef EVK board definition; IPRO6S is not supported.
- For these features, use FreeRTOS applications.

## Related documents { #related }

- [First Zephyr Application](../get-started/first-app-zephyr.md): creating the workspace, building and flashing step by step.
- [Thread & Matter](thread-matter.md): OpenThread configuration and a first test.
- [OTA Updates](ota.md): MCUboot and MCUmgr.
- [BLE Development](ble.md): controller variants and the BLE API.
