---
title: 相機與影像
description: DVP 相機介面、ISP，以及硬體 MJPEG 編碼與解碼。
generated: tools/gen_api.py
migrate_from: []
---

# 相機與影像

DVP 相機介面、ISP，以及硬體 MJPEG 編碼與解碼。說明取自標頭檔註解（英文）。

| 標頭 | 函式 | 說明 |
|---|---|---|
| [`hal_cam.h`](#hal_cam-h) | 4 | Camera capture driver without the ISP: DVP or SPI camera input written to memory, with output crop, frame-rate control and ping-pong buffers. |
| [`hal_isp.h`](#hal_isp-h) | 9 | Image signal processor (ISP) driver: camera or memory input, global crop, two scaler output channels plus an extended channel, frame-rate control, digital zoom and ping-pong output buffers. |
| [`hal_mjpeg.h`](#hal_mjpeg-h) | 17 | Hardware JPEG encoder driver: encode YUV 4:2:2, YUV 4:2:0 or grey-scale frames to baseline JPEG in software-triggered or hardware auto mode. |
| [`hal_mjdec.h`](#hal_mjdec-h) | 6 | Hardware JPEG decoder driver: decode a baseline JPEG into semi-planar YUV or grey-scale frames. |

## hal_cam.h { #hal_cam-h }

`#include "hal_cam.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_cam.h)）

Camera capture driver without the ISP: DVP or SPI camera input written to memory, with output crop, frame-rate control and ping-pong buffers.

The driver feeds the camera input (DVP_AS or SPI2DVP) directly to the DVP-to-AXI writers, without the image signal processor. Use [`hal_isp.h`](#hal_isp-h) instead when scaling, colour conversion or several output channels are needed.

Typical sequence: configure the sensor, fill a [`cam_hal_cfg_t`](#cam_hal_cfg_t), [`cam_init()`](#cam_init), then [`cam_start()`](#cam_start). Each written frame is reported through `cam_hal_cfg_t::out_callback` from the capture interrupt. [`cam_deinit()`](#cam_deinit) removes the callback.

### cam_init { #cam_init }

```c
int cam_init(cam_hal_cfg_t *cam_hal_cfg);
```

Initialize camera capture.

Configures the input path and the DVP-to-AXI writers and installs the capture interrupt. Capture starts with [`cam_start()`](#cam_start).

| 參數 | 說明 |
|---|---|
| `cam_hal_cfg` | Configuration. `cam_hal_out_t::pp_num` is clamped in place to 1 to `CAM_MAX_BUFFER_NUM`. |

**回傳值**：Always 0. An invalid crop window (reported on the console) is replaced by no cropping, and an invalid frame-rate setting by the full frame rate.

### cam_start { #cam_start }

```c
int cam_start(void);
```

Enable the configured input source so that frames are received.

**回傳值**：Always 0.

### cam_deinit { #cam_deinit }

```c
int cam_deinit(void);
```

Disable the capture interrupt and remove the frame callback.

The input source and the writers are not disabled.

**回傳值**：Always 0.

### cam_fps_cfg { #cam_fps_cfg }

```c
int cam_fps_cfg(cam_hal_frame_rate_t frc);
```

Change the output frame rate at run time.

| 參數 | 說明 |
|---|---|
| `frc` | Frame-rate setting; `dst_fps = 0` drops every frame. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Applied. |
| `1` | Invalid setting (`src_fps` is 0 or `dst_fps` exceeds `src_fps`); the current rate is kept. |

### cam_hal_src_e { #cam_hal_src_e }

Camera input source.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_SRC_SPI2DVP` | `0` | SPI camera through the SPI-to-DVP bridge. |
| `CAM_HAL_SRC_DVP_AS` | `1` | Parallel DVP camera. |

### cam_hal_out_format_e { #cam_hal_out_format_e }

Output format.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_OUT_FMT_YUYV` |  | YUYV interleaved, one plane. |
| `CAM_HAL_OUT_FMT_YUV422SP` |  | YUV 4:2:2 semi-planar: the Y plane at the output address, followed by the interleaved UV plane. |
| `CAM_HAL_OUT_FMT_Y_ONLY` |  | Y (luminance) only. |

### 匿名列舉 { #hal_cam-h-enum }

Events reported in `cam_out_frame_info_t::event`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_INT_NORMAL` |  | A frame has been written. |
| `CAM_HAL_INT_FIFO_OVERWRITE` |  | FIFO overwrite; the writer is restarted. |
| `CAM_HAL_INT_VSYNC_CNT_ERROR` |  | The number of valid lines per frame did not match the input height. |
| `CAM_HAL_INT_HSYNC_CNT_ERROR` |  | The number of valid pixels per line did not match the input width. |
| `CAM_HAL_INT_ALL` |  | Number of event codes. |

### cam_hal_spi2dvp_data_order_e { #cam_hal_spi2dvp_data_order_e }

SPI2DVP data order.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_SPI2DVP_ORDER_UV_FIRST` |  | The first input byte is a chroma (UV) byte. |
| `CAM_HAL_SPI2DVP_ORDER_Y_FIRST` |  | The first input byte is a luma (Y) byte. |

### cam_hal_spi2dvp_data_format_e { #cam_hal_spi2dvp_data_format_e }

SPI2DVP input format.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_SPI2DVP_FORMAT_YUV422` |  | YUV 4:2:2 interleaved input. |
| `CAM_HAL_SPI2DVP_FORMAT_Y_ONLY` |  | Y-only input. |

### cam_hal_spi2dvp_mode_e { #cam_hal_spi2dvp_mode_e }

SPI2DVP SPI mode (clock phase and polarity).

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_SPI2DVP_MODE_0` |  | SPI mode 0: phase 0, polarity 0. |
| `CAM_HAL_SPI2DVP_MODE_1` |  | SPI mode 1: phase 1, polarity 0. |
| `CAM_HAL_SPI2DVP_MODE_2` |  | SPI mode 2: phase 0, polarity 1. |
| `CAM_HAL_SPI2DVP_MODE_3` |  | SPI mode 3: phase 1, polarity 1. |

### cam_hal_spi2dvp_data_endian_e { #cam_hal_spi2dvp_data_endian_e }

SPI2DVP bit order.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_SPI2DVP_ENDIAN_LSB` |  | LSB first. |
| `CAM_HAL_SPI2DVP_ENDIAN_MSB` |  | MSB first. |

### cam_hal_dvp_active_type_e { #cam_hal_dvp_active_type_e }

DVP HSYNC/VSYNC active level.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_DVP_ACTIVE_HIGH` |  | Active high. |
| `CAM_HAL_DVP_ACTIVE_LOW` |  | Active low. |

### cam_hal_dvp_data_byte_t { #cam_hal_dvp_data_byte_t }

DVP input byte order.

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_HAL_DATA_BYTE_LOWER` |  | The first byte is the lower byte. |
| `CAM_HAL_DATA_BYTE_HIGHER` |  | The first byte is the higher byte. |

### cam_hal_spi2dvp_input_t { #cam_hal_spi2dvp_input_t }

SPI2DVP input configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `order` | `cam_hal_spi2dvp_data_order_e` | Data order: Y first or UV first. |
| `format` | `cam_hal_spi2dvp_data_format_e` | Input format: YUYV or Y only. |
| `mode` | `cam_hal_spi2dvp_mode_e` | SPI mode (clock phase and polarity). |
| `endian` | `cam_hal_spi2dvp_data_endian_e` | Bit order: LSB or MSB first. |

### cam_hal_dvp_input_t { #cam_hal_dvp_input_t }

DVP input configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `hsync` | `cam_hal_dvp_active_type_e` | HSYNC active level. |
| `vsync` | `cam_hal_dvp_active_type_e` | VSYNC active level. |
| `order` | `cam_hal_dvp_data_byte_t` | Byte order: lower or higher byte first. |
| `pclk` | `uint32_t` | Sensor pixel clock in Hz. |
| `totalHPixels` | `uint16_t` | Sensor line length including horizontal blanking, in pixels. |

### cam_hal_src_cfg_t { #cam_hal_src_cfg_t }

Source-specific input configuration; the member is selected by `cam_hal_cfg_t::cam_src`.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `spi2dvp_input` | `cam_hal_spi2dvp_input_t` | Used with `CAM_HAL_SRC_SPI2DVP`. |
| `dvp_input` | `cam_hal_dvp_input_t` | Used with `CAM_HAL_SRC_DVP_AS`. |

### cam_hal_size_t { #cam_hal_size_t }

Image size.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `width` | `uint16_t` | Width in pixels. |
| `height` | `uint16_t` | Height in lines. |

### cam_hal_crop_t { #cam_hal_crop_t }

Crop window.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `start_x` | `uint16_t` | Left edge in pixels; must be even. |
| `start_y` | `uint16_t` | Top edge in lines. |
| `width` | `uint16_t` | Width in pixels; must be even. |
| `height` | `uint16_t` | Height in lines. |

### cam_hal_frame_rate_t { #cam_hal_frame_rate_t }

Output frame-rate control.

Of every `src_fps` input frames, `dst_fps` are written; for example 30/15 writes every other frame.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `src_fps` | `uint8_t` | Input frame rate; must be at least 1. |
| `dst_fps` | `uint8_t` | Output frame rate, at most `src_fps`; 0 drops every frame. |

### cam_out_frame_info_t { #cam_out_frame_info_t }

Frame information passed to `cam_hal_cfg_t::out_callback`.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `event` | `uint32_t` | Event, one of the `CAM_HAL_INT_*` values. |
| `out_addr` | `uint32_t` | Address of the frame just written. |
| `out_size` | `uint32_t` | Size of the frame in bytes (Y and UV planes together for `CAM_HAL_OUT_FMT_YUV422SP`). |

### cam_hal_out_t { #cam_hal_out_t }

Output configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `format` | `cam_hal_out_format_e` | Output format. |
| `ring_line` | `uint16_t` | Lines of the output line ring, or 0 to write whole frames. A ring is typically read by the JPEG encoder; when non-zero, `pp_num` is forced to 1. |
| `pp_num` | `uint8_t` | Number of ping-pong buffers, 1 to `CAM_MAX_BUFFER_NUM`; 0 is treated as 1. |
| `addr` | `uint32_t[CAM_MAX_BUFFER_NUM]` | Output buffer addresses; writing starts at addr[0]. |
| `fr_ctrl` | `cam_hal_frame_rate_t` | Frame-rate control; an invalid setting writes every frame. |
| `out_crop` | `cam_hal_crop_t` | Output crop within the input image; an invalid window disables cropping. |

### cam_hal_cfg_t { #cam_hal_cfg_t }

Complete camera configuration for [`cam_init()`](#cam_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `cam_src` | `cam_hal_src_e` | Input source. |
| `in_size` | `cam_hal_size_t` | Input image size. |
| `src_cfg` | `cam_hal_src_cfg_t` | Source-specific input configuration. |
| `output_cfg` | `cam_hal_out_t` | Output configuration. |
| `out_callback` | `void(*)(cam_out_frame_info_t info)` | Frame callback, called from the capture interrupt; may be NULL. |

### 巨集 { #hal_cam-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `CAM_MAX_BUFFER_NUM` | `(2)` | Maximum number of ping-pong output buffers (see `cam_hal_out_t::pp_num`). |

## hal_isp.h { #hal_isp-h }

`#include "hal_isp.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_isp.h)）

Image signal processor (ISP) driver: camera or memory input, global crop, two scaler output channels plus an extended channel, frame-rate control, digital zoom and ping-pong output buffers.

The ISP takes its input from a DVP camera, an SPI camera or a test source that reads frames from memory. Output channel 0 writes YUV or Y-only images, output channel 1 writes RGB or ARGB images, and the extended channel taps the image at a selectable point of the pipeline.

Typical sequence: configure the sensor, fill an [`isp_hal_cfg_t`](#isp_hal_cfg_t), [`isp_init()`](#isp_init), then [`isp_start()`](#isp_start). Each written frame is reported through `isp_hal_cfg_t::out_callback` from the capture interrupt. Zoom, frame rate and channel settings can be changed while running. [`isp_deinit()`](#isp_deinit) removes the callbacks and disables the input.

### isp_init { #isp_init }

```c
int isp_init(isp_hal_cfg_t *isp_hal_cfg);
```

Initialize the ISP.

Configures the input path, the global crop, the YUV adjustment stage and every enabled output channel, and installs the capture interrupts. Processing starts with [`isp_start()`](#isp_start). If the extended channel cannot be used because of the channel 0 format, it is skipped with a console message.

| 參數 | 說明 |
|---|---|
| `isp_hal_cfg` | Configuration. The `pp_num` of each channel is clamped in place to 1 to `ISP_MAX_BUFFER_NUM`, and an invalid global crop is corrected in place. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `1` | The input width exceeds `ISP_MAX_IN_WIDTH`. |

### isp_start { #isp_start }

```c
int isp_start(void);
```

Enable the configured input source so that frames are processed.

**回傳值**：Always 0.

### isp_deinit { #isp_deinit }

```c
int isp_deinit(void);
```

Remove the channel callbacks and interrupts and disable the input source.

**回傳值**：Always 0.

### isp_tsrc_trigger { #isp_tsrc_trigger }

```c
int isp_tsrc_trigger(void);
```

Make the test source send one frame.

Use with `ISP_HAL_SRC_TSRC` when `isp_hal_tsrc_input_t::tsrc_conti` is false.

**回傳值**：Always 0.

### isp_zoom_cfg { #isp_zoom_cfg }

```c
int isp_zoom_cfg(uint8_t channel, isp_hal_crop_t scaler_in);
```

Change the digital zoom (scaler input window) of a channel at run time.

The new window is applied when the ISP next reaches the middle line of a frame.

| 參數 | 說明 |
|---|---|
| `channel` | `ISP_CHANNEL_0` or `ISP_CHANNEL_1`. |
| `scaler_in` | Scaler input window; `start_x` and `width` must be even and the window must lie inside the scaler input image. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Accepted. |
| `1` | Invalid channel or window. |
| `2` | The channel is not enabled. |

### isp_fps_cfg { #isp_fps_cfg }

```c
int isp_fps_cfg(uint8_t channel, isp_hal_frame_rate_t frc);
```

Change the output frame rate of a channel at run time.

| 參數 | 說明 |
|---|---|
| `channel` | `ISP_CHANNEL_0`, `ISP_CHANNEL_1` or `ISP_CHANNEL_EXT`. |
| `frc` | Frame-rate setting; `dst_fps = 0` drops every frame. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Applied. |
| `1` | Invalid channel, or invalid setting (`src_fps` is 0 or `dst_fps` exceeds `src_fps`). |
| `2` | The channel is not enabled. |

### isp_update_chn0_cfg { #isp_update_chn0_cfg }

```c
int isp_update_chn0_cfg(isp_hal_out_chnl_0_t chn0_cfg);
```

Change the configuration of output channel 0 at run time.

Reprograms the channel's scaler and writers and enables its interrupt if needed. Call it shortly after the start of a frame so that the change does not land in the middle of a frame. With `enable` set to 0 the channel is only marked as disabled; its hardware is not stopped.

| 參數 | 說明 |
|---|---|
| `chn0_cfg` | New channel 0 configuration. |

**回傳值**：Always 0.

### isp_update_chn1_cfg { #isp_update_chn1_cfg }

```c
int isp_update_chn1_cfg(isp_hal_out_chnl_1_t chn1_cfg);
```

Change the configuration of output channel 1 at run time.

Reprograms the channel's scaler and writer and enables its interrupt if needed. Call it shortly after the start of a frame so that the change does not land in the middle of a frame. With `enable` set to 0 the channel is only marked as disabled; its hardware is not stopped.

| 參數 | 說明 |
|---|---|
| `chn1_cfg` | New channel 1 configuration. |

**回傳值**：Always 0.

### isp_get_input_resolution { #isp_get_input_resolution }

```c
void isp_get_input_resolution(uint16_t *width, uint16_t *height);
```

Get the input image size passed to the last successful [`isp_init()`](#isp_init).

| 參數 | 說明 |
|---|---|
| `width` | Receives the input width in pixels. |
| `height` | Receives the input height in lines. |

### 匿名列舉 { #hal_isp-h-enum }

ISP output channel index.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_CHANNEL_0` |  | Scaler output channel 0 (YUV and Y-only formats). |
| `ISP_CHANNEL_1` |  | Scaler output channel 1 (RGB and ARGB formats). |
| `ISP_CHANNEL_EXT` |  | Extended output channel. |
| `ISP_CHANNEL_MAX_NUM` |  | Number of output channels. |

### isp_hal_src_e { #isp_hal_src_e }

ISP input source.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_SRC_SPI2DVP` | `0` | SPI camera through the SPI-to-DVP bridge. |
| `ISP_HAL_SRC_DVP_AS` | `1` | Parallel DVP camera. |
| `ISP_HAL_SRC_TSRC` | `9` | Test source: frames read from memory. |

### isp_hal_out_format0_e { #isp_hal_out_format0_e }

Output formats of channel 0.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_OUT_FMT0_YUYV` |  | YUYV interleaved, one plane. |
| `ISP_HAL_OUT_FMT0_YUV422SP` |  | YUV 4:2:2 semi-planar (Y plane, then UV plane). |
| `ISP_HAL_OUT_FMT0_NV12` |  | YUV 4:2:0 semi-planar (Y plane, then UV plane). |
| `ISP_HAL_OUT_FMT0_Y_ONLY` |  | Y (luminance) only. |

### isp_hal_out_format1_e { #isp_hal_out_format1_e }

Output formats of channel 1.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_OUT_FMT1_RGB` |  | RGB. |
| `ISP_HAL_OUT_FMT1_ARGB` |  | ARGB. |

### isp_hal_ext_src_e { #isp_hal_ext_src_e }

Tap point of the extended channel.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_EXT_SRC_RAW` |  | The raw ISP input image. |
| `ISP_HAL_EXT_SRC_ISP_OUT` |  | The ISP output, before the scalers. |
| `ISP_HAL_EXT_SRC_OUT_CHN0_IN` |  | Scaler output channel 0; channel 0 must be enabled. |
| `ISP_HAL_EXT_SRC_OUT_CHN1_IN` |  | Scaler output channel 1; channel 1 must be enabled. |

### isp_hal_out_format_ext_e { #isp_hal_out_format_ext_e }

Output formats of the extended channel.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_OUT_FMT_EXT_YUYV` |  | YUYV; available for every tap point. |
| `ISP_HAL_OUT_FMT_EXT_Y_ONLY` |  | Y only; available for every tap point. |
| `ISP_HAL_OUT_FMT_EXT_RGB` |  | RGB; only with `ISP_HAL_EXT_SRC_OUT_CHN1_IN`. |
| `ISP_HAL_OUT_FMT_EXT_ARGB` |  | ARGB; only with `ISP_HAL_EXT_SRC_OUT_CHN1_IN`. |

### 匿名列舉 { #hal_isp-h-enum-2 }

Events reported in `isp_out_frame_info_t::event`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_INT_NORMAL` |  | A frame has been written. |
| `ISP_HAL_INT_FIFO_OVERWRITE` |  | FIFO overwrite. |
| `ISP_HAL_INT_VSYNC_CNT_ERROR` |  | The number of valid lines per frame did not match the expected height. |
| `ISP_HAL_INT_HSYNC_CNT_ERROR` |  | The number of valid pixels per line did not match the expected width. |
| `ISP_HAL_INT_ALL` |  | Number of event codes. |

### isp_hal_spi2dvp_sel_e { #isp_hal_spi2dvp_sel_e }

SPI port used by the SPI-to-DVP bridge.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_SPI2DVP_SEL_SPI_0` |  | SPI port 0. |
| `ISP_HAL_SPI2DVP_SEL_SPI_1` |  | SPI port 1. |

### isp_hal_spi2dvp_data_order_e { #isp_hal_spi2dvp_data_order_e }

SPI2DVP data order.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_SPI2DVP_ORDER_UV_FIRST` |  | The first input byte is a chroma (UV) byte. |
| `ISP_HAL_SPI2DVP_ORDER_Y_FIRST` |  | The first input byte is a luma (Y) byte. |

### isp_hal_spi2dvp_data_format_e { #isp_hal_spi2dvp_data_format_e }

SPI2DVP input format.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_SPI2DVP_FORMAT_YUV422` |  | YUV 4:2:2 interleaved input. |
| `ISP_HAL_SPI2DVP_FORMAT_Y_ONLY` |  | Y-only input. |

### isp_hal_spi2dvp_mode_e { #isp_hal_spi2dvp_mode_e }

SPI2DVP SPI mode (clock phase and polarity).

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_SPI2DVP_MODE_0` |  | SPI mode 0: phase 0, polarity 0. |
| `ISP_HAL_SPI2DVP_MODE_1` |  | SPI mode 1: phase 1, polarity 0. |
| `ISP_HAL_SPI2DVP_MODE_2` |  | SPI mode 2: phase 0, polarity 1. |
| `ISP_HAL_SPI2DVP_MODE_3` |  | SPI mode 3: phase 1, polarity 1. |

### isp_hal_spi2dvp_data_endian_e { #isp_hal_spi2dvp_data_endian_e }

SPI2DVP bit order.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_SPI2DVP_ENDIAN_LSB` |  | LSB first. |
| `ISP_HAL_SPI2DVP_ENDIAN_MSB` |  | MSB first. |

### isp_hal_dvp_active_type_e { #isp_hal_dvp_active_type_e }

DVP HSYNC/VSYNC active level.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_DVP_ACTIVE_HIGH` |  | Active high. |
| `ISP_HAL_DVP_ACTIVE_LOW` |  | Active low. |

### isp_hal_dvp_data_byte_t { #isp_hal_dvp_data_byte_t }

DVP input byte order.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_HAL_DATA_BYTE_LOWER` |  | The first byte is the lower byte. |
| `ISP_HAL_DATA_BYTE_HIGHER` |  | The first byte is the higher byte. |

### isp_hal_spi2dvp_input_t { #isp_hal_spi2dvp_input_t }

SPI2DVP input configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `order` | `isp_hal_spi2dvp_data_order_e` | Data order: Y first or UV first. |
| `format` | `isp_hal_spi2dvp_data_format_e` | Input format: YUYV or Y only. |
| `mode` | `isp_hal_spi2dvp_mode_e` | SPI mode (clock phase and polarity). |
| `endian` | `isp_hal_spi2dvp_data_endian_e` | Bit order: LSB or MSB first. |
| `spi_sel` | `isp_hal_spi2dvp_sel_e` | SPI port: SPI 0 or SPI 1. |

### isp_hal_dvp_input_t { #isp_hal_dvp_input_t }

DVP input configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `hsync` | `isp_hal_dvp_active_type_e` | HSYNC active level. |
| `vsync` | `isp_hal_dvp_active_type_e` | VSYNC active level. |
| `order` | `isp_hal_dvp_data_byte_t` | Byte order: lower or higher byte first. |
| `pclk` | `uint32_t` | Sensor pixel clock in Hz. |
| `totalHPixels` | `uint16_t` | Sensor line length including horizontal blanking, in pixels. |

### isp_hal_tsrc_input_t { #isp_hal_tsrc_input_t }

Test-source (memory input) configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `input_addr` | `uint32_t` | Address of the input frame (YUV 4:2:2, 16 bits per pixel). |
| `tsrc_conti` | `bool` | true: read frames continuously; false: read one frame per [`isp_tsrc_trigger()`](#isp_tsrc_trigger) |

### isp_hal_src_cfg_t { #isp_hal_src_cfg_t }

Source-specific input configuration; the member is selected by `isp_hal_cfg_t::isp_src`.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `spi2dvp_input` | `isp_hal_spi2dvp_input_t` | Used with `ISP_HAL_SRC_SPI2DVP`. |
| `dvp_input` | `isp_hal_dvp_input_t` | Used with `ISP_HAL_SRC_DVP_AS`. |
| `tsrc_input` | `isp_hal_tsrc_input_t` | Used with `ISP_HAL_SRC_TSRC`. |

### isp_hal_size_t { #isp_hal_size_t }

Image size.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `width` | `uint16_t` | Width in pixels. |
| `height` | `uint16_t` | Height in lines. |

### isp_hal_crop_t { #isp_hal_crop_t }

Crop window.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `start_x` | `uint16_t` | Left edge in pixels; must be even. |
| `start_y` | `uint16_t` | Top edge in lines. |
| `width` | `uint16_t` | Width in pixels; must be even. |
| `height` | `uint16_t` | Height in lines. |

### isp_hal_scaler_cfg_t { #isp_hal_scaler_cfg_t }

Scaler input and output of an output channel.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `in` | `isp_hal_crop_t` | Scaler input window; a window smaller than the image gives a digital zoom. |
| `out` | `isp_hal_size_t` | Scaler output size, at most `ISP_MAX_OUT_WIDTH` x `ISP_MAX_OUT_HEIGHT`. |

### isp_hal_frame_rate_t { #isp_hal_frame_rate_t }

Output-channel frame-rate control.

Of every `src_fps` input frames, `dst_fps` are written; for example 30/15 writes every other frame.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `src_fps` | `uint8_t` | Input frame rate; must be at least 1. |
| `dst_fps` | `uint8_t` | Output frame rate, at most `src_fps`; 0 drops every frame. |

### isp_out_frame_info_t { #isp_out_frame_info_t }

Frame information passed to `isp_hal_cfg_t::out_callback`.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `event` | `uint32_t` | Event, one of the `ISP_HAL_INT_*` values. |
| `out_port` | `uint32_t` | Output channel: `ISP_CHANNEL_0`, `ISP_CHANNEL_1` or `ISP_CHANNEL_EXT`. |
| `out_addr` | `uint32_t` | Address of the frame just written. |
| `out_size` | `uint32_t` | Size of the frame in bytes. |

### isp_hal_out_chn_comm_t { #isp_hal_out_chn_comm_t }

Settings common to all output channels.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `pp_num` | `uint8_t` | Number of ping-pong buffers, 1 to `ISP_MAX_BUFFER_NUM`; 0 is treated as 1. |
| `addr` | `uint32_t[ISP_MAX_BUFFER_NUM]` | Output buffer addresses; writing starts at addr[0]. |
| `fr_ctrl` | `isp_hal_frame_rate_t` | Frame-rate control. |
| `out_crop` | `isp_hal_crop_t` | Final crop of the channel output. |

### isp_hal_out_chnl_0_t { #isp_hal_out_chnl_0_t }

Output channel 0 configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `enable` | `uint8_t` | Non-zero enables the channel. |
| `scaler_cfg` | `isp_hal_scaler_cfg_t` | Scaler input and output. |
| `format` | `isp_hal_out_format0_e` | Output format. |
| `ring_line` | `uint16_t` | Lines of the output line ring, or 0 to write whole frames. A ring is typically read by the JPEG encoder; when non-zero, `pp_num` is forced to 1. |
| `chn_common` | `isp_hal_out_chn_comm_t` | Common output settings. |

### isp_hal_out_chnl_1_t { #isp_hal_out_chnl_1_t }

Output channel 1 configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `enable` | `uint8_t` | Non-zero enables the channel. |
| `scaler_cfg` | `isp_hal_scaler_cfg_t` | Scaler input and output. |
| `format` | `isp_hal_out_format1_e` | Output format. |
| `chn_common` | `isp_hal_out_chn_comm_t` | Common output settings. |

### isp_hal_out_chnl_ext_t { #isp_hal_out_chnl_ext_t }

Extended output channel configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `enable` | `uint8_t` | Non-zero enables the channel. |
| `ext_src` | `isp_hal_ext_src_e` | Tap point. |
| `format` | `isp_hal_out_format_ext_e` | Output format. |
| `chn_common` | `isp_hal_out_chn_comm_t` | Common output settings. |

### isp_hal_cfg_t { #isp_hal_cfg_t }

Complete ISP configuration for [`isp_init()`](#isp_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `isp_src` | `isp_hal_src_e` | Input source. |
| `in_size` | `isp_hal_size_t` | Input image size; the width must not exceed `ISP_MAX_IN_WIDTH`. |
| `src_cfg` | `isp_hal_src_cfg_t` | Source-specific input configuration. |
| `glb_crop` | `isp_hal_crop_t` | Global crop applied to the ISP output before the scalers. |
| `yuv_adj_en` | `uint8_t` | Non-zero enables the YUV adjustment stage. |
| `out_ch_0` | `isp_hal_out_chnl_0_t` | Output channel 0; its buffers may be in OCRAM or PSRAM. |
| `out_ch_1` | `isp_hal_out_chnl_1_t` | Output channel 1; its buffers must be in PSRAM. |
| `out_ch_ext` | `isp_hal_out_chnl_ext_t` | Extended output channel; its buffers may be in OCRAM or PSRAM. Not available when channel 0 is enabled with the YUV422SP or NV12 format. |
| `out_callback` | `void(*)(isp_out_frame_info_t info)` | Frame callback for all channels, called from the capture interrupt; may be NULL. |

### 巨集 { #hal_isp-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `ISP_MAX_IN_WIDTH` | `(1280)` | Maximum input width in pixels; [`isp_init()`](#isp_init) rejects wider inputs. |
| `ISP_MAX_IN_HEIGHT` | `(720)` | Maximum input height in lines. |
| `ISP_MAX_OUT_WIDTH` | `(1920)` | Maximum scaler output width in pixels. |
| `ISP_MAX_OUT_HEIGHT` | `(1080)` | Maximum scaler output height in lines. |
| `ISP_MAX_BUFFER_NUM` | `(2)` | Maximum number of ping-pong output buffers per channel (see `isp_hal_out_chn_comm_t::pp_num`). |

## hal_mjpeg.h { #hal_mjpeg-h }

`#include "hal_mjpeg.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_mjpeg.h)）

Hardware JPEG encoder driver: encode YUV 4:2:2, YUV 4:2:0 or grey-scale frames to baseline JPEG in software-triggered or hardware auto mode.

The encoder shares the JPEG hardware block with the decoder ([`hal_mjdec.h`](#hal_mjdec-h)); only one of them can be initialized at a time. Encoded frames are kept in a queue: [`mjpeg_get_one_frame()`](#mjpeg_get_one_frame) returns the oldest one and [`mjpeg_drop_one_frame()`](#mjpeg_drop_one_frame) releases it.

Software-triggered sequence: [`mjpeg_init()`](#mjpeg_init); build a header with [`mjpeg_headerCreate()`](#mjpeg_headerCreate) and load it with [`mjpeg_fill_header_tail()`](#mjpeg_fill_header_tail); for each frame, clean the data cache over the input, set the input planes with [`mjpeg_set_input_addr()`](#mjpeg_set_input_addr), then for the first frame call `mjpeg_set_mode(1, 1, 1)` and `mjpeg_start(1)`, and for later frames [`mjpeg_sw_run_next()`](#mjpeg_sw_run_next); wait for `MJENC_HAL_INT_NORMAL` in the callback, fetch the frame, invalidate the data cache over it, use it and drop it. Finish with [`mjpeg_stop()`](#mjpeg_stop) and [`mjpeg_deinit()`](#mjpeg_deinit).

In hardware auto mode (`mjpeg_start(0)`) the encoder reads the frames that the camera or ISP writes into the input buffer (a full frame or a ring of `mjpeg_hal_cfg_t::rows` lines) and encodes them continuously.

### mjpeg_init { #mjpeg_init }

```c
int mjpeg_init(struct mjpeg_hal_cfg_t *mjpeg_hal_cfg);
```

Initialize the encoder.

Claims the JPEG hardware for encoding, programs the format, image size, buffers and quantization tables, and installs and enables the encoder interrupt. The frame-done and error events stay masked until [`mjpeg_start()`](#mjpeg_start); the swap event is enabled when swap mode is selected.

| 參數 | 說明 |
|---|---|
| `mjpeg_hal_cfg` | Encoder configuration. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | The JPEG hardware is initialized for decoding. |

### mjpeg_deinit { #mjpeg_deinit }

```c
int mjpeg_deinit(void);
```

Release the JPEG hardware from encoding.

| 回傳碼 | 說明 |
|---|---|
| `0` | Released (or not initialized). |
| `-1` | The JPEG hardware is initialized for decoding. |

### mjpeg_start { #mjpeg_start }

```c
void mjpeg_start(int is_sw_mode);
```

Start encoding.

Enables the frame-done and error events, then either triggers a software-mode run as configured by [`mjpeg_set_mode()`](#mjpeg_set_mode) or starts hardware auto mode.

| 參數 | 說明 |
|---|---|
| `is_sw_mode` | Non-zero: software-triggered mode. 0: hardware auto mode. |

### mjpeg_stop { #mjpeg_stop }

```c
void mjpeg_stop(void);
```

Disable the encoder.

### mjpeg_get_one_frame { #mjpeg_get_one_frame }

```c
uint8_t mjpeg_get_one_frame(uint32_t *addr, uint32_t *len);
```

Get the oldest encoded frame without removing it.

The frame (header included) stays valid until [`mjpeg_drop_one_frame()`](#mjpeg_drop_one_frame) is called. Invalidate the data cache over it before reading it.

| 參數 | 說明 |
|---|---|
| `addr` | Start address of the JPEG frame. |
| `len` | Frame length in bytes. |

| 回傳碼 | 說明 |
|---|---|
| `0` | A frame is available. |
| `1` | No frame is available. |

### mjpeg_drop_one_frame { #mjpeg_drop_one_frame }

```c
void mjpeg_drop_one_frame(void);
```

Release the oldest encoded frame so that its space can be reused.

### mjpeg_fill_header_tail { #mjpeg_fill_header_tail }

```c
void mjpeg_fill_header_tail(uint8_t *header, uint32_t header_len);
```

Load the JPEG header that the encoder writes in front of each frame.

| 參數 | 說明 |
|---|---|
| `header` | Header bytes, for example built by [`mjpeg_headerCreate()`](#mjpeg_headerCreate). |
| `header_len` | Header length in bytes. |

### mjpeg_headerCreate { #mjpeg_headerCreate }

```c
uint32_t mjpeg_headerCreate(uint8_t type, uint8_t q, int width, int height, uint8_t *out);
```

Build a baseline JPEG header.

Writes the start-of-image marker, the luminance and chrominance quantization tables for quality `q`, the frame header, the standard Huffman tables and the start-of-scan header.

| 參數 | 說明 |
|---|---|
| `type` | Header type: `YUV_MODE_400`, `YUV_MODE_420` or `YUV_MODE_422`. |
| `q` | JPEG quality, 1 to 100; use the value of `mjpeg_hal_cfg_t::quality`. |
| `width` | Image width in pixels. |
| `height` | Image height in pixels. |
| `out` | Destination buffer, at least 605 bytes. |

**回傳值**：Header length in bytes: 605 for `YUV_MODE_420` and `YUV_MODE_422`, 595 for `YUV_MODE_400`.

### mjpeg_set_mode { #mjpeg_set_mode }

```c
void mjpeg_set_mode(int is_sw_mode, int is_frame_mode, int frm_cnt);
```

Configure software-triggered mode.

| 參數 | 說明 |
|---|---|
| `is_sw_mode` | Non-zero to configure software mode; 0 does nothing. |
| `is_frame_mode` | Non-zero: frame mode (whole frames per run). 0: kick mode (block rows per [`mjpeg_sw_kick()`](#mjpeg_sw_kick)). |
| `frm_cnt` | Number of frames encoded per run. |

### mjpeg_sw_run_next { #mjpeg_sw_run_next }

```c
void mjpeg_sw_run_next(void);
```

Trigger the next software-mode run.

### mjpeg_sw_run_abort { #mjpeg_sw_run_abort }

```c
void mjpeg_sw_run_abort(void);
```

Abort the current software-mode run.

### mjpeg_sw_kick_block { #mjpeg_sw_kick_block }

```c
void mjpeg_sw_kick_block(uint16_t kick_count);
```

Set the number of block rows encoded per kick in software kick mode.

| 參數 | 說明 |
|---|---|
| `kick_count` | Number of block rows per [`mjpeg_sw_kick()`](#mjpeg_sw_kick) (13-bit value). |

### mjpeg_sw_kick_stop { #mjpeg_sw_kick_stop }

```c
void mjpeg_sw_kick_stop(void);
```

Leave software kick mode.

### mjpeg_sw_kick { #mjpeg_sw_kick }

```c
void mjpeg_sw_kick(void);
```

Encode the next group of block rows in software kick mode.

### mjpeg_set_input_addr { #mjpeg_set_input_addr }

```c
void mjpeg_set_input_addr(int type, uint32_t addr);
```

Set an input plane address.

| 參數 | 說明 |
|---|---|
| `type` | `MJPEG_HAL_SET_ADDR_Y` or `MJPEG_HAL_SET_ADDR_UV`; other values are ignored. |
| `addr` | Plane address. |

### mjpeg_get_swap_occur_cnt { #mjpeg_get_swap_occur_cnt }

```c
uint32_t mjpeg_get_swap_occur_cnt(void);
```

Get the number of swap events in the current frame.

Counts `MJENC_HAL_INT_SWAP` events since [`mjpeg_init()`](#mjpeg_init), restarting from 0 when a swap event marks the end of a frame.

**回傳值**：Number of swap events.

### mjpeg_free_swap_memory { #mjpeg_free_swap_memory }

```c
void mjpeg_free_swap_memory(void);
```

In swap mode, mark the output buffer halves as consumed so that the encoder can reuse them.

### 匿名列舉 { #hal_mjpeg-h-enum }

Input formats for `mjpeg_hal_cfg_t::format`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `MJPEG_HAL_FORMAT_YUV422_YUYV` | `0` | YUV 4:2:2 interleaved, byte order Y0 U Y1 V. |
| `MJPEG_HAL_FORMAT_YUV422_YVYU` | `1` | YUV 4:2:2 interleaved, byte order Y0 V Y1 U. |
| `MJPEG_HAL_FORMAT_YUV422_UYVY` | `2` | YUV 4:2:2 interleaved, byte order U Y0 V Y1. |
| `MJPEG_HAL_FORMAT_YUV422_VYUY` | `3` | YUV 4:2:2 interleaved, byte order V Y0 U Y1. |
| `MJPEG_HAL_FORMAT_YUV422SP_NV16` | `4` | YUV 4:2:2 semi-planar, UV plane U first. |
| `MJPEG_HAL_FORMAT_YUV422SP_NV61` | `5` | YUV 4:2:2 semi-planar, UV plane V first. |
| `MJPEG_HAL_FORMAT_YUV420SP_NV12` | `6` | YUV 4:2:0 semi-planar, UV plane U first. |
| `MJPEG_HAL_FORMAT_YUV420SP_NV21` | `7` | YUV 4:2:0 semi-planar, UV plane V first. |
| `MJPEG_HAL_FORMAT_GRAY` | `8` | Grey scale (Y plane only). |

### 匿名列舉 { #hal_mjpeg-h-enum-2 }

Events passed to `mjpeg_hal_cfg_t::callback`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `MJENC_HAL_INT_NORMAL` | `0` | A frame has been encoded. |
| `MJENC_HAL_INT_IDLE` |  | The encoder entered idle. |
| `MJENC_HAL_INT_SWAP` |  | Swap mode: one half of the output buffer is full. |
| `MJENC_HAL_INT_ERR_CAM_OVERWRITE` |  | An input frame was overwritten before it was encoded. |
| `MJENC_HAL_INT_ERR_MEM_OVERWRITE` |  | The output buffer is full. |
| `MJENC_HAL_INT_ERR_FRAME_OVERWRITE` |  | The frame-information queue is full; the record of a new frame was lost. |

### 匿名列舉 { #hal_mjpeg-h-enum-3 }

Input plane selector for [`mjpeg_set_input_addr()`](#mjpeg_set_input_addr).

| 名稱 | 值 | 說明 |
|---|---|---|
| `MJPEG_HAL_SET_ADDR_Y` | `0` | Y plane, or the whole frame for interleaved and grey formats. |
| `MJPEG_HAL_SET_ADDR_UV` |  | UV plane of semi-planar formats. |

### mjpeg_hal_cfg_t { #mjpeg_hal_cfg_t }

Encoder configuration for [`mjpeg_init()`](#mjpeg_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `format` | `uint8_t` | Input format, one of the `MJPEG_HAL_FORMAT_*` values. |
| `quality` | `uint8_t` | JPEG quality, 1 to 100 (0 is treated as 1). Pass the same value to [`mjpeg_headerCreate()`](#mjpeg_headerCreate). |
| `rows` | `uint16_t` | Number of input lines held in the input buffer: the frame height for a full-frame buffer, or the ring height for a line ring. Use a multiple of 8 (16 for 4:2:0 formats). |
| `resolution_x` | `uint16_t` | Image width in pixels. |
| `resolution_y` | `uint16_t` | Image height in pixels. |
| `input_bufaddr0` | `uint32_t` | Address of the Y plane, or of the whole frame for interleaved and grey formats. |
| `input_bufaddr1` | `uint32_t` | Address of the UV plane (semi-planar formats). |
| `output_bufaddr` | `uint32_t` | Output (bitstream) buffer address, 4-byte aligned. |
| `output_bufsize` | `uint32_t` | Output buffer size in bytes; rounded down to a multiple of 128. |
| `input_yy_table` | `uint16_t *` | Not used; the driver uses its built-in luminance quantization table. |
| `input_uv_table` | `uint16_t *` | Not used; the driver uses its built-in chrominance quantization table. |
| `output_swap_mode_en` | `uint8_t` | 0: frame mode. 1: swap mode; the output buffer is split into two halves used as ping-pong buffers, with `MJENC_HAL_INT_SWAP` each time a half is full. |
| `hw_mode_swen_en` | `uint8_t` | Hardware auto mode: 1 starts encoding without waiting for the first frame-done of the input source. |
| `hw_mode_sshot_en` | `uint8_t` | Hardware auto mode: 1 encodes a single frame and does not restart the encoder after it. |
| `callback` | `void(*)(uint32_t event)` | Event callback, called from the JPEG encoder interrupt with an `MJENC_HAL_INT_*` value. Must not be NULL. |

### 巨集 { #hal_mjpeg-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `_MJPEG_SW_OUT_PING_PONG_MODE_` |  | Defined on IPRO7. In hardware auto mode without output swap mode, the driver splits the output buffer into two halves that it uses alternately, and stops and restarts the encoder after every frame. This avoids an encoder stall after 255 frames when the input is a line ring. [`mjpeg_get_one_frame()`](#mjpeg_get_one_frame) and [`mjpeg_drop_one_frame()`](#mjpeg_drop_one_frame) then operate on this two-entry queue. |
| `YUV_MODE_400` | `1` | Header type for [`mjpeg_headerCreate()`](#mjpeg_headerCreate): grey scale. |
| `YUV_MODE_420` | `2` | Header type for [`mjpeg_headerCreate()`](#mjpeg_headerCreate): YUV 4:2:0. |
| `YUV_MODE_422` | `3` | Header type for [`mjpeg_headerCreate()`](#mjpeg_headerCreate): YUV 4:2:2. |
| `MJPEG_DEFAULT_QUALITY` | `50` | Default JPEG quality (1 to 100). |

## hal_mjdec.h { #hal_mjdec-h }

`#include "hal_mjdec.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_mjdec.h)）

Hardware JPEG decoder driver: decode a baseline JPEG into semi-planar YUV or grey-scale frames.

The decoder shares the JPEG hardware block with the encoder ([`hal_mjpeg.h`](#hal_mjpeg-h)); only one of them can be initialized at a time. Typical sequence: [`mjdec_init()`](#mjdec_init), [`mjdec_set_callback()`](#mjdec_set_callback), clean the data cache over the JPEG data, then [`mjdec_start_decoder()`](#mjdec_start_decoder). Decoding runs in the background; the callback reports the decoded frame from the decoder interrupt, after which the decoder is disabled. Invalidate the data cache over the output planes before reading them, and call [`mjdec_deinit()`](#mjdec_deinit) to hand the hardware back.

### mjdec_init { #mjdec_init }

```c
int mjdec_init(mjdec_config_t *config);
```

Initialize the decoder.

Claims the JPEG hardware for decoding, parses the JPEG header when `mjdec_config_t::is_skip_header` is 1, programs the output format and buffers, and installs and enables the decoder interrupt.

| 參數 | 說明 |
|---|---|
| `config` | Decoder configuration. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | The JPEG hardware is initialized for encoding, the header could not be parsed, or its dimensions do not match `width` and `height`. |

### mjdec_deinit { #mjdec_deinit }

```c
int mjdec_deinit(void);
```

Release the JPEG hardware from decoding.

| 回傳碼 | 說明 |
|---|---|
| `0` | Released (or not initialized). |
| `-1` | The JPEG hardware is initialized for encoding. |

### mjdec_disable { #mjdec_disable }

```c
void mjdec_disable(void);
```

Disable the decoder.

### mjdec_start_decoder { #mjdec_start_decoder }

```c
int mjdec_start_decoder(uint8_t *jpeg_buf_addr);
```

Start decoding one JPEG frame.

Enables the decoder and queues the JPEG data; returns without waiting. Clean the data cache over the JPEG data first.

| 參數 | 說明 |
|---|---|
| `jpeg_buf_addr` | JPEG data; must be 8-byte aligned, otherwise it is not queued. |

**回傳值**：Always 0.

### mjdec_set_callback { #mjdec_set_callback }

```c
int mjdec_set_callback(mjdec_frame_cb frame_cb, void *usrdata);
```

Install the frame callback.

| 參數 | 說明 |
|---|---|
| `frame_cb` | Callback, or NULL to remove it. |
| `usrdata` | Pointer passed back to the callback. |

**回傳值**：Always 0.

### mjdec_irq_handler { #mjdec_irq_handler }

```c
void mjdec_irq_handler(void);
```

Decoder interrupt handler.

Installed by [`mjdec_init()`](#mjdec_init); applications do not call it.

### 匿名列舉 { #hal_mjdec-h-enum }

Interrupt types reported in `mjdec_frame_desc_t::ucIntType`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `MJDEC_HAL_INT_NORMAL` | `0` | A frame has been decoded. |
| `MJDEC_HAL_INT_BACK_IDLE` |  | The decoder returned to idle (not reported to the callback). |
| `MJDEC_HAL_INT_ALL` |  | Number of interrupt types. |

### 匿名列舉 { #hal_mjdec-h-enum-2 }

Output formats for `mjdec_config_t::yuv_mode`.

| 名稱 | 值 | 說明 |
|---|---|---|
| `MJDEC_HAL_FORMAT_YUV420_SP` | `0` | YUV 4:2:0 semi-planar: a Y plane and an interleaved UV plane of half height (NV12/NV21). |
| `MJDEC_HAL_FORMAT_YUV400` | `1` | Grey scale: Y plane only. |
| `MJDEC_HAL_FORMAT_YUV422_SP` | `2` | YUV 4:2:2 semi-planar: a Y plane and an interleaved UV plane of full height (NV16/NV61). |

### mjdec_config_t { #mjdec_config_t }

Decoder configuration for [`mjdec_init()`](#mjdec_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `width` | `uint16_t` | Image width in pixels; must match the JPEG header when `is_skip_header` is 1. |
| `height` | `uint16_t` | Image height in pixels; must match the JPEG header when `is_skip_header` is 1. |
| `input_buf_addr` | `uint8_t *` | JPEG data used to parse the header at init. |
| `output_buf_addr_yy` | `uint8_t *` | Y-plane output buffer. The driver rounds the address up to a multiple of 8 bytes; a 32-byte-aligned buffer is recommended for cache maintenance. |
| `output_buf_addr_uv` | `uint8_t *` | UV-plane output buffer (not used for `MJDEC_HAL_FORMAT_YUV400`); same alignment rules. |
| `yuv_mode` | `uint8_t` | Output format, one of the `MJDEC_HAL_FORMAT_*` values. |
| `is_skip_header` | `uint8_t` | 1: the data starts with a JPEG header; [`mjdec_init()`](#mjdec_init) parses it (searching the first 714, 599 or 605 bytes for YUV420, YUV400 and YUV422 respectively), loads its tables and the decoder skips it. 0: the data has no header. |
| `out_u_order_even` | `uint8_t` | 1: U samples at even and V samples at odd byte offsets of the UV plane; 0: the reverse order |

### mjdec_frame_desc_t { #mjdec_frame_desc_t }

Decoded frame description passed to the frame callback.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `frame_start_addr_yy` | `uint8_t *` | Start of the Y plane. |
| `frame_start_addr_uv` | `uint8_t *` | Start of the UV plane. |
| `frame_size_yy` | `uint32_t` | Y-plane size in bytes as reported by the driver. The current driver reports width x 8 here, not the full plane size; compute the plane size from the image dimensions. |
| `frame_size_uv` | `uint32_t` | UV-plane size in bytes: width x height for YUV422, width x height / 2 for YUV420, 0 for YUV400. |
| `ucIntType` | `uint8_t` | Interrupt type, `MJDEC_HAL_INT_NORMAL`. |

### 型別定義 { #hal_mjdec-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `mjdec_frame_cb` | `typedef int(*) mjdec_frame_cb(void *usrdata, mjdec_frame_desc_t *frame_desc)` | Frame callback. Called from the decoder interrupt when a frame has been decoded. Use only interrupt-safe calls. |
