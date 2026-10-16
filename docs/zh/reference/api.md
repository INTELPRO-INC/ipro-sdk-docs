---
title: "API 參考"
description: IPRO 專屬公開 API 索引：平台初始化與 FreeRTOS 掛鉤、BLE 控制器啟動、HAL 周邊、日誌、IPRO7AI EVK 板級函式庫與 AI 推論執行庫，附標頭檔路徑與用途。
migrate_from:
  - "api-reference.html — 第 3 階段改由 Doxygen 產生"
---

# API 參考

本頁列出開發 IPRO7 FreeRTOS 應用最常用的 IPRO 專屬公開 API：每一項都附上標頭檔（路徑相對於 SDK 根目錄）與一行用途，範例只取自 SDK 隨附的應用。Zephyr Bluetooth 的 `bt_*` API 不在此重述，請直接查閱 [Zephyr 官方文件](#ble-host)。

!!! info "過渡版本"
    本頁為人工整理的過渡版參考，之後將由從原始碼產生的完整 API 參考（Doxygen）取代。參數、回傳值與限制以標頭檔註解為準；HAL 的完整說明另見 [文件下載](../documents/index.md) 中的《API 規格書》。

!!! note "適用範圍"
    本頁的 HAL 與平台 API 用於 FreeRTOS 應用。Zephyr 應用請使用 Zephyr 的裝置驅動 API，見 [Zephyr RTOS](../guides/zephyr.md)。

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

三個呼叫之間各等 50 ms，在 FreeRTOS 任務中執行；完整的啟動程式與就緒回呼見 [BLE 開發](../guides/ble.md#ble-init)。

控制器函式庫由 `.config` 的 `CONFIG_IPRO_BLE_CTLR_LIB`、`CONFIG_IPRO_BLE_CTLR_FEATURE` 與 `CONFIG_IPRO_BLE_CTLR_CFG_DBG` 選擇，對照表見 [BLE 開發](../guides/ble.md#controller-variants)。

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

## HAL 周邊 { #hal }

HAL 標頭位於 `bsp/hal/inc/`，實作在 `bsp/hal/src/`。下表只列名稱與用途；控制命令、結構與裝置編號定義在各標頭中。

### GPIO { #hal-gpio }

標頭：`bsp/hal/inc/hal_gpio.h`。腳位以編號傳入（IPRO7 為 GPIO 0–41），`GPIO_PIN_x` 列舉只是便利常數。

| API | 用途 |
|---|---|
| `gpio_set_mode(pin, mode)` | 設定模式，例如 `GPIO_OUTPUT_PP_MODE`、`GPIO_INPUT_PD_MODE`、`GPIO_ASYNC_FALLING_TRIGER_INT_MODE`、`GPIO_HZ_MODE` |
| `gpio_write(pin, value)`、`gpio_toggle(pin)`、`gpio_read(pin)` | 輸出、切換、讀取 |
| `gpio_attach_irq(pin, cb)`、`gpio_irq_enable(pin, enabled)` | 掛上中斷回呼並啟用中斷 |

```c title="LED 輸出（取自 ipro_ble_remote）"
gpio_set_mode(LED_GPIO_PIN, GPIO_OUTPUT_PP_MODE);
gpio_write(LED_GPIO_PIN, 0);    /* 先關閉 LED */
```

### UART { #hal-uart }

標頭：`bsp/hal/inc/hal_uart.h`。裝置編號 `UART0_INDEX`、`UART1_INDEX`；UART0 為主控台與 shell 使用。

| API | 用途 |
|---|---|
| `uart_init(uart_id, oflag)`、`uart_uninit(uart_id)` | 開啟、關閉 |
| `uart_write(uart_id, buf, size)`、`uart_read(uart_id, buf, size)` | 傳送、接收 |
| `uart_read_available(uart_id, buf, max)` | 非阻塞讀取 RX FIFO 中已有的資料 |
| `uart_set_baudrate(uart_id, baud)`、`uart_set_callback(uart_id, args)`、`uart_ioctl(uart_id, cmd, args)` | 鮑率、事件回呼、控制命令（`UART_CTRL_*`） |

### SPI 與 I2C { #hal-spi-i2c }

| API | 標頭檔 | 用途 |
|---|---|---|
| `spi_init()`、`spi_deinit()`、`spi_setConfig()`、`spi_enable()`、`spi_ioctl()` | `bsp/hal/inc/hal_spi.h` | 開啟、設定與啟用 SPI（`SPI0_INDEX`、`SPI1_INDEX`） |
| `spi_transmit()`、`spi_receive()`、`spi_transmit_receive()` | 同上 | 傳送、接收、全雙工傳輸 |
| `i2c_init()`、`i2c_setConfig()` | `bsp/hal/inc/hal_i2c.h` | 開啟與設定 I2C（`I2C0_INDEX`、`I2C1_INDEX`） |
| `i2c_transfer(i2c_id, msgs, num)` | 同上 | 傳送一組 `i2c_msg_t` 訊息（從端位址、子位址、`I2C_RD` 旗標、長度、緩衝區） |

### PWM、ADC 與 DAC { #hal-pwm-adc }

| API | 標頭檔 | 用途 |
|---|---|---|
| `pwm_init()`、`pwm_ioctl()`、`pwm_close()` | `bsp/hal/inc/hal_pwm.h` | 開啟、控制、關閉 PWM 通道 |
| `pwm_channel_start()`、`pwm_channel_stop()`、`pwm_channel_freq_update()`、`pwm_channel_dutycycle_update()` | 同上 | 以 `pwm_ioctl()` 實作的便利巨集 |
| `hal_adc_init()`、`hal_adc_read()`、`hal_adc_ioctl()` | `bsp/hal/inc/hal_adc.h` | 開啟、讀取、控制 ADC（`ADC_CTRL_CHANNEL_START`、`ADC_CTRL_CHANNEL_STOP`、`ADC_CTRL_CHANNEL_CONFIG`） |
| `hal_adc_get_tsen()`、`hal_adc_trim_tsen()` | 同上 | 讀取內部溫度感測器 |
| `hal_dac_init()`、`hal_dac_write()`、`hal_dac_control()`、`hal_dac_deinit()` | `bsp/hal/inc/hal_dac.h` | DAC 輸出 |

!!! warning "ADC 便利巨集無法使用"
    `hal_adc.h` 中的 `adc_channel_start()`、`adc_channel_stop()`、`adc_channel_config()` 會展開成不存在的 `adc_ioctl()`，連結時會失敗。請直接以 `hal_adc_ioctl()` 搭配對應的 `ADC_CTRL_*` 命令。

### 計時與看門狗 { #hal-timer }

| API | 標頭檔 | 用途 |
|---|---|---|
| `timer_init()`、`timer_setCallback()`、`timer_start()`、`timer_stop()`、`timer_get_counter()` | `bsp/hal/inc/hal_timer.h` | 硬體計時器（設定結構 `hal_timer_config_t`） |
| `mtimer_get_time_ms()`、`mtimer_get_time_us()`、`mtimer_delay_ms()`、`mtimer_delay_us()` | `bsp/hal/inc/hal_mtimer.h` | 系統計時器時間戳記與忙等延遲 |
| `wdt_init()`、`wdt_feed()`、`wdt_disable()`、`wdt_setTimeout()` | `bsp/hal/inc/hal_wdt.h` | 看門狗 |
| `rtc_set_timestamp()`、`rtc_get_timestamp()` | `bsp/hal/inc/hal_rtc.h` | RTC 時間戳記 |

### Flash、分割區與系統 { #hal-system }

| API | 標頭檔 | 用途 |
|---|---|---|
| `flash_read()`、`flash_write()`、`flash_erase()` | `bsp/hal/inc/hal_flash.h` | 以 Flash 實體位址讀、寫、抹除（不是 `0x13000000` 起的 XIP 映射位址） |
| `flash_get_jedecid()`、`flash_get_size()` | 同上 | Flash JEDEC ID 與容量 |
| `hal_boot2_partition_addr_active(name, &addr, &size)` | `bsp/hal/inc/hal_boot2.h` | 依分割表名稱取得使用中分割區的 Flash 位址與大小；AI 範例用它找到 `mfg` 分割區中的模型 |
| `hal_reboot()`、`hal_reboot_download()` | `bsp/hal/inc/hal_sys.h` | 重新開機；重新開機進入下載模式（shell 指令 `reboot`、`reboot_dl` 即呼叫這兩個函式） |
| `hal_rand()`、`hal_rand_stream(buf, len)` | `bsp/hal/inc/hal_sec_trng.h` | 硬體亂數 |

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

## IPRO7AI EVK 板級函式庫 { #evk-board }

`components/board/ipro7ai_evk` 是 IPRO7AI EVK 子板（`CONFIG_IPRO7AI_EVK`）的板級函式庫：一個 `evk.h`、一次 `evk_begin()`，即可使用板上的面板、相機、麥克風、喇叭與 microSD。標頭位於 `components/board/ipro7ai_evk/include/`。IPRO7AI Reef EVK 不使用此函式庫。

| 區塊 | 標頭 | 主要 API | `.config` |
|---|---|---|---|
| 板子初始化 | `evk.h` | `evk_begin()`（相機待命、喇叭放大器關閉、面板初始化並清畫面；在第一個任務中呼叫一次）、`evk_ready()` | `CONFIG_COMPONENTS_IPRO7AI_EVK_ENABLE=y` |
| 面板與繪圖 | `st7789p3.h`、`evk_gfx.h` | `st7789p3_blit_start()`、`st7789p3_blit_push()`、`evk_gfx_text_at()`、`evk_gfx_text_centered()`、`evk_gfx_splash()` | 同上 |
| 相機 | `evk_cam.h` | `evk_cam_start()`、`evk_cam_stop()`、`evk_cam_set_frame_cb()`、`evk_cam_set_npu_input()`、`evk_cam_set_npu_frame_cb()`、`evk_cam_npu_rearm()` | `CONFIG_EVK_CAMERA=y` |
| 麥克風 | `evk_mic.h` | `evk_mic_start()`、`evk_mic_read()`、`evk_mic_stop()`、`evk_mic_set_gain_db()` | `CONFIG_EVK_AUDIO=y` |
| 喇叭 | `evk_spk.h`、`evk_pcm.h` | `evk_spk_open()`、`evk_spk_write()`、`evk_spk_tone()`、`evk_spk_set_volume()`、`evk_spk_close()`；`evk_pcm_*` 為整數 PCM 運算 | `CONFIG_EVK_AUDIO=y` |
| microSD | `evk_sd.h` | `evk_sd_present()`、`evk_sd_mount()`、`evk_sd_exists()`、`evk_sd_unmount()`；檔案系統掛在 `sd:/` | `CONFIG_EVK_SDCARD=y` |
| Shell 指令 | — | `lcd`、`cam`、`mic`、`spk`、`sd` | `CONFIG_EVK_SHELL=y`（應用自有同名指令時請勿開啟） |

各區塊還需要其他相依設定，例如相機需 `CONFIG_MM_SUPPORT=y`、`CONFIG_COMPONENTS_SENSOR_ENABLE=y` 與 `CONFIG_USE_PSRAM=y`；完整清單見 SDK 內的 `components/board/ipro7ai_evk/README.md`。相機、音訊或 SD 卡缺少必要設定時，CMake 設定階段會直接報錯。

```c title="板子初始化與相機啟動（取自 ipro7ai_evk_launcher）"
#include "evk.h"

static void app_task(void *param)
{
    evk_begin();                    /* 相機待命、放大器關閉、面板就緒 */
    if (evk_cam_start() != EVK_CAM_OK) {
        IPRO_LOGE(LOG_TAG, "camera start failed");
    }
    /* ... */
}
```

## AI 推論執行庫 { #ai-runtime }

NPU 推論執行庫以預編譯函式庫 `components/ai/lib/libai.a` 提供，SDK 只附標頭。應用的 `.config` 需設定 `CONFIG_AI_SUPPORT=y`，並明確設定 `CONFIG_USE_PSRAM=y`（建置不會自動帶入）。

| API | 標頭檔 | 用途 |
|---|---|---|
| `iproai_npu_init()` | `components/ai/src/inst/include/iproai_inst_npu.h` | 初始化 NPU；在建立模型前呼叫一次 |
| `iproai_create()` | `components/ai/src/core/include/iproai_core.h` | 建立模型 handle（`iproai_model_hdl_t`），失敗回傳 `NULL` |
| `iproai_load_model_from_buffer(hdl, buf)` | 同上 | 從記憶體載入 `.inm` 模型，例如連結進韌體或經 XIP 讀取 `mfg` 分割區 |
| `iproai_load_model_from_file(hdl, path)` | 同上 | 從 SD 卡載入模型，路徑使用 FatFS 的 `sd:/...` 形式；需 `CONFIG_AI_MODEL_FROM_FILE=y` |
| `iproai_getNetInfo(hdl)` | 同上 | 取得模型資訊（輸入尺寸、層數、NPU 層數） |
| `iproai_setResultCB(hdl, cb)`、`iproai_setCustom_Postproc_CB(hdl, cb)` | 同上 | 推論結果回呼、自訂後處理回呼 |
| `iproai_startCompute(hdl)` | 同上 | 執行一次推論 |
| `iproai_getInputBuffer()`、`iproai_getOutputBuffer()`、`iproai_getInputResolution()`、`iproai_setSourceResolution()` | 同上 | 輸入輸出緩衝區與解析度 |
| `iproai_free(hdl)` | 同上 | 釋放模型 |
| `NPU_Img_Ext_Addr_Cfg(addr)` | `bsp/hal/inc/hal_npu.h` | 設定 NPU 讀取輸入影像的位址 |

函式回傳 `IPROAI_Status_e`（`components/ai/iproai_def.h`），成功為 `IPROAI_STATUS_NO_ERROR`。

```c title="從 SD 卡載入並執行模型（依 ipro_ai_link 整理）"
#include "iproai_core.h"
#include "hal_npu.h"
#include "drv_glb.h"

GLB_PER_Clock_UnGate(GLB_AHB_CLOCK_MM);
iproai_npu_init();

iproai_model_hdl_t hdl = iproai_create();
if (hdl == NULL ||
    iproai_load_model_from_file(hdl, "sd:/model.inm") != IPROAI_STATUS_NO_ERROR) {
    /* 處理錯誤 */
}
iproai_setResultCB(hdl, on_result);

/* 每次推論：輸入緩衝區前 4 個位元組為大小表頭，影像從 +4 開始 */
NPU_Img_Ext_Addr_Cfg((uint32_t)(uintptr_t)(input + 4));
if (iproai_startCompute(hdl) != IPROAI_STATUS_NO_ERROR) {
    /* 處理錯誤 */
}
```

模型轉換工具未包含於 V2.1.0，請洽 INTELPRO。模型存放位置與 NPU 記憶體預算見 [AI 與 NPU](../guides/ai-npu.md)。

## 相關文件 { #related }

- [BLE 開發](../guides/ble.md)：控制器選擇、初始化順序與 GATT 範例。
- [建置系統與設定](../guides/build-system.md)：`.config` 與應用結構。
- [除錯與疑難排解](debugging.md)：日誌、當機輸出與 FreeRTOS 掛鉤的訊息。
- IPRO7 API 規格書：見[文件下載](../documents/index.md)。
