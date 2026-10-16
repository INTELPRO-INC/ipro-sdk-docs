---
title: "Low Power"
description: WFI, PDS and HBN in FreeRTOS applications — the low-power framework, configuration, ipro_lp_test commands, retention and wake-up, BLE with sleep, and how to measure
migrate_from: []
---

# Low Power

FreeRTOS applications on IPRO7 can use three power-saving states: WFI (FreeRTOS tickless idle), PDS (Power-Down Sleep, Level 31, which resumes in place) and HBN (Hibernate, which wakes through a cold boot). The SDK provides PDS entry and recovery through the prebuilt low-power framework `hal_lp`, together with the `ipro_lp_test` test application and the low-power commands of `ipro7_demo`. Zephyr RTOS does not support low-power modes yet.

!!! abstract "At a glance"
    - Framework: `bsp/hal/lp_framework/ipro7/` (`hal_lp.h`, prebuilt `liblp_framework.a`) and `hal_pm.h`; automatic mode selection in `components/sys/ipro_pm/`.
    - Test: the `lp` commands of `apps/test/ipro_lp_test` (IPRO7 EVB, no PSRAM, no BLE).
    - Wake-up: PDS wakes on an RTC timer, GPIO and other sources; the console UART cannot wake PDS.
    - Not included: PDS during a BLE connection (it needs controller source code that V2.1.0 does not ship). No low-power modes under Zephyr.

## Low-power modes { #modes }

