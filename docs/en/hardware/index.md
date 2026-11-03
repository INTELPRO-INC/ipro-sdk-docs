---
title: "Hardware"
description: IPRO chip specifications, the IPRO7AI Reef EVK, pin mapping and current measurement
migrate_from: []
---

# Hardware

Start here to look up chip specifications, wire up the IPRO7AI Reef EVK, map pins or measure current. Every step and example on this site targets the IPRO7AI Reef EVK V4.0.

## Chips { #chips }

<div class="grid cards" markdown>

-   :material-chip:{ .lg } **[IPRO7](chips/ipro7.md)**

    ---

    RISC-V RV32IMAFC, BLE 5.4 with LE Audio, IEEE 802.15.4, ISP and hardware MJPEG; the target of 37 applications in this release.

-   :material-brain:{ .lg } **[IPRO7AI](chips/ipro7ai.md)**

    ---

    The IPRO7 variant with the NPU enabled and 8 MB of PSRAM in the package; the main chip of the Reef EVK.

-   :material-wifi:{ .lg } **[IPRO6S](chips/ipro6s.md)**

    ---

    RISC-V SoC with built-in Wi-Fi 6. This release ships three IPRO6S Wi-Fi applications; on the Reef it is the FIN Wi-Fi card in the microSD slot.

</div>

## Boards { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **[IPRO7AI Reef EVK V4.0](boards/reef-evk.md)**

    ---

    IPRO7AI (QFN56) board: OV5640 camera connector, PDM microphone, headset jack and speaker, microSD slot (takes the IPRO6S FIN card), RGB LED and a 40-pin expansion header; powered from USB-C only.

</div>

The SDK also has applications for the IPRO7 EVB, the IPRO7AI EVK, the IPRO6S EVB and the IPRO7 Arduino board; see [Examples](../examples/index.md). Contact INTELPRO for these boards.

## Pins and power { #pinout-power }

<div class="grid cards" markdown>

-   :material-table:{ .lg } **[Pinout & Peripheral Mapping](pinmux.md)**

    ---

    GPIO function select, UART / SPI / SDIO / I2S pins, the alternate-function tables and the Reef's default pins.

-   :material-flash:{ .lg } **[Power & Current Measurement](power.md)**

    ---

    How the Reef is powered, measuring the IPRO7AI's current with SW8 and JP2, and power design recommendations.

</div>
