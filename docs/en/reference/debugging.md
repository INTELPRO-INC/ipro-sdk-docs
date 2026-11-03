---
title: "Debugging & Troubleshooting"
description: Debugging on the IPRO7AI Reef EVK with the serial console and logs, entering download mode, reading crash output, analyzing builds, running the on-board self-test, and tables for common build, flash, console and run-time problems.
migrate_from:
  - "tools-debugging.html#gdb-debugging"
  - "tools-debugging.html#crash-analysis"
  - "getting-started.html#debugging"
  - "getting-started.html#troubleshooting"
  - "getting-started.html#board-testing"
  - "getting-started.html#next-steps"
---

# Debugging & Troubleshooting

IPRO7 FreeRTOS applications are debugged over the serial console: shell commands and logs show the state as it happens, and on a crash the firmware prints its own exception analysis and call stack. The steps on this page are for the IPRO7AI Reef EVK V4.0.

## Serial console { #debugging }

The Reef's console is UART0 (GPIO20 TX / GPIO21 RX) on the U6 debug connector; the same UART is used for flashing. U6 does not power the board; USB-C does. Wiring is on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#debug-connector).

| Connection | Port on the host |
|---|---|
| 3.3 V USB-to-UART cable (on U6 pins 2, 3, 4) | macOS `/dev/cu.usbserial-XXXX`, Linux `/dev/ttyUSB0`, Windows a port such as `COM5` |
| IPRO Debug Probe (pin-reversed cable to U6) | Enumerates as `IPRO7 CMSIS_DAP` with two CDC ports: the one whose name ends in `02` is the Reef console (for example `/dev/cu.usbmodemXXXX02`), `04` is the CCI bridge |

The baud rate is `CONFIG_PLATFORM_UART_BAUDRATE` in the application's configuration file, 115200 when unset. Every Reef configuration uses 115200 except `defconfig_reef` of `ipro7_jpeg_decode`, which uses 921600. Among the configurations for other boards, the `.config` of `ipro7ai_evk_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_rps`, `ipro_speaker_recog`, `ipro7_uvc_cam`, `ipro7_jpeg_decode` and `ipro_epd_el036` also use 921600. Framing is 8N1 with no flow control.

<div class="ipro-steps" markdown>

1. **Open the console** with any serial terminal program. With `screen` on macOS / Linux:

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    Press Enter and the shell prompt appears. To leave `screen`, press Ctrl-A, then K.

2. **List the commands**: type `help`. It lists the built-in commands and those the application registers.

