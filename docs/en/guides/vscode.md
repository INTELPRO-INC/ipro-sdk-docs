---
title: "VS Code Extension"
description: IPRO SDK Extension 3.3.0 features, the build and flash workflow, settings, commands, and using it with SDK V2.1.0
migrate_from:
  - "vscode-extension.html"
not_migrated:
  - "vscode-extension.html#installation — installation steps live in get-started/windows.md"
  - "vscode-extension.html#cli-tools — the IntelProCube command line belongs on the flashing page"
---

# VS Code Extension

IPRO SDK Extension 3.3.0 (identifier `ipro.ipro-sdk-extension`) brings FreeRTOS project browsing, CMake builds, IntelProCube flashing, a serial console and memory analysis into VS Code. It requires VS Code 1.102 or later. The extension is not part of the SDK package and is versioned separately from the SDK and the Windows installer; installation is covered in [Windows Setup & VS Code](../get-started/windows.md).

!!! abstract "At a glance"
    - Version 3.3.0; settings use the `ipro.*` namespace. The `devtool.*` settings and `IPRO SDK:` command names in older documents no longer apply.
    - SDK V2.1.0 is imported as a folder; extract the `.tar.gz` first.
    - Flashing uses IntelProCube; the console uses the extension's built-in serialport, with separate flash and console baud rates.
    - 3.3.0 has no general-purpose GDB debug adapter.

## Features { #features }

| Feature | What it does |
|---|---|
| Projects / Target | Browse projects by category, with pins and recents; shows the active project, profile, UART, probe and tool status |
| Control Center | Connection, console baud rate and operation status in one place, with build, flash, monitor and component update actions |
| Build / Batch Build | CMake configuration with Make or Ninja builds, debug / release / size profiles, jump from Problems to source, `compile_commands.json` integration |
| Menuconfig | Graphical `.config` editor that can load a defconfig |
| Flash / Monitor | Flash with IntelProCube; the built-in serialport console works on Windows |
| Analysis / Debug | Memory Map, Decode Crash Report, Pin Function Lookup; Register Explorer needs a compatible CCI connection |

