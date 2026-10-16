---
title: "低功耗"
description: FreeRTOS 應用的 WFI、PDS 與 HBN 低功耗模式：低功耗框架、設定、ipro_lp_test 測試指令、記憶體保留與喚醒、BLE 與睡眠、量測方法
migrate_from: []
---

# 低功耗

IPRO7 的 FreeRTOS 應用可使用三種省電狀態：WFI（FreeRTOS tickless idle）、PDS（Power-Down Sleep，Level 31，喚醒後原地繼續）與 HBN（Hibernate，喚醒時冷開機）。SDK 以預編譯的低功耗框架 `hal_lp` 提供 PDS 的進入與恢復，並附測試應用 `ipro_lp_test` 與 `ipro7_demo` 的低功耗指令。Zephyr RTOS 目前不支援低功耗模式。

!!! abstract "重點"
    - 框架：`bsp/hal/lp_framework/ipro7/`（`hal_lp.h`，預編譯 `liblp_framework.a`）與 `hal_pm.h`；自動選擇模式的 `components/sys/ipro_pm/`。
    - 測試：`apps/test/ipro_lp_test`（IPRO7 EVB，無 PSRAM、無 BLE）的 `lp` 指令。
    - 喚醒：PDS 可由 RTC 計時、GPIO 等喚醒；主控台 UART 無法喚醒 PDS。
    - 未包含：BLE 連線中的 PDS（需要 V2.1.0 沒有的控制器原始碼）。Zephyr 下沒有低功耗模式。

## 低功耗模式 { #modes }

