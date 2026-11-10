---
title: "Get Started"
description: From a fresh computer and an IPRO7AI Reef EVK to a running board — hardware and tools to prepare, then build and flash the out-of-box firmware until the console answers.
migrate_from: []
---

# Get Started

Work through these pages in order to go from a fresh computer to the out-of-box firmware `ipro7ai_reef_demo` running on an IPRO7AI Reef EVK V4.0, checked with `reef selftest`. Every procedure on this site is written for this board; applications for the IPRO7 EVB, IPRO7AI EVK, IPRO6S EVK and IPRO7 Arduino board need those boards — contact INTELPRO.

## What you need { #what-you-need }

| Item | Notes | Where to get it |
|---|---|---|
| IPRO7AI Reef EVK V4.0 | silkscreen "IPRO7AI REEF EVK V4.0" | INTELPRO |
| USB-C cable | the board's only power input; use a data cable (some applications use the board's USB device port) | your own |
| Console cable (one of) | a 3.3 V USB-to-UART adapter with an SH1.0 6-pin plug for U6, or the IPRO Debug Probe with a pin-reversed cable to U6 | adapter: your own; Debug Probe: INTELPRO |
| Host | macOS or Linux (bash) runs every SDK command-line tool; Windows works through the installer, the VS Code Extension and `build_freertos.ps1` | — |
| RISC-V toolchain | GCC 14 (GCC 13.1.1 on Windows), `riscv64-unknown-elf-gcc` | macOS / Linux: INTELPRO; Windows: installed by Online Setup |
| IntelProCube v0.6.3 | the flash tool: `ipro_iot_tool_macos`, `ipro_iot_tool_linux`, `ipro_iot_tool.exe` | macOS / Linux: INTELPRO; Windows: installed by Online Setup |
| SDK | `IPRO-SDK-V2.2.0.tar.gz` | [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) |
| Optional | OV5640 FLEX-24 camera module, microSD card, 8 Ω speaker (on J_SPK), headphones | your own; they complete the camera, slot and speaker steps of the self-test |

How to wire the console cable: [IPRO7AI Reef EVK: Debug connector U6](../hardware/boards/reef-evk.md#debug-connector).

!!! tip "Graphical development environment"
    IPRO Workbench (macOS on Apple silicon, Windows 11) puts setting up the tools, building, flashing and the serial monitor in one window; see [IPRO Workbench](../workbench/index.md).

## In this order { #path }

<div class="grid cards" markdown>

-   :material-tools:{ .lg } **1. [Set Up Your Host](environment.md)**

    ---

    Download and verify the SDK, install CMake, make, Python, the RISC-V toolchain and IntelProCube, and prove the setup with one build.

-   :material-microsoft-windows:{ .lg } **2. [Windows Setup & VS Code](windows.md)**

    ---

    Windows only: install the SDK, the tools and the VS Code Extension with Online Setup in one go, then build and flash in VS Code or with `build_freertos.ps1`.

-   :material-developer-board:{ .lg } **3. [First FreeRTOS Application](first-app-freertos.md)**

    ---

    Set the switches, wire the console, then build, flash and run `ipro7ai_reef_demo` and check the LED, speaker, SD slot and camera with `reef selftest`.

-   :material-usb-port:{ .lg } **4. [Flashing & Serial Console](flash-and-monitor.md)**

    ---

    Reference: the four ways into download mode, IntelProCube options and partition tables, boot2 and `mfg` data, the console and how to recognise ports.

-   :material-console:{ .lg } **5. [macOS / Linux Command Line](command-line.md)**

    ---

    Reference: `make -C`, `DEFCONFIG=`, build directories and outputs, and the actions, options and environment variables of `build_freertos.sh`.

</div>

## Next steps { #next-steps }

Once the board runs the out-of-box firmware, continue with three hands-on tutorials:

- [Build and Flash Workflow](../tutorials/build-and-flash.md): the everyday edit, build, flash and monitor loop.
- [Create Your First Application](../tutorials/first-own-app.md): start an application of your own and run it on the Reef.
- [Test Your Application](../tutorials/testing.md): test your application on the host and on the board.

The full board reference (switches, pins, expansion header) is on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md). The Zephyr boards in this release are the IPRO7 EVB and IPRO7AI EVK; there is no Reef board, see [Zephyr RTOS](../guides/zephyr.md).
