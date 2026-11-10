---
title: "開始使用"
description: 從一台新電腦與一塊 IPRO7AI Reef EVK 開始：準備硬體與工具、建置並燒錄開箱韌體，直到主控台回應。
migrate_from: []
---

# 開始使用

依下列順序完成，就能從一台新電腦開始，在 IPRO7AI Reef EVK V4.0 上建置、燒錄並執行開箱韌體 `ipro7ai_reef_demo`，再以 `reef selftest` 確認板上功能。本站的操作步驟都以這塊板子為準；IPRO7 EVB、IPRO7AI EVK、IPRO6S EVK 與 IPRO7 Arduino 板的應用需要對應的板子，請洽 INTELPRO。

## 需要準備 { #what-you-need }

| 項目 | 說明 | 取得方式 |
|---|---|---|
| IPRO7AI Reef EVK V4.0 | 絲印「IPRO7AI REEF EVK V4.0」 | INTELPRO |
| USB-C 線 | 板子唯一的電源輸入；要能傳資料（板上 USB 裝置功能會用到） | 自備 |
| 主控台線（二擇一） | 3.3 V 的 USB 轉 UART 轉接器，以 SH1.0 6 pin 插頭接 U6；或 IPRO Debug Probe，以兩端腳序對調的排線接 U6 | 轉接器自備；Debug Probe 向 INTELPRO 索取 |
| 主機 | macOS 或 Linux（bash）可使用 SDK 全部的命令列工具；Windows 以安裝程式、VS Code Extension 與 `build_freertos.ps1` 開發 | — |
| RISC-V 工具鏈 | GCC 14（Windows 為 GCC 13.1.1），`riscv64-unknown-elf-gcc` | macOS／Linux 版向 INTELPRO 索取；Windows 版由安裝程式安裝 |
| IntelProCube 0.7.0.1 | 燒錄工具：`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | [GitHub Release](https://github.com/INTELPRO-INC/ipro-cube/releases)；Windows 版也由安裝程式安裝 |
| SDK | `IPRO-SDK-V2.2.1.tar.gz` | [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.1) |
| 選用 | OV5640 FLEX-24 相機模組、microSD 卡、8 Ω 喇叭（接 J_SPK）、耳機 | 自備；用來完成自我檢查的相機、卡槽與喇叭項目 |

主控台線的接法見 [IPRO7AI Reef EVK：除錯排座 U6](../hardware/boards/reef-evk.md#debug-connector)。

!!! tip "圖形化開發環境"
    IPRO Workbench（Apple 晶片的 macOS、Windows 11）把補齊工具、建置、燒錄與序列埠監看放在同一個視窗，見 [IPRO Workbench](../workbench/index.md)。

## 依序完成 { #path }

<div class="grid cards" markdown>

-   :material-tools:{ .lg } **1. [準備開發環境](environment.md)**

    ---

    下載並校驗 SDK，安裝 CMake、make、Python、RISC-V 工具鏈與 IntelProCube，以一次建置確認環境可用。

-   :material-microsoft-windows:{ .lg } **2. [Windows 安裝與 VS Code](windows.md)**

    ---

    只有使用 Windows 時需要：以 Online Setup 一次安裝 SDK、工具與 VS Code Extension，在 VS Code 或以 `build_freertos.ps1` 建置與燒錄。

-   :material-developer-board:{ .lg } **3. [第一個 FreeRTOS 應用](first-app-freertos.md)**

    ---

    設定開關、接主控台線，建置、燒錄並執行 `ipro7ai_reef_demo`，以 `reef selftest` 檢查 LED、喇叭、SD 卡槽與相機。

-   :material-usb-port:{ .lg } **4. [燒錄與序列埠](flash-and-monitor.md)**

    ---

    參考：四種進入下載模式的方式、IntelProCube 參數與分割表、boot2 與 `mfg` 資料、主控台與序列埠辨識。

-   :material-console:{ .lg } **5. [macOS／Linux 命令列](command-line.md)**

    ---

    參考：`make -C`、`DEFCONFIG=`、建置目錄與產出，以及 `build_freertos.sh` 的動作、選項與環境變數。

</div>

## 下一步 { #next-steps }

板子跑起開箱韌體之後，接著做這三篇實作教學：

- [建置與燒錄流程](../tutorials/build-and-flash.md)：修改程式、建置、燒錄、看主控台的日常迴圈。
- [建立第一個應用](../tutorials/first-own-app.md)：從零建立自己的應用並在 Reef 上執行。
- [測試應用](../tutorials/testing.md)：在主機與板子上測試自己的應用。

板子的完整資料（開關、腳位、擴充排針）見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。本版的 Zephyr 板型只有 IPRO7 EVB 與 IPRO7AI EVK，沒有 Reef，見 [Zephyr RTOS](../guides/zephyr.md)。
