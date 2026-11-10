---
template: home.html
title: IPRO SDK
description: INTELPRO IPRO SDK 開發文件：以 IPRO7AI Reef EVK V4.0 一步步建置、燒錄與測試 BLE、LE Audio、AI、影像與 Wi-Fi（經 IPRO6S FIN 卡）應用。
hide:
  - navigation
  - toc
hero:
  release_text: "{sdk} 已於 {date} 發佈"
  release_link: reference/release-notes/
  title: "IPRO 系列晶片\u200b開發套件"
  lead: 一套架構涵蓋 IPRO7 與 IPRO6 系列：FreeRTOS 與 Zephyr、BLE 5.4 與 LE Audio、Wi-Fi 6、NPU 端側 AI 與影像處理。
  primary:
    text: 開始使用
    link: get-started/
  download_text: 下載 SDK
arch:
  chips_label: 晶片
  chip_link_text: 晶片規格
  default: ipro7ai
  chips:
    - { id: ipro7, name: IPRO7, sdk: V2.2.0, link: hardware/chips/ipro7/, desc: BLE 5.4 與 LE Audio、802.15.4、ISP 與 MJPEG 的 RISC-V 無線 SoC。 }
    - { id: ipro7ai, name: IPRO7AI, sdk: V2.2.0, link: hardware/chips/ipro7ai/, desc: IPRO7 加上 NPU 與封裝內 PSRAM；IPRO7AI Reef EVK V4.0 的主晶片。 }
    - { id: ipro6s, name: IPRO6S, sdk: V2.2.0, link: hardware/chips/ipro6s/, desc: 內建 Wi-Fi 6 的 RISC-V SoC；在 Reef 上是插在 microSD 卡座的 FIN Wi-Fi 卡。 }
  layers:
    - name: 應用
      items:
        - { title: 範例應用, link: examples/, chips: [ipro7, ipro7ai, ipro6s], desc: 隨附的 40 個應用；在 Reef 上執行的 9 個各有逐步說明。 }
        - { title: IPRO AI Teach, link: teach/, chips: [ipro7ai], desc: Reef 的 Edge AI 韌體，以 IPRO AI Studio 教會板子辨識影像、聲紋與感測訊號。 }
        - { title: 你的應用, wide: true, link: tutorials/first-own-app/, chips: [ipro7, ipro7ai, ipro6s], desc: 從 Reef 的 .config 複製一個開始，以 .config 選擇元件。 }
    - name: 元件
      items:
        - { title: BLE Host, link: guides/ble/, chips: [ipro7, ipro7ai], desc: Zephyr v4.4 Bluetooth Host，以 bt_* API 開發。 }
        - { title: BLE 控制器, link: guides/ble/, chips: [ipro7, ipro7ai], desc: IPRO BLE 控制器預編譯函式庫，依連線數與功能選擇。 }
        - { title: LE Audio／LC3, link: guides/audio/, chips: [ipro7, ipro7ai], desc: BAP、CAP 與 LC3 編解碼，單播與廣播音訊。 }
        - { title: AI 執行庫, link: guides/ai-npu/, chips: [ipro7ai], desc: NPU 推論執行庫與 Edge AI 平台：模型儲存、輸入來源與前處理。 }
        - { title: 相機與 ISP, link: guides/camera/, chips: [ipro7, ipro7ai], desc: DVP 相機、ISP 與硬體 MJPEG，可做 USB 網路攝影機。 }
        - { title: lwIP／mbedTLS, link: guides/networking/, chips: [ipro7, ipro7ai, ipro6s], desc: TCP/IP 協定堆疊與 TLS。 }
        - { title: Wi-Fi 6, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: IPRO6S 內建的 Wi-Fi 6；MAC、wpa_supplicant 與射頻為預編譯函式庫。 }
        - { title: SDIO Wi-Fi 主機, link: guides/networking/, chips: [ipro7, ipro7ai], desc: 經 SDIO 接 IPRO6S（Reef 上為 FIN 卡），為 IPRO7 系列提供 Wi-Fi。 }
        - { title: Thread, link: guides/thread-matter/, chips: [ipro7, ipro7ai], desc: 802.15.4 與 OpenThread，在 Zephyr 下提供。 }
    - name: RTOS
      items:
        - { title: FreeRTOS, link: guides/architecture/, chips: [ipro7, ipro7ai, ipro6s], desc: 主要開發路徑，所有範例應用都以 FreeRTOS 建置。 }
        - { title: Zephyr v4.4, link: guides/zephyr/, chips: [ipro7, ipro7ai], desc: SDK 同時是 Zephyr 模組，板型為 ipro7_evb 與 ipro7ai_evk（本版沒有 Reef 板型）。 }
    - name: BSP 與 HAL
      items:
        - { title: HAL 與驅動, link: reference/api/, chips: [ipro7, ipro7ai, ipro6s], desc: 周邊驅動與 HAL API。 }
        - { title: 板級設定, link: hardware/boards/reef-evk/, chips: [ipro7, ipro7ai], desc: Reef 的腳位、電源與記憶體配置，以 .config 選擇板卡。 }
        - { title: 低功耗, link: guides/low-power/, chips: [ipro7, ipro7ai], desc: PDS 休眠與喚醒、保留記憶體規劃。 }
