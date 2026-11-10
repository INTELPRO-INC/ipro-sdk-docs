---
title: "最初の独自アプリケーションを作る"
description: 空のディレクトリから IPRO7AI Reef EVK 用の独自 FreeRTOS アプリケーションを書き、RGB LED の点滅、キーの読み取り、シェルコマンドの追加、SDK のログ API による出力を行います。
---

# 最初の独自アプリケーションを作る

このチュートリアルでは、空のディレクトリから始めて IPRO7AI Reef EVK 上で `my_reef_app` を作ります。このアプリケーションは起動時にあいさつを出力し、RGB LED を点滅させ、SW3、SW4、SW5 を押すと色を変え、独自のシェルコマンド `myapp` を追加します。各手順では、入力するコマンドやコードと、ボードがどう動作するかを示します。続く[アプリケーションのテスト](testing.md)では、同じアプリケーションを使って自動テストを説明します。

## 前提条件 { #prerequisites }

- SW7 を CAM、SW8 を PWR にし、USB-C から給電した IPRO7AI Reef EVK。U6 に IPRO Debug Probe または 3.3 V USB-UART ケーブルを接続します（配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照）。
- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了していること。ツールチェーンが動作し、`make -C apps/platform/ipro7ai_reef_demo` でビルドでき、ボードへの書き込みを一度行っています。
- IntelProCube 0.7.0.1 のコマンドライン書き込みツール（`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、または `ipro_iot_tool.exe`）。インストール方法は[開発環境の準備](../get-started/environment.md#intelprocube)を参照してください。すべてのアプリケーションに共通する書き込みとコンソールの手順は[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)にあります。
- 文字を入力できるシリアルターミナル（115200 ボー、8N1 に設定）。

すべてのコマンドは SDK のルート（以下 `<SDK>` と表記）から実行します。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **アプリケーションディレクトリを作成し、Makefile をコピーします。** アプリケーションは `apps/` の 2 階層下（`apps/<カテゴリ>/<アプリ>`）に置く必要があります。Makefile が `../../../` で SDK のルートを見つけるためです。カテゴリ名は自由に決められます。このチュートリアルでは `custom` を使います。

    ```bash
    mkdir -p apps/custom/my_reef_app
    cp apps/platform/ipro7ai_reef_demo/Makefile apps/custom/my_reef_app/
    ```

    Makefile は SDK ルートの `project.build` にビルドを渡すだけなので、変更せずにそのまま使います。

2. **`.config` を作成します。** 出荷時ファームウェアの `apps/platform/ipro7ai_reef_demo/.config` を、チップ、Reef ボード、PSRAM、コンソール、FreeRTOS、シェル、ログだけに絞ったものです。オーディオ、USB、カメラ、SD カードは含みません。

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

    最初のコメント行は、`./build_freertos.sh -l` でアプリケーションの説明として表示されます。ビルドは `.config` を書かれたとおりに読み、Kconfig の `select` やデフォルト値を適用しないため、PSRAM などのオプションは明示する必要があります。

3. **`CMakeLists.txt` を作成します。**

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt"
    # my_reef_app: first application on the IPRO7AI Reef EVK.

    __component_add_include_dirs(.)

    __set_main_file(main.c)
    setup_project(my_reef_app)
    ```

    `setup_project()` に渡す名前で出力ファイル名（`my_reef_app_IPRO7.bin`）が決まります。

4. **`main.c` を作成します。** `ipro_platform_init()` は 1 回の呼び出しでヒープ、boot2、ログ、シェルを初期化します。デフォルトの FreeRTOS フック、ヒープ、assert 処理は SDK がすでに提供しているため、`main.c` で改めて書く必要はありません。

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

    `IPRO_LOGI()`、`IPRO_LOGW()`、`IPRO_LOGE()` は SDK のログ API（`ipro_log.h`）です。ファイルごとに独自の `LOG_TAG` を付けます。`xTaskCreate()` に渡すスタックサイズの単位はワードで、1024 は 4 KB です。

5. **ビルドします。**

    ```bash
    make -C apps/custom/my_reef_app
    ```

    ビルドに成功すると、最後にメモリ使用量と出力ファイルが表示されます（数値はリリースによって多少変わります）。

    ```text
    Memory region         Used Size  Region Size  %age Used
               flash:       92080 B         1 MB      8.78%
               psram:        9368 B         8 MB      0.11%
               ocram:       29840 B       256 KB     11.38%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin
    ```

    `./build_freertos.sh build my_reef_app` でもビルドできます。スクリプトが名前から `apps/custom/my_reef_app` を見つけます。

6. **ダウンロードモードに入り、書き込みます。** SW1（BOOT）を押したまま SW2（RESET）を短く押し、SW1 を離します。次に、IntelProCube のディレクトリから以下を実行します（パーティションテーブルは出荷時ファームウェアと同じものです）。

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

    このツールは失敗しても終了コード 0 で終了します。出力に `[All Success]` が含まれていることを確認してください。IPRO Debug Probe を使う場合、ポートは名前が `02` で終わるものです。

