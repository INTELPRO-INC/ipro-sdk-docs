---
title: "版本資訊"
description: IPRO SDK 各正式版本的發行日期、新增內容、未包含項目與已知限制，新版在前。
migrate_from:
  - "changelog.html"
---

# 版本資訊

IPRO SDK 的正式發行紀錄，新版在前；目前版本為 V2.2.0。各版本的下載檔與發行說明在 [GitHub Releases](https://github.com/INTELPRO-INC/IPRO-SDK/releases)；SDK 套件的整體說明見套件根目錄的 `README.md`。Windows 線上安裝程式 Online Setup 的版本也列在此頁（目前為 3.6.0），下載位置是 [ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest)。

## IPRO-SDK-V2.2.0 { #v2-2-0 }

<span class="ipro-badge">最新版本</span> 發行日期：2026-11-03 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0)

IPRO7／IPRO7AI 與 IPRO6S 雙晶片版本，取代 V2.1.0。共 40 個 FreeRTOS 應用：37 個 IPRO7、3 個 IPRO6S。下載檔為 `IPRO-SDK-V2.2.0.tar.gz`，SHA-256 見 Release 頁面。

**新增與變更**

- **IPRO6S 應用回到套件**：`ipro6_demo`（Wi-Fi 6 station／soft-AP，DTIM 低功耗）、`ipro6_if_wifi`（經 SDIO 或 USB 給主機用的 Wi-Fi 橋接）與 `ipro6_fmac`（FullMAC 韌體與其 Flash 載入程式）。Wi-Fi MAC、共存與 RF 函式庫依每個隨附的 `defconfig_*` 各自預編譯，每個設定連結為它建置的函式庫。Reef 的 FIN Wi-Fi 卡韌體即 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio`，見 [IPRO6S](../hardware/chips/ipro6s.md)。
- **新應用 `ipro_reef_teach`**：IPRO7AI Reef EVK 上的 Edge AI 韌體，內含三個 Teach 工具：`image`（USB 相機與分類器）、`voice`（辨識誰在說話）與 `sensor`（任何感測器）。開機時選定一個模式，每個模式有自己的 USB 識別，由 IPRO AI Studio 操作；也可用 `tools/teach_web/` 在瀏覽器中做影像 Teach。IPRO AI Studio 可從 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下載。
- **IPRO Edge AI 平台 V2.0**（`components/ai`）：執行環境、每個工具一個槽位的模型儲存區、輸入來源、前處理與應用框架；NPU 等待設有上限，逾時會重置該區塊並進入安全的故障狀態；Edge AI 韌體會啟用 AON 看門狗（進入下載模式時關閉）。修正 CPU 層圖讀取超出最後一筆層記錄的問題。
- **整晶片重置**：`hal_reboot_full()` 經 AON 看門狗重置整顆晶片，包含 always-on 電源域；啟用 `CONFIG_APP_WATCHDOG` 時，`platform_init()` 從開機一開始就啟動看門狗。`ipro_reef_teach` 以它切換工具，修正 Reef 接著相機時，從 `image` 模式切出後下一次開機可能停住直到重置的問題。
- **新應用 `ipro7_jpeg_decode`**：以軟體（TJpgDec）把 JPEG 解碼為 RGB565／RGB888，含格式檢查，並可解碼沒有 Huffman 表的相機 MJPEG 影格；IPRO7 的 MJPEG 硬體只能編碼。Reef 使用 `defconfig_reef`，主控台 921600 baud。
- **`ipro7ai_reef_demo`**：`mic usb` 讓 Reef 成為 USB 麥克風（16 kHz，由 PDM 時脈轉換取樣率）；`mic sdrec` 把錄音存成 SD 卡上的 WAV 檔。
- **`build_freertos.sh`**：`flash` 依設定檔自動選 `--chip-variant`（Reef 與 IPRO7AI EVK 為 `IPRO7AI`），可用 `-c` 或 `IPRO_CHIP_VARIANT` 覆寫；`-P` 或 `IPRO_FLASH_PT` 指定分割表；`flash` 送出的 `reboot_dl`、`monitor` 與 `test` 都使用應用自己的主控台鮑率。見[工具命令列](tools.md#build-cli)。
- **BLE 控制器**：IPRO7 的 16 個預編譯函式庫以本版原始碼重新建置；標頭檔宣告的 `ipro_ble_ctlr_heap_watermarks()` 與 `ipro_ble_ctlr_link_diag_start()` 現在可以連結使用。
- **USB 裝置**：修正 RX FIFO 溢位、反初始化時中斷連線、CDC-ECM 封包框架，USB 主控台可穩定連上。**lwIP**：在中斷中呼叫 `sys_mbox_trypost` 時改走 FromISR 路徑。Opus 改以自己的 `arch.h` 建置。
- **BSP**：只用 BLE 的應用可使用關閉 PLL 的系統時脈；`CONFIG_OCRAM_NORET_SCRATCH_ONLY` 讓 RAM 狀態留在 PDS 保留的 64 KB 內；`hal_lp_enter_fastboot()` 進入 HBN；安全引擎 HAL v2，含 PSA 加速器驅動。
- 範例應用不再內建任何網路帳號或密碼。

**應用**

- 共 40 個：37 個 IPRO7、3 個 IPRO6S。相較 V2.1.0，新增 `ipro_reef_teach`、`ipro7_jpeg_decode`、`ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`；V2.1.0 的語者辨識應用改名為 `ipro_speaker_recog`。
- 9 個應用附 IPRO7AI Reef EVK 的設定，清單與建置命令見[常見問題](faq.md#reef-apps)與 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)。

發行前以套件內容重新建置並檢查：36 個 IPRO7 FreeRTOS 應用（`ipro_agora_sentino` 需先取得 AOSL 核心）、IPRO6S 的 7 個設定，以及 `ipro7_evb`、`ipro7ai_evk` 的 Zephyr 範例。

**未包含**

- IntelProCube 燒錄工具與 RISC-V 工具鏈：請洽 INTELPRO。
- IPRO AI Studio（含模型轉換）：從 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下載。
- IPRO6S 的 BLE 控制器函式庫與 BLE／BR/EDR 應用；IPRO6S 應用只有 Wi-Fi。
- Matter；FreeRTOS 應用的 Thread（Thread 只在 Zephyr 下提供）。
- 晶片上除錯（OpenOCD／GDB）的設定、當機傾印的主機端工具、板級自動測試腳本、`menuconfig`。
- Zephyr：沒有 Reef 的板型；不支援 IPRO6S；沒有低功耗模式，也沒有顯示、相機、音訊編解碼、USB、SD 主機、乙太網路與 NPU 驅動。
- `ipro_agora_sentino` 需要的 AOSL 核心與 Sentino 裝置三元組：AOSL 從 GitHub 取得，步驟見該應用的 README。

### 已知問題與注意事項 { #v2-2-0-known-issues }

- **Reef 板級設定檔的註解**：`bsp/board/ipro7/ipro7ai_reef_board_config.h` 的註解描述的是前一版（V3.0）載板的擴充排針與跳線；腳位定義與 V4.0 相同。V4.0 的排針、開關與跳線以本站的 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) 為準。
- **兩個 IPRO6S 設定檔沒有對應的預編譯函式庫**：`ipro6_demo/defconfig_ipro6_lpwifi_ping` 與 `ipro6_fmac/defconfig_ipro6_fmac_ap` 隨附在套件中，但沒有設定 `CONFIG_WIRELESS_LIB_VARIANT`，不在發行前檢查的設定之列。請使用 [IPRO6S](../hardware/chips/ipro6s.md) 頁列出的設定檔。
- **`ipro_le_audio_headset`**：應用 README 的狀態欄標示音訊輸出（render）目前停用、媒體串流尚未驗證；依賴音訊輸出前請先看 README 的狀態說明。
- **`ipro_throughput_test` 的文件**：README 與 `OPERATION_MANUAL.md` 提到的示範應用、Android App 與控制器建置選項（例如 `CONFIG_BTBLECONTROLLER_LIB`、`link8`）不在本版中；建置與燒錄請依 README 的 Build／Flash 段落與 [BLE 吞吐量測試](../tutorials/ble-throughput.md)。
- **當機後的等待**：`ipro7ai_reef_demo` 與 `ipro_reef_teach` 設了 `CONFIG_EXCEPTION_DUMP=y`，當機後會重複印出 `==DUMP_READY:2000000==` 等待未隨附的主機端工具；存下診斷後按 SW2 重置，或把它設為 `n`。見[當機分析](debugging.md#crash-analysis)。
- **`build_freertos.sh` 只燒錄 IPRO7**：它固定傳 `--chipname ipro7`，也無法傳 `--boot2`、`--mfg`；IPRO6S 映像、`ipro_ble_remote` 的 OTA 版本與 `ipro_reef_teach` 請直接使用 IntelProCube。
- **README 中提到但未隨附的項目**：部分元件與應用的 README 提到不在本版中的應用、工具或文件（例如板子使用手冊與 Edge AI 程式設計指南）。文件可向 INTELPRO 索取，見[文件下載](../documents/index.md)。

## Online Setup 3.6.0 { #tools-3-6-0 }

發行日期：2026-11-04 ・ [下載安裝程式](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.6.0)

Windows 線上安裝程式。安裝 SDK V2.2.0 時修正它在 Windows 上的建置問題：辨識 IPRO 工具鏈（原本以 `/dev/null` 試編，Windows 上一律改用標準 GCC 旗標與非 DSP 版預編譯庫）、CMake 4 搭配 Ninja 時的建置訊息，以及序列埠主控台；並加入 PowerShell 版的 `build_freertos.ps1`。SDK only 與 Full 安裝出相同的 SDK：SDK 一律依搭配的工具鏈準備。SDK 與工具鏈可以加到既有環境，已安裝的檔案不覆蓋。工具鏈仍為 GCC 13.1.1、Extension 維持 3.3.0。操作見 [Windows 安裝與 VS Code](../get-started/windows.md)。

## IPRO-SDK-V2.1.0 { #v2-1-0 }

發行日期：2026-10-16 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0)

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

- IPRO6S 的應用、BLE 控制器函式庫與 `ipro6_rf`：套件 README 仍提到 IPRO6S，但本版沒有對應內容；當時 IPRO6S 開發請使用 V2.0.1；V2.2.0 起 IPRO6S 應用回到套件，見 [IPRO6S](../hardware/chips/ipro6s.md)。
- IPRO6S 端的 Wi-Fi 韌體（含 Reef 的 FIN 卡），請洽 INTELPRO。
- Matter；FreeRTOS 應用的 Thread（Thread 只在 Zephyr 下提供）；模型轉換工具。
- IntelProCube 燒錄工具與 RISC-V 工具鏈，需另行取得。

**已知限制**

- `ipro_ble_remote/defconfig_lowpower` 會改為從原始碼建置 BLE 控制器，無法以本套件建置。
- `build_freertos.sh flash` 不傳 `--chip-variant` 與 `--pt`，`monitor` 固定 115200 baud；IPRO7AI 板子與 921600 baud 的應用請直接使用工具。V2.2.0 已改善，見 [IPRO-SDK-V2.2.0](#v2-2-0)。
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

## Online Setup 3.5.0 { #tools-3-5-0 }

發行日期：2026-09-10 ・ [下載安裝程式](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.5.0)

每次執行時自動辨識 IPRO-SDK 的正式 SDK Release，支援 `.tar.gz` SDK 壓縮檔，並在完整安裝時為舊版 Windows linker 準備預編譯庫。

## IPRO-SDK-V2.0.1 { #v2-0-1 }

發行日期：2026-09-09 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)

延續 V2.0 的 IPRO6S 支援及 31 個應用專案，修正長時間 BLE 音訊傳輸。

- 修正連續傳輸時 Bluetooth Host queue 發布的原子性問題。
- PDM 邏輯錄音最長 4 小時，PSRAM ring 保留 240 秒，每 30 秒自動分段傳輸；Android 在分段間維持高連線優先權。
- PDM 改用 `link2` 控制器、單連線 Host 與 2M PHY，提供 EVB／EVK 配置與 Android 配套原始碼。
- 包含 IPRO6S Wi-Fi／BR/EDR 範例、SDIO 雙端韌體、NPU／TFLM 範例及 `.inm`／`.tflite` 模型。
- 包含 `ipro_unit_test` 與 Linux x86-64 CMake；1.2.1 的 `serial_monitor.py` 與 `PREBUILT-ARCHIVES-STRIPPED.txt` 不在此包。

正式發行紀錄記載 31/31 應用建置成功，並以 Pixel 7a 與 IPRO7AI 完成五分鐘錄音：十個 960,000 位元組的區塊、無掉包或序號缺口、ring 覆寫成功，穩態傳輸為 84.2–91.2 KB/s。數值對應該測試組合，不代表所有板子與手機皆有相同結果。

## Online Installer 3.4.0 { #tools-3-4-0 }

[下載安裝程式](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.4.0)

新增動態公開清單、獨立套件版本、完整安裝的相容性選擇，以及快取離線安裝。Extension 維持 3.3.0。此版只會安裝清單中登錄的 SDK（stable 為 1.2.1）；要安裝 SDK V2.2.0 請使用 3.6.0，見 [Windows 安裝與 VS Code](../get-started/windows.md)。

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
