---
title: "Zephyr RTOS"
description: IPRO SDK 作為 Zephyr v4.4.0 模組：支援板卡、工作區、燒錄與主控台、功能範圍、範例、預編譯元件與本版限制
migrate_from:
  - "zephyr-rtos.html#overview"
  - "zephyr-rtos.html#boards"
  - "zephyr-rtos.html#features"
  - "zephyr-rtos.html#samples"
  - "zephyr-rtos.html#prebuilt"
  - "zephyr-rtos.html#limitations"
---

# Zephyr RTOS

<span class="ipro-badge">V2.1.0 新增</span>

IPRO SDK 同時是一個 Zephyr v4.4.0 模組：SDK 的 HAL 與 SoC 驅動以 Zephyr 的裝置驅動 API 提供，應用可以直接用 Zephyr 開發。FreeRTOS 應用與其建置流程不受影響；低功耗、相機、USB、NPU 等功能目前只有 FreeRTOS 應用支援，選擇前請先看[本版限制](#limitations)。

!!! abstract "重點"
    - 板卡：`ipro7_evb`（IPRO7 EVB）、`ipro7ai_evk`（IPRO7AI EVK）。IPRO7AI Reef EVK 沒有 Zephyr 板級定義。
    - 支援：常用周邊驅動、BLE（Zephyr Host＋IPRO BLE 控制器預編譯函式庫）、IEEE 802.15.4 與 OpenThread、MCUboot 與經 BLE 的 MCUmgr 更新。
    - 未支援：低功耗模式，以及相機、音訊 codec、USB、SD host、Ethernet、NPU 的 Zephyr 驅動。
    - 主控台：UART0，2000000 baud。
    - 第一次建置的步驟見[第一個 Zephyr 應用](../get-started/first-app-zephyr.md)。

## 概覽 { #overview }

| 檔案／目錄 | 作用 |
|---|---|
| `west.yml` | SDK 是 west 的 manifest repository：固定 Zephyr v4.4.0，只匯入允許清單上的模組 |
| `zephyr/module.yml` | 把 SDK 註冊為 Zephyr 模組（名稱 `ipro_sdk`），提供板卡、SoC、devicetree 與 `west flash` runner |
| `zephyr/boards/`、`soc/`、`dts/` | 板級定義、SoC 定義與 devicetree binding |
| `zephyr/drivers/`、`hal_glue/`、`include/` | Zephyr 驅動與接到 SDK HAL 的介接層 |
| `zephyr/patches.yml`、`patches/` | SDK 對 Zephyr 的 2 個修補，建立工作區時套用 |
| `zephyr/samples/`、`zephyr/tests/` | SDK 範例與測試 |
| `tools/zephyr/` | 工作區建立、建置、燒錄與主控台腳本 |

Zephyr 驅動建立在 SDK 的 HAL 之上，HAL 直接從 `bsp/` 編譯，不另外複製。BLE 使用 Zephyr 的 Host 搭配 IPRO BLE 控制器（預編譯函式庫）；IEEE 802.15.4 使用 Zephyr 的驅動介面與 OpenThread。

## 支援板卡 { #boards }

| Zephyr board | 硬體 | Flash（devicetree） | PSRAM | `west flash` 預設 |
|---|---|---|---|---|
| `ipro7_evb` | IPRO7 EVB | 2 MB | 無 | `--pt=partition_cfg_2M.toml`，經 CMSIS-DAP probe 進入下載模式 |
| `ipro7ai_evk` | IPRO7AI EVK | 1 MB | 8 MB | `--pt=partition_cfg_1M_boot2.toml`，`--boot shell` |

- 兩塊板子的主控台都在 UART0，2000000 baud。IPRO7AI EVK 的 LCD 透過 Zephyr 內建的 ST7789V 驅動使用。
- 分割表名稱是 IntelProCube 內 `chips/ipro7/partition/` 下的檔案。
- `ipro6s_evb` 的板卡檔案隨附於 SDK，但本版的 Zephyr 不支援 IPRO6S。IPRO6S 見 [IPRO6S（V2.0.1）](../hardware/chips/ipro6s.md)。

!!! note "IPRO7AI Reef EVK"
    本版沒有 Reef 的 Zephyr 板級定義，Reef 的相機、音訊與 LED 都沒有 devicetree 描述，建議使用 FreeRTOS 應用。SoC 的 Kconfig 說明提到 Reef 可執行 `ipro7_evb` 映像，此時要設定 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`（Reef 的 RF 晶體微調值）；`ipro7_evb` 的 devicetree 以 2 MB Flash、無 PSRAM 描述板子，使用前請確認與手上的 Reef 相符。

## 工作區 { #workspace }

`tools/zephyr/bootstrap.sh` 在 SDK 根目錄下建立 `zephyr-workspace/`，第一次執行需要連上 GitHub。逐步操作見[第一個 Zephyr 應用](../get-started/first-app-zephyr.md)。

```bash
tools/zephyr/bootstrap.sh              # 建立 zephyr-workspace/
source zephyr-workspace/env.sh         # ZEPHYR_BASE、CROSS_COMPILE、west
```

bootstrap 依序：

1. 建立 `.venv` 並安裝 west。
2. 以 SDK 的 `west.yml` 初始化 west，執行 `west update`（預設淺層下載；`--full` 改為完整下載）。
3. 以 `west patch apply` 套用 `zephyr/patches.yml` 的修補。
4. 安裝 Zephyr 與 MCUboot（imgtool）的 Python 套件。
5. 產生 `env.sh`：`ZEPHYR_TOOLCHAIN_VARIANT=cross-compile`、`CROSS_COMPILE`、`ZEPHYR_BASE`、`PATH`。

| 選項／環境變數 | 說明 |
|---|---|
| `-w DIR` | 改用其他工作區目錄 |
| `--full` | 完整下載 Zephyr 與模組（預設為淺層） |
| `IPRO_TOOLCHAIN` | 工具鏈目錄，預設 `/opt/toolchain/riscv_ipro7` |

`west.yml` 只匯入下列模組：`mbedtls`、`tf-psa-crypto`、`openthread`、`picolibc`、`segger`、`mcuboot`、`liblc3`、`zcbor`。

!!! warning "重新執行 bootstrap"
    重新執行前，bootstrap 會把修補動過的 Zephyr 檔案還原成固定版本，這些檔案的本地修改會被丟棄。

SDK 範例與測試需要 CMake 3.20 以上。SDK 隨附的 `tools/cmake/` 是 3.15 版的 Linux x86-64 執行檔，不能用於 Zephyr。

## 燒錄與主控台 { #flash-console }

```bash
cd zephyr-workspace
west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke
west flash -d build/smoke
```

`west flash` 使用 SDK 的 `ipro` runner，以 IntelProCube 命令列工具寫入映像（燒錄鮑率 2000000）。進入下載模式的方式由 `--boot` 決定：`probe`（IPRO7 CMSIS-DAP probe，`ipro7_evb` 的預設）、`shell`（由執行中韌體送出 `reboot_dl`，`ipro7ai_evk` 的預設）或 `manual`（手動按住 BOOT 再重置）。例如沒有 probe 時：`west flash -- --boot shell --port /dev/cu.usbserial-XXXX`。

- Flash 腳位設定取自 IntelProCube 的設定檔，`west flash` 不會傳 `--chip-variant`；設定方式見[燒錄與序列埠](../get-started/flash-and-monitor.md#flash-tool)。
- 以 sysbuild 建置的 MCUboot 映像，`west flash` 會先以 `tools/zephyr/merge_mcuboot.py` 把 MCUboot 與已簽章的應用合併成一個 FW 映像再燒錄。
- 主控台為 UART0、2000000 baud：`tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX`。
- `tools/zephyr/flash.sh` 以 115200 baud 送出 `reboot_dl`，執行中的 Zephyr 映像收不到；請先手動進入下載模式，或改用 `west flash`。

`west flash` 的全部選項與 `tools/zephyr/` 各腳本的用法見[工具命令列](../reference/tools.md#zephyr-tools)。

## 功能範圍 { #features }

| 項目 | Zephyr 下的支援 |
|---|---|
| 驅動 | GPIO、UART（含 async）、SPI、I2C、PWM、ADC、DAC、counter／RTC、watchdog、flash、DMA、entropy、hwinfo、I2S／PDM |
| 顯示 | IPRO7AI EVK 的 LCD（Zephyr 內建 ST7789V 驅動） |
| Bluetooth LE | Zephyr Host 搭配 IPRO BLE 控制器（預編譯函式庫，與 FreeRTOS 共用 `components/wireless/bluetooth/ipro_ble_controller/lib/`） |
| IEEE 802.15.4／Thread | Zephyr 的 IEEE 802.15.4 驅動與 OpenThread，見 [Thread 與 Matter](thread-matter.md) |
| 開機與更新 | 透過 sysbuild 使用 MCUboot；以 MCUmgr SMP 經 BLE 上傳映像，見 [OTA 更新](ota.md) |

Zephyr 下的 BLE 控制器以下列設定選擇，devicetree overlay 需啟用 `bt_hci` 節點（`zephyr/samples/bt_peripheral_hr/ipro7.overlay`）：

```ini title="zephyr/samples/bt_peripheral_hr/ipro7.conf"
CONFIG_IPRO7_EM_SIZE_KB=16
CONFIG_BT_IPRO_CTLR_LIB="link1_periph"
CONFIG_BT_IPRO_CTLR_FEATURE="bt52"
CONFIG_BT_MAX_CONN=1
CONFIG_ENTROPY_GENERATOR=y
```

ISO／LE Audio 使用 `zephyr/samples/bt_le_audio/iso.conf`（`link1`、`bt54_iso2`、`CONFIG_IPRO7_EM_SIZE_KB=32`）。控制器配置的說明見 [BLE 開發](ble.md)。

## 範例 { #samples }

| 範例（`zephyr/samples/`） | 板卡 | 內容 |
|---|---|---|
| `periph_smoke` | `ipro7_evb` | 逐一操作各驅動（GPIO、UART、SPI、I2C、PWM、flash、DMA、counter、watchdog、TRNG） |
| `mcuboot_app` | `ipro7_evb`、`ipro7ai_evk` | 驗證 boot2 → MCUboot → image-0 開機鏈 |
| `ble_ota` | `ipro7_evb`、`ipro7ai_evk` | MCUboot＋MCUmgr SMP，經 BLE 更新 |
| `bap_broadcast_source` | `ipro7_evb`、`ipro7ai_evk` | LE Audio 廣播來源（LC3） |
| `bap_broadcast_sink` | `ipro7ai_evk` | LE Audio 廣播接收，輸出到 EVK 喇叭 |
| `le_audio_headset` | `ipro7ai_evk` | LE Audio unicast 耳機（CAP acceptor） |
| `evk_demo` | `ipro7ai_evk` | `evk` shell 指令：LCD、麥克風、喇叭；相機預覽需 `CONFIG_EVK_DEMO_CAMERA=y` |
| `ieee802154_shell` | `ipro7_evb` | IEEE 802.15.4 shell；另附 OpenThread 用的 `ot.conf`、`csl.conf` |
| `bt_peripheral_hr`、`bt_le_audio` | – | 給 Zephyr 內建範例使用的設定片段 |

Zephyr 內建範例搭配 SDK 設定片段（在 `zephyr-workspace/` 執行）：

```bash
west build -b ipro7_evb zephyr/samples/bluetooth/peripheral_hr -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.overlay
west build -b ipro7_evb zephyr/samples/net/openthread/shell -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/ieee802154_shell/ot.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/ieee802154_shell/app.overlay
```

`zephyr/tests/` 有 15 組驅動測試（`zephyr/tests/drivers/`）與 3 組 SoC 測試（`camclk`、`psram`、`reboot`），為 Zephyr 標準的 ztest 測試。

## 預編譯元件 { #prebuilt }

Zephyr 建置時，除了下列元件，所有 SDK 程式（包含 HAL）都從原始碼編譯：

| 元件 | 位置 |
|---|---|
| IPRO BLE 控制器 | `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| RF 驅動 | `components/wireless/rf/ipro7_rf/lib/zephyr/`（`libipro_rf_core.a`、`libipro_rf_core_short_enums.a`） |
| IEEE 802.15.4 MAC | `components/wireless/ieee802154/lib/zephyr/`（`libipro_ieee802154_core.a`、`libipro_ieee802154_core_short_enums.a`） |

連結 BLE 控制器時，整個映像以 `-fshort-enums` 編譯；建置系統會自動選用相符的 RF 與 802.15.4 函式庫版本。

## 本版限制 { #limitations }

- 低功耗模式：不會透過 Zephyr 的 `pm_state` 進入 PDS／HBN，BLE 控制器也不會進入睡眠。需要低功耗請使用 FreeRTOS，見[低功耗](low-power.md)。
- 沒有相機、音訊 codec、USB、SD host、Ethernet 與 NPU 的 Zephyr 驅動；顯示只有 IPRO7AI EVK 的 LCD（ST7789V）。`evk_demo` 的相機預覽在範例內直接使用 SDK HAL。
- IPRO7 在 Zephyr 下沒有 Wi-Fi；`zephyr/drivers/wifi` 是 IPRO6S 用的驅動，本版不支援。
- 沒有 IPRO7AI Reef EVK 板級定義；不支援 IPRO6S。
- 以上功能請使用 FreeRTOS 應用。

## 相關文件 { #related }

- [第一個 Zephyr 應用](../get-started/first-app-zephyr.md)：建立工作區、建置與燒錄的步驟。
- [Thread 與 Matter](thread-matter.md)：OpenThread 設定與試用。
- [OTA 更新](ota.md)：MCUboot 與 MCUmgr。
- [BLE 開發](ble.md)：控制器配置與 BLE API。
