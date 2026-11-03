---
title: "First FreeRTOS Application"
description: Set the switches and wire the console of the IPRO7AI Reef EVK, then build, flash and run the out-of-box firmware ipro7ai_reef_demo and check the board with reef selftest.
migrate_from:
  - "getting-started.html#freertos-quickstart"
  - "getting-started.html#first-build"
---

# First FreeRTOS Application

Build the out-of-box firmware `ipro7ai_reef_demo`, flash it to an IPRO7AI Reef EVK V4.0, open the console and run `reef selftest` to check the LED, speaker, SD slot and camera. At the end the console shows the `ipro />` prompt and every block on the board answers a shell command.

## Prerequisites { #prerequisites }

- [Set Up Your Host](environment.md) is done: `./build_freertos.sh ipro7ai_reef_demo` builds and IntelProCube's `--help` runs. On Windows, see also [Windows Setup & VS Code](windows.md).
- An IPRO7AI Reef EVK V4.0, a USB-C cable and a console cable (3.3 V USB-to-UART adapter or IPRO Debug Probe).
- Optional: an OV5640 FLEX-24 camera module, a microSD card and an 8 Ω speaker on J_SPK. Without them the matching self-test lines report nothing found.
- Command-line examples use macOS. On Linux, use `/dev/ttyUSB0` and `ipro_iot_tool_linux`; on Windows, follow the Windows tab of each step.

## Set the switches and wire the board { #connect }

<div class="ipro-steps" markdown>

