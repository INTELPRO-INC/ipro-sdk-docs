---
title: "IPRO AI Studio のインストール"
description: macOS と Windows に IPRO AI Studio 0.4.2 をインストールし、初回起動、カメラの許可、Studio が Reef を見つけることの確認を行います。同じプログラムに含まれる ipro-ai コマンドラインの使い方も説明します。
---

# IPRO AI Studio のインストール

このページを終えると、コンピューターには 3 つの Teach ツールを操作する IPRO AI Studio と、同じプログラムに含まれる `ipro-ai` コマンドラインが入ります。Edge AI ファームウェアが動作している IPRO7AI Reef EVK を接続すると、Studio は自動的にボードを見つけます。このページは IPRO AI Studio 0.4.2 を対象としています。インターフェースは英語で、ボタンとページ名は画面の表示どおりに太字で示します。

## 前提条件 { #prerequisites }

- Apple シリコン搭載の macOS 11 以降のコンピューター（Intel Mac は非対応）、または 64 ビット Windows（x64）。
- [GitHub の IPRO AI Studio リリース](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest)から入手したインストーラー：
    - macOS：`IPRO-AI-Studio-0.4.2.dmg`
    - Windows：`IPRO-AI-Studio-0.4.2-windows-x64.zip`
- 接続の確認用：Edge AI ファームウェアを書き込んだ IPRO7AI Reef EVK と USB-C データケーブル。ボードにまだ書き込んでいない場合は、先に Studio をインストールしてから [Edge AI ファームウェアの書き込み](firmware.md)の手順に従ってください。

Studio には必要なモデル変換ツールと書き込みツールが含まれています。Teach、Sensor、Audio の各ページを使うために、Python などのプログラムを別途用意する必要はありません。

## インストール { #install }

<div class="ipro-steps" markdown>

1. **プログラムをインストールします**

    === "macOS"

        `IPRO-AI-Studio-0.4.2.dmg` を開き、**IPRO AI Studio** を「アプリケーション」フォルダーにドラッグします。

    === "Windows"

        `IPRO-AI-Studio-0.4.2-windows-x64.zip` を、プログラムを置きたい場所（例：`C:\IPRO\`）に展開します。`ipro-ai-studio` フォルダーができ、`ipro-ai-studio.exe` がウィンドウ版のプログラム、`ipro-ai.exe` がコマンドラインです。必要な Visual C++ ランタイムも同じフォルダーにあり、ほかにインストールするものはありません。

2. **初めて起動します**

    === "macOS"

        Finder の「アプリケーション」フォルダーで **IPRO AI Studio** を右クリックして **開く** を選び、ダイアログでもう一度 **開く** をクリックします。または、ターミナルでダウンロード時の検疫属性を削除してから、通常どおり開きます：

        ```bash
        xattr -dr com.apple.quarantine "/Applications/IPRO AI Studio.app"
        ```

    === "Windows"

        `ipro-ai-studio` フォルダー内の `ipro-ai-studio.exe` をダブルクリックします。

    左側のレールには **Convert**、**Inspect**、**Verify**、**Board**、**Teach**、**Sensor**、**Audio** が並びます。最初の 4 つはモデルの変換、検査、比較のツールで、Teach ツールは最後の 3 つを使います。

3. **3 つの Teach ページを開きます**：レールをクリックするか、**Go** メニューまたはショートカットを使います。

    | ページ | ツール | ショートカット（macOS / Windows） | ファームウェアのモード |
    |---|---|---|---|
    | **Teach** | 画像認識 | Command+5 / Ctrl+5 | `image` |
    | **Sensor** | センサー認識 | Command+6 / Ctrl+6 | `sensor` |
    | **Audio** | 声紋認識 | Command+7 / Ctrl+7 | `voice` |

4. **カメラを許可します**：初めて **Teach** ページを開くと、macOS が IPRO AI Studio にカメラの使用を許可するかどうかを尋ねるので、**許可** を選びます。Teach ページは Reef の USB カメラ映像から学習用の画像を切り出すため、許可しないとカメラ映像は空のままです。

</div>

## OS の権限 { #permissions }

| 項目 | macOS | Windows |
|---|---|---|
| カメラ（Teach ページ） | 初めて Teach を開いたときに許可します。拒否した場合、Teach ページに `IPRO AI Studio is not allowed to use the camera.` と表示されます。**システム設定 → プライバシーとセキュリティ → カメラ** で IPRO AI Studio をオンにして、Studio を開き直します | **設定 → プライバシーとセキュリティ → カメラ** で、デスクトップアプリがカメラにアクセスできることを確認します |
| シリアルポート（3 ページすべて） | 権限は不要です | 権限は不要です |

ボードの USB シリアルポートを開けるプログラムは一度に 1 つだけです。Studio を使っている間は、ターミナルプログラムや 2 つ目の Studio ウィンドウなど、このポートを開いているほかのプログラムを閉じてください。これは IPRO Debug Probe のコンソールポートとは別のもので、両方を同時に開くことができます。

## Studio がボードを見つける仕組み { #board-discovery }

Teach、Sensor、Audio の各ページは自分でボードを探すので、シリアルポートを選ぶ必要はありません。Edge AI ファームウェアはモードに応じて、INTELPRO の USB VID 0x3896 の下で異なる USB デバイスとして認識され、各ページは自分に対応するデバイスだけを探します：

| ファームウェアのモード | USB デバイス名 | VID:PID | 探すページ |
|---|---|---|---|
| `image` | IPRO7 UVC Cam（USB カメラ＋シリアル） | 3896:0705 | **Teach** |
| `voice` | IPRO Reef Voice（シリアル） | 3896:0720 | **Audio** |
| `sensor` | IPRO Reef Sensor（シリアル） | 3896:0721 | **Sensor** |

- ページがボードを見つけると、上部のステータス行の **Board** に `on USB`（Teach ページ）または `ready`（Sensor ページと Audio ページ）と表示されます。
- ボードが別のモードのときは、上部のバナーにそのことが表示され（例：`The Reef is in voiceprint mode.`）、**Switch to Teach**、**Switch to Sensor**、**Switch to Audio** のいずれかのボタンが表示されます。ボタンを押すと、ボードは 3 つのモデルを保持したまま、このページのモードで再起動します（約 2 秒）。数秒以内にページが再びボードを見つけます。
- ボードのファームウェアにツールが 1 つしかない場合、ボタンを押すと `This Reef's firmware runs one Teach only.` と表示されます。Edge AI ファームウェア `ipro_reef_teach` を書き込んでください。
- 複数の Reef を接続している場合、ページはそのうちの 1 台を見つけます。迷ったら 1 台ずつ接続してください。コマンドラインでは `--port` を指定できます。

