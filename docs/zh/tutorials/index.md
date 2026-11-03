---
title: "教學"
description: 在 IPRO7AI Reef EVK 上從頭到尾動手做的教學：建置與燒錄、寫自己的應用並測試、BLE、LE Audio、USB 網路攝影機，以及經 IPRO6S FIN 卡以 Wi-Fi 傳送的 RTSP 串流。
migrate_from:
  - "tutorials.html#next-steps"
---

# 教學

每篇教學都在 IPRO7AI Reef EVK 上一步一步完成，附上要輸入的命令與預期的輸出。開始前請先完成[開始使用](../get-started/index.md)，確認工具鏈與 IntelProCube 燒錄工具可用。

<div class="grid cards" markdown>

-   **[建置與燒錄流程](build-and-flash.md)**

    ---

    日常開發迴圈：`build_freertos.sh` 串接動作、`DEFCONFIG=` 替代設定、乾淨建置與讀取記憶體用量。

-   **[建立第一個自己的應用](first-own-app.md)**

    ---

    從空目錄寫出自己的應用：讓 RGB LED 閃爍、讀取按鍵、加入 shell 指令、使用日誌 API。

-   **[測試你的應用](testing.md)**

    ---

    主控台手動檢查、會印出判定結果的自我測試、`serial_monitor.py` 與 `build_freertos.sh test` 自動化，以及主機端單元測試。

-   **[第一個 BLE 應用](first-ble-app.md)**

    ---

    在 Reef 上執行 `ipro_ble_remote`，用手機操作 GATT 服務、修改程式，再以 BLE OTA 更新韌體。

-   **[BLE 吞吐量測試](ble-throughput.md)**

    ---

    兩塊 Reef 執行 `ipro_throughput_test`，量測 1M／2M PHY 吞吐量，並與 SDK 的實測結果比對。

-   **[LE Audio 入門](le-audio.md)**

    ---

    執行 LE Audio unicast 耳機 `ipro_le_audio_headset`，與手機配對、以按鍵調整音量，並了解本版的驗證範圍。

-   **[USB 網路攝影機與剪刀石頭布](usb-webcam.md)**

    ---

    `ipro7_uvc_cam` 讓 Reef 成為免驅動的 USB 網路攝影機，另一個設定在 NPU 上玩剪刀石頭布並畫進影像。

-   **[Wi-Fi 與 RTSP 相機串流](wifi-rtsp.md)**

    ---

    經 microSD 卡座上的 IPRO6S FIN 卡連上 Wi-Fi，以 RTSP 串流相機影像，並更新 FIN 卡韌體。

</div>

## 各教學需要的硬體 { #requirements }

每篇都需要 IPRO7AI Reef EVK、USB-C 線，以及接在 U6 的 IPRO Debug Probe 或 3.3 V USB 轉 UART 線。其他需求：

| 教學 | Reef 數量 | 手機 | 相機 | FIN 卡 | microSD 卡 | 其他 |
|---|---|---|---|---|---|---|
| [建置與燒錄流程](build-and-flash.md) | 1 | — | — | — | — | — |
| [建立第一個自己的應用](first-own-app.md) | 1 | — | — | — | — | — |
| [測試你的應用](testing.md) | 1 | — | — | — | — | 自動化部分需 macOS 或 Linux |
| [第一個 BLE 應用](first-ble-app.md) | 1 | Android 或 iOS | 選用（拍照） | — | 選用（存照片） | BLE OTA 需有藍牙的 macOS／Linux 電腦 |
| [BLE 吞吐量測試](ble-throughput.md) | 2 | — | — | — | — | 每塊板子各一條除錯線 |
| [LE Audio 入門](le-audio.md) | 1 | 支援 LE Audio 的 Android | — | — | — | 選用耳機（J2） |
| [USB 網路攝影機與剪刀石頭布](usb-webcam.md) | 1 | — | OV5640 | — | — | 可傳資料的 USB-C 線 |
| [Wi-Fi 與 RTSP 相機串流](wifi-rtsp.md) | 1 | — | OV5640 | 需要 | — | 無線基地台；裝有 VLC 或 `ffplay` 的電腦 |

用 Reef 訓練與部署自己的 AI 模型，見 [IPRO AI Teach](../teach/index.md)。
