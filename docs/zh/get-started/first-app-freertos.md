---
title: "第一個 FreeRTOS 應用"
description: 在 IPRO7AI Reef EVK 上設定開關、接主控台線，建置、燒錄並執行開箱韌體 ipro7ai_reef_demo，再以 reef selftest 檢查板上功能。
migrate_from:
  - "getting-started.html#freertos-quickstart"
  - "getting-started.html#first-build"
---

# 第一個 FreeRTOS 應用

在 IPRO7AI Reef EVK V4.0 上建置並燒錄開箱韌體 `ipro7ai_reef_demo`，開啟主控台後以 `reef selftest` 檢查 LED、喇叭、SD 卡槽與相機。完成後，主控台出現 `ipro />` 提示字元，板上每個功能區塊都能以 shell 指令操作。

## 前置需求 { #prerequisites }

- 已完成[準備開發環境](environment.md)：`./build_freertos.sh ipro7ai_reef_demo` 能建置成功，IntelProCube 的 `--help` 能執行。Windows 另見 [Windows 安裝與 VS Code](windows.md)。
- IPRO7AI Reef EVK V4.0、USB-C 線、主控台線（3.3 V USB 轉 UART 轉接器或 IPRO Debug Probe）。
- 選用：OV5640 FLEX-24 相機模組、microSD 卡、8 Ω 喇叭（接 J_SPK）。沒有這些時，自我檢查的對應項目會顯示未偵測到。
- 以下命令列範例以 macOS 為準；Linux 把序列埠換成 `/dev/ttyUSB0`、工具換成 `ipro_iot_tool_linux`，Windows 依各步驟的分頁操作。

## 設定開關與接線 { #connect }

<div class="ipro-steps" markdown>

