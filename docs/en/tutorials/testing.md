---
title: "Test Your Application"
description: Test your own application on the IPRO7AI Reef EVK with manual console checks, the out-of-box hardware self-test, a self-test in your app that prints a verdict, automated runs with serial_monitor.py and build_freertos.sh test, and host-side unit tests.
---

# Test Your Application

This tutorial continues with `my_reef_app` from [Create Your First Application](first-own-app.md). At the end the app has a `myapp selftest` command and a boot-time self-test whose last line is `ALL TESTS PASSED` or `SOME TESTS FAILED`. You can run it by hand at the console, or let one command or a CI script flash the board, reset it and judge the result.

## Prerequisites { #prerequisites }

- [Create Your First Application](first-own-app.md) done: `apps/custom/my_reef_app` builds, flashes and answers `myapp status`.
- An IPRO7AI Reef EVK powered from USB-C, with an IPRO Debug Probe or a USB-UART cable on U6.
- For the automated parts (`tools/serial_monitor.py`, `build_freertos.sh`): macOS or Linux with Python 3.8 or later. `serial_monitor.py` uses POSIX termios and needs no pyserial, but it does not run on Windows.
- For host-side unit tests: a C compiler (`cc`) on your computer. No board or RISC-V toolchain is involved.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Check by hand at the console.** Open the console (115200 baud) and type these commands to look at the app and the system:

    ```text
    myapp status
    ps
    free
    ```

    `myapp status` prints the LED colour, the blink period and the key counts. `ps` lists every task, including `my_app` and `keys`. `free` prints `Heap: total <size>, free <free>, min free <lowest>`. Press SW3 and run `myapp status` again: the SW3 count goes up by one. Checks like these are quick while you develop, but someone has to read them every time.

2. **Check the hardware with the out-of-box firmware.** When you suspect the board itself, flash the out-of-box firmware `ipro7ai_reef_demo` (build and flash as in [First FreeRTOS Application](../get-started/first-app-freertos.md)) and type:

    ```text
    reef selftest
    ```

    In about 3 seconds it lights the LED red, green and blue, plays a 1 kHz tone on the speaker, checks the SD slot and probes the camera:

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: <something seated | empty>, supply <on | off>
    [4/4] camera bus: <sensor name> at 0x<address>
    done - keys: press any and run `btn status`
    ```

    Without a camera the last item reads `no sensor`. This smoke test is judged by eye and ear. Once the hardware is known good, flash your own app again.

3. **Add a self-test to your app.** A self-test does three things: it prints one line per check, prints a fixed verdict string at the end and returns the number of failures. Create `selftest.c`:

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

    `ALL TESTS PASSED` and `SOME TESTS FAILED` are exactly the two strings `build_freertos.sh test` waits for.

4. **Keep the LED in the app task's hands.** The self-test drives the LED, which the `my_app` task is blinking. So that the two never write the LED at the same time, the shell command only requests a test and the `my_app` task runs it. Add before the `#endif` in `my_app.h`:

    ```c title="apps/custom/my_reef_app/my_app.h (add)"
    /* Self-test: one line per check, then ALL TESTS PASSED or SOME TESTS FAILED.
     * Returns the number of failed checks. Drives the LED: call it from the app
     * task only; other tasks use my_app_request_selftest(). */
    int      my_app_selftest(void);
    void     my_app_request_selftest(void);
    ```

    Make four changes in `main.c`. Below `s_blink_ms`, add a task handle:

    ```c title="apps/custom/my_reef_app/main.c (add)"
    static TaskHandle_t      s_app_task;
    ```

    Below `my_app_get_blink_ms()`, add the request function:

    ```c title="apps/custom/my_reef_app/main.c (add)"
    void my_app_request_selftest(void)
    {
        if (s_app_task != NULL) {
            xTaskNotifyGive(s_app_task);
        }
    }
    ```

    In `app_task()`, replace everything from the `blinking the RGB LED` line to the end of the loop with the code below. It runs the self-test once at boot (controlled by a `.config` option), and the loop now waits on a task notification, so a request wakes it early to run the test:

    ```c title="apps/custom/my_reef_app/main.c (second half of app_task)"
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

    Finally, keep the task handle in `main()`:

    ```c title="apps/custom/my_reef_app/main.c (change in main)"
        xTaskCreate(app_task, "my_app", 1024, NULL, 5, &s_app_task);
    ```

5. **Add the `myapp selftest` command and the boot option.** In `cmd_myapp()` in `app_cli.c`, replace the final `else` branch with:

    ```c title="apps/custom/my_reef_app/app_cli.c (change)"
        } else if (strcmp(argv[1], "selftest") == 0) {
            my_app_request_selftest();
        } else {
            printf("myapp [status] | myapp color <r> <g> <b> | myapp blink <ms> | myapp selftest\n");
        }
    ```

    Add `selftest.c` to `target_sources` in `CMakeLists.txt`:

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt (excerpt)"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
        app_cli.c
        selftest.c
    )
    ```

    Add your own option at the end of `.config`. Every `CONFIG_X=y` in `.config` becomes a global `-DCONFIG_X=1`, so the code can test it with `#ifdef`:

    ```ini title="apps/custom/my_reef_app/.config (add)"
    # my_reef_app: run the self-test once at boot
    CONFIG_MYAPP_SELFTEST_AT_BOOT=y
    ```

    After changing `.config`, do a clean build:

    ```bash
    ./build_freertos.sh clean build my_reef_app
    ```

    ```text
    ✓ Build succeeded (10s)
      Binary: <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin (96 KB)
    ```

