---
title: "除錯與疑難排解"
description: 在 IPRO7AI Reef EVK 上以序列埠主控台與日誌除錯、進入下載模式、解讀當機輸出、分析建置結果、執行板上自我檢查，以及建置、燒錄、主控台與執行期常見問題的對照表。
migrate_from:
  - "tools-debugging.html#gdb-debugging"
  - "tools-debugging.html#crash-analysis"
  - "getting-started.html#debugging"
  - "getting-started.html#troubleshooting"
  - "getting-started.html#board-testing"
  - "getting-started.html#next-steps"
---

# 除錯與疑難排解

IPRO7 FreeRTOS 應用以序列埠主控台除錯：shell 指令與日誌即時顯示狀態，當機時韌體會自行印出例外分析與呼叫堆疊。本頁的步驟以 IPRO7AI Reef EVK V4.0 為準。

## 序列埠主控台 { #debugging }

Reef 的主控台是 UART0（GPIO20 TX／GPIO21 RX），由除錯排座 U6 引出，也是燒錄用的 UART。U6 不供電，板子由 USB-C 供電；接線見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#debug-connector)。

| 連接方式 | 主機上看到的序列埠 |
|---|---|
| 3.3 V USB 轉 UART 線（接 U6 第 2、3、4 腳） | macOS `/dev/cu.usbserial-XXXX`，Linux `/dev/ttyUSB0`，Windows `COM5` 之類 |
| IPRO Debug Probe（以腳序對調的排線接 U6） | 列為 `IPRO7 CMSIS_DAP`，有兩個 CDC 埠：名稱以 `02` 結尾的是 Reef 主控台（例如 `/dev/cu.usbmodemXXXX02`），`04` 是 CCI 橋接 |

鮑率由應用設定檔的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200。Reef 的應用設定都是 115200，只有 `ipro7_jpeg_decode` 的 `defconfig_reef` 是 921600。其他板子的設定中，`ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro_speaker_recog`、`ipro7_uvc_cam` 的 `.config`、`ipro7_jpeg_decode` 的 `.config` 與 `ipro_epd_el036` 也是 921600。格式 8N1、無流量控制。

<div class="ipro-steps" markdown>

1. **開啟主控台**：用任一序列埠終端程式開啟埠。以 macOS／Linux 的 `screen` 為例：

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    按 Enter，畫面出現 shell 提示字元。離開 `screen`：Ctrl-A 再按 K。

2. **列出指令**：輸入 `help`，畫面列出內建指令與應用註冊的指令。

