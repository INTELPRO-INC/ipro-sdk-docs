---
title: "Low Power"
description: WFI, PDS and HBN in IPRO7 FreeRTOS applications — the low-power framework, configuration, programming interface, retention and wake-up, BLE with sleep, and measuring the IPRO7AI current on the Reef
migrate_from: []
---

# Low Power

FreeRTOS applications on IPRO7 can use three power-saving states: WFI (FreeRTOS tickless idle), PDS (Power-Down Sleep, Level 31, which resumes in place) and HBN (Hibernate, which wakes through a cold boot). The SDK provides PDS entry and recovery through the prebuilt low-power framework `hal_lp`, and automatic WFI/PDS selection through `ipro_pm`. On the IPRO7AI Reef EVK you can measure the IPRO7AI's own current with SW8 and JP2; none of the shipped Reef configurations enters PDS.

!!! abstract "At a glance"
    - Framework: `bsp/hal/lp_framework/ipro7/` (`hal_lp.h`, prebuilt `liblp_framework.a`) and `hal_pm.h`; automatic mode selection in `components/sys/ipro_pm/`.
    - Reef: no shipped Reef configuration uses PDS. SW8 and JP2 put an ammeter in the IPRO7AI's 3.3 V supply.
    - Wake-up: PDS wakes on the RTC timer, GPIO and other sources; the console UART cannot wake PDS.
    - Not included: PDS during a BLE connection (it needs a controller source build). No low-power modes under Zephyr.

## Low-power modes { #modes }

