---
title: "VS Code Extension"
description: IPRO SDK Extension 3.3.0 搭配 SDK V2.2.0：設定 SDK 根目錄、建置、燒錄 IPRO7AI Reef EVK、序列埠主控台、記憶體分析與命令
migrate_from:
  - "vscode-extension.html"
not_migrated:
  - "vscode-extension.html#installation — installation steps live in get-started/windows.md"
  - "vscode-extension.html#cli-tools — the IntelProCube command line belongs on the flashing page"
---

# VS Code Extension

IPRO SDK Extension 3.3.0（識別碼 `ipro.ipro-sdk-extension`）把 FreeRTOS 專案瀏覽、CMake 建置、IntelProCube 燒錄、序列埠主控台與記憶體分析整合到 VS Code，需要 VS Code 1.102 以上。Extension 不包含在 SDK 套件內，與 SDK、負責安裝它的 IPRO SDK Online Setup 分開計版；安裝步驟見 [Windows 安裝與 VS Code](../get-started/windows.md)。

!!! abstract "重點"
    - Online Setup 3.4.0 會安裝 Extension 與各項工具，但它的套件清單仍以 SDK V1.2.1 為穩定版。SDK V2.2.0 請自行加入，再以 `IPRO Setup: Set SDK Root` 指向它。
    - SDK V2.2.0 以 GCC 14 建置，請確認 Extension 使用的編譯器相符。
    - 燒錄 IPRO7AI Reef EVK 時，晶片配置用 `IPRO7AI`，分割表用應用所用的那一份；boot2 映像與 `mfg` 資料以 IntelProCube 命令列寫入。
    - 主控台鮑率（`ipro.monitorBaudRate`）與燒錄鮑率（`ipro.baudRate`）分開設定。
    - 沒有原始碼層級（F5）除錯：安裝 OpenOCD 並不會設定好 GDB debug adapter。

## 功能 { #features }

| 功能 | 用途 |
|---|---|
| 專案 | 依分類瀏覽應用、釘選並切換目前的專案（`IPRO: Go to Project…`、`IPRO: Select Project`） |
| Build／Batch Build | CMake 設定與 Make／Ninja 建置（`ipro.generator`），debug／release／size Profile，錯誤可從 Problems 跳到原始碼 |
| 設定 | `IPRO Config: Menuconfig`、`IPRO Config: Open .config`、`IPRO Config: Load Defconfig` |
| Flash／Monitor | 以 IntelProCube 燒錄；內建序列埠主控台，鮑率另外設定 |
| Analysis／Debug | Memory Map、Decode Crash Report、Pin Function Lookup；Register Explorer 需相容的 CCI 連線 |

