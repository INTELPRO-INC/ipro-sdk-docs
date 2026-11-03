---
title: "USB 網路攝影機與剪刀石頭布"
description: 在 IPRO7AI Reef EVK 上以 ipro7_uvc_cam 把 OV5640 相機變成免驅動的 USB 網路攝影機，再換成在 NPU 上執行剪刀石頭布、把結果畫進影像的版本。
---

# USB 網路攝影機與剪刀石頭布

完成本教學後，IPRO7AI Reef EVK 接上 OV5640 相機，經 USB-C 成為電腦上的一支 USB 網路攝影機（UVC，MJPEG），不必安裝驅動程式；您可以在電腦的相機程式中選 1280×720 或 640×360 觀看。接著換成 `defconfig_reef_rps` 設定：板子在 NPU 上辨識手勢，和您玩剪刀石頭布，遊戲畫面直接畫在送給電腦的影像裡。兩者都是 `apps/multimedia/ipro7_uvc_cam` 應用的 Reef 設定。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK、OV5640 FLEX-24 相機模組，以及一條可傳資料的 USB-C 線（接電腦，同時供電與傳影像）。
- U6 接 IPRO Debug Probe 或 3.3 V USB 轉 UART 線（115200 8N1，接法見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)），用來燒錄與看主控台。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)，並取得 IntelProCube v0.6.3 命令列燒錄工具（需另行取得）。
- 電腦上能開啟 USB 相機的程式：macOS 的 QuickTime Player、Windows 的「相機」App，或 Linux 上任何 V4L2 程式（例如 `ffplay`）。主機使用作業系統內建的 UVC 驅動；INTELPRO 在 macOS 上驗證過。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **接上相機**：先拔掉 USB-C。把 OV5640 模組的排線插進 FPC1，確認 SW7 在 CAM（相機腳位接到 IPRO7AI、相機電源開啟）、SW8 在 PWR，接好 U6，最後把 USB-C 接到電腦。

2. **建置網路攝影機設定**：在 SDK 根目錄執行：

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640
    ```

    產出：`apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin`。不加 `DEFCONFIG=` 的 `make` 建置的是另一塊板子（IPRO7 EVB）的版本，不能用在 Reef。

3. **燒錄**：按住 SW1（BOOT）、按一下 SW2（RESET）、放開 SW1 進入下載模式，再於 IntelProCube 目錄下以標準 2 MB 分割表燒錄：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\multimedia\ipro7_uvc_cam\build_reef_ov5640\build_out\ipro7_uvc_cam_IPRO7.bin
        ```

    確認輸出中有 `[All Success]`（工具失敗時也以 0 結束）。這兩個設定不使用 `mfg` 分割區。

4. **開啟主控台並重置**：以 115200 baud 開啟 U6 的序列埠，按一下 SW2。主控台印出：

    ```text
    [SYS] Reset reason: <原因>
    [UVC] Starting init task...
    [OS] Starting OS Scheduler...
    [UVC] Bringing up USB UVC webcam (720p MJPEG)...
    [UVC] Streaming pipeline started
    ```

5. **確認電腦認得攝影機**：板子以 `IPRO7 UVC Cam` 的名稱出現，USB VID／PID 為 `0x3896`／`0x0701`：

    === "macOS"

        ```bash
        system_profiler SPUSBDataType | grep -A4 "IPRO7 UVC Cam"
        ```

    === "Linux"

        ```bash
        lsusb -d 3896:0701
        ```

    === "Windows"

        在「裝置管理員」的「相機」下出現 `IPRO7 UVC Cam`。

6. **在電腦上觀看**：
    - macOS：開啟 QuickTime Player，選「檔案 > 新增影片錄製」，在錄製按鈕旁的選單選 `IPRO7 UVC Cam`。
    - Windows：開啟「相機」App，切換到 `IPRO7 UVC Cam`。
    - Linux：

        ```bash
        ffplay -f v4l2 -input_format mjpeg -video_size 640x360 /dev/video0
        ```

    影像有兩種大小，由電腦端的程式選擇：1280×720（畫面複雜時約 15 fps，受 USB Full-Speed 頻寬限制）與 640×360（30 fps）。

7. **調整感測器（選用）**：主控台的 `cam` 指令可以直接讀寫 OV5640 的暫存器（暫存器位址與資料皆為十六進位），也能印出畫面分格的統計：

    ```text
    cam rd 300a 2
    ```

    ```text
    RD 300a 56 40
    ```

    `300a`、`300b` 是 OV5640 的晶片 ID（`0x56`、`0x40`）。`cam wr <reg> <hexbytes>` 寫入暫存器，`cam grid [cols rows]` 以 `GRID … GRIDEND` 印出各格的平均 Y、U、V。寫入的值在重置後恢復預設。

