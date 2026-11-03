---
title: "測試你的應用"
description: 在 IPRO7AI Reef EVK 上測試自己的應用：主控台手動檢查、開箱韌體的硬體自我檢查、在應用中加入會印出判定結果的自我測試，再以 serial_monitor.py 與 build_freertos.sh test 自動執行，最後在電腦上跑主機端單元測試。
---

# 測試你的應用

本教學延續[建立第一個自己的應用](first-own-app.md)的 `my_reef_app`。完成後，應用會有一個 `myapp selftest` 指令與開機自我測試，最後一行印出 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；您可以在主控台手動執行，也可以用一行命令或 CI 腳本自動燒錄、重置並判定結果。

## 前置需求 { #prerequisites }

- 完成[建立第一個自己的應用](first-own-app.md)，`apps/custom/my_reef_app` 能建置、燒錄並回應 `myapp status`。
- IPRO7AI Reef EVK 以 USB-C 供電，U6 接 IPRO Debug Probe 或 USB 轉 UART 線。
- 自動化的部分（`tools/serial_monitor.py`、`build_freertos.sh`）需要 macOS 或 Linux 與 Python 3.8 以上：`serial_monitor.py` 使用 POSIX 的 termios，不需要 pyserial，但不能在 Windows 上執行。
- 主機端單元測試需要電腦上的 C 編譯器（`cc`），不需要板子與 RISC-V 工具鏈。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **在主控台手動檢查**：開啟主控台（115200 baud），依序輸入下列指令，確認應用與系統狀態：

    ```text
    myapp status
    ps
    free
    ```

    `myapp status` 印出 LED 顏色、閃爍週期與按鍵次數；`ps` 列出所有任務，其中要有 `my_app` 與 `keys`；`free` 印出 `Heap: total <總量>, free <剩餘>, min free <最低剩餘>`。按 SW3 後再輸入一次 `myapp status`，SW3 的次數要加 1。這類檢查適合開發中隨手確認，但每次都要人看。

2. **用開箱韌體確認硬體**：懷疑是板子本身的問題時，先燒錄開箱韌體 `ipro7ai_reef_demo`（建置與燒錄見[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)），在主控台輸入：

    ```text
    reef selftest
    ```

    約 3 秒內依序檢查：LED 亮紅、綠、藍；喇叭發出 1 kHz 測試音；SD 卡座偵測；相機探測：

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: <something seated | empty>, supply <on | off>
    [4/4] camera bus: <感測器名稱> at 0x<位址>
    done - keys: press any and run `btn status`
    ```

    沒接相機時第 4 項是 `no sensor`。這是看的、聽的硬體冒煙測試，結果要由人判斷；確認硬體正常後，再燒回自己的應用。

3. **在應用中加入自我測試**：自我測試要做三件事：逐項印出結果、最後印出固定的判定字串、傳回失敗項數。建立 `selftest.c`：

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

    判定字串 `ALL TESTS PASSED` 與 `SOME TESTS FAILED` 正是 `build_freertos.sh test` 等待的兩個字串。

4. **讓 LED 只由應用任務驅動**：自我測試會操作 LED，而 LED 平常由 `my_app` 任務閃爍。為了不讓兩者同時寫 LED，shell 指令只「請求」測試，由 `my_app` 任務執行。在 `my_app.h` 的 `#endif` 前加入：

    ```c title="apps/custom/my_reef_app/my_app.h（加入）"
    /* Self-test: one line per check, then ALL TESTS PASSED or SOME TESTS FAILED.
     * Returns the number of failed checks. Drives the LED: call it from the app
     * task only; other tasks use my_app_request_selftest(). */
    int      my_app_selftest(void);
    void     my_app_request_selftest(void);
    ```

    在 `main.c` 中做四處修改。在 `s_blink_ms` 下面加入任務代號：

    ```c title="apps/custom/my_reef_app/main.c（加入）"
    static TaskHandle_t      s_app_task;
    ```

    在 `my_app_get_blink_ms()` 下面加入請求函式：

    ```c title="apps/custom/my_reef_app/main.c（加入）"
    void my_app_request_selftest(void)
    {
        if (s_app_task != NULL) {
            xTaskNotifyGive(s_app_task);
        }
    }
    ```

    把 `app_task()` 中 `blinking the RGB LED` 那行之後到迴圈結束的部分改成下面這樣：開機時執行一次自我測試（由 `.config` 選項控制），迴圈中的等待改用任務通知，收到請求就提早醒來執行測試：

    ```c title="apps/custom/my_reef_app/main.c（app_task 的後半）"
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

    最後在 `main()` 中把任務代號存起來：

    ```c title="apps/custom/my_reef_app/main.c（main 內修改）"
        xTaskCreate(app_task, "my_app", 1024, NULL, 5, &s_app_task);
    ```

5. **加入 `myapp selftest` 指令與開機選項**：在 `app_cli.c` 的 `cmd_myapp()` 中，把最後的 `else` 分支換成：

    ```c title="apps/custom/my_reef_app/app_cli.c（修改）"
        } else if (strcmp(argv[1], "selftest") == 0) {
            my_app_request_selftest();
        } else {
            printf("myapp [status] | myapp color <r> <g> <b> | myapp blink <ms> | myapp selftest\n");
        }
    ```

    在 `CMakeLists.txt` 的 `target_sources` 加入 `selftest.c`：

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt（節錄）"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
        app_cli.c
        selftest.c
    )
    ```

    在 `.config` 最後加入自己的選項。`.config` 中每個 `CONFIG_X=y` 都會成為全域的 `-DCONFIG_X=1`，所以程式可以用 `#ifdef` 判斷：

    ```ini title="apps/custom/my_reef_app/.config（加入）"
    # my_reef_app: run the self-test once at boot
    CONFIG_MYAPP_SELFTEST_AT_BOOT=y
    ```

    改了 `.config` 之後做一次乾淨建置：

    ```bash
    ./build_freertos.sh clean build my_reef_app
    ```

    ```text
    ✓ Build succeeded (10s)
      Binary: <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin (96 KB)
    ```

