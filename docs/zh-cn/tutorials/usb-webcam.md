---
title: "USB 网络摄像头与石头剪刀布"
description: 在 IPRO7AI Reef EVK 上用 ipro7_uvc_cam 把 OV5640 摄像头变成免驱动的 USB 网络摄像头，再换成在 NPU 上运行石头剪刀布、并把结果画进画面的版本。
---

# USB 网络摄像头与石头剪刀布

完成本教程后，接上 OV5640 摄像头的 IPRO7AI Reef EVK 会通过 USB-C 成为电脑上的一个 USB 网络摄像头（UVC，MJPEG），无需安装驱动程序；您可以在电脑的相机程序中选择 1280×720 或 640×360 观看。接着换成 `defconfig_reef_rps` 配置：开发板在 NPU 上识别手势，和您玩石头剪刀布，游戏画面直接画在发给电脑的视频里。两者都是 `apps/multimedia/ipro7_uvc_cam` 应用的 Reef 配置。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK、OV5640 FLEX-24 摄像头模组，以及一条可传输数据的 USB-C 线（连接电脑，同时供电和传输视频）。
- U6 接 IPRO Debug Probe 或 3.3 V USB 转 UART 线（115200 8N1，接法见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)），用于烧录和查看控制台。
- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)，并已按[准备开发环境](../get-started/environment.md#intelprocube)安装 IntelProCube 0.7.0.1 命令行烧录工具。
- 电脑上能打开 USB 摄像头的程序：macOS 的 QuickTime Player、Windows 的“相机”应用，或 Linux 上任意 V4L2 程序（例如 `ffplay`）。主机使用操作系统内置的 UVC 驱动；INTELPRO 已在 macOS 上验证过。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **接上摄像头**：先拔掉 USB-C。把 OV5640 模组的排线插入 FPC1，确认 SW7 拨到 CAM（摄像头引脚接到 IPRO7AI、摄像头电源打开）、SW8 拨到 PWR，接好 U6，最后把 USB-C 连接到电脑。

2. **构建网络摄像头配置**：在 SDK 根目录执行：

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640
    ```

    输出：`apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin`。不加 `DEFCONFIG=` 的 `make` 构建的是另一块开发板（IPRO7 EVB）的版本，不能用于 Reef。

3. **烧录**：按住 SW1（BOOT）、按一下 SW2（RESET）、松开 SW1 进入下载模式，然后在 IntelProCube 目录下用标准 2 MB 分区表烧录：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\multimedia\ipro7_uvc_cam\build_reef_ov5640\build_out\ipro7_uvc_cam_IPRO7.bin
        ```

    确认输出中有 `[All Success]`（工具失败时也以 0 退出）。这两个配置不使用 `mfg` 分区。

4. **打开控制台并复位**：以 115200 baud 打开 U6 的串口，按一下 SW2。控制台打印：

    ```text
    [SYS] Reset reason: <原因>
    [UVC] Starting init task...
    [OS] Starting OS Scheduler...
    [UVC] Bringing up USB UVC webcam (720p MJPEG)...
    [UVC] Streaming pipeline started
    ```

5. **确认电脑识别到摄像头**：开发板以 `IPRO7 UVC Cam` 的名称出现，USB VID／PID 为 `0x3896`／`0x0701`：

    === "macOS"

        ```bash
        system_profiler SPUSBDataType | grep -A4 "IPRO7 UVC Cam"
        ```

    === "Linux"

        ```bash
        lsusb -d 3896:0701
        ```

    === "Windows"

        “设备管理器”的“照相机”下出现 `IPRO7 UVC Cam`。

6. **在电脑上观看**：
    - macOS：打开 QuickTime Player，选择“文件 > 新建影片录制”，在录制按钮旁的菜单中选择 `IPRO7 UVC Cam`。
    - Windows：打开“相机”应用，切换到 `IPRO7 UVC Cam`。
    - Linux：

        ```bash
        ffplay -f v4l2 -input_format mjpeg -video_size 640x360 /dev/video0
        ```

    视频有两种尺寸，由电脑端的程序选择：1280×720（画面复杂时约 15 fps，受 USB Full-Speed 带宽限制）和 640×360（30 fps）。

7. **调整传感器（可选）**：控制台的 `cam` 命令可以直接读写 OV5640 的寄存器（寄存器地址和数据均为十六进制），也能打印画面分格的统计：

    ```text
    cam rd 300a 2
    ```

    ```text
    RD 300a 56 40
    ```

    `300a`、`300b` 是 OV5640 的芯片 ID（`0x56`、`0x40`）。`cam wr <reg> <hexbytes>` 写入寄存器，`cam grid [cols rows]` 以 `GRID … GRIDEND` 打印各格的平均 Y、U、V。写入的值在复位后恢复默认。

8. **换成石头剪刀布配置**：构建 `defconfig_reef_rps`，按步骤 3 的方式烧录（命令中的路径改为 `build_reef_rps`）：

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps
    ```

    输出：`apps/multimedia/ipro7_uvc_cam/build_reef_rps/build_out/ipro7_uvc_cam_IPRO7.bin`。手势分类模型已链接进固件，无需另外烧录模型。

9. **开始玩**：复位后在电脑上以 640×360 打开 `IPRO7 UVC Cam`。画面上方是比分栏、下方是信息栏，中间的方框是 NPU 查看的区域，框内实时显示当前识别到的手势。把手放进方框并保持不动：画面倒数 3、2、1，开发板捕捉您的手势、随机出拳，再显示双方的手势和比分；手离开方框后才会开始下一局。

    在控制台输入 `rps` 查看模型和游戏状态：

    ```text
    rps
    ```

    ```text
    model   : ready, <字节数> B from <来源>, loaded in <毫秒> ms, <剩余> KB heap left
    npu     : <帧数> frames, 0 errors, <每秒推理次数> fps, last <毫秒> ms
    now     : <当前手势> <置信度>%  (r <%> p <%> s <%> n <%>)
    game    : round <局数>, you <胜> me <负> draw <和>, conf >= 60%, mirror on
    ```

    | 命令 | 作用 |
    |---|---|
    | `rps go` | 不等手放进方框，立即开始一局 |
    | `rps reset` | 比分清零 |
    | `rps mirror on\|off` | 画面左右镜像（默认开启，像照镜子）；观看程序本身会镜像预览时（例如 Photo Booth、FaceTime）改为 `off` |
    | `rps print on\|off` | 在控制台逐条打印分类结果 |
    | `rps conf <百分比>` | 计入一次手势所需的置信度（默认 60） |
    | `rps dump` | 以 base64 打印 NPU 看到的一张 128×128 图像（`CAPBEGIN` 到 `CAPEND`，115200 baud 下约 8 秒） |

</div>

## 验证结果 { #verify }

- 控制台打印 `[UVC] Streaming pipeline started`，电脑列出 `IPRO7 UVC Cam`（`3896:0701`）。
- 网络摄像头配置：相机程序显示实时画面，可以在 1280×720 和 640×360 之间切换。
- 石头剪刀布配置：画面上有比分栏、方框和实时手势标签；把手放进方框会开始倒数，`rps` 中 `npu` 一行的帧数持续增加。

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| 电脑上没有出现 `IPRO7 UVC Cam` | USB-C 线只能充电，或烧录的不是 Reef 版本 | 换一条可传输数据的线；确认烧录的是 `build_reef_ov5640` 或 `build_reef_rps` 中的文件 |
| 控制台停在 `Bringing up …`，或画面全黑 | 摄像头没接好，或 SW7 不在 CAM | 拔掉 USB-C 后重新插好摄像头排线，SW7 拨到 CAM，再上电 |
| 1280×720 的帧率偏低 | USB Full-Speed 的带宽上限，画面越复杂 MJPEG 越大 | 改用 640×360（30 fps） |
| 石头剪刀布左右颠倒 | 观看程序自己也做了镜像 | 输入 `rps mirror off` |
| 手放在方框里却不倒数 | 识别置信度低于阈值，或手的位置太偏 | 用 `rps print on` 查看分类结果；调整光线和距离；必要时 `rps conf 50` |
| 烧录输出中没有 `[All Success]` | 未进入下载模式，或缺少 `--chip-variant IPRO7AI` | 重新进入下载模式；确认命令参数 |

## 下一步 { #next-steps }

- [IPRO AI Teach](../teach/index.md)：用自己的图像训练分类器并部署到 Reef（`ipro_reef_teach` 的图像模式使用同一套摄像头管线）。
- [摄像头与图像](../guides/camera.md)：图像管线、ISP 通道与支持的传感器。
- [AI 与 NPU](../guides/ai-npu.md)：NPU 推理与模型。
- [Wi-Fi 与 RTSP 摄像头视频流](wifi-rtsp.md)：改为通过 Wi-Fi 以 RTSP 发送摄像头画面。
