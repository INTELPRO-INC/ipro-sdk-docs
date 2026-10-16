---
title: "Guides"
description: IPRO SDK development guides by feature area — architecture, build, BLE, audio, camera, AI, networking, Zephyr, low power and OTA
migrate_from: []
---

# Guides

What the SDK provides in each feature area, how to configure it, and which shipped example to start from.

<div class="grid cards" markdown>

-   :material-layers-triple:{ .lg } **[Architecture](architecture.md)**

    ---

    Layers, the FreeRTOS and Zephyr paths, components, directory layout and BSP.

-   :material-hammer-wrench:{ .lg } **[Build System & Configuration](build-system.md)**

    ---

    Build flow, `.config` and `autoconf.h`, alternate configurations, memory layout, new applications.

-   :material-bluetooth:{ .lg } **[BLE Development](ble.md)**

    ---

    Zephyr v4.4.0 host on the IPRO BLE controller: archive selection, bring-up order, GATT.

-   :material-headphones:{ .lg } **[Audio & LE Audio](audio.md)**

    ---

    Audio capture and output, LE Audio unicast and broadcast, LC3, USB audio, PDM recording.

-   :material-camera:{ .lg } **[Camera & Imaging](camera.md)**

    ---

    DVP sensors, ISP, hardware MJPEG, the USB webcam and the EVK camera library.

-   :material-brain:{ .lg } **[AI & NPU](ai-npu.md)**

    ---

    Prebuilt inference runtime, model storage and loading, NPU examples.

-   :material-lan:{ .lg } **[Networking](networking.md)**

    ---

    Ethernet, lwIP and mbedTLS; Wi-Fi added through an IPRO6S over SDIO.

-   :material-cube-outline:{ .lg } **[Zephyr RTOS](zephyr.md)**

    ---

    The Zephyr v4.4.0 module, the `ipro7_evb` and `ipro7ai_evk` boards, building and flashing with west.

-   :material-access-point-network:{ .lg } **[Thread & Matter](thread-matter.md)**

    ---

    IEEE 802.15.4 and OpenThread under Zephyr, and the delivery status of Matter.

-   :material-battery-charging:{ .lg } **[Low Power](low-power.md)**

    ---

    WFI, PDS and HBN modes, the low-power framework, `ipro_lp_test` and BLE sleep.

-   :material-update:{ .lg } **[OTA Updates](ota.md)**

    ---

    boot2 OTA packages and A/B partitions, updating the Reef over BLE, and MCUboot with MCUmgr under Zephyr.

-   :material-microsoft-visual-studio-code:{ .lg } **[VS Code Extension](vscode.md)**

    ---

    Extension 3.3.0: project browsing, builds, flashing, the serial monitor and memory analysis.

</div>