6. **燒錄並手動執行一次**：照[建立第一個自己的應用](first-own-app.md)的步驟 6 燒錄，按 SW2 重置。開機時 LED 依序亮紅、綠、藍，主控台印出：

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: blinking the RGB LED on GPIO24
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <剩餘位元組> bytes of heap free
    ALL TESTS PASSED
    ```

    之後隨時可以在主控台輸入 `myapp selftest` 再跑一次。開機時按住 SW3，`keys` 一項會是 `FAIL`，最後一行變成 `SOME TESTS FAILED`，可以用這個方法確認失敗路徑也正確。

7. **用 `serial_monitor.py` 自動判定**：關掉終端程式（同一個序列埠不能同時被兩個程式開啟），在 SDK 根目錄執行：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX \
        --send "myapp selftest" \
        --wait-for "ALL TESTS PASSED|SOME TESTS FAILED" --timeout 15
    echo "exit=$?"
    ```

    輸出如下（省略 shell 的指令回顯與提示字元）：

    ```text
    [serial_monitor] Sent: myapp selftest
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <剩餘位元組> bytes of heap free
    ALL TESTS PASSED

    [serial_monitor] MATCHED: ALL TESTS PASSED
    exit=0
    ```

    `serial_monitor.py` 以 115200 baud 開啟序列埠（`--baud` 可改），送出 `--send` 的指令，再等待符合 `--wait-for` 正規表示式的輸出。結束碼：

    | 結束碼 | 意義 |
    |---|---|
    | 0 | 符合的文字含有 `PASSED` |
    | 1 | 符合的文字不含 `PASSED`（例如 `SOME TESTS FAILED`） |
    | 2 | `--timeout` 秒內沒有符合（沒給 `--wait-for` 時，一律在逾時後以 2 結束） |
    | 3 | 無法開啟序列埠或送出指令 |

    等待不含 `PASSED` 的字串時，結束碼 1 代表「找到了」。例如確認重置後應用有起來：`--send reboot --wait-for "Hello from my_reef_app"` 成功時結束碼是 1，逾時才是 2。

8. **寫成腳本或放進 CI**：把上一步包成腳本，依結束碼決定成敗，並以 `--log` 保存完整輸出：

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

    在 CI 上執行時，板子要接在執行工作的那台機器上。

9. **一行命令完成建置、燒錄與測試**：`build_freertos.sh test` 依序建置、燒錄（先送 `reboot_dl` 讓板子進入下載模式）、送出 `reboot`，再等待 `ALL TESTS PASSED|SOME TESTS FAILED`。開機自我測試（步驟 5 的 `CONFIG_MYAPP_SELFTEST_AT_BOOT=y`）就是讓應用在重置後自己印出判定。燒錄工具以 `IPRO_FLASH_TOOL` 指定，分割表以 `-P` 指定，`--chip-variant IPRO7AI` 由腳本依 `.config` 的 `CONFIG_IPRO7AI_REEF=y` 自動帶入：

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

    成功時最後印出：

    ```text
    ✓ All tests passed
    ```

    結束碼 0 為通過、1 為有測試失敗、2 為 `-t` 秒內（預設 30）沒看到判定。燒錄完成後若主控台沒有任何輸出，按一下 SW2（RESET）讓板子離開下載模式，測試會繼續等到逾時為止。Windows 上沒有 `build_freertos.sh test`，請以手動燒錄加上步驟 6 的方式測試。

