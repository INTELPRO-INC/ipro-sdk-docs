---
title: Peripheral I/O
description: GPIO, UART, SPI, I2C, PWM, ADC, DAC, analog comparator, KeyScan, QDEC and DMA.
generated: tools/gen_api.py
migrate_from: []
---

# Peripheral I/O

GPIO, UART, SPI, I2C, PWM, ADC, DAC, analog comparator, KeyScan, QDEC and DMA.

| Header | Functions | Description |
|---|---|---|
| [`hal_gpio.h`](#hal_gpio-h) | 6 | GPIO driver: pin mode, read/write and pin interrupts. |
| [`hal_uart.h`](#hal_uart-h) | 11 | UART driver: configuration, polling and DMA transfers, interrupts. |
| [`uart_config.h`](#uart_config-h) | 0 | Compile-time UART line options used by the UART driver ([`hal_uart.h`](#hal_uart-h)). |
| [`hal_spi.h`](#hal_spi-h) | 8 | SPI controller driver: configuration, blocking transfers, FIFO and DMA control, interrupt callback. |
| [`hal_i2c.h`](#hal_i2c-h) | 3 | I2C master driver: blocking register-style transfers. |
| [`hal_pwm.h`](#hal_pwm-h) | 3 | PWM driver: one PWM group with four channels; period, duty cycle and polarity control. |
| [`hal_adc.h`](#hal_adc-h) | 7 | General-purpose ADC driver: channel selection, polled, interrupt and DMA reads, battery and die-temperature measurement. |
| [`adc_config.h`](#adc_config-h) | 0 | Fixed analog front-end settings applied by [`hal_adc_init()`](#hal_adc_init). |
| [`hal_dac.h`](#hal_dac-h) | 5 | General-purpose DAC driver: two 10-bit output channels, register or DMA output. |
| [`hal_acomp.h`](#hal_acomp-h) | 6 | Analog comparator (ACOMP) driver: input selection, hysteresis, output and edge interrupts. |
| [`hal_keyscan.h`](#hal_keyscan-h) | 0 | Key-scan matrix controller definitions: control commands, matrix size, events and the device configuration. |
| [`hal_qdec.h`](#hal_qdec-h) | 0 | Quadrature decoder (QDEC) definitions: instances, control commands, events and the device configuration. |
| [`hal_dma.h`](#hal_dma-h) | 13 | DMA driver: channel configuration, linked-list (LLI) transfers and completion callbacks. |

## hal_gpio.h { #hal_gpio-h }

`#include "hal_gpio.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_gpio.h))

GPIO driver: pin mode, read/write and pin interrupts.

Pins are addressed by their GPIO number. [`gpio_set_mode()`](#gpio_set_mode) routes the pin to the GPIO function and sets direction and pull resistor (or an interrupt trigger). All pin interrupts share one CPU interrupt line; to get a callback for a pin:

1. [`gpio_set_mode()`](#gpio_set_mode) with one of the interrupt modes (this leaves the pin interrupt masked),
1. [`gpio_attach_irq()`](#gpio_attach_irq) to register the callback,
1. [`gpio_irq_enable()`](#gpio_irq_enable) with `enabled` = 1 to unmask the pin interrupt.

### gpio_set_mode { #gpio_set_mode }

```c
void gpio_set_mode(uint32_t pin, uint32_t mode);
```

Configure a pin as GPIO with the given mode.

Selects the GPIO function, drive strength 0 and the Schmitt-trigger input. For the interrupt modes the shared GPIO interrupt is disabled in the CPU while the pin is being set up and enabled again afterwards. Unknown mode values are ignored.

| Parameter | Description |
|---|---|
| `pin` | GPIO number. |
| `mode` | One of the `GPIO_*_MODE` values. |

### gpio_write { #gpio_write }

```c
void gpio_write(uint32_t pin, uint32_t value);
```

Set the output level of a pin.

| Parameter | Description |
|---|---|
| `pin` | GPIO number. |
| `value` | 0 drives the pin low; any other value drives it high. |

### gpio_toggle { #gpio_toggle }

```c
void gpio_toggle(uint32_t pin);
```

Invert the output level of a pin.

| Parameter | Description |
|---|---|
| `pin` | GPIO number. |

### gpio_read { #gpio_read }

```c
int gpio_read(uint32_t pin);
```

Read the input level of a pin.

| Parameter | Description |
|---|---|
| `pin` | GPIO number. |

**Returns:** 1 if the pin is high, 0 if it is low.

### gpio_attach_irq { #gpio_attach_irq }

```c
void gpio_attach_irq(uint32_t pin, void(*cbfun)(uint32_t pin));
```

Register a callback for a pin interrupt.

Adds the pin to the list served by the shared GPIO interrupt handler, installs that handler and enables the GPIO interrupt in the CPU. The callback runs in interrupt context; the driver clears the pin's interrupt status after the callback returns. Each call allocates a list entry with malloc(); there is no function to remove an entry.

| Parameter | Description |
|---|---|
| `pin` | GPIO number, configured with an interrupt mode. |
| `cbfun` | Callback; receives the GPIO number of the pin that fired. |

### gpio_irq_enable { #gpio_irq_enable }

```c
void gpio_irq_enable(uint32_t pin, uint8_t enabled);
```

Unmask or mask the interrupt of a pin.

| Parameter | Description |
|---|---|
| `pin` | GPIO number. |
| `enabled` | Non-zero to unmask the pin interrupt, 0 to mask it. |

### gpio_pin_type { #gpio_pin_type }

GPIO numbers 0 to 31.

The `pin` argument of the GPIO functions is the plain GPIO number, so these names are optional.

| Name | Value | Description |
|---|---|---|
| `GPIO_PIN_0` | `0` | GPIO 0. |
| `GPIO_PIN_1` |  | GPIO 1. |
| `GPIO_PIN_2` |  | GPIO 2. |
| `GPIO_PIN_3` |  | GPIO 3. |
| `GPIO_PIN_4` |  | GPIO 4. |
| `GPIO_PIN_5` |  | GPIO 5. |
| `GPIO_PIN_6` |  | GPIO 6. |
| `GPIO_PIN_7` |  | GPIO 7. |
| `GPIO_PIN_8` |  | GPIO 8. |
| `GPIO_PIN_9` |  | GPIO 9. |
| `GPIO_PIN_10` |  | GPIO 10. |
| `GPIO_PIN_11` |  | GPIO 11. |
| `GPIO_PIN_12` |  | GPIO 12. |
| `GPIO_PIN_13` |  | GPIO 13. |
| `GPIO_PIN_14` |  | GPIO 14. |
| `GPIO_PIN_15` |  | GPIO 15. |
| `GPIO_PIN_16` |  | GPIO 16. |
| `GPIO_PIN_17` |  | GPIO 17. |
| `GPIO_PIN_18` |  | GPIO 18. |
| `GPIO_PIN_19` |  | GPIO 19. |
| `GPIO_PIN_20` |  | GPIO 20. |
| `GPIO_PIN_21` |  | GPIO 21. |
| `GPIO_PIN_22` |  | GPIO 22. |
| `GPIO_PIN_23` |  | GPIO 23. |
| `GPIO_PIN_24` |  | GPIO 24. |
| `GPIO_PIN_25` |  | GPIO 25. |
| `GPIO_PIN_26` |  | GPIO 26. |
| `GPIO_PIN_27` |  | GPIO 27. |
| `GPIO_PIN_28` |  | GPIO 28. |
| `GPIO_PIN_29` |  | GPIO 29. |
| `GPIO_PIN_30` |  | GPIO 30. |
| `GPIO_PIN_31` |  | GPIO 31. |
| `GPIO_PIN_MAX` |  | Number of names in this enumeration (32). |

### Macros { #hal_gpio-h-macros }

| Name | Value | Description |
|---|---|---|
| `GPIO_OUTPUT_MODE` | `0` | Output, no pull resistor. |
| `GPIO_OUTPUT_PP_MODE` | `1` | Output with pull-up. |
| `GPIO_OUTPUT_PD_MODE` | `2` | Output with pull-down. |
| `GPIO_INPUT_MODE` | `3` | Input, no pull resistor. |
| `GPIO_INPUT_PP_MODE` | `4` | Input with pull-up. |
| `GPIO_INPUT_PD_MODE` | `5` | Input with pull-down. |
| `GPIO_ASYNC_RISING_TRIGER_INT_MODE` | `6` | Interrupt on rising edge, asynchronous. |
| `GPIO_ASYNC_FALLING_TRIGER_INT_MODE` | `7` | Interrupt on falling edge, asynchronous. |
| `GPIO_ASYNC_HIGH_LEVEL_INT_MODE` | `8` | Interrupt on high level, asynchronous. |
| `GPIO_ASYNC_LOW_LEVEL_INT_MODE` | `9` | Interrupt on low level, asynchronous. |
| `GPIO_SYNC_RISING_TRIGER_INT_MODE` | `10` | Interrupt on rising edge, synchronous. |
| `GPIO_SYNC_FALLING_TRIGER_INT_MODE` | `11` | Interrupt on falling edge, synchronous. |
| `GPIO_SYNC_HIGH_LEVEL_INT_MODE` | `12` | Interrupt on high level, synchronous. |
| `GPIO_SYNC_LOW_LEVEL_INT_MODE` | `13` | Interrupt on low level, synchronous. |
| `GPIO_HZ_MODE` | `14` | High impedance: input, output and pull resistors off; the pin interrupt is masked. |

## hal_uart.h { #hal_uart-h }

`#include "hal_uart.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_uart.h))

UART driver: configuration, polling and DMA transfers, interrupts.

Each UART has a device record ([`uart_device_t`](#uart_device_t)) initialised from the board configuration (`UART0_CONFIG`, `UART1_CONFIG`). [`uart_init()`](#uart_init) applies it and selects the transfer mode with `COMMON_CAPS_*` flags:

- Polling (flags 0): [`uart_write()`](#uart_write) blocks until the data is in the TX FIFO; [`uart_read()`](#uart_read) and [`uart_read_available()`](#uart_read_available) return the bytes already received.
- DMA (`COMMON_CAPS_DMA_TX` / `COMMON_CAPS_DMA_RX`): attach a configured DMA channel (see [`hal_dma.h`](#hal_dma-h)) with `UART_CTRL_ATTACH_TX_DMA` / `UART_CTRL_ATTACH_RX_DMA` after [`uart_init()`](#uart_init); [`uart_write()`](#uart_write) and [`uart_read()`](#uart_read) then start a DMA transfer and return immediately.

For interrupt-driven reception, register a callback with [`uart_set_callback()`](#uart_set_callback) and enable the interrupts with `UART_CTRL_SET_INT`, then read the data with [`uart_read_available()`](#uart_read_available) when `UART_EVENT_RX_FIFO` arrives. Compile-time line options are in [`uart_config.h`](#uart_config-h).

### uart_init { #uart_init }

```c
int uart_init(int uart_id, uint16_t oflag);
```

Initialise a UART from its device record.

Applies baud rate, data bits, stop bits and parity from the device record (board configuration or [`uart_set_baudrate()`](#uart_set_baudrate)), the options of [`uart_config.h`](#uart_config-h), the FIFO threshold and the RX time-out (`UART_DEFAULT_RTO_TIMEOUT`); enables TX free-run mode and the RX deglitch filter; clears both FIFOs; enables the transmitter and receiver; and installs the UART interrupt handler. All UART interrupts stay masked and the CPU interrupt stays disabled until `UART_CTRL_SET_INT`. Any DMA channels attached earlier are detached.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). |
| `oflag` | Transfer mode, OR of `COMMON_CAPS_*` flags: `COMMON_CAPS_DMA_TX` / `COMMON_CAPS_DMA_RX` enable the FIFO DMA requests and make [`uart_write()`](#uart_write) / [`uart_read()`](#uart_read) use DMA; `COMMON_CAPS_INT_TX` / `COMMON_CAPS_INT_RX` make them return -2; 0 selects polling. |

**Returns:** 0.

### uart_uninit { #uart_uninit }

```c
int uart_uninit(int uart_id);
```

Reset a UART.

Applies a software reset to the UART block. Call [`uart_init()`](#uart_init) before using the UART again.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). Other values are ignored. |

**Returns:** 0.

### uart_ioctl { #uart_ioctl }

```c
int uart_ioctl(int uart_id, int cmd, void *args);
```

Execute a UART control command.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). |
| `cmd` | Command, one of the `UART_CTRL_*` values. |
| `args` | Command argument; see the description of each command. |

**Returns:** For `UART_CTRL_GET_TX_FIFO` and `UART_CTRL_GET_RX_FIFO`: the FIFO count. 0 for all other commands; unknown commands are ignored.

### uart_write { #uart_write }

```c
int uart_write(int uart_id, const void *buffer, uint32_t size);
```

Send data.

- Polling mode: blocks until every byte has been written into the TX FIFO (not until it has left the wire).
- DMA mode: starts a DMA transfer from `buffer` and returns immediately. The buffer must stay valid until the transfer completes (DMA callback, or [`dma_channel_check_busy()`](#hal_dma-h-macros)); a new call stops a transfer still in progress. The data cache is not cleaned for `buffer`.
- Interrupt mode (`COMMON_CAPS_INT_TX`): not supported, returns -2.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). |
| `buffer` | Data to send. |
| `size` | Number of bytes to send. |

**Returns:** 0 on success. In polling mode, a non-zero status if the TX FIFO stays full for too long. In DMA mode, -1 if no TX DMA channel is attached, or the negative error of [`dma_reload()`](#dma_reload). -2 in interrupt mode.

### uart_read { #uart_read }

```c
int uart_read(int uart_id, void *buffer, uint32_t size);
```

Receive data.

- Polling mode: does not block; copies up to `size` bytes that are already in the RX FIFO.
- DMA mode: starts a DMA transfer of exactly `size` bytes into `buffer` and returns immediately; completion is reported by the DMA callback. The data cache is not invalidated for `buffer`.
- Interrupt mode (`COMMON_CAPS_INT_RX`): not supported, returns -2.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). |
| `buffer` | Buffer for the received data. |
| `size` | Size of `buffer` in bytes. |

**Returns:** Polling mode: number of bytes copied (0 if none). DMA mode: 0 on success, -1 if no RX DMA channel is attached, or the negative error of [`dma_reload()`](#dma_reload). -2 in interrupt mode.

### uart_int_tx_enable { #uart_int_tx_enable }

```c
int uart_int_tx_enable(uint8_t id);
```

Unmask the TX FIFO request interrupt.

The UART interrupt must also be enabled in the CPU (`UART_CTRL_SET_INT`) for `UART_EVENT_TX_FIFO` to be delivered.

| Parameter | Description |
|---|---|
| `id` | Hardware UART number (0 or 1). |

**Returns:** 0.

### uart_int_tx_disable { #uart_int_tx_disable }

```c
int uart_int_tx_disable(uint8_t id);
```

Mask the TX FIFO request interrupt.

| Parameter | Description |
|---|---|
| `id` | Hardware UART number (0 or 1). |

**Returns:** 0.

### uart_set_baudrate { #uart_set_baudrate }

```c
void uart_set_baudrate(int uart_id, int baudrate);
```

Store the baud rate used by the next [`uart_init()`](#uart_init).

The hardware is not changed; use `UART_CTRL_CONFIG` to change the baud rate of a running UART.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). |
| `baudrate` | Baud rate in bit/s. |

### uart_set_callback { #uart_set_callback }

```c
void uart_set_callback(int uart_id, void *args);
```

Set the event callback of a UART.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). |
| `args` | Callback function with the signature of `uart_device_t::callback`, or NULL to remove it. |

### uart_getDevice { #uart_getDevice }

```c
uart_device_t * uart_getDevice(int uart_id);
```

Get the driver's device record of a UART.

| Parameter | Description |
|---|---|
| `uart_id` | UART index, [`uart_index_type`](#uart_index_type). Not range-checked. |

**Returns:** Pointer to the internal record.

### uart_read_available { #uart_read_available }

```c
int uart_read_available(int uart_id, void *buffer, uint32_t max_size);
```

Read available data from the UART RX FIFO (non-blocking).

Copies the bytes already in the RX FIFO, up to `max_size`, in any transfer mode. It can be called from the UART callback.

| Parameter | Description |
|---|---|
| `uart_id` | Hardware UART number (`UART0_INDEX` or `UART1_INDEX`). |
| `buffer` | Buffer to store received data. |
| `max_size` | Maximum number of bytes to read. |

**Returns:** Number of bytes actually read (0 if the FIFO is empty).

### Anonymous enum { #hal_uart-h-enum }

Commands for [`uart_ioctl()`](#uart_ioctl).

| Name | Value | Description |
|---|---|---|
| `UART_CTRL_SET_INT` | `0` | Unmask the interrupts given in `args` (non-zero OR of [`uart_it_type`](#uart_it_type) flags) and enable the UART interrupt in the CPU. |
| `UART_CTRL_CLR_INT` |  | Mask the interrupts given in `args` (non-zero OR of [`uart_it_type`](#uart_it_type) flags) and disable the UART interrupt in the CPU, which stops all callbacks of this UART. |
| `UART_CTRL_RESUME` |  | Enable the transmitter and receiver. |
| `UART_CTRL_SUSPEND` |  | Disable the transmitter and receiver. |
| `UART_CTRL_CONFIG` |  | Reprogram the line settings from `args` (`uart_param_cfg_t *`) and clear both FIFOs. The device record is not updated. |
| `UART_CTRL_ATTACH_TX_DMA` |  | Use DMA channel `(int)args` for [`uart_write()`](#uart_write) in DMA mode. The channel must be configured memory-to-peripheral with the UART TX request line. |
| `UART_CTRL_ATTACH_RX_DMA` |  | Use DMA channel `(int)args` for [`uart_read()`](#uart_read) in DMA mode. The channel must be configured peripheral-to-memory with the UART RX request line. |
| `UART_CTRL_TX_DMA_SUSPEND` |  | Disable the TX DMA request and clear `COMMON_CAPS_DMA_TX`, so [`uart_write()`](#uart_write) stops using DMA. |
| `UART_CTRL_RX_DMA_SUSPEND` |  | Disable the RX DMA request and clear `COMMON_CAPS_DMA_RX`, so [`uart_read()`](#uart_read) stops using DMA. |
| `UART_CTRL_TX_DMA_RESUME` |  | Enable the TX DMA request and set `COMMON_CAPS_DMA_TX`. |
| `UART_CTRL_RX_DMA_RESUME` |  | Enable the RX DMA request and set `COMMON_CAPS_DMA_RX`. |
| `UART_CTRL_GET_TX_FIFO` |  | [`uart_ioctl()`](#uart_ioctl) returns the number of free entries in the TX FIFO. |
| `UART_CTRL_GET_RX_FIFO` |  | [`uart_ioctl()`](#uart_ioctl) returns the number of bytes waiting in the RX FIFO. |
| `UART_CTRL_CLEAR_TX_FIFO` |  | Discard the contents of the TX FIFO. |
| `UART_CTRL_CLEAR_RX_FIFO` |  | Discard the contents of the RX FIFO. |
| `UART_CTRL_SET_CALLBACK` |  | Set the event callback; `args` is a function pointer with the signature of `uart_device_t::callback`. |
| `UART_CTRL_TX_FLUSH` |  | Not implemented: [`uart_ioctl()`](#uart_ioctl) ignores it and returns 0. |
| `UART_CTRL_BAUDRATE_SET` |  | Not implemented: [`uart_ioctl()`](#uart_ioctl) ignores it and returns 0. Use `UART_CTRL_CONFIG` to change the baud rate. |
| `UART_CTRL_TX_TRIGGER_OFF` |  | Mask the TX FIFO request interrupt, as [`uart_int_tx_disable()`](#uart_int_tx_disable). |
| `UART_CTRL_TX_TRIGGER_ON` |  | Unmask the TX FIFO request interrupt, as [`uart_int_tx_enable()`](#uart_int_tx_enable). |

### uart_index_type { #uart_index_type }

UART index (the `uart_id` argument of the UART functions).

| Name | Value | Description |
|---|---|---|
| `UART0_INDEX` | `0` | UART0. |
| `UART1_INDEX` |  | UART1. |
| `UART_MAX_INDEX` |  | Number of UARTs. |

### uart_databits_t { #uart_databits_t }

Number of data bits per character.

| Name | Value | Description |
|---|---|---|
| `UART_DATA_LEN_5` | `0` | Data length is 5 bits. |
| `UART_DATA_LEN_6` | `1` | Data length is 6 bits. |
| `UART_DATA_LEN_7` | `2` | Data length is 7 bits. |
| `UART_DATA_LEN_8` | `3` | Data length is 8 bits. |

### uart_stopbits_t { #uart_stopbits_t }

Number of stop bits.

| Name | Value | Description |
|---|---|---|
| `UART_STOP_ZERO_D_FIVE` | `0` | 0.5 stop bit |
| `UART_STOP_ONE` | `1` | 1 stop bit |
| `UART_STOP_ONE_D_FIVE` | `2` | 1.5 stop bit |
| `UART_STOP_TWO` | `3` | 2 stop bits |

### uart_parity_t { #uart_parity_t }

Parity mode.

| Name | Value | Description |
|---|---|---|
| `UART_PAR_NONE` | `0` | No parity. |
| `UART_PAR_ODD` | `1` | Parity bit is odd. |
| `UART_PAR_EVEN` | `2` | Parity bit is even. |

### uart_event_type { #uart_event_type }

Events passed to the UART callback (`uart_device_t::callback`).

The callback runs in the UART interrupt handler.

| Name | Value | Description |
|---|---|---|
| `UART_EVENT_TX_END` |  | TX transfer-end interrupt (`UART_TX_END_IT`). |
| `UART_EVENT_TX_FIFO` |  | TX FIFO request interrupt (`UART_TX_FIFO_IT`): the TX FIFO can take more data. Reported on every interrupt while the request is active; the request clears when data is written. |
| `UART_EVENT_RX_END` |  | RX transfer-end interrupt (`UART_RX_END_IT`). |
| `UART_EVENT_RX_FIFO` |  | Data is waiting in the RX FIFO: RX FIFO request interrupt (`UART_RX_FIFO_IT`) or RX time-out (`UART_RTO_IT`). Read the data with [`uart_read_available()`](#uart_read_available). |
| `UART_EVENT_RTO` |  | Not delivered: the driver reports an RX time-out as `UART_EVENT_RX_FIFO`. |
| `UART_EVENT_PCE` |  | RX parity error (`UART_PCE_IT`). |
| `UART_EVENT_TX_FER` |  | TX FIFO overflow or underflow (`UART_TX_FER_IT`). |
| `UART_EVENT_RX_FER` |  | RX FIFO overflow or underflow (`UART_RX_FER_IT`). |
| `UART_EVENT_UNKNOWN` |  | Not generated by the driver. |

### uart_it_type { #uart_it_type }

Interrupt flags for `UART_CTRL_SET_INT` and `UART_CTRL_CLR_INT`.

| Name | Value | Description |
|---|---|---|
| `UART_TX_END_IT` | `1 << 0` | TX transfer end. |
| `UART_RX_END_IT` | `1 << 1` | RX transfer end. |
| `UART_TX_FIFO_IT` | `1 << 2` | TX FIFO request (TX FIFO can take more data). |
| `UART_RX_FIFO_IT` | `1 << 3` | RX FIFO request (data waiting in the RX FIFO). |
| `UART_RTO_IT` | `1 << 4` | RX time-out (line idle after received data). |
| `UART_PCE_IT` | `1 << 5` | RX parity error. |
| `UART_TX_FER_IT` | `1 << 6` | TX FIFO overflow or underflow. |
| `UART_RX_FER_IT` | `1 << 7` | RX FIFO overflow or underflow. |
| `UART_ALL_IT` | `1 << 8` | Despite its name, the driver maps this bit to the receiver's LIN sync-field error interrupt, not to all interrupts. OR the individual flags to select several interrupts. |

### uart_param_cfg_t { #uart_param_cfg_t }

Line settings for `UART_CTRL_CONFIG`.

| Field | Type | Description |
|---|---|---|
| `baudrate` | `uint32_t` | Baud rate in bit/s. |
| `databits` | `uart_databits_t` | Data bits per character. |
| `stopbits` | `uart_stopbits_t` | Stop bits. |
| `parity` | `uart_parity_t` | Parity mode. |

### uart_device_t { #uart_device_t }

Configuration and state of one UART.

The driver keeps one record per UART; get it with [`uart_getDevice()`](#uart_getDevice).

| Field | Type | Description |
|---|---|---|
| `id` | `uint8_t` | Hardware UART number (0 or 1). |
| `caps` | `uint16_t` | Mode flags (`COMMON_CAPS_*`) set by [`uart_init()`](#uart_init) and by the DMA suspend/resume commands. |
| `baudrate` | `uint32_t` | Baud rate in bit/s applied by [`uart_init()`](#uart_init). |
| `databits` | `uart_databits_t` | Data bits applied by [`uart_init()`](#uart_init). |
| `stopbits` | `uart_stopbits_t` | Stop bits applied by [`uart_init()`](#uart_init). |
| `parity` | `uart_parity_t` | Parity applied by [`uart_init()`](#uart_init). |
| `fifo_threshold` | `uint8_t` | TX and RX FIFO threshold written by [`uart_init()`](#uart_init); a DMA request is not asserted while the FIFO count is below it. |
| `tx_dma` | `int` | DMA channel for [`uart_write()`](#uart_write) in DMA mode, or -1 (reset to -1 by [`uart_init()`](#uart_init)). |
| `rx_dma` | `int` | DMA channel for [`uart_read()`](#uart_read) in DMA mode, or -1 (reset to -1 by [`uart_init()`](#uart_init)). |
| `callback` | `void(*)(void *dev, void *args, uint32_t size, uint32_t event)` | Event callback, called from the UART interrupt handler with this record as `dev`, NULL as `args`, 0 as `size` and a [`uart_event_type`](#uart_event_type) value as `event`. NULL disables it. |

### Macros { #hal_uart-h-macros }

| Name | Value | Description |
|---|---|---|
| `UART_FIFO_LEN` | `128` | Buffer-length constant (128). The UART driver does not use it; query the FIFO levels with `UART_CTRL_GET_TX_FIFO` and `UART_CTRL_GET_RX_FIFO`. |

## uart_config.h { #uart_config-h }

`#include "uart_config.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/default_config/uart_config.h))

Compile-time UART line options used by the UART driver ([`hal_uart.h`](#hal_uart-h)).

[`uart_init()`](#uart_init) and `UART_CTRL_CONFIG` apply these values to every UART. A value of 1 enables an option, 0 disables it.

### Macros { #uart_config-h-macros }

| Name | Value | Description |
|---|---|---|
| `UART_CTS_FLOWCONTROL_ENABLE` | `(0)` | TX CTS hardware flow control. |
| `UART_RTS_FLOWCONTROL_ENABLE` | `(0)` | Software control of the RX RTS output. |
| `UART_RX_DEGLITCH_ENABLE` | `(0)` | Not used: the driver always enables the RX deglitch filter. |
| `UART_MSB_FIRST_ENABLE` | `(0)` | Send and receive each byte MSB first (0 = LSB first). |
| `UART_TX_SWCONTROL_ENABLE` | `(0)` | Software control of the TX output. |
| `UART_TX_LINMODE_ENABLE` | `(0)` | TX LIN mode: a LIN header is sent before the data. |
| `UART_RX_LINMODE_ENABLE` | `(0)` | RX LIN mode: a LIN header is required and checked before the data. |
| `UART_TX_BREAKBIT_CNT` | `(0)` | TX break length for LIN mode; the hardware adds 8 bit times to this count. |
| `UART_FIFO_MAX_LEN` | `128` | Buffer-length constant; not used by the UART driver. |
| `UART_DEFAULT_RTO_TIMEOUT` | `100` | RX time-out value programmed by [`uart_init()`](#uart_init); see `UART_RTO_IT`. |

## hal_spi.h { #hal_spi-h }

`#include "hal_spi.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_spi.h))

SPI controller driver: configuration, blocking transfers, FIFO and DMA control, interrupt callback.

The HAL keeps one [`spi_device_t`](#spi_device_t) per controller, initialised from the board's `SPI0_CONFIG` / `SPI1_CONFIG` defaults. Typical sequence: fill an [`spi_device_t`](#spi_device_t) and pass it to [`spi_setConfig()`](#spi_setConfig), then [`spi_init()`](#spi_init), [`spi_enable()`](#spi_enable) with 1, then [`spi_transmit()`](#spi_transmit), [`spi_receive()`](#spi_receive) or [`spi_transmit_receive()`](#spi_transmit_receive). [`spi_init()`](#spi_init) programs the hardware from the stored configuration, so call [`spi_setConfig()`](#spi_setConfig) first.

Transfer lengths count frames: a frame is 1, 2 or 4 bytes of the buffer for 8-, 16- and 24/32-bit frame sizes. The transfer functions poll the FIFOs without a timeout.

### spi_init { #spi_init }

```c
int spi_init(int spi_id);
```

Program the controller from its stored configuration.

Disables the controller, applies the clock, bit and byte order, polarity, phase, frame size, de-glitch and FIFO settings of the configuration set with [`spi_setConfig()`](#spi_setConfig) (or the board default), flushes both FIFOs, unmasks all SPI interrupt sources in the controller and registers the SPI0 interrupt handler when `caps` requests interrupts. The controller stays disabled; call [`spi_enable()`](#spi_enable).

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)); not range-checked. |

**Returns:** 0 (always).

!!! note "Note"
    `pin_swap_enable` and the master/slave pad selection act on SPI0, and interrupt callbacks are delivered for SPI0 only.

### spi_deinit { #spi_deinit }

```c
int spi_deinit(int spi_id);
```

Disable the controller and reset it.

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |

**Returns:** 0 (always).

### spi_setConfig { #spi_setConfig }

```c
void spi_setConfig(spi_device_t *dev);
```

Store a configuration for the controller given by `dev->id`.

The structure is copied; the hardware is not touched until [`spi_init()`](#spi_init).

| Parameter | Description |
|---|---|
| `dev` | Configuration to copy. |

### spi_enable { #spi_enable }

```c
int spi_enable(int spi_id, int en);
```

Enable or disable the controller.

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |
| `en` | Non-zero enables, 0 disables. |

**Returns:** 0 (always).

### spi_ioctl { #spi_ioctl }

```c
int spi_ioctl(int spi_id, int cmd, void *args);
```

Run a control command.

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |
| `cmd` | Command, an `SPI_CTRL_*` value. |
| `args` | Command argument, see the command list. |

**Returns:** The FIFO count or busy status for the `SPI_CTRL_GET_*` commands, otherwise 0. Unknown commands are ignored.

### spi_transmit { #spi_transmit }

```c
int spi_transmit(int spi_id, void *buffer, uint32_t size);
```

Send `size` frames and wait until the transfer has finished.

Received data is discarded.

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |
| `buffer` | Data to send. |
| `size` | Number of frames. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `3` | The configured frame size is invalid. |

### spi_receive { #spi_receive }

```c
int spi_receive(int spi_id, void *buffer, uint32_t size);
```

Receive `size` frames, sending all-ones frames meanwhile.

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |
| `buffer` | Receive buffer. |
| `size` | Number of frames. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `3` | The configured frame size is invalid. |

### spi_transmit_receive { #spi_transmit_receive }

```c
int spi_transmit_receive(int spi_id, const void *send_buf, void *recv_buf, uint32_t length);
```

Send and receive `length` frames in full duplex.

| Parameter | Description |
|---|---|
| `spi_id` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |
| `send_buf` | Data to send. |
| `recv_buf` | Receive buffer. |
| `length` | Number of frames. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `3` | The configured frame size is invalid. |

### Anonymous enum { #hal_spi-h-enum }

Commands for [`spi_ioctl()`](#spi_ioctl).

Unless stated otherwise `args` is not used and [`spi_ioctl()`](#spi_ioctl) returns 0.

| Name | Value | Description |
|---|---|---|
| `SPI_CTRL_ATTACH_TX_DMA` | `0` | Enable TX FIFO DMA requests (same as [`SPI_CTRL_TX_DMA_RESUME`](#hal_spi-h-enum)). |
| `SPI_CTRL_ATTACH_RX_DMA` |  | Enable RX FIFO DMA requests (same as [`SPI_CTRL_RX_DMA_RESUME`](#hal_spi-h-enum)). |
| `SPI_CTRL_CONFIG_CLOCK` |  | Set the SCLK frequency; `args` is the frequency in Hz cast to `void *`. The highest achievable frequency not above it is used. |
| `SPI_CTRL_TX_DMA_SUSPEND` |  | Disable TX FIFO DMA requests and clear `COMMON_CAPS_DMA_TX` in `caps`. |
| `SPI_CTRL_RX_DMA_SUSPEND` |  | Disable RX FIFO DMA requests and clear `COMMON_CAPS_DMA_RX` in `caps`. |
| `SPI_CTRL_TX_DMA_RESUME` |  | Enable TX FIFO DMA requests and set `COMMON_CAPS_DMA_TX` in `caps`. |
| `SPI_CTRL_RX_DMA_RESUME` |  | Enable RX FIFO DMA requests and set `COMMON_CAPS_DMA_RX` in `caps`. |
| `SPI_CTRL_GET_TX_FIFO` |  | Return the TX FIFO free count reported by the hardware. |
| `SPI_CTRL_GET_RX_FIFO` |  | Return the RX FIFO fill count reported by the hardware. |
| `SPI_CTRL_CLEAR_TX_FIFO` |  | Flush the TX FIFO. |
| `SPI_CTRL_CLEAR_RX_FIFO` |  | Flush the RX FIFO. |
| `SPI_CTRL_GET_BUS_BUSY_STATUS` |  | Return 1 while the bus is busy, 0 when idle. |
| `SPI_CTRL_SET_FRAME_SIZE` |  | Flush both FIFOs and set the frame size; `args` is an `SPI_DATASIZE_*` value cast to `void *`. |
| `SPI_CTRL_SET_CALLBACK` |  | Set the interrupt callback; `args` is the function pointer (see `spi_device_t::callback`). |
| `SPI_CTRL_SET_INT_MASK` |  | Mask an interrupt source; `args` is an [`HAL_SPI_INT_Type`](#HAL_SPI_INT_Type) value cast to `void *`. |
| `SPI_CTRL_SET_INT_UNMASK` |  | Unmask an interrupt source; `args` is an [`HAL_SPI_INT_Type`](#HAL_SPI_INT_Type) value cast to `void *`. |

### spi_index_type { #spi_index_type }

SPI controller index, passed as `spi_id`.

| Name | Value | Description |
|---|---|---|
| `SPI0_INDEX` |  | SPI controller 0. |
| `SPI1_INDEX` |  | SPI controller 1. |
| `SPI_MAX_INDEX` |  | Number of controllers; not a valid index. |

### HAL_SPI_INT_Type { #HAL_SPI_INT_Type }

SPI interrupt sources, passed as the `event` argument of the callback and as the `args` of [`SPI_CTRL_SET_INT_MASK`](#hal_spi-h-enum) and [`SPI_CTRL_SET_INT_UNMASK`](#hal_spi-h-enum).

| Name | Value | Description |
|---|---|---|
| `HAL_SPI_INT_END` |  | Transfer end; master and slave mode. |
| `HAL_SPI_INT_TX_FIFO_REQ` |  | TX FIFO request: TX FIFO count above the threshold. |
| `HAL_SPI_INT_RX_FIFO_REQ` |  | RX FIFO request: RX FIFO count above the threshold. |
| `HAL_SPI_INT_SLAVE_TIMEOUT` |  | Slave mode: bus idle for the configured time-out. |
| `HAL_SPI_INT_SLAVE_UNDERRUN` |  | Slave mode: TX data not ready during a transfer. |
| `HAL_SPI_INT_FIFO_ERROR` |  | TX or RX FIFO overflow or underflow. |
| `HAL_SPI_INT_ALL` |  | All interrupt sources (mask and unmask only). |

### spi_event_type { #spi_event_type }

SPI event codes.

Not used by this driver: the callback receives [`HAL_SPI_INT_Type`](#HAL_SPI_INT_Type) values.

| Name | Value | Description |
|---|---|---|
| `SPI_EVENT_TX_FIFO` |  | TX FIFO event. |
| `SPI_EVENT_RX_FIFO` |  | RX FIFO event. |
| `SPI_EVENT_UNKNOWN` |  | Unknown event. |

### spi_device_t { #spi_device_t }

SPI controller configuration and state.

Fill it and pass it to [`spi_setConfig()`](#spi_setConfig) before [`spi_init()`](#spi_init).

| Field | Type | Description |
|---|---|---|
| `caps` | `uint16_t` | Capability flags: `COMMON_CAPS_INT_TX` or `COMMON_CAPS_INT_RX` register the interrupt handler; `COMMON_CAPS_DMA_TX` and `COMMON_CAPS_DMA_RX` enable the FIFO DMA requests. |
| `id` | `uint8_t` | Controller index ([`SPI0_INDEX`](#spi_index_type) or [`SPI1_INDEX`](#spi_index_type)). |
| `clk` | `uint32_t` | SCLK frequency in Hz; 0 or values above 48 MHz select 48 MHz. |
| `mode` | `uint8_t` | [`SPI_MASTER_MODE`](#hal_spi-h-macros) or [`SPI_SLAVE_MODE`](#hal_spi-h-macros). |
| `direction` | `uint8_t` | Bit and byte order, an `SPI_*_DIRECTION_FIRST` value. |
| `ignore_cs` | `uint8_t` | Non-zero selects 3-pin mode without a chip-select signal; drive chip select with a GPIO when the device needs one. |
| `clk_polaraity` | `uint8_t` | Clock polarity: [`SPI_POLARITY_LOW`](#hal_spi-h-macros) or [`SPI_POLARITY_HIGH`](#hal_spi-h-macros). |
| `clk_phase` | `uint8_t` | Clock phase: [`SPI_PHASE_1EDGE`](#hal_spi-h-macros) or [`SPI_PHASE_2EDGE`](#hal_spi-h-macros). |
| `datasize` | `uint8_t` | Frame size, an `SPI_DATASIZE_*` value. |
| `fifo_threshold` | `uint8_t` | TX and RX FIFO threshold for the FIFO request interrupts and DMA. |
| `pin_swap_enable` | `uint8_t` | Non-zero swaps the MOSI and MISO pins (SPI0 pin swap). |
| `delitch_cnt` | `uint8_t` | Input de-glitch count; non-zero enables the de-glitch filter. |
| `callback` | `void(*)(void *dev, uint32_t event)` | Interrupt callback, called from the interrupt handler with `dev` pointing at this structure and `event` an [`HAL_SPI_INT_Type`](#HAL_SPI_INT_Type) value; may be NULL. |

### Macros { #hal_spi-h-macros }

| Name | Value | Description |
|---|---|---|
| `SPI_LSB_BYTE0_DIRECTION_FIRST` | `0` | Each byte LSB first; byte 0 of a multi-byte frame first. |
| `SPI_LSB_BYTE3_DIRECTION_FIRST` | `1` | Each byte LSB first; byte 3 of a multi-byte frame first. |
| `SPI_MSB_BYTE0_DIRECTION_FIRST` | `2` | Each byte MSB first; byte 0 of a multi-byte frame first. |
| `SPI_MSB_BYTE3_DIRECTION_FIRST` | `3` | Each byte MSB first; byte 3 of a multi-byte frame first. |
| `SPI_DATASIZE_8BIT` | `0` | 8-bit frames; 1 buffer byte per frame. |
| `SPI_DATASIZE_16BIT` | `1` | 16-bit frames; 2 buffer bytes per frame. |
| `SPI_DATASIZE_24BIT` | `2` | 24-bit frames; 4 buffer bytes per frame. |
| `SPI_DATASIZE_32BIT` | `3` | 32-bit frames; 4 buffer bytes per frame. |
| `SPI_POLARITY_LOW` | `0` | SCLK idles low (CPOL = 0). |
| `SPI_POLARITY_HIGH` | `1` | SCLK idles high (CPOL = 1). |
| `SPI_PHASE_1EDGE` | `0` | Data sampled on the first SCLK edge (CPHA = 0). |
| `SPI_PHASE_2EDGE` | `1` | Data sampled on the second SCLK edge (CPHA = 1). |
| `SPI_SLAVE_MODE` | `0` | Slave. |
| `SPI_MASTER_MODE` | `1` | Master. |
| `SPI_TRANSFER_TYPE_8BIT` | `0` | 8-bit transfers. |
| `SPI_TRANSFER_TYPE_16BIT` | `1` | 16-bit transfers. |
| `SPI_TRANSFER_TPYE_24BIT` | `2` | 24-bit transfers (the name is spelled this way). |
| `SPI_TRANSFER_TYPE_32BIT` | `3` | 32-bit transfers. |

## hal_i2c.h { #hal_i2c-h }

`#include "hal_i2c.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_i2c.h))

I2C master driver: blocking register-style transfers.

Each controller has a configuration record initialised from the board configuration (`I2C0_CONFIG`, `I2C1_CONFIG`); replace it with [`i2c_setConfig()`](#i2c_setConfig) if needed, call [`i2c_init()`](#i2c_init), then exchange data with [`i2c_transfer()`](#i2c_transfer). A register read or write is one [`i2c_msg_t`](#i2c_msg_t) with a `SUB_ADDR_*` flag: the controller sends the register (sub-)address before the data.

### i2c_init { #i2c_init }

```c
int i2c_init(int i2c_id);
```

Initialise an I2C controller from its configuration record.

In `I2C_HW_MODE`, writes `i2c_device_t::phase` to the phase-period registers. Pin multiplexing is not configured here.

| Parameter | Description |
|---|---|
| `i2c_id` | Controller index, [`i2c_index_type`](#i2c_index_type). |

**Returns:** 0.

### i2c_transfer { #i2c_transfer }

```c
int i2c_transfer(int i2c_id, i2c_msg_t msgs[], uint32_t num);
```

Execute an I2C master transfer (blocking).

Sends or receives the first message with a 7-bit address. The function busy-waits until the transfer ends or times out.

| Parameter | Description |
|---|---|
| `i2c_id` | Controller index, [`i2c_index_type`](#i2c_index_type). |
| `msgs` | Messages; received data is stored in the `buf` of a read message. |
| `num` | Number of messages in `msgs`. |

**Returns:** 0 on success (also when `num` is 0 or in `I2C_SW_MODE`), or the non-zero timeout status of the low-level transfer, which also covers a slave that does not acknowledge.

!!! warning "Warning"
    Only `msgs[0]` is executed; the function returns after the first message. Issue one call per message.

### i2c_setConfig { #i2c_setConfig }

```c
void i2c_setConfig(i2c_device_t *dev);
```

Replace the configuration record of a controller.

Copies `dev` into the record of controller `dev->id`. Call [`i2c_init()`](#i2c_init) afterwards to apply it.

| Parameter | Description |
|---|---|
| `dev` | New configuration. |

### i2c_index_type { #i2c_index_type }

I2C controller index (the `i2c_id` argument of the I2C functions).

Only the controllers enabled in the board configuration are listed, so the numbering depends on the build.

| Name | Value | Description |
|---|---|---|
| `I2C0_INDEX` |  | I2C0 (present when `BSP_USING_I2C0` is defined). |
| `I2C1_INDEX` |  | I2C1 (present when `BSP_USING_I2C1` is defined). |
| `I2C_MAX_INDEX` |  | Number of enabled I2C controllers. |

### i2c_msg_t { #i2c_msg_t }

One I2C message for [`i2c_transfer()`](#i2c_transfer).

| Field | Type | Description |
|---|---|---|
| `slaveaddr` | `uint8_t` | 7-bit slave address, without the R/W bit. |
| `subaddr` | `uint32_t` | Register (sub-)address; its length is set by the `SUB_ADDR_*` flag. |
| `flags` | `uint16_t` | `I2C_WR` or `I2C_RD`, ORed with one `SUB_ADDR_*` flag. |
| `len` | `uint16_t` | Number of data bytes, 1 to 256; longer messages are truncated to 256 bytes. |
| `buf` | `uint8_t *` | Data to send, or buffer for the received data. |

### i2c_device_t { #i2c_device_t }

Configuration of one I2C controller.

| Field | Type | Description |
|---|---|---|
| `id` | `uint8_t` | Hardware controller number. |
| `mode` | `uint8_t` | `I2C_HW_MODE` or `I2C_SW_MODE`. |
| `phase` | `uint32_t` | Value written to the start, stop and data phase-period fields by [`i2c_init()`](#i2c_init). On IPRO7 every [`i2c_transfer()`](#i2c_transfer) reprograms the bus to 400 kHz, which replaces this setting. |

### Macros { #hal_i2c-h-macros }

| Name | Value | Description |
|---|---|---|
| `I2C_WR` | `0x0000` | Write: send the data in `i2c_msg_t::buf`. |
| `I2C_RD` | `0x0001` | Read: receive data into `i2c_msg_t::buf`. |
| `I2C_RW_MASK` | `0x0001` | Mask of the direction bit. |
| `SUB_ADDR_0BYTE` | `0x0010` | No sub-address phase. |
| `SUB_ADDR_1BYTE` | `0x0020` | Send a 1-byte sub-address from `i2c_msg_t::subaddr`. |
| `SUB_ADDR_2BYTE` | `0x0040` | Send a 2-byte sub-address from `i2c_msg_t::subaddr`. The controller sends the low byte first; swap the two bytes for a device that expects the high byte first. |
| `I2C_HW_MODE` | `0` | Use the I2C controller. |
| `I2C_SW_MODE` | `1` | Software mode; not implemented: [`i2c_init()`](#i2c_init) and [`i2c_transfer()`](#i2c_transfer) do nothing and return 0. |

## hal_pwm.h { #hal_pwm-h }

`#include "hal_pwm.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pwm.h))

PWM driver: one PWM group with four channels; period, duty cycle and polarity control.

The IPRO7 has a single PWM group, so pass 0 as `pwm_id`. [`pwm_init()`](#pwm_init) sets up the group (counter clock divider 32, period 1000 counts) with all channel outputs disabled; `PWM_CTRL_RESUME` starts the group and enables the outputs. The output frequency is the PWM counter clock divided by the period.

Per-channel commands act on the channel recorded in `pwm_device_t::ch` of device slot `pwm_id` (channel 0 for slot 0 with the default board configuration). For finer control, use the PWM driver in drv_pwm.h directly.

### pwm_init { #pwm_init }

```c
int pwm_init(int pwm_id, uint16_t caps);
```

Initialize the PWM group.

Selects the crystal clock with a divider of 32 and a period of 1000 counts, graceful stop mode, and configures all four channels with their outputs disabled. Prints the PWM clock frequency.

| Parameter | Description |
|---|---|
| `pwm_id` | PWM group (0). |
| `caps` | Capability flags; not used. |

**Returns:** Always 0.

### pwm_ioctl { #pwm_ioctl }

```c
int pwm_ioctl(int pwm_id, int cmd, void *args);
```

Control the PWM group or a channel.

| Parameter | Description |
|---|---|
| `pwm_id` | PWM group (0); also selects the device slot whose `pwm_device_t::ch` is used by per-channel commands. |
| `cmd` | Command, one of the `PWM_CTRL_*` codes. |
| `args` | Command argument; see the description of each `PWM_CTRL_*` code. |

| Return value | Description |
|---|---|
| `0` | Success (unknown commands are ignored). |
| `-1` | `PWM_CTRL_FREQUENCE_CONFIG` with a period larger than the PWM clock frequency in Hz. |

### pwm_close { #pwm_close }

```c
int pwm_close(int pwm_id, int ch);
```

Disable one channel's outputs or the whole PWM group.

| Parameter | Description |
|---|---|
| `pwm_id` | PWM group (0). |
| `ch` | Channel 0 to 3 to disable that channel's positive and negative outputs, or a value greater than 4 to disable the whole group. |

**Returns:** Always 0.

### Anonymous enum { #hal_pwm-h-enum }

Command codes for [`pwm_ioctl()`](#pwm_ioctl).

| Name | Value | Description |
|---|---|---|
| `PWM_CTRL_CONFIG` | `0` | Accepted; performs no action. |
| `PWM_CTRL_RESUME` |  | Enable the PWM group and the positive and negative outputs of channels 0, 2 and 3 (channel 1 is left unchanged). `args`: unused. |
| `PWM_CTRL_SUSPEND` |  | Disable the PWM group. `args`: unused. |
| `PWM_CTRL_FREQUENCE_CONFIG` |  | Set the period, in PWM counter clocks (16-bit). `args`: period cast to `void *`. [`pwm_ioctl()`](#pwm_ioctl) returns -1 if the value exceeds the PWM clock frequency in Hz. |
| `PWM_CTRL_DUTYCYCLE_CONFIG` |  | Set the low and high thresholds of the channel. `args`: pointer to a [`pwm_dutycycle_config_t`](#pwm_dutycycle_config_t). |
| `PWM_CTRL_POLARITY_CONFIG` |  | Set the positive and negative output polarity of the channel. `args`: pointer to a `PWM_CHx_CFG_Type` (drv_pwm.h); its `polP` and `polN` fields are used. |
| `PWM_CTRL_IT_PULSE_COUNT_CONFIG` |  | Not implemented; performs no action. |
| `PWM_CTRL_SET_CALLBACKG` |  | Store the event callback in `pwm_device_t::callback`. `args`: the function pointer. The driver does not enable the PWM interrupt, so the callback is not invoked in this release. |
| `PWM_CRTL_GET_PERIOD_CONFIG` |  | Read the current period. `args`: pointer to a `uint16_t` that receives it. |

### pwm_index_type { #pwm_index_type }

PWM device slot index (one per channel).

| Name | Value | Description |
|---|---|---|
| `PWM_CH0_INDEX` |  | Slot of PWM channel 0. |
| `PWM_CH1_INDEX` |  | Slot of PWM channel 1. |
| `PWM_CH2_INDEX` |  | Slot of PWM channel 2. |
| `PWM_CH3_INDEX` |  | Slot of PWM channel 3. |
| `PWM_MAX_INDEX` |  | Number of slots. |

### pwm_event_type { #pwm_event_type }

Event codes passed to `pwm_device_t::callback`.

| Name | Value | Description |
|---|---|---|
| `PWM_EVENT_COMPLETE` |  | PWM interrupt serviced. |

### pwm_dutycycle_config_t { #pwm_dutycycle_config_t }

Channel thresholds for `PWM_CTRL_DUTYCYCLE_CONFIG`.

Within each period the output is active from `threshold_low` to `threshold_high` counts, so the duty cycle is (`threshold_high` - `threshold_low`) / period.

| Field | Type | Description |
|---|---|---|
| `threshold_low` | `uint16_t` | Count at which the active phase starts. |
| `threshold_high` | `uint16_t` | Count at which the active phase ends. |

### pwm_device_t { #pwm_device_t }

PWM device slot.

The slots are initialized from the board configuration (`PWM_CH0_CONFIG` to `PWM_CH3_CONFIG`).

| Field | Type | Description |
|---|---|---|
| `caps` | `uint16_t` | Capability flags; not used by the driver. |
| `bActive` | `uint8_t` | Non-zero lets the driver's interrupt handler service this slot; not set by the driver. |
| `ch` | `uint8_t` | Channel (0 to 3) affected by per-channel commands. |
| `polarity_invert_mode` | `uint8_t` | Polarity inversion; not used by the driver. |
| `period` | `uint16_t` | Last period set with `PWM_CTRL_FREQUENCE_CONFIG`, in counter clocks. |
| `threshold_low` | `uint16_t` | Initial low threshold; not applied by the driver. |
| `threshold_high` | `uint16_t` | Initial high threshold; not applied by the driver. |
| `it_pulse_count` | `uint16_t` | Interrupt pulse count; not used by the driver. |
| `callback` | `void(*)(void *dev, void *args, uint32_t size, uint32_t event)` | Event callback: `dev` is this [`pwm_device_t`](#pwm_device_t), `args` is NULL, `size` is 0 and `event` is `PWM_EVENT_COMPLETE`. Set with `PWM_CTRL_SET_CALLBACKG`. |

### Macros { #hal_pwm-h-macros }

| Name | Value | Description |
|---|---|---|
| `pwm_channel_start(dev)` | `pwm_ioctl(dev, PWM_CTRL_RESUME, NULL)` | Start the PWM group and enable its outputs (`PWM_CTRL_RESUME`). |
| `pwm_channel_stop(dev)` | `pwm_ioctl(dev, PWM_CTRL_SUSPEND, NULL)` | Stop the PWM group (`PWM_CTRL_SUSPEND`). |
| `pwm_channel_freq_update(dev, count)` | `pwm_ioctl(dev, PWM_CTRL_FREQUENCE_CON...` | Set the period (`PWM_CTRL_FREQUENCE_CONFIG`). |
| `pwm_channel_dutycycle_update(dev, cfg)` | `pwm_ioctl(dev, PWM_CTRL_DUTYCYCLE_CON...` | Set the channel thresholds (`PWM_CTRL_DUTYCYCLE_CONFIG`). |
| `pwm_it_pulse_count_update(dev, count)` | `pwm_ioctl(dev, PWM_CTRL_IT_PULSE_COUN...` | Issue `PWM_CTRL_IT_PULSE_COUNT_CONFIG` (no effect in this release). |

## hal_adc.h { #hal_adc-h }

`#include "hal_adc.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_adc.h))

General-purpose ADC driver: channel selection, polled, interrupt and DMA reads, battery and die-temperature measurement.

The SoC has one general-purpose ADC (`ADC0_INDEX`). A typical sequence is: fill an [`adc_device_t`](#adc_device_t), call [`hal_adc_setConfig()`](#hal_adc_setConfig) and [`hal_adc_init()`](#hal_adc_init), select the input with `ADC_CTRL_CHANNEL_CONFIG`, start conversions with `ADC_CTRL_CHANNEL_START`, then read results with [`hal_adc_read()`](#hal_adc_read).

External input pins must be set to `GPIO_FUN_ANALOG` before they are sampled. Fixed analog front-end settings (reference trims, PGA stage gains, chopper mode) come from [`adc_config.h`](#adc_config-h). For audio capture use [`hal_auadc.h`](audio.md#hal_auadc-h) instead.

### hal_adc_init { #hal_adc_init }

```c
int hal_adc_init(int adc_id);
```

Initialize the ADC with the configuration stored by [`hal_adc_setConfig()`](#hal_adc_setConfig).

Selects the 32 MHz ADC source clock, resets and configures the converter and its FIFO, and installs the ADC interrupt handler when `adc_device_t::caps` requests interrupts. Resets `adc_device_t::rx_dma` to -1, so attach a DMA channel afterwards.

| Parameter | Description |
|---|---|
| `adc_id` | ADC instance (`ADC0_INDEX`). |

**Returns:** Always 0.

### hal_adc_read { #hal_adc_read }

```c
int hal_adc_read(int adc_id, void *buffer, uint32_t size);
```

Read conversion results.

- DMA mode (`COMMON_CAPS_DMA_RX`): reloads the attached DMA channel to copy `size` bytes of raw FIFO words into `buffer` and starts it; returns at once. Convert the words with `ADC_CTRL_DATA_PARSE` once the transfer completes.
- Otherwise: busy-waits until the FIFO holds `size` results, then writes `size` parsed [`adc_channel_val_t`](#adc_channel_val_t) entries to `buffer`.

| Parameter | Description |
|---|---|
| `adc_id` | ADC instance (`ADC0_INDEX`). |
| `buffer` | DMA mode: buffer for raw 32-bit words. Otherwise: array of at least `size` [`adc_channel_val_t`](#adc_channel_val_t). |
| `size` | DMA mode: transfer length in bytes (a multiple of 4). Otherwise: number of results, 1 to 32. |

**Returns:** DMA mode: 0 on success, -1 if no DMA channel is attached or the length is invalid, other negative values on DMA set-up failure. Otherwise: `size` on success, -1 if `size` is greater than 32.

!!! warning "Warning"
    The non-DMA path blocks without a time-out; conversions must have been started.

### hal_adc_trim_tsen { #hal_adc_trim_tsen }

```c
int hal_adc_trim_tsen(uint16_t *tsen_offset);
```

Read the factory temperature-sensor offset from eFuse.

| Parameter | Description |
|---|---|
| `tsen_offset` | Receives the offset for [`hal_adc_get_tsen()`](#hal_adc_get_tsen). Left unchanged when no valid trim is programmed. |

| Return value | Description |
|---|---|
| `0` | Offset read. |
| `1` | No valid trim in eFuse (not programmed or parity error). |

### hal_adc_get_tsen { #hal_adc_get_tsen }

```c
float hal_adc_get_tsen(uint16_t tsen_offset);
```

Measure the die temperature.

Performs two blocking conversions with different sensor bias settings and converts their difference to a temperature. Before calling, initialize the ADC with `adc_device_t::continuous_conv_mode` set to false, select `ADC_CHANNEL_TSEN_P` against `ADC_CHANNEL_GND` with `ADC_CTRL_CHANNEL_CONFIG`, and issue `ADC_CTRL_TSEN_ON`. Do not start conversions with `ADC_CTRL_CHANNEL_START`; this function starts them itself.

| Parameter | Description |
|---|---|
| `tsen_offset` | Sensor offset, normally from [`hal_adc_trim_tsen()`](#hal_adc_trim_tsen). |

**Returns:** Temperature in degrees Celsius.

### hal_adc_getDevice { #hal_adc_getDevice }

```c
adc_device_t * hal_adc_getDevice(int index);
```

Get the driver's configuration slot for an ADC instance.

| Parameter | Description |
|---|---|
| `index` | ADC instance (`ADC0_INDEX`). Not range-checked. |

**Returns:** Pointer to the internal [`adc_device_t`](#adc_device_t).

### hal_adc_setConfig { #hal_adc_setConfig }

```c
void hal_adc_setConfig(adc_device_t *dev);
```

Store an ADC configuration for the next [`hal_adc_init()`](#hal_adc_init).

Copies `dev` into the driver slot selected by `adc_device_t::id`.

| Parameter | Description |
|---|---|
| `dev` | Configuration to copy. |

### hal_adc_ioctl { #hal_adc_ioctl }

```c
int hal_adc_ioctl(int adc_id, int cmd, void *args);
```

Control the ADC.

| Parameter | Description |
|---|---|
| `adc_id` | ADC instance (`ADC0_INDEX`). |
| `cmd` | Command, one of the `ADC_CTRL_*` codes. |
| `args` | Command argument; see the description of each `ADC_CTRL_*` code. |

**Returns:** 0 for every command except `ADC_CTRL_CHANNEL_CONFIG`, which returns non-zero if an external channel's pin is not in analog mode.

### Anonymous enum { #hal_adc-h-enum }

Command codes for [`hal_adc_ioctl()`](#hal_adc_ioctl).

| Name | Value | Description |
|---|---|---|
| `ADC_CTRL_SET_INT` | `0` | Unmask ADC interrupt sources and enable the ADC interrupt. `args`: bitmask of [`adc_it_type`](#adc_it_type) values cast to `void *`. |
| `ADC_CTRL_CLEAR_INT` |  | Disable the ADC interrupt at the CPU. `args`: bitmask of [`adc_it_type`](#adc_it_type) values. The sources themselves are not masked in the ADC by this command. |
| `ADC_CTRL_ADD_INT_CB` |  | Install the event callback (see `adc_device_t::callback`). `args`: the function pointer. |
| `ADC_CTRL_ATTACH_RX_DMA` |  | Attach the DMA channel used by [`hal_adc_read()`](#hal_adc_read) in DMA mode. `args`: DMA channel index cast to `void *`. |
| `ADC_CTRL_CHANNEL_START` |  | Start conversions. `args`: unused. |
| `ADC_CTRL_CHANNEL_STOP` |  | Stop conversions. `args`: unused. |
| `ADC_CTRL_CHANNEL_CONFIG` |  | Select the input channel(s). `args`: pointer to an [`adc_channel_cfg_t`](#adc_channel_cfg_t). Uses `adc_device_t::continuous_conv_mode`. [`hal_adc_ioctl()`](#hal_adc_ioctl) returns non-zero if an external channel's pin is not in `GPIO_FUN_ANALOG` mode (the channel is still configured). |
| `ADC_CTRL_VBAT_ON` |  | Enable the internal VBAT divider so that `ADC_CHANNEL_VABT_HALF` reads VBAT/2. `args`: unused. |
| `ADC_CTRL_VBAT_OFF` |  | Disable the internal VBAT divider. `args`: unused. |
| `ADC_CTRL_TSEN_ON` |  | Configure the internal temperature sensor (internal diode mode) for [`hal_adc_get_tsen()`](#hal_adc_get_tsen). `args`: unused. |
| `ADC_CTRL_TSEN_OFF` |  | Accepted for symmetry; performs no action. `args`: unused. |
| `ADC_CTRL_DATA_PARSE` |  | Convert raw FIFO words (for example from a DMA buffer) into results. `args`: pointer to an [`adc_data_parse_t`](#adc_data_parse_t). |

### adc_index_type { #adc_index_type }

ADC instance index.

| Name | Value | Description |
|---|---|---|
| `ADC0_INDEX` |  | The general-purpose ADC. |
| `ADC_MAX_INDEX` |  | Number of ADC instances. |

### adc_channel_t { #adc_channel_t }

ADC input channel.

Used as the entries of `adc_channel_cfg_t::pos_channel` and `adc_channel_cfg_t::neg_channel`. Channels 0 to 11 are external pins; the others are internal signals.

| Name | Value | Description |
|---|---|---|
| `ADC_CHANNEL0` |  | External ADC channel 0. |
| `ADC_CHANNEL1` |  | External ADC channel 1. |
| `ADC_CHANNEL2` |  | External ADC channel 2. |
| `ADC_CHANNEL3` |  | External ADC channel 3. |
| `ADC_CHANNEL4` |  | External ADC channel 4. |
| `ADC_CHANNEL5` |  | External ADC channel 5. |
| `ADC_CHANNEL6` |  | External ADC channel 6. |
| `ADC_CHANNEL7` |  | External ADC channel 7. |
| `ADC_CHANNEL8` |  | External ADC channel 8. |
| `ADC_CHANNEL9` |  | External ADC channel 9. |
| `ADC_CHANNEL10` |  | External ADC channel 10. |
| `ADC_CHANNEL11` |  | External ADC channel 11. |
| `ADC_CHANNEL_DAC_OUTA` |  | DAC output A, ADC channel 12. |
| `ADC_CHANNEL_DAC_OUTB` |  | DAC output B, ADC channel 13. |
| `ADC_CHANNEL_TSEN_P` |  | Temperature sensor positive node, ADC channel 14. |
| `ADC_CHANNEL_TSEN_N` |  | Temperature sensor negative node, ADC channel 15. |
| `ADC_CHANNEL_VREF` |  | Reference voltage, ADC channel 16. |
| `ADC_CHANNEL_DCTEST` |  | DC test node, ADC channel 17. |
| `ADC_CHANNEL_VABT_HALF` |  | VBAT/2 (needs `ADC_CTRL_VBAT_ON`), ADC channel 18. |
| `ADC_CHANNEL_SENP3` |  | Sensor node SenVP3, ADC channel 19. |
| `ADC_CHANNEL_SENP2` |  | Sensor node SenVP2, ADC channel 20. |
| `ADC_CHANNEL_SENP1` |  | Sensor node SenVP1, ADC channel 21. |
| `ADC_CHANNEL_SENP0` |  | Sensor node SenVP0, ADC channel 22. |
| `ADC_CHANNEL_GND` |  | Ground, ADC channel 23. Use as the negative input for single-ended measurements. |

### adc_clk_div_t { #adc_clk_div_t }

ADC clock divider, applied to the 32 MHz ADC source clock.

| Name | Value | Description |
|---|---|---|
| `ADC_CLOCK_DIV_1` |  | ADC clock = 32 MHz. |
| `ADC_CLOCK_DIV_4` |  | ADC clock = 8 MHz. |
| `ADC_CLOCK_DIV_8` |  | ADC clock = 4 MHz. |
| `ADC_CLOCK_DIV_12` |  | ADC clock = 2.666 MHz. |
| `ADC_CLOCK_DIV_16` |  | ADC clock = 2 MHz. |
| `ADC_CLOCK_DIV_20` |  | ADC clock = 1.6 MHz. |
| `ADC_CLOCK_DIV_24` |  | ADC clock = 1.333 MHz. |
| `ADC_CLOCK_DIV_32` |  | ADC clock = 1 MHz. |

### adc_vref_t { #adc_vref_t }

ADC reference voltage (full scale of a single-ended conversion).

| Name | Value | Description |
|---|---|---|
| `ADC_VREF_3V2` | `0` | 3.2 V reference |
| `ADC_VREF_2V` | `1` | 2.0 V reference |

### adc_data_width_t { #adc_data_width_t }

ADC result width and hardware averaging.

| Name | Value | Description |
|---|---|---|
| `ADC_DATA_WIDTH_12B` |  | 12 bits, no averaging |
| `ADC_DATA_WIDTH_14B_WITH_16_AVERAGE` |  | 14 bits, average of 16 conversions |
| `ADC_DATA_WIDTH_14B_WITH_64_AVERAGE` |  | 14 bits, average of 64 conversions |
| `ADC_DATA_WIDTH_16B_WITH_128_AVERAGE` |  | 16 bits, average of 128 conversions |
| `ADC_DATA_WIDTH_16B_WITH_256_AVERAGE` |  | 16 bits, average of 256 conversions |

### adc_fifo_threshold_t { #adc_fifo_threshold_t }

ADC FIFO threshold.

Number of conversion results in the FIFO that raises the FIFO-ready interrupt (interrupt mode) or a DMA request (DMA mode). Despite the names, the unit is one 32-bit conversion result, not one byte.

| Name | Value | Description |
|---|---|---|
| `ADC_FIFO_THRESHOLD_1BYTE` |  | Threshold of 1 result. |
| `ADC_FIFO_THRESHOLD_4BYTE` |  | Threshold of 4 results. |
| `ADC_FIFO_THRESHOLD_8BYTE` |  | Threshold of 8 results. |
| `ADC_FIFO_THRESHOLD_16BYTE` |  | Threshold of 16 results. |

### adc_pga_gain_t { #adc_pga_gain_t }

ADC PGA gain.

| Name | Value | Description |
|---|---|---|
| `ADC_GAIN_NONE` |  | No PGA gain. |
| `ADC_GAIN_1` |  | PGA gain 1. |
| `ADC_GAIN_2` |  | PGA gain 2. |
| `ADC_GAIN_4` |  | PGA gain 4. |
| `ADC_GAIN_8` |  | PGA gain 8. |
| `ADC_GAIN_16` |  | PGA gain 16. |
| `ADC_GAIN_32` |  | PGA gain 32. |

### adc_event_type { #adc_event_type }

Event codes passed to `adc_device_t::callback`.

| Name | Value | Description |
|---|---|---|
| `ADC_EVENT_UNDERRUN` |  | FIFO underrun. |
| `ADC_EVENT_OVERRUN` |  | FIFO overrun. |
| `ADC_EVENT_FIFO` |  | FIFO reached its threshold; `args` points to the parsed [`adc_channel_val_t`](#adc_channel_val_t) results and `size` is their count. |
| `ADC_EVENT_UNKNOWN` |  | Unknown event (not reported by the driver). |

### adc_it_type { #adc_it_type }

Interrupt source bits for `ADC_CTRL_SET_INT` and `ADC_CTRL_CLEAR_INT`.

| Name | Value | Description |
|---|---|---|
| `ADC_UNDERRUN_IT` | `1 << 2` | FIFO underrun interrupt. |
| `ADC_OVERRUN_IT` | `1 << 3` | FIFO overrun interrupt. |
| `ADC_FIFO_IT` | `1 << 5` | FIFO-ready (threshold reached) interrupt. |

### adc_channel_cfg_t { #adc_channel_cfg_t }

Channel list for `ADC_CTRL_CHANNEL_CONFIG`.

With `num` equal to 1 the ADC converts one positive/negative pair; with a larger `num` it scans the pairs in order (up to 12 entries).

| Field | Type | Description |
|---|---|---|
| `pos_channel` | `uint8_t *` | Array of `num` positive inputs ([`adc_channel_t`](#adc_channel_t) values). |
| `neg_channel` | `uint8_t *` | Array of `num` negative inputs ([`adc_channel_t`](#adc_channel_t) values); use `ADC_CHANNEL_GND` for single-ended inputs. |
| `num` | `uint8_t` | Number of entries in each array (1 to 12). |

### adc_channel_val_t { #adc_channel_val_t }

One parsed conversion result.

| Field | Type | Description |
|---|---|---|
| `posChan` | `int8_t` | Positive channel ([`adc_channel_t`](#adc_channel_t) value). |
| `negChan` | `int8_t` | Negative channel, or -1 in single-ended mode. |
| `value` | `uint16_t` | Conversion code at the configured width (for example 0 to 65535 for 16-bit results), after gain-coefficient correction. |
| `volt` | `float` | Measured voltage in volts (negative values possible in differential mode). |

### adc_data_parse_t { #adc_data_parse_t }

Argument of `ADC_CTRL_DATA_PARSE`.

| Field | Type | Description |
|---|---|---|
| `input` | `uint32_t *` | Raw 32-bit FIFO words to convert. |
| `output` | `adc_channel_val_t *` | Destination array, at least `num` entries. |
| `num` | `uint32_t` | Number of words to convert. |

### adc_device_t { #adc_device_t }

ADC configuration and run-time state.

Pass a filled copy to [`hal_adc_setConfig()`](#hal_adc_setConfig) before [`hal_adc_init()`](#hal_adc_init).

| Field | Type | Description |
|---|---|---|
| `id` | `int` | ADC instance (`ADC0_INDEX`); selects the slot written by [`hal_adc_setConfig()`](#hal_adc_setConfig). |
| `caps` | `uint16_t` | Capability flags: `COMMON_CAPS_INT_RX` or `COMMON_CAPS_INT_TX` installs the ADC interrupt handler; `COMMON_CAPS_DMA_RX` selects DMA reads in [`hal_adc_read()`](#hal_adc_read). |
| `clk_div` | `adc_clk_div_t` | ADC clock divider; keep the ADC clock at or below 2 MHz. |
| `vref` | `adc_vref_t` | ADC reference voltage. |
| `continuous_conv_mode` | `bool` | true: convert continuously; false: one conversion (or one scan) per start |
| `differential_mode` | `bool` | true: differential input; false: single-ended input |
| `data_width` | `adc_data_width_t` | Result width and averaging. |
| `fifo_threshold` | `adc_fifo_threshold_t` | FIFO threshold for the FIFO-ready interrupt or DMA request. |
| `gain` | `adc_pga_gain_t` | PGA gain. Not applied by [`hal_adc_init()`](#hal_adc_init); the PGA stage gains come from `ADC_PGA_GAIN1` and `ADC_PGA_GAIN2` in [`adc_config.h`](#adc_config-h). |
| `rx_dma` | `int` | DMA channel for DMA reads; set to -1 by [`hal_adc_init()`](#hal_adc_init) and set with `ADC_CTRL_ATTACH_RX_DMA`. |
| `callback` | `void(*)(void *dev, void *args, uint32_t size, uint32_t event)` | Event callback, called from the ADC interrupt: `dev` is this [`adc_device_t`](#adc_device_t), `event` an [`adc_event_type`](#adc_event_type) value; for `ADC_EVENT_FIFO` `args` points to `size` parsed [`adc_channel_val_t`](#adc_channel_val_t) results, otherwise `args` is NULL and `size` is 0. May be NULL. |

## adc_config.h { #adc_config-h }

`#include "adc_config.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/default_config/adc_config.h))

Fixed analog front-end settings applied by [`hal_adc_init()`](#hal_adc_init).

These values are written to the general-purpose ADC on every [`hal_adc_init()`](#hal_adc_init) call and are not part of [`adc_device_t`](#adc_device_t). Each value is an index into the corresponding hardware setting, as described per macro.

### Macros { #adc_config-h-macros }

| Name | Value | Description |
|---|---|---|
| `ADC_DATA_WIDIH_12` | `(0)` | Data-width code for 12-bit results (not used by [`hal_adc_init()`](#hal_adc_init); the width comes from `adc_device_t::data_width`). |
| `ADC_V18_SELECT` | `(2)` | Internal 1.8 V rail trim: 2 selects 1.82 V (0 = 1.62 V, 1 = 1.72 V, 3 = 1.92 V). |
| `ADC_V11_SELECT` | `(1)` | Internal 1.1 V rail trim: 1 selects 1.1 V (0 = 1.0 V, 2 = 1.18 V, 3 = 1.26 V). |
| `ADC_PGA_VCM` | `(1)` | PGA common-mode voltage: 1 selects 1.2 V (0 = 1.0 V, 2 = 1.4 V, 3 = 1.6 V). |
| `ADC_PGA_GAIN1` | `(1)` | First PGA stage gain index (1 = gain 1). |
| `ADC_PGA_GAIN2` | `(1)` | Second PGA stage gain index (1 = gain 1). |
| `ADC_CHOP_MODE` | `(2)` | Chopper mode: 2 enables reference auto-zero and PGA chopping (0 = all off, 1 = reference auto-zero only, 3 = auto-zero, PGA chopping and RPC). |
| `ADC_BIAS_SELECT` | `(0)` | Bias current source: 0 = main bandgap, 1 = always-on bandgap. |
| `ADC_OFFSET_CALIB_EN` | `(0)` | Offset calibration enable (0 = disabled). |
| `ADC_OFFSER_CALIB_VAL` | `(0)` | Offset calibration value written to the ADC. |

## hal_dac.h { #hal_dac-h }

`#include "hal_dac.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_dac.h))

General-purpose DAC driver: two 10-bit output channels, register or DMA output.

Channel 0 (DAC output A) is on GPIO23 and channel 1 (DAC output B) on GPIO22. Set the pins to `GPIO_FUN_ANALOG` before [`hal_dac_init()`](#hal_dac_init); a channel whose pin is not in analog mode is not enabled. Typical sequence: fill a [`dac_device_t`](#dac_device_t), [`hal_dac_setConfig()`](#hal_dac_setConfig), [`hal_dac_init()`](#hal_dac_init), then, for DMA output, attach a DMA channel with `DAC_CTRL_TX_DMA` and stream samples with [`hal_dac_write()`](#hal_dac_write).

Samples are 10-bit codes (0 to 1023, mid-scale 512) stored one per `uint16_t`.

### hal_dac_setConfig { #hal_dac_setConfig }

```c
void hal_dac_setConfig(dac_device_t *dev);
```

Store a DAC configuration for the next [`hal_dac_init()`](#hal_dac_init).

Copies `dev` into the driver slot selected by `dac_device_t::id`.

| Parameter | Description |
|---|---|
| `dev` | Configuration to copy. |

### hal_dac_init { #hal_dac_init }

```c
int hal_dac_init(int dac_id);
```

Initialize the DAC with the configuration stored by [`hal_dac_setConfig()`](#hal_dac_setConfig).

Selects the 32 MHz DAC clock, sets the divider for `dac_device_t::sample_freq`, selects the reference and the data source (DMA or registers) and enables the requested channels whose pins are in analog mode. Resets `dac_device_t::tx_dma` to -1, so attach a DMA channel afterwards. Channels enabled by an earlier call stay selected.

| Parameter | Description |
|---|---|
| `dac_id` | DAC instance (`DAC0_INDEX`). |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | `dac_device_t::sample_freq` is not one of [`dac_sample_frequence`](#dac_sample_frequence). |

### hal_dac_deinit { #hal_dac_deinit }

```c
int hal_dac_deinit(int dac_id);
```

Disable both DAC channels and the DAC DMA request.

| Parameter | Description |
|---|---|
| `dac_id` | DAC instance (`DAC0_INDEX`); not used. |

**Returns:** Always 0.

### hal_dac_control { #hal_dac_control }

```c
int hal_dac_control(int dac_id, int cmd, void *args);
```

Control the DAC.

| Parameter | Description |
|---|---|
| `dac_id` | DAC instance (`DAC0_INDEX`). |
| `cmd` | Command; only `DAC_CTRL_TX_DMA` is supported, others are ignored. |
| `args` | Command argument (DMA channel index for `DAC_CTRL_TX_DMA`). |

**Returns:** Always 0.

### hal_dac_write { #hal_dac_write }

```c
int hal_dac_write(int dac_id, int channel, const void *buffer, uint32_t size);
```

Output samples.

- DMA mode (`COMMON_CAPS_DMA_TX`): reloads the attached DMA channel to send `size` bytes from `buffer` to the DAC and starts it; returns at once. `channel` is not used; the enabled channels are fed by the DMA data.
- Otherwise: writes the `size` codes of `buffer` one after another to the selected channel(s) without pacing, so the output settles at the last code. Use `size` = 1 to set a static level.

| Parameter | Description |
|---|---|
| `dac_id` | DAC instance (`DAC0_INDEX`). |
| `channel` | Register mode: `DAC_CHANNEL_0`, `DAC_CHANNEL_1` or `DAC_CHANNEL_ALL`. |
| `buffer` | Samples, one 10-bit code per `uint16_t`. In DMA mode it must stay valid until the transfer completes. |
| `size` | DMA mode: length in bytes. Register mode: number of codes. |

**Returns:** 0 on success. DMA mode: -1 if no DMA channel is attached, other negative values on DMA set-up failure. Register mode: -1 if `channel` selects no channel.

### dac_index_type { #dac_index_type }

DAC instance index.

| Name | Value | Description |
|---|---|---|
| `DAC0_INDEX` |  | The general-purpose DAC. |
| `DAC_MAX_INDEX` |  | Number of DAC instances. |

### Anonymous enum { #hal_dac-h-enum }

Command codes for [`hal_dac_control()`](#hal_dac_control).

| Name | Value | Description |
|---|---|---|
| `DAC_CTRL_TX_DMA` | `0` | Attach the DMA channel used by [`hal_dac_write()`](#hal_dac_write) in DMA mode. `args`: DMA channel index cast to `void *`. |

### dac_sample_frequence { #dac_sample_frequence }

Supported DAC sample rates, in Hz.

The rate is derived from the 32 MHz DAC clock by integer division, so the actual rate can deviate slightly from the nominal value.

| Name | Value | Description |
|---|---|---|
| `DAC_SAMPLE_FREQ_8KHZ` | `8000` | 8 kHz |
| `DAC_SAMPLE_FREQ_16KHZ` | `16000` | 16 kHz |
| `DAC_SAMPLE_FREQ_32KHZ` | `32000` | 32 kHz |
| `DAC_SAMPLE_FREQ_512KHZ` | `512000` | 512 kHz |

### dac_device_t { #dac_device_t }

DAC configuration and run-time state.

Pass a filled copy to [`hal_dac_setConfig()`](#hal_dac_setConfig) before [`hal_dac_init()`](#hal_dac_init).

| Field | Type | Description |
|---|---|---|
| `id` | `int` | DAC instance (`DAC0_INDEX`); selects the slot written by [`hal_dac_setConfig()`](#hal_dac_setConfig). |
| `caps` | `uint16_t` | `COMMON_CAPS_DMA_TX` selects DMA output; otherwise [`hal_dac_write()`](#hal_dac_write) writes the output registers directly |
| `sample_freq` | `enum dac_sample_frequence` | Sample rate. |
| `channels` | `uint8_t` | Channels to enable: `DAC_CHANNEL_0`, `DAC_CHANNEL_1` or `DAC_CHANNEL_ALL`. |
| `vref` | `uint8_t` | Reference: `DAC_VREF_INTERNAL` or `DAC_VREF_EXTERNAL`. |
| `tx_dma` | `int` | DMA channel for DMA output; set to -1 by [`hal_dac_init()`](#hal_dac_init) and set with `DAC_CTRL_TX_DMA`. |

### Macros { #hal_dac-h-macros }

| Name | Value | Description |
|---|---|---|
| `DAC_CHANNEL_0` | `(1 << 0)` | Channel 0 (DAC output A, GPIO23). |
| `DAC_CHANNEL_1` | `(1 << 1)` | Channel 1 (DAC output B, GPIO22); enabling it in [`hal_dac_init()`](#hal_dac_init) also enables channel 0. |
| `DAC_CHANNEL_ALL` | `(DAC_CHANNEL_0 \| DAC_CHANNEL_1)` | Both channels. |
| `DAC_VREF_INTERNAL` | `0` | Internal reference: output voltage = (1.8 V - 0.2 V) x code / 1024 + 0.2 V, that is 0.2 V to 1.8 V. |
| `DAC_VREF_EXTERNAL` | `1` | External reference on GPIO7 (analog mode): output voltage = (0.9 x Vref - 0.1 x Vref) x code / 1024 + 0.1 x Vref, that is 0.1 x Vref to 0.9 x Vref. |

## hal_acomp.h { #hal_acomp-h }

`#include "hal_acomp.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_acomp.h))

Analog comparator (ACOMP) driver: input selection, hysteresis, output and edge interrupts.

The SoC has two analog comparators in the always-on domain, selected by an index of 0 or 1. Typical sequence: [`acomp_init()`](#acomp_init), [`acomp_enable()`](#acomp_enable), then poll [`acomp_get_result()`](#acomp_get_result) or unmask an edge interrupt with [`acomp_interrupt_unmask()`](#acomp_interrupt_unmask).

### acomp_init { #acomp_init }

```c
void acomp_init(uint8_t idx, acomp_cfg_t *device);
```

Configure a comparator.

Disables the comparator, then programs the inputs and hysteresis with the input multiplexer enabled, a level scaling factor of 1 and the slow-response power mode. The comparator stays disabled; call [`acomp_enable()`](#acomp_enable) afterwards.

| Parameter | Description |
|---|---|
| `idx` | Comparator index, 0 or 1 (any non-zero value selects comparator 1). |
| `device` | Configuration. |

### acomp_enable { #acomp_enable }

```c
void acomp_enable(uint8_t idx);
```

Enable a comparator.

| Parameter | Description |
|---|---|
| `idx` | Comparator index, 0 or 1. |

### acomp_disable { #acomp_disable }

```c
void acomp_disable(uint8_t idx);
```

Disable a comparator.

| Parameter | Description |
|---|---|
| `idx` | Comparator index, 0 or 1. |

### acomp_interrupt_mask { #acomp_interrupt_mask }

```c
void acomp_interrupt_mask(uint8_t idx, uint8_t edge_type);
```

Mask (disable) a comparator edge interrupt.

| Parameter | Description |
|---|---|
| `idx` | Comparator index, 0 or 1. |
| `edge_type` | Edge, one of [`acomp_it_type`](#acomp_it_type). |

!!! note "Note"
    In this release, passing `ACOMP_POSITIVE_IT` (value 0) has no effect; only `ACOMP_NEGATIVE_IT` changes the comparator's interrupt enable.

### acomp_interrupt_unmask { #acomp_interrupt_unmask }

```c
void acomp_interrupt_unmask(uint8_t idx, uint8_t edge_type);
```

Clear any pending interrupt of a comparator and unmask (enable) an edge interrupt.

| Parameter | Description |
|---|---|
| `idx` | Comparator index, 0 or 1. |
| `edge_type` | Edge, one of [`acomp_it_type`](#acomp_it_type). |

!!! note "Note"
    In this release, passing `ACOMP_POSITIVE_IT` (value 0) only clears the pending interrupt; only `ACOMP_NEGATIVE_IT` changes the comparator's interrupt enable.

### acomp_get_result { #acomp_get_result }

```c
int acomp_get_result(uint8_t idx);
```

Read the raw comparator output.

| Parameter | Description |
|---|---|
| `idx` | Comparator index, 0 or 1. |

**Returns:** 1 if the comparator output is high, 0 if it is low.

### acomp_channel_type { #acomp_channel_type }

Comparator input selection, for either the positive or the negative input.

| Name | Value | Description |
|---|---|---|
| `ACOMP_CHANNEL_ADC_CHANNEL0` |  | ADC input channel 0. |
| `ACOMP_CHANNEL_ADC_CHANNEL1` |  | ADC input channel 1. |
| `ACOMP_CHANNEL_ADC_CHANNEL2` |  | ADC input channel 2. |
| `ACOMP_CHANNEL_ADC_CHANNEL3` |  | ADC input channel 3. |
| `ACOMP_CHANNEL_ADC_CHANNEL4` |  | ADC input channel 4. |
| `ACOMP_CHANNEL_ADC_CHANNEL5` |  | ADC input channel 5. |
| `ACOMP_CHANNEL_ADC_CHANNEL6` |  | ADC input channel 6. |
| `ACOMP_CHANNEL_ADC_CHANNEL7` |  | ADC input channel 7. |
| `ACOMP_CHANNEL_DAC_CHANNELA` |  | DAC output channel A. |
| `ACOMP_CHANNEL_DAC_CHANNELB` |  | DAC output channel B. |
| `ACOMP_CHANNEL_VREF_1P2V` |  | 1.2 V reference voltage |
| `ACOMP_CHANNEL_0P375VBAT` |  | 6/16 x VBAT; marked as not implemented on IPRO7 |
| `ACOMP_CHANNEL_0P25VBAT` |  | 4/16 x VBAT |
| `ACOMP_CHANNEL_0P1875VBAT` |  | 3/16 x VBAT |
| `ACOMP_CHANNEL_0P3125VBAT` |  | 5/16 x VBAT |
| `ACOMP_CHANNEL_VSS` |  | Ground (VSS). |

### acomp_hysteresis_vol_type { #acomp_hysteresis_vol_type }

Comparator hysteresis voltage.

| Name | Value | Description |
|---|---|---|
| `ACOMP_HYSTERESIS_VOLT_NONE` |  | No hysteresis. |
| `ACOMP_HYSTERESIS_VOLT_10MV` |  | 10 mV hysteresis |
| `ACOMP_HYSTERESIS_VOLT_20MV` |  | 20 mV hysteresis |
| `ACOMP_HYSTERESIS_VOLT_30MV` |  | 30 mV hysteresis |
| `ACOMP_HYSTERESIS_VOLT_40MV` |  | 40 mV hysteresis |
| `ACOMP_HYSTERESIS_VOLT_50MV` |  | 50 mV hysteresis |
| `ACOMP_HYSTERESIS_VOLT_60MV` |  | 60 mV hysteresis |
| `ACOMP_HYSTERESIS_VOLT_70MV` |  | 70 mV hysteresis |

### acomp_it_type { #acomp_it_type }

Edge selector for [`acomp_interrupt_mask()`](#acomp_interrupt_mask) and [`acomp_interrupt_unmask()`](#acomp_interrupt_unmask).

| Name | Value | Description |
|---|---|---|
| `ACOMP_POSITIVE_IT` | `0` | Positive (rising) edge interrupt. |
| `ACOMP_NEGATIVE_IT` | `1` | Negative (falling) edge interrupt. |

### acomp_cfg_t { #acomp_cfg_t }

Comparator configuration for [`acomp_init()`](#acomp_init).

| Field | Type | Description |
|---|---|---|
| `pos_ch` | `enum acomp_channel_type` | Positive input. |
| `neg_ch` | `enum acomp_channel_type` | Negative input. |
| `pos_hysteresis_vol` | `enum acomp_hysteresis_vol_type` | Hysteresis on the positive side. |
| `neg_hysteresis_vol` | `enum acomp_hysteresis_vol_type` | Hysteresis on the negative side. |

## hal_keyscan.h { #hal_keyscan-h }

`#include "hal_keyscan.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_keyscan.h))

Key-scan matrix controller definitions: control commands, matrix size, events and the device configuration.

The key-scan controller scans a key matrix of up to 20 columns by 8 rows and reports pressed keys as key codes. A key code is `column x row_num + row`, with column and row counted from 0. The device slot is initialized from the board configuration (`KEYSCAN_CONFIG`).

### Anonymous enum { #hal_keyscan-h-enum }

Key-scan control command codes.

| Name | Value | Description |
|---|---|---|
| `KYS_CTRL_SET_INT` | `0` | Install the key-scan interrupt handler (when the key-scan peripheral is enabled in the board configuration), unmask the interrupt and enable it. `args`: unused. |
| `KYS_CTRL_CLR_INT` |  | Remove the interrupt handler, mask the interrupt and disable it. `args`: unused. |
| `KYS_CTRL_GET_INT` |  | Returns the interrupt status bits (bits 3:0). `args`: unused. |
| `KYS_CTRL_RESUME` |  | Enable scanning. `args`: unused. |
| `KYS_CTRL_SUSPEND` |  | Disable scanning. `args`: unused. |
| `KYS_CTRL_KEYSCAN_GET_KEYCODE` |  | Read the key code of the first reported key and clear the key-code status. `args`: pointer to a `uint32_t` that receives the key code. |
| `KYS_CTRL_SET_CALLBACK` |  | Install the event callback (see `keyscan_device_t::callback`). `args`: the function pointer. |

### keyscan_index_type { #keyscan_index_type }

Key-scan instance index.

| Name | Value | Description |
|---|---|---|
| `KEYSCAN_INDEX` |  | The key-scan controller. |
| `KEYSCAN_MAX_INDEX` |  | Number of key-scan controllers. |

### col_num_type { #col_num_type }

Number of matrix columns (1 to 20).

| Name | Value | Description |
|---|---|---|
| `COL_NUM_1` | `1` | 1 column |
| `COL_NUM_2` |  | 2 columns |
| `COL_NUM_3` |  | 3 columns |
| `COL_NUM_4` |  | 4 columns |
| `COL_NUM_5` |  | 5 columns |
| `COL_NUM_6` |  | 6 columns |
| `COL_NUM_7` |  | 7 columns |
| `COL_NUM_8` |  | 8 columns |
| `COL_NUM_9` |  | 9 columns |
| `COL_NUM_10` |  | 10 columns |
| `COL_NUM_11` |  | 11 columns |
| `COL_NUM_12` |  | 12 columns |
| `COL_NUM_13` |  | 13 columns |
| `COL_NUM_14` |  | 14 columns |
| `COL_NUM_15` |  | 15 columns |
| `COL_NUM_16` |  | 16 columns |
| `COL_NUM_17` |  | 17 columns |
| `COL_NUM_18` |  | 18 columns |
| `COL_NUM_19` |  | 19 columns |
| `COL_NUM_20` |  | 20 columns |

### row_num_type { #row_num_type }

Number of matrix rows (1 to 8).

| Name | Value | Description |
|---|---|---|
| `ROW_NUM_1` | `1` | 1 row |
| `ROW_NUM_2` |  | 2 rows |
| `ROW_NUM_3` |  | 3 rows |
| `ROW_NUM_4` |  | 4 rows |
| `ROW_NUM_5` |  | 5 rows |
| `ROW_NUM_6` |  | 6 rows |
| `ROW_NUM_7` |  | 7 rows |
| `ROW_NUM_8` |  | 8 rows |

### keyscan_event_type { #keyscan_event_type }

Event codes passed to `keyscan_device_t::callback`.

| Name | Value | Description |
|---|---|---|
| `KEYSCAN_EVENT_TRIG` |  | Key event; the callback's `args` carries the key code. |
| `KEYSCAN_EVENT_UNKNOWN` |  | Unknown event (not reported by the driver). |

### keyscan_device_t { #keyscan_device_t }

Key-scan device configuration.

| Field | Type | Description |
|---|---|---|
| `col_num` | `enum col_num_type` | Number of matrix columns. |
| `row_num` | `enum row_num_type` | Number of matrix rows. |
| `deglitch_count` | `uint8_t` | Deglitch count; 0 disables the deglitch filter. |
| `callback` | `void(*)(void *dev, void *args, uint32_t size, uint32_t event)` | Event callback, called from the key-scan interrupt: `dev` is this [`keyscan_device_t`](#keyscan_device_t), `args` is the key code cast to `void *`, `size` is 0 and `event` is `KEYSCAN_EVENT_TRIG`. May be NULL. |

### Macros { #hal_keyscan-h-macros }

| Name | Value | Description |
|---|---|---|
| `KEYSCAN_DEV(dev)` | `((keyscan_device_t *)dev)` | Cast a generic device pointer to [`keyscan_device_t`](#keyscan_device_t). |

## hal_qdec.h { #hal_qdec-h }

`#include "hal_qdec.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_qdec.h))

Quadrature decoder (QDEC) definitions: instances, control commands, events and the device configuration.

The SoC has three quadrature decoders (`QDEC0_INDEX` to `QDEC2_INDEX`) that sample a rotary encoder's A/B inputs, accumulate the movement and report it periodically. This header provides the configuration structure, the control command codes and the event codes used by the QDEC driver.

### Anonymous enum { #hal_qdec-h-enum }

QDEC control command codes.

| Name | Value | Description |
|---|---|---|
| `QDEC_CTRL_SET_INT` |  | Unmask interrupt sources and enable the decoder's interrupt. `args`: bitmask of [`qdec_event_type`](#qdec_event_type) values. |
| `QDEC_CTRL_CLR_INT` |  | Mask interrupt sources and disable the decoder's interrupt. `args`: bitmask of [`qdec_event_type`](#qdec_event_type) values. |
| `QDEC_CTRL_RESUME` |  | Enable the decoder. `args`: unused. |
| `QDEC_CTRL_SUSPEND` |  | Disable the decoder. `args`: unused. |
| `QDEC_CTRL_GET_SAMPLE_VAL` |  | Returns the current sample value. `args`: unused. |
| `QDEC_CTRL_GET_SAMPLE_DIR` |  | Returns the direction of the last change: 0 = no change, 1 = clockwise, 2 = counter-clockwise, 3 = error. `args`: unused. |
| `QDEC_CTRL_GET_ERROR_CNT` |  | Returns the error count. `args`: unused. |
| `QDEC_CTRL_SET_CALLBACK` |  | Install the event callback (see `qdec_device_t::callback`). `args`: the function pointer. |

### qdec_index_type { #qdec_index_type }

QDEC instance index.

| Name | Value | Description |
|---|---|---|
| `QDEC0_INDEX` |  | Quadrature decoder 0. |
| `QDEC1_INDEX` |  | Quadrature decoder 1. |
| `QDEC2_INDEX` |  | Quadrature decoder 2. |
| `QDEC_MAX_INDEX` |  | Number of quadrature decoders. |

### qdec_event_type { #qdec_event_type }

QDEC events: interrupt-source bits for `QDEC_CTRL_SET_INT` and `QDEC_CTRL_CLR_INT`, and the `event` value passed to the callback.

| Name | Value | Description |
|---|---|---|
| `QDEC_REPORT_EVENT` | `1 << 0` | Report interrupt: a report period has elapsed. |
| `QDEC_SAMPLE_EVENT` | `1 << 1` | Sample interrupt: a sample has been taken. |
| `QDEC_ERROR_EVENT` | `1 << 2` | Error interrupt. |
| `QDEC_OVERFLOW_EVENT` | `1 << 3` | Accumulator overflow interrupt. |
| `QDEC_ALL_EVENT` | `1 << 4` | Upper bound of the event bits (not an event). |

### qdec_device_t { #qdec_device_t }

QDEC device configuration.

The device slots are initialized from the board configuration (`QDEC0_CONFIG` to `QDEC2_CONFIG`).

| Field | Type | Description |
|---|---|---|
| `id` | `uint8_t` | Hardware decoder (0 to 2). |
| `caps` | `uint16_t` | Capability flags: `COMMON_CAPS_INT_RX` installs the decoder's interrupt handler at initialization. |
| `callback` | `void(*)(void *dev, void *args, uint32_t size, uint32_t event)` | Event callback, called from the decoder interrupt: `dev` is this [`qdec_device_t`](#qdec_device_t), `args` is NULL, `size` is 0 and `event` is one [`qdec_event_type`](#qdec_event_type) value. May be NULL. |
| `acc_mode` | `uint8_t` | Accumulator mode: 0 = stop accumulating on overflow, 1 = continue accumulating. |
| `sample_mode` | `uint8_t` | Sample mode: 0 = stop sampling when a report is ready, 1 = sample continuously. |
| `sample_period` | `uint8_t` | Sample period code, 0 to 12: 32 us x 2^code with a 1 MHz decoder clock (32 us, 64 us, ..., 65 ms, 131 ms). |
| `report_mode` | `uint8_t` | Report mode: 0 = count time only while the sample changes, 1 = count time continuously. |
| `report_period` | `uint32_t` | Report period, in sample periods. |
| `led_en` | `uint8_t` | Non-zero enables the LED output (for optical encoders). |
| `led_swap` | `uint8_t` | Non-zero swaps the LED on/off polarity. |
| `led_period` | `uint16_t` | Time in us the LED is switched on before each sample. |
| `deglitch_en` | `uint8_t` | Non-zero enables the input deglitch filter. |
| `deglitch_strength` | `uint8_t` | Deglitch filter strength. |

## hal_dma.h { #hal_dma-h }

`#include "hal_dma.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_dma.h))

DMA driver: channel configuration, linked-list (LLI) transfers and completion callbacks.

The SoC has one DMA controller (`DMA0_ID`) with eight channels. Each transfer is described by a chain of linked-list items ([`dma_lli_ctrl_t`](#dma_lli_ctrl_t)) that [`dma_reload()`](#dma_reload) builds from the channel configuration.

Typical sequence with fixed channels:

1. Fill a zero-initialised [`dma_device_t`](#dma_device_t) (channel, direction, request lines, widths, bursts, address increment, transfer mode) and install it with [`dma_setConfig()`](#dma_setConfig).
1. Program the channel with [`dma_init()`](#dma_init).
1. Optionally register a callback with `DMA_CTRL_SET_CALLBACK` and unmask the channel interrupts with `DMA_CTRL_SET_INT`.
1. Build the transfer with [`dma_reload()`](#dma_reload) and start it with [`dma_channel_start()`](#hal_dma-h-macros).

When `CONFIG_DMA_CHANNEL_ALLOCATOR` is enabled, [`dma_request_channel()`](#dma_request_channel) hands out free channels at run time instead of fixed channel numbers.

Peripheral drivers that use DMA (for example [`hal_uart.h`](#hal_uart-h)) take a channel configured this way.

### dma_getDevice { #dma_getDevice }

```c
dma_device_t * dma_getDevice(int dma_id, int dma_ch);
```

Get the driver's configuration record of a channel.

Changes made through the returned pointer are used by the next [`dma_init()`](#dma_init) / [`dma_channel_attach()`](#dma_channel_attach) (direction, request lines) and the next [`dma_reload()`](#dma_reload) (widths, bursts, increments, mode).

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |

**Returns:** Pointer to the internal record. The arguments are not range-checked.

### dma_ioctl { #dma_ioctl }

```c
int dma_ioctl(int dma_id, int dma_ch, int cmd, void *args);
```

Execute a channel control command.

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |
| `cmd` | Command, one of the `DMA_CTRL_*` values. |
| `args` | Command argument; see the description of each command. |

**Returns:** For `DMA_CTRL_CHANNEL_GET_STATUS`: 1 if the channel is enabled, 0 if idle. 0 for all other commands; unknown commands are ignored.

### dma_reload { #dma_reload }

```c
int dma_reload(int dma_id, int dma_ch, uint32_t src_addr, uint32_t dst_addr, uint32_t transfer_size, dma_lli_ctrl_t **lliCfg);
```

Build the LLI chain of a transfer and load it into a channel.

Stops the channel first (a transfer still in progress is aborted), splits the transfer into items of at most `DMA_MAX_TRANSFER_PER_LLI` source-width items, links them according to `dma_device_t::transfer_mode`, writes the chain back from the data cache and loads the first item. The channel is not started; call [`dma_channel_start()`](#hal_dma-h-macros) afterwards. The function calls realloc() on every invocation.

In `DMA_LLI_PINGPONG_MODE` and `DMA_LLI_CYCLE_N_MODE` the memory buffer must hold 2 or `dma_device_t::lli_count` times `transfer_size` bytes.

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |
| `src_addr` | Source address (buffer or peripheral data register). |
| `dst_addr` | Destination address (buffer or peripheral data register). |
| `transfer_size` | Transfer length in bytes (per segment in the circular buffer modes). Must be a multiple of the source width. 0 only stops the channel. |
| `lliCfg` | If not NULL, receives the chain and takes ownership of it: the caller must free() it once the channel no longer uses it. If NULL, the driver keeps the chain and frees it in [`dma_close()`](#dma_close). |

| Return value | Description |
|---|---|
| `0` | Success (or `transfer_size` was 0). |
| `-1` | `transfer_size` is not a multiple of the source width. |
| `-2` | Out of memory for the chain. |
| `-3` | Invalid `dma_device_t::src_width`. |

!!! note "Note"
    The data buffers themselves are not cleaned or invalidated in the data cache, and they must stay valid until the transfer completes.

### dma_init { #dma_init }

```c
int dma_init(int dma_id, int dma_ch);
```

Program a channel from its configuration record.

Writes direction, request lines, widths, bursts and address increments into the channel, installs the DMA interrupt handler and enables the DMA interrupt in the CPU.

With `CONFIG_DMA_CHANNEL_ALLOCATOR` this is the same as [`dma_channel_attach()`](#dma_channel_attach).

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |

**Returns:** 0.

!!! warning "Warning"
    Without `CONFIG_DMA_CHANNEL_ALLOCATOR` this function disables and re-enables the whole DMA controller, which aborts transfers in progress on all other channels, and it does not enable the per-channel clock. Use [`dma_channel_attach()`](#dma_channel_attach) while other channels are running.

### dma_setConfig { #dma_setConfig }

```c
void dma_setConfig(dma_device_t *dma_device);
```

Install a channel configuration.

Copies the whole structure into the driver's record of channel `dma_device->ch`, including the `callback` and `lli_cfg` members, so zero-initialise the structure before filling it. The hardware is not touched; call [`dma_init()`](#dma_init) or [`dma_channel_attach()`](#dma_channel_attach) afterwards.

| Parameter | Description |
|---|---|
| `dma_device` | Configuration to copy; its `id` and `ch` select the channel. |

### dma_close { #dma_close }

```c
int dma_close(uint32_t dma_id, int dma_ch);
```

Stop a channel and clear its hardware configuration.

Frees the LLI chain owned by the driver, disables the channel and writes an all-zero channel configuration.

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |

**Returns:** 0.

!!! warning "Warning"
    Do not call it on a channel obtained from [`dma_request_channel()`](#dma_request_channel); use [`dma_release_channel()`](#dma_release_channel) instead.

### dma_controller_init { #dma_controller_init }

```c
void dma_controller_init(int dma_id);
```

Enable a DMA controller and its interrupt (one time).

Enables the controller, installs the DMA interrupt handler and enables the DMA interrupt in the CPU. Only the first call has an effect; later calls return immediately. All users (allocator or fixed channels) share the same controller.

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |

### dma_channel_attach { #dma_channel_attach }

```c
int dma_channel_attach(int dma_id, int dma_ch);
```

Program one channel without disturbing the other channels.

Calls [`dma_controller_init()`](#dma_controller_init), enables the per-channel DMA clock (channels 4-7 are clock-gated after reset), masks the channel interrupts and disables the channel, then writes the channel registers from the record installed with [`dma_setConfig()`](#dma_setConfig). The callback stored in that record is used by the interrupt handler.

Unlike [`dma_init()`](#dma_init) without `CONFIG_DMA_CHANNEL_ALLOCATOR`, it does not disable the controller, so transfers in progress on other channels keep running. Use it when several channels run at the same time (for example audio playback and capture).

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |

**Returns:** 0.

!!! note "Note"
    The channel interrupts stay masked; unmask them with `DMA_CTRL_SET_INT`.

### dma_request_channel { #dma_request_channel }

```c
dma_ch_handle_t dma_request_channel(uint32_t req, uint8_t dir, const char *owner);
```

Acquire a DMA channel routed to a peripheral request line.

Takes the first free channel, sets its direction and request routing (the peripheral side gets `req`, the memory side `DMA_REQUEST_NONE`) and programs it with [`dma_channel_attach()`](#dma_channel_attach). Widths, bursts, address increments, transfer mode and callback still have to be set, for example through [`dma_getDevice()`](#dma_getDevice) and [`dma_ioctl()`](#dma_ioctl); widths and bursts take effect at the next [`dma_reload()`](#dma_reload). Pass [`dma_handle_to_ch()`](#dma_handle_to_ch) of the handle as the channel index to the other DMA functions.

Calling it again with the same `owner` and `req` returns the same handle and increments its reference count; release it the same number of times. Memory-to-memory requests (`DMA_REQUEST_NONE`) always get a new channel.

| Parameter | Description |
|---|---|
| `req` | Peripheral request line (`DMA_REQUEST_DAC0`, `DMA_REQUEST_AUD_ADC`, ...), or `DMA_REQUEST_NONE` for memory-to-memory. |
| `dir` | Direction: `DMA_MEMORY_TO_PERIPH`, `DMA_PERIPH_TO_MEMORY` or `DMA_MEMORY_TO_MEMORY`. |
| `owner` | Name of the user for log messages and [`dma_dump_allocation()`](#dma_dump_allocation) (for example "audio_dac"). It must stay valid as long as the handle (usually a string literal). |

**Returns:** Handle on success; NULL if all channels are in use or if `req` is already bound to a channel by a different owner.

!!! warning "Warning"
    Task context only: it takes an internal mutex. Do not call it from an interrupt handler.

### dma_release_channel { #dma_release_channel }

```c
void dma_release_channel(dma_ch_handle_t h);
```

Release a channel obtained from [`dma_request_channel()`](#dma_request_channel).

Decrements the reference count. On the final release the channel is stopped, its interrupts are masked, its LLI chain is freed, its callback is cleared and it returns to the free pool. NULL is ignored; releasing a channel that is not allocated prints a warning and does nothing.

| Parameter | Description |
|---|---|
| `h` | Handle to release. |

### dma_handle_to_ch { #dma_handle_to_ch }

```c
int dma_handle_to_ch(dma_ch_handle_t h);
```

Get the channel index of a handle.

Use the result as the `dma_ch` argument of [`dma_reload()`](#dma_reload), [`dma_channel_start()`](#hal_dma-h-macros) and the other channel functions.

| Parameter | Description |
|---|---|
| `h` | Handle from [`dma_request_channel()`](#dma_request_channel). |

**Returns:** Channel index (0-7), or -1 if `h` is NULL.

### dma_dump_allocation { #dma_dump_allocation }

```c
void dma_dump_allocation(void);
```

Print the channel allocation table to the console.

Prints one line per channel with owner, request line, direction and reference count. Task context only (takes the allocator mutex).

### dma_channel_is_allocator_owned { #dma_channel_is_allocator_owned }

```c
int dma_channel_is_allocator_owned(int dma_id, int dma_ch);
```

Check whether a channel is owned by the allocator.

Code that uses fixed channel numbers can call it to detect a conflict with an allocator user.

| Parameter | Description |
|---|---|
| `dma_id` | DMA controller, `DMA0_ID`. |
| `dma_ch` | Channel index, `DMA0_CHx_INDEX`. |

**Returns:** 1 if the channel was claimed with [`dma_request_channel()`](#dma_request_channel); 0 otherwise (also for out-of-range arguments or before the first request).

### Anonymous enum { #hal_dma-h-enum }

Commands for [`dma_ioctl()`](#dma_ioctl).

| Name | Value | Description |
|---|---|---|
| `DMA_CTRL_SET_INT` | `0` | Unmask the channel's transfer-complete and error interrupts. `args` is unused. |
| `DMA_CTRL_CLEAR_INT` |  | Mask the channel's transfer-complete and error interrupts. `args` is unused. |
| `DMA_CTRL_CHANNEL_LLI_UPDATE` |  | Load the LLI item at address `args` (`dma_lli_ctrl_t *`) into the channel registers. |
| `DMA_CTRL_CHANNEL_TRANS_PARAM_UPDATE` |  | Update the stored width, burst and address increment settings from `args` (`dma_trans_param_t *`). The new values are used by the next [`dma_reload()`](#dma_reload). |
| `DMA_CTRL_CHANNEL_GET_STATUS` |  | Query the channel: [`dma_ioctl()`](#dma_ioctl) returns 1 while the channel is enabled (transfer in progress), 0 when it is idle. `args` is unused. |
| `DMA_CTRL_CHANNEL_START` |  | Enable the channel (start the loaded transfer). `args` is unused. |
| `DMA_CTRL_CHANNEL_STOP` |  | Disable the channel. `args` is unused. |
| `DMA_CTRL_SET_CALLBACK` |  | Set the completion callback. `args` is a function pointer with the signature of `dma_device_t::callback`. |

### dma_index_type { #dma_index_type }

DMA channel index (the `dma_ch` argument of the DMA functions).

| Name | Value | Description |
|---|---|---|
| `DMA0_CH0_INDEX` | `0` | Channel 0. |
| `DMA0_CH1_INDEX` |  | Channel 1. |
| `DMA0_CH2_INDEX` |  | Channel 2. |
| `DMA0_CH3_INDEX` |  | Channel 3. |
| `DMA0_CH4_INDEX` |  | Channel 4. |
| `DMA0_CH5_INDEX` |  | Channel 5. |
| `DMA0_CH6_INDEX` |  | Channel 6. |
| `DMA0_CH7_INDEX` |  | Channel 7. |
| `DMA_MAX_INDEX` |  | Number of channels per controller. |

### Anonymous enum { #hal_dma-h-enum-2 }

DMA controller index (the `dma_id` argument of the DMA functions).

| Name | Value | Description |
|---|---|---|
| `DMA0_ID` | `0` | The DMA controller. |
| `DMA_ID_MAX` |  | Number of DMA controllers. |

### dma_transfer_dir_type { #dma_transfer_dir_type }

Transfer direction (`dma_device_t::direction`).

| Name | Value | Description |
|---|---|---|
| `DMA_MEMORY_TO_MEMORY` | `0` | Memory to memory. |
| `DMA_MEMORY_TO_PERIPH` |  | Memory to peripheral. |
| `DMA_PERIPH_TO_MEMORY` |  | Peripheral to memory. |
| `DMA_PERIPH_TO_PERIPH` |  | Peripheral to peripheral. |

### Anonymous enum { #hal_dma-h-enum-3 }

Events passed to the channel callback (`dma_device_t::callback`).

| Name | Value | Description |
|---|---|---|
| `HAL_DMA_INT_COMPLETE` | `0` | An LLI item with its interrupt bit set has completed (end of transfer, or end of a buffer segment in circular modes). |
| `HAL_DMA_INT_ERR` |  | The channel reported a transfer error. |

### dma_control_data_t { #dma_control_data_t }

Control word of an LLI item.

[`dma_reload()`](#dma_reload) fills it from the channel configuration. In the field descriptions, "reset" is the hardware reset value of the field.

| Field | Type | Description |
|---|---|---|
| `bits` | `struct dma_control_data_t::@236360215344316233303071060244070213363063353174` | Bit-field view of the control word. |
| `WORD` | `uint32_t` | Raw 32-bit control word. |

### dma_lli_ctrl_t { #dma_lli_ctrl_t }

One linked-list item (LLI) of a DMA transfer, as read by the controller.

Items reached through `nextlli` are fetched from memory by the controller, so a chain built by the application must be written back from the data cache before the transfer starts. [`dma_reload()`](#dma_reload) does this for the chains it builds.

| Field | Type | Description |
|---|---|---|
| `src_addr` | `uint32_t` | Source address. |
| `dst_addr` | `uint32_t` | Destination address. |
| `nextlli` | `uint32_t` | Address of the next item, or 0 to end the chain. |
| `cfg` | `dma_control_data_t` | Control word of this item. |

### dma_trans_param_t { #dma_trans_param_t }

Parameter block for `DMA_CTRL_CHANNEL_TRANS_PARAM_UPDATE`.

Only the fields selected in `map` are copied into the channel configuration; they take effect at the next [`dma_reload()`](#dma_reload).

| Field | Type | Description |
|---|---|---|
| `map` | `uint8_t` | OR of `DMA_PARAM_UPDATE_*` flags selecting the fields to apply. |
| `src_width` | `uint8_t` | Source width, `DMA_TRANSFER_WIDTH_*`. |
| `src_burst` | `uint8_t` | Source burst size, `DMA_BURST_INCR*`. |
| `dst_width` | `uint8_t` | Destination width, `DMA_TRANSFER_WIDTH_*`. |
| `dst_burst` | `uint8_t` | Destination burst size, `DMA_BURST_INCR*`. |
| `src_addr_inc` | `uint8_t` | Source address increment, `DMA_ADDR_INCREMENT_*`. |
| `dst_addr_inc` | `uint8_t` | Destination address increment, `DMA_ADDR_INCREMENT_*`. |

### dma_device_t { #dma_device_t }

Configuration and state of one DMA channel.

The driver keeps one record per channel, initialised from the board configuration (`DMA0_CHx_CONFIG`). Install a new one with [`dma_setConfig()`](#dma_setConfig) or modify the record returned by [`dma_getDevice()`](#dma_getDevice).

| Field | Type | Description |
|---|---|---|
| `id` | `uint8_t` | DMA controller, `DMA0_ID`. |
| `ch` | `uint8_t` | Channel index, `DMA0_CHx_INDEX`. |
| `transfer_mode` | `uint8_t` | LLI chain mode used by [`dma_reload()`](#dma_reload), `DMA_LLI_*_MODE`. |
| `direction` | `uint8_t` | Transfer direction, [`dma_transfer_dir_type`](#dma_transfer_dir_type). |
| `src_req` | `uint32_t` | Source request line, `DMA_REQUEST_*` (`DMA_REQUEST_NONE` for a memory source). |
| `dst_req` | `uint32_t` | Destination request line, `DMA_REQUEST_*` (`DMA_REQUEST_NONE` for a memory destination). |
| `src_addr_inc` | `uint8_t` | Source address increment, `DMA_ADDR_INCREMENT_*`. |
| `dst_addr_inc` | `uint8_t` | Destination address increment, `DMA_ADDR_INCREMENT_*`. |
| `src_burst_size` | `uint8_t` | Source burst size, `DMA_BURST_INCR*`. |
| `dst_burst_size` | `uint8_t` | Destination burst size, `DMA_BURST_INCR*`. |
| `src_width` | `uint8_t` | Source width, `DMA_TRANSFER_WIDTH_*`. [`dma_reload()`](#dma_reload) converts its byte count with this width. |
| `dst_width` | `uint8_t` | Destination width, `DMA_TRANSFER_WIDTH_*`. |
| `lli_count` | `uint8_t` | Number of buffers for `DMA_LLI_CYCLE_N_MODE` (2 = double buffer, 3 = triple, ...); ignored by the other modes. |
| `lli_cfg` | `dma_lli_ctrl_t *` | LLI chain owned by the driver (allocated by [`dma_reload()`](#dma_reload)); set to NULL when installing a configuration. |
| `callback` | `void(*)(void *dev, uint32_t event)` | Callback called from the DMA interrupt handler with this record as `dev` and `HAL_DMA_INT_COMPLETE` or `HAL_DMA_INT_ERR` as `event`. NULL disables it. |

### Typedefs { #hal_dma-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `dma_ch_handle_t` | `typedef struct dma_channel_handle* dma_ch_handle_t` | Opaque handle of a channel obtained from [`dma_request_channel()`](#dma_request_channel). |

### Macros { #hal_dma-h-macros }

| Name | Value | Description |
|---|---|---|
| `DMA_LLI_ONCE_MODE` | `0` | Single pass; one completion interrupt at the end of the transfer. |
| `DMA_LLI_CYCLE_MODE` | `1` | Circular: the last item links back to the first; a completion interrupt at the end of every pass. |
| `DMA_LLI_PINGPONG_MODE` | `2` | Circular double buffer: the memory buffer holds two halves of `transfer_size` bytes each and a completion interrupt is raised after each half. |
| `DMA_LLI_CYCLE_N_MODE` | `3` | Circular N-buffer mode: the memory buffer holds `lli_count` segments of `transfer_size` bytes each and a completion interrupt is raised after each segment. |
| `DMA_ADDR_INCREMENT_DISABLE` | `0` | Address stays fixed (peripheral data register). |
| `DMA_ADDR_INCREMENT_ENABLE` | `1` | Address advances after each item (memory buffer). |
| `DMA_TRANSFER_WIDTH_8BIT` | `0` | 8-bit items. |
| `DMA_TRANSFER_WIDTH_16BIT` | `1` | 16-bit items. |
| `DMA_TRANSFER_WIDTH_32BIT` | `2` | 32-bit items. |
| `DMA_TRANSFER_WIDTH_MAX` | `3` | Number of width values; not a valid width. |
| `DMA_BURST_INCR1` | `0` | 1 item per burst. |
| `DMA_BURST_INCR4` | `1` | 4 items per burst. |
| `DMA_BURST_INCR8` | `2` | 8 items per burst. |
| `DMA_BURST_INCR16` | `3` | 16 items per burst. |
| `DMA_ADDR_UART0_TDR` | `(UART0_BASE + 0x88)` | UART0 TX FIFO data register. |
| `DMA_ADDR_UART0_RDR` | `(UART0_BASE + 0x8C)` | UART0 RX FIFO data register. |
| `DMA_ADDR_UART1_TDR` | `(UART1_BASE + 0x88)` | UART1 TX FIFO data register. |
| `DMA_ADDR_UART1_RDR` | `(UART1_BASE + 0x8C)` | UART1 RX FIFO data register. |
| `DMA_ADDR_I2C_TDR` | `(I2C_BASE + 0x88)` | I2C TX FIFO data register. |
| `DMA_ADDR_I2C_RDR` | `(I2C_BASE + 0x8C)` | I2C RX FIFO data register. |
| `DMA_ADDR_SPI_TDR` | `(SPI_BASE + 0x88)` | SPI0 TX FIFO data register. |
| `DMA_ADDR_SPI_RDR` | `(SPI_BASE + 0x8C)` | SPI0 RX FIFO data register. |
| `DMA_ADDR_SPI1_TDR` | `(SPI1_BASE + 0x88)` | SPI1 TX FIFO data register. |
| `DMA_ADDR_SPI1_RDR` | `(SPI1_BASE + 0x8C)` | SPI1 RX FIFO data register. |
| `DMA_ADDR_I2S_TDR` | `(I2S_BASE + 0x88)` | I2S TX FIFO data register. |
| `DMA_ADDR_I2S_RDR` | `(I2S_BASE + 0x8C)` | I2S RX FIFO data register. |
| `DMA_ADDR_ADC_RDR` | `(GPIP_BASE + 0x04)` | General-purpose ADC data register. |
| `DMA_ADDR_DAC_TDR` | `(GPIP_BASE + 0X48)` | General-purpose DAC data register. |
| `DMA_ADDR_AUD_RDR` | `(AUD_BASE + 0xC88)` | Audio ADC RX FIFO data register. |
| `DMA_ADDR_DBI_TDR` | `(DBI_BASE   + 0x88)` | DBI (display bus interface) TX FIFO data register. |
| `DMA_REQUEST_NONE` | `0x00000000` | No peripheral (memory side); same value as `DMA_REQUEST_UART0_RX`. |
| `DMA_REQUEST_UART0_RX` | `0x00000000` | UART0 RX. |
| `DMA_REQUEST_UART0_TX` | `0x00000001` | UART0 TX. |
| `DMA_REQUEST_UART1_RX` | `0x00000002` | UART1 RX. |
| `DMA_REQUEST_UART1_TX` | `0x00000003` | UART1 TX. |
| `DMA_REQUEST_I2C0_RX` | `0x00000004` | I2C RX. |
| `DMA_REQUEST_I2C0_TX` | `0x00000005` | I2C TX. |
| `DMA_REQUEST_SPI0_RX` | `0x00000006` | SPI0 RX. |
| `DMA_REQUEST_SPI0_TX` | `0x00000007` | SPI0 TX. |
| `DMA_REQUEST_IR_TX` | `0x00000008` | IR TX. |
| `DMA_REQUEST_AUD_ADC` | `0x00000009` | Audio ADC. |
| `DMA_REQUEST_I2S_RX` | `0x0000000A` | I2S RX (IPRO7 request 10; IPRO6 uses 16). |
| `DMA_REQUEST_I2S_TX` | `0x0000000B` | I2S TX (IPRO7 request 11; IPRO6 uses 17). |
| `DMA_REQUEST_ADC0` | `0x0000000C` | General-purpose ADC. |
| `DMA_REQUEST_DAC0` | `0x0000000D` | General-purpose DAC. |
| `DMA_REQUEST_SPI1_RX` | `0x0000000E` | SPI1 RX (IPRO7 request mux). |
| `DMA_REQUEST_SPI1_TX` | `0x0000000F` | SPI1 TX (IPRO7 request mux). |
| `DMA_REQUEST_DBI_TX` | `0x00000014` | DBI TX. |
| `DMA_REQUEST_USB_EP0` | `0x00000018` | USB endpoint 0. |
| `DMA_REQUEST_USB_EP1` | `0x00000019` | USB endpoint 1. |
| `DMA_REQUEST_USB_EP2` | `0x0000001A` | USB endpoint 2. |
| `DMA_REQUEST_USB_EP3` | `0x0000001B` | USB endpoint 3. |
| `DMA_REQUEST_USB_EP4` | `0x0000001C` | USB endpoint 4. |
| `DMA_REQUEST_USB_EP5` | `0x0000001D` | USB endpoint 5. |
| `DMA_REQUEST_USB_EP6` | `0x0000001E` | USB endpoint 6. |
| `DMA_REQUEST_USB_EP7` | `0x0000001F` | USB endpoint 7. |
| `DMA_PARAM_UPDATE_SRC_WIDTH` | `(1 << 0)` | Apply `dma_trans_param_t::src_width`. |
| `DMA_PARAM_UPDATE_SRC_BURST` | `(1 << 1)` | Apply `dma_trans_param_t::src_burst`. |
| `DMA_PARAM_UPDATE_DST_WIDTH` | `(1 << 2)` | Apply `dma_trans_param_t::dst_width`. |
| `DMA_PARAM_UPDATE_DST_BURST` | `(1 << 3)` | Apply `dma_trans_param_t::dst_burst`. |
| `DMA_PARAM_UPDATE_SRC_ADDR_INC` | `(1 << 4)` | Apply `dma_trans_param_t::src_addr_inc`. |
| `DMA_PARAM_UPDATE_DST_ADDR_INC` | `(1 << 5)` | Apply `dma_trans_param_t::dst_addr_inc`. |
| `DMA_PARAM_UPDATE_WIDTH` | `(DMA_PARAM_UPDATE_SRC_WIDTH \| DMA_PAR...` | Apply both widths. |
| `DMA_PARAM_UPDATE_BURST` | `(DMA_PARAM_UPDATE_SRC_BURST \| DMA_PAR...` | Apply both burst sizes. |
| `DMA_PARAM_UPDATE_ALL` | `(0xFF)` | Apply all fields. |
| `dma_channel_start(id, chn)` | `dma_ioctl(id, chn, DMA_CTRL_CHANNEL_S...` | Start (enable) a channel. |
| `dma_channel_stop(id, chn)` | `dma_ioctl(id, chn, DMA_CTRL_CHANNEL_S...` | Stop (disable) a channel. |
| `dma_channel_lli_update(id, chn, list)` | `dma_ioctl(id, chn, DMA_CTRL_CHANNEL_L...` | Load an LLI item into a channel (see `DMA_CTRL_CHANNEL_LLI_UPDATE`). |
| `dma_channel_check_busy(id, chn)` | `dma_ioctl(id, chn, DMA_CTRL_CHANNEL_G...` | Check whether a channel is still enabled. |
| `DMA_MAX_TRANSFER_PER_LLI` | `(4096 - 32)` | Maximum number of transfer items per LLI item built by [`dma_reload()`](#dma_reload), in units of the source width. Longer transfers are split into several items. |
