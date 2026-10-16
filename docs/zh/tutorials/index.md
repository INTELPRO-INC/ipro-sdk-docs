---
title: "教學"
description: 在 IPRO7AI Reef EVK 上從頭到尾跑完的實作教學：BLE 應用、日常建置燒錄、BLE 吞吐量與 LE Audio。
migrate_from:
  - "tutorials.html#next-steps"
---

# 教學

每篇教學都以 V2.1.0 隨附的應用為基礎，在 IPRO7AI Reef EVK 上一步一步完成，並附上預期的主控台輸出。開始前請先完成[開始使用](../get-started/index.md)，確認工具鏈與燒錄工具可用。

<div class="grid cards" markdown>

-   **[第一個 BLE 應用](first-ble-app.md)**

    ---

    在 Reef 上執行 `ipro_ble_remote`，用手機操作 GATT 服務，再改裝置名稱並在連線時發出提示音。

-   **[建置與燒錄流程](build-and-flash.md)**

    ---

    日常開發迴圈：`build_freertos.sh` 串接動作、`DEFCONFIG=` 替代設定、乾淨建置、讀記憶體用量，以及腳本預設值的修正方式。

-   **[BLE 吞吐量測試](ble-throughput.md)**

    ---

    兩塊 Reef 執行 `ipro_throughput_test`，量測 1M／2M PHY 吞吐量，並與 SDK 的實測結果比對。

-   **[LE Audio 入門](le-audio.md)**

    ---

    在 Reef 上執行 LE Audio unicast 耳機 `ipro_le_audio_headset`，與手機配對、以按鍵調整音量，並認識 Zephyr 的廣播範例。

</div>
