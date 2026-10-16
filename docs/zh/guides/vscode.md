---
title: "VS Code Extension"
description: IPRO SDK Extension 3.3.0 的功能、建置與燒錄流程、設定、命令，以及搭配 SDK V2.1.0 的方式
migrate_from:
  - "vscode-extension.html"
not_migrated:
  - "vscode-extension.html#installation — 安裝步驟在 get-started/windows.md"
  - "vscode-extension.html#cli-tools — IntelProCube 命令列屬於燒錄與序列埠頁"
---

# VS Code Extension

IPRO SDK Extension 3.3.0（識別碼 `ipro.ipro-sdk-extension`）把 FreeRTOS 專案瀏覽、CMake 建置、IntelProCube 燒錄、序列埠主控台與記憶體分析整合到 VS Code，需要 VS Code 1.102 以上。Extension 不包含在 SDK 套件內，與 SDK、Windows 安裝包分開計版；安裝步驟見 [Windows 安裝與 VS Code](../get-started/windows.md)。

!!! abstract "重點"
    - 版本 3.3.0，設定使用 `ipro.*` 命名空間；舊文件中的 `devtool.*` 設定與 `IPRO SDK:` 命令名稱已不適用。
    - SDK V2.1.0 以資料夾匯入，`.tar.gz` 需先解壓。
    - 燒錄使用 IntelProCube；主控台使用 Extension 內建的 serialport，燒錄與主控台的鮑率分開設定。
    - 3.3.0 沒有一般的 GDB debug adapter。

## 功能 { #features }

| 功能 | 用途 |
|---|---|
| Projects／Target | 依分類瀏覽專案、釘選與最近使用；顯示目前專案、Profile、UART、Probe 與工具狀態 |
| Control Center | 集中顯示連線、主控台鮑率與操作狀態，提供建置、燒錄、監看與元件更新入口 |
| Build／Batch Build | CMake 設定與 Make／Ninja 建置，debug／release／size Profile，錯誤可從 Problems 跳到原始碼，整合 `compile_commands.json` |
| Menuconfig | 圖形化編輯 `.config`，可載入 defconfig |
| Flash／Monitor | 以 IntelProCube 燒錄；內建 serialport 主控台可在 Windows 執行 |
| Analysis／Debug | Memory Map、Decode Crash Report、Pin Function Lookup；Register Explorer 需相容的 CCI 連線 |

