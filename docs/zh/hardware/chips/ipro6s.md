---
title: "IPRO6S"
description: IPRO6S 的規格、V2.3.0 隨附的三個 Wi-Fi 應用與其設定、建置與燒錄，以及在 IPRO7AI Reef EVK 上作為 FIN Wi-Fi 卡的用法
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S

IPRO6S 是內建 Wi-Fi 的 RISC-V SoC，與 IPRO7 使用同一份 SDK 原始碼樹與同一套工具鏈建置。V2.3.0 隨附三個 IPRO6S Wi-Fi 應用：獨立連網的 `ipro6_demo`、把 Wi-Fi 經 SDIO 或 USB 橋接給主處理器的 `ipro6_if_wifi`，以及 Linux 主機用的 FullMAC 韌體 `ipro6_fmac`。在 IPRO7AI Reef EVK 上，IPRO6S 是插在 microSD 卡座的 FIN Wi-Fi 卡，經 SDIO 為 IPRO7AI 提供連網。

<div class="ipro-facts" markdown>
<div><strong>Wi-Fi</strong><span>內建於晶片</span></div>
<div><strong>RV32IMAFC</strong><span>與 IPRO7 相同的工具鏈</span></div>
<div><strong>3</strong><span>IPRO6S 應用</span></div>
<div><strong>ipro6</strong><span>燒錄時的 <code>--chipname</code></span></div>
</div>

## 晶片規格 { #ipro6s }

| 項目 | IPRO6S |
|---|---|
| 核心 | RISC-V RV32IMAFC，含 DSP 擴充 |
| 無線 | 內建 Wi-Fi |
| NPU／ISP | 無 |
| RTOS | FreeRTOS V11 |
| 參考板 | IPRO6S EVK（供應請洽 INTELPRO）；Reef 的 FIN 卡 |

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

