---
title: "燒錄與序列埠"
description: IPRO7AI Reef EVK 的燒錄與主控台參考：進入下載模式的四種方式、IntelProCube 命令列參數與分割表、boot2 與 mfg 資料、build_freertos.sh flash，以及主控台與序列埠辨識。
migrate_from:
  - "getting-started.html#flashing"
  - "getting-started.html#serial-monitor"
  - "tools-debugging.html#flash-tool"
  - "tools-debugging.html#serial-monitor"
---

# 燒錄與序列埠

FreeRTOS 應用以 IntelProCube 命令列工具經 UART0 燒錄，主控台也在同一個 UART 上；在 IPRO7AI Reef EVK 上，兩者都經過除錯排座 U6。本頁整理 Reef 的所有燒錄方式、各應用需要的分割表與額外映像，以及怎麼開啟主控台、怎麼認出序列埠。第一次操作請先完成[第一個 FreeRTOS 應用](first-app-freertos.md)。

## 前置需求 { #prerequisites }

- IntelProCube v0.6.3：`ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`，見[準備開發環境](environment.md#intelprocube)。
- 已建置的映像檔：`apps/<分類>/<應用>/build/build_out/<應用>_IPRO7.bin`；以 `DEFCONFIG=defconfig_<名稱>` 建置時在 `build_<名稱>/build_out/`。
- 主控台線接在 U6，見[設定開關與接線](first-app-freertos.md#connect)。序列埠寫法：macOS `/dev/cu.usbserial-XXXX`、Linux `/dev/ttyUSB0`、Windows `COM5`。

## 燒錄工具 { #flash-tool }

在 IntelProCube 目錄下執行命令列工具：它從 `chips/` 讀取晶片設定，`--pt chips/...` 這類相對路徑也以這個目錄為準。Reef 用到的參數：

| 參數 | Reef 的值 | 說明 |
|---|---|---|
| `--chipname` | `ipro7` | IPRO7 與 IPRO7AI |
| `--chip-variant` | `IPRO7AI` | Flash 腳位設定：`IPRO7AI` 為 `0x9`（Reef 的 QFN56），`IPRO7` 為 `0x2`。工具把它寫入 `<IntelProCube>/chips/ipro7/eflash_loader/eflash_loader_cfg.ini` |
| `--port` | 主控台序列埠 | U6 的轉接器，或 Debug Probe 名稱結尾 `02` 的序列埠 |
| `--baudrate` | `921600` | 燒錄鮑率，與應用的主控台鮑率無關 |
| `--firmware` | 應用的 `.bin` | 建置產出的映像檔 |
| `--pt` | 分割表 | `.toml` 路徑，或 `chips/ipro7/partition/` 下的檔名，見[分割表](#partition-tables) |
| `--boot2` | boot2 映像 | 使用 boot2 的應用（`ipro_ble_remote`），見[首次燒錄 ipro_ble_remote](#boot2-ab) |
| `--mfg` | `mfg` 分割區資料 | AI 模型與 Teach 模式資料（`ipro_reef_teach`），見 [ipro_reef_teach](#mfg) |
| `--skip-ota` | — | 不產生 OTA 檔；`ipro_reef_teach` 使用自己的分割表時加上 |

`--help` 列出全部參數。

!!! warning "以輸出判斷結果"
    工具即使燒錄失敗也會以 0 結束。輸出的最後一行是 `[All Success]` 才算成功。

## 進入下載模式 { #download-mode }

燒錄前，IPRO7AI 必須在開機 ROM 的下載模式。進入後主控台沒有任何輸出，直到重置為止。

| 方式 | 操作 | 適用情況 |
|---|---|---|
| 按鍵 | 按住 **SW1（BOOT）**，按一下 **SW2（RESET）**，再放開 SW1 | 任何時候；板上韌體當掉或沒有 shell 時也可用 |
| `reboot_dl` | 在主控台輸入 `reboot_dl`，畫面印出 `reboot to download mode` | 板上正在執行含 shell 的 SDK 韌體；`build_freertos.sh flash` 自動使用這個方式 |
| 自動下載線 | 轉接器的 DTR 接 U6 第 5 腳（BOOT），RTS 接第 6 腳（RESET），板上各經 1 kΩ 接到 GPIO41 與重置腳；這種自動下載線不必按鍵即可進入下載模式 | 轉接器有 DTR 與 RTS 腳 |
| IPRO Debug Probe | 在探針名稱結尾 `02` 的序列埠送出控制字，見下方步驟 | 以 Debug Probe 連接 U6 |

以 Debug Probe 進入下載模式（macOS 為例，在 SDK 根目錄執行）：

<div class="ipro-steps" markdown>

1. **拉高 BOOT 並重置**：依序送出 `IPRODL_1` 與 `IPRORST_RESET`。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
    ```

    每行印出 `[serial_monitor] Sent: …` 與 `[serial_monitor] TIMEOUT after 1s`（沒有指定 `--wait-for` 時的正常結尾）；之後主控台不再有輸出。

2. **燒錄**：保持 BOOT 拉高，以同一個 `02` 序列埠執行[燒錄步驟](#flashing)。

3. **放開 BOOT 並重置**：送出 `IPRODL_0` 與 `IPRORST_RESET`，板子以新韌體開機。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_0 --timeout 1
    python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 3
    ```

</div>

## 燒錄步驟 { #flashing }

<div class="ipro-steps" markdown>

1. **釋放序列埠**：關閉所有開著主控台序列埠的終端程式。

2. **進入下載模式**：依[進入下載模式](#download-mode)任一方式。主控台不再有輸出。

3. **燒錄**：在 IntelProCube 目錄下執行。以 `ipro7ai_reef_demo` 為例，其他應用依[分割表](#partition-tables)替換 `--pt` 並加上需要的參數。

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

    輸出開頭列出這次燒錄的參數，結尾是驗證結果（節錄，時間戳記省略）：

    ```text
    [...] - Chip name is ipro7
    [...] - Serial port is /dev/cu.usbserial-XXXX
    [...] - Baudrate is 921600
    [...] - Firmware is <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ...
    [...] - flash jedec id: ef401500
    ...
    [...] - Verify success
    [...] - Program Finished
    ...
    [...] - [All Success]
    ```

4. **重置並開啟主控台**：按 SW2（RESET）讓板子以新韌體開機，再依應用的鮑率開啟[主控台](#serial-monitor)。

</div>

## 分割表 { #partition-tables }

分割表決定韌體、`mfg`（AI 模型）與其他資料在 Flash 中的位置。IntelProCube 隨附通用的分割表（在 `<IntelProCube>/chips/ipro7/partition/`，例如 `partition_cfg_2M.toml`）；需要特殊配置的應用把自己的 `.toml` 放在應用目錄。

| 應用（Reef 設定） | `--pt` | 其他參數 |
|---|---|---|
| `ipro7ai_reef_demo`（`.config`、`defconfig_wifi_ipro6s`） | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro7_uvc_cam`（`defconfig_reef_ov5640`、`defconfig_reef_rps`） | `chips/ipro7/partition/partition_cfg_2M.toml` | — |
| `ipro_ble_remote`（`defconfig_reef`） | `<SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml` | 首次燒錄加 `--boot2`，見[下一節](#boot2-ab) |
| `ipro_reef_teach`（`.config`） | `<SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml` | `--skip-ota`；首次燒錄加 `--mfg`，見 [ipro_reef_teach](#mfg) |
| 其他 Reef 應用 | 依該應用 README | — |

`ipro7ai_reef_demo` 預設連結 1 MB 的 Flash 版面，放得進兩種封裝內 Flash；開機訊息若顯示 JEDEC `0xEF4015`（2 MB），可在 `.config` 加入 `CONFIG_IPRO7_FLASH_2M=y` 讓連結器使用整顆 Flash。

## 首次燒錄 ipro_ble_remote（boot2 與 A/B 分割表） { #boot2-ab }

`ipro_ble_remote` 的 Reef 設定支援 BLE OTA，需要 boot2 與 A/B 兩個韌體槽。第一次以有線方式燒錄時，一併寫入 boot2 與應用自己的分割表：

<div class="ipro-steps" markdown>

1. **建置**

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    產出 `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`。

2. **進入下載模式並燒錄**：boot2 映像隨 IntelProCube 提供，不在 SDK 內。

    ```bash
    cd <IntelProCube>
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
        --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
        --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
    ```

    輸出結尾為 `[All Success]`。

3. **確認**：按 SW2 重置，在 115200 baud 的主控台看到 boot2 標題 `[BOOT2] IPRO7 Boot2 v0.5.2`，接著應用印出 `[BLE] Advertising: IPRO-Remote`。

</div>

!!! warning "不要用 partition_cfg_2M.toml 做 OTA"
    在 Reef 上以標準的 `partition_cfg_2M.toml` 燒錄 `ipro_ble_remote` 後執行 OTA，新韌體會寫進一個 boot2 從不開機的槽（0x12A000）。要用 OTA，一定要以上面的 boot2 與 `partition_cfg_2M_remote_ab.toml` 燒錄。OTA 的步驟見 [OTA 韌體更新](../guides/ota.md)。

## ipro_reef_teach（mfg 資料） { #mfg }

Edge AI 韌體 `ipro_reef_teach` 使用自己的分割表，`mfg` 分割區存放模式設定與聲紋模型。第一次燒錄時一併寫入 `mfg` 資料：

```bash
make -C apps/ai/ipro_reef_teach
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 --skip-ota \
    --pt <SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml \
    --firmware <SDK>/apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin \
    --mfg <SDK>/reef_teach_mfg.bin
```

重置後主控台（115200）出現 `RTCH:   mode: image …`，USB-C 上出現 USB 攝影機與序列埠（`3896:0705`）。之後只更新韌體時省略 `--mfg`，模式與模型會保留。模式切換與 IPRO AI Studio 的操作見 [IPRO AI Teach](../teach/firmware.md)。

## 以 build_freertos.sh 燒錄 { #build-script }

在 macOS／Linux 上，`build_freertos.sh` 的 `flash` 動作依下列順序工作：

1. 找到映像檔：`build/`，或以 `-d defconfig_<名稱>` 指定的 `build_<名稱>/`。不存在時停止並提示 `Run 'build' first.`。
2. 找到工具：`IPRO_FLASH_TOOL`，否則 PATH 上的 `ipro_iot_tool_macos`／`ipro_iot_tool_linux`。
3. 找到序列埠：`-p`，否則 `IPRO_SERIAL_PORT`，否則唯一接上的 `/dev/cu.usbmodem*`、`/dev/cu.usbserial*`、`/dev/ttyACM*` 或 `/dev/ttyUSB*`。
4. 以應用的主控台鮑率（`CONFIG_PLATFORM_UART_BAUDRATE`，未設定時 115200）送出 `reboot_dl`，等 2 秒。
5. 執行 `<工具> --chipname ipro7 --chip-variant <變體> --port <序列埠> --firmware <bin> --baudrate 921600 [--pt <分割表>]`。變體：`-c`，否則 `IPRO_CHIP_VARIANT`，否則依設定檔判斷（Reef 設定為 `IPRO7AI`）。分割表：`-P`，否則 `IPRO_FLASH_PT`，否則不帶 `--pt`。
6. 輸出含 `[All Success]` 時印出 `✓ Flash succeeded`，否則 `✗ Flash failed`。

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

`-P` 請給 `.toml` 的完整路徑：腳本在目前目錄執行工具，不會切換到 IntelProCube 目錄。

!!! note "腳本做不到的事"
    - 不能傳 `--boot2`、`--mfg` 或 `--skip-ota`：`ipro_ble_remote` 的首次燒錄與 `ipro_reef_teach` 的 `mfg` 資料請直接執行工具。
    - `--chipname` 固定為 `ipro7`，不能燒錄 IPRO6S 映像。
    - 板上韌體沒有 shell 或當掉時收不到 `reboot_dl`：先以按鍵進入下載模式。
    - `flash` 不會先建置；分開執行 `build` 與 `flash` 時，兩次都要加相同的 `-d`。

## 序列埠主控台 { #serial-monitor }

主控台是 UART0（GPIO20 TX／GPIO21 RX，U6 第 3／4 腳），8N1、無流量控制。鮑率由應用設定檔的 `CONFIG_PLATFORM_UART_BAUDRATE` 決定，未設定時為 115200：

| 鮑率 | Reef 設定 |
|---|---|
| 115200 | `ipro7ai_reef_demo`（兩個設定）、`ipro_reef_teach`、`ipro_ble_remote`、`ipro_throughput_test`、`ipro_le_audio_headset`、`ipro7_uvc_cam`（兩個 Reef 設定）、`ipro_ai_link`、`ipro_agora_sentino` |
| 921600 | `ipro7_jpeg_decode`（`defconfig_reef`） |

查詢某個設定檔的鮑率（沒有輸出表示未設定，即 115200）：

```bash
grep CONFIG_PLATFORM_UART_BAUDRATE apps/multimedia/ipro7_jpeg_decode/defconfig_reef
```

### 互動式終端程式 { #terminal }

要輸入 shell 指令，請用互動式終端程式：

=== "macOS"

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    結束：++ctrl+a++，++k++，回答 `y`。也可以用 `minicom`、`picocom`（以 Homebrew 安裝）。

=== "Linux"

    ```bash
    picocom -b 115200 /dev/ttyUSB0
    ```

    結束：++ctrl+a++，++ctrl+x++。也可以用 `minicom -D /dev/ttyUSB0 -b 115200` 或 `screen`。

=== "Windows"

    PuTTY：Connection type 選 **Serial**，Serial line 填 `COM5`，Speed 填 `115200`，按 **Open**。也可以用 Tera Term，或 VS Code Extension 的 `IPRO: Serial Monitor`。

燒錄前一定要先關閉終端程式，否則工具開不了序列埠。

### tools/serial_monitor.py { #serial-monitor-py }

SDK 隨附的非互動式主控台工具，供腳本與自動化使用（macOS／Linux；只使用 Python 標準函式庫的 termios，不需 pyserial）。它開啟序列埠、可先送出一行指令，然後讀取輸出直到逾時或比對到指定文字。

```text
python3 tools/serial_monitor.py <序列埠> [--baud 115200] [--timeout 30] [--send CMD] [--wait-for REGEX] [--log FILE]
```

| 選項 | 說明 |
|---|---|
| `--baud` | 鮑率，預設 115200 |
| `--timeout` | 讀取秒數，預設 30；`0` 表示持續讀取到按 ++ctrl+c++ |
| `--send` | 開始讀取前送出的一行（自動加上 CR LF） |
| `--wait-for` | 比對到這個正規表示式就結束 |
| `--log` | 同時把原始輸出存到檔案 |

| 結束碼 | 意義 |
|---|---|
| 0 | `--wait-for` 比對到的文字含 `PASSED` |
| 1 | 比對到的文字不含 `PASSED` |
| 2 | 逾時，沒有比對到（沒有指定 `--wait-for` 時，讀完一定是 2） |
| 3 | 開啟序列埠或送出指令失敗 |

```bash
# 送出指令並讀 10 秒
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# 重新開機，等到 shell 就緒，並存檔
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot --wait-for "shell ready" --timeout 15 --log boot.log
```

### macOS 的序列埠 { #macos-cu }

macOS 上每個序列埠有 `/dev/cu.*` 與 `/dev/tty.*` 兩個名稱。一律使用 `/dev/cu.*`：`/dev/tty.*` 會等待 carrier detect 訊號，開啟後卡住沒有輸出。

## 辨識序列埠 { #ports }

| 連接方式 | macOS | Linux | Windows |
|---|---|---|---|
| U6 上的 USB 轉 UART 轉接器 | `/dev/cu.usbserial-XXXX`（依轉接器而定） | 多半為 `/dev/ttyUSB0` | 裝置管理員中新增的 COM 埠 |
| IPRO Debug Probe | 兩個 `/dev/cu.usbmodem…`：結尾 `02` 是主控台（UART 橋接），`04` 是 CCI 橋接 | 兩個 `/dev/ttyACM*` | 兩個 COM 埠 |

IPRO Debug Probe 在 USB 上的名稱是 `IPRO7 CMSIS_DAP`。在 Linux 與 Windows 上分辨兩個序列埠：以 115200 分別開啟，按 SW2 重置，顯示開機訊息的那一個就是主控台。

Reef 的 USB-C 不是主控台。部分應用會讓板子在 USB-C 上以 INTELPRO 的 VID `0x3896` 出現為 USB 裝置：

| 應用 | VID:PID | 主機看到的裝置 |
|---|---|---|
| `ipro_reef_teach` image 模式 | `3896:0705` | USB 攝影機與序列埠（瀏覽器中名稱為「IPRO7 UVC Cam」） |
| `ipro_reef_teach` voice 模式 | `3896:0720` | 序列埠（CDC-ACM） |
| `ipro_reef_teach` sensor 模式 | `3896:0721` | 序列埠（CDC-ACM） |
| `ipro7_uvc_cam` | `3896:0701` | USB 攝影機 |
| `ipro_ai_link` | `3896:0704` | 序列埠（CDC） |
| `ipro7ai_reef_demo` 執行 `mic usb` 時 | `3896:0003` | USB 麥克風（UAC） |
| `ipro_agora_sentino` | `3896:0138`、`3896:0104` | USB 網路介面（NCM）、序列埠（CDC） |
| `ipro_le_audio_headset` | `3896:0001` | USB 音訊（UAC，測試用 PID） |

查看主機上的 USB 裝置：macOS 用 `system_profiler SPUSBDataType`，Linux 用 `lsusb`（例如列出 `ID 3896:0705`），Windows 在裝置管理員的裝置內容 →「詳細資料」→「硬體識別碼」（例如 `USB\VID_3896&PID_0705`）。

## 確認結果 { #verify }

- 燒錄輸出的最後一行是 `[All Success]`。
- 按 SW2 重置後，主控台以應用的鮑率顯示開機訊息；含 shell 的應用按 ++enter++ 出現 `ipro />`，輸入 `help` 列出指令。
- 使用 USB 功能的應用，主機上出現上表的 VID:PID。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| 工具停在握手階段，沒有 `[All Success]` | 板子不在下載模式，或序列埠被終端程式占用 | 關閉終端程式；以按鍵進入下載模式後重試 |
| 出現 `flash jedec id: 00000000` 與 `IPRO FLASH MATCH TYPE FAIL` | `--chip-variant` 不是 `IPRO7AI`，Flash 腳位錯誤 | 加上 `--chip-variant IPRO7AI` |
| 工具找不到分割表或 boot2 檔案 | 相對路徑不是以 IntelProCube 目錄為準 | 先 `cd <IntelProCube>`；SDK 內的檔案用完整路徑 |
| `✗ Flash tool not found: ipro_iot_tool_macos` | 未設定 `IPRO_FLASH_TOOL`，PATH 上也找不到工具 | `export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` |
| `✗ Binary not found: …`，提示 `Run 'build' first.` | `flash` 不會先建置，或少了建置時的 `-d` | 在 `flash` 前加 `build`；加上相同的 `-d` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 接了多個 USB 序列埠（Debug Probe 本身就有兩個） | 以 `-p` 或 `IPRO_SERIAL_PORT` 指定主控台序列埠 |
| `No serial port found: pass -p PORT or set IPRO_SERIAL_PORT` | 沒有偵測到 USB 序列埠 | 檢查轉接器與驅動程式，見[準備開發環境](environment.md#usb-serial) |
| 燒錄成功，但重置後主控台沒有輸出 | 板子仍在下載模式（BOOT 被 DTR 或探針拉住），或鮑率、RX／TX 不對 | 放開 BOOT（探針送 `IPRODL_0`）後按 SW2；確認鮑率；對調 RX 與 TX |
| 主控台亂碼 | 鮑率不符 | 依[主控台](#serial-monitor)的鮑率重新開啟 |
| macOS 開啟序列埠後卡住 | 用了 `/dev/tty.*` | 改用 `/dev/cu.*` |
| `ipro_reef_teach` 顯示 `NO MFG PARTITION` | 板上不是 `partition_reef_teach.toml` 的分割表 | 依 [ipro_reef_teach](#mfg) 以應用的分割表與 `--mfg` 重新燒錄 |

## 下一步 { #next-steps }

- [建置與燒錄流程](../tutorials/build-and-flash.md)：日常的修改、建置、燒錄與監看迴圈。
- [macOS／Linux 命令列](command-line.md)：`build_freertos.sh` 的全部動作與選項。
- [除錯與疑難排解](../reference/debugging.md)
