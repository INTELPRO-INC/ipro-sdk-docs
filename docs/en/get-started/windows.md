---
title: "Windows Setup & VS Code"
description: Install the tools and the VS Code Extension on Windows with IPRO SDK Online Setup, add SDK V2.2.0 by hand, build the IPRO7AI Reef EVK out-of-box firmware, flash it with ipro_iot_tool.exe and open the console in a terminal program.
migrate_from:
  - "windows-installation.html"
  - "vscode-extension.html#installation"
not_migrated:
  - "windows-installation.html#overview"
  - "windows-installation.html#package-contents"
  - "windows-installation.html#install-modes"
  - "windows-installation.html#full-install"
  - "windows-installation.html#extension-only"
  - "windows-installation.html#sdk-only"
  - "windows-installation.html#settings"
---

# Windows Setup & VS Code

On Windows, install the toolchain, build tools, IntelProCube and the VS Code Extension with IPRO SDK Online Setup, add SDK V2.2.0 by hand, build the IPRO7AI Reef EVK out-of-box firmware `ipro7ai_reef_demo`, then flash it with `ipro_iot_tool.exe` and see the console on a COM port.

!!! info "The installer does not install V2.2.0"
    Online Setup's catalog still lists SDK V1.2.1 as the stable SDK. Use the installer for the tools and the Extension, then add the SDK by hand as in [Add SDK V2.2.0](#get-sdk).

## Requirements { #requirements }