migrate_from:
  - "index.html"
---

## 從 Reef 開始 { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **IPRO7AI Reef EVK V4.0** <span class="ipro-badge">開發板</span>

    ---

    IPRO7AI 開發板：OV5640 相機、PDM 麥克風、耳麥孔與喇叭、microSD 卡座、RGB LED 與樹莓派位置的 40-pin 排針。本站所有步驟都以這塊板為準。

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">OV5640</span> <span class="ipro-tag">PDM 麥克風</span> <span class="ipro-tag">DAC 喇叭</span> <span class="ipro-tag">microSD</span>

    [板卡規格與上手](hardware/boards/reef-evk.md)

-   :material-brain:{ .lg } **IPRO AI Teach**

    ---

    燒錄 Edge AI 韌體 `ipro_reef_teach`，在 IPRO AI Studio 中收集樣本、訓練，再把模型部署回板子：影像辨識、聲紋辨識與感測器辨識。

    <span class="ipro-tag">NPU</span> <span class="ipro-tag">影像</span> <span class="ipro-tag">聲紋</span> <span class="ipro-tag">感測器</span>

    [完整操作流程](teach/index.md)

-   :material-wifi:{ .lg } **Wi-Fi 與 RTSP**

    ---

    把 IPRO6S FIN 卡插進 microSD 卡座，經 SDIO 連上 Wi-Fi，並以 RTSP 串流相機畫面。

    <span class="ipro-tag">IPRO6S</span> <span class="ipro-tag">Wi-Fi 6</span> <span class="ipro-tag">RTSP</span>

    [逐步教學](tutorials/wifi-rtsp.md)

</div>

