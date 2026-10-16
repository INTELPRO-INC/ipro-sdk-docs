---
title: "API Reference"
description: Index of the IPRO-specific public APIs — platform init and FreeRTOS hooks, BLE controller bring-up, HAL peripherals, logging, the IPRO7AI EVK board library and the AI runtime — with header paths and purposes.
migrate_from:
  - "api-reference.html — 第 3 階段改由 Doxygen 產生"
---

# API Reference

This page lists the IPRO-specific public APIs you need most when writing an IPRO7 FreeRTOS application. Each entry gives the header (path relative to the SDK root) and a one-line purpose; examples come only from applications that ship with the SDK. The Zephyr Bluetooth `bt_*` APIs are not repeated here — use the [official Zephyr documentation](#ble-host).

!!! info "Interim reference"
    This is a hand-curated interim reference. A complete reference generated from the sources (Doxygen) will replace it. The header comments are authoritative for parameters, return values and limits; the HAL is also covered in full by the *API Specification* listed under [Documents](../documents/index.md).

!!! note "Scope"
    The HAL and platform APIs on this page are for FreeRTOS applications. Zephyr applications use Zephyr's device driver APIs; see [Zephyr RTOS](../guides/zephyr.md).

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

Wait 50 ms between the calls and run them in a FreeRTOS task; the complete bring-up code and ready callback are in [BLE Development](../guides/ble.md#ble-init).

The controller library is selected by `CONFIG_IPRO_BLE_CTLR_LIB`, `CONFIG_IPRO_BLE_CTLR_FEATURE` and `CONFIG_IPRO_BLE_CTLR_CFG_DBG` in `.config`; the table is in [BLE Development](../guides/ble.md#controller-variants).

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

## HAL peripherals { #hal }

HAL headers are in `bsp/hal/inc/`, implementations in `bsp/hal/src/`. The tables give names and purposes only; control commands, structures and device indexes are defined in each header.

### GPIO { #hal-gpio }

Header: `bsp/hal/inc/hal_gpio.h`. Pins are passed by number (GPIO 0–41 on IPRO7); the `GPIO_PIN_x` enumerators are convenience constants only.

| API | Purpose |
|---|---|
| `gpio_set_mode(pin, mode)` | Set the mode, e.g. `GPIO_OUTPUT_PP_MODE`, `GPIO_INPUT_PD_MODE`, `GPIO_ASYNC_FALLING_TRIGER_INT_MODE`, `GPIO_HZ_MODE` |
| `gpio_write(pin, value)`, `gpio_toggle(pin)`, `gpio_read(pin)` | Drive, toggle, read |
| `gpio_attach_irq(pin, cb)`, `gpio_irq_enable(pin, enabled)` | Attach an interrupt callback and enable the interrupt |

```c title="LED output (from ipro_ble_remote)"
gpio_set_mode(LED_GPIO_PIN, GPIO_OUTPUT_PP_MODE);
gpio_write(LED_GPIO_PIN, 0);    /* LED off initially */
```

### UART { #hal-uart }

Header: `bsp/hal/inc/hal_uart.h`. Device indexes `UART0_INDEX` and `UART1_INDEX`; UART0 carries the console and the shell.

| API | Purpose |
|---|---|
| `uart_init(uart_id, oflag)`, `uart_uninit(uart_id)` | Open, close |
| `uart_write(uart_id, buf, size)`, `uart_read(uart_id, buf, size)` | Send, receive |
| `uart_read_available(uart_id, buf, max)` | Non-blocking read of whatever is in the RX FIFO |
| `uart_set_baudrate(uart_id, baud)`, `uart_set_callback(uart_id, args)`, `uart_ioctl(uart_id, cmd, args)` | Baud rate, event callback, control commands (`UART_CTRL_*`) |

### SPI and I2C { #hal-spi-i2c }

| API | Header | Purpose |
|---|---|---|
| `spi_init()`, `spi_deinit()`, `spi_setConfig()`, `spi_enable()`, `spi_ioctl()` | `bsp/hal/inc/hal_spi.h` | Open, configure and enable SPI (`SPI0_INDEX`, `SPI1_INDEX`) |
| `spi_transmit()`, `spi_receive()`, `spi_transmit_receive()` | same | Transmit, receive, full-duplex transfer |
| `i2c_init()`, `i2c_setConfig()` | `bsp/hal/inc/hal_i2c.h` | Open and configure I2C (`I2C0_INDEX`, `I2C1_INDEX`) |
| `i2c_transfer(i2c_id, msgs, num)` | same | Run a set of `i2c_msg_t` messages (slave address, sub-address, `I2C_RD` flag, length, buffer) |

### PWM, ADC and DAC { #hal-pwm-adc }

| API | Header | Purpose |
|---|---|---|
| `pwm_init()`, `pwm_ioctl()`, `pwm_close()` | `bsp/hal/inc/hal_pwm.h` | Open, control, close a PWM channel |
| `pwm_channel_start()`, `pwm_channel_stop()`, `pwm_channel_freq_update()`, `pwm_channel_dutycycle_update()` | same | Convenience macros built on `pwm_ioctl()` |
| `hal_adc_init()`, `hal_adc_read()`, `hal_adc_ioctl()` | `bsp/hal/inc/hal_adc.h` | Open, read, control the ADC (`ADC_CTRL_CHANNEL_START`, `ADC_CTRL_CHANNEL_STOP`, `ADC_CTRL_CHANNEL_CONFIG`) |
| `hal_adc_get_tsen()`, `hal_adc_trim_tsen()` | same | Read the internal temperature sensor |
| `hal_dac_init()`, `hal_dac_write()`, `hal_dac_control()`, `hal_dac_deinit()` | `bsp/hal/inc/hal_dac.h` | DAC output |

!!! warning "The ADC convenience macros do not link"
    `adc_channel_start()`, `adc_channel_stop()` and `adc_channel_config()` in `hal_adc.h` expand to `adc_ioctl()`, which does not exist, so the link fails. Call `hal_adc_ioctl()` with the matching `ADC_CTRL_*` command instead.

### Timers and watchdog { #hal-timer }

| API | Header | Purpose |
|---|---|---|
| `timer_init()`, `timer_setCallback()`, `timer_start()`, `timer_stop()`, `timer_get_counter()` | `bsp/hal/inc/hal_timer.h` | Hardware timers (configuration struct `hal_timer_config_t`) |
| `mtimer_get_time_ms()`, `mtimer_get_time_us()`, `mtimer_delay_ms()`, `mtimer_delay_us()` | `bsp/hal/inc/hal_mtimer.h` | System-timer timestamps and busy-wait delays |
| `wdt_init()`, `wdt_feed()`, `wdt_disable()`, `wdt_setTimeout()` | `bsp/hal/inc/hal_wdt.h` | Watchdog |
| `rtc_set_timestamp()`, `rtc_get_timestamp()` | `bsp/hal/inc/hal_rtc.h` | RTC timestamp |

### Flash, partitions and system { #hal-system }

| API | Header | Purpose |
|---|---|---|
| `flash_read()`, `flash_write()`, `flash_erase()` | `bsp/hal/inc/hal_flash.h` | Read, write and erase by physical flash address (not the XIP window at `0x13000000`) |
| `flash_get_jedecid()`, `flash_get_size()` | same | Flash JEDEC ID and size |
| `hal_boot2_partition_addr_active(name, &addr, &size)` | `bsp/hal/inc/hal_boot2.h` | Flash address and size of the active partition with that name; the AI examples use it to find the model in the `mfg` partition |
| `hal_reboot()`, `hal_reboot_download()` | `bsp/hal/inc/hal_sys.h` | Reboot; reboot into download mode (the shell commands `reboot` and `reboot_dl` call these) |
| `hal_rand()`, `hal_rand_stream(buf, len)` | `bsp/hal/inc/hal_sec_trng.h` | Hardware random numbers |

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

## IPRO7AI EVK board library { #evk-board }

`components/board/ipro7ai_evk` is the board library for the IPRO7AI EVK sub-board (`CONFIG_IPRO7AI_EVK`): include `evk.h`, call `evk_begin()` once, and use the panel, camera, microphone, speaker and microSD on the board. Headers are in `components/board/ipro7ai_evk/include/`. The IPRO7AI Reef EVK does not use this library.

| Block | Header | Main APIs | `.config` |
|---|---|---|---|
| Board init | `evk.h` | `evk_begin()` (parks the camera, turns the speaker amplifier off, initializes and clears the panel; call once from the first task), `evk_ready()` | `CONFIG_COMPONENTS_IPRO7AI_EVK_ENABLE=y` |
| Panel and graphics | `st7789p3.h`, `evk_gfx.h` | `st7789p3_blit_start()`, `st7789p3_blit_push()`, `evk_gfx_text_at()`, `evk_gfx_text_centered()`, `evk_gfx_splash()` | same |
| Camera | `evk_cam.h` | `evk_cam_start()`, `evk_cam_stop()`, `evk_cam_set_frame_cb()`, `evk_cam_set_npu_input()`, `evk_cam_set_npu_frame_cb()`, `evk_cam_npu_rearm()` | `CONFIG_EVK_CAMERA=y` |
| Microphone | `evk_mic.h` | `evk_mic_start()`, `evk_mic_read()`, `evk_mic_stop()`, `evk_mic_set_gain_db()` | `CONFIG_EVK_AUDIO=y` |
| Speaker | `evk_spk.h`, `evk_pcm.h` | `evk_spk_open()`, `evk_spk_write()`, `evk_spk_tone()`, `evk_spk_set_volume()`, `evk_spk_close()`; `evk_pcm_*` is integer PCM math | `CONFIG_EVK_AUDIO=y` |
| microSD | `evk_sd.h` | `evk_sd_present()`, `evk_sd_mount()`, `evk_sd_exists()`, `evk_sd_unmount()`; the file system is mounted at `sd:/` | `CONFIG_EVK_SDCARD=y` |
| Shell commands | — | `lcd`, `cam`, `mic`, `spk`, `sd` | `CONFIG_EVK_SHELL=y` (leave it off if the application has its own commands with these names) |

Each block needs further options; the camera, for example, needs `CONFIG_MM_SUPPORT=y`, `CONFIG_COMPONENTS_SENSOR_ENABLE=y` and `CONFIG_USE_PSRAM=y`. The full list is in the SDK's `components/board/ipro7ai_evk/README.md`. When the camera, audio or SD card block is missing a required option, CMake stops at configure time.

```c title="Board init and camera start (from ipro7ai_evk_launcher)"
#include "evk.h"

static void app_task(void *param)
{
    evk_begin();                    /* camera parked, amp off, panel up */
    if (evk_cam_start() != EVK_CAM_OK) {
        IPRO_LOGE(LOG_TAG, "camera start failed");
    }
    /* ... */
}
```

## AI inference runtime { #ai-runtime }

The NPU inference runtime ships as the prebuilt library `components/ai/lib/libai.a`; the SDK includes only its headers. Set `CONFIG_AI_SUPPORT=y` in the application's `.config`, and set `CONFIG_USE_PSRAM=y` explicitly — the build does not add it for you.

| API | Header | Purpose |
|---|---|---|
| `iproai_npu_init()` | `components/ai/src/inst/include/iproai_inst_npu.h` | Initialize the NPU; call once before creating a model |
| `iproai_create()` | `components/ai/src/core/include/iproai_core.h` | Create a model handle (`iproai_model_hdl_t`); returns `NULL` on failure |
| `iproai_load_model_from_buffer(hdl, buf)` | same | Load an `.inm` model from memory, e.g. linked into the firmware or read over XIP from the `mfg` partition |
| `iproai_load_model_from_file(hdl, path)` | same | Load a model from the SD card using a FatFS `sd:/...` path; needs `CONFIG_AI_MODEL_FROM_FILE=y` |
| `iproai_getNetInfo(hdl)` | same | Model information (input size, layer count, NPU layer count) |
| `iproai_setResultCB(hdl, cb)`, `iproai_setCustom_Postproc_CB(hdl, cb)` | same | Result callback, custom post-processing callback |
| `iproai_startCompute(hdl)` | same | Run one inference |
| `iproai_getInputBuffer()`, `iproai_getOutputBuffer()`, `iproai_getInputResolution()`, `iproai_setSourceResolution()` | same | Input and output buffers and resolutions |
| `iproai_free(hdl)` | same | Release the model |
| `NPU_Img_Ext_Addr_Cfg(addr)` | `bsp/hal/inc/hal_npu.h` | Set the address the NPU reads the input image from |

The functions return `IPROAI_Status_e` (`components/ai/iproai_def.h`); success is `IPROAI_STATUS_NO_ERROR`.

```c title="Load a model from the SD card and run it (after ipro_ai_link)"
#include "iproai_core.h"
#include "hal_npu.h"
#include "drv_glb.h"

GLB_PER_Clock_UnGate(GLB_AHB_CLOCK_MM);
iproai_npu_init();

iproai_model_hdl_t hdl = iproai_create();
if (hdl == NULL ||
    iproai_load_model_from_file(hdl, "sd:/model.inm") != IPROAI_STATUS_NO_ERROR) {
    /* handle the error */
}
iproai_setResultCB(hdl, on_result);

/* Each inference: the first 4 bytes of the input buffer are a size header; the image starts at +4 */
NPU_Img_Ext_Addr_Cfg((uint32_t)(uintptr_t)(input + 4));
if (iproai_startCompute(hdl) != IPROAI_STATUS_NO_ERROR) {
    /* handle the error */
}
```

The model conversion tools are not included in V2.1.0; contact INTELPRO. Model storage options and the NPU memory budget are covered in [AI & NPU](../guides/ai-npu.md).

## Related documents { #related }

- [BLE Development](../guides/ble.md): controller selection, bring-up order and GATT examples.
- [Build System & Configuration](../guides/build-system.md): `.config` and application structure.
- [Debugging & Troubleshooting](debugging.md): logs, crash output and FreeRTOS hook messages.
- IPRO7 API specification: see [Documents](../documents/index.md).