3. **只送一行指令並看結果**（不需要互動式終端機）：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "free" --timeout 3
    ```

    畫面印出堆積總量、剩餘量與歷史最低剩餘量，3 秒後結束。

</div>

`CONFIG_SHELL=y` 的應用都有下列內建指令：

| 指令 | 用途 |
|---|---|
| `help` | 列出所有指令 |
| `ps` | 任務清單與 CPU 使用率 |
| `free` | 堆積總量、剩餘量與歷史最低剩餘量 |
| `time` | 開機後經過的時間 |
| `p <位址> [個數] [寬度]` | 讀取記憶體（寬度 1、2 或 4 位元組，預設 4） |
| `m <位址> <值> <寬度>` | 寫入記憶體 |
| `memtrace <位址> [個數]`、`memtrace <位址> <值> <個數>` | 以 32 位元字讀取或填寫記憶體（位址為十六進位） |
| `reboot` | 重新開機 |
| `reboot_dl` | 重新開機並進入下載模式，印出 `reboot to download mode` |
| `reboot_usb [code]` | 重新開機進入 boot2 的 USB 下載模式（只對以 boot2 燒錄的映像有作用），見[進入下載模式](#download-mode) |
| `watchdog`、`watchdog test` | 啟用 `CONFIG_APP_WATCHDOG` 的應用（例如 `ipro_reef_teach`）：顯示 AON 看門狗狀態；`test` 停止餵狗，板子在逾時後重新開機 |
| `ls`、`cat`、`hexdump`、`pwd`、`cd`、`mkdir`、`rm`、`cp` | 檔案系統指令，設定中有 `CONFIG_EVFS`、`CONFIG_EVFS_POSIX` 與 `CONFIG_IPRO_OSAL` 時才有 |

日誌使用 `IPRO_LOGx` 巨集（見 [API 參考](api/index.md#log-api)）。要看除錯等級的日誌，在 `.config` 設 `CONFIG_LOG_DEFAULT_LEVEL=4` 後重新建置；此值是整數，隨附應用預設為 3（資訊）。

開機時值得留意的訊息：

| 訊息 | 意義 |
|---|---|
| `[XTAL] capcode <開機值> -> <設定值>` | 已套用 `CONFIG_IPRO7_XTAL_CAPCODE` 的晶體微調；Reef 未指定時預設為 95 |
| `[PSRAM] WARNING: init failed` | 應用啟用了 `CONFIG_USE_PSRAM`，但 PSRAM 初始化失敗 |
| `[BOOT2] IPRO7 Boot2 v0.6.0` | 映像以 boot2 燒錄（例如 `ipro_ble_remote` 的 Reef OTA 版本），boot2 先執行，再啟動應用 |

## 進入下載模式 { #download-mode }

燒錄前，Reef 必須在下載模式。在下載模式中主控台沒有任何輸出；燒錄完成後按一下 SW2（RESET）回到一般開機。

| 方法 | 適用情況 |
|---|---|
| 按鍵 SW1＋SW2 | 隨時可用，包含第一次燒錄與韌體當掉時 |
| 主控台 `reboot_dl` | 板上已在執行含 shell 的 SDK 韌體 |
| U6 的 DTR／RTS 自動下載線 | USB 轉 UART 線的 DTR、RTS 接到 U6 第 5、6 腳 |
| IPRO Debug Probe 的關鍵字 | 以探針接 U6 |

<div class="ipro-steps" markdown>

1. **按鍵**：按住 SW1（BOOT）不放，按一下 SW2（RESET），再放開 SW1。主控台保持靜默，表示已在下載模式。

2. **主控台指令**：在 shell 輸入 `reboot_dl`，或在主機上執行：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
    ```

    畫面印出 `reboot to download mode` 後不再有輸出。`build_freertos.sh flash` 會以應用的主控台鮑率自動送出這個指令。

3. **自動下載線**：U6 第 5 腳（BOOT）與第 6 腳（RESET）經 1 kΩ 分別接 GPIO41 與重置腳，USB 轉 UART 線的 DTR 接第 5 腳、RTS 接第 6 腳時，能控制 DTR／RTS 的主機程式可以不按鍵就讓板子進入下載模式：BOOT 為高準位時放開 RESET。

4. **IPRO Debug Probe**：在探針名稱以 `02` 結尾的埠上，先送 `IPRODL_1` 再送 `IPRORST_RESET`；燒錄期間保持 DL 為高；燒完送 `IPRODL_0` 與 `IPRORST_RESET` 回到一般開機：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    # 以 --port /dev/cu.usbmodemXXXX02 燒錄，確認 [All Success]
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    最後一行之後，主控台出現應用的開機訊息。

</div>

**boot2 的 USB 下載模式**：以 boot2 燒錄的映像（例如 `ipro_ble_remote` 的 Reef OTA 版本）可用 `reboot_usb [code]` 重新開機進入 boot2 的 USB 下載模式，畫面印出 `reboot to boot2 USB download (HBN_RSV3=0x555342FF)`；`code` 決定等待時間（`0x01` 2 秒、`0x02` 5 秒、`0xFF` 一直等待，預設 `0xFF`）。OTA 套件驗證失敗時，boot2 也會停在這個 USB 救援模式。SDK 沒有隨附經 USB 燒錄的主機端工具；要重新燒錄時，請以上方的 UART 方法進入下載模式。

## GDB 與除錯器 { #gdb-debugging }

!!! info "未包含於 V2.2.1"
    以 JTAG 進行晶片上除錯所需的 OpenOCD 設定與步驟未包含於 V2.2.1，請洽 INTELPRO。

