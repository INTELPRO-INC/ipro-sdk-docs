---
title: "IPRO Workbench"
description: INTELPRO が IPRO シリーズのチップ向けに提供する IDE、IPRO Workbench の概要です。機能、ウィンドウと IPRO Home、対応環境、インストールからデバッグまでの流れ、完全版マニュアルを紹介します。
---

# IPRO Workbench

IPRO Workbench は、INTELPRO が IPRO シリーズのチップ向けに提供する統合開発環境（IDE）です。1 つのウィンドウで IPRO SDK アプリケーションのビルド、ボードへの書き込み、ボードのシリアル出力の確認を行えます。さらに、C/C++ のコードナビゲーション、ピン設定、GATT 設定、メモリ解析、クラッシュ解析、ボード上でのテスト、RF・Wi-Fi スループット・消費電力の測定、そして自分でビルドと書き込みを行える AI アシスタントも備えています。

このセクションのページでは、[IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) と IPRO Debug Probe を例に説明します。各手順には、行う操作と表示される内容を記載しています。画面が一致しない場合は[トラブルシューティング](troubleshooting.md)を参照してください。IPRO6S EVK でも、ビルド、書き込み、モニターの手順は同じです。異なる点は、[IPRO6S EVK](flash.md#ipro6s)（[書き込みとボード](flash.md)のセクション）にまとめています。VS Code で作業する場合は [VS Code 拡張機能](../guides/vscode.md)を参照してください。

!!! info "提供状況"
    macOS 版と Windows 版の IPRO Workbench 0.1.1（プレビュー）は、[GitHub の IPRO Workbench リリースページ](https://github.com/INTELPRO-INC/ipro-workbench/releases/tag/v0.1.1)で公開しています。GitHub アカウントは不要です。Linux 版はまだありません。[IPRO Workbench のインストール](install.md)を参照してください。

## できること { #features }

| 機能 | 説明 |
|---|---|
| 環境の整備 | SDK、RISC-V ツールチェーン、CMake、Python、IntelProCube、ボードを自動的にチェックし、不足しているものは GitHub からワンクリックでインストールします。 |
| ビルド、書き込み、モニター | 1 つのボタンでビルド、書き込み、シリアルモニターの起動を行います。各ステップの出力は個別に表示され、いずれかのステップが失敗するとそこで停止して理由を説明します。 |
| アプリケーション管理 | SDK 内のアプリケーションをカテゴリー別に一覧表示します。ボードの Hello World や既存のサンプルから新しいアプリケーションを作成します。 |
| 設定（Kconfig） | アプリケーションの `.config` をフォームで編集し、変更したオプションだけを書き込みます。各オプションのヘルプと依存関係も表示します。 |
| ピン設定 | パッケージ図と表で各 GPIO の機能を割り当て、競合とボードの配線をチェックし、初期化コードを生成します。 |
| GATT 設定 | BLE のサービスとキャラクタリスティックをフォームで定義し、UUID、長さ、アプリケーションの設定をチェックして、GATT サービスのコードを生成します。[GATT サービスを設定する](develop.md#gatt)を参照してください。 |
| メモリ解析 | flash、ocram、hbnram を使用しているライブラリ、オブジェクトファイル、シンボルを表示します。ビルドごとのサイズの変化を比較し、メモリバジェットを設定できます。 |
| 書き込みとボード | パーティションテーブルの表示とチェック、ボードの Flash の検出、ボード上で動作しているファームウェアの確認、mfg パーティションへの AI モデルの書き込みを行います。IPRO6S EVK には専用のパーティションテーブルで書き込みます。 |
| シリアルモニター | フィルター、タイムスタンプ、保存と全ログの記録、シリアルプロッター、2 つ目のポートの同時モニターに対応します。 |
| デバッグと解析 | クラッシュアドレスをソース行に自動でデコードし、クラッシュダンプを収集・解析し、レジスターとそのフィールドを参照できます。 |
| テストと測定 | ボード上のテスト結果を **Testing** ビューに表示します。RF テスト（BLE DTM）、Wi-Fi スループット（iperf）、消費電力の波形、電池寿命の見積もりも行えます。 |
| AI アシスタント | 内蔵の IPRO AI アシスタントが、ビルド、出力の読み取り、設定、ピン、GATT サービスの変更を自分で行います。IDE の外部の AI アシスタント（Claude Code など）も、MCP を通じて同じツール群を使用できます。 |

## ウィンドウの各領域 { #window }

![IPRO Workbench のウィンドウ。ツールバー、IPRO サイドバー、エディター領域、下部パネル、ステータスバーの 5 つの領域に 1〜5 の番号が付いている](../assets/workbench/window-areas.svg)

| 番号 | 領域 | 用途 |
|---|---|---|
| 1 | ツールバー | 現在のアプリケーション、ボード、ポートと、ビルド、書き込み、モニターなどのボタンがあります。アプリケーション名やボード名をクリックすると変更できます。 |
| 2 | IPRO サイドバー | **Applications** には SDK 内のアプリケーション、**Board** にはプローブとそのポート、ボード上で動作しているファームウェア、**Environment** にはチェック結果が項目ごとに表示されます。 |
| 3 | エディター領域 | IPRO Home、ソースコード、そして設定、ピン、メモリマップ、パーティションテーブルなどのビューはすべてここに開きます。 |
| 4 | 下部パネル | **Output** の **IPRO Build**、**IPRO Flash**、**IPRO Setup** には、それぞれビルド、書き込み、インストールの過程が表示されます。**Terminal** の **IPRO Monitor** がシリアルモニターです。 |
| 5 | ステータスバー | 現在のアプリケーション、ボード、メモリ使用量を表示します。環境に不足があるときもここで知らせます。 |

## IPRO Home { #home }

IPRO Home は、SDK を開いた後にエディター領域の最初のタブとして表示されます。閉じた場合は、ツールバーの右側にある家のアイコン（**IPRO Home**）をクリックすると再び開きます。

![IPRO Home のページ。バナー、Application カード、Recent applications カード、Setup カード、Tools カードに緑の丸で 1〜5 の番号が付いている](../assets/workbench/home-tools.svg)

| 番号 | 領域 | 用途 |
|---|---|---|
| 1 | バナー | 常に「次のステップ」を表示します。SDK を開く前は SDK を開くよう促し、環境に不足があるときは環境を整えるよう促し、すべての準備ができると「&lt;application&gt; is ready to run」と **Build, Flash and Monitor** ボタンを表示します。 |
| 2 | Application | 現在のアプリケーション、ボード、ポート（クリックすると変更できます）、Settings (Kconfig)・Pins・GATT services・AI assistant (MCP) へのリンク、Build・Flash・Monitor・Debug の各ボタンがあります。ビルドの後はメモリ使用量も表示します。 |
| 3 | Recent applications | 最近使用したアプリケーションです。クリックすると、そのアプリケーションに切り替わります。ここから新しいアプリケーションを作成することもできます。 |
| 4 | Setup | 環境チェックの概要と **Check Again** があります。不足があるときは **Fix Environment** を表示します。 |
| 5 | Tools | 9 つのツールページへの入口です：Memory map、Partition table、Register reference、Serial plotter、Power、Crash dumps、RF test (DTM)、Wi-Fi throughput、AI model。それぞれに用途を説明する 1 行があり、名前をクリックするとページが開きます。 |

ツールページはすべてエディター領域に開き、共通のレイアウトになっています。上部にタイトルとそのページが対象とするアプリケーション、次にオプションとボタン、その下に結果が表示されます。同じコマンドは、IPRO メニューとコマンドパレット（`IPRO` と入力）にもあります。

## 対応環境 { #requirements }

| 項目 | 内容 |
|---|---|
| コンピューター | macOS 12 以降（Apple シリコン）、Windows 11（x64） |
| IPRO SDK | IPRO SDK 2.2.1（IPRO6S EVK には 2.2.1 以降が必要です。IPRO7 シリーズの手順は 2.2.0 でも同じです） |
| チップ | IPRO7、IPRO7AI、IPRO6S（SDK の IPRO6 アプリケーションをビルドします） |
| ボード | [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md)、[IPRO6S EVK](flash.md#ipro6s) |
| 書き込みと接続 | IPRO Debug Probe（USB）。書き込みには IntelProCube を使用します（IPRO6S EVK には 0.7.0.1 以降が必要です） |
| 表示言語 | 繁体字中国語、英語 |

## 作業の流れ { #workflow }

<div class="ipro-steps" markdown>

1. **インストールして環境を整えます。** IPRO Workbench をインストールし、**Fix Environment** で SDK とツールをインストールしたら、SDK を開き、IPRO Debug Probe を介してボードを接続します。[IPRO Workbench のインストール](install.md)を参照してください。

2. **最初のアプリケーションを実行します。** `ipro_unit_test` を選択して **Build, Flash and Monitor** をクリックし、`ALL TESTS PASSED` が表示されるのを待ちます。その後、自分のアプリケーションを作成します。[初めての実行](first-run.md)を参照してください。

3. **開発します。** フォームで設定（Kconfig）を変更し、ピンを割り当ててコードを生成し、GATT サービスを定義してコードを生成し、ビルドエラーを修正し、メモリの使われ方を確認します。[アプリケーションの開発](develop.md)を参照してください。

4. **書き込みます。** IDE のチェックを受けながら書き込み、パーティションテーブルをボードと比較し、AI モデルを mfg パーティションに書き込み、IPRO6S EVK のビルド、書き込み、モニターを行います。[書き込みとボード](flash.md)を参照してください。

5. **モニターします。** ボードのシリアル出力を表示、フィルター、タイムスタンプ付与、保存し、出力される数値をグラフにします。[シリアルモニター](monitor.md)を参照してください。

6. **デバッグと測定を行います。** クラッシュアドレスをデコードし、クラッシュダンプを収集し、レジスターを参照します。さらに、ボードテスト、RF テスト、Wi-Fi スループットのテスト、消費電力の解析を実行します。[デバッグと解析](debug.md)と[テストと測定](measure.md)を参照してください。

</div>

## 完全版マニュアル { #manual }

IPRO Workbench Operation Manual V1.2 は、IPRO Workbench 0.1.1 を対象とした PDF で、0.1.1 のリリースに添付されています。[英語版](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.1.1/IPRO-Workbench-Operation-Manual-V1.2-en.pdf)（73 ページ）と[繁体字中国語版](https://github.com/INTELPRO-INC/ipro-workbench/releases/download/v0.1.1/IPRO-Workbench-Operation-Manual-V1.2-zh-TW.pdf)（67 ページ）があります。[ドキュメント](../documents/index.md)にも掲載しています。

## このセクションのページ { #pages }

<div class="grid cards" markdown>

-   **[IPRO Workbench のインストール](install.md)**

    ---

    インストーラーのダウンロードと検証、macOS と Windows へのインストール、表示言語、開発環境の整備、SDK を開く、ボードの接続。

-   **[初めての実行](first-run.md)**

    ---

    `ipro_unit_test` のビルド、書き込み、モニター、自分のアプリケーションの作成、アプリケーションのコンテキストメニュー。

-   **[アプリケーションの開発](develop.md)**

    ---

    設定（Kconfig）、ピン設定と生成コード、GATT サービスと生成コード、ビルドとエラー、メモリマップ、サイズの変化とメモリバジェット。

-   **[書き込みとボード](flash.md)**

    ---

    書き込みとそのチェック、パーティションテーブル、ボードの Flash とファームウェアの確認、mfg への AI モデルの書き込み、IPRO6S EVK。

-   **[シリアルモニター](monitor.md)**

    ---

    モニターを開いてコマンドを入力する、フィルター、タイムスタンプ、保存と全ログ、シリアルプロッター、2 つ目のポート。

-   **[デバッグと解析](debug.md)**

    ---

    クラッシュアドレスの自動デコード、完全なコールチェーンを含むクラッシュダンプ、レジスターリファレンス。

-   **[テストと測定](measure.md)**

    ---

    Testing ビューでのボードテスト、BLE Direct Test Mode での RF テスト、iperf による Wi-Fi スループット、消費電力の波形と電池寿命の見積もり。

-   **[AI アシスタント](ai.md)**

    ---

    AI 機能の有効化、ビルドエラーの修正やクラッシュの解析の依頼、IDE の外部の AI アシスタントから MCP を通じて使用する方法。

-   **[トラブルシューティング](troubleshooting.md)**

    ---

    画面のメッセージ、ツールバーとサイドバーの状態、macOS と Windows の問題、問題を報告するときに送るもの。

-   **[ショートカット、コマンド、設定](reference.md)**

    ---

    キーボードショートカット、IPRO コマンド、`ipro.*` 設定、MCP ツール、IDE が使用するファイルとフォルダー。

</div>

## 本リリースの範囲 { #limitations }

これらのページは IPRO Workbench 0.1.1 プレビューを対象としています。本リリースには次の制限事項があります。

- インストーラーは Apple や Microsoft の署名を受けていないため、IPRO Workbench を初めて開くときやインストールするときに、オペレーティングシステムが確認を表示します（対処方法は[インストール](install.md#install)を参照してください）。
- JTAG によるデバッグはまだ利用できません。ボードがクラッシュした場合は、代わりに[デバッグと解析](debug.md)で説明しているクラッシュのデコードとクラッシュダンプを使用してください。
- 自動更新はデフォルトでオフです。新しいバージョンを入手するには、リリースページからダウンロードして再度インストールしてください。
- IPRO6 シリーズのボードは、起動時にビルド時刻とパーティションテーブルを出力しません。そのため、**Board** にはボードがどのファームウェアを実行しているかが表示されず、パーティションテーブルとボードの比較も行われません。
- Wi-Fi スループット（iperf）：ネットワーク名とパスワードにスペースを含めることはできません。また、ボードはパスワードをシリアルモニターにエコーします。
- Linux 版はまだありません。
