---
title: "测试你的应用"
description: 在 IPRO7AI Reef EVK 上测试自己的应用：控制台手动检查、出厂固件的硬件自检、在应用中加入打印判定结果的自检，再用 serial_monitor.py 和 build_freertos.sh test 自动执行，最后在电脑上运行主机端单元测试。
---

# 测试你的应用

本教程延续[创建第一个自己的应用](first-own-app.md)中的 `my_reef_app`。完成后，应用会有一个 `myapp selftest` 命令和启动自检，最后一行打印 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；您可以在控制台手动执行，也可以用一行命令或 CI 脚本自动烧录、复位并判定结果。

## 前提条件 { #prerequisites }

- 已完成[创建第一个自己的应用](first-own-app.md)，`apps/custom/my_reef_app` 能构建、烧录并响应 `myapp status`。
- IPRO7AI Reef EVK 用 USB-C 供电，U6 接 IPRO Debug Probe 或 USB 转 UART 线。
- 自动化部分（`tools/serial_monitor.py`、`build_freertos.sh`）需要 macOS 或 Linux 以及 Python 3.8 或更高版本：`serial_monitor.py` 使用 POSIX 的 termios，不需要 pyserial，但不能在 Windows 上运行。
- 主机端单元测试需要电脑上的 C 编译器（`cc`），不需要开发板和 RISC-V 工具链。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **在控制台手动检查**：打开控制台（115200 baud），依次输入下列命令，确认应用和系统状态：

    ```text
    myapp status
    ps
    free
    ```

    `myapp status` 打印 LED 颜色、闪烁周期和按键次数；`ps` 列出所有任务，其中应有 `my_app` 和 `keys`；`free` 打印 `Heap: total <总量>, free <剩余>, min free <最低剩余>`。按 SW3 后再输入一次 `myapp status`，SW3 的次数应加 1。这类检查适合开发过程中随手确认，但每次都需要人工查看。

