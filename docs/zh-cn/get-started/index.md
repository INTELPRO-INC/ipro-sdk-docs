---
title: "开始使用"
description: 从一台新电脑和一块 IPRO7AI Reef EVK 开始：准备硬件与工具，构建并烧录出厂固件，直到控制台响应。
migrate_from: []
---

# 开始使用

按以下顺序完成，就能从一台新电脑开始，在 IPRO7AI Reef EVK V4.0 上构建、烧录并运行出厂固件 `ipro7ai_reef_demo`，再用 `reef selftest` 检查板上功能。本站的操作步骤都以这块开发板为准；IPRO7 EVB、IPRO7AI EVK、IPRO6S EVK 与 IPRO7 Arduino 板的应用需要对应的开发板，请联系 INTELPRO。

## 需要准备 { #what-you-need }

| 项目 | 说明 | 获取方式 |
|---|---|---|
| IPRO7AI Reef EVK V4.0 | 丝印“IPRO7AI REEF EVK V4.0” | INTELPRO |
| USB-C 线 | 开发板唯一的电源输入；需支持数据传输（板上 USB 设备功能会用到） | 自备 |
| 控制台线（二选一） | 3.3 V 的 USB 转 UART 适配器，通过 SH1.0 6 pin 插头接 U6；或 IPRO Debug Probe，通过两端引脚顺序对调的排线接 U6 | 适配器自备；Debug Probe 向 INTELPRO 索取 |
| 主机 | macOS 或 Linux（bash）可使用 SDK 全部的命令行工具；Windows 通过安装程序、VS Code Extension 与 `build_freertos.ps1` 开发 | — |
| RISC-V 工具链 | GCC 14（Windows 为 GCC 13.1.1），`riscv64-unknown-elf-gcc` | macOS／Linux 版向 INTELPRO 索取；Windows 版由安装程序安装 |
| IntelProCube 0.7.0.1 | 烧录工具：`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | [GitHub Release](https://github.com/INTELPRO-INC/ipro-cube/releases)；Windows 版也由安装程序安装 |
| SDK | `IPRO-SDK-V2.2.1.tar.gz` | [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.1) |
| 可选 | OV5640 FLEX-24 摄像头模组、microSD 卡、8 Ω 扬声器（接 J_SPK）、耳机 | 自备；用于完成自检中的摄像头、卡槽与扬声器项目 |

控制台线的接法见 [IPRO7AI Reef EVK：调试排座 U6](../hardware/boards/reef-evk.md#debug-connector)。

!!! tip "图形化开发环境"
    IPRO Workbench（Apple 芯片的 macOS、Windows 11）把补齐工具、构建、烧录与串口监视放在同一个窗口中，见 [IPRO Workbench](../workbench/index.md)。

## 按顺序完成 { #path }

<div class="grid cards" markdown>

-   :material-tools:{ .lg } **1. [准备开发环境](environment.md)**

    ---

    下载并校验 SDK，安装 CMake、make、Python、RISC-V 工具链与 IntelProCube，通过一次构建确认环境可用。

-   :material-microsoft-windows:{ .lg } **2. [Windows 安装与 VS Code](windows.md)**

    ---

    仅在使用 Windows 时需要：用 Online Setup 一次安装 SDK、工具与 VS Code Extension，在 VS Code 中或用 `build_freertos.ps1` 构建与烧录。

-   :material-developer-board:{ .lg } **3. [第一个 FreeRTOS 应用](first-app-freertos.md)**

    ---

    设置开关、连接控制台线，构建、烧录并运行 `ipro7ai_reef_demo`，用 `reef selftest` 检查 LED、扬声器、SD 卡槽与摄像头。

-   :material-usb-port:{ .lg } **4. [烧录与串口](flash-and-monitor.md)**

    ---

    参考：进入下载模式的四种方式、IntelProCube 参数与分区表、boot2 与 `mfg` 数据、控制台与串口识别。

-   :material-console:{ .lg } **5. [macOS／Linux 命令行](command-line.md)**

    ---

    参考：`make -C`、`DEFCONFIG=`、构建目录与输出，以及 `build_freertos.sh` 的动作、选项与环境变量。

</div>

## 下一步 { #next-steps }

开发板运行起出厂固件之后，接着完成这三篇实践教程：

- [构建与烧录流程](../tutorials/build-and-flash.md)：修改代码、构建、烧录、查看控制台的日常循环。
- [创建第一个应用](../tutorials/first-own-app.md)：从零创建自己的应用并在 Reef 上运行。
- [测试应用](../tutorials/testing.md)：在主机与开发板上测试自己的应用。

开发板的完整资料（开关、引脚、扩展排针）见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。本版本的 Zephyr 板型只有 IPRO7 EVB 与 IPRO7AI EVK，没有 Reef，见 [Zephyr RTOS](../guides/zephyr.md)。
