---
title: "IPRO6S"
description: IPRO6S 的規格、V2.2.0 隨附的三個 Wi-Fi 6 應用與其設定、建置與燒錄，以及在 IPRO7AI Reef EVK 上作為 FIN Wi-Fi 卡的用法
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S

IPRO6S 是內建 Wi-Fi 6 的 RISC-V SoC，與 IPRO7 使用同一份 SDK 原始碼樹與同一套工具鏈建置。V2.2.0 隨附三個 IPRO6S Wi-Fi 應用：獨立連網的 `ipro6_demo`、把 Wi-Fi 經 SDIO 或 USB 橋接給主處理器的 `ipro6_if_wifi`，以及 Linux 主機用的 FullMAC 韌體 `ipro6_fmac`。在 IPRO7AI Reef EVK 上，IPRO6S 是插在 microSD 卡座的 FIN Wi-Fi 卡，經 SDIO 為 IPRO7AI 提供連網。

<div class="ipro-facts" markdown>
<div><strong>Wi-Fi 6</strong><span>內建於晶片</span></div>
<div><strong>RV32IMAFC</strong><span>與 IPRO7 相同的工具鏈</span></div>
<div><strong>3</strong><span>IPRO6S 應用</span></div>
<div><strong>ipro6</strong><span>燒錄時的 <code>--chipname</code></span></div>
</div>

## 晶片規格 { #ipro6s }

| 項目 | IPRO6S |
|---|---|
| 核心 | RISC-V RV32IMAFC，含 DSP 擴充 |
| 無線 | 內建 Wi-Fi 6 |
| NPU／ISP | 無 |
| RTOS | FreeRTOS V11 |
| 參考板 | IPRO6S EVB（供應請洽 INTELPRO）；Reef 的 FIN 卡 |

| 區域 | 大小 | 起始位址 | 說明 |
|---|---|---|---|
| Flash | 2 MB | `0x13000000` | |
| TCM RAM | 320 KB | `0x11000000` | 程式碼與資料；縮減配置為 280 KB |
| Wi-Fi RAM | 160 KB | `0x21050000` | |
| HBN RAM | 4 KB | `0x20090000` | |

IPRO6S 應用以下列設定選擇晶片，映像檔名的晶片後綴為 `IPRO6`：

```ini title="apps/platform/ipro6_if_wifi/defconfig_ipro6_sdio（節錄）"
CONFIG_IPRO6=y
CONFIG_CHIP="IPRO6"
CONFIG_CPU_ID="intelpro_ipro7"     # 與 IPRO7 共用工具鏈
CONFIG_FREERTOS_SUPPORT=y
```

## 本版 SDK 支援 { #status }

| 項目 | V2.2.0 |
|---|---|
| 應用 | `ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`（`apps/platform/`） |
| Wi-Fi 6 | MAC（`components/wireless/macsw`）、fhost API、wpa_supplicant 與 lwIP 轉接層（`components/wireless/wifi6`）、RF 驅動（`components/wireless/rf/ipro6_rf`），皆為依應用設定預編譯的函式庫 |
| 低功耗 | DTIM 低功耗韌體映像 `bsp/hal/lp_framework/ipro6/prebuilt/ipro6_lpfw.bin`，由低功耗設定嵌入 |
| Bluetooth | IPRO6S 的藍牙控制器函式庫與雙模（BR/EDR）應用未包含於 V2.2.0，請洽 INTELPRO。本版 IPRO6S 應用只使用 Wi-Fi |
| Zephyr RTOS | 隨附 `ipro6s_evb` 板型檔案，但本版不支援 IPRO6S 的 Zephyr 建置 |
| 燒錄 | IntelProCube v0.6.3 命令列工具（另行取得），`--chipname ipro6`；`build_freertos.sh` 的 `flash` 只支援 IPRO7 |

## 應用與設定 { #apps }

