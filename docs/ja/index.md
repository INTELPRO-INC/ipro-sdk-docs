---
template: home.html
title: IPRO SDK
description: "INTELPRO IPRO SDK のドキュメント。IPRO7AI Reef EVK V4.0 で BLE、LE Audio、AI、画像処理、Wi-Fi（IPRO6S FIN カード経由）のアプリケーションを、順を追ってビルド、書き込み、テストします。"
hide:
  - navigation
  - toc
hero:
  release_text: "{sdk} を {date} にリリースしました"
  release_link: reference/release-notes/
  title: "IPRO チップ向けの​組み込み SDK"
  lead: "IPRO7 と IPRO6 の両ファミリーをひとつのアーキテクチャで。FreeRTOS と Zephyr、BLE 5.4 と LE Audio、Wi-Fi 6、NPU によるオンデバイス AI、画像処理に対応します。"
  primary:
    text: はじめる
    link: get-started/
  download_text: SDK をダウンロード
arch:
  chips_label: チップ
  chip_link_text: チップの仕様
  default: ipro7ai
  chips:
    - { id: ipro7, name: IPRO7, sdk: V2.2.0, link: hardware/chips/ipro7/, desc: "BLE 5.4 と LE Audio、802.15.4、ISP、MJPEG を備えた RISC-V ワイヤレス SoC です。" }
    - { id: ipro7ai, name: IPRO7AI, sdk: V2.2.0, link: hardware/chips/ipro7ai/, desc: "IPRO7 に NPU とパッケージ内 PSRAM を加えた SoC で、IPRO7AI Reef EVK V4.0 に搭載されています。" }
    - { id: ipro6s, name: IPRO6S, sdk: V2.2.0, link: hardware/chips/ipro6s/, desc: "Wi-Fi 6 を内蔵した RISC-V SoC です。Reef では microSD スロットに挿す FIN Wi-Fi カードとして使います。" }
  layers:
    - name: アプリ
      items:
        - { title: サンプル, link: examples/, chips: [ipro7, ipro7ai, ipro6s], desc: "同梱の 40 個のアプリケーションです。Reef で動作する 9 個には手順ページがあります。" }
        - { title: IPRO AI Teach, link: teach/, chips: [ipro7ai], desc: "Reef の Edge AI ファームウェアです。IPRO AI Studio を使って、ボードに画像、声紋、センサー信号を学習させます。" }
        - { title: 独自のアプリケーション, wide: true, link: tutorials/first-own-app/, chips: [ipro7, ipro7ai, ipro6s], desc: "Reef の .config のコピーから始め、その中でコンポーネントを選びます。" }
    - name: コンポーネント
      items:
        - { title: BLE ホスト, link: guides/ble/, chips: [ipro7, ipro7ai], desc: "Zephyr v4.4 の Bluetooth ホストで、bt_* API でプログラミングします。" }
        - { title: BLE コントローラー, link: guides/ble/, chips: [ipro7, ipro7ai], desc: "IPRO BLE コントローラーのビルド済みライブラリで、接続数と機能に応じて選びます。" }
        - { title: LE Audio / LC3, link: guides/audio/, chips: [ipro7, ipro7ai], desc: "ユニキャストとブロードキャストのオーディオに対応する BAP、CAP と LC3 コーデックです。" }
        - { title: AI ランタイム, link: guides/ai-npu/, chips: [ipro7ai], desc: "NPU 推論ランタイムと Edge AI プラットフォーム（モデルストア、入力ソース、前処理）です。" }
        - { title: カメラと ISP, link: guides/camera/, chips: [ipro7, ipro7ai], desc: "DVP カメラ、ISP、ハードウェア MJPEG で、USB ウェブカメラを構成できます。" }
        - { title: lwIP / mbedTLS, link: guides/networking/, chips: [ipro7, ipro7ai, ipro6s], desc: "TCP/IP スタックと TLS です。" }
        - { title: Wi-Fi 6, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: "IPRO6S 内蔵の Wi-Fi 6 です。MAC、wpa_supplicant、RF はビルド済みライブラリとして提供します。" }
        - { title: SDIO Wi-Fi ホスト, link: guides/networking/, chips: [ipro7, ipro7ai], desc: "SDIO で接続した IPRO6S（Reef では FIN カード）を通じて、IPRO7 ファミリーに Wi-Fi を提供します。" }
        - { title: Thread, link: guides/thread-matter/, chips: [ipro7, ipro7ai], desc: "802.15.4 と OpenThread で、Zephyr で利用できます。" }
    - name: RTOS
      items:
        - { title: FreeRTOS, link: guides/architecture/, chips: [ipro7, ipro7ai, ipro6s], desc: "主な開発プラットフォームです。すべてのサンプルアプリケーションは FreeRTOS 上でビルドします。" }
        - { title: Zephyr v4.4, link: guides/zephyr/, chips: [ipro7, ipro7ai], desc: "SDK は Zephyr モジュールでもあり、ボード ipro7_evb と ipro7ai_evk を提供します（本リリースに Reef ボードはありません）。" }
    - name: BSP と HAL
      items:
        - { title: HAL とドライバー, link: reference/api/, chips: [ipro7, ipro7ai, ipro6s], desc: "周辺機能のドライバーと HAL API です。" }
        - { title: ボード設定, link: hardware/boards/reef-evk/, chips: [ipro7, ipro7ai], desc: "Reef のピン配置、電源、メモリレイアウトです。ボードは .config で選びます。" }
        - { title: 低消費電力, link: guides/low-power/, chips: [ipro7, ipro7ai], desc: "PDS スリープとウェイクアップ、リテンションの計画です。" }
