---
title: "AI アシスタント"
description: IPRO Workbench に内蔵された IPRO AI アシスタントについて、AI 機能を有効にする方法、ビルドエラーの修正やクラッシュの解析を依頼する方法、IDE の外部の AI アシスタントから MCP を通じて IPRO のツールを使用する方法を説明します。
---

# AI アシスタント

IPRO Workbench には IPRO AI アシスタントが内蔵されています。質問に答えるだけでなく、IDE のツールを自分で使って、ビルド、ビルド出力の読み取り、書き込み、シリアルポートの読み取り、設定、ピン、GATT サービスの変更、メモリマップとレジスターの参照、クラッシュアドレスのデコードを行えます。IDE の外部の AI アシスタント（Claude Code など）も、MCP を通じて同じツール群を使用できます。

## AI 機能を有効にする { #enable }

AI 機能はデフォルトでオフです。使用する前に、次の設定を行います。

<div class="ipro-steps" markdown>

1. **有効にします。** 設定を開き（`Cmd+,` / `Ctrl+,`）、**AI Features** を探して AI 機能をオンにします。

2. **モデルを選択します。** 同じ場所で、使用するモデル（例：Claude Code、Anthropic API キー、GitHub Copilot）を設定します。キーの入力やアカウントへのサインインはご自身で行い、ほかの人に代わりに入力させないでください。

</div>

以下のいずれかの **Ask AI…** ボタンを押したときに AI 機能がまだオフの場合、IDE はまず「AI features are off…」と表示します。**Turn On AI** を押すと有効になります。

## ビルドエラーの修正を AI に依頼する { #fix-build }

<div class="ipro-steps" markdown>

1. **依頼します。** ビルドが失敗したら、エラーの通知で **Ask AI to Fix** を押します。

    **期待される結果**：右側に AI チャットが開きます。最初のメッセージは `@IPRO` で始まり、エラーの内容が含まれています。アシスタントはビルド出力とソースコードを読んで原因を修正し、再度ビルドして、最後に何を変更したかを数文で説明します。

2. **変更を確認します。** 説明を読んだら、エディターで変更されたファイルを確認します。同意できない変更は、元に戻す（`Cmd+Z` / `Ctrl+Z`）か、バージョン管理でファイルを復元します。

</div>

`pins.yaml` または `gatt.yaml` にエラーがある場合や CMake の構成が失敗した場合も、通知の **Ask AI to Fix** で、その問題への対処をアシスタントに依頼できます。

## クラッシュの解析を AI に依頼する { #analyze-crash }

<div class="ipro-steps" markdown>

1. **直前のクラッシュについて質問します。** ボードがクラッシュまたは停止したら（シリアルモニターを開いた状態で）、IPRO メニューから **Ask AI About the Last Crash** を選択します。

    **期待される結果**：モニターの最後の数十行が添付された状態でチャットが開きます。アシスタントはコードアドレスをデコードし、その箇所のコードを読んで、原因と修正方法を説明します。

2. **クラッシュダンプを使用します。** [クラッシュダンプ](debug.md#crash-dump)を収集した場合は、**Crash Dump** ビューで **Ask AI to Explain** を押します。アシスタントは、完全なコールチェーンからクラッシュを説明します。

</div>

## IDE の外部の AI アシスタントから使用する（MCP） { #mcp }

IPRO Workbench を開いている間、このコンピューター上で MCP サーバーが提供され、Claude Code、VS Code、Cursor などの AI アシスタントが IPRO のツールを使用できます。アシスタントがビルドしたときも、出力は IDE の **IPRO Build** に表示されます。

<div class="ipro-steps" markdown>

1. **設定をコピーします。** IPRO メニューから **Connect an AI Assistant (MCP)…** を選択し（または IPRO Home の **AI assistant (MCP)** をクリックし）、使用しているアシスタントを選択します。

    **期待される結果**：「Copied the … setup. It includes the token, so keep it private.」という通知が表示されます。一覧には Claude Code、VS Code / GitHub Copilot、Cursor があります。Claude Code の場合、コピーされるのはターミナルで実行する 1 行の `claude mcp add …` コマンドです。ほかの 2 つの場合は、設定ファイル（`.vscode/mcp.json`、`~/.cursor/mcp.json`）に貼り付ける内容です。

2. **貼り付けます。** クリップボードの内容を該当する場所に貼り付けます。例えば Claude Code の場合は、そのコマンドをターミナルに貼り付けて実行し、Claude Code を起動します。

    **期待される結果**：Claude Code の MCP 一覧で `ipro` サーバーが接続済みになり、`ipro_build` や `ipro_flash` などのツールが表示されます。

3. **指示を出します。** アシスタントに指示を出します。例えば「ipro_unit_test をビルドして書き込み、シリアルポートを読んでテスト結果を教えてください」と入力します。

    **期待される結果**：IDE の **IPRO Build** と **IPRO Flash** にビルド、続いて書き込みの様子が表示され、最後にアシスタントが、合格したテストと失敗したテストの数を報告します。

</div>

!!! warning "重要"
    - MCP サーバーはこのコンピューター上でのみ提供され（`127.0.0.1`、デフォルトのポートは 41730）、すべてのリクエストにアクセストークンが必要です。
    - トークンはホームフォルダーの `.ipro-ide/mcp.json` に保存され、読み取れるのは自分のアカウントだけです。コピーした設定にはトークンが含まれているため、公開の場所に貼り付けないでください。
    - サーバーが不要な場合は、設定で `ipro.mcp.enabled` をオフにします。

MCP が提供するツールについては、[MCP ツール](reference.md#mcp-tools)を参照してください。
