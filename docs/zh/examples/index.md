---
title: "範例"
description: V2.3.0 隨附的 41 個 FreeRTOS 應用：可在 IPRO7AI Reef EVK 上執行的 9 個應用各有一頁步驟，其他應用列出所需板卡。
migrate_from:
  - "applications.html"
not_migrated:
  - "applications.html#ipro-ble-img-capture"
---

# 範例

SDK 隨附 41 個 FreeRTOS 應用，其中 38 個以 IPRO7／IPRO7AI 為目標、3 個以 IPRO6S 為目標。每個應用都是 `apps/` 下的獨立目錄，內含 `.config`、`CMakeLists.txt` 與 `Makefile`。可在 [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) 上執行的 9 個應用各有一頁，寫出建置、燒錄與執行的步驟；其他應用需要別的板卡，只列在[其他板卡的應用](#other-boards)。

## 在 Reef 上建置 { #overview }

多數應用的預設 `.config` 是其他板卡，Reef 使用應用目錄中的 Reef 設定檔，以 `DEFCONFIG=` 選用：

```bash
make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
```

| 項目 | 規則 |
|---|---|
| 建置目錄 | `DEFCONFIG=defconfig_<名稱>` 建置於 `build_<名稱>/`，`.config` 不變；不加 `DEFCONFIG=` 時建置於 `build/` |
| 映像 | `<建置目錄>/build_out/<應用>_IPRO7.bin`（IPRO6S 應用為 `_IPRO6.bin`） |
| 直接以 `make` 建置 Reef | 只有 `ipro7ai_reef_demo`、`ipro_reef_teach` 與 `ipro_agora_sentino`；其他應用不加 `DEFCONFIG=` 會建置成 IPRO7 EVB 或 IPRO7AI EVK 版 |
| 燒錄 | `--chipname ipro7 --chip-variant IPRO7AI`；分割表、boot2 與 mfg 資料依各應用頁面 |
| 主控台 | U6 的 UART0：除 `ipro7_jpeg_decode` 為 921600 外，Reef 設定都是 115200 baud |
| 一次完成 | `./build_freertos.sh -d defconfig_reef build flash monitor ipro_throughput_test`，自動選用 `--chip-variant IPRO7AI`，以 `-P` 指定分割表；無法寫入 boot2 與 mfg 資料（見[工具命令列](../reference/tools.md)） |

下載模式、主控台接線與第一次燒錄見 [Reef 上手](../hardware/boards/reef-evk.md#quick-start)。

## Reef EVK 範例 { #reef }

<!-- BEGIN generated: examples-reef -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7ai_reef_demo`](ipro7ai_reef_demo.md) | Reef 開箱韌體：RGB LED、按鍵、喇叭與耳機、PDM 與耳麥麥克風、microSD、OV5640 相機各有一組 shell 指令；`mic usb` 讓板子成為 USB 麥克風，`mic sdrec` 把錄音存成 SD 卡上的 WAV 檔 | Reef（`.config`）；Reef＋IPRO6S FIN 卡（`defconfig_wifi_ipro6s`：Wi-Fi 與 RTSP 相機串流） | UART 115200 |
| [`ipro_reef_teach`](ipro_reef_teach.md) | Reef 的 Edge AI 韌體：一個映像包含三個 Teach 工具，`image`（USB 相機＋影像分類）、`voice`（聲紋辨識）與 `sensor`（感測器分類），開機時依 Flash 中儲存的模式擇一執行，由 IPRO AI Studio 操作。完整操作見 [IPRO AI Teach](../teach/index.md) | Reef（`.config`）；`image` 模式需要 OV5640 相機 | UART 115200 |
| [`ipro_ble_remote`](ipro_ble_remote.md) | GATT 參考應用：LED、按鍵、環境、UART、相機影像與影像上傳服務；Reef 版另有 Reef 硬體服務與 BLE A/B OTA。隨附 Android 示範 App `ipro_remote_demo.apk`。教學見[第一個 BLE 應用](../tutorials/first-ble-app.md) | Reef（`defconfig_reef`：WS2812、相機、SD 卡、音訊與 BLE A/B OTA）；`.config`、`defconfig` 為 IPRO7 EVB | UART 115200 |
| [`ipro_throughput_test`](ipro_throughput_test.md) | 兩板 BLE 吞吐量測試：1M／2M／Coded PHY、DLE、ATT MTU 247。教學見 [BLE 吞吐量測試](../tutorials/ble-throughput.md) | 兩塊 Reef（`defconfig_reef`）；`.config` 為 IPRO7 EVB | UART 115200 |
| [`ipro_le_audio_headset`](ipro_le_audio_headset.md) | LE Audio unicast 耳機：BAP unicast server、PACS、ASCS、CAP、CSIP、VCP，LC3 解碼後由 DAC 輸出。教學見 [LE Audio 入門](../tutorials/le-audio.md) | Reef（`defconfig_reef`：DAC 輸出到耳麥孔與喇叭）；`.config`、`DAC.config`、`UAC.config` 為 IPRO7 EVB | UART 115200 |
| [`ipro7_uvc_cam`](ipro7_uvc_cam.md) | USB 網路攝影機：OV5640、ISP、硬體 MJPEG、USB Video Class；另一個 Reef 設定在 NPU 上跑剪刀石頭布並畫進影像。教學見 [USB 網路攝影機與剪刀石頭布](../tutorials/usb-webcam.md) | Reef（`defconfig_reef_ov5640`：網路攝影機；`defconfig_reef_rps`：剪刀石頭布）；`.config` 為 IPRO7 EVB 搭配 SC101IOT | Reef：UART 115200<br>`.config`：UART 921600 |
| [`ipro7_jpeg_decode`](ipro7_jpeg_decode.md) | 以軟體（TJpgDec）把 JPEG 解碼成 RGB565／RGB888，附格式探測、內建測試圖與主機端工具；IPRO7 的 MJPEG 硬體只能編碼 | Reef（`defconfig_reef`）；`.config` 為 IPRO7AI EVK | UART **921600** |
| [`ipro_ai_link`](ipro_ai_link.md) | IPRO AI Studio「Run on board」的板端韌體：由 microSD（`sd:/`）載入 `.inm` 模型與輸入、在 NPU 上推論、輸出原始結果；也可在主控台手動操作 | Reef（`defconfig_reef`）；`.config` 為 IPRO7 EVB | UART 115200（另有 USB CDC 主控台） |
| [`ipro_agora_sentino`](ipro_agora_sentino.md) | Sentino 雲端 AI 語音對話：BLE 配網、經 IPRO6S FIN 卡連 Wi-Fi、MQTT 登入、Agora RTC 即時語音；需另備 Sentino 裝置三元組與 AOSL 核心 | Reef＋IPRO6S FIN 卡（`.config`，`make` 或 `make BOARD=reef`）；`BOARD=evk` 為 IPRO7AI EVK（可建置，未經板上驗證） | Reef：UART 115200 |
<!-- END generated: examples-reef -->

## 其他板卡的應用 { #other-boards }

以下應用沒有 Reef 設定，需要表中所列的板卡；點選名稱開啟 GitHub 上的原始碼。這些板卡的供應請洽 INTELPRO。

### BLE { #ble }

<!-- BEGIN generated: examples-ble -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro_ble_transparent`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/bluetooth/ble/ipro_ble_transparent) | UART／BLE 透明傳輸橋接，以 AT 指令設定（AT 指令走 USB CDC） | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_ble_hid_keyboard`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/bluetooth/ble/ipro_ble_hid_keyboard) | HID over GATT 鍵盤 | 需要 IPRO7 EVB | UART 115200 |
<!-- END generated: examples-ble -->

### 音訊與語音 { #audio }

<!-- BEGIN generated: examples-audio -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro_pdm_mic_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/multimedia/ipro_pdm_mic_demo) | PDM 麥克風收音、DAC 播放、經 BLE 以 LC3 串流、SMP 配對、PDS31 休眠與綁定重連；Android 範例 App 原始碼在 `tools/android/IproMicDemo/`。Reef 上的錄音與播放見 `ipro7ai_reef_demo` 的 `mic` 指令 | 需要 IPRO7 EVB（`.config`）或 IPRO7AI EVK（`make BOARD=evk`） | EVB：UART 115200<br>EVK：UART 921600 |
<!-- END generated: examples-audio -->

### 平台與板卡 { #platform }

<!-- BEGIN generated: examples-platform -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7_demo) | 全晶片參考：PWM、SPI、I2S、LCD、音訊 ADC／DAC、USB 裝置（CDC、HID、MSC、UAC、UVC）、檔案系統、TRNG、DSP 等，各有 shell 指令 | 需要 IPRO7 EVB；另有 `defconfig_boot2_nopsram`、`defconfig_boot2_ota`、`defconfig_nist_fulltest`、`defconfig_security_cert` | UART 115200 |
| [`ipro7ai_evk_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_evk_demo) | IPRO7AI EVK bring-up：LCD、相機、麥克風、喇叭與 SD 卡；`config_bt` 加上 BLE 與 LE Audio | 需要 IPRO7AI EVK | `.config`：UART 921600<br>`config_*`：UART 115200 |
| [`ipro7ai_evk_launcher`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_evk_launcher) | 相機、LCD、麥克風與喇叭整合在單一映像，以 NPU 辨識手勢切換頁面 | 需要 IPRO7AI EVK | UART 921600 |
| [`ipro7ai_sensor_tag_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_sensor_tag_demo) | 讀取 6 軸 IMU、電量計、按鍵，控制 LED 與蜂鳴器；每秒 20 行 `名稱:數值` 經板子的 USB 送出，IPRO Workbench 0.2.0 的感測器儀表板依 `dashboard.yaml` 排版；經板子的 USB 以 `tools/ipro_dl.py` 燒錄 | 需要 IPRO7AI Sensor Tag | 板子的 USB（CDC） |
<!-- END generated: examples-platform -->

### AI 與影像 { #ai-vision }

<!-- BEGIN generated: examples-ai-vision -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7ai_evk_person_detect`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro7ai_evk_person_detect) | 相機預覽顯示在 LCD，疊加 NPU 執行 YOLOv8 的人形／寵物框 | 需要 IPRO7AI EVK | UART 115200 |
| [`ipro7ai_evk_rps`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro7ai_evk_rps) | 與 NPU 上的 int8 CNN 玩剪刀石頭布，附模型與訓練腳本；Reef 上的同一個遊戲為 `ipro7_uvc_cam` 的 `defconfig_reef_rps` | 需要 IPRO7AI EVK | UART 921600 |
| [`ipro_speaker_recog`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro_speaker_recog) | 以 NPU 辨識說話者，模型放在 mfg 分割區；Reef 上的聲紋辨識為 `ipro_reef_teach` 的 `voice` 模式 | 需要 IPRO7 EVB | UART 921600 |
<!-- END generated: examples-ai-vision -->

