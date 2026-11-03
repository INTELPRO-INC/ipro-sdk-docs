---
title: "建置與燒錄流程"
description: 在 IPRO7AI Reef EVK 上反覆執行的修改、建置、燒錄、監看迴圈：以 build_freertos.sh 一行完成、切換替代設定、乾淨建置、讀取記憶體用量。
migrate_from:
  - "tutorials.html — 教學 2"
---

# 建置與燒錄流程

日常開發的迴圈是「修改程式 → 建置 → 燒錄 → 看主控台」。本教學在 IPRO7AI Reef EVK 上修改開箱韌體 `ipro7ai_reef_demo` 的開機標題，用 `build_freertos.sh` 一行完成建置、燒錄與監看，並在主控台看到修改後的文字；之後說明替代設定、乾淨建置與記憶體用量。第一次安裝與燒錄請先完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)。

## 前置需求 { #prerequisites }

- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)：板上正在執行 `ipro7ai_reef_demo`，主控台能回應 `reef selftest`。
- macOS 或 Linux。`build_freertos.sh` 需要 bash；Windows 以 VS Code Extension 建置，再依 [Windows 安裝與 VS Code](../get-started/windows.md#flash) 燒錄，迴圈相同。
- 以下命令都在 SDK 根目錄執行，範例以 macOS 為準。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **設定環境變數**：在這個終端機視窗設定一次，之後的命令都會用到。

    ```bash
    export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
    export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
    export IPRO_FLASH_PT=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
    ```

    Linux 改用 `ipro_iot_tool_linux` 與 `/dev/ttyUSB0`。`IPRO_FLASH_PT` 會套用到這個視窗中的每一次 `flash`；改燒有自己分割表的應用時，以 `unset IPRO_FLASH_PT` 清掉或用 `-P` 覆寫。

2. **修改程式**：用編輯器打開 `apps/platform/ipro7ai_reef_demo/main.c`，在 `main()` 的開機標題後面加上自己的文字：

    ```c title="apps/platform/ipro7ai_reef_demo/main.c"
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. **建置、燒錄並監看**：關閉開著這個序列埠的終端程式，然後執行：

    ```bash
    ./build_freertos.sh -t 15 build flash monitor ipro7ai_reef_demo
    ```

    板上的韌體收到 `reboot_dl` 後自行進入下載模式，不必按鍵。輸出依序如下（節錄）：

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    → Building ipro7ai_reef_demo...
    ✓ Build succeeded (14s)
      Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
      Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
    → Entering download mode...
    reboot to download mode
    → Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
    [...] - Chip name is ipro7
    ...
    [...] - [All Success]
    ✓ Flash succeeded (…)
    → Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
    [serial_monitor] Sent: reboot
    ...
    I (…) REEF:   IPRO7AI Reef carrier demo - my build
    ...
    [serial_monitor] TIMEOUT after 15s
    ✗ Action 'monitor' failed — stopping.

    Summary:
      ✓ build
      ✓ flash
      ✗ monitor (exit 2)
    ```

    `monitor` 讀滿 `-t` 指定的秒數後以結束碼 2 結束，腳本把它列為失敗，這是正常的：只要 `build` 與 `flash` 都是 ✓，新韌體就已經在板上執行。

4. **互動確認**：以終端程式開啟主控台（例如 `screen /dev/cu.usbserial-XXXX 115200`），輸入 `reef status` 或 `led 0 40 0`，確認新韌體正常回應。再次燒錄前先關閉終端程式。

5. **重複**：之後每次修改，重複步驟 3 即可。只想確認能否編譯時，只執行 `build`：

    ```bash
    ./build_freertos.sh build ipro7ai_reef_demo
    ```

</div>

## 確認結果 { #verify }

- `Summary` 中 `build` 與 `flash` 都是 ✓。
- 主控台的開機訊息中出現 `IPRO7AI Reef carrier demo - my build`。
- 按 SW3、SW4、SW5 時 LED 仍然亮紅、綠、藍，`reef selftest` 的輸出與修改前相同。

## build_freertos.sh 動作與選項 { #actions }

本教學用到 `build`、`flash`、`monitor`，以及 `-t`（監看秒數）、`-d`（替代設定）、`-P`（分割表）。動作依序執行，任一動作失敗就停止。其他動作（`clean`、`size`、`test`）與全部選項、環境變數見 [macOS／Linux 命令列](../get-started/command-line.md#build-script)。

## 替代設定與建置目錄 { #variants }

同一個應用可以有多個設定檔。替代設定以 `-d` 選用，建置在 `build_<名稱>/`，應用目錄的 `.config` 不受影響：

```bash
./build_freertos.sh -d defconfig_wifi_ipro6s build ipro7ai_reef_demo        # 建置於 build_wifi_ipro6s/
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam       # USB 網路攝影機
```

- `flash`、`size` 依 `-d` 找映像檔：分開執行時每次都要加相同的 `-d`。
- 建置時設定檔會被複製成 `build_<名稱>/.config`；要改設定，請改應用目錄中的原檔。
- 燒錄 `ipro7_uvc_cam` 的 `defconfig_reef_ov5640` 並接上 OV5640 後，Reef 的 USB-C 上出現 USB 攝影機（`3896:0701`），用電腦的相機應用程式即可看到畫面。
- Reef 可用的全部設定與建置命令見 [Reef 的建置設定](../get-started/command-line.md#reef-configs)；需要 boot2 或 `mfg` 資料的應用，首次燒錄見[燒錄與序列埠](../get-started/flash-and-monitor.md#partition-tables)。

## 乾淨建置 { #clean-build }

修改 `.config` 或替代設定之後，尤其是 Flash 大小、PSRAM、AI 或 BLE 控制器相關的選項，先清除再建置。`clean` 只刪除對應的建置目錄：

```bash
./build_freertos.sh clean build ipro7ai_reef_demo                            # 刪除並重建 build/
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo   # 刪除並重建 build_wifi_ipro6s/
```

`clean` 完成時印出 `✓ Clean complete`。

## 讀取記憶體用量 { #memory-usage }

連結時會印出各記憶體區域的用量。用 `make` 建置時直接顯示在終端機；用 `build_freertos.sh` 時寫在 `build.log`：

```bash
grep -A5 "Memory region" apps/platform/ipro7ai_reef_demo/build/build.log
```

`ipro7ai_reef_demo` 預設設定的結果：

```text
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
```

- `flash` 是連結時的 Flash 上限。`ipro7ai_reef_demo` 預設連結 1 MB 版面（建置設定階段印出 `-- IPRO7 flash: 1M (default, on-chip)`）；Reef 的封裝內 Flash 回報 JEDEC `0xEF4015`（2 MB）時，可在 `.config` 加入 `CONFIG_IPRO7_FLASH_2M=y` 使用整顆 Flash。
- `flash` 百分比沒有超過，不代表放得進韌體分割區：請把 `Binary:` 顯示的 `.bin` 大小與分割表的韌體分割區比較。`partition_cfg_2M.toml` 的韌體分割區為 1180 KB。
- `ocram` 是晶片內的 OCRAM。AI 關閉時，這個區域是 256 KB 扣掉 BLE 使用的 `CONFIG_EM_SIZE`，建置設定階段印出 `-- AI disabled: OCRAM=256KB` 之類的訊息；AI 開啟時配置不同。各區域由哪些設定決定，見[建置系統與設定](../guides/build-system.md)。

`size` 動作列出 `.elf` 的總大小與各區段：

```bash
./build_freertos.sh size ipro7ai_reef_demo
```

```text
→ Size report for ipro7ai_reef_demo_IPRO7.elf

   text    data     bss     dec     hex filename
 235928   14008   49588  299524   49204 <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf
...
```

上面的數字取自 V2.2.0 的建置，依工具鏈版本與修改內容會有所不同。

## 腳本自動帶入的參數 { #script-defaults }

`build_freertos.sh` 從應用的設定檔讀出參數，Reef 不需另外指定：

| 項目 | 來源 |
|---|---|
| `--chip-variant` | 設定檔有 `CONFIG_IPRO7AI_REEF=y` 時為 `IPRO7AI`；`-c` 或 `IPRO_CHIP_VARIANT` 可覆寫 |
| `--pt` | `-P` 或 `IPRO_FLASH_PT`；兩者都沒有時不帶 `--pt`，由工具使用自己的預設分割表 |
| `reboot_dl` 與 `monitor` 的鮑率 | 設定檔的 `CONFIG_PLATFORM_UART_BAUDRATE`，未設定時 115200（`ipro7_jpeg_decode` 的 Reef 設定為 921600） |
| 燒錄鮑率 | 固定 921600 |

腳本不能傳 boot2 與 `mfg` 資料，`--chipname` 固定為 `ipro7`；這些情況請直接執行 IntelProCube，見[燒錄與序列埠](../get-started/flash-and-monitor.md#build-script)。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| `✗ Build failed`，最後 30 行有編譯錯誤 | 程式有錯 | 依錯誤訊息修正；完整記錄在 `build.log` |
| `✗ Flash failed`，工具輸出停在握手階段 | 板上韌體沒有回應 `reboot_dl`（沒有 shell、當掉或鮑率不同），或序列埠被終端程式占用 | 關閉終端程式；按住 SW1、按一下 SW2、放開 SW1 後只執行 `flash` |
| `✗ Flash tool not found: …` | 新開的終端機視窗沒有 `IPRO_FLASH_TOOL` | 重新執行步驟 1，或把 `export` 加進 shell 的啟動檔 |
| `✗ Binary not found: …` | `flash` 前沒有建置，或少了 `-d` | 加上 `build`，或加上建置時用的 `-d` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 未設定 `IPRO_SERIAL_PORT`，且接了多個序列埠 | 設定 `IPRO_SERIAL_PORT` 或加 `-p` |
| 主控台看不到修改後的文字 | 燒錄沒有成功，或看的是舊的輸出 | 確認 `Summary` 中 `flash` 為 ✓；重新執行步驟 3 |
| 改了 `.config` 但行為沒變 | 舊的建置結果仍在 | 執行 `clean build` |
| 改用其他應用後燒錄失敗或無法開機 | `IPRO_FLASH_PT` 仍指向前一個應用的分割表 | `unset IPRO_FLASH_PT`，依[分割表](../get-started/flash-and-monitor.md#partition-tables)以 `-P` 指定 |

## 下一步 { #next-steps }

- [建立第一個應用](first-own-app.md)：從零建立自己的應用。
- [測試應用](testing.md)：自動檢查應用的輸出。
- [macOS／Linux 命令列](../get-started/command-line.md)：`build_freertos.sh` 的全部動作、選項與限制。
- [建置系統與設定](../guides/build-system.md)：`.config` 鍵值、連結腳本與記憶體配置。
