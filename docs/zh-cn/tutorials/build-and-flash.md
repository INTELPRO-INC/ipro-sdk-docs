---
title: "构建与烧录流程"
description: 在 IPRO7AI Reef EVK 上反复执行的修改、构建、烧录、监视循环：用 build_freertos.sh 一行完成、切换替代配置、干净构建、查看内存占用。
migrate_from:
  - "tutorials.html — 教學 2"
---

# 构建与烧录流程

日常开发的循环是“修改代码 → 构建 → 烧录 → 看控制台”。本教程在 IPRO7AI Reef EVK 上修改出厂固件 `ipro7ai_reef_demo` 的启动标题，用 `build_freertos.sh` 一行完成构建、烧录和监视，并在控制台看到修改后的文字；之后介绍替代配置、干净构建和内存占用。首次安装与烧录请先完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)。

## 前提条件 { #prerequisites }

- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)：板上正在运行 `ipro7ai_reef_demo`，控制台能响应 `reef selftest`。
- macOS 或 Linux。`build_freertos.sh` 需要 bash；Windows 改用 PowerShell 的 `build_freertos.ps1`（动作和选项相同），或用 VS Code Extension 构建和烧录，见 [Windows 安装与 VS Code](../get-started/windows.md#command-line)，循环相同。
- 以下命令都在 SDK 根目录执行，示例以 macOS 为准。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **设置环境变量**：在这个终端窗口中设置一次，后面的命令都会用到。

    ```bash
    export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
    export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
    export IPRO_FLASH_PT=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
    ```

    Linux 改用 `ipro_iot_tool_linux` 和 `/dev/ttyUSB0`。`IPRO_FLASH_PT` 会作用于这个窗口中的每一次 `flash`；改烧带有自己分区表的应用时，用 `unset IPRO_FLASH_PT` 清除，或用 `-P` 覆盖。

2. **修改代码**：用编辑器打开 `apps/platform/ipro7ai_reef_demo/main.c`，在 `main()` 的启动标题后面加上自己的文字：

    ```c title="apps/platform/ipro7ai_reef_demo/main.c"
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **构建、烧录并监视**：关闭打开着这个串口的终端程序，然后执行：

    ```bash
    ./build_freertos.sh -t 15 build flash monitor ipro7ai_reef_demo
    ```

    板上的固件收到 `reboot_dl` 后自行进入下载模式，无需按键。输出依次如下（节选）：

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    → Building ipro7ai_reef_demo...
    ✓ Build succeeded (14s)
      Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
      Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
    → Entering download mode...
    reboot to download mode
    → Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
    [...] - Chip name is ipro7
    ...
    [...] - [All Success]
    ✓ Flash succeeded (…)
    → Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
    [serial_monitor] Sent: reboot
    ...
    I (…) REEF:   IPRO7AI Reef carrier demo - my build
    ...
    [serial_monitor] TIMEOUT after 15s
    ✗ Action 'monitor' failed — stopping.

    Summary:
      ✓ build
      ✓ flash
      ✗ monitor (exit 2)
    ```

    `monitor` 读满 `-t` 指定的秒数后以退出码 2 结束，脚本把它列为失败，这是正常的：只要 `build` 和 `flash` 都是 ✓，新固件就已经在板上运行。

4. **交互确认**：用终端程序打开控制台（例如 `screen /dev/cu.usbserial-XXXX 115200`），输入 `reef status` 或 `led 0 40 0`，确认新固件正常响应。再次烧录前先关闭终端程序。

5. **重复**：之后每次修改，重复步骤 3 即可。只想确认能否编译时，只执行 `build`：

    ```bash
    ./build_freertos.sh build ipro7ai_reef_demo
    ```

</div>

## 验证结果 { #verify }

- `Summary` 中 `build` 和 `flash` 都是 ✓。
- 控制台的启动信息中出现 `IPRO7AI Reef carrier demo - my build`。
- 按 SW3、SW4、SW5 时 LED 仍然亮红、绿、蓝，`reef selftest` 的输出与修改前相同。

## build_freertos.sh 动作与选项 { #actions }

本教程用到 `build`、`flash`、`monitor`，以及 `-t`（监视秒数）、`-d`（替代配置）、`-P`（分区表）。动作按顺序执行，任一动作失败即停止。其他动作（`clean`、`size`、`test`）以及全部选项、环境变量见 [macOS／Linux 命令行](../get-started/command-line.md#build-script)。

## 替代配置与构建目录 { #variants }

同一个应用可以有多个配置文件。替代配置用 `-d` 选择，构建在 `build_<名称>/` 中，应用目录的 `.config` 不受影响：

```bash
./build_freertos.sh -d defconfig_wifi_ipro6s build ipro7ai_reef_demo        # 构建于 build_wifi_ipro6s/
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam       # USB 网络摄像头
```

- `flash`、`size` 根据 `-d` 查找镜像文件：分开执行时每次都要加上相同的 `-d`。
- 构建时配置文件会被复制为 `build_<名称>/.config`；要修改配置，请修改应用目录中的原文件。
- 烧录 `ipro7_uvc_cam` 的 `defconfig_reef_ov5640` 并接上 OV5640 后，Reef 的 USB-C 上会出现 USB 摄像头（`3896:0701`），用电脑的相机应用即可看到画面。
- Reef 可用的全部配置和构建命令见 [Reef 的构建配置](../get-started/command-line.md#reef-configs)；需要 boot2 或 `mfg` 数据的应用，首次烧录见[烧录与串口](../get-started/flash-and-monitor.md#partition-tables)。

## 干净构建 { #clean-build }

修改 `.config` 或替代配置之后，尤其是 Flash 大小、PSRAM、AI 或 BLE 控制器相关的选项，先清除再构建。`clean` 只删除对应的构建目录：

```bash
./build_freertos.sh clean build ipro7ai_reef_demo                            # 删除并重建 build/
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo   # 删除并重建 build_wifi_ipro6s/
```

`clean` 完成时打印 `✓ Clean complete`。

## 查看内存占用 { #memory-usage }

链接时会打印各内存区域的占用。用 `make` 构建时直接显示在终端中；用 `build_freertos.sh` 时写在 `build.log` 里：

```bash
grep -A5 "Memory region" apps/platform/ipro7ai_reef_demo/build/build.log
```

`ipro7ai_reef_demo` 默认配置的结果：

```text
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
```

- `flash` 是链接时的 Flash 上限。`ipro7ai_reef_demo` 默认按 1 MB 布局链接（构建配置阶段打印 `-- IPRO7 flash: 1M (default, on-chip)`）；Reef 的封装内 Flash 报告 JEDEC `0xEF4015`（2 MB）时，可在 `.config` 中加入 `CONFIG_IPRO7_FLASH_2M=y` 使用整颗 Flash。
- `flash` 百分比没有超出，并不代表固件放得进固件分区：请把 `Binary:` 显示的 `.bin` 大小与分区表中的固件分区对比。`partition_cfg_2M.toml` 的固件分区为 1180 KB。
- `ocram` 是芯片内部的 OCRAM。AI 关闭时，这个区域是 256 KB 减去 BLE 使用的 `CONFIG_EM_SIZE`，构建配置阶段会打印 `-- AI disabled: OCRAM=256KB` 之类的信息；AI 开启时分配方式不同。各区域由哪些配置决定，见[构建系统与配置](../guides/build-system.md)。

`size` 动作列出 `.elf` 的总大小和各段：

```bash
./build_freertos.sh size ipro7ai_reef_demo
```

```text
→ Size report for ipro7ai_reef_demo_IPRO7.elf

   text    data     bss     dec     hex filename
 235928   14008   49588  299524   49204 <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf
...
```

以上数字取自 V2.2.0 的构建，会因工具链版本和修改内容而有所不同。

## 脚本自动带入的参数 { #script-defaults }

`build_freertos.sh` 从应用的配置文件读出参数，Reef 无需另外指定：

| 项目 | 来源 |
|---|---|
| `--chip-variant` | 配置文件中有 `CONFIG_IPRO7AI_REEF=y` 时为 `IPRO7AI`；`-c` 或 `IPRO_CHIP_VARIANT` 可覆盖 |
| `--pt` | `-P` 或 `IPRO_FLASH_PT`；两者都没有时不带 `--pt`，由工具使用自己的默认分区表 |
| `reboot_dl` 与 `monitor` 的波特率 | 配置文件中的 `CONFIG_PLATFORM_UART_BAUDRATE`，未设置时为 115200（`ipro7_jpeg_decode` 的 Reef 配置为 921600） |
| 烧录波特率 | 固定为 921600 |

脚本无法传递 boot2 和 `mfg` 数据，`--chipname` 固定为 `ipro7`；这些情况请直接运行 IntelProCube，见[烧录与串口](../get-started/flash-and-monitor.md#build-script)。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| `✗ Build failed`，最后 30 行有编译错误 | 代码有错误 | 根据错误信息修正；完整记录在 `build.log` 中 |
| `✗ Flash failed`，工具输出停在握手阶段 | 板上固件没有响应 `reboot_dl`（没有 shell、死机或波特率不同），或串口被终端程序占用 | 关闭终端程序；按住 SW1、按一下 SW2、松开 SW1 后只执行 `flash` |
| `✗ Flash tool not found: …` | 新打开的终端窗口中没有 `IPRO_FLASH_TOOL` | 重新执行步骤 1，或把 `export` 加入 shell 的启动文件 |
| `✗ Binary not found: …` | `flash` 前没有构建，或缺少 `-d` | 加上 `build`，或加上构建时使用的 `-d` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 未设置 `IPRO_SERIAL_PORT`，且连接了多个串口 | 设置 `IPRO_SERIAL_PORT` 或加上 `-p` |
| 控制台看不到修改后的文字 | 烧录没有成功，或看到的是旧的输出 | 确认 `Summary` 中 `flash` 为 ✓；重新执行步骤 3 |
| 改了 `.config` 但行为没变 | 旧的构建结果仍在 | 执行 `clean build` |
| 改用其他应用后烧录失败或无法启动 | `IPRO_FLASH_PT` 仍指向上一个应用的分区表 | `unset IPRO_FLASH_PT`，按[分区表](../get-started/flash-and-monitor.md#partition-tables)用 `-P` 指定 |

## 下一步 { #next-steps }

- [创建第一个应用](first-own-app.md)：从零创建自己的应用。
- [测试应用](testing.md)：自动检查应用的输出。
- [macOS／Linux 命令行](../get-started/command-line.md)：`build_freertos.sh` 的全部动作、选项与限制。
- [构建系统与配置](../guides/build-system.md)：`.config` 键值、链接脚本与内存分配。
