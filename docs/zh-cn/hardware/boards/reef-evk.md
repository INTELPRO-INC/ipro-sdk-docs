---
title: IPRO7AI Reef EVK V4.0
description: IPRO7AI Reef EVK V4.0 的板载功能、开关与跳线、快速上手与下载模式、出厂固件、经 IPRO6S FIN 卡的 Wi-Fi、可运行的示例、USB 标识符与引脚对照
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK V4.0

<span class="ipro-badge">V4.0</span>

IPRO7AI Reef EVK 以 IPRO7AI（QFN56）为核心，Flash 与 PSRAM 都在芯片封装内。板上有 OV5640 摄像头排线座、PDM 数字麦克风、耳麦插孔与扬声器功放、microSD 卡座、RGB LED、按键，以及位置与引脚排列都与树莓派相同的 40-pin 扩展排针；仅由 USB-C 供电，没有 LCD 和电池。本页对应 V4.0 开发板（丝印“IPRO7AI REEF EVK V4.0”）；本站所有步骤都以这块板为准。

<figure>
  <img src="/ipro-sdk-docs/assets/images/reef-v4-top.jpg" alt="IPRO7AI Reef EVK V4.0 正面：上边缘为 40-pin 排针 J_IO，右上方为 SW1、SW2 与 PCB 天线，左边缘为 SW7、U6 与 microSD 卡座，下边缘为 JP3、扬声器座、耳麦插孔、SW8、JP2 与 USB-C" width="1500" height="1011" loading="lazy">
  <figcaption>IPRO7AI Reef EVK V4.0 正面</figcaption>
</figure>

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>SoC（QFN56），NPU、ISP、BLE、IEEE 802.15.4</span></div>
<div><strong>2 MB＋8 MB</strong><span>封装内 Flash 与 PSRAM</span></div>
<div><strong>40-pin</strong><span>J_IO，树莓派的位置与引脚排列，3.3 V</span></div>
<div><strong>U6</strong><span>控制台 UART，115200 baud</span></div>
<div><strong>USB-C</strong><span>唯一电源输入</span></div>
</div>

## 板载功能 { #features }

| 模块 | 内容 |
|---|---|
| 核心 | IPRO7AI（U1，QFN56）：RISC-V RV32IMAFC、NPU、ISP、2.4 GHz 射频（BLE、IEEE 802.15.4）；32 MHz 晶振（X1） |
| 内存 | 封装内 2 MB Flash 与 8 MB PSRAM；芯片内 256 KB OCRAM |
| 天线 | PCB 天线 E1（默认）；把 R2 的 0 Ω 电阻移到 R1，改接 u.FL 天线座 RF1 |
| 摄像头 | FPC1：0.5 mm 间距 24 pin 立式排线座，OV5640 FLEX-24 引脚定义，8 位 DVP；摄像头的 2.8 V 与 1.5 V 由板上稳压器供电 |
| 摄像头／GPIO 切换 | SW7 经 4 颗 SN74CB3Q3257 把 16 个摄像头引脚切换到 J_IO；切到 GPIO 时摄像头电源关闭 |
| 音频输入 | PDM 数字麦克风 MK1；耳麦麦克风经耳麦插孔 J2 接到模拟输入 AIN6、AIN7 |
| 音频输出 | IPRO7AI 的 GPDAC 经耳机放大级（TLV9061）到耳麦插孔 J2（3.5 mm，CTIA 接法）；并经 D 类功放 PAM8302A 到扬声器座 J_SPK（1.25 mm 2 pin，接 8 Ω 扬声器） |
| 存储 | microSD 卡座 CARD1（自弹式），4 位 SD 接口；卡检测与卡座电源各接一个 GPIO |
| USB | USB-C（USB1）：5 V 供电与 USB 2.0 Full-Speed 设备 |
| 调试 | U6：1.0 mm 间距 6 pin（SH1.0），控制台 UART、BOOT、RESET；接 IPRO Debug Probe |
| 按键与指示灯 | SW1 BOOT、SW2 RESET、SW3／SW4／SW5 用户按键（侧按式）；LED1 RGB LED（WS2812B-2020）、LED2 电源指示灯（绿） |
| 扩展 | J_IO：2 × 20、2.54 mm 间距排针，位置与引脚排列同树莓派 40-pin；信号均为 3.3 V |
| 电流测量 | SW8（PWR／MEAS）与 JP2，测量 IPRO7AI 的 3.3 V 电流 |
| 外形 | 85 × 56 mm，板厚 1.6 mm，六层板；四个 Ø2.75 mm 安装孔，孔距 58 × 49 mm，与 40-pin 排针的相对位置同树莓派，可用 M2.5 铜柱固定 |

