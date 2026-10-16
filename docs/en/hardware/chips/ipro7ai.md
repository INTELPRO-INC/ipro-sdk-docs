---
title: "IPRO7AI"
description: How the IPRO7AI variant differs, how to set up the NPU runtime and its memory needs, and the SDK examples that use the NPU
migrate_from:
  - "architecture.html#soc-variants"
  - "ai-npu.html#architecture"
---

# IPRO7AI

IPRO7AI is the same die as [IPRO7](ipro7.md) with the NPU enabled and 8 MB of PSRAM inside the package. Everything else (CPU, radio, peripherals) matches IPRO7. In this SDK release it runs camera object detection, gesture classification and on-board inference for IPRO AI Studio; both the IPRO7AI EVK and the IPRO7AI Reef EVK carry it.

<div class="ipro-facts" markdown>
<div><strong>0.1 TOPS</strong><span>NPU</span></div>
<div><strong>8 MB</strong><span>In-package PSRAM</span></div>
<div><strong>IPRO7AI</strong><span><code>--chip-variant</code> when flashing</span></div>
<div><strong>libai.a</strong><span>Prebuilt inference runtime</span></div>
</div>

## Differences from IPRO7 { #soc-variants }

| Item | IPRO7AI |
|---|---|
| NPU | Enabled, 0.1 TOPS. NPU activation buffers live in PSRAM, so every AI application needs PSRAM |
| PSRAM | 8 MB in the package, at `0x1e000000` |
| Flash | In the package, 1 MB or 2 MB depending on the part. The SDK links the 1 MB layout by default, which fits both; if the boot log reports JEDEC ID `0xEF4015` (2 MB), add `CONFIG_IPRO7_FLASH_2M=y` to `.config` to use the whole part |
| Flashing | `--chip-variant IPRO7AI` selects this chip's flash pins (`flash_pin` = `0x9` in the tool's settings file) |
| Everything else | CPU, memory map, radio and peripherals as on IPRO7, see [IPRO7 key specifications](ipro7.md#key-specs) |

## NPU and inference runtime { #architecture }

The inference runtime ships as the prebuilt library `components/ai/lib/libai.a`, with public headers in `components/ai/` (`iproai_def.h`) and `components/ai/src/`. The package contains no runtime source. For inference on the CPU, TensorFlow Lite Micro, NMSIS-NN and TinyMaix are in `components/3rdparty/`.

### Enable AI { #config }

Write these settings into the application's `.config` explicitly. This SDK's build does not apply Kconfig `select`, so PSRAM is not turned on for you:

```ini title=".config (excerpt)"
CONFIG_AI_SUPPORT=y          # link components/ai (libai.a)
CONFIG_USE_PSRAM=y           # NPU activation buffers and models live in PSRAM
CONFIG_MM_SUPPORT=y          # when you use the camera and ISP
CONFIG_AI_MODEL_FROM_FILE=y  # when you load models from the SD card
```

### Where models live { #models }

The NPU runs models in the `.inm` format, stored in one of three places:

| Location | How | Example |
|---|---|---|
| `mfg` flash partition | The model sits at partition start + 0x1000 and the flash tool writes it with `--mfg`; `flash.sh --full` in the application directory writes the partition table, firmware and model in one go | `ipro7ai_evk_person_detect` |
| Linked into the firmware | The model is embedded in the image through an assembly file | `ipro7ai_evk_rps` (`CONFIG_RPS_EMBED_MODEL=y`), `ipro_npu_yolo` |
| SD card | At boot the whole `.inm` is read into PSRAM; paths use FatFS `sd:/` (for example `sd:/models/person.inm`) | the detection page of `ipro7ai_evk_launcher`, `ipro_ai_link` |

The package ships models in `apps/platform/ipro7_demo/demo/ai/ai_model/`, `apps/test/ipro_npu_yolo/src/` and `apps/ai/ipro7ai_evk_rps/model/`. The model conversion tool is not included in V2.1.0; contact INTELPRO. `ipro7ai_evk_rps/train/` also has the training scripts for that classifier.

### Memory { #memory }

With both AI and imaging enabled (`CONFIG_AI_SUPPORT`, `CONFIG_MM_SUPPORT`), the linker shrinks the OCRAM region to 64 KB, and to 48 KB when BLE is also used. The BLE controller and host need about 67 KB of OCRAM, so one image cannot use both the NPU and BLE; that is why `ipro7ai_evk_demo` splits AI (`config_ai`) and Bluetooth (`config_bt`) into separate configurations. The OCRAM size for each combination is in [Build System & Configuration](../../guides/build-system.md#memory-layout).

The Zephyr RTOS port has no NPU driver in this release; the NPU examples are FreeRTOS applications.

## AI examples in the SDK { #sdk-usage }

| Example | Board (configuration) | What it does |
|---|---|---|
| `ipro7ai_evk_person_detect` | IPRO7AI EVK | Camera preview with YOLOv8 person / pet boxes; model in the `mfg` partition |
| `ipro7ai_evk_rps` | IPRO7AI EVK | Rock-paper-scissors against a 4-class int8 CNN linked into the firmware; training scripts included |
| `ipro7ai_evk_launcher` | IPRO7AI EVK | Pages switched by hand gestures recognized on the NPU; a second model detects people and pets |
| `ipro7_uvc_cam` | Reef (`defconfig_reef_rps`) | USB webcam that draws rock-paper-scissors results into the video stream |
| `ipro_ai_link` | IPRO7 EVB; Reef (`defconfig_reef`) | Board firmware for IPRO AI Studio "Run on board": model and input from `sd:/`, outputs back over USB |
| `ipro_npu_yolo` | IPRO7 EVB | YOLOv8 person / pet detection on the NPU |
| `ipro_ai_bench` | IPRO7 EVB | NPU versus CPU inference timing |

For build and usage, see each application's README and the [AI and NPU guide](../../guides/ai-npu.md).

## Boards with IPRO7AI { #boards }

| Board | Package | Board configuration |
|---|---|---|
| [IPRO7AI Reef EVK](../boards/reef-evk.md) | QFN56, soldered on the carrier | `CONFIG_IPRO7AI_REEF=y` |
| [IPRO7AI EVK](../boards/ipro7ai-evk.md) | Module on the EVK sub-board | `CONFIG_IPRO7AI_EVK=y` |

## Related documents { #documents }

- [IPRO7](ipro7.md): full chip specifications and memory map.
- [AI and NPU guide](../../guides/ai-npu.md): model deployment and the inference API.
- IPRO7 datasheet: see [Documents](../../documents/index.md).
