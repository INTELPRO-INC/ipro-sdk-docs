---
title: "IPRO7AI"
description: What sets the IPRO7AI apart, how to configure the NPU runtime and its memory, and the NPU examples on the IPRO7AI Reef EVK
migrate_from:
  - "architecture.html#soc-variants"
  - "ai-npu.html#architecture"
---

# IPRO7AI

IPRO7AI is the same die as [IPRO7](ipro7.md) with the NPU enabled and 8 MB of PSRAM and the flash in the package; CPU, wireless and peripherals are the same as IPRO7. It is the main chip of the IPRO7AI Reef EVK. In this release it runs camera object recognition, the three IPRO AI Teach tools and on-board inference for IPRO AI Studio.

<div class="ipro-facts" markdown>
<div><strong>0.1 TOPS</strong><span>NPU</span></div>
<div><strong>8 MB</strong><span>PSRAM in the package</span></div>
<div><strong>IPRO7AI</strong><span><code>--chip-variant</code> when flashing</span></div>
<div><strong>libai.a</strong><span>prebuilt inference runtime</span></div>
</div>

## Differences from IPRO7 { #soc-variants }

| Item | IPRO7AI |
|---|---|
| NPU | Enabled, 0.1 TOPS; the NPU's activation buffers live in PSRAM, so every AI application needs PSRAM |
| PSRAM | 8 MB in the package, at `0x1e000000` |
| Flash | In the package. The SDK links a 1 MB layout by default; `CONFIG_IPRO7_FLASH_2M=y` selects the 2 MB layout. The `.config` of `ipro7ai_reef_demo` notes that you can add this line when the boot log reports JEDEC ID `0xEF4015` (2 MB) |
| Flashing | `--chip-variant IPRO7AI` selects this chip's flash pins (`flash_pin` `0x9` in the tool's configuration file) |
| Everything else | CPU, memory map, wireless and peripherals as on IPRO7, see [IPRO7 key specifications](ipro7.md#key-specs) |

Among the Reef configurations, the `.config` of `ipro_reef_teach` and `ipro_agora_sentino` and the `defconfig_reef` of `ipro_ble_remote`, `ipro_le_audio_headset` and `ipro_ai_link` already use the 2 MB layout; the other Reef configurations use the 1 MB layout.

## NPU and inference runtime { #architecture }

The inference runtime ships as the prebuilt library `components/ai/lib/libai.a`; its public headers are `components/ai/iproai_def.h` and the headers of the modules under `components/ai/`. The runtime source is not in the package. In V2.3.0 `components/ai` is the IPRO Edge AI platform V2.0: runtime, a model store with one slot per tool, input sources, preprocessing and an application framework. Waits on the NPU are bounded; a timeout resets the NPU block and leaves it in a safe fault state. For inference on the CPU there are TensorFlow Lite Micro, NMSIS-NN and TinyMaix (`components/3rdparty/`).

### Enable AI { #config }

Write these settings explicitly in the application's `.config`. This SDK's build does not apply Kconfig `select`, so PSRAM is not turned on for you:

```ini title=".config (excerpt)"
CONFIG_AI_SUPPORT=y          # link components/ai (libai.a)
CONFIG_USE_PSRAM=y           # NPU activation buffers and models live in PSRAM
CONFIG_MM_SUPPORT=y          # when you use the camera and the ISP
CONFIG_AI_MODEL_FROM_FILE=y  # when you load models from the SD card
```

The `.config` of `ipro_reef_teach` and the `defconfig_reef` of `ipro_ai_link` are complete Reef configurations to start from.

### Where models live { #models }

The NPU runs models in the `.inm` format, stored in one of three places:

| Location | How | Reef example |
|---|---|---|
| `mfg` flash partition | Written by the flash tool with `--mfg`. `ipro_reef_teach` has its own partition table `partition_reef_teach.toml` and `mfg` layout (one slot each for the mode, the voiceprint, image and sensor models); `mfg_payload.py` builds what you flash | `ipro_reef_teach` |
| Linked into the firmware | The model is built into the image; nothing else to flash | `defconfig_reef_rps` of `ipro7_uvc_cam` |
| SD card | Read from `sd:/` (FatFS) into PSRAM at run time | `defconfig_reef` of `ipro_ai_link` |

Models in the package: `apps/ai/ipro_reef_teach/model/` (the voiceprint model `model_b.spkb`), `tools/teach_web/assets/`, `apps/platform/ipro7_demo/demo/ai/ai_model/`, `apps/test/ipro_npu_yolo/src/` and `apps/ai/ipro7ai_evk_rps/model/`. IPRO AI Studio and the Edge AI tools ship in the separate IPRO Edge AI package, not in the SDK; contact INTELPRO for the model conversion tool.

### Memory { #memory }

With AI and imaging both enabled (`CONFIG_AI_SUPPORT`, `CONFIG_MM_SUPPORT`), the NPU's SRAM is mapped from `0x11020000` up, so the linker limits OCRAM to the first 64 KB (`0x11010000`–`0x11020000`). When the application also reserves BLE controller Exchange Memory (`CONFIG_EM_SIZE` not 0), OCRAM shrinks to 48 KB plus a non-retained region of 64 KB − `CONFIG_EM_SIZE`. CMake prints the layout it chose during the build, for example `AI+MM (EM=0): OCRAM=64KB`.

The Zephyr RTOS port has no NPU driver; the NPU examples are FreeRTOS applications.

## NPU examples on the Reef { #sdk-usage }

| Example | Reef configuration | What it does |
|---|---|---|
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `.config` | Board firmware for IPRO AI Teach 2.0: three tools, `image` (USB camera and image classifier), `voice` (voiceprint) and `sensor` (sensor signals), one at a time, driven from IPRO AI Studio |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `defconfig_reef_rps` | USB webcam that draws the NPU's rock-paper-scissors result into the video |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `defconfig_reef` | Board firmware for IPRO AI Studio "Run on board": loads models and inputs from `sd:/` and returns the outputs over USB |

The other NPU examples target the IPRO7AI EVK or the IPRO7 EVB (`ipro7ai_evk_person_detect`, `ipro7ai_evk_rps`, `ipro7ai_evk_launcher`, `ipro_speaker_recog`, `ipro_npu_yolo`, `ipro_ai_bench`); see [Examples](../../examples/index.md).

## Boards with IPRO7AI { #boards }

| Board | Package | Board configuration |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | QFN56, soldered on the board | `CONFIG_IPRO7AI_REEF=y` |

The IPRO7AI EVK (`CONFIG_IPRO7AI_EVK=y`) also carries this chip; contact INTELPRO for it.

## Related documents { #documents }

- [IPRO7](ipro7.md): full chip specifications and memory map.
- [AI & NPU guide](../../guides/ai-npu.md): deploying models and the inference API.
- [IPRO AI Teach](../../teach/index.md): teach the Reef to recognize images, voiceprints and sensor signals with IPRO AI Studio.
- IPRO7 datasheet: see [Documents](../../documents/index.md).
