---
title: "创建第一个自己的应用"
description: 从空目录开始，在 IPRO7AI Reef EVK 上写出自己的 FreeRTOS 应用：让 RGB LED 闪烁、读取按键、添加 shell 命令，并用 SDK 的日志 API 输出信息。
---

# 创建第一个自己的应用

本教程从一个空目录开始，在 IPRO7AI Reef EVK 上创建应用 `my_reef_app`：启动时打印信息、让 RGB LED 闪烁、按 SW3／SW4／SW5 切换颜色，并添加自己的 shell 命令 `myapp`。每一步都给出要输入的命令或代码，以及开发板上应该看到的结果。完成后，[测试你的应用](testing.md)会用同一个应用演示自动化测试。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK，SW7 拨到 CAM、SW8 拨到 PWR，用 USB-C 供电；U6 接 IPRO Debug Probe 或 3.3 V USB 转 UART 线（接法见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。
- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)：工具链可用，`make -C apps/platform/ipro7ai_reef_demo` 能构建成功，也烧录过一次。
- IntelProCube v0.6.3 命令行烧录工具（`ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`），需另行获取。烧录与控制台的通用步骤见[烧录与串口](../get-started/flash-and-monitor.md)。
- 一个可输入命令的串口终端程序，设为 115200 baud、8N1。

所有命令都在 SDK 根目录（下文用 `<SDK>` 表示）执行。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **创建应用目录并复制 Makefile**：应用必须放在 `apps/` 下两层（`apps/<类别>/<应用>`），因为 Makefile 通过 `../../../` 找到 SDK 根目录。类别名称可自定义，本教程使用 `custom`。

    ```bash
    mkdir -p apps/custom/my_reef_app
    cp apps/platform/ipro7ai_reef_demo/Makefile apps/custom/my_reef_app/
    ```

    Makefile 只是把构建交给 SDK 根目录的 `project.build`，不需要修改。

2. **创建 `.config`**：内容取自出厂固件 `apps/platform/ipro7ai_reef_demo/.config`，只保留芯片、Reef 板级、PSRAM、控制台、FreeRTOS、shell 和日志，去掉音频、USB、摄像头和 SD 卡。

    ```ini title="apps/custom/my_reef_app/.config"
    # my_reef_app: first application on the IPRO7AI Reef EVK.
    CONFIG_IPRO7=y
    CONFIG_CHIP="IPRO7"
    CONFIG_CPU_ID="intelpro_ipro7"
    CONFIG_CROSS_COMPILE="/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-"
    CONFIG_IPRO7AI_REEF=y
    CONFIG_BOARD="IPRO7AI_REEF"

    # Build
    CONFIG_LINK_FLASH=y
    CONFIG_PARTITION=y
    CONFIG_ENABLE_FRAME_POINTER=y
    CONFIG_EXCEPTION_DUMP=y

    # Memory: Kconfig `select` is not applied, so PSRAM is set explicitly.
    CONFIG_USE_PSRAM=y
    # CONFIG_AI_SUPPORT is not set

    # Console on UART0 (U6), 115200 8N1
    CONFIG_PLATFORM_UART_BAUDRATE=115200

    # FreeRTOS
    CONFIG_FREERTOS_SUPPORT=y
    CONFIG_COMPONENTS_FREERTOS_ENABLE=y
    CONFIG_FREERTOS=y
    CONFIG_IPRO_OSAL=y
    CONFIG_FREERTOS_HZ=1000
    CONFIG_MAIN_TASK_STACK_SIZE=4096
    CONFIG_FREERTOS_TIMER_TASK_STACK_WORDS=1024

    # Shell and logging
    CONFIG_SHELL=y
    CONFIG_SHELL_EXEC_THREAD=y
    CONFIG_COMPONENTS_SOFTCRC_ENABLE=y
    CONFIG_COMPONENTS_UTILITY_API_ENABLE=y
    CONFIG_COMPONENTS_NEW_LIBC_ENABLE=y
    CONFIG_IPRO_LOG_ENABLE=y
    CONFIG_LOG_BUFFER_SIZE=256
    CONFIG_LOG_COLORS=y
    CONFIG_LOG_DEFAULT_LEVEL_INFO=y
    CONFIG_LOG_DEFAULT_LEVEL=3
    CONFIG_LOG_OUTPUT_UART=y
    CONFIG_LOG_TIMESTAMP=y
    CONFIG_LOG_USE_MUTEX=y
    ```

    第一行注释会成为 `./build_freertos.sh -l` 列出的应用说明。构建系统按文件内容原样读取 `.config`，不应用 Kconfig 的 `select` 和默认值，所以 PSRAM 等选项要显式写出。

