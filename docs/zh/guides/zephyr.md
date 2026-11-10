---
title: "Zephyr RTOS"
description: IPRO SDK 作為 Zephyr v4.4.0 模組：支援板卡、工作區、以 west 建置與燒錄、範例、預編譯元件，以及本版 Zephyr 尚未涵蓋的功能
migrate_from:
  - "zephyr-rtos.html#overview"
  - "zephyr-rtos.html#boards"
  - "zephyr-rtos.html#features"
  - "zephyr-rtos.html#samples"
  - "zephyr-rtos.html#prebuilt"
  - "zephyr-rtos.html#limitations"
  - "getting-started.html#zephyr-quickstart"
  - "zephyr-rtos.html#setup"
  - "zephyr-rtos.html#build-flash"
---

# Zephyr RTOS

IPRO SDK 同時是一個 Zephyr v4.4.0 模組：SDK 的 HAL 與 SoC 驅動透過 Zephyr 的裝置驅動 API 提供，可以改用 Zephyr 而非 FreeRTOS 開發應用。本頁是 Zephyr 端的參考：支援板卡、工作區、`west` 建置與燒錄、範例與限制。FreeRTOS 應用與其建置方式不受影響。

!!! abstract "重點"
    - 板卡：`ipro7_evb`（IPRO7 EVB）與 `ipro7ai_evk`（IPRO7AI EVK）。**V2.2.1 沒有 IPRO7AI Reef EVK 的 Zephyr 板卡定義**；在 Reef 上請使用 FreeRTOS 應用。
    - 可用：常用周邊驅動、BLE（Zephyr host 搭配預編譯的 IPRO BLE 控制器）、IEEE 802.15.4 與 OpenThread、MCUboot 搭配 MCUmgr 經 BLE 更新。
    - 不可用：低功耗模式，以及相機、音訊編解碼器、USB、SD host、乙太網路與 NPU 的 Zephyr 驅動。
    - 主控台：UART0，2,000,000 baud。主機需要：含 venv 的 Python 3、git、可連上 GitHub 的網路、CMake 3.20 以上。
    - 第一次建置：先看[工作區](#workspace)，再看[建置、燒錄與主控台](#flash-console)。

## 概覽 { #overview }

| 檔案／目錄 | 作用 |
|---|---|
| `west.yml` | SDK 本身是 west manifest repository：固定 Zephyr v4.4.0，只匯入允許清單中的模組 |
| `zephyr/module.yml` | 把 SDK 註冊為 Zephyr 模組，帶入板卡、SoC、devicetree binding 與 `west flash` runner |
| `zephyr/boards/`、`soc/`、`dts/` | 板卡定義、SoC 定義、devicetree binding |
| `zephyr/drivers/`、`hal_glue/`、`include/` | Zephyr 驅動，以及與 SDK HAL 的介接 |
| `zephyr/patches.yml`、`patches/` | SDK 對 Zephyr 的兩個修補，建立工作區時套用 |
| `zephyr/samples/`、`zephyr/tests/` | SDK 範例與測試 |
| `tools/zephyr/` | 建立工作區、建置、燒錄與開啟主控台的腳本 |

Zephyr 驅動呼叫 SDK 的 HAL，HAL 直接從 `bsp/` 編譯。BLE 使用 Zephyr 的 host 搭配 IPRO BLE 控制器函式庫；IEEE 802.15.4 使用 Zephyr 的驅動介面與 OpenThread。

## 支援板卡 { #boards }

| Zephyr 板卡 | 硬體 | Flash（devicetree） | PSRAM | `west flash` 預設 |
|---|---|---|---|---|
| `ipro7_evb` | IPRO7 EVB | 2 MB | 無 | `--pt=partition_cfg_2M.toml`，經 IPRO7 CMSIS-DAP 探針進入下載模式 |
| `ipro7ai_evk` | IPRO7AI EVK | 1 MB | 8 MB | `--pt=partition_cfg_1M_boot2.toml`、`--boot=shell` |

- 兩塊板子的主控台都在 UART0，2,000,000 baud。
- 分割表名稱指的是 IntelProCube 的 `chips/ipro7/partition/` 下的檔案。
- SDK 附有 `ipro6s_evb` 的板卡檔案，但本版 Zephyr 不支援 IPRO6S。

!!! info "IPRO7AI Reef EVK"
    V2.2.1 沒有 Reef 的 Zephyr 板卡，Reef 的相機、音訊、LED 與 microSD 插槽也沒有 devicetree 描述。本版未驗證在 Reef 上執行 Zephyr 映像。需要在 Reef 上使用 Zephyr 時請洽 INTELPRO。

## 工作區 { #workspace }

`tools/zephyr/bootstrap.sh` 在 SDK 根目錄建立 `zephyr-workspace/`。第一次執行會從 GitHub 下載 Zephyr 與模組。

```bash
tools/zephyr/bootstrap.sh              # 建立 zephyr-workspace/
source zephyr-workspace/env.sh         # 設定 ZEPHYR_BASE、CROSS_COMPILE，並把 west 加入 PATH
```

腳本依序：

1. 建立 `zephyr-workspace/.venv` 並安裝 west。
2. 以 SDK 的 `west.yml` 初始化 west，執行 `west update`（預設淺層下載）。
3. 套用 `zephyr/patches.yml` 中的修補。
4. 安裝 Zephyr 與 MCUboot 需要的 Python 套件。
5. 寫出 `env.sh`：`ZEPHYR_TOOLCHAIN_VARIANT=cross-compile`、`CROSS_COMPILE`、`ZEPHYR_BASE`、`PATH`。

| 選項／變數 | 說明 |
|---|---|
| `-w DIR` | 改用其他工作區目錄 |
| `--full` | 下載 Zephyr 與模組的完整歷史 |
| `IPRO_TOOLCHAIN` | 工具鏈目錄，預設 `/opt/toolchain/riscv_ipro7` |

`west.yml` 只匯入 `mbedtls`、`tf-psa-crypto`、`openthread`、`picolibc`、`segger`、`mcuboot`、`liblc3` 與 `zcbor`。

!!! warning "再次執行 bootstrap"
    更新前，bootstrap 會把修補涉及的 Zephyr 檔案還原成固定版本，對這些檔案的本機修改會遺失。

Zephyr 需要 CMake 3.20 以上。`tools/cmake/` 內附的是 Linux x86-64 用的 CMake 3.15，只供 FreeRTOS 建置使用。

## 建置、燒錄與主控台 { #flash-console }

先 `source env.sh`，再在 `zephyr-workspace/` 執行：

```bash
west build -b ipro7_evb zephyr/samples/hello_world                       # Zephyr 本身的範例
west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke     # SDK 的範例
west flash -d build/smoke
../tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX                  # 主控台，2,000,000 baud
```

在 SDK 根目錄，`tools/zephyr/build.sh [-b ipro7_evb|ipro7ai_evk] [-d DIR] [-p] APP [-- cmake 參數]` 包裝了 `west build`，SDK 範例可直接寫名稱（`tools/zephyr/build.sh -b ipro7ai_evk periph_smoke`）。

`west flash` 使用 SDK 的 `ipro` runner（`zephyr/scripts/runners/ipro.py`）：讓板子進入下載模式，以 IntelProCube 命令列工具寫入 `zephyr.bin`，再重置板子。

| Runner 選項 | 說明 |
|---|---|
| `--boot probe`／`shell`／`manual` | 進入下載模式的方式：IPRO7 CMSIS-DAP 探針（預設）、執行中映像的 `reboot_dl`，或手動 |
| `--port`、`--probe-port` | 燒錄 UART 與探針橋接埠；預設 `$IPRO_SERIAL_PORT`、`$IPRO_PROBE_PORT` |
| `--tool` | IntelProCube CLI 執行檔；預設 `$IPRO_FLASH_TOOL`，或 `PATH` 上的工具 |
| `--pt` | 分割表：`.toml` 路徑，或工具 `chips/<chip>/partition/` 下的表名 |
| `--baudrate`、`--console-baud` | 燒錄速率，以及 `--boot shell` 使用的主控台速率；預設都是 2000000 |
| `--no-reset`、`--attempts`、`--tool-arg` | 燒錄後停在下載模式；重試次數（3）；傳給工具的額外參數 |

Runner 選項寫在 `--` 之後，例如 `west flash -- --boot shell --port /dev/cu.usbserial-XXXX`。

- `west flash` 不傳 `--chip-variant`；IntelProCube 使用存在 `chips/ipro7/eflash_loader/eflash_loader_cfg.ini` 的 flash 腳位設定。
- 含 MCUboot 的 sysbuild 映像，`west flash` 會先以 `tools/zephyr/merge_mcuboot.py` 把 MCUboot 與簽章後的應用合併成一個映像。
- `tools/zephyr/flash.sh` 以 115200 baud 送出 `reboot_dl`，執行中的 Zephyr 映像（2,000,000 baud）收不到；請先手動進入下載模式，或改用 `west flash`。

## 功能範圍 { #features }

| 項目 | Zephyr 下 |
|---|---|
| 驅動 | GPIO、UART（含 async）、SPI、I2C、PWM、ADC、DAC、counter／RTC、watchdog、flash、DMA、entropy、hwinfo、I2S／PDM |
| 顯示 | IPRO7AI EVK 的 LCD，使用 Zephyr 本身的 ST7789V 驅動 |
| Bluetooth LE | Zephyr host 搭配 `components/wireless/bluetooth/ipro_ble_controller/lib/` 的 IPRO BLE 控制器函式庫 |
| IEEE 802.15.4／Thread | Zephyr 的 IEEE 802.15.4 驅動與 OpenThread，見 [Thread 與 Matter](thread-matter.md) |
| 開機與更新 | 經 sysbuild 的 MCUboot；以 MCUmgr SMP 經 BLE 上傳映像，見 [OTA 更新](ota.md) |

Zephyr 下以下列設定選擇 BLE 控制器函式庫，並以 devicetree overlay 啟用 `bt_hci` 節點（`zephyr/samples/bt_peripheral_hr/ipro7.overlay`）：

```ini title="zephyr/samples/bt_peripheral_hr/ipro7.conf（節錄）"
CONFIG_IPRO7_EM_SIZE_KB=16
CONFIG_BT_IPRO_CTLR_LIB="link1_periph"
CONFIG_BT_IPRO_CTLR_FEATURE="bt52"
CONFIG_BT_MAX_CONN=1
CONFIG_ENTROPY_GENERATOR=y
```

ISO 與 LE Audio 改用 `zephyr/samples/bt_le_audio/iso.conf`（`link1`、`bt54_iso2`、`CONFIG_IPRO7_EM_SIZE_KB=32`）。函式庫組合見 [BLE 開發](ble.md)。

## 範例 { #samples }

| 範例（`zephyr/samples/`） | 板卡 | 內容 |
|---|---|---|
| `periph_smoke` | `ipro7_evb` | 逐一測試驅動：GPIO、UART、SPI、I2C、PWM、flash、DMA、counter、watchdog、TRNG |
| `mcuboot_app` | `ipro7_evb`、`ipro7ai_evk` | 驗證 boot2 → MCUboot → 映像的開機鏈 |
| `ble_ota` | `ipro7_evb`、`ipro7ai_evk` | MCUboot＋MCUmgr SMP，經 BLE 更新 |
| `bap_broadcast_source` | `ipro7_evb`、`ipro7ai_evk` | LE Audio 廣播來源（LC3） |
| `bap_broadcast_sink` | `ipro7ai_evk` | LE Audio 廣播接收，從 EVK 喇叭播放 |
| `le_audio_headset` | `ipro7ai_evk` | LE Audio unicast 耳機（CAP acceptor） |
| `evk_demo` | `ipro7ai_evk` | EVK 的 LCD、麥克風、喇叭與相機預覽的 `evk` shell 指令 |
| `ieee802154_shell` | `ipro7_evb` | IEEE 802.15.4 shell；另附 OpenThread 用的 `ot.conf` 與 `csl.conf` |
| `bt_peripheral_hr`、`bt_le_audio` | – | 給 Zephyr 本身範例使用的設定片段 |

Zephyr 本身的範例搭配 SDK 的設定片段（在 `zephyr-workspace/` 執行）：

```bash
west build -b ipro7_evb zephyr/samples/bluetooth/peripheral_hr -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.overlay
west build -b ipro7_evb zephyr/samples/net/openthread/shell -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/ieee802154_shell/ot.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/ieee802154_shell/app.overlay
```

`zephyr/tests/` 有 15 組驅動測試（`zephyr/tests/drivers/`）與 3 組 SoC 測試（`camclk`、`psram`、`reboot`），都是標準的 ztest。

## 預編譯元件 { #prebuilt }

Zephyr 建置時，除下列元件外，包括 HAL 在內的 SDK 程式碼都從原始碼編譯：

| 元件 | 位置 |
|---|---|
| IPRO BLE 控制器 | `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| RF 驅動 | `components/wireless/rf/ipro7_rf/lib/zephyr/`（`libipro_rf_core.a`、`libipro_rf_core_short_enums.a`） |
| IEEE 802.15.4 MAC | `components/wireless/ieee802154/lib/zephyr/`（`libipro_ieee802154_core.a`、`libipro_ieee802154_core_short_enums.a`） |

連結 BLE 控制器時，整個映像以 `-fshort-enums` 編譯，建置會自動選用對應的 RF 與 802.15.4 函式庫版本。

## 本版限制 { #limitations }

- 沒有 IPRO7AI Reef EVK 的 Zephyr 板卡；Zephyr 不支援 IPRO6S。
- 低功耗模式：Zephyr 的 `pm_state` 不會進入 PDS 或 HBN，BLE 控制器也不會睡眠。需要低功耗請用 FreeRTOS，見[低功耗](low-power.md)。
- 沒有相機、音訊編解碼器、USB、SD host、乙太網路與 NPU 的 Zephyr 驅動；唯一的顯示是 IPRO7AI EVK 的 LCD。
- Zephyr 下 IPRO7 沒有 Wi-Fi：`zephyr/drivers/wifi` 是 IPRO6S 晶片本身的驅動。
- 需要上述功能的產品請使用 FreeRTOS 應用。

## 相關文件 { #related }

- [Thread 與 Matter](thread-matter.md)：OpenThread 設定與第一次測試。
- [OTA 更新](ota.md)：MCUboot 與 MCUmgr。
- [BLE 開發](ble.md)：控制器函式庫與 BLE API。
- [工具命令列](../reference/tools.md)：`tools/zephyr/` 腳本。
