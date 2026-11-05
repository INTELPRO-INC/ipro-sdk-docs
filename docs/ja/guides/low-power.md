---
title: "低消費電力"
description: IPRO7 の FreeRTOS アプリケーションでの WFI、PDS、HBN — 低消費電力フレームワーク、設定、プログラミングインターフェース、保持と復帰、BLE とスリープ、Reef での IPRO7AI の電流測定
migrate_from: []
---

# 低消費電力

IPRO7 の FreeRTOS アプリケーションでは、3 つの省電力状態を使用できます。WFI（FreeRTOS の tickless idle）、PDS（Power-Down Sleep、Level 31。その場から再開）、HBN（Hibernate。コールドブートで復帰）です。SDK は、ビルド済みの低消費電力フレームワーク `hal_lp` による PDS への移行と復帰、および `ipro_pm` による WFI と PDS の自動選択を提供します。IPRO7AI Reef EVK では SW8 と JP2 を使って IPRO7AI 単体の電流を測定できますが、同梱の Reef 向け設定はいずれも PDS に入りません。

!!! abstract "要点"
    - フレームワーク：`bsp/hal/lp_framework/ipro7/`（`hal_lp.h`、ビルド済みの `liblp_framework.a`）と `hal_pm.h`。モードの自動選択は `components/sys/ipro_pm/`。
    - Reef：同梱の Reef 向け設定で PDS を使うものはありません。SW8 と JP2 で IPRO7AI の 3.3 V 電源に電流計を挿入できます。
    - 復帰：PDS は RTC タイマー、GPIO などで復帰します。コンソール UART では PDS から復帰できません。
    - 含まれないもの：BLE 接続中の PDS（コントローラーのソースビルドが必要）。Zephyr での低消費電力モード。

## 低消費電力モード { #modes }

