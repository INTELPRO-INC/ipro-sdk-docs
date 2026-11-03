---
title: "Create Your First Application"
description: Start from an empty directory and write your own FreeRTOS application for the IPRO7AI Reef EVK that blinks the RGB LED, reads the keys, adds a shell command and logs through the SDK's logging API.
---

# Create Your First Application

This tutorial starts from an empty directory and builds `my_reef_app` on the IPRO7AI Reef EVK: it prints a greeting at boot, blinks the RGB LED, changes colour when you press SW3, SW4 or SW5, and adds a shell command of its own, `myapp`. Each step gives the command or code to enter and what the board should do. [Test Your Application](testing.md) then uses the same app to show automated testing.

## Prerequisites { #prerequisites }

- An IPRO7AI Reef EVK with SW7 on CAM and SW8 on PWR, powered from USB-C, with an IPRO Debug Probe or a 3.3 V USB-UART cable on U6 (wiring in [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)).
- [First FreeRTOS Application](../get-started/first-app-freertos.md) done: the toolchain works, `make -C apps/platform/ipro7ai_reef_demo` builds, and you have flashed the board once.
- The IntelProCube v0.6.3 command-line flasher (`ipro_iot_tool_macos`, `ipro_iot_tool_linux` or `ipro_iot_tool.exe`), obtained separately. The flashing and console steps common to every app are in [Flashing & Serial Console](../get-started/flash-and-monitor.md).
- A serial terminal you can type into, set to 115200 baud, 8N1.

Run every command from the SDK root, written `<SDK>` below.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Create the app directory and copy a Makefile.** An app must sit two levels below `apps/` (`apps/<category>/<app>`), because its Makefile finds the SDK root at `../../../`. The category name is yours to choose; this tutorial uses `custom`.

    ```bash
    mkdir -p apps/custom/my_reef_app
    cp apps/platform/ipro7ai_reef_demo/Makefile apps/custom/my_reef_app/
    ```

    The Makefile only hands the build to `project.build` in the SDK root; leave it as it is.

2. **Create `.config`.** It is the out-of-box firmware's `apps/platform/ipro7ai_reef_demo/.config` cut down to the chip, the Reef board, PSRAM, the console, FreeRTOS, the shell and logging; audio, USB, camera and SD card are gone.

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

    The first comment line becomes the app's description in `./build_freertos.sh -l`. The build reads `.config` as written and applies no Kconfig `select` or default, so options such as PSRAM must be stated.

3. **Create `CMakeLists.txt`:**

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt"
    # my_reef_app: first application on the IPRO7AI Reef EVK.

    __component_add_include_dirs(.)

    __set_main_file(main.c)
    setup_project(my_reef_app)
    ```

    The name given to `setup_project()` sets the output file name: `my_reef_app_IPRO7.bin`.

4. **Create `main.c`.** `ipro_platform_init()` sets up the heap, boot2, logging and the shell in one call. The SDK already provides default FreeRTOS hooks, heap and assert handling, so `main.c` does not repeat them.

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

    `IPRO_LOGI()`, `IPRO_LOGW()` and `IPRO_LOGE()` are the SDK's logging API (`ipro_log.h`); give each file its own `LOG_TAG`. The stack size passed to `xTaskCreate()` is in words: 1024 is 4 KB.

5. **Build:**

    ```bash
    make -C apps/custom/my_reef_app
    ```

    A successful build ends with the memory usage and the output file (the numbers change a little between releases):

    ```text
    Memory region         Used Size  Region Size  %age Used
               flash:       92080 B         1 MB      8.78%
               psram:        9368 B         8 MB      0.11%
               ocram:       29840 B       256 KB     11.38%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin
    ```

    `./build_freertos.sh build my_reef_app` works too; it finds `apps/custom/my_reef_app` by name.

6. **Enter download mode and flash.** Hold SW1 (BOOT), tap SW2 (RESET), release SW1. Then run from the IntelProCube directory (the partition table is the one the out-of-box firmware uses):

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

    The tool exits with 0 even when it fails; check that the output contains `[All Success]`. With an IPRO Debug Probe, the port is the one whose name ends in `02`.

7. **Open the console and reset.** Open the same port at 115200 baud and tap SW2. Each log line starts with the level, a timestamp and a thread number, left out here:

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: alive 0
    MYAPP: alive 1
    MYAPP: alive 2
    ```

    Type `help` to list the shell commands the SDK builds in, such as `ps`, `free`, `reboot` and `reboot_dl`. From now on, typing `reboot_dl` puts the board in download mode for the next flash, with no keys to press.

