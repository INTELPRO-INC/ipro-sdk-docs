---
title: "快捷鍵、命令與設定"
description: IPRO Workbench 0.1.1 的快捷鍵、IPRO 命令、ipro.* 設定、MCP 工具，以及 IDE 用到的檔案與資料夾。
---

# 快捷鍵、命令與設定

## 快捷鍵 { #shortcuts }

| 動作 | macOS | Windows |
|---|---|---|
| 建置、燒錄並監看 | `Cmd+Alt+R` | `Ctrl+Alt+R` |
| 建置 | `Cmd+Alt+B` | `Ctrl+Alt+B` |
| 燒錄 | `Cmd+Alt+U` | `Ctrl+Alt+U` |
| 序列埠監看 | `Cmd+Alt+M` | `Ctrl+Alt+M` |
| 命令選擇區 | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| 開啟設定 | `Cmd+,` | `Ctrl+,` |
| 儲存（設定、腳位、GATT、檔案） | `Cmd+S` | `Ctrl+S` |

## IPRO 命令一覽 { #commands }

下列命令都可以在命令選擇區輸入 `IPRO` 找到，大部分也在 IPRO 選單、工具列或右鍵選單上。

| 命令 | 用途 |
|---|---|
| IPRO 首頁 | 開啟首頁 |
| 開啟 SDK…／從 GitHub 安裝 SDK… | 開啟或安裝 IPRO SDK |
| 檢查環境／補齊環境 | 重新檢查開發環境；安裝缺少的項目 |
| 選擇應用程式…／新增應用程式…／複製為新應用程式… | 管理應用程式 |
| 選擇開發板…／選擇連接埠… | 更換開發板或序列埠 |
| 選擇工具鏈…／選擇 IntelProCube… | 改用這台電腦上已有的工具 |
| 建置、燒錄並監看／建置／燒錄／停止 | 執行與停止 |
| 重新設定並建置／清除建置 | 重新執行 CMake 設定；刪除建置結果 |
| 重置開發板 | 透過探棒重置板子 |
| 序列埠監看／在另一個連接埠開監看… | 開啟監看 |
| 篩選監看輸出…／顯示監看時間戳記／儲存監看輸出… | 監看的顯示與存檔 |
| 序列埠繪圖 | 把板子印出的數字畫成曲線 |
| 設定（Kconfig）…／Menuconfig／開啟 .config | 修改應用程式設定 |
| 腳位設定… | 設定腳位並產生程式碼 |
| GATT 設定… | 定義 BLE 服務與特性並產生程式碼 |
| 記憶體分佈 | 看記憶體用到哪裡 |
| 分割表／AI 模型… | 分割表檢視；檢查並寫入 NPU 模型 |
| 在板子上執行測試 | 重置板子並收集 Unity 測試結果 |
| RF 測試（DTM）…／Wi-Fi 傳輸速率（iperf）…／功耗… | 射頻、Wi-Fi 傳輸速率與功耗量測 |
| 當機傾印… | 開啟收集過的當機傾印 |
| 暫存器參考 | 查周邊、暫存器與欄位 |
| 請 AI 分析上次當機／連接 AI 助理（MCP）… | AI 助理 |

## 設定一覽 { #settings }

開啟設定後搜尋 `ipro`，可以看到下列項目。