| モード | 移行方法 | 保持されるもの | 復帰要因 | 復帰後 |
|---|---|---|---|---|
| WFI | FreeRTOS の tickless idle（`CONFIG_FREERTOS_USE_TICKLESS_IDLE`） | すべて | 任意の割り込み | その場から続行 |
| PDS（Level 31） | `hal_lp_enter()`、または低レベルの `pm_pds_mode_enter(PM_PDS_LEVEL_31, …)` | OCRAM（[保持と復帰](#retention-wake)を参照）、HBN RAM。オプションでセルフリフレッシュ状態の PSRAM | RTC タイマー、GPIO、アナログコンパレーター（ACOMP）、BLE | その場から続行。CPU、RF、MISC の各ドメインはリセットされるため、コンソール UART とシステムタイマーを再初期化する必要があります |
| HBN（Level 0） | `hal_lp_enter_fastboot()`、または低レベルの `pm_hbn_mode_enter(PM_HBN_LEVEL_0, …)` | HBN RAM（4 KB）と RTC のみ | RTC タイマー、AON ピン、BOR、ACOMP | ファームウェアの先頭からコールドブート。`hal_lp_is_fastboot_wakeup()` で判別します |

## アーキテクチャ { #architecture }

| レイヤー | 場所 | 役割 |
|---|---|---|
| アプリケーション | ユーザーのコード | いつスリープするか、何を保持するか、何で復帰するかを決めます |
| モードの自動選択 | `components/sys/ipro_pm/`（ソース） | FreeRTOS の tickless idle にフックし、アプリケーションが設定した範囲内で、アイドル期間ごとに WFI か PDS を選びます |
| 低消費電力フレームワーク | `bsp/hal/lp_framework/ipro7/`：`hal_lp.h`、`lp_uart.h`、`lib/liblp_framework.a`（ビルド済み。IPRO7 のビルドでは常にリンク） | RTC と GPIO による復帰、CPU 状態の保存と復元、Flash XIP と PSRAM の復旧、仮想時間、RC32K のキャリブレーション、ウェイクアップフック |
| 低レベルの電源管理 | `bsp/hal/inc/hal_pm.h` | `pm_pds_mode_enter()`、`pm_hbn_mode_enter()`、`pm_pds_gpio_wakeup_set()`、`pm_pds_set_misc_keep()`、32 kHz クロックソースの選択 |

## 設定 { #configuration }

```ini title="apps/test/ipro_lp_test/.config（抜粋）"
# CONFIG_USE_PSRAM is not set
CONFIG_HAL_LP=y
CONFIG_FREERTOS_IDLE_HOOK=y
CONFIG_PLATFORM_UART_BAUDRATE=115200
```

| キー | 説明 |
|---|---|
| `CONFIG_HAL_LP` | `hal_lp` を通じて PDS に入るアプリケーション（`ipro_lp_test`）が設定しています |
| `CONFIG_FREERTOS_IDLE_HOOK` | `vApplicationIdleHook()` を有効にします。アプリケーションはここでアイドル時に PDS に入れます |
| `CONFIG_FREERTOS_USE_TICKLESS_IDLE` | FreeRTOS の tickless idle。アイドル時に CPU が WFI に入ります |
| `CONFIG_IPRO_PM` | `ipro_pm` を有効にします。`CONFIG_FREERTOS_USE_TICKLESS_IDLE=1` と `CONFIG_FREERTOS_IDLE_HOOK=y` も必要で、ない場合はビルドが `#error` で停止します |
| `CONFIG_IPRO_PM_MAX_MODE` | 起動時に許可する最も深いモード：0 アクティブ、1 WFI（デフォルト）、2 ネイティブ、3 PDS。実行時には `ipro_pm_policy_set()` で変更します |
| `CONFIG_IPRO_PM_IDLE_PDS` | アイドルタスク自身が PDS に入ります（BLE コントローラーの動作中を除く）。`CONFIG_IPRO_PM_TIMEBASE=y` も設定します |
| `CONFIG_IPRO_PM_SHELL` | `pm` シェルコマンド（状態、ポリシー、`pm stats`） |

`.config` は書かれたとおりに `autoconf.h` に変換されます。Kconfig の依存関係は適用されないため、関連するキーはすべて明示的に書いてください。

!!! warning "HOTCODE オプションとは併用できません"
    `CONFIG_IPRO7_BLE_HOTCODE` と `CONFIG_IPRO7_WIFI_HOST_HOTCODE` は、低消費電力のレイアウト（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`、`CONFIG_OCRAM_NORET_SPLIT`）と併用できません。リンカースクリプトの生成がエラーで停止します。Reef では、`ipro7ai_reef_demo/defconfig_wifi_ipro6s` が Wi-Fi 用のオプションを、`ipro_throughput_test/defconfig_reef` が BLE 用のオプションを使用しています。

## テストアプリケーション ipro_lp_test { #lp-test }

`apps/test/ipro_lp_test` は、BLE も PSRAM も使わない最小構成のアプリケーションで、RTC による復帰を伴う PDS Level 31 をテストします。IPRO7 EVB 向けに設定されています（`CONFIG_EVB=y`）。`lp` シェルコマンドでこのページの各ケースを確認できます。`lp sleep <ms>`（`hal_lp` による PDS）、`lp auto on|off`（アイドル時の PDS）、`lp status`、`lp mem [ms]`（どの OCRAM が保持されるか）、`lp misc on|off`（MISC ドメインの電源を維持）、`lp fastboot <ms>`（コールドブートによる HBN からの復帰）、`lp wakectx` です。このページとあわせて `src/lp_test_cli.c` を読んでください。

## プログラミングインターフェース { #api }

次の流れは `apps/platform/ipro7_demo/demo/soc/peripheral/lowpower_demo.c` に沿っています。フレームワークを初期化し、ウェイクアップフックを登録して、RTC タイマーで PDS に入ります。

```c title="RTC タイマーで PDS に入る"
#include "hal_lp.h"

extern void shell_uart_reinit(void);
extern void vPortSetupTimerInterrupt(void);

static int wake_reinit(int wakeup_reason, void *arg)
{
    (void)wakeup_reason;
    (void)arg;
    shell_uart_reinit();          /* PDS でコンソール UART がリセットされている */
    vPortSetupTimerInterrupt();   /* FreeRTOS のシステムタイマー */
    /* その他の周辺機能（I2C、SPI など）はここで再初期化する */
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
        .psram_retention  = 1,     /* PSRAM がある場合はセルフリフレッシュで保持 */
        .ocram_retention  = 1,
    };
    hal_lp_result_t res;
    int ret = hal_lp_enter(&cfg, &res);   /* 復帰要因（HAL_LP_WAKEUP_*）または負のエラーコード */
    if (ret == HAL_LP_ERR_ENTRY_ABORTED) {
        /* 割り込みが保留中で、チップは PDS に入らなかった（WFI 1 回と同じ） */
    }
    return ret;
}
```

- `hal_lp_result_t` は、復帰要因、復帰のトリガーとなった GPIO、実際のスリープ時間を返します。`hal_lp_get_virtual_ms()` はスリープをまたいで継続する時間基準を提供します。
- GPIO による復帰：`hal_lp_cfg_t` の `gpio_wakeup_en` と `gpio_cfg`（`wakeup_mask`、トリガー、プル）を設定します。GPIO0～31 が使用できます。
- スリープ後に FreeRTOS のティックカウントは自動では補正されません。`ipro_lp_test` と同様に、`xTaskCatchUpTicks()` で実際のスリープ時間を加算してください。
- HBN：`hal_lp_enter_fastboot()` の後、チップはコールドブートで復帰するため、この呼び出しから戻ることはありません。起動時に `hal_lp_is_fastboot_wakeup()` を確認し、`hal_lp_get_wake_context()` で復帰コンテキストを読み出します。残す必要があるデータは、事前に HBN RAM に置いておく必要があります。

## 保持と復帰 { #retention-wake }

- **OCRAM**：MISC ドメインの電源を切った状態（デフォルト）では、PDS31 を通じて保持されるのは OCRAM の先頭 64 KB だけです。`pm_pds_set_misc_keep()` で MISC ドメインの電源を維持すると、OCRAM 全体が保持されます。復帰後に必要なデータは先頭 64 KB に置くか MISC を維持し、`ipro_lp_test` の `lp mem` で結果を確認してください。
- **PSRAM**：`psram_retention` により PDS 中は PSRAM がセルフリフレッシュ状態に保たれ、復帰時にフレームワークが PSRAM を復旧します。IPRO7AI（Reef の SoC）では PSRAM がパッケージに内蔵されており、PDS 中もセルフリフレッシュ状態を維持する必要があります。
- **HBN RAM**：4 KB。HBN を通じて保持される唯一のメモリです。フレームワークのパラメーターと fastboot の復帰コンテキストもここに置かれます。
- **コンソール**：UART0 は PDS31 でリセットされるドメインにあるため、復帰後に再初期化してください（`shell_uart_reinit()` または `platform_init()`）。コンソールの RX ピン（GPIO21、Reef では U6 の 4 番ピン）では PDS から復帰できず、スリープ中に入力した文字は失われます。
- **GPIO による復帰**：`hal_lp` は GPIO0～31 に対応します。低レベルの `pm_pds_gpio_wakeup_set()`（`hal_pm.h`）は GPIO0～41 を受け付けますが、ピンは 4 本単位でトリガー設定を共有し、使えるのは ASYNC トリガーだけです（SYNC トリガーには PDS で停止するクロックが必要です）。HBN からは AON ピンでのみ復帰します。
- **32 kHz クロック**：デフォルトは RC32K です。ボードに 32 kHz 水晶がある場合は `pm_pds_set_32k_src()` で切り替えます。Reef には水晶がなく RC32K で動作します。フレームワークには RC32K のキャリブレーションが含まれています。
- **Flash**：`flash_power_down = 1` にするとスリープ中は Flash の電源が切られ、復帰時にフレームワークが XIP を復旧します。

## BLE とスリープ { #ble-sleep }

- `ipro_pm` の BLE バックエンドと BLE 接続中の PDS（`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`）には、BLE コントローラーのソースビルドが必須です。コントローラーはビルド済みライブラリとしてのみ提供されるため、これらはパッケージからはビルドできません。BLE 接続中の低消費電力が必要な製品については、INTELPRO にお問い合わせください。
- `ipro_ble_remote/defconfig_reef` は意図的に PDS を使わずに動作します。Reef は USB 給電で、カメラとオーディオにはクロックが必要なためです。
- `ipro_pdm_mic_demo`（IPRO7 EVB、IPRO7AI EVK）は、tickless WFI と手動の `pds [sec]` コマンドを使った BLE の例です。
- BLE コントローラーのバリアント、Exchange Memory のサイズなどの BLE の設定については、[BLE 開発](ble.md)を参照してください。

## 測定 { #measure }

- 外部の測定器を使い、SoC の電源経路で測定します。Reef では SW8 と JP2 で IPRO7AI の 3.3 V を測定器に通します（手順は後述）。その他のボードについては[電源と消費電流の測定](../hardware/power.md)を参照してください。
- チップが実際にどのくらいの頻度で、どのくらいの時間スリープしているかを確認し、復帰要因（`hal_lp_result_t`）をログに残します。想定より頻繁に復帰する場合は、まずタイマーと保留中の割り込みを調べます（`hal_lp_enter()` が `HAL_LP_ERR_ENTRY_ABORTED` を返します）。
- `ipro_pm` を使う場合、`pm stats` で各モードの滞在時間と推定電流を一覧表示できます。この推定値は設定どうしの比較用であり、実測の代わりにはなりません。
- 同じファームウェアを WFI と PDS で比較し、UART の出力が途中で切れないよう、出力が終わってからスリープに入るようにします。

## Reef でのハンズオン { #hands-on }

ファームウェアの動作中に IPRO7AI が消費する電流を測定します。同梱の Reef 向け設定はいずれも PDS に入らないため、この手順では出荷時ファームウェアを使い、アイドル状態のシェルとカメラパイプライン動作中とを比較します。独自のアプリケーションでも同じ手順を繰り返すと、スリープを追加する前のベースラインを得られます。

3 ピンの JP2 ヘッダーにつなぐリード線付きの電流計（またはソースメジャーユニット）が必要です。

<div class="ipro-steps" markdown>

1. **設定**

    追加するものはありません。`apps/platform/ipro7ai_reef_demo/.config` は低消費電力のキーを設定していない（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM` がない）ため、CPU はアイドルになるだけです。

