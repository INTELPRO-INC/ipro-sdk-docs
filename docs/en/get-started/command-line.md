---
title: "macOS / Linux Command Line"
description: Install the toolchain and build tools on macOS or Linux, unpack SDK V2.1.0 and confirm that it builds.
migrate_from:
  - "getting-started.html#installation"
  - "getting-started.html#directory-structure"
  - "tools-debugging.html#macos-notes"
---

# macOS / Linux Command Line

Install the toolchain and build tools on macOS or Linux, unpack SDK V2.1.0, and build one application with `build_freertos.sh` to confirm that everything works.

## Prerequisites { #prerequisites }

| Tool | Requirement | Where to get it |
|---|---|---|
| RISC-V toolchain | `riscv64-unknown-elf-gcc`, by default in `/opt/toolchain/riscv_ipro7/bin/` | Not included in V2.1.0; contact INTELPRO |
| CMake | 3.19 or later; Zephyr needs 3.20 or later | Your package manager |
| GNU Make | FreeRTOS applications build with Unix Makefiles | Your package manager |
| Python | 3.8 or later | Your package manager |
| git | Needed for the Zephyr workspace | Your package manager |
| IntelProCube v0.6.3 command-line tool | `ipro_iot_tool_macos` or `ipro_iot_tool_linux` | Not included in V2.1.0; contact INTELPRO |

The CMake bundled in the SDK's `tools/cmake/` is a Linux x86-64 build of version 3.15. It is older than the table above requires and does not run on macOS, so install CMake from your system.

## Installation { #installation }

<div class="ipro-steps" markdown>

1. **Install the build tools**

    === "macOS"

        ```bash
        xcode-select --install          # provides make
        brew install cmake python git
        ```

    === "Linux"

        ```bash
        sudo apt update
        sudo apt install -y cmake make python3 python3-venv git
        ```

        This example is for Debian / Ubuntu; on other distributions install the equivalent packages. `python3-venv` is used by the Zephyr workspace.

    Check the versions:

    ```bash
    cmake --version     # 3.19 or later
    python3 --version   # 3.8 or later
    ```

2. **Install the toolchain**: put the toolchain from INTELPRO in `/opt/toolchain/riscv_ipro7/` and check that it runs.

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc --version
    ```

    If you keep it somewhere else, set `CROSS_COMPILE` to the compiler prefix, including the trailing hyphen, before building:

    ```bash
    export CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-
    ```

3. **Verify and unpack the SDK**

    ```bash
    shasum -a 256 -c IPRO-SDK-V2.1.0.tar.gz.sha256   # or sha256sum -c on Linux
    tar xzf IPRO-SDK-V2.1.0.tar.gz
    cd IPRO-SDK-V2.1.0
    cat VERSION.txt
    ```

    The check should print `IPRO-SDK-V2.1.0.tar.gz: OK`, and `VERSION.txt` should show `IPRO-SDK-V2.1.0`.

4. **Point the scripts at the flash tool**: set `IPRO_FLASH_TOOL` to the IntelProCube command-line tool, or add the IntelProCube directory to `PATH`. `build_freertos.sh`, the apps' `flash.sh` scripts and Zephyr's `west flash` all look for the tool this way.

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ```

    You can also set `IPRO_SERIAL_PORT` to the board's serial port; when only one USB serial port is connected, the scripts pick it on their own.

</div>

## Directory structure { #directory-structure }

The unpacked root holds `apps/` (one directory per application), `bsp/`, `components/`, `cmake/`, `tools/` and `zephyr/`, plus `build_freertos.sh`, `project.build`, `west.yml` and `VERSION.txt`. What each directory contains is described in [Architecture](../guides/architecture.md#directory).

A FreeRTOS application's output goes to `apps/<category>/<app>/build/build_out/` as `<app>_IPRO7.bin`, `.elf` and `.map`.

## Verify { #verify }

From the SDK root, list every application:

```bash
./build_freertos.sh -l
```

Applications are listed by category, for example `ipro7ai_reef_demo` under `platform`. Then build one to confirm that the toolchain and CMake work:

```bash
./build_freertos.sh ipro7ai_reef_demo
```

On success the script prints `Build succeeded` and the `.bin` path after `Binary:`; the full log is in `build/build.log` inside the application directory.

## macOS notes { #macos-notes }

- Use `/dev/cu.*` serial devices (for example `/dev/cu.usbserial-XXXX`), not `/dev/tty.*`: the latter waits for carrier detect and blocks.
- The CMake in `tools/cmake/` is a Linux binary. `project.build` prefers the `cmake` on PATH, so installing CMake on macOS is all you need.
- `tools/serial_monitor.py` uses only the Python standard library (termios), so pyserial is not needed. Rates such as 921600 and 2000000 work on macOS too; the script sets them separately.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `No cmake found`, or running `tools/cmake/bin/cmake` fails on macOS | No `cmake` on PATH, so the build falls back to the bundled Linux CMake | Install CMake 3.19 or later and put it on PATH |
| `riscv64-unknown-elf-gcc` not found | The toolchain is not in `/opt/toolchain/riscv_ipro7/` | Set `CROSS_COMPILE` to the toolchain prefix |
| `Project '…' not found` | The application name does not match | Check names with `./build_freertos.sh -l`, or use the path under `apps/`, such as `platform/ipro7ai_reef_demo` |
| `Flash tool not found` | `IPRO_FLASH_TOOL` is not set and the tool is not on PATH | Set it as in step 4 of [Installation](#installation) |
| The serial port hangs with no output | A `/dev/tty.*` device was used on macOS | Use `/dev/cu.*` instead |

## Next steps { #next-steps }

- [First FreeRTOS Application](first-app-freertos.md): build, flash and run `ipro7ai_reef_demo` on the Reef EVK.
- [First Zephyr Application](first-app-zephyr.md): create the Zephyr workspace and flash `hello_world`.
- [Build System & Configuration](../guides/build-system.md): `.config`, `DEFCONFIG=` and alternate configurations.
