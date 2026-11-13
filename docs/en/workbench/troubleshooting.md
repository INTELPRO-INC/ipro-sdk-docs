---
title: "Troubleshooting"
description: What the messages, toolbar and side bar status of IPRO Workbench mean and what to do, macOS and Windows issues, and what to attach when you report a problem.
---

# Troubleshooting

Causes and fixes for the messages and states you see in IPRO Workbench 0.2.1, by where they appear.

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
| IntelProCube has no …, the partition table … flashes with. Without one the board would not boot. | This IntelProCube version lacks the partition table the board needs (the IPRO6S EVK needs `partition_cfg_fw_direct.toml` of 0.7.0.1 or later) | Press **Install IntelProCube**, or select a version 0.7.0.1 or later on the IntelProCube row of **Environment**, then flash again |
| `mfg uses the same space as FW …` (a check result in the **Partition Table** and **AI Model** views) | The 1M partition table has no separate space for the AI model | In **Partition Table**, select a table with a separate mfg partition (for example the one that ships with the application) |
| The board did not answer. Is it running the MFG firmware? | During an RF test, the board is not running the MFG firmware, or the monitor is not open | Flash the MFG firmware, open the monitor, then press **Check Firmware** |
| No results in the **Testing** view | The board did not restart, or the application does not use the Unity test framework | Make sure the monitor is on the probe's UART port, then press **Run Tests on Board** |
| The board did not answer wifi_state. Flash an application with the Wi-Fi shell and iperf… | Wi-Fi throughput: the application on the board has no Wi-Fi shell, or the monitor is on another port | On the IPRO6S EVK flash `platform/ipro6_demo`; under **Board** on the tool page choose this board's port |
| The network name must be 1 to 32 characters without spaces… / The password must be 8 to 63 characters without spaces. | The board's shell cannot take a space | Use a network name and password without spaces (set up another network on the access point if necessary) |
| The board did not join …. Check the name and password. | A typing mistake in the name or password, or the network is not on 2.4 GHz | Correct it and press **Join Network** again |
| This PC has no address on the board's network (…). | The computer and the board are not on the same Wi-Fi network | Put the computer on the same network (in access point mode, the network the board created), then press **Run Test** |
| The board did not connect to this PC on TCP port 5001. A firewall on this PC may block incoming connections… | With the board sending and the computer receiving, the computer's firewall blocks the incoming connection (the Windows default) | Let the firewall allow incoming TCP 5001 (see [Running the Test](measure.md#iperf-run)), or send from the computer to the board instead |
| This PC could not reach the board's iperf server… / An earlier iperf is still running on the board… | The board's iperf server is still waiting for a connection | Press **Reset Board**; after the board restarts, join the network again |
| The board did not restart. Is the monitor on the console port of an IPRO Debug Probe? | The monitor is open on CCI or another port | Click the board on the toolbar and use **Select Port…** to switch back to the probe's UART |
| … is not connected. Check the cable to the board, or pick another port. | The selected port is gone (the board was unplugged, or its USB port got another name) | Check the cable, then click the board on the toolbar and choose the port again with **Select Port…** |
| The setting ipro.board.port keeps the port at …. Clear the setting to use …? | The `ipro.board.port` setting names a port other than the one you want | Press **Use …** to clear the setting, or cancel to keep it |
| The board on … answered, but its flash did not: it was flashed as …, and the flash pins of that board are not this one's. | The board selected on the toolbar is not the one connected, so the wrong flash pins were used | Press **Select Board**, choose the connected board, then **Retry** |
| … is laid out for boot2, and this IntelProCube has no boot2 image for …. | The partition table needs boot2, and IntelProCube has none for the chip | Press **Install IntelProCube** to update it, or choose a table that starts the firmware directly in **Partition Table** |
| IntelProCube … is too old for …: a board flashed with it does not start. | The IPRO6S EVK needs IntelProCube 0.7.0.1 or later | Press **Install IntelProCube**, or **Browse…** to a newer one |
| The board did not start boot2's USB downloader. … | While [flashing over the board's own USB](flash.md#usb-flash), the board did not restart into the downloader (for example a firmware without a USB console) | Press **Flash** again, and within 20 s unplug the board's USB cable and plug it in |
| The default partition table comes with IntelProCube, and IntelProCube was not found. / This IntelProCube has no …. | **Partition Table** cannot find the default table | Press **Install IntelProCube**, or choose another table in **Flash with** |
| The partition table's FW partition has one slot. An OTA needs a table with a second FW slot… / This partition table is a layout without boot2… | **OTA Package**: the partition table is not a boot2 A/B layout | In **Partition Table**, choose a table with room for boot2 and a second FW slot (for example `partition_cfg_2M_remote_ab.toml` of `ipro_ble_remote`); see [OTA package](flash.md#ota) |
| boot2 OTA packages are for IPRO7 applications; this one is built for the …. | **OTA Package** does not take IPRO6S applications | None; the IPRO6S has no boot2 OTA package |
| The board did not answer the ota_uart command. Its application needs CONFIG_IPRO_OTA=y and CONFIG_IPRO_OTA_UART=y… | The application on the board has no `ota_uart` command, or the port is not its console | Build and flash it with IPRO SDK V2.3.0 and these two settings on, then send again |
| The board refused the package: the partition table on the board has no second FW slot. … | The board has not been flashed with an A/B table yet | Flash the application with the A/B table and boot2 first (steps 2 and 3 of [OTA package](flash.md#ota)) |
| The board refused the package: its SHA-256 does not match: the file is damaged, or the line dropped data. | Data was lost on the way | Try again with **Check on Board**; if it still fails, make the package again |
| The board did not list any network (no answer to wifi_scan). | Wi-Fi throughput: the board did not answer the scan | Make sure the application on the board has the Wi-Fi shell (for example `ipro6_demo`), then press **Scan** |
| The Wi-Fi stack did not start (no answer to stack_wifi). | The board did not answer `stack_wifi` | Reset the board, then press **Join Network** again |

## Toolbar and side bar status { #status }

| Status you see | What to do |
|---|---|
| The toolbar shows "no probe" in amber | The IDE cannot find the IPRO Debug Probe. Check the USB cable and connect the probe directly to the computer if you can; once it is plugged in, it appears automatically within a few seconds. |
| The status bar shows "Setup: N" | Click it to open IPRO Home, and press **Fix Environment** in the banner. |
| **Board** shows "Runs other firmware" | The board is not running the latest build of the current application. To run the current program, flash it. |
| **Board** has no "Runs …" line for the IPRO6S EVK | Normal with IPRO SDK 2.2.1 or earlier: the IPRO6 firmware of those versions prints no build time at boot, so the IDE cannot check the firmware on the board; rely on `[All Success]` in **IPRO Flash** and the boot messages in the monitor. From IPRO SDK V2.3.0 on the line is shown (see [Differences from the IPRO7 Series](flash.md#ipro6s-differences)). |
| The status bar shows no configuration (a gear and `.config`) | Normal. It is shown only for applications that have other configuration files such as `defconfig_*` or `config_*` (see [Configurations](develop.md#configurations)). |

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
| **SDK for this toolchain** says it needs adjusting | IPRO SDK 2.2.1 and earlier need a few host fixes before they build on Windows. Press **Fix Environment** (or **Prepare the SDK for this toolchain** on that row), and the IDE handles them automatically. |
| Wi-Fi throughput: no result when the board sends and the computer receives | The Windows firewall blocks incoming connections by default. Add an inbound rule that allows TCP port 5001 (see [Running the Test](measure.md#iperf-run)), or send from the computer to the board instead. |
| Linking fails when you build with the RISC-V toolchain 13.1.1 | On Windows, build the IPRO SDK with the RISC-V toolchain 14.2.1; 13.1.1 cannot link the SDK's prebuilt libraries. Press **Fix Environment** to install 14.2.1, or choose it on the toolchain row of **Environment**. |
| Flashing fails after you select the board's own USB port | The Windows version cannot flash over a board's own USB yet. Connect the IPRO Debug Probe and select its UART. |
| The Python row says kconfiglib is missing | Run `python -m pip install kconfiglib windows-curses` in a Command Prompt, then press **Check Again**. |
| The code editor prompts you to download clangd | Code navigation uses clangd. Follow the prompt and let it download, or press Fix on the clangd row of **Environment**. |

## Collect information about a problem { #collect }

When you report a problem to INTELPRO, attach:

1. The IDE version: choose **Help → About**.
2. The output of the step that failed: in the **Output** panel, select **IPRO Build**, **IPRO Flash** or **IPRO Setup**, select all and copy.
3. The board's output: on the IPRO Monitor tab, press **Save Monitor Output…**, or attach the monitor logs in `build/logs`.
4. For a crash, attach the crash dump folder in `build/crash`.
