---
title: "Wi-Fi 与 RTSP 摄像头视频流"
description: 让 IPRO7AI Reef EVK 通过 microSD 卡座上的 IPRO6S FIN 卡连接 Wi-Fi，用 RTSP 把 OV5640 摄像头的画面推流到电脑，并用 ipro6s_ota 更新 FIN 卡固件。
---

# Wi-Fi 与 RTSP 摄像头视频流

IPRO7AI Reef EVK 通过 FIN 卡联网：FIN 卡是插在 microSD 卡座（CARD1）上的 IPRO6S Wi-Fi 卡，通过 SDIO 与 IPRO7AI 通信。完成本教程后，Reef 运行出厂固件的 Wi-Fi 版本 `ipro7ai_reef_demo`（`defconfig_wifi_ipro6s`），连接到您的无线接入点，并通过 RTSP 在 `rtsp://<IP>:8554/av0_0` 提供摄像头的 MJPEG 视频，电脑用 VLC 或 `ffplay` 观看。最后介绍如何用 `ipro6s_ota` 通过 Wi-Fi 更新 FIN 卡的固件。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK、IPRO6S FIN 卡、OV5640 FLEX-24 摄像头模组。
- FIN 卡上要有 Wi-Fi 固件：IPRO6S 的 `ipro6_if_wifi`，用 `defconfig_ipro6_sdio` 构建（SDIO 版本，见步骤 2）。
- U6 接 IPRO Debug Probe 或 3.3 V USB 转 UART 线（115200 8N1，接法见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。
- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)，并已按[准备开发环境](../get-started/environment.md#intelprocube)安装 IntelProCube 0.7.0.1 命令行烧录工具。
- 一台无线接入点（SSID 和密码），以及一台连接在同一网络上、装有 VLC 或 `ffplay` 的电脑。

!!! info "FIN 卡的首次烧录"
    SDK 提供 FIN 卡固件的源代码和构建配置，也提供通过 Wi-Fi 更新固件的 `ipro6s_ota` 命令；FIN 卡上还没有固件时，首次写入固件的方式请联系 INTELPRO。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **接上 FIN 卡和摄像头**：先拔掉 USB-C。把 JP3 设为 GPIO（卡座电源改由 GPIO14 控制，`fin cycle` 才能为卡片重新上电），把 FIN 卡插入 microSD 卡座，摄像头排线插入 FPC1，确认 SW7 拨到 CAM、SW8 拨到 PWR，接好 U6，最后接上 USB-C 供电。

2. **（可选）构建 FIN 卡固件**：要更新 FIN 卡（步骤 10）时才需要。在 SDK 根目录执行：

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
    ```

    输出：`apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。这个配置在启动约 600 ms 后自动启动 Wi-Fi 和 SDIO 桥接，FIN 卡上无需输入任何命令；连接和 DHCP 都由 Reef 端控制。

3. **构建 Reef 的 Wi-Fi 版本**：

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    输出：`apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin`。这个配置在出厂固件的基础上加入 `components/network/ipronet_host`（SDIO 主机端）、lwIP 和 RTSP 服务器（端口 8554）；USB 麦克风功能（`mic usb`）因此被移除。

4. **烧录**：按住 SW1（BOOT）、按一下 SW2（RESET）、松开 SW1 进入下载模式（板上已在运行出厂固件时，也可以输入 `reboot_dl`），然后在 IntelProCube 目录下执行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build_wifi_ipro6s\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    确认输出中有 `[All Success]`（工具失败时也以 0 退出）。

5. **打开控制台并确认 FIN 卡**：以 115200 baud 打开控制台，按一下 SW2。启动信息最后打印可用的命令（行首的级别、时间等字段已省略）：

    ```text
    REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    REEF: IPRO-WiFi - `ipronet_up <ssid> <psk>`
    REEF: RTSP - `rtsp_cam on [fps]`
    ```

    输入 `fin`，确认卡片已插好、卡座已通电：

    ```text
    IPRO6S_FIN: SDIO slave in the SD slot, SD_VDD = its 3V3.
      seated : yes (DET GPIO15)
      supply : on (GPIO14, JP3 2-3 required for control)
      host   : SDH_0 on GPIO28-33, see apps/platform/ipro7_sdio_wifi
    fin cycle | fin power on|off
    ```

    （信息中的“JP3 2-3”是旧版开发板的跳线名称，在 V4.0 板上对应 JP3＝GPIO。）

6. **启动 Wi-Fi 并扫描接入点**：

    ```text
    ipronet_up
    ipro6s_scan
    ipro6s_scan_last
    ```

    `ipronet_up` 不带参数时只启动 FIN 卡上的 Wi-Fi，打印 `ipronet_start -> 0`。`ipro6s_scan` 开始扫描，结果异步返回；稍等一两秒后，`ipro6s_scan_last` 列出最近一次的结果：

    ```text
    [ctrl] scan_last: <数量> APs (on_scan_result fired <次数> times)
       0 ssid=<SSID>                           rssi=<信号强度> ch=<信道> auth=<加密方式>
    ```

7. **连接接入点**：

    ```text
    ipro6s_connect <SSID> <密码>
    ```

    ```text
    [ctrl] connect '<SSID>' -> 0 (CONNECTED_IND + IP_UPDATE_IND arrive async)
    [ctrl] STA CONNECTED
    [ctrl] IP <IP 地址> / <子网掩码> gw <网关>
    ```

    也可以一步完成启动和连接：复位后直接输入 `ipronet_up <SSID> <密码>`。如果没有看到 `[ctrl] IP …` 这一行，输入 `ipro6s_link_status`，`host connected=1 ip=1` 表示已连接并获取到 IP。

8. **开始 RTSP 推流**：

    ```text
    rtsp_cam on
    ```

    摄像头未启动时会先启动摄像头，再打印视频格式和地址：

    ```text
    rtsp_cam: on, <传感器> <宽>x<高> JPEG q<质量>, 15 fps
    rtsp_cam: rtsp://<IP 地址>:8554/av0_0
    ```

    默认 15 fps；`rtsp_cam on <fps>` 可指定 1–30。

9. **在电脑上观看**：电脑与 Reef 在同一网络上时，用 VLC 打开网络串流（“媒体 > 打开网络串流”），输入上一步打印的地址；或使用 `ffplay`：

    ```bash
    ffplay rtsp://<IP 地址>:8554/av0_0
    ```

    `rtsp_cam stats` 显示已发送的帧数、平均 JPEG 大小和编码错误；`rtsp_cam off` 停止发送视频（摄像头继续运行，`cam stop` 才会停止摄像头）；`ipronet_down` 关闭 Wi-Fi。

10. **更新 FIN 卡固件**：`ipro6s_ota` 从 HTTP 服务器下载 IPRO6S 的 OTA 包并写入 FIN 卡，卡片重启后由它的 boot2 安装。该包是 IntelProCube 生成的 IPRO6S 包（`FW_OTA.bin.xz.ota`，512 bytes 头部加 XZ 压缩内容），用步骤 2 的构建结果生成该包的步骤请联系 INTELPRO。把包放在电脑上的某个文件夹中，在该文件夹启动 HTTP 服务器：

    ```bash
    python3 -m http.server 8000
    ```

    在 Reef 的控制台（已连接 Wi-Fi）输入：

    ```text
    ipro6s_ota http://<电脑的 IP>:8000/FW_OTA.bin.xz.ota
    ```

    整个过程约 30–60 秒：Reef 先停止 Wi-Fi 传输、下载该包，FIN 卡写入并校验后重启安装，Reef 再重新枚举卡片并恢复连接。成功时打印：

    ```text
    [ota] fetch <字节数> B in <毫秒> ms
    [ota] RESULT OK total=<毫秒> …
    ```

    失败时打印 `[ota] RESULT ERR rc=<代码> … phase=<阶段>`。

</div>

## 验证结果 { #verify }

- `fin` 显示 `seated : yes`，`ipro6s_scan_last` 列出附近的接入点。
- 连接后控制台打印 `[ctrl] IP …`，`ipro6s_link_status` 显示 `host connected=1 ip=1`。
- `rtsp_cam on` 打印 `rtsp://<IP>:8554/av0_0`，VLC 或 `ffplay` 显示实时画面，`rtsp_cam stats` 的帧数持续增加。

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| `fin` 显示 `seated : no` | 卡片没有插到底 | 拔掉 USB-C，重新插好 FIN 卡后再上电 |
| `ipronet_start` 返回非 0 | FIN 卡没有响应：没有固件、固件不是 SDIO 版本，或卡片状态异常 | JP3 设为 GPIO 时输入 `fin cycle` 重新上电后再试；确认卡上是 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio` 固件 |
| `ipro6s_scan_last` 显示 0 个 AP | 扫描结果尚未返回 | 等一两秒再输入一次 `ipro6s_scan_last`；必要时重新执行 `ipro6s_scan` |
| 一直没有 `[ctrl] IP …` | SSID 或密码错误，或接入点不在范围内 | 用 `ipro6s_scan_last` 确认 SSID；`ipro6s_disconnect` 后重新 `ipro6s_connect` |
| `rtsp_cam: camera gives no frames - …` | 摄像头没有输出帧 | 确认 SW7 拨到 CAM、摄像头排线已插好；输入 `cam stop` 后再 `rtsp_cam on` |
| `rtsp_cam: no IP yet - …` | Wi-Fi 还没有获取到 IP | 先完成步骤 7，再输入 `rtsp_cam on` 获取地址 |
| VLC 连接不上 | 电脑与 Reef 不在同一网络，或接入点隔离了无线客户端 | 确认电脑能 `ping <IP 地址>`；关闭接入点的客户端隔离功能 |
| `ipro6s_ota` 打印 `[ota] RESULT ERR … phase=fetch` | 电脑上的 HTTP 服务器无法连接或路径错误 | 在电脑的浏览器中打开同一个地址确认；检查防火墙 |

## 下一步 { #next-steps }

- [网络](../guides/networking.md)：`ipronet_host` API、lwIP 集成与网络配置。
- [IPRO6S](../hardware/chips/ipro6s.md)：FIN 卡上的 IPRO6S 芯片以及 `ipro6_if_wifi` 的其他配置。
- [USB 网络摄像头与石头剪刀布](usb-webcam.md)：改为通过 USB 发送摄像头画面。
- [摄像头与图像](../guides/camera.md)：图像管线与传感器配置。
