---
title: "IPRO7AI"
description: IPRO7AI 型号的差异、NPU 推理运行库的配置与内存需求，以及在 IPRO7AI Reef EVK 上使用 NPU 的示例
migrate_from:
  - "architecture.html#soc-variants"
  - "ai-npu.html#architecture"
---

# IPRO7AI

IPRO7AI 与 [IPRO7](ipro7.md) 是同一颗裸片：IPRO7AI 启用了 NPU，并在封装内集成 8 MB PSRAM 与 Flash，其余规格（CPU、无线、外设）与 IPRO7 相同。它是 IPRO7AI Reef EVK 的主芯片；本版本 SDK 用它运行摄像头图像识别、IPRO AI Teach 的三种教学工具与 IPRO AI Studio 的板端推理。

<div class="ipro-facts" markdown>
<div><strong>0.1 TOPS</strong><span>NPU</span></div>
<div><strong>8 MB</strong><span>封装内 PSRAM</span></div>
<div><strong>IPRO7AI</strong><span>烧录时的 <code>--chip-variant</code></span></div>
<div><strong>libai.a</strong><span>预编译推理运行库</span></div>
</div>

## 与 IPRO7 的差异 { #soc-variants }

| 项目 | IPRO7AI |
|---|---|
| NPU | 启用，0.1 TOPS；NPU 的 activation 缓冲区放在 PSRAM 中，因此 AI 应用必须启用 PSRAM |
| PSRAM | 封装内 8 MB，地址 `0x1e000000` |
| Flash | 封装内。SDK 默认按 1 MB 布局链接；设置 `CONFIG_IPRO7_FLASH_2M=y` 改用 2 MB 布局。`ipro7ai_reef_demo` 的 `.config` 注明：启动日志报告 JEDEC ID `0xEF4015`（2 MB）时可加入这一行 |
| 烧录 | `--chip-variant IPRO7AI`，选用这颗芯片的 Flash 引脚（工具配置文件中 `flash_pin` 为 `0x9`） |
| 其他 | CPU、内存映射、无线与外设与 IPRO7 相同，见 [IPRO7 主要规格](ipro7.md#key-specs) |

在 Reef 的应用配置中，`ipro_reef_teach`、`ipro_agora_sentino` 的 `.config` 与 `ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` 的 `defconfig_reef` 已设置 2 MB 布局，其他 Reef 配置使用 1 MB 布局。

## NPU 与推理运行库 { #architecture }

推理运行库以预编译库 `components/ai/lib/libai.a` 提供，公开头文件为 `components/ai/iproai_def.h` 与 `components/ai/` 下各模块的头文件；发布包不含推理运行库源代码。V2.2.1 的 `components/ai` 是 IPRO Edge AI 平台 V2.0：运行库、每个工具一个槽位的模型存储区、输入源、预处理与应用框架。等待 NPU 有时间上限，超时会复位 NPU 模块并进入安全的故障状态。CPU 端推理另有 TensorFlow Lite Micro、NMSIS-NN 与 TinyMaix（`components/3rdparty/`）。

### 启用 AI { #config }

在应用的 `.config` 中显式写出下列配置。本 SDK 的构建不会应用 Kconfig 的 `select`，所以 PSRAM 不会自动开启：

```ini title=".config（节选）"
CONFIG_AI_SUPPORT=y          # 链接 components/ai（libai.a）
CONFIG_USE_PSRAM=y           # NPU activation 缓冲区与模型放在 PSRAM 中
CONFIG_MM_SUPPORT=y          # 使用摄像头与 ISP 时
CONFIG_AI_MODEL_FROM_FILE=y  # 从 SD 卡加载模型时
```

`ipro_reef_teach` 的 `.config` 与 `ipro_ai_link` 的 `defconfig_reef` 是完整的 Reef 示例配置。

### 模型存放 { #models }

NPU 使用 `.inm` 格式的模型，可放在三个位置：

| 位置 | 做法 | Reef 上的示例 |
|---|---|---|
| `mfg` Flash 分区 | 烧录工具用 `--mfg` 写入。`ipro_reef_teach` 使用自己的分区表 `partition_reef_teach.toml` 与 `mfg` 布局（模式、声纹、图像与传感模型各一个槽位），烧录内容由 `mfg_payload.py` 生成 | `ipro_reef_teach` |
| 链接进固件 | 模型编译进镜像，无需另外烧录 | `ipro7_uvc_cam` 的 `defconfig_reef_rps` |
| SD 卡 | 运行时把 `.inm` 经 FatFS 从 `sd:/` 读入 PSRAM | `ipro_ai_link` 的 `defconfig_reef` |

发布包附带的模型位于 `apps/ai/ipro_reef_teach/model/`（声纹模型 `model_b.spkb`）、`tools/teach_web/assets/`、`apps/platform/ipro7_demo/demo/ai/ai_model/`、`apps/test/ipro_npu_yolo/src/` 与 `apps/ai/ipro7ai_evk_rps/model/`。IPRO AI Studio 与 Edge AI 工具随单独的 IPRO Edge AI 套件提供，不在 SDK 内；模型转换工具请联系 INTELPRO。

### 内存 { #memory }

同时启用 AI 与图像（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）时，NPU 的 SRAM 映射在 `0x11020000` 以上，链接器把 OCRAM 缩减为前 64 KB（`0x11010000`–`0x11020000`）。应用同时配置了 BLE 控制器的 Exchange Memory（`CONFIG_EM_SIZE` 不为 0）时，OCRAM 再缩减为 48 KB，另有一段 64 KB − `CONFIG_EM_SIZE` 的非保持区。构建时 CMake 会打印实际采用的大小，例如 `AI+MM (EM=0): OCRAM=64KB`。

Zephyr RTOS 版本未提供 NPU 驱动；NPU 示例都是 FreeRTOS 应用。

## 在 Reef 上使用 NPU 的示例 { #sdk-usage }

| 示例 | Reef 配置 | 内容 |
|---|---|---|
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `.config` | IPRO AI Teach 2.0 的板端固件：`image`（USB 摄像头与图像分类）、`voice`（声纹）、`sensor`（传感器信号）三种工具，一次运行一种，由 IPRO AI Studio 操作 |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `defconfig_reef_rps` | USB 摄像头，把 NPU 石头剪刀布的识别结果绘制到图像中 |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `defconfig_reef` | IPRO AI Studio “Run on board”的板端固件：从 `sd:/` 加载模型与输入，经 USB 返回输出 |

其他 NPU 示例以 IPRO7AI EVK 或 IPRO7 EVB 为目标（`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro7ai_evk_launcher`、`ipro_speaker_recog`、`ipro_npu_yolo`、`ipro_ai_bench`），见[示例](../../examples/index.md)。

## 搭载 IPRO7AI 的开发板 { #boards }

| 开发板 | 封装 | 板级配置 |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | QFN56，焊在板上 | `CONFIG_IPRO7AI_REEF=y` |

IPRO7AI EVK（`CONFIG_IPRO7AI_EVK=y`）也使用这颗芯片；供货请联系 INTELPRO。

## 相关文档 { #documents }

- [IPRO7](ipro7.md)：完整芯片规格与内存映射。
- [AI 与 NPU 指南](../../guides/ai-npu.md)：模型部署与推理 API。
- [IPRO AI Teach](../../teach/index.md)：在 Reef 上用 IPRO AI Studio 教开发板识别图像、声纹与传感器信号。
- IPRO7 规格书：见[文档下载](../../documents/index.md)。
