---
title: "Flashing & Serial Console"
description: Flash FreeRTOS applications with the IntelProCube command-line tool, per-board flash settings, what build_freertos.sh flash does, and console baud rates with serial_monitor.py.
migrate_from:
  - "getting-started.html#flashing"
  - "getting-started.html#serial-monitor"
  - "tools-debugging.html#flash-tool"
  - "tools-debugging.html#serial-monitor"
---

# Flashing & Serial Console

FreeRTOS applications are flashed over the serial port with the IntelProCube command-line tool, and the console runs on the same UART. Follow these steps to flash any application, then open the console at that application's baud rate. Zephyr images use `west flash` instead; see [First Zephyr Application](first-app-zephyr.md).

## Prerequisites { #prerequisites }

- The IntelProCube v0.6.3 command-line tool: `ipro_iot_tool.exe` (Windows), `ipro_iot_tool_macos` or `ipro_iot_tool_linux`. Not included in V2.1.0; contact INTELPRO.
- A built image: `apps/<category>/<app>/build/build_out/<app>_IPRO7.bin`, or `build_<name>/build_out/` when built with `DEFCONFIG=defconfig_<name>`.
- The board's serial port: `/dev/cu.usbserial-XXXX` on macOS, `/dev/ttyUSB0` on Linux, `COM5` on Windows.

## Flash tool { #flash-tool }

`build_freertos.sh`, the apps' `flash.sh` scripts and `west flash` find the tool through `IPRO_FLASH_TOOL`, or else look for the executable for your OS on PATH. When you run the tool yourself and give the partition table as `chips/...`, run it from the IntelProCube directory. On Windows you can also flash with `IPRO: Flash` in the VS Code Extension; see [VS Code Extension](../guides/vscode.md).

