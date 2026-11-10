---
title: "IPRO6S"
description: IPRO6S specifications, the three Wi-Fi 6 applications in V2.2.0 and their configurations, building and flashing, and its role as the FIN Wi-Fi card on the IPRO7AI Reef EVK
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S

IPRO6S is a RISC-V SoC with built-in Wi-Fi 6. It builds from the same SDK tree and with the same toolchain as IPRO7. V2.2.0 ships three IPRO6S Wi-Fi applications: `ipro6_demo` for stand-alone networking, `ipro6_if_wifi` to bridge Wi-Fi to a host processor over SDIO or USB, and `ipro6_fmac`, FullMAC firmware for a Linux host. On the IPRO7AI Reef EVK the IPRO6S is the FIN Wi-Fi card in the microSD slot, which gives the IPRO7AI its network connection over SDIO.

<div class="ipro-facts" markdown>
<div><strong>Wi-Fi 6</strong><span>on the chip</span></div>
<div><strong>RV32IMAFC</strong><span>same toolchain as IPRO7</span></div>
<div><strong>3</strong><span>IPRO6S applications</span></div>
<div><strong>ipro6</strong><span><code>--chipname</code> when flashing</span></div>
</div>

## Chip specifications { #ipro6s }

| Item | IPRO6S |
|---|---|
| Core | RISC-V RV32IMAFC with DSP extensions |
| Wireless | Built-in Wi-Fi 6 |
| NPU / ISP | None |
| RTOS | FreeRTOS V11 |
| Reference boards | IPRO6S EVK (contact INTELPRO); the FIN card on the Reef |

| Region | Size | Base address | Notes |
|---|---|---|---|
| Flash | 2 MB | `0x13000000` | |
| TCM RAM | 320 KB | `0x11000000` | Code and data; 280 KB in the reduced layout |
| Wi-Fi RAM | 160 KB | `0x21050000` | |
| HBN RAM | 4 KB | `0x20090000` | |

IPRO6S applications select the chip with these settings; their images carry the chip suffix `IPRO6`:

```ini title="apps/platform/ipro6_if_wifi/defconfig_ipro6_sdio (excerpt)"
CONFIG_IPRO6=y
CONFIG_CHIP="IPRO6"
CONFIG_CPU_ID="intelpro_ipro7"     # same toolchain as IPRO7
CONFIG_FREERTOS_SUPPORT=y
```

## SDK support in this release { #status }

