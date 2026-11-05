---
title: "API 参考"
description: "IPRO 专有公开 C API：由 SDK V2.1.0 头文件通过 Doxygen 生成的分类参考，以及平台初始化、BLE 控制器启动与日志的用法说明。"
migrate_from:
  - "api-reference.html — 第 3 階段改由 Doxygen 產生"
---

# API 参考

IPRO 专有的公开 C API。下方“API 分类”由 SDK V2.1.0 随附的公开头文件通过 Doxygen 生成，每个函数、类型与宏都附有头文件中的说明；其后几节说明平台初始化、BLE 控制器启动与日志的用法。Zephyr Bluetooth 的 `bt_*` API 不在此重复，请直接查阅 [Zephyr 官方文档](#ble-host)。

!!! note "适用范围"
    本页的 HAL 与平台 API 用于 FreeRTOS 应用。Zephyr 应用请使用 Zephyr 的设备驱动 API，见 [Zephyr RTOS](../../guides/zephyr.md)。

## API 分类 { #groups }

按功能分类的完整参考，生成自 SDK V2.1.0 的公开头文件。

<!-- BEGIN generated: api-groups -->
| 分类 | 头文件数 | 函数 | 内容 |
|---|---|---|---|
| [平台与系统](platform.md) | 11 | 65 | FreeRTOS 启动与钩子、HAL 公共定义、系统控制、时钟、定时器、看门狗、RTC 与内存分配辅助。 |
| [内存、Flash 与启动](memory-boot.md) | 5 | 45 | Flash 读写、PSRAM、boot2 与分区表管理。 |
| [电源管理与低功耗](power.md) | 4 | 52 | 电源模式、PDS 休眠与唤醒，以及低功耗框架与低功耗 UART。 |
| [外设 I/O](peripherals.md) | 13 | 62 | GPIO、UART、SPI、I2C、PWM、ADC、DAC、模拟比较器、KeyScan、QDEC 与 DMA。 |
| [音频](audio.md) | 3 | 16 | 音频 ADC（PDM 与模拟麦克风）与 I2S。 |
| [摄像头与图像](camera.md) | 4 | 36 | DVP 摄像头接口、ISP，以及硬件 MJPEG 编码与解码。 |
| [SD 卡与 SDIO](sd-sdio.md) | 4 | 61 | 硬件 SD 主机、SDIO，以及用 PIO 实现的 SD 主机。 |
| [以太网](ethernet.md) | 3 | 27 | EMAC、lwIP 网络接口与以太网 PHY。 |
| [PIO](pio.md) | 3 | 24 | 可编程 I/O：CCI、CMSIS-DAP 与扫描接口。 |
| [安全引擎](security.md) | 9 | 49 | AES、GMAC、哈希、DSA、ECDSA、P-256 与硬件随机数。 |
| [无线与 BLE 控制器](wireless-ble.md) | 7 | 41 | 无线电初始化，以及 IPRO BLE 控制器的启动、HCI 传输、低功耗与 NVDS 接口。 |
| [AI 运行库](ai.md) | 18 | 133 | NPU 驱动、推理核心、算子与后处理，以及检测与语音模型的接口。 |
<!-- END generated: api-groups -->

## 平台初始化与 FreeRTOS 钩子 { #rtos-platform }

所有 FreeRTOS 应用共用 `components/os/freertos/freertos_app_hooks`，它提供平台初始化，以及堆、FreeRTOS 钩子与 assert 的默认实现。

| API | 头文件 | 用途 |
|---|---|---|
| `void ipro_platform_init(void)` | `components/os/freertos/freertos_app_hooks.h` | 在 `main()` 开头调用一次。依次执行 `platform_init()`、`ipro_setup_heap()`、`hal_boot2_init()`、PSRAM 检查、`ipro_log_init()`（`CONFIG_IPRO_LOG_ENABLE`）、shell 初始化（`CONFIG_SHELL`）与 `ipro_pm_init()`（`CONFIG_IPRO_PM`）。 |
| `void ipro_setup_heap(void)` | 同上 | 从链接器符号收集 OCRAM 与 PSRAM（若启用）的堆区段，调用 `vPortDefineHeapRegions()`。`ipro_platform_init()` 已调用它，应用无需再调用。 |
| `void ipro_dump_task_stacks(const char *where)` | 同上 | 打印每个任务的栈最低剩余量（字节）与剩余堆；需要 `configUSE_TRACE_FACILITY=1`。 |

下列 FreeRTOS 钩子在 `components/os/freertos/freertos_app_hooks.c` 中以弱符号（weak）提供默认实现。要覆盖时，在应用自己的源文件中定义同名的非弱符号函数即可，链接器会自动采用。

| 钩子 | 默认行为 |
|---|---|
| `vApplicationStackOverflowHook()` | 打印 `[!] Stack overflow: <任务名称>` 与各任务栈剩余量，然后停住。 |
| `vApplicationMallocFailedHook()` | 打印请求大小、剩余堆与历史最低剩余堆、调用者地址与任务名称，然后停住；`pvPortMalloc(0)` 只给出警告。 |
| `vApplicationIdleHook()` | 执行 `__WFI()`。 |
| `vApplicationGetIdleTaskMemory()`、`vApplicationGetTimerTaskMemory()` | 提供 Idle 与 Timer 任务的静态栈与 TCB。 |
| `vAssertCalled()` | 关闭中断，打印 `[!] ASSERT <文件>:<行号>` 与调用者地址，然后停住。 |

```c title="main.c（最小应用骨架，取自 SDK README）"
#include "freertos_app_hooks.h"
#include <FreeRTOS.h>
#include <task.h>

static void app_task(void *arg)
{
    for (;;) {
        /* 应用代码 */
    }
}

int main(void)
{
    ipro_platform_init();   /* 堆、boot2、日志、shell */
    xTaskCreate(app_task, "app", 1024, NULL, 5, NULL);
    vTaskStartScheduler();
    for (;;) {}
}
```

!!! warning "不要重复初始化"
    `ipro_platform_init()` 已初始化 shell 与日志，请勿在应用中再调用一次。也不要把堆、钩子或 assert 的样板代码加回 `main.c`。

FreeRTOS 内核（V11.1.0）本身的 API（`xTaskCreate()`、队列、信号量等）请见 [FreeRTOS API 参考](https://www.freertos.org/Documentation/02-Kernel/04-API-references/01-Task-creation/00-TaskHandle)。`xTaskCreate()` 的栈深度单位是 word，不是字节。

## BLE 控制器启动 { #ble-core }

BLE 由 Zephyr v4.4.0 Host 与 IPRO BLE 控制器（预编译库）组成，两者通过内存中的 HCI 字节流相连。应用必须依次启动控制器、HCI 驱动与 Host。

| API | 头文件 | 用途 |
|---|---|---|
| `int ipro_ble_ctlr_controller_init(unsigned int task_priority)` | `components/wireless/bluetooth/ipro_ble_controller/include/ipro_ble_controller.h` | 启动控制器并创建控制器任务。返回 0 表示成功、-1 表示已启动、-2 表示创建任务失败。控制器须满足射频时序，优先级应高于应用任务；随附应用使用 `configMAX_PRIORITIES - 1`。 |
| `int hci_driver_ipro_ble_ctlr_init(void)` | `components/wireless/bluetooth/ipro_bt_host/port/include/hci_driver_ipro_ble_ctlr.h` | 在 `bt_enable()` 之前调用。Zephyr 4.4 在构建时就绑定 HCI 设备，此函数为与现有应用保持源码兼容而保留，随附应用仍按此顺序调用。 |
| `void ipro_ble_ctlr_hcitl_host_ready(void)` | `components/wireless/bluetooth/ipro_ble_controller/hcitl/ipro_ble_ctlr_hcitl.h`（由 `ipro_ble_controller.h` 引入） | 在 `bt_enable()` 的就绪回调中调用，标记 HCI 初始化完成；之后控制器可以在事件之间休眠。 |
| `int bt_enable(bt_ready_cb_t cb)` | `<zephyr/bluetooth/bluetooth.h>` | 启动 Host，完成时调用 `cb`。见 [Zephyr Bluetooth API](#ble-host)。 |

三个调用之间各等待 50 ms，在 FreeRTOS 任务中执行；完整的启动代码与就绪回调见 [BLE 开发](../../guides/ble.md#ble-init)。

控制器库由 `.config` 中的 `CONFIG_IPRO_BLE_CTLR_LIB`、`CONFIG_IPRO_BLE_CTLR_FEATURE` 与 `CONFIG_IPRO_BLE_CTLR_CFG_DBG` 选择，对照表见 [BLE 开发](../../guides/ble.md#controller-variants)。

## Zephyr Bluetooth API { #ble-host }

应用使用 Zephyr 的 `bt_*` 回调式 API，头文件以 `<zephyr/bluetooth/...>` 引入；SDK 内的副本位于 `components/wireless/bluetooth/ipro_bt_host/upstream/zephyr/include/zephyr/bluetooth/`。下列链接均指向 Zephyr v4.4.0 版文档，与 SDK 导入的 Host 版本一致。

| 主题 | 常用 API | Zephyr v4.4.0 文档 |
|---|---|---|
| Bluetooth API 总览 | — | [Bluetooth API](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/index.html) |
| GAP：启动、广播、扫描 | `bt_enable()`、`bt_le_adv_start()`、`bt_le_scan_start()` | [Generic Access Profile (GAP)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gap.html) |
| 连接管理 | `bt_conn_cb_register()`、`bt_conn_le_create()`、`bt_conn_disconnect()` | [Connection Management](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/connection_mgmt.html) |
| GATT 服务器与客户端 | `BT_GATT_SERVICE_DEFINE()`、`bt_gatt_notify()`、`bt_gatt_discover()` | [Generic Attribute Profile (GATT)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gatt.html) |
| LE Audio | BAP、PACS、ASCS、CAP | [Bluetooth Audio](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/audio/audio.html) |
| 配对数据存储 | `settings_load_subtree()` | [Settings](https://docs.zephyrproject.org/4.4.0/services/settings/index.html) |
| 完整函数索引 | — | [Zephyr API 文档（Doxygen）](https://docs.zephyrproject.org/4.4.0/doxygen/html/group__bluetooth.html) |

!!! tip "以 SDK 内的头文件为准"
    Zephyr 文档以 Zephyr 内核为前提；在 FreeRTOS 应用中，Host 通过 SDK 的移植层运行，相关的 `CONFIG_BT_*` 项写在应用的 `.config` 中。宏是否存在请以 SDK 内的头文件为准，例如可连接广播可用 `BT_LE_ADV_CONN_FAST_1`，而 `BT_LE_ADV_CONN_NAME` 在此版本的 Host 中不存在。

## 日志 { #log-api }

头文件：`components/utils/include/ipro_log.h`（配置默认值在 `ipro_log_config.h` 中）。需要 `CONFIG_IPRO_LOG_ENABLE=y`；`ipro_platform_init()` 会以默认配置调用 `ipro_log_init()`。

| API | 用途 |
|---|---|
| `IPRO_LOGE`、`IPRO_LOGW`、`IPRO_LOGI`、`IPRO_LOGD`、`IPRO_LOGV`（`tag, format, ...`） | 错误、警告、信息、调试、详细级别的日志。级别高于 `CONFIG_LOG_DEFAULT_LEVEL` 的调用不会输出 |
| `IPRO_LOG_BUFFER_HEX(tag, buf, len)`、`IPRO_LOG_BUFFER_HEXDUMP(tag, buf, len)` | 以十六进制（加 ASCII）转储缓冲区 |
| `ipro_log_set_level()`、`ipro_log_get_level()`、`ipro_log_level_enabled()` | 运行时调整或查询级别 |
| `ipro_log_set_output_func()` | 改用自定义输出函数 |

`CONFIG_LOG_DEFAULT_LEVEL` 是整数：1 错误、2 警告、3 信息（随附应用的配置）、4 调试、5 详细。输出格式为 `<级别字母> (<时间>) <TAG>: <消息>`。

```c title="日志（每个文件定义自己的 TAG）"
#include "ipro_log.h"

#define TAG "MY_MODULE"

IPRO_LOGI(TAG, "connected, handle %u", handle);
IPRO_LOGE(TAG, "init failed (err %d)", err);
```

## 相关文档 { #related }

- [BLE 开发](../../guides/ble.md)：控制器选择、初始化顺序与 GATT 示例。
- [构建系统与配置](../../guides/build-system.md)：`.config` 与应用结构。
- [调试与故障排除](../debugging.md)：日志、崩溃输出与 FreeRTOS 钩子的信息。
- IPRO7 API 规格书：见[文档下载](../../documents/index.md)。
