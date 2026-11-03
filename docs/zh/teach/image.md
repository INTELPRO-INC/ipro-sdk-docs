---
title: "影像辨識"
description: 以 IPRO AI Studio 的 Teach 頁教 IPRO7AI Reef EVK 認得自己的物品：切到 image 模式、確認相機、建立類別、錄製、訓練、部署，在板上看結果並補錄再訓練。
---

# 影像辨識

把物品拿到 Reef 的相機前錄幾秒、在電腦上訓練、部署到板子，之後板子的 NPU 會即時辨識畫面中央方框裡的物品，並把結果疊在相機畫面上。全程在 IPRO AI Studio 的 **Teach** 頁完成，不需要寫程式。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK 已燒錄 Edge AI 韌體，見[燒錄 Edge AI 韌體](firmware.md)。
- OV5640 相機模組：在斷電狀態下把排線插進 FPC1，並確認 SW7 在 CAM。插拔相機排線前一定先拔掉 USB-C。
- 一條可傳資料的 USB-C 線，接 Reef 的 USB-C 與電腦。
- 已安裝 IPRO AI Studio，並允許它使用相機，見[安裝 IPRO AI Studio](install.md)。

## 運作方式 { #how-it-works }

- OV5640 以 1280×720 擷取，ISP 同時產生兩路輸出：640×360 的預覽畫面壓成 MJPEG，以標準 USB 攝影機（UVC）送到電腦；畫面中央的方框縮成 128×128 送給 NPU。
- 預覽畫面中央的方框就是模型看到的範圍。Teach 頁從預覽畫面裁出同一個方框當訓練圖片。
- 模型是凍結的 MobileNet 骨幹加一個分類層，只訓練最後一層，所以在電腦的 CPU 上幾秒就完成。每一層都在 NPU 上執行。
- 部署時，Studio 經 USB 序列埠把模型與類別名稱送進板子；板子先檢查大小、CRC-32 與模型格式，確認無誤才寫入 Flash，再自動重新開機。
- 板子把辨識結果畫在方框外面，方框裡永遠保持相機的原始影像，因為 Teach 頁要從這裡裁出訓練圖片。

## 連上板子 { #connect }

<div class="ipro-steps" markdown>

1. **接上 USB-C**：電腦出現名為 **IPRO7 UVC Cam** 的相機與序列埠。沒有出現時，板子不在 `image` 模式，先做下一步。

2. **開啟 Teach 頁**：在 Studio 左側導覽列按 **Teach**（macOS 為 Command＋5，Windows 為 Ctrl＋5）。板子在別的模式時，頁面上方出現 `The Reef is in … mode.` 與 **Switch to Teach**，按下後等板子重新開機（約 2 秒）。也可以在主控台輸入 `mode image`。

3. **確認相機畫面**：**Camera** 區出現 Reef 的相機畫面，中央有綠色方框。板上還沒有影像模型時，畫面上方顯示 `IPRO AI TEACH` 與 `NO MODEL`。

4. **確認狀態**：頁面上方的狀態列 **Board** 顯示 `on USB`；**Put it on the board** 區顯示板子目前的狀態，例如 `Board found, no model on it yet.` 或 `Running 3 classes: …`。

</div>

## Teach 頁介面 { #page-layout }

| 區塊 | 說明 |
|---|---|
| 狀態列 | **Board**（`on USB` 表示找到板子）、**Crops**（已收集的圖片數）、**Held-out accuracy**（保留驗證的正確率）、**Last deploy**（上次部署花的時間） |
| **Camera** | Reef 的相機畫面。綠框是模型看到的範圍，方框外是板子疊上去的辨識結果。左下角的 **Mirror** 只左右鏡像預覽、不影響訓練，預設關閉 |
| **Hold to record** | 按住錄製目前選取的類別，每秒擷取 5 張，放開即停止；按鈕上顯示類別名稱，例如 **Hold to record CLASS 1** |
| **Classes** | 類別清單。每列有名稱、圖片數、最近的縮圖，以及 **Review**（檢視並刪除不好的圖片）、**Clear**（清掉這一類的所有圖片）、**Remove**（刪除類別；BACKGROUND 不能刪除）。上方有 **Open…**、**Save…**、**+ Add class** |
| **Train** | 骨幹網路的下拉選單與 **Train** 按鈕；下方顯示訓練結果 |
| **Put it on the board** | 板子目前跑的模型與 **Deploy** 按鈕；下方逐步顯示部署進度 |

