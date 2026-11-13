---
title: "硬體"
description: IPRO 晶片規格、IPRO7AI Reef EVK 開發板、腳位對照與電流量測
migrate_from: []
---

# 硬體

查晶片規格、IPRO7AI Reef EVK 的接線、腳位對照與電流量測時從這裡開始。本站的上手步驟與範例都以 IPRO7AI Reef EVK V4.0 為準。

## 晶片 { #chips }

<div class="grid cards" markdown>

-   :material-chip:{ .lg } **[IPRO7](chips/ipro7.md)**

    ---

    RISC-V RV32IMAFC、BLE 5.4 與 LE Audio、IEEE 802.15.4、ISP 與硬體 MJPEG；本版 38 個應用的目標晶片。

-   :material-brain:{ .lg } **[IPRO7AI](chips/ipro7ai.md)**

    ---

    啟用 NPU、封裝內含 8 MB PSRAM 的 IPRO7 型號；Reef EVK 上的主晶片。

-   :material-wifi:{ .lg } **[IPRO6S](chips/ipro6s.md)**

    ---

    內建 Wi-Fi 的 RISC-V SoC。本版隨附三個 IPRO6S Wi-Fi 應用；在 Reef 上它是插在 microSD 卡座的 FIN Wi-Fi 卡。

</div>

## 開發板 { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **[IPRO7AI Reef EVK V4.0](boards/reef-evk.md)**

    ---

    IPRO7AI（QFN56）開發板：OV5640 相機排線座、PDM 麥克風、耳麥孔與喇叭、microSD 卡座（可插 IPRO6S FIN 卡）、RGB LED、40-pin 擴充排針；只由 USB-C 供電。

</div>

SDK 中另有以 IPRO7 EVB、IPRO7AI EVK、IPRO6S EVK 與 IPRO7 Arduino 板為目標的應用，見[範例](../examples/index.md)；這些板子的供應請洽 INTELPRO。

## 腳位與電源 { #pinout-power }

<div class="grid cards" markdown>

-   :material-table:{ .lg } **[腳位與周邊對照](pinmux.md)**

    ---

    GPIO 功能選擇、UART／SPI／SDIO／I2S 腳位、替代功能表，以及 Reef 的預設腳位。

-   :material-flash:{ .lg } **[電源與功耗量測](power.md)**

    ---

    Reef 的供電方式、以 SW8 與 JP2 量測 IPRO7AI 電流的步驟，以及電源設計建議。

</div>