| 設定 | 說明 |
|---|---|
| `ipro.sdk.path` | 開啟的資料夾不是 SDK 時所使用的 IPRO SDK 資料夾 |
| `ipro.tools.base` | IDE 安裝工具的位置，留空表示家目錄的 `IPRO/tools` |
| `ipro.toolchain.prefix` | 交叉編譯前綴，留空則自動尋找 |
| `ipro.flashTool.path` | IntelProCube 資料夾或執行檔，留空則自動尋找 |
| `ipro.build.profile` | 建置組態：Debug、Release、MinSizeRel |
| `ipro.build.generator` | CMake 產生器：auto、Unix Makefiles、Ninja |
| `ipro.build.memoryBudget` | 各記憶體區段的用量上限（百分比），例如 `{ "flash": 90 }` |
| `ipro.build.failOverBudget` | 超出記憶體預算時算建置失敗 |
| `ipro.board.id` | 開發板，auto 表示依應用程式的 `.config`（晶片與板子） |
| `ipro.board.port` | 燒錄與監看用的序列埠，留空則使用探棒的 UART |
| `ipro.flash.baudRate` | IntelProCube 的鮑率 |
| `ipro.run.openMonitor` | 燒錄成功後開啟序列埠監看，預設開啟 |
| `ipro.monitor.baudRate` | 序列埠監看的鮑率，預設 115200 |
| `ipro.monitor.timestamps` | 監看每一行開頭加上收到的時間 |
| `ipro.monitor.filter` | 監看只顯示符合這個正規表示式的行 |
| `ipro.monitor.logToFile` | 把每次監看的完整內容存到應用程式的 `build/logs` |
| `ipro.mcp.enabled`／`ipro.mcp.port` | 提供給 IDE 外 AI 助理的 MCP 伺服器，預設開啟、連接埠 41730 |
| `ipro.macos.probeDownloadMode` | macOS：燒錄時由探棒拉住下載腳位 |
| `ipro.macos.checkQuarantine` | macOS：啟動時檢查工具的隔離標記 |

## MCP 工具一覽 { #mcp-tools }

IDE 外的 AI 助理經 MCP 看到的工具如下（名稱即 MCP 的工具名稱）。內建的 IPRO AI 助理使用同一組工具。

| 工具 | 用途 |
|---|---|
| `ipro_get_target` | SDK、目前的應用程式、開發板、序列埠、環境問題與上次建置結果 |
| `ipro_list_applications` | 列出 SDK 的所有應用程式 |
| `ipro_select_application` | 切換目前的應用程式 |
| `ipro_build` | 建置目前的應用程式，回傳錯誤、警告與記憶體用量 |
| `ipro_get_build_output` | 讀 IPRO Build 或 IPRO Flash 最近的輸出 |
| `ipro_flash` | 燒錄最近一次建置的韌體並開啟監看 |
| `ipro_reset_board` | 透過探棒重置板子 |
| `ipro_read_monitor` | 讀板子在監看上最近印出的行 |
| `ipro_board_tests` | 板子上次開機的韌體與 Unity 測試結果 |
| `ipro_get_settings`／`ipro_set_settings` | 讀取、修改應用程式的 Kconfig 設定 |
| `ipro_get_pins`／`ipro_set_pins` | 讀取、修改腳位設定並產生程式碼 |
| `ipro_get_gatt`／`ipro_set_gatt` | 讀取、修改 GATT 服務並產生程式碼（可先只檢查不寫入） |
| `ipro_memory_map` | 各記憶體區段的用量與最大的函式庫、物件檔 |
| `ipro_partition_table` | 燒錄會寫入的分割表與檢查結果 |
| `ipro_ai_model` | 檢查 NPU 模型能否放進應用程式與分割表 |
| `ipro_crash_dump` | 最近一份當機傾印的例外與呼叫鏈 |
| `ipro_decode_addresses` | 把程式位址解碼成函式、檔案與行號 |
| `ipro_lookup_register` | 依名稱或位址查暫存器 |

## 檔案位置 { #file-locations }

| 位置 | 內容 |
|---|---|
| 家目錄的 `IPRO/tools/<工具>/<版本>` | 「補齊環境」安裝的工具（Windows 為 `%USERPROFILE%\IPRO\tools`） |
| 家目錄的 `IPRO/SDK/<版本>` | 「從 GitHub 安裝 SDK」安裝的 SDK |
| 家目錄的 `.ipro-ide` | IDE 的設定與 MCP 存取權杖（`mcp.json`） |
| `apps/<分類>/<名稱>/build` | 應用程式的建置結果（韌體、ELF、map 檔） |
| `apps/<分類>/<名稱>/build/logs` | 監看的完整記錄（開啟 Log To File 時） |
| `apps/<分類>/<名稱>/build/crash` | 收集的當機傾印 |
| `apps/<分類>/<名稱>/pins.yaml` | 腳位設定；`app_pins.h`、`app_pins.c` 由它產生 |
| `apps/<分類>/<名稱>/gatt.yaml` | GATT 服務；`app_gatt.h`、`app_gatt.c` 由它產生 |
