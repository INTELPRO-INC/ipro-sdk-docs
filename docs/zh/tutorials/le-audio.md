---
title: "LE Audio 入門"
description: 在 IPRO7AI Reef EVK 上執行 LE Audio unicast 耳機 ipro_le_audio_headset：與 LE Audio 手機配對、以按鍵調整 VCP 音量、用測試音確認音訊輸出，並認識設定重點與本版的驗證範圍。
migrate_from:
  - "tutorials.html — 教學 4"
---

# LE Audio 入門

完成本教學後，IPRO7AI Reef EVK 會執行 `ipro_le_audio_headset`：以 `IPRO-LE-Audio` 名稱廣播，與支援 LE Audio 的手機配對，提供 PACS、ASCS、CAS 與 VCP 等 LE Audio 服務。您會用板上按鍵調整 VCP 音量、以測試音確認喇叭與耳機孔的輸出，並了解建置 LE Audio 應用需要的設定。

!!! warning "本版的驗證範圍"
    依應用 README，這個應用目前是 profile 與 ISO 資料路徑的開發版本，不是完成的音訊產品：
    
    - 已驗證：手機掃描、連線、配對（安全等級 4）、LE Audio 服務探索（`1853`、`1850`、`184e`、`1844`），以及 VCP 音量控制。
    - 尚未驗證：從手機串流音樂。Android 手機目前顯示此韌體沒有已連線的音訊通道。LC3 解碼後的播放與聲學驗證也尚未完成。
    
    `test_tone` 測試音直接驅動 DAC，不經 LE Audio 串流。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK：SW8 在 PWR，以 USB-C 供電；U6 接 IPRO Debug Probe 或 3.3 V USB 轉 UART 線（115200 8N1，接法見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。可另接耳機到 J2。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)，並取得 IntelProCube v0.6.3 命令列燒錄工具（需另行取得）。
- 一個可輸入指令的序列埠終端程式（見[燒錄與序列埠](../get-started/flash-and-monitor.md)）。
- 一支支援並已開啟 LE Audio 的 Android 手機。應用 README 記錄的測試手機是 Pixel 10 Pro（Android 17）。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **建置 Reef 設定**：

    ```bash
    make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef
    ```

    產出：`apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin`。這個設定以 2 MB Flash 連結（`CONFIG_IPRO7_FLASH_2M=y`）。不加 `DEFCONFIG=` 的 `make` 建置的是 IPRO7 EVB 版本。

2. **燒錄**：讓 Reef 進入下載模式（按住 SW1、按一下 SW2、放開 SW1；板上韌體有 shell 時也可以輸入 `reboot_dl`），再於 IntelProCube 目錄下執行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --firmware <SDK>\apps\bluetooth\le_audio\ipro_le_audio_headset\build_reef\build_out\ipro_le_audio_headset_IPRO7.bin
        ```

    工具失敗時也會以 0 結束，請確認輸出中有 `[All Success]`。

3. **開啟主控台並重置**：以 115200 baud 開啟主控台，按 SW2。開機後會看到下列訊息（省略行首的等級、時間等欄位）：

    ```text
    MAIN: IPRO LE Audio Headset v2.0 (Zephyr blestack)
    ...
    BLE_INIT: Advertising started: IPRO-LE-Audio
    KEYS: Keys: SW3 vol-, SW4 vol+, SW5 mute (GPIO<n>/<n>/<n>)
    ```

4. **確認音訊輸出**：輸入下列指令，喇叭會播放 3 秒的 1 kHz 測試音；J2 插著耳機時，喇叭放大器關閉，聲音只從耳機出來。

    ```text
    test_tone 3
    ```

5. **與手機配對**：在手機的藍牙設定中配對新裝置，選擇 `IPRO-LE-Audio`。主控台會印出：

    ```text
    BLE_INIT: Connected: <手機位址>
    BLE_INIT: Security requested: level 2
    BLE_INIT: Security changed: <手機位址> level <n>
    BLE_INIT: [SMP] Pairing complete: <手機位址>, bonded=1
    ```

    手機會把它列為 LE Audio 裝置。配對資訊存在 Flash 中，重新開機後仍保留。

6. **以按鍵調整音量**：按 SW4 調高、SW3 調低、SW5 靜音或取消靜音。按鍵經 VCP Volume Renderer 改變音量，已連線的手機音量條會跟著變動。主控台印出：

    ```text
    VCP_SERVER: Volume state changed: volume=<0-255> mute=<0|1>
    ```

    輸入 `vol` 可查看目前音量。

7. **查看狀態**：

    ```text
    leaudio_status
    ```

    顯示 `BLE Ready`、收到與解碼的音訊幀數，以及目前的取樣率與輸出（`DAC (Speaker)`）。

</div>

!!! info "從手機串流音樂"
    從手機串流音樂在本版尚未驗證（見本頁開頭）。若您的音源端建立了串流，主控台會印出 `Stream … started (Streaming state)`，`leaudio_status` 的 `Frames Received` 會持續增加；結果請以實際量測為準。

## 確認結果 { #verify }

- 主控台印出 `Advertising started: IPRO-LE-Audio`，`test_tone 3` 有聲音。
- 手機完成配對，主控台印出 `Pairing complete: …, bonded=1`。手機探索到的服務包含 CAS（`0x1853`）、PACS（`0x1850`）、ASCS（`0x184E`）與 VCS（`0x1844`）。
- 按 SW3／SW4／SW5 時主控台印出 `Volume state changed`，手機的音量條同步變動。

## 設定重點 { #configuration }

LE Audio 需要支援 ISO 的控制器函式庫與較大的 Exchange Memory，Host 則依角色啟用對應的 profile。以下節錄自 `defconfig_reef`：

```ini title="apps/bluetooth/le_audio/ipro_le_audio_headset/defconfig_reef（節錄）"
# 控制器：peripheral ACL＋兩路 ISO，Bluetooth 5.4 功能
CONFIG_IPRO_BLE_CTLR_LIB="link1_periph"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt54_iso2"
CONFIG_IPRO_BLE_CTLR_CFG_DBG=y
CONFIG_EM_SIZE=32
CONFIG_BT_CONN=1

