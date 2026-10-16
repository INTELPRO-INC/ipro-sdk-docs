---
title: "IPRO6S (V2.0.1)"
description: IPRO6S support status, chip specifications, its use as the Wi-Fi companion of an IPRO7, and where to start with Wi-Fi 6 and BR/EDR on SDK V2.0.1
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S (V2.0.1)

IPRO6S is a RISC-V SoC with built-in Wi-Fi 6, BLE 5.4 and BR/EDR. You can use it in two ways: as a stand-alone Wi-Fi / dual-mode Bluetooth chip, developed on SDK V2.0.1; or as the Wi-Fi companion of an IPRO7, connected over SDIO. The IPRO7 host side of the second option ships in V2.1.0.

!!! info "V2.1.0 does not build for IPRO6S"
    V2.1.0 contains no IPRO6S applications, no IPRO6S BLE controller libraries and no `ipro6_rf` RF driver. The package README and `VERSION.txt` still list IPRO6S, but nothing in the package builds for it. Use [SDK V2.0.1](#get-v2-0-1) for IPRO6S development. Content marked "V2.0.1" on this page applies to V2.0.1.

## Support status { #status }

| Item | V2.1.0 | V2.0.1 |
|---|---|---|
| IPRO6S applications (`ipro6_demo`, `ipro6_btdm_phyrf`, `ipro6_if_wifi`) | No | Yes |
| IPRO6S BLE controller libraries | No | Yes |
| RF driver `ipro6_rf` | No | Yes |
| SDIO Wi-Fi host on the IPRO7 (`components/network/ipronet_host`) | Yes | — |
| Zephyr RTOS board `ipro6s_evb` | Files included, not supported in this release | — |

## Chip specifications { #ipro6s }

| Item | IPRO6S |
|---|---|
| Core | RISC-V RV32IMAFC with DSP extensions; same toolchain as IPRO7 |
| Bluetooth | BLE 5.4 and BR/EDR: A2DP, AVRCP, HFP-HF, SCO |
| Wi-Fi | Built-in Wi-Fi 6 |
| NPU / ISP | None |
| Reference board | IPRO6S EVB |

| Region | Size | Base address | Notes |
|---|---|---|---|
| Flash | 2 MB | `0x13000000` | |
| TCM RAM | 320 KB | `0x11000000` | Code and data; 280 KB in the reduced layout |
| Wi-Fi RAM | 160 KB | `0x21050000` | The Bluetooth Exchange Memory (`CONFIG_EM_SIZE`) is carved from the top |
| HBN RAM | 4 KB | `0x20090000` | |

How much memory an application can use depends on the linker layout and the controller settings; follow the configurations of `ipro6_demo`, `ipro6_if_wifi` and `ipro6_btdm_phyrf` in V2.0.1.

IPRO6S applications in V2.0.1 select the chip with:

```ini title=".config (V2.0.1, excerpt)"
CONFIG_IPRO6=y
CONFIG_CPU_ID="intelpro_ipro7"     # same toolchain as IPRO7
CONFIG_BOARD="EVB"
CONFIG_BTDM_ENABLE=y               # IPRO6S = IPRO6 plus the dual-mode controller
CONFIG_FREERTOS_SUPPORT=y
```

## Wi-Fi companion for IPRO7 { #dual-chip }

Products that need Wi-Fi use two chips: the IPRO7 is the main SoC and runs the application, AI, BLE, audio and the IP stack; the IPRO6S runs the Wi-Fi firmware and provides the wireless link as an SDIO device.

```mermaid
flowchart LR
    A["IPRO7<br/>application + ipronet_host + lwIP"] -- "SDIO 4-bit" --> B["IPRO6S<br/>Wi-Fi firmware"]
    B -- "Wi-Fi" --> C["Access point"]
```

The IPRO7 host component `components/network/ipronet_host` ships with V2.1.0: it drives the IPRO6S through the SDH controller (fixed on GPIO28–33) and presents the link as the lwIP network interface `iproeth0`. Its `.config` settings, the API and the applications that use it (`ipro7_sdio_wifi`, the `defconfig_wifi_ipro6s` build of `ipro7ai_reef_demo`, `ipro_agora_sentino`) are covered in [Networking](../../guides/networking.md#wifi-ipro6).

The **IPRO6S FIN card** is an IPRO6S Wi-Fi card that plugs into the Reef's SD slot, works as an SDIO device and is powered from the slot's SD_VDD; see [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp) for how to use it.

IPRO6S firmware:

- `ipro6_if_wifi` (the IPRO6S SDIO Wi-Fi firmware) ships only with V2.0.1, not with V2.1.0.
- The FIN-card firmware is not included in V2.1.0; contact INTELPRO.

## Stand-alone Wi-Fi 6 (V2.0.1) { #ipro6s-wifi6 }

To use the IPRO6S's own Wi-Fi 6, start from `apps/platform/ipro6_demo/` in V2.0.1 and enable:

```ini title=".config (V2.0.1, excerpt)"
CONFIG_WIFI6=y
CONFIG_USE_MACSW=y
```

The Wi-Fi MAC (`components/wireless/macsw`) is a prebuilt library. The fhost API, wpa_supplicant and the lwIP adapter above it (`components/wireless/wifi6`) are source, so you can adapt the network stack and supplicant settings. `ipro6_demo` shows station and soft-AP bring-up, DHCP and the shell commands that drive them.

## BLE and BR/EDR (V2.0.1) { #ipro6s-btdm }

In V2.0.1 the IPRO6S shares the Zephyr 4.4 BLE host with IPRO7 and adds six dual-mode controller libraries, `libipro_ble_controller_ipro6s_link{1,2,4}_br[_release].a`. Start from `apps/platform/ipro6_btdm_phyrf/.config` in V2.0.1:

```ini title="apps/platform/ipro6_btdm_phyrf/.config (V2.0.1, excerpt)"
CONFIG_IPRO6=y
CONFIG_BTDM_ENABLE=y
CONFIG_BTDM_BT_ENABLE=y               # BR/EDR compiled in (_br)
CONFIG_BTDM_MAX_ACL_CONNECTIONS=4     # link<N>: 1, 2 or 4
```

Without `CONFIG_BTDM_DEBUG` the `_release` library is used. The example shows an A2DP sink (SBC), AVRCP, HFP-HF and the SCO audio bridge to I2S. Build it in V2.0.1 with:

```bash
./build_freertos.sh ipro6_btdm_phyrf build
```

## Get SDK V2.0.1 { #get-v2-0-1 }

IPRO6S development uses the GitHub release [`IPRO-SDK-V2.0.1`](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1) (2026-09-09). For building and flashing on V2.0.1, follow the README in that package.

## Related documents { #documents }

- [IPRO7](ipro7.md): specifications of the main chip.
- [IPRO7AI Reef EVK](../boards/reef-evk.md): how to use the FIN card.
- [Networking guide](../../guides/networking.md): lwIP, Ethernet and the SDIO Wi-Fi host.
