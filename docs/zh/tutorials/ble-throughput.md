---
title: "BLE 吞吐量測試"
description: 以兩塊 IPRO7AI Reef EVK 執行 ipro_throughput_test，量測 1M 與 2M PHY 的 BLE 吞吐量，並與 SDK 的實測結果比對。
migrate_from:
  - "tutorials.html — 教學 3"
---

# BLE 吞吐量測試

兩塊 IPRO7AI Reef EVK 燒錄同一個 `ipro_throughput_test` 韌體，一塊當 Slave（peripheral），另一塊當 Master（central），透過自訂 GATT 服務灌送資料。完成後您會得到兩個方向在 1M 與 2M PHY 下的吞吐量，並能與 SDK 在相同條件下的實測值比對：Reef 對 Reef、2M PHY 可達 1.34 Mbps，1M PHY 可達 747 kbps。

## 前置需求 { #prerequisites }

- 兩塊 IPRO7AI Reef EVK，各自以 USB-C 供電，並各用一條 USB 轉 UART 線接 U6（115200 8N1）。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)，並取得 IntelProCube v0.6.3 命令列燒錄工具。
- 每塊板子各開一個可輸入指令的序列埠終端程式（見[燒錄與序列埠](../get-started/flash-and-monitor.md)）。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **建置 Reef 設定**：

    ```bash
    make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef
    ```

    產出：`apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin`。連結器的記憶體用量表顯示約 360 KB Flash，以及 224 KB OCRAM 區域中的約 205 KB。

