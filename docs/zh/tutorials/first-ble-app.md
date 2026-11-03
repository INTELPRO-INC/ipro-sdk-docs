---
title: "第一個 BLE 應用"
description: 在 IPRO7AI Reef EVK 上執行 ipro_ble_remote：第一次以 boot2 與 A/B 分割表燒錄、用手機操作 GATT 服務、修改裝置名稱並在連線時發出提示音，最後以 BLE OTA 更新韌體。
migrate_from:
  - "tutorials.html — 教學 1"
---

# 第一個 BLE 應用

完成本教學後，IPRO7AI Reef EVK 會執行 SDK 的 GATT 參考應用 `ipro_ble_remote`：手機可以點亮板上的 RGB LED、收到按鍵通知，並與板子互傳文字。接著您會修改程式，把廣播名稱改成 `IPRO-Hello`、讓板子在手機連上時發出短嗶聲，最後不接線，經 BLE OTA 把新韌體送進板子。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK：SW7 在 CAM、SW8 在 PWR，以 USB-C 供電；U6 接 IPRO Debug Probe 或 3.3 V USB 轉 UART 線（115200 8N1，接法見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。可另接 OV5640 FLEX-24 相機模組與 microSD 卡，用來試拍照功能。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)：工具鏈位於 `/opt/toolchain/riscv_ipro7/`，`make` 能建置 SDK 應用。
- IntelProCube v0.6.3（需另行取得）：命令列燒錄工具 `ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`，以及它附帶的 boot2 映像檔 `chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin`。
- 一支手機，擇一：
    - Android：應用目錄隨附的示範 App `apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk`。
    - Android 或 iOS：可讀寫 GATT 特徵值的 BLE 工具 App，例如 nRF Connect 或 LightBlue。以下步驟以這類工具說明。
- BLE OTA（步驟 10–12）：一台有 Bluetooth LE 的 macOS 或 Linux 電腦，Python 3 與 `bleak` 套件。

!!! note "Reef 設定使用 2 MB Flash、boot2 與 A/B 分割表"
    `ipro_ble_remote` 的 Reef 設定 `defconfig_reef` 以 2 MB Flash 連結（`CONFIG_IPRO7_FLASH_2M=y`）並啟用 BLE OTA（`CONFIG_IPRO_BLE_REMOTE_OTA=y`）。燒錄時要一併寫入 boot2 與應用隨附的 A/B 分割表 `partition_cfg_2M_remote_ab.toml`：FW A（0x12000，824 KB）是執行區，FW B（0xE0000，512 KB）暫存 OTA 套件。`build_freertos.sh` 無法帶 `--boot2`，所以本教學直接使用燒錄工具。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **建置 Reef 設定**：在 SDK 根目錄執行：

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    `DEFCONFIG=` 不會動到 `.config`，建置目錄是 `build_reef/`。成功時連結器最後印出記憶體用量表（Flash 一列顯示 `2 MB`），產出檔為 `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`。不加 `DEFCONFIG=` 的 `make` 建置的是 IPRO7 EVB 版本，不能用在 Reef。

2. **讓 Reef 進入下載模式**：按住 SW1（BOOT），按一下 SW2（RESET），再放開 SW1。板上韌體已有 shell 時，也可以在主控台輸入 `reboot_dl`。進入下載模式後主控台沒有任何輸出。

