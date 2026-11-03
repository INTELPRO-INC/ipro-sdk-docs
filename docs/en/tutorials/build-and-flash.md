---
title: "Build and Flash Workflow"
description: The edit, build, flash and monitor loop on the IPRO7AI Reef EVK — one build_freertos.sh line per iteration, alternate configurations, clean builds and reading memory usage.
migrate_from:
  - "tutorials.html — Tutorial 2"
---

# Build and Flash Workflow

Day-to-day development is a loop: edit, build, flash, watch the console. In this tutorial you change the boot banner of the out-of-box firmware `ipro7ai_reef_demo` on the IPRO7AI Reef EVK, build, flash and monitor with one `build_freertos.sh` line, and see your text on the console; then you switch configurations, clean-build and read memory usage. For first-time installation and flashing, complete [First FreeRTOS Application](../get-started/first-app-freertos.md) first.

## Prerequisites { #prerequisites }

- [First FreeRTOS Application](../get-started/first-app-freertos.md) is done: the board runs `ipro7ai_reef_demo` and its console answers `reef selftest`.
- macOS or Linux. `build_freertos.sh` needs bash; on Windows, build with the VS Code Extension and flash as in [Windows Setup & VS Code](../get-started/windows.md#flash) — the loop is the same.
- Run every command from the SDK root; examples use macOS.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Set the environment** once in this terminal window; every later command uses it.

    ```bash
    export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
    export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
    export IPRO_FLASH_PT=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
    ```

    On Linux use `ipro_iot_tool_linux` and `/dev/ttyUSB0`. `IPRO_FLASH_PT` applies to every `flash` in this window; when you move to an application with its own partition table, clear it with `unset IPRO_FLASH_PT` or override it with `-P`.

2. **Edit the code:** open `apps/platform/ipro7ai_reef_demo/main.c` and append your own text to the boot banner in `main()`:

    ```c title="apps/platform/ipro7ai_reef_demo/main.c"
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **Build, flash and monitor:** close any terminal program that holds the port, then run:

    ```bash
    ./build_freertos.sh -t 15 build flash monitor ipro7ai_reef_demo
    ```

    The running firmware receives `reboot_dl` and enters download mode by itself, so no buttons are needed. The output, in order (excerpt):

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    → Building ipro7ai_reef_demo...
    ✓ Build succeeded (14s)
      Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
      Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
    → Entering download mode...
    reboot to download mode
    → Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
    [...] - Chip name is ipro7
    ...
    [...] - [All Success]
    ✓ Flash succeeded (…)
    → Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
    [serial_monitor] Sent: reboot
    ...
    I (…) REEF:   IPRO7AI Reef carrier demo - my build
    ...
    [serial_monitor] TIMEOUT after 15s
    ✗ Action 'monitor' failed — stopping.

    Summary:
      ✓ build
      ✓ flash
      ✗ monitor (exit 2)
    ```

    `monitor` reads for the `-t` seconds and ends with exit code 2, which the script lists as a failure. That is expected: once `build` and `flash` show ✓, the new firmware runs on the board.

4. **Try it interactively:** open the console in a terminal program (for example `screen /dev/cu.usbserial-XXXX 115200`) and type `reef status` or `led 0 40 0` to check that the new firmware answers. Close the terminal before the next flash.

5. **Repeat:** after each change, run step 3 again. To check only that the code compiles, run `build` alone:

    ```bash
    ./build_freertos.sh build ipro7ai_reef_demo
    ```

</div>

## Verify { #verify }

- `Summary` shows ✓ for `build` and `flash`.
- The boot messages on the console include `IPRO7AI Reef carrier demo - my build`.
- SW3, SW4 and SW5 still light the LED red, green and blue, and `reef selftest` prints the same as before the change.

## build_freertos.sh actions and options { #actions }

This tutorial uses `build`, `flash` and `monitor`, with `-t` (monitor time), `-d` (alternate configuration) and `-P` (partition table). Actions run in order and stop at the first failure. The other actions (`clean`, `size`, `test`) and every option and environment variable: [macOS / Linux Command Line](../get-started/command-line.md#build-script).

## Alternate configurations and build directories { #variants }

One application can have several configuration files. Choose an alternate one with `-d`; it builds in `build_<name>/` and leaves the application's `.config` untouched:

```bash
./build_freertos.sh -d defconfig_wifi_ipro6s build ipro7ai_reef_demo        # builds in build_wifi_ipro6s/
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam       # USB webcam
```

- `flash` and `size` use `-d` to find the image: when you run them separately, give each the same `-d`.
- The build copies the configuration to `build_<name>/.config`; edit the original in the application directory.
- After flashing `ipro7_uvc_cam` with `defconfig_reef_ov5640` and fitting an OV5640, a USB camera (`3896:0701`) appears on the Reef's USB-C; any camera application on the computer shows the picture.
- Every Reef configuration and its build command: [Reef build configurations](../get-started/command-line.md#reef-configs). For applications that need boot2 or `mfg` data on the first flash, see [Flashing & Serial Console](../get-started/flash-and-monitor.md#partition-tables).

## Clean build { #clean-build }

After changing `.config` or an alternate configuration — particularly flash size, PSRAM, AI or BLE controller options — clean before building. `clean` removes only the matching build directory:

```bash
./build_freertos.sh clean build ipro7ai_reef_demo                            # remove and rebuild build/
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo   # remove and rebuild build_wifi_ipro6s/
```

`clean` prints `✓ Clean complete` when done.

## Reading memory usage { #memory-usage }

The link step prints how much of each memory region is used. With `make` it appears in the terminal; with `build_freertos.sh` it goes to `build.log`:

```bash
grep -A5 "Memory region" apps/platform/ipro7ai_reef_demo/build/build.log
```

For `ipro7ai_reef_demo` with its default configuration:

```text
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
```

- `flash` is the flash limit used for linking. `ipro7ai_reef_demo` links a 1 MB layout by default (the configure stage prints `-- IPRO7 flash: 1M (default, on-chip)`); if the Reef's in-package flash reports JEDEC `0xEF4015` (2 MB), add `CONFIG_IPRO7_FLASH_2M=y` to `.config` to use all of it.
- A `flash` percentage under 100 does not mean the image fits the firmware partition: compare the `.bin` size shown after `Binary:` with the firmware partition of the table you flash with. In `partition_cfg_2M.toml` it is 1180 KB.
- `ocram` is the on-chip OCRAM. With AI off, the region is 256 KB minus the `CONFIG_EM_SIZE` used by BLE, and the configure stage prints a line such as `-- AI disabled: OCRAM=256KB`; with AI on the layout differs. Which settings size each region: [Build System & Configuration](../guides/build-system.md).

The `size` action lists the total and per-section sizes of the `.elf`:

```bash
./build_freertos.sh size ipro7ai_reef_demo
```

```text
→ Size report for ipro7ai_reef_demo_IPRO7.elf

   text    data     bss     dec     hex filename
 235928   14008   49588  299524   49204 <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf
...
```

The numbers come from a V2.2.0 build and change with the toolchain version and your edits.

## What the script fills in { #script-defaults }

`build_freertos.sh` reads its flashing parameters from the application's configuration, so the Reef needs nothing extra:

| Parameter | Source |
|---|---|
| `--chip-variant` | `IPRO7AI` when the configuration has `CONFIG_IPRO7AI_REEF=y`; override with `-c` or `IPRO_CHIP_VARIANT` |
| `--pt` | `-P` or `IPRO_FLASH_PT`; with neither, no `--pt` and the tool uses its own default table |
| Baud rate of `reboot_dl` and `monitor` | `CONFIG_PLATFORM_UART_BAUDRATE` from the configuration, 115200 when unset (921600 for the Reef configuration of `ipro7_jpeg_decode`) |
| Flashing baud rate | always 921600 |

The script cannot pass boot2 or `mfg` data, and `--chipname` is fixed to `ipro7`; in those cases run IntelProCube directly, see [Flashing & Serial Console](../get-started/flash-and-monitor.md#build-script).

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `✗ Build failed` with compiler errors in the last 30 lines | an error in the code | fix it from the messages; the full log is `build.log` |
| `✗ Flash failed`; the tool stops at the handshake | the firmware did not act on `reboot_dl` (no shell, hung, or another baud rate), or a terminal program holds the port | close the terminal; hold SW1, press SW2, release SW1, then run `flash` alone |
| `✗ Flash tool not found: …` | a new terminal window without `IPRO_FLASH_TOOL` | redo step 1, or add the `export` lines to your shell start-up file |
| `✗ Binary not found: …` | no build before `flash`, or `-d` missing | add `build`, or the `-d` used for the build |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | `IPRO_SERIAL_PORT` not set and several ports present | set `IPRO_SERIAL_PORT` or add `-p` |
| The console does not show your text | flashing failed, or you are reading old output | check that `flash` shows ✓ in `Summary`; run step 3 again |
| A `.config` change has no effect | old build results remain | run `clean build` |
| Another application fails to flash or boot | `IPRO_FLASH_PT` still points at the previous application's table | `unset IPRO_FLASH_PT` and give the right table with `-P`, see [Partition tables](../get-started/flash-and-monitor.md#partition-tables) |

## Next steps { #next-steps }

- [Create Your First Application](first-own-app.md): start an application of your own.
- [Test Your Application](testing.md): check your application's output automatically.
- [macOS / Linux Command Line](../get-started/command-line.md): every action, option and limit of `build_freertos.sh`.
- [Build System & Configuration](../guides/build-system.md): `.config` keys, linker scripts and memory layout.