- Windows x64 with access to GitHub (Online Setup downloads its components from a public catalog and GitHub releases).
- VS Code 1.102 or later (the installer can download it).
- An IPRO7AI Reef EVK, a USB-C cable and a console cable; see [What you need](index.md#what-you-need).
- A toolchain that matches V2.2.0: V2.2.0 is built with GCC 14, while the installer picks the toolchain declared compatible with SDK V1.2.1. Ask INTELPRO for a Windows toolchain that matches V2.2.0.

## Install the tools { #online-3-4-0 }

<div class="ipro-steps" markdown>

1. **Download the installer** `IPRO-SDK-Online-Setup-3.4.0.exe` from the [Online Setup 3.4.0 release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/online-installer-v3.4.0); no GitHub sign-in is needed.

2. **Choose a directory:** run the installer and, under **Select Destination Location**, enter a new folder that does not exist yet (the installation root).

3. **Choose Full environment** under **Choose packages**. It installs the SDK, the RISC-V toolchain, the build tools (CMake, Ninja, Python), IntelProCube, OpenOCD and VS Code Extension 3.3.0. Keep the versions at **latest**: latest means the version each component marks as stable / compatible, not the newest GitHub release.

4. **Choose the extra tasks:** tick **Install VS Code from Microsoft if absent** if VS Code is not installed; keep **Install the selected Extension into VS Code** ticked; tick **Add installed tools to user PATH** to run the tools from an ordinary terminal.

5. **Check the summary and install:** on **Ready to Install**, check the directory, mode and versions, then click **Install**.

6. **Reopen VS Code and your terminals** so they pick up the new `PATH`.

</div>

## Add SDK V2.2.0 { #get-sdk }

<div class="ipro-steps" markdown>

1. **Download** `IPRO-SDK-V2.2.0.tar.gz` from the [IPRO-SDK-V2.2.0 release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) and note the SHA-256 published there.

2. **Verify** it in PowerShell:

    ```powershell
    Get-FileHash .\IPRO-SDK-V2.2.0.tar.gz -Algorithm SHA256
    ```

    The 64 hexadecimal characters in the `Hash` column must match the release page (case does not matter).

3. **Unpack into a new directory and check the version:**

    ```powershell
    tar -xzf .\IPRO-SDK-V2.2.0.tar.gz
    Get-Content .\IPRO-SDK-V2.2.0\VERSION.txt
    ```

    ```text
    IPRO SDK Release
    ========================================
    IPRO7: IPRO-SDK-V2.2.0
    IPRO6: IPRO-SDK-V2.2.0

    Release Date: 2026-11-03
    Base Commit: 60afd4ab
    ```

    `IPRO-SDK-V2.2.0\` contains `CMakeLists.txt`, `apps\` and `bsp\`.

</div>

## Set up the VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **Check that the Extension is installed:** search the Extensions view for `@installed IPRO`; IPRO SDK Extension (identifier `ipro.ipro-sdk-extension`) should be listed.

2. **Open the SDK** with **File → Open Folder…** on the `IPRO-SDK-V2.2.0` root, and grant Workspace Trust once you have checked the source.

3. **Set the SDK root:** press ++f1++, run `IPRO Setup: Set SDK Root` and choose the same directory.

4. **Check the environment:** run `IPRO Setup: Run Diagnostics` and check the paths of the SDK root, compiler, CMake, Python and flash tool. The compiler must be a toolchain that matches V2.2.0; the folder of the flash tool is `<IntelProCube>` in the steps below.

5. **Build the out-of-box firmware:** run `IPRO: Go to Project…`, choose `ipro7ai_reef_demo` in the platform category, then run `IPRO: Build`.

</div>

The other Extension commands and settings are in [VS Code Extension](../guides/vscode.md).

## Flash { #flash }

<div class="ipro-steps" markdown>

1. **Wire the board:** SW7 on CAM, SW8 on PWR, console cable on U6, USB-C plugged in; see [Set the switches and wire the board](first-app-freertos.md#connect).

2. **Find the COM port:** open **Device Manager → Ports (COM & LPT)**; the entry that appears when you plug in the adapter is the console, for example `COM5`. The IPRO Debug Probe adds two COM ports; see [Recognise the ports](flash-and-monitor.md#ports).

3. **Enter download mode:** hold SW1 (BOOT), press and release SW2 (RESET), release SW1.

4. **Flash** from the IntelProCube folder in PowerShell:

    ```powershell
    cd <IntelProCube>
    .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
        --port COM5 --baudrate 921600 `
        --pt chips/ipro7/partition/partition_cfg_2M.toml `
        --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

    Only a final `[All Success]` line means success; the tool exits 0 even on failure. The options are explained in [Flashing & Serial Console](flash-and-monitor.md#flash-tool).

</div>

## Console { #console }

<div class="ipro-steps" markdown>

1. **Open a terminal program:** in PuTTY choose **Serial**, set Serial line to `COM5` and Speed to `115200`, and click **Open**. Tera Term works too, as does the VS Code Extension's `IPRO: Serial Monitor` (pick the port with `IPRO: Select Serial Port`).

2. **Reset:** press SW2 (RESET). The window shows the boot banner `IPRO7AI Reef carrier demo`; press ++enter++ for the `ipro />` prompt.

3. **Self-test:** type `reef selftest`. The expected output is in [First FreeRTOS Application](first-app-freertos.md#verify).

</div>

Close the terminal program before flashing, or `ipro_iot_tool.exe` cannot open the COM port.

## Building from the command line { #command-line }

The SDK does not document a Windows command-line build, and `build_freertos.sh` and `tools/serial_monitor.py` need bash and POSIX termios, so they do not run on Windows. What the build scripts need on Windows:

- `cmake` and `python` on `PATH` (on Windows the build calls `python`, not `python3`).
- `CROSS_COMPILE=<toolchain dir>\bin\riscv64-unknown-elf-` (with the trailing hyphen) on the `make` command line: the applications' `.config` files hold the Unix path `/opt/toolchain/...` in `CONFIG_CROSS_COMPILE`, and Windows has no default path.
- GNU Make: Online Setup's build tools package contains CMake, Ninja and Python, not make.

## Verify { #verify }

- `IPRO: Build` produces:

    ```text
    apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

- The output of `ipro_iot_tool.exe` ends with `[All Success]`.
- After a reset the terminal shows the boot messages and `ipro />`, and `reef selftest` steps the LED through its colours and plays a 1 kHz tone.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| The installed SDK is V1.2.1 | the catalog does not list V2.x yet | add the SDK as in [Add SDK V2.2.0](#get-sdk) and point `IPRO Setup: Set SDK Root` at it |
| Windows warns of an unknown publisher or shows SmartScreen | the installer is not code-signed | follow your company's security policy; do not turn protection off |
| Diagnostics still shows the old SDK path | workspace or user settings point to the old SDK | run `IPRO Setup: Set SDK Root`, then Diagnostics again |
| No IPRO commands | the Extension is not in the current VS Code profile, or the workspace is not trusted | check the Extension, profile and Workspace Trust, then run `Developer: Reload Window` |
| `IPRO: Build` cannot find the compiler or fails to compile | toolchain does not match V2.2.0, or wrong path | get a V2.2.0 toolchain from INTELPRO and check the path in Diagnostics |
| No new COM port in Device Manager | charge-only USB cable, or missing adapter driver | change the cable; install the adapter maker's driver; for the Debug Probe contact INTELPRO |
| `ipro_iot_tool.exe` prints no `[All Success]` | the board is not in download mode, or a terminal program holds the COM port | close the terminal; enter download mode again with SW1 + SW2 |
| `flash jedec id: 00000000` | `--chip-variant IPRO7AI` is missing | add it and flash again |
| Garbage or nothing in the terminal | baud rate not 115200, board still in download mode, or RX/TX swapped | open at 115200; press SW2; swap RX and TX |

## Next steps { #next-steps }

- [First FreeRTOS Application](first-app-freertos.md): the self-test and commands of the out-of-box firmware.
- [Flashing & Serial Console](flash-and-monitor.md): other download-mode methods, partition tables, boot2 and `mfg` data.
- [VS Code Extension](../guides/vscode.md): Extension commands and settings.
