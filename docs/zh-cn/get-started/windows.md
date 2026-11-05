---
title: "Windows 安装与 VS Code"
description: 在 Windows 上用 IPRO SDK Online Setup 3.6.0 一次安装 SDK V2.2.0、RISC-V 工具链、构建工具、IntelProCube 与 VS Code Extension，在 VS Code 或 PowerShell 中构建 IPRO7AI Reef EVK 的出厂固件，烧录并打开控制台。
migrate_from:
  - "windows-installation.html"
  - "vscode-extension.html#installation"
not_migrated:
  - "windows-installation.html#overview"
  - "windows-installation.html#package-contents"
  - "windows-installation.html#install-modes"
  - "windows-installation.html#full-install"
  - "windows-installation.html#extension-only"
  - "windows-installation.html#sdk-only"
  - "windows-installation.html#settings"
---

# Windows 安装与 VS Code

在 Windows 上用 IPRO SDK Online Setup 一次安装 SDK V2.2.0、RISC-V 工具链、构建工具（CMake、Ninja、Python）、IntelProCube、OpenOCD 与 VS Code Extension，构建 IPRO7AI Reef EVK 的出厂固件 `ipro7ai_reef_demo`，烧录后在 COM 口上看到控制台。构建与烧录可以在 VS Code 中进行，也可以在 PowerShell 中用 `build_freertos.ps1` 进行。

!!! info "工具链版本"
    Online Setup 安装的 Windows 版工具链是 GCC 13.1.1，并据此准备 SDK（处理内容记录在 SDK 根目录的 `PREBUILT-ARCHIVES-STRIPPED.json` 中）。SDK V2.2.0 在 macOS／Linux 上用 GCC 14 构建，两者构建出的镜像不同。

## 前提条件 { #requirements }

