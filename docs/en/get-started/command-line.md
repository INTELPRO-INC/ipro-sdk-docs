---
title: "macOS / Linux Command Line"
description: Complete reference for building, cleaning, flashing and monitoring FreeRTOS applications with make and build_freertos.sh on macOS or Linux, with IPRO7AI Reef EVK examples.
migrate_from:
  - "getting-started.html#installation"
  - "getting-started.html#directory-structure"
  - "tools-debugging.html#macos-notes"
---

# macOS / Linux Command Line

On macOS and Linux, FreeRTOS applications build with `make -C`, or with `build_freertos.sh`, which chains build, flash and monitor in one line. This page is the reference for both: build directories and outputs, alternate configurations, cleaning, and the actions, options, environment variables and limits of `build_freertos.sh`, with examples for the IPRO7AI Reef EVK. Tool installation is on [Set Up Your Host](environment.md).

## Prerequisites { #prerequisites }

- [Set Up Your Host](environment.md) is done: toolchain, CMake, make, Python and IntelProCube.
- Run every command below from the SDK root.
- For flashing, the board is wired as in [Set the switches and wire the board](first-app-freertos.md#connect).

## Directory structure { #directory-structure }

| Path | Contents |
|---|---|
| `apps/<category>/<app>/` | applications: `.config`, alternate `defconfig_*` files, `CMakeLists.txt`, `Makefile`, sources; categories `ai`, `bluetooth`, `multimedia`, `platform`, `test` |
| `bsp/` | board settings and linker scripts, SoC drivers, HAL |
| `components/` | FreeRTOS, BLE, networking, audio, AI, USB, file systems and more; some as prebuilt libraries |
| `cmake/` | toolchain and build macros |
| `tools/` | `serial_monitor.py`, `create_ota.py`, `teach_web/`, `zephyr/`, bundled CMake (Linux x86-64) |
| `zephyr/` | Zephyr module (IPRO7 EVB and IPRO7AI EVK boards) |
| `build_freertos.sh`, `project.build`, `VERSION.txt` | build front end, make-to-CMake glue, version information |

The components are described in [Architecture](../guides/architecture.md).

## Build with make { #make }

```bash
make -C apps/<category>/<app>                            # build .config into build/
make -C apps/<category>/<app> DEFCONFIG=defconfig_<name>  # build an alternate configuration into build_<name>/
```

- **Build directory:** with `DEFCONFIG=` it is `build_` plus the file name without its `defconfig_` prefix, for example `defconfig_reef` → `build_reef/` and `defconfig_wifi_ipro6s` → `build_wifi_ipro6s/`. The alternate file is copied to `build_<name>/.config`; the application's own `.config` is left alone. Edit the original file in the application directory, not the copy.
- **Outputs:** `<build dir>/build_out/<app>_IPRO7.bin` (to flash), `.elf` (with debug symbols), `.map` (memory map); `<build dir>/include/generated/autoconf.h` holds the macros generated from the configuration. Every build also copies `compile_commands.json` to the SDK root for editor indexing.
- **Toolchain:** `make -C … CROSS_COMPILE=<dir>/bin/riscv64-unknown-elf-`, or the environment variable of the same name, overrides `CONFIG_CROSS_COMPILE` in `.config`.
- **Parallel build:** the inner CMake build always runs with `-j4`.
- **`BOARD=`:** used only by `ipro_agora_sentino` (default `reef`) and `ipro_pdm_mic_demo`; other applications choose the board with `DEFCONFIG=`.

Building `ipro7ai_reef_demo` prints (excerpt):

```text
[INFO] Build Path: <SDK>/apps/platform/ipro7ai_reef_demo/build
CPU: intelpro_ipro7
...
-- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
-- Generated autoconf header: <SDK>/apps/platform/ipro7ai_reef_demo/build/include/generated/autoconf.h
...
-- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
-- IPRO7 flash: 1M (default, on-chip)
-- AI disabled: OCRAM=256KB
...
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
[100%] Built target ipro7ai_reef_demo_IPRO7.elf
```

The `[board] IPRO7AI Reef` line confirms that the build targets the Reef. Without it, the configuration is for another board.

### Reef build configurations { #reef-configs }

These configurations target the Reef. Where the table shows `DEFCONFIG=`, a plain `make` builds the application's `.config` for another board.

| Application | Build command | Build directory | Console |
|---|---|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` | `build/` | 115200 |
| `ipro7ai_reef_demo` + Wi-Fi | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | `build_wifi_ipro6s/` | 115200 |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` | `build/` | 115200 |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro7_uvc_cam` webcam | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | `build_reef_ov5640/` | 115200 |
| `ipro7_uvc_cam` rock-paper-scissors | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | `build_reef_rps/` | 115200 |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | `build_reef/` | 921600 |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` | `build/` | 115200 |

Which partition table each application flashes with, and which need boot2 or `mfg` data: [Flashing & Serial Console: Partition tables](flash-and-monitor.md#partition-tables).

## Clean { #clean }

```bash
make -C apps/platform/ipro7ai_reef_demo clean                                   # removes build/
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s clean   # removes build_wifi_ipro6s/
```

`clean` removes only the matching build directory. After changing `.config` or an alternate configuration, clean before building.

## build_freertos.sh { #build-script }

```text
./build_freertos.sh [actions...] [options] <project>
```

Actions chain and run in order; the first failure stops the rest, and with more than one action a summary lists each result at the end. Without an action, `build` runs. The project is a name (`ipro7ai_reef_demo`) or a path under `apps/` (`platform/ipro7ai_reef_demo`).

### Actions { #actions }

| Action | Does |
|---|---|
| `build` | runs `make -C <app> [DEFCONFIG=…]`. The full output goes to `<build dir>/build.log`; on success it prints `✓ Build succeeded`, the `Binary:` path and size, on failure the last 30 lines of the log |
| `clean` | runs `make -C <app> clean`, removing the build directory |
| `flash` | sends `reboot_dl`, then flashes the built image with IntelProCube; see [Flashing & Serial Console](flash-and-monitor.md#build-script) |
| `monitor` | opens the port at the application's console baud rate, sends `reboot` first and reads for `-t` seconds; output only, no typing |
| `size` | prints the total and per-section sizes of the `.elf` with `riscv64-unknown-elf-size` |
| `test` | builds, flashes, sends `reboot` and waits for `ALL TESTS PASSED` or `SOME TESTS FAILED`; exit code 0 pass, 1 fail, 2 timeout |

### Options { #options }

| Option | Meaning |
|---|---|
| `-p`, `--port PORT` | serial port; defaults to `IPRO_SERIAL_PORT`, else the only USB serial port present |
| `-t`, `--timeout SEC` | read time of `monitor` and `test`, 30 s by default; `0` runs until ++ctrl+c++ |
| `-w`, `--wait-for PAT` | `monitor` stops when this regular expression matches; it counts as success only if the matched text contains `PASSED` |
| `-d`, `--defconfig FILE` | alternate configuration, built in `build_<name>/`; `flash` and `size` also look for the image there |
| `-c`, `--chip-variant V` | `--chip-variant` for flashing; defaults to `IPRO_CHIP_VARIANT`, else `IPRO7AI` for IPRO7AI EVK and Reef configurations and `IPRO7` for the rest |
| `-P`, `--pt TABLE` | partition table for flashing: a `.toml` path, or a file name under the tool's `chips/ipro7/partition/`; defaults to `IPRO_FLASH_PT`, else no `--pt` |
| `-j`, `--jobs N` | parallel jobs of the outer `make` (the inner build always uses `-j4`) |
| `-v`, `--verbose` | show the full build output on screen |
| `-l`, `--list` | list every project by category |
| `-h`, `--help` | help |

### Environment variables { #environment }

| Variable | Effect |
|---|---|
| `IPRO_FLASH_TOOL` | path of the IntelProCube command-line tool; when unset, `ipro_iot_tool_macos` / `ipro_iot_tool_linux` is looked up on `PATH` |
| `IPRO_SERIAL_PORT` | default serial port (`-p` wins) |
| `IPRO_CHIP_VARIANT` | default `--chip-variant` (`-c` wins) |
| `IPRO_FLASH_PT` | default partition table (`-P` wins) |
| `CROSS_COMPILE` | passed to `make`; overrides the toolchain prefix in `.config` |

### List the projects { #list }

```bash
./build_freertos.sh -l
```

Lists the projects under `apps/` by category, with the first line of each `.config` as a description (excerpt):

```text
ai
  ipro7ai_evk_person_detect           IPRO7AI EVK person detection: SC101IOT camera -> ISP -> NPU (YOLOv8) with
  ipro7ai_evk_rps                     IPRO7AI EVK rock-paper-scissors: SC101IOT camera -> ISP -> NPU classifier,
  ipro_reef_teach
  ipro_speaker_recog

bluetooth/ble
  ipro_ble_hid_keyboard
  ipro_ble_remote
  ipro_ble_transparent
  ipro_throughput_test
...
platform
  ...
  ipro7ai_reef_demo                   IPRO7AI Reef carrier board demo.
```

The list covers the applications of every board; the configurations for the Reef are those in [the table above](#reef-configs).

## Reef examples { #examples }

Set the environment once (macOS shown):

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
PT2M=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
```

```bash
# out-of-box firmware: build, flash, watch the boot messages for 30 s
./build_freertos.sh -P $PT2M build flash monitor ipro7ai_reef_demo

# clean rebuild of the Wi-Fi variant
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo

# USB webcam: build and flash
./build_freertos.sh -d defconfig_reef_ov5640 -P $PT2M build flash ipro7_uvc_cam

# a 921600-baud application: monitor uses the baud rate from the configuration
./build_freertos.sh -d defconfig_reef build flash monitor ipro7_jpeg_decode

# build only (the first flash needs boot2; run the tool directly)
./build_freertos.sh -d defconfig_reef build size ipro_ble_remote
```

A successful `build` prints:

```text
Project: ipro_ble_remote  (bluetooth/ble/ipro_ble_remote)
Defconfig: defconfig_reef

→ Building ipro_ble_remote...
✓ Build succeeded (19s)
  Binary: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin (561 KB)
  Log: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build.log
```

## Limits { #limits }

- **IPRO7 only:** `flash` always passes `--chipname ipro7`, so it cannot flash IPRO6S images.
- **No `--boot2`, `--mfg` or `--skip-ota`:** run IntelProCube directly for the first flash of `ipro_ble_remote` and the `mfg` data of `ipro_reef_teach`; see [Flashing & Serial Console](flash-and-monitor.md#boot2-ab).
- **The tool runs in the current directory:** give `-P` the full path of the `.toml`.
- **`reboot_dl` needs a shell:** with firmware that has no shell or has hung, enter download mode with the buttons first.
- **`monitor` is not an interactive terminal:** use a terminal program to type commands; see [Interactive terminal](flash-and-monitor.md#terminal). A timeout (exit 2) or a match without `PASSED` (exit 1) counts as a failure and stops later actions, so put `monitor` last.
- **`size` uses the default toolchain path:** it always calls `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size`.
- **No `BOARD=` option:** choose alternate configurations with `-d`.
- **macOS and Linux only:** the script needs bash, and port autodetection only knows `/dev/*` names.

## Verify { #verify }

```bash
./build_freertos.sh -l                      # lists the projects
./build_freertos.sh ipro7ai_reef_demo       # prints ✓ Build succeeded and the Binary: path
ls apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

## macOS notes { #macos-notes }

- Use `/dev/cu.*` serial ports (for example `/dev/cu.usbserial-XXXX`), not `/dev/tty.*`: the latter waits for carrier detect and hangs.
- The CMake bundled in `tools/cmake/` is a Linux binary; the build prefers the `cmake` on `PATH`, so Homebrew's CMake is all macOS needs.
- `tools/serial_monitor.py` uses only the Python standard library (termios), no pyserial; it sets high baud rates such as 921600 on macOS itself, so they work as is.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `✗ Project '…' not found. Did you mean:` | incomplete name | use the full name from `-l` |
| `✗ Multiple projects match '…':` | the same name in several categories | use the path, for example `platform/ipro7ai_reef_demo` |
| `✗ Build failed` with `No cmake found` in the last 30 lines | no `cmake` on `PATH` | install CMake 3.15 or later |
| The build log cannot find `riscv64-unknown-elf-gcc` | the toolchain is not at `/opt/toolchain/riscv_ipro7/` | set `CROSS_COMPILE` |
| No `[board] IPRO7AI Reef` line in the build output | the configuration is for another board | add `DEFCONFIG=` or `-d` as in [Reef build configurations](#reef-configs) |
| After a build with `-d`, `flash` or `size` reports `Binary not found` or `ELF not found` | without `-d` the script looks in `build/` | add the same `-d` |
| `✗ Flash tool not found: ipro_iot_tool_macos` | IntelProCube not found | set `IPRO_FLASH_TOOL` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | more than one USB serial port | name it with `-p` or `IPRO_SERIAL_PORT` |
| `size` fails to find `riscv64-unknown-elf-size` | the toolchain is not at the default path | run `<toolchain dir>/bin/riscv64-unknown-elf-size <elf>` directly |

## Next steps { #next-steps }

- [First FreeRTOS Application](first-app-freertos.md): build, flash and run `ipro7ai_reef_demo` on the Reef.
- [Build and Flash Workflow](../tutorials/build-and-flash.md): the everyday edit, build, flash and monitor loop.
- [Build System & Configuration](../guides/build-system.md): `.config` keys, linker scripts and memory layout.
