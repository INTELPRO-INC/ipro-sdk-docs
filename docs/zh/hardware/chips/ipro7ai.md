---
title: "IPRO7AI"
description: IPRO7AI 型號的差異、NPU 推論執行庫的設定與記憶體需求，以及使用 NPU 的 SDK 範例
migrate_from:
  - "architecture.html#soc-variants"
  - "ai-npu.html#architecture"
---

# IPRO7AI

IPRO7AI 與 [IPRO7](ipro7.md) 是同一顆晶粒：IPRO7AI 啟用 NPU，並在封裝內放入 8 MB PSRAM。其餘規格（CPU、無線、周邊）與 IPRO7 相同。本版 SDK 用它執行相機影像辨識、手勢分類與 IPRO AI Studio 的板端推論；IPRO7AI EVK 與 IPRO7AI Reef EVK 都使用這顆晶片。

<div class="ipro-facts" markdown>
<div><strong>0.1 TOPS</strong><span>NPU</span></div>
<div><strong>8 MB</strong><span>封裝內 PSRAM</span></div>
<div><strong>IPRO7AI</strong><span>燒錄時的 <code>--chip-variant</code></span></div>
<div><strong>libai.a</strong><span>預編譯推論執行庫</span></div>
</div>

## 與 IPRO7 的差異 { #soc-variants }

| 項目 | IPRO7AI |
|---|---|
| NPU | 啟用，0.1 TOPS；NPU 的 activation 緩衝區放在 PSRAM，所以 AI 應用一定要開 PSRAM |
| PSRAM | 封裝內 8 MB，位址 `0x1e000000` |
| Flash | 封裝內，依料號為 1 MB 或 2 MB；SDK 預設連結 1 MB 版面，兩種都放得下。開機訊息回報 JEDEC ID `0xEF4015`（2 MB）時，可在 `.config` 加入 `CONFIG_IPRO7_FLASH_2M=y` 使用整顆 Flash |
| 燒錄 | `--chip-variant IPRO7AI`，選用這顆晶片的 Flash 腳位（工具設定檔中 `flash_pin` 為 `0x9`） |
| 其他 | CPU、記憶體配置、無線與周邊與 IPRO7 相同，見 [IPRO7 主要規格](ipro7.md#key-specs) |

## NPU 與推論執行庫 { #architecture }

推論執行庫以預編譯函式庫 `components/ai/lib/libai.a` 提供，公開標頭在 `components/ai/`（`iproai_def.h`）與 `components/ai/src/`。套件不含推論執行庫原始碼；CPU 端推論另有 TensorFlow Lite Micro、NMSIS-NN 與 TinyMaix（`components/3rdparty/`）。

### 啟用 AI { #config }

在應用的 `.config` 明確寫出下列設定。本 SDK 的建置不會套用 Kconfig 的 `select`，所以 PSRAM 不會自動打開：

```ini title=".config（節錄）"
CONFIG_AI_SUPPORT=y          # 連結 components/ai（libai.a）
CONFIG_USE_PSRAM=y           # NPU activation 緩衝區與模型放在 PSRAM
CONFIG_MM_SUPPORT=y          # 使用相機與 ISP 時
CONFIG_AI_MODEL_FROM_FILE=y  # 從 SD 卡載入模型時
```

### 模型存放 { #models }

NPU 使用 `.inm` 格式的模型，可放在三個位置：

| 位置 | 做法 | 範例 |
|---|---|---|
| `mfg` Flash 分割區 | 模型放在分割區起點 +0x1000，燒錄工具以 `--mfg` 寫入；應用目錄內的 `flash.sh --full` 一次寫入分割表、韌體與模型 | `ipro7ai_evk_person_detect` |
| 連結進韌體 | 模型以組語檔嵌入映像 | `ipro7ai_evk_rps`（`CONFIG_RPS_EMBED_MODEL=y`）、`ipro_npu_yolo` |
| SD 卡 | 開機時把整個 `.inm` 讀入 PSRAM，路徑使用 FatFS 的 `sd:/`（例如 `sd:/models/person.inm`） | `ipro7ai_evk_launcher` 的偵測頁、`ipro_ai_link` |

套件隨附的模型位於 `apps/platform/ipro7_demo/demo/ai/ai_model/`、`apps/test/ipro_npu_yolo/src/` 與 `apps/ai/ipro7ai_evk_rps/model/`。模型轉換工具未包含於 V2.1.0，請洽 INTELPRO。`ipro7ai_evk_rps/train/` 另附該分類模型的訓練腳本。

### 記憶體 { #memory }

同時啟用 AI 與影像（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）時，連結器把 OCRAM 可用區縮為 64 KB，使用 BLE 時再縮為 48 KB；BLE 控制器與 Host 約需 67 KB OCRAM，因此同一個映像不能同時啟用 NPU 與 BLE，`ipro7ai_evk_demo` 為此把 AI（`config_ai`）與藍牙（`config_bt`）分成不同設定。各組合的 OCRAM 大小見[建置系統與設定](../../guides/build-system.md#memory-layout)。

Zephyr RTOS 版本未提供 NPU 驅動；NPU 範例都是 FreeRTOS 應用。

## SDK 中的 AI 範例 { #sdk-usage }

| 範例 | 開發板（設定） | 內容 |
|---|---|---|
| `ipro7ai_evk_person_detect` | IPRO7AI EVK | 相機預覽與 YOLOv8 人物／寵物框，模型在 `mfg` 分割區 |
| `ipro7ai_evk_rps` | IPRO7AI EVK | 剪刀石頭布：4 類 int8 CNN，模型連結進韌體，附訓練腳本 |
| `ipro7ai_evk_launcher` | IPRO7AI EVK | 以 NPU 辨識手勢切換頁面；第二個模型做人物／寵物偵測 |
| `ipro7_uvc_cam` | Reef（`defconfig_reef_rps`） | USB 網路攝影機，把剪刀石頭布結果畫進影像串流 |
| `ipro_ai_link` | IPRO7 EVB；Reef（`defconfig_reef`） | IPRO AI Studio「Run on board」的板端韌體：從 `sd:/` 載入模型與輸入，經 USB 傳回輸出 |
| `ipro_npu_yolo` | IPRO7 EVB | NPU 上的 YOLOv8 人物／寵物偵測 |
| `ipro_ai_bench` | IPRO7 EVB | NPU 與 CPU 推論時間比較 |

建置與使用方式見各應用目錄的 README，以及 [AI 與 NPU 指南](../../guides/ai-npu.md)。

## 搭載 IPRO7AI 的開發板 { #boards }

| 開發板 | 封裝 | 板級設定 |
|---|---|---|
| [IPRO7AI Reef EVK](../boards/reef-evk.md) | QFN56，焊於載板 | `CONFIG_IPRO7AI_REEF=y` |
| [IPRO7AI EVK](../boards/ipro7ai-evk.md) | 模組，裝在 EVK 子板上 | `CONFIG_IPRO7AI_EVK=y` |

## 相關文件 { #documents }

- [IPRO7](ipro7.md)：完整晶片規格與記憶體配置。
- [AI 與 NPU 指南](../../guides/ai-npu.md)：模型部署與推論 API。
- IPRO7 規格書：見 [文件下載](../../documents/index.md)。
