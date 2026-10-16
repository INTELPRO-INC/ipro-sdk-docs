---
title: Power Management & Low Power
description: Power modes, PDS sleep and wake-up, the low-power framework and the low-power UART.
generated: tools/gen_api.py
migrate_from: []
---

# Power Management & Low Power

Power modes, PDS sleep and wake-up, the low-power framework and the low-power UART.

| Header | Functions | Description |
|---|---|---|
| [`hal_pm.h`](#hal_pm-h) | 22 | Power-management primitives: PDS and HBN sleep entry, wakeup sources, 32 kHz clock ownership and sleep-domain policy. |
| [`hal_pm_util.h`](#hal_pm_util-h) | 0 | Section attributes for code and data that must run from PDS retained RAM. |
| [`hal_lp.h`](#hal_lp-h) | 25 | Low-power framework (IPRO7): PDS sleep with resume, HBN fast-boot sleep, wake-up hooks and sleep timing. |
| [`lp_uart.h`](#lp_uart-h) | 5 | Minimal polled UART output for low-power wake-up code. |

## hal_pm.h { #hal_pm-h }

`#include "hal_pm.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pm.h))

Power-management primitives: PDS and HBN sleep entry, wakeup sources, 32 kHz clock ownership and sleep-domain policy.

Two sleep modes are available:

- **PDS** (power-down sleep): the CPU and most digital domains are powered down, retained RAM keeps its contents. On wake-up the CPU is reset, so execution only resumes where it stopped when the low-power framework saved and restores the context. Use [`hal_lp_enter()`](#hal_lp_enter) ([`hal_lp.h`](#hal_lp-h)) for that; the PDS functions here are its building blocks.
- **HBN** (hibernate): everything except the always-on domain is powered down; wake-up is a full boot. Only the 4 KB HBN RAM ([`hal_hbnram_mgnt.h`](platform.md#hal_hbnram_mgnt-h)) can carry state across.

Wake-up times are given in RTC ticks of the 32.768 kHz clock unless stated otherwise. Functions marked IPRO7 or IPRO6 only are no-ops (or not available) on the other chip.

### pm_pds_enable { #pm_pds_enable }

```c
void pm_pds_enable(uint32_t *cfg);
```

Program the PDS hardware and execute WFI (low level).

Writes back the data cache (IPRO7), applies the level configuration (including [`pm_pds_set_misc_keep()`](#pm_pds_set_misc_keep) and the BLE domain policy) and waits for the PDS sequencer to power the core down. No wakeup source is armed here; use [`pm_pds_mode_enter()`](#pm_pds_mode_enter) or, to resume execution after the sleep, [`hal_lp_enter()`](#hal_lp_enter).

A completed PDS sleep resets the CPU, so the function returns only when the core did not power down: an enabled interrupt was pending, the one-shot fallback set with [`pm_pds_wfi_fallback_set()`](#pm_pds_wfi_fallback_set) expired, or the level in `cfg` is not supported. On IPRO7 the interrupt enable state of the caller is restored on return.

| Parameter | Description |
|---|---|
| `cfg` | Pointer to a [`PM_PDS_CFG_Type`](#PM_PDS_CFG_Type), cast to `uint32_t *`. |

!!! warning "Warning"
    In builds with PSRAM, the PSRAM is put into self-refresh before the WFI and is not brought back if the function returns; [`hal_lp_enter()`](#hal_lp_enter) handles this case.

### pm_pds_set_misc_keep { #pm_pds_set_misc_keep }

```c
void pm_pds_set_misc_keep(bool keep);
```

Keep the Misc power domain alive across PDS sleeps.

By default PDS level 31 powers down and resets the Misc domain, which contains the IEEE 802.15.4 MAC. With `keep` = true the domain stays powered and out of reset (its clock is still gated), so its register state survives the sleep and does not need to be re-initialized on every wake-up, at the cost of higher sleep current.

The setting changes the HAL's default PDS configuration and stays in effect for all later sleeps until changed again. Call it before the first PDS entry. An active BLE domain policy ([`pm_pds_ble_ctlr_domain_policy_set()`](#pm_pds_ble_ctlr_domain_policy_set)) overrides it.

| Parameter | Description |
|---|---|
| `keep` | true to keep the Misc domain powered, false to restore the default (power down and reset). |

### pm_pds_ble_ctlr_domain_policy_set { #pm_pds_ble_ctlr_domain_policy_set }

```c
void pm_pds_ble_ctlr_domain_policy_set(uint32_t policy);
```

Set the PDS domain policy for the following PDS entries (IPRO7).

The policy is applied on top of the HAL's default configuration for each entry; the defaults themselves are not modified, so setting [`PM_PDS_BLE_CTLR_DOMAIN_POLICY_NONE`](#hal_pm-h-macros) restores the default behaviour. In builds where the policy is not supported the call has no effect.

| Parameter | Description |
|---|---|
| `policy` | Bitwise OR of `PM_PDS_BLE_CTLR_DOMAIN_POLICY_*` values. |

### pm_pds_ble_ctlr_domain_policy_get { #pm_pds_ble_ctlr_domain_policy_get }

```c
uint32_t pm_pds_ble_ctlr_domain_policy_get(void);
```

Get the PDS domain policy set with [`pm_pds_ble_ctlr_domain_policy_set()`](#pm_pds_ble_ctlr_domain_policy_set).

**Returns:** The current policy bits; always [`PM_PDS_BLE_CTLR_DOMAIN_POLICY_NONE`](#hal_pm-h-macros) in builds where the policy is not supported.

### pm_pds_set_dcdc11_vsel { #pm_pds_set_dcdc11_vsel }

```c
void pm_pds_set_dcdc11_vsel(uint8_t vsel, bool enable);
```

Set the PDS voltage-select field PDS_CTL[27:23] (IPRO6 only).

Stores the value in the IPRO6 PDS level configuration, which the HAL writes to the hardware on every PDS entry. The field selects the voltage of the main LDO11 regulator, which is powered down during PDS, so it does not lower the PDS sleep current; the retention rail is set with [`pm_ldo11_rt_set()`](#pm_ldo11_rt_set). No effect on IPRO7.

| Parameter | Description |
|---|---|
| `vsel` | 5-bit voltage select (reset value 0x8). |
| `enable` | true to apply `vsel` during PDS (PDS_CTL[18]); false keeps the run-mode voltage. |

### pm_pds_get_dcdc11_vsel { #pm_pds_get_dcdc11_vsel }

```c
void pm_pds_get_dcdc11_vsel(uint8_t *vsel, uint8_t *enable);
```

Read back the values set with [`pm_pds_set_dcdc11_vsel()`](#pm_pds_set_dcdc11_vsel) (IPRO6 only).

| Parameter | Description |
|---|---|
| `vsel` | Receives the voltage select; may be NULL. |
| `enable` | Receives 1 if the select is enabled, else 0; may be NULL. Both values are 0 on IPRO7. |

### pm_ldo11_rt_set { #pm_ldo11_rt_set }

```c
void pm_ldo11_rt_set(uint8_t sel);
```

Set the LDO11 retention voltage used during PDS (IPRO6 only).

The register is retained across PDS, so one call after each power-on covers all later sleeps. A lower retention voltage lowers the PDS sleep current. No effect on IPRO7.

| Parameter | Description |
|---|---|
| `sel` | Voltage code, 0 to 15: 0.60 V + 0.05 V x `sel`. The silicon default is 10 (1.10 V); the low-power configuration `CONFIG_LP_LDO11_RT_SEL` defaults to 6 (0.90 V). |

### pm_ldo11_use_ext_dcdc { #pm_ldo11_use_ext_dcdc }

```c
void pm_ldo11_use_ext_dcdc(void);
```

Hand the 1.1 V core rail over to an external DCDC (IPRO6 only).

Steps the internal LDO11 SoC and retention outputs down to 1.05 V, waits 1 ms, then sets 1.00 V, so that an external 1.1 V supply on the same rail carries the load. Only for boards that have such a supply (`CONFIG_LP_LDO11_EXT_DCDC`). No effect on IPRO7.

### pm_pds_set_32k_src { #pm_pds_set_32k_src }

```c
void pm_pds_set_32k_src(uint8_t use_xtal, uint32_t settle_ms);
```

Select the 32 kHz clock source and take ownership of it.

Until this is called the HAL owns the 32 kHz selection and keeps the RC32K oscillator as the default. After the call the selection made here is preserved through PDS entries. Nothing calls it during boot, so the platform default is unchanged unless an application or component (for example the BLE controller low-power support) calls it.

| Parameter | Description |
|---|---|
| `use_xtal` | 1 to power up the 32.768 kHz crystal and select it, 0 to power up and select the RC32K oscillator. |
| `settle_ms` | Delay in ms between powering up the crystal and selecting it. The function does not check that the crystal oscillates, and selecting a crystal that has not started stops the 32 kHz domain (RTC and sleep timer). When switching to the crystal from cold, pass its full start-up time (typically hundreds of ms). |

!!! note "Note"
    On IPRO7, selecting the RC32K oscillator re-applies its factory trim; run [`hal_rc32k_force_cal()`](platform.md#hal_rc32k_force_cal) afterwards if a run-time calibration is needed.

!!! note "Note"
    Blocks for `settle_ms` when `use_xtal` is 1.

### pm_pds_get_32k_src { #pm_pds_get_32k_src }

```c
void pm_pds_get_32k_src(uint8_t *use_xtal, uint8_t *forced_rc);
```

Read the current 32 kHz clock selection.

| Parameter | Description |
|---|---|
| `use_xtal` | Receives 1 if the 32.768 kHz crystal is currently selected, else 0; may be NULL. |
| `forced_rc` | Receives 1 while [`pm_pds_set_32k_src()`](#pm_pds_set_32k_src) has not been called (the HAL still owns the selection), else 0; may be NULL. |

### pm_pds_mode_enter { #pm_pds_mode_enter }

```c
void pm_pds_mode_enter(enum pm_pds_sleep_level pds_level, uint32_t sleep_time);
```

Arm the timed wakeup and enter PDS sleep.

Masks all wakeup sources and clears pending wake events, arms the RTC compare for `sleep_time` (and, on IPRO7, the GPIO pins armed with [`pm_pds_gpio_wakeup_set()`](#pm_pds_gpio_wakeup_set)), then calls [`pm_pds_enable()`](#pm_pds_enable).

A completed PDS sleep resets the CPU: the boot ROM continues at the callback set with [`pm_set_wakeup_callback()`](#pm_set_wakeup_callback) or performs a normal boot. The function therefore returns only when the core did not power down (see [`pm_pds_enable()`](#pm_pds_enable)). To sleep and continue after the call, use [`hal_lp_enter()`](#hal_lp_enter).

| Parameter | Description |
|---|---|
| `pds_level` | PDS level; must be [`PM_PDS_LEVEL_31`](#pm_pds_sleep_level). |
| `sleep_time` | Sleep time in RTC ticks (32.768 kHz). 0 arms no RTC wakeup. On IPRO7 a target set with [`pm_pds_rtc_target_override_set()`](#pm_pds_rtc_target_override_set) replaces it. |

### pm_pds_gpio_wakeup_set { #pm_pds_gpio_wakeup_set }

```c
int pm_pds_gpio_wakeup_set(uint8_t pin, uint8_t trigger);
```

Arm a GPIO as a PDS wakeup source (IPRO7 only).

PDS keeps the GPIO pad logic powered, so ordinary GPIOs can wake the chip (HBN only has the always-on pads). The hardware groups the pins (GPIO0-3, 4-7, 8-9, 20-23, 24-27, 28-31, 32-35, 36-39, 40-41) and the trigger is set per group, so pins in one group share the trigger of the last call for that group. GPIO10 to GPIO19 cannot wake the chip from PDS.

The pin's PDS pad configuration is set right away to input with the pull-up enabled. The arming takes effect at the next [`pm_pds_mode_enter()`](#pm_pds_mode_enter) (also when called through [`hal_lp_enter()`](#hal_lp_enter)) and stays until [`pm_pds_gpio_wakeup_unset()`](#pm_pds_gpio_wakeup_unset) or [`pm_pds_gpio_wakeup_clear()`](#pm_pds_gpio_wakeup_clear).

| Parameter | Description |
|---|---|
| `pin` | GPIO number: 0 to 9 or 20 to 41. |
| `trigger` | Trigger mode, a `PDS_GPIO_INT_TRIG_Type` value from drv_pds.h. Use an asynchronous mode such as `PDS_GPIO_INT_ASYNC_LOW_LEVEL` (for a button that pulls the pin low): the synchronous modes need a clock that is stopped in PDS. |

| Return value | Description |
|---|---|
| `0` | Pin armed. |
| `-1` | The pin has no PDS wakeup capability or the pad configuration failed. |

### pm_pds_gpio_wakeup_clear { #pm_pds_gpio_wakeup_clear }

```c
void pm_pds_gpio_wakeup_clear(void);
```

Disarm all GPIO wakeup pins armed with [`pm_pds_gpio_wakeup_set()`](#pm_pds_gpio_wakeup_set) (IPRO7 only).

### pm_pds_gpio_wakeup_unset { #pm_pds_gpio_wakeup_unset }

```c
void pm_pds_gpio_wakeup_unset(uint8_t pin);
```

Disarm one GPIO wakeup pin armed with [`pm_pds_gpio_wakeup_set()`](#pm_pds_gpio_wakeup_set) (IPRO7 only).

The pin group stays armed while another pin of the group is armed.

| Parameter | Description |
|---|---|
| `pin` | GPIO number; pins without PDS wakeup capability are ignored. |

### pm_pds_gpio_wakeup_dump { #pm_pds_gpio_wakeup_dump }

```c
void pm_pds_gpio_wakeup_dump(void);
```

Print the PDS GPIO wakeup configuration and the pad levels PDS currently sees (IPRO7 only).

Applies the pending GPIO arming to the hardware first (as the next PDS entry would), then prints the PDS GPIO registers and wakeup-source enables. Does not enter sleep. Intended for debugging a GPIO wakeup that does not trigger.

### pm_pds_gpio_wakeup_source { #pm_pds_gpio_wakeup_source }

```c
int pm_pds_gpio_wakeup_source(void);
```

Get the GPIO that woke the chip from PDS (IPRO7 only).

Call it after the wake-up and before the next PDS entry.

**Returns:** The lowest armed GPIO number whose PDS wakeup event is pending, or -1 if the wake-up was not caused by an armed GPIO.

### pm_pds_rtc_target_override_set { #pm_pds_rtc_target_override_set }

```c
void pm_pds_rtc_target_override_set(uint64_t target_ticks);
```

Set an absolute RTC wake-up time for the next PDS entry (IPRO7 only).

The next [`pm_pds_mode_enter()`](#pm_pds_mode_enter) call with a non-zero sleep time arms the RTC compare at `target_ticks` instead of "now + sleep time", and consumes the setting. If the target is not in the future it is ignored and the relative sleep time is used. Use it when the deadline is already known as an absolute RTC count, so no relative time has to be derived from it.

| Parameter | Description |
|---|---|
| `target_ticks` | Absolute RTC counter value (32.768 kHz ticks); 0 clears a pending setting. |

### pm_pds_wfi_fallback_set { #pm_pds_wfi_fallback_set }

```c
void pm_pds_wfi_fallback_set(uint64_t counts);
```

Bound the WFI of the next PDS entry (IPRO7 only).

If the core is still running `counts` machine-timer counts after the WFI that enters PDS, the machine timer ends the WFI and [`pm_pds_enable()`](#pm_pds_enable) returns ([`hal_lp_enter()`](#hal_lp_enter) then reports [`HAL_LP_ERR_ENTRY_ABORTED`](#hal_lp-h-macros)). With 0 the machine-timer compare is parked and the WFI waits until PDS engages. The setting is consumed by the next [`pm_pds_enable()`](#pm_pds_enable). [`hal_lp_set_entry_guard()`](#hal_lp_set_entry_guard) sets it in microseconds.

| Parameter | Description |
|---|---|
| `counts` | Timeout in machine-timer counts (4 per microsecond on IPRO7), or 0 for no bound. |

### pm_pds_resleep { #pm_pds_resleep }

```c
void pm_pds_resleep(uint32_t sleep_time);
```

Re-enter PDS directly from the wake-up path (IPRO6 only).

Used by the IPRO6 Wi-Fi DTIM wake flow to go back to sleep without resuming the full firmware. Runs from TCM and does not return. On IPRO7 this is an empty function that returns immediately; IPRO7 resumes the firmware through [`hal_lp_enter()`](#hal_lp_enter) instead.

| Parameter | Description |
|---|---|
| `sleep_time` | Next sleep time in RTC ticks (32.768 kHz). |

### pm_hbn_mode_enter { #pm_hbn_mode_enter }

```c
void pm_hbn_mode_enter(enum pm_hbn_sleep_level hbn_level, uint32_t sleep_time);
```

Enter HBN (hibernate) sleep.

Does not return.

Everything except the always-on domain is powered down and all RAM except HBN RAM (at [`PM_HBN_LEVEL_0`](#pm_hbn_sleep_level)) is lost; the wake-up is a full boot.

| Parameter | Description |
|---|---|
| `hbn_level` | HBN level; use [`PM_HBN_LEVEL_0`](#pm_hbn_sleep_level) to keep HBN RAM. |
| `sleep_time` | Sleep time in RTC ticks (32.768 kHz). On IPRO6 the RTC compare is armed for this time (0 = no timed wakeup). On IPRO7 the value is not used and no RTC compare is armed; use [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot) for a timed hibernate. |

### pm_set_wakeup_callback { #pm_set_wakeup_callback }

```c
void pm_set_wakeup_callback(void(*wakeup_callback)(void));
```

Set the code the boot ROM jumps to after a PDS wake-up.

Without a callback, a PDS wake-up performs a normal boot. The callback runs directly after the boot ROM, before any start-up code, with the CPU freshly reset; it must not depend on XIP flash or on CPU state from before the sleep.

| Parameter | Description |
|---|---|
| `wakeup_callback` | Entry point to jump to. |

!!! note "Note"
    [`hal_lp_enter()`](#hal_lp_enter) installs its own wake-up entry on every call and clears it after the wake-up; do not combine it with this function.

### pm_clear_wakeup_callback { #pm_clear_wakeup_callback }

```c
void pm_clear_wakeup_callback(void);
```

Remove the wake-up callback; the next PDS wake-up performs a normal boot.

### pm_pds_sleep_level { #pm_pds_sleep_level }

PDS sleep levels.

[`PM_PDS_LEVEL_31`](#pm_pds_sleep_level) selects the deepest PDS level on every chip; the HAL maps it to the matching hardware configuration, so callers pass the same value on IPRO7 and IPRO6.

| Name | Value | Description |
|---|---|---|
| `PM_PDS_LEVEL_31` | `31` | Deepest PDS level: CPU, RF and Misc domains reset and clock-gated, retained RAM kept. |

### pm_hbn_sleep_level { #pm_hbn_sleep_level }

HBN (hibernate) levels.

Use [`PM_HBN_LEVEL_0`](#pm_hbn_sleep_level) when HBN RAM contents must survive; deeper levels also power down parts of the always-on domain.

| Name | Value | Description |
|---|---|---|
| `PM_HBN_LEVEL_0` |  | Always-on domain kept: HBN RAM and RTC retained. |
| `PM_HBN_LEVEL_1` |  | Also powers down the always-on core. |
| `PM_HBN_LEVEL_2` |  | As level 1; on IPRO7 the RC32K oscillator is turned off too. |

### PM_PDS_CFG_Type { #PM_PDS_CFG_Type }

PDS entry configuration passed to [`pm_pds_enable()`](#pm_pds_enable).

[`pm_pds_mode_enter()`](#pm_pds_mode_enter) fills it with the HAL defaults. [`pm_pds_enable()`](#pm_pds_enable) currently reads only `pdsLevel`, `sleepTime` and `ocramRetetion`; the other fields are kept for source compatibility and do not change the sleep.

| Field | Type | Description |
|---|---|---|
| `pdsLevel` | `uint8_t` | PDS level; must be [`PM_PDS_LEVEL_31`](#pm_pds_sleep_level). |
| `turnOffRF` | `uint8_t` | Turn off RF during sleep (not used). |
| `powerDownFlash` | `uint8_t` | Power down the flash during sleep (not used). |
| `ocramRetetion` | `uint8_t` | OCRAM retention request. Only consulted together with the BLE domain policy bit [`PM_PDS_BLE_CTLR_DOMAIN_POLICY_SAFE_OCRAM`](#hal_pm-h-macros) (builds with `CONFIG_OCRAM_NORET_SPLIT`), which then selects the conservative retention setup. |
| `turnoffPLL` | `uint8_t` | Turn off the PLL during sleep (not used). |
| `turnoffDLL` | `uint8_t` | Turn off the DLL during sleep (not used). |
| `flashContRead` | `uint8_t` | Flash continuous-read mode (not used). |
| `pdsLdoEn` | `uint8_t` | PDS LDO voltage control (not used). |
| `fastRecovery` | `uint8_t` | Fast recovery path (not used). |
| `sleepTime` | `uint32_t` | Sleep time in RTC ticks (32.768 kHz), passed to the PDS hardware configuration. The RTC wakeup itself is armed by [`pm_pds_mode_enter()`](#pm_pds_mode_enter). |
| `flashCfg` | `uint32_t *` | Flash configuration pointer (not used). |
| `ldoLevel` | `uint32_t` | LDO output voltage level (not used). |
| `preCbFun` | `void(*)(void)` | Pre-sleep callback (not used). |
| `postCbFun` | `void(*)(void)` | Post-wakeup callback (not used). |

### Macros { #hal_pm-h-macros }

| Name | Value | Description |
|---|---|---|
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_NONE` | `(0U)` | No policy: HAL defaults. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_ENABLE` | `(1U << 0)` | Apply the policy; without this bit all other bits are ignored. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_RF` | `(1U << 1)` | PDS does not gate the RF power. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_BZ` | `(1U << 2)` | Keep the radio baseband domain out of reset and clocked. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_BLE_PWR_OFF` | `(1U << 3)` | Allow the BLE core domain to power off. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_BLE_MEM_ACTIVE` | `(1U << 4)` | Keep the BLE memory out of standby. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_MISC` | `(1U << 5)` | Keep the Misc domain powered and out of reset (clock gated). |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_SAFE_OCRAM` | `(1U << 6)` | Use the conservative OCRAM retention setup (builds with `CONFIG_OCRAM_NORET_SPLIT`). |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_MISC_LIVE` | `(1U << 7)` | Keep the Misc domain powered, out of reset, clocked and not isolated. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_CLOCKS` | `(1U << 8)` | Keep the crystal, the RC32M oscillator and the core LDO running. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_GLOBAL_PWR` | `(1U << 9)` | Do not apply the global PDS power-off. |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_KEEP_ANALOG` | `(1U << 10)` | Keep AVDD14 and the system bandgap on (builds without PSRAM turn both off by default). |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_NO_SOC_RST` | `(1U << 11)` | Do not let PDS drive the SoC reset line, even with [`PM_PDS_BLE_CTLR_DOMAIN_POLICY_BLE_PWR_OFF`](#hal_pm-h-macros) (without that bit the reset is never driven). |
| `PM_PDS_BLE_CTLR_DOMAIN_POLICY_CONNECTED_BASELINE` | `(PM_PDS_BLE_CTLR_DOMAIN_POLICY_ENABLE...` | Policy for keeping a connected BLE link across PDS. |

## hal_pm_util.h { #hal_pm_util-h }

`#include "hal_pm_util.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pm_util.h))

Section attributes for code and data that must run from PDS retained RAM.

Legacy header of the PDS helper module. The helper functions it used to declare are not part of the HAL build; use [`hal_lp.h`](#hal_lp-h) and [`hal_pm.h`](#hal_pm-h) instead.

### Macros { #hal_pm_util-h-macros }

| Name | Value | Description |
|---|---|---|
| `ATTR_PDS_RAM_SECTION` | `__attribute__((section(".pds_ram_code...` | Place a function in the `.pds_ram_code` section. The section must be mapped to retained RAM by the application's linker script; the SDK linker scripts do not define it. |
| `ATTR_PDS_RAM_CONST_SECTION` | `__attribute__((section(".pds_ram_data...` | Place constant data in the `.pds_ram_data` section (same constraints as [`ATTR_PDS_RAM_SECTION`](#hal_pm_util-h-macros)). |

## hal_lp.h { #hal_lp-h }

`#include "hal_lp.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/lp_framework/ipro7/hal_lp.h))

Low-power framework (IPRO7): PDS sleep with resume, HBN fast-boot sleep, wake-up hooks and sleep timing.

[`hal_lp_enter()`](#hal_lp_enter) puts the chip into PDS level 31 and returns to the caller after the wake-up, as if the call had simply blocked: clocks, flash XIP access, PSRAM and the interrupt controller are restored before it returns. Peripherals that lose their configuration in PDS are re-initialized by the application, typically in a wake-up hook ([`hal_lp_register_wakeup_hook()`](#hal_lp_register_wakeup_hook)). [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot) instead hibernates (HBN); the wake-up is a full boot that can be recognized with [`hal_lp_is_fastboot_wakeup()`](#hal_lp_is_fastboot_wakeup).

Typical use:

```c
hal_lp_init();                       // once, after start-up

hal_lp_cfg_t cfg = { 0 };
cfg.rtc_wakeup_en = 1;
cfg.rtc_sleep_us  = 500000;          // 500 ms
hal_lp_result_t res;
int reason = hal_lp_enter(&cfg, &res);
if (reason >= 0 && (reason & HAL_LP_WAKEUP_RTC)) {
    // woke up from the RTC; res.sleep_duration_us holds the time slept
}
```

Times are in microseconds unless stated otherwise; RTC ticks are periods of the 32.768 kHz clock. See [`hal_pm.h`](#hal_pm-h) for the underlying PDS controls (GPIO wake pins, 32 kHz clock source, domain policy).

### hal_lp_set_timing_policy { #hal_lp_set_timing_policy }

```c
void hal_lp_set_timing_policy(uint32_t policy, uint32_t pds_wakeup_delay_us);
```

Set the sleep timing policy.

| Parameter | Description |
|---|---|
| `policy` | Bitwise OR of `HAL_LP_TIMING_POLICY_*` values. |
| `pds_wakeup_delay_us` | PDS wake-up latency in microseconds. Used only with [`HAL_LP_TIMING_POLICY_PDS_WAKE_DELAY_VALID`](#hal_lp-h-macros); otherwise [`HAL_LP_PDS_WAKEUP_DELAY_US`](#hal_lp-h-macros) is restored. |

### hal_lp_get_timing_policy { #hal_lp_get_timing_policy }

```c
void hal_lp_get_timing_policy(uint32_t *policy, uint32_t *pds_wakeup_delay_us);
```

Get the sleep timing policy.

| Parameter | Description |
|---|---|
| `policy` | Receives the policy bits; may be NULL. |
| `pds_wakeup_delay_us` | Receives the stored wake-up latency in microseconds; may be NULL. |

### hal_lp_us_to_rtc_cnt { #hal_lp_us_to_rtc_cnt }

```c
uint32_t hal_lp_us_to_rtc_cnt(uint64_t us);
```

Convert microseconds to RTC ticks according to the timing policy.

| Parameter | Description |
|---|---|
| `us` | Time in microseconds. |

**Returns:** RTC ticks, rounded down: exact with [`HAL_LP_TIMING_POLICY_EXACT_US_TO_RTC`](#hal_lp-h-macros), otherwise [`HAL_LP_US_TO_RTC_CNT()`](#hal_lp-h-macros). Truncated to 32 bits.

### hal_lp_get_pds_wakeup_delay_us { #hal_lp_get_pds_wakeup_delay_us }

```c
uint32_t hal_lp_get_pds_wakeup_delay_us(void);
```

Get the PDS wake-up latency currently in effect.

**Returns:** The latency set with [`hal_lp_set_timing_policy()`](#hal_lp_set_timing_policy) when [`HAL_LP_TIMING_POLICY_PDS_WAKE_DELAY_VALID`](#hal_lp-h-macros) is set, otherwise [`HAL_LP_PDS_WAKEUP_DELAY_US`](#hal_lp-h-macros), in microseconds.

### hal_lp_init { #hal_lp_init }

```c
int hal_lp_init(void);
```

Initialize the low-power framework.

Clears the framework state (including the RC32K ready flag), records the flash and PSRAM configuration needed to restore them after a wake-up, and installs the wake-up code in HBN RAM. Registered wake-up hooks are kept.

**Returns:** Always 0.

!!! note "Note"
    Call once after start-up (after [`hal_boot2_init()`](memory-boot.md#hal_boot2_init)) and before the first [`hal_lp_enter()`](#hal_lp_enter).

### hal_lp_enter { #hal_lp_enter }

```c
int hal_lp_enter(hal_lp_cfg_t *cfg, hal_lp_result_t *result);
```

Enter PDS sleep and return after the wake-up.

The call blocks until the chip wakes up. In order, it:

1. consumes the entry guard set with [`hal_lp_set_entry_guard()`](#hal_lp_set_entry_guard);
1. if `cfg` requests no GPIO wake-up and has no `gpio_cfg`, uses the configuration registered with [`hal_lp_gpio_wakeup_cfg()`](#hal_lp_gpio_wakeup_cfg) (and stores it in `cfg`);
1. calls `pre_sleep_cb`, then disables interrupts;
1. programs the GPIO wake-up pins and enters PDS level 31 with the RTC timer set to `rtc_sleep_us` minus the wake-up latency (see [`hal_lp_get_pds_wakeup_delay_us()`](#hal_lp_get_pds_wakeup_delay_us)), but at least [`HAL_LP_PDS_WAKEUP_MIN_US`](#hal_lp-h-macros);
1. after the wake-up restores clocks, flash XIP access, PSRAM and the interrupt controller, and re-enables interrupts if they were enabled on entry;
1. runs the wake-up hooks, then `post_wakeup_cb`, and fills `result`.

| Parameter | Description |
|---|---|
| `cfg` | Sleep request. Its `gpio_wakeup_en` and `gpio_cfg` fields may be updated as described above. |
| `result` | Receives the wake-up details; may be NULL. |

**Returns:** `HAL_LP_WAKEUP_*` bits of the wake-up source (0 if none was identified) on success, or a negative value:

| Return value | Description |
|---|---|
| `-1` | `cfg` is NULL. |
| `-2` | Neither `rtc_wakeup_en` nor `gpio_wakeup_en` is set. |
| `HAL_LP_ERR_ENTRY_ABORTED` | The core did not enter PDS; nothing was powered down. |

!!! note "Note"
    The RTC timer is always armed, even when `rtc_wakeup_en` is 0; for a GPIO-only wake-up set `rtc_sleep_us` to the longest acceptable sleep time.

!!! note "Note"
    [`hal_lp_init()`](#hal_lp_init) must have been called once before.

### hal_lp_set_entry_guard { #hal_lp_set_entry_guard }

```c
void hal_lp_set_entry_guard(bool abort_on_pending_irq, uint32_t entry_fallback_us);
```

Set entry safeguards for the next [`hal_lp_enter()`](#hal_lp_enter) call only.

The settings are consumed by the next [`hal_lp_enter()`](#hal_lp_enter), whatever its outcome. They are kept outside [`hal_lp_cfg_t`](#hal_lp_cfg_t) so that the layout of that structure stays unchanged for code built against earlier versions of this header.

| Parameter | Description |
|---|---|
| `abort_on_pending_irq` | true: return [`HAL_LP_ERR_ENTRY_ABORTED`](#hal_lp-h-macros) instead of entering PDS while an enabled interrupt other than the machine timer is pending. |
| `entry_fallback_us` | Non-zero: if the core is still running this many microseconds after the WFI that enters PDS, [`hal_lp_enter()`](#hal_lp_enter) returns [`HAL_LP_ERR_ENTRY_ABORTED`](#hal_lp-h-macros). 0: wait until PDS engages. |

### hal_lp_enter_fastboot { #hal_lp_enter_fastboot }

```c
int hal_lp_enter_fastboot(hal_lp_cfg_t *cfg);
```

Hibernate (HBN level 0); the wake-up is a full boot.

All RAM except the 4 KB HBN RAM is lost. Before entering HBN the function calls `pre_sleep_cb`, saves the boot parameters to HBN RAM (so that the next boot can use them), fills the wake context ([`hal_hbnram_lp_wake_ctx_t`](platform.md#hal_hbnram_lp_wake_ctx_t): requested wake-up sources, RTC count, wake counter), sets [`BOOT_FLAG_LP_FASTBOOT`](platform.md#hal_hbnram_mgnt-h-macros) and arms the RTC timer for `rtc_sleep_us` (with the same minimum and latency handling as [`hal_lp_enter()`](#hal_lp_enter)). Everything the application needs after the wake-up must be stored in HBN RAM before this call, for example in `hal_hbnram_lp_wake_ctx_t::reserved`.

After the wake-up, the firmware detects it with [`hal_lp_is_fastboot_wakeup()`](#hal_lp_is_fastboot_wakeup) and reads the context with [`hal_lp_get_wake_context()`](#hal_lp_get_wake_context).

| Parameter | Description |
|---|---|
| `cfg` | Sleep request. Only `rtc_wakeup_en`, `rtc_sleep_us`, `gpio_wakeup_en` and `pre_sleep_cb` are used; the retention options do not apply. As in [`hal_lp_enter()`](#hal_lp_enter), a configuration registered with [`hal_lp_gpio_wakeup_cfg()`](#hal_lp_gpio_wakeup_cfg) may be stored in it. |

**Returns:** Does not return on success.

| Return value | Description |
|---|---|
| `-1` | `cfg` is NULL. |
| `-2` | Neither `rtc_wakeup_en` nor `gpio_wakeup_en` is set. |

!!! note "Note"
    Only the RTC timer is armed as a wake-up source; GPIO pins are not armed.

### hal_lp_is_fastboot_wakeup { #hal_lp_is_fastboot_wakeup }

```c
bool hal_lp_is_fastboot_wakeup(void);
```

Check whether this boot is a wake-up from [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot).

Checks the wake-context magic and [`BOOT_FLAG_LP_FASTBOOT`](platform.md#hal_hbnram_mgnt-h-macros), and clears the flag, so only the first call after such a wake-up returns true. Safe to call early in main().

**Returns:** true if this boot resumed from [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot), false otherwise.

### hal_lp_get_wake_context { #hal_lp_get_wake_context }

```c
const volatile hal_hbnram_lp_wake_ctx_t * hal_lp_get_wake_context(void);
```

Get the wake context written by [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot).

The contents are meaningful when [`hal_lp_is_fastboot_wakeup()`](#hal_lp_is_fastboot_wakeup) has returned true (or `hal_hbnram_lp_wake_ctx_t::magic` is [`HAL_HBNRAM_LP_WAKE_CTX_MAGIC`](platform.md#hal_hbnram_mgnt-h-macros)).

**Returns:** Pointer to the context in HBN RAM; never NULL.

### hal_lp_gpio_wakeup_cfg { #hal_lp_gpio_wakeup_cfg }

```c
int hal_lp_gpio_wakeup_cfg(hal_lp_gpio_cfg_t *cfg);
```

Register a default GPIO wake-up configuration.

[`hal_lp_enter()`](#hal_lp_enter) and [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot) use it when the request passed to them has `gpio_wakeup_en` = 0 and `gpio_cfg` = NULL. Only the pointer is stored, so the configuration must stay valid; NULL removes it.

| Parameter | Description |
|---|---|
| `cfg` | GPIO wake-up configuration, or NULL. |

**Returns:** Always 0.

!!! note "Note"
    See the note at [`hal_lp_gpio_cfg_t`](#hal_lp_gpio_cfg_t) about arming the pins with [`pm_pds_gpio_wakeup_set()`](#pm_pds_gpio_wakeup_set).

### hal_lp_get_wakeup_reason { #hal_lp_get_wakeup_reason }

```c
int hal_lp_get_wakeup_reason(void);
```

Get the wake-up reason of the last [`hal_lp_enter()`](#hal_lp_enter) sleep.

**Returns:** `HAL_LP_WAKEUP_*` bits; [`HAL_LP_WAKEUP_UNKNOWN`](#hal_lp-h-macros) (0) if no source was identified.

### hal_lp_get_wakeup_gpio { #hal_lp_get_wakeup_gpio }

```c
uint32_t hal_lp_get_wakeup_gpio(void);
```

Get the GPIO bits of the last wake-up.

**Returns:** GPIO wake bits; always 0 on IPRO7. Use [`pm_pds_gpio_wakeup_source()`](#pm_pds_gpio_wakeup_source) to find the pin.

### hal_lp_register_wakeup_hook { #hal_lp_register_wakeup_hook }

```c
int hal_lp_register_wakeup_hook(hal_lp_wakeup_hook_t hook, void *arg);
```

Register a wake-up hook.

Hooks are called in registration order. Up to 8 hooks can be registered; registering a hook that is already registered only replaces its argument.

| Parameter | Description |
|---|---|
| `hook` | Hook function. |
| `arg` | User argument passed to `hook`. |

| Return value | Description |
|---|---|
| `0` | Registered (or argument updated). |
| `-1` | `hook` is NULL. |
| `-2` | The hook table is full. |

!!! note "Note"
    Not thread-safe; register hooks during initialization.

### hal_lp_unregister_wakeup_hook { #hal_lp_unregister_wakeup_hook }

```c
int hal_lp_unregister_wakeup_hook(hal_lp_wakeup_hook_t hook);
```

Unregister a wake-up hook.

| Parameter | Description |
|---|---|
| `hook` | Hook function to remove. |

| Return value | Description |
|---|---|
| `0` | Removed. |
| `-1` | `hook` is NULL or not registered. |

### hal_lp_wakeup_hook_count { #hal_lp_wakeup_hook_count }

```c
uint32_t hal_lp_wakeup_hook_count(void);
```

Get the number of registered wake-up hooks.

Hooks run after every [`hal_lp_enter()`](#hal_lp_enter) wake-up, whichever component requested the sleep.

**Returns:** Number of registered hooks.

### hal_lp_get_virtual_us { #hal_lp_get_virtual_us }

```c
uint64_t hal_lp_get_virtual_us(void);
```

Get a time stamp that keeps counting during sleep, in microseconds.

Derived from the always-on RTC counter (32.768 kHz, about 30.5 us resolution), which keeps running in PDS. Its accuracy is that of the selected 32 kHz clock. The count restarts when the RTC counter is cleared (power-on reset, [`rtc_init()`](platform.md#rtc_init)).

**Returns:** Time in microseconds.

### hal_lp_get_virtual_ms { #hal_lp_get_virtual_ms }

```c
uint64_t hal_lp_get_virtual_ms(void);
```

Get the time stamp of [`hal_lp_get_virtual_us()`](#hal_lp_get_virtual_us) in milliseconds.

**Returns:** Time in milliseconds.

### hal_lp_rtc_clk_sel { #hal_lp_rtc_clk_sel }

```c
void hal_lp_rtc_clk_sel(bool use_xtal32k);
```

Select the clock source of the RTC and the sleep timer.

Only switches the selection; the 32.768 kHz crystal must already be running ([`pm_pds_set_32k_src()`](#pm_pds_set_32k_src) powers it up and also records the choice for later PDS entries).

| Parameter | Description |
|---|---|
| `use_xtal32k` | true for the 32.768 kHz crystal, false for the RC32K oscillator. |

!!! note "Note"
    Selecting the RC32K oscillator re-applies its factory trim, discarding a run-time calibration.

### hal_lp_rc32k_coarse_adj { #hal_lp_rc32k_coarse_adj }

```c
int hal_lp_rc32k_coarse_adj(uint32_t expect_time, uint32_t actual_time);
```

Apply a coarse frequency correction to the RC32K oscillator.

Adjusts the oscillator in proportion to the relative error `(actual_time - expect_time) / expect_time`, measured by the caller over the same interval with a reference clock and with the RC32K clock.

| Parameter | Description |
|---|---|
| `expect_time` | Interval length according to the reference clock. |
| `actual_time` | Interval length according to the RC32K clock, in the same unit (for example microseconds). |

| Return value | Description |
|---|---|
| `0` | Correction applied (or none needed). |
| `-1` | The RC32K clock is already marked ready ([`hal_lp_set_rc32k_ready()`](#hal_lp_set_rc32k_ready)); nothing changed. |
| `-2` | `expect_time` or `actual_time` is 0. |

### hal_lp_set_rc32k_ready { #hal_lp_set_rc32k_ready }

```c
void hal_lp_set_rc32k_ready(uint8_t ready);
```

Mark the RC32K calibration as complete or not.

While marked ready, [`hal_lp_rc32k_coarse_adj()`](#hal_lp_rc32k_coarse_adj) makes no further changes. The flag is cleared by [`hal_lp_init()`](#hal_lp_init).

| Parameter | Description |
|---|---|
| `ready` | 1 = ready, 0 = not ready. |

### hal_lp_get_rc32k_ready { #hal_lp_get_rc32k_ready }

```c
uint8_t hal_lp_get_rc32k_ready(void);
```

Get the RC32K ready flag set with [`hal_lp_set_rc32k_ready()`](#hal_lp_set_rc32k_ready).

**Returns:** 1 if ready, 0 if not.

### hal_lp_xip_recovery { #hal_lp_xip_recovery }

```c
void hal_lp_xip_recovery(void);
```

Restore flash XIP access after a PDS wake-up.

Called automatically on the [`hal_lp_enter()`](#hal_lp_enter) wake-up path; only custom wake-up code that runs before that point needs to call it. Does nothing unless a recovery is pending and [`hal_lp_init()`](#hal_lp_init) has recorded the flash configuration.

!!! note "Note"
    Runs from TCM; it must be called before any code or data in XIP flash is accessed after the wake-up.

### hal_lp_get_psram_dqs_cfg { #hal_lp_get_psram_dqs_cfg }

```c
uint16_t hal_lp_get_psram_dqs_cfg(void);
```

Get the PSRAM calibration value that [`hal_lp_init()`](#hal_lp_init) records for the wake-up path.

Weak function: the default returns 0 (no PSRAM). Builds with `CONFIG_USE_PSRAM` provide the calibrated value (see [`hal_psram.h`](memory-boot.md#hal_psram-h)).

**Returns:** PSRAM DQS configuration, or 0 when there is no PSRAM.

### hal_lp_psram_restore { #hal_lp_psram_restore }

```c
void hal_lp_psram_restore(void);
```

Re-initialize the PSRAM after a PDS wake-up.

Called automatically by the framework when a PSRAM configuration was recorded ([`hal_lp_get_psram_dqs_cfg()`](#hal_lp_get_psram_dqs_cfg) returned non-zero), both after a wake-up and after an aborted entry. Weak function: the default does nothing; builds with `CONFIG_USE_PSRAM` provide the implementation.

### hal_lp_gpio_trig_t { #hal_lp_gpio_trig_t }

GPIO wake-up trigger mode.

| Name | Value | Description |
|---|---|---|
| `HAL_LP_GPIO_TRIG_FALLING_EDGE` | `0` | Falling edge. |
| `HAL_LP_GPIO_TRIG_RISING_EDGE` |  | Rising edge. |
| `HAL_LP_GPIO_TRIG_LOW_LEVEL` |  | Low level. |
| `HAL_LP_GPIO_TRIG_HIGH_LEVEL` |  | High level. |
| `HAL_LP_GPIO_TRIG_BOTH_EDGE` |  | Rising and falling edge. |
| `HAL_LP_GPIO_TRIG_NONE` | `0xF` | No trigger; the IPRO7 implementation treats it as falling edge. |

### hal_lp_gpio_res_t { #hal_lp_gpio_res_t }

GPIO pull resistor for wake-up pins.

| Name | Value | Description |
|---|---|---|
| `HAL_LP_GPIO_RES_NONE` | `0` | No pull resistor. |
| `HAL_LP_GPIO_RES_PULL_UP` |  | Pull-up. |
| `HAL_LP_GPIO_RES_PULL_DOWN` |  | Pull-down. |

### hal_lp_gpio_pin_cfg_t { #hal_lp_gpio_pin_cfg_t }

Per-pin GPIO wake-up configuration.

!!! note "Note"
    Not used by the IPRO7 implementation: all pins in `hal_lp_gpio_cfg_t::wakeup_mask` use the default trigger and pull.

| Field | Type | Description |
|---|---|---|
| `pin` | `uint8_t` | GPIO number. |
| `enable` | `uint8_t` | Non-zero to enable wake-up on this pin. |
| `trig_mode` | `hal_lp_gpio_trig_t` | Trigger mode. |
| `res_mode` | `hal_lp_gpio_res_t` | Pull resistor. |

### hal_lp_gpio_cfg_t { #hal_lp_gpio_cfg_t }

GPIO wake-up configuration for [`hal_lp_enter()`](#hal_lp_enter).

Each pin in `wakeup_mask` is configured as an input with `default_res` and unmasked as a PDS wake-up pin; the trigger mode is programmed for the pin groups GPIO0-3, GPIO4-7 and GPIO8-9.

!!! note "Note"
    On IPRO7 the PDS GPIO wake-up source itself is enabled only for pins armed with [`pm_pds_gpio_wakeup_set()`](#pm_pds_gpio_wakeup_set) ([`hal_pm.h`](#hal_pm-h)). Arm the wake-up pins there; that function also covers GPIO20 to GPIO41.

| Field | Type | Description |
|---|---|---|
| `wakeup_mask` | `uint32_t` | Bit n set = GPIO n can wake the chip. |
| `default_trig` | `hal_lp_gpio_trig_t` | Trigger mode for all pins. |
| `default_res` | `hal_lp_gpio_res_t` | Pull resistor for all pins. |
| `pin_cfg` | `hal_lp_gpio_pin_cfg_t *` | Per-pin settings; not used on IPRO7. |
| `pin_cfg_count` | `uint8_t` | Number of entries in `pin_cfg`. |

### hal_lp_cfg_t { #hal_lp_cfg_t }

Sleep request for [`hal_lp_enter()`](#hal_lp_enter) and [`hal_lp_enter_fastboot()`](#hal_lp_enter_fastboot).

Zero-initialize the structure and set the fields you need.

| Field | Type | Description |
|---|---|---|
| `rtc_wakeup_en` | `uint8_t` | Request the RTC wake-up. The RTC timer is armed for `rtc_sleep_us` in any case (see [`hal_lp_enter()`](#hal_lp_enter)). |
| `rtc_sleep_us` | `uint64_t` | Sleep time in microseconds; must be below 2^32 RTC ticks (about 36 hours). |
| `gpio_wakeup_en` | `uint8_t` | Request GPIO wake-up with `gpio_cfg`. |
| `gpio_cfg` | `hal_lp_gpio_cfg_t *` | GPIO wake-up configuration, or NULL. |
| `flash_power_down` | `uint8_t` | Not used by the IPRO7 implementation. |
| `psram_retention` | `uint8_t` | Not used by the IPRO7 implementation; in builds with PSRAM its contents are always kept in self-refresh during PDS. |
| `ocram_retention` | `uint8_t` | Not used by the IPRO7 implementation. |
| `pre_sleep_cb` | `hal_lp_callback_t` | Called before the sleep, before interrupts are disabled; may be NULL. |
| `pre_sleep_arg` | `void *` | Argument for `pre_sleep_cb`. |
| `post_wakeup_cb` | `hal_lp_callback_t` | Called after the wake-up, after the wake-up hooks; may be NULL. |
| `post_wakeup_arg` | `void *` | Argument for `post_wakeup_cb`. |

### hal_lp_result_t { #hal_lp_result_t }

Result of [`hal_lp_enter()`](#hal_lp_enter).

| Field | Type | Description |
|---|---|---|
| `wakeup_reason` | `int32_t` | `HAL_LP_WAKEUP_*` bits, same as the return value of [`hal_lp_enter()`](#hal_lp_enter). |
| `wakeup_gpio_bits` | `uint32_t` | GPIO wake bits; always 0 on IPRO7 (use [`pm_pds_gpio_wakeup_source()`](#pm_pds_gpio_wakeup_source)). |
| `sleep_duration_us` | `uint64_t` | Time spent in sleep, measured with the RTC, in microseconds. If the RTC was reset during the sleep, the requested time is reported. |

### Typedefs { #hal_lp-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `hal_lp_callback_t` | `typedef int(*) hal_lp_callback_t(void *arg)` | Sleep callback type used by [`hal_lp_cfg_t`](#hal_lp_cfg_t). |
| `hal_lp_wakeup_hook_t` | `typedef int(*) hal_lp_wakeup_hook_t(int wakeup_reason, void *arg)` | Wake-up hook type. Hooks run after every wake-up from [`hal_lp_enter()`](#hal_lp_enter), after the system has been restored and interrupts have been re-enabled (if they were enabled on entry), before `post_wakeup_cb`. Use them to re-initialize peripherals that lose their configuration in PDS. |

### Macros { #hal_lp-h-macros }

| Name | Value | Description |
|---|---|---|
| `HAL_LP_WAKEUP_UNKNOWN` | `0` | No wake-up source identified. |
| `HAL_LP_WAKEUP_RTC` | `(1 << 0)` | RTC timer. |
| `HAL_LP_WAKEUP_GPIO` | `(1 << 1)` | GPIO; see [`pm_pds_gpio_wakeup_source()`](#pm_pds_gpio_wakeup_source) for the pin. |
| `HAL_LP_WAKEUP_ACOMP` | `(1 << 2)` | Analog comparator; not reported by the IPRO7 implementation. |
| `HAL_LP_WAKEUP_BLE` | `(1 << 3)` | BLE controller sleep timer. |
| `HAL_LP_TIMING_POLICY_NONE` | `(0U)` | Use the defaults. |
| `HAL_LP_TIMING_POLICY_EXACT_US_TO_RTC` | `(1U << 0)` | [`hal_lp_us_to_rtc_cnt()`](#hal_lp_us_to_rtc_cnt) uses the exact conversion instead of [`HAL_LP_US_TO_RTC_CNT()`](#hal_lp-h-macros). |
| `HAL_LP_TIMING_POLICY_PDS_WAKE_DELAY_VALID` | `(1U << 1)` | Use the wake-up latency passed to [`hal_lp_set_timing_policy()`](#hal_lp_set_timing_policy) instead of [`HAL_LP_PDS_WAKEUP_DELAY_US`](#hal_lp-h-macros). |
| `HAL_LP_US_TO_RTC_CNT(us)` | `(((uint64_t)(us) * 67) >> 11)` | Convert microseconds to RTC ticks (fast approximation). Computes `us * 67 / 2048`, about 0.16 % less than the exact value. |
| `HAL_LP_MS_TO_RTC_CNT(ms)` | `(((uint64_t)(ms) * 33554) >> 10)` | Convert milliseconds to RTC ticks (fast approximation). Computes `ms * 33554 / 1024`, less than 0.01 % below the exact value. |
| `HAL_LP_RTC_CNT_TO_US(cnt)` | `(((uint64_t)(cnt) * 1000000) >> 15)` | Convert RTC ticks to microseconds (exact, rounded down). |
| `HAL_LP_RTC_CNT_TO_MS(cnt)` | `(((uint64_t)(cnt) * 1000) >> 15)` | Convert RTC ticks to milliseconds (exact, rounded down). |
| `HAL_LP_ERR_ENTRY_ABORTED` | `(-3)` | [`hal_lp_enter()`](#hal_lp_enter) result: the core did not enter PDS, because an enabled interrupt was already pending or the entry timeout set with [`hal_lp_set_entry_guard()`](#hal_lp_set_entry_guard) expired. Nothing was powered down; the caller continues as after a plain WFI. |
| `HAL_LP_PDS_WAKEUP_MIN_US` | `1220` | Shortest sleep time [`hal_lp_enter()`](#hal_lp_enter) programs, in microseconds; shorter requests are extended to this value. |
| `HAL_LP_PDS_WAKEUP_DELAY_US` | `300` | Default PDS wake-up latency in microseconds. [`hal_lp_enter()`](#hal_lp_enter) subtracts the wake-up latency from the requested sleep time so that execution resumes close to the requested time. |
| `HAL_LP_MAX_WAKEUP_GPIO` | `32` | Number of GPIOs `hal_lp_gpio_cfg_t::wakeup_mask` can address (GPIO0 to GPIO31). |

## lp_uart.h { #lp_uart-h }

`#include "lp_uart.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/lp_framework/ipro7/lp_uart.h))

Minimal polled UART output for low-power wake-up code.

Debug output for code that runs while the chip wakes up from sleep, before the normal UART driver and XIP flash are available. The functions run from TCM and busy-wait on the UART transmit FIFO; they do not use interrupts or DMA. String arguments must also be readable at that point (not in XIP flash before it has been restored).

### lp_uart_init { #lp_uart_init }

```c
void lp_uart_init(int uart_id, uint32_t baudrate);
```

Set up a UART for transmit and receive with minimal initialization.

Sets the bit period for TX and RX and enables both directions; pin multiplexing is not changed, and the UART clock is assumed to be the 32 MHz XCLK.

| Parameter | Description |
|---|---|
| `uart_id` | 0 selects UART0; any other value selects UART1. |
| `baudrate` | Baud rate in bit/s, for example 2000000. |

### lp_uart_putc { #lp_uart_putc }

```c
void lp_uart_putc(int uart_id, char c);
```

Send one character; waits until the transmit FIFO has space.

| Parameter | Description |
|---|---|
| `uart_id` | 0 selects UART0; any other value selects UART1. |
| `c` | Character to send. |

### lp_uart_puts { #lp_uart_puts }

```c
void lp_uart_puts(int uart_id, const char *str);
```

Send a NUL-terminated string; each `'\n'` is sent as CR LF.

| Parameter | Description |
|---|---|
| `uart_id` | 0 selects UART0; any other value selects UART1. |
| `str` | String to send. |

### lp_uart_puthex { #lp_uart_puthex }

```c
void lp_uart_puthex(int uart_id, uint32_t val);
```

Send a value as `0x` followed by 8 upper-case hexadecimal digits.

| Parameter | Description |
|---|---|
| `uart_id` | 0 selects UART0; any other value selects UART1. |
| `val` | Value to print. |

### lp_uart_putdec { #lp_uart_putdec }

```c
void lp_uart_putdec(int uart_id, uint32_t val);
```

Send an unsigned value in decimal, without leading zeros.

| Parameter | Description |
|---|---|
| `uart_id` | 0 selects UART0; any other value selects UART1. |
| `val` | Value to print. |

### Macros { #lp_uart-h-macros }

| Name | Value | Description |
|---|---|---|
| `lp_print(str)` | `lp_uart_puts(0, str)` | Print a string on UART0. |
| `lp_println(str)` | `do { lp_uart_puts(0, str); lp_uart_pu...` | Print a string followed by CR LF on UART0. |
| `lp_print_hex(val)` | `lp_uart_puthex(0, val)` | Print a value in hexadecimal with a `0x` prefix on UART0. |
| `lp_print_dec(val)` | `lp_uart_putdec(0, val)` | Print an unsigned value in decimal on UART0. |
| `lp_print_char(c)` | `lp_uart_putc(0, c)` | Print one character on UART0. |
| `lp_print_nl()` | `lp_uart_puts(0, "\r\n")` | Print CR LF on UART0. |
| `lp_print_reg(label, val)` | `do { \ lp_uart_puts(0, label); \ ...` | Print a labelled value on UART0 as `label: 0x12345678` followed by CR LF. |
