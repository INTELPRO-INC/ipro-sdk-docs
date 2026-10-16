---
title: 文件下載
description: IPRO7／IPRO7AI 正式晶片、軟體與開發板文件清單，含版本、語言與涵蓋內容。
generated: tools/gen_documents.py
migrate_from: []
---

# 文件下載

INTELPRO 為 IPRO7 與 IPRO7AI 提供的正式文件，對應 SDK V2.1。每份文件都有繁體中文與英文版。

!!! info "取得方式"
    標示「向 INTELPRO 索取」的文件，請向 INTELPRO 索取，並註明文件名稱、版本與語言。

## 晶片文件 { #chip-documents }

| 文件 | 版本 | 語言 | 內容 | 取得方式 |
|---|---|---|---|---|
| IPRO7 產品簡介 | V1.0 | 繁中／English | 功能概要、方塊圖、目標應用、封裝與訂購資訊 | 向 INTELPRO 索取 |
| IPRO7 資料手冊 | V1.6 | 繁中／English | 功能描述、腳位定義與 GPIO 腳位多工、AI／NPU、電氣規格、標記與訂購資訊 | 向 INTELPRO 索取 |
| IPRO7 暫存器參考手冊 | V1.3 | 繁中／English | 系統與記憶體、重置與時脈，以及 GPIO、ADC、DMA、SPI、UART、I2C、PWM、計時器、音訊 ADC、KeyScan、低功耗、安全引擎與 MJPEG 的暫存器 | 向 INTELPRO 索取 |
| IPRO7 硬體設計指南 | V1.1 | 繁中／English | SoC 硬體參考，以及電源、PCB 佈線、時脈電路、開機模式與 strap 腳、介面參考設計、封裝 footprint 與 SoM 參考設計 | 向 INTELPRO 索取 |
| IPRO7 應用說明：電源上電驗證 | V1.1 | 繁中／English | 電源架構與上電順序、測試點、量測步驟與驗收標準、檢查表 | 向 INTELPRO 索取 |

## 軟體文件 { #software-documents }

| 文件 | 版本 | 語言 | 內容 | 取得方式 |
|---|---|---|---|---|
| IPRO7 SDK 安裝指南 | V1.1 | 繁中／English | 安裝程式與安裝模式、編輯器設定、單一套件更新與離線安裝、第一次建置、燒錄與序列埠鮑率 | 向 INTELPRO 索取 |
| IPRO7 程式設計指南 | V1.1 | 繁中／English | 開發環境、SDK 架構、建置系統、FreeRTOS、各周邊、BLE、經 SDIO 外接的 Wi-Fi、多媒體、USB、安全引擎、電源管理、OTA、除錯與日誌 | 向 INTELPRO 索取 |
| IPRO7 API 規格書 | V1.1 | 繁中／English | HAL、USB、安全引擎、BLE、經 SDIO 外接的 Wi-Fi、檔案系統、OS 抽象層與 AI／NPU 執行環境的 API，以及錯誤碼 | 向 INTELPRO 索取 |
| IPRO7 軟體工具使用指南 | V1.1 | 繁中／English | RISC-V 工具鏈、建置與設定系統、燒錄與下載工具、除錯工具、序列埠監看、BLE 工具、RF 調校工具、映像檔工具、記憶體與大小分析 | 向 INTELPRO 索取 |
| IPRO7AI AI Studio 使用指南 | V1.3 | 繁中／English | 模型準備與編譯、NPU 派工檢視、數值驗證、上板執行與運算子支援表 | 向 INTELPRO 索取 |

## 開發板文件 { #board-documents }

| 文件 | 版本 | 語言 | 內容 | 取得方式 |
|---|---|---|---|---|
| IPRO7AI Reef EVK 開發板使用手冊 | V1.2 | 繁中／English | 系統架構、板面、快速上手、跳線與按鍵、介面、電源、燒錄與除錯、SDK 範例 | 向 INTELPRO 索取 |
| IPRO Debug Probe 使用手冊 | V1.1 | 繁中／English | 板面、快速上手、按鍵與 LED、UART 與 JTAG／CCI 介面、電源、主機設定、燒錄與除錯、BOM 與製造資料 | 向 INTELPRO 索取 |

板卡的上手步驟見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)，SDK 的 API 索引見 [API 參考](../reference/api/index.md)。
