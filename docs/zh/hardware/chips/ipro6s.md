---
title: "IPRO6S（V2.0.1）"
description: IPRO6S 的支援狀態、晶片規格、作為 IPRO7 Wi-Fi 夥伴晶片的用法，以及 SDK V2.0.1 的 Wi-Fi 6 與 BR/EDR 開發起點
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S（V2.0.1）

IPRO6S 是內建 Wi-Fi 6、支援 BLE 5.4 與 BR/EDR 的 RISC-V SoC。它有兩種用法：在 SDK V2.0.1 上作為獨立的 Wi-Fi／藍牙雙模晶片開發；或作為 IPRO7 的 Wi-Fi 夥伴晶片，經 SDIO 為 IPRO7 提供連網，這部分的 IPRO7 主機端隨 V2.1.0 提供。

!!! info "V2.1.0 不支援 IPRO6S 建置"
    V2.1.0 沒有 IPRO6S 應用、IPRO6S BLE 控制器函式庫與 RF 驅動 `ipro6_rf`；套件的 README 與 `VERSION.txt` 仍列出 IPRO6S，但沒有可建置的 IPRO6S 內容。IPRO6S 開發請使用 [SDK V2.0.1](#get-v2-0-1)。本頁標示「V2.0.1」的內容適用於 V2.0.1。

## 支援狀態 { #status }

| 項目 | V2.1.0 | V2.0.1 |
|---|---|---|
| IPRO6S 應用（`ipro6_demo`、`ipro6_btdm_phyrf`、`ipro6_if_wifi`） | 無 | 有 |
| IPRO6S BLE 控制器函式庫 | 無 | 有 |
| RF 驅動 `ipro6_rf` | 無 | 有 |
| IPRO7 端的 SDIO Wi-Fi 主機（`components/network/ipronet_host`） | 有 | — |
| Zephyr RTOS 板型 `ipro6s_evb` | 檔案隨附，但本版不支援 | — |

## 晶片規格 { #ipro6s }

| 項目 | IPRO6S |
|---|---|
| 核心 | RISC-V RV32IMAFC，含 DSP 擴充；與 IPRO7 使用同一套工具鏈 |
| Bluetooth | BLE 5.4 與 BR/EDR：A2DP、AVRCP、HFP-HF、SCO |
| Wi-Fi | 內建 Wi-Fi 6 |
| NPU／ISP | 無 |
| 參考板 | IPRO6S EVB |

| 區域 | 大小 | 起始位址 | 說明 |
|---|---|---|---|
| Flash | 2 MB | `0x13000000` | |
| TCM RAM | 320 KB | `0x11000000` | 程式碼與資料；縮減配置為 280 KB |
| Wi-Fi RAM | 160 KB | `0x21050000` | 藍牙 Exchange Memory（`CONFIG_EM_SIZE`）由頂端劃出 |
| HBN RAM | 4 KB | `0x20090000` | |

應用實際可用的記憶體取決於連結器配置與控制器設定；請以 V2.0.1 中 `ipro6_demo`、`ipro6_if_wifi` 與 `ipro6_btdm_phyrf` 的配置為準。

V2.0.1 的 IPRO6S 應用以下列設定選擇晶片：

```ini title=".config（V2.0.1，節錄）"
CONFIG_IPRO6=y
CONFIG_CPU_ID="intelpro_ipro7"     # 與 IPRO7 共用工具鏈
CONFIG_BOARD="EVB"
CONFIG_BTDM_ENABLE=y               # IPRO6S = IPRO6 加上雙模控制器
CONFIG_FREERTOS_SUPPORT=y
```

## IPRO7 的 SDIO Wi-Fi 夥伴晶片 { #dual-chip }

需要 Wi-Fi 的產品採雙晶片架構：IPRO7 是主控 SoC，負責應用、AI、BLE、音訊與 IP 協定堆疊；IPRO6S 執行 Wi-Fi 韌體，作為 SDIO 從端提供無線連線。

```mermaid
flowchart LR
    A["IPRO7<br/>應用 + ipronet_host + lwIP"] -- "SDIO 4-bit" --> B["IPRO6S<br/>Wi-Fi 韌體"]
    B -- "Wi-Fi" --> C["無線基地台"]
```

IPRO7 端的主機元件 `components/network/ipronet_host` 隨 V2.1.0 提供：它經 SDH 控制器（固定在 GPIO28–33）驅動 IPRO6S，把連線呈現為 lwIP 網路介面 `iproeth0`。`.config` 設定、API 用法與使用它的應用（`ipro7_sdio_wifi`、`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s`、`ipro_agora_sentino`）見[網路](../../guides/networking.md#wifi-ipro6)。

**IPRO6S FIN 卡**是插入 Reef SD 卡槽的 IPRO6S Wi-Fi 卡，以 SDIO 從端工作，由卡槽的 SD_VDD 供電；用法見 [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp)。

IPRO6S 端韌體：

- `ipro6_if_wifi`（IPRO6S 的 SDIO Wi-Fi 韌體）只收錄於 V2.0.1，V2.1.0 未包含。
- FIN 卡上的韌體未包含於 V2.1.0，請洽 INTELPRO。

## Wi-Fi 6 獨立連網（V2.0.1） { #ipro6s-wifi6 }

以 IPRO6S 本身的 Wi-Fi 6 連網時，在 V2.0.1 以 `apps/platform/ipro6_demo/` 為起點，啟用：

```ini title=".config（V2.0.1，節錄）"
CONFIG_WIFI6=y
CONFIG_USE_MACSW=y
```

Wi-Fi MAC（`components/wireless/macsw`）是預編譯函式庫；其上的 fhost API、wpa_supplicant 與 lwIP 轉接層（`components/wireless/wifi6`）是原始碼，可依產品調整網路堆疊與 supplicant 設定。`ipro6_demo` 示範 Station 與 soft-AP 啟動、DHCP，以及操作它們的 shell 指令。

## BLE 與 BR/EDR（V2.0.1） { #ipro6s-btdm }

V2.0.1 的 IPRO6S 與 IPRO7 共用 Zephyr 4.4 BLE Host，另使用六個雙模控制器函式庫 `libipro_ble_controller_ipro6s_link{1,2,4}_br[_release].a`。以 V2.0.1 的 `apps/platform/ipro6_btdm_phyrf/.config` 為起點：

```ini title="apps/platform/ipro6_btdm_phyrf/.config（V2.0.1，節錄）"
CONFIG_IPRO6=y
CONFIG_BTDM_ENABLE=y
CONFIG_BTDM_BT_ENABLE=y               # 編入 BR/EDR（_br）
CONFIG_BTDM_MAX_ACL_CONNECTIONS=4     # link<N>：1、2 或 4
```

未設定 `CONFIG_BTDM_DEBUG` 時選用 `_release` 版本。此範例示範 A2DP sink（SBC）、AVRCP、HFP-HF，以及把 SCO 音訊橋接到 I2S。在 V2.0.1 中建置：

```bash
./build_freertos.sh ipro6_btdm_phyrf build
```

## 取得 SDK V2.0.1 { #get-v2-0-1 }

IPRO6S 開發使用 GitHub Release [`IPRO-SDK-V2.0.1`](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)（2026-09-09）。V2.0.1 的建置與燒錄流程以該版本套件內的 README 為準。

## 相關文件 { #documents }

- [IPRO7](ipro7.md)：主控晶片規格。
- [IPRO7AI Reef EVK](../boards/reef-evk.md)：FIN 卡的使用方式。
- [網路指南](../../guides/networking.md)：lwIP、乙太網路與 SDIO Wi-Fi 主機。