### 網路與 IPRO6S { #networking }

<!-- BEGIN generated: examples-networking -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro7_sdio_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7_sdio_wifi) | IPRO7 作為 SDIO 主機、IPRO6S 作為 Wi-Fi 無線電，提供 lwIP 網路介面 `iproeth0` 與 DHCP。Reef 上的同等功能為 `ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` | 需要 IPRO7 EVB 與 IPRO6S | UART 115200 |
| [`ipro6_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro6_demo) | IPRO6S Wi-Fi station／soft-AP 與 shell；`defconfig_ipro6_lpwifi` 加上 DTIM 省電，`defconfig_ipro6_lp` 為低功耗示範 | 需要 IPRO6S EVK（見 [IPRO6S](../hardware/chips/ipro6s.md)） | UART 115200 |
| [`ipro6_if_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro6_if_wifi) | IPRO6S Wi-Fi 橋接到主機：SDIO（`defconfig_ipro6_sdio`，也是 Reef FIN 卡的韌體）或 USB（`defconfig_ipro6_usb`） | IPRO6S EVK；FIN 卡（`defconfig_ipro6_sdio`，以 `--chipname ipro6` 燒錄，見 [IPRO6S](../hardware/chips/ipro6s.md)） | UART 115200 |
| [`ipro6_fmac`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro6_fmac) | 給 Linux cfg80211 主機的 FullMAC 韌體（`defconfig_ipro6_fmac`）與其 Flash 載入程式（`defconfig_ipro6_fmac_loader`）；Linux 驅動程式不在 SDK 內 | 需要 IPRO6S EVK | UART 115200 |
<!-- END generated: examples-networking -->

