---
title: "Install IPRO AI Studio"
description: Install IPRO AI Studio 0.4.2 on macOS and Windows, open it the first time, allow the camera, check that Studio finds the Reef, and use the ipro-ai command line inside the same program.
---

# Install IPRO AI Studio

At the end of this page your computer has IPRO AI Studio, which drives the three Teach tools, and the `ipro-ai` command line that comes in the same program. When you connect an IPRO7AI Reef EVK running the Edge AI firmware, Studio finds the board by itself. This page covers IPRO AI Studio 0.4.2; its interface is in English, and buttons and page names are shown in bold as they appear on screen.

## Prerequisites { #prerequisites }

- A computer with macOS 11 or later on Apple silicon (Intel Macs are not supported), or 64-bit Windows (x64).
- The installer, from the [IPRO AI Studio releases on GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest):
    - macOS: `IPRO-AI-Studio-0.4.2.dmg`
    - Windows: `IPRO-AI-Studio-0.4.2-windows-x64.zip`
- To check the connection: an IPRO7AI Reef EVK flashed with the Edge AI firmware and a USB-C data cable. If the board is not flashed yet, install Studio first, then follow [Flash the Edge AI Firmware](firmware.md).

Studio includes the model converter and flash tool it needs; the Teach, Sensor and Audio pages need no separate Python or other programs.

## Install { #install }

<div class="ipro-steps" markdown>

1. **Install the program**

    === "macOS"

        Open `IPRO-AI-Studio-0.4.2.dmg` and drag **IPRO AI Studio** into the Applications folder.

    === "Windows"

        Unzip `IPRO-AI-Studio-0.4.2-windows-x64.zip` where you want the program, for example `C:\IPRO\`. You get an `ipro-ai-studio` folder: `ipro-ai-studio.exe` is the windowed program and `ipro-ai.exe` is the command line. The Visual C++ runtime it needs is in the same folder; nothing else to install.

2. **Open it the first time**

    === "macOS"

        In Finder's Applications folder, right-click **IPRO AI Studio**, choose **Open**, then **Open** again in the dialog. Or remove the download quarantine in Terminal and open it normally:

        ```bash
        xattr -dr com.apple.quarantine "/Applications/IPRO AI Studio.app"
        ```

    === "Windows"

        Double-click `ipro-ai-studio.exe` in the `ipro-ai-studio` folder.

    The rail on the left lists **Convert**, **Inspect**, **Verify**, **Board**, **Teach**, **Sensor** and **Audio**. The first four are model conversion, inspection and comparison tools; the Teach tools use the last three.

3. **Find the three Teach pages**: click the rail, or use the **Go** menu or a shortcut.

    | Page | Tool | Shortcut (macOS / Windows) | Firmware mode |
    |---|---|---|---|
    | **Teach** | Image recognition | Command+5 / Ctrl+5 | `image` |
    | **Sensor** | Sensor recognition | Command+6 / Ctrl+6 | `sensor` |
    | **Audio** | Voiceprint recognition | Command+7 / Ctrl+7 | `voice` |

4. **Allow the camera**: the first time you open the **Teach** page, macOS asks whether IPRO AI Studio may use the camera; choose **Allow**. The Teach page cuts its training pictures out of the Reef's USB camera stream, so without the permission the camera view stays empty.

</div>

## Operating-system permissions { #permissions }

| Item | macOS | Windows |
|---|---|---|
| Camera (Teach page) | Allow it the first time you open Teach. If you refused, the Teach page shows `IPRO AI Studio is not allowed to use the camera.`; turn IPRO AI Studio on in **System Settings → Privacy & Security → Camera**, then reopen Studio | In **Settings → Privacy & security → Camera**, make sure desktop apps may access the camera |
| Serial port (all three pages) | No permission needed | No permission needed |

Only one program at a time can open the board's USB serial port. While you use Studio, close anything else that has it open, such as a terminal program or a second Studio window. This is not the console port on the IPRO Debug Probe; the two can be open at the same time.

## How Studio finds the board { #board-discovery }

The Teach, Sensor and Audio pages look for the board themselves; you do not pick a serial port. Depending on its mode, the Edge AI firmware enumerates as a different USB device under INTELPRO's USB VID 0x3896, and each page looks only for its own:

| Firmware mode | USB device name | VID:PID | Page that looks for it |
|---|---|---|---|
| `image` | IPRO7 UVC Cam (USB camera + serial) | 3896:0705 | **Teach** |
| `voice` | IPRO Reef Voice (serial) | 3896:0720 | **Audio** |
| `sensor` | IPRO Reef Sensor (serial) | 3896:0721 | **Sensor** |

- When the page finds the board, **Board** in the status row at the top shows `on USB` (Teach page) or `ready` (Sensor and Audio pages).
- When the board is in another mode, a banner at the top says so, for example `The Reef is in voiceprint mode.`, with a **Switch to Teach**, **Switch to Sensor** or **Switch to Audio** button. Press it: the board restarts into this page's mode (about 2 s) with all three models kept, and the page finds it again within a few seconds.
- If the board's firmware has only one tool, pressing the button shows `This Reef's firmware runs one Teach only.`; flash the Edge AI firmware, `ipro_reef_teach`.
- With several Reefs attached, a page finds one of them. When in doubt, connect one at a time; the command line takes `--port`.