6. **Flash and run it once by hand.** Flash as in step 6 of [Create Your First Application](first-own-app.md) and tap SW2. At boot the LED shows red, green and blue, and the console prints:

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: blinking the RGB LED on GPIO24
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <free bytes> bytes of heap free
    ALL TESTS PASSED
    ```

    Type `myapp selftest` at any time to run it again. To check the failure path, hold SW3 while the board boots: `keys` reads `FAIL` and the last line becomes `SOME TESTS FAILED`.

7. **Let `serial_monitor.py` judge the result.** Close your terminal program (two programs cannot open the same port), then run from the SDK root:

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX \
        --send "myapp selftest" \
        --wait-for "ALL TESTS PASSED|SOME TESTS FAILED" --timeout 15
    echo "exit=$?"
    ```

    The output (shell echo and prompt left out):

    ```text
    [serial_monitor] Sent: myapp selftest
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <free bytes> bytes of heap free
    ALL TESTS PASSED

    [serial_monitor] MATCHED: ALL TESTS PASSED
    exit=0
    ```

    `serial_monitor.py` opens the port at 115200 baud (change it with `--baud`), sends the `--send` command and waits for output that matches the `--wait-for` regular expression. Exit codes:

    | Exit code | Meaning |
    |---|---|
    | 0 | The matched text contains `PASSED` |
    | 1 | The matched text does not contain `PASSED` (for example `SOME TESTS FAILED`) |
    | 2 | Nothing matched within `--timeout` seconds (without `--wait-for`, it always ends with 2 at the timeout) |
    | 3 | The port could not be opened or the command could not be sent |

    When you wait for a string without `PASSED`, exit code 1 means "found". For example, to check that the app comes up after a reset, `--send reboot --wait-for "Hello from my_reef_app"` exits with 1 on success and 2 on a timeout.

8. **Put it in a script or in CI.** Wrap the previous step in a script that decides on the exit code and keeps the full output with `--log`:

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

    In CI, the board must be connected to the machine that runs the job.

9. **Build, flash and test in one command.** `build_freertos.sh test` builds, flashes (sending `reboot_dl` first to put the board in download mode), sends `reboot` and waits for `ALL TESTS PASSED|SOME TESTS FAILED`. The boot-time self-test (`CONFIG_MYAPP_SELFTEST_AT_BOOT=y` from step 5) is what makes the app print a verdict on its own after the reset. Name the flasher with `IPRO_FLASH_TOOL` and the partition table with `-P`; the script adds `--chip-variant IPRO7AI` itself because `.config` has `CONFIG_IPRO7AI_REEF=y`:

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

    On success it ends with:

    ```text
    ✓ All tests passed
    ```

    Exit code 0 is a pass, 1 means some tests failed, 2 means no verdict within `-t` seconds (30 by default). If the console stays silent after flashing, tap SW2 (RESET) to leave download mode; the test keeps waiting until its timeout. `build_freertos.sh test` does not run on Windows; there, flash by hand and test as in step 6.

