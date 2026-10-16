---
title: "Tool Command Lines"
description: Commands, options and examples for the host tools that ship with the SDK — build_freertos.sh, make, the IntelProCube flash tool, serial_monitor.py, create_ota.py, tools/zephyr and size analysis.
migrate_from:
  - "tools-debugging.html#overview"
  - "tools-debugging.html#build-cli"
  - "tools-debugging.html#zephyr-tools"
  - "tools-debugging.html#automated-testing"
  - "tools-debugging.html#size-analysis"
  - "tools-debugging.html#dev-workflow"
---

# Tool Command Lines

Command syntax, options and examples for the host tools that ship with the SDK. For step-by-step flashing and console use, see [Flashing & Serial Console](../get-started/flash-and-monitor.md). Where an example needs a board, it uses the IPRO7AI Reef EVK.

## Tools at a glance { #overview }

| Tool | Path | Purpose | V2.1.0 |
|---|---|---|---|
| `build_freertos.sh` | SDK root | Build, clean, flash, console, size report and automated test for FreeRTOS applications | Included |
| `make` + `project.build` | each application's `Makefile` | Build one application | Included |
| `serial_monitor.py` | `tools/` | Read the console; optionally send one command first, wait for a pattern and save a log (macOS, Linux) | Included |
| `create_ota.py` | `tools/` | Build a boot2 OTA package | Included |
| Zephyr scripts | `tools/zephyr/` | Zephyr workspace, build, flash, console and sample matrix | Included |
| `parse_kconfig_dynamic.py` | `tools/script/` | Export a Kconfig tree as JSON (needs kconfiglib; not used by the build) | Included |
| CMake 3.15 | `tools/cmake/` | Linux x86-64 only; does not run on macOS | Included |
| Android sample app source | `tools/android/IproMicDemo/` | Android Studio project for `ipro_pdm_mic_demo` | Included |
| IntelProCube v0.6.3 command-line flasher | `ipro_iot_tool_macos`, `ipro_iot_tool_linux`, `ipro_iot_tool.exe` | Flash firmware over the serial port | Not included in V2.1.0; contact INTELPRO |
| RISC-V toolchain | `/opt/toolchain/riscv_ipro7/` | Compiler (GCC, `riscv64-unknown-elf-`) | Not included in V2.1.0; contact INTELPRO |
| Board test script, crash address parser, OpenOCD configuration | — | — | Not included in V2.1.0; contact INTELPRO |

## Environment variables { #environment }

| Variable | Used by | Effect |
|---|---|---|
| `IPRO_FLASH_TOOL` | `build_freertos.sh`, `tools/zephyr/flash.sh`, `west flash`, per-application `flash.sh` | Path to the IntelProCube command-line tool. When unset, the tool name for your OS is looked up on `PATH` |
| `IPRO_SERIAL_PORT` | `build_freertos.sh`, `tools/zephyr/flash.sh`, `monitor.sh`, `west flash` | Default serial port. When it is unset and no `-p` / `--port` is given, the only USB serial port present is used |
| `IPRO_PROBE_PORT` | `west flash` | The debug probe's UART bridge (it takes the download-mode keywords); defaults to `--port` |
| `CROSS_COMPILE` | `make`, `build_freertos.sh build` | Toolchain prefix; set in the environment, it overrides `CONFIG_CROSS_COMPILE` in `.config` |
| `IPRO_TOOLCHAIN` | `tools/zephyr/bootstrap.sh` | Toolchain directory for the Zephyr workspace; default `/opt/toolchain/riscv_ipro7` |
| `IPRO_ZEPHYR_WS` | `tools/zephyr/build.sh`, `ci_build.sh` | Zephyr workspace location; default `<SDK>/zephyr-workspace` |

## build_freertos.sh { #build-cli }

```text
./build_freertos.sh [actions...] [options] <project>
```

Actions can be chained and run in order; the first failing action stops the run. With no action, `build` runs.

