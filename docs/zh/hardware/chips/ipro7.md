---
title: "IPRO7"
description: IPRO7 晶片的公開規格、記憶體配置、本版 SDK 支援範圍與搭載的開發板
migrate_from:
  - "hardware.html — IPRO7 晶片概覽、無線規格詳細、AI 與多媒體、介面規格"
---

# IPRO7

IPRO7 是 INTELPRO 的 2.4 GHz 低功耗無線 SoC：RISC-V RV32IMAFC 192 MHz 處理器、Bluetooth 5.4 與 LE Audio、IEEE 802.15.4 無線電、ISP 影像處理與硬體 MJPEG。本版 SDK 的 40 個應用中有 37 個以 IPRO7 為目標。啟用 NPU 的型號 [IPRO7AI](ipro7ai.md) 是 IPRO7AI Reef EVK 的主晶片。

<div class="ipro-facts" markdown>
<div><strong>192 MHz</strong><span>RISC-V RV32IMAFC</span></div>
<div><strong>256 KB</strong><span>OCRAM</span></div>
<div><strong>8 MB</strong><span>PSRAM（選配，IPRO7AI 內含）</span></div>
<div><strong>BLE 5.4</strong><span>LE Audio、802.15.4</span></div>
<div><strong>42</strong><span>GPIO（QFN56）</span></div>
</div>

## 概覽 { #chip-overview }

