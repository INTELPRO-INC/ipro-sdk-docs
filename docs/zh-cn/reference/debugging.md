---
title: "调试与故障排除"
description: 在 IPRO7AI Reef EVK 上通过串口控制台与日志调试、进入下载模式、解读崩溃输出、分析构建结果、执行板上自检，以及构建、烧录、控制台与运行时常见问题的对照表。
migrate_from:
  - "tools-debugging.html#gdb-debugging"
  - "tools-debugging.html#crash-analysis"
  - "getting-started.html#debugging"
  - "getting-started.html#troubleshooting"
  - "getting-started.html#board-testing"
  - "getting-started.html#next-steps"
---

# 调试与故障排除

IPRO7 FreeRTOS 应用通过串口控制台调试：shell 命令与日志实时显示状态，崩溃时固件会自行打印异常分析与调用栈。本页的步骤以 IPRO7AI Reef EVK V4.0 为准。

## 串口控制台 { #debugging }

Reef 的控制台是 UART0（GPIO20 TX／GPIO21 RX），由调试排座 U6 引出，也是烧录用的 UART。U6 不供电，开发板由 USB-C 供电；接线见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#debug-connector)。

| 连接方式 | 主机上看到的串口 |
|---|---|
| 3.3 V USB 转 UART 线（接 U6 第 2、3、4 脚） | macOS `/dev/cu.usbserial-XXXX`，Linux `/dev/ttyUSB0`，Windows `COM5` 之类 |
| IPRO Debug Probe（用线序对调的排线接 U6） | 显示为 `IPRO7 CMSIS_DAP`，有两个 CDC 端口：名称以 `02` 结尾的是 Reef 控制台（例如 `/dev/cu.usbmodemXXXX02`），`04` 是 CCI 桥接 |

波特率由应用配置文件中的 `CONFIG_PLATFORM_UART_BAUDRATE` 决定，未设置时为 115200。Reef 的应用配置都是 115200，只有 `ipro7_jpeg_decode` 的 `defconfig_reef` 是 921600。其他开发板的配置中，`ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro_speaker_recog`、`ipro7_uvc_cam` 的 `.config`、`ipro7_jpeg_decode` 的 `.config` 与 `ipro_epd_el036` 也是 921600。格式为 8N1、无流控。

<div class="ipro-steps" markdown>

1. **打开控制台**：用任一串口终端程序打开端口。以 macOS／Linux 的 `screen` 为例：

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    按 Enter，出现 shell 提示符。退出 `screen`：按 Ctrl-A 再按 K。

2. **列出命令**：输入 `help`，终端列出内置命令与应用注册的命令。

3. **只发送一行命令并查看结果**（不需要交互式终端）：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "free" --timeout 3
    ```

    输出堆总量、剩余量与历史最低剩余量，3 秒后退出。

</div>

`CONFIG_SHELL=y` 的应用都有下列内置命令：

| 命令 | 用途 |
|---|---|
| `help` | 列出所有命令 |
| `ps` | 任务列表与 CPU 使用率 |
| `free` | 堆总量、剩余量与历史最低剩余量 |
| `time` | 启动后经过的时间 |
| `p <地址> [个数] [宽度]` | 读取内存（宽度 1、2 或 4 字节，默认 4） |
| `m <地址> <值> <宽度>` | 写入内存 |
| `memtrace <地址> [个数]`、`memtrace <地址> <值> <个数>` | 以 32 位字读取或填写内存（地址为十六进制） |
| `reboot` | 重启 |
| `reboot_dl` | 重启并进入下载模式，打印 `reboot to download mode` |
| `reboot_usb [code]` | 重启进入 boot2 的 USB 下载模式（仅对以 boot2 烧录的镜像有效），见[进入下载模式](#download-mode) |
| `watchdog`、`watchdog test` | 启用 `CONFIG_APP_WATCHDOG` 的应用（例如 `ipro_reef_teach`）：显示 AON 看门狗状态；`test` 停止喂狗，开发板在超时后重启 |
| `ls`、`cat`、`hexdump`、`pwd`、`cd`、`mkdir`、`rm`、`cp` | 文件系统命令，配置中有 `CONFIG_EVFS`、`CONFIG_EVFS_POSIX` 与 `CONFIG_IPRO_OSAL` 时才有 |

日志使用 `IPRO_LOGx` 宏（见 [API 参考](api/index.md#log-api)）。要查看调试级别的日志，在 `.config` 中设置 `CONFIG_LOG_DEFAULT_LEVEL=4` 后重新构建；此值是整数，随附应用默认为 3（信息）。

启动时值得留意的信息：

| 信息 | 含义 |
|---|---|
| `[XTAL] capcode <启动值> -> <设定值>` | 已应用 `CONFIG_IPRO7_XTAL_CAPCODE` 的晶体微调；Reef 未指定时默认为 95 |
| `[PSRAM] WARNING: init failed` | 应用启用了 `CONFIG_USE_PSRAM`，但 PSRAM 初始化失败 |
| `[BOOT2] IPRO7 Boot2 v0.6.0` | 镜像以 boot2 方式烧录（例如 `ipro_ble_remote` 的 Reef OTA 版本），boot2 先运行，再启动应用 |

## 进入下载模式 { #download-mode }

烧录前，Reef 必须处于下载模式。在下载模式下控制台没有任何输出；烧录完成后按一下 SW2（RESET）回到正常启动。

| 方法 | 适用情况 |
|---|---|
| 按键 SW1＋SW2 | 随时可用，包括首次烧录与固件崩溃时 |
| 控制台 `reboot_dl` | 板上已在运行含 shell 的 SDK 固件 |
| U6 的 DTR／RTS 自动下载线 | USB 转 UART 线的 DTR、RTS 接到 U6 第 5、6 脚 |
| IPRO Debug Probe 的关键字 | 用探针连接 U6 |

<div class="ipro-steps" markdown>

1. **按键**：按住 SW1（BOOT）不放，按一下 SW2（RESET），再松开 SW1。控制台保持静默，表示已进入下载模式。

2. **控制台命令**：在 shell 中输入 `reboot_dl`，或在主机上执行：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
    ```

    打印 `reboot to download mode` 后不再有输出。`build_freertos.sh flash` 会以应用的控制台波特率自动发送这个命令。

