---
title: "第一个 FreeRTOS 应用"
description: 在 IPRO7AI Reef EVK 上设置开关、连接控制台线，构建、烧录并运行出厂固件 ipro7ai_reef_demo，再用 reef selftest 检查板上功能。
migrate_from:
  - "getting-started.html#freertos-quickstart"
  - "getting-started.html#first-build"
---

# 第一个 FreeRTOS 应用

在 IPRO7AI Reef EVK V4.0 上构建并烧录出厂固件 `ipro7ai_reef_demo`，打开控制台后用 `reef selftest` 检查 LED、扬声器、SD 卡槽与摄像头。完成后，控制台出现 `ipro />` 提示符，板上每个功能模块都能通过 shell 命令操作。

## 前提条件 { #prerequisites }

- 已完成[准备开发环境](environment.md)：`./build_freertos.sh ipro7ai_reef_demo` 能构建成功，IntelProCube 的 `--help` 能运行。Windows 另见 [Windows 安装与 VS Code](windows.md)。
- IPRO7AI Reef EVK V4.0、USB-C 线、控制台线（3.3 V USB 转 UART 适配器或 IPRO Debug Probe）。
- 可选：OV5640 FLEX-24 摄像头模组、microSD 卡、8 Ω 扬声器（接 J_SPK）。没有这些时，自检的对应项目会显示未检测到。
- 以下命令行示例以 macOS 为准；Linux 把串口换成 `/dev/ttyUSB0`、工具换成 `ipro_iot_tool_linux`，Windows 按各步骤的标签页操作。

## 设置开关与接线 { #connect }

<div class="ipro-steps" markdown>

