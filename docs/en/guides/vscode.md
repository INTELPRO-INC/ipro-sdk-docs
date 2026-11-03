---
title: "VS Code Extension"
description: IPRO SDK Extension 3.3.0 with SDK V2.2.0 — setting the SDK root, building, flashing the IPRO7AI Reef EVK, the serial monitor, memory analysis and the commands
migrate_from:
  - "vscode-extension.html"
not_migrated:
  - "vscode-extension.html#installation — installation steps live in get-started/windows.md"
  - "vscode-extension.html#cli-tools — the IntelProCube command line belongs on the flashing page"
---

# VS Code Extension

IPRO SDK Extension 3.3.0 (identifier `ipro.ipro-sdk-extension`) brings FreeRTOS project browsing, CMake builds, IntelProCube flashing, a serial console and memory analysis into VS Code 1.102 or later. It is not part of the SDK package and is versioned separately from the SDK and from IPRO SDK Online Setup, which installs it; installation is in [Windows Setup & VS Code](../get-started/windows.md).

!!! abstract "At a glance"
    - Online Setup 3.4.0 installs the Extension and the tools, but its catalog still lists SDK V1.2.1 as the stable SDK. Add SDK V2.2.0 by hand and point `IPRO Setup: Set SDK Root` at it.
    - SDK V2.2.0 is built with GCC 14; check that the compiler the Extension uses matches.
    - On the IPRO7AI Reef EVK, flash with chip variant `IPRO7AI` and the partition table the application uses; boot2 images and the `mfg` payload are written with the IntelProCube command line.
    - The console baud rate (`ipro.monitorBaudRate`) is separate from the flashing baud rate (`ipro.baudRate`).
    - No source-level (F5) debugging: installing OpenOCD does not set up a GDB debug adapter.

## Features { #features }

| Feature | What it does |
|---|---|
| Projects | Browse the applications by category, pin them and switch the active project (`IPRO: Go to Project…`, `IPRO: Select Project`) |
| Build / Batch Build | CMake configuration with Make or Ninja (`ipro.generator`), debug / release / size profiles, jump from Problems to source |
| Configuration | `IPRO Config: Menuconfig`, `IPRO Config: Open .config`, `IPRO Config: Load Defconfig` |
| Flash / Monitor | Flash with IntelProCube; built-in serial console with its own baud rate |
| Analysis / Debug | Memory Map, Decode Crash Report, Pin Function Lookup; Register Explorer needs a compatible CCI connection |

