---
title: "アプリケーションのテスト"
description: IPRO7AI Reef EVK 上で独自アプリケーションをテストします。コンソールでの手動確認、出荷時ファームウェアのハードウェアセルフテスト、判定結果を出力するアプリケーション内のセルフテスト、serial_monitor.py と build_freertos.sh test による自動実行、ホスト側のユニットテストを扱います。
---

# アプリケーションのテスト

このチュートリアルでは、[最初の独自アプリケーションを作る](first-own-app.md)の `my_reef_app` を引き続き使います。最終的に、アプリケーションには `myapp selftest` コマンドと、最後の行が `ALL TESTS PASSED` または `SOME TESTS FAILED` になる起動時セルフテストが加わります。セルフテストはコンソールから手動で実行することも、1 つのコマンドや CI スクリプトにボードへの書き込み、リセット、結果の判定を任せることもできます。

## 前提条件 { #prerequisites }

- [最初の独自アプリケーションを作る](first-own-app.md)を完了していること。`apps/custom/my_reef_app` のビルドと書き込みができ、`myapp status` に応答します。
- USB-C から給電し、U6 に IPRO Debug Probe または USB-UART ケーブルを接続した IPRO7AI Reef EVK。
- 自動化の部分（`tools/serial_monitor.py`、`build_freertos.sh`）には、Python 3.8 以降を備えた macOS または Linux。`serial_monitor.py` は POSIX termios を使うため pyserial は不要ですが、Windows では動作しません。
- ホスト側のユニットテストには、コンピューター上の C コンパイラー（`cc`）。ボードや RISC-V ツールチェーンは使いません。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **コンソールで手動で確認します。** コンソール（115200 ボー）を開き、次のコマンドを入力してアプリケーションとシステムの状態を確認します。

    ```text
    myapp status
    ps
    free
    ```

    `myapp status` は LED の色、点滅周期、キーの押下回数を表示します。`ps` は `my_app` や `keys` を含むすべてのタスクを一覧表示します。`free` は `Heap: total <合計>, free <空き>, min free <最小空き>` を表示します。SW3 を押してから `myapp status` を再度実行すると、SW3 の回数が 1 増えています。このような確認は開発中には手軽ですが、毎回だれかが結果を読む必要があります。