7. **コンソールを開いてリセットします。** 同じポートを 115200 ボーで開き、SW2 を短く押します。各ログ行の先頭にはレベル、タイムスタンプ、スレッド番号が付きますが、ここでは省略しています。

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: alive 0
    MYAPP: alive 1
    MYAPP: alive 2
    ```

    `help` と入力すると、SDK に組み込まれたシェルコマンド（`ps`、`free`、`reboot`、`reboot_dl` など）が一覧表示されます。以降は `reboot_dl` と入力すれば、キーを押さずにボードを次の書き込み用のダウンロードモードにできます。

8. **RGB LED を点滅させます。** Reef の WS2812 RGB LED は GPIO24 に接続されており、そのドライバー `rgb_led.c` は出荷時ファームウェアに含まれています。コピーせず、`ipro_ble_remote` の Reef ビルドと同じように元の場所のまま使います。`CMakeLists.txt` を次のように変更します。

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

    `main.c` を次のものに置き換えます。色は 1 つの 32 ビット変数に `0xRRGGBB` として保持し、点滅周期 0 は常時点灯を意味します。

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

    再ビルド（手順 5）し、`reboot_dl` と入力して書き込み（手順 6）、SW2 を短く押します。コンソールに `MYAPP: blinking the RGB LED on GPIO24` と表示され、LED が暗い緑で 0.5 秒点灯、0.5 秒消灯を繰り返します。`CONFIG_IPRO7AI_REEF` によって `board_config.h` が Reef のピン定義を選択します。`BOARD_RGB_LED_PIN` などのマクロはそこで定義されています。

9. **キーを読み取ります。** Reef には読み取り可能なキーが 4 つあります。SW1（BOOT、GPIO41、アクティブ High）と、アクティブ Low の SW3（GPIO10）、SW4（GPIO27）、SW5（GPIO11）です。SW2 はハードウェアリセットで、読み取れません。出荷時ファームウェアの `keys.c` は、これらを 10 ms ごとにデバウンス付きでポーリングします。`CMakeLists.txt` の `target_sources` に 1 行追加します。

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt（抜粋）"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
    )
    ```

    `main.c` で `#include "rgb_led.h"` の下に `#include "keys.h"` を追加し、`led_show()` の後にキーのコールバックを追加します。

    ```c title="apps/custom/my_reef_app/main.c（追加）"
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

    次に、`app_task()` 内の `rgb_led_init()` ブロックの後で、キーのポーリングを開始します。

    ```c title="apps/custom/my_reef_app/main.c（app_task に追加）"
        if (keys_init() == 0) {
            keys_set_callback(on_key, NULL);
        } else {
            IPRO_LOGE(LOG_TAG, "keys init failed");
        }
    ```

    コールバックはキーのポーリングタスクで実行されます。処理は短くし（変数の設定、ログ 1 行など）、コールバック内では決して待機しないでください。再ビルド、書き込み、リセットを行ってから SW3 を押すと、LED が赤で点滅し、コンソールに次のように表示されます。

    ```text
    MYAPP: SW3 pressed (1 presses)
    ```

    SW4 と SW5 では緑と青に切り替わります。SW1 を押したまま SW2 を押さないでください。ボードがダウンロードモードに入ります。

10. **独自のシェルコマンドを追加します。** シェルコマンドが関数を通じてアプリケーションの状態を読み書きできるように、ヘッダーを作成します。

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

    `main.c` に `#include "my_app.h"` を追加し、次の 4 つの関数を `led_show()` の前に置きます。

    ```c title="apps/custom/my_reef_app/main.c（追加）"
    void my_app_set_color(uint32_t rgb)   { s_rgb = rgb & 0xFFFFFFu; }
    uint32_t my_app_get_color(void)       { return s_rgb; }
    void my_app_set_blink_ms(uint32_t ms) { s_blink_ms = ms; }
    uint32_t my_app_get_blink_ms(void)    { return s_blink_ms; }
    ```

    `app_cli.c` を作成します。コマンドは `SHELL_CMD_EXPORT_ALIAS(関数, コマンド名, 説明)` で登録します。ファイル全体を `#ifdef CONFIG_SHELL` で囲み、シェルを含まないビルド（低消費電力構成など）がシェル API を参照しないようにします。

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

    最後に、`CMakeLists.txt` を完全版に置き換えます。シェルはリンカーセクションを通じてコマンドを見つけ、コマンドを名前で呼び出すコードはないため、アプリケーションライブラリ全体をリンクする必要があります。そうしないと、リンカーがコマンドを取り除いてしまいます。

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

