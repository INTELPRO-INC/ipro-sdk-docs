---
title: "選擇開發環境"
description: SDK V2.1.0 的內容與下載、需要準備的硬體與工具，以及 Windows 與 macOS／Linux 兩種開發環境的差異。
migrate_from:
  - "getting-started.html#sdk-2-1-0"
  - "getting-started.html#prerequisites"
---

# 選擇開發環境

IPRO SDK 可以在 Windows 上以安裝程式與 VS Code Extension 開發，也可以在 macOS／Linux 上以命令列開發。先下載 SDK、備妥板卡與另行取得的工具，再依[下表](#choose)選擇環境。

## SDK V2.1.0 { #sdk-2-1-0 }

從 [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0) 下載 `IPRO-SDK-V2.1.0.tar.gz` 與校驗檔 `IPRO-SDK-V2.1.0.tar.gz.sha256`。解壓與校驗步驟在各環境的安裝頁。

| 內容 | 說明 |
|---|---|
| FreeRTOS 應用 | 35 個，全部以 IPRO7 系列為目標，涵蓋 IPRO7 EVB、IPRO7AI EVK 與 IPRO7AI Reef EVK |
| Zephyr RTOS | SDK 同時是 Zephyr v4.4.0 模組，支援 `ipro7_evb` 與 `ipro7ai_evk` 兩個板型 |
| 主機端工具 | `build_freertos.sh`（建置、燒錄、監看）、`tools/serial_monitor.py`（主控台）、`tools/zephyr/`（Zephyr 工作區與燒錄腳本） |

!!! info "需另行取得"
    - **RISC-V 工具鏈**（`riscv64-unknown-elf-gcc`）：未包含於 V2.1.0，請洽 INTELPRO。
    - **IntelProCube v0.6.3 命令列燒錄工具**（`ipro_iot_tool.exe`、`ipro_iot_tool_macos`、`ipro_iot_tool_linux`）：未包含於 V2.1.0，請洽 INTELPRO。
    - **Zephyr 本體與模組**：第一次執行 `tools/zephyr/bootstrap.sh` 時從 GitHub 下載。

## 系統需求 { #prerequisites }

**硬體**

- 開發板：IPRO7AI Reef EVK（入門範例使用此板）、IPRO7AI EVK 或 IPRO7 EVB。
- Reef EVK 需要兩條線：USB-C 線（供電，Reef 只能由 USB-C 供電）與 USB 轉 UART 線（接 U6 主控台接頭，SH1.0）。
- 其他板卡：連到主控台 UART0（GPIO20 TX／GPIO21 RX）的 USB 序列埠，接法見[板卡頁](../hardware/index.md)。

**軟體**

| 項目 | Windows（VS Code） | macOS／Linux（命令列） |
|---|---|---|
| SDK | V2.1.0 壓縮檔，解壓到新目錄 | 同左 |
| 工具鏈 | 請洽 INTELPRO 取得相容 V2.1.0 的版本 | 預設路徑 `/opt/toolchain/riscv_ipro7/`，或以 `CROSS_COMPILE` 指定 |
| 建置工具 | 由 Online Installer 安裝 | CMake 3.19 以上、GNU Make、Python 3.8 以上；Zephyr 另需 CMake 3.20 以上 |
| 燒錄工具 | IntelProCube（`ipro_iot_tool.exe`） | IntelProCube（`ipro_iot_tool_macos`／`ipro_iot_tool_linux`） |
| 編輯器 | VS Code 與 IPRO SDK Extension | 不限 |

## 兩種環境的差異 { #choose }

| 工作 | Windows＋VS Code | macOS／Linux 命令列 |
|---|---|---|
| 安裝 | Online Installer 安裝工具與 Extension；SDK V2.1.0 手動下載解壓 | 自行安裝工具，下載解壓 SDK |
| 建置 FreeRTOS 應用 | Extension 的 `IPRO: Build` | `make -C apps/<分類>/<應用>` 或 `./build_freertos.sh <應用>` |
| 燒錄 | Extension 的 `IPRO: Flash`，或直接執行 `ipro_iot_tool.exe` | 直接執行 IntelProCube 命令列工具，或 `./build_freertos.sh <應用> flash` |
| 主控台 | Extension 的 Serial Monitor 或其他序列埠終端程式 | `tools/serial_monitor.py` 或其他序列埠終端程式 |
| Zephyr | SDK 未提供 Windows 流程 | `tools/zephyr/bootstrap.sh` 與 `west` |

SDK 隨附的腳本（`build_freertos.sh`、`tools/zephyr/*.sh`）需要 bash，`tools/serial_monitor.py` 使用 POSIX 的 termios，因此這些工具在 macOS／Linux 上執行。需要 Zephyr，或要以腳本自動化建置、燒錄與測試時，選擇 macOS／Linux；習慣 VS Code 圖形介面時，選擇 Windows。

## 下一步 { #next-steps }

- [Windows 安裝與 VS Code](windows.md)
- [macOS／Linux 命令列](command-line.md)
- 環境已就緒：[第一個 FreeRTOS 應用](first-app-freertos.md)
