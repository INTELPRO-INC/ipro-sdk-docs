---
title: "常見問題"
description: 建置、燒錄與主控台、BLE、平台與連網、除錯的常見問題與簡答，以 IPRO7AI Reef EVK 為準，並連到詳細說明的頁面。
migrate_from:
  - "faq.html"
---

# 常見問題

每題先給結論，需要操作時列出命令與預期結果，細節連到對應頁面。範例以 IPRO7AI Reef EVK V4.0 為準。錯誤訊息的對照表見[除錯與疑難排解](debugging.md#troubleshooting)。

## 建置 { #build }

### SDK、燒錄工具與工具鏈從哪裡取得？ { #get-tools }

- **SDK V2.2.0**：從 [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) 下載 `IPRO-SDK-V2.2.0.tar.gz`，核對頁面上的 SHA-256 後解開：

    ```bash
    shasum -a 256 IPRO-SDK-V2.2.0.tar.gz      # Linux：sha256sum；與 Release 頁面上的值相同
    tar xzf IPRO-SDK-V2.2.0.tar.gz
    cat IPRO-SDK-V2.2.0/VERSION.txt
    ```

    `VERSION.txt` 印出 `IPRO7: IPRO-SDK-V2.2.0`、`IPRO6: IPRO-SDK-V2.2.0` 與 `Release Date: 2026-11-03`。
- **RISC-V 工具鏈**與 **IntelProCube v0.6.3 命令列燒錄工具**（`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe`）：未包含於 V2.2.0，請洽 INTELPRO。工具鏈預設安裝於 `/opt/toolchain/riscv_ipro7/`。
- **Windows 線上安裝程式 3.4.0 與 VS Code Extension 3.3.0**：仍是目前版本，但安裝程式的 SDK 清單中 stable 版仍是 V1.2.1；V2.2.0 請從上面的 Release 頁面下載。
- **IPRO AI Studio 與 Edge AI 工具**：隨 IPRO Edge AI 套件另行提供，不在 SDK 內。

### build_freertos.sh 與 make -C 有什麼不同？ { #build-cli-vs-make }

`make -C apps/<分類>/<應用>` 只建置一個應用，必須寫完整路徑。`build_freertos.sh` 在 `make` 之外加上 `clean`、`flash`、`monitor`、`size` 與 `test`，可只寫應用名稱並串接動作：

```bash
make -C apps/platform/ipro7ai_reef_demo
./build_freertos.sh clean build ipro7ai_reef_demo
```

兩者產出相同，都在 `<應用>/build/build_out/`。`build_freertos.sh flash` 會依設定檔自動替 Reef 選 `--chip-variant IPRO7AI`，以 `-P` 指定分割表，`monitor` 以應用自己的主控台鮑率開啟。它無法傳 `--boot2` 與 `--mfg`，也不能燒錄 IPRO6S；這些情況直接使用 IntelProCube 工具，見[工具命令列](tools.md#build-cli)。

### 哪些應用能在 Reef 上執行？要選哪個設定檔？ { #reef-apps }

40 個應用中有 9 個附 Reef 設定。只有 `ipro7ai_reef_demo`、`ipro_reef_teach` 與 `ipro_agora_sentino` 直接 `make` 就是 Reef 版本；其他應用的 `.config` 是 IPRO7 EVB 或 IPRO7AI EVK 的設定，要以 `DEFCONFIG=` 選 Reef 設定：

| 應用 | 建置命令（在 SDK 根目錄） |
|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` |
| `ipro7ai_reef_demo`（Wi-Fi 與 RTSP） | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` |
| `ipro7_uvc_cam`（網路攝影機） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` |
| `ipro7_uvc_cam`（剪刀石頭布） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef`（主控台 921600） |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` |

`DEFCONFIG=defconfig_<名稱>` 的輸出放在 `build_<名稱>/build_out/`，例如 `defconfig_reef` 在 `build_reef/build_out/`，`.config` 不會被改動。要確認一個設定檔是不是 Reef 版本：

```bash
grep CONFIG_IPRO7AI_REEF apps/bluetooth/ble/ipro_ble_remote/defconfig_reef
```

印出 `CONFIG_IPRO7AI_REEF=y` 即是。各應用的分割表、`--boot2`、`--mfg` 與 USB 識別見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)，其餘應用需要的板子見[範例](../examples/index.md)。

### 改了 .config，相依的設定卻沒有生效？ { #kconfig }

建置照原樣讀取 `.config`，由 `cmake/generate_autoconf.cmake` 產生 `autoconf.h`。Kconfig 檔只是說明，`select`、`depends on` 與預設值都不會自動套用，相依設定必須自己寫進 `.config`。例如啟用 `CONFIG_AI_SUPPORT=y` 時，也要寫入 `CONFIG_USE_PSRAM=y`。唯一的例外是 Reef 的晶體微調：設定檔沒寫 `CONFIG_IPRO7_XTAL_CAPCODE` 時，建置會加入 95。

`make menuconfig` 需要的 `tools/kconfig/menuconfig.py` 與 `make defconfig` 使用的 `configs/` 目錄都未隨附，請直接編輯 `.config`，或另存成 `defconfig_<名稱>` 以 `DEFCONFIG=` 建置。詳見[建置系統與設定](../guides/build-system.md)。

### 找不到工具鏈，或工具鏈不在預設路徑？ { #toolchain }

工具鏈前綴依序取自：環境或命令列的 `CROSS_COMPILE`、設定檔的 `CONFIG_CROSS_COMPILE`、`project.build` 的預設路徑 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-`（Windows 沒有預設值）。40 個 `.config` 中有 30 個寫了 `CONFIG_CROSS_COMPILE`。工具鏈放在其他位置時：

```bash
export CROSS_COMPILE=<工具鏈路徑>/bin/riscv64-unknown-elf-
make -C apps/platform/ipro7ai_reef_demo
```

CMake 設定階段印出 `[toolchain] Vendor toolchain detected …` 表示找到了 INTELPRO 的工具鏈。`.config` 中的 `CONFIG_CPU_ID="intelpro_ipro7"` 請保留。`build_freertos.sh size` 固定使用預設路徑的 `size`。

### 可以在 Windows 上建置嗎？ { #windows }

套件中的命令列流程以 macOS 與 Linux 為主：`build_freertos.sh` 是 bash 腳本，`tools/serial_monitor.py` 使用 termios，兩者都不能在 Windows 執行。`project.build` 有 Windows 分支，條件如下：

- 每次建置都要指定 `CROSS_COMPILE`，因為 Windows 沒有預設的工具鏈路徑，而 `.config` 中的 `CONFIG_CROSS_COMPILE` 是 Unix 路徑：`make -C apps/platform/ipro7ai_reef_demo CROSS_COMPILE=<工具鏈路徑>/bin/riscv64-unknown-elf-`。
- `cmake` 與 `python`（不是 `python3`）必須在 `PATH` 上；隨附的 `tools/cmake/` 只有 Linux 版。
- 燒錄用 `ipro_iot_tool.exe`，序列埠為 `COM5` 這類名稱；主控台用任一 Windows 序列埠終端程式開啟。

套件沒有說明 Windows 上使用哪一種 shell 與 `make`。Windows 的安裝程式與 VS Code Extension 見 [Windows 安裝與 VS Code](../get-started/windows.md)。

### Flash 或 RAM 不夠用？ { #memory }

先看連結器在建置最後印出的記憶體區段使用量，再用 `./build_freertos.sh size <應用>` 與 `.map` 檔找出最大的占用者，方法見[大小與記憶體分析](tools.md#size-analysis)。OCRAM 為 256 KB，BLE 控制器的 Exchange Memory（`CONFIG_EM_SIZE`）由其中劃出；同時啟用 `CONFIG_AI_SUPPORT` 與 `CONFIG_MM_SUPPORT` 時，OCRAM 區段縮為 64 KB 或 48 KB。關閉不需要的元件，或把大型緩衝區放到 PSRAM（`CONFIG_USE_PSRAM=y`）。Flash 預設以 1 MB 版面連結，設 `CONFIG_IPRO7_FLASH_2M=y` 改用 2 MB 版面；Reef 各設定的情況見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#bsp)。

## 燒錄與主控台 { #flash-console }

### 燒錄失敗怎麼辦？ { #flashing }

依序確認：

1. **看結果字串**：工具輸出中有沒有 `[All Success]`；工具失敗時也以 0 結束。
2. **晶片設定**：Reef 用 `--chip-variant IPRO7AI`。工具會記住上一次的設定，換板子時務必重新指定。輸出出現 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` 就是這個原因。
3. **下載模式**：按住 SW1（BOOT），按一下 SW2（RESET），放開 SW1，主控台應保持靜默；或在主控台輸入 `reboot_dl`，畫面印出 `reboot to download mode`。其他方法見[進入下載模式](debugging.md#download-mode)。
4. **序列埠**：關閉其他監看程式；macOS 用 `/dev/cu.*`；IPRO Debug Probe 用名稱以 `02` 結尾的埠。
5. **分割表**：`ipro7ai_reef_demo` 與 `ipro7_uvc_cam` 用 `--pt chips/ipro7/partition/partition_cfg_2M.toml`；`ipro_ble_remote` 的 OTA 版本第一次要帶 `--boot2` 與 `partition_cfg_2M_remote_ab.toml`；`ipro_reef_teach` 用自己的 `partition_reef_teach.toml`、`--skip-ota` 與 `--mfg`。各應用見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)。

燒完按 SW2 重置，主控台出現應用的開機訊息即成功。完整步驟見[燒錄與序列埠](../get-started/flash-and-monitor.md)。

### 主控台是亂碼或沒有輸出？ { #console }

亂碼多半是鮑率不符。鮑率由設定檔的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200；Reef 的設定都是 115200，只有 `ipro7_jpeg_decode` 的 `defconfig_reef` 是 921600。`build_freertos.sh monitor` 會自動使用應用的鮑率；自己開啟時指定 `--baud`：

```bash
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0
```

沒有輸出時：板子可能還在下載模式（按 SW2 重置）、U6 的 TX／RX 接反（U6 第 3 腳是 Reef 的 TX），或開的是 Debug Probe 的 `04` 埠。`serial_monitor.py` 只能讀取與送出一行指令；要逐行輸入，請用 `screen /dev/cu.usbserial-XXXX 115200` 或其他序列埠終端程式。

### macOS 的 /dev/cu.* 與 /dev/tty.* 有什麼差別？ { #macos-serial }

同一個序列裝置在 macOS 上有兩個節點：`/dev/cu.*` 直接開啟；`/dev/tty.*` 會等待載波偵測（DCD）訊號，程式因此卡住。一律使用 `/dev/cu.*`。

出現 `Resource busy` 表示其他程式（另一個監看程式、IDE 或 `stty -f`）正占用序列埠。以 `lsof /dev/cu.usbserial-XXXX` 找出並關閉它，同一時間只開一個監看程式。

## BLE { #ble }

### 該選哪一個 BLE 控制器函式庫？ { #ble-variant }

由 `.config` 的三個設定選出函式庫：`CONFIG_IPRO_BLE_CTLR_LIB`（`link1_periph` 只做 peripheral 與 broadcaster；需要 central 或多條連線時用 `link1`、`link2`、`link4`）、`CONFIG_IPRO_BLE_CTLR_FEATURE`（`bt54_iso2` 加入 ISO／LE Audio，需要 `CONFIG_EM_SIZE=32`）與 `CONFIG_IPRO_BLE_CTLR_CFG_DBG`（未設定時使用 `_release` 函式庫）。`CONFIG_BT_CONN` 不可超過所選函式庫的連線數。建置時 CMake 印出 `[ipro_ble_controller] Using prebuilt <檔名>`，可確認實際連結的函式庫。完整規則見 [BLE 開發](../guides/ble.md)；從最接近需求的 Reef 設定（例如 `ipro_ble_remote/defconfig_reef`）開始修改。

### 有 BLE 控制器原始碼嗎？ { #ble-prebuilt }

沒有。IPRO BLE 控制器只以預編譯函式庫提供，位於 `components/wireless/bluetooth/ipro_ble_controller/lib/`，共 16 個 IPRO7 函式庫：4 種連線配置 × 2 種功能配置 × debug／release。本版沒有 IPRO6S 的 BLE 控制器函式庫，IPRO6S 應用只有 Wi-Fi。

下列設定會改為從原始碼建置控制器，在本套件中無法建置：`CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`。需要其他函式庫組合或這些功能時，請洽 INTELPRO。

### 配對資料在重置後消失？ { #ble-bonding }

配對金鑰由 Host 的 Settings 儲存。參考 `ipro_le_audio_headset` 的 `defconfig_reef`：

```ini title=".config"
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_EASYFLASH4=y
```

在 `bt_enable()` 的就緒回呼中，先呼叫 `ipro_ble_ctlr_hcitl_host_ready()`，再於開始廣播前呼叫 `settings_load_subtree("bt")` 並檢查回傳值；先廣播的話，已配對的手機連上時會找不到金鑰而重新配對。`ipro_ble_remote` 的設定不儲存配對資料。若板子上已沒有配對資料而手機仍保留舊配對，請在手機的藍牙設定中刪除該裝置後重新配對。

### BLE 吞吐量能到多少？ { #ble-throughput }

`ipro_throughput_test` 在兩片 IPRO7AI Reef EVK 之間的實測（預編譯 `link2` 控制器、ATT MTU 247、DLE 251 位元組、每包 244 位元組、連線間隔 50 ms、`CONFIG_IPRO7_BLE_HOTCODE=y`、單向傳送 8 秒）：2M PHY 約 1.34 Mbps，1M PHY 約 747 kbps。數值對應該測試條件，不代表所有情境。

大量資料建議使用 2M PHY、30–50 ms 連線間隔與 244 位元組的資料包。步驟與完整結果見 [BLE 吞吐量測試](../tutorials/ble-throughput.md)。

### 如何做 OTA 韌體更新？ { #ota }

在 Reef 上，`ipro_ble_remote` 的 `defconfig_reef` 提供 BLE OTA（GATT 服務 `0xFF60`），需要 boot2 與 A/B 分割表 `partition_cfg_2M_remote_ab.toml`：

1. 以 `--boot2` 與 `--pt …/partition_cfg_2M_remote_ab.toml` 第一次燒錄，開機訊息先出現 `[BOOT2] IPRO7 Boot2 v0.5.2`。
2. 以 `make_reef_ota.sh` 產生 `build_reef/build_out/ipro_ble_remote_reef.xz.ota`。
3. 以 `reef_ota.py` 或 Android 示範 App `ipro_remote_demo.apk` 傳送套件；板子重新開機後執行新韌體。

不要在以標準 `partition_cfg_2M.toml` 燒錄的 Reef 上做 OTA，板子會完全沒有輸出，只能進下載模式重燒。命令見 [Reef 的 OTA 工具](tools.md#reef-ota-tools)，整體流程見 [OTA 更新](../guides/ota.md)。

## 平台與連網 { #platform }

### V2.2.0 支援 IPRO6S 嗎？ { #ipro6s }

支援 Wi-Fi。V2.2.0 隨附 3 個 IPRO6S 應用：`ipro6_demo`（Wi-Fi 6 station／soft-AP）、`ipro6_if_wifi`（經 SDIO 或 USB 給主機用的 Wi-Fi 橋接）與 `ipro6_fmac`（Linux 主機用的 FullMAC 韌體）。本版沒有 IPRO6S 的 BLE 控制器函式庫與 BLE／BR/EDR 應用。

在 Reef 上，IPRO6S 是插在 microSD 卡座的 FIN Wi-Fi 卡，卡上韌體是 `ipro6_if_wifi` 的 SDIO 設定：

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

產出 `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。IPRO6S 映像以 IntelProCube 的 `--chipname ipro6` 燒錄，`build_freertos.sh flash` 不適用。可用的設定檔與燒錄方式見 [IPRO6S](../hardware/chips/ipro6s.md)。

### IPRO7 要怎麼連網？ { #wifi }

IPRO7 以外接無線電連上 Wi-Fi，Reef 上是經 SDIO 連接的 IPRO6S FIN 卡：

- **IPRO6S（SDIO）**：IPRO7 端元件 `components/network/ipronet_host`，lwIP 網路介面 `iproeth0`。Reef 上就是 FIN 卡：`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s`（含 RTSP 相機串流）與 `ipro_agora_sentino`。步驟見 [Wi-Fi 與 RTSP 串流](../tutorials/wifi-rtsp.md)。
- **其他**：ATBM6162（SDIO）、AIC8800（SDIO）與 ESP32（UART AT 指令）的元件也在套件中。
- **有線網路**：EMAC（RMII）驅動（`CONFIG_ETHERNET`）。

詳見[網路](../guides/networking.md)。

### SDK 支援哪些 RTOS？BLE Host 是 Zephyr 嗎？ { #rtos }

40 個應用全部是 FreeRTOS（核心 V11.1.0）：37 個 IPRO7、3 個 IPRO6S。BLE Host 來自 Zephyr v4.4.0，透過 SDK 的移植層在 FreeRTOS 上執行，應用使用 Zephyr 的 `bt_*` API，但不需要安裝 Zephyr。

SDK 也是 Zephyr v4.4.0 模組，板型為 `ipro7_evb` 與 `ipro7ai_evk`，沒有 Reef 的板型；SoC 的 Kconfig 說明指出 Reef 執行 `ipro7_evb` 映像時要設 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`。詳見 [Zephyr RTOS](../guides/zephyr.md)。

### 可以使用 Thread 或 Matter 嗎？ { #thread-matter }

Thread 只在 Zephyr 下提供：Zephyr 的 IEEE 802.15.4 驅動加上 OpenThread，以 Zephyr 的 `samples/net/openthread/shell` 搭配 SDK 的 `zephyr/samples/ieee802154_shell/ot.conf` 與 `app.overlay` 建置。FreeRTOS 應用不含 Thread，本版也不含 Matter。詳見 [Thread 與 Matter](../guides/thread-matter.md)。

### 如何調整晶體頻率偏移（CFO）？ { #xtal-capcode }

在 `.config` 設定 `CONFIG_IPRO7_XTAL_CAPCODE=<1–255>`。開機時 `board_init()` 套用它並印出 `[XTAL] capcode <開機值> -> <設定值>`，之後每次 RF 初始化都會重新載入。設為 0 時保留開機值，直到第一次 RF 初始化載入 ROM 預設值 85。Reef 未指定時自動使用 95，CMake 設定階段印出 `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)`。

數值越大，頻率越低：頻率偏高（正偏移）時調大，偏低時調小。這是板子層級的數值，量產時仍需逐顆校正。程式中也可直接呼叫 `AON_Set_Xtal_CapCode()` 與 `AON_Get_Xtal_CapCode()`（`bsp/drivers/ipro7_soc/std_drv/inc/drv_aon.h`）。

## 除錯 { #debug }

### 如何開啟除錯日誌？ { #debug-log }

在 `.config` 設定整數等級後重新建置：

```ini title=".config"
CONFIG_IPRO_LOG_ENABLE=y
CONFIG_LOG_DEFAULT_LEVEL=4    # 1 錯誤、2 警告、3 資訊、4 除錯、5 詳細
```

程式讀取的是 `CONFIG_LOG_DEFAULT_LEVEL` 這個整數，只改 `CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y` 之類的選項不會生效；`CONFIG_BT_DEBUG` 也不會開啟 Host 日誌。執行時可用 `ipro_log_set_level()` 調整，見 [API 參考](api/index.md#log-api)。

### 當機或堆疊溢位怎麼分析？ { #crash }

韌體在 CPU 例外時會印出 `MCAUSE`、`MEPC`、出錯的任務與呼叫回溯；用工具鏈的 `addr2line` 對照同一次建置的 `.elf`，即可找到函式與原始碼行號。堆疊溢位會印出 `[!] Stack overflow: <任務>`，請加大 `xTaskCreate()` 的堆疊深度（單位為 word）。`ipro7ai_reef_demo` 與 `ipro_reef_teach` 當機後會重複印出 `==DUMP_READY:2000000==`，等待未隨附的主機端工具：存下診斷後按 SW2 重置即可。本版沒有晶片上除錯器（JTAG／GDB）的設定。詳見[當機分析](debugging.md#crash-analysis)。
