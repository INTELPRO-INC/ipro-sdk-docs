---
title: "Flashing & Serial Console"
description: Flashing and console reference for the IPRO7AI Reef EVK — four ways into download mode, IntelProCube options and partition tables, boot2 and mfg data, build_freertos.sh flash, the console and how to recognise serial ports.
migrate_from:
  - "getting-started.html#flashing"
  - "getting-started.html#serial-monitor"
  - "tools-debugging.html#flash-tool"
  - "tools-debugging.html#serial-monitor"
---

# Flashing & Serial Console

FreeRTOS applications are flashed over UART0 with the IntelProCube command-line tool, and the console runs on the same UART; on the IPRO7AI Reef EVK both go through the debug connector U6. This page covers every way to flash the Reef, the partition tables and extra images each application needs, how to open the console and how to recognise the serial ports. For a first run, follow [First FreeRTOS Application](first-app-freertos.md).

## Prerequisites { #prerequisites }

- IntelProCube 0.7.0.1: `ipro_iot_tool_macos`, `ipro_iot_tool_linux` or `ipro_iot_tool.exe`; see [Set Up Your Host](environment.md#intelprocube).
- A built image: `apps/<category>/<app>/build/build_out/<app>_IPRO7.bin`, or `build_<name>/build_out/` when built with `DEFCONFIG=defconfig_<name>`.
- A console cable on U6; see [Set the switches and wire the board](first-app-freertos.md#connect). Ports are written `/dev/cu.usbserial-XXXX` (macOS), `/dev/ttyUSB0` (Linux) and `COM5` (Windows).

## Flash tool { #flash-tool }

Run the command-line tool from the IntelProCube directory: it reads its chip settings from `chips/`, and relative paths such as `--pt chips/...` resolve there. The options used on the Reef:

| Option | Reef value | Meaning |
|---|---|---|
| `--chipname` | `ipro7` | IPRO7 and IPRO7AI |
| `--chip-variant` | `IPRO7AI` | flash-pin setting: `IPRO7AI` is `0x9` (the Reef's QFN56), `IPRO7` is `0x2`. The tool writes it to `<IntelProCube>/chips/ipro7/eflash_loader/eflash_loader_cfg.ini` |
| `--port` | console port | the adapter on U6, or the Debug Probe port ending in `02` |
| `--baudrate` | `921600` | flashing speed, independent of the application's console baud rate |
| `--firmware` | the application's `.bin` | the image from the build |
| `--pt` | partition table | a `.toml` path, or a file name under `chips/ipro7/partition/`; see [Partition tables](#partition-tables) |
| `--boot2` | boot2 image | for applications that use boot2 (`ipro_ble_remote`); see [First flash of ipro_ble_remote](#boot2-ab) |
| `--mfg` | `mfg` partition data | AI models and Teach mode data (`ipro_reef_teach`); see [ipro_reef_teach](#mfg) |
| `--skip-ota` | — | skip OTA file generation; used with `ipro_reef_teach`'s own table |

`--help` lists every option.

!!! warning "Judge by the output"
    The tool exits 0 even when flashing fails. Only a final `[All Success]` line means success.

## Enter download mode { #download-mode }

Before flashing, the IPRO7AI must be in the boot ROM's download mode. The console stays silent from then until the next reset.

| Method | How | When |
|---|---|---|
| Buttons | hold **SW1 (BOOT)**, press and release **SW2 (RESET)**, release SW1 | always; also when the firmware has hung or has no shell |
| `reboot_dl` | type `reboot_dl` at the console; it prints `reboot to download mode` | the board runs SDK firmware with a shell; `build_freertos.sh flash` uses this method |
| Auto-download cable | the adapter's DTR goes to U6 pin 5 (BOOT) and RTS to pin 6 (RESET); on the board each passes 1 kΩ to GPIO41 and the reset pin, so such a cable enters download mode without the buttons | adapters with DTR and RTS |
| IPRO Debug Probe | send control keywords on the probe port ending in `02`, see below | the Debug Probe is wired to U6 |

!!! tip "IntelProCube 0.7.0.1 enters download mode by itself"
    Before it flashes, the tool sends `reboot_dl` on the serial port; with an IPRO Debug Probe it also puts the chip in download mode through the probe's BOOT and RESET lines, and resets the chip when flashing is done. INTELPRO checked this with 0.7.0.1 on a Reef through the Debug Probe: no buttons or control keywords were needed, and it took about 8 s. With a plain USB-to-UART adapter and firmware without a shell, use the buttons. The manual steps below are for when the tool cannot handshake.

Download mode with the Debug Probe (macOS shown, from the SDK root):

<div class="ipro-steps" markdown>

1. **Raise BOOT and reset:** send `IPRODL_1`, then `IPRORST_RESET`.

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    Each command prints `[serial_monitor] Sent: …` and `[serial_monitor] TIMEOUT after 1s` (the normal ending without `--wait-for`); the console then goes silent.

2. **Flash:** keep BOOT raised and run the [flashing steps](#flashing) on the same `02` port.

3. **Release BOOT and reset:** send `IPRODL_0` and `IPRORST_RESET`; the board boots the new firmware.

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 3
    ```

</div>

## Flashing steps { #flashing }

<div class="ipro-steps" markdown>

1. **Free the serial port:** close every terminal program that has the console port open.

2. **Enter download mode** with any method from [Enter download mode](#download-mode). The console goes silent.

3. **Flash** from the IntelProCube directory. The example is `ipro7ai_reef_demo`; for other applications change `--pt` and add options as listed in [Partition tables](#partition-tables).

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

    The output starts with the settings of this run and ends with the verification (excerpt, timestamps left out):

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    [...] - Firmware is <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ...
    [...] - shake hand success
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

4. **Reset and open the console:** press SW2 (RESET) to boot the new firmware, then open the [console](#serial-monitor) at the application's baud rate.

</div>

## Partition tables { #partition-tables }

The partition table places the firmware, the `mfg` data (AI models) and other data in flash. IntelProCube ships general tables in `<IntelProCube>/chips/ipro7/partition/`, such as `partition_cfg_2M.toml`; applications that need a special layout keep their own `.toml` in the application directory.

| Application (Reef configuration) | `--pt` | Other options |
|---|---|---|
| `ipro7ai_reef_demo` (`.config`, `defconfig_wifi_ipro6s`) | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro7_uvc_cam` (`defconfig_reef_ov5640`, `defconfig_reef_rps`) | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro_ble_remote` (`defconfig_reef`) | `<SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml` | `--boot2` on the first flash, see the [next section](#boot2-ab) |
| `ipro_reef_teach` (`.config`) | `<SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml` | `--skip-ota`; `--mfg` on the first flash, see [ipro_reef_teach](#mfg) |
| Other Reef applications | as in the application's README | — |

`ipro7ai_reef_demo` links a 1 MB flash layout by default, which fits either in-package flash part. If the boot log reports JEDEC `0xEF4015` (2 MB), add `CONFIG_IPRO7_FLASH_2M=y` to `.config` to give the linker the whole part.

## First flash of ipro_ble_remote (boot2 and A/B table) { #boot2-ab }

The Reef configuration of `ipro_ble_remote` supports BLE OTA, which needs boot2 and two firmware slots, A and B. On the first wired flash, write boot2 and the application's own table together:

<div class="ipro-steps" markdown>

1. **Build:**

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    The image is `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`.

2. **Enter download mode and flash.** The boot2 image comes with IntelProCube, not with the SDK.

    ```bash
    cd <IntelProCube>
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --boot2 chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin \
        --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
        --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
    ```

    The output ends with `[All Success]`.

3. **Check:** press SW2. The console at 115200 baud shows the boot2 banner `[BOOT2] IPRO7 Boot2 v0.6.0`, then the application logs `[BLE] Advertising: IPRO-Remote`.

</div>

!!! warning "Never OTA with partition_cfg_2M.toml"
    If `ipro_ble_remote` was flashed to a Reef with the standard `partition_cfg_2M.toml`, an OTA update is written to a slot that boot2 never boots (0x12A000). For OTA, always flash with boot2 and `partition_cfg_2M_remote_ab.toml` as above. OTA steps: [OTA Firmware Update](../guides/ota.md).

## ipro_reef_teach (mfg data) { #mfg }

The Edge AI firmware `ipro_reef_teach` uses its own partition table; its `mfg` partition holds the mode setting and the voiceprint model. On the first flash, write the `mfg` data too:

```bash
make -C apps/ai/ipro_reef_teach
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 --skip-ota \
    --pt <SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml \
    --firmware <SDK>/apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin \
    --mfg <SDK>/reef_teach_mfg.bin
```

After a reset the console (115200) shows `RTCH:   mode: image …`, and a USB camera plus a serial port (`3896:0705`) appear on USB-C. To update the firmware only, leave out `--mfg`; the mode and models stay. Switching modes and using IPRO AI Studio: [IPRO AI Teach](../teach/firmware.md).

## Flashing with build_freertos.sh { #build-script }

On macOS and Linux, the `flash` action of `build_freertos.sh` works in this order:

1. Find the image in `build/`, or in `build_<name>/` with `-d defconfig_<name>`. If it is missing, stop with `Run 'build' first.`
2. Find the tool: `IPRO_FLASH_TOOL`, else `ipro_iot_tool_macos` / `ipro_iot_tool_linux` on `PATH`.
3. Find the port: `-p`, else `IPRO_SERIAL_PORT`, else the only `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`, `/dev/ttyACM*` or `/dev/ttyUSB*` present.
4. Send `reboot_dl` at the application's console baud rate (`CONFIG_PLATFORM_UART_BAUDRATE`, 115200 when unset) and wait 2 s.
5. Run `<tool> --chipname ipro7 --chip-variant <variant> --port <port> --firmware <bin> --baudrate 921600 [--pt <table>]`. Variant: `-c`, else `IPRO_CHIP_VARIANT`, else from the configuration (`IPRO7AI` for Reef configurations). Table: `-P`, else `IPRO_FLASH_PT`, else no `--pt`.
6. Print `✓ Flash succeeded` when the output contains `[All Success]`, otherwise `✗ Flash failed`.

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

Give `-P` the full path of the `.toml`: the script runs the tool from the current directory, not from the IntelProCube directory.

!!! note "What the script cannot do"
    - It cannot pass `--boot2`, `--mfg` or `--skip-ota`: run the tool directly for the first flash of `ipro_ble_remote` and the `mfg` data of `ipro_reef_teach`.
    - `--chipname` is fixed to `ipro7`, so it cannot flash IPRO6S images.
    - Firmware without a shell, or hung firmware, does not receive `reboot_dl`: enter download mode with the buttons first.
    - `flash` does not build; when you run `build` and `flash` separately, give both the same `-d`.

## Serial console { #serial-monitor }

The console is UART0 (GPIO20 TX / GPIO21 RX, U6 pins 3 / 4), 8N1, no flow control. The baud rate is `CONFIG_PLATFORM_UART_BAUDRATE` in the application's configuration, 115200 when unset:

| Baud rate | Reef configurations |
|---|---|
| 115200 | `ipro7ai_reef_demo` (both), `ipro_reef_teach`, `ipro_ble_remote`, `ipro_throughput_test`, `ipro_le_audio_headset`, `ipro7_uvc_cam` (both Reef configurations), `ipro_ai_link`, `ipro_agora_sentino` |
| 921600 | `ipro7_jpeg_decode` (`defconfig_reef`) |

To check a configuration file (no output means unset, so 115200):

```bash
grep CONFIG_PLATFORM_UART_BAUDRATE apps/multimedia/ipro7_jpeg_decode/defconfig_reef
```

### Interactive terminal { #terminal }

To type shell commands, use an interactive terminal program:

=== "macOS"

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    To quit: ++ctrl+a++, ++k++, answer `y`. `minicom` and `picocom` (from Homebrew) also work.

=== "Linux"

    ```bash
    picocom -b 115200 /dev/ttyUSB0
    ```

    To quit: ++ctrl+a++, ++ctrl+x++. `minicom -D /dev/ttyUSB0 -b 115200` and `screen` also work.

=== "Windows"

    PuTTY: set Connection type to **Serial**, Serial line to `COM5`, Speed to `115200`, and click **Open**. Tera Term or the VS Code Extension's `IPRO: Serial Monitor` also work.

Close the terminal program before flashing, or the tool cannot open the port.

### tools/serial_monitor.py { #serial-monitor-py }

The SDK's non-interactive console tool for scripts and automation (macOS / Linux; it uses only the Python standard library's termios, no pyserial). It opens the port, optionally sends one line, then reads until a timeout or a matching pattern.

```text
python3 tools/serial_monitor.py <port> [--baud 115200] [--timeout 30] [--send CMD] [--wait-for REGEX] [--log FILE]
```

| Option | Meaning |
|---|---|
| `--baud` | baud rate, 115200 by default |
| `--timeout` | seconds to read, 30 by default; `0` reads until ++ctrl+c++ |
| `--send` | one line to send before reading (CR LF appended) |
| `--wait-for` | stop when this regular expression matches |
| `--log` | also save the raw output to a file |

| Exit code | Meaning |
|---|---|
| 0 | the text matched by `--wait-for` contains `PASSED` |
| 1 | the matched text does not contain `PASSED` |
| 2 | timeout without a match (always 2 when `--wait-for` is not given) |
| 3 | opening the port or sending failed |

```bash
# send a command and read for 10 s
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# reboot, wait for the shell, and keep a log
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot --wait-for "shell ready" --timeout 15 --log boot.log
```

### Serial ports on macOS { #macos-cu }

macOS gives each serial port two names, `/dev/cu.*` and `/dev/tty.*`. Always use `/dev/cu.*`: `/dev/tty.*` waits for carrier detect and hangs with no output.

## Recognise the ports { #ports }

| Connection | macOS | Linux | Windows |
|---|---|---|---|
| USB-to-UART adapter on U6 | `/dev/cu.usbserial-XXXX` (depends on the adapter) | usually `/dev/ttyUSB0` | a new COM port in Device Manager |
| IPRO Debug Probe | two `/dev/cu.usbmodem…` ports: the one ending in `02` is the console (UART bridge), `04` is the CCI bridge | two `/dev/ttyACM*` ports | two COM ports |

The IPRO Debug Probe identifies itself on USB as `IPRO7 CMSIS_DAP`. To tell its two ports apart on Linux and Windows, open each at 115200 and press SW2: the one that shows the boot messages is the console.

The Reef's USB-C is not the console. Some applications make the board appear on USB-C as a USB device with INTELPRO's VID `0x3896`:

| Application | VID:PID | What the host sees |
|---|---|---|
| `ipro_reef_teach`, image mode | `3896:0705` | USB camera and serial port (named "IPRO7 UVC Cam" in the browser) |
| `ipro_reef_teach`, voice mode | `3896:0720` | serial port (CDC-ACM) |
| `ipro_reef_teach`, sensor mode | `3896:0721` | serial port (CDC-ACM) |
| `ipro7_uvc_cam` | `3896:0701` | USB camera |
| `ipro_ai_link` | `3896:0704` | serial port (CDC) |
| `ipro7ai_reef_demo` while `mic usb` runs | `3896:0003` | USB microphone (UAC) |
| `ipro_agora_sentino` | `3896:0138`, `3896:0104` | USB network interface (NCM), serial port (CDC) |
| `ipro_le_audio_headset` | `3896:0001` | USB audio (UAC, test PID) |

To list USB devices on the host: `system_profiler SPUSBDataType` on macOS, `lsusb` on Linux (for example `ID 3896:0705`), and on Windows the device's Properties → **Details** → **Hardware Ids** in Device Manager (for example `USB\VID_3896&PID_0705`).

## Verify { #verify }

- The last line of the flash output is `[All Success]`.
- After SW2, the console shows the boot messages at the application's baud rate; in applications with a shell, ++enter++ brings up `ipro />` and `help` lists the commands.
- Applications that use USB appear on the host with the VID:PID in the table above.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| The tool stops at the handshake without `[All Success]` | the board is not in download mode, or a terminal program holds the port | close the terminal; enter download mode with the buttons and retry |
| `flash jedec id: 00000000` and `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` is not `IPRO7AI`, so the flash pins are wrong | add `--chip-variant IPRO7AI` |
| The tool cannot find a partition table or boot2 file | the relative path is not resolved from the IntelProCube directory | `cd <IntelProCube>` first; give files inside the SDK as full paths |
| `✗ Flash tool not found: ipro_iot_tool_macos` | `IPRO_FLASH_TOOL` not set and the tool is not on `PATH` | `export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` |
| `✗ Binary not found: …` with `Run 'build' first.` | `flash` does not build, or the `-d` used for the build is missing | add `build` before `flash`; add the same `-d` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | more than one USB serial port (the Debug Probe alone has two) | name the console port with `-p` or `IPRO_SERIAL_PORT` |
| `No serial port found: pass -p PORT or set IPRO_SERIAL_PORT` | no USB serial port detected | check the adapter and its driver; see [Set Up Your Host](environment.md#usb-serial) |
| Flashing succeeded but the console is silent after reset | still in download mode (BOOT held by DTR or the probe), wrong baud rate, RX/TX swapped | release BOOT (send `IPRODL_0` to the probe) and press SW2; check the baud rate; swap RX and TX |
| Garbage on the console | wrong baud rate | reopen at the rate in [Serial console](#serial-monitor) |
| A terminal hangs on macOS | `/dev/tty.*` was used | use `/dev/cu.*` |
| `ipro_reef_teach` prints `NO MFG PARTITION` | the board does not carry the `partition_reef_teach.toml` layout | reflash with the application's table and `--mfg` as in [ipro_reef_teach](#mfg) |

## Next steps { #next-steps }

- [Build and Flash Workflow](../tutorials/build-and-flash.md): the everyday edit, build, flash and monitor loop.
- [macOS / Linux Command Line](command-line.md): every action and option of `build_freertos.sh`.
- [Debugging & Troubleshooting](../reference/debugging.md)