| Mode | How to enter | What is kept | Wake sources | After wake-up |
|---|---|---|---|---|
| WFI | FreeRTOS tickless idle (`CONFIG_FREERTOS_USE_TICKLESS_IDLE`) | Everything | Any interrupt | Continues in place |
| PDS (Level 31) | `hal_lp_enter()`, or the low-level `pm_pds_mode_enter(PM_PDS_LEVEL_31, …)` | OCRAM (see [retention and wake-up](#retention-wake)), HBN RAM; optionally PSRAM in self-refresh | RTC timer, GPIO, analog comparator (ACOMP), BLE | Continues in place; the CPU, RF and MISC domains are reset, so the console UART and the system timer must be reinitialized |
| HBN (Level 0) | `hal_lp_enter_fastboot()`, or the low-level `pm_hbn_mode_enter(PM_HBN_LEVEL_0, …)` | Only HBN RAM (4 KB) and the RTC | RTC timer, AON pins, BOR, ACOMP | Cold boot, firmware starts from the beginning; detect it with `hal_lp_is_fastboot_wakeup()` |

## Architecture { #architecture }

| Layer | Location | What it does |
|---|---|---|
| Application | `ipro_lp_test`, `ipro7_demo`, `ipro_pdm_mic_demo` | Decides when to sleep, what to keep and what wakes the chip |
| Automatic mode selection | `components/sys/ipro_pm/` (source) | Hooks into FreeRTOS tickless idle and picks WFI or PDS for each idle window, within the limits the application sets |
| Low-power framework | `bsp/hal/lp_framework/ipro7/`: `hal_lp.h`, `lp_uart.h`, `lib/liblp_framework.a` (prebuilt, always linked in IPRO7 builds) | RTC and GPIO wake-up, CPU state save and restore, flash XIP and PSRAM recovery, virtual time, RC32K calibration, wake-up hooks |
| Low-level power management | `bsp/hal/inc/hal_pm.h` | `pm_pds_mode_enter()`, `pm_hbn_mode_enter()`, `pm_pds_gpio_wakeup_set()`, 32 kHz clock source selection |

## Configuration { #configuration }

```ini title="apps/test/ipro_lp_test/.config (excerpt)"
CONFIG_EVB=y
# CONFIG_USE_PSRAM is not set
CONFIG_HAL_LP=y
CONFIG_FREERTOS_IDLE_HOOK=y
CONFIG_PLATFORM_UART_BAUDRATE=115200
```

| Key | Notes |
|---|---|
| `CONFIG_HAL_LP` | Set by applications that sleep (`ipro_lp_test`) |
| `CONFIG_FREERTOS_IDLE_HOOK` | Enables `vApplicationIdleHook()`; `ipro_lp_test` runs its automatic PDS there |
| `CONFIG_FREERTOS_USE_TICKLESS_IDLE` | FreeRTOS tickless idle; the CPU enters WFI when idle |
| `CONFIG_IPRO_PM` | Enables `ipro_pm`; also requires `CONFIG_FREERTOS_USE_TICKLESS_IDLE=1` and `CONFIG_FREERTOS_IDLE_HOOK=y`, or the build stops with `#error` |
| `CONFIG_IPRO_PM_MAX_MODE` | Deepest mode allowed at boot: 0 active, 1 WFI (default), 2 native, 3 PDS; change it at run time with `ipro_pm_policy_set()` |
| `CONFIG_IPRO_PM_IDLE_PDS` | The idle task enters PDS itself (not used while the BLE controller runs); also set `CONFIG_IPRO_PM_TIMEBASE=y` |
| `CONFIG_IPRO_PM_SHELL` | The `pm` shell command (status, policy, `pm stats`) |

`.config` is turned into `autoconf.h` as written; Kconfig dependencies are not applied, so write out every related key.

!!! warning "Not compatible with the HOTCODE options"
    `CONFIG_IPRO7_BLE_HOTCODE` and `CONFIG_IPRO7_WIFI_HOST_HOTCODE` cannot be combined with the low-power memory layouts (`CONFIG_HAL_LP`, `CONFIG_IPRO_PM_BLE` and others); linker script generation fails with an error.

## Test application ipro_lp_test { #lp-test }

`apps/test/ipro_lp_test` is a minimal project without BLE or PSRAM that tests PDS Level 31 with RTC timer wake-up. It is configured for the IPRO7 EVB.

<div class="ipro-steps" markdown>

1. **Build**

    ```bash
    make -C apps/test/ipro_lp_test
    ```

    Output: `apps/test/ipro_lp_test/build/build_out/ipro_lp_test_IPRO7.bin`

2. **Flash** it as described on the [IPRO7 EVB](../hardware/boards/ipro7-evb.md) page and in [Flashing & Serial Console](../get-started/flash-and-monitor.md). The console runs at 115200 baud.

3. **Test**: enter these commands one by one and check that the board wakes and returns to the prompt each time.

    ```text
    lp rtc
    lp sleep 1000
    lp status
    lp mem 1000
    ```

</div>

| Command | Purpose |
|---|---|
| `lp sleep <ms>` | PDS through the `hal_lp` framework, woken by the RTC timer |
| `lp auto on` / `off` | Enter PDS automatically when idle (1 second each time) |
| `lp status`, `lp reset` | Show / clear sleep statistics |
| `lp heap` | Free heap |
| `lp rtc` | RTC counter (run it twice to check that it counts) |
| `lp raw <ms>` | PDS test that bypasses `hal_lp` (the board reboots) |
| `lp raw2 <ms> [fdpr]` | Minimal PDS test (f = flash, d = DLL, p = PLL, r = RF) |
| `lp hbn` | HBN register state |
| `lp clk` | Saved and current clock state |
| `lp fastboot <ms>` | Wake through the cold-boot path (the command does not return) |
| `lp wakectx` | Context of the last fastboot wake-up (kept in HBN RAM) |
| `lp mem [ms]` | Which OCRAM contents above and below 64 KB survive a sleep |
| `lp misc on` / `off` | Keep the MISC power domain on, or off (default), during PDS |

`ipro7_demo` (`CONFIG_DEMO_LOWPOWER=y`, already set in its shipped `.config`) also provides `lp_test [sleep_ms] [loop_count]`, `lp_gpio_test <gpio_pin> [trigger_mode]`, `pds_demo [sec]`, `hbn_demo [sec]` and `hbn_fastboot [ms]`.

## Programming interface { #api }

This flow follows `apps/platform/ipro7_demo/demo/soc/peripheral/lowpower_demo.c`: initialize the framework, register a wake-up hook, and enter PDS with an RTC timer.

```c title="Enter PDS with an RTC timer"
#include "hal_lp.h"

extern void shell_uart_reinit(void);
extern void vPortSetupTimerInterrupt(void);

static int wake_reinit(int wakeup_reason, void *arg)
{
    (void)wakeup_reason;
    (void)arg;
    shell_uart_reinit();          /* PDS reset the console UART */
    vPortSetupTimerInterrupt();   /* FreeRTOS system timer */
    /* Reinitialize other peripherals (I2C, SPI, ...) here */
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
        .psram_retention  = 1,     /* keep PSRAM in self-refresh when present */
        .ocram_retention  = 1,
    };
    hal_lp_result_t res;
    int ret = hal_lp_enter(&cfg, &res);   /* wake reason (HAL_LP_WAKEUP_*) or a negative error */
    if (ret == HAL_LP_ERR_ENTRY_ABORTED) {
        /* An interrupt was pending; the chip never entered PDS (same as one WFI) */
    }
    return ret;
}
```

- `hal_lp_result_t` reports the wake reason, the GPIOs that triggered it and the actual sleep time; `hal_lp_get_virtual_ms()` gives a time base that continues across sleeps.
- GPIO wake-up: set `gpio_wakeup_en` and `gpio_cfg` (`wakeup_mask`, trigger, pull) in `hal_lp_cfg_t`; GPIO0–31 are available. See `lp_gpio_test` in `ipro7_demo`.
- The FreeRTOS tick count is not corrected for you after a sleep: `ipro_lp_test` adds the actual sleep time back with `xTaskCatchUpTicks()`.
- HBN: after `hal_lp_enter_fastboot()` the chip wakes through a cold boot, so the call never returns. At boot, check `hal_lp_is_fastboot_wakeup()` and read the wake context with `hal_lp_get_wake_context()`; anything that must survive the sleep has to be in HBN RAM first.

## Retention and wake-up { #retention-wake }

- **OCRAM**: according to `ipro_lp_test`, its default PDS31 configuration powers down the MISC domain, so only the first 64 KB of OCRAM are guaranteed to be retained; `lp misc on` keeps the MISC domain powered through PDS and retains all of OCRAM. Retention depends on the power-domain settings, so keep the data you need after wake-up in the first 64 KB and check your configuration with `lp mem`.
- **PSRAM**: `psram_retention` keeps PSRAM in self-refresh during PDS, and the framework restores PSRAM on wake-up. On IPRO7AI the PSRAM is inside the chip package and must stay in self-refresh through PDS.
- **HBN RAM**: 4 KB, the only memory kept through HBN; the framework's parameters and the fastboot wake context live here too.
- **Console**: UART0 sits in a domain that PDS31 resets, so reinitialize it after wake-up (`shell_uart_reinit()` or `platform_init()`). The console RX pin (GPIO21) cannot wake PDS, and characters typed during sleep are lost.
- **GPIO wake-up**: `hal_lp` supports GPIO0–31. The low-level `pm_pds_gpio_wakeup_set()` (`hal_pm.h`) accepts GPIO0–41, but pins share trigger settings in groups of four, and only ASYNC triggers work (the SYNC ones need a clock that PDS stops). HBN wakes only from the AON pins.
- **32 kHz clock**: RC32K by default; `pm_pds_set_32k_src()` switches to a 32 kHz crystal (the board must have one). The framework includes RC32K calibration functions.
- **Flash**: with `flash_power_down = 1` the flash is powered down during sleep, and the framework restores XIP on wake-up.

## BLE with sleep { #ble-sleep }

- The BLE backend of `ipro_pm` and PDS during a BLE connection (`CONFIG_IPRO_PM_BLE`, `CONFIG_IPRO_PM_PDS_CONNECTED`) force a source build of the BLE controller. Controller source is not included in V2.1.0, so these cannot be built from the package — and neither can `apps/bluetooth/ble/ipro_ble_remote/defconfig_lowpower`. For products that need low power during BLE connections, contact INTELPRO.
- `apps/multimedia/ipro_pdm_mic_demo` enables tickless idle, but its shipped configurations set `CONFIG_IPRO_PDM_MIC_WFI_ONLY=1`: the CPU enters WFI when idle while BLE and RF keep running. Its automatic PDS option, `CONFIG_IPRO_PDM_MIC_AUTO_PDS`, is off in every shipped configuration.
- The same application's `pds [sec]` command enters PDS31 by hand and wakes on a timer or a GPIO (pins defined in `src/pdm_sleep.c`); the recording buffer in OCRAM is still there after wake-up.
- For BLE controller variants, Exchange Memory size and other BLE settings, see [BLE Development](ble.md).

## Measuring { #measure }

- Measure the current in the board's power path with an external meter; for measurement points and methods see [Power & Current Measurement](../hardware/power.md).
- Use `lp status` to confirm how often and how long the chip actually sleeps, and log the wake reason (`hal_lp_result_t`). If it wakes more often than expected, look for timers and pending interrupts first (`hal_lp_enter()` returns `HAL_LP_ERR_ENTRY_ABORTED`).
- With `ipro_pm`, `pm stats` lists the residency in each mode and an estimated current. The estimate is for comparing configurations only; it does not replace a measurement.
- Compare the same firmware under WFI and under PDS, and let UART output finish before sleeping so that it is not cut off.

## Limitations in this release { #limitations }

- No low-power modes under Zephyr RTOS (`pm_state` does not enter PDS or HBN); see [Zephyr RTOS](zephyr.md).
- PDS during a BLE connection cannot be built from the V2.1.0 package.
- The shipped low-power examples target the IPRO7 EVB; the IPRO7AI Reef EVK and the IPRO7AI EVK have no example configuration that uses PDS.
- `CONFIG_IPRO_PM_IDLE_PDS` (PDS entered by the idle task) has no shipped example; validate it on your own board before use.
- The low-power memory layouts cannot be combined with the HOTCODE options.

## Related documents { #related }

- [Power & Current Measurement](../hardware/power.md)
- [BLE Development](ble.md)
- [Build System & Configuration](build-system.md)
- [Zephyr RTOS](zephyr.md)
