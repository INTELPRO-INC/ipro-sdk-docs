---
title: Memory
description: Flash access, PSRAM, boot2 and the partition table manager.
generated: tools/gen_api.py
migrate_from: []
---

# Memory

Flash access, PSRAM, boot2 and the partition table manager.

| Header | Functions | Description |
|---|---|---|
| [`hal_flash.h`](#hal_flash-h) | 12 | Serial NOR flash access: identification, read, program, erase. |
| [`hal_psram.h`](#hal_psram-h) | 12 | On-chip PSRAM: initialization, DQS calibration and sleep modes. |
| [`hal_sf_psram.h`](#hal_sf_psram-h) | 1 | External quad-SPI PSRAM on the second serial-flash interface. |
| [`hal_boot2.h`](#hal_boot2-h) | 15 | Boot information: partition table lookup and update, efuse boot configuration, PSRAM bring-up from the boot path. |
| [`hal_ptmgr.h`](#hal_ptmgr-h) | 5 | Partition table format and low-level partition-table access. |

## hal_flash.h { #hal_flash-h }

`#include "hal_flash.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_flash.h))

Serial NOR flash access: identification, read, program, erase.

All addresses taken by these functions are flash offsets (0 = first byte of the flash device), not CPU bus addresses; the flash is also visible read-only through the XIP window at [`FLASH_XIP_BASE`](#hal_flash-h-macros). Program and erase follow NOR rules: a range must be erased (all bytes 0xFF) before it is programmed, and erase works on whole sectors.

The read, program and erase functions disable interrupts while they talk to the flash, because code and data in XIP flash are not reachable during the operation. [`flash_write()`](#flash_write) does this per 256-byte chunk; [`flash_erase()`](#flash_erase) keeps interrupts disabled for the whole erase, so split large erases if interrupt latency matters.

The flash driver is initialized during start-up ([`hal_boot2_init()`](#hal_boot2_init) calls [`flash_init()`](#flash_init)).

### flash_get_jedecid { #flash_get_jedecid }

```c
uint32_t flash_get_jedecid(void);
```

Get the JEDEC ID of the flash detected by [`flash_init()`](#flash_init).

**Returns:** The 24-bit JEDEC ID as `0xMMTTCC`: manufacturer ID in bits 23:16, memory type in bits 15:8, capacity code in bits 7:0. 0 before [`flash_init()`](#flash_init) has run.

### flash_get_size { #flash_get_size }

```c
uint32_t flash_get_size(void);
```

Get the flash size derived from the JEDEC capacity code.

**Returns:** Flash size in bytes, or 0 when the JEDEC ID is not known yet.

### flash_init { #flash_init }

```c
int flash_init(void);
```

Initialize the flash driver configuration.

Takes over the configuration set up by the boot ROM (or detects the flash when no configuration is available) so that the other functions in this header can be used.

**Returns:** 0 (`SUCCESS`) on success, non-zero if the flash could not be configured.

!!! note "Note"
    Called by [`hal_boot2_init()`](#hal_boot2_init); applications normally do not call it.

### flash_read_jedec_id { #flash_read_jedec_id }

```c
int flash_read_jedec_id(uint8_t *data);
```

Read the JEDEC ID directly from the flash device.

| Parameter | Description |
|---|---|
| `data` | Buffer of at least 4 bytes. Receives the 3 ID bytes in the order the device sends them (manufacturer first) followed by a zero byte. |

**Returns:** Always 0 (`SUCCESS`).

!!! note "Note"
    Interrupts are enabled on return, even if they were disabled on entry.

### flash_read_via_xip { #flash_read_via_xip }

```c
int flash_read_via_xip(uint32_t addr, uint8_t *data, uint32_t len);
```

Read flash through the memory-mapped XIP window and the cache.

| Parameter | Description |
|---|---|
| `addr` | Flash offset to read from. |
| `data` | Destination buffer. |
| `len` | Number of bytes to read. |

**Returns:** Always 0 (`SUCCESS`).

!!! note "Note"
    [`flash_write()`](#flash_write) and [`flash_erase()`](#flash_erase) do not invalidate the CPU cache, so data read this way can be stale after a program or erase; use [`flash_read()`](#flash_read) to read back what is in the device.

!!! note "Note"
    Interrupts are enabled on return, even if they were disabled on entry.

### flash_read { #flash_read }

```c
int flash_read(uint32_t addr, uint8_t *data, uint32_t len);
```

Read data from flash with flash commands.

| Parameter | Description |
|---|---|
| `addr` | Flash offset to read from. |
| `data` | Destination buffer. |
| `len` | Number of bytes to read. |

**Returns:** 0 (`SUCCESS`) on success, non-zero on failure.

!!! note "Note"
    Interrupts are enabled on return, even if they were disabled on entry.

### flash_write { #flash_write }

```c
int flash_write(uint32_t addr, uint8_t *data, uint32_t len);
```

Program data into flash.

The data is copied through a 256-byte internal buffer, so `data` may be located in any memory, including PSRAM. Interrupts are disabled for each 256-byte chunk and restored to their previous state afterwards.

| Parameter | Description |
|---|---|
| `addr` | Flash offset to program; the range must be erased. |
| `data` | Data to write. |
| `len` | Number of bytes to write; 0 does nothing. |

**Returns:** 0 (`SUCCESS`) on success, non-zero if `data` is NULL, the range wraps past the end of the 32-bit address space, or programming fails.

### flash_erase { #flash_erase }

```c
int flash_erase(uint32_t startaddr, uint32_t len);
```

Erase a flash range.

Every sector that overlaps `[startaddr, startaddr + len - 1]` is erased; aligned 32 KB and 64 KB blocks are erased with block commands. The sector size is normally 4 KB.

| Parameter | Description |
|---|---|
| `startaddr` | Flash offset of the first byte to erase. |
| `len` | Number of bytes to erase. |

**Returns:** 0 (`SUCCESS`) on success, non-zero on failure.

!!! note "Note"
    Data outside the requested range but in the same sector is erased too.

!!! note "Note"
    Interrupts are enabled on return, even if they were disabled on entry.

### flash_get_cfg { #flash_get_cfg }

```c
int flash_get_cfg(uint8_t **cfg_addr, uint32_t *len);
```

Get the flash configuration used by the driver.

| Parameter | Description |
|---|---|
| `cfg_addr` | Receives a pointer to the driver's `SPI_Flash_Cfg_Type` configuration. |
| `len` | Receives the size of that structure in bytes. |

**Returns:** Always 0 (`SUCCESS`).

!!! note "Note"
    The pointer refers to the driver's live configuration; treat it as read-only.

### flash_readReg { #flash_readReg }

```c
uint32_t flash_readReg(uint8_t readRegCmd, uint8_t len);
```

Read a flash register with a custom read-register command.

| Parameter | Description |
|---|---|
| `readRegCmd` | Read-register command byte, for example 0x05 or 0x35 for the status registers of most devices. |
| `len` | Number of register bytes to read (1 to 4). |

**Returns:** The register bytes in little-endian order; only the low `len` bytes are meaningful.

!!! warning "Warning"
    Does not disable interrupts. Call it with interrupts disabled and without any other flash access in progress.

### flash_writeReg { #flash_writeReg }

```c
void flash_writeReg(uint8_t writeRegCmd, uint32_t writeVal, uint8_t len);
```

Write a flash register with a custom write-register command.

| Parameter | Description |
|---|---|
| `writeRegCmd` | Write-register command byte, for example 0x01. |
| `writeVal` | Register bytes in little-endian order. |
| `len` | Number of register bytes to write (1 to 4). |

!!! warning "Warning"
    Does not disable interrupts. Call it with interrupts disabled and without any other flash access in progress. A wrong value can lock the flash or disable quad mode.

### hal_flash_config_update { #hal_flash_config_update }

```c
int hal_flash_config_update(uint32_t flashCfgAddr);
```

Print the active flash configuration if a configuration block is present.

Checks for [`FLASH_MAGIC_CODE`](#hal_flash-h-macros) at `flashCfgAddr` + 4 and, if found, prints the main fields of the configuration the driver is using. The driver configuration itself is not changed.

| Parameter | Description |
|---|---|
| `flashCfgAddr` | CPU address of the configuration block. |

**Returns:** Always 0.

### Macros { #hal_flash-h-macros }

| Name | Value | Description |
|---|---|---|
| `FLASH_NOT_DETECT` | `0x10` | Legacy status value meaning "no flash detected"; not returned by the functions in this header. |
| `FLASH_XIP_BASE` | `DRV_FLASH_XIP_BASE` | CPU bus address at which the flash is mapped for execute-in-place (XIP) reads. |
| `FLASH_MAGIC_CODE` | `0x47464346` | Magic word (ASCII "FCFG" in little-endian byte order) that marks a stored flash-configuration block; checked by [`hal_flash_config_update()`](#hal_flash_config_update). |

## hal_psram.h { #hal_psram-h }

`#include "hal_psram.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_psram.h))

On-chip PSRAM: initialization, DQS calibration and sleep modes.

The functions are available in builds with `CONFIG_USE_PSRAM`. The system start-up code initializes and calibrates the PSRAM before the PSRAM data sections are loaded, so applications normally only use the sleep-mode functions, if any.

The DQS (read strobe) delay is chosen from a table of [`HAL_PSRAM_DQS_TABLE_SIZE`](#hal_psram-h-macros) steps. A calibration result ("DQS
configuration") is encoded as `(left << 4) | right`, the first and last table index at which the PSRAM passed the read/write test; the centre of that window is used.

### hal_psram_gpio_init { #hal_psram_gpio_init }

```c
void hal_psram_gpio_init(void);
```

Prepare the PSRAM pads for the PSRAM controller.

Releases the sleep-mode pad configuration of the PSRAM pins and resets them to plain inputs without pull resistors.

### hal_psram_get_dqs_value { #hal_psram_get_dqs_value }

```c
uint16_t hal_psram_get_dqs_value(uint8_t index);
```

Get an entry of the DQS delay table.

| Parameter | Description |
|---|---|
| `index` | Table index, 0 to [`HAL_PSRAM_DQS_TABLE_SIZE`](#hal_psram-h-macros) - 1. |

**Returns:** The DQS delay setting; 0xFFC0 (the default delay) for an index outside the table.

### hal_psram_get_dqs_cfg { #hal_psram_get_dqs_cfg }

```c
uint16_t hal_psram_get_dqs_cfg(void);
```

Get the DQS configuration in use.

**Returns:** DQS configuration `(left << 4) | right`, as set by calibration or [`hal_psram_set_dqs_cfg()`](#hal_psram_set_dqs_cfg); 0 before either.

### hal_psram_set_dqs_cfg { #hal_psram_set_dqs_cfg }

```c
void hal_psram_set_dqs_cfg(uint16_t cfg);
```

Record the DQS configuration of a PSRAM initialized elsewhere.

Used by the start-up code when the PSRAM was set up before the HAL (by the early start-up code or the boot loader), so that the low-power framework can restore it after PDS.

| Parameter | Description |
|---|---|
| `cfg` | DQS configuration `(left << 4) \| right`. |

### hal_psram_winbond_init_dqs { #hal_psram_winbond_init_dqs }

```c
uint16_t hal_psram_winbond_init_dqs(int8_t burst_len, uint8_t is_fixLatency, uint8_t latency, uint16_t dqs_delay);
```

Initialize the PSRAM controller and device with a given DQS delay.

| Parameter | Description |
|---|---|
| `burst_len` | Burst length, a `PSRAM_WINBOND_BURST_LENGTH_*` value of the PSRAM driver. |
| `is_fixLatency` | 1 for fixed latency, 0 for variable latency. |
| `latency` | Latency, a `PSRAM_WINBOND_*_CLOCKS_LATENCY` value. |
| `dqs_delay` | DQS delay setting, for example from [`hal_psram_get_dqs_value()`](#hal_psram_get_dqs_value). |

**Returns:** The PSRAM ID register read back; [`HAL_PSRAM_ID_WINBOND_8MB`](#hal_psram-h-macros) when the device responds correctly.

### hal_psram_enter_hybridsleep { #hal_psram_enter_hybridsleep }

```c
void hal_psram_enter_hybridsleep(void);
```

Put the PSRAM into hybrid sleep; its contents are retained.

The PSRAM cannot be accessed until [`hal_psram_exit_hybridsleep()`](#hal_psram_exit_hybridsleep) (or the low-power framework's restore) has run. Used by the PDS entry path.

### hal_psram_enter_deepsleep { #hal_psram_enter_deepsleep }

```c
void hal_psram_enter_deepsleep(void);
```

Put the PSRAM into deep power-down; its contents are lost.

The PSRAM must be initialized again before it is used.

### hal_psram_exit_hybridsleep { #hal_psram_exit_hybridsleep }

```c
void hal_psram_exit_hybridsleep(void);
```

Leave hybrid sleep; blocks for about 120 us.

### hal_psram_rw_check { #hal_psram_rw_check }

```c
uint8_t hal_psram_rw_check(void);
```

Test the PSRAM with a write/read pattern.

**Returns:** `SUCCESS` (0) if the test passed, `ERROR` (1) otherwise.

!!! warning "Warning"
    Destructive: overwrites the first 1 MB of the PSRAM.

### hal_psram_x8_calibration { #hal_psram_x8_calibration }

```c
uint16_t hal_psram_x8_calibration(uint16_t psram_dqs_cfg, int32_t *psram_dqs_win_num, uint16_t *new_dqs_cfg);
```

Select the DQS delay of the PSRAM.

With a valid efuse value the PSRAM is initialized at the centre of the stored window. With `psram_dqs_cfg` = 0xFFFF (no efuse trim) all [`HAL_PSRAM_DQS_TABLE_SIZE`](#hal_psram-h-macros) delays are tried with [`hal_psram_rw_check()`](#hal_psram_rw_check) and the centre of the passing window is used; the window must be wider than 4 steps.

| Parameter | Description |
|---|---|
| `psram_dqs_cfg` | DQS configuration from efuse ([`hal_boot2_get_psram_dqs_cfg()`](#hal_boot2_get_psram_dqs_cfg)), or 0xFFFF. |
| `psram_dqs_win_num` | Receives the window width in table steps; must not be NULL. |
| `new_dqs_cfg` | Receives the DQS configuration used; may be NULL. |

**Returns:** [`HAL_PSRAM_ID_WINBOND_8MB`](#hal_psram-h-macros) on success, `ERROR` (1) on failure.

!!! warning "Warning"
    Destructive when a sweep runs: overwrites the first 1 MB of the PSRAM for every tried delay.

### hal_psram_init { #hal_psram_init }

```c
uint32_t hal_psram_init(uint16_t psram_dqs_cfg);
```

Initialize and calibrate the PSRAM.

Sets up the pads and the PSRAM clock, then runs [`hal_psram_x8_calibration()`](#hal_psram_x8_calibration) and keeps the result for the low-power framework. Runs from TCM.

| Parameter | Description |
|---|---|
| `psram_dqs_cfg` | DQS configuration from efuse ([`hal_boot2_get_psram_dqs_cfg()`](#hal_boot2_get_psram_dqs_cfg)), or 0xFFFF to calibrate. |

**Returns:** [`HAL_PSRAM_ID_WINBOND_8MB`](#hal_psram-h-macros) on success.

!!! warning "Warning"
    On a calibration failure the function does not return: it prints the window width every 500 ms forever.

### hal_psram_print_calibration_log { #hal_psram_print_calibration_log }

```c
void hal_psram_print_calibration_log(void);
```

Print the PSRAM calibration log recorded during early boot.

Calibration runs before the console is available, so its messages are kept in a small buffer at the start of the heap. Call this after the console UART is initialized and before the heap is used; the buffer is printed once.

### Macros { #hal_psram-h-macros }

| Name | Value | Description |
|---|---|---|
| `HAL_PSRAM_ID_WINBOND_8MB` | `0x0c86` | Value of the PSRAM ID register of the supported 8 MB device. |
| `HAL_PSRAM_DQS_TABLE_SIZE` | `16` | Number of entries in the DQS delay table. |

## hal_sf_psram.h { #hal_sf_psram-h }

`#include "hal_sf_psram.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sf_psram.h))

External quad-SPI PSRAM on the second serial-flash interface.

### hal_sf_psram_init { #hal_sf_psram_init }

```c
void hal_sf_psram_init(uint8_t sw_reset);
```

Initialize an external quad-SPI PSRAM and enable cached access.

Configures the pins (CLK GPIO27, CS GPIO17, DATA0 to DATA3 on GPIO28, GPIO24, GPIO23 and GPIO26, flash CS GPIO25), initializes the controller and the device, resets the device, reads and prints its ID, and enables cached quad-mode access.

| Parameter | Description |
|---|---|
| `sw_reset` | Not used; a software reset of the PSRAM is always issued. |

## hal_boot2.h { #hal_boot2-h }

`#include "hal_boot2.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_boot2.h))

Boot information: partition table lookup and update, efuse boot configuration, PSRAM bring-up from the boot path.

At start-up the boot loader (boot2) hands the active partition table to the firmware. [`hal_boot2_init()`](#hal_boot2_init) copies it into RAM (reading it from flash if the hand-over copy is not valid) and initializes the flash driver. Afterwards the partition helpers in this header resolve a partition by name to its flash offset or to its XIP bus address, and [`hal_boot2_update_ptable()`](#hal_boot2_update_ptable) switches the active image slot of an entry for a firmware update (see [`hal_ptmgr.h`](#hal_ptmgr-h) for the table format).

Typical firmware-update flow:

```c
PtTable_Entry_Config e;
if (hal_boot2_get_active_entries(PT_ENTRY_FW_CPU0, &e) == 0) {
    uint32_t slot = e.Address[!e.activeIndex];   // inactive slot
    // erase and write the new image at 'slot' with flash_erase()/flash_write()
    e.len = image_len;                           // size of the new image
    hal_boot2_update_ptable(&e);                 // boot the new slot next time
    hal_reboot();
}
```

### hal_boot2_partition_bus_addr_active { #hal_boot2_partition_bus_addr_active }

```c
int hal_boot2_partition_bus_addr_active(const char *name, uint32_t *addr, uint32_t *size);
```

Get the XIP bus address and size of the active copy of a partition.

Same as [`hal_boot2_partition_bus_addr()`](#hal_boot2_partition_bus_addr), returning only the copy selected by the entry's active index.

| Parameter | Description |
|---|---|
| `name` | Partition name, for example `"factory"`. |
| `addr` | Bus address of the active copy. |
| `size` | Maximum size of the active copy in bytes. |

**Returns:** 0 on success, or a negative errno value as listed for [`hal_boot2_partition_bus_addr()`](#hal_boot2_partition_bus_addr).

### hal_boot2_partition_bus_addr_inactive { #hal_boot2_partition_bus_addr_inactive }

```c
int hal_boot2_partition_bus_addr_inactive(const char *name, uint32_t *addr, uint32_t *size);
```

Get the XIP bus address and size of the inactive copy of a partition.

| Parameter | Description |
|---|---|
| `name` | Partition name. |
| `addr` | Bus address of the inactive copy. |
| `size` | Maximum size of the inactive copy in bytes. |

**Returns:** 0 on success, or a negative errno value as listed for [`hal_boot2_partition_bus_addr()`](#hal_boot2_partition_bus_addr).

### hal_boot2_partition_bus_addr { #hal_boot2_partition_bus_addr }

```c
int hal_boot2_partition_bus_addr(const char *name, uint32_t *addr0, uint32_t *addr1, uint32_t *size0, uint32_t *size1, int *active);
```

Look up a partition and return both copies as XIP bus addresses.

The flash offsets stored in the partition table are converted to addresses in the memory-mapped flash window, relative to the flash offset of the running image, so the partition can be read directly through a pointer. This only works for partitions placed after the `"FW"` partition.

| Parameter | Description |
|---|---|
| `name` | Partition name (NUL-terminated, up to 8 characters). |
| `addr0` | Bus address of copy 0. |
| `addr1` | Bus address of copy 1. |
| `size0` | Maximum size of copy 0 in bytes. |
| `size1` | Maximum size of copy 1 in bytes. |
| `active` | Active copy index of the entry (0 or 1). |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-EIO` | No valid partition table is loaded. |
| `-ENOENT` | No partition with this name. |
| `-ECANCELED` | The table has no `"FW"` partition. |
| `-EINVAL` | The partition lies before the `"FW"` partition. |
| `-EFAULT` | The `"FW"` entry has an invalid active index. |

### hal_boot2_partition_addr_active { #hal_boot2_partition_addr_active }

```c
int hal_boot2_partition_addr_active(const char *name, uint32_t *addr, uint32_t *size);
```

Get the flash offset and size of the active copy of a partition.

| Parameter | Description |
|---|---|
| `name` | Partition name, for example `"FW"`. |
| `addr` | Flash offset of the active copy. |
| `size` | Maximum size of the active copy in bytes. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-EIO` | No valid partition table is loaded. |
| `-ENOENT` | No partition with this name. |

### hal_boot2_partition_addr_inactive { #hal_boot2_partition_addr_inactive }

```c
int hal_boot2_partition_addr_inactive(const char *name, uint32_t *addr, uint32_t *size);
```

Get the flash offset and size of the inactive copy of a partition.

Firmware updates write the new image to this copy.

| Parameter | Description |
|---|---|
| `name` | Partition name. |
| `addr` | Flash offset of the inactive copy. |
| `size` | Maximum size of the inactive copy in bytes. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-EIO` | No valid partition table is loaded. |
| `-ENOENT` | No partition with this name. |

### hal_boot2_partition_addr { #hal_boot2_partition_addr }

```c
int hal_boot2_partition_addr(const char *name, uint32_t *addr0, uint32_t *addr1, uint32_t *size0, uint32_t *size1, int *active);
```

Look up a partition and return the flash offsets of both copies.

| Parameter | Description |
|---|---|
| `name` | Partition name (NUL-terminated, up to 8 characters). |
| `addr0` | Flash offset of copy 0. |
| `addr1` | Flash offset of copy 1. |
| `size0` | Maximum size of copy 0 in bytes. |
| `size1` | Maximum size of copy 1 in bytes. |
| `active` | Active copy index of the entry (0 or 1). |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-EIO` | No valid partition table is loaded. |
| `-ENOENT` | No partition with this name. |

### hal_boot2_get_active_partition { #hal_boot2_get_active_partition }

```c
uint8_t hal_boot2_get_active_partition(void);
```

Get which of the two partition-table copies is in use.

**Returns:** The active table, a [`PtTable_ID_Type`](#PtTable_ID_Type) value ([`PT_TABLE_ID_0`](#PtTable_ID_Type) or [`PT_TABLE_ID_1`](#PtTable_ID_Type)).

### hal_boot2_get_active_entries_byname { #hal_boot2_get_active_entries_byname }

```c
int hal_boot2_get_active_entries_byname(uint8_t *name, PtTable_Entry_Config *ptEntry_hal);
```

Copy the partition entry with the given name.

| Parameter | Description |
|---|---|
| `name` | NUL-terminated partition name. |
| `ptEntry_hal` | Receives a copy of the entry. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | No entry with this name, or a NULL argument. |

### hal_boot2_get_active_entries { #hal_boot2_get_active_entries }

```c
int hal_boot2_get_active_entries(int type, PtTable_Entry_Config *ptEntry);
```

Copy the first partition entry of the given type.

| Parameter | Description |
|---|---|
| `type` | Entry type, a [`PtTable_Entry_Type`](#PtTable_Entry_Type) value such as [`PT_ENTRY_FW_CPU0`](#PtTable_Entry_Type). |
| `ptEntry` | Receives a copy of the entry. |

| Return value | Description |
|---|---|
| `0` | Success. |
| `-1` | No entry of this type, or a NULL argument. |

### hal_boot2_update_ptable { #hal_boot2_update_ptable }

```c
int hal_boot2_update_ptable(PtTable_Entry_Config *ptEntry);
```

Switch the active copy of a partition entry and store the table.

Toggles `ptEntry->activeIndex`, increments `ptEntry->age`, replaces the entry of the same type in the RAM copy of the table (or appends it) and writes the table, with its age incremented, to the partition-table copy that is not currently active. The boot loader picks the table with the higher age, so the change takes effect at the next boot.

| Parameter | Description |
|---|---|
| `ptEntry` | Entry to update, normally obtained with [`hal_boot2_get_active_entries()`](#hal_boot2_get_active_entries) or [`hal_boot2_get_active_entries_byname()`](#hal_boot2_get_active_entries_byname). Its `activeIndex` and `age` fields are modified. |

**Returns:** A [`PtTable_Error_Type`](#PtTable_Error_Type) value: [`PT_ERROR_SUCCESS`](#PtTable_Error_Type) (0) on success.

!!! note "Note"
    Blocks while the partition-table sector is erased and programmed.

### hal_boot2_dump { #hal_boot2_dump }

```c
int hal_boot2_dump(void);
```

Print the loaded partition table to the console.

**Returns:** Always 0.

### hal_boot2_psram { #hal_boot2_psram }

```c
uint32_t hal_boot2_psram(void);
```

Initialize and calibrate the on-chip PSRAM from the boot path.

Calls [`hal_psram_init()`](#hal_psram_init) with the DQS value read from efuse. Builds without `CONFIG_USE_PSRAM` return 0 without touching the hardware.

**Returns:** The PSRAM device ID on success, 0 when PSRAM support is not built in. See [`hal_psram_init()`](#hal_psram_init) for the failure behaviour.

### hal_boot2_init { #hal_boot2_init }

```c
int hal_boot2_init(void);
```

Load the partition table and initialize the flash driver.

Copies the partition table handed over by the boot loader (or reads it from flash when that copy is not valid), initializes the flash driver, prints the partition table and flash information, and applies the RC32K and RC32M oscillator trims ([`hal_rc32k_cal()`](platform.md#hal_rc32k_cal), [`hal_rc32m_cal()`](platform.md#hal_rc32m_cal)).

**Returns:** Always 0.

!!! note "Note"
    Called once during start-up by [`ipro_platform_init()`](platform.md#ipro_platform_init); call it yourself only when that function is not used. Must be called before any other function in this header except [`hal_boot2_init_efuse()`](#hal_boot2_init_efuse).

### hal_boot2_get_psram_dqs_cfg { #hal_boot2_get_psram_dqs_cfg }

```c
unsigned int hal_boot2_get_psram_dqs_cfg(void);
```

Get the PSRAM DQS calibration value read from efuse.

**Returns:** The value encoded as `(left << 4) | right`, or 0xFFFF when no valid trim is burned. Valid after [`hal_boot2_init_efuse()`](#hal_boot2_init_efuse).

### hal_boot2_init_efuse { #hal_boot2_init_efuse }

```c
void hal_boot2_init_efuse(void);
```

Read the boot-relevant efuse settings into the HAL's copy.

Called early by the system start-up code, before PSRAM is initialized. Applications do not need to call it.

### HAL_Err_Type { #HAL_Err_Type }

Generic success/error code.

| Name | Value | Description |
|---|---|---|
| `HAL_SUCCESS` | `0` | Operation succeeded. |
| `HAL_ERROR` | `1` | Operation failed. |

### boot2_efuse_hw_config { #boot2_efuse_hw_config }

Boot-relevant efuse settings, read by [`hal_boot2_init_efuse()`](#hal_boot2_init_efuse).

The HAL keeps one instance, filled during system start-up; the PSRAM calibration value is available through [`hal_boot2_get_psram_dqs_cfg()`](#hal_boot2_get_psram_dqs_cfg).

| Field | Type | Description |
|---|---|---|
| `encrypted` | `uint8_t[HAL_BOOT2_CPU_GROUP_MAX]` | Flash encryption per CPU group: 0 = off, otherwise the `SF_CTRL_AES_*BITS` key type plus 1. |
| `sign` | `uint8_t[HAL_BOOT2_CPU_GROUP_MAX]` | Secure-boot signature check per CPU group: 1 = image must be signed. |
| `hbn_check_sign` | `uint8_t` | 1 = signature is also checked when booting out of hibernate (HBN). |
| `rsvd` | `uint8_t[3]` | Reserved. |
| `chip_id` | `uint8_t[8]` | Chip identifier from efuse. |
| `pk_hash_cpu0` | `uint8_t[HAL_BOOT2_PK_HASH_SIZE]` | Secure-boot public-key hash for CPU 0. |
| `pk_hash_cpu1` | `uint8_t[HAL_BOOT2_PK_HASH_SIZE]` | Public-key hash for a second CPU; not filled on single-CPU parts. |
| `uart_download_cfg` | `uint8_t` | UART download configuration field. |
| `sf_pin_cfg` | `uint8_t` | Serial-flash pin configuration field. |
| `keep_dbg_port_closed` | `uint8_t` | 1 = debug port stays closed after boot. |
| `boot_pin_cfg` | `uint8_t` | Boot-pin configuration field. |
| `psram_dqs_cfg` | `uint32_t` | PSRAM DQS window from efuse, encoded `(left << 4) \| right`; 0xFFFF when no valid trim is burned. |
| `dev_info` | `uint32_t` | Efuse device-information word. |

### Typedefs { #hal_boot2-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `fptr_Flash_Erase_t` | `typedef int(*) fptr_Flash_Erase_t(uint32_t startaddr, uint32_t endaddr)` | Flash erase callback type. |
| `fptr_Flash_Write_t` | `typedef int(*) fptr_Flash_Write_t(uint32_t addr, uint8_t *data, uint32_t len)` | Flash program callback type. |
| `fptr_Flash_Read_t` | `typedef int(*) fptr_Flash_Read_t(uint32_t addr, uint8_t *data, uint32_t len)` | Flash read callback type. |

### Macros { #hal_boot2-h-macros }

| Name | Value | Description |
|---|---|---|
| `HAL_BOOT2_CPU_GROUP_MAX` | `1` | Number of CPU groups described by the efuse boot configuration. |
| `HAL_BOOT2_CPU_MAX` | `1` | Number of CPUs handled by the boot path. |
| `HAL_BOOT2_RAM_IMG_COUNT_MAX` | `2` | Maximum number of RAM images the boot path can load. |
| `HAL_BOOT2_PK_HASH_SIZE` | `256 / 8` | Size of a secure-boot public-key hash in bytes (SHA-256, 32 bytes). |

## hal_ptmgr.h { #hal_ptmgr-h }

`#include "hal_ptmgr.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_ptmgr.h))

Partition table format and low-level partition-table access.

The flash holds two copies of the partition table (PT0 and PT1). Each copy is a [`PtTable_Config`](#PtTable_Config) header followed by `entryCnt` [`PtTable_Entry_Config`](#PtTable_Entry_Config) entries and a CRC32 over those entries. The boot loader uses the valid copy with the higher `age`. Every entry describes one partition with two slots (`Address[0]`/`Address[1]`); `activeIndex` selects the slot that is in use, which is how A/B firmware updates are switched.

Most applications use the higher-level helpers in [`hal_boot2.h`](#hal_boot2-h), which work on the table loaded at start-up. The functions here operate on a caller supplied [`PtTable_Stuff_Config`](#PtTable_Stuff_Config) and are meant for code that reads or writes the tables itself.

### PtTable_Get_Active_Entries { #PtTable_Get_Active_Entries }

```c
PtTable_Error_Type PtTable_Get_Active_Entries(PtTable_Stuff_Config *ptStuff, PtTable_Entry_Type type, PtTable_Entry_Config *ptEntry);
```

Copy the first entry of a given type from a partition table.

| Parameter | Description |
|---|---|
| `ptStuff` | Partition table to search. |
| `type` | Entry type to look for. |
| `ptEntry` | Receives a copy of the entry. |

| Return value | Description |
|---|---|
| `PT_ERROR_SUCCESS` | Entry found and copied. |
| `PT_ERROR_PARAMETER` | `ptStuff` or `ptEntry` is NULL. |
| `PT_ERROR_ENTRY_NOT_FOUND` | No entry of this type. |

### PtTable_Update_Entry { #PtTable_Update_Entry }

```c
PtTable_Error_Type PtTable_Update_Entry(const SPI_Flash_Cfg_Type *pFlashCfg, PtTable_ID_Type targetTableID, PtTable_Stuff_Config *ptStuff, PtTable_Entry_Config *ptEntry);
```

Update an entry in a partition table and write the table to flash.

Same as [`PtTable_Update_Entry_Ops()`](#PtTable_Update_Entry_Ops) using the HAL flash functions ([`flash_read()`](#flash_read), [`flash_erase()`](#flash_erase), [`flash_write()`](#flash_write)).

| Parameter | Description |
|---|---|
| `pFlashCfg` | Unused; pass NULL. |
| `targetTableID` | Copy to write ([`PT_TABLE_ID_0`](#PtTable_ID_Type) or [`PT_TABLE_ID_1`](#PtTable_ID_Type)). |
| `ptStuff` | Table to modify and write. |
| `ptEntry` | New contents of the entry. |

**Returns:** See [`PtTable_Update_Entry_Ops()`](#PtTable_Update_Entry_Ops).

### PtTable_Get_Active_Entries_By_Name { #PtTable_Get_Active_Entries_By_Name }

```c
PtTable_Error_Type PtTable_Get_Active_Entries_By_Name(PtTable_Stuff_Config *ptStuff, uint8_t *name, PtTable_Entry_Config *ptEntry);
```

Copy the entry with a given name from a partition table.

| Parameter | Description |
|---|---|
| `ptStuff` | Partition table to search. |
| `name` | NUL-terminated partition name; must match exactly. |
| `ptEntry` | Receives a copy of the entry. |

| Return value | Description |
|---|---|
| `PT_ERROR_SUCCESS` | Entry found and copied. |
| `PT_ERROR_PARAMETER` | `ptStuff` or `ptEntry` is NULL. |
| `PT_ERROR_ENTRY_NOT_FOUND` | No entry with this name. |

### PtTable_Get_Active_Partition_Ops { #PtTable_Get_Active_Partition_Ops }

```c
PtTable_ID_Type PtTable_Get_Active_Partition_Ops(const PtTable_Flash_Ops *ops, PtTable_Stuff_Config ptStuff[2]);
```

Read both partition-table copies and select the active one.

Each copy is checked for [`PT_MAGIC_CODE`](#hal_ptmgr-h-macros), a valid entry count and both CRCs. If both are valid the one with the higher `age` is selected (PT0 on a tie).

| Parameter | Description |
|---|---|
| `ops` | Flash access functions. |
| `ptStuff` | Two-element array that receives PT0 in `ptStuff[0]` and PT1 in `ptStuff[1]`. |

**Returns:** [`PT_TABLE_ID_0`](#PtTable_ID_Type) or [`PT_TABLE_ID_1`](#PtTable_ID_Type), or [`PT_TABLE_ID_INVALID`](#PtTable_ID_Type) when neither copy is valid.

### PtTable_Update_Entry_Ops { #PtTable_Update_Entry_Ops }

```c
PtTable_Error_Type PtTable_Update_Entry_Ops(const PtTable_Flash_Ops *ops, PtTable_ID_Type targetTableID, PtTable_Stuff_Config *ptStuff, PtTable_Entry_Config *ptEntry);
```

Update an entry in a partition table and write the table to flash.

The entry with the same `type` as `ptEntry` is replaced (or `ptEntry` is appended if no such entry exists), the table `age` is incremented, both CRCs are recomputed, and the table is erased and written at the flash offset of `targetTableID`.

| Parameter | Description |
|---|---|
| `ops` | Flash access functions. |
| `targetTableID` | Copy to write ([`PT_TABLE_ID_0`](#PtTable_ID_Type) or [`PT_TABLE_ID_1`](#PtTable_ID_Type)); normally the copy that is not active, so that a power loss leaves the active copy intact. |
| `ptStuff` | Table to modify and write. |
| `ptEntry` | New contents of the entry. |

| Return value | Description |
|---|---|
| `PT_ERROR_SUCCESS` | Table written. |
| `PT_ERROR_PARAMETER` | An argument is NULL. |
| `PT_ERROR_TABLE_NOT_VALID` | `targetTableID` is [`PT_TABLE_ID_INVALID`](#PtTable_ID_Type). |
| `PT_ERROR_ENTRY_UPDATE_FAIL` | New entry, but the table is full. |
| `PT_ERROR_FALSH_WRITE` | Erasing or writing the flash failed. |

### PtTable_Error_Type { #PtTable_Error_Type }

Result codes of the partition-table functions.

| Name | Value | Description |
|---|---|---|
| `PT_ERROR_SUCCESS` |  | Success. |
| `PT_ERROR_TABLE_NOT_VALID` |  | Invalid partition table (or table ID). |
| `PT_ERROR_ENTRY_NOT_FOUND` |  | No matching entry. |
| `PT_ERROR_ENTRY_UPDATE_FAIL` |  | Entry could not be added: table full. |
| `PT_ERROR_CRC32` |  | CRC32 mismatch. |
| `PT_ERROR_PARAMETER` |  | Invalid argument (for example NULL). |
| `PT_ERROR_FALSH_READ` |  | Flash read failed. |
| `PT_ERROR_FALSH_WRITE` |  | Flash write (or erase) failed. |
| `PT_ERROR_FALSH_ERASE` |  | Flash erase failed. |

### PtTable_ID_Type { #PtTable_ID_Type }

Identifies one of the two partition-table copies.

| Name | Value | Description |
|---|---|---|
| `PT_TABLE_ID_0` |  | Partition table copy 0 (PT0). |
| `PT_TABLE_ID_1` |  | Partition table copy 1 (PT1). |
| `PT_TABLE_ID_INVALID` |  | Neither copy is valid. |

### PtTable_Entry_Type { #PtTable_Entry_Type }

Well-known partition entry types (`PtTable_Entry_Config::type`).

| Name | Value | Description |
|---|---|---|
| `PT_ENTRY_FW_CPU0` |  | Firmware image of CPU 0 (the application). |
| `PT_ENTRY_FW_CPU1` |  | Firmware image of a second CPU. |
| `PT_ENTRY_MAX` | `16` | Maximum number of entries in a table. |

### PtTable_Config { #PtTable_Config }

Partition table header.

| Field | Type | Description |
|---|---|---|
| `magicCode` | `uint32_t` | [`PT_MAGIC_CODE`](#hal_ptmgr-h-macros) for a valid table. |
| `version` | `uint16_t` | Table format version. |
| `entryCnt` | `uint16_t` | Number of entries that follow (1 to [`PT_ENTRY_MAX`](#PtTable_Entry_Type)). |
| `age` | `uint32_t` | Update counter; the valid copy with the higher age is used. |
| `crc32` | `uint32_t` | CRC32 of the preceding header fields. |

### PtTable_Entry_Config { #PtTable_Entry_Config }

One partition entry.

| Field | Type | Description |
|---|---|---|
| `type` | `uint8_t` | Entry type, see [`PtTable_Entry_Type`](#PtTable_Entry_Type). |
| `device` | `uint8_t` | Storage device index. |
| `activeIndex` | `uint8_t` | Slot in use: 0 = `Address[0]`, 1 = `Address[1]`. |
| `name` | `uint8_t[9]` | NUL-terminated partition name. |
| `Address` | `uint32_t[2]` | Flash offset of slot 0 and slot 1. |
| `maxLen` | `uint32_t[2]` | Size reserved for slot 0 and slot 1, in bytes. |
| `len` | `uint32_t` | Length of the image in the active slot, in bytes. |
| `age` | `uint32_t` | Entry update counter. |

### PtTable_Stuff_Config { #PtTable_Stuff_Config }

In-memory image of one partition-table copy.

| Field | Type | Description |
|---|---|---|
| `ptTable` | `PtTable_Config` | Table header. |
| `ptEntries` | `PtTable_Entry_Config[PT_ENTRY_MAX]` | Entries; only the first `ptTable.entryCnt` are used. |
| `crc32` | `uint32_t` | CRC32 of the used entries, as filled by [`hal_boot2_init()`](#hal_boot2_init). In flash, and in tables handled by the `_Ops` functions, the CRC is stored directly after the last used entry instead. |

### PtTable_Flash_Ops { #PtTable_Flash_Ops }

Flash access functions used by the `_Ops` variants.

Addresses are flash offsets. Each function returns 0 (`SUCCESS`) on success and non-zero on failure.

| Field | Type | Description |
|---|---|---|
| `read` | `int(*)(uint32_t addr, uint8_t *data, uint32_t len)` | Read `len` bytes at `addr` into `data`. |
| `erase` | `int(*)(uint32_t addr, uint32_t len)` | Erase `len` bytes starting at `addr`. |
| `write` | `int(*)(uint32_t addr, uint8_t *data, uint32_t len)` | Program `len` bytes at `addr`. |

### Typedefs { #hal_ptmgr-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `pPtTable_Flash_Erase` | `typedef int(*) pPtTable_Flash_Erase(uint32_t startaddr, uint32_t endaddr)` | Flash erase callback type. |
| `pPtTable_Flash_Write` | `typedef int(*) pPtTable_Flash_Write(uint32_t addr, uint8_t *data, uint32_t len)` | Flash program callback type. |
| `pPtTable_Flash_Read` | `typedef int(*) pPtTable_Flash_Read(uint32_t addr, uint8_t *data, uint32_t len)` | Flash read callback type. |

### Macros { #hal_ptmgr-h-macros }

| Name | Value | Description |
|---|---|---|
| `PT_TABLE0_ADDRESS` | `0xE000` | Flash offset of partition-table copy 0. On IPRO7 the `_Ops` functions take the actual offset from the boot header (flash offset 164) instead. |
| `PT_TABLE1_ADDRESS` | `0xF000` | Flash offset of partition-table copy 1. On IPRO7 the `_Ops` functions take the actual offset from the boot header (flash offset 168) instead. |
| `PT_MAGIC_CODE` | `0x54505049` | Magic word of a valid partition table (`PtTable_Config::magicCode`). |
