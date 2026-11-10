---
title: "準備開發環境"
description: 在 macOS、Linux 或 Windows 上取得並校驗 SDK，安裝建置工具、RISC-V 工具鏈與 IntelProCube，接上主控台線，並以一次建置確認環境。
migrate_from:
  - "getting-started.html#sdk-2-1-0"
  - "getting-started.html#prerequisites"
---

# 準備開發環境

完成本頁後，主機上有 SDK、建置工具、RISC-V 工具鏈與 IntelProCube 燒錄工具，能辨識 Reef 的主控台序列埠，並能在 SDK 根目錄建置 IPRO7AI Reef EVK 的開箱韌體。各步驟依作業系統分頁；Windows 的完整流程另見 [Windows 安裝與 VS Code](windows.md)。

## 前置需求 { #prerequisites }

| 項目 | 需求 |
|---|---|
| 主機 | macOS 或 Linux（有 bash）；或 Windows x64 |
| 權限 | 安裝套件與寫入 `/opt/toolchain/` 需要系統管理員權限 |
| 網路 | 下載 SDK；Windows 的 Online Setup 需要連上 GitHub |
| 另行取得 | RISC-V 工具鏈：macOS／Linux 版向 INTELPRO 索取，Windows 版由 Online Setup 安裝 |
| 燒錄工具 | IntelProCube 0.7.0.1：從 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) 下載，見[安裝 IntelProCube](#intelprocube)；Windows 版由 Online Setup 安裝 |
| 硬體 | IPRO7AI Reef EVK、USB-C 線、主控台線，見[需要準備](index.md#what-you-need) |

## 取得 SDK { #get-sdk }

<div class="ipro-steps" markdown>

1. **下載**：從 [IPRO-SDK-V2.2.0 Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) 下載 `IPRO-SDK-V2.2.0.tar.gz`，並記下頁面上公布的 SHA-256 值。

2. **校驗**：計算下載檔的 SHA-256。

    === "macOS"

        ```bash
        shasum -a 256 IPRO-SDK-V2.2.0.tar.gz
        ```

    === "Linux"

        ```bash
        sha256sum IPRO-SDK-V2.2.0.tar.gz
        ```

    === "Windows"

        ```powershell
        Get-FileHash .\IPRO-SDK-V2.2.0.tar.gz -Algorithm SHA256
        ```

    畫面印出 64 個十六進位字元，應與 Release 頁面公布的值完全相同（大小寫不影響）。不同時請重新下載。

3. **解壓並確認版本**：解壓到新的目錄，不要覆蓋舊版 SDK。

    === "macOS／Linux"

        ```bash
        tar xzf IPRO-SDK-V2.2.0.tar.gz
        cd IPRO-SDK-V2.2.0
        cat VERSION.txt
        ```

    === "Windows"

        ```powershell
        tar -xzf .\IPRO-SDK-V2.2.0.tar.gz
        Get-Content .\IPRO-SDK-V2.2.0\VERSION.txt
        ```

    `VERSION.txt` 的內容：

    ```text
    IPRO SDK Release
    ========================================
    IPRO7: IPRO-SDK-V2.2.0
    IPRO6: IPRO-SDK-V2.2.0

    Release Date: 2026-11-03
    Base Commit: 60afd4ab
    ```

    解壓出的 `IPRO-SDK-V2.2.0/` 就是 SDK 根目錄（本站寫作 `<SDK>`），裡面有 `apps/`、`bsp/`、`components/`、`build_freertos.sh` 與 `VERSION.txt`。

</div>

## 安裝建置工具 { #host-tools }

<div class="ipro-steps" markdown>

1. **安裝 CMake、GNU Make 與 Python**

    === "macOS"

        ```bash
        xcode-select --install          # 提供 make
        brew install cmake python3
        ```

    === "Linux"

        ```bash
        sudo apt update
        sudo apt install -y cmake make python3
        ```

        以 Debian／Ubuntu 為例，其他發行版請安裝對應的套件。Linux x86-64 上若 PATH 沒有 `cmake`，建置會改用 SDK 隨附的 `tools/cmake/`（CMake 3.15）。

    === "Windows"

        由 Online Setup 的 **Full environment** 或 **Build tools only** 安裝 CMake、Ninja 與 Python，見 [Windows 安裝與 VS Code](windows.md#online-setup)。

2. **確認版本**（macOS／Linux）

    ```bash
    cmake --version     # 3.15 以上；Zephyr 需 3.20 以上
    make --version      # 第一行為 GNU Make
    python3 --version   # 3.8 以上
    ```

</div>

## 安裝 RISC-V 工具鏈 { #toolchain }

<div class="ipro-steps" markdown>

1. **放到預設路徑**

    === "macOS／Linux"

        依 INTELPRO 提供的壓縮檔解壓，讓下列檔案存在：

        ```text
        /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc
        ```

    === "Windows"

        Online Setup 安裝 Windows 版工具鏈 GCC 13.1.1，並依它準備 SDK，SDK V2.2.0 可以直接建置；它建出的映像與 macOS／Linux 上以 GCC 14 建出的不同。見 [Windows 安裝與 VS Code](windows.md#online-setup)。

2. **確認可以執行**（macOS／Linux）

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc --version
    ```

    第一行以 `riscv64-unknown-elf-gcc` 開頭，版本為 14.x。

3. **放在其他路徑時**：設定編譯器前綴 `CROSS_COMPILE`（含最後的連字號）。建置依序採用命令列或環境變數的 `CROSS_COMPILE`、應用 `.config` 的 `CONFIG_CROSS_COMPILE`，最後才是預設路徑。

    ```bash
    export CROSS_COMPILE=<工具鏈目錄>/bin/riscv64-unknown-elf-
    ```

    要長期使用，把這行加進 `~/.zshrc`（macOS）或 `~/.bashrc`（Linux）。

</div>

## 安裝 IntelProCube { #intelprocube }

IntelProCube 是 IPRO6 與 IPRO7 的燒錄與 OTA 工具，公開在 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases)；本站以 0.7.0.1 為準。Windows 由 Online Setup 安裝 0.7.0，它燒錄 IPRO7 與 Reef 的檔案和 0.7.0.1 相同，見 [Windows 安裝與 VS Code](windows.md)；燒錄 IPRO6S 時，依 [IntelProCube 的 README](https://github.com/INTELPRO-INC/ipro-cube#windows) 另外安裝 0.7.0.1。

<div class="ipro-steps" markdown>

1. **下載並核對**

    === "macOS"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-macos-arm64.tar.gz
        shasum -a 256 IntelProCube-0.7.0.1-macos-arm64.tar.gz
        ```

        畫面顯示 `c3a8bf7eca2a48c3f9bf40c3241ddf6aec5155688f2a92f40a84cc47f7633bc4`。macOS 版需要 Apple 晶片。改用瀏覽器下載時，解壓前先執行 `xattr -d com.apple.quarantine IntelProCube-0.7.0.1-macos-arm64.tar.gz`，否則 macOS 會結束套件裡的程式。

    === "Linux"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-linux-x64.tar.gz
        sha256sum IntelProCube-0.7.0.1-linux-x64.tar.gz
        ```

        畫面顯示 `efc5765ca402d0af00b42489dd61a74481531875b871517af5c0bca9d7387df9`。Linux 版適用 x86-64。

    數值不同時請重新下載。每個版本的值都列在 Release 頁的 `SHA256SUMS.txt`。

2. **解壓**

    === "macOS"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-macos-arm64.tar.gz -C ~/ipro
        ```

    === "Linux"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-linux-x64.tar.gz -C ~/ipro
        ```

    解壓後得到 `~/ipro/IntelProCube`，本站寫作 `<IntelProCube>`。命令列工具要在這個目錄下執行，因為它從 `chips/` 讀取晶片設定、分割表與 boot2 映像。

3. **確認可以執行**

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --help
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --help
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --help
        ```

    畫面以用法說明開頭，例如：

    ```text
    usage: ipro_iot_tool_macos [-h] [--list-ports] --chipname CHIPNAME
                               [--interface INTERFACE] [--port PORT]
                               [--baudrate BAUDRATE] [--xtal XTAL]
                               [--chip-variant CHIP_VARIANT] [--dts DTS] [--pt PT]
                               [--boot2 BOOT2] [--firmware FIRMWARE] [--mfg MFG]
    ...
    ```

4. **讓 `build_freertos.sh` 找得到工具**（macOS／Linux）：設定 `IPRO_FLASH_TOOL`，或把 `<IntelProCube>` 加入 `PATH`。

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ```

</div>

## 接上主控台線 { #usb-serial }

Reef 板上沒有 USB 轉 UART 晶片：USB-C 只負責供電與板上 USB 裝置功能，主控台與燒錄都經 U6 的轉接器或 IPRO Debug Probe。

<div class="ipro-steps" markdown>

1. **把轉接器或 Debug Probe 接到電腦**（先不必接板子），查看新增的序列埠：

    === "macOS"

        ```bash
        ls /dev/cu.*
        ```

        USB 轉 UART 轉接器出現為 `/dev/cu.usbserial-XXXX`（名稱依轉接器而定）；IPRO Debug Probe 出現兩個 `/dev/cu.usbmodem…`，名稱結尾為 `02` 的是主控台。

    === "Linux"

        ```bash
        ls /dev/ttyUSB* /dev/ttyACM*
        ```

        轉接器多半出現為 `/dev/ttyUSB0`；IPRO Debug Probe 出現兩個 `/dev/ttyACM*`。

    === "Windows"

        開啟「裝置管理員」→「連接埠 (COM 和 LPT)」，插入前後比較，多出來的就是新的 COM 埠（例如 `COM5`）；IPRO Debug Probe 會多出兩個。

2. **沒有新增序列埠時**：換一條確定能傳資料的 USB 線；作業系統無法辨識轉接器時，安裝轉接器廠商提供的驅動程式；Debug Probe 請洽 INTELPRO。

3. **Linux 的權限**：開啟序列埠出現 `Permission denied` 時，以 `ls -l /dev/ttyUSB0` 查看擁有序列埠的群組（常見為 `dialout`），把自己加入該群組後重新登入：

    ```bash
    sudo usermod -aG dialout $USER
    ```

</div>

Debug Probe 的兩個序列埠怎麼分辨、Reef 各應用在 USB-C 上出現的裝置，見[燒錄與序列埠：辨識序列埠](flash-and-monitor.md#ports)。

## 確認結果 { #verify }

在 SDK 根目錄建置開箱韌體（macOS／Linux）：

```bash
./build_freertos.sh ipro7ai_reef_demo
```

成功時的輸出：

```text
Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

→ Building ipro7ai_reef_demo...
✓ Build succeeded (14s)
  Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
  Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
```

建置時間與檔案大小會因主機與工具鏈而略有不同。Windows 上以 VS Code Extension 的 `IPRO: Build` 或 `build_freertos.ps1` 確認，見 [Windows 安裝與 VS Code](windows.md#verify)。

## 兩種環境的差異 { #choose }

| 工作 | macOS／Linux | Windows |
|---|---|---|
| 安裝工具 | 系統套件管理工具，加上 INTELPRO 提供的工具鏈，以及從 GitHub 下載的 IntelProCube | Online Setup（工具鏈、CMake／Ninja／Python、IntelProCube、OpenOCD、VS Code Extension） |
| 建置 | `make -C apps/<分類>/<應用>` 或 `./build_freertos.sh` | VS Code Extension 的 `IPRO: Build` |
| 燒錄 | IntelProCube 命令列工具，或 `./build_freertos.sh … flash` | `ipro_iot_tool.exe` |
| 主控台 | `screen`、`picocom` 等終端程式；`tools/serial_monitor.py` | PuTTY 等終端程式，或 Extension 的 Serial Monitor |
| 自動化（`build_freertos.sh`、`tools/serial_monitor.py`） | 可用 | 不可用：兩者需要 bash 與 POSIX termios |
| Zephyr（`tools/zephyr/`） | 可用 | SDK 未提供 Windows 流程 |

本站的命令列範例以 macOS／Linux 為準。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 計算出的 SHA-256 與 Release 頁面不同 | 下載不完整或檔案損毀 | 刪除後重新下載 |
| `No cmake found. Install cmake or provide bundled cmake at …` | PATH 上沒有 `cmake`，且隨附的 CMake 無法在此主機執行（隨附版只適用 Linux x86-64） | 依[安裝建置工具](#host-tools)安裝 CMake 3.15 以上 |
| `riscv64-unknown-elf-gcc: No such file or directory` | 工具鏈不在 `/opt/toolchain/riscv_ipro7/` | 依[安裝 RISC-V 工具鏈](#toolchain)設定 `CROSS_COMPILE` |
| `Flash tool not found: ipro_iot_tool_macos` | 未設定 `IPRO_FLASH_TOOL`，PATH 上也沒有 IntelProCube | 依[安裝 IntelProCube](#intelprocube) 第 4 步設定 |
| 插上轉接器後沒有新的序列埠 | USB 線只能充電，或缺驅動程式 | 換線；安裝轉接器廠商的驅動程式 |
| Linux 開啟序列埠時 `Permission denied` | 使用者不在序列埠的群組內 | 加入 `dialout` 等群組後重新登入 |
| macOS 開啟 `/dev/tty.*` 後卡住 | `tty.*` 會等待 carrier detect 訊號 | 改用 `/dev/cu.*` |

## 下一步 { #next-steps }

- 使用 Windows：[Windows 安裝與 VS Code](windows.md)
- 環境已就緒：[第一個 FreeRTOS 應用](first-app-freertos.md)
- 命令列參考：[macOS／Linux 命令列](command-line.md)
