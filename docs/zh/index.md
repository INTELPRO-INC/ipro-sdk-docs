---
template: home.html
title: IPRO SDK
description: INTELPRO IPRO SDK 開發文件：在 IPRO7 與 IPRO7AI 上以 FreeRTOS 或 Zephyr 開發 BLE、LE Audio、AI 與影像應用。
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
    - { id: ipro7, name: IPRO7, sdk: V2.1.0, link: hardware/chips/ipro7/, desc: BLE 5.4 與 LE Audio、802.15.4、ISP 與 MJPEG 的 RISC-V 無線 SoC。 }
    - { id: ipro7ai, name: IPRO7AI, sdk: V2.1.0, link: hardware/chips/ipro7ai/, desc: IPRO7 加上 NPU 與封裝內 8 MB PSRAM，用於端側 AI 影像。 }
    - { id: ipro6s, name: IPRO6S, sdk: V2.0.1, link: hardware/chips/ipro6s/, desc: 內建 Wi-Fi 6、支援 BLE 5.4 與 BR/EDR 的 RISC-V SoC。 }
  layers:
    - name: 應用
      items:
        - { title: 範例應用, wide: true, link: examples/, chips: [ipro7, ipro7ai, ipro6s], desc: 隨附的 BLE、音訊、AI、相機與網路範例，依板卡分類。 }
        - { title: 你的應用, wide: true, link: guides/build-system/, chips: [ipro7, ipro7ai, ipro6s], desc: 以 .config 選擇元件與板卡，從範例複製一個開始。 }
    - name: 元件
      items:
        - { title: BLE Host, link: guides/ble/, chips: [ipro7, ipro7ai, ipro6s], desc: Zephyr v4.4 Bluetooth Host，以 bt_* API 開發。 }
        - { title: BLE 控制器, link: guides/ble/, chips: [ipro7, ipro7ai, ipro6s], desc: IPRO BLE 控制器預編譯函式庫，依連線數與功能選擇。 }
        - { title: LE Audio／LC3, link: guides/audio/, chips: [ipro7, ipro7ai], desc: BAP、CAP 與 LC3 編解碼，單播與廣播音訊。 }
        - { title: BR/EDR 音訊, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: A2DP、AVRCP、HFP 與 SCO 雙模藍牙音訊。 }
        - { title: AI 執行庫, link: guides/ai-npu/, chips: [ipro7ai], desc: NPU 推論執行庫與隨附模型，人形偵測與手勢分類。 }
        - { title: 相機與 ISP, link: guides/camera/, chips: [ipro7, ipro7ai], desc: DVP 相機、ISP 與硬體 MJPEG，可做 USB 網路攝影機。 }
        - { title: lwIP／mbedTLS, link: guides/networking/, chips: [ipro7, ipro7ai, ipro6s], desc: TCP/IP 協定堆疊與 TLS。 }
        - { title: Wi-Fi 6, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: IPRO6S 內建的 Wi-Fi 6。 }
        - { title: SDIO Wi-Fi 主機, link: guides/networking/, chips: [ipro7, ipro7ai], desc: 經 SDIO 接 IPRO6S，為 IPRO7 系列提供 Wi-Fi。 }
        - { title: Thread, link: guides/thread-matter/, chips: [ipro7, ipro7ai], desc: 802.15.4 與 OpenThread，在 Zephyr 下提供。 }
    - name: RTOS
      items:
        - { title: FreeRTOS, link: guides/architecture/, chips: [ipro7, ipro7ai, ipro6s], desc: 主要開發路徑，所有範例應用都以 FreeRTOS 建置。 }
        - { title: Zephyr v4.4, link: guides/zephyr/, chips: [ipro7, ipro7ai], desc: SDK 同時是 Zephyr 模組，支援 ipro7_evb 與 ipro7ai_evk。 }
    - name: BSP 與 HAL
      items:
        - { title: HAL 與驅動, link: reference/api/, chips: [ipro7, ipro7ai, ipro6s], desc: 周邊驅動與 HAL API。 }
        - { title: 板級設定, link: guides/build-system/, chips: [ipro7, ipro7ai, ipro6s], desc: 各板卡的腳位、電源與記憶體配置。 }
        - { title: 低功耗, link: guides/low-power/, chips: [ipro7, ipro7ai], desc: PDS 休眠與喚醒、保留記憶體規劃。 }
