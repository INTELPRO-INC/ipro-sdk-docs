---
title: "Hardware"
description: Specifications, pin mapping and power measurement for IPRO chips and boards
migrate_from: []
---

# Hardware

Start here to look up chip specifications, pick a board, map pins or measure current. Examples default to the IPRO7AI Reef EVK.

## Chips { #chips }

<div class="grid cards" markdown>

-   :material-chip:{ .lg } **[IPRO7](chips/ipro7.md)**

    ---

    RISC-V RV32IMAFC, BLE 5.4 with LE Audio, ISP and a full set of peripherals; the main chip of this SDK release.

-   :material-brain:{ .lg } **[IPRO7AI](chips/ipro7ai.md)**

    ---

    The IPRO7 variant with the NPU enabled and PSRAM in the package, used by the camera object-detection and gesture examples.

-   :material-wifi:{ .lg } **[IPRO6S (V2.0.1)](chips/ipro6s.md)**

    ---

    Wi-Fi 6 plus BLE and BR/EDR. Stand-alone development uses SDK V2.0.1; this release ships the host side for using it as the Wi-Fi companion of an IPRO7.

</div>

## Boards { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **[IPRO7AI Reef EVK](boards/reef-evk.md)** <span class="ipro-badge">Recommended</span>

    ---

    IPRO7AI (QFN56) carrier: OV5640 camera, speaker and headphones, three audio inputs and an SD slot that also takes the IPRO6S FIN card for Wi-Fi.

-   :material-monitor-dashboard:{ .lg } **[IPRO7AI EVK](boards/ipro7ai-evk.md)**

    ---

    2.4" LCD, SC101IOT camera, PDM microphone, speaker and micro-SD, for vision AI and user-interface work.

-   :material-expansion-card:{ .lg } **[IPRO7 EVB](boards/ipro7-evb.md)**

    ---

    IPRO7 evaluation board with Ethernet, JTAG, USB and expansion headers; the default board of most application `.config` files.

</div>

## Pins and power { #pinout-power }

<div class="grid cards" markdown>

-   :material-table:{ .lg } **[Pinout & Peripheral Mapping](pinmux.md)**

    ---

    GPIO function select, UART / SPI / SDIO / I2S pins, alternate-function tables, board default pins and peripheral wiring.

-   :material-flash:{ .lg } **[Power & Current Measurement](power.md)**

    ---

    Board power trees, power design recommendations, and how to measure sleep current with `ipro_lp_test`.

</div>