8. **Blink the RGB LED.** The Reef's WS2812 RGB LED is on GPIO24, and its driver `rgb_led.c` ships with the out-of-box firmware. Use it in place, as the Reef build of `ipro_ble_remote` does, rather than copying it. Change `CMakeLists.txt` to:

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

    Replace `main.c` with the version below. The colour lives in one 32-bit variable as `0xRRGGBB`; a blink period of 0 means steady on.

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

    Rebuild (step 5), type `reboot_dl`, flash (step 6) and tap SW2. The console prints `MYAPP: blinking the RGB LED on GPIO24` and the LED blinks dim green, 0.5 s on and 0.5 s off. `board_config.h` picks the Reef pin definitions because of `CONFIG_IPRO7AI_REEF`; macros such as `BOARD_RGB_LED_PIN` come from there.

9. **Read the keys.** The Reef has four readable keys: SW1 (BOOT, GPIO41, active high) and SW3 (GPIO10), SW4 (GPIO27) and SW5 (GPIO11), which are active low. SW2 is the hardware reset and cannot be read. The out-of-box firmware's `keys.c` polls them every 10 ms with debounce. Add one line to `target_sources` in `CMakeLists.txt`:

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt (excerpt)"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
    )
    ```

    In `main.c`, add `#include "keys.h"` below `#include "rgb_led.h"`, and add a key callback after `led_show()`:

    ```c title="apps/custom/my_reef_app/main.c (add)"
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

    Then start the key poller in `app_task()`, after the `rgb_led_init()` block:

    ```c title="apps/custom/my_reef_app/main.c (add in app_task)"
        if (keys_init() == 0) {
            keys_set_callback(on_key, NULL);
        } else {
            IPRO_LOGE(LOG_TAG, "keys init failed");
        }
    ```

    The callback runs in the key poll task: keep it short (set a variable, log a line) and never wait in it. Rebuild, flash and reset, then press SW3. The LED blinks red and the console prints:

    ```text
    MYAPP: SW3 pressed (1 presses)
    ```

    SW4 and SW5 switch to green and blue. Do not tap SW2 while holding SW1: that puts the board in download mode.

10. **Add your own shell command.** Create a header so the shell command reads and changes the app's state through functions:

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

    In `main.c`, add `#include "my_app.h"` and put these four functions before `led_show()`:

    ```c title="apps/custom/my_reef_app/main.c (add)"
    void my_app_set_color(uint32_t rgb)   { s_rgb = rgb & 0xFFFFFFu; }
    uint32_t my_app_get_color(void)       { return s_rgb; }
    void my_app_set_blink_ms(uint32_t ms) { s_blink_ms = ms; }
    uint32_t my_app_get_blink_ms(void)    { return s_blink_ms; }
    ```

    Create `app_cli.c`. A command is registered with `SHELL_CMD_EXPORT_ALIAS(function, command name, description)`, and the whole file sits inside `#ifdef CONFIG_SHELL` so that builds without the shell (low-power configurations, for example) never reference the shell API:

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

    Finally, replace `CMakeLists.txt` with the complete version. The shell finds commands through a linker section and nothing calls them by name, so the app library must be linked whole; otherwise the linker drops the command:

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

