---
title: "低功耗"
description: IPRO7 FreeRTOS 應用的 WFI、PDS 與 HBN：低功耗框架、設定、程式介面、記憶體保留與喚醒、BLE 與睡眠，以及在 Reef 上量測 IPRO7AI 的電流
migrate_from: []
---

# 低功耗

IPRO7 的 FreeRTOS 應用可使用三種省電狀態：WFI（FreeRTOS tickless idle）、PDS（Power-Down Sleep，Level 31，喚醒後原地繼續）與 HBN（Hibernate，喚醒時冷開機）。SDK 以預編譯的低功耗框架 `hal_lp` 提供 PDS 的進入與恢復，並以 `ipro_pm` 自動選擇 WFI 或 PDS。在 IPRO7AI Reef EVK 上可以用 SW8 與 JP2 量測 IPRO7AI 本身的電流；隨附的 Reef 設定檔都不會進入 PDS。

!!! abstract "重點"
    - 框架：`bsp/hal/lp_framework/ipro7/`（`hal_lp.h`、預編譯的 `liblp_framework.a`）與 `hal_pm.h`；自動選擇模式的 `components/sys/ipro_pm/`。
    - Reef：隨附的 Reef 設定檔都沒有使用 PDS。SW8 與 JP2 可以把電流表串進 IPRO7AI 的 3.3 V 電源。
    - 喚醒：PDS 可由 RTC 計時、GPIO 等來源喚醒；主控台 UART 無法喚醒 PDS。
    - 未包含：BLE 連線中的 PDS（需要從原始碼建置控制器）。Zephyr 下沒有低功耗模式。

## 低功耗模式 { #modes }

