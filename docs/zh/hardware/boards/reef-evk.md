---
title: IPRO7AI Reef EVK
description: IPRO7AI Reef EVK 的板上功能、跳線、上手步驟、開箱韌體、支援範例與腳位對照
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK

<span class="ipro-badge">推薦</span>

IPRO7AI Reef EVK 把 IPRO7AI（QFN56）直接焊在載板上，板上有 OmniVision FLEX-24 相機接頭（OV5640／OV2640）、DAC 喇叭與耳機輸出、三種收音、WS2812 RGB LED、按鍵與 SD 卡槽；卡槽也可插 IPRO6S FIN 卡擴充 Wi-Fi。板上沒有 LCD 與電池。本站的上手步驟與範例預設使用這塊板。

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>SoC（QFN56，焊於載板）</span></div>
<div><strong>1／2 MB</strong><span>封裝內 Flash，依料號</span></div>
<div><strong>U6</strong><span>UART 主控台，115200 baud</span></div>
<div><strong>OV5640</strong><span>相機（亦支援 OV2640），DVP</span></div>
<div><strong>USB-C</strong><span>唯一電源輸入</span></div>
</div>

## 板上功能 { #features }

| 區塊 | 內容 |
|---|---|
| 核心 | IPRO7AI（QFN56）、32 MHz 石英晶體；PCB 天線或 u.FL 天線座（以 0 Ω 電阻二擇一） |
| 記憶體 | 封裝內 8 MB PSRAM；封裝內 Flash 1 MB 或 2 MB，依料號 |
| 除錯與燒錄 | U6（SH1.0 6 pin）：UART0（GPIO20 TX／GPIO21 RX），DTR 接 BOOT、RTS 接 RESET，可使用自動下載線；SW1 為 BOOT、SW2 為 RESET |
| USB | USB-C：供電與 USB 裝置（GPIO8／9） |
| 相機 | 24 pin 0.5 mm FPC，OmniVision FLEX-24 腳序（OV5640／OV2640 模組）；DVP 8-bit，SCCB 走 I2C0 |
| 音訊輸出 | DAC A 通道（GPIO23）同時接 D 類喇叭擴大機（J_SPK）與 3.5 mm 耳機孔 J2；耳機為單聲道 |
| 音訊輸入 | PDM 麥克風（GPIO16／17）、耳機麥克風（AIN7／AIN6 差動輸入）、3.5 mm AUX-IN J1（AIN4／AIN5） |
| LED 與按鍵 | WS2812 RGB LED（GPIO24）、電源指示燈；使用者按鍵 SW3、SW4、SW5，以及開機後可讀取的 SW1（BOOT） |
| 儲存與 Wi-Fi | SD 卡槽（SDH 控制器，GPIO28–33，4-bit），卡片偵測 GPIO15、電源開關 GPIO14；同一卡槽可插 IPRO6S FIN 卡 |
| 擴充 | J_IO 2×12（2.54 mm）：電源、RESET、BOOT、UART、SDIO 訊號與 GPIO14／15／18／19／27 |

### 跳線 { #jumpers }

| 跳線 | 設定 |
|---|---|
| JP1 | VDDIO1 電源（GPIO0–9、GPIO36–41：相機、USB、BOOT）：1-2 = 3.3 V，2-3 = 2.8 V。**必須插上** |
| JP2 | 1-2：3V3 由板上降壓轉換器供應。R40（0 Ω）作用相同，兩者裝一個即可 |
| JP3 | SD_VDD：1-2 = 常開；2-3 = 由 GPIO14 控制。使用 IPRO6S FIN 卡時設為 2-3，`fin cycle` 才能重新為卡片上電 |

!!! warning "上電前"
    - 插上 JP1。沒有插時，VDDIO1 這組腳位（相機、USB、BOOT）沒有電。
    - 只從 USB-C 供電。WS2812 LED 與喇叭擴大機由 VBUS 供電，只把限流電源接到 3V3 時，LED 與喇叭不會動作。

## 上手 { #quick-start }

<div class="ipro-steps" markdown>

1. **接線**：依上表設定跳線，接上 USB-C 供電，並把 USB 轉 UART 線接到 U6。

2. **建置開箱韌體**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    產出：`apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`

3. **進入下載模式**：按住 SW1（BOOT）不放，按一下 SW2（RESET），再放開 SW1。使用接在 U6 的自動下載線時不必按鍵；板上韌體正在執行時，也可以在主控台輸入 `reboot_dl`。

