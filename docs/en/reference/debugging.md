---
title: "Debugging & Troubleshooting"
description: Debug with the serial console and logs, read crash output, analyze builds, run the on-board unit tests, and look up common build, flash, console and run-time problems.
migrate_from:
  - "tools-debugging.html#gdb-debugging"
  - "tools-debugging.html#crash-analysis"
  - "getting-started.html#debugging"
  - "getting-started.html#troubleshooting"
  - "getting-started.html#board-testing"
  - "getting-started.html#next-steps"
---

# Debugging & Troubleshooting

IPRO7 FreeRTOS applications are debugged mainly over the serial console: shell commands and logs show state as it happens, and on a crash the firmware prints its own exception analysis and call chain.

## Serial console { #debugging }

The console is on UART0 (GPIO20 TX / GPIO21 RX); on the IPRO7AI Reef EVK it comes out on connector U6. The baud rate is `CONFIG_PLATFORM_UART_BAUDRATE` in the application's `.config`, 115200 when unset; a few applications such as `ipro7ai_evk_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_rps`, `ipro7_uvc_cam` and `ipro_epd_el036` use 921600. Zephyr images always run at 2000000 baud. To open the console, see [serial_monitor.py](tools.md#serial-monitor).

Every application with `CONFIG_SHELL=y` has these built-in commands; `help` also lists the ones the application registers:

| Command | Purpose |
|---|---|
| `help` | List all commands |
| `ps` | Task list with CPU usage |
| `free` | Total, free and minimum-ever free heap |
| `time` | Time since boot |
| `p <addr> [count] [width]` | Read memory (width 1, 2 or 4 bytes; default 4) |
| `m <addr> <value> <width>` | Write memory |
| `reboot` | Reboot |
| `reboot_dl` | Reboot into download mode, ready for flashing |