1. **撥開關**：SW7 撥到 **CAM**，SW8 撥到 **PWR**。SW7 在 GPIO 時相機沒有電；SW8 在 MEAS 時 IPRO7AI 改由 JP2 供電，見 [開關與跳線](../hardware/boards/reef-evk.md#jumpers)。

2. **接主控台線到 U6**（板子先不要上電）：

    | U6 腳 | 訊號 | 接到 USB 轉 UART 轉接器 |
    |---|---|---|
    | 1 | NC | — |
    | 2 | GND | GND |
    | 3 | TX（GPIO20，Reef 送出） | RX |
    | 4 | RX（GPIO21，Reef 接收） | TX |
    | 5 | BOOT（經 1 kΩ 接 GPIO41） | 選用：DTR |
    | 6 | RESET（經 1 kΩ，低準位重置） | 選用：RTS |

    使用 IPRO Debug Probe 時，以兩端腳序對調的排線接探針的 CN_UART：探針第 n 腳接 U6 第 7 − n 腳。

    !!! warning "排線方向"
        不要用兩端腳序相同的排線接 Debug Probe：UART 與控制線會接錯，探針的 3.3 V 也會接到 U6 的 RESET。

3. **上電**：接上 USB-C。綠色電源指示燈 LED2 亮起。U6 不供電，板子只由 USB-C 供電。

4. **確認序列埠**：把轉接器或探針接上電腦，確認出現序列埠，例如 macOS 的 `/dev/cu.usbserial-XXXX`、Linux 的 `/dev/ttyUSB0`、Windows 的 `COM5`。Debug Probe 使用名稱結尾為 `02` 的那一個，見[辨識序列埠](flash-and-monitor.md#ports)。

</div>

## 建置 { #first-build }

<div class="ipro-steps" markdown>

1. **建置開箱韌體**：在 SDK 根目錄執行。Windows 改用 VS Code Extension 的 `IPRO: Build`（見[設定 VS Code Extension](windows.md#installation)），或 PowerShell 的 `build_freertos.ps1`（見[命令列建置](windows.md#command-line)）。

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    建置設定階段會印出 Reef 的板級設定，結尾印出記憶體用量與映像檔路徑（節錄）：

    ```text
    -- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
    -- IPRO7 flash: 1M (default, on-chip)
    -- AI disabled: OCRAM=256KB
    ...
    Memory region         Used Size  Region Size  %age Used
               flash:      249944 B         1 MB     23.84%
               psram:       45376 B         8 MB      0.54%
               ocram:       32144 B       256 KB     12.26%
              hbnram:        2460 B         4 KB     60.06%
    Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    [100%] Built target ipro7ai_reef_demo_IPRO7.elf
    ```

    數字依工具鏈版本會略有不同。

2. **確認產出**

    ```bash
    ls apps/platform/ipro7ai_reef_demo/build/build_out/
    ```

    ```text
    ipro7ai_reef_demo_IPRO7.bin    燒錄用的映像檔
    ipro7ai_reef_demo_IPRO7.elf    含除錯符號
    ipro7ai_reef_demo_IPRO7.map    記憶體配置
    lib/
    ```

</div>

## 燒錄與執行 { #flash-and-run }

<div class="ipro-steps" markdown>

1. **釋放序列埠**：關閉所有開著這個序列埠的終端程式。燒錄與主控台共用同一個 UART。

2. **進入下載模式**：按住 **SW1（BOOT）**，按一下 **SW2（RESET）**，再放開 SW1。進入下載模式後主控台沒有任何輸出。

    板子已經在執行 SDK 韌體（例如出廠的開箱韌體）時，也可以在主控台輸入 `reboot_dl`，畫面印出 `reboot to download mode` 後就進入下載模式。U6 接了 DTR／RTS 的自動下載線或 Debug Probe 時，見[進入下載模式](flash-and-monitor.md#download-mode)。

3. **燒錄**：在 IntelProCube 目錄下執行命令列工具。`--chip-variant IPRO7AI` 選擇 Reef 的 Flash 腳位，`--pt` 指定 IntelProCube 隨附的分割表。

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

    工具逐行印出進度（節錄，時間戳記省略）：

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

    最後一行是 `[All Success]` 才算成功。工具即使燒錄失敗也會以 0 結束，不能用結束碼判斷。

4. **開啟主控台**：以 115200 baud、8N1、無流量控制開啟同一個序列埠。

    === "macOS"

        ```bash
        screen /dev/cu.usbserial-XXXX 115200
        ```

        結束 `screen`：按 ++ctrl+a++，再按 ++k++，回答 `y`。

    === "Linux"

        ```bash
        picocom -b 115200 /dev/ttyUSB0
        ```

        結束 `picocom`：按 ++ctrl+a++，再按 ++ctrl+x++。沒有 `picocom` 時以 `sudo apt install picocom` 安裝。

    === "Windows"

        在 PuTTY 選 **Serial**，Serial line 填 `COM5`、Speed 填 `115200`，按 **Open**。也可以用 VS Code Extension 的 `IPRO: Serial Monitor`。

5. **重置**：按一下 **SW2（RESET）**。RGB LED 以藍光呼吸一次後熄滅，主控台出現開機訊息（節錄，`(…)` 內是時間戳記）：

    ```text
    I (…) REEF: ==========================================
    I (…) REEF:   IPRO7AI Reef carrier demo
    I (…) REEF:   UART0 TX=20 RX=21  RGB=G24  SPK_EN=G25(hi)
    I (…) REEF:   CAM: FLEX-24 D0-7=G0-7 XCLK=G22 RST=G34 PWDN=G35
    ...
    I (…) REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    ```

    按 ++enter++ 會出現提示字元 `ipro />`。

</div>

## 確認結果 { #verify }

<div class="ipro-steps" markdown>

1. **按鍵**：依序按 SW3、SW4、SW5 與 SW1（BOOT），RGB LED 分別亮紅、綠、藍、白光。

2. **自我檢查**：在主控台輸入 `reef selftest`。約 3 秒內 LED 依序亮紅、綠、藍，喇叭發出 1 kHz 短音，輸出如下（接 OV5640、未插 SD 卡時）：

    ```text
    ipro />reef selftest
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: __rti_name_ov5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    | 行 | 檢查內容 | 其他可能的結果 |
    |---|---|---|
    | `[3/4] SD slot` | 卡槽是否有卡、卡槽電源 | 插卡時為 `something seated` |
    | `[4/4] camera bus` | 經 SCCB 偵測到的相機感測器與位址 | 未接相機時為 `no sensor`；OV2640 為 `__rti_name_ov2640 at 0x30` |

3. **列出指令**：輸入 `help`，列出所有 shell 指令，包括 `reboot` 與 `reboot_dl`。

</div>

### 開箱韌體的指令 { #commands }

| 指令 | 作用 |
|---|---|
| `reef status`、`reef selftest` | 板子狀態（腳位、按鍵、LED、擴大機、偵測線）；自我檢查 |
| `led <r> <g> <b>`、`led rainbow`、`led off` | RGB LED 顏色（0–255，例如 `led 40 0 0`）、彩虹效果、關閉 |
| `btn status`、`btn watch` | 按鍵狀態與按下次數；即時列出按下與放開 |
| `spk tone <hz> <ms>`、`hp` | 喇叭輸出正弦波；讀取耳麥插入偵測 |
| `mic rec pdm <秒>`、`mic rec headset <秒>`、`mic play`、`mic loop` | 以板上 PDM 麥克風或耳麥錄音到 PSRAM（最長 10 秒）後播放，或即時監聽 |
| `mic sdrec <來源> <名稱> <秒>`、`mic usb <來源>` | 錄成 `sd:/rec/<名稱>.wav`；讓板子從 USB-C 當成 USB 麥克風，直到 `mic stop` |
| `sd mount`、`sd ls`、`sd test` | microSD（FatFS 掛載於 `sd:`） |
| `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on`、`cam bar off` | OV5640 相機（SW7 在 CAM） |
| `reboot`、`reboot_dl` | 重新開機；重新開機並進入下載模式 |

各指令的說明與相機上手順序見 [IPRO7AI Reef EVK：開箱韌體](../hardware/boards/reef-evk.md#reef-demo)。

## 一次完成：build_freertos.sh { #one-command }

在 macOS／Linux 上，`build_freertos.sh` 可以把建置、燒錄與監看串成一行。它從應用的設定判斷要傳 `--chip-variant IPRO7AI`，並以應用的主控台鮑率開啟序列埠。板上已執行含 shell 的 SDK 韌體時，它會先送出 `reboot_dl` 進入下載模式；第一次燒錄請先依上面的步驟手動進入下載模式。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

成功時依序印出 `✓ Build succeeded`、工具的燒錄輸出、`✓ Flash succeeded`，接著顯示開機訊息 30 秒。`monitor` 只讀取輸出，不能輸入指令；結束時印出 `[serial_monitor] TIMEOUT after 30s`，腳本把它算成失敗，這是正常的。所有選項見 [macOS／Linux 命令列](command-line.md#build-script)。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 綠色電源燈 LED2 不亮 | USB-C 未接好，或電源沒有供電 | 換 USB-C 線或電源；只能由 USB-C 供電 |
| 燒錄輸出沒有 `[All Success]`，停在握手階段 | 板子不在下載模式，或序列埠被終端程式占用 | 關閉終端程式；按住 SW1、按一下 SW2、放開 SW1 後重新燒錄 |
| 出現 `flash jedec id: 00000000` 與 `IPRO FLASH MATCH TYPE FAIL` | Flash 腳位設定錯誤 | 燒錄命令加上 `--chip-variant IPRO7AI` |
| 工具找不到 `chips/...` 下的分割表 | 不是在 IntelProCube 目錄下執行 | 先 `cd <IntelProCube>` 再執行 |
| 燒錄成功但主控台沒有輸出 | 板子仍在下載模式、鮑率或序列埠不對、RX／TX 接反 | 按 SW2 重置；以 115200 開啟；macOS 用 `/dev/cu.*`；對調轉接器的 RX 與 TX |
| 主控台亂碼 | 鮑率不是 115200 | 以 115200、8N1 重新開啟 |
| 主控台有輸出，但輸入指令沒有反應 | 轉接器的 TX 沒有接到 U6 第 4 腳 | 檢查 U6 第 4 腳（RX）的接線 |
| `[4/4] camera bus: no sensor` | 未接相機、排線未插好，或 SW7 不在 CAM | 拔掉 USB-C 後重插相機排線；SW7 撥到 CAM |
| 喇叭沒有聲音 | 沒有接喇叭，或接頭沒插好 | 把 8 Ω 喇叭接到 J_SPK |
| `[3/4] SD slot: empty`，但有插卡 | 卡沒有推到底 | 把卡推入直到卡住 |
| 建置時找不到編譯器 | 工具鏈不在預設路徑 | 設定 `CROSS_COMPILE`，見[準備開發環境](environment.md#toolchain) |

更多燒錄與主控台問題見[燒錄與序列埠](flash-and-monitor.md#troubleshooting)。

## 下一步 { #next-steps }

- [建置與燒錄流程](../tutorials/build-and-flash.md)：修改程式後重新建置、燒錄與監看。
- [建立第一個應用](../tutorials/first-own-app.md)與[測試應用](../tutorials/testing.md)。
- [燒錄與序列埠](flash-and-monitor.md)：其他下載模式、分割表、boot2 與 `mfg` 資料。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：完整的開關、腳位與相機上手順序。
