---
title: "開發指南"
description: 依功能領域整理的 IPRO SDK 開發指南：架構、建置、BLE、音訊、相機、AI、網路、Zephyr、低功耗與 OTA
migrate_from: []
---

# 開發指南

依功能領域說明 SDK 提供什麼、怎麼設定，以及該從哪個隨附範例開始。

<div class="grid cards" markdown>

-   :material-layers-triple:{ .lg } **[系統架構](architecture.md)**

    ---

    分層架構、FreeRTOS 與 Zephyr 兩條路徑、元件與目錄配置、BSP。

-   :material-hammer-wrench:{ .lg } **[建置系統與設定](build-system.md)**

    ---

    建置流程、`.config` 與 `autoconf.h`、替代設定、記憶體配置、建立新應用。

-   :material-bluetooth:{ .lg } **[BLE 開發](ble.md)**

    ---

    Zephyr v4.4.0 Host 與 IPRO BLE 控制器：控制器選擇、初始化順序、GATT。

-   :material-headphones:{ .lg } **[音訊與 LE Audio](audio.md)**

    ---

    音訊擷取與輸出、LE Audio 單播與廣播、LC3、USB 音訊、PDM 錄音。

-   :material-camera:{ .lg } **[相機與影像](camera.md)**

    ---

    DVP 感測器、ISP、MJPEG 硬體編碼、USB 攝影機與 EVK 相機函式庫。

-   :material-brain:{ .lg } **[AI 與 NPU](ai-npu.md)**

    ---

    預編譯推論執行庫、模型的存放與載入、NPU 範例。

-   :material-lan:{ .lg } **[網路](networking.md)**

    ---

    乙太網路、lwIP 與 mbedTLS，經 IPRO6S（SDIO）擴充 Wi-Fi。

-   :material-cube-outline:{ .lg } **[Zephyr RTOS](zephyr.md)**

    ---

    Zephyr v4.4.0 模組、`ipro7_evb` 與 `ipro7ai_evk` 板卡、west 建置與燒錄。

-   :material-access-point-network:{ .lg } **[Thread 與 Matter](thread-matter.md)**

    ---

    Zephyr 下的 IEEE 802.15.4 與 OpenThread，以及 Matter 的交付狀態。

-   :material-battery-charging:{ .lg } **[低功耗](low-power.md)**

    ---

    WFI、PDS 與 HBN 模式、低功耗框架、`ipro_lp_test` 與 BLE 睡眠。

-   :material-update:{ .lg } **[OTA 更新](ota.md)**

    ---

    boot2 OTA 套件與 A/B 分割表、經 BLE 更新 Reef，以及 Zephyr 的 MCUboot 與 MCUmgr。

-   :material-microsoft-visual-studio-code:{ .lg } **[VS Code Extension](vscode.md)**

    ---

    Extension 3.3.0：專案瀏覽、建置、燒錄、主控台與記憶體分析。

</div>
