---
title: "IPRO7"
description: Public specifications, memory map, SDK support in this release and boards for the IPRO7 chip
migrate_from:
  - "hardware.html — IPRO7 晶片概覽、無線規格詳細、AI 與多媒體、介面規格"
---

# IPRO7

IPRO7 is INTELPRO's 2.4 GHz low-power wireless SoC: a 192 MHz RISC-V RV32IMAFC core, Bluetooth 5.4 with LE Audio, an IEEE 802.15.4 radio, an ISP and hardware MJPEG. Every application in this SDK release targets IPRO7. For the variant with the NPU enabled, see [IPRO7AI](ipro7ai.md).

<div class="ipro-facts" markdown>
<div><strong>192 MHz</strong><span>RISC-V RV32IMAFC</span></div>
<div><strong>256 KB</strong><span>OCRAM</span></div>
<div><strong>8 MB</strong><span>PSRAM (optional, built into IPRO7AI)</span></div>
<div><strong>BLE 5.4</strong><span>LE Audio, 802.15.4</span></div>
<div><strong>42</strong><span>GPIOs (QFN56)</span></div>
</div>

## Overview { #chip-overview }

- **Processing and memory**: RV32IMAFC with DSP extensions, 256 KB OCRAM, 4 KB of RAM retained in hibernate, code executed in place from flash; 8 MB of in-package PSRAM is optional (built into the IPRO7AI variant).
- **Wireless**: Bluetooth 5.4 LE with LE Audio and IEEE 802.15.4 on an integrated 2.4 GHz RF transceiver.
- **Imaging and audio**: DVP camera interface, ISP, MJPEG codec, audio ADC, GPDAC and I2S.
- **Networking**: wired networking uses the on-chip EMAC (RMII); for Wi-Fi, add an IPRO6S companion over SDIO, see [IPRO6S](ipro6s.md).

## Key specifications { #key-specs }

### Processor and system { #cpu-memory }

| Item | Specification |
|---|---|
| CPU | RISC-V RV32IMAFC with DSP extensions, 192 MHz |
| Cache | L1 instruction cache 16 KB / data cache 16 KB |
| OCRAM | 256 KB |
| Hibernate RAM | 4 KB (HBN RAM) |
| ROM | 128 KB |
| eFuse | 2 Kb |
| PSRAM | Optional, 8 MB in the package (built into the IPRO7AI variant); none on QFN32 |
| Flash | Execute in place; the SDK's default layout is 1 MB, and 2 / 4 / 8 MB with an external SF3 flash |
| Timing | RTC, 2 timers, watchdog (WDT) |
| DMA | 8 channels |
| Clock | 32 MHz crystal on the boards; the PLL generates the 192 MHz system clock |

### Wireless { #wireless }

| Item | Specification |
|---|---|
| Bluetooth | Bluetooth 5.4 LE; 1M / 2M PHY and Long Range (Coded PHY, 500 / 125 kbps) |
| LE Audio | CIS / BIS isochronous channels; needs the `bt54_iso2` build of the BLE controller |
| Connections | Up to 4 with this release's prebuilt controllers (`link1_periph` / `link1` / `link2` / `link4`) |
| IEEE 802.15.4 | 802.15.4 radio; the SDK provides the driver and OpenThread under Zephyr RTOS |
| RF | 2.4 GHz transceiver with integrated balun and PA / LNA; control lines for an external PA / LNA |
| Wi-Fi | None built in; add an IPRO6S companion over SDIO |

### Multimedia and AI { #ai-multimedia }

| Item | Specification |
|---|---|
| Camera | 8-bit DVP and SPI camera interfaces; ISP |
| Video | Hardware MJPEG encoder and decoder |
| Display | DBI / SPI display interfaces |
| Audio in | Audio ADC (AUADC) for PDM digital and analog microphones; the driver offers 16- and 20-bit resolution |
| Audio out | GPDAC, 2 channels, 10-bit; I2S |
| NPU | 0.1 TOPS, enabled on the IPRO7AI variant, see [IPRO7AI](ipro7ai.md) |

### Security { #security }

| Item | Specification |
|---|---|
| Boot and debug | Secure Boot, Secure Debug |
| Crypto engine | AES (ECB / CTR / CBC / XTS), GMAC; SHA-1 / 224 / 256 / 384 / 512, MD5 |
| Public key | PKA (RSA / ECC acceleration) |
| Random numbers | TRNG |
| Flash protection | On-the-fly AES decryption of flash (OTFAD) |