2. **用出厂固件确认硬件**：怀疑是开发板本身的问题时，先烧录出厂固件 `ipro7ai_reef_demo`（构建与烧录见[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)），在控制台输入：

    ```text
    reef selftest
    ```

    约 3 秒内依次检查：LED 亮红、绿、蓝；扬声器发出 1 kHz 测试音；SD 卡座检测；摄像头探测：

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: <something seated | empty>, supply <on | off>
    [4/4] camera bus: <传感器名称> at 0x<地址>
    done - keys: press any and run `btn status`
    ```

    没接摄像头时第 4 项是 `no sensor`。这是靠看、靠听的硬件冒烟测试，结果需要人工判断；确认硬件正常后，再烧回自己的应用。

3. **在应用中加入自检**：自检要做三件事：逐项打印结果、最后打印固定的判定字符串、返回失败项数。创建 `selftest.c`：

    ```c title="apps/custom/my_reef_app/selftest.c"
    /* my_reef_app: self-test that prints a verdict test tools can wait for. */
    #include <stdio.h>
    #include <stdint.h>
    #include <stdbool.h>

    #include <FreeRTOS.h>
    #include <task.h>

    #include "rgb_led.h"
    #include "keys.h"
    #include "my_app.h"

    #define MIN_FREE_HEAP (16u * 1024u)

    static bool check(const char *name, bool ok)
    {
        printf("[selftest] %s: %s\n", name, ok ? "PASS" : "FAIL");
        return ok;
    }

    /* LED: show red, green and blue for 300 ms each and read each colour back. */
    static bool test_led(void)
    {
        static const uint8_t colours[3][3] = { { 40, 0, 0 }, { 0, 40, 0 }, { 0, 0, 40 } };
        bool ok = (rgb_led_init() == 0);

        for (int i = 0; i < 3 && ok; i++) {
            uint8_t r, g, b;

            ok = (rgb_led_set(colours[i][0], colours[i][1], colours[i][2]) == 0);
            rgb_led_get(&r, &g, &b);
            ok = ok && r == colours[i][0] && g == colours[i][1] && b == colours[i][2];
            vTaskDelay(pdMS_TO_TICKS(300));
        }
        (void)rgb_led_set(0, 0, 0);
        return ok;
    }

    /* Keys: the poll task is running and no key reads as held down. */
    static bool test_keys(void)
    {
        bool ok = (keys_init() == 0);

        for (int k = 0; k < KEY_COUNT && ok; k++) {
            ok = !keys_is_pressed((key_id_t)k);
        }
        return ok;
    }

    int my_app_selftest(void)
    {
        size_t free_heap = xPortGetFreeHeapSize();
        int failed = 0;

        failed += !check("led", test_led());
        failed += !check("keys", test_keys());
        failed += !check("heap", free_heap >= MIN_FREE_HEAP);
        printf("[selftest] %lu bytes of heap free\n", (unsigned long)free_heap);
        printf("%s\n", failed ? "SOME TESTS FAILED" : "ALL TESTS PASSED");
        return failed;
    }
    ```

    判定字符串 `ALL TESTS PASSED` 和 `SOME TESTS FAILED` 正是 `build_freertos.sh test` 等待的两个字符串。

4. **让 LED 只由应用任务驱动**：自检会操作 LED，而 LED 平时由 `my_app` 任务控制闪烁。为了避免两者同时写 LED，shell 命令只“请求”测试，由 `my_app` 任务执行。在 `my_app.h` 的 `#endif` 前加入：

    ```c title="apps/custom/my_reef_app/my_app.h（添加）"
    /* Self-test: one line per check, then ALL TESTS PASSED or SOME TESTS FAILED.
     * Returns the number of failed checks. Drives the LED: call it from the app
     * task only; other tasks use my_app_request_selftest(). */
    int      my_app_selftest(void);
    void     my_app_request_selftest(void);
    ```

    在 `main.c` 中做四处修改。在 `s_blink_ms` 下面加入任务句柄：

    ```c title="apps/custom/my_reef_app/main.c（添加）"
    static TaskHandle_t      s_app_task;
    ```

    在 `my_app_get_blink_ms()` 下面加入请求函数：

    ```c title="apps/custom/my_reef_app/main.c（添加）"
    void my_app_request_selftest(void)
    {
        if (s_app_task != NULL) {
            xTaskNotifyGive(s_app_task);
        }
    }
    ```

    把 `app_task()` 中 `blinking the RGB LED` 那一行之后到循环结束的部分改成下面这样：启动时执行一次自检（由 `.config` 选项控制），循环中的等待改用任务通知，收到请求就提前唤醒并执行测试：

    ```c title="apps/custom/my_reef_app/main.c（app_task 的后半部分）"
        IPRO_LOGI(LOG_TAG, "blinking the RGB LED on GPIO%d", BOARD_RGB_LED_PIN);
    #ifdef CONFIG_MYAPP_SELFTEST_AT_BOOT
        (void)my_app_selftest();
    #endif

        for (;;) {
            uint32_t period = s_blink_ms;

            on = (period == 0) ? true : !on;
            led_show(on ? s_rgb : 0);
            /* Wait one blink step; wake early when `myapp selftest` asks. */
            if (ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(period ? period : 100)) != 0) {
                (void)my_app_selftest();
            }
        }
    ```

    最后在 `main()` 中把任务句柄保存起来：

    ```c title="apps/custom/my_reef_app/main.c（在 main 中修改）"
        xTaskCreate(app_task, "my_app", 1024, NULL, 5, &s_app_task);
    ```

5. **加入 `myapp selftest` 命令和启动选项**：在 `app_cli.c` 的 `cmd_myapp()` 中，把最后的 `else` 分支替换为：

    ```c title="apps/custom/my_reef_app/app_cli.c（修改）"
        } else if (strcmp(argv[1], "selftest") == 0) {
            my_app_request_selftest();
        } else {
            printf("myapp [status] | myapp color <r> <g> <b> | myapp blink <ms> | myapp selftest\n");
        }
    ```

    在 `CMakeLists.txt` 的 `target_sources` 中加入 `selftest.c`：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt（节选）"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
        app_cli.c
        selftest.c
    )
    ```

    在 `.config` 末尾加入自己的选项。`.config` 中每个 `CONFIG_X=y` 都会成为全局的 `-DCONFIG_X=1`，所以代码可以用 `#ifdef` 判断：

    ```ini title="apps/custom/my_reef_app/.config（添加）"
    # my_reef_app: run the self-test once at boot
    CONFIG_MYAPP_SELFTEST_AT_BOOT=y
    ```

    修改 `.config` 之后做一次干净构建：

    ```bash
    ./build_freertos.sh clean build my_reef_app
    ```

    ```text
    ✓ Build succeeded (10s)
      Binary: <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin (96 KB)
    ```

