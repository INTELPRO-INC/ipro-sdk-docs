---
title: "FAQ"
description: Short answers to common questions about building, flashing and the console, BLE, platform and networking, and debugging, with links to the detailed pages.
migrate_from:
  - "faq.html"
---

# FAQ

Each answer starts with the conclusion and links to the page with the details. For a table of error messages, see [Debugging & Troubleshooting](debugging.md#troubleshooting).

## Building { #build }

### Where do I get the flash tool and the toolchain? { #get-tools }

Neither is included in V2.1.0; contact INTELPRO for:

- the RISC-V toolchain, installed by default in `/opt/toolchain/riscv_ipro7/`;
- the command-line flasher of IntelProCube v0.6.3: `ipro_iot_tool_macos`, `ipro_iot_tool_linux` or `ipro_iot_tool.exe`.

The SDK itself is available from its [GitHub release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0).

### What is the difference between build_freertos.sh and make -C? { #build-cli-vs-make }

`make -C apps/<category>/<app>` builds one application from its `.config` and needs the full path. `build_freertos.sh` wraps `make` and adds the `clean`, `flash`, `monitor`, `size` and `test` actions; it takes just the application name and chains actions:

```bash
make -C apps/platform/ipro7ai_reef_demo
./build_freertos.sh clean build ipro7ai_reef_demo
```

Both produce the same output in `<app>/build/build_out/`. The `flash` and `monitor` actions of `build_freertos.sh` use fixed baud rates and arguments, so flash the Reef and other IPRO7AI boards with the IntelProCube tool directly; see [Flashing & Serial Console](../get-started/flash-and-monitor.md#build-script).

### I changed .config, but a dependent option did not take effect. Why? { #kconfig }

The build reads `.config` as written and generates `autoconf.h` with `cmake/generate_autoconf.cmake`. The Kconfig files are documentation only: `select`, `depends on` and defaults are not applied, so write every dependency into `.config` yourself. For example, with `CONFIG_AI_SUPPORT=y` also set `CONFIG_USE_PSRAM=y`.

The package's Kconfig tree references components that do not ship, so `menuconfig` does not work; edit `.config` directly. See [Build System & Configuration](../guides/build-system.md).

### The toolchain is not found, or it is not in the default path { #toolchain }

Every `.config` points `CONFIG_CROSS_COMPILE` at `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-`. If your toolchain is elsewhere, set `CROSS_COMPILE` in the environment; it overrides `.config`:

```bash
export CROSS_COMPILE=<toolchain path>/bin/riscv64-unknown-elf-
make -C apps/platform/ipro7ai_reef_demo
```

Keep `CONFIG_CPU_ID="intelpro_ipro7"` in `.config`; the build picks its compiler flags from it. `build_freertos.sh size` always uses `size` from the default path, and the Zephyr workspace takes its toolchain directory from `IPRO_TOOLCHAIN`.

### Flash or RAM is too small { #memory }

Start with the memory-region usage the linker prints at the end of the build, then find the largest users with `./build_freertos.sh size <app>` and the `.map` file, as described in [Size and memory analysis](tools.md#size-analysis). OCRAM is 256 KB, and the BLE controller's Exchange Memory (`CONFIG_EM_SIZE`) comes out of it; with both `CONFIG_AI_SUPPORT` and `CONFIG_MM_SUPPORT` set, the OCRAM region shrinks to 64 KB or 48 KB. Disable components you do not need, or move large buffers to PSRAM (`CONFIG_USE_PSRAM=y`).

## Flashing and console { #flash-console }

### Flashing fails. What should I check? { #flashing }

In this order:

1. Is `[All Success]` in the tool output? The tool exits with 0 even when it fails.
2. Does `--chip-variant` match the board? `IPRO7AI` for the IPRO7AI Reef EVK and IPRO7AI EVK, `IPRO7` for the IPRO7 EVB. The tool remembers the last setting, so always pass it when you switch boards.
3. Is the board in download mode? Type `reboot_dl` on the console; on the Reef you can also hold SW1 (BOOT) and press SW2 (RESET).
4. Is a serial monitor holding the port? On macOS, use `/dev/cu.*`.
5. Is the partition table right? The Reef uses `--pt chips/ipro7/partition/partition_cfg_2M.toml`; the IPRO7AI EVK AI examples use their own `flash.sh --full`.

Error messages are listed under [Flashing troubleshooting](debugging.md#troubleshooting-flash); the full procedure is in [Flashing & Serial Console](../get-started/flash-and-monitor.md).

### The console shows garbage or nothing at all { #console }

Garbage usually means a baud rate mismatch. The rate is the application's `CONFIG_PLATFORM_UART_BAUDRATE`, 115200 when unset; `ipro7ai_evk_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_rps`, `ipro7_uvc_cam`, `ipro_epd_el036` and a few others use 921600; Zephyr images use 2000000. `build_freertos.sh monitor` always uses 115200, so for other rates run:

```bash
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0
```

`ipro_enc28j60_test`, `ipro_gh7007_test`, `ipro_gh7007_video` and `ipro_pio_sdh_test` run their console over USB CDC; open the USB serial port the board enumerates.

### What is the difference between /dev/cu.* and /dev/tty.* on macOS? { #macos-serial }

macOS gives each serial device two nodes: `/dev/cu.*` opens immediately, while `/dev/tty.*` waits for the carrier-detect (DCD) signal, so the program hangs. Always use `/dev/cu.*`.

`Resource busy` means another program — a second monitor, an IDE or `stty -f` — holds the port. Find and close it with `lsof /dev/cu.usbserial-XXXX`, and keep only one monitor open at a time.

## BLE { #ble }

### Which BLE controller library should I use? { #ble-variant }

Three `.config` settings select the library: `CONFIG_IPRO_BLE_CTLR_LIB` (`link1_periph` is peripheral and broadcaster only; for the central role or more connections use `link1`, `link2` or `link4`), `CONFIG_IPRO_BLE_CTLR_FEATURE` (`bt54_iso2` adds ISO / LE Audio and needs `CONFIG_EM_SIZE=32`) and `CONFIG_IPRO_BLE_CTLR_CFG_DBG` (not set selects the `_release` library). The full rules and what each shipped application uses are in [BLE Development](../guides/ble.md#controller-variants); start from the `.config` of the closest application.

### Is the BLE controller source available? { #ble-prebuilt }

No. The IPRO BLE controller ships only as prebuilt libraries in `components/wireless/bluetooth/ipro_ble_controller/lib/`: 16 IPRO7 libraries, 4 connection configurations × 2 feature profiles × debug / release.

These settings switch the controller to a source build, which cannot be built from this package: `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`, `CONFIG_IPRO_BLE_CTLR_SUBRATING`, `CONFIG_IPRO_BLE_CTLR_CSSA`, `CONFIG_IPRO_PM_BLE` and `CONFIG_IPRO_PM_PDS_CONNECTED` (`ipro_ble_remote/defconfig_lowpower` sets the last two). Contact INTELPRO if you need another library combination or these features.

### Bonds are lost after a reset { #ble-bonding }

Bond keys are stored through the host's Settings. Use the settings from `ipro_pdm_mic_demo` and `ipro_le_audio_headset`:

```ini title=".config"
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_EASYFLASH4=y
```

In the `bt_enable()` ready callback, call `ipro_ble_ctlr_hcitl_host_ready()` first, then `settings_load_subtree("bt")` before you start advertising, and check its return value. If you advertise first, a bonded phone that connects finds no keys and pairs again. The default `ipro_ble_remote` configuration does not store bonds. If the board has no bond but the phone still keeps the old one, remove the device on the phone and pair again.

### What BLE throughput can I expect? { #ble-throughput }

Measured with `ipro_throughput_test` between two IPRO7AI Reef EVKs (prebuilt `link2` controller, ATT MTU 247, DLE 251 bytes, 244-byte packets, 50 ms connection interval, `CONFIG_IPRO7_BLE_HOTCODE=y`, 8 s one-way flood): about 1.34 Mbps on 2M PHY and 747 kbps on 1M PHY. The numbers apply to that setup only.

For bulk data, use 2M PHY, a 30–50 ms connection interval and 244-byte packets; under these conditions longer intervals are faster, not slower. Steps and full results are in [BLE Throughput Test](../tutorials/ble-throughput.md).

### How do I update firmware over the air? { #ota }

- **FreeRTOS**: build the OTA package with `tools/create_ota.py` from the combined image IntelProCube produces (see [create_ota.py](tools.md#ota-package)). The OTA GATT service (`0xFF60`) of `ipro_ble_remote` is enabled only in its `defconfig_reef` build, together with the A/B partition table `partition_cfg_2M_remote_ab.toml`; OTA on the Reef requires that table.
- **Zephyr**: build MCUboot with sysbuild (`zephyr/samples/mcuboot_app`) and upload images over BLE with MCUmgr SMP (`zephyr/samples/ble_ota`).

The full flow is in [OTA Updates](../guides/ota.md).

## Platform and networking { #platform }

### Does V2.1.0 support IPRO6S? { #ipro6s }

No. V2.1.0 contains IPRO7 applications only; for IPRO6S development use SDK V2.0.1, see [IPRO6S (V2.0.1)](../hardware/chips/ipro6s.md).

### How does IPRO7 connect to a network? { #wifi }

Wi-Fi comes from an IPRO6S companion acting as the radio over SDIO:

- The IPRO7-side component is `components/network/ipronet_host` (lwIP interface `iproeth0`), used by `ipro7_sdio_wifi`, the `defconfig_wifi_ipro6s` build of `ipro7ai_reef_demo` (the IPRO6S FIN card on the Reef, with an RTSP stream) and `ipro_agora_sentino`.
- The IPRO6S-side firmware, including the FIN card's, is not included in V2.1.0; contact INTELPRO.

For wired networking there is the EMAC (RMII) driver (`CONFIG_ETHERNET`), and `ipro_enc28j60_test` for an ENC28J60 over SPI.

See [Networking](../guides/networking.md).

### Which RTOSes does the SDK support? Is the BLE host Zephyr? { #rtos }

All 35 applications use FreeRTOS (kernel V11.1.0). The BLE host comes from Zephyr v4.4.0 and runs on FreeRTOS through the SDK's port layer: applications use Zephyr's `bt_*` APIs, but no Zephyr installation is needed.

The SDK is also a Zephyr v4.4.0 module for `ipro7_evb` and `ipro7ai_evk`. Zephyr in this release has no low-power modes and no display, camera, audio codec, USB, SD host, Ethernet or NPU drivers — use FreeRTOS for those — and no board definition for the IPRO7AI Reef EVK. See [Zephyr RTOS](../guides/zephyr.md).

### Can I use Thread or Matter? { #thread-matter }

Thread is available under Zephyr only: Zephyr's IEEE 802.15.4 driver with OpenThread, built from Zephyr's `samples/net/openthread/shell` with the SDK's `zephyr/samples/ieee802154_shell/ot.conf` and `app.overlay`. FreeRTOS applications do not include Thread, and this release does not include Matter. See [Thread & Matter](../guides/thread-matter.md).

### How do I trim the crystal frequency offset (CFO)? { #xtal-capcode }

Set `CONFIG_IPRO7_XTAL_CAPCODE=<1–255>` in `.config`. `board_init()` applies it at boot and prints `[XTAL] capcode <boot value> -> <setting>`, and every RF init loads it again. With 0, the boot value stays until the first RF init loads the ROM default of 85. The IPRO7AI Reef EVK uses 95 when the config does not set a value.

A higher value lowers the frequency: increase it when the frequency is high (positive offset), decrease it when low. This is a board-level value; production units still need a per-unit trim. Under Zephyr the option is `CONFIG_SOC_IPRO7_XTAL_CAPCODE`; set it to 95 on the Reef. From code you can also call `AON_Set_Xtal_CapCode()` and `AON_Get_Xtal_CapCode()` (`bsp/drivers/ipro7_soc/std_drv/inc/drv_aon.h`).

## Debugging { #debug }

### How do I enable debug logs? { #debug-log }

Set the integer level in `.config` and rebuild:

```ini title=".config"
CONFIG_IPRO_LOG_ENABLE=y
CONFIG_LOG_DEFAULT_LEVEL=4    # 1 error, 2 warning, 3 info, 4 debug, 5 verbose
```

The code reads the integer `CONFIG_LOG_DEFAULT_LEVEL`; changing only an option such as `CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y` has no effect, and `CONFIG_BT_DEBUG` does not turn on host logs. At run time, use `ipro_log_set_level()`; see [API Reference](api.md#log-api).

### How do I analyze a crash or a stack overflow? { #crash }

On a CPU exception the firmware prints `MCAUSE`, `MEPC`, the faulting task and a backtrace; run the toolchain's `addr2line` against the `.elf` from the same build to get source lines. A stack overflow prints `[!] Stack overflow: <task>`; increase the stack depth passed to `xTaskCreate()` (in words). See [Crash analysis](debugging.md#crash-analysis).
