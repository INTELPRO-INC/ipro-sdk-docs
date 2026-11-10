---
title: "Wi-Fi 與 RTSP 相機串流"
description: 讓 IPRO7AI Reef EVK 經 microSD 卡座上的 IPRO6S FIN 卡連上 Wi-Fi，以 RTSP 把 OV5640 相機的影像串流到電腦，並以 ipro6s_ota 更新 FIN 卡韌體。
---

# Wi-Fi 與 RTSP 相機串流

IPRO7AI Reef EVK 經 FIN 卡連網：FIN 卡是插在 microSD 卡座（CARD1）上的 IPRO6S Wi-Fi 卡，以 SDIO 與 IPRO7AI 溝通。完成本教學後，Reef 執行開箱韌體的 Wi-Fi 版本 `ipro7ai_reef_demo`（`defconfig_wifi_ipro6s`），連上您的無線基地台，並以 RTSP 在 `rtsp://<IP>:8554/av0_0` 提供相機的 MJPEG 影像，電腦用 VLC 或 `ffplay` 觀看。最後說明如何以 `ipro6s_ota` 經 Wi-Fi 更新 FIN 卡的韌體。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK、IPRO6S FIN 卡、OV5640 FLEX-24 相機模組。
- FIN 卡上要有 Wi-Fi 韌體：IPRO6S 的 `ipro6_if_wifi`，以 `defconfig_ipro6_sdio` 建置（SDIO 版本，見步驟 2）。
- U6 接 IPRO Debug Probe 或 3.3 V USB 轉 UART 線（115200 8N1，接法見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)，並依[準備開發環境](../get-started/environment.md#intelprocube)安裝 IntelProCube 0.7.0.1 命令列燒錄工具。
- 一台無線基地台（SSID 與密碼），以及一台連在同一個網路上、裝有 VLC 或 `ffplay` 的電腦。

!!! info "FIN 卡的第一次燒錄"
    SDK 提供 FIN 卡韌體的原始碼與建置設定，也提供經 Wi-Fi 更新韌體的 `ipro6s_ota` 指令；FIN 卡上還沒有韌體時，第一次寫入韌體的方式請洽 INTELPRO。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **接上 FIN 卡與相機**：先拔掉 USB-C。把 JP3 設在 GPIO（卡座電源改由 GPIO14 控制，`fin cycle` 才能重新為卡片上電），把 FIN 卡插進 microSD 卡座，相機排線插進 FPC1，確認 SW7 在 CAM、SW8 在 PWR，接好 U6，最後接上 USB-C 供電。

2. **（選用）建置 FIN 卡韌體**：要更新 FIN 卡（步驟 10）時才需要。在 SDK 根目錄執行：

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
    ```

    產出：`apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。這個設定開機約 600 ms 後自動啟動 Wi-Fi 與 SDIO 橋接，FIN 卡上不必輸入任何指令；連線與 DHCP 都由 Reef 端控制。

3. **建置 Reef 的 Wi-Fi 版本**：

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    產出：`apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin`。這個設定在開箱韌體上加入 `components/network/ipronet_host`（SDIO 主機端）、lwIP 與 RTSP 伺服器（埠 8554）；USB 麥克風功能（`mic usb`）因此移除。

4. **燒錄**：按住 SW1（BOOT）、按一下 SW2（RESET）、放開 SW1 進入下載模式（板上已在執行開箱韌體時，也可以輸入 `reboot_dl`），再於 IntelProCube 目錄下執行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build_wifi_ipro6s\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    確認輸出中有 `[All Success]`（工具失敗時也以 0 結束）。

5. **開啟主控台並確認 FIN 卡**：以 115200 baud 開啟主控台，按一下 SW2。開機訊息最後印出可用的指令（行首的等級、時間等欄位省略）：

    ```text
    REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    REEF: IPRO-WiFi - `ipronet_up <ssid> <psk>`
    REEF: RTSP - `rtsp_cam on [fps]`
    ```

    輸入 `fin`，確認卡片已插好、卡座有電：

    ```text
    IPRO6S_FIN: SDIO slave in the SD slot, SD_VDD = its 3V3.
      seated : yes (DET GPIO15)
      supply : on (GPIO14, JP3 2-3 required for control)
      host   : SDH_0 on GPIO28-33, see apps/platform/ipro7_sdio_wifi
    fin cycle | fin power on|off
    ```

    （訊息中的「JP3 2-3」是舊版板子的跳線名稱，在 V4.0 板上對應 JP3＝GPIO。）

6. **啟動 Wi-Fi 並掃描基地台**：

    ```text
    ipronet_up
    ipro6s_scan
    ipro6s_scan_last
    ```

    `ipronet_up` 不帶參數時只啟動 FIN 卡上的 Wi-Fi，印出 `ipronet_start -> 0`。`ipro6s_scan` 開始掃描，結果非同步送回；稍等一兩秒後，`ipro6s_scan_last` 列出最近一次的結果：

    ```text
    [ctrl] scan_last: <數量> APs (on_scan_result fired <次數> times)
       0 ssid=<SSID>                           rssi=<訊號強度> ch=<頻道> auth=<加密方式>
    ```

7. **連上基地台**：

    ```text
    ipro6s_connect <SSID> <密碼>
    ```

    ```text
    [ctrl] connect '<SSID>' -> 0 (CONNECTED_IND + IP_UPDATE_IND arrive async)
    [ctrl] STA CONNECTED
    [ctrl] IP <IP 位址> / <子網路遮罩> gw <閘道>
    ```

    也可以一步完成啟動與連線：重置後直接輸入 `ipronet_up <SSID> <密碼>`。若沒有看到 `[ctrl] IP …` 這一行，輸入 `ipro6s_link_status`，`host connected=1 ip=1` 表示已連線並取得 IP。

8. **開始 RTSP 串流**：

    ```text
    rtsp_cam on
    ```

    相機未啟動時會先啟動相機，再印出影像格式與網址：

    ```text
    rtsp_cam: on, <感測器> <寬>x<高> JPEG q<品質>, 15 fps
    rtsp_cam: rtsp://<IP 位址>:8554/av0_0
    ```

    預設 15 fps；`rtsp_cam on <fps>` 可指定 1–30。

9. **在電腦上觀看**：電腦與 Reef 在同一個網路上時，以 VLC 開啟網路串流（「媒體 > 開啟網路串流」），輸入上一步印出的網址；或使用 `ffplay`：

    ```bash
    ffplay rtsp://<IP 位址>:8554/av0_0
    ```

    `rtsp_cam stats` 顯示已送出的影格數、平均 JPEG 大小與編碼錯誤；`rtsp_cam off` 停止送出影像（相機繼續執行，`cam stop` 才停止相機）；`ipronet_down` 關閉 Wi-Fi。

10. **更新 FIN 卡韌體**：`ipro6s_ota` 從 HTTP 伺服器下載 IPRO6S 的 OTA 套件並寫入 FIN 卡，卡片重新開機後由它的 boot2 安裝。套件是 IntelProCube 產生的 IPRO6S 套件（`FW_OTA.bin.xz.ota`，512 bytes 標頭加 XZ 壓縮內容），以步驟 2 的建置結果產生套件的步驟請洽 INTELPRO。把套件放在電腦的某個資料夾，在該資料夾啟動 HTTP 伺服器：

    ```bash
    python3 -m http.server 8000
    ```

    在 Reef 的主控台（已連上 Wi-Fi）輸入：

    ```text
    ipro6s_ota http://<電腦的 IP>:8000/FW_OTA.bin.xz.ota
    ```

    整個過程約 30–60 秒：Reef 先停止 Wi-Fi 傳輸、下載套件，FIN 卡寫入並驗證後重新開機安裝，Reef 再重新列舉卡片並恢復連線。成功時印出：

    ```text
    [ota] fetch <位元組數> B in <毫秒> ms
    [ota] RESULT OK total=<毫秒> …
    ```

    失敗時印出 `[ota] RESULT ERR rc=<代碼> … phase=<階段>`。

</div>

## 確認結果 { #verify }

- `fin` 顯示 `seated : yes`，`ipro6s_scan_last` 列出附近的基地台。
- 連線後主控台印出 `[ctrl] IP …`，`ipro6s_link_status` 顯示 `host connected=1 ip=1`。
- `rtsp_cam on` 印出 `rtsp://<IP>:8554/av0_0`，VLC 或 `ffplay` 顯示即時影像，`rtsp_cam stats` 的影格數持續增加。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `fin` 顯示 `seated : no` | 卡片沒有插到底 | 拔掉 USB-C，重新插好 FIN 卡後再上電 |
| `ipronet_start` 傳回非 0 | FIN 卡沒有回應：沒有韌體、韌體不是 SDIO 版本，或卡片狀態異常 | JP3 在 GPIO 時輸入 `fin cycle` 重新上電後再試；確認卡上是 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio` 韌體 |
| `ipro6s_scan_last` 顯示 0 個 AP | 掃描結果尚未回來 | 等一兩秒再輸入一次 `ipro6s_scan_last`；必要時重新 `ipro6s_scan` |
| 一直沒有 `[ctrl] IP …` | SSID 或密碼錯誤，或基地台不在範圍內 | 用 `ipro6s_scan_last` 確認 SSID；`ipro6s_disconnect` 後重新 `ipro6s_connect` |
| `rtsp_cam: camera gives no frames - …` | 相機沒有影格 | 確認 SW7 在 CAM、相機排線插好；輸入 `cam stop` 後再 `rtsp_cam on` |
| `rtsp_cam: no IP yet - …` | Wi-Fi 還沒有取得 IP | 先完成步驟 7，再輸入 `rtsp_cam on` 取得網址 |
| VLC 連不上 | 電腦與 Reef 不在同一個網路，或基地台隔離了無線用戶端 | 確認電腦能 `ping <IP 位址>`；關閉基地台的用戶端隔離功能 |
| `ipro6s_ota` 印出 `[ota] RESULT ERR … phase=fetch` | 電腦的 HTTP 伺服器無法連線或路徑錯誤 | 在電腦的瀏覽器開同一個網址確認；檢查防火牆 |

## 下一步 { #next-steps }

- [網路](../guides/networking.md)：`ipronet_host` API、lwIP 整合與網路設定。
- [IPRO6S](../hardware/chips/ipro6s.md)：FIN 卡上的 IPRO6S 晶片與 `ipro6_if_wifi` 的其他設定。
- [USB 網路攝影機與剪刀石頭布](usb-webcam.md)：改經 USB 送出相機影像。
- [相機與影像](../guides/camera.md)：影像管線與感測器設定。