- Windows x64，能访问 GitHub（Online Setup 从公开的软件包清单与 GitHub Release 下载组件）。
- VS Code 1.102 及以上版本（也可以让安装程序下载）。
- IPRO7AI Reef EVK、USB-C 线，以及接在 U6 上的 IPRO Debug Probe 或 USB 转 UART 适配器，见[需要准备](index.md#what-you-need)。

## 安装 { #online-setup }

<div class="ipro-steps" markdown>

1. **下载安装程序**：从 [IPRO SDK Online Setup 最新版](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest)（3.6.0）下载 `IPRO-SDK-Online-Setup-3.6.0.exe`，无需登录 GitHub。

2. **校验**：在 PowerShell 中计算哈希值。

    ```powershell
    Get-FileHash .\IPRO-SDK-Online-Setup-3.6.0.exe -Algorithm SHA256
    ```

    `Hash` 列应与同一个 Release 的 `SHA256SUMS.txt` 中同名文件的值相同（不区分大小写）。安装程序没有代码签名，Windows 可能显示 SmartScreen 警告，请按公司的信息安全规定处理。

3. **选择 Full environment**：运行安装程序，在 **Choose packages** 中选择 **Full environment**。

4. **确认版本**：**Select package versions** 中各组件保持 latest，下拉菜单会直接显示对应的版本，例如 `latest (2.2.0)`。

5. **选择目录**：在 **Select Destination Location** 中保留默认的新文件夹 `C:\IPRO\versions\3.6.0-<日期时间>`，或填入一个尚不存在的文件夹（安装根目录，本页写作 `<安装目录>`）。

6. **选择附加任务**：尚未安装 VS Code 时勾选 **Install VS Code from Microsoft if absent**；保持勾选 **Install the selected Extension into VS Code**；要让 VS Code 直接使用这个环境，勾选 **Switch only selected component settings**；要在普通终端中直接运行工具，勾选 **Add installed tools to user PATH**。

7. **安装**：在 **Ready to Install** 中确认目录、模式与版本后点击 **Install**。

8. **查看完成页**：完成页会列出 SDK 的位置（`<安装目录>\sdk\IPRO-SDK-V2.2.0`）、命令行构建的第一条命令与工具链的位置。重新打开 VS Code 与终端，使新的设置与 PATH 生效。

</div>

安装时会修正 SDK 在 Windows 上的构建问题（识别 IPRO 工具链、CMake 4 搭配 Ninja 的构建信息、串口控制台），并加入 `build_freertos.ps1`；修改的文件记录在 SDK 根目录的 `WINDOWS-HOST-FIXES.json` 中。

## 配置 VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **确认 Extension 已安装**：在 Extensions 面板中搜索 `@installed IPRO`，应看到 IPRO SDK Extension（标识符 `ipro.ipro-sdk-extension`）。

2. **打开 SDK**：通过 **File → Open Folder…** 打开 `<安装目录>\sdk\IPRO-SDK-V2.2.0`，确认来源后允许 Workspace Trust。

3. **指定 SDK 根目录**：如果安装时没有勾选设置切换任务，按 ++f1++ 执行 `IPRO Setup: Set SDK Root`，选择同一个目录。

4. **检查环境**：执行 `IPRO Setup: Run Diagnostics`，确认 SDK 根目录、编译器、CMake、Python 与烧录工具都指向 `<安装目录>` 下。

5. **构建出厂固件**：执行 `IPRO: Go to Project…`，在 platform 分类中选择 `ipro7ai_reef_demo`，再执行 `IPRO: Build`。

</div>

Extension 的其他命令与设置见 [VS Code Extension](../guides/vscode.md)。

## 命令行构建 { #command-line }

`build_freertos.ps1` 是 `build_freertos.sh` 的 Windows 版，动作与选项相同：`build`、`clean`、`flash`、`monitor`、`size`、`test` 可以组合，按顺序执行。它使用同一个安装目录中的工具链、CMake、Ninja、Python 与 IntelProCube，没有加入 PATH 也能运行。Windows 默认不允许直接运行 `.ps1`；用 `powershell -ExecutionPolicy Bypass -File` 运行只影响这一次，不会改变系统设置。

<div class="ipro-steps" markdown>

1. **切换到 SDK 目录**

    ```powershell
    cd <安装目录>\sdk\IPRO-SDK-V2.2.0
    ```

2. **构建**

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 build ipro7ai_reef_demo
    ```

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    -> Building ipro7ai_reef_demo...
    [OK] Build succeeded (21s)
      Binary: ...\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin (219 KB)
      Toolchain: <安装目录>/toolchain/riscv_ipro7_win32/bin/riscv64-unknown-elf-gcc
      Log: ...\apps\platform\ipro7ai_reef_demo\build\build.log
    ```

    失败时会输出构建日志的最后 30 行与完整日志的位置。

3. **确认识别到 IPRO 工具链**

    ```powershell
    Select-String -Path apps\platform\ipro7ai_reef_demo\build\build.log -Pattern "\[toolchain\]"
    ```

    ```text
    -- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
    ```

</div>

其他用法：`-l` 列出所有应用，`-h` 显示所有选项，`-d defconfig_<名称>` 用替代配置构建，`-c <前缀>` 指定其他工具链（前缀以 `riscv64-unknown-elf-` 结尾）。

## 烧录 { #flash }

### 使用 IPRO Debug Probe { #flash-probe }

<div class="ipro-steps" markdown>

1. **接线**：SW7 拨到 CAM、SW8 拨到 PWR，IPRO Debug Probe 接 U6，再接上 Reef 的 USB-C，见[设置开关与接线](first-app-freertos.md#connect)。Probe 在 Windows 上会显示为两个 COM 口，见[识别串口](flash-and-monitor.md#ports)。

2. **烧录并查看启动信息**：在 SDK 目录执行：

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 flash monitor ipro7ai_reef_demo -w "IPRO7AI Reef carrier demo"
    ```

    脚本会选用 probe 的控制台端口，由 IntelProCube 让开发板进入下载模式、烧录并复位，看到启动信息后控制台结束：

    ```text
    [All Success]
    [OK] Flash succeeded (6s)
    ...
    [serial_monitor] MATCHED: IPRO7AI Reef carrier demo

    Summary:
      [OK] flash
      [OK] monitor
    ```

    IPRO7AI 开发板的应用会自动带上 `--chip-variant IPRO7AI` 与分区表 `partition_cfg_2M.toml`。连接了多个串口时，用 `-p COM5` 指定控制台所在的端口。

</div>

在 VS Code 中：用 `IPRO: Select Serial Port` 选择 probe 的控制台端口，在 `IPRO Config: Configure Flash…` 中把芯片配置设为 `IPRO7AI`、分区表设为 `partition_cfg_2M.toml`，再执行 `IPRO: Flash`。

### 使用 USB 转 UART 适配器 { #flash-uart }

<div class="ipro-steps" markdown>

1. **接线**：SW7 拨到 CAM、SW8 拨到 PWR，控制台线接 U6，接上 USB-C，见[设置开关与接线](first-app-freertos.md#connect)。

2. **找出 COM 口**：打开“设备管理器”→“端口 (COM 和 LPT)”，插上适配器后多出来的就是控制台，例如 `COM5`。

3. **进入下载模式**：按住 SW1（BOOT），按一下 SW2（RESET），再松开 SW1。

4. **烧录**：在 PowerShell 中切换到 `<安装目录>\IntelProCube` 执行：

    ```powershell
    cd <安装目录>\IntelProCube
    .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
        --port COM5 --baudrate 921600 `
        --pt chips/ipro7/partition/partition_cfg_2M.toml `
        --firmware <安装目录>\sdk\IPRO-SDK-V2.2.0\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

    输出的最后一行是 `[All Success]` 才算成功；工具失败时也以 0 退出。参数说明见[烧录与串口](flash-and-monitor.md#flash-tool)。烧录完成后按 SW2 复位。

</div>

## 控制台 { #console }

<div class="ipro-steps" markdown>

1. **打开控制台**：在 SDK 目录执行 `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 monitor ipro7ai_reef_demo -t 30`，或在 PuTTY 中选择 **Serial**，Serial line 填控制台的 COM 口、Speed 填 `115200`，点击 **Open**。也可以使用 Tera Term，或 VS Code Extension 的 `IPRO: Serial Monitor`。

2. **复位**：`build_freertos.ps1 monitor` 会发送 `reboot`；使用其他终端程序时按 SW2（RESET）。窗口中出现启动信息 `IPRO7AI Reef carrier demo`，按 ++enter++ 出现 `ipro />`。

3. **自检**：输入 `reef selftest`，预期输出见[第一个 FreeRTOS 应用](first-app-freertos.md#verify)。

</div>

烧录前先关闭终端程序，否则烧录工具无法打开 COM 口。

## 单独安装 SDK 或工具链 { #components }

在 **Choose packages** 中选择 **SDK only** 或 **Toolchain only** 时，版本页之后会出现 **Choose where to install**：

- **Add to this existing environment**：列表列出之前用 Online Setup 安装的环境及其中的 SDK、工具链，默认选择最新且带工具链的环境。SDK 放入该环境的 `sdk\`，直接使用环境中的工具构建；该环境中已有同一版本时会提示改选。已安装的文件一律不覆盖。
- **A new directory**：安装到新的文件夹。SDK 会按照 `/TOOLCHAINROOT=` 指定的、VS Code 设置中的、或最新的其他环境中的工具链准备，`build_freertos.ps1` 也会使用那套工具链。

静默安装时用 `/MODE=sdk /ENV=<环境文件夹>` 添加到已有环境。其他命令行参数见 [Online Setup 安装说明](https://github.com/INTELPRO-INC/ipro-sdk-releases/blob/main/INSTALLATION.zh-TW.md)。

## 验证结果 { #verify }

- 构建完成后生成：

    ```text
    apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

- 构建日志中有 `Vendor toolchain detected`。
- 烧录输出以 `[All Success]` 结尾。
- 复位后控制台显示启动信息与 `ipro />`，`reef selftest` 依次点亮 LED 并发出 1 kHz 短音。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| Windows 显示未知发布者或 SmartScreen 警告 | 安装程序没有代码签名 | 按公司的信息安全规定处理；不要关闭防护 |
| `.\build_freertos.ps1` 无法运行 | Windows 默认不允许运行 `.ps1` | 用 `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 ...` 运行 |
| 完成页提示找不到工具链 | SDK only 安装到新文件夹时没有可搭配的工具链 | 把 SDK 添加到带工具链的环境，或用 `/TOOLCHAINROOT=<工具链文件夹>` 重新安装 |
| Diagnostics 仍显示旧的 SDK 路径 | 工作区或用户设置中的 SDK 根目录指向旧版 | 执行 `IPRO Setup: Set SDK Root` 后重新执行 Diagnostics |
| 找不到 IPRO 命令 | Extension 不在当前的 VS Code Profile 中，或工作区未受信任 | 确认 Extension、Profile 与 Workspace Trust，执行 `Developer: Reload Window` |
| 设备管理器中没有新的 COM 口 | USB 线只能充电，或缺少适配器的驱动程序 | 换线；安装适配器厂商的驱动程序；Debug Probe 请联系 INTELPRO |
| 烧录输出没有 `[All Success]` | 开发板不在下载模式，或 COM 口被终端程序占用 | 关闭终端程序；使用适配器时重新用 SW1＋SW2 进入下载模式 |
| `flash jedec id: 00000000` | 没有加 `--chip-variant IPRO7AI` | 加上后重新烧录 |
| 控制台乱码或没有输出 | 波特率不是 115200、开发板仍在下载模式，或 RX／TX 接反 | 以 115200 打开；按 SW2；对调 RX 与 TX |

安装问题请保留 `<安装目录>\online-install.json`、`online-postinstall.log` 与同级的 `<安装目录>.download.log`。

## 下一步 { #next-steps }

- [第一个 FreeRTOS 应用](first-app-freertos.md)：出厂固件的自检与命令。
- [烧录与串口](flash-and-monitor.md)：其他下载模式、分区表、boot2 与 `mfg` 数据。
- [VS Code Extension](../guides/vscode.md)：Extension 的命令与设置。