Logs use the `IPRO_LOGx` macros (see [API Reference](api/index.md#log-api)). For debug-level logs, set `CONFIG_LOG_DEFAULT_LEVEL=4` in `.config` and rebuild; the value is an integer, and the shipped applications use 3 (info).

Boot messages worth knowing:

| Message | Meaning |
|---|---|
| `[XTAL] capcode <boot value> -> <setting>` | The crystal trim from `CONFIG_IPRO7_XTAL_CAPCODE` was applied; on the IPRO7AI Reef EVK it defaults to 95 when the config does not set it |
| `[PSRAM] WARNING: init failed` | The application enables `CONFIG_USE_PSRAM`, but PSRAM did not initialize |

## GDB and debug probe { #gdb-debugging }

!!! info "Not included in V2.1.0"
    The OpenOCD configuration needed for on-chip JTAG debugging is not included in V2.1.0; contact INTELPRO.

- **The ELF carries debug information**: the default build compiles with `-g3 -Os`, so `<app>/build/build_out/<app>_IPRO7.elf` works directly with the toolchain's `riscv64-unknown-elf-addr2line` or `riscv64-unknown-elf-gdb` for offline analysis. The `.bin` you flash has no symbols.
- **Prebuilt libraries have no debug information**: the IPRO BLE controller, RF, AI, ISP, LC3 and low-power framework libraries are stripped of debug information and keep only symbol names, so you cannot step through their source.
- **IPRO Debug Probe**: it enumerates as `IPRO7 CMSIS_DAP` with two CDC serial ports. The one whose name ends in `02` is the UART bridge to the board's console (UART0); `04` is the CCI bridge. `west flash` uses the probe by default to put the board in download mode (`--boot probe`, see [Zephyr scripts](tools.md#zephyr-tools)). The probe's hardware and wiring are in the *Debug Probe Board User Guide* listed under [Documents](../documents/index.md).

## Crash analysis { #crash-analysis }

On a CPU exception, the default exception handler prints these blocks on the console and then halts:

| Block | Contents |
|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` | `MCAUSE`, `MEPC`, `MTVAL` and the exception type (e.g. `Illegal Instruction`, `Load Access Fault`) |
| `=== ADDRESS ANALYSIS ===` | Which region the exception PC is in (FLASH / PSRAM / OCRAM), the return address `ra`, and whether the stack pointer `sp` is in range |
| `=== FAULTING TASK ===` | The FreeRTOS task that faulted and its minimum free stack (0 means that task overflowed its stack) |
| Register dump | The general registers at the exception |
| `=== STACK BACKTRACE ===` | The call chain walked through the frame pointer (`s0`), one return address per level |

Turn the exception PC, `ra` and the backtrace addresses into function names and source lines with the toolchain's `addr2line`:

```bash
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-addr2line -f -C \
    -e apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf \
    0x1301c148 0x13004a2e
```

The addresses must come from the same build as the `.elf`; after a rebuild, old addresses no longer apply.

| Setting | Effect |
|---|---|
| `CONFIG_ENABLE_FRAME_POINTER=y` | Compiles with `-fno-omit-frame-pointer` so the backtrace has the full call chain; without it you usually get only the exception PC and `ra` |
| `CONFIG_EXCEPTION_AUTO_REBOOT=y` | Reboots after printing the diagnostics and records the reset reason `HAL_RST_REASON_EXCEPTION`; meant for production, keep it off while developing |
| `CONFIG_EXCEPTION_DUMP=y` | After the diagnostics, prints `==DUMP_READY:` and waits for a host tool to read memory. That host tool is not included in V2.1.0; when you see this message, read the diagnostics above it and reset the board |

`.config` is read as written and Kconfig defaults are not applied, so write these settings out explicitly.

Other fatal messages come from the [FreeRTOS hooks](api/index.md#rtos-platform):

| Message | Cause | Fix |
|---|---|---|
| `[!] Stack overflow: <task>` | That task ran out of stack | Increase the stack depth passed to `xTaskCreate()` (in words); the `[STACKS]` list that follows shows every task's free stack |
| `[!] Malloc failed, requested: …` | Heap exhausted | Watch the free heap with `free`, allocate less or enable PSRAM; resolve the `caller` address with `addr2line` |
| `[!] ASSERT <file>:<line>` | A `configASSERT()` failed | Check the condition at that file and line; resolve the `Caller` address with `addr2line` |

## Build analysis { #build-analysis }

When you build with `build_freertos.sh`, the full output goes to `<build dir>/build.log` and only the last 30 lines are printed on failure; add `-v` to see everything. A few lines from the CMake configure step tell you what the build used:

| Message | Meaning |
|---|---|
| `[toolchain] Vendor toolchain detected …` | The toolchain from INTELPRO was found, and the IPRO7 DSP extensions and tuning are enabled; `Standard toolchain detected` means a generic RISC-V GCC |
| `[bluetooth] Using unified Zephyr 4.4 host (ipro_bt_host)` | The BLE host is part of the build |
| `[ipro_ble_controller] Using prebuilt …` | The BLE controller library actually linked; check it against your `CONFIG_IPRO_BLE_CTLR_*` settings |
| `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` | The Reef build added the default crystal trim |
| `AI disabled: OCRAM=240KB (256-16)`, `AI+MM (EM=0): OCRAM=64KB …` | The OCRAM region size for this build: 256 KB minus `CONFIG_EM_SIZE` without AI, shrinking to 64 KB or 48 KB with AI and imaging both on |

At the end of the build the linker prints the usage of each memory region; to track down a region that is too full, see [Size and memory analysis](tools.md#size-analysis).

## On-board testing { #board-testing }

`apps/test/ipro_unit_test` tests the HAL and the shared components, which is useful on a new board or after a port. It is configured for the IPRO7 EVB (`CONFIG_EVB=y`), runs every test automatically at boot (`CONFIG_TEST_AUTO_RUN=y`), and ends with a summary and `ALL TESTS PASSED` or `SOME TESTS FAILED`.

<div class="ipro-steps" markdown>

1. **Build**

    ```bash
    make -C apps/test/ipro_unit_test
    ```

2. **Flash and wait for the result**: on an IPRO7 EVB, one command builds, flashes and evaluates.

    ```bash
    ./build_freertos.sh test ipro_unit_test -p /dev/cu.usbserial-XXXX -t 60
    ```

    Exit code 0 means pass, 1 fail, 2 timeout. `test` flashes without `--chip-variant`; if IntelProCube last flashed an IPRO7AI board, run the tool once with `--chip-variant IPRO7` first.

3. **Re-run selectively**: use these commands on the console (115200 baud).

    | Command | Purpose |
    |---|---|
    | `test_all` | Run every test |
    | `test_list` | List the test suites |
    | `test_run <suite>` | Run one suite |
    | `test_group <sw|hal|crypto|ble>` | Run one group |
    | `test_status` | Show the result summary |

</div>

HAL tests skip themselves when the hardware they need is not detected.

## Troubleshooting { #troubleshooting }

### Build { #troubleshooting-build }

| Symptom | Cause | Fix |
|---|---|---|
| `No cmake found`, or `tools/cmake` fails to execute on macOS | No CMake on the system; the bundled `tools/cmake/` is a Linux x86-64 build | Install CMake 3.19 or later (3.20 or later for Zephyr; for example `brew install cmake`) and put it on `PATH` |
| `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc` not found | The toolchain is not installed, or is somewhere else | Get the toolchain from INTELPRO; for another location, `export CROSS_COMPILE=<path>/bin/riscv64-unknown-elf-` |
| `[ipro_ble_controller] CONFIG_EM_SIZE must match …` | `.config` has no `CONFIG_EM_SIZE` | Add `CONFIG_EM_SIZE` (the shipped applications use 16 or 32) |
| `bt54_iso2 needs at least 32 KB EM` | An LE Audio configuration with 16 KB EM | Set `CONFIG_EM_SIZE=32` |
| `unsupported variant` or `unsupported feature profile` | The controller setting is not one of the provided combinations | Use `link1_periph`, `link1`, `link2` or `link4` for `CONFIG_IPRO_BLE_CTLR_LIB`, and `bt52` or `bt54_iso2` for `CONFIG_IPRO_BLE_CTLR_FEATURE` |
| Configure fails in `ipro_ble_controller` with `ipro_ble_remote/defconfig_lowpower`, or after setting `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`, `CONFIG_IPRO_BLE_CTLR_SUBRATING`, `CONFIG_IPRO_BLE_CTLR_CSSA`, `CONFIG_IPRO_PM_BLE` or `CONFIG_IPRO_PM_PDS_CONNECTED` | These settings switch the BLE controller to a source build, and the package contains only the prebuilt libraries | Remove them; contact INTELPRO if you need these features |
| `CONFIG_EVK_CAMERA needs …`, `CONFIG_EVK_AUDIO needs …`, `CONFIG_EVK_SDCARD needs …` | The EVK board library is missing a dependency | Add the options the message names; see [API Reference](api/ipro7ai-evk.md) |
| Link error `undefined reference to adc_ioctl` | One of the ADC convenience macros such as `adc_channel_start()` was used | Call `hal_adc_ioctl()` instead |
| A feature such as `CONFIG_AI_SUPPORT` is on, but what it depends on is not | The build reads `.config` as written and does not apply Kconfig `select` or `depends on` | Set dependencies explicitly — AI needs `CONFIG_USE_PSRAM=y`, for example; see [Build System & Configuration](../guides/build-system.md) |
| The linker reports a memory region overflow | Code or data does not fit in `flash`, `ocram` or another region | Find the largest users with [Size and memory analysis](tools.md#size-analysis); with AI and imaging both on, OCRAM shrinks to 64 KB or 48 KB |

### Flashing { #troubleshooting-flash }

| Symptom | Cause | Fix |
|---|---|---|
| No `[All Success]`; the output shows `flash jedec id: 00000000` or `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` does not match the board; the tool reuses the last setting it stored | Flash again with `--chip-variant IPRO7AI` for the IPRO7AI Reef EVK and IPRO7AI EVK, or `IPRO7` for the IPRO7 EVB |
| The tool cannot connect to the board | The board is not in download mode, or another program holds the port | Type `reboot_dl` on the console, or use the board's download-mode procedure (Reef: hold SW1 BOOT and press SW2 RESET; see [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)); close any serial monitor |
| `build_freertos.sh flash` reports `Flash tool not found` | The IntelProCube tool is not found | Set `IPRO_FLASH_TOOL`, or add the tool directory to `PATH` |
| `No serial port found` or `Several serial ports` | No USB serial port, or more than one | Pass `-p`, or set `IPRO_SERIAL_PORT` |
| An IPRO7AI EVK AI example shows `NO MFG PARTITION` after boot | The example's partition table was not written (e.g. flashed with `build_freertos.sh flash`, which passes no `--pt`) | Run `PORT=/dev/cu.usbserial-XXXX ./flash.sh --full` in the example's directory to write the partition table, firmware and model in one go |

### Console { #troubleshooting-console }

| Symptom | Cause | Fix |
|---|---|---|
| Garbled characters | Baud rate mismatch | Use the application's `CONFIG_PLATFORM_UART_BAUDRATE` (115200 or 921600); Zephyr uses 2000000 |
| On macOS the program hangs with no output | A `/dev/tty.*` device was opened | Use `/dev/cu.*` |
| `Resource busy`, or `serial_monitor.py` exits with code 3 | Another program holds the port | Close other terminals or monitors; find the holder with `lsof /dev/cu.usbserial-XXXX` |
| `cat` shows only part of the output | `cat` buffers serial input badly on macOS | Use `tools/serial_monitor.py` or another serial terminal |
| No UART output from `ipro_enc28j60_test`, `ipro_gh7007_test`, `ipro_gh7007_video` or `ipro_pio_sdh_test` | These applications run their console over USB CDC | Open the USB serial port the board enumerates |

### Run time and BLE { #troubleshooting-runtime }

| Symptom | Cause | Fix |
|---|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` on the console | CPU exception | Read it as described in [Crash analysis](#crash-analysis) |
| `[!] Stack overflow`, `[!] Malloc failed`, `[!] ASSERT` | Stack or heap exhausted, or an assertion failed | See the table in [Crash analysis](#crash-analysis) |
| `[PSRAM] WARNING: init failed` | The build enables PSRAM, but the PSRAM on the board did not initialize | Check that the board and package have PSRAM; if not, remove `CONFIG_USE_PSRAM` and the features that need it |
| Bonds are gone after a reset and the phone has to pair again | Bond storage is not enabled, or not loaded before advertising | See the [FAQ](faq.md#ble-bonding) |
| BLE throughput far below expectations | Connection parameters, PHY or CPU load | See [BLE Throughput Test](../tutorials/ble-throughput.md) |
| `west flash` cannot enter download mode | The default `--boot probe` needs the IPRO debug probe | Use `west flash -- --boot manual` (by hand) or `--boot shell` (when the running image has a shell) |

## Next steps { #next-steps }

- [Tool Command Lines](tools.md): all options of the build, flash and monitor tools.
- [API Reference](api/index.md): platform, BLE, HAL and logging APIs.
- [FAQ](faq.md): common questions about building, BLE, networking and RTOS.
- [BLE Development](../guides/ble.md) and [Zephyr RTOS](../guides/zephyr.md): guides by feature area.
