---
title: PIO
description: 可程式 I/O：CCI、CMSIS-DAP 與掃描介面。
generated: tools/gen_api.py
migrate_from: []
---

# PIO

可程式 I/O：CCI、CMSIS-DAP 與掃描介面。說明取自標頭檔註解（英文）。

| 標頭 | 函式 | 說明 |
|---|---|---|
| [`hal_pio_cci.h`](#hal_pio_cci-h) | 2 | CCI bus master on a programmable-I/O (PIO) state machine. |
| [`hal_pio_cmsis_dap.h`](#hal_pio_cmsis_dap-h) | 10 | JTAG shift engine for a CMSIS-DAP debug probe on a programmable-I/O (PIO) state machine. |
| [`hal_pio_scan.h`](#hal_pio_scan-h) | 12 | Scan-chain pattern player on programmable-I/O (PIO) state machine 0. |

## hal_pio_cci.h { #hal_pio_cci-h }

`#include "hal_pio_cci.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pio_cci.h)）

CCI bus master on a programmable-I/O (PIO) state machine.

The master drives CLK (side-set), DI and CS (a two-pin output group) and samples DO. Each bit cell takes three PIO instructions: drive DI/CS with CLK low, raise CLK and sample DO while CLK is high (just after the rising edge, where the CCI slave expects it), then lower CLK. CLK idles low.

The cell has the same structure as the JTAG cell of [`hal_pio_cmsis_dap.h`](#hal_pio_cmsis_dap-h), so both can coexist on separate state machines and pins (JTAG normally on SM0, CCI on SM1). [`hal_pio_cci_init()`](#hal_pio_cci_init) loads the cell program at instruction address 0, where it replaces an identical JTAG program. It is not identical to the TDI-only JTAG program used when `hal_pio_cmsis_dap_cfg_t::tms_gpio` is set, so do not run that JTAG profile at the same time.

The PIO block clock must already be enabled, for example by [`hal_pio_cmsis_dap_board_init()`](#hal_pio_cmsis_dap_board_init) or [`hal_pio_cmsis_dap_init()`](#hal_pio_cmsis_dap_init).

Transfers use DMA0 channels 0 (TX) and 1 (RX), which the application must leave free.

### hal_pio_cci_init { #hal_pio_cci_init }

```c
int hal_pio_cci_init(const hal_pio_cci_cfg_t *cfg);
```

Configure the pins, load the cell program and start the CCI state machine.

Copies `cfg`, loads the three-instruction cell at instruction address 0, configures and enables state machine `cfg->pio_sm`, routes CLK, DI and CS to PIO outputs and DO to a PIO input with pull-up, and sets up DMA0 channels 0 and 1 for the state machine's FIFOs.

| 參數 | 說明 |
|---|---|
| `cfg` | Configuration; copied, so it need not stay valid. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `cfg` is NULL. |

### hal_pio_cci_shift { #hal_pio_cci_shift }

```c
void hal_pio_cci_shift(const uint32_t *tx, uint32_t n, uint32_t *rx);
```

Clock `n` bit cells and capture DO.

For clock i, bit 0 of `tx`[i] is the DI level and bit 1 the CS level (bit order swapped when `out_swap` is set). Bit 0 of `rx`[i] receives DO as sampled during clock i's high phase. DMA feeds the TX FIFO and drains the RX FIFO, so CLK does not pause in the middle of a frame.

The call blocks until both DMA channels finish or a bounded poll count expires; a timeout is not reported.

| 參數 | 說明 |
|---|---|
| `tx` | Cell words, `n` entries. |
| `n` | Number of cells; 0 does nothing. |
| `rx` | Captured DO bits, `n` entries. Must not be NULL: with NULL the function returns without clocking. Pass a scratch buffer for write-only frames. |

!!! note "注意"
    `tx` and `rx` are accessed by DMA without cache maintenance: place them in non-cacheable, DMA-reachable RAM.

### hal_pio_cci_cfg_t { #hal_pio_cci_cfg_t }

CCI master configuration.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `pin_clk` | `uint8_t` | CLK GPIO, driven by side-set. |
| `pin_di` | `uint8_t` | DI GPIO (master to slave), part of the two-pin output group. |
| `pin_cs` | `uint8_t` | CS GPIO, part of the two-pin output group; must be adjacent to `pin_di` (see `out_swap`). |
| `pin_do` | `uint8_t` | DO GPIO (slave to master), PIO input with pull-up. |
| `pio_sm` | `uint8_t` | PIO state machine index (normally 1; 0 is used by JTAG). |
| `out_swap` | `uint8_t` | 0: output group starts at DI and CS = DI + 1; TX word bit 0 = DI, bit 1 = CS. 1: output group starts at CS and DI = CS + 1; the caller must pack bit 0 = CS, bit 1 = DI. |
| `clkdiv_int` | `uint16_t` | Integer part of the SM clock divider. CLK = f_PIO / (12 * divider), i.e. 8 MHz / divider with a 96 MHz PIO clock. 0 means 65536. |
| `clkdiv_frac` | `uint8_t` | Fractional part of the SM clock divider, in 1/256 steps. |

## hal_pio_cmsis_dap.h { #hal_pio_cmsis_dap-h }

`#include "hal_pio_cmsis_dap.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pio_cmsis_dap.h)）

JTAG shift engine for a CMSIS-DAP debug probe on a programmable-I/O (PIO) state machine.

This HAL owns the JTAG PIO program, the PIO block clock, the pin multiplexing, the state-machine configuration and a per-TCK shift primitive. It has no knowledge of the CMSIS-DAP protocol; the probe firmware builds DAP commands on top of [`hal_pio_cmsis_dap_shift()`](#hal_pio_cmsis_dap_shift).

Each TCK period takes three PIO instructions of four SM cycles each (12 SM cycles): drive TDI/TMS with TCK low, raise TCK and sample TDO while TCK is high, lower TCK. TCK idles low between words.

Typical sequence: [`hal_pio_cmsis_dap_board_init()`](#hal_pio_cmsis_dap_board_init) or [`hal_pio_cmsis_dap_init()`](#hal_pio_cmsis_dap_init), [`hal_pio_cmsis_dap_set_clock()`](#hal_pio_cmsis_dap_set_clock), [`hal_pio_cmsis_dap_set_port()`](#hal_pio_cmsis_dap_set_port) with [`HAL_DAP_PORT_JTAG`](#hal_dap_port_t), then [`hal_pio_cmsis_dap_shift()`](#hal_pio_cmsis_dap_shift) calls.

The implementation is not part of the prebuilt HAL library: add `bsp/hal/src/hal_pio_cmsis_dap.c` and `bsp/drivers/ipro7_soc/std_drv/src/drv_pio.c` to the application's sources. See [`hal_pio_cci.h`](#hal_pio_cci-h) for the CCI master that can share the PIO block.

### hal_pio_cmsis_dap_board_init { #hal_pio_cmsis_dap_board_init }

```c
void hal_pio_cmsis_dap_board_init(void);
```

Initialise the probe from the application's Kconfig pin settings.

Calls [`hal_pio_cmsis_dap_init()`](#hal_pio_cmsis_dap_init) with the pins `CONFIG_CMSIS_DAP_PIN_TCK`, `_TMS`, `_TDI`, `_TDO`, `_NRESET` and `_NTRST`, state machine 0, the 96 MHz PIO clock source without pre-division and an SM divider of 96 (TCK about 83 kHz until [`hal_pio_cmsis_dap_set_clock()`](#hal_pio_cmsis_dap_set_clock) is called). The state machine is not started.

### hal_pio_cmsis_dap_init { #hal_pio_cmsis_dap_init }

```c
int hal_pio_cmsis_dap_init(const hal_pio_cmsis_dap_cfg_t *cfg);
```

Reset the PIO block and set up the JTAG state machine and pins.

Resets the PIO block and enables its clock with `cfg->pio_clk_sel` and `cfg->pio_clk_div`, loads the JTAG program at instruction address 0, configures state machine `cfg->pio_sm`, routes TCK and TDI (and TMS unless `tms_gpio`) to PIO outputs and TDO to a PIO input with pull-up, and releases nSRST and nTRST. The state machine is left stopped; start it with [`hal_pio_cmsis_dap_set_port()`](#hal_pio_cmsis_dap_set_port).

| 參數 | 說明 |
|---|---|
| `cfg` | Configuration; copied, so it need not stay valid. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `cfg` is NULL. |

### hal_pio_cmsis_dap_deinit { #hal_pio_cmsis_dap_deinit }

```c
void hal_pio_cmsis_dap_deinit(void);
```

Stop the state machine (same as [`hal_pio_cmsis_dap_set_port()`](#hal_pio_cmsis_dap_set_port) with [`HAL_DAP_PORT_OFF`](#hal_dap_port_t)).

Pins keep their configuration.

### hal_pio_cmsis_dap_set_port { #hal_pio_cmsis_dap_set_port }

```c
int hal_pio_cmsis_dap_set_port(hal_dap_port_t port);
```

Start or stop the state machine.

| 參數 | 說明 |
|---|---|
| `port` | [`HAL_DAP_PORT_JTAG`](#hal_dap_port_t) or [`HAL_DAP_PORT_SWD`](#hal_dap_port_t) starts it, [`HAL_DAP_PORT_OFF`](#hal_dap_port_t) stops it. |

**回傳值**：0 (always).

### hal_pio_cmsis_dap_pio_reclock { #hal_pio_cmsis_dap_pio_reclock }

```c
void hal_pio_cmsis_dap_pio_reclock(void);
```

Reset and re-clock the whole PIO block, wiping all state-machine state.

Uses the clock settings of the last [`hal_pio_cmsis_dap_init()`](#hal_pio_cmsis_dap_init) call. Programs, pin directions and FIFOs of every state machine are lost, so re-initialise the state machine to be used next (for example with [`hal_pio_cci_init()`](#hal_pio_cci_init)) afterwards. Use it when two PIO users take turns on shared pads, so that a stopped state machine leaves no pin-direction claim on a shared pad.

### hal_pio_cmsis_dap_set_clock { #hal_pio_cmsis_dap_set_clock }

```c
uint32_t hal_pio_cmsis_dap_set_clock(uint32_t hz);
```

Set the TCK frequency.

Programs an integer SM divider of `8 MHz / hz` (at least 1), which assumes a 96 MHz PIO clock.

| 參數 | 說明 |
|---|---|
| `hz` | Requested TCK frequency in Hz; 0 selects a divider of 96. |

**回傳值**：Resulting TCK frequency in Hz (8 MHz / divider), at most 8 MHz.

### hal_pio_cmsis_dap_shift { #hal_pio_cmsis_dap_shift }

```c
void hal_pio_cmsis_dap_shift(const uint32_t *tx, uint32_t n, uint32_t *rx);
```

Shift `n` TCK cycles and capture TDO.

Each word of `tx` drives one TCK cycle: bit 0 = TDI, bit 1 = TMS (swapped with `out_swap`; TDI only, in bit 0, with `tms_gpio`). Bit 0 of `rx`[i] receives TDO sampled during cycle i. The CPU feeds and drains the FIFOs and the call blocks until all `n` results are read; there is no timeout.

| 參數 | 說明 |
|---|---|
| `tx` | Cycle words, `n` entries. |
| `n` | Number of TCK cycles. |
| `rx` | Captured TDO bits, `n` entries, or NULL to discard them. |

**前置條件**：The state machine is running ([`hal_pio_cmsis_dap_set_port()`](#hal_pio_cmsis_dap_set_port) with [`HAL_DAP_PORT_JTAG`](#hal_dap_port_t) or [`HAL_DAP_PORT_SWD`](#hal_dap_port_t)); otherwise the call never returns.

### hal_pio_cmsis_dap_set_tms { #hal_pio_cmsis_dap_set_tms }

```c
void hal_pio_cmsis_dap_set_tms(uint32_t level);
```

Drive the CPU-owned TMS pin.

Only acts when the configuration has `tms_gpio` set (and a TMS pin); otherwise it does nothing. Call it before shifting a run with constant TMS, or before each bit when TMS changes per bit.

| 參數 | 說明 |
|---|---|
| `level` | 0 drives TMS low, any other value high. |

### hal_pio_cmsis_dap_set_pins { #hal_pio_cmsis_dap_set_pins }

```c
void hal_pio_cmsis_dap_set_pins(uint8_t value, uint8_t select);
```

Set the probe pins for the CMSIS-DAP `DAP_SWJ_Pins` command.

Bit layout as in CMSIS-DAP: bit 0 TCK, 1 TMS, 2 TDI, 3 TDO, 5 nTRST, 7 nRESET. Only nRESET and nTRST are driven (1 releases the line to its pull-up, 0 drives it low); the other selected bits are only stored for [`hal_pio_cmsis_dap_get_pins()`](#hal_pio_cmsis_dap_get_pins).

| 參數 | 說明 |
|---|---|
| `value` | New pin levels. |
| `select` | Mask of the bits in `value` to apply. |

### hal_pio_cmsis_dap_get_pins { #hal_pio_cmsis_dap_get_pins }

```c
uint8_t hal_pio_cmsis_dap_get_pins(void);
```

Read the probe pins in `DAP_SWJ_Pins` bit layout.

nRESET (bit 7) and nTRST (bit 5) are read from their pins when configured; the other bits are the values last stored by [`hal_pio_cmsis_dap_set_pins()`](#hal_pio_cmsis_dap_set_pins).

**回傳值**：Pin state byte.

### hal_dap_port_t { #hal_dap_port_t }

Debug port selected by [`hal_pio_cmsis_dap_set_port()`](#hal_pio_cmsis_dap_set_port).

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_DAP_PORT_OFF` |  | Port off: the state machine is stopped. |
| `HAL_DAP_PORT_JTAG` |  | JTAG: the state machine runs. |
| `HAL_DAP_PORT_SWD` |  | SWD: the state machine runs (same cell as JTAG). |

### hal_pio_cmsis_dap_cfg_t { #hal_pio_cmsis_dap_cfg_t }

Probe pin and clock configuration for [`hal_pio_cmsis_dap_init()`](#hal_pio_cmsis_dap_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `pin_tck` | `uint8_t` | TCK GPIO (also SWCLK), driven by side-set; any GPIO. |
| `pin_tdi` | `uint8_t` | TDI GPIO; output-group bit 0, or bit 1 with `out_swap`. |
| `pin_tms` | `uint8_t` | TMS GPIO; output-group bit 1, or bit 0 (group base) with `out_swap`; a plain CPU-driven GPIO with `tms_gpio`. |
| `pin_tdo` | `uint8_t` | TDO GPIO; PIO input with pull-up; any GPIO outside the output group. |
| `pin_nreset` | `uint8_t` | nSRST GPIO, emulated open drain (driven low or released to a pull-up); 0xFF = none. |
| `pin_ntrst` | `uint8_t` | nTRST GPIO, emulated open drain; 0xFF = none. |
| `pio_sm` | `uint8_t` | PIO state machine index ([`hal_pio_cmsis_dap_board_init()`](#hal_pio_cmsis_dap_board_init) uses 0). |
| `out_swap` | `uint8_t` | 0: output group starts at TDI and TMS = TDI + 1; TX word bit 0 = TDI, bit 1 = TMS. 1: output group starts at TMS and TDI = TMS + 1; the caller must pack bit 0 = TMS, bit 1 = TDI. Ignored when `tms_gpio` is set. |
| `tms_gpio` | `uint8_t` | 1: TMS is a plain GPIO driven by the CPU with [`hal_pio_cmsis_dap_set_tms()`](#hal_pio_cmsis_dap_set_tms), not part of the PIO output group. The cell then shifts TDI only (one bit per TX word) and TDI and TMS need not be adjacent. |
| `pio_clk_div` | `uint8_t` | PIO clock pre-divider in GLB: f_PIO = source / (pio_clk_div + 1). |
| `pio_clk_sel` | `uint8_t` | PIO clock source select in GLB; 0 selects the 96 MHz source. |
| `clkdiv_int` | `uint16_t` | Integer part of the SM clock divider: TCK = f_PIO / (12 * divider); 0 means 65536. [`hal_pio_cmsis_dap_set_clock()`](#hal_pio_cmsis_dap_set_clock) replaces the divider in use. |
| `clkdiv_frac` | `uint8_t` | Fractional part of the SM clock divider, in 1/256 steps. |

## hal_pio_scan.h { #hal_pio_scan-h }

`#include "hal_pio_scan.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pio_scan.h)）

Scan-chain pattern player on programmable-I/O (PIO) state machine 0.

Drives a device under test's scan inputs, scan clocks and scan enable from a stream of TX words and captures its scan outputs into RX words. All output pins form one PIO output group that is driven only by `out` instructions (no side-set), so every pin level, including the clocks, comes from the TX stream.

The default program plays one scan cell per four instructions and consumes three TX words per cell:

1. pin levels from the start of the cell to the clock rise (scan data, clock low); the input pins are sampled once, at the strobe time, while these levels are still applied, giving one RX word per cell;
1. pin levels from the clock rise to the clock fall (clock pulse);
1. pin levels from the clock fall to the end of the cell. Only the low `out_cnt` bits of a TX word are used; bit i of an RX word is GPIO `in_base + i`. The phase lengths come from the timing fields of [`hal_pio_scan_cfg_t`](#hal_pio_scan_cfg_t).

Transport: [`hal_pio_scan_shift()`](#hal_pio_scan_shift) for one burst; [`hal_pio_scan_start()`](#hal_pio_scan_start), [`hal_pio_scan_feed()`](#hal_pio_scan_feed) / [`hal_pio_scan_feed_log()`](#hal_pio_scan_feed_log) and [`hal_pio_scan_stop()`](#hal_pio_scan_stop) to keep the scan clock running across patterns; [`hal_pio_scan_shift_dma()`](#hal_pio_scan_shift_dma) for a DMA-paced burst.

The implementation is not part of the prebuilt HAL library: add `bsp/hal/src/hal_pio_scan.c` and `bsp/drivers/ipro7_soc/std_drv/src/drv_pio.c` to the application's sources.

### hal_pio_scan_init { #hal_pio_scan_init }

```c
int hal_pio_scan_init(const hal_pio_scan_cfg_t *cfg);
```

Reset the PIO block and set up state machine 0 and the pins.

Copies `cfg`, resets the PIO block and enables its clock, builds the program selected by `cfg` and loads it at instruction address 0, configures state machine 0 (pins, shift directions with autopull after `out_cnt` bits and autopush after `in_cnt` bits, clock divider, wrap, input synchroniser bypass, output directions) and routes the output and input groups to the PIO. The state machine is left stopped.

| 參數 | 說明 |
|---|---|
| `cfg` | Configuration; copied, so it need not stay valid. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `cfg` is NULL. |

### hal_pio_scan_shift { #hal_pio_scan_shift }

```c
int hal_pio_scan_shift(const uint32_t *tx, uint32_t tx_words, uint32_t *rx, uint32_t rx_words);
```

Play one CPU-paced burst: restart the state machine, feed and collect, stop.

Same as [`hal_pio_scan_start()`](#hal_pio_scan_start), [`hal_pio_scan_feed()`](#hal_pio_scan_feed) and [`hal_pio_scan_stop()`](#hal_pio_scan_stop).

| 參數 | 說明 |
|---|---|
| `tx` | TX words. |
| `tx_words` | Number of TX words. |
| `rx` | Buffer for the captured RX words. |
| `rx_words` | Number of RX words to collect. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL buffer with a non-zero count, or the RX words did not arrive within the polling bound. |

### hal_pio_scan_start { #hal_pio_scan_start }

```c
void hal_pio_scan_start(void);
```

Restart and enable state machine 0 for a streaming session.

Call it exactly once before a series of [`hal_pio_scan_feed()`](#hal_pio_scan_feed) calls and end the series with [`hal_pio_scan_stop()`](#hal_pio_scan_stop). The state machine keeps running between feeds; when the TX FIFO runs empty it stalls with the last pin levels applied. Restarting it between patterns would break the continuity that devices with continuously clocked scan-compression logic rely on.

### hal_pio_scan_feed { #hal_pio_scan_feed }

```c
int hal_pio_scan_feed(const uint32_t *tx, uint32_t tx_words, uint32_t *rx, uint32_t rx_words);
```

Feed TX words to the running state machine and collect RX words.

The CPU keeps the TX FIFO topped up and drains the RX FIFO until `rx_words` words have been read. The state machine is neither restarted nor stopped.

| 參數 | 說明 |
|---|---|
| `tx` | TX words. |
| `tx_words` | Number of TX words. |
| `rx` | Buffer for the captured RX words. |
| `rx_words` | Number of RX words to collect. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL buffer with a non-zero count, or the RX words did not arrive within the polling bound. |

**前置條件**：[`hal_pio_scan_start()`](#hal_pio_scan_start) has been called.

### hal_pio_scan_stop { #hal_pio_scan_stop }

```c
void hal_pio_scan_stop(void);
```

Stop state machine 0 at the end of a streaming session.

### hal_pio_scan_feed_log { #hal_pio_scan_feed_log }

```c
int hal_pio_scan_feed_log(const uint32_t *tx, uint32_t n, uint8_t *caplog, uint32_t log_max, uint32_t in_mask);
```

Feed a long burst without letting the TX FIFO run empty, logging the captures.

Feeds all `n` TX words in one loop so that the scan clock does not stop at pattern boundaries, and stores `rx & in_mask` of the first `log_max` RX words in `caplog` (later words are still read, but not stored).

| 參數 | 說明 |
|---|---|
| `tx` | TX words. |
| `n` | Number of TX words; the function also waits for `n` RX words. |
| `caplog` | Capture log, `log_max` bytes. |
| `log_max` | Number of captures to store. |
| `in_mask` | Mask applied to each RX word before it is stored. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `tx` or `caplog` is NULL with a non-zero `n`, or the RX words did not arrive within the polling bound. |

**前置條件**：[`hal_pio_scan_start()`](#hal_pio_scan_start) has been called.

!!! note "注意"
    The function expects one RX word per TX word; the default program produces one RX word per three TX words.

### hal_pio_scan_shift_dma { #hal_pio_scan_shift_dma }

```c
int hal_pio_scan_shift_dma(const uint32_t *tx, uint32_t tx_words, uint32_t *rx, uint32_t rx_words);
```

Play one DMA-paced burst.

Same result as [`hal_pio_scan_shift()`](#hal_pio_scan_shift), but the FIFOs are fed and drained by DMA (TX: memory to PIO on request [`HAL_PIO_SCAN_DMA_REQ_TX`](#hal_pio_scan-h-macros), RX: PIO to memory on [`HAL_PIO_SCAN_DMA_REQ_RX`](#hal_pio_scan-h-macros)) using `dma_id`, `dma_tx_ch` and `dma_rx_ch` of the configuration. The HAL cleans the data cache over `tx` and invalidates it over `rx`, so both buffers may be cacheable.

Only compiled when `HAL_PIO_SCAN_USE_DMA` is defined for hal_pio_scan.c; there is no CPU-paced fallback.

| 參數 | 說明 |
|---|---|
| `tx` | TX words. |
| `tx_words` | Number of TX words. |
| `rx` | Buffer for the captured RX words. |
| `rx_words` | Number of RX words to collect. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | A NULL buffer with a non-zero count, a rejected DMA setup, a timeout, or extra words left in the RX FIFO (the capture is misaligned; run the call again). |

!!! note "注意"
    Calls [`dma_init()`](peripherals.md#dma_init) for both channels. Without `CONFIG_DMA_CHANNEL_ALLOCATOR` that disables the whole DMA controller for a moment and aborts transfers on its other channels.

### hal_pio_scan_deinit { #hal_pio_scan_deinit }

```c
void hal_pio_scan_deinit(void);
```

Stop state machine 0 and its DMA requests.

### hal_pio_scan_tx_fifo_addr { #hal_pio_scan_tx_fifo_addr }

```c
uint32_t hal_pio_scan_tx_fifo_addr(void);
```

Return the address of state machine 0's TX FIFO register (a DMA destination).

**回傳值**：Absolute MMIO address.

### hal_pio_scan_rx_fifo_addr { #hal_pio_scan_rx_fifo_addr }

```c
uint32_t hal_pio_scan_rx_fifo_addr(void);
```

Return the address of state machine 0's RX FIFO register (a DMA source).

**回傳值**：Absolute MMIO address.

### hal_pio_scan_build_prog { #hal_pio_scan_build_prog }

```c
uint8_t hal_pio_scan_build_prog(uint16_t period_ns, uint16_t clk_rise_ns, uint16_t clk_fall_ns, uint16_t strobe_ns, uint8_t out_cnt, uint8_t in_cnt, uint16_t prog[4], uint8_t *wrap_top);
```

Build the default four-instruction scan program from the cell timing.

Instructions, each lasting one phase: `out` (cell start to strobe), `in` (strobe to clock rise; samples the inputs at the strobe), `out` (clock rise to clock fall), `out` (clock fall to cell end). The timing arguments are SM-cycle counts; each phase is clamped to 1 to 32 cycles. They must satisfy `strobe_ns` &lt; `clk_rise_ns` &lt; `clk_fall_ns` &lt; `period_ns`, otherwise (or with `period_ns` 0) every phase is one cycle long.

| 參數 | 說明 |
|---|---|
| `period_ns` | Cell period. |
| `clk_rise_ns` | Clock rise within the cell. |
| `clk_fall_ns` | Clock fall within the cell. |
| `strobe_ns` | Input sample point within the cell. |
| `out_cnt` | Pins driven per `out`. |
| `in_cnt` | Pins sampled by `in`. |
| `prog` | Receives the 4 instruction words. |
| `wrap_top` | Receives the wrap-top instruction index (3). |

**回傳值**：Number of instructions (4).

### hal_pio_scan_build_doublet_prog { #hal_pio_scan_build_doublet_prog }

```c
uint8_t hal_pio_scan_build_doublet_prog(uint16_t period_ns, uint16_t clk_rise_ns, uint16_t clk_fall_ns, uint16_t strobe_ns, uint8_t out_cnt, uint8_t in_cnt, uint16_t prog[16]);
```

Build the capture-doublet scan program.

Normal cells have the same waveform as the default program (three TX words, one RX word). A down-counter in the X register selects a boundary cell that, after the sample, emits a one-cycle launch pulse, a gap and a capture pulse, so that launch and capture are only a few SM cycles apart (two cycles, 20.8 ns, with a 96 MHz SM clock and the default gap).

TX stream: one word that loads X with the number of normal cells before the first boundary cell, then three words per normal cell and six words per boundary cell (cell start, launch, gap, capture, hold, and the X value for the next segment). Each cell gives one RX word.

Timing arguments are SM-cycle counts as for [`hal_pio_scan_build_prog()`](#hal_pio_scan_build_prog); the strobe-to-rise and hold phases are at least 2 cycles, and every phase is 4 cycles when the timing is inconsistent or `period_ns` is 0. The capture pulse width and the launch-to-capture gap are compile-time settings of hal_pio_scan.c (`HAL_PIO_DOUBLET_CAPW`, default 4 cycles; `HAL_PIO_DOUBLET_GAP`, default 1 cycle).

| 參數 | 說明 |
|---|---|
| `period_ns` | Cell period. |
| `clk_rise_ns` | Clock rise within the cell. |
| `clk_fall_ns` | Clock fall within the cell. |
| `strobe_ns` | Input sample point within the cell. |
| `out_cnt` | Pins driven per `out`. |
| `in_cnt` | Pins sampled by `in`. |
| `prog` | Receives the instruction words (13 used). |

**回傳值**：Number of instructions (13).

### hal_pio_scan_cfg_t { #hal_pio_scan_cfg_t }

Scan player configuration for [`hal_pio_scan_init()`](#hal_pio_scan_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `out_base` | `uint8_t` | First GPIO of the output group (scan inputs, scan clocks, scan enable). |
| `out_cnt` | `uint8_t` | Number of output pins; also the bits consumed per `out` (TX word). |
| `in_base` | `uint8_t` | First GPIO of the input group (scan outputs of the device under test). |
| `in_cnt` | `uint8_t` | Number of input pins sampled per cell; bits per RX word. |
| `ss_base` | `uint8_t` | First side-set GPIO; unused while `ss_cnt` is 0. |
| `ss_cnt` | `uint8_t` | Side-set pin count. Keep 0: with a non-zero count the state machine reads part of every delay field as side-set. |
| `ss_pio_mask` | `uint32_t` | Not used by the current implementation. |
| `clkdiv_int` | `uint16_t` | Integer part of the SM clock divider: SM clock = f_PIO / (clkdiv_int + clkdiv_frac / 256); 0 means 65536. |
| `clkdiv_frac` | `uint8_t` | Fractional part of the SM clock divider, in 1/256 steps. |
| `pio_clk_div` | `uint8_t` | PIO clock pre-divider in GLB: f_PIO = source / (pio_clk_div + 1). |
| `pio_clk_sel` | `uint8_t` | PIO clock source select in GLB; 0 selects the 96 MHz source. |
| `input_sync_bypass` | `uint32_t` | Value for the PIO input-synchroniser bypass register (one bit per GPIO); 0 keeps the 2-flip-flop synchronisers on all inputs. |
| `dma_id` | `uint8_t` | DMA controller used by [`hal_pio_scan_shift_dma()`](#hal_pio_scan_shift_dma). |
| `dma_tx_ch` | `uint8_t` | DMA channel for TX (memory to PIO), used by [`hal_pio_scan_shift_dma()`](#hal_pio_scan_shift_dma). |
| `dma_rx_ch` | `uint8_t` | DMA channel for RX (PIO to memory), used by [`hal_pio_scan_shift_dma()`](#hal_pio_scan_shift_dma). |
| `period_ns` | `uint16_t` | Cell period. The four timing fields come from the test pattern's timing set (for example a WGL timeplate). After multiplication by `delay_scale` the values are used as SM-cycle counts, each phase clamped to 1 to 32 cycles. They must satisfy strobe &lt; rise &lt; fall &lt; period; otherwise (or when all are 0) every phase is one cycle long. |
| `clk_rise_ns` | `uint16_t` | Scan clock rise within the cell (see `period_ns` for units). |
| `clk_fall_ns` | `uint16_t` | Scan clock fall within the cell (see `period_ns` for units). |
| `strobe_ns` | `uint16_t` | Input sample point within the cell. |
| `uniform_phases` | `uint8_t` | Non-zero: ignore the timing fields and give every phase one SM cycle (four cycles per cell). |
| `delay_scale` | `uint8_t` | Factor applied to the timing fields before the program is built; 0 or 1 = no scaling. |
| `capture_doublet` | `uint8_t` | Non-zero: load the capture-doublet program of [`hal_pio_scan_build_doublet_prog()`](#hal_pio_scan_build_doublet_prog) instead of the default program; the TX stream must use its layout. |
| `branch_probe` | `uint8_t` | Diagnostic option: non-zero appends an unconditional jump to each cell of the default program, taking one cycle from the last phase when it is longer than one cycle. A cell still consumes three TX words. |

### 巨集 { #hal_pio_scan-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_PIO_SCAN_DMA_REQ_TX` | `20u` | Request ID of the SM0 TX FIFO (memory to PIO). |
| `HAL_PIO_SCAN_DMA_REQ_RX` | `16u` | Request ID of the SM0 RX FIFO (PIO to memory). |