3. **燒錄 boot2、A/B 分割表與韌體**：在 IntelProCube 目錄下執行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin `
            --pt <SDK>\apps\bluetooth\ble\ipro_ble_remote\partition_cfg_2M_remote_ab.toml `
            --firmware <SDK>\apps\bluetooth\ble\ipro_ble_remote\build_reef\build_out\ipro_ble_remote_IPRO7.bin
        ```

    `--chip-variant IPRO7AI` 選擇 Reef（QFN56）的 Flash 腳位。工具失敗時也會以 0 結束，請確認輸出中有 `[All Success]`。使用 IPRO Debug Probe 時，連接埠是名稱以 `02` 結尾的那一個。之後每次重新燒錄這個應用都用同一個完整命令，A/B 配置才會保持一致。

4. **開啟主控台並重置**：以 115200 baud 開啟 U6 的序列埠（方法見[燒錄與序列埠](../get-started/flash-and-monitor.md)），按一下 SW2（RESET）。主控台先出現 boot2 的訊息，再出現應用的開機訊息（行首的等級、時間等欄位省略）：

    ```text
    [BOOT2] IPRO7 Boot2 v0.5.2
    ...
    REMOTE_APP: [BLE] Initialized
    REMOTE_APP: [BLE] All services initialized
    REMOTE_APP: [BLE] Advertising: IPRO-Remote
    ```

5. **從手機連線**：
    - 用隨附的 Android App：把 `ipro_remote_demo.apk` 複製到手機後開啟安裝（需允許安裝未知來源的 App），或在電腦上執行 `adb install apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk`。
    - 用 BLE 工具 App：掃描並連線 `IPRO-Remote`。

    連上後主控台印出：

    ```text
    REMOTE_APP: Connected! Peer: <手機位址>
    ```

6. **操作 GATT 服務**：在 BLE 工具 App 中找到下列特徵值並操作：

    | 動作 | 特徵值 | 板上結果 |
    |---|---|---|
    | 寫入 `01` | LED State `0xFF11` | WS2812 LED 亮起（預設白色），主控台印出 `[LED] State: ON` |
    | 寫入 `00 FF 00` | LED Colour `0xFF81` | LED 改為綠色（3 bytes：R、G、B） |
    | 開啟通知後按 SW3 | Button State `0xFF21` | 手機收到 `01`（按下）與 `00`（放開） |
    | 開啟通知 | UART TX `0xFF41` | 手機收到 `Welcome to IPRO Remote!` |
    | 寫入文字 `hello` | UART RX `0xFF42` | 主控台印出 `[UART RX] hello`，手機收到 `Echo: hello` |
    | 寫入 `E8 03 2C 01 1E` | Tone `0xFF84` | 喇叭（或插在 J2 的耳機）發出 1 kHz、300 ms 的聲音（頻率、時間皆為 little-endian u16，最後一個 byte 是音量 %） |

    SW1（BOOT）短按會讓應用拍一張照片（需接相機；插著 microSD 卡時另存到 `sd:/REMOTE/`），測試按鍵時請用 SW3、SW4 或 SW5。主控台的 `reef status` 指令會列出板卡、LED、相機與溫度狀態。

7. **修改程式**：編輯 `apps/bluetooth/ble/ipro_ble_remote/src/app/remote_app.c` 的三處。

    檔案開頭已在 `CONFIG_IPRO7AI_REEF` 條件內引入 `remote_reef.h`，在它下面加入宣告 `reef_hw_tone()` 的 `reef_hw.h`：

    ```c title="src/app/remote_app.c"
    #if defined(CONFIG_IPRO7AI_REEF)
    #include "remote_reef.h"
    #include "reef_hw.h"
    #endif
    ```

    更改廣播名稱：

    ```c title="src/app/remote_app.c"
    #define DEVICE_NAME "IPRO-Hello"
    ```

    在 `connected_cb()` 中、`Connected! Peer` 那行記錄之後加入提示音：

    ```c title="src/app/remote_app.c"
        IPRO_LOGI(LOG_TAG, "Connected! Peer: %s", addr_str);

    #if defined(CONFIG_IPRO7AI_REEF)
        /* 手機連上時，喇叭與耳機孔發出 1 kHz、150 ms 的短嗶聲 */
        (void)reef_hw_tone(1000, 150, 30);
    #endif
    ```

    `reef_hw_tone()` 只把請求交給負責 Reef 硬體的任務就返回，可以安全地在 BLE 連線回呼中呼叫。這個應用以 `-Werror` 編譯，任何警告都會讓建置失敗。

8. **重新建置並燒錄**：重複步驟 1 的建置命令（只會重新編譯修改過的檔案），在主控台輸入 `reboot_dl`，再用步驟 3 的命令燒錄。

9. **再次連線**：按 SW2 重置後，主控台印出 `REMOTE_APP: [BLE] Advertising: IPRO-Hello`。在手機上重新掃描並連線 `IPRO-Hello`，連上的瞬間 Reef 會嗶一聲。

10. **準備 OTA 工具**：之後的更新改走 BLE，不必接 U6。在 SDK 根目錄建立 Python 虛擬環境並安裝 `bleak`：

    ```bash
    python3 -m venv .venv
    .venv/bin/pip install bleak
    ```

    手機與工具 App 先中斷和板子的連線：Reef 設定只允許一條連線（`CONFIG_BT_CONN=1`）。

11. **產生 OTA 套件**：隨意改一處程式（例如把提示音改成 `reef_hw_tone(2000, 150, 30)`），重新建置（步驟 1），再把建置結果打包成 boot2 OTA 套件。打包腳本會呼叫 IntelProCube 產生整體映像，再以 SDK 的 `tools/create_ota.py` 壓縮：

    === "macOS"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    === "Linux"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    產出：`apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota`（約 345 KB）。OTA 只接受這個 `.xz.ota` 套件，不能直接送 `.bin`。

12. **以 BLE 推送並確認**：`reef_ota.py` 預設尋找名為 `IPRO-Remote` 的裝置，板子已改名，所以用 `REMOTE_NAME` 指定：

    ```bash
    REMOTE_NAME=IPRO-Hello .venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py \
        apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota
    ```

    工具依序印出板子目前的版本資訊、套件大小與 CRC32、傳送時間、`verified, slot switched; rebooting`，等板子重新開機後再連一次並印出新的版本資訊：

    ```text
    running: <相機、SD 卡與編譯時間>
    ipro_ble_remote_reef.xz.ota: <位元組數> bytes, CRC32 <值>, <酬載> bytes/packet
    sent in <秒數> s (<速率> KB/s)
    verified, slot switched; rebooting
    running: <新的編譯時間>
    ```

    板子的主控台同時印出 `[OTA] START: …`、`[OTA] CRC32 OK! Switching partition...`、`[OTA] Ready to reboot`，重新開機時再次出現 `[BOOT2] IPRO7 Boot2 v0.5.2`：boot2 驗證套件的 SHA256、解壓到 FW A 後才啟動應用。INTELPRO 在 macOS、MTU 247 下實測 345 KB 套件的傳輸時間為 13–17 秒。隨附的 Android 示範 App 也能推送同一個 `.xz.ota` 套件。

</div>

!!! danger "不要用標準分割表做 OTA"
    Reef 上只能以 `partition_cfg_2M_remote_ab.toml` 做 OTA。若板子是用 IntelProCube 的標準 `partition_cfg_2M.toml` 燒錄的，OTA 寫進它的 FW B（0x12A000）並切換後，板子完全沒有輸出，只能進下載模式重新燒錄。

## 確認結果 { #verify }

- 主控台的廣播訊息顯示 `IPRO-Hello`，手機掃描清單也出現 `IPRO-Hello`。
- 手機連線時聽得到嗶聲，主控台印出 `Connected! Peer: …`。
- 步驟 6 的 LED、按鍵與 UART 操作仍然正常。
- `reef_ota.py` 最後一行的 `running:` 顯示新的編譯時間，重新連線時聽到步驟 11 改過的提示音。

`main.c` 開機橫幅中的 `Device Name: 'IPRO-Remote'` 是固定字串，不影響廣播名稱。

## 程式如何運作 { #how-it-works }

`main.c` 完成平台初始化後建立 `BLERemote` 任務，任務呼叫 `remote_app_init()`。BLE 依固定順序啟動：先建立控制器任務，再初始化 HCI 驅動，最後啟動 Zephyr Host（取自 `src/app/remote_app.c`）：

```c title="src/app/remote_app.c"
err = ipro_ble_ctlr_controller_init(configMAX_PRIORITIES - 1);  /* IPRO BLE 控制器 */
vTaskDelay(pdMS_TO_TICKS(50));
err = hci_driver_ipro_ble_ctlr_init();                           /* HCI 驅動 */
vTaskDelay(pdMS_TO_TICKS(50));
err = bt_enable(bt_ready_cb);                                    /* Zephyr Host */
```

Host 就緒後，`bt_ready_cb()` 依序呼叫 `bt_set_name(DEVICE_NAME)`、`bt_conn_cb_register(&conn_callbacks)` 註冊連線回呼，初始化 GATT 服務，最後開始可連線廣播。服務以 `BT_GATT_SERVICE_DEFINE()` 靜態定義於 `src/services/remote_services.c`。廣播資料與參數如下，`DEVICE_NAME` 同時用在廣播資料與 `bt_set_name()`：

```c title="src/app/remote_app.c"
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
};