6. **烧录并手动执行一次**：按照[创建第一个自己的应用](first-own-app.md)的步骤 6 烧录，按 SW2 复位。启动时 LED 依次亮红、绿、蓝，控制台打印：

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: blinking the RGB LED on GPIO24
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <剩余字节数> bytes of heap free
    ALL TESTS PASSED
    ```

    之后随时可以在控制台输入 `myapp selftest` 再运行一次。启动时按住 SW3，`keys` 一项会是 `FAIL`，最后一行变成 `SOME TESTS FAILED`，可以用这个方法确认失败路径也正确。

7. **用 `serial_monitor.py` 自动判定**：关闭终端程序（同一个串口不能同时被两个程序打开），在 SDK 根目录执行：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX \
        --send "myapp selftest" \
        --wait-for "ALL TESTS PASSED|SOME TESTS FAILED" --timeout 15
    echo "exit=$?"
    ```

    输出如下（省略 shell 的命令回显和提示符）：

    ```text
    [serial_monitor] Sent: myapp selftest
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <剩余字节数> bytes of heap free
    ALL TESTS PASSED

    [serial_monitor] MATCHED: ALL TESTS PASSED
    exit=0
    ```

    `serial_monitor.py` 以 115200 baud 打开串口（可用 `--baud` 修改），发送 `--send` 指定的命令，再等待与 `--wait-for` 正则表达式匹配的输出。退出码：

    | 退出码 | 含义 |
    |---|---|
    | 0 | 匹配到的文字包含 `PASSED` |
    | 1 | 匹配到的文字不包含 `PASSED`（例如 `SOME TESTS FAILED`） |
    | 2 | `--timeout` 秒内没有匹配（未指定 `--wait-for` 时，一律在超时后以 2 退出） |
    | 3 | 无法打开串口或发送命令 |

    等待不含 `PASSED` 的字符串时，退出码 1 表示“找到了”。例如确认复位后应用已经启动：`--send reboot --wait-for "Hello from my_reef_app"` 成功时退出码是 1，超时才是 2。

8. **写成脚本或放进 CI**：把上一步封装成脚本，根据退出码判断成败，并用 `--log` 保存完整输出：

    ```bash title="board_selftest.sh"
    #!/bin/sh
    # Run the on-board self-test of my_reef_app and fail unless it passes.
    PORT=${IPRO_SERIAL_PORT:?set IPRO_SERIAL_PORT to the Reef console port}
    python3 tools/serial_monitor.py "$PORT" --send "myapp selftest" \
        --wait-for "ALL TESTS PASSED|SOME TESTS FAILED" --timeout 15 --log selftest.log
    rc=$?
    case $rc in
        0) echo "self-test passed" ;;
        1) echo "self-test failed, see selftest.log" ;;
        2) echo "no verdict within 15 s, see selftest.log" ;;
        *) echo "cannot open $PORT" ;;
    esac
    exit $rc
    ```

    ```bash
    IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX sh board_selftest.sh
    ```

    在 CI 上运行时，开发板要连接在执行该任务的那台机器上。

