---
title: ipro_ai_link
description: IPRO AI Studio「Run on board」的板端韌體：由 microSD（sd:/）載入 .inm 模型與輸入、在 NPU 上推論、輸出原始結果；也可在主控台手動操作
generated: tools/gen_examples.py
migrate_from: []
---

# ipro_ai_link

IPRO AI Studio「Run on board」的板端韌體：由 microSD（`sd:/`）載入 `.inm` 模型與輸入、在 NPU 上推論、輸出原始結果；也可在主控台手動操作

| 項目 | 內容 |
|---|---|
| 原始碼 | [`apps/test/ipro_ai_link`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_ai_link) |
| 板卡與設定 | Reef（`defconfig_reef`）；`.config` 為 IPRO7 EVB |
| 主控台 | UART 115200（另有 USB CDC 主控台） |
| 建置 | Reef：`make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |

## 在 Reef 上執行 { #on-the-reef }

這個應用沒有 README，以下依原始碼整理。需要一張 FAT 格式的 microSD 卡。

<div class="ipro-steps" markdown>

1. **建置**

    ```bash
    make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef
    ```

    映像在 `apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin`。

2. **燒錄**：進入[下載模式](../hardware/boards/reef-evk.md#download-mode)，在 IntelProCube 目錄執行

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --firmware <SDK>/apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin
    ```

    確認 `[All Success]` 後按一下 SW2。

3. **執行**：以 115200 baud 開啟主控台，開機印出 `ipro_ai_link ready`。USB-C 接上電腦時，板子出現為兩個 CDC 序列埠（VID `0x3896`、PID `0x0704`）：第一個傳資料，第二個是主控台。

4. **手動推論**：把 `.inm` 模型與原始輸入檔複製到 SD 卡，插入卡座後依序輸入

    ```text
    ai_mount
    ai_load sd:/model.inm
    ai_input sd:/input.bin
    ai_run
    ai_out
    ```

    `ai_out` 以十六進位印出輸出張量，每個位元組都以 XOR 0x80 儲存。路徑一律以 `sd:/` 開頭。

</div>

SDK 隨附可用的模型，例如 `apps/platform/ipro7_demo/demo/ai/ai_model/mbv2.inm`。IPRO AI Studio 可從 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下載。
