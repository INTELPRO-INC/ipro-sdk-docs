---
title: "低功耗"
description: IPRO7 FreeRTOS 应用的 WFI、PDS 与 HBN：低功耗框架、配置、编程接口、内存保持与唤醒、BLE 与睡眠，以及在 Reef 上测量 IPRO7AI 的电流
migrate_from: []
---

# 低功耗

IPRO7 的 FreeRTOS 应用可使用三种省电状态：WFI（FreeRTOS tickless idle）、PDS（Power-Down Sleep，Level 31，唤醒后原地继续）与 HBN（Hibernate，唤醒时冷启动）。SDK 以预编译的低功耗框架 `hal_lp` 提供 PDS 的进入与恢复，并通过 `ipro_pm` 自动选择 WFI 或 PDS。在 IPRO7AI Reef EVK 上可以用 SW8 与 JP2 测量 IPRO7AI 本身的电流；随附的 Reef 配置文件都不会进入 PDS。

!!! abstract "要点"
    - 框架：`bsp/hal/lp_framework/ipro7/`（`hal_lp.h`、预编译的 `liblp_framework.a`）与 `hal_pm.h`；自动选择模式的 `components/sys/ipro_pm/`。
    - Reef：随附的 Reef 配置文件都没有使用 PDS。SW8 与 JP2 可以把电流表串入 IPRO7AI 的 3.3 V 电源。
    - 唤醒：PDS 可由 RTC 定时、GPIO 等来源唤醒；控制台 UART 无法唤醒 PDS。
    - 未包含：BLE 连接中的 PDS（需要从源代码构建控制器）。Zephyr 下没有低功耗模式。

## 低功耗模式 { #modes }

