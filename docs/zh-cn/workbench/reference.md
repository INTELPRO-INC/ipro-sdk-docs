---
title: "快捷键、命令与设置"
description: IPRO Workbench 0.2.0 参考：键盘快捷键、IPRO 命令、ipro.* 设置、MCP 工具以及 IDE 使用的文件和文件夹。
---

# 快捷键、命令与设置

IPRO Workbench 0.2.0 的键盘快捷键、命令、设置、MCP 工具和文件位置。

## 键盘快捷键 { #shortcuts }

| 操作 | macOS | Windows |
|---|---|---|
| Build, Flash and Monitor | `Cmd+Alt+R` | `Ctrl+Alt+R` |
| Build | `Cmd+Alt+B` | `Ctrl+Alt+B` |
| Flash | `Cmd+Alt+U` | `Ctrl+Alt+U` |
| Serial Monitor | `Cmd+Alt+M` | `Ctrl+Alt+M` |
| 命令面板 | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| 打开设置 | `Cmd+,` | `Ctrl+,` |
| 保存（配置、引脚、GATT、文件） | `Cmd+S` | `Ctrl+S` |

## IPRO 命令 { #commands }

在命令面板中输入 `IPRO`，即可找到下列所有命令。其中大多数命令也位于 IPRO 菜单、工具栏或右键菜单中。