3. **创建 `CMakeLists.txt`**：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt"
    # my_reef_app: first application on the IPRO7AI Reef EVK.

    __component_add_include_dirs(.)

    __set_main_file(main.c)
    setup_project(my_reef_app)
    ```

    `setup_project()` 中的名称决定输出文件名：`my_reef_app_IPRO7.bin`。

4. **创建 `main.c`**：`ipro_platform_init()` 一次完成内存堆、boot2、日志和 shell 的初始化；FreeRTOS 的 hook、heap 和 assert 已由 SDK 提供默认实现，`main.c` 无需再写。

    ```c title="apps/custom/my_reef_app/main.c"
    /* my_reef_app: first application on the IPRO7AI Reef EVK. */
    #include <stdint.h>

    #include <generated/autoconf.h>
    #include <FreeRTOS.h>
    #include <task.h>

    #include "freertos_app_hooks.h"
    #include "ipro_log.h"

    #define LOG_TAG "MYAPP"

    static void app_task(void *param)
    {
        uint32_t n = 0;

        (void)param;
        for (;;) {
            IPRO_LOGI(LOG_TAG, "alive %lu", (unsigned long)n++);
            vTaskDelay(pdMS_TO_TICKS(2000));
        }
    }

    int main(void)
    {
        ipro_platform_init();   /* heap, boot2, log, shell */

        IPRO_LOGI(LOG_TAG, "Hello from my_reef_app");

        xTaskCreate(app_task, "my_app", 1024, NULL, 5, NULL);
        vTaskStartScheduler();
        while (1) {
        }
        return 0;
    }
    ```

    `IPRO_LOGI()`、`IPRO_LOGW()`、`IPRO_LOGE()` 是 SDK 的日志 API（`ipro_log.h`），每个文件使用自己的 `LOG_TAG`。`xTaskCreate()` 的栈大小以 word 为单位，1024 即 4 KB。

5. **构建**：

    ```bash
    make -C apps/custom/my_reef_app
    ```

    成功时最后打印内存占用和输出文件（数字随版本略有不同）：

    ```text
    Memory region         Used Size  Region Size  %age Used
               flash:       92080 B         1 MB      8.78%
               psram:        9368 B         8 MB      0.11%
               ocram:       29840 B       256 KB     11.38%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin
    ```

    也可以用 `./build_freertos.sh build my_reef_app`，它会自动找到 `apps/custom/my_reef_app`。

6. **进入下载模式并烧录**：按住 SW1（BOOT），按一下 SW2（RESET），再松开 SW1。然后在 IntelProCube 目录下执行（分区表与出厂固件相同）：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\custom\my_reef_app\build\build_out\my_reef_app_IPRO7.bin
        ```

    工具即使失败也会以 0 退出，请确认输出中有 `[All Success]`。使用 IPRO Debug Probe 时，端口是名称以 `02` 结尾的那一个。

