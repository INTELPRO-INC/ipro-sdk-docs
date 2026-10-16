---
title: Ethernet
description: EMAC, the lwIP network interface and the Ethernet PHY.
generated: tools/gen_api.py
migrate_from: []
---

# Ethernet

EMAC, the lwIP network interface and the Ethernet PHY.

| Header | Functions | Description |
|---|---|---|
| [`hal_emac.h`](#hal_emac-h) | 22 | Ethernet MAC (EMAC) driver: initialization, buffer-descriptor TX/RX, MDIO access to the PHY and interrupt hooks. |
| [`hal_ethernetif.h`](#hal_ethernetif-h) | 3 | lwIP network interface for the Ethernet MAC: interface setup, link handling and DHCP client. |
| [`ethernet_phy.h`](#ethernet_phy-h) | 2 | Ethernet PHY driver: configuration, auto-negotiation and link status. |

## hal_emac.h { #hal_emac-h }

`#include "hal_emac.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_emac.h))

Ethernet MAC (EMAC) driver: initialization, buffer-descriptor TX/RX, MDIO access to the PHY and interrupt hooks.

The EMAC moves frames through a table of hardware buffer descriptors (BDs): the TX descriptors come first, followed by the RX descriptors. Each descriptor points at one frame buffer. Typical sequence:

1. [`emac_init()`](#emac_init) - pins, clock, MAC configuration and interrupt handler.
1. [`emac_phy_init()`](#emac_phy_init) ([`ethernet_phy.h`](#ethernet_phy-h)) - PHY reset and auto-negotiation.
1. [`emac_bd_init()`](#emac_bd_init) - descriptor rings and their buffers.
1. [`emac_start()`](#emac_start) - enable the transmitter and the receiver.
1. [`emac_bd_tx_enqueue()`](#emac_bd_tx_enqueue) / [`emac_bd_rx_dequeue()`](#emac_bd_rx_dequeue) - move frames.

Most applications do not call these functions directly but use the lwIP network interface in [`hal_ethernetif.h`](#hal_ethernetif-h), which runs this sequence. The driver controls EMAC instance 0.

### emac_init { #emac_init }

```c
int emac_init(emac_device_t *emac_cfg);
```

Initialize the EMAC: pins, clock, MAC settings and interrupt handler.

Configures GPIO3-GPIO7 and GPIO36-GPIO39 as EMAC pins, then drives GPIO40 as the PHY reset line (low for 10 ms, then high, followed by a 150 ms wait). Enables the EMAC clock, selects the external 50 MHz RMII reference clock and programs the MAC: the MAC address from `emac_cfg`, SPEED_SEL_MODE, hardware padding and CRC generation, 64-byte minimum and `ETH_MAX_PACKET_SIZE` maximum frame length, reception of broadcast frames and promiscuous mode (address filtering is left to the network stack). Finally registers the EMAC interrupt handler and unmasks all EMAC interrupts. The transmitter and receiver stay disabled until [`emac_start()`](#emac_start).

| Parameter | Description |
|---|---|
| `emac_cfg` | MAC configuration; only `mac_addr` is used. |

**Returns:** 0 (always).

!!! note "Note"
    Blocking for about 160 ms because of the PHY reset sequence.

### emac_bd_init { #emac_bd_init }

```c
int emac_bd_init(uint8_t *eth_tx_buff, uint8_t tx_buf_count, uint8_t *eth_rx_buff, uint8_t rx_buf_count);
```

Set up the TX and RX buffer-descriptor rings.

Descriptor i of each ring points at offset `i * ETH_MAX_PACKET_SIZE` of its buffer area. TX descriptors start empty; RX descriptors are handed to the EMAC, ready to receive. Resets the driver's ring indexes.

| Parameter | Description |
|---|---|
| `eth_tx_buff` | TX buffer area of `tx_buf_count * ETH_MAX_PACKET_SIZE` bytes, or NULL to leave the TX buffer addresses at 0 (then only [`EMAC_NOCOPY_PACKET`](#hal_emac-h-macros) transmissions work). |
| `tx_buf_count` | Number of TX descriptors (at least 1). |
| `eth_rx_buff` | RX buffer area of `rx_buf_count * ETH_MAX_PACKET_SIZE` bytes. |
| `rx_buf_count` | Number of RX descriptors (at least 1). |

**Returns:** 0 (always).

**Precondition:** [`emac_init()`](#emac_init) has been called; the transmitter and receiver are stopped.

!!! note "Note"
    The driver does no cache maintenance: place both buffer areas in non-cacheable memory (hal_ethernetif.c uses `ATTR_NOCACHE_NOINIT_RAM_SECTION`).

### emac_bd_fragment_support { #emac_bd_fragment_support }

```c
int emac_bd_fragment_support(void);
```

Tell whether [`emac_bd_tx_enqueue()`](#emac_bd_tx_enqueue) accepts frames split over several descriptors.

**Returns:** 1 (fragmented frames are supported, see [`EMAC_FRAGMENT_PACKET`](#hal_emac-h-macros)).

### emac_bd_tx_enqueue { #emac_bd_tx_enqueue }

```c
int emac_bd_tx_enqueue(uint32_t flags, uint32_t len, const uint8_t *data_in);
```

Queue one frame, or one fragment of a frame, on the next TX descriptor.

Unless [`EMAC_NOCOPY_PACKET`](#hal_emac-h-macros) is given, the data is copied into the descriptor's buffer. The descriptor is then handed to the EMAC, which pads short frames and appends the CRC; it transmits once the transmitter is enabled ([`emac_start()`](#emac_start) or [`emac_start_tx()`](#emac_start_tx)). Non-blocking.

| Parameter | Description |
|---|---|
| `flags` | [`EMAC_NORMAL_PACKET`](#hal_emac-h-macros), or a combination of [`EMAC_FRAGMENT_PACKET`](#hal_emac-h-macros) and [`EMAC_NOCOPY_PACKET`](#hal_emac-h-macros). |
| `len` | Number of bytes in `data_in`, without the CRC. When copying, at most `ETH_MAX_PACKET_SIZE` (not checked). |
| `data_in` | Frame data, starting with the destination MAC address. |

| Return value | Description |
|---|---|
| `0` | Queued. |
| `NORESC` | The next TX descriptor is still owned by the EMAC (ring full); nothing was queued. |

**Precondition:** [`emac_bd_init()`](#emac_bd_init) has been called.

!!! note "Note"
    No locking: call from one context only, and not together with the lwIP interface of [`hal_ethernetif.h`](#hal_ethernetif-h), which drives the same descriptors.

!!! warning "Warning"
    With [`EMAC_NOCOPY_PACKET`](#hal_emac-h-macros) the descriptor keeps pointing at `data_in` afterwards: keep that memory valid until the frame is sent, and note that later copy-mode frames on the same descriptor are written into it.

### emac_bd_rx_dequeue { #emac_bd_rx_dequeue }

```c
int emac_bd_rx_dequeue(uint32_t flags, uint32_t *len, uint8_t *data_out);
```

Take the next received frame from the RX ring.

Copies the frame out of the current RX descriptor, hands the descriptor back to the EMAC and advances to the next one. Non-blocking.

| Parameter | Description |
|---|---|
| `flags` | Ignored. |
| `len` | Received frame length in bytes; 0 when no frame is ready. |
| `data_out` | Destination buffer of at least `ETH_MAX_PACKET_SIZE` bytes, or NULL to drop the frame without copying. |

| Return value | Description |
|---|---|
| `0` | A frame was taken. |
| `NORESC` | No received frame is pending. |

**Precondition:** [`emac_bd_init()`](#emac_bd_init) has been called.

!!! note "Note"
    No locking: call from one context only, and not together with the lwIP interface of [`hal_ethernetif.h`](#hal_ethernetif-h).

### emac_rx_done_callback_app { #emac_rx_done_callback_app }

```c
__WEAK void emac_rx_done_callback_app(void);
```

Application hook: a frame has been received.

Called from the EMAC interrupt handler only when [`CTX_TYPE`](#hal_emac-h-macros) is 0; with the default [`CTX_TYPE`](#hal_emac-h-macros) 1 the driver wakes its own task instead and this hook is not called. The RX-done interrupt is masked before the hook runs; unmask it with [`emac_intmask()`](#emac_intmask) once the RX ring has been drained. The driver supplies an empty weak default.

!!! note "Note"
    Runs in interrupt context: keep it short, do not block, and use only ISR-safe RTOS calls.

### emac_rx_error_callback_app { #emac_rx_error_callback_app }

```c
__WEAK void emac_rx_error_callback_app(void);
```

Application hook: a receive error occurred.

Called from the EMAC interrupt handler (with any [`CTX_TYPE`](#hal_emac-h-macros)). The driver supplies a weak default that prints a message.

!!! note "Note"
    Runs in interrupt context: keep it short, do not block, and use only ISR-safe RTOS calls.

### emac_rx_busy_callback_app { #emac_rx_busy_callback_app }

```c
__WEAK void emac_rx_busy_callback_app(void);
```

Application hook: a frame was dropped because no RX descriptor was free.

Called from the EMAC interrupt handler only when [`CTX_TYPE`](#hal_emac-h-macros) is 0. The driver supplies an empty weak default.

!!! note "Note"
    Runs in interrupt context: keep it short, do not block, and use only ISR-safe RTOS calls.

### emac_tx_error_callback_app { #emac_tx_error_callback_app }

```c
__WEAK void emac_tx_error_callback_app(void);
```

Application hook: a transmit error occurred.

Called from the EMAC interrupt handler (with any [`CTX_TYPE`](#hal_emac-h-macros)). The driver supplies a weak default that prints a message.

!!! note "Note"
    Runs in interrupt context: keep it short, do not block, and use only ISR-safe RTOS calls.

### emac_tx_done_callback_app { #emac_tx_done_callback_app }

```c
__WEAK void emac_tx_done_callback_app(void);
```

Application hook: a frame has been transmitted.

Called from the EMAC interrupt handler only when [`CTX_TYPE`](#hal_emac-h-macros) is 0. The TX-done interrupt is masked before the hook runs; unmask it with [`emac_intmask()`](#emac_intmask) when needed. The driver supplies an empty weak default.

!!! note "Note"
    Runs in interrupt context: keep it short, do not block, and use only ISR-safe RTOS calls.

### emac_phy_set_address { #emac_phy_set_address }

```c
int emac_phy_set_address(uint16_t phyAddress);
```

Select the MDIO address used by [`emac_phy_reg_read()`](#emac_phy_reg_read) and [`emac_phy_reg_write()`](#emac_phy_reg_write).

| Parameter | Description |
|---|---|
| `phyAddress` | PHY address, 0-31. |

**Returns:** 0 (always).

### emac_phy_config_full_duplex { #emac_phy_config_full_duplex }

```c
int emac_phy_config_full_duplex(uint8_t fullDuplex);
```

Set the MAC duplex mode.

[`emac_phy_init()`](#emac_phy_init) calls this with the negotiated mode.

| Parameter | Description |
|---|---|
| `fullDuplex` | 1 for full duplex, 0 for half duplex. |

**Returns:** 0 (always).

### emac_phy_reg_read { #emac_phy_reg_read }

```c
int emac_phy_reg_read(uint16_t phyReg, uint16_t *regValue);
```

Read a PHY register over MDIO.

| Parameter | Description |
|---|---|
| `phyReg` | Clause-22 register address, 0-31 (see `mii.h`). |
| `regValue` | Register value. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | The MDIO read failed. |

!!! note "Note"
    Busy-waits, without a timeout, until the MDIO transaction completes.

### emac_phy_reg_write { #emac_phy_reg_write }

```c
int emac_phy_reg_write(uint16_t phyReg, uint16_t regValue);
```

Write a PHY register over MDIO.

| Parameter | Description |
|---|---|
| `phyReg` | Clause-22 register address, 0-31 (see `mii.h`). |
| `regValue` | Value to write. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | The MDIO write failed. |

!!! note "Note"
    Busy-waits, without a timeout, until the MDIO transaction completes.

### emac_stop { #emac_stop }

```c
int emac_stop(void);
```

Disable the transmitter and the receiver.

**Returns:** 0 (always).

### emac_start { #emac_start }

```c
int emac_start(void);
```

Enable the transmitter and the receiver.

**Returns:** 0 (always).

**Precondition:** [`emac_bd_init()`](#emac_bd_init) has been called.

### emac_start_tx { #emac_start_tx }

```c
int emac_start_tx(void);
```

Enable the transmitter only.

**Returns:** 0 (always).

### emac_stop_tx { #emac_stop_tx }

```c
int emac_stop_tx(void);
```

Disable the transmitter only.

**Returns:** 0 (always).

### emac_start_rx { #emac_start_rx }

```c
int emac_start_rx(void);
```

Enable the receiver only.

**Returns:** 0 (always).

### emac_stop_rx { #emac_stop_rx }

```c
int emac_stop_rx(void);
```

Disable the receiver only.

**Returns:** 0 (always).

### emac_intmask { #emac_intmask }

```c
int emac_intmask(EMAC_INT_Type intType, int intMask);
```

Mask or unmask EMAC interrupt sources.

| Parameter | Description |
|---|---|
| `intType` | Interrupt source: one `EMAC_INT_*` value of `EMAC_INT_Type`, or `EMAC_INT_ALL`. |
| `intMask` | `MASK` (1) to disable the source, `UNMASK` (0) to enable it. |

**Returns:** 0 (always).

### emac_get_fram_len { #emac_get_fram_len }

```c
int emac_get_fram_len(uint16_t *max, uint16_t *min);
```

Read the frame length limits programmed into the EMAC.

[`emac_init()`](#emac_init) sets them to 64 bytes (minimum) and `ETH_MAX_PACKET_SIZE` (maximum).

| Parameter | Description |
|---|---|
| `max` | Maximum frame length in bytes. |
| `min` | Minimum frame length in bytes. |

**Returns:** 0 (always).

### EMAC_BD_TYPE_e { #EMAC_BD_TYPE_e }

Buffer-descriptor direction, used by the driver to locate the active descriptor.

| Name | Value | Description |
|---|---|---|
| `EMAC_BD_TYPE_INVLAID` |  | Invalid or unspecified. |
| `EMAC_BD_TYPE_TX` |  | TX descriptor. |
| `EMAC_BD_TYPE_RX` |  | RX descriptor. |
| `EMAC_BD_TYPE_NONE` |  | No descriptor. |
| `EMAC_BD_TYPE_MAX` | `0x7FFFFFFF` | Forces a 32-bit enum. |

### emac_device_t { #emac_device_t }

MAC configuration passed to [`emac_init()`](#emac_init).

| Field | Type | Description |
|---|---|---|
| `mac_addr` | `uint8_t[6]` | Station MAC address in written order (`mac_addr[0]` is the first octet). |

### Macros { #hal_emac-h-macros }

| Name | Value | Description |
|---|---|---|
| `EMAC_NORMAL_PACKET` | `(uint32_t)(0)` | Whole frame in one descriptor, copied into the descriptor buffer. |
| `EMAC_FRAGMENT_PACKET` | `(uint32_t)(0x01)` | Not the last fragment: the next queued descriptor continues the same frame. |
| `EMAC_NOCOPY_PACKET` | `(uint32_t)(0x02)` | Transmit directly from the caller's buffer instead of copying it. |
| `SPEED_SEL_MODE` | `1` | 1 = 10/100 Mb/s, 0 = 10 Mb/s only; applied by [`emac_init()`](#emac_init). |
| `CTX_TYPE` | `1` | Frame-processing model the EMAC and lwIP drivers are built with (1). 1: the EMAC interrupt handler wakes the network interface task of hal_ethernetif.c, which fills TX descriptors from its queue and drains the RX ring; the TX-done, RX-done and RX-busy application hooks are not called. 0: the interrupt handler calls those hooks directly. The drivers are compiled with this value, so changing it here alone has no effect. |
| `ETH_TX_BUFFER_SIZE` | `(ETH_MAX_PACKET_SIZE)` | Size in bytes of one TX descriptor buffer (default `ETH_MAX_PACKET_SIZE`, 1524). [`emac_bd_init()`](#emac_bd_init) lays out the buffers with a stride of `ETH_MAX_PACKET_SIZE` bytes whatever this value is, so keep it at `ETH_MAX_PACKET_SIZE`. |
| `ETH_RX_BUFFER_SIZE` | `(ETH_MAX_PACKET_SIZE)` | Size in bytes of one RX descriptor buffer (default `ETH_MAX_PACKET_SIZE`, 1524). [`emac_bd_init()`](#emac_bd_init) lays out the buffers with a stride of `ETH_MAX_PACKET_SIZE` bytes whatever this value is, so keep it at `ETH_MAX_PACKET_SIZE`. |
| `EMAC_TX_COMMON_FLAGS` | `(EMAC_BD_FIELD_MSK(TX_RD) \|  \ EMAC_B...` | Control bits set in every TX descriptor: ready (owned by the EMAC), interrupt on completion, pad short frames, append the CRC, end of frame. |

## hal_ethernetif.h { #hal_ethernetif-h }

`#include "hal_ethernetif.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_ethernetif.h))

lwIP network interface for the Ethernet MAC: interface setup, link handling and DHCP client.

Typical use, from the lwIP tcpip thread (for example in the tcpip_init() done callback):

```c
netif_add(netif, &ipaddr, &netmask, &gw, NULL, ethernetif_init, tcpip_input);
netif_set_default(netif);
ethernet_link_status_updated(netif);
netif_set_link_callback(netif, ethernet_link_status_updated); // needs LWIP_NETIF_LINK_CALLBACK
```

[`ethernetif_init()`](#ethernetif_init) brings up the MAC ([`hal_emac.h`](#hal_emac-h)) and the PHY ([`ethernet_phy.h`](#ethernet_phy-h)) and starts the driver tasks; [`ethernet_link_status_updated()`](#ethernet_link_status_updated) starts the DHCP client once the link is up. If no DHCP lease is obtained after more than four attempts, the driver applies a static fallback address built into the driver.

### ethernetif_init { #ethernetif_init }

```c
err_t ethernetif_init(struct netif *netif);
```

lwIP init callback of the Ethernet interface; pass it to netif_add().

Names the interface, sets `etharp_output()` as its output function and the driver's link output, and starts the driver TX/RX task (1024-word stack, priority 29). Then initializes the MAC with [`emac_init()`](#emac_init), using a fixed MAC address compiled into the driver (every board gets the same address), and the PHY with [`emac_phy_init()`](#emac_phy_init), configured for an RTL8201F in RMII mode with 10/100 Mb/s auto-negotiation. Sets up 6 TX and 6 RX descriptors, starts the MAC, sets an MTU of 1500 bytes and the broadcast and ARP flags, starts the DHCP client task (256-word stack, priority 16) and, when [`emac_phy_init()`](#emac_phy_init) returned 0, sets the interface and its link up.

| Parameter | Description |
|---|---|
| `netif` | Interface being added by netif_add(). |

**Returns:** `ERR_OK` (always).

!!! note "Note"
    Blocking: waits for PHY auto-negotiation (see [`PHY_ANEG_TIMEOUT`](#ethernet_phy-h-macros)).

!!! warning "Warning"
    If the PHY does not report a link (for example when no cable is connected), this function does not return: it prints an error and stops in an endless loop.

### ethernet_link_check_state { #ethernet_link_check_state }

```c
void ethernet_link_check_state(struct netif *netif);
```

Poll the PHY link state and update the interface.

If the interface link is up but [`ethernet_phy_status_get()`](#ethernet_phy_status_get) reports no link, stops the MAC and sets the interface and its link down. If both are down, runs [`emac_phy_init()`](#emac_phy_init) again. It never sets the interface up again.

| Parameter | Description |
|---|---|
| `netif` | Interface added with [`ethernetif_init()`](#ethernetif_init). |

!!! warning "Warning"
    Do not use in this release: [`ethernet_phy_status_get()`](#ethernet_phy_status_get) reads a PHY configuration that is not kept valid after [`ethernetif_init()`](#ethernetif_init) returns, and the re-initialization path passes NULL to [`emac_phy_init()`](#emac_phy_init).

### ethernet_link_status_updated { #ethernet_link_status_updated }

```c
void ethernet_link_status_updated(struct netif *netif);
```

Link-change callback: start the DHCP client when the link is up.

Link up: sets the DHCP state to [`DHCP_START`](#hal_ethernetif-h-macros); on its next poll the DHCP task clears the interface address and calls `dhcp_start()`. Link down: sets [`DHCP_LINK_DOWN`](#hal_ethernetif-h-macros). Non-blocking.

Register it with `netif_set_link_callback()` and also call it once after netif_add(), because [`ethernetif_init()`](#ethernetif_init) may set the link up before the callback is registered.

| Parameter | Description |
|---|---|
| `netif` | Ethernet interface. |

### Macros { #hal_ethernetif-h-macros }

| Name | Value | Description |
|---|---|---|
| `DHCP_OFF` | `(uint8_t)0` | DHCP idle. |
| `DHCP_START` | `(uint8_t)1` | Start requested; the task calls `dhcp_start()`. |
| `DHCP_WAIT_ADDRESS` | `(uint8_t)2` | Waiting for a lease from a DHCP server. |
| `DHCP_ADDRESS_ASSIGNED` | `(uint8_t)3` | Lease obtained. |
| `DHCP_TIMEOUT` | `(uint8_t)4` | No lease (more than 4 tries); static fallback set. |
| `DHCP_LINK_DOWN` | `(uint8_t)5` | Link lost; the client returns to [`DHCP_OFF`](#hal_ethernetif-h-macros). |

## ethernet_phy.h { #ethernet_phy-h }

`#include "ethernet_phy.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/ethernet_phy.h))

Ethernet PHY driver: configuration, auto-negotiation and link status.

The PHY is reached over the EMAC management interface (MDIO, see [`emac_phy_reg_read()`](#emac_phy_reg_read) and [`emac_phy_reg_write()`](#emac_phy_reg_write) in [`hal_emac.h`](#hal_emac-h)), so call [`emac_init()`](#emac_init) first. [`emac_phy_init()`](#emac_phy_init) resets the PHY, checks its identifier, programs the advertised modes, waits for auto-negotiation and applies the negotiated duplex mode to the MAC; [`ethernet_phy_status_get()`](#ethernet_phy_status_get) then reports the recorded link state. The driver targets the RTL8201F 10/100 PHY used by the default network interface ([`hal_ethernetif.h`](#hal_ethernetif-h)).

Register addresses and bit masks of the standard registers are in `mii.h`. The `PHY_*` register macros below are aliases for the common registers plus the extended registers of LAN8720-compatible PHYs.

### ethernet_phy_status_get { #ethernet_phy_status_get }

```c
emac_phy_status_t ethernet_phy_status_get();
```

Return the link state recorded by the last [`emac_phy_init()`](#emac_phy_init).

Reads the [`emac_phy_cfg_t`](#emac_phy_cfg_t) passed to [`emac_phy_init()`](#emac_phy_init); it does not access the PHY. Non-blocking.

**Returns:** [`EMAC_PHY_STAT_100MBITS_FULLDUPLEX`](#emac_phy_status_t) when the link is up at 100 Mb/s full duplex, [`EMAC_PHY_STAT_LINK_UP`](#emac_phy_status_t) when it is up in another mode, [`EMAC_PHY_STAT_LINK_DOWN`](#emac_phy_status_t) otherwise.

!!! warning "Warning"
    Call [`emac_phy_init()`](#emac_phy_init) first; the configuration pointer is not checked in release builds.

### emac_phy_init { #emac_phy_init }

```c
int emac_phy_init(emac_phy_cfg_t *cfg);
```

Reset and configure the PHY, then wait for the link.

Sequence: writes `BMCR_RESET` and waits 20 ms; reads the PHY identifier and compares it with `emac_phy_cfg_t::phy_id`; if [`PHY_RTL8201F_S700_RMII_TIMINGS`](#ethernet_phy-h-macros) is set, selects RMII mode; programs the advertised modes (or forces speed and duplex when `emac_phy_cfg_t::auto_negotiation` is 0) and restarts auto-negotiation if needed; waits for auto-negotiation to complete, polling every 50 ms up to [`PHY_ANEG_TIMEOUT`](#ethernet_phy-h-macros) times; stores the resulting speed, duplex and state in `cfg` and sets the MAC duplex mode with [`emac_phy_config_full_duplex()`](#emac_phy_config_full_duplex). Progress is logged on the console.

| Parameter | Description |
|---|---|
| `cfg` | PHY configuration (in) and link result (out). Must not be NULL and must stay valid afterwards (see [`emac_phy_cfg_t`](#emac_phy_cfg_t)). |

| Return value | Description |
|---|---|
| `0` | Configuration done; check `emac_phy_cfg_t::phy_state` for the link. |
| `-1` | Auto-negotiation did not complete in time; phy_state is [`PHY_STATE_DOWN`](#ethernet_phy-h-macros). |

**Precondition:** [`emac_init()`](#emac_init) has been called.

!!! note "Note"
    Blocking: returns only after auto-negotiation completes or times out.

!!! note "Note"
    If the identifier read from the PHY does not match `emac_phy_cfg_t::phy_id` (or cannot be read), the RMII, advertisement and forced-mode setup is skipped; this is not reported in the return value.

!!! note "Note"
    Only the duplex mode is applied to the MAC; the MAC speed mode is fixed by SPEED_SEL_MODE at [`emac_init()`](#emac_init).

### emac_phy_status_t { #emac_phy_status_t }

Link state reported by [`ethernet_phy_status_get()`](#ethernet_phy_status_get).

The order is significant: values up to [`EMAC_PHY_STAT_LINK_DOWN`](#emac_phy_status_t) mean "no
link", values above [`EMAC_PHY_STAT_LINK_UP`](#emac_phy_status_t) carry speed and duplex.

| Name | Value | Description |
|---|---|---|
| `EMAC_PHY_STAT_EEROR` |  | PHY error. Not returned by the current driver. |
| `EMAC_PHY_STAT_LINK_DOWN` |  | No link. |
| `EMAC_PHY_STAT_LINK_INIT` |  | Link being set up. Not returned by the current driver. |
| `EMAC_PHY_STAT_LINK_UP` |  | Link up in a mode other than 100 Mb/s full duplex. |
| `EMAC_PHY_STAT_100MBITS_FULLDUPLEX` |  | Link up at 100 Mb/s, full duplex. |
| `EMAC_PHY_STAT_100MBITS_HALFDUPLEX` |  | 100 Mb/s half duplex. Not returned by the driver. |
| `EMAC_PHY_STAT_10MBITS_FULLDUPLEX` |  | 10 Mb/s full duplex. Not returned by the driver. |
| `EMAC_PHY_STAT_10MBITS_HALFDUPLEX` |  | 10 Mb/s half duplex. Not returned by the driver. |

### emac_phy_cfg_t { #emac_phy_cfg_t }

PHY configuration and state, passed to [`emac_phy_init()`](#emac_phy_init).

Fields marked "in" are read by [`emac_phy_init()`](#emac_phy_init); fields marked "out" are written by it. The driver keeps a pointer to this structure for [`ethernet_phy_status_get()`](#ethernet_phy_status_get), so it must stay valid while that function is used.

| Field | Type | Description |
|---|---|---|
| `auto_negotiation` | `uint8_t` | In: 1 = auto-negotiate the modes in `flags`; 0 = force `speed` and `full_duplex`. |
| `full_duplex` | `uint8_t` | In: forced duplex when auto-negotiation is off (1 = full, 0 = half). Out: link duplex. |
| `phy_state` | `uint8_t` | In/out: a PHY_STATE_* value. Initialize to [`PHY_STATE_DOWN`](#ethernet_phy-h-macros); the driver sets only DOWN and UP. |
| `use_irq` | `uint8_t` | Use a PHY interrupt (0 = no). Not used by the driver. |
| `speed` | `uint16_t` | In: forced speed in Mb/s (10 or 100). Out: link speed in Mb/s (10 or 100). |
| `phy_address` | `uint16_t` | MDIO address (0-31). Not applied by [`emac_phy_init()`](#emac_phy_init); use [`emac_phy_set_address()`](#emac_phy_set_address). |
| `phy_id` | `uint32_t` | In: expected ID, compared with `((PHYID1 << 16) \| PHYID2) & 0x00FFFFF0`. Out: full ID read from the PHY. |
| `flags` | `uint32_t` | In: `SUPPORTED_*` link modes to advertise, plus the PHY option flags. |

### Macros { #ethernet_phy-h-macros }

| Name | Value | Description |
|---|---|---|
| `PHY_RTL8211x_FORCE_MASTER` | `BIT(1)` | Force 1000BASE-T master mode (RTL8211x). Not used by the driver. |
| `PHY_RTL8211F_FORCE_EEE_RXC_ON` | `BIT(3)` | Keep RXC running in EEE mode (RTL8211F). Not used by the driver. |
| `PHY_RTL8201F_S700_RMII_TIMINGS` | `BIT(4)` | RTL8201F: [`emac_phy_init()`](#emac_phy_init) selects RMII mode (page 7, register 16, bit 3). |
| `EMAC_PHY_ADDRESS` | `0x00U` | Default MDIO address of the PHY. |
| `PHY_LINK_TO` | `((uint32_t)0x00000FFFU)` | Link-up wait loop limit. |
| `PHY_AUTONEGO_COMPLETED_TO` | `((uint32_t)0x00000FFFU)` | Auto-negotiation wait loop limit. |
| `PHY_BCR` | `((uint16_t)0x00U)` | Basic control register (register 0). |
| `PHY_BSR` | `((uint16_t)0x01U)` | Basic status register (register 1). |
| `PHY_BSR_100BASETXFULL` | `(1 << 14)` | BSR: 100BASE-TX full-duplex capable. |
| `PHY_BSR_100BASETXHALF` | `(1 << 13)` | BSR: 100BASE-TX half-duplex capable. |
| `PHY_BSR_10BASETXFULL` | `(1 << 12)` | BSR: 10BASE-T full-duplex capable. |
| `PHY_BSR_10BASETXHALF` | `(1 << 11)` | BSR: 10BASE-T half-duplex capable. |
| `PHY_RESET` | `((uint16_t)0x8000U)` | BCR: software reset. |
| `PHY_LOOPBACK` | `((uint16_t)0x4000U)` | BCR: loopback mode. |
| `PHY_FULLDUPLEX_100M` | `((uint16_t)0x2100U)` | BCR value: 100 Mb/s, full duplex. |
| `PHY_HALFDUPLEX_100M` | `((uint16_t)0x2000U)` | BCR value: 100 Mb/s, half duplex. |
| `PHY_FULLDUPLEX_10M` | `((uint16_t)0x0100U)` | BCR value: 10 Mb/s, full duplex. |
| `PHY_HALFDUPLEX_10M` | `((uint16_t)0x0000U)` | BCR value: 10 Mb/s, half duplex. |
| `PHY_AUTONEGOTIATION` | `((uint16_t)0x1000U)` | BCR: enable auto-negotiation. |
| `PHY_RESTART_AUTONEGOTIATION` | `((uint16_t)0x0200U)` | BCR: restart auto-negotiation. |
| `PHY_POWERDOWN` | `((uint16_t)0x0800U)` | BCR: power-down mode. |
| `PHY_ISOLATE` | `((uint16_t)0x0400U)` | BCR: isolate the PHY from the MII. |
| `PHY_AUTONEGO_COMPLETE` | `((uint16_t)0x0020U)` | BSR: auto-negotiation complete. |
| `PHY_LINKED_STATUS` | `((uint16_t)0x0004U)` | BSR: valid link established. |
| `PHY_JABBER_DETECTION` | `((uint16_t)0x0002U)` | BSR: jabber condition detected. |
| `PHY_PHYID1` | `((uint16_t)0x02U)` | PHY identifier 1 (register 2). |
| `PHY_PHYID2` | `((uint16_t)0x03U)` | PHY identifier 2 (register 3). |
| `PHY_ADVERTISE` | `((uint16_t)0x04U)` | Auto-negotiation advertisement (reg 4). |
| `PHY_ADVERTISE_100BASETXFULL` | `(1 << 8)` | Advertise 100BASE-TX full duplex. |
| `PHY_ADVERTISE_100BASETXHALF` | `(1 << 7)` | Advertise 100BASE-TX half duplex. |
| `PHY_ADVERTISE_10BASETXFULL` | `(1 << 6)` | Advertise 10BASE-T full duplex. |
| `PHY_ADVERTISE_10BASETXHALF` | `(1 << 5)` | Advertise 10BASE-T half duplex. |
| `PHY_ADVERTISE_8023` | `(1 << 0)` | Selector field value for IEEE 802.3. |
| `PHY_LPA` | `((uint16_t)0x05U)` | Link partner ability (register 5). |
| `PHY_EXPANSION` | `((uint16_t)0x06U)` | Auto-negotiation expansion (register 6). |
| `PHY_CTRL_STATUS` | `((uint16_t)17U)` | Mode control/status (register 17). |
| `PHY_CTRL_STATUS_EDPWRDOWN` | `(1 << 13)` | Enable energy-detect power-down. |
| `PHY_CTRL_STATUS_ENERGYON` | `(1 << 1)` | Energy detected on the line. |
| `PHY_SPECIAL_MODES` | `((uint16_t)18U)` | Special modes register (register 18). |
| `PHY_SPECIAL_MODES_MODE` | `(7 << 5)` | Transceiver mode field (bits 7:5). |
| `PHY_SPECIAL_MODES_MODE_PWRDOWN` | `(6 << 5)` | Mode: power down. |
| `PHY_SPECIAL_MODES_MODE_ALL` | `(7 << 5)` | All capable, AN enabled. |
| `PHY_SPECIAL_MODES_PHYAD` | `(0x1F << 0)` | PHY address field (bits 4:0). |
| `PHY_SR` | `((uint16_t)0x1FU)` | Special control/status. |
| `PHY_SR_SPEED_OFFSET` | `(2)` | Bit position of the PHY_SR speed indication field. |
| `PHY_SR_SPEED_MASK` | `(0x7 << PHY_SR_SPEED_OFFSET)` | PHY_SR speed indication field (bits 4:2). |
| `PHY_SR_SPEED_10BASETXHALF` | `(0x1 << PHY_SR_SPEED_OFFSET)` | Speed indication: 10BASE-T half duplex. |
| `PHY_SR_SPEED_10BASETXFULL` | `(0x5 << PHY_SR_SPEED_OFFSET)` | Speed indication: 10BASE-T full duplex. |
| `PHY_SR_SPEED_100BASETXHALF` | `(0x2 << PHY_SR_SPEED_OFFSET)` | Speed indication: 100BASE-TX half duplex. |
| `PHY_SR_SPEED_100BASETXFULL` | `(0x6 << PHY_SR_SPEED_OFFSET)` | Speed indication: 100BASE-TX full duplex. |
| `PHY_SR_SPEED_MODE_COMPARE(status, mode)` | `(!!(mode == (status & PHY_SR_SPEED_MA...` | Test the PHY_SR speed indication field against one mode. |
| `PHY_SPEED_STATUS` | `((uint16_t)0x0004U)` | Bit 2: 10 Mb/s link. |
| `PHY_DUPLEX_STATUS` | `((uint16_t)0x0010U)` | Bit 4: full duplex link. |
| `PHY_ISFR` | `((uint16_t)0x1DU)` | Interrupt source flags. |
| `PHY_ISFR_INT4` | `((uint16_t)0x0010U)` | Link-down interrupt flag. |
| `PHY_GMII2RGMII_ID` | `0x5a5a5a5a` | Pseudo identifier for a GMII-to-RGMII converter. |
| `PHY_MAX_ADDR` | `32` | Number of MDIO addresses (0-31). |
| `PHY_FLAG_BROKEN_RESET` | `(1 << 0)` | The PHY does not support software reset. |
| `SUPPORTED_10baseT_Half` | `(1 << 0)` | 10BASE-T half duplex. |
| `SUPPORTED_10baseT_Full` | `(1 << 1)` | 10BASE-T full duplex. |
| `SUPPORTED_100baseT_Half` | `(1 << 2)` | 100BASE-T half duplex. |
| `SUPPORTED_100baseT_Full` | `(1 << 3)` | 100BASE-T full duplex. |
| `SUPPORTED_1000baseT_Half` | `(1 << 4)` | 1000BASE-T half duplex. |
| `SUPPORTED_1000baseT_Full` | `(1 << 5)` | 1000BASE-T full duplex. |
| `SUPPORTED_Autoneg` | `(1 << 6)` | Auto-negotiation. |
| `SUPPORTED_TP` | `(1 << 7)` | Twisted-pair port. |
| `SUPPORTED_AUI` | `(1 << 8)` | AUI port. |
| `SUPPORTED_MII` | `(1 << 9)` | MII port. |
| `SUPPORTED_FIBRE` | `(1 << 10)` | Fibre port. |
| `SUPPORTED_BNC` | `(1 << 11)` | BNC port. |
| `SUPPORTED_10000baseT_Full` | `(1 << 12)` | 10GBASE-T full duplex. |
| `SUPPORTED_Pause` | `(1 << 13)` | Symmetric pause. |
| `SUPPORTED_Asym_Pause` | `(1 << 14)` | Asymmetric pause. |
| `SUPPORTED_2500baseX_Full` | `(1 << 15)` | 2500BASE-X full duplex. |
| `SUPPORTED_Backplane` | `(1 << 16)` | Backplane. |
| `SUPPORTED_1000baseKX_Full` | `(1 << 17)` | 1000BASE-KX full duplex. |
| `SUPPORTED_10000baseKX4_Full` | `(1 << 18)` | 10GBASE-KX4 full duplex. |
| `SUPPORTED_10000baseKR_Full` | `(1 << 19)` | 10GBASE-KR full duplex. |
| `SUPPORTED_10000baseR_FEC` | `(1 << 20)` | 10GBASE-R forward error correction. |
| `SUPPORTED_1000baseX_Half` | `(1 << 21)` | 1000BASE-X half duplex. |
| `SUPPORTED_1000baseX_Full` | `(1 << 22)` | 1000BASE-X full duplex. |
| `ADVERTISED_10baseT_Half` | `(1 << 0)` | Advertise 10BASE-T half duplex. |
| `ADVERTISED_10baseT_Full` | `(1 << 1)` | Advertise 10BASE-T full duplex. |
| `ADVERTISED_100baseT_Half` | `(1 << 2)` | Advertise 100BASE-T half duplex. |
| `ADVERTISED_100baseT_Full` | `(1 << 3)` | Advertise 100BASE-T full duplex. |
| `ADVERTISED_1000baseT_Half` | `(1 << 4)` | Advertise 1000BASE-T half duplex. |
| `ADVERTISED_1000baseT_Full` | `(1 << 5)` | Advertise 1000BASE-T full duplex. |
| `ADVERTISED_Autoneg` | `(1 << 6)` | Advertise auto-negotiation. |
| `ADVERTISED_TP` | `(1 << 7)` | Twisted-pair port. |
| `ADVERTISED_AUI` | `(1 << 8)` | AUI port. |
| `ADVERTISED_MII` | `(1 << 9)` | MII port. |
| `ADVERTISED_FIBRE` | `(1 << 10)` | Fibre port. |
| `ADVERTISED_BNC` | `(1 << 11)` | BNC port. |
| `ADVERTISED_10000baseT_Full` | `(1 << 12)` | Advertise 10GBASE-T full duplex. |
| `ADVERTISED_Pause` | `(1 << 13)` | Advertise symmetric pause. |
| `ADVERTISED_Asym_Pause` | `(1 << 14)` | Advertise asymmetric pause. |
| `ADVERTISED_2500baseX_Full` | `(1 << 15)` | Advertise 2500BASE-X full duplex. |
| `ADVERTISED_Backplane` | `(1 << 16)` | Backplane. |
| `ADVERTISED_1000baseKX_Full` | `(1 << 17)` | Advertise 1000BASE-KX full duplex. |
| `ADVERTISED_10000baseKX4_Full` | `(1 << 18)` | Advertise 10GBASE-KX4 full duplex. |
| `ADVERTISED_10000baseKR_Full` | `(1 << 19)` | Advertise 10GBASE-KR full duplex. |
| `ADVERTISED_10000baseR_FEC` | `(1 << 20)` | Advertise 10GBASE-R FEC. |
| `ADVERTISED_1000baseX_Half` | `(1 << 21)` | Advertise 1000BASE-X half duplex. |
| `ADVERTISED_1000baseX_Full` | `(1 << 22)` | Advertise 1000BASE-X full duplex. |
| `PHY_DEFAULT_FEATURES` | `(SUPPORTED_Autoneg \| \ SUPPORTED_TP \|...` | Auto-negotiation, twisted pair and MII. |
| `PHY_10BT_FEATURES` | `(SUPPORTED_10baseT_Half \| \ SUPPORTED...` | 10BASE-T half and full duplex. |
| `PHY_100BT_FEATURES` | `(SUPPORTED_100baseT_Half \| \ SUPPORTE...` | 100BASE-T half and full duplex. |
| `PHY_1000BT_FEATURES` | `(SUPPORTED_1000baseT_Half \| \ SUPPORT...` | 1000BASE-T half and full duplex. |
| `PHY_BASIC_FEATURES` | `(PHY_10BT_FEATURES \| \ PHY_100BT_FEAT...` | 10/100 Mb/s modes plus [`PHY_DEFAULT_FEATURES`](#ethernet_phy-h-macros) (used by the default interface). |
| `PHY_GBIT_FEATURES` | `(PHY_BASIC_FEATURES \| \ PHY_1000BT_FE...` | [`PHY_BASIC_FEATURES`](#ethernet_phy-h-macros) plus the 1000BASE-T modes. |
| `PHY_10G_FEATURES` | `(PHY_GBIT_FEATURES \| \ SUPPORTED_1000...` | [`PHY_GBIT_FEATURES`](#ethernet_phy-h-macros) plus 10GBASE-T full duplex. |
| `PHY_ANEG_TIMEOUT` | `4000` | Maximum number of 50 ms polls [`emac_phy_init()`](#emac_phy_init) waits for auto-negotiation to complete (default 4000, about 200 s). The value is used when the driver source is compiled; to change it, define it on the compiler command line for the driver build. |
| `PHY_STATE_DOWN` | `(0)` | PHY not usable or link down. |
| `PHY_STATE_READY` | `(1)` | PHY ready, waiting for the MAC. Not set by the driver. |
| `PHY_STATE_UP` | `(2)` | Link up: auto-negotiation complete or link detected. |
| `PHY_STATE_RUNNING` | `(3)` | Interface running. Not set by the driver. |
| `PHY_STATE_NOLINK` | `(4)` | No cable connected. Not set by the driver. |
| `PHY_STATE_STOPPED` | `(5)` | PHY stopped. Not set by the driver. |
| `PHY_STATE_TESTING` | `(6)` | Test mode. Not set by the driver. |