Every flash uses `--chipname ipro7`, `--chip-variant` (the board's flash pin setting, see below), `--port`, `--baudrate 921600` (the download baud rate the application READMEs and scripts use), `--firmware` and, where needed, `--pt` (the partition table). All options are listed in [Tool Command Lines](../reference/tools.md#flash-tool).

`--chip-variant` writes the matching `flash_pin` into `chips/ipro7/eflash_loader/eflash_loader_cfg.ini` in the tool directory: `IPRO7` writes `0x2`, `IPRO7AI` writes `0x9`. The tool has no other option for the flash pins, and it ships with `0x2`. Anything that runs the tool without `--chip-variant` (`build_freertos.sh flash`, the apps' `flash.sh`, `west flash`) uses whatever value is in that file, so on a Reef or IPRO7AI EVK run the tool once with `--chip-variant IPRO7AI`, or check that the file says `0x9`.

!!! warning "Judge by the output"
    The tool exits with 0 even when flashing fails. It has only succeeded if the output contains `[All Success]`.

## Flashing steps { #flashing }

<div class="ipro-steps" markdown>

1. **Free the serial port**: close anything that is monitoring the same port.

2. **Enter download mode**: if the board is running SDK firmware with a shell, send `reboot_dl` at the firmware's current console rate:

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 115200 --send reboot_dl --timeout 2
    ```

    Otherwise use the buttons or straps listed in [Per-board settings](#board-settings). A board in download mode prints nothing on the console.

3. **Flash**: run the tool from the IntelProCube directory. The example flashes `ipro7ai_reef_demo` to the Reef; for other boards, change `--chip-variant` and `--pt` as in [Per-board settings](#board-settings).

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

4. **Check and reset**: once the output shows `[All Success]`, reset the board and open the [console](#serial-monitor) at the application's baud rate.

</div>

## Per-board settings { #board-settings }

| | IPRO7AI Reef EVK | IPRO7AI EVK | IPRO7 EVB |
|---|---|---|---|
| `--chip-variant` | `IPRO7AI` | `IPRO7AI` | `IPRO7` |
| Partition table | `chips/ipro7/partition/partition_cfg_2M.toml` (Reef application READMEs) | The `.toml` in the AI application's directory, passed by its `flash.sh` | Per the application README; the SDK README example passes no `--pt` |
| Download mode | Hold SW1 (BOOT), tap SW2 (RESET); U6's DTR / RTS reach BOOT and RESET, so an auto-download cable works; or `reboot_dl` | `reboot_dl`; for the manual method see the board page | `reboot_dl`, or the BOOT strap |
| Console | UART0 on U6 (SH1.0), GPIO20 TX / GPIO21 RX | UART0, GPIO20 TX / GPIO21 RX | UART0, GPIO20 TX / GPIO21 RX |

`IPRO7` for the IPRO7 EVB (`flash_pin` `0x2`) follows the mapping in the SDK README. If the handshake passes and then reports `flash jedec id: 00000000`, flash again with `--chip-variant IPRO7AI` (`0x9`).

On the IPRO7AI EVK, `ipro7ai_evk_person_detect`, `ipro7ai_evk_rps` and `ipro7ai_evk_launcher` come with a `flash.sh`: run it once with `--full` to write the partition table, firmware and model, then without arguments to update only the firmware. The script takes the serial port from the `PORT` environment variable and, in `BAUD`, the console rate of the firmware currently on the board (used to send `reboot_dl`; the default is the application's own rate):

```bash
cd apps/ai/ipro7ai_evk_person_detect
PORT=/dev/cu.usbserial-XXXX BAUD=115200 ./flash.sh --full
```

Wiring, jumpers and the manual download-mode procedure for each board are on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md), [IPRO7AI EVK](../hardware/boards/ipro7ai-evk.md) and [IPRO7 EVB](../hardware/boards/ipro7-evb.md).

## Flashing with build_freertos.sh { #build-script }

`build_freertos.sh` actions can be chained and run in order:

```bash
./build_freertos.sh ipro7_demo build flash monitor -p /dev/cu.usbserial-XXXX
```

- `flash` sends `reboot_dl` at 115200 through `tools/serial_monitor.py`, then runs `<tool> --chipname ipro7 --port <port> --firmware <bin> --baudrate 921600` and checks for `[All Success]`.
- `monitor` opens the port with `tools/serial_monitor.py`, sends `reboot` and reads for `-t` seconds (default 30).
- Serial port: `-p`, else `IPRO_SERIAL_PORT`, else the only USB serial port connected.
- Alternate configurations: add `-d defconfig_<name>`. If you run `build` and `flash` separately, pass it both times so that `flash` finds the image under `build_<name>/`.

!!! warning "The script's fixed settings may not suit your board"
    - **No `--chip-variant`**: the tool uses the `flash_pin` in its ini file. The Reef and IPRO7AI EVK need `0x9`; see [Flash tool](#flash-tool).
    - **No `--pt`**: the tool writes its own default partition table. When a board or application needs a specific table (`partition_cfg_2M.toml` for the Reef applications, the `.toml` files of the IPRO7AI EVK AI applications), run the tool directly or use the application's `flash.sh`.
    - **`reboot_dl` and `monitor` always use 115200 baud**: firmware with a 921600-baud console, or without a shell, does not receive `reboot_dl`, so enter download mode by hand and monitor with `python3 tools/serial_monitor.py <port> --baud 921600`. `monitor` also sends `reboot` first, so the board restarts.
    - **`flash` does not build**: it stops if the image is missing, so put `build` in front of it.
    - **`monitor` exit status**: on a timeout, on ++ctrl+c++, or when `-w` matches text without `PASSED`, the exit status is not 0; the script counts the action as failed and skips the actions after it. Make `monitor` the last action.

## Serial console { #serial-monitor }

The console of a FreeRTOS application is UART0 (GPIO20 TX / GPIO21 RX), 8N1. The baud rate comes from `CONFIG_PLATFORM_UART_BAUDRATE` in the application's `.config` and is 115200 when the key is not set.

| Baud rate | Applications |
|---|---|
| 115200 | Most applications, including `ipro7ai_reef_demo`, `ipro7_demo`, `ipro7ai_evk_person_detect` and the BLE applications |
| 921600 | `ipro7ai_evk_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_rps`, `ipro7_uvc_cam`, `ipro_epd_el036` and a few others |
| 2000000 | Zephyr images (`ipro7_evb`, `ipro7ai_evk`) |

Alternate configuration files can use a different rate; for example the `config_*` files of `ipro7ai_evk_demo` and the `defconfig_reef_*` files of `ipro7_uvc_cam` use 115200. Check the file you actually build with (no output means the key is not set, so 115200):

```bash
grep CONFIG_PLATFORM_UART_BAUDRATE apps/platform/ipro7ai_reef_demo/.config
```

`ipro_enc28j60_test`, `ipro_gh7007_test`, `ipro_gh7007_video` and `ipro_pio_sdh_test` put their console on USB CDC rather than UART0.

### tools/serial_monitor.py { #serial-monitor-py }

```text
python3 tools/serial_monitor.py <port> [--baud 115200] [--timeout 30] [--send CMD] [--wait-for PATTERN] [--log FILE]
```

`--baud` defaults to 115200; `--timeout 0` keeps reading until you press ++ctrl+c++. Every option and exit status is listed in [Tool Command Lines](../reference/tools.md#serial-monitor).

```bash
# Keep reading (115200)
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0

# A 921600 application, read for 60 s and save the log
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 60 --log console.log

# Send a command and read the reply
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 5
```

- The script uses only Python's standard termios module (no pyserial) and runs on macOS and Linux. On Windows, use the VS Code Extension's Serial Monitor or another serial terminal.
- It is not an interactive terminal: each run sends just the one `--send` line. For a back-and-forth session, use an interactive serial terminal.
- On macOS use `/dev/cu.*`, not `/dev/tty.*`: the latter waits for carrier detect and blocks.
- Stop monitoring before you flash, so the port is free.

## Verify { #verify }

- The flash output contains `[All Success]`.
- After a reset, the console shows the application's boot messages; FreeRTOS applications with the shell enabled show the `ipro />` prompt, and `help` lists the commands.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| No `[All Success]`; the handshake fails | The board is not in download mode, or another program holds the port | Enter download mode as in [Per-board settings](#board-settings); close the monitor |
| The handshake passes, then `flash jedec id: 00000000` and `IPRO FLASH MATCH TYPE FAIL` | `flash_pin` does not match the board | Flash with the right `--chip-variant` (`IPRO7AI` for the IPRO7AI EVK and Reef); if an IPRO7 EVB still shows this with `IPRO7`, use `IPRO7AI` |
| `Flash tool not found` | `IPRO_FLASH_TOOL` is not set and the tool is not on PATH | Set `IPRO_FLASH_TOOL` |
| `Binary not found` with `Run 'build' first.` | `flash` does not build | Put `build` before `flash`; with an alternate configuration, pass `-d` to `flash` as well |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | More than one USB serial port is connected | Use `-p` or `IPRO_SERIAL_PORT` |
| Garbled console | Wrong baud rate | Set `--baud` to the application's `CONFIG_PLATFORM_UART_BAUDRATE` |
| No console output at all | The board is still in download mode, or a `/dev/tty.*` device was used on macOS | Reset the board; use `/dev/cu.*` |
| An IPRO7AI EVK AI application shows `NO MFG PARTITION` | The board has the tool's default partition table, which has no `mfg` partition | Reflash with the application's `./flash.sh --full` |

## Next steps { #next-steps }

- [Tool Command Lines](../reference/tools.md): every option of `build_freertos.sh`, `serial_monitor.py` and the Zephyr scripts.
- [Build and Flash Workflow](../tutorials/build-and-flash.md)
- [Debugging & Troubleshooting](../reference/debugging.md)
