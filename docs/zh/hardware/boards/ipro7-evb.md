---
title: "IPRO7 EVB"
description: IPRO7 EVB 的板上功能、接頭、預設腳位、上手步驟、支援範例與 SDK 板級支援
migrate_from:
  - "hardware.html — 評估板 (EVB)／IPRO7-SEVB V1、IPRO7-SEVB 電源架構、EVB 預設 Pin 配置總覽"
not_migrated:
  - "hardware.html#evb — 開發用驗證平台卡片"
---

# IPRO7 EVB

IPRO7 EVB 是 IPRO7 的評估板：QFN56 晶片插座、12 V DC 供電、乙太網路、JTAG、USB、DVP 相機與 GPIO 擴充接頭。多數應用的 `.config` 以它為預設板型（`CONFIG_EVB=y`），Zephyr 板型 `ipro7_evb` 也對應這塊板。

<div class="ipro-facts" markdown>
<div><strong>IPRO7</strong><span>QFN56 插座</span></div>
<div><strong>12 V</strong><span>DC 輸入（J1）</span></div>
<div><strong>J19</strong><span>UART 主控台</span></div>
<div><strong>J23</strong><span>JTAG</span></div>
<div><strong>RJ45</strong><span>10/100 Mbps 乙太網路</span></div>
</div>

## 板上功能 { #evb }

| 區塊 | 內容 |
|---|---|
| 電源 | 12 V DC 輸入（J1），多級穩壓產生 5 V、3.3 V、1.8 V、1.5 V、0.9 V；輸入端有 TVS 保護 |
| 核心 | IPRO7 QFN56 插座，32 MHz 石英晶體 |
| 天線 | 板載 PCB 天線；U.FL 天線座（J118–J122） |
| 除錯 | JTAG（J23，GPIO0／1／2／11）、UART 主控台（J19，UART0 GPIO20／21）、USB 2.0（J40） |
| 相機 | DVP 接頭（J27），8-bit 資料（D0–D7）、PCLK／VSYNC／HSYNC |
| 音訊 | DAC 喇叭輸出，擴大機致能 GPIO22（低電位開啟）；I2S 介面 |
| 網路 | RJ45 乙太網路，10/100 Mbps |
| 儲存 | micro-SD（GPIO28–33） |
| 擴充 | GPIO 擴充接頭（J56–J63）；PWM 與馬達控制介面 |

### 主要接頭 { #connectors }

| 接頭 | 用途 |
|---|---|
| J1 | 12 V DC 電源輸入 |
| J2 | 系統電源輸出 |
| J12、J13、J17 | USB |
| J19 | UART 主控台 |
| J23 | JTAG 除錯 |
| J27 | DVP 相機 |
| J40 | USB 2.0 |
| J56–J63 | GPIO 擴充 |
| J118–J122 | U.FL 天線座 |
| RJ45 | 乙太網路 |

