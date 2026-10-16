---
title: "硬體"
description: IPRO 晶片與開發板的規格、腳位對照與電源量測
migrate_from: []
---

# 硬體

查晶片規格、選開發板、對照腳位與量測電流時從這裡開始；範例預設使用 IPRO7AI Reef EVK。

## 晶片 { #chips }

<div class="grid cards" markdown>

-   :material-chip:{ .lg } **[IPRO7](chips/ipro7.md)**

    ---

    RISC-V RV32IMAFC、BLE 5.4 與 LE Audio、ISP 與周邊介面；本版 SDK 的主要晶片。

-   :material-brain:{ .lg } **[IPRO7AI](chips/ipro7ai.md)**

    ---

    啟用 NPU 並內含 PSRAM 的 IPRO7 型號，用於相機影像辨識與手勢分類範例。

-   :material-wifi:{ .lg } **[IPRO6S（V2.0.1）](chips/ipro6s.md)**

    ---

    Wi-Fi 6 與 BLE／BR/EDR 晶片；獨立開發使用 SDK V2.0.1。本版提供 IPRO7 經 SDIO 把它當作 Wi-Fi 夥伴晶片的主機端。

</div>

## 開發板 { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **[IPRO7AI Reef EVK](boards/reef-evk.md)** <span class="ipro-badge">推薦</span>

    ---

    IPRO7AI（QFN56）載板：OV5640 相機、喇叭與耳機、三種收音、SD 卡槽，可插 IPRO6S FIN 卡擴充 Wi-Fi。

-   :material-monitor-dashboard:{ .lg } **[IPRO7AI EVK](boards/ipro7ai-evk.md)**

    ---

    2.4 吋 LCD、SC101IOT 相機、PDM 麥克風、喇叭與 micro-SD，適合影像 AI 與人機介面。

-   :material-expansion-card:{ .lg } **[IPRO7 EVB](boards/ipro7-evb.md)**

    ---

    IPRO7 評估板：乙太網路、JTAG、USB 與擴充接頭；多數應用 `.config` 的預設板型。

</div>

## 腳位與電源 { #pinout-power }

<div class="grid cards" markdown>

-   :material-table:{ .lg } **[腳位與周邊對照](pinmux.md)**

    ---

    GPIO 功能選擇、UART／SPI／SDIO／I2S 腳位、替代功能表、開發板預設腳位與周邊接線。

-   :material-flash:{ .lg } **[電源與功耗量測](power.md)**

    ---

    各開發板的電源架構、電源設計建議，以及用 `ipro_lp_test` 量測睡眠電流的步驟。

</div>
