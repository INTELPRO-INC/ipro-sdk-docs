---
title: "Windows Setup & VS Code"
description: Install SDK V2.2.0, the RISC-V toolchain, the build tools, IntelProCube and the VS Code Extension on Windows in one go with IPRO SDK Online Setup 3.6.0, build the IPRO7AI Reef EVK out-of-box firmware in VS Code or PowerShell, flash it and open the console.
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

On Windows, IPRO SDK Online Setup installs SDK V2.2.0, the RISC-V toolchain, the build tools (CMake, Ninja, Python), IntelProCube, OpenOCD and the VS Code Extension in one go. You then build the IPRO7AI Reef EVK out-of-box firmware `ipro7ai_reef_demo`, flash it, and see its console on a COM port. Build and flash in VS Code, or in PowerShell with `build_freertos.ps1`.

!!! info "Toolchain version"
    The Windows toolchain Online Setup installs is GCC 13.1.1, and the SDK is prepared for it (recorded in `PREBUILT-ARCHIVES-STRIPPED.json` in the SDK root). SDK V2.2.0 builds with GCC 14 on macOS and Linux, so the images differ from those builds.

## Requirements { #requirements }

- Windows x64 with access to GitHub (Online Setup downloads its components from a public catalog and GitHub releases).
- VS Code 1.102 or later (the installer can download it).
- An IPRO7AI Reef EVK, a USB-C cable, and an IPRO Debug Probe or a USB-to-UART adapter on U6; see [What you need](index.md#what-you-need).

## Install { #online-setup }

<div class="ipro-steps" markdown>

1. **Download the installer** `IPRO-SDK-Online-Setup-3.6.0.exe` from the [latest IPRO SDK Online Setup release](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest) (3.6.0); no GitHub sign-in is needed.

2. **Verify** it in PowerShell:

    ```powershell
    Get-FileHash .\IPRO-SDK-Online-Setup-3.6.0.exe -Algorithm SHA256
    ```

    The `Hash` column must equal the value for the same file in that release's `SHA256SUMS.txt` (case does not matter). The installer is not code-signed, so Windows may show a SmartScreen warning; follow your company's security rules.

3. **Choose Full environment** under **Choose packages**.

4. **Check the versions:** keep every component on latest under **Select package versions**; the list shows what latest resolves to, for example `latest (2.2.0)`.

5. **Choose a directory:** under **Select Destination Location**, keep the default new folder `C:\IPRO\versions\3.6.0-<date-time>` or enter a folder that does not exist yet (the installation root, `<install dir>` on this page).

6. **Choose the extra tasks:** tick **Install VS Code from Microsoft if absent** if VS Code is not installed; keep **Install the selected Extension into VS Code** ticked; tick **Switch only selected component settings** to point VS Code at this environment; tick **Add installed tools to user PATH** to run the tools from any terminal.

7. **Install:** on **Ready to Install**, check the directory, mode and versions, then click **Install**.

8. **Read the finished page:** it lists the SDK folder (`<install dir>\sdk\IPRO-SDK-V2.2.0`), the first command-line command and the toolchain folder. Reopen VS Code and your terminals so they pick up the new settings and `PATH`.

</div>

Setup also fixes the SDK's Windows build issues (recognising the IPRO toolchain, the build message that breaks Ninja under CMake 4, the serial console) and adds `build_freertos.ps1`; the files it changed are listed in `WINDOWS-HOST-FIXES.json` in the SDK root.

## Set up the VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **Check the Extension is installed:** search the Extensions panel for `@installed IPRO`; you should see IPRO SDK Extension (identifier `ipro.ipro-sdk-extension`).

2. **Open the SDK:** use **File → Open Folder…** on `<install dir>\sdk\IPRO-SDK-V2.2.0`, and allow Workspace Trust after checking the source.

3. **Set the SDK root:** if you did not tick the settings task during installation, press ++f1++ and run `IPRO Setup: Set SDK Root` on the same folder.

4. **Check the environment:** run `IPRO Setup: Run Diagnostics` and check that the SDK root, compiler, CMake, Python and flash tool all point under `<install dir>`.

5. **Build the out-of-box firmware:** run `IPRO: Go to Project…`, pick `ipro7ai_reef_demo` in the platform category, then run `IPRO: Build`.

</div>

The Extension's other commands and settings are in [VS Code Extension](../guides/vscode.md).

## Command-line build { #command-line }

`build_freertos.ps1` is the Windows counterpart of `build_freertos.sh`, with the same actions and options: `build`, `clean`, `flash`, `monitor`, `size` and `test` combine and run in order. It uses the toolchain, CMake, Ninja, Python and IntelProCube of the same installation, whether or not they are on `PATH`. Windows does not run `.ps1` files directly by default; `powershell -ExecutionPolicy Bypass -File` applies to that one run and does not change system settings.

<div class="ipro-steps" markdown>

1. **Go to the SDK folder**

    ```powershell
    cd <install dir>\sdk\IPRO-SDK-V2.2.0
    ```

2. **Build**

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 build ipro7ai_reef_demo
    ```

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    -> Building ipro7ai_reef_demo...
    [OK] Build succeeded (21s)
      Binary: ...\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin (219 KB)
      Toolchain: <install dir>/toolchain/riscv_ipro7_win32/bin/riscv64-unknown-elf-gcc
      Log: ...\apps\platform\ipro7ai_reef_demo\build\build.log
    ```

    On failure it prints the last 30 lines of the build log and where the full log is.

3. **Check the IPRO toolchain was recognised**

    ```powershell
    Select-String -Path apps\platform\ipro7ai_reef_demo\build\build.log -Pattern "\[toolchain\]"
    ```

    ```text
    -- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
    ```

</div>

More: `-l` lists every application, `-h` shows every option, `-d defconfig_<name>` builds an alternate configuration, and `-c <prefix>` selects another toolchain (the prefix ends in `riscv64-unknown-elf-`).

## Flash { #flash }

### With the IPRO Debug Probe { #flash-probe }

<div class="ipro-steps" markdown>

1. **Wire up:** SW7 to CAM, SW8 to PWR, the IPRO Debug Probe on U6, then the Reef's USB-C; see [Set the switches and wire the board](first-app-freertos.md#connect). The probe shows up on Windows as two COM ports; see [Recognise the ports](flash-and-monitor.md#ports).

2. **Flash and watch the boot banner:** in the SDK folder, run:

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 flash monitor ipro7ai_reef_demo -w "IPRO7AI Reef carrier demo"
    ```

    The script picks the probe's console port; IntelProCube puts the board in download mode, flashes it and resets it, and the monitor stops when the banner appears:

    ```text
    [All Success]
    [OK] Flash succeeded (6s)
    ...
    [serial_monitor] MATCHED: IPRO7AI Reef carrier demo

    Summary:
      [OK] flash
      [OK] monitor
    ```

    IPRO7AI board applications get `--chip-variant IPRO7AI` and the `partition_cfg_2M.toml` partition table automatically. With several serial ports connected, name the console port with `-p COM5`.

</div>

In VS Code: pick the probe's console port with `IPRO: Select Serial Port`, set the chip variant to `IPRO7AI` and the partition table to `partition_cfg_2M.toml` in `IPRO Config: Configure Flash…`, then run `IPRO: Flash`.

### With a USB-to-UART adapter { #flash-uart }

<div class="ipro-steps" markdown>

1. **Wire up:** SW7 to CAM, SW8 to PWR, the console cable on U6, then the USB-C; see [Set the switches and wire the board](first-app-freertos.md#connect).

2. **Find the COM port:** open Device Manager → Ports (COM & LPT); the port that appears when you plug the adapter in is the console, for example `COM5`.

3. **Enter download mode:** hold SW1 (BOOT), press SW2 (RESET) once, then release SW1.

4. **Flash:** in PowerShell, go to `<install dir>\IntelProCube` and run:

    ```powershell
    cd <install dir>\IntelProCube
    .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
        --port COM5 --baudrate 921600 `
        --pt chips/ipro7/partition/partition_cfg_2M.toml `
        --firmware <install dir>\sdk\IPRO-SDK-V2.2.0\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

    Only a last line of `[All Success]` means success; the tool exits with 0 even when it fails. The parameters are explained in [Flashing & Serial Console](flash-and-monitor.md#flash-tool). Press SW2 to reset when it is done.

</div>

## Console { #console }

<div class="ipro-steps" markdown>

1. **Open the console:** in the SDK folder run `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 monitor ipro7ai_reef_demo -t 30`, or in PuTTY choose **Serial**, set Serial line to the console's COM port and Speed to `115200`, and click **Open**. Tera Term works too, as does the VS Code Extension's `IPRO: Serial Monitor`.

2. **Reset:** `build_freertos.ps1 monitor` sends `reboot`; with another terminal program press SW2 (RESET). The window shows the boot banner `IPRO7AI Reef carrier demo`; press ++enter++ to get `ipro />`.

3. **Self-test:** type `reef selftest`. The expected output is in [First FreeRTOS Application](first-app-freertos.md#verify).

</div>

Close the terminal program before flashing; otherwise the flash tool cannot open the COM port.

## Install an SDK or a toolchain on its own { #components }

When you choose **SDK only** or **Toolchain only** under **Choose packages**, **Choose where to install** follows the versions page:

- **Add to this existing environment:** the list shows the environments you installed with Online Setup, with their SDKs and toolchains, and preselects the newest one that has a toolchain. The SDK goes into that environment's `sdk\` and builds with the tools already there; a version that is already there is refused. Nothing already installed is overwritten.
- **A new directory:** installs into a new folder. The SDK is prepared for the toolchain given with `/TOOLCHAINROOT=`, the one configured in VS Code, or the one of the newest other environment, and `build_freertos.ps1` uses that toolchain.

Silent installs add to an environment with `/MODE=sdk /ENV=<environment folder>`. The other command-line parameters are in the [Online Setup installation notes](https://github.com/INTELPRO-INC/ipro-sdk-releases/blob/main/INSTALLATION.zh-TW.md) (Traditional Chinese).

## Check the result { #verify }

- The build produces:

    ```text
    apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

- The build log contains `Vendor toolchain detected`.
- The flash output ends with `[All Success]`.
- After a reset the console shows the boot banner and `ipro />`, and `reef selftest` lights the LEDs in turn and plays a short 1 kHz tone.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| Windows shows an unknown publisher or a SmartScreen warning | The installer has no code signature | Follow your company's security rules; do not turn protection off |
| `.\build_freertos.ps1` does not run | Windows does not run `.ps1` files by default | Run `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 ...` |
| The finished page says no toolchain was found | An SDK-only install into a new folder found no toolchain to pair with | Add the SDK to an environment that has a toolchain, or install again with `/TOOLCHAINROOT=<toolchain folder>` |
| Diagnostics still shows the old SDK path | The SDK root in the workspace or user settings points at the old version | Run `IPRO Setup: Set SDK Root`, then Diagnostics again |
| No IPRO commands | The Extension is not in the current VS Code profile, or the workspace is not trusted | Check the Extension, profile and Workspace Trust; run `Developer: Reload Window` |
| No new COM port in Device Manager | A charge-only USB cable, or the adapter's driver is missing | Change the cable; install the adapter vendor's driver; for the Debug Probe, contact INTELPRO |
| Flashing does not end with `[All Success]` | The board is not in download mode, or a terminal program holds the COM port | Close the terminal program; with an adapter, enter download mode again with SW1 + SW2 |
| `flash jedec id: 00000000` | `--chip-variant IPRO7AI` is missing | Add it and flash again |
| Garbled or no console output | Baud rate not 115200, the board still in download mode, or RX/TX swapped | Open at 115200; press SW2; swap RX and TX |

For installation problems keep `<install dir>\online-install.json`, `online-postinstall.log` and the adjacent `<install dir>.download.log`.

## Next steps { #next-steps }

- [First FreeRTOS Application](first-app-freertos.md): the out-of-box firmware's self-test and commands.
- [Flashing & Serial Console](flash-and-monitor.md): other download modes, partition tables, boot2 and the `mfg` data.
- [VS Code Extension](../guides/vscode.md): the Extension's commands and settings.
