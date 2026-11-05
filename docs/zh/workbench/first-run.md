---
title: "第一次執行"
description: 在 IPRO Workbench 用 SDK 內附的 ipro_unit_test 走完一輪建置、燒錄與看板子輸出，再從開發板的 Hello World 建立自己的第一個應用程式。
---

# 第一次執行

先用 SDK 內附的單元測試 `ipro_unit_test` 走完一輪「建置 → 燒錄 → 看板子輸出」，確認電腦、探棒與 IPRO7AI Reef EVK V4.0 都正常；再建立自己的第一個應用程式 `my_app`，在 **IPRO Monitor** 看到它的輸出。

## 前置需求 { #prerequisites }

- 已完成[安裝 IPRO Workbench](install.md)：「開發環境」每一列都是綠色勾勾，IDE 已開啟 IPRO SDK。
- IPRO 除錯探棒以 USB 接電腦並接上 IPRO7AI Reef EVK V4.0，側邊欄「開發板」列出探棒的兩個連接埠（見[接上開發板](install.md#connect-board)）。

## 執行 ipro_unit_test { #unit-test }

<div class="ipro-steps" markdown>

1. **選應用程式。** 在側邊欄「應用程式」點 **ipro_unit_test**（在 `test` 分類下，可在搜尋框輸入 `unit`）。

    **應該看到**：工具列與狀態列都顯示 `ipro_unit_test`，首頁橫幅寫「ipro_unit_test 已可執行」。

2. **建置、燒錄並監看。** 按首頁的 **建置、燒錄並監看**（macOS `Cmd+Alt+R`，Windows `Ctrl+Alt+R`）。也可以在應用程式清單上按兩下該應用程式。

    **應該看到**，依序是：

    1. 「輸出」的 **IPRO Build** 顯示編譯過程，最後列出 flash、ocram、hbnram 的用量。
    2. **IPRO Flash** 顯示燒錄進度，最後一行是 `[All Success]`。
    3. 下方開出 **IPRO Monitor** 終端機，開發板重新開機，跑完測試後出現 `ALL TESTS PASSED`。

3. **看狀態列與首頁。**

    **應該看到**：狀態列顯示記憶體用量，例如 `flash 36% · ocram 47% · hbnram 82%`；首頁「應用程式」卡片也有用量條。側邊欄「開發板」多一行「執行中：ipro_unit_test（… 建置）」，表示板子跑的正是剛建置的韌體。

</div>

![建置完成後的下方面板：「輸出」選在 IPRO Build，列出編譯到 100% 的過程；左邊「開發環境」每一列都是綠色勾勾，狀態列顯示 flash 36% · ocram 47% · hbnram 82%](../assets/workbench/build-output.svg)

| 輸出 | 內容 |
|---|---|
| IPRO Build | CMake 設定與編譯過程、記憶體用量、與上一次建置相比的大小變化 |
| IPRO Flash | IntelProCube 的燒錄過程；成功時最後一行是 `[All Success]` |
| IPRO Monitor | 板子的序列埠輸出（終端機），可以直接打字送指令給板子 |

任何一步失敗，IDE 都會停在那一步並跳出說明與處理按鈕，例如「前往錯誤」「重試」「選擇連接埠」。常見訊息見[疑難排解](troubleshooting.md#messages)。

!!! tip "只做其中一步"
    只想建置、只想燒錄或只想開監看時，用工具列上的個別按鈕，或快捷鍵：建置 `Cmd+Alt+B`，燒錄 `Cmd+Alt+U`，監看 `Cmd+Alt+M`（Windows 把 `Cmd` 換成 `Ctrl`）。

## 建立自己的應用程式 { #own-app }

<div class="ipro-steps" markdown>

1. **開啟新增應用程式。** 在「應用程式」清單上方按 **＋**（新增應用程式…），或首頁的「從範本或範例新增應用程式」。

2. **填寫並建立。** 「從何開始」選 **開發板的 Hello World**，開發板選 **IPRO7AI Reef**，名稱輸入 `my_app`，分類保留 `user`，按 **建立**。

    名稱只能用小寫英文字母、數字與底線，並以字母開頭。

    **應該看到**：清單多了 `user/my_app`，它成為目前的應用程式，編輯器打開它的 `main.c`。

3. **執行。** 按 **建置、燒錄並監看**。

    **應該看到**：IPRO Monitor 出現 `Hello from my_app`。

</div>

![「新增 IPRO 應用程式」對話框：從何開始選了開發板的 Hello World，開發板是 IPRO7AI Reef (IPRO7AI)，名稱 my_app，分類 user，右下是建立與取消按鈕](../assets/workbench/new-app.svg)

要從現有的範例開始，在清單的應用程式上按右鍵，選 **複製為新應用程式…**，或在「從何開始」選 **複製現有的應用程式**。新的應用程式放在 SDK 的 `apps/<分類>/<名稱>`。

## 應用程式的右鍵選單 { #app-menu }

在「應用程式」清單的應用程式上按右鍵，可以直接做這些事：

![在應用程式清單的 ipro_unit_test 上按右鍵開出的選單：建置、燒錄並監看、建置、燒錄、除錯、設定（Kconfig）…、腳位設定…、重新設定並建置、清除建置、記憶體分佈、分割表、AI 模型…、功耗…、Menuconfig、開啟 .config、複製為新應用程式…、開啟所在資料夾、複製路徑](../assets/workbench/app-menu.svg)

| 項目 | 用途 |
|---|---|
| 建置、燒錄並監看／建置／燒錄／除錯 | 與工具列相同 |
| 設定（Kconfig）…／Menuconfig／開啟 .config | 修改應用程式的設定，見[開發應用程式](develop.md#kconfig) |
| 腳位設定… | 指定 GPIO 的功能並產生程式碼 |
| 重新設定並建置／清除建置 | 重新執行 CMake 設定後建置；刪除建置結果 |
| 記憶體分佈 | 看記憶體用到哪裡 |
| 分割表／AI 模型…／功耗… | 見[燒錄與開發板](flash.md)與[測試與量測](measure.md#power) |
| 複製為新應用程式… | 以這個應用程式為起點建立新的應用程式 |
| 開啟所在資料夾／複製路徑 | 在檔案總管（Finder）中開啟，或複製資料夾路徑 |

## 下一步 { #next-steps }

- [開發應用程式](develop.md)：修改設定、設定腳位、處理建置錯誤，以及看記憶體用到哪裡。
- [燒錄與開發板](flash.md)：燒錄時的檢查、分割表與 AI 模型。
- [序列埠監看](monitor.md)：篩選、時間戳記、存檔與序列埠繪圖。
- 任何一步失敗時，見[疑難排解](troubleshooting.md)。