| 項目 | V2.3.0 |
|---|---|
| 應用 | `ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`（`apps/platform/`） |
| Wi-Fi | MAC（`components/wireless/macsw`）、fhost API、wpa_supplicant 與 lwIP 轉接層（`components/wireless/wifi6`）、RF 驅動（`components/wireless/rf/ipro6_rf`），皆為依應用設定預編譯的函式庫 |
| 低功耗 | DTIM 低功耗韌體映像 `bsp/hal/lp_framework/ipro6/prebuilt/ipro6_lpfw.bin`，由低功耗設定嵌入 |
| Bluetooth | IPRO6S 的藍牙控制器函式庫與雙模（BR/EDR）應用未包含於 V2.3.0，請洽 INTELPRO。本版 IPRO6S 應用只使用 Wi-Fi |
| Zephyr RTOS | 隨附 `ipro6s_evb` 板型檔案，但本版不支援 IPRO6S 的 Zephyr 建置 |
| 燒錄 | [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 以上的命令列工具，`--chipname ipro6`；`build_freertos.sh` 的 `flash` 只支援 IPRO7 |

## 應用與設定 { #apps }

每個 IPRO6S 應用都以 `DEFCONFIG=` 選擇設定。下表是經過建置驗證的設定；應用的 `.config` 是第一個設定的副本。

| 應用 | 設定 | 內容 |
|---|---|---|
| `ipro6_demo` | `defconfig_ipro6_lpwifi` | Wi-Fi Station 與 soft-AP、lwIP、shell，加上 DTIM 省電 |
| | `defconfig_ipro6_lp` | 低功耗示範，不含 Wi-Fi |
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 橋接：主處理器經 SDIO 看到類似乙太網路的介面；Reef 的 FIN 卡韌體 |
| | `defconfig_ipro6_usb` | 同上，經 USB |
| | `defconfig_ipro6_lp` | 低功耗示範，不含 Wi-Fi |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | Linux cfg80211 主機用的 FullMAC 韌體（映像 `ipro6s_fmac.img`）；`make` 預設使用這個設定 |
| | `defconfig_ipro6_fmac_loader` | 經 SDIO 或 USB 接收 FullMAC 韌體的 Flash 載入程式 |

- `ipro6_fmac/defconfig_ipro6_fmac_ap` 沒有設定 `CONFIG_WIRELESS_LIB_VARIANT`，不在驗證過的設定之列；使用前請洽 INTELPRO。V2.2.x 隨附的 `ipro6_demo/defconfig_ipro6_lpwifi_ping` 需要 Wi-Fi 函式庫原始碼，V2.3.0 起不在套件中。
- `ipro6_fmac` 的 Linux 主機端驅動未包含於 V2.3.0。
- 這三個應用以 IPRO6S EVK 為目標（`CONFIG_BOARD="EVB"`）；在 Reef 上只有 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio` 執行於 FIN 卡。

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

## 燒錄與上板驗證 { #flashing }

以下以 IPRO6S EVK 搭配 IPRO Debug Probe 為例，從建置 `ipro6_demo` 到在主控台看見 Wi-Fi 掃描結果。IPRO6S 映像以 IntelProCube 命令列工具的 `--chipname ipro6` 燒錄；`build_freertos.sh` 的 `flash` 不適用。

需要：

- IPRO6S EVK、2.4 GHz 天線、IPRO Debug Probe 與它的 UART 排線、USB-C 電源。
- 依[準備開發環境](../../get-started/environment.md)安裝的工具鏈，以及 SDK V2.3.0（下文寫作 `<SDK>`）。
- [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 以上：依 [README](https://github.com/INTELPRO-INC/ipro-cube#readme) 下載、核對 SHA-256，解壓到新的資料夾（下文寫作 `<IntelProCube>`）。以 0.7.0 燒錄的映像無法開機，見[燒錄成功卻沒有開機](#ipro6s-no-boot)。

<div class="ipro-steps" markdown>

1. **建置**：在 `<SDK>` 根目錄執行

    ```bash
    make -C apps/platform/ipro6_demo DEFCONFIG=defconfig_ipro6_lpwifi
    ```

    結束時連結器印出各記憶體區域的用量，其中 `flash` 一行約為：

    ```text
               flash:     1092656 B         2 MB     52.10%
    ```

    映像位於 `apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin`。

2. **接線**：天線接到 EVK 的 RF1（u.FL）。IPRO Debug Probe 的 UART 排線接到 EVK 的 J_UART，探針以 USB 接電腦。EVK 以 USB-C 供電，LED1 亮起。

3. **找出序列埠**：在 `<IntelProCube>` 目錄執行（Linux 為 `./ipro_iot_tool_linux`，Windows 為 `ipro_iot_tool.exe`，下同）

    ```bash
    ./ipro_iot_tool_macos --list-ports
    ```

    探針會列出兩個埠：標示 `(IPRO_U)`、名稱以 `02` 結尾的是 UART，燒錄與主控台都用它；`(IPRO_C)` 是晶片除錯埠。macOS 列出的名稱以 `/dev/tty.` 開頭，請改用 `/dev/cu.` 開頭的同名埠，例如 `/dev/cu.usbmodemXXXX02`。

4. **燒錄**：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro6 --chip-variant IPRO6S \
        --port /dev/cu.usbmodemXXXX02 --baudrate 2000000 \
        --pt chips/ipro6/partition/partition_cfg_fw_direct.toml \
        --firmware <SDK>/apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin
    ```

    工具經探針讓晶片進入下載模式，燒錄並校驗後重置晶片，約需 15 秒。輸出最後出現 `[All Success]` 才算成功；工具即使失敗也以 0 結束。`partition_cfg_fw_direct.toml` 把韌體放在 Flash 位址 0x0、不使用 boot2，分割表放在最後兩個扇區。

5. **確認開機**：以 115200 baud（8N1、無流量控制）開啟同一個埠，再按一下 EVK 的 RESET（SW2）。

    ```bash
    screen /dev/cu.usbmodemXXXX02 115200
    ```

    V2.3.0 起，開機訊息前段有一行 `Build:<時間>,<日期>`，是這次建置的時間，和 IPRO7 相同。開機訊息的最後幾行：

    ```text
    [OS] Starting OS Scheduler...
    [EVENT] Event loop initialized
    [EVENT] WiFi event handler registered
    Init Shell (RT-Thread FinSH based)
    ipro />
    ```

6. **確認 Wi-Fi**：輸入 `stack_wifi`，出現 `CODE_WIFI_ON_MGMR_DONE` 後再輸入 `wifi_scan`。

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

    附近每個基地台一行（最多 50 行，沒用到的顯示 `empty`）。列得出基地台，表示射頻與 Wi-Fi 協定堆疊都正常。同一次開機只需執行一次 `stack_wifi`。

7. **確認 soft-AP**：啟動基地台，金鑰為 8 到 63 個字元。

    ```text
    ipro />wifi_ap_start -s IPRO6S_AP -k <key> -c 6
    [WPA] AP-ENABLED
    [APP] [EVT] CODE_WIFI_ON_AP_STARTED
    ```

    用電腦或手機以該金鑰連上 `IPRO6S_AP`，會從板子取得 192.168.169.0/24 的位址（板子是 192.168.169.1），主控台印出 `AP-STA-CONNECTED` 與該裝置的 MAC 位址。`wifi_ap_stop` 停止基地台。

</div>

### 手動進入下載模式 { #ipro6s-download-mode }

工具經探針的 DL 線自動進入下載模式。使用一般 USB 轉 UART 線，或工具回報握手失敗時，先手動進入下載模式再執行燒錄指令：按住 BOOT（SW1），按一下 RESET（SW2），再放開 BOOT。晶片在下載模式時主控台沒有任何輸出；燒錄完成後按一下 RESET 回到正常開機。燒錄前請關閉占用該序列埠的終端程式（例如 `screen`），否則工具無法開啟序列埠。

### 燒錄成功卻沒有開機 { #ipro6s-no-boot }

IntelProCube 0.7.0 的 IPRO6 開機標頭時序不適用於 2 MB 封裝內 Flash 的 IPRO6S：輸出有 `[All Success]`，重置後主控台卻沒有任何訊息，晶片停在下載模式。請改用 0.7.0.1 以上並解壓到新的資料夾。若把 0.7.0.1 解壓覆蓋在用過的 0.7.0 資料夾上，先刪除 `chips/ipro6/img_create_iot/efuse_bootheader_cfg.ini`：這個檔案在工具第一次執行時由範本產生，之後不會更新。IPRO SDK Online Setup 3.6.0 以前安裝的 IntelProCube 是 0.7.0，燒錄 IPRO6S 時請另外安裝 0.7.0.1。

## Reef 上的 FIN Wi-Fi 卡 { #dual-chip }

FIN 卡是把 IPRO6S 做在 SD 卡形狀板緣上的 Wi-Fi 卡，插進 Reef 的 microSD 卡座，以 SDIO 從端工作，由卡座的 SD_VDD 供電。IPRO7AI 是主控 SoC，負責應用、AI、BLE、音訊與 IP 協定堆疊；FIN 卡上的 IPRO6S 執行 `ipro6_if_wifi`（`defconfig_ipro6_sdio`），提供無線連線。

```mermaid
flowchart LR
    A["IPRO7AI（Reef）<br/>應用 + ipronet_host + lwIP"] -- "SDIO 4-bit（microSD 卡座）" --> B["IPRO6S FIN 卡<br/>ipro6_if_wifi"]
    B -- "Wi-Fi" --> C["無線基地台"]
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
