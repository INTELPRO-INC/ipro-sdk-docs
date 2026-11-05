---
title: "安装 IPRO AI Studio"
description: 在 macOS 与 Windows 上安装 IPRO AI Studio 0.4.2、首次打开、允许使用摄像头、确认 Studio 找到 Reef，以及使用同一程序中的 ipro-ai 命令行。
---

# 安装 IPRO AI Studio

完成本页后，电脑上会有可以操作三个 Teach 工具的 IPRO AI Studio，以及同一程序提供的 `ipro-ai` 命令行；接上已烧录 Edge AI 固件的 IPRO7AI Reef EVK 时，Studio 会自动找到开发板。本页对应 IPRO AI Studio 0.4.2，界面为英文，按钮与页面名称按界面原文以粗体标示。

## 前提条件 { #prerequisites }

- 电脑：Apple 芯片的 Mac（macOS 11 及以上，不支持 Intel Mac），或 Windows 64 位（x64）。
- 安装包，从 [GitHub 上的 IPRO AI Studio 发布页](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载：
    - macOS：`IPRO-AI-Studio-0.4.2.dmg`
    - Windows：`IPRO-AI-Studio-0.4.2-windows-x64.zip`
- 需要确认连接时：一块已烧录 Edge AI 固件的 IPRO7AI Reef EVK 与一条支持数据传输的 USB-C 线。开发板尚未烧录时，先完成安装，再按[烧录 Edge AI 固件](firmware.md)烧录。

Studio 已内置模型转换与烧录所需的工具，使用 Teach、Sensor、Audio 三个页面不需要另外安装 Python 或其他程序。

## 安装 { #install }

<div class="ipro-steps" markdown>

1. **安装程序**

    === "macOS"

        打开 `IPRO-AI-Studio-0.4.2.dmg`，把 **IPRO AI Studio** 拖进“应用程序”文件夹。

    === "Windows"

        把 `IPRO-AI-Studio-0.4.2-windows-x64.zip` 解压到要存放程序的位置，例如 `C:\IPRO\`。解压后得到 `ipro-ai-studio` 文件夹，其中 `ipro-ai-studio.exe` 是图形界面程序，`ipro-ai.exe` 是命令行。运行所需的 Visual C++ 运行库已放在同一个文件夹中，不需要另外安装。

2. **首次打开**

    === "macOS"

        在 Finder 的“应用程序”文件夹中右键点按 **IPRO AI Studio**，选择“打开”，再在对话框中点击“打开”。也可以在终端中移除下载文件的隔离属性后直接打开：

        ```bash
        xattr -dr com.apple.quarantine "/Applications/IPRO AI Studio.app"
        ```

    === "Windows"

        在 `ipro-ai-studio` 文件夹中双击 `ipro-ai-studio.exe`。

    界面左侧的导航栏依次是 **Convert**、**Inspect**、**Verify**、**Board**、**Teach**、**Sensor**、**Audio**。前四个页面是模型转换、查看与比对工具；Teach 工具使用的是后三个页面。

3. **认识三个 Teach 页面**：可以点击导航栏，也可以用 **Go** 菜单或快捷键切换。

    | 页面 | 工具 | 快捷键（macOS／Windows） | 对应的固件模式 |
    |---|---|---|---|
    | **Teach** | 图像识别 | Command＋5／Ctrl＋5 | `image` |
    | **Sensor** | 传感器识别 | Command＋6／Ctrl＋6 | `sensor` |
    | **Audio** | 声纹识别 | Command＋7／Ctrl＋7 | `voice` |

4. **允许使用摄像头**：首次打开 **Teach** 页面时，macOS 会询问是否允许 IPRO AI Studio 使用摄像头，请选择“允许”。Teach 页面从 Reef 的 USB 摄像头画面中裁出训练图片，不允许时摄像头画面会一直为空。

</div>

## 操作系统权限 { #permissions }

| 项目 | macOS | Windows |
|---|---|---|
| 摄像头（Teach 页面） | 首次打开 Teach 页面时允许。如果曾经拒绝，Teach 页面会显示 `IPRO AI Studio is not allowed to use the camera.`；在“系统设置 → 隐私与安全性 → 摄像头”中打开 IPRO AI Studio，再重新打开 Studio | 在“设置 → 隐私和安全性 → 摄像头”中，确认已允许桌面应用访问摄像头 |
| 串口（三个页面） | 不需要另外授权 | 不需要另外授权 |

开发板的 USB 串口同一时间只能被一个程序使用。使用 Studio 时，请关闭其他打开了这个串口的程序，例如终端程序或另一个 Studio 窗口。它与 IPRO Debug Probe 上的控制台串口是不同的端口，两者可以同时打开。

## Studio 如何找到开发板 { #board-discovery }

Teach、Sensor、Audio 三个页面会自动查找开发板，不需要选择串口。Edge AI 固件根据当前模式，以 INTELPRO 的 USB VID 0x3896 枚举成不同的 USB 设备，每个页面只查找自己模式对应的那一个：

| 固件模式 | USB 设备名称 | VID:PID | 查找它的页面 |
|---|---|---|---|
| `image` | IPRO7 UVC Cam（USB 摄像头＋串口） | 3896:0705 | **Teach** |
| `voice` | IPRO Reef Voice（串口） | 3896:0720 | **Audio** |
| `sensor` | IPRO Reef Sensor（串口） | 3896:0721 | **Sensor** |

- 找到开发板时，页面上方状态栏的 **Board** 显示 `on USB`（Teach 页面）或 `ready`（Sensor、Audio 页面）。
- 开发板处于其他模式时，页面上方出现横幅，例如 `The Reef is in voiceprint mode.`，以及 **Switch to Teach**、**Switch to Sensor** 或 **Switch to Audio** 按钮。点击后开发板重启并进入该页面的模式（约 2 秒），三个模型都保留在板上，页面会在数秒内重新找到开发板。
- 板上的固件只有单一工具时，点击切换会显示 `This Reef's firmware runs one Teach only.`；请改为烧录 Edge AI 固件 `ipro_reef_teach`。
- 同时连接多块 Reef 时，页面会找到其中一块。不确定时一次只连接一块；命令行可以用 `--port` 指定。

## ipro-ai 命令行 { #cli }

`ipro-ai` 命令行就在 Studio 的可执行文件中，与 Studio 使用同一套部署与验证逻辑，适合用在脚本中。

=== "macOS"

    ```bash
    alias ipro-ai='"/Applications/IPRO AI Studio.app/Contents/MacOS/ipro-ai-studio" --cli'
    ipro-ai device list
    ```

    把 `alias` 那一行加入 shell 的配置文件（例如 `~/.zshrc`），之后打开的终端都能直接使用 `ipro-ai`。

=== "Windows"

    ```powershell
    cd C:\IPRO\ipro-ai-studio
    .\ipro-ai.exe device list
    ```

常用的设备命令：

| 命令 | 作用 |
|---|---|
| `ipro-ai device list` | 列出 USB 上的 Teach 工具：工具、串口、VID:PID、序列号 |
| `ipro-ai device info --json` | 固件名称与版本、平台版本、可切换的模式、当前工具的槽位容量与板上模型 |
| `ipro-ai model list --all` | 依次切换三个模式、列出各自的模型，最后切回原模式 |
| `ipro-ai deploy <套件.ipkg> --switch` | 先切换到模型套件所属的模式再部署，并回读板上模型的 CRC 进行确认 |

每个设备命令都可以加 `--port` 指定 Reef 的 USB 串口（省略时自动查找 USB 上唯一的一块），加 `--json` 得到机器可读的输出。完整命令与模型套件 `.ipkg` 的格式见《IPRO7AI Reef 开发套件使用手册》，可向 INTELPRO 索取，见[文档下载](../documents/index.md)。

## 验证结果 { #verify }

1. Studio 打开后，导航栏中有 **Teach**、**Sensor**、**Audio** 三个页面。
2. 接上已烧录 Edge AI 固件的 Reef，运行 `ipro-ai device list`，输出列出一块开发板，例如（`voice` 模式，macOS）：

    ```text
      voice   /dev/cu.usbmodemXXXX  USB 3896:0720  <序列号>
    ```

3. 运行 `ipro-ai device info --json`，输出的 `version` 字段显示 Edge AI 固件与平台版本：

    ```text
    "version": {"platform": "2.0", "proto": 2, "abi": 1, "store": 1,
                "tool": "voice", "fw": "ipro_reef_teach", "ver": "2.0.0", "chip": "IPRO7AI"},
    ```

4. 打开与开发板模式对应的页面，状态栏的 **Board** 显示 `on USB` 或 `ready`。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| macOS 显示无法打开“IPRO AI Studio” | 下载的程序带有隔离属性 | 在 Finder 中右键点按并选择“打开”，或运行上面的 `xattr` 命令 |
| Teach 页面显示 `IPRO AI Studio is not allowed to use the camera.` | 曾经拒绝摄像头权限 | 在系统的摄像头隐私设置中允许 IPRO AI Studio，再重新打开 Studio |
| `ipro-ai device list` 报告找不到 IPRO 设备（退出码 3） | 开发板没有启动、USB-C 线仅支持充电，或板上不是 Edge AI 固件 | 换一条支持数据传输的线；查看控制台的启动信息；按[烧录 Edge AI 固件](firmware.md)烧录 |
| 页面一直显示 `Looking for the board…` | 开发板处于其他模式，或另一个程序占用了开发板的串口 | 等待页面出现 **Switch to …**；关闭其他打开了该串口的程序 |

其他情况见[故障排除](troubleshooting.md)。

## 下一步 { #next-steps }

- [烧录 Edge AI 固件](firmware.md)：开发板还没有 Edge AI 固件时。
- [图像识别](image.md)、[声纹识别](voice.md)、[传感器识别](sensor.md)：逐步操作三个工具。