The SDK build reads only `.config` and does not resolve Kconfig `select` or `depends on`. After editing in Menuconfig, check that dependent options are written into `.config`; see [Build System & Configuration](build-system.md#configuration).

## Control Center { #control-center }

Press F1 and run `IPRO: Open Control Center`. It shows the current SDK and project, the UART, the settings and the actual console baud rate, and enables actions according to what is going on. Opening the panel never flashes or resets the board. The Control Center arrived in 3.2.4; 3.3.0 added the component update entry.

## First build { #workflow }

<div class="ipro-steps" markdown>

1. Run `IPRO: Go to Project…` and pick `ipro7ai_reef_demo` in the platform category.
2. Run `IPRO Config: Select Build Profile` and choose debug, release or size.
3. Run `IPRO Setup: Run Diagnostics` to check the actual paths of the SDK, compiler, CMake, Ninja and Python.
4. Run `IPRO: Build` and watch the Terminal; errors in Problems jump to the source.
5. Check that `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin` and the `.elf` were produced.

</div>

The Windows installer defaults to Ninja; set `ipro.generator` to `auto`, `make` or `ninja`. `IPRO: Batch Build` builds several selected projects in one go. After changing the SDK or tool paths, Clean and rebuild so no stale cache is reused.

## Flashing and the console { #flash }

<div class="ipro-steps" markdown>

1. Choose IntelProCube with `IPRO Setup: Select Flash Tool`, or set `ipro.flashToolPath`.
2. Connect the board, run `IPRO: Select Serial Port` and pick the probe's UART port. The CCI port is for register access and cannot be used for the console or flashing.
3. In `IPRO Config: Configure Flash…`, check the chip variant, flash target, partition table and baud rate. The chip variant must match the actual board: the IPRO7AI Reef EVK uses `IPRO7AI`, for example.
4. Run `IPRO: Flash` and check the tool's verification and success messages. The extension releases its own console connection first; close any other program holding the port.
5. Set the console baud rate to match the firmware with `IPRO Config: Set Monitor Baud Rate`, then run `IPRO: Serial Monitor`. Close and reopen the console after changing the rate.

</div>

| Setting | Meaning |
|---|---|
| `ipro.baudRate` | Flashing baud rate, default 921600 |
| `ipro.monitorBaudRate` | Console baud rate, default 115200; must match the firmware |
| `ipro.chipVariant` | The board's flashing variant, not a build profile |

Most applications use a 115200-baud console; `ipro7ai_evk_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_rps`, `ipro7_uvc_cam`, `ipro_epd_el036` and a few others use 921600. The application's `CONFIG_PLATFORM_UART_BAUDRATE` is authoritative.

Since 3.2.0 the console uses the built-in serialport, so on Windows it does not depend on the SDK's `serial_monitor.py`, and opening it does not reboot the board. To reboot, run `IPRO: Reset Board` or type `reboot` in the firmware console. Flashing from the command line is covered in [Flashing & Serial Console](../get-started/flash-and-monitor.md).

## Memory and debug tools { #memory-map }

- `IPRO Analyse: Memory Map`: after a build, shows each memory region, per-component usage and the difference from the previous build; exports CSV or Markdown. Whether an image fits is still decided by the linker output and the actual partition table.
- `IPRO Analyse: Decode Crash Report`: turns an exception backtrace into source locations.
- `IPRO Debug: Pin Function Lookup`: looks up pin functions.
- `IPRO Debug: Register Explorer`: needs a compatible probe, a CCI connection and the right board settings.

Extension 3.3.0 has no general-purpose GDB debug adapter, and installing OpenOCD does not by itself give you F5 source-level debugging.

## Component updates { #component-updates }

Run `IPRO Setup: Update Components` from F1 or from the Control Center.

| Source | Behavior |
|---|---|
| Extension VSIX | Installs the selected VSIX and reloads the window; does not update the SDK or tools |
| SDK ZIP | Extracts and checks the SDK structure; you can enter a SHA-256 supplied by INTELPRO |
| SDK Folder | Select an extracted root containing `CMakeLists.txt`, `apps` and `bsp`; extract `.tar.gz` and `.7z` archives yourself first |
| SDK Git | Takes a snapshot of an HTTPS or SSH repository you can access, at a branch or tag, and records the commit; SSH trust and credentials must be set up beforehand |

- After choosing the source, pick the parent directory for versions and a new version name that does not exist yet; Output → IPRO SDK shows progress and the log.
- When the import finishes you can open it in a new window; the SDK Root, toolchain and current window do not switch automatically. Run Diagnostics and build an official example first, then move your own changes over one at a time, and keep the old SDK so you can go back.
- Each version directory contains `sdk\` (the SDK root), `update.json` (source, time, checksum or Git commit) and `update.log`. A failed or cancelled import keeps the unfinished directory and its log; retry under a new name.
- A Git import is a snapshot, not a working tree you can pull into. Submodules, unresolved LFS pointers and symbolic links are not supported, and the toolchain is not updated.

## Commands { #shortcuts }

F1 or Ctrl+Shift+P opens the command palette. 3.3.0 declares no default shortcuts for flashing or the console; bind your own if you like. Ctrl+Shift+B uses VS Code's build task configuration.

| Command | Purpose |
|---|---|
| `IPRO: Open Control Center` | Open the Control Center |
| `IPRO Setup: Update Components` | Update from a VSIX, SDK ZIP, folder or Git snapshot |
| `IPRO Setup: Set SDK Root` | Set the SDK root |
| `IPRO Setup: Run Diagnostics` | Check SDK and tool paths |
| `IPRO: Go to Project…` | Find and switch projects |
| `IPRO Config: Select Build Profile` | Choose debug, release or size |
| `IPRO: Build` | Build the current project |
| `IPRO: Clean` | Remove the current project's build output |
| `IPRO: Batch Build` | Build several projects |
| `IPRO Config: Menuconfig` | Edit the configuration |
| `IPRO Config: Configure Flash…` | Set the chip variant and flashing parameters |
| `IPRO: Select Serial Port` | Choose the UART |
| `IPRO Config: Set Monitor Baud Rate` | Set the console baud rate |
| `IPRO: Flash` | Flash the firmware |
| `IPRO: Serial Monitor` | Open the console |
| `IPRO: Close Serial Monitor` | Close the console and release the port |
| `IPRO: Build, Flash & Monitor` | Build, flash and open the console in sequence |
| `IPRO: Reset Board` | Reset the board through a compatible probe |
| `IPRO Analyse: Memory Map` | Analyze memory usage |
| `IPRO Analyse: Decode Crash Report` | Decode exceptions and backtraces |
| `IPRO Debug: Pin Function Lookup` | Look up pin functions |
| `IPRO Debug: Register Explorer` | Inspect registers over CCI |

## FAQ { #faq }

| Symptom | What to do |
|---|---|
| IPRO commands are missing | Check the VSIX version, profile, Workspace Trust and SDK root, then reload the window |
| Switching the SDK Root has no effect | Workspace and folder settings can override User settings; the path Diagnostics reports is what counts |
| Garbled console or the old baud rate | Check the firmware's console rate and `ipro.monitorBaudRate`, then close and reopen the console |
| The probe is detected but CCI does not respond | USB enumeration does not mean the board-side CCI link works; check the wiring and board settings |
| The flash tool is not found | Pick it with `IPRO Setup: Select Flash Tool` and make sure the IntelProCube directory contains `ipro_iot_tool.exe` |

## Version history { #version }

| Version | Changes |
|---|---|
| 3.3.0 | Independent component updates |
| 3.2.4 | Control Center |
| 3.2.3 | Better serial port hand-over between console and flashing; separate UART and CCI port selection |
| 3.2.2 | Separate console baud rate |
| 3.2.1 | Fixed Windows tool path settings |
| 3.2.0 | Built-in serialport console |

The SDK source package, the extension VSIX and the full Windows installer are versioned separately. The SDK package contains no VSIX; the installer you receive and the Extensions panel show the actual version.

## Using SDK V2.1.0 { #sdk-2-1-0 }

<div class="ipro-steps" markdown>

1. Download, verify and extract SDK V2.1.0 to a new directory as described in [Windows Setup & VS Code](../get-started/windows.md#sdk-2-1-0).
2. Import the extracted folder with `IPRO Setup: Update Components`, or select it directly with `IPRO Setup: Set SDK Root`.
3. Reopen the SDK and run `IPRO Setup: Run Diagnostics`.

</div>

- FreeRTOS applications in V2.1.0 support IPRO7 only; keep SDK V2.0.1 for IPRO6S development, see [IPRO6S](../hardware/chips/ipro6s.md).
- The SDK README specifies a GCC 14 toolchain. The toolchain version in the Windows installer is listed in [Windows Setup & VS Code](../get-started/windows.md); confirm it is compatible before using V2.1.0, and keep a working older environment until the new version has been built and verified on a board.
- For Make builds on Windows, `project.build` uses the `cmake` on your PATH; check its version.

## Related documents { #related }

- [Windows Setup & VS Code](../get-started/windows.md): install the Extension and point it at SDK V2.1.0.
- [Flashing & Serial Console](../get-started/flash-and-monitor.md): the IntelProCube command-line tool and per-board flash settings.
- [Build System & Configuration](build-system.md): `.config` and alternate configurations.