## ipro-ai コマンドライン { #cli }

`ipro-ai` コマンドラインは Studio の実行ファイルに含まれており、Studio と同じデプロイと検証のロジックを使います。スクリプトや自動化に利用できます。

=== "macOS"

    ```bash
    alias ipro-ai='"/Applications/IPRO AI Studio.app/Contents/MacOS/ipro-ai-studio" --cli'
    ipro-ai device list
    ```

    `alias` の行をシェルの起動ファイル（例：`~/.zshrc`）に追加すると、どのターミナルでも `ipro-ai` を使えます。

=== "Windows"

    ```powershell
    cd C:\IPRO\ipro-ai-studio
    .\ipro-ai.exe device list
    ```

よく使うデバイスコマンド：

| コマンド | 機能 |
|---|---|
| `ipro-ai device list` | USB 上の Teach ツールを一覧表示します：ツール、シリアルポート、VID:PID、シリアル番号 |
| `ipro-ai device info --json` | ファームウェアの名前とバージョン、プラットフォームのバージョン、使用可能なモード、現在のツールのスロットサイズとモデル |
| `ipro-ai model list --all` | 3 つのモードを順に切り替えて各モードのモデルを一覧表示し、元のモードに戻します |
| `ipro-ai deploy <package.ipkg> --switch` | パッケージのモードに切り替えてデプロイし、モデルの CRC を読み戻して確認します |

すべてのデバイスコマンドで、Reef の USB シリアルポートを指定する `--port`（省略すると USB 上の唯一のボードを使用）と、機械可読な出力を得る `--json` を使えます。人が読むメッセージは中国語です。英語のキーが必要な場合は `--json` を使ってください。全コマンドと `.ipkg` モデルパッケージの形式は、INTELPRO から入手できる IPRO7AI Reef Development Kit User Guide に記載されています。[ドキュメント](../documents/index.md)を参照してください。

## 動作確認 { #verify }

1. Studio が起動し、レールに **Teach**、**Sensor**、**Audio** があります。
2. Edge AI ファームウェアが動作している Reef を接続すると、`ipro-ai device list` に 1 台のボードが表示されます。例（`voice` モード、macOS）：

    ```text
      voice   /dev/cu.usbmodemXXXX  USB 3896:0720  <serial number>
    ```

3. `ipro-ai device info --json` の `version` に、Edge AI ファームウェアとプラットフォームのバージョンが表示されます：

    ```text
    "version": {"platform": "2.0", "proto": 2, "abi": 1, "store": 1,
                "tool": "voice", "fw": "ipro_reef_teach", "ver": "2.0.0", "chip": "IPRO7AI"},
    ```

4. ボードのモードに対応するページを開くと、ステータス行の **Board** に `on USB` または `ready` と表示されます。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| macOS で IPRO AI Studio を開けないと表示される | ダウンロードしたアプリが検疫されている | Finder で右クリックして **開く** を選ぶか、上記の `xattr` コマンドを実行します |
| Teach ページに `IPRO AI Studio is not allowed to use the camera.` と表示される | カメラの使用が拒否された | システムのカメラのプライバシー設定で IPRO AI Studio を許可し、Studio を開き直します |
| `ipro-ai device list` で IPRO デバイスが見つからない（終了コード 3） | ボードが動作していない、USB-C ケーブルが充電専用、またはボードで Edge AI ファームウェアが動作していない | データ通信対応のケーブルを使います。コンソールの起動ログを確認します。[Edge AI ファームウェアの書き込み](firmware.md)のとおりに書き込みます |
| ページに `Looking for the board…` が表示され続ける | ボードが別のモードになっている、またはほかのプログラムがシリアルポートを使用している | **Switch to …** のバナーが表示されるのを待ちます。そのポートを使っているほかのプログラムを閉じます |

その他の問題は[トラブルシューティング](troubleshooting.md)を参照してください。

## 次のステップ { #next-steps }

- [Edge AI ファームウェアの書き込み](firmware.md)：ボードにまだ書き込んでいない場合。
- [画像認識](image.md)、[声紋認識](voice.md)、[センサー認識](sensor.md)：各ツールの手順。
