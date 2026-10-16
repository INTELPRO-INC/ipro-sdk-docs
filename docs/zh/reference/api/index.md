---
title: "API 參考"
description: "IPRO 專屬公開 C API：由 SDK V2.1.0 標頭以 Doxygen 產生的分類參考，加上平台初始化、BLE 控制器啟動與日誌的用法說明。"
migrate_from:
  - "api-reference.html — 第 3 階段改由 Doxygen 產生"
---

# API 參考

IPRO 專屬的公開 C API。下方「API 分類」由 SDK V2.1.0 隨附的公開標頭以 Doxygen 產生，每個函式、型別與巨集都附上標頭內的說明；其後幾節說明平台初始化、BLE 控制器啟動與日誌的用法。Zephyr Bluetooth 的 `bt_*` API 不在此重述，請直接查閱 [Zephyr 官方文件](#ble-host)。

!!! note "適用範圍"
    本頁的 HAL 與平台 API 用於 FreeRTOS 應用。Zephyr 應用請使用 Zephyr 的裝置驅動 API，見 [Zephyr RTOS](../../guides/zephyr.md)。

## API 分類 { #groups }

依功能分類的完整參考，產生自 SDK V2.1.0 的公開標頭。

<!-- BEGIN generated: api-groups -->
| 分類 | 標頭數 | 函式 | 內容 |
|---|---|---|---|
| [平台與系統](platform.md) | 11 | 65 | FreeRTOS 啟動與掛鉤、HAL 共用定義、系統控制、時脈、計時器、看門狗、RTC 與記憶體配置輔助。 |
| [記憶體、Flash 與開機](memory-boot.md) | 5 | 45 | Flash 讀寫、PSRAM、boot2 與分割表管理。 |
| [電源管理與低功耗](power.md) | 4 | 52 | 電源模式、PDS 休眠與喚醒，以及低功耗框架與低功耗 UART。 |
| [周邊 I/O](peripherals.md) | 13 | 62 | GPIO、UART、SPI、I2C、PWM、ADC、DAC、類比比較器、KeyScan、QDEC 與 DMA。 |
| [音訊](audio.md) | 3 | 16 | 音訊 ADC（PDM 與類比麥克風）與 I2S。 |
| [相機與影像](camera.md) | 4 | 36 | DVP 相機介面、ISP，以及硬體 MJPEG 編碼與解碼。 |
| [SD 卡與 SDIO](sd-sdio.md) | 4 | 61 | 硬體 SD 主機、SDIO，以及以 PIO 實作的 SD 主機。 |
| [乙太網路](ethernet.md) | 3 | 27 | EMAC、lwIP 網路介面與乙太網路 PHY。 |
| [PIO](pio.md) | 3 | 24 | 可程式 I/O：CCI、CMSIS-DAP 與掃描介面。 |
| [安全引擎](security.md) | 9 | 49 | AES、GMAC、雜湊、DSA、ECDSA、P-256 與硬體亂數。 |
| [無線與 BLE 控制器](wireless-ble.md) | 7 | 41 | 無線電初始化，以及 IPRO BLE 控制器的啟動、HCI 傳輸、低功耗與 NVDS 介面。 |
| [AI 執行庫](ai.md) | 18 | 133 | NPU 驅動、推論核心、運算子與後處理，以及偵測與語音模型的介面。 |
| [IPRO7AI EVK 板卡庫](ipro7ai-evk.md) | 12 | 113 | EVK 子板的面板、繪圖、相機、麥克風、喇叭、PCM 與 microSD 介面。 |
<!-- END generated: api-groups -->

## 平台初始化與 FreeRTOS 掛鉤 { #rtos-platform }

所有 FreeRTOS 應用共用 `components/os/freertos/freertos_app_hooks`，它提供平台初始化，以及堆積、FreeRTOS 掛鉤與 assert 的預設實作。

| API | 標頭檔 | 用途 |
|---|---|---|
| `void ipro_platform_init(void)` | `components/os/freertos/freertos_app_hooks.h` | 在 `main()` 開頭呼叫一次。依序執行 `platform_init()`、`ipro_setup_heap()`、`hal_boot2_init()`、PSRAM 檢查、`ipro_log_init()`（`CONFIG_IPRO_LOG_ENABLE`）、shell 初始化（`CONFIG_SHELL`）與 `ipro_pm_init()`（`CONFIG_IPRO_PM`）。 |
| `void ipro_setup_heap(void)` | 同上 | 從連結器符號收集 OCRAM 與 PSRAM（若啟用）的堆積區段，呼叫 `vPortDefineHeapRegions()`。`ipro_platform_init()` 已呼叫，應用不需再呼叫。 |
| `void ipro_dump_task_stacks(const char *where)` | 同上 | 列印每個任務的堆疊最低剩餘量（位元組）與剩餘堆積；需要 `configUSE_TRACE_FACILITY=1`。 |

下列 FreeRTOS 掛鉤在 `components/os/freertos/freertos_app_hooks.c` 以弱符號（weak）提供預設實作。要改寫時，在應用自己的原始檔定義同名的非弱符號函式即可，連結器會自動採用。

| 掛鉤 | 預設行為 |
|---|---|
| `vApplicationStackOverflowHook()` | 印出 `[!] Stack overflow: <任務名稱>` 與各任務堆疊剩餘量，然後停住。 |
| `vApplicationMallocFailedHook()` | 印出要求大小、剩餘與歷史最低堆積、呼叫者位址與任務名稱，然後停住；`pvPortMalloc(0)` 只警告。 |
| `vApplicationIdleHook()` | 執行 `__WFI()`。 |
| `vApplicationGetIdleTaskMemory()`、`vApplicationGetTimerTaskMemory()` | 提供 Idle 與 Timer 任務的靜態堆疊與 TCB。 |
| `vAssertCalled()` | 關閉中斷，印出 `[!] ASSERT <檔案>:<行號>` 與呼叫者位址，然後停住。 |

```c title="main.c（最小應用骨架，取自 SDK README）"
#include "freertos_app_hooks.h"
#include <FreeRTOS.h>
#include <task.h>

static void app_task(void *arg)
{
    for (;;) {
        /* 應用程式碼 */
    }
}

int main(void)
{
    ipro_platform_init();   /* 堆積、boot2、日誌、shell */
    xTaskCreate(app_task, "app", 1024, NULL, 5, NULL);
    vTaskStartScheduler();
    for (;;) {}
}
```

!!! warning "不要重複初始化"
    `ipro_platform_init()` 已初始化 shell 與日誌，請勿在應用中再呼叫一次。也不要把堆積、掛鉤或 assert 的樣板程式碼加回 `main.c`。

FreeRTOS 核心（V11.1.0）本身的 API（`xTaskCreate()`、佇列、號誌等）請見 [FreeRTOS API 參考](https://www.freertos.org/Documentation/02-Kernel/04-API-references/01-Task-creation/00-TaskHandle)。`xTaskCreate()` 的堆疊深度單位是 word，不是位元組。

## BLE 控制器啟動 { #ble-core }

BLE 由 Zephyr v4.4.0 Host 與 IPRO BLE 控制器（預編譯函式庫）組成，兩者以記憶體內的 HCI 位元組串流相連。應用必須依序啟動控制器、HCI 驅動與 Host。

| API | 標頭檔 | 用途 |
|---|---|---|
| `int ipro_ble_ctlr_controller_init(unsigned int task_priority)` | `components/wireless/bluetooth/ipro_ble_controller/include/ipro_ble_controller.h` | 啟動控制器並建立控制器任務。回傳 0 成功、-1 已啟動、-2 建立任務失敗。控制器有無線電時限，優先權應高於應用任務；隨附應用使用 `configMAX_PRIORITIES - 1`。 |
| `int hci_driver_ipro_ble_ctlr_init(void)` | `components/wireless/bluetooth/ipro_bt_host/port/include/hci_driver_ipro_ble_ctlr.h` | 在 `bt_enable()` 之前呼叫。Zephyr 4.4 於建置時就綁定 HCI 裝置，此函式為與既有應用的原始碼相容而保留，隨附應用仍依此順序呼叫。 |
| `void ipro_ble_ctlr_hcitl_host_ready(void)` | `components/wireless/bluetooth/ipro_ble_controller/hcitl/ipro_ble_ctlr_hcitl.h`（由 `ipro_ble_controller.h` 引入） | 在 `bt_enable()` 的就緒回呼中呼叫，標記 HCI 初始化完成；之後控制器可以在事件之間休眠。 |
| `int bt_enable(bt_ready_cb_t cb)` | `<zephyr/bluetooth/bluetooth.h>` | 啟動 Host，完成時呼叫 `cb`。見 [Zephyr Bluetooth API](#ble-host)。 |

三個呼叫之間各等 50 ms，在 FreeRTOS 任務中執行；完整的啟動程式與就緒回呼見 [BLE 開發](../../guides/ble.md#ble-init)。

控制器函式庫由 `.config` 的 `CONFIG_IPRO_BLE_CTLR_LIB`、`CONFIG_IPRO_BLE_CTLR_FEATURE` 與 `CONFIG_IPRO_BLE_CTLR_CFG_DBG` 選擇，對照表見 [BLE 開發](../../guides/ble.md#controller-variants)。

## Zephyr Bluetooth API { #ble-host }

應用使用 Zephyr 的 `bt_*` 回呼式 API，標頭以 `<zephyr/bluetooth/...>` 引入；SDK 內的副本位於 `components/wireless/bluetooth/ipro_bt_host/upstream/zephyr/include/zephyr/bluetooth/`。下列連結皆指向 Zephyr v4.4.0 版文件，與 SDK 匯入的 Host 版本一致。

| 主題 | 常用 API | Zephyr v4.4.0 文件 |
|---|---|---|
| Bluetooth API 總覽 | — | [Bluetooth API](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/index.html) |
| GAP：啟動、廣播、掃描 | `bt_enable()`、`bt_le_adv_start()`、`bt_le_scan_start()` | [Generic Access Profile (GAP)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gap.html) |
| 連線管理 | `bt_conn_cb_register()`、`bt_conn_le_create()`、`bt_conn_disconnect()` | [Connection Management](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/connection_mgmt.html) |
| GATT 伺服器與用戶端 | `BT_GATT_SERVICE_DEFINE()`、`bt_gatt_notify()`、`bt_gatt_discover()` | [Generic Attribute Profile (GATT)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gatt.html) |
| LE Audio | BAP、PACS、ASCS、CAP | [Bluetooth Audio](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/audio/audio.html) |
| 配對資料儲存 | `settings_load_subtree()` | [Settings](https://docs.zephyrproject.org/4.4.0/services/settings/index.html) |
| 完整函式索引 | — | [Zephyr API 文件（Doxygen）](https://docs.zephyrproject.org/4.4.0/doxygen/html/group__bluetooth.html) |

!!! tip "以 SDK 內的標頭為準"
    Zephyr 文件以 Zephyr 核心為前提；在 FreeRTOS 應用中，Host 透過 SDK 的移植層執行，相關 `CONFIG_BT_*` 項目寫在應用的 `.config`。巨集是否存在請以 SDK 內的標頭為準，例如連線式廣播可用 `BT_LE_ADV_CONN_FAST_1`，而 `BT_LE_ADV_CONN_NAME` 在此版本的 Host 中不存在。

## 日誌 { #log-api }

標頭：`components/utils/include/ipro_log.h`（設定預設值在 `ipro_log_config.h`）。需要 `CONFIG_IPRO_LOG_ENABLE=y`；`ipro_platform_init()` 會以預設設定呼叫 `ipro_log_init()`。

| API | 用途 |
|---|---|
| `IPRO_LOGE`、`IPRO_LOGW`、`IPRO_LOGI`、`IPRO_LOGD`、`IPRO_LOGV`（`tag, format, ...`） | 錯誤、警告、資訊、除錯、詳細等級的日誌。等級高於 `CONFIG_LOG_DEFAULT_LEVEL` 的呼叫不會輸出 |
| `IPRO_LOG_BUFFER_HEX(tag, buf, len)`、`IPRO_LOG_BUFFER_HEXDUMP(tag, buf, len)` | 以十六進位（加 ASCII）傾印緩衝區 |
| `ipro_log_set_level()`、`ipro_log_get_level()`、`ipro_log_level_enabled()` | 執行時調整或查詢等級 |
| `ipro_log_set_output_func()` | 改用自訂輸出函式 |

`CONFIG_LOG_DEFAULT_LEVEL` 是整數：1 錯誤、2 警告、3 資訊（隨附應用的設定）、4 除錯、5 詳細。輸出格式為 `<等級字母> (<時間>) <TAG>: <訊息>`。

```c title="日誌（每個檔案定義自己的 TAG）"
#include "ipro_log.h"

#define TAG "MY_MODULE"

IPRO_LOGI(TAG, "connected, handle %u", handle);
IPRO_LOGE(TAG, "init failed (err %d)", err);
```

## 相關文件 { #related }

- [BLE 開發](../../guides/ble.md)：控制器選擇、初始化順序與 GATT 範例。
- [建置系統與設定](../../guides/build-system.md)：`.config` 與應用結構。
- [除錯與疑難排解](../debugging.md)：日誌、當機輸出與 FreeRTOS 掛鉤的訊息。
- IPRO7 API 規格書：見[文件下載](../../documents/index.md)。