每個 IPRO6S 應用都以 `DEFCONFIG=` 選擇設定。下表是經過建置驗證的設定；應用的 `.config` 是第一個設定的副本。

| 應用 | 設定 | 內容 |
|---|---|---|
| `ipro6_demo` | `defconfig_ipro6_lpwifi` | Wi-Fi 6 Station 與 soft-AP、lwIP、shell，加上 DTIM 省電 |
| | `defconfig_ipro6_lp` | 低功耗示範，不含 Wi-Fi |
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 6 橋接：主處理器經 SDIO 看到類似乙太網路的介面；Reef 的 FIN 卡韌體 |
| | `defconfig_ipro6_usb` | 同上，經 USB |
| | `defconfig_ipro6_lp` | 低功耗示範，不含 Wi-Fi |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | Linux cfg80211 主機用的 FullMAC 韌體（映像 `ipro6s_fmac.img`）；`make` 預設使用這個設定 |
| | `defconfig_ipro6_fmac_loader` | 經 SDIO 或 USB 接收 FullMAC 韌體的 Flash 載入程式 |

- `ipro6_demo/defconfig_ipro6_lpwifi_ping` 與 `ipro6_fmac/defconfig_ipro6_fmac_ap` 沒有設定 `CONFIG_WIRELESS_LIB_VARIANT`，不在驗證過的設定之列；使用前請洽 INTELPRO。
- `ipro6_fmac` 的 Linux 主機端驅動未包含於 V2.2.0。
- 這三個應用以 IPRO6S EVB 為目標（`CONFIG_BOARD="EVB"`）；在 Reef 上只有 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio` 執行於 FIN 卡。

## 建置 { #build }

在 SDK 根目錄執行，以 FIN 卡韌體為例：

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

建置結束時連結器印出 Flash 與 RAM 用量，映像位於 `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。輸出目錄為 `build_` 加上去掉 `defconfig_` 的設定名稱；`ipro6_fmac` 的 Makefile 預設帶 `DEFCONFIG=defconfig_ipro6_fmac`，所以直接 `make` 也輸出到 `build_ipro6_fmac/`。`build_freertos.sh -d defconfig_ipro6_sdio build ipro6_if_wifi` 也能建置，但不能燒錄 IPRO6S。

### Wi-Fi 函式庫與自訂設定 { #wifi-libs }

Wi-Fi 的 MAC、fhost、wpa_supplicant、lwIP 轉接層與 RF 驅動依應用設定各預編譯一份，放在各元件的 `lib/<應用>-<設定>/`，由設定中的 `CONFIG_WIRELESS_LIB_VARIANT` 選擇，例如 `defconfig_ipro6_sdio` 的：

```ini
CONFIG_WIFI6=y
CONFIG_USE_MACSW=y
CONFIG_WIRELESS_LIB_VARIANT="ipro6_if_wifi-ipro6_sdio"
```

自訂設定時，保留上表某一個設定的 Wi-Fi 選項與它的 `CONFIG_WIRELESS_LIB_VARIANT`；預編譯函式庫只為這些組合提供。

`ipro6_demo` 以 `CONFIG_WIFI_MEM_PROFILE_PERF`（預設）、`_BALANCED`、`_APP` 三選一，決定 Wi-Fi 緩衝區與應用堆積如何分配 RAM；在設定檔加入一行即可切換，改完要刪除建置目錄再建置。各設定的可用堆積與吞吐量見 `apps/platform/ipro6_demo/profile_selection_readme.md`。

## 燒錄 { #flashing }

IPRO6S 映像以 IntelProCube 命令列工具的 `--chipname ipro6` 燒錄，在 IntelProCube 目錄下執行：

```bash
./ipro_iot_tool_macos --chipname ipro6 --config chips/ipro6/conf/iot.toml --skip-ota
```

