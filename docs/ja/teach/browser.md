---
title: "ブラウザー版の画像 Teach"
description: SDK の tools/teach_web を使い、Chrome または Edge で IPRO7AI Reef EVK の画像 Teach を行います。ローカルサーバーの起動、記録、ブラウザーでの学習、Web Serial によるデプロイ、オフラインでの使用、IPRO AI Studio との違い。
---

# ブラウザー版の画像 Teach

SDK の `tools/teach_web` は、IPRO AI Studio をインストールせずに使える画像 Teach です。Chrome または Edge でローカルの Web ページを開き、Reef のカメラの前で記録し、ブラウザーで学習して、同じ USB-C ケーブルで Web Serial を使ってボードにデプロイします。流れは Studio の **Teach** ページと同じで、生成されるモデルは Studio のものとバイト単位で同一です。Windows、macOS、Linux で動作します。

## 前提条件 { #prerequisites }

- OV5640 カメラを接続し（SW7 を CAM）、Edge AI ファームウェアを書き込んで `image` モードにした IPRO7AI Reef EVK。このページからはモードを切り替えられません。ボードが別のモードの場合は、先にコンソールで `mode image` と入力するか、Studio の **Switch to Teach** を使ってください。[Edge AI ファームウェアの書き込み](firmware.md#modes)を参照してください。
- Reef の USB-C とコンピューターを接続する USB-C データケーブル。ボードへの電源供給と、映像とモデルの両方の転送に使います。
- Chrome または Edge（Web Serial に対応しています。Safari と Firefox は非対応です）。
- Python 3.8 以降。このコンピューターでページを配信するためだけに使います。
- SDK V2.2.1：`tools/teach_web/`。

## ページの起動 { #start }

<div class="ipro-steps" markdown>

1. **ローカルサーバーを起動します**。SDK のルートで実行します：

    ```bash
    python3 tools/teach_web/serve.py
    ```

    `tools/teach_web/` をこのコンピューターだけ（127.0.0.1）に向けて `http://localhost:8780` で配信し、デフォルトのブラウザーで開きます。それが Chrome や Edge でない場合は、アドレスをどちらかに貼り付けてください。カメラとシリアルポートは `localhost` または `https` のページからしか使えないため、ディスク上の `index.html` を直接開いても動作しません。

2. **カメラを許可します**：初回はブラウザーがカメラの使用を求めるので、許可します。

3. **Reef のカメラを選びます**：**Camera** メニューで **IPRO7 UVC Cam** を選びます。明るい四角がモデルの見る範囲です。

</div>

`serve.py` のオプション：別のポートを使う `--port <port>`、ブラウザーを開かない `--no-browser`、`--fetch-runtime`（[オフラインでの使用](#offline)を参照）。

## 収集、学習、デプロイ { #steps }

<div class="ipro-steps" markdown>

1. **収集します**：クラスを選択し、物体を四角の中に入れて、**Hold to record**（またはスペースキー）を数秒間押し続けます。ボードが「何もない」と答えられるよう、四角に何も入れずに記録した **BACKGROUND** クラスを残しておきます。クラスは最大 8 つです。ボードは独自のフォントで名前を描画するため、名前には A-Z と 0-9 を 15 文字まで使えます。**Review** を押して画像を確認し、不良なものにチェックを入れて **Delete selected** を押してから、**Done** を押します。

2. **学習します**：バックボーン（MobileNetV2 0.35 または MobileNetV1 0.25）を選んで **Train** を押します。1～2 秒で終わります。各クラスの画像の 4 枚に 1 枚が取り分けられて採点されます。1 回の記録の画像は互いに似ているため、このスコアは新しい場面での精度ではなく、「クラスを区別できる」ことを示すものと考えてください。

3. **ボードを接続します**：**Connect…**（または最初の **Deploy**）を押すと、ブラウザーが使用するシリアルポートを尋ねるので、**IPRO7 UVC Cam** を選びます。

4. **デプロイします**：**Deploy** を押します。ページは **Build the model**、**Send and write**、**Restart the board** を実行します。モデルを作成してラベルとともに送信し、ボードがそれを確認して書き込み、再起動します。カメラは自動的に戻ります。転送が拒否されたり中断されたりしても、ボード上の既存のモデルには影響しません。

5. **ボードで実行します**：ボードは自身の NPU で四角の中を分類し、ラベル、その信頼度、全クラスの確率を四角の横に描画します。

</div>

**Save…** と **Open…** を使うと、画像のセットを `.teach` ファイルに保存し、後で追加したり再学習したりできます。

## 動作確認 { #verify }

1. デプロイ後にカメラ映像が戻り、四角の横にクラス名と確率が表示されます。
2. 各クラスの物体を四角に入れるとそのクラスが表示され、四角が空のときは **BACKGROUND** が表示されます。
3. 同じ映像が、Studio や USB カメラを開けるほかのプログラムでも表示されます。

## オフラインでの使用 { #offline }

このページは LiteRT.js でバックボーンを実行します。ローカルコピーがない場合は jsDelivr CDN からダウンロードします。インターネットに接続していないコンピューターで使う前に、インターネットに接続したコンピューターで次のコマンドを 1 回実行してください（約 22 MB、npm の integrity ハッシュで検証されます）：

```bash
python3 tools/teach_web/serve.py --fetch-runtime
```

ランタイムは `tools/teach_web/vendor/` に保存されます。このフォルダーをオフラインのコンピューターにコピーしてください。

## Voice ページ { #voice-page }

`voice.html`（ページ上部の **Voice** タブ）は、ブラウザー版の声紋認識です。Reef を `voice` モードにして **Connect…** を押し、**IPRO Reef Voice** を選びます。その後、話者の登録（**Teach a voice**、**Record**）、**Start listening** による話者の表示、**Stranger mode** と **Thresholds** の使用ができます。処理はすべてボード上で行われ、ページはコマンドを送って返ってきたラベルを描画するだけです。各コントロールの意味は Studio の Audio ページと同じです。[声紋認識](voice.md)を参照してください。

## IPRO AI Studio との比較 { #compare }

| | ブラウザー、`tools/teach_web` | IPRO AI Studio |
|---|---|---|
| 入手先 | SDK に付属 | [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) |
| インストールするもの | Python 3.8 以降と、Chrome または Edge | Studio アプリケーション |
| OS | Windows、macOS、Linux | macOS、Windows |
| 画像認識 | あり：収集、学習、デプロイ | あり（**Teach** ページ） |
| 声紋認識 | あり（`voice.html`） | あり（**Audio** ページ） |
| センサー認識 | なし | あり（**Sensor** ページ） |
| ボードのモードの切り替え | なし。コンソールの `mode` か Studio を使用 | **Switch to …** ボタン |
| 収集した画像の保存 | `.teach` ファイル | フォルダー（クラスごとに PNG ファイルのサブフォルダー） |
| コマンドライン、`.ipkg` モデルパッケージ | なし | `ipro-ai` コマンドライン |
| インターネット | LiteRT.js のダウンロードに 1 回必要。または `--fetch-runtime` で事前に取得 | 不要 |

どちらもバイト単位で同じ画像モデルを生成します。ブラウザーで学習した分類層は、同梱のテンプレート `.inm` に直接書き込まれ、モデル変換ツールは使いません。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| `This browser has no Web Serial` | ブラウザーが Web Serial に対応していない | Chrome または Edge を使います |
| `Open this page from http://localhost` | ページをディスクから開いた | `serve.py` で起動し、`http://localhost:8780` を開きます |
| カメラの一覧に **IPRO7 UVC Cam** がない | ボードが `image` モードではない、Edge AI ファームウェアが動作していない、またはケーブルが充電専用 | コンソールで `mode image` と入力します。データ通信対応のケーブルを使います |
| デプロイ後に `The camera went away` と表示される | ボードが再起動中 | 正常です。カメラは自動的に戻ります。戻らない場合は USB-C を抜き差しします |
| macOS でどのプログラムにもカメラ映像が表示されない | ほかのプログラムがまだカメラを使用している | そのプログラムを終了し、USB-C を抜き差しします |
| `The model runtime did not load` | インターネット接続もローカルコピーもない | インターネットに接続したコンピューターで `serve.py --fetch-runtime` を実行するか、`vendor/` をコピーします |

## 次のステップ { #next-steps }

- [画像認識](image.md)：Studio の Teach ページ。コマンドラインでの学習とモデルパッケージも使えます。
- [センサー認識](sensor.md)：Studio でのみ使用できます。