| Item | V2.2.0 |
|---|---|
| Applications | `ipro6_demo`, `ipro6_if_wifi`, `ipro6_fmac` (`apps/platform/`) |
| Wi-Fi 6 | MAC (`components/wireless/macsw`), fhost API, wpa_supplicant and lwIP adapter (`components/wireless/wifi6`), RF driver (`components/wireless/rf/ipro6_rf`); all prebuilt per application configuration |
| Low power | The DTIM low-power firmware image `bsp/hal/lp_framework/ipro6/prebuilt/ipro6_lpfw.bin`, embedded by the low-power configurations |
| Bluetooth | The IPRO6S Bluetooth controller libraries and dual-mode (BR/EDR) applications are not included in V2.2.0; contact INTELPRO. The IPRO6S applications in this release use Wi-Fi only |
| Zephyr RTOS | The `ipro6s_evb` board files are included, but IPRO6S is not supported under Zephyr in this release |
| Flashing | [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 or later, command-line tool, with `--chipname ipro6`; the `flash` action of `build_freertos.sh` handles IPRO7 only |

## Applications and configurations { #apps }

Each IPRO6S application picks its configuration with `DEFCONFIG=`. The table lists the build-verified configurations; an application's `.config` is a copy of its first configuration.

| Application | Configuration | What it does |
|---|---|---|
| `ipro6_demo` | `defconfig_ipro6_lpwifi` | Wi-Fi 6 station and soft-AP, lwIP, shell, plus DTIM power save |
| | `defconfig_ipro6_lp` | Low-power demo without Wi-Fi |
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 6 bridge: the host processor sees an Ethernet-like interface over SDIO; the firmware of the Reef's FIN card |
| | `defconfig_ipro6_usb` | The same over USB |
| | `defconfig_ipro6_lp` | Low-power demo without Wi-Fi |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | FullMAC firmware for a Linux cfg80211 host (image `ipro6s_fmac.img`); the default of `make` |
| | `defconfig_ipro6_fmac_loader` | The flash loader that receives the FullMAC firmware over SDIO or USB |

- `ipro6_demo/defconfig_ipro6_lpwifi_ping` and `ipro6_fmac/defconfig_ipro6_fmac_ap` set no `CONFIG_WIRELESS_LIB_VARIANT` and are not among the verified configurations; contact INTELPRO before using them.
- The Linux host driver for `ipro6_fmac` is not included in V2.2.0.
- The three applications target the IPRO6S EVK (`CONFIG_BOARD="EVB"`); on the Reef, only `defconfig_ipro6_sdio` of `ipro6_if_wifi` runs, on the FIN card.

## Build { #build }

Run from the SDK root; the FIN card firmware as an example:

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

At the end of the build the linker prints flash and RAM usage, and the image is `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`. The output directory is `build_` plus the configuration name without `defconfig_`. The Makefile of `ipro6_fmac` passes `DEFCONFIG=defconfig_ipro6_fmac` by default, so a plain `make` there also builds into `build_ipro6_fmac/`. `build_freertos.sh -d defconfig_ipro6_sdio build ipro6_if_wifi` builds as well, but it cannot flash an IPRO6S.

### Wi-Fi libraries and custom configurations { #wifi-libs }

The Wi-Fi MAC, fhost, wpa_supplicant, lwIP adapter and RF driver are prebuilt once per application configuration, in each component's `lib/<app>-<config>/`, and selected by the configuration's `CONFIG_WIRELESS_LIB_VARIANT`. For `defconfig_ipro6_sdio`:

```ini
CONFIG_WIFI6=y
CONFIG_USE_MACSW=y
CONFIG_WIRELESS_LIB_VARIANT="ipro6_if_wifi-ipro6_sdio"
```

For a custom configuration, keep the Wi-Fi options of one of the configurations above and its `CONFIG_WIRELESS_LIB_VARIANT`; the prebuilt libraries exist only for those.

`ipro6_demo` chooses how RAM is split between the Wi-Fi buffers and the application heap with one of `CONFIG_WIFI_MEM_PROFILE_PERF` (default), `_BALANCED` and `_APP`. Add one line to the configuration to switch, then delete the build directory and build again. Free heap and throughput for each profile are in `apps/platform/ipro6_demo/profile_selection_readme.md`.

## Flash and verify on the board { #flashing }

This walk-through uses an IPRO6S EVK with an IPRO Debug Probe: build `ipro6_demo`, flash it, and see a Wi-Fi scan on the console. IPRO6S images are flashed with the IntelProCube command-line tool and `--chipname ipro6`; the `flash` action of `build_freertos.sh` does not apply.

You need:

- An IPRO6S EVK, a 2.4 GHz antenna, an IPRO Debug Probe with its UART cable, and a USB-C power source.
- The toolchain, installed as in [Set Up Your Host](../../get-started/environment.md), and SDK V2.2.0 (written `<SDK>` below).
- [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 or later: download it, check its SHA-256 and extract it to a new folder as its [README](https://github.com/INTELPRO-INC/ipro-cube#readme) describes (written `<IntelProCube>` below). Images flashed with 0.7.0 do not boot; see [Flashing succeeds but the board does not boot](#ipro6s-no-boot).

<div class="ipro-steps" markdown>

1. **Build**: in the `<SDK>` root, run

    ```bash
    make -C apps/platform/ipro6_demo DEFCONFIG=defconfig_ipro6_lpwifi
    ```

    When it finishes, the linker prints the use of each memory region; the `flash` line reads about:

    ```text
               flash:     1092656 B         2 MB     52.10%
    ```

    The image is `apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin`.

2. **Connect**: connect the antenna to RF1 (u.FL) on the EVK. Connect the UART cable of the IPRO Debug Probe to J_UART on the EVK, and the probe to the computer over USB. Power the EVK through USB-C; LED1 lights up.

3. **Find the serial port**: in `<IntelProCube>`, run (on Linux `./ipro_iot_tool_linux`, on Windows `ipro_iot_tool.exe`; the same below)

    ```bash
    ./ipro_iot_tool_macos --list-ports
    ```

    The probe shows two ports. The one marked `(IPRO_U)`, whose name ends in `02`, is the UART: use it for flashing and for the console. `(IPRO_C)` is the chip debug port. macOS lists names that start with `/dev/tty.`; use the matching port that starts with `/dev/cu.`, for example `/dev/cu.usbmodemXXXX02`.

4. **Flash**:

    ```bash
    ./ipro_iot_tool_macos --chipname ipro6 --chip-variant IPRO6S \
        --port /dev/cu.usbmodemXXXX02 --baudrate 2000000 \
        --pt chips/ipro6/partition/partition_cfg_fw_direct.toml \
        --firmware <SDK>/apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin
    ```

    The tool puts the chip into download mode through the probe, writes and verifies the image, and resets the chip, in about 15 seconds. Only `[All Success]` at the end of the output means success; the tool exits 0 even when it fails. `partition_cfg_fw_direct.toml` places the firmware at flash address 0x0 without boot2 and keeps the partition table in the last two sectors.

5. **Check the boot**: open the same port at 115200 baud (8N1, no flow control), then press RESET (SW2) on the EVK.

    ```bash
    screen /dev/cu.usbmodemXXXX02 115200
    ```

    The boot messages end with:

    ```text
    [OS] Starting OS Scheduler...
    [EVENT] Event loop initialized
    [EVENT] WiFi event handler registered
    Init Shell (RT-Thread FinSH based)
    ipro />
    ```

6. **Check Wi-Fi**: type `stack_wifi`; when `CODE_WIFI_ON_MGMR_DONE` appears, type `wifi_scan`.

    ```text
    ipro />stack_wifi
    ...
    [APP] [EVT] CODE_WIFI_ON_INIT_DONE
    ...
    [APP] [EVT] CODE_WIFI_ON_MGMR_DONE
    ipro />wifi_scan
    [APP] [EVT] CODE_WIFI_ON_SCAN_DONE
    ...
    index[00]: channel 01, bssid XX:XX:XX:XX:XX:XX, rssi -20, ... auth WPA2-PSK, cipher: AES, SSID <ssid>
    ```

    Each nearby access point takes one line (up to 50 lines; unused ones show `empty`). If access points are listed, the radio and the Wi-Fi stack work. Run `stack_wifi` once per boot.

</div>

### Enter download mode by hand { #ipro6s-download-mode }

The tool enters download mode through the DL line of the probe. With a plain USB-to-UART cable, or when the tool reports a handshake failure, enter download mode by hand and then run the flash command: hold BOOT (SW1), press RESET (SW2), release BOOT. In download mode the console prints nothing; after flashing, press RESET to boot normally. Close any terminal program that holds the serial port (for example `screen`) before flashing, or the tool cannot open the port.

### Flashing succeeds but the board does not boot { #ipro6s-no-boot }

The IPRO6 boot header timing in IntelProCube 0.7.0 does not suit IPRO6S parts with the 2 MB in-package flash: the output ends with `[All Success]`, but after a reset the console stays silent and the chip stays in download mode. Use 0.7.0.1 or later, extracted to a new folder. If you extracted 0.7.0.1 over a 0.7.0 folder that has been used, delete `chips/ipro6/img_create_iot/efuse_bootheader_cfg.ini` first: the tool creates it from the template on its first run and never updates it. IPRO SDK Online Setup 3.6.0 and earlier install IntelProCube 0.7.0; install 0.7.0.1 separately to flash an IPRO6S.

## The FIN Wi-Fi card on the Reef { #dual-chip }

The FIN card puts an IPRO6S on an SD-card-shaped edge. It plugs into the Reef's microSD slot, works as an SDIO slave and is powered from the slot's SD_VDD. The IPRO7AI is the main SoC and runs the application, AI, BLE, audio and the IP stack; the IPRO6S on the card runs `ipro6_if_wifi` (`defconfig_ipro6_sdio`) and provides the wireless link.

```mermaid
flowchart LR
    A["IPRO7AI (Reef)<br/>application + ipronet_host + lwIP"] -- "SDIO 4-bit (microSD slot)" --> B["IPRO6S FIN card<br/>ipro6_if_wifi"]
    B -- "Wi-Fi 6" --> C["Access point"]
```

On the IPRO7AI, the host component `components/network/ipronet_host` drives the card through the SD host (GPIO28–33) and presents the link as the lwIP network interface `iproeth0`. Reef applications that use it:

| Application | Configuration | What it does |
|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `defconfig_wifi_ipro6s` | Wi-Fi connection and an RTSP camera stream at `rtsp://<ip>:8554/av0_0` |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `.config` | Sentino cloud voice chat, online through the FIN card |

With JP3 on GPIO, GPIO14 switches the slot's power and `fin cycle` power-cycles the card. For the connection and streaming steps see [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp) and [Wi-Fi and RTSP streaming](../../tutorials/wifi-rtsp.md).

### Update the FIN card firmware { #fin-update }

The `defconfig_wifi_ipro6s` build of `ipro7ai_reef_demo` offers two ways:

<div class="ipro-steps" markdown>

1. **Update over Wi-Fi**: the FIN firmware (`defconfig_ipro6_sdio` sets `CONFIG_RNM_OTA=y`) accepts the IPRO6 OTA package `FW_OTA.bin.xz.ota` made by IntelProCube. Put the package on an HTTP server the Reef can reach, for example by running this in the package's directory:

    ```bash
    python3 -m http.server 8000
    ```

2. **Connect and update from the Reef console**:

    ```text
    ipronet_up <ssid> <psk>
    ipro6s_ota http://<host-ip>:8000/FW_OTA.bin.xz.ota
    ```

    The card writes the package to its firmware partition, checks it with SHA-256, reboots and boot2 installs it; this takes about 30–60 seconds. On success the console prints `[ota] RESULT OK`; on failure `[ota] RESULT ERR rc=…` and the phase that failed. Only `http://` is supported.

</div>

The other way is `ipro6_dl` at the Reef console: it powers the card off, drives the SD_D0 (GPIO29) download strap high and powers it on again, so the IPRO6S starts in BROM download mode. Flashing then goes through the IPRO6S's UART with `--chipname ipro6`; how to reach that UART on the FIN card is not covered in this release's documentation, contact INTELPRO. `ipro6_rst` power-cycles the card back into a normal boot, and `ipro6_pwr 0|1` switches its power by hand.

## Related documents { #documents }

- [IPRO7](ipro7.md#networking): how IPRO7 connects to networks.
- [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp): the FIN card, JP3 and the Wi-Fi commands.
- [Networking guide](../../guides/networking.md): lwIP, Ethernet and the SDIO Wi-Fi host.
- `components/network/ipronet_host/README.md`: the host API and the OTA flow.
