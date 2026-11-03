---
title: "Teach 疑難排解"
description: IPRO AI Teach 常見狀況的原因與處理：找不到板子、模式或 USB 裝置不對、相機沒有畫面、燒錄失敗、部署被拒或中斷、看門狗重新開機，以及 ipro-ai 命令列的結束碼。
---

# Teach 疑難排解

依類別列出 IPRO AI Teach 常見的狀況。畫面與主控台上的訊息照原文列出，方便對照；每個工具頁也有該工具的疑難排解。

## 先確認這幾件事 { #checklist }

1. **USB-C 線可以傳資料。** 只能充電的線會讓板子亮燈，但電腦列舉不出任何 USB 裝置。
2. **USB-C 接在 Reef 自己的 USB-C（USB1）。** IPRO Debug Probe 的 USB 埠只提供主控台與燒錄，Teach 工具不經過它。
3. **板子跑的是 Edge AI 韌體。** 主控台的開機訊息有 `IPRO7AI Reef Teach: image, voice, sensor` 與 `mode:` 一行。
4. **板子的模式與要用的頁面相符。** `image` 對 **Teach**、`voice` 對 **Audio**、`sensor` 對 **Sensor**；不符時頁面上方會出現 **Switch to …**。
5. **沒有其他程式占用板子的 USB 序列埠。** 同一時間只能有一個程式開啟它。

## 連線與模式 { #connection }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 電腦上沒有出現 Reef 的 USB 裝置 | USB-C 線只能充電，或韌體沒有開機 | 換一條可傳資料的線；看主控台的開機訊息 |
| LED2（電源指示燈）不亮 | USB-C 沒有供電，或保險絲因過電流暫時斷開 | 換一條線或一個 USB 埠；拔掉 40-pin 排針上的擴充板後再試 |
| Studio 顯示 `The Reef is in <模式> mode.` | 板子目前在別的模式 | 按頁面上的 **Switch to …** |
| 按 **Switch to …** 後顯示 `This Reef's firmware runs one Teach only.` | 板上不是 Edge AI 韌體，而是只有單一工具的韌體 | 依[燒錄 Edge AI 韌體](firmware.md)改燒 `ipro_reef_teach` |
| 按 **Switch to …** 後顯示 `The Reef did not switch.` | 切換指令沒有完成，例如序列埠被占用 | 關閉其他開著板子序列埠的程式再按一次；或在主控台輸入 `mode <模式>` |
| 頁面找到了另一片板子 | 多片 Reef 同時接在電腦上 | 一次只接一片；命令列以 `--port` 指定 |
| 開機訊息或 `ipro-ai model list` 顯示 `install_interrupted` | 上次部署沒有完成（斷電、重置、拔線） | 重新部署 |
| 開機訊息或 `ipro-ai model list` 顯示 `crc` | 已提交的模型內容損壞 | 重新部署 |
| 開機訊息或 `ipro-ai model list` 顯示 `no_xip` | 分割區無法讀取 | 以 `partition_reef_teach.toml` 重新燒錄韌體 |
| 部署被拒，訊息含 `size` | 模型超過分格容量 | 改用較小的模型（感測器的 Medium、Small，或影像的 MobileNetV1 0.25） |

