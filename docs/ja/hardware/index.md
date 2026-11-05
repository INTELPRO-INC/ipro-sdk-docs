---
title: "ハードウェア"
description: IPRO チップの仕様、IPRO7AI Reef EVK、ピン割り当て、電流測定
migrate_from: []
---

# ハードウェア

チップの仕様を調べる、IPRO7AI Reef EVK を配線する、ピンを割り当てる、電流を測定する、といった作業はここから始めてください。このサイトの手順とサンプルはすべて IPRO7AI Reef EVK V4.0 を対象にしています。

## チップ { #chips }

<div class="grid cards" markdown>

-   :material-chip:{ .lg } **[IPRO7](chips/ipro7.md)**

    ---

    RISC-V RV32IMAFC、LE Audio 対応の BLE 5.4、IEEE 802.15.4、ISP、ハードウェア MJPEG を備えます。本リリースでは 37 個のアプリケーションの対象チップです。

-   :material-brain:{ .lg } **[IPRO7AI](chips/ipro7ai.md)**

    ---

    NPU を有効にし、8 MB の PSRAM をパッケージに内蔵した IPRO7 のバリアントです。Reef EVK のメインチップです。

-   :material-wifi:{ .lg } **[IPRO6S](chips/ipro6s.md)**

    ---

    Wi-Fi 6 を内蔵した RISC-V SoC です。本リリースには IPRO6S の Wi-Fi アプリケーションが 3 個含まれます。Reef では microSD スロットに挿す FIN Wi-Fi カードとして使います。

</div>

## ボード { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **[IPRO7AI Reef EVK V4.0](boards/reef-evk.md)**

    ---

    IPRO7AI（QFN56）ボードです。OV5640 カメラコネクター、PDM マイク、ヘッドセットジャックとスピーカー、microSD スロット（IPRO6S FIN カードを装着可能）、RGB LED、40 ピン拡張ヘッダーを備えます。電源は USB-C からのみ供給します。

</div>

SDK には IPRO7 EVB、IPRO7AI EVK、IPRO6S EVB、IPRO7 Arduino ボード向けのアプリケーションもあります。[サンプル](../examples/index.md)を参照してください。これらのボードについては INTELPRO にお問い合わせください。

## ピンと電源 { #pinout-power }

<div class="grid cards" markdown>

-   :material-table:{ .lg } **[ピン配置と周辺機能マッピング](pinmux.md)**

    ---

    GPIO の機能選択、UART / SPI / SDIO / I2S のピン、代替機能表、Reef のデフォルトピンです。

-   :material-flash:{ .lg } **[電源と電流測定](power.md)**

    ---

    Reef の給電方法、SW8 と JP2 による IPRO7AI の電流測定、電源設計の推奨事項です。

</div>