| Mode | How to enter | What is kept | Wake sources | After wake-up |
|---|---|---|---|---|
| WFI | FreeRTOS tickless idle (`CONFIG_FREERTOS_USE_TICKLESS_IDLE`) | Everything | Any interrupt | Continues in place |
| PDS (Level 31) | `hal_lp_enter()`, or the low-level `pm_pds_mode_enter(PM_PDS_LEVEL_31, …)` | OCRAM (see [Retention and wake-up](#retention-wake)), HBN RAM; optionally PSRAM in self-refresh | RTC timer, GPIO, analog comparator (ACOMP), BLE | Continues in place; the CPU, RF and MISC domains are reset, so the console UART and the system timer must be reinitialized |
| HBN (Level 0) | `hal_lp_enter_fastboot()`, or the low-level `pm_hbn_mode_enter(PM_HBN_LEVEL_0, …)` | Only HBN RAM (4 KB) and the RTC | RTC timer, AON pins, BOR, ACOMP | Cold boot from the start of the firmware; detect it with `hal_lp_is_fastboot_wakeup()` |

## Architecture { #architecture }

| Layer | Location | What it does |
|---|---|---|
| Application | your code | Decides when to sleep, what to keep and what wakes the chip |
| Automatic mode selection | `components/sys/ipro_pm/` (source) | Hooks into FreeRTOS tickless idle and picks WFI or PDS for each idle window, within the limits the application sets |
| Low-power framework | `bsp/hal/lp_framework/ipro7/`: `hal_lp.h`, `lp_uart.h`, `lib/liblp_framework.a` (prebuilt, always linked in IPRO7 builds) | RTC and GPIO wake-up, CPU state save and restore, flash XIP and PSRAM recovery, virtual time, RC32K calibration, wake-up hooks |
| Low-level power management | `bsp/hal/inc/hal_pm.h` | `pm_pds_mode_enter()`, `pm_hbn_mode_enter()`, `pm_pds_gpio_wakeup_set()`, `pm_pds_set_misc_keep()`, 32 kHz clock source selection |

## Configuration { #configuration }

```ini title="apps/test/ipro_lp_test/.config (excerpt)"
# CONFIG_USE_PSRAM is not set
CONFIG_HAL_LP=y
CONFIG_FREERTOS_IDLE_HOOK=y
CONFIG_PLATFORM_UART_BAUDRATE=115200
```

| Key | Notes |
|---|---|
| `CONFIG_HAL_LP` | Set by applications that enter PDS through `hal_lp` (`ipro_lp_test`) |
| `CONFIG_FREERTOS_IDLE_HOOK` | Enables `vApplicationIdleHook()`, where an application can enter PDS when idle |
| `CONFIG_FREERTOS_USE_TICKLESS_IDLE` | FreeRTOS tickless idle; the CPU enters WFI when idle |
| `CONFIG_IPRO_PM` | Enables `ipro_pm`; also requires `CONFIG_FREERTOS_USE_TICKLESS_IDLE=1` and `CONFIG_FREERTOS_IDLE_HOOK=y`, or the build stops with `#error` |
| `CONFIG_IPRO_PM_MAX_MODE` | Deepest mode allowed at boot: 0 active, 1 WFI (default), 2 native, 3 PDS; change it at run time with `ipro_pm_policy_set()` |
| `CONFIG_IPRO_PM_IDLE_PDS` | The idle task enters PDS itself (not while the BLE controller runs); also set `CONFIG_IPRO_PM_TIMEBASE=y` |
| `CONFIG_IPRO_PM_SHELL` | The `pm` shell command (status, policy, `pm stats`) |

`.config` becomes `autoconf.h` as written; Kconfig dependencies are not applied, so write out every related key.

!!! warning "Not compatible with the HOTCODE options"
    `CONFIG_IPRO7_BLE_HOTCODE` and `CONFIG_IPRO7_WIFI_HOST_HOTCODE` cannot be combined with the low-power layouts (`CONFIG_HAL_LP`, `CONFIG_IPRO_PM_BLE`, `CONFIG_IPRO_PM_PDS_CONNECTED`, `CONFIG_OCRAM_NORET_SPLIT`); linker script generation stops with an error. On the Reef, `ipro7ai_reef_demo/defconfig_wifi_ipro6s` uses the Wi-Fi option and `ipro_throughput_test/defconfig_reef` the BLE option.

## Test application ipro_lp_test { #lp-test }

`apps/test/ipro_lp_test` is a minimal application without BLE or PSRAM that tests PDS Level 31 with RTC wake-up. It is configured for the IPRO7 EVB (`CONFIG_EVB=y`). Its `lp` shell commands cover the cases on this page: `lp sleep <ms>` (PDS through `hal_lp`), `lp auto on|off` (PDS when idle), `lp status`, `lp mem [ms]` (which OCRAM survives), `lp misc on|off` (keep the MISC domain powered), `lp fastboot <ms>` (HBN wake through cold boot) and `lp wakectx`. Read its `src/lp_test_cli.c` alongside this page.

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
- GPIO wake-up: set `gpio_wakeup_en` and `gpio_cfg` (`wakeup_mask`, trigger, pull) in `hal_lp_cfg_t`; GPIO0–31 are available.
- The FreeRTOS tick count is not corrected for you after a sleep: add the actual sleep time back with `xTaskCatchUpTicks()`, as `ipro_lp_test` does.
- HBN: after `hal_lp_enter_fastboot()` the chip wakes through a cold boot, so the call never returns. At boot, check `hal_lp_is_fastboot_wakeup()` and read the wake context with `hal_lp_get_wake_context()`; anything that must survive has to be in HBN RAM first.

## Retention and wake-up { #retention-wake }

- **OCRAM**: with the MISC domain powered down (the default), only the first 64 KB of OCRAM is retained through PDS31; `pm_pds_set_misc_keep()` keeps the MISC domain powered and retains all of OCRAM. Keep the data you need after wake-up in the first 64 KB, or keep MISC on, and check the result with `lp mem` in `ipro_lp_test`.
- **PSRAM**: `psram_retention` keeps PSRAM in self-refresh during PDS, and the framework restores it on wake-up. On IPRO7AI (the Reef's SoC) the PSRAM is inside the package and must stay in self-refresh through PDS.
- **HBN RAM**: 4 KB, the only memory kept through HBN; the framework's parameters and the fastboot wake context live there too.
- **Console**: UART0 sits in a domain that PDS31 resets, so reinitialize it after wake-up (`shell_uart_reinit()` or `platform_init()`). The console RX pin (GPIO21, U6 pin 4 on the Reef) cannot wake PDS, and characters typed during sleep are lost.
- **GPIO wake-up**: `hal_lp` supports GPIO0–31. The low-level `pm_pds_gpio_wakeup_set()` (`hal_pm.h`) accepts GPIO0–41, but pins share trigger settings in groups of four and only ASYNC triggers work (the SYNC ones need a clock that PDS stops). HBN wakes only from the AON pins.
- **32 kHz clock**: RC32K by default; `pm_pds_set_32k_src()` switches to a 32 kHz crystal when the board has one. The Reef has none and runs from RC32K; the framework includes RC32K calibration.
- **Flash**: with `flash_power_down = 1` the flash is powered down during sleep, and the framework restores XIP on wake-up.

## BLE with sleep { #ble-sleep }

- The BLE backend of `ipro_pm` and PDS during a BLE connection (`CONFIG_IPRO_PM_BLE`, `CONFIG_IPRO_PM_PDS_CONNECTED`) force a source build of the BLE controller. The controller ships only as prebuilt libraries, so these cannot be built from the package. For products that need low power during BLE connections, contact INTELPRO.
- `ipro_ble_remote/defconfig_reef` deliberately runs without PDS: the Reef is USB-powered, and its camera and audio need the clocks.
- `ipro_pdm_mic_demo` (IPRO7 EVB, IPRO7AI EVK) shows BLE with tickless WFI and a manual `pds [sec]` command.
- For BLE controller variants, Exchange Memory size and other BLE settings, see [BLE Development](ble.md).

## Measuring { #measure }

- Measure in the SoC's supply path with an external meter. On the Reef, SW8 and JP2 route the IPRO7AI's 3.3 V through the meter (walk-through below); other boards are covered in [Power & Current Measurement](../hardware/power.md).
- Confirm how often and how long the chip actually sleeps, and log the wake reason (`hal_lp_result_t`). If it wakes more often than expected, look for timers and pending interrupts first (`hal_lp_enter()` returns `HAL_LP_ERR_ENTRY_ABORTED`).
- With `ipro_pm`, `pm stats` lists the residency in each mode and an estimated current. The estimate is for comparing configurations only; it does not replace a measurement.
- Compare the same firmware under WFI and under PDS, and let UART output finish before sleeping so that it is not cut off.

## Hands-on on the Reef { #hands-on }

Measure how much current the IPRO7AI draws while your firmware runs. No shipped Reef configuration enters PDS, so this walk-through uses the out-of-box firmware and compares an idle shell with the camera pipeline running; repeat it with your own application to get its baseline before you add sleep.

You need an ammeter (or a source-measure unit) with leads for the 3-pin JP2 header.

<div class="ipro-steps" markdown>

1. **Configuration**

    Nothing to add. `apps/platform/ipro7ai_reef_demo/.config` sets no low-power key (`CONFIG_HAL_LP`, `CONFIG_IPRO_PM` are absent), so the CPU only idles.

2. **Build and flash**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    In download mode (hold SW1, tap SW2, release SW1), from the IntelProCube directory:

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    Details are in [Flashing & Serial Console](../get-started/flash-and-monitor.md).

3. **Put the meter in the supply**

    Unplug USB-C. Connect the ammeter between JP2 pin 1 (3V3) and pin 2 (SOC), slide SW8 to **MEAS**, then plug USB-C back in. The reading covers the IPRO7AI's 3.3 V pins only, not the camera, LED, amplifier or microSD socket.

4. **Read the idle current**

    Open the console at 115200 baud. At power-on the demo parks the camera; with the `ipro />` prompt waiting, note the meter reading.

5. **Run the camera pipeline and compare**

    ```text
    cam start
    cam stop
    cam park
    ```

    The console answers ``streaming - `cam status` in a second``, then `stopped`, then `PWDN high, RESETB low, XCLK off`. Note the reading while the stream runs and again after `cam park`: the difference is what the camera pipeline (XCLK, DVP input, ISP) costs the SoC.

6. **Restore the board**

    Unplug USB-C, slide SW8 back to **PWR**, and only then remove the meter. With SW8 on MEAS and nothing on JP2, the IPRO7AI is unpowered while the peripherals back-feed it through the I/O pins.

</div>

Next: start your own application with [Create Your First Application](../tutorials/first-own-app.md), and check its behavior and current with [Test Your Application](../tutorials/testing.md).

## Limitations in this release { #limitations }

- No shipped IPRO7AI Reef EVK configuration enters PDS or HBN; `ipro_lp_test` and the `ipro7_demo` low-power commands target the IPRO7 EVB.
- PDS during a BLE connection cannot be built from the package (controller source build).
- No low-power modes under Zephyr RTOS (`pm_state` does not enter PDS or HBN); see [Zephyr RTOS](zephyr.md).
- `CONFIG_IPRO_PM_IDLE_PDS` (PDS entered by the idle task) has no shipped example; validate it on your board before use.
- The low-power memory layouts cannot be combined with the HOTCODE options.

## Related documents { #related }

- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md): SW8, JP2 and the current-measurement procedure.
- [Power & Current Measurement](../hardware/power.md)
- [BLE Development](ble.md)
- [Build System & Configuration](build-system.md)
- [Zephyr RTOS](zephyr.md)