9. **一行命令完成构建、烧录和测试**：`build_freertos.sh test` 依次构建、烧录（先发送 `reboot_dl` 让开发板进入下载模式）、发送 `reboot`，再等待 `ALL TESTS PASSED|SOME TESTS FAILED`。启动自检（步骤 5 中的 `CONFIG_MYAPP_SELFTEST_AT_BOOT=y`）就是让应用在复位后自己打印判定结果。烧录工具用 `IPRO_FLASH_TOOL` 指定，分区表用 `-P` 指定，`--chip-variant IPRO7AI` 由脚本根据 `.config` 中的 `CONFIG_IPRO7AI_REEF=y` 自动带入：

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ./build_freertos.sh -p /dev/cu.usbserial-XXXX \
            -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
            test my_reef_app
        echo "exit=$?"
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ./build_freertos.sh -p /dev/ttyUSB0 \
            -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
            test my_reef_app
        echo "exit=$?"
        ```

    成功时最后打印：

    ```text
    ✓ All tests passed
    ```

    退出码 0 表示通过、1 表示有测试失败、2 表示 `-t` 秒内（默认 30）没有看到判定结果。烧录完成后如果控制台没有任何输出，按一下 SW2（RESET）让开发板退出下载模式，测试会一直等到超时为止。Windows 上没有 `build_freertos.sh test`，请用手动烧录加上步骤 6 的方式测试。

10. **在电脑上运行主机端单元测试**：不涉及硬件的纯逻辑代码（信号处理、协议解析、数据转换）最好在电脑上测试。SDK 附带几组这类测试，每组是一个 `test_host/run.sh`，用电脑上的 `cc` 编译并运行。音频组件的测试覆盖 Reef 麦克风使用的 PDM 处理链：

    ```bash
    sh components/audio/test_host/run.sh
    ```

    ```text
    audio_asrc: 826 passed, 0 failed
    audio_pdm_mic: 37 passed, 0 failed
    ```

    LE Audio 耳机应用的 DAC 噪声整形器：

    ```bash
    sh apps/bluetooth/le_audio/ipro_le_audio_headset/test_host/run.sh
    ```

    ```text
    in-band error rms: 32 kHz rounding 0.1916 codes, order 1 0.00521 (31.3 dB better), order 2 0.000653 (49.4 dB better)
    dac_ns: all tests passed
    ```

    两个脚本在任何一项失败时都以非 0 退出，可以直接放进 CI。要为自己的模块编写主机端测试，参照 `components/audio/test_host/` 的做法：一个包含 `main()` 的 `test_*.c`，与被测的 `.c` 一起用 `cc` 编译（`run.sh` 加了 `-fsanitize=address,undefined` 以捕获内存错误）。

</div>

## 验证结果 { #verify }

- 复位后控制台最后打印 `ALL TESTS PASSED`，LED 先亮红、绿、蓝，再开始闪烁。
- `python3 tools/serial_monitor.py <串口> --send "myapp selftest" --wait-for "ALL TESTS PASSED|SOME TESTS FAILED"` 的退出码为 0；启动时按住 SW3 再执行一次，退出码为 1。
- `./build_freertos.sh … test my_reef_app` 打印 `✓ All tests passed` 并以 0 退出。
- `sh components/audio/test_host/run.sh` 打印两行 `0 failed`。

## 测试方式比较 { #methods }

| 方式 | 需要 | 判定 | 适用场景 |
|---|---|---|---|
| 控制台手动命令 | 开发板、终端程序 | 人工 | 开发过程中随手确认 |
| `reef selftest`（出厂固件） | 开发板、出厂固件 | 人工（看、听） | 确认开发板硬件正常 |
| `myapp selftest`＋`serial_monitor.py` | 开发板、macOS／Linux | 退出码 0／1／2／3 | 脚本、CI，无需重新烧录 |
| `build_freertos.sh test` | 开发板、IntelProCube、macOS／Linux | 退出码 0／1／2 | 每次修改后完整验证 |
| `test_host/run.sh` | 电脑上的 `cc` | 退出码 | 纯逻辑，最快 |

SDK 的 `ipro_unit_test` 也用 `build_freertos.sh test` 运行，但它的配置是 IPRO7 EVB，不是 Reef。

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| `serial_monitor.py` 退出码 3，信息为 `Failed to open …` | 串口被终端程序占用，或端口名错误 | 关闭终端程序；macOS 使用 `/dev/cu.*`，不要使用 `/dev/tty.*` |
| 退出码 2，输出只有 `Sent: myapp selftest` | 应用没有在运行，或不是这一版固件 | 打开终端程序确认 `myapp selftest` 有响应；重新烧录 |
| `myapp selftest` 只打印用法说明 | 旧版 `app_cli.c` | 确认已加入步骤 5 的 `selftest` 分支并重新构建 |
| 启动时没有自检输出 | 改了 `.config` 但没有干净构建，或选项名称拼写错误 | `./build_freertos.sh clean build my_reef_app`，确认 `CONFIG_MYAPP_SELFTEST_AT_BOOT=y` |
| `build_freertos.sh test` 出现 `Flash tool not found` | 没有设置 `IPRO_FLASH_TOOL`，PATH 中也没有烧录工具 | 设置 `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`（或 `_linux`） |
| `Several serial ports, pass -p PORT …` | 连接了不止一个 USB 串口（例如探针的两个端口） | 用 `-p` 或 `IPRO_SERIAL_PORT` 指定控制台的端口；使用探针时是名称以 `02` 结尾的端口 |
| `Test timed out (no result pattern seen)` | 烧录后开发板停在下载模式，或判定字符串没有打印出来 | 按 SW2；用 `-t 60` 延长等待时间；确认已开启启动自检选项 |
| `keys: FAIL` | 测试时有按键被按住 | 松开按键再测；如果持续失败，用 `myapp status` 查看哪个按键显示 `down` |

## 下一步 { #next-steps }

- [构建与烧录流程](build-and-flash.md)：`build_freertos.sh` 的其他动作与选项。
- [烧录与串口](../get-started/flash-and-monitor.md)：进入下载模式的各种方式以及 `serial_monitor.py` 的完整选项。
- [第一个 BLE 应用](first-ble-app.md)：在 Reef 上运行并修改 GATT 参考应用。