| 模式 | 進入方式 | 保留的內容 | 喚醒來源 | 喚醒後 |
|---|---|---|---|---|
| WFI | FreeRTOS tickless idle（`CONFIG_FREERTOS_USE_TICKLESS_IDLE`） | 全部 | 任何中斷 | 原地繼續 |
| PDS（Level 31） | `hal_lp_enter()`，或低階的 `pm_pds_mode_enter(PM_PDS_LEVEL_31, …)` | OCRAM（見[保留與喚醒](#retention-wake)）、HBN RAM；可選擇讓 PSRAM 自刷新 | RTC 計時、GPIO、類比比較器（ACOMP）、BLE | 原地繼續；CPU、RF 與 MISC 電源域被重置，主控台 UART 與系統計時器要重新初始化 |
| HBN（Level 0） | `hal_lp_enter_fastboot()`，或低階的 `pm_hbn_mode_enter(PM_HBN_LEVEL_0, …)` | 只有 HBN RAM（4 KB）與 RTC | RTC 計時、AON 腳位、BOR、ACOMP | 從韌體開頭冷開機；以 `hal_lp_is_fastboot_wakeup()` 判斷 |

## 架構 { #architecture }

| 層 | 位置 | 內容 |
|---|---|---|
| 應用 | 自己的程式 | 決定何時睡眠、要保留什麼、由什麼喚醒 |
| 自動模式選擇 | `components/sys/ipro_pm/`（原始碼） | 掛在 FreeRTOS tickless idle 上，依每段閒置時間與應用設定的限制選 WFI 或 PDS |
| 低功耗框架 | `bsp/hal/lp_framework/ipro7/`：`hal_lp.h`、`lp_uart.h`、`lib/liblp_framework.a`（預編譯，IPRO7 建置一律連結） | RTC 與 GPIO 喚醒、CPU 狀態儲存與還原、flash XIP 與 PSRAM 復原、虛擬時間、RC32K 校正、喚醒 hook |
| 低階電源管理 | `bsp/hal/inc/hal_pm.h` | `pm_pds_mode_enter()`、`pm_hbn_mode_enter()`、`pm_pds_gpio_wakeup_set()`、`pm_pds_set_misc_keep()`、32 kHz 時脈來源選擇 |

## 設定 { #configuration }

```ini title="apps/test/ipro_lp_test/.config（節錄）"
# CONFIG_USE_PSRAM is not set
CONFIG_HAL_LP=y
CONFIG_FREERTOS_IDLE_HOOK=y
CONFIG_PLATFORM_UART_BAUDRATE=115200
```

| 設定 | 說明 |
|---|---|
| `CONFIG_HAL_LP` | 經 `hal_lp` 進入 PDS 的應用設定這一項（`ipro_lp_test`） |
| `CONFIG_FREERTOS_IDLE_HOOK` | 啟用 `vApplicationIdleHook()`，應用可在其中於閒置時進入 PDS |
| `CONFIG_FREERTOS_USE_TICKLESS_IDLE` | FreeRTOS tickless idle；閒置時 CPU 進入 WFI |
| `CONFIG_IPRO_PM` | 啟用 `ipro_pm`；另需 `CONFIG_FREERTOS_USE_TICKLESS_IDLE=1` 與 `CONFIG_FREERTOS_IDLE_HOOK=y`，否則建置以 `#error` 停止 |
| `CONFIG_IPRO_PM_MAX_MODE` | 開機時允許的最深模式：0 active、1 WFI（預設）、2 native、3 PDS；執行中以 `ipro_pm_policy_set()` 調整 |
| `CONFIG_IPRO_PM_IDLE_PDS` | 由 idle 任務自行進入 PDS（BLE 控制器執行時不會）；同時設定 `CONFIG_IPRO_PM_TIMEBASE=y` |
| `CONFIG_IPRO_PM_SHELL` | `pm` shell 指令（狀態、策略、`pm stats`） |

`.config` 會原樣轉成 `autoconf.h`，Kconfig 的相依關係不會套用，相關設定都要寫出來。

!!! warning "不能與 HOTCODE 選項並用"
    `CONFIG_IPRO7_BLE_HOTCODE` 與 `CONFIG_IPRO7_WIFI_HOST_HOTCODE` 不能與低功耗記憶體佈局（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`、`CONFIG_OCRAM_NORET_SPLIT`）並用，產生 linker script 時會報錯停止。在 Reef 上，`ipro7ai_reef_demo/defconfig_wifi_ipro6s` 使用 Wi-Fi 的選項，`ipro_throughput_test/defconfig_reef` 使用 BLE 的選項。

## 測試應用 ipro_lp_test { #lp-test }

`apps/test/ipro_lp_test` 是不含 BLE 與 PSRAM 的最小應用，以 RTC 喚醒測試 PDS Level 31，設定對象是 IPRO7 EVB（`CONFIG_EVB=y`）。它的 `lp` shell 指令涵蓋本頁的各種情況：`lp sleep <ms>`（經 `hal_lp` 進入 PDS）、`lp auto on|off`（閒置時進入 PDS）、`lp status`、`lp mem [ms]`（哪些 OCRAM 保留下來）、`lp misc on|off`（MISC 電源域保持供電）、`lp fastboot <ms>`（HBN 冷開機喚醒）與 `lp wakectx`。可對照本頁閱讀它的 `src/lp_test_cli.c`。

## 程式介面 { #api }

以下流程依 `apps/platform/ipro7_demo/demo/soc/peripheral/lowpower_demo.c`：初始化框架、註冊喚醒 hook，再以 RTC 計時進入 PDS。

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
    /* 其他周邊（I2C、SPI…）在這裡重新初始化 */
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
        .psram_retention  = 1,     /* 有 PSRAM 時讓它自刷新 */
        .ocram_retention  = 1,
    };
    hal_lp_result_t res;
    int ret = hal_lp_enter(&cfg, &res);   /* 回傳喚醒原因（HAL_LP_WAKEUP_*）或負的錯誤碼 */
    if (ret == HAL_LP_ERR_ENTRY_ABORTED) {
        /* 有中斷待處理，晶片沒有進入 PDS（等同一次 WFI） */
    }
    return ret;
}
```

- `hal_lp_result_t` 回報喚醒原因、觸發喚醒的 GPIO 與實際睡眠時間；`hal_lp_get_virtual_ms()` 提供跨越睡眠持續計數的時基。
- GPIO 喚醒：在 `hal_lp_cfg_t` 設定 `gpio_wakeup_en` 與 `gpio_cfg`（`wakeup_mask`、觸發方式、上下拉）；可用 GPIO0–31。
- 睡眠後 FreeRTOS 的 tick 計數不會自動補正：像 `ipro_lp_test` 一樣以 `xTaskCatchUpTicks()` 補上實際睡眠時間。
- HBN：呼叫 `hal_lp_enter_fastboot()` 後晶片以冷開機喚醒，這個呼叫不會返回。開機時以 `hal_lp_is_fastboot_wakeup()` 判斷，並以 `hal_lp_get_wake_context()` 讀取喚醒內容；要跨越 HBN 保留的資料必須先放進 HBN RAM。

## 保留與喚醒 { #retention-wake }

- **OCRAM**：MISC 電源域斷電時（預設），PDS31 只保留 OCRAM 的前 64 KB；`pm_pds_set_misc_keep()` 讓 MISC 電源域保持供電，就會保留整個 OCRAM。喚醒後要用的資料請放在前 64 KB，或讓 MISC 保持供電，並以 `ipro_lp_test` 的 `lp mem` 確認結果。
- **PSRAM**：`psram_retention` 讓 PSRAM 在 PDS 期間自刷新，喚醒時由框架恢復。IPRO7AI（Reef 的 SoC）的 PSRAM 在封裝內，PDS 期間必須保持自刷新。
- **HBN RAM**：4 KB，HBN 期間唯一保留的記憶體；框架的參數與 fastboot 喚醒內容也放在這裡。
- **主控台**：UART0 所在的電源域在 PDS31 時會被重置，喚醒後要重新初始化（`shell_uart_reinit()` 或 `platform_init()`）。主控台 RX 腳位（GPIO21，Reef 上是 U6 第 4 腳）無法喚醒 PDS，睡眠期間輸入的字元會遺失。
- **GPIO 喚醒**：`hal_lp` 支援 GPIO0–31。低階的 `pm_pds_gpio_wakeup_set()`（`hal_pm.h`）可設 GPIO0–41，但每四支腳位共用觸發設定，且只有 ASYNC 觸發有效（SYNC 需要 PDS 期間停止的時脈）。HBN 只能由 AON 腳位喚醒。
- **32 kHz 時脈**：預設 RC32K；板子有 32 kHz 晶振時可用 `pm_pds_set_32k_src()` 切換。Reef 沒有 32 kHz 晶振，使用 RC32K；框架附有 RC32K 校正。
- **Flash**：`flash_power_down = 1` 時睡眠期間 flash 斷電，喚醒時由框架恢復 XIP。

## BLE 與睡眠 { #ble-sleep }

- `ipro_pm` 的 BLE 後端與 BLE 連線中的 PDS（`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`）會強制從原始碼建置 BLE 控制器。控制器只以預編譯函式庫提供，因此無法以本套件建置。產品若需要在 BLE 連線中省電，請洽 INTELPRO。
- `ipro_ble_remote/defconfig_reef` 刻意不使用 PDS：Reef 由 USB 供電，相機與音訊也需要時脈。
- `ipro_pdm_mic_demo`（IPRO7 EVB、IPRO7AI EVK）示範 BLE 搭配 tickless WFI，以及手動進入 PDS 的 `pds [sec]` 指令。
- BLE 控制器組合、Exchange Memory 大小等設定見 [BLE 開發](ble.md)。

## 量測 { #measure }

- 以外接電表量測 SoC 的供電路徑。在 Reef 上，SW8 與 JP2 會讓 IPRO7AI 的 3.3 V 經過電表（步驟見下節）；其他板子見[電源與功耗量測](../hardware/power.md)。
- 確認晶片實際睡眠的次數與時間，並記錄喚醒原因（`hal_lp_result_t`）。喚醒次數比預期多時，先檢查計時器與待處理的中斷（`hal_lp_enter()` 會回傳 `HAL_LP_ERR_ENTRY_ABORTED`）。
- 使用 `ipro_pm` 時，`pm stats` 列出各模式的停留時間與估算電流。估算值只用來比較不同設定，不能取代實際量測。
- 以同一份韌體比較 WFI 與 PDS，並在睡眠前等 UART 輸出送完，以免被截斷。

## 在 Reef 上動手做 { #hands-on }

量測韌體執行時 IPRO7AI 消耗的電流。隨附的 Reef 設定檔都不會進入 PDS，所以這裡以出廠韌體比較「shell 閒置」與「相機管線運作」兩種狀態；換成自己的應用重做一次，就能在加入睡眠前得到它的基準值。

需要：一台電流表（或電源量測單元），以及接 3 腳 JP2 排針的測試線。

<div class="ipro-steps" markdown>

1. **設定**

    不需要增加設定。`apps/platform/ipro7ai_reef_demo/.config` 沒有任何低功耗設定（沒有 `CONFIG_HAL_LP`、`CONFIG_IPRO_PM`），CPU 只會閒置。

2. **建置與燒錄**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    進入下載模式（按住 SW1、按一下 SW2、放開 SW1）後，在 IntelProCube 目錄執行：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    細節見[燒錄與序列埠](../get-started/flash-and-monitor.md)。

3. **把電表串進電源**

    拔掉 USB-C。電流表接在 JP2 第 1 腳（3V3）與第 2 腳（SOC）之間，SW8 撥到 **MEAS**，再插回 USB-C。讀值只包含 IPRO7AI 的 3.3 V 腳位，不含相機、LED、功率放大器與 microSD 插槽。

4. **讀取閒置電流**

    以 115200 baud 開啟主控台。開機時範例會先讓相機停駐；出現 `ipro />` 提示字元後，記下電表讀值。

5. **啟動相機管線並比較**

    ```text
    cam start
    cam stop
    cam park
    ```

    主控台依序回應 ``streaming - `cam status` in a second``、`stopped`、`PWDN high, RESETB low, XCLK off`。分別記下串流進行中與 `cam park` 之後的讀值：兩者的差就是相機管線（XCLK、DVP 輸入、ISP）在 SoC 上的耗電。

6. **還原板子**

    拔掉 USB-C，把 SW8 撥回 **PWR**，最後才拆下電表。SW8 在 MEAS 而 JP2 沒接任何東西時，IPRO7AI 沒有供電，周邊的 3.3 V 卻會經由 I/O 腳位反灌。

</div>

下一步：依[建立第一個自己的應用](../tutorials/first-own-app.md)開始動手，再依[測試你的應用](../tutorials/testing.md)檢查它的行為與電流。

## 本版限制 { #limitations }

- 隨附的 IPRO7AI Reef EVK 設定檔都不會進入 PDS 或 HBN；`ipro_lp_test` 與 `ipro7_demo` 的低功耗指令以 IPRO7 EVB 為對象。
- BLE 連線中的 PDS 無法以本套件建置（需要從原始碼建置控制器）。
- Zephyr RTOS 下沒有低功耗模式（`pm_state` 不會進入 PDS 或 HBN），見 [Zephyr RTOS](zephyr.md)。
- `CONFIG_IPRO_PM_IDLE_PDS`（由 idle 任務進入 PDS）沒有隨附範例，使用前請在自己的板子上驗證。
- 低功耗記憶體佈局不能與 HOTCODE 選項並用。

## 相關文件 { #related }

- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：SW8、JP2 與電流量測步驟。
- [電源與功耗量測](../hardware/power.md)
- [BLE 開發](ble.md)
- [建置系統與設定](build-system.md)
- [Zephyr RTOS](zephyr.md)
