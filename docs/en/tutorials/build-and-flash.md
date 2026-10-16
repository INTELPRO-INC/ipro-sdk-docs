---
title: "Build and Flash Workflow"
description: The day-to-day build, flash and monitor loop, covering build_freertos.sh action chains, DEFCONFIG variants, clean builds, reading memory usage and working around the script's defaults.
migrate_from:
  - "tutorials.html — 教學 2"
---

# Build and Flash Workflow

Run the loop you repeat all day — edit, build, flash, watch the console — using `ipro7ai_reef_demo`, the out-of-box firmware of the IPRO7AI Reef EVK, as the example. For the first-time setup and first flash, see [First FreeRTOS Application](../get-started/first-app-freertos.md) and [Flashing & Serial Console](../get-started/flash-and-monitor.md).

## Prerequisites { #prerequisites }

- First FreeRTOS application done: the toolchain is in `/opt/toolchain/riscv_ipro7/` and `make` builds SDK applications.
- The IntelProCube v0.6.3 command-line flash tool, obtained separately. Set `IPRO_FLASH_TOOL` to the tool's path, or add the tool's directory to `PATH`.
- An IPRO7AI Reef EVK, powered, with a USB-to-UART cable on U6.
- Run every command below from the SDK root.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Set the serial port**: `build_freertos.sh` takes the `-p` option, then the `IPRO_SERIAL_PORT` environment variable, then the only USB serial port on the system. With several boards attached, name the port:

    === "macOS"

        ```bash
        export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
        ```

    === "Linux"

        ```bash
        export IPRO_SERIAL_PORT=/dev/ttyUSB0
        ```

2. **Find the project name**:

    ```bash
    ./build_freertos.sh -l
    ```

    Projects are listed by category (excerpt):

    ```text
    bluetooth/ble
      ipro_ble_hid_keyboard
      ipro_ble_remote
      ipro_ble_transparent
      ipro_throughput_test

    platform
      ...
      ipro7ai_reef_demo                   IPRO7AI Reef carrier board demo.
    ```

    The text next to a name is the first comment line of its `.config`; most projects have none. The script accepts the project name (`ipro7ai_reef_demo`) or the category path (`platform/ipro7ai_reef_demo`); `make -C` needs the full path `apps/platform/ipro7ai_reef_demo`.

3. **Build and check memory usage**:

    ```bash
    ./build_freertos.sh build ipro7ai_reef_demo
    ```

    ```text
    ✓ Build succeeded (12s)
      Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (219 KB)
      Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
    ```

    The full build output goes to `build.log`. Show the linker's memory usage table (explained under [Reading memory usage](#memory-usage)):

    ```bash
    grep -A5 "Memory region" apps/platform/ipro7ai_reef_demo/build/build.log
    ```

