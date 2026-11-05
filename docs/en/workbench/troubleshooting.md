---
title: "Troubleshooting"
description: What the messages, toolbar and side bar status of IPRO Workbench mean and what to do, macOS and Windows issues, and what to attach when you report a problem.
---

# Troubleshooting

Causes and fixes for the messages and states you see in IPRO Workbench 0.1.0, by where they appear.

## Messages on screen { #messages }

Whenever a step fails, the IDE pops up an explanation with buttons to deal with it. The table lists the cause and what to do for each message.

| Message on screen | Cause | What to do |
|---|---|---|
| The board did not answer on … | The probe cable is not connected properly, the board has no power, or the wrong port is selected | Check the cable and the power, then press **Select Port** or **Retry** |
| Another program has … open, so IntelProCube cannot use it | Another serial monitor or terminal has the same port open | Close that program, then press **Retry** |
| … has not been built yet. | There is no firmware to flash yet | Press **Build and Flash** |
| Flashing needs IntelProCube, and it was not found. | IntelProCube is not installed | Press **Install IntelProCube**, or **Browse…** to point to an existing one |
| … did not compile. First error at … | The code has an error | Press **Go to Error**; the **Problems** view lists all errors. You can also press **Ask AI to Fix** |
| CMake could not configure … | `.config` or `CMakeLists.txt` is wrong | Read the **IPRO Build** output, fix the problem, then press **Reconfigure and Build** |
| The toolchain or the build tools are missing. | The development environment is not complete yet | Press **Fix Environment** |
| pins.yaml of … has errors, so app_pins.c was not generated. | The pin settings conflict, or a signal is not available on that pin | Press **Open Pin Configuration**, fix the items under **Problems** one by one, then press **Save and Generate** |
| The board started firmware built …, not the … just flashed. | The flash did not actually reach the board | Read the **IPRO Flash** output and press **Flash Again** |
| … is over its memory budget | A memory region exceeds the limit set in `ipro.build.memoryBudget` | Press **Memory Map** to find the large symbols, or **Budget Settings** to adjust the limit |
| The partition table of … reaches …, but the board on this probe has … of flash | The selected partition table is larger than the board's flash | Press **Partition Table** to choose another one, or check the flash size in `.config` |
| `mfg uses the same space as FW …` (a check result in the **Partition Table** and **AI Model** views) | The 1M partition table has no separate space for the AI model | In **Partition Table**, select a table with a separate mfg partition (for example the one that ships with the application) |
| The board did not answer. Is it running the MFG firmware? | During an RF test, the board is not running the MFG firmware, or the monitor is not open | Flash the MFG firmware, open the monitor, then press **Check Firmware** |
| No results in the **Testing** view | The monitor filter hides the test lines, or the board did not restart | Clear the filter, then press **Run Tests on Board** |
| The board did not restart. Is the monitor on the console port of an IPRO Debug Probe? | The monitor is open on CCI or another port | Click the board on the toolbar and use **Select Port…** to switch back to the probe's UART |

## Toolbar and side bar status { #status }

| Status you see | What to do |
|---|---|
| The toolbar shows "no probe" in amber | The IDE cannot find the IPRO Debug Probe. Check the USB cable and connect the probe directly to the computer if you can; once it is plugged in, it appears automatically within a few seconds. |
| The status bar shows "Setup: N" | Click it to open IPRO Home, and press **Fix Environment** in the banner. |
| **Board** shows "Runs other firmware" | The board is not running the latest build of the current application. To run the current program, flash it. |

## macOS issues { #macos }

| Situation | What to do |
|---|---|
| The first launch says the developer cannot be verified | Go to System Settings → Privacy & Security and click **Open Anyway** (see [Install IPRO Workbench](install.md#install)). |
| **Environment** shows **macOS quarantine** | The tools were downloaded with a browser or a chat app, so macOS stops them when they run. Click the lock icon on that row and confirm to remove the flag. |
| CMake or the build program is reported missing | On macOS the IDE does not install the build tools. Run `xcode-select --install` and `brew install cmake ninja` in a terminal, then press **Check Again**. |
| Flashing fails midway with `Device not configured` | The probe dropped off USB (cable, hub or power supply). Change the cable or connect the probe directly to the computer, then press **Retry**. |

## Windows issues { #windows }

| Situation | What to do |
|---|---|
| Installation shows "Windows protected your PC" | Click **More info**, check that the app name is IPRO-Workbench, then click **Run anyway**. |
| A COM port cannot be opened from another serial tool | On Windows, a COM port can be used by only one program at a time. Close IPRO Monitor before you open the other tool, and close that tool when you are done so the IDE can flash. |
| **SDK for this toolchain** says it needs adjusting | SDK 2.2.0 needs a few host fixes before it builds on Windows. Press **Fix Environment** (or **Prepare the SDK for this toolchain** on that row), and the IDE handles them automatically. |
| The Python row says kconfiglib is missing | Run `python -m pip install kconfiglib windows-curses` in a Command Prompt, then press **Check Again**. |
| The code editor prompts you to download clangd | Code navigation uses clangd. Follow the prompt and let it download. |

## Collect information about a problem { #collect }

When you report a problem to INTELPRO, attach:

1. The IDE version: choose **Help → About**.
2. The output of the step that failed: in the **Output** panel, select **IPRO Build**, **IPRO Flash** or **IPRO Setup**, select all and copy.
3. The board's output: on the IPRO Monitor tab, press **Save Monitor Output…**, or attach the monitor logs in `build/logs`.
4. For a crash, attach the crash dump folder in `build/crash`.