4. **燒錄**：在 IntelProCube 目錄下執行命令列工具。`--chip-variant IPRO7AI` 選用 QFN56 的 Flash 腳位，`--pt` 使用 Reef 應用 README 的分割表。以 macOS 為例，Linux 與 Windows 的命令見[燒錄與序列埠](../../get-started/flash-and-monitor.md#flashing)：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    工具即使失敗也會以 0 結束，請以輸出中的 `[All Success]` 判斷結果。`build_freertos.sh` 的 `flash` 動作不帶 `--chip-variant` 與 `--pt`，不要用它燒錄 Reef。

5. **開啟主控台並自我檢查**：按 SW2 重置後，在 U6 上以 115200 baud（8N1）送出 `reef selftest`。Windows 上以任一序列埠終端程式開啟 `COM5` 後輸入。

    ```bash
    python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10
    ```

    開機時 LED 呼吸一次藍光；SW3、SW4、SW5、BOOT 分別點亮紅、綠、藍、白光。`reef selftest` 約 3 秒內依序檢查 LED、喇叭 1 kHz 測試音、SD 卡偵測與相機探測，輸出說明見[第一個 FreeRTOS 應用](../../get-started/first-app-freertos.md#verify)。

</div>

## 開箱韌體 ipro7ai_reef_demo { #reef-demo }

板上每個功能區塊各有一組 shell 指令。Reef 沒有 LCD，相機以 shell 指令檢查。

| 區塊 | Shell 指令 | 說明 |
|---|---|---|
| 狀態與自我檢查 | `reef status`、`reef selftest` | 腳位、按鍵、LED、擴大機與偵測線狀態；一次跑完自我檢查 |
| RGB LED（WS2812） | `led <r> <g> <b>`、`led rainbow`、`led off` | 設定顏色（0–255）或彩虹效果 |
| 按鍵 | `btn status`、`btn watch` | 去彈跳後的狀態與按下次數；即時列出按下／放開事件 |
| 喇叭與耳機 | `spk tone <hz> <ms>`、`hp` | DAC A 輸出正弦波；指令加上 `hp` 時擴大機靜音、只走耳機。`hp` 讀取耳機插入偵測（GPIO26） |
| 音訊輸入 | `mic rec <來源> <秒>`、`mic play`、`mic loop` | 來源為 `pdm`、`headset` 或 `aux`；以 16 kHz 錄到 PSRAM（最長 10 秒）後播放，或即時監聽 |
| SD 卡 | `sd mount`、`sd ls`、`sd test`、`sd bench`、`sd power` | FatFS 掛載於 `sd:`；寫入、讀回並驗證；JP3 為 2-3 時控制 SD_VDD |
| FIN 卡 | `fin`、`fin cycle` | 卡槽狀態；JP3 為 2-3 時重新為 FIN 卡上電 |
| 相機 | `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on` | OV5640／OV2640 以 YUV422 1280×720 經 ISP 通道 0；影格數、每秒影格與錯誤計數、ASCII 縮圖、感測器彩條 |

相機上手的順序：

```text
cam probe        經 SCCB 讀取感測器 ID
cam start        開始擷取
cam status       間隔一秒執行兩次：影格數增加、錯誤數不變
cam bar on       切到彩條
cam snap         ASCII 縮圖應為垂直色帶
cam bar off
cam snap         拍到實際畫面
```

## Wi-Fi 與 RTSP 相機串流 { #wifi-rtsp }

`defconfig_wifi_ipro6s` 建置透過插在卡槽上的 IPRO6S FIN 卡（SDIO）連網，並以 RTSP 提供相機的 MJPEG 串流（`rtsp://<ip>:8554/av0_0`）；IPRO7 端使用 SDK 隨附的 `components/network/ipronet_host` 與 `components/network/rtsp_server`。

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # 輸出於 build_wifi_ipro6s/build_out/
```

連線與串流的步驟、指令表與 `ipronet_host` API 見[網路](../../guides/networking.md#wifi-ipro6)。JP3 設為 2-3 時，可用 `fin cycle` 重新為 FIN 卡上電。

!!! info "需另行取得"
    FIN 卡上的 IPRO6S 韌體未包含於 V2.1.0，請洽 INTELPRO。

## 支援的範例 { #examples }

| 範例 | Reef 設定 | 內容 |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` | 預設 `.config`；`defconfig_wifi_ipro6s` | 開箱韌體；加上 Wi-Fi 與 RTSP 串流 |
| `apps/bluetooth/ble/ipro_ble_remote` | `defconfig_reef` | 在 Reef 硬體上的 GATT 服務（LED、按鍵、相機、麥克風、喇叭、SD 卡）與 BLE OTA。OTA 需要 boot2 與 `partition_cfg_2M_remote_ab.toml`，不要用標準的 `partition_cfg_2M.toml`，詳見該應用 README |
| `apps/bluetooth/ble/ipro_throughput_test` | `defconfig_reef` | 兩塊板之間的 BLE 吞吐量測試 |
| `apps/bluetooth/le_audio/ipro_le_audio_headset` | `defconfig_reef` | LE Audio 單播耳機，DAC 輸出版本 |
| `apps/multimedia/ipro7_uvc_cam` | `defconfig_reef_ov5640`、`defconfig_reef_rps` | USB 網路攝影機；另一個設定把 NPU 剪刀石頭布結果畫進影像 |
| `apps/test/ipro_ai_link` | `defconfig_reef` | IPRO AI Studio「Run on board」的板端韌體 |
| `apps/multimedia/ipro_agora_sentino` | 預設 `.config` | 雲端 AI 語音對話：BLE 配網、FIN 卡 Wi-Fi、Agora RTC。需另備裝置三元組、FIN 卡韌體與 AOSL 子模組，見該應用 README |

以 `DEFCONFIG=` 選擇 Reef 設定，輸出放在 `build_<名稱>/`，名稱為檔名去掉 `defconfig_` 的部分：

```bash
make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef   # 輸出於 build_reef/build_out/
```

上表所有 Reef 設定的主控台都是 115200 baud。

## 腳位對照 { #pinout }

| 區塊 | 腳位 |
|---|---|
| UART0 主控台 | TX GPIO20、RX GPIO21（U6；J_IO 13／15） |
| USB 裝置 | DP GPIO8、DM GPIO9 |
| 相機 DVP | D0–D7 = GPIO0–7、PCLK GPIO38、VSYNC GPIO39、HREF GPIO40、XCLK GPIO22、RESETB GPIO34、PWDN GPIO35 |
| 相機 SCCB | SCL GPIO36、SDA GPIO37（I2C0） |
| 喇叭 | DAC A GPIO23 → D 類擴大機；致能 GPIO25，高電位開啟 |
| 耳機 | 與喇叭共用 DAC A；插入偵測 GPIO26，低電位表示已插入 |
| PDM 麥克風 | CLK GPIO16、DATA GPIO17 |
| 耳機麥克風 | AIN7（GPIO13）正端、AIN6（GPIO12）負端 |
| AUX-IN | AIN4（GPIO10）左、AIN5（GPIO11）右 |
| RGB LED | WS2812 DI GPIO24，以 SPI0 MOSI 驅動（需 `pin_swap_enable = 0`） |
| 按鍵 | SW1 BOOT GPIO41（高電位有效）、SW3 GPIO10、SW4 GPIO27、SW5 GPIO11（低電位有效） |
| SD 卡槽 | D1 GPIO28、D0 GPIO29、CLK GPIO30、CMD GPIO31、D3 GPIO32、D2 GPIO33；偵測 GPIO15（低 = 有卡）；電源 GPIO14（低 = 開） |

GPIO10／11 同時是 AUX-IN 與 SW3／SW5，同一時間只能當類比輸入或按鍵使用。GPIO22 在晶片上也是 DAC B 通道，Reef 把它用作相機時脈。

J_IO（2×12）腳位：

| 腳 | 訊號 | 腳 | 訊號 |
|---|---|---|---|
| 1 | 3V3 | 2 | GND |
| 3 | VBUS | 4 | GND |
| 5 | VDDIO1 | 6 | SDIO_DAT1（GPIO28） |
| 7 | 1V8 | 8 | SDIO_DAT0（GPIO29） |
| 9 | SYS_RESET | 10 | SDIO_CLK（GPIO30） |
| 11 | GPIO41（BOOT） | 12 | SDIO_CMD（GPIO31） |
| 13 | GPIO20（UART TX） | 14 | SDIO_DAT3（GPIO32） |
| 15 | GPIO21（UART RX） | 16 | SDIO_DAT2（GPIO33） |
| 17 | GPIO18 | 18 | GPIO14（SD_PWR_EN） |
| 19 | GPIO19 | 20 | GPIO15（SD_DET） |
| 21 | GPIO27（SW4） | 22–24 | GND |

GPIO18／19 是 32 kHz 晶體腳位，Reef 沒有裝晶體，可作一般 GPIO。

## SDK 板級支援 { #bsp }

- **板級設定**：`.config` 寫入 `CONFIG_IPRO7AI_REEF=y` 與 `CONFIG_BOARD="IPRO7AI_REEF"`，設定檔為 `bsp/board/ipro7/ipro7ai_reef_board_config.h`。建置不套用 Kconfig 的 `select`，所以也要明確寫入 `CONFIG_USE_PSRAM=y`。
- **晶體微調**：`.config` 沒有設定 `CONFIG_IPRO7_XTAL_CAPCODE` 時，`bsp/board/ipro7/CMakeLists.txt` 會替 Reef 套用 95；在 `.config` 寫入其他值即可覆寫（0 = 保留開機時的值）。
- **Flash 版面**：`ipro7ai_reef_demo` 預設連結 1 MB 版面，兩種封裝內 Flash 都放得下。開機訊息回報 JEDEC ID `0xEF4015`（2 MB）時，可加入 `CONFIG_IPRO7_FLASH_2M=y`。`ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` 的 `defconfig_reef` 與 `ipro_agora_sentino` 已設定 2 MB。
- **Zephyr RTOS**：本版沒有 Reef 的 Zephyr 板型。SoC 的 Kconfig 說明指出 Reef 可執行 `ipro7_evb` 映像，並需設定 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`。

## 相關文件 { #documents }

- `apps/platform/ipro7ai_reef_demo/README.md`：完整指令與相機除錯說明。
- `bsp/board/ipro7/ipro7ai_reef_board_config.h`：腳位、電源樹與跳線的原始說明。
- [電源與功耗量測](../power.md#reef-power)：Reef 的電源架構。
- [腳位與周邊對照](../pinmux.md)、[IPRO7AI](../chips/ipro7ai.md)。
- IPRO7AI Reef EVK 使用手冊（腳位圖、電源樹、跳線）：見 [文件下載](../../documents/index.md)。