| 模式 | 進入方式 | 保留的內容 | 喚醒來源 | 喚醒後 |
|---|---|---|---|---|
| WFI | FreeRTOS tickless idle（`CONFIG_FREERTOS_USE_TICKLESS_IDLE`） | 全部 | 任何中斷 | 原地繼續 |
| PDS（Level 31） | `hal_lp_enter()`，或低階的 `pm_pds_mode_enter(PM_PDS_LEVEL_31, …)` | OCRAM（見[保留與喚醒](#retention-wake)）、HBN RAM；可選擇讓 PSRAM 自刷新 | RTC 計時、GPIO、類比比較器（ACOMP）、BLE | 原地繼續；CPU、RF 與 MISC 電源域被重置，主控台 UART 與系統計時器要重新初始化 |
| HBN（Level 0） | `hal_lp_enter_fastboot()`，或低階的 `pm_hbn_mode_enter(PM_HBN_LEVEL_0, …)` | 只有 HBN RAM（4 KB）與 RTC | RTC 計時、AON 腳位、BOR、ACOMP | 冷開機，從頭執行韌體；以 `hal_lp_is_fastboot_wakeup()` 判斷 |

## 架構 { #architecture }

| 層 | 位置 | 內容 |
|---|---|---|
| 應用 | `ipro_lp_test`、`ipro7_demo`、`ipro_pdm_mic_demo` | 決定何時睡眠、要保留什麼、由什麼喚醒 |
| 自動模式選擇 | `components/sys/ipro_pm/`（原始碼） | 掛在 FreeRTOS tickless idle 上，依每段閒置時間與應用的保持條件選 WFI 或 PDS |
| 低功耗框架 | `bsp/hal/lp_framework/ipro7/`：`hal_lp.h`、`lp_uart.h`、`lib/liblp_framework.a`（預編譯，IPRO7 建置一律連結） | RTC／GPIO 喚醒、CPU 狀態保存與恢復、Flash XIP 與 PSRAM 恢復、虛擬時間、RC32K 校正、喚醒 hook |
| 低階電源管理 | `bsp/hal/inc/hal_pm.h` | `pm_pds_mode_enter()`、`pm_hbn_mode_enter()`、`pm_pds_gpio_wakeup_set()`、32 kHz 時脈來源選擇 |

## 設定 { #configuration }

```ini title="apps/test/ipro_lp_test/.config（節錄）"
CONFIG_EVB=y
# CONFIG_USE_PSRAM is not set
CONFIG_HAL_LP=y
CONFIG_FREERTOS_IDLE_HOOK=y
CONFIG_PLATFORM_UART_BAUDRATE=115200
```

| 設定 | 說明 |
|---|---|
| `CONFIG_HAL_LP` | 會進入睡眠的應用設定（`ipro_lp_test`） |
| `CONFIG_FREERTOS_IDLE_HOOK` | 啟用 `vApplicationIdleHook()`；`ipro_lp_test` 在其中執行自動 PDS |
| `CONFIG_FREERTOS_USE_TICKLESS_IDLE` | FreeRTOS tickless idle；閒置時 CPU 進入 WFI |
| `CONFIG_IPRO_PM` | 啟用 `ipro_pm`；必須同時設定 `CONFIG_FREERTOS_USE_TICKLESS_IDLE=1` 與 `CONFIG_FREERTOS_IDLE_HOOK=y`，否則建置以 `#error` 停止 |
| `CONFIG_IPRO_PM_MAX_MODE` | 開機時允許的最深模式：0 不睡眠、1 WFI（預設）、2 native、3 PDS；執行中可用 `ipro_pm_policy_set()` 改變 |
| `CONFIG_IPRO_PM_IDLE_PDS` | 由 idle 任務自行進入 PDS（BLE 控制器運作時不使用）；需同時設定 `CONFIG_IPRO_PM_TIMEBASE=y` |
| `CONFIG_IPRO_PM_SHELL` | `pm` shell 指令（狀態、策略、`pm stats`） |

`.config` 會原樣轉成 `autoconf.h`，Kconfig 的相依關係不會自動套用，相關設定都要寫出來。

!!! warning "與 HOTCODE 設定互斥"
    `CONFIG_IPRO7_BLE_HOTCODE` 與 `CONFIG_IPRO7_WIFI_HOST_HOTCODE` 不能和低功耗的記憶體配置（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_BLE` 等）同時使用，連結器腳本產生時會直接報錯。

## 測試應用 ipro_lp_test { #lp-test }

`apps/test/ipro_lp_test` 是不含 BLE 與 PSRAM 的最小專案，以 RTC 計時喚醒測試 PDS Level 31，設定對象為 IPRO7 EVB。

<div class="ipro-steps" markdown>

1. **建置**

    ```bash
    make -C apps/test/ipro_lp_test
    ```

    產出：`apps/test/ipro_lp_test/build/build_out/ipro_lp_test_IPRO7.bin`

2. **燒錄**：依 [IPRO7 EVB](../hardware/boards/ipro7-evb.md) 與[燒錄與序列埠](../get-started/flash-and-monitor.md)的步驟燒錄，主控台 115200 baud。

3. **測試**：依序輸入下列指令，確認每次都會喚醒並回到提示字元。

    ```text
    lp rtc
    lp sleep 1000
    lp status
    lp mem 1000
    ```

</div>

| 指令 | 用途 |
|---|---|
| `lp sleep <ms>` | 經 `hal_lp` 框架進入 PDS，RTC 計時喚醒 |
| `lp auto on`／`off` | 閒置時自動進入 PDS（每次 1 秒） |
| `lp status`、`lp reset` | 顯示／清除睡眠統計 |
| `lp heap` | 剩餘 heap |
| `lp rtc` | RTC 計數值（執行兩次確認有在計數） |
| `lp raw <ms>` | 繞過 `hal_lp` 的 PDS 測試（板子會重新開機） |
| `lp raw2 <ms> [fdpr]` | 最小 PDS 測試（f＝flash、d＝DLL、p＝PLL、r＝RF） |
| `lp hbn` | HBN 暫存器狀態 |
| `lp clk` | 睡眠前保存與目前的時脈狀態 |
| `lp fastboot <ms>` | 以冷開機路徑喚醒（指令不會返回） |
| `lp wakectx` | 上一次 fastboot 喚醒的內容（存於 HBN RAM） |
| `lp mem [ms]` | 檢查睡眠後 OCRAM 在 64 KB 以上與以下保留了哪些內容 |
| `lp misc on`／`off` | PDS 期間保持／關閉 MISC 電源域（預設 `off`） |

`ipro7_demo`（`CONFIG_DEMO_LOWPOWER=y`，隨附 `.config` 已開啟）另有 `lp_test [sleep_ms] [loop_count]`、`lp_gpio_test <gpio_pin> [trigger_mode]`、`pds_demo [sec]`、`hbn_demo [sec]` 與 `hbn_fastboot [ms]`。

## 程式介面 { #api }

下列流程取自 `apps/platform/ipro7_demo/demo/soc/peripheral/lowpower_demo.c`：初始化框架、註冊喚醒 hook、以 RTC 計時進入 PDS。

```c title="以 RTC 計時進入 PDS"
#include "hal_lp.h"

extern void shell_uart_reinit(void);
extern void vPortSetupTimerInterrupt(void);

static int wake_reinit(int wakeup_reason, void *arg)
{
    (void)wakeup_reason;
    (void)arg;
    shell_uart_reinit();          /* PDS 重置了主控台 UART */
    vPortSetupTimerInterrupt();   /* FreeRTOS 系統計時器 */
    /* 其他需要重新初始化的周邊（I2C、SPI…）放在這裡 */
    return 0;
}

int sleep_ms(uint32_t ms)
{
    static int initialized;
    if (!initialized) {
        if (hal_lp_init() != 0) {
            return -1;
        }
        hal_lp_register_wakeup_hook(wake_reinit, NULL);
        initialized = 1;
    }

    hal_lp_cfg_t cfg = {
        .rtc_wakeup_en    = 1,
        .rtc_sleep_us     = ms * 1000ULL,
        .flash_power_down = 1,
        .psram_retention  = 1,     /* 有 PSRAM 時保持自刷新 */
        .ocram_retention  = 1,
    };
    hal_lp_result_t res;
    int ret = hal_lp_enter(&cfg, &res);   /* 回傳喚醒原因（HAL_LP_WAKEUP_*）或負值錯誤 */
    if (ret == HAL_LP_ERR_ENTRY_ABORTED) {
        /* 有中斷待處理，沒有真正進入 PDS，等同一次 WFI */
    }
    return ret;
}
```

- `hal_lp_result_t` 提供喚醒原因、觸發的 GPIO 與實際睡眠時間；`hal_lp_get_virtual_ms()` 提供跨睡眠的連續時間。
- GPIO 喚醒：在 `hal_lp_cfg_t` 設定 `gpio_wakeup_en` 與 `gpio_cfg`（`wakeup_mask`、觸發方式、上下拉），可用 GPIO0–31。範例見 `ipro7_demo` 的 `lp_gpio_test`。
- 睡眠後 FreeRTOS 的 tick 不會自動補上：`ipro_lp_test` 以 `xTaskCatchUpTicks()` 補回實際睡眠時間。
- HBN：`hal_lp_enter_fastboot()` 進入後以冷開機喚醒，函式不會返回。開機時以 `hal_lp_is_fastboot_wakeup()` 判斷，`hal_lp_get_wake_context()` 讀取喚醒內容；要帶過睡眠的資料必須先放進 HBN RAM。

## 保留與喚醒 { #retention-wake }

- **OCRAM**：依 `ipro_lp_test` 的說明，它預設的 PDS31 設定會關閉 MISC 電源域，只保證保留 OCRAM 的前 64 KB；`lp misc on` 讓 MISC 電源域在 PDS 期間維持供電，保留整個 OCRAM。保留範圍取決於電源域設定，請把喚醒後要用的資料放在前 64 KB，並以 `lp mem` 在自己的設定下確認。
- **PSRAM**：以 `psram_retention` 讓 PSRAM 在 PDS 期間自刷新，框架在喚醒時恢復 PSRAM。IPRO7AI 的 PSRAM 封裝在晶片內，進入 PDS 時要保持自刷新。
- **HBN RAM**：4 KB，HBN 期間唯一保留的記憶體；框架的參數與 fastboot 喚醒內容也存放在這裡。
- **主控台**：UART0 位於 PDS31 會重置的電源域，喚醒後要重新初始化（`shell_uart_reinit()` 或 `platform_init()`）。主控台的 RX（GPIO21）無法喚醒 PDS，睡眠期間輸入的字元會遺失。
- **GPIO 喚醒**：`hal_lp` 支援 GPIO0–31；低階的 `pm_pds_gpio_wakeup_set()`（`hal_pm.h`）可用 GPIO0–41，但每 4 支腳共用一組觸發設定，且必須使用 ASYNC 觸發（SYNC 需要 PDS 期間停止的時脈）。HBN 只能由 AON 腳位喚醒。
- **32 kHz 時脈**：預設使用 RC32K；`pm_pds_set_32k_src()` 可改用 32 kHz 晶體（板上需有晶體）。框架提供 RC32K 校正函式。
- **Flash**：`flash_power_down = 1` 時 Flash 在睡眠期間斷電，框架在喚醒時恢復 XIP。

## BLE 與睡眠 { #ble-sleep }

- `ipro_pm` 的 BLE 後端與 BLE 連線中的 PDS（`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`）會強制從原始碼建置 BLE 控制器，而控制器原始碼未包含於 V2.1.0，因此無法從套件建置；`apps/bluetooth/ble/ipro_ble_remote/defconfig_lowpower` 也因此無法建置。需要 BLE 連線中低功耗的產品，請洽 INTELPRO。
- `apps/multimedia/ipro_pdm_mic_demo` 開啟 tickless idle，但隨附設定為 `CONFIG_IPRO_PDM_MIC_WFI_ONLY=1`：閒置時 CPU 進入 WFI，BLE 與 RF 持續運作；自動 PDS 選項 `CONFIG_IPRO_PDM_MIC_AUTO_PDS` 在所有隨附設定中都關閉。
- 同一應用的 `pds [sec]` 指令手動進入 PDS31，以計時或 GPIO 喚醒（腳位定義在 `src/pdm_sleep.c`），OCRAM 中的錄音緩衝在喚醒後仍在。
- BLE 控制器配置、Exchange Memory 大小等設定見 [BLE 開發](ble.md)。

## 量測 { #measure }

- 以外部電流表量測板子電源路徑的電流，量測點與方法見[電源與功耗量測](../hardware/power.md)。
- 以 `lp status` 確認實際進入睡眠的次數與時間，並記錄喚醒原因（`hal_lp_result_t`）；喚醒次數比預期多時，先檢查計時器與待處理中斷（`hal_lp_enter()` 回傳 `HAL_LP_ERR_ENTRY_ABORTED`）。
- 使用 `ipro_pm` 時，`pm stats` 列出各模式的停留比例與估算電流；估算值只用於比較設定，不能取代實測。
- 比較同一份韌體在 WFI 與 PDS 下的結果，並在睡眠前讓 UART 輸出完成，避免輸出被截斷。

## 本版限制 { #limitations }

- Zephyr RTOS 下沒有低功耗模式（不會經 `pm_state` 進入 PDS／HBN），見 [Zephyr RTOS](zephyr.md)。
- BLE 連線中的 PDS 無法從 V2.1.0 套件建置。
- 隨附的低功耗範例以 IPRO7 EVB 為對象；IPRO7AI Reef EVK 與 IPRO7AI EVK 沒有使用 PDS 的範例設定。
- `CONFIG_IPRO_PM_IDLE_PDS`（idle 任務進入 PDS）沒有隨附範例，使用前請在自己的板子上驗證。
- 低功耗記憶體配置不能與 HOTCODE 設定同時使用。

## 相關文件 { #related }

- [電源與功耗量測](../hardware/power.md)
- [BLE 開發](ble.md)
- [建置系統與設定](build-system.md)
- [Zephyr RTOS](zephyr.md)
