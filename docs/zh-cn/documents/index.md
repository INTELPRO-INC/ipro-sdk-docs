---
title: 文档下载
description: IPRO7／IPRO7AI 正式芯片、软件与开发板文档清单，含版本、语言与涵盖内容。
generated: tools/gen_documents.py
migrate_from: []
---

# 文档下载

INTELPRO 为 IPRO7 与 IPRO7AI 提供的正式文档，软件文档对应 SDK V2.1 与 IPRO AI Teach 2.0，IPRO Workbench 操作手册对应 IPRO Workbench 0.1.1。各文档提供的语言列于表中。

!!! info "获取方式"
    标注“向 INTELPRO 索取”的文档，请向 INTELPRO 索取，并注明文档名称、版本与语言。

## 芯片文档 { #chip-documents }

| 文档 | 版本 | 语言 | 内容 | 获取方式 |
|---|---|---|---|---|
| IPRO7 产品简介 | V1.0 | 繁体中文／English | 功能概要、框图、目标应用、封装与订购信息 | 向 INTELPRO 索取 |
| IPRO7 数据手册 | V1.6 | 繁体中文／English | 功能描述、引脚定义与 GPIO 引脚复用、AI／NPU、电气规格、标识与订购信息 | 向 INTELPRO 索取 |
| IPRO7 寄存器参考手册 | V1.3 | 繁体中文／English | 系统与内存、复位与时钟，以及 GPIO、ADC、DMA、SPI、UART、I2C、PWM、定时器、音频 ADC、KeyScan、低功耗、安全引擎与 MJPEG 的寄存器 | 向 INTELPRO 索取 |
| IPRO7 硬件设计指南 | V1.1 | 繁体中文／English | SoC 硬件参考，以及电源、PCB 布线、时钟电路、启动模式与 strap 引脚、接口参考设计、封装 footprint 与 SoM 参考设计 | 向 INTELPRO 索取 |
| IPRO7 应用笔记：电源上电验证 | V1.1 | 繁体中文／English | 电源架构与上电时序、测试点、测量步骤与验收标准、检查表 | 向 INTELPRO 索取 |

## 软件文档 { #software-documents }

| 文档 | 版本 | 语言 | 内容 | 获取方式 |
|---|---|---|---|---|
| IPRO7 SDK 安装指南 | V1.1 | 繁体中文／English | 安装程序与安装模式、编辑器设置、单个软件包更新与离线安装、首次构建、烧录与串口波特率 | 向 INTELPRO 索取 |
| IPRO7 编程指南 | V1.1 | 繁体中文／English | 开发环境、SDK 架构、构建系统、FreeRTOS、各外设、BLE、经 SDIO 外接的 Wi-Fi、多媒体、USB、安全引擎、电源管理、OTA、调试与日志 | 向 INTELPRO 索取 |
| IPRO7 API 规格书 | V1.1 | 繁体中文／English | HAL、USB、安全引擎、BLE、经 SDIO 外接的 Wi-Fi、文件系统、OS 抽象层与 AI／NPU 运行环境的 API，以及错误码 | 向 INTELPRO 索取 |
| IPRO7 软件工具使用指南 | V1.1 | 繁体中文／English | RISC-V 工具链、构建与配置系统、烧录与下载工具、调试工具、串口监视、BLE 工具、RF 调校工具、镜像文件工具、内存与大小分析 | 向 INTELPRO 索取 |
| IPRO7AI Edge AI 编程指南 | V1.2 | 繁体中文 | Edge AI 平台 V2.0 的运行层、模型存储、数据源、预处理、应用框架与事件、设备协议、主机端 SDK 与命令行 | 向 INTELPRO 索取 |
| IPRO7AI AI Studio 使用指南 | V1.3 | 繁体中文／English | 模型准备与编译、NPU 任务分派查看、数值验证、上板运行与算子支持表 | 向 INTELPRO 索取 |
| IPRO Workbench 操作手册 | V1.2 | 繁体中文／English | IPRO Workbench 0.1.1 的安装、首次运行、开发与设置、烧录（含 IPRO6S EVK）、串口监视、调试、板上测试与测量（含 Wi-Fi 传输速率）、AI 助手与故障排除 | [繁体中文](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.1.1/IPRO-Workbench-Operation-Manual-V1.2-zh-TW.pdf)／[English](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.1.1/IPRO-Workbench-Operation-Manual-V1.2-en.pdf) |

## 开发板文档 { #board-documents }

| 文档 | 版本 | 语言 | 内容 | 获取方式 |
|---|---|---|---|---|
| IPRO7AI Reef 开发套件使用手册 | V1.1 | 繁体中文 | V4.0 开发板硬件、接口与供电；烧录；IPRO AI Teach 2.0 的图像、声纹、传感器工具；模型包与命令行；性能与故障排除 | 向 INTELPRO 索取 |
| IPRO Debug Probe 使用手册 | V1.1 | 繁体中文／English | 板面、快速上手、按键与 LED、UART 与 JTAG／CCI 接口、电源、主机设置、烧录与调试、BOM 与生产数据 | 向 INTELPRO 索取 |

开发板的上手步骤见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)，SDK 的 API 索引见 [API 参考](../reference/api/index.md)。
