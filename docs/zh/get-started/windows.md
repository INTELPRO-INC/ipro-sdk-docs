---
title: "Windows 安裝與 VS Code"
description: 以 Online Installer 安裝 Windows 開發工具與 VS Code Extension，再手動加入 SDK V2.1.0 並建置第一個專案。
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

在 Windows 上以 Online Installer 安裝工具鏈、建置工具、IntelProCube 與 VS Code Extension，再把 Extension 指向 SDK V2.1.0，建置 IPRO7AI Reef EVK 的開箱韌體 `ipro7ai_reef_demo`。

!!! warning "安裝程式目前不會安裝 V2.1.0"
    2026-10-16 核對：Online Installer 的套件清單仍以 SDK 1.2.1 為 stable，尚未登錄 V2.x，選擇 latest 也不會安裝 V2.1.0。請以安裝程式安裝工具與 Extension，再依[改用 SDK V2.1.0](#sdk-2-1-0) 手動加入 SDK。

## 前置需求 { #requirements }

- 可連上網路的 Windows 電腦：Online Installer 從公開的套件清單下載元件。
- VS Code 1.102 以上。
- 已下載 `IPRO-SDK-V2.1.0.tar.gz` 與 `IPRO-SDK-V2.1.0.tar.gz.sha256`，見[選擇開發環境](environment.md#sdk-2-1-0)。
- 相容 V2.1.0 的工具鏈：V2.1.0 的 README 標示 GCC 14，而安裝程式清單中的 Windows 工具鏈是針對 SDK 1.2.1 宣告的組合。請洽 INTELPRO 取得並確認版本。

## 安裝工具 { #online-3-4-0 }

<div class="ipro-steps" markdown>

1. **下載安裝程式**：從 [Online Installer 3.4.0 Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/online-installer-v3.4.0) 下載 `IPRO-SDK-Online-Setup-3.4.0.exe`，不需登入 GitHub。

2. **選擇模式與目錄**：第一次安裝選 **Full**；另外六種模式（SDK、toolchain、build tools、IntelProCube、OpenOCD、Extension）各安裝單一元件。目的目錄請選全新的資料夾。

3. **核對選項後安裝**：寫入 VS Code 設定與更新 PATH 兩個選項預設不勾選，需要時再勾選。版本選 latest 時，安裝的是各元件標示為 stable／相容的版本，不是 GitHub 上最新的 Release。

4. **重新開啟 VS Code 與終端機**，讓新的 PATH 生效。

</div>

## 改用 SDK V2.1.0 { #sdk-2-1-0 }

<div class="ipro-steps" markdown>

1. **校驗下載檔**：在 PowerShell 計算雜湊值，與 `.sha256` 檔中的值比對（大小寫不同不影響）。

    ```powershell
    Get-FileHash .\IPRO-SDK-V2.1.0.tar.gz -Algorithm SHA256
    Get-Content .\IPRO-SDK-V2.1.0.tar.gz.sha256
    ```

2. **解壓到新目錄**：不要覆蓋舊版 SDK，保留舊版以便回復。

    ```powershell
    tar -xzf .\IPRO-SDK-V2.1.0.tar.gz
    Get-Content .\IPRO-SDK-V2.1.0\VERSION.txt
    ```

    `VERSION.txt` 應顯示 `IPRO-SDK-V2.1.0`；根目錄 `IPRO-SDK-V2.1.0\` 內應有 `CMakeLists.txt`、`apps\` 與 `bsp\`。

</div>

## 設定 VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **確認 Extension 已安裝**：在 Extensions 面板搜尋 `@installed IPRO`，應看到 IPRO SDK Extension（識別碼 `ipro.ipro-sdk-extension`）。若沒有，選 **… → Install from VSIX…** 安裝 VSIX，完成後執行 `Developer: Reload Window`。

2. **開啟 SDK**：以 **File → Open Folder…** 開啟 `IPRO-SDK-V2.1.0` 根目錄，確認來源後允許 Workspace Trust。

3. **指定 SDK 根目錄**：按 ++f1++ 執行 `IPRO Setup: Set SDK Root`，選擇同一個目錄。

4. **檢查環境**：執行 `IPRO Setup: Run Diagnostics`，確認 SDK 根目錄、編譯器、CMake 與 Python 的實際路徑；編譯器須為相容 V2.1.0 的工具鏈。

5. **建置第一個專案**：執行 `IPRO: Go to Project…`，在 platform 分類選擇 `ipro7ai_reef_demo`，再執行 `IPRO: Build`。

</div>

Extension 的命令、燒錄設定與 Monitor 見 [VS Code Extension](../guides/vscode.md)。

## 確認結果 { #verify }

建置完成後應產生：

```text
apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
```

建置成功只代表工具可用，尚未燒錄到板子上。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 安裝後的 SDK 是 1.2.1 | 套件清單尚未登錄 V2.x | 依[改用 SDK V2.1.0](#sdk-2-1-0) 手動加入 |
| 切換後仍使用舊 SDK | 工作區或 User 設定中的 SDK 根目錄仍指向舊版 | 執行 `IPRO Setup: Set SDK Root`，再以 `IPRO Setup: Run Diagnostics` 確認實際路徑 |
| 找不到 IPRO 命令 | Extension 不在目前的 VS Code Profile，或工作區未受信任 | 確認 Extension、Profile 與 Workspace Trust，執行 `Developer: Reload Window` |
| 在命令列直接執行 `make` 時找不到編譯器 | 應用 `.config` 的 `CONFIG_CROSS_COMPILE` 是 Unix 路徑 `/opt/toolchain/...`；Windows 上的建置使用 PATH 上的 `cmake` | 在 `make` 命令列加上 `CROSS_COMPILE=<工具鏈目錄>\bin\riscv64-unknown-elf-`（含最後的連字號），並確認 PATH 上的 CMake 為 3.19 以上 |
| `build_freertos.sh` 或 `tools/serial_monitor.py` 無法執行 | 兩者需要 bash 與 POSIX termios | 在 Windows 使用 Extension 的建置、燒錄與 Serial Monitor，或其他序列埠終端程式 |

## 下一步 { #next-steps }

- [第一個 FreeRTOS 應用](first-app-freertos.md)：燒錄 `ipro7ai_reef_demo`，在 Reef 上執行自我檢查。
- [燒錄與序列埠](flash-and-monitor.md)：`ipro_iot_tool.exe` 的參數與各板設定。
- [VS Code Extension](../guides/vscode.md)：Control Center、燒錄設定與 Monitor。
