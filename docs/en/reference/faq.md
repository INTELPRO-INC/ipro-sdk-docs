---
title: "FAQ"
description: Short answers to common questions on building, flashing and the console, BLE, platform and networking, and debugging, for the IPRO7AI Reef EVK, with links to the detailed pages.
migrate_from:
  - "faq.html"
---

# FAQ

Each answer starts with the conclusion; where you need to act, it gives the command and what you should see, and links to the page with the details. Examples use the IPRO7AI Reef EVK V4.0. For a table of error messages, see [Debugging & Troubleshooting](debugging.md#troubleshooting).

## Building { #build }

### Where do I get the SDK, the flash tool and the toolchain? { #get-tools }

- **SDK V2.2.0**: download `IPRO-SDK-V2.2.0.tar.gz` from the [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0), check it against the SHA-256 on that page and unpack it:

    ```bash
    shasum -a 256 IPRO-SDK-V2.2.0.tar.gz      # Linux: sha256sum; must match the release page
    tar xzf IPRO-SDK-V2.2.0.tar.gz
    cat IPRO-SDK-V2.2.0/VERSION.txt
    ```

    `VERSION.txt` prints `IPRO7: IPRO-SDK-V2.2.0`, `IPRO6: IPRO-SDK-V2.2.0` and `Release Date: 2026-11-03`.
- **The RISC-V toolchain** and **the IntelProCube v0.6.3 command-line flash tool** (`ipro_iot_tool_macos`, `ipro_iot_tool_linux`, `ipro_iot_tool.exe`): not included in V2.2.0; contact INTELPRO. The toolchain installs to `/opt/toolchain/riscv_ipro7/` by default.
- **Windows online installer 3.6.0 and VS Code extension 3.3.0**: current; download the installer from [ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest). It installs SDK V2.2.0 and the Windows toolchain directly; see [Windows Setup & VS Code](../get-started/windows.md).
- **IPRO AI Studio**: not in the SDK; download it from [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest).

### What is the difference between build_freertos.sh and make -C? { #build-cli-vs-make }

`make -C apps/<category>/<app>` builds one application and needs the full path. `build_freertos.sh` adds `clean`, `flash`, `monitor`, `size` and `test`, takes just the application name and chains actions:

```bash
make -C apps/platform/ipro7ai_reef_demo
./build_freertos.sh clean build ipro7ai_reef_demo
```

Both produce the same output in `<app>/build/build_out/`. `build_freertos.sh flash` picks `--chip-variant IPRO7AI` for Reef configurations by itself and takes a partition table with `-P`; `monitor` opens the console at the application's own baud rate. It cannot pass `--boot2` or `--mfg` and cannot flash IPRO6S; use the IntelProCube tool directly for those. See [Tool Command Lines](tools.md#build-cli).

### Which applications run on the Reef, and which configuration do I pick? { #reef-apps }

Nine of the 40 applications have a Reef configuration. Only `ipro7ai_reef_demo`, `ipro_reef_teach` and `ipro_agora_sentino` build for the Reef with a plain `make`; for the others, `.config` targets the IPRO7 EVB or the IPRO7AI EVK, and you select the Reef configuration with `DEFCONFIG=`:

| Application | Build command (from the SDK root) |
|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` |
| `ipro7ai_reef_demo` (Wi-Fi and RTSP) | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` |
| `ipro7_uvc_cam` (webcam) | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` |
| `ipro7_uvc_cam` (rock-paper-scissors) | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` (console 921600) |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` |

`DEFCONFIG=defconfig_<name>` builds into `build_<name>/build_out/` (for example `build_reef/build_out/` for `defconfig_reef`) and leaves `.config` alone. To check whether a configuration file is for the Reef:

```bash
grep CONFIG_IPRO7AI_REEF apps/bluetooth/ble/ipro_ble_remote/defconfig_reef
```

It prints `CONFIG_IPRO7AI_REEF=y` for a Reef configuration. The partition table, `--boot2`, `--mfg` and USB identity of each application are on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples); the boards the other applications need are in [Examples](../examples/index.md).

### I changed .config, but a dependent option did not take effect. Why? { #kconfig }

The build reads `.config` as written and generates `autoconf.h` from it with `cmake/generate_autoconf.cmake`. The Kconfig files only document the options: `select`, `depends on` and defaults are not applied, so you write the dependent options into `.config` yourself. For example, `CONFIG_AI_SUPPORT=y` also needs `CONFIG_USE_PSRAM=y`. The one exception is the Reef crystal trim: when the configuration does not set `CONFIG_IPRO7_XTAL_CAPCODE`, the build adds 95.

`make menuconfig` needs `tools/kconfig/menuconfig.py`, and `make defconfig` needs a `configs/` directory; neither ships. Edit `.config` directly, or save a copy as `defconfig_<name>` and build it with `DEFCONFIG=`. See [Build System & Configuration](../guides/build-system.md).

### The toolchain is not found, or it is not in the default path { #toolchain }

The toolchain prefix comes from, in order: `CROSS_COMPILE` in the environment or on the command line, `CONFIG_CROSS_COMPILE` in the configuration file, and the default in `project.build`, `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-` (there is no default on Windows). 30 of the 40 `.config` files set `CONFIG_CROSS_COMPILE`. With the toolchain elsewhere:

```bash
export CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-
make -C apps/platform/ipro7ai_reef_demo
```

`[toolchain] Vendor toolchain detected …` at configure time means the INTELPRO toolchain was found. Keep `CONFIG_CPU_ID="intelpro_ipro7"` in `.config`. `build_freertos.sh size` always uses the `size` at the default path.

### Can I build on Windows? { #windows }

The command-line flow in the package targets macOS and Linux: `build_freertos.sh` is a bash script and `tools/serial_monitor.py` uses termios, so neither runs on Windows. `project.build` has a Windows branch, with these conditions:

- Pass `CROSS_COMPILE` on every build, because Windows has no default toolchain path and the `CONFIG_CROSS_COMPILE` in `.config` is a Unix path: `make -C apps/platform/ipro7ai_reef_demo CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-`.
- `cmake` and `python` (not `python3`) must be on `PATH`; the bundled `tools/cmake/` is Linux only.
- Flash with `ipro_iot_tool.exe` and a port such as `COM5`; open the console with any Windows serial terminal.

The package does not say which shell or `make` to use on Windows. For the Windows installer and the VS Code extension, see [Windows Setup & VS Code](../get-started/windows.md).

### Flash or RAM is too small { #memory }

Start with the memory region use the linker prints at the end of the build, then find the largest users with `./build_freertos.sh size <app>` and the `.map` file; see [Size and memory analysis](tools.md#size-analysis). OCRAM is 256 KB, and the BLE controller's Exchange Memory (`CONFIG_EM_SIZE`) comes out of it; with both `CONFIG_AI_SUPPORT` and `CONFIG_MM_SUPPORT`, the OCRAM region shrinks to 64 KB or 48 KB. Turn off components you do not need, or move large buffers to PSRAM (`CONFIG_USE_PSRAM=y`). Flash links with a 1 MB layout by default; `CONFIG_IPRO7_FLASH_2M=y` selects the 2 MB layout. What each Reef configuration uses is on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#bsp).

## Flashing and console { #flash-console }

### Flashing fails. What should I check? { #flashing }

Check, in order:

1. **The verdict line**: is `[All Success]` in the tool's output? The tool exits 0 even when it fails.
2. **Chip setting**: use `--chip-variant IPRO7AI` on the Reef. The tool remembers the last setting, so always pass it again when you switch boards. `flash jedec id: 00000000` or `IPRO FLASH MATCH TYPE FAIL` in the output means this is the problem.
3. **Download mode**: hold SW1 (BOOT), press and release SW2 (RESET), release SW1; the console should stay silent. Or type `reboot_dl` at the console; it prints `reboot to download mode`. Other methods are in [Enter download mode](debugging.md#download-mode).
4. **Serial port**: close other monitors; use `/dev/cu.*` on macOS; on the IPRO Debug Probe use the port whose name ends in `02`.
5. **Partition table**: `ipro7ai_reef_demo` and `ipro7_uvc_cam` use `--pt chips/ipro7/partition/partition_cfg_2M.toml`; the OTA build of `ipro_ble_remote` needs `--boot2` and `partition_cfg_2M_remote_ab.toml` the first time; `ipro_reef_teach` uses its own `partition_reef_teach.toml` with `--skip-ota` and `--mfg`. Each application is listed on [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples).

After flashing, press SW2 to reset; the application's boot messages on the console mean it worked. The full steps are in [Flashing & Serial Console](../get-started/flash-and-monitor.md).

### The console shows garbage or nothing at all { #console }

Garbage is usually a baud-rate mismatch. The rate is `CONFIG_PLATFORM_UART_BAUDRATE` in the configuration file, 115200 when unset; every Reef configuration uses 115200 except `defconfig_reef` of `ipro7_jpeg_decode`, which uses 921600. `build_freertos.sh monitor` uses the application's rate by itself; when you open the port yourself, pass `--baud`:

```bash
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0
```

No output at all: the board may still be in download mode (press SW2), TX / RX on U6 may be swapped (U6 pin 3 is the Reef's TX), or you opened the probe's `04` port. `serial_monitor.py` only reads and sends one command; to type commands line by line, use `screen /dev/cu.usbserial-XXXX 115200` or another serial terminal.

### What is the difference between /dev/cu.* and /dev/tty.* on macOS? { #macos-serial }

macOS creates two nodes for the same serial device: `/dev/cu.*` opens immediately; `/dev/tty.*` waits for the carrier detect (DCD) signal, so programs hang. Always use `/dev/cu.*`.

`Resource busy` means another program (another monitor, an IDE or `stty -f`) holds the port. Find and close it with `lsof /dev/cu.usbserial-XXXX`, and keep only one monitor open at a time.

## BLE { #ble }

### Which BLE controller library should I use? { #ble-variant }

Three `.config` settings select the library: `CONFIG_IPRO_BLE_CTLR_LIB` (`link1_periph` is peripheral and broadcaster only; use `link1`, `link2` or `link4` for a central or several links), `CONFIG_IPRO_BLE_CTLR_FEATURE` (`bt54_iso2` adds ISO / LE Audio and needs `CONFIG_EM_SIZE=32`) and `CONFIG_IPRO_BLE_CTLR_CFG_DBG` (unset selects the `_release` library). `CONFIG_BT_CONN` must not exceed the library's link count. At configure time CMake prints `[ipro_ble_controller] Using prebuilt <file>`, the library actually linked. The full rules are in [BLE Development](../guides/ble.md); start from the closest Reef configuration (for example `ipro_ble_remote/defconfig_reef`).

### Is the BLE controller source available? { #ble-prebuilt }

No. The IPRO BLE controller ships only as prebuilt libraries in `components/wireless/bluetooth/ipro_ble_controller/lib/`: 16 IPRO7 libraries, 4 link configurations × 2 feature profiles × debug / release. This release has no IPRO6S BLE controller library; the IPRO6S applications are Wi-Fi only.

These settings build the controller from source and cannot be built from this package: `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`, `CONFIG_IPRO_BLE_CTLR_SUBRATING`, `CONFIG_IPRO_BLE_CTLR_CSSA`, `CONFIG_IPRO_PM_BLE`, `CONFIG_IPRO_PM_PDS_CONNECTED`. Contact INTELPRO if you need another library combination or these features.

### Bonds are lost after a reset { #ble-bonding }

The host's Settings store the bond keys. Use `defconfig_reef` of `ipro_le_audio_headset` as the reference:

```ini title=".config"
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_EASYFLASH4=y
```

In the `bt_enable()` ready callback, call `ipro_ble_ctlr_hcitl_host_ready()` first, then `settings_load_subtree("bt")` before you start advertising, and check its return value; if you advertise first, a bonded phone that connects finds no keys and pairs again. The `ipro_ble_remote` configurations do not store bonds. If the board has lost its bonds but the phone still has the old one, remove the device in the phone's Bluetooth settings and pair again.

### What BLE throughput can I expect? { #ble-throughput }

Measured with `ipro_throughput_test` between two IPRO7AI Reef EVKs (prebuilt `link2` controller, ATT MTU 247, DLE 251 bytes, 244-byte packets, 50 ms connection interval, `CONFIG_IPRO7_BLE_HOTCODE=y`, one direction for 8 seconds): about 1.34 Mbps on the 2M PHY and about 747 kbps on the 1M PHY. The numbers belong to that setup, not to every situation.

For bulk data, use the 2M PHY, a 30–50 ms connection interval and 244-byte packets. Steps and full results are in [BLE Throughput Test](../tutorials/ble-throughput.md).

### How do I update firmware over the air? { #ota }

On the Reef, `defconfig_reef` of `ipro_ble_remote` provides BLE OTA (GATT service `0xFF60`); it needs boot2 and the A/B partition table `partition_cfg_2M_remote_ab.toml`:

1. Flash the first time with `--boot2` and `--pt …/partition_cfg_2M_remote_ab.toml`; the boot messages start with `[BOOT2] IPRO7 Boot2 v0.5.2`.
2. Build `build_reef/build_out/ipro_ble_remote_reef.xz.ota` with `make_reef_ota.sh`.
3. Send the package with `reef_ota.py` or the Android demo app `ipro_remote_demo.apk`; after the reboot the board runs the new firmware.

Never run OTA on a Reef flashed with the standard `partition_cfg_2M.toml`: the board goes completely silent and has to be reflashed from download mode. The commands are in [Reef OTA tools](tools.md#reef-ota-tools); the complete flow is in [OTA Updates](../guides/ota.md).

## Platform and networking { #platform }

### Does V2.2.0 support IPRO6S? { #ipro6s }

Yes, for Wi-Fi. V2.2.0 ships three IPRO6S applications: `ipro6_demo` (Wi-Fi 6 station / soft-AP), `ipro6_if_wifi` (Wi-Fi bridge to a host over SDIO or USB) and `ipro6_fmac` (FullMAC firmware for a Linux host). This release has no IPRO6S BLE controller library and no BLE or BR/EDR application for IPRO6S.

On the Reef, the IPRO6S is the FIN Wi-Fi card in the microSD slot, and its firmware is the SDIO configuration of `ipro6_if_wifi`:

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

The output is `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`. IPRO6S images are flashed with IntelProCube's `--chipname ipro6`; `build_freertos.sh flash` does not apply. The supported configurations and flashing are on [IPRO6S](../hardware/chips/ipro6s.md).

### How does IPRO7 connect to a network? { #wifi }

IPRO7 connects to Wi-Fi through an external radio, on the Reef the IPRO6S FIN card over SDIO:

- **IPRO6S (SDIO)**: the IPRO7 component `components/network/ipronet_host`, with the lwIP network interface `iproeth0`. On the Reef this is the FIN card: `defconfig_wifi_ipro6s` of `ipro7ai_reef_demo` (with an RTSP camera stream) and `ipro_agora_sentino`. Steps are in [Wi-Fi and RTSP streaming](../tutorials/wifi-rtsp.md).
- **Others**: components for ATBM6162 (SDIO), AIC8800 (SDIO) and ESP32 (UART AT commands) are also in the package.
- **Wired**: the EMAC (RMII) driver (`CONFIG_ETHERNET`).

See [Networking](../guides/networking.md).

### Which RTOSes does the SDK support? Is the BLE host Zephyr? { #rtos }

All 40 applications are FreeRTOS (kernel V11.1.0): 37 for IPRO7 and 3 for IPRO6S. The BLE host is Zephyr v4.4.0's, running on FreeRTOS through the SDK's port layer; applications use Zephyr's `bt_*` API without installing Zephyr.

The SDK is also a Zephyr v4.4.0 module with the boards `ipro7_evb` and `ipro7ai_evk`, and no Reef board; the SoC's Kconfig help notes that a Reef running `ipro7_evb` images needs `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`. See [Zephyr RTOS](../guides/zephyr.md).

### Can I use Thread or Matter? { #thread-matter }

Thread is available under Zephyr only: Zephyr's IEEE 802.15.4 driver plus OpenThread, built from Zephyr's `samples/net/openthread/shell` with the SDK's `zephyr/samples/ieee802154_shell/ot.conf` and `app.overlay`. FreeRTOS applications have no Thread, and this release has no Matter. See [Thread & Matter](../guides/thread-matter.md).

### How do I trim the crystal frequency offset (CFO)? { #xtal-capcode }

Set `CONFIG_IPRO7_XTAL_CAPCODE=<1–255>` in `.config`. At boot `board_init()` applies it and prints `[XTAL] capcode <boot value> -> <set value>`, and every RF initialization reloads it. With 0 the boot value stays until the first RF initialization loads the ROM default 85. The Reef uses 95 when it is not set, and CMake prints `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` at configure time.

A higher value lowers the frequency: raise it when the frequency is high (positive offset), lower it when it is low. This is a per-board value; production still calibrates each unit. Code can also call `AON_Set_Xtal_CapCode()` and `AON_Get_Xtal_CapCode()` (`bsp/drivers/ipro7_soc/std_drv/inc/drv_aon.h`).

## Debugging { #debug }

### How do I enable debug logs? { #debug-log }

Set the integer level in `.config` and rebuild:

```ini title=".config"
CONFIG_IPRO_LOG_ENABLE=y
CONFIG_LOG_DEFAULT_LEVEL=4    # 1 error, 2 warning, 3 info, 4 debug, 5 verbose
```

The code reads the integer `CONFIG_LOG_DEFAULT_LEVEL`; setting options such as `CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y` has no effect, and `CONFIG_BT_DEBUG` does not turn on host logs. Change the level at run time with `ipro_log_set_level()`; see [API Reference](api/index.md#log-api).

### How do I analyze a crash or a stack overflow? { #crash }

On a CPU exception the firmware prints `MCAUSE`, `MEPC`, the faulting task and a backtrace; run the toolchain's `addr2line` against the `.elf` of the same build to get the function and source line. A stack overflow prints `[!] Stack overflow: <task>`; increase the stack depth in `xTaskCreate()` (in words). After a crash, `ipro7ai_reef_demo` and `ipro_reef_teach` keep printing `==DUMP_READY:2000000==` while they wait for a host tool that does not ship: save the diagnostics and press SW2 to reset. This release has no setup for an on-target debugger (JTAG / GDB). See [Crash analysis](debugging.md#crash-analysis).