| 命令 | 用途 |
|---|---|
| **IPRO Home** | 打开 IPRO Home |
| **Open SDK…** / **Install SDK from GitHub…** | 打开或安装 IPRO SDK |
| **Check Environment** / **Fix Environment** | 重新检查开发环境；安装缺少的项目 |
| **Select Application…** / **New Application…** / **Copy as New Application…** | 管理应用程序 |
| **Select Configuration…** | 选择应用程序构建所用的配置文件（`.config`、`defconfig_*`、`config_*`）；请参阅[配置文件](develop.md#configurations) |
| **Select Board…** / **Select Port…** | 更换开发板或串口 |
| **Select Toolchain…** / **Select IntelProCube…** | 改用本机上已有的工具 |
| **Build, Flash and Monitor** / **Build** / **Flash** / **Stop** | 运行与停止 |
| **Reconfigure and Build** / **Clean** | 重新运行 CMake 配置；删除构建结果 |
| **Reset Board** | 通过探针复位开发板 |
| **Serial Monitor** / **Open Monitor on Another Port…** | 打开监视器 |
| **Filter Monitor Output…** / **Show Monitor Timestamps** / **Save Monitor Output…** | 显示和保存监视器输出 |
| **Serial Plotter** | 将开发板打印的数值绘制成曲线 |
| **Sensor Dashboard** | 将开发板打印的 `名称:数值` 显示为仪表板；请参阅[传感器仪表板](monitor.md#dashboard) |
| **Settings (Kconfig)…** / **Menuconfig** / **Open .config** | 修改应用程序配置 |
| **Pin Configuration…** | 配置引脚并生成代码 |
| **GATT Configuration…** | 定义 BLE 服务和特征并生成代码 |
| **Memory Map** | 查看内存被什么占用 |
| **Partition Table** / **AI Model…** | 分区表视图；检查并写入 NPU 模型 |
| **OTA Package…** | 制作 boot2 OTA 包并发送到开发板；请参阅 [OTA 包](flash.md#ota) |
| **Run Tests on Board** | 复位开发板并收集 Unity 测试结果 |
| **RF Test (DTM)…** / **Wi-Fi Throughput (iperf)…** / **Power…** | 射频、Wi-Fi 吞吐量与功耗测量 |
| **Crash Dumps…** | 打开之前收集的崩溃转储 |
| **Register Reference** | 查阅外设、寄存器和字段 |
| **Ask AI About the Last Crash** / **Connect an AI Assistant (MCP)…** | AI 助手 |

## 设置 { #settings }

打开设置并搜索 `ipro`，即可看到以下各项。

| 设置项 | 说明 |
|---|---|
| `ipro.sdk.path` | 打开的文件夹不是 SDK 时使用的 IPRO SDK 文件夹 |
| `ipro.tools.base` | IDE 安装工具的位置。留空表示主目录下的 `IPRO/tools` |
| `ipro.toolchain.prefix` | 交叉编译前缀。留空表示自动查找 |
| `ipro.flashTool.path` | IntelProCube 的文件夹或可执行文件。留空表示自动查找 |
| `ipro.build.profile` | 构建类型：Debug、Release、MinSizeRel |
| `ipro.build.generator` | CMake 生成器：auto、Unix Makefiles、Ninja |
| `ipro.build.memoryBudget` | 构建可使用的各内存区域的最大比例（百分比），例如 `{ "flash": 90 }` |
| `ipro.build.failOverBudget` | 超出内存预算的构建判为失败 |
| `ipro.board.id` | 开发板。auto 表示跟随应用程序的 `.config` |
| `ipro.board.port` | 用于烧录和监视器的串口。留空表示选择探针的 UART |
| `ipro.flash.baudRate` | IntelProCube 的波特率 |
| `ipro.run.openMonitor` | 烧录成功后打开串口监视器；默认开启 |
| `ipro.monitor.baudRate` | 串口监视器的控制台波特率，默认为 115200 |
| `ipro.monitor.timestamps` | 在监视器每一行的开头加上接收时间 |
| `ipro.monitor.filter` | 只显示与此正则表达式匹配的监视器行 |
| `ipro.monitor.logToFile` | 将每次监视器会话的完整内容保存到应用程序的 `build/logs` |
| `ipro.mcp.enabled` / `ipro.mcp.port` | 供 IDE 之外的 AI 助手使用的 MCP 服务器；默认开启，端口 41730 |
| `ipro.ai.assistant` | **Ask AI to Fix** 等请求交给谁：`ipro`（IPRO 助手，需要语言模型；默认）或 `claudeCode`（Claude Code 助手，使用你的 Claude Code 登录，并通过 MCP 使用 IPRO 工具） |
| `ipro.macos.probeDownloadMode` | macOS：烧录时保持 IPRO Debug Probe 的下载模式 strap 引脚 |
| `ipro.macos.checkQuarantine` | macOS：启动时检查工具是否带有隔离标记 |

## MCP 工具 { #mcp-tools }

IDE 之外的 AI 助手通过 MCP 可以看到以下工具（名称即 MCP 工具名）。内置的 IPRO AI 助手使用同一组工具。如何连接助手：请参阅 [AI 助手](ai.md#mcp)。

| 工具 | 用途 |
|---|---|
| `ipro_get_target` | SDK、当前的应用程序、开发板和串口、开发环境问题以及上一次构建的结果 |
| `ipro_open_folder` | 打开 IPRO SDK 文件夹；指定应用程序文件夹时，打开它所在的 SDK 并将它设为当前应用程序 |
| `ipro_list_applications` | 列出 SDK 中的所有应用程序 |
| `ipro_select_application` | 切换当前应用程序 |
| `ipro_list_configurations` / `ipro_select_configuration` | 列出当前应用程序的配置文件；选择构建所用的配置文件 |
| `ipro_list_boards` / `ipro_select_board` | 列出 IDE 识别的开发板及当前使用的开发板；选择开发板，或恢复为 auto |
| `ipro_list_ports` / `ipro_select_port` | 列出这台计算机的串口（探针的 UART、CCI 及其他）；选择烧录、监视和复位使用的端口 |
| `ipro_build` | 构建当前应用程序；返回错误、警告和内存用量 |
| `ipro_get_build_output` | 读取 IPRO Build 或 IPRO Flash 的最新输出 |
| `ipro_flash` | 烧录最新构建并打开监视器 |
| `ipro_reset_board` | 通过探针复位开发板 |
| `ipro_open_monitor` / `ipro_close_monitor` | 在当前端口上打开串口监视器（可同时复位开发板）；关闭监视器以释放端口 |
| `ipro_read_monitor` | 读取开发板在监视器上打印的最新几行 |
| `ipro_write_monitor` | 在开发板的控制台上输入一行命令，并返回开发板随后打印的内容 |
| `ipro_board_tests` | 开发板上次启动的固件以及 Unity 测试结果 |
| `ipro_get_settings` / `ipro_set_settings` | 读取和修改应用程序的 Kconfig 配置 |
| `ipro_get_pins` / `ipro_set_pins` | 读取和修改引脚配置并生成代码 |
| `ipro_get_gatt` / `ipro_set_gatt` | 读取和修改 GATT 服务并生成代码（试运行只检查、不写入） |
| `ipro_memory_map` | 各内存区域的用量以及占用最大的库和目标文件 |
| `ipro_partition_table` | 烧录时写入的分区表及其检查结果 |
| `ipro_ai_model` | 检查 NPU 模型是否适合该应用程序及其分区表 |
| `ipro_crash_dump` | 最新崩溃转储中的异常和调用链 |
| `ipro_decode_addresses` | 将代码地址解码为函数、文件和行号 |
| `ipro_lookup_register` | 按名称或地址查找寄存器 |

## 文件位置 { #file-locations }

| 位置 | 内容 |
|---|---|
| 主目录下的 `IPRO/tools/<tool>/<version>` | **Fix Environment** 安装的工具（Windows 上为 `%USERPROFILE%\IPRO\tools`） |
| 主目录下的 `IPRO/SDK/<version>` | **Install SDK from GitHub…** 安装的 SDK |
| 主目录下的 `.ipro-ide` | IDE 设置和 MCP 访问令牌（`mcp.json`） |
| `apps/<category>/<name>/build` | 应用程序的构建结果（固件、ELF、map 文件） |
| `apps/<category>/<name>/build_<configuration>` | 以 `defconfig_<configuration>` 构建的结果（`config_<configuration>` 对应 `build_config_<configuration>`），与 `make DEFCONFIG=<file>` 相同 |
| `apps/<category>/<name>/build/build_out/<name>.xz.ota` | **OTA Package** 制作的 boot2 OTA 包（选择了配置文件时位于该配置文件的构建文件夹中） |
| `apps/<category>/<name>/build/logs` | 监视器的完整日志（开启 **Log To File** 时） |
| `apps/<category>/<name>/build/crash` | 收集的崩溃转储 |
| `apps/<category>/<name>/pins.yaml` | 引脚配置；`app_pins.h` 和 `app_pins.c` 由它生成 |
| `apps/<category>/<name>/gatt.yaml` | GATT 服务；`app_gatt.h` 和 `app_gatt.c` 由它生成 |
| `apps/<category>/<name>/dashboard.yaml` | Sensor Dashboard 的布局 |
