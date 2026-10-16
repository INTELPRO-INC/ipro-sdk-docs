---
title: "LE Audio 入門"
description: 在 IPRO7AI Reef EVK 上執行 LE Audio unicast 耳機 ipro_le_audio_headset，與手機配對、以按鍵調整音量，並認識設定重點與 Zephyr 廣播範例。
migrate_from:
  - "tutorials.html — 教學 4"
---

# LE Audio 入門

完成本教學後，IPRO7AI Reef EVK 會執行 `ipro_le_audio_headset`：以 `IPRO-LE-Audio` 名稱廣播，與支援 LE Audio 的手機配對，提供 PACS、ASCS、VCP 等 LE Audio 服務，並把 LC3 解碼後的音訊送到板上的喇叭與耳機孔。您也會用板上按鍵調整 VCP 音量，並了解建置 LE Audio 應用需要的設定。

!!! abstract "V2.1.0 的 LE Audio"
    - FreeRTOS：`ipro_le_audio_headset`，LE Audio unicast 耳機（BAP unicast server），支援 IPRO7 EVB 與 IPRO7AI Reef EVK。
    - Zephyr：`zephyr/samples/` 下的 BIS 廣播來源、廣播接收與 unicast 耳機範例，見 [Zephyr 範例](#zephyr-samples)。
    - 獨立的 FreeRTOS BIS 廣播來源與接收應用：未包含於 V2.1.0，請洽 INTELPRO。
    - 控制器需使用 `bt54_iso2` 函式庫與 `CONFIG_EM_SIZE=32`。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK：上電前插上 JP1，以 USB-C 供電；USB 轉 UART 線接 U6（115200 8N1）。可另接耳機到 J2。
- 已完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)，並取得 IntelProCube v0.6.3 命令列燒錄工具。
- 一個可輸入指令的序列埠終端程式（見[燒錄與序列埠](../get-started/flash-and-monitor.md)）。
- 一支支援並已開啟 LE Audio 的 Android 手機。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **建置 Reef 設定**：

    ```bash
    make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef
    ```

    產出：`apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin`。這個設定以 2 MB Flash 連結（`CONFIG_IPRO7_FLASH_2M=y`）；Reef 的封裝內 Flash 容量見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#bsp)。

2. **燒錄**：讓 Reef 進入下載模式（按住 SW1、按一下 SW2、放開 SW1），再於 IntelProCube 目錄下執行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\bluetooth\le_audio\ipro_le_audio_headset\build_reef\build_out\ipro_le_audio_headset_IPRO7.bin
        ```

    確認輸出中有 `[All Success]`。

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
    依 V2.1.0 隨附的應用 README，這個應用已驗證手機連線、配對、LE Audio 服務探索與 VCP 音量控制；從手機串流音樂尚未驗證。來源端建立串流時，主控台會印出 `Stream … started (Streaming state)`，`leaudio_status` 的 `Frames Received` 會持續增加。

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

應用附有三種輸出設定：

| 設定檔 | 板卡 | 解碼後的音訊 |
|---|---|---|
| `.config`（與 `DAC.config` 相同的 DAC 輸出） | IPRO7 EVB | 晶片內建 DAC 與喇叭 |
| `UAC.config` | IPRO7 EVB | 以 48 kHz 單聲道 USB 麥克風送給電腦（USB Audio Class） |
| `defconfig_reef` | IPRO7AI Reef EVK | DAC 輸出到喇叭與 J2 耳機孔；SW3／SW4／SW5 控制音量 |

`DAC.config` 與 `UAC.config` 依檔頭說明複製成 `.config` 後做乾淨建置（見[建置與燒錄流程](build-and-flash.md#variants)）。

## LE Audio 名詞 { #concepts }

| 名詞 | 意義 | 在 `ipro_le_audio_headset` 中 |
|---|---|---|
| CIS | 連線式等時串流，一對一，用於耳機 | 接收端 |
| BIS | 廣播等時串流，一對多（Auracast） | 未使用；見 Zephyr 廣播範例 |
| BAP | 建立與管理音訊串流 | Unicast Server，2 個 sink ASE |
| PACS | 宣告支援的編解碼能力 | LC3：16／32／48 kHz、7.5／10 ms、單聲道、每幀 26–155 octets |
| ASCS | 音訊串流端點（ASE）的設定與狀態 | 啟用 |
| VCP | 音量控制 | Volume Renderer |
| CAP／CSIP | 通用音訊 profile／協同裝置組 | CAP Acceptor 與 CSIP set member |
| LC3 | LE Audio 的標準編解碼器 | 預編譯函式庫 |

## Zephyr 範例 { #zephyr-samples }

V2.1.0 的 Zephyr 移植另附三個 LE Audio 範例：BIS 廣播來源 `bap_broadcast_source`、廣播接收 `bap_broadcast_sink`，以及以 CIS 接收的 unicast 耳機 `le_audio_headset`。Zephyr 沒有 Reef 的板級定義，這些範例使用 IPRO7 EVB 與 IPRO7AI EVK。各範例的板卡、內容與建置命令見[音訊與 LE Audio](../guides/audio.md#broadcast-audio)，工作區的建立與燒錄見 [Zephyr RTOS](../guides/zephyr.md)。

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
- [Zephyr RTOS](../guides/zephyr.md)：建置與燒錄 Zephyr 範例。