3. **Send one command and read the answer** (no interactive terminal needed):

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "free" --timeout 3
    ```

    It prints the heap total, free and minimum-ever free, and exits after 3 seconds.

</div>

Every application with `CONFIG_SHELL=y` has these built-in commands:

| Command | Purpose |
|---|---|
| `help` | List all commands |
| `ps` | Task list and CPU usage |
| `free` | Heap total, free and minimum-ever free |
| `time` | Time since boot |
| `p <addr> [count] [width]` | Read memory (width 1, 2 or 4 bytes, default 4) |
| `m <addr> <value> <width>` | Write memory |
| `memtrace <addr> [count]`, `memtrace <addr> <value> <count>` | Read or fill memory as 32-bit words (hexadecimal address) |
| `reboot` | Reboot |
| `reboot_dl` | Reboot into download mode; prints `reboot to download mode` |
| `reboot_usb [code]` | Reboot into boot2's USB download mode (only for images flashed with boot2); see [Enter download mode](#download-mode) |
| `watchdog`, `watchdog test` | In applications with `CONFIG_APP_WATCHDOG` (for example `ipro_reef_teach`): show the AON watchdog state; `test` stops feeding it and the board restarts after the time-out |
| `ls`, `cat`, `hexdump`, `pwd`, `cd`, `mkdir`, `rm`, `cp` | File-system commands; present only when the configuration has `CONFIG_EVFS`, `CONFIG_EVFS_POSIX` and `CONFIG_IPRO_OSAL` |

Logs use the `IPRO_LOGx` macros (see [API Reference](api/index.md#log-api)). For debug-level logs, set `CONFIG_LOG_DEFAULT_LEVEL=4` in `.config` and rebuild; the value is an integer, and the shipped applications use 3 (info).

Boot messages worth knowing:

| Message | Meaning |
|---|---|
| `[XTAL] capcode <boot value> -> <set value>` | The `CONFIG_IPRO7_XTAL_CAPCODE` crystal trim was applied; on the Reef it defaults to 95 when not set |
| `[PSRAM] WARNING: init failed` | The application enables `CONFIG_USE_PSRAM`, but PSRAM did not initialize |
| `[BOOT2] IPRO7 Boot2 v0.5.2` | The image was flashed with boot2 (for example the Reef OTA build of `ipro_ble_remote`); boot2 runs first, then starts the application |

## Enter download mode { #download-mode }

The Reef must be in download mode before flashing. In download mode the console prints nothing; after flashing, press SW2 (RESET) once to boot normally.

| Method | When to use |
|---|---|
| Keys SW1 + SW2 | Always works, including the first flash and when the firmware has hung |
| `reboot_dl` at the console | The board runs SDK firmware with a shell |
| DTR / RTS auto-download cable on U6 | A USB-to-UART cable with DTR and RTS wired to U6 pins 5 and 6 |
| IPRO Debug Probe keywords | The probe is connected to U6 |

<div class="ipro-steps" markdown>

1. **Keys**: hold SW1 (BOOT), press and release SW2 (RESET), then release SW1. The console stays silent: the board is in download mode.

2. **Console command**: type `reboot_dl` in the shell, or on the host run:

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
    ```

    It prints `reboot to download mode` and then nothing more. `build_freertos.sh flash` sends this command for you at the application's console baud rate.

3. **Auto-download cable**: U6 pin 5 (BOOT) and pin 6 (RESET) reach GPIO41 and the reset pin through 1 kΩ each. With a USB-to-UART cable's DTR on pin 5 and RTS on pin 6, a host program that controls DTR / RTS can put the board in download mode without the keys: RESET is released while BOOT is high.

4. **IPRO Debug Probe**: on the probe port whose name ends in `02`, send `IPRODL_1`, then `IPRORST_RESET`; keep DL high while flashing; afterwards send `IPRODL_0` and `IPRORST_RESET` to boot normally:

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    # flash with --port /dev/cu.usbmodemXXXX02 and check for [All Success]
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    After the last line, the application's boot messages appear on the console.

</div>

**boot2 USB download mode**: an image flashed with boot2 (for example the Reef OTA build of `ipro_ble_remote`) can reboot into boot2's USB download mode with `reboot_usb [code]`; it prints `reboot to boot2 USB download (HBN_RSV3=0x555342FF)`. `code` sets how long boot2 waits (`0x01` 2 s, `0x02` 5 s, `0xFF` forever; default `0xFF`). boot2 also stops in this USB rescue mode when an OTA package fails its check. The SDK ships no host tool for flashing over USB; to reflash, enter download mode with one of the UART methods above.

## GDB and debug probe { #gdb-debugging }

!!! info "Not included in V2.2.0"
    The OpenOCD configuration and the procedure for on-target debugging over JTAG are not included in V2.2.0; contact INTELPRO.

