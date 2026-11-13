---
title: "IPRO Workbench"
description: IPRO Workbench 是 INTELPRO 为 IPRO 芯片提供的 IDE：功能、窗口布局与 IPRO Home、支持的环境、从安装到调试与 OTA 的完整流程，以及完整操作手册。
---

# IPRO Workbench

IPRO Workbench 是 INTELPRO 为 IPRO 系列芯片提供的集成开发环境（IDE）。在同一个窗口中即可构建 IPRO SDK 应用程序、将其烧录到开发板，并查看开发板的串口输出。它还提供 C/C++ 代码导航、配置文件切换、引脚配置、GATT 配置、内存分析、OTA 包、传感器仪表板、崩溃分析、板上测试、射频、Wi-Fi 吞吐量与功耗测量，以及能够自行构建和烧录的 AI 助手。

本节各页面以 [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) 搭配 IPRO Debug Probe 为例。每一步都写明要做什么、应看到什么；界面与本节不一致时，请参阅[故障排除](troubleshooting.md)。使用 IPRO6S EVK 时，构建、烧录和监视的步骤相同；不同之处汇总在 [IPRO6S EVK](flash.md#ipro6s) 一节（位于[烧录与开发板](flash.md)）中。如果习惯使用 VS Code 开发，请参阅 [VS Code Extension](../guides/vscode.md)。

!!! info "获取方式"
    IPRO Workbench 0.2.0（预览版）的 macOS 与 Windows 版本发布在 [GitHub 上的 IPRO Workbench 发布页](https://github.com/INTELPRO-INC/ipro-workbench/releases/tag/v0.2.0)，无需 GitHub 账号。暂无 Linux 版本。请参阅[安装 IPRO Workbench](install.md)。

    请搭配 IPRO SDK V2.3.0 使用。较旧的 SDK 也能使用，只是本节标有“SDK V2.3.0”的功能无法使用。

## 功能 { #features }

| 功能 | 说明 |
|---|---|
| 补全开发环境 | 自动检查 SDK、RISC-V 工具链、CMake、Python、IntelProCube 和开发板，缺少的项目一键从 GitHub 安装。 |
| 构建、烧录与监视 | 一个按钮即可完成构建、烧录并打开串口监视器。每一步的输出分开显示；任何一步失败都会停下并说明原因。 |
| 应用程序管理 | 按类别列出 SDK 中的应用程序；可基于开发板的 Hello World、BLE peripheral、IPRO6S EVK 的 Wi-Fi station、IPRO7AI Reef EVK V4.0 的 AI vision 或现有示例创建新的应用程序；请参阅[创建自己的应用程序](first-run.md#own-app)。 |
| 配置（Kconfig） | 以表单方式编辑应用程序的 `.config`，只写入你修改的选项，并显示每个选项的帮助文本和依赖关系。 |
| 配置文件 | 列出应用程序的 `defconfig_*` 和 `config_*` 配置文件；所选的配置文件构建在与 `make DEFCONFIG=<文件>` 相同的 `build_<名称>` 文件夹中，`.config` 保持不变；请参阅[配置文件](develop.md#configurations)。 |
| 引脚配置 | 在封装图和表格中指定每个 GPIO 的功能，检查冲突以及与开发板接线是否一致，并生成初始化代码。 |
| GATT 配置 | 以表单方式定义 BLE 服务和特征，检查 UUID、长度以及应用程序的配置，并生成 GATT 服务代码；请参阅[配置 GATT 服务](develop.md#gatt)。 |
| 内存分析 | 显示 flash、ocram 和 hbnram 分别被哪些库、目标文件和符号占用；比较每次构建之间的大小变化，并可设置内存预算。 |
| 烧录与开发板 | 分区表查看与检查、分区表为 boot2 布局时一并写入 boot2、识别开发板的 Flash、核对开发板上运行的固件，以及将 AI 模型写入 mfg 分区；IPRO6S EVK 使用它自己的分区表烧录。 |
| OTA 包 | 制作应用程序的 boot2 OTA 包并显示是否签名；通过控制台 UART 发送到开发板进行安装，或只让开发板检查（SDK V2.3.0）；请参阅 [OTA 包](flash.md#ota)。 |
| 通过开发板自身的 USB 烧录 | 所选端口是开发板自身的 USB 端口时，通过 boot2 的 USB 下载模式烧录，无需探针（macOS，SDK V2.3.0）；请参阅[通过开发板自身的 USB 烧录](flash.md#usb-flash)。 |
| 串口监视器 | 过滤、时间戳、保存与完整日志、串口绘图器，以及同时监视第二个端口。 |
| 传感器仪表板 | 将开发板打印的 `名称:数值` 显示为数值卡片、仪表、指示灯、倾斜视图和曲线，并通过按钮向开发板发送命令；布局写在应用程序的 `dashboard.yaml` 中；请参阅[传感器仪表板](monitor.md#dashboard)。 |
| 调试与分析 | 自动将崩溃地址解码为源代码行（IPRO7 系列和 IPRO6S），收集并分析崩溃转储，查阅寄存器及其字段。 |
| 测试与测量 | 板上测试结果显示在 **Testing** 视图中、射频测试（BLE DTM）、Wi-Fi 吞吐量（iperf，含扫描、开发板的 MAC 与信号、Wi-Fi 内存 profile）、功耗曲线与电池续航估算。 |
| AI 助手 | 内置的 IPRO AI 助手会自行构建、读取输出、修改配置、引脚和 GATT 服务；IDE 之外的 AI 助手（例如 Claude Code）也可通过 MCP 使用同一组工具，还能打开 SDK，选择开发板、端口和配置文件，并在开发板的控制台上输入命令。 |

## 窗口各区域 { #window }

![IPRO Workbench 窗口，五个区域以 1 到 5 编号：工具栏、IPRO 侧边栏、编辑区、底部面板和状态栏](../assets/workbench/window-areas.svg)

| 编号 | 区域 | 用途 |
|---|---|---|
| 1 | 工具栏 | 当前的应用程序、开发板和端口，以及构建、烧录、监视等按钮。点击应用程序或开发板名称即可更换。 |
| 2 | IPRO 侧边栏 | **Applications** 列出 SDK 中的应用程序；**Board** 显示探针、探针的端口以及开发板上运行的固件；**Environment** 逐项列出检查结果。 |
| 3 | 编辑区 | IPRO Home、源代码，以及配置、引脚、内存映射、分区表等视图都在这里打开。 |
| 4 | 底部面板 | **Output** 中的 **IPRO Build**、**IPRO Flash** 和 **IPRO Setup** 分别显示构建、烧录和安装过程；**Terminal** 中的 **IPRO Monitor** 是串口监视器。 |
| 5 | 状态栏 | 当前的应用程序、开发板和内存用量；开发环境缺少项目时也会在这里提醒。 |

## IPRO Home { #home }

IPRO Home 是打开 SDK 后编辑区中的第一个标签页。如果关闭了它，点击工具栏右侧的房屋图标（**IPRO Home**）即可重新打开。

![IPRO Home 页面，以绿色圆圈 1 到 5 标出横幅、Application 卡片、Recent applications 卡片、Setup 卡片和 Tools 卡片](../assets/workbench/home-tools.svg)

| 编号 | 区域 | 用途 |
|---|---|---|
| 1 | 横幅 | 始终提示“下一步”：尚未打开 SDK 时提示打开 SDK，开发环境缺少项目时提示补全开发环境，一切就绪后显示“&lt;application&gt; is ready to run”和 **Build, Flash and Monitor** 按钮。 |
| 2 | Application | 当前的应用程序、开发板和端口（点击即可更换）；开发板有使用前需要注意的事项时，列在开发板下方（例如 IPRO7AI Reef EVK V4.0 的“The camera needs SW7 on CAM. …”）；指向 Settings (Kconfig)、Pins、GATT services 和 AI assistant (MCP) 的链接；Build、Flash、Monitor 和 Debug 按钮。构建之后还会显示内存用量。 |
| 3 | Recent applications | 最近使用过的应用程序；点击即可切换。也可以从这里新建应用程序。 |
| 4 | Setup | 开发环境检查的摘要以及 **Check Again**；缺少项目时显示 **Fix Environment**。 |
| 5 | Tools | 十个工具页面的入口：Memory map、Partition table、Register reference、Serial plotter、Power、Crash dumps、RF test (DTM)、Wi-Fi throughput、AI model 和 OTA package。每一项都有一行文字说明用途；点击名称即可打开页面。 |

工具页面都在编辑区中打开，并采用同一种布局：顶部是标题和该页面对应的应用程序，然后是选项和按钮，再往下是结果。同样的命令也位于 IPRO 菜单和命令面板中（输入 `IPRO`）；[Sensor Dashboard](monitor.md#dashboard) 不在 **Tools** 卡片上，需从 IPRO 菜单或命令面板打开。

## 支持的环境 { #requirements }

| 项目 | 说明 |
|---|---|
| 计算机 | macOS 12 或更高版本（Apple 芯片）；Windows 11（x64） |
| IPRO SDK | IPRO SDK V2.3.0。标有“SDK V2.3.0”的功能需要这一版本；其他功能在 2.2.x 上也能使用（IPRO6S EVK 需要 2.2.1 或更高版本） |
| 芯片 | IPRO7、IPRO7AI、IPRO6S（构建 SDK 中的 IPRO6 应用程序） |
| 开发板 | [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md)、[IPRO6S EVK](flash.md#ipro6s)；IPRO7AI Sensor Tag（[传感器仪表板](monitor.md#dashboard)和[通过开发板自身的 USB 烧录](flash.md#usb-flash)的示例） |
| 烧录与连接 | IPRO Debug Probe（USB）；烧录使用 IntelProCube（IPRO6S EVK 需要 0.7.0.1 或更高版本）；在 macOS 上也可以通过开发板自身的 USB 烧录（SDK V2.3.0） |
| 界面语言 | 繁体中文、英文、简体中文、日文 |

## 工作流程 { #workflow }

<div class="ipro-steps" markdown>

1. **安装并补全开发环境。** 安装 IPRO Workbench，用 **Fix Environment** 安装 SDK 和工具，打开 SDK，并通过 IPRO Debug Probe 连接开发板；请参阅[安装 IPRO Workbench](install.md)。

2. **运行第一个应用程序。** 选择 `ipro_unit_test`，点击 **Build, Flash and Monitor** 并等待出现 `ALL TESTS PASSED`，然后创建自己的应用程序；请参阅[首次运行](first-run.md)。

3. **开发。** 以表单修改配置（Kconfig），选择要构建的配置文件，分配引脚并生成相应代码，定义 GATT 服务并生成相应代码，修复构建错误并查看内存用在了哪里；请参阅[开发应用程序](develop.md)。

4. **烧录与更新。** 在 IDE 的检查下烧录，将分区表与开发板进行比对，将 AI 模型写入 mfg 分区，制作 OTA 包并通过控制台 UART 发送到开发板，通过开发板自身的 USB 烧录，并构建、烧录和监视 IPRO6S EVK；请参阅[烧录与开发板](flash.md)。

5. **监视。** 查看、过滤、添加时间戳并保存开发板的串口输出，将其打印的数值绘制成曲线或显示在传感器仪表板上；请参阅[串口监视](monitor.md)。

6. **调试与测量。** 解码崩溃地址、收集崩溃转储并查阅寄存器，然后运行板上测试、射频测试、Wi-Fi 吞吐量测试和功耗分析；请参阅[调试与分析](debug.md)和[测试与测量](measure.md)。

</div>

## 完整操作手册 { #manual }

《IPRO Workbench 操作手册》V1.2 以 PDF 形式附在 0.2.0 版本的发布页上：[英文版](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.2.0/IPRO-Workbench-Operation-Manual-V1.2-en.pdf)（73 页）或[繁体中文版](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.2.0/IPRO-Workbench-Operation-Manual-V1.2-zh-TW.pdf)（67 页）。V1.2 是为 0.1.1 编写的，0.2.0 的手册稍后提供；0.2.0 新增和变更的操作以本节为准。它也列在[文档下载](../documents/index.md)中。

## 本节页面 { #pages }

<div class="grid cards" markdown>

-   **[安装 IPRO Workbench](install.md)**

    ---

    下载并校验安装程序，在 macOS 和 Windows 上安装，界面语言，补全开发环境，打开 SDK 并连接开发板。

-   **[首次运行](first-run.md)**

    ---

    构建、烧录并监视 `ipro_unit_test`，创建自己的应用程序，以及应用程序的右键菜单。

-   **[开发应用程序](develop.md)**

    ---

    配置（Kconfig），配置文件，引脚配置与生成的代码，GATT 服务与生成的代码，构建与错误，内存映射、大小变化与内存预算。

-   **[烧录与开发板](flash.md)**

    ---

    烧录及其检查，分区表，开发板的 Flash 与固件核对，将 AI 模型写入 mfg，OTA 包，通过开发板自身的 USB 烧录，以及 IPRO6S EVK。

-   **[串口监视](monitor.md)**

    ---

    打开监视器并输入命令，过滤、时间戳、保存与完整日志、串口绘图器、第二个端口以及传感器仪表板。

-   **[调试与分析](debug.md)**

    ---

    自动解码崩溃地址、包含完整调用链的崩溃转储，以及寄存器参考。

-   **[测试与测量](measure.md)**

    ---

    Testing 视图中的板上测试、以 BLE Direct Test Mode 进行的射频测试、以 iperf 测量 Wi-Fi 吞吐量与 Wi-Fi 内存 profile，以及功耗曲线与电池续航估算。

-   **[AI 助手](ai.md)**

    ---

    开启 AI 功能，让 AI 修复构建错误或分析崩溃，并让 IDE 之外的 AI 助手通过 MCP 使用它。

-   **[故障排除](troubleshooting.md)**

    ---

    界面上的消息、工具栏和侧边栏的状态、macOS 与 Windows 上的问题，以及报告问题时需要提供的信息。

-   **[快捷键、命令与设置](reference.md)**

    ---

    键盘快捷键、IPRO 命令、`ipro.*` 设置、MCP 工具以及 IDE 使用的文件和文件夹。

</div>

## 本版本的范围 { #limitations }

本节各页面对应 IPRO Workbench 0.2.0 预览版。本版本有以下限制：

- 安装程序没有 Apple（未经公证）或 Microsoft 的签名，因此首次打开或安装 IPRO Workbench 时，操作系统会显示提示（处理方法见[安装](install.md#install)）。
- 暂不支持通过 JTAG 调试。开发板崩溃时，请改用[调试与分析](debug.md)中介绍的崩溃解码和崩溃转储。
- 自动更新已关闭。要获取新版本，请从发布页下载并重新安装。
- [Wi-Fi 吞吐量（iperf）](measure.md#iperf)：开发板的网络名称和密码不能包含空格，并且开发板会在串口监视器中回显密码。开发板向 Windows 计算机发送时，防火墙必须允许传入的 TCP 端口 5001。
- [通过开发板自身的 USB 烧录](flash.md#usb-flash)仅在 macOS 版中提供；在 Windows 上请通过 IPRO Debug Probe 烧录。
- 在 Windows 上构建 IPRO SDK 需要使用 RISC-V 工具链 14.2.1（环境检查会安装它）；13.1.1 无法链接 SDK 预编译的库。
- IPRO6 系列开发板启动时不打印分区表和 Flash ID，因此分区表不会与开发板上的进行比对，启动时也不识别开发板的 Flash；使用 IPRO SDK 2.2.1 或更早版本时，**Board** 也不显示开发板运行的是哪个固件（请参阅[与 IPRO7 系列的不同之处](flash.md#ipro6s-differences)）。
- 暂无 Linux 版本。
