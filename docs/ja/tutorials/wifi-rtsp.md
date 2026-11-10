---
title: "Wi-Fi と RTSP カメラストリーミング"
description: microSD スロットの IPRO6S FIN カード経由で IPRO7AI Reef EVK を Wi-Fi に接続し、OV5640 カメラの映像を RTSP でコンピューターにストリーミングして、ipro6s_ota で FIN カードのファームウェアを更新します。
---

# Wi-Fi と RTSP カメラストリーミング

IPRO7AI Reef EVK は FIN カードを通じてネットワークに接続します。FIN カードは microSD スロット（CARD1）に挿す IPRO6S Wi-Fi カードで、IPRO7AI と SDIO で通信します。このチュートリアルを終えると、Reef で出荷時ファームウェア `ipro7ai_reef_demo` の Wi-Fi 版（`defconfig_wifi_ipro6s`）が動作し、お使いのアクセスポイントに接続して、カメラ映像を MJPEG として RTSP で `rtsp://<IP>:8554/av0_0` から配信します。この映像を VLC または `ffplay` で視聴します。最後の手順では、`ipro6s_ota` を使って Wi-Fi 経由で FIN カードのファームウェアを更新する方法を示します。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK、IPRO6S FIN カード、OV5640 FLEX-24 カメラモジュール。
- FIN カード上の Wi-Fi ファームウェア：`defconfig_ipro6_sdio` でビルドした IPRO6S の `ipro6_if_wifi` アプリケーション（SDIO 版。手順 2 を参照）。
- U6 に接続した IPRO Debug Probe または 3.3 V USB-UART ケーブル（115200 8N1。配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照）。
- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了し、[開発環境の準備](../get-started/environment.md#intelprocube)に従って IntelProCube 0.7.0.1 のコマンドライン書き込みツールをインストールしていること。
- Wi-Fi アクセスポイント（SSID とパスフレーズ）と、同じネットワーク上にあり、VLC または `ffplay` をインストールしたコンピューター。

!!! info "FIN カードへの最初のファームウェア"
    SDK には、FIN カードのファームウェアのソースとビルド構成、および Wi-Fi 経由でファームウェアを更新する `ipro6s_ota` コマンドが含まれています。ファームウェアがまだ書き込まれていない FIN カードに書き込むには、INTELPRO にお問い合わせください。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **FIN カードとカメラを取り付けます。** まず USB-C を抜きます。JP3 を GPIO に設定し（これでスロットの電源が GPIO14 に従います。`fin cycle` でカードの電源を入れ直すにはこの設定が必要です）、FIN カードを microSD スロットに、カメラケーブルを FPC1 に挿します。SW7 が CAM、SW8 が PWR になっていることを確認し、U6 を接続して、最後に USB-C を接続します。

2. **（任意）FIN カードのファームウェアをビルドします。** カードを更新する場合（手順 10）にのみ必要です。SDK のルートから次を実行します。

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
    ```

    出力は `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin` です。この構成では、リセットから約 600 ms 後に Wi-Fi と SDIO ブリッジが自動的に起動します。FIN カード側で入力するものはなく、アソシエーションと DHCP は Reef が制御します。

3. **Reef の Wi-Fi 版をビルドします。**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    出力は `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin` です。この構成は、出荷時ファームウェアに `components/network/ipronet_host`（SDIO ホスト側）、lwIP、RTSP サーバー（ポート 8554）を追加し、容量を確保するために USB マイク（`mic usb`）を外しています。

4. **書き込みます。** SW1（BOOT）を押したまま SW2（RESET）を短く押し、SW1 を離してダウンロードモードに入ってから（出荷時ファームウェアが動作している場合は `reboot_dl` でも同じです）、IntelProCube のディレクトリから次を実行します。

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build_wifi_ipro6s\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    出力に `[All Success]` があることを確認してください（このツールは失敗しても終了コード 0 で終了します）。

5. **コンソールを開いて FIN カードを確認します。** コンソールを 115200 ボーで開き、SW2 を短く押します。起動ログの最後に、使用できるコマンドが表示されます（レベルと時刻のフィールドは省略）。

    ```text
    REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    REEF: IPRO-WiFi - `ipronet_up <ssid> <psk>`
    REEF: RTSP - `rtsp_cam on [fps]`
    ```

    `fin` と入力して、カードが挿さって電源が入っていることを確認します。

    ```text
    IPRO6S_FIN: SDIO slave in the SD slot, SD_VDD = its 3V3.
      seated : yes (DET GPIO15)
      supply : on (GPIO14, JP3 2-3 required for control)
      host   : SDH_0 on GPIO28-33, see apps/platform/ipro7_sdio_wifi
    fin cycle | fin power on|off
    ```

    （メッセージ中の「JP3 2-3」は以前のボードリビジョンでのジャンパー名で、V4.0 ボードでは JP3 = GPIO に相当します。）

6. **Wi-Fi を起動し、アクセスポイントをスキャンします。**

    ```text
    ipronet_up
    ipro6s_scan
    ipro6s_scan_last
    ```

    引数なしの `ipronet_up` は FIN カードの Wi-Fi を起動するだけで、`ipronet_start -> 0` と表示します。`ipro6s_scan` はスキャンを開始し、結果は非同期に届きます。1～2 秒後に `ipro6s_scan_last` で最新の結果を一覧表示します。

    ```text
    [ctrl] scan_last: <数> APs (on_scan_result fired <回数> times)
       0 ssid=<SSID>                           rssi=<信号強度> ch=<チャネル> auth=<セキュリティ>
    ```

7. **アクセスポイントに接続します。**

    ```text
    ipro6s_connect <SSID> <パスフレーズ>
    ```

    ```text
    [ctrl] connect '<SSID>' -> 0 (CONNECTED_IND + IP_UPDATE_IND arrive async)
    [ctrl] STA CONNECTED
    [ctrl] IP <IP アドレス> / <ネットマスク> gw <ゲートウェイ>
    ```

    起動と接続を一度に行うには、代わりにリセット直後に `ipronet_up <SSID> <パスフレーズ>` と入力します。`[ctrl] IP …` の行が表示されない場合は、`ipro6s_link_status` と入力します。`host connected=1 ip=1` と表示されれば、リンクが確立してアドレスが割り当てられています。

8. **RTSP ストリーミングを開始します。**

    ```text
    rtsp_cam on
    ```

    カメラがまだ動作していない場合は起動してから、フォーマットと URL を表示します。

    ```text
    rtsp_cam: on, <センサー> <幅>x<高さ> JPEG q<画質>, 15 fps
    rtsp_cam: rtsp://<IP アドレス>:8554/av0_0
    ```

    デフォルトは 15 fps で、`rtsp_cam on <fps>` で 1～30 を指定できます。

9. **コンピューターで視聴します。** コンピューターを同じネットワークに接続した状態で、VLC でネットワークストリームを開き（「メディア」>「ネットワークストリームを開く」）、前の手順で表示された URL を入力します。または `ffplay` を使います。

    ```bash
    ffplay rtsp://<IP アドレス>:8554/av0_0
    ```

    `rtsp_cam stats` は送信したフレーム数、JPEG の平均サイズ、エンコーダーのエラーを表示します。`rtsp_cam off` は送信を停止し（カメラは `cam stop` まで動作し続けます）、`ipronet_down` は Wi-Fi を停止します。

10. **FIN カードのファームウェアを更新します。** `ipro6s_ota` は HTTP サーバーから IPRO6S の OTA パッケージをダウンロードして FIN カードに書き込み、FIN カードの boot2 が再起動後にそれをインストールします。パッケージは IntelProCube で生成した IPRO6S パッケージ（`FW_OTA.bin.xz.ota`。512 バイトのヘッダーと XZ 圧縮された内容）です。手順 2 のビルド結果をパッケージにする手順については、INTELPRO にお問い合わせください。パッケージをコンピューター上のフォルダーに置き、そのフォルダーを HTTP で公開します。

    ```bash
    python3 -m http.server 8000
    ```

    Reef のコンソールで（Wi-Fi に接続した状態で）次のように入力します。

    ```text
    ipro6s_ota http://<コンピューターの IP>:8000/FW_OTA.bin.xz.ota
    ```

    更新全体には約 30～60 秒かかります。Reef が Wi-Fi の通信を止めてパッケージをダウンロードし、FIN カードがそれを書き込んで確認し、インストールのために再起動します。その後、Reef がカードを再度列挙して再接続します。成功すると次のように表示されます。

    ```text
    [ota] fetch <バイト数> B in <ミリ秒> ms
    [ota] RESULT OK total=<ミリ秒> …
    ```

    失敗すると `[ota] RESULT ERR rc=<コード> … phase=<フェーズ>` と表示されます。

</div>

## 動作確認 { #verify }

- `fin` に `seated : yes` と表示され、`ipro6s_scan_last` に周囲のアクセスポイントが一覧表示されます。
- 接続後、コンソールに `[ctrl] IP …` と表示され、`ipro6s_link_status` に `host connected=1 ip=1` と表示されます。
- `rtsp_cam on` で `rtsp://<IP>:8554/av0_0` と表示され、VLC または `ffplay` にライブ映像が表示され、`rtsp_cam stats` のフレーム数が増え続けます。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| `fin` に `seated : no` と表示される | カードが奥まで挿さっていない | USB-C を抜き、FIN カードを挿し直してから再度電源を入れます |
| `ipronet_start` が 0 以外を返す | FIN カードが応答しない（ファームウェアがない、SDIO 版ではない、またはカードが停止している） | JP3 を GPIO にした状態で `fin cycle` と入力してカードの電源を入れ直し、再試行します。カードで `defconfig_ipro6_sdio` でビルドした `ipro6_if_wifi` が動作していることを確認します |
| `ipro6s_scan_last` に 0 APs と表示される | スキャン結果がまだ届いていない | 1～2 秒待ってから `ipro6s_scan_last` を再実行します。必要に応じて `ipro6s_scan` を再実行します |
| `[ctrl] IP …` が表示されない | SSID かパスフレーズが正しくない、またはアクセスポイントが範囲外にある | `ipro6s_scan_last` で SSID を確認します。`ipro6s_disconnect` を実行してから、再度 `ipro6s_connect` を実行します |
| `rtsp_cam: camera gives no frames - …` | カメラがフレームを出力していない | SW7 が CAM になっていることとカメラケーブルを確認します。`cam stop` と入力してから `rtsp_cam on` を実行します |
| `rtsp_cam: no IP yet - …` | Wi-Fi にまだアドレスがない | 手順 7 を完了してから、URL を表示するために再度 `rtsp_cam on` を実行します |
| VLC で接続できない | コンピューターと Reef が別のネットワークにある、またはアクセスポイントが無線クライアントを分離している | コンピューターから `ping <IP アドレス>` が通ることを確認します。アクセスポイントのクライアント分離機能をオフにします |
| `ipro6s_ota` で `[ota] RESULT ERR … phase=fetch` と表示される | コンピューターの HTTP サーバーに到達できない、またはパスが正しくない | コンピューターのブラウザーで同じ URL を開きます。ファイアウォールを確認します |

## 次のステップ { #next-steps }

- [ネットワーク](../guides/networking.md)：`ipronet_host` API、lwIP の統合、ネットワークの設定。
- [IPRO6S](../hardware/chips/ipro6s.md)：FIN カード上の IPRO6S チップと、その他の `ipro6_if_wifi` 構成。
- [USB ウェブカメラとじゃんけん](usb-webcam.md)：代わりに、カメラ映像を USB で送信します。
- [カメラと画像処理](../guides/camera.md)：画像パイプラインとセンサーの設定。