7. **打开控制台并复位**：以 115200 baud 打开同一个串口，按一下 SW2。每行日志开头有级别、时间戳和线程编号，以下省略：

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: alive 0
    MYAPP: alive 1
    MYAPP: alive 2
    ```

    在控制台输入 `help`，会列出 SDK 内置的 shell 命令，例如 `ps`、`free`、`reboot` 和 `reboot_dl`。之后要重新烧录时，在控制台输入 `reboot_dl` 就能进入下载模式，无需按键。

8. **让 RGB LED 闪烁**：Reef 的 WS2812 RGB LED 接在 GPIO24 上，驱动程序 `rgb_led.c` 随出厂固件提供。与 `ipro_ble_remote` 的 Reef 配置一样，直接引用它，不要复制。把 `CMakeLists.txt` 改为：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt"
    # my_reef_app: first application on the IPRO7AI Reef EVK.

    __component_add_include_dirs(.)

    # Reef board drivers from the out-of-box demo, used in place (not copied).
    set(REEF_DEMO_SRC ${CMAKE_SOURCE_DIR}/apps/platform/ipro7ai_reef_demo/src)
    __component_add_include_dirs(${REEF_DEMO_SRC})
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
    )

    __set_main_file(main.c)
    setup_project(my_reef_app)
    ```

    把 `main.c` 替换为下面的内容。颜色以 `0xRRGGBB` 存放在一个 32 位变量中，闪烁周期为 0 时常亮：

    ```c title="apps/custom/my_reef_app/main.c"
    /* my_reef_app: first application on the IPRO7AI Reef EVK. */
    #include <stdint.h>
    #include <stdbool.h>

    #include <generated/autoconf.h>
    #include <FreeRTOS.h>
    #include <task.h>

    #include "freertos_app_hooks.h"
    #include "ipro_log.h"
    #include "board_config.h"
    #include "rgb_led.h"

    #define LOG_TAG "MYAPP"

    static volatile uint32_t s_rgb      = 0x002800;  /* 0xRRGGBB: dim green */
    static volatile uint32_t s_blink_ms = 500;       /* 0 = steady on */

    static void led_show(uint32_t rgb)
    {
        (void)rgb_led_set((uint8_t)(rgb >> 16), (uint8_t)(rgb >> 8), (uint8_t)rgb);
    }

    static void app_task(void *param)
    {
        bool on = false;

        (void)param;
        if (rgb_led_init() != 0) {
            IPRO_LOGE(LOG_TAG, "RGB LED init failed");
        }
        IPRO_LOGI(LOG_TAG, "blinking the RGB LED on GPIO%d", BOARD_RGB_LED_PIN);

        for (;;) {
            uint32_t period = s_blink_ms;

            on = (period == 0) ? true : !on;
            led_show(on ? s_rgb : 0);
            vTaskDelay(pdMS_TO_TICKS(period ? period : 100));
        }
    }

    int main(void)
    {
        ipro_platform_init();   /* heap, boot2, log, shell */

        IPRO_LOGI(LOG_TAG, "Hello from my_reef_app");

        xTaskCreate(app_task, "my_app", 1024, NULL, 5, NULL);
        vTaskStartScheduler();
        while (1) {
        }
        return 0;
    }
    ```

    重新构建（步骤 5）、在控制台输入 `reboot_dl` 后烧录（步骤 6）、按 SW2 复位。控制台打印 `MYAPP: blinking the RGB LED on GPIO24`，LED 以暗绿色每 0.5 秒亮灭一次。`board_config.h` 根据 `CONFIG_IPRO7AI_REEF` 选用 Reef 的引脚定义，`BOARD_RGB_LED_PIN` 等宏都来自那里。

9. **读取按键**：Reef 上可读取的按键有 SW1（BOOT，GPIO41，高电平有效）、SW3（GPIO10）、SW4（GPIO27）和 SW5（GPIO11，后三者低电平有效）；SW2 是硬件复位，读不到。出厂固件的 `keys.c` 以 10 ms 轮询并消抖。在 `CMakeLists.txt` 的 `target_sources` 中加入一行：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt（节选）"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
    )
    ```

    在 `main.c` 的 `#include "rgb_led.h"` 下面加入 `#include "keys.h"`，在 `led_show()` 之后加入按键回调：

    ```c title="apps/custom/my_reef_app/main.c（添加）"
    /* Called from the keys poll task on every debounced press and release. */
    static void on_key(key_id_t key, bool pressed, void *ctx)
    {
        (void)ctx;
        if (!pressed) {
            return;
        }
        IPRO_LOGI(LOG_TAG, "%s pressed (%lu presses)", keys_name(key),
                  (unsigned long)keys_press_count(key));
        switch (key) {
        case KEY_SW3: s_rgb = 0x280000; break;   /* red */
        case KEY_SW4: s_rgb = 0x002800; break;   /* green */
        case KEY_SW5: s_rgb = 0x000028; break;   /* blue */
        default: break;                          /* SW1 (BOOT): log only */
        }
    }
    ```

    再在 `app_task()` 中 `rgb_led_init()` 代码块之后启动按键轮询：

    ```c title="apps/custom/my_reef_app/main.c（在 app_task 中添加）"
        if (keys_init() == 0) {
            keys_set_callback(on_key, NULL);
        } else {
            IPRO_LOGE(LOG_TAG, "keys init failed");
        }
    ```

    回调在按键轮询任务中执行，只做设置变量、记录日志这类简短的工作，不要在其中等待。重新构建、烧录并复位后，按 SW3，LED 变为红色闪烁，控制台打印：

    ```text
    MYAPP: SW3 pressed (1 presses)
    ```

    SW4、SW5 分别切换为绿色和蓝色。不要在按住 SW1 时按 SW2，那样会让开发板进入下载模式。

