---
title: "Tool Command Lines"
description: Commands, options and examples for the host tools in SDK V2.3.0 — build_freertos.sh, make, the IntelProCube flash tool, serial_monitor.py, create_ota.py, the Reef Teach and OTA tools — and what does not ship.
migrate_from:
  - "tools-debugging.html#overview"
  - "tools-debugging.html#build-cli"
  - "tools-debugging.html#zephyr-tools"
  - "tools-debugging.html#automated-testing"
  - "tools-debugging.html#size-analysis"
  - "tools-debugging.html#dev-workflow"
---

# Tool Command Lines

Command syntax, options and examples for the host tools that ship with the SDK. Examples use the IPRO7AI Reef EVK V4.0. For step-by-step flashing and console use, see [Flashing & Serial Console](../get-started/flash-and-monitor.md).

## Tools at a glance { #overview }

| Tool | Path | Purpose | Availability |
|---|---|---|---|
| `build_freertos.sh` | SDK root | Build, clean, flash, console, size report and automated test | Included |
| `make` + `project.build` | each application's `Makefile` | Build one application | Included |
| `serial_monitor.py` | `tools/` | Read the console; optionally send one command first, wait for a pattern and save a log (macOS, Linux; not an interactive terminal) | Included |
| `create_ota.py` | `tools/` | Wrap IntelProCube's combined image into a boot2 OTA package | Included |
| `ipro_dl.py` | `tools/` | Flashes a board through boot2's USB downloader, Python standard library only (macOS, Linux); `ipro7ai_sensor_tag_demo` on the IPRO7AI Sensor Tag is flashed with it over the board's USB, and IPRO Workbench 0.2.0 on macOS uses it to flash over the board's USB. From V2.3.0 | Included |
| Browser image Teach | `tools/teach_web/` | Collect images, train a classifier and deploy it to `ipro_reef_teach`, in Chrome or Edge | Included |
| `mfg_payload.py` | `apps/ai/ipro_reef_teach/` | Build the `--mfg` content of `ipro_reef_teach` (boot mode and voiceprint model) | Included |
| Reef BLE OTA tools | `apps/bluetooth/ble/ipro_ble_remote/tools/` | `make_reef_ota.sh`, `reef_ota.py`, `reef_ble_test.py`, plus the Android demo app `ipro_remote_demo.apk` (in the application directory) | Included |
| `parse_kconfig_dynamic.py` | `tools/script/` | Export a Kconfig tree as JSON (needs kconfiglib; not used by the build) | Included |
| CMake 3.15 | `tools/cmake/` | Fallback when no `cmake` is on `PATH`; Linux x86-64 only | Included |
| Zephyr scripts | `tools/zephyr/` | Zephyr workspace, build, flash and console (`ipro7_evb` and `ipro7ai_evk` boards) | Included |
| IntelProCube 0.7.0.1 command-line flasher | `ipro_iot_tool_macos`, `ipro_iot_tool_linux`, `ipro_iot_tool.exe` | Flash firmware, partition tables, boot2 and `mfg` content over the serial port | Not included in V2.3.0; download it from [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) |
| RISC-V toolchain | `/opt/toolchain/riscv_ipro7/` | Compiler (GCC 14, `riscv64-unknown-elf-`) | Not included in V2.3.0; contact INTELPRO |
| IPRO AI Studio | — | IPRO AI Teach, model conversion and deployment | Not in the SDK; download from [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) |
| OpenOCD / GDB connection setup, the board test script `tools/board_test.sh`, a crash-dump host tool | — | On-target debugging, automated board tests, reading memory after `==DUMP_READY:` | Not included in V2.3.0; contact INTELPRO |
| `tools/kconfig/menuconfig.py`, the `configs/` defconfig directory, `ota_products.py` for OTA signing | — | `make menuconfig`, `make defconfig`, `create_ota.py --sign-key` | Not included in V2.3.0 |

This release has no setup or procedure for on-target debugging over JTAG / GDB. Debugging relies on the serial console, logs and offline `addr2line`; see [Debugging & Troubleshooting](debugging.md).

