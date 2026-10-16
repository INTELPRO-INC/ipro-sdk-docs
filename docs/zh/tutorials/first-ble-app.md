---
title: "第一個 BLE 應用"
description: 在 IPRO7AI Reef EVK 上執行 ipro_ble_remote，用手機操作 GATT 服務，再修改裝置名稱並在連線時發出提示音。
migrate_from:
  - "tutorials.html — 教學 1"
---

# 第一個 BLE 應用

完成本教學後，IPRO7AI Reef EVK 會執行 SDK 的 GATT 參考應用 `ipro_ble_remote`：手機可以點亮板上的 RGB LED、收到按鍵通知，並與板子互傳文字。接著您會修改程式，把廣播名稱改成 `IPRO-Hello`，並讓板子在手機連上時發出短嗶聲。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK：上電前插上 JP1，以 USB-C 供電；USB 轉 UART 線接 U6 接頭（115200 8N1）。詳見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)：工具鏈位於 `/opt/toolchain/riscv_ipro7/`，`make` 能建置 SDK 應用。
- IntelProCube v0.6.3 的命令列燒錄工具（`ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`），需另行取得。
- 一支手機，安裝可讀寫 GATT 特徵值的 BLE 工具 App，例如 nRF Connect 或 LightBlue。

!!! note "Reef 設定使用 2 MB Flash 與 A/B 分割表"
    `ipro_ble_remote` 的 Reef 設定 `defconfig_reef` 以 2 MB Flash 連結（`CONFIG_IPRO7_FLASH_2M=y`），並啟用 BLE OTA，因此第一次燒錄要一併寫入 boot2 與應用隨附的 A/B 分割表 `partition_cfg_2M_remote_ab.toml`。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **建置 Reef 設定**：在 SDK 根目錄執行：

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    `DEFCONFIG=` 不會動到 `.config`，建置目錄是 `build_reef/`。成功時連結器最後會印出記憶體用量表，產出檔為 `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`。

2. **讓 Reef 進入下載模式**：按住 SW1（BOOT），按一下 SW2（RESET），再放開 SW1。若板上韌體已有 shell，也可以在主控台輸入 `reboot_dl`。

3. **第一次燒錄（boot2＋A/B 分割表＋韌體）**：在 IntelProCube 目錄下執行：

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

    `--chip-variant IPRO7AI` 選擇 Reef（QFN56）的 Flash 腳位。工具失敗時也會以 0 結束，請確認輸出中有 `[All Success]`。

4. **開啟主控台並重置**：以 115200 baud 開啟 U6 的序列埠（方法見[燒錄與序列埠](../get-started/flash-and-monitor.md)），按一下 SW2（RESET）。主控台先出現 boot2 的訊息，再出現應用的開機訊息（行首的等級、時間等欄位省略）：

    ```text
    [BOOT2] IPRO7 Boot2 v0.5.2
    ...
    REMOTE_APP: [BLE] Initialized
    REMOTE_APP: [BLE] All services initialized
    REMOTE_APP: [BLE] Advertising: IPRO-Remote
    ```

5. **從手機連線**：在 BLE 工具 App 中掃描並連線 `IPRO-Remote`。主控台會印出：

    ```text
    REMOTE_APP: Connected! Peer: <手機位址>
    ```

6. **操作 GATT 服務**：在 App 中找到下列特徵值並操作：

    | 動作 | 特徵值 | 板上結果 |
    |---|---|---|
    | 寫入 `01` | LED State `0xFF11` | WS2812 LED 亮起（預設白色），主控台印出 `[LED] State: ON` |
    | 寫入 `00 FF 00` | LED Colour `0xFF81` | LED 改為綠色（3 bytes：R、G、B） |
    | 開啟通知後按 SW3 | Button State `0xFF21` | 手機收到 `01`（按下）與 `00`（放開） |
    | 開啟通知 | UART TX `0xFF41` | 手機收到 `Welcome to IPRO Remote!` |
    | 寫入文字 `hello` | UART RX `0xFF42` | 主控台印出 `[UART RX] hello`，手機收到 `Echo: hello` |

    SW1（BOOT）短按會讓應用拍照，測試按鍵時請用 SW3、SW4 或 SW5。

7. **修改程式**：編輯 `apps/bluetooth/ble/ipro_ble_remote/src/app/remote_app.c` 的三處。

    加入 Reef 硬體介面的標頭檔：

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

8. **重新建置並燒錄**：重複步驟 1 的建置命令（只會重新編譯修改過的檔案），進入下載模式後，用步驟 3 的命令再燒錄一次。

9. **再次連線**：重置板子後，主控台印出 `REMOTE_APP: [BLE] Advertising: IPRO-Hello`。在手機上重新掃描並連線 `IPRO-Hello`，連上的瞬間 Reef 會嗶一聲。

</div>

## 確認結果 { #verify }

- 主控台的廣播訊息顯示 `IPRO-Hello`，手機掃描清單也出現 `IPRO-Hello`。
- 手機連線時聽得到嗶聲，主控台印出 `Connected! Peer: …`。
- 步驟 6 的 LED、按鍵與 UART 操作仍然正常。

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

自己寫廣播參數時，可沿用上面的 `struct bt_le_adv_param`，或使用 Host 提供的巨集，例如 `BT_LE_ADV_CONN_FAST_1`。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 燒錄輸出沒有 `[All Success]`，或出現 `flash jedec id: 00000000` | Flash 腳位設定不符 | 確認命令有 `--chip-variant IPRO7AI`，並先讓板子進入下載模式 |
| 燒錄成功但主控台沒有任何輸出 | 未使用 boot2 與 A/B 分割表，或序列埠鮑率不對 | 用步驟 3 的完整命令重燒；主控台設為 115200 |
| 手機仍顯示 `IPRO-Remote` | 手機快取了舊名稱 | 確認主控台的廣播訊息已是 `IPRO-Hello`，再關閉並重新開啟手機藍牙後掃描 |
| LED 不亮或沒有嗶聲 | WS2812 與喇叭放大器由 USB VBUS 供電 | 以 USB-C 供電，不要只從 3V3 供電 |
| 建置因警告失敗 | 應用以 `-Werror` 編譯 | 確認 `#include "reef_hw.h"` 放在 `CONFIG_IPRO7AI_REEF` 條件內，且呼叫寫在函式內 |

## 下一步 { #next-steps }

- [建置與燒錄流程](build-and-flash.md)：加快日常的建置、燒錄與監看迴圈。
- [BLE 吞吐量測試](ble-throughput.md)：用兩塊 Reef 量測傳輸速率。
- [BLE 開發](../guides/ble.md)：控制器函式庫選擇、Host 設定與 API。
- [OTA 更新](../guides/ota.md)：`ipro_ble_remote` 的 Reef 設定已含 BLE A/B OTA，操作方式見應用目錄的 README。
