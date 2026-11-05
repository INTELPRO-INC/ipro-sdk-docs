---
title: "VS Code Extension"
description: IPRO SDK Extension 3.3.0 配合 SDK V2.2.0：设置 SDK 根目录、构建、烧录 IPRO7AI Reef EVK、串口控制台、内存分析与命令
migrate_from:
  - "vscode-extension.html"
not_migrated:
  - "vscode-extension.html#installation — installation steps live in get-started/windows.md"
  - "vscode-extension.html#cli-tools — the IntelProCube command line belongs on the flashing page"
---

# VS Code Extension

IPRO SDK Extension 3.3.0（标识符 `ipro.ipro-sdk-extension`）把 FreeRTOS 项目浏览、CMake 构建、IntelProCube 烧录、串口控制台与内存分析集成到 VS Code 中，需要 VS Code 1.102 或更高版本。Extension 不包含在 SDK 包内，与 SDK 以及负责安装它的 IPRO SDK Online Setup 各自独立编号版本；安装步骤见 [Windows 安装与 VS Code](../get-started/windows.md)。

!!! abstract "要点"
    - Online Setup 3.6.0 一次性安装 SDK V2.2.0、Extension 与各项工具；以 Full environment 安装的环境可以直接构建。
    - Windows 上的工具链是 Online Setup 安装的 GCC 13.1.1，SDK 已针对它做好准备；用 Diagnostics 确认 Extension 使用的是同一安装目录中的编译器。
    - 烧录 IPRO7AI Reef EVK 时，芯片配置用 `IPRO7AI`，分区表用应用所使用的那一份；boot2 镜像与 `mfg` 数据通过 IntelProCube 命令行写入。
    - 控制台波特率（`ipro.monitorBaudRate`）与烧录波特率（`ipro.baudRate`）分开设置。
    - 没有源代码级（F5）调试：安装 OpenOCD 并不会配置好 GDB debug adapter。

## 功能 { #features }

| 功能 | 用途 |
|---|---|
| 项目 | 按分类浏览应用、固定并切换当前项目（`IPRO: Go to Project…`、`IPRO: Select Project`） |
| Build／Batch Build | CMake 配置与 Make／Ninja 构建（`ipro.generator`），debug／release／size Profile，可从 Problems 中的错误跳转到源代码 |
| 配置 | `IPRO Config: Menuconfig`、`IPRO Config: Open .config`、`IPRO Config: Load Defconfig` |
| Flash／Monitor | 用 IntelProCube 烧录；内置串口控制台，波特率单独设置 |
| Analysis／Debug | Memory Map、Decode Crash Report、Pin Function Lookup；Register Explorer 需要兼容的 CCI 连接 |