3. **自动下载线**：U6 第 5 脚（BOOT）与第 6 脚（RESET）经 1 kΩ 分别接 GPIO41 与复位脚。USB 转 UART 线的 DTR 接第 5 脚、RTS 接第 6 脚时，能控制 DTR／RTS 的主机程序无需按键即可让开发板进入下载模式：在 BOOT 为高电平时释放 RESET。

4. **IPRO Debug Probe**：在探针名称以 `02` 结尾的端口上，先发送 `IPRODL_1` 再发送 `IPRORST_RESET`；烧录期间保持 DL 为高；烧录完成后发送 `IPRODL_0` 与 `IPRORST_RESET` 回到正常启动：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    # 以 --port /dev/cu.usbmodemXXXX02 烧录，确认 [All Success]
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    最后一行执行后，控制台出现应用的启动信息。

</div>

**boot2 的 USB 下载模式**：以 boot2 烧录的镜像（例如 `ipro_ble_remote` 的 Reef OTA 版本）可用 `reboot_usb [code]` 重启进入 boot2 的 USB 下载模式，打印 `reboot to boot2 USB download (HBN_RSV3=0x555342FF)`；`code` 决定等待时间（`0x01` 2 秒、`0x02` 5 秒、`0xFF` 一直等待，默认 `0xFF`）。OTA 包校验失败时，boot2 也会停在这个 USB 救援模式。SDK 没有随附通过 USB 烧录的主机端工具；要重新烧录时，请用上面的 UART 方法进入下载模式。

## GDB 与调试器 { #gdb-debugging }

!!! info "未包含在 V2.2.1 中"
    以 JTAG 进行片上调试所需的 OpenOCD 配置与步骤未包含在 V2.2.1 中，请联系 INTELPRO。

