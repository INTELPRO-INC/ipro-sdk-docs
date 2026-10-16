---
title: "First Zephyr Application"
description: Create the Zephyr workspace, then build hello_world for the IPRO7 EVB or IPRO7AI EVK and flash it with west flash.
migrate_from:
  - "getting-started.html#zephyr-quickstart"
  - "zephyr-rtos.html#setup"
  - "zephyr-rtos.html#build-flash"
---

# First Zephyr Application

Create the Zephyr workspace, build Zephyr's `hello_world` for the IPRO7 EVB (`ipro7_evb`) or the IPRO7AI EVK (`ipro7ai_evk`), flash it with `west flash` and see its output on the console.

!!! info "IPRO7AI Reef EVK"
    V2.1.0 has no Zephyr board definition for the IPRO7AI Reef EVK. On the Reef, use the [FreeRTOS application](first-app-freertos.md).

## Prerequisites { #prerequisites }

- macOS or Linux: the scripts in `tools/zephyr/` need bash.
- The RISC-V toolchain, by default in `/opt/toolchain/riscv_ipro7`: not included in V2.1.0; contact INTELPRO.
- The host tools for Zephyr v4.4.0: CMake 3.20 or later, Python 3 with venv, git, and the other tools Zephyr requires (such as Ninja and dtc), as listed in Zephyr's [Getting Started Guide](https://docs.zephyrproject.org/latest/develop/getting_started/index.html).
- Access to GitHub the first time you create the workspace.
- The IntelProCube command-line tool, found through `IPRO_FLASH_TOOL` or PATH (see [macOS / Linux Command Line](command-line.md#installation)).
- One way to put the board into download mode: an IPRO7 CMSIS-DAP probe, firmware with a shell already running on the board, or by hand.

## Create the workspace { #setup }

<div class="ipro-steps" markdown>

1. **Run the bootstrap script** from the SDK root. It creates a Python venv with west in `zephyr-workspace/`, downloads Zephyr v4.4.0 and the modules listed in `west.yml`, applies the patches in `zephyr/patches.yml`, and writes `env.sh`.

    ```bash
    tools/zephyr/bootstrap.sh
    ```

    If the toolchain is not at the default path, set `IPRO_TOOLCHAIN=<toolchain dir>` first; add `-w <dir>` to put the workspace elsewhere. The script ends with `[bootstrap] done.`.

2. **Load the environment** once in every new terminal. `env.sh` sets `ZEPHYR_BASE` and `CROSS_COMPILE` and puts west on PATH.

    ```bash
    source zephyr-workspace/env.sh
    cd zephyr-workspace
    ```

</div>

## Build and flash { #build-flash }

<div class="ipro-steps" markdown>

1. **Build** from `zephyr-workspace/`.

    === "IPRO7 EVB"

        ```bash
        west build -b ipro7_evb zephyr/samples/hello_world
        ```

    === "IPRO7AI EVK"

        ```bash
        west build -b ipro7ai_evk zephyr/samples/hello_world
        ```

    The image is `build/zephyr/zephyr.bin`. The SDK's own samples are one level up in `zephyr/samples/`, for example:

    ```bash
    west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke
    ```

2. **Flash**: `west flash` puts the board into download mode, then writes the image with the IntelProCube command-line tool. The partition table comes from `chips/ipro7/partition/` in the tool's directory: `partition_cfg_2M.toml` for `ipro7_evb` and `partition_cfg_1M_boot2.toml` for `ipro7ai_evk`. `--boot` selects how the board enters download mode:

    | `--boot` | How | Board default |
    |---|---|---|
    | `probe` | The IPRO7 CMSIS-DAP probe drives BOOT and reset | `ipro7_evb` |
    | `shell` | Sends `reboot_dl` on the console; the board must be running firmware with a shell | `ipro7ai_evk` |
    | `manual` | You put the board into download mode when prompted, then press Enter (for the IPRO7AI EVK, see its board page) | — |

    ```bash
    west flash                                   # board default
    west flash -- --boot manual                  # no probe: enter download mode by hand
    west flash -- --boot shell --port /dev/cu.usbserial-XXXX
    ```

    `--boot shell` sends `reboot_dl` at `--console-baud` (default 2000000, the Zephyr console rate). If the board is running a FreeRTOS application, pass that application's rate instead, for example `--console-baud 115200`. Give the port with `--port` or `IPRO_SERIAL_PORT`; with a single USB serial port connected it is picked automatically. `west flash` passes no `--chip-variant`, so the tool uses its current `flash_pin` setting; see [Flash tool](flash-and-monitor.md#flash-tool).

3. **Open the console**: the Zephyr console is on UART0 at 2000000 baud.

    ```bash
    ../tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX
    ```

    `monitor.sh` reads through `tools/serial_monitor.py` until you press ++ctrl+c++.

</div>

## Verify { #verify }

After a reset, the console shows the Zephyr boot banner, then a line that starts with `Hello World!` followed by the board name. Images for `ipro7_evb` and `ipro7ai_evk` include the shell and its `reboot_dl` command by default, so from now on you can reflash with `west flash -- --boot shell`.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| bootstrap reports `could not create a venv with pip` | Python venv is missing | Install `python3-venv` or `virtualenv` |
| `no ipro_iot_tool found` | The flash tool cannot be found | Set `IPRO_FLASH_TOOL`, or add the IntelProCube directory to PATH |
| `several serial ports, pass --port or set IPRO_SERIAL_PORT` | More than one USB serial port is connected | Use `--port` or `IPRO_SERIAL_PORT` |
| `partition table not found` | There is no `chips/ipro7/partition/` next to the tool | Point `IPRO_FLASH_TOOL` at the tool inside the IntelProCube directory |
| `flashing failed (is the board in download mode? …)` | The board did not enter download mode | Without a probe, use `--boot shell` (needs a shell on the board) or `--boot manual` |
| Flashing succeeds but the console is silent | The rate is not 2000000, or the board is still in download mode | Open the console with `monitor.sh` (2000000 by default); press the board's reset button |
| `tools/zephyr/flash.sh` cannot put a running Zephyr image into download mode | The script sends `reboot_dl` at 115200, while the Zephyr console runs at 2000000 | Use `west flash -- --boot shell` instead |
| You need low power, display, camera, audio codec, USB, SD, Ethernet or NPU | Zephyr in this release has no such modes or drivers yet; the IPRO7AI EVK LCD works through Zephyr's own ST7789V driver | Use a FreeRTOS application |

## Next steps { #next-steps }

- [Zephyr RTOS](../guides/zephyr.md): supported drivers, SDK samples, BLE and 802.15.4.
- [Flashing & Serial Console](flash-and-monitor.md): flash tool options and per-board settings.
- [First FreeRTOS Application](first-app-freertos.md)