SDK 构建原样读取 `.config`，不解析 Kconfig 的 `select` 与 `depends on`。用 Menuconfig 修改后，请确认依赖选项都已写入 `.config`，见[构建系统与配置](build-system.md#configuration)。

## 使用 SDK V2.2.0 { #sdk-2-2-0 }

<div class="ipro-steps" markdown>

1. 用 Online Setup 安装：新环境选择 **Full environment**，见 [Windows 安装与 VS Code](../get-started/windows.md#online-setup)；已有环境时，可选择 **SDK only** 把 SDK V2.2.0 加入该环境，见[单独安装 SDK 或工具链](../get-started/windows.md#components)。
2. 用 **File → Open Folder…** 打开 `<安装目录>\sdk\IPRO-SDK-V2.2.0`（其中包含 `CMakeLists.txt`、`apps` 与 `bsp`）。如果安装时没有勾选设置切换任务，对它执行 `IPRO Setup: Set SDK Root`。
3. 执行 `IPRO Setup: Run Diagnostics`，核对 SDK 根目录、编译器、CMake、Ninja、Python 与烧录工具都指向同一个安装目录；编译器是 `<安装目录>\toolchain\riscv_ipro7_win32` 中的 GCC 13.1.1。改用其他工具链时用 `ipro.toolchainPath` 设置（编译器前缀，以 `riscv64-unknown-elf-` 结尾）。

</div>

- 在 V2.2.0 完成构建并上板验证之前，保留原来的 SDK 目录。不要把旧的 `build/` 目录、CMake 缓存或 `.vscode` 文件夹复制到新的 SDK 中。
- 工作区设置（`.vscode/settings.json`）可能会覆盖用户设置；以 Diagnostics 显示的路径为准。

## 控制中心 { #control-center }

按 F1 执行 `IPRO: Open Control Center`，在同一个面板中查看当前的 SDK、项目与连接，以及常用操作；再执行 `IPRO Setup: Run Diagnostics` 核对工具路径。也可以在 VS Code 的 Settings 中搜索 `ipro` 调整设置。

## 第一次构建 { #workflow }

<div class="ipro-steps" markdown>

1. 执行 `IPRO: Go to Project…`，选择 platform 分类下的 `ipro7ai_reef_demo`。
2. 执行 `IPRO Config: Select Build Profile`，选择 debug、release 或 size。
3. 执行 `IPRO: Build`，在 Terminal 中查看结果；可从 Problems 中的错误跳转到源代码。构建成功的标准是退出码为 0 且生成了镜像，而不是看到 CMake 打印 `Configuring done`。
4. 确认已生成 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

</div>

`IPRO: Batch Build` 一次构建多个选定的项目。SDK 或工具路径变更后，先执行 `IPRO: Clean` 再重新构建，避免沿用旧的缓存。

多数 Reef 应用把 Reef 的配置放在另一个文件中（`defconfig_reef`、`defconfig_reef_ov5640` 等）；直接构建即为 Reef 版本的只有 `ipro7ai_reef_demo`、`ipro_reef_teach` 与 `ipro_agora_sentino`。命令行写法 `make -C <应用> DEFCONFIG=<文件名>` 与 Reef 配置列表见[构建系统与配置](build-system.md#variants)。

## 烧录与控制台 { #flash }

<div class="ipro-steps" markdown>

1. 用 `IPRO Setup: Select Flash Tool` 选择 IntelProCube，或把 `ipro.flashToolPath` 设为它所在的文件夹。
2. 接好开发板（SW7 拨到 CAM、SW8 拨到 PWR、控制台线接 U6、插上 USB-C），执行 `IPRO: Select Serial Port` 选择控制台端口。使用 IPRO Debug Probe 时选择它的 UART 端口；CCI 端口用于寄存器访问，不能用于控制台或烧录。
3. 在 `IPRO Config: Configure Flash…` 中把芯片配置设为 `IPRO7AI`，分区表设为应用所使用的那一份：`ipro7ai_reef_demo` 与 `ipro7_uvc_cam` 网络摄像头用 `partition_cfg_2M.toml`。自带分区表的应用列在[烧录与串口](../get-started/flash-and-monitor.md#partition-tables)中。
4. 让 Reef 进入下载模式：按住 SW1（BOOT），按一下 SW2（RESET），松开 SW1。然后执行 `IPRO: Flash`，确认烧录工具的结果。请先关闭其他占用串口的程序。
5. 按 SW2 启动固件。确认 `ipro.monitorBaudRate` 与固件一致（`IPRO Config: Set Monitor Baud Rate`），再执行 `IPRO: Serial Monitor`。要更改波特率时，先执行 `IPRO: Close Serial Monitor`，设置后再重新打开。

</div>

| 设置 | 含义 |
|---|---|
| `ipro.baudRate` | 烧录波特率，默认 921600 |
| `ipro.monitorBaudRate` | 控制台波特率，默认 115200，必须与固件一致 |
| `ipro.chipVariant` | 传给烧录工具的 `--chip-variant`：Reef 用 `IPRO7AI` |
| `ipro.partitionTable` | 传给烧录工具的 `--pt`；在 Reef 上请根据应用设置 |
| `ipro.flashTargets`、`ipro.activeFlashTarget` | 具名的烧录配置，切换时无需每次修改设置 |

所有 Reef 配置的控制台都是 115200 baud，只有 `ipro7_jpeg_decode`（`defconfig_reef`）是 921600，以应用的 `CONFIG_PLATFORM_UART_BAUDRATE` 为准。`ipro_ble_remote` 的首次烧录（boot2 与 A/B 分区表）与 `ipro_reef_teach` 的 `mfg` 数据，请使用 IntelProCube 命令行，见[烧录与串口](../get-started/flash-and-monitor.md#boot2-ab)与[烧录 Edge AI 固件](../teach/firmware.md)。

## 内存与调试工具 { #memory-map }

- `IPRO Analyse: Memory Map`：构建后查看各内存区域与各组件的用量。能否放得下仍以链接器输出与烧录时使用的分区表为准。
- `IPRO Analyse: Decode Crash Report`：把异常的回溯转换为源代码位置。
- `IPRO Debug: Pin Function Lookup`：查询引脚功能。
- `IPRO Debug: Register Explorer`：需要兼容的 Probe、正常工作的 CCI 连接与正确的板端设置。Probe 能在 USB 上枚举，不代表它与开发板之间的 CCI 连接可用。

安装 OpenOCD 并不会带来 F5 源代码级调试：Extension 不会配置 GDB debug adapter 或 launch 配置。控制台日志与崩溃解码见[调试与故障排除](../reference/debugging.md)。

## 在 Reef 上动手实践 { #hands-on }

用出厂固件在 VS Code 中走一遍“修改、构建、烧录”流程。

<div class="ipro-steps" markdown>

1. **确认控制台配置。** 固件的控制台波特率写在 `.config` 中，`ipro.monitorBaudRate` 必须与之相同：

    ```ini title="apps/platform/ipro7ai_reef_demo/.config（节选）"
    CONFIG_PLATFORM_UART_BAUDRATE=115200
    ```

2. **修改代码。** 打开 `apps/platform/ipro7ai_reef_demo/main.c`，修改 `main()` 中的标语：

    ```c title="apps/platform/ipro7ai_reef_demo/main.c（节选，已修改）"
    ipro_platform_init();   /* heap + boot2 + log + shell */

    IPRO_LOGI(LOG_TAG, "==========================================");
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **构建**：执行 `IPRO: Build`。镜像文件是 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

4. **烧录**：按照[烧录与控制台](#flash)，用 SW1 + SW2 进入下载模式，以芯片配置 `IPRO7AI`、分区表 `partition_cfg_2M.toml` 执行 `IPRO: Flash`，再按 SW2。

5. **查看控制台**：以 115200 baud 执行 `IPRO: Serial Monitor`。开头几行中（省略了日志前缀）：

    ```text
    Build:<时间>,<日期>
    ...
      IPRO7AI Reef carrier demo - my build
    ```

    `Build:` 行是这次构建的时间，标语则是你修改过的文字。`reef selftest` 可检查板上的各个模块。

</div>

完成后把那一行改回来，或重新烧录出厂镜像。接下来：[创建第一个自己的应用](../tutorials/first-own-app.md)与[测试你的应用](../tutorials/testing.md)。

## 组件更新 { #component-updates }

更新通过 IPRO SDK Online Setup 进行；它把组件安装到新的目录，或把 SDK、工具链加入现有环境，不会覆盖正在使用的版本：

| Online Setup 模式 | 安装内容 | 可切换的设置 |
|---|---|---|
| Full environment | SDK、工具链、构建工具（CMake、Ninja、Python）、IntelProCube、OpenOCD、Extension | 全部 |
| SDK only | SDK | `ipro.sdkRoot` |
| Toolchain only | RISC-V 工具链 | `ipro.toolchainPath` |
| Build tools only | CMake、Ninja、Python | 各自的路径 |
| IntelProCube only | IntelProCube | `ipro.flashToolPath` |
| OpenOCD only | OpenOCD | — |
| Extension only | Extension VSIX | — |

SDK only 与 Toolchain only 可以加入现有环境，见[单独安装 SDK 或工具链](../get-started/windows.md#components)。更新后重启 VS Code 并执行 Diagnostics。要回退到旧版本时，把设置指回保留的目录，或用 **Install from VSIX…** 安装旧版 VSIX。

## 命令 { #shortcuts }

按 F1 或 Ctrl+Shift+P 打开命令面板。Extension 没有默认快捷键，可自行绑定。

| 命令 | 用途 |
|---|---|
| `IPRO: Open Control Center` | 打开控制中心 |
| `IPRO Setup: Set SDK Root` | 设置 SDK 根目录 |
| `IPRO Setup: Run Diagnostics` | 检查 SDK 与工具路径 |
| `IPRO Setup: Select Flash Tool` | 选择 IntelProCube 文件夹 |
| `IPRO: Go to Project…`、`IPRO: Select Project` | 查找与切换项目 |
| `IPRO Config: Select Build Profile` | 选择 debug、release 或 size |
| `IPRO: Build` | 构建当前项目 |
| `IPRO: Clean` | 删除当前项目的构建输出 |
| `IPRO: Batch Build` | 构建多个项目 |
| `IPRO Config: Menuconfig`、`IPRO Config: Open .config` | 编辑或打开配置 |
| `IPRO Config: Select Flash Target`、`IPRO Config: Configure Flash…` | 选择烧录目标；设置芯片配置、分区表与波特率 |
| `IPRO: Select Serial Port` | 选择控制台／烧录串口 |
| `IPRO Config: Set Monitor Baud Rate` | 设置控制台波特率 |
| `IPRO: Flash` | 烧录固件 |
| `IPRO: Serial Monitor`、`IPRO: Close Serial Monitor` | 打开控制台；关闭并释放串口 |
| `IPRO: Build, Flash & Monitor` | 依次构建、烧录并打开控制台 |
| `IPRO Analyse: Memory Map` | 分析内存用量 |
| `IPRO Analyse: Decode Crash Report` | 解码异常与回溯 |
| `IPRO Debug: Pin Function Lookup` | 查询引脚功能 |
| `IPRO Debug: Register Explorer` | 经 CCI 查看寄存器 |

## 常见问题 { #faq }

| 现象 | 处理方法 |
|---|---|
| 找不到 IPRO 命令 | 确认 Extension 版本、VS Code Profile、Workspace Trust 与 SDK 根目录，再重新加载窗口 |
| Diagnostics 仍显示旧的 SDK | 工作区与文件夹设置可能覆盖了用户设置；对 V2.2.0 目录再执行一次 `IPRO Setup: Set SDK Root` |
| 编译或链接失败 | 用 Diagnostics 确认编译器是同一个安装目录中的工具链（Windows 为 Online Setup 安装的 GCC 13.1.1；macOS／Linux 为 GCC 14） |
| 控制台乱码或仍是旧的波特率 | 核对固件的控制台波特率与 `ipro.monitorBaudRate`，再关闭并重新打开控制台 |
| 烧录 Reef 时出现 `flash jedec id: 00000000` | 把芯片配置设为 `IPRO7AI` |
| 烧录工具没有打印 `[All Success]` | 开发板没有进入下载模式，或串口被其他程序占用 |
| 能检测到 Probe，但 CCI 没有响应 | USB 枚举成功不代表板端的 CCI 连接正常；检查接线与板端设置 |

## 版本 { #version }

SDK、Extension 与 Online Setup 是各自独立编号版本的软件包。当前的 Extension 是 3.3.0，由 Online Setup 3.6.0 安装；安装程序的版本号不代表 Extension 也是同一版本。实际安装的版本以 Extensions 面板中显示的为准。

## 相关文档 { #related }

- [Windows 安装与 VS Code](../get-started/windows.md)：安装工具与 Extension、加入 SDK V2.2.0。
- [烧录与串口](../get-started/flash-and-monitor.md)：IntelProCube 命令行、分区表、boot2 与 `mfg`。
- [构建系统与配置](build-system.md)：`.config`、替代配置与 Reef 构建列表。
- [创建第一个自己的应用](../tutorials/first-own-app.md)：自己的 Reef 应用。
