---
title: "IPRO7AI EVK"
description: IPRO7AI EVK 的板上功能、J6 接線、上手步驟、launcher 與板級展示韌體、支援範例與 SDK 板級支援
migrate_from:
  - "applications.html#ipro7ai-evk-demo"
  - "applications.html#ipro7ai-evk-launcher"
---

# IPRO7AI EVK

IPRO7AI EVK 是把 IPRO7AI 模組裝在子板上的開發套件，板上有 2.4 吋 LCD、SC101IOT 相機、PDM 麥克風、喇叭、micro-SD 卡槽與 Li-ion 充電電路，適合影像 AI 與人機介面開發。它和 [IPRO7AI Reef EVK](reef-evk.md) 是不同的板子：Reef 沒有 LCD，相機與音訊配置也不同。

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>模組，裝在 EVK 子板上</span></div>
<div><strong>1 MB</strong><span>封裝內 Flash</span></div>
<div><strong>2.4"</strong><span>ST7789P3 LCD，240 × 320</span></div>
<div><strong>SC101IOT</strong><span>相機，1280 × 720 DVP</span></div>
<div><strong>J6</strong><span>上電前接好 VDDIO1</span></div>
</div>

## 板上功能 { #features }

| 區塊 | 內容 |
|---|---|
| 核心 | IPRO7AI：NPU、封裝內 8 MB PSRAM 與 1 MB Flash |
| 顯示 | HEM LCM-T2D4BP-084：2.4 吋 IPS、240 × 320、ST7789P3，4 線 SPI（SPI0），3.3 V |
| 相機 | SmartSens SC101IOT，1280 × 720 DVP，SCCB 位址 0x68，接在 FPC CN5 |
| 喇叭 | 晶片 DAC（GPIO23）→ TPA2037D1 單聲道 D 類擴大機 → J1 |
| 麥克風 | Infineon IM69D129 PDM 麥克風，經 AUADC |
| 儲存 | micro-SD 卡槽（SDH 控制器，4-bit，可切斷電源），FatFS 掛載於 `sd:/` |
| 電源 | USB-C（CN1）供電與 USB 裝置；Li-ion 電池接頭 CN4 與充電電路 |
| 除錯 | UART0 主控台（GPIO20／21）；JTAG 腳位；RST 按鍵（SW1，板上唯一按鍵） |

### 腳位 { #pinout }

| 區塊 | 腳位 |
|---|---|
| 顯示 | CS GPIO10、背光 GPIO12、RST GPIO14、SCLK GPIO15、MOSI GPIO16、DC GPIO17 |
| 相機 | D0–D7 = GPIO0–7、SCL GPIO36、SDA GPIO37、PCLK GPIO38、VSYNC GPIO39、HSYNC GPIO40、MCLK GPIO41、RST GPIO35 |
| 喇叭 | DAC GPIO23；擴大機致能 GPIO22，高電位開啟 |
| 麥克風 | CLK GPIO18、DAT GPIO19 |
| micro-SD | 電源 GPIO27、D1 GPIO28、D0 GPIO29、CLK GPIO30、CMD GPIO31、D3 GPIO32、D2 GPIO33、偵測 GPIO34 |
| 主控台 | UART0 TX GPIO20、RX GPIO21 |
| JTAG | TMS GPIO24、TDI GPIO25、TCK GPIO26、TDO GPIO11 |
| 備用 | GPIO13（只接到 J3） |

GPIO22 在晶片上也是 DAC B 通道，EVK 把它用作擴大機致能，所以音訊輸出為單聲道。GPIO41 同時是開機 strap 與相機 MCLK。

!!! warning "上電前接好 J6"
    J6（2×5）的腳 3 是 VDDIO1 的電源輸入，VDDIO1 供電給 GPIO0–9、GPIO36–41（相機的 DVP 與 SCCB）以及封裝內 Flash。用一條跳線把**腳 3 接到腳 7（2.8 V）**；兩腳不相鄰，跳線帽套不上。VDDIO1 在重置時沒有電，晶片讀不到 Flash，會進入下載模式而不是正常開機。

## 上手 { #quick-start }

以 `ipro7ai_evk_launcher` 為例：一個映像同時使用相機、LCD、麥克風與喇叭，並用 NPU 辨識手勢換頁。

<div class="ipro-steps" markdown>

1. **接線**：依上方警告接好 J6 腳 3–腳 7，接上 USB-C，並把 USB 轉 UART 線接到 UART0（GPIO20 TX／GPIO21 RX）。

2. **建置**

    ```bash
    make -C apps/platform/ipro7ai_evk_launcher
    ```

    產出：`apps/platform/ipro7ai_evk_launcher/build/build_out/ipro7ai_evk_launcher_IPRO7.bin`

3. **準備燒錄工具**：EVK 的 Flash 腳位設定是 `0x9`。直接執行 IntelProCube 命令列工具時加上 `--chip-variant IPRO7AI`，工具會把設定檔 `chips/ipro7/eflash_loader/eflash_loader_cfg.ini` 的 `flash_pin` 寫成 `0x9`。應用目錄的 `flash.sh` 不帶 `--chip-variant`，沿用設定檔當時的值；若讀到的 Flash JEDEC ID 是 `00000000` 並出現 `IPRO FLASH MATCH TYPE FAIL`，表示腳位設定不對，不是板子壞掉。