struct bt_le_adv_param adv_param = {
    .id = BT_ID_DEFAULT,
    .options = BT_LE_ADV_OPT_CONN,
    .interval_min = 160,  /* 100ms (N * 0.625ms) */
    .interval_max = 320,  /* 200ms */
};
int err = bt_le_adv_start(&adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
```

Reef 設定另外編入兩個服務：OTA `0xFF60`（控制 `0xFF61`、資料 `0xFF62`、狀態 `0xFF63`）與 Reef 硬體服務 `0xFF80`（LED Colour `0xFF81`、Key Event `0xFF82`、Sound Level `0xFF83`、Tone `0xFF84`、Board Info `0xFF85`）。LED、按鍵、喇叭、SD 卡與相機的驅動直接引用開箱韌體 `apps/platform/ipro7ai_reef_demo/src` 的原始碼；`src/board/reef_hw.c` 是唯一操作這些硬體的任務，BLE 回呼只投遞請求給它。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 燒錄輸出沒有 `[All Success]`，或出現 `flash jedec id: 00000000` | 未進入下載模式，或 Flash 腳位設定不符 | 先進入下載模式；確認命令有 `--chip-variant IPRO7AI` |
| 燒錄成功但主控台沒有任何輸出 | 未一併寫入 boot2 與 A/B 分割表，或序列埠鮑率不對 | 用步驟 3 的完整命令重燒；主控台設為 115200 |
| 手機仍顯示 `IPRO-Remote` | 手機快取了舊名稱 | 確認主控台的廣播訊息已是 `IPRO-Hello`，再關閉並重新開啟手機藍牙後掃描 |
| LED 不亮或沒有嗶聲 | WS2812 與喇叭放大器由 USB VBUS 供電；J2 插著耳機時喇叭關閉 | 以 USB-C 供電，不要只從 3.3 V 供電；拔掉耳機或改聽耳機 |
| 建置因警告失敗 | 應用以 `-Werror` 編譯 | 確認 `#include "reef_hw.h"` 放在 `CONFIG_IPRO7AI_REEF` 條件內，且呼叫寫在函式內 |
| `make_reef_ota.sh` 印出 `IntelProCube tool not found` | 沒有設定 `IPRO_FLASH_TOOL`，PATH 上也沒有燒錄工具 | 設定 `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`（或 `_linux`） |
| `make_reef_ota.sh` 印出 `build first: …` | 還沒有 `build_reef/` 的建置結果 | 先執行步驟 1 |
| `reef_ota.py` 印出 `IPRO-Remote not found` | 板子已改名、正與手機連線，或電腦的藍牙未開啟／未授權 | 設定 `REMOTE_NAME=IPRO-Hello`；中斷手機連線；macOS 上允許終端機使用藍牙 |
| `reef_ota.py` 印出 `device error …` | 板子拒絕套件或寫入失敗 | 確認送的是 `.xz.ota`；看主控台的 `[OTA]` 訊息 |
| OTA 後板子沒有回來 | boot2 驗證套件失敗時會停在 USB 救援模式 | 進入下載模式，以步驟 3 的命令重新燒錄 |

## 下一步 { #next-steps }

- [BLE 吞吐量測試](ble-throughput.md)：用兩塊 Reef 量測傳輸速率。
- [LE Audio 入門](le-audio.md)：在 Reef 上執行 LE Audio 耳機範例。
- [BLE 開發](../guides/ble.md)：控制器函式庫選擇、Host 設定與 API。
- [OTA 更新](../guides/ota.md)：分割表、OTA 套件格式與 boot2 的更新流程。
