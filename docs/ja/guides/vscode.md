---
title: "VS Code Extension"
description: SDK V2.2.0 で使う IPRO SDK Extension 3.3.0 — SDK ルートの設定、ビルド、IPRO7AI Reef EVK への書き込み、シリアルモニター、メモリ解析、コマンド
migrate_from:
  - "vscode-extension.html"
not_migrated:
  - "vscode-extension.html#installation — installation steps live in get-started/windows.md"
  - "vscode-extension.html#cli-tools — the IntelProCube command line belongs on the flashing page"
---

# VS Code Extension

IPRO SDK Extension 3.3.0（識別子 `ipro.ipro-sdk-extension`）は、FreeRTOS のプロジェクトの閲覧、CMake によるビルド、IntelProCube による書き込み、シリアルコンソール、メモリ解析を VS Code 1.102 以降に提供します。SDK パッケージには含まれず、SDK とも、これをインストールする IPRO SDK Online Setup とも別にバージョン管理されています。インストール方法は [Windows のセットアップと VS Code](../get-started/windows.md) を参照してください。

!!! abstract "要点"
    - Online Setup 3.6.0 は SDK V2.2.0、Extension、各種ツールを一度にインストールします。Full environment でインストールした環境は、そのままビルドできます。
    - Windows のツールチェーンは Online Setup がインストールする GCC 13.1.1 で、SDK はこれに合わせて用意されています。Extension が同じインストール先のコンパイラーを使っていることを Diagnostics で確認してください。
    - IPRO7AI Reef EVK では、チップバリアント `IPRO7AI` と、アプリケーションが使うパーティションテーブルで書き込みます。boot2 のイメージと `mfg` ペイロードは IntelProCube のコマンドラインで書き込みます。
    - コンソールのボーレート（`ipro.monitorBaudRate`）は書き込みのボーレート（`ipro.baudRate`）とは別の設定です。
    - ソースレベル（F5）のデバッグはできません。OpenOCD をインストールしても GDB のデバッグアダプターは設定されません。

## 機能 { #features }

| 機能 | 内容 |
|---|---|
| プロジェクト | アプリケーションをカテゴリー別に閲覧し、ピン留めし、アクティブなプロジェクトを切り替えます（`IPRO: Go to Project…`、`IPRO: Select Project`） |
| Build / Batch Build | Make または Ninja による CMake の構成（`ipro.generator`）、debug / release / size のプロファイル、Problems からソースへのジャンプ |
| 設定 | `IPRO Config: Menuconfig`、`IPRO Config: Open .config`、`IPRO Config: Load Defconfig` |
| Flash / Monitor | IntelProCube による書き込み。独自のボーレートを持つ内蔵のシリアルコンソール |
| Analysis / Debug | Memory Map、Decode Crash Report、Pin Function Lookup。Register Explorer には互換性のある CCI 接続が必要です |