4. **進入下載模式**：板上韌體執行中時，`flash.sh` 會先送出 `reboot_dl`。全新的板子或韌體無法執行時，手動操作：

    1. 把 J6 腳 3 上的跳線從腳 7 移到腳 1（或直接拔掉），讓 VDDIO1 斷電。
    2. 按 RST（SW1）。
    3. 把跳線接回腳 3–腳 7；寫入 Flash 時 VDDIO1 必須有電。

    在下載模式下主控台沒有任何輸出，這是正常的。

5. **燒錄分割表、韌體與手勢模型**：第一次使用 `--full`，之後只換韌體時不加參數。

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube 目錄>/ipro_iot_tool_macos
        cd apps/platform/ipro7ai_evk_launcher
        PORT=/dev/cu.usbserial-XXXX ./flash.sh --full
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube 目錄>/ipro_iot_tool_linux
        cd apps/platform/ipro7ai_evk_launcher
        PORT=/dev/ttyUSB0 ./flash.sh --full
        ```

    === "Windows"

        `flash.sh` 是 bash 腳本；在 Windows 上於 IntelProCube 目錄直接執行工具：

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI --port COM5 --baudrate 921600 --skip-ota `
            --pt <SDK>\apps\platform\ipro7ai_evk_launcher\partition_cfg_1M_launcher.toml `
            --firmware <SDK>\apps\platform\ipro7ai_evk_launcher\build\build_out\ipro7ai_evk_launcher_IPRO7.bin `
            --mfg <SDK>\apps\ai\ipro7ai_evk_rps\model\rps_v3.inm
        ```

    `flash.sh` 以輸出中的 `[All Success]` 判斷成功，完成後按 RST 重置。

6. **確認結果**：主控台為 921600 baud。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --send "app status" --timeout 10
    ```

    LCD 顯示相機預覽；手掌（PAPER）在框內停留約半秒會換到下一頁。

</div>

## 範例韌體 ipro7ai_evk_launcher { #ipro7ai-evk-launcher }

兩個模型共用一顆 NPU：手勢分類器（剪刀石頭布模型）負責換頁，YOLOv8 負責人物／寵物偵測。

| 頁面 | 顯示 | ROCK（石頭） | SCISSORS（剪刀） |
|---|---|---|---|
| 1 CAMERA | 即時預覽、手勢框與辨識結果 | 凍結／恢復預覽 | 鏡像開／關 |
| 2 DETECT | 即時預覽加上人物（綠）／寵物（黃）框 | 寵物框開／關 | 鏡像開／關 |
| 3 VOICE | 麥克風波形與峰值（dBFS） | 錄 5 秒後由喇叭播放 | 重播上一段 |
| 4 ABOUT | 各區塊狀態：模型來源、NPU 與相機速率、麥克風、喇叭、SD 卡、記憶體 | — | — |

PAPER（布）切換到下一頁。沒有相機時，可用 shell 的 `app next`、`app select`、`app alt` 代替手勢。

模型來源：

| 卡片上的檔案 | SDK 中的來源 | 用途 |
|---|---|---|
| `sd:/models/gesture.inm` | `apps/ai/ipro7ai_evk_rps/model/rps_v3.inm` | 選用；與 `mfg` 分割區內的模型相同，卡片上有檔案時優先使用 |
| `sd:/models/person.inm` | `apps/platform/ipro7_demo/demo/ai/ai_model/person_pet_detect.inm` | DETECT 頁必需；放不進 `mfg` 分割區，只能放在 SD 卡 |

Flash 版面（`partition_cfg_1M_launcher.toml`）：韌體 320 KB 從 `0x3000` 開始，`mfg` 688 KB 從 `0x53000` 開始；`ipro7ai_evk_person_detect` 與 `ipro7ai_evk_rps` 使用相同版面，三者可互換。此映像啟用 NPU，不含藍牙。

常用 shell 指令：

```text
app status               所有區塊的狀態
app page <1..4>          跳到指定頁
app rec [秒]             錄音後播放（VOICE 頁）
spk tone [hz] [ms]       只測喇叭
mic level [秒]           只測麥克風（峰值／RMS，dBFS）
sd ls [路徑]             列出 SD 卡內容
```

## 板級展示 ipro7ai_evk_demo { #ipro7ai-evk-demo }

`ipro7ai_evk_demo` 是 EVK 的板級展示與 bring-up 工具，每個區塊各有一組 shell 指令：`lcd`（顯示）、`cam`（相機）、`spk`（喇叭）、`mic`（麥克風）、`vbat` 與 `adc`（讀取 SoC 自身的供電電壓與一般 GPADC 通道）、`sd`（micro-SD）、`vid`（SD 卡影片播放），以及 `config_bt` 設定中的 `bt`（BLE 與 LE Audio 單播 sink）。