## 建立類別並錄製 { #collect }

<div class="ipro-steps" markdown>

1. **命名類別**：清單預設有 **BACKGROUND**、**CLASS 1**、**CLASS 2**。點名稱欄位即可改名，按 **+ Add class** 增加類別，最多 8 類。名稱可用英文字母、數字、空白、底線、連字號與句點，最多 15 個字元；Studio 會轉成大寫。板子用內建的點陣字型顯示名稱，所以不支援中文。

2. **錄 BACKGROUND**：選取 **BACKGROUND**，方框內什麼都不放，按住 **Hold to record** 幾秒。這一類讓板子能回答「沒有東西」，一定要錄。

3. **錄每一類物品**：點選要錄的類別，把物品放進方框，按住 **Hold to record** 幾秒。錄製中預覽畫面的方框變成紅色，標示 `REC` 與類別名稱；類別旁的數字是這一類已收集的圖片數。

4. **檢查圖片**：每一類錄完後按 **Review**，刪掉不好的圖片，例如物品有一半在方框外的畫面。整類要重錄時按 **Clear**。

</div>

錄製要點：

- 小東西要靠近鏡頭，讓它占滿大部分的方框。
- 錄製時慢慢轉動、前後移動物品，讓模型看到不同的角度與距離。外觀或顏色相近的兩類，某些角度可能互相誤判，請在這些角度多補錄。
- 在實際使用的光線與背景下錄製。訓練時會自動為每張圖加上左右鏡像與兩種亮度變化，不必另外錄鏡像。
- 預覽畫面預設不鏡像，看到的就是相機實際拍到的方向；要像照鏡子一樣操作，勾選 **Mirror**，不影響訓練。

## 訓練 { #train }

<div class="ipro-steps" markdown>

1. **選擇骨幹網路**：在 **Train** 的下拉選單選一個（見下表）。預設是 MobileNetV2 0.35。

2. **按 Train**：訓練在電腦的 CPU 上進行，通常幾秒內完成。至少要有兩類有圖片，否則顯示 `Record at least two classes, then train.`；沒有圖片的類別會略過。

3. **看結果**：完成後顯示 `Trained in <秒數> s: <百分比> of held-out crops right`，狀態列的 **Held-out accuracy** 同步更新。

</div>

每一類每 4 張圖片中保留 1 張不參與訓練，訓練完用來評分，這就是 **Held-out accuracy**。同一次錄製的圖片彼此很像，所以這個分數只代表「這些類別分得開」，不代表換一個場景也一樣準。圖片太少、無法保留驗證資料時，顯示 `Too few crops to hold any out for checking.`。

結果出現 `<A> taken for <B> (<n>x)` 時，表示有 n 張 A 類的圖片被判成 B 類，常見原因是錄製時物品離開了方框。對這兩類按 **Review**，刪掉這些圖片後重新訓練。

| 下拉選單的選項 | 特點 | 模型大小 |
|---|---|---|
| MobileNetV2 0.35（預設） | 較準 | 461 KB |
| MobileNetV1 0.25 | 較快，模型約一半大 | 237 KB |

選單上標示的 NPU 時間為概略值；INTELPRO 以 Edge AI 韌體 2.0.0 實測，MobileNetV2 0.35 在板上 NPU 每次約 10.5 ms。

## 部署 { #deploy }

<div class="ipro-steps" markdown>

