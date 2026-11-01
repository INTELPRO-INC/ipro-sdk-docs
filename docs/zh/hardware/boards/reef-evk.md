---
title: IPRO7AI Reef EVK
description: IPRO7AI Reef EVK（V4.0 開發板）的板上功能、開關與跳線、上手步驟、開箱韌體、支援範例與腳位對照
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK

<span class="ipro-badge">推薦</span>

IPRO7AI Reef EVK 以 IPRO7AI（QFN56）為核心，Flash 與 PSRAM 都在晶片封裝內。板上有 OV5640 相機排線座、PDM 數位麥克風、耳麥孔與喇叭放大器、microSD 卡座、RGB LED、按鍵，以及位置與腳序同樹莓派的 40-pin 擴充排針；只由 USB-C 供電，沒有 LCD 與電池。本頁對應 V4.0 開發板（絲印「IPRO7AI REEF EVK V4.0」），本站的上手步驟與範例預設使用這塊板。

<figure>
  <img src="/ipro-sdk-docs/assets/images/reef-v4-top.jpg" alt="IPRO7AI Reef EVK V4.0 正面：上緣為 40-pin 排針 J_IO，右上為 SW1、SW2 與 PCB 天線，左緣為 SW7、U6 與 microSD 卡座，下緣為 JP3、喇叭座、耳麥孔、SW8、JP2 與 USB-C" width="1500" height="1011" loading="lazy">
  <figcaption>IPRO7AI Reef EVK V4.0 正面</figcaption>
</figure>

<div class="ipro-facts" markdown>
<div><strong>IPRO7AI</strong><span>SoC（QFN56），NPU、ISP、BLE、IEEE 802.15.4</span></div>
<div><strong>2 MB＋8 MB</strong><span>封裝內 Flash 與 PSRAM</span></div>
<div><strong>40-pin</strong><span>J_IO，樹莓派位置與腳序，3.3 V</span></div>
<div><strong>U6</strong><span>主控台 UART，115200 baud</span></div>
<div><strong>USB-C</strong><span>唯一電源輸入</span></div>
</div>

## 板上功能 { #features }

| 區塊 | 內容 |
|---|---|
| 核心 | IPRO7AI（U1，QFN56）：RISC-V RV32IMAFC、NPU、ISP、2.4 GHz 射頻（BLE、IEEE 802.15.4）；32 MHz 晶體（X1） |
| 記憶體 | 封裝內 2 MB Flash 與 8 MB PSRAM；晶片內 256 KB OCRAM |
| 天線 | PCB 天線 E1（預設）；把 R2 的 0 Ω 電阻移到 R1，改接 u.FL 天線座 RF1 |
| 相機 | FPC1：0.5 mm 間距 24 pin 直立式排線座，OV5640 FLEX-24 腳位，8 位元 DVP；相機的 2.8 V 與 1.5 V 由板上穩壓器供應 |
| 相機／GPIO 切換 | SW7 經 4 顆 SN74CB3Q3257 把 16 支相機腳位切到 J_IO；切到 GPIO 時相機電源關閉 |
| 音訊輸入 | PDM 數位麥克風 MK1；耳麥麥克風經耳麥孔 J2 接到類比輸入 AIN6、AIN7 |
| 音訊輸出 | IPRO7AI 的 GPDAC 經耳機放大級（TLV9061）到耳麥孔 J2（3.5 mm，CTIA 接法）；並經 D 類放大器 PAM8302A 到喇叭座 J_SPK（1.25 mm 2 pin，接 8 Ω 喇叭） |
| 儲存 | microSD 卡座 CARD1（推入推出式），4 位元 SD 介面；卡片偵測與卡座電源各接一支 GPIO |
| USB | USB-C（USB1）：5 V 供電與 USB 2.0 Full-Speed 裝置 |
| 除錯 | U6：1.0 mm 間距 6 pin（SH1.0），主控台 UART、BOOT、RESET；接 IPRO Debug Probe |
| 按鍵與指示燈 | SW1 BOOT、SW2 RESET、SW3／SW4／SW5 使用者按鍵（側按式）；LED1 RGB LED（WS2812B-2020）、LED2 電源指示燈（綠） |
| 擴充 | J_IO：2 × 20、2.54 mm 間距排針，位置與腳序同樹莓派 40-pin；訊號均為 3.3 V |
| 電流量測 | SW8（PWR／MEAS）與 JP2，量測 IPRO7AI 的 3.3 V 電流 |
| 外形 | 85 × 56 mm，板厚 1.6 mm，六層板；四個 Ø2.75 mm 固定孔，孔距 58 × 49 mm，與 40-pin 排針的相對位置同樹莓派，可用 M2.5 支柱固定 |