| 模式 | 进入方式 | 保持的内容 | 唤醒源 | 唤醒后 |
|---|---|---|---|---|
| WFI | FreeRTOS tickless idle（`CONFIG_FREERTOS_USE_TICKLESS_IDLE`） | 全部 | 任何中断 | 原地继续 |
| PDS（Level 31） | `hal_lp_enter()`，或底层的 `pm_pds_mode_enter(PM_PDS_LEVEL_31, …)` | OCRAM（见[保持与唤醒](#retention-wake)）、HBN RAM；可选择让 PSRAM 自刷新 | RTC 定时、GPIO、模拟比较器（ACOMP）、BLE | 原地继续；CPU、RF 与 MISC 电源域被复位，控制台 UART 与系统定时器要重新初始化 |
| HBN（Level 0） | `hal_lp_enter_fastboot()`，或底层的 `pm_hbn_mode_enter(PM_HBN_LEVEL_0, …)` | 只有 HBN RAM（4 KB）与 RTC | RTC 定时、AON 引脚、BOR、ACOMP | 从固件开头冷启动；用 `hal_lp_is_fastboot_wakeup()` 判断 |

## 架构 { #architecture }

| 层 | 位置 | 内容 |
|---|---|---|
| 应用 | 自己的程序 | 决定何时睡眠、保持哪些内容、由什么唤醒 |
| 自动模式选择 | `components/sys/ipro_pm/`（源代码） | 挂接在 FreeRTOS tickless idle 上，根据每段空闲时间与应用设定的限制选择 WFI 或 PDS |
| 低功耗框架 | `bsp/hal/lp_framework/ipro7/`：`hal_lp.h`、`lp_uart.h`、`lib/liblp_framework.a`（预编译，IPRO7 构建始终链接） | RTC 与 GPIO 唤醒、CPU 状态保存与还原、flash XIP 与 PSRAM 恢复、虚拟时间、RC32K 校准、唤醒 hook |
| 底层电源管理 | `bsp/hal/inc/hal_pm.h` | `pm_pds_mode_enter()`、`pm_hbn_mode_enter()`、`pm_pds_gpio_wakeup_set()`、`pm_pds_set_misc_keep()`、32 kHz 时钟源选择 |

## 配置 { #configuration }

```ini title="apps/test/ipro_lp_test/.config（节选）"
# CONFIG_USE_PSRAM is not set
CONFIG_HAL_LP=y
CONFIG_FREERTOS_IDLE_HOOK=y
CONFIG_PLATFORM_UART_BAUDRATE=115200
```

| 配置 | 说明 |
|---|---|
| `CONFIG_HAL_LP` | 通过 `hal_lp` 进入 PDS 的应用设置这一项（`ipro_lp_test`） |
| `CONFIG_FREERTOS_IDLE_HOOK` | 启用 `vApplicationIdleHook()`，应用可在其中于空闲时进入 PDS |
| `CONFIG_FREERTOS_USE_TICKLESS_IDLE` | FreeRTOS tickless idle；空闲时 CPU 进入 WFI |
| `CONFIG_IPRO_PM` | 启用 `ipro_pm`；另需 `CONFIG_FREERTOS_USE_TICKLESS_IDLE=1` 与 `CONFIG_FREERTOS_IDLE_HOOK=y`，否则构建会以 `#error` 停止 |
| `CONFIG_IPRO_PM_MAX_MODE` | 启动时允许的最深模式：0 active、1 WFI（默认）、2 native、3 PDS；运行中用 `ipro_pm_policy_set()` 调整 |
| `CONFIG_IPRO_PM_IDLE_PDS` | 由 idle 任务自行进入 PDS（BLE 控制器运行时不会）；同时设置 `CONFIG_IPRO_PM_TIMEBASE=y` |
| `CONFIG_IPRO_PM_SHELL` | `pm` shell 命令（状态、策略、`pm stats`） |

`.config` 会原样转换为 `autoconf.h`，Kconfig 的依赖关系不会被应用，相关配置都要写出来。

!!! warning "不能与 HOTCODE 选项同时使用"
    `CONFIG_IPRO7_BLE_HOTCODE` 与 `CONFIG_IPRO7_WIFI_HOST_HOTCODE` 不能与低功耗内存布局（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`、`CONFIG_OCRAM_NORET_SPLIT`）同时使用，生成 linker script 时会报错停止。在 Reef 上，`ipro7ai_reef_demo/defconfig_wifi_ipro6s` 使用 Wi-Fi 的选项，`ipro_throughput_test/defconfig_reef` 使用 BLE 的选项。

## 测试应用 ipro_lp_test { #lp-test }

`apps/test/ipro_lp_test` 是不含 BLE 与 PSRAM 的最小应用，用 RTC 唤醒测试 PDS Level 31，配置面向 IPRO7 EVB（`CONFIG_EVB=y`）。它的 `lp` shell 命令覆盖本页的各种情况：`lp sleep <ms>`（通过 `hal_lp` 进入 PDS）、`lp auto on|off`（空闲时进入 PDS）、`lp status`、`lp mem [ms]`（哪些 OCRAM 被保持下来）、`lp misc on|off`（MISC 电源域保持供电）、`lp fastboot <ms>`（HBN 冷启动唤醒）与 `lp wakectx`。可对照本页阅读它的 `src/lp_test_cli.c`。

## 编程接口 { #api }

以下流程参照 `apps/platform/ipro7_demo/demo/soc/peripheral/lowpower_demo.c`：初始化框架、注册唤醒 hook，再通过 RTC 定时进入 PDS。

```c title="通过 RTC 定时进入 PDS"
#include "hal_lp.h"

extern void shell_uart_reinit(void);
extern void vPortSetupTimerInterrupt(void);

static int wake_reinit(int wakeup_reason, void *arg)
{
    (void)wakeup_reason;
    (void)arg;
    shell_uart_reinit();          /* PDS 复位了控制台 UART */
    vPortSetupTimerInterrupt();   /* FreeRTOS 系统定时器 */
    /* 其他外设（I2C、SPI…）在这里重新初始化 */
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
        .psram_retention  = 1,     /* 有 PSRAM 时让它自刷新 */
        .ocram_retention  = 1,
    };
    hal_lp_result_t res;
    int ret = hal_lp_enter(&cfg, &res);   /* 返回唤醒原因（HAL_LP_WAKEUP_*）或负的错误码 */
    if (ret == HAL_LP_ERR_ENTRY_ABORTED) {
        /* 有中断待处理，芯片没有进入 PDS（相当于一次 WFI） */
    }
    return ret;
}
```

- `hal_lp_result_t` 报告唤醒原因、触发唤醒的 GPIO 与实际睡眠时间；`hal_lp_get_virtual_ms()` 提供跨越睡眠持续计数的时基。
- GPIO 唤醒：在 `hal_lp_cfg_t` 中设置 `gpio_wakeup_en` 与 `gpio_cfg`（`wakeup_mask`、触发方式、上下拉）；可用 GPIO0–31。
- 睡眠后 FreeRTOS 的 tick 计数不会自动补偿：像 `ipro_lp_test` 一样用 `xTaskCatchUpTicks()` 补上实际睡眠时间。
- HBN：调用 `hal_lp_enter_fastboot()` 后芯片以冷启动方式唤醒，这个调用不会返回。启动时用 `hal_lp_is_fastboot_wakeup()` 判断，并用 `hal_lp_get_wake_context()` 读取唤醒上下文；需要跨越 HBN 保持的数据必须事先放入 HBN RAM。

## 保持与唤醒 { #retention-wake }

- **OCRAM**：MISC 电源域断电时（默认），PDS31 只保持 OCRAM 的前 64 KB；`pm_pds_set_misc_keep()` 让 MISC 电源域保持供电，就会保持整个 OCRAM。唤醒后要用的数据请放在前 64 KB，或让 MISC 保持供电，并用 `ipro_lp_test` 的 `lp mem` 确认结果。
- **PSRAM**：`psram_retention` 让 PSRAM 在 PDS 期间自刷新，唤醒时由框架恢复。IPRO7AI（Reef 的 SoC）的 PSRAM 在封装内，PDS 期间必须保持自刷新。
- **HBN RAM**：4 KB，HBN 期间唯一保持的内存；框架的参数与 fastboot 唤醒上下文也放在这里。
- **控制台**：UART0 所在的电源域在 PDS31 时会被复位，唤醒后要重新初始化（`shell_uart_reinit()` 或 `platform_init()`）。控制台 RX 引脚（GPIO21，Reef 上是 U6 第 4 脚）无法唤醒 PDS，睡眠期间输入的字符会丢失。
- **GPIO 唤醒**：`hal_lp` 支持 GPIO0–31。底层的 `pm_pds_gpio_wakeup_set()`（`hal_pm.h`）可设置 GPIO0–41，但每四个引脚共用触发设置，且只有 ASYNC 触发有效（SYNC 需要 PDS 期间会停止的时钟）。HBN 只能由 AON 引脚唤醒。
- **32 kHz 时钟**：默认 RC32K；板上有 32 kHz 晶振时可用 `pm_pds_set_32k_src()` 切换。Reef 没有 32 kHz 晶振，使用 RC32K；框架附带 RC32K 校准。
- **Flash**：`flash_power_down = 1` 时睡眠期间 flash 断电，唤醒时由框架恢复 XIP。

## BLE 与睡眠 { #ble-sleep }

- `ipro_pm` 的 BLE 后端与 BLE 连接中的 PDS（`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`）会强制从源代码构建 BLE 控制器。控制器只以预编译库提供，因此无法用本 SDK 包构建。产品如需在 BLE 连接中省电，请联系 INTELPRO。
- `ipro_ble_remote/defconfig_reef` 有意不使用 PDS：Reef 由 USB 供电，摄像头与音频也需要时钟。
- `ipro_pdm_mic_demo`（IPRO7 EVB、IPRO7AI EVK）演示 BLE 配合 tickless WFI，以及手动进入 PDS 的 `pds [sec]` 命令。
- BLE 控制器组合、Exchange Memory 大小等配置见 [BLE 开发](ble.md)。

## 测量 { #measure }

- 用外接电表测量 SoC 的供电路径。在 Reef 上，SW8 与 JP2 会让 IPRO7AI 的 3.3 V 经过电表（步骤见下一节）；其他开发板见[电源与功耗测量](../hardware/power.md)。
- 确认芯片实际睡眠的次数与时间，并记录唤醒原因（`hal_lp_result_t`）。唤醒次数比预期多时，先检查定时器与待处理的中断（`hal_lp_enter()` 会返回 `HAL_LP_ERR_ENTRY_ABORTED`）。
- 使用 `ipro_pm` 时，`pm stats` 列出各模式的停留时间与估算电流。估算值只用于比较不同配置，不能代替实际测量。
- 用同一份固件比较 WFI 与 PDS，并在睡眠前等待 UART 输出发送完毕，以免被截断。

## 在 Reef 上动手实践 { #hands-on }

测量固件运行时 IPRO7AI 消耗的电流。随附的 Reef 配置文件都不会进入 PDS，所以这里用出厂固件比较“shell 空闲”与“摄像头管线运行”两种状态；换成自己的应用再做一次，就能在加入睡眠之前得到它的基准值。

需要：一台电流表（或源测量单元），以及连接 3 针 JP2 排针的测试线。

<div class="ipro-steps" markdown>

1. **配置**

    无需增加配置。`apps/platform/ipro7ai_reef_demo/.config` 没有任何低功耗配置（没有 `CONFIG_HAL_LP`、`CONFIG_IPRO_PM`），CPU 只会空闲。

2. **构建与烧录**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    进入下载模式（按住 SW1、按一下 SW2、松开 SW1）后，在 IntelProCube 目录执行：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    详见[烧录与串口](../get-started/flash-and-monitor.md)。

3. **把电表串入电源**

    拔掉 USB-C。电流表接在 JP2 第 1 脚（3V3）与第 2 脚（SOC）之间，SW8 拨到 **MEAS**，再插回 USB-C。读数只包含 IPRO7AI 的 3.3 V 引脚，不含摄像头、LED、功率放大器与 microSD 卡槽。

4. **读取空闲电流**

    以 115200 baud 打开控制台。启动时示例会先让摄像头停驻；出现 `ipro />` 提示符后，记下电表读数。

5. **启动摄像头管线并比较**

    ```text
    cam start
    cam stop
    cam park
    ```

    控制台依次响应 ``streaming - `cam status` in a second``、`stopped`、`PWDN high, RESETB low, XCLK off`。分别记下视频流进行中与 `cam park` 之后的读数：两者之差就是摄像头管线（XCLK、DVP 输入、ISP）在 SoC 上的功耗。

6. **恢复开发板**

    拔掉 USB-C，把 SW8 拨回 **PWR**，最后再拆下电表。SW8 在 MEAS 而 JP2 没接任何东西时，IPRO7AI 没有供电，外设的 3.3 V 却会经由 I/O 引脚倒灌。

</div>

下一步：按照[创建第一个自己的应用](../tutorials/first-own-app.md)开始动手，再按照[测试你的应用](../tutorials/testing.md)检查它的行为与电流。

## 本版本的限制 { #limitations }

- 随附的 IPRO7AI Reef EVK 配置文件都不会进入 PDS 或 HBN；`ipro_lp_test` 与 `ipro7_demo` 的低功耗命令面向 IPRO7 EVB。
- BLE 连接中的 PDS 无法用本 SDK 包构建（需要从源代码构建控制器）。
- Zephyr RTOS 下没有低功耗模式（`pm_state` 不会进入 PDS 或 HBN），见 [Zephyr RTOS](zephyr.md)。
- `CONFIG_IPRO_PM_IDLE_PDS`（由 idle 任务进入 PDS）没有随附示例，使用前请在自己的开发板上验证。
- 低功耗内存布局不能与 HOTCODE 选项同时使用。

## 相关文档 { #related }

- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：SW8、JP2 与电流测量步骤。
- [电源与功耗测量](../hardware/power.md)
- [BLE 开发](ble.md)
- [构建系统与配置](build-system.md)
- [Zephyr RTOS](zephyr.md)