1. **Set the switches:** SW7 to **CAM**, SW8 to **PWR**. With SW7 on GPIO the camera has no power; with SW8 on MEAS the IPRO7AI is supplied through JP2. See [Switches and jumpers](../hardware/boards/reef-evk.md#jumpers).

2. **Connect the console cable to U6** (board still unpowered):

    | U6 pin | Signal | USB-to-UART adapter |
    |---|---|---|
    | 1 | NC | — |
    | 2 | GND | GND |
    | 3 | TX (GPIO20, Reef output) | RX |
    | 4 | RX (GPIO21, Reef input) | TX |
    | 5 | BOOT (1 kΩ to GPIO41) | optional: DTR |
    | 6 | RESET (1 kΩ, active low) | optional: RTS |

    The IPRO Debug Probe connects from its CN_UART through a pin-reversed cable: probe pin n to U6 pin 7 − n.

    !!! warning "Cable direction"
        Do not connect the Debug Probe with a straight cable: the UART and control lines end up on the wrong pins and the probe's 3.3 V lands on U6 RESET.

3. **Power up:** plug in USB-C. The green power LED, LED2, lights. U6 does not power the board; only USB-C does.

4. **Check the serial port:** plug the adapter or probe into the computer and confirm the port appears, for example `/dev/cu.usbserial-XXXX` on macOS, `/dev/ttyUSB0` on Linux or `COM5` on Windows. With the Debug Probe, use the port whose name ends in `02`; see [Recognise the ports](flash-and-monitor.md#ports).

</div>

## Build { #first-build }

<div class="ipro-steps" markdown>

1. **Build the out-of-box firmware** from the SDK root. On Windows, use `IPRO: Build` in the VS Code Extension (see [Set up the VS Code Extension](windows.md#installation)) or `build_freertos.ps1` in PowerShell (see [Command-line build](windows.md#command-line)) instead.

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    The configure stage reports the Reef board settings; the end of the build shows memory usage and the image path (excerpt):

    ```text
    -- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
    -- IPRO7 flash: 1M (default, on-chip)
    -- AI disabled: OCRAM=256KB
    ...
    Memory region         Used Size  Region Size  %age Used
               flash:      249944 B         1 MB     23.84%
               psram:       45376 B         8 MB      0.54%
               ocram:       32144 B       256 KB     12.26%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    [100%] Built target ipro7ai_reef_demo_IPRO7.elf
    ```

    The numbers vary slightly with the toolchain version.

2. **Check the output:**

    ```bash
    ls apps/platform/ipro7ai_reef_demo/build/build_out/
    ```

    ```text
    ipro7ai_reef_demo_IPRO7.bin    image to flash
    ipro7ai_reef_demo_IPRO7.elf    with debug symbols
    ipro7ai_reef_demo_IPRO7.map    memory map
    lib/
    ```

</div>

## Flash and run { #flash-and-run }

<div class="ipro-steps" markdown>

1. **Free the serial port:** close every terminal program that has the port open. Flashing and the console share the same UART.

2. **Enter download mode:** hold **SW1 (BOOT)**, press and release **SW2 (RESET)**, then release SW1. The console stays silent in download mode.

    If the board already runs SDK firmware (such as the factory out-of-box firmware), typing `reboot_dl` at its console does the same: it prints `reboot to download mode` and goes silent. With a DTR/RTS auto-download cable or the Debug Probe, see [Enter download mode](flash-and-monitor.md#download-mode).

3. **Flash** from the IntelProCube directory. `--chip-variant IPRO7AI` selects the Reef's flash pins; `--pt` names a partition table that ships with IntelProCube.

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    The tool prints its progress line by line (excerpt, timestamps left out):

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

    Only a final `[All Success]` means success. The tool exits 0 even when flashing fails, so its exit code tells you nothing.

4. **Open the console** at 115200 baud, 8N1, no flow control, on the same port:

    === "macOS"

        ```bash
        screen /dev/cu.usbserial-XXXX 115200
        ```

        To quit `screen`: press ++ctrl+a++, then ++k++, and answer `y`.

    === "Linux"

        ```bash
        picocom -b 115200 /dev/ttyUSB0
        ```

        To quit `picocom`: press ++ctrl+a++, then ++ctrl+x++. Install it with `sudo apt install picocom` if needed.

    === "Windows"

        In PuTTY choose **Serial**, set Serial line to `COM5` and Speed to `115200`, and click **Open**. The VS Code Extension's `IPRO: Serial Monitor` also works.

5. **Reset:** press **SW2 (RESET)**. The RGB LED breathes blue once and goes dark, and the console shows the boot messages (excerpt; `(…)` is a timestamp):

    ```text
    I (…) REEF: ==========================================
    I (…) REEF:   IPRO7AI Reef carrier demo
    I (…) REEF:   UART0 TX=20 RX=21  RGB=G24  SPK_EN=G25(hi)
    I (…) REEF:   CAM: FLEX-24 D0-7=G0-7 XCLK=G22 RST=G34 PWDN=G35
    ...
    I (…) REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    ```

    Press ++enter++ to get the `ipro />` prompt.

</div>

## Verify { #verify }

<div class="ipro-steps" markdown>

1. **Keys:** press SW3, SW4, SW5 and SW1 (BOOT) in turn; the RGB LED lights red, green, blue and white.

2. **Self-test:** type `reef selftest` at the console. Within about 3 seconds the LED steps through red, green and blue, the speaker plays a short 1 kHz tone, and the console shows (with an OV5640 fitted and no SD card):

    ```text
    ipro />reef selftest
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: __rti_name_ov5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    | Line | Checks | Other results |
    |---|---|---|
    | `[3/4] SD slot` | whether a card is seated, slot supply | `something seated` with a card in |
    | `[4/4] camera bus` | the camera sensor found over SCCB and its address | `no sensor` without a camera; `__rti_name_ov2640 at 0x30` for an OV2640 |

3. **List the commands:** type `help`. It lists every shell command, including `reboot` and `reboot_dl`.

</div>

### Commands of the out-of-box firmware { #commands }

| Command | Does |
|---|---|
| `reef status`, `reef selftest` | board state (pins, keys, LED, amplifier, detect lines); self-test |
| `led <r> <g> <b>`, `led rainbow`, `led off` | RGB LED colour (0–255, for example `led 40 0 0`), rainbow effect, off |
| `btn status`, `btn watch` | key state and press counts; live press and release events |
| `spk tone <hz> <ms>`, `hp` | sine tone on the speaker; headset-detect level |
| `mic rec pdm <s>`, `mic rec headset <s>`, `mic play`, `mic loop` | record from the on-board PDM microphone or a headset into PSRAM (up to 10 s) and play back, or monitor live |
| `mic sdrec <src> <name> <s>`, `mic usb <src>` | record to `sd:/rec/<name>.wav`; make the board a USB microphone on its USB-C until `mic stop` |
| `sd mount`, `sd ls`, `sd test` | microSD card (FatFS at `sd:`) |
| `cam probe`, `cam start`, `cam status`, `cam snap`, `cam bar on`, `cam bar off` | OV5640 camera (SW7 on CAM) |
| `reboot`, `reboot_dl` | restart; restart into download mode |

Details of each block and the camera bring-up order: [IPRO7AI Reef EVK: Out-of-box firmware](../hardware/boards/reef-evk.md#reef-demo).

## One command: build_freertos.sh { #one-command }

On macOS and Linux, `build_freertos.sh` chains build, flash and monitor. It reads the application's configuration to pass `--chip-variant IPRO7AI` and to open the console at the application's own baud rate. When the board already runs SDK firmware with a shell, it sends `reboot_dl` to enter download mode; the first time, enter download mode by hand as above.

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

On success it prints `✓ Build succeeded`, the tool's flash output and `✓ Flash succeeded`, then shows the boot messages for 30 seconds. `monitor` only reads; you cannot type commands into it. It ends with `[serial_monitor] TIMEOUT after 30s`, which the script counts as a failure — that is expected. All options: [macOS / Linux Command Line](command-line.md#build-script).

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| The green power LED2 stays dark | USB-C not seated, or no power from the source | change the USB-C cable or supply; USB-C is the only power input |
| No `[All Success]`; the tool stops at the handshake | the board is not in download mode, or a terminal program holds the port | close the terminal; hold SW1, press SW2, release SW1, flash again |
| `flash jedec id: 00000000` and `IPRO FLASH MATCH TYPE FAIL` | wrong flash pins | add `--chip-variant IPRO7AI` to the command |
| The tool cannot find a partition table under `chips/...` | not run from the IntelProCube directory | `cd <IntelProCube>` first |
| Flashing succeeded but the console stays silent | board still in download mode, wrong baud rate or port, RX/TX swapped | press SW2; open at 115200; use `/dev/cu.*` on macOS; swap the adapter's RX and TX |
| Garbage on the console | baud rate is not 115200 | reopen at 115200, 8N1 |
| Output appears but typed commands get no answer | the adapter's TX does not reach U6 pin 4 | check the wire to U6 pin 4 (RX) |
| `[4/4] camera bus: no sensor` | no camera, cable not seated, or SW7 not on CAM | unplug USB-C and reseat the camera cable; set SW7 to CAM |
| No sound from the speaker | no speaker, or its plug is loose | connect an 8 Ω speaker to J_SPK |
| `[3/4] SD slot: empty` with a card inserted | card not pushed in | push the card until it latches |
| The build cannot find the compiler | toolchain not at the default path | set `CROSS_COMPILE`; see [Set Up Your Host](environment.md#toolchain) |

More flashing and console problems: [Flashing & Serial Console](flash-and-monitor.md#troubleshooting).

## Next steps { #next-steps }

- [Build and Flash Workflow](../tutorials/build-and-flash.md): rebuild, reflash and monitor after a change.
- [Create Your First Application](../tutorials/first-own-app.md) and [Test Your Application](../tutorials/testing.md).
- [Flashing & Serial Console](flash-and-monitor.md): other download-mode methods, partition tables, boot2 and `mfg` data.
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md): all switches, pins and the camera bring-up order.
