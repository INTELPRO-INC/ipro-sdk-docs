---
title: "Guides"
description: IPRO SDK development guides by feature area — architecture, build, BLE, audio, camera, AI, networking, Zephyr, Thread, low power, OTA and VS Code, with hands-on steps on the IPRO7AI Reef EVK
migrate_from: []
---

# Guides

What the SDK provides in each feature area, the `CONFIG_*` keys that turn it on, and a hands-on walk-through on the IPRO7AI Reef EVK. New to the SDK? Build your own application first in [Create Your First Application](../tutorials/first-own-app.md).

<div class="grid cards" markdown>

-   :material-layers-triple:{ .lg } **[Architecture](architecture.md)**

    ---

    Layers, the FreeRTOS and Zephyr paths, components, directory layout and BSP, traced through the out-of-box firmware.

-   :material-hammer-wrench:{ .lg } **[Build System & Configuration](build-system.md)**

    ---

    Build flow, `.config` and `autoconf.h`, the Reef configurations, memory layout, new applications.

-   :material-bluetooth:{ .lg } **[BLE Development](ble.md)**

    ---

    Zephyr v4.4.0 host on the IPRO7 BLE controller: archive selection, bring-up order, GATT on the Reef.

-   :material-headphones:{ .lg } **[Audio & LE Audio](audio.md)**

    ---

    PDM and headset microphones, speaker and headphones, USB microphone, SD-card recording, LE Audio and LC3.

-   :material-camera:{ .lg } **[Camera & Imaging](camera.md)**

    ---

    The Reef OV5640 camera: DVP, ISP, hardware MJPEG, the USB webcam, RTSP and software JPEG decoding.

-   :material-brain:{ .lg } **[AI & NPU](ai-npu.md)**

    ---

    Prebuilt inference runtime, model storage and loading, the Reef AI applications.

-   :material-school:{ .lg } **[IPRO AI Teach](../teach/index.md)**

    ---

    Image, voiceprint and sensor recognition in one Reef firmware: collect, train and deploy from IPRO AI Studio.

-   :material-lan:{ .lg } **[Networking](networking.md)**

    ---

    lwIP and mbedTLS; Wi-Fi on the Reef through the IPRO6S FIN card over SDIO; RMII Ethernet.

-   :material-cube-outline:{ .lg } **[Zephyr RTOS](zephyr.md)**

    ---

    The Zephyr v4.4.0 module, the `ipro7_evb` and `ipro7ai_evk` boards, building and flashing with west.

-   :material-access-point-network:{ .lg } **[Thread & Matter](thread-matter.md)**

    ---

    IEEE 802.15.4 and OpenThread under Zephyr, and the status of Matter.

-   :material-battery-charging:{ .lg } **[Low Power](low-power.md)**

    ---

    WFI, PDS and HBN, the low-power framework, BLE with sleep, and measuring current on the Reef.

-   :material-update:{ .lg } **[OTA Updates](ota.md)**

    ---

    boot2 OTA packages and A/B partitions, updating the Reef over BLE, the FIN card over Wi-Fi, and MCUboot under Zephyr.

-   :material-microsoft-visual-studio-code:{ .lg } **[VS Code Extension](vscode.md)**

    ---

    Extension 3.3.0 with SDK V2.2.1: building, flashing the Reef, the serial monitor and memory analysis.

</div>
