---
title: AI 執行庫
description: NPU 驅動、推論核心、運算子與後處理，以及偵測與語音模型的介面。
generated: tools/gen_api.py
migrate_from: []
---

# AI 執行庫

NPU 驅動、推論核心、運算子與後處理，以及偵測與語音模型的介面。說明取自標頭檔註解（英文）。

| 標頭 | 函式 | 說明 |
|---|---|---|
| [`hal_npu.h`](#hal_npu-h) | 14 | NPU hardware access for IPRO7: clock and bus set-up, layer buffers, network parameters, start, stop and interrupt acknowledge. |
| [`iproai_def.h`](#iproai_def-h) | 0 | AI engine types: model handle, network and layer descriptions, results, callbacks. |
| [`iproai_core.h`](#iproai_core-h) | 13 | AI engine entry points: create a model, load it, run inference, release it. |
| [`iproai_inst_npu.h`](#iproai_inst_npu-h) | 8 | Low-level NPU control used by the AI runtime: set-up, dispatch and teardown. |
| [`iproai_inst_util.h`](#iproai_inst_util-h) | 11 | AI runtime utilities: cache-line aligned allocation, fixed-point conversion and tensor addressing in the model data buffer. |
| [`iproai_inst_postprocess.h`](#iproai_inst_postprocess-h) | 13 | Built-in (legacy) post-processors run by the AI runtime after an inference. |
| [`iproai_riscv_nnfunctions.h`](#iproai_riscv_nnfunctions-h) | 2 | CPU convolution kernel (NMSIS-NN style) used by the AI runtime, with its fixed-point types and limits. |
| [`iproai_cycle_profile.h`](#iproai_cycle_profile-h) | 10 | Cycle-accurate NPU-busy versus CPU-busy split of model inference. |
| [`yolov8_detect.h`](#yolov8_detect-h) | 12 | YOLOv8 detection post-processor for 6-output NPU models, plus the box and NMS helpers shared by the other detectors. |
| [`yolov8_person_pet_detect.h`](#yolov8_person_pet_detect-h) | 5 | Person and pet detection: YOLOv8 post-processor preset. |
| [`gesture_dfl_detect.h`](#gesture_dfl_detect-h) | 4 | Post-processor for the hand-sign digit detector (YOLOv8-ReLU, anchor-free with DFL boxes) on the IPRO7-AI NPU. |
| [`big_a_sppf_detect.h`](#big_a_sppf_detect-h) | 4 | Post-processor for the BIG-A + SPPF-lite single-class product detector (SKU-110K) on the IPRO7-AI NPU. |
| [`fbank.h`](#fbank-h) | 2 | Log mel-filterbank feature extraction for the speaker-embedding model. |
| [`embedding_dim.h`](#embedding_dim-h) | 0 | Length of the speaker-embedding vector shared by the speaker modules. |
| [`speaker_embed.h`](#speaker_embed-h) | 3 | Speaker-embedding engine: PCM clip in, normalised voiceprint out. |
| [`speaker_recog.h`](#speaker_recog-h) | 20 | Speaker recognition on a pooled NPU feature map: embeddings, registration and identification. |
| [`gallery.h`](#gallery-h) | 10 | Enrolled-speaker gallery: enrollment, identification and verification. |
| [`diarize.h`](#diarize-h) | 2 | Speaker diarization: online clustering of speaker embeddings. |

## hal_npu.h { #hal_npu-h }

`#include "hal_npu.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_npu.h)）

NPU hardware access for IPRO7: clock and bus set-up, layer buffers, network parameters, start, stop and interrupt acknowledge.

These functions program the NPU registers directly. They are used by the AI runtime, which drives the NPU layer by layer; most applications use the runtime API instead of calling them. A typical sequence is: [`NPU_Clk_Div()`](#NPU_Clk_Div) and [`NPU_Bus_Setting()`](#NPU_Bus_Setting) once; for each model or layer, [`hal_npu_layer_setup()`](#hal_npu_layer_setup), [`hal_npu_set_input_buffer()`](#hal_npu_set_input_buffer) and [`hal_npu_set_net_param()`](#hal_npu_set_net_param); then hal_npu_clk_enable(1) and [`hal_npu_start()`](#hal_npu_start), and wait for the NPU interrupt, whose handler calls [`hal_npu_ack_irq()`](#hal_npu_ack_irq).

### NPU_Clk_Div { #NPU_Clk_Div }

```c
void NPU_Clk_Div(int n);
```

Select the NPU clock source and set its divider.

| 參數 | 說明 |
|---|---|
| `n` | Divider value written to the NPU clock-divider field; the AI runtime uses 0. |

### NPU_Bus_Setting { #NPU_Bus_Setting }

```c
void NPU_Bus_Setting(void);
```

Apply the default NPU bus settings.

Sets the read and write outstanding-transaction limits to 3 and the read and write command lengths to 63.

### hal_npu_clk_enable { #hal_npu_clk_enable }

```c
void hal_npu_clk_enable(uint8_t enable);
```

Enable or disable the NPU clock.

Enabling ungates the multimedia bus clock. Disabling performs no hardware action in this release.

| 參數 | 說明 |
|---|---|
| `enable` | Non-zero to enable, 0 to disable. |

### hal_npu_ack_irq { #hal_npu_ack_irq }

```c
void hal_npu_ack_irq(void);
```

Acknowledge (clear) the NPU interrupt.

Call it from the NPU interrupt handler, and before enabling the interrupt to discard a stale request.

### hal_npu_layer_setup { #hal_npu_layer_setup }

```c
void hal_npu_layer_setup(uint8_t *inst_buf, uint8_t *weights_buf, uint8_t *bias_buf, uint8_t *mult_shift_buf);
```

Set the buffers of the next NPU layer group.

The buffers come from the compiled model and must be readable by the NPU.

| 參數 | 說明 |
|---|---|
| `inst_buf` | NPU instruction stream. |
| `weights_buf` | Weights. |
| `bias_buf` | Biases. |
| `mult_shift_buf` | Requantization multiplier and shift parameters. |

### hal_npu_set_input_buffer { #hal_npu_set_input_buffer }

```c
void hal_npu_set_input_buffer(uint8_t *input_buf, int patch_size);
```

Set the NPU input (working) buffer.

| 參數 | 說明 |
|---|---|
| `input_buf` | Input buffer address. |
| `patch_size` | Image memory segment size, as given by the compiled model. |

### hal_npu_set_net_param { #hal_npu_set_net_param }

```c
void hal_npu_set_net_param(uint8_t unsign_input, uint8_t relu_n, uint8_t use_tflite, uint32_t mode);
```

Set the network-wide NPU parameters.

| 參數 | 說明 |
|---|---|
| `unsign_input` | Non-zero if the input data are unsigned 8-bit values. |
| `relu_n` | ReLU-N setting of the model; not used in this release. |
| `use_tflite` | Non-zero to load the requantization parameters from memory (models with TensorFlow Lite-style quantization). |
| `mode` | Input mode code from the compiled model (2-bit field). |

### hal_npu_reset_unsign { #hal_npu_reset_unsign }

```c
void hal_npu_reset_unsign(void);
```

Clear the unsigned-input flag set by [`hal_npu_set_net_param()`](#hal_npu_set_net_param).

Used for the layer groups after the first one, whose inputs are signed.

### hal_npu_start { #hal_npu_start }

```c
void hal_npu_start(void);
```

Start the NPU, or resume it after it has halted.

The first call after reset or [`hal_npu_stop()`](#hal_npu_stop) starts execution; later calls resume it. The NPU raises its interrupt when it halts.

### hal_npu_stop { #hal_npu_stop }

```c
void hal_npu_stop(void);
```

Stop the NPU.

The next [`hal_npu_start()`](#hal_npu_start) issues a start instead of a resume.

### NPU_Img_Ext_Addr_Cfg { #NPU_Img_Ext_Addr_Cfg }

```c
void NPU_Img_Ext_Addr_Cfg(uint32_t addr);
```

Set the external image input address.

| 參數 | 說明 |
|---|---|
| `addr` | Address of the input data that the NPU reads for external input. |

### NPU_Img_Ext_Addr_Get { #NPU_Img_Ext_Addr_Get }

```c
uint32_t NPU_Img_Ext_Addr_Get(void);
```

Get the external image input address.

**回傳值**：The address set by [`NPU_Img_Ext_Addr_Cfg()`](#NPU_Img_Ext_Addr_Cfg).

### NPU_Bus_Delay { #NPU_Bus_Delay }

```c
void NPU_Bus_Delay(uint8_t enable, uint8_t rcmd, uint8_t wcmd);
```

Set the NPU bus read and write command lengths.

| 參數 | 說明 |
|---|---|
| `enable` | Not used in this release. |
| `rcmd` | Read command length, 0 to 63. |
| `wcmd` | Write command length, 0 to 63. |

!!! warning "警告"
    Values above 63 are not masked and spill into the neighbouring bus settings.

### NPU_SRAM_EN { #NPU_SRAM_EN }

```c
void NPU_SRAM_EN();
```

Set the NPU enable bit in the SoC SRAM configuration register.

### 型別定義 { #hal_npu-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `imgBuffer` | `char* imgBuffer` | Image buffer used by the AI runtime for external input. A weak definition initialized to NULL is provided; an application that feeds external input defines its own. The runtime reads the input data from `imgBuffer + 4`; the first 4 bytes are a size header. |

## iproai_def.h { #iproai_def-h }

`#include "iproai_def.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/iproai_def.h)）

AI engine types: model handle, network and layer descriptions, results, callbacks.

These definitions are shared by the AI engine library and applications. Read them together with [`iproai_core.h`](#iproai_core-h), which declares the functions that create a model, load it, run inference and release it.

After a model is loaded, [`iproai_getNetInfo()`](#iproai_getNetInfo) returns its struct [`iproai_net_info_t`](#iproai_net_info_t). The `layers` array of that structure holds one struct [`cpu_inst_layer_t`](#cpu_inst_layer_t) per layer, and `output_layer` lists the layers whose outputs are the model outputs.

All tensors of a model live in one working buffer, returned by [`iproai_getInputBuffer()`](#iproai_getInputBuffer). The buffer is divided into patches of `patch_size` bytes and every tensor starts at a patch boundary: the output of layer `l` starts at byte offset `l->out_layer_mem * net->patch_size`. Tensors are stored in height, width, channel order. A layer that runs on the NPU (`NPU_on`) stores its output with the channel count rounded up to a multiple of 4; the padding bytes carry no data.

For a TensorFlow Lite model (`use_tflite`), an output byte `q`, read as unsigned, has the real value `output_scale * (q - tf_output_offset)`:

```c
struct iproai_net_info_t *net = iproai_getNetInfo(hdl);
const struct cpu_inst_layer_t *l = &net->layers[net->output_layer[0]];
const uint8_t *base = iproai_getInputBuffer(hdl);
const uint8_t *q = base + (uint32_t)l->out_layer_mem * (uint32_t)net->patch_size;
float v0 = l->output_scale * ((int)q[0] - l->tf_output_offset);
```

### IPROAI_Device_Type_e { #IPROAI_Device_Type_e }

Compute device identifiers, stored in `IPROAI_Model_t::dev` (not read by the library).

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_DEVICE_CPU` | `0` | The CPU. |
| `IPROAI_DEVICE_NPU` | `1` | The NPU. |
| `IPROAI_DEVICE_UNKNOWN` |  | Unknown device. |

### IPROAI_Feature_Level_e { #IPROAI_Feature_Level_e }

Engine feature levels, stored in `IPROAI_Model_t::level` (not read by the library).

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_FEATURE_LEVEL_1` | `0` | Feature level 1. |
| `IPROAI_FEATURE_LEVEL_UNKNOWN` |  | Unknown feature level. |

### IPROAI_Padding_Mode_e { #IPROAI_Padding_Mode_e }

Convolution padding modes, with TensorFlow naming.

Not used by the current library.

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_PADDING_SAME` | `1` | Output size is input size / stride, rounded up. |
| `IPROAI_PADDING_VALID` | `2` | No padding: the kernel stays inside the input. |

### IPROAI_Status_e { #IPROAI_Status_e }

Status codes returned by the AI engine functions.

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_STATUS_NO_ERROR` | `0` | Success. |
| `IPROAI_STATUS_OUT_OF_MEMORY` |  | A heap allocation failed. |
| `IPROAI_STATUS_INCOMPLETE` |  | Incomplete (not returned by the current library). |
| `IPROAI_STATUS_BAD_DATA` |  | Model data is truncated, inconsistent or unreadable. |
| `IPROAI_STATUS_OP_FAILED` |  | The inference did not complete. |
| `IPROAI_STATUS_UNAVAILABLE_DEVICE` |  | No model instance (NULL handle). |
| `IPROAI_STATUS_INVALID_INPUT` |  | Invalid argument, a file that cannot be opened, or a feature not built into the library. |

### IPROAI_ProcStatus_e { #IPROAI_ProcStatus_e }

States of the inference loop run by [`iproai_startCompute()`](#iproai_startCompute).

The loop alternates between CPU stages and NPU stages until all layers have run.

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_PROCESS_START` | `0` | Start of an inference. |
| `IPROAI_PROCESS_STOP` |  | Defined but not used by the current library. |
| `IPROAI_PROCESS_RESUME` |  | Defined but not used by the current library. |
| `IPROAI_PROCESS_CPU` |  | Run the next layers on the CPU. |
| `IPROAI_PROCESS_NPU` |  | Run the next block of layers on the NPU. |
| `IPROAI_PROCESS_DONE` |  | All layers have run. |
| `IPROAI_PROCESS_FAIL` |  | The loop reached an unexpected state. |

### LAYER_TYPE { #LAYER_TYPE }

Layer operators, stored in `cpu_inst_layer_t::type`.

Several types are fused forms produced by the model converter (for example `CONV_MAX`). Whether a layer runs on the NPU or on the CPU is given by `cpu_inst_layer_t::NPU_on` and `cpu_inst_layer_t::DSP_on`, not by its type.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CONVOLUTIONAL` |  | 2-D convolution (regular, grouped or depthwise). |
| `MAXPOOL` |  | Max pooling. |
| `AVGPOOL` |  | Average pooling. |
| `ROUTE` |  | Concatenation of several inputs along the channel axis. |
| `SHORTCUT` |  | Element-wise addition of two inputs (residual connection). |
| `MATMUL` |  | Fully connected layer (matrix multiplication). |
| `UPSAMPLE` |  | Nearest-neighbour upsampling. |
| `YOLO` |  | Anchor-based YOLO detection head. |
| `SOFTMAX` |  | Softmax. |
| `CONV_MAX` |  | Convolution followed by max pooling, fused into one layer. |
| `ROUTE_MAX` |  | Concatenation followed by max pooling, fused into one layer. |
| `ROUTE_CONV` |  | Concatenation followed by convolution, fused into one layer. |
| `ROUTE_UPSAMPLE` |  | Concatenation followed by upsampling, fused into one layer. |
| `RESHAPE` |  | Reshape. |
| `ROUTE_W` |  | Concatenation along the width or height axis. |
| `LOGISTIC_L` |  | Logistic (sigmoid) function. |
| `SSD` |  | TensorFlow Lite SSD detection post-processing (box decoding and NMS). |
| `TRANSPOSE` |  | Transpose (axis permutation). |
| `PAD` |  | Padding of the width and height axes. |
| `LOG_SOFTMAX` |  | Log-softmax. |
| `DEQUANTIZE` |  | Conversion from 8-bit to float. |
| `TRANSPOSE_LK` |  | Rearrangement of a 1-D input into kernel-sized windows (1-D im2col). |
| `MEAN` |  | Mean reduction. |
| `GATHER` |  | Gather by index. |
| `CUSTOM_L` |  | Operator without a built-in implementation; skipped with a warning. |
| `PRE_TRANSCONV` |  | Input zero-interleaving step of a transposed convolution. |
| `RESIZE_BILINEAR` |  | Bilinear resize. |
| `ARGMAX` |  | Index of the maximum along an axis. |
| `QUANTIZE` |  | Quantization (TensorFlow Lite QUANTIZE). |
| `LEAKY_L` |  | Leaky ReLU. |
| `MUL` |  | Element-wise multiplication. |
| `DEPTH_TO_SPACE` |  | Depth to space. |
| `MINIMUM` |  | Element-wise minimum. |
| `SUB` |  | Element-wise subtraction. |
| `STRIDESLICE` |  | Strided slice. |
| `PRELU_L` |  | Parametric ReLU. |
| `TANH_L` |  | Hyperbolic tangent. |
| `MAXIMUM` |  | Element-wise maximum. |
| `LUT_L` |  | Element-wise lookup through a 256-entry int8 table. The model converter folds a DEQUANTIZE, float operator, QUANTIZE sequence for an element-wise operator that has no integer kernel (ELU, GELU and others) into one table, so the operator runs as a plain byte lookup, without floating point. |
| `UNKNOWN` |  | Unrecognized layer type. |

### APPLICATION_TYPE { #APPLICATION_TYPE }

Application types, stored in `iproai_net_info_t::app_type` and `iproai_result_t::app_type`.

The model converter records the type in the model header. At the end of [`iproai_startCompute()`](#iproai_startCompute) the engine runs the built-in post-processing for that type, if the library includes it, and reports results through the callback set with [`iproai_setResultCB()`](#iproai_setResultCB). Built-in post-processing is present only when the library is built with `CONFIG_AI_LEGACY_YOLO` (for `OBJECT_DETECTION` and `FACE_LANDMARK`) or `CONFIG_AI_LEGACY_POSTPROCESS` (for the other types that have one). Otherwise read the output tensors directly, as shown in the description of [`iproai_def.h`](#iproai_def-h).

| 名稱 | 值 | 說明 |
|---|---|---|
| `CLASSIFICATION` |  | Image classification. Built-in post-processing reports the top class. |
| `OBJECT_DETECTION` |  | Object detection. Built-in YOLO post-processing reports one result per object. |
| `KEYPOINT_DETECTION` |  | Keypoint detection. No built-in post-processing. |
| `FACE_RECONGNITION` |  | Face recognition: the output embedding is compared with the registered identities in `IPROAI_Model_t::post_info`. Built-in post-processing reports the best match. |
| `FACE_LANDMARK` |  | Face detection with five landmark points. Built-in YOLO post-processing reports one result per face. |
| `KEYWORD_SPOTTING` |  | Keyword spotting (audio classification). Built-in post-processing reports the top class. |
| `CUSTOM` |  | Application-defined model. No built-in post-processing. |
| `RETINA_FACE` |  | RetinaFace-style face detection with landmark points. Built-in post-processing reports one result per face. |
| `RETINA_PERSON` |  | RetinaNet-style person detection. Built-in post-processing reports one result per person. |
| `FR_REGISTRATION` |  | Face registration (embedding extraction). No built-in post-processing. |
| `FR_EVALUATION` |  | Face recognition evaluation. Built-in post-processing prints the closest identity on the console and does not call the result callback. |
| `RETINA` |  | RetinaNet-style multi-class detection. Built-in post-processing reports one result per object. |
| `SEGMENTATION` |  | Semantic segmentation. No built-in post-processing. |
| `LOWLIGHT` |  | Low-light image enhancement. No built-in post-processing. |
| `SR` |  | Super-resolution. No built-in post-processing. |

### cpu_inst_layer_t { #cpu_inst_layer_t }

Description of one layer of a loaded model.

The engine fills these records when a model is loaded; applications read them through `iproai_net_info_t::layers`. Tensor positions are patch indices into the working buffer of the model (see the description of [`iproai_def.h`](#iproai_def-h)). Fields not documented here are internal to the engine.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `type` | `int` | Operator, a [`LAYER_TYPE`](#LAYER_TYPE) value. |
| `output_layer` | `bool` | True when the output of this layer is a model output. |
| `h` | `int` | Height of the first input. |
| `w` | `int` | Width of the first input. |
| `c` | `int` | Channel count of the first input. |
| `c2` | `int` | Channel count of the second input as stored in the layer table; for a layer with more than one input `cn[0]` holds the same value. |
| `cn` | `int[MAX_Input_num - 1]` | Channel counts of the second and later inputs of a multi-input layer (`cn[0]` is the second input); 0 when unused. |
| `out_h` | `int` | Output height. |
| `out_w` | `int` | Output width. |
| `out_c` | `int` | Output channel count. |
| `n` | `int` | Count field of the layer table: number of inputs of a concatenation layer, number of anchor masks of a `YOLO` layer. |
| `groups` | `int` | Convolution groups; equal to `c` for a depthwise convolution. |
| `size` | `int` | Kernel size (square kernel). |
| `stride` | `int` | Stride. |
| `dilation` | `int` | Dilation factor. |
| `img_in` | `int` | Non-zero when the layer reads the input image of the model. |
| `in_layer1_mem` | `int` | Patch index of the first input in the working buffer. |
| `in_layer2_mem` | `int` | Patch index of the second input in the working buffer. |
| `out_layer_mem` | `int` | Patch index of the output in the working buffer. |
| `in_layer_mem_n` | `int *` | Patch indices of the third and later inputs (`input_num` - 2 entries), or NULL when the layer has at most two inputs. |
| `ext_input` | `int` | Non-zero when the layer reads its input from the external input address. Set only in the NPU layer records (`iproai_net_info_t::npu_layers`); for the whole model use `iproai_net_info_t::ext_input`. |
| `input_num` | `int` | Number of inputs of the layer. |
| `tf_output_offset` | `int` | Output zero point (TensorFlow Lite models). An output byte `q`, read as unsigned, has the real value `output_scale * (q - tf_output_offset)`. |
| `input_scale` | `float` | Quantization scale of the first input (TensorFlow Lite models). |
| `input2_scale` | `float` | Quantization scale of the second input; recorded for `SSD` layers only. |
| `input3_scale` | `float` | Quantization scale of the anchor input of an `SSD` layer. |
| `output_scale` | `float` | Output quantization scale (TensorFlow Lite models), used with `tf_output_offset`; 0 when the model does not record it. |
| `NPU_on` | `int` | Non-zero when the layer runs on the NPU. |
| `DSP_on` | `int` | Non-zero when the layer runs on the CPU. When both `NPU_on` and `DSP_on` are set, a CPU step prepares the input and the NPU then runs the layer (a transposed convolution, for example). |

### iproai_net_info_t { #iproai_net_info_t }

Description of a loaded model, returned by [`iproai_getNetInfo()`](#iproai_getNetInfo).

[`iproai_create()`](#iproai_create) allocates the structure, the load functions fill it, and it stays valid until [`iproai_free()`](#iproai_free). Applications read it and must not modify it, except for the fields that say so. Fields not documented here are internal to the engine.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `parent` | `void *` | Model instance that owns this description. |
| `layers` | `struct cpu_inst_layer_t *` | Layer records in execution order. |
| `npu_layers` | `struct cpu_inst_layer_t *` | Layer records decoded from the NPU section of the model (`npu_layer_cnt` entries). NULL when the model has no NPU section or when the engine places the layers itself (`use_npu_accel`). |
| `layer_cnt` | `int` | Number of entries in `layers`. |
| `npu_layer_cnt` | `int` | Number of entries in `npu_layers`. |
| `mode` | `int` | 1 if a layer has `img_in` set, else 0; passed to the NPU. |
| `w` | `int` | Input width of the model. |
| `h` | `int` | Input height of the model. |
| `c` | `int` | Input channel count of the model. |
| `IPROAI_version` | `uint16_t` | Model format version from the model header. |
| `patch_size` | `int` | Size of one patch of the working buffer, in bytes. |
| `patch_count` | `int` | Number of patches declared in the model header. The working buffer can be larger: it covers the highest patch index that any layer uses. |
| `unsign_input` | `int` | Non-zero for an unsigned 8-bit input, zero for signed 8-bit. |
| `relu_n` | `int` | ReLU-N clamp value from the model header, passed to the NPU. |
| `use_tflite` | `int` | Non-zero for a model converted from TensorFlow Lite (scale and zero point quantization), zero for the older fixed-point format. |
| `app_type` | `int` | Application type, an [`APPLICATION_TYPE`](#APPLICATION_TYPE) value. |
| `ext_input` | `uint8_t` | Non-zero when the model reads its input image from an external address instead of the working buffer. A load sets that address from `imgBuffer + 4` (the global `imgBuffer` of [`hal_npu.h`](#hal_npu-h)); [`NPU_Img_Ext_Addr_Cfg()`](#NPU_Img_Ext_Addr_Cfg) changes it. |
| `use_npu_accel` | `int` | Non-zero when the engine decides at load time which layers run on the NPU ([`check_IPROAI_NPU_RUN()`](#check_IPROAI_NPU_RUN)); zero when the model records the placement. |
| `output_num` | `int` | Number of model outputs (used entries of `output_layer`). |
| `output_layer` | `int[MAX_Output_num]` | Indices into `layers` of the output layers, in ascending layer order. |
| `prior_bbox` | `float *` | Prior boxes for the built-in RetinaNet-style post-processing, four values per box. The library reads this field but does not fill it; set it before [`iproai_startCompute()`](#iproai_startCompute) when that post-processing is used. |
| `prior_bbox_num` | `int` | Number of boxes in `prior_bbox`. |
| `LUT` | `float *` | Optional lookup table for the logistic function of the built-in `RETINA` post-processing; when NULL the function is computed directly. |
| `LUT2` | `float *` | Optional lookup table for the exponential of the built-in `RETINA` box decoding; when NULL the function is computed directly. |
| `custom_postprocess` | `uint8_t` | Set to 1 by [`iproai_setCustom_Postproc_CB()`](#iproai_setCustom_Postproc_CB), which disables the built-in `FR_EVALUATION` post-processing; cleared by a model load. |

### iproai_model_info_t { #iproai_model_info_t }

Model sections copied from a model blob, with the time spent in the last inference.

A model blob holds eight sections: instruction records, biases, weights, and requantization multipliers and shifts, once for the CPU and once for the NPU. The load functions copy every non-empty section into its own heap buffer; the pointer of an empty section is NULL.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `cpu` | `struct iproai_model_info_t::@255110114267126205036354045056353374026272001316` | CPU sections and timing. |
| `npu` | `struct iproai_model_info_t::@237357377043161174010104124202332121240131257165` | NPU sections and timing. |

### iproai_result_t { #iproai_result_t }

Result reported by the built-in post-processing through [`iproai_inference_cb`](#iproai_def-h-typedefs).

`app_type` selects the member of `r` that holds the result:

- `OBJECT_DETECTION`, `RETINA_FACE`, `RETINA_PERSON`, `RETINA`: `r.objdet` (`RETINA_FACE` also fills the landmark points of `r.landmark`);
- `CLASSIFICATION`, `KEYWORD_SPOTTING`: `r.classification`;
- `FACE_RECONGNITION`: `r.fr`;
- `FACE_LANDMARK`: `r.landmark`.

An `SSD` layer reports each detection with `app_type` set to `OBJECT_DETECTION`. `r.objdet` and `r.landmark` start with the same members, so `best_class`, `prob` and `rect` can be read through either. Coordinates are in pixels of the source resolution set with [`iproai_setSourceResolution()`](#iproai_setSourceResolution).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `r` | `union iproai_result_t::@277331267003060270376160005222203207240143002127` | Result data, selected by `app_type`. |
| `app_type` | `int` | Application type of the result, an [`APPLICATION_TYPE`](#APPLICATION_TYPE) value. |

### IPROAI_Model_t { #IPROAI_Model_t }

Model instance behind an [`iproai_model_hdl_t`](#iproai_def-h-typedefs).

[`iproai_create()`](#iproai_create) allocates it, the load functions fill it and [`iproai_free()`](#iproai_free) releases it. Applications should use the `iproai_*` functions instead of accessing this structure.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `inst` | `struct iproai_model_info_t` | Model sections and inference timing. |
| `dev` | `IPROAI_Device_Type_e` | Compute device; not read by the current library. |
| `level` | `IPROAI_Feature_Level_e` | Feature level; not read by the current library. |
| `buffer` | `uint8_t *` | Working buffer holding every tensor of the model, allocated at load time and returned by [`iproai_getInputBuffer()`](#iproai_getInputBuffer). |
| `share_buffer` | `uint8_t` | Non-zero when `buffer` is provided by the caller instead of being allocated at load time. [`iproai_create()`](#iproai_create) sets 0; [`iproai_free()`](#iproai_free) releases `buffer` in either case. |
| `net` | `struct iproai_net_info_t *` | Network description, returned by [`iproai_getNetInfo()`](#iproai_getNetInfo). |
| `result_cb` | `iproai_inference_cb` | Result callback, set with [`iproai_setResultCB()`](#iproai_setResultCB). |
| `custom_postproc_cb` | `iproai_custom_postproc_cb` | Custom post-processing callback, set with [`iproai_setCustom_Postproc_CB()`](#iproai_setCustom_Postproc_CB). |
| `post_info` | `union IPROAI_Model_t::@252151030357113212227351077331205033021254335210` | Data for the built-in post-processing, set with `load_postprocess_classification()` or `load_postprocess_face_recongnition()`. |
| `in` | `struct IPROAI_Model_t::@040361171307027305232131033063237115223232174106` | Source image resolution, set with [`iproai_setSourceResolution()`](#iproai_setSourceResolution); the built-in post-processing scales coordinates to it. |
| `out` | `struct IPROAI_Model_t::@270062214122352136175366117124225047032250141030` | Output resolution; not used by the current library. |
| `buffer_from_file` | `uint8_t *` | Staging buffer of a model read by [`iproai_load_model_from_file()`](#iproai_load_model_from_file), released by [`iproai_free()`](#iproai_free). Used only when the loader keeps pointers into the file data instead of copying the sections; NULL otherwise. |

### 型別定義 { #iproai_def-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `fixed_point_t` | `typedef int8_t fixed_point_t` | 8-bit element type of the engine's quantized tensors. |
| `iproai_model_hdl_t` | `typedef uint8_t* iproai_model_hdl_t` | Handle to a model instance, returned by [`iproai_create()`](#iproai_create). Treat the handle as opaque and pass it to the `iproai_*` functions. It points to the [`IPROAI_Model_t`](#IPROAI_Model_t) that holds the instance. |
| `iproai_inference_cb` | `typedef void(*) iproai_inference_cb(struct iproai_result_t *detect_result)` | Result callback, set with [`iproai_setResultCB()`](#iproai_setResultCB). Called by the built-in post-processing from the task that runs [`iproai_startCompute()`](#iproai_startCompute): once per inference for a classification, once per object for a detection, and not at all when nothing is detected. |
| `iproai_custom_postproc_cb` | `typedef void(*) iproai_custom_postproc_cb(struct iproai_net_info_t *net, fixed_point_t *DATA_buf, int layer, int size)` | Custom post-processing callback, set with [`iproai_setCustom_Postproc_CB()`](#iproai_setCustom_Postproc_CB). |
| `tflite_230_names` | `const char* const tflite_230_names[128]` | Names of the TensorFlow Lite 2.3 builtin operators, indexed by builtin operator code. The engine uses the table to name operators in console messages, for example for a `CUSTOM_L` layer. The last entry is "NULL". |

### 巨集 { #iproai_def-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `MAX_Input_num` | `(8)` | Number of per-input slots in [`cpu_inst_layer_t`](#cpu_inst_layer_t) (maximum inputs of one layer). |
| `MAX_Output_num` | `(10)` | Capacity of `iproai_net_info_t::output_layer` (maximum number of model outputs). |

## iproai_core.h { #iproai_core-h }

`#include "iproai_core.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/core/include/iproai_core.h)）

AI engine entry points: create a model, load it, run inference, release it.

A model is a blob produced by the model converter. It starts with a 32-byte table of eight 32-bit section sizes, so its total size is 32 bytes plus their sum. The types used here, and the way output tensors are laid out, are described in [`iproai_def.h`](#iproai_def-h).

Typical sequence:

1. Ungate the multimedia clock domain that contains the NPU (`GLB_PER_Clock_UnGate(GLB_AHB_CLOCK_MM)`).
1. For a model that reads its input from an external address (`ext_input`), point the global `imgBuffer` ([`hal_npu.h`](#hal_npu-h)) at a buffer whose data starts at `imgBuffer + 4`.
1. Call [`iproai_create()`](#iproai_create), then [`iproai_load_model_from_buffer()`](#iproai_load_model_from_buffer) or [`iproai_load_model_from_file()`](#iproai_load_model_from_file).
1. Optionally call [`iproai_setResultCB()`](#iproai_setResultCB) and [`iproai_setSourceResolution()`](#iproai_setSourceResolution) for the built-in post-processing.
1. For each input: write it into the working buffer ([`iproai_getInputBuffer()`](#iproai_getInputBuffer)) or set its address with [`NPU_Img_Ext_Addr_Cfg()`](#NPU_Img_Ext_Addr_Cfg), call [`iproai_startCompute()`](#iproai_startCompute), then read the output tensors.
1. Call [`iproai_free()`](#iproai_free).

The engine allocates its memory from the FreeRTOS heap. Its functions are not thread-safe: make all calls for a model from one task and run one inference at a time. None of them may be called from an interrupt handler. Apart from [`iproai_load_model_from_file()`](#iproai_load_model_from_file) and [`iproai_startCompute()`](#iproai_startCompute), the functions do not check their handle or pointer arguments for NULL.

### iproai_create { #iproai_create }

```c
iproai_model_hdl_t iproai_create(void);
```

Create a model instance.

Allocates an empty model and its network description from the FreeRTOS heap. Each call also applies the NPU clock divider and bus settings; the first call creates the semaphores of the NPU driver. Load a model into the instance with [`iproai_load_model_from_buffer()`](#iproai_load_model_from_buffer) or [`iproai_load_model_from_file()`](#iproai_load_model_from_file).

**回傳值**：Handle to the new instance, or NULL when the heap is exhausted.

### iproai_getNetInfo { #iproai_getNetInfo }

```c
struct iproai_net_info_t * iproai_getNetInfo(iproai_model_hdl_t hdl);
```

Get the network description of a model.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle from [`iproai_create()`](#iproai_create). |

**回傳值**：Network description. Its fields are zero until a model is loaded; the pointer stays valid until [`iproai_free()`](#iproai_free).

### iproai_load_model_from_file { #iproai_load_model_from_file }

```c
IPROAI_Status_e iproai_load_model_from_file(iproai_model_hdl_t hdl, const char *name);
```

Load a model from a file on a FatFS volume.

Reads the whole file into a heap buffer, checks that its section table matches the file size and loads it with [`iproai_load_model_from_buffer()`](#iproai_load_model_from_buffer). The staging buffer is released before the function returns, so the peak heap use is the file size plus the memory of the loaded model.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle from [`iproai_create()`](#iproai_create), with no model loaded yet. |
| `name` | FatFS path of the model file, for example `"sd:/model.inm"`. The volume must already be mounted with `f_mount()`. |

| 回傳碼 | 說明 |
|---|---|
| `IPROAI_STATUS_NO_ERROR` | Model loaded. |
| `IPROAI_STATUS_INVALID_INPUT` | `hdl` or `name` is NULL, the file cannot be opened, or the library was built without `CONFIG_AI_MODEL_FROM_FILE`. |
| `IPROAI_STATUS_BAD_DATA` | The file is shorter than 32 bytes, a read failed, or the section table does not match the file size. |
| `IPROAI_STATUS_OUT_OF_MEMORY` | The staging buffer or a model section could not be allocated. |

!!! note "注意"
    The same warnings as for [`iproai_load_model_from_buffer()`](#iproai_load_model_from_buffer) apply.

### iproai_load_model_from_buffer { #iproai_load_model_from_buffer }

```c
IPROAI_Status_e iproai_load_model_from_buffer(iproai_model_hdl_t hdl, const uint8_t *buffer);
```

Load a model from memory.

Copies each section of the model blob into its own heap buffer, decodes the layer table, allocates the working buffer and programs the NPU with the buffers of this model. The blob is only read during the call, so it can sit in memory-mapped (XIP) flash and may be released afterwards. Loading prints the buffer sizes, the layer table and an NPU register dump on the console.

For a model with `ext_input` set, the load programs the external input address of the NPU from the global `imgBuffer` ([`hal_npu.h`](#hal_npu-h)) plus 4 and cleans the data cache over the input frame there, so `imgBuffer` must point at a valid buffer before this call.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle from [`iproai_create()`](#iproai_create), with no model loaded yet. To change models, free the handle and create a new one. |
| `buffer` | Model blob produced by the model converter, 4-byte aligned. |

| 回傳碼 | 說明 |
|---|---|
| `IPROAI_STATUS_NO_ERROR` | Sections copied (layer-table errors are not reported here; see the first warning). |
| `IPROAI_STATUS_OUT_OF_MEMORY` | A section could not be allocated. The sections already copied stay attached to `hdl`; [`iproai_free()`](#iproai_free) releases them. |

!!! warning "警告"
    Errors found while decoding the layer table are printed on the console but not returned. In particular, a failed allocation of the working buffer leaves [`iproai_getInputBuffer()`](#iproai_getInputBuffer) returning NULL.

!!! warning "警告"
    The NPU is programmed when a model is loaded, and [`iproai_startCompute()`](#iproai_startCompute) does not program it again. With several models loaded, NPU layers use the buffers of the model loaded last.

### iproai_getInputBuffer { #iproai_getInputBuffer }

```c
uint8_t * iproai_getInputBuffer(iproai_model_hdl_t hdl);
```

Get the working buffer of a model.

The working buffer holds every tensor of the model: the input, the intermediate results and the outputs, each starting at a patch boundary (see [`iproai_def.h`](#iproai_def-h)). For a model without `ext_input`, write the input tensor at the input patch of the layer that reads the image (the first layer, or the layer with `img_in` set): byte offset `in_layer1_mem * patch_size`. After an inference, the output of a layer starts at byte offset `out_layer_mem * patch_size`.

The NPU accesses this memory directly. Clean the data cache over the input you wrote (`L1C_DCACHE_CLEAN_INVALID_RANGE()`) before starting the inference, and invalidate it over an output before reading the output.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |

**回傳值**：Start of the working buffer, or NULL when no model is loaded or the buffer could not be allocated.

### iproai_getOutputBuffer { #iproai_getOutputBuffer }

```c
uint8_t * iproai_getOutputBuffer(iproai_model_hdl_t hdl, uint32_t *size);
```

Get the output tensor of the last layer of a model.

Returns the address of the output of `layers[layer_cnt - 1]` in the working buffer. For a model with several outputs, or when the last layer is not the output you need, use [`iproai_getInputBuffer()`](#iproai_getInputBuffer) with `iproai_net_info_t::output_layer` instead.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle with a model loaded. |
| `size` | Receives `patch_size`, the size of one working-buffer patch in bytes. This is not the size of the tensor: compute that from `out_h`, `out_w` and `out_c` of the layer, with the channel count rounded up to a multiple of 4 when the layer runs on the NPU. |

**回傳值**：Start of the output tensor.

### iproai_free { #iproai_free }

```c
IPROAI_Status_e iproai_free(iproai_model_hdl_t hdl);
```

Release a model instance and everything it owns.

Frees the layer tables, the working buffer, the copied model sections, the network description and the instance itself. The NPU driver stays initialized for later models. The handle and every pointer obtained from it are invalid afterwards. The function can be called after a failed load.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle from [`iproai_create()`](#iproai_create); must not be NULL. |

**回傳值**：IPROAI_STATUS_NO_ERROR.

### iproai_setResultCB { #iproai_setResultCB }

```c
IPROAI_Status_e iproai_setResultCB(iproai_model_hdl_t hdl, iproai_inference_cb cb);
```

Set the callback that receives the results of the built-in post-processing.

The callback is called from [`iproai_startCompute()`](#iproai_startCompute); see [`iproai_inference_cb`](#iproai_def-h-typedefs). It can be set before or after the model is loaded.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |
| `cb` | Callback, or NULL to remove it. |

**回傳值**：IPROAI_STATUS_NO_ERROR.

!!! warning "警告"
    The built-in post-processing and `SSD` layers call the callback without checking it for NULL. Set a callback before running such a model.

### iproai_setCustom_Postproc_CB { #iproai_setCustom_Postproc_CB }

```c
IPROAI_Status_e iproai_setCustom_Postproc_CB(iproai_model_hdl_t hdl, iproai_custom_postproc_cb cb);
```

Register a custom post-processing callback.

Stores `cb` and sets `custom_postprocess` in the network description, which disables the built-in `FR_EVALUATION` post-processing. A model load clears the flag, so call this function after the load.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |
| `cb` | Callback to store. |

**回傳值**：IPROAI_STATUS_NO_ERROR.

!!! note "注意"
    The current library does not call `cb`.

### iproai_startCompute { #iproai_startCompute }

```c
IPROAI_Status_e iproai_startCompute(iproai_model_hdl_t hdl);
```

Run one inference of the loaded model.

Runs all layers, alternating between CPU stages and NPU stages, then runs the built-in post-processing for the application type of the model if the library includes it (see [`APPLICATION_TYPE`](#APPLICATION_TYPE)). The calling task blocks while the NPU runs; other tasks keep running. The time spent in CPU and NPU stages is stored in `IPROAI_Model_t::inst` (`process_time`, in RTOS ticks).

Prepare the input first, as described for [`iproai_getInputBuffer()`](#iproai_getInputBuffer) or with [`NPU_Img_Ext_Addr_Cfg()`](#NPU_Img_Ext_Addr_Cfg). Patches of the working buffer are reused between layers, so the input is not guaranteed to survive a run: provide it again before every inference. The outputs stay in the working buffer until the next inference.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle with a model loaded. |

| 回傳碼 | 說明 |
|---|---|
| `IPROAI_STATUS_NO_ERROR` | All layers ran. |
| `IPROAI_STATUS_UNAVAILABLE_DEVICE` | `hdl` is NULL. |

!!! note "注意"
    Call it from a task with enough stack for the CPU layers of the model; the SDK examples use 4096 to 8192 words.

!!! warning "警告"
    With several models loaded, NPU layers use the buffers of the model loaded last (see [`iproai_load_model_from_buffer()`](#iproai_load_model_from_buffer)).

### iproai_getInputResolution { #iproai_getInputResolution }

```c
IPROAI_Status_e iproai_getInputResolution(iproai_model_hdl_t hdl, uint32_t *width, uint32_t *height);
```

Get the input resolution of the loaded model.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |
| `width` | Receives the input width (`iproai_net_info_t::w`); 0 before a load. |
| `height` | Receives the input height (`iproai_net_info_t::h`); 0 before a load. |

**回傳值**：IPROAI_STATUS_NO_ERROR.

### iproai_setSourceResolution { #iproai_setSourceResolution }

```c
IPROAI_Status_e iproai_setSourceResolution(iproai_model_hdl_t hdl, uint32_t width, uint32_t height);
```

Set the resolution of the source image that the input was taken from.

The built-in post-processing of detection models (`OBJECT_DETECTION`, `FACE_LANDMARK`, the RetinaNet types and `SSD` layers) scales box and landmark coordinates to this resolution. Both values are 0 after [`iproai_create()`](#iproai_create), which yields zero coordinates.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |
| `width` | Source width, in pixels. |
| `height` | Source height, in pixels. |

**回傳值**：IPROAI_STATUS_NO_ERROR.

### check_IPROAI_NPU_RUN { #check_IPROAI_NPU_RUN }

```c
bool check_IPROAI_NPU_RUN(struct iproai_net_info_t *net, struct cpu_inst_layer_t *l);
```

Check whether the NPU can run a layer.

The engine uses this check at load time to place the layers of a model whose `use_npu_accel` flag is set. It looks at the layer type and at its kernel size, stride, dilation, upsampling factor, padding and number of inputs.

| 參數 | 說明 |
|---|---|
| `net` | Network the layer belongs to (not used by the current check). |
| `l` | Layer to check. |

**回傳值**：true when the NPU can run the layer, false when the layer must run on the CPU.

## iproai_inst_npu.h { #iproai_inst_npu-h }

`#include "iproai_inst_npu.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/iproai_inst_npu.h)）

Low-level NPU control used by the AI runtime: set-up, dispatch and teardown.

Most applications never call these functions: [`iproai_create()`](#iproai_create), [`iproai_load_model_from_buffer()`](#iproai_load_model_from_buffer), [`iproai_startCompute()`](#iproai_startCompute) and [`iproai_free()`](#iproai_free) ([`iproai_core.h`](#iproai_core-h)) use them internally. They matter when several models share the NPU, or when an application tears the NPU down completely.

### iproai_npu_inference { #iproai_npu_inference }

```c
IPROAI_ProcStatus_e iproai_npu_inference();
```

Run the NPU program that is currently configured and wait for it.

Enables the NPU clock, starts the NPU and blocks the calling task on a semaphore (no timeout) until the completion interrupt arrives, then gates the clock again. The CPU is free for other tasks while waiting.

Requires the interrupt set-up done by [`iproai_npu_initCfg()`](#iproai_npu_initCfg). Must be called from a task, not from an interrupt handler.

**回傳值**：[`IPROAI_PROCESS_CPU`](#IPROAI_ProcStatus_e), the next state of the runtime's execution loop.

### iproai_npu_stop { #iproai_npu_stop }

```c
IPROAI_Status_e iproai_npu_stop(void);
```

Stop the NPU.

Called by the runtime at the end of every inference.

**回傳值**：[`IPROAI_STATUS_NO_ERROR`](#IPROAI_Status_e).

### iproai_npu_initCfg { #iproai_npu_initCfg }

```c
IPROAI_Status_e iproai_npu_initCfg(iproai_model_hdl_t hdl);
```

Program the NPU for a loaded model and install its interrupt handler.

Writes the model's NPU instruction, weight, bias and multiplier/shift buffers, its data buffer and patch size and its network parameters into the NPU registers, then registers and enables the NPU completion interrupt. Calls [`iproai_npu_init()`](#iproai_npu_init) if the completion semaphore does not exist yet. Prints a register dump and progress messages to the console.

Called by the model loader. Call it again before running a model when another model has used the NPU since (see the note in the file description).

| 參數 | 說明 |
|---|---|
| `hdl` | Handle of a loaded model. |

**回傳值**：[`IPROAI_STATUS_NO_ERROR`](#IPROAI_Status_e).

### iproai_npu_release { #iproai_npu_release }

```c
IPROAI_Status_e iproai_npu_release(iproai_model_hdl_t hdl);
```

Free the NPU layer table of a model.

Called by [`iproai_free()`](#iproai_free). The pointer in the model is not cleared, so do not call it in addition to [`iproai_free()`](#iproai_free) for the same model.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |

**回傳值**：[`IPROAI_STATUS_NO_ERROR`](#IPROAI_Status_e).

### iproai_npu_exec_lock_required { #iproai_npu_exec_lock_required }

```c
void iproai_npu_exec_lock_required(void);
```

Take the NPU execution mutex, waiting as long as necessary.

The mutex only serialises code that takes it explicitly: [`iproai_startCompute()`](#iproai_startCompute) does not take it. Requires [`iproai_npu_init()`](#iproai_npu_init) (called by [`iproai_create()`](#iproai_create)). Must be called from a task.

### iproai_npu_exec_lock_release { #iproai_npu_exec_lock_release }

```c
void iproai_npu_exec_lock_release(bool in_isr);
```

Release the NPU execution mutex taken with [`iproai_npu_exec_lock_required()`](#iproai_npu_exec_lock_required).

| 參數 | 說明 |
|---|---|
| `in_isr` | Selects the interrupt-handler variant of the give when true. FreeRTOS does not allow a mutex to be given from an interrupt handler, so pass false and call it from the task that took the mutex. |

### iproai_npu_init { #iproai_npu_init }

```c
void iproai_npu_init(void);
```

Initialise the NPU support of the runtime.

On the first call (or the first after [`iproai_npu_destroy()`](#iproai_npu_destroy)) creates the completion semaphore and the execution mutex and gates the NPU clock off. Every call then sets the NPU clock divider and bus configuration. [`iproai_create()`](#iproai_create) calls it, so applications normally do not need to.

### iproai_npu_destroy { #iproai_npu_destroy }

```c
void iproai_npu_destroy(void);
```

Delete the semaphores created by [`iproai_npu_init()`](#iproai_npu_init).

Call only when no model will run any more, after [`iproai_free()`](#iproai_free) of every model; call [`iproai_npu_init()`](#iproai_npu_init) (or [`iproai_create()`](#iproai_create)) before using the NPU again.

## iproai_inst_util.h { #iproai_inst_util-h }

`#include "iproai_inst_util.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/iproai_inst_util.h)）

AI runtime utilities: cache-line aligned allocation, fixed-point conversion and tensor addressing in the model data buffer.

Included by [`iproai_core.h`](#iproai_core-h). Buffers that the NPU or a DMA engine reads or writes should come from [`IPROAI_MALLOC`](#iproai_inst_util-h-macros), which aligns them to a cache line so that cache maintenance never touches neighbouring heap objects.

Tensors of a loaded model live in its data buffer ([`iproai_getInputBuffer()`](#iproai_getInputBuffer)), which is divided into memory slots of `net->patch_size` bytes; a layer's output starts at slot `layer.out_layer_mem`. [`MEM_PTR()`](#MEM_PTR) and [`MEM_PTR_ADDR()`](#MEM_PTR_ADDR) compute such addresses.

### iproai_mem_alloc { #iproai_mem_alloc }

```c
void * iproai_mem_alloc(size_t size, const char *func, const int line);
```

Allocate a cache-line aligned buffer from the FreeRTOS heap.

Use [`IPROAI_MALLOC`](#iproai_inst_util-h-macros) rather than calling this directly. The returned pointer is aligned to the 32-byte cache line; the raw heap pointer is stored just below it for [`iproai_mem_free()`](#iproai_mem_free).

| 參數 | 說明 |
|---|---|
| `size` | Size in bytes. |
| `func` | Name of the calling function, used in the error message. |
| `line` | Source line of the call, used in the error message. |

**回傳值**：Aligned pointer, or NULL if `size` is 0 or the heap is exhausted (a message is printed in both cases).

### iproai_mem_free { #iproai_mem_free }

```c
void iproai_mem_free(void *addr, const char *func, const int line);
```

Free a buffer allocated with [`iproai_mem_alloc()`](#iproai_mem_alloc).

Use [`IPROAI_FREE`](#iproai_inst_util-h-macros) rather than calling this directly.

| 參數 | 說明 |
|---|---|
| `addr` | Pointer returned by [`iproai_mem_alloc()`](#iproai_mem_alloc), or NULL (ignored). |
| `func` | Name of the calling function, used in diagnostics. |
| `line` | Source line of the call, used in diagnostics. |

### unsigned_to_signed { #unsigned_to_signed }

```c
int unsigned_to_signed(int in, int bit);
```

Sign-extend a two's-complement bit field.

Uses a small temporary heap allocation.

| 參數 | 說明 |
|---|---|
| `in` | Field value in the low `bit` bits; higher bits must be 0. |
| `bit` | Width of the field in bits, 1 to 31. |

**回傳值**：The field value interpreted as a signed number of `bit` bits.

### fixed_to_float { #fixed_to_float }

```c
float fixed_to_float(fixed_point_t input, int FIXED_POINT_FRACTIONAL_BITS);
```

Convert an 8-bit fixed-point value to float.

| 參數 | 說明 |
|---|---|
| `input` | Fixed-point value. |
| `FIXED_POINT_FRACTIONAL_BITS` | Number of fractional bits, 0 or more. |

**回傳值**：`input / 2^FIXED_POINT_FRACTIONAL_BITS`.

### fixed32_to_fixed8 { #fixed32_to_fixed8 }

```c
fixed_point_t fixed32_to_fixed8(int32_t input, int FIXED_POINT_FRACTIONAL_BITS);
```

Requantise a 32-bit fixed-point value to 8 bits.

Shifts right by `FIXED_POINT_FRACTIONAL_BITS` with rounding to nearest (ties away from zero), or left by its magnitude when it is 0 or negative, and saturates to [-128, 127].

| 參數 | 說明 |
|---|---|
| `input` | 32-bit value. |
| `FIXED_POINT_FRACTIONAL_BITS` | Right-shift amount (negative: left shift). |

**回傳值**：Rounded and saturated 8-bit value.

### fixed8_to_fixed8 { #fixed8_to_fixed8 }

```c
fixed_point_t fixed8_to_fixed8(fixed_point_t input, int FIXED_POINT_FRACTIONAL_BITS);
```

Rescale an 8-bit fixed-point value by a power of two.

Same rounding and saturation as [`fixed32_to_fixed8()`](#fixed32_to_fixed8), for an 8-bit input.

| 參數 | 說明 |
|---|---|
| `input` | 8-bit value. |
| `FIXED_POINT_FRACTIONAL_BITS` | Right-shift amount (negative: left shift). |

**回傳值**：Rounded and saturated 8-bit value.

### fixed32_to_fixed32 { #fixed32_to_fixed32 }

```c
int32_t fixed32_to_fixed32(int32_t input, int FIXED_POINT_FRACTIONAL_BITS);
```

Rescale a 32-bit fixed-point value by a power of two.

Same rounding as [`fixed32_to_fixed8()`](#fixed32_to_fixed8); the result saturates to the int32_t range.

| 參數 | 說明 |
|---|---|
| `input` | 32-bit value. |
| `FIXED_POINT_FRACTIONAL_BITS` | Right-shift amount (negative: left shift). |

**回傳值**：Rounded and saturated 32-bit value.

### float_to_fixed { #float_to_fixed }

```c
fixed_point_t float_to_fixed(float input, int FIXED_POINT_FRACTIONAL_BITS);
```

Convert a float to 8-bit fixed point.

Saturates `input` to the range representable with `FIXED_POINT_FRACTIONAL_BITS` fractional bits, then rounds `input * 2^FIXED_POINT_FRACTIONAL_BITS` to the nearest integer.

| 參數 | 說明 |
|---|---|
| `input` | Value to convert. |
| `FIXED_POINT_FRACTIONAL_BITS` | Number of fractional bits, 0 to 7. |

**回傳值**：8-bit fixed-point value.

### fixed8_to_fixed32 { #fixed8_to_fixed32 }

```c
int32_t fixed8_to_fixed32(fixed_point_t input, int FIXED_POINT_FRACTIONAL_BITS);
```

Shift an 8-bit value and widen it to 32 bits.

Arithmetic right shift by `FIXED_POINT_FRACTIONAL_BITS` (no rounding), or left shift by its magnitude when it is 0 or negative.

| 參數 | 說明 |
|---|---|
| `input` | 8-bit value. |
| `FIXED_POINT_FRACTIONAL_BITS` | Right-shift amount (negative: left shift). |

**回傳值**：Shifted value.

### MEM_PTR { #MEM_PTR }

```c
int8_t * MEM_PTR(int mux, fixed_point_t *DATA_buf, int PATCH_SIZE);
```

Get the start of a memory slot in a model data buffer.

| 參數 | 說明 |
|---|---|
| `mux` | Slot index, for example a layer's `out_layer_mem`. |
| `DATA_buf` | Model data buffer, from [`iproai_getInputBuffer()`](#iproai_getInputBuffer). |
| `PATCH_SIZE` | Slot size in bytes, `net->patch_size`. |

**回傳值**：`DATA_buf + mux * PATCH_SIZE`.

### MEM_PTR_ADDR { #MEM_PTR_ADDR }

```c
fixed_point_t * MEM_PTR_ADDR(int mux, int addr, fixed_point_t *DATA_buf, int patch_size);
```

Get the address of a byte inside a memory slot of a model data buffer.

| 參數 | 說明 |
|---|---|
| `mux` | Slot index, for example a layer's `out_layer_mem`. |
| `addr` | Byte offset inside the slot. |
| `DATA_buf` | Model data buffer, from [`iproai_getInputBuffer()`](#iproai_getInputBuffer). |
| `patch_size` | Slot size in bytes, `net->patch_size`. |

**回傳值**：`DATA_buf + mux * patch_size + addr`.

### 巨集 { #iproai_inst_util-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_MALLOC(sz)` | `iproai_mem_alloc(sz, __func__, __LINE__)` | Allocate a cache-line aligned buffer from the FreeRTOS heap. Wrapper around [`iproai_mem_alloc()`](#iproai_mem_alloc) that records the calling function and line for its error message. Define it before including this header to substitute another allocator. |
| `IPROAI_FREE(addr)` | `iproai_mem_free(addr, __func__, __LIN...` | Free a buffer allocated with [`IPROAI_MALLOC`](#iproai_inst_util-h-macros). Wrapper around [`iproai_mem_free()`](#iproai_mem_free). Define it before including this header to substitute another allocator. |
| `BALI_CHN_ALIGN(sz)` | `(((sz + 3) >> 2) << 2)` | Round a channel count up to a multiple of 4. NPU tensors store each pixel with its channel count padded this way, so a pixel of a 3-channel tensor occupies 4 bytes. |

## iproai_inst_postprocess.h { #iproai_inst_postprocess-h }

`#include "iproai_inst_postprocess.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/iproai_inst_postprocess.h)）

Built-in (legacy) post-processors run by the AI runtime after an inference.

When a model's application type selects one of these post-processors, [`iproai_startCompute()`](#iproai_startCompute) calls it after the inference and the post-processor reports its result through the callback registered with [`iproai_setResultCB()`](#iproai_setResultCB), as a `struct iproai_result_t`:

Application type 
Post-processor 
Result fields 


CLASSIFICATION 
image_classification() 
r.classification 


KEYWORD_SPOTTING 
KWS_classification() 
r.classification 


FACE_RECONGNITION 
face_recongnition() 
r.fr 


OBJECT_DETECTION 
yolo_obj_det() 
r.objdet 


FACE_LANDMARK 
yolo_face_landmark() 
r.landmark 


RETINA_FACE 
retina_face() 
r.objdet, r.landmark 


RETINA_PERSON 
retina_person() 
r.objdet 


RETINA 
retina() 
r.objdet

The class names and the reference face features they use are set with [`load_postprocess_classification()`](#load_postprocess_classification) and [`load_postprocess_face_recongnition()`](#load_postprocess_face_recongnition); the image size used to scale boxes is the one set with [`iproai_setSourceResolution()`](#iproai_setSourceResolution).

These functions are only built when the matching option is enabled: `CONFIG_AI_LEGACY_YOLO` for [`yolo_obj_det()`](#yolo_obj_det) and [`yolo_face_landmark()`](#yolo_face_landmark), `CONFIG_AI_LEGACY_POSTPROCESS` for all the others. New applications decode model outputs themselves, for example with [`yolov8_detect.h`](#yolov8_detect-h).

Unless stated otherwise, `net` is the network information of the model ([`iproai_getNetInfo()`](#iproai_getNetInfo)), `DATA_buf` its data buffer ([`iproai_getInputBuffer()`](#iproai_getInputBuffer)) and `result_cb` the callback that receives the results.

### image_classification { #image_classification }

```c
void image_classification(struct iproai_net_info_t *net, const char **imgnet_names, fixed_point_t *DATA_buf, iproai_inference_cb result_cb, int num);
```

Report the most probable class of a classifier with a background class.

Takes the arg-max over the first `num` bytes (read as unsigned) of the last layer's output. Index 0 is treated as the background class, so the class reported is the arg-max minus 1; prints its name and calls `result_cb` once with `r.classification.best_class` set to it.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `imgnet_names` | Class names, indexed by the reported class. |
| `DATA_buf` | Model data buffer. |
| `result_cb` | Result callback. |
| `num` | Number of model outputs, background included. |

!!! warning "警告"
    If the background output wins, the name lookup uses index -1.

### KWS_classification { #KWS_classification }

```c
void KWS_classification(struct iproai_net_info_t *net, const char **imgnet_names, fixed_point_t *DATA_buf, iproai_inference_cb result_cb, int num);
```

Report the most probable keyword of a keyword-spotting model.

Takes the arg-max over the first `num` bytes (read as unsigned) of the last layer's output, prints its name and calls `result_cb` once with `r.classification.best_class` set to the arg-max index.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `imgnet_names` | Keyword names, indexed by class. |
| `DATA_buf` | Model data buffer. |
| `result_cb` | Result callback. |
| `num` | Number of model outputs. |

### get_output_data { #get_output_data }

```c
void get_output_data(struct iproai_net_info_t *net, fixed_point_t *DATA_buf, int layer, int size);
```

Print the first bytes of a layer's output to the console (diagnostic).

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `DATA_buf` | Model data buffer. |
| `layer` | Index of the layer in `net->layers[]`. |
| `size` | Number of bytes to print, in hexadecimal. |

### face_recongnition { #face_recongnition }

```c
void face_recongnition(struct iproai_net_info_t *net, const char **names, int names_len, const float **feature_list, int feature_len, fixed_point_t *DATA_buf, iproai_inference_cb result_cb);
```

Identify a face against a set of reference feature vectors.

Converts the first 128 values of the last layer's output from fixed point to float and computes their cosine similarity with each reference vector. The best reference with a similarity above 0.63 wins. Prints every similarity and the result, then calls `result_cb` once with `r.fr.best_class` set to the winning index, or 255 if no reference matches.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `names` | Name of each reference, `names_len` entries. |
| `names_len` | Number of references. |
| `feature_list` | Reference vectors. Despite its type this must point to one contiguous float array (cast to `const float **`): reference i starts at float offset `i * feature_len` and its first 128 floats are used. |
| `feature_len` | Distance between two references, in floats (at least 128). |
| `DATA_buf` | Model data buffer. |
| `result_cb` | Result callback. |

### yolo_obj_det { #yolo_obj_det }

```c
void yolo_obj_det(struct iproai_net_info_t *net, const char **names, int image_width, int image_height, iproai_inference_cb result_cb);
```

Decode a legacy YOLO (v2/v3 region layer) object detector.

Uses a confidence threshold of 0.24 and an NMS IoU threshold of 0.45, prints each detection and calls `result_cb` once per detection with `r.objdet.rect` (top-left corner and size in pixels of the `image_width` x `image_height` image), `r.objdet.best_class` and `r.objdet.prob` (percent). Nothing is reported when no box is found.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `names` | Class names. |
| `image_width` | Width of the image boxes are scaled to, pixels. |
| `image_height` | Height of the image boxes are scaled to, pixels. |
| `result_cb` | Result callback. |

### yolo_face_landmark { #yolo_face_landmark }

```c
void yolo_face_landmark(struct iproai_net_info_t *net, const char **names, int image_width, int image_height, iproai_inference_cb result_cb);
```

Decode a legacy YOLO face detector with five facial landmarks.

Uses the same thresholds as [`yolo_obj_det()`](#yolo_obj_det). Prints every face and calls `result_cb` once, after all faces are processed, with `r.landmark`: `lx1` to `lx5` hold the left eye, right eye, nose, left and right mouth corner of the most probable face, in pixels; `rect`, `best_class` and `prob` (percent) are those of the right-most face. Both refer to the same face when exactly one face is detected.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `names` | Class names. |
| `image_width` | Width of the image coordinates are scaled to, pixels. |
| `image_height` | Height of the image coordinates are scaled to, pixels. |
| `result_cb` | Result callback. |

!!! warning "警告"
    If candidate boxes exist but none passes the threshold, the callback still runs with an unset result.

### load_postprocess_classification { #load_postprocess_classification }

```c
void load_postprocess_classification(iproai_model_hdl_t hdl, const char **classes_name, int classes_num);
```

Set the class-name table used by the built-in post-processors.

The array is not copied and must stay valid while the model is used.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |
| `classes_name` | Class names, indexed by class. |
| `classes_num` | Number of entries in `classes_name` (the number of outputs for [`image_classification()`](#image_classification) and [`KWS_classification()`](#KWS_classification), the class count for [`retina()`](#retina)). |

### load_postprocess_face_recongnition { #load_postprocess_face_recongnition }

```c
void load_postprocess_face_recongnition(iproai_model_hdl_t hdl, const char **names, int names_num, const float **features_list, int features_num);
```

Set the reference faces used by [`face_recongnition()`](#face_recongnition).

The arrays are not copied and must stay valid while the model is used.

| 參數 | 說明 |
|---|---|
| `hdl` | Model handle. |
| `names` | Name of each reference face. |
| `names_num` | Number of reference faces. |
| `features_list` | Reference feature vectors, in the contiguous layout described for [`face_recongnition()`](#face_recongnition). |
| `features_num` | Distance between two reference vectors, in floats. |

### retina_face { #retina_face }

```c
void retina_face(struct iproai_net_info_t *net, const char **imgnet_names, fixed_point_t *DATA_buf, int image_width, int image_height, iproai_inference_cb result_cb);
```

Decode a RetinaFace-style face detector.

Expects three outputs, told apart by their channel count: boxes (4), landmarks (10) and two-class scores (2). Boxes are decoded against the prior boxes of the model (`net->prior_bbox`, variances 0.1 and 0.2), then NMS runs with an IoU threshold of 0.4, a score threshold of 0.5 and at most 50 faces. For each face, prints it and calls `result_cb` with `r.objdet.rect` (top-left corner and size in pixels of the `image_width` x `image_height` image), `r.objdet.prob` (percent), `best_class` 0, and the first four landmark points in `r.landmark.lx1` to `lx4`.

Free memory slots of `DATA_buf` are used as scratch space.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `imgnet_names` | Not used. |
| `DATA_buf` | Model data buffer. |
| `image_width` | Width of the image boxes are scaled to, pixels. |
| `image_height` | Height of the image boxes are scaled to, pixels. |
| `result_cb` | Result callback. |

### retina_person { #retina_person }

```c
void retina_person(struct iproai_net_info_t *net, const char **imgnet_names, fixed_point_t *DATA_buf, int image_width, int image_height, iproai_inference_cb result_cb);
```

Decode a RetinaNet-style single-class person detector.

Like [`retina_face()`](#retina_face) without landmarks: expects a box output (4 channels) and a two-class score output (2 channels), and uses a score threshold of 0.7. Calls `result_cb` once per person with `r.objdet` (`best_class` 0).

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `imgnet_names` | Not used. |
| `DATA_buf` | Model data buffer. |
| `image_width` | Width of the image boxes are scaled to, pixels. |
| `image_height` | Height of the image boxes are scaled to, pixels. |
| `result_cb` | Result callback. |

### retina { #retina }

```c
void retina(struct iproai_net_info_t *net, const char **imgnet_names, int class_num, fixed_point_t *DATA_buf, int image_width, int image_height, iproai_inference_cb result_cb);
```

Decode a multi-class RetinaNet-style detector.

Expects a box output (4 channels) and a score output with `class_num` logits per prior box (passed through a sigmoid). For each class, runs NMS with an IoU threshold of 0.2, a score threshold of 0.3 and at most 50 boxes, drops boxes narrower or lower than 50 pixels, prints the rest and calls `result_cb` once per box with `r.objdet.rect` (pixels of the `image_width` x `image_height` image), `best_class` (class index) and `prob` (percent).

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `imgnet_names` | Class names, `class_num` entries. |
| `class_num` | Number of classes. |
| `DATA_buf` | Model data buffer. |
| `image_width` | Width of the image boxes are scaled to, pixels. |
| `image_height` | Height of the image boxes are scaled to, pixels. |
| `result_cb` | Result callback. |

!!! warning "警告"
    `prob` is read from the wrong candidate index and does not reliably belong to the reported box.

### get_segmentation_mask { #get_segmentation_mask }

```c
void get_segmentation_mask(struct iproai_net_info_t *net, fixed_point_t *DATA_buf, int layer, uint32_t out_image_width, uint32_t out_image_height, iproai_inference_cb result_cb);
```

Count the foreground pixels of a segmentation output (diagnostic).

Counts the pixels of the last layer's output whose value exceeds 128 and prints the count. Nothing else is reported.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `DATA_buf` | Model data buffer. |
| `layer` | Not used; the last layer is always read. |
| `out_image_width` | Width of the output mask, pixels. |
| `out_image_height` | Height of the output mask, pixels. |
| `result_cb` | Not called. |

### get_sr_result { #get_sr_result }

```c
void get_sr_result(struct iproai_net_info_t *net, fixed_point_t *DATA_buf, int layer, uint32_t out_image_width, uint32_t out_image_height, iproai_inference_cb result_cb);
```

Placeholder post-processor for super-resolution models.

Reads the 3-channel output image of the last layer, prints its size and reports nothing.

| 參數 | 說明 |
|---|---|
| `net` | Network information. |
| `DATA_buf` | Model data buffer. |
| `layer` | Not used; the last layer is always read. |
| `out_image_width` | Width of the output image, pixels. |
| `out_image_height` | Height of the output image, pixels. |
| `result_cb` | Not called. |

## iproai_riscv_nnfunctions.h { #iproai_riscv_nnfunctions-h }

`#include "iproai_riscv_nnfunctions.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/iproai_riscv_nnfunctions.h)）

CPU convolution kernel (NMSIS-NN style) used by the AI runtime, with its fixed-point types and limits.

The runtime falls back to these kernels for layers that run on the CPU instead of the NPU. The parameter structures (::nmsis_nn_conv_params, ::nmsis_nn_dims, ...) come from riscv_nn_types.h.

Quantisation follows TensorFlow Lite: a real value is `scale * (q - zero_point)`, convolution offsets are the negated zero points, and results are requantised per output channel with a Q31 multiplier and a power-of-two shift.

### iproai_convolve_s8_get_buffer_size { #iproai_convolve_s8_get_buffer_size }

```c
int32_t iproai_convolve_s8_get_buffer_size(const nmsis_nn_dims *input_dims, const nmsis_nn_dims *filter_dims);
```

Get the scratch-buffer size of an int8 convolution.

| 參數 | 說明 |
|---|---|
| `input_dims` | Input tensor dimensions; only `c` (input channels) is used. |
| `filter_dims` | Filter dimensions; only `w` and `h` (kernel width and height) are used. |

**回傳值**：`2 * input_dims->c * filter_dims->w * filter_dims->h * sizeof(int16_t)` bytes when the library is built with the RISC-V DSP extension (`RISCV_MATH_DSP`), otherwise 0. [`riscv_convolve_u8()`](#riscv_convolve_u8) does not use a scratch buffer.

### riscv_convolve_u8 { #riscv_convolve_u8 }

```c
riscv_status riscv_convolve_u8(const nmsis_nn_context *ctx, const nmsis_nn_conv_params *conv_params, const nmsis_nn_per_channel_quant_params *quant_params, const nmsis_nn_dims *input_dims, const uint8_t *input_data, const nmsis_nn_dims *filter_dims, const uint8_t *filter_data, const nmsis_nn_dims *bias_dims, const int32_t *bias_data, const nmsis_nn_dims *output_dims, uint8_t *output_data);
```

2-D convolution of unsigned 8-bit tensors with per-channel requantisation (reference C implementation).

For every batch, output pixel and output channel `oc:`

```text
acc = sum over ky, kx, ic of
        (input[y][x][ic] + input_offset) * (filter[oc][ic][ky][kx] + filter_offset)
acc = acc + bias[oc]                                  (if bias_data != NULL)
out = requantize(acc, multiplier[oc], shift[oc]) + output_offset
out = clamp(out, activation.min, activation.max)
```

with `y = stride.h * oy - padding.h + ky` and `x = stride.w * ox - padding.w + kx`. Taps that fall outside the input are skipped, which is equivalent to padding with the input zero point. `requantize()` follows TensorFlow Lite: a positive `shift` first multiplies `acc` by `2^shift`, the result is then scaled by the Q31 multiplier as `round(acc * multiplier / 2^31)`, and a negative `shift` finally divides by `2^-shift`, rounding half away from zero. The accumulator is 32-bit.

Tensor layouts (all dimensions must fit in 16 bits):

- input: `[input_dims->n][input_dims->h][input_dims->w][input_dims->c]` (NHWC);
- filter: `[output_dims->c][input_dims->c][filter_dims->h][filter_dims->w]`; note that the input channel comes before the kernel rows;
- bias: `output_dims->c` int32 values;
- output: `[input_dims->n][output_dims->h][output_dims->w][output_dims->c]` (NHWC).

Grouped and dilated convolutions are not supported: `conv_params->dilation` is ignored and every output channel uses all input channels.

| 參數 | 說明 |
|---|---|
| `ctx` | Context; must not be NULL, its buffer is not used. |
| `conv_params` | `input_offset` and `filter_offset` are added to every input and filter value (the negated zero points), `output_offset` is added after requantisation (the output zero point); `stride`, `padding` and `activation` (clamp range, within 0 to 255) are used. |
| `quant_params` | Per-output-channel `multiplier` and `shift` arrays, `output_dims->c` entries each. |
| `input_dims` | Input dimensions; `n` is the batch count. |
| `input_data` | Input tensor. |
| `filter_dims` | Filter dimensions; only `h` and `w` (kernel height and width) are used. |
| `filter_data` | Filter tensor. |
| `bias_dims` | Not used. |
| `bias_data` | Bias per output channel, or NULL for none. |
| `output_dims` | Output dimensions; `h`, `w` and `c` are used. |
| `output_data` | Output tensor. |

**回傳值**：Always [`RISCV_MATH_SUCCESS`](#riscv_status); the arguments are not validated.

### riscv_status { #riscv_status }

Error status returned by some functions in the library.

| 名稱 | 值 | 說明 |
|---|---|---|
| `RISCV_MATH_SUCCESS` | `0` | No error. |
| `RISCV_MATH_ARGUMENT_ERROR` | `-1` | One or more arguments are incorrect. |
| `RISCV_MATH_LENGTH_ERROR` | `-2` | Length of data buffer is incorrect. |
| `RISCV_MATH_SIZE_MISMATCH` | `-3` | Size of matrices is not compatible with the operation. |
| `RISCV_MATH_NANINF` | `-4` | Not-a-number (NaN) or infinity is generated. |
| `RISCV_MATH_SINGULAR` | `-5` | Input matrix is singular and cannot be inverted. |
| `RISCV_MATH_TEST_FAILURE` | `-6` | Test Failed. |
| `RISCV_MATH_DECOMPOSITION_FAILURE` | `-7` | Decomposition Failed. |

### riscv_nnword { #riscv_nnword }

One 32-bit word viewed as one q31, two q15 or four q7 values, for SIMD-style access.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `word` | `q31_t` | The whole word as one q31 value. |
| `half_words` | `q15_t[2]` | The word as two q15 values. |
| `bytes` | `q7_t[4]` | The word as four q7 values. |

### riscv_nnword_u { #riscv_nnword_u }

One 32-bit word viewed as one, two or four unsigned integers.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `word` | `uint32_t` | The whole word as one unsigned 32-bit value. |
| `half_words` | `uint16_t[2]` | The word as two unsigned 16-bit values. |
| `bytes` | `uint8_t[4]` | The word as four unsigned 8-bit values. |

### riscv_nn_double { #riscv_nn_double }

The two 32-bit halves of a 64-bit value (little-endian order).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `low` | `uint32_t` | Low 32 bits. |
| `high` | `int32_t` | High 32 bits, signed. |

### riscv_nn_long_long { #riscv_nn_long_long }

A 64-bit signed value accessible as a whole or as two 32-bit halves.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `long_long` | `int64_t` | The whole 64-bit value. |
| `word` | `struct riscv_nn_double` | The value as low and high halves. |

### 型別定義 { #iproai_riscv_nnfunctions-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `q7_t` | `typedef int8_t q7_t` | 8-bit fractional data type in 1.7 format. |
| `q15_t` | `typedef int16_t q15_t` | 16-bit fractional data type in 1.15 format. |
| `q31_t` | `typedef int32_t q31_t` | 32-bit fractional data type in 1.31 format. |
| `q63_t` | `typedef int64_t q63_t` | 64-bit fractional data type in 1.63 format. |
| `float32_t` | `typedef float float32_t` | 32-bit floating-point type definition. |
| `float64_t` | `typedef double float64_t` | 64-bit floating-point type definition. |

### 巨集 { #iproai_riscv_nnfunctions-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `F64_MAX` | `((float64_t)DBL_MAX)` | Largest [`float64_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `F32_MAX` | `((float32_t)FLT_MAX)` | Largest [`float32_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `F64_MIN` | `(-DBL_MAX)` | Most negative [`float64_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `F32_MIN` | `(-FLT_MAX)` | Most negative [`float32_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `F64_ABSMAX` | `((float64_t)DBL_MAX)` | Largest [`float64_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `F32_ABSMAX` | `((float32_t)FLT_MAX)` | Largest [`float32_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `F64_ABSMIN` | `((float64_t)0.0)` | Smallest [`float64_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `F32_ABSMIN` | `((float32_t)0.0)` | Smallest [`float32_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `Q31_MAX` | `((q31_t)(0x7FFFFFFFL))` | Largest [`q31_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `Q15_MAX` | `((q15_t)(0x7FFF))` | Largest [`q15_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `Q7_MAX` | `((q7_t)(0x7F))` | Largest [`q7_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `Q31_MIN` | `((q31_t)(0x80000000L))` | Most negative [`q31_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `Q15_MIN` | `((q15_t)(0x8000))` | Most negative [`q15_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `Q7_MIN` | `((q7_t)(0x80))` | Most negative [`q7_t`](#iproai_riscv_nnfunctions-h-typedefs) value. |
| `Q31_ABSMAX` | `((q31_t)(0x7FFFFFFFL))` | Largest [`q31_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `Q15_ABSMAX` | `((q15_t)(0x7FFF))` | Largest [`q15_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `Q7_ABSMAX` | `((q7_t)(0x7F))` | Largest [`q7_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `Q31_ABSMIN` | `((q31_t)0)` | Smallest [`q31_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `Q15_ABSMIN` | `((q15_t)0)` | Smallest [`q15_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `Q7_ABSMIN` | `((q7_t)0)` | Smallest [`q7_t`](#iproai_riscv_nnfunctions-h-typedefs) magnitude. |
| `CMPLX_DIM` | `2` | Number of scalars in one complex value (real and imaginary part). |

## iproai_cycle_profile.h { #iproai_cycle_profile-h }

`#include "iproai_cycle_profile.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/iproai_cycle_profile.h)）

Cycle-accurate NPU-busy versus CPU-busy split of model inference.

Measures, with the 64-bit CPU cycle counter, how much of each inference run by [`iproai_startCompute()`](#iproai_startCompute) the CPU spends waiting for the NPU. The tick-based profiling counters have 1 ms resolution, which is too coarse for layers that take tens of microseconds; these counters resolve single cycles.

The waiting share is the concurrency budget of the system: the runtime blocks on an RTOS semaphore while the NPU runs instead of spinning, so every cycle counted as NPU-busy is available to other tasks (for example a second model running on the CPU).

Two kinds of data are kept:

- accumulated totals since the last [`iproai_cycle_reset()`](#iproai_cycle_reset): [`iproai_cycle_total()`](#iproai_cycle_total), [`iproai_cycle_npu()`](#iproai_cycle_npu), [`iproai_cycle_runs()`](#iproai_cycle_runs), [`iproai_cycle_npu_dispatches()`](#iproai_cycle_npu_dispatches), printed by [`iproai_cycle_report()`](#iproai_cycle_report);
- a per-layer breakdown (spans) of the most recent inference only: [`iproai_cycle_spans()`](#iproai_cycle_spans), [`iproai_cycle_span()`](#iproai_cycle_span), printed by [`iproai_cycle_layer_report()`](#iproai_cycle_layer_report).

All values are CPU clock cycles. Enable the feature with `CONFIG_AI_CYCLE_PROFILE`; when it is disabled every function in this header is replaced by a macro that evaluates to 0, NULL or nothing, so calls can stay in application code at no cost.

### iproai_cycle_spans { #iproai_cycle_spans }

```c
uint16_t iproai_cycle_spans(void);
```

Get the number of spans recorded for the most recent inference.

**回傳值**：Span count, 0 to [`IPROAI_CYCLE_MAX_SPANS`](#iproai_cycle_profile-h-macros).

### iproai_cycle_span { #iproai_cycle_span }

```c
const iproai_cycle_span_t * iproai_cycle_span(uint16_t i);
```

Get one span of the most recent inference.

| 參數 | 說明 |
|---|---|
| `i` | Span index, 0 to `iproai_cycle_spans() - 1`, in execution order. |

**回傳值**：Pointer to the span, valid until the next inference starts, or NULL if `i` is out of range.

### iproai_cycle_spans_truncated { #iproai_cycle_spans_truncated }

```c
int iproai_cycle_spans_truncated(void);
```

Check whether spans of the most recent inference were dropped.

**回傳值**：Non-zero if the inference produced more than [`IPROAI_CYCLE_MAX_SPANS`](#iproai_cycle_profile-h-macros) spans, 0 otherwise.

### iproai_cycle_layer_report { #iproai_cycle_layer_report }

```c
void iproai_cycle_layer_report(void);
```

Print the span breakdown of the most recent inference.

Prints one `AILAYER` line per span (layer range, NPU flag, cycles and the share of the total in permille) and ends with an `AILAYEREND` line, which makes the output easy to parse on a host.

### iproai_cycle_npu { #iproai_cycle_npu }

```c
uint64_t iproai_cycle_npu(void);
```

Get the cycles spent waiting for the NPU since the last reset.

**回傳值**：Accumulated NPU-busy cycles over all NPU dispatches.

### iproai_cycle_total { #iproai_cycle_total }

```c
uint64_t iproai_cycle_total(void);
```

Get the cycles spent in whole inferences since the last reset.

**回傳值**：Accumulated duration of all [`iproai_startCompute()`](#iproai_startCompute) calls, in cycles.

### iproai_cycle_runs { #iproai_cycle_runs }

```c
uint32_t iproai_cycle_runs(void);
```

Get the number of completed inferences since the last reset.

**回傳值**：Inference count.

### iproai_cycle_npu_dispatches { #iproai_cycle_npu_dispatches }

```c
uint32_t iproai_cycle_npu_dispatches(void);
```

Get the number of NPU dispatches since the last reset.

Each dispatch runs one contiguous group of NPU layers.

**回傳值**：Dispatch count.

### iproai_cycle_reset { #iproai_cycle_reset }

```c
void iproai_cycle_reset(void);
```

Clear the accumulated totals.

Resets the values returned by [`iproai_cycle_npu()`](#iproai_cycle_npu), [`iproai_cycle_total()`](#iproai_cycle_total), [`iproai_cycle_runs()`](#iproai_cycle_runs) and [`iproai_cycle_npu_dispatches()`](#iproai_cycle_npu_dispatches). The span breakdown is not affected; it is replaced at the start of every inference.

### iproai_cycle_report { #iproai_cycle_report }

```c
void iproai_cycle_report(void);
```

Print the accumulated NPU/CPU split to the console.

Prints the number of inferences and NPU dispatches, the total and per-inference cycles, the NPU-busy and CPU-busy cycles with their percentages, and the share of the core a co-running task could use. Prints a short notice instead if no inference was recorded.

### iproai_cycle_span_t { #iproai_cycle_span_t }

One timed stretch of an inference.

A layer running on the CPU or DSP is timed on its own, so `first` equals `last`. NPU work is different: one NPU dispatch executes a whole contiguous run of NPU layers without stopping in between, so the hardware offers no per-layer boundary to measure. Such a span covers layers `first` to `last` and reports their combined time; it is not split between them.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `first` | `uint16_t` | Index of the first layer covered. |
| `last` | `uint16_t` | Index of the last layer covered (`first` for CPU layers). |
| `cycles` | `uint32_t` | Duration in CPU cycles; saturates at UINT32_MAX, never wraps. |
| `on_npu` | `uint8_t` | 1 for an NPU dispatch, 0 for a CPU or DSP layer. |

### 巨集 { #iproai_cycle_profile-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `IPROAI_CYCLE_MAX_SPANS` | `256` | Maximum number of spans recorded for one inference; further spans are dropped and [`iproai_cycle_spans_truncated()`](#iproai_cycle_spans_truncated) reports it. The storage is a fixed array so that profiling never allocates memory during inference. |

## yolov8_detect.h { #yolov8_detect-h }

`#include "yolov8_detect.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/detect/yolov8_detect.h)）

YOLOv8 detection post-processor for 6-output NPU models, plus the box and NMS helpers shared by the other detectors.

Decodes the output tensors of an anchor-free YOLOv8 model compiled with separate box and class heads per level (3 levels x 2 heads = 6 outputs) into a list of boxes in input-image pixels. The result types and the helpers ([`yolov8_nms()`](#yolov8_nms), [`yolov8_box_iou()`](#yolov8_box_iou), ...) are also used by [`gesture_dfl_detect.h`](#gesture_dfl_detect-h) and [`big_a_sppf_detect.h`](#big_a_sppf_detect-h).

Typical sequence:

1. Load the model, then [`yolov8_init()`](#yolov8_init) (or [`yolov8_person_pet_init()`](#yolov8_person_pet_init)) with the network information from [`iproai_getNetInfo()`](#iproai_getNetInfo).
1. Per frame: [`iproai_startCompute()`](#iproai_startCompute), then [`yolov8_process_6out()`](#yolov8_process_6out) with the model data region from [`iproai_getInputBuffer()`](#iproai_getInputBuffer).
1. [`yolov8_deinit()`](#yolov8_deinit) when done.

Expected model outputs, in `net->output_layer[]` order: box P5, class P5, box P4, class P4, box P3, class P3 (P3/P4/P5 = strides 8/16/32). Each tensor is stored cell by cell with 4 bytes per cell: a box cell holds the left, top, right and bottom distances to the cell centre in grid units, a class cell holds one logit per class followed by padding. Values are 8-bit and dequantised as `(q - zero_point) * scale`.

### yolov8_init { #yolov8_init }

```c
int yolov8_init(yolov8_config_t *config, struct iproai_net_info_t *net);
```

Initialise the YOLOv8 detector for a loaded model.

Sets the defaults (input [`YOLOV8_INPUT_WIDTH`](#yolov8_detect-h-macros) x [`YOLOV8_INPUT_HEIGHT`](#yolov8_detect-h-macros), [`YOLOV8_NUM_CLASSES`](#yolov8_detect-h-macros) classes, default thresholds), reads the quantisation of the six outputs and the cell count of each level from `net`, and allocates the anchor grid, the sigmoid table and the buffers with `malloc()`. `class_names` is not touched.

| 參數 | 說明 |
|---|---|
| `config` | Detector state to fill. |
| `net` | Network information from [`iproai_getNetInfo()`](#iproai_getNetInfo); the model must have exactly [`YOLOV8_NUM_OUTPUTS`](#yolov8_detect-h-macros) outputs. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL argument, the model does not have six outputs, or an allocation failed. |

!!! note "注意"
    The anchor grid is generated from the default input size with the height rounded down to a multiple of 16 (640 x 352): the model's output grids must be 80 x 44, 40 x 22 and 20 x 11 cells for the boxes to decode correctly.

### yolov8_process_6out { #yolov8_process_6out }

```c
int yolov8_process_6out(yolov8_config_t *config, struct iproai_net_info_t *net, uint8_t *data_buffer, yolov8_result_t *result);
```

Decode the six output tensors of one inference into detections.

For every cell the highest class logit is taken; cells whose confidence (sigmoid of that logit) is at least `conf_threshold` become candidates (up to [`YOLOV8_MAX_CANDIDATES`](#yolov8_detect-h-macros), scanning P3, P4, then P5). Their boxes are decoded, then class-wise NMS keeps up to [`YOLOV8_MAX_DETECTIONS`](#yolov8_detect-h-macros) boxes, clamped to the input size and named from `class_names`.

| 參數 | 說明 |
|---|---|
| `config` | Detector initialised with [`yolov8_init()`](#yolov8_init). |
| `net` | Network information of the same model. |
| `data_buffer` | Model data region, from [`iproai_getInputBuffer()`](#iproai_getInputBuffer). Each output tensor is read at `out_layer_mem * patch_size` bytes from it. |
| `result` | Receives the detections; `num_detections` is 0 when nothing passes the threshold. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, including when nothing is detected. |
| `-1` | A NULL argument or a temporary allocation failed. |

!!! note "注意"
    Allocates temporary buffers with `malloc()` on each call.

### yolov8_deinit { #yolov8_deinit }

```c
void yolov8_deinit(yolov8_config_t *config);
```

Free the buffers allocated by [`yolov8_init()`](#yolov8_init).

The pointers in `config` are not cleared, so call it only once per successful [`yolov8_init()`](#yolov8_init).

| 參數 | 說明 |
|---|---|
| `config` | Detector state; NULL is ignored. |

### yolov8_print_results { #yolov8_print_results }

```c
void yolov8_print_results(const yolov8_result_t *result);
```

Print detection results to the console.

| 參數 | 說明 |
|---|---|
| `result` | Results to print; NULL is ignored. |

### yolov8_generate_anchors { #yolov8_generate_anchors }

```c
yolov8_anchor_grid_t * yolov8_generate_anchors(uint32_t img_height, uint32_t img_width);
```

Build the cell-centre grid of the three detection levels.

Note the argument order: height first. `img_height` is rounded down to a multiple of 16 first. Each level contributes `(img_width / stride) * (img_height / stride)` cells, for strides 8, 16 and 32.

| 參數 | 說明 |
|---|---|
| `img_height` | Model input height, pixels. |
| `img_width` | Model input width, pixels. |

**回傳值**：Grid allocated with `malloc()` (free it with [`yolov8_free_anchor_grid()`](#yolov8_free_anchor_grid)), or NULL if an allocation failed.

### yolov8_free_anchor_grid { #yolov8_free_anchor_grid }

```c
void yolov8_free_anchor_grid(yolov8_anchor_grid_t *grid);
```

Free a grid returned by [`yolov8_generate_anchors()`](#yolov8_generate_anchors).

| 參數 | 說明 |
|---|---|
| `grid` | Grid to free; NULL is ignored. |

### yolov8_softmax { #yolov8_softmax }

```c
void yolov8_softmax(const float *input, float *output, uint32_t size);
```

Compute a numerically stable softmax.

| 參數 | 說明 |
|---|---|
| `input` | Input values, at least one. |
| `output` | Probabilities summing to 1; may be the same array as `input`. |
| `size` | Number of elements. |

### yolov8_dfl { #yolov8_dfl }

```c
void yolov8_dfl(const float *box_pred, uint32_t num_anchors, uint32_t reg_max, float *output);
```

Convert Distribution Focal Loss (DFL) bins to box-side distances.

For each cell and each of the four sides, takes the softmax over the `reg_max` bins and outputs its expected bin index. With `reg_max` equal to 1 the input is copied unchanged.

| 參數 | 說明 |
|---|---|
| `box_pred` | Bin logits, planar `[4 * reg_max][num_anchors]` (side-major, then bin, then cell). |
| `num_anchors` | Number of cells. |
| `reg_max` | Bins per side, 1 to 16. |
| `output` | Distances, planar `[4][num_anchors]` (left, top, right, bottom), in grid units. |

### yolov8_dist2bbox { #yolov8_dist2bbox }

```c
void yolov8_dist2bbox(const float *distances, const yolov8_anchor_grid_t *anchors, uint32_t num_anchors, float *boxes);
```

Convert side distances around cell centres into boxes.

| 參數 | 說明 |
|---|---|
| `distances` | Planar `[4][num_anchors]` left, top, right and bottom distances in grid units. |
| `anchors` | Cell centres and strides from [`yolov8_generate_anchors()`](#yolov8_generate_anchors). |
| `num_anchors` | Number of cells to convert. |
| `boxes` | Planar `[4][num_anchors]` centre x, centre y, width and height in input pixels. |

### yolov8_nms { #yolov8_nms }

```c
int yolov8_nms(const float *boxes, const float *scores, const int *classes, int num_boxes, float iou_threshold, yolov8_detection_t *output);
```

Greedy class-aware non-maximum suppression.

Sorts the boxes by descending score and keeps each box unless an already-kept box of the same class overlaps it with an IoU greater than `iou_threshold`. Stops after [`YOLOV8_MAX_DETECTIONS`](#yolov8_detect-h-macros) boxes.

| 參數 | 說明 |
|---|---|
| `boxes` | Planar `[4][num_boxes]` centre x, centre y, width and height (row stride `num_boxes`). |
| `scores` | Score of each box. |
| `classes` | Class index of each box. |
| `num_boxes` | Number of boxes. |
| `iou_threshold` | IoU above which a box is suppressed. |
| `output` | Kept detections, highest score first, as corner boxes with confidence and class index (the class name is not set). Room for `min(num_boxes, YOLOV8_MAX_DETECTIONS)` entries. |

**回傳值**：Number of detections written, or -1 if a temporary buffer could not be allocated.

### yolov8_box_iou { #yolov8_box_iou }

```c
float yolov8_box_iou(const yolov8_box_t *box1, const yolov8_box_t *box2);
```

Compute the intersection over union of two boxes.

| 參數 | 說明 |
|---|---|
| `box1` | First box. |
| `box2` | Second box. |

**回傳值**：IoU in [0, 1]; 0 if the union area is not positive.

### yolov8_sigmoid_lut { #yolov8_sigmoid_lut }

```c
float yolov8_sigmoid_lut(const float *sigmoid_table, uint32_t table_size, float x);
```

Evaluate the sigmoid with a lookup table.

Interpolates linearly in a table that samples the sigmoid uniformly over [-10, 10], such as `yolov8_config_t::sigmoid_table`. Outside that range the sigmoid is computed exactly.

| 參數 | 說明 |
|---|---|
| `sigmoid_table` | Table of sigmoid values over [-10, 10]. |
| `table_size` | Number of entries in the table. |
| `x` | Input value. |

**回傳值**：Sigmoid of `x`, 0 to 1.

### yolov8_box_t { #yolov8_box_t }

Axis-aligned bounding box in input-image pixels.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `x1` | `float` | Left edge. |
| `y1` | `float` | Top edge. |
| `x2` | `float` | Right edge. |
| `y2` | `float` | Bottom edge. |

### yolov8_detection_t { #yolov8_detection_t }

One detected object.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `box` | `yolov8_box_t` | Bounding box, input-image pixels. |
| `confidence` | `float` | Class confidence after sigmoid, 0 to 1. |
| `class_id` | `int` | Class index. |
| `class_name` | `const char *` | Class name (static string, not owned). Set by the process functions; [`yolov8_nms()`](#yolov8_nms) leaves it unset. |

### yolov8_result_t { #yolov8_result_t }

Detection results of one frame.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `detections` | `yolov8_detection_t[YOLOV8_MAX_DETECTIONS]` | Detections, highest confidence first. |
| `num_detections` | `int` | Number of valid entries in `detections`. |
| `inference_time_ms` | `uint32_t` | Time spent in the post-processing call itself (not the NPU inference), in RTOS ticks, which are milliseconds at the default 1 kHz tick rate. |

### yolov8_anchor_grid_t { #yolov8_anchor_grid_t }

Cell centres and strides of all detection levels.

Built by [`yolov8_generate_anchors()`](#yolov8_generate_anchors); entries are ordered P3, P4, P5 and row by row within a level.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `anchors` | `float *` | Cell centres `(x + 0.5, y + 0.5)` in grid units, `num_anchors * 2` floats. |
| `strides` | `float *` | Stride of each cell's level, `num_anchors` floats. |
| `num_anchors` | `uint32_t` | Total number of cells over all levels. |

### yolov8_quant_param_t { #yolov8_quant_param_t }

Quantisation parameters of one output tensor.

Real value = `(q - zero_point) * scale`.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `scale` | `float` | Dequantisation scale. |
| `zero_point` | `int32_t` | Dequantisation zero point. |

### yolov8_config_t { #yolov8_config_t }

Detector configuration and state.

Filled by [`yolov8_init()`](#yolov8_init). `conf_threshold`, `iou_threshold` and `class_names` may be changed after init; the other fields describe the model and the allocated buffers and must be left alone.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `input_width` | `uint32_t` | Model input width, pixels; boxes are clamped to it. |
| `input_height` | `uint32_t` | Model input height, pixels; boxes are clamped to it. |
| `num_classes` | `uint32_t` | Number of class logits used per cell (at most 4). |
| `reg_max` | `uint32_t` | DFL bins per box side ([`YOLOV8_REG_MAX`](#yolov8_detect-h-macros)). |
| `class_names` | `const char **` | Class-name table indexed by class ID, or NULL to report "unknown". [`yolov8_init()`](#yolov8_init) does not set it; [`yolov8_person_pet_init()`](#yolov8_person_pet_init) does. |
| `conf_threshold` | `float` | Minimum class confidence (0 to 1) for a candidate. |
| `iou_threshold` | `float` | NMS IoU threshold. |
| `net` | `struct iproai_net_info_t *` | Network information passed to [`yolov8_init()`](#yolov8_init). |
| `anchor_grid` | `yolov8_anchor_grid_t *` | Cell centres and strides (allocated by init). |
| `quant_params` | `yolov8_quant_param_t[YOLOV8_NUM_OUTPUTS]` | Quantisation of each output tensor, in `net->output_layer[]` order. |
| `layer_sizes` | `uint32_t[YOLOV8_NUM_LAYERS]` | Number of cells of levels P3, P4 and P5, from the output tensor shapes. |
| `total_anchors` | `uint32_t` | Sum of `layer_sizes`. |
| `sigmoid_table` | `float *` | Sigmoid lookup table over [-10, 10] (allocated by init). |
| `sigmoid_table_size` | `uint32_t` | Number of entries in `sigmoid_table`. |
| `mem_pool` | `struct yolov8_config_t::@033366200166222020246111320212342155333172174122` | Buffers allocated by [`yolov8_init()`](#yolov8_init) and reused for every frame. |

### 巨集 { #yolov8_detect-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `YOLOV8_STRIDE_P3` | `8` | Stride of level P3. |
| `YOLOV8_STRIDE_P4` | `16` | Stride of level P4. |
| `YOLOV8_STRIDE_P5` | `32` | Stride of level P5. |
| `YOLOV8_INPUT_WIDTH` | `640` | Default model input width, pixels. |
| `YOLOV8_INPUT_HEIGHT` | `360` | Default model input height, pixels. |
| `YOLOV8_NUM_CLASSES` | `2` | Default number of classes (person, pet). |
| `YOLOV8_NUM_LAYERS` | `3` | Detection levels: P3, P4, P5. |
| `YOLOV8_NUM_OUTPUTS` | `6` | Output tensors: 3 box heads + 3 class heads. |
| `YOLOV8_REG_MAX` | `1` | DFL bins per box side; 1 means the box head outputs the distances directly. |
| `YOLOV8_MAX_DETECTIONS` | `50` | Size of `yolov8_result_t::detections` and maximum number of boxes kept by [`yolov8_nms()`](#yolov8_nms). |
| `YOLOV8_MAX_CANDIDATES` | `200` | Maximum number of cells above the confidence threshold that [`yolov8_process_6out()`](#yolov8_process_6out) keeps per frame; further cells are dropped. |
| `YOLOV8_DEFAULT_CONF_THRESHOLD` | `0.25f` | Default minimum class confidence (after sigmoid) for a candidate. |
| `YOLOV8_DEFAULT_IOU_THRESHOLD` | `0.45f` | Default IoU above which NMS suppresses the lower-scoring box. |

## yolov8_person_pet_detect.h { #yolov8_person_pet_detect-h }

`#include "yolov8_person_pet_detect.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/detect/yolov8_person_pet_detect.h)）

Person and pet detection: YOLOv8 post-processor preset.

Thin wrapper around [`yolov8_detect.h`](#yolov8_detect-h) for the two-class person/pet model: [`yolov8_person_pet_init()`](#yolov8_person_pet_init) configures the generic detector with the class names below, and the other functions forward to their yolov8_* counterparts with extra console logging. Use the yolov8_* functions directly if the logging is not wanted.

### yolov8_person_pet_init { #yolov8_person_pet_init }

```c
int yolov8_person_pet_init(yolov8_config_t *config, struct iproai_net_info_t *net);
```

Initialise the detector for the person/pet model.

Calls [`yolov8_init()`](#yolov8_init), then sets two classes, the [`yolov8_person_pet_class_names`](#yolov8_person_pet_detect-h-typedefs) table and the default thresholds, and prints the resulting configuration.

| 參數 | 說明 |
|---|---|
| `config` | Detector state to fill. |
| `net` | Network information from [`iproai_getNetInfo()`](#iproai_getNetInfo). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL argument or [`yolov8_init()`](#yolov8_init) failed. |

### yolov8_person_pet_process { #yolov8_person_pet_process }

```c
int yolov8_person_pet_process(yolov8_config_t *config, struct iproai_net_info_t *net, uint8_t *data_buffer, yolov8_result_t *result);
```

Decode one inference of the person/pet model.

Calls [`yolov8_process_6out()`](#yolov8_process_6out) and logs the number of detections.

| 參數 | 說明 |
|---|---|
| `config` | Detector initialised with [`yolov8_person_pet_init()`](#yolov8_person_pet_init). |
| `net` | Network information of the model. |
| `data_buffer` | Model data region, from [`iproai_getInputBuffer()`](#iproai_getInputBuffer). |
| `result` | Receives the detections. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, including when nothing is detected. |
| `-1` | A NULL argument or the decoding failed. |

### yolov8_person_pet_process_6out { #yolov8_person_pet_process_6out }

```c
int yolov8_person_pet_process_6out(yolov8_config_t *config, iproai_model_hdl_t hdl, yolov8_result_t *result);
```

Former decode entry point taking a model handle.

DeprecatedUse yolov8_person_pet_process(). This function does nothing except print an error message.

| 參數 | 說明 |
|---|---|
| `config` | Unused. |
| `hdl` | Unused. |
| `result` | Not written. |

**回傳值**：Always -1.

### yolov8_person_pet_deinit { #yolov8_person_pet_deinit }

```c
void yolov8_person_pet_deinit(yolov8_config_t *config);
```

Free the detector buffers.

Calls [`yolov8_deinit()`](#yolov8_deinit); the same once-per-init rule applies.

| 參數 | 說明 |
|---|---|
| `config` | Detector state; NULL is ignored. |

### yolov8_person_pet_print_results { #yolov8_person_pet_print_results }

```c
void yolov8_person_pet_print_results(const yolov8_result_t *result);
```

Print person/pet detection results to the console.

Prints each box with its centre and size, the number of persons and pets, and the post-processing time.

| 參數 | 說明 |
|---|---|
| `result` | Results to print; NULL is ignored. |

### 型別定義 { #yolov8_person_pet_detect-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `yolov8_person_pet_class_names` | `const char* yolov8_person_pet_class_names[]` | Class names of the person/pet model: index 0 is "person", index 1 is "pet". |

### 巨集 { #yolov8_person_pet_detect-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `YOLOV8_PERSON_PET_NUM_CLASSES` | `2` | Number of classes of the person/pet model. |

## gesture_dfl_detect.h { #gesture_dfl_detect-h }

`#include "gesture_dfl_detect.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/detect/gesture_dfl_detect.h)）

Post-processor for the hand-sign digit detector (YOLOv8-ReLU, anchor-free with DFL boxes) on the IPRO7-AI NPU.

The model recognises hand signs for the digits 0 to 9. It has 3 raw output heads (P3/P4/P5), each of shape [1, H, W, 74]:

- channels 0..63: DFL box regression, 4 sides x 16 bins;
- channels 64..73: 10 class logits (digits 0 to 9), no objectness.

Decoding, with every value dequantised as `f(q) = (q - zero_point) * scale`:

```text
reg[side][b] = f(ch[side * 16 + b]),  b = 0..15
dist[side]   = sum over b of softmax(reg[side])[b] * b
ax, ay       = grid_x + 0.5, grid_y + 0.5
x1 = (ax - dist[0]) * stride      y1 = (ay - dist[1]) * stride
x2 = (ax + dist[2]) * stride      y2 = (ay + dist[3]) * stride
score[c] = sigmoid(f(ch[64 + c])); class = argmax(score); conf = max(score)
```

Cells with `conf >= conf_threshold` go through greedy NMS ([`yolov8_nms()`](#yolov8_nms)). The results use the [`yolov8_detect.h`](#yolov8_detect-h) types ([`yolov8_result_t`](#yolov8_result_t)).

NPU output memory: channels are padded to a multiple of 4 per cell (76 bytes), so `value(h, w, c)` is at `data_buffer + out_layer_mem * patch_size + (h * W + w) * 76 + c`.

Typical sequence: [`gdfl_init()`](#gdfl_init) after loading the model, then per frame [`iproai_startCompute()`](#iproai_startCompute) and [`gdfl_process()`](#gdfl_process), and [`gdfl_deinit()`](#gdfl_deinit) when done.

### gdfl_init { #gdfl_init }

```c
int gdfl_init(gdfl_config_t *cfg, struct iproai_net_info_t *net);
```

Initialise the hand-sign digit post-processor.

Clears `cfg`, applies the default thresholds, resolves the three output levels (grid size, stride, quantisation) from `net` and allocates the scratch buffers with `malloc()`.

| 參數 | 說明 |
|---|---|
| `cfg` | Detector state to fill. |
| `net` | Network information from [`iproai_getNetInfo()`](#iproai_getNetInfo). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL argument, the model does not have exactly three outputs, or an allocation failed. |

### gdfl_process { #gdfl_process }

```c
int gdfl_process(gdfl_config_t *cfg, struct iproai_net_info_t *net, uint8_t *data_buffer, yolov8_result_t *result);
```

Decode the three 8-bit output heads and run NMS.

Invalidates the data cache over the three output regions before reading them, since the NPU writes its outputs to memory behind the CPU cache. At the default log level it also prints the raw values of two cells and the peak class score of the frame, which helps to spot an input that does not reach the NPU.

| 參數 | 說明 |
|---|---|
| `cfg` | Detector state from [`gdfl_init()`](#gdfl_init). |
| `net` | Network information of the same model. |
| `data_buffer` | Model data region, from [`iproai_getInputBuffer()`](#iproai_getInputBuffer). |
| `result` | Receives the detections, boxes in input pixels clamped to the input size, class names "0".."9". |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, including when nothing is detected. |
| `-1` | A NULL argument or a temporary allocation failed. |

!!! note "注意"
    Allocates a temporary candidate buffer with `malloc()` on each call.

### gdfl_deinit { #gdfl_deinit }

```c
void gdfl_deinit(gdfl_config_t *cfg);
```

Release the scratch buffers.

The buffer pointers are cleared, so calling it twice is harmless.

| 參數 | 說明 |
|---|---|
| `cfg` | Detector state; NULL is ignored. |

### gdfl_print_results { #gdfl_print_results }

```c
void gdfl_print_results(const yolov8_result_t *result);
```

Print detections to the console.

| 參數 | 說明 |
|---|---|
| `result` | Results to print; NULL is ignored. |

### gdfl_level_t { #gdfl_level_t }

Per-output-level descriptor, resolved from the network information by [`gdfl_init()`](#gdfl_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `layer_idx` | `uint32_t` | Index of the output layer in `net->layers[]`. |
| `out_w` | `uint32_t` | Grid width of the level, cells. |
| `out_h` | `uint32_t` | Grid height of the level, cells. |
| `ch_stride` | `uint32_t` | Bytes per cell: channel count rounded up to 4 (76). |
| `stride` | `uint32_t` | Input pixels per cell: input width / grid width (8, 16 or 32). |
| `scale` | `float` | Dequantisation scale of the output. |
| `zero_point` | `int32_t` | Dequantisation zero point of the output. |

### gdfl_config_t { #gdfl_config_t }

Detector configuration and scratch state.

Filled by [`gdfl_init()`](#gdfl_init); `conf_threshold` and `iou_threshold` may be changed afterwards.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `input_width` | `uint32_t` | Model input width, pixels: the network width, or 8 x the finest grid width if the network does not report one. |
| `input_height` | `uint32_t` | Model input height, pixels (same rule). |
| `conf_threshold` | `float` | Minimum class confidence (after sigmoid) for a candidate. |
| `iou_threshold` | `float` | NMS IoU threshold. |
| `net` | `struct iproai_net_info_t *` | Network information passed to [`gdfl_init()`](#gdfl_init). |
| `levels` | `gdfl_level_t[GDFL_NUM_LAYERS]` | Output levels, in `net->output_layer[]` order. |
| `mem_pool` | `struct gdfl_config_t::@336051311063327004164035106170012051221060060310` | Scratch buffers allocated by [`gdfl_init()`](#gdfl_init) and reused per frame. |

### 型別定義 { #gesture_dfl_detect-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `gdfl_class_names` | `const char* gdfl_class_names[]` | Class names "0" to "9", indexed by class ID. |

### 巨集 { #gesture_dfl_detect-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `GDFL_NUM_LAYERS` | `3` | Output levels: P3, P4, P5. |
| `GDFL_REG_MAX` | `16` | DFL bins per box side. |
| `GDFL_NUM_CLASSES` | `10` | Classes: digits 0 to 9. |
| `GDFL_OUT_CH` | `(4 * GDFL_REG_MAX + GDFL_NUM_CLASSES)` | Channels per cell (74). |
| `GDFL_MAX_DETECTIONS` | `50` | Entries allocated for the NMS output. |
| `GDFL_MAX_CANDIDATES` | `512` | Maximum number of cells above the confidence threshold kept per frame; further ones are dropped. |
| `GDFL_DEFAULT_CONF` | `0.25f` | Default minimum class confidence. |
| `GDFL_DEFAULT_IOU` | `0.45f` | Default NMS IoU threshold. |

## big_a_sppf_detect.h { #big_a_sppf_detect-h }

`#include "big_a_sppf_detect.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/detect/big_a_sppf_detect.h)）

Post-processor for the BIG-A + SPPF-lite single-class product detector (SKU-110K) on the IPRO7-AI NPU.

This model is a YOLOv5-style anchor-based detector, unlike the anchor-free YOLOv8 models of [`yolov8_detect.h`](#yolov8_detect-h). It has 3 output levels (P3/P4/P5), each of shape [1, H, W, 18] where 18 = 3 anchor slots x (4 box + 1 objectness + 1 class) values, for a single class.

Decoding, with every value dequantised as `(q - zero_point) * scale`:

```text
cx = (sigmoid(tx) + grid_x) / grid_w      (normalised 0..1)
cy = (sigmoid(ty) + grid_y) / grid_h
bw = exp(tw)                              (normalised, no anchor prior)
bh = exp(th)
score = sigmoid(obj) * sigmoid(cls)
box = [cx - bw/2, cy - bh/2, cx + bw/2, cy + bh/2] * input size
```

followed by greedy NMS ([`yolov8_nms()`](#yolov8_nms)). The results use the [`yolov8_detect.h`](#yolov8_detect-h) types ([`yolov8_result_t`](#yolov8_result_t)), so code that consumes YOLOv8 detections works unchanged.

Typical sequence: [`big_a_sppf_init()`](#big_a_sppf_init) after loading the model, then per frame [`iproai_startCompute()`](#iproai_startCompute) and [`big_a_sppf_process()`](#big_a_sppf_process), and [`big_a_sppf_deinit()`](#big_a_sppf_deinit) when done.

### big_a_sppf_init { #big_a_sppf_init }

```c
int big_a_sppf_init(big_a_sppf_config_t *config, struct iproai_net_info_t *net);
```

Initialise the BIG-A + SPPF-lite post-processor.

Clears `config`, applies the default thresholds, resolves the three output levels from `net` and allocates the scratch buffers with `malloc()`. The output order does not matter: each level is decoded with its own grid size.

| 參數 | 說明 |
|---|---|
| `config` | Detector state to fill. |
| `net` | Network information from [`iproai_getNetInfo()`](#iproai_getNetInfo). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL argument, the model does not have exactly three outputs, or an allocation failed. |

### big_a_sppf_process { #big_a_sppf_process }

```c
int big_a_sppf_process(big_a_sppf_config_t *config, struct iproai_net_info_t *net, uint8_t *data_buffer, yolov8_result_t *result);
```

Decode the three 8-bit output tensors and run NMS.

| 參數 | 說明 |
|---|---|
| `config` | Detector state from [`big_a_sppf_init()`](#big_a_sppf_init). |
| `net` | Network information of the same model. |
| `data_buffer` | Model data region, from [`iproai_getInputBuffer()`](#iproai_getInputBuffer). Each output level is read at `out_layer_mem * patch_size` bytes from it. |
| `result` | Receives the detections, boxes in input pixels clamped to the input size. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, including when nothing is detected. |
| `-1` | A NULL argument or a temporary allocation failed. |

!!! note "注意"
    Allocates a temporary candidate buffer with `malloc()` on each call.

### big_a_sppf_deinit { #big_a_sppf_deinit }

```c
void big_a_sppf_deinit(big_a_sppf_config_t *config);
```

Release the scratch buffers.

The buffer pointers are cleared, so calling it twice is harmless.

| 參數 | 說明 |
|---|---|
| `config` | Detector state; NULL is ignored. |

### big_a_sppf_print_results { #big_a_sppf_print_results }

```c
void big_a_sppf_print_results(const yolov8_result_t *result);
```

Print detections to the console.

| 參數 | 說明 |
|---|---|
| `result` | Results to print; NULL is ignored. |

### big_a_sppf_level_t { #big_a_sppf_level_t }

Per-output-level descriptor, resolved from the network information by [`big_a_sppf_init()`](#big_a_sppf_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `layer_idx` | `uint32_t` | Index of the output layer in `net->layers[]`. |
| `out_w` | `uint32_t` | Grid width, cells (e.g. 32 / 16 / 8 for a 256-pixel input). |
| `out_h` | `uint32_t` | Grid height, cells. |
| `ch_stride` | `uint32_t` | Bytes per cell: channel count rounded up to 4 (18 -&gt; 20). |
| `scale` | `float` | Dequantisation scale of the output. |
| `zero_point` | `int32_t` | Dequantisation zero point of the output. |

### big_a_sppf_config_t { #big_a_sppf_config_t }

Detector configuration and scratch state.

Filled by [`big_a_sppf_init()`](#big_a_sppf_init); `conf_threshold` and `iou_threshold` may be changed afterwards.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `input_width` | `uint32_t` | Model input width, pixels: the network width, or 8 x the finest grid width if the network does not report one. |
| `input_height` | `uint32_t` | Model input height, pixels (same rule as the width). |
| `num_classes` | `uint32_t` | Number of classes ([`BIG_A_SPPF_NUM_CLASSES`](#big_a_sppf_detect-h-macros)). |
| `conf_threshold` | `float` | Minimum score, `sigmoid(obj) * sigmoid(cls)`. |
| `iou_threshold` | `float` | NMS IoU threshold. |
| `net` | `struct iproai_net_info_t *` | Network information passed to [`big_a_sppf_init()`](#big_a_sppf_init). |
| `levels` | `big_a_sppf_level_t[BIG_A_SPPF_NUM_LAYERS]` | Output levels, in `net->output_layer[]` order. |
| `mem_pool` | `struct big_a_sppf_config_t::@170307112237052303113173136152342267120067025000` | Scratch buffers allocated by [`big_a_sppf_init()`](#big_a_sppf_init), reused per frame. |

### 型別定義 { #big_a_sppf_detect-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `big_a_sppf_class_names` | `const char* big_a_sppf_class_names[]` | Class-name table: index 0 is "product". |

### 巨集 { #big_a_sppf_detect-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `BIG_A_SPPF_NUM_LAYERS` | `3` | Output levels: P3, P4, P5. |
| `BIG_A_SPPF_ANCHORS` | `3` | Anchor slots per cell. |
| `BIG_A_SPPF_NUM_CLASSES` | `1` | Single class ("product"). |
| `BIG_A_SPPF_FIELDS` | `6` | Values per anchor slot: tx, ty, tw, th, obj, cls. |
| `BIG_A_SPPF_OUT_CH` | `(BIG_A_SPPF_ANCHORS * BIG_A_SPPF_FIELDS)` | Channels per cell (18). |
| `BIG_A_SPPF_MAX_DETECTIONS` | `64` | Number of entries allocated for the NMS output. At most [`YOLOV8_MAX_DETECTIONS`](#yolov8_detect-h-macros) detections are reported. |
| `BIG_A_SPPF_MAX_CANDIDATES` | `512` | Maximum number of anchor slots above the score threshold kept per frame; further ones are dropped. |
| `BIG_A_SPPF_DEFAULT_CONF` | `0.25f` | Default minimum score for a candidate. |
| `BIG_A_SPPF_DEFAULT_IOU` | `0.45f` | Default NMS IoU threshold. |

## fbank.h { #fbank-h }

`#include "fbank.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/audio/fbank.h)）

Log mel-filterbank feature extraction for the speaker-embedding model.

Converts 16 kHz mono PCM into a fixed `[FBANK_SEQ_LEN][FBANK_N_MELS]` matrix of log mel-filterbank energies, the input format of the speaker-embedding model (see [`speaker_embed.h`](#speaker_embed-h), which calls these functions itself).

Per frame (25 ms window, 10 ms hop): DC removal, pre-emphasis ([`FBANK_PREEMPH`](#fbank-h-macros)), Povey window, 512-point FFT, power spectrum, triangular mel filters between [`FBANK_LOW_FREQ`](#fbank-h-macros) and [`FBANK_HIGH_FREQ`](#fbank-h-macros), natural logarithm. After all frames, the mean of each mel bin over the valid frames is subtracted (per-column mean normalisation).

Two interchangeable back-ends implement this header, selected at build time by `CONFIG_AI_FBANK_INT`:

- not set (default): floating-point implementation;
- set: fixed-point implementation (Q15 tables, Q8 logarithm) for the IPRO7 DSP extension. Its output matches the float back-end within quantisation noise.

The layout of [`FBankContext`](#FBankContext) differs between the back-ends, but callers only allocate `sizeof(FBankContext)` and pass the pointer to [`fbank_init()`](#fbank_init) and [`fbank_compute()`](#fbank_compute), so application code is the same for both.

### fbank_init { #fbank_init }

```c
void fbank_init(FBankContext *ctx);
```

Compute the analysis window and mel filterbank.

Call once at start-up; the context is read-only afterwards and can be reused for any number of [`fbank_compute()`](#fbank_compute) calls.

| 參數 | 說明 |
|---|---|
| `ctx` | Context to fill. Must not be NULL. |

### fbank_compute { #fbank_compute }

```c
int fbank_compute(const FBankContext *ctx, const int16_t *samples, int n_samples, float out[FBANK_SEQ_LEN][FBANK_N_MELS]);
```

Compute normalised log mel-filterbank features for one clip.

Frames are taken every [`FBANK_FRAME_SHIFT`](#fbank-h-macros) samples while a full [`FBANK_FRAME_LEN`](#fbank-h-macros) window fits, up to [`FBANK_SEQ_LEN`](#fbank-h-macros) frames; samples beyond that are ignored. A full 300-frame matrix needs 48240 samples (3.015 s). Rows after the last valid frame are zero before normalisation. The per-bin mean of the valid rows is then subtracted from every row, so padding rows end up holding minus that mean.

| 參數 | 說明 |
|---|---|
| `ctx` | Context prepared by [`fbank_init()`](#fbank_init). |
| `samples` | Signed 16-bit mono PCM at [`FBANK_SAMPLE_RATE`](#fbank-h-macros) Hz. |
| `n_samples` | Number of samples in `samples`. |
| `out` | Output matrix `[FBANK_SEQ_LEN][FBANK_N_MELS]`, row-major (one row per frame), natural-log units. |

**回傳值**：Number of valid frames extracted (0 to [`FBANK_SEQ_LEN`](#fbank-h-macros), before padding); 0 when `n_samples` is shorter than one window.

!!! note "注意"
    The float back-end keeps about 7 KB of working buffers on the caller's stack. The fixed-point back-end uses static scratch buffers instead, so in that build calls must not run concurrently.

### FBankContext { #FBankContext }

Pre-computed window and mel filterbank (floating-point back-end).

Fill once with [`fbank_init()`](#fbank_init) and reuse for every [`fbank_compute()`](#fbank_compute) call. About 84 KB, so allocate it on the heap or in static memory.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `window` | `float[FBANK_FRAME_LEN]` | Povey window. |
| `mel_fb` | `float[FBANK_N_MELS][FBANK_N_BINS]` | Mel filter weights per FFT bin. |
| `mel_lo` | `int16_t[FBANK_N_MELS]` | First non-zero bin of each triangular filter; the filterbank sum only visits bins `mel_lo[m]..mel_hi[m]`, which gives the same result as the full sum because all other weights are exactly 0. |
| `mel_hi` | `int16_t[FBANK_N_MELS]` | Last non-zero bin of each triangular filter. |

### 巨集 { #fbank-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `FBANK_SEQ_LEN` | `300` | Output frames: 3 s at 100 frames/s. |
| `FBANK_N_MELS` | `80` | Mel bins per frame. |
| `FBANK_SAMPLE_RATE` | `16000` | Expected PCM sample rate, Hz. |
| `FBANK_FRAME_LEN` | `400` | Analysis window, samples (25 ms at 16 kHz). |
| `FBANK_FRAME_SHIFT` | `160` | Hop between frames, samples (10 ms at 16 kHz). |
| `FBANK_FFT_SIZE` | `512` | FFT length: next power of two &gt;= [`FBANK_FRAME_LEN`](#fbank-h-macros). |
| `FBANK_N_BINS` | `(FBANK_FFT_SIZE / 2 + 1)` | Power-spectrum bins (257). |
| `FBANK_LOW_FREQ` | `20.0f` | Lower edge of the mel filterbank, Hz. |
| `FBANK_HIGH_FREQ` | `8000.0f` | Upper edge of the mel filterbank, Hz (Nyquist). |
| `FBANK_PREEMPH` | `0.97f` | Pre-emphasis coefficient. |

## embedding_dim.h { #embedding_dim-h }

`#include "embedding_dim.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/audio/embedding_dim.h)）

Length of the speaker-embedding vector shared by the speaker modules.

Kept in its own header so that the embedding engine ([`speaker_embed.h`](#speaker_embed-h)), the enrolled-speaker gallery ([`gallery.h`](#gallery-h)) and the diarization clusterer ([`diarize.h`](#diarize-h)) agree on the vector length without depending on each other.

### 巨集 { #embedding_dim-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EMBEDDING_DIM` | `256` | Number of float elements in one speaker embedding produced by [`speaker_embed()`](#speaker_embed) and consumed by the gallery and diarization APIs. |

## speaker_embed.h { #speaker_embed-h }

`#include "speaker_embed.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/audio/speaker_embed.h)）

Speaker-embedding engine: PCM clip in, normalised voiceprint out.

Common front end for speaker identification, verification and diarization (see [`gallery.h`](#gallery-h) and [`diarize.h`](#diarize-h)). One call runs the whole pipeline:

```text
int16 PCM, 16 kHz mono
  -> log mel-filterbank [300][80] (fbank.h)
  -> INT8 quantisation, written to the NPU input
  -> speaker-embedding model on the NPU
  -> dequantisation and L2 normalisation -> embedding[EMBEDDING_DIM]
```

Typical sequence: [`speaker_embed_init()`](#speaker_embed_init) or [`speaker_embed_init_buf()`](#speaker_embed_init_buf) once, then [`speaker_embed()`](#speaker_embed) per clip.

The engine keeps a single model instance and shared scratch buffers and is not reentrant: serialise all [`speaker_embed()`](#speaker_embed) calls, for example by running them in one task. Each call reprograms the NPU external-input address, so it must also be serialised with other NPU work. The calling task needs a generous stack: with the default floating-point filterbank, the feature extraction alone uses about 7 KB of it (see [`fbank_compute()`](#fbank_compute)).

### speaker_embed_init { #speaker_embed_init }

```c
int speaker_embed_init(const char *model_path);
```

Load the embedding model from a file and initialise the engine.

Reads the whole model file into a temporary heap buffer, then behaves like [`speaker_embed_init_buf()`](#speaker_embed_init_buf). Returns 0 immediately if the engine is already initialised.

| 參數 | 說明 |
|---|---|
| `model_path` | Path of the compiled model file. The file system holding it (for example the SD card) must already be mounted. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, or already initialised. |
| `-1` | The file cannot be opened or read, or initialisation failed. |

### speaker_embed_init_buf { #speaker_embed_init_buf }

```c
int speaker_embed_init_buf(const uint8_t *model_buf);
```

Initialise the engine from a model image already in memory.

Creates the model instance, loads the model, allocates the feature and NPU-input buffers from the FreeRTOS heap and prepares the filterbank. The model is copied during loading, so `model_buf` only needs to stay valid for the duration of this call (it may point into memory-mapped flash). Returns 0 immediately if the engine is already initialised.

| 參數 | 說明 |
|---|---|
| `model_buf` | Start of the compiled model image. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, or already initialised. |
| `-1` | Model creation or loading failed, or a buffer could not be allocated. |

### speaker_embed { #speaker_embed }

```c
int speaker_embed(const int16_t *pcm, int n_samples, float emb[EMBEDDING_DIM]);
```

Compute the L2-normalised speaker embedding of one PCM clip.

Extracts the features with [`fbank_compute()`](#fbank_compute), runs the model on the NPU and blocks until the inference is complete.

| 參數 | 說明 |
|---|---|
| `pcm` | Signed 16-bit mono PCM at 16 kHz. |
| `n_samples` | Number of samples. The model sees at most 300 frames (48240 samples, about 3 s); longer clips are truncated and shorter ones are padded. |
| `emb` | Receives the embedding, [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats with unit L2 norm (left unnormalised only if its norm is effectively zero). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | The engine is not initialised or the inference failed. |

## speaker_recog.h { #speaker_recog-h }

`#include "speaker_recog.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/audio/speaker_recog.h)）

Speaker recognition on a pooled NPU feature map: embeddings, registration and identification.

This module turns the raw output feature map of a speaker model running on the NPU into a speaker embedding and matches it against a small database of registered speakers by cosine similarity. It also provides the matching audio front end (log mel-filterbank features from PCM).

Processing in [`speaker_recog_process()`](#speaker_recog_process):

```text
8-bit NPU output [C*T*F] -> dequantise -> statistics pooling (mean and
standard deviation, 2*C*T values) -> Linear + ReLU + BatchNorm ->
Linear -> embedding[emb_size]
```

The two linear stages run on the CPU with float weights loaded by [`speaker_recog_init()`](#speaker_recog_init) (from a file) or [`speaker_recog_load_weights_from_buffer()`](#speaker_recog_load_weights_from_buffer).

Typical call sequence:

1. [`speaker_recog_preprocess_init()`](#speaker_recog_preprocess_init), then [`speaker_recog_preprocess_pcm()`](#speaker_recog_preprocess_pcm) to build the model input from PCM.
1. [`speaker_recog_init()`](#speaker_recog_init) (and [`speaker_recog_set_net()`](#speaker_recog_set_net) once the model is loaded), run the model with [`iproai_startCompute()`](#iproai_startCompute).
1. [`speaker_recog_process()`](#speaker_recog_process) on the model output.
1. [`speaker_recog_register()`](#speaker_recog_register) to store the new embedding as a speaker, or read the identification result filled in by step 3.
1. [`speaker_recog_deinit()`](#speaker_recog_deinit) and [`speaker_recog_preprocess_deinit()`](#speaker_recog_preprocess_deinit) when done.

For the end-to-end embedding engine with a 256-element voiceprint, see [`speaker_embed.h`](#speaker_embed-h) and [`gallery.h`](#gallery-h) instead.

### speaker_recog_init { #speaker_recog_init }

```c
int speaker_recog_init(speaker_recog_config_t *config, struct iproai_net_info_t *net, const char *weights_path);
```

Initialise the speaker recognition module.

Clears `config`, sets the default model dimensions and threshold, takes the output quantisation parameters from `net` (if given), allocates the working buffers and one embedding per database slot from the FreeRTOS heap, and loads the linear-stage weights from `weights_path`.

The database is not empty afterwards: slots 0 and 1 hold two built-in example speakers. Call [`speaker_recog_clear()`](#speaker_recog_clear) to start with an empty database.

| 參數 | 說明 |
|---|---|
| `config` | Configuration to initialise. |
| `net` | Network information of the model, or NULL to set it later with [`speaker_recog_set_net()`](#speaker_recog_set_net). |
| `weights_path` | Weights file to read; NULL selects [`SPEAKER_RECOG_DEFAULT_WEIGHTS_PATH`](#speaker_recog-h-macros), and an empty string skips loading so that the caller can supply the weights with [`speaker_recog_load_weights_from_buffer()`](#speaker_recog_load_weights_from_buffer). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `config` is NULL, an allocation failed, or the weights file is missing, unreadable or smaller than the expected size. All resources are released in that case. |

### speaker_recog_load_weights_from_buffer { #speaker_recog_load_weights_from_buffer }

```c
int speaker_recog_load_weights_from_buffer(speaker_recog_config_t *config, const uint8_t *buf, uint32_t len);
```

Use weights already in memory (zero-copy).

Use when the weights are linked into the firmware or memory-mapped from flash instead of read from a file. The buffer is not copied, and [`speaker_recog_deinit()`](#speaker_recog_deinit) does not free it, so it must stay valid as long as `config` is used.

The layout is the same as the weights file: W1, b1, running_mean, running_var, W2, b2, back to back, all float32 little-endian, with the sizes given in [`speaker_recog_weights_t`](#speaker_recog_weights_t). The total is `(emb_size * pool_dim + 4 * emb_size + emb_size * emb_size) * 4` bytes, 993024 bytes for the default dimensions.

| 參數 | 說明 |
|---|---|
| `config` | Configuration initialised with [`speaker_recog_init()`](#speaker_recog_init) and an empty `weights_path`. |
| `buf` | Start of the weights; must be 4-byte aligned. |
| `len` | Size of `buf` in bytes; must be at least the total above. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL argument, `len` of 0, or `len` below the required size. |

### speaker_recog_set_net { #speaker_recog_set_net }

```c
int speaker_recog_set_net(speaker_recog_config_t *config, struct iproai_net_info_t *net);
```

Attach the network information of the model.

Stores `net` and reads the dequantisation scale and zero point of its first output layer. Call after the model is loaded if [`speaker_recog_init()`](#speaker_recog_init) was given NULL.

| 參數 | 說明 |
|---|---|
| `config` | Configuration. |
| `net` | Network information from [`iproai_getNetInfo()`](#iproai_getNetInfo). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `config` or `net` is NULL. |

### speaker_recog_process { #speaker_recog_process }

```c
int speaker_recog_process(speaker_recog_config_t *config, const uint8_t *npu_output, uint32_t output_size, speaker_recog_result_t *result);
```

Compute the speaker embedding of one model output and identify it.

Dequantises the output as `(byte - output_zero_point) * output_scale`, reading the bytes as unsigned, then applies pooling and the two linear stages. The resulting embedding is compared with every registered speaker; the best match is reported if its cosine similarity is greater than or equal to `similarity_threshold`.

| 參數 | 說明 |
|---|---|
| `config` | Configuration with weights loaded. |
| `npu_output` | Raw 8-bit output tensor of the model, for example `iproai_getInputBuffer(hdl)` plus the output layer's `out_layer_mem * patch_size`. |
| `output_size` | Size of `npu_output` in bytes; must be at least `input_c * input_t * input_f`. |
| `result` | Receives the identification result and a pointer to the embedding. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL argument, the module is not initialised, no weights are loaded, or `output_size` is too small. |

!!! note "注意"
    Each call prints a summary of the raw output tensor to the console.

### speaker_recog_deinit { #speaker_recog_deinit }

```c
void speaker_recog_deinit(speaker_recog_config_t *config);
```

Release all resources of the module.

Frees the working buffers, the database embeddings and weights read from a file. Weights supplied with [`speaker_recog_load_weights_from_buffer()`](#speaker_recog_load_weights_from_buffer) are not freed. Safe to call on a partly initialised configuration.

| 參數 | 說明 |
|---|---|
| `config` | Configuration to release; NULL is ignored. |

### speaker_recog_register { #speaker_recog_register }

```c
int speaker_recog_register(speaker_recog_config_t *config, const char *name);
```

Register the most recent embedding as a new speaker.

Copies the embedding computed by the last [`speaker_recog_process()`](#speaker_recog_process) call into the first free database slot.

| 參數 | 說明 |
|---|---|
| `config` | Configuration. |
| `name` | NUL-terminated speaker name; copied and truncated to `SPEAKER_RECOG_MAX_NAME_LEN - 1` characters. |

**回傳值**：Slot index used (0 to `SPEAKER_RECOG_MAX_SPEAKERS - 1`) on success, -1 if an argument is NULL, no embedding has been computed yet, or the database is full.

### speaker_recog_unregister { #speaker_recog_unregister }

```c
int speaker_recog_unregister(speaker_recog_config_t *config, int speaker_id);
```

Remove a registered speaker.

| 參數 | 說明 |
|---|---|
| `config` | Configuration. |
| `speaker_id` | Slot index to free. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `config` is NULL, `speaker_id` is out of range, or the slot is not registered. |

### speaker_recog_clear { #speaker_recog_clear }

```c
void speaker_recog_clear(speaker_recog_config_t *config);
```

Remove all registered speakers, including the built-in examples.

| 參數 | 說明 |
|---|---|
| `config` | Configuration; NULL is ignored. |

### speaker_recog_get_count { #speaker_recog_get_count }

```c
int speaker_recog_get_count(const speaker_recog_config_t *config);
```

Get the number of registered speakers.

| 參數 | 說明 |
|---|---|
| `config` | Configuration. |

**回傳值**：Number of registered speakers, or 0 if `config` is NULL.

### speaker_recog_get_speaker { #speaker_recog_get_speaker }

```c
const speaker_info_t * speaker_recog_get_speaker(const speaker_recog_config_t *config, int speaker_id);
```

Get a registered speaker by slot index.

| 參數 | 說明 |
|---|---|
| `config` | Configuration. |
| `speaker_id` | Slot index, 0 to `SPEAKER_RECOG_MAX_SPEAKERS - 1`. |

**回傳值**：Pointer to the slot, or NULL if `config` is NULL, the index is out of range or the slot is not registered.

### speaker_recog_print_result { #speaker_recog_print_result }

```c
void speaker_recog_print_result(const speaker_recog_result_t *result);
```

Print an identification result to the console.

| 參數 | 說明 |
|---|---|
| `result` | Result to print; NULL is ignored. |

### speaker_recog_print_speakers { #speaker_recog_print_speakers }

```c
void speaker_recog_print_speakers(const speaker_recog_config_t *config);
```

Print the registered speakers to the console.

| 參數 | 說明 |
|---|---|
| `config` | Configuration; NULL is ignored. |

### speaker_recog_cosine_similarity { #speaker_recog_cosine_similarity }

```c
float speaker_recog_cosine_similarity(const float *emb1, const float *emb2, int size);
```

Compute the cosine similarity of two float vectors.

| 參數 | 說明 |
|---|---|
| `emb1` | First vector. |
| `emb2` | Second vector. |
| `size` | Number of elements in each vector. |

**回傳值**：Cosine similarity in [-1, 1], or 0 if either vector has (near) zero norm.

### cosine_int8 { #cosine_int8 }

```c
float cosine_int8(const int8_t *a, const int8_t *b, int size);
```

Compute the cosine similarity of two int8 vectors.

The raw integer values are used, without dequantisation.

| 參數 | 說明 |
|---|---|
| `a` | First vector. |
| `b` | Second vector. |
| `size` | Number of elements in each vector. |

**回傳值**：Cosine similarity in [-1, 1], or 0 if either vector has (near) zero norm.

### speaker_recog_preprocess_init { #speaker_recog_preprocess_init }

```c
int speaker_recog_preprocess_init(const speaker_recog_preprocess_config_t *config);
```

Initialise the audio front end.

Allocates the frame, FFT and filterbank buffers from the FreeRTOS heap and builds the window (Hann raised to the power 0.85) and the mel filterbank. The front end is a single module-wide instance: if it is already initialised, the call returns 0 and `config` is ignored.

| 參數 | 說明 |
|---|---|
| `config` | Front-end configuration, or NULL for the `MFCC_DEFAULT_*` values. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success, or already initialised. |
| `-1` | An allocation failed. |

### speaker_recog_preprocess_deinit { #speaker_recog_preprocess_deinit }

```c
void speaker_recog_preprocess_deinit(void);
```

Release the audio front end.

Frees everything allocated by [`speaker_recog_preprocess_init()`](#speaker_recog_preprocess_init); the front end can then be initialised again with a different configuration.

### speaker_recog_preprocess_pcm { #speaker_recog_preprocess_pcm }

```c
int speaker_recog_preprocess_pcm(const int16_t *pcm_data, int pcm_samples, float *output, int output_size);
```

Convert PCM audio to model input features.

Splits the clip into frames, and for each frame removes the DC offset, applies pre-emphasis (0.97), the window, a real FFT, the mel filterbank and a natural logarithm. Finally the mean of each mel bin over all frames is subtracted. At most [`MFCC_DEFAULT_NUM_FRAMES`](#speaker_recog-h-macros) frames are produced.

| 參數 | 說明 |
|---|---|
| `pcm_data` | Signed 16-bit mono PCM at the configured sample rate. |
| `pcm_samples` | Number of samples in `pcm_data`; must be at least one frame length (400 with the defaults). Shorter clips are rejected only up to frame length minus hop length (240 with the defaults); between the two a single frame of undefined values is produced. |
| `output` | Receives `[num_frames][n_mels]` floats, row-major. |
| `output_size` | Size of `output` in bytes; must be at least `num_frames * n_mels * sizeof(float)`. [`speaker_recog_preprocess_get_output_size()`](#speaker_recog_preprocess_get_output_size) gives a size that is always large enough. |

**回傳值**：Number of frames written (1 to [`MFCC_DEFAULT_NUM_FRAMES`](#speaker_recog-h-macros)) on success, or -1 if the front end is not initialised, the clip is too short, `output_size` is too small, or a temporary buffer cannot be allocated.

### speaker_recog_preprocess_file { #speaker_recog_preprocess_file }

```c
int speaker_recog_preprocess_file(const char *pcm_path, float *output, int output_size);
```

Read a raw PCM file and convert it to model input features.

The file must contain headerless signed 16-bit mono samples; the whole file is read into a temporary heap buffer and passed to [`speaker_recog_preprocess_pcm()`](#speaker_recog_preprocess_pcm).

| 參數 | 說明 |
|---|---|
| `pcm_path` | Path of the PCM file; its file system must be mounted. |
| `output` | Receives `[num_frames][n_mels]` floats, row-major. |
| `output_size` | Size of `output` in bytes. |

**回傳值**：Number of frames written on success, or -1 if the file cannot be opened or read, memory is short, or conversion fails.

### speaker_recog_preprocess_get_required_samples { #speaker_recog_preprocess_get_required_samples }

```c
int speaker_recog_preprocess_get_required_samples(void);
```

Get the number of PCM samples that yields the maximum frame count.

Valid only after [`speaker_recog_preprocess_init()`](#speaker_recog_preprocess_init).

**回傳值**：`(MFCC_DEFAULT_NUM_FRAMES - 1) * hop + frame_length` in samples (47920 for the defaults), or 0 before initialisation.

### speaker_recog_preprocess_get_output_size { #speaker_recog_preprocess_get_output_size }

```c
int speaker_recog_preprocess_get_output_size(void);
```

Get an output buffer size that fits any clip.

May be called before [`speaker_recog_preprocess_init()`](#speaker_recog_preprocess_init); the default mel count is assumed then.

**回傳值**：`MFCC_DEFAULT_NUM_FRAMES * n_mels * sizeof(float)` in bytes (95360 for the defaults).

### speaker_info_t { #speaker_info_t }

One slot of the speaker database.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `embedding` | `float *` | Stored embedding, `emb_size` floats (heap). |
| `name` | `char[SPEAKER_RECOG_MAX_NAME_LEN]` | NUL-terminated speaker name. |
| `valid` | `bool` | True if the slot holds a speaker. |

### speaker_recog_result_t { #speaker_recog_result_t }

Result of [`speaker_recog_process()`](#speaker_recog_process).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `speaker_id` | `int` | Slot of the identified speaker, or -1. |
| `speaker_name` | `const char *` | Name of the identified speaker (points into the database), or NULL if unknown. |
| `similarity` | `float` | Best cosine similarity found, even when below the threshold; -1.0 if no speaker is registered. |
| `embedding` | `float *` | Embedding of this call (`emb_size` floats). Points to an internal buffer that the next [`speaker_recog_process()`](#speaker_recog_process) call overwrites. |
| `process_time_ms` | `uint32_t` | Processing time, milliseconds. |

### speaker_recog_weights_t { #speaker_recog_weights_t }

Weights of the two linear stages that follow the pooling.

All arrays are float32. They point either into `raw_buffer` (weights read from a file) or into a caller-provided buffer.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `W1` | `float *` | First linear layer weights `[emb_size][pool_dim]`. |
| `b1` | `float *` | First linear layer bias `[emb_size]`. |
| `running_mean` | `float *` | BatchNorm running mean `[emb_size]`. |
| `running_var` | `float *` | BatchNorm running variance `[emb_size]`. |
| `W2` | `float *` | Second linear layer weights `[emb_size][emb_size]`. |
| `b2` | `float *` | Second linear layer bias `[emb_size]`. |
| `raw_buffer` | `uint8_t *` | Heap buffer holding the weights read from a file and freed by [`speaker_recog_deinit()`](#speaker_recog_deinit); NULL when the weights were mapped from a caller buffer. |
| `buffer_size` | `uint32_t` | Size of `raw_buffer` in bytes (0 when mapped). |

### speaker_recog_buffers_t { #speaker_recog_buffers_t }

Working buffers allocated by [`speaker_recog_init()`](#speaker_recog_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `dequantized` | `float *` | Dequantised NPU output `[C*T*F]`. |
| `transposed` | `float *` | Dequantised output reordered for pooling `[C*T*F]`. |
| `pooled` | `float *` | Pooled features `[pool_dim]`. |
| `seg1_out` | `float *` | Output of the first linear stage `[emb_size]`. |
| `embedding` | `float *` | Final embedding `[emb_size]`. |

### speaker_database_t { #speaker_database_t }

Database of registered speakers.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `speakers` | `speaker_info_t[SPEAKER_RECOG_MAX_SPEAKERS]` | Speaker slots. |
| `count` | `int` | Number of valid slots. |

### speaker_recog_config_t { #speaker_recog_config_t }

Speaker recognition configuration and state.

Initialise with [`speaker_recog_init()`](#speaker_recog_init); treat the fields as read-only except `similarity_threshold`, which may be changed at any time.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `input_c` | `uint32_t` | C dimension of the model output (default 128). |
| `input_t` | `uint32_t` | T dimension of the model output (default 20). |
| `input_f` | `uint32_t` | F dimension of the model output (default 75). |
| `emb_size` | `uint32_t` | Embedding length (default 48). |
| `pool_dim` | `uint32_t` | Pooled feature length, 2 * C * T (default 5120). |
| `similarity_threshold` | `float` | Minimum cosine similarity for a positive identification. |
| `net` | `struct iproai_net_info_t *` | Network information of the model, or NULL if not set yet. |
| `output_scale` | `float` | Dequantisation scale of the model output. |
| `output_zero_point` | `int32_t` | Dequantisation zero point of the model output. |
| `weights` | `speaker_recog_weights_t` | Linear-stage weights. |
| `buffers` | `speaker_recog_buffers_t` | Working buffers. |
| `database` | `speaker_database_t` | Registered speakers. |
| `initialized` | `bool` | True after a successful [`speaker_recog_init()`](#speaker_recog_init). |
| `weights_loaded` | `bool` | True once the linear-stage weights are available. |
| `has_current_embedding` | `bool` | True once [`speaker_recog_process()`](#speaker_recog_process) has produced an embedding that [`speaker_recog_register()`](#speaker_recog_register) can store. |

### speaker_recog_preprocess_config_t { #speaker_recog_preprocess_config_t }

Audio front-end configuration for [`speaker_recog_preprocess_init()`](#speaker_recog_preprocess_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `sample_rate` | `uint32_t` | Sample rate, Hz (default 16000). |
| `frame_length_ms` | `uint32_t` | Frame length, ms (default 25). |
| `hop_length_ms` | `uint32_t` | Hop between frames, ms (default 10). |
| `n_fft` | `uint32_t` | Not used: the FFT size is always the frame length in samples rounded up to a power of two (512 for the defaults). |
| `n_mels` | `uint32_t` | Number of mel bins (default 80). |
| `fmin` | `float` | Lower edge of the mel filterbank, Hz (default 20). |
| `fmax` | `float` | Upper edge of the mel filterbank, Hz (default 8000). |

### 巨集 { #speaker_recog-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `SPEAKER_RECOG_DEFAULT_C` | `128` | Channels (C) of the model output. |
| `SPEAKER_RECOG_DEFAULT_T` | `20` | T dimension of the model output. |
| `SPEAKER_RECOG_DEFAULT_F` | `75` | F dimension of the model output (pooled). |
| `SPEAKER_RECOG_DEFAULT_EMB_SIZE` | `48` | Embedding length, floats. |
| `SPEAKER_RECOG_DEFAULT_POOL_DIM` | `5120` | Pooled feature length: 2 * C * T. |
| `MFCC_DEFAULT_SAMPLE_RATE` | `16000` | Sample rate, Hz. |
| `MFCC_DEFAULT_FRAME_LEN_MS` | `25` | Frame length, ms (400 samples at 16 kHz). |
| `MFCC_DEFAULT_HOP_LEN_MS` | `10` | Hop length, ms (160 samples at 16 kHz). |
| `MFCC_DEFAULT_NUM_MELS` | `80` | Number of mel bins. |
| `MFCC_DEFAULT_MEL_LOW_FREQ` | `20.0f` | Lower edge of the mel filterbank, Hz. |
| `MFCC_DEFAULT_MEL_HIGH_FREQ` | `8000.0f` | Upper edge of the mel filterbank, Hz. |
| `MFCC_DEFAULT_NUM_FRAMES` | `298` | Maximum number of frames produced per clip. |
| `SPEAKER_RECOG_MAX_SPEAKERS` | `20` | Number of speaker slots in the database. |
| `SPEAKER_RECOG_MAX_NAME_LEN` | `32` | Size of a speaker-name buffer in bytes, including the terminating NUL. |
| `SPEAKER_RECOG_DEFAULT_SIMILARITY_THRESHOLD` | `0.5f` | Default cosine-similarity threshold for accepting an identification. |
| `SPEAKER_RECOG_DEFAULT_WEIGHTS_PATH` | `"/sdcard/ai_model/audio_weights.bin"` | Weights file loaded by [`speaker_recog_init()`](#speaker_recog_init) when its `weights_path` is NULL. |

## gallery.h { #gallery-h }

`#include "gallery.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/audio/gallery.h)）

Enrolled-speaker gallery: enrollment, identification and verification.

Stores one voiceprint (an L2-normalised embedding of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats, see [`speaker_embed.h`](#speaker_embed-h)) per named speaker and compares new embeddings against them by cosine similarity:

- [`gallery_enroll()`](#gallery_enroll) / [`gallery_upsert()`](#gallery_upsert) add or update a speaker;
- [`gallery_identify()`](#gallery_identify) finds the best match among all speakers (1:N);
- [`gallery_verify()`](#gallery_verify) checks one claimed identity (1:1);
- [`gallery_save_to_buf()`](#gallery_save_to_buf) / [`gallery_load_from_buf()`](#gallery_load_from_buf) serialise the gallery to and from a memory image (for example a flash partition).

A [`Gallery`](#Gallery) lives entirely in RAM and has a fixed size of about 135 KB, so place it in static or heap memory. The functions do not lock: callers that share one [`Gallery`](#Gallery) between tasks must serialise access.

Serialised image format (all fields little-endian): Offset 
Size 
Content 


0 
4 
GALLERY_MAGIC 


4 
4 
number of speakers n 


8 
4 
embedding length (EMBEDDING_DIM) 


12 
4 
decision threshold, float32 


16 
n * (64 + 4 * 256) 
per speaker: 64-byte name, then the embedding as float32

The image size is therefore `16 + n * 1088` bytes. The multi-clip enrollment accumulator is not stored.

### gallery_init { #gallery_init }

```c
void gallery_init(Gallery *g, float threshold);
```

Initialise an empty gallery.

Sets the speaker count to 0, the embedding length to [`EMBEDDING_DIM`](#embedding_dim-h-macros) and the decision threshold to `threshold`.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery) to initialise. Must not be NULL. |
| `threshold` | Cosine-similarity decision threshold used by [`gallery_identify()`](#gallery_identify) and [`gallery_verify()`](#gallery_verify), typically [`GALLERY_DEFAULT_THRESHOLD`](#gallery-h-macros). |

### gallery_clear { #gallery_clear }

```c
void gallery_clear(Gallery *g);
```

Remove all enrolled speakers.

The embedding length and the decision threshold are kept.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery) to clear. |

### gallery_load_from_buf { #gallery_load_from_buf }

```c
int gallery_load_from_buf(Gallery *g, const void *buf, size_t len);
```

Load a gallery from a serialised image in memory.

Reads the format described in [`gallery.h`](#gallery-h), including the decision threshold stored in the image. After a successful load each speaker's enrollment accumulator is seeded with its stored voiceprint (count 1), so further [`gallery_enroll()`](#gallery_enroll) calls refine it.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery) to fill. |
| `buf` | Start of the image, for example a memory-mapped flash partition. No alignment requirement. |
| `len` | Number of readable bytes at `buf`. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | Bad magic number, truncated image, more than [`GALLERY_MAX_SPEAKERS`](#gallery-h-macros) speakers or an embedding length other than [`EMBEDDING_DIM`](#embedding_dim-h-macros). `g` may be partly overwritten. |

### gallery_save_to_buf { #gallery_save_to_buf }

```c
int gallery_save_to_buf(const Gallery *g, void *buf, size_t buf_size, int max_speakers);
```

Serialise the gallery into a memory buffer.

Writes the format described in [`gallery.h`](#gallery-h), readable by [`gallery_load_from_buf()`](#gallery_load_from_buf). The enrollment accumulators are not written.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery) to serialise. |
| `buf` | Destination buffer. |
| `buf_size` | Size of `buf` in bytes; must be at least `16 + n * 1088` for the `n` speakers written. |
| `max_speakers` | Write at most this many speakers (the first ones); pass a negative value (or [`GALLERY_MAX_SPEAKERS`](#gallery-h-macros)) for no extra limit. |

**回傳值**：Number of bytes written, or -1 if `buf_size` is too small (nothing is written in that case).

### gallery_upsert { #gallery_upsert }

```c
int gallery_upsert(Gallery *g, const char *name, const float embedding[EMBEDDING_DIM]);
```

Add a speaker, or replace the voiceprint of an existing one.

If a speaker named `name` exists, its stored voiceprint is overwritten with `embedding`; otherwise a new speaker is appended. Unlike [`gallery_enroll()`](#gallery_enroll), this does not update the enrollment accumulator.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery). |
| `name` | NUL-terminated speaker name; truncated to `GALLERY_NAME_LEN - 1` characters. |
| `embedding` | L2-normalised embedding of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | The speaker is new and the gallery already holds [`GALLERY_MAX_SPEAKERS`](#gallery-h-macros) speakers. |

### gallery_enroll { #gallery_enroll }

```c
int gallery_enroll(Gallery *g, const char *name, const float embedding[EMBEDDING_DIM]);
```

Enroll one clip of a speaker (multi-clip enrollment).

Adds `embedding` to the named speaker's accumulator, creating the speaker on the first call, and stores the L2-normalised mean of all clips so far as the voiceprint. Calling it once per clip for three or more clips gives a more robust voiceprint than a single clip.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery). |
| `name` | NUL-terminated speaker name; truncated to `GALLERY_NAME_LEN - 1` characters. |
| `embedding` | L2-normalised embedding of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats. |

**回傳值**：Number of clips accumulated for this speaker so far (1 or more), or -1 if the speaker is new and the gallery is full.

### gallery_identify { #gallery_identify }

```c
int gallery_identify(const Gallery *g, const float embedding[EMBEDDING_DIM], float *score_out);
```

Identify the speaker of an embedding among all enrolled speakers (1:N).

Computes the cosine similarity (dot product of unit vectors) against every stored voiceprint and keeps the best one.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery). |
| `embedding` | L2-normalised embedding of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats. |
| `score_out` | Receives the best similarity, or -2.0 when the gallery is empty. May be NULL. |

**回傳值**：Index (0 to `n - 1`) of the best match if its similarity is greater than or equal to the gallery threshold, otherwise -1 (rejected).

### gallery_remove { #gallery_remove }

```c
int gallery_remove(Gallery *g, int idx);
```

Remove the speaker at an index.

Later entries move down by one so indices stay contiguous; indices returned earlier for those speakers change.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery). |
| `idx` | Index of the speaker to remove, 0 to `n - 1`. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `idx` is out of range. |

### gallery_rename { #gallery_rename }

```c
int gallery_rename(Gallery *g, int idx, const char *name);
```

Rename the speaker at an index.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery). |
| `idx` | Index of the speaker, 0 to `n - 1`. |
| `name` | New NUL-terminated name; truncated to `GALLERY_NAME_LEN - 1` characters. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `idx` is out of range, or `name` is NULL or empty. |
| `-2` | Another speaker already has this name. Names must stay unique because [`gallery_enroll()`](#gallery_enroll), [`gallery_upsert()`](#gallery_upsert) and [`gallery_verify()`](#gallery_verify) look speakers up by name. |

### gallery_verify { #gallery_verify }

```c
int gallery_verify(const Gallery *g, const char *name, const float embedding[EMBEDDING_DIM], float *score_out);
```

Verify a claimed identity (1:1).

Compares `embedding` only with the voiceprint of the speaker called `name`.

| 參數 | 說明 |
|---|---|
| `g` | [`Gallery`](#Gallery). |
| `name` | NUL-terminated name of the claimed speaker. |
| `embedding` | L2-normalised embedding of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats. |
| `score_out` | Receives the cosine similarity, or -2.0 if the speaker does not exist. May be NULL. |

| 回傳碼 | 說明 |
|---|---|
| `1` | Accepted: similarity is greater than or equal to the threshold. |
| `0` | Rejected: similarity is below the threshold. |
| `-2` | No speaker called `name` is enrolled. |

### Gallery { #Gallery }

Speaker gallery: names, voiceprints and enrollment accumulators.

Only the first `n` entries of each array are valid.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `n` | `int` | Number of enrolled speakers. |
| `dim` | `int` | Embedding length; always [`EMBEDDING_DIM`](#embedding_dim-h-macros). |
| `threshold` | `float` | Cosine-similarity decision threshold. |
| `names` | `char[GALLERY_MAX_SPEAKERS][GALLERY_NAME_LEN]` | NUL-terminated speaker names. |
| `embeddings` | `float[GALLERY_MAX_SPEAKERS][EMBEDDING_DIM]` | Stored voiceprints: L2-normalised mean of each speaker's embeddings. |
| `acc` | `float[GALLERY_MAX_SPEAKERS][EMBEDDING_DIM]` | Multi-clip enrollment accumulator: running sum of the embeddings passed to [`gallery_enroll()`](#gallery_enroll); `embeddings` is this sum normalised. |
| `count` | `int[GALLERY_MAX_SPEAKERS]` | Number of clips accumulated per speaker. |

### 巨集 { #gallery-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `GALLERY_MAX_SPEAKERS` | `64` | Maximum number of speakers one [`Gallery`](#Gallery) can hold. |
| `GALLERY_NAME_LEN` | `64` | Size of each speaker-name slot in bytes, including the terminating NUL; longer names are truncated to `GALLERY_NAME_LEN - 1` characters. |
| `GALLERY_MAGIC` | `0x474C5279u` | Magic number at the start of a serialised gallery image. |
| `GALLERY_DEFAULT_THRESHOLD` | `0.42f` | Default cosine-similarity decision threshold for [`gallery_init()`](#gallery_init), for galleries whose enrollment and identification embeddings both come from [`speaker_embed()`](#speaker_embed). |

## diarize.h { #diarize-h }

`#include "diarize.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/ai/src/inst/include/audio/diarize.h)）

Speaker diarization: online clustering of speaker embeddings.

Answers "which segments were spoken by the same person" without any prior enrollment. Each segment's embedding is compared with the centroids of the clusters seen so far; it joins the closest cluster when the cosine similarity reaches the threshold, otherwise it starts a new cluster. The same returned index therefore means the same speaker.

Typical sequence:

1. [`diarize_init()`](#diarize_init) once per session.
1. For each speech segment: [`speaker_embed()`](#speaker_embed) (see [`speaker_embed.h`](#speaker_embed-h)), then [`diarize_update()`](#diarize_update) with the resulting embedding.

The state has a fixed size and the module never allocates memory. It is independent of the feature extraction and the NPU: it only operates on L2-normalised embeddings of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats.

### diarize_init { #diarize_init }

```c
void diarize_init(DiarizeState *s);
```

Reset the state to zero clusters.

Call once before the first [`diarize_update()`](#diarize_update) of a session.

| 參數 | 說明 |
|---|---|
| `s` | State to clear. Must not be NULL. |

### diarize_update { #diarize_update }

```c
int diarize_update(DiarizeState *s, const float emb[EMBEDDING_DIM], float threshold);
```

Assign one segment embedding to a speaker cluster.

Finds the cluster whose centroid has the highest cosine similarity (dot product of unit vectors) with `emb`. If that similarity is greater than or equal to `threshold`, the embedding is merged into the cluster: the centroid becomes the renormalised running mean and the cluster count is incremented. Otherwise a new cluster is created with `emb` as its centroid.

| 參數 | 說明 |
|---|---|
| `s` | State initialised with [`diarize_init()`](#diarize_init). |
| `emb` | L2-normalised embedding of [`EMBEDDING_DIM`](#embedding_dim-h-macros) floats, as produced by [`speaker_embed()`](#speaker_embed). |
| `threshold` | Cosine-similarity merge threshold, typically [`DIARIZE_DEFAULT_THRESHOLD`](#diarize-h-macros). |

**回傳值**：0-based cluster index (a new speaker gets the next free index), or -1 if a new cluster is needed but all [`DIARIZE_MAX_CLUSTERS`](#diarize-h-macros) are in use.

### DiarizeState { #DiarizeState }

Diarization state: one centroid per speaker found so far.

About 33 KB (`DIARIZE_MAX_CLUSTERS * EMBEDDING_DIM` floats plus counters), so place it in static or heap memory rather than on a task stack.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `centroids` | `float[DIARIZE_MAX_CLUSTERS][EMBEDDING_DIM]` | Cluster centroids, each an L2-normalised running mean of the embeddings assigned to that cluster. Only the first `n_clusters` rows are valid. |
| `counts` | `int[DIARIZE_MAX_CLUSTERS]` | Number of segments merged into each cluster. |
| `n_clusters` | `int` | Number of clusters (speakers) in use. |

### 巨集 { #diarize-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `DIARIZE_MAX_CLUSTERS` | `32` | Maximum number of distinct speakers (clusters) one [`DiarizeState`](#DiarizeState) can hold. |
| `DIARIZE_DEFAULT_THRESHOLD` | `0.55f` | Default cosine-similarity merge threshold for [`diarize_update()`](#diarize_update). A higher value splits speakers more readily and yields more clusters. |