- **處理與記憶體**：RV32IMAFC（含 DSP 擴充）、256 KB OCRAM、4 KB 休眠保留 RAM，Flash 以 XIP 執行；可選配封裝內 8 MB PSRAM（IPRO7AI 型號內含）。
- **無線**：Bluetooth 5.4 LE 與 LE Audio、IEEE 802.15.4，整合 2.4 GHz RF 收發器。
- **影像與音訊**：DVP 相機介面、ISP、MJPEG 編解碼、音訊 ADC、GPDAC 與 I2S。
- **網路**：有線網路使用內建 EMAC（RMII）；無線網路經 SDIO 或 UART 外接無線電，例如經 SDIO 外接 IPRO6S，見[網路連線](#networking)。

## 主要規格 { #key-specs }

### 處理器與系統 { #cpu-memory }

| 項目 | 規格 |
|---|---|
| CPU | RISC-V RV32IMAFC，含 DSP 擴充指令，192 MHz |
| 快取 | L1 指令快取 16 KB／資料快取 16 KB |
| OCRAM | 256 KB |
| 休眠保留 RAM | 4 KB（HBN RAM） |
| ROM | 128 KB |
| eFuse | 2 Kb |
| PSRAM | 選配，封裝內 8 MB（IPRO7AI 型號內含）；QFN32 沒有 |
| Flash | XIP 執行；SDK 預設連結 1 MB 版面，以 `CONFIG_IPRO7_FLASH_2M` 等設定改用 2／4／8 MB |
| 計時 | RTC、Timer ×2、看門狗（WDT） |
| DMA | 8 通道 |
| 時脈 | 開發板使用 32 MHz 石英晶體，系統時脈由 PLL 產生 192 MHz |

### 無線 { #wireless }

| 項目 | 規格 |
|---|---|
| Bluetooth | Bluetooth 5.4 LE；1M／2M PHY 與 Long Range（Coded PHY，500／125 kbps） |
| LE Audio | CIS／BIS 等時通道；需使用 `bt54_iso2` 版本的 BLE 控制器 |
| 連線數 | 本版預編譯控制器最多 4 條連線（`link1_periph`／`link1`／`link2`／`link4`） |
| IEEE 802.15.4 | 802.15.4 無線電；SDK 在 Zephyr RTOS 下提供驅動與 OpenThread |
| RF | 2.4 GHz 收發器，整合 balun 與 PA／LNA；可控制外接 PA／LNA |

### 網路連線 { #networking }

有線網路使用晶片內的 EMAC（RMII 介面）。無線網路經 SDIO 或 UART 外接無線電，SDK 隨附下列驅動：

| 無線電 | 介面 | SDK 中的位置 |
|---|---|---|
| IPRO6S（Wi-Fi 6） | SDIO，lwIP 網路介面 `iproeth0` | `components/network/ipronet_host`；Reef 上是插在 microSD 卡座的 FIN 卡，見 [IPRO6S](ipro6s.md) |
| ATBM6162 | SDIO | `components/wireless/wifi_atbm6162`；`ipro_atbm_probe` |
| AIC8800 | SDIO（預編譯的廠商函式庫） | `components/wireless/wifi_aic8800`；`ipro_agora_sentino` 的 `config_evk` |
| ESP32 | UART AT 指令 | `components/network/esp32_wifi_at`；`ipro7_demo`（`CONFIG_ESP32_WIFI_AT`） |

### 多媒體與 AI { #ai-multimedia }

| 項目 | 規格 |
|---|---|
| 相機 | DVP 8-bit 與 SPI 相機介面；ISP 影像處理 |
| 視訊編碼 | 硬體 MJPEG 編解碼 |
| 顯示 | DBI／SPI 顯示介面 |
| 音訊輸入 | 音訊 ADC（AUADC）：PDM 數位麥克風與類比麥克風輸入，驅動提供 16／20 位元解析度 |
| 音訊輸出 | GPDAC 2 通道 10 位元；I2S |
| NPU | 0.1 TOPS，於 IPRO7AI 型號啟用，見 [IPRO7AI](ipro7ai.md) |

### 安全 { #security }

| 項目 | 規格 |
|---|---|
| 開機與除錯 | Secure Boot、Secure Debug |
| 加密引擎 | AES（ECB／CTR／CBC／XTS）、GMAC；SHA-1／224／256／384／512、MD5 |
| 公鑰運算 | PKA（RSA／ECC 加速） |
| 亂數 | TRNG |
| Flash 保護 | Flash 即時 AES 解密（OTFAD） |

### 周邊介面 { #interfaces }

| 介面 | 數量／規格 | 說明 |
|---|---|---|
| GPIO | 42（QFN56） | 每支 GPIO 以功能值 0–27 選擇用途，見 [腳位與周邊對照](../pinmux.md) |
| UART | ×2 | TX／RX／CTS／RTS 經 UART signal 繞到 GPIO |
| SPI | ×2 | 主／從模式，資料寬度 8／16／24／32 位元 |
| I2C | ×2 | 主／從模式 |
| I2S | ×1 | 主／從模式；標準、左對齊、右對齊、DSP 格式 |
| PWM | 4 通道 | 每通道 H／L 互補輸出 |
| GPADC | 12 個外部通道 | 12 位元，另有 14／16 位元（硬體平均）輸出 |
| GPDAC | 2 通道 | 10 位元；A 通道 GPIO23、B 通道 GPIO22 |
| QDEC | ×3 | 正交解碼（滑鼠、旋鈕） |
| KYS | ×1 | 鍵盤掃描 |
| IR | ×1 | 紅外線遙控接收 |
| USB | ×1 | USB 2.0 全速，裝置／主機 |
| SD／SDIO | ×1 | SD 主控（SDH），1／4-bit，固定在 GPIO28–33 |
| 乙太網路 | ×1 | EMAC，RMII 介面 |
| PIO | ×1 | 可程式化 IO |

### 封裝 { #packages }

| 封裝 | GPIO | 說明 |
|---|---|---|
| QFN56（7 × 7 mm） | 42（GPIO0–41） | 標準封裝；USB 在 GPIO8／9 |
| QFN32 | 較少（例如沒有 GPIO41） | 沒有封裝內 PSRAM，沒有 NPU |

## 記憶體配置 { #memory-map }

| 區域 | 大小 | 起始位址 | 說明 |
|---|---|---|---|
| Flash | 1 MB | `0x13000000` | XIP；以 `CONFIG_IPRO7_FLASH_2M` 等設定改用 2／4／8 MB |
| PSRAM | 8 MB | `0x1e000000` | AI／NPU 與 ISP 應用需要；在 `.config` 明確設定 `CONFIG_USE_PSRAM=y` |
| OCRAM | 256 KB | `0x11010000` | 堆疊、中斷與效能關鍵程式碼；BLE 控制器的 Exchange Memory 由頂端劃出。PDS31 睡眠時只保留前 64 KB，其餘只在 MISC 電源域保持供電時保留 |
| HBN RAM | 4 KB | `0x20090000` | 休眠期間保留 |

同時啟用 AI 與影像（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）時，連結器把 OCRAM 縮為 64 KB，見 [IPRO7AI](ipro7ai.md#memory)。

## 本版 SDK 支援 { #sdk-support }

| 項目 | V2.2.0 |
|---|---|
| FreeRTOS 應用 | 40 個應用中 37 個以 IPRO7 為目標：`CONFIG_IPRO7=y`、`CONFIG_CHIP="IPRO7"`、`CONFIG_CPU_ID="intelpro_ipro7"`；映像為 `<應用>_IPRO7.bin` |
| Zephyr RTOS | Zephyr v4.4.0 模組；板型 `ipro7_evb` 與 `ipro7ai_evk`，本版沒有 Reef 的 Zephyr 板型 |
| 工具鏈 | RISC-V GCC（`riscv64-unknown-elf-`，`rv32imafc`／`ilp32f`），不隨 SDK 提供，請向 INTELPRO 取得 |
| BLE | Zephyr v4.4.0 Host（原始碼）搭配 IPRO BLE 控制器（預編譯函式庫，16 個 IPRO7 版本：`link1_periph`／`link1`／`link2`／`link4` × `bt52`／`bt54_iso2` × 除錯／`_release`） |
| IEEE 802.15.4／Thread | 僅 Zephyr RTOS：IEEE 802.15.4 驅動與 OpenThread |
| Matter、Zigbee | 未包含於 V2.2.0，請洽 INTELPRO。 |
| 燒錄 | IntelProCube v0.6.3 命令列工具（另行取得）：`--chipname ipro7`；Reef 等 IPRO7AI 板用 `--chip-variant IPRO7AI` |

## 搭載 IPRO7 的開發板 { #boards }

| 開發板 | 晶片 | 板級設定 |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | IPRO7AI（QFN56，焊在板上） | `CONFIG_IPRO7AI_REEF=y`、`CONFIG_BOARD="IPRO7AI_REEF"` |

IPRO7 EVB（`CONFIG_EVB=y`）與 IPRO7AI EVK（`CONFIG_IPRO7AI_EVK=y`）是多數應用 `.config` 的預設板型；這些板子的供應請洽 INTELPRO。

## 相關文件 { #documents }

- [IPRO7AI](ipro7ai.md)：NPU 與 AI 範例。
- [腳位與周邊對照](../pinmux.md)、[電源與功耗量測](../power.md)。
- IPRO7 規格書與硬體設計指南：見 [文件下載](../../documents/index.md)。