### Peripheral interfaces { #interfaces }

| Interface | Count / spec | Notes |
|---|---|---|
| GPIO | 42 (QFN56) | Each GPIO selects its role with a function value 0–27, see [Pinout & Peripheral Mapping](../pinmux.md) |
| UART | 2 | TX / RX / CTS / RTS reach the GPIOs through UART signals |
| SPI | 2 | Master / slave, 8 / 16 / 24 / 32-bit data |
| I2C | 2 | Master / slave |
| I2S | 1 | Master / slave; standard, left-justified, right-justified and DSP formats |
| PWM | 4 channels | Complementary H / L output per channel |
| GPADC | 12 external channels | 12-bit, plus 14- and 16-bit output with hardware averaging |
| GPDAC | 2 channels | 10-bit; channel A on GPIO23, channel B on GPIO22 |
| QDEC | 3 | Quadrature decoders (mouse, rotary knob) |
| KYS | 1 | Key scan |
| IR | 1 | Infrared remote receiver |
| USB | 1 | USB 2.0 full speed, device / host |
| SD / SDIO | 1 | SD host (SDH), 1 / 4-bit, fixed on GPIO28–33 |
| Ethernet | 1 | EMAC with RMII |
| PIO | 1 | Programmable IO |

### Packages { #packages }

| Package | GPIOs | Notes |
|---|---|---|
| QFN56 (7 × 7 mm) | 42 (GPIO0–41) | Standard package; USB on GPIO8 / 9 |
| QFN32 | Fewer (no GPIO41, for example) | No in-package PSRAM, no NPU |

## Memory map { #memory-map }

| Region | Size | Base address | Notes |
|---|---|---|---|
| Flash | 1 MB | `0x13000000` | Execute in place; with an external SF3 flash select 2 / 4 / 8 MB with `CONFIG_IPRO7_FLASH_2M` and its siblings |
| PSRAM | 8 MB | `0x1e000000` | Needed by AI / NPU and ISP applications; set `CONFIG_USE_PSRAM=y` explicitly in `.config` |
| OCRAM | 256 KB | `0x11010000` | Stacks, interrupt handling and time-critical code; the BLE controller's Exchange Memory is taken from the top |
| HBN RAM | 4 KB | `0x20090000` | Retained in hibernate |

With AI and imaging both enabled the usable OCRAM region shrinks; see [Build System & Configuration](../../guides/build-system.md#memory-layout).

## SDK support in this release { #sdk-support }

| Item | V2.1.0 |
|---|---|
| FreeRTOS applications | All 35 target IPRO7: `CONFIG_IPRO7=y`, `CONFIG_CHIP="IPRO7"`, `CONFIG_CPU_ID="intelpro_ipro7"` |
| Zephyr RTOS | Zephyr v4.4.0 module; boards `ipro7_evb` and `ipro7ai_evk` |
| Toolchain | RISC-V GCC (`riscv64-unknown-elf-`, `rv32imafc` / `ilp32f`); not part of the SDK, obtain it from INTELPRO |
| BLE | Zephyr v4.4.0 host (source) on the IPRO BLE controller (prebuilt library, 16 IPRO7 builds) |
| IEEE 802.15.4 / Thread | Zephyr RTOS only: IEEE 802.15.4 driver and OpenThread |
| Matter, Zigbee | Not included in V2.1.0; contact INTELPRO. |
| Flashing | IntelProCube v0.6.3 command-line tool (obtained separately): `--chipname ipro7`, with `--chip-variant IPRO7` for the IPRO7 EVB and `--chip-variant IPRO7AI` for IPRO7AI boards |

## Boards with IPRO7 { #boards }

| Board | Chip | Board configuration |
|---|---|---|
| [IPRO7AI Reef EVK](../boards/reef-evk.md) | IPRO7AI (QFN56, soldered on the carrier) | `CONFIG_IPRO7AI_REEF=y` |
| [IPRO7AI EVK](../boards/ipro7ai-evk.md) | IPRO7AI | `CONFIG_IPRO7AI_EVK=y` |
| [IPRO7 EVB](../boards/ipro7-evb.md) | IPRO7 (QFN56 socket) | `CONFIG_EVB=y` |

## Related documents { #documents }

- [IPRO7AI](ipro7ai.md): the NPU and the AI examples.
- [Pinout & Peripheral Mapping](../pinmux.md), [Power & Current Measurement](../power.md).
- IPRO7 datasheet and hardware design guide: see [Documents](../../documents/index.md).
