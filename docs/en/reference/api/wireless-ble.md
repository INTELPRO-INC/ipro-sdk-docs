---
title: Wireless & BLE Controller
description: Radio start-up and the IPRO BLE controller interfaces for bring-up, HCI transport, low power and NVDS.
generated: tools/gen_api.py
migrate_from: []
---

# Wireless & BLE Controller

Radio start-up and the IPRO BLE controller interfaces for bring-up, HCI transport, low power and NVDS.

| Header | Functions | Description |
|---|---|---|
| [`hal_wireless.h`](#hal_wireless-h) | 13 | Radio settings for BLE and IEEE 802.15.4: MAC address, default TX power, TX power offsets and the crystal capcode temperature table. |
| [`ipro_ble_controller.h`](#ipro_ble_controller-h) | 0 | BLE controller entry point: start the controller and reach its HCI transport. |
| [`ipro_ble_ctlr_arch.h`](#ipro_ble_ctlr_arch-h) | 10 | IPRO7 BLE controller start-up, task control and connected low-power windows. |
| [`ipro_ble_ctlr_hcitl.h`](#ipro_ble_ctlr_hcitl-h) | 6 | HCI byte-stream transport between the Bluetooth host and the on-chip BLE controller. |
| [`ipro_ble_ctlr_lowpower.h`](#ipro_ble_ctlr_lowpower-h) | 2 | IPRO7 BLE controller sleep clock: 32 kHz source qualification and drift bound. |
| [`ipro_ble_ctlr_pds_snapshot.h`](#ipro_ble_ctlr_pds_snapshot-h) | 8 | IPRO7 BLE controller connected platform PDS: enable, policy modes and window grants. |
| [`ipro_ble_ctlr_nvds.h`](#ipro_ble_ctlr_nvds-h) | 2 | IPRO7 BLE controller parameters: Bluetooth device address and clock accuracy. |

## hal_wireless.h { #hal_wireless-h }

`#include "hal_wireless.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_wireless.h))

Radio settings for BLE and IEEE 802.15.4: MAC address, default TX power, TX power offsets and the crystal capcode temperature table.

The values live in one RAM structure inside the HAL (all zero at start-up) and are returned unchanged by the matching `_get` function. Of these settings, the BLE controller reads the default TX power, at RF initialization and whenever the host gives no TX power preference, so call [`hal_wireless_default_tx_power_set()`](#hal_wireless_default_tx_power_set) before initializing the BLE controller. The functions do no locking; set the values during initialization.

### hal_wireless_mac_addr_set { #hal_wireless_mac_addr_set }

```c
int hal_wireless_mac_addr_set(uint8_t mac[8]);
```

Store the radio MAC address.

| Parameter | Description |
|---|---|
| `mac` | 8-byte address, copied as is. |

**Returns:** 0 (always).

!!! note "Note"
    This call only records the value in the HAL; it does not program the radio.

### hal_wireless_mac_addr_get { #hal_wireless_mac_addr_get }

```c
int hal_wireless_mac_addr_get(uint8_t mac[8]);
```

Read the stored radio MAC address.

| Parameter | Description |
|---|---|
| `mac` | Receives the 8 stored bytes (all zero if never set). |

**Returns:** 0 (always).

### hal_wireless_power_offset_set { #hal_wireless_power_offset_set }

```c
int hal_wireless_power_offset_set(int8_t poweroffset_zigbee[16], int8_t poweroffset_ble[4]);
```

Store the TX power offset tables.

| Parameter | Description |
|---|---|
| `poweroffset_zigbee` | 16 signed IEEE 802.15.4 TX power offsets. |
| `poweroffset_ble` | 4 signed BLE TX power offsets. |

**Returns:** 0 (always).

!!! note "Note"
    This call only records the value in the HAL; it does not program the radio.

### hal_wireless_power_offset_get { #hal_wireless_power_offset_get }

```c
int hal_wireless_power_offset_get(int8_t poweroffset_zigbee[16], int8_t poweroffset_ble[4]);
```

Read the stored TX power offset tables.

| Parameter | Description |
|---|---|
| `poweroffset_zigbee` | Receives the 16 IEEE 802.15.4 offsets. |
| `poweroffset_ble` | Receives the 4 BLE offsets. |

**Returns:** 0 (always).

### hal_wireless_capcode_offset_table_set { #hal_wireless_capcode_offset_table_set }

```c
int hal_wireless_capcode_offset_table_set(int8_t temp[], int8_t offset[], uint8_t size);
```

Store the crystal capcode offset table indexed by temperature.

Entry i applies from temperature `temp[i]` up to, but not including, `temp[i + 1]`; see [`hal_wireless_capcode_offset_get()`](#hal_wireless_capcode_offset_get).

| Parameter | Description |
|---|---|
| `temp` | `size` temperature thresholds, in ascending order. |
| `offset` | `size` capcode offsets, one per threshold. |
| `size` | Number of entries, at most [`MAX_CAPCODE_TABLE_SIZE`](#hal_wireless-h-macros). |

| Return value | Description |
|---|---|
| `0` | Table stored. |
| `-1` | `size` is larger than [`MAX_CAPCODE_TABLE_SIZE`](#hal_wireless-h-macros); nothing stored. |

!!! note "Note"
    This call only records the value in the HAL; it does not program the radio.

### hal_wireless_capcode_offset_table_get { #hal_wireless_capcode_offset_table_get }

```c
int hal_wireless_capcode_offset_table_get(int8_t temp[], int8_t offset[], uint8_t *size);
```

Read the stored capcode offset table.

| Parameter | Description |
|---|---|
| `temp` | Receives the temperature thresholds; room for [`MAX_CAPCODE_TABLE_SIZE`](#hal_wireless-h-macros) entries is always enough. |
| `offset` | Receives the capcode offsets; same size as `temp`. |
| `size` | Number of entries copied (0 if no table was stored). |

**Returns:** 0 (always).

### hal_wireless_capcode_offset_get { #hal_wireless_capcode_offset_get }

```c
int8_t hal_wireless_capcode_offset_get(int8_t temp);
```

Look up the capcode offset for a temperature.

With T the stored thresholds, returns the stored offset i - 1 for the first i (from 1) with `temp` below T[i], otherwise the last stored offset. A temperature below the second threshold therefore gets the first offset.

| Parameter | Description |
|---|---|
| `temp` | Temperature, in the unit used for the table thresholds. |

**Returns:** Capcode offset from the stored table; the first stored offset when the table has fewer than two entries (0 if no table was ever stored).

### hal_wireless_default_tx_power_set { #hal_wireless_default_tx_power_set }

```c
void hal_wireless_default_tx_power_set(int8_t power);
```

Set the default (maximum) radio TX power.

The BLE controller reads this value at RF initialization and as the TX power of activities for which the host gives no preference. The IPRO7 BLE controller supports -9 to +10 dBm; the value is not range-checked here.

| Parameter | Description |
|---|---|
| `power` | TX power in dBm. |

### hal_wireless_default_tx_power_get { #hal_wireless_default_tx_power_get }

```c
int8_t hal_wireless_default_tx_power_get(void);
```

Read the default radio TX power.

**Returns:** TX power in dBm (0 if never set).

### hal_wireless_power_tcal_en_set { #hal_wireless_power_tcal_en_set }

```c
void hal_wireless_power_tcal_en_set(uint8_t en);
```

Store the enable flag of TX power temperature calibration.

| Parameter | Description |
|---|---|
| `en` | Non-zero to enable, 0 to disable. |

!!! note "Note"
    This call only records the value in the HAL; it does not program the radio.

### hal_wireless_power_tcal_en_get { #hal_wireless_power_tcal_en_get }

```c
uint8_t hal_wireless_power_tcal_en_get(void);
```

Read the stored TX power temperature calibration flag.

**Returns:** The value last passed to [`hal_wireless_power_tcal_en_set()`](#hal_wireless_power_tcal_en_set) (0 if never set).

### hal_wireless_capcode_tcal_en_set { #hal_wireless_capcode_tcal_en_set }

```c
void hal_wireless_capcode_tcal_en_set(uint8_t en);
```

Store the enable flag of capcode temperature calibration.

| Parameter | Description |
|---|---|
| `en` | Non-zero to enable, 0 to disable. |

!!! note "Note"
    This call only records the value in the HAL; it does not program the radio.

### hal_wireless_capcode_tcal_en_get { #hal_wireless_capcode_tcal_en_get }

```c
uint8_t hal_wireless_capcode_tcal_en_get(void);
```

Read the stored capcode temperature calibration flag.

**Returns:** The value last passed to [`hal_wireless_capcode_tcal_en_set()`](#hal_wireless_capcode_tcal_en_set) (0 if never set).

### Macros { #hal_wireless-h-macros }

| Name | Value | Description |
|---|---|---|
| `MAX_CAPCODE_TABLE_SIZE` | `30` | Maximum number of entries in the capcode temperature table. |

## ipro_ble_controller.h { #ipro_ble_controller-h }

`#include "ipro_ble_controller.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/wireless/bluetooth/ipro_ble_controller/include/ipro_ble_controller.h))

BLE controller entry point: start the controller and reach its HCI transport.

The BLE controller is delivered as a prebuilt library. It runs in its own FreeRTOS task and exchanges standard H4 HCI packets with the Bluetooth host through an in-memory byte stream, the same packets a UART HCI link would carry.

Include this header instead of a platform directory. On IPRO7 it provides [`ipro_ble_ctlr_arch.h`](#ipro_ble_ctlr_arch-h) (controller start-up and task control) and [`ipro_ble_ctlr_hcitl.h`](#ipro_ble_ctlr_hcitl-h) (the HCI byte-stream transport). IPRO6S builds (`CONFIG_BTDM_ENABLE` or `CONFIG_IPRO6`) get the `btdm_sdk.h` compatibility API together with the same HCI transport header.

Typical IPRO7 bring-up with the bundled Bluetooth host:

1. [`ipro_platform_init()`](platform.md#ipro_platform_init) ([`freertos_app_hooks.h`](platform.md#freertos_app_hooks-h)), create the application task and start the scheduler.
1. [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init) with a priority above the application tasks, or `ipro_pm_ble_controller_init()` (ipro_pm_ble.h) when the power manager should also run connected platform PDS.
1. `hci_driver_ipro_ble_ctlr_init()` and `bt_enable()` to start the host.
1. Once `bt_enable()` reports ready, [`ipro_ble_ctlr_hcitl_host_ready()`](#ipro_ble_ctlr_hcitl_host_ready). Until then the controller keeps the BLE core awake.

Further IPRO7 headers: [`ipro_ble_ctlr_lowpower.h`](#ipro_ble_ctlr_lowpower-h) (32 kHz sleep clock), [`ipro_ble_ctlr_pds_snapshot.h`](#ipro_ble_ctlr_pds_snapshot-h) (connected platform PDS) and [`ipro_ble_ctlr_nvds.h`](#ipro_ble_ctlr_nvds-h) (device address).

## ipro_ble_ctlr_arch.h { #ipro_ble_ctlr_arch-h }

`#include "ipro_ble_ctlr_arch.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/wireless/bluetooth/ipro_ble_controller/plf/ipro7/arch/main/ipro_ble_ctlr_arch.h))

IPRO7 BLE controller start-up, task control and connected low-power windows.

[`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init) brings the controller up and creates its FreeRTOS task. The task blocks whenever it has nothing to do and is woken by the BLE interrupt and by [`ipro_ble_ctlr_ctrl_notify()`](#ipro_ble_ctlr_ctrl_notify), which the HCI transport ([`ipro_ble_ctlr_hcitl.h`](#ipro_ble_ctlr_hcitl-h)) calls when the host sends bytes or makes room for the controller's output.

For connected platform PDS, the controller also publishes after each connection event the idle window until the next radio event (ipro_ble_ctlr_pds_candidate_token, ipro_ble_ctlr_pds_candidate_slack_hus, ipro_ble_ctlr_pds_full_generation). An RTOS idle policy checks a window with [`ipro_ble_ctlr_pds_candidate_revalidate()`](#ipro_ble_ctlr_pds_candidate_revalidate) and grants it with [`ipro_ble_ctlr_pds_tickless_grant()`](#ipro_ble_ctlr_pds_tickless_grant) ([`ipro_ble_ctlr_pds_snapshot.h`](#ipro_ble_ctlr_pds_snapshot-h)). The ipro_pm power manager implements such a policy; see [`ipro_ble_ctlr_pds_snapshot.h`](#ipro_ble_ctlr_pds_snapshot-h) for the full sequence.

Time values with the suffix `_hus` are in half-microseconds (units of 0.5 us).

### ipro_ble_ctlr_controller_init { #ipro_ble_ctlr_controller_init }

```c
int ipro_ble_ctlr_controller_init(unsigned int task_priority);
```

Start the BLE controller.

Enables the BLE clock, resets the BLE core, qualifies the 32 kHz sleep clock ([`ipro_ble_ctlr_lowpower_init()`](#ipro_ble_ctlr_lowpower_init)), prepares the HCI transport, loads the device address and clock accuracies ([`ipro_ble_ctlr_nvds_init()`](#ipro_ble_ctlr_nvds_init)), initializes the controller, creates the controller task and finally enables the BLE interrupt. The FreeRTOS scheduler does not have to be running yet. Call it once.

| Parameter | Description |
|---|---|
| `task_priority` | FreeRTOS priority of the controller task. The controller has hard radio deadlines, so use a priority above the application tasks (the SDK examples use `configMAX_PRIORITIES - 1`). |

| Return value | Description |
|---|---|
| `0` | Controller started. |
| `-1` | The controller was already started. |
| `-2` | The controller task could not be created. |

!!! note "Note"
    Blocks for more than a second while the sleep clock is qualified (crystal settling, RC32K calibration and a one-second accuracy measurement, depending on the board).

!!! note "Note"
    With the power manager, call `ipro_pm_ble_controller_init()` (ipro_pm_ble.h) instead: it calls this function and sets up connected PDS.

### ipro_ble_ctlr_ctrl_notify { #ipro_ble_ctlr_ctrl_notify }

```c
void ipro_ble_ctlr_ctrl_notify(void);
```

Wake the controller task.

The controller task blocks while it has nothing to do. Every external event that gives it work must wake it; otherwise it sleeps until the next radio interrupt. The HCI transport functions ([`ipro_ble_ctlr_hcitl.h`](#ipro_ble_ctlr_hcitl-h)) already call this when the host sends bytes or makes room for a stalled transfer, so applications rarely need it.

Wake-ups are latched: a wake-up sent just before the task blocks is not lost.

!!! note "Note"
    Callable from a task or from an interrupt handler. Does nothing before [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init).

### ipro_ble_ctlr_controller_task_handle { #ipro_ble_ctlr_controller_task_handle }

```c
TaskHandle_t ipro_ble_ctlr_controller_task_handle(void);
```

Get the controller task handle.

An RTOS idle policy can pass it to `xTaskGetExpectedIdleTimeExcludingTask()` to look past the controller's 1 ms connection poll while a link is in the low-power profile ([`ipro_ble_ctlr_tickless_connection_active_set()`](#ipro_ble_ctlr_tickless_connection_active_set)).

**Returns:** FreeRTOS handle of the controller task, or NULL before [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init) has created it.

### ipro_ble_ctlr_controller_kick { #ipro_ble_ctlr_controller_kick }

```c
void ipro_ble_ctlr_controller_kick(void);
```

Wake the controller task from task context.

Same as [`ipro_ble_ctlr_ctrl_notify()`](#ipro_ble_ctlr_ctrl_notify) for callers that are known to run in a task. Does nothing before [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init).

### ipro_ble_ctlr_tickless_connection_active_set { #ipro_ble_ctlr_tickless_connection_active_set }

```c
void ipro_ble_ctlr_tickless_connection_active_set(bool active);
```

Mark whether the current connection uses the connected low-power (PDS) profile.

While set, the controller publishes after each connection event the idle window until the next radio event (ipro_ble_ctlr_pds_candidate_slack_hus, ipro_ble_ctlr_pds_candidate_token, ipro_ble_ctlr_pds_full_generation) and polls the link every millisecond, so that an RTOS idle policy can grant the window with [`ipro_ble_ctlr_pds_tickless_grant()`](#ipro_ble_ctlr_pds_tickless_grant). Setting it also resets the window statistics. Clear it when the link leaves the profile or disconnects.

| Parameter | Description |
|---|---|
| `active` | true when the link enters the profile, false when it leaves it. |

!!! note "Note"
    ipro_pm sets and clears it automatically for applications that start the controller with `ipro_pm_ble_controller_init()`.

### ipro_ble_ctlr_tickless_connection_active_get { #ipro_ble_ctlr_tickless_connection_active_get }

```c
bool ipro_ble_ctlr_tickless_connection_active_get(void);
```

Report whether the connected low-power profile is set.

**Returns:** The value last set with [`ipro_ble_ctlr_tickless_connection_active_set()`](#ipro_ble_ctlr_tickless_connection_active_set); false after [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init).

### ipro_ble_ctlr_clock_drift_uses_active { #ipro_ble_ctlr_clock_drift_uses_active }

```c
bool ipro_ble_ctlr_clock_drift_uses_active(void);
```

Report whether receive windows are sized with the active-clock accuracy only.

**Returns:** true when neither the controller's own BLE-core deep sleep nor the platform sleep-drift mode ([`ipro_ble_ctlr_platform_sleep_drift_enable()`](#ipro_ble_ctlr_platform_sleep_drift_enable)) is enabled, so the controller times connection events with the accuracy of the 32 MHz crystal.

### ipro_ble_ctlr_platform_sleep_drift_enable { #ipro_ble_ctlr_platform_sleep_drift_enable }

```c
void ipro_ble_ctlr_platform_sleep_drift_enable(bool enable);
```

Use the sleep-clock accuracy for the receive windows after a platform PDS.

When enabled, the receive windows that follow a platform PDS, until the link has re-synchronized, are widened for the 32 kHz sleep-clock accuracy ([`ipro_ble_ctlr_lowpower_sleep_drift_ppm_get()`](#ipro_ble_ctlr_lowpower_sleep_drift_ppm_get)), and never for less than the floor set with [`ipro_ble_ctlr_platform_sleep_drift_floor_set()`](#ipro_ble_ctlr_platform_sleep_drift_floor_set). Ordinary connection events keep the active-clock accuracy. Disabled by default; enable it when connected PDS is used.

| Parameter | Description |
|---|---|
| `enable` | true to enable, false to disable. |

!!! note "Note"
    `ipro_pm_ble_controller_init()` enables it when connected PDS is available.

### ipro_ble_ctlr_platform_sleep_drift_floor_set { #ipro_ble_ctlr_platform_sleep_drift_floor_set }

```c
void ipro_ble_ctlr_platform_sleep_drift_floor_set(uint32_t ppm);
```

Set the minimum clock drift assumed for the first receive window after a platform PDS.

| Parameter | Description |
|---|---|
| `ppm` | Floor in ppm; values above 2000 are clamped to 2000, and 0 removes the floor. The default is 1000 ppm. |

### ipro_ble_ctlr_pds_candidate_revalidate { #ipro_ble_ctlr_pds_candidate_revalidate }

```c
bool ipro_ble_ctlr_pds_candidate_revalidate(uint32_t token, uint32_t *fresh_slack_hus);
```

Check that a published idle window can still be granted and get what is left of it.

Succeeds only if `token` is still the current window identifier (ipro_ble_ctlr_pds_candidate_token), the connection is in the low-power profile, no HCI bytes are in flight and the HCI hold-off (ipro_ble_ctlr_hcitl_awake_guard_ms) has expired, the link is neither guarded nor recovering from a previous PDS, the BLE core is not in its own deep sleep, and the window has not run out. After a failure, `ipro_ble_ctlr_pds_reval_last_reason` ([`ipro_ble_ctlr_pds_snapshot.h`](#ipro_ble_ctlr_pds_snapshot-h)) tells a transient HCI hold-up from any other cause.

| Parameter | Description |
|---|---|
| `token` | Window identifier read from ipro_ble_ctlr_pds_candidate_token. |
| `fresh_slack_hus` | Time left in the window, in half-microseconds; written only on success. |

**Returns:** true if the window can still be granted, false otherwise.

!!! note "Note"
    Does not block; it can be called from the RTOS idle hook with interrupts masked.

### Typedefs { #ipro_ble_ctlr_arch-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `ipro_ble_ctlr_tickless_slack_hus` | `volatile uint32_t ipro_ble_ctlr_tickless_slack_hus` | Radio deadline published for the RTOS tickless idle hook, in half-microseconds. UINT32_MAX means that the idle hook does not need to arrange a wake-up for the controller: the running BLE core's own interrupt wakes the CPU from WFI. The value is advisory for WFI only; platform PDS is entered only through a grant ([`ipro_ble_ctlr_pds_tickless_grant()`](#ipro_ble_ctlr_pds_tickless_grant)), which the controller admits again itself. |
| `ipro_ble_ctlr_pds_candidate_slack_hus` | `volatile uint32_t ipro_ble_ctlr_pds_candidate_slack_hus` | Length of the latest idle window published after a connection event, in half-microseconds, counted from the moment of publication. Published only while the connection is in the low-power profile ([`ipro_ble_ctlr_tickless_connection_active_set()`](#ipro_ble_ctlr_tickless_connection_active_set)) and only for windows of at least 50 ms; set to 0 once a window has been used for a PDS. The value ages from the moment it is published: use [`ipro_ble_ctlr_pds_candidate_revalidate()`](#ipro_ble_ctlr_pds_candidate_revalidate) to get the time that is left. |
| `ipro_ble_ctlr_pds_candidate_token` | `volatile uint32_t ipro_ble_ctlr_pds_candidate_token` | Identifier of the published idle window. It changes whenever a window is published or used for a PDS, and is 0 until the first window after [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init). Pass it to [`ipro_ble_ctlr_pds_candidate_revalidate()`](#ipro_ble_ctlr_pds_candidate_revalidate). |
| `ipro_ble_ctlr_pds_full_generation` | `volatile uint32_t ipro_ble_ctlr_pds_full_generation` | Generation counter of published idle windows: incremented for every new window and never 0 once a window has been published. A PDS policy grants each generation at most once. |

## ipro_ble_ctlr_hcitl.h { #ipro_ble_ctlr_hcitl-h }

`#include "ipro_ble_ctlr_hcitl.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/wireless/bluetooth/ipro_ble_controller/hcitl/ipro_ble_ctlr_hcitl.h))

HCI byte-stream transport between the Bluetooth host and the on-chip BLE controller.

Host and controller exchange standard H4 packets (a packet-type byte followed by the HCI packet) through two in-memory ring buffers, exactly as they would over a UART HCI link. The controller cannot tell the difference, and the host never touches controller memory:

- host to controller (h2c): written by the host with [`ipro_ble_ctlr_hcitl_host_write()`](#ipro_ble_ctlr_hcitl_host_write), read by the controller task;
- controller to host (c2h): written by the controller task, read by the host with [`ipro_ble_ctlr_hcitl_host_read()`](#ipro_ble_ctlr_hcitl_host_read).

Each ring has exactly one producer and one consumer and needs no lock. On the host side this means one writer and one reader at a time: serialize [`ipro_ble_ctlr_hcitl_host_write()`](#ipro_ble_ctlr_hcitl_host_write) calls when several tasks send HCI packets.

The stream never loses a byte, because a missing byte would desynchronize the H4 framing for good. A full ring therefore never drops or blocks: [`ipro_ble_ctlr_hcitl_host_write()`](#ipro_ble_ctlr_hcitl_host_write) accepts only what fits and the caller keeps the rest, and the controller holds back its own output until the host has read enough to make room.

Host-side sequence:

1. [`ipro_ble_ctlr_hcitl_host_set_rx_notify()`](#ipro_ble_ctlr_hcitl_host_set_rx_notify) with a callback that wakes the host RX thread.
1. Send commands and data with [`ipro_ble_ctlr_hcitl_host_write()`](#ipro_ble_ctlr_hcitl_host_write); after each notification, read events and data with [`ipro_ble_ctlr_hcitl_host_read()`](#ipro_ble_ctlr_hcitl_host_read) until it returns 0.
1. When the host has finished its HCI initialization, call [`ipro_ble_ctlr_hcitl_host_ready()`](#ipro_ble_ctlr_hcitl_host_ready) so that the controller may let the BLE core sleep.

The bundled host driver (`hci_driver_ipro_ble_ctlr_init()`) performs steps 1 and 2; an application that uses it only has to call [`ipro_ble_ctlr_hcitl_host_ready()`](#ipro_ble_ctlr_hcitl_host_ready).

### ipro_ble_ctlr_hcitl_host_ready { #ipro_ble_ctlr_hcitl_host_ready }

```c
void ipro_ble_ctlr_hcitl_host_ready(void);
```

Tell the controller that the host has finished its HCI initialization.

Until this is called the controller keeps the BLE core out of deep sleep and never enters platform PDS, so that every exchange of the host's start-up command sequence finds it awake. Call it once the host stack is up, for example from the `bt_enable()` ready callback. Further calls have no additional effect. It also wakes the controller task.

!!! note "Note"
    ipro_pm (`ipro_pm_ble_controller_init()`) calls it on the first connection if the application has not done so.

### ipro_ble_ctlr_hcitl_host_write { #ipro_ble_ctlr_hcitl_host_write }

```c
uint32_t ipro_ble_ctlr_hcitl_host_write(const uint8_t *data, uint32_t len);
```

Send H4 bytes to the controller.

Copies as many bytes as fit into the host-to-controller ring, restarts the HCI awake guard (ipro_ble_ctlr_hcitl_awake_guard_ms) and wakes the controller task. The data is an H4 stream: every packet starts with its packet-type byte (for example 0x01 for a command, 0x02 for ACL data). A packet may be split across several calls.

| Parameter | Description |
|---|---|
| `data` | H4 bytes to send, including the packet-type byte of each packet. |
| `len` | Number of bytes in `data`. |

**Returns:** Number of bytes accepted, from 0 to `len`. Less than `len` means the ring is full: keep the remaining bytes and send them later; never drop them, or the stream loses its framing. Check [`ipro_ble_ctlr_hcitl_host_write_space()`](#ipro_ble_ctlr_hcitl_host_write_space) first to avoid a partial write.

!!! note "Note"
    Non-blocking. Task context only; one writer at a time.

### ipro_ble_ctlr_hcitl_host_write_space { #ipro_ble_ctlr_hcitl_host_write_space }

```c
uint32_t ipro_ble_ctlr_hcitl_host_write_space(void);
```

Get the free space in the host-to-controller ring.

**Returns:** Number of bytes [`ipro_ble_ctlr_hcitl_host_write()`](#ipro_ble_ctlr_hcitl_host_write) can accept right now.

### ipro_ble_ctlr_hcitl_host_read { #ipro_ble_ctlr_hcitl_host_read }

```c
uint32_t ipro_ble_ctlr_hcitl_host_read(uint8_t *out, uint32_t max);
```

Read H4 bytes sent by the controller.

Copies up to `max` bytes out of the controller-to-host ring. Packet boundaries are not preserved: the host parses the H4 stream (type byte, header, payload) itself. If the controller was waiting for room in the ring, it is woken.

| Parameter | Description |
|---|---|
| `out` | Destination buffer of at least `max` bytes. |
| `max` | Maximum number of bytes to read. |

**Returns:** Number of bytes read; 0 when nothing is available.

!!! note "Note"
    Non-blocking; one reader at a time. When it returns 0, wait for the notification registered with [`ipro_ble_ctlr_hcitl_host_set_rx_notify()`](#ipro_ble_ctlr_hcitl_host_set_rx_notify).

### ipro_ble_ctlr_hcitl_host_avail { #ipro_ble_ctlr_hcitl_host_avail }

```c
uint32_t ipro_ble_ctlr_hcitl_host_avail(void);
```

Get the number of bytes waiting in the controller-to-host ring.

**Returns:** Number of bytes [`ipro_ble_ctlr_hcitl_host_read()`](#ipro_ble_ctlr_hcitl_host_read) can return right now.

### ipro_ble_ctlr_hcitl_host_set_rx_notify { #ipro_ble_ctlr_hcitl_host_set_rx_notify }

```c
void ipro_ble_ctlr_hcitl_host_set_rx_notify(void(*cb)(void));
```

Register the callback that tells the host the controller has data for it.

The callback is invoked every time the controller adds bytes to the controller-to-host ring, which can happen several times per packet. Pass NULL to remove it.

| Parameter | Description |
|---|---|
| `cb` | Callback without arguments, or NULL. |

!!! warning "Warning"
    The callback runs in the controller task, not in the host's context. Only wake the host RX thread there (give a semaphore or send a task notification). Do not parse HCI or call anything that blocks: the time would be charged to the controller task, which has hard radio deadlines.

### Typedefs { #ipro_ble_ctlr_hcitl-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `ipro_ble_ctlr_hcitl_host_is_ready` | `volatile bool ipro_ble_ctlr_hcitl_host_is_ready` | False until [`ipro_ble_ctlr_hcitl_host_ready()`](#ipro_ble_ctlr_hcitl_host_ready) has been called after controller start-up. Read-only for applications. |
| `ipro_ble_ctlr_hcitl_awake_guard_ms` | `volatile uint32_t ipro_ble_ctlr_hcitl_awake_guard_ms` | Time in milliseconds for which host-to-controller traffic keeps the BLE core out of deep sleep (default 100). Every [`ipro_ble_ctlr_hcitl_host_write()`](#ipro_ble_ctlr_hcitl_host_write) restarts the interval, so a command and its response complete without a deep-sleep entry in between. ipro_pm lowers it to 5 ms while a link is in its PDS profile and restores 100 ms afterwards. |

### Macros { #ipro_ble_ctlr_hcitl-h-macros }

| Name | Value | Description |
|---|---|---|
| `IPRO_BLE_CTLR_HCITL_H2C_SIZE` | `2048` | Host-to-controller ring size in bytes. Holds eight maximum-size ACL packets of 256 bytes each on the wire (251-byte payload, 4-byte ACL header, 1-byte H4 type): the controller's whole ACL transmit credit window plus one, so the host can queue a full window of data without waiting for the radio. |
| `IPRO_BLE_CTLR_HCITL_C2H_SIZE` | `1024` | Controller-to-host ring size in bytes: 4096 in ISO-over-HCI and voice-over-HCI controller profiles, 1024 otherwise. Events are small but frequent and received ACL data uses up to 256 bytes per packet. In ISO profiles a single timestamped ISO packet is close to 256 bytes and several streams share the ring with control events, so the larger ring absorbs short scheduling delays of the host thread without holding back the controller. |

## ipro_ble_ctlr_lowpower.h { #ipro_ble_ctlr_lowpower-h }

`#include "ipro_ble_ctlr_lowpower.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/wireless/bluetooth/ipro_ble_controller/plf/ipro7/lowpower/ipro_ble_ctlr_lowpower.h))

IPRO7 BLE controller sleep clock: 32 kHz source qualification and drift bound.

Two clocks time a BLE link. While the CPU only waits in core-retentive WFI between radio events, BLE timing stays on the 32 MHz crystal and uses its accuracy. When the BLE core sleeps on its own or the chip enters platform PDS, elapsed time is measured on the 32 kHz clock instead. That clock is therefore selected and qualified once at controller start-up, and its accuracy is reported to the controller.

### ipro_ble_ctlr_lowpower_init { #ipro_ble_ctlr_lowpower_init }

```c
int ipro_ble_ctlr_lowpower_init(void);
```

Select and qualify the 32 kHz sleep clock for the BLE controller.

The board configuration names the candidate source (`board_get_32k_source()`, from `BOARD_CLK_32K_SOURCE_MACRO`):

- a board that declares RC32K calibrates RC32K straight away;
- a board that declares the 32 kHz crystal, or declares nothing, first measures the crystal against the 32 MHz crystal. If it is off by more than 500 ppm or does not oscillate, RC32K is calibrated and used instead.

The measured error is compensated, and an accuracy bound that also covers temperature and supply (by default at least 50 ppm for the crystal and 500 ppm for RC32K) becomes the value returned by [`ipro_ble_ctlr_lowpower_sleep_drift_ppm_get()`](#ipro_ble_ctlr_lowpower_sleep_drift_ppm_get). Only the controller's own sleep and platform PDS use the result.

Called by [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init) before the controller core is initialized; applications do not need to call it.

**Returns:** 0 when the 32 kHz crystal was qualified and selected; when RC32K is selected, the calibrated RC32K capacitor code (0 or greater); a negative value when the RC32K calibration or its accuracy measurement failed.

!!! note "Note"
    Blocks for more than a second: crystal settling (1.5 s), RC32K calibration and a one-second accuracy measurement, depending on the board.

!!! warning "Warning"
    Do not reselect the 32 kHz source afterwards (for example with `HBN_32K_Sel()`): on IPRO7 that reapplies the factory trim and discards the RC32K calibration.

### ipro_ble_ctlr_lowpower_sleep_drift_ppm_get { #ipro_ble_ctlr_lowpower_sleep_drift_ppm_get }

```c
uint16_t ipro_ble_ctlr_lowpower_sleep_drift_ppm_get(void);
```

Get the sleep-clock accuracy bound the controller uses.

This is the positive accuracy bound of the 32 kHz clock in ppm. Whenever the 32 kHz clock times the link, the controller uses it to widen receive windows and to report its sleep clock accuracy to peers. It is not the signed error that the controller compensates.

**Returns:** Accuracy bound in ppm, between 20 and 2000; 500 before [`ipro_ble_ctlr_lowpower_init()`](#ipro_ble_ctlr_lowpower_init) has qualified the clock.

## ipro_ble_ctlr_pds_snapshot.h { #ipro_ble_ctlr_pds_snapshot-h }

`#include "ipro_ble_ctlr_pds_snapshot.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/wireless/bluetooth/ipro_ble_controller/plf/ipro7/lowpower/ipro_ble_ctlr_pds_snapshot.h))

IPRO7 BLE controller connected platform PDS: enable, policy modes and window grants.

Connected platform PDS powers the IPRO7 down between connection events while a BLE link stays up. The controller owns the whole PDS cycle: it saves the BLE core state, enters PDS, restores the core and re-synchronizes the link. The application, or the ipro_pm power manager, only decides which idle windows may be used.

Set-up, after [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init):

1. ipro_ble_ctlr_pds_enable(true) once.
1. When a connection is established, ipro_ble_ctlr_pds_auto_connected(true). When its parameters leave room for a PDS between connection events, ipro_ble_ctlr_tickless_connection_active_set(true) and ipro_ble_ctlr_pds_auto_config(true, 0) (grant-only mode).
1. In the RTOS idle hook, for each new window (ipro_ble_ctlr_pds_full_generation), check it with [`ipro_ble_ctlr_pds_candidate_revalidate()`](#ipro_ble_ctlr_pds_candidate_revalidate), size the sleep to the shorter of the RTOS and radio windows minus [`ipro_ble_ctlr_pds_reserve_us()`](#ipro_ble_ctlr_pds_reserve_us), and grant it once with [`ipro_ble_ctlr_pds_tickless_grant()`](#ipro_ble_ctlr_pds_tickless_grant).
1. When the link leaves the profile or disconnects, undo step 2.

`ipro_pm_ble_controller_init()` (ipro_pm_ble.h) does all of this; use these functions directly only to implement a different policy.

The controller reports what happened to each grant through optional hooks that the application may define (the controller references them as weak symbols):

- `bool ipro_ble_ctlr_app_pds_prepare(uint32_t sleep_us)`: controller task, interrupts masked, last point before the cycle commits; return false to keep this window on WFI.
- `void ipro_ble_ctlr_app_pds_resumed(void)`: right after the chip returns from PDS, interrupts masked.
- `void ipro_ble_ctlr_app_pds_cycle_consumed(void)`: controller task; the grant was used for a PDS cycle.
- `void ipro_ble_ctlr_app_pds_grant_released(void)`: the grant was given back without a PDS; only the window is lost and the next one may be granted. It can also run in the task that calls ipro_ble_ctlr_pds_enable(false) or ipro_ble_ctlr_pds_auto_connected(false).
- `void ipro_ble_ctlr_app_pds_recovered(void)`: BLE interrupt context; the first connection event after the PDS re-synchronized the link.
- `void ipro_ble_ctlr_app_pds_recovery_failed(uint32_t reason)`: controller task; the link did not recover, `reason` is an [`ipro_ble_ctlr_pds_recovery_fail_reason`](#ipro_ble_ctlr_pds_recovery_fail_reason) value.
- `void ipro_ble_ctlr_app_pds_link_stuck(uint32_t links)`: controller task; a recovery disconnection did not complete and the host was sent HCI Hardware Error. The application owns any reset.

When ipro_pm handles BLE (`CONFIG_IPRO_PM_BLE`), it defines these hooks itself and the application must not define them.

Time values with the suffix `_hus` are in half-microseconds (units of 0.5 us).

### ipro_ble_ctlr_pds_reserve_us { #ipro_ble_ctlr_pds_reserve_us }

```c
uint32_t ipro_ble_ctlr_pds_reserve_us(void);
```

Get the time the controller reserves around each connected PDS cycle.

The reserve covers waking the chip, restoring the BLE core and reaching the next radio event with a guard; it is 22000 us with the default configuration. A PDS policy subtracts it from the idle window before it calls [`ipro_ble_ctlr_pds_tickless_grant()`](#ipro_ble_ctlr_pds_tickless_grant).

**Returns:** Reserve in microseconds.

### ipro_ble_ctlr_pds_enable { #ipro_ble_ctlr_pds_enable }

```c
int ipro_ble_ctlr_pds_enable(bool enable);
```

Enable or disable connected platform PDS.

Enabling keeps the MISC power domain on across PDS, so that the RAM holding host task stacks and kernel objects keeps its contents, and initializes the low-power HAL (`hal_lp_init()`). Disabling gives back any pending grant and ends any post-PDS recovery hold. Call it after [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init), which resets the PDS state.

| Parameter | Description |
|---|---|
| `enable` | true to enable, false to disable. |

| Return value | Description |
|---|---|
| `0` | Done. |
| `-1` | PDS is not available: the controller library was built without PDS support, its profile uses an exchange memory other than 16 KB (for example the ISO profiles), or the low-power HAL failed to initialize. |

!!! note "Note"
    Enabling changes the PDS configuration of the whole system (MISC domain kept on).

### ipro_ble_ctlr_pds_auto_config { #ipro_ble_ctlr_pds_auto_config }

```c
int ipro_ble_ctlr_pds_auto_config(bool enable, uint32_t sleep_us);
```

Select the automatic connected-PDS mode.

- `enable` false: no automatic PDS; a pending automatic request is dropped.
- `enable` true, `sleep_us` 0: grant-only mode. A PDS cycle runs only when the RTOS idle policy grants a window with [`ipro_ble_ctlr_pds_tickless_grant()`](#ipro_ble_ctlr_pds_tickless_grant). ipro_pm uses this mode.
- `enable` true, `sleep_us` not 0: the controller requests a PDS of `sleep_us` on its own whenever the connected link allows one (no pending link-procedure instant, clean reception since the previous PDS).

Automatic PDS also needs ipro_ble_ctlr_pds_enable(true) and ipro_ble_ctlr_pds_auto_connected(true).

| Parameter | Description |
|---|---|
| `enable` | true to enable automatic PDS, false to disable it. |
| `sleep_us` | PDS length in microseconds for the self-requested mode (10000 or more), or 0 for grant-only mode. Ignored when `enable` is false. |

| Return value | Description |
|---|---|
| `0` | Done. |
| `-1` | `sleep_us` is out of range, or PDS is not available in this controller profile. |

### ipro_ble_ctlr_pds_tickless_grant { #ipro_ble_ctlr_pds_tickless_grant }

```c
int ipro_ble_ctlr_pds_tickless_grant(uint32_t sleep_us);
```

Grant the controller one connected PDS cycle in the current idle window.

Called by the RTOS idle policy after [`ipro_ble_ctlr_pds_candidate_revalidate()`](#ipro_ble_ctlr_pds_candidate_revalidate) succeeded. The controller uses the grant at its next safe point in the same window, shortening the sleep if less of the window is left, and reports the outcome through the hooks listed in the file description. Only one grant can be outstanding at a time.

| Parameter | Description |
|---|---|
| `sleep_us` | Requested PDS length in microseconds, 10000 or more. |

| Return value | Description |
|---|---|
| `0` | Grant accepted. |
| `-1` | Grant refused: `sleep_us` is out of range, a request is already pending, grant-only mode is not active (ipro_ble_ctlr_pds_auto_config(true, 0) and ipro_ble_ctlr_pds_auto_connected(true)), PDS is not enabled or not available in this controller profile, a link-procedure instant is pending, the link is guarded or still recovering from the previous PDS, reception has not been clean since then, or the link has not settled yet. |

!!! note "Note"
    Does not block; it can be called from the RTOS idle hook with interrupts masked.

### ipro_ble_ctlr_pds_auto_connected { #ipro_ble_ctlr_pds_auto_connected }

```c
void ipro_ble_ctlr_pds_auto_connected(bool connected);
```

Tell the controller whether a connection is up for connected PDS.

Call it with true when a connection is established and with false when it ends. True restarts the link-settle and reception checks for the new link; false gives back any pending grant and ends any post-PDS recovery hold left from the link.

| Parameter | Description |
|---|---|
| `connected` | true when the link is up, false when it is gone. |

### ipro_ble_ctlr_pds_auto_enabled { #ipro_ble_ctlr_pds_auto_enabled }

```c
bool ipro_ble_ctlr_pds_auto_enabled(void);
```

Report whether automatic connected PDS is enabled.

**Returns:** true after [`ipro_ble_ctlr_pds_auto_config()`](#ipro_ble_ctlr_pds_auto_config) enabled it, false otherwise.

### ipro_ble_ctlr_pds_snapshot_enabled { #ipro_ble_ctlr_pds_snapshot_enabled }

```c
bool ipro_ble_ctlr_pds_snapshot_enabled(void);
```

Report whether connected platform PDS is enabled.

**Returns:** true after ipro_ble_ctlr_pds_enable(true) until ipro_ble_ctlr_pds_enable(false); false when PDS is not available in this controller profile.

### ipro_ble_ctlr_pds_clock_drift { #ipro_ble_ctlr_pds_clock_drift }

```c
bool ipro_ble_ctlr_pds_clock_drift(int32_t *error_hus, int32_t *ppm, uint32_t *elapsed_ms);
```

Measure the controller clock against the 32 kHz RTC since the last PDS restore.

Compares the BLE clock rebuilt after the last platform PDS with the always-on 32 kHz RTC. Diagnostic; any output pointer may be NULL.

| Parameter | Description |
|---|---|
| `error_hus` | Accumulated error of the BLE clock in half-microseconds (positive: the BLE clock is ahead of the RTC). |
| `ppm` | The same error in parts per million of the elapsed time. |
| `elapsed_ms` | RTC time since the reference point, in milliseconds. |

**Returns:** true on success; false until a platform-PDS restore has set a reference point, while the BLE core is in its own deep sleep, or if the clock sample timed out.

### ipro_ble_ctlr_pds_recovery_fail_reason { #ipro_ble_ctlr_pds_recovery_fail_reason }

Why a link did not recover after a platform PDS; passed as `reason` to the optional `ipro_ble_ctlr_app_pds_recovery_failed()` hook.

After a restore the controller keeps the BLE core awake until the first clean connection event. If no connection event arrives within six connection intervals (each interval x (latency + 1), by default) after the next scheduled event, capped at the supervision timeout, or if the BLE core reports an error, or if a restore step times out, recovery is abandoned and every link is ended with reason 0x08 (the host receives HCI Disconnection Complete). Events that keep running without re-synchronizing are left to the link layer's own supervision timeout.

| Name | Value | Description |
|---|---|---|
| `IPRO_BLE_CTLR_PDS_RECOVERY_NONE` | `0` | No failure. |
| `IPRO_BLE_CTLR_PDS_RECOVERY_NO_PROGRESS` |  | No connection event within the recovery window; the links were ended. |
| `IPRO_BLE_CTLR_PDS_RECOVERY_HW_ERROR` |  | The BLE core reported an error during recovery; the links were ended. |
| `IPRO_BLE_CTLR_PDS_RECOVERY_NOT_CONVERGED` |  | Events run but do not re-synchronize; recorded only, never passed to the hook. |
| `IPRO_BLE_CTLR_PDS_RECOVERY_RESTORE_TIMEOUT` |  | A bounded wait while restoring the BLE core expired; the links were ended. |

### Typedefs { #ipro_ble_ctlr_pds_snapshot-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `ipro_ble_ctlr_pds_reval_last_reason` | `volatile uint32_t ipro_ble_ctlr_pds_reval_last_reason` | Failure class (`IPRO_BLE_CTLR_PDS_REVAL_*`) of the last [`ipro_ble_ctlr_pds_candidate_revalidate()`](#ipro_ble_ctlr_pds_candidate_revalidate) call. Every call updates it; it is meaningful after a call that returned false. |

### Macros { #ipro_ble_ctlr_pds_snapshot-h-macros }

| Name | Value | Description |
|---|---|---|
| `IPRO_BLE_CTLR_PDS_REVAL_OTHER` | `1U` | The window can no longer be granted (stale token, profile left, guarded, expired). |
| `IPRO_BLE_CTLR_PDS_REVAL_HCI` | `2U` | HCI bytes are in flight or the HCI hold-off is running. Transient: the same window may be offered again once the transport is idle. |

## ipro_ble_ctlr_nvds.h { #ipro_ble_ctlr_nvds-h }

`#include "ipro_ble_ctlr_nvds.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/wireless/bluetooth/ipro_ble_controller/plf/ipro7/nvds/ipro_ble_ctlr_nvds.h))

IPRO7 BLE controller parameters: Bluetooth device address and clock accuracy.

At start-up the controller reads its Bluetooth device address, the accuracy of its sleep and active clocks and its wake-up timing from a small parameter store in RAM, which [`ipro_ble_ctlr_nvds_init()`](#ipro_ble_ctlr_nvds_init) fills. Nothing is kept in flash: the store is rebuilt on every boot.

### ipro_ble_ctlr_nvds_init { #ipro_ble_ctlr_nvds_init }

```c
bool ipro_ble_ctlr_nvds_init(void);
```

Fill the controller parameter store.

Stores the device address, the 32 kHz sleep-clock accuracy measured by [`ipro_ble_ctlr_lowpower_init()`](#ipro_ble_ctlr_lowpower_init), the active-clock accuracy, the wake-up times and the setting of the controller's own BLE-core deep sleep. The device address is taken from the first of these sources that is usable:

1. the factory MAC address in eFuse, if it is programmed and is a valid unicast, globally administered address with a non-zero device part;
1. an address derived from the chip ID: locally administered, shown as `1E:0B:37:xx:xx:xx`, unique per chip but not a registered public address;
1. a fixed development address, if the chip ID cannot be read either.

The address in use is logged at start-up.

Called by [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init) before the controller core starts, because the core reads the address while it initializes; applications do not need to call it.

**Returns:** true if the address comes from eFuse; false if a fallback address is used or the parameter store could not be initialized.

### ipro_ble_ctlr_nvds_bd_addr_get { #ipro_ble_ctlr_nvds_bd_addr_get }

```c
void ipro_ble_ctlr_nvds_bd_addr_get(uint8_t addr[6]);
```

Get the Bluetooth device address the controller uses.

| Parameter | Description |
|---|---|
| `addr` | Six-byte buffer that receives the address in Bluetooth byte order, least significant byte first: `addr[5]` is the first byte a scanner displays. |

!!! note "Note"
    Valid once [`ipro_ble_ctlr_controller_init()`](#ipro_ble_ctlr_controller_init) has run.