规格依据 V4.0 设计文件（原理图与物料清单）。

### 开关与跳线 { #jumpers }

| 位号 | 位置 | 作用 |
|---|---|---|
| SW7 | CAM（默认） | 摄像头引脚接到 IPRO7AI，摄像头电源开启。使用摄像头时必须在 CAM |
| | GPIO | 16 个摄像头引脚改接到 J_IO（[引脚表](#j-io)中标 * 的引脚），两颗摄像头稳压器关闭 |
| SW8 | PWR | 正常使用：IPRO7AI 的 3.3 V 直接由板上电源供电 |
| | MEAS | 测量：IPRO7AI 的 3.3 V 改经 JP2 供电；JP2 必须接电流表或外部 3.3 V 电源 |
| JP3 | ON | microSD 卡座始终有电 |
| | GPIO | 卡座电源由 GPIO14 控制：低电平或未驱动时有电，高电平时断电 |
| JP2 | — | 3 pin：1＝3V3（板上 3.3 V）、2＝SOC（IPRO7AI 的 3.3 V）、3＝GND；仅在 SW8＝MEAS 时使用 |

测量 IPRO7AI 的电流：拔掉 USB-C，把电流表接在 JP2 的 1、2 脚之间（或把外部 3.3 V 电源接在 2、3 脚），SW8 拨到 MEAS，再接上 USB-C。测量完毕先拔掉 USB-C，把 SW8 拨回 PWR，再拆下电流表。测得的是 IPRO7AI 的 3.3 V 引脚及其去耦电容、启动引脚上拉电阻的电流，不含外设。

!!! warning "上电前"
    - 只从 USB-C 供电。J_IO 的 5 V 引脚（2、4 脚）是输出，不能从这里给开发板供电。
    - 所有 IO 都是 3.3 V 电平，不可接 5 V 信号。
    - 插拔摄像头排线前先拔掉 USB-C。
    - SW8 平时放在 PWR。放在 MEAS 时，若 JP2 没有接电流表或外部 3.3 V 电源，就不要接 USB-C：IPRO7AI 没有电，外设的 3.3 V 却会经 IO 引脚倒灌。

## 快速上手 { #quick-start }

完成后，开发板运行出厂固件 `ipro7ai_reef_demo`，并在控制台响应 `reef selftest`。主机需要 RISC-V 工具链与 IntelProCube v0.6.3（向 INTELPRO 获取）、CMake 3.15 及以上、GNU make 与 Python 3.8 及以上，见[开始使用](../../get-started/index.md)。

<div class="ipro-steps" markdown>

1. **设置开关并接线**：SW7 拨到 CAM、SW8 拨到 PWR。把控制台线接到 U6：3.3 V 的 USB 转 UART 线（引脚见[调试插座 U6](#debug-connector)），或用两端线序反向的排线接 IPRO Debug Probe。最后接上 USB-C。

    绿色电源灯 LED2 亮起。U6 不供电，开发板只由 USB-C 供电。

2. **找到串口**：在主机上列出串口。

    ```bash
    ls /dev/cu.usb*        # macOS
    ls /dev/ttyUSB* /dev/ttyACM*   # Linux
    ```

    USB 转 UART 线会出现一个串口，例如 `/dev/cu.usbserial-XXXX`。IPRO Debug Probe 会出现两个（设备名称 `IPRO7 CMSIS_DAP`）：名称以 `02` 结尾的是 Reef 控制台，`04` 是 CCI 桥接。Windows 在“设备管理器”中查看 `COM` 编号。

3. **构建出厂固件**：在 SDK 根目录执行

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    构建结束时打印 Flash 与 RAM 用量，镜像位于 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

4. **进入下载模式**：按住 SW1（BOOT），按一下 SW2（RESET），再松开 SW1。

    控制台不再有任何输出。其他方式见[下载模式](#download-mode)。

5. **烧录**：在 IntelProCube 目录执行（Linux 为 `./ipro_iot_tool_linux`，Windows 为 `ipro_iot_tool.exe`）

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    输出最后出现 `[All Success]` 才算成功；工具即使失败也以 0 退出。`--chip-variant IPRO7AI` 选用 QFN56 的 Flash 引脚。

6. **启动并自检**：按一下 SW2，以 115200 baud（8N1、无流控）打开控制台，输入 `reef selftest`。

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    启动日志中有 `IPRO7AI Reef carrier demo` 与 `shell ready - ...`，RGB LED 蓝光呼吸一次。`reef selftest` 约 3 秒内依次打印：

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: OV5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    第 3 行随是否插卡而不同；没接摄像头时第 4 行为 `no sensor`。按 SW3、SW4、SW5、SW1 分别亮红、绿、蓝、白光。

</div>

熟悉流程后，可以用 `build_freertos.sh` 一次完成构建、烧录与打开控制台。它根据应用的配置自动选用 `--chip-variant IPRO7AI`，以应用自己的波特率打开控制台；板上已有 SDK 固件时会先发送 `reboot_dl`，首次烧录则要先用按键进入下载模式：

```bash
export IPRO_FLASH_TOOL=<ICUBE>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <ICUBE>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

这个脚本无法写入 boot2 与 mfg 数据，`ipro_ble_remote` 的首次烧录与 `ipro_reef_teach` 请直接使用 IntelProCube。选项见[工具命令行](../../reference/tools.md)。

## 下载模式 { #download-mode }

烧录前，IPRO7AI 必须在复位时检测到 BOOT（GPIO41）为高电平，进入 ROM 的下载模式。进入后控制台没有任何输出；烧录完成后按一下 SW2 回到正常启动。

| 方式 | 操作 | 适用场景 |
|---|---|---|
| 按键 | 按住 SW1（BOOT），按一下 SW2（RESET），松开 SW1 | 任何时候，包括板上固件无响应时 |
| 控制台命令 | 在控制台输入 `reboot_dl` | 板上运行 SDK 固件时；`build_freertos.sh flash` 会自动发送 |
| 自动下载线 | U6 第 5 脚 BOOT 与第 6 脚 RESET 各经 1 kΩ 接到 IPRO7AI，接上 USB 转 UART 线的 DTR 与 RTS 即可由主机控制 | 使用带 DTR、RTS 的转接线时 |
| IPRO Debug Probe | 向探针以 `02` 结尾的串口写入 `IPRODL_1`，再写入 `IPRORST_RESET`；烧录完成后写入 `IPRODL_0`，再写入 `IPRORST_RESET` | 使用 IPRO Debug Probe 时 |

用 Debug Probe 进入下载模式（每行发送一个关键字）：

```bash
python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
```

烧录完成后用同样的方式发送 `IPRODL_0` 与 `IPRORST_RESET`，开发板正常启动。

使用 boot2 的镜像（例如 `ipro_ble_remote` 的 Reef 版）另有 `reboot_usb [code]`：重启后进入 boot2 的 USB 下载模式（默认一直等待）。OTA 包校验失败时，boot2 也会停在这个 USB 救援模式。

## 出厂固件 ipro7ai_reef_demo { #reef-demo }

板上每个功能模块各有一组 shell 命令，`help` 列出全部命令。Reef 没有 LCD，摄像头用 shell 命令检查。

| 模块 | Shell 命令 | 说明 |
|---|---|---|
| 状态与自检 | `reef status`、`reef selftest` | 引脚、按键、LED、功放与检测线状态；一次运行全部自检 |
| RGB LED | `led <r> <g> <b>`、`led rainbow`、`led off` | 设置颜色（0–255）或彩虹效果 |
| 按键 | `btn status`、`btn watch` | 去抖后的状态与按下次数；实时列出按下／松开事件 |
| 扬声器与耳机 | `spk tone <hz> <ms>`、`hp` | GPDAC 输出正弦波；命令加上 `hp` 时功放静音、只从耳机输出。单独的 `hp` 读取耳麦插入检测（GPIO26） |
| 音频输入 | `mic rec <来源> <秒>`、`mic play`、`mic loop` | 来源为 `pdm`（板载麦克风）或 `headset`（耳麦）；以 16 kHz 录到 PSRAM（最长 10 秒）后播放，或实时监听 |
| 录音到 SD 卡 | `mic sdrec <来源> <名称> <秒>` | 录制为 `sd:/rec/<名称>.wav` |
| USB 麦克风 | `mic usb <来源>` | 开发板经 USB-C 成为 16 kHz 的 USB 麦克风 |
| SD 卡 | `sd mount`、`sd ls`、`sd test`、`sd bench`、`sd power` | FatFS 挂载在 `sd:`；写入、读回并校验；JP3 在 GPIO 时，`sd power` 通过 GPIO14 开关卡座电源 |
| FIN 卡 | `fin`、`fin cycle` | 卡座上 IPRO6S FIN 卡的状态；JP3 在 GPIO 时给卡片重新上电 |
| 摄像头 | `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on` | OV5640 以 YUV422 1280×720 经 ISP 通道 0；帧数、帧率与错误计数、ASCII 缩略图、传感器彩条 |

应用 README 中的 AUX-IN 输入（`mic rec aux`）是上一版底板的功能，V4.0 没有 AUX-IN 插座。

摄像头上手的顺序（SW7 在 CAM）：

```text
cam probe        经 SCCB 读取传感器 ID
cam start        开始采集
cam status       间隔一秒执行两次：帧数增加、错误数不变
cam bar on       切换到彩条
cam snap         ASCII 缩略图应为竖直色带
cam bar off
cam snap         拍到实际画面
```

## Wi-Fi 与 RTSP 摄像头视频流 { #wifi-rtsp }

把 IPRO6S FIN 卡插入 microSD 卡座，Reef 即可经 SDIO 连上 Wi-Fi，并通过 RTSP 提供摄像头的 MJPEG 视频流（`rtsp://<ip>:8554/av0_0`）。

- **FIN 卡固件**：IPRO6S 的 `ipro6_if_wifi`，用 `defconfig_ipro6_sdio` 构建：

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio   # build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin
    ```

    更新方式见 [IPRO6S](../chips/ipro6s.md)；卡片已连上 Wi-Fi 时，可在 Reef 控制台用 `ipro6s_ota <http url>` 更新。

- **Reef 固件**：`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s`：

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # build_wifi_ipro6s/build_out/
    ```

- **开关**：JP3 放在 GPIO，`fin cycle` 才能给卡片重新上电。

连接后在控制台输入 `ipronet_up <ssid> <psk>`，再输入 `rtsp_cam on`，用 RTSP 播放器打开 `rtsp://<ip>:8554/av0_0`。完整步骤见 [Wi-Fi 与 RTSP 摄像头视频流](../../tutorials/wifi-rtsp.md)。

## 支持的示例 { #examples }

下列 9 个应用（11 个配置）可在 Reef 上构建与运行，每个都有[示例页面](../../examples/index.md#reef)给出烧录与运行步骤。除 `ipro7ai_reef_demo`、`ipro_reef_teach` 与 `ipro_agora_sentino` 外，其他应用直接执行 `make` 会构建为其他开发板，Reef 要加上 `DEFCONFIG=`。

| 应用 | 构建命令（在 SDK 根目录） | 控制台 | 烧录注意事项 |
|---|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `make -C apps/platform/ipro7ai_reef_demo` | 115200 | `--pt chips/ipro7/partition/partition_cfg_2M.toml` |
| `ipro7ai_reef_demo`（Wi-Fi） | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | 115200 | 需要运行 `ipro6_if_wifi` 的 FIN 卡，JP3 在 GPIO |
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `make -C apps/ai/ipro_reef_teach` | 115200 | 自有分区表 `partition_reef_teach.toml`、`--skip-ota` 与 `--mfg`，见 [烧录 Edge AI 固件](../../teach/firmware.md) |
| [`ipro_ble_remote`](../../examples/ipro_ble_remote.md) | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | 115200 | 首次烧录需要 `--boot2` 与 `partition_cfg_2M_remote_ab.toml`；OTA 只能用这个 A/B 分区表 |
| [`ipro_throughput_test`](../../examples/ipro_throughput_test.md) | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | 115200 | 需要两块板 |
| [`ipro_le_audio_headset`](../../examples/ipro_le_audio_headset.md) | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | 115200 | — |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | 115200 | `--pt chips/ipro7/partition/partition_cfg_2M.toml` |
| `ipro7_uvc_cam`（石头剪刀布） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | 115200 | 同上；模型已链接进固件 |
| [`ipro7_jpeg_decode`](../../examples/ipro7_jpeg_decode.md) | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | **921600** | — |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | 115200 | 需要 microSD 卡 |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `make -C apps/multimedia/ipro_agora_sentino` | 115200 | 先获取 AOSL 核心；需要 FIN 卡与 Sentino 设备三元组 |

用 `DEFCONFIG=` 构建的输出放在 `build_<名称>/build_out/`，名称为文件名去掉 `defconfig_` 的部分，例如 `defconfig_reef` → `build_reef/`。

## USB 标识符 { #usb-ids }

Reef 的 USB-C 由 IPRO7AI 的 USB 2.0 Full-Speed 设备提供，标识符取决于运行的固件。所有应用的 VID 都是 `0x3896`（INTELPRO INC.）。

| PID | 应用与模式 | 主机看到的设备 |
|---|---|---|
| `0x0705` | `ipro_reef_teach` 的 `image` 模式 | UVC 摄像头＋CDC 串口 |
| `0x0720` | `ipro_reef_teach` 的 `voice` 模式 | CDC 串口 |
| `0x0721` | `ipro_reef_teach` 的 `sensor` 模式 | CDC 串口 |
| `0x0701` | `ipro7_uvc_cam` | UVC 摄像头“IPRO7 UVC Cam” |
| `0x0704` | `ipro_ai_link` | 两个 CDC 串口（数据、控制台） |
| `0x0003` | `ipro7ai_reef_demo` 的 `mic usb` | USB 音频设备（麦克风） |

`ipro_ble_remote`、`ipro_throughput_test`、`ipro_le_audio_headset`、`ipro7_jpeg_decode`、`ipro_agora_sentino` 与 `ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 不使用 USB 设备，USB-C 仅用于供电。

## 引脚对照 { #pinout }

| 模块 | 引脚 |
|---|---|
| UART0 控制台 | TX GPIO20、RX GPIO21（U6 第 3／4 脚；J_IO 第 8／10 脚） |
| USB 设备 | D+ GPIO8、D− GPIO9 |
| 摄像头 DVP | 数据 GPIO0–7、PCLK GPIO38、VSYNC GPIO39、HREF GPIO40、XCLK GPIO22（由 IPRO7AI 输出）、RESETB GPIO34、PWDN GPIO35 |
| 摄像头 SCCB | SIOC GPIO36、SIOD GPIO37（I2C0；上拉电阻在摄像头侧） |
| 扬声器 | GPDAC GPIO23 → PAM8302A；使能 GPIO25，高电平开启，启动时默认关闭 |
| 耳麦插孔 J2 | 耳机与扬声器共用 GPDAC GPIO23；麦克风 AIN6（GPIO12）、AIN7（GPIO13）；插入检测 GPIO26（GPADC） |
| PDM 麦克风 | CLK GPIO16、DATA GPIO17 |
| RGB LED | WS2812B DI GPIO24，由 SPI0 MOSI 驱动（需 `pin_swap_enable = 0`） |
| 按键 | SW1 BOOT GPIO41（下拉，按下为高电平）；SW3 GPIO10、SW4 GPIO27、SW5 GPIO11（按下为低电平） |
| microSD | CLK GPIO30、CMD GPIO31、DAT0 GPIO29、DAT1 GPIO28、DAT2 GPIO33、DAT3 GPIO32；卡检测 GPIO15；卡座电源 GPIO14（JP3 在 GPIO 时，低电平＝有电） |
| J_IO 的 I2C | SDA GPIO19、SCL GPIO18（板上 4.7 kΩ 上拉） |

microSD 的 CMD 与 DAT 线没有外部上拉电阻，要开启 IPRO7AI 的内部上拉（SDK 的板级配置已开启）。用 GPIO14 关闭卡座电源前，先把 GPIO28–33 设为低电平或输入。microSD 这组引脚只接卡座，没有引出到 J_IO。

### 40-pin 扩展排针 J_IO { #j-io }

J_IO 是 2 × 20、2.54 mm 间距的直针排针，位置与引脚排列同树莓派的 40-pin 排针：电源、地、I2C 与 UART 都在相同位置。奇数引脚在靠板内的一排，偶数引脚在板边的一排。所有信号都是 3.3 V，每个信号引脚都有 ESD 保护。

- 标 * 的引脚经过摄像头切换芯片：只有 SW7＝GPIO 时才接到 IPRO7AI，SW7＝CAM 时不连接任何信号。
- 2、4 脚的 5 V 由 USB 5 V 经二极管输出，只在接着 USB-C 时有电，不能从这里给开发板供电。
- 16、18 脚（BOOT、RESET）默认未连接；需要时在 R92、R93 焊上 0 Ω 电阻。
- 27、28 脚是第二组 I2C，SW7＝GPIO 时可读取扩展板上的 ID EEPROM。

| 引脚 | 信号 | 说明 | 引脚 | 信号 | 说明 |
|---|---|---|---|---|---|
| 1 | 3.3 V | 电源输出 | 2 | 5 V | 输出（USB 5 V 经二极管） |
| 3 | GPIO19 | I2C SDA（4.7 kΩ 上拉） | 4 | 5 V | 输出（同 2 脚） |
| 5 | GPIO18 | I2C SCL（4.7 kΩ 上拉） | 6 | GND | |
| 7 | GPIO27 | SW4 按键 | 8 | GPIO20 | UART0 TX（控制台） |
| 9 | GND | | 10 | GPIO21 | UART0 RX（控制台） |
| 11 | GPIO10 | SW3 按键 | 12 | GPIO0 * | |
| 13 | GPIO14 | microSD 电源控制 | 14 | GND | |
| 15 | GPIO15 | microSD 卡检测 | 16 | BOOT | 默认未连接 |
| 17 | 3.3 V | 电源输出 | 18 | RESET | 默认未连接 |
| 19 | GPIO4 * | | 20 | GND | |
| 21 | GPIO5 * | | 22 | GPIO35 * | |
| 23 | GPIO7 * | | 24 | GPIO6 * | |
| 25 | GND | | 26 | GPIO34 * | |
| 27 | GPIO37 * | 第二组 I2C SDA | 28 | GPIO36 * | 第二组 I2C SCL |
| 29 | GPIO22 * | | 30 | GND | |
| 31 | GPIO39 * | | 32 | GPIO40 * | |
| 33 | GPIO38 * | | 34 | GND | |
| 35 | GPIO1 * | | 36 | GPIO11 | SW5 按键 |
| 37 | NC | 未连接 | 38 | GPIO3 * | |
| 39 | GND | | 40 | GPIO2 * | |

### 调试插座 U6 { #debug-connector }

U6 是 1.0 mm 间距、6 pin 的卧式插座（SH1.0），提供控制台 UART 与 BOOT、RESET 控制线，用于烧录固件与查看启动日志。控制台是 UART0，也是烧录用的 UART：115200 baud、8N1、无流控（烧录时 921600 baud）。

| 引脚 | 信号 | 说明 |
|---|---|---|
| 1 | NC | 未连接 |
| 2 | GND | 地 |
| 3 | TX（GPIO20） | Reef 发送（控制台输出） |
| 4 | RX（GPIO21） | Reef 接收（控制台输入） |
| 5 | BOOT | 经 1 kΩ 接 GPIO41；复位释放时为高电平即进入下载模式 |
| 6 | RESET | 经 1 kΩ 接 IPRO7AI 的复位引脚；低电平复位 |

IPRO Debug Probe 的 CN_UART 用两端线序反向的排线接到 U6：探针第 n 脚接 U6 第 7 − n 脚（探针 RST→RESET、DL→BOOT、TXD→RX、RXD→TX、GND→GND，探针的 3V3 落在 U6 的空脚上）。

!!! warning "排线方向"
    不要使用两端线序相同（第 1 脚接第 1 脚）的排线：UART 与控制线会接错，探针第 6 脚的 3.3 V 也会接到 U6 的 RESET。

## SDK 板级支持 { #bsp }

- **板级配置**：`.config` 中写入 `CONFIG_IPRO7AI_REEF=y` 与 `CONFIG_BOARD="IPRO7AI_REEF"`，引脚定义在 `bsp/board/ipro7/ipro7ai_reef_board_config.h`。同一个配置中不要再写入 `CONFIG_EVB=y`：两者都存在时会按 IPRO7 EVB 构建。
- **PSRAM**：构建不应用 Kconfig 的 `select`，Reef 配置都显式写入 `CONFIG_USE_PSRAM=y`（`ipro_throughput_test` 的 `defconfig_reef` 例外，它没有开启 PSRAM）。从零开始的新应用请复制 `apps/platform/ipro7ai_reef_demo/.config`。
- **引脚定义**：配置文件中控制台、USB、摄像头、扬声器、麦克风、LED、按键与 SD 卡的 `BOARD_*` 引脚与本页一致。文件内注释描述的扩展排针与跳线属于上一版（V3.0）底板，V4.0 以本页为准。
- **晶振微调**：`.config` 没有设置 `CONFIG_IPRO7_XTAL_CAPCODE` 时，构建会为 Reef 应用 95；在 `.config` 中写入其他值即可覆盖（0 = 保留启动时的值）。启动日志中的 `[XTAL] capcode` 一行显示实际的值。
- **Flash 布局**：`ipro7ai_reef_demo`、`ipro7_uvc_cam`、`ipro7_jpeg_decode` 与 `ipro_throughput_test` 的 Reef 配置使用 1 MB 布局，两种封装内 Flash 都放得下；`ipro_reef_teach`、`ipro_agora_sentino` 的 `.config` 与 `ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` 的 `defconfig_reef` 设置了 `CONFIG_IPRO7_FLASH_2M=y`。要让 1 MB 布局的应用使用整颗 2 MB Flash，在其配置中加入 `CONFIG_IPRO7_FLASH_2M=y`。
- **Zephyr RTOS**：本版本没有 Reef 的 Zephyr 板型。SoC 的 Kconfig 说明 Reef 可运行 `ipro7_evb` 镜像并需设置 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`，这种用法未经验证。

## 相关文档 { #documents }

- [IPRO AI Teach](../../teach/index.md)：在这块板上用 IPRO AI Studio 教开发板识别图像、声纹与传感器信号。
- [示例](../../examples/index.md#reef)：可在 Reef 上运行的应用，各有构建、烧录与运行步骤。
- [引脚与外设对照](../pinmux.md)、[电源与功耗测量](../power.md)、[IPRO7AI](../chips/ipro7ai.md)、[IPRO6S](../chips/ipro6s.md)。
- `apps/platform/ipro7ai_reef_demo/README.md`：出厂固件的完整命令与摄像头调试说明。
- IPRO7AI Reef 开发套件使用手册（V4.0 开发板硬件、接口与供电）与 IPRO Debug Probe 使用手册：向 INTELPRO 索取，见[文档下载](../../documents/index.md)。
