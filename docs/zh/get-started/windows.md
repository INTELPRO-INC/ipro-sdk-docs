---
title: "Windows 安裝與 VS Code"
description: 在 Windows 上以 IPRO SDK Online Setup 安裝工具與 VS Code Extension，手動加入 SDK V2.2.0，建置 IPRO7AI Reef EVK 的開箱韌體，並以 ipro_iot_tool.exe 燒錄、以終端程式開啟主控台。
migrate_from:
  - "windows-installation.html"
  - "vscode-extension.html#installation"
not_migrated:
  - "windows-installation.html#overview"
  - "windows-installation.html#package-contents"
  - "windows-installation.html#install-modes"
  - "windows-installation.html#full-install"
  - "windows-installation.html#extension-only"
  - "windows-installation.html#sdk-only"
  - "windows-installation.html#settings"
---

# Windows 安裝與 VS Code

在 Windows 上以 IPRO SDK Online Setup 安裝工具鏈、建置工具、IntelProCube 與 VS Code Extension，手動加入 SDK V2.2.0，建置 IPRO7AI Reef EVK 的開箱韌體 `ipro7ai_reef_demo`，再以 `ipro_iot_tool.exe` 燒錄並在 COM 埠上看到主控台。

!!! info "安裝程式不會安裝 V2.2.0"
    Online Setup 的套件清單仍以 SDK V1.2.1 為 stable 版本。請以安裝程式安裝工具與 Extension，再依[加入 SDK V2.2.0](#get-sdk) 手動加入 SDK。

## 前置需求 { #requirements }

- Windows x64，可連上 GitHub（Online Setup 從公開的套件清單與 GitHub Release 下載元件）。
- VS Code 1.102 以上（也可以讓安裝程式下載）。
- IPRO7AI Reef EVK、USB-C 線、主控台線，見[需要準備](index.md#what-you-need)。
- 相容 V2.2.0 的工具鏈：V2.2.0 以 GCC 14 建置，安裝程式選的工具鏈是依 SDK V1.2.1 宣告的相容組合。請向 INTELPRO 確認並取得相容 V2.2.0 的 Windows 工具鏈。

## 安裝工具 { #online-3-4-0 }

<div class="ipro-steps" markdown>

1. **下載安裝程式**：從 [Online Setup 3.4.0 Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/online-installer-v3.4.0) 下載 `IPRO-SDK-Online-Setup-3.4.0.exe`，不需登入 GitHub。

2. **選擇目錄**：執行安裝程式，在 **Select Destination Location** 填入一個尚不存在的新資料夾（安裝根目錄）。

3. **選擇 Full environment**：在 **Choose packages** 選 **Full environment**。它安裝 SDK、RISC-V 工具鏈、建置工具（CMake、Ninja、Python）、IntelProCube、OpenOCD 與 VS Code Extension 3.3.0。版本保持 **latest**：latest 是各元件標示為 stable／相容的版本，不是 GitHub 上最新的 Release。

4. **選擇附加工作**：尚未安裝 VS Code 時勾選 **Install VS Code from Microsoft if absent**；保持勾選 **Install the selected Extension into VS Code**；要在一般終端機直接執行工具時勾選 **Add installed tools to user PATH**。

5. **核對摘要後安裝**：在 **Ready to Install** 確認目錄、模式與版本後按 **Install**。

6. **重新開啟 VS Code 與終端機**，讓新的 PATH 生效。

</div>

## 加入 SDK V2.2.0 { #get-sdk }

<div class="ipro-steps" markdown>

1. **下載**：從 [IPRO-SDK-V2.2.0 Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) 下載 `IPRO-SDK-V2.2.0.tar.gz`，記下頁面公布的 SHA-256 值。

2. **校驗**：在 PowerShell 計算雜湊值。

    ```powershell
    Get-FileHash .\IPRO-SDK-V2.2.0.tar.gz -Algorithm SHA256
    ```

    `Hash` 欄的 64 個十六進位字元應與 Release 頁面的值相同（大小寫不影響）。

3. **解壓到新目錄並確認版本**

    ```powershell
    tar -xzf .\IPRO-SDK-V2.2.0.tar.gz
    Get-Content .\IPRO-SDK-V2.2.0\VERSION.txt
    ```

    ```text
    IPRO SDK Release
    ========================================
    IPRO7: IPRO-SDK-V2.2.0
    IPRO6: IPRO-SDK-V2.2.0

    Release Date: 2026-11-03
    Base Commit: 60afd4ab
    ```

    `IPRO-SDK-V2.2.0\` 內應有 `CMakeLists.txt`、`apps\` 與 `bsp\`。

</div>

## 設定 VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **確認 Extension 已安裝**：在 Extensions 面板搜尋 `@installed IPRO`，應看到 IPRO SDK Extension（識別碼 `ipro.ipro-sdk-extension`）。

2. **開啟 SDK**：以 **File → Open Folder…** 開啟 `IPRO-SDK-V2.2.0` 根目錄，確認來源後允許 Workspace Trust。

3. **指定 SDK 根目錄**：按 ++f1++ 執行 `IPRO Setup: Set SDK Root`，選擇同一個目錄。

4. **檢查環境**：執行 `IPRO Setup: Run Diagnostics`，確認 SDK 根目錄、編譯器、CMake、Python 與燒錄工具的路徑。編譯器應指向相容 V2.2.0 的工具鏈，燒錄工具所在的資料夾就是後面步驟的 `<IntelProCube>`。

5. **建置開箱韌體**：執行 `IPRO: Go to Project…`，在 platform 分類選擇 `ipro7ai_reef_demo`，再執行 `IPRO: Build`。

</div>

Extension 的其他命令與設定見 [VS Code Extension](../guides/vscode.md)。

## 燒錄 { #flash }

<div class="ipro-steps" markdown>

1. **接線**：SW7 撥到 CAM、SW8 撥到 PWR，主控台線接 U6，接上 USB-C，見[設定開關與接線](first-app-freertos.md#connect)。

2. **找出 COM 埠**：開啟「裝置管理員」→「連接埠 (COM 和 LPT)」，插上轉接器後多出來的就是主控台，例如 `COM5`。IPRO Debug Probe 會多出兩個 COM 埠，見[辨識序列埠](flash-and-monitor.md#ports)。

3. **進入下載模式**：按住 SW1（BOOT），按一下 SW2（RESET），再放開 SW1。

4. **燒錄**：在 PowerShell 切換到 IntelProCube 資料夾執行：

    ```powershell
    cd <IntelProCube>
    .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
        --port COM5 --baudrate 921600 `
        --pt chips/ipro7/partition/partition_cfg_2M.toml `
        --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

    輸出的最後一行是 `[All Success]` 才算成功；工具失敗時也以 0 結束。參數說明見[燒錄與序列埠](flash-and-monitor.md#flash-tool)。

</div>

## 主控台 { #console }

<div class="ipro-steps" markdown>

1. **開啟終端程式**：在 PuTTY 選 **Serial**，Serial line 填 `COM5`，Speed 填 `115200`，按 **Open**。也可以用 Tera Term，或 VS Code Extension 的 `IPRO: Serial Monitor`（以 `IPRO: Select Serial Port` 選 COM 埠）。

2. **重置**：按 SW2（RESET）。視窗出現開機訊息 `IPRO7AI Reef carrier demo`，按 ++enter++ 出現 `ipro />`。

3. **自我檢查**：輸入 `reef selftest`，預期輸出見[第一個 FreeRTOS 應用](first-app-freertos.md#verify)。

</div>

燒錄前先關閉終端程式，否則 `ipro_iot_tool.exe` 開不了 COM 埠。

## 命令列建置 { #command-line }

SDK 沒有提供 Windows 命令列的建置流程，`build_freertos.sh` 與 `tools/serial_monitor.py` 需要 bash 與 POSIX termios，不能在 Windows 上執行。建置程式在 Windows 上的需求：

- `cmake` 與 `python` 在 PATH 上（建置在 Windows 上呼叫 `python`，不是 `python3`）。
- 執行 `make` 時以 `CROSS_COMPILE=<工具鏈目錄>\bin\riscv64-unknown-elf-`（含最後的連字號）指定工具鏈：應用 `.config` 中的 `CONFIG_CROSS_COMPILE` 是 Unix 路徑 `/opt/toolchain/...`，Windows 上沒有預設路徑。
- GNU Make：Online Setup 的建置工具套件包含 CMake、Ninja 與 Python，不含 make。

## 確認結果 { #verify }

- `IPRO: Build` 完成後產生：

    ```text
    apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

- `ipro_iot_tool.exe` 的輸出結尾為 `[All Success]`。
- 重置後終端程式顯示開機訊息與 `ipro />`，`reef selftest` 依序點亮 LED 並發出 1 kHz 短音。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 安裝後的 SDK 是 V1.2.1 | 套件清單尚未登錄 V2.x | 依[加入 SDK V2.2.0](#get-sdk) 手動加入，並以 `IPRO Setup: Set SDK Root` 指向它 |
| Windows 顯示未知發行者或 SmartScreen 警告 | 安裝程式沒有程式碼簽章 | 依公司的資訊安全規定處理；不要停用防護 |
| Diagnostics 仍顯示舊的 SDK 路徑 | 工作區或使用者設定中的 SDK 根目錄指向舊版 | 執行 `IPRO Setup: Set SDK Root` 後重新執行 Diagnostics |
| 找不到 IPRO 命令 | Extension 不在目前的 VS Code Profile，或工作區未受信任 | 確認 Extension、Profile 與 Workspace Trust，執行 `Developer: Reload Window` |
| `IPRO: Build` 找不到編譯器或編譯失敗 | 工具鏈不相容 V2.2.0，或路徑錯誤 | 向 INTELPRO 取得相容 V2.2.0 的工具鏈，在 Diagnostics 確認路徑 |
| 裝置管理員沒有新的 COM 埠 | USB 線只能充電，或缺轉接器的驅動程式 | 換線；安裝轉接器廠商的驅動程式；Debug Probe 請洽 INTELPRO |
| `ipro_iot_tool.exe` 沒有 `[All Success]` | 板子不在下載模式，或 COM 埠被終端程式占用 | 關閉終端程式；重新以 SW1＋SW2 進入下載模式 |
| `flash jedec id: 00000000` | 沒有加 `--chip-variant IPRO7AI` | 加上後重新燒錄 |
| 終端程式亂碼或沒有輸出 | 鮑率不是 115200、板子仍在下載模式，或 RX／TX 接反 | 以 115200 開啟；按 SW2；對調 RX 與 TX |

## 下一步 { #next-steps }

- [第一個 FreeRTOS 應用](first-app-freertos.md)：開箱韌體的自我檢查與指令。
- [燒錄與序列埠](flash-and-monitor.md)：其他下載模式、分割表、boot2 與 `mfg` 資料。
- [VS Code Extension](../guides/vscode.md)：Extension 的命令與設定。
