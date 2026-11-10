---
title: "建立第一個自己的應用"
description: 從空目錄開始，在 IPRO7AI Reef EVK 上寫出自己的 FreeRTOS 應用：讓 RGB LED 閃爍、讀取按鍵、加入 shell 指令並以 SDK 的日誌 API 輸出訊息。
---

# 建立第一個自己的應用

本教學從一個空目錄開始，在 IPRO7AI Reef EVK 上建立應用 `my_reef_app`：開機印出訊息、讓 RGB LED 閃爍、按 SW3／SW4／SW5 換顏色，並加入自己的 shell 指令 `myapp`。每一步都有要輸入的命令或程式碼，以及板子上應該看到的結果。完成後，[測試你的應用](testing.md)會用同一個應用示範自動化測試。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK，SW7 在 CAM、SW8 在 PWR，以 USB-C 供電；U6 接 IPRO Debug Probe 或 3.3 V USB 轉 UART 線（接法見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)：工具鏈可用，`make -C apps/platform/ipro7ai_reef_demo` 能建置成功，也燒錄過一次。
- IntelProCube 0.7.0.1 命令列燒錄工具（`ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`），安裝方式見[準備開發環境](../get-started/environment.md#intelprocube)。燒錄與主控台的共通步驟見[燒錄與序列埠](../get-started/flash-and-monitor.md)。
- 一個可輸入指令的序列埠終端程式，設為 115200 baud、8N1。

所有命令都在 SDK 根目錄（下文以 `<SDK>` 表示）執行。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **建立應用目錄並複製 Makefile**：應用必須放在 `apps/` 底下兩層（`apps/<類別>/<應用>`），因為 Makefile 以 `../../../` 找到 SDK 根目錄。類別名稱可自訂，本教學用 `custom`。

    ```bash
    mkdir -p apps/custom/my_reef_app
    cp apps/platform/ipro7ai_reef_demo/Makefile apps/custom/my_reef_app/
    ```

    Makefile 只把建置交給 SDK 根目錄的 `project.build`，不需要修改。

2. **建立 `.config`**：內容取自開箱韌體 `apps/platform/ipro7ai_reef_demo/.config`，只留下晶片、Reef 板級、PSRAM、主控台、FreeRTOS、shell 與日誌，拿掉音訊、USB、相機與 SD 卡。

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

    第一行註解會成為 `./build_freertos.sh -l` 列出的應用說明。建置系統照檔案內容讀取 `.config`，不套用 Kconfig 的 `select` 與預設值，所以 PSRAM 等選項要明寫。

3. **建立 `CMakeLists.txt`**：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt"
    # my_reef_app: first application on the IPRO7AI Reef EVK.

    __component_add_include_dirs(.)

    __set_main_file(main.c)
    setup_project(my_reef_app)
    ```

    `setup_project()` 的名稱決定輸出檔名：`my_reef_app_IPRO7.bin`。

4. **建立 `main.c`**：`ipro_platform_init()` 一次完成記憶體堆積、boot2、日誌與 shell 的初始化；FreeRTOS 的 hook、heap 與 assert 已由 SDK 提供預設實作，`main.c` 不必再寫。

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

    `IPRO_LOGI()`、`IPRO_LOGW()`、`IPRO_LOGE()` 是 SDK 的日誌 API（`ipro_log.h`），每個檔案用自己的 `LOG_TAG`。`xTaskCreate()` 的堆疊大小以 word 計，1024 即 4 KB。

5. **建置**：

    ```bash
    make -C apps/custom/my_reef_app
    ```

    成功時最後印出記憶體用量與產出檔（數字依版本略有不同）：

    ```text
    Memory region         Used Size  Region Size  %age Used
               flash:       92080 B         1 MB      8.78%
               psram:        9368 B         8 MB      0.11%
               ocram:       29840 B       256 KB     11.38%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin
    ```

    也可以用 `./build_freertos.sh build my_reef_app`，它會自動找到 `apps/custom/my_reef_app`。

6. **進入下載模式並燒錄**：按住 SW1（BOOT），按一下 SW2（RESET），再放開 SW1。然後在 IntelProCube 目錄下執行（分割表與開箱韌體相同）：

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

    工具即使失敗也會以 0 結束，請確認輸出中有 `[All Success]`。使用 IPRO Debug Probe 時，連接埠是名稱以 `02` 結尾的那一個。

7. **開啟主控台並重置**：以 115200 baud 開啟同一個序列埠，按一下 SW2。每行日誌開頭有等級、時間戳記與執行緒編號，以下省略：

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: alive 0
    MYAPP: alive 1
    MYAPP: alive 2
    ```

    在主控台輸入 `help`，會列出 SDK 內建的 shell 指令，例如 `ps`、`free`、`reboot` 與 `reboot_dl`。之後要重新燒錄時，在主控台輸入 `reboot_dl` 就能進入下載模式，不必按按鍵。

8. **讓 RGB LED 閃爍**：Reef 的 WS2812 RGB LED 接在 GPIO24，驅動程式 `rgb_led.c` 隨開箱韌體提供。像 `ipro_ble_remote` 的 Reef 設定一樣，直接引用它，不要複製。把 `CMakeLists.txt` 改成：

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

    把 `main.c` 換成下面的內容。顏色以 `0xRRGGBB` 存在一個 32 位元變數裡，閃爍週期為 0 時恆亮：

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

    重新建置（步驟 5）、在主控台輸入 `reboot_dl` 後燒錄（步驟 6）、按 SW2 重置。主控台印出 `MYAPP: blinking the RGB LED on GPIO24`，LED 以暗綠色每 0.5 秒亮滅一次。`board_config.h` 依 `CONFIG_IPRO7AI_REEF` 選用 Reef 的腳位定義，`BOARD_RGB_LED_PIN` 等巨集都來自那裡。

9. **讀取按鍵**：Reef 可讀取的按鍵有 SW1（BOOT，GPIO41，高準位有效）、SW3（GPIO10）、SW4（GPIO27）與 SW5（GPIO11，後三者低準位有效）；SW2 是硬體重置，讀不到。開箱韌體的 `keys.c` 以 10 ms 輪詢並去彈跳。在 `CMakeLists.txt` 的 `target_sources` 加入一行：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt（節錄）"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
    )
    ```

    在 `main.c` 的 `#include "rgb_led.h"` 下面加入 `#include "keys.h"`，在 `led_show()` 之後加入按鍵回呼：

    ```c title="apps/custom/my_reef_app/main.c（加入）"
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

    再在 `app_task()` 的 `rgb_led_init()` 區塊後面啟動按鍵輪詢：

    ```c title="apps/custom/my_reef_app/main.c（app_task 內加入）"
        if (keys_init() == 0) {
            keys_set_callback(on_key, NULL);
        } else {
            IPRO_LOGE(LOG_TAG, "keys init failed");
        }
    ```

    回呼在按鍵輪詢任務中執行，只做設定變數與記錄這類短工作，不要在裡面等待。重新建置、燒錄並重置後，按 SW3，LED 改成紅色閃爍，主控台印出：

    ```text
    MYAPP: SW3 pressed (1 presses)
    ```

    SW4、SW5 分別換成綠色與藍色。不要在按住 SW1 時按 SW2，那會讓板子進入下載模式。

10. **加入自己的 shell 指令**：建立一個標頭檔，讓 shell 指令透過函式讀寫應用狀態：

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

    在 `main.c` 加入 `#include "my_app.h"`，並在 `led_show()` 前面加入這四個函式：

    ```c title="apps/custom/my_reef_app/main.c（加入）"
    void my_app_set_color(uint32_t rgb)   { s_rgb = rgb & 0xFFFFFFu; }
    uint32_t my_app_get_color(void)       { return s_rgb; }
    void my_app_set_blink_ms(uint32_t ms) { s_blink_ms = ms; }
    uint32_t my_app_get_blink_ms(void)    { return s_blink_ms; }
    ```

    建立 `app_cli.c`。指令以 `SHELL_CMD_EXPORT_ALIAS(函式, 指令名稱, 說明)` 註冊，整個檔案以 `#ifdef CONFIG_SHELL` 包起來，關掉 shell 的建置（例如低功耗設定）才不會參照 shell 的 API：

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

    最後把 `CMakeLists.txt` 改成完整版本。shell 指令是經由連結區段找到的，程式中沒有人直接呼叫它，所以應用的程式庫必須整個連結進來，否則指令會被連結器丟掉：

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

