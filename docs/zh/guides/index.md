---
title: "開發指南"
description: 依功能領域整理的 IPRO SDK 開發指南：架構、建置、BLE、音訊、相機、AI、網路、Zephyr、Thread、低功耗、OTA 與 VS Code，附 IPRO7AI Reef EVK 上的動手做步驟
migrate_from: []
---

# 開發指南

依功能領域說明 SDK 提供什麼、用哪些 `CONFIG_*` 開啟，並附在 IPRO7AI Reef EVK 上動手做的步驟。第一次使用 SDK，請先依[建立第一個自己的應用](../tutorials/first-own-app.md)做出自己的應用。

<div class="grid cards" markdown>

-   :material-layers-triple:{ .lg } **[系統架構](architecture.md)**

    ---

    分層架構、FreeRTOS 與 Zephyr 兩條路徑、元件與目錄配置、BSP，並從出廠韌體逐層對照。

-   :material-hammer-wrench:{ .lg } **[建置系統與設定](build-system.md)**

    ---

    建置流程、`.config` 與 `autoconf.h`、Reef 各組設定、記憶體配置、建立新應用。

-   :material-bluetooth:{ .lg } **[BLE 開發](ble.md)**

    ---

    Zephyr v4.4.0 Host 與 IPRO7 BLE 控制器：控制器選擇、初始化順序、在 Reef 上實作 GATT。

-   :material-headphones:{ .lg } **[音訊與 LE Audio](audio.md)**

    ---

    PDM 與耳機麥克風、喇叭與耳機輸出、USB 麥克風、SD 卡錄音、LE Audio 與 LC3。

-   :material-camera:{ .lg } **[相機與影像](camera.md)**

    ---

    Reef 的 OV5640 相機：DVP、ISP、MJPEG 硬體編碼、USB 攝影機、RTSP 與軟體 JPEG 解碼。

-   :material-brain:{ .lg } **[AI 與 NPU](ai-npu.md)**

    ---

    預編譯推論執行庫、模型的存放與載入、Reef 的 AI 應用。

-   :material-school:{ .lg } **[IPRO AI Teach](../teach/index.md)**

    ---

    Reef 上一份韌體的影像、聲紋、感測器辨識：在 IPRO AI Studio 收資料、訓練、部署。

-   :material-lan:{ .lg } **[網路](networking.md)**

    ---

    lwIP 與 mbedTLS；Reef 經 SDIO 透過 IPRO6S FIN 卡使用 Wi-Fi；RMII 乙太網路。

-   :material-cube-outline:{ .lg } **[Zephyr RTOS](zephyr.md)**

    ---

    Zephyr v4.4.0 模組、`ipro7_evb` 與 `ipro7ai_evk` 板卡、west 建置與燒錄。

-   :material-access-point-network:{ .lg } **[Thread 與 Matter](thread-matter.md)**

    ---

    Zephyr 下的 IEEE 802.15.4 與 OpenThread，以及 Matter 的現況。

-   :material-battery-charging:{ .lg } **[低功耗](low-power.md)**

    ---

    WFI、PDS 與 HBN、低功耗框架、BLE 與睡眠，以及在 Reef 上量測電流。

-   :material-update:{ .lg } **[OTA 更新](ota.md)**

    ---

    boot2 OTA 套件與 A/B 分割表、經 BLE 更新 Reef、經 Wi-Fi 更新 FIN 卡，以及 Zephyr 的 MCUboot。

-   :material-microsoft-visual-studio-code:{ .lg } **[VS Code Extension](vscode.md)**

    ---

    Extension 3.3.0 搭配 SDK V2.2.1：建置、燒錄 Reef、序列埠監看與記憶體分析。

</div>
