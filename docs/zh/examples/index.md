---
title: "範例"
description: V2.1.0 隨附的 FreeRTOS 應用目錄：用途、支援的板卡與替代設定、主控台鮑率與 GitHub 原始碼連結。
migrate_from:
  - "applications.html"
not_migrated:
  - "applications.html#ipro-ble-img-capture"
---

# 範例

V2.1.0 隨附的 FreeRTOS 應用，依用途分組。每個應用都是 `apps/` 下的獨立目錄，內含 `.config`、`CMakeLists.txt` 與 `Makefile`，全部以 IPRO7 系列晶片為目標；點選應用名稱可開啟 GitHub 上的原始碼與 README。Zephyr 範例位於 `zephyr/samples/`，見 [Zephyr RTOS](../guides/zephyr.md)。

表中板卡簡稱：EVB＝[IPRO7 EVB](../hardware/boards/ipro7-evb.md)、EVK＝[IPRO7AI EVK](../hardware/boards/ipro7ai-evk.md)、Reef＝[IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。

## 建置與燒錄 { #overview }

- 建置：`make -C apps/<分類>/<應用>`，或 `./build_freertos.sh build <應用>`。產出在 `build/build_out/<應用>_IPRO7.bin`。
- 替代設定：`defconfig_*` 與 `config_*` 以 `DEFCONFIG=` 選用，建置於 `build_<名稱>/`；`BOARD=` 只有 `ipro_pdm_mic_demo` 與 `ipro_agora_sentino` 支援。詳見[建置與燒錄流程](../tutorials/build-and-flash.md)。
- 主控台：表中的鮑率來自各設定的 `CONFIG_PLATFORM_UART_BAUDRATE`，未設定時為 115200。標示 USB CDC 的程式，主控台走 USB 虛擬序列埠，不使用 UART。
- 燒錄：Reef 與 EVK 使用 `--chip-variant IPRO7AI`，其他參數見[燒錄與序列埠](../get-started/flash-and-monitor.md)；需要特定分割表、boot2 或模型分割區的應用，以該應用的 README 為準。

## BLE { #ble }

| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro_ble_remote`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_ble_remote) | GATT 參考應用：LED、按鍵、環境感測、UART、PIR 影像與影像上傳服務；隨附 Android 示範 App `ipro_remote_demo.apk`。教學見[第一個 BLE 應用](../tutorials/first-ble-app.md) | EVB（`.config`）；Reef（`defconfig_reef`：WS2812、相機、SD 卡、音訊與 BLE A/B OTA，需 boot2 與 `partition_cfg_2M_remote_ab.toml`）。`defconfig_lowpower` 需要控制器原始碼，無法以 V2.1.0 建置 | UART 115200 |
| [`ipro_ble_transparent`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_ble_transparent) | UART／BLE 透明傳輸橋接，以 AT 指令設定；隨附設定的 AT 指令走 USB CDC | EVB | UART 115200 |
| [`ipro_ble_hid_keyboard`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_ble_hid_keyboard) | HID over GATT 鍵盤 | EVB | UART 115200 |
| [`ipro_throughput_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_throughput_test) | 兩板 BLE 吞吐量測試：1M／2M／Coded PHY、DLE、ATT MTU 247。教學見 [BLE 吞吐量測試](../tutorials/ble-throughput.md) | EVB（`.config`）；Reef（`defconfig_reef`） | UART 115200 |
| [`ipro_le_audio_headset`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/le_audio/ipro_le_audio_headset) | LE Audio unicast 耳機：BAP unicast server、PACS、ASCS、VCP、CAP，LC3 解碼。教學見 [LE Audio 入門](../tutorials/le-audio.md) | EVB（`.config`／`DAC.config`：DAC 輸出；`UAC.config`：USB Audio）；Reef（`defconfig_reef`） | UART 115200 |

獨立的 FreeRTOS BIS 廣播來源與接收應用未包含於 V2.1.0，請洽 INTELPRO；Zephyr 有對應的廣播範例。

## 音訊與語音 { #audio }

| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro_pdm_mic_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/multimedia/ipro_pdm_mic_demo) | PDM 麥克風收音、DAC 播放、經 BLE 以 LC3 串流、SMP 配對、PDS31 休眠與綁定重連、2M 大量傳輸；Android 範例 App 原始碼在 `tools/android/IproMicDemo/` | EVB（`.config`，`config_evb` 相同）；EVK（`make BOARD=evk`，使用 `config_evk`，另提供 16 kHz USB 麥克風） | EVB：UART 115200<br>EVK：UART 921600 |
| [`ipro_agora_sentino`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/multimedia/ipro_agora_sentino) | Sentino 雲端 AI 語音對話：BLE 配網、經 IPRO6S FIN 卡連 Wi-Fi、MQTT 登入、Agora RTC 即時語音。需另備 Sentino 裝置三元組與 AOSL（見 README）；FIN 卡端韌體未包含於 V2.1.0，請洽 INTELPRO | Reef（`.config`，`make` 或 `make BOARD=reef`）；EVK（`make BOARD=evk`，使用 `config_evk`，可建置但未經板上驗證） | Reef：UART 115200<br>EVK：UART 921600 |

## 平台與板卡 { #platform }

| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7_demo) | 全晶片參考：PWM、SPI、I2S、LCD、音訊 ADC／DAC、USB 裝置（CDC、HID、MSC、UAC、UVC）、檔案系統、TRNG 與 DSP 等，各有 shell 指令；BLE 示範預設關閉 | EVB；另有 `defconfig_boot2`、`defconfig_boot2_nopsram`、`defconfig_boot2_ota`、`defconfig_nist_fulltest`、`defconfig_security_cert` | UART 115200 |
| [`ipro7ai_evk_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7ai_evk_demo) | IPRO7AI EVK bring-up：LCD、相機、麥克風、喇叭與 SD 卡 | EVK。`.config` 與 `config_video`：SD 卡影片播放，不含藍牙；`config_ai`：AI 與 NPU，不含藍牙；`config_bt`、`config_autoplay`：BLE 與 LE Audio unicast 接收，不含 AI | `.config`：UART 921600<br>`config_*`：UART 115200 |
| [`ipro7ai_evk_launcher`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7ai_evk_launcher) | 相機、LCD、麥克風與喇叭整合在單一映像，以 NPU 辨識手勢切換頁面；人形／寵物偵測模型由 SD 卡 `sd:/models/person.inm` 載入；附 `flash.sh` | EVK | UART 921600 |
| [`ipro7ai_reef_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7ai_reef_demo) | Reef 開箱韌體：WS2812、按鍵、喇叭與耳機、PDM／耳機麥克風／AUX-IN、SD 卡、OV5640／OV2640 相機，各有 shell 指令 | Reef（`.config`）；`defconfig_wifi_ipro6s`：經 IPRO6S FIN 卡連 Wi-Fi，並以 RTSP 串流相機畫面 | UART 115200 |

## AI 與影像 { #ai-vision }

| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7ai_evk_person_detect`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/ai/ipro7ai_evk_person_detect) | 相機預覽顯示在 LCD，疊加 NPU 執行 YOLOv8 的人形／寵物框；模型燒錄到 mfg 分割區（附 `flash.sh`） | EVK | UART 115200 |
| [`ipro7ai_evk_rps`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/ai/ipro7ai_evk_rps) | 與 NPU 上的 4 類 int8 CNN 玩剪刀石頭布；模型預設連結進韌體，附模型與訓練腳本 | EVK | UART 921600 |
| [`ipro7_uvc_cam`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/multimedia/ipro7_uvc_cam) | USB 網路攝影機：DVP 感測器、ISP、硬體 MJPEG、USB Video Class | EVB（`.config`，SC101IOT）；Reef（`defconfig_reef_ov5640`：OV5640；`defconfig_reef_rps`：在影像中加入 NPU 剪刀石頭布） | `.config`：UART 921600<br>Reef：UART 115200 |

AI 推論的效能與 CPU 推論函式庫比較程式列在[測試與 bring-up 程式](#test-apps)。

## 網路 { #networking }

無線網路由 IPRO6S 經 SDIO 提供，有線網路使用 Ethernet。

| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7_sdio_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7_sdio_wifi) | IPRO7 作為 SDIO 主機、IPRO6S 作為 Wi-Fi 無線電（`components/network/ipronet_host`），提供 lwIP 網路介面 `iproeth0` 與 DHCP。IPRO6S 端韌體未包含於 V2.1.0，請洽 INTELPRO | EVB | UART 115200 |

使用 IPRO6S FIN 卡連網的還有 `ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 與 `ipro_agora_sentino`；SPI 介面的 ENC28J60 乙太網路見 `ipro_enc28j60_test`。

