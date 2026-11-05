---
title: "IPRO7"
description: IPRO7 芯片的公开规格、内存映射、本版本 SDK 的支持范围与搭载该芯片的开发板
migrate_from:
  - "hardware.html — IPRO7 晶片概覽、無線規格詳細、AI 與多媒體、介面規格"
---

# IPRO7

IPRO7 是 INTELPRO 的 2.4 GHz 低功耗无线 SoC：RISC-V RV32IMAFC 192 MHz 处理器、Bluetooth 5.4 与 LE Audio、IEEE 802.15.4 无线电、ISP 图像处理与硬件 MJPEG。本版本 SDK 的 40 个应用中有 37 个以 IPRO7 为目标。启用 NPU 的型号 [IPRO7AI](ipro7ai.md) 是 IPRO7AI Reef EVK 的主芯片。

<div class="ipro-facts" markdown>
<div><strong>192 MHz</strong><span>RISC-V RV32IMAFC</span></div>
<div><strong>256 KB</strong><span>OCRAM</span></div>
<div><strong>8 MB</strong><span>PSRAM（可选，IPRO7AI 内含）</span></div>
<div><strong>BLE 5.4</strong><span>LE Audio、802.15.4</span></div>
<div><strong>42</strong><span>GPIO（QFN56）</span></div>
</div>

## 概览 { #chip-overview }

