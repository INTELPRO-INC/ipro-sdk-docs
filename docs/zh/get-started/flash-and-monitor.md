---
title: "燒錄與序列埠"
description: 以 IntelProCube 命令列工具燒錄 FreeRTOS 應用、各板的燒錄設定、build_freertos.sh flash 的行為，以及主控台鮑率與 serial_monitor.py。
migrate_from:
  - "getting-started.html#flashing"
  - "getting-started.html#serial-monitor"
  - "tools-debugging.html#flash-tool"
  - "tools-debugging.html#serial-monitor"
---

# 燒錄與序列埠

FreeRTOS 應用以 IntelProCube 命令列工具經序列埠燒錄，主控台也在同一個 UART 上。依下列步驟燒錄任何應用，再依應用的鮑率開啟主控台。Zephyr 映像改用 `west flash`，見[第一個 Zephyr 應用](first-app-zephyr.md)。

## 前置需求 { #prerequisites }

- IntelProCube v0.6.3 命令列工具：`ipro_iot_tool.exe`（Windows）、`ipro_iot_tool_macos`、`ipro_iot_tool_linux`。未包含於 V2.1.0，請洽 INTELPRO。
- 已建置的映像檔：`apps/<分類>/<應用>/build/build_out/<應用>_IPRO7.bin`；以 `DEFCONFIG=defconfig_<名稱>` 建置時位於 `build_<名稱>/build_out/`。
- 板子的序列埠：macOS `/dev/cu.usbserial-XXXX`、Linux `/dev/ttyUSB0`、Windows `COM5`。

## 燒錄工具 { #flash-tool }

`build_freertos.sh`、各應用的 `flash.sh` 與 `west flash` 依 `IPRO_FLASH_TOOL` 找工具；未設定時改找 PATH 上對應作業系統的執行檔。直接執行工具並以 `chips/...` 指定分割表時，請在 IntelProCube 目錄下執行。Windows 上也可用 VS Code Extension 的 `IPRO: Flash`，見 [VS Code Extension](../guides/vscode.md)。

