---
title: "Shortcuts, Commands and Settings"
description: Reference for IPRO Workbench 0.1.1 - keyboard shortcuts, IPRO commands, ipro.* settings, the MCP tools and the files and folders the IDE uses.
---

# Shortcuts, Commands and Settings

Keyboard shortcuts, commands, settings, MCP tools and file locations of IPRO Workbench 0.1.1.

## Keyboard shortcuts { #shortcuts }

| Action | macOS | Windows |
|---|---|---|
| Build, Flash and Monitor | `Cmd+Alt+R` | `Ctrl+Alt+R` |
| Build | `Cmd+Alt+B` | `Ctrl+Alt+B` |
| Flash | `Cmd+Alt+U` | `Ctrl+Alt+U` |
| Serial Monitor | `Cmd+Alt+M` | `Ctrl+Alt+M` |
| Command Palette | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Open Settings | `Cmd+,` | `Ctrl+,` |
| Save (settings, pins, GATT, files) | `Cmd+S` | `Ctrl+S` |

## IPRO commands { #commands }

You can find all of the commands below by typing `IPRO` in the command palette. Most of them are also on the IPRO menu, the toolbar or a context menu.

| Command | Purpose |
|---|---|
| **IPRO Home** | Open IPRO Home |
| **Open SDK…** / **Install SDK from GitHub…** | Open or install an IPRO SDK |
| **Check Environment** / **Fix Environment** | Check the development environment again; install the missing items |
| **Select Application…** / **New Application…** / **Copy as New Application…** | Manage applications |
| **Select Board…** / **Select Port…** | Change the board or the serial port |
| **Select Toolchain…** / **Select IntelProCube…** | Use tools that are already on this computer instead |
| **Build, Flash and Monitor** / **Build** / **Flash** / **Stop** | Run and stop |
| **Reconfigure and Build** / **Clean** | Run the CMake configuration again; delete the build results |
| **Reset Board** | Reset the board through the probe |
| **Serial Monitor** / **Open Monitor on Another Port…** | Open a monitor |
| **Filter Monitor Output…** / **Show Monitor Timestamps** / **Save Monitor Output…** | Display and save the monitor output |
| **Serial Plotter** | Plot the numbers the board prints as curves |
| **Settings (Kconfig)…** / **Menuconfig** / **Open .config** | Change the application settings |
| **Pin Configuration…** | Configure pins and generate code |
| **GATT Configuration…** | Define BLE services and characteristics and generate code |
| **Memory Map** | See what uses the memory |
| **Partition Table** / **AI Model…** | Partition table view; check and write an NPU model |
| **Run Tests on Board** | Reset the board and collect the Unity test results |
| **RF Test (DTM)…** / **Wi-Fi Throughput (iperf)…** / **Power…** | RF, Wi-Fi throughput and power measurements |
| **Crash Dumps…** | Open crash dumps collected earlier |
| **Register Reference** | Look up peripherals, registers and fields |
| **Ask AI About the Last Crash** / **Connect an AI Assistant (MCP)…** | AI assistant |

## Settings { #settings }

Open Settings and search for `ipro` to see the following items.

| Setting | Description |
|---|---|
| `ipro.sdk.path` | IPRO SDK folder to use when the open folder is not an SDK |
| `ipro.tools.base` | Where the IDE installs tools. Empty means `IPRO/tools` in the home folder |
| `ipro.toolchain.prefix` | Cross-compile prefix. Empty means found automatically |
| `ipro.flashTool.path` | IntelProCube folder or executable. Empty means found automatically |
| `ipro.build.profile` | Build profile: Debug, Release, MinSizeRel |
| `ipro.build.generator` | CMake generator: auto, Unix Makefiles, Ninja |
| `ipro.build.memoryBudget` | Largest share of each memory region a build may use, in percent, e.g. `{ "flash": 90 }` |
| `ipro.build.failOverBudget` | A build over the memory budget fails |
| `ipro.board.id` | Board. auto follows the application's `.config` |
| `ipro.board.port` | Serial port for flashing and the monitor. Empty picks the probe's UART |
| `ipro.flash.baudRate` | IntelProCube baud rate |
| `ipro.run.openMonitor` | Open the serial monitor after a successful flash; on by default |
| `ipro.monitor.baudRate` | Console baud rate of the serial monitor, 115200 by default |
| `ipro.monitor.timestamps` | Start each monitor line with the time it came |
| `ipro.monitor.filter` | Show only monitor lines matching this regular expression |
| `ipro.monitor.logToFile` | Save the full content of every monitor session to the application's `build/logs` |
| `ipro.mcp.enabled` / `ipro.mcp.port` | MCP server for AI assistants outside the IDE; on by default, port 41730 |
| `ipro.macos.probeDownloadMode` | macOS: hold the IPRO Debug Probe download strap while flashing |
| `ipro.macos.checkQuarantine` | macOS: check the tools for the quarantine flag at startup |

## MCP tools { #mcp-tools }

AI assistants outside the IDE see the following tools through MCP (the names are the MCP tool names). The built-in IPRO AI assistant uses the same set of tools. How to connect an assistant: [AI Assistant](ai.md#mcp).

| Tool | Purpose |
|---|---|
| `ipro_get_target` | The SDK, the current application, board and serial port, environment problems and the last build result |
| `ipro_list_applications` | List all applications in the SDK |
| `ipro_select_application` | Switch the current application |
| `ipro_build` | Build the current application; returns errors, warnings and memory usage |
| `ipro_get_build_output` | Read the latest output of IPRO Build or IPRO Flash |
| `ipro_flash` | Flash the latest build and open the monitor |
| `ipro_reset_board` | Reset the board through the probe |
| `ipro_read_monitor` | Read the latest lines the board printed on the monitor |
| `ipro_board_tests` | The firmware the board booted last time and the Unity test results |
| `ipro_get_settings` / `ipro_set_settings` | Read and change the application's Kconfig settings |
| `ipro_get_pins` / `ipro_set_pins` | Read and change the pin configuration and generate code |
| `ipro_get_gatt` / `ipro_set_gatt` | Read and change the GATT services and generate code (a dry run checks without writing) |
| `ipro_memory_map` | Usage of each memory region and the largest libraries and object files |
| `ipro_partition_table` | The partition table that flashing writes, and its check results |
| `ipro_ai_model` | Check whether an NPU model fits the application and its partition table |
| `ipro_crash_dump` | The exception and call chain of the latest crash dump |
| `ipro_decode_addresses` | Decode code addresses into functions, files and line numbers |
| `ipro_lookup_register` | Look up a register by name or address |

## File locations { #file-locations }

| Location | Contents |
|---|---|
| `IPRO/tools/<tool>/<version>` in the home folder | Tools installed by **Fix Environment** (on Windows, `%USERPROFILE%\IPRO\tools`) |
| `IPRO/SDK/<version>` in the home folder | SDKs installed by **Install SDK from GitHub…** |
| `.ipro-ide` in the home folder | IDE settings and the MCP access token (`mcp.json`) |
| `apps/<category>/<name>/build` | Build results of the application (firmware, ELF, map file) |
| `apps/<category>/<name>/build/logs` | Full monitor logs (when **Log To File** is on) |
| `apps/<category>/<name>/build/crash` | Collected crash dumps |
| `apps/<category>/<name>/pins.yaml` | Pin configuration; `app_pins.h` and `app_pins.c` are generated from it |
| `apps/<category>/<name>/gatt.yaml` | GATT services; `app_gatt.h` and `app_gatt.c` are generated from it |
