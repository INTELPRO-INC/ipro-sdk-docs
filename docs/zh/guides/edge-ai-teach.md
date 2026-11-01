---
title: "IPRO AI Teach 2.0"
description: IPRO7AI Reef 上的 Edge AI 平台 V2.0：一份韌體裡的影像、聲紋、感測器三個辨識工具，在 IPRO AI Studio 收資料、訓練、部署到板上的 NPU
---

# IPRO AI Teach 2.0

IPRO AI Teach 2.0 是 IPRO7AI Reef 上的 Edge AI 平台 V2.0：一份韌體裡有影像、聲紋、感測器三個辨識工具，在 IPRO AI Studio 收集資料、在電腦上訓練，再經 USB-C 部署到板上，由 NPU 執行。整個流程不需要寫程式；要把模型放進自己的應用時，平台提供同一套執行庫與 API。

!!! info "取得方式"
    IPRO AI Teach 2.0（Edge AI 平台 V2.0 韌體、IPRO AI Studio）未包含於 V2.1.0，請洽 INTELPRO。

!!! abstract "重點"
    - 一份韌體 `ipro_reef_teach`：影像、聲紋、感測器三種模式，一次執行一種；切換約 2 秒，三個模型都保留在板上。
    - IPRO AI Studio 的 Teach、Audio、Sensor 頁面：收資料、訓練（電腦的 CPU 即可，不需要 GPU）、部署、看結果。
    - 模型以 `.ipkg` 套件部署；`ipro-ai` 命令列可做部署、驗證與跑分，適合自動化。
    - 硬體：IPRO7AI Reef（V4）。

## 介紹影片 { #video }

<video controls preload="metadata" playsinline width="100%" poster="/ipro-sdk-docs/assets/videos/ipro-ai-teach-2-intro.jpg">
  <source src="/ipro-sdk-docs/assets/videos/ipro-ai-teach-2-intro.mp4" type="video/mp4">
</video>

硬體導覽、燒錄，以及影像、聲紋、感測器三個工具從收資料到在板上辨識的流程（約 3 分鐘）。

## 三個工具 { #tools }

| | 影像 | 聲紋 | 感測器 |
|---|---|---|---|
| 做什麼 | 相機畫面裡的物件分類 | 辨識誰在說話；註冊的人有名字，沒註冊的人以編號標示 | 振動、IMU 等感測訊號的狀態分類，沒教過的狀態回答 `UNKNOWN` |
| IPRO AI Studio 頁面 | Teach | Audio | Sensor |
| USB 裝置 | IPRO7 UVC Cam（3896:0705），相機＋序列埠 | IPRO Reef Voice（3896:0720） | IPRO Reef Sensor（3896:0721） |
| 類別或人數 | 最多 8 類 | 最多 19 人，存在板上的快閃記憶體 | 最多 8 類（`UNKNOWN` 占一類） |
| 結果頻率 | 隨相機影格 | 每秒 1 次 | 每秒 4 次 |
| 板上 NPU 時間 | 約 10.5 ms（MobileNetV2 0.35） | 約 8.9 ms | 約 4.6 ms |
| 模型分格容量 | 508 KB | 444 KB | 252 KB |

三個工具共用板上的 NPU，各自的模型存在快閃記憶體的獨立分格。部署時先寫入、讀回並檢查 CRC，最後才提交；部署途中斷電或重置，板子會回報「install interrupted」，不會留下寫了一半的模型。

## 使用流程 { #workflow }

<div class="ipro-steps" markdown>

1. **燒錄一次韌體。** 以 IntelProCube 燒錄 `ipro_reef_teach` 韌體與它的分割區表，聲紋模型隨 mfg 酬載一起寫入。之後換模型不必再燒錄。
2. **接上 USB-C。** 電腦依目前的模式列舉出上表的 USB 裝置；IPRO AI Studio 以 USB 名稱找到板子。
3. **在 Studio 收資料、訓練。** 影像：對著相機錄每一類；聲紋：每人朗讀約 20 秒註冊；感測器：每種狀態錄一段。
4. **部署。** 模型經同一條 USB-C 寫進板子，板子重新開機後載入；板子在別的模式時，頁面會提供 **Switch to …** 切換。
5. **看結果。** 影像結果疊在相機畫面上；聲紋與感測器的結果顯示在 Studio 頁面，板上的 RGB LED 同步提示。

</div>

## 模型套件與命令列 { #packages-and-cli }

模型以 `.ipkg` 套件交付：內含模型、類別名稱、前處理參數與檔案雜湊，部署前會先檢查目標晶片、執行層版本與分格容量。`ipro-ai` 命令列提供與 Studio 相同的功能，加上 `--json` 可接進自動化流程：

```bash
ipro-ai device list                    # 列出接上的 Reef 與目前的模式
ipro-ai model list --all               # 三個模式各自的模型
ipro-ai deploy vib.ipkg --switch       # 切到套件對應的模式後部署，並確認 CRC
ipro-ai benchmark -n 100 --json        # 板上推論時間
```

## 給應用開發者 { #for-developers }

平台的執行庫與 API 隨 Edge AI 平台提供，要在自己的韌體裡使用同樣的模型時可直接呼叫：

| 標頭 | 用途 |
|---|---|
| `ipro_ai.h` | 開啟多個模型並由同一個 NPU 依序執行；每段 NPU 運算有逾時上限，NPU 故障時拒絕執行並回報錯誤，不會卡住 |
| `ipro_ai_store.h` | 模型分格、提交紀錄、CRC 檢查 |
| `ipro_ai_source.h` | 資料來源（推入式環形緩衝、定時取樣） |
| `ipro_ai_preproc.h` | 感測器、聲紋、影像的前處理 |
| `ipro_ai_app.h`、`ipro_ai_event.h` | 應用管線與推論結果事件 |
| `app_watchdog.h` | AON 看門狗：系統停止回應時自動重新啟動 |

## 本版限制 { #limitations }

- 一次只執行一個工具；模型分格各一格，部署中斷時該工具會沒有模型，重新部署即可。
- 影像工具需要接上 OV5640 相機模組。
- 感測器的異常偵測模式只以正常資料訓練，對只改變振幅或緩慢漂移的故障較不敏感；錄得到的故障建議以分類模式訓練。

## 相關文件 { #related }

- [AI 與 NPU](ai-npu.md)：IPRO7AI NPU 與 IPROAI 執行庫。
- [文件下載](../documents/index.md)：IPRO7AI Reef 使用手冊、IPRO Edge AI 程式設計指南（向 INTELPRO 索取）。
