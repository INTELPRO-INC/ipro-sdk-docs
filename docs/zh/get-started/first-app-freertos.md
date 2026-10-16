---
title: "第一個 FreeRTOS 應用"
description: 在 IPRO7AI Reef EVK 上建置、燒錄開箱韌體 ipro7ai_reef_demo，並以 reef selftest 檢查板上功能。
migrate_from:
  - "getting-started.html#freertos-quickstart"
  - "getting-started.html#first-build"
---

# 第一個 FreeRTOS 應用

在 IPRO7AI Reef EVK 上建置並燒錄開箱韌體 `ipro7ai_reef_demo`，開啟主控台後以 `reef selftest` 檢查 LED、喇叭、SD 卡槽與相機。IPRO7AI EVK 與 IPRO7 EVB 的不同處見[其他板卡](#other-boards)。

## 前置需求 { #prerequisites }

- 已完成 [Windows](windows.md) 或 [macOS／Linux](command-line.md) 的安裝，可以建置應用。
- IntelProCube v0.6.3 命令列工具：未包含於 V2.1.0，請洽 INTELPRO。
- IPRO7AI Reef EVK、USB-C 線（Reef 只能由 USB-C 供電），以及接 U6 主控台接頭（SH1.0）的 USB 轉 UART 線。
- 選用：FLEX-24 相機模組（OV5640 或 OV2640）與 SD 卡，用來完成自我檢查的相機與卡槽項目。

!!! warning "上電前"
    **JP1 必須插上**（VDDIO1：1-2 為 3.3 V，2-3 為 2.8 V），否則相機、USB 與 BOOT 所在的 VDDIO1 電源組沒有供電。JP2 插 1-2（與 R40 0 Ω 等效，兩者擇一）。其他跳線見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。

## 建置 { #first-build }

<div class="ipro-steps" markdown>

1. **建置開箱韌體**：在 SDK 根目錄執行下列任一命令。Windows 上改用 VS Code Extension 的 `IPRO: Build`（見 [Windows 安裝與 VS Code](windows.md#installation)）。

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    # 或
    ./build_freertos.sh ipro7ai_reef_demo
    ```

2. **確認產出**：建置結束時，連結器會列出 Flash 與 RAM 用量。產出位於：

    ```text
    apps/platform/ipro7ai_reef_demo/build/build_out/
    ├── ipro7ai_reef_demo_IPRO7.bin    燒錄用的映像檔
    ├── ipro7ai_reef_demo_IPRO7.elf    含除錯符號
    └── ipro7ai_reef_demo_IPRO7.map    記憶體配置
    ```

</div>

## 燒錄與執行 { #flash-and-run }

<div class="ipro-steps" markdown>

1. **接線並進入下載模式**：接上 USB-C 與 U6 的 USB 轉 UART 線。按住 **SW1（BOOT）**，按一下 **SW2（RESET）**，再放開 SW1。U6 的 DTR 與 RTS 也接到 BOOT 與 RESET，使用自動下載線時可省略按鍵。

2. **燒錄**：在 IntelProCube 目錄下執行命令列工具。`--chip-variant IPRO7AI` 選擇 Reef 的 Flash 腳位設定，`--pt` 指定 Reef 應用 README 使用的分割表。

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    工具即使燒錄失敗也會以 0 結束；輸出中出現 `[All Success]` 才算成功。

3. **開啟主控台並重置**：主控台在 U6，鮑率 115200（8N1）。在 macOS／Linux 上先啟動 SDK 的 `tools/serial_monitor.py`（`--timeout 0` 會持續讀取，按 ++ctrl+c++ 結束），再按 SW2（RESET）。Windows 上使用 Extension 的 Serial Monitor 或其他序列埠終端程式。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 115200 --timeout 0
    ```

4. **執行自我檢查**：按 ++ctrl+c++ 結束上一步的監看，再送出 `reef selftest`。使用互動式序列埠終端程式時直接輸入即可。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 5
    ```

</div>

## 確認結果 { #verify }

開機時 RGB LED 以藍光呼吸一次後熄滅，主控台出現 `IPRO7AI Reef carrier demo` 標題與 `shell ready` 訊息，接著是 `ipro />` 提示字元。按 SW3、SW4、SW5 時，LED 分別亮紅、綠、藍。

`reef selftest` 約 3 秒完成，輸出格式如下：

```text
[1/4] RGB LED: red, green, blue
[2/4] speaker: 1 kHz, 300 ms, 20%
[3/4] SD slot: <empty | something seated>, supply <on | off>
[4/4] camera bus: <感測器> at 0x<SCCB 位址>
done - keys: press any and run `btn status`
```

- 第 1 步：LED 依序亮紅、綠、藍。
- 第 2 步：喇叭發出 1 kHz 短音。
- 第 3 步：卡槽是否有卡，以及卡槽供電狀態。
- 第 4 步：偵測到的相機感測器；未接相機時顯示 `no sensor`。

輸入 `help` 可列出所有指令；各功能區塊的指令說明見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。

## 其他板卡 { #other-boards }

步驟相同，差在建議的應用、`--chip-variant`、分割表、進入下載模式的方式與主控台鮑率：

- **IPRO7AI EVK**：從 `apps/platform/ipro7ai_evk_launcher` 開始，以應用目錄的 `./flash.sh --full` 燒錄分割表、韌體與手勢模型，主控台 921600 baud。上電前要先接好 J6，步驟見 [IPRO7AI EVK](../hardware/boards/ipro7ai-evk.md#quick-start)。
- **IPRO7 EVB**：以 `ipro_ble_remote` 為例的步驟見 [IPRO7 EVB](../hardware/boards/ipro7-evb.md#quick-start)，主控台 115200 baud。

各板的 `--chip-variant`、分割表與下載模式整理在[燒錄與序列埠](flash-and-monitor.md#board-settings)。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 輸出沒有 `[All Success]`，握手失敗 | 板子不在下載模式 | 按住 SW1（BOOT）、按一下 SW2（RESET）後重新燒錄 |
| 握手成功，但出現 `flash jedec id: 00000000` 與 `IPRO FLASH MATCH TYPE FAIL` | Flash 腳位設定為 `0x2`；Reef 與 IPRO7AI EVK 需要 `0x9` | 燒錄命令加上 `--chip-variant IPRO7AI` |
| 燒錄後主控台沒有輸出 | 板子仍在下載模式（開機 ROM 不輸出），或鮑率、序列埠不符 | 按 SW2（RESET）；`ipro7ai_reef_demo` 使用 115200；macOS 使用 `/dev/cu.*`；確認 JP1 已插上 |
| 主控台正常，但 LED 不亮、喇叭無聲 | WS2812 與喇叭放大器由 VBUS 供電 | 由 USB-C 供電，不要只在 3V3 接電源 |
| `[4/4] camera bus: no sensor` | 未接相機，或排線未插好 | 確認 FLEX-24 相機模組已插好 |
| 建置時找不到編譯器 | 工具鏈不在預設路徑 | 設定 `CROSS_COMPILE`，見 [macOS／Linux 命令列](command-line.md#troubleshooting) |

## 下一步 { #next-steps }

- [燒錄與序列埠](flash-and-monitor.md)：燒錄工具參數、各板設定、`build_freertos.sh flash` 與主控台鮑率。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：完整的 shell 指令、跳線，以及經 IPRO6S FIN 卡的 Wi-Fi 與 RTSP 串流。
- [第一個 BLE 應用](../tutorials/first-ble-app.md)
- [範例](../examples/index.md)
