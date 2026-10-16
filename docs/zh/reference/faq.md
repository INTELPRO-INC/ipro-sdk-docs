---
title: "常見問題"
description: 建置、燒錄與主控台、BLE、平台與連網、除錯的常見問題與簡答，並連到詳細說明的頁面。
migrate_from:
  - "faq.html"
---

# 常見問題

每題先給結論，細節連到對應頁面。錯誤訊息的對照表見 [除錯與疑難排解](debugging.md#troubleshooting)。

## 建置 { #build }

### 燒錄工具與工具鏈從哪裡取得？ { #get-tools }

兩者都未包含於 V2.1.0，請洽 INTELPRO：

- RISC-V 工具鏈，預設安裝於 `/opt/toolchain/riscv_ipro7/`。
- IntelProCube v0.6.3 的命令列燒錄工具：`ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`。

SDK 本身可由 [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0) 下載。

### build_freertos.sh 與 make -C 有什麼不同？ { #build-cli-vs-make }

`make -C apps/<分類>/<應用>` 以應用的 `.config` 建置單一應用，必須寫完整路徑。`build_freertos.sh` 在 `make` 之外加上 `clean`、`flash`、`monitor`、`size` 與 `test` 動作，可只寫應用名稱並串接多個動作：

```bash
make -C apps/platform/ipro7ai_reef_demo
./build_freertos.sh clean build ipro7ai_reef_demo
```

兩者產出相同，都在 `<應用>/build/build_out/`。`build_freertos.sh` 的 `flash` 與 `monitor` 有固定的鮑率與參數，Reef 等 IPRO7AI 板子請直接用 IntelProCube 工具燒錄，見[燒錄與序列埠](../get-started/flash-and-monitor.md#build-script)。

### 改了 .config，相依的設定卻沒有生效？ { #kconfig }

建置照原樣讀取 `.config`，由 `cmake/generate_autoconf.cmake` 產生 `autoconf.h`。Kconfig 檔只是說明，`select`、`depends on` 與預設值都不會自動套用，相依設定必須自己寫進 `.config`。例如啟用 `CONFIG_AI_SUPPORT=y` 時，也要寫入 `CONFIG_USE_PSRAM=y`。

套件中的 Kconfig 樹引用了未隨附的元件，`menuconfig` 無法使用，請直接編輯 `.config`。詳見 [建置系統與設定](../guides/build-system.md)。

### 找不到工具鏈，或工具鏈不在預設路徑？ { #toolchain }

每個 `.config` 都以 `CONFIG_CROSS_COMPILE` 指向 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-`。工具鏈放在其他位置時，在環境中設定 `CROSS_COMPILE`，它會優先於 `.config`：

```bash
export CROSS_COMPILE=<工具鏈路徑>/bin/riscv64-unknown-elf-
make -C apps/platform/ipro7ai_reef_demo
```

`.config` 中的 `CONFIG_CPU_ID="intelpro_ipro7"` 請保留，建置依它選擇編譯旗標。`build_freertos.sh size` 固定使用預設路徑的 `size`；Zephyr 工作區則由 `IPRO_TOOLCHAIN` 指定工具鏈目錄。

### Flash 或 RAM 不夠用？ { #memory }

先看連結器在建置最後印出的記憶體區段使用量，再用 `./build_freertos.sh size <應用>` 與 `.map` 檔找出最大的占用者，方法見 [大小與記憶體分析](tools.md#size-analysis)。OCRAM 為 256 KB，BLE 控制器的 Exchange Memory（`CONFIG_EM_SIZE`）由其中劃出；同時啟用 `CONFIG_AI_SUPPORT` 與 `CONFIG_MM_SUPPORT` 時，OCRAM 區段縮為 64 KB 或 48 KB。關閉不需要的元件，或把大型緩衝區放到 PSRAM（`CONFIG_USE_PSRAM=y`）。

## 燒錄與主控台 { #flash-console }

### 燒錄失敗怎麼辦？ { #flashing }

依序確認：

1. 工具輸出中有沒有 `[All Success]`；工具失敗時也以 0 結束。
2. `--chip-variant` 是否符合板子：IPRO7AI Reef EVK 與 IPRO7AI EVK 用 `IPRO7AI`，IPRO7 EVB 用 `IPRO7`。工具會記住上一次的設定，換板子時務必重新指定。
3. 板子是否在下載模式：在主控台輸入 `reboot_dl`；Reef 也可按住 SW1（BOOT）再按 SW2（RESET）。
4. 序列埠是否被監看程式占用；macOS 要用 `/dev/cu.*`。
5. 分割表是否正確：Reef 使用 `--pt chips/ipro7/partition/partition_cfg_2M.toml`；IPRO7AI EVK 的 AI 範例用各自的 `flash.sh --full`。

錯誤訊息對照見 [燒錄的疑難排解](debugging.md#troubleshooting-flash)，完整步驟見 [燒錄與序列埠](../get-started/flash-and-monitor.md)。

### 主控台是亂碼或沒有輸出？ { #console }

亂碼多半是鮑率不符。鮑率由應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200；`ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_epd_el036` 等使用 921600；Zephyr 映像為 2000000。`build_freertos.sh monitor` 固定使用 115200，其他鮑率請直接執行：

```bash
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0
```

`ipro_enc28j60_test`、`ipro_gh7007_test`、`ipro_gh7007_video` 與 `ipro_pio_sdh_test` 的主控台走 USB CDC，請開啟板子列舉出的 USB 序列埠。

### macOS 的 /dev/cu.* 與 /dev/tty.* 有什麼差別？ { #macos-serial }

同一個序列裝置在 macOS 上有兩個節點：`/dev/cu.*` 直接開啟；`/dev/tty.*` 會等待載波偵測（DCD）訊號，程式因此卡住。一律使用 `/dev/cu.*`。

出現 `Resource busy` 表示其他程式（另一個監看程式、IDE 或 `stty -f`）正占用序列埠。以 `lsof /dev/cu.usbserial-XXXX` 找出並關閉它，同一時間只開一個監看程式。

## BLE { #ble }

### 該選哪一個 BLE 控制器函式庫？ { #ble-variant }

由 `.config` 的三個設定選出函式庫：`CONFIG_IPRO_BLE_CTLR_LIB`（`link1_periph` 只做 peripheral 與 broadcaster；需要 central 或多條連線時用 `link1`、`link2`、`link4`）、`CONFIG_IPRO_BLE_CTLR_FEATURE`（`bt54_iso2` 加入 ISO／LE Audio，需要 `CONFIG_EM_SIZE=32`）與 `CONFIG_IPRO_BLE_CTLR_CFG_DBG`（未設定時使用 `_release` 函式庫）。完整規則與各隨附應用的選擇見 [BLE 開發](../guides/ble.md#controller-variants)；從最接近需求的應用 `.config` 開始修改。

### 有 BLE 控制器原始碼嗎？ { #ble-prebuilt }

沒有。IPRO BLE 控制器只以預編譯函式庫提供，位於 `components/wireless/bluetooth/ipro_ble_controller/lib/`，共 16 個 IPRO7 函式庫：4 種連線配置 × 2 種功能配置 × debug／release。

下列設定會改為從原始碼建置控制器，在本套件中無法建置：`CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`（`ipro_ble_remote/defconfig_lowpower` 即使用後兩者）。需要其他函式庫組合或這些功能時，請洽 INTELPRO。

### 配對資料在重置後消失？ { #ble-bonding }

配對金鑰由 Host 的 Settings 儲存。參考 `ipro_pdm_mic_demo` 與 `ipro_le_audio_headset` 的設定：

```ini title=".config"
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_EASYFLASH4=y
```

在 `bt_enable()` 的就緒回呼中，先呼叫 `ipro_ble_ctlr_hcitl_host_ready()`，再於開始廣播前呼叫 `settings_load_subtree("bt")` 並檢查回傳值；先廣播的話，已配對的手機連上時會找不到金鑰而重新配對。`ipro_ble_remote` 的預設設定不儲存配對資料。若板子上已沒有配對資料而手機仍保留舊配對，請在手機上刪除該裝置後重新配對。

### BLE 吞吐量能到多少？ { #ble-throughput }

`ipro_throughput_test` 在兩片 IPRO7AI Reef EVK 之間的實測（預編譯 `link2` 控制器、ATT MTU 247、DLE 251 位元組、每包 244 位元組、連線間隔 50 ms、`CONFIG_IPRO7_BLE_HOTCODE=y`、單向傳送 8 秒）：2M PHY 約 1.34 Mbps，1M PHY 約 747 kbps。數值對應該測試條件，不代表所有情境。

大量資料建議使用 2M PHY、30–50 ms 連線間隔與 244 位元組的資料包；在這組條件下，較長的間隔反而較快。步驟與完整結果見 [BLE 吞吐量測試](../tutorials/ble-throughput.md)。

### 如何做 OTA 韌體更新？ { #ota }

- **FreeRTOS**：OTA 套件由 `tools/create_ota.py` 從 IntelProCube 產生的合併映像建立（見 [create_ota.py](tools.md#ota-package)）。`ipro_ble_remote` 的 OTA GATT 服務（`0xFF60`）只在 `defconfig_reef` 建置中啟用，搭配 A/B 分割表 `partition_cfg_2M_remote_ab.toml`；在 Reef 上做 OTA 必須使用這個分割表。
- **Zephyr**：以 sysbuild 建置 MCUboot（`zephyr/samples/mcuboot_app`），經 BLE 以 MCUmgr SMP 上傳映像（`zephyr/samples/ble_ota`）。

完整流程見 [OTA 更新](../guides/ota.md)。

## 平台與連網 { #platform }

### V2.1.0 支援 IPRO6S 嗎？ { #ipro6s }

不支援。V2.1.0 只提供 IPRO7 應用；IPRO6S 開發請使用 SDK V2.0.1，見 [IPRO6S（V2.0.1）](../hardware/chips/ipro6s.md)。

### IPRO7 要怎麼連網？ { #wifi }

Wi-Fi 需經 SDIO 外接 IPRO6S 作為無線電：

- IPRO7 端元件 `components/network/ipronet_host`（lwIP 網路介面 `iproeth0`），使用者有 `ipro7_sdio_wifi`、`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s`（Reef 上的 IPRO6S FIN 卡，含 RTSP 串流），以及 `ipro_agora_sentino`。
- IPRO6S 端的韌體（含 FIN 卡）未包含於 V2.1.0，請洽 INTELPRO。

有線網路使用 EMAC（RMII）驅動（`CONFIG_ETHERNET`），另有 SPI 介面 ENC28J60 的測試應用 `ipro_enc28j60_test`。

詳見 [網路](../guides/networking.md)。

### SDK 支援哪些 RTOS？BLE Host 是 Zephyr 嗎？ { #rtos }

35 個應用全部是 FreeRTOS（核心 V11.1.0）。BLE Host 來自 Zephyr v4.4.0，透過 SDK 的移植層在 FreeRTOS 上執行，應用使用 Zephyr 的 `bt_*` API，但不需要安裝 Zephyr。

此外，SDK 也是 Zephyr v4.4.0 模組，支援 `ipro7_evb` 與 `ipro7ai_evk`。本版 Zephyr 尚無低功耗模式，也沒有顯示、相機、音訊編解碼、USB、SD 主機、乙太網路與 NPU 驅動，這些功能請用 FreeRTOS；也沒有 IPRO7AI Reef EVK 的板級定義。詳見 [Zephyr RTOS](../guides/zephyr.md)。

### 可以使用 Thread 或 Matter 嗎？ { #thread-matter }

Thread 只在 Zephyr 下提供：Zephyr 的 IEEE 802.15.4 驅動加上 OpenThread，以 Zephyr 的 `samples/net/openthread/shell` 搭配 SDK 的 `zephyr/samples/ieee802154_shell/ot.conf` 與 `app.overlay` 建置。FreeRTOS 應用不含 Thread，本版也不含 Matter。詳見 [Thread 與 Matter](../guides/thread-matter.md)。

### 如何調整晶體頻率偏移（CFO）？ { #xtal-capcode }

在 `.config` 設定 `CONFIG_IPRO7_XTAL_CAPCODE=<1–255>`。開機時 `board_init()` 套用它並印出 `[XTAL] capcode <開機值> -> <設定值>`，之後每次 RF 初始化都會重新載入。設為 0 時保留開機值，直到第一次 RF 初始化載入 ROM 預設值 85。IPRO7AI Reef EVK 未指定時自動使用 95。

數值越大，頻率越低：頻率偏高（正偏移）時調大，偏低時調小。這是板子層級的數值，量產時仍需逐顆校正。Zephyr 使用 `CONFIG_SOC_IPRO7_XTAL_CAPCODE`，在 Reef 上請設為 95。程式中也可直接呼叫 `AON_Set_Xtal_CapCode()` 與 `AON_Get_Xtal_CapCode()`（`bsp/drivers/ipro7_soc/std_drv/inc/drv_aon.h`）。

## 除錯 { #debug }

### 如何開啟除錯日誌？ { #debug-log }

在 `.config` 設定整數等級後重新建置：

```ini title=".config"
CONFIG_IPRO_LOG_ENABLE=y
CONFIG_LOG_DEFAULT_LEVEL=4    # 1 錯誤、2 警告、3 資訊、4 除錯、5 詳細
```

程式讀取的是 `CONFIG_LOG_DEFAULT_LEVEL` 這個整數，只改 `CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y` 之類的選項不會生效；`CONFIG_BT_DEBUG` 也不會開啟 Host 日誌。執行時可用 `ipro_log_set_level()` 調整，見 [API 參考](api/index.md#log-api)。

### 當機或堆疊溢位怎麼分析？ { #crash }

韌體在 CPU 例外時會印出 `MCAUSE`、`MEPC`、出錯的任務與呼叫回溯；用工具鏈的 `addr2line` 對照同一次建置的 `.elf` 即可找到原始碼行號。堆疊溢位會印出 `[!] Stack overflow: <任務>`，請加大 `xTaskCreate()` 的堆疊深度（單位為 word）。詳見 [當機分析](debugging.md#crash-analysis)。