11. **ビルドと書き込みを行い、コマンドを試します。** 再ビルドし、`reboot_dl` と入力して書き込み、SW2 を短く押します。コンソールで次のように入力します。

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

    色を変えて、点滅を止めます。

    ```text
    myapp color 0 0 80
    myapp blink 0
    ```

    ```text
    LED (0,0,80)
    blink 0 ms
    ```

    LED が青の常時点灯になります。`help` に `myapp            - my_reef_app LED and keys` が表示されるようになります。

</div>

## 動作確認 { #verify }

- 起動ログに `MYAPP: Hello from my_reef_app` と `MYAPP: blinking the RGB LED on GPIO24` が表示され、LED が 0.5 秒ごとに点滅します。
- SW3、SW4、SW5 で LED が赤、緑、青に切り替わり、コンソールに `<キー> pressed (<回数> presses)` が表示されます。
- `myapp status` で色、点滅周期、4 つのキーすべての押下回数が表示され、`myapp color` と `myapp blink` で LED がすぐに変わります。

アプリケーションディレクトリの内容は次のとおりです。

```text
apps/custom/my_reef_app/
├── .config
├── CMakeLists.txt
├── Makefile
├── app_cli.c
├── main.c
└── my_app.h
```

## 仕組み { #how-it-works }

- **起動**：`main()` は `ipro_platform_init()`（プラットフォーム、ヒープ、boot2、ログ、シェル）を呼び出し、`my_app` タスクを作成してスケジューラーを開始します。`vApplicationIdleHook` などの FreeRTOS フックを置き換えるには、自分のソースで weak でない版を定義します。リンカーがそちらを選択します。
- **ビルド**：ビルドは `.config` を読み、各 `CONFIG_X=y` はグローバルな `-DCONFIG_X=1` と CMake 変数 `CONFIG_X` になります。`board_config.h` はボードオプションに応じてピンのマクロを選択します。`main.c` は単独で実行ファイルにコンパイルされ、その他のソースは `app` ライブラリに入ります。
- **ボードドライバー**：`rgb_led.c`（GPIO24 から SPI0 経由で WS2812 の波形を出力）と `keys.c`（10 ms ポーリング、30 ms デバウンス）は `apps/platform/ipro7ai_reef_demo/src/` にあり、CMake から参照されます。`rgb_led_set()` は 1 色分を SPI のバイト列にエンコードし、約 30 µs の波形をクリティカルセクション内で送信します。
- **役割分担**：キーのコールバックはポーリングタスクで、シェルコマンドはシェルタスクで実行され、どちらも `s_rgb` と `s_blink_ms` を変更するだけです。LED ドライバーを呼び出すのは `my_app` タスクだけなので、追加のロックは不要です。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| `make` が `project.build` を見つけられない | アプリケーションが `apps/` の 2 階層下にないため、`../../../` が SDK のルートを指していない | `apps/<カテゴリ>/<アプリ>` に置くか、`make IPRO_SDK_BASE=<SDK>` を実行します |
| コンパイルエラー `rgb_led.h: No such file or directory` | 出荷時ファームウェアのドライバーのインクルードパスがない | `CMakeLists.txt` に `__component_add_include_dirs(${REEF_DEMO_SRC})` があることを確認します |
| `myapp: command not found.` | アプリケーションライブラリ全体がリンクされていない、または `.config` に `CONFIG_SHELL=y` がない | `CMakeLists.txt` の `SDK_WHOLE_ARCHIVE_LIBS` の行と `app_cli.c` を確認します |
| 書き込みは成功するが、コンソールに何も表示されない | ボードがまだダウンロードモードにある、またはボーレートかケーブルが正しくない | SW2 を短く押します。115200 を使います。U6 のケーブルは両端でピンの並びが逆になっている必要があります（[IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照） |
| ログ行は表示されるが、LED が点灯しない | WS2812 は USB VBUS で動作する | 3.3 V だけで給電せず、USB-C から給電します |
| 書き込みツールの出力に `[All Success]` がない | ボードがダウンロードモードになっていない、または `--chip-variant` が正しくない | 先に `reboot_dl` と入力するか、SW1 + SW2 を使います。Reef では常に `--chip-variant IPRO7AI` を指定します |

## 次のステップ { #next-steps }

- [アプリケーションのテスト](testing.md)：`my_reef_app` にセルフテストを追加し、スクリプトと `build_freertos.sh test` から実行します。
- [ビルドと書き込みの流れ](build-and-flash.md)：`build_freertos.sh` でビルド、書き込み、モニターを連結します。
- [最初の BLE アプリケーション](first-ble-app.md)：Reef 上で GATT リファレンスアプリケーションを実行し、変更します。
- [BLE 開発](../guides/ble.md)：独自アプリケーションに BLE が必要になったときの出発点です。コントローラーライブラリから `.config` のキーまでを扱います。
