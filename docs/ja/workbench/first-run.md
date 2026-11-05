---
title: "初めての実行"
description: IPRO Workbench で ipro_unit_test を使ってビルド、書き込み、モニターの流れを 1 回通し、ボードの Hello World から自分のアプリケーションを作成します。
---

# 初めての実行

SDK に付属するユニットテスト `ipro_unit_test` を使って「ビルド → 書き込み → ボードの出力を確認」の流れを 1 回通し、コンピューター、プローブ、ボードがすべて正常に動作することを確認します。その後、最初の自分のアプリケーションを作成します。最後には、IPRO7AI Reef EVK V4.0 の IPRO Monitor に `ALL TESTS PASSED`、続いて `Hello from my_app` が表示されます。

## 前提条件 { #prerequisites }

- IPRO Workbench がインストールされ、**Environment** のすべての行にチェックが付き、IPRO SDK が開いていること。[IPRO Workbench のインストール](install.md)を参照してください。
- IPRO7AI Reef EVK V4.0 が IPRO Debug Probe を介して接続され、サイドバーの **Board** にプローブとそのポートが表示されていること。[ボードを接続する](install.md#connect-board)を参照してください。

## ipro_unit_test を実行する { #unit-test }

<div class="ipro-steps" markdown>

1. **アプリケーションを選択します。** サイドバーの **Applications** で **ipro_unit_test** をクリックします（`test` カテゴリーにあります。検索ボックスに `unit` と入力しても見つかります）。

    **期待される結果**：ツールバーとステータスバーの両方に `ipro_unit_test` と表示され、IPRO Home のバナーに「Ready to run ipro_unit_test」と表示されます。

2. **ビルド、書き込み、モニターを行います。** IPRO Home で **Build, Flash and Monitor** をクリックします（macOS では `Cmd+Alt+R`、Windows では `Ctrl+Alt+R`）。アプリケーション一覧でアプリケーションをダブルクリックしても実行できます。

    **期待される結果**（この順に表示されます）：

    1. **Output** の **IPRO Build** にコンパイルの過程が表示され、最後に flash、ocram、hbnram の使用量が一覧表示されます。
    2. **IPRO Flash** に書き込みの進行状況が表示され、最後の行は `[All Success]` になります。
    3. 下に **IPRO Monitor** ターミナルが開き、ボードが再起動し、テストが終わると `ALL TESTS PASSED` が表示されます。

3. **ステータスバーと IPRO Home を確認します。**

    **期待される結果**：ステータスバーにメモリ使用量（例：`flash 36% · ocram 47% · hbnram 82%`）が表示され、IPRO Home の **Application** カードにも使用量のバーが表示されます。サイドバーの **Board** には「Runs ipro_unit_test (built …)」という行が追加されます。これは、いまビルドしたファームウェアをボードが実行していることを示します。

</div>

![ビルド後の IPRO Build の出力。flash、ocram、hbnram のメモリ使用量が表示されている](../assets/workbench/build-output.svg)

| 出力 | 内容 |
|---|---|
| **IPRO Build** | CMake の構成とコンパイル、メモリ使用量、前回のビルドからのサイズの変化 |
| **IPRO Flash** | IntelProCube による書き込みの過程。成功すると最後の行は `[All Success]` |
| **IPRO Monitor** | ボードのシリアル出力（ターミナル）。ボードに直接コマンドを入力できます |

いずれかのステップが失敗すると、IDE はそのステップで停止し、**Go to Error**、**Retry**、**Select Port** などの対処用のボタンとともに説明を表示します。よくあるメッセージについては、[トラブルシューティング](troubleshooting.md#messages)を参照してください。

!!! tip
    ビルドだけ、書き込みだけ、またはモニターを開くだけを行うには、ツールバーの個別のボタンか、次のショートカットを使用します。ビルド `Cmd+Alt+B`、書き込み `Cmd+Alt+U`、モニター `Cmd+Alt+M`（Windows では `Cmd` を `Ctrl` に置き換えます）。

## 自分のアプリケーションを作成する { #own-app }

<div class="ipro-steps" markdown>

1. **新しいアプリケーションを開始します。** **Applications** 一覧の上にある **+**（**New Application…**）か、IPRO Home の **New application from a template or an example** をクリックします。

2. **フォームに入力します。** **Start from** で **Hello World for a board** を、**Board** で **IPRO7AI Reef** を選択し、名前に `my_app` と入力します。カテゴリーは `user` のままにして、**Create** をクリックします。

    名前に使用できるのは英小文字、数字、アンダースコアだけで、先頭は英字にする必要があります。

    **期待される結果**：一覧に `user/my_app` が表示されて現在のアプリケーションになり、エディターでその `main.c` が開きます。

3. **実行します。** **Build, Flash and Monitor** をクリックします。

    **期待される結果**：IPRO Monitor に `Hello from my_app` が表示されます。

</div>

![Start from、Board、名前、カテゴリーの欄がある New IPRO Application ダイアログ](../assets/workbench/new-app.svg)

既存のサンプルから始めるには、一覧でアプリケーションを右クリックして **Copy as New Application…** を選択するか、**Start from** で **A copy of an existing application** を選択します。新しいアプリケーションは SDK の `apps/<category>/<name>` に作成されます。

## アプリケーションのコンテキストメニュー { #app-menu }

**Applications** 一覧でアプリケーションを右クリックすると、次の操作を直接実行できます。

![Applications 一覧でアプリケーションを右クリックしたときのコンテキストメニュー](../assets/workbench/app-menu.svg)

| 項目 | 用途 |
|---|---|
| **Build, Flash and Monitor** / **Build** / **Flash** / **Debug** | ツールバーと同じ |
| **Settings (Kconfig)…** / **Menuconfig** / **Open .config** | アプリケーションの設定を変更する。[アプリケーションの開発](develop.md#kconfig)を参照 |
| **Pin Configuration…** | GPIO の機能を割り当て、コードを生成する |
| **Reconfigure and Build** / **Clean** | CMake の構成をやり直してビルドする／ビルド結果を削除する |
| **Memory Map** | メモリの使われ方を確認する |
| **Partition Table** / **AI Model…** / **Power…** | [書き込みとボード](flash.md)と[テストと測定](measure.md#power)を参照 |
| **Copy as New Application…** | このアプリケーションを元に新しいアプリケーションを作成する |
| **Open Containing Folder** / **Copy Path** | フォルダーをエクスプローラー（Finder）で開く／フォルダーのパスをコピーする |

## 次のステップ { #next-steps }

- [アプリケーションの開発](develop.md)：設定（Kconfig）、ピン、ビルドエラー、メモリの使われ方。
- [書き込みとボード](flash.md)：書き込み時に IDE がチェックする内容、パーティションテーブル、AI モデル。
- [シリアルモニター](monitor.md)：フィルター、タイムスタンプ、ログ、シリアルプロッター、2 つ目のポート。
