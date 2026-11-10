---
title: "烧录与串口"
description: IPRO7AI Reef EVK 的烧录与控制台参考：进入下载模式的四种方式、IntelProCube 命令行参数与分区表、boot2 与 mfg 数据、build_freertos.sh flash，以及控制台与串口识别。
migrate_from:
  - "getting-started.html#flashing"
  - "getting-started.html#serial-monitor"
  - "tools-debugging.html#flash-tool"
  - "tools-debugging.html#serial-monitor"
---

# 烧录与串口

FreeRTOS 应用通过 IntelProCube 命令行工具经 UART0 烧录，控制台也在同一个 UART 上；在 IPRO7AI Reef EVK 上，两者都经过调试排座 U6。本页整理 Reef 的所有烧录方式、各应用所需的分区表与额外镜像，以及如何打开控制台、如何识别串口。首次操作请先完成[第一个 FreeRTOS 应用](first-app-freertos.md)。

## 前提条件 { #prerequisites }

- IntelProCube 0.7.0.1：`ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`，见[准备开发环境](environment.md#intelprocube)。
- 已构建的镜像文件：`apps/<分类>/<应用>/build/build_out/<应用>_IPRO7.bin`；以 `DEFCONFIG=defconfig_<名称>` 构建时位于 `build_<名称>/build_out/`。
- 控制台线接在 U6，见[设置开关与接线](first-app-freertos.md#connect)。串口写法：macOS `/dev/cu.usbserial-XXXX`、Linux `/dev/ttyUSB0`、Windows `COM5`。

## 烧录工具 { #flash-tool }

在 IntelProCube 目录下运行命令行工具：它从 `chips/` 读取芯片配置，`--pt chips/...` 这类相对路径也以这个目录为基准。Reef 用到的参数：

| 参数 | Reef 的值 | 说明 |
|---|---|---|
| `--chipname` | `ipro7` | IPRO7 与 IPRO7AI |
| `--chip-variant` | `IPRO7AI` | Flash 引脚配置：`IPRO7AI` 为 `0x9`（Reef 的 QFN56），`IPRO7` 为 `0x2`。工具把它写入 `<IntelProCube>/chips/ipro7/eflash_loader/eflash_loader_cfg.ini` |
| `--port` | 控制台串口 | U6 上的适配器，或 Debug Probe 名称以 `02` 结尾的串口 |
| `--baudrate` | `921600` | 烧录波特率，与应用的控制台波特率无关 |
| `--firmware` | 应用的 `.bin` | 构建生成的镜像文件 |
| `--pt` | 分区表 | `.toml` 路径，或 `chips/ipro7/partition/` 下的文件名，见[分区表](#partition-tables) |
| `--boot2` | boot2 镜像 | 使用 boot2 的应用（`ipro_ble_remote`），见[首次烧录 ipro_ble_remote](#boot2-ab) |
| `--mfg` | `mfg` 分区数据 | AI 模型与 Teach 模式数据（`ipro_reef_teach`），见 [ipro_reef_teach](#mfg) |
| `--skip-ota` | — | 不生成 OTA 文件；`ipro_reef_teach` 使用自己的分区表时加上 |

`--help` 列出全部参数。

!!! warning "根据输出判断结果"
    即使烧录失败，工具也会以 0 退出。输出的最后一行是 `[All Success]` 才算成功。

## 进入下载模式 { #download-mode }

烧录前，IPRO7AI 必须处于启动 ROM 的下载模式。进入后控制台没有任何输出，直到复位为止。

| 方式 | 操作 | 适用情况 |
|---|---|---|
| 按键 | 按住 **SW1（BOOT）**，按一下 **SW2（RESET）**，再松开 SW1 | 任何时候；板上固件死机或没有 shell 时也可用 |
| `reboot_dl` | 在控制台输入 `reboot_dl`，屏幕输出 `reboot to download mode` | 板上正在运行含 shell 的 SDK 固件；`build_freertos.sh flash` 自动使用这种方式 |
| 自动下载线 | 适配器的 DTR 接 U6 第 5 脚（BOOT），RTS 接第 6 脚（RESET），板上分别经 1 kΩ 接到 GPIO41 与复位脚；这种自动下载线无需按键即可进入下载模式 | 适配器有 DTR 与 RTS 引脚 |
| IPRO Debug Probe | 在探针名称以 `02` 结尾的串口上发送控制字，见下方步骤 | 用 Debug Probe 连接 U6 |

!!! tip "IntelProCube 0.7.0.1 会自己进入下载模式"
    工具开始烧录前会先在串口发送 `reboot_dl`；用 IPRO Debug Probe 连接时，还会通过探针的 BOOT 与 RESET 线让芯片进入下载模式，烧录完成后再复位芯片。INTELPRO 用 0.7.0.1 通过 Debug Probe 在 Reef 上实测，无需按键或手动发送控制字，约 8 秒完成。板上固件没有 shell、又只用普通 USB 转 UART 线时，仍要用按键进入下载模式。下面的手动步骤供工具无法握手时使用。

用 Debug Probe 进入下载模式（以 macOS 为例，在 SDK 根目录执行）：

<div class="ipro-steps" markdown>

1. **拉高 BOOT 并复位**：依次发送 `IPRODL_1` 与 `IPRORST_RESET`。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    每行命令输出 `[serial_monitor] Sent: …` 与 `[serial_monitor] TIMEOUT after 1s`（未指定 `--wait-for` 时的正常结尾）；之后控制台不再有输出。

2. **烧录**：保持 BOOT 拉高，用同一个 `02` 串口执行[烧录步骤](#flashing)。

3. **释放 BOOT 并复位**：发送 `IPRODL_0` 与 `IPRORST_RESET`，开发板以新固件启动。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 3
    ```

</div>

## 烧录步骤 { #flashing }

<div class="ipro-steps" markdown>

1. **释放串口**：关闭所有打开着控制台串口的终端程序。

2. **进入下载模式**：任选[进入下载模式](#download-mode)中的一种方式。控制台不再有输出。

3. **烧录**：在 IntelProCube 目录下执行。以 `ipro7ai_reef_demo` 为例，其他应用按[分区表](#partition-tables)替换 `--pt` 并加上所需参数。

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

    输出开头列出本次烧录的参数，结尾是验证结果（节选，省略时间戳）：

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    [...] - Firmware is <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ...
    [...] - shake hand success
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

4. **复位并打开控制台**：按 SW2（RESET）让开发板以新固件启动，再按应用的波特率打开[控制台](#serial-monitor)。

</div>

## 分区表 { #partition-tables }

分区表决定固件、`mfg`（AI 模型）与其他数据在 Flash 中的位置。IntelProCube 随附通用的分区表（位于 `<IntelProCube>/chips/ipro7/partition/`，例如 `partition_cfg_2M.toml`）；需要特殊布局的应用把自己的 `.toml` 放在应用目录中。

| 应用（Reef 配置） | `--pt` | 其他参数 |
|---|---|---|
| `ipro7ai_reef_demo`（`.config`、`defconfig_wifi_ipro6s`） | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro7_uvc_cam`（`defconfig_reef_ov5640`、`defconfig_reef_rps`） | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro_ble_remote`（`defconfig_reef`） | `<SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml` | 首次烧录加 `--boot2`，见[下一节](#boot2-ab) |
| `ipro_reef_teach`（`.config`） | `<SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml` | `--skip-ota`；首次烧录加 `--mfg`，见 [ipro_reef_teach](#mfg) |
| 其他 Reef 应用 | 参见该应用的 README | — |

`ipro7ai_reef_demo` 默认链接 1 MB 的 Flash 布局，两种封装内 Flash 都放得下；如果启动信息显示 JEDEC `0xEF4015`（2 MB），可以在 `.config` 中加入 `CONFIG_IPRO7_FLASH_2M=y`，让链接器使用整颗 Flash。

## 首次烧录 ipro_ble_remote（boot2 与 A/B 分区表） { #boot2-ab }

`ipro_ble_remote` 的 Reef 配置支持 BLE OTA，需要 boot2 与 A/B 两个固件槽。第一次以有线方式烧录时，一并写入 boot2 与应用自己的分区表：

<div class="ipro-steps" markdown>

1. **构建**

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    生成 `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`。

2. **进入下载模式并烧录**：boot2 镜像随 IntelProCube 提供，不在 SDK 中。

    ```bash
    cd <IntelProCube>
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --boot2 chips/ipro7/builtin_imgs/boot2_v0.6.0/ipro_boot2_IPRO7_v0.6.0.bin \
        --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
        --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
    ```

    输出以 `[All Success]` 结尾。

3. **确认**：按 SW2 复位，在 115200 baud 的控制台中看到 boot2 标题 `[BOOT2] IPRO7 Boot2 v0.6.0`，接着应用输出 `[BLE] Advertising: IPRO-Remote`。

</div>

!!! warning "不要用 partition_cfg_2M.toml 做 OTA"
    在 Reef 上用标准的 `partition_cfg_2M.toml` 烧录 `ipro_ble_remote` 后执行 OTA，新固件会写入一个 boot2 从不启动的槽（0x12A000）。要使用 OTA，必须用上面的 boot2 与 `partition_cfg_2M_remote_ab.toml` 烧录。OTA 的步骤见 [OTA 固件更新](../guides/ota.md)。

## ipro_reef_teach（mfg 数据） { #mfg }

Edge AI 固件 `ipro_reef_teach` 使用自己的分区表，`mfg` 分区存放模式配置与声纹模型。第一次烧录时一并写入 `mfg` 数据：

```bash
make -C apps/ai/ipro_reef_teach
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 --skip-ota \
    --pt <SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml \
    --firmware <SDK>/apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin \
    --mfg <SDK>/reef_teach_mfg.bin
```

复位后控制台（115200）出现 `RTCH:   mode: image …`，USB-C 上出现 USB 摄像头与串口（`3896:0705`）。之后只更新固件时省略 `--mfg`，模式与模型会保留。模式切换与 IPRO AI Studio 的操作见 [IPRO AI Teach](../teach/firmware.md)。

## 用 build_freertos.sh 烧录 { #build-script }

在 macOS／Linux 上，`build_freertos.sh` 的 `flash` 动作按以下顺序工作：

1. 找到镜像文件：`build/`，或用 `-d defconfig_<名称>` 指定的 `build_<名称>/`。不存在时停止并提示 `Run 'build' first.`。
2. 找到工具：`IPRO_FLASH_TOOL`，否则为 PATH 中的 `ipro_iot_tool_macos`／`ipro_iot_tool_linux`。
3. 找到串口：`-p`，否则为 `IPRO_SERIAL_PORT`，否则为唯一连接的 `/dev/cu.usbmodem*`、`/dev/cu.usbserial*`、`/dev/ttyACM*` 或 `/dev/ttyUSB*`。
4. 以应用的控制台波特率（`CONFIG_PLATFORM_UART_BAUDRATE`，未设置时为 115200）发送 `reboot_dl`，等待 2 秒。
5. 执行 `<工具> --chipname ipro7 --chip-variant <变体> --port <串口> --firmware <bin> --baudrate 921600 [--pt <分区表>]`。变体：`-c`，否则为 `IPRO_CHIP_VARIANT`，否则根据配置文件判断（Reef 配置为 `IPRO7AI`）。分区表：`-P`，否则为 `IPRO_FLASH_PT`，否则不带 `--pt`。
6. 输出包含 `[All Success]` 时输出 `✓ Flash succeeded`，否则输出 `✗ Flash failed`。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

`-P` 请给出 `.toml` 的完整路径：脚本在当前目录运行工具，不会切换到 IntelProCube 目录。

!!! note "脚本做不到的事"
    - 不能传入 `--boot2`、`--mfg` 或 `--skip-ota`：`ipro_ble_remote` 的首次烧录与 `ipro_reef_teach` 的 `mfg` 数据请直接运行工具。
    - `--chipname` 固定为 `ipro7`，不能烧录 IPRO6S 镜像。
    - 板上固件没有 shell 或已死机时收不到 `reboot_dl`：先用按键进入下载模式。
    - `flash` 不会先构建；分开执行 `build` 与 `flash` 时，两次都要加相同的 `-d`。

## 串口控制台 { #serial-monitor }

控制台是 UART0（GPIO20 TX／GPIO21 RX，U6 第 3／4 脚），8N1、无流控。波特率由应用配置文件中的 `CONFIG_PLATFORM_UART_BAUDRATE` 决定，未设置时为 115200：

| 波特率 | Reef 配置 |
|---|---|
| 115200 | `ipro7ai_reef_demo`（两个配置）、`ipro_reef_teach`、`ipro_ble_remote`、`ipro_throughput_test`、`ipro_le_audio_headset`、`ipro7_uvc_cam`（两个 Reef 配置）、`ipro_ai_link`、`ipro_agora_sentino` |
| 921600 | `ipro7_jpeg_decode`（`defconfig_reef`） |

查询某个配置文件的波特率（没有输出表示未设置，即 115200）：

```bash
grep CONFIG_PLATFORM_UART_BAUDRATE apps/multimedia/ipro7_jpeg_decode/defconfig_reef
```

### 交互式终端程序 { #terminal }

要输入 shell 命令，请使用交互式终端程序：

=== "macOS"

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    退出：++ctrl+a++，++k++，回答 `y`。也可以使用 `minicom`、`picocom`（用 Homebrew 安装）。

=== "Linux"

    ```bash
    picocom -b 115200 /dev/ttyUSB0
    ```

    退出：++ctrl+a++，++ctrl+x++。也可以使用 `minicom -D /dev/ttyUSB0 -b 115200` 或 `screen`。

=== "Windows"

    PuTTY：Connection type 选择 **Serial**，Serial line 填 `COM5`，Speed 填 `115200`，点击 **Open**。也可以使用 Tera Term，或 VS Code Extension 的 `IPRO: Serial Monitor`。

烧录前一定要先关闭终端程序，否则工具无法打开串口。

### tools/serial_monitor.py { #serial-monitor-py }

SDK 随附的非交互式控制台工具，供脚本与自动化使用（macOS／Linux；只使用 Python 标准库的 termios，不需要 pyserial）。它打开串口，可以先发送一行命令，然后读取输出，直到超时或匹配到指定文本。

```text
python3 tools/serial_monitor.py <串口> [--baud 115200] [--timeout 30] [--send CMD] [--wait-for REGEX] [--log FILE]
```

| 选项 | 说明 |
|---|---|
| `--baud` | 波特率，默认 115200 |
| `--timeout` | 读取秒数，默认 30；`0` 表示持续读取到按下 ++ctrl+c++ |
| `--send` | 开始读取前发送的一行（自动加上 CR LF） |
| `--wait-for` | 匹配到这个正则表达式即结束 |
| `--log` | 同时把原始输出保存到文件 |

| 退出码 | 含义 |
|---|---|
| 0 | `--wait-for` 匹配到的文本包含 `PASSED` |
| 1 | 匹配到的文本不包含 `PASSED` |
| 2 | 超时，未匹配到（未指定 `--wait-for` 时，读完一定是 2） |
| 3 | 打开串口或发送命令失败 |

```bash
# 发送命令并读取 10 秒
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# 重启，等到 shell 就绪，并保存到文件
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot --wait-for "shell ready" --timeout 15 --log boot.log
```

### macOS 的串口 { #macos-cu }

macOS 上每个串口都有 `/dev/cu.*` 与 `/dev/tty.*` 两个名称。一律使用 `/dev/cu.*`：`/dev/tty.*` 会等待 carrier detect 信号，打开后卡住没有输出。

## 识别串口 { #ports }

| 连接方式 | macOS | Linux | Windows |
|---|---|---|---|
| U6 上的 USB 转 UART 适配器 | `/dev/cu.usbserial-XXXX`（取决于适配器） | 通常为 `/dev/ttyUSB0` | 设备管理器中新增的 COM 口 |
| IPRO Debug Probe | 两个 `/dev/cu.usbmodem…`：以 `02` 结尾的是控制台（UART 桥接），`04` 是 CCI 桥接 | 两个 `/dev/ttyACM*` | 两个 COM 口 |

IPRO Debug Probe 在 USB 上的名称是 `IPRO7 CMSIS_DAP`。在 Linux 与 Windows 上区分两个串口：以 115200 分别打开，按 SW2 复位，显示启动信息的那一个就是控制台。

Reef 的 USB-C 不是控制台。部分应用会让开发板在 USB-C 上以 INTELPRO 的 VID `0x3896` 显示为 USB 设备：

| 应用 | VID:PID | 主机看到的设备 |
|---|---|---|
| `ipro_reef_teach` image 模式 | `3896:0705` | USB 摄像头与串口（浏览器中的名称为“IPRO7 UVC Cam”） |
| `ipro_reef_teach` voice 模式 | `3896:0720` | 串口（CDC-ACM） |
| `ipro_reef_teach` sensor 模式 | `3896:0721` | 串口（CDC-ACM） |
| `ipro7_uvc_cam` | `3896:0701` | USB 摄像头 |
| `ipro_ai_link` | `3896:0704` | 串口（CDC） |
| `ipro7ai_reef_demo` 执行 `mic usb` 时 | `3896:0003` | USB 麦克风（UAC） |
| `ipro_agora_sentino` | `3896:0138`、`3896:0104` | USB 网络接口（NCM）、串口（CDC） |
| `ipro_le_audio_headset` | `3896:0001` | USB 音频（UAC，测试用 PID） |

查看主机上的 USB 设备：macOS 用 `system_profiler SPUSBDataType`，Linux 用 `lsusb`（例如列出 `ID 3896:0705`），Windows 在设备管理器中打开设备的“属性”→“详细信息”→“硬件 Id”（例如 `USB\VID_3896&PID_0705`）。

## 验证结果 { #verify }

- 烧录输出的最后一行是 `[All Success]`。
- 按 SW2 复位后，控制台以应用的波特率显示启动信息；含 shell 的应用按 ++enter++ 出现 `ipro />`，输入 `help` 列出命令。
- 使用 USB 功能的应用，主机上出现上表中的 VID:PID。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| 工具停在握手阶段，没有 `[All Success]` | 开发板不在下载模式，或串口被终端程序占用 | 关闭终端程序；用按键进入下载模式后重试 |
| 出现 `flash jedec id: 00000000` 与 `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` 不是 `IPRO7AI`，Flash 引脚错误 | 加上 `--chip-variant IPRO7AI` |
| 工具找不到分区表或 boot2 文件 | 相对路径不是以 IntelProCube 目录为基准 | 先 `cd <IntelProCube>`；SDK 中的文件使用完整路径 |
| `✗ Flash tool not found: ipro_iot_tool_macos` | 未设置 `IPRO_FLASH_TOOL`，PATH 中也找不到工具 | `export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` |
| `✗ Binary not found: …`，提示 `Run 'build' first.` | `flash` 不会先构建，或缺少构建时用的 `-d` | 在 `flash` 前加 `build`；加上相同的 `-d` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 连接了多个 USB 串口（Debug Probe 本身就有两个） | 用 `-p` 或 `IPRO_SERIAL_PORT` 指定控制台串口 |
| `No serial port found: pass -p PORT or set IPRO_SERIAL_PORT` | 没有检测到 USB 串口 | 检查适配器与驱动程序，见[准备开发环境](environment.md#usb-serial) |
| 烧录成功，但复位后控制台没有输出 | 开发板仍在下载模式（BOOT 被 DTR 或探针拉住），或波特率、RX／TX 不对 | 释放 BOOT（探针发送 `IPRODL_0`）后按 SW2；确认波特率；对调 RX 与 TX |
| 控制台乱码 | 波特率不匹配 | 按[控制台](#serial-monitor)中的波特率重新打开 |
| macOS 打开串口后卡住 | 使用了 `/dev/tty.*` | 改用 `/dev/cu.*` |
| `ipro_reef_teach` 显示 `NO MFG PARTITION` | 板上的分区表不是 `partition_reef_teach.toml` | 按 [ipro_reef_teach](#mfg) 用应用的分区表与 `--mfg` 重新烧录 |

## 下一步 { #next-steps }

- [构建与烧录流程](../tutorials/build-and-flash.md)：日常的修改、构建、烧录与监视循环。
- [macOS／Linux 命令行](command-line.md)：`build_freertos.sh` 的全部动作与选项。
- [调试与故障排除](../reference/debugging.md)