SDK のビルドは `.config` をそのまま読み込み、Kconfig の `select` や `depends on` を解決しません。Menuconfig で編集した後は、依存するオプションが `.config` に書き込まれていることを確認してください。[ビルドシステムと設定](build-system.md#configuration)を参照してください。

## SDK V2.2.0 を使う { #sdk-2-2-0 }

<div class="ipro-steps" markdown>

1. Online Setup でインストールします。新しい環境では、[Windows のセットアップと VS Code](../get-started/windows.md#online-setup) のとおりに **Full environment** を選びます。既存の環境に SDK V2.2.0 を追加する場合は、[SDK またはツールチェーンだけをインストールする](../get-started/windows.md#components)のとおりに **SDK only** を選びます。
2. **File → Open Folder…** で `<install dir>\sdk\IPRO-SDK-V2.2.0` を開きます（`CMakeLists.txt`、`apps`、`bsp` を含むフォルダーです）。インストール時に設定タスクにチェックを入れなかった場合は、このフォルダーに対して `IPRO Setup: Set SDK Root` を実行します。
3. `IPRO Setup: Run Diagnostics` を実行し、SDK ルート、コンパイラー、CMake、Ninja、Python、書き込みツールがすべて同じインストール先を指していることを確認します。コンパイラーは `<install dir>\toolchain\riscv_ipro7_win32` の GCC 13.1.1 です。別のツールチェーンを使う場合は、`ipro.toolchainPath`（`riscv64-unknown-elf-` で終わるコンパイラーのプレフィックス）を設定します。

</div>

- V2.2.0 をビルドしてボードで動作を確認するまで、以前の SDK のディレクトリは残しておいてください。古い `build/` ディレクトリ、CMake キャッシュ、`.vscode` フォルダーを新しい SDK にコピーしないでください。
- ワークスペースの設定（`.vscode/settings.json`）はユーザー設定を上書きできます。実際に使われるのは Diagnostics が表示するパスです。

## Control Center { #control-center }

F1 を押して `IPRO: Open Control Center` を実行すると、現在の SDK、プロジェクト、接続とよく使う操作が 1 つのパネルに表示されます。続いて `IPRO Setup: Run Diagnostics` でツールのパスを確認します。VS Code の Settings で `ipro` を検索して設定を探すこともできます。

## 最初のビルド { #workflow }

<div class="ipro-steps" markdown>

1. `IPRO: Go to Project…` を実行し、platform カテゴリーの `ipro7ai_reef_demo` を選びます。
2. `IPRO Config: Select Build Profile` を実行し、debug、release、size のいずれかを選びます。
3. `IPRO: Build` を実行し、Terminal を確認します。Problems に表示されたエラーからソースにジャンプできます。ビルドの成功は、CMake が `Configuring done` を出力したことではなく、終了コード 0 で終わりイメージが存在することで判断します。
4. `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin` が生成されたことを確認します。

</div>

`IPRO: Batch Build` は、選択した複数のプロジェクトを一度にビルドします。SDK やツールのパスを変更した後は、古いキャッシュが再利用されないよう `IPRO: Clean` を実行してからビルドし直してください。

ほとんどの Reef 向けアプリケーションは、Reef 用の設定を別ファイル（`defconfig_reef`、`defconfig_reef_ov5640` など）として同梱しています。そのままで Reef 向けのビルドになるのは `ipro7ai_reef_demo`、`ipro_reef_teach`、`ipro_agora_sentino` だけです。コマンドラインでの指定方法 `make -C <app> DEFCONFIG=<file>` と Reef 向け設定の一覧は、[ビルドシステムと設定](build-system.md#variants)に記載しています。

## 書き込みとコンソール { #flash }

<div class="ipro-steps" markdown>

1. `IPRO Setup: Select Flash Tool` で IntelProCube を選ぶか、`ipro.flashToolPath` にそのフォルダーを設定します。
2. ボードを接続し（SW7 を CAM、SW8 を PWR にし、U6 にコンソールケーブル、USB-C を接続）、`IPRO: Select Serial Port` を実行してコンソールのポートを選びます。IPRO Debug Probe を使う場合は、その UART ポートを選びます。CCI ポートはレジスターアクセス用で、コンソールや書き込みには使えません。
3. `IPRO Config: Configure Flash…` で、チップバリアントを `IPRO7AI` に、パーティションテーブルをアプリケーションが使うものに設定します。`ipro7ai_reef_demo` と `ipro7_uvc_cam` のウェブカメラでは `partition_cfg_2M.toml` です。独自のテーブルを使うアプリケーションは、[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md#partition-tables)に一覧があります。
4. Reef をダウンロードモードにします。SW1（BOOT）を押したまま SW2（RESET）を押して離し、SW1 を離します。続いて `IPRO: Flash` を実行し、ツールの結果を確認します。事前に、ポートを使用しているほかのプログラムを閉じておいてください。
5. SW2 を押してファームウェアを起動します。`ipro.monitorBaudRate` がファームウェアと一致していることを確認し（`IPRO Config: Set Monitor Baud Rate`）、`IPRO: Serial Monitor` を実行します。ボーレートを変える場合は、先に `IPRO: Close Serial Monitor` を実行してからボーレートを設定し、モニターを開き直します。

</div>

| 設定 | 意味 |
|---|---|
| `ipro.baudRate` | 書き込みのボーレート。デフォルトは 921600 |
| `ipro.monitorBaudRate` | コンソールのボーレート。デフォルトは 115200。ファームウェアと一致させる必要があります |
| `ipro.chipVariant` | 書き込みツールの `--chip-variant`。Reef では `IPRO7AI` |
| `ipro.partitionTable` | 書き込みツールの `--pt`。Reef ではアプリケーションごとに設定します |
| `ipro.flashTargets`、`ipro.activeFlashTarget` | 名前付きの書き込み設定。毎回編集せずに設定を切り替えられます |

Reef 向けの設定はすべてコンソールが 115200 baud ですが、`ipro7_jpeg_decode`（`defconfig_reef`）だけは 921600 を使います。基準となるのはアプリケーションの `CONFIG_PLATFORM_UART_BAUDRATE` です。`ipro_ble_remote` の最初の書き込み（boot2 と A/B テーブル）と `ipro_reef_teach` の最初の書き込み（`mfg` ペイロード）には IntelProCube のコマンドラインを使います。[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md#boot2-ab)と [Edge AI ファームウェアの書き込み](../teach/firmware.md)を参照してください。

## メモリとデバッグのツール { #memory-map }

- `IPRO Analyse: Memory Map`：ビルド後に、各メモリ領域とコンポーネントごとの使用量を表示します。イメージが収まるかどうかは、あくまでリンカーの出力と書き込みに使うパーティションテーブルで判断します。
- `IPRO Analyse: Decode Crash Report`：例外のバックトレースをソースの位置に変換します。
- `IPRO Debug: Pin Function Lookup`：ピンの機能を調べます。
- `IPRO Debug: Register Explorer`：互換性のあるプローブ、正常な CCI 接続、正しいボード設定が必要です。プローブが USB で列挙されても、ボードとの CCI リンクが機能しているとは限りません。

OpenOCD をインストールしても、F5 によるソースレベルのデバッグはできません。Extension は GDB のデバッグアダプターも起動構成も設定しません。コンソールのログとクラッシュのデコードについては、[デバッグとトラブルシューティング](../reference/debugging.md)を参照してください。

## Reef でのハンズオン { #hands-on }

出荷時ファームウェアを使って、VS Code での編集、ビルド、書き込みのサイクルを実行します。

<div class="ipro-steps" markdown>

1. **コンソールの設定を確認します。** ファームウェアのコンソールのボーレートは `.config` で設定されています。`ipro.monitorBaudRate` を同じ値にする必要があります。

    ```ini title="apps/platform/ipro7ai_reef_demo/.config（抜粋）"
    CONFIG_PLATFORM_UART_BAUDRATE=115200
    ```

2. **コードを変更します。** `apps/platform/ipro7ai_reef_demo/main.c` を開き、`main()` のバナー行を変更します。

    ```c title="apps/platform/ipro7ai_reef_demo/main.c（抜粋、変更後）"
    ipro_platform_init();   /* heap + boot2 + log + shell */

    IPRO_LOGI(LOG_TAG, "==========================================");
    IPRO_LOGI(LOG_TAG, "  IPRO7AI Reef carrier demo - my build");
    ```

3. `IPRO: Build` で**ビルドします**。イメージは `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin` です。

4. [書き込みとコンソール](#flash)のとおりに**書き込みます**。SW1 + SW2 でダウンロードモードにし、チップバリアント `IPRO7AI` と `partition_cfg_2M.toml` で `IPRO: Flash` を実行してから、SW2 を押します。

5. 115200 で `IPRO: Serial Monitor` を開き、**コンソールを確認します**。最初の数行に次の内容が表示されます（ログのプレフィックスは省略）。

    ```text
    Build:<time>,<date>
    ...
      IPRO7AI Reef carrier demo - my build
    ```

    `Build:` の行にはビルドした時刻が、バナーには変更内容が表示されます。`reef selftest` でボードの各ブロックを確認できます。

</div>

終わったら、変更した行を元に戻すか、出荷時のイメージを書き込み直してください。次のステップ：[最初の独自アプリケーションを作る](../tutorials/first-own-app.md)と[アプリケーションのテスト](../tutorials/testing.md)。

## コンポーネントの更新 { #component-updates }

更新は IPRO SDK Online Setup で行います。Online Setup は、コンポーネントを新しいディレクトリにインストールするか、既存の環境に SDK やツールチェーンを追加します。使用中のものを上書きすることはありません。

| Online Setup のモード | インストールするもの | 切り替えられる設定 |
|---|---|---|
| Full environment | SDK、ツールチェーン、ビルドツール（CMake、Ninja、Python）、IntelProCube、OpenOCD、Extension | すべて |
| SDK only | SDK | `ipro.sdkRoot` |
| Toolchain only | RISC-V ツールチェーン | `ipro.toolchainPath` |
| Build tools only | CMake、Ninja、Python | それぞれのパス |
| IntelProCube only | IntelProCube | `ipro.flashToolPath` |
| OpenOCD only | OpenOCD | — |
| Extension only | Extension の VSIX | — |

SDK only と Toolchain only は、既存の環境に追加できます。[SDK またはツールチェーンだけをインストールする](../get-started/windows.md#components)を参照してください。更新後は VS Code を開き直して Diagnostics を実行します。元に戻すには、残しておいたディレクトリを設定で指定するか、**Install from VSIX…** で以前の VSIX をインストールします。

## コマンド { #shortcuts }

F1 または Ctrl+Shift+P でコマンドパレットを開きます。Extension はデフォルトのキーバインドを定義していないため、必要に応じて独自に割り当ててください。

| コマンド | 用途 |
|---|---|
| `IPRO: Open Control Center` | Control Center を開く |
| `IPRO Setup: Set SDK Root` | SDK ルートを設定 |
| `IPRO Setup: Run Diagnostics` | SDK とツールのパスを確認 |
| `IPRO Setup: Select Flash Tool` | IntelProCube のフォルダーを選択 |
| `IPRO: Go to Project…`、`IPRO: Select Project` | プロジェクトを検索、切り替え |
| `IPRO Config: Select Build Profile` | debug、release、size から選択 |
| `IPRO: Build` | 現在のプロジェクトをビルド |
| `IPRO: Clean` | 現在のプロジェクトのビルド出力を削除 |
| `IPRO: Batch Build` | 複数のプロジェクトをビルド |
| `IPRO Config: Menuconfig`、`IPRO Config: Open .config` | 設定を編集、または開く |
| `IPRO Config: Select Flash Target`、`IPRO Config: Configure Flash…` | 書き込みターゲットを選択。チップバリアント、パーティションテーブル、ボーレートを設定 |
| `IPRO: Select Serial Port` | コンソール／書き込みのポートを選択 |
| `IPRO Config: Set Monitor Baud Rate` | コンソールのボーレートを設定 |
| `IPRO: Flash` | ファームウェアを書き込み |
| `IPRO: Serial Monitor`、`IPRO: Close Serial Monitor` | コンソールを開く。コンソールを閉じてポートを解放 |
| `IPRO: Build, Flash & Monitor` | ビルド、書き込み、コンソールの表示を順に実行 |
| `IPRO Analyse: Memory Map` | メモリ使用量を解析 |
| `IPRO Analyse: Decode Crash Report` | 例外とバックトレースをデコード |
| `IPRO Debug: Pin Function Lookup` | ピンの機能を調べる |
| `IPRO Debug: Register Explorer` | CCI 経由でレジスターを確認 |

## よくある質問 { #faq }

| 症状 | 対処 |
|---|---|
| IPRO のコマンドが表示されない | Extension のバージョン、VS Code のプロファイル、Workspace Trust、SDK ルートを確認し、ウィンドウを再読み込みします |
| Diagnostics に古い SDK が表示される | ワークスペースとフォルダーの設定はユーザー設定を上書きできます。V2.2.0 のディレクトリに対して `IPRO Setup: Set SDK Root` を再度実行します |
| コンパイルまたはリンクに失敗する | コンパイラーが V2.2.0 に合ったツールチェーン（GCC 14）であることを確認します |
| コンソールが文字化けする、または古いボーレートのまま | ファームウェアのコンソールのボーレートと `ipro.monitorBaudRate` を確認し、モニターを閉じて開き直します |
| Reef への書き込み中に `flash jedec id: 00000000` と表示される | チップバリアントを `IPRO7AI` に設定します |
| 書き込みツールが `[All Success]` を出力しない | ボードがダウンロードモードになっていないか、ほかのプログラムがポートを使用しています |
| プローブは検出されるが CCI が応答しない | USB で列挙されても、ボード側の CCI リンクが機能しているとは限りません。配線とボードの設定を確認します |

## バージョン { #version }

SDK、Extension、Online Setup は、それぞれ独自のバージョン番号を持つ別々のパッケージです。現在の Extension は 3.3.0 で、Online Setup 3.6.0 がインストールします。インストーラーのバージョンが Extension のバージョンと同じとは限りません。インストールされているバージョンは Extensions ビューで確認できます。

## 関連ドキュメント { #related }

- [Windows のセットアップと VS Code](../get-started/windows.md)：ツールと Extension のインストール、SDK V2.2.0 の追加。
- [書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)：IntelProCube のコマンドライン、パーティションテーブル、boot2 と `mfg`。
- [ビルドシステムと設定](build-system.md)：`.config`、代替の設定、Reef 向けビルドの一覧。
- [最初の独自アプリケーションを作る](../tutorials/first-own-app.md)：独自の Reef アプリケーション。