2. **燒錄兩塊板子**：每塊板子先進入下載模式（按住 SW1、按一下 SW2、放開 SW1），再於 IntelProCube 目錄下以各自的序列埠燒錄同一個檔案：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\bluetooth\ble\ipro_throughput_test\build_reef\build_out\ipro_throughput_test_IPRO7.bin
        ```

    兩次燒錄的輸出都要有 `[All Success]`。

3. **開啟兩個主控台並重置**：兩個終端機都以 115200 baud 開啟，按各板的 SW2。重置後約 7 秒，主控台印出 `BLE initialized`（控制器先確認 32 kHz 時脈來源，所以需要一點時間）。以下訊息省略行首的等級、時間等欄位。

4. **建立連線**：先在 Slave 板輸入：

    ```text
    tp slave
    ```

    ```text
    TP_APP: Slave started - advertising as 'IPRO-TP-TEST'
    ```

    再在 Master 板輸入：

    ```text
    tp master
    ```

    Master 會掃描 `IPRO-TP-TEST` 並自動連線。等 Master 印出最後一行再繼續：

    ```text
    TP_APP: Found target: IPRO-TP-TEST RSSI:<訊號強度> Addr:<位址>
    TP_APP: Connected: <位址>
    ...
    TP_APP: MTU exchange complete: MTU=247
    ...
    TP_APP: Notifications enabled - ready for test
    ```

5. **設定連線參數與 PHY**：在 Master 板輸入（`tp conn` 的單位是 1.25 ms，40 即 50 ms）：

    ```text
    tp conn 40 40
    tp phy 2
    tp status
    ```

    兩塊板子都會印出 `Connection params updated: interval=40 …` 與 `PHY updated: TX=2 RX=2`；`tp status` 顯示 `Connection Interval: 50.00 ms` 與 `PHY: 2M`。

6. **量測下行（Slave → Master，notification）**：先在 Master 板輸入 `tp stats` 並記下 RX bytes，再在 Slave 板輸入：

    ```text
    tp start 244 10
    ```

    測試期間 Slave 每秒印出一行統計，10 秒後印出總結：

    ```text
    [TP] TX: <封包數> pkts, <位元組數> bytes, <速率> Kbps | RX: 0 pkts, 0 bytes, 0.0 Kbps | Err: 0
    ...
    === Throughput Test Statistics ===
    Duration: <毫秒> ms
    TX: <封包數> packets, <位元組數> bytes, <速率> Kbps (<速率> KBps)
    RX: 0 packets, 0 bytes, 0.00 Kbps (0.00 KBps)
    Errors: 0
    Connection: interval=50.00ms, PHY=2M
    ==================================
    ```

    測試結束後再在 Master 板輸入一次 `tp stats`。

7. **量測上行（Master → Slave，write without response）**：反過來做一次：先在 Slave 板輸入 `tp stats`，再在 Master 板輸入 `tp start 244 10`，結束後於 Slave 板再輸入 `tp stats`。

8. **改用 1M PHY 再量一次**：在 Master 板輸入 `tp phy 1`，重複步驟 6 與 7。要同時量測兩個方向，就在兩塊板子上同時輸入 `tp start 244 10`。

</div>

## 確認結果 { #verify }

傳送端總結中的 TX 速率，是 Host 協定堆疊接受的封包數換算而來，與實際送達只差幾個封包。接收端的 RX 計數器會跨測試累加，總結中的 RX 速率沒有意義。要算出實際送達的速率，請用接收端測試前後兩次 `tp stats` 的 RX bytes 差值：

```text
送達速率 (kbps) = (RX bytes 差值 × 8) ÷ 測試毫秒數
```

把結果與下一節的參考值比對。數值遠低於參考值時，先用 `tp status` 確認連線間隔與 PHY，再看[影響吞吐量的因素](#tuning)。

## 參考值 { #benchmarks }

以下是 SDK 隨附於 `ipro_throughput_test` README 的實測值（2026-10-07）：兩塊 IPRO7AI Reef EVK、預編譯 `link2` 控制器函式庫、ATT MTU 247、DLE 251 octets、244 bytes 酬載、灌送 8 秒，速率以接收端實際收到的封包計算。「下行」為 Slave → Master 的 notification，「上行」為 Master → Slave 的 write without response。

| PHY | 連線間隔 | 下行／上行，`CONFIG_IPRO7_BLE_HOTCODE=y`（隨附設定） | 下行／上行，關閉該選項 |
|---|---|---|---|
| 2M | 7.5 ms | 1055／1056 kbps | 891／957 kbps |
| 2M | 15 ms | 1180／1180 kbps | 921／930 kbps |
| 2M | 30 ms | 1315／1315 kbps | 737／788 kbps |
| 2M | 50 ms | **1342／1333 kbps** | 593／642 kbps |
| 1M | 7.5 ms | 526／525 kbps | 437／492 kbps |
| 1M | 15 ms | 656／656 kbps | 559／554 kbps |
| 1M | 30 ms | 722／721 kbps | 584／551 kbps |
| 1M | 50 ms | **747／746 kbps** | 535／568 kbps |

兩個方向同時傳送時（`CONFIG_IPRO7_BLE_HOTCODE=y`，每個方向的速率）：2M PHY、50 ms 為 782／783 kbps，30 ms 為 719／719 kbps，15 ms 為 653／654 kbps；1M PHY、50 ms 為 389／390 kbps。以 20 bytes 酬載（對應 MTU 23）在 1M PHY 測試時約 165 kbps，Coded S8 PHY 下行約 34 kbps。

## 影響吞吐量的因素 { #tuning }

- **空中時間**：一個 251 octets 的資料 PDU 加上空的確認封包與兩段封包間隔，在 2M PHY 約 1.39 ms、1M PHY 約 2.47 ms，所以 244 bytes 酬載的上限約為 2M 1.40 Mbps、1M 790 kbps。
- **連線事件長度**：控制器會提早結束每個連線事件以安排下一個，間隔越短，損失的比例越高。7.5 ms 間隔只容得下約四個 2M 封包（約 1.05 Mbps），所以大量資料傳輸適合 30–50 ms 間隔；在意延遲時用 15 ms，2M 仍有 1.18 Mbps。
- **CPU**：程式碼在 Flash 上執行時，每個封包的處理時間比封包在空中的時間還長，吞吐量就受 CPU 限制。隨附設定的 `CONFIG_IPRO7_BLE_HOTCODE=y` 把 BLE 每封包的處理路徑放到 OCRAM 執行；這需要約 88 KB 的 OCRAM，而且不能與 AI+MM 記憶體配置或低功耗設定（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_*`、`CONFIG_OCRAM_NORET_SPLIT`）同時使用。
- **先看 CPU，再調緩衝區**：在傳送端先輸入 `tp cpu`，開始測試，結束後再輸入一次 `tp cpu`。`IDLE` 的比例遠低於 50% 表示 CPU 是瓶頸，加大主機或控制器的緩衝區也沒有幫助。
- **小封包**：ATT MTU 23（20 bytes 酬載）時連線間隔幾乎沒有影響，1M PHY 約 165 kbps。
- **Coded PHY 未調校**：應用要求的最大傳送時間為 2120 µs，在 Coded S8 每個 PDU 只放得下約 27 octets。