1. **確認板子**：**Put it on the board** 區找到了板子，並顯示板子目前跑的類別或 `Board found, no model on it yet.`。

2. **按 Deploy**：Studio 依序執行三個步驟並打勾：**Compile the model**（產生模型）、**Send and write**（傳送並寫入）、**Restart the board**（重新開機）。

3. **等相機回來**：板子重新開機時相機畫面會暫時消失，畫面顯示 `Deploying… the camera comes back when the board does.`，這是正常的；重新開機後相機自動回來。

4. **確認完成**：顯示 `On the board in <秒數> s` 與 `It now recognises …`，列出板子現在認得的類別。

</div>

板子在寫入前會先檢查收到的模型；被拒絕時，板上原有的模型不受影響，可以直接再部署一次。寫入途中斷電或拔線時，影像辨識只有一個分格，板上會沒有模型，相機畫面顯示 `NO MODEL: DEPLOY INTERRUPTED`，重新部署即可。

## 在板上看結果 { #run }

部署完成後，把物品放進方框，板子的 NPU 即時辨識，並把結果疊在相機畫面上：

| 位置 | 內容 |
|---|---|
| 上方 | `IPRO AI TEACH`、NPU 每次辨識的時間與每秒辨識次數 |
| 方框左側 | 得分最高的類別與它的信心度 |
| 方框右側 | 每個類別的機率；得分最高的一類以綠色顯示 |
| 下方 | 模型的類別數，例如 `3 CLASSES` |

這個畫面是 Reef 自己畫進 USB 攝影機影像的，任何能開啟 USB 攝影機的程式都看得到，不限於 Studio。

在主控台也可以確認狀態：

| 指令 | 作用 |
|---|---|
| `teach` | 模型狀態、類別清單與即時機率、NPU 速率、USB 連線狀態 |
| `teach print on`／`teach print off` | 在主控台印出每一筆結果 |
| `teach mirror on`／`teach mirror off` | 鏡像板子送出的相機畫面（預設關閉；Teach 頁需要相機的原始方向，平常請保持關閉） |
| `teach dump` | 傾印目前送給 NPU 的 128×128 輸入 |

## 確認結果 { #verify }

1. 每一類的物品放進方框時，方框左側顯示該類的名稱，右側該類的機率最高並以綠色顯示。
2. 方框空著時顯示 **BACKGROUND**。
3. 畫面下方的類別數與 Teach 頁的類別數相同。
4. 拔插 USB-C 或重新開機後，模型仍在板上：相機畫面不再顯示 `NO MODEL`，**Put it on the board** 顯示 `Running <n> classes: …`。

## 補錄與再訓練 { #iterate }

訓練分數只代表收集到的圖片分得開。請在實際場景測試，發現誤判就針對那個角度或光線補錄，再訓練、部署一次：

1. 選取誤判的類別，在誤判的角度與光線下按住 **Hold to record** 補錄；必要時按 **Review** 刪掉不好的圖片。
2. 按 **Train**。類別或圖片改變後，訓練結果區會提示 `The crops changed since training. Train again.`。
3. 按 **Deploy**。

保存與重用收集到的圖片：

- **Save…**：選一個資料夾，Studio 在裡面為每一類建一個子資料夾，存成 PNG 圖片。
- **Open…**：開啟同樣結構的資料夾（每類一個子資料夾，`.png` 或 `.jpg`），就能補錄或重新訓練，不必從頭收集。128×128 的圖片直接當訓練圖片，其他尺寸的圖片當作相機畫面，裁出中央方框。資料夾名稱就是類別名稱。
- 同一個資料夾也可以不開視窗，以命令列訓練成模型套件再部署：

    ```bash
    ipro-ai train image <資料夾> --out cups.ipkg --backbone mnv2_035
    ipro-ai deploy cups.ipkg --switch
    ```

    `--backbone` 可以是 `mnv2_035`（MobileNetV2 0.35）或 `mnv1_025`（MobileNetV1 0.25）。

