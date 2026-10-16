---
title: "除錯與疑難排解"
description: 以序列埠主控台與日誌除錯、解讀當機輸出、分析建置結果、執行板上單元測試，以及建置、燒錄、主控台與執行期常見問題的對照表。
migrate_from:
  - "tools-debugging.html#gdb-debugging"
  - "tools-debugging.html#crash-analysis"
  - "getting-started.html#debugging"
  - "getting-started.html#troubleshooting"
  - "getting-started.html#board-testing"
  - "getting-started.html#next-steps"
---

# 除錯與疑難排解

IPRO7 FreeRTOS 應用主要以序列埠主控台除錯：shell 指令與日誌即時顯示狀態，當機時韌體會自行印出例外分析與呼叫堆疊。

## 序列埠主控台 { #debugging }

主控台在 UART0（GPIO20 TX／GPIO21 RX）；IPRO7AI Reef EVK 由 U6 接頭引出。鮑率由應用 `.config` 的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200；`ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_epd_el036` 等少數應用使用 921600。Zephyr 映像固定為 2000000 baud。開啟方式見 [serial_monitor.py](tools.md#serial-monitor)。

`CONFIG_SHELL=y` 的應用都有下列內建指令，應用另外註冊的指令以 `help` 列出：

| 指令 | 用途 |
|---|---|
| `help` | 列出所有指令 |
| `ps` | 任務清單與 CPU 使用率 |
| `free` | 堆積總量、剩餘量與歷史最低剩餘量 |
| `time` | 開機後經過的時間 |
| `p <位址> [個數] [寬度]` | 讀取記憶體（寬度 1、2 或 4 位元組，預設 4） |
| `m <位址> <值> <寬度>` | 寫入記憶體 |
| `reboot` | 重新開機 |
| `reboot_dl` | 重新開機並進入下載模式，準備燒錄 |

日誌使用 `IPRO_LOGx` 巨集（見 [API 參考](api/index.md#log-api)）。要看除錯等級的日誌，在 `.config` 設 `CONFIG_LOG_DEFAULT_LEVEL=4` 後重新建置；此值是整數，隨附應用預設為 3（資訊）。

開機時值得留意的訊息：

| 訊息 | 意義 |
|---|---|
| `[XTAL] capcode <開機值> -> <設定值>` | 已套用 `CONFIG_IPRO7_XTAL_CAPCODE` 的晶體微調；IPRO7AI Reef EVK 未指定時預設為 95 |
| `[PSRAM] WARNING: init failed` | 應用啟用了 `CONFIG_USE_PSRAM`，但 PSRAM 初始化失敗 |

## GDB 與除錯器 { #gdb-debugging }

!!! info "未包含於 V2.1.0"
    以 JTAG 進行線上除錯所需的 OpenOCD 設定未包含於 V2.1.0，請洽 INTELPRO。

- **ELF 帶除錯資訊**：預設建置以 `-g3 -Os` 編譯，`<應用>/build/build_out/<應用>_IPRO7.elf` 可直接交給工具鏈的 `riscv64-unknown-elf-addr2line` 或 `riscv64-unknown-elf-gdb` 做離線分析。燒錄用的 `.bin` 不含符號。
- **預編譯函式庫不含除錯資訊**：IPRO BLE 控制器、RF、AI、ISP、LC3 與低功耗框架等預編譯函式庫已移除除錯資訊，只保留符號名稱，無法在其中做原始碼層級單步執行。
- **IPRO Debug Probe**：在主機上列為 `IPRO7 CMSIS_DAP`，有兩個 CDC 序列埠。名稱以 `02` 結尾的是接到板子主控台（UART0）的 UART 橋接，`04` 是 CCI 橋接。`west flash` 預設透過它讓板子進入下載模式（`--boot probe`，見 [Zephyr 腳本](tools.md#zephyr-tools)）。除錯器的硬體與接線見 [文件下載](../documents/index.md) 中的《Debug Probe 使用手冊》。

## 當機分析 { #crash-analysis }

CPU 例外時，預設的例外處理程式會在主控台印出下列區塊，然後停住：

| 區塊 | 內容 |
|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` | `MCAUSE`、`MEPC`、`MTVAL` 與例外類型（例如 `Illegal Instruction`、`Load Access Fault`） |
| `=== ADDRESS ANALYSIS ===` | 例外 PC 所在區域（FLASH／PSRAM／OCRAM）、返回位址 `ra`、堆疊指標 `sp` 是否在合法範圍 |
| `=== FAULTING TASK ===` | 發生例外的 FreeRTOS 任務名稱與堆疊最低剩餘量（0 表示該任務堆疊曾經溢位） |
| 暫存器傾印 | 例外當下的一般暫存器 |
| `=== STACK BACKTRACE ===` | 以框架指標（`s0`）回溯的呼叫鏈，每層列出返回位址 |

用工具鏈的 `addr2line` 把例外 PC、`ra` 與回溯中的位址換成函式名稱與原始碼行號：

```bash
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-addr2line -f -C \
    -e apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf \
    0x1301c148 0x13004a2e
```

位址必須對應同一次建置的 `.elf`；重新建置後舊的位址就不再適用。

| 設定 | 作用 |
|---|---|
| `CONFIG_ENABLE_FRAME_POINTER=y` | 以 `-fno-omit-frame-pointer` 編譯，回溯才有完整的呼叫鏈；未設定時通常只能看到例外 PC 與 `ra` |
| `CONFIG_EXCEPTION_AUTO_REBOOT=y` | 印完診斷後自動重新開機，重置原因記為 `HAL_RST_REASON_EXCEPTION`；適合量產，開發時建議關閉 |
| `CONFIG_EXCEPTION_DUMP=y` | 印完診斷後顯示 `==DUMP_READY:` 並等待主機端工具讀取記憶體；該主機端工具未包含於 V2.1.0，看到此訊息時直接閱讀上方的診斷並重置板子 |

`.config` 是照原樣讀入的，Kconfig 的預設值不會自動套用，上述設定需要明確寫入。

其他致命訊息來自 [FreeRTOS 掛鉤](api/index.md#rtos-platform)：

| 訊息 | 原因 | 處理 |
|---|---|---|
| `[!] Stack overflow: <任務>` | 該任務堆疊用盡 | 加大 `xTaskCreate()` 的堆疊深度（單位為 word）；隨後的 `[STACKS]` 列表顯示各任務剩餘量 |
| `[!] Malloc failed, requested: …` | 堆積不足 | 以 `free` 指令觀察剩餘量，減少配置或啟用 PSRAM；訊息中的 `caller` 位址可用 `addr2line` 查出呼叫者 |
| `[!] ASSERT <檔案>:<行號>` | `configASSERT()` 失敗 | 依檔案與行號檢查條件；`Caller` 位址可用 `addr2line` 查詢 |

## 建置分析 { #build-analysis }

以 `build_freertos.sh` 建置時，完整輸出寫在 `<建置目錄>/build.log`，失敗時只在終端機印出最後 30 行；加 `-v` 可直接看完整輸出。CMake 設定階段的幾行訊息可確認建置用了什麼：

| 訊息 | 意義 |
|---|---|
| `[toolchain] Vendor toolchain detected …` | 偵測到 INTELPRO 提供的工具鏈，啟用 IPRO7 專用的 DSP 擴充與最佳化；若顯示 `Standard toolchain detected`，表示使用一般 RISC-V GCC |
| `[bluetooth] Using unified Zephyr 4.4 host (ipro_bt_host)` | 已納入 BLE Host |
| `[ipro_ble_controller] Using prebuilt …` | 實際連結的 BLE 控制器函式庫檔名，可核對 `CONFIG_IPRO_BLE_CTLR_*` 是否如預期 |
| `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` | Reef 建置自動加入晶體微調預設值 |
| `AI disabled: OCRAM=240KB (256-16)`、`AI+MM (EM=0): OCRAM=64KB …` | 這次建置的 OCRAM 區段大小：未啟用 AI 時為 256 KB 減 `CONFIG_EM_SIZE`；AI 與影像同時啟用時縮為 64 KB 或 48 KB |

連結器在建置最後印出各記憶體區段的使用量；記憶體不足時的分析方法見 [大小與記憶體分析](tools.md#size-analysis)。

## 板上測試 { #board-testing }

`apps/test/ipro_unit_test` 測試 HAL 與共用元件，適合在新板子或移植後確認基本功能。它的設定為 IPRO7 EVB（`CONFIG_EVB=y`），開機後自動執行全部測試（`CONFIG_TEST_AUTO_RUN=y`），最後印出摘要與 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`。

<div class="ipro-steps" markdown>

1. **建置**

    ```bash
    make -C apps/test/ipro_unit_test
    ```

2. **燒錄並等待結果**：在 IPRO7 EVB 上可一次完成建置、燒錄與判讀。

    ```bash
    ./build_freertos.sh test ipro_unit_test -p /dev/cu.usbserial-XXXX -t 60
    ```

    結束碼 0 為通過、1 為失敗、2 為逾時。`test` 燒錄時不指定 `--chip-variant`，若 IntelProCube 上一次燒錄的是 IPRO7AI 板子，先以 `--chip-variant IPRO7` 執行一次工具。

3. **單獨重跑**：主控台（115200 baud）可用下列指令。

    | 指令 | 用途 |
    |---|---|
    | `test_all` | 執行全部測試 |
    | `test_list` | 列出測試套件 |
    | `test_run <套件>` | 執行單一套件 |
    | `test_group <sw|hal|crypto|ble>` | 執行一組測試 |
    | `test_status` | 顯示結果摘要 |

</div>

偵測不到對應硬體的 HAL 測試會自動略過。

## 疑難排解 { #troubleshooting }

### 建置 { #troubleshooting-build }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `No cmake found`，或在 macOS 上執行 `tools/cmake` 出現無法執行的錯誤 | 系統沒有 CMake；隨附的 `tools/cmake/` 是 Linux x86-64 版 | 安裝 CMake 3.19 以上（Zephyr 需 3.20 以上；例如 `brew install cmake`）並放進 `PATH` |
| 找不到 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc` | 工具鏈未安裝或在其他路徑 | 向 INTELPRO 取得工具鏈；放在其他路徑時 `export CROSS_COMPILE=<路徑>/bin/riscv64-unknown-elf-` |
| `[ipro_ble_controller] CONFIG_EM_SIZE must match …` | `.config` 缺少 `CONFIG_EM_SIZE` | 加上 `CONFIG_EM_SIZE`（隨附應用使用 16 或 32） |
| `bt54_iso2 needs at least 32 KB EM` | LE Audio 設定搭配了 16 KB EM | 設 `CONFIG_EM_SIZE=32` |
| `unsupported variant` 或 `unsupported feature profile` | 控制器設定值不在提供的組合內 | `CONFIG_IPRO_BLE_CTLR_LIB` 用 `link1_periph`、`link1`、`link2`、`link4`；`CONFIG_IPRO_BLE_CTLR_FEATURE` 用 `bt52`、`bt54_iso2` |
| 使用 `ipro_ble_remote/defconfig_lowpower`，或設了 `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED` 後，在 `ipro_ble_controller` 設定階段失敗 | 這些設定會改為從原始碼建置 BLE 控制器，而套件只提供預編譯函式庫 | 移除這些設定；需要這些功能請洽 INTELPRO |
| `CONFIG_EVK_CAMERA needs …`、`CONFIG_EVK_AUDIO needs …`、`CONFIG_EVK_SDCARD needs …` | EVK 板級函式庫缺少相依設定 | 依訊息補上設定，見 [API 參考](api/ipro7ai-evk.md) |
| 連結錯誤 `undefined reference to adc_ioctl` | 使用了 `adc_channel_start()` 等 ADC 便利巨集 | 改用 `hal_adc_ioctl()` |
| 開了 `CONFIG_AI_SUPPORT` 等功能，但相依項目沒有跟著啟用 | 建置照原樣讀取 `.config`，不會套用 Kconfig 的 `select` 與 `depends on` | 明確寫入相依設定，例如 AI 需要 `CONFIG_USE_PSRAM=y`；見 [建置系統與設定](../guides/build-system.md) |
| 連結器回報記憶體區段溢位 | 程式或資料超出 `flash`、`ocram` 等區段 | 依 [大小與記憶體分析](tools.md#size-analysis) 找出最大的占用者；AI 與影像同時啟用時 OCRAM 只剩 64 KB 或 48 KB |

### 燒錄 { #troubleshooting-flash }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 沒有 `[All Success]`，輸出出現 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` 與板子不符；工具沿用上一次寫入的設定 | IPRO7AI Reef EVK 與 IPRO7AI EVK 用 `--chip-variant IPRO7AI`，IPRO7 EVB 用 `IPRO7`，重新燒錄 |
| 工具無法與板子連線 | 板子不在下載模式，或序列埠被其他程式占用 | 在主控台輸入 `reboot_dl`，或依板子進入下載模式（Reef：按住 SW1 BOOT 再按 SW2 RESET，見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）；關閉序列埠監看程式 |
| `build_freertos.sh flash` 顯示 `Flash tool not found` | 找不到 IntelProCube 工具 | 設定 `IPRO_FLASH_TOOL`，或把工具目錄加入 `PATH` |
| `No serial port found` 或 `Several serial ports` | 沒有或有多個 USB 序列埠 | 以 `-p` 指定，或設定 `IPRO_SERIAL_PORT` |
| IPRO7AI EVK 的 AI 範例開機後顯示 `NO MFG PARTITION` | 燒錄時沒有寫入該範例的分割表（例如用了不傳 `--pt` 的 `build_freertos.sh flash`） | 在範例目錄執行 `PORT=/dev/cu.usbserial-XXXX ./flash.sh --full`，一次燒錄分割表、韌體與模型 |

### 主控台 { #troubleshooting-console }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 亂碼 | 鮑率不符 | 依應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 設定（115200 或 921600）；Zephyr 為 2000000 |
| macOS 上程式卡住、沒有輸出 | 開了 `/dev/tty.*` | 改用 `/dev/cu.*` |
| `Resource busy`，或 `serial_monitor.py` 以結束碼 3 結束 | 序列埠被其他程式占用 | 關閉其他終端機或監看程式；以 `lsof /dev/cu.usbserial-XXXX` 找出占用者 |
| `cat` 只顯示部分輸出 | macOS 上 `cat` 讀序列埠有緩衝問題 | 改用 `tools/serial_monitor.py` 或其他序列埠終端程式 |
| `ipro_enc28j60_test`、`ipro_gh7007_test`、`ipro_gh7007_video`、`ipro_pio_sdh_test` 的 UART 沒有輸出 | 這些應用的主控台走 USB CDC | 開啟板子列舉出的 USB 序列埠 |

### 執行期與 BLE { #troubleshooting-runtime }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 主控台出現 `=== ENHANCED EXCEPTION ANALYSIS ===` | CPU 例外 | 依 [當機分析](#crash-analysis) 解讀 |
| `[!] Stack overflow`、`[!] Malloc failed`、`[!] ASSERT` | 堆疊、堆積不足或斷言失敗 | 見 [當機分析](#crash-analysis) 的對照表 |
| `[PSRAM] WARNING: init failed` | 建置啟用了 PSRAM，但板上 PSRAM 無法初始化 | 確認板子與封裝有 PSRAM；沒有時移除 `CONFIG_USE_PSRAM` 與依賴 PSRAM 的功能 |
| 板子重置後配對資料消失，手機必須重新配對 | 未啟用配對資料儲存，或未在廣播前載入 | 見 [常見問題](faq.md#ble-bonding) |
| BLE 吞吐量遠低於預期 | 連線參數、PHY 或 CPU 負載 | 見 [BLE 吞吐量測試](../tutorials/ble-throughput.md) |
| `west flash` 無法進入下載模式 | 預設 `--boot probe` 需要 IPRO 除錯器 | 改用 `west flash -- --boot manual`（手動）或 `--boot shell`（執行中的映像有 shell 時） |

## 下一步 { #next-steps }

- [工具命令列](tools.md)：建置、燒錄與監看工具的完整選項。
- [API 參考](api/index.md)：平台、BLE、HAL 與日誌 API。
- [常見問題](faq.md)：建置、BLE、網路與 RTOS 的常見問答。
- [BLE 開發](../guides/ble.md) 與 [Zephyr RTOS](../guides/zephyr.md)：依功能領域的開發指南。