每次燒錄用到的參數是 `--chipname ipro7`、`--chip-variant`（板子的 Flash 腳位設定，見下段）、`--port`、`--baudrate 921600`（應用 README 與腳本使用的燒錄鮑率）、`--firmware`，以及需要時的 `--pt`（分割表）。全部參數見[工具命令列](../reference/tools.md#flash-tool)。

`--chip-variant` 會把對應的 `flash_pin` 寫入工具目錄的 `chips/ipro7/eflash_loader/eflash_loader_cfg.ini`：`IPRO7` 寫入 `0x2`，`IPRO7AI` 寫入 `0x9`。工具沒有另外指定 Flash 腳位的參數，出廠值為 `0x2`。不帶 `--chip-variant` 的流程（`build_freertos.sh flash`、各應用的 `flash.sh`、`west flash`）沿用該檔當時的值，因此在 Reef 或 IPRO7AI EVK 上，先以 `--chip-variant IPRO7AI` 執行過一次工具，或確認該檔的值為 `0x9`。

!!! warning "以輸出判斷結果"
    工具即使燒錄失敗也會以 0 結束。輸出中出現 `[All Success]` 才算成功。

## 燒錄步驟 { #flashing }

<div class="ipro-steps" markdown>

1. **釋放序列埠**：結束正在監看同一序列埠的程式。

2. **進入下載模式**：板子正在執行含 shell 的 SDK 韌體時，以韌體目前的主控台鮑率送出 `reboot_dl`：

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 115200 --send reboot_dl --timeout 2
    ```

    否則依[各板設定](#board-settings)以按鍵或腳位進入。進入下載模式後，主控台不會有任何輸出。

3. **燒錄**：在 IntelProCube 目錄下執行。以下以 Reef 的 `ipro7ai_reef_demo` 為例，其他板子依[各板設定](#board-settings)替換 `--chip-variant` 與 `--pt`。

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

4. **確認並重置**：輸出出現 `[All Success]` 後重置板子，再依應用的鮑率開啟[主控台](#serial-monitor)。

</div>

## 各板設定 { #board-settings }

| | IPRO7AI Reef EVK | IPRO7AI EVK | IPRO7 EVB |
|---|---|---|---|
| `--chip-variant` | `IPRO7AI` | `IPRO7AI` | `IPRO7` |
| 分割表 | `chips/ipro7/partition/partition_cfg_2M.toml`（Reef 應用的 README） | AI 應用目錄內的 `.toml`，由應用的 `flash.sh` 帶入 | 依應用 README；SDK README 的範例不指定 `--pt` |
| 進入下載模式 | 按住 SW1（BOOT）、按一下 SW2（RESET）；U6 的 DTR／RTS 接 BOOT 與 RESET，可用自動下載線；或 `reboot_dl` | `reboot_dl`；手動方式見板卡頁 | `reboot_dl`，或 BOOT 腳位 |
| 主控台 | U6（SH1.0）上的 UART0，GPIO20 TX／GPIO21 RX | UART0，GPIO20 TX／GPIO21 RX | UART0，GPIO20 TX／GPIO21 RX |

IPRO7 EVB 的 `IPRO7`（`flash_pin` 為 `0x2`）依 SDK README 的對應；若握手成功後讀到 `flash jedec id: 00000000`，改以 `--chip-variant IPRO7AI`（`0x9`）再燒錄一次。

IPRO7AI EVK 的 `ipro7ai_evk_person_detect`、`ipro7ai_evk_rps` 與 `ipro7ai_evk_launcher` 隨附 `flash.sh`：第一次以 `--full` 寫入分割表、韌體與模型，之後只更新韌體時不加參數。腳本以環境變數 `PORT` 指定序列埠，以 `BAUD` 指定板上韌體目前的主控台鮑率（送出 `reboot_dl` 用，預設為該應用自己的鮑率）：

```bash
cd apps/ai/ipro7ai_evk_person_detect
PORT=/dev/cu.usbserial-XXXX BAUD=115200 ./flash.sh --full
```

板子的接線、跳線與手動進入下載模式的方式見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)、[IPRO7AI EVK](../hardware/boards/ipro7ai-evk.md) 與 [IPRO7 EVB](../hardware/boards/ipro7-evb.md)。

## 以 build_freertos.sh 燒錄 { #build-script }

`build_freertos.sh` 的動作可以串接，依序執行：

```bash
./build_freertos.sh ipro7_demo build flash monitor -p /dev/cu.usbserial-XXXX
```

- `flash`：以 `tools/serial_monitor.py` 在 115200 送出 `reboot_dl`，接著執行 `<工具> --chipname ipro7 --port <序列埠> --firmware <bin> --baudrate 921600`，並以 `[All Success]` 判斷結果。
- `monitor`：以 `tools/serial_monitor.py` 開啟序列埠並送出 `reboot`，讀取 `-t` 秒（預設 30）。
- 序列埠：`-p`，否則 `IPRO_SERIAL_PORT`，否則唯一接上的 USB 序列埠。
- 替代設定：加上 `-d defconfig_<名稱>`。分開執行 `build` 與 `flash` 時兩次都要加，`flash` 才會找到 `build_<名稱>/` 下的映像檔。

!!! warning "腳本的固定值不一定適用所有板子"
    - **不帶 `--chip-variant`**：沿用工具 ini 中的 `flash_pin`。Reef 與 IPRO7AI EVK 需要 `0x9`，見[燒錄工具](#flash-tool)。
    - **不帶 `--pt`**：工具寫入自己的預設分割表。需要特定分割表時（Reef 應用的 `partition_cfg_2M.toml`、IPRO7AI EVK AI 應用的 `.toml`），請直接執行工具或應用的 `flash.sh`。
    - **`reboot_dl` 與 `monitor` 固定使用 115200 baud**：主控台為 921600 baud 或沒有 shell 的韌體收不到 `reboot_dl`，請手動進入下載模式，並改以 `python3 tools/serial_monitor.py <序列埠> --baud 921600` 監看。`monitor` 也會先送出 `reboot`，讓板子重新開機。
    - **`flash` 不會先建置**：映像檔不存在時會停止，請在前面加上 `build`。
    - **`monitor` 的結束碼**：逾時、按 ++ctrl+c++，或 `-w` 比對到不含 `PASSED` 的文字時，結束碼不是 0，腳本把它記為失敗並停止後面的動作。把 `monitor` 放在最後一個動作。

## 序列埠主控台 { #serial-monitor }

FreeRTOS 應用的主控台在 UART0（GPIO20 TX／GPIO21 RX），8N1。鮑率由應用 `.config` 的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200。

| 鮑率 | 應用 |
|---|---|
| 115200 | 多數應用，包括 `ipro7ai_reef_demo`、`ipro7_demo`、`ipro7ai_evk_person_detect` 與 BLE 應用 |
| 921600 | `ipro7ai_evk_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_epd_el036` 等 |
| 2000000 | Zephyr 映像（`ipro7_evb`、`ipro7ai_evk`） |

替代設定檔的鮑率可能不同，例如 `ipro7ai_evk_demo` 的 `config_*` 與 `ipro7_uvc_cam` 的 `defconfig_reef_*` 為 115200。以實際建置所用的設定檔為準（沒有輸出表示未設定，即 115200）：

```bash
grep CONFIG_PLATFORM_UART_BAUDRATE apps/platform/ipro7ai_reef_demo/.config
```

`ipro_enc28j60_test`、`ipro_gh7007_test`、`ipro_gh7007_video` 與 `ipro_pio_sdh_test` 的主控台走 USB CDC，不在 UART0。

### tools/serial_monitor.py { #serial-monitor-py }

```text
python3 tools/serial_monitor.py <序列埠> [--baud 115200] [--timeout 30] [--send CMD] [--wait-for PATTERN] [--log FILE]
```

`--baud` 預設 115200；`--timeout 0` 會持續讀取，直到按 ++ctrl+c++。各選項與結束碼見[工具命令列](../reference/tools.md#serial-monitor)。

```bash
# 持續監看（115200）
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0

# 921600 的應用，監看 60 秒並存檔
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 60 --log console.log

# 送出指令並讀取回應
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 5
```

- 腳本只使用 Python 標準函式庫的 termios，不需 pyserial，在 macOS 與 Linux 上執行。Windows 請用 VS Code Extension 的 Serial Monitor 或其他序列埠終端程式。
- 它不是互動式終端：每次只送出 `--send` 的一行。需要連續輸入時改用互動式序列埠終端程式。
- macOS 使用 `/dev/cu.*`，不要用 `/dev/tty.*`：後者會等待 carrier detect 訊號而卡住。
- 燒錄前結束監看，釋放序列埠。

## 確認結果 { #verify }

- 燒錄輸出出現 `[All Success]`。
- 重置後主控台出現應用的開機訊息；啟用 shell 的 FreeRTOS 應用會顯示 `ipro />` 提示字元，輸入 `help` 可列出指令。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 輸出沒有 `[All Success]`，握手失敗 | 板子不在下載模式，或序列埠被其他程式占用 | 依[各板設定](#board-settings)進入下載模式；結束監看程式 |
| 握手成功，但出現 `flash jedec id: 00000000` 與 `IPRO FLASH MATCH TYPE FAIL` | `flash_pin` 不符合板子 | 以正確的 `--chip-variant` 燒錄（IPRO7AI EVK 與 Reef 為 `IPRO7AI`）；IPRO7 EVB 以 `IPRO7` 仍出現此訊息時，改用 `IPRO7AI` |
| `Flash tool not found` | 未設定 `IPRO_FLASH_TOOL`，PATH 上也找不到工具 | 設定 `IPRO_FLASH_TOOL` |
| `Binary not found`，提示 `Run 'build' first.` | `flash` 不會自動建置 | 在 `flash` 前加上 `build`；使用替代設定時，`flash` 也要加 `-d` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 接了多個 USB 序列埠 | 以 `-p` 或 `IPRO_SERIAL_PORT` 指定 |
| 主控台亂碼 | 鮑率不符 | 依應用的 `CONFIG_PLATFORM_UART_BAUDRATE` 設定 `--baud` |
| 主控台完全沒有輸出 | 板子停在下載模式，或 macOS 上使用了 `/dev/tty.*` | 重置板子；改用 `/dev/cu.*` |
| IPRO7AI EVK 的 AI 應用顯示 `NO MFG PARTITION` | 板上是工具的預設分割表，沒有 `mfg` 分割區 | 以應用的 `./flash.sh --full` 重新燒錄 |

## 下一步 { #next-steps }

- [工具命令列](../reference/tools.md)：`build_freertos.sh`、`serial_monitor.py` 與 Zephyr 腳本的完整選項。
- [建置與燒錄流程](../tutorials/build-and-flash.md)
- [除錯與疑難排解](../reference/debugging.md)
