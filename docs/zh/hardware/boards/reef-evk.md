---
title: IPRO7AI Reef EVK V4.0
description: IPRO7AI Reef EVK V4.0 的板上功能、開關與跳線、上手與下載模式、開箱韌體、經 IPRO6S FIN 卡的 Wi-Fi、可執行的範例、USB 識別碼與腳位對照
migrate_from:
  - "hardware.html — IPRO7AI Reef EVK"
  - "audio-multimedia.html#reef-demo"
  - "applications.html#ipro7ai-reef-demo"
  - "getting-started.html#flashing — Reef"
---

# IPRO7AI Reef EVK V4.0

<span class="ipro-badge">V4.0</span>

IPRO7AI Reef EVK 以 IPRO7AI（QFN56）為核心，Flash 與 PSRAM 都在晶片封裝內。板上有 OV5640 相機排線座、PDM 數位麥克風、耳麥孔與喇叭放大器、microSD 卡座、RGB LED、按鍵，以及位置與腳序同樹莓派的 40-pin 擴充排針；只由 USB-C 供電，沒有 LCD 與電池。本頁對應 V4.0 開發板（絲印「IPRO7AI REEF EVK V4.0」）；本站所有步驟都以這塊板為準。

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

完成後，板子執行開箱韌體 `ipro7ai_reef_demo`，並在主控台回應 `reef selftest`。主機需要 RISC-V 工具鏈（向 INTELPRO 取得）、IntelProCube 0.7.0.1（從 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) 下載）、CMake 3.15 以上、GNU make 與 Python 3.8 以上，見[開始使用](../../get-started/index.md)。

<div class="ipro-steps" markdown>