- **The ELF has debug information**: the default build compiles with `-g3 -Os`, so `<build dir>/build_out/<app>_IPRO7.elf` works with the toolchain's `riscv64-unknown-elf-addr2line` or `riscv64-unknown-elf-gdb` for offline analysis. The `.bin` you flash has no symbols.
- **Prebuilt libraries have no debug information**: the IPRO BLE controller, RF, AI, ISP, LC3 and low-power framework libraries are stripped of debug information and keep only symbol names, so you cannot step through their source.
- **IPRO Debug Probe**: on the Reef it serves as the console bridge and download-mode control (see [Enter download mode](#download-mode)). The probe firmware is not part of the SDK; its hardware and wiring are in the Debug Probe User Manual on [Documents](../documents/index.md).

## Crash analysis { #crash-analysis }

On a CPU exception, the default exception handler prints these blocks on the console:

| Block | Contents |
|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` | `MCAUSE`, `MEPC`, `MTVAL` and the exception type (for example `Illegal Instruction`, `Load Access Fault`) |
| `=== ADDRESS ANALYSIS ===` | The region of the faulting PC (FLASH / PSRAM / OCRAM), the return address `ra`, and whether the stack pointer `sp` is in range |
| `=== FAULTING TASK ===` | The FreeRTOS task that faulted and its stack high-water mark (0 means its stack has overflowed) |
| Register dump | General registers at the time of the exception |
| `=== STACK BACKTRACE ===` | Call chain walked through the frame pointer (`s0`), one return address per level |

<div class="ipro-steps" markdown>

1. **Save the output**: log the console to a file, for example `python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0 --log crash.log`, reproduce the problem, then press Ctrl-C.

2. **Turn addresses into source lines**: look up the faulting PC (`MEPC`), `ra` and the backtrace addresses in the `.elf` of the same build:

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-addr2line -f -C \
        -e apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf \
        0x1301c148 0x13004a2e
    ```

    Each address prints two lines: the function name and `file:line`. `??:0` means the address is not in this ELF, or the ELF is from a different build.

3. **Reset the board**: press SW2 (RESET) once.

</div>

!!! warning "`==DUMP_READY:2000000==` keeps repeating"
    The `.config` of `ipro7ai_reef_demo` and `ipro_reef_teach` sets `CONFIG_EXCEPTION_DUMP=y`: after the diagnostics above, the console prints `==DUMP_READY:2000000==` about every 10 seconds for up to 5 minutes, waiting for a host tool to read memory. That host tool is not included in V2.2.0. Save the diagnostics printed above, then press SW2 to reset; if you do not want the wait, set `CONFIG_EXCEPTION_DUMP=n` in `.config` and rebuild.

| Setting | Effect |
|---|---|
| `CONFIG_ENABLE_FRAME_POINTER=y` | Compiles with `-fno-omit-frame-pointer` so the backtrace has the full call chain; without it you usually get only the faulting PC and `ra` |
| `CONFIG_EXCEPTION_AUTO_REBOOT=y` | Reboots after printing the diagnostics, with reset reason `HAL_RST_REASON_EXCEPTION`; useful in production, best left off during development |
| `CONFIG_EXCEPTION_DUMP=y` | Waits for a host tool after the diagnostics (see the note above) |

`.config` is read as written and Kconfig defaults are not applied, so set these explicitly.

Other fatal messages come from the [FreeRTOS hooks](api/index.md#rtos-platform):

| Message | Cause | Fix |
|---|---|---|
| `[!] Stack overflow: <task>` | That task ran out of stack | Increase the stack depth in `xTaskCreate()` (in words); the `[STACKS]` list that follows shows each task's headroom |
| `[!] Malloc failed, requested: …` | Out of heap | Watch the free heap with `free`, allocate less or enable PSRAM; look up the `caller` address with `addr2line` |
| `[!] ASSERT <file>:<line>` | A `configASSERT()` failed | Check the condition at that file and line; look up the `Caller` address with `addr2line` |

## Build analysis { #build-analysis }

With `build_freertos.sh`, the full output goes to `<build dir>/build.log` and only the last 30 lines are printed on failure; add `-v` to see everything. These CMake configure messages tell you what the build used:

| Message | Meaning |
|---|---|
| `[toolchain] Vendor toolchain detected …` | The INTELPRO toolchain was found and the IPRO7 DSP extensions and tuning are on; `Standard toolchain detected` means a generic RISC-V GCC |
| `[bluetooth] Using unified Zephyr 4.4 host (ipro_bt_host)` | The BLE host is in the build |
| `[ipro_ble_controller] Using prebuilt …` | The BLE controller library actually linked; check it against your `CONFIG_IPRO_BLE_CTLR_*` |
| `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` | The Reef build added the crystal trim default; if this line is missing, check that the configuration has `CONFIG_IPRO7AI_REEF=y` |
| `AI disabled: OCRAM=240KB (256-16)`, `AI+MM (EM=0): OCRAM=64KB …` | OCRAM region size for this build: 256 KB minus `CONFIG_EM_SIZE` without AI; 64 KB or 48 KB with both AI and imaging |

The linker prints the use of each memory region at the end of the build; for out-of-memory analysis see [Size and memory analysis](tools.md#size-analysis).

## On-board self-test { #board-testing }

The Reef's out-of-box firmware `ipro7ai_reef_demo` has a built-in self-test, handy when a board arrives, after rewiring or after flashing. Put SW7 on CAM and SW8 on PWR.

<div class="ipro-steps" markdown>

1. **Check the boot**: press SW2 (RESET). The RGB LED breathes blue once and goes off, and the shell prompt appears on the console.

2. **Run the self-test**

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10
    ```

    Within about 3 seconds the LED lights red, green and blue, the speaker plays a 1 kHz tone, and the console prints the following (lines 3 and 4 depend on the board's state):

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: <sensor name> at 0x<address>
    done - keys: press any and run `btn status`
    ```

    With a microSD card inserted, line 3 says `something seated`; `no sensor` on line 4 means no camera was found.

3. **Check the keys**: press SW3, SW4, SW5 and BOOT; the LED lights red, green, blue and white. Then send `btn status`; it lists each key's state and press count.

4. **Board state**: send `reef status`; it lists the console pins, keys, LED, speaker, headset detect, SD slot and camera.

</div>

`ipro_unit_test` (unit tests for the HAL and shared components, `./build_freertos.sh test ipro_unit_test`) needs the IPRO7 EVB.

## Troubleshooting { #troubleshooting }

### Build { #troubleshooting-build }

| Symptom | Cause | Fix |
|---|---|---|
| `No cmake found`, or `tools/cmake` fails to run on macOS | No CMake on the system; the bundled `tools/cmake/` is a Linux x86-64 binary | Install CMake 3.15 or newer (3.20 or newer for Zephyr; for example `brew install cmake`), put it on `PATH`, and check with `cmake --version` |
| `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc` not found | Toolchain not installed, or installed elsewhere | Get the toolchain from INTELPRO; in another location, `export CROSS_COMPILE=<path>/bin/riscv64-unknown-elf-` |
| `[ipro_ble_controller] CONFIG_EM_SIZE must match …` | `CONFIG_EM_SIZE` missing from `.config` | Add `CONFIG_EM_SIZE` (the shipped applications use 16 or 32) |
| `bt54_iso2 needs at least 32 KB EM` | An LE Audio configuration with a 16 KB EM | Set `CONFIG_EM_SIZE=32` |
| `unsupported variant` or `unsupported feature profile` | Controller settings outside the shipped combinations | Use `link1_periph`, `link1`, `link2` or `link4` for `CONFIG_IPRO_BLE_CTLR_LIB`, and `bt52` or `bt54_iso2` for `CONFIG_IPRO_BLE_CTLR_FEATURE` |
| Configure fails in `ipro_ble_controller` after setting `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`, `CONFIG_IPRO_BLE_CTLR_SUBRATING`, `CONFIG_IPRO_BLE_CTLR_CSSA`, `CONFIG_IPRO_PM_BLE` or `CONFIG_IPRO_PM_PDS_CONNECTED` | These settings build the BLE controller from source, and the package ships only prebuilt libraries | Remove them; contact INTELPRO if you need those features |
| Link error `undefined reference to adc_ioctl` | An ADC convenience macro such as `adc_channel_start()` was used | Use `hal_adc_ioctl()` |
| A feature such as `CONFIG_AI_SUPPORT` is on but its dependencies are not | The build reads `.config` as written and does not apply Kconfig `select` or `depends on` | Set the dependencies explicitly, for example `CONFIG_USE_PSRAM=y` for AI; see [Build System & Configuration](../guides/build-system.md) |
| An image built with plain `make` does nothing on the Reef | Most applications' `.config` targets another board | Build the Reef configuration with `DEFCONFIG=defconfig_reef…`; see the [FAQ](faq.md#reef-apps) |
| The linker reports a memory region overflow | Code or data exceed `flash`, `ocram` or another region | Find the largest users as in [Size and memory analysis](tools.md#size-analysis); with AI and imaging both on, OCRAM is only 64 KB or 48 KB |

### Flashing { #troubleshooting-flash }

| Symptom | Cause | Fix |
|---|---|---|
| No `[All Success]`; the output shows `flash jedec id: 00000000` or `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` does not match the board; the tool reused the last setting | Use `--chip-variant IPRO7AI` on the Reef and flash again |
| The tool cannot talk to the board | The board is not in download mode, or another program holds the serial port | [Enter download mode](#download-mode), close any serial monitor, and retry |
| `build_freertos.sh flash` says `Flash tool not found` | The IntelProCube tool was not found | Set `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`, or put the tool's directory on `PATH` |
| `No serial port found` or `Several serial ports` | None, or more than one, USB serial port | Pass `-p`, or set `IPRO_SERIAL_PORT` |
| `build_freertos.sh flash` fails for an IPRO6S application | The script always passes `--chipname ipro7` | Flash with `--chipname ipro6` from the IntelProCube directory; see [IPRO6S](../hardware/chips/ipro6s.md) |
| The Reef is completely silent after a BLE OTA | OTA was run on a board flashed with the standard `partition_cfg_2M.toml` | Enter download mode and reflash with boot2 and `partition_cfg_2M_remote_ab.toml`; see [ipro_ble_remote](../examples/ipro_ble_remote.md) |

### Console { #troubleshooting-console }

| Symptom | Cause | Fix |
|---|---|---|
| Garbage characters | Wrong baud rate | Use the application's `CONFIG_PLATFORM_UART_BAUDRATE`: 115200 for most Reef configurations, 921600 for `defconfig_reef` of `ipro7_jpeg_decode` |
| No output at all | The board is in download mode; or TX / RX are swapped; or you opened the probe's `04` port | Press SW2 to reset; check that U6 pin 3 (TX) goes to the cable's RX and pin 4 to TX; on the probe use the port ending in `02` |
| The program hangs with no output on macOS | You opened `/dev/tty.*` | Use `/dev/cu.*` |
| `Resource busy`, or `serial_monitor.py` exits with code 3 | Another program holds the port | Close other terminals or monitors; find the holder with `lsof /dev/cu.usbserial-XXXX` |
| `cat` shows only part of the output | `cat` buffers serial input on macOS | Use `tools/serial_monitor.py` or another serial terminal |
| `==DUMP_READY:2000000==` keeps repeating | Waiting for a dump tool after a crash | See [Crash analysis](#crash-analysis) |

### Run time and BLE { #troubleshooting-runtime }

| Symptom | Cause | Fix |
|---|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` on the console | CPU exception | Read it as in [Crash analysis](#crash-analysis) |
| `[!] Stack overflow`, `[!] Malloc failed`, `[!] ASSERT` | Out of stack or heap, or a failed assertion | See the table in [Crash analysis](#crash-analysis) |
| `[PSRAM] WARNING: init failed` | The build enables PSRAM, but PSRAM did not initialize | Check that you built a Reef configuration (`CONFIG_IPRO7AI_REEF=y`); if it persists, contact INTELPRO |
| `cam probe` or `reef selftest` reports `no sensor` | SW7 is not on CAM, or the camera cable is not seated | Set SW7 to CAM; unplug USB-C, reseat the cable, then power up again |
| Bonds are lost after a reset and the phone has to pair again | Bond storage is off, or bonds are not loaded before advertising | See the [FAQ](faq.md#ble-bonding) |
| BLE throughput far below expectations | Connection parameters, PHY or CPU load | See [BLE Throughput Test](../tutorials/ble-throughput.md) |

## Next steps { #next-steps }

- [Tool Command Lines](tools.md): every option of the build, flash and monitor tools.
- [Test your application](../tutorials/testing.md): testing your own application on the Reef.
- [API Reference](api/index.md): platform, BLE, HAL and logging APIs.
- [FAQ](faq.md): common questions on building, BLE, networking and RTOSes.