NPU 與 BLE 無法同時放進 OCRAM，因此依用途選擇設定檔：

| 設定 | 內容 | 主控台 |
|---|---|---|
| `.config`（預設） | SD 卡影片展示，不含藍牙與 NPU，不自動播放 | 921600 |
| `config_ai` | NPU、相機、顯示、音訊、SD 卡；不含藍牙 | 115200 |
| `config_bt` | BLE 與 LE Audio、相機、顯示、音訊、SD 卡；不含 NPU | 115200 |
| `config_autoplay` | 與 `config_bt` 相同，開機自動播放影片 | 115200 |
| `config_video` | SD 卡影片展示，自動播放 | 115200 |

```bash
make -C apps/platform/ipro7ai_evk_demo DEFCONFIG=config_bt   # 輸出於 build_config_bt/build_out/
```

也可以 `cp config_bt .config && make clean && make` 切換預設設定。燒錄時使用 `--chip-variant IPRO7AI`；應用 README 中使用舊版燒錄工具的指令已不適用。

上手時的檢查順序：

```text
lcd id          讀回面板 ID，確認 SPI 線路
lcd bars        彩條
cam probe       掃描 SCCB 找到感測器
cam start       即時預覽
spk tone 1000 2 1 kHz 正弦波，確認 DAC、擴大機與喇叭
mic rec 3       錄 3 秒
mic stats       峰值與 RMS
mic play        播放
```

## 支援的範例 { #examples }

| 範例 | EVK 設定 | 內容 |
|---|---|---|
| `apps/platform/ipro7ai_evk_launcher` | 預設 `.config` | 手勢換頁的整合展示，見上方 |
| `apps/platform/ipro7ai_evk_demo` | `.config`、`config_*` | 板級展示與 bring-up，見上方 |
| `apps/ai/ipro7ai_evk_person_detect` | 預設 `.config` | 相機預覽與 YOLOv8 人物／寵物框；`flash.sh --full` 寫入模型，主控台 115200 |
| `apps/ai/ipro7ai_evk_rps` | 預設 `.config` | 與 NPU 玩剪刀石頭布；模型連結進韌體，附訓練腳本；主控台 921600 |
| `apps/test/kw307_radar_test` | 預設 `.config` | 經 UART 連接的 24 GHz 雷達模組 |
| `apps/multimedia/ipro_pdm_mic_demo` | `make BOARD=evk`（`config_evk`） | PDM 錄音、DAC 播放、BLE 傳輸與 USB 音訊；輸出於 `build_config_evk/`，主控台 921600 |

Zephyr RTOS 支援 `ipro7ai_evk` 板型，SDK 範例 `zephyr/samples/evk_demo` 使用 LCD、麥克風、喇叭與相機預覽。

## SDK 板級支援 { #bsp }

- **板級設定**：`CONFIG_IPRO7AI_EVK=y`、`CONFIG_BOARD="IPRO7AI_EVK"`，並明確寫入 `CONFIG_USE_PSRAM=y`。設定檔 `bsp/board/ipro7/ipro7ai_evk_board_config.h`；接線、電源與下載模式說明在 `bsp/board/ipro7/IPRO7AI_EVK.md`。
- **板級函式庫** `components/board/ipro7ai_evk`：`#include "evk.h"` 後呼叫 `evk_begin()`，再使用 `evk_gfx_*`（面板）、`evk_cam_*`（相機）、`evk_mic_*`／`evk_spk_*`（音訊）、`evk_sd_*`（SD 卡）。依需要在 `.config` 加入：

    ```ini title=".config（節錄）"
    CONFIG_COMPONENTS_IPRO7AI_EVK_ENABLE=y   # 面板、繪圖與 PCM 工具，必要
    CONFIG_EVK_CAMERA=y                      # 另需 CONFIG_MM_SUPPORT、CONFIG_COMPONENTS_SENSOR_ENABLE、CONFIG_USE_PSRAM
    CONFIG_EVK_AUDIO=y                       # 另需 CONFIG_AUDIO_OUTPUT、CONFIG_DMA_CHANNEL_ALLOCATOR
    CONFIG_EVK_SDCARD=y                      # 另需 EVFS 與 FatFS 相關設定，見元件 README
    CONFIG_EVK_SHELL=y                       # 只在應用沒有自己的 lcd／cam／mic／spk／sd 指令時開啟
    ```

- **Zephyr RTOS**：板型 `ipro7ai_evk`；`west flash` 對此板預設使用 `--boot=shell`（由執行中的映像送出 `reboot_dl`）與 `partition_cfg_1M_boot2.toml`。

## 相關文件 { #documents }

- `bsp/board/ipro7/IPRO7AI_EVK.md`：J6、電源樹與下載模式。
- `components/board/ipro7ai_evk/README.md`：板級函式庫 API 與設定。
- 各範例目錄的 README：建置、燒錄與指令。
- [電源與功耗量測](../power.md#evk-power)：EVK 的電源架構。
- [IPRO7AI](../chips/ipro7ai.md)、[腳位與周邊對照](../pinmux.md)。