`defconfig_reef` 只是把 `.config` 的 `CONFIG_EVB=y` 換成 Reef 板級設定，兩者的 BLE 設定相同：

```ini title="apps/bluetooth/ble/ipro_throughput_test/defconfig_reef（節錄）"
CONFIG_IPRO_BLE_CTLR_LIB="link2"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt52"
CONFIG_BT_CONN=2
CONFIG_EM_SIZE=32
CONFIG_BT_L2CAP_TX_BUF_COUNT=10
CONFIG_BT_CONN_TX_MAX=10
CONFIG_IPRO7_BLE_HOTCODE=y
CONFIG_FREERTOS_TIMER_TASK_STACK_WORDS=1024
```

## 指令參考 { #commands }

| 指令 | 說明 |
|---|---|
| `tp slave` | 以 peripheral 啟動並開始廣播 `IPRO-TP-TEST` |
| `tp master [addr]` | 以 central 啟動、掃描並連線；可指定位址 `XX:XX:XX:XX:XX:XX` |
| `tp start [size] [sec] [interval_ms]` | 由本板開始傳送 |
| `tp stop` | 停止測試；未在測試時則中斷連線 |
| `tp stats` | 顯示統計 |
| `tp status` | 顯示角色、狀態、連線間隔與 PHY |
| `tp phy <1\|2\|3>` | 要求 1M、2M 或 Coded PHY |
| `tp conn <min> <max>` | 要求連線間隔，單位 1.25 ms（latency 0、supervision timeout 1 秒） |
| `tp interval <ms>` | 變更進行中測試的傳送間隔 |
| `tp cpu` | 自上次 `tp cpu` 以來各任務的 CPU 比例與最小剩餘堆疊 |
| `tp help` | 顯示指令說明 |

`tp start` 的參數：`size` 預設 244（20–244 bytes）；`sec` 預設 10，`0` 表示直到 `tp stop`；`interval_ms` 省略時為灌送模式（flood），指定 1–1000 則為封包間隔。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 燒錄出現 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` | Flash 腳位設定不符 | 確認命令有 `--chip-variant IPRO7AI` |
| 每次重試都出現 `IPRO FLASH WRITE CHECK FAIL` | 某些映像檔會發生 | 在 IntelProCube 的 ini 設定 `decompress_write = false` 後燒錄，完成後改回 |
| Master 連到別塊板子 | 附近有多個 `IPRO-TP-TEST` 在廣播 | 關閉其他測試板，或用 `tp master XX:XX:XX:XX:XX:XX` 指定 Slave 的位址 |
| `Cannot start test - notifications not enabled by client` | 連線後的服務探索尚未完成 | 等 Master 印出 `Notifications enabled - ready for test` 再開始 |
| 速率遠低於參考值 | 連線間隔或 PHY 不如預期，或 CPU 滿載 | 用 `tp status` 確認間隔與 PHY，再用 `tp cpu` 檢查傳送端 |
| `tp phy 3` 後約 1 秒斷線（reason 0x08） | 切換到 Coded PHY 時偶爾發生 | 重新連線後再切換一次 |

## 下一步 { #next-steps }

- [BLE 開發](../guides/ble.md)：控制器函式庫（`link1_periph`、`link1`、`link2`、`link4`）與 Host 設定。
- [LE Audio 入門](le-audio.md)：在 Reef 上執行 LE Audio 耳機範例。
- [範例](../examples/index.md)：其他 BLE 應用與其 Reef 設定。
