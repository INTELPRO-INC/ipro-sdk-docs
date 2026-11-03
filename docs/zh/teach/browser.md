---
title: "瀏覽器版影像 Teach"
description: 以 SDK 的 tools/teach_web 在 Chrome 或 Edge 完成 IPRO7AI Reef EVK 的影像 Teach：啟動本機伺服器、錄製、在瀏覽器訓練、經 Web Serial 部署，以及離線使用與和 IPRO AI Studio 的差異。
---

# 瀏覽器版影像 Teach

SDK 的 `tools/teach_web` 是不需安裝 IPRO AI Studio 的影像 Teach：在 Chrome 或 Edge 打開一個本機網頁，對著 Reef 的相機錄製、在瀏覽器裡訓練，再經同一條 USB-C 以 Web Serial 部署到板子。流程與 Studio 的 **Teach** 頁相同，做出的模型也與 Studio 逐位元組相同。Windows、macOS、Linux 都能使用。

## 前置需求 { #prerequisites }

- IPRO7AI Reef EVK 接上 OV5640 相機（SW7 在 CAM），已燒錄 Edge AI 韌體，並在 `image` 模式。網頁不能切換模式：板子在別的模式時，先在主控台輸入 `mode image`，或用 Studio 的 **Switch to Teach**。見[燒錄 Edge AI 韌體](firmware.md#modes)。
- 一條可傳資料的 USB-C 線，接 Reef 的 USB-C 與電腦：供電，也傳送影像與模型。
- Chrome 或 Edge（有 Web Serial；Safari 與 Firefox 沒有）。
- Python 3.8 以上，只用來在本機提供網頁。
- SDK V2.2.0：`tools/teach_web/`。

## 啟動網頁 { #start }

<div class="ipro-steps" markdown>

1. **啟動本機伺服器**：在 SDK 根目錄執行：

    ```bash
    python3 tools/teach_web/serve.py
    ```

    伺服器只在本機（127.0.0.1）提供 `tools/teach_web/`，網址為 `http://localhost:8780`，並以預設瀏覽器開啟。預設瀏覽器不是 Chrome 或 Edge 時，把網址貼到其中一個。相機與序列埠只開放給 `localhost` 或 `https` 的網頁，直接從磁碟開啟 `index.html` 無法使用。

2. **允許相機**：第一次開啟時，瀏覽器詢問是否允許使用相機，請允許。

3. **選擇 Reef 的相機**：在 **Camera** 的選單選 **IPRO7 UVC Cam**。明亮的正方形就是模型看到的範圍。

</div>

`serve.py` 的選項：`--port <埠號>` 改用其他埠，`--no-browser` 不自動開啟瀏覽器，`--fetch-runtime` 見[離線使用](#offline)。

## 收集、訓練、部署 { #steps }

<div class="ipro-steps" markdown>

1. **收集**：選取一個類別，把物品放進正方形，按住 **Hold to record**（或空白鍵）幾秒。保留 **BACKGROUND** 類別，在正方形裡什麼都不放的情況下錄製，讓板子能回答「沒有東西」。最多 8 類；名稱用 A–Z、0–9，最多 15 個字元，因為板子以自己的字型顯示。按 **Review** 檢視圖片，勾選不好的圖片後按 **Delete selected**，再按 **Done**。

2. **訓練**：選擇骨幹網路（MobileNetV2 0.35 或 MobileNetV1 0.25），按 **Train**，一兩秒內完成。每一類每 4 張圖片保留 1 張評分；同一次錄製的圖片彼此很像，這個分數代表「類別分得開」，不代表換一個場景也一樣準。

3. **連接板子**：按 **Connect…**（或第一次按 **Deploy** 時），瀏覽器詢問要用哪個序列埠，選 **IPRO7 UVC Cam**。

4. **部署**：按 **Deploy**。網頁依序執行 **Build the model**、**Send and write**、**Restart the board**：產生模型、連同類別名稱送出，板子檢查並寫入後重新開機，相機會自己回來。傳送被拒絕或中斷時，板上原有的模型不受影響。

5. **在板上執行**：板子以自己的 NPU 辨識正方形裡的內容，把類別名稱、信心度與每一類的機率畫在正方形旁邊。

</div>

**Save…** 與 **Open…** 把收集的圖片存成或讀回一個 `.teach` 檔，之後可以補錄或重新訓練。

## 確認結果 { #verify }

1. 部署完成後相機畫面回來，正方形旁顯示類別名稱與機率。
2. 每一類物品放進正方形時，顯示對應的類別；正方形空著時顯示 **BACKGROUND**。
3. 同一個畫面在 Studio 或任何能開啟 USB 攝影機的程式中都看得到。

## 離線使用 { #offline }

網頁以 LiteRT.js 執行骨幹網路。沒有本機副本時，它從 jsDelivr CDN 下載。在沒有網路的電腦上使用前，先在有網路的電腦執行一次（約 22 MB，下載後以 npm 的完整性雜湊檢查）：

```bash
python3 tools/teach_web/serve.py --fetch-runtime
```

執行時庫存放在 `tools/teach_web/vendor/`；把這個資料夾一起複製到沒有網路的電腦即可。

## 聲紋頁 { #voice-page }

`voice.html`（網頁上方的 **Voice** 分頁）是瀏覽器版的聲紋辨識：Reef 在 `voice` 模式時，按 **Connect…** 選 **IPRO Reef Voice**，即可註冊講者（**Teach a voice**、**Record**）、按 **Start listening** 看誰在說話，並使用 **Stranger mode** 與 **Thresholds**。所有運算都在板上，網頁只送出指令並畫出板子回傳的標籤。各項操作的意思與 Studio 的 Audio 頁相同，見[聲紋辨識](voice.md)。

## 與 IPRO AI Studio 的差異 { #compare }

| | 瀏覽器版 `tools/teach_web` | IPRO AI Studio |
|---|---|---|
| 取得方式 | SDK 隨附 | IPRO Edge AI 套件，向 INTELPRO 索取 |
| 需要安裝 | Python 3.8 以上與 Chrome 或 Edge | Studio 應用程式 |
| 作業系統 | Windows、macOS、Linux | macOS、Windows |
| 影像辨識 | 有：收集、訓練、部署 | 有（**Teach** 頁） |
| 聲紋辨識 | 有（`voice.html`） | 有（**Audio** 頁） |
| 感測器辨識 | 沒有 | 有（**Sensor** 頁） |
| 切換板子的模式 | 沒有；以主控台 `mode` 或 Studio 切換 | **Switch to …** 按鈕 |
| 保存收集的圖片 | `.teach` 檔 | 資料夾（每類一個子資料夾的 PNG） |
| 命令列、模型套件 `.ipkg` | 沒有 | `ipro-ai` 命令列 |
| 網路 | 第一次需要下載 LiteRT.js，或事先以 `--fetch-runtime` 取得 | 不需要 |

兩者的影像模型逐位元組相同：分類層在瀏覽器中訓練後直接寫進隨附的範本 `.inm`，不需要模型轉換器。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `This browser has no Web Serial` | 瀏覽器沒有 Web Serial | 改用 Chrome 或 Edge |
| `Open this page from http://localhost` | 直接從磁碟開啟了網頁 | 以 `serve.py` 啟動，從 `http://localhost:8780` 開啟 |
| 相機清單裡沒有 **IPRO7 UVC Cam** | 板子不在 `image` 模式、沒有 Edge AI 韌體，或 USB-C 線只能充電 | 主控台輸入 `mode image`；換一條可傳資料的線 |
| 部署後顯示 `The camera went away` | 板子正在重新開機 | 正常現象，相機會自己回來；沒有回來就拔插 USB-C |
| macOS 上所有程式都看不到相機畫面 | 另一個程式仍占用相機 | 關閉那個程式，再拔插 USB-C |
| `The model runtime did not load` | 沒有網路，也沒有本機副本 | 在有網路的電腦執行 `serve.py --fetch-runtime`，或把 `vendor/` 複製過來 |

## 下一步 { #next-steps }

- [影像辨識](image.md)：Studio 的 Teach 頁，含命令列訓練與模型套件。
- [感測器辨識](sensor.md)：只能在 Studio 操作。