!!! note "供電"
    以 J1 接 12 V DC 變壓器。各電源軌的電壓與用途見 [電源與功耗量測](../power.md#evb-power)。

## 預設腳位 { #default-pins }

板級設定在開機時設定下列腳位，其餘腳位維持重置狀態，由應用或驅動自行設定：

| 腳位 | 用途 |
|---|---|
| GPIO0、GPIO1、GPIO2、GPIO11 | JTAG（功能 14） |
| GPIO15 | GPIO 輸出，開機時為低電位；`ipro7_sdio_wifi` 用它控制 SDIO Wi-Fi 夥伴晶片的電源 |
| GPIO20、GPIO21 | UART0 TX／RX（主控台） |
| GPIO28–GPIO33 | SD 卡（功能 27）；設定 `CONFIG_DISABLE_SDC_PINMUX` 時改給外接 SF3 Flash |

各腳位的上下拉與驅動強度、未佔用的 GPIO 清單，見 [腳位與周邊對照](../pinmux.md#evb-default-pins)。

## 上手 { #quick-start }

以 BLE 參考應用 `ipro_ble_remote` 為例。

<div class="ipro-steps" markdown>

1. **接線**：J1 接 12 V DC，USB 轉 UART 線接到 J19。

2. **指定燒錄工具**：`build_freertos.sh` 從 `IPRO_FLASH_TOOL` 或 `PATH` 尋找 IntelProCube 命令列工具。

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube 目錄>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube 目錄>/ipro_iot_tool_linux
        ```

3. **建置、燒錄並開啟主控台**

    ```bash
    ./build_freertos.sh build flash monitor -p /dev/cu.usbserial-XXXX ipro_ble_remote
    ```

    `flash` 會先在主控台以 115200 baud 送出 `reboot_dl` 讓板子進入下載模式（板上沒有可回應的韌體時，改以 BOOT 腳位手動進入），再以 921600 baud 燒錄，並以輸出中的 `[All Success]` 判斷成功；`monitor` 以 115200 baud 開啟主控台。

    `build_freertos.sh` 不帶 `--chip-variant`，沿用工具設定檔中的 Flash 腳位。EVB 使用 `IPRO7`（`flash_pin` 為 `0x2`）。若同一套 IntelProCube 曾以 `--chip-variant IPRO7AI` 燒錄 Reef 或 EVK，先在 IntelProCube 目錄直接燒錄一次（macOS 為例，其他作業系統見[燒錄與序列埠](../../get-started/flash-and-monitor.md#flashing)）：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7 \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build/build_out/ipro_ble_remote_IPRO7.bin
    ```

4. **確認結果**：主控台出現開機訊息；用手機的 BLE 掃描 App 可以看到 `IPRO-Remote`。

</div>

## 支援的範例 { #examples }

`.config` 預設為 EVB 的應用：

| 類別 | 範例 |
|---|---|
| 平台參考 | `ipro7_demo`（整顆晶片的周邊與系統展示）、`ipro7_sdio_wifi`（經 SDIO 外接 IPRO6S 的 Wi-Fi 主機） |
| BLE | `ipro_ble_remote`、`ipro_ble_transparent`、`ipro_ble_hid_keyboard`、`ipro_throughput_test` |
| 音訊 | `ipro_le_audio_headset`、`ipro_pdm_mic_demo`（外接 PDM 麥克風於 GPIO0／1） |
| 相機 | `ipro7_uvc_cam`（SC101IOT 感測器、ISP、硬體 MJPEG、USB Video Class） |
| AI | `ipro_npu_yolo`、`ipro_ai_bench`、`ipro_ai_link`、`ipro_tflm_test`、`ipro_tflm_yolo`、`ipro_nmsis_nn_test`、`ipro_tinymaix_demo` |
| 顯示與感測器 | `ipro_gh7007_test`、`ipro_gh7007_video`、`ipro_epd_test`、`ipro_epd_el036`、`mpu6500_test` |
| 儲存與低功耗 | `ipro_pio_sdh_test`、`ipro_lp_test` |
| 單元測試 | `ipro_unit_test` |

## SDK 板級支援 { #bsp }

- **板級設定**：`CONFIG_EVB=y`、`CONFIG_BOARD="EVB"`，設定檔 `bsp/board/ipro7/ipro7_evb_board_config.h`。系統時脈為 32 MHz 晶體經 PLL 產生 192 MHz。
- **Flash 版面**：預設 1 MB（`CONFIG_IPRO7_FLASH_1M`）。外接 SF3 Flash 時以 `CONFIG_IPRO7_FLASH_2M` 等鍵選 2／4／8 MB，並設定 `CONFIG_DISABLE_SDC_PINMUX` 把 GPIO28–33 交給 Flash。
- **PSRAM**：需要 PSRAM 的應用在 `.config` 寫入 `CONFIG_USE_PSRAM=y`。
- **喇叭擴大機**：EVB 的擴大機致能為低電位開啟（`BOARD_SPK_EN_ACTIVE` 預設 0），`components/audio` 的 DAC 輸出預設使用 GPIO22。
- **Zephyr RTOS**：板型 `ipro7_evb`，主控台 2000000 baud；`west flash` 對此板預設使用 `partition_cfg_2M.toml`。

## 相關文件 { #documents }

- [腳位與周邊對照](../pinmux.md)：功能選擇、替代功能與 EVB 預設腳位。
- [電源與功耗量測](../power.md#evb-power)：EVB 電源軌。
- [IPRO7](../chips/ipro7.md)：晶片規格。
- 板卡使用手冊與 IPRO7 硬體設計指南：見 [文件下載](../../documents/index.md)。
