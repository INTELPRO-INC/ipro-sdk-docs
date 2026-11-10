---
title: "开发指南"
description: 按功能领域整理的 IPRO SDK 开发指南：架构、构建、BLE、音频、摄像头、AI、网络、Zephyr、Thread、低功耗、OTA 与 VS Code，附 IPRO7AI Reef EVK 上的动手实践步骤
migrate_from: []
---

# 开发指南

按功能领域说明 SDK 提供什么、用哪些 `CONFIG_*` 开启，并附在 IPRO7AI Reef EVK 上动手实践的步骤。第一次使用 SDK，请先按照[创建第一个自己的应用](../tutorials/first-own-app.md)做出自己的应用。

<div class="grid cards" markdown>

-   :material-layers-triple:{ .lg } **[系统架构](architecture.md)**

    ---

    分层架构、FreeRTOS 与 Zephyr 两条路径、组件与目录布局、BSP，并从出厂固件逐层对照。

-   :material-hammer-wrench:{ .lg } **[构建系统与配置](build-system.md)**

    ---

    构建流程、`.config` 与 `autoconf.h`、Reef 的各组配置、内存布局、创建新应用。

-   :material-bluetooth:{ .lg } **[BLE 开发](ble.md)**

    ---

    Zephyr v4.4.0 Host 与 IPRO7 BLE 控制器：控制器选择、初始化顺序、在 Reef 上实现 GATT。

-   :material-headphones:{ .lg } **[音频与 LE Audio](audio.md)**

    ---

    PDM 与耳机麦克风、扬声器与耳机输出、USB 麦克风、SD 卡录音、LE Audio 与 LC3。

-   :material-camera:{ .lg } **[摄像头与图像](camera.md)**

    ---

    Reef 的 OV5640 摄像头：DVP、ISP、MJPEG 硬件编码、USB 摄像头、RTSP 与软件 JPEG 解码。

-   :material-brain:{ .lg } **[AI 与 NPU](ai-npu.md)**

    ---

    预编译推理运行库、模型的存放与加载、Reef 的 AI 应用。

-   :material-school:{ .lg } **[IPRO AI Teach](../teach/index.md)**

    ---

    Reef 上一份固件完成图像、声纹、传感器识别：在 IPRO AI Studio 中采集数据、训练、部署。

-   :material-lan:{ .lg } **[网络](networking.md)**

    ---

    lwIP 与 mbedTLS；Reef 经 SDIO 通过 IPRO6S FIN 卡使用 Wi-Fi；RMII 以太网。

-   :material-cube-outline:{ .lg } **[Zephyr RTOS](zephyr.md)**

    ---

    Zephyr v4.4.0 模块、`ipro7_evb` 与 `ipro7ai_evk` 开发板、west 构建与烧录。

-   :material-access-point-network:{ .lg } **[Thread 与 Matter](thread-matter.md)**

    ---

    Zephyr 下的 IEEE 802.15.4 与 OpenThread，以及 Matter 的现状。

-   :material-battery-charging:{ .lg } **[低功耗](low-power.md)**

    ---

    WFI、PDS 与 HBN、低功耗框架、BLE 与睡眠，以及在 Reef 上测量电流。

-   :material-update:{ .lg } **[OTA 更新](ota.md)**

    ---

    boot2 OTA 套件与 A/B 分区表、经 BLE 更新 Reef、经 Wi-Fi 更新 FIN 卡，以及 Zephyr 的 MCUboot。

-   :material-microsoft-visual-studio-code:{ .lg } **[VS Code Extension](vscode.md)**

    ---

    Extension 3.3.0 配合 SDK V2.2.1：构建、烧录 Reef、串口监视与内存分析。

</div>