## Environment variables { #environment }

| Variable | Used by | Effect |
|---|---|---|
| `IPRO_FLASH_TOOL` | `build_freertos.sh`, `make_reef_ota.sh`, `tools/zephyr/flash.sh`, `west flash` | Path to the IntelProCube command-line tool. When unset, the tool name for your OS is looked up on `PATH` |
| `IPRO_SERIAL_PORT` | `build_freertos.sh`, the `tools/zephyr/` scripts, `west flash` | Default serial port. When it is unset and no `-p` is given, the only USB serial port present is used |
| `IPRO_CHIP_VARIANT` | `build_freertos.sh flash` | The `--chip-variant` to flash with (`IPRO7` or `IPRO7AI`). When unset it is chosen from the application's configuration; see [build_freertos.sh](#build-cli) |
| `IPRO_FLASH_PT` | `build_freertos.sh flash` | The `--pt` partition table to flash with. When unset, no `--pt` is passed and the tool uses its default table |
| `IPRO_PROBE_PORT` | `west flash` | The IPRO Debug Probe's UART bridge; defaults to `--port` |
| `CROSS_COMPILE` | `make`, `build_freertos.sh build` | Toolchain prefix; set in the environment or on the command line, it overrides `CONFIG_CROSS_COMPILE` in `.config` |
| `IPRO_TOOLCHAIN` | `tools/zephyr/bootstrap.sh` | Toolchain directory for the Zephyr workspace; default `/opt/toolchain/riscv_ipro7` |
| `IPRO_ZEPHYR_WS` | `tools/zephyr/build.sh`, `ci_build.sh` | Zephyr workspace location; default `<SDK>/zephyr-workspace` |

## build_freertos.sh { #build-cli }

```text
./build_freertos.sh [actions...] [options] <project>
```

Actions can be chained and run in order; the first failure stops the run. With no action, `build` runs. It is a bash script for macOS and Linux.

| Action | What it does |
|---|---|
| `build` | Runs `make -C <app>`, logs to `<build dir>/build.log`, prints the `.bin` path and size on success, or the last 30 log lines on failure |
| `clean` | Deletes the build directory |
| `flash` | Sends `reboot_dl` at the application's console baud rate, waits 2 s, then flashes with the IntelProCube tool: `--chipname ipro7 --chip-variant <auto> --baudrate 921600`, plus `--pt` when `-P` is given. Success is the `[All Success]` line in the tool's output. Does not build first |
| `monitor` | Opens `serial_monitor.py` at the application's console baud rate, sends `reboot` first and stops after `-t` seconds |
| `size` | Runs `size` and `size -A` on the ELF (first 30 section lines) |
| `test` | Builds, flashes, sends `reboot` and waits for `ALL TESTS PASSED` or `SOME TESTS FAILED`; exit code 0 pass, 1 fail, 2 time-out |

The console baud rate is `CONFIG_PLATFORM_UART_BAUDRATE` in the configuration file in use, 115200 when unset.

| Option | Meaning | Default |
|---|---|---|
| `-p, --port PORT` | Serial port | `$IPRO_SERIAL_PORT`, else the only USB serial port |
| `-t, --timeout SEC` | Seconds for `monitor` and `test` | `30` |
| `-w, --wait-for PAT` | Regular expression `monitor` waits for | — |
| `-d, --defconfig FILE` | Use an alternate configuration file from the application directory and build into `build_<name>/` (`defconfig_reef` → `build_reef/`) | — |
| `-c, --chip-variant V` | `--chip-variant` for flashing: `IPRO7` or `IPRO7AI` | `$IPRO_CHIP_VARIANT`; else `IPRO7AI` when the configuration sets `CONFIG_IPRO7AI_REEF=y` or `CONFIG_IPRO7AI_EVK=y`, `IPRO7` otherwise |
| `-P, --pt TABLE` | Partition table for flashing: a `.toml` path (passed to the tool as an absolute path) or a table name under the tool's `chips/ipro7/partition/` | `$IPRO_FLASH_PT`, else none |
| `-j, --jobs N` | Parallel jobs for the outer `make`; the inner CMake build always uses `-j4` | — |
| `-v, --verbose` | Show the full build output | — |
| `-l, --list` | List all 41 projects under `apps/` by category | — |
| `-h, --help` | Help | — |

