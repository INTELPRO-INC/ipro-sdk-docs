---
title: "Windows 安裝與 VS Code"
description: 在 Windows 上以 IPRO SDK Online Setup 3.6.0 一次安裝 SDK V2.2.0、RISC-V 工具鏈、建置工具、IntelProCube 與 VS Code Extension，在 VS Code 或 PowerShell 建置 IPRO7AI Reef EVK 的開箱韌體，燒錄並開啟主控台。
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

在 Windows 上以 IPRO SDK Online Setup 一次安裝 SDK V2.2.0、RISC-V 工具鏈、建置工具（CMake、Ninja、Python）、IntelProCube、OpenOCD 與 VS Code Extension，建置 IPRO7AI Reef EVK 的開箱韌體 `ipro7ai_reef_demo`，燒錄後在 COM 埠上看到主控台。建置與燒錄可以在 VS Code 中進行，也可以在 PowerShell 以 `build_freertos.ps1` 進行。

!!! info "工具鏈版本"
    Online Setup 安裝的 Windows 版工具鏈是 GCC 13.1.1，並依它準備 SDK（處理內容記錄在 SDK 根目錄的 `PREBUILT-ARCHIVES-STRIPPED.json`）。SDK V2.2.0 在 macOS／Linux 以 GCC 14 建置，兩者建出的映像不同。

## 前置需求 { #requirements }