11. **Build, flash and try the command.** Rebuild, type `reboot_dl`, flash and tap SW2. At the console, type:

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

    Change the colour and stop the blinking:

    ```text
    myapp color 0 0 80
    myapp blink 0
    ```

    ```text
    LED (0,0,80)
    blink 0 ms
    ```

    The LED turns steady blue. `help` now lists `myapp            - my_reef_app LED and keys`.

</div>

## Verify { #verify }

- The boot log shows `MYAPP: Hello from my_reef_app` and `MYAPP: blinking the RGB LED on GPIO24`, and the LED blinks every 0.5 s.
- SW3, SW4 and SW5 switch the LED to red, green and blue, and the console prints `<key> pressed (<count> presses)`.
- `myapp status` shows the colour, the blink period and the press count of all four keys; `myapp color` and `myapp blink` change the LED at once.

The app directory now holds:

```text
apps/custom/my_reef_app/
├── .config
├── CMakeLists.txt
├── Makefile
├── app_cli.c
├── main.c
└── my_app.h
```

## How it works { #how-it-works }

- **Start-up:** `main()` calls `ipro_platform_init()` (platform, heap, boot2, logging, shell), creates the `my_app` task and starts the scheduler. To replace a FreeRTOS hook such as `vApplicationIdleHook`, define a non-weak version in your own source; the linker picks it.
- **Build:** the build reads `.config`; each `CONFIG_X=y` becomes a global `-DCONFIG_X=1` and the CMake variable `CONFIG_X`. `board_config.h` selects the pin macros from the board option. `main.c` is compiled into the executable on its own; the other sources go into the `app` library.
- **Board drivers:** `rgb_led.c` (WS2812 waveform from GPIO24 through SPI0) and `keys.c` (10 ms poll, 30 ms debounce) live in `apps/platform/ipro7ai_reef_demo/src/` and are referenced from CMake. `rgb_led_set()` encodes one colour into SPI bytes and sends the roughly 30 µs waveform inside a critical section.
- **Who does what:** the key callback runs in the poll task and the shell command in the shell task; both only change `s_rgb` and `s_blink_ms`. Only the `my_app` task calls the LED driver, so no extra lock is needed.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `make` cannot find `project.build` | The app is not two levels below `apps/`, so `../../../` misses the SDK root | Put it at `apps/<category>/<app>`, or run `make IPRO_SDK_BASE=<SDK>` |
| Compile error `rgb_led.h: No such file or directory` | The include path of the out-of-box drivers is missing | Check that `CMakeLists.txt` has `__component_add_include_dirs(${REEF_DEMO_SRC})` |
| `myapp: command not found.` | The app library is not linked whole, or `.config` lacks `CONFIG_SHELL=y` | Check the `SDK_WHOLE_ARCHIVE_LIBS` line and `app_cli.c` in `CMakeLists.txt` |
| Flashing succeeds but the console stays silent | The board is still in download mode, or the baud rate or cable is wrong | Tap SW2; use 115200; the U6 cable must be pin-reversed (see [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)) |
| Log lines appear but the LED stays dark | The WS2812 runs from USB VBUS | Power the board from USB-C, not from 3.3 V alone |
| No `[All Success]` in the flasher output | The board is not in download mode, or `--chip-variant` is wrong | Type `reboot_dl` or use SW1 + SW2 first; always pass `--chip-variant IPRO7AI` for the Reef |

## Next steps { #next-steps }

- [Test Your Application](testing.md): add a self-test to `my_reef_app` and run it from a script and from `build_freertos.sh test`.
- [Build and Flash Workflow](build-and-flash.md): chain build, flash and monitor with `build_freertos.sh`.
- [Your First BLE Application](first-ble-app.md): run the GATT reference app on the Reef and change it.
- [BLE Development](../guides/ble.md): where to start when your own app needs BLE, from the controller library to the `.config` keys.
