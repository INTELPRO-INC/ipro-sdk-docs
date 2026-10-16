---
title: IPRO7AI EVK 板卡庫
description: EVK 子板的面板、繪圖、相機、麥克風、喇叭、PCM 與 microSD 介面。
generated: tools/gen_api.py
migrate_from: []
---

# IPRO7AI EVK 板卡庫

EVK 子板的面板、繪圖、相機、麥克風、喇叭、PCM 與 microSD 介面。說明取自標頭檔註解（英文）。

| 標頭 | 函式 | 說明 |
|---|---|---|
| [`evk.h`](#evk-h) | 2 | IPRO7AI EVK board library: one include, one [`evk_begin()`](#evk_begin). |
| [`st7789p3.h`](#st7789p3-h) | 40 | ST7789P3 4-wire SPI LCD driver for the LCM-T2D4BP-084 (240x320 IPS). |
| [`st7789p3_port.h`](#st7789p3_port-h) | 0 | Board and SoC wiring for the LCM-T2D4BP-084 (ST7789P3) SPI LCD. |
| [`evk_gfx.h`](#evk_gfx-h) | 10 | Row-compositing text and overlay helpers for the ST7789P3 panel. |
| [`font5x7.h`](#font5x7-h) | 2 | Minimal 5x7 bitmap font for on-screen text: ASCII 0x20..0x5A (space, punctuation, digits, upper case). |
| [`evk_cam.h`](#evk_cam-h) | 22 | SC101IOT DVP camera into the ISP, with two outputs: LCD preview and NPU input. |
| [`evk_cam_port.h`](#evk_cam_port-h) | 0 | Board wiring for the SC101IOT DVP camera on the IPRO7AI EVK. |
| [`evk_mic.h`](#evk_mic-h) | 11 | PDM microphone capture (IM69D129 on GPIO18/19 through the AUADC). |
| [`evk_spk.h`](#evk_spk-h) | 11 | Speaker: on-chip DAC (GPIO23) into the TPA2037D1 class-D amplifier. |
| [`evk_audio_port.h`](#evk_audio_port-h) | 0 | Speaker (DAC and class-D amplifier) and PDM microphone wiring on the IPRO7AI EVK sub-board. |
| [`evk_pcm.h`](#evk_pcm-h) | 8 | Integer-only PCM helpers shared by the microphone and speaker paths. |
| [`evk_sd.h`](#evk_sd-h) | 7 | micro-SD card on the SDH controller (GPIO27-34), FatFS mounted at "sd:". |

## evk.h { #evk-h }

`#include "evk.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk.h)）

IPRO7AI EVK board library: one include, one [`evk_begin()`](#evk_begin).

The IPRO7AI EVK sub-board (`CONFIG_IPRO7AI_EVK`) carries a 2.4-inch ST7789P3 LCD, an SC101IOT 720p DVP camera, a PDM microphone and a DAC-driven class-D speaker. This library is the board support layer for it: an application calls [`evk_begin()`](#evk_begin) once and then uses the functions in [`st7789p3.h`](#st7789p3-h) and [`evk_gfx.h`](#evk_gfx-h) (panel), [`evk_cam.h`](#evk_cam-h) (camera, ISP and NPU feed), [`evk_mic.h`](#evk_mic-h) and [`evk_spk.h`](#evk_spk-h) (audio) and [`evk_sd.h`](#evk_sd-h) (micro-SD card).

Which blocks are compiled in follows the application's `.config`:

Option 
Adds 


CONFIG_COMPONENTS_IPRO7AI_EVK_ENABLE 
the library; panel and gfx are always built 


CONFIG_EVK_CAMERA 
evk_cam (needs MM_SUPPORT and the sensor) 


CONFIG_EVK_AUDIO 
evk_mic, evk_spk, evk_pcm (needs AUDIO_OUTPUT) 


CONFIG_EVK_SDCARD 
evk_sd (needs FatFS and EVFS) 


CONFIG_EVK_SHELL 
lcd, cam, mic, spk, sd shell commands

Pin assignments are in [`st7789p3_port.h`](#st7789p3_port-h), [`evk_cam_port.h`](#evk_cam_port-h) and [`evk_audio_port.h`](#evk_audio_port-h).

### evk_begin { #evk_begin }

```c
int evk_begin(void);
```

Bring the board to a known state.

Holds the camera sensor in reset (when the camera block is built), turns the speaker amplifier off (when the audio block is built), then initialises the panel with [`ST7789P3_SEQ_MINIMAL`](#st7789p3-h-macros) and clears it to black. A second call returns 0 without doing anything.

**回傳值**：0 on success, or -1 if the panel did not initialise (the camera and amplifier steps have still run, and [`evk_ready()`](#evk_ready) reports true).

!!! note "注意"
    Call once from task context: the panel reset and init sequence sleep for several hundred milliseconds.

### evk_ready { #evk_ready }

```c
bool evk_ready(void);
```

Report whether [`evk_begin()`](#evk_begin) has run.

**回傳值**：true once [`evk_begin()`](#evk_begin) has completed (whatever it returned).

### 巨集 { #evk-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_HAS_DISPLAY` | `1` | Panel and gfx: always 1. |
| `EVK_HAS_CAMERA` | `1` | 1 when `CONFIG_EVK_CAMERA` is set ([`evk_cam.h`](#evk_cam-h)). |
| `EVK_HAS_AUDIO` | `1` | 1 when `CONFIG_EVK_AUDIO` is set ([`evk_mic.h`](#evk_mic-h), [`evk_spk.h`](#evk_spk-h)). |
| `EVK_HAS_SDCARD` | `1` | 1 when `CONFIG_EVK_SDCARD` is set ([`evk_sd.h`](#evk_sd-h)). |
| `EVK_BOARD_NAME` | `"IPRO7AI EVK"` | Board name string, as printed in the [`evk_begin()`](#evk_begin) log line. |

## st7789p3.h { #st7789p3-h }

`#include "st7789p3.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/st7789p3.h)）

ST7789P3 4-wire SPI LCD driver for the LCM-T2D4BP-084 (240x320 IPS).

No framebuffer and no DMA: transfers are blocking, polled and row-at-a-time out of a single static row buffer, so the driver needs no heap and no PSRAM. Drawing functions take a recursive bus lock, so several tasks can draw.

Pixel format is RGB565. Bytes go on the wire high byte first; the driver keeps its row buffer pre-swapped so 16-bit SPI frames land in that order (`SPI_MSB_BYTE0_DIRECTION_FIRST` sends byte 0 of each 16-bit frame first). Functions that take a colour or a pixel row in "host order" swap it themselves; [`st7789p3_blit_push()`](#st7789p3_blit_push) expects "wire order" ([`st7789p3_swap()`](#st7789p3_swap)).

Typical use: [`st7789p3_init()`](#st7789p3_init) (or [`evk_begin()`](#evk_begin)), then [`st7789p3_fill_rect()`](#st7789p3_fill_rect) / [`st7789p3_draw_row()`](#st7789p3_draw_row), or a [`st7789p3_blit_start()`](#st7789p3_blit_start) / [`st7789p3_blit_push()`](#st7789p3_blit_push) / [`st7789p3_blit_end()`](#st7789p3_blit_end) burst inside [`st7789p3_bus_lock()`](#st7789p3_bus_lock) / [`st7789p3_bus_unlock()`](#st7789p3_bus_unlock). The wiring is in [`st7789p3_port.h`](#st7789p3_port-h).

### st7789p3_bus_init { #st7789p3_bus_init }

```c
void st7789p3_bus_init(void);
```

Mux the pins and configure SPI0 and the control GPIOs.

Creates the bus lock on first use. Idempotent. Does not touch RESET beyond driving it inactive, and sends nothing to the panel.

### st7789p3_reset { #st7789p3_reset }

```c
void st7789p3_reset(void);
```

Pulse RESET low, release it and wait for the panel to settle.

The datasheet's reset table gives the reset timings as "TBD", so the widths come from its spike-rejection rule instead: a RESX pulse shorter than 5 us is rejected, longer than 9 us resets. RESET is held low for 10 ms, and the 150 ms settle covers the documented 120 ms maximum blanking sequence plus the NVM reload. Takes about 170 ms in total.

!!! note "注意"
    Blocking; sleeps when the scheduler is running.

### st7789p3_init { #st7789p3_init }

```c
int st7789p3_init(int seq, int clear);
```

Full bring-up: bus init, hardware reset, init sequence, default orientation and optional clear.

After the init sequence the orientation is set to [`ST_DEFAULT_DIR`](#st7789p3_port-h-macros), RGB order, mirroring off and inversion on.

| 參數 | 說明 |
|---|---|
| `seq` | [`ST7789P3_SEQ_MINIMAL`](#st7789p3-h-macros) or [`ST7789P3_SEQ_TUNED`](#st7789p3-h-macros). |
| `clear` | Non-zero to fill the screen black once the panel is on. |

**回傳值**：[`ST7789P3_OK`](#st7789p3-h-macros), or [`ST7789P3_ERR_PARAM`](#st7789p3-h-macros) for an unknown sequence.

!!! note "注意"
    Blocking (about 0.5 s); sleeps when the scheduler is running.

### st7789p3_get_seq { #st7789p3_get_seq }

```c
int st7789p3_get_seq(void);
```

Report which sequence the last successful [`st7789p3_init()`](#st7789p3_init) used.

**回傳值**：[`ST7789P3_SEQ_MINIMAL`](#st7789p3-h-macros) or [`ST7789P3_SEQ_TUNED`](#st7789p3-h-macros) ([`ST7789P3_SEQ_MINIMAL`](#st7789p3-h-macros) before any init).

### st7789p3_is_ready { #st7789p3_is_ready }

```c
bool st7789p3_is_ready(void);
```

Report whether the panel has been initialised.

**回傳值**：true once [`st7789p3_init()`](#st7789p3_init) has completed.

### st7789p3_set_spi_clk { #st7789p3_set_spi_clk }

```c
void st7789p3_set_spi_clk(uint32_t hz);
```

Set the SPI clock; reprograms SPI0 immediately if the bus is up.

The IPRO7 SPI clock is sourced from XCLK at or below 16 MHz and from BCLK above it, and the driver picks the closest achievable rate not above the request, so the effective clock can be lower than asked.

| 參數 | 說明 |
|---|---|
| `hz` | Requested SCLK in Hz (default [`ST_SPI_CLK_HZ`](#st7789p3_port-h-macros)); 0 is ignored. |

### st7789p3_get_spi_clk { #st7789p3_get_spi_clk }

```c
uint32_t st7789p3_get_spi_clk(void);
```

Read back the requested SPI clock.

**回傳值**：The last value given to [`st7789p3_set_spi_clk()`](#st7789p3_set_spi_clk), in Hz. This is the request, not the measured rate.

### st7789p3_set_framing { #st7789p3_set_framing }

```c
void st7789p3_set_framing(int mode);
```

Select the command framing.

| 參數 | 說明 |
|---|---|
| `mode` | [`ST7789P3_FRAME_WINDOW`](#st7789p3-h-macros) or [`ST7789P3_FRAME_BYTE`](#st7789p3-h-macros); any other value selects [`ST7789P3_FRAME_WINDOW`](#st7789p3-h-macros). |

### st7789p3_get_framing { #st7789p3_get_framing }

```c
int st7789p3_get_framing(void);
```

Read the command framing.

**回傳值**：[`ST7789P3_FRAME_WINDOW`](#st7789p3-h-macros) or [`ST7789P3_FRAME_BYTE`](#st7789p3-h-macros).

### st7789p3_set_backlight { #st7789p3_set_backlight }

```c
void st7789p3_set_backlight(int on);
```

Switch the backlight enable pin (GPIO12).

On or off only: the module has no LEDPWM pin and brightness is set by the board's LED driver. Before the bus is initialised the setting is stored and applied by [`st7789p3_bus_init()`](#st7789p3_bus_init).

| 參數 | 說明 |
|---|---|
| `on` | Non-zero for on (default), 0 for off. |

### st7789p3_get_backlight { #st7789p3_get_backlight }

```c
int st7789p3_get_backlight(void);
```

Read the backlight setting.

**回傳值**：1 if on, 0 if off.

### st7789p3_set_dir { #st7789p3_set_dir }

```c
int st7789p3_set_dir(uint8_t dir, uint8_t mirror);
```

Set the orientation via MADCTL (36h) and swap the reported dimensions accordingly.

| 參數 | 說明 |
|---|---|
| `dir` | 0 = portrait 240x320, 1 = landscape 320x240, 2 = portrait flipped, 3 = landscape flipped. |
| `mirror` | Non-zero mirrors horizontally (toggles MX within the mode). |

**回傳值**：[`ST7789P3_OK`](#st7789p3-h-macros), or [`ST7789P3_ERR_PARAM`](#st7789p3-h-macros) if `dir` is above 3.

### st7789p3_get_dir { #st7789p3_get_dir }

```c
uint8_t st7789p3_get_dir(void);
```

Read the orientation.

**回傳值**：0..3, as passed to [`st7789p3_set_dir()`](#st7789p3_set_dir).

### st7789p3_set_bgr { #st7789p3_set_bgr }

```c
void st7789p3_set_bgr(int bgr);
```

Select RGB or BGR channel order (MADCTL bit 3) and re-apply MADCTL immediately.

Use this when red and blue come out swapped.

| 參數 | 說明 |
|---|---|
| `bgr` | 0 for RGB (default), non-zero for BGR. |

### st7789p3_get_bgr { #st7789p3_get_bgr }

```c
int st7789p3_get_bgr(void);
```

Read the channel order.

**回傳值**：0 for RGB, 1 for BGR.

### st7789p3_set_inversion { #st7789p3_set_inversion }

```c
void st7789p3_set_inversion(int on);
```

Switch display inversion: INVON (21h) or INVOFF (20h).

The IPS glass is normally black, so the init sequences turn inversion on; without it the picture comes out as a negative.

| 參數 | 說明 |
|---|---|
| `on` | Non-zero for INVON (default), 0 for INVOFF. |

### st7789p3_get_inversion { #st7789p3_get_inversion }

```c
int st7789p3_get_inversion(void);
```

Read the inversion setting.

**回傳值**：1 if inversion is on, 0 if off.

### st7789p3_set_sleep { #st7789p3_set_sleep }

```c
void st7789p3_set_sleep(int sleep_in);
```

Enter or leave sleep: SLPIN (10h) or SLPOUT (11h).

| 參數 | 說明 |
|---|---|
| `sleep_in` | Non-zero to enter sleep, 0 to leave it. |

!!! note "注意"
    Waits the 120 ms the datasheet requires before the next command.

### st7789p3_set_display { #st7789p3_set_display }

```c
void st7789p3_set_display(int on);
```

Switch the display output: DISPON (29h) or DISPOFF (28h).

GRAM contents are kept.

| 參數 | 說明 |
|---|---|
| `on` | Non-zero for on, 0 for off. |

!!! note "注意"
    Waits 10 ms after the command.

### st7789p3_gamma_default { #st7789p3_gamma_default }

```c
void st7789p3_gamma_default(void);
```

Restore the datasheet default gamma curves (E0h/E1h).

### st7789p3_get_madctl { #st7789p3_get_madctl }

```c
uint8_t st7789p3_get_madctl(void);
```

Read the MADCTL byte as last written.

**回傳值**：MADCTL (36h) value.

### st7789p3_write_reg { #st7789p3_write_reg }

```c
void st7789p3_write_reg(uint8_t cmd, const uint8_t *args, uint32_t nargs);
```

Write a command byte (D/C low) followed by optional parameter bytes (D/C high), using the current framing.

Does nothing until the bus has been initialised. Does not take the bus lock.

| 參數 | 說明 |
|---|---|
| `cmd` | Command byte. |
| `args` | Parameter bytes, or NULL when `nargs` is 0. |
| `nargs` | Number of parameter bytes. |

### st7789p3_write_cmd { #st7789p3_write_cmd }

```c
void st7789p3_write_cmd(uint8_t cmd);
```

Write a command byte alone (D/C low).

| 參數 | 說明 |
|---|---|
| `cmd` | Command byte. |

### st7789p3_write_data { #st7789p3_write_data }

```c
void st7789p3_write_data(const uint8_t *buf, uint32_t len);
```

Write parameter or data bytes alone (D/C high) in one CS window.

Does nothing if the bus is not initialised, `buf` is NULL or `len` is 0.

| 參數 | 說明 |
|---|---|
| `buf` | Bytes to send. |
| `len` | Number of bytes. |

### st7789p3_read_reg { #st7789p3_read_reg }

```c
int st7789p3_read_reg(uint8_t cmd, uint8_t *out, uint32_t nbytes);
```

Read back a register over the shared SDA line (bit-banged).

The module has no separate SDO pin, so this is the datasheet's "Interface-I" read: command byte out on SDA, then ONE dummy clock, then the chip drives the same SDA line. The driver re-muxes SCLK and MOSI to GPIO for the transfer and restores hardware SPI afterwards (initialising the bus first if needed).

Command-Table-2 registers are not readable unless SPIRD (E7h bit 0) is set; Command-Table-1 reads (04h RDDID, 09h RDDST, 0Ah RDDPM, DAh/DBh/DCh RDID1-3) work as shipped.

| 參數 | 說明 |
|---|---|
| `cmd` | Read command. |
| `out` | Destination buffer, `nbytes` long. |
| `nbytes` | Bytes to clock in, 1..8 (1 for RDID1-3, 3 for RDDID, 4 for RDDST). |

**回傳值**：[`ST7789P3_OK`](#st7789p3-h-macros), or [`ST7789P3_ERR_PARAM`](#st7789p3-h-macros) if `out` is NULL or `nbytes` is out of range.

### st7789p3_width { #st7789p3_width }

```c
uint16_t st7789p3_width(void);
```

Panel width in the current orientation.

**回傳值**：240 in portrait, 320 in landscape.

### st7789p3_height { #st7789p3_height }

```c
uint16_t st7789p3_height(void);
```

Panel height in the current orientation.

**回傳值**：320 in portrait, 240 in landscape.

### st7789p3_set_window { #st7789p3_set_window }

```c
void st7789p3_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
```

Send CASET (2Ah) and RASET (2Bh) for an inclusive rectangle, ready for RAMWR.

No clipping is applied.

| 參數 | 說明 |
|---|---|
| `x0` | First column. |
| `y0` | First row. |
| `x1` | Last column (inclusive). |
| `y1` | Last row (inclusive). |

### st7789p3_blit_start { #st7789p3_blit_start }

```c
void st7789p3_blit_start(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
```

Open a pixel burst: set the window, send RAMWR (2Ch), hold CS low and switch SPI to 16-bit frames.

Coordinates are inclusive and not clipped. Wrap the whole burst in [`st7789p3_bus_lock()`](#st7789p3_bus_lock) / [`st7789p3_bus_unlock()`](#st7789p3_bus_unlock).

| 參數 | 說明 |
|---|---|
| `x0` | First column. |
| `y0` | First row. |
| `x1` | Last column (inclusive). |
| `y1` | Last row (inclusive). |

### st7789p3_blit_push { #st7789p3_blit_push }

```c
void st7789p3_blit_push(const uint16_t *pixels, uint16_t npix);
```

Push pixels into the burst opened by [`st7789p3_blit_start()`](#st7789p3_blit_start).

| 參數 | 說明 |
|---|---|
| `pixels` | RGB565 pixels in wire order (fill with [`st7789p3_swap()`](#st7789p3_swap)). |
| `npix` | Number of pixels; 0 (or a NULL `pixels`) does nothing. |

### st7789p3_blit_end { #st7789p3_blit_end }

```c
void st7789p3_blit_end(void);
```

Close the burst opened by [`st7789p3_blit_start()`](#st7789p3_blit_start): wait for the bus to go idle, restore 8-bit frames and release CS.

### st7789p3_bus_lock { #st7789p3_bus_lock }

```c
void st7789p3_bus_lock(void);
```

Take the panel bus lock (recursive, waits forever).

[`st7789p3_fill_rect()`](#st7789p3_fill_rect), [`st7789p3_draw_row()`](#st7789p3_draw_row) and the evk_gfx direct-drawing helpers take it themselves. Anything that drives [`st7789p3_blit_start()`](#st7789p3_blit_start) / [`st7789p3_blit_push()`](#st7789p3_blit_push) / [`st7789p3_blit_end()`](#st7789p3_blit_end) directly must wrap the WHOLE burst, otherwise two tasks interleave their pixels in one RAMWR window and the panel shows shredded rows.

!!! note "注意"
    Task context only. A no-op before [`st7789p3_bus_init()`](#st7789p3_bus_init) and while the scheduler is not running.

### st7789p3_bus_unlock { #st7789p3_bus_unlock }

```c
void st7789p3_bus_unlock(void);
```

Release the panel bus lock taken with [`st7789p3_bus_lock()`](#st7789p3_bus_lock).

!!! note "注意"
    Task context only. A no-op before [`st7789p3_bus_init()`](#st7789p3_bus_init) and while the scheduler is not running.

### st7789p3_swap { #st7789p3_swap }

```c
uint16_t st7789p3_swap(uint16_t c);
```

Convert an RGB565 value between host order and wire order (byte swap).

| 參數 | 說明 |
|---|---|
| `c` | RGB565 colour. |

**回傳值**：`c` with its two bytes exchanged.

### st7789p3_fill_rect { #st7789p3_fill_rect }

```c
void st7789p3_fill_rect(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1, uint16_t color);
```

Fill an inclusive rectangle with one colour, clipped to the panel.

Takes the bus lock and yields every 16 rows. Does nothing if the bus is not initialised or nothing is left after clipping.

| 參數 | 說明 |
|---|---|
| `x0` | First column. |
| `y0` | First row. |
| `x1` | Last column (inclusive). |
| `y1` | Last row (inclusive). |
| `color` | RGB565 colour in host order. |

### st7789p3_fill_screen { #st7789p3_fill_screen }

```c
void st7789p3_fill_screen(uint16_t color);
```

Fill the whole visible area with one colour.

| 參數 | 說明 |
|---|---|
| `color` | RGB565 colour in host order. |

### st7789p3_draw_pixel { #st7789p3_draw_pixel }

```c
void st7789p3_draw_pixel(uint16_t x, uint16_t y, uint16_t color);
```

Draw a single pixel.

Cheap for markers, far too slow for bulk drawing.

| 參數 | 說明 |
|---|---|
| `x` | Column. |
| `y` | Row. |
| `color` | RGB565 colour in host order. |

### st7789p3_draw_row { #st7789p3_draw_row }

```c
void st7789p3_draw_row(uint16_t x0, uint16_t y, const uint16_t *row, uint16_t npix);
```

Draw one row of pixels starting at (`x0`, `y`).

The row is clipped to the panel width and copied into the driver's row buffer (swapped to wire order). Takes the bus lock.

| 參數 | 說明 |
|---|---|
| `x0` | First column. |
| `y` | Row. |
| `row` | RGB565 pixels in host order. |
| `npix` | Number of pixels. |

### st7789p3_pin_out { #st7789p3_pin_out }

```c
void st7789p3_pin_out(uint8_t pin, int level);
```

Drive any pin as a plain GPIO output, for continuity checks with a multimeter.

Leaves the pin muxed as GPIO and marks the bus uninitialised, so drawing calls do nothing until [`st7789p3_bus_init()`](#st7789p3_bus_init) or [`st7789p3_init()`](#st7789p3_init) runs again.

| 參數 | 說明 |
|---|---|
| `pin` | GPIO number. |
| `level` | Non-zero for high, 0 for low. |

### st7789p3_pin_in { #st7789p3_pin_in }

```c
int st7789p3_pin_in(uint8_t pin);
```

Read any pin as a plain GPIO input.

Has the same side effect as [`st7789p3_pin_out()`](#st7789p3_pin_out): the bus must be initialised again afterwards.

| 參數 | 說明 |
|---|---|
| `pin` | GPIO number. |

**回傳值**：Pin level: 0 for low, non-zero for high.

### 巨集 { #st7789p3-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `ST7789P3_OK` | `0` | Success. |
| `ST7789P3_ERR_PARAM` | `-1` | Argument out of range or NULL. |
| `ST_BLACK` | `0x0000u` | Black. |
| `ST_WHITE` | `0xFFFFu` | White. |
| `ST_RED` | `0xF800u` | Red. |
| `ST_GREEN` | `0x07E0u` | Green. |
| `ST_BLUE` | `0x001Fu` | Blue. |
| `ST_YELLOW` | `0xFFE0u` | Yellow. |
| `ST_CYAN` | `0x07FFu` | Cyan. |
| `ST_MAGENTA` | `0xF81Fu` | Magenta. |
| `ST_GRAY` | `0x8410u` | Mid grey. |
| `ST7789P3_SEQ_MINIMAL` | `0` | Only the mandatory settings (RGB565, MADCTL, INVON); every power, timing and gamma register stays at the datasheet default. The default. |
| `ST7789P3_SEQ_TUNED` | `1` | Minimal plus the conventional ST7789-module power, VCOM and gamma block; for an image that looks washed out, dim or flickery with the minimal one. |
| `ST7789P3_FRAME_WINDOW` | `0` | One CS-low window per register write (default). |
| `ST7789P3_FRAME_BYTE` | `1` | One CS-low window per byte, for a marginal link. |
| `ST_RGB565(r, g, b)` | `((uint16_t)(((uint16_t)((r) & 0xF8) <...` | Pack 8-bit red, green and blue into an RGB565 value (host order). |

## st7789p3_port.h { #st7789p3_port-h }

`#include "st7789p3_port.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/st7789p3_port.h)）

Board and SoC wiring for the LCM-T2D4BP-084 (ST7789P3) SPI LCD.

Module: LCM-T2D4BP-084 V1.0, 2.4-inch IPS TFT, transmissive / normally black, 240(H) x 320(V) dots, driver IC Sitronix ST7789P3, 4-line SPI ("SPI-4" / 4L1P), 17-pin FPC. VDD = VDDIO = 2.8..3.3 V; backlight = 4 white LEDs, Vf 3.0 V at 80 mA.

FPC pinout (module specification, section 7) and how the board uses it:

```text
1  GND      -> GND
2  TP_SDA   \
3  TP_SCL    |  capacitive touch controller - NOT CONNECTED on this board.
4  TP_RST    |  The module specification names no touch IC and gives no
5  TP_INT    |  register map, so touch is not supported.
6  TP_VDD   /
7  TE       -> NOT CONNECTED. Without it there is no tearing-effect sync;
               full-frame writes can shear against the panel scan.
8  RESET    -> GPIO14   (active low)
9  SDA      -> GPIO16   (SPI0 MOSI; also the read-back line)
10 SCL      -> GPIO15   (SPI0 SCLK)
11 CS       -> GPIO10   (active low, driven as a plain GPIO)
12 D/C      -> GPIO17   (0 = command, 1 = parameter/pixel data)
13 GND      -> GND
14 VDD      -> 3.3 V
15 LEDA     \  backlight anode/cathode -> board boost / constant-current
16 LEDK     /  rail. NOT a GPIO. GPIO12 below is only a board-side ENABLE.
17 GND      -> GND
```

IPRO7 SPI0 pad roles follow (pin % 4): 0 = MOSI, 1 = MISO, 2 = SS, 3 = SCLK. So GPIO16 = MOSI and GPIO15 = SCLK are the hardware-SPI pads, while GPIO10 and GPIO14 (SS positions) are used as plain GPIOs, and GPIO17 (MISO position) carries D/C. Only SCLK and MOSI are muxed to `GPIO_FUN_SPI`; everything else stays `GPIO_FUN_GPIO`.

The assignment matches the SDK's ILI9341 SPI driver (`ili9341_spi.h`), which uses the same LCD connector.

### 巨集 { #st7789p3_port-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `ST_SPI_CPOL` | `0` | Clock polarity: idle low (`SPI_POLARITY_LOW`). |
| `ST_SPI_CPHA` | `0` | Clock phase: sample on the first edge (`SPI_PHASE_1EDGE`). |
| `ST_PANEL_W` | `240` | Native (portrait) width in pixels. |
| `ST_PANEL_H` | `320` | Native (portrait) height in pixels. |
| `ST_SPI_ID` | `0` | SPI controller the panel is on: SPI0. |
| `ST_SPI_CLK_HZ` | `16000000u` | Default SCLK in Hz. The ST7789P3 datasheet lists every serial AC timing as "TBD", so there is no published maximum to design against. 16 MHz is the top of the IPRO7 XCLK-sourced SPI range (the SPI clock switches from XCLK to BCLK above 16 MHz), which keeps the divider on the cleaner path, and is well under what ST7789-family parts normally sustain. A full 240x320 RGB565 frame at 16 MHz takes about 77 ms. Change it at run time with [`st7789p3_set_spi_clk()`](#st7789p3_set_spi_clk) (shell: `lcd clk <hz>`). |
| `ST_PIN_MOSI` | `16` | Module SDA (FPC 9): SPI0 MOSI, also the read-back line. |
| `ST_PIN_SCLK` | `15` | Module SCL (FPC 10): SPI0 SCLK. |
| `ST_PIN_CS` | `10` | Module CS (FPC 11): chip select, active low, driven as a GPIO. |
| `ST_PIN_DC` | `17` | Module D/C (FPC 12): 0 = command, 1 = data. |
| `ST_PIN_RST` | `14` | Module RESET (FPC 8): active low. |
| `ST_PIN_BL` | `12` | Board backlight ENABLE (not LEDA/LEDK): high = on. |
| `ST_MAX_DIM` | `320` | Largest row length any orientation can ask for (landscape = 320 px), and the size of the driver's row buffer in pixels. |
| `ST_DEFAULT_DIR` | `3` | Orientation the panel comes up in, applied by [`st7789p3_init()`](#st7789p3_init) after the init sequence (which leaves MADCTL at 0 = portrait). ```text 0 = portrait 240x320   1 = landscape 320x240 2 = portrait flipped   3 = landscape flipped ``` 3 rather than 1: both are landscape, 180 degrees apart, and 1 comes out upside down with this panel's mounting. Verified on the IPRO7AI EVK. Because it is applied at init, the boot screen, a shell `lcd init` and the camera preview all start in the same orientation. |

## evk_gfx.h { #evk_gfx-h }

`#include "evk_gfx.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_gfx.h)）

Row-compositing text and overlay helpers for the ST7789P3 panel.

The panel driver has no framebuffer: the picture is streamed one row at a time out of a single row buffer. Everything here works in that model. An overlay is prepared once (position, colour, glyphs) and is then asked to contribute to row `y` while that row is being built. Coordinates are in "row space": x is the index into the row buffer and y the row number of the image being composed (panel coordinates for the direct-drawing helpers).

Pixels in a row buffer are always in WIRE order (see st7789p3_swap()), and so are the colours stored in the overlay structs. Function arguments that take a colour expect host-order RGB565 and swap it themselves.

This model is cheap enough to run beside a 10 fps camera preview, as the EVK person-detection and rock-paper-scissors examples do.

### evk_text_set { #evk_text_set }

```c
void evk_text_set(evk_text_t *t, const char *s, int scale, uint16_t fg, bool backing, int x, int y);
```

Prepare a text line for compositing.

| 參數 | 說明 |
|---|---|
| `t` | Text line to fill. |
| `s` | Text; NULL is treated as "". Truncated to [`EVK_GFX_MAX_CHARS`](#evk_gfx-h-macros) characters; see [`font5x7.h`](#font5x7-h) for the characters that draw. |
| `scale` | Integer glyph scale; values below 1 are treated as 1. |
| `fg` | Glyph colour, RGB565 in host order (stored swapped). |
| `backing` | true to draw a black box behind the glyphs. |
| `x` | Left edge of the padded box, in row space. |
| `y` | Top edge of the padded box, in row space. |

### evk_text_width { #evk_text_width }

```c
int evk_text_width(const char *s, int scale);
```

Width of the padded box `s` would occupy.

| 參數 | 說明 |
|---|---|
| `s` | Text (NULL is treated as ""); truncated as [`evk_text_set()`](#evk_text_set) does. |
| `scale` | Integer glyph scale. |

**回傳值**：Width in pixels, or 0 for an empty string.

### evk_text_height { #evk_text_height }

```c
int evk_text_height(int scale);
```

Height of a padded text box.

| 參數 | 說明 |
|---|---|
| `scale` | Integer glyph scale. |

**回傳值**：Height in pixels (`7 * scale + 2 * EVK_GFX_PAD`).

### evk_text_row { #evk_text_row }

```c
void evk_text_row(const evk_text_t *t, uint16_t *row, int w, int y);
```

Composite the part of a text line that intersects one row.

Clipped horizontally to the row; a no-op when `y` is outside the box.

| 參數 | 說明 |
|---|---|
| `t` | Text line prepared with [`evk_text_set()`](#evk_text_set). |
| `row` | Row buffer, wire-order RGB565. |
| `w` | Row buffer width in pixels. |
| `y` | Row number, in row space. |

### evk_rect_row { #evk_rect_row }

```c
void evk_rect_row(const evk_rect_t *r, uint16_t *row, int w, int y);
```

Composite the part of a rectangle outline that intersects one row.

Clipped horizontally to the row; a no-op when `y` is outside the rectangle.

| 參數 | 說明 |
|---|---|
| `r` | Rectangle. |
| `row` | Row buffer, wire-order RGB565. |
| `w` | Row buffer width in pixels. |
| `y` | Row number, in row space. |

### evk_gfx_yuyv_row { #evk_gfx_yuyv_row }

```c
void evk_gfx_yuyv_row(const uint32_t *src, uint16_t *dst, int npix, bool uv_swap, bool mirror);
```

Convert one YUYV row to RGB565 in wire order.

The source packs two pixels per 32-bit word as bytes [Y0 U Y1 V] (lowest address first) and is converted with full-range BT.601 coefficients.

| 參數 | 說明 |
|---|---|
| `src` | Source row, `npix / 2` words. |
| `dst` | Destination row, `npix` pixels. |
| `npix` | Pixel count; must be even. |
| `uv_swap` | true to treat the chroma bytes as [Y0 V Y1 U] (skin comes out blue when this is wrong). |
| `mirror` | true to write the row right-to-left (selfie view). |

### evk_gfx_draw_bar { #evk_gfx_draw_bar }

```c
void evk_gfx_draw_bar(int y0, int h, const evk_text_t *a, const evk_text_t *b, uint16_t bg);
```

Fill a band of full-width rows and composite up to two text lines onto it.

Draws rows `y0` .. `y0` + `h` - 1 across the whole panel. Does nothing if `h` is not positive or the band does not fit on the panel. Takes the panel bus lock for the whole burst.

| 參數 | 說明 |
|---|---|
| `y0` | First row, in panel coordinates. |
| `h` | Number of rows. |
| `a` | First text line (panel coordinates), or NULL. |
| `b` | Second text line (panel coordinates), or NULL. |
| `bg` | Background colour, RGB565 in host order. |

### evk_gfx_text_at { #evk_gfx_text_at }

```c
void evk_gfx_text_at(int x, int y, const char *s, int scale, uint16_t fg, uint16_t bg);
```

Draw text at a position with a solid box behind it.

The box is the padded text box, clipped to the panel. Takes the panel bus lock.

| 參數 | 說明 |
|---|---|
| `x` | Left edge of the padded box, in panel coordinates. |
| `y` | Top edge of the padded box, in panel coordinates. |
| `s` | Text (NULL or "" draws nothing). |
| `scale` | Integer glyph scale. |
| `fg` | Glyph colour, RGB565 in host order. |
| `bg` | Box colour, RGB565 in host order. |

### evk_gfx_text_centered { #evk_gfx_text_centered }

```c
void evk_gfx_text_centered(int y, const char *s, int scale, uint16_t fg, uint16_t bg);
```

Draw text horizontally centred on the panel, with a solid box behind it (see [`evk_gfx_text_at()`](#evk_gfx_text_at)).

| 參數 | 說明 |
|---|---|
| `y` | Top edge of the padded box, in panel coordinates; the box is [`evk_text_height()`](#evk_text_height) rows tall. |
| `s` | Text (NULL or "" draws nothing). |
| `scale` | Integer glyph scale. |
| `fg` | Glyph colour, RGB565 in host order. |
| `bg` | Box colour, RGB565 in host order. |

### evk_gfx_splash { #evk_gfx_splash }

```c
void evk_gfx_splash(const char *line1, const char *line2);
```

Clear the panel to black and draw two centred lines on it.

`line1` is drawn white at scale 2, `line2` grey at scale 1 below it; the pair is centred vertically. Takes the panel bus lock.

| 參數 | 說明 |
|---|---|
| `line1` | Title line, or NULL. |
| `line2` | Subtitle line, or NULL. |

### evk_text_t { #evk_text_t }

A line of text at a fixed place, in row space.

Prepare with [`evk_text_set()`](#evk_text_set), composite with [`evk_text_row()`](#evk_text_row). The fields are filled by [`evk_text_set()`](#evk_text_set); treat them as read-only.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `text` | `char[EVK_GFX_MAX_CHARS+1]` | NUL-terminated text, at most [`EVK_GFX_MAX_CHARS`](#evk_gfx-h-macros) characters. |
| `len` | `int` | Number of characters in `text`. |
| `scale` | `int` | Integer glyph scale (&gt;= 1). |
| `fg` | `uint16_t` | Glyph colour, RGB565 in wire order. |
| `backing` | `bool` | true to draw a black box behind the glyphs. |
| `x` | `int` | Left edge of the padded box, in row space. |
| `y` | `int` | Top edge of the padded box, in row space. |
| `w` | `int` | Width of the padded box in pixels (0 for empty text). |
| `h` | `int` | Height of the padded box in pixels. |

### evk_rect_t { #evk_rect_t }

An outlined rectangle, in row space, composited with [`evk_rect_row()`](#evk_rect_row).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `x1` | `int` | Left column, inclusive. |
| `y1` | `int` | Top row, inclusive. |
| `x2` | `int` | Right column, inclusive. |
| `y2` | `int` | Bottom row, inclusive. |
| `thickness` | `int` | Outline width in pixels (values below 1 draw 1). |
| `color` | `uint16_t` | Outline colour, RGB565 in wire order. |

### 巨集 { #evk_gfx-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_GFX_MAX_CHARS` | `52` | Longest text line, in characters (315 px padded at scale 1, fits a 320 px row). |
| `EVK_GFX_PAD` | `2` | Padding around a text box, in pixels. |

## font5x7.h { #font5x7-h }

`#include "font5x7.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/font5x7.h)）

Minimal 5x7 bitmap font for on-screen text: ASCII 0x20..0x5A (space, punctuation, digits, upper case).

Lower case is folded to upper case; any other character draws as a blank. Glyphs are column-major, one byte per column, bit 0 = top row and bit 6 = bottom row (the common HD44780-style 5x7 layout).

### font5x7_glyph { #font5x7_glyph }

```c
const uint8_t * font5x7_glyph(char ch);
```

Look up the glyph for a character.

| 參數 | 說明 |
|---|---|
| `ch` | Character; lower case is folded to upper case. |

**回傳值**：Pointer to [`FONT_W`](#font5x7-h-macros) column bytes; never NULL (a blank glyph for characters outside 0x20..0x5A).

### font5x7_pixel { #font5x7_pixel }

```c
bool font5x7_pixel(const uint8_t *glyph, int col, int row);
```

Test one pixel of a glyph.

| 參數 | 說明 |
|---|---|
| `glyph` | Glyph from [`font5x7_glyph()`](#font5x7_glyph). |
| `col` | Column, 0..4 (not range-checked). |
| `row` | Row, 0..6 (0 = top). |

**回傳值**：true if the pixel is set.

### 巨集 { #font5x7-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `FONT_W` | `5` | Glyph width in pixels (columns). |
| `FONT_H` | `7` | Glyph height in pixels (rows). |
| `FONT_ADVANCE` | `6` | Horizontal advance per character: glyph plus a 1-column gap. |

## evk_cam.h { #evk_cam-h }

`#include "evk_cam.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_cam.h)）

SC101IOT DVP camera into the ISP, with two outputs: LCD preview and NPU input.

- **Channel 0**: YUYV, 320x180 (letterbox) or 320x240 (crop) on the landscape panel, ping-pong buffers in PSRAM, runs continuously at the preview rate and is handed to a display task through [`evk_cam_set_frame_cb()`](#evk_cam_set_frame_cb).
- **Channel 1**: ARGB, a sensor region of interest scaled to the NPU input size (for example the central 512x512 scaled to 128x128), written into a single buffer owned by the consumer, one frame in flight, handed over through [`evk_cam_set_npu_frame_cb()`](#evk_cam_set_npu_frame_cb).

Channel 1 is gated (destination frame rate 0) from the moment a frame completes until the consumer calls [`evk_cam_npu_rearm()`](#evk_cam_npu_rearm), so the NPU never reads a buffer the ISP is still writing. The two channels are otherwise independent: the preview keeps its rate whatever the NPU is doing.

Typical sequence: [`evk_begin()`](#evk_begin), optionally [`evk_cam_set_npu_input()`](#evk_cam_set_npu_input) and [`evk_cam_set_npu_frame_cb()`](#evk_cam_set_npu_frame_cb), [`evk_cam_set_frame_cb()`](#evk_cam_set_frame_cb), then [`evk_cam_start()`](#evk_cam_start); [`evk_cam_stop()`](#evk_cam_stop) when done. The first 6 frames after each start are discarded while auto-exposure and white balance settle.

[`evk_cam_start()`](#evk_cam_start) and [`evk_cam_stop()`](#evk_cam_stop) enforce the required order: the sensor is held in reset while the multimedia blocks are reset and while the ISP is torn down, and the ISP 3A (auto-exposure / auto-white-balance) engine is never stopped, so the next start runs 3A again.

Board wiring, and where this board differs from the SDK's generic EVB camera setup, is described in [`evk_cam_port.h`](#evk_cam_port-h).

### evk_cam_probe { #evk_cam_probe }

```c
int evk_cam_probe(void);
```

Bring up SCCB, MCLK (24 MHz), the reset line and the DVP pins, then probe for the sensor.

Pulses the sensor reset, then scans SCCB up to 5 times, 200 ms apart. Safe to call repeatedly; the probe runs again each time. Does not start the ISP. [`evk_cam_start()`](#evk_cam_start) calls it itself.

**回傳值**：[`EVK_CAM_OK`](#evk_cam-h-macros), or [`EVK_CAM_ERR_NODEV`](#evk_cam-h-macros) if no sensor answered.

!!! note "注意"
    Blocking; call from task context. When no sensor answers it takes at least 1 s.

### evk_cam_set_npu_input { #evk_cam_set_npu_input }

```c
void evk_cam_set_npu_input(const evk_cam_npu_input_t *in);
```

Set the channel-1 geometry and buffer.

The settings take effect on the next [`evk_cam_start()`](#evk_cam_start). Channel 1 is enabled only when `addr`, `out_w` and `out_h` are all non-zero; the default (`addr` == 0) leaves it off.

| 參數 | 說明 |
|---|---|
| `in` | Configuration to copy, or NULL to clear it (channel 1 off). |

### evk_cam_set_npu_frame_cb { #evk_cam_set_npu_frame_cb }

```c
void evk_cam_set_npu_frame_cb(evk_cam_npu_frame_cb_t cb, void *arg);
```

Register the channel-1 (NPU input) frame callback.

| 參數 | 說明 |
|---|---|
| `cb` | Callback, or NULL to stop delivering frames. |
| `arg` | Passed back to `cb` unchanged. |

### evk_cam_start { #evk_cam_start }

```c
int evk_cam_start(void);
```

Start the ISP pipeline.

Holds the sensor in reset while the multimedia blocks are reset, calls [`evk_cam_probe()`](#evk_cam_probe), sets the panel to the [`evk_cam_set_rot()`](#evk_cam_set_rot) orientation and clears it, allocates the preview buffers in PSRAM and starts the ISP. Channel 1 is enabled only if [`evk_cam_set_npu_input()`](#evk_cam_set_npu_input) gave it a buffer; without one the camera is a plain preview. Clears the counters and re-enables the NPU feed ([`evk_cam_npu_set_enabled()`](#evk_cam_npu_set_enabled)) whenever channel 1 has a buffer. Returns [`EVK_CAM_OK`](#evk_cam-h-macros) at once if the pipeline is already running.

| 回傳碼 | 說明 |
|---|---|
| `EVK_CAM_OK` | Running. |
| `EVK_CAM_ERR_STATE` | The panel is not initialised (call [`evk_begin()`](#evk_begin)). |
| `EVK_CAM_ERR_NODEV` | No sensor answered on SCCB. |
| `EVK_CAM_ERR_NOMEM` | The preview frame buffer could not be allocated. |

!!! note "注意"
    Blocking; call from task context.

### evk_cam_stop { #evk_cam_stop }

```c
void evk_cam_stop(void);
```

Stop the pipeline and hold the sensor in reset.

The sensor is put in reset even when the pipeline is not running, so that a sensor left configured does not keep streaming.

### evk_cam_is_running { #evk_cam_is_running }

```c
bool evk_cam_is_running(void);
```

Report whether the pipeline is running.

**回傳值**：true between a successful [`evk_cam_start()`](#evk_cam_start) and [`evk_cam_stop()`](#evk_cam_stop).

### evk_cam_set_frame_cb { #evk_cam_set_frame_cb }

```c
void evk_cam_set_frame_cb(evk_cam_frame_cb_t cb, void *arg);
```

Register the channel-0 (preview) frame callback.

| 參數 | 說明 |
|---|---|
| `cb` | Callback, or NULL to stop delivering frames. |
| `arg` | Passed back to `cb` unchanged. |

### evk_cam_get_geometry { #evk_cam_get_geometry }

```c
void evk_cam_get_geometry(evk_cam_geometry_t *out);
```

Read the preview geometry computed by the last [`evk_cam_start()`](#evk_cam_start).

| 參數 | 說明 |
|---|---|
| `out` | Destination; ignored if NULL. |

### evk_cam_get_stats { #evk_cam_get_stats }

```c
void evk_cam_get_stats(evk_cam_stats_t *out);
```

Read the pipeline counters.

| 參數 | 說明 |
|---|---|
| `out` | Destination; ignored if NULL. |

### evk_cam_sensor_name { #evk_cam_sensor_name }

```c
const char * evk_cam_sensor_name(void);
```

Name of the sensor found by the last successful probe.

**回傳值**：Sensor name string, or NULL before a sensor has been found.

### evk_cam_sensor_addr { #evk_cam_sensor_addr }

```c
uint8_t evk_cam_sensor_addr(void);
```

7-bit SCCB address of the sensor found by the last successful probe.

**回傳值**：Sensor address, or 0 before a sensor has been found.

### evk_cam_sensor_size { #evk_cam_sensor_size }

```c
void evk_cam_sensor_size(uint16_t *w, uint16_t *h);
```

Sensor output size in pixels.

Before a sensor has been found this reports [`EVK_CAM_SENSOR_W`](#evk_cam_port-h-macros) x [`EVK_CAM_SENSOR_H`](#evk_cam_port-h-macros).

| 參數 | 說明 |
|---|---|
| `w` | Width; ignored if NULL. |
| `h` | Height; ignored if NULL. |

### evk_cam_set_fit { #evk_cam_set_fit }

```c
int evk_cam_set_fit(int fit);
```

Select the preview aspect handling; takes effect on the next [`evk_cam_start()`](#evk_cam_start).

| 參數 | 說明 |
|---|---|
| `fit` | [`EVK_CAM_FIT_LETTERBOX`](#evk_cam-h-macros) or [`EVK_CAM_FIT_CROP`](#evk_cam-h-macros). |

**回傳值**：[`EVK_CAM_OK`](#evk_cam-h-macros), or [`EVK_CAM_ERR_PARAM`](#evk_cam-h-macros) for any other value.

### evk_cam_get_fit { #evk_cam_get_fit }

```c
int evk_cam_get_fit(void);
```

Read the preview aspect handling.

**回傳值**：[`EVK_CAM_FIT_LETTERBOX`](#evk_cam-h-macros) or [`EVK_CAM_FIT_CROP`](#evk_cam-h-macros).

### evk_cam_set_fps { #evk_cam_set_fps }

```c
int evk_cam_set_fps(int fps);
```

Set the preview (channel 0) frame rate.

Applied immediately when the pipeline is running.

| 參數 | 說明 |
|---|---|
| `fps` | Frames per second, 1..30 (default 10). |

**回傳值**：[`EVK_CAM_OK`](#evk_cam-h-macros), or [`EVK_CAM_ERR_PARAM`](#evk_cam-h-macros) if out of range.

### evk_cam_get_fps { #evk_cam_get_fps }

```c
int evk_cam_get_fps(void);
```

Read the preview frame rate.

**回傳值**：Frames per second.

### evk_cam_set_rot { #evk_cam_set_rot }

```c
int evk_cam_set_rot(int rot);
```

Set the panel orientation used by the preview; takes effect on the next [`evk_cam_start()`](#evk_cam_start).

| 參數 | 說明 |
|---|---|
| `rot` | 0..3 as for [`st7789p3_set_dir()`](#st7789p3_set_dir); 1 and 3 are landscape (default [`ST_DEFAULT_DIR`](#st7789p3_port-h-macros)). |

**回傳值**：[`EVK_CAM_OK`](#evk_cam-h-macros), or [`EVK_CAM_ERR_PARAM`](#evk_cam-h-macros) if out of range.

### evk_cam_get_rot { #evk_cam_get_rot }

```c
int evk_cam_get_rot(void);
```

Read the preview panel orientation.

**回傳值**：0..3.

### evk_cam_npu_set_enabled { #evk_cam_npu_set_enabled }

```c
void evk_cam_npu_set_enabled(bool on);
```

Turn the NPU feed on or off.

The feed is on by default whenever channel 1 is configured. Off gates channel 1 and leaves the preview alone; on lets the next frame through (as [`evk_cam_npu_rearm()`](#evk_cam_npu_rearm)).

| 參數 | 說明 |
|---|---|
| `on` | true to feed the NPU, false to stop. |

### evk_cam_npu_enabled { #evk_cam_npu_enabled }

```c
bool evk_cam_npu_enabled(void);
```

Report whether the NPU feed is enabled.

**回傳值**：true if channel-1 frames are being delivered.

### evk_cam_npu_rearm { #evk_cam_npu_rearm }

```c
void evk_cam_npu_rearm(void);
```

Open channel 1 for one more frame.

Call it when the NPU is done with the previous frame (one frame in flight). Has no effect unless the pipeline is running, channel 1 is configured, the feed is enabled and the start-up frames have passed.

### evk_cam_reset_pin { #evk_cam_reset_pin }

```c
void evk_cam_reset_pin(int level);
```

Drive the sensor RESET line directly, for hardware checks.

| 參數 | 說明 |
|---|---|
| `level` | 0 asserts reset (GPIO35 low); non-zero releases it. |

### evk_cam_geometry_t { #evk_cam_geometry_t }

Where the preview image sits on the panel and which part of the sensor it shows.

Filled by [`evk_cam_get_geometry()`](#evk_cam_get_geometry) after [`evk_cam_start()`](#evk_cam_start); a UI uses it to map sensor-pixel rectangles (such as the NPU ROI) onto the preview. All values are in pixels.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `panel_w` | `uint16_t` | Panel width in the chosen orientation. |
| `panel_h` | `uint16_t` | Panel height in the chosen orientation. |
| `img_w` | `uint16_t` | Preview image (channel-0 frame) width. |
| `img_h` | `uint16_t` | Preview image (channel-0 frame) height. |
| `ox` | `uint16_t` | Left edge of the preview image on the panel. |
| `oy` | `uint16_t` | Top edge of the preview image on the panel. |
| `crop_x` | `uint16_t` | Left edge of the sensor window channel 0 is scaled from. |
| `crop_y` | `uint16_t` | Top edge of the sensor window channel 0 is scaled from. |
| `crop_w` | `uint16_t` | Width of the sensor window channel 0 is scaled from. |
| `crop_h` | `uint16_t` | Height of the sensor window channel 0 is scaled from. |
| `roi_x` | `uint16_t` | Left edge of the sensor window channel 1 (NPU) is scaled from. |
| `roi_y` | `uint16_t` | Top edge of the sensor window channel 1 is scaled from. |
| `roi_w` | `uint16_t` | Width of the sensor window channel 1 (NPU) is scaled from. |
| `roi_h` | `uint16_t` | Height of the sensor window channel 1 is scaled from. |

### evk_cam_npu_input_t { #evk_cam_npu_input_t }

Channel-1 (NPU input) configuration, passed to [`evk_cam_set_npu_input()`](#evk_cam_set_npu_input) before [`evk_cam_start()`](#evk_cam_start).

The ROI is in sensor pixels (1280x720).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `addr` | `uint32_t` | Buffer the ISP writes ARGB into, `out_w * out_h * 4` bytes; 0 = channel 1 off. |
| `out_w` | `uint16_t` | Scaler output width in pixels, equal to the model input width. |
| `out_h` | `uint16_t` | Scaler output height in pixels, equal to the model input height. |
| `roi_x` | `uint16_t` | Left edge of the sensor window to scale from. |
| `roi_y` | `uint16_t` | Top edge of the sensor window to scale from. |
| `roi_w` | `uint16_t` | Width of the sensor window to scale from. |
| `roi_h` | `uint16_t` | Height of the sensor window to scale from. |

### evk_cam_stats_t { #evk_cam_stats_t }

Pipeline counters, read with [`evk_cam_get_stats()`](#evk_cam_get_stats).

All are cleared by [`evk_cam_start()`](#evk_cam_start).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `frames0` | `uint32_t` | Channel-0 completions, including the discarded start-up frames. |
| `frames1` | `uint32_t` | Channel-1 completions. |
| `pushed` | `uint32_t` | Channel-1 frames the NPU callback accepted (returned 0). |
| `dropped` | `uint32_t` | Channel-0 frames superseded before display. Not updated by this library; stays 0. |
| `fifo_err` | `uint32_t` | ISP FIFO overwrite events (`ISP_HAL_INT_FIFO_OVERWRITE`). |
| `vsync_err` | `uint32_t` | ISP VSYNC count errors (`ISP_HAL_INT_VSYNC_CNT_ERROR`). |
| `hsync_err` | `uint32_t` | ISP HSYNC count errors (`ISP_HAL_INT_HSYNC_CNT_ERROR`). |

### 型別定義 { #evk_cam-h-typedefs }

| 名稱 | 定義 | 說明 |
|---|---|---|
| `evk_cam_frame_cb_t` | `typedef void(*) evk_cam_frame_cb_t(uint32_t yuyv_addr, void *arg)` | New channel-0 (preview) frame callback. Called from the ISP interrupt for every completed preview frame once the start-up frames have been discarded. Record the address and wake a task; do not draw from the callback. |
| `evk_cam_npu_frame_cb_t` | `typedef int(*) evk_cam_npu_frame_cb_t(uint32_t argb_addr, void *arg)` | New channel-1 (NPU input) frame callback. Called from the ISP interrupt with channel 1 already gated. Whatever the return value, channel 1 stays gated until [`evk_cam_npu_rearm()`](#evk_cam_npu_rearm) is called. |

### 巨集 { #evk_cam-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_CAM_OK` | `0` | Success. |
| `EVK_CAM_ERR_PARAM` | `-1` | Argument out of range. |
| `EVK_CAM_ERR_NODEV` | `-2` | No sensor answered on SCCB. |
| `EVK_CAM_ERR_NOMEM` | `-3` | PSRAM frame buffer allocation failed. |
| `EVK_CAM_ERR_STATE` | `-4` | Wrong state for this call (panel not initialised). |
| `EVK_CAM_FIT_LETTERBOX` | `0` | Whole frame to 320x180 with black bars (default). |
| `EVK_CAM_FIT_CROP` | `1` | Centre 960x720 to 320x240, fills the screen. |

## evk_cam_port.h { #evk_cam_port-h }

`#include "evk_cam_port.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_cam_port.h)）

Board wiring for the SC101IOT DVP camera on the IPRO7AI EVK.

Taken from the board schematic (the IPRO7AI module U5 and the CN5 "Camera" connector), not from the SDK's generic EVB defaults; two of the assignments differ from those defaults.

Sensor: SmartSens SC101IOT, 1280x720, SCCB address 0x68, PCLK 72 MHz, total 1600x750. Driver: `components/sensor/sc101iot.c` (720p is selected there at compile time by `#define resolution_720P 1`).

CN5 = FH34SRJ-24S-0.5SH, 24-pin 0.5 mm FPC:

```text
1  AVDD2V8    2.8 V analog          (C34 4.7uF + C35 100nF)
2  DOVDD1V8   digital I/O, 1.8 V on V1 (sensor spec 2.7-2.9 V)  (C32 4.7uF + C33 100nF)
3  DVDD1V8    digital core, 1.8 V on V1
4  MCLK   <- GPIO41  DVP_REF_CLK    (GPIO_FUN_CAM_MISC + GLB_Set_CAM_CLK)
5  PCLK   -> GPIO38
6  VSYNC  -> GPIO39
7  AGND
8  D0        NOT CONNECTED  (see "8 data lines" below)
9  D1        NOT CONNECTED
10 DGND1
11 D2     -> GPIO0   DVP_D0
12 D3     -> GPIO1   DVP_D1
13 DGND2
14 D4     -> GPIO2   DVP_D2
15 D5     -> GPIO3   DVP_D3
16 DGND3
17 D6     -> GPIO4   DVP_D4
18 D7     -> GPIO5   DVP_D5
19 D8     -> GPIO6   DVP_D6
20 D9     -> GPIO7   DVP_D7
21 HSYNC  -> GPIO40
22 SCL    <- GPIO36
23 SDA    <> GPIO37
24 RESET  <- GPIO35 through Q3, active low
25 GND1  26 GND2
```

**Three things this board does differently**

1. *The camera bank has its own supply, and V1 powers the sensor below spec.* On IPRO7 the VDDIO_1 bank covers GPIO0-9 and GPIO36-41 (exactly the camera pins), and the SoC brings that bank out on its own supply pin (U5 pin 36, VDDIO1). The LCD pins (GPIO10-17) sit in VDDIO_2 at 3.3 V. VDDIO1 also powers the in-package flash (minimum about 2.7 V), so it cannot be 1.8 V; on V1 it is fed 2.8 V (J6 pin 3 wired to pin 7, 2V8_CAM). The SC101IOT wants DOVDD 2.7-2.9 V, but V1 feeds its DOVDD and DVDD from 1V8_SOC (pins 2/3 above), so the 2.8 V DVP/SCCB lines drive a sensor powered at 1.8 V. This operates on the IPRO7AI EVK but is outside the sensor's datasheet range.
1. *Reset is level-shifted, not direct.* GPIO35 is in the VDDIO_3 bank (GPIO20-35) at 3.3 V, so it cannot drive a 1.8 V input. Q3 (MSL2310-N N-MOSFET, gate on DOVDD1V8, drain on the 3.3 V side, source on the 1.8 V side) with R56 4.7k pulling up to DOVDD1V8 translates it. R55, the 3.3 V-side pull-up, is not fitted, so the link is one-way: the SoC drives GPIO35 push-pull and the sensor sees the same polarity at 1.8 V. Drive GPIO35 LOW to assert reset, HIGH to release it. When GPIO35 is high-impedance, R56 releases reset.
1. *There is no PWDN pin.* The SDK's generic EVB camera code drives GPIO34 as sensor power-down and GPIO35 as reset. On this board GPIO34 is SD_DET (micro-SD card detect), so only reset exists. Do not drive GPIO34 from camera code.

**8 data lines out of the sensor's 10**

The sensor's D0/D1 are left unconnected and its D2..D9 land on the SoC's DVP_D0..D7. That is the standard MSB-aligned 8-bit tap on a 10-bit output: the two least-significant bits are discarded, so the bus carries the top 8 bits at full scale and no shifting or scaling is needed in firmware.

**SCCB pin naming**

On IPRO7 the I2C0 role of a pad is fixed by its parity: EVEN pin = SCL, ODD pin = SDA. GPIO36 is therefore SCL and GPIO37 is SDA, as wired here. `components/sensor/sccb.h` labels the two macros the other way round for the IPRO7 EVB configuration; this has no effect, because `SCCB_Init()` only muxes both pins to `GPIO_FUN_I2C` and nothing depends on which macro names which pin.

### 巨集 { #evk_cam_port-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_CAM_PIN_SCL` | `36` | SCCB clock (I2C0 SCL), CN5 pin 22. |
| `EVK_CAM_PIN_SDA` | `37` | SCCB data (I2C0 SDA), CN5 pin 23. |
| `EVK_CAM_PIN_D0` | `0` | DVP_D0 (sensor D2); DVP_D0..D7 are GPIO0..GPIO7. |
| `EVK_CAM_PIN_PCLK` | `38` | DVP pixel clock from the sensor. |
| `EVK_CAM_PIN_VSYNC` | `39` | DVP vertical sync from the sensor. |
| `EVK_CAM_PIN_HSYNC` | `40` | DVP horizontal sync from the sensor. |
| `EVK_CAM_PIN_MCLK` | `41` | DVP_REF_CLK: 24 MHz sensor master clock out. |
| `EVK_CAM_PIN_RST` | `35` | Sensor RESET, active low, via the Q3 level shifter. |
| `EVK_CAM_SENSOR_W` | `1280` | Sensor output width in pixels. |
| `EVK_CAM_SENSOR_H` | `720` | Sensor output height in pixels. |
| `EVK_CAM_SENSOR_NAME` | `"SC101IOT"` | Sensor name passed to the ISP 3A engine. |

## evk_mic.h { #evk_mic-h }

`#include "evk_mic.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_mic.h)）

PDM microphone capture (IM69D129 on GPIO18/19 through the AUADC).

Frames of [`EVK_MIC_FRAME_SAMPLES`](#evk_audio_port-h-macros) mono int16 samples (20 ms at the nominal 16 kHz) arrive by DMA into a non-cached OCRAM ping-pong buffer; the completion interrupt copies each one into a FreeRTOS stream buffer that holds 8 frames (160 ms), and [`evk_mic_read()`](#evk_mic_read) hands them to the caller. The reader is expected to keep up: when the stream buffer is full the newest frame is dropped and counted in `evk_mic_stats_t::dropped`. The first 5 frames after each start are discarded while the microphone settles.

`hal_auadc_pdm_init()` may only run once per boot (re-initialising it breaks DMA on later calls), so the hardware is configured on the first [`evk_mic_start()`](#evk_mic_start) and later starts and stops only gate the AUADC.

Everything here is integer arithmetic, including the digital-gain register write (the HAL's floating-point gain entry point is not used), because the FreeRTOS port on IPRO7 does not save the FPU registers across a context switch.

### evk_mic_start { #evk_mic_start }

```c
int evk_mic_start(void);
```

Start capture.

On first use, allocates the stream buffer, hands GPIO18/19 back from the always-on block to the digital pad mux and configures the AUADC for PDM at [`EVK_MIC_RATE_HZ`](#evk_audio_port-h-macros). Every start empties the stream buffer and discards the first 5 frames. Returns [`EVK_MIC_OK`](#evk_mic-h-macros) at once if already capturing.

| 回傳碼 | 說明 |
|---|---|
| `EVK_MIC_OK` | Capturing. |
| `EVK_MIC_ERR_NOMEM` | The stream buffer could not be allocated. |
| `EVK_MIC_ERR_HW` | The AUADC could not be initialised or started. |

### evk_mic_stop { #evk_mic_stop }

```c
void evk_mic_stop(void);
```

Stop capture (gates the AUADC; the configuration is kept).

### evk_mic_running { #evk_mic_running }

```c
bool evk_mic_running(void);
```

Report whether capture is running.

**回傳值**：true between a successful [`evk_mic_start()`](#evk_mic_start) and [`evk_mic_stop()`](#evk_mic_stop).

### evk_mic_read { #evk_mic_read }

```c
uint32_t evk_mic_read(int16_t *dst, uint32_t timeout_ms);
```

Wait for and copy one frame of samples.

| 參數 | 說明 |
|---|---|
| `dst` | Buffer for [`EVK_MIC_FRAME_SAMPLES`](#evk_audio_port-h-macros) int16 samples. |
| `timeout_ms` | Longest time to wait for a frame, in milliseconds. |

**回傳值**：Samples copied ([`EVK_MIC_FRAME_SAMPLES`](#evk_audio_port-h-macros)), or 0 on timeout, if `dst` is NULL or if capture has never been started.

!!! note "注意"
    Blocking; call from task context.

### evk_mic_flush { #evk_mic_flush }

```c
void evk_mic_flush(void);
```

Drop whatever is queued.

Call after a pause, before reading again.

### evk_mic_set_gain_db { #evk_mic_set_gain_db }

```c
int evk_mic_set_gain_db(int db);
```

Set the AUADC digital gain.

Applied immediately once the AUADC has been configured (after the first [`evk_mic_start()`](#evk_mic_start)); before that it is stored and applied at configuration.

| 參數 | 說明 |
|---|---|
| `db` | Gain in whole dB, 0..[`EVK_MIC_DIGITAL_GAIN_DB`](#evk_audio_port-h-macros) (default [`EVK_MIC_DIGITAL_GAIN_DB`](#evk_audio_port-h-macros)). |

**回傳值**：[`EVK_MIC_OK`](#evk_mic-h-macros), or [`EVK_MIC_ERR_PARAM`](#evk_mic-h-macros) if out of range.

### evk_mic_get_gain_db { #evk_mic_get_gain_db }

```c
int evk_mic_get_gain_db(void);
```

Read the AUADC digital gain.

**回傳值**：Gain in whole dB.

### evk_mic_real_rate { #evk_mic_real_rate }

```c
uint32_t evk_mic_real_rate(void);
```

Sample rate the AUADC really produces for the nominal [`EVK_MIC_RATE_HZ`](#evk_audio_port-h-macros).

**回傳值**：Rate in Hz (about 15875).

### evk_mic_get_stats { #evk_mic_get_stats }

```c
void evk_mic_get_stats(evk_mic_stats_t *out);
```

Read the capture counters.

| 參數 | 說明 |
|---|---|
| `out` | Destination; ignored if NULL. |

### evk_mic_level { #evk_mic_level }

```c
void evk_mic_level(const int16_t *pcm, uint32_t n, uint16_t *peak, uint16_t *rms);
```

Peak and RMS of a block of samples, integer only (same as [`evk_pcm_level()`](#evk_pcm_level)).

| 參數 | 說明 |
|---|---|
| `pcm` | Samples. |
| `n` | Number of samples. |
| `peak` | max(\|sample\|), 0..32768; ignored if NULL. |
| `rms` | sqrt(mean(sample^2)), 0..32767; ignored if NULL. |

### evk_mic_dbfs_x10 { #evk_mic_dbfs_x10 }

```c
int evk_mic_dbfs_x10(uint32_t v);
```

Convert a level to dBFS, integer only (same as [`evk_pcm_dbfs_x10()`](#evk_pcm_dbfs_x10)).

| 參數 | 說明 |
|---|---|
| `v` | Level on a 0..32768 scale (32768 = full scale). |

**回傳值**：20*log10(v/32768) in tenths of a dB; -1200 for 0.

### evk_mic_stats_t { #evk_mic_stats_t }

Capture counters, read with [`evk_mic_get_stats()`](#evk_mic_get_stats).

Counted since boot.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `isr_frames` | `uint32_t` | DMA frame completions, counted even when not capturing. |
| `delivered` | `uint32_t` | Frames queued for the reader. |
| `dropped` | `uint32_t` | Frames lost because the stream buffer was full. |
| `discarded` | `uint32_t` | Start-up frames thrown away while the mic settles. |

### 巨集 { #evk_mic-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_MIC_OK` | `0` | Success. |
| `EVK_MIC_ERR_PARAM` | `-1` | Argument out of range. |
| `EVK_MIC_ERR_NOMEM` | `-2` | The stream buffer could not be allocated. |
| `EVK_MIC_ERR_HW` | `-3` | AUADC / PDM initialisation or start failed. |

## evk_spk.h { #evk_spk-h }

`#include "evk_spk.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_spk.h)）

Speaker: on-chip DAC (GPIO23) into the TPA2037D1 class-D amplifier.

A thin wrapper over the `components/audio` DAC sink that opens it with this board's amplifier-enable polarity, applies a software volume in Q12 (integer, no FPU), and offers a tone generator for self-test. Audio is mono int16.

The DAC's native rate is 32 kHz ([`EVK_SPK_NATIVE_RATE_HZ`](#evk_audio_port-h-macros)). Opening at another rate (16 kHz for a microphone recording, for example) goes through the sink's linear resampler. Writes block until the DMA ring has room, so a producer is paced by the DAC. Only one stream can be open at a time.

### evk_spk_open { #evk_spk_open }

```c
int evk_spk_open(uint32_t rate_hz, uint8_t ring_count, uint16_t ring_ms);
```

Open the DAC for streaming and switch the amplifier on.

| 參數 | 說明 |
|---|---|
| `rate_hz` | Sample rate of the samples that will be written, in Hz, 8000..48000. |
| `ring_count` | Segments in the DMA ring (0 = 4). |
| `ring_ms` | Milliseconds per segment (0 = 20). Deeper rings tolerate a producer that is sometimes late; shallower ones start playing sooner. |

| 回傳碼 | 說明 |
|---|---|
| `EVK_SPK_OK` | Open. |
| `EVK_SPK_ERR_STATE` | Already open. |
| `EVK_SPK_ERR_PARAM` | `rate_hz` out of range. |
| `EVK_SPK_ERR_HW` | The audio sink could not be created or started. |

### evk_spk_close { #evk_spk_close }

```c
void evk_spk_close(void);
```

Stop and close the DAC stream.

Does nothing if it is not open.

### evk_spk_is_open { #evk_spk_is_open }

```c
bool evk_spk_is_open(void);
```

Report whether a stream is open.

**回傳值**：true between a successful [`evk_spk_open()`](#evk_spk_open) and [`evk_spk_close()`](#evk_spk_close).

### evk_spk_write { #evk_spk_write }

```c
int evk_spk_write(const int16_t *pcm, uint32_t n);
```

Write samples with the current volume applied.

| 參數 | 說明 |
|---|---|
| `pcm` | Samples at the rate given to [`evk_spk_open()`](#evk_spk_open). |
| `n` | Number of samples. |

| 回傳碼 | 說明 |
|---|---|
| `EVK_SPK_OK` | All samples queued. |
| `EVK_SPK_ERR_STATE` | No stream is open. |
| `EVK_SPK_ERR_PARAM` | `pcm` is NULL. |
| `EVK_SPK_ERR_HW` | The sink rejected a write. |

!!! note "注意"
    Blocks until the DMA ring has room; call from task context.

### evk_spk_write_silence { #evk_spk_write_silence }

```c
int evk_spk_write_silence(uint32_t n);
```

Write silence, to keep the ring fed while idle.

| 參數 | 說明 |
|---|---|
| `n` | Number of samples, at the rate given to [`evk_spk_open()`](#evk_spk_open). |

| 回傳碼 | 說明 |
|---|---|
| `EVK_SPK_OK` | All samples queued. |
| `EVK_SPK_ERR_STATE` | No stream is open. |
| `EVK_SPK_ERR_HW` | The sink rejected a write. |

!!! note "注意"
    Blocks until the DMA ring has room; call from task context.

### evk_spk_written { #evk_spk_written }

```c
uint32_t evk_spk_written(void);
```

Samples written since [`evk_spk_open()`](#evk_spk_open).

Counts the samples passed to [`evk_spk_write()`](#evk_spk_write) and [`evk_spk_write_silence()`](#evk_spk_write_silence), at the rate given to [`evk_spk_open()`](#evk_spk_open).

**回傳值**：Sample count.

### evk_spk_played { #evk_spk_played }

```c
uint32_t evk_spk_played(void);
```

Samples the DAC has played since [`evk_spk_open()`](#evk_spk_open).

Counted per completed DMA segment at the DAC's 32 kHz rate, so it reflects the hardware's real rate. When the stream was opened at 32000 Hz, `evk_spk_written() - evk_spk_played()` is what the sink still holds.

**回傳值**：Sample count, or 0 when no stream is open.

### evk_spk_set_volume { #evk_spk_set_volume }

```c
int evk_spk_set_volume(int pct);
```

Set the software volume; applies to the next write.

| 參數 | 說明 |
|---|---|
| `pct` | Volume in percent, 0..[`EVK_SPK_VOLUME_MAX`](#evk_spk-h-macros) (default 100). |

**回傳值**：[`EVK_SPK_OK`](#evk_spk-h-macros), or [`EVK_SPK_ERR_PARAM`](#evk_spk-h-macros) if out of range.

### evk_spk_get_volume { #evk_spk_get_volume }

```c
int evk_spk_get_volume(void);
```

Read the software volume.

**回傳值**：Volume in percent.

### evk_spk_enable { #evk_spk_enable }

```c
void evk_spk_enable(int on);
```

Drive the amplifier enable (GPIO22, active high) directly.

The DAC sink drives it on start and stop; this is for hardware checks and for keeping the amplifier off while nothing plays.

| 參數 | 說明 |
|---|---|
| `on` | Non-zero to enable the amplifier, 0 to disable it. |

### evk_spk_tone { #evk_spk_tone }

```c
int evk_spk_tone(uint32_t freq_hz, uint32_t ms, uint32_t amp_pct);
```

Play a sine tone at the DAC's native rate.

Opens the DAC at [`EVK_SPK_NATIVE_RATE_HZ`](#evk_audio_port-h-macros), plays the tone with the current volume applied, adds 80 ms of silence so the ring drains, and closes the DAC again.

| 參數 | 說明 |
|---|---|
| `freq_hz` | Tone frequency in Hz, 1..16000. |
| `ms` | Duration in milliseconds. |
| `amp_pct` | Amplitude in percent of full scale; values above 100 are treated as 100. |

| 回傳碼 | 說明 |
|---|---|
| `EVK_SPK_OK` | Played. |
| `EVK_SPK_ERR_PARAM` | `freq_hz` out of range. |
| `EVK_SPK_ERR_STATE` | A stream is already open. |
| `EVK_SPK_ERR_HW` | The sink could not be opened or rejected a write. |

!!! note "注意"
    Blocking for the length of the tone; call from task context.

### 巨集 { #evk_spk-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_SPK_OK` | `0` | Success. |
| `EVK_SPK_ERR_PARAM` | `-1` | Argument out of range or NULL. |
| `EVK_SPK_ERR_STATE` | `-2` | Wrong state: not open, or already open. |
| `EVK_SPK_ERR_HW` | `-3` | The audio sink failed to create, start or write. |
| `EVK_SPK_VOLUME_MAX` | `200` | Highest volume in percent; 100 = unity, 200 = +6 dB. |

## evk_audio_port.h { #evk_audio_port-h }

`#include "evk_audio_port.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_audio_port.h)）

Speaker (DAC and class-D amplifier) and PDM microphone wiring on the IPRO7AI EVK sub-board.

**Speaker**

```text
GPIO23  SPK_DAC_OUT -> R27 470R / C20 3.3nF (RC, fc ~102 kHz) -> C19 2.2uF
                    -> R26 4.7k -> TPA2037D1 IN+ (single-ended, IN- AC-grounded)
GPIO22  SPK_EN      -> 1k / 10k divider -> TPA2037D1 EN
PA_VDD  <- VBAT     (the amplifier runs off the battery rail, not 3V3)
```

SPK_EN is ACTIVE HIGH: R25 pulls EN to ground, so the amplifier is off until GPIO22 is driven high. GPIO22 is also DAC channel B, so using it as the enable makes the board mono.

The `components/audio` DAC backend drives the enable with the polarity the board header declares (`BOARD_SPK_EN_ACTIVE` = 1 on this board); evk_spk passes the polarity explicitly as well, so it does not depend on which board header the application was compiled against.

**PDM microphone**

```text
GPIO18  DMIC_CLK -> IM69D129FV01 CLK    (even pin = PDM_CLK)
GPIO19  DMIC_DAT <- IM69D129FV01 DATA   (odd pin  = PDM_DIN)
```

SELECT is tied to GND, so the microphone drives the LEFT slot. Its VDD is DMIC_1V8.

GPIO18/19 are the two highest always-on (AON) pads and also the 32.768 kHz crystal pins. Out of reset the AON block owns them with their input receivers off (`HBN_PAD_CTRL_2` `en_aon_ctrl_msb` = 0b11, `ie_smt_msb` = 0), so muxing them to PDM has no effect until they are handed back to the digital pad mux. [`evk_mic_start()`](#evk_mic_start) does this on first use. Verified on the IPRO7AI EVK.

**Sample rates: neither side is exactly 16 kHz**

- PDM capture: 2.032 MHz / 128 = 15875 Hz for a nominal 16000 Hz.
- DAC: root clock ~31.88 MHz; the nominal 32000 Hz is ~31985 Hz.

Nothing in this library needs sample-accurate synchronisation; a recording played back is under 1 % off in pitch.

### 巨集 { #evk_audio_port-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_SPK_PIN_DAC` | `23` | SPK_DAC_OUT: DAC channel A analogue out to the amp. |
| `EVK_SPK_PIN_EN` | `22` | SPK_EN: TPA2037D1 enable, active high. |
| `EVK_SPK_EN_ACTIVE` | `1` | Level on [`EVK_SPK_PIN_EN`](#evk_audio_port-h-macros) that turns the amp on. |
| `EVK_MIC_PIN_CLK` | `18` | DMIC_CLK: PDM clock out (even pin = PDM_CLK). |
| `EVK_MIC_PIN_DAT` | `19` | DMIC_DAT: PDM data in (odd pin = PDM_DIN). |
| `EVK_MIC_PDM_CHANNEL` | `0` | PDM slot the mic drives: 0 = left (SELECT to GND). |
| `EVK_MIC_RATE_HZ` | `16000` | Nominal capture rate in Hz; real is ~15875 Hz. |
| `EVK_MIC_FRAME_MS` | `20` | Capture frame length in milliseconds. |
| `EVK_MIC_FRAME_SAMPLES` | `(EVK_MIC_RATE_HZ / 1000 * EVK_MIC_FRA...` | 320 samples. |
| `EVK_SPK_NATIVE_RATE_HZ` | `32000` | DAC native rate in Hz; other rates go through the `components/audio` linear resampler. |
| `EVK_MIC_DIGITAL_GAIN_DB` | `18` | AUADC digital gain in dB applied by default, and the maximum [`evk_mic_set_gain_db()`](#evk_mic_set_gain_db) accepts. +18 dB is the hardware maximum and the only gain stage that improves resolution (it is applied before the 16-bit truncation). Normal speech at arm's length then peaks around -36 dBFS on this board. |

## evk_pcm.h { #evk_pcm-h }

`#include "evk_pcm.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_pcm.h)）

Integer-only PCM helpers shared by the microphone and speaker paths.

No libm and no floating point: the FreeRTOS port on IPRO7 does not save the FPU registers across a context switch, so two tasks using floating point corrupt each other silently. On the EVK, audio runs beside an NPU task. All functions are reentrant and work on mono int16 samples.

### evk_pcm_level { #evk_pcm_level }

```c
void evk_pcm_level(const int16_t *pcm, uint32_t n, uint16_t *peak, uint16_t *rms);
```

Peak and RMS of a block of samples.

| 參數 | 說明 |
|---|---|
| `pcm` | Samples (may be NULL only when `n` is 0). |
| `n` | Number of samples. |
| `peak` | max(\|sample\|), 0..32768; ignored if NULL. |
| `rms` | sqrt(mean(sample^2)), 0..32767 (0 when `n` is 0); ignored if NULL. |

### evk_pcm_dbfs_x10 { #evk_pcm_dbfs_x10 }

```c
int evk_pcm_dbfs_x10(uint32_t v);
```

Convert a level to dBFS.

| 參數 | 說明 |
|---|---|
| `v` | Level on a 0..32768 scale (32768 = full scale). |

**回傳值**：20*log10(v / 32768) in tenths of a dB (0 at full scale); -1200 for `v` = 0.

### evk_pcm_gain_q12 { #evk_pcm_gain_q12 }

```c
int32_t evk_pcm_gain_q12(int db);
```

Convert a gain in dB to a Q12 factor, table-driven.

| 參數 | 說明 |
|---|---|
| `db` | Gain in whole dB; clamped to -60..+48. |

**回傳值**：round(4096 * 10^(db/20)); 4096 = 0 dB.

### evk_pcm_apply_gain { #evk_pcm_apply_gain }

```c
uint32_t evk_pcm_apply_gain(const int16_t *src, int16_t *dst, uint32_t n, int32_t gain_q12);
```

Apply a Q12 gain with saturation: `dst[i] = clamp((src[i] * gain_q12) >> 12, -32768, 32767)`.

| 參數 | 說明 |
|---|---|
| `src` | Input samples. |
| `dst` | Output samples; may be the same buffer as `src`. |
| `n` | Number of samples. |
| `gain_q12` | Gain in Q12 (see [`evk_pcm_gain_q12()`](#evk_pcm_gain_q12)). |

**回傳值**：Number of samples that clipped.

### evk_pcm_sine_fill { #evk_pcm_sine_fill }

```c
void evk_pcm_sine_fill(int16_t *dst, uint32_t n, uint32_t *phase, uint32_t step, int32_t amp_q15);
```

Fill a buffer with a sine wave (256-entry table with linear interpolation).

| 參數 | 說明 |
|---|---|
| `dst` | Output, `n` samples. |
| `n` | Number of samples. |
| `phase` | 32-bit phase accumulator, carried between calls (start at 0). |
| `step` | Phase increment per sample, `freq * 2^32 / sample_rate` (use [`evk_pcm_sine_step()`](#evk_pcm_sine_step)). |
| `amp_q15` | Peak amplitude, 0..32767. |

### evk_pcm_sine_step { #evk_pcm_sine_step }

```c
uint32_t evk_pcm_sine_step(uint32_t freq_hz, uint32_t rate_hz);
```

Phase increment for [`evk_pcm_sine_fill()`](#evk_pcm_sine_fill).

| 參數 | 說明 |
|---|---|
| `freq_hz` | Tone frequency in Hz; below `rate_hz` / 2. |
| `rate_hz` | Sample rate in Hz. |

**回傳值**：`freq_hz * 2^32 / rate_hz`, or 0 when `rate_hz` is 0.

### evk_pcm_isqrt { #evk_pcm_isqrt }

```c
uint32_t evk_pcm_isqrt(uint32_t v);
```

Integer square root.

| 參數 | 說明 |
|---|---|
| `v` | Input. |

**回傳值**：floor(sqrt(`v`)).

### evk_pcm_ilog2_q8 { #evk_pcm_ilog2_q8 }

```c
uint32_t evk_pcm_ilog2_q8(uint32_t v);
```

Base-2 logarithm in Q8 fixed point.

| 參數 | 說明 |
|---|---|
| `v` | Input, &gt;= 1. |

**回傳值**：log2(`v`) * 256, truncated (8 fractional bits); 0 for `v` = 0.

## evk_sd.h { #evk_sd-h }

`#include "evk_sd.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/components/board/ipro7ai_evk/include/evk_sd.h)）

micro-SD card on the SDH controller (GPIO27-34), FatFS mounted at "sd:".

The board configuration does the pin work: `BOARD_PINMUX_INIT()` muxes GPIO28-33 to the SD controller and drives SD_PWR_EN, and the clock set-up un-gates and programs the SDH clock. Mounting only needs the FatFS disk driver registered and `f_mount()` called. The 4-bit bus is requested before the driver registers: the port defaults to 1-bit, which has a quarter of the bandwidth and is too slow for sustained reads.

Card-detect is GPIO34 (`BOARD_SD_DET_PIN`, low when a card is seated); the card supply switch is GPIO27 (`BOARD_SD_PWR_EN_PIN`).

Needs `CONFIG_EVFS=y`, `CONFIG_EVFS_USE_FATFS=y` and `CONFIG_COMPONENTS_FATFS_ENABLE=y` (the FatFS port layer includes `vfs_inode.h`, so EVFS has to be enabled with it). Paths passed to FatFS start with [`EVK_SD_ROOT`](#evk_sd-h-macros).

### evk_sd_present { #evk_sd_present }

```c
bool evk_sd_present(void);
```

Read the card-detect switch.

**回傳值**：true when the switch reports a card seated.

### evk_sd_mount { #evk_sd_mount }

```c
int evk_sd_mount(void);
```

Register the SDH disk driver (first call only) and mount the card at "sd:".

Mounts immediately, so a missing or unformatted card fails here rather than on the first file operation. Returns [`EVK_SD_OK`](#evk_sd-h-macros) at once if already mounted.

**回傳值**：[`EVK_SD_OK`](#evk_sd-h-macros), or [`EVK_SD_ERR_MOUNT`](#evk_sd-h-macros) if the card could not be mounted.

!!! note "注意"
    Blocking; call from task context.

### evk_sd_unmount { #evk_sd_unmount }

```c
int evk_sd_unmount(void);
```

Unmount the card.

Does nothing if it is not mounted.

**回傳值**：[`EVK_SD_OK`](#evk_sd-h-macros).

### evk_sd_mounted { #evk_sd_mounted }

```c
bool evk_sd_mounted(void);
```

Report whether the card is mounted.

**回傳值**：true between a successful [`evk_sd_mount()`](#evk_sd_mount) and [`evk_sd_unmount()`](#evk_sd_unmount).

### evk_sd_power { #evk_sd_power }

```c
void evk_sd_power(int on);
```

Switch the card supply (`BOARD_SD_PWR_EN_PIN`) on or off.

| 參數 | 說明 |
|---|---|
| `on` | Non-zero to power the card, 0 to cut its supply. |

### evk_sd_space_kb { #evk_sd_space_kb }

```c
int evk_sd_space_kb(uint32_t *total_kb, uint32_t *free_kb);
```

Total and free space on the mounted card.

| 參數 | 說明 |
|---|---|
| `total_kb` | Total space in KiB; ignored if NULL. |
| `free_kb` | Free space in KiB; ignored if NULL. |

| 回傳碼 | 說明 |
|---|---|
| `EVK_SD_OK` | Success. |
| `EVK_SD_ERR_STATE` | The card is not mounted. |
| `EVK_SD_ERR_IO` | `f_getfree()` failed. |

### evk_sd_exists { #evk_sd_exists }

```c
bool evk_sd_exists(const char *path);
```

Check whether a file or directory exists on the mounted card.

| 參數 | 說明 |
|---|---|
| `path` | Full path, for example "sd:/models/gesture.inm". |

**回傳值**：true if `path` exists; false if it does not, if `path` is NULL or if the card is not mounted.

### 巨集 { #evk_sd-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `EVK_SD_OK` | `0` | Success. |
| `EVK_SD_ERR_MOUNT` | `-1` | `f_mount()` failed: no card, or no FAT file system. |
| `EVK_SD_ERR_IO` | `-2` | A FatFS query failed. |
| `EVK_SD_ERR_STATE` | `-3` | The card is not mounted. |
| `EVK_SD_ROOT` | `"sd:/"` | Root directory of the mounted card. |