## 測試與 bring-up 程式 { #test-apps }

`apps/test/` 下的單元測試、效能測試與周邊 bring-up 程式。多數需要外接模組或面板，接線見各程式的 README 或原始碼。

| 程式 | 用途 | 板卡 | 主控台 |
|---|---|---|---|
| [`ipro_unit_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_unit_test) | HAL 與共用元件的單元測試，結束時印出 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`（可用 `./build_freertos.sh test ipro_unit_test`） | EVB | UART 115200 |
| [`ipro_ai_bench`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_ai_bench) | 整個模型在 NPU 與 CPU 上的推論時間比較 | EVB | UART 115200 |
| [`ipro_ai_link`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_ai_link) | IPRO AI Studio「Run on board」的板端韌體：由 SD 卡（`sd:/`）載入模型與輸入，結果經 USB 回傳 | EVB；Reef（`defconfig_reef`） | UART 115200 |
| [`ipro_npu_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_npu_yolo) | NPU 上的 YOLOv8 人形／寵物偵測 | EVB | UART 115200 |
| [`ipro_tflm_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_tflm_test) | TensorFlow Lite Micro 搭配 NMSIS-NN 核心的模型效能測試 | EVB | UART 115200 |
| [`ipro_tflm_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_tflm_yolo) | 以 TensorFlow Lite Micro 在 CPU 上執行 YOLOv8 | EVB | UART 115200 |
| [`ipro_nmsis_nn_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_nmsis_nn_test) | NMSIS-NN 運算子測試 | EVB | UART 115200 |
| [`ipro_tinymaix_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_tinymaix_demo) | TinyMaix INT8 MNIST 推論（`nn_info`、`nn_run`、`nn_benchmark`） | EVB | UART 115200 |
| [`ipro_gh7007_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_gh7007_test) | GH7007 5 吋 SPI LCD bring-up | EVB | USB CDC |
| [`ipro_gh7007_video`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_gh7007_video) | 在 GH7007 面板播放 SD 卡上的影片 | EVB | USB CDC |
| [`ipro_epd_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_epd_test) | GDEY0213F52 2.13 吋電子紙 bring-up | EVB | UART 115200 |
| [`ipro_epd_el036`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_epd_el036) | EL036MF1 電子紙 bring-up | EVB | UART 921600 |
| [`kw307_radar_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/kw307_radar_test) | KW307 24 GHz 雷達模組（UART） | EVK | UART 115200 |
| [`mpu6500_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/mpu6500_test) | MPU-6500 IMU（I2C；`mpu_init`、`mpu_read`、`mpu_stream`） | EVB | UART 115200 |
| [`ipro_enc28j60_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_enc28j60_test) | ENC28J60 SPI 乙太網路 bring-up，收發原始封包 | IPRO7 Arduino 板 | USB CDC |
| [`ipro_pio_sdh_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_pio_sdh_test) | 軟體（PIO）SD 主機與硬體 SDH 同時掛載的檔案系統測試 | EVB | USB CDC |
| [`ipro_sdio_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_sdio_probe) | SDIO 主機基本測試 | EVB | UART 115200 |
| [`ipro_atbm_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_atbm_probe) | ATBM6162 SDIO 模組 bring-up 探測 | EVB | UART 115200 |
| [`ipro_lp_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_lp_test) | PDS31 進出與 RTC 喚醒測試（`lp` 指令） | EVB | UART 115200 |

## 下一步 { #next-steps }

- [第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)：建置、燒錄並執行第一個應用。
- [建置系統與設定](../guides/build-system.md#variants)：`DEFCONFIG=`、`BOARD=` 與替代設定的建置目錄。
- [教學](../tutorials/index.md)：以 `ipro_ble_remote`、`ipro_throughput_test` 與 `ipro_le_audio_headset` 一步步實作。
- [Zephyr RTOS](../guides/zephyr.md#samples)：`zephyr/samples/` 的 Zephyr 範例。
