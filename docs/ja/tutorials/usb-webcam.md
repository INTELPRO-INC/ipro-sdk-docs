---
title: "USB ウェブカメラとじゃんけん"
description: ipro7_uvc_cam で IPRO7AI Reef EVK と OV5640 カメラをドライバー不要の USB ウェブカメラにし、続いて NPU でじゃんけんを行い、ゲームを映像に描画するビルドに切り替えます。
---

# USB ウェブカメラとじゃんけん

このチュートリアルを終えると、OV5640 カメラを取り付けた IPRO7AI Reef EVK が、USB-C ポート経由でコンピューターに USB ウェブカメラ（UVC、MJPEG）として認識されます。ドライバーのインストールは不要で、任意のカメラアプリで 1280×720 または 640×360 の映像を見られます。続いて `defconfig_reef_rps` 構成に切り替えると、ボードが NPU で手の形を認識してあなたとじゃんけんを行い、送信する映像にゲームを描画します。どちらも `apps/multimedia/ipro7_uvc_cam` アプリケーションの Reef 構成です。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK、OV5640 FLEX-24 カメラモジュール、コンピューターと接続する USB-C データケーブル（ボードへの給電と映像の伝送を兼ねます）。
- 書き込みとコンソール用に、U6 に接続した IPRO Debug Probe または 3.3 V USB-UART ケーブル（115200 8N1。配線は [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) を参照）。
- [最初の FreeRTOS アプリケーション](../get-started/first-app-freertos.md)を完了し、IntelProCube v0.6.3 のコマンドライン書き込みツール（別途入手）を用意していること。
- USB カメラを開けるアプリ：macOS の QuickTime Player、Windows の「カメラ」アプリ、または Linux の `ffplay` などの V4L2 プログラム。ホストはオペレーティングシステム内蔵の UVC ドライバーを使います。INTELPRO は macOS で動作を確認しています。

## 手順 { #steps }

<div class="ipro-steps" markdown>

1. **カメラを接続します。** まず USB-C を抜きます。OV5640 モジュールのフレキシブルケーブルを FPC1 に挿し、SW7 が CAM（カメラのピンを IPRO7AI に接続し、カメラの電源をオン）、SW8 が PWR になっていることを確認します。U6 を接続し、最後に USB-C をコンピューターに接続します。

2. **ウェブカメラ構成をビルドします。** SDK のルートから次を実行します。

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640
    ```

    出力は `apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin` です。`DEFCONFIG=` を付けずに `make` だけを実行すると別のボード（IPRO7 EVB）向けにビルドされ、Reef では動作しません。

3. **書き込みます。** SW1（BOOT）を押したまま SW2（RESET）を短く押し、SW1 を離してダウンロードモードに入ってから、IntelProCube のディレクトリから標準の 2 MB テーブルで書き込みます。

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\multimedia\ipro7_uvc_cam\build_reef_ov5640\build_out\ipro7_uvc_cam_IPRO7.bin
        ```

    出力に `[All Success]` があることを確認してください（このツールは失敗しても終了コード 0 で終了します）。この 2 つの構成は `mfg` パーティションを使いません。

4. **コンソールを開いてリセットします。** U6 のポートを 115200 ボーで開き、SW2 を短く押します。コンソールに次のように表示されます。

    ```text
    [SYS] Reset reason: <理由>
    [UVC] Starting init task...
    [OS] Starting OS Scheduler...
    [UVC] Bringing up USB UVC webcam (720p MJPEG)...
    [UVC] Streaming pipeline started
    ```

5. **コンピューターがカメラを認識していることを確認します。** ボードは USB VID/PID `0x3896`/`0x0701` の `IPRO7 UVC Cam` として現れます。

    === "macOS"

        ```bash
        system_profiler SPUSBDataType | grep -A4 "IPRO7 UVC Cam"
        ```

    === "Linux"

        ```bash
        lsusb -d 3896:0701
        ```

    === "Windows"

        デバイス マネージャーの「カメラ」の下に `IPRO7 UVC Cam` が表示されます。

6. **コンピューターで映像を見ます。**
    - macOS：QuickTime Player を開き、「ファイル」>「新規ムービー収録」を選び、録画ボタンの横のメニューで `IPRO7 UVC Cam` を選びます。
    - Windows：「カメラ」アプリを開き、`IPRO7 UVC Cam` に切り替えます。
    - Linux：

        ```bash
        ffplay -f v4l2 -input_format mjpeg -video_size 640x360 /dev/video0
        ```

    映像には 2 つのサイズがあり、コンピューター上のアプリがどちらかを選びます。1280×720（情報量の多いシーンでは約 15 fps。USB Full-Speed の帯域による制限）と 640×360（30 fps）です。

7. **センサーを調整します（任意）。** コンソールの `cam` コマンドは、OV5640 のレジスターを直接読み書きでき（レジスターアドレスとデータは 16 進数）、フレームをグリッドに分けた統計も表示できます。

    ```text
    cam rd 300a 2
    ```

    ```text
    RD 300a 56 40
    ```

    `300a` と `300b` には OV5640 のチップ ID（`0x56`、`0x40`）が入っています。`cam wr <reg> <hexbytes>` はレジスターに書き込み、`cam grid [cols rows]` は各セルの Y、U、V の平均を `GRID` と `GRIDEND` の間に表示します。書き込んだ値は、リセット後にデフォルトに戻ります。

