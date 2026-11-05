---
title: "硬件"
description: IPRO 芯片规格、IPRO7AI Reef EVK 开发板、引脚对照与电流测量
migrate_from: []
---

# 硬件

查阅芯片规格、IPRO7AI Reef EVK 的接线、引脚对照与电流测量时从这里开始。本站的上手步骤与示例都以 IPRO7AI Reef EVK V4.0 为准。

## 芯片 { #chips }

<div class="grid cards" markdown>

-   :material-chip:{ .lg } **[IPRO7](chips/ipro7.md)**

    ---

    RISC-V RV32IMAFC、BLE 5.4 与 LE Audio、IEEE 802.15.4、ISP 与硬件 MJPEG；本版本 37 个应用的目标芯片。

-   :material-brain:{ .lg } **[IPRO7AI](chips/ipro7ai.md)**

    ---

    启用 NPU、封装内含 8 MB PSRAM 的 IPRO7 型号；Reef EVK 上的主芯片。

-   :material-wifi:{ .lg } **[IPRO6S](chips/ipro6s.md)**

    ---

    内置 Wi-Fi 6 的 RISC-V SoC。本版本附带三个 IPRO6S Wi-Fi 应用；在 Reef 上它是插在 microSD 卡座中的 FIN Wi-Fi 卡。

</div>

## 开发板 { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **[IPRO7AI Reef EVK V4.0](boards/reef-evk.md)**

    ---

    IPRO7AI（QFN56）开发板：OV5640 摄像头排线座、PDM 麦克风、耳麦插孔与扬声器、microSD 卡座（可插 IPRO6S FIN 卡）、RGB LED、40-pin 扩展排针；仅由 USB-C 供电。

</div>

SDK 中另有以 IPRO7 EVB、IPRO7AI EVK、IPRO6S EVB 与 IPRO7 Arduino 板为目标的应用，见[示例](../examples/index.md)；这些开发板的供货请联系 INTELPRO。

## 引脚与电源 { #pinout-power }

<div class="grid cards" markdown>

-   :material-table:{ .lg } **[引脚与外设对照](pinmux.md)**

    ---

    GPIO 功能选择、UART／SPI／SDIO／I2S 引脚、复用功能表，以及 Reef 的默认引脚。

-   :material-flash:{ .lg } **[电源与功耗测量](power.md)**

    ---

    Reef 的供电方式、用 SW8 与 JP2 测量 IPRO7AI 电流的步骤，以及电源设计建议。

</div>