10. **Run host-side unit tests.** Pure logic that does not touch hardware (signal processing, protocol parsing, data conversion) is best tested on your computer. The SDK ships several such tests, each a `test_host/run.sh` that compiles with your computer's `cc` and runs. The audio component's test covers the PDM chain the Reef's microphone uses:

    ```bash
    sh components/audio/test_host/run.sh
    ```

    ```text
    audio_asrc: 826 passed, 0 failed
    audio_pdm_mic: 37 passed, 0 failed
    ```

    The DAC noise shaper of the LE Audio headset app:

    ```bash
    sh apps/bluetooth/le_audio/ipro_le_audio_headset/test_host/run.sh
    ```

    ```text
    in-band error rms: 32 kHz rounding 0.1916 codes, order 1 0.00521 (31.3 dB better), order 2 0.000653 (49.4 dB better)
    dac_ns: all tests passed
    ```

    Both scripts exit non-zero when any check fails, so they drop straight into CI. To write host tests for your own module, follow `components/audio/test_host/`: a `test_*.c` with `main()`, compiled with `cc` together with the `.c` under test (`run.sh` adds `-fsanitize=address,undefined` to catch memory errors).

</div>

## Verify { #verify }

- After a reset the console ends with `ALL TESTS PASSED`, and the LED shows red, green and blue before it starts blinking.
- `python3 tools/serial_monitor.py <port> --send "myapp selftest" --wait-for "ALL TESTS PASSED|SOME TESTS FAILED"` exits with 0; with SW3 held during boot, it exits with 1.
- `./build_freertos.sh … test my_reef_app` prints `✓ All tests passed` and exits with 0.
- `sh components/audio/test_host/run.sh` prints two lines ending in `0 failed`.

## Ways to test { #methods }

| Method | Needs | Verdict | Use it for |
|---|---|---|---|
| Console commands by hand | Board, terminal | A person | Quick checks while developing |
| `reef selftest` (out-of-box firmware) | Board, out-of-box firmware | A person (look and listen) | Knowing the hardware is good |
| `myapp selftest` + `serial_monitor.py` | Board, macOS/Linux | Exit code 0/1/2/3 | Scripts and CI, no reflash |
| `build_freertos.sh test` | Board, IntelProCube, macOS/Linux | Exit code 0/1/2 | Full check after every change |
| `test_host/run.sh` | `cc` on your computer | Exit code | Pure logic, fastest |

The SDK's `ipro_unit_test` also runs with `build_freertos.sh test`, but it is configured for the IPRO7 EVB, not the Reef.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `serial_monitor.py` exits with 3, `Failed to open …` | A terminal program holds the port, or the port name is wrong | Close the terminal; on macOS use `/dev/cu.*`, not `/dev/tty.*` |
| Exit code 2, output shows only `Sent: myapp selftest` | The app is not running, or it is an older build | Check in a terminal that `myapp selftest` answers; flash again |
| `myapp selftest` prints only the usage line | Old `app_cli.c` | Check that the `selftest` branch from step 5 is in, and rebuild |
| No self-test output at boot | `.config` changed without a clean build, or the option name is misspelled | Run `./build_freertos.sh clean build my_reef_app` and check `CONFIG_MYAPP_SELFTEST_AT_BOOT=y` |
| `build_freertos.sh test` says `Flash tool not found` | `IPRO_FLASH_TOOL` is unset and the flasher is not on PATH | Set `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` (or `_linux`) |
| `Several serial ports, pass -p PORT …` | More than one USB serial port is present (a probe has two) | Name the console port with `-p` or `IPRO_SERIAL_PORT`; on a probe it is the one ending in `02` |
| `Test timed out (no result pattern seen)` | The board stayed in download mode after flashing, or no verdict was printed | Tap SW2; allow more time with `-t 60`; check that the boot self-test option is on |
| `keys: FAIL` | A key was held during the test | Release the keys and run again; if it keeps failing, `myapp status` shows which key reads `down` |

## Next steps { #next-steps }

- [Build and Flash Workflow](build-and-flash.md): the other `build_freertos.sh` actions and options.
- [Flashing & Serial Console](../get-started/flash-and-monitor.md): every way into download mode and all `serial_monitor.py` options.
- [Your First BLE Application](first-ble-app.md): run and change the GATT reference app on the Reef.
