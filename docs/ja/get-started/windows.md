---
title: "Windows のセットアップと VS Code"
description: IPRO SDK Online Setup 3.6.0 で SDK V2.2.0、RISC-V ツールチェーン、ビルドツール、IntelProCube、VS Code Extension を Windows に一括インストールし、IPRO7AI Reef EVK の出荷時ファームウェアを VS Code または PowerShell でビルドして書き込み、コンソールを開きます。
migrate_from:
  - "windows-installation.html"
  - "vscode-extension.html#installation"
not_migrated:
  - "windows-installation.html#overview"
  - "windows-installation.html#package-contents"
  - "windows-installation.html#install-modes"
  - "windows-installation.html#full-install"
  - "windows-installation.html#extension-only"
  - "windows-installation.html#sdk-only"
  - "windows-installation.html#settings"
---

# Windows のセットアップと VS Code

Windows では、IPRO SDK Online Setup が SDK V2.2.0、RISC-V ツールチェーン、ビルドツール（CMake、Ninja、Python）、IntelProCube、OpenOCD、VS Code Extension を一括でインストールします。その後、IPRO7AI Reef EVK の出荷時ファームウェア `ipro7ai_reef_demo` をビルドして書き込み、COM ポートでコンソールを確認します。ビルドと書き込みは、VS Code で行うか、PowerShell で `build_freertos.ps1` を使って行います。

!!! info "ツールチェーンのバージョン"
    Online Setup がインストールする Windows 用ツールチェーンは GCC 13.1.1 で、SDK はそれに合わせて準備されます（SDK ルートの `PREBUILT-ARCHIVES-STRIPPED.json` に記録されます）。SDK V2.2.0 は macOS と Linux では GCC 14 でビルドされるため、生成されるイメージはそれらとは異なります。

## 要件 { #requirements }