11. **建置、燒錄並試用指令**：重新建置、`reboot_dl`、燒錄、按 SW2。在主控台輸入：

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

    改顏色並讓 LED 恆亮：

    ```text
    myapp color 0 0 80
    myapp blink 0
    ```

    ```text
    LED (0,0,80)
    blink 0 ms
    ```

    LED 變成藍色恆亮。輸入 `help`，清單中出現 `myapp            - my_reef_app LED and keys`。

</div>

## 確認結果 { #verify }

- 開機訊息有 `MYAPP: Hello from my_reef_app` 與 `MYAPP: blinking the RGB LED on GPIO24`，LED 每 0.5 秒亮滅一次。
- 按 SW3、SW4、SW5 時 LED 換成紅、綠、藍色，主控台印出 `<按鍵> pressed (<次數> presses)`。
- `myapp status` 顯示目前顏色、閃爍週期與四個按鍵的按下次數；`myapp color` 與 `myapp blink` 立即改變 LED。

應用目錄最後有這些檔案：

```text
apps/custom/my_reef_app/
├── .config
├── CMakeLists.txt
├── Makefile
├── app_cli.c
├── main.c
└── my_app.h
```

## 程式如何運作 { #how-it-works }

- **啟動**：`main()` 呼叫 `ipro_platform_init()`（平台、記憶體堆積、boot2、日誌、shell），建立 `my_app` 任務後啟動排程器。要換掉某個 FreeRTOS hook（例如 `vApplicationIdleHook`），在自己的原始碼定義非 weak 版本即可，連結器會自動選用。
- **建置**：建置系統讀取 `.config`，每個 `CONFIG_X=y` 都成為全域的 `-DCONFIG_X=1`，同時是 CMake 變數 `CONFIG_X`；`board_config.h` 依板級設定選出腳位巨集。`main.c` 單獨編進執行檔，其他原始碼編進 `app` 程式庫。
- **板級驅動**：`rgb_led.c`（GPIO24 經 SPI0 產生 WS2812 波形）與 `keys.c`（10 ms 輪詢、30 ms 去彈跳）位於 `apps/platform/ipro7ai_reef_demo/src/`，在 CMake 中直接引用。`rgb_led_set()` 把一個顏色編碼成 SPI 位元組，在臨界區段內送出約 30 µs 的波形。
- **任務分工**：按鍵回呼在輪詢任務中執行，shell 指令在 shell 任務中執行，兩者都只改變 `s_rgb` 與 `s_blink_ms`；實際呼叫 LED 驅動的只有 `my_app` 任務，所以不需要額外的鎖。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `make` 找不到 `project.build` | 應用不在 `apps/` 底下兩層，Makefile 的 `../../../` 指不到 SDK 根目錄 | 放在 `apps/<類別>/<應用>`，或執行 `make IPRO_SDK_BASE=<SDK>` |
| 編譯錯誤 `rgb_led.h: No such file or directory` | 沒有加入開箱韌體驅動的標頭檔路徑 | 確認 `CMakeLists.txt` 有 `__component_add_include_dirs(${REEF_DEMO_SRC})` |
| 輸入 `myapp` 出現 `myapp: command not found.` | 應用程式庫沒有整個連結，或 `.config` 沒有 `CONFIG_SHELL=y` | 確認 `CMakeLists.txt` 有 `SDK_WHOLE_ARCHIVE_LIBS` 那一行與 `app_cli.c` |
| 燒錄成功但主控台沒有輸出 | 板子還在下載模式，或鮑率、排線方向不對 | 按 SW2；主控台設 115200；U6 排線兩端腳序必須對調（見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)） |
| 主控台有訊息但 LED 不亮 | WS2812 由 USB VBUS 供電 | 以 USB-C 供電，不要只從 3.3 V 供電 |
| 燒錄輸出沒有 `[All Success]` | 未進入下載模式，或 `--chip-variant` 不對 | 先 `reboot_dl` 或按 SW1＋SW2；Reef 一律用 `--chip-variant IPRO7AI` |

## 下一步 { #next-steps }

- [測試你的應用](testing.md)：為 `my_reef_app` 加上自我測試，用腳本與 `build_freertos.sh test` 自動執行。
- [建置與燒錄流程](build-and-flash.md)：用 `build_freertos.sh` 串接建置、燒錄與監看。
- [第一個 BLE 應用](first-ble-app.md)：在 Reef 上執行 GATT 參考應用並修改它。
- [BLE 開發](../guides/ble.md)：要讓自己的應用加入 BLE 時，從控制器函式庫與 `.config` 設定開始。