migrate_from:
  - "index.html"
---

## Reef から始める { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **IPRO7AI Reef EVK V4.0** <span class="ipro-badge">対象ボード</span>

    ---

    OV5640 カメラ、PDM マイク、ヘッドセットジャックとスピーカー、microSD スロット、RGB LED、Raspberry Pi 形式の 40 ピンヘッダーを備えた IPRO7AI 開発ボードです。このサイトの手順はすべてこのボード向けに書かれています。

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">OV5640</span> <span class="ipro-tag">PDM マイク</span> <span class="ipro-tag">DAC スピーカー</span> <span class="ipro-tag">microSD</span>

    [仕様とクイックスタート](hardware/boards/reef-evk.md)

-   :material-brain:{ .lg } **IPRO AI Teach**

    ---

    Edge AI ファームウェア `ipro_reef_teach` を書き込み、IPRO AI Studio でデータを収集して学習させ、モデルをボードに戻して配置します。画像分類、話者認識、センサー分類に対応します。

    <span class="ipro-tag">NPU</span> <span class="ipro-tag">画像</span> <span class="ipro-tag">声紋</span> <span class="ipro-tag">センサー</span>

    [全体の流れ](teach/index.md)

-   :material-wifi:{ .lg } **Wi-Fi と RTSP**

    ---

    IPRO6S FIN カードを microSD スロットに挿し、SDIO 経由で Wi-Fi に接続して、カメラ映像を RTSP で配信します。

    <span class="ipro-tag">IPRO6S</span> <span class="ipro-tag">Wi-Fi 6</span> <span class="ipro-tag">RTSP</span>

    [手順付きのチュートリアル](tutorials/wifi-rtsp.md)

</div>