## The ipro-ai command line { #cli }

The `ipro-ai` command line is inside Studio's executable and uses the same deploy and verify logic as Studio, for scripts and automation.

=== "macOS"

    ```bash
    alias ipro-ai='"/Applications/IPRO AI Studio.app/Contents/MacOS/ipro-ai-studio" --cli'
    ipro-ai device list
    ```

    Add the `alias` line to your shell's startup file (for example `~/.zshrc`) to have `ipro-ai` in every terminal.

=== "Windows"

    ```powershell
    cd C:\IPRO\ipro-ai-studio
    .\ipro-ai.exe device list
    ```

Common device commands:

| Command | What it does |
|---|---|
| `ipro-ai device list` | Lists the Teach tools on USB: tool, serial port, VID:PID, serial number |
| `ipro-ai device info --json` | Firmware name and version, platform version, available modes, the current tool's slot size and model |
| `ipro-ai model list --all` | Switches through the three modes, lists each mode's model, then switches back |
| `ipro-ai deploy <package.ipkg> --switch` | Switches to the package's mode, deploys, and reads back the model's CRC to confirm |

Every device command takes `--port` to name the Reef's USB serial port (without it, the only board on USB is used) and `--json` for machine-readable output. Human-readable messages are in Chinese; use `--json` for English keys. The full command set and the `.ipkg` model package format are in the IPRO7AI Reef Development Kit User Guide, available from INTELPRO; see [Documents](../documents/index.md).

## Verify { #verify }

1. Studio opens with **Teach**, **Sensor** and **Audio** in the rail.
2. With a Reef running the Edge AI firmware attached, `ipro-ai device list` lists one board, for example (`voice` mode, macOS):

    ```text
      voice   /dev/cu.usbmodemXXXX  USB 3896:0720  <serial number>
    ```

3. `ipro-ai device info --json` shows the Edge AI firmware and platform version under `version`:

    ```text
    "version": {"platform": "2.0", "proto": 2, "abi": 1, "store": 1,
                "tool": "voice", "fw": "ipro_reef_teach", "ver": "2.0.0", "chip": "IPRO7AI"},
    ```

4. Open the page that matches the board's mode: **Board** in the status row shows `on USB` or `ready`.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| macOS says IPRO AI Studio cannot be opened | The downloaded app is quarantined | Right-click it in Finder and choose **Open**, or run the `xattr` command above |
| The Teach page shows `IPRO AI Studio is not allowed to use the camera.` | The camera permission was refused | Allow IPRO AI Studio in the system's camera privacy settings, then reopen Studio |
| `ipro-ai device list` finds no IPRO device (exit code 3) | The board is not running, the USB-C cable is charge-only, or the board does not run the Edge AI firmware | Use a data cable; check the console boot log; flash as in [Flash the Edge AI Firmware](firmware.md) |
| A page keeps showing `Looking for the board…` | The board is in another mode, or another program holds its serial port | Wait for the **Switch to …** banner; close other programs using that port |

For anything else, see [Troubleshooting](troubleshooting.md).

## Next steps { #next-steps }

- [Flash the Edge AI Firmware](firmware.md), if the board does not have it yet.
- [Image Recognition](image.md), [Voiceprint Recognition](voice.md), [Sensor Recognition](sensor.md): each tool step by step.