2. **ビルドと書き込み**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    ダウンロードモード（SW1 を押したまま SW2 を押して離し、SW1 を離す）で、IntelProCube のディレクトリから次を実行します。

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    詳しくは[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)を参照してください。

3. **電源に測定器を入れる**

    USB-C を抜きます。JP2 の 1 番ピン（3V3）と 2 番ピン（SOC）の間に電流計を接続し、SW8 を **MEAS** に切り替えてから、USB-C を接続し直します。測定値は IPRO7AI の 3.3 V ピンだけのもので、カメラ、LED、アンプ、microSD ソケットは含みません。

4. **アイドル電流を読む**

    115200 baud でコンソールを開きます。電源投入時にデモはカメラをパーク状態にします。`ipro />` プロンプトが入力待ちの状態で、測定器の値を記録します。

5. **カメラパイプラインを動かして比較する**

    ```text
    cam start
    cam stop
    cam park
    ```

    コンソールには ``streaming - `cam status` in a second``、`stopped`、`PWDN high, RESETB low, XCLK off` の順に応答が表示されます。ストリームの動作中と `cam park` の後でそれぞれ値を記録します。その差が、カメラパイプライン（XCLK、DVP 入力、ISP）による SoC の消費電流です。

6. **ボードを元に戻す**

    USB-C を抜き、SW8 を **PWR** に戻してから、測定器を外します。SW8 が MEAS のまま JP2 に何も接続されていないと、IPRO7AI には電源が供給されず、周辺回路から I/O ピンを通じて逆給電される状態になります。