- **处理与内存**：RV32IMAFC（含 DSP 扩展）、256 KB OCRAM、4 KB 休眠保持 RAM，Flash 以 XIP 方式执行；可选封装内 8 MB PSRAM（IPRO7AI 型号内含）。
- **无线**：Bluetooth 5.4 LE 与 LE Audio、IEEE 802.15.4，集成 2.4 GHz RF 收发器。
- **图像与音频**：DVP 摄像头接口、ISP、MJPEG 编解码、音频 ADC、GPDAC 与 I2S。
- **网络**：有线网络使用内置 EMAC（RMII）；无线网络经 SDIO 或 UART 外接无线模块，例如经 SDIO 外接 IPRO6S，见[网络连接](#networking)。

## 主要规格 { #key-specs }

### 处理器与系统 { #cpu-memory }

| 项目 | 规格 |
|---|---|
| CPU | RISC-V RV32IMAFC，含 DSP 扩展指令，192 MHz |
| 缓存 | L1 指令缓存 16 KB／数据缓存 16 KB |
| OCRAM | 256 KB |
| 休眠保持 RAM | 4 KB（HBN RAM） |
| ROM | 128 KB |
| eFuse | 2 Kb |
| PSRAM | 可选，封装内 8 MB（IPRO7AI 型号内含）；QFN32 没有 |
| Flash | XIP 执行；SDK 默认按 1 MB 布局链接，用 `CONFIG_IPRO7_FLASH_2M` 等配置改用 2／4／8 MB |
| 计时 | RTC、Timer ×2、看门狗（WDT） |
| DMA | 8 通道 |
| 时钟 | 开发板使用 32 MHz 晶振，系统时钟由 PLL 产生 192 MHz |

### 无线 { #wireless }

| 项目 | 规格 |
|---|---|
| Bluetooth | Bluetooth 5.4 LE；1M／2M PHY 与 Long Range（Coded PHY，500／125 kbps） |
| LE Audio | CIS／BIS 等时通道；需使用 `bt54_iso2` 版本的 BLE 控制器 |
| 连接数 | 本版本预编译控制器最多 4 个连接（`link1_periph`／`link1`／`link2`／`link4`） |
| IEEE 802.15.4 | 802.15.4 无线电；SDK 在 Zephyr RTOS 下提供驱动与 OpenThread |
| RF | 2.4 GHz 收发器，集成 balun 与 PA／LNA；可控制外接 PA／LNA |

### 网络连接 { #networking }

有线网络使用芯片内的 EMAC（RMII 接口）。无线网络经 SDIO 或 UART 外接无线模块，SDK 附带下列驱动：

| 无线模块 | 接口 | SDK 中的位置 |
|---|---|---|
| IPRO6S（Wi-Fi 6） | SDIO，lwIP 网络接口 `iproeth0` | `components/network/ipronet_host`；Reef 上是插在 microSD 卡座中的 FIN 卡，见 [IPRO6S](ipro6s.md) |
| ATBM6162 | SDIO | `components/wireless/wifi_atbm6162`；`ipro_atbm_probe` |
| AIC8800 | SDIO（预编译的厂商库） | `components/wireless/wifi_aic8800`；`ipro_agora_sentino` 的 `config_evk` |
| ESP32 | UART AT 指令 | `components/network/esp32_wifi_at`；`ipro7_demo`（`CONFIG_ESP32_WIFI_AT`） |

### 多媒体与 AI { #ai-multimedia }

| 项目 | 规格 |
|---|---|
| 摄像头 | DVP 8 位与 SPI 摄像头接口；ISP 图像处理 |
| 视频编码 | 硬件 MJPEG 编解码 |
| 显示 | DBI／SPI 显示接口 |
| 音频输入 | 音频 ADC（AUADC）：PDM 数字麦克风与模拟麦克风输入，驱动提供 16／20 位分辨率 |
| 音频输出 | GPDAC 2 通道 10 位；I2S |
| NPU | 0.1 TOPS，在 IPRO7AI 型号上启用，见 [IPRO7AI](ipro7ai.md) |

### 安全 { #security }

| 项目 | 规格 |
|---|---|
| 启动与调试 | Secure Boot、Secure Debug |
| 加密引擎 | AES（ECB／CTR／CBC／XTS）、GMAC；SHA-1／224／256／384／512、MD5 |
| 公钥运算 | PKA（RSA／ECC 加速） |
| 随机数 | TRNG |
| Flash 保护 | Flash 实时 AES 解密（OTFAD） |

### 外设接口 { #interfaces }

| 接口 | 数量／规格 | 说明 |
|---|---|---|
| GPIO | 42（QFN56） | 每个 GPIO 用功能值 0–27 选择用途，见 [引脚与外设对照](../pinmux.md) |
| UART | ×2 | TX／RX／CTS／RTS 经 UART signal 路由到 GPIO |
| SPI | ×2 | 主／从模式，数据宽度 8／16／24／32 位 |
| I2C | ×2 | 主／从模式 |
| I2S | ×1 | 主／从模式；标准、左对齐、右对齐、DSP 格式 |
| PWM | 4 通道 | 每通道 H／L 互补输出 |
| GPADC | 12 个外部通道 | 12 位，另有 14／16 位（硬件平均）输出 |
| GPDAC | 2 通道 | 10 位；A 通道 GPIO23、B 通道 GPIO22 |
| QDEC | ×3 | 正交解码（鼠标、旋钮） |
| KYS | ×1 | 键盘扫描 |
| IR | ×1 | 红外遥控接收 |
| USB | ×1 | USB 2.0 全速，设备／主机 |
| SD／SDIO | ×1 | SD 主控（SDH），1／4-bit，固定在 GPIO28–33 |
| 以太网 | ×1 | EMAC，RMII 接口 |
| PIO | ×1 | 可编程 IO |

### 封装 { #packages }

| 封装 | GPIO | 说明 |
|---|---|---|
| QFN56（7 × 7 mm） | 42（GPIO0–41） | 标准封装；USB 在 GPIO8／9 |
| QFN32 | 较少（例如没有 GPIO41） | 没有封装内 PSRAM，没有 NPU |

## 内存映射 { #memory-map }

| 区域 | 大小 | 起始地址 | 说明 |
|---|---|---|---|
| Flash | 1 MB | `0x13000000` | XIP；用 `CONFIG_IPRO7_FLASH_2M` 等配置改用 2／4／8 MB |
| PSRAM | 8 MB | `0x1e000000` | AI／NPU 与 ISP 应用需要；在 `.config` 中显式设置 `CONFIG_USE_PSRAM=y` |
| OCRAM | 256 KB | `0x11010000` | 栈、中断与性能关键代码；BLE 控制器的 Exchange Memory 从顶端划出。PDS31 睡眠时只保持前 64 KB，其余部分只在 MISC 电源域保持供电时保持 |
| HBN RAM | 4 KB | `0x20090000` | 休眠期间保持 |

同时启用 AI 与图像（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）时，链接器把 OCRAM 缩减为 64 KB，见 [IPRO7AI](ipro7ai.md#memory)。

## 本版本 SDK 支持 { #sdk-support }

| 项目 | V2.2.0 |
|---|---|
| FreeRTOS 应用 | 40 个应用中 37 个以 IPRO7 为目标：`CONFIG_IPRO7=y`、`CONFIG_CHIP="IPRO7"`、`CONFIG_CPU_ID="intelpro_ipro7"`；镜像为 `<应用>_IPRO7.bin` |
| Zephyr RTOS | Zephyr v4.4.0 模块；板型 `ipro7_evb` 与 `ipro7ai_evk`，本版本没有 Reef 的 Zephyr 板型 |
| 工具链 | RISC-V GCC（`riscv64-unknown-elf-`，`rv32imafc`／`ilp32f`），不随 SDK 提供，请向 INTELPRO 获取 |
| BLE | Zephyr v4.4.0 Host（源代码）搭配 IPRO BLE 控制器（预编译库，16 个 IPRO7 版本：`link1_periph`／`link1`／`link2`／`link4` × `bt52`／`bt54_iso2` × 调试／`_release`） |
| IEEE 802.15.4／Thread | 仅 Zephyr RTOS：IEEE 802.15.4 驱动与 OpenThread |
| Matter、Zigbee | 未包含在 V2.2.0 中，请联系 INTELPRO。 |
| 烧录 | IntelProCube v0.6.3 命令行工具（需另行获取）：`--chipname ipro7`；Reef 等 IPRO7AI 开发板用 `--chip-variant IPRO7AI` |

## 搭载 IPRO7 的开发板 { #boards }

| 开发板 | 芯片 | 板级配置 |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | IPRO7AI（QFN56，焊在板上） | `CONFIG_IPRO7AI_REEF=y`、`CONFIG_BOARD="IPRO7AI_REEF"` |

IPRO7 EVB（`CONFIG_EVB=y`）与 IPRO7AI EVK（`CONFIG_IPRO7AI_EVK=y`）是多数应用 `.config` 的默认板型；这些开发板的供货请联系 INTELPRO。

## 相关文档 { #documents }

- [IPRO7AI](ipro7ai.md)：NPU 与 AI 示例。
- [引脚与外设对照](../pinmux.md)、[电源与功耗测量](../power.md)。
- IPRO7 规格书与硬件设计指南：见 [文档下载](../../documents/index.md)。