The SDK build reads `.config` as it is and does not resolve Kconfig `select` or `depends on`. After editing in Menuconfig, check that dependent options are written into `.config`; see [Build System & Configuration](build-system.md#configuration).

## Using SDK V2.2.0 { #sdk-2-2-0 }

<div class="ipro-steps" markdown>

1. Download, verify and unpack `IPRO-SDK-V2.2.0.tar.gz` from the [IPRO-SDK-V2.2.0 release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) into a new directory, as described in [Add SDK V2.2.0](../get-started/windows.md#get-sdk).
2. Open that directory with **File → Open Folder…** (it contains `CMakeLists.txt`, `apps` and `bsp`) and run `IPRO Setup: Set SDK Root` on it.
3. Run `IPRO Setup: Run Diagnostics` and check the SDK root, the compiler, CMake, Ninja, Python and the flash tool. The compiler must be a GCC 14 toolchain that matches V2.2.0; Online Setup installs the toolchain its catalog pairs with SDK V1.2.1. Ask INTELPRO for a matching toolchain, and set it with `ipro.toolchainPath` (the compiler prefix, ending in `riscv64-unknown-elf-`).

</div>

- Keep the previous SDK directory until V2.2.0 has been built and run on the board. Do not copy an old `build/` directory, CMake cache or `.vscode` folder into the new SDK.
- Workspace settings (`.vscode/settings.json`) can override user settings; the path Diagnostics reports is the one in use.

## Control Center { #control-center }

Press F1 and run `IPRO: Open Control Center` for the current SDK, project and connection with the common actions in one panel, then `IPRO Setup: Run Diagnostics` to check the tool paths. Settings can also be searched for `ipro` in VS Code's Settings.

## First build { #workflow }

<div class="ipro-steps" markdown>

1. Run `IPRO: Go to Project…` and pick `ipro7ai_reef_demo` in the platform category.
2. Run `IPRO Config: Select Build Profile` and choose debug, release or size.
3. Run `IPRO: Build` and watch the Terminal; errors in Problems jump to the source. A build has succeeded when it exits with code 0 and the image exists, not when CMake prints `Configuring done`.
4. Check that `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin` was produced.

</div>

`IPRO: Batch Build` builds several selected projects in one go. After changing the SDK or tool paths, run `IPRO: Clean` and build again so no stale cache is reused.

Most Reef applications ship their Reef configuration as a separate file (`defconfig_reef`, `defconfig_reef_ov5640` and so on); only `ipro7ai_reef_demo`, `ipro_reef_teach` and `ipro_agora_sentino` are Reef builds as they stand. The command-line form, `make -C <app> DEFCONFIG=<file>`, and the list of Reef configurations are in [Build System & Configuration](build-system.md#variants).

## Flashing and the console { #flash }

<div class="ipro-steps" markdown>

1. Choose IntelProCube with `IPRO Setup: Select Flash Tool`, or set `ipro.flashToolPath` to its folder.
2. Connect the board (SW7 on CAM, SW8 on PWR, console cable on U6, USB-C), run `IPRO: Select Serial Port` and pick the console port. With the IPRO Debug Probe, pick its UART port; the CCI port is for register access and cannot be used for the console or flashing.
3. In `IPRO Config: Configure Flash…` set the chip variant to `IPRO7AI` and the partition table to the one the application uses: `partition_cfg_2M.toml` for `ipro7ai_reef_demo` and the `ipro7_uvc_cam` webcam. Applications with their own table are listed in [Flashing & Serial Console](../get-started/flash-and-monitor.md#partition-tables).
4. Put the Reef in download mode: hold SW1 (BOOT), press and release SW2 (RESET), release SW1. Then run `IPRO: Flash` and check the tool's result. Close any other program that holds the port first.
5. Press SW2 to start the firmware. Check that `ipro.monitorBaudRate` matches the firmware (`IPRO Config: Set Monitor Baud Rate`), then run `IPRO: Serial Monitor`. To change the rate, run `IPRO: Close Serial Monitor` first, set the rate, and open the monitor again.

</div>

| Setting | Meaning |
|---|---|
| `ipro.baudRate` | Flashing baud rate, default 921600 |
| `ipro.monitorBaudRate` | Console baud rate, default 115200; must match the firmware |
| `ipro.chipVariant` | `--chip-variant` for the flash tool: `IPRO7AI` on the Reef |
| `ipro.partitionTable` | `--pt` for the flash tool; set it per application on the Reef |
| `ipro.flashTargets`, `ipro.activeFlashTarget` | Named flash configurations, to switch between settings without editing them each time |

Every Reef configuration has a 115200-baud console except `ipro7_jpeg_decode` (`defconfig_reef`), which uses 921600; the application's `CONFIG_PLATFORM_UART_BAUDRATE` is authoritative. The first flash of `ipro_ble_remote` (boot2 and the A/B table) and of `ipro_reef_teach` (the `mfg` payload) use the IntelProCube command line; see [Flashing & Serial Console](../get-started/flash-and-monitor.md#boot2-ab) and [Flash the Edge AI Firmware](../teach/firmware.md).

## Memory and debug tools { #memory-map }

- `IPRO Analyse: Memory Map`: after a build, shows each memory region and the usage per component. Whether an image fits is still decided by the linker output and the partition table you flash with.
- `IPRO Analyse: Decode Crash Report`: turns an exception backtrace into source locations.
- `IPRO Debug: Pin Function Lookup`: looks up pin functions.
- `IPRO Debug: Register Explorer`: needs a compatible probe, a working CCI connection and the right board settings. A probe that enumerates over USB does not prove that the CCI link to the board works.

Installing OpenOCD does not give you F5 source-level debugging: the Extension sets up no GDB debug adapter or launch configuration. Console logs and crash decoding are covered in [Debugging & Troubleshooting](../reference/debugging.md).

## Hands-on on the Reef { #hands-on }

The edit–build–flash loop in VS Code, on the out-of-box firmware.

<div class="ipro-steps" markdown>

1. **Check the console setting.** The firmware's console rate is set in its `.config`; `ipro.monitorBaudRate` must be the same:

    ```ini title="apps/platform/ipro7ai_reef_demo/.config (excerpt)"
    CONFIG_PLATFORM_UART_BAUDRATE=115200
    ```

2. **Change the code.** Open `apps/platform/ipro7ai_reef_demo/main.c` and change the banner line in `main()`:

    ```c title="apps/platform/ipro7ai_reef_demo/main.c (excerpt, edited)"
    ipro_platform_init();   /* heap + boot2 + log + shell */

    IPRO_LOGI(LOG_TAG, "==========================================");
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **Build** with `IPRO: Build`. The image is `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`.

4. **Flash** as in [Flashing and the console](#flash): download mode with SW1 + SW2, `IPRO: Flash` with chip variant `IPRO7AI` and `partition_cfg_2M.toml`, then SW2.

5. **Check the console** with `IPRO: Serial Monitor` at 115200. Among the first lines (log prefixes left out):

    ```text
    Build:<time>,<date>
    ...
      IPRO7AI Reef carrier demo - my build
    ```

    The `Build:` line shows the time of your build, and the banner shows your change. `reef selftest` checks the board blocks.

</div>

Restore the line, or flash the out-of-box image again, when you are done. Next: [Create Your First Application](../tutorials/first-own-app.md) and [Test Your Application](../tutorials/testing.md).

## Component updates { #component-updates }

Updates go through IPRO SDK Online Setup, which installs each component into a new directory and never overwrites the one in use:

| Online Setup mode | Installs | Settings it can switch |
|---|---|---|
| Full environment | SDK, toolchain, build tools (CMake, Ninja, Python), IntelProCube, OpenOCD, Extension | all of them |
| Toolchain only | RISC-V toolchain | `ipro.toolchainPath` |
| Build tools only | CMake, Ninja, Python | their paths |
| IntelProCube only | IntelProCube | `ipro.flashToolPath` |
| Extension only | the Extension VSIX | — |

SDK V2.2.0 is not in the installer's catalog: add it by hand ([Using SDK V2.2.0](#sdk-2-2-0)). After an update, reopen VS Code and run Diagnostics. To go back, point the settings at the directory you kept, or install the older VSIX with **Install from VSIX…**.

## Commands { #shortcuts }

F1 or Ctrl+Shift+P opens the command palette. The Extension declares no default key bindings; bind your own if you like.

| Command | Purpose |
|---|---|
| `IPRO: Open Control Center` | Open the Control Center |
| `IPRO Setup: Set SDK Root` | Set the SDK root |
| `IPRO Setup: Run Diagnostics` | Check SDK and tool paths |
| `IPRO Setup: Select Flash Tool` | Choose the IntelProCube folder |
| `IPRO: Go to Project…`, `IPRO: Select Project` | Find and switch projects |
| `IPRO Config: Select Build Profile` | Choose debug, release or size |
| `IPRO: Build` | Build the current project |
| `IPRO: Clean` | Remove the current project's build output |
| `IPRO: Batch Build` | Build several projects |
| `IPRO Config: Menuconfig`, `IPRO Config: Open .config` | Edit or open the configuration |
| `IPRO Config: Select Flash Target`, `IPRO Config: Configure Flash…` | Choose the flash target; set the chip variant, partition table and baud rate |
| `IPRO: Select Serial Port` | Choose the console / flashing port |
| `IPRO Config: Set Monitor Baud Rate` | Set the console baud rate |
| `IPRO: Flash` | Flash the firmware |
| `IPRO: Serial Monitor`, `IPRO: Close Serial Monitor` | Open the console; close it and release the port |
| `IPRO: Build, Flash & Monitor` | Build, flash and open the console in sequence |
| `IPRO Analyse: Memory Map` | Analyze memory usage |
| `IPRO Analyse: Decode Crash Report` | Decode exceptions and backtraces |
| `IPRO Debug: Pin Function Lookup` | Look up pin functions |
| `IPRO Debug: Register Explorer` | Inspect registers over CCI |

## FAQ { #faq }

| Symptom | What to do |
|---|---|
| IPRO commands are missing | Check the Extension version, the VS Code profile, Workspace Trust and the SDK root, then reload the window |
| Diagnostics still shows the old SDK | Workspace and folder settings can override user settings; run `IPRO Setup: Set SDK Root` again on the V2.2.0 directory |
| Build fails to compile or link | Check that the compiler is a toolchain that matches V2.2.0 (GCC 14) |
| Garbled console or the old baud rate | Check the firmware's console rate and `ipro.monitorBaudRate`, then close and reopen the monitor |
| `flash jedec id: 00000000` while flashing the Reef | Set the chip variant to `IPRO7AI` |
| No `[All Success]` from the flash tool | The board is not in download mode, or another program holds the port |
| The probe is detected but CCI does not respond | USB enumeration does not mean the board-side CCI link works; check the wiring and board settings |

## Versions { #version }

The SDK, the Extension and Online Setup are separate packages with their own version numbers. The current Extension is 3.3.0, installed by Online Setup 3.4.0; an installer version does not imply the same Extension version. The Extensions view shows the version installed.

## Related documents { #related }

- [Windows Setup & VS Code](../get-started/windows.md): install the tools and the Extension, add SDK V2.2.0.
- [Flashing & Serial Console](../get-started/flash-and-monitor.md): the IntelProCube command line, partition tables, boot2 and `mfg`.
- [Build System & Configuration](build-system.md): `.config`, alternate configurations and the Reef build list.
- [Create Your First Application](../tutorials/first-own-app.md): your own Reef application.