## 燒錄 { #flashing }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 燒錄工具結束了，但輸出沒有 `[All Success]` | 燒錄失敗；工具失敗時也以 0 結束 | 確認板子在下載模式、序列埠正確，再燒一次 |
| 交握成功，但 Flash ID 為 `00000000`，ErrorCode `003D` | Flash 腳位設定錯誤 | 燒錄指令加上 `--chip-variant IPRO7AI` |
| 燒錄工具回報交握失敗或打不開序列埠 | 終端機程式仍占用序列埠，或板子不在下載模式 | 關閉終端機程式；重新進入下載模式 |
| macOS 用 `utils/ipro_flash.sh` 時出現 `[Errno 83] Device error`，ErrorCode `0003` | 探針讓 Reef 進入下載模式後，它的序列埠短暫消失 | 等一兩秒，再執行一次同樣的指令 |
| macOS 上開啟序列埠後卡住沒有反應 | 用了 `/dev/tty.*` | 改用 `/dev/cu.*` |
| 主控台沒有任何輸出，`reboot_dl` 沒有作用 | 韌體當掉，shell 不在 | 用按鍵（按住 SW1、按一下 SW2、放開 SW1）或探針進入下載模式，重新燒錄 |
| 主控台看不到任何字 | 排線兩端腳序相同，或開到探針的另一個序列埠 | 改用兩端腳序對調的排線；開啟探針的「IPRO7 UART」序列埠，115200 baud |
| 燒到了另一片板子 | 多片板子同時接在電腦上，`--port` 指到別片 | 燒錄前以主控台的開機訊息確認板子；不確定時一次只接一片 |
| 改燒 Edge AI 韌體後，影像與感測器都沒有模型 | 原本的韌體使用標準分割表，模型分格的位置不同 | 正常現象；以 Studio 重新部署 |
| 用 Studio **Board** 頁的 **Flash** 燒錄後，Teach 工具不正常 | Board 頁以標準分割表寫入，沒有 mfg 酬載 | 以 IntelProCube 依[燒錄 Edge AI 韌體](firmware.md#flashing)重新燒錄 |

## 影像辨識 { #image }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 相機清單裡沒有 **IPRO7 UVC Cam**；Studio 顯示 `No board with the Teach firmware on USB.` | 板子不在 `image` 模式，或 USB-C 線只能充電 | 切到 `image` 模式；換一條可傳資料的線 |
| Teach 頁顯示 `IPRO AI Studio is not allowed to use the camera.` | macOS 拒絕過相機權限 | 「系統設定 → 隱私權與安全性 → 相機」打開 IPRO AI Studio，再重新開啟 Studio |
| Windows 上 Teach 頁沒有相機畫面 | 系統的相機隱私權設定不允許桌面應用程式 | 「設定 → 隱私權與安全性 → 相機」允許桌面應用程式存取相機 |
| macOS 上所有程式都看不到相機畫面 | 另一個程式仍占用相機 | 關閉那個程式，再拔插 USB-C |
| 主控台反覆出現 `no camera answers` | 相機沒有接上，或 SW7 不在 CAM | 拔掉 USB-C，檢查相機排線，把 SW7 撥到 CAM |
| 40-pin 排針上的部分 GPIO 沒有反應 | 這些腳經相機切換晶片，SW7 在 CAM | 使用相機時這是正常的；要用這些 GPIO 時把 SW7 撥到 GPIO（相機電源會關閉） |
| 畫面顯示 `NO MODEL: NO MODEL IN MFG` | 還沒有部署模型 | 用 Teach 頁部署 |
| 畫面顯示 `NO MODEL: DEPLOY INTERRUPTED` | 上次部署沒有完成 | 重新部署 |
| 畫面顯示 `NO MODEL: NO MFG PARTITION` | 燒錄時用的分割表沒有 mfg 分割區 | 以 `partition_reef_teach.toml` 重新燒錄韌體 |
| 畫面顯示 `NO MODEL: WRONG MODEL` | 分格裡是別種模型 | 重新部署一次 |
| 部署後 Camera 區顯示 `The board went away. Waiting for it…` | 板子正在重新開機 | 正常現象，相機會自己回來；沒有回來就拔插 USB-C |
| 訓練結果顯示 `<A> taken for <B>` | 錄製時物品離開了方框 | 對這兩類按 **Review**，刪除不好的圖片後重新訓練 |
| 實際使用時常把某一類誤判成另一類 | 某些角度或光線的資料不夠，或兩類外觀相近 | 在誤判的角度與光線下補錄，再訓練、部署 |

## 聲紋辨識 { #voice }

| 症狀 | 原因 | 處理 |
|---|---|---|
| Audio 頁顯示板子沒有聲紋模型，或主控台顯示 `NO MODEL` | 板上沒有有效的聲紋模型 | 以帶 `--mfg` 的指令重新燒錄，或以 `ipro-ai deploy` 部署聲紋模型，見[更換聲紋模型](voice.md#voice-model) |
| 打不開板子的序列埠 | 別的程式占用了板子的序列埠 | 關閉其他使用該序列埠的程式後再試 |
| 註冊失敗，原因 `Too little speech was heard` | 聽到的語音太少 | 說大聲一點或靠近一點，持續朗讀到時間結束 |
| 未註冊的人一直被標上某位已註冊者的名字 | 一般模式下名稱門檻偏低；喇叭播放的聲音尤其如此 | 開啟陌生人模式，或調高 **Name match** |
| 已註冊的人常被標成 Speaker k | 註冊時的位置、麥克風或音量和實際使用時不同，或名稱門檻太高 | 在實際位置以 Reef 的麥克風重新註冊；或稍微調低 **Name match** |
| 同一個人被拆成好幾位 Speaker | 新講者門檻太高 | 調低 **New speaker**，或替其中一位取名 |
| 沒人說話時也出現標籤 | 音樂、電視等持續聲音被當成語音 | 移除背景聲源，在安靜的環境使用 |
| 換了聲紋模型後，已註冊的人都不見了 | 聲紋與模型綁在一起 | 以新模型重新註冊 |
| 無法在主控台以中文名字註冊或取名 | 主控台只接受 ASCII 字元 | 在 Audio 頁輸入名字 |

## 感測器辨識 { #sensor }

| 症狀 | 原因 | 處理 |
|---|---|---|
| **Put it on the board** 顯示 `Connect a Reef running the Edge AI firmware to its own USB-C port.` | 找不到在 `sensor` 模式的板子 | 確認韌體與 USB-C 線；USB-C 要接在 Reef 本身的埠 |
| `Not ready to train` | 板子沒連上，或有錄音的類別不到 2 類（異常偵測模式要剛好 1 類） | 連上板子並補錄類別 |
| `too short: hold for at least one window` | 按住的時間比一個視窗還短 | 按久一點 |
| `<k> of <n> classes have no held-out data` | 有類別每次錄的時間太短，無法保留驗證資料 | 每次按住超過視窗長度的 2 倍 |
| **Import CSV…** 顯示 `<N> columns` | CSV 的欄數和資料來源的通道數不同 | 一欄一個通道、一列一個取樣點 |
| **Open…** 顯示 `Not a Sensor Teach folder` | 資料夾裡沒有 `sensor_teach.json` | 開啟由 **Save…** 存的資料夾 |
| 部署失敗：`the board did not come back with the model within 30 s` | 板子沒有在 30 秒內帶著新模型回來 | 拔插 USB-C 後確認主控台的開機訊息，再部署一次 |
| 換了資料來源後，原本訓練好的模型不能用 | 模型只適用於訓練時的資料來源 | 在新的資料來源上重新錄製與訓練 |
| 即時結果在狀態轉換時出現 `UNKNOWN` | 視窗同時含兩種狀態 | 正常現象；以連續幾次的結果判斷 |
| 異常偵測在正常的重負載下也報警 | 正常資料沒有涵蓋這種負載 | 在各種正常負載、轉速下補錄正常資料，重新訓練 |

## 執行中與看門狗 { #runtime }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 沒有操作，板子卻自己重新開機（主控台重新出現開機訊息） | 系統停住後，韌體內建的看門狗在約 5.6～8 秒內把板子重新開機；例如 NPU 執行了損毀的模型 | 板子回到原本的模式，模型都保留。重新部署驗證過的模型；記下當時的操作與主控台訊息，回報 INTELPRO |
| 想確認看門狗是否啟用 | | 主控台輸入 `watchdog` 查看狀態；`watchdog test` 停止餵狗，板子應在數秒內重新開機 |
| 部署過程中拔掉 USB-C 或重置 | 部署在提交前被中斷 | 該工具沒有模型（`install_interrupted`），重新部署即可；另外兩個工具的模型不受影響 |

## ipro-ai 命令列 { #cli }

`ipro-ai` 的裝置與模型命令以固定的結束碼回報結果，加上 `--json` 時標準輸出只有一份 JSON，`error.type` 說明錯誤種類。

| 結束碼 | 意思 | 處理 |
|---|---|---|
| `0` | 成功 | |
| `1` | 檢查不符：套件損壞、`verify` 不一致、部署後讀回的 CRC 或大小不對 | 確認板上模型的 CRC 與套件相同；重新產生套件 |
| `2` | 用法錯誤：參數、檔案讀不到、USB 上有多片板子卻沒有給 `--port` | 修正參數；以 `--port` 指定板子 |
| `3` | 找不到裝置，或序列埠在途中消失 | 確認 USB-C 線與韌體；用 `ipro-ai device list` 查看 |
| `4` | 板子拒絕（例如 `TDEP ERR crc`）或回覆看不懂 | 依回覆內容處理；重新部署 |
| `5` | 逾時：板子沒有回答，或重新開機後沒有回來 | 看主控台的開機訊息；用 `ipro-ai device list` 確認 |
| `6` | 不相容：韌體沒有這個功能（例如 Edge AI 韌體沒有回滾）、工具種類或 ABI 不合、放不下 | 依訊息改用合適的模型或命令 |
| `7` | 工具內部錯誤 | 保留 `--json` 的輸出，回報 INTELPRO |

## 回報問題 { #report }

聯絡 INTELPRO 時，請附上：

- 主控台從開機到出問題的完整訊息（IPRO Debug Probe 的「IPRO7 UART」序列埠，115200 baud）。
- `ipro-ai device info --json` 的輸出：韌體、平台版本、模式與板上模型。
- IPRO AI Studio 的版本（Windows 在 **Help** 選單、macOS 在應用程式選單的 **About IPRO AI Studio**）與作業系統。
- 操作步驟，以及畫面上顯示的訊息原文。