8. **換成剪刀石頭布設定**：建置 `defconfig_reef_rps`，以步驟 3 的方式燒錄（命令中的路徑改成 `build_reef_rps`）：

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps
    ```

    產出：`apps/multimedia/ipro7_uvc_cam/build_reef_rps/build_out/ipro7_uvc_cam_IPRO7.bin`。手勢分類模型已連結進韌體，不必另外燒錄模型。

9. **開始玩**：重置後在電腦上以 640×360 開啟 `IPRO7 UVC Cam`。畫面上方是比分列、下方是訊息列，中間的方框是 NPU 看的區域，框內即時顯示目前辨識到的手勢。把手放進方框並保持不動：畫面倒數 3、2、1，板子擷取您的手勢、隨機出拳，再顯示雙方的手勢與比分；手離開方框後才會開始下一局。

    在主控台輸入 `rps` 查看模型與遊戲狀態：

    ```text
    rps
    ```

    ```text
    model   : ready, <位元組數> B from <來源>, loaded in <毫秒> ms, <剩餘> KB heap left
    npu     : <影格數> frames, 0 errors, <每秒推論次數> fps, last <毫秒> ms
    now     : <目前手勢> <信心度>%  (r <%> p <%> s <%> n <%>)
    game    : round <局數>, you <勝> me <負> draw <和>, conf >= 60%, mirror on
    ```

    | 指令 | 作用 |
    |---|---|
    | `rps go` | 不等手放進方框，立刻開始一局 |
    | `rps reset` | 比分歸零 |
    | `rps mirror on\|off` | 影像左右鏡像（預設開，像照鏡子）；觀看程式本身會鏡像預覽時（例如 Photo Booth、FaceTime）改為 `off` |
    | `rps print on\|off` | 在主控台逐筆印出分類結果 |
    | `rps conf <百分比>` | 計入一次手勢所需的信心度（預設 60） |
    | `rps dump` | 以 base64 印出 NPU 看到的一張 128×128 影像（`CAPBEGIN` 到 `CAPEND`，115200 baud 約 8 秒） |

</div>

## 確認結果 { #verify }

- 主控台印出 `[UVC] Streaming pipeline started`，電腦列出 `IPRO7 UVC Cam`（`3896:0701`）。
- 網路攝影機設定：相機程式顯示即時影像，可以在 1280×720 與 640×360 之間切換。
- 剪刀石頭布設定：影像上有比分列、方框與即時手勢標籤；把手放進方框會開始倒數，`rps` 的 `npu` 一行的影格數持續增加。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 電腦沒有出現 `IPRO7 UVC Cam` | USB-C 線只能充電，或燒錄的是非 Reef 版本 | 換一條可傳資料的線；確認燒錄的是 `build_reef_ov5640` 或 `build_reef_rps` 的檔案 |
| 主控台停在 `Bringing up …`，或影像全黑 | 相機沒接好，或 SW7 不在 CAM | 拔掉 USB-C 後重插相機排線，SW7 撥到 CAM，再上電 |
| 1280×720 的影格率偏低 | USB Full-Speed 的頻寬上限，畫面越複雜 MJPEG 越大 | 改用 640×360（30 fps） |
| 剪刀石頭布左右顛倒 | 觀看程式自己也做了鏡像 | 輸入 `rps mirror off` |
| 手放在方框裡卻不倒數 | 辨識信心度低於門檻，或手的位置太偏 | 用 `rps print on` 看分類結果；調整光線與距離；必要時 `rps conf 50` |
| 燒錄輸出沒有 `[All Success]` | 未進入下載模式，或缺少 `--chip-variant IPRO7AI` | 重新進入下載模式；確認命令參數 |

## 下一步 { #next-steps }

- [IPRO AI Teach](../teach/index.md)：用自己的影像訓練分類器並部署到 Reef（`ipro_reef_teach` 的影像模式使用同一套相機管線）。
- [相機與影像](../guides/camera.md)：影像管線、ISP 通道與支援的感測器。
- [AI 與 NPU](../guides/ai-npu.md)：NPU 推論與模型。
- [Wi-Fi 與 RTSP 相機串流](wifi-rtsp.md)：改經 Wi-Fi 以 RTSP 送出相機影像。
