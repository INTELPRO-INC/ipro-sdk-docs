---
title: "API リファレンス"
description: "IPRO 固有の公開 C API です。SDK V2.1.0 のヘッダーから Doxygen で生成したリファレンスと、プラットフォームの起動、BLE コントローラーの起動、ログの使い方を説明します。"
migrate_from:
  - "api-reference.html — 第 3 階段改由 Doxygen 產生"
---

# API リファレンス

IPRO 固有の公開 C API です。以下の API グループは、SDK V2.1.0 に同梱の公開ヘッダーから Doxygen で生成したもので、すべての関数、型、マクロについてヘッダーのドキュメントを掲載しています。その後の節では、プラットフォームの起動、BLE コントローラーの起動、ログについて説明します。Zephyr Bluetooth の `bt_*` API はここでは繰り返しません。[Zephyr の公式ドキュメント](#ble-host) を参照してください。

!!! note "対象範囲"
    このページの HAL とプラットフォームの API は FreeRTOS アプリケーション用です。Zephyr アプリケーションは Zephyr のデバイスドライバー API を使います。[Zephyr RTOS](../../guides/zephyr.md) を参照してください。

## API グループ { #groups }

公開ヘッダーから生成した、SDK V2.1.0 の分野別の完全なリファレンスです。

<!-- BEGIN generated: api-groups -->
| 分類 | ヘッダー数 | 関数 | 内容 |
|---|---|---|---|
| [プラットフォームとシステム](platform.md) | 11 | 65 | FreeRTOS の起動とフック、HAL の共通定義、システム制御、クロック、タイマー、ウォッチドッグ、RTC、メモリ割り当ての補助。 |
| [メモリ、Flash、ブート](memory-boot.md) | 5 | 45 | Flash の読み書き、PSRAM、boot2、パーティションテーブルの管理。 |
| [電源管理と低消費電力](power.md) | 4 | 52 | 電源モード、PDS スリープと復帰、低消費電力フレームワークと低消費電力 UART。 |
| [周辺 I/O](peripherals.md) | 13 | 62 | GPIO、UART、SPI、I2C、PWM、ADC、DAC、アナログコンパレーター、KeyScan、QDEC、DMA。 |
| [オーディオ](audio.md) | 3 | 16 | オーディオ ADC（PDM マイクとアナログマイク）と I2S。 |
| [カメラと画像処理](camera.md) | 4 | 36 | DVP カメラインターフェース、ISP、ハードウェア MJPEG のエンコードとデコード。 |
| [SD カードと SDIO](sd-sdio.md) | 4 | 61 | ハードウェア SD ホスト、SDIO、PIO で実装した SD ホスト。 |
| [イーサネット](ethernet.md) | 3 | 27 | EMAC、lwIP ネットワークインターフェース、イーサネット PHY。 |
| [PIO](pio.md) | 3 | 24 | プログラマブル I/O：CCI、CMSIS-DAP、スキャンインターフェース。 |
| [セキュリティエンジン](security.md) | 9 | 49 | AES、GMAC、ハッシュ、DSA、ECDSA、P-256、ハードウェア乱数。 |
| [ワイヤレスと BLE コントローラー](wireless-ble.md) | 7 | 41 | 無線の初期化と、IPRO BLE コントローラーの起動、HCI トランスポート、低消費電力、NVDS のインターフェース。 |
| [AI ランタイム](ai.md) | 18 | 133 | NPU ドライバー、推論コア、演算子と後処理、検出モデルと音声モデルのインターフェース。 |
<!-- END generated: api-groups -->

## プラットフォーム初期化と FreeRTOS フック { #rtos-platform }

すべての FreeRTOS アプリケーションは `components/os/freertos/freertos_app_hooks` を共有しています。これはプラットフォームの初期化と、ヒープ、FreeRTOS フック、アサートのデフォルト実装を提供します。

| API | ヘッダー | 用途 |
|---|---|---|
| `void ipro_platform_init(void)` | `components/os/freertos/freertos_app_hooks.h` | `main()` の先頭で一度呼び出します。`platform_init()`、`ipro_setup_heap()`、`hal_boot2_init()`、PSRAM のチェック、`ipro_log_init()`（`CONFIG_IPRO_LOG_ENABLE`）、シェルの初期化（`CONFIG_SHELL`）、`ipro_pm_init()`（`CONFIG_IPRO_PM`）をこの順に実行します。 |
| `void ipro_setup_heap(void)` | 同上 | リンカーシンボルから OCRAM と（有効な場合は）PSRAM のヒープ領域を集め、`vPortDefineHeapRegions()` を呼び出します。`ipro_platform_init()` から呼び出し済みです。 |
| `void ipro_dump_task_stacks(const char *where)` | 同上 | 各タスクの最小空きスタック（バイト）と空きヒープを表示します。`configUSE_TRACE_FACILITY=1` が必要です。 |

次の FreeRTOS フックには、`components/os/freertos/freertos_app_hooks.c` に weak のデフォルト実装があります。置き換えるには、同じ名前の非 weak 関数をアプリケーションのソースに定義します。リンカーが自動的にそちらを選びます。

| フック | デフォルトの動作 |
|---|---|
| `vApplicationStackOverflowHook()` | `[!] Stack overflow: <task name>` と全タスクの空きスタックを表示し、停止します。 |
| `vApplicationMallocFailedHook()` | 要求サイズ、空きヒープと過去最小の空きヒープ、呼び出し元アドレス、タスク名を表示し、停止します。`pvPortMalloc(0)` は警告のみです。 |
| `vApplicationIdleHook()` | `__WFI()` を実行します。 |
| `vApplicationGetIdleTaskMemory()`、`vApplicationGetTimerTaskMemory()` | Idle タスクと Timer タスクの静的スタックと TCB を提供します。 |
| `vAssertCalled()` | 割り込みを禁止し、`[!] ASSERT <file>:<line>` と呼び出し元アドレスを表示して停止します。 |

```c title="main.c（最小のアプリケーション、SDK の README より）"
#include "freertos_app_hooks.h"
#include <FreeRTOS.h>
#include <task.h>

static void app_task(void *arg)
{
    for (;;) {
        /* アプリケーションのコード */
    }
}

int main(void)
{
    ipro_platform_init();   /* ヒープ、boot2、ログ、シェル */
    xTaskCreate(app_task, "app", 1024, NULL, 5, NULL);
    vTaskStartScheduler();
    for (;;) {}
}
```

!!! warning "二重に初期化しないでください"
    `ipro_platform_init()` はすでにシェルとログを初期化しています。アプリケーションからこれらを再度呼び出さないでください。ヒープ、フック、アサートの定型コードを `main.c` に戻すこともしないでください。

FreeRTOS カーネル（V11.1.0）自体の API（`xTaskCreate()`、キュー、セマフォ）については、[FreeRTOS API リファレンス](https://www.freertos.org/Documentation/02-Kernel/04-API-references/01-Task-creation/00-TaskHandle) を参照してください。`xTaskCreate()` に渡すスタックサイズはバイトではなくワード単位です。

## BLE コントローラーの起動 { #ble-core }

Bluetooth LE は、Zephyr v4.4.0 のホストと IPRO BLE コントローラー（ビルド済みライブラリ）を、メモリ上の HCI バイトストリームでつないで構成されています。アプリケーションはコントローラー、HCI ドライバー、ホストの順に起動します。

| API | ヘッダー | 用途 |
|---|---|---|
| `int ipro_ble_ctlr_controller_init(unsigned int task_priority)` | `components/wireless/bluetooth/ipro_ble_controller/include/ipro_ble_controller.h` | コントローラーを起動し、そのタスクを作成します。成功時は 0、起動済みの場合は -1、タスクを作成できなかった場合は -2 を返します。コントローラーには厳しい無線のデッドラインがあるため、アプリケーションのタスクより高い優先度を与えてください。同梱のアプリケーションは `configMAX_PRIORITIES - 1` を使っています。 |
| `int hci_driver_ipro_ble_ctlr_init(void)` | `components/wireless/bluetooth/ipro_bt_host/port/include/hci_driver_ipro_ble_ctlr.h` | `bt_enable()` の前に呼び出します。Zephyr 4.4 は HCI デバイスをビルド時にバインドします。この関数は既存アプリケーションとのソース互換性のために残されており、同梱のアプリケーションは引き続きこの順で呼び出しています。 |
| `void ipro_ble_ctlr_hcitl_host_ready(void)` | `components/wireless/bluetooth/ipro_ble_controller/hcitl/ipro_ble_ctlr_hcitl.h`（`ipro_ble_controller.h` からインクルード） | `bt_enable()` の ready コールバックから呼び出し、HCI の初期化完了を通知します。これ以降、コントローラーはイベントの合間にスリープできます。 |
| `int bt_enable(bt_ready_cb_t cb)` | `<zephyr/bluetooth/bluetooth.h>` | ホストを起動し、完了すると `cb` を呼び出します。[Zephyr Bluetooth API](#ble-host) を参照してください。 |

各呼び出しの間は 50 ms 待ち、FreeRTOS のタスク内で実行してください。起動コードと ready コールバックの全体は [BLE 開発](../../guides/ble.md#ble-init) にあります。

コントローラーライブラリは `.config` の `CONFIG_IPRO_BLE_CTLR_LIB`、`CONFIG_IPRO_BLE_CTLR_FEATURE`、`CONFIG_IPRO_BLE_CTLR_CFG_DBG` で選択します。対応表は [BLE 開発](../../guides/ble.md#controller-variants) にあります。

## Zephyr Bluetooth API { #ble-host }

アプリケーションは `<zephyr/bluetooth/...>` ヘッダーを通じて、Zephyr のコールバック方式の `bt_*` API を使います。SDK に含まれるコピーは `components/wireless/bluetooth/ipro_bt_host/upstream/zephyr/include/zephyr/bluetooth/` にあります。以下のリンク先は、SDK のホストと同じバージョンである Zephyr v4.4.0 のドキュメントです。

| トピック | 主な API | Zephyr v4.4.0 のドキュメント |
|---|---|---|
| Bluetooth API の概要 | — | [Bluetooth API](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/index.html) |
| GAP：有効化、アドバタイズ、スキャン | `bt_enable()`、`bt_le_adv_start()`、`bt_le_scan_start()` | [Generic Access Profile (GAP)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gap.html) |
| 接続管理 | `bt_conn_cb_register()`、`bt_conn_le_create()`、`bt_conn_disconnect()` | [Connection Management](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/connection_mgmt.html) |
| GATT サーバーとクライアント | `BT_GATT_SERVICE_DEFINE()`、`bt_gatt_notify()`、`bt_gatt_discover()` | [Generic Attribute Profile (GATT)](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/gatt.html) |
| LE Audio | BAP、PACS、ASCS、CAP | [Bluetooth Audio](https://docs.zephyrproject.org/4.4.0/connectivity/bluetooth/api/audio/audio.html) |
| ボンディング情報の保存 | `settings_load_subtree()` | [Settings](https://docs.zephyrproject.org/4.4.0/services/settings/index.html) |
| 関数の全索引 | — | [Zephyr API ドキュメント（Doxygen）](https://docs.zephyrproject.org/4.4.0/doxygen/html/group__bluetooth.html) |

!!! tip "SDK のヘッダーが正となります"
    Zephyr のドキュメントは Zephyr カーネルを前提にしています。FreeRTOS アプリケーションでは、ホストは SDK の移植レイヤー上で動作し、その `CONFIG_BT_*` オプションはアプリケーションの `.config` に記述します。マクロを使う前に、SDK のヘッダーに存在するか確認してください。例えば、接続可能なアドバタイズには `BT_LE_ADV_CONN_FAST_1` を使います。`BT_LE_ADV_CONN_NAME` はこのバージョンのホストには存在しません。

## ログ { #log-api }

ヘッダー：`components/utils/include/ipro_log.h`（デフォルト値は `ipro_log_config.h`）。`CONFIG_IPRO_LOG_ENABLE=y` が必要です。`ipro_platform_init()` がデフォルト設定で `ipro_log_init()` を呼び出します。

| API | 用途 |
|---|---|
| `IPRO_LOGE`、`IPRO_LOGW`、`IPRO_LOGI`、`IPRO_LOGD`、`IPRO_LOGV`（`tag, format, ...`） | エラー、警告、情報、デバッグ、詳細のメッセージ。`CONFIG_LOG_DEFAULT_LEVEL` より上のレベルの呼び出しは何も出力しません |
| `IPRO_LOG_BUFFER_HEX(tag, buf, len)`、`IPRO_LOG_BUFFER_HEXDUMP(tag, buf, len)` | バッファーを 16 進数（と ASCII）でダンプ |
| `ipro_log_set_level()`、`ipro_log_get_level()`、`ipro_log_level_enabled()` | 実行時にレベルを変更または取得 |
| `ipro_log_set_output_func()` | 出力先を独自の関数に変更 |

`CONFIG_LOG_DEFAULT_LEVEL` は整数です：1 エラー、2 警告、3 情報（同梱のアプリケーションが使用）、4 デバッグ、5 詳細。出力は `<level letter> (<time>) <TAG>: <message>` の形式です。

```c title="ログ（ファイルごとに 1 つの TAG）"
#include "ipro_log.h"

#define TAG "MY_MODULE"

IPRO_LOGI(TAG, "connected, handle %u", handle);
IPRO_LOGE(TAG, "init failed (err %d)", err);
```

## 関連ドキュメント { #related }

- [BLE 開発](../../guides/ble.md)：コントローラーの選択、起動順序、GATT のサンプル。
- [ビルドシステムと設定](../../guides/build-system.md)：`.config` とアプリケーションの構成。
- [デバッグとトラブルシューティング](../debugging.md)：ログ、クラッシュ出力、FreeRTOS フックのメッセージ。
- IPRO7 API 仕様書：[ドキュメント](../../documents/index.md) を参照してください。