`<project>` is an application name (`ipro7ai_reef_demo`) or a path below `apps/` (`platform/ipro7ai_reef_demo`). An ambiguous or unknown name prints the candidates. The description column of `-l` comes from the first comment line of `.config` and is blank for some applications.

Build, flash and open the console on the Reef in one go (before the very first flash there is no SDK firmware on the board to answer `reboot_dl`, so [enter download mode](debugging.md#download-mode) by hand):

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

You should see, in order:

```text
→ Entering download mode...
→ Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
...
✓ Flash succeeded (…)
→ Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
```

Pick another Reef configuration with `-d`, for example:

```bash
./build_freertos.sh -d defconfig_reef build ipro_ble_remote          # output in build_reef/build_out/
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam
./build_freertos.sh -l                                              # list the 41 projects
./build_freertos.sh size ipro7ai_reef_demo
```

Output goes to `<app>/build/build_out/` (`build_<name>/build_out/` with `-d`): `<app>_<chip>.bin`, `.elf` and `.map`, where the chip comes from `CONFIG_CHIP` (`_IPRO7` for IPRO7 applications, `_IPRO6` for IPRO6S applications).

!!! warning "Limits of build_freertos.sh"
    - `flash` always passes `--chipname ipro7`: flash IPRO6S applications (such as the FIN card firmware `ipro6_if_wifi`) with IntelProCube's `--chipname ipro6` directly.
    - It cannot pass `--boot2`, `--mfg` or `--skip-ota`: flash `ipro_ble_remote` the first time (boot2 + A/B table) and `ipro_reef_teach` (its own table and `mfg` content) with the [IntelProCube tool](#flash-tool) directly.
    - There is no `BOARD=` option; a `config_<board>` file can be named with `-d config_evk` and builds into `build_config_evk/`.
    - The flash tool runs in your current directory; give `-P` the full path of the `.toml`.
    - `size` always uses `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size` and ignores `CROSS_COMPILE`.

## make targets { #make-targets }

Each application's `Makefile` calls `project.build` in the SDK root (CMake with the `Unix Makefiles` generator, then `make -j4`).

| Command | What it does |
|---|---|
| `make -C apps/<category>/<app>` | Build with `.config` into `build/` |
| `make -C apps/<category>/<app> clean` | Delete the build directory (with `DEFCONFIG=`, the matching `build_<name>/`) |
| `make -C apps/<category>/<app> DEFCONFIG=defconfig_<name>` | Build an alternate configuration into `build_<name>/`; `.config` is left alone |
| `make -C apps/<category>/<app> CROSS_COMPILE=<dir>/bin/riscv64-unknown-elf-` | Set the toolchain prefix; overrides `CONFIG_CROSS_COMPILE` in `.config` |
| `make -C apps/multimedia/ipro_agora_sentino BOARD=evk` | Only `ipro_agora_sentino` (default `reef` = `.config`) and `ipro_pdm_mic_demo` (default `evb`) read `BOARD=`: it selects `config_<board>` and builds into `build_config_<board>/` |

- CMake: the `cmake` on `PATH` first, then `tools/cmake/` (Linux x86-64); with neither, the build stops at `No cmake found`.
- After each build, `compile_commands.json` is copied to the SDK root for editors.
- `make menuconfig` needs `tools/kconfig/menuconfig.py`, which does not ship; the `defconfig` and `list-defconfigs` targets of some `Makefile`s look in a `configs/` directory that does not ship either. Edit `.config` directly, or save a copy as `defconfig_<name>` and build it with `DEFCONFIG=`.

## IntelProCube flash tool { #flash-tool }

Flashing uses the IntelProCube command-line tool. It is not included in V2.3.0: download 0.7.0.1 from [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) and install it as in [Set Up Your Host](../get-started/environment.md#intelprocube). The tool reads its chip files from its own `chips/` directory, so run it from the IntelProCube directory. The table is compiled from the READMEs and scripts in the SDK; the tool itself is the reference for the full option set.

| Option | Meaning |
|---|---|
| `--chipname ipro7` | IPRO7 / IPRO7AI (the Reef). IPRO6S (for example the FIN card) uses `--chipname ipro6` |
| `--chip-variant IPRO7AI` | Flash pin setting: `IPRO7AI` (`0x9`) for the IPRO7AI (Reef, QFN56), `IPRO7` (`0x2`) for the IPRO7 EVB. The tool writes it into its own `chips/ipro7/eflash_loader/eflash_loader_cfg.ini`, so always pass it again when you switch boards |
| `--port` | Serial port: a USB-to-UART cable, or the IPRO Debug Probe port whose name ends in `02` |
| `--baudrate 921600` | Flashing baud rate, independent of the application's console rate |
| `--firmware` | The `.bin` to flash |
| `--pt` | Partition table (`.toml`): a path relative to the tool directory (for example `chips/ipro7/partition/partition_cfg_2M.toml`) or a full path. Without it, the tool's default table is used |
| `--boot2` | Also flash a boot2 image (for example the tool's `chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin`); needed for `ipro_ble_remote` OTA on the Reef |
| `--mfg` | File to write into the `mfg` partition (AI models; the boot mode and voiceprint model of `ipro_reef_teach`) |
| `--skip-ota` | Used with an application's own partition table, for example `ipro_reef_teach` |
| `--build` | Only build the combined image `chips/ipro7/img_create_iot/whole_img.bin`, without flashing; input for [`create_ota.py`](#ota-package) |

Flashing the Reef's out-of-box firmware ([enter download mode](debugging.md#download-mode) first):

```bash
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 \
    --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

A successful run ends with `[All Success]`. The tool exits 0 even when it fails, so judge by that line. On Linux use `./ipro_iot_tool_linux`; on Windows `ipro_iot_tool.exe` and a port such as `COM5`. The partition table, `--boot2` and `--mfg` each Reef application needs are listed on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples).

## serial_monitor.py { #serial-monitor }

```text
python3 tools/serial_monitor.py <port> [--baud 115200] [--timeout 30]
                                [--send CMD] [--wait-for PATTERN] [--log FILE]
```

Opens the port with the Python standard library's termios, so it needs no pyserial; it runs on macOS and Linux, not on Windows. It only reads output (optionally after sending one command); it is not an interactive terminal. To type commands line by line, use `screen`, `minicom` or another serial terminal program.

| Option | Meaning | Default |
|---|---|---|
| `--baud` | Baud rate; high rates such as 921600 and 2000000 work on macOS and Linux | `115200` |
| `--timeout` | Seconds to watch; `0` runs until Ctrl-C | `30` |
| `--send` | One command to send before watching, for example `reboot`, `reboot_dl`, `reef selftest` | — |
| `--wait-for` | Regular expression; the monitor exits on the first match | — |
| `--log` | Also save the raw output to a file | — |

| Exit code | Meaning |
|---|---|
| 0 | Matched, and the matched text contains `PASSED` |
| 1 | Matched, but the matched text does not contain `PASSED` |
| 2 | Timed out without a match |
| 3 | Could not open the port or send the command |
| 130 | Stopped with Ctrl-C |

```bash
# Reef console (115200): run the self-test, stop after 10 s
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# ipro7_jpeg_decode's Reef configuration (921600): watch until Ctrl-C and save a log
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0 --log console.log

# Reboot the running firmware into download mode (it prints "reboot to download mode")
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
```

On macOS use `/dev/cu.*`; `/dev/tty.*` waits for carrier detect and hangs. Stop the monitor before flashing so the port is free.

## create_ota.py { #ota-package }

Wraps the combined image that IntelProCube builds into a boot2 OTA package: XZ-compressed by default, written as `<input name>.xz.ota`, or uncompressed as `<input name>.ota` with `--raw`. The input must be the combined image with a boot header that starts with `IPNP` (the tool's `chips/ipro7/img_create_iot/whole_img.bin`), not the `.bin` from an SDK build; the script stops on any other format.

```text
python3 tools/create_ota.py <whole_img.bin> [--raw] [-o OUTPUT] [--hw-ver STR] [--fw-ver STR]
```

| Option | Meaning |
|---|---|
| `--raw` | No compression |
| `-o, --output` | Output file |
| `--hw-ver` | Hardware version string in the header; set it explicitly rather than relying on the default |
| `--fw-ver` | Firmware version string in the header (default `OTA_V1.0.0`) |
| `--sign-key`, `--product` and the other signing options | Need `ota_products.py`, which does not ship; not usable with V2.3.0 |

On the Reef, `make_reef_ota.sh` of `ipro_ble_remote` runs the tool's `--build` and this script for you; see [Host tools for Reef applications](#reef-tools). The complete OTA flow is in [OTA Updates](../guides/ota.md).

## Host tools for Reef applications { #reef-tools }

### Browser image Teach: tools/teach_web { #teach-web }

Collect images from the Reef's camera, train a classifier and deploy it over USB in Chrome or Edge, without installing IPRO AI Studio. The board must run `ipro_reef_teach` in `image` mode; the host needs Python 3.8 or newer.

<div class="ipro-steps" markdown>

1. **Start the web server**

    ```bash
    python3 tools/teach_web/serve.py
    ```

    The browser opens `http://localhost:8780` (if your default browser is not Chrome or Edge, paste the address into one of them).

2. **Connect the board**: allow camera access; on **Connect…** or the first **Deploy**, pick the serial port **IPRO7 UVC Cam**.

3. **Offline computers**: run `python3 tools/teach_web/serve.py --fetch-runtime` once while online; it stores the LiteRT.js runtime (about 22 MB) locally.

</div>

### The mfg content of ipro_reef_teach: mfg_payload.py { #mfg-payload }

The first flash of `ipro_reef_teach` writes the boot mode and the voiceprint model with `--mfg`:

```bash
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
```

`--mode` is `image`, `voice` or `sensor`. Pass the resulting `reef_teach_mfg.bin` to IntelProCube with `--mfg`; the flash command is on the [example page](../examples/ipro_reef_teach.md). Leave out `--mfg` when you update only the firmware.

### Reef OTA tools of ipro_ble_remote { #reef-ota-tools }

| Tool | Command | Result |
|---|---|---|
| `make_reef_ota.sh` | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh` | Needs a `DEFCONFIG=defconfig_reef` build first; writes `build_reef/build_out/ipro_ble_remote_reef.xz.ota` (about 345 KB). It takes the newest boot2 in the IntelProCube folder, or the file in `IPRO_BOOT2` |
| `reef_ota.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py <package.xz.ota>` | Sends the package over BLE (bleak) to the board named `IPRO-Remote` and prints progress and status |
| `reef_ble_test.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ble_test.py` | Tests the Reef's GATT services as a bleak central (`info led env sound tone img`; `keys` and `motion` need someone at the board); captured JPEGs land next to the script |
| `ipro_remote_demo.apk` | Install on an Android phone | Demo app for `ipro_ble_remote`; it can push `.xz.ota` packages |

Both Python scripts need bleak: `python3 -m venv .venv && .venv/bin/pip install bleak`. OTA works only on a board flashed with boot2 and `partition_cfg_2M_remote_ab.toml`; never run OTA on a Reef flashed with the standard `partition_cfg_2M.toml`.

### Tools of other Reef applications { #reef-app-tools }

| Tool | Purpose |
|---|---|
| `apps/multimedia/ipro7_jpeg_decode/host/jpeg_check.py photo.jpg [--fix out.jpg]` | Check on the PC whether IPRO7 can decode a JPEG, and convert it if needed |
| `apps/multimedia/ipro7_jpeg_decode/host/jdec_host.py -p <port> upload photo.jpg --go 565` | Send a JPEG to the board over the console for decoding, and fetch the result for comparison |
| `apps/multimedia/ipro7_jpeg_decode/host/run_host_tests.py` | Check the decoder on the PC against libjpeg (needs `cc`, `djpeg`) |
| `apps/multimedia/ipro_agora_sentino/setup_ncm_nat.sh` | Set up NAT for the USB-NCM link on macOS |

## Zephyr scripts { #zephyr-tools }

`tools/zephyr/` (`bootstrap.sh`, `build.sh`, `flash.sh`, `monitor.sh`, `ci_build.sh`) serves the Zephyr boards `ipro7_evb` and `ipro7ai_evk`; this release has no Zephyr board for the Reef. Usage is in [Zephyr RTOS](../guides/zephyr.md).

## Size and memory analysis { #size-analysis }

| Method | Command or location | Shows |
|---|---|---|
| Linker memory report | Last lines of every build (in `build.log` with `build_freertos.sh`) | Use and percentage of each memory region (`flash`, `ocram`, and `psram` when enabled) |
| `size` action | `./build_freertos.sh size <app>` | text / data / bss totals and section sizes |
| Map file | `<build dir>/build_out/<app>_IPRO7.map` | Address and size of every object file and library |
| Symbols by size | `riscv64-unknown-elf-nm --size-sort -S <ELF>` | Largest functions and variables |
| Disassembly | `CONFIG_GENERATE_ASM=y` in `.config` | Also writes `<app>_IPRO7.asm` |

```bash
./build_freertos.sh size ipro7ai_reef_demo
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-nm --size-sort -S \
    apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf | tail -20
```

With both `CONFIG_AI_SUPPORT` and `CONFIG_MM_SUPPORT`, the linker script shrinks the OCRAM region to 64 KB (`CONFIG_EM_SIZE` 0) or 48 KB (`CONFIG_EM_SIZE` above 0), and CMake prints `AI+MM …: OCRAM=…` at configure time. The memory map is on [IPRO7](../hardware/chips/ipro7.md); the OCRAM budget is in [Build System & Configuration](../guides/build-system.md).

## Automated testing { #automated-testing }

`./build_freertos.sh test ipro_unit_test` builds, flashes and waits for `ALL TESTS PASSED` or `SOME TESTS FAILED`; `ipro_unit_test` needs the IPRO7 EVB. The Reef's on-board self-test is `reef selftest` in the out-of-box firmware; see [Debugging & Troubleshooting](debugging.md#board-testing).

## Other tools { #other-tools }

| Tool | What it does |
|---|---|
| `tools/script/parse_kconfig_dynamic.py Kconfig [PROJECT_SYMBOL]` | Prints a Kconfig tree as JSON; needs kconfiglib. The build does not use it: `cmake/generate_autoconf.cmake` reads `.config` directly to generate `autoconf.h` |
| `components/audio/tools/gen_asrc_coef.py` | Generates the audio sample-rate converter coefficients |
| `*/test_host/run.sh` | Unit tests that run on the PC, for example `components/audio/test_host/run.sh` and `apps/ai/ipro_reef_teach/sensor/test_host/run.sh` |
| Tools for other boards | `flash.sh` and `enter_dl.py` of the IPRO7AI EVK examples, `tools/mkimg.py` of `ipro6_fmac` (IPRO6S EVK), `tools/android/IproMicDemo/` (`ipro_pdm_mic_demo`): they need those boards |

## Development workflow { #dev-workflow }

The edit, build, flash and console loop on the Reef is in [Build and Flash Workflow](../tutorials/build-and-flash.md); to start your own application, see [Create your first application](../tutorials/first-own-app.md). Debugging and common errors are in [Debugging & Troubleshooting](debugging.md).