SDK には IPRO7 EVB、IPRO7AI EVK、IPRO6S EVK 向けのアプリケーションも含まれており、[サンプル](examples/index.md#other-boards) に一覧があります。これらのボードについては INTELPRO にお問い合わせください。

## 3 ステップで始める { #quick-start }

<div class="ipro-quickstart" markdown>

<div class="ipro-steps" markdown>

1. **ホストの準備**：RISC-V ツールチェーンを INTELPRO から入手し、IntelProCube 0.7.0.1 を GitHub からダウンロードし、CMake 3.15 以降、GNU make、Python 3.8 以降をインストールしてから、リリースページから SDK V2.2.0 をダウンロードします。[インストール](get-started/index.md)
2. **出荷時ファームウェアのビルド**：SDK ルートで `make -C apps/platform/ipro7ai_reef_demo` を実行します。イメージは `build/build_out/ipro7ai_reef_demo_IPRO7.bin` です。
3. **書き込みとセルフテスト**：SW1 を押したまま SW2 を押してダウンロードモードに入り、IntelProCube で書き込んで `[All Success]` を確認します。U6 のコンソール（115200 baud）で `reef selftest` と入力し、LED、スピーカー、SD カード、カメラが順にチェックを通過することを確認します。[詳しい手順](get-started/first-app-freertos.md)

</div>

<div class="ipro-term" data-typing>
<div class="ipro-term__bar"><span></span><span></span><span></span><em>IPRO7AI Reef EVK</em></div>
<pre><code><span class="ln c"># 出荷時ファームウェアをビルド</span>
<span class="ln"><span class="p">$ </span><span class="cmd">make -C apps/platform/ipro7ai_reef_demo</span></span>
<span class="ln c"># 書き込み（IntelProCube のディレクトリで実行）</span>
<span class="ln"><span class="p">$ </span><span class="cmd">./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI ...</span></span>
<span class="ln ok">[All Success]</span>
<span class="ln c"># リセット後、U6 のコンソール（115200 baud）で</span>
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

## その他のリソース { #resources }

<div class="ipro-links" markdown>

- [:material-monitor-dashboard: **IPRO Workbench**](workbench/index.md)<br>IPRO の開発環境。ツールのセットアップ、ビルド、書き込み、モニター、デバッグをひとつのウィンドウで行えます
- [:material-brain: **IPRO AI Teach**](teach/index.md)<br>IPRO AI Studio をインストールし、Edge AI ファームウェアを書き込んで、Reef に画像、声紋、センサー信号を学習させます
- [:material-school-outline: **チュートリアル**](tutorials/index.md)<br>ビルドと書き込み、最初のアプリケーション、テスト、BLE、LE Audio、ウェブカメラ、Wi-Fi
- [:material-view-grid-outline: **サンプル**](examples/index.md)<br>同梱の 40 個のアプリケーション。Reef で動作する 9 個には手順があります
- [:material-code-tags: **API リファレンス**](reference/api/index.md)<br>プラットフォーム、HAL、BLE コントローラー、AI ランタイムのインターフェース
- [:material-console: **ツールのコマンドライン**](reference/tools.md)<br>ビルドスクリプト、書き込み、シリアルコンソール、OTA、Teach ツール
- [:material-help-circle-outline: **よくある質問**](reference/faq.md)<br>ビルド、書き込み、BLE、ネットワークに関するよくある質問

</div>

## V2.2.0 の新機能 { #whats-new }

- **IPRO6S アプリケーションが復活**：`ipro6_demo`（DTIM 省電力に対応した Wi-Fi 6 ステーション／ソフト AP）、`ipro6_if_wifi`（SDIO または USB でホストと接続する Wi-Fi ブリッジで、Reef の FIN カードのファームウェアでもあります）、`ipro6_fmac`（FullMAC ファームウェアとその Flash ローダー）。IPRO6S アプリケーションは Wi-Fi のみで、本リリースには IPRO6S の Bluetooth はありません。
- **Edge AI プラットフォーム V2.0 と `ipro_reef_teach`**：画像、声紋、センサーの Teach ツールをひとつにまとめた Reef 用ファームウェアで、IPRO AI Studio から操作します。IPRO AI Studio は [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) からダウンロードできます。
- **新しい `ipro7_jpeg_decode`**：ソフトウェアで JPEG を RGB565 / RGB888 にデコードします。`ipro7ai_reef_demo` には `mic usb`（USB マイク）と `mic sdrec`（SD カードへの WAV 録音）が加わりました。
- **40 個のアプリケーション**。USB デバイス、lwIP、BSP の修正については [リリースノート](reference/release-notes.md) を参照してください。