1. **設定開關並接線**：SW7 撥到 CAM、SW8 撥到 PWR。把主控台線接到 U6：3.3 V 的 USB 轉 UART 線（腳位見[除錯排座 U6](#debug-connector)），或以兩端腳序對調的排線接 IPRO Debug Probe。最後接上 USB-C。

    綠色電源燈 LED2 亮起。U6 不供電，板子只由 USB-C 供電。

2. **找出序列埠**：在主機上列出序列埠。

    ```bash
    ls /dev/cu.usb*        # macOS
    ls /dev/ttyUSB* /dev/ttyACM*   # Linux
    ```

    USB 轉 UART 線出現一個序列埠，例如 `/dev/cu.usbserial-XXXX`。IPRO Debug Probe 出現兩個（裝置名稱 `IPRO7 CMSIS_DAP`）：名稱結尾為 `02` 的是 Reef 主控台，`04` 是 CCI 橋接。Windows 在裝置管理員中查看 `COM` 編號。

3. **建置開箱韌體**：在 SDK 根目錄執行

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    建置結尾印出 Flash 與 RAM 用量，映像在 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

4. **進入下載模式**：按住 SW1（BOOT），按一下 SW2（RESET），再放開 SW1。

    主控台不再有任何輸出。其他方式見[下載模式](#download-mode)。以 IPRO Debug Probe 連接時可以略過這一步：IntelProCube 0.7.0.1 會經探針讓晶片進入下載模式，燒錄後自動重置。

5. **燒錄**：在 IntelProCube 目錄執行（Linux 為 `./ipro_iot_tool_linux`，Windows 為 `ipro_iot_tool.exe`）

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    輸出最後出現 `[All Success]` 才算成功；工具即使失敗也以 0 結束。`--chip-variant IPRO7AI` 選用 QFN56 的 Flash 腳位。

6. **啟動並自我檢查**：按一下 SW2，以 115200 baud（8N1、無流量控制）開啟主控台，輸入 `reef selftest`。

    ```bash
    screen /dev/cu.usbserial-XXXX 115200
    ```

    開機訊息有 `IPRO7AI Reef carrier demo` 與 `shell ready - ...`，RGB LED 呼吸一次藍光。`reef selftest` 約 3 秒內依序印出：

    ```text
    [1/4] RGB LED: red, green, blue
    [2/4] speaker: 1 kHz, 300 ms, 20%
    [3/4] SD slot: empty, supply on
    [4/4] camera bus: OV5640 at 0x3C
    done - keys: press any and run `btn status`
    ```

    第 3 行依是否插卡而不同；沒接相機時第 4 行為 `no sensor`。按 SW3、SW4、SW5、SW1 分別亮紅、綠、藍、白光。

</div>

熟悉流程後，`build_freertos.sh` 可以一次完成建置、燒錄與主控台。它依應用的設定自動選用 `--chip-variant IPRO7AI`，以應用自己的鮑率開啟主控台；板上已有 SDK 韌體時會先送出 `reboot_dl`，第一次燒錄則先以按鍵進入下載模式：

```bash
export IPRO_FLASH_TOOL=<ICUBE>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <ICUBE>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

這個腳本無法寫入 boot2 與 mfg 資料，`ipro_ble_remote` 的第一次燒錄與 `ipro_reef_teach` 請直接使用 IntelProCube。選項見[工具命令列](../../reference/tools.md)。

## 下載模式 { #download-mode }

燒錄前，IPRO7AI 必須在重置時看到 BOOT（GPIO41）為高準位，進入 ROM 的下載模式。進入後主控台沒有任何輸出；燒錄完成後按一下 SW2 回到正常開機。

| 方式 | 操作 | 適用時機 |
|---|---|---|
| 按鍵 | 按住 SW1（BOOT），按一下 SW2（RESET），放開 SW1 | 任何時候，包括板上韌體無回應時 |
| 主控台指令 | 在主控台輸入 `reboot_dl` | 板上執行 SDK 韌體時；`build_freertos.sh flash` 會自動送出 |
| 自動下載線 | U6 第 5 腳 BOOT 與第 6 腳 RESET 各經 1 kΩ 接到 IPRO7AI，接上 USB 轉 UART 線的 DTR 與 RTS 即可由主機控制 | 使用帶 DTR、RTS 的轉接線時 |
| IPRO Debug Probe | 對探針結尾為 `02` 的序列埠寫入 `IPRODL_1` 再寫入 `IPRORST_RESET`；燒錄完成後寫入 `IPRODL_0` 再寫入 `IPRORST_RESET` | 使用 IPRO Debug Probe 時 |

以 Debug Probe 進入下載模式（每行送出一個關鍵字）：

```bash
python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRODL_1 --timeout 1
python3 tools/serial_monitor.py /dev/cu.usbmodemXXXX02 --send IPRORST_RESET --timeout 1
```

燒錄完成後以同樣方式送出 `IPRODL_0` 與 `IPRORST_RESET`，板子正常開機。

使用 boot2 的映像（例如 `ipro_ble_remote` 的 Reef 版）另有 `reboot_usb [code]`：重新開機進入 boot2 的 USB 下載模式（預設一直等待）。OTA 套件驗證失敗時，boot2 也會停在這個 USB 救援模式。

## 開箱韌體 ipro7ai_reef_demo { #reef-demo }

板上每個功能區塊各有一組 shell 指令，`help` 列出全部指令。Reef 沒有 LCD，相機以 shell 指令檢查。

| 區塊 | Shell 指令 | 說明 |
|---|---|---|
| 狀態與自我檢查 | `reef status`、`reef selftest` | 腳位、按鍵、LED、擴大機與偵測線狀態；一次跑完自我檢查 |
| RGB LED | `led <r> <g> <b>`、`led rainbow`、`led off` | 設定顏色（0–255）或彩虹效果 |
| 按鍵 | `btn status`、`btn watch` | 去彈跳後的狀態與按下次數；即時列出按下／放開事件 |
| 喇叭與耳機 | `spk tone <hz> <ms>`、`hp` | GPDAC 輸出正弦波；指令加上 `hp` 時擴大機靜音、只走耳機。單獨的 `hp` 讀取耳麥插入偵測（GPIO26） |
| 音訊輸入 | `mic rec <來源> <秒>`、`mic play`、`mic loop` | 來源為 `pdm`（板上麥克風）或 `headset`（耳麥）；以 16 kHz 錄到 PSRAM（最長 10 秒）後播放，或即時監聽 |
| 錄音到 SD 卡 | `mic sdrec <來源> <名稱> <秒>` | 錄成 `sd:/rec/<名稱>.wav` |
| USB 麥克風 | `mic usb <來源>` | 板子經 USB-C 成為 16 kHz 的 USB 麥克風 |
| SD 卡 | `sd mount`、`sd ls`、`sd test`、`sd bench`、`sd power` | FatFS 掛載於 `sd:`；寫入、讀回並驗證；JP3 在 GPIO 時，`sd power` 以 GPIO14 開關卡座電源 |
| FIN 卡 | `fin`、`fin cycle` | 卡座上 IPRO6S FIN 卡的狀態；JP3 在 GPIO 時重新為卡片上電 |
| 相機 | `cam probe`、`cam start`、`cam status`、`cam snap`、`cam bar on` | OV5640 以 YUV422 1280×720 經 ISP 通道 0；影格數、每秒影格與錯誤計數、ASCII 縮圖、感測器彩條 |

應用 README 中的 AUX-IN 輸入（`mic rec aux`）是前一版載板的功能，V4.0 沒有 AUX-IN 插座。

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

把 IPRO6S FIN 卡插進 microSD 卡座，Reef 經 SDIO 連上 Wi-Fi，並以 RTSP 提供相機的 MJPEG 串流（`rtsp://<ip>:8554/av0_0`）。

- **FIN 卡韌體**：IPRO6S 的 `ipro6_if_wifi`，以 `defconfig_ipro6_sdio` 建置：

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio   # build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin
    ```

    更新方式見 [IPRO6S](../chips/ipro6s.md)；卡片已連上 Wi-Fi 時，可在 Reef 主控台以 `ipro6s_ota <http url>` 更新。

- **Reef 韌體**：`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s`：

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # build_wifi_ipro6s/build_out/
    ```

- **開關**：JP3 放在 GPIO，`fin cycle` 才能重新為卡片上電。

連線後在主控台輸入 `ipronet_up <ssid> <psk>`，再輸入 `rtsp_cam on`，以 RTSP 播放程式開啟 `rtsp://<ip>:8554/av0_0`。完整步驟見 [Wi-Fi 與 RTSP 相機串流](../../tutorials/wifi-rtsp.md)。

## 支援的範例 { #examples }

下列 9 個應用（11 個設定）可在 Reef 上建置與執行，每個都有[範例頁](../../examples/index.md#reef)寫出燒錄與執行步驟。除 `ipro7ai_reef_demo`、`ipro_reef_teach` 與 `ipro_agora_sentino` 外，其他應用直接執行 `make` 會建置成別的板卡，Reef 要加上 `DEFCONFIG=`。

| 應用 | 建置命令（在 SDK 根目錄） | 主控台 | 燒錄注意事項 |
|---|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `make -C apps/platform/ipro7ai_reef_demo` | 115200 | `--pt chips/ipro7/partition/partition_cfg_2M.toml` |
| `ipro7ai_reef_demo`（Wi-Fi） | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | 115200 | 需要執行 `ipro6_if_wifi` 的 FIN 卡，JP3 在 GPIO |
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `make -C apps/ai/ipro_reef_teach` | 115200 | 自有分割表 `partition_reef_teach.toml`、`--skip-ota` 與 `--mfg`，見 [燒錄 Edge AI 韌體](../../teach/firmware.md) |
| [`ipro_ble_remote`](../../examples/ipro_ble_remote.md) | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | 115200 | 第一次燒錄需要 `--boot2` 與 `partition_cfg_2M_remote_ab.toml`；OTA 只能用這個 A/B 分割表 |
| [`ipro_throughput_test`](../../examples/ipro_throughput_test.md) | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | 115200 | 需要兩塊板 |
| [`ipro_le_audio_headset`](../../examples/ipro_le_audio_headset.md) | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | 115200 | — |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | 115200 | `--pt chips/ipro7/partition/partition_cfg_2M.toml` |
| `ipro7_uvc_cam`（剪刀石頭布） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | 115200 | 同上；模型已連結進韌體 |
| [`ipro7_jpeg_decode`](../../examples/ipro7_jpeg_decode.md) | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | **921600** | — |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | 115200 | 需要 microSD 卡 |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `make -C apps/multimedia/ipro_agora_sentino` | 115200 | 先取得 AOSL 核心；需要 FIN 卡與 Sentino 裝置三元組 |

以 `DEFCONFIG=` 建置的輸出放在 `build_<名稱>/build_out/`，名稱為檔名去掉 `defconfig_` 的部分，例如 `defconfig_reef` → `build_reef/`。

## USB 識別碼 { #usb-ids }

Reef 的 USB-C 由 IPRO7AI 的 USB 2.0 Full-Speed 裝置提供，識別碼依執行的韌體而定。所有應用的 VID 都是 `0x3896`（INTELPRO INC.）。

| PID | 應用與模式 | 主機看到的裝置 |
|---|---|---|
| `0x0705` | `ipro_reef_teach` 的 `image` 模式 | UVC 相機＋CDC 序列埠 |
| `0x0720` | `ipro_reef_teach` 的 `voice` 模式 | CDC 序列埠 |
| `0x0721` | `ipro_reef_teach` 的 `sensor` 模式 | CDC 序列埠 |
| `0x0701` | `ipro7_uvc_cam` | UVC 相機「IPRO7 UVC Cam」 |
| `0x0704` | `ipro_ai_link` | 兩個 CDC 序列埠（資料、主控台） |
| `0x0003` | `ipro7ai_reef_demo` 的 `mic usb` | USB 音訊裝置（麥克風） |

`ipro_ble_remote`、`ipro_throughput_test`、`ipro_le_audio_headset`、`ipro7_jpeg_decode`、`ipro_agora_sentino` 與 `ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 不使用 USB 裝置，USB-C 只供電。

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

- **板級設定**：`.config` 寫入 `CONFIG_IPRO7AI_REEF=y` 與 `CONFIG_BOARD="IPRO7AI_REEF"`，腳位定義在 `bsp/board/ipro7/ipro7ai_reef_board_config.h`。同一個設定不要再寫入 `CONFIG_EVB=y`：兩者都有時會以 IPRO7 EVB 建置。
- **PSRAM**：建置不套用 Kconfig 的 `select`，Reef 設定都明確寫入 `CONFIG_USE_PSRAM=y`（`ipro_throughput_test` 的 `defconfig_reef` 例外，它沒有開啟 PSRAM）。從零開始的新應用請複製 `apps/platform/ipro7ai_reef_demo/.config`。
- **腳位定義**：設定檔中主控台、USB、相機、喇叭、麥克風、LED、按鍵與 SD 卡的 `BOARD_*` 腳位與本頁相同。檔內註解描述的擴充排針與跳線屬於前一版（V3.0）載板，V4.0 以本頁為準。
- **晶體微調**：`.config` 沒有設定 `CONFIG_IPRO7_XTAL_CAPCODE` 時，建置會替 Reef 套用 95；在 `.config` 寫入其他值即可覆寫（0 = 保留開機時的值）。開機訊息的 `[XTAL] capcode` 一行顯示實際的值。
- **Flash 版面**：`ipro7ai_reef_demo`、`ipro7_uvc_cam`、`ipro7_jpeg_decode` 與 `ipro_throughput_test` 的 Reef 設定使用 1 MB 版面，兩種封裝內 Flash 都放得下；`ipro_reef_teach`、`ipro_agora_sentino` 的 `.config` 與 `ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` 的 `defconfig_reef` 設定 `CONFIG_IPRO7_FLASH_2M=y`。要讓 1 MB 版面的應用使用整顆 2 MB Flash，在其設定加入 `CONFIG_IPRO7_FLASH_2M=y`。
- **Zephyr RTOS**：本版沒有 Reef 的 Zephyr 板型。SoC 的 Kconfig 說明 Reef 可執行 `ipro7_evb` 映像並需設定 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`，這個用法未經驗證。

## 相關文件 { #documents }

- [IPRO AI Teach](../../teach/index.md)：在這塊板上以 IPRO AI Studio 教會板子辨識影像、聲紋與感測訊號。
- [範例](../../examples/index.md#reef)：可在 Reef 上執行的應用，各有建置、燒錄與執行步驟。
- [腳位與周邊對照](../pinmux.md)、[電源與功耗量測](../power.md)、[IPRO7AI](../chips/ipro7ai.md)、[IPRO6S](../chips/ipro6s.md)。
- `apps/platform/ipro7ai_reef_demo/README.md`：開箱韌體的完整指令與相機除錯說明。
- IPRO7AI Reef 開發套件使用手冊（V4.0 開發板硬體、介面與供電）與 IPRO Debug Probe 使用手冊：向 INTELPRO 索取，見[文件下載](../../documents/index.md)。
