---
title: "IPRO7AI"
description: IPRO7AI 型號的差異、NPU 推論執行庫的設定與記憶體需求，以及在 IPRO7AI Reef EVK 上使用 NPU 的範例
migrate_from:
  - "architecture.html#soc-variants"
  - "ai-npu.html#architecture"
---

# IPRO7AI

IPRO7AI 與 [IPRO7](ipro7.md) 是同一顆晶粒：IPRO7AI 啟用 NPU，並在封裝內放入 8 MB PSRAM 與 Flash，其餘規格（CPU、無線、周邊）與 IPRO7 相同。它是 IPRO7AI Reef EVK 的主晶片；本版 SDK 用它執行相機影像辨識、IPRO AI Teach 的三種教學工具與 IPRO AI Studio 的板端推論。

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
| Flash | 封裝內。SDK 預設連結 1 MB 版面；設定 `CONFIG_IPRO7_FLASH_2M=y` 改用 2 MB 版面。`ipro7ai_reef_demo` 的 `.config` 註明：開機訊息回報 JEDEC ID `0xEF4015`（2 MB）時可加入這一行 |
| 燒錄 | `--chip-variant IPRO7AI`，選用這顆晶片的 Flash 腳位（工具設定檔中 `flash_pin` 為 `0x9`） |
| 其他 | CPU、記憶體配置、無線與周邊與 IPRO7 相同，見 [IPRO7 主要規格](ipro7.md#key-specs) |

Reef 的應用設定中，`ipro_reef_teach`、`ipro_agora_sentino` 的 `.config` 與 `ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` 的 `defconfig_reef` 已設定 2 MB 版面，其他 Reef 設定使用 1 MB 版面。

## NPU 與推論執行庫 { #architecture }

推論執行庫以預編譯函式庫 `components/ai/lib/libai.a` 提供，公開標頭為 `components/ai/iproai_def.h` 與 `components/ai/` 下各模組的標頭；套件不含推論執行庫原始碼。V2.3.0 的 `components/ai` 是 IPRO Edge AI 平台 V2.0：執行庫、每個工具一個槽位的模型儲存區、輸入來源、前處理與應用框架。等待 NPU 有時間上限，逾時會重置 NPU 區塊並進入安全的故障狀態。CPU 端推論另有 TensorFlow Lite Micro、NMSIS-NN 與 TinyMaix（`components/3rdparty/`）。

### 啟用 AI { #config }

在應用的 `.config` 明確寫出下列設定。本 SDK 的建置不會套用 Kconfig 的 `select`，所以 PSRAM 不會自動打開：

```ini title=".config（節錄）"
CONFIG_AI_SUPPORT=y          # 連結 components/ai（libai.a）
CONFIG_USE_PSRAM=y           # NPU activation 緩衝區與模型放在 PSRAM
CONFIG_MM_SUPPORT=y          # 使用相機與 ISP 時
CONFIG_AI_MODEL_FROM_FILE=y  # 從 SD 卡載入模型時
```

`ipro_reef_teach` 的 `.config` 與 `ipro_ai_link` 的 `defconfig_reef` 是完整的 Reef 範例設定。

### 模型存放 { #models }

NPU 使用 `.inm` 格式的模型，可放在三個位置：

| 位置 | 做法 | Reef 上的範例 |
|---|---|---|
| `mfg` Flash 分割區 | 燒錄工具以 `--mfg` 寫入。`ipro_reef_teach` 使用自己的分割表 `partition_reef_teach.toml` 與 `mfg` 配置（模式、聲紋、影像與感測模型各一個槽位），燒錄內容由 `mfg_payload.py` 產生 | `ipro_reef_teach` |
| 連結進韌體 | 模型編進映像，不必另外燒錄 | `ipro7_uvc_cam` 的 `defconfig_reef_rps` |
| SD 卡 | 執行時把 `.inm` 由 FatFS 的 `sd:/` 讀入 PSRAM | `ipro_ai_link` 的 `defconfig_reef` |

套件隨附的模型位於 `apps/ai/ipro_reef_teach/model/`（聲紋模型 `model_b.spkb`）、`tools/teach_web/assets/`、`apps/platform/ipro7_demo/demo/ai/ai_model/`、`apps/test/ipro_npu_yolo/src/` 與 `apps/ai/ipro7ai_evk_rps/model/`。IPRO AI Studio 與 Edge AI 工具隨另外的 IPRO Edge AI 套件提供，不在 SDK 內；模型轉換工具請洽 INTELPRO。

### 記憶體 { #memory }

同時啟用 AI 與影像（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）時，NPU 的 SRAM 映射在 `0x11020000` 以上，連結器把 OCRAM 縮為前 64 KB（`0x11010000`–`0x11020000`）。應用同時設定 BLE 控制器的 Exchange Memory（`CONFIG_EM_SIZE` 不為 0）時，OCRAM 再縮為 48 KB，另有一段 64 KB − `CONFIG_EM_SIZE` 的非保留區。建置時 CMake 會印出實際採用的大小，例如 `AI+MM (EM=0): OCRAM=64KB`。

Zephyr RTOS 版本未提供 NPU 驅動；NPU 範例都是 FreeRTOS 應用。

## 在 Reef 上使用 NPU 的範例 { #sdk-usage }

| 範例 | Reef 設定 | 內容 |
|---|---|---|
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `.config` | IPRO AI Teach 2.0 的板端韌體：`image`（USB 相機與影像分類）、`voice`（聲紋）、`sensor`（感測訊號）三種工具，一次執行一種，由 IPRO AI Studio 操作 |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `defconfig_reef_rps` | USB 網路攝影機，把 NPU 剪刀石頭布的辨識結果畫進影像 |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `defconfig_reef` | IPRO AI Studio「Run on board」的板端韌體：從 `sd:/` 載入模型與輸入，經 USB 傳回輸出 |

其他 NPU 範例以 IPRO7AI EVK 或 IPRO7 EVB 為目標（`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro7ai_evk_launcher`、`ipro_speaker_recog`、`ipro_npu_yolo`、`ipro_ai_bench`），見[範例](../../examples/index.md)。

## 搭載 IPRO7AI 的開發板 { #boards }

| 開發板 | 封裝 | 板級設定 |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | QFN56，焊在板上 | `CONFIG_IPRO7AI_REEF=y` |

IPRO7AI EVK（`CONFIG_IPRO7AI_EVK=y`）也使用這顆晶片；供應請洽 INTELPRO。

## 相關文件 { #documents }

- [IPRO7](ipro7.md)：完整晶片規格與記憶體配置。
- [AI 與 NPU 指南](../../guides/ai-npu.md)：模型部署與推論 API。
- [IPRO AI Teach](../../teach/index.md)：在 Reef 上以 IPRO AI Studio 教會板子辨識影像、聲紋與感測訊號。
- IPRO7 規格書：見[文件下載](../../documents/index.md)。