## 規格 { #specs }

| 項目 | 規格 |
|---|---|
| 相機畫面（USB 攝影機） | 640×360 MJPEG，USB Full-Speed |
| 模型輸入 | 畫面中央方框（預覽畫面的 x 192–447、y 52–307），縮成 128×128 RGB |
| 類別數 | 2～8 類（含 BACKGROUND） |
| 類別名稱 | 最多 15 個字元：英文大寫、數字、空白、底線、連字號與句點 |
| 訓練方式 | 凍結的 MobileNet 骨幹，只訓練最後一層；在電腦的 CPU 上執行 |
| 模型 | MobileNetV2 0.35（461 KB，63 層全在 NPU）或 MobileNetV1 0.25（237 KB） |
| 板上 NPU 時間 | MobileNetV2 0.35 約 10.5 ms；模型載入約 0.74 秒 |
| 模型存放位置 | 影像模型分格，可放 508 KB |

## 使用建議 { #tips }

- **一定要有 BACKGROUND 類別。** 沒有它，方框空著時板子仍會從已知類別中挑一個回答。
- **影像辨識沒有「不認識」這個答案。** 沒教過的物品會被歸到最像的一類，而且信心度可能很高。會出現在畫面中的其他物品，請另外建立一個類別（例如 OTHER）並錄製。
- 方框裡的畫面才是模型看到的內容；物品只出現在方框外時不會被辨識。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| 相機清單裡沒有 **IPRO7 UVC Cam**；Studio 顯示 `No board with the Teach firmware on USB.` | 板子不在 `image` 模式、沒有 Edge AI 韌體，或 USB-C 線只能充電 | 在 Teach 頁按 **Switch to Teach** 或在主控台輸入 `mode image`；換一條可傳資料的線 |
| Camera 區一直顯示 `Looking for the IPRO7 UVC Cam…` | 同上 | 同上 |
| macOS 上 Camera 區沒有畫面，顯示相機權限訊息 | IPRO AI Studio 沒有相機權限 | 見[作業系統權限](install.md#permissions) |
| macOS 上所有程式都看不到相機畫面 | 另一個程式仍占用相機 | 關閉那個程式，再拔插 USB-C |
| 主控台反覆出現 `no camera answers` | 相機沒有接上，或 SW7 不在 CAM | 拔掉 USB-C，檢查相機排線，把 SW7 撥到 CAM |
| 相機畫面顯示 `NO MODEL: NO MODEL IN MFG` | 還沒有部署影像模型 | 訓練後按 **Deploy** |
| 相機畫面顯示 `NO MODEL: DEPLOY INTERRUPTED` | 上次部署沒有完成 | 重新部署 |
| 相機畫面顯示 `NO MODEL: WRONG MODEL` | 分格裡是別種模型 | 重新部署一次 |
| Camera 區顯示 `The board went away. Waiting for it…` | 板子正在重新開機（例如剛部署或切換模式），或 USB-C 被拔掉 | 部署後屬正常現象，相機會自己回來；沒有回來就拔插 USB-C |
| 訓練結果顯示 `<A> taken for <B>` | 錄製時物品離開了方框 | 對這兩類按 **Review**，刪除不好的圖片後重新訓練 |
| 實際使用時常把某一類誤判成另一類 | 某些角度或光線的資料不夠，或兩類外觀相近 | 在誤判的角度與光線下補錄，再訓練、部署 |
| 方框空著時也回答某個物品類別 | 沒有 BACKGROUND 類別，或 BACKGROUND 錄得太少 | 錄 BACKGROUND 後重新訓練、部署 |

其他狀況見[疑難排解](troubleshooting.md)。

## 下一步 { #next-steps }

- [聲紋辨識](voice.md)：讓同一片 Reef 認得誰在說話。
- [瀏覽器版影像 Teach](browser.md)：不安裝 Studio，在 Chrome 或 Edge 做同樣的流程。