4. **Flash**: put the Reef in download mode (type `reboot_dl` at the console, or hold SW1, tap SW2 and release SW1), then run from the IntelProCube directory (macOS shown; the Linux and Windows commands are in [Flashing & Serial Console](../get-started/flash-and-monitor.md#flashing)):

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    Check the output for `[All Success]`; the tool exits with 0 even when it fails. On the Reef, do not use the script's `flash` action — see [Script defaults](#script-defaults).

5. **Watch the console**:

    ```bash
    ./build_freertos.sh monitor -t 0 ipro7ai_reef_demo
    ```

    `monitor` sends `reboot` first, so the board restarts and you see the whole boot log; `-t 0` keeps the output coming until you press Ctrl+C. This view is output only; to type shell commands, use a terminal program (see [Flashing & Serial Console](../get-started/flash-and-monitor.md)).

6. **Iterate**: after each code change, repeat steps 3 to 5. Chained actions run in order and stop at the first failure:

    ```bash
    ./build_freertos.sh build size ipro7ai_reef_demo
    ```

</div>

## Verify { #verify }

- `build` prints `✓ Build succeeded` and the `Binary:` path; `build.log` contains the memory usage table.
- The flash tool's output contains `[All Success]`.
- `monitor` shows the boot messages of the new firmware.

## build_freertos.sh actions and options { #actions }

Usage: `./build_freertos.sh [actions...] [options] <project>`; without an action it runs `build`. This tutorial uses the `build`, `monitor`, `size` and `clean` actions, plus `-d` (alternate configuration), `-t 0` (keep `monitor` running until Ctrl+C) and `-p` (serial port). Actions run in order and stop at the first failure; with several actions the script ends with a per-action summary. Every action and option is listed in [Tool Command Lines](../reference/tools.md#build-cli).

## Variants and build directories { #variants }

Every application builds from the `.config` in its directory. Select an alternate configuration with `DEFCONFIG=` or `build_freertos.sh -d`; it builds in `build_<name>/` and leaves `.config` untouched:

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # builds in build_wifi_ipro6s/
./build_freertos.sh build -d defconfig_wifi_ipro6s ipro7ai_reef_demo       # same
```

- Each build copies the alternate configuration to `build_<name>/.config`, so edit the original file in the application directory, not the copy in the build directory.
- The directory naming rule, `BOARD=`, and the configuration files you copy over `.config` (`DAC.config` and `UAC.config` of `ipro_le_audio_headset`) are covered in [Build System & Configuration](../guides/build-system.md#variants); which applications ship which alternate configurations is listed under [Examples](../examples/index.md).

## Clean builds { #clean-build }

Do a clean build after changing `.config` or an alternate configuration, especially flash size, PSRAM, `CONFIG_EM_SIZE`, the controller library or AI options, and after switching `.config` by copying a file over it. `clean` deletes only the matching build directory:

```bash
# Default configuration: deletes build/
make -C apps/platform/ipro7ai_reef_demo clean
# Alternate configuration: deletes build_wifi_ipro6s/
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s clean
# Clean and rebuild in one go with the script
./build_freertos.sh clean build -d defconfig_wifi_ipro6s ipro7ai_reef_demo
```

Each build also copies `compile_commands.json` to the SDK root for your editor's code index.

## Reading memory usage { #memory-usage }

The link step prints how much of each memory region the image uses. This is the default configuration of `ipro7ai_reef_demo`:

```text
Memory region         Used Size  Region Size  %age Used
           flash:      224792 B         1 MB     21.44%
           psram:       36064 B         8 MB      0.43%
           ocram:       31248 B       256 KB     11.92%
          hbnram:        2460 B         4 KB     60.06%
```

- `flash` is the link limit for the whole flash (1 MB by default), not the size of the firmware partition in your partition table, so a `flash` percentage below 100 % does not mean the image fits that partition. Compare the `.bin` size shown by `Binary:` with the firmware partition of the partition table you flash with.
- `ocram` is 256 KB minus `CONFIG_EM_SIZE`. For example, the Reef configuration of `ipro_throughput_test` sets `CONFIG_EM_SIZE=32`, so its `ocram` region is 224 KB, of which it uses 205 KB. Which settings size each region is described in [Build System & Configuration](../guides/build-system.md#memory-layout).
- The configure step also prints the layout it chose, for example `-- IPRO7 flash: 1M (default, on-chip)` and `-- AI disabled: OCRAM=256KB`.
- With `make`, the table appears in your terminal; with `build_freertos.sh` it goes to `build.log` and shows on screen only with `-v`. The `size` action lists section sizes as well.

## Script defaults { #script-defaults }

The `flash` and `monitor` actions of `build_freertos.sh` use fixed parameters: `flash` sends `reboot_dl` at 115200 baud and passes only `--chipname ipro7 --port --firmware --baudrate 921600`, with no `--chip-variant`, `--pt` or `--boot2`; `monitor` always opens at 115200 baud and sends `reboot` first. So:

- On the Reef, run the flash tool directly as in [step 4](#steps); if the running firmware does not take `reboot_dl`, hold SW1, tap SW2 and release SW1 to enter download mode.
- For applications with a 921600-baud console (see the Console column under [Examples](../examples/index.md)), use `python3 tools/serial_monitor.py <port> --baud 921600 --timeout 0`.
- Make `monitor` the last action: when it ends on a timeout or Ctrl+C, the script records it as failed and skips the actions after it.

The full explanation is in [Flashing & Serial Console](../get-started/flash-and-monitor.md#build-script).

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `Project '…' not found. Did you mean:` | Incomplete name | Use the full name shown by `-l` |
| `Multiple projects match` | The same name exists in several categories | Use the category path, for example `platform/ipro7ai_reef_demo` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | More than one USB serial port is attached | Add `-p` or set `IPRO_SERIAL_PORT` |
| `Flash tool not found` | The IntelProCube command-line tool is not found | Set `IPRO_FLASH_TOOL` or add the tool's directory to `PATH` |
| After a build with `-d`, a later `flash` or `size` reports `Binary not found` or `ELF not found` | Without `-d` the script looks in `build/` | Pass the same `-d` again |
| `No cmake found` | No CMake on the system; the bundled `tools/cmake/` is a Linux x86-64 build | Install CMake 3.19 or later |
| No `[All Success]` in the flash tool's output | The board is not in download mode, or `--chip-variant` is wrong | Enter download mode again; use `IPRO7AI` for the Reef and the IPRO7AI EVK |
| Garbage on the console | Baud rate mismatch | Use the application's `CONFIG_PLATFORM_UART_BAUDRATE` (115200 when unset) |

## Next steps { #next-steps }

- [Build System & Configuration](../guides/build-system.md): `.config` keys, creating a new application and linker scripts.
- [Your First BLE Application](first-ble-app.md): use the same loop on a BLE application.
- [Tool Command Lines](../reference/tools.md): all options of the flash tool and the serial tools.
