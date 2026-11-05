---
title: "教程"
description: 在 IPRO7AI Reef EVK 上从头到尾动手完成的教程：构建与烧录、编写并测试自己的应用、BLE、LE Audio、USB 网络摄像头，以及通过 IPRO6S FIN 卡经 Wi-Fi 传输的 RTSP 视频流。
migrate_from:
  - "tutorials.html#next-steps"
---

# 教程

每篇教程都在 IPRO7AI Reef EVK 上一步一步完成，并给出要输入的命令和预期的输出。开始之前请先完成[开始使用](../get-started/index.md)，确认工具链和 IntelProCube 烧录工具可用。

<div class="grid cards" markdown>

-   **[构建与烧录流程](build-and-flash.md)**

    ---

    日常开发循环：`build_freertos.sh` 串联动作、`DEFCONFIG=` 替代配置、干净构建以及查看内存占用。

-   **[创建第一个自己的应用](first-own-app.md)**

    ---

    从空目录写出自己的应用：让 RGB LED 闪烁、读取按键、添加 shell 命令、使用日志 API。

-   **[测试你的应用](testing.md)**

    ---

    控制台手动检查、打印判定结果的自检、用 `serial_monitor.py` 和 `build_freertos.sh test` 自动化，以及主机端单元测试。

-   **[第一个 BLE 应用](first-ble-app.md)**

    ---

    在 Reef 上运行 `ipro_ble_remote`，用手机操作 GATT 服务、修改代码，再通过 BLE OTA 更新固件。

-   **[BLE 吞吐量测试](ble-throughput.md)**

    ---

    两块 Reef 运行 `ipro_throughput_test`，测量 1M／2M PHY 吞吐量，并与 SDK 的实测结果对比。

-   **[LE Audio 入门](le-audio.md)**

    ---

    运行 LE Audio unicast 耳机 `ipro_le_audio_headset`，与手机配对、用按键调节音量，并了解本版本的验证范围。

-   **[USB 网络摄像头与石头剪刀布](usb-webcam.md)**

    ---

    `ipro7_uvc_cam` 让 Reef 成为免驱动的 USB 网络摄像头；另一个配置在 NPU 上玩石头剪刀布，并把结果画进画面。

-   **[Wi-Fi 与 RTSP 摄像头视频流](wifi-rtsp.md)**

    ---

    通过 microSD 卡座上的 IPRO6S FIN 卡连接 Wi-Fi，用 RTSP 推送摄像头视频流，并更新 FIN 卡固件。

</div>

## 各教程所需的硬件 { #requirements }

每篇都需要 IPRO7AI Reef EVK、USB-C 线，以及接在 U6 上的 IPRO Debug Probe 或 3.3 V USB 转 UART 线。其他需求：

| 教程 | Reef 数量 | 手机 | 摄像头 | FIN 卡 | microSD 卡 | 其他 |
|---|---|---|---|---|---|---|
| [构建与烧录流程](build-and-flash.md) | 1 | — | — | — | — | — |
| [创建第一个自己的应用](first-own-app.md) | 1 | — | — | — | — | — |
| [测试你的应用](testing.md) | 1 | — | — | — | — | 自动化部分需要 macOS 或 Linux |
| [第一个 BLE 应用](first-ble-app.md) | 1 | Android 或 iOS | 可选（拍照） | — | 可选（保存照片） | BLE OTA 需要带蓝牙的 macOS／Linux 电脑 |
| [BLE 吞吐量测试](ble-throughput.md) | 2 | — | — | — | — | 每块开发板各一条调试线 |
| [LE Audio 入门](le-audio.md) | 1 | 支持 LE Audio 的 Android | — | — | — | 可选耳机（J2） |
| [USB 网络摄像头与石头剪刀布](usb-webcam.md) | 1 | — | OV5640 | — | — | 可传输数据的 USB-C 线 |
| [Wi-Fi 与 RTSP 摄像头视频流](wifi-rtsp.md) | 1 | — | OV5640 | 需要 | — | 无线接入点；装有 VLC 或 `ffplay` 的电脑 |

要用 Reef 训练和部署自己的 AI 模型，请参阅 [IPRO AI Teach](../teach/index.md)。
