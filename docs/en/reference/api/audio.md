---
title: Audio
description: Audio ADC (PDM and analog microphones) and I2S.
generated: tools/gen_api.py
migrate_from: []
---

# Audio

Audio ADC (PDM and analog microphones) and I2S.

| Header | Functions | Description |
|---|---|---|
| [`hal_auadc.h`](#hal_auadc-h) | 11 | Audio ADC (AUADC) driver: analog or PDM microphone capture into a DMA ping-pong buffer, high-pass filter and gain control. |
| [`hal_i2s.h`](#hal_i2s-h) | 5 | I2S driver: master or slave operation, I2S, justified and DSP/PCM formats, DMA transfers. |
| [`i2s_config.h`](#i2s_config-h) | 0 | Fixed I2S options applied by [`hal_i2s_init()`](#hal_i2s_init). |

## hal_auadc.h { #hal_auadc-h }

`#include "hal_auadc.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_auadc.h))

Audio ADC (AUADC) driver: analog or PDM microphone capture into a DMA ping-pong buffer, high-pass filter and gain control.

Capture is 16-bit mono PCM. Typical sequence: [`hal_auadc_amic_init()`](#hal_auadc_amic_init) or [`hal_auadc_pdm_init()`](#hal_auadc_pdm_init), optional gain and filter settings, [`hal_auadc_start()`](#hal_auadc_start); the frame callback then runs every time one half of the ping-pong buffer is full. Stop with [`hal_auadc_stop()`](#hal_auadc_stop) and release the DMA channel with [`hal_auadc_deinit()`](#hal_auadc_deinit).

The DMA writes one contiguous region of 2 x `pcm_frame_size` bytes that starts at `pcm_frame_buf[0]`: allocate it as one block and set `pcm_frame_buf[1]` to `pcm_frame_buf[0] + pcm_frame_size` bytes. On a cached system, invalidate the half named by the callback before reading it.

### hal_auadc_real_rate { #hal_auadc_real_rate }

```c
uint32_t hal_auadc_real_rate(uint32_t nominal_rate);
```

Get the actual capture rate for a nominal rate setting.

The figures are suitable for buffer sizing. An application that needs an exact time base should calibrate against a known reference signal.

| Parameter | Description |
|---|---|
| `nominal_rate` | Nominal rate in Hz, as in `hal_auadc_pdm_cfg_t::sample_rate`. |

**Returns:** Actual rate in Hz: 7937 for 8000; 47625 for 32000 (this setting runs at three times the 16 kHz rate); 48000 for 48000 (not characterized); 15875 for 16000 and for any other value.

### hal_auadc_amic_init { #hal_auadc_amic_init }

```c
int hal_auadc_amic_init(hal_auadc_amic_cfg_t *cfg);
```

Initialize analog microphone capture.

Validates `cfg`, obtains a DMA channel, sets the input pins to analog mode, configures the audio ADC (nominal 16 kHz, analog gain 42 dB) and the DMA ping-pong transfer. Capture does not start until [`hal_auadc_start()`](#hal_auadc_start).

| Parameter | Description |
|---|---|
| `cfg` | Configuration. The structure is copied; the buffers it points to must stay valid while capture runs. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | `cfg` is NULL, a field is out of range, a buffer pointer is NULL, or no DMA channel is available. |

### hal_auadc_pdm_init { #hal_auadc_pdm_init }

```c
int hal_auadc_pdm_init(hal_auadc_pdm_cfg_t *cfg);
```

Initialize PDM microphone capture.

Validates `cfg`, obtains a DMA channel, muxes the clock and data pins to the PDM function, configures the audio ADC at the requested rate and the DMA ping-pong transfer. Capture does not start until [`hal_auadc_start()`](#hal_auadc_start).

| Parameter | Description |
|---|---|
| `cfg` | Configuration. The structure is copied; the buffers it points to must stay valid while capture runs. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | `cfg` is NULL, `pcm_frame_size` is out of range, a buffer pointer is NULL, or no DMA channel is available. |

### hal_auadc_start { #hal_auadc_start }

```c
int hal_auadc_start(void);
```

Start capture.

Arms the DMA ping-pong transfer from the start of `pcm_frame_buf[0]` and starts the audio ADC.

| Return value | Description |
|---|---|
| `0` | Capture started. |
| `-1` | Neither init function has been called successfully. |

### hal_auadc_stop { #hal_auadc_stop }

```c
int hal_auadc_stop(void);
```

Stop capture.

Stops the DMA channel and the audio ADC and clears the ADC FIFO. The configuration is kept; [`hal_auadc_start()`](#hal_auadc_start) resumes capture from the first half.

| Return value | Description |
|---|---|
| `0` | Capture stopped. |
| `-1` | Neither init function has been called successfully. |

### hal_auadc_deinit { #hal_auadc_deinit }

```c
void hal_auadc_deinit(void);
```

Release the DMA channel obtained by [`hal_auadc_amic_init()`](#hal_auadc_amic_init) or [`hal_auadc_pdm_init()`](#hal_auadc_pdm_init).

Call it after [`hal_auadc_stop()`](#hal_auadc_stop) once capture is no longer needed; otherwise the DMA channel stays allocated. Also clears the frame callback. Does nothing if no init has been done.

### hal_auadc_set_high_pass_filter { #hal_auadc_set_high_pass_filter }

```c
void hal_auadc_set_high_pass_filter(int k1, int k2);
```

Configure the first-order high-pass filter of the capture path.

Transfer function: `H(z) = (1 - z^-1) / (1 - (1 - 2^-k1 - 2^-k2) z^-1)`. Larger coefficients give a lower corner frequency. The reset default is k1 = 8 with the k2 term disabled.

| Parameter | Description |
|---|---|
| `k1` | First coefficient, 3 to 13, or 0 to disable the k1 term. |
| `k2` | Second coefficient, 3 to 13, or 0 to disable the k2 term. |

### hal_auadc_set_analog_gain { #hal_auadc_set_analog_gain }

```c
void hal_auadc_set_analog_gain(int gain_db);
```

Set the analog (PGA) gain of the analog microphone input.

[`hal_auadc_amic_init()`](#hal_auadc_amic_init) programs 42 dB; call this function after init to change it.

| Parameter | Description |
|---|---|
| `gain_db` | Gain in dB, 6 to 42 in 3 dB steps. Values outside the range are clamped; other values are rounded down to a 3 dB step. |

### hal_auadc_set_digital_gain { #hal_auadc_set_digital_gain }

```c
void hal_auadc_set_digital_gain(float gain_db);
```

Set the digital gain of the capture path.

| Parameter | Description |
|---|---|
| `gain_db` | Gain in dB, -95.5 to +18 in 0.5 dB steps. Values outside the range are clamped; other values are truncated toward zero to a 0.5 dB step. |

### hal_auadc_get_analog_gain { #hal_auadc_get_analog_gain }

```c
int hal_auadc_get_analog_gain(void);
```

Get the current analog (PGA) gain.

**Returns:** Gain in dB, 6 to 42.

### hal_auadc_get_digital_gain { #hal_auadc_get_digital_gain }

```c
float hal_auadc_get_digital_gain(void);
```

Get the current digital gain.

**Returns:** Gain in dB, in 0.5 dB steps.

### Anonymous enum { #hal_auadc-h-enum }

PDM channel selection for `hal_auadc_pdm_cfg_t::pdm_ch`.

| Name | Value | Description |
|---|---|---|
| `HAL_AUADC_PDM_CH_LEFT` |  | Capture the PDM left channel. |
| `HAL_AUADC_PDM_CH_RIGHT` |  | Capture the PDM right channel. |

### hal_auadc_amic_cfg_t { #hal_auadc_amic_cfg_t }

Analog microphone configuration for [`hal_auadc_amic_init()`](#hal_auadc_amic_init).

The analog input channels 0 to 7 are GPIO 4, 5, 6, 7, 10, 11, 12 and 13. Capture runs at the nominal 16 kHz setting (15875 Hz actual).

| Field | Type | Description |
|---|---|---|
| `amic_single_ended` | `uint8_t` | 0: differential input (positive and negative channel); 1: single-ended input (positive channel only) |
| `amic_pos_ch` | `uint8_t` | Positive input channel, 0 to 7. |
| `amic_neg_ch` | `uint8_t` | Negative input channel, 0 to 7; used in differential mode only. |
| `pcm_frame_size` | `uint16_t` | Size of one half of the ping-pong buffer in bytes, 1 to 4095; use an even value (16-bit samples). |
| `pcm_frame_buf` | `int16_t *[2]` | The two halves of the ping-pong buffer; both must be non-NULL (see the file description for the layout). |
| `pcm_frame_event` | `hal_auadc_callback_t` | Frame-ready callback, or NULL. |

### hal_auadc_pdm_cfg_t { #hal_auadc_pdm_cfg_t }

PDM (digital) microphone configuration for [`hal_auadc_pdm_init()`](#hal_auadc_pdm_init).

The HAL does not validate the pin numbers. When GPIO 18 or 19 is used, the HAL first releases those pads from the 32 kHz crystal oscillator and selects the internal RC 32 kHz clock if the crystal was in use.

| Field | Type | Description |
|---|---|---|
| `pdm_clk_pin` | `uint8_t` | GPIO number of the PDM clock output. |
| `pdm_in_pin` | `uint8_t` | GPIO number of the PDM data input. |
| `pdm_ch` | `uint8_t` | PDM channel: `HAL_AUADC_PDM_CH_LEFT` or `HAL_AUADC_PDM_CH_RIGHT` (any other value selects the right channel). |
| `pcm_frame_size` | `uint16_t` | Size of one half of the ping-pong buffer in bytes, 1 to 4095; use an even value (16-bit samples). |
| `pcm_frame_buf` | `int16_t *[2]` | The two halves of the ping-pong buffer; both must be non-NULL (see the file description for the layout). |
| `pcm_frame_event` | `hal_auadc_callback_t` | Frame-ready callback, or NULL. |
| `sample_rate` | `uint32_t` | Nominal capture rate in Hz: 8000, 16000, 32000 or 48000. Zero, or any other value, selects 16000. The actual rate is derived from the 2.032 MHz audio clock and differs from the nominal figure; for example the 16000 setting yields 15875 Hz. Use [`hal_auadc_real_rate()`](#hal_auadc_real_rate) to obtain it. |

### Typedefs { #hal_auadc-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `hal_auadc_callback_t` | `typedef void(*) hal_auadc_callback_t(int buf_idx)` | Frame-ready callback. Called from the DMA interrupt each time one half of the capture buffer has been filled. Keep it short and use only interrupt-safe calls. |

## hal_i2s.h { #hal_i2s-h }

`#include "hal_i2s.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_i2s.h))

I2S driver: master or slave operation, I2S, justified and DSP/PCM formats, DMA transfers.

Typical sequence: fill an [`i2s_device_t`](#i2s_device_t), [`hal_i2s_setConfig()`](#hal_i2s_setConfig), [`hal_i2s_init()`](#hal_i2s_init) with the DMA capability flags, attach DMA channels with `I2S_CTRL_ATTACH_TX_DMA` and `I2S_CTRL_ATTACH_RX_DMA`, then queue transfers with [`hal_i2s_write()`](#hal_i2s_write) and [`hal_i2s_read()`](#hal_i2s_read). Pin multiplexing is not done by this driver. Fixed options (endianness, mono channel, clock inversion) come from [`i2s_config.h`](#i2s_config-h).

### hal_i2s_setConfig { #hal_i2s_setConfig }

```c
void hal_i2s_setConfig(i2s_device_t *dev);
```

Store an I2S configuration for the next [`hal_i2s_init()`](#hal_i2s_init).

Copies `dev` into the driver slot selected by `i2s_device_t::id`.

| Parameter | Description |
|---|---|
| `dev` | Configuration to copy. |

### hal_i2s_write { #hal_i2s_write }

```c
int hal_i2s_write(int i2s_id, const void *buffer, uint32_t size);
```

Queue a DMA transmit transfer.

Reloads the attached TX DMA channel with `size` bytes from `buffer` and starts it; returns without waiting for completion.

| Parameter | Description |
|---|---|
| `i2s_id` | I2S instance. |
| `buffer` | Data to send; must stay valid until the transfer completes. |
| `size` | Length in bytes. |

| Return value | Description |
|---|---|
| `0` | Transfer started. |
| `-1` | The device was not initialized with `COMMON_CAPS_DMA_TX`, or no TX DMA channel is attached. |

### hal_i2s_read { #hal_i2s_read }

```c
int hal_i2s_read(int i2s_id, void *buffer, uint32_t size);
```

Queue a DMA receive transfer.

Reloads the attached RX DMA channel to receive `size` bytes into `buffer` and starts it; returns without waiting for completion.

| Parameter | Description |
|---|---|
| `i2s_id` | I2S instance. |
| `buffer` | Destination; must stay valid until the transfer completes. |
| `size` | Length in bytes. |

| Return value | Description |
|---|---|
| `0` | Transfer started. |
| `-1` | The device was not initialized with `COMMON_CAPS_DMA_RX`, or no RX DMA channel is attached. |

### hal_i2s_control { #hal_i2s_control }

```c
int hal_i2s_control(int i2s_id, int cmd, void *args);
```

Control the I2S interface.

| Parameter | Description |
|---|---|
| `i2s_id` | I2S instance. |
| `cmd` | Command, one of the `I2S_CTRL_*` codes. |
| `args` | Command argument; see the description of each `I2S_CTRL_*` code. |

**Returns:** The FIFO count for `I2S_CTRL_GET_TX_FIFO` and `I2S_CTRL_GET_RX_FIFO`; otherwise 0 on success, or -1 for an unknown command or (for `I2S_CTRL_SET_SAMPL_FREQ`) an invalid configured frame size.

### hal_i2s_init { #hal_i2s_init }

```c
int hal_i2s_init(int i2s_id, uint16_t caps);
```

Initialize and enable an I2S interface with the configuration stored by [`hal_i2s_setConfig()`](#hal_i2s_setConfig).

Programs the format, frame and sample sizes, channel count, bit clock (derived from the I2S peripheral clock and `i2s_device_t::sampl_freq_hz`) and FIFO, then enables the interface as master or slave. Resets the TX and RX DMA channels to -1.

| Parameter | Description |
|---|---|
| `i2s_id` | I2S instance. |
| `caps` | Capability flags: `COMMON_CAPS_DMA_TX` and/or `COMMON_CAPS_DMA_RX` enable the FIFO DMA requests. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | Invalid interface format, frame size, data size or channel count (including three or four channels outside DSP mode). |

### i2s_index_type { #i2s_index_type }

I2S instance index.

| Name | Value | Description |
|---|---|---|
| `I2S0_INDEX` |  | I2S instance 0 (present when `BSP_USING_I2S0` is defined). |
| `I2S_MAX_INDEX` |  | Number of I2S instances. |

### Anonymous enum { #hal_i2s-h-enum }

Command codes for [`hal_i2s_control()`](#hal_i2s_control).

| Name | Value | Description |
|---|---|---|
| `I2S_CTRL_ATTACH_TX_DMA` |  | Attach the DMA channel used by [`hal_i2s_write()`](#hal_i2s_write). `args`: DMA channel index cast to `void *`. |
| `I2S_CTRL_ATTACH_RX_DMA` |  | Attach the DMA channel used by [`hal_i2s_read()`](#hal_i2s_read). `args`: DMA channel index cast to `void *`. |
| `I2S_CTRL_GET_TX_FIFO` |  | [`hal_i2s_control()`](#hal_i2s_control) returns the TX FIFO available count reported by the hardware. `args`: unused. |
| `I2S_CTRL_GET_RX_FIFO` |  | [`hal_i2s_control()`](#hal_i2s_control) returns the RX FIFO available count reported by the hardware. `args`: unused. |
| `I2S_CTRL_SET_SAMPL_FREQ` |  | Change the sample rate. `args`: rate in Hz cast to `void *`. The bit clock is recomputed from the I2S clock and the configured frame size. |
| `I2S_CTRL_SET_FIFO_24B_LJ` |  | Select the FIFO layout of 24-bit samples. `args`: 0 = right-justified (bits 23:0 hold the sample, bits 31:24 are zero), 1 = left-justified (bits 31:8 hold the sample, bits 7:0 are zero). |

### interface_mode_t { #interface_mode_t }

I2S interface (frame) format.

| Name | Value | Description |
|---|---|---|
| `I2S_MODE_STD` |  | Standard I2S: left-justified frame with a one-bit data delay. |
| `I2S_MODE_LEFT` |  | Left-justified format, no data delay. |
| `I2S_MODE_RIGHT` |  | Right-justified format. |
| `I2S_MODE_DSP_A` |  | DSP/PCM mode A: one-bit-clock frame sync, one-bit data delay. |
| `I2S_MODE_DSP_B` |  | DSP/PCM mode B: one-bit-clock frame sync, no data delay. |

### i2s_frame_size_t { #i2s_frame_size_t }

Frame (slot) size per channel.

| Name | Value | Description |
|---|---|---|
| `I2S_FRAME_LEN_8` | `1` | 8-bit slot |
| `I2S_FRAME_LEN_16` | `2` | 16-bit slot |
| `I2S_FRAME_LEN_24` | `3` | 24-bit slot |
| `I2S_FRAME_LEN_32` | `4` | 32-bit slot |

### i2s_data_size_t { #i2s_data_size_t }

Sample (data) size.

| Name | Value | Description |
|---|---|---|
| `I2S_DATA_LEN_8` | `1` | 8-bit samples |
| `I2S_DATA_LEN_16` | `2` | 16-bit samples |
| `I2S_DATA_LEN_24` | `3` | 24-bit samples |
| `I2S_DATA_LEN_32` | `4` | 32-bit samples |

### i2s_channel_num_t { #i2s_channel_num_t }

Number of channels per frame.

| Name | Value | Description |
|---|---|---|
| `I2S_FS_CHANNELS_NUM_MONO` | `1` | Mono: two-channel frames of which one channel is used (see `I2S_MONO_CHANNEL` in [`i2s_config.h`](#i2s_config-h)). |
| `I2S_FS_CHANNELS_NUM_2` | `2` | Stereo. With 8-bit or 16-bit samples, the left and right samples share one FIFO entry. |
| `I2S_FS_CHANNELS_NUM_3` | `3` | Three channels; DSP modes only, frame size must equal data size. |
| `I2S_FS_CHANNELS_NUM_4` | `4` | Four channels; DSP modes only, frame size must equal data size. [`hal_i2s_init()`](#hal_i2s_init) currently returns -1 for this value. |

### i2s_mode_t { #i2s_mode_t }

Clock role.

| Name | Value | Description |
|---|---|---|
| `I2S_MODE_MASTER` | `0` | Master: the SoC drives the bit clock and frame sync. |
| `I2S_MODE_SLAVE` |  | Slave: the bit clock and frame sync are inputs. |

### i2s_device_t { #i2s_device_t }

I2S configuration and run-time state.

Pass a filled copy to [`hal_i2s_setConfig()`](#hal_i2s_setConfig) before [`hal_i2s_init()`](#hal_i2s_init).

| Field | Type | Description |
|---|---|---|
| `caps` | `uint16_t` | Capability flags; overwritten by the `caps` argument of [`hal_i2s_init()`](#hal_i2s_init). |
| `id` | `uint8_t` | I2S instance; selects the slot written by [`hal_i2s_setConfig()`](#hal_i2s_setConfig). |
| `iis_mode` | `i2s_mode_t` | Master or slave. |
| `interface_mode` | `interface_mode_t` | Interface format. |
| `sampl_freq_hz` | `uint32_t` | Sample rate in Hz. |
| `channel_num` | `i2s_channel_num_t` | Channels per frame. |
| `frame_size` | `i2s_frame_size_t` | Slot size per channel. |
| `data_size` | `i2s_data_size_t` | Sample size. |
| `fifo_threshold` | `uint8_t` | TX and RX FIFO threshold for DMA requests, 0 to 15. |
| `tx_dma` | `int` | TX DMA channel; set to -1 by [`hal_i2s_init()`](#hal_i2s_init) and set with `I2S_CTRL_ATTACH_TX_DMA`. |
| `rx_dma` | `int` | RX DMA channel; set to -1 by [`hal_i2s_init()`](#hal_i2s_init) and set with `I2S_CTRL_ATTACH_RX_DMA`. |

### Macros { #hal_i2s-h-macros }

| Name | Value | Description |
|---|---|---|
| `I2S_DEFAULT_RTO_TIMEOUT` | `15` | Default receive time-out value. Not used by the I2S driver. |

## i2s_config.h { #i2s_config-h }

`#include "i2s_config.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/default_config/i2s_config.h))

Fixed I2S options applied by [`hal_i2s_init()`](#hal_i2s_init).

### Macros { #i2s_config-h-macros }

| Name | Value | Description |
|---|---|---|
| `I2S_ADUIO_PLL_DEFAULT` | `AUDIO_PLL_12288000_HZ` | Default audio PLL setting (12.288 MHz); not used by the I2S driver. |
| `I2S_DATA_ENDIAN` | `I2S_DATA_ENDIAN_MSB` | Bit order: MSB first. |
| `I2S_MONO_CHANNEL` | `I2S_RX_MONO_MODE_RIGHT_CHANNEL` | Channel used in mono mode: the right channel. |
| `I2S_LR_EXCHANGE` | `DISABLE` | Swap the left and right samples within each FIFO entry (stereo 8-bit and 16-bit samples only); disabled. |
| `I2S_FS_INVERT` | `DISABLE` | Invert the frame-sync polarity; disabled. |
| `I2S_BCLK_INVERT` | `DISABLE` | Invert the bit-clock polarity; disabled. |
