---
title: SD Card & SDIO
description: Hardware SD host, SDIO, and the PIO-based SD host.
generated: tools/gen_api.py
migrate_from: []
---

# SD Card & SDIO

Hardware SD host, SDIO, and the PIO-based SD host.

| Header | Functions | Description |
|---|---|---|
| [`hal_sdh.h`](#hal_sdh-h) | 10 | SD card / eMMC driver on the SDH controller: card initialization, block read and write, erase and eMMC partition helpers. |
| [`hal_sdio.h`](#hal_sdio-h) | 34 | SDIO host stack on the SDH controller: card enumeration, CMD52/CMD53 register and data access, function management and card interrupts. |
| [`hal_pio_sdh.h`](#hal_pio_sdh-h) | 13 | SD card host built on the IPRO7 PIO state machines: card initialization, 512-byte block read and write, FatFS port. |
| [`hal_pio_sdh_crc.h`](#hal_pio_sdh_crc-h) | 4 | SD command and data checksums (CRC7, 4-line CRC16) and command framing for the PIO SD host ([`hal_pio_sdh.h`](#hal_pio_sdh-h)). |

## hal_sdh.h { #hal_sdh-h }

`#include "hal_sdh.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sdh.h))

SD card / eMMC driver on the SDH controller: card initialization, block read and write, erase and eMMC partition helpers.

Typical sequence: optionally call [`SDH_ClockSet()`](#SDH_ClockSet), then [`SDH_Init()`](#SDH_Init) with a caller-owned [`sd_card_t`](#sd_card_t), then move 512-byte blocks with [`SDH_ReadMultiBlocks()`](#SDH_ReadMultiBlocks) and [`SDH_WriteMultiBlocks()`](#SDH_WriteMultiBlocks). Block addresses passed to this API are always in 512-byte block units; for byte-addressed (SDSC) cards the driver converts them to byte addresses.

[`SDH_Init()`](#SDH_Init) keeps a pointer to the [`sd_card_t`](#sd_card_t) it is given, and the other functions use it, so that structure must stay valid while the card is in use. The functions busy-poll the controller and use static transfer descriptors: they are blocking and not reentrant, so serialize calls made from several tasks.

The header also provides the SD/MMC protocol constants used by the driver (command indexes, R1 card-status bits, EXT_CSD field offsets) and the status codes ([`status_t`](#hal_sdh-h-typedefs)) that the SDIO host stack in [`hal_sdio.h`](#hal_sdio-h) extends.

### SDH_ClockSet { #SDH_ClockSet }

```c
status_t SDH_ClockSet(uint32_t clockInit, uint32_t clockSrc, uint32_t clockTransfer, SD_ID_Type sdId);
```

Set the clocks used by the next [`SDH_Init()`](#SDH_Init) or [`MMC_BootMode_Init()`](#MMC_BootMode_Init).

Only stores the values; they take effect when the controller is next configured. Defaults: 400 kHz identification clock, 96 MHz source clock, 48 MHz transfer clock. No range check is done.

| Parameter | Description |
|---|---|
| `clockInit` | Card identification clock in Hz. |
| `clockSrc` | SDH controller source clock in Hz. Must equal the actual source clock, because the bus-clock divider is computed from it. |
| `clockTransfer` | Bus clock in Hz used after identification. |
| `sdId` | Controller ID (`SDH_ID`). |

**Returns:** Always [`Status_Success`](#_generic_status).

### SDH_Init { #SDH_Init }

```c
status_t SDH_Init(uint32_t bus_wide, sd_card_t *pOutCardInfo, SD_ID_Type sdId);
```

Reset the SDH controller and initialize the inserted SD card or eMMC device.

Resets and ungates the SDH peripheral, starts the bus in 1-bit mode at the identification clock and runs the SD initialization sequence (CMD0, CMD8, ACMD41, CMD2, CMD3, CMD9, CMD7, ACMD51, a best-effort CMD6 high-speed switch, CMD16, ACMD6, ACMD13); the bus then runs at the transfer clock. A card that does not answer CMD8 is treated as eMMC (CMD1, CMD2, CMD3, CMD9, CMD7, CMD8 SEND_EXT_CSD); see [`EMMC_HIGHSPEED_MODE`](#hal_sdh-h-macros) for the eMMC bus mode. SD cards that do not answer CMD8 (Physical Layer v1.x) are therefore not supported.

| Parameter | Description |
|---|---|
| `bus_wide` | Requested data bus width (`SDH_Data_Bus_Width_Type`): `SDH_DATA_BUS_WIDTH_1BIT` or `SDH_DATA_BUS_WIDTH_4BITS` for SD cards (1-bit is used if the card lacks 4-bit support; 8-bit fails with [`Status_SDH_SetDataBusWidthFailed`](#_sdmmc_status)). For eMMC, `SDH_DATA_BUS_WIDTH_8BITS` is also accepted. |
| `pOutCardInfo` | Card description filled in by the driver. Must not be NULL and must stay valid while the card is in use: the driver keeps this pointer. |
| `sdId` | Controller ID (`SDH_ID`). |

**Returns:** [`Status_Success`](#_generic_status) when the card is initialized; [`Status_InvalidArgument`](#_generic_status) if `pOutCardInfo` is NULL; [`Status_SDH_SDIO_InvalidCard`](#_sdmmc_status) if neither the SD nor the eMMC sequence succeeded; otherwise the [`_sdmmc_status`](#_sdmmc_status) code of the step that failed (for example [`Status_SDH_GoIdleFailed`](#_sdmmc_status) or [`Status_SDH_SendCsdFailed`](#_sdmmc_status)).

!!! note "Note"
    Blocking.

### SD_Erase { #SD_Erase }

```c
status_t SD_Erase(uint32_t startaddr, uint32_t endaddr, SD_ID_Type sdId);
```

Erase a range of blocks on an SD card and wait until the card is done.

Sends CMD32, CMD33 and CMD38, then polls the card state with CMD13 while it reports the programming or receiving state (no timeout). Intended for SD cards: eMMC devices use CMD35/CMD36 instead, which this function does not send. Call after [`SDH_Init()`](#SDH_Init).

| Parameter | Description |
|---|---|
| `startaddr` | First block to erase, in 512-byte block units. |
| `endaddr` | Last block to erase (inclusive), in 512-byte block units. |
| `sdId` | Controller ID (`SDH_ID`). |

| Return value | Description |
|---|---|
| `Status_Success` | Erase completed. |
| `Status_SDH_CmdResponseError` | A command failed or its R1 response reported an error. |

### SDH_ReadMultiBlocks { #SDH_ReadMultiBlocks }

```c
status_t SDH_ReadMultiBlocks(uint8_t *readbuff, uint32_t ReadAddr, uint16_t BlockSize, uint32_t NumberOfBlocks, SD_ID_Type sdId);
```

Read blocks from the card with ADMA2 and wait for completion.

Uses CMD17 for one block or CMD18 for several, ended with auto CMD23 when the card supports it ([`SD_SupportSetBlockCountCmd`](#_sd_card_flag)) or auto CMD12 otherwise. The data cache is cleaned and invalidated over the buffer before the transfer. Call after [`SDH_Init()`](#SDH_Init).

| Parameter | Description |
|---|---|
| `readbuff` | Destination, `BlockSize * NumberOfBlocks` bytes, 8-byte aligned. |
| `ReadAddr` | First block number, in 512-byte block units. |
| `BlockSize` | Block size in bytes; pass `sd_card_t::blockSize` (512). Forced to 512 for byte-addressed (SDSC) cards. |
| `NumberOfBlocks` | Number of blocks to read, at least 1. |
| `sdId` | Controller ID (`SDH_ID`). |

| Return value | Description |
|---|---|
| `Status_Success` | Data read. |
| `Status_InvalidArgument` | `readbuff` is not 8-byte aligned. |
| `Status_Timeout` | No data completion within [`SDIO_DATATIMEOUT_MS`](#hal_sdh-h-macros). |
| `Status_SDH_TransferFailed` | The transfer could not be started or the data phase failed. |
| `Status_SDH_CmdResponseError` | The read command failed or its R1 response reported an error. |

### SDH_WriteMultiBlocks { #SDH_WriteMultiBlocks }

```c
status_t SDH_WriteMultiBlocks(const uint8_t *writebuff, uint32_t WriteAddr, uint16_t BlockSize, uint32_t NumberOfBlocks, SD_ID_Type sdId);
```

Write blocks to the card with ADMA2 and wait until the card is no longer busy.

Uses CMD24 for one block or CMD25 for several, ended with auto CMD23 when the card supports it or auto CMD12 otherwise. On an eMMC device with reliable write enabled ([`EMMC_SetRelWR()`](#EMMC_SetRelWR)) and supported ([`EXT_CSD_WR_REL_PARAM_EN`](#hal_sdh-h-macros)), the blocks are written as a reliable write. The data cache is cleaned over the buffer before the transfer. After the data phase the function waits, without a timeout, until the card releases DAT0. Call after [`SDH_Init()`](#SDH_Init).

| Parameter | Description |
|---|---|
| `writebuff` | Source data, `BlockSize * NumberOfBlocks` bytes, 8-byte aligned. |
| `WriteAddr` | First block number, in 512-byte block units. |
| `BlockSize` | Block size in bytes; pass `sd_card_t::blockSize` (512). Forced to 512 for byte-addressed (SDSC) cards. |
| `NumberOfBlocks` | Number of blocks to write, at least 1. |
| `sdId` | Controller ID (`SDH_ID`). |

| Return value | Description |
|---|---|
| `Status_Success` | Data written. |
| `Status_InvalidArgument` | `writebuff` is not 8-byte aligned. |
| `Status_Timeout` | No data completion within [`SDIO_DATATIMEOUT_MS`](#hal_sdh-h-macros). |
| `Status_SDH_TransferFailed` | The transfer could not be started or the data phase failed. |
| `Status_SDH_CmdResponseError` | The write command failed or its R1 response reported an error. |

### SDH_ReadMultiBlocksBlocking { #SDH_ReadMultiBlocksBlocking }

```c
status_t SDH_ReadMultiBlocksBlocking(uint8_t *readbuff, uint32_t ReadAddr, uint16_t BlockSize, uint32_t NumberOfBlocks, SD_ID_Type sdId);
```

Read blocks using the low-level blocking transfer of the SDH driver.

Same commands and addressing as [`SDH_ReadMultiBlocks()`](#SDH_ReadMultiBlocks); the data cache is cleaned and invalidated over the buffer before the transfer. Any command or data failure, including a timeout, is reported as [`Status_SDH_TransferFailed`](#_sdmmc_status). Call after [`SDH_Init()`](#SDH_Init).

| Parameter | Description |
|---|---|
| `readbuff` | Destination, `BlockSize * NumberOfBlocks` bytes, 8-byte aligned. |
| `ReadAddr` | First block number, in 512-byte block units. |
| `BlockSize` | Block size in bytes (512); forced to 512 for SDSC cards. |
| `NumberOfBlocks` | Number of blocks to read, at least 1. |
| `sdId` | Controller ID (`SDH_ID`). |

| Return value | Description |
|---|---|
| `Status_Success` | Data read. |
| `Status_InvalidArgument` | `readbuff` is not 8-byte aligned. |
| `Status_SDH_TransferFailed` | The transfer failed. |

### SDH_WriteMultiBlocksBlocking { #SDH_WriteMultiBlocksBlocking }

```c
status_t SDH_WriteMultiBlocksBlocking(uint8_t *writebuff, uint32_t WriteAddr, uint16_t BlockSize, uint32_t NumberOfBlocks, SD_ID_Type sdId);
```

Write blocks using the low-level blocking transfer of the SDH driver.

Same commands and addressing as [`SDH_WriteMultiBlocks()`](#SDH_WriteMultiBlocks), without reliable write. Any command or data failure, including a timeout, is reported as [`Status_SDH_TransferFailed`](#_sdmmc_status). Call after [`SDH_Init()`](#SDH_Init).

| Parameter | Description |
|---|---|
| `writebuff` | Source data, `BlockSize * NumberOfBlocks` bytes, 8-byte aligned. |
| `WriteAddr` | First block number, in 512-byte block units. |
| `BlockSize` | Block size in bytes (512); forced to 512 for SDSC cards. |
| `NumberOfBlocks` | Number of blocks to write, at least 1. |
| `sdId` | Controller ID (`SDH_ID`). |

| Return value | Description |
|---|---|
| `Status_Success` | Data written. |
| `Status_InvalidArgument` | `writebuff` is not 8-byte aligned. |
| `Status_SDH_TransferFailed` | The transfer failed. |

!!! note "Note"
    Unlike [`SDH_WriteMultiBlocks()`](#SDH_WriteMultiBlocks), this function does not clean the data cache over `writebuff` and does not wait for the card to finish programming after the data phase.

### MMC_SwitchPartition { #MMC_SwitchPartition }

```c
void MMC_SwitchPartition(int part, SD_ID_Type sdId);
```

Select the eMMC partition that later block accesses address.

Writes `part` to the EXT_CSD PARTITION_CONFIG byte with CMD6 (write-byte access) and then re-reads EXT_CSD into the [`sd_card_t`](#sd_card_t) registered by [`SDH_Init()`](#SDH_Init). eMMC only; call after [`SDH_Init()`](#SDH_Init). A failure is only reported on the console.

| Parameter | Description |
|---|---|
| `part` | New PARTITION_CONFIG value. Bits [2:0] select the partition: 0 = user area, [`EXT_CSD_PART_CONFIG_ACC_BOOT0`](#hal_sdh-h-macros) (1) = first boot partition, 2 = second boot partition, [`EXT_CSD_PART_CONFIG_ACC_RPMB`](#hal_sdh-h-macros) (3) = RPMB, [`EXT_CSD_PART_CONFIG_ACC_GP0`](#hal_sdh-h-macros) (4) = first general-purpose partition. The whole byte is written, so keep the boot configuration bits you need (the current value is in sd_card_t::ext_csd.partConfig). |
| `sdId` | Controller ID (`SDH_ID`). |

### MMC_BootMode_Init { #MMC_BootMode_Init }

```c
status_t MMC_BootMode_Init(void *data, uint32_t data_len, SD_ID_Type sdId);
```

Read eMMC boot data with the controller's boot-mode transfer.

Resets the SDH controller, configures it in 1-bit mode at the transfer clock set by [`SDH_ClockSet()`](#SDH_ClockSet), puts the device in pre-idle state (CMD0 with argument 0xF0F0F0F0) and starts a boot data transfer into `data` with ADMA2. Unlike [`SDH_Init()`](#SDH_Init), it does not reset or ungate the SDH peripheral in GLB, and no data-cache maintenance is done on `data`.

| Parameter | Description |
|---|---|
| `data` | Destination buffer; must hold `data_len` rounded up to a multiple of 512 bytes. |
| `data_len` | Number of bytes to read; rounded up to whole 512-byte blocks. |
| `sdId` | Controller ID (`SDH_ID`). |

**Returns:** [`Status_Success`](#_generic_status) when the controller reports boot done, [`Status_Fail`](#_generic_status) on a command error. If setting up the DMA descriptors or the data transfer fails, the low-level driver status (an `SDH_Stat_Type` value) is returned instead.

!!! warning "Warning"
    Polls without a timeout until boot done or a command error.

### EMMC_SetRelWR { #EMMC_SetRelWR }

```c
void EMMC_SetRelWR(int enable, SD_ID_Type sdId);
```

Enable or disable reliable write for [`SDH_WriteMultiBlocks()`](#SDH_WriteMultiBlocks) on eMMC.

Stores the setting in the [`sd_card_t`](#sd_card_t) registered by [`SDH_Init()`](#SDH_Init), so call it after [`SDH_Init()`](#SDH_Init). It takes effect only on eMMC devices whose EXT_CSD WR_REL_PARAM has [`EXT_CSD_WR_REL_PARAM_EN`](#hal_sdh-h-macros) set; [`SDH_WriteMultiBlocksBlocking()`](#SDH_WriteMultiBlocksBlocking) ignores it.

| Parameter | Description |
|---|---|
| `enable` | Non-zero to write with reliable write, 0 for normal writes. |
| `sdId` | Controller ID (`SDH_ID`). |

### SD_Error { #SD_Error }

Internal transfer wait states of the driver.

[`SD_OK`](#SD_Error) has the value 0, the same as [`Status_Success`](#_generic_status), so a [`status_t`](#hal_sdh-h-typedefs) result can also be compared against [`SD_OK`](#SD_Error).

| Name | Value | Description |
|---|---|---|
| `SD_OK` | `0` | Operation completed successfully. |
| `SD_CMD_ERROR` |  | Command phase, or a polled read data phase, reported an error. |
| `SD_DataCfg_ERROR` |  | Data phase reported an error. |
| `SD_WAITING` |  | Transfer still in progress. |

### _status_groups { #_status_groups }

Status group numbers.

| Name | Value | Description |
|---|---|---|
| `StatusGroup_Generic` | `0` | Group number for generic status codes. |
| `StatusGroup_SDH` | `1` | Group number for SDHC status code. |

### _generic_status { #_generic_status }

Generic status return codes.

| Name | Value | Description |
|---|---|---|
| `Status_Success` | `MAKE_STATUS(StatusGroup_Generic, 0)` | Success (0). |
| `Status_Fail` | `MAKE_STATUS(StatusGroup_Generic, 1)` | Generic failure. |
| `Status_OutOfRange` | `MAKE_STATUS(StatusGroup_Generic, 2)` | Value out of range. |
| `Status_InvalidArgument` | `MAKE_STATUS(StatusGroup_Generic, 3)` | Invalid argument (for example a NULL or misaligned buffer). |
| `Status_Timeout` | `MAKE_STATUS(StatusGroup_Generic, 4)` | Operation timed out. |

### _sdmmc_status { #_sdmmc_status }

SD/MMC card API's running status.

| Name | Value | Description |
|---|---|---|
| `Status_SDH_NotSupportYet` | `MAKE_STATUS(StatusGroup_SDH, 0U)` | Not supported yet. |
| `Status_SDH_TransferFailed` | `MAKE_STATUS(StatusGroup_SDH, 1U)` | Command or data transfer failed. |
| `Status_SDH_SetCardBlockSizeFailed` | `MAKE_STATUS(StatusGroup_SDH, 2U)` | Set block size failed. |
| `Status_SDH_HostNotSupport` | `MAKE_STATUS(StatusGroup_SDH, 3U)` | Host doesn't support. |
| `Status_SDH_CardNotSupport` | `MAKE_STATUS(StatusGroup_SDH, 4U)` | Card doesn't support. |
| `Status_SDH_AllSendCidFailed` | `MAKE_STATUS(StatusGroup_SDH, 5U)` | Send CID failed. |
| `Status_SDH_SendRelativeAddressFailed` | `MAKE_STATUS(StatusGroup_SDH, 6U)` | Send relative address failed. |
| `Status_SDH_SendCsdFailed` | `MAKE_STATUS(StatusGroup_SDH, 7U)` | Send CSD failed. |
| `Status_SDH_SelectCardFailed` | `MAKE_STATUS(StatusGroup_SDH, 8U)` | Select card failed. |
| `Status_SDH_SendScrFailed` | `MAKE_STATUS(StatusGroup_SDH, 9U)` | Send SCR failed. |
| `Status_SDH_SetDataBusWidthFailed` | `MAKE_STATUS(StatusGroup_SDH, 10U)` | Set bus width failed. |
| `Status_SDH_GoIdleFailed` | `MAKE_STATUS(StatusGroup_SDH, 11U)` | Go idle failed. |
| `Status_SDH_HandShakeOperationConditionFailed` | `MAKE_STATUS(StatusGroup_SDH, 12U)` | Send Operation Condition failed. |
| `Status_SDH_SendApplicationCommandFailed` | `MAKE_STATUS(StatusGroup_SDH, 13U)` | Send application command failed. |
| `Status_SDH_SwitchFailed` | `MAKE_STATUS(StatusGroup_SDH, 14U)` | Switch command failed. |
| `Status_SDH_StopTransmissionFailed` | `MAKE_STATUS(StatusGroup_SDH, 15U)` | Stop transmission failed. |
| `Status_SDH_WaitWriteCompleteFailed` | `MAKE_STATUS(StatusGroup_SDH, 16U)` | Wait write complete failed. |
| `Status_SDH_SetBlockCountFailed` | `MAKE_STATUS(StatusGroup_SDH, 17U)` | Set block count failed. |
| `Status_SDH_SetRelativeAddressFailed` | `MAKE_STATUS(StatusGroup_SDH, 18U)` | Set relative address failed. |
| `Status_SDH_SwitchBusTimingFailed` | `MAKE_STATUS(StatusGroup_SDH, 19U)` | Switch bus timing failed. |
| `Status_SDH_SendExtendedCsdFailed` | `MAKE_STATUS(StatusGroup_SDH, 20U)` | Send EXT_CSD failed. |
| `Status_SDH_ConfigureBootFailed` | `MAKE_STATUS(StatusGroup_SDH, 21U)` | Configure boot failed. |
| `Status_SDH_ConfigureExtendedCsdFailed` | `MAKE_STATUS(StatusGroup_SDH, 22U)` | Configure EXT_CSD failed. |
| `Status_SDH_EnableHighCapacityEraseFailed` | `MAKE_STATUS(StatusGroup_SDH, 23U)` | Enable high capacity erase failed. |
| `Status_SDH_SendTestPatternFailed` | `MAKE_STATUS(StatusGroup_SDH, 24U)` | Send test pattern failed. |
| `Status_SDH_ReceiveTestPatternFailed` | `MAKE_STATUS(StatusGroup_SDH, 25U)` | Receive test pattern failed. |
| `Status_SDH_SDIO_ResponseError` | `MAKE_STATUS(StatusGroup_SDH, 26U)` | SDIO response error. |
| `Status_SDH_SDIO_InvalidArgument` | `MAKE_STATUS(StatusGroup_SDH, 27U)` | SDIO invalid argument response error. |
| `Status_SDH_SDIO_SendOperationConditionFail` | `MAKE_STATUS(StatusGroup_SDH, 28U)` | SDIO send operation condition failed. |
| `Status_SDH_InvalidVoltage` | `MAKE_STATUS(StatusGroup_SDH, 29U)` | Invalid voltage. |
| `Status_SDH_SDIO_SwitchHighSpeedFail` | `MAKE_STATUS(StatusGroup_SDH, 30U)` | Switch to high speed failed. |
| `Status_SDH_SDIO_ReadCISFail` | `MAKE_STATUS(StatusGroup_SDH, 31U)` | Read CIS failed. |
| `Status_SDH_SDIO_InvalidCard` | `MAKE_STATUS(StatusGroup_SDH, 32U)` | Invalid card: neither SD nor eMMC initialization succeeded. |
| `Status_SDH_TuningFail` | `MAKE_STATUS(StatusGroup_SDH, 33U)` | Tuning failed. |
| `Status_SDH_SwitchVoltageFail` | `MAKE_STATUS(StatusGroup_SDH, 34U)` | Switch voltage failed. |
| `Status_SDH_ReTuningRequest` | `MAKE_STATUS(StatusGroup_SDH, 35U)` | Re-tuning requested. |
| `Status_SDH_SetDriverStrengthFail` | `MAKE_STATUS(StatusGroup_SDH, 36U)` | Set driver strength failed. |
| `Status_SDH_SetPowerClassFail` | `MAKE_STATUS(StatusGroup_SDH, 37U)` | Set power class failed. |
| `Status_SDH_HostNotReady` | `MAKE_STATUS(StatusGroup_SDH, 38U)` | Host controller not ready. |
| `Status_SDH_CardDetectFailed` | `MAKE_STATUS(StatusGroup_SDH, 39U)` | Card detect failed. |
| `Status_SDH_CmdResponseError` | `MAKE_STATUS(StatusGroup_SDH, 40U)` | Command failed or its R1 response reported an error bit. |
| `Status_SDH_SendSsrFailed` | `MAKE_STATUS(StatusGroup_SDH, 41U)` | Send SSR failed. |

### SDTransferState { #SDTransferState }

SDIO Transfer state (not used by this driver).

| Name | Value | Description |
|---|---|---|
| `SD_TRANSFER_OK` | `0` | No transfer in progress. |
| `SD_TRANSFER_BUSY` | `1` | Transfer in progress. |
| `SD_TRANSFER_ERROR` |  | Transfer failed. |

### SDCardState { #SDCardState }

SD card states: the CURRENT_STATE field, bits [12:9] of the R1 card status, plus a driver-defined error value.

| Name | Value | Description |
|---|---|---|
| `SD_CARD_READY` | `((uint32_t)0x00000001)` | ready |
| `SD_CARD_IDENTIFICATION` | `((uint32_t)0x00000002)` | ident |
| `SD_CARD_STANDBY` | `((uint32_t)0x00000003)` | stby |
| `SD_CARD_TRANSFER` | `((uint32_t)0x00000004)` | tran |
| `SD_CARD_SENDING` | `((uint32_t)0x00000005)` | data (sending data) |
| `SD_CARD_RECEIVING` | `((uint32_t)0x00000006)` | rcv (receiving data) |
| `SD_CARD_PROGRAMMING` | `((uint32_t)0x00000007)` | prg (programming) |
| `SD_CARD_DISCONNECTED` | `((uint32_t)0x00000008)` | dis (disconnected) |
| `SD_CARD_ERROR` | `((uint32_t)0x000000FF)` | Error (not a card state). |

### _sd_ocr_flag { #_sd_ocr_flag }

OCR register in SD card.

| Name | Value | Description |
|---|---|---|
| `SD_OcrHostCapacitySupportFlag` | `(1U << 30U)` | HCS (ACMD41 argument) / CCS (response): high capacity. |
| `SD_OcrCardCapacitySupportFlag` | `SD_OcrHostCapacitySupportFlag` | Card capacity status (CCS). |
| `SD_OcrSwitch18RequestFlag` | `(1U << 24U)` | Switch to 1.8V request. |
| `SD_OcrSwitch18AcceptFlag` | `SD_OcrSwitch18RequestFlag` | Switch to 1.8V accepted. |
| `SD_OcrVdd27_28Flag` | `(1U << 15U)` | VDD 2.7-2.8. |
| `SD_OcrVdd28_29Flag` | `(1U << 16U)` | VDD 2.8-2.9. |
| `SD_OcrVdd29_30Flag` | `(1U << 17U)` | VDD 2.9-3.0. |
| `SD_OcrVdd30_31Flag` | `(1U << 18U)` | VDD 3.0-3.1. |
| `SD_OcrVdd31_32Flag` | `(1U << 19U)` | VDD 3.1-3.2. |
| `SD_OcrVdd32_33Flag` | `(1U << 20U)` | VDD 3.2-3.3. |
| `SD_OcrVdd33_34Flag` | `(1U << 21U)` | VDD 3.3-3.4. |
| `SD_OcrVdd34_35Flag` | `(1U << 22U)` | VDD 3.4-3.5. |
| `SD_OcrVdd35_36Flag` | `(1U << 23U)` | VDD 3.5-3.6. |

### _sd_card_flag { #_sd_card_flag }

SD card flags, stored in `sd_card_t::flags`.

| Name | Value | Description |
|---|---|---|
| `SD_SupportHighCapacityFlag` | `(1U << 1U)` | Card reported CCS = 1 (SDHC/SDXC). |
| `SD_Support4BitWidthFlag` | `(1U << 2U)` | Support 4-bit data width. |
| `SD_SupportSdhcFlag` | `(1U << 3U)` | Card answered CMD8 (Physical Layer v2.00 or later). |
| `SD_SupportSdxcFlag` | `(1U << 4U)` | Capacity in the SDXC range (CSD v2.0 C_SIZE &gt;= 0xFFFF). |
| `SD_SupportVoltage180v` | `(1U << 5U)` | Set for eMMC devices; the driver itself stays at 3.3 V signalling. |
| `SD_SupportSetBlockCountCmd` | `(1U << 6U)` | Card supports CMD23 (SET_BLOCK_COUNT). |
| `SD_SupportSpeedClassControlCmd` | `(1U << 7U)` | Card supports CMD20 (speed class control). |

### _sd_card_type { #_sd_card_type }

Card type, stored in `sd_card_t::type`.

| Name | Value | Description |
|---|---|---|
| `SD_TYPE_SDC` | `1` | SD memory card. |
| `SD_TYPE_EMMC` | `2` | eMMC device. |

### _sd_scr_flag { #_sd_scr_flag }

SD card SCR register flags.

| Name | Value | Description |
|---|---|---|
| `SD_ScrDataStatusAfterErase` | `(1U << 0U)` | Data status after erases [55:55]. |
| `SD_ScrSdSpecification3` | `(1U << 1U)` | Specification version 3.00 or higher [47:47]. |

### sd_group_num { #sd_group_num }

SD CMD6 (SWITCH_FUNC) function group, numbered from 0.

| Name | Value | Description |
|---|---|---|
| `SDH_GroupTimingMode` | `0U` | Function group 1: access mode (bus speed). |
| `SDH_GroupCommandSystem` | `1U` | Function group 2: command system. |
| `SDH_GroupDriverStrength` | `2U` | Function group 3: driver strength. |
| `SDH_GroupCurrentLimit` | `3U` | Function group 4: current limit. |

### sd_timing_mode_t { #sd_timing_mode_t }

SD card timing mode flags.

| Name | Value | Description |
|---|---|---|
| `SDH_TimingSDR12DefaultMode` | `0U` | Identification mode & SDR12. |
| `SDH_TimingSDR25HighSpeedMode` | `1U` | High speed mode & SDR25. |
| `SDH_TimingSDR50Mode` | `2U` | SDR50 mode. |
| `SDH_TimingSDR104Mode` | `3U` | SDR104 mode. |
| `SDH_TimingDDR50Mode` | `4U` | DDR50 mode. |

### _sd_specification_version { #_sd_specification_version }

SD card specification version number, stored in `sd_card_t::version`.

| Name | Value | Description |
|---|---|---|
| `SD_SpecificationVersion1_0` | `(1U << 0U)` | SD card version 1.0-1.01. |
| `SD_SpecificationVersion1_1` | `(1U << 1U)` | SD card version 1.10. |
| `SD_SpecificationVersion2_0` | `(1U << 2U)` | SD card version 2.00. |
| `SD_SpecificationVersion3_0` | `(1U << 3U)` | SD card version 3.0. |

### sd_switch_mode_t { #sd_switch_mode_t }

SD card switch mode.

| Name | Value | Description |
|---|---|---|
| `SDH_SwitchCheck` | `0U` | SD switch mode 0: check function. |
| `SDH_SwitchSet` | `1U` | SD switch mode 1: set function. |

### mmc_switch_mode_t { #mmc_switch_mode_t }

Access mode of the MMC CMD6 (SWITCH) argument, bits [25:24].

| Name | Value | Description |
|---|---|---|
| `MMC_SWITCH_MODE_CMD_SET` | `0x0` | Change the command set. |
| `MMC_SWITCH_MODE_SET_BITS` | `0x1` | Set the bits given in the value byte. |
| `MMC_SWITCH_MODE_CLEAR_BITS` | `0x2` | Clear the bits given in the value byte. |
| `MMC_SWITCH_MODE_WRITE_BYTE` | `0x3` | Write the value byte. |

### SD_CSD { #SD_CSD }

Card Specific Data: CSD register, field-per-member layout.

Not filled by this driver; the decoded CSD is in [`sd_csd_t`](#sd_csd_t).

| Field | Type | Description |
|---|---|---|
| `CSDStruct` | `uint8_t` | CSD structure. |
| `SysSpecVersion` | `uint8_t` | System specification version. |
| `Reserved1` | `uint8_t` | Reserved. |
| `TAAC` | `uint8_t` | Data read access-time 1. |
| `NSAC` | `uint8_t` | Data read access-time 2 in CLK cycles. |
| `MaxBusClkFrec` | `uint8_t` | Maximum bus clock frequency. |
| `CardComdClasses` | `uint16_t` | Card command classes. |
| `RdBlockLen` | `uint8_t` | Maximum read data block length. |
| `PartBlockRead` | `uint8_t` | Partial blocks for read allowed. |
| `WrBlockMisalign` | `uint8_t` | Write block misalignment. |
| `RdBlockMisalign` | `uint8_t` | Read block misalignment. |
| `DSRImpl` | `uint8_t` | DSR implemented. |
| `Reserved2` | `uint8_t` | Reserved. |
| `DeviceSize` | `uint32_t` | Device Size. |
| `MaxRdCurrentVDDMin` | `uint8_t` | Maximum read current at VDD min. |
| `MaxRdCurrentVDDMax` | `uint8_t` | Maximum read current at VDD max. |
| `MaxWrCurrentVDDMin` | `uint8_t` | Maximum write current at VDD min. |
| `MaxWrCurrentVDDMax` | `uint8_t` | Maximum write current at VDD max. |
| `DeviceSizeMul` | `uint8_t` | Device size multiplier. |
| `EraseGrSize` | `uint8_t` | Erase group size. |
| `EraseGrMul` | `uint8_t` | Erase group size multiplier. |
| `WrProtectGrSize` | `uint8_t` | Write protect group size. |
| `WrProtectGrEnable` | `uint8_t` | Write protect group enable. |
| `ManDeflECC` | `uint8_t` | Manufacturer default ECC. |
| `WrSpeedFact` | `uint8_t` | Write speed factor. |
| `MaxWrBlockLen` | `uint8_t` | Maximum write data block length. |
| `WriteBlockPaPartial` | `uint8_t` | Partial blocks for write allowed. |
| `Reserved3` | `uint8_t` | Reserved. |
| `ContentProtectAppli` | `uint8_t` | Content protection application. |
| `FileFormatGrouop` | `uint8_t` | File format group. |
| `CopyFlag` | `uint8_t` | Copy flag (OTP). |
| `PermWrProtect` | `uint8_t` | Permanent write protection. |
| `TempWrProtect` | `uint8_t` | Temporary write protection. |
| `FileFormat` | `uint8_t` | File Format. |
| `ECC` | `uint8_t` | ECC code. |

### SD_CID { #SD_CID }

Card Identification Data: CID register, field-per-member layout.

Not filled by this driver; the decoded CID is in [`sd_cid_t`](#sd_cid_t).

| Field | Type | Description |
|---|---|---|
| `ManufacturerID` | `uint8_t` | Manufacturer ID. |
| `OEM_AppliID` | `uint8_t[3]` | OEM/application ID, NUL-terminated for printing. |
| `ProdName` | `uint8_t[6]` | Product name, NUL-terminated for printing. |
| `ProdRev` | `uint8_t` | Product Revision. |
| `ProdSN` | `uint32_t` | Product Serial Number. |
| `month` | `uint8_t` | Manufacturing month. |
| `year` | `uint32_t` | Manufacturing year. |

### SD_CardStatus { #SD_CardStatus }

SD Status register (ACMD13), field-per-member layout.

Not filled by this driver; see [`sd_ssr_t`](#sd_ssr_t) and `sd_card_t::rawSsr`.

| Field | Type | Description |
|---|---|---|
| `DAT_BUS_WIDTH` | `uint8_t` | DAT_BUS_WIDTH: current bus width. |
| `SECURED_MODE` | `uint8_t` | SECURED_MODE: card is in secured mode. |
| `SD_CARD_TYPE` | `uint16_t` | SD_CARD_TYPE. |
| `SIZE_OF_PROTECTED_AREA` | `uint32_t` | SIZE_OF_PROTECTED_AREA. |
| `SPEED_CLASS` | `uint8_t` | SPEED_CLASS. |
| `PERFORMANCE_MOVE` | `uint8_t` | PERFORMANCE_MOVE. |
| `AU_SIZE` | `uint8_t` | AU_SIZE: allocation unit size code. |
| `ERASE_SIZE` | `uint16_t` | ERASE_SIZE: number of AUs erased at a time. |
| `ERASE_TIMEOUT` | `uint8_t` | ERASE_TIMEOUT. |
| `ERASE_OFFSET` | `uint8_t` | ERASE_OFFSET. |

### sd_cid_t { #sd_cid_t }

SD card CID register.

| Field | Type | Description |
|---|---|---|
| `manufacturerID` | `uint8_t` | Manufacturer ID [127:120]. |
| `applicationID` | `uint16_t` | OEM/Application ID [119:104]. |
| `productName` | `uint8_t[5]` | Product name [103:64]. |
| `productVersion` | `uint8_t` | Product revision [63:56]. |
| `productSerialNumber` | `uint32_t` | Product serial number [55:24]. |
| `manufacturerData` | `uint16_t` | Manufacturing date [19:8]. |

### sd_csd_t { #sd_csd_t }

SD card CSD register.

[`SDH_Init()`](#SDH_Init) decodes csdStructure, dataReadAccessTime1, dataReadAccessTime2, transferSpeed, cardCommandClass, readBlockLength, deviceSize and (CSD v1.0 only) deviceSizeMultiplier. The other members are not written by the driver.

| Field | Type | Description |
|---|---|---|
| `csdStructure` | `uint8_t` | CSD structure [127:126]. |
| `dataReadAccessTime1` | `uint8_t` | Data read access-time-1 [119:112]. |
| `dataReadAccessTime2` | `uint8_t` | Data read access-time-2 in clock cycles (NSAC*100) [111:104]. |
| `transferSpeed` | `uint8_t` | Maximum data transfer rate [103:96]. |
| `cardCommandClass` | `uint16_t` | Card command classes [95:84]. |
| `readBlockLength` | `uint8_t` | Maximum read data block length [83:80]. |
| `flags` | `uint16_t` | CSD flag bits (not decoded by this driver). |
| `deviceSize` | `uint32_t` | Device size C_SIZE: [73:62] for CSD v1.0, [69:48] for CSD v2.0. |
| `readCurrentVddMin` | `uint8_t` | Maximum read current at VDD min [61:59]. |
| `readCurrentVddMax` | `uint8_t` | Maximum read current at VDD max [58:56]. |
| `writeCurrentVddMin` | `uint8_t` | Maximum write current at VDD min [55:53]. |
| `writeCurrentVddMax` | `uint8_t` | Maximum write current at VDD max [52:50]. |
| `deviceSizeMultiplier` | `uint8_t` | Device size multiplier [49:47]. |
| `eraseSectorSize` | `uint8_t` | Erase sector size [45:39]. |
| `writeProtectGroupSize` | `uint8_t` | Write protect group size [38:32]. |
| `writeSpeedFactor` | `uint8_t` | Write speed factor [28:26]. |
| `writeBlockLength` | `uint8_t` | Maximum write data block length [25:22]. |
| `fileFormat` | `uint8_t` | File format [11:10]. |

### mmc_ext_csd_t { #mmc_ext_csd_t }

Raw 512-byte EXT_CSD register of an eMMC device.

Read with CMD8 (SEND_EXT_CSD) during [`SDH_Init()`](#SDH_Init) and again after [`MMC_SwitchPartition()`](#MMC_SwitchPartition). Each member is the EXT_CSD byte at the given offset; the ranges named `reserved_*` are bytes the driver does not decode.

| Field | Type | Description |
|---|---|---|
| `reserved_0_165` | `uint8_t[166]` | Bytes 0-165. |
| `rel_param` | `uint8_t` | Byte 166: WR_REL_PARAM. |
| `rel_set` | `uint8_t` | Byte 167: WR_REL_SET. |
| `reserved_168_176` | `uint8_t[9]` | Bytes 168-176. |
| `bootbusContions` | `uint8_t` | Byte 177: BOOT_BUS_CONDITIONS. |
| `reserved_178` | `uint8_t` | Byte 178. |
| `partConfig` | `uint8_t` | Byte 179: PARTITION_CONFIG. |
| `reserved_180_182` | `uint8_t[3]` | Bytes 180-182. |
| `busWidth` | `uint8_t` | Byte 183: BUS_WIDTH. |
| `reserved_184` | `uint8_t` | Byte 184. |
| `hsTiming` | `uint8_t` | Byte 185: HS_TIMING. |
| `reserved_186` | `uint8_t` | Byte 186. |
| `powerClass` | `uint8_t` | Byte 187: POWER_CLASS. |
| `reserved_188_191` | `uint8_t[4]` | Bytes 188-191. |
| `csdRev` | `uint8_t` | Byte 192: EXT_CSD_REV. |
| `reserved_193` | `uint8_t` | Byte 193. |
| `csdStructure` | `uint8_t` | Byte 194: CSD_STRUCTURE. |
| `reserved_195` | `uint8_t` | Byte 195. |
| `cardType` | `uint8_t` | Byte 196: DEVICE_TYPE (EXT_CSD_CARD_TYPE_* bits). |
| `reserved_197_199` | `uint8_t[3]` | Bytes 197-199. |
| `powerClass_52_195` | `uint8_t` | Byte 200: PWR_CL_52_195. |
| `powerClass_26_195` | `uint8_t` | Byte 201: PWR_CL_26_195. |
| `powerClass_52_360` | `uint8_t` | Byte 202: PWR_CL_52_360. |
| `powerClass_26_360` | `uint8_t` | Byte 203: PWR_CL_26_360. |
| `reserved_204_221` | `uint8_t[18]` | Bytes 204-221. |
| `rel_wr_sec_count` | `uint8_t` | Byte 222: REL_WR_SEC_C. |
| `reserved_223_225` | `uint8_t[3]` | Bytes 223-225. |
| `bootMultSize` | `uint8_t` | Byte 226: BOOT_SIZE_MULT (boot partition size in 128 KB units). |
| `reserved_227_511` | `uint8_t[285]` | Bytes 227-511. |

### sd_scr_t { #sd_scr_t }

SD card SCR register.

| Field | Type | Description |
|---|---|---|
| `scrStructure` | `uint8_t` | SCR Structure [63:60]. |
| `sdSpecification` | `uint8_t` | SD memory card specification version [59:56]. |
| `flags` | `uint16_t` | SCR flags in [`_sd_scr_flag`](#_sd_scr_flag). |
| `sdSecurity` | `uint8_t` | Security specification supported [54:52]. |
| `sdBusWidths` | `uint8_t` | Data bus widths supported [51:48]. |
| `extendedSecurity` | `uint8_t` | Extended security support [46:43]. |
| `commandSupport` | `uint8_t` | Command support bits [33:32]: bit 1 = CMD23, bit 0 = CMD20. |
| `reservedForManufacturer` | `uint32_t` | reserved for manufacturer usage [31:0] |

### sd_ssr_t { #sd_ssr_t }

SD Status register.

Not decoded by this driver; the raw SD Status block read by [`SDH_Init()`](#SDH_Init) is in `sd_card_t::rawSsr`.

| Field | Type | Description |
|---|---|---|
| `dataBusWidth` | `uint8_t` | Data Bus Width [511:510]: 0b00 = 1 line, 0b10 = 4 lines. |
| `secureMode` | `uint8_t` | Secure Mode [509]. |
| `SDCardType` | `uint16_t` | SD Card Type [495:480]. |
| `sizeOfProtectedArea` | `uint32_t` | Size Of Protected area [479:448]. |
| `speedClass` | `uint8_t` | speed classes [447:440] |
| `performanceMove` | `uint8_t` | performance move [439:432] |
| `AUSize` | `uint8_t` | AU size [431:428]. |
| `eraseSize` | `uint16_t` | erase size [423:408] |
| `eraseTimeOut` | `uint8_t` | erase timeout [407:402] |
| `eraseOffset` | `uint8_t` | erase offset [401:400] |
| `UHSSpeedGrade` | `uint8_t` | UHS speed grade [399:396]. |
| `UHSAUSize` | `uint8_t` | UHS AU size [395:392]. |

### sd_card_t { #sd_card_t }

SD card state.

Define the card structure including the necessary fields to identify and describe the card. Allocated by the caller and filled in by [`SDH_Init()`](#SDH_Init); the driver keeps a pointer to it for the later calls on the same controller.

| Field | Type | Description |
|---|---|---|
| `@016354276207311361052046056025003270263366240027` | `union sd_card_t::@104027144201072367342116331173017256363227263240` |  |
| `relativeAddress` | `uint32_t` | Relative address of the card. |
| `version` | `uint32_t` | SD specification version ([`_sd_specification_version`](#_sd_specification_version)), SD cards only. |
| `flags` | `uint32_t` | Flags in [`_sd_card_flag`](#_sd_card_flag). |
| `rawCid` | `uint32_t[4U]` | Raw CID response: CID bits [127:8], least significant word first. |
| `rawCsd` | `uint32_t[4U]` | Raw CSD response: CSD bits [127:8], least significant word first. |
| `rawScr` | `uint32_t[2U]` | Raw SCR: rawScr[1] = bits [63:32], rawScr[0] = bits [31:0]. |
| `rawSsr` | `uint32_t[16U]` | Raw 64-byte SD Status block (ACMD13), SD cards only. |
| `ocr` | `uint32_t` | Raw OCR from the ACMD41 (SD) or CMD1 (eMMC) response. |
| `cid` | `sd_cid_t` | CID decoded from rawCid. |
| `scr` | `sd_scr_t` | SCR decoded from rawScr (SD cards only). |
| `ssr` | `sd_ssr_t` | SD Status (not decoded, see [`sd_ssr_t`](#sd_ssr_t)). |
| `blockCount` | `uint32_t` | Card total block number, computed from the CSD. |
| `blockSize` | `uint32_t` | Card block size in bytes (512). |
| `type` | `uint8_t` | Card type: SD_TYPE_SDC (1) or SD_TYPE_EMMC (2). |
| `access_mode` | `uint8_t` | 0: byte addressing (SDSC), 1: block (sector) addressing |
| `rel_wr` | `uint8_t` | Reliable write requested with [`EMMC_SetRelWR()`](#EMMC_SetRelWR): 0 off, 1 on. |

### Typedefs { #hal_sdh-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `status_t` | `typedef int32_t status_t` | Type used for all status and error return values. |

### Macros { #hal_sdh-h-macros }

| Name | Value | Description |
|---|---|---|
| `SD_CMD_GO_IDLE_STATE` | `((uint8_t)0)` | CMD0 GO_IDLE_STATE. |
| `SD_CMD_SEND_OP_COND` | `((uint8_t)1)` | CMD1 SEND_OP_COND (MMC). |
| `SD_CMD_ALL_SEND_CID` | `((uint8_t)2)` | CMD2 ALL_SEND_CID. |
| `SD_CMD_SET_REL_ADDR` | `((uint8_t)3)` | CMD3: SEND_RELATIVE_ADDR (SD) / SET_RELATIVE_ADDR (MMC). |
| `SD_CMD_SET_DSR` | `((uint8_t)4)` | CMD4 SET_DSR. |
| `SD_CMD_SDIO_SEN_OP_COND` | `((uint8_t)5)` | CMD5 IO_SEND_OP_COND (SDIO). |
| `SD_CMD_HS_SWITCH` | `((uint8_t)6)` | CMD6 SWITCH_FUNC (SD) / SWITCH (MMC). |
| `SD_CMD_SEL_DESEL_CARD` | `((uint8_t)7)` | CMD7 SELECT/DESELECT_CARD. |
| `SD_CMD_HS_SEND_EXT_CSD` | `((uint8_t)8)` | CMD8 SEND_EXT_CSD (MMC). |
| `SDIO_SEND_IF_COND` | `((uint8_t)8)` | CMD8 SEND_IF_COND (SD). |
| `SD_CMD_SEND_CSD` | `((uint8_t)9)` | CMD9 SEND_CSD. |
| `SD_CMD_SEND_CID` | `((uint8_t)10)` | CMD10 SEND_CID. |
| `SD_CMD_READ_DAT_UNTIL_STOP` | `((uint8_t)11)` | CMD11 READ_DAT_UNTIL_STOP (MMC); SD Card doesn't support it. |
| `SD_CMD_STOP_TRANSMISSION` | `((uint8_t)12)` | CMD12 STOP_TRANSMISSION. |
| `SD_CMD_SEND_STATUS` | `((uint8_t)13)` | CMD13 SEND_STATUS. |
| `SD_CMD_HS_BUSTEST_READ` | `((uint8_t)14)` | CMD14 BUSTEST_R (MMC). |
| `SD_CMD_GO_INACTIVE_STATE` | `((uint8_t)15)` | CMD15 GO_INACTIVE_STATE. |
| `SD_CMD_SET_BLOCKLEN` | `((uint8_t)16)` | CMD16 SET_BLOCKLEN. |
| `SD_CMD_READ_SINGLE_BLOCK` | `((uint8_t)17)` | CMD17 READ_SINGLE_BLOCK. |
| `SD_CMD_READ_MULT_BLOCK` | `((uint8_t)18)` | CMD18 READ_MULTIPLE_BLOCK. |
| `SD_CMD_HS_BUSTEST_WRITE` | `((uint8_t)19)` | CMD19 BUSTEST_W (MMC). |
| `SD_CMD_WRITE_DAT_UNTIL_STOP` | `((uint8_t)20)` | CMD20 WRITE_DAT_UNTIL_STOP (MMC); on SD cards CMD20 is SPEED_CLASS_CONTROL. |
| `SD_CMD_SET_BLOCK_COUNT` | `((uint8_t)23)` | CMD23 SET_BLOCK_COUNT; optional on SD cards (see SD_SupportSetBlockCountCmd). |
| `SD_CMD_WRITE_SINGLE_BLOCK` | `((uint8_t)24)` | CMD24 WRITE_BLOCK. |
| `SD_CMD_WRITE_MULT_BLOCK` | `((uint8_t)25)` | CMD25 WRITE_MULTIPLE_BLOCK. |
| `SD_CMD_PROG_CID` | `((uint8_t)26)` | CMD26 PROGRAM_CID; reserved for manufacturers. |
| `SD_CMD_PROG_CSD` | `((uint8_t)27)` | CMD27 PROGRAM_CSD. |
| `SD_CMD_SET_WRITE_PROT` | `((uint8_t)28)` | CMD28 SET_WRITE_PROT. |
| `SD_CMD_CLR_WRITE_PROT` | `((uint8_t)29)` | CMD29 CLR_WRITE_PROT. |
| `SD_CMD_SEND_WRITE_PROT` | `((uint8_t)30)` | CMD30 SEND_WRITE_PROT. |
| `SD_CMD_SD_ERASE_GRP_START` | `((uint8_t)32)` | CMD32 ERASE_WR_BLK_START: set the address of the first write block to be erased (SD cards only). |
| `SD_CMD_SD_ERASE_GRP_END` | `((uint8_t)33)` | CMD33 ERASE_WR_BLK_END: set the address of the last write block of the range to be erased (SD cards only). |
| `SD_CMD_ERASE_GRP_START` | `((uint8_t)35)` | CMD35 ERASE_GROUP_START: set the address of the first erase group (MMC only, spec 3.31). |
| `SD_CMD_ERASE_GRP_END` | `((uint8_t)36)` | CMD36 ERASE_GROUP_END: set the address of the last erase group of the range (MMC only, spec 3.31). |
| `SD_CMD_ERASE` | `((uint8_t)38)` | CMD38 ERASE. |
| `SD_CMD_FAST_IO` | `((uint8_t)39)` | CMD39 FAST_IO (MMC); SD Card doesn't support it. |
| `SD_CMD_GO_IRQ_STATE` | `((uint8_t)40)` | CMD40 GO_IRQ_STATE (MMC); SD Card doesn't support it. |
| `SD_CMD_LOCK_UNLOCK` | `((uint8_t)42)` | CMD42 LOCK_UNLOCK. |
| `SD_CMD_APP_CMD` | `((uint8_t)55)` | CMD55 APP_CMD: next command is an application command. |
| `SD_CMD_GEN_CMD` | `((uint8_t)56)` | CMD56 GEN_CMD. |
| `SD_CMD_NO_CMD` | `((uint8_t)64)` | Not a valid command index (marks "no command"). |
| `SD_CMD_APP_SD_SET_BUSWIDTH` | `((uint8_t)6)` | ACMD6 SET_BUS_WIDTH; for SD Card only. |
| `SD_CMD_SD_APP_STAUS` | `((uint8_t)13)` | ACMD13 SD_STATUS; for SD Card only. |
| `SD_CMD_SD_APP_SEND_NUM_WRITE_BLOCKS` | `((uint8_t)22)` | ACMD22 SEND_NUM_WR_BLOCKS; for SD Card only. |
| `SD_CMD_SD_APP_OP_COND` | `((uint8_t)41)` | ACMD41 SD_SEND_OP_COND; for SD Card only. |
| `SD_CMD_SD_APP_SET_CLR_CARD_DETECT` | `((uint8_t)42)` | ACMD42 SET_CLR_CARD_DETECT; for SD Card only. |
| `SD_CMD_SD_APP_SEND_SCR` | `((uint8_t)51)` | ACMD51 SEND_SCR; for SD Card only. |
| `SD_CMD_SDIO_RW_DIRECT` | `((uint8_t)52)` | CMD52 IO_RW_DIRECT; for SD I/O Card only. |
| `SD_CMD_SDIO_RW_EXTENDED` | `((uint8_t)53)` | CMD53 IO_RW_EXTENDED; for SD I/O Card only. |
| `SD_CMD_SD_APP_GET_MKB` | `((uint8_t)43)` | ACMD43 GET_MKB; for SD Card only. |
| `SD_CMD_SD_APP_GET_MID` | `((uint8_t)44)` | ACMD44 GET_MID; for SD Card only. |
| `SD_CMD_SD_APP_SET_CER_RN1` | `((uint8_t)45)` | ACMD45 SET_CER_RN1; for SD Card only. |
| `SD_CMD_SD_APP_GET_CER_RN2` | `((uint8_t)46)` | ACMD46 GET_CER_RN2; for SD Card only. |
| `SD_CMD_SD_APP_SET_CER_RES2` | `((uint8_t)47)` | ACMD47 SET_CER_RES2; for SD Card only. |
| `SD_CMD_SD_APP_GET_CER_RES1` | `((uint8_t)48)` | ACMD48 GET_CER_RES1; for SD Card only. |
| `SD_CMD_SD_APP_SECURE_READ_MULTIPLE_BLOCK` | `((uint8_t)18)` | ACMD18 SECURE_READ_MULTI_BLOCK; for SD Card only. |
| `SD_CMD_SD_APP_SECURE_WRITE_MULTIPLE_BLOCK` | `((uint8_t)25)` | ACMD25 SECURE_WRITE_MULTI_BLOCK; for SD Card only. |
| `SD_CMD_SD_APP_SECURE_ERASE` | `((uint8_t)38)` | ACMD38 SECURE_ERASE; for SD Card only. |
| `SD_CMD_SD_APP_CHANGE_SECURE_AREA` | `((uint8_t)49)` | ACMD49 CHANGE_SECURE_AREA; for SD Card only. |
| `SD_CMD_SD_APP_SECURE_WRITE_MKB` | `((uint8_t)48)` | ACMD48 SECURE_WRITE_MKB; for SD Card only. |
| `SD_CSR_ADDR_OUT_OF_RANGE` | `((uint32_t)0x80000000)` | Bit 31 OUT_OF_RANGE. |
| `SD_CSR_ADDR_MISALIGNED` | `((uint32_t)0x40000000)` | Bit 30 ADDRESS_ERROR (misaligned address). |
| `SD_CSR_BLOCK_LEN_ERR` | `((uint32_t)0x20000000)` | Bit 29 BLOCK_LEN_ERROR. |
| `SD_CSR_ERASE_SEQ_ERR` | `((uint32_t)0x10000000)` | Bit 28 ERASE_SEQ_ERROR. |
| `SD_CSR_BAD_ERASE_PARAM` | `((uint32_t)0x08000000)` | Bit 27 ERASE_PARAM. |
| `SD_CSR_WRITE_PROT_VIOLATION` | `((uint32_t)0x04000000)` | Bit 26 WP_VIOLATION. |
| `SD_CSR_LOCK_UNLOCK_FAILED` | `((uint32_t)0x01000000)` | Bit 24 LOCK_UNLOCK_FAILED. |
| `SD_CSR_COM_CRC_FAILED` | `((uint32_t)0x00800000)` | Bit 23 COM_CRC_ERROR. |
| `SD_CSR_ILLEGAL_CMD` | `((uint32_t)0x00400000)` | Bit 22 ILLEGAL_COMMAND. |
| `SD_CSR_CARD_ECC_FAILED` | `((uint32_t)0x00200000)` | Bit 21 CARD_ECC_FAILED. |
| `SD_CSR_CC_ERROR` | `((uint32_t)0x00100000)` | Bit 20 CC_ERROR (internal controller error). |
| `SD_CSR_GENERAL_UNKNOWN_ERROR` | `((uint32_t)0x00080000)` | Bit 19 ERROR (general or unknown error). |
| `SD_CSR_STREAM_READ_UNDERRUN` | `((uint32_t)0x00040000)` | Bit 18 STREAM_READ_UNDERRUN (MMC). |
| `SD_CSR_STREAM_WRITE_OVERRUN` | `((uint32_t)0x00020000)` | Bit 17 STREAM_WRITE_OVERRUN (MMC). |
| `SD_CSR_CID_CSD_OVERWRIETE` | `((uint32_t)0x00010000)` | Bit 16 CID/CSD_OVERWRITE. |
| `SD_CSR_WP_ERASE_SKIP` | `((uint32_t)0x00008000)` | Bit 15 WP_ERASE_SKIP. |
| `SD_CSR_CARD_ECC_DISABLED` | `((uint32_t)0x00004000)` | Bit 14 CARD_ECC_DISABLED. |
| `SD_CSR_ERASE_RESET` | `((uint32_t)0x00002000)` | Bit 13 ERASE_RESET. |
| `SD_CSR_AKE_SEQ_ERROR` | `((uint32_t)0x00000008)` | Bit 3 AKE_SEQ_ERROR. |
| `SD_CSR_ERRORBITS` | `((uint32_t)0xFDFFE008)` | All error bits above. The driver fails a command whose R1 response has any of them set ([`Status_SDH_CmdResponseError`](#_sdmmc_status)). |
| `SD_MAX_VOLT_TRIAL` | `((uint32_t)0x0000FFFF)` | Maximum ACMD41 attempts while waiting for card power-up. |
| `SD_ALLZERO` | `((uint32_t)0x00000000)` | All-zero word. |
| `SD_WIDE_BUS_SUPPORT` | `((uint32_t)0x00040000)` | SD_BUS_WIDTHS 4-bit support bit, within SCR bits [63:32]. |
| `SD_SINGLE_BUS_SUPPORT` | `((uint32_t)0x00010000)` | SD_BUS_WIDTHS 1-bit support bit, within SCR bits [63:32]. |
| `SD_CARD_LOCKED` | `((uint32_t)0x02000000)` | R1 bit 25 CARD_IS_LOCKED. |
| `SD_0TO7BITS` | `((uint32_t)0x000000FF)` | Mask of bits 0-7 of a word. |
| `SD_8TO15BITS` | `((uint32_t)0x0000FF00)` | Mask of bits 8-15 of a word. |
| `SD_16TO23BITS` | `((uint32_t)0x00FF0000)` | Mask of bits 16-23 of a word. |
| `SD_24TO31BITS` | `((uint32_t)0xFF000000)` | Mask of bits 24-31 of a word. |
| `SD_MAX_DATA_LENGTH` | `((uint32_t)0x01FFFFFF)` | Largest data length value, in bytes (not used by this driver). |
| `SD_VOLTAGE_WINDOW_SD` | `((uint32_t)0x00100000)` | OCR voltage-window bit 20 (3.2-3.3 V). |
| `SD_HIGH_CAPACITY` | `((uint32_t)0x40000000)` | HCS bit (bit 30) of the ACMD41 argument. |
| `SD_STD_CAPACITY` | `((uint32_t)0x00000000)` | ACMD41 argument without HCS (standard capacity). |
| `SD_CHECK_PATTERN` | `((uint32_t)0x000001AA)` | CMD8 argument: 2.7-3.6 V supply (VHS = 1) and check pattern 0xAA, echoed back by the card in R7. |
| `SDIO_STD_CAPACITY_SD_CARD_V1_1` | `((uint32_t)0x00000000)` | Standard-capacity SD card, v1.1. |
| `SDIO_STD_CAPACITY_SD_CARD_V2_0` | `((uint32_t)0x00000001)` | Standard-capacity SD card, v2.0. |
| `SDIO_HIGH_CAPACITY_SD_CARD` | `((uint32_t)0x00000002)` | High-capacity SD card. |
| `SDIO_MULTIMEDIA_CARD` | `((uint32_t)0x00000003)` | MultiMediaCard. |
| `SDIO_SECURE_DIGITAL_IO_CARD` | `((uint32_t)0x00000004)` | SDIO card. |
| `SDIO_HIGH_SPEED_MULTIMEDIA_CARD` | `((uint32_t)0x00000005)` | High-speed MultiMediaCard. |
| `SDIO_SECURE_DIGITAL_IO_COMBO_CARD` | `((uint32_t)0x00000006)` | SDIO combo card (I/O and memory). |
| `SDIO_HIGH_CAPACITY_MMC_CARD` | `((uint32_t)0x00000007)` | High-capacity MMC. |
| `MMC_GO_IDLE_STATE` | `0` | CMD0: bc. |
| `MMC_SEND_OP_COND` | `1` | CMD1: bcr, [31:0] OCR, R3. |
| `MMC_ALL_SEND_CID` | `2` | CMD2: bcr, R2. |
| `MMC_SET_RELATIVE_ADDR` | `3` | CMD3: ac, [31:16] RCA, R1. |
| `MMC_SET_DSR` | `4` | CMD4: bc, [31:16] RCA. |
| `MMC_SLEEP_AWAKE` | `5` | CMD5: ac, [31:16] RCA, [15] flag, R1b. |
| `MMC_SWITCH` | `6` | CMD6: ac, [31:0] access/index/value/cmd set, R1b. |
| `MMC_SELECT_CARD` | `7` | CMD7: ac, [31:16] RCA, R1. |
| `MMC_SEND_EXT_CSD` | `8` | CMD8: adtc, R1. |
| `MMC_SEND_CSD` | `9` | CMD9: ac, [31:16] RCA, R2. |
| `MMC_SEND_CID` | `10` | CMD10: ac, [31:16] RCA, R2. |
| `MMC_READ_DAT_UNTIL_STOP` | `11` | CMD11: adtc, [31:0] data address, R1. |
| `MMC_STOP_TRANSMISSION` | `12` | CMD12: ac, R1b. |
| `MMC_SEND_STATUS` | `13` | CMD13: ac, [31:16] RCA, R1. |
| `MMC_BUS_TEST_R` | `14` | CMD14: adtc, R1. |
| `MMC_GO_INACTIVE_STATE` | `15` | CMD15: ac, [31:16] RCA. |
| `MMC_BUS_TEST_W` | `19` | CMD19: adtc, R1. |
| `MMC_SPI_READ_OCR` | `58` | CMD58 (SPI mode): spi_R3. |
| `MMC_SPI_CRC_ON_OFF` | `59` | CMD59 (SPI mode): [0:0] flag, spi_R1. |
| `MMC_SET_BLOCKLEN` | `16` | CMD16: ac, [31:0] block length, R1. |
| `MMC_READ_SINGLE_BLOCK` | `17` | CMD17: adtc, [31:0] data address, R1. |
| `MMC_READ_MULTIPLE_BLOCK` | `18` | CMD18: adtc, [31:0] data address, R1. |
| `MMC_SEND_TUNING_BLOCK` | `19` | CMD19 (tuning block): adtc, R1. |
| `MMC_SEND_TUNING_BLOCK_HS200` | `21` | CMD21 (HS200 tuning block): adtc, R1. |
| `MMC_WRITE_DAT_UNTIL_STOP` | `20` | CMD20: adtc, [31:0] data address, R1. |
| `MMC_SET_BLOCK_COUNT` | `23` | CMD23: adtc, [31:0] block count, R1. |
| `MMC_WRITE_BLOCK` | `24` | CMD24: adtc, [31:0] data address, R1. |
| `MMC_WRITE_MULTIPLE_BLOCK` | `25` | CMD25: adtc, R1. |
| `MMC_PROGRAM_CID` | `26` | CMD26: adtc, R1. |
| `MMC_PROGRAM_CSD` | `27` | CMD27: adtc, R1. |
| `MMC_SET_WRITE_PROT` | `28` | CMD28: ac, [31:0] data address, R1b. |
| `MMC_CLR_WRITE_PROT` | `29` | CMD29: ac, [31:0] data address, R1b. |
| `MMC_SEND_WRITE_PROT` | `30` | CMD30: adtc, [31:0] write-protect data address, R1. |
| `MMC_ERASE_GROUP_START` | `35` | CMD35: ac, [31:0] data address, R1. |
| `MMC_ERASE_GROUP_END` | `36` | CMD36: ac, [31:0] data address, R1. |
| `MMC_ERASE` | `38` | CMD38: ac, R1b. |
| `MMC_FAST_IO` | `39` | CMD39: ac, R4. |
| `MMC_GO_IRQ_STATE` | `40` | CMD40: bcr, R5. |
| `MMC_LOCK_UNLOCK` | `42` | CMD42: adtc, R1b. |
| `MMC_APP_CMD` | `55` | CMD55: ac, [31:16] RCA, R1. |
| `MMC_GEN_CMD` | `56` | CMD56: adtc, [0] RD/WR, R1. |
| `MMC_QUE_TASK_PARAMS` | `44` | CMD44: ac, [20:16] task ID, R1. |
| `MMC_QUE_TASK_ADDR` | `45` | CMD45: ac, [31:0] data address, R1. |
| `MMC_EXECUTE_READ_TASK` | `46` | CMD46: adtc, [20:16] task ID, R1. |
| `MMC_EXECUTE_WRITE_TASK` | `47` | CMD47: adtc, [20:16] task ID, R1. |
| `MMC_CMDQ_TASK_MGMT` | `48` | CMD48: ac, [20:16] task ID, R1b. |
| `EXT_CSD_CMDQ_MODE_EN` | `15` | CMDQ_MODE_EN (R/W). |
| `EXT_CSD_FLUSH_CACHE` | `32` | FLUSH_CACHE (W). |
| `EXT_CSD_CACHE_CTRL` | `33` | CACHE_CTRL (R/W). |
| `EXT_CSD_POWER_OFF_NOTIFICATION` | `34` | POWER_OFF_NOTIFICATION (R/W). |
| `EXT_CSD_PACKED_FAILURE_INDEX` | `35` | PACKED_FAILURE_INDEX (RO). |
| `EXT_CSD_PACKED_CMD_STATUS` | `36` | PACKED_COMMAND_STATUS (RO). |
| `EXT_CSD_EXP_EVENTS_STATUS` | `54` | EXCEPTION_EVENTS_STATUS (RO, 2 bytes). |
| `EXT_CSD_EXP_EVENTS_CTRL` | `56` | EXCEPTION_EVENTS_CTRL (R/W, 2 bytes). |
| `EXT_CSD_DATA_SECTOR_SIZE` | `61` | DATA_SECTOR_SIZE (R). |
| `EXT_CSD_GP_SIZE_MULT` | `143` | GP_SIZE_MULT (R/W). |
| `EXT_CSD_PARTITION_SETTING_COMPLETED` | `155` | PARTITION_SETTING_COMPLETED (R/W). |
| `EXT_CSD_PARTITION_ATTRIBUTE` | `156` | PARTITIONS_ATTRIBUTE (R/W). |
| `EXT_CSD_PARTITION_SUPPORT` | `160` | PARTITIONING_SUPPORT (RO). |
| `EXT_CSD_HPI_MGMT` | `161` | HPI_MGMT (R/W). |
| `EXT_CSD_RST_N_FUNCTION` | `162` | RST_n_FUNCTION (R/W). |
| `EXT_CSD_BKOPS_EN` | `163` | BKOPS_EN (R/W). |
| `EXT_CSD_BKOPS_START` | `164` | BKOPS_START (W). |
| `EXT_CSD_SANITIZE_START` | `165` | SANITIZE_START (W). |
| `EXT_CSD_WR_REL_PARAM` | `166` | WR_REL_PARAM (RO). |
| `EXT_CSD_RPMB_MULT` | `168` | RPMB_SIZE_MULT (RO). |
| `EXT_CSD_FW_CONFIG` | `169` | FW_CONFIG (R/W). |
| `EXT_CSD_BOOT_WP` | `173` | BOOT_WP (R/W). |
| `EXT_CSD_ERASE_GROUP_DEF` | `175` | ERASE_GROUP_DEF (R/W). |
| `EXT_CSD_BOOT_BUS_CONTIONS` | `177` | BOOT_BUS_CONDITIONS (R/W). |
| `EXT_CSD_PART_CONFIG` | `179` | PARTITION_CONFIG (R/W). |
| `EXT_CSD_ERASED_MEM_CONT` | `181` | ERASED_MEM_CONT (RO). |
| `EXT_CSD_BUS_WIDTH` | `183` | BUS_WIDTH (R/W). |
| `EXT_CSD_STROBE_SUPPORT` | `184` | STROBE_SUPPORT (RO). |
| `EXT_CSD_HS_TIMING` | `185` | HS_TIMING (R/W). |
| `EXT_CSD_POWER_CLASS` | `187` | POWER_CLASS (R/W). |
| `EXT_CSD_REV` | `192` | EXT_CSD_REV (RO). |
| `EXT_CSD_STRUCTURE` | `194` | CSD_STRUCTURE (RO). |
| `EXT_CSD_CARD_TYPE` | `196` | DEVICE_TYPE (RO). |
| `EXT_CSD_DRIVER_STRENGTH` | `197` | DRIVER_STRENGTH (RO). |
| `EXT_CSD_OUT_OF_INTERRUPT_TIME` | `198` | OUT_OF_INTERRUPT_TIME (RO). |
| `EXT_CSD_PART_SWITCH_TIME` | `199` | PARTITION_SWITCH_TIME (RO). |
| `EXT_CSD_PWR_CL_52_195` | `200` | PWR_CL_52_195 (RO). |
| `EXT_CSD_PWR_CL_26_195` | `201` | PWR_CL_26_195 (RO). |
| `EXT_CSD_PWR_CL_52_360` | `202` | PWR_CL_52_360 (RO). |
| `EXT_CSD_PWR_CL_26_360` | `203` | PWR_CL_26_360 (RO). |
| `EXT_CSD_SEC_CNT` | `212` | SEC_COUNT (RO, 4 bytes). |
| `EXT_CSD_S_A_TIMEOUT` | `217` | S_A_TIMEOUT (RO). |
| `EXT_CSD_REL_WR_SEC_C` | `222` | REL_WR_SEC_C (RO). |
| `EXT_CSD_HC_WP_GRP_SIZE` | `221` | HC_WP_GRP_SIZE (RO). |
| `EXT_CSD_ERASE_TIMEOUT_MULT` | `223` | ERASE_TIMEOUT_MULT (RO). |
| `EXT_CSD_HC_ERASE_GRP_SIZE` | `224` | HC_ERASE_GRP_SIZE (RO). |
| `EXT_CSD_BOOT_MULT` | `226` | BOOT_SIZE_MULT (RO). |
| `EXT_CSD_SEC_TRIM_MULT` | `229` | SEC_TRIM_MULT (RO). |
| `EXT_CSD_SEC_ERASE_MULT` | `230` | SEC_ERASE_MULT (RO). |
| `EXT_CSD_SEC_FEATURE_SUPPORT` | `231` | SEC_FEATURE_SUPPORT (RO). |
| `EXT_CSD_TRIM_MULT` | `232` | TRIM_MULT (RO). |
| `EXT_CSD_PWR_CL_200_195` | `236` | PWR_CL_200_195 (RO). |
| `EXT_CSD_PWR_CL_200_360` | `237` | PWR_CL_200_360 (RO). |
| `EXT_CSD_PWR_CL_DDR_52_195` | `238` | PWR_CL_DDR_52_195 (RO). |
| `EXT_CSD_PWR_CL_DDR_52_360` | `239` | PWR_CL_DDR_52_360 (RO). |
| `EXT_CSD_BKOPS_STATUS` | `246` | BKOPS_STATUS (RO). |
| `EXT_CSD_POWER_OFF_LONG_TIME` | `247` | POWER_OFF_LONG_TIME (RO). |
| `EXT_CSD_GENERIC_CMD6_TIME` | `248` | GENERIC_CMD6_TIME (RO). |
| `EXT_CSD_CACHE_SIZE` | `249` | CACHE_SIZE (RO, 4 bytes). |
| `EXT_CSD_PWR_CL_DDR_200_360` | `253` | PWR_CL_DDR_200_360 (RO). |
| `EXT_CSD_FIRMWARE_VERSION` | `254` | FIRMWARE_VERSION (RO, 8 bytes). |
| `EXT_CSD_PRE_EOL_INFO` | `267` | PRE_EOL_INFO (RO). |
| `EXT_CSD_DEVICE_LIFE_TIME_EST_TYP_A` | `268` | DEVICE_LIFE_TIME_EST_TYP_A (RO). |
| `EXT_CSD_DEVICE_LIFE_TIME_EST_TYP_B` | `269` | DEVICE_LIFE_TIME_EST_TYP_B (RO). |
| `EXT_CSD_CMDQ_DEPTH` | `307` | CMDQ_DEPTH (RO). |
| `EXT_CSD_CMDQ_SUPPORT` | `308` | CMDQ_SUPPORT (RO). |
| `EXT_CSD_SUPPORTED_MODE` | `493` | SUPPORTED_MODES (RO). |
| `EXT_CSD_TAG_UNIT_SIZE` | `498` | TAG_UNIT_SIZE (RO). |
| `EXT_CSD_DATA_TAG_SUPPORT` | `499` | DATA_TAG_SUPPORT (RO). |
| `EXT_CSD_MAX_PACKED_WRITES` | `500` | MAX_PACKED_WRITES (RO). |
| `EXT_CSD_MAX_PACKED_READS` | `501` | MAX_PACKED_READS (RO). |
| `EXT_CSD_BKOPS_SUPPORT` | `502` | BKOPS_SUPPORT (RO). |
| `EXT_CSD_HPI_FEATURES` | `503` | HPI_FEATURES (RO). |
| `EXT_CSD_WR_REL_PARAM_EN` | `(1<<2)` | WR_REL_PARAM EN_REL_WR: enhanced reliable write supported (checked when [`EMMC_SetRelWR()`](#EMMC_SetRelWR) is on). |
| `EXT_CSD_WR_REL_PARAM_EN_RPMB_REL_WR` | `(1<<4)` | WR_REL_PARAM EN_RPMB_REL_WR. |
| `EXT_CSD_BOOT_WP_B_PWR_WP_DIS` | `(0x40)` | BOOT_WP B_PWR_WP_DIS. |
| `EXT_CSD_BOOT_WP_B_PERM_WP_DIS` | `(0x10)` | BOOT_WP B_PERM_WP_DIS. |
| `EXT_CSD_BOOT_WP_B_PERM_WP_EN` | `(0x04)` | BOOT_WP B_PERM_WP_EN. |
| `EXT_CSD_BOOT_WP_B_PWR_WP_EN` | `(0x01)` | BOOT_WP B_PWR_WP_EN. |
| `EXT_CSD_PART_CONFIG_ACC_MASK` | `(0x7)` | PARTITION_CONFIG PARTITION_ACCESS field, bits [2:0] (0 = user area). |
| `EXT_CSD_PART_CONFIG_ACC_BOOT0` | `(0x1)` | PARTITION_ACCESS: first boot partition. |
| `EXT_CSD_PART_CONFIG_ACC_RPMB` | `(0x3)` | PARTITION_ACCESS: RPMB partition. |
| `EXT_CSD_PART_CONFIG_ACC_GP0` | `(0x4)` | PARTITION_ACCESS: first general-purpose partition. |
| `EXT_CSD_PART_SETTING_COMPLETED` | `(0x1)` | PARTITION_SETTING_COMPLETED bit. |
| `EXT_CSD_PART_SUPPORT_PART_EN` | `(0x1)` | PARTITIONING_SUPPORT PARTITIONING_EN bit. |
| `EXT_CSD_CMD_SET_NORMAL` | `(1<<0)` | Command set: standard (CMD6 argument [2:0]). |
| `EXT_CSD_CMD_SET_SECURE` | `(1<<1)` | Command set: secure. |
| `EXT_CSD_CMD_SET_CPSECURE` | `(1<<2)` | Command set: content protection secure. |
| `EXT_CSD_CARD_TYPE_HS_26` | `(1<<0)` | Card can run at 26MHz. |
| `EXT_CSD_CARD_TYPE_HS_52` | `(1<<1)` | Card can run at 52MHz. |
| `EXT_CSD_CARD_TYPE_HS` | `(EXT_CSD_CARD_TYPE_HS_26 \| EXT_CSD_CA...` | Any HS mode. |
| `EXT_CSD_CARD_TYPE_DDR_1_8V` | `(1<<2)` | Card can run at 52MHz, DDR mode at 1.8 V or 3 V I/O. |
| `EXT_CSD_CARD_TYPE_DDR_1_2V` | `(1<<3)` | Card can run at 52MHz, DDR mode at 1.2 V I/O. |
| `EXT_CSD_CARD_TYPE_DDR_52` | `(EXT_CSD_CARD_TYPE_DDR_1_8V \| EXT_CSD...` | Any 52 MHz DDR mode. |
| `EXT_CSD_CARD_TYPE_HS200_1_8V` | `(1<<4)` | Card can run at 200MHz, SDR mode at 1.8 V I/O. |
| `EXT_CSD_CARD_TYPE_HS200_1_2V` | `(1<<5)` | Card can run at 200MHz, SDR mode at 1.2 V I/O. |
| `EXT_CSD_CARD_TYPE_HS200` | `(EXT_CSD_CARD_TYPE_HS200_1_8V \| EXT_C...` | Any HS200 mode. |
| `EXT_CSD_CARD_TYPE_HS400_1_8V` | `(1<<6)` | Card can run at 200MHz DDR, 1.8 V I/O. |
| `EXT_CSD_CARD_TYPE_HS400_1_2V` | `(1<<7)` | Card can run at 200MHz DDR, 1.2 V I/O. |
| `EXT_CSD_CARD_TYPE_HS400` | `(EXT_CSD_CARD_TYPE_HS400_1_8V \| EXT_C...` | Any HS400 mode. |
| `EXT_CSD_CARD_TYPE_HS400ES` | `(1<<8)` | Card can run at HS400ES. |
| `EXT_CSD_BUS_WIDTH_1` | `0` | Card is in 1 bit mode. |
| `EXT_CSD_BUS_WIDTH_4` | `1` | Card is in 4 bit mode. |
| `EXT_CSD_BUS_WIDTH_8` | `2` | Card is in 8 bit mode. |
| `EXT_CSD_DDR_BUS_WIDTH_4` | `5` | Card is in 4 bit DDR mode. |
| `EXT_CSD_DDR_BUS_WIDTH_8` | `6` | Card is in 8 bit DDR mode. |
| `EXT_CSD_BUS_WIDTH_STROBE` | `BIT(7)` | Enhanced strobe mode. |
| `EXT_CSD_TIMING_BC` | `0` | Backwards compatibility. |
| `EXT_CSD_TIMING_HS` | `1` | High speed. |
| `EXT_CSD_TIMING_HS200` | `2` | HS200. |
| `EXT_CSD_TIMING_HS400` | `3` | HS400. |
| `EXT_CSD_DRV_STR_SHIFT` | `4` | Driver Strength shift. |
| `EXT_CSD_SEC_ER_EN` | `BIT(0)` | SEC_FEATURE_SUPPORT SECURE_ER_EN. |
| `EXT_CSD_SEC_BD_BLK_EN` | `BIT(2)` | SEC_FEATURE_SUPPORT SEC_BD_BLK_EN. |
| `EXT_CSD_SEC_GB_CL_EN` | `BIT(4)` | SEC_FEATURE_SUPPORT SEC_GB_CL_EN. |
| `EXT_CSD_SEC_SANITIZE` | `BIT(6)` | SEC_FEATURE_SUPPORT SEC_SANITIZE (v4.5 only). |
| `EXT_CSD_RST_N_EN_MASK` | `0x3` | RST_n_FUNCTION enable field mask. |
| `EXT_CSD_RST_N_ENABLED` | `1` | RST_n is enabled on card. |
| `EXT_CSD_NO_POWER_NOTIFICATION` | `0` | POWER_OFF_NOTIFICATION: no notification. |
| `EXT_CSD_POWER_ON` | `1` | POWER_OFF_NOTIFICATION: powered on. |
| `EXT_CSD_POWER_OFF_SHORT` | `2` | POWER_OFF_NOTIFICATION: short power-off. |
| `EXT_CSD_POWER_OFF_LONG` | `3` | POWER_OFF_NOTIFICATION: long power-off. |
| `EXT_CSD_PWR_CL_8BIT_MASK` | `0xF0` | Power class for the 8-bit bus, bits [7:4]. |
| `EXT_CSD_PWR_CL_4BIT_MASK` | `0x0F` | Power class for the 4-bit bus, bits [3:0]. |
| `EXT_CSD_PWR_CL_8BIT_SHIFT` | `4` | Shift of the 8-bit bus power class. |
| `EXT_CSD_PWR_CL_4BIT_SHIFT` | `0` | Shift of the 4-bit bus power class. |
| `EXT_CSD_PACKED_EVENT_EN` | `BIT(3)` | EXCEPTION_EVENTS_CTRL PACKED_EVENT_EN. |
| `EXT_CSD_URGENT_BKOPS` | `BIT(0)` | EXCEPTION_EVENTS_STATUS URGENT_BKOPS. |
| `EXT_CSD_DYNCAP_NEEDED` | `BIT(1)` | EXCEPTION_EVENTS_STATUS DYNCAP_NEEDED. |
| `EXT_CSD_SYSPOOL_EXHAUSTED` | `BIT(2)` | EXCEPTION_EVENTS_STATUS SYSPOOL_EXHAUSTED. |
| `EXT_CSD_PACKED_FAILURE` | `BIT(3)` | EXCEPTION_EVENTS_STATUS PACKED_FAILURE. |
| `EXT_CSD_PACKED_GENERIC_ERROR` | `BIT(0)` | PACKED_COMMAND_STATUS generic error. |
| `EXT_CSD_PACKED_INDEXED_ERROR` | `BIT(1)` | PACKED_COMMAND_STATUS indexed error. |
| `EXT_CSD_BKOPS_LEVEL_2` | `0x2` | BKOPS_STATUS level 2: performance impacted. |
| `EXT_CSD_MANUAL_BKOPS_MASK` | `0x01` | BKOPS_EN manual background operations enable. |
| `EXT_CSD_AUTO_BKOPS_MASK` | `0x02` | BKOPS_EN automatic background operations enable. |
| `EXT_CSD_CMDQ_MODE_ENABLED` | `BIT(0)` | CMDQ_MODE_EN: command queuing enabled. |
| `EXT_CSD_CMDQ_DEPTH_MASK` | `GENMASK(4, 0)` | CMDQ_DEPTH queue depth field. |
| `EXT_CSD_CMDQ_SUPPORTED` | `BIT(0)` | CMDQ_SUPPORT: command queuing supported. |
| `EMMC_OCR_BUSY` | `(1<<31)` | Bit 31: set when the device has finished power-up. |
| `EMMC_SECTOR_MODE` | `((uint32_t)0x40000000)` | Access mode bits [30:29] = 10b: sector addressing. |
| `SDIO_CMDTIMEOUT_MS` | `(1000)` | Command-phase timeout of the driver, in ms. |
| `SDIO_DATATIMEOUT_MS` | `(5000)` | Data-phase timeout of the driver, in ms. [`SDH_ReadMultiBlocks()`](#SDH_ReadMultiBlocks) and [`SDH_WriteMultiBlocks()`](#SDH_WriteMultiBlocks) return [`Status_Timeout`](#_generic_status) when the data phase does not complete within this time. |
| `SDIO_SDCARD_INT_MODE` | `(0)` | Completion-wait mode of the driver. 0 (default) busy-polls the controller status. The interrupt-driven variant selected by a non-zero value does not build in this SDK, and the SDIO host stack ([`hal_sdio.h`](#hal_sdio-h)) installs its own SDH interrupt handler, so keep this at 0. |
| `EMMC_HIGHSPEED_MODE` | `(0)` | eMMC high-speed switch in [`SDH_Init()`](#SDH_Init). With the default 0 an eMMC device is left in 1-bit mode at the identification clock. A non-zero value makes [`SDH_Init()`](#SDH_Init) switch a high-speed-capable device to HS timing and the requested bus width, and run the bus at the transfer clock set by [`SDH_ClockSet()`](#SDH_ClockSet). |
| `SDH_DEFAULT_BLOCK_SIZE` | `(512U)` | Default (and only supported) data block size, in bytes. |
| `MAKE_STATUS(group, code)` | `((((group)*100) + (code)))` | Construct a status code value from a group and code number. |

## hal_sdio.h { #hal_sdio-h }

`#include "hal_sdio.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sdio.h))

SDIO host stack on the SDH controller: card enumeration, CMD52/CMD53 register and data access, function management and card interrupts.

Implements the host side of the SDIO Simplified Specification (CMD0, CMD5, CMD3, CMD7, CMD52, CMD53) so that an external SDIO device, such as a Wi-Fi module, can be enumerated and accessed over the SDH peripheral. [`hal_sdh.h`](#hal_sdh-h) provides the status-code scheme and controller types; this module adds the SDIO I/O semantics, CCCR/FBR/CIS parsing, function management and DAT1 card-interrupt dispatch. It drives the single SDH controller and uses FreeRTOS objects.

Typical sequence: [`sdio_host_init()`](#sdio_host_init), [`sdio_card_enumerate()`](#sdio_card_enumerate), then bus setup ([`sdio_set_high_speed()`](#sdio_set_high_speed), [`sdio_set_bus_width()`](#sdio_set_bus_width), [`sdio_set_clock()`](#sdio_set_clock)), then [`sdio_set_block_size()`](#sdio_set_block_size) and [`sdio_enable_func()`](#sdio_enable_func) for each function used, [`sdio_claim_irq()`](#sdio_claim_irq) and [`sdio_enable_irq()`](#sdio_enable_irq) for card interrupts, and [`sdio_readb()`](#sdio_readb) / [`sdio_writeb()`](#sdio_writeb) / [`sdio_read_blocks()`](#sdio_read_blocks) / [`sdio_write_blocks()`](#sdio_write_blocks) for I/O.

Threading: all calls are synchronous (blocking). Each CMD52/CMD53 takes the host's recursive mutex for the duration of the command; [`sdio_claim_host()`](#sdio_claim_host) holds it across a sequence of commands. Card-interrupt handlers run in the task that calls [`sdio_wait_irq()`](#sdio_wait_irq) or [`sdio_poll_irq()`](#sdio_poll_irq), not in the ISR.

### sdio_host_init { #sdio_host_init }

```c
SDIO_Status_Type sdio_host_init(SDIO_Host_Type *host, SD_ID_Type sd_id);
```

Initialize a host descriptor and bring up the SDH controller (no card I/O).

Clears `host`, creates its recursive mutex and card-interrupt semaphore, resets and ungates the SDH peripheral, configures 1-bit mode at 400 kHz with 3.3 V signalling and powers the bus. It then registers the card-interrupt ISR and enables the SDH interrupt at the CPU; the card-interrupt signal itself stays disabled until [`sdio_enable_irq()`](#sdio_enable_irq).

| Parameter | Description |
|---|---|
| `host` | Descriptor to initialize (caller-allocated). |
| `sd_id` | Controller ID (`SDH_ID`). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Host ready for [`sdio_card_enumerate()`](#sdio_card_enumerate). |
| `Status_SDIO_InvalidArg` | `host` is NULL or the RTOS objects could not be created. |

!!! warning "Warning"
    Call it once per descriptor: a second call creates new RTOS objects without deleting the old ones. Use [`sdio_host_reinit()`](#sdio_host_reinit) to repeat the controller bring-up.

### sdio_host_reset { #sdio_host_reset }

```c
SDIO_Status_Type sdio_host_reset(SDIO_Host_Type *host);
```

Software-reset the SDH controller (reset all) and wait for completion.

The controller configuration is lost; run [`sdio_host_reinit()`](#sdio_host_reinit) before further card I/O. Only the controller is reset: a device that needs a reset or power-enable GPIO must be sequenced by the caller.

| Parameter | Description |
|---|---|
| `host` | Host initialized with [`sdio_host_init()`](#sdio_host_init). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Reset done. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |

### sdio_card_enumerate { #sdio_card_enumerate }

```c
SDIO_Status_Type sdio_card_enumerate(SDIO_Host_Type *host);
```

Run full SDIO enumeration: CMD0, CMD8, CMD5, CMD3, CMD7, then read the common CIS pointer and each function's FBR and CIS.

The CMD8 response is ignored. CMD5 is repeated with the card's voltage window until the card reports ready (about 1 s at most). If the card does not answer the first CMD5, as happens with a card that stayed selected across a host reset, the CCCR I/O Abort RES bit is written to reset the card's I/O part, CMD5 is polled for up to 1 s, and if needed the sequence is restarted once from CMD0. On success host-&gt;ocr, num_funcs, rca, common_cis_ptr and funcs[1..num_funcs] are filled.

No function is enabled and the bus stays in 1-bit mode at 400 kHz: set up the bus, then call [`sdio_set_block_size()`](#sdio_set_block_size) and [`sdio_enable_func()`](#sdio_enable_func) for each function used.

| Parameter | Description |
|---|---|
| `host` | Host initialized with [`sdio_host_init()`](#sdio_host_init) or [`sdio_host_reinit()`](#sdio_host_reinit). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Card enumerated. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |
| `Status_SDIO_NotSDIOCard` | The card reports no I/O functions. |
| `Status_SDIO_CmdTimeout` | A command failed or the card did not become ready. |
| `Status_SDIO_R5Error` | A CCCR read returned an R5 error. |

### sdio_set_bus_width { #sdio_set_bus_width }

```c
SDIO_Status_Type sdio_set_bus_width(SDIO_Host_Type *host, uint8_t width);
```

Switch bus width on the card and on the controller.

Writes the width bits of CCCR bus interface control, then reprograms the SDH controller with that width, with its high-speed enable following host-&gt;high_speed and with a bus clock of 50 MHz (high speed) or 25 MHz (requested values, see [`sdio_set_clock()`](#sdio_set_clock)). Any clock set earlier with [`sdio_set_clock()`](#sdio_set_clock) is replaced. Card must support 4-bit (most do).

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |
| `width` | [`SDIO_BUS_WIDTH_1BIT`](#hal_sdio-h-macros) or [`SDIO_BUS_WIDTH_4BIT`](#hal_sdio-h-macros). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Width changed. |
| `Status_SDIO_InvalidArg` | `host` is NULL or `width` is not valid. |
| `Status_SDIO_BusWidthReject` | Writing the CCCR register failed. |
| `Status_SDIO_CmdTimeout` | Reading the CCCR register failed. |
| `Status_SDIO_R5Error` | Reading the CCCR register returned an R5 error. |

### sdio_set_bus_width_fast { #sdio_set_bus_width_fast }

```c
void sdio_set_bus_width_fast(SDIO_Host_Type *host, uint8_t width);
```

Switch the bus width on a live, enumerated bus without re-initializing the controller.

Changes only the card's CCCR width bits and the controller's data-width bit; no clock or controller re-initialization. The other CCCR bus interface bits are read once and cached. CMD53 reads use this internally for the 1-bit read options ([`sdio_set_reads_1bit()`](#sdio_set_reads_1bit), [`sdio_set_read_1bit_max()`](#sdio_set_read_1bit_max)). Command errors are ignored.

| Parameter | Description |
|---|---|
| `host` | Enumerated host (must not be NULL). |
| `width` | [`SDIO_BUS_WIDTH_1BIT`](#hal_sdio-h-macros) or [`SDIO_BUS_WIDTH_4BIT`](#hal_sdio-h-macros). |

!!! warning "Warning"
    Hold the host with [`sdio_claim_host()`](#sdio_claim_host) around the call so that it cannot race a transfer in another task.

### sdio_set_high_speed { #sdio_set_high_speed }

```c
SDIO_Status_Type sdio_set_high_speed(SDIO_Host_Type *host, bool enable);
```

Enable or disable SDIO High Speed (50 MHz) on the card and set the bus clock.

Reads CCCR bus speed select. When enabling, it fails if the card does not support high speed; otherwise it sets or clears EHS, records host-&gt;high_speed and calls [`sdio_set_clock()`](#sdio_set_clock) with 50 MHz or 25 MHz.

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |
| `enable` | true to enable high speed, false to return to default speed. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Done. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |
| `Status_SDIO_HighSpeedReject` | The card does not support high speed. |
| `Status_SDIO_CmdTimeout` | The CCCR access failed. |
| `Status_SDIO_R5Error` | The CCCR access returned an R5 error. |

!!! note "Note"
    The controller's high-speed enable is not changed here; it follows host-&gt;high_speed at the next [`sdio_set_bus_width()`](#sdio_set_bus_width). Because the clock is raised first, a caller can instead set EHS with [`sdio_writeb()`](#sdio_writeb), set host-&gt;high_speed and call [`sdio_set_bus_width()`](#sdio_set_bus_width), which applies the controller's high-speed enable and the 50 MHz clock together.

### sdio_set_clock { #sdio_set_clock }

```c
SDIO_Status_Type sdio_set_clock(SDIO_Host_Type *host, uint32_t hz);
```

Set the SDH bus clock (SDCLK).

The caller is responsible for staying within the card capability (default speed: 25 MHz, high speed: 50 MHz). The divider is derived from the 96 MHz SDH source clock by integer division, so the resulting clock can differ from `hz`.

| Parameter | Description |
|---|---|
| `host` | Initialized host. |
| `hz` | Requested bus clock in Hz; must not be 0. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Clock set. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |

### sdio_set_small_pio { #sdio_set_small_pio }

```c
void sdio_set_small_pio(int enable);
```

Select which CMD53 transfers use PIO instead of ADMA2.

Workaround for small transfers whose single ADMA2 descriptor fails to start the data engine at high speed / 4-bit. Applies to all hosts. Default 0.

| Parameter | Description |
|---|---|
| `enable` | 0 = all transfers use ADMA2; 1 (or any other non-zero value except 2) = transfers of at most 64 bytes use PIO; 2 = only 512-byte reads use PIO, all other transfers use ADMA2. |

### sdio_set_sampling_clk_sel { #sdio_set_sampling_clk_sel }

```c
void sdio_set_sampling_clk_sel(int enable);
```

Select the delayed (io_dly) sampling clock for reads (HOST_CTRL_2 bit7).

With the bit set (SAMPLING_CLK_SEL), the input-delay taps in the GLB register `GLB_SMIH_0_IO_DLY_0` shift the read capture point; with it clear, the reset state, they have no effect. The register is written immediately.

| Parameter | Description |
|---|---|
| `enable` | Non-zero sets the bit, 0 clears it. |

### sdio_set_ignore_rd_crc { #sdio_set_ignore_rd_crc }

```c
void sdio_set_ignore_rd_crc(int enable);
```

Accept CMD53 read data even when the controller reports a data-phase error.

Data CRC (and other non-timeout data errors) are ignored for reads; a data timeout is still reported. Writes are not affected. Default off. A caller that enables this must verify the received data by other means.

| Parameter | Description |
|---|---|
| `enable` | Non-zero to ignore read data errors, 0 for normal checking. |

### sdio_set_reads_1bit { #sdio_set_reads_1bit }

```c
void sdio_set_reads_1bit(int enable);
```

Run all CMD53 reads at 1-bit while writes keep the configured width.

Each CMD53 read switches to 1-bit with [`sdio_set_bus_width_fast()`](#sdio_set_bus_width_fast) inside the transfer's mutex and restores the width afterwards, so the switch is atomic against other tasks. Default off.

| Parameter | Description |
|---|---|
| `enable` | Non-zero to read at 1-bit, 0 to read at the configured width. |

### sdio_set_read_1bit_max { #sdio_set_read_1bit_max }

```c
void sdio_set_read_1bit_max(uint32_t max_bytes);
```

Run CMD53 reads of at most `max_bytes` bytes at 1-bit.

Larger reads keep the configured width. The width switch happens inside the transfer's mutex, as for [`sdio_set_reads_1bit()`](#sdio_set_reads_1bit). Independent of [`sdio_set_reads_1bit()`](#sdio_set_reads_1bit), which forces every read to 1-bit.

| Parameter | Description |
|---|---|
| `max_bytes` | Size threshold in bytes; 0 disables. |

### sdio_set_dir_phase { #sdio_set_dir_phase }

```c
void sdio_set_dir_phase(const SDIO_Phase_Type *rd_phase, const SDIO_Phase_Type *wr_phase, int enable);
```

Use separate sampling phases for CMD53 reads and CMD53 writes.

When enabled, each CMD53 applies `rd_phase` or `wr_phase`, chosen by transfer direction, inside the transfer's mutex. The last applied setting is cached, so consecutive transfers in the same direction write no registers. Useful when the read-optimal phase makes the host mis-sample the card's CRC status after a write. Combines with [`sdio_set_reads_1bit()`](#sdio_set_reads_1bit): a 1-bit read still uses `rd_phase`. Default off.

| Parameter | Description |
|---|---|
| `rd_phase` | Phase applied before reads (copied). |
| `wr_phase` | Phase applied before writes (copied). |
| `enable` | Non-zero to enable (both pointers must be non-NULL, otherwise the feature is disabled), 0 to disable. Disabling leaves the registers as they are; the caller restores its preferred global phase. |

### sdio_host_reinit { #sdio_host_reinit }

```c
SDIO_Status_Type sdio_host_reinit(SDIO_Host_Type *host);
```

Re-run the SDH controller bring-up and clear the enumeration state without re-creating the RTOS objects or re-registering the ISR.

Under the host mutex, repeats the controller bring-up of [`sdio_host_init()`](#sdio_host_init) (reset, 1-bit, 400 kHz, power on) and clears rca, num_funcs, common_cis_ptr, funcs[], bus_width (1-bit) and high_speed. Registered interrupt handlers are kept, but [`sdio_enable_irq()`](#sdio_enable_irq) must be called again after re-enumeration. Use it for repeated re-enumeration (follow with [`sdio_card_enumerate()`](#sdio_card_enumerate)); [`sdio_host_init()`](#sdio_host_init) must not be called twice.

| Parameter | Description |
|---|---|
| `host` | Host already initialized once with [`sdio_host_init()`](#sdio_host_init). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Controller re-initialized. |
| `Status_SDIO_InvalidArg` | `host` is NULL or was never initialized. |

### sdio_set_block_size { #sdio_set_block_size }

```c
SDIO_Status_Type sdio_set_block_size(SDIO_Host_Type *host, uint8_t func_num, uint16_t block_size);
```

Set function block size (CCCR FN0_BLOCK_SIZE or FBR per-func).

Writes the 2-byte block size register with two CMD52 writes and records the value in funcs[func_num].cur_blk_size, which [`sdio_read_blocks()`](#sdio_read_blocks) and [`sdio_write_blocks()`](#sdio_write_blocks) use.

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |
| `func_num` | Function number, 0 to host-&gt;num_funcs. |
| `block_size` | Block size in bytes; not checked against max_blk_size. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Block size set. |
| `Status_SDIO_InvalidArg` | `host` is NULL or `func_num` &gt; num_funcs. |
| `Status_SDIO_BlockSizeReject` | A register write failed. |

### sdio_enable_func { #sdio_enable_func }

```c
SDIO_Status_Type sdio_enable_func(SDIO_Host_Type *host, uint8_t func_num);
```

Set IO Enable bit, poll IO Ready until function is ready.

IO_READY is polled up to 200 times at 5 ms intervals (about 1 s).

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |
| `func_num` | Function number, 1 to host-&gt;num_funcs. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Function enabled and ready. |
| `Status_SDIO_InvalidArg` | `host` is NULL or `func_num` is out of range. |
| `Status_SDIO_FuncEnableFail` | The write failed or the function did not become ready in time. |
| `Status_SDIO_CmdTimeout` | Reading IO_ENABLE failed. |
| `Status_SDIO_R5Error` | Reading IO_ENABLE returned an R5 error. |

### sdio_disable_func { #sdio_disable_func }

```c
SDIO_Status_Type sdio_disable_func(SDIO_Host_Type *host, uint8_t func_num);
```

Clear IO Enable bit.

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |
| `func_num` | Function number, 1 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Function disabled. |
| `Status_SDIO_InvalidArg` | `host` is NULL or `func_num` is 0. |
| `Status_SDIO_CmdTimeout` | The CCCR access failed. |
| `Status_SDIO_R5Error` | The CCCR access returned an R5 error. |

### sdio_claim_host { #sdio_claim_host }

```c
SDIO_Status_Type sdio_claim_host(SDIO_Host_Type *host);
```

Claim exclusive ownership of the SDIO host for a sequence of back-to-back CMDs (recursive).

Use it to span several [`sdio_readb()`](#sdio_readb) / [`sdio_writeb()`](#sdio_writeb) / [`sdio_read_blocks()`](#sdio_read_blocks) / [`sdio_write_blocks()`](#sdio_write_blocks) calls without releasing the bus in between, for example polling a status register with CMD52 and then writing data with CMD53. Waits forever for the mutex. Each [`sdio_claim_host()`](#sdio_claim_host) must be paired with a [`sdio_release_host()`](#sdio_release_host) on the same task.

Calling these is optional: every CMD52/CMD53 function already claims and releases the host internally. Nesting works because the host mutex is recursive.

| Parameter | Description |
|---|---|
| `host` | Initialized host. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Host claimed. |
| `Status_SDIO_InvalidArg` | `host` or its mutex is NULL. |

### sdio_release_host { #sdio_release_host }

```c
SDIO_Status_Type sdio_release_host(SDIO_Host_Type *host);
```

Release the host claimed with [`sdio_claim_host()`](#sdio_claim_host).

| Parameter | Description |
|---|---|
| `host` | Host claimed by the calling task. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Host released. |
| `Status_SDIO_InvalidArg` | `host` or its mutex is NULL. |

### sdio_readb { #sdio_readb }

```c
SDIO_Status_Type sdio_readb(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, uint8_t *out_val);
```

Read one byte from func/addr with CMD52 (IO_RW_DIRECT).

| Parameter | Description |
|---|---|
| `host` | Host with a selected card. |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Register address, 0 to 0x1FFFF. |
| `out_val` | Byte read; must not be NULL. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Byte read. |
| `Status_SDIO_InvalidArg` | A NULL pointer, or `func_num` / `addr` out of range. |
| `Status_SDIO_CmdTimeout` | The command failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_writeb { #sdio_writeb }

```c
SDIO_Status_Type sdio_writeb(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, uint8_t val);
```

Write one byte with CMD52 (IO_RW_DIRECT).

| Parameter | Description |
|---|---|
| `host` | Host with a selected card. |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Register address, 0 to 0x1FFFF. |
| `val` | Byte to write. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Byte written. |
| `Status_SDIO_InvalidArg` | `host` is NULL, or `func_num` / `addr` out of range. |
| `Status_SDIO_CmdTimeout` | The command failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_writeb_readback { #sdio_writeb_readback }

```c
SDIO_Status_Type sdio_writeb_readback(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, uint8_t val, uint8_t *out_old);
```

Write one byte with CMD52 and the read-after-write (RAW) flag.

With RAW set the card returns the register content read back after the write in the R5 response, which is returned in `out_old`.

| Parameter | Description |
|---|---|
| `host` | Host with a selected card. |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Register address, 0 to 0x1FFFF. |
| `val` | Byte to write. |
| `out_old` | Byte returned in the R5 response; may be NULL. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Byte written. |
| `Status_SDIO_InvalidArg` | `host` is NULL, or `func_num` / `addr` out of range. |
| `Status_SDIO_CmdTimeout` | The command failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_read_bytes { #sdio_read_bytes }

```c
SDIO_Status_Type sdio_read_bytes(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, uint8_t *buf, uint16_t count, bool fixed_addr);
```

Byte-mode CMD53 read (count is byte length, max 511; 0 means 512).

Uses ADMA2 unless [`sdio_set_small_pio()`](#sdio_set_small_pio) selects PIO for this transfer; the data cache is maintained over `buf` by the function. Takes the host mutex and applies the read options set with [`sdio_set_dir_phase()`](#sdio_set_dir_phase), [`sdio_set_reads_1bit()`](#sdio_set_reads_1bit), [`sdio_set_read_1bit_max()`](#sdio_set_read_1bit_max) and [`sdio_set_ignore_rd_crc()`](#sdio_set_ignore_rd_crc).

| Parameter | Description |
|---|---|
| `host` | Host with a selected card. |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Start register address, 0 to 0x1FFFF. |
| `buf` | Destination, `count` bytes (512 if 0); must be 4-byte aligned. |
| `count` | Byte count, 0 to 511; 0 transfers 512 bytes. |
| `fixed_addr` | true: the card address is not incremented (FIFO access); false: it increments. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Data read. |
| `Status_SDIO_InvalidArg` | `host` or `buf` is NULL, or an argument is out of range. |
| `Status_SDIO_BufferAlignment` | `buf` is not 4-byte aligned. |
| `Status_SDIO_DataTimeout` | The transfer failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_write_bytes { #sdio_write_bytes }

```c
SDIO_Status_Type sdio_write_bytes(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, const uint8_t *buf, uint16_t count, bool fixed_addr);
```

Byte-mode CMD53 write (count is byte length, max 511; 0 means 512).

Uses ADMA2 unless [`sdio_set_small_pio()`](#sdio_set_small_pio) selects PIO for this transfer; the data cache is cleaned over `buf` before the transfer. Takes the host mutex and applies the write phase set with [`sdio_set_dir_phase()`](#sdio_set_dir_phase).

| Parameter | Description |
|---|---|
| `host` | Host with a selected card. |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Start register address, 0 to 0x1FFFF. |
| `buf` | Source, `count` bytes (512 if 0); must be 4-byte aligned. |
| `count` | Byte count, 0 to 511; 0 transfers 512 bytes. |
| `fixed_addr` | true: the card address is not incremented (FIFO access); false: it increments. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Data written. |
| `Status_SDIO_InvalidArg` | `host` or `buf` is NULL, or an argument is out of range. |
| `Status_SDIO_BufferAlignment` | `buf` is not 4-byte aligned. |
| `Status_SDIO_DataTimeout` | The transfer failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_read_blocks { #sdio_read_blocks }

```c
SDIO_Status_Type sdio_read_blocks(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, uint8_t *buf, uint16_t count, bool fixed_addr);
```

Read blocks with CMD53 in block mode.

The function must have its block size set first: the block size is funcs[func_num].cur_blk_size, set with [`sdio_set_block_size()`](#sdio_set_block_size); total bytes = `count` * block size. Transfer, cache and option handling are as for [`sdio_read_bytes()`](#sdio_read_bytes).

| Parameter | Description |
|---|---|
| `host` | Host with a selected card (must not be NULL). |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Start register address, 0 to 0x1FFFF. |
| `buf` | Destination, `count` blocks; must be 4-byte aligned. |
| `count` | Number of blocks, 1 to 511. With 0 the command carries a block count of 0 (an open-ended transfer in the SDIO specification) while the host moves one block, so do not pass 0. |
| `fixed_addr` | true: the card address is not incremented (FIFO access); false: it increments. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Data read. |
| `Status_SDIO_InvalidArg` | No block size set, `buf` is NULL, or an argument is out of range. |
| `Status_SDIO_BufferAlignment` | `buf` is not 4-byte aligned. |
| `Status_SDIO_DataTimeout` | The transfer failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_write_blocks { #sdio_write_blocks }

```c
SDIO_Status_Type sdio_write_blocks(SDIO_Host_Type *host, uint8_t func_num, uint32_t addr, const uint8_t *buf, uint16_t count, bool fixed_addr);
```

Write blocks with CMD53 in block mode.

The function must have its block size set first: the block size is funcs[func_num].cur_blk_size, set with [`sdio_set_block_size()`](#sdio_set_block_size); total bytes = `count` * block size. Transfer and cache handling are as for [`sdio_write_bytes()`](#sdio_write_bytes).

| Parameter | Description |
|---|---|
| `host` | Host with a selected card (must not be NULL). |
| `func_num` | Function number, 0 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `addr` | Start register address, 0 to 0x1FFFF. |
| `buf` | Source, `count` blocks; must be 4-byte aligned. |
| `count` | Number of blocks, 1 to 511 (do not pass 0, see [`sdio_read_blocks()`](#sdio_read_blocks)). |
| `fixed_addr` | true: the card address is not incremented (FIFO access); false: it increments. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Data written. |
| `Status_SDIO_InvalidArg` | No block size set, `buf` is NULL, or an argument is out of range. |
| `Status_SDIO_BufferAlignment` | `buf` is not 4-byte aligned. |
| `Status_SDIO_DataTimeout` | The transfer failed. |
| `Status_SDIO_R5Error` | The R5 response flags an error. |

### sdio_claim_irq { #sdio_claim_irq }

```c
SDIO_Status_Type sdio_claim_irq(SDIO_Host_Type *host, uint8_t func_num, SDIO_IRQ_Handler handler, void *arg);
```

Register a per-function interrupt handler.

Must be called before [`sdio_enable_irq()`](#sdio_enable_irq). Only stores `handler` and `arg` in the host; [`sdio_enable_irq()`](#sdio_enable_irq) enables the interrupt in the card for every function that has a handler.

| Parameter | Description |
|---|---|
| `host` | Initialized host. |
| `func_num` | Function number, 1 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |
| `handler` | Handler, called from [`sdio_wait_irq()`](#sdio_wait_irq) / [`sdio_poll_irq()`](#sdio_poll_irq). |
| `arg` | Argument passed to `handler`. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Handler registered. |
| `Status_SDIO_InvalidArg` | `host` is NULL or `func_num` is out of range. |

### sdio_release_irq { #sdio_release_irq }

```c
SDIO_Status_Type sdio_release_irq(SDIO_Host_Type *host, uint8_t func_num);
```

Unregister the interrupt handler of a function.

Clears the handler and argument only; CCCR INT_ENABLE in the card is not changed (call [`sdio_enable_irq()`](#sdio_enable_irq) or [`sdio_disable_irq()`](#sdio_disable_irq) to update it). Not synchronized with interrupt dispatch: release a handler only while no task is running [`sdio_wait_irq()`](#sdio_wait_irq) or [`sdio_poll_irq()`](#sdio_poll_irq) on this host. Not for ISR context.

| Parameter | Description |
|---|---|
| `host` | Initialized host. |
| `func_num` | Function number, 1 to [`SDIO_MAX_FUNCS`](#hal_sdio-h-macros). |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Handler removed. |
| `Status_SDIO_InvalidArg` | `host` is NULL or `func_num` is out of range. |

### sdio_enable_irq { #sdio_enable_irq }

```c
SDIO_Status_Type sdio_enable_irq(SDIO_Host_Type *host);
```

Enable the DAT1 card interrupt at the SDH controller and set CCCR INT_ENABLE for registered functions.

Writes INT_ENABLE with the master enable bit plus the bit of every function 1..num_funcs that has a handler, then enables the controller's card-interrupt status and signal. Call once after all [`sdio_claim_irq()`](#sdio_claim_irq) calls, and again after changing the set of handlers or after [`sdio_host_reinit()`](#sdio_host_reinit).

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Interrupts enabled. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |
| `Status_SDIO_CmdTimeout` | Writing INT_ENABLE failed. |
| `Status_SDIO_R5Error` | Writing INT_ENABLE returned an R5 error. |

### sdio_disable_irq { #sdio_disable_irq }

```c
SDIO_Status_Type sdio_disable_irq(SDIO_Host_Type *host);
```

Disable the card interrupt at the controller and clear CCCR INT_ENABLE.

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Interrupts disabled. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |
| `Status_SDIO_CmdTimeout` | Writing INT_ENABLE failed. |
| `Status_SDIO_R5Error` | Writing INT_ENABLE returned an R5 error. |

### sdio_set_wait_demotion { #sdio_set_wait_demotion }

```c
void sdio_set_wait_demotion(void *task, unsigned base_prio);
```

Lower a task's priority while it waits for the data phase of an SDH DMA transfer.

The SDH data phase of a blocking transfer, such as a CMD53, is polled. While the registered task polls, its priority is set to `tskIDLE_PRIORITY + 1`, so that lower-priority tasks can run, and is then set back to `base_prio`. Other tasks keep polling at their own priority.

| Parameter | Description |
|---|---|
| `task` | FreeRTOS `TaskHandle_t` of the task to demote; NULL disables. |
| `base_prio` | Priority restored after each wait. Pass the task's base priority: while the host mutex is held, the current priority may be raised by priority inheritance. |

### sdio_poll_irq { #sdio_poll_irq }

```c
SDIO_Status_Type sdio_poll_irq(SDIO_Host_Type *host);
```

Poll SDH for SDIO card interrupt and dispatch to registered handlers.

Non-blocking. Takes the card-interrupt semaphore with zero timeout; if the ISR has not given it, reads the controller's card-interrupt status directly (for use without [`sdio_enable_irq()`](#sdio_enable_irq)). When an interrupt is pending, reads CCCR INT_PENDING with CMD52 and calls the handler of each pending function. Returns immediately whether or not any work was found.

Prefer [`sdio_wait_irq()`](#sdio_wait_irq): it blocks until the ISR signals instead of polling.

| Parameter | Description |
|---|---|
| `host` | Enumerated host. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Nothing pending, or the handlers were called. |
| `Status_SDIO_InvalidArg` | `host` is NULL. |
| `Status_SDIO_CmdTimeout` | Reading INT_PENDING failed. |
| `Status_SDIO_R5Error` | Reading INT_PENDING returned an R5 error. |

### sdio_wait_irq { #sdio_wait_irq }

```c
SDIO_Status_Type sdio_wait_irq(SDIO_Host_Type *host, uint32_t ticks);
```

Block on the SDH card-interrupt semaphore (given by the ISR), then read CCCR INT_PENDING over CMD52 and dispatch to registered per-function handlers.

Requires [`sdio_enable_irq()`](#sdio_enable_irq).

| Parameter | Description |
|---|---|
| `host` | SDIO host descriptor. |
| `ticks` | RTOS ticks to wait; `portMAX_DELAY` waits forever. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | An interrupt was dispatched (also when no registered handler matched). |
| `Status_SDIO_InvalidArg` | `host` is NULL. |
| `Status_SDIO_CmdTimeout` | No interrupt within `ticks`, or reading INT_PENDING failed. |
| `Status_SDIO_R5Error` | Reading INT_PENDING returned an R5 error. |

### sdio_walk_cis { #sdio_walk_cis }

```c
SDIO_Status_Type sdio_walk_cis(SDIO_Host_Type *host, uint8_t func_num, uint32_t start_ptr, SDIO_CIS_Tuple_CB cb, void *arg);
```

Walk a CIS tuple chain from `start_ptr` and call `cb` for each tuple.

Tuples are read with CMD52 from the function 0 address space. Null tuples are skipped and not reported; the walk ends at [`SDIO_CISTPL_END`](#hal_sdio-h-macros), when `cb` returns non-zero, or at the end of the CIS area (0x17FFF). Used during enumeration; exposed for device-specific parsing.

| Parameter | Description |
|---|---|
| `host` | Host with a selected card. |
| `func_num` | Function that owns the chain; currently unused, since the CIS is always read from function 0 space. |
| `start_ptr` | Address of the first tuple, 0x1000 to 0x17FFF (for example `SDIO_Func_Info_Type::cis_ptr`). |
| `cb` | Callback per tuple; may be NULL. |
| `arg` | Argument passed to `cb`. |

| Return value | Description |
|---|---|
| `Status_SDIO_Success` | Walk finished. |
| `Status_SDIO_InvalidArg` | `start_ptr` is outside the CIS area, or `host` is NULL. |
| `Status_SDIO_CmdTimeout` | A CMD52 read failed. |
| `Status_SDIO_R5Error` | A CMD52 read returned an R5 error. |

### SDIO_Status_Type { #SDIO_Status_Type }

SDIO host status codes.

[`Status_SDIO_Success`](#SDIO_Status_Type) is 0, the same value as [`Status_Success`](#_generic_status). The other codes are in the [`StatusGroup_SDH`](#_status_groups) group, numbered from 100.

| Name | Value | Description |
|---|---|---|
| `Status_SDIO_Success` | `0` | Success. |
| `Status_SDIO_NoCard` | `MAKE_STATUS(StatusGroup_SDH, 100U)` | No card (not returned by the current implementation). |
| `Status_SDIO_NotSDIOCard` | `MAKE_STATUS(StatusGroup_SDH, 101U)` | The CMD5 response reports no I/O functions. |
| `Status_SDIO_FuncNotSupported` | `MAKE_STATUS(StatusGroup_SDH, 102U)` | Function not supported (not returned by the current implementation). |
| `Status_SDIO_FuncEnableFail` | `MAKE_STATUS(StatusGroup_SDH, 103U)` | Writing IO_ENABLE failed or the function did not become ready in IO_READY. |
| `Status_SDIO_BlockSizeReject` | `MAKE_STATUS(StatusGroup_SDH, 104U)` | Writing the block size register failed. |
| `Status_SDIO_BusWidthReject` | `MAKE_STATUS(StatusGroup_SDH, 105U)` | Writing the CCCR bus interface control register failed. |
| `Status_SDIO_HighSpeedReject` | `MAKE_STATUS(StatusGroup_SDH, 106U)` | The card does not support high speed (CCCR SHS clear). |
| `Status_SDIO_CmdTimeout` | `MAKE_STATUS(StatusGroup_SDH, 107U)` | A command failed (no response, timeout or CRC error), the card did not become ready, or [`sdio_wait_irq()`](#sdio_wait_irq) timed out. |
| `Status_SDIO_CmdCRCError` | `MAKE_STATUS(StatusGroup_SDH, 108U)` | Command CRC error (not returned; reported as [`Status_SDIO_CmdTimeout`](#SDIO_Status_Type)). |
| `Status_SDIO_DataTimeout` | `MAKE_STATUS(StatusGroup_SDH, 109U)` | The CMD53 data phase failed (timeout, CRC or DMA error). |
| `Status_SDIO_DataCRCError` | `MAKE_STATUS(StatusGroup_SDH, 110U)` | Data CRC error (not returned; reported as [`Status_SDIO_DataTimeout`](#SDIO_Status_Type)). |
| `Status_SDIO_R5Error` | `MAKE_STATUS(StatusGroup_SDH, 111U)` | The R5 response flags an error (CRC, illegal command, general error, invalid function or out of range). |
| `Status_SDIO_InvalidArg` | `MAKE_STATUS(StatusGroup_SDH, 112U)` | Invalid argument or host state, or RTOS object creation failed in [`sdio_host_init()`](#sdio_host_init). |
| `Status_SDIO_BufferAlignment` | `MAKE_STATUS(StatusGroup_SDH, 113U)` | The CMD53 buffer is not 4-byte aligned or its address was rejected by the DMA. |
| `Status_SDIO_TupleNotFound` | `MAKE_STATUS(StatusGroup_SDH, 114U)` | CIS tuple not found (not returned by the current implementation). |

### SDIO_Func_Info_Type { #SDIO_Func_Info_Type }

Per-function information collected during enumeration.

Stored in `SDIO_Host_Type::funcs`, indexed by function number. [`sdio_card_enumerate()`](#sdio_card_enumerate) fills func_num, cis_ptr and, from the function CIS, func_class, manf_id, prod_id and max_blk_size.

| Field | Type | Description |
|---|---|---|
| `func_num` | `uint8_t` | 1..SDIO_MAX_FUNCS (0 reserved for CCCR) |
| `func_class` | `uint8_t` | Function code from CISTPL_FUNCID (first body byte). |
| `enabled` | `uint8_t` | Set after [`sdio_enable_func()`](#sdio_enable_func), cleared by [`sdio_disable_func()`](#sdio_disable_func). |
| `cur_blk_size` | `uint16_t` | Block size programmed with [`sdio_set_block_size()`](#sdio_set_block_size) (0 = not set). |
| `max_blk_size` | `uint16_t` | CIS-reported maximum block size (CISTPL_FUNCE), 0 if absent. |
| `cis_ptr` | `uint32_t` | Function-specific CIS chain start (from the FBR). |
| `manf_id` | `uint16_t` | Manufacturer code from CISTPL_MANFID. |
| `prod_id` | `uint16_t` | Card (product) ID from CISTPL_MANFID. |

### SDIO_Host_Type { #SDIO_Host_Type }

SDIO host descriptor.

One per SDH controller instance.

Caller allocates; pass to [`sdio_host_init()`](#sdio_host_init) before any other API. The stack keeps a pointer to the most recently initialized host for its interrupt handler, so only one host is active at a time.

| Field | Type | Description |
|---|---|---|
| `sd_id` | `SD_ID_Type` | Underlying SDH controller ID. |
| `rca` | `uint16_t` | Relative card address from CMD3. |
| `num_funcs` | `uint8_t` | Discovered IO function count (from the CMD5 response). |
| `bus_width` | `uint8_t` | SDIO_BUS_WIDTH_1BIT or SDIO_BUS_WIDTH_4BIT. |
| `high_speed` | `uint8_t` | 1 if HS enabled; [`sdio_set_bus_width()`](#sdio_set_bus_width) applies it to the controller |
| `ocr` | `uint32_t` | Operating Conditions Register (voltage window bits [23:15]). |
| `common_cis_ptr` | `uint32_t` | CIS pointer for function 0. |
| `funcs` | `SDIO_Func_Info_Type[SDIO_MAX_FUNCS+1]` | Per-function info, indexed by function number (index 0 is only used for cur_blk_size). |
| `irq_handlers` | `SDIO_IRQ_Handler[SDIO_MAX_FUNCS+1]` | Interrupt handlers, indexed by function number (set by [`sdio_claim_irq()`](#sdio_claim_irq)). |
| `irq_args` | `void *[SDIO_MAX_FUNCS+1]` | Handler arguments, indexed by function number. |
| `mutex` | `void *` | Opaque OS mutex handle (recursive). |
| `card_int_sem` | `void *` | Binary sem given by SDH ISR on DAT1 IRQ. |

### SDIO_Phase_Type { #SDIO_Phase_Type }

One SDH sampling-phase setting: the full GLB input-delay register word plus HOST_CTRL_2 bit7 SAMPLING_CLK_SEL.

| Field | Type | Description |
|---|---|---|
| `io_dly` | `uint32_t` | Full value of GLB register `GLB_SMIH_0_IO_DLY_0` (GLB_BASE + 0x438), the input-delay taps. |
| `samp_sel` | `uint8_t` | SDH HOST_CTRL_2 bit7 SAMPLING_CLK_SEL: non-zero selects the delayed clock. |

### Typedefs { #hal_sdio-h-typedefs }

| Name | Definition | Description |
|---|---|---|
| `SDIO_IRQ_Handler` | `typedef void(*) SDIO_IRQ_Handler(uint8_t func_num, void *arg)` | Per-function SDIO card-interrupt handler. Called from [`sdio_wait_irq()`](#sdio_wait_irq) or [`sdio_poll_irq()`](#sdio_poll_irq), in the calling task's context (not in the ISR), for each function whose bit is set in CCCR INT_PENDING. The host has already cleared the controller's card-interrupt status; the handler must clear the interrupt cause in the device, typically by writing the function's own interrupt register. It may call the CMD52 and CMD53 functions of this module. |
| `SDIO_CIS_Tuple_CB` | `typedef int(*) SDIO_CIS_Tuple_CB(uint8_t code, uint8_t link, const uint8_t *body, uint8_t body_len, void *arg)` | Callback invoked by [`sdio_walk_cis()`](#sdio_walk_cis) for each CIS tuple. |

### Macros { #hal_sdio-h-macros }

| Name | Value | Description |
|---|---|---|
| `SDIO_FUNC_0` | `0U` | Common (CCCR) function. |
| `SDIO_FUNC_1` | `1U` | I/O function 1. |
| `SDIO_FUNC_2` | `2U` | I/O function 2. |
| `SDIO_MAX_FUNCS` | `7U` | Max IO functions per card. |
| `SDIO_CCCR_REVISION` | `0x00U` | CCCR/SDIO revision. |
| `SDIO_CCCR_SD_SPEC_REVISION` | `0x01U` | SD specification revision. |
| `SDIO_CCCR_IO_ENABLE` | `0x02U` | I/O enable: bit n enables function n. |
| `SDIO_CCCR_IO_READY` | `0x03U` | I/O ready: bit n set when function n is ready. |
| `SDIO_CCCR_INT_ENABLE` | `0x04U` | Interrupt enable: bit 0 master enable, bit n function n. |
| `SDIO_CCCR_INT_PENDING` | `0x05U` | Interrupt pending: bit n set while function n interrupts. |
| `SDIO_CCCR_IO_ABORT` | `0x06U` | I/O abort: function select for abort, RES (I/O reset) bit. |
| `SDIO_CCCR_BUS_INTERFACE_CTRL` | `0x07U` | Bus interface control (bus width, card-detect pull-up). |
| `SDIO_CCCR_CARD_CAPABILITY` | `0x08U` | Card capability. |
| `SDIO_CCCR_COMMON_CIS_PTR` | `0x09U` | Common CIS pointer, 3 bytes little-endian. |
| `SDIO_CCCR_BUS_SUSPEND` | `0x0CU` | Bus suspend. |
| `SDIO_CCCR_FUNC_SELECT` | `0x0DU` | Function select. |
| `SDIO_CCCR_EXEC_FLAGS` | `0x0EU` | Exec flags. |
| `SDIO_CCCR_READY_FLAGS` | `0x0FU` | Ready flags. |
| `SDIO_CCCR_FN0_BLOCK_SIZE` | `0x10U` | Function 0 block size, 2 bytes little-endian. |
| `SDIO_CCCR_POWER_CONTROL` | `0x12U` | Power control. |
| `SDIO_CCCR_HIGHSPEED` | `0x13U` | Bus speed select: bit 0 SHS (high speed supported), bit 1 EHS (enable high speed). |
| `SDIO_FBR_BASE(func)` | `(0x100U * (func))` | Base address of the FBR of a function. |
| `SDIO_FBR_CSA_PTR_OFFSET` | `0x0BU` | FBR offset 0x0B, intended for the CSA pointer (3 bytes LE). The SDIO specification places the CSA pointer at 0x0C-0x0E; not used by this stack. |
| `SDIO_FBR_CIS_PTR_OFFSET` | `0x09U` | FBR offset of the function CIS pointer, 3 bytes LE. |
| `SDIO_FBR_BLOCK_SIZE_OFFSET` | `0x10U` | FBR offset of the function block size, 2 bytes LE. |
| `SDIO_CISTPL_NULL` | `0x00U` | Null tuple (skipped). |
| `SDIO_CISTPL_VERS_1` | `0x15U` | Level 1 version / product information. |
| `SDIO_CISTPL_MANFID` | `0x20U` | Manufacturer and card ID. |
| `SDIO_CISTPL_FUNCID` | `0x21U` | Function ID. |
| `SDIO_CISTPL_FUNCE` | `0x22U` | Function extension. |
| `SDIO_CISTPL_END` | `0xFFU` | End of the tuple chain. |
| `SDIO_BUS_WIDTH_1BIT` | `0x00U` | Bus width field: 1-bit. |
| `SDIO_BUS_WIDTH_4BIT` | `0x02U` | Bus width field: 4-bit. |
| `SDIO_BUS_ECSI_MASK` | `0x20U` | ECSI: enable continuous SPI interrupt. |
| `SDIO_BUS_SCSI_MASK` | `0x40U` | SCSI: continuous SPI interrupt supported. |
| `SDIO_BUS_CD_DISABLE` | `0x80U` | CD disable: disconnect the DAT3 pull-up. |
| `SDIO_CMD53_RW_FLAG` | `(1U << 31)` | R/W flag: 1 = write. |
| `SDIO_CMD53_FUNC_SHIFT` | `28` | Shift of the function number field. |
| `SDIO_CMD53_FUNC_MASK` | `(0x7U << 28)` | Function number field, bits [30:28]. |
| `SDIO_CMD53_BLOCK_MODE` | `(1U << 27)` | Block mode (1) or byte mode (0). |
| `SDIO_CMD53_OP_INC_ADDR` | `(1U << 26)` | OP code: incrementing address. |
| `SDIO_CMD53_REG_ADDR_SHIFT` | `9` | Shift of the register address field. |
| `SDIO_CMD53_REG_ADDR_MASK` | `(0x1FFFFU << 9)` | Register address field, bits [25:9]. |
| `SDIO_CMD53_BYTE_BLOCK_COUNT_MAX` | `0x1FFU` | Largest byte/block count (9-bit count field). |

## hal_pio_sdh.h { #hal_pio_sdh-h }

`#include "hal_pio_sdh.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pio_sdh.h))

SD card host built on the IPRO7 PIO state machines: card initialization, 512-byte block read and write, FatFS port.

An alternative to the hardware SDH controller ([`hal_sdh.h`](#hal_sdh-h)) for SD memory cards. A PIO state machine generates CLK by side-set and shifts the 48-bit commands out and the responses in on CMD; the same state machine then clocks the DATA lines (1-bit or 4-bit) for the data phase. The hardware SDH (on GPIO28-33) is independent of this host and is left untouched, so both can be used in the same system.

Typical use: fill a [`hal_pio_sdh_cfg_t`](#hal_pio_sdh_cfg_t), call [`hal_pio_sdh_init()`](#hal_pio_sdh_init), then [`hal_pio_sdh_read_blocks()`](#hal_pio_sdh_read_blocks) and [`hal_pio_sdh_write_blocks()`](#hal_pio_sdh_write_blocks), or register the host with FatFS through [`fatfs_pio_sdh_driver_register()`](#fatfs_pio_sdh_driver_register). Functions that return `int` return 0 on success and a negative value on error. The driver state is global (one card) and the functions are blocking and not thread-safe.

### hal_pio_sdh_init { #hal_pio_sdh_init }

```c
int hal_pio_sdh_init(const hal_pio_sdh_cfg_t *cfg, hal_pio_sdh_card_t *out);
```

Set up the PIO host and initialize the SD card.

Runs [`hal_pio_sdh_hw_setup()`](#hal_pio_sdh_hw_setup), sends the power-up clocks and then CMD0, CMD8, ACMD41 (repeated until the card is ready, up to 1000 attempts), CMD2, CMD3, CMD9, CMD7 and ACMD6 (4-bit bus). It then tries the CMD6 high-speed switch (best effort, see [`hal_pio_sdh_switch_hs()`](#hal_pio_sdh_switch_hs)) and sets the 24 MHz transfer clock. Supports SD memory cards (SDSC, SDHC, SDXC).

| Parameter | Description |
|---|---|
| `cfg` | Pin, state machine, DMA and clock configuration (copied). |
| `out` | Card information; may be NULL. |

| Return value | Description |
|---|---|
| `0` | Card ready. |
| `-1` | `cfg` is NULL. |
| `-2` | The card did not leave the busy state during ACMD41. |
| `-3` | CMD2 (ALL_SEND_CID) failed. |
| `-4` | CMD3 (SEND_RELATIVE_ADDR) failed. |
| `-5` | CMD9 (SEND_CSD) failed. |
| `-6` | CMD7 (SELECT_CARD) failed. |
| `-7` | ACMD6 (4-bit bus width) failed. |

### hal_pio_sdh_hw_setup { #hal_pio_sdh_hw_setup }

```c
int hal_pio_sdh_hw_setup(const hal_pio_sdh_cfg_t *cfg);
```

Configure the GLB PIO clock and pin mux, load the CLK/CMD program on the state machine and start it.

Copies `cfg`, selects the 400 kHz identification clock, and sets up the DMA channels when cfg-&gt;use_dma is set. The state machine clocks CLK only while it has bits to shift; CLK stays low when idle. [`hal_pio_sdh_init()`](#hal_pio_sdh_init) calls this; call it directly only to drive the bus by hand with [`hal_pio_sdh_send_cmd()`](#hal_pio_sdh_send_cmd) and [`hal_pio_sdh_clock_burst()`](#hal_pio_sdh_clock_burst).

| Parameter | Description |
|---|---|
| `cfg` | Configuration (copied). |

| Return value | Description |
|---|---|
| `0` | Done. |
| `-1` | `cfg` is NULL. |

### hal_pio_sdh_send_cmd { #hal_pio_sdh_send_cmd }

```c
int hal_pio_sdh_send_cmd(uint8_t cmd, uint32_t arg, uint8_t resp_bits, uint32_t raw[2]);
```

Send one 48-bit command and optionally receive a 48-bit response.

Sends 8 idle clocks first. The response CRC is not checked: use [`sdio_check_r1_crc()`](#sdio_check_r1_crc) for R1/R6/R7 responses (R3 has no CRC). Requires [`hal_pio_sdh_hw_setup()`](#hal_pio_sdh_hw_setup) or [`hal_pio_sdh_init()`](#hal_pio_sdh_init).

| Parameter | Description |
|---|---|
| `cmd` | Command index, 0 to 63. |
| `arg` | 32-bit command argument. |
| `resp_bits` | 48 for R1/R3/R6/R7, 0 for no response. Any other value (such as 136 for R2) sends the command but returns -1 without reading a response. |
| `raw` | For a 48-bit response: raw[0] = first 32 response bits (start bit in bit 31), raw[1] = last 16 bits in bits [15:0]. Not written when `resp_bits` is 0. |

| Return value | Description |
|---|---|
| `0` | Command sent (and response received). |
| `-1` | Transmit timeout, response timeout or unsupported `resp_bits`. |

### hal_pio_sdh_clock_burst { #hal_pio_sdh_clock_burst }

```c
void hal_pio_sdh_clock_burst(uint32_t n);
```

Run n clock cycles with CMD released (&gt;=74 required after card power-up).

CMD is not driven, so the card sees it high through the pull-up. Returns early, silently, if the state machine stops consuming bits.

| Parameter | Description |
|---|---|
| `n` | Number of clock cycles. |

### hal_pio_sdh_read_blocks { #hal_pio_sdh_read_blocks }

```c
int hal_pio_sdh_read_blocks(uint8_t *buf, uint32_t lba, uint32_t count);
```

Read 512-byte blocks from the card.

Uses CMD17 for one block. For several blocks it sends CMD23 and a bounded CMD18 when the card accepts CMD23, otherwise an open-ended CMD18 ended with CMD12. Works with a 1-bit or 4-bit bus, through DMA when cfg-&gt;use_dma was set. Call after [`hal_pio_sdh_init()`](#hal_pio_sdh_init).

| Parameter | Description |
|---|---|
| `buf` | Destination, `count * 512` bytes. |
| `lba` | First block, in 512-byte units (converted to a byte address for SDSC cards). |
| `count` | Number of blocks, at least 1. |

| Return value | Description |
|---|---|
| `0` | Data read. |
| `negative` | `buf` is NULL, `count` is 0, a command failed, or the data phase failed (timeout or CRC error). |

### hal_pio_sdh_write_blocks { #hal_pio_sdh_write_blocks }

```c
int hal_pio_sdh_write_blocks(const uint8_t *buf, uint32_t lba, uint32_t count);
```

Write 512-byte blocks to the card (4-bit bus only).

Uses CMD24 for one block, after which (by default) the card status is polled with CMD13 until the card is back in the transfer state, for at most 500 ms. For several blocks it sends CMD23 and a bounded CMD25 when the card accepts CMD23, otherwise an open-ended CMD25 ended with CMD12, and then waits for the card to finish programming. Call after [`hal_pio_sdh_init()`](#hal_pio_sdh_init).

| Parameter | Description |
|---|---|
| `buf` | Source data, `count * 512` bytes. |
| `lba` | First block, in 512-byte units (converted to a byte address for SDSC cards). |
| `count` | Number of blocks, at least 1. |

| Return value | Description |
|---|---|
| `0` | Data written. |
| `negative` | `buf` is NULL, `count` is 0, the bus is not 4-bit, a command failed, the data phase failed, or the card did not finish programming in time. |

### hal_pio_sdh_set_clock { #hal_pio_sdh_set_clock }

```c
int hal_pio_sdh_set_clock(uint32_t hz);
```

Set the SD clock.

The clock is 24 MHz / N with N = 24 MHz / `hz` rounded down and limited to 1..65535, so it is at most 24 MHz and otherwise not below `hz`. 0 selects the 400 kHz identification clock. Applies to the command and the data phases. Requires [`hal_pio_sdh_hw_setup()`](#hal_pio_sdh_hw_setup) or [`hal_pio_sdh_init()`](#hal_pio_sdh_init); assumes the 96 MHz PIO clock.

| Parameter | Description |
|---|---|
| `hz` | Requested clock in Hz. |

**Returns:** Always 0.

### fatfs_pio_sdh_driver_register { #fatfs_pio_sdh_driver_register }

```c
void fatfs_pio_sdh_driver_register(const hal_pio_sdh_cfg_t *cfg);
```

Register this host as the FatFS disk driver of the `DEV_SD` drive.

Implemented in the FatFS port of the SDK, built when `CONFIG_HAL_PIO_SDH` is enabled. Copies `cfg`; the card is initialized with [`hal_pio_sdh_init()`](#hal_pio_sdh_init) on the first disk initialization, and registering again makes the next access re-initialize it. The hardware SDH FatFS port uses the same `DEV_SD` drive slot; the last registration wins. Failed reads and writes are retried once.

| Parameter | Description |
|---|---|
| `cfg` | Configuration for [`hal_pio_sdh_init()`](#hal_pio_sdh_init) (copied). |

### hal_pio_sdh_set_pad_cfg { #hal_pio_sdh_set_pad_cfg }

```c
int hal_pio_sdh_set_pad_cfg(uint8_t drive, uint8_t pull_up, uint8_t smt);
```

Set drive strength, internal pull-up and Schmitt trigger for all six SD pins.

The setting is sticky: it is stored and re-applied on every later [`hal_pio_sdh_init()`](#hal_pio_sdh_init) / [`hal_pio_sdh_hw_setup()`](#hal_pio_sdh_hw_setup), and applied immediately if the hardware is already set up. Boot defaults: drive strength `CONFIG_HAL_PIO_SDH_PAD_DRIVE` (3 if not set), pull-ups on unless `CONFIG_HAL_PIO_SDH_PULL_NONE` is set, Schmitt trigger on.

| Parameter | Description |
|---|---|
| `drive` | Drive strength 0 to 3; larger values are limited to 3. |
| `pull_up` | Non-zero enables the internal pull-ups. Use 0 with SD adapters that provide external pull-up resistors. |
| `smt` | Non-zero enables the Schmitt trigger inputs. |

**Returns:** Always 0.

### hal_pio_sdh_set_bus_width { #hal_pio_sdh_set_bus_width }

```c
int hal_pio_sdh_set_bus_width(uint8_t width);
```

Switch DATA bus width (1 or 4) via ACMD6; needs an initialized card.

Writes need a 4-bit bus (see [`hal_pio_sdh_write_blocks()`](#hal_pio_sdh_write_blocks)).

| Parameter | Description |
|---|---|
| `width` | 1 or 4. |

| Return value | Description |
|---|---|
| `0` | Width changed. |
| `-1` | `width` is not 1 or 4, or no card is initialized. |
| `-2` | ACMD6 failed. |

### hal_pio_sdh_switch_hs { #hal_pio_sdh_switch_hs }

```c
int hal_pio_sdh_switch_hs(uint8_t *status);
```

Switch the card to High-Speed access mode with CMD6 (SWITCH_FUNC).

Reads the 512-bit switch status and, when the card grants high speed, makes the host sample read data with high-speed timing. The clock is not changed. [`hal_pio_sdh_init()`](#hal_pio_sdh_init) already calls this (best effort). The card must be initialized and in 4-bit mode.

| Parameter | Description |
|---|---|
| `status` | 64-byte buffer for the switch status; may be NULL. |

| Return value | Description |
|---|---|
| `0` | High speed granted. |
| `-1` | The command or the status read failed. |
| `-2` | The card did not grant high speed. |

### hal_pio_sdh_card_status { #hal_pio_sdh_card_status }

```c
int hal_pio_sdh_card_status(uint32_t *status, uint32_t *state);
```

Read the card status with CMD13 (SEND_STATUS).

Read-only: the card state is not changed.

| Parameter | Description |
|---|---|
| `status` | 32-bit R1 card status; may be NULL. |
| `state` | CURRENT_STATE field, bits [12:9] of the status (4 = tran, 5 = data, 6 = rcv, 7 = prg); may be NULL. |

| Return value | Description |
|---|---|
| `0` | Status read. |
| `-1` | No card initialized, no response, or response CRC error. |

### hal_pio_sdh_deinit { #hal_pio_sdh_deinit }

```c
void hal_pio_sdh_deinit(void);
```

Stop the PIO state machine used by the host.

Only the CLK/CMD state machine is disabled; pins, DMA channels and the PIO clock stay configured. Call [`hal_pio_sdh_init()`](#hal_pio_sdh_init) to use the card again.

### hal_pio_sdh_cfg_t { #hal_pio_sdh_cfg_t }

PIO SD host configuration.

Reference pin map: CLK = GPIO22, CMD = GPIO23, DAT0..DAT3 = GPIO24..27. Constraints: DAT0..DAT3 must be 4 contiguous ascending GPIOs, and pin_clk must equal pin_d0 - 2.

| Field | Type | Description |
|---|---|---|
| `pin_clk` | `uint8_t` | CLK GPIO (22 in the reference map); must equal pin_d0 - 2. |
| `pin_cmd` | `uint8_t` | CMD GPIO (23 in the reference map). |
| `pin_d0` | `uint8_t` | DAT0 GPIO (24 in the reference map); DAT1..DAT3 = pin_d0 + 1..3. |
| `sm_cmd` | `uint8_t` | PIO state machine that runs the CLK/CMD and DATA programs (0 in the reference configuration). |
| `sm_dat` | `uint8_t` | PIO state machine reserved for DATA (1 in the reference configuration); not used by the current implementation, which runs the data phase on sm_cmd. |
| `use_dma` | `uint8_t` | 1 = DMA data path, 0 = CPU-paced FIFO. |
| `dma_tx_ch` | `uint8_t` | DMA0 channel pacing the TX FIFO (use_dma). |
| `dma_rx_ch` | `uint8_t` | DMA0 channel draining the RX FIFO (use_dma). |
| `pio_clk_div` | `uint8_t` | GLB PIO clock divider. The driver's SD clock settings assume a 96 MHz PIO clock (pio_clk_sel = 0, pio_clk_div = 0). |
| `pio_clk_sel` | `uint8_t` | GLB PIO clock source select (0 in the reference configuration). |

### hal_pio_sdh_card_t { #hal_pio_sdh_card_t }

Card information returned by [`hal_pio_sdh_init()`](#hal_pio_sdh_init).

| Field | Type | Description |
|---|---|---|
| `block_count` | `uint32_t` | Total 512-byte sectors, computed from the CSD. |
| `block_size` | `uint32_t` | Always 512. |
| `access_mode` | `uint8_t` | 0 = byte addressing (SDSC), 1 = sector (SDHC/SDXC). |
| `bus_width` | `uint8_t` | Data bus width after initialization: 1 or 4 (init selects 4). |
| `cid` | `uint8_t[16]` | Raw CID register, most significant byte first (cid[0] = bits [127:120]). |
| `csd` | `uint8_t[16]` | Raw CSD register, most significant byte first (csd[0] = bits [127:120]). |

## hal_pio_sdh_crc.h { #hal_pio_sdh_crc-h }

`#include "hal_pio_sdh_crc.h"` ([Source](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_pio_sdh_crc.h))

SD command and data checksums (CRC7, 4-line CRC16) and command framing for the PIO SD host ([`hal_pio_sdh.h`](#hal_pio_sdh-h)).

Pure functions without hardware access, kept separate from the PIO driver so that they can be unit-tested on a host computer. The algorithms follow the SD Physical Layer Simplified Specification.

### crc7_byte { #crc7_byte }

```c
uint8_t crc7_byte(uint8_t crc, uint8_t b);
```

Accumulate one byte into a running CRC7 (SD command checksum).

CRC7 with polynomial x^7 + x^3 + 1. Seed with 0 and feed the bytes in transmit order; the result holds CRC7 in bits [7:1], bit[0] = 0, ready to be combined with the end bit.

| Parameter | Description |
|---|---|
| `crc` | Running value from the previous call, 0 for the first byte. |
| `b` | Next byte. |

**Returns:** Updated running value, CRC7 in bits [7:1].

### sdio_crc16_4bit { #sdio_crc16_4bit }

```c
uint64_t sdio_crc16_4bit(const uint32_t *data, uint32_t num_words);
```

CRC16 for the 4 DATA lines in parallel (4-bit bus mode).

Computes the SD data CRC16 (x^16 + x^12 + x^5 + 1) of each of the four lines. Each 32-bit word carries 8 bits per line; the words are read in memory order and byte-swapped, so `data` is the data block as sent on the bus, first byte first.

| Parameter | Description |
|---|---|
| `data` | Data words, 4-byte aligned. |
| `num_words` | Number of 32-bit words (128 for a 512-byte block). |

**Returns:** The four 16-bit lane CRCs packed as 16 nibbles in transmit order: bits [63:60] are the first CRC nibble sent on DAT3..DAT0.

### sdio_make_cmd_words { #sdio_make_cmd_words }

```c
void sdio_make_cmd_words(uint8_t cmd, uint32_t arg, uint8_t resp_bits, uint32_t *w0, uint32_t *w1);
```

Build the two 32-bit words the PIO command program expects for a command: bit-count fields + 48-bit packet (MSB first) + CRC7 + end bit.

Layout: `w0` bits [31:24] = 47 (command length in bits minus one), [23:16] = start bit (0), direction bit (1) and the 6-bit command index, [15:0] = argument bits [31:16]. `w1` bits [31:16] = argument bits [15:0], [15:9] = CRC7, bit 8 = end bit (1), [7:0] = `resp_bits` - 1 (0 when `resp_bits` is 0).

| Parameter | Description |
|---|---|
| `cmd` | Command index, 0 to 63. |
| `arg` | 32-bit command argument. |
| `resp_bits` | Expected response length in bits (48 or 136), or 0 for no response. |
| `w0` | First word. |
| `w1` | Second word. |

### sdio_check_r1_crc { #sdio_check_r1_crc }

```c
int sdio_check_r1_crc(uint32_t resp0, uint32_t resp1);
```

Verify the CRC7 of a 48-bit R1/R6/R7 response.

Not applicable to R3, which carries no CRC.

| Parameter | Description |
|---|---|
| `resp0` | First 32 bits of the response (start bit in bit 31), as returned in raw[0] by [`hal_pio_sdh_send_cmd()`](#hal_pio_sdh_send_cmd). |
| `resp1` | Last 16 bits of the response in bits [15:0] ([15:8] = last payload byte, [7:1] = CRC7, bit 0 = end bit), as returned in raw[1] by [`hal_pio_sdh_send_cmd()`](#hal_pio_sdh_send_cmd). |

| Return value | Description |
|---|---|
| `0` | The CRC matches. |
| `-1` | The CRC does not match. |
