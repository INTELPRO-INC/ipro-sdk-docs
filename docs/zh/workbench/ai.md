---
title: "AI 助理"
description: 開啟 IPRO Workbench 的 AI 功能、請內建的 IPRO AI 助理修正建置錯誤與分析當機，以及透過 MCP 讓 Claude Code 等 IDE 外的 AI 助理使用 IDE 的工具。
---

# AI 助理

IPRO Workbench 內建 IPRO AI 助理。它不只回答問題，還能自己使用 IDE 的工具：建置、讀建置輸出、燒錄、讀序列埠、改設定與腳位、查記憶體分佈與暫存器、解碼當機位址。IDE 外面的 AI 助理（例如 Claude Code）也能透過 MCP 使用同一組工具。

## 開啟 AI 功能 { #enable }

AI 功能預設關閉。使用前：

<div class="ipro-steps" markdown>

1. **開啟 AI 功能。** 開啟設定（`Cmd+,`／`Ctrl+,`），找到「AI Features」，開啟 AI 功能。

2. **設定模型。** 在同一處設定要使用的模型，例如 Claude Code、Anthropic API 金鑰或 GitHub Copilot。金鑰與帳號登入請自己輸入，不要交給別人代填。

</div>

功能還沒開啟時，按下面任何一個「請 AI…」按鈕，IDE 會先提示「AI 功能目前關閉…」，按 **開啟 AI 功能** 即可。

## 請 AI 修正建置錯誤 { #fix-build }

<div class="ipro-steps" markdown>

1. **請 AI 修正。** 建置失敗時，在錯誤通知上按 **請 AI 修正**。

    **應該看到**：右邊開出 AI 對話，第一則訊息以 `@IPRO` 開頭，帶著錯誤內容。助理會讀建置輸出與原始碼、修正後重新建置，最後用幾句話說明改了什麼。

2. **檢查修改。** 看完說明後，檢查編輯器中被修改的檔案；不同意時可以用復原（`Cmd+Z`／`Ctrl+Z`）或版本控制還原。

</div>

`pins.yaml` 有錯誤或 CMake 設定失敗時，通知上的 **請 AI 修正** 也會請助理處理對應的問題。

## 請 AI 分析當機 { #analyze-crash }

<div class="ipro-steps" markdown>

1. **分析上次當機。** 板子當機或停住時（序列埠監看開著），選 IPRO 選單的 **請 AI 分析上次當機**。

    **應該看到**：對話附上監看的最後幾十行。助理會解出程式位址、讀那裡的程式碼，說明原因與修正方法。

2. **依當機傾印說明。** 收集了[當機傾印](debug.md#crash-dump)時，在「當機傾印」畫面按 **請 AI 解釋**，助理會依完整的呼叫鏈說明。

</div>

## 讓 IDE 外的 AI 助理使用 IDE（MCP） { #mcp }

IPRO Workbench 開著時，會在這台電腦上提供一個 MCP 伺服器，讓 Claude Code、VS Code、Cursor 等 AI 助理使用 IPRO 的工具。助理建置時，輸出照樣顯示在 IDE 的 **IPRO Build**。

<div class="ipro-steps" markdown>

1. **複製設定。** 選 IPRO 選單的 **連接 AI 助理（MCP）…**（或首頁的「AI 助理（MCP）」），選擇你用的助理。

    **應該看到**：通知「已複製 … 的設定。內容含有存取權杖，請勿外流。」清單有 Claude Code、VS Code／GitHub Copilot 與 Cursor：Claude Code 複製的是一行要在終端機執行的 `claude mcp add …` 指令；另外兩個是要貼進設定檔（`.vscode/mcp.json`、`~/.cursor/mcp.json`）的內容。

2. **貼上設定。** 把剪貼簿的內容貼到對應的位置。以 Claude Code 為例，在終端機貼上並執行那一行指令，再啟動 Claude Code。

    **應該看到**：Claude Code 的 MCP 清單中，`ipro` 伺服器為已連線，並列出 `ipro_build`、`ipro_flash` 等工具。

3. **對助理下指令。** 例如「建置並燒錄 ipro_unit_test，讀序列埠告訴我測試結果」。

    **應該看到**：IDE 的 **IPRO Build**、**IPRO Flash** 依序出現建置與燒錄過程，助理最後回報測試通過與失敗的數目。

</div>

!!! warning "重要"
    - MCP 伺服器只在這台電腦上提供（`127.0.0.1`，預設連接埠 41730），每個請求都要帶存取權杖。
    - 權杖存在家目錄的 `.ipro-ide/mcp.json`，只有你的帳號能讀。複製出來的設定含有權杖，不要貼到公開的地方。
    - 不需要時，在設定關閉 `ipro.mcp.enabled`。

MCP 提供的工具見 [MCP 工具一覽](reference.md#mcp-tools)。