10. **在電腦上跑主機端單元測試**：不碰硬體的純邏輯程式（訊號處理、協定解析、資料轉換）最好在電腦上測。SDK 隨附幾組這類測試，各自是一個 `test_host/run.sh`，用電腦的 `cc` 編譯並執行。音訊元件的測試涵蓋 Reef 麥克風使用的 PDM 處理鏈：

    ```bash
    sh components/audio/test_host/run.sh
    ```

    ```text
    audio_asrc: 826 passed, 0 failed
    audio_pdm_mic: 37 passed, 0 failed
    ```

    LE Audio 耳機應用的 DAC 雜訊整形器：

    ```bash
    sh apps/bluetooth/le_audio/ipro_le_audio_headset/test_host/run.sh
    ```

    ```text
    in-band error rms: 32 kHz rounding 0.1916 codes, order 1 0.00521 (31.3 dB better), order 2 0.000653 (49.4 dB better)
    dac_ns: all tests passed
    ```

    兩個腳本在任何一項失敗時都以非 0 結束，可以直接放進 CI。要為自己的模組寫主機端測試，照 `components/audio/test_host/` 的做法：一個 `test_*.c` 含 `main()`，與受測的 `.c` 一起用 `cc` 編譯（`run.sh` 加了 `-fsanitize=address,undefined` 以抓出記憶體錯誤）。

</div>

## 確認結果 { #verify }

- 重置後主控台最後印出 `ALL TESTS PASSED`，LED 先亮紅、綠、藍再開始閃爍。
- `python3 tools/serial_monitor.py <序列埠> --send "myapp selftest" --wait-for "ALL TESTS PASSED|SOME TESTS FAILED"` 的結束碼為 0；開機時按住 SW3 再執行一次，結束碼為 1。
- `./build_freertos.sh … test my_reef_app` 印出 `✓ All tests passed` 並以 0 結束。
- `sh components/audio/test_host/run.sh` 印出兩行 `0 failed`。

## 測試方式比較 { #methods }

| 方式 | 需要 | 判定 | 適合 |
|---|---|---|---|
| 主控台手動指令 | 板子、終端程式 | 人 | 開發中隨手確認 |
| `reef selftest`（開箱韌體） | 板子、開箱韌體 | 人（看、聽） | 確認板子硬體正常 |
| `myapp selftest`＋`serial_monitor.py` | 板子、macOS／Linux | 結束碼 0／1／2／3 | 腳本、CI，不重新燒錄 |
| `build_freertos.sh test` | 板子、IntelProCube、macOS／Linux | 結束碼 0／1／2 | 每次修改後完整驗證 |
| `test_host/run.sh` | 電腦的 `cc` | 結束碼 | 純邏輯，最快 |

SDK 的 `ipro_unit_test` 也用 `build_freertos.sh test` 執行，但它的設定是 IPRO7 EVB，不是 Reef。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `serial_monitor.py` 結束碼 3，訊息 `Failed to open …` | 序列埠被終端程式占用，或埠名錯誤 | 關掉終端程式；macOS 用 `/dev/cu.*`，不要用 `/dev/tty.*` |
| 結束碼 2，輸出只有 `Sent: myapp selftest` | 應用沒有在執行，或不是這一版韌體 | 開終端程式確認 `myapp selftest` 有回應；重新燒錄 |
| `myapp selftest` 只印出使用說明 | 舊版 `app_cli.c` | 確認步驟 5 的 `selftest` 分支已加入並重新建置 |
| 開機沒有自我測試輸出 | `.config` 改了但沒有乾淨建置，或選項名稱打錯 | `./build_freertos.sh clean build my_reef_app`，確認 `CONFIG_MYAPP_SELFTEST_AT_BOOT=y` |
| `build_freertos.sh test` 出現 `Flash tool not found` | 沒有設定 `IPRO_FLASH_TOOL`，PATH 上也沒有燒錄工具 | 設定 `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`（或 `_linux`） |
| `Several serial ports, pass -p PORT …` | 接了不只一個 USB 序列埠（例如探針的兩個埠） | 用 `-p` 或 `IPRO_SERIAL_PORT` 指定主控台的埠；探針是名稱以 `02` 結尾的埠 |
| `Test timed out (no result pattern seen)` | 燒錄後板子停在下載模式，或判定字串沒印出 | 按 SW2；用 `-t 60` 延長等待；確認開機自我測試選項已開啟 |
| `keys: FAIL` | 測試時有按鍵被按住 | 放開按鍵再測；若持續失敗，用 `myapp status` 看哪個按鍵顯示 `down` |

## 下一步 { #next-steps }

- [建置與燒錄流程](build-and-flash.md)：`build_freertos.sh` 的其他動作與選項。
- [燒錄與序列埠](../get-started/flash-and-monitor.md)：下載模式的各種進入方式與 `serial_monitor.py` 的完整選項。
- [第一個 BLE 應用](first-ble-app.md)：在 Reef 上執行並修改 GATT 參考應用。