10. **添加自己的 shell 命令**：创建一个头文件，让 shell 命令通过函数读写应用状态：

    ```c title="apps/custom/my_reef_app/my_app.h"
    /* my_reef_app: state shared between the app task and the shell. */
    #ifndef MY_APP_H
    #define MY_APP_H

    #include <stdint.h>

    /* LED colour as 0xRRGGBB; blink half-period in ms (0 = steady on). */
    void     my_app_set_color(uint32_t rgb);
    uint32_t my_app_get_color(void);
    void     my_app_set_blink_ms(uint32_t ms);
    uint32_t my_app_get_blink_ms(void);

    #endif /* MY_APP_H */
    ```

    在 `main.c` 中加入 `#include "my_app.h"`，并在 `led_show()` 前面加入这四个函数：

    ```c title="apps/custom/my_reef_app/main.c（添加）"
    void my_app_set_color(uint32_t rgb)   { s_rgb = rgb & 0xFFFFFFu; }
    uint32_t my_app_get_color(void)       { return s_rgb; }
    void my_app_set_blink_ms(uint32_t ms) { s_blink_ms = ms; }
    uint32_t my_app_get_blink_ms(void)    { return s_blink_ms; }
    ```

    创建 `app_cli.c`。命令用 `SHELL_CMD_EXPORT_ALIAS(函数, 命令名称, 说明)` 注册，整个文件用 `#ifdef CONFIG_SHELL` 包起来，这样关闭 shell 的构建（例如低功耗配置）才不会引用 shell 的 API：

    ```c title="apps/custom/my_reef_app/app_cli.c"
    /* my_reef_app: the `myapp` shell command. */
    #include <generated/autoconf.h>

    #ifdef CONFIG_SHELL

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    #include "shell.h"
    #include "keys.h"
    #include "my_app.h"

    static void print_status(void)
    {
        uint32_t rgb = my_app_get_color();

        printf("LED (%lu,%lu,%lu), blink %lu ms\n",
               (unsigned long)((rgb >> 16) & 0xFF), (unsigned long)((rgb >> 8) & 0xFF),
               (unsigned long)(rgb & 0xFF), (unsigned long)my_app_get_blink_ms());
        for (int k = 0; k < KEY_COUNT; k++) {
            printf("%s: %s, %lu presses\n", keys_name((key_id_t)k),
                   keys_is_pressed((key_id_t)k) ? "down" : "up",
                   (unsigned long)keys_press_count((key_id_t)k));
        }
    }

    static int cmd_myapp(int argc, char **argv)
    {
        if (argc < 2 || strcmp(argv[1], "status") == 0) {
            print_status();
        } else if (strcmp(argv[1], "color") == 0 && argc == 5) {
            int r = atoi(argv[2]), g = atoi(argv[3]), b = atoi(argv[4]);

            if (r < 0 || r > 255 || g < 0 || g > 255 || b < 0 || b > 255) {
                printf("values are 0..255\n");
                return -1;
            }
            my_app_set_color(((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b);
            printf("LED (%d,%d,%d)\n", r, g, b);
        } else if (strcmp(argv[1], "blink") == 0 && argc == 3) {
            int ms = atoi(argv[2]);

            if (ms < 0 || ms > 5000) {
                printf("blink is 0..5000 ms (0 = steady on)\n");
                return -1;
            }
            my_app_set_blink_ms((uint32_t)ms);
            printf("blink %d ms\n", ms);
        } else {
            printf("myapp [status] | myapp color <r> <g> <b> | myapp blink <ms>\n");
        }
        return 0;
    }
    SHELL_CMD_EXPORT_ALIAS(cmd_myapp, myapp, my_reef_app LED and keys);

    #endif /* CONFIG_SHELL */
    ```

    最后把 `CMakeLists.txt` 改成完整版本。shell 命令是通过链接段找到的，代码中没有任何地方直接调用它，所以应用的库必须整体链接进来，否则命令会被链接器丢弃：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt"
    # my_reef_app: first application on the IPRO7AI Reef EVK.

    __component_add_include_dirs(.)

    # Reef board drivers from the out-of-box demo, used in place (not copied).
    set(REEF_DEMO_SRC ${CMAKE_SOURCE_DIR}/apps/platform/ipro7ai_reef_demo/src)
    __component_add_include_dirs(${REEF_DEMO_SRC})
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
        app_cli.c
    )

    # SHELL_CMD_EXPORT_ALIAS casts the handler to the shell's generic type.
    target_compile_options(app PRIVATE -Wall -Wextra -Wno-cast-function-type)

    # Shell commands are found through their linker section, never called by name,
    # so the app archive must be linked whole or the commands are dropped.
    set_property(GLOBAL APPEND PROPERTY SDK_LIBS app)
    set_property(GLOBAL APPEND PROPERTY SDK_WHOLE_ARCHIVE_LIBS app)

    __set_main_file(main.c)
    setup_project(my_reef_app)
    ```

11. **构建、烧录并试用命令**：重新构建、`reboot_dl`、烧录、按 SW2。在控制台输入：

    ```text
    myapp status
    ```

    ```text
    LED (0,40,0), blink 500 ms
    BOOT/SW1: up, 0 presses
    SW3: up, 0 presses
    SW4: up, 0 presses
    SW5: up, 0 presses
    ```

    更改颜色并让 LED 常亮：

    ```text
    myapp color 0 0 80
    myapp blink 0
    ```

    ```text
    LED (0,0,80)
    blink 0 ms
    ```

    LED 变为蓝色常亮。输入 `help`，列表中出现 `myapp            - my_reef_app LED and keys`。

</div>

## 验证结果 { #verify }

- 启动信息中有 `MYAPP: Hello from my_reef_app` 和 `MYAPP: blinking the RGB LED on GPIO24`，LED 每 0.5 秒亮灭一次。
- 按 SW3、SW4、SW5 时 LED 切换为红、绿、蓝色，控制台打印 `<按键> pressed (<次数> presses)`。
- `myapp status` 显示当前颜色、闪烁周期和四个按键的按下次数；`myapp color` 和 `myapp blink` 立即改变 LED。

应用目录最后包含这些文件：

```text
apps/custom/my_reef_app/
├── .config
├── CMakeLists.txt
├── Makefile
├── app_cli.c
├── main.c
└── my_app.h
```

## 工作原理 { #how-it-works }

- **启动**：`main()` 调用 `ipro_platform_init()`（平台、内存堆、boot2、日志、shell），创建 `my_app` 任务后启动调度器。要替换某个 FreeRTOS hook（例如 `vApplicationIdleHook`），在自己的源代码中定义非 weak 版本即可，链接器会自动选用。
- **构建**：构建系统读取 `.config`，每个 `CONFIG_X=y` 都会成为全局的 `-DCONFIG_X=1`，同时也是 CMake 变量 `CONFIG_X`；`board_config.h` 根据板级配置选出引脚宏。`main.c` 单独编译进可执行文件，其他源代码编译进 `app` 库。
- **板级驱动**：`rgb_led.c`（GPIO24 经 SPI0 产生 WS2812 波形）和 `keys.c`（10 ms 轮询、30 ms 消抖）位于 `apps/platform/ipro7ai_reef_demo/src/`，在 CMake 中直接引用。`rgb_led_set()` 把一个颜色编码成 SPI 字节，在临界区内发出约 30 µs 的波形。
- **任务分工**：按键回调在轮询任务中执行，shell 命令在 shell 任务中执行，两者都只修改 `s_rgb` 和 `s_blink_ms`；真正调用 LED 驱动的只有 `my_app` 任务，所以不需要额外加锁。

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| `make` 找不到 `project.build` | 应用不在 `apps/` 下两层，Makefile 中的 `../../../` 指不到 SDK 根目录 | 放在 `apps/<类别>/<应用>`，或执行 `make IPRO_SDK_BASE=<SDK>` |
| 编译错误 `rgb_led.h: No such file or directory` | 没有加入出厂固件驱动的头文件路径 | 确认 `CMakeLists.txt` 中有 `__component_add_include_dirs(${REEF_DEMO_SRC})` |
| 输入 `myapp` 出现 `myapp: command not found.` | 应用的库没有整体链接，或 `.config` 中没有 `CONFIG_SHELL=y` | 确认 `CMakeLists.txt` 中有 `SDK_WHOLE_ARCHIVE_LIBS` 那一行以及 `app_cli.c` |
| 烧录成功但控制台没有输出 | 开发板还在下载模式，或波特率、排线方向不对 | 按 SW2；控制台设为 115200；U6 排线两端的线序必须对调（见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)） |
| 控制台有信息但 LED 不亮 | WS2812 由 USB VBUS 供电 | 用 USB-C 供电，不要只从 3.3 V 供电 |
| 烧录输出中没有 `[All Success]` | 未进入下载模式，或 `--chip-variant` 不对 | 先 `reboot_dl` 或按 SW1＋SW2；Reef 一律使用 `--chip-variant IPRO7AI` |

## 下一步 { #next-steps }

- [测试你的应用](testing.md)：为 `my_reef_app` 加上自检，用脚本和 `build_freertos.sh test` 自动执行。
- [构建与烧录流程](build-and-flash.md)：用 `build_freertos.sh` 串联构建、烧录和监视。
- [第一个 BLE 应用](first-ble-app.md)：在 Reef 上运行 GATT 参考应用并修改它。
- [BLE 开发](../guides/ble.md)：要让自己的应用加入 BLE 时，从控制器库和 `.config` 配置开始。
