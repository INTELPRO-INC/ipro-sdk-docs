---
title: "Set Up Your Host"
description: Get and verify the SDK, install the build tools, the RISC-V toolchain and IntelProCube on macOS, Linux or Windows, connect the console cable and prove the setup with one build.
migrate_from:
  - "getting-started.html#sdk-2-1-0"
  - "getting-started.html#prerequisites"
---

# Set Up Your Host

At the end of this page your computer has the SDK, the build tools, the RISC-V toolchain and the IntelProCube flash tool, recognises the Reef's console port, and builds the out-of-box firmware of the IPRO7AI Reef EVK from the SDK root. Each step has a tab per operating system; the full Windows procedure is on [Windows Setup & VS Code](windows.md).

## Prerequisites { #prerequisites }

| Item | Requirement |
|---|---|
| Host | macOS or Linux with bash, or Windows x64 |
| Rights | installing packages and writing `/opt/toolchain/` need administrator rights |
| Network | to download the SDK; Windows Online Setup needs access to GitHub |
| Obtained separately | the RISC-V toolchain: from INTELPRO for macOS / Linux, installed by Online Setup on Windows |
| Flash tool | IntelProCube 0.7.0.1: download it from [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases), see [Install IntelProCube](#intelprocube); installed by Online Setup on Windows |
| Hardware | IPRO7AI Reef EVK, USB-C cable, console cable; see [What you need](index.md#what-you-need) |

## Get the SDK { #get-sdk }

<div class="ipro-steps" markdown>

1. **Download** `IPRO-SDK-V2.2.1.tar.gz` from the [IPRO-SDK-V2.2.1 release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.1) and note the SHA-256 published on that page.

2. **Verify** the download:

    === "macOS"

        ```bash
        shasum -a 256 IPRO-SDK-V2.2.1.tar.gz
        ```

    === "Linux"

        ```bash
        sha256sum IPRO-SDK-V2.2.1.tar.gz
        ```

    === "Windows"

        ```powershell
        Get-FileHash .\IPRO-SDK-V2.2.1.tar.gz -Algorithm SHA256
        ```

    The 64 hexadecimal characters printed must match the value on the release page (case does not matter). If they differ, download again.

3. **Unpack and check the version.** Unpack into a new directory; do not overwrite an older SDK.

    === "macOS / Linux"

        ```bash
        tar xzf IPRO-SDK-V2.2.1.tar.gz
        cd IPRO-SDK-V2.2.1
        cat VERSION.txt
        ```

    === "Windows"

        ```powershell
        tar -xzf .\IPRO-SDK-V2.2.1.tar.gz
        Get-Content .\IPRO-SDK-V2.2.1\VERSION.txt
        ```

    `VERSION.txt` reads:

    ```text
    IPRO SDK Release
    ========================================
    IPRO7: IPRO-SDK-V2.2.1
    IPRO6: IPRO-SDK-V2.2.1

    Release Date: 2026-11-10
    Base Commit: 60afd4ab
    ```

    `IPRO-SDK-V2.2.1/` is the SDK root (`<SDK>` on this site); it holds `apps/`, `bsp/`, `components/`, `build_freertos.sh` and `VERSION.txt`.

</div>

## Install the build tools { #host-tools }

<div class="ipro-steps" markdown>

1. **Install CMake, GNU Make and Python.**

    === "macOS"

        ```bash
        xcode-select --install          # provides make
        brew install cmake python3
        ```

    === "Linux"

        ```bash
        sudo apt update
        sudo apt install -y cmake make python3
        ```

        Debian / Ubuntu shown; on other distributions install the equivalent packages. On Linux x86-64, when no `cmake` is on `PATH`, the build falls back to the CMake 3.15 in the SDK's `tools/cmake/`.

    === "Windows"

        Online Setup installs CMake, Ninja and Python with **Full environment** or **Build tools only**; see [Windows Setup & VS Code](windows.md#online-setup).

2. **Check the versions** (macOS / Linux):

    ```bash
    cmake --version     # 3.15 or later; Zephyr needs 3.20 or later
    make --version      # first line: GNU Make
    python3 --version   # 3.8 or later
    ```

</div>

## Install the RISC-V toolchain { #toolchain }

<div class="ipro-steps" markdown>

1. **Put it at the default path.**

    === "macOS / Linux"

        Unpack the archive from INTELPRO so that this file exists:

        ```text
        /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc
        ```

    === "Windows"

        Online Setup installs the Windows toolchain GCC 13.1.1 and prepares the SDK for it, so SDK V2.2.0 builds as it is; the images differ from those GCC 14 builds on macOS and Linux. See [Windows Setup & VS Code](windows.md#online-setup).

2. **Check that it runs** (macOS / Linux):

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc --version
    ```

    The first line starts with `riscv64-unknown-elf-gcc` and shows version 14.x.

3. **Somewhere else?** Set the compiler prefix `CROSS_COMPILE` (with the trailing hyphen). The build takes `CROSS_COMPILE` from the command line or the environment first, then `CONFIG_CROSS_COMPILE` from the application's `.config`, then the default path.

    ```bash
    export CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-
    ```

    To keep it, add the line to `~/.zshrc` (macOS) or `~/.bashrc` (Linux).

</div>

## Install IntelProCube { #intelprocube }

IntelProCube, the flashing and OTA tool for IPRO6 and IPRO7, is published on [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases); this site uses 0.7.0.1. On Windows, Online Setup installs 0.7.0, whose files for IPRO7 and the Reef are the same as 0.7.0.1's; see [Windows Setup & VS Code](windows.md). To flash an IPRO6S, install 0.7.0.1 as well, following the [IntelProCube README](https://github.com/INTELPRO-INC/ipro-cube#windows).

<div class="ipro-steps" markdown>

1. **Download and check it.**

    === "macOS"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-macos-arm64.tar.gz
        shasum -a 256 IntelProCube-0.7.0.1-macos-arm64.tar.gz
        ```

        You should see `c3a8bf7eca2a48c3f9bf40c3241ddf6aec5155688f2a92f40a84cc47f7633bc4`. The macOS package needs Apple silicon. If you download it with a browser instead, run `xattr -d com.apple.quarantine IntelProCube-0.7.0.1-macos-arm64.tar.gz` before extracting, or macOS stops the programs inside.

    === "Linux"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-linux-x64.tar.gz
        sha256sum IntelProCube-0.7.0.1-linux-x64.tar.gz
        ```

        You should see `efc5765ca402d0af00b42489dd61a74481531875b871517af5c0bca9d7387df9`. The Linux package is for x86-64.

    If the value differs, download the file again. The values for every version are in the release's `SHA256SUMS.txt`.

2. **Extract it.**

    === "macOS"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-macos-arm64.tar.gz -C ~/ipro
        ```

    === "Linux"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-linux-x64.tar.gz -C ~/ipro
        ```

    This gives `~/ipro/IntelProCube`, written `<IntelProCube>` on this site. Run the command-line tool from that directory: it reads the chip settings, partition tables and boot2 images from `chips/`.

3. **Check that it runs.**

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --help
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --help
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --help
        ```

    The output starts with the usage summary:

    ```text
    usage: ipro_iot_tool_macos [-h] [--list-ports] --chipname CHIPNAME
                               [--interface INTERFACE] [--port PORT]
                               [--baudrate BAUDRATE] [--xtal XTAL]
                               [--chip-variant CHIP_VARIANT] [--dts DTS] [--pt PT]
                               [--boot2 BOOT2] [--firmware FIRMWARE] [--mfg MFG]
    ...
    ```

4. **Let `build_freertos.sh` find it** (macOS / Linux): set `IPRO_FLASH_TOOL`, or put `<IntelProCube>` on `PATH`.

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ```

</div>

## Connect the console cable { #usb-serial }

The Reef has no USB-to-UART chip on board: its USB-C carries power and the board's own USB device functions, while the console and flashing go through the adapter or IPRO Debug Probe on U6.

<div class="ipro-steps" markdown>

1. **Plug the adapter or Debug Probe into the computer** (the board can stay disconnected) and look for the new serial port:

    === "macOS"

        ```bash
        ls /dev/cu.*
        ```

        A USB-to-UART adapter appears as `/dev/cu.usbserial-XXXX` (the name depends on the adapter). The IPRO Debug Probe adds two `/dev/cu.usbmodem…` ports; the one ending in `02` is the console.

    === "Linux"

        ```bash
        ls /dev/ttyUSB* /dev/ttyACM*
        ```

        An adapter usually appears as `/dev/ttyUSB0`; the IPRO Debug Probe adds two `/dev/ttyACM*` ports.

    === "Windows"

        Open **Device Manager → Ports (COM & LPT)** and compare before and after plugging in: the new entry is the port, for example `COM5`. The IPRO Debug Probe adds two.

2. **No new port?** Try a cable that carries data. If the system does not recognise the adapter, install the driver from the adapter's maker; for the Debug Probe, contact INTELPRO.

3. **Linux permissions:** if opening the port fails with `Permission denied`, check the group that owns it with `ls -l /dev/ttyUSB0` (often `dialout`), add yourself to that group and log in again:

    ```bash
    sudo usermod -aG dialout $USER
    ```

</div>

How to tell the Debug Probe's two ports apart, and the USB devices each Reef application presents on USB-C: [Flashing & Serial Console: Recognise the ports](flash-and-monitor.md#ports).

## Verify { #verify }

Build the out-of-box firmware from the SDK root (macOS / Linux):

```bash
./build_freertos.sh ipro7ai_reef_demo
```

A successful build prints:

```text
Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

→ Building ipro7ai_reef_demo...
✓ Build succeeded (14s)
  Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
  Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
```

Build time and image size vary slightly with the host and toolchain. On Windows, check with `IPRO: Build` in the VS Code Extension or with `build_freertos.ps1`; see [Windows Setup & VS Code](windows.md#verify).

## How the two environments differ { #choose }

| Task | macOS / Linux | Windows |
|---|---|---|
| Install the tools | system package manager, plus the toolchain from INTELPRO and IntelProCube from GitHub | Online Setup (toolchain, CMake / Ninja / Python, IntelProCube, OpenOCD, VS Code Extension) |
| Build | `make -C apps/<category>/<app>` or `./build_freertos.sh` | `IPRO: Build` in the VS Code Extension |
| Flash | the IntelProCube command-line tool, or `./build_freertos.sh … flash` | `ipro_iot_tool.exe` |
| Console | a terminal program such as `screen` or `picocom`; `tools/serial_monitor.py` | a terminal program such as PuTTY, or the Extension's Serial Monitor |
| Automation (`build_freertos.sh`, `tools/serial_monitor.py`) | available | not available: both need bash and POSIX termios |
| Zephyr (`tools/zephyr/`) | available | no Windows procedure in the SDK |

Command-line examples on this site are written for macOS / Linux.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| The computed SHA-256 differs from the release page | incomplete or damaged download | delete the file and download it again |
| `No cmake found. Install cmake or provide bundled cmake at …` | no `cmake` on `PATH`, and the bundled one cannot run on this host (it is Linux x86-64 only) | install CMake 3.15 or later as in [Install the build tools](#host-tools) |
| `riscv64-unknown-elf-gcc: No such file or directory` | the toolchain is not at `/opt/toolchain/riscv_ipro7/` | set `CROSS_COMPILE` as in [Install the RISC-V toolchain](#toolchain) |
| `Flash tool not found: ipro_iot_tool_macos` | `IPRO_FLASH_TOOL` is not set and IntelProCube is not on `PATH` | step 4 of [Install IntelProCube](#intelprocube) |
| No new serial port after plugging in the adapter | charge-only USB cable, or a missing driver | change the cable; install the adapter maker's driver |
| `Permission denied` when opening the port on Linux | you are not in the port's group | join `dialout` (or the group shown) and log in again |
| A terminal hangs after opening `/dev/tty.*` on macOS | `tty.*` waits for carrier detect | use `/dev/cu.*` |

## Next steps { #next-steps }

- On Windows: [Windows Setup & VS Code](windows.md)
- Host ready: [First FreeRTOS Application](first-app-freertos.md)
- Command-line reference: [macOS / Linux Command Line](command-line.md)
