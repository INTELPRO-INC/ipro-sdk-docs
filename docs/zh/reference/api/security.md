---
title: 安全引擎
description: AES、GMAC、雜湊、DSA、ECDSA、P-256 與硬體亂數。
generated: tools/gen_api.py
migrate_from: []
---

# 安全引擎

AES、GMAC、雜湊、DSA、ECDSA、P-256 與硬體亂數。說明取自標頭檔註解（英文）。

| 標頭 | 函式 | 說明 |
|---|---|---|
| [`hal_sec_common.h`](#hal_sec_common-h) | 3 | Security engine bring-up, SHA context layouts and the critical section used by the security-engine helpers. |
| [`hal_sec_hw_common.h`](#hal_sec_hw_common-h) | 0 | Security-engine driver includes and capability flags shared by the security HAL sources. |
| [`hal_sec_aes.h`](#hal_sec_aes-h) | 6 | AES-128/192/256 in ECB, CBC and CTR mode on the security engine. |
| [`hal_sec_gmac.h`](#hal_sec_gmac-h) | 6 | GHASH (the GF(2^128) hash used by AES-GCM and GMAC) on the security engine. |
| [`hal_sec_hash.h`](#hal_sec_hash-h) | 5 | SHA-1, SHA-224, SHA-256, SHA-384 and SHA-512 on the security engine. |
| [`hal_sec_dsa.h`](#hal_sec_dsa-h) | 6 | RSA modular exponentiation, CRT signing and verification on the public-key accelerator (PKA). |
| [`hal_sec_ecdsa.h`](#hal_sec_ecdsa-h) | 14 | ECDSA and ECDH on 256-bit curves using the public-key accelerator (PKA), plus direct access to the TRNG. |
| [`hal_sec_p256.h`](#hal_sec_p256-h) | 4 | NIST P-256 point doubling and mixed addition on the public-key accelerator (PKA), as building blocks for a scalar multiplication. |
| [`hal_sec_trng.h`](#hal_sec_trng-h) | 5 | Random numbers from the security engine's true random number generator (TRNG), and ring-oscillator frequency measurement. |

## hal_sec_common.h { #hal_sec_common-h }

`#include "hal_sec_common.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_common.h)）

Security engine bring-up, SHA context layouts and the critical section used by the security-engine helpers.

Call [`hal_sec_common_init()`](#hal_sec_common_init) once at start-up, before the random-number functions in [`hal_sec_trng.h`](#hal_sec_trng-h) are used.

The critical-section helpers [`hal_sec_enter_critical()`](#hal_sec_enter_critical) and [`hal_sec_exit_critical()`](#hal_sec_exit_critical) depend on the build. When `CONFIG_FREERTOS` or `CONFIG_FREERTOS_SUPPORT` is defined they use the FreeRTOS kernel critical section (`taskENTER_CRITICAL()` / `taskEXIT_CRITICAL()`), so this header then includes `FreeRTOS.h` and `task.h`. In any other build (bare metal, Zephyr) they save the global interrupt enable, disable interrupts and restore the saved state (`__irq_save()` / `__irq_restore()` from `system_soc.h`).

For hashing use the API in [`hal_sec_hash.h`](#hal_sec_hash-h); no function in the SDK takes the SHA context types declared here.

### hal_sec_common_init { #hal_sec_common_init }

```c
int hal_sec_common_init(void);
```

Initialise the security-engine blocks the platform needs.

Currently this initialises the TRNG and is equivalent to [`hal_sec_trng_init()`](#hal_sec_trng_init). The random-number functions in [`hal_sec_trng.h`](#hal_sec_trng-h), and the Wi-Fi supplicant that draws its handshake nonces from them, require it.

**回傳值**：0 (the TRNG initialisation always reports success).

!!! note "注意"
    Compiled into the HAL for FreeRTOS and Zephyr builds only.

### hal_sec_enter_critical { #hal_sec_enter_critical }

```c
unsigned long hal_sec_enter_critical(void);
```

Enter the critical section that protects shared security-engine state.

FreeRTOS build: calls `taskENTER_CRITICAL()`, which masks interrupts up to the kernel's system-call priority and nests. Interrupts above that priority keep running.

**回傳值**：Value to pass to [`hal_sec_exit_critical()`](#hal_sec_exit_critical) (always 0 in this build).

!!! warning "警告"
    Task context only; the FreeRTOS critical section must not be entered from an interrupt handler.

### hal_sec_exit_critical { #hal_sec_exit_critical }

```c
void hal_sec_exit_critical(unsigned long prev_level);
```

Leave the critical section entered with [`hal_sec_enter_critical()`](#hal_sec_enter_critical).

FreeRTOS build: calls `taskEXIT_CRITICAL()`.

| 參數 | 說明 |
|---|---|
| `prev_level` | Value returned by the matching [`hal_sec_enter_critical()`](#hal_sec_enter_critical) call (ignored in this build). |

### hal_sha_type_t { #hal_sha_type_t }

Hash algorithm identifiers stored in the SHA context types below.

The hash API in [`hal_sec_hash.h`](#hal_sec_hash-h) uses enum [`sec_hash_type`](#sec_hash_type) instead.

| 名稱 | 值 | 說明 |
|---|---|---|
| `HAL_SHA1` |  | SHA-1 (20-byte digest). |
| `HAL_SHA224` |  | SHA-224 (28-byte digest). |
| `HAL_SHA256` |  | SHA-256 (32-byte digest). |
| `HAL_MD5` |  | MD5 (16-byte digest). |
| `HAL_SHA384` |  | SHA-384 (48-byte digest). |
| `HAL_SHA512` |  | SHA-512 (64-byte digest). |

### hal_SEC_Eng_SHA256_Link_Ctx { #hal_SEC_Eng_SHA256_Link_Ctx }

Link-mode running state for SHA-1, SHA-224 and SHA-256.

Same layout as the security-engine driver's SHA-256 link context.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `total` | `uint32_t[2]` | Number of message bytes processed (low word, high word). |
| `shaBuf` | `uint32_t *` | Buffer holding input bytes not yet processed (64 bytes). |
| `shaPadding` | `uint32_t *` | Buffer holding the padding block (64 bytes). |
| `linkAddr` | `uint32_t` | Address of the link configuration the engine reads. |

### hal_SEC_Eng_SHA_Link_Config_Type { #hal_SEC_Eng_SHA_Link_Config_Type }

Link configuration read by the SHA engine, used for every SHA variant.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `shaCfgWord` | `uint32_t` | Control word: SHA mode, hash select, block count. |
| `shaSrcAddr` | `uint32_t` | Message source address. |
| `result` | `uint32_t[16]` | Intermediate or final hash value (64 bytes). |

### hal_sha_ctx_t { #hal_sha_ctx_t }

Complete SHA-1/SHA-224/SHA-256 context with its working buffers.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `guard0_` | `uint32_t[7]` | Padding that keeps the fields below off the previous cache line. |
| `type` | `hal_sha_type_t` | Algorithm, one of [`hal_sha_type_t`](#hal_sha_type_t). |
| `ctx` | `hal_SEC_Eng_SHA256_Link_Ctx` | Running state. |
| `link_cfg` | `hal_SEC_Eng_SHA_Link_Config_Type` | Link configuration read by the engine. |
| `tmp` | `uint32_t[16]` | Storage for unprocessed input (64 bytes). |
| `pad` | `uint32_t[16]` | Storage for the padding block (64 bytes). |
| `guard1_` | `uint32_t[7]` | Padding that keeps the fields above off the next cache line. |

### hal_SEC_Eng_SHA512_Link_Ctx { #hal_SEC_Eng_SHA512_Link_Ctx }

Link-mode running state for SHA-384 and SHA-512.

Same layout as the security-engine driver's SHA-512 link context.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `total` | `uint64_t[2]` | Number of message bytes processed (low word, high word). |
| `shaBuf` | `uint64_t *` | Buffer holding input bytes not yet processed (128 bytes). |
| `shaPadding` | `uint64_t *` | Buffer holding the padding block (128 bytes). |
| `linkAddr` | `uint32_t` | Address of the link configuration the engine reads. |

### hal_sha512_ctx_t { #hal_sha512_ctx_t }

Complete SHA-384/SHA-512 context with its working buffers.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `guard0_` | `uint32_t[7]` | Padding that keeps the fields below off the previous cache line. |
| `type` | `hal_sha_type_t` | Algorithm, one of [`hal_sha_type_t`](#hal_sha_type_t). |
| `ctx` | `hal_SEC_Eng_SHA512_Link_Ctx` | Running state. |
| `link_cfg` | `hal_SEC_Eng_SHA_Link_Config_Type` | Link configuration read by the engine. |
| `tmp` | `uint64_t[16]` | Storage for unprocessed input (128 bytes). |
| `pad` | `uint64_t[16]` | Storage for the padding block (128 bytes). |
| `guard1_` | `uint32_t[7]` | Padding that keeps the fields above off the next cache line. |

## hal_sec_hw_common.h { #hal_sec_hw_common-h }

`#include "hal_sec_hw_common.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_hw_common.h)）

Security-engine driver includes and capability flags shared by the security HAL sources.

Pulls in the GLB and security-engine driver headers (`drv_glb.h`, `drv_sec_eng.h`).

### 巨集 { #hal_sec_hw_common-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `SHA512_CAPABLE` |  | Defined when the security engine supports SHA-384 and SHA-512. |

## hal_sec_aes.h { #hal_sec_aes-h }

`#include "hal_sec_aes.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_aes.h)）

AES-128/192/256 in ECB, CBC and CTR mode on the security engine.

Typical sequence: [`sec_aes_init()`](#sec_aes_init) or [`sec_aes_init_ex()`](#sec_aes_init_ex), [`sec_aes_setkey()`](#sec_aes_setkey), one or more [`sec_aes_encrypt()`](#sec_aes_encrypt) / [`sec_aes_decrypt()`](#sec_aes_decrypt) calls, [`sec_aes_deinit()`](#sec_aes_deinit).

Keys, IVs and counter blocks are plain byte arrays in the order defined by FIPS-197 and SP 800-38A (byte 0 first); the HAL programs the engine in big-endian mode. Data is processed in 16-byte blocks.

All calls are blocking: the CPU polls the engine until the operation ends. The HAL takes no lock and every handle drives the same AES engine, so callers in different tasks must serialise their use of it.

### sec_aes_init { #sec_aes_init }

```c
int sec_aes_init(sec_aes_handle_t *handle, sec_aes_type aes_type, sec_aes_key_type key_type);
```

Initialise an AES handle in link mode.

Same as [`sec_aes_init_ex()`](#sec_aes_init_ex) with [`SEC_MODE_LINK`](#sec_mode_t).

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `aes_type` | Block cipher mode ([`SEC_AES_CBC`](#sec_aes_type), [`SEC_AES_CTR`](#sec_aes_type) or [`SEC_AES_ECB`](#sec_aes_type)). |
| `key_type` | Key length ([`SEC_AES_KEY_128`](#sec_aes_key_type), [`SEC_AES_KEY_192`](#sec_aes_key_type) or [`SEC_AES_KEY_256`](#sec_aes_key_type)). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_aes_init_ex { #sec_aes_init_ex }

```c
int sec_aes_init_ex(sec_aes_handle_t *handle, sec_mode_t mode, sec_aes_type aes_type, sec_aes_key_type key_type);
```

Initialise an AES handle in the given operation mode.

Direct mode switches the engine out of link mode. Link mode clears the handle's link configuration and stores the cipher mode and key length in it. No key is loaded yet; call [`sec_aes_setkey()`](#sec_aes_setkey) next.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `mode` | [`SEC_MODE_DIRECT`](#sec_mode_t) or [`SEC_MODE_LINK`](#sec_mode_t). |
| `aes_type` | Block cipher mode ([`SEC_AES_CBC`](#sec_aes_type), [`SEC_AES_CTR`](#sec_aes_type) or [`SEC_AES_ECB`](#sec_aes_type)). |
| `key_type` | Key length ([`SEC_AES_KEY_128`](#sec_aes_key_type), [`SEC_AES_KEY_192`](#sec_aes_key_type) or [`SEC_AES_KEY_256`](#sec_aes_key_type)). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_aes_setkey { #sec_aes_setkey }

```c
int sec_aes_setkey(sec_aes_handle_t *handle, const uint8_t *key, uint8_t key_len, const uint8_t *nonce, uint8_t dir);
```

Load the key and IV and select the direction.

The direction chosen here applies to every following [`sec_aes_encrypt()`](#sec_aes_encrypt) and [`sec_aes_decrypt()`](#sec_aes_decrypt) call on the handle.

| 參數 | 說明 |
|---|---|
| `handle` | Handle initialised with [`sec_aes_init()`](#sec_aes_init) or [`sec_aes_init_ex()`](#sec_aes_init_ex). |
| `key` | Key bytes. Link mode: NULL (or `key_len` 0) selects the hardware key. Direct mode with `key_len` 0: the hardware key is used and the byte at `key` is read as the hardware key selector, so `key` must not be NULL. |
| `key_len` | Key length in bytes: 16, 24 or 32, matching the key length given at init; 0 selects the hardware key. In direct mode only zero versus non-zero matters (the length comes from the init key length). |
| `nonce` | 16-byte IV (CBC) or initial counter block (CTR). Link mode: NULL keeps the IV already in the handle. Direct mode: 16 bytes are always read, so pass a valid buffer even for ECB. |
| `dir` | [`SEC_AES_DIR_ENCRYPT`](#sec_aes_dir_type) or [`SEC_AES_DIR_DECRYPT`](#sec_aes_dir_type). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_aes_encrypt { #sec_aes_encrypt }

```c
int sec_aes_encrypt(sec_aes_handle_t *handle, const uint8_t *in, uint32_t len, size_t offset, uint8_t *out);
```

Run the AES operation on `len` bytes.

Despite its name this runs the direction selected with [`sec_aes_setkey()`](#sec_aes_setkey); [`sec_aes_encrypt()`](#sec_aes_encrypt) and [`sec_aes_decrypt()`](#sec_aes_decrypt) perform the same operation.

The HAL cleans the data cache over `in` and cleans and invalidates it over `out` before and after the engine's DMA, so both buffers may be cacheable. Prefer an `out` buffer aligned to the 32-byte cache line and a `len` that covers whole lines: data that shares a cache line with `out` and is written by another task or an interrupt during the call can be lost.

| 參數 | 說明 |
|---|---|
| `handle` | Handle with a key loaded by [`sec_aes_setkey()`](#sec_aes_setkey). |
| `in` | Input data. |
| `len` | Length in bytes; must be a multiple of 16. |
| `offset` | Ignored. |
| `out` | Output buffer of `len` bytes. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | NULL argument, `len` not a multiple of 16, or engine error or timeout. |

### sec_aes_decrypt { #sec_aes_decrypt }

```c
int sec_aes_decrypt(sec_aes_handle_t *handle, const uint8_t *in, uint32_t len, size_t offset, uint8_t *out);
```

Run the AES operation on `len` bytes.

Identical to [`sec_aes_encrypt()`](#sec_aes_encrypt): the direction is the one selected with [`sec_aes_setkey()`](#sec_aes_setkey), not the function name.

| 參數 | 說明 |
|---|---|
| `handle` | Handle with a key loaded by [`sec_aes_setkey()`](#sec_aes_setkey). |
| `in` | Input data. |
| `len` | Length in bytes; must be a multiple of 16. |
| `offset` | Ignored. |
| `out` | Output buffer of `len` bytes (same alignment advice as [`sec_aes_encrypt()`](#sec_aes_encrypt)). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | NULL argument, `len` not a multiple of 16, or engine error or timeout. |

### sec_aes_deinit { #sec_aes_deinit }

```c
int sec_aes_deinit(sec_aes_handle_t *handle);
```

Release an AES handle.

In direct mode the engine's enable, key-select and IV-select bits are cleared. The whole handle, including any key copy, is then zeroed.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to release. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_mode_t { #sec_mode_t }

Security engine operation mode.

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_MODE_DIRECT` | `0` | Direct mode: the CPU programs the engine registers. |
| `SEC_MODE_LINK` |  | Link mode: the engine reads its configuration from the handle by DMA. |

### sec_aes_type { #sec_aes_type }

AES block cipher mode.

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_AES_CBC` |  | Cipher block chaining; the IV is the 16-byte `nonce` of [`sec_aes_setkey()`](#sec_aes_setkey). |
| `SEC_AES_CTR` |  | Counter mode; the initial 16-byte counter block is the `nonce` of [`sec_aes_setkey()`](#sec_aes_setkey). |
| `SEC_AES_ECB` |  | Electronic codebook; no IV. |

### sec_aes_key_type { #sec_aes_key_type }

AES key length.

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_AES_KEY_128` |  | 128-bit key (16 bytes). |
| `SEC_AES_KEY_256` |  | 256-bit key (32 bytes). |
| `SEC_AES_KEY_192` |  | 192-bit key (24 bytes). |

### sec_aes_dir_type { #sec_aes_dir_type }

AES direction.

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_AES_DIR_ENCRYPT` |  | Encrypt. Also use this for CTR mode in both directions. |
| `SEC_AES_DIR_DECRYPT` |  | Decrypt (ECB and CBC). |

### sec_aes_handle_t { #sec_aes_handle_t }

AES handle for both direct and link mode.

The caller provides the storage (static or stack); the HAL keeps no pointer to it between calls. In link mode the HAL accesses `link_cfg` through its non-cacheable alias ([`hal_get_noncacheable_addr()`](platform.md#hal_get_noncacheable_addr)), so the handle itself may live in cacheable RAM.

Layout: offset 0 holds mode/aes_type/key_type/dir (16 bytes, CPU-only), offset 16 holds 48 bytes of padding (`guard0`) and `link_cfg` starts at offset 64. Place the handle on a 64-byte boundary (for example with `__attribute__((aligned(64)))`) so that `link_cfg` never shares a cache line with the CPU-written fields.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `mode` | `sec_mode_t` | Operation mode: direct or link. |
| `aes_type` | `sec_aes_type` | AES mode: CBC/CTR/ECB. |
| `key_type` | `sec_aes_key_type` | Key length: 128/192/256 bits. |
| `dir` | `sec_aes_dir_type` | Direction: encrypt/decrypt. |
| `@337134303055204251124131112137327142034132264230` | `union sec_aes_handle_t::@302144027160267067200221114352343215114316221137` |  |

## hal_sec_gmac.h { #hal_sec_gmac-h }

`#include "hal_sec_gmac.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_gmac.h)）

GHASH (the GF(2^128) hash used by AES-GCM and GMAC) on the security engine.

The engine computes GHASH with a 16-byte hash subkey H; for AES-GCM, H = AES-K(0^128), which the caller computes (for example with [`hal_sec_aes.h`](#hal_sec_aes-h) in ECB mode). Typical sequence: [`sec_gmac_init()`](#sec_gmac_init) once, [`sec_gmac_start()`](#sec_gmac_start), [`sec_gmac_clear()`](#sec_gmac_clear), [`sec_gmac_update()`](#sec_gmac_update) for the AAD, the ciphertext and finally the 16-byte length block, [`sec_gmac_finish()`](#sec_gmac_finish), [`sec_gmac_deinit()`](#sec_gmac_deinit). The caller XORs the result with E(K, J0) to form a GCM tag. All byte strings are in GCM order (byte 0 first).

Calls are blocking (the CPU polls the engine). The HAL takes no lock; callers in different tasks must serialise their use of the engine.

### sec_gmac_init { #sec_gmac_init }

```c
int sec_gmac_init(void);
```

Put the GHASH engine in big-endian link mode.

Call once before any other function in this file. Calling it again is harmless.

**回傳值**：0 (always).

### sec_gmac_start { #sec_gmac_start }

```c
int sec_gmac_start(sec_gmac_handle_t *handle, const uint8_t key[16]);
```

Clear a handle and load the hash subkey.

The running GHASH value is cleared as well.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to set up. |
| `key` | 16-byte hash subkey H. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` or `key` is NULL. |

### sec_gmac_clear { #sec_gmac_clear }

```c
int sec_gmac_clear(sec_gmac_handle_t *handle);
```

Reset the running GHASH value to zero, keeping the hash subkey.

Use it to start a new message with the same subkey.

| 參數 | 說明 |
|---|---|
| `handle` | Handle set up with [`sec_gmac_start()`](#sec_gmac_start). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_gmac_update { #sec_gmac_update }

```c
int sec_gmac_update(sec_gmac_handle_t *handle, const uint8_t *input, uint32_t input_len);
```

Absorb data into the running GHASH value.

Whole 16-byte blocks are processed directly from `input`; a trailing partial block is zero-padded to 16 bytes and processed too. Because of this padding only the last update of each GCM field (AAD or ciphertext) may have a length that is not a multiple of 16.

The HAL cleans the data cache over `input`, so it may be cacheable.

| 參數 | 說明 |
|---|---|
| `handle` | Handle set up with [`sec_gmac_start()`](#sec_gmac_start). |
| `input` | Data to absorb. |
| `input_len` | Length in bytes; must be below 1 MiB (16 * 65536). 0 does nothing. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL, `input_len` is too large, or engine error or timeout. |

### sec_gmac_finish { #sec_gmac_finish }

```c
int sec_gmac_finish(sec_gmac_handle_t *handle, uint8_t result[16]);
```

Read the running GHASH value.

The value is copied as is; append the GCM length block with [`sec_gmac_update()`](#sec_gmac_update) before calling this. The handle is not changed.

| 參數 | 說明 |
|---|---|
| `handle` | Handle set up with [`sec_gmac_start()`](#sec_gmac_start). |
| `result` | 16-byte output buffer. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` or `result` is NULL. |

### sec_gmac_deinit { #sec_gmac_deinit }

```c
int sec_gmac_deinit(sec_gmac_handle_t *handle);
```

Erase a handle's link configuration, including the hash subkey.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to erase. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_gmac_handle_t { #sec_gmac_handle_t }

GHASH handle (link mode only).

The caller provides the storage. The HAL accesses `link_cfg` and `tmp_buf` through their non-cacheable aliases ([`hal_get_noncacheable_addr()`](platform.md#hal_get_noncacheable_addr)), so the handle may live in cacheable RAM; place it on a 32-byte boundary so that `link_cfg` does not share a cache line with other data.

!!! note "注意"
    Do not write the handle through its cacheable address while it is in use, for example by clearing it with memset() right before [`sec_gmac_start()`](#sec_gmac_start): a dirty cache line written back later overwrites the engine state. [`sec_gmac_start()`](#sec_gmac_start) clears the link configuration itself.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `guard0` | `uint32_t[8]` | Cache line guard. |
| `link_cfg` | `SEC_Eng_GMAC_Link_Config_Type` | Link configuration: hash subkey and running GHASH value. |
| `guard1` | `uint32_t[8]` | Cache line guard. |
| `tmp_buf` | `uint8_t[16]` | Zero-padded copy of a trailing partial block. |

## hal_sec_hash.h { #hal_sec_hash-h }

`#include "hal_sec_hash.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_hash.h)）

SHA-1, SHA-224, SHA-256, SHA-384 and SHA-512 on the security engine.

Typical sequence: [`sec_hash_init()`](#sec_hash_init) or [`sec_hash_init_ex()`](#sec_hash_init_ex), any number of [`sec_hash_update()`](#sec_hash_update) calls, [`sec_hash_finish()`](#sec_hash_finish), [`sec_hash_deinit()`](#sec_hash_deinit). The digest is written in the standard FIPS 180-4 byte order.

Calls are blocking (the CPU polls the engine). The HAL takes no lock and all handles use the same SHA engine, so callers in different tasks must serialise each call. In link mode every handle carries its own intermediate state, so several link-mode hashes can be in progress at the same time; in direct mode the intermediate state is held by the engine, so only one direct-mode hash can be in progress.

### sec_hash_init { #sec_hash_init }

```c
int sec_hash_init(sec_hash_handle_t *handle, uint8_t type);
```

Start a hash in link mode.

Same as [`sec_hash_init_ex()`](#sec_hash_init_ex) with [`SEC_HASH_MODE_LINK`](#sec_hash_mode_t).

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `type` | Algorithm, a value of enum [`sec_hash_type`](#sec_hash_type). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL or `type` is not a valid algorithm. |

### sec_hash_init_ex { #sec_hash_init_ex }

```c
int sec_hash_init_ex(sec_hash_handle_t *handle, sec_hash_mode_t mode, uint8_t type);
```

Start a hash in the given operation mode.

Clears the whole handle, then prepares the engine (direct mode) or the handle's link configuration (link mode) for `type`.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `mode` | [`SEC_HASH_MODE_DIRECT`](#sec_hash_mode_t) or [`SEC_HASH_MODE_LINK`](#sec_hash_mode_t). |
| `type` | Algorithm, a value of enum [`sec_hash_type`](#sec_hash_type). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL or `type` is not a valid algorithm. |

### sec_hash_deinit { #sec_hash_deinit }

```c
int sec_hash_deinit(sec_hash_handle_t *handle);
```

Erase the handle's data buffers.

Zeroes `shaBuf` and `shaPadding` through both their cacheable and non-cacheable addresses. The engine itself is not touched.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to erase. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `handle` is NULL. |

### sec_hash_update { #sec_hash_update }

```c
int sec_hash_update(sec_hash_handle_t *handle, const void *buffer, uint32_t size);
```

Add data to the hash.

The HAL cleans the data cache over `buffer` before the engine reads it, so the buffer may be cacheable.

| 參數 | 說明 |
|---|---|
| `handle` | Handle started with [`sec_hash_init()`](#sec_hash_init) or [`sec_hash_init_ex()`](#sec_hash_init_ex). |
| `buffer` | Data to hash. |
| `size` | Data size in bytes; must not be 0. |

| 回傳碼 | 說明 |
|---|---|
| `0` | The data was passed to the engine. Engine timeouts are not reported. |
| `-1` | `handle` or `buffer` is NULL, or `size` is 0. |

### sec_hash_finish { #sec_hash_finish }

```c
int sec_hash_finish(sec_hash_handle_t *handle, void *buffer);
```

Pad the message and read the digest.

| 參數 | 說明 |
|---|---|
| `handle` | Handle started with [`sec_hash_init()`](#sec_hash_init) or [`sec_hash_init_ex()`](#sec_hash_init_ex). |
| `buffer` | Digest output; must hold the digest length of the algorithm (20, 28, 32, 48 or 64 bytes). The CPU writes it, so it may be cacheable. |

**回傳值**：Digest length in bytes (20, 28, 32, 48 or 64) on success, or -1 if `handle` or `buffer` is NULL or the handle holds an invalid algorithm. Engine timeouts are not reported.

### sec_hash_mode_t { #sec_hash_mode_t }

Hash engine operation mode.

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_HASH_MODE_DIRECT` | `0` | Direct mode: the CPU programs the engine registers. |
| `SEC_HASH_MODE_LINK` |  | Link mode: the engine reads its configuration from the handle by DMA. |

### sec_hash_type { #sec_hash_type }

Hash algorithm, passed as the `type` argument of [`sec_hash_init()`](#sec_hash_init).

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_HASH_SHA1` |  | SHA-1, 20-byte digest. |
| `SEC_HASH_SHA224` |  | SHA-224, 28-byte digest. |
| `SEC_HASH_SHA256` |  | SHA-256, 32-byte digest. |
| `SEC_HASH_SHA384` |  | SHA-384, 48-byte digest. |
| `SEC_HASH_SHA512` |  | SHA-512, 64-byte digest. |
| `SEC_HASH_UNKNOWN` |  | Number of algorithms; not a valid algorithm. |

### sec_hash_handle_t { #sec_hash_handle_t }

Hash handle for both direct and link mode.

The caller provides the storage. The HAL accesses the buffers the engine reads (`shaBuf`, `shaPadding` and the link configuration) through their non-cacheable aliases ([`hal_get_noncacheable_addr()`](platform.md#hal_get_noncacheable_addr)) and performs the cache maintenance itself, so the handle may live in cacheable RAM. Buffer sizes fit SHA-512, the largest block size (128 bytes).

The running context stores pointers into the handle, so a handle must not be moved or copied with memcpy() while a hash is in progress.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `mode` | `sec_hash_mode_t` | Operation mode: direct or link. |
| `type` | `uint8_t` | Algorithm, a value of enum [`sec_hash_type`](#sec_hash_type). |
| `shaBuf` | `uint64_t[16]` | Input bytes not yet processed (128 bytes, enough for SHA-512). |
| `shaPadding` | `uint64_t[16]` | Padding block (128 bytes, enough for SHA-512). |
| `@240157250356373000360224130104241075121055366210` | `union sec_hash_handle_t::@212112352314241244032265365042031211271327020041` |  |

### 巨集 { #hal_sec_hash-h-macros }

| 名稱 | 值 | 說明 |
|---|---|---|
| `SEC_MODE_DEFINED` |  | Defined once [`sec_hash_mode_t`](#sec_hash_mode_t) has been declared. |

## hal_sec_dsa.h { #hal_sec_dsa-h }

`#include "hal_sec_dsa.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_dsa.h)）

RSA modular exponentiation, CRT signing and verification on the public-key accelerator (PKA).

Despite the `dsa` prefix these functions implement raw RSA: no padding scheme is applied or checked; the caller encodes and parses the padding.

Big numbers are unsigned integers stored as big-endian byte strings (most significant byte first) in 4-byte aligned `uint32_t` buffers. A number of `size` bits occupies `size / 32` words. Supported operand sizes are 64, 128, 256, 512, 768, 1024, 1536 and 2048 bits; the RSA modulus can be up to 2048 bits.

Calls are blocking. The HAL takes no lock and the PKA is shared with the ECC functions ([`hal_sec_ecdsa.h`](#hal_sec_ecdsa-h), [`hal_sec_p256.h`](#hal_sec_p256-h)); serialise access with the other users. The SDK's mbedTLS hardware port takes `ipro_sec_pka_mutex_take()` / `ipro_sec_pka_mutex_give()` around its PKA calls.

### sec_dsa_init { #sec_dsa_init }

```c
int sec_dsa_init(sec_dsa_handle_t *handle, uint32_t size);
```

Reset the PKA and initialise an RSA handle.

Resets the PKA, selects big-endian operand order and zeroes `handle`.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `size` | Modulus length in bits (up to 2048). |

**回傳值**：0 (always).

### sec_dsa_mexp_binary { #sec_dsa_mexp_binary }

```c
int sec_dsa_mexp_binary(uint32_t size, const uint32_t *a, const uint32_t *b, const uint32_t *c, uint32_t *r);
```

Compute r = a^b mod c with square-and-multiply on the PKA.

The PKA must already be reset and in big-endian mode: call [`sec_dsa_init()`](#sec_dsa_init), or `Sec_Eng_PKA_Reset()` followed by `Sec_Eng_PKA_BigEndian_Enable()`.

| 參數 | 說明 |
|---|---|
| `size` | Operand size in bits (64, 128, 256, 512, 768, 1024, 1536 or 2048). |
| `a` | Base, `size` bits. |
| `b` | Exponent, `size` bits. |
| `c` | Modulus, `size` bits. |
| `r` | Result, `size` bits. |

**回傳值**：0 (always).

!!! warning "警告"
    The most significant byte of `b` must be zero; with a non-zero top byte the exponent loop does not terminate.

### sec_dsa_mexp_mont { #sec_dsa_mexp_mont }

```c
int sec_dsa_mexp_mont(uint32_t size, uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *invR_c, uint32_t *primeN_c, uint32_t *r);
```

Compute r = a^b mod c with the PKA's Montgomery exponentiation.

The PKA must already be reset and in big-endian mode (see [`sec_dsa_mexp_binary()`](#sec_dsa_mexp_binary)). With R = 2^size the caller supplies the Montgomery constants.

| 參數 | 說明 |
|---|---|
| `size` | Operand size in bits (64 to 1536; see the warning). |
| `a` | Base, `size` bits. |
| `b` | Exponent, `size` bits. |
| `c` | Modulus, `size` bits; must be odd. |
| `invR_c` | R^-1 mod c, `size` bits. |
| `primeN_c` | -c^-1 mod R, `size` bits. |
| `r` | Result, `size` bits. |

**回傳值**：0 (always).

!!! warning "警告"
    At `size` 2048 the PKA returns an all-zero result; use [`sec_dsa_mexp_binary()`](#sec_dsa_mexp_binary) for 2048-bit operands.

### sec_dsa_decrypt_crt { #sec_dsa_decrypt_crt }

```c
int sec_dsa_decrypt_crt(uint32_t size, uint32_t *c, sec_dsa_crt_cfg_t *crtCfg, uint32_t *d, uint32_t *r);
```

Compute r = c^d mod (p * q) with the Chinese remainder theorem.

Runs two [`sec_dsa_mexp_mont()`](#sec_dsa_mexp_mont) exponentiations, modulo `p` and modulo `q`, and recombines them. The PKA must already be reset and in big-endian mode.

| 參數 | 說明 |
|---|---|
| `size` | Prime length in bits (half the modulus length, at most 1024). |
| `c` | Input value, `size` bits. |
| `crtCfg` | CRT private key; every value is `size` bits. |
| `d` | Not used. |
| `r` | Result, 2 * `size` bits. |

**回傳值**：0 (always).

### sec_dsa_sign { #sec_dsa_sign }

```c
int sec_dsa_sign(sec_dsa_handle_t *handle, const uint32_t *hash, uint32_t hashLenInWord, uint32_t *s);
```

Raw RSA signature s = hash^d mod n, computed with the CRT key.

Resets the PKA, places `hash` in the least significant words of a `size / 2`-bit zero buffer and runs [`sec_dsa_decrypt_crt()`](#sec_dsa_decrypt_crt) with `handle->crtCfg`.

| 參數 | 說明 |
|---|---|
| `handle` | Handle with `size` and `crtCfg` set. |
| `hash` | Message representative, big-endian, `hashLenInWord` words. |
| `hashLenInWord` | Length of `hash` in 32-bit words; at most `size / 64`. |
| `s` | Signature, `size` bits (`size / 32` words). |

**回傳值**：0 (always).

### sec_dsa_verify { #sec_dsa_verify }

```c
int sec_dsa_verify(sec_dsa_handle_t *handle, const uint32_t *hash, uint32_t hashLenInWord, const uint32_t *s);
```

Verify a raw RSA signature by computing s^e mod n.

Resets the PKA, computes s^e mod n with [`sec_dsa_mexp_binary()`](#sec_dsa_mexp_binary) and compares the least significant `hashLenInWord` words of the result with `hash`. The remaining, more significant words (the padding) are not checked.

| 參數 | 說明 |
|---|---|
| `handle` | Handle with `size`, `n` and `e` set. Because `e` is the exponent of [`sec_dsa_mexp_binary()`](#sec_dsa_mexp_binary), its most significant byte must be zero (true for usual public exponents such as 65537). |
| `hash` | Expected value, big-endian, `hashLenInWord` words. |
| `hashLenInWord` | Length of `hash` in 32-bit words. |
| `s` | Signature, `size` bits. |

| 回傳碼 | 說明 |
|---|---|
| `0` | The low words of s^e mod n equal `hash`. |
| `-1` | Mismatch. |

### sec_dsa_crt_cfg_t { #sec_dsa_crt_cfg_t }

RSA private key in Chinese-remainder-theorem form.

Every value is a big-endian number of `size / 2` bits, where `size` is the modulus length given to [`sec_dsa_init()`](#sec_dsa_init). R denotes 2^(size / 2).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `dP` | `uint32_t *` | d mod (p - 1). |
| `dQ` | `uint32_t *` | d mod (q - 1). |
| `qInv` | `uint32_t *` | q^-1 mod p. |
| `p` | `uint32_t *` | First prime factor p. |
| `invR_p` | `uint32_t *` | R^-1 mod p (Montgomery constant). |
| `primeN_p` | `uint32_t *` | -p^-1 mod R (Montgomery constant). |
| `q` | `uint32_t *` | Second prime factor q. |
| `invR_q` | `uint32_t *` | R^-1 mod q (Montgomery constant). |
| `primeN_q` | `uint32_t *` | -q^-1 mod R (Montgomery constant). |

### sec_dsa_handle_t { #sec_dsa_handle_t }

RSA key handle.

[`sec_dsa_init()`](#sec_dsa_init) zeroes the handle and sets `size` and `crtSize`; the caller then points the key fields at its own buffers.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `size` | `uint32_t` | Modulus length in bits. |
| `crtSize` | `uint32_t` | Prime length in bits (`size` / 2). |
| `n` | `uint32_t *` | Modulus n (`size` bits); used by [`sec_dsa_verify()`](#sec_dsa_verify). |
| `e` | `uint32_t *` | Public exponent (`size` bits); used by [`sec_dsa_verify()`](#sec_dsa_verify). |
| `d` | `uint32_t *` | Private exponent; not used by the current implementation. |
| `crtCfg` | `sec_dsa_crt_cfg_t` | CRT private key; used by [`sec_dsa_sign()`](#sec_dsa_sign). |

## hal_sec_ecdsa.h { #hal_sec_ecdsa-h }

`#include "hal_sec_ecdsa.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_ecdsa.h)）

ECDSA and ECDH on 256-bit curves using the public-key accelerator (PKA), plus direct access to the TRNG.

Scalars, coordinates, hashes and signature values are 256-bit unsigned integers stored as 32-byte big-endian byte strings (most significant byte first) in 4-byte aligned `uint32_t[8]` buffers.

Curve support: [`sec_ecdsa_get_public_key()`](#sec_ecdsa_get_public_key), [`sec_ecdh_get_public_key()`](#sec_ecdh_get_public_key) and [`sec_ecdh_get_encrypt_key()`](#sec_ecdh_get_encrypt_key) support both [`ECP_SECP256R1`](#sec_ecp_type) and [`ECP_SECP256K1`](#sec_ecp_type); [`sec_ecdsa_sign()`](#sec_ecdsa_sign) and [`sec_ecdsa_verify()`](#sec_ecdsa_verify) support [`ECP_SECP256R1`](#sec_ecp_type) (NIST P-256) only.

Calls are blocking. The HAL takes no lock and the PKA is shared with the RSA functions ([`hal_sec_dsa.h`](#hal_sec_dsa-h)) and [`hal_sec_p256.h`](#hal_sec_p256-h); serialise access with the other users. The SDK's mbedTLS hardware port takes `ipro_sec_pka_mutex_take()` / `ipro_sec_pka_mutex_give()` around its PKA calls.

### sec_ecdsa_init { #sec_ecdsa_init }

```c
int sec_ecdsa_init(sec_ecdsa_handle_t *handle, sec_ecp_type id);
```

Prepare the PKA and the TRNG for ECDSA on curve `id`.

Resets the PKA, selects big-endian operand order, enables the TRNG and stores `id` in the handle. The key pointers are left unchanged.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `id` | Curve. |

**回傳值**：0 (always).

### sec_ecdsa_deinit { #sec_ecdsa_deinit }

```c
int sec_ecdsa_deinit(sec_ecdsa_handle_t *handle);
```

Reset the PKA after ECDSA use.

| 參數 | 說明 |
|---|---|
| `handle` | Handle (not modified). |

**回傳值**：0 (always).

### sec_ecdsa_sign { #sec_ecdsa_sign }

```c
int sec_ecdsa_sign(sec_ecdsa_handle_t *handle, const uint32_t *random_k, const uint32_t *hash, uint32_t hashLenInWord, uint32_t *r, uint32_t *s);
```

Create an ECDSA signature (r, s) on P-256.

Resets the PKA, computes R = k * G, r = R.x mod n and s = k^-1 * (hash + r * d) mod n with d = `handle->privateKey`. When r or s comes out as zero the computation is repeated, up to 100 times.

| 參數 | 說明 |
|---|---|
| `handle` | Handle with `privateKey` set. |
| `random_k` | Per-signature secret nonce k, in [1, n - 1]; NULL draws k from the TRNG. A caller-supplied k must be unpredictable and never reused. |
| `hash` | 32-byte message digest. |
| `hashLenInWord` | Not used; 8 words (32 bytes) of `hash` are always read. |
| `r` | Signature value r (32 bytes). |
| `s` | Signature value s (32 bytes). |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `privateKey`, `hash`, `r` or `s` is NULL, no nonce below n was drawn, or r or s was still zero after 100 attempts. |

!!! warning "警告"
    The P-256 group order is used whatever `handle->ecpId` says, so signatures for [`ECP_SECP256K1`](#sec_ecp_type) are not valid.

### sec_ecdsa_verify { #sec_ecdsa_verify }

```c
int sec_ecdsa_verify(sec_ecdsa_handle_t *handle, const uint32_t *hash, uint32_t hashLen, const uint32_t *r, const uint32_t *s);
```

Verify an ECDSA signature (r, s) on P-256.

Checks that r and s lie in [1, n - 1], computes R = (hash / s) * G + (r / s) * Q with Q = (`publicKeyx`, `publicKeyy`) and compares R.x mod n with r.

| 參數 | 說明 |
|---|---|
| `handle` | Handle initialised for [`ECP_SECP256R1`](#sec_ecp_type) with `publicKeyx` and `publicKeyy` set. |
| `hash` | 32-byte message digest. |
| `hashLen` | Length of `hash` in 32-bit words; must be 8. |
| `r` | Signature value r (32 bytes). |
| `s` | Signature value s (32 bytes). |

| 回傳碼 | 說明 |
|---|---|
| `0` | The signature is valid. |
| `-1` | Invalid signature, unsupported curve, `hashLen` not 8, or a NULL argument or key pointer. |

### sec_ecdsa_get_private_key { #sec_ecdsa_get_private_key }

```c
int sec_ecdsa_get_private_key(sec_ecdsa_handle_t *handle, uint32_t *private_key);
```

Generate a random private key below the P-256 group order n.

Draws 32 bytes from the TRNG until the value is below n, up to 100 tries. The TRNG must be enabled ([`sec_ecdsa_init()`](#sec_ecdsa_init) does this).

| 參數 | 說明 |
|---|---|
| `handle` | Not used. |
| `private_key` | 32-byte output buffer. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | No value below n was obtained. |

### sec_ecdsa_get_public_key { #sec_ecdsa_get_public_key }

```c
int sec_ecdsa_get_public_key(sec_ecdsa_handle_t *handle, const uint32_t *private_key, const uint32_t *pRx, const uint32_t *pRy);
```

Compute the public key Q = d * G on the handle's curve.

Same as [`sec_ecdh_get_public_key()`](#sec_ecdh_get_public_key). Resets the PKA first.

| 參數 | 說明 |
|---|---|
| `handle` | Handle initialised with [`sec_ecdsa_init()`](#sec_ecdsa_init). |
| `private_key` | Private key d (32 bytes). |
| `pRx` | Q.x (32 bytes). Declared as pointer to const, but written. |
| `pRy` | Q.y (32 bytes). Declared as pointer to const, but written. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `private_key` is NULL. |
| `1` | The handle holds an unsupported curve. |

### sec_ecdh_init { #sec_ecdh_init }

```c
int sec_ecdh_init(sec_ecdh_handle_t *handle, sec_ecp_type id);
```

Prepare the PKA and the TRNG for ECDH on curve `id`.

Resets the PKA, selects big-endian operand order, enables the TRNG and stores `id` in the handle.

| 參數 | 說明 |
|---|---|
| `handle` | Handle to initialise. |
| `id` | Curve. |

**回傳值**：0 (always).

### sec_ecdh_deinit { #sec_ecdh_deinit }

```c
int sec_ecdh_deinit(sec_ecdh_handle_t *handle);
```

Reset the PKA after ECDH use.

| 參數 | 說明 |
|---|---|
| `handle` | Handle (not modified). |

**回傳值**：0 (always).

### sec_ecdh_get_encrypt_key { #sec_ecdh_get_encrypt_key }

```c
int sec_ecdh_get_encrypt_key(sec_ecdh_handle_t *handle, const uint32_t *pkX, const uint32_t *pkY, const uint32_t *private_key, const uint32_t *pRx, const uint32_t *pRy);
```

Compute the ECDH shared point S = d * P for a peer public key P.

The shared secret is S.x (`pRx`). Resets the PKA first.

| 參數 | 說明 |
|---|---|
| `handle` | Handle initialised with [`sec_ecdh_init()`](#sec_ecdh_init). |
| `pkX` | Peer public key x coordinate (32 bytes). |
| `pkY` | Peer public key y coordinate (32 bytes). |
| `private_key` | Own private key d (32 bytes). |
| `pRx` | S.x, the shared secret (32 bytes). Declared as pointer to const, but written. |
| `pRy` | S.y (32 bytes). Declared as pointer to const, but written. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `private_key` is NULL. |
| `1` | The handle holds an unsupported curve. |

!!! warning "警告"
    The peer point is not checked to lie on the curve; validate it before calling.

### sec_ecdh_get_public_key { #sec_ecdh_get_public_key }

```c
int sec_ecdh_get_public_key(sec_ecdh_handle_t *handle, const uint32_t *private_key, const uint32_t *pRx, const uint32_t *pRy);
```

Compute the public key Q = d * G on the handle's curve.

Resets the PKA first.

| 參數 | 說明 |
|---|---|
| `handle` | Handle initialised with [`sec_ecdh_init()`](#sec_ecdh_init). |
| `private_key` | Private key d (32 bytes). |
| `pRx` | Q.x (32 bytes). Declared as pointer to const, but written. |
| `pRy` | Q.y (32 bytes). Declared as pointer to const, but written. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | `private_key` is NULL. |
| `1` | The handle holds an unsupported curve. |

### sec_ecc_get_random_value { #sec_ecc_get_random_value }

```c
int sec_ecc_get_random_value(uint32_t *randomData, uint32_t *maxRef, uint32_t size);
```

Fill a buffer with TRNG output, optionally below an upper bound.

Reads `size` bytes from the TRNG. With `maxRef` set, the draw is repeated (up to 100 times) until the value, read as a big-endian number, is below `maxRef`. The TRNG must be enabled.

| 參數 | 說明 |
|---|---|
| `randomData` | Output buffer of `size` bytes. |
| `maxRef` | Exclusive upper bound, `size` bytes big-endian, or NULL for no bound. |
| `size` | Number of bytes. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | No value below `maxRef` was obtained. |

### sec_eng_trng_enable { #sec_eng_trng_enable }

```c
int sec_eng_trng_enable(void);
```

Enable the TRNG and wait for its first output.

Busy-waits with a bounded poll count. Unlike [`hal_sec_trng_init()`](#hal_sec_trng_init) it does not set the ring-oscillator selection.

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `2` | The TRNG did not become ready (timeout). |

### sec_eng_trng_disable { #sec_eng_trng_disable }

```c
void sec_eng_trng_disable(void);
```

Disable the TRNG.

### sec_eng_trng_read { #sec_eng_trng_read }

```c
int sec_eng_trng_read(uint8_t data[32]);
```

Read one 32-byte block from the TRNG.

Triggers a generation, busy-waits for it and copies the result. The TRNG must be enabled. This bypasses the buffering of [`hal_sec_trng.h`](#hal_sec_trng-h).

| 參數 | 說明 |
|---|---|
| `data` | 32-byte output buffer. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `2` | The TRNG did not finish (timeout). |

### sec_ecp_type { #sec_ecp_type }

Elliptic curve identifier.

| 名稱 | 值 | 說明 |
|---|---|---|
| `ECP_SECP256R1` | `0` | NIST P-256 (secp256r1). |
| `ECP_SECP256K1` | `1` | secp256k1. |
| `ECP_TYPE_MAX` | `2` | Number of curves; not a valid curve. |

### sec_ecdsa_handle_t { #sec_ecdsa_handle_t }

ECDSA key handle.

The key fields point at caller-owned 32-byte buffers; set the ones the operation needs after [`sec_ecdsa_init()`](#sec_ecdsa_init).

| 欄位 | 型別 | 說明 |
|---|---|---|
| `ecpId` | `sec_ecp_type` | Curve, set by [`sec_ecdsa_init()`](#sec_ecdsa_init). |
| `privateKey` | `uint32_t *` | Private key d; read by [`sec_ecdsa_sign()`](#sec_ecdsa_sign). |
| `publicKeyx` | `uint32_t *` | Public key x coordinate; read by [`sec_ecdsa_verify()`](#sec_ecdsa_verify). |
| `publicKeyy` | `uint32_t *` | Public key y coordinate; read by [`sec_ecdsa_verify()`](#sec_ecdsa_verify). |

### sec_ecdh_handle_t { #sec_ecdh_handle_t }

ECDH handle.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `ecpId` | `sec_ecp_type` | Curve, set by [`sec_ecdh_init()`](#sec_ecdh_init). |

## hal_sec_p256.h { #hal_sec_p256-h }

`#include "hal_sec_p256.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_p256.h)）

NIST P-256 point doubling and mixed addition on the public-key accelerator (PKA), as building blocks for a scalar multiplication.

These functions are a field-arithmetic back end for a caller that implements the scalar multiplication itself (for example an mbedTLS ECP accelerator hook); they are not stand-alone ECDH or signing functions. The caller owns the PKA lock, validates the curve and the input points, and keeps scalar blinding and randomisation. No private scalar passes through this interface, but coordinates may still be sensitive.

Call sequence: [`sec_p256_field_init()`](#sec_p256_field_init), any number of [`sec_p256_double()`](#sec_p256_double) and [`sec_p256_add_mixed()`](#sec_p256_add_mixed) calls, [`sec_p256_field_free()`](#sec_p256_field_free). The field operations follow a fixed schedule without branches on scalar bits.

Built for IPRO7 only.

### sec_p256_field_init { #sec_p256_field_init }

```c
void sec_p256_field_init(void);
```

Reset the PKA and load the P-256 field constants.

Selects big-endian operand order and loads p, -p^-1 mod 2^256, 1 and 2^512 mod p into PKA registers. Call it once, with the PKA lock held, before [`sec_p256_double()`](#sec_p256_double) or [`sec_p256_add_mixed()`](#sec_p256_add_mixed).

### sec_p256_field_free { #sec_p256_field_free }

```c
void sec_p256_field_free(void);
```

Clear the PKA registers used by the field back end and reset the PKA.

Call it when the scalar multiplication is finished, before releasing the PKA lock.

### sec_p256_double { #sec_p256_double }

```c
void sec_p256_double(sec_p256_point_t *r, const sec_p256_point_t *p);
```

Compute r = 2 * p in Jacobian coordinates (curve parameter a = -3).

| 參數 | 說明 |
|---|---|
| `r` | Result; may be the same object as `p`. |
| `p` | Input point. |

### sec_p256_add_mixed { #sec_p256_add_mixed }

```c
void sec_p256_add_mixed(sec_p256_point_t *r, const sec_p256_point_t *p, const sec_p256_point_t *q);
```

Compute r = p + q, with `q` in affine coordinates.

Only q.x and q.y are read; q.z is ignored and q must not be the point at infinity. Special cases: if p is the point at infinity (p.z = 0), `q` is copied to `r` unchanged; if p = q the result is 2 * p; if p = -q the result is the point at infinity, returned as (1, 1, 0).

| 參數 | 說明 |
|---|---|
| `r` | Result; may be the same object as `p` or `q`. |
| `p` | Jacobian input point. |
| `q` | Affine input point. |

### sec_p256_point_t { #sec_p256_point_t }

P-256 point in Jacobian coordinates.

Each coordinate is a 32-byte big-endian integer in [0, p) stored in a 4-byte aligned array. The affine point is x = X / Z^2, y = Y / Z^3; Z = 0 is the point at infinity.

| 欄位 | 型別 | 說明 |
|---|---|---|
| `x` | `uint32_t[8]` | Jacobian X coordinate (32 bytes, big-endian). |
| `y` | `uint32_t[8]` | Jacobian Y coordinate (32 bytes, big-endian). |
| `z` | `uint32_t[8]` | Jacobian Z coordinate (32 bytes, big-endian). |

## hal_sec_trng.h { #hal_sec_trng-h }

`#include "hal_sec_trng.h"`（[原始碼](https://github.com/INTELPRO-INC/IPRO-SDK/blob/IPRO-SDK-V2.1.0/bsp/hal/inc/hal_sec_trng.h)）

Random numbers from the security engine's true random number generator (TRNG), and ring-oscillator frequency measurement.

Call [`hal_sec_trng_init()`](#hal_sec_trng_init) (or [`hal_sec_common_init()`](#hal_sec_common_init)) once before reading random data. The TRNG delivers 32-byte blocks; the HAL buffers one block and hands it out in pieces. If a block read times out or returns all zeros (for example after a low-power state powered the engine down), the HAL re-initialises the TRNG once and retries.

The read functions run inside hal_sec_enter_critical() (see [`hal_sec_common.h`](#hal_sec_common-h)) and busy-wait on the engine. In FreeRTOS builds they must therefore be called from task context, not from an interrupt handler.

Compiled into the HAL for FreeRTOS and Zephyr builds only.

### hal_rand_stream { #hal_rand_stream }

```c
int hal_rand_stream(uint8_t *buf, int len);
```

Fill a buffer with random bytes.

| 參數 | 說明 |
|---|---|
| `buf` | Output buffer. |
| `len` | Number of bytes; 0 or a negative value does nothing. |

| 回傳碼 | 說明 |
|---|---|
| `0` | Success. |
| `-1` | The TRNG timed out, also after one re-initialisation. |
| `1` | The TRNG returned an all-zero block, also after one re-initialisation. |

!!! note "注意"
    An error can be reported after `buf` has been filled, while the HAL refills its internal buffer; treat the whole output as unusable on any non-zero return.

!!! warning "警告"
    [`hal_sec_trng_init()`](#hal_sec_trng_init) must have been called; before that the first bytes returned are zeros.

### hal_rand { #hal_rand }

```c
int hal_rand(void);
```

Return a random `int`.

Reads `sizeof(int)` bytes with [`hal_rand_stream()`](#hal_rand_stream); errors are not reported.

**回傳值**：Random value (any bit pattern, including negative values).

### hal_sec_get_random_word { #hal_sec_get_random_word }

```c
uint32_t hal_sec_get_random_word(void);
```

Return a random 32-bit word.

Reads 4 bytes with [`hal_rand_stream()`](#hal_rand_stream); errors are not reported.

**回傳值**：Random value.

### hal_sec_trng_init { #hal_sec_trng_init }

```c
int hal_sec_trng_init(void);
```

Initialise the TRNG.

On IPRO7 this first selects the ring oscillators that feed the entropy source, then enables the TRNG, which busy-waits for its first generation. The internal buffer is marked empty so that the next read fetches a fresh block. Calling it again re-initialises the TRNG.

**回傳值**：0 (always; a TRNG enable timeout is not reported).

### hal_rosc_measure { #hal_rosc_measure }

```c
uint32_t hal_rosc_measure(uint8_t rosc_idx, uint16_t *t_cnt, uint16_t *g_cnt);
```

Measure the frequency of one of the TRNG ring oscillators.

Counts the selected ring oscillator against the 32 MHz crystal with the security engine's clock detector and returns `32 MHz * t_count / (g_count + 1)`. Intended for production test. Available on IPRO7 only.

| 參數 | 說明 |
|---|---|
| `rosc_idx` | Ring oscillator index, 0 to 3. |
| `t_cnt` | Receives the ring-oscillator count; may be NULL. |
| `g_cnt` | Receives the crystal reference count; may be NULL. |

**回傳值**：Frequency in Hz, or 0 if `rosc_idx` is above 3 or the reference count is 0.

!!! note "注意"
    Busy-waits for the measurement to finish without a timeout.