| Action | Description |
|---|---|
| `build` | Runs `make -C <app>` and logs to `<build dir>/build.log`; prints the `.bin` path and size on success, the last 30 log lines on failure |
| `clean` | Deletes the build directory |
| `flash` | Sends `reboot_dl` through `serial_monitor.py` (115200 baud), then flashes the `.bin` with the IntelProCube tool; success means `[All Success]` in the output. It does not build first |
| `monitor` | Opens the console with `serial_monitor.py` at 115200 baud, sends `reboot` first and stops after `-t` seconds |
| `size` | Runs `size` and `size -A` (first 30 lines of sections) on the ELF |
| `test` | Builds, flashes, sends `reboot` and waits for `ALL TESTS PASSED` or `SOME TESTS FAILED`; exits 0 on pass, 1 on failure, 2 on timeout |

| Option | Description | Default |
|---|---|---|
| `-p, --port PORT` | Serial port | `$IPRO_SERIAL_PORT`, else the only USB serial port |
| `-t, --timeout SEC` | Seconds for `monitor` and `test` | `30` |
| `-w, --wait-for PAT` | Regular expression `monitor` waits for | — |
| `-d, --defconfig FILE` | Use an alternate config file from the application directory; builds in `build_<name>/` (`defconfig_reef` → `build_reef/`) | — |
| `-j, --jobs N` | Parallel build jobs | — |
| `-v, --verbose` | Show the full build output | — |
| `-l, --list` | List every project under `apps/` by category | — |
| `-h, --help` | Help | — |

`<project>` is an application name (`ipro7ai_reef_demo`) or a path below `apps/` (`platform/ipro7ai_reef_demo`). If the name is ambiguous or unknown, the script lists candidates. The description column of `-l` comes from the first comment line of `.config` and is empty for some applications.

```bash
./build_freertos.sh -l                                  # list the 35 applications
./build_freertos.sh ipro7ai_reef_demo                   # build the Reef out-of-box firmware
./build_freertos.sh clean build platform/ipro7ai_reef_demo
./build_freertos.sh -d defconfig_reef build ipro_ble_remote   # Reef config, output in build_reef/
./build_freertos.sh size ipro7ai_reef_demo
```

Output goes to `<app>/build/build_out/` (`build_<name>/build_out/` with `-d`): `<app>_IPRO7.bin`, `.elf` and `.map`.

