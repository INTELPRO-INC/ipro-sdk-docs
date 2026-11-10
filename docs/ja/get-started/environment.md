---
title: "開発環境の準備"
description: SDK を入手して検証し、macOS、Linux、Windows にビルドツール、RISC-V ツールチェーン、IntelProCube をインストールし、コンソールケーブルを接続して、1 回のビルドで環境を確認します。
migrate_from:
  - "getting-started.html#sdk-2-1-0"
  - "getting-started.html#prerequisites"
---

# 開発環境の準備

このページを終えると、コンピューターに SDK、ビルドツール、RISC-V ツールチェーン、書き込みツール IntelProCube がそろい、Reef のコンソールポートが認識され、SDK ルートから IPRO7AI Reef EVK の出荷時ファームウェアをビルドできるようになります。各手順には OS ごとのタブがあります。Windows の手順全体は [Windows のセットアップと VS Code](windows.md) にあります。

## 前提条件 { #prerequisites }

| 項目 | 要件 |
|---|---|
| ホスト | bash が使える macOS または Linux、または Windows x64 |
| 権限 | パッケージのインストールと `/opt/toolchain/` への書き込みには管理者権限が必要です |
| ネットワーク | SDK のダウンロードに必要です。Windows の Online Setup には GitHub へのアクセスが必要です |
| 別途入手するもの | RISC-V ツールチェーン：macOS／Linux 用は INTELPRO から入手し、Windows では Online Setup がインストールします |
| 書き込みツール | IntelProCube 0.7.0.1：[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) からダウンロードします。[IntelProCube のインストール](#intelprocube)を参照してください。Windows では Online Setup がインストールします |
| ハードウェア | IPRO7AI Reef EVK、USB-C ケーブル、コンソールケーブル。[必要なもの](index.md#what-you-need) を参照してください |

## SDK の入手 { #get-sdk }

<div class="ipro-steps" markdown>

1. **ダウンロードします：** [IPRO-SDK-V2.2.0 リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) から `IPRO-SDK-V2.2.0.tar.gz` をダウンロードし、そのページに掲載されている SHA-256 を控えておきます。

2. **ダウンロードしたファイルを検証します：**

    === "macOS"

        ```bash
        shasum -a 256 IPRO-SDK-V2.2.0.tar.gz
        ```

    === "Linux"

        ```bash
        sha256sum IPRO-SDK-V2.2.0.tar.gz
        ```

    === "Windows"

        ```powershell
        Get-FileHash .\IPRO-SDK-V2.2.0.tar.gz -Algorithm SHA256
        ```

    表示される 64 文字の 16 進数が、リリースページの値と一致する必要があります（大文字と小文字は区別しません）。一致しない場合は、もう一度ダウンロードしてください。

3. **展開してバージョンを確認します。** 新しいディレクトリに展開し、古い SDK に上書きしないでください。

    === "macOS / Linux"

        ```bash
        tar xzf IPRO-SDK-V2.2.0.tar.gz
        cd IPRO-SDK-V2.2.0
        cat VERSION.txt
        ```

    === "Windows"

        ```powershell
        tar -xzf .\IPRO-SDK-V2.2.0.tar.gz
        Get-Content .\IPRO-SDK-V2.2.0\VERSION.txt
        ```

    `VERSION.txt` の内容：

    ```text
    IPRO SDK Release
    ========================================
    IPRO7: IPRO-SDK-V2.2.0
    IPRO6: IPRO-SDK-V2.2.0

    Release Date: 2026-11-03
    Base Commit: 60afd4ab
    ```

    `IPRO-SDK-V2.2.0/` が SDK ルート（このサイトでは `<SDK>`）で、`apps/`、`bsp/`、`components/`、`build_freertos.sh`、`VERSION.txt` が入っています。

</div>

## ビルドツールのインストール { #host-tools }

<div class="ipro-steps" markdown>

1. **CMake、GNU Make、Python をインストールします。**

    === "macOS"

        ```bash
        xcode-select --install          # make が入ります
        brew install cmake python3
        ```

    === "Linux"

        ```bash
        sudo apt update
        sudo apt install -y cmake make python3
        ```

        Debian／Ubuntu の例です。他のディストリビューションでは同等のパッケージをインストールしてください。Linux x86-64 では、`PATH` に `cmake` がない場合、SDK の `tools/cmake/` にある CMake 3.15 がビルドに使われます。

    === "Windows"

        Online Setup は、**Full environment** または **Build tools only** を選ぶと CMake、Ninja、Python をインストールします。[Windows のセットアップと VS Code](windows.md#online-setup) を参照してください。

2. **バージョンを確認します**（macOS／Linux）：

    ```bash
    cmake --version     # 3.15 以降。Zephyr には 3.20 以降が必要
    make --version      # 1 行目が GNU Make
    python3 --version   # 3.8 以降
    ```

</div>

## RISC-V ツールチェーンのインストール { #toolchain }

<div class="ipro-steps" markdown>

1. **デフォルトのパスに配置します。**

    === "macOS / Linux"

        INTELPRO から入手したアーカイブを、次のファイルが存在するように展開します：

        ```text
        /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc
        ```

    === "Windows"

        Online Setup は Windows 用ツールチェーン GCC 13.1.1 をインストールし、SDK をそれに合わせて準備するため、SDK V2.2.0 はそのままビルドできます。生成されるイメージは、macOS と Linux で GCC 14 を使ってビルドしたものとは異なります。[Windows のセットアップと VS Code](windows.md#online-setup) を参照してください。

2. **動作を確認します**（macOS／Linux）：

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc --version
    ```

    1 行目は `riscv64-unknown-elf-gcc` で始まり、バージョン 14.x が表示されます。

3. **別の場所に置く場合：** コンパイラーのプレフィックス `CROSS_COMPILE`（末尾のハイフンを含む）を設定します。ビルドは、まずコマンドラインまたは環境変数の `CROSS_COMPILE`、次にアプリケーションの `.config` の `CONFIG_CROSS_COMPILE`、最後にデフォルトのパスの順に使います。

    ```bash
    export CROSS_COMPILE=<toolchain dir>/bin/riscv64-unknown-elf-
    ```

    設定を残すには、この行を `~/.zshrc`（macOS）または `~/.bashrc`（Linux）に追加します。

</div>

## IntelProCube のインストール { #intelprocube }

IntelProCube は IPRO6 と IPRO7 の書き込み・OTA ツールで、[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) で公開されています。このサイトは 0.7.0.1 を前提にしています。Windows では Online Setup が 0.7.0 をインストールします。IPRO7 と Reef の書き込みに使うファイルは 0.7.0.1 と同じです（[Windows のセットアップと VS Code](windows.md) を参照）。IPRO6S に書き込むときは、[IntelProCube の README](https://github.com/INTELPRO-INC/ipro-cube#windows) に従って 0.7.0.1 も別途インストールしてください。

<div class="ipro-steps" markdown>

1. **ダウンロードして確認します。**

    === "macOS"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-macos-arm64.tar.gz
        shasum -a 256 IntelProCube-0.7.0.1-macos-arm64.tar.gz
        ```

        `c3a8bf7eca2a48c3f9bf40c3241ddf6aec5155688f2a92f40a84cc47f7633bc4` と表示されます。macOS 版には Apple シリコンが必要です。ブラウザーでダウンロードした場合は、展開する前に `xattr -d com.apple.quarantine IntelProCube-0.7.0.1-macos-arm64.tar.gz` を実行してください。実行しないと、macOS がパッケージ内のプログラムを終了させます。

    === "Linux"

        ```bash
        curl -LO https://github.com/INTELPRO-INC/ipro-cube/releases/download/v0.7.0.1/IntelProCube-0.7.0.1-linux-x64.tar.gz
        sha256sum IntelProCube-0.7.0.1-linux-x64.tar.gz
        ```

        `efc5765ca402d0af00b42489dd61a74481531875b871517af5c0bca9d7387df9` と表示されます。Linux 版は x86-64 用です。

    値が異なる場合はダウンロードし直してください。各バージョンの値はリリースの `SHA256SUMS.txt` にも記載されています。

2. **展開します。**

    === "macOS"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-macos-arm64.tar.gz -C ~/ipro
        ```

    === "Linux"

        ```bash
        mkdir -p ~/ipro
        tar xzf IntelProCube-0.7.0.1-linux-x64.tar.gz -C ~/ipro
        ```

    `~/ipro/IntelProCube` ができます。このサイトでは `<IntelProCube>` と表記します。コマンドラインツールはこのディレクトリで実行してください。チップ設定、パーティションテーブル、boot2 イメージを `chips/` から読み込むためです。

3. **動作を確認します。**

    === "macOS"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_macos --help
        ```

    === "Linux"

        ```bash
        cd <IntelProCube>
        ./ipro_iot_tool_linux --help
        ```

    === "Windows"

        ```powershell
        cd <IntelProCube>
        .\ipro_iot_tool.exe --help
        ```

    出力は使い方の概要から始まります：

    ```text
    usage: ipro_iot_tool_macos [-h] [--list-ports] --chipname CHIPNAME
                               [--interface INTERFACE] [--port PORT]
                               [--baudrate BAUDRATE] [--xtal XTAL]
                               [--chip-variant CHIP_VARIANT] [--dts DTS] [--pt PT]
                               [--boot2 BOOT2] [--firmware FIRMWARE] [--mfg MFG]
    ...
    ```

4. **`build_freertos.sh` から見つけられるようにします**（macOS／Linux）：`IPRO_FLASH_TOOL` を設定するか、`<IntelProCube>` を `PATH` に追加します。

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ```

</div>

## コンソールケーブルの接続 { #usb-serial }

Reef には USB-UART 変換チップが搭載されていません。USB-C は電源とボード自身の USB デバイス機能に使われ、コンソールと書き込みは U6 に接続したアダプターまたは IPRO Debug Probe を経由します。

<div class="ipro-steps" markdown>

1. **アダプターまたは Debug Probe をコンピューターに接続し**（ボードは接続していなくてもかまいません）、新しく現れたシリアルポートを探します：

    === "macOS"

        ```bash
        ls /dev/cu.*
        ```

        USB-UART 変換アダプターは `/dev/cu.usbserial-XXXX` として表示されます（名前はアダプターによって異なります）。IPRO Debug Probe を接続すると `/dev/cu.usbmodem…` ポートが 2 つ追加され、末尾が `02` のものがコンソールです。

    === "Linux"

        ```bash
        ls /dev/ttyUSB* /dev/ttyACM*
        ```

        アダプターは通常 `/dev/ttyUSB0` として表示されます。IPRO Debug Probe を接続すると `/dev/ttyACM*` ポートが 2 つ追加されます。

    === "Windows"

        **デバイス マネージャー → ポート (COM と LPT)** を開き、接続の前後で比較します。新しく現れたエントリがそのポートです（例：`COM5`）。IPRO Debug Probe を接続すると 2 つ追加されます。

2. **新しいポートが現れない場合：** データ通信に対応したケーブルを試してください。システムがアダプターを認識しない場合は、アダプターのメーカーが提供するドライバーをインストールしてください。Debug Probe については INTELPRO にお問い合わせください。

3. **Linux の権限：** ポートを開くときに `Permission denied` で失敗する場合は、`ls -l /dev/ttyUSB0` でポートを所有するグループ（多くは `dialout`）を確認し、自分をそのグループに追加してログインし直します：

    ```bash
    sudo usermod -aG dialout $USER
    ```

</div>

Debug Probe の 2 つのポートの見分け方と、各 Reef アプリケーションが USB-C で提供する USB デバイスについては、[書き込みとシリアルコンソール：ポートの見分け方](flash-and-monitor.md#ports) を参照してください。

## 動作確認 { #verify }

SDK ルートから出荷時ファームウェアをビルドします（macOS／Linux）：

```bash
./build_freertos.sh ipro7ai_reef_demo
```

ビルドに成功すると次のように表示されます：

```text
Project: ipro7ai_reef_demo  (platform/ipro7ai_reef_demo)

→ Building ipro7ai_reef_demo...
✓ Build succeeded (14s)
  Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (244 KB)
  Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
```

ビルド時間とイメージサイズは、ホストとツールチェーンによって多少異なります。Windows では、VS Code Extension の `IPRO: Build` または `build_freertos.ps1` で確認します。[Windows のセットアップと VS Code](windows.md#verify) を参照してください。

## 2 つの環境の違い { #choose }

| 作業 | macOS／Linux | Windows |
|---|---|---|
| ツールのインストール | システムのパッケージマネージャーに加え、INTELPRO から入手するツールチェーンと、GitHub からダウンロードする IntelProCube | Online Setup（ツールチェーン、CMake / Ninja / Python、IntelProCube、OpenOCD、VS Code Extension） |
| ビルド | `make -C apps/<category>/<app>` または `./build_freertos.sh` | VS Code Extension の `IPRO: Build` |
| 書き込み | IntelProCube のコマンドラインツール、または `./build_freertos.sh … flash` | `ipro_iot_tool.exe` |
| コンソール | `screen` や `picocom` などのターミナルプログラム、`tools/serial_monitor.py` | PuTTY などのターミナルプログラム、または Extension の Serial Monitor |
| 自動化（`build_freertos.sh`、`tools/serial_monitor.py`） | 利用可能 | 利用不可：どちらも bash と POSIX termios が必要です |
| Zephyr（`tools/zephyr/`） | 利用可能 | SDK に Windows 用の手順はありません |

このサイトのコマンドライン例は macOS／Linux 向けに書かれています。

## トラブルシューティング { #troubleshooting }

| 症状 | 原因 | 対処 |
|---|---|---|
| 計算した SHA-256 がリリースページの値と異なる | ダウンロードが不完全、またはファイルが破損している | ファイルを削除して、もう一度ダウンロードします |
| `No cmake found. Install cmake or provide bundled cmake at …` | `PATH` に `cmake` がなく、同梱の CMake もこのホストでは実行できない（Linux x86-64 専用） | [ビルドツールのインストール](#host-tools) のとおり CMake 3.15 以降をインストールします |
| `riscv64-unknown-elf-gcc: No such file or directory` | ツールチェーンが `/opt/toolchain/riscv_ipro7/` にない | [RISC-V ツールチェーンのインストール](#toolchain) のとおり `CROSS_COMPILE` を設定します |
| `Flash tool not found: ipro_iot_tool_macos` | `IPRO_FLASH_TOOL` が未設定で、IntelProCube が `PATH` にない | [IntelProCube のインストール](#intelprocube) の手順 4 を行います |
| アダプターを接続しても新しいシリアルポートが現れない | 充電専用の USB ケーブル、またはドライバーがない | ケーブルを交換します。アダプターメーカーのドライバーをインストールします |
| Linux でポートを開くと `Permission denied` になる | ポートのグループに属していない | `dialout`（または表示されたグループ）に参加して、ログインし直します |
| macOS で `/dev/tty.*` を開くとターミナルが固まる | `tty.*` はキャリア検出を待つ | `/dev/cu.*` を使います |

## 次のステップ { #next-steps }

- Windows の場合：[Windows のセットアップと VS Code](windows.md)
- ホストの準備ができたら：[最初の FreeRTOS アプリケーション](first-app-freertos.md)
- コマンドラインのリファレンス：[macOS／Linux のコマンドライン](command-line.md)