- **ELF 帶除錯資訊**：預設建置以 `-g3 -Os` 編譯，`<建置目錄>/build_out/<應用>_IPRO7.elf` 可直接交給工具鏈的 `riscv64-unknown-elf-addr2line` 或 `riscv64-unknown-elf-gdb` 做離線分析。燒錄用的 `.bin` 不含符號。
- **預編譯函式庫不含除錯資訊**：IPRO BLE 控制器、RF、AI、ISP、LC3 與低功耗框架等預編譯函式庫已移除除錯資訊，只保留符號名稱，無法在其中做原始碼層級單步執行。
- **IPRO Debug Probe**：在 Reef 上用作主控台橋接與下載模式控制（見[進入下載模式](#download-mode)）。探針的韌體不在 SDK 內；硬體與接線見[文件下載](../documents/index.md)中的《Debug Probe 使用手冊》。

## 當機分析 { #crash-analysis }

CPU 例外時，預設的例外處理程式會在主控台印出下列區塊：

| 區塊 | 內容 |
|---|---|
| `=== ENHANCED EXCEPTION ANALYSIS ===` | `MCAUSE`、`MEPC`、`MTVAL` 與例外類型（例如 `Illegal Instruction`、`Load Access Fault`） |
| `=== ADDRESS ANALYSIS ===` | 例外 PC 所在區域（FLASH／PSRAM／OCRAM）、返回位址 `ra`、堆疊指標 `sp` 是否在合法範圍 |
| `=== FAULTING TASK ===` | 發生例外的 FreeRTOS 任務名稱與堆疊最低剩餘量（0 表示該任務堆疊曾經溢位） |
| 暫存器傾印 | 例外當下的一般暫存器 |
| `=== STACK BACKTRACE ===` | 以框架指標（`s0`）回溯的呼叫鏈，每層列出返回位址 |

<div class="ipro-steps" markdown>

1. **存下輸出**：把主控台輸出存檔，例如 `python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0 --log crash.log`，重現問題後按 Ctrl-C。

2. **把位址換成原始碼行號**：用同一次建置的 `.elf` 查詢例外 PC（`MEPC`）、`ra` 與回溯中的位址：

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-addr2line -f -C \
        -e apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf \
        0x1301c148 0x13004a2e
    ```

    每個位址印出兩行：函式名稱，以及 `檔案:行號`。印出 `??:0` 表示位址不在這個 ELF 中，或 ELF 不是同一次建置。

3. **重置板子**：按一下 SW2（RESET）。

</div>

!!! warning "`==DUMP_READY:2000000==` 一直重複出現"
    `ipro7ai_reef_demo` 與 `ipro_reef_teach` 的 `.config` 設了 `CONFIG_EXCEPTION_DUMP=y`：印完上述診斷後，主控台約每 10 秒印一次 `==DUMP_READY:2000000==`，最長 5 分鐘，等待主機端工具讀取記憶體。這個主機端工具未包含於 V2.2.1。請先存下上方的診斷，再按 SW2 重置；不需要這個等待時，在 `.config` 改成 `CONFIG_EXCEPTION_DUMP=n` 後重新建置。

| 設定 | 作用 |
|---|---|
| `CONFIG_ENABLE_FRAME_POINTER=y` | 以 `-fno-omit-frame-pointer` 編譯，回溯才有完整的呼叫鏈；未設定時通常只能看到例外 PC 與 `ra` |
| `CONFIG_EXCEPTION_AUTO_REBOOT=y` | 印完診斷後自動重新開機，重置原因記為 `HAL_RST_REASON_EXCEPTION`；適合量產，開發時建議關閉 |
| `CONFIG_EXCEPTION_DUMP=y` | 印完診斷後等待主機端工具（見上方說明） |

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
| `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)` | Reef 建置自動加入晶體微調預設值；沒有這行時，請確認設定檔有 `CONFIG_IPRO7AI_REEF=y` |
| `AI disabled: OCRAM=240KB (256-16)`、`AI+MM (EM=0): OCRAM=64KB …` | 這次建置的 OCRAM 區段大小：未啟用 AI 時為 256 KB 減 `CONFIG_EM_SIZE`；AI 與影像同時啟用時縮為 64 KB 或 48 KB |

連結器在建置最後印出各記憶體區段的使用量；記憶體不足時的分析方法見[大小與記憶體分析](tools.md#size-analysis)。

## 板上自我檢查 { #board-testing }

Reef 開箱韌體 `ipro7ai_reef_demo` 內建自我檢查，適合在收到板子、換線或燒錄後確認硬體。SW7 放在 CAM、SW8 放在 PWR。

<div class="ipro-steps" markdown>

1. **確認開機**：按一下 SW2（RESET）。RGB LED 呼吸一次藍光後熄滅，主控台出現 shell 提示字元。

2. **執行自我檢查**

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10
    ```

    約 3 秒內，LED 依序亮紅、綠、藍，喇叭發出 1 kHz 測試音，畫面印出下列內容（第 3、4 行依板子狀態而定）：

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: <感測器名稱> at 0x<位址>
    done - keys: press any and run `btn status`
    ```

    插著 microSD 卡時第 3 行為 `something seated`；第 4 行為 `no sensor` 表示沒有偵測到相機。

3. **檢查按鍵**：按 SW3、SW4、SW5 與 BOOT，LED 分別亮紅、綠、藍、白；再送出 `btn status`，畫面列出各鍵的狀態與按下次數。

4. **看整板狀態**：送出 `reef status`，畫面列出主控台腳位、按鍵、LED、喇叭、耳麥偵測、SD 卡座與相機的狀態。

</div>

`ipro_unit_test`（HAL 與共用元件的單元測試，`./build_freertos.sh test ipro_unit_test`）需要 IPRO7 EVB。

## 疑難排解 { #troubleshooting }

### 建置 { #troubleshooting-build }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `No cmake found`，或在 macOS 上執行 `tools/cmake` 出現無法執行的錯誤 | 系統沒有 CMake；隨附的 `tools/cmake/` 是 Linux x86-64 版 | 安裝 CMake 3.15 以上（Zephyr 需 3.20 以上；例如 `brew install cmake`）並放進 `PATH`，再執行 `cmake --version` 確認 |
| 找不到 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc` | 工具鏈未安裝或在其他路徑 | 向 INTELPRO 取得工具鏈；放在其他路徑時 `export CROSS_COMPILE=<路徑>/bin/riscv64-unknown-elf-` |
| `[ipro_ble_controller] CONFIG_EM_SIZE must match …` | `.config` 缺少 `CONFIG_EM_SIZE` | 加上 `CONFIG_EM_SIZE`（隨附應用使用 16 或 32） |
| `bt54_iso2 needs at least 32 KB EM` | LE Audio 設定搭配了 16 KB EM | 設 `CONFIG_EM_SIZE=32` |
| `unsupported variant` 或 `unsupported feature profile` | 控制器設定值不在提供的組合內 | `CONFIG_IPRO_BLE_CTLR_LIB` 用 `link1_periph`、`link1`、`link2`、`link4`；`CONFIG_IPRO_BLE_CTLR_FEATURE` 用 `bt52`、`bt54_iso2` |
| 設了 `CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE` 或 `CONFIG_IPRO_PM_PDS_CONNECTED` 後，在 `ipro_ble_controller` 設定階段失敗 | 這些設定會改為從原始碼建置 BLE 控制器，而套件只提供預編譯函式庫 | 移除這些設定；需要這些功能請洽 INTELPRO |
| 連結錯誤 `undefined reference to adc_ioctl` | 使用了 `adc_channel_start()` 等 ADC 便利巨集 | 改用 `hal_adc_ioctl()` |
| 開了 `CONFIG_AI_SUPPORT` 等功能，但相依項目沒有跟著啟用 | 建置照原樣讀取 `.config`，不會套用 Kconfig 的 `select` 與 `depends on` | 明確寫入相依設定，例如 AI 需要 `CONFIG_USE_PSRAM=y`；見[建置系統與設定](../guides/build-system.md) |
| 以 `make` 建置後燒到 Reef 沒有反應 | 多數應用的 `.config` 是其他板子的設定 | 以 `DEFCONFIG=defconfig_reef…` 建置 Reef 版本，見[常見問題](faq.md#reef-apps) |
| 連結器回報記憶體區段溢位 | 程式或資料超出 `flash`、`ocram` 等區段 | 依[大小與記憶體分析](tools.md#size-analysis)找出最大的占用者；AI 與影像同時啟用時 OCRAM 只剩 64 KB 或 48 KB |

### 燒錄 { #troubleshooting-flash }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 沒有 `[All Success]`，輸出出現 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` 與板子不符；工具沿用上一次寫入的設定 | Reef 用 `--chip-variant IPRO7AI`，重新燒錄 |
| 工具無法與板子連線 | 板子不在下載模式，或序列埠被其他程式占用 | 依[進入下載模式](#download-mode)操作，再關閉序列埠監看程式後重試 |
| `build_freertos.sh flash` 顯示 `Flash tool not found` | 找不到 IntelProCube 工具 | 設定 `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`，或把工具目錄加入 `PATH` |
| `No serial port found` 或 `Several serial ports` | 沒有或有多個 USB 序列埠 | 以 `-p` 指定，或設定 `IPRO_SERIAL_PORT` |
| `build_freertos.sh flash` 燒錄 IPRO6S 應用失敗 | 腳本固定傳 `--chipname ipro7` | 在 IntelProCube 目錄直接以 `--chipname ipro6` 燒錄，見 [IPRO6S](../hardware/chips/ipro6s.md) |
| IPRO6S 燒錄出現 `[All Success]`，重置後主控台卻沒有輸出 | IntelProCube 0.7.0 的 IPRO6 開機標頭時序不適用 2 MB Flash 的 IPRO6S | 改用 IntelProCube 0.7.0.1 以上，見 [IPRO6S](../hardware/chips/ipro6s.md#ipro6s-no-boot) |
| Reef 做完 BLE OTA 後完全沒有輸出 | 以標準 `partition_cfg_2M.toml` 燒錄的板子做了 OTA | 進入下載模式，以 boot2 與 `partition_cfg_2M_remote_ab.toml` 重新燒錄，見 [ipro_ble_remote](../examples/ipro_ble_remote.md) |

### 主控台 { #troubleshooting-console }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 亂碼 | 鮑率不符 | 依應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 設定：Reef 多為 115200，`ipro7_jpeg_decode` 的 `defconfig_reef` 為 921600 |
| 完全沒有輸出 | 板子在下載模式；或 TX／RX 接反；或接的是 Debug Probe 的 `04` 埠 | 按 SW2 重置；確認 U6 第 3 腳（TX）接轉接線的 RX、第 4 腳接 TX；探針用名稱以 `02` 結尾的埠 |
| macOS 上程式卡住、沒有輸出 | 開了 `/dev/tty.*` | 改用 `/dev/cu.*` |
| `Resource busy`，或 `serial_monitor.py` 以結束碼 3 結束 | 序列埠被其他程式占用 | 關閉其他終端機或監看程式；以 `lsof /dev/cu.usbserial-XXXX` 找出占用者 |
| `cat` 只顯示部分輸出 | macOS 上 `cat` 讀序列埠有緩衝問題 | 改用 `tools/serial_monitor.py` 或其他序列埠終端程式 |
| `==DUMP_READY:2000000==` 一直重複 | 當機後等待傾印工具 | 見[當機分析](#crash-analysis) |

### 執行期與 BLE { #troubleshooting-runtime }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 主控台出現 `=== ENHANCED EXCEPTION ANALYSIS ===` | CPU 例外 | 依[當機分析](#crash-analysis)解讀 |
| `[!] Stack overflow`、`[!] Malloc failed`、`[!] ASSERT` | 堆疊、堆積不足或斷言失敗 | 見[當機分析](#crash-analysis)的對照表 |
| `[PSRAM] WARNING: init failed` | 建置啟用了 PSRAM，但 PSRAM 無法初始化 | 確認建置的是 Reef 設定（`CONFIG_IPRO7AI_REEF=y`）；仍失敗請洽 INTELPRO |
| `cam probe` 或 `reef selftest` 顯示 `no sensor` | SW7 不在 CAM，或相機排線沒有插好 | SW7 撥到 CAM；拔掉 USB-C 後重新插好排線，再上電 |
| 板子重置後配對資料消失，手機必須重新配對 | 未啟用配對資料儲存，或未在廣播前載入 | 見[常見問題](faq.md#ble-bonding) |
| BLE 吞吐量遠低於預期 | 連線參數、PHY 或 CPU 負載 | 見 [BLE 吞吐量測試](../tutorials/ble-throughput.md) |

## 下一步 { #next-steps }

- [工具命令列](tools.md)：建置、燒錄與監看工具的完整選項。
- [測試你的應用](../tutorials/testing.md)：在 Reef 上測試自己的應用。
- [API 參考](api/index.md)：平台、BLE、HAL 與日誌 API。
- [常見問題](faq.md)：建置、BLE、網路與 RTOS 的常見問答。
