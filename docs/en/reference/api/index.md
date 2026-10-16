---
title: "API Reference"
description: "The IPRO-specific public C API: a reference generated with Doxygen from the SDK V2.1.0 headers, plus how to use platform start-up, BLE controller bring-up and logging."
migrate_from:
  - "api-reference.html — 第 3 階段改由 Doxygen 產生"
---

# API Reference

The IPRO-specific public C API. The API groups below are generated with Doxygen from the public headers shipped in SDK V2.1.0, with the header documentation for every function, type and macro; the sections after them explain platform start-up, BLE controller bring-up and logging. Zephyr Bluetooth `bt_*` APIs are not repeated here; see the [official Zephyr documentation](#ble-host).

!!! note "Scope"
    The HAL and platform APIs on this page are for FreeRTOS applications. Zephyr applications use Zephyr's device driver APIs; see [Zephyr RTOS](../../guides/zephyr.md).

## API groups { #groups }

The complete reference by area, generated from the public headers of SDK V2.1.0.

<!-- BEGIN generated: api-groups -->
| Group | Headers | Functions | Contents |
|---|---|---|---|
| [Platform & System](platform.md) | 11 | 65 | FreeRTOS start-up and hooks, common HAL definitions, system control, clocks, timers, watchdogs, RTC and memory helpers. |
| [Memory](memory-boot.md) | 5 | 45 | Flash access, PSRAM, boot2 and the partition table manager. |
| [Power Management & Low Power](power.md) | 4 | 52 | Power modes, PDS sleep and wake-up, the low-power framework and the low-power UART. |
| [Peripheral I/O](peripherals.md) | 13 | 62 | GPIO, UART, SPI, I2C, PWM, ADC, DAC, analog comparator, KeyScan, QDEC and DMA. |
| [Audio](audio.md) | 3 | 16 | Audio ADC (PDM and analog microphones) and I2S. |
| [Camera & Imaging](camera.md) | 4 | 36 | DVP camera interface, ISP, and hardware MJPEG encoding and decoding. |
| [SD Card & SDIO](sd-sdio.md) | 4 | 61 | Hardware SD host, SDIO, and the PIO-based SD host. |
| [Ethernet](ethernet.md) | 3 | 27 | EMAC, the lwIP network interface and the Ethernet PHY. |
| [PIO](pio.md) | 3 | 24 | Programmable I/O for CCI, CMSIS-DAP and scan interfaces. |
| [Security Engine](security.md) | 9 | 49 | AES, GMAC, hashing, DSA, ECDSA, P-256 and the hardware random number generator. |
| [Wireless & BLE Controller](wireless-ble.md) | 7 | 41 | Radio start-up and the IPRO BLE controller interfaces for bring-up, HCI transport, low power and NVDS. |
| [AI Runtime](ai.md) | 18 | 133 | The NPU driver, inference core, operators and post-processing, and the detection and speech model interfaces. |
| [IPRO7AI EVK Board Library](ipro7ai-evk.md) | 12 | 113 | The EVK sub-board interfaces for the panel, graphics, camera, microphone, speaker, PCM and microSD. |
<!-- END generated: api-groups -->

## Platform init and FreeRTOS hooks { #rtos-platform }

Every FreeRTOS application shares `components/os/freertos/freertos_app_hooks`, which provides platform init plus default heap, FreeRTOS hook and assert implementations.

| API | Header | Purpose |
|---|---|---|
| `void ipro_platform_init(void)` | `components/os/freertos/freertos_app_hooks.h` | Call once at the start of `main()`. Runs `platform_init()`, `ipro_setup_heap()`, `hal_boot2_init()`, a PSRAM check, `ipro_log_init()` (`CONFIG_IPRO_LOG_ENABLE`), shell init (`CONFIG_SHELL`) and `ipro_pm_init()` (`CONFIG_IPRO_PM`), in that order. |
| `void ipro_setup_heap(void)` | same | Collects the OCRAM and (if enabled) PSRAM heap regions from linker symbols and calls `vPortDefineHeapRegions()`. Already called by `ipro_platform_init()`. |
| `void ipro_dump_task_stacks(const char *where)` | same | Prints each task's minimum free stack (bytes) and the free heap. Needs `configUSE_TRACE_FACILITY=1`. |

The FreeRTOS hooks below have weak default implementations in `components/os/freertos/freertos_app_hooks.c`. To replace one, define a non-weak function of the same name in your application's sources; the linker picks it automatically.

| Hook | Default behavior |
|---|---|
| `vApplicationStackOverflowHook()` | Prints `[!] Stack overflow: <task name>` and every task's free stack, then halts. |
| `vApplicationMallocFailedHook()` | Prints the requested size, free and minimum-ever heap, caller address and task name, then halts. `pvPortMalloc(0)` only warns. |
| `vApplicationIdleHook()` | Executes `__WFI()`. |
| `vApplicationGetIdleTaskMemory()`, `vApplicationGetTimerTaskMemory()` | Provide the static stacks and TCBs of the Idle and Timer tasks. |
| `vAssertCalled()` | Disables interrupts, prints `[!] ASSERT <file>:<line>` and the caller address, then halts. |

```c title="main.c (minimal application, from the SDK README)"
#include "freertos_app_hooks.h"
#include <FreeRTOS.h>
#include <task.h>

static void app_task(void *arg)
{
    for (;;) {
        /* your code */
    }
}

int main(void)
{
    ipro_platform_init();   /* heap, boot2, log, shell */
    xTaskCreate(app_task, "app", 1024, NULL, 5, NULL);
    vTaskStartScheduler();
    for (;;) {}
}
```

!!! warning "Do not initialize twice"
    `ipro_platform_init()` already initializes the shell and logging; do not call those again from the application. Do not add heap, hook or assert boilerplate back into `main.c` either.

For the FreeRTOS kernel (V11.1.0) API itself — `xTaskCreate()`, queues, semaphores — see the [FreeRTOS API reference](https://www.freertos.org/Documentation/02-Kernel/04-API-references/01-Task-creation/00-TaskHandle). The stack depth passed to `xTaskCreate()` is in words, not bytes.

## BLE controller bring-up { #ble-core }

Bluetooth LE combines the Zephyr v4.4.0 host with the IPRO BLE controller (prebuilt library), joined by an in-memory HCI byte stream. The application starts the controller, the HCI driver and the host, in that order.

| API | Header | Purpose |
|---|---|---|
| `int ipro_ble_ctlr_controller_init(unsigned int task_priority)` | `components/wireless/bluetooth/ipro_ble_controller/include/ipro_ble_controller.h` | Starts the controller and creates its task. Returns 0 on success, -1 if already started, -2 if the task could not be created. The controller has hard radio deadlines, so give it a higher priority than application tasks; the shipped applications use `configMAX_PRIORITIES - 1`. |
| `int hci_driver_ipro_ble_ctlr_init(void)` | `components/wireless/bluetooth/ipro_bt_host/port/include/hci_driver_ipro_ble_ctlr.h` | Call before `bt_enable()`. Zephyr 4.4 binds the HCI device at build time; the function is kept for source compatibility with existing applications, and the shipped applications still call it in this order. |
| `void ipro_ble_ctlr_hcitl_host_ready(void)` | `components/wireless/bluetooth/ipro_ble_controller/hcitl/ipro_ble_ctlr_hcitl.h` (included by `ipro_ble_controller.h`) | Call from the `bt_enable()` ready callback to mark the HCI initialization as complete; from then on the controller may sleep between events. |
| `int bt_enable(bt_ready_cb_t cb)` | `<zephyr/bluetooth/bluetooth.h>` | Starts the host and calls `cb` when done. See [Zephyr Bluetooth API](#ble-host). |

Wait 50 ms between the calls and run them in a FreeRTOS task; the complete bring-up code and ready callback are in [BLE Development](../../guides/ble.md#ble-init).

The controller library is selected by `CONFIG_IPRO_BLE_CTLR_LIB`, `CONFIG_IPRO_BLE_CTLR_FEATURE` and `CONFIG_IPRO_BLE_CTLR_CFG_DBG` in `.config`; the table is in [BLE Development](../../guides/ble.md#controller-variants).

## Zephyr Bluetooth API { #ble-host }

Applications use Zephyr's callback-based `bt_*` APIs through `<zephyr/bluetooth/...>` headers; the SDK's copy is in `components/wireless/bluetooth/ipro_bt_host/upstream/zephyr/include/zephyr/bluetooth/`. The links below point to the Zephyr v4.4.0 documentation, the same version as the host in the SDK.

| Topic | Common APIs | Zephyr v4.4.0 documentation |
|---|---|---|
| Bluetooth API overview | — | [Bluetooth API](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/index.html) |
| GAP: enable, advertise, scan | `bt_enable()`, `bt_le_adv_start()`, `bt_le_scan_start()` | [Generic Access Profile (GAP)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gap.html) |
| Connection management | `bt_conn_cb_register()`, `bt_conn_le_create()`, `bt_conn_disconnect()` | [Connection Management](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/connection_mgmt.html) |
| GATT server and client | `BT_GATT_SERVICE_DEFINE()`, `bt_gatt_notify()`, `bt_gatt_discover()` | [Generic Attribute Profile (GATT)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gatt.html) |
| LE Audio | BAP, PACS, ASCS, CAP | [Bluetooth Audio](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/audio/audio.html) |
| Bond storage | `settings_load_subtree()` | [Settings](https://docs.zephyrproject.org/4.4.0/services/settings/index.html) |
| Full function index | — | [Zephyr API documentation (Doxygen)](https://docs.zephyrproject.org/4.4.0/doxygen/html/group__bluetooth.html) |

!!! tip "The SDK's headers are authoritative"
    The Zephyr documentation assumes the Zephyr kernel. In a FreeRTOS application the host runs on the SDK's port layer, and its `CONFIG_BT_*` options go in the application's `.config`. Check that a macro exists in the SDK's headers before using it: for connectable advertising use `BT_LE_ADV_CONN_FAST_1`, for example; `BT_LE_ADV_CONN_NAME` does not exist in this host version.

## Logging { #log-api }

Header: `components/utils/include/ipro_log.h` (defaults in `ipro_log_config.h`). Requires `CONFIG_IPRO_LOG_ENABLE=y`; `ipro_platform_init()` calls `ipro_log_init()` with the default configuration.

| API | Purpose |
|---|---|
| `IPRO_LOGE`, `IPRO_LOGW`, `IPRO_LOGI`, `IPRO_LOGD`, `IPRO_LOGV` (`tag, format, ...`) | Error, warning, info, debug and verbose messages. Calls above `CONFIG_LOG_DEFAULT_LEVEL` produce no output |
| `IPRO_LOG_BUFFER_HEX(tag, buf, len)`, `IPRO_LOG_BUFFER_HEXDUMP(tag, buf, len)` | Dump a buffer as hex (plus ASCII) |
| `ipro_log_set_level()`, `ipro_log_get_level()`, `ipro_log_level_enabled()` | Change or query the level at run time |
| `ipro_log_set_output_func()` | Route output to your own function |

`CONFIG_LOG_DEFAULT_LEVEL` is an integer: 1 error, 2 warning, 3 info (what the shipped applications use), 4 debug, 5 verbose. Output looks like `<level letter> (<time>) <TAG>: <message>`.

```c title="Logging (one TAG per file)"
#include "ipro_log.h"

#define TAG "MY_MODULE"

IPRO_LOGI(TAG, "connected, handle %u", handle);
IPRO_LOGE(TAG, "init failed (err %d)", err);
```

## Related documents { #related }

- [BLE Development](../../guides/ble.md): controller selection, bring-up order and GATT examples.
- [Build System & Configuration](../../guides/build-system.md): `.config` and application structure.
- [Debugging & Troubleshooting](../debugging.md): logs, crash output and FreeRTOS hook messages.
- IPRO7 API specification: see [Documents](../../documents/index.md).