2. **出荷時ファームウェアでハードウェアを確認します。** ボード自体を疑う場合は、出荷時ファームウェア `ipro7ai_reef_demo` を書き込み（ビルドと書き込みは[最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)のとおり）、次のように入力します。

    ```text
    reef selftest
    ```

    約 3 秒で、LED を赤、緑、青に点灯させ、スピーカーで 1 kHz のトーンを鳴らし、SD スロットを確認し、カメラを検出します。

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: <something seated | empty>, supply <on | off>
    [4/4] camera bus: <センサー名> at 0x<アドレス>
    done - keys: press any and run `btn status`
    ```

    カメラがない場合、最後の項目は `no sensor` になります。このスモークテストは目と耳で判定します。ハードウェアに問題がないことがわかったら、独自アプリケーションを再度書き込みます。

3. **アプリケーションにセルフテストを追加します。** セルフテストは次の 3 つを行います。確認ごとに 1 行を出力し、最後に決まった判定文字列を出力し、失敗の数を返します。`selftest.c` を作成します。

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

    `ALL TESTS PASSED` と `SOME TESTS FAILED` は、`build_freertos.sh test` が待ち受ける 2 つの文字列そのものです。

4. **LED の操作はアプリケーションタスクに任せます。** セルフテストは LED を駆動しますが、その LED は `my_app` タスクが点滅させています。両者が同時に LED に書き込まないように、シェルコマンドはテストを要求するだけにし、テストは `my_app` タスクが実行します。`my_app.h` の `#endif` の前に次を追加します。

    ```c title="apps/custom/my_reef_app/my_app.h（追加）"
    /* Self-test: one line per check, then ALL TESTS PASSED or SOME TESTS FAILED.
     * Returns the number of failed checks. Drives the LED: call it from the app
     * task only; other tasks use my_app_request_selftest(). */
    int      my_app_selftest(void);
    void     my_app_request_selftest(void);
    ```

    `main.c` に 4 か所の変更を加えます。`s_blink_ms` の下にタスクハンドルを追加します。

    ```c title="apps/custom/my_reef_app/main.c（追加）"
    static TaskHandle_t      s_app_task;
    ```

    `my_app_get_blink_ms()` の下に、要求用の関数を追加します。

    ```c title="apps/custom/my_reef_app/main.c（追加）"
    void my_app_request_selftest(void)
    {
        if (s_app_task != NULL) {
            xTaskNotifyGive(s_app_task);
        }
    }
    ```

    `app_task()` 内の `blinking the RGB LED` の行からループの終わりまでを、次のコードに置き換えます。起動時にセルフテストを 1 回実行し（`.config` のオプションで制御）、ループはタスク通知を待つようになるため、要求があると待機を早めに切り上げてテストを実行します。

    ```c title="apps/custom/my_reef_app/main.c（app_task の後半）"
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

    最後に、`main()` でタスクハンドルを保持します。

    ```c title="apps/custom/my_reef_app/main.c（main 内の変更）"
        xTaskCreate(app_task, "my_app", 1024, NULL, 5, &s_app_task);
    ```

5. **`myapp selftest` コマンドと起動時オプションを追加します。** `app_cli.c` の `cmd_myapp()` で、最後の `else` 分岐を次のものに置き換えます。

    ```c title="apps/custom/my_reef_app/app_cli.c（変更）"
        } else if (strcmp(argv[1], "selftest") == 0) {
            my_app_request_selftest();
        } else {
            printf("myapp [status] | myapp color <r> <g> <b> | myapp blink <ms> | myapp selftest\n");
        }
    ```

    `CMakeLists.txt` の `target_sources` に `selftest.c` を追加します。

    ```cmake title="apps/custom/my_reef_app/CMakeLists.txt（抜粋）"
    target_sources(app PRIVATE
        ${REEF_DEMO_SRC}/rgb_led.c
        ${REEF_DEMO_SRC}/keys.c
        app_cli.c
        selftest.c
    )
    ```

    `.config` の末尾に独自のオプションを追加します。`.config` の各 `CONFIG_X=y` はグローバルな `-DCONFIG_X=1` になるため、コードから `#ifdef` で判定できます。

    ```ini title="apps/custom/my_reef_app/.config（追加）"
    # my_reef_app: run the self-test once at boot
    CONFIG_MYAPP_SELFTEST_AT_BOOT=y
    ```

    `.config` を変更したら、クリーンビルドを行います。

    ```bash
    ./build_freertos.sh clean build my_reef_app
    ```

    ```text
    ✓ Build succeeded (10s)
      Binary: <SDK>/apps/custom/my_reef_app/build/build_out/my_reef_app_IPRO7.bin (96 KB)
    ```

6. **書き込み、手動で一度実行します。** [最初の独自アプリケーションを作る](first-own-app.md)の手順 6 のとおりに書き込み、SW2 を短く押します。起動時に LED が赤、緑、青に点灯し、コンソールに次のように表示されます。

    ```text
    MYAPP: Hello from my_reef_app
    MYAPP: blinking the RGB LED on GPIO24
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <空きバイト数> bytes of heap free
    ALL TESTS PASSED
    ```

    `myapp selftest` と入力すれば、いつでも再実行できます。失敗時の動作を確認するには、SW3 を押したままボードを起動します。`keys` が `FAIL` になり、最後の行が `SOME TESTS FAILED` になります。