8. **じゃんけん構成に切り替えます。** `defconfig_reef_rps` をビルドし、手順 3 と同じように書き込みます（パスは `build_reef_rps` にします）。

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps
    ```

    出力は `apps/multimedia/ipro7_uvc_cam/build_reef_rps/build_out/ipro7_uvc_cam_IPRO7.bin` です。手の形を認識するモデルはファームウェアにリンクされているため、別途書き込むモデルはありません。

9. **遊びます。** リセット後、コンピューターで `IPRO7 UVC Cam` を 640×360 で開きます。上部にスコアバー、下部にメッセージバーがあり、中央の枠が NPU の見ている領域で、認識中の手の形がリアルタイムでラベル表示されます。手を枠の中で静止させると、映像に 3、2、1 とカウントダウンが表示され、ボードがあなたの手を取り込み、自分の手をランダムに選んで、両者の手とスコアを表示します。手が枠から出ると、次のラウンドが始まります。

    コンソールで `rps` と入力すると、モデルとゲームの状態が表示されます。

    ```text
    rps
    ```

    ```text
    model   : ready, <バイト数> B from <ソース>, loaded in <ミリ秒> ms, <残り> KB heap left
    npu     : <フレーム数> frames, 0 errors, <毎秒の推論回数> fps, last <ミリ秒> ms
    now     : <現在の手> <信頼度>%  (r <%> p <%> s <%> n <%>)
    game    : round <ラウンド数>, you <勝ち数> me <負け数> draw <引き分け数>, conf >= 60%, mirror on
    ```

    | コマンド | 効果 |
    |---|---|
    | `rps go` | 枠内に手が入るのを待たずに、すぐにラウンドを開始します |
    | `rps reset` | スコアをリセットします |
    | `rps mirror on\|off` | 映像を左右反転します（デフォルトはオンで、鏡と同じ向き）。ビューアー側がプレビューを反転する場合（Photo Booth、FaceTime）は `off` を使います |
    | `rps print on\|off` | 分類器の結果をすべてコンソールに表示します |
    | `rps conf <パーセント>` | 手の形として認める信頼度（デフォルトは 60） |
    | `rps dump` | NPU が見ている 128×128 のフレームを 1 枚、`CAPBEGIN` と `CAPEND` の間に base64 で表示します（115200 ボーで約 8 秒） |

</div>

## 動作確認 { #verify }

- コンソールに `[UVC] Streaming pipeline started` と表示され、コンピューターに `IPRO7 UVC Cam`（`3896:0701`）が表示されます。
- ウェブカメラ構成：カメラアプリにライブ映像が表示され、1280×720 と 640×360 を切り替えられます。
- じゃんけん構成：映像にスコアバー、枠、リアルタイムの手の形のラベルが表示されます。枠に手を入れるとカウントダウンが始まり、`rps` の `npu` 行のフレーム数が増え続けます。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| コンピューターに `IPRO7 UVC Cam` が表示されない | 充電専用の USB-C ケーブルを使っている、または Reef 用ではないビルドを書き込んだ | データ通信対応のケーブルを使います。`build_reef_ov5640` または `build_reef_rps` のファイルを書き込んだことを確認します |
| コンソールが `Bringing up …` で止まる、または映像が黒い | カメラが正しく挿さっていない、または SW7 が CAM になっていない | USB-C を抜き、カメラケーブルを挿し直し、SW7 を CAM にしてから再度電源を入れます |
| 1280×720 でフレームレートが低い | USB Full-Speed の帯域による。情報量の多いシーンほど MJPEG フレームが大きくなる | 640×360（30 fps）を使います |
| じゃんけんの映像の左右が逆になる | ビューアー側でも映像を反転している | `rps mirror off` と入力します |
| 枠に手を入れてもカウントダウンが始まらない | 信頼度がしきい値を下回っている、または手が中央からずれている | `rps print on` で結果を確認します。照明と距離を改善します。`rps conf 50` を試します |
| 書き込みツールで `[All Success]` が表示されない | ダウンロードモードになっていない、または `--chip-variant IPRO7AI` がない | 再度ダウンロードモードに入ります。コマンドを確認します |

## 次のステップ { #next-steps }

- [IPRO AI Teach](../teach/index.md)：自分の画像で分類器を学習させ、Reef にデプロイします（`ipro_reef_teach` の画像モードは同じカメラパイプラインを使います）。
- [カメラと画像処理](../guides/camera.md)：画像パイプライン、ISP チャネル、対応センサー。
- [AI と NPU](../guides/ai-npu.md)：NPU 推論とモデル。
- [Wi-Fi と RTSP カメラストリーミング](wifi-rtsp.md)：代わりに、カメラ映像を Wi-Fi 経由の RTSP で送信します。