IPRO6S 應用以 `--chipname ipro6` 燒錄；建置與設定見 [IPRO6S](../hardware/chips/ipro6s.md)。

### 測試與 bring-up 程式 { #test-apps }

<!-- BEGIN generated: examples-test-apps -->
| 應用 | 用途 | 板卡與設定 | 主控台 |
|---|---|---|---|
| [`ipro_unit_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_unit_test) | HAL 與共用元件的單元測試，結束時印出 `ALL TESTS PASSED` 或 `SOME TESTS FAILED` | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_ai_bench`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_ai_bench) | 整個模型在 NPU 與 CPU 上的推論時間比較 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_npu_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_npu_yolo) | NPU 上的 YOLOv8 人形／寵物偵測 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_tflm_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_tflm_test) | TensorFlow Lite Micro 搭配 NMSIS-NN 核心的模型效能測試 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_tflm_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_tflm_yolo) | 以 TensorFlow Lite Micro 在 CPU 上執行 YOLOv8 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_nmsis_nn_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_nmsis_nn_test) | NMSIS-NN 運算子測試 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_tinymaix_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_tinymaix_demo) | TinyMaix INT8 MNIST 推論（`nn_info`、`nn_run`、`nn_benchmark`） | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_gh7007_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_gh7007_test) | GH7007 5 吋 SPI LCD bring-up | 需要 IPRO7 EVB | USB CDC |
| [`ipro_gh7007_video`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_gh7007_video) | 在 GH7007 面板播放 SD 卡上的影片 | 需要 IPRO7 EVB | USB CDC |
| [`ipro_epd_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_epd_test) | GDEY0213F52 2.13 吋電子紙 bring-up | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_epd_el036`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_epd_el036) | EL036MF1 電子紙 bring-up | 需要 IPRO7 EVB | UART 921600 |
| [`kw307_radar_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/kw307_radar_test) | KW307 24 GHz 雷達模組（UART） | 需要 IPRO7AI EVK | UART 115200 |
| [`mpu6500_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/mpu6500_test) | MPU-6500 IMU（I2C；`mpu_init`、`mpu_read`、`mpu_stream`） | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_enc28j60_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_enc28j60_test) | ENC28J60 SPI 乙太網路 bring-up，收發原始封包 | 需要 IPRO7 Arduino 板 | USB CDC |
| [`ipro_pio_sdh_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_pio_sdh_test) | 軟體（PIO）SD 主機與硬體 SDH 同時掛載的檔案系統測試 | 需要 IPRO7 EVB | USB CDC |
| [`ipro_sdio_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_sdio_probe) | SDIO 主機基本測試 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_atbm_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_atbm_probe) | ATBM6162 SDIO Wi-Fi 模組 bring-up 探測 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_lp_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_lp_test) | PDS31 進出與 RTC 喚醒測試（`lp` 指令） | 需要 IPRO7 EVB | UART 115200 |
<!-- END generated: examples-test-apps -->

## 下一步 { #next-steps }

- [建置與燒錄流程](../tutorials/build-and-flash.md)：在 Reef 上建置、燒錄與開啟主控台的完整流程。
- [建立第一個自己的應用](../tutorials/first-own-app.md)：從 Reef 的 `.config` 開始建立新應用。
- [建置系統與設定](../guides/build-system.md)：`DEFCONFIG=`、`BOARD=` 與設定檔。
- [Zephyr RTOS](../guides/zephyr.md)：`zephyr/samples/` 的 Zephyr 範例（本版沒有 Reef 的 Zephyr 板型）。