7. **`serial_monitor.py` に結果を判定させます。** ターミナルプログラムを閉じ（2 つのプログラムが同じポートを開くことはできません）、SDK のルートから次を実行します。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX \
        --send "myapp selftest" \
        --wait-for "ALL TESTS PASSED|SOME TESTS FAILED" --timeout 15
    echo "exit=$?"
    ```

    出力は次のとおりです（シェルのエコーとプロンプトは省略）。

    ```text
    [serial_monitor] Sent: myapp selftest
    [selftest] led: PASS
    [selftest] keys: PASS
    [selftest] heap: PASS
    [selftest] <空きバイト数> bytes of heap free
    ALL TESTS PASSED

    [serial_monitor] MATCHED: ALL TESTS PASSED
    exit=0
    ```

    `serial_monitor.py` はポートを 115200 ボーで開き（`--baud` で変更可能）、`--send` のコマンドを送信して、`--wait-for` の正規表現に一致する出力を待ちます。終了コードは次のとおりです。

    | 終了コード | 意味 |
    |---|---|
    | 0 | 一致したテキストに `PASSED` が含まれる |
    | 1 | 一致したテキストに `PASSED` が含まれない（例：`SOME TESTS FAILED`） |
    | 2 | `--timeout` 秒以内に何も一致しなかった（`--wait-for` がない場合は、タイムアウトで必ず 2 で終了） |
    | 3 | ポートを開けなかった、またはコマンドを送信できなかった |

    `PASSED` を含まない文字列を待つ場合、終了コード 1 は「見つかった」ことを意味します。たとえばリセット後にアプリケーションが起動することを確認する `--send reboot --wait-for "Hello from my_reef_app"` は、成功すると 1、タイムアウトすると 2 で終了します。

8. **スクリプトや CI に組み込みます。** 前の手順をスクリプトにまとめ、終了コードで成否を判定し、`--log` で出力全体を保存します。

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

    CI で使う場合は、ジョブを実行するマシンにボードを接続しておく必要があります。

9. **ビルド、書き込み、テストを 1 つのコマンドで行います。** `build_freertos.sh test` は、ビルドと書き込み（先に `reboot_dl` を送ってボードをダウンロードモードにします）を行い、`reboot` を送信して `ALL TESTS PASSED|SOME TESTS FAILED` を待ちます。リセット後にアプリケーションが自分で判定を出力するのは、起動時セルフテスト（手順 5 の `CONFIG_MYAPP_SELFTEST_AT_BOOT=y`）があるからです。書き込みツールは `IPRO_FLASH_TOOL` で、パーティションテーブルは `-P` で指定します。`.config` に `CONFIG_IPRO7AI_REEF=y` があるため、`--chip-variant IPRO7AI` はスクリプトが自動で追加します。

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

    成功すると、最後に次のように表示されます。

    ```text
    ✓ All tests passed
    ```

    終了コード 0 は合格、1 は一部のテストの失敗、2 は `-t` 秒（デフォルト 30）以内に判定が出なかったことを意味します。書き込み後にコンソールに何も表示されない場合は、SW2（RESET）を短く押してダウンロードモードを抜けます。テストはタイムアウトまで待ち続けます。`build_freertos.sh test` は Windows では動作しません。Windows では手動で書き込み、手順 6 のとおりにテストします。

10. **ホスト側のユニットテストを実行します。** ハードウェアに触れない純粋なロジック（信号処理、プロトコル解析、データ変換）は、コンピューター上でテストするのが最適です。SDK にはこのようなテストがいくつか含まれており、それぞれ `test_host/run.sh` がコンピューターの `cc` でコンパイルして実行します。オーディオコンポーネントのテストは、Reef のマイクが使う PDM チェーンを対象とします。

    ```bash
    sh components/audio/test_host/run.sh
    ```

    ```text
    audio_asrc: 826 passed, 0 failed
    audio_pdm_mic: 37 passed, 0 failed
    ```

    LE Audio ヘッドセットアプリケーションの DAC ノイズシェーパーのテストは次のとおりです。

    ```bash
    sh apps/bluetooth/le_audio/ipro_le_audio_headset/test_host/run.sh
    ```

    ```text
    in-band error rms: 32 kHz rounding 0.1916 codes, order 1 0.00521 (31.3 dB better), order 2 0.000653 (49.4 dB better)
    dac_ns: all tests passed
    ```

    どちらのスクリプトも、いずれかの確認が失敗すると 0 以外で終了するため、そのまま CI に組み込めます。独自モジュールのホストテストを書くときは `components/audio/test_host/` に倣います。`main()` を持つ `test_*.c` を、テスト対象の `.c` とともに `cc` でコンパイルします（`run.sh` はメモリエラーを検出するために `-fsanitize=address,undefined` を追加します）。

</div>

## 動作確認 { #verify }

- リセット後、コンソールの出力が `ALL TESTS PASSED` で終わり、LED は点滅を始める前に赤、緑、青に点灯します。
- `python3 tools/serial_monitor.py <ポート> --send "myapp selftest" --wait-for "ALL TESTS PASSED|SOME TESTS FAILED"` は 0 で終了します。SW3 を押したまま起動した場合は 1 で終了します。
- `./build_freertos.sh … test my_reef_app` は `✓ All tests passed` を表示し、0 で終了します。
- `sh components/audio/test_host/run.sh` は `0 failed` で終わる 2 行を表示します。

## テストの方法 { #methods }

| 方法 | 必要なもの | 判定 | 用途 |
|---|---|---|---|
| コンソールコマンドを手動で実行 | ボード、ターミナル | 人 | 開発中の手早い確認 |
| `reef selftest`（出荷時ファームウェア） | ボード、出荷時ファームウェア | 人（目視と聴覚） | ハードウェアが正常であることの確認 |
| `myapp selftest` + `serial_monitor.py` | ボード、macOS/Linux | 終了コード 0/1/2/3 | スクリプトや CI（再書き込みなし） |
| `build_freertos.sh test` | ボード、IntelProCube、macOS/Linux | 終了コード 0/1/2 | 変更のたびの全体確認 |
| `test_host/run.sh` | コンピューター上の `cc` | 終了コード | 純粋なロジック、最も高速 |

SDK の `ipro_unit_test` も `build_freertos.sh test` で実行できますが、Reef ではなく IPRO7 EVB 向けに構成されています。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| `serial_monitor.py` が 3 で終了し、`Failed to open …` と表示される | ターミナルプログラムがポートを使用している、またはポート名が正しくない | ターミナルを閉じます。macOS では `/dev/tty.*` ではなく `/dev/cu.*` を使います |
| 終了コード 2 で、出力に `Sent: myapp selftest` しか表示されない | アプリケーションが動作していない、または古いビルドである | ターミナルで `myapp selftest` が応答することを確認し、再度書き込みます |
| `myapp selftest` が使い方の行だけを表示する | `app_cli.c` が古い | 手順 5 の `selftest` 分岐が入っていることを確認し、再ビルドします |
| 起動時にセルフテストの出力がない | クリーンビルドせずに `.config` を変更した、またはオプション名のつづりが誤っている | `./build_freertos.sh clean build my_reef_app` を実行し、`CONFIG_MYAPP_SELFTEST_AT_BOOT=y` を確認します |
| `build_freertos.sh test` で `Flash tool not found` と表示される | `IPRO_FLASH_TOOL` が未設定で、書き込みツールが PATH 上にない | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`（または `_linux`）を設定します |
| `Several serial ports, pass -p PORT …` | USB シリアルポートが複数ある（プローブには 2 つある） | `-p` または `IPRO_SERIAL_PORT` でコンソールポートを指定します。プローブでは `02` で終わるポートです |
| `Test timed out (no result pattern seen)` | 書き込み後にボードがダウンロードモードのままになっている、または判定が出力されなかった | SW2 を短く押します。`-t 60` で時間を延ばします。起動時セルフテストのオプションが有効であることを確認します |
| `keys: FAIL` | テスト中にキーが押されていた | キーを離して再実行します。失敗が続く場合は、`myapp status` でどのキーが `down` になっているかを確認します |

## 次のステップ { #next-steps }

- [ビルドと書き込みの流れ](build-and-flash.md)：`build_freertos.sh` のその他のアクションとオプション。
- [書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)：ダウンロードモードに入るすべての方法と、`serial_monitor.py` の全オプション。
- [最初の BLE アプリケーション](first-ble-app.md)：Reef 上で GATT リファレンスアプリケーションを実行し、変更します。