規格依 V4.0 設計檔（原理圖與物料表）。

### 開關與跳線 { #jumpers }

| 位號 | 位置 | 作用 |
|---|---|---|
| SW7 | CAM（預設） | 相機腳位接到 IPRO7AI，相機電源開啟。使用相機時必須在 CAM |
| | GPIO | 16 支相機腳位改接到 J_IO（[腳位表](#j-io)標 * 的腳），兩顆相機穩壓器關閉 |
| SW8 | PWR | 一般使用：IPRO7AI 的 3.3 V 直接由板上電源供應 |
| | MEAS | 量測：IPRO7AI 的 3.3 V 改經 JP2 供應；JP2 必須接電流表或外部 3.3 V 電源 |
| JP3 | ON | microSD 卡座一直有電 |
| | GPIO | 卡座電源由 GPIO14 控制：低準位或未驅動時有電，高準位時斷電 |
| JP2 | — | 3 pin：1＝3V3（板上 3.3 V）、2＝SOC（IPRO7AI 的 3.3 V）、3＝GND；只在 SW8＝MEAS 時使用 |

量測 IPRO7AI 的電流：拔掉 USB-C，把電流表接在 JP2 的 1、2 腳之間（或把外部 3.3 V 電源接在 2、3 腳），SW8 撥到 MEAS，再接上 USB-C。量完先拔掉 USB-C，把 SW8 撥回 PWR，再拆電流表。量到的是 IPRO7AI 的 3.3 V 腳及其去耦電容、開機腳上拉電阻的電流，不含周邊。

!!! warning "上電前"
    - 只從 USB-C 供電。J_IO 的 5 V 腳（2、4 腳）是輸出，不能由此對板子供電。
    - 所有 IO 都是 3.3 V 準位，不可接 5 V 訊號。
    - 插拔相機排線前先拔掉 USB-C。
    - SW8 平常放在 PWR。放在 MEAS 時，JP2 沒有接電流表或外部 3.3 V 電源就不要接 USB-C：IPRO7AI 沒有電，周邊的 3.3 V 卻會經 IO 腳倒灌。

## 上手 { #quick-start }

<div class="ipro-steps" markdown>

1. **接線**：確認 SW7 在 CAM、SW8 在 PWR。把 IPRO Debug Probe 接到 U6（也可以用 3.3 V 的 USB 轉 UART 線，腳位見[除錯排座 U6](#debug-connector)），再接上 USB-C 供電。U6 不供電，板子由自己的 USB-C 供電。

2. **建置開箱韌體**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    產出：`apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`

3. **進入下載模式**：按住 SW1（BOOT）不放，按一下 SW2（RESET），再放開 SW1。接 IPRO Debug Probe 時，探針經 U6 的 BOOT 與 RESET 線控制下載模式；板上韌體正在執行時，也可以在主控台輸入 `reboot_dl`。

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
| RGB LED | `led <r> <g> <b>`、`led rainbow`、`led off` | 設定顏色（0–255）或彩虹效果 |
| 按鍵 | `btn status`、`btn watch` | 去彈跳後的狀態與按下次數；即時列出按下／放開事件 |
| 喇叭與耳機 | `spk tone <hz> <ms>`、`hp` | GPDAC 輸出正弦波；指令加上 `hp` 時擴大機靜音、只走耳機。單獨的 `hp` 指令讀取 GPIO26（耳麥插入偵測）的準位 |
| 音訊輸入 | `mic rec <來源> <秒>`、`mic play`、`mic loop` | 來源為 `pdm`（板上麥克風）或 `headset`（耳麥）；以 16 kHz 錄到 PSRAM（最長 10 秒）後播放，或即時監聽 |
| SD 卡 | `sd mount`、`sd ls`、`sd test`、`sd bench`、`sd power` | FatFS 掛載於 `sd:`；寫入、讀回並驗證；JP3 在 GPIO 時，`sd power` 以 GPIO14 開關卡座電源 |
| FIN 卡 | `fin`、`fin cycle` | 卡座上 IPRO6S Wi-Fi 卡的狀態；JP3 在 GPIO 時重新為卡片上電 |
| 相機 | `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on` | OV5640 以 YUV422 1280×720 經 ISP 通道 0；影格數、每秒影格與錯誤計數、ASCII 縮圖、感測器彩條 |

相機上手的順序（SW7 在 CAM）：

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

`defconfig_wifi_ipro6s` 建置透過 microSD 卡座的 SDIO 介面連接 IPRO6S Wi-Fi 卡（FIN 卡）連網，並以 RTSP 提供相機的 MJPEG 串流（`rtsp://<ip>:8554/av0_0`）；IPRO7 端使用 SDK 隨附的 `components/network/ipronet_host` 與 `components/network/rtsp_server`。

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # 輸出於 build_wifi_ipro6s/build_out/
```

連線與串流的步驟、指令表與 `ipronet_host` API 見[網路](../../guides/networking.md#wifi-ipro6)。JP3 在 GPIO 時，可用 `fin cycle` 重新為卡片上電。

!!! info "需另行取得"
    IPRO6S Wi-Fi 卡（FIN 卡）與卡上韌體未包含於 V2.1.0，請洽 INTELPRO。

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
| UART0 主控台 | TX GPIO20、RX GPIO21（U6 第 3／4 腳；J_IO 第 8／10 腳） |
| USB 裝置 | D+ GPIO8、D− GPIO9 |
| 相機 DVP | 資料 GPIO0–7、PCLK GPIO38、VSYNC GPIO39、HREF GPIO40、XCLK GPIO22（由 IPRO7AI 輸出）、RESETB GPIO34、PWDN GPIO35 |
| 相機 SCCB | SIOC GPIO36、SIOD GPIO37（I2C0；上拉電阻在相機側） |
| 喇叭 | GPDAC GPIO23 → PAM8302A；致能 GPIO25，高準位開啟，開機時預設關閉 |
| 耳麥孔 J2 | 耳機與喇叭共用 GPDAC GPIO23；麥克風 AIN6（GPIO12）、AIN7（GPIO13）；插入偵測 GPIO26（GPADC） |
| PDM 麥克風 | CLK GPIO16、DATA GPIO17 |
| RGB LED | WS2812B DI GPIO24，以 SPI0 MOSI 驅動（需 `pin_swap_enable = 0`） |
| 按鍵 | SW1 BOOT GPIO41（下拉，按下為高準位）；SW3 GPIO10、SW4 GPIO27、SW5 GPIO11（按下為低準位） |
| microSD | CLK GPIO30、CMD GPIO31、DAT0 GPIO29、DAT1 GPIO28、DAT2 GPIO33、DAT3 GPIO32；卡片偵測 GPIO15；卡座電源 GPIO14（JP3 在 GPIO 時，低準位＝有電） |
| J_IO 的 I2C | SDA GPIO19、SCL GPIO18（板上 4.7 kΩ 上拉） |

microSD 的 CMD 與 DAT 線沒有外部上拉電阻，要開啟 IPRO7AI 的內部上拉（SDK 的板級設定已開啟）。以 GPIO14 關閉卡座電源前，先把 GPIO28–33 設為低準位或輸入。microSD 這組腳只接卡座，沒有引到 J_IO。

### 40-pin 擴充排針 J_IO { #j-io }

J_IO 是 2 × 20、2.54 mm 間距的直立排針，位置與腳序同樹莓派的 40-pin 排針：電源、接地、I2C 與 UART 都在相同位置。奇數腳在靠板內的一排，偶數腳在板邊的一排。所有訊號都是 3.3 V，每支訊號腳都有 ESD 保護。

- 標 * 的腳經相機切換晶片：只有 SW7＝GPIO 時才接到 IPRO7AI，SW7＝CAM 時沒有連接任何訊號。
- 2、4 腳的 5 V 由 USB 5 V 經二極體輸出，只在接著 USB-C 時有電，不能由此對板子供電。
- 16、18 腳（BOOT、RESET）預設未連接；需要時在 R92、R93 焊上 0 Ω 電阻。
- 27、28 腳是第二組 I2C，SW7＝GPIO 時可讀取擴充板上的 ID EEPROM。

| 腳 | 訊號 | 說明 | 腳 | 訊號 | 說明 |
|---|---|---|---|---|---|
| 1 | 3.3 V | 電源輸出 | 2 | 5 V | 輸出（USB 5 V 經二極體） |
| 3 | GPIO19 | I2C SDA（4.7 kΩ 上拉） | 4 | 5 V | 輸出（同 2 腳） |
| 5 | GPIO18 | I2C SCL（4.7 kΩ 上拉） | 6 | GND | |
| 7 | GPIO27 | SW4 按鍵 | 8 | GPIO20 | UART0 TX（主控台） |
| 9 | GND | | 10 | GPIO21 | UART0 RX（主控台） |
| 11 | GPIO10 | SW3 按鍵 | 12 | GPIO0 * | |
| 13 | GPIO14 | microSD 電源控制 | 14 | GND | |
| 15 | GPIO15 | microSD 卡片偵測 | 16 | BOOT | 預設未連接 |
| 17 | 3.3 V | 電源輸出 | 18 | RESET | 預設未連接 |
| 19 | GPIO4 * | | 20 | GND | |
| 21 | GPIO5 * | | 22 | GPIO35 * | |
| 23 | GPIO7 * | | 24 | GPIO6 * | |
| 25 | GND | | 26 | GPIO34 * | |
| 27 | GPIO37 * | 第二組 I2C SDA | 28 | GPIO36 * | 第二組 I2C SCL |
| 29 | GPIO22 * | | 30 | GND | |
| 31 | GPIO39 * | | 32 | GPIO40 * | |
| 33 | GPIO38 * | | 34 | GND | |
| 35 | GPIO1 * | | 36 | GPIO11 | SW5 按鍵 |
| 37 | NC | 未連接 | 38 | GPIO3 * | |
| 39 | GND | | 40 | GPIO2 * | |

### 除錯排座 U6 { #debug-connector }

U6 是 1.0 mm 間距、6 pin 的臥式排座（SH1.0），提供主控台 UART 與 BOOT、RESET 控制線，用來燒錄韌體與看開機訊息。主控台是 UART0，也是燒錄用的 UART：115200 baud、8N1、無流量控制（燒錄時 921600 baud）。

| 腳 | 訊號 | 說明 |
|---|---|---|
| 1 | NC | 未連接 |
| 2 | GND | 接地 |
| 3 | TX（GPIO20） | Reef 送出（主控台輸出） |
| 4 | RX（GPIO21） | Reef 接收（主控台輸入） |
| 5 | BOOT | 經 1 kΩ 接 GPIO41；重置放開時為高準位即進入下載模式 |
| 6 | RESET | 經 1 kΩ 接 IPRO7AI 的重置腳；低準位重置 |

IPRO Debug Probe 的 CN_UART 以兩端腳序對調的排線接到 U6：探針第 n 腳接 U6 第 7 − n 腳（探針 RST→RESET、DL→BOOT、TXD→RX、RXD→TX、GND→GND，探針的 3V3 落在 U6 的空腳）。

!!! warning "排線方向"
    不要使用兩端腳序相同（第 1 腳接第 1 腳）的排線：UART 與控制線會接錯，探針第 6 腳的 3.3 V 也會接到 U6 的 RESET。

## SDK 板級支援 { #bsp }

- **板級設定**：`.config` 寫入 `CONFIG_IPRO7AI_REEF=y` 與 `CONFIG_BOARD="IPRO7AI_REEF"`，設定檔為 `bsp/board/ipro7/ipro7ai_reef_board_config.h`。建置不套用 Kconfig 的 `select`，所以也要明確寫入 `CONFIG_USE_PSRAM=y`。
- **腳位定義**：設定檔中主控台、USB、相機、喇叭、麥克風、LED、按鍵與 SD 卡的 `BOARD_*` 腳位與本頁相同。檔內註解與 `ipro7ai_reef_demo` README 中的跳線、擴充排針與音訊輸入說明寫的是前一版載板，V4.0 以本頁為準。
- **晶體微調**：`.config` 沒有設定 `CONFIG_IPRO7_XTAL_CAPCODE` 時，`bsp/board/ipro7/CMakeLists.txt` 會替 Reef 套用 95；在 `.config` 寫入其他值即可覆寫（0 = 保留開機時的值）。
- **Flash 版面**：`ipro7ai_reef_demo` 預設連結 1 MB 版面。V4.0 的封裝內 Flash 為 2 MB，加入 `CONFIG_IPRO7_FLASH_2M=y` 可讓連結器使用整顆 Flash。`ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` 的 `defconfig_reef` 與 `ipro_agora_sentino` 已設定 2 MB。
- **Zephyr RTOS**：本版沒有 Reef 的 Zephyr 板型。SoC 的 Kconfig 說明指出 Reef 可執行 `ipro7_evb` 映像，並需設定 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`。

## 相關文件 { #documents }

- `apps/platform/ipro7ai_reef_demo/README.md`：完整指令與相機除錯說明。
- `bsp/board/ipro7/ipro7ai_reef_board_config.h`：SDK 使用的腳位定義。
- [IPRO AI Teach 2.0](../../guides/edge-ai-teach.md)：在這塊板上以 IPRO AI Studio 教會板子辨識影像、聲紋與感測訊號。
- [腳位與周邊對照](../pinmux.md)、[IPRO7AI](../chips/ipro7ai.md)。
- IPRO7AI Reef 開發套件使用手冊（V4.0 開發板硬體、介面與供電）與 IPRO Debug Probe 使用手冊：向 INTELPRO 索取，見[文件下載](../../documents/index.md)。
