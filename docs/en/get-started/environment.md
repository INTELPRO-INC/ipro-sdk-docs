---
title: "Choose Your Environment"
description: What SDK V2.1.0 contains and where to get it, the hardware and tools you need, and how the Windows and macOS / Linux environments differ.
migrate_from:
  - "getting-started.html#sdk-2-1-0"
  - "getting-started.html#prerequisites"
---

# Choose Your Environment

You can develop with the IPRO SDK on Windows, using an installer and the VS Code Extension, or on macOS / Linux from the command line. Download the SDK, get your board and the separately supplied tools ready, then pick an environment from [the comparison below](#choose).

## SDK V2.1.0 { #sdk-2-1-0 }

Download `IPRO-SDK-V2.1.0.tar.gz` and its checksum file `IPRO-SDK-V2.1.0.tar.gz.sha256` from the [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0). The installation pages for each environment show how to verify and unpack them.

| Contents | Details |
|---|---|
| FreeRTOS applications | 35, all for the IPRO7 family, covering the IPRO7 EVB, IPRO7AI EVK and IPRO7AI Reef EVK |
| Zephyr RTOS | The SDK is also a Zephyr v4.4.0 module, with the boards `ipro7_evb` and `ipro7ai_evk` |
| Host tools | `build_freertos.sh` (build, flash, monitor), `tools/serial_monitor.py` (console), `tools/zephyr/` (Zephyr workspace and flashing scripts) |

!!! info "Obtained separately"
    - **RISC-V toolchain** (`riscv64-unknown-elf-gcc`): not included in V2.1.0; contact INTELPRO.
    - **IntelProCube v0.6.3 command-line flasher** (`ipro_iot_tool.exe`, `ipro_iot_tool_macos`, `ipro_iot_tool_linux`): not included in V2.1.0; contact INTELPRO.
    - **Zephyr and its modules**: downloaded from GitHub the first time you run `tools/zephyr/bootstrap.sh`.

## Requirements { #prerequisites }

**Hardware**

- A board: the IPRO7AI Reef EVK (used by the getting-started examples), the IPRO7AI EVK or the IPRO7 EVB.
- The Reef EVK needs two cables: a USB-C cable for power (the Reef is powered from USB-C only) and a USB-to-UART cable on the U6 console connector (SH1.0).
- Other boards: a USB serial connection to the console UART0 (GPIO20 TX / GPIO21 RX); see the [board pages](../hardware/index.md) for wiring.

**Software**

| Item | Windows (VS Code) | macOS / Linux (command line) |
|---|---|---|
| SDK | V2.1.0 archive, unpacked into a new directory | Same |
| Toolchain | Get a V2.1.0-compatible build from INTELPRO | Default path `/opt/toolchain/riscv_ipro7/`, or set `CROSS_COMPILE` |
| Build tools | Installed by the Online Installer | CMake 3.19 or later, GNU Make, Python 3.8 or later; Zephyr needs CMake 3.20 or later |
| Flash tool | IntelProCube (`ipro_iot_tool.exe`) | IntelProCube (`ipro_iot_tool_macos` / `ipro_iot_tool_linux`) |
| Editor | VS Code with the IPRO SDK Extension | Any |

## How the environments differ { #choose }

| Task | Windows + VS Code | macOS / Linux command line |
|---|---|---|
| Install | Online Installer for the tools and the Extension; download and unpack SDK V2.1.0 yourself | Install the tools yourself; download and unpack the SDK |
| Build a FreeRTOS app | `IPRO: Build` in the Extension | `make -C apps/<category>/<app>` or `./build_freertos.sh <app>` |
| Flash | `IPRO: Flash` in the Extension, or run `ipro_iot_tool.exe` directly | Run the IntelProCube CLI directly, or `./build_freertos.sh <app> flash` |
| Console | The Extension's Serial Monitor, or any serial terminal | `tools/serial_monitor.py`, or any serial terminal |
| Zephyr | No Windows procedure in the SDK | `tools/zephyr/bootstrap.sh` and `west` |

The SDK's scripts (`build_freertos.sh`, `tools/zephyr/*.sh`) need bash, and `tools/serial_monitor.py` uses POSIX termios, so these tools run on macOS and Linux. Choose macOS / Linux if you need Zephyr or want to script builds, flashing and tests; choose Windows if you prefer working in the VS Code interface.

## Next steps { #next-steps }

- [Windows Setup & VS Code](windows.md)
- [macOS / Linux Command Line](command-line.md)
- Environment already set up: [First FreeRTOS Application](first-app-freertos.md)