`chips/ipro6/conf/iot.toml` 要指向剛建置的 `.bin`。工具即使失敗也會以 0 結束，請以輸出中的 `[All Success]` 判斷結果。IPRO6S EVB 進入下載模式的操作請洽 INTELPRO；Reef 上的 FIN 卡見下一節。

## Reef 上的 FIN Wi-Fi 卡 { #dual-chip }

FIN 卡是把 IPRO6S 做在 SD 卡形狀板緣上的 Wi-Fi 卡，插進 Reef 的 microSD 卡座，以 SDIO 從端工作，由卡座的 SD_VDD 供電。IPRO7AI 是主控 SoC，負責應用、AI、BLE、音訊與 IP 協定堆疊；FIN 卡上的 IPRO6S 執行 `ipro6_if_wifi`（`defconfig_ipro6_sdio`），提供無線連線。

```mermaid
flowchart LR
    A["IPRO7AI（Reef）<br/>應用 + ipronet_host + lwIP"] -- "SDIO 4-bit（microSD 卡座）" --> B["IPRO6S FIN 卡<br/>ipro6_if_wifi"]
    B -- "Wi-Fi 6" --> C["無線基地台"]
```

IPRO7AI 端的主機元件 `components/network/ipronet_host` 經 SD 主控（GPIO28–33）驅動卡片，把連線呈現為 lwIP 網路介面 `iproeth0`。使用它的 Reef 應用：

| 應用 | 設定 | 內容 |
|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `defconfig_wifi_ipro6s` | Wi-Fi 連線與 RTSP 相機串流 `rtsp://<ip>:8554/av0_0` |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `.config` | Sentino 雲端語音對話，經 FIN 卡連網 |

把 JP3 設在 GPIO 時，卡座電源由 GPIO14 控制，`fin cycle` 可以重新為卡片上電。連線與串流的步驟見 [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp) 與 [Wi-Fi 與 RTSP 串流](../../tutorials/wifi-rtsp.md)。

### 更新 FIN 卡韌體 { #fin-update }

`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 建置提供兩種方式：

<div class="ipro-steps" markdown>

1. **經 Wi-Fi 更新**：FIN 卡韌體（`defconfig_ipro6_sdio` 已設定 `CONFIG_RNM_OTA=y`）接受 IntelProCube 產生的 IPRO6 OTA 套件 `FW_OTA.bin.xz.ota`。把套件放在 Reef 連得到的 HTTP 伺服器上，例如在套件所在目錄執行：

    ```bash
    python3 -m http.server 8000
    ```

2. **在 Reef 主控台連線並更新**：

    ```text
    ipronet_up <ssid> <psk>
    ipro6s_ota http://<主機 IP>:8000/FW_OTA.bin.xz.ota
    ```

    卡片把套件寫入韌體分割區、以 SHA-256 檢查後重新開機由 boot2 安裝，約需 30–60 秒。成功時主控台印出 `[ota] RESULT OK`，失敗時印出 `[ota] RESULT ERR rc=…` 與失敗的階段。只支援 `http://`。

</div>

另一種方式是在 Reef 主控台輸入 `ipro6_dl`：它關閉卡片電源，拉高 SD_D0（GPIO29）的下載腳位後重新上電，讓 IPRO6S 進入 BROM 下載模式，之後要經 IPRO6S 的 UART 以 `--chipname ipro6` 燒錄；FIN 卡上 UART 的接法未包含於本版文件，請洽 INTELPRO。`ipro6_rst` 重新為卡片上電回到一般開機，`ipro6_pwr 0|1` 手動開關卡片電源。

## 相關文件 { #documents }

- [IPRO7](ipro7.md#networking)：IPRO7 的網路連線方式。
- [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp)：FIN 卡、JP3 與 Wi-Fi 指令。
- [網路指南](../../guides/networking.md)：lwIP、乙太網路與 SDIO Wi-Fi 主機。
- `components/network/ipronet_host/README.md`：主機端 API 與 OTA 流程。
