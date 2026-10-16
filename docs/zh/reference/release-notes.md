---
title: "版本資訊"
description: IPRO SDK 各正式版本的發行日期、新增內容、未包含項目與已知限制，新版在前。
migrate_from:
  - "changelog.html"
---

# 版本資訊

IPRO SDK 的正式發行紀錄，新版在前。各版本的下載檔與發行說明在 [GitHub Releases](https://github.com/INTELPRO-INC/IPRO-SDK/releases)；SDK 套件的整體說明見套件根目錄的 `README.md`。

## IPRO-SDK-V2.1.0 { #v2-1-0 }

<span class="ipro-badge">最新版本</span> 發行日期：2026-10-16 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0)

新增 Zephyr RTOS 支援；FreeRTOS 應用以 IPRO7 為目標，共 35 個。

**新增與變更**

- **Zephyr RTOS**：SDK 同時是 Zephyr v4.4.0 模組（`zephyr/module.yml`、`west.yml`），支援 `ipro7_evb` 與 `ipro7ai_evk`：GPIO、UART、SPI、I2C、PWM、ADC、DAC、計時器與 RTC、看門狗、Flash、DMA、亂數產生器、I2S／PDM 等驅動，Bluetooth LE（Zephyr Host 搭配 IPRO BLE 控制器預編譯函式庫）、IEEE 802.15.4 與 OpenThread，以 sysbuild 建置的 MCUboot，以及經 BLE 的映像上傳（MCUmgr SMP）。從 `tools/zephyr/bootstrap.sh` 開始，見 [Zephyr RTOS](../guides/zephyr.md)。
- RF 驅動與 IEEE 802.15.4 MAC 以 Zephyr 用的預編譯函式庫提供（`components/wireless/rf/ipro7_rf/lib/zephyr/`、`components/wireless/ieee802154/lib/zephyr/`）。
- **新應用 `ipro_agora_sentino`**：在 IPRO7AI Reef EVK 上的 Sentino 雲端 AI 語音對話：BLE 配網、經 IPRO6S FIN 卡連 Wi-Fi、MQTT 與 Agora RTC。隨附 Agora RTC SDK 預編譯函式庫與 AOSL 的 IPRO7 移植；AOSL 核心、由 Sentino 平台配發的裝置三元組與 FIN 卡韌體需另行取得，方法見該應用的 README。
- **IPRO7AI Reef EVK 晶體微調**：Reef 建置預設把 RF 晶體 capcode 設為 95，於開機與每次 RF 初始化時套用（`CONFIG_IPRO7_XTAL_CAPCODE`，應用設定中明確指定的值優先）；預編譯的 RF 與 IEEE 802.15.4 函式庫會採用應用的設定值。Zephyr 在 Reef 上請設定 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`。
- **工具**：新增 `tools/serial_monitor.py`（`--timeout 0` 持續監看到 Ctrl-C，Linux 也可使用高鮑率）與 `tools/zephyr/`。`build_freertos.sh` 與 Zephyr 腳本的序列埠取自 `-p`／`IPRO_SERIAL_PORT`，未指定時自動使用唯一的 USB 序列埠；燒錄工具取自 `IPRO_FLASH_TOOL` 或 `PATH`。
- IPRO BLE 控制器的 16 個 IPRO7 預編譯函式庫已更新。

**應用**

- 共 35 個 FreeRTOS 應用。相較 V2.0.9，新增 `ipro_agora_sentino`。
- 相較 V2.0.1，新增 7 個：`ipro7ai_reef_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_ai_link`、`ipro_agora_sentino`；IPRO6S 的 3 個應用（`ipro6_btdm_phyrf`、`ipro6_demo`、`ipro6_if_wifi`）不再提供。

**未包含**

- IPRO6S 的應用、BLE 控制器函式庫與 `ipro6_rf`：套件 README 仍提到 IPRO6S，但本版沒有對應內容；IPRO6S 開發請使用 V2.0.1，見 [IPRO6S（V2.0.1）](../hardware/chips/ipro6s.md)。
- IPRO6S 端的 Wi-Fi 韌體（含 Reef 的 FIN 卡），請洽 INTELPRO。
- Matter；FreeRTOS 應用的 Thread（Thread 只在 Zephyr 下提供）；模型轉換工具。
- IntelProCube 燒錄工具與 RISC-V 工具鏈，需另行取得。

**已知限制**

- `ipro_ble_remote/defconfig_lowpower` 會改為從原始碼建置 BLE 控制器，無法以本套件建置。
- `build_freertos.sh flash` 不傳 `--chip-variant` 與 `--pt`，`monitor` 固定 115200 baud；IPRO7AI 板子與 921600 baud 的應用請直接使用工具，見[燒錄與序列埠](../get-started/flash-and-monitor.md#build-script)。
- Zephyr 尚無低功耗模式，也沒有顯示、相機、音訊編解碼、USB、SD 主機、乙太網路與 NPU 驅動；沒有 IPRO7AI Reef EVK 的板級定義。

發行時的建置與上板驗證紀錄見 GitHub Release 頁面。

## IPRO-SDK-V2.0.9 { #v2-0-9 }

發行日期：2026-10-15 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.9)

V2.1.0 之前的 IPRO7 版本，共 34 個應用，不含 Zephyr。

- 新增 IPRO7AI Reef EVK 開箱韌體 `ipro7ai_reef_demo`：LED、按鍵、喇叭與耳機、麥克風、SD 卡與 OV5640／OV2640 相機；`defconfig_wifi_ipro6s` 經 IPRO6S FIN 卡提供 Wi-Fi 與 RTSP 相機串流。
- 新增 IPRO7AI EVK 應用 `ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7ai_evk_person_detect`，建立在新的 EVK 板級函式庫 `components/board/ipro7ai_evk` 上。
- 新增 `ipro7_uvc_cam`（USB UVC 相機）與 `ipro_ai_link`（IPRO AI Studio 的上板執行）。
- AI 函式庫 `libai.a` 可從 SD 卡載入模型；預編譯函式庫不含建置機器的路徑。
- 只含 IPRO7 應用；IPRO6S 開發請使用 V2.0.1。

## IPRO-SDK-V2.0.1 { #v2-0-1 }

發行日期：2026-09-09 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)

延續 V2.0 的 IPRO6S 支援及 31 個應用專案，修正長時間 BLE 音訊傳輸。

- 修正連續傳輸時 Bluetooth Host queue 發布的原子性問題。
- PDM 邏輯錄音最長 4 小時，PSRAM ring 保留 240 秒，每 30 秒自動分段傳輸；Android 在分段間維持高連線優先權。
- PDM 改用 `link2` 控制器、單連線 Host 與 2M PHY，提供 EVB／EVK 配置與 Android 配套原始碼。
- 包含 IPRO6S Wi-Fi／BR/EDR 範例（見 [IPRO6S（V2.0.1）](../hardware/chips/ipro6s.md)）、SDIO 雙端韌體、NPU／TFLM 範例及 `.inm`／`.tflite` 模型。
- 包含 `ipro_unit_test` 與 Linux x86-64 CMake；1.2.1 的 `serial_monitor.py` 與 `PREBUILT-ARCHIVES-STRIPPED.txt` 不在此包。

正式發行紀錄記載 31/31 應用建置成功，並以 Pixel 7a 與 IPRO7AI 完成五分鐘錄音：十個 960,000 位元組的區塊、無掉包或序號缺口、ring 覆寫成功，穩態傳輸為 84.2–91.2 KB/s。數值對應該測試組合，不代表所有板子與手機皆有相同結果。

## Online Installer 3.4.0 { #tools-3-4-0 }

[下載安裝程式](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/online-installer-v3.4.0)

新增動態公開清單、獨立套件版本、完整安裝的相容性選擇，以及快取離線安裝。Extension 維持 3.3.0。2026-10-16 核對時，清單中的 SDK stable 仍為 1.2.1，尚未登錄 V2.x；SDK V2.x 需另由正式 Release 下載，見 [Windows 安裝與 VS Code](../get-started/windows.md#sdk-2-1-0)。

## 開發工具：Windows 安裝包／Extension 3.3.0 { #tools-3-3-0 }

安裝包與 Extension 獨立計版，此版對應 SDK V1.2.1。Windows 安裝精靈提供 Full、Extension only 與 SDK only 三種模式；Extension 新增從 VSIX、SDK ZIP／資料夾與 Git 快照更新元件的入口，並延續控制中心與 Windows 內建序列埠監看。操作見 [Windows 安裝與 VS Code](../get-started/windows.md) 與 [VS Code Extension](../guides/vscode.md)。

## IPRO-IPRO7-SDK-V1.2.1 { #v1-2-1 }

發行日期：2026-09-08 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/v1.2.1)

- Zephyr 4.4 Host 位於 `ipro_bt_host`；IPRO BLE 控制器（預編譯函式庫）位於 `ipro_ble_controller`。
- 16 個控制器預編譯函式庫：4 種 ACL 配置 × 2 種功能配置 × debug／release；不含控制器原始碼。
- 包含 IPRO7 端 `ipronet_host`、`sdiowifi` 元件與 `ipro7_sdio_wifi` 範例；相容的 IPRO6S 韌體需另行取得。
- AI 推論以 `components/ai/lib/libai.a` 與標頭提供，未隨附 `.blai` 模型檔。
- 隨附 `tools/serial_monitor.py`；燒錄工具、板級測試腳本、當機解析工具與 OpenOCD 設定需另行取得。
- 依 `PREBUILT-ARCHIVES-STRIPPED.txt`，AI、ISP、RF、LC3 與低功耗框架函式庫已移除除錯資訊，以相容 binutils 2.41 之前的連結器；無法在這些函式庫內做原始碼層級單步執行。

| 應用 | 路徑 | 說明 |
|---|---|---|
| `ipro_ble_remote` | `apps/bluetooth/ble/ipro_ble_remote/` | GATT 服務、影像傳輸與 OTA |
| `ipro_ble_transparent` | `apps/bluetooth/ble/ipro_ble_transparent/` | UART／BLE 透明傳輸 |
| `ipro_throughput_test` | `apps/bluetooth/ble/ipro_throughput_test/` | BLE 雙向吞吐量測試 |
| `ipro_ble_hid_keyboard` | `apps/bluetooth/ble/ipro_ble_hid_keyboard/` | HID over GATT 鍵盤 |
| `ipro_le_audio_headset` | `apps/bluetooth/le_audio/ipro_le_audio_headset/` | LE Audio 耳機，DAC／USB 音訊輸出配置 |
| `ipro_pdm_mic_demo` | `apps/multimedia/ipro_pdm_mic_demo/` | PDM 麥克風擷取、BLE 傳輸與 LC3 壓縮 |
| `ipro7_demo` | `apps/platform/ipro7_demo/` | 周邊、影像、音訊與乙太網路示範 |
| `ipro7_sdio_wifi` | `apps/platform/ipro7_sdio_wifi/` | IPRO7 SDIO 主機，搭配 IPRO6S 作為 Wi-Fi 無線電 |
| `ipro7ai_evk_demo` | `apps/platform/ipro7ai_evk_demo/` | IPRO7AI EVK 顯示、相機、音訊與 AI／BLE 配置 |

V1.0.1 的獨立影像擷取、BIS source／sink、雲端音訊閘道與語音助理應用未包含於此版。

## IPROREL-IPRO7-V1.0.1 { #v1-0-1 }

發行日期：2026-03-13 ・ 平台：IPRO7（RISC-V RV32IMAFC）

IPRO7 完整 SDK 交付包，整合平台、BLE、ISP 與 LE Audio，含 9 個參考應用、以 Zephyr 為基礎的 BLE Host、預編譯 linkN 控制器函式庫與統一建置系統。

| 分類 | 應用 | 說明 |
|---|---|---|
| bluetooth/ble | `ipro_ble_remote` | GATT 服務示範（LED、Button、UART、OTA、影像傳輸） |
| bluetooth/ble | `ipro_ble_transparent` | BLE 透明資料傳輸，含 AT 指令介面 |
| bluetooth/ble | `ipro_ble_img_capture` | 影像擷取與 BLE 影像上傳服務（含 OTA） |
| bluetooth/ble | `ipro_throughput_test` | 雙向 BLE 吞吐量測試（2M PHY + DLE） |
| bluetooth/le_audio | `ipro_le_audio_headset` | GAF／BAP 單播與廣播耳機（LC3） |
| bluetooth/le_audio | `ipro_le_audio_bis_source` | Auracast 相容 BIS 廣播音源 |
| bluetooth/le_audio | `ipro_le_audio_bis_sink` | BIS 廣播接收端（BASE 解析與音訊重取樣） |
| multimedia | `ipro_agora_sentino` | Agora RTC 雲端音訊串流閘道（經乙太網路／USB NCM 連網） |
| platform | `ipro7_demo` | IPRO7 平台周邊功能示範 |

- BLE 協定堆疊：以 Zephyr 為基礎的 Host（GAP、GATT、L2CAP、SMP、ISO、LE Audio）；IPRO BLE 控制器預編譯函式庫，含標準 BLE（`link1_periph`、`link1`–`link8`）、LE Audio（`link1_leaudio`、`link2_leaudio`）、BLE 5.4 + LE Audio（`link1_leaudio_53_54`、`link2_leaudio_53_54`、`link4_leaudio_53_54`）與 BLE 5.3／5.4（`link1_53`、`link1_54`、`link2_54`）等變體。
- 預編譯函式庫：`isp_algorithm`（ISP 影像處理）、`ipro7_rf`（RF 驅動）、`liblc3`（LC3 編解碼）、`lp_framework`（低功耗框架）。
- 已知限制：不含 BLE 控制器原始碼，僅提供 linkN 預編譯變體；不支援 `CONFIG_BLE_FORCE_SOURCE_BUILD`。

## IPRO-BLE-SDK-V0.0.1 { #v0-0-1 }

發行日期：2026-02-12 ・ 平台：IPRO7（RISC-V RV32IMAFC）

IPRO BLE SDK 首次正式發行，提供 BLE 5.4 與 LE Audio 開發環境，含 10 個應用、以 Zephyr 為基礎的 BLE Host、預編譯控制器函式庫與統一建置系統。

- BLE 應用：BLE Remote（GATT 服務示範）、Throughput Test（雙向吞吐量測試）、HID Keyboard（HOGP 鍵盤）、Transparent Data（透明傳輸與 AT 指令）。
- LE Audio 應用：LE Audio Headset（GAF／BAP 單播與廣播耳機）、BIS Broadcast Source（Auracast 相容廣播音源）、BIS Broadcast Sink（BASE 解析與重取樣）、Walkie-Talkie（以 BIS 實作的按鍵通話）。
- ESL 應用：ESL Tag（符合 Bluetooth ESL Profile 的電子標籤）、ESL Gateway（管理 ESL 標籤的存取點）。
- BLE 協定堆疊：IPRO BLE 控制器預編譯函式庫（linkN 變體，本版新增 `link2_54`）、預編譯 RF 驅動（`ipro7_rf`）與 LC3 編解碼（`liblc3`）；移除舊的 btprofile 元件，應用統一使用 Zephyr `bt_*` API。
- 建置系統：統一建置命令 `./build_freertos.sh <app> build flash monitor`、自動偵測 vendor 與標準 GCC 工具鏈、Kconfig 設定系統。
- 系統需求：RISC-V 工具鏈 `/opt/toolchain/riscv_ipro7/`、CMake 3.19 以上、Ninja、Python 3.8 以上。
- 已知限制：不含控制器原始碼；`ipro_blecontroller_test`（UART HCI 模式）因需要控制器原始碼而未包含；不支援 `CONFIG_BLE_FORCE_SOURCE_BUILD`。