# 配對與綁定
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_BT_BONDABLE=y

# LE Audio profile
CONFIG_BT_AUDIO=y
CONFIG_BT_AUDIO_RX=y
CONFIG_BT_BAP_UNICAST_SERVER=y
CONFIG_BT_PACS=y
CONFIG_BT_ASCS=y
CONFIG_BT_VCP_VOL_REND=y
CONFIG_BT_CAP_ACCEPTOR=y
CONFIG_BT_CSIP_SET_MEMBER=y

# ISO 通道
CONFIG_BT_ISO=y
CONFIG_BT_ISO_RX=y
CONFIG_BT_ISO_PERIPHERAL=y

# LC3 編解碼器（預編譯）與 DAC 輸出
CONFIG_COMPONENTS_LC3_ENABLE=y
CONFIG_BSP_USING_DAC=y
```

- `bt54_iso2` 需要 `CONFIG_EM_SIZE` 至少 32，否則建置在設定階段就會停止。
- `CONFIG_IPRO_BLE_CTLR_CFG_DBG=y` 選用除錯版控制器函式庫；未設定時使用 `_release` 版。
- 這個應用沒有啟用媒體控制（MCP）與通話控制（CCP）。

Reef 只使用 `defconfig_reef`：DAC 輸出到喇叭與 J2 耳機孔（J2 插著耳機時喇叭放大器關閉），SW3／SW4／SW5 經 VCP 調整音量。`dac os 0|1|2` 切換 DAC 輸出路徑（Reef 預設 `1`，512 kHz 加雜訊整形），`dac spk <dB>` 調整喇叭路徑的增益。應用的 `.config`、`DAC.config` 與 `UAC.config` 是 IPRO7 EVB 的設定。

## LE Audio 名詞 { #concepts }

| 名詞 | 意義 | 在 `ipro_le_audio_headset` 中 |
|---|---|---|
| CIS | 連線式等時串流，一對一，用於耳機 | 接收端 |
| BIS | 廣播等時串流，一對多（Auracast） | 未使用 |
| BAP | 建立與管理音訊串流 | Unicast Server，2 個 sink ASE |
| PACS | 宣告支援的編解碼能力 | LC3：16／32／48 kHz、7.5／10 ms、單聲道、每幀 26–155 octets |
| ASCS | 音訊串流端點（ASE）的設定與狀態 | 啟用 |
| VCP | 音量控制 | Volume Renderer |
| CAP／CSIP | 通用音訊 profile／協同裝置組 | CAP Acceptor 與 CSIP set member |
| LC3 | LE Audio 的標準編解碼器 | 預編譯函式庫 |

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 手機的藍牙清單看不到 `IPRO-LE-Audio` | 手機未開啟 LE Audio，或板子已與其他裝置連線 | 開啟手機的 LE Audio；這個應用同時只接受一條連線，連線期間停止廣播 |
| 重新燒錄後無法再配對 | 手機或板子保留了舊的綁定資訊 | 在主控台輸入 `leaudio_unpair` 清除綁定，並在手機上刪除此裝置後重新配對 |
| `test_tone` 沒有聲音 | 耳機插在 J2 時喇叭會關閉；放大器由 USB VBUS 供電 | 拔掉耳機或改聽耳機；以 USB-C 供電 |
| 按鍵時出現 `volume control not up yet` | VCP 尚未完成初始化 | 等開機訊息結束再按 |
| 建置在設定階段停止，訊息提到 `CONFIG_EM_SIZE` | `bt54_iso2` 需要較大的 Exchange Memory | 設定 `CONFIG_EM_SIZE=32` |

## 下一步 { #next-steps }

- [音訊與 LE Audio](../guides/audio.md)：音訊框架、DAC、PDM 與 LC3。
- [BLE 開發](../guides/ble.md)：控制器函式庫選擇與 Host 設定。
- [第一個 BLE 應用](first-ble-app.md)：在 Reef 上修改 GATT 應用並以 BLE OTA 更新。