- GitHub にアクセスできる Windows x64（Online Setup は公開カタログと GitHub のリリースからコンポーネントをダウンロードします）。
- VS Code 1.102 以降（インストーラーがダウンロードできます）。
- IPRO7AI Reef EVK、USB-C ケーブル、U6 に接続する IPRO Debug Probe または USB-UART 変換アダプター。[必要なもの](index.md#what-you-need) を参照してください。

## インストール { #online-setup }

<div class="ipro-steps" markdown>

1. **インストーラーをダウンロードします：** [IPRO SDK Online Setup の最新リリース](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest)（3.6.0）から `IPRO-SDK-Online-Setup-3.6.0.exe` をダウンロードします。GitHub へのサインインは不要です。

2. **PowerShell で検証します：**

    ```powershell
    Get-FileHash .\IPRO-SDK-Online-Setup-3.6.0.exe -Algorithm SHA256
    ```

    `Hash` 列の値が、同じリリースの `SHA256SUMS.txt` に記載された同じファイルの値と一致する必要があります（大文字と小文字は区別しません）。インストーラーにはコード署名がないため、Windows が SmartScreen の警告を表示することがあります。社内のセキュリティ規定に従ってください。

3. **Full environment を選びます：** **Choose packages** で選択します。

4. **バージョンを確認します：** **Select package versions** では、すべてのコンポーネントを latest のままにします。一覧には latest が実際にどのバージョンになるかが表示されます（例：`latest (2.2.0)`）。

5. **ディレクトリを選びます：** **Select Destination Location** では、デフォルトの新しいフォルダー `C:\IPRO\versions\3.6.0-<date-time>` のままにするか、まだ存在しないフォルダーを入力します（これがインストールルートで、このページでは `<install dir>` と表記します）。

6. **追加のタスクを選びます：** VS Code がインストールされていない場合は **Install VS Code from Microsoft if absent** にチェックを入れます。**Install the selected Extension into VS Code** はチェックしたままにします。VS Code がこの環境を使うようにするには **Switch only selected component settings** に、どのターミナルからでもツールを実行できるようにするには **Add installed tools to user PATH** にチェックを入れます。

7. **インストールします：** **Ready to Install** でディレクトリ、モード、バージョンを確認し、**Install** をクリックします。

8. **完了ページを確認します：** SDK フォルダー（`<install dir>\sdk\IPRO-SDK-V2.2.0`）、最初に実行するコマンドラインのコマンド、ツールチェーンのフォルダーが表示されます。新しい設定と `PATH` を反映させるため、VS Code とターミナルを開き直してください。

</div>

セットアップでは、SDK の Windows でのビルドの問題（IPRO ツールチェーンの認識、CMake 4 で Ninja を止めてしまうビルドメッセージ、シリアルコンソール）も修正され、`build_freertos.ps1` が追加されます。変更されたファイルは SDK ルートの `WINDOWS-HOST-FIXES.json` に記載されています。

## VS Code Extension のセットアップ { #installation }

<div class="ipro-steps" markdown>

1. **Extension がインストールされていることを確認します：** Extensions パネルで `@installed IPRO` を検索すると、IPRO SDK Extension（識別子 `ipro.ipro-sdk-extension`）が表示されます。

2. **SDK を開きます：** **File → Open Folder…** で `<install dir>\sdk\IPRO-SDK-V2.2.0` を開き、ソースを確認したうえで Workspace Trust を許可します。

3. **SDK ルートを設定します：** インストール時に設定のタスクにチェックを入れなかった場合は、++f1++ を押し、同じフォルダーに対して `IPRO Setup: Set SDK Root` を実行します。

4. **環境を確認します：** `IPRO Setup: Run Diagnostics` を実行し、SDK ルート、コンパイラー、CMake、Python、書き込みツールがすべて `<install dir>` の下を指していることを確認します。

5. **出荷時ファームウェアをビルドします：** `IPRO: Go to Project…` を実行して platform カテゴリの `ipro7ai_reef_demo` を選び、`IPRO: Build` を実行します。

</div>

Extension のその他のコマンドと設定は [VS Code Extension](../guides/vscode.md) にあります。

## コマンドラインでのビルド { #command-line }

`build_freertos.ps1` は `build_freertos.sh` の Windows 版で、アクションは同じです。`build`、`clean`、`flash`、`monitor`、`size`、`test` は組み合わせて指定でき、順に実行されます。オプションもほぼ同じですが、ここでの `-c` はツールチェーンのプレフィックス（`--cross`）で、チップバリアントとパーティションテーブルは長い形式の `--chip-variant` と `--pt` だけです（`build_freertos.sh` では `-c` が `--chip-variant`、`-P` がパーティションテーブルです）。`PATH` に登録されているかどうかにかかわらず、同じインストールのツールチェーン、CMake、Ninja、Python、IntelProCube を使います。Windows はデフォルトでは `.ps1` ファイルを直接実行しません。`powershell -ExecutionPolicy Bypass -File` はその 1 回の実行にだけ適用され、システムの設定は変更しません。

<div class="ipro-steps" markdown>

1. **SDK フォルダーに移動します**

    ```powershell
    cd <install dir>\sdk\IPRO-SDK-V2.2.0
    ```

2. **ビルドします**

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 build ipro7ai_reef_demo
    ```

    ```text
    Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

    -> Building ipro7ai_reef_demo...
    [OK] Build succeeded (21s)
      Binary: ...\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin (219 KB)
      Toolchain: <install dir>/toolchain/riscv_ipro7_win32/bin/riscv64-unknown-elf-gcc
      Log: ...\apps\platform\ipro7ai_reef_demo\build\build.log
    ```

    失敗した場合は、ビルドログの最後の 30 行と、ログ全体の場所が表示されます。

3. **IPRO ツールチェーンが認識されたことを確認します**

    ```powershell
    Select-String -Path apps\platform\ipro7ai_reef_demo\build\build.log -Pattern "\[toolchain\]"
    ```

    ```text
    -- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
    ```

</div>

その他：`-l` はすべてのアプリケーションを一覧表示し、`-h` はすべてのオプションを表示します。`-d defconfig_<name>` は別構成をビルドし、`-c <prefix>` は別のツールチェーンを選びます（プレフィックスは `riscv64-unknown-elf-` で終わります）。

## 書き込み { #flash }

### IPRO Debug Probe を使う場合 { #flash-probe }

<div class="ipro-steps" markdown>

1. **接続します：** SW7 を CAM、SW8 を PWR にし、IPRO Debug Probe を U6 に接続してから、Reef の USB-C を接続します。[スイッチの設定とボードの接続](first-app-freertos.md#connect) を参照してください。Windows ではプローブは 2 つの COM ポートとして表示されます。[ポートの見分け方](flash-and-monitor.md#ports) を参照してください。

2. **書き込んで起動バナーを確認します：** SDK フォルダーで次を実行します：

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 flash monitor ipro7ai_reef_demo -w "IPRO7AI Reef carrier demo"
    ```

    スクリプトがプローブのコンソールポートを選び、IntelProCube がボードをダウンロードモードにして書き込み、リセットします。バナーが表示されるとモニターは停止します：

    ```text
    [All Success]
    [OK] Flash succeeded (6s)
    ...
    [serial_monitor] MATCHED: IPRO7AI Reef carrier demo

    Summary:
      [OK] flash
      [OK] monitor
    ```

    IPRO7AI ボードのアプリケーションには、`--chip-variant IPRO7AI` とパーティションテーブル `partition_cfg_2M.toml` が自動的に適用されます。複数のシリアルポートが接続されている場合は、`-p COM5` でコンソールポートを指定します。

</div>

VS Code の場合：`IPRO: Select Serial Port` でプローブのコンソールポートを選び、`IPRO Config: Configure Flash…` でチップバリアントを `IPRO7AI`、パーティションテーブルを `partition_cfg_2M.toml` に設定してから、`IPRO: Flash` を実行します。

### USB-UART 変換アダプターを使う場合 { #flash-uart }

<div class="ipro-steps" markdown>

1. **接続します：** SW7 を CAM、SW8 を PWR にし、コンソールケーブルを U6 に接続してから、USB-C を接続します。[スイッチの設定とボードの接続](first-app-freertos.md#connect) を参照してください。

2. **COM ポートを確認します：** デバイス マネージャー → ポート (COM と LPT) を開きます。アダプターを接続したときに現れるポートがコンソールです（例：`COM5`）。

3. **ダウンロードモードに入ります：** SW1 (BOOT) を押したまま SW2 (RESET) を 1 回押し、SW1 を離します。

4. **書き込みます：** PowerShell で `<install dir>\IntelProCube` に移動し、次を実行します：

    ```powershell
    cd <install dir>\IntelProCube
    .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
        --port COM5 --baudrate 921600 `
        --pt chips/ipro7/partition/partition_cfg_2M.toml `
        --firmware <install dir>\sdk\IPRO-SDK-V2.2.0\apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

    最後の行が `[All Success]` の場合のみ成功です。ツールは失敗しても終了コード 0 で終了します。パラメーターについては [書き込みとシリアルコンソール](flash-and-monitor.md#flash-tool) で説明しています。完了したら SW2 を押してリセットします。

</div>

## コンソール { #console }

<div class="ipro-steps" markdown>

1. **コンソールを開きます：** SDK フォルダーで `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 monitor ipro7ai_reef_demo -t 30` を実行するか、PuTTY で **Serial** を選び、Serial line をコンソールの COM ポート、Speed を `115200` に設定して **Open** をクリックします。Tera Term や VS Code Extension の `IPRO: Serial Monitor` も使えます。

2. **リセットします：** `build_freertos.ps1 monitor` は `reboot` を送信します。他のターミナルプログラムでは SW2 (RESET) を押します。ウィンドウに起動バナー `IPRO7AI Reef carrier demo` が表示されます。++enter++ を押すと `ipro />` が表示されます。

3. **セルフテストを実行します：** `reef selftest` と入力します。期待される出力は [最初の FreeRTOS アプリケーション](first-app-freertos.md#verify) にあります。

</div>

書き込みの前にターミナルプログラムを閉じてください。開いたままだと、書き込みツールが COM ポートを開けません。

## SDK またはツールチェーンだけをインストールする { #components }

**Choose packages** で **SDK only** または **Toolchain only** を選ぶと、バージョンのページの次に **Choose where to install** が表示されます：

- **Add to this existing environment**：Online Setup でインストールした環境が、それぞれの SDK とツールチェーンとともに一覧表示され、ツールチェーンを含む最新の環境があらかじめ選択されています。SDK はその環境の `sdk\` に入り、そこにあるツールでビルドされます。すでに存在するバージョンは拒否されます。インストール済みのものが上書きされることはありません。
- **A new directory**：新しいフォルダーにインストールします。SDK は、`/TOOLCHAINROOT=` で指定したツールチェーン、VS Code に設定されているツールチェーン、または他の環境のうち最新のもののツールチェーンに合わせて準備され、`build_freertos.ps1` はそのツールチェーンを使います。

サイレントインストールでは、`/MODE=sdk /ENV=<environment folder>` で環境に追加します。その他のコマンドラインパラメーターは [Online Setup のインストールノート](https://github.com/INTELPRO-INC/ipro-sdk-releases/blob/main/INSTALLATION.zh-TW.md)（繁体字中国語）にあります。

## 動作確認 { #verify }

- ビルドで次のファイルが生成されます：

    ```text
    apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
    ```

- ビルドログに `Vendor toolchain detected` が含まれます。
- 書き込みの出力が `[All Success]` で終わります。
- リセット後、コンソールに起動バナーと `ipro />` が表示され、`reef selftest` で LED が順に点灯し、1 kHz の短いトーンが鳴ります。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| Windows に発行元不明または SmartScreen の警告が表示される | インストーラーにコード署名がない | 社内のセキュリティ規定に従います。保護機能は無効にしないでください |
| `.\build_freertos.ps1` が実行されない | Windows はデフォルトで `.ps1` ファイルを実行しない | `powershell -ExecutionPolicy Bypass -File .\build_freertos.ps1 ...` で実行します |
| 完了ページに、ツールチェーンが見つからないと表示される | 新しいフォルダーへの SDK のみのインストールで、組み合わせるツールチェーンが見つからなかった | ツールチェーンを含む環境に SDK を追加するか、`/TOOLCHAINROOT=<toolchain folder>` を付けてインストールし直します |
| Diagnostics に古い SDK のパスが表示される | ワークスペースまたはユーザー設定の SDK ルートが古いバージョンを指している | `IPRO Setup: Set SDK Root` を実行してから、もう一度 Diagnostics を実行します |
| IPRO のコマンドが表示されない | 現在の VS Code プロファイルに Extension がない、またはワークスペースが信頼されていない | Extension、プロファイル、Workspace Trust を確認し、`Developer: Reload Window` を実行します |
| デバイス マネージャーに新しい COM ポートが現れない | 充電専用の USB ケーブル、またはアダプターのドライバーがない | ケーブルを交換し、アダプターメーカーのドライバーをインストールします。Debug Probe については INTELPRO にお問い合わせください |
| 書き込みが `[All Success]` で終わらない | ボードがダウンロードモードになっていない、またはターミナルプログラムが COM ポートを使用している | ターミナルプログラムを閉じます。アダプターの場合は SW1 + SW2 でもう一度ダウンロードモードに入ります |
| `flash jedec id: 00000000` | `--chip-variant IPRO7AI` が指定されていない | 追加して、もう一度書き込みます |
| コンソールが文字化けする、または何も表示されない | ボーレートが 115200 でない、ボードがダウンロードモードのまま、または RX と TX が逆 | 115200 で開きます。SW2 を押します。RX と TX を入れ替えます |

インストールで問題が発生した場合は、`<install dir>\online-install.json`、`online-postinstall.log`、および隣にある `<install dir>.download.log` を保存しておいてください。

## 次のステップ { #next-steps }

- [最初の FreeRTOS アプリケーション](first-app-freertos.md)：出荷時ファームウェアのセルフテストとコマンド。
- [書き込みとシリアルコンソール](flash-and-monitor.md)：その他のダウンロードモード、パーティションテーブル、boot2、`mfg` データ。
- [VS Code Extension](../guides/vscode.md)：Extension のコマンドと設定。