SDK 也包含 IPRO7 EVB、IPRO7AI EVK 與 IPRO6S EVK 的應用，列在[範例](examples/index.md#other-boards)；這些板卡的供應請洽 INTELPRO。

## 三步上手 { #quick-start }

<div class="ipro-quickstart" markdown>

<div class="ipro-steps" markdown>

1. **準備開發環境**：向 INTELPRO 取得 RISC-V 工具鏈，從 GitHub 下載 IntelProCube 0.7.0.1，安裝 CMake 3.15 以上、GNU make 與 Python 3.8 以上，再從發佈頁下載 SDK V2.2.0。[安裝說明](get-started/index.md)
2. **建置開箱韌體**：在 SDK 根目錄執行 `make -C apps/platform/ipro7ai_reef_demo`，映像在 `build/build_out/ipro7ai_reef_demo_IPRO7.bin`。
3. **燒錄並自我檢查**：按住 SW1、按一下 SW2 進入下載模式，以 IntelProCube 燒錄並確認 `[All Success]`；在 U6 主控台（115200 baud）輸入 `reef selftest`，LED、喇叭、SD 卡與相機依序通過。[完整步驟](get-started/first-app-freertos.md)

</div>

<div class="ipro-term" data-typing>
<div class="ipro-term__bar"><span></span><span></span><span></span><em>IPRO7AI Reef EVK</em></div>
<pre><code><span class="ln c"># 建置開箱韌體</span>
<span class="ln"><span class="p">$ </span><span class="cmd">make -C apps/platform/ipro7ai_reef_demo</span></span>
<span class="ln c"># 燒錄（在 IntelProCube 目錄下）</span>
<span class="ln"><span class="p">$ </span><span class="cmd">./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI ...</span></span>
<span class="ln ok">[All Success]</span>
<span class="ln c"># 重置後，U6 主控台（115200 baud）</span>
<span class="ln o">  IPRO7AI Reef carrier demo</span>
<span class="ln o">shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, ...</span>
<span class="ln"><span class="p">ipro /&gt; </span><span class="cmd">reef selftest</span></span>
<span class="ln o">[1/4] RGB LED: red, green, blue</span>
<span class="ln o">[2/4] speaker: 1 kHz, 300 ms, 20%</span>
<span class="ln o">[3/4] SD slot: empty, supply on</span>
<span class="ln o">[4/4] camera bus: __rti_name_ov5640 at 0x3C</span>
<span class="ln ok">done - keys: press any and run `btn status`</span></code></pre>
</div>

</div>

## 更多資源 { #resources }

<div class="ipro-links" markdown>

- [:material-monitor-dashboard: **IPRO Workbench**](workbench/index.md)<br>IPRO 的整合開發環境：補齊工具、建置、燒錄、序列埠監看與除錯都在同一個視窗
- [:material-brain: **IPRO AI Teach**](teach/index.md)<br>安裝 IPRO AI Studio、燒錄 Edge AI 韌體，教會 Reef 辨識影像、聲紋與感測訊號
- [:material-school-outline: **教學**](tutorials/index.md)<br>建置與燒錄、第一個自己的應用、測試、BLE、LE Audio、網路攝影機與 Wi-Fi
- [:material-view-grid-outline: **範例**](examples/index.md)<br>40 個隨附應用；Reef 上可執行的 9 個各有步驟
- [:material-code-tags: **API 參考**](reference/api/index.md)<br>平台、HAL、BLE 控制器與 AI 執行庫的介面
- [:material-console: **工具命令列**](reference/tools.md)<br>建置腳本、燒錄、序列埠、OTA 與 Teach 工具
- [:material-help-circle-outline: **常見問題**](reference/faq.md)<br>建置、燒錄、BLE 與連網的常見問題

</div>

## V2.2.0 重點 { #whats-new }

- **IPRO6S 應用回歸**：`ipro6_demo`（Wi-Fi 6 station／soft-AP 與 DTIM 省電）、`ipro6_if_wifi`（經 SDIO 或 USB 橋接到主機，也是 Reef FIN 卡的韌體）與 `ipro6_fmac`（FullMAC 韌體與 Flash 載入程式）。IPRO6S 應用只含 Wi-Fi，本版沒有 IPRO6S 藍牙。
- **Edge AI 平台 V2.0 與 `ipro_reef_teach`**：一個 Reef 韌體包含影像、聲紋與感測器三個 Teach 工具，由 IPRO AI Studio 操作；IPRO AI Studio 可從 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下載。
- **新應用 `ipro7_jpeg_decode`**：以軟體把 JPEG 解碼成 RGB565／RGB888。`ipro7ai_reef_demo` 新增 `mic usb`（USB 麥克風）與 `mic sdrec`（錄 WAV 到 SD 卡）。
- **共 40 個應用**。USB 裝置、lwIP 與 BSP 的修正見[版本資訊](reference/release-notes.md)。
