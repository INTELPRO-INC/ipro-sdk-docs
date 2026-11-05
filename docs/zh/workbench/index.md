---
title: "IPRO Workbench"
description: INTELPRO 為 IPRO 系列晶片提供的整合開發環境：在同一個視窗建置 IPRO SDK 的應用程式、燒錄開發板、監看序列埠，並提供腳位設定、記憶體分析、當機分析、測試量測與 AI 助理。
---

# IPRO Workbench

IPRO Workbench 是 INTELPRO 為 IPRO 系列晶片提供的整合開發環境（IDE）。在同一個視窗裡就能建置 IPRO SDK 的應用程式、燒錄到開發板、看板子的序列埠輸出，並提供 C/C++ 程式碼導覽、腳位設定、記憶體分析、當機分析、板上測試、RF 與功耗量測，以及能自己動手建置與燒錄的 AI 助理。

本節對應 IPRO Workbench 0.1.0，以 [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) 加上 IPRO 除錯探棒（IPRO Debug Probe）示範。每一步都寫「做什麼」和「應該看到什麼」；畫面和本節不一樣時，請看[疑難排解](troubleshooting.md)。習慣在 VS Code 開發時，見 [VS Code Extension](../guides/vscode.md)。

!!! info "取得方式"
    IPRO Workbench 0.1.0 預覽版的 macOS 與 Windows 安裝檔在 [GitHub 的 IPRO Workbench 發行頁](https://github.com/INTELPRO-INC/ipro-workbench/releases/tag/v0.1.0)，不需要 GitHub 帳號；安裝步驟見[安裝 IPRO Workbench](install.md)。尚未提供 Linux 版。

## 能做什麼 { #features }

| 功能 | 說明 |
|---|---|
| [補齊開發環境](install.md#environment) | 自動檢查 SDK、RISC-V 工具鏈、CMake、Python、IntelProCube 與開發板，缺的項目一鍵從 GitHub 安裝。 |
| [建置、燒錄並監看](first-run.md#unit-test) | 一個按鍵完成建置、燒錄與開啟序列埠監看；每一步的輸出分開顯示，任何一步失敗就停下並說明原因。 |
| [應用程式管理](first-run.md#own-app) | 依分類列出 SDK 裡的應用程式；從開發板的 Hello World 或現有範例建立新的應用程式。 |
| [設定（Kconfig）](develop.md#kconfig) | 以表單修改應用程式的 `.config`，只寫入你改的項目，並列出每個項目的說明與相依條件。 |
| [腳位設定](develop.md#pins) | 在封裝圖與表格上指定每支 GPIO 的功能，檢查衝突與開發板上的接線，並產生初始化程式碼。 |
| [記憶體分析](develop.md#memory) | 列出 flash、ocram、hbnram 各被哪些函式庫、物件檔與符號用掉；比較每次建置的大小變化，並可設定記憶體預算。 |
| [燒錄與開發板](flash.md) | 分割表檢視與檢查、辨識板子的 Flash、核對板子上執行的韌體、把 AI 模型寫入 mfg 分割區。 |
| [序列埠監看](monitor.md) | 篩選、時間戳記、存檔與完整記錄、序列埠繪圖，以及在第二個連接埠同時監看。 |
| [除錯與分析](debug.md) | 當機位址自動解碼成原始碼行號、收集並分析當機傾印、查暫存器與欄位。 |
| [測試與量測](measure.md) | 板上測試結果進入「測試」檢視、RF 測試（BLE DTM）、功耗曲線與電池壽命估算。 |
| [AI 助理](ai.md) | 內建的 IPRO AI 助理會自己建置、讀輸出、改設定與腳位；IDE 外的 AI 助理（例如 Claude Code）也能透過 MCP 使用同一組工具。 |

## 視窗各區 { #window }

![IPRO Workbench 視窗：上方是工具列，左邊是 IPRO 側邊欄的應用程式、開發板與開發環境，中間是 IPRO 首頁，下方是「輸出」面板的建置過程，最下面是狀態列；綠色圓圈 1 到 5 標示各區](../assets/workbench/window-areas.svg)

| 編號 | 區域 | 用途 |
|---|---|---|
| 1 | 工具列 | 目前的應用程式、開發板與連接埠，以及建置、燒錄、監看等按鈕。按應用程式或開發板的名稱可以更換。 |
| 2 | IPRO 側邊欄 | 「應用程式」列出 SDK 裡的應用程式；「開發板」顯示探棒、連接埠與板子正在執行的韌體；「開發環境」逐項列出檢查結果。 |
| 3 | 編輯區 | IPRO 首頁、原始碼，以及設定、腳位、記憶體分佈、分割表等檢視都開在這裡。 |
| 4 | 下方面板 | 「輸出」的 **IPRO Build**、**IPRO Flash**、**IPRO Setup** 分別顯示建置、燒錄與安裝過程；「終端機」裡的 **IPRO Monitor** 是序列埠監看。 |
| 5 | 狀態列 | 目前的應用程式、開發板與記憶體用量；環境有缺項時會在這裡提醒。 |

IPRO 首頁最上方的橫幅永遠提示「下一步」：還沒開 SDK 時請你開啟 SDK，環境缺項時請你補齊環境，一切就緒後則提示可以執行。

## 支援的環境 { #requirements }

| 項目 | 內容 |
|---|---|
| 電腦 | macOS 12 以上（Apple Silicon）；Windows 11（x64） |
| IPRO SDK | IPRO SDK 2.2.0 |
| 晶片 | IPRO7、IPRO7AI |
| 開發板 | IPRO7AI Reef EVK V4.0，見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) |
| 燒錄與連線 | IPRO 除錯探棒（USB），燒錄使用 IntelProCube |
| 介面語言 | 繁體中文、英文 |

## 整體流程 { #workflow }

<div class="ipro-steps" markdown>

1. **安裝並補齊環境。** 安裝 IPRO Workbench，按 **補齊環境** 安裝缺少的工具，再開啟 SDK、接上開發板，見[安裝 IPRO Workbench](install.md)。

2. **第一次執行。** 用 `ipro_unit_test` 走完一輪建置、燒錄與看板子輸出，再從開發板的 Hello World 建立自己的應用程式，見[第一次執行](first-run.md)。

3. **開發應用程式。** 以表單修改 `.config`、設定腳位並產生初始化程式碼、處理建置錯誤，並看記憶體用到哪裡，見[開發應用程式](develop.md)。

4. **燒錄。** 燒錄前後 IDE 會檢查分割表與板子的 Flash、核對板子上執行的韌體，也能把 AI 模型寫入 mfg 分割區，見[燒錄與開發板](flash.md)。

5. **看序列埠輸出。** 在 **IPRO Monitor** 看板子的輸出、送指令給板子，並可篩選、存檔或畫成曲線，見[序列埠監看](monitor.md)。

6. **除錯與量測。** 當機位址自動解碼成原始碼行號，需要時收集當機傾印、查暫存器，再於板子上執行測試、以 BLE DTM 做 RF 測試、看功耗曲線，見[除錯與分析](debug.md)與[測試與量測](measure.md)。

</div>

## 完整操作手冊 { #manual }

《IPRO Workbench 操作手冊》V1.1 的 PDF 附在 GitHub 的 0.1.0 發行版：[繁體中文版](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.1.0/IPRO-Workbench-Operation-Manual-V1.1-zh-TW.pdf)（52 頁）、[英文版](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.1.0/IPRO-Workbench-Operation-Manual-V1.1-en.pdf)（53 頁）。本節依這份手冊整理；要離線閱讀或列印時，請下載 PDF。

## 本節頁面 { #pages }

<div class="grid cards" markdown>

-   **[安裝 IPRO Workbench](install.md)**

    ---

    下載與核對安裝檔、在 macOS 與 Windows 安裝、介面語言、補齊開發環境、開啟 SDK、接上開發板。

-   **[第一次執行](first-run.md)**

    ---

    用 `ipro_unit_test` 走完建置、燒錄與監看，建立自己的應用程式，以及應用程式的右鍵選單。

-   **[開發應用程式](develop.md)**

    ---

    修改設定（Kconfig）、設定腳位並產生程式碼、建置與錯誤、記憶體分佈與記憶體預算。

-   **[燒錄與開發板](flash.md)**

    ---

    燒錄前後的檢查、分割表、開發板的 Flash 與韌體核對、把 AI 模型寫入 mfg 分割區。

-   **[序列埠監看](monitor.md)**

    ---

    開啟監看與輸入指令、篩選、時間戳記、存檔與完整記錄、序列埠繪圖、同時監看另一個連接埠。

-   **[除錯與分析](debug.md)**

    ---

    當機位址自動解碼、收集與分析當機傾印、暫存器參考。

-   **[測試與量測](measure.md)**

    ---

    板上測試進入「測試」檢視、RF 測試（BLE DTM）、功耗曲線與 CR2032 電池壽命估算。

-   **[AI 助理](ai.md)**

    ---

    開啟 AI 功能、請 AI 修正建置錯誤與分析當機，以及讓 IDE 外的 AI 助理經 MCP 使用 IDE。

-   **[疑難排解](troubleshooting.md)**

    ---

    畫面上的訊息、工具列與側邊欄的狀態、macOS 與 Windows 特有的狀況，以及回報問題時要附的資訊。

-   **[快捷鍵、命令與設定](reference.md)**

    ---

    快捷鍵、IPRO 命令、`ipro.*` 設定、MCP 工具與 IDE 用到的檔案位置。

</div>

## 本版範圍 { #limitations }

本節對應 IPRO Workbench 0.1.0 預覽版。這一版有下列限制：

- 安裝檔沒有 Apple 或 Microsoft 的簽章，第一次開啟或安裝時作業系統會提示（處理方式見[安裝](install.md#install)）。
- 以 JTAG 除錯的功能尚未開放。當機時請改用[除錯與分析](debug.md)的當機解碼與當機傾印。
- 自動更新預設關閉。新版本請到發行頁下載後重新安裝。
- 序列埠監看的[篩選](monitor.md#filter)也會擋住 IDE 自己讀取的內容（建置戳記、分割表、測試結果）。做這些步驟前請先取消篩選。
- 尚未提供 Linux 版。
