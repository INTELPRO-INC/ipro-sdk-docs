---
title: Documents
description: The formal IPRO7 / IPRO7AI chip, software and board documents, with version, languages and contents.
generated: tools/gen_documents.py
migrate_from: []
---

# Documents

The formal documents INTELPRO provides for IPRO7 and IPRO7AI, matching SDK V2.1. Every document is available in Traditional Chinese and English.

!!! info "How to get them"
    For documents marked "On request", contact INTELPRO and name the document, version and language.

## Chip documents { #chip-documents }

| Document | Version | Languages | Contents | Availability |
|---|---|---|---|---|
| IPRO7 Product Brief | V1.0 | zh-TW / English | Feature overview, block diagram, target applications, package and ordering information | On request |
| IPRO7 Datasheet | V1.6 | zh-TW / English | Functional description, pin definitions and GPIO pin multiplexing, AI / NPU, electrical specifications, marking and ordering information | On request |
| IPRO7 Reference Manual | V1.3 | zh-TW / English | System and memory, reset and clocks, and the registers of GPIO, ADC, DMA, SPI, UART, I2C, PWM, timers, audio ADC, KeyScan, low power, the security engine and MJPEG | On request |
| IPRO7 Hardware Design Guide | V1.1 | zh-TW / English | SoC hardware reference, plus power, PCB routing, clock circuits, boot mode and strap pins, interface reference designs, package footprint and the SoM reference design | On request |
| IPRO7 Application Note: Power-up Verification | V1.1 | zh-TW / English | Power architecture and power-on sequence, test points, measurement procedure and acceptance criteria, checklist | On request |

## Software documents { #software-documents }

| Document | Version | Languages | Contents | Availability |
|---|---|---|---|---|
| IPRO7 SDK Installation Guide | V1.1 | zh-TW / English | Installer and installation modes, editor setup, single-package updates and offline installation, first build, flashing and console baud rate | On request |
| IPRO7 Programming Guide | V1.1 | zh-TW / English | Development environment, SDK architecture, build system, FreeRTOS, peripherals, BLE, Wi-Fi through an external companion chip, multimedia, USB, security engine, power management, OTA, debugging and logging | On request |
| IPRO7 API Specification | V1.1 | zh-TW / English | APIs for the HAL, USB, security engine, BLE, Wi-Fi through an external companion chip, file system, OS abstraction layer and AI / NPU runtime, plus error codes | On request |
| IPRO7 Software Tools User Guide | V1.1 | zh-TW / English | RISC-V toolchain, build and configuration system, flashing and download tool, debugging tools, serial monitoring, BLE tools, RF tuning tool, image tools, memory and size analysis | On request |
| IPRO7AI AI Studio User Guide | V1.3 | zh-TW / English | Model preparation and compilation, NPU dispatch inspection, numerical verification, running on board and the operator support matrix | On request |

## Board documents { #board-documents }

| Document | Version | Languages | Contents | Availability |
|---|---|---|---|---|
| IPRO7AI Reef EVK Board User Guide | V1.2 | zh-TW / English | System architecture, board overview, quick start, jumpers and buttons, interfaces, power, programming and debug, SDK examples | On request |
| IPRO Debug Probe Board User Guide | V1.1 | zh-TW / English | Board overview, quick start, button and LED, UART and JTAG / CCI interfaces, power, host setup, programming and debug, BOM and fabrication data | On request |

For board bring-up steps see [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md); for the SDK's API index see [API Reference](../reference/api/index.md).