- **ELF 带调试信息**：默认构建以 `-g3 -Os` 编译，`<构建目录>/build_out/<应用>_IPRO7.elf` 可直接交给工具链的 `riscv64-unknown-elf-addr2line` 或 `riscv64-unknown-elf-gdb` 做离线分析。烧录用的 `.bin` 不含符号。
- **预编译库不含调试信息**：IPRO BLE 控制器、RF、AI、ISP、LC3 与低功耗框架等预编译库已移除调试信息，只保留符号名称，无法在其中进行源码级单步执行。
- **IPRO Debug Probe**：在 Reef 上用作控制台桥接与下载模式控制（见[进入下载模式](#download-mode)）。探针的固件不在 SDK 中；硬件与接线见[文档下载](../documents/index.md)中的《Debug Probe 使用手册》。

## 崩溃分析 { #crash-analysis }

CPU 异常时，默认的异常处理程序会在控制台打印下列区块：

| 区块 | 内容 |
|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` | `MCAUSE`、`MEPC`、`MTVAL` 与异常类型（例如 `Illegal Instruction`、`Load Access Fault`） |
| `=== ADDRESS ANALYSIS ===` | 异常 PC 所在区域（FLASH／PSRAM／OCRAM）、返回地址 `ra`、栈指针 `sp` 是否在合法范围内 |
| `=== FAULTING TASK ===` | 发生异常的 FreeRTOS 任务名称与栈最低剩余量（0 表示该任务的栈曾经溢出） |
| 寄存器转储 | 异常发生时的通用寄存器 |
| `=== STACK BACKTRACE ===` | 以帧指针（`s0`）回溯的调用链，每层列出返回地址 |

<div class="ipro-steps" markdown>

1. **保存输出**：把控制台输出保存到文件，例如 `python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0 --log crash.log`，复现问题后按 Ctrl-C。

2. **把地址换算成源码行号**：用同一次构建的 `.elf` 查询异常 PC（`MEPC`）、`ra` 与回溯中的地址：

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-addr2line -f -C \
        -e apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf \
        0x1301c148 0x13004a2e
    ```

    每个地址打印两行：函数名称，以及 `文件:行号`。打印 `??:0` 表示地址不在这个 ELF 中，或 ELF 不是同一次构建的产物。

3. **复位开发板**：按一下 SW2（RESET）。

</div>

!!! warning "`==DUMP_READY:2000000==` 不断重复出现"
    `ipro7ai_reef_demo` 与 `ipro_reef_teach` 的 `.config` 设置了 `CONFIG_EXCEPTION_DUMP=y`：打印完上述诊断信息后，控制台约每 10 秒打印一次 `==DUMP_READY:2000000==`，最长 5 分钟，等待主机端工具读取内存。这个主机端工具未包含在 V2.2.1 中。请先保存上述诊断信息，再按 SW2 复位；不需要这个等待时，在 `.config` 中改为 `CONFIG_EXCEPTION_DUMP=n` 后重新构建。

| 配置 | 作用 |
|---|---|
| `CONFIG_ENABLE_FRAME_POINTER=y` | 以 `-fno-omit-frame-pointer` 编译，回溯才有完整的调用链；未设置时通常只能看到异常 PC 与 `ra` |
| `CONFIG_EXCEPTION_AUTO_REBOOT=y` | 打印完诊断信息后自动重启，复位原因记为 `HAL_RST_REASON_EXCEPTION`；适合量产，开发时建议关闭 |
| `CONFIG_EXCEPTION_DUMP=y` | 打印完诊断信息后等待主机端工具（见上方说明） |

`.config` 是按原样读入的，Kconfig 的默认值不会自动应用，上述配置需要明确写入。

其他致命信息来自 [FreeRTOS 钩子](api/index.md#rtos-platform)：

| 信息 | 原因 | 处理 |
|---|---|---|
| `[!] Stack overflow: <任务>` | 该任务的栈用尽 | 加大 `xTaskCreate()` 的栈深度（单位为 word）；随后的 `[STACKS]` 列表显示各任务的剩余量 |
| `[!] Malloc failed, requested: …` | 堆不足 | 用 `free` 命令观察剩余量，减少分配或启用 PSRAM；信息中的 `caller` 地址可用 `addr2line` 查出调用者 |
| `[!] ASSERT <文件>:<行号>` | `configASSERT()` 失败 | 根据文件与行号检查条件；`Caller` 地址可用 `addr2line` 查询 |

## 构建分析 { #build-analysis }

用 `build_freertos.sh` 构建时，完整输出写在 `<构建目录>/build.log` 中，失败时只在终端打印最后 30 行；加 `-v` 可直接查看完整输出。CMake 配置阶段的几行信息可用来确认构建使用了什么：

| 信息 | 含义 |
|---|---|
| `[toolchain] Vendor toolchain detected …` | 检测到 INTELPRO 提供的工具链，启用 IPRO7 专用的 DSP 扩展与优化；若显示 `Standard toolchain detected`，表示使用的是通用 RISC-V GCC |
| `[bluetooth] Using unified Zephyr 4.4 host (ipro_bt_host)` | 已包含 BLE Host |
| `[ipro_ble_controller] Using prebuilt …` | 实际链接的 BLE 控制器库文件名，可核对 `CONFIG_IPRO_BLE_CTLR_*` 是否符合预期 |
| `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` | Reef 构建自动加入晶体微调默认值；没有这一行时，请确认配置文件中有 `CONFIG_IPRO7AI_REEF=y` |
| `AI disabled: OCRAM=240KB (256-16)`、`AI+MM (EM=0): OCRAM=64KB …` | 本次构建的 OCRAM 区段大小：未启用 AI 时为 256 KB 减去 `CONFIG_EM_SIZE`；AI 与图像同时启用时缩小为 64 KB 或 48 KB |

链接器在构建最后打印各内存区段的使用量；内存不足时的分析方法见[大小与内存分析](tools.md#size-analysis)。

## 板上自检 { #board-testing }

Reef 出厂固件 `ipro7ai_reef_demo` 内置自检，适合在收到开发板、更换连线或烧录后确认硬件。SW7 拨到 CAM、SW8 拨到 PWR。

<div class="ipro-steps" markdown>

1. **确认启动**：按一下 SW2（RESET）。RGB LED 呼吸一次蓝光后熄灭，控制台出现 shell 提示符。

2. **执行自检**

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10
    ```

    约 3 秒内，LED 依次亮红、绿、蓝光，扬声器发出 1 kHz 测试音，输出下列内容（第 3、4 行视开发板状态而定）：

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: <传感器名称> at 0x<地址>
    done - keys: press any and run `btn status`
    ```

    插着 microSD 卡时第 3 行为 `something seated`；第 4 行为 `no sensor` 表示没有检测到摄像头。

3. **检查按键**：按 SW3、SW4、SW5 与 BOOT，LED 分别亮红、绿、蓝、白光；再发送 `btn status`，输出列出各键的状态与按下次数。

4. **查看整板状态**：发送 `reef status`，输出列出控制台引脚、按键、LED、扬声器、耳麦检测、SD 卡座与摄像头的状态。

</div>

`ipro_unit_test`（HAL 与公共组件的单元测试，`./build_freertos.sh test ipro_unit_test`）需要 IPRO7 EVB。

## 故障排除 { #troubleshooting }

### 构建 { #troubleshooting-build }

| 现象 | 原因 | 处理 |
|---|---|---|
| `No cmake found`，或在 macOS 上执行 `tools/cmake` 时出现无法执行的错误 | 系统中没有 CMake；随附的 `tools/cmake/` 是 Linux x86-64 版 | 安装 CMake 3.15 及以上版本（Zephyr 需要 3.20 及以上；例如 `brew install cmake`）并加入 `PATH`，再执行 `cmake --version` 确认 |
| 找不到 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc` | 工具链未安装或安装在其他路径 | 向 INTELPRO 获取工具链；安装在其他路径时 `export CROSS_COMPILE=<路径>/bin/riscv64-unknown-elf-` |
| `[ipro_ble_controller] CONFIG_EM_SIZE must match …` | `.config` 缺少 `CONFIG_EM_SIZE` | 加上 `CONFIG_EM_SIZE`（随附应用使用 16 或 32） |
| `bt54_iso2 needs at least 32 KB EM` | LE Audio 配置搭配了 16 KB EM | 设置 `CONFIG_EM_SIZE=32` |
| `unsupported variant` 或 `unsupported feature profile` | 控制器配置值不在提供的组合内 | `CONFIG_IPRO_BLE_CTLR_LIB` 用 `link1_periph`、`link1`、`link2`、`link4`；`CONFIG_IPRO_BLE_CTLR_FEATURE` 用 `bt52`、`bt54_iso2` |
| 设置了 `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE` 或 `CONFIG_IPRO_PM_PDS_CONNECTED` 后，在 `ipro_ble_controller` 配置阶段失败 | 这些配置会改为从源码构建 BLE 控制器，而软件包只提供预编译库 | 移除这些配置；需要这些功能请联系 INTELPRO |
| 链接错误 `undefined reference to adc_ioctl` | 使用了 `adc_channel_start()` 等 ADC 便捷宏 | 改用 `hal_adc_ioctl()` |
| 开启了 `CONFIG_AI_SUPPORT` 等功能，但依赖项没有随之启用 | 构建按原样读取 `.config`，不会应用 Kconfig 的 `select` 与 `depends on` | 明确写入依赖配置，例如 AI 需要 `CONFIG_USE_PSRAM=y`；见[构建系统与配置](../guides/build-system.md) |
| 用 `make` 构建后烧录到 Reef 没有反应 | 多数应用的 `.config` 是其他开发板的配置 | 以 `DEFCONFIG=defconfig_reef…` 构建 Reef 版本，见[常见问题](faq.md#reef-apps) |
| 链接器报告内存区段溢出 | 代码或数据超出 `flash`、`ocram` 等区段 | 按[大小与内存分析](tools.md#size-analysis)找出占用最大的部分；AI 与图像同时启用时 OCRAM 只剩 64 KB 或 48 KB |

### 烧录 { #troubleshooting-flash }

| 现象 | 原因 | 处理 |
|---|---|---|
| 没有 `[All Success]`，输出中出现 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` 与开发板不符；工具沿用了上一次写入的配置 | Reef 用 `--chip-variant IPRO7AI`，重新烧录 |
| 工具无法与开发板建立连接 | 开发板不在下载模式，或串口被其他程序占用 | 按[进入下载模式](#download-mode)操作，关闭串口监视程序后重试 |
| `build_freertos.sh flash` 显示 `Flash tool not found` | 找不到 IntelProCube 工具 | 设置 `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`，或把工具目录加入 `PATH` |
| `No serial port found` 或 `Several serial ports` | 没有或有多个 USB 串口 | 用 `-p` 指定，或设置 `IPRO_SERIAL_PORT` |
| `build_freertos.sh flash` 烧录 IPRO6S 应用失败 | 脚本固定传 `--chipname ipro7` | 在 IntelProCube 目录下直接以 `--chipname ipro6` 烧录，见 [IPRO6S](../hardware/chips/ipro6s.md) |
| IPRO6S 烧录出现 `[All Success]`，复位后控制台却没有输出 | IntelProCube 0.7.0 的 IPRO6 启动头时序不适用于 2 MB Flash 的 IPRO6S | 改用 IntelProCube 0.7.0.1 及以上，见 [IPRO6S](../hardware/chips/ipro6s.md#ipro6s-no-boot) |
| Reef 完成 BLE OTA 后完全没有输出 | 对以标准 `partition_cfg_2M.toml` 烧录的开发板做了 OTA | 进入下载模式，以 boot2 与 `partition_cfg_2M_remote_ab.toml` 重新烧录，见 [ipro_ble_remote](../examples/ipro_ble_remote.md) |

### 控制台 { #troubleshooting-console }

| 现象 | 原因 | 处理 |
|---|---|---|
| 乱码 | 波特率不符 | 按应用的 `CONFIG_PLATFORM_UART_BAUDRATE` 设置：Reef 多为 115200，`ipro7_jpeg_decode` 的 `defconfig_reef` 为 921600 |
| 完全没有输出 | 开发板处于下载模式；或 TX／RX 接反；或接的是 Debug Probe 的 `04` 端口 | 按 SW2 复位；确认 U6 第 3 脚（TX）接转接线的 RX、第 4 脚接 TX；探针用名称以 `02` 结尾的端口 |
| macOS 上程序卡住、没有输出 | 打开的是 `/dev/tty.*` | 改用 `/dev/cu.*` |
| `Resource busy`，或 `serial_monitor.py` 以退出码 3 结束 | 串口被其他程序占用 | 关闭其他终端或监视程序；用 `lsof /dev/cu.usbserial-XXXX` 找出占用者 |
| `cat` 只显示部分输出 | macOS 上用 `cat` 读取串口存在缓冲问题 | 改用 `tools/serial_monitor.py` 或其他串口终端程序 |
| `==DUMP_READY:2000000==` 不断重复 | 崩溃后在等待转储工具 | 见[崩溃分析](#crash-analysis) |

### 运行时与 BLE { #troubleshooting-runtime }

| 现象 | 原因 | 处理 |
|---|---|---|
| 控制台出现 `=== ENHANCED EXCEPTION ANALYSIS ===` | CPU 异常 | 按[崩溃分析](#crash-analysis)解读 |
| `[!] Stack overflow`、`[!] Malloc failed`、`[!] ASSERT` | 栈不足、堆不足或断言失败 | 见[崩溃分析](#crash-analysis)中的对照表 |
| `[PSRAM] WARNING: init failed` | 构建启用了 PSRAM，但 PSRAM 无法初始化 | 确认构建的是 Reef 配置（`CONFIG_IPRO7AI_REEF=y`）；仍失败请联系 INTELPRO |
| `cam probe` 或 `reef selftest` 显示 `no sensor` | SW7 不在 CAM 位置，或摄像头排线没有插好 | 把 SW7 拨到 CAM；拔掉 USB-C 后重新插好排线，再上电 |
| 开发板复位后配对数据消失，手机必须重新配对 | 未启用配对数据存储，或未在广播前加载 | 见[常见问题](faq.md#ble-bonding) |
| BLE 吞吐量远低于预期 | 连接参数、PHY 或 CPU 负载 | 见 [BLE 吞吐量测试](../tutorials/ble-throughput.md) |

## 下一步 { #next-steps }

- [工具命令行](tools.md)：构建、烧录与监视工具的完整选项。
- [测试你的应用](../tutorials/testing.md)：在 Reef 上测试自己的应用。
- [API 参考](api/index.md)：平台、BLE、HAL 与日志 API。
- [常见问题](faq.md)：构建、BLE、网络与 RTOS 的常见问答。