!!! warning "Fixed settings in flash, monitor and size"
    - `flash` passes neither `--chip-variant` nor `--pt`, and `reboot_dl` and `monitor` always use 115200 baud. For the IPRO7AI Reef EVK, the IPRO7AI EVK, applications that need a specific partition table, and applications with a 921600-baud console, use the IntelProCube tool and `serial_monitor.py` instead, as described in [Flashing & Serial Console](../get-started/flash-and-monitor.md#build-script).
    - `size` always uses `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size` and ignores `CROSS_COMPILE`.

## make targets { #make-targets }

Each application's `Makefile` calls `project.build` in the SDK root, which configures CMake with the `Unix Makefiles` generator and builds with `make -j4`.

| Command | Description |
|---|---|
| `make -C apps/<category>/<app>` | Build from `.config` into `build/` |
| `make -C apps/<category>/<app> clean` | Delete the build directory |
| `make -C apps/<category>/<app> DEFCONFIG=defconfig_<name>` | Build from an alternate config into `build_<name>/`; `.config` is untouched |
| `make -C apps/multimedia/ipro_pdm_mic_demo BOARD=evk` | Only `ipro_pdm_mic_demo` and `ipro_agora_sentino` accept `BOARD=`: they use `config_<board>` and build into `build_config_<board>/` |

- CMake: the `cmake` on `PATH` is preferred; `tools/cmake/` (Linux x86-64) is the fallback.
- After each build, `compile_commands.json` is copied to the SDK root for editors.
- The `defconfig`, `list-defconfigs` and `menuconfig` targets in some Makefiles depend on files the package does not contain and do not work; edit `.config` directly.

## IntelProCube flash tool { #flash-tool }

Flashing uses the command-line tool of IntelProCube v0.6.3, which is not included in V2.1.0; contact INTELPRO. The table below is collected from the READMEs and flash scripts in the SDK; the tool itself is authoritative for its options. Run it from the IntelProCube directory.

| Option | Description |
|---|---|
| `--chipname ipro7` | Chip |
| `--chip-variant IPRO7` or `IPRO7AI` | The board's flash-pin setting, stored as `flash_pin` in the tool's configuration file: `IPRO7` (`0x2`) for the IPRO7 EVB, `IPRO7AI` (`0x9`) for the IPRO7AI EVK and the IPRO7AI Reef EVK. Later runs that omit the option reuse it |
| `--port` | Serial port |
| `--baudrate` | Flashing baud rate; the SDK's application READMEs and scripts use `921600` |
| `--firmware` | The `.bin` to flash |
| `--pt` | Partition table (`.toml`), as a path relative to the tool directory (for example `chips/ipro7/partition/partition_cfg_2M.toml`) or a full path. Without it, the tool writes its default table |
| `--mfg` | File for the `mfg` partition (an AI model); see `flash.sh` in the IPRO7AI EVK AI examples |
| `--build`, `--boot2` | Only produce the combined image `chips/ipro7/img_create_iot/whole_img.bin` for [`create_ota.py`](#ota-package); see `apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh` |

```bash
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 \
    --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

The tool exits with 0 even when it fails; check the output for `[All Success]`. The commands for each OS, the per-board settings and how to enter download mode are in [Flashing & Serial Console](../get-started/flash-and-monitor.md).

## serial_monitor.py { #serial-monitor }

```text
python3 tools/serial_monitor.py <port> [--baud 115200] [--timeout 30]
                                [--send CMD] [--wait-for PATTERN] [--log FILE]
```

It opens the port with the Python standard library's termios module, so pyserial is not needed. It runs on macOS and Linux, not on Windows.

| Option | Description | Default |
|---|---|---|
| `--baud` | Baud rate; high rates such as 921600 and 2000000 work on both macOS and Linux | `115200` |
| `--timeout` | Seconds to monitor; `0` runs until Ctrl-C | `30` |
| `--send` | One line sent before monitoring, e.g. `reboot`, `reboot_dl` | — |
| `--wait-for` | Regular expression; stops when it matches | — |
| `--log` | Also save the raw output to a file | — |

| Exit code | Meaning |
|---|---|
| 0 | Pattern matched and the match contains `PASSED` |
| 1 | Pattern matched but the match does not contain `PASSED` |
| 2 | Timed out without a match |
| 3 | Could not open the port or send the command |
| 130 | Stopped with Ctrl-C |

```bash
# Reef console (115200) until Ctrl-C
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0

# An application with a 921600-baud console, saved to a file
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 60 --log console.log

# Reboot the running firmware into download mode
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
```

On macOS use `/dev/cu.*`; `/dev/tty.*` waits for carrier detect and blocks. Stop monitoring before flashing to release the port.

## create_ota.py { #ota-package }

Packs the combined image produced by IntelProCube into a boot2 OTA package: XZ-compressed by default, written to `<input name>.xz.ota`, or uncompressed with `--raw`, written to `<input name>.ota`. The input must be the combined image with its boot header, starting with `IPNP` (the tool's `chips/ipro7/img_create_iot/whole_img.bin`), not the `.bin` from the SDK build; the script stops on any other input.

```text
python3 tools/create_ota.py <whole_img.bin> [--raw] [-o OUTPUT] [--hw-ver STR] [--fw-ver STR]
```

| Option | Description |
|---|---|
| `--raw` | No compression |
| `-o, --output` | Output file |
| `--hw-ver` | Hardware version string written to the header; always set it rather than relying on the default |
| `--fw-ver` | Firmware version string written to the header (default `OTA_V1.0.0`) |
| `--sign-key`, `--product` and the other signing options | Need a product configuration file the package does not contain; not usable with V2.1.0 |

```bash
python3 tools/create_ota.py <IntelProCube>/chips/ipro7/img_create_iot/whole_img.bin \
    -o ipro_ble_remote_reef.xz.ota --hw-ver <hw-version> --fw-ver 202610160900
```

The overall OTA flow (Reef A/B partitions, transfer over BLE) is in [OTA Updates](../guides/ota.md).

## Zephyr scripts { #zephyr-tools }

The scripts in `tools/zephyr/` support the `ipro7_evb` and `ipro7ai_evk` boards. The full workflow is in [Zephyr RTOS](../guides/zephyr.md).

| Script | Command | Description |
|---|---|---|
| `bootstrap.sh` | `tools/zephyr/bootstrap.sh [-w DIR] [--full]` | Creates `zephyr-workspace/`: a Python venv with west, Zephyr v4.4.0 and the modules `west.yml` lists, the patches in `zephyr/patches.yml`, and `env.sh`. `--full` fetches the modules in full; the toolchain path comes from `IPRO_TOOLCHAIN` |
| `build.sh` | `tools/zephyr/build.sh [-b BOARD] [-d DIR] [-p] APP [-- CMAKE_ARGS]` | Builds a Zephyr application; `-b` defaults to `ipro7_evb`, `-p` is a pristine build, `APP` is a path or a sample name under `zephyr/samples/`. Output: `<workspace>/build/<board>/<app>/zephyr/zephyr.bin` |
| `flash.sh` | `tools/zephyr/flash.sh [--port PORT] [--build-dir DIR | zephyr.bin]` | Flashes `zephyr.bin` with the IntelProCube tool (921600 baud, no `--pt`) |
| `monitor.sh` | `tools/zephyr/monitor.sh [--port PORT] [--baud 2000000] [--timeout S]` | Opens the UART0 console at 2000000 baud; runs until Ctrl-C by default |
| `ci_build.sh` | `tools/zephyr/ci_build.sh [-b BOARD] [-q]` | Builds the sample matrix pristine with warnings as errors and prints sizes; `-q` builds only hello_world and blinky. Summary in `<workspace>/build/ci/summary.md` |
| `merge_mcuboot.py` | `merge_mcuboot.py <sysbuild build dir> [-o merged.bin] [--slot1 FILE]` | Joins MCUboot and the signed application into one FW image to flash with IntelProCube |
| `csl_pcap.py` | `csl_pcap.py FILE.pcap [--ts-end] [--dump]` | Analyzes CSL timing in an 802.15.4 sniffer capture |

```bash
tools/zephyr/bootstrap.sh
source zephyr-workspace/env.sh
cd zephyr-workspace
west build -b ipro7_evb zephyr/samples/hello_world
west flash                    # enters download mode through the IPRO debug probe; without one add -- --boot manual
```

`west flash` uses the SDK's `ipro` runner; its options go after `--`:

| Option | Description | Default |
|---|---|---|
| `--boot probe|shell|manual` | How the board enters download mode: the IPRO debug probe (CMSIS-DAP), the running image's `reboot_dl`, or BOOT and reset by hand | `probe` (`shell` on `ipro7ai_evk`) |
| `--port` | Flashing serial port | `$IPRO_SERIAL_PORT` |
| `--probe-port` | The debug probe's UART bridge | `$IPRO_PROBE_PORT`, else `--port` |
| `--tool` | IntelProCube tool | `$IPRO_FLASH_TOOL`, else `PATH` |
| `--pt` | Partition table | `ipro7_evb`: `partition_cfg_2M.toml`; `ipro7ai_evk`: `partition_cfg_1M_boot2.toml` |
| `--baudrate` | Flashing baud rate | `2000000` |
| `--console-baud` | Baud rate `--boot shell` uses to send `reboot_dl` | `2000000` |
| `--attempts` | Flash attempts before giving up | `3` |
| `--tool-arg` | Extra argument for the tool (repeatable) | — |
| `--no-reset` | Stay in download mode after flashing | — |

!!! warning "Known script limitations"
    - `-h` on `bootstrap.sh`, `build.sh`, `flash.sh` and `ci_build.sh` does not print usage; use this page.
    - `flash.sh` sends `reboot_dl` at 115200 baud, which a running Zephyr image (console at 2000000 baud) does not receive. Use `west flash -- --boot shell`, or put the board in download mode by hand.
    - Without `-b`, `ci_build.sh` also builds `ipro6s_evb`, which this release does not support; pass `-b ipro7_evb` or `-b ipro7ai_evk`.
    - This release has no Zephyr board definition for the IPRO7AI Reef EVK.

## Size and memory analysis { #size-analysis }

| Method | Command or location | What you get |
|---|---|---|
| Linker memory report | the last lines of every build (in `build.log` with `build_freertos.sh`) | Used size and percentage per memory region (`flash`, `ocram`, plus `psram` when enabled) |
| `size` action | `./build_freertos.sh size <app>` | text / data / bss totals and per-section sizes |
| Map file | `<app>/build/build_out/<app>_IPRO7.map` | Address and size of every object file and library |
| Symbols by size | `riscv64-unknown-elf-nm --size-sort -S <ELF>` | The largest functions and variables |
| Disassembly | set `CONFIG_GENERATE_ASM=y` in `.config` | The build also writes `<app>_IPRO7.asm` |

```bash
./build_freertos.sh size ipro7ai_reef_demo
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-nm --size-sort -S \
    apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf | tail -20
```

With both `CONFIG_AI_SUPPORT` and `CONFIG_MM_SUPPORT` set, the linker script shrinks the OCRAM region to 64 KB (`CONFIG_EM_SIZE` of 0) or 48 KB (`CONFIG_EM_SIZE` above 0), which is why AI and BLE rarely fit in one image. The memory map is on the [IPRO7](../hardware/chips/ipro7.md) page and the OCRAM budget in [Build System & Configuration](../guides/build-system.md).

## Automated testing { #automated-testing }

```bash
./build_freertos.sh test ipro_unit_test -p /dev/cu.usbserial-XXXX -t 60
```

`test` builds, flashes, sends `reboot` and waits for `ALL TESTS PASSED` or `SOME TESTS FAILED`. Exit codes: 0 pass, 1 fail, 2 timeout. Flashing uses the fixed `flash` settings above; `ipro_unit_test` is configured for the IPRO7 EVB. Test contents and on-board commands are under [On-board testing](debugging.md#board-testing).

## Other tools { #other-tools }

| Tool | Description |
|---|---|
| `tools/script/parse_kconfig_dynamic.py Kconfig [PROJECT_SYMBOL]` | Prints a Kconfig tree as JSON; needs kconfiglib. The build does not use it: `cmake/generate_autoconf.cmake` reads `.config` directly to produce `autoconf.h` |
| `apps/ai/ipro7ai_evk_person_detect/flash.sh`, `apps/ai/ipro7ai_evk_rps/flash.sh`, `apps/platform/ipro7ai_evk_launcher/flash.sh` | Flash scripts for the IPRO7AI EVK AI examples (partition table, firmware and `mfg` model) |
| `apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh`, `reef_ota.py` | Build a Reef OTA package and send it over BLE |
| `apps/test/ipro_gh7007_video/tools/video_convert.py` | Convert video for the GH7007 panel player |
| `components/audio/tools/gen_asrc_coef.py` | Generate audio sample-rate converter coefficients |

## Development workflow { #dev-workflow }

One edit–build–flash–check loop on the Reef is walked through in [Build and Flash Workflow](../tutorials/build-and-flash.md).

For Zephyr applications use `west build` / `west flash` instead (see [Zephyr scripts](#zephyr-tools)). Debugging and common errors are in [Debugging & Troubleshooting](debugging.md).