</div>

次のステップ：[最初の独自アプリケーションを作る](../tutorials/first-own-app.md)で独自のアプリケーションを作成し、[アプリケーションのテスト](../tutorials/testing.md)でその動作と電流を確認します。

## 本リリースの制限事項 { #limitations }

- 同梱の IPRO7AI Reef EVK 向け設定で PDS や HBN に入るものはありません。`ipro_lp_test` と `ipro7_demo` の低消費電力コマンドは IPRO7 EVB 向けです。
- BLE 接続中の PDS はパッケージからビルドできません（コントローラーのソースビルドが必要）。
- Zephyr RTOS では低消費電力モードを使用できません（`pm_state` は PDS にも HBN にも入りません）。[Zephyr RTOS](zephyr.md) を参照してください。
- `CONFIG_IPRO_PM_IDLE_PDS`（アイドルタスクによる PDS への移行）には同梱のサンプルがありません。使用する前にご使用のボードで検証してください。
- 低消費電力のメモリレイアウトは HOTCODE オプションと併用できません。

## 関連ドキュメント { #related }

- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：SW8、JP2 と電流測定の手順。
- [電源と消費電流の測定](../hardware/power.md)
- [BLE 開発](ble.md)
- [ビルドシステムと設定](build-system.md)
- [Zephyr RTOS](zephyr.md)
