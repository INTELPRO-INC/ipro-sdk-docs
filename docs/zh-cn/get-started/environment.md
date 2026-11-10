---
title: "准备开发环境"
description: 在 macOS、Linux 或 Windows 上获取并校验 SDK，安装构建工具、RISC-V 工具链与 IntelProCube，连接控制台线，并通过一次构建确认环境。
migrate_from:
  - "getting-started.html#sdk-2-1-0"
  - "getting-started.html#prerequisites"
---

# 准备开发环境

完成本页后，主机上将具备 SDK、构建工具、RISC-V 工具链与 IntelProCube 烧录工具，能识别 Reef 的控制台串口，并能在 SDK 根目录构建 IPRO7AI Reef EVK 的出厂固件。各步骤按操作系统分标签页；Windows 的完整流程另见 [Windows 安装与 VS Code](windows.md)。

## 前提条件 { #prerequisites }

| 项目 | 要求 |
|---|---|
| 主机 | macOS 或 Linux（有 bash）；或 Windows x64 |
| 权限 | 安装软件包与写入 `/opt/toolchain/` 需要管理员权限 |
| 网络 | 下载 SDK；Windows 的 Online Setup 需要能访问 GitHub |
| 另行获取 | RISC-V 工具链：macOS／Linux 版向 INTELPRO 索取，Windows 版由 Online Setup 安装 |
| 烧录工具 | IntelProCube 0.7.0.1：从 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) 下载，见[安装 IntelProCube](#intelprocube)；Windows 版由 Online Setup 安装 |
| 硬件 | IPRO7AI Reef EVK、USB-C 线、控制台线，见[需要准备](index.md#what-you-need) |

## 获取 SDK { #get-sdk }

<div class="ipro-steps" markdown>

1. **下载**：从 [IPRO-SDK-V2.2.0 Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) 下载 `IPRO-SDK-V2.2.0.tar.gz`，并记下页面上公布的 SHA-256 值。

2. **校验**：计算下载文件的 SHA-256。

    === "macOS"

        ```bash
        shasum -a 256 IPRO-SDK-V2.2.0.tar.gz
        ```

    === "Linux"

        ```bash
        sha256sum IPRO-SDK-V2.2.0.tar.gz
        ```

    === "Windows"

        ```powershell
        Get-FileHash .\IPRO-SDK-V2.2.0.tar.gz -Algorithm SHA256
        ```

    屏幕输出 64 个十六进制字符，应与 Release 页面公布的值完全相同（不区分大小写）。不同时请重新下载。

3. **解压并确认版本**：解压到新的目录，不要覆盖旧版 SDK。

    === "macOS／Linux"

        ```bash
        tar xzf IPRO-SDK-V2.2.0.tar.gz
        cd IPRO-SDK-V2.2.0
        cat VERSION.txt
        ```

    === "Windows"

        ```powershell
        tar -xzf .\IPRO-SDK-V2.2.0.tar.gz
        Get-Content .\IPRO-SDK-V2.2.0\VERSION.txt
        ```

    `VERSION.txt` 的内容：

    ```text
    IPRO SDK Release
    ========================================
    IPRO7: IPRO-SDK-V2.2.0
    IPRO6: IPRO-SDK-V2.2.0

    Release Date: 2026-11-03
    Base Commit: 60afd4ab
    ```

    解压出的 `IPRO-SDK-V2.2.0/` 就是 SDK 根目录（本站写作 `<SDK>`），其中包含 `apps/`、`bsp/`、`components/`、`build_freertos.sh` 与 `VERSION.txt`。

</div>

## 安装构建工具 { #host-tools }

<div class="ipro-steps" markdown>

1. **安装 CMake、GNU Make 与 Python**

    === "macOS"

        ```bash
        xcode-select --install          # 提供 make
        brew install cmake python3
        ```

    === "Linux"

        ```bash
        sudo apt update
        sudo apt install -y cmake make python3
        ```

        以 Debian／Ubuntu 为例，其他发行版请安装对应的软件包。在 Linux x86-64 上，如果 PATH 中没有 `cmake`，构建会改用 SDK 随附的 `tools/cmake/`（CMake 3.15）。

    === "Windows"

        通过 Online Setup 的 **Full environment** 或 **Build tools only** 安装 CMake、Ninja 与 Python，见 [Windows 安装与 VS Code](windows.md#online-setup)。

2. **确认版本**（macOS／Linux）

    ```bash
    cmake --version     # 3.15 及以上；Zephyr 需要 3.20 及以上
    make --version      # 第一行为 GNU Make
    python3 --version   # 3.8 及以上
    ```

</div>

## 安装 RISC-V 工具链 { #toolchain }

<div class="ipro-steps" markdown>

1. **放到默认路径**

    === "macOS／Linux"

        按 INTELPRO 提供的压缩包解压，使以下文件存在：

        ```text
        /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc
        ```

    === "Windows"

        Online Setup 安装 Windows 版工具链 GCC 13.1.1，并据此准备 SDK，SDK V2.2.0 可以直接构建；它构建出的镜像与 macOS／Linux 上用 GCC 14 构建出的不同。见 [Windows 安装与 VS Code](windows.md#online-setup)。

2. **确认可以运行**（macOS／Linux）

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc --version
    ```

    第一行以 `riscv64-unknown-elf-gcc` 开头，版本为 14.x。

3. **放在其他路径时**：设置编译器前缀 `CROSS_COMPILE`（包括末尾的连字符）。构建时依次采用命令行或环境变量中的 `CROSS_COMPILE`、应用 `.config` 中的 `CONFIG_CROSS_COMPILE`，最后才是默认路径。

    ```bash
    export CROSS_COMPILE=<工具链目录>/bin/riscv64-unknown-elf-
    ```

    如需长期使用，把这一行加入 `~/.zshrc`（macOS）或 `~/.bashrc`（Linux）。

</div>

## 安装 IntelProCube { #intelprocube }

IntelProCube 是 IPRO6 与 IPRO7 的烧录与 OTA 工具，公开在 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases)；本站以 0.7.0.1 为准。Windows 由 Online Setup 安装 0.7.0，它烧录 IPRO7 与 Reef 的文件与 0.7.0.1 相同，见 [Windows 安装与 VS Code](windows.md)；烧录 IPRO6S 时，按 [IntelProCube 的 README](https://github.com/INTELPRO-INC/ipro-cube#windows) 另外安装 0.7.0.1。

<div class="ipro-steps" markdown>

1. **下载并核对**

    === "macOS"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-macos-arm64.tar.gz
        shasum -a 256 IntelProCube-0.7.0.1-macos-arm64.tar.gz
        ```

        屏幕显示 `c3a8bf7eca2a48c3f9bf40c3241ddf6aec5155688f2a92f40a84cc47f7633bc4`。macOS 版需要 Apple 芯片。改用浏览器下载时，解压前先运行 `xattr -d com.apple.quarantine IntelProCube-0.7.0.1-macos-arm64.tar.gz`，否则 macOS 会终止软件包里的程序。

    === "Linux"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-linux-x64.tar.gz
        sha256sum IntelProCube-0.7.0.1-linux-x64.tar.gz
        ```

        屏幕显示 `efc5765ca402d0af00b42489dd61a74481531875b871517af5c0bca9d7387df9`。Linux 版适用 x86-64。

    数值不同时请重新下载。每个版本的值都列在 Release 页的 `SHA256SUMS.txt`。

2. **解压**

    === "macOS"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-macos-arm64.tar.gz -C ~/ipro
        ```

    === "Linux"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-linux-x64.tar.gz -C ~/ipro
        ```

    解压后得到 `~/ipro/IntelProCube`，本站写作 `<IntelProCube>`。命令行工具要在这个目录下运行，因为它从 `chips/` 读取芯片配置、分区表与 boot2 镜像。

3. **确认可以运行**

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --help
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --help
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --help
        ```

    屏幕以用法说明开头，例如：

    ```text
    usage: ipro_iot_tool_macos [-h] [--list-ports] --chipname CHIPNAME
                               [--interface INTERFACE] [--port PORT]
                               [--baudrate BAUDRATE] [--xtal XTAL]
                               [--chip-variant CHIP_VARIANT] [--dts DTS] [--pt PT]
                               [--boot2 BOOT2] [--firmware FIRMWARE] [--mfg MFG]
    ...
    ```

4. **让 `build_freertos.sh` 找到工具**（macOS／Linux）：设置 `IPRO_FLASH_TOOL`，或把 `<IntelProCube>` 加入 `PATH`。

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ```

</div>

## 连接控制台线 { #usb-serial }

Reef 板上没有 USB 转 UART 芯片：USB-C 只负责供电与板上 USB 设备功能，控制台与烧录都通过 U6 上的适配器或 IPRO Debug Probe。

<div class="ipro-steps" markdown>

1. **把适配器或 Debug Probe 连接到电脑**（暂时不必接开发板），查看新增的串口：

    === "macOS"

        ```bash
        ls /dev/cu.*
        ```

        USB 转 UART 适配器显示为 `/dev/cu.usbserial-XXXX`（名称取决于适配器）；IPRO Debug Probe 显示两个 `/dev/cu.usbmodem…`，名称以 `02` 结尾的是控制台。

    === "Linux"

        ```bash
        ls /dev/ttyUSB* /dev/ttyACM*
        ```

        适配器通常显示为 `/dev/ttyUSB0`；IPRO Debug Probe 显示两个 `/dev/ttyACM*`。

    === "Windows"

        打开“设备管理器”→“端口 (COM 和 LPT)”，比较插入前后的列表，多出来的就是新的 COM 口（例如 `COM5`）；IPRO Debug Probe 会多出两个。

2. **没有新增串口时**：换一根确认能传输数据的 USB 线；操作系统无法识别适配器时，安装适配器厂商提供的驱动程序；Debug Probe 请联系 INTELPRO。

3. **Linux 的权限**：打开串口时出现 `Permission denied`，用 `ls -l /dev/ttyUSB0` 查看串口所属的用户组（常见为 `dialout`），把自己加入该用户组后重新登录：

    ```bash
    sudo usermod -aG dialout $USER
    ```

</div>

Debug Probe 的两个串口如何区分、Reef 各应用在 USB-C 上显示为什么设备，见[烧录与串口：识别串口](flash-and-monitor.md#ports)。

## 验证结果 { #verify }

在 SDK 根目录构建出厂固件（macOS／Linux）：

```bash
./build_freertos.sh ipro7ai_reef_demo
```

成功时的输出：

```text
Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

→ Building ipro7ai_reef_demo...
✓ Build succeeded (14s)
  Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
  Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
```

构建时间与文件大小会因主机与工具链不同而略有差异。在 Windows 上通过 VS Code Extension 的 `IPRO: Build` 或 `build_freertos.ps1` 确认，见 [Windows 安装与 VS Code](windows.md#verify)。

## 两种环境的差异 { #choose }

| 任务 | macOS／Linux | Windows |
|---|---|---|
| 安装工具 | 系统包管理器，加上 INTELPRO 提供的工具链，以及从 GitHub 下载的 IntelProCube | Online Setup（工具链、CMake／Ninja／Python、IntelProCube、OpenOCD、VS Code Extension） |
| 构建 | `make -C apps/<分类>/<应用>` 或 `./build_freertos.sh` | VS Code Extension 的 `IPRO: Build` |
| 烧录 | IntelProCube 命令行工具，或 `./build_freertos.sh … flash` | `ipro_iot_tool.exe` |
| 控制台 | `screen`、`picocom` 等终端程序；`tools/serial_monitor.py` | PuTTY 等终端程序，或 Extension 的 Serial Monitor |
| 自动化（`build_freertos.sh`、`tools/serial_monitor.py`） | 可用 | 不可用：两者需要 bash 与 POSIX termios |
| Zephyr（`tools/zephyr/`） | 可用 | SDK 未提供 Windows 流程 |

本站的命令行示例以 macOS／Linux 为准。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| 计算出的 SHA-256 与 Release 页面不同 | 下载不完整或文件损坏 | 删除后重新下载 |
| `No cmake found. Install cmake or provide bundled cmake at …` | PATH 中没有 `cmake`，且随附的 CMake 无法在此主机上运行（随附版仅适用于 Linux x86-64） | 按[安装构建工具](#host-tools)安装 CMake 3.15 及以上版本 |
| `riscv64-unknown-elf-gcc: No such file or directory` | 工具链不在 `/opt/toolchain/riscv_ipro7/` | 按[安装 RISC-V 工具链](#toolchain)设置 `CROSS_COMPILE` |
| `Flash tool not found: ipro_iot_tool_macos` | 未设置 `IPRO_FLASH_TOOL`，PATH 中也没有 IntelProCube | 按[安装 IntelProCube](#intelprocube) 第 4 步设置 |
| 插上适配器后没有新的串口 | USB 线只能充电，或缺少驱动程序 | 换线；安装适配器厂商的驱动程序 |
| Linux 打开串口时出现 `Permission denied` | 用户不在串口所属的用户组中 | 加入 `dialout` 等用户组后重新登录 |
| macOS 打开 `/dev/tty.*` 后卡住 | `tty.*` 会等待 carrier detect 信号 | 改用 `/dev/cu.*` |

## 下一步 { #next-steps }

- 使用 Windows：[Windows 安装与 VS Code](windows.md)
- 环境已就绪：[第一个 FreeRTOS 应用](first-app-freertos.md)
- 命令行参考：[macOS／Linux 命令行](command-line.md)
