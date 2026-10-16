---
title: 平台與系統
description: FreeRTOS 啟動與掛鉤、HAL 共用定義、系統控制、時脈、計時器、看門狗、RTC 與記憶體配置輔助。
generated: tools/gen_api.py
migrate_from: []
---

# 平台與系統

FreeRTOS 啟動與掛鉤、HAL 共用定義、系統控制、時脈、計時器、看門狗、RTC 與記憶體配置輔助。說明取自標頭檔註解（英文）。

| 標頭 | 函式 | 說明 |
|---|---|---|
| [`freertos_app_hooks.h`](#freertos_app_hooks-h) | 3 | FreeRTOS application support: platform start-up, heap set-up and stack report. |
| [`hal_common.h`](#hal_common-h) | 13 | Definitions shared by the HAL drivers, global interrupt control, chip resets and memory-address helpers. |
| [`hal_sys.h`](#hal_sys-h) | 18 | System control: reset reason, reboot and reset, oscillator calibration, peripheral clock gating. |
| [`hal_clock.h`](#hal_clock-h) | 3 | Clock-source identifiers for board configuration, board clock initialization and (IPRO6) 32 kHz clock selection. |
| [`hal_mtimer.h`](#hal_mtimer-h) | 5 | Machine-timer time stamps and busy-wait delays. |
| [`hal_timer.h`](#hal_timer-h) | 6 | General-purpose timer driver: counter channels with three compare match interrupts each. |
| [`hal_rtc.h`](#hal_rtc-h) | 3 | Always-on RTC: counter reset with compare alarm, and a simple time stamp in seconds. |
| [`hal_wdt.h`](#hal_wdt-h) | 7 | Watchdog timer (WDT) of the timer block: chip reset or interrupt on timeout. |
| [`hal_aon_wdt.h`](#hal_aon_wdt-h) | 5 | Always-on (AON) watchdog timer: chip reset on timeout, also in the PDS and HBN sleep modes. |
| [`hal_cache_alloc.h`](#hal_cache_alloc-h) | 2 | Cache-line aligned heap allocation for DMA and hardware-accelerator buffers (FreeRTOS builds). |
| [`hal_hbnram_mgnt.h`](#hal_hbnram_mgnt-h) | 0 | HBN RAM layout: the 4 KB always-on RAM shared by boot, firmware and the low-power framework. |

## freertos_app_hooks.h { #freertos_app_hooks-h }

`#include "freertos_app_hooks.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/os/freertos/freertos_app_hooks.h)）

FreeRTOS application support: platform start-up, heap set-up and stack report.

The matching source file also provides weak default FreeRTOS hooks (stack overflow, malloc failed, idle, static idle and timer task memory, assert). An application replaces any of them by defining its own version.

Typical `main()`:

```c
int main(void)
{
    ipro_platform_init();
    xTaskCreate(app_task, "app", 1024, NULL, 5, NULL);
    vTaskStartScheduler();
    return 0;
}
```

### ipro_setup_heap { #ipro_setup_heap }

```c
void ipro_setup_heap(void);
```

Hand the linker-defined heap regions to the FreeRTOS heap.

Builds the region list for `vPortDefineHeapRegions()` from linker symbols: the main heap (in PSRAM for flash builds with PSRAM enabled, otherwise in on-chip RAM) and, when the memory layout provides one, the non-retention on-chip RAM heap. Empty regions are skipped, the regions are sorted by address and the size of each is printed.

!!! note "注意"
    Call it once, before the first heap allocation. [`ipro_platform_init()`](#ipro_platform_init) already calls it; call it directly only when not using [`ipro_platform_init()`](#ipro_platform_init).

### ipro_platform_init { #ipro_platform_init }

```c
void ipro_platform_init(void);
```

Run the standard platform start-up sequence before the scheduler starts.

In order: system and debug-UART initialization (`platform_init()`), [`ipro_setup_heap()`](#ipro_setup_heap), `hal_boot2_init()`, a PSRAM check (flash builds with PSRAM print a warning if PSRAM failed to initialize), `ipro_log_init()` when `CONFIG_IPRO_LOG_ENABLE` is set, the shell on UART0 with its own task when `CONFIG_SHELL` is set, and `ipro_pm_init()` when `CONFIG_IPRO_PM` is set.

After it returns, create the application tasks and call `vTaskStartScheduler()`.

!!! note "注意"
    Call it once. It already starts the shell; do not initialize the shell again.

### ipro_dump_task_stacks { #ipro_dump_task_stacks }

```c
void ipro_dump_task_stacks(const char *where);
```

Print the free heap size and every task's stack high-water mark.

For each task (up to 20) it prints the smallest free stack space ever seen, in bytes. A small value means the task came close to overflowing and its stack must not shrink; a large value means the stack is over-provisioned and can be reduced. It uses a static buffer and `uxTaskGetSystemState()` rather than the heap, so the default malloc-failed and stack-overflow hooks can call it.

| 參數 | 說明 |
|---|---|
| `where` | Label printed in the header line; may be NULL. |

!!! note "注意"
    Not reentrant. Prints nothing unless `configUSE_TRACE_FACILITY` is 1 (the SDK default).

## hal_common.h { #hal_common-h }

`#include "hal_common.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_common.h)）

Definitions shared by the HAL drivers, global interrupt control, chip resets and memory-address helpers.

### cpu_global_irq_enable { #cpu_global_irq_enable }

```c
void cpu_global_irq_enable(void);
```

Enable interrupts globally on the CPU.

Not nestable: interrupts are enabled even if they were disabled by an outer section. Use `__irq_save()` / `__irq_restore()` for nested critical sections.

### cpu_global_irq_disable { #cpu_global_irq_disable }

```c
void cpu_global_irq_disable(void);
```

Disable interrupts globally on the CPU (see [`cpu_global_irq_enable()`](#cpu_global_irq_enable)).

### hal_por_reset { #hal_por_reset }

```c
void hal_por_reset(void);
```

Trigger a software power-on reset of the whole chip.

### hal_system_reset { #hal_system_reset }

```c
void hal_system_reset(void);
```

Trigger a software system reset.

### hal_cpu_reset { #hal_cpu_reset }

```c
void hal_cpu_reset(void);
```

Trigger a software reset of the CPU only.

### hal_reboot_config { #hal_reboot_config }

```c
void hal_reboot_config(hal_reboot_cfg_t rbot);
```

Select the boot mode for the next reboot.

| 參數 | 說明 |
|---|---|
| `rbot` | Boot mode. |

!!! note "注意"
    Not implemented: the setting is ignored. Use [`hal_reboot()`](#hal_reboot), [`hal_reboot_download()`](#hal_reboot_download) or [`hal_reboot_media()`](#hal_reboot_media) ([`hal_sys.h`](#hal_sys-h)) instead.

### hal_get_chip_id { #hal_get_chip_id }

```c
void hal_get_chip_id(uint8_t chip_id[8]);
```

Read the 8-byte chip ID (factory MAC address field) from efuse.

| 參數 | 說明 |
|---|---|
| `chip_id` | Buffer of 8 bytes that receives the ID. |

### hal_enter_usb_iap { #hal_enter_usb_iap }

```c
void hal_enter_usb_iap(void);
```

Reboot into the boot loader's USB download (IAP) mode.

Does not return.

Sets a request flag in the always-on domain, waits 1 s and performs a power-on reset.

### hal_jump2app { #hal_jump2app }

```c
void hal_jump2app(uint32_t flash_offset);
```

Start a firmware image at another flash offset.

Does not return.

Maps the XIP window to `flash_offset` and jumps to its start.

| 參數 | 說明 |
|---|---|
| `flash_offset` | Flash offset of the image; must be in the range 0xC000 to 0x3FAFFF. Any other value makes the function loop forever. |

!!! note "注意"
    Interrupts and peripherals are left as they are; disable them before the jump.

### hal_get_trng_seed { #hal_get_trng_seed }

```c
int hal_get_trng_seed(void);
```

Get a 32-bit random seed from the hardware random number generator.

**回傳值**：Random value.

!!! note "注意"
    Gates the security-engine clock again before returning; do not call it while the security engine is in use.

### hal_system_init { #hal_system_init }

```c
void hal_system_init(void);
```

Run the board initialization (board_init()).

Called by the platform start-up code.

### hal_is_cacheable_addr { #hal_is_cacheable_addr }

```c
int hal_is_cacheable_addr(const void *addr);
```

Check whether an address is in the cacheable memory view.

| 參數 | 說明 |
|---|---|
| `addr` | Address to check. |

**回傳值**：1 for addresses in the 0x1xxxxxxx cacheable view, 0 otherwise.

### hal_get_noncacheable_addr { #hal_get_noncacheable_addr }

```c
void * hal_get_noncacheable_addr(const void *addr);
```

Get the non-cacheable alias of an address.

Memory in the cacheable 0x1xxxxxxx view is also visible, without the data cache, at the same offset in the 0x2xxxxxxx view.

| 參數 | 說明 |
|---|---|
| `addr` | Address to convert. |

**回傳值**：The 0x2xxxxxxx alias of a cacheable address, or `addr` unchanged if it is not cacheable.

### hal_reboot_cfg_t { #hal_reboot_cfg_t }

Boot mode after a reboot.

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_REBOOT_AS_BOOTPIN` |  | As selected by the boot pins. |
| `HAL_REBOOT_FROM_INTERFACE` |  | From an interface: download mode. |
| `HAL_REBOOT_FROM_MEDIA` |  | From flash (media): run the firmware. |
| `HAL_REBOOT_MAX` |  | Number of modes (not a valid mode). |

### 巨集 { #hal_common-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `COMMON_CAPS_INT_TX` | `(1 << 0)` | Interrupt-driven transmit. |
| `COMMON_CAPS_INT_RX` | `(1 << 1)` | Interrupt-driven receive. |
| `COMMON_CAPS_DMA_TX` | `(1 << 2)` | DMA transmit. |
| `COMMON_CAPS_DMA_RX` | `(1 << 3)` | DMA receive. |
| `COMMON_AlignCeil(x, N)` | `( ((x) + ((N) - 1)) / (N) * (N) )` | Round `x` up to the next multiple of `N`. Arguments are evaluated more than once. |

## hal_sys.h { #hal_sys-h }

`#include "hal_sys.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sys.h)）

System control: reset reason, reboot and reset, oscillator calibration, peripheral clock gating.

The reset reason is determined once during start-up ([`hal_rst_reason_detect()`](#hal_rst_reason_detect)) and can then be read with [`hal_rst_reason_get()`](#hal_rst_reason_get). It is kept in HBN RAM (see [`hal_hbnram_mgnt.h`](#hal_hbnram_mgnt-h)).

### hal_rst_reason_str { #hal_rst_reason_str }

```c
const char * hal_rst_reason_str(hal_rst_reason_t reason);
```

Get a printable name of a reset reason.

| 參數 | 說明 |
|---|---|
| `reason` | Reset reason. |

**回傳值**：Constant string such as `"Power-On"`, or `"Invalid"` for a value outside [`hal_rst_reason_t`](#hal_rst_reason_t).

### hal_rst_reason_get { #hal_rst_reason_get }

```c
hal_rst_reason_t hal_rst_reason_get(void);
```

Get the reset reason detected during start-up.

**回傳值**：The value determined by [`hal_rst_reason_detect()`](#hal_rst_reason_detect), or [`HAL_RST_REASON_UNKNOWN`](#hal_rst_reason_t) if detection has not run.

### hal_rst_reason_set { #hal_rst_reason_set }

```c
void hal_rst_reason_set(hal_rst_reason_t reason);
```

Store the reason for an upcoming reset.

The value is kept in HBN RAM and reported by [`hal_rst_reason_detect()`](#hal_rst_reason_detect) at the next boot (unless a hardware reason such as a watchdog reset takes precedence). [`hal_reboot()`](#hal_reboot) and the exception handler call it themselves.

| 參數 | 說明 |
|---|---|
| `reason` | Reason to report after the reset. |

### hal_rst_reason_detect { #hal_rst_reason_detect }

```c
hal_rst_reason_t hal_rst_reason_detect(void);
```

Determine the reset reason (start-up code only).

Evaluates the sources listed at [`hal_rst_reason_t`](#hal_rst_reason_t), initializes the HBN RAM system information after a power-on reset, clears the hardware status it used and the stored reason, and caches the result for [`hal_rst_reason_get()`](#hal_rst_reason_get).

**回傳值**：Detected reset reason.

!!! note "注意"
    Called once by the system start-up code. Calling it again clears the status it relies on and gives a different result.

### hal_reboot { #hal_reboot }

```c
void hal_reboot(void);
```

Reboot the chip with a power-on reset.

Does not return.

Records [`HAL_RST_REASON_SOFTWARE`](#hal_rst_reason_t) as reset reason and boots as selected by the boot pins.

### hal_reboot_download { #hal_reboot_download }

```c
void hal_reboot_download(void);
```

Reboot into download (firmware update over interface) mode, regardless of the boot pins.

Does not return.

### hal_reboot_media { #hal_reboot_media }

```c
void hal_reboot_media(void);
```

Reboot and boot the firmware from flash (media boot), regardless of the boot pins.

Does not return.

### hal_sys_reset { #hal_sys_reset }

```c
void hal_sys_reset(void);
```

Reset the system (without a power-on reset).

Does not return.

No reset reason is recorded; the next boot reports [`HAL_RST_REASON_SOFTWARE`](#hal_rst_reason_t) unless one was set with [`hal_rst_reason_set()`](#hal_rst_reason_set).

### hal_poweroff { #hal_poweroff }

```c
void hal_poweroff(void);
```

Power off the chip.

!!! note "注意"
    Not implemented: the function returns without doing anything.

### hal_rc32k_cal { #hal_rc32k_cal }

```c
int hal_rc32k_cal(void);
```

Apply the factory RC32K oscillator trim from efuse.

Called during start-up by [`hal_boot2_init()`](memory-boot.md#hal_boot2_init). Does not measure the oscillator; use [`hal_rc32k_force_cal()`](#hal_rc32k_force_cal) for a run-time calibration.

**回傳值**：The applied capacitor trim value (0 or greater), or -1 if no valid trim is burned in efuse (the oscillator keeps its reset settings). Always -1 on IPRO6.

### hal_rc32k_force_cal { #hal_rc32k_force_cal }

```c
int hal_rc32k_force_cal(void);
```

Calibrate the RC32K oscillator at run time (IPRO7).

Measures the oscillator against the high-frequency crystal (through the machine timer) and searches the capacitor and frequency trim for the smallest error, regardless of the efuse trim. The 32 kHz source selected on entry is restored. The result is logged.

**回傳值**：The selected capacitor trim value. Always -1 on IPRO6.

!!! note "注意"
    Blocks for a few seconds; call from task context. The 32.768 kHz crystal, if fitted, is briefly powered as a reference.

### hal_rc32k_sw_cal { #hal_rc32k_sw_cal }

```c
int hal_rc32k_sw_cal(void);
```

Calibrate the RC32K capacitor trim without a 32.768 kHz crystal (IPRO7).

Tries all 16 capacitor trim values, measures each against the machine timer for 150 ms and keeps the value with the smallest error. The 32 kHz source selected on entry is restored.

**回傳值**：The selected capacitor trim value (0 to 15). Always -1 on IPRO6.

!!! note "注意"
    Blocks for about 2.4 s; call from task context.

### hal_rc32k_measure_error_ppm { #hal_rc32k_measure_error_ppm }

```c
int hal_rc32k_measure_error_ppm(uint32_t window_us);
```

Measure the frequency error of the current 32 kHz clock (IPRO7).

Compares the RTC counter with the machine timer (derived from the high-frequency crystal) over `window_us`. The 32 kHz source is not changed, so select the RC32K oscillator first to measure it.

| 參數 | 說明 |
|---|---|
| `window_us` | Measurement window in microseconds; values below 10000 are raised to 10000. One RTC tick over the window limits the resolution (about 30 ppm at 1 s). |

**回傳值**：Signed error in ppm relative to 32768 Hz (positive = fast), or `INT32_MAX` if the measurement failed. Always `INT32_MAX` on IPRO6.

!!! note "注意"
    Blocks for `window_us`; interrupts are disabled only briefly while the counters are sampled.

### hal_rc32k_measure_cdet_ppm { #hal_rc32k_measure_cdet_ppm }

```c
int hal_rc32k_measure_cdet_ppm(uint32_t *out_t_count, uint32_t *out_g_count);
```

Measure the RC32K frequency error with the clock-detection counter (IPRO7).

Counts high-frequency crystal cycles over 32 RC32K cycles in hardware.

| 參數 | 說明 |
|---|---|
| `out_t_count` | Receives the raw RC32K (test clock) count; may be NULL. |
| `out_g_count` | Receives the raw reference clock count; may be NULL. |

**回傳值**：Signed error in ppm relative to 32768 Hz, or `INT32_MAX` if the counter did not complete or returned no reference count.

!!! note "注意"
    Only reliable before [`hal_rc32m_cal()`](#hal_rc32m_cal) has run (it runs in [`hal_boot2_init()`](memory-boot.md#hal_boot2_init)); afterwards the counter does not return valid counts. Use [`hal_rc32k_measure_error_ppm()`](#hal_rc32k_measure_error_ppm) at run time. Not available on IPRO6.

### hal_rc32m_cal { #hal_rc32m_cal }

```c
int hal_rc32m_cal(void);
```

Trim the RC32M oscillator (IPRO7).

Applies the efuse trim if a valid one is burned, otherwise runs the hardware calibration. Called during start-up by [`hal_boot2_init()`](memory-boot.md#hal_boot2_init).

**回傳值**：The applied trim code. Always -1 on IPRO6.

### hal_clock_enable { #hal_clock_enable }

```c
int hal_clock_enable(hal_module_t module);
```

Enable (ungate) the bus clock of a peripheral module.

| 參數 | 說明 |
|---|---|
| `module` | Module to enable. |

**回傳值**：0 on success, -1 if the module is not available on this chip.

### hal_clock_disable { #hal_clock_disable }

```c
int hal_clock_disable(hal_module_t module);
```

Disable (gate) the bus clock of a peripheral module.

| 參數 | 說明 |
|---|---|
| `module` | Module to disable. |

**回傳值**：0 on success, -1 if the module is not available on this chip.

### hal_module_reset { #hal_module_reset }

```c
int hal_module_reset(hal_module_t module);
```

Reset a peripheral module by software.

| 參數 | 說明 |
|---|---|
| `module` | Module to reset. On IPRO7, [`HAL_MODULE_PKA`](#hal_module_t) resets the whole security engine. |

**回傳值**：0 on success, -1 if the module is not available on this chip.

### hal_rst_reason_t { #hal_rst_reason_t }

System reset reason.

[`hal_rst_reason_detect()`](#hal_rst_reason_detect) checks the sources in this order:

1. AON watchdog reset status (chips with the AON watchdog);
1. HBN RAM magic missing: power-on reset;
1. watchdog reset status;
1. PDS wake-up status;
1. otherwise the reason stored with [`hal_rst_reason_set()`](#hal_rst_reason_set) before the reset, or [`HAL_RST_REASON_SOFTWARE`](#hal_rst_reason_t) if none was stored.

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_RST_REASON_UNKNOWN` | `0` | Unknown, or detection has not run yet. |
| `HAL_RST_REASON_POWER_ON` | `1` | Power-on reset (cold boot). |
| `HAL_RST_REASON_WDT` | `2` | Watchdog timer reset. |
| `HAL_RST_REASON_EXCEPTION` | `3` | Reset after a CPU exception. |
| `HAL_RST_REASON_SOFTWARE` | `4` | Software reset ([`hal_reboot()`](#hal_reboot), [`hal_sys_reset()`](#hal_sys_reset), ...). |
| `HAL_RST_REASON_LP_WAKEUP` | `5` | Wake-up from PDS sleep. |
| `HAL_RST_REASON_AON_WDT` | `6` | AON (always-on) watchdog timeout. |

### 匿名列舉 { #hal_sys-h-enum }

Legacy reset reason codes; use [`hal_rst_reason_t`](#hal_rst_reason_t) instead.

| 名稱 | 值 | 說明 |
|---|---|---|
| `SYSTEM_RST_POR` | `0` | Power-on reset. |
| `SYSTEM_RST_BOR` | `1` | Brown-out reset. |
| `SYSTEM_RST_WDT` | `2` | Watchdog reset. |
| `SYSTEM_RST_HBN` | `3` | Wake-up from hibernate. |
| `SYSTEM_RST_SOFTWARE` | `4` | Software reset. |

### hal_module_t { #hal_module_t }

Peripheral modules for [`hal_clock_enable()`](#hal_clock_enable), [`hal_clock_disable()`](#hal_clock_disable) and [`hal_module_reset()`](#hal_module_reset).

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_MODULE_SEC_ENG` | `0` | Security engine (AES, SHA, TRNG, PKA). |
| `HAL_MODULE_USB` |  | USB controller. |
| `HAL_MODULE_EMAC` |  | Ethernet MAC. |
| `HAL_MODULE_PKA` |  | Public-key accelerator. On IPRO7 its reset is the security-engine reset; not available on IPRO6. |
| `HAL_MODULE_MAX` |  | Number of modules (not a valid module). |

## hal_clock.h { #hal_clock-h }

`#include "hal_clock.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_clock.h)）

Clock-source identifiers for board configuration, board clock initialization and (IPRO6) 32 kHz clock selection.

The identifiers are the values that the board configuration header (board_config.h) assigns to its clock-source settings, for example `XTAL_TYPE` and the `BSP_*_CLOCK_SOURCE` macros. The initialization functions are implemented by the board support package and are called during start-up (board_init()).

### system_clock_init { #system_clock_init }

```c
void system_clock_init(void);
```

Set up the system clocks from the board configuration.

Configures the system (CPU and bus) clock, the machine-timer clock, the 32 kHz clock and the XCLK source as defined by the board configuration. Called by board_init() during start-up.

### peripheral_clock_init { #peripheral_clock_init }

```c
void peripheral_clock_init(void);
```

Set up peripheral clock gating and peripheral clock sources from the board configuration.

Called by board_init() during start-up.

### system_mtimer_clock_init { #system_mtimer_clock_init }

```c
void system_mtimer_clock_init(void);
```

Reset the machine timer and clock it from XCLK.

!!! warning "警告"
    Clears the machine-timer counter used by [`mtimer_get_time_us()`](#mtimer_get_time_us), the delay functions and the RTOS tick. Only for start-up and low-level restore code.

### 巨集 { #hal_clock-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `XTAL_NONE` | `0` | No main crystal. |
| `EXTERNAL_XTAL_32M` | `1` | External 32 MHz crystal. |
| `INTERNAL_RC_32M` | `2` | Internal 32 MHz RC oscillator. |
| `EXTERNAL_XTAL_32K` | `0` | External 32.768 kHz crystal. |
| `INTERNAL_RC_32K` | `1` | Internal RC32K oscillator. |
| `ROOT_CLOCK_SOURCE_XCLK` | `1` | Crystal/XCLK clock; its value depends on whether the board uses an external 32 MHz crystal (`XTAL_TYPE`). |
| `ROOT_CLOCK_SOURCE_PLL_57P6M` | `2` | PLL output, 57.6 MHz. |
| `ROOT_CLOCK_SOURCE_PLL_96M` | `3` | PLL output, 96 MHz. |
| `ROOT_CLOCK_SOURCE_PLL_144M` | `4` | PLL output, 144 MHz. |
| `ROOT_CLOCK_SOURCE_32K_CLK` | `5` | 32 kHz clock. |
| `ROOT_CLOCK_SOURCE_FCLK` | `6` | FCLK (fast clock, the CPU clock). |
| `ROOT_CLOCK_SOURCE_BCLK` | `7` | BCLK (bus clock). |
| `ROOT_CLOCK_SOURCE_1K_CLK` | `8` | 1 kHz clock. |
| `ROOT_CLOCK_SOURCE_AUPLL_12288000_HZ` | `9` | Audio PLL, 12.288 MHz. |
| `ROOT_CLOCK_SOURCE_AUPLL_11289600_HZ` | `10` | Audio PLL, 11.2896 MHz. |
| `ROOT_CLOCK_SOURCE_AUPLL_5644800_HZ` | `11` | Audio PLL, 5.6448 MHz. |
| `ROOT_CLOCK_SOURCE_AUPLL_24576000_HZ` | `12` | Audio PLL, 24.576 MHz. |
| `ROOT_CLOCK_SOURCE_AUPLL_24000000_HZ` | `13` | Audio PLL, 24 MHz. |

## hal_mtimer.h { #hal_mtimer-h }

`#include "hal_mtimer.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_mtimer.h)）

Machine-timer time stamps and busy-wait delays.

The RISC-V machine timer is a free-running 64-bit counter that also drives the RTOS tick. The functions run from TCM, so they can be used in low-power wake-up code before XIP flash is restored.

### mtimer_get_time_ms { #mtimer_get_time_ms }

```c
uint64_t mtimer_get_time_ms();
```

Get the machine-timer time in units of about 1 ms.

**回傳值**：Time stamp in units of 1.024 ms (microseconds divided by 1024, to avoid a 64-bit division), so the value runs about 2.3 % slower than real milliseconds. Use [`mtimer_get_time_us()`](#mtimer_get_time_us) / 1000 when exact milliseconds are needed.

### mtimer_get_time_us { #mtimer_get_time_us }

```c
uint64_t mtimer_get_time_us();
```

Get the machine-timer time in microseconds.

**回傳值**：Microseconds counted by the machine timer since reset or the last [`mtimer_clear_time()`](#mtimer_clear_time).

### mtimer_delay_ms { #mtimer_delay_ms }

```c
void mtimer_delay_ms(uint32_t time);
```

Busy-wait for a number of milliseconds.

Does not yield to the scheduler; use the RTOS delay functions in tasks.

| 參數 | 說明 |
|---|---|
| `time` | Delay in milliseconds. |

### mtimer_delay_us { #mtimer_delay_us }

```c
void mtimer_delay_us(uint32_t time);
```

Busy-wait for a number of microseconds.

| 參數 | 說明 |
|---|---|
| `time` | Delay in microseconds. |

### mtimer_clear_time { #mtimer_clear_time }

```c
void mtimer_clear_time();
```

Reset the machine-timer counter to 0.

!!! warning "警告"
    The counter is shared with the RTOS tick and the delay functions; do not call this while the scheduler is running.

## hal_timer.h { #hal_timer-h }

`#include "hal_timer.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_timer.h)）

General-purpose timer driver: counter channels with three compare match interrupts each.

The timer block has two channels. Each channel counts at its channel clock and has three comparators that can raise interrupts and, in preload mode, reload the counter. Typical sequence:

1. Optionally set the clock divider with [`timer_set_div()`](#timer_set_div).
1. Configure the channel with [`timer_init()`](#timer_init); match times are given in microseconds.
1. Register a callback with [`timer_setCallback()`](#timer_setCallback).
1. Start counting with [`timer_start()`](#timer_start).

### timer_init { #timer_init }

```c
int timer_init(int timer_id, int timer_ch, hal_timer_config_t *timerCfg);
```

Configure a timer channel without starting it.

Masks the channel interrupts, stops the channel, sets counting mode, reload comparator and reload value, converts the three match times to counter ticks with the channel clock rate at the time of the call, and programs the comparators selected by `hal_timer_config_t::trigger` (comparator value = ticks + reload - 2, where reload counts only in preload mode). The other comparators are set to 0xFFFFFFFF. The match interrupts of the selected comparators are unmasked and, for `TIMER0_INDEX`, the channel interrupt is enabled in the CPU and its handler installed.

| 參數 | 說明 |
|---|---|
| `timer_id` | Timer block, `TIMER0_INDEX`. |
| `timer_ch` | Channel, [`timer_ch_index_type`](#timer_ch_index_type). |
| `timerCfg` | Channel configuration. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | All three converted comparator values are 0 (for example a free-running channel with all times 0). Counting mode and reload settings are applied anyway, so [`timer_start()`](#timer_start) still runs the counter, but no comparator is set up. |

### timer_set_div { #timer_set_div }

```c
void timer_set_div(int timer_id, int timer_ch, uint8_t div);
```

Set the clock divider of a channel.

The counter clock becomes the channel source clock divided by (`div` + 1). Call it before [`timer_init()`](#timer_init), which converts the match times with the clock rate in effect at that moment.

| 參數 | 說明 |
|---|---|
| `timer_id` | Timer block, `TIMER0_INDEX`. |
| `timer_ch` | Channel, [`timer_ch_index_type`](#timer_ch_index_type). |
| `div` | Divider value; the clock is divided by `div` + 1. |

### timer_setCallback { #timer_setCallback }

```c
void timer_setCallback(int timer_id, int timer_ch, void *fn);
```

Register the match callback of a channel.

| 參數 | 說明 |
|---|---|
| `timer_id` | Timer block, `TIMER0_INDEX`. |
| `timer_ch` | Channel, [`timer_ch_index_type`](#timer_ch_index_type). |
| `fn` | Callback with the signature of `timer_device_t::callback` (runs in interrupt context), or NULL to remove it. |

### timer_get_counter { #timer_get_counter }

```c
uint32_t timer_get_counter(int timer_id, int timer_ch);
```

Read the current counter value of a channel.

| 參數 | 說明 |
|---|---|
| `timer_id` | Timer block, `TIMER0_INDEX`. |
| `timer_ch` | Channel, [`timer_ch_index_type`](#timer_ch_index_type). |

**回傳值**：Counter value in counter clock ticks.

### timer_start { #timer_start }

```c
void timer_start(int timer_id, int timer_ch);
```

Start counting on a channel.

| 參數 | 說明 |
|---|---|
| `timer_id` | Timer block, `TIMER0_INDEX`. |
| `timer_ch` | Channel, [`timer_ch_index_type`](#timer_ch_index_type). |

### timer_stop { #timer_stop }

```c
void timer_stop(int timer_id, int timer_ch);
```

Stop counting on a channel.

| 參數 | 說明 |
|---|---|
| `timer_id` | Timer block, `TIMER0_INDEX`. |
| `timer_ch` | Channel, [`timer_ch_index_type`](#timer_ch_index_type). |

### timer_ch_index_type { #timer_ch_index_type }

Timer channel (the `timer_ch` argument of the timer functions).

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER_CH0_INDEX` |  | Channel 0. |
| `TIMER_CH1_INDEX` |  | Channel 1. |
| `TIMER_CH_MAX_INDEX` |  | Number of channels. |

### timer_index_type { #timer_index_type }

Timer block (the `timer_id` argument of the timer functions).

Use `TIMER0_INDEX`: the SoC has a single timer block, and [`timer_init()`](#timer_init) installs interrupt handlers only for `TIMER0_INDEX`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER0_INDEX` |  | The timer block. |
| `TIMER1_INDEX` |  | Not a separate timer block; no interrupt handlers are installed for it. |
| `TIMER_MAX_INDEX` |  | Number of indexes. |

### timer_preload_trigger_type { #timer_preload_trigger_type }

Comparator that reloads the counter (`hal_timer_config_t::trigger`).

[`timer_init()`](#timer_init) also enables the match interrupts of this comparator and of all lower-numbered comparators.

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER_PRELOAD_TRIGGER_NONE` |  | No reload; [`timer_init()`](#timer_init) enables no match interrupt. |
| `TIMER_PRELOAD_TRIGGER_COMP0` |  | Reload on comparator 0 match; comparator 0 interrupt enabled. |
| `TIMER_PRELOAD_TRIGGER_COMP1` |  | Reload on comparator 1 match; comparator 0 and 1 interrupts enabled. |
| `TIMER_PRELOAD_TRIGGER_COMP2` |  | Reload on comparator 2 match; comparator 0, 1 and 2 interrupts enabled. |

### timer_cnt_mode_type { #timer_cnt_mode_type }

Counting mode (`hal_timer_config_t::cnt_mode`).

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER_CNT_PRELOAD` |  | The counter restarts from `hal_timer_config_t::reload` when the trigger comparator matches. |
| `TIMER_CNT_FREERUN` |  | The counter runs freely and wraps around. |

### timer_compare_id_type { #timer_compare_id_type }

Comparator number.

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER_COMPARE_ID_0` |  | Comparator 0. |
| `TIMER_COMPARE_ID_1` |  | Comparator 1. |
| `TIMER_COMPARE_ID_2` |  | Comparator 2. |

### timer_it_type { #timer_it_type }

Comparator interrupt bit masks (bit n = comparator n).

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER_COMP0_IT` | `1 << 0` | Comparator 0 match. |
| `TIMER_COMP1_IT` | `1 << 1` | Comparator 1 match. |
| `TIMER_COMP2_IT` | `1 << 2` | Comparator 2 match. |

### timer_event_type { #timer_event_type }

Events passed to the timer callback.

| 名稱 | 值 | 說明 |
|---|---|---|
| `TIMER_EVENT_COMP0` |  | Comparator 0 matched. |
| `TIMER_EVENT_COMP1` |  | Comparator 1 matched. |
| `TIMER_EVENT_COMP2` |  | Comparator 2 matched. |
| `TIMER_EVENT_UNKNOWN` |  | Not generated by the driver. |

### timer_device_t { #timer_device_t }

State of one timer channel kept by the driver.

Applications do not access it directly; the `callback` member shows the signature expected by [`timer_setCallback()`](#timer_setCallback).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `id` | `uint8_t` | Timer block index. |
| `ch` | `uint8_t` | Channel index. |
| `cnt_mode` | `enum timer_cnt_mode_type` | Counting mode. |
| `trigger` | `enum timer_preload_trigger_type` | Reload comparator. |
| `reload` | `uint32_t` | Reload value in counter ticks. |
| `timeout1` | `uint32_t` | Comparator 0 time in microseconds. |
| `timeout2` | `uint32_t` | Comparator 1 time in microseconds. |
| `timeout3` | `uint32_t` | Comparator 2 time in microseconds. |
| `callback` | `void(*)(int timer_id, int timer_ch, uint32_t event)` | Match callback, called from the timer interrupt handler with the timer block index as `timer_id` and a [`timer_event_type`](#timer_event_type) value as `event`. The `timer_ch` argument carries the comparator number (0 to 2), not the channel number. |

### hal_timer_config_t { #hal_timer_config_t }

Channel configuration for [`timer_init()`](#timer_init).

Match times are converted to counter ticks with the channel clock: the resolution is 1 us when the clock is a multiple of 1 MHz, and coarser otherwise (the time is truncated to the resolution).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `cnt_mode` | `uint8_t` | Counting mode, [`timer_cnt_mode_type`](#timer_cnt_mode_type). |
| `trigger` | `uint8_t` | Reload comparator, [`timer_preload_trigger_type`](#timer_preload_trigger_type). |
| `reload` | `uint32_t` | Counter value loaded on reload, in counter ticks. Used only in `TIMER_CNT_PRELOAD` mode, where it is also added to each comparator value. |
| `timeout1` | `uint32_t` | Comparator 0 match time in microseconds. |
| `timeout2` | `uint32_t` | Comparator 1 match time in microseconds. |
| `timeout3` | `uint32_t` | Comparator 2 match time in microseconds. |

## hal_rtc.h { #hal_rtc-h }

`#include "hal_rtc.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_rtc.h)）

Always-on RTC: counter reset with compare alarm, and a simple time stamp in seconds.

The RTC counter runs from the 32 kHz clock (32768 ticks per second) in the always-on domain and keeps counting during PDS and HBN sleep. The low-power functions ([`hal_lp.h`](power.md#hal_lp-h), [`hal_pm.h`](power.md#hal_pm-h)) use the same counter.

### rtc_init { #rtc_init }

```c
void rtc_init(uint64_t sleep_time);
```

Restart the RTC counter and arm its compare alarm.

Clears the RTC counter, sets the compare value to `sleep_time` seconds later and enables the counter.

| 參數 | 說明 |
|---|---|
| `sleep_time` | Time until the compare alarm in seconds. |

!!! note "注意"
    Clearing the counter also restarts the time base of [`rtc_get_timestamp()`](#rtc_get_timestamp) and [`hal_lp_get_virtual_us()`](power.md#hal_lp_get_virtual_us).

### rtc_set_timestamp { #rtc_set_timestamp }

```c
void rtc_set_timestamp(uint64_t time_stamp);
```

Set the offset that [`rtc_get_timestamp()`](#rtc_get_timestamp) adds to the RTC time.

| 參數 | 說明 |
|---|---|
| `time_stamp` | Offset in seconds, for example the current time taken right after [`rtc_init()`](#rtc_init). |

### rtc_get_timestamp { #rtc_get_timestamp }

```c
uint64_t rtc_get_timestamp(void);
```

Get the RTC time stamp in seconds.

**回傳值**：The RTC counter in whole seconds plus the offset set with [`rtc_set_timestamp()`](#rtc_set_timestamp). The offset is added as is; it is not adjusted for the counter value at the time it was set.

## hal_wdt.h { #hal_wdt-h }

`#include "hal_wdt.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_wdt.h)）

Watchdog timer (WDT) of the timer block: chip reset or interrupt on timeout.

Start the watchdog with [`wdt_init()`](#wdt_init) and call [`wdt_feed()`](#wdt_feed) more often than the timeout. The timeout is counted in watchdog clock ticks; this driver does not set the watchdog clock source or divider. For a watchdog that keeps running in the low-power modes see [`hal_aon_wdt.h`](#hal_aon_wdt-h).

### wdt_init { #wdt_init }

```c
void wdt_init(int int_mode, uint32_t wdt_timeout);
```

Configure and start the watchdog.

Stops the watchdog; if `wdt_timeout` is non-zero, sets the timeout, selects the timeout action and starts it again.

| 參數 | 說明 |
|---|---|
| `int_mode` | 0: a timeout resets the chip. Non-zero: a timeout raises the watchdog interrupt instead of a reset; the driver's handler only clears it. |
| `wdt_timeout` | Timeout in watchdog clock ticks. Only the low 16 bits are used. 0 leaves the watchdog stopped. SDK examples pass milliseconds, which assumes a 1 kHz watchdog clock. |

### wdt_disable { #wdt_disable }

```c
void wdt_disable(void);
```

Stop the watchdog.

### wdt_get_counter { #wdt_get_counter }

```c
uint32_t wdt_get_counter(void);
```

Read the watchdog counter.

**回傳值**：Current counter value in watchdog clock ticks (16 bits).

### wdt_feed { #wdt_feed }

```c
void wdt_feed(void);
```

Reset the watchdog counter (feed the watchdog).

### wdt_isWDTReset { #wdt_isWDTReset }

```c
void wdt_isWDTReset(void);
```

Read the watchdog reset flag.

!!! note "注意"
    The function returns `void`, so the flag it reads is not available to the caller; calling it has no visible effect.

### wdt_clearWDTReset { #wdt_clearWDTReset }

```c
void wdt_clearWDTReset(void);
```

Clear the flag that records a reset caused by the watchdog.

### wdt_setTimeout { #wdt_setTimeout }

```c
void wdt_setTimeout(uint32_t wdt_timeout);
```

Change the watchdog timeout.

Stops the watchdog, writes the new timeout and starts it again, even if it was stopped before.

| 參數 | 說明 |
|---|---|
| `wdt_timeout` | Timeout in watchdog clock ticks (low 16 bits used), as for [`wdt_init()`](#wdt_init). |

## hal_aon_wdt.h { #hal_aon_wdt-h }

`#include "hal_aon_wdt.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_aon_wdt.h)）

Always-on (AON) watchdog timer: chip reset on timeout, also in the PDS and HBN sleep modes.

The AON watchdog is clocked by the 32 kHz clock (RC32K or XTAL32K) and keeps running in the PDS and HBN sleep modes. The timeout is selected with a mask bit:

```text
timeout = 2^(mask_bit + 1) / 32768 seconds
```

mask_bit 
timeout 
mask_bit 
timeout 
mask_bit 
timeout 


15 
2 s 
18 
16 s 
21 
128 s 


16 
4 s 
19 
32 s 
22 
256 s 


17 
8 s 
20 
64 s

Every step doubles the timeout, so there are no intermediate values: a 30 s budget means choosing 32 s (mask 19).

[`aon_wdt_init()`](#aon_wdt_init) clears the AON watchdog reset flag, so read [`aon_wdt_get_reset_status()`](#aon_wdt_get_reset_status) before calling it. On chips without AON watchdog support (`CONFIG_AON_WDT_SUPPORT` not set, for example IPRO6) all functions do nothing and [`aon_wdt_get_reset_status()`](#aon_wdt_get_reset_status) returns 0.

### aon_wdt_init { #aon_wdt_init }

```c
void aon_wdt_init(uint8_t mask_bit);
```

Initialize and start the AON watchdog timer.

Stops the watchdog, clears its reset flag, sets the timeout, enables it and feeds it once.

| 參數 | 說明 |
|---|---|
| `mask_bit` | Timeout mask bit (0-63; only the low 6 bits are used). Use the `AON_WDT_TIMEOUT_*` defines. |

### aon_wdt_feed { #aon_wdt_feed }

```c
void aon_wdt_feed(void);
```

Feed (kick) the AON watchdog timer, resetting its counter.

### aon_wdt_disable { #aon_wdt_disable }

```c
void aon_wdt_disable(void);
```

Disable the AON watchdog timer.

### aon_wdt_get_reset_status { #aon_wdt_get_reset_status }

```c
int aon_wdt_get_reset_status(void);
```

Check if the last reset was caused by the AON watchdog.

| 回傳碼 | 說明 |
|---|---|
| `1` | The AON watchdog triggered the reset. |
| `0` | It did not, the flag was cleared, or AON watchdog support is not built in. |

### aon_wdt_clear_reset_status { #aon_wdt_clear_reset_status }

```c
void aon_wdt_clear_reset_status(void);
```

Clear the AON watchdog reset status flag.

### 巨集 { #hal_aon_wdt-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `AON_WDT_TIMEOUT_2S` | `15` | mask_bit for a 2 s timeout. |
| `AON_WDT_TIMEOUT_4S` | `16` | mask_bit for a 4 s timeout. |
| `AON_WDT_TIMEOUT_8S` | `17` | mask_bit for an 8 s timeout. |
| `AON_WDT_TIMEOUT_16S` | `18` | mask_bit for a 16 s timeout. |
| `AON_WDT_TIMEOUT_32S` | `19` | mask_bit for a 32 s timeout. |
| `AON_WDT_TIMEOUT_64S` | `20` | mask_bit for a 64 s timeout. |
| `AON_WDT_DEFAULT_TIMEOUT` | `AON_WDT_TIMEOUT_16S` | Default timeout for the system AON watchdog. |

## hal_cache_alloc.h { #hal_cache_alloc-h }

`#include "hal_cache_alloc.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_cache_alloc.h)）

Cache-line aligned heap allocation for DMA and hardware-accelerator buffers (FreeRTOS builds).

pvPortMalloc() only guarantees `portBYTE_ALIGNMENT` (8 bytes on IPRO7). Buffers shared with DMA or hardware accelerators need cache-line alignment so that cleaning or invalidating the data cache for the buffer does not affect other heap objects in the same cache line. Allocate such buffers with [`pvPortMallocCacheAligned()`](#pvPortMallocCacheAligned) and round their size up to a multiple of [`HAL_CACHE_LINE_SIZE`](#hal_cache_alloc-h-macros) as well.

### pvPortMallocCacheAligned { #pvPortMallocCacheAligned }

```c
void * pvPortMallocCacheAligned(size_t size);
```

Allocate a heap block whose start is aligned to a cache line.

Allocates `size` + [`HAL_CACHE_LINE_SIZE`](#hal_cache_alloc-h-macros) + `sizeof(void *)` bytes with pvPortMalloc() and returns the first cache-line aligned address inside it.

| 參數 | 說明 |
|---|---|
| `size` | Number of usable bytes. |

**回傳值**：Cache-line aligned pointer, or NULL if the allocation failed.

!!! note "注意"
    Free the block only with [`vPortFreeCacheAligned()`](#vPortFreeCacheAligned), never with vPortFree() or free().

### vPortFreeCacheAligned { #vPortFreeCacheAligned }

```c
void vPortFreeCacheAligned(void *ptr);
```

Free a block allocated with [`pvPortMallocCacheAligned()`](#pvPortMallocCacheAligned).

| 參數 | 說明 |
|---|---|
| `ptr` | Pointer returned by [`pvPortMallocCacheAligned()`](#pvPortMallocCacheAligned), or NULL (no effect). |

### 巨集 { #hal_cache_alloc-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_CACHE_LINE_SIZE` | `CCM_CACHELINE_SIZE` | Data cache line size in bytes (32). |

## hal_hbnram_mgnt.h { #hal_hbnram_mgnt-h }

`#include "hal_hbnram_mgnt.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_hbnram_mgnt.h)）

HBN RAM layout: the 4 KB always-on RAM shared by boot, firmware and the low-power framework.

HBN RAM keeps its contents in PDS sleep, in HBN level 0 and across warm resets; it is undefined after a power-on reset. This header is the single definition of how the 4 KB are divided. Use the `HAL_HBNRAM_*_ADDR` and `*_SIZE` macros instead of hard-coded addresses.

Layout (offsets from `HBN_RAM_BASE`, 0x20090000 on IPRO7 and IPRO6):

```text
0x000  LP_FW       1024 B  low-power wake-up code
0x400  LP_PARAM     512 B  low-power framework state
0x600  RSTINFO       32 B  hal_hbnram_sysinfo_t (reset reason, boot status)
0x620  LP_WAKE_CTX   64 B  hal_hbnram_lp_wake_ctx_t (HBN fast-boot wake)
0x660  BOOT2        644 B  boot-parameter snapshot for HBN fast-boot wake
0x8E4  RESERVED    1564 B  free (IPRO6: 540 B, followed by WLCAL)
0xB00  WLCAL       1024 B  IPRO6 only: Wi-Fi/RF calibration data
0xF00  IOT2LP       256 B  parameters of the stand-alone low-power image
0x1000 end
```

The LP_FW, LP_PARAM, BOOT2 and IOT2LP regions belong to the HAL and the low-power framework; applications must not write them. Applications may use the documented fields of [`hal_hbnram_sysinfo_t`](#hal_hbnram_sysinfo_t) and the scratch words of [`hal_hbnram_lp_wake_ctx_t`](#hal_hbnram_lp_wake_ctx_t).

### hal_hbnram_sysinfo_t { #hal_hbnram_sysinfo_t }

System information kept in HBN RAM, shared by boot loader and firmware.

Survives PDS/HBN sleep and warm resets. After a power-on reset the content is undefined; [`hal_rst_reason_detect()`](#hal_rst_reason_detect) recognizes this through `magic`, then sets `magic` and clears `reset_reason`. Access the structure through [`hal_hbnram_sysinfo`](#hal_hbnram_mgnt-h-macros). Size: 32 bytes.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `magic` | `uint32_t` | [`HAL_HBNRAM_SYSINFO_MAGIC`](#hal_hbnram_mgnt-h-macros) when the region is valid. |
| `reset_reason` | `uint32_t` | Reset reason for the next boot, a [`hal_rst_reason_t`](#hal_rst_reason_t) value; written by [`hal_rst_reason_set()`](#hal_rst_reason_set). |
| `wdt_reset_count` | `uint8_t` | Number of consecutive AON watchdog resets. |
| `boot_stage` | `uint8_t` | Boot progress, a `BOOT_STAGE_*` value. |
| `boot_flags` | `uint8_t` | `BOOT_FLAG_*` bits. |
| `_pad0` | `uint8_t` | Padding. |
| `boot_uptime_ms` | `uint32_t` | Firmware uptime in ms at the last boot checkpoint, for diagnostics; not written by the HAL. |
| `stub_enter_count` | `uint32_t` | Diagnostic counter of the start-up code; not written by the HAL. Treat as reserved. |
| `reserved` | `uint32_t[3]` | Reserved. |

### hal_hbnram_lp_wake_ctx_t { #hal_hbnram_lp_wake_ctx_t }

Wake context of the HBN fast-boot path.

[`hal_lp_enter_fastboot()`](power.md#hal_lp_enter_fastboot) fills this structure just before the chip enters HBN. A wake-up from HBN is a full boot, so the firmware reads it after start-up with [`hal_lp_get_wake_context()`](power.md#hal_lp_get_wake_context), after [`hal_lp_is_fastboot_wakeup()`](power.md#hal_lp_is_fastboot_wakeup) has returned true. Size: 64 bytes, all fields 32-bit.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `magic` | `uint32_t` | [`HAL_HBNRAM_LP_WAKE_CTX_MAGIC`](#hal_hbnram_mgnt-h-macros) when valid. |
| `wake_reason` | `uint32_t` | `HAL_LP_WAKEUP_*` bits ([`hal_lp.h`](power.md#hal_lp-h)) of the wake sources that were requested, not of the one that fired. |
| `wake_gpio_bits` | `uint32_t` | GPIO wake bits; currently always 0. |
| `rtc_cnt_low` | `uint32_t` | Low 32 bits of the RTC counter (32.768 kHz ticks) taken just before entering HBN. |
| `rtc_cnt_high` | `uint32_t` | High bits of that RTC counter value. |
| `wake_counter` | `uint32_t` | Number of fast-boot sleeps since the context was last invalid; incremented on every [`hal_lp_enter_fastboot()`](power.md#hal_lp_enter_fastboot). |
| `reserved` | `uint32_t[10]` | Not used by the HAL; free for application data that must survive the HBN sleep. |

### 型別定義 { #hal_hbnram_mgnt-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `hal_hbnram_rstinfo_t` | `typedef hal_hbnram_sysinfo_t hal_hbnram_rstinfo_t` | Former name of [`hal_hbnram_sysinfo_t`](#hal_hbnram_sysinfo_t). |

### 巨集 { #hal_hbnram_mgnt-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_HBNRAM_LP_FW_OFFSET` | `0x000` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_LP_FW_SIZE` | `0x400` | Size in bytes (1 KB). |
| `HAL_HBNRAM_LP_FW_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_LP_FW_OFFSET)` | Address. |
| `HAL_HBNRAM_LP_PARAM_OFFSET` | `0x400` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_LP_PARAM_SIZE` | `0x200` | Size in bytes (512 B). |
| `HAL_HBNRAM_LP_PARAM_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_LP_PARAM_O...` | Address. |
| `HAL_HBNRAM_RSTINFO_OFFSET` | `0x600` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_RSTINFO_SIZE` | `0x020` | Size in bytes (32 B). |
| `HAL_HBNRAM_RSTINFO_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_RSTINFO_OF...` | Address. |
| `BOOT_STAGE_BOOT2` | `0` | The boot loader is running. |
| `BOOT_STAGE_FW_EARLY` | `1` | Firmware early initialization is running. |
| `BOOT_STAGE_FW_READY` | `2` | Firmware scheduler has started. |
| `BOOT_STAGE_FW_OK` | `3` | Firmware has confirmed a successful boot. |
| `BOOT_FLAG_WDT_ENABLED` | `(1 << 0)` | The AON watchdog is running. |
| `BOOT_FLAG_OTA_PENDING` | `(1 << 1)` | A firmware update is in progress. |
| `BOOT_FLAG_FW_BOOTED` | `(1 << 2)` | The firmware booted successfully. |
| `BOOT_FLAG_LP_FASTBOOT` | `(1 << 3)` | This boot is a wake-up from [`hal_lp_enter_fastboot()`](power.md#hal_lp_enter_fastboot); set by the HAL, read and cleared by [`hal_lp_is_fastboot_wakeup()`](power.md#hal_lp_is_fastboot_wakeup). |
| `HAL_HBNRAM_LP_WAKE_CTX_OFFSET` | `0x620` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_LP_WAKE_CTX_SIZE` | `0x040` | Size in bytes (64 B). |
| `HAL_HBNRAM_LP_WAKE_CTX_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_LP_WAKE_CT...` | Address. |
| `HAL_HBNRAM_BOOT2_OFFSET` | `0x660` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_BOOT2_SIZE` | `0x284` | Size in bytes: 4-byte magic + 640-byte payload. |
| `HAL_HBNRAM_BOOT2_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_BOOT2_OFFSET)` | Address of the region. May be defined before including this header, for example to point host-side tests at a buffer. |
| `HAL_HBNRAM_BOOT2_DATA_SIZE` | `0x280` | Payload size in bytes (640 B). |
| `HAL_HBNRAM_BOOT2_MAGIC` | `0x32544F42` | Magic word of a valid snapshot ("BOT2"). |
| `HAL_HBNRAM_RESERVED_OFFSET` | `0x8E4` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_RESERVED_SIZE` | `0x61C` | Size in bytes (1564 B; 540 B on IPRO6). |
| `HAL_HBNRAM_RESERVED_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_RESERVED_O...` | Address. |
| `HAL_HBNRAM_IOT2LP_OFFSET` | `0xF00` | Offset from `HBN_RAM_BASE`. |
| `HAL_HBNRAM_IOT2LP_SIZE` | `0x100` | Size in bytes (256 B). |
| `HAL_HBNRAM_IOT2LP_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_IOT2LP_OFF...` | Address. |
| `HAL_HBNRAM_TOTAL_SIZE` | `0x1000` | Total size of HBN RAM in bytes (4 KB). |
| `HAL_HBNRAM_SYSINFO_MAGIC` | `0x52535449` | Value of `hal_hbnram_sysinfo_t::magic` once the region has been initialized. Any other value means the contents are undefined, i.e. the chip had a power-on reset. |
| `AON_WDT_MAX_RESETS` | `5` | Number of consecutive AON watchdog resets (`hal_hbnram_sysinfo_t::wdt_reset_count`) after which download mode is entered. |
| `HAL_HBNRAM_SYSINFO_ADDR` | `HAL_HBNRAM_RSTINFO_ADDR` | Address of the [`hal_hbnram_sysinfo_t`](#hal_hbnram_sysinfo_t) instance (same as [`HAL_HBNRAM_RSTINFO_ADDR`](#hal_hbnram_mgnt-h-macros)). |
| `hal_hbnram_sysinfo` | `((volatile hal_hbnram_sysinfo_t *)HAL...` | Pointer to the [`hal_hbnram_sysinfo_t`](#hal_hbnram_sysinfo_t) instance in HBN RAM. |
| `HAL_HBNRAM_RSTINFO_MAGIC` | `HAL_HBNRAM_SYSINFO_MAGIC` | Former name of [`HAL_HBNRAM_SYSINFO_MAGIC`](#hal_hbnram_mgnt-h-macros). |
| `hal_hbnram_rstinfo` | `hal_hbnram_sysinfo` | Former name of [`hal_hbnram_sysinfo`](#hal_hbnram_mgnt-h-macros). |
| `HAL_HBNRAM_LP_WAKE_CTX_MAGIC` | `0x4657414B` | Value of `hal_hbnram_lp_wake_ctx_t::magic` when the context is valid. |
| `hal_hbnram_lp_wake_ctx` | `((volatile hal_hbnram_lp_wake_ctx_t *...` | Pointer to the [`hal_hbnram_lp_wake_ctx_t`](#hal_hbnram_lp_wake_ctx_t) instance in HBN RAM. |
| `HAL_HBNRAM_CLK32K_OVR_OFFSET` | `(HAL_HBNRAM_RESERVED_OFFSET + HAL_HBN...` | Offset of the 32 kHz clock override word: the last 32-bit word of the RESERVED region. On IPRO6 the board start-up code reads it to choose between the 32 kHz crystal and the RC oscillator. |
| `HAL_HBNRAM_CLK32K_OVR_ADDR` | `(HBN_RAM_BASE + HAL_HBNRAM_CLK32K_OVR...` | Address of the 32 kHz clock override word. |