1. **拨开关**：SW7 拨到 **CAM**，SW8 拨到 **PWR**。SW7 在 GPIO 位置时摄像头没有供电；SW8 在 MEAS 位置时 IPRO7AI 改由 JP2 供电，见[开关与跳线](../hardware/boards/reef-evk.md#jumpers)。

2. **把控制台线接到 U6**（开发板先不要上电）：

    | U6 引脚 | 信号 | 接到 USB 转 UART 适配器 |
    |---|---|---|
    | 1 | NC | — |
    | 2 | GND | GND |
    | 3 | TX（GPIO20，Reef 发送） | RX |
    | 4 | RX（GPIO21，Reef 接收） | TX |
    | 5 | BOOT（经 1 kΩ 接 GPIO41） | 可选：DTR |
    | 6 | RESET（经 1 kΩ，低电平复位） | 可选：RTS |

    使用 IPRO Debug Probe 时，用两端引脚顺序对调的排线连接探针的 CN_UART：探针第 n 脚接 U6 第 7 − n 脚。

    !!! warning "排线方向"
        不要用两端引脚顺序相同的排线连接 Debug Probe：UART 与控制线会接错，探针的 3.3 V 也会接到 U6 的 RESET。

3. **上电**：接上 USB-C。绿色电源指示灯 LED2 亮起。U6 不供电，开发板只由 USB-C 供电。

4. **确认串口**：把适配器或探针连接到电脑，确认出现串口，例如 macOS 的 `/dev/cu.usbserial-XXXX`、Linux 的 `/dev/ttyUSB0`、Windows 的 `COM5`。Debug Probe 使用名称以 `02` 结尾的那一个，见[识别串口](flash-and-monitor.md#ports)。

</div>

## 构建 { #first-build }

<div class="ipro-steps" markdown>

1. **构建出厂固件**：在 SDK 根目录执行。Windows 改用 VS Code Extension 的 `IPRO: Build`（见[配置 VS Code Extension](windows.md#installation)），或 PowerShell 中的 `build_freertos.ps1`（见[命令行构建](windows.md#command-line)）。

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    构建配置阶段会输出 Reef 的板级配置，结尾输出内存用量与镜像文件路径（节选）：

    ```text
    -- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
    -- IPRO7 flash: 1M (default, on-chip)
    -- AI disabled: OCRAM=256KB
    ...
    Memory region         Used Size  Region Size  %age Used
               flash:      249944 B         1 MB     23.84%
               psram:       45376 B         8 MB      0.54%
               ocram:       32144 B       256 KB     12.26%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    [100%] Built target ipro7ai_reef_demo_IPRO7.elf
    ```

    数字会因工具链版本不同而略有差异。

2. **确认输出**

    ```bash
    ls apps/platform/ipro7ai_reef_demo/build/build_out/
    ```

    ```text
    ipro7ai_reef_demo_IPRO7.bin    用于烧录的镜像文件
    ipro7ai_reef_demo_IPRO7.elf    含调试符号
    ipro7ai_reef_demo_IPRO7.map    内存布局
    lib/
    ```

</div>

## 烧录与运行 { #flash-and-run }

<div class="ipro-steps" markdown>

1. **释放串口**：关闭所有打开着这个串口的终端程序。烧录与控制台共用同一个 UART。

2. **进入下载模式**：按住 **SW1（BOOT）**，按一下 **SW2（RESET）**，再松开 SW1。进入下载模式后控制台没有任何输出。

    开发板已在运行 SDK 固件（例如出厂的出厂固件）时，也可以在控制台输入 `reboot_dl`，屏幕输出 `reboot to download mode` 后即进入下载模式。U6 接了 DTR／RTS 自动下载线或 Debug Probe 时，见[进入下载模式](flash-and-monitor.md#download-mode)。

3. **烧录**：在 IntelProCube 目录下运行命令行工具。`--chip-variant IPRO7AI` 选择 Reef 的 Flash 引脚，`--pt` 指定 IntelProCube 随附的分区表。

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    工具逐行输出进度（节选，省略时间戳）：

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

    最后一行是 `[All Success]` 才算成功。即使烧录失败，工具也会以 0 退出，不能用退出码判断。

4. **打开控制台**：以 115200 baud、8N1、无流控打开同一个串口。

    === "macOS"

        ```bash
        screen /dev/cu.usbserial-XXXX 115200
        ```

        退出 `screen`：按 ++ctrl+a++，再按 ++k++，回答 `y`。

    === "Linux"

        ```bash
        picocom -b 115200 /dev/ttyUSB0
        ```

        退出 `picocom`：按 ++ctrl+a++，再按 ++ctrl+x++。没有 `picocom` 时用 `sudo apt install picocom` 安装。

    === "Windows"

        在 PuTTY 中选择 **Serial**，Serial line 填 `COM5`、Speed 填 `115200`，点击 **Open**。也可以使用 VS Code Extension 的 `IPRO: Serial Monitor`。

5. **复位**：按一下 **SW2（RESET）**。RGB LED 以蓝光呼吸一次后熄灭，控制台出现启动信息（节选，`(…)` 内是时间戳）：

    ```text
    I (…) REEF: ==========================================
    I (…) REEF:   IPRO7AI Reef carrier demo
    I (…) REEF:   UART0 TX=20 RX=21  RGB=G24  SPK_EN=G25(hi)
    I (…) REEF:   CAM: FLEX-24 D0-7=G0-7 XCLK=G22 RST=G34 PWDN=G35
    ...
    I (…) REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    ```

    按 ++enter++ 会出现提示符 `ipro />`。

</div>

## 验证结果 { #verify }

<div class="ipro-steps" markdown>

1. **按键**：依次按 SW3、SW4、SW5 与 SW1（BOOT），RGB LED 分别亮红、绿、蓝、白光。

2. **自检**：在控制台输入 `reef selftest`。约 3 秒内 LED 依次亮红、绿、蓝，扬声器发出 1 kHz 短音，输出如下（接了 OV5640、未插 SD 卡时）：

    ```text
    ipro />reef selftest
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: __rti_name_ov5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    | 行 | 检查内容 | 其他可能的结果 |
    |---|---|---|
    | `[3/4] SD slot` | 卡槽中是否有卡、卡槽电源 | 插卡时为 `something seated` |
    | `[4/4] camera bus` | 通过 SCCB 检测到的摄像头传感器与地址 | 未接摄像头时为 `no sensor`；OV2640 为 `__rti_name_ov2640 at 0x30` |

3. **列出命令**：输入 `help`，列出所有 shell 命令，包括 `reboot` 与 `reboot_dl`。

</div>

### 出厂固件的命令 { #commands }

| 命令 | 作用 |
|---|---|
| `reef status`、`reef selftest` | 开发板状态（引脚、按键、LED、功放、检测线）；自检 |
| `led <r> <g> <b>`、`led rainbow`、`led off` | RGB LED 颜色（0–255，例如 `led 40 0 0`）、彩虹效果、关闭 |
| `btn status`、`btn watch` | 按键状态与按下次数；实时列出按下与松开 |
| `spk tone <hz> <ms>`、`hp` | 扬声器输出正弦波；读取耳麦插入检测 |
| `mic rec pdm <秒>`、`mic rec headset <秒>`、`mic play`、`mic loop` | 用板上 PDM 麦克风或耳麦录音到 PSRAM（最长 10 秒）后播放，或实时监听 |
| `mic sdrec <来源> <名称> <秒>`、`mic usb <来源>` | 录制为 `sd:/rec/<名称>.wav`；让开发板通过 USB-C 作为 USB 麦克风，直到 `mic stop` |
| `sd mount`、`sd ls`、`sd test` | microSD（FatFS 挂载于 `sd:`） |
| `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on`、`cam bar off` | OV5640 摄像头（SW7 在 CAM） |
| `reboot`、`reboot_dl` | 重启；重启并进入下载模式 |

各命令的说明与摄像头上手顺序见 [IPRO7AI Reef EVK：出厂固件](../hardware/boards/reef-evk.md#reef-demo)。

## 一次完成：build_freertos.sh { #one-command }

在 macOS／Linux 上，`build_freertos.sh` 可以把构建、烧录与监视串成一条命令。它根据应用的配置判断要传入 `--chip-variant IPRO7AI`，并以应用的控制台波特率打开串口。板上已运行含 shell 的 SDK 固件时，它会先发送 `reboot_dl` 进入下载模式；首次烧录请先按上面的步骤手动进入下载模式。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

成功时依次输出 `✓ Build succeeded`、工具的烧录输出、`✓ Flash succeeded`，接着显示启动信息 30 秒。`monitor` 只读取输出，不能输入命令；结束时输出 `[serial_monitor] TIMEOUT after 30s`，脚本把它算作失败，这是正常的。所有选项见 [macOS／Linux 命令行](command-line.md#build-script)。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| 绿色电源灯 LED2 不亮 | USB-C 未接好，或电源没有供电 | 更换 USB-C 线或电源；只能由 USB-C 供电 |
| 烧录输出没有 `[All Success]`，停在握手阶段 | 开发板不在下载模式，或串口被终端程序占用 | 关闭终端程序；按住 SW1、按一下 SW2、松开 SW1 后重新烧录 |
| 出现 `flash jedec id: 00000000` 与 `IPRO FLASH MATCH TYPE FAIL` | Flash 引脚配置错误 | 在烧录命令中加上 `--chip-variant IPRO7AI` |
| 工具找不到 `chips/...` 下的分区表 | 不是在 IntelProCube 目录下运行 | 先 `cd <IntelProCube>` 再运行 |
| 烧录成功但控制台没有输出 | 开发板仍在下载模式、波特率或串口不对、RX／TX 接反 | 按 SW2 复位；以 115200 打开；macOS 使用 `/dev/cu.*`；对调适配器的 RX 与 TX |
| 控制台乱码 | 波特率不是 115200 | 以 115200、8N1 重新打开 |
| 控制台有输出，但输入命令没有反应 | 适配器的 TX 没有接到 U6 第 4 脚 | 检查 U6 第 4 脚（RX）的接线 |
| `[4/4] camera bus: no sensor` | 未接摄像头、排线未插好，或 SW7 不在 CAM | 拔掉 USB-C 后重新插好摄像头排线；SW7 拨到 CAM |
| 扬声器没有声音 | 没有接扬声器，或插头没插好 | 把 8 Ω 扬声器接到 J_SPK |
| `[3/4] SD slot: empty`，但已插卡 | 卡没有推到底 | 把卡推入直到卡住 |
| 构建时找不到编译器 | 工具链不在默认路径 | 设置 `CROSS_COMPILE`，见[准备开发环境](environment.md#toolchain) |

更多烧录与控制台问题见[烧录与串口](flash-and-monitor.md#troubleshooting)。

## 下一步 { #next-steps }

- [构建与烧录流程](../tutorials/build-and-flash.md)：修改代码后重新构建、烧录与监视。
- [创建第一个应用](../tutorials/first-own-app.md)与[测试应用](../tutorials/testing.md)。
- [烧录与串口](flash-and-monitor.md)：其他下载模式、分区表、boot2 与 `mfg` 数据。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：完整的开关、引脚与摄像头上手顺序。
