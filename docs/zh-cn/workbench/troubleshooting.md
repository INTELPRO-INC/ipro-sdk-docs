---
title: "故障排除"
description: IPRO Workbench 的消息、工具栏和侧边栏状态的含义及处理方法，macOS 与 Windows 上的问题，以及报告问题时需要附上的信息。
---

# 故障排除

按出现的位置，列出 IPRO Workbench 0.2.1 中各种消息和状态的原因及解决方法。

## 界面上的消息 { #messages }

任何一步失败时，IDE 都会弹出说明以及处理问题的按钮。下表列出每条消息的原因和处理方法。

| 界面上的消息 | 原因 | 处理方法 |
|---|---|---|
| The board did not answer on … | 探针线缆没有接好、开发板没有供电，或选错了端口 | 检查线缆和电源，然后点击 **Select Port** 或 **Retry** |
| Another program has … open, so IntelProCube cannot use it | 其他串口监视器或终端打开了同一个端口 | 关闭该程序，然后点击 **Retry** |
| … has not been built yet. | 还没有可烧录的固件 | 点击 **Build and Flash** |
| Flashing needs IntelProCube, and it was not found. | 未安装 IntelProCube | 点击 **Install IntelProCube**，或点击 **Browse…** 指向已有的 IntelProCube |
| … did not compile. First error at … | 代码有错误 | 点击 **Go to Error**；**Problems** 视图列出所有错误。也可以点击 **Ask AI to Fix** |
| CMake could not configure … | `.config` 或 `CMakeLists.txt` 有误 | 阅读 **IPRO Build** 的输出，修正问题后点击 **Reconfigure and Build** |
| The toolchain or the build tools are missing. | 开发环境尚未补全 | 点击 **Fix Environment** |
| pins.yaml of … has errors, so app_pins.c was not generated. | 引脚配置有冲突，或某个信号在该引脚上不可用 | 点击 **Open Pin Configuration**，逐项修正 **Problems** 下的问题，然后点击 **Save and Generate** |
| The board started firmware built …, not the … just flashed. | 烧录实际上没有写入开发板 | 查看 **IPRO Flash** 的输出，然后点击 **Flash Again** |
| … is over its memory budget | 某个内存区域超出了 `ipro.build.memoryBudget` 中设置的上限 | 点击 **Memory Map** 找出占用较大的符号，或点击 **Budget Settings** 调整上限 |
| The partition table of … reaches …, but the board on this probe has … of flash | 所选的分区表大于开发板的 Flash | 点击 **Partition Table** 选择其他分区表，或检查 `.config` 中的 Flash 大小 |
| IntelProCube has no …, the partition table … flashes with. Without one the board would not boot. | 此版本的 IntelProCube 缺少开发板所需的分区表（IPRO6S EVK 需要 0.7.0.1 或更高版本中的 `partition_cfg_fw_direct.toml`） | 点击 **Install IntelProCube**，或在 **Environment** 的 IntelProCube 一行选择 0.7.0.1 或更高的版本，然后重新烧录 |
| `mfg uses the same space as FW …`（**Partition Table** 和 **AI Model** 视图中的检查结果） | 1M 分区表没有为 AI 模型单独预留空间 | 在 **Partition Table** 中选择带有独立 mfg 分区的分区表（例如应用程序自带的分区表） |
| The board did not answer. Is it running the MFG firmware? | 射频测试期间，开发板运行的不是 MFG 固件，或监视器没有打开 | 烧录 MFG 固件并打开监视器，然后点击 **Check Firmware** |
| **Testing** 视图中没有结果 | 开发板没有重启，或应用程序没有使用 Unity 测试框架 | 确认监视器接在探针的 UART 端口上，然后点击 **Run Tests on Board** |
| The board did not answer wifi_state. Flash an application with the Wi-Fi shell and iperf… | Wi-Fi 吞吐量：开发板上的应用程序没有 Wi-Fi shell，或监视器打开在其他端口上 | 在 IPRO6S EVK 上烧录 `platform/ipro6_demo`；在工具页面的 **Board** 中选择这块开发板的端口 |
| The network name must be 1 to 32 characters without spaces… / The password must be 8 to 63 characters without spaces. | 开发板的 shell 无法接受空格 | 使用不含空格的网络名称和密码（必要时在接入点上另设一个网络） |
| The board did not join …. Check the name and password. | 名称或密码输入有误，或该网络不在 2.4 GHz 上 | 更正后再次点击 **Join Network** |
| This PC has no address on the board's network (…). | 计算机与开发板不在同一个 Wi-Fi 网络上 | 让计算机加入同一个网络（接入点模式下为开发板创建的网络），然后点击 **Run Test** |
| The board did not connect to this PC on TCP port 5001. A firewall on this PC may block incoming connections… | 开发板发送、计算机接收时，计算机的防火墙拦截了传入连接（Windows 的默认行为） | 让防火墙允许传入的 TCP 5001（请参阅[运行测试](measure.md#iperf-run)），或改为从计算机向开发板发送 |
| This PC could not reach the board's iperf server… / An earlier iperf is still running on the board… | 开发板的 iperf 服务器仍在等待连接 | 点击 **Reset Board**；开发板重启后，重新加入网络 |
| The board did not restart. Is the monitor on the console port of an IPRO Debug Probe? | 监视器打开在 CCI 或其他端口上 | 点击工具栏上的开发板，用 **Select Port…** 切换回探针的 UART |
| … is not connected. Check the cable to the board, or pick another port. | 所选端口已不存在（开发板被拔掉，或 USB 端口的名称变了） | 检查线缆，然后点击工具栏上的开发板，用 **Select Port…** 重新选择 |
| The setting ipro.board.port keeps the port at …. Clear the setting to use …? | 设置 `ipro.board.port` 指定的端口与你要使用的不同 | 点击 **Use …** 清除该设置；要保留时取消 |
| The board on … answered, but its flash did not: it was flashed as …, and the flash pins of that board are not this one's. | 工具栏上选择的开发板与实际连接的不同，烧录用错了 Flash 引脚 | 点击 **Select Board** 选择实际连接的开发板，然后点击 **Retry** |
| … is laid out for boot2, and this IntelProCube has no boot2 image for …. | 分区表需要 boot2，而 IntelProCube 没有这颗芯片的 boot2 | 点击 **Install IntelProCube** 更新，或在 **Partition Table** 中改选直接启动固件的分区表 |
| IntelProCube … is too old for …: a board flashed with it does not start. | IPRO6S EVK 需要 IntelProCube 0.7.0.1 或更高版本 | 点击 **Install IntelProCube**，或通过 **Browse…** 指向较新的版本 |
| The board did not start boot2's USB downloader. … | [通过开发板自身的 USB 烧录](flash.md#usb-flash)时，开发板没有重启并进入下载模式（例如固件没有 USB 控制台） | 再次点击 **Flash**，并在 20 秒内拔下开发板的 USB 线再插上 |
| The default partition table comes with IntelProCube, and IntelProCube was not found. / This IntelProCube has no …. | **Partition Table** 找不到默认的分区表 | 点击 **Install IntelProCube**，或在 **Flash with** 中改选其他分区表 |
| The partition table's FW partition has one slot. An OTA needs a table with a second FW slot… / This partition table is a layout without boot2… | **OTA Package**：分区表不是 boot2 的 A/B 布局 | 在 **Partition Table** 中选择为 boot2 预留了空间且有第二个 FW slot 的分区表（例如 `ipro_ble_remote` 的 `partition_cfg_2M_remote_ab.toml`）；请参阅 [OTA 包](flash.md#ota) |
| boot2 OTA packages are for IPRO7 applications; this one is built for the …. | **OTA Package** 不支持 IPRO6S 的应用程序 | 无；IPRO6S 不制作 boot2 OTA 包 |
| The board did not answer the ota_uart command. Its application needs CONFIG_IPRO_OTA=y and CONFIG_IPRO_OTA_UART=y… | 开发板上的应用程序没有 `ota_uart` 命令，或端口不是它的控制台 | 用 IPRO SDK V2.3.0、开启这两项配置构建并烧录后，再发送 |
| The board refused the package: the partition table on the board has no second FW slot. … | 开发板尚未用 A/B 分区表烧录过 | 先用 A/B 分区表和 boot2 烧录应用程序（请参阅 [OTA 包](flash.md#ota)的第 2、3 步） |
| The board refused the package: its SHA-256 does not match: the file is damaged, or the line dropped data. | 传输中丢失了数据 | 点击 **Check on Board** 再试一次；仍然失败时重新制作 OTA 包 |
| The board did not list any network (no answer to wifi_scan). | Wi-Fi 吞吐量：开发板没有响应扫描 | 确认开发板上的应用程序带有 Wi-Fi 命令（例如 `ipro6_demo`），然后点击 **Scan** |
| The Wi-Fi stack did not start (no answer to stack_wifi). | 开发板没有响应 `stack_wifi` | 复位开发板后再点击 **Join Network** |

## 工具栏和侧边栏的状态 { #status }

| 看到的状态 | 处理方法 |
|---|---|
| 工具栏以琥珀色显示“no probe” | IDE 找不到 IPRO Debug Probe。检查 USB 线，并尽量将探针直接连接到计算机；插好后，探针会在几秒内自动出现。 |
| 状态栏显示“Setup: N” | 点击它打开 IPRO Home，然后点击横幅中的 **Fix Environment**。 |
| **Board** 显示“Runs other firmware” | 开发板运行的不是当前应用程序的最新构建。要运行当前的程序，请烧录它。 |
| IPRO6S EVK 的 **Board** 下没有“Runs …”一行 | 使用 IPRO SDK 2.2.1 或更早版本时属于正常现象：这些版本的 IPRO6 固件启动时不打印构建时间，因此 IDE 无法核对开发板上的固件；请以 **IPRO Flash** 中的 `[All Success]` 和监视器中的启动信息为准。从 IPRO SDK V2.3.0 起会显示这一行（请参阅[与 IPRO7 系列的不同之处](flash.md#ipro6s-differences)）。 |
| 状态栏中没有配置文件（齿轮和 `.config`） | 这是正常现象。应用程序没有 `defconfig_*`、`config_*` 等其他配置文件时不显示（请参阅[配置文件](develop.md#configurations)）。 |

## macOS 上的问题 { #macos }

| 情况 | 处理方法 |
|---|---|
| 首次启动时提示无法验证开发者 | 前往“系统设置 → 隐私与安全性”，点击 **仍要打开**（请参阅[安装 IPRO Workbench](install.md#install)）。 |
| **Environment** 显示 **macOS quarantine** | 这些工具是用浏览器或聊天应用下载的，因此 macOS 会在运行时阻止它们。点击该行的锁形图标并确认，即可移除该标记。 |
| 提示缺少 CMake 或构建程序 | macOS 上 IDE 不会安装构建工具。在终端中运行 `xcode-select --install` 和 `brew install cmake ninja`，然后点击 **Check Again**。 |
| 烧录中途失败，显示 `Device not configured` | 探针从 USB 上掉线（线缆、集线器或供电问题）。更换线缆或将探针直接连接到计算机，然后点击 **Retry**。 |

## Windows 上的问题 { #windows }

| 情况 | 处理方法 |
|---|---|
| 安装时显示“Windows 已保护你的电脑” | 点击 **更多信息**，确认应用名称为 IPRO-Workbench，然后点击 **仍要运行**。 |
| 其他串口工具无法打开 COM 端口 | 在 Windows 上，一个 COM 端口同一时间只能被一个程序使用。打开其他工具前先关闭 IPRO Monitor；用完后也请关闭该工具，以便 IDE 进行烧录。 |
| **SDK for this toolchain** 提示需要调整 | IPRO SDK 2.2.1 及更早版本需要几处主机端修正才能在 Windows 上构建。点击 **Fix Environment**（或该行的 **Prepare the SDK for this toolchain**），IDE 会自动处理。 |
| Wi-Fi 吞吐量：开发板发送、计算机接收时没有结果 | Windows 防火墙默认拦截传入连接。添加一条允许 TCP 端口 5001 的入站规则（请参阅[运行测试](measure.md#iperf-run)），或改为从计算机向开发板发送。 |
| 使用 RISC-V 工具链 13.1.1 构建时链接失败 | 在 Windows 上构建 IPRO SDK 需要使用 RISC-V 工具链 14.2.1，13.1.1 无法链接 SDK 预编译的库。点击 **Fix Environment** 安装 14.2.1，或在 **Environment** 的工具链一行改选它。 |
| 选择开发板自身的 USB 端口后无法烧录 | Windows 版暂时不支持通过开发板的 USB 烧录。请连接 IPRO Debug Probe 并选择它的 UART。 |
| Python 一行提示缺少 kconfiglib | 在命令提示符中运行 `python -m pip install kconfiglib windows-curses`，然后点击 **Check Again**。 |
| 代码编辑器提示下载 clangd | 代码导航使用 clangd。按提示让它下载即可，或在 **Environment** 的 clangd 一行点击 Fix。 |

## 收集问题信息 { #collect }

向 INTELPRO 报告问题时，请附上：

1. IDE 的版本：选择 **Help → About**。
2. 失败步骤的输出：在 **Output** 面板中选择 **IPRO Build**、**IPRO Flash** 或 **IPRO Setup**，全选并复制。
3. 开发板的输出：在 IPRO Monitor 标签页上点击 **Save Monitor Output…**，或附上 `build/logs` 中的监视器日志。
4. 如果是崩溃，请附上 `build/crash` 中的崩溃转储文件夹。