SDK 建置只讀 `.config`，不解析 Kconfig 的 `select` 與 `depends on`。用 Menuconfig 修改後，請確認相依選項都已寫入 `.config`，見[建置系統與設定](build-system.md#configuration)。

## 控制中心 { #control-center }

按 F1，執行 `IPRO: Open Control Center`。控制中心顯示目前的 SDK 與專案、UART、設定與實際的主控台鮑率，並依工作狀態啟用各項操作。開啟面板本身不會燒錄或重置開發板。控制中心在 3.2.4 加入，3.3.0 再加上元件更新入口。

## 第一次建置 { #workflow }

<div class="ipro-steps" markdown>

1. 執行 `IPRO: Go to Project…`，選擇 platform 分類的 `ipro7ai_reef_demo`。
2. 執行 `IPRO Config: Select Build Profile`，選擇 debug、release 或 size。
3. 執行 `IPRO Setup: Run Diagnostics`，確認 SDK、編譯器、CMake、Ninja 與 Python 的實際路徑。
4. 執行 `IPRO: Build`，在 Terminal 查看結果；錯誤可從 Problems 跳到原始碼。
5. 確認產生 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin` 與 `.elf`。

</div>

Windows 安裝包預設使用 Ninja；`ipro.generator` 可設為 `auto`、`make` 或 `ninja`。`IPRO: Batch Build` 一次建置多個選定的專案。SDK 或工具路徑變更後，先 Clean 再重新建置，避免沿用舊的快取。

## 燒錄與主控台 { #flash }

<div class="ipro-steps" markdown>

1. 以 `IPRO Setup: Select Flash Tool` 選擇 IntelProCube，或設定 `ipro.flashToolPath`。
2. 接上開發板，執行 `IPRO: Select Serial Port`，選擇 Probe 的 UART 埠。CCI 埠用於暫存器存取，不能用於主控台或燒錄。
3. 以 `IPRO Config: Configure Flash…` 核對晶片配置、燒錄目標、分割表與鮑率。晶片配置必須符合實際的板子，例如 IPRO7AI Reef EVK 使用 `IPRO7AI`。
4. 執行 `IPRO: Flash`，確認燒錄工具的驗證與成功訊息。Extension 會先釋放自己的主控台連線；其他程式占用序列埠時要先關閉。
5. 以 `IPRO Config: Set Monitor Baud Rate` 設定與韌體相同的主控台鮑率，再執行 `IPRO: Serial Monitor`。改鮑率後關閉再重開主控台。

</div>

| 設定 | 意義 |
|---|---|
| `ipro.baudRate` | 燒錄鮑率，預設 921600 |
| `ipro.monitorBaudRate` | 主控台鮑率，預設 115200，必須與韌體一致 |
| `ipro.chipVariant` | 板子的燒錄配置，不是建置 Profile |

多數應用的主控台是 115200 baud；`ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_epd_el036` 等應用使用 921600，以應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 為準。

3.2.0 起主控台使用內建 serialport，Windows 上不依賴 SDK 的 `serial_monitor.py`，開啟時也不會自動重開機。要重開機可執行 `IPRO: Reset Board`，或在韌體主控台輸入 `reboot`。命令列燒錄見[燒錄與序列埠](../get-started/flash-and-monitor.md)。

## 記憶體與除錯工具 { #memory-map }

- `IPRO Analyse: Memory Map`：建置後檢視各記憶體區域、元件用量與前後兩次建置的差異，可匯出 CSV 或 Markdown。是否放得下仍以連結器輸出與實際分割表為準。
- `IPRO Analyse: Decode Crash Report`：把例外的回溯轉成原始碼位置。
- `IPRO Debug: Pin Function Lookup`：查詢腳位功能。
- `IPRO Debug: Register Explorer`：需要相容的 Probe、CCI 連線與正確的板端設定。

Extension 3.3.0 沒有一般的 GDB debug adapter；安裝 OpenOCD 也不代表可以直接按 F5 做原始碼除錯。

## 元件更新 { #component-updates }

F1 執行 `IPRO Setup: Update Components`，或從控制中心進入。

| 來源 | 行為 |
|---|---|
| Extension VSIX | 安裝選取的 VSIX 後重新載入視窗；不更新 SDK 或工具 |
| SDK ZIP | 解壓並驗證 SDK 結構，可輸入 INTELPRO 提供的 SHA-256 |
| SDK Folder | 選取已解壓、含 `CMakeLists.txt`、`apps`、`bsp` 的根目錄；`.tar.gz` 與 `.7z` 要先自行解壓 |
| SDK Git | 以有權限的 HTTPS 或 SSH 儲存庫與 branch／tag 建立快照，記錄 commit；SSH 信任與認證要事先完成 |

- 選擇來源後，指定版本儲存的上層目錄與尚未存在的新版本名稱；Output → IPRO SDK 顯示進度與紀錄。
- 匯入完成後可在新視窗開啟；SDK Root、工具鏈與原視窗不會自動切換。先執行 Diagnostics 與官方範例的建置，再逐項移轉自己的修改，並保留舊 SDK 以便回復。
- 每個版本目錄下有 `sdk\`（SDK 根目錄）、`update.json`（來源、時間、checksum 或 Git commit）與 `update.log`。失敗或取消時保留未完成的目錄與紀錄，重試時使用新名稱。
- Git 匯入是快照，不是可以直接 pull 的工作目錄；不支援 submodule、未解析的 LFS pointer 與符號連結，也不會更新工具鏈。

## 命令 { #shortcuts }

F1 或 Ctrl+Shift+P 開啟命令面板。3.3.0 沒有預設的燒錄與主控台快捷鍵，可自行綁定；Ctrl+Shift+B 使用 VS Code 的建置工作設定。

| 命令 | 用途 |
|---|---|
| `IPRO: Open Control Center` | 開啟控制中心 |
| `IPRO Setup: Update Components` | 更新 VSIX、SDK ZIP、資料夾或 Git 快照 |
| `IPRO Setup: Set SDK Root` | 設定 SDK 根目錄 |
| `IPRO Setup: Run Diagnostics` | 檢查 SDK 與工具路徑 |
| `IPRO: Go to Project…` | 搜尋並切換專案 |
| `IPRO Config: Select Build Profile` | 選擇 debug、release 或 size |
| `IPRO: Build` | 建置目前專案 |
| `IPRO: Clean` | 清除目前專案的建置產物 |
| `IPRO: Batch Build` | 一次建置多個專案 |
| `IPRO Config: Menuconfig` | 編輯設定 |
| `IPRO Config: Configure Flash…` | 設定晶片配置與燒錄參數 |
| `IPRO: Select Serial Port` | 選擇 UART |
| `IPRO Config: Set Monitor Baud Rate` | 設定主控台鮑率 |
| `IPRO: Flash` | 燒錄韌體 |
| `IPRO: Serial Monitor` | 開啟主控台 |
| `IPRO: Close Serial Monitor` | 關閉主控台並釋放序列埠 |
| `IPRO: Build, Flash & Monitor` | 依序建置、燒錄並開啟主控台 |
| `IPRO: Reset Board` | 透過相容的 Probe 重置開發板 |
| `IPRO Analyse: Memory Map` | 分析記憶體用量 |
| `IPRO Analyse: Decode Crash Report` | 解析例外與回溯 |
| `IPRO Debug: Pin Function Lookup` | 查詢腳位功能 |
| `IPRO Debug: Register Explorer` | 透過 CCI 檢視暫存器 |

## 常見問題 { #faq }

| 現象 | 處理 |
|---|---|
| 找不到 IPRO 命令 | 核對 VSIX 版本、Profile、Workspace Trust 與 SDK 根目錄，再重新載入視窗 |
| 切換 SDK Root 沒有生效 | 工作區與資料夾設定可能優先於 User 設定；以 Diagnostics 顯示的實際路徑為準 |
| 主控台亂碼或仍使用舊鮑率 | 核對韌體的主控台鮑率與 `ipro.monitorBaudRate`，關閉後重開主控台 |
| Probe 偵測成功但 CCI 不通 | USB 列舉成功不代表板端 CCI 已連通，另行檢查接線與板端設定 |
| 找不到燒錄工具 | 以 `IPRO Setup: Select Flash Tool` 選擇，確認 IntelProCube 目錄中有 `ipro_iot_tool.exe` |

## 版本紀錄 { #version }

| 版本 | 變更 |
|---|---|
| 3.3.0 | 元件獨立更新 |
| 3.2.4 | 控制中心 |
| 3.2.3 | 改善主控台與燒錄之間的序列埠交接，UART 與 CCI 埠分開選擇 |
| 3.2.2 | 主控台鮑率獨立設定 |
| 3.2.1 | Windows 工具路徑固定設定 |
| 3.2.0 | 內建 serialport 主控台 |

SDK 原始碼套件、Extension VSIX 與 Windows 完整安裝包分開計版。SDK 套件內沒有 VSIX；實際版本以取得的安裝包與 Extensions 面板顯示為準。

## 搭配 SDK V2.1.0 { #sdk-2-1-0 }

<div class="ipro-steps" markdown>

1. 依 [Windows 安裝與 VS Code](../get-started/windows.md#sdk-2-1-0) 下載、校驗並解壓 SDK V2.1.0 到新的目錄。
2. 以 `IPRO Setup: Update Components` 匯入解壓後的資料夾，或以 `IPRO Setup: Set SDK Root` 直接選擇該目錄。
3. 重新開啟 SDK，執行 `IPRO Setup: Run Diagnostics`。

</div>

- V2.1.0 的 FreeRTOS 應用只支援 IPRO7；IPRO6S 開發請保留 SDK V2.0.1，見 [IPRO6S](../hardware/chips/ipro6s.md)。
- SDK 的 README 指定 GCC 14 工具鏈。Windows 安裝包內的工具鏈版本見 [Windows 安裝與 VS Code](../get-started/windows.md)，使用 V2.1.0 前請確認相容，並在新版本完成建置與板上驗證前保留可用的舊環境。
- 在 Windows 以 Make 建置時，`project.build` 使用 PATH 上的 `cmake`；請確認其版本。

## 相關文件 { #related }

- [Windows 安裝與 VS Code](../get-started/windows.md)：安裝 Extension 並指向 SDK V2.1.0。
- [燒錄與序列埠](../get-started/flash-and-monitor.md)：IntelProCube 命令列工具與各板燒錄設定。
- [建置系統與設定](build-system.md)：`.config` 與替代設定。