- Windows x64，可連上 GitHub（Online Setup 從公開的套件清單與 GitHub Release 下載元件）。
- VS Code 1.102 以上（也可以讓安裝程式下載）。
- IPRO7AI Reef EVK、USB-C 線，以及接在 U6 的 IPRO Debug Probe 或 USB 轉 UART 轉接器，見[需要準備](index.md#what-you-need)。

## 安裝 { #online-setup }

<div class="ipro-steps" markdown>

1. **下載安裝程式**：從 [IPRO SDK Online Setup 最新版](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest)（3.6.0）下載 `IPRO-SDK-Online-Setup-3.6.0.exe`，不需登入 GitHub。

2. **校驗**：在 PowerShell 計算雜湊值。

    ```powershell
    Get-FileHash .\IPRO-SDK-Online-Setup-3.6.0.exe -Algorithm SHA256
    ```

    `Hash` 欄應與同一個 Release 的 `SHA256SUMS.txt` 中同名檔案的值相同（大小寫不影響）。安裝程式沒有程式碼簽章，Windows 可能顯示 SmartScreen 警告，請依公司的資訊安全規定處理。

3. **選擇 Full environment**：執行安裝程式，在 **Choose packages** 選 **Full environment**。

4. **確認版本**：**Select package versions** 各元件保持 latest，選單會直接顯示對應的版本，例如 `latest (2.2.0)`。

5. **選擇目錄**：在 **Select Destination Location** 保留預設的新資料夾 `C:\IPRO\versions\3.6.0-<日期時間>`，或填入一個尚不存在的資料夾（安裝根目錄，本頁寫作 `<安裝目錄>`）。

6. **選擇附加工作**：尚未安裝 VS Code 時勾選 **Install VS Code from Microsoft if absent**；保持勾選 **Install the selected Extension into VS Code**；要讓 VS Code 直接使用這個環境，勾選 **Switch only selected component settings**；要在一般終端機直接執行工具時，勾選 **Add installed tools to user PATH**。

7. **安裝**：在 **Ready to Install** 確認目錄、模式與版本後按 **Install**。

8. **看完成頁**：完成頁會列出 SDK 的位置（`<安裝目錄>\sdk\IPRO-SDK-V2.2.0`）、命令列建置的第一個指令與工具鏈的位置。重新開啟 VS Code 與終端機，讓新的設定與 PATH 生效。

</div>

安裝時會修正 SDK 在 Windows 上的建置問題（辨識 IPRO 工具鏈、CMake 4 搭配 Ninja 的建置訊息、序列埠主控台），並加入 `build_freertos.ps1`；修改的檔案記錄在 SDK 根目錄的 `WINDOWS-HOST-FIXES.json`。

## 設定 VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **確認 Extension 已安裝**：在 Extensions 面板搜尋 `@installed IPRO`，應看到 IPRO SDK Extension（識別碼 `ipro.ipro-sdk-extension`）。

2. **開啟 SDK**：以 **File → Open Folder…** 開啟 `<安裝目錄>\sdk\IPRO-SDK-V2.2.0`，確認來源後允許 Workspace Trust。

3. **指定 SDK 根目錄**：安裝時沒有勾選設定切換工作時，按 ++f1++ 執行 `IPRO Setup: Set SDK Root`，選擇同一個目錄。

4. **檢查環境**：執行 `IPRO Setup: Run Diagnostics`，確認 SDK 根目錄、編譯器、CMake、Python 與燒錄工具都指向 `<安裝目錄>` 底下。

5. **建置開箱韌體**：執行 `IPRO: Go to Project…`，在 platform 分類選擇 `ipro7ai_reef_demo`，再執行 `IPRO: Build`。

</div>

Extension 的其他命令與設定見 [VS Code Extension](../guides/vscode.md)。

## 命令列建置 { #command-line }

`build_freertos.ps1` 是 `build_freertos.sh` 的 Windows 版，動作相同：`build`、`clean`、`flash`、`monitor`、`size`、`test` 可以組合，依序執行。選項大致相同，但 `-c` 在這裡是工具鏈前綴（`--cross`）；晶片變體與分割表只有長選項 `--chip-variant`、`--pt`（`build_freertos.sh` 的 `-c` 是 `--chip-variant`，`-P` 是分割表）。它使用同一個安裝目錄中的工具鏈、CMake、Ninja、Python 與 IntelProCube，沒有加入 PATH 也能執行。Windows 預設不允許直接執行 `.ps1`；以 `powershell -ExecutionPolicy Bypass -File` 執行只影響這一次，不會改變系統設定。

<div class="ipro-steps" markdown>

1. **切換到 SDK 目錄**

    ```powershell
    cd <安裝目錄>\sdk\IPRO-SDK-V2.2.0
    ```

2. **建置**

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 build ipro7ai_reef_demo
    ```

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    -> Building ipro7ai_reef_demo...
    [OK] Build succeeded (21s)
      Binary: ...\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin (219 KB)
      Toolchain: <安裝目錄>/toolchain/riscv_ipro7_win32/bin/riscv64-unknown-elf-gcc
      Log: ...\apps\platform\ipro7ai_reef_demo\build\build.log
    ```

    失敗時會印出建置記錄的最後 30 行與完整記錄的位置。

3. **確認辨識 IPRO 工具鏈**

    ```powershell
    Select-String -Path apps\platform\ipro7ai_reef_demo\build\build.log -Pattern "\[toolchain\]"
    ```

    ```text
    -- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
    ```

</div>

其他用法：`-l` 列出所有應用，`-h` 顯示所有選項，`-d defconfig_<名稱>` 以替代設定建置，`-c <前綴>` 指定其他工具鏈（前綴以 `riscv64-unknown-elf-` 結尾）。

## 燒錄 { #flash }

### 以 IPRO Debug Probe { #flash-probe }

<div class="ipro-steps" markdown>

1. **接線**：SW7 撥到 CAM、SW8 撥到 PWR，IPRO Debug Probe 接 U6，再接上 Reef 的 USB-C，見[設定開關與接線](first-app-freertos.md#connect)。Probe 在 Windows 上會出現兩個 COM 埠，見[辨識序列埠](flash-and-monitor.md#ports)。

2. **燒錄並看開機訊息**：在 SDK 目錄執行：

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 flash monitor ipro7ai_reef_demo -w "IPRO7AI Reef carrier demo"
    ```

    腳本會選用 probe 的主控台埠，由 IntelProCube 讓板子進入下載模式、燒錄並重置，看到開機訊息後主控台結束：

    ```text
    [All Success]
    [OK] Flash succeeded (6s)
    ...
    [serial_monitor] MATCHED: IPRO7AI Reef carrier demo

    Summary:
      [OK] flash
      [OK] monitor
    ```

    IPRO7AI 板子的應用會自動帶入 `--chip-variant IPRO7AI` 與分割表 `partition_cfg_2M.toml`。接了多個序列埠時，以 `-p COM5` 指定主控台的埠。

</div>

在 VS Code 中：以 `IPRO: Select Serial Port` 選 probe 的主控台埠，在 `IPRO Config: Configure Flash…` 把晶片配置設為 `IPRO7AI`、分割表設為 `partition_cfg_2M.toml`，再執行 `IPRO: Flash`。

### 以 USB 轉 UART 轉接器 { #flash-uart }

<div class="ipro-steps" markdown>

1. **接線**：SW7 撥到 CAM、SW8 撥到 PWR，主控台線接 U6，接上 USB-C，見[設定開關與接線](first-app-freertos.md#connect)。

2. **找出 COM 埠**：開啟「裝置管理員」→「連接埠 (COM 和 LPT)」，插上轉接器後多出來的就是主控台，例如 `COM5`。

3. **進入下載模式**：按住 SW1（BOOT），按一下 SW2（RESET），再放開 SW1。

4. **燒錄**：在 PowerShell 切換到 `<安裝目錄>\IntelProCube` 執行：

    ```powershell
    cd <安裝目錄>\IntelProCube
    .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
        --port COM5 --baudrate 921600 `
        --pt chips/ipro7/partition/partition_cfg_2M.toml `
        --firmware <安裝目錄>\sdk\IPRO-SDK-V2.2.0\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

    輸出的最後一行是 `[All Success]` 才算成功；工具失敗時也以 0 結束。參數說明見[燒錄與序列埠](flash-and-monitor.md#flash-tool)。燒錄完按 SW2 重置。

</div>

## 主控台 { #console }

<div class="ipro-steps" markdown>

1. **開啟主控台**：在 SDK 目錄執行 `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 monitor ipro7ai_reef_demo -t 30`，或在 PuTTY 選 **Serial**，Serial line 填主控台的 COM 埠、Speed 填 `115200`，按 **Open**。也可以用 Tera Term，或 VS Code Extension 的 `IPRO: Serial Monitor`。

2. **重置**：`build_freertos.ps1 monitor` 會送出 `reboot`；使用其他終端程式時按 SW2（RESET）。視窗出現開機訊息 `IPRO7AI Reef carrier demo`，按 ++enter++ 出現 `ipro />`。

3. **自我檢查**：輸入 `reef selftest`，預期輸出見[第一個 FreeRTOS 應用](first-app-freertos.md#verify)。

</div>

燒錄前先關閉終端程式，否則燒錄工具開不了 COM 埠。

## 單獨安裝 SDK 或工具鏈 { #components }

在 **Choose packages** 選 **SDK only** 或 **Toolchain only** 時，版本頁之後會出現 **Choose where to install**：

- **Add to this existing environment**：清單列出之前以 Online Setup 安裝的環境與其中的 SDK、工具鏈，預設選最新、且有工具鏈的環境。SDK 放進該環境的 `sdk\`，直接使用環境中的工具建置；同版本已在該環境時會提示改選。已安裝的檔案一律不覆蓋。
- **A new directory**：裝到新的資料夾。SDK 會依 `/TOOLCHAINROOT=` 指定的、VS Code 設定的、或最新的其他環境中的工具鏈準備，`build_freertos.ps1` 也會使用那套工具鏈。

靜默安裝以 `/MODE=sdk /ENV=<環境資料夾>` 加到既有環境。其他命令列參數見 [Online Setup 安裝說明](https://github.com/INTELPRO-INC/ipro-sdk-releases/blob/main/INSTALLATION.zh-TW.md)。

## 確認結果 { #verify }

- 建置完成後產生：

    ```text
    apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

- 建置記錄有 `Vendor toolchain detected`。
- 燒錄輸出的結尾為 `[All Success]`。
- 重置後主控台顯示開機訊息與 `ipro />`，`reef selftest` 依序點亮 LED 並發出 1 kHz 短音。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| Windows 顯示未知發行者或 SmartScreen 警告 | 安裝程式沒有程式碼簽章 | 依公司的資訊安全規定處理；不要停用防護 |
| `.\build_freertos.ps1` 無法執行 | Windows 預設不允許執行 `.ps1` | 以 `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 ...` 執行 |
| 完成頁提示找不到工具鏈 | SDK only 裝到新資料夾時沒有可搭配的工具鏈 | 把 SDK 加到有工具鏈的環境，或以 `/TOOLCHAINROOT=<工具鏈資料夾>` 重新安裝 |
| Diagnostics 仍顯示舊的 SDK 路徑 | 工作區或使用者設定中的 SDK 根目錄指向舊版 | 執行 `IPRO Setup: Set SDK Root` 後重新執行 Diagnostics |
| 找不到 IPRO 命令 | Extension 不在目前的 VS Code Profile，或工作區未受信任 | 確認 Extension、Profile 與 Workspace Trust，執行 `Developer: Reload Window` |
| 裝置管理員沒有新的 COM 埠 | USB 線只能充電，或缺轉接器的驅動程式 | 換線；安裝轉接器廠商的驅動程式；Debug Probe 請洽 INTELPRO |
| 燒錄沒有 `[All Success]` | 板子不在下載模式，或 COM 埠被終端程式占用 | 關閉終端程式；使用轉接器時重新以 SW1＋SW2 進入下載模式 |
| `flash jedec id: 00000000` | 沒有加 `--chip-variant IPRO7AI` | 加上後重新燒錄 |
| 主控台亂碼或沒有輸出 | 鮑率不是 115200、板子仍在下載模式，或 RX／TX 接反 | 以 115200 開啟；按 SW2；對調 RX 與 TX |

安裝問題請保留 `<安裝目錄>\online-install.json`、`online-postinstall.log` 與相鄰的 `<安裝目錄>.download.log`。

## 下一步 { #next-steps }

- [第一個 FreeRTOS 應用](first-app-freertos.md)：開箱韌體的自我檢查與指令。
- [燒錄與序列埠](flash-and-monitor.md)：其他下載模式、分割表、boot2 與 `mfg` 資料。
- [VS Code Extension](../guides/vscode.md)：Extension 的命令與設定。