migrate_from:
  - "index.html"
---

## 選擇你的板卡 { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **IPRO7AI Reef EVK** <span class="ipro-badge">推薦</span>

    ---

    IPRO7AI 載板，相機、音訊與 SD 卡槽都在板上；卡槽也可插 IPRO6S FIN 卡擴充 Wi-Fi。

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">OV5640</span> <span class="ipro-tag">PDM 麥克風</span> <span class="ipro-tag">DAC 喇叭</span> <span class="ipro-tag">SD 卡</span>

    [板卡規格與上手](hardware/boards/reef-evk.md)

-   :material-monitor-dashboard:{ .lg } **IPRO7AI EVK**

    ---

    搭配子板的 LCD、相機、麥克風與喇叭，適合影像 AI 與人機介面開發。

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">2.4 吋 LCD</span> <span class="ipro-tag">SC101IOT</span> <span class="ipro-tag">microSD</span>

    [板卡規格](hardware/boards/ipro7ai-evk.md)

-   :material-chip:{ .lg } **IPRO7 EVB**

    ---

    IPRO7 評估板，多數 BLE、音訊與測試範例的預設板型，也是 Zephyr 的 `ipro7_evb`。

    <span class="ipro-tag">IPRO7</span> <span class="ipro-tag">BLE 範例</span> <span class="ipro-tag">Zephyr</span>

    [板卡規格](hardware/boards/ipro7-evb.md)

</div>

## 三步上手 { #quick-start }

<div class="ipro-quickstart" markdown>

<div class="ipro-steps" markdown>

1. **安裝開發環境**：Windows 使用 Online Installer 3.4.0 與 VS Code Extension 3.3.0；macOS 與 Linux 使用命令列工具鏈。[安裝說明](get-started/index.md)
2. **建置第一個應用**：在 SDK 根目錄執行 `make -C apps/platform/ipro7ai_reef_demo`，產出位於 `build/build_out/`。
3. **燒錄並開啟主控台**：以 IntelProCube 燒錄，主控台在 U6 接頭（115200 baud），輸入 `reef selftest` 檢查板上功能。[完整步驟](get-started/first-app-freertos.md)

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
<span class="ln o">[4/4] camera bus: OV5640 at 0x3C</span>
<span class="ln ok">done - keys: press any and run `btn status`</span></code></pre>
</div>

</div>

## 更多資源 { #resources }

<div class="ipro-links" markdown>

- [:material-layers-triple: **Zephyr RTOS**](guides/zephyr.md)<br>Zephyr v4.4 模組、`ipro7_evb` 與 `ipro7ai_evk` 板卡、範例
- [:material-view-grid-outline: **範例**](examples/index.md)<br>隨附應用總覽，依功能與板卡分類
- [:material-school-outline: **教學**](tutorials/index.md)<br>BLE、吞吐量與 LE Audio 的逐步教學
- [:material-code-tags: **API 參考**](reference/api.md)<br>平台、HAL、BLE 控制器與 AI 執行庫的介面
- [:material-console: **工具命令列**](reference/tools.md)<br>建置腳本、燒錄、序列埠與 OTA 工具
- [:material-help-circle-outline: **常見問題**](reference/faq.md)<br>建置、燒錄、BLE 與連網的常見問題

</div>

## V2.1.0 重點 { #whats-new }

- **Zephyr RTOS v4.4**：SDK 同時是 Zephyr 模組，支援 `ipro7_evb` 與 `ipro7ai_evk`。
- **新增 `ipro_agora_sentino`**：在 Reef 上以 Sentino 雲端 AI 進行語音對話（相較 V2.0.9 唯一新增的應用）。
- **相較 V2.0.1 共新增 7 個應用**：`ipro7ai_reef_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro_ai_link`、`ipro7_uvc_cam`、`ipro_agora_sentino`。
- **未包含**：Matter、FreeRTOS 應用的 Thread（Thread 僅於 Zephyr 提供）與模型轉換工具。完整內容見[版本資訊](reference/release-notes.md)。