SDK 建置原樣讀取 `.config`，不解析 Kconfig 的 `select` 與 `depends on`。用 Menuconfig 修改後，請確認相依選項都已寫入 `.config`，見[建置系統與設定](build-system.md#configuration)。

## 使用 SDK V2.2.0 { #sdk-2-2-0 }

<div class="ipro-steps" markdown>

1. 依[加入 SDK V2.2.0](../get-started/windows.md#get-sdk)，從 [IPRO-SDK-V2.2.0 發行頁](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0)下載、校驗 `IPRO-SDK-V2.2.0.tar.gz`，解壓到新的目錄。
2. 以 **File → Open Folder…** 開啟該目錄（內含 `CMakeLists.txt`、`apps` 與 `bsp`），並對它執行 `IPRO Setup: Set SDK Root`。
3. 執行 `IPRO Setup: Run Diagnostics`，核對 SDK 根目錄、編譯器、CMake、Ninja、Python 與燒錄工具。編譯器必須是與 V2.2.0 相符的 GCC 14 工具鏈；Online Setup 安裝的是清單中與 SDK V1.2.1 搭配的工具鏈。請向 INTELPRO 取得相符的工具鏈，再以 `ipro.toolchainPath` 設定（編譯器前綴，以 `riscv64-unknown-elf-` 結尾）。

</div>

- 在 V2.2.0 建置並上板驗證之前，保留原本的 SDK 目錄。不要把舊的 `build/` 目錄、CMake 快取或 `.vscode` 資料夾複製到新的 SDK。
- 工作區設定（`.vscode/settings.json`）可能蓋過使用者設定；以 Diagnostics 顯示的路徑為準。

## 控制中心 { #control-center }

按 F1 執行 `IPRO: Open Control Center`，在同一個面板看到目前的 SDK、專案與連線，以及常用操作；再執行 `IPRO Setup: Run Diagnostics` 核對工具路徑。也可以在 VS Code 的 Settings 搜尋 `ipro` 調整設定。

## 第一次建置 { #workflow }

<div class="ipro-steps" markdown>

1. 執行 `IPRO: Go to Project…`，選擇 platform 分類的 `ipro7ai_reef_demo`。
2. 執行 `IPRO Config: Select Build Profile`，選擇 debug、release 或 size。
3. 執行 `IPRO: Build`，在 Terminal 查看結果；錯誤可從 Problems 跳到原始碼。建置成功的標準是結束碼為 0 且產生映像，不是看到 CMake 印出 `Configuring done`。
4. 確認產生 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

</div>

`IPRO: Batch Build` 一次建置多個選定的專案。SDK 或工具路徑變更後，先執行 `IPRO: Clean` 再重新建置，避免沿用舊的快取。

多數 Reef 應用把 Reef 的設定放在另一個檔案（`defconfig_reef`、`defconfig_reef_ov5640` 等）；直接建置就是 Reef 版本的只有 `ipro7ai_reef_demo`、`ipro_reef_teach` 與 `ipro_agora_sentino`。命令列寫法 `make -C <應用> DEFCONFIG=<檔名>` 與 Reef 設定清單見[建置系統與設定](build-system.md#variants)。

## 燒錄與主控台 { #flash }

<div class="ipro-steps" markdown>

1. 以 `IPRO Setup: Select Flash Tool` 選擇 IntelProCube，或把 `ipro.flashToolPath` 設為它的資料夾。
2. 接好開發板（SW7 撥到 CAM、SW8 撥到 PWR、主控台線接 U6、插上 USB-C），執行 `IPRO: Select Serial Port` 選擇主控台埠。使用 IPRO Debug Probe 時選它的 UART 埠；CCI 埠用於暫存器存取，不能用於主控台或燒錄。
3. 在 `IPRO Config: Configure Flash…` 把晶片配置設為 `IPRO7AI`，分割表設為應用所用的那一份：`ipro7ai_reef_demo` 與 `ipro7_uvc_cam` 網路攝影機用 `partition_cfg_2M.toml`。自帶分割表的應用列在[燒錄與序列埠](../get-started/flash-and-monitor.md#partition-tables)。
4. 讓 Reef 進入下載模式：按住 SW1（BOOT），按一下 SW2（RESET），放開 SW1。接著執行 `IPRO: Flash`，確認燒錄工具的結果。先關閉其他占用序列埠的程式。
5. 按 SW2 啟動韌體。確認 `ipro.monitorBaudRate` 與韌體一致（`IPRO Config: Set Monitor Baud Rate`），再執行 `IPRO: Serial Monitor`。要改鮑率時，先執行 `IPRO: Close Serial Monitor`，設定後再重新開啟。

</div>

| 設定 | 意義 |
|---|---|
| `ipro.baudRate` | 燒錄鮑率，預設 921600 |
| `ipro.monitorBaudRate` | 主控台鮑率，預設 115200，必須與韌體一致 |
| `ipro.chipVariant` | 傳給燒錄工具的 `--chip-variant`：Reef 用 `IPRO7AI` |
| `ipro.partitionTable` | 傳給燒錄工具的 `--pt`；在 Reef 上請依應用設定 |
| `ipro.flashTargets`、`ipro.activeFlashTarget` | 具名的燒錄設定，切換時不必每次修改設定 |

所有 Reef 設定的主控台都是 115200 baud，只有 `ipro7_jpeg_decode`（`defconfig_reef`）是 921600，以應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 為準。`ipro_ble_remote` 的第一次燒錄（boot2 與 A/B 分割表）與 `ipro_reef_teach` 的 `mfg` 資料，請用 IntelProCube 命令列，見[燒錄與序列埠](../get-started/flash-and-monitor.md#boot2-ab)與[燒錄 Edge AI 韌體](../teach/firmware.md)。

## 記憶體與除錯工具 { #memory-map }

- `IPRO Analyse: Memory Map`：建置後檢視各記憶體區域與各元件的用量。是否放得下仍以連結器輸出與燒錄時用的分割表為準。
- `IPRO Analyse: Decode Crash Report`：把例外的回溯轉成原始碼位置。
- `IPRO Debug: Pin Function Lookup`：查詢腳位功能。
- `IPRO Debug: Register Explorer`：需要相容的 Probe、可正常運作的 CCI 連線與正確的板端設定。Probe 能在 USB 列舉，不代表與開發板之間的 CCI 連線可用。

安裝 OpenOCD 並不會帶來 F5 原始碼層級除錯：Extension 不會設定 GDB debug adapter 或 launch 設定。主控台日誌與當機解碼見[除錯與疑難排解](../reference/debugging.md)。

## 在 Reef 上動手做 { #hands-on }

以出廠韌體走一次 VS Code 裡的「修改、建置、燒錄」流程。

<div class="ipro-steps" markdown>

1. **確認主控台設定。** 韌體的主控台鮑率寫在 `.config`，`ipro.monitorBaudRate` 必須相同：

    ```ini title="apps/platform/ipro7ai_reef_demo/.config（節錄）"
    CONFIG_PLATFORM_UART_BAUDRATE=115200
    ```

2. **修改程式。** 開啟 `apps/platform/ipro7ai_reef_demo/main.c`，修改 `main()` 裡的標語：

    ```c title="apps/platform/ipro7ai_reef_demo/main.c（節錄，已修改）"
    ipro_platform_init();   /* heap + boot2 + log + shell */

    IPRO_LOGI(LOG_TAG, "==========================================");
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **建置**：執行 `IPRO: Build`。映像檔是 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

4. **燒錄**：依[燒錄與主控台](#flash)，以 SW1 + SW2 進入下載模式，晶片配置 `IPRO7AI`、分割表 `partition_cfg_2M.toml` 執行 `IPRO: Flash`，再按 SW2。

5. **看主控台**：以 115200 baud 執行 `IPRO: Serial Monitor`。開頭幾行中（略去日誌前綴）：

    ```text
    Build:<時間>,<日期>
    ...
      IPRO7AI Reef carrier demo - my build
    ```

    `Build:` 行是這次建置的時間，標語則是你改過的文字。`reef selftest` 可檢查板上各區塊。

</div>

完成後把那一行改回來，或重新燒錄出廠映像。接下來：[建立第一個自己的應用](../tutorials/first-own-app.md)與[測試你的應用](../tutorials/testing.md)。

## 元件更新 { #component-updates }

更新透過 IPRO SDK Online Setup 進行；它把每個元件安裝到新的目錄，不會覆蓋正在使用的版本：

| Online Setup 模式 | 安裝內容 | 可切換的設定 |
|---|---|---|
| Full environment | SDK、工具鏈、建置工具（CMake、Ninja、Python）、IntelProCube、OpenOCD、Extension | 全部 |
| Toolchain only | RISC-V 工具鏈 | `ipro.toolchainPath` |
| Build tools only | CMake、Ninja、Python | 各自的路徑 |
| IntelProCube only | IntelProCube | `ipro.flashToolPath` |
| Extension only | Extension VSIX | — |

SDK V2.2.0 不在安裝程式的清單中，請自行加入（見[使用 SDK V2.2.0](#sdk-2-2-0)）。更新後重開 VS Code 並執行 Diagnostics。要回到舊版時，把設定指回保留的目錄，或以 **Install from VSIX…** 安裝舊版 VSIX。

## 命令 { #shortcuts }

F1 或 Ctrl+Shift+P 開啟命令面板。Extension 沒有預設快捷鍵，可自行綁定。

| 命令 | 用途 |
|---|---|
| `IPRO: Open Control Center` | 開啟控制中心 |
| `IPRO Setup: Set SDK Root` | 設定 SDK 根目錄 |
| `IPRO Setup: Run Diagnostics` | 檢查 SDK 與工具路徑 |
| `IPRO Setup: Select Flash Tool` | 選擇 IntelProCube 資料夾 |
| `IPRO: Go to Project…`、`IPRO: Select Project` | 尋找與切換專案 |
| `IPRO Config: Select Build Profile` | 選擇 debug、release 或 size |
| `IPRO: Build` | 建置目前的專案 |
| `IPRO: Clean` | 刪除目前專案的建置輸出 |
| `IPRO: Batch Build` | 建置多個專案 |
| `IPRO Config: Menuconfig`、`IPRO Config: Open .config` | 編輯或開啟設定 |
| `IPRO Config: Select Flash Target`、`IPRO Config: Configure Flash…` | 選擇燒錄目標；設定晶片配置、分割表與鮑率 |
| `IPRO: Select Serial Port` | 選擇主控台／燒錄序列埠 |
| `IPRO Config: Set Monitor Baud Rate` | 設定主控台鮑率 |
| `IPRO: Flash` | 燒錄韌體 |
| `IPRO: Serial Monitor`、`IPRO: Close Serial Monitor` | 開啟主控台；關閉並釋放序列埠 |
| `IPRO: Build, Flash & Monitor` | 依序建置、燒錄並開啟主控台 |
| `IPRO Analyse: Memory Map` | 分析記憶體用量 |
| `IPRO Analyse: Decode Crash Report` | 解碼例外與回溯 |
| `IPRO Debug: Pin Function Lookup` | 查詢腳位功能 |
| `IPRO Debug: Register Explorer` | 經 CCI 檢視暫存器 |

## 常見問題 { #faq }

| 現象 | 處理方式 |
|---|---|
| 找不到 IPRO 命令 | 確認 Extension 版本、VS Code Profile、Workspace Trust 與 SDK 根目錄，再重新載入視窗 |
| Diagnostics 仍顯示舊的 SDK | 工作區與資料夾設定可能蓋過使用者設定；對 V2.2.0 目錄再執行一次 `IPRO Setup: Set SDK Root` |
| 編譯或連結失敗 | 確認編譯器是與 V2.2.0 相符的工具鏈（GCC 14） |
| 主控台亂碼或仍是舊鮑率 | 核對韌體的主控台鮑率與 `ipro.monitorBaudRate`，再關閉並重開主控台 |
| 燒錄 Reef 時出現 `flash jedec id: 00000000` | 把晶片配置設為 `IPRO7AI` |
| 燒錄工具沒有印出 `[All Success]` | 開發板沒有進入下載模式，或序列埠被其他程式占用 |
| 偵測得到 Probe，但 CCI 沒有回應 | USB 列舉成功不代表板端的 CCI 連線正常；檢查接線與板端設定 |

## 版本 { #version }

SDK、Extension 與 Online Setup 是各自計版的套件。目前的 Extension 是 3.3.0，由 Online Setup 3.4.0 安裝；安裝程式的版本號不代表 Extension 也是同一版。實際安裝的版本以 Extensions 面板顯示為準。

## 相關文件 { #related }

- [Windows 安裝與 VS Code](../get-started/windows.md)：安裝工具與 Extension、加入 SDK V2.2.0。
- [燒錄與序列埠](../get-started/flash-and-monitor.md)：IntelProCube 命令列、分割表、boot2 與 `mfg`。
- [建置系統與設定](build-system.md)：`.config`、替代設定與 Reef 建置清單。
- [建立第一個自己的應用](../tutorials/first-own-app.md)：自己的 Reef 應用。
