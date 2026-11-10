---
title: "リリースノート"
description: IPRO SDK の各正式リリースのリリース日、追加内容、含まれないもの、既知の制限事項を新しい順にまとめています。
migrate_from:
  - "changelog.html"
---

# リリースノート

IPRO SDK の正式リリースを新しい順に掲載しています。現在のリリースは V2.2.1 です。各バージョンのダウンロードとリリースノートは [GitHub Releases](https://github.com/INTELPRO-INC/IPRO-SDK/releases) にあります。SDK パッケージ自体の説明は、パッケージのルートにある `README.md` を参照してください。Windows 用オンラインインストーラー Online Setup もここに掲載しています（現在 3.6.0）。[ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest) からダウンロードできます。

## IPRO-SDK-V2.2.1 { #v2-2-1 }

<span class="ipro-badge">最新版</span> リリース日：2026-11-10 · [GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.1)

V2.2.0 の修正リリースで、アプリケーションは V2.2.0 と同じ 40 個の FreeRTOS アプリケーションです。ダウンロードファイルは `IPRO-SDK-V2.2.1.tar.gz` で、SHA-256 はリリースページに記載しています。[V2.2.0](#v2-2-0) のその他の内容（既知の問題を含む）は V2.2.1 にも当てはまります。

**修正**

- **IPRO6S の soft-AP**：工場出荷時の MAC アドレスがないチップ（IPRO6S EVK など）では、`wifi_ap_start` がメッセージなしで失敗していました。現在はステーションとアクセスポイントが起動ごとに 1 つのランダムアドレスを共有し、アクセスポイントは最下位ビットだけを反転させます。修正は `ipro6_demo`（`defconfig_ipro6_lpwifi`）と `ipro6_if_wifi`（`defconfig_ipro6_sdio`、`defconfig_ipro6_usb`）のビルド済み `libipro_os_adapter.a` に含まれます。手順は [IPRO6S](../hardware/chips/ipro6s.md#flashing) を参照してください。
- **`ipro_ble_remote` の `make_reef_ota.sh`**：IntelProCube フォルダー内の最新の boot2（0.7.0.1 では v0.6.0）、または `IPRO_BOOT2` で指定したファイルを使います。スクリプトを先に書き換える必要はなくなりました。
- **パッケージの README**：IntelProCube 0.7.0.1 を GitHub から取得する手順（ダウンロードとチェックサム）と、IPRO6S EVK の書き込みコマンド（`--chip-variant IPRO6S`、`partition_cfg_fw_direct.toml`）を記載しました。
- **Zephyr**：`zephyr/subsys/net/ipro_wifi/net_al_zephyr.c` をパッケージ内の lwIP ポートの L2 ソケットインターフェースに合わせました。IPRO6S は引き続き Zephyr では未対応です。

リリース前にパッケージからビルドして確認したもの：IPRO7 の FreeRTOS アプリケーション 36 個、IPRO6S の構成 7 個、Zephyr サンプル。ボード上では、IPRO6S EVK のスキャンと、コンピューターが接続して DHCP アドレスを取得できる soft-AP（macOS と Windows でそれぞれビルド・書き込み）、IPRO7AI Reef EVK の `reef selftest` を確認しました。

### 既知の問題 { #v2-2-1-known-issues }

- **IPRO Workbench 0.1.0 と IPRO6S**：Workbench は IPRO6S のパーティションテーブルを付けずに IPRO6S イメージを書き込むため、ボードが起動しません。IPRO Workbench 0.1.1 以降を使う（[IPRO6S EVK](../workbench/flash.md#ipro6s) を参照）か、[IPRO6S](../hardware/chips/ipro6s.md#flashing) のとおり IntelProCube のコマンドラインで書き込んでください。

## IPRO-SDK-V2.2.0 { #v2-2-0 }

リリース日：2026-11-03 · [GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0)

IPRO7 / IPRO7AI と IPRO6S のデュアルチップリリースで、V2.1.0 を置き換えます。FreeRTOS アプリケーションは 40 個（IPRO7 用 37 個、IPRO6S 用 3 個）です。ダウンロードファイルは `IPRO-SDK-V2.2.0.tar.gz` で、SHA-256 はリリースページに記載しています。

**新機能と変更点**

- **IPRO6S アプリケーションの復活**：`ipro6_demo`（Wi-Fi 6 ステーション / ソフト AP、DTIM 低消費電力）、`ipro6_if_wifi`（SDIO または USB 経由でホストに接続する Wi-Fi ブリッジ）、`ipro6_fmac`（FullMAC ファームウェアとその Flash ローダー）。Wi-Fi MAC、共存、RF のライブラリは同梱の `defconfig_*` ごとにビルド済みで、各設定はその設定用にビルドされたライブラリをリンクします。Reef の FIN Wi-Fi カードのファームウェアは、`ipro6_if_wifi` の `defconfig_ipro6_sdio` です。[IPRO6S](../hardware/chips/ipro6s.md) を参照してください。
- **新しいアプリケーション `ipro_reef_teach`**：IPRO7AI Reef EVK 用の Edge AI ファームウェアで、3 つの Teach ツールを備えています：`image`（USB カメラと分類器）、`voice`（誰が話しているか）、`sensor`（任意のセンサー）。起動時に 1 つのモードが選ばれ、モードごとに独自の USB ID を持ち、IPRO AI Studio から操作します。`tools/teach_web/` を使うとブラウザーで画像 Teach ができます。IPRO AI Studio は [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) からダウンロードできます。
- **IPRO Edge AI プラットフォーム V2.0**（`components/ai`）：ランタイム、ツールごとに 1 スロットを持つモデルストア、入力ソース、前処理、アプリケーションフレームワーク。NPU の待機には上限があり、超過するとブロックをリセットしてフェイルクローズの故障状態に入ります。Edge AI ファームウェアは AON ウォッチドッグを有効にします（ダウンロードモードでは無効）。CPU のレイヤーグラフが最後のレイヤーレコードを越えて読み出すことはなくなりました。
- **チップ全体のリセット**：`hal_reboot_full()` は AON ウォッチドッグを通じて、常時オンドメインを含むチップ全体をリセットします。`CONFIG_APP_WATCHDOG` を有効にすると、`platform_init()` は起動の最初からウォッチドッグを有効にします。`ipro_reef_teach` はこれを使ってツールを切り替えます。これにより、カメラを接続した Reef で `image` モードから切り替えた後、次回の起動がリセットするまで停止する問題が修正されました。
- **新しいアプリケーション `ipro7_jpeg_decode`**：ソフトウェア（TJpgDec）で JPEG を RGB565 / RGB888 にデコードします。フォーマットの事前チェックを備え、Huffman テーブルのないカメラの MJPEG フレームにも対応します。IPRO7 の MJPEG ブロックはエンコード専用です。Reef では `defconfig_reef` を使い、コンソールは 921600 baud です。
- **`ipro7ai_reef_demo`**：`mic usb` で Reef を USB マイク（16 kHz、PDM クロックからレート変換）にします。`mic sdrec` は SD カードに WAV ファイルを録音します。
- **`build_freertos.sh`**：`flash` は設定から `--chip-variant` を選択し（Reef と IPRO7AI EVK では `IPRO7AI`）、`-c` または `IPRO_CHIP_VARIANT` で上書きできます。`-P` または `IPRO_FLASH_PT` でパーティションテーブルを渡せます。`flash` が送信する `reboot_dl`、`monitor`、`test` はアプリケーション自身のコンソールボーレートを使います。[ツールのコマンドライン](tools.md#build-cli) を参照してください。
- **BLE コントローラー**：IPRO7 用の 16 個のビルド済みライブラリを本リリースのソースから再ビルドしました。ヘッダーで宣言済みだった `ipro_ble_ctlr_heap_watermarks()` と `ipro_ble_ctlr_link_diag_start()` がリンクできるようになりました。
- **USB デバイス**：RX FIFO のオーバーフローを修正、デイニシャライズ時に切断、CDC-ECM のフレーミングを修正し、USB コンソールが確実に接続されるようになりました。**lwIP**：割り込みからの `sys_mbox_trypost` は FromISR の経路を通ります。Opus は独自の `arch.h` でビルドされます。
- **BSP**：BLE のみのアプリケーション向けに PLL を停止したシステムクロック。`CONFIG_OCRAM_NORET_SCRATCH_ONLY` で RAM の状態を PDS で保持される 64 KB 内に収めます。`hal_lp_enter_fastboot()` は HBN に入ります。PSA アクセラレータードライバーを含むセキュリティエンジン HAL v2。
- サンプルアプリケーションにはネットワークの認証情報が組み込まれていません。

**アプリケーション**

- 合計 40 個：IPRO7 用 37 個、IPRO6S 用 3 個。V2.1.0 と比べて、`ipro_reef_teach`、`ipro7_jpeg_decode`、`ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac` が新規で、V2.1.0 の話者認識アプリケーションは `ipro_speaker_recog` に名前が変わりました。
- 9 個のアプリケーションに IPRO7AI Reef EVK 用の設定があります。一覧とビルドコマンドは [よくある質問](faq.md#reef-apps) と [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples) にあります。

リリース前にパッケージからビルドして確認したもの：36 個の IPRO7 FreeRTOS アプリケーション（`ipro_agora_sentino` は先に AOSL コアが必要）、IPRO6S の 7 つの設定、`ipro7_evb` と `ipro7ai_evk` 用の Zephyr サンプル。

**含まれないもの**

- IntelProCube 書き込みツール：[GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) から 0.7.0.1 をダウンロードします。[開発環境の準備](../get-started/environment.md#intelprocube)を参照してください。
- RISC-V ツールチェーン：INTELPRO にお問い合わせください。
- モデル変換ツールを含む IPRO AI Studio：[GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) からダウンロードしてください。
- IPRO6S 用の BLE コントローラーライブラリと、IPRO6S 用の BLE / BR/EDR アプリケーション。IPRO6S アプリケーションは Wi-Fi のみです。
- Matter。FreeRTOS アプリケーションの Thread（Thread は Zephyr で利用可能）。
- オンターゲットデバッグ（OpenOCD / GDB）の設定、クラッシュダンプ用ホストツール、ボードテストスクリプト、`menuconfig`。
- Zephyr：Reef のボード定義はありません。IPRO6S には対応していません。低消費電力モードはなく、ディスプレイ、カメラ、オーディオコーデック、USB、SD ホスト、イーサネット、NPU のドライバーもありません。
- `ipro_agora_sentino` に必要な AOSL コアと Sentino デバイストリプル：AOSL はアプリケーションの README の説明に従って GitHub から入手します。

### 既知の問題と注意事項 { #v2-2-0-known-issues }

- **Reef ボードヘッダーのコメント**：`bsp/board/ipro7/ipro7ai_reef_board_config.h` のコメントは、以前の（V3.0）キャリアボードの拡張ヘッダーとジャンパーについて記述しています。ピン定義は V4.0 と一致しています。V4.0 のヘッダー、スイッチ、ジャンパーについては、このサイトの [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) が正となります。
- **ビルド済みライブラリセットがない IPRO6S の設定が 2 つあります**：`ipro6_demo/defconfig_ipro6_lpwifi_ping` と `ipro6_fmac/defconfig_ipro6_fmac_ap` はパッケージに含まれていますが、`CONFIG_WIRELESS_LIB_VARIANT` を設定しておらず、リリース時に確認した設定にも含まれていません。[IPRO6S](../hardware/chips/ipro6s.md) のページに記載した設定を使ってください。
- **`ipro_le_audio_headset`**：アプリケーションの README では、オーディオのレンダリングは現在無効、メディアストリーミングは未検証とされています。オーディオ出力を前提にする前に、README のステータスの節を読んでください。
- **`ipro_throughput_test` のドキュメント**：README と `OPERATION_MANUAL.md` には、本リリースに含まれないデモアプリケーション、Android アプリ、コントローラーのビルドオプション（`CONFIG_BTBLECONTROLLER_LIB` や `link8` など）が記載されています。ビルドと書き込みは README の Build / Flash の節と [BLE スループットテスト](../tutorials/ble-throughput.md) に従ってください。
- **クラッシュ後の待機**：`ipro7ai_reef_demo` と `ipro_reef_teach` は `CONFIG_EXCEPTION_DUMP=y` を設定しているため、クラッシュ後、同梱されていないホストツールを待って `==DUMP_READY:2000000==` を表示し続けます。診断情報を保存して SW2 を押すか、この設定を `n` にしてください。[クラッシュの解析](debugging.md#crash-analysis) を参照してください。
- **`build_freertos.sh` は IPRO7 のみ書き込めます**：常に `--chipname ipro7` を渡し、`--boot2` や `--mfg` は渡せません。IPRO6S のイメージ、`ipro_ble_remote` の OTA ビルド、`ipro_reef_teach` は IntelProCube で直接書き込んでください。
- **README に記載されているが同梱されていないもの**：一部のコンポーネントやアプリケーションの README は、本リリースに含まれないアプリケーション、ツール、ドキュメント（ボードのユーザーガイドや Edge AI プログラミングガイドなど）に言及しています。ドキュメントは INTELPRO から入手できます。[ドキュメント](../documents/index.md) を参照してください。

## Online Setup 3.6.0 { #tools-3-6-0 }

リリース日：2026-11-04 · [インストーラーのダウンロード](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.6.0)

Windows 用オンラインインストーラーです。SDK V2.2.0 をインストールする際、SDK の Windows でのビルドの問題を修正します：IPRO ツールチェーンの認識（判定時に `/dev/null` をコンパイルしていたため、Windows のビルドはすべて標準 GCC のフラグと DSP 非対応のビルド済みライブラリにフォールバックしていました）、CMake 4 で Ninja によるビルドを失敗させるビルドメッセージ、シリアルコンソール。また、PowerShell 用の `build_freertos.ps1` を追加します。SDK only と Full は同じ SDK をインストールするようになり、その SDK は組み合わせるツールチェーンに合わせて準備されます。既存の環境に、何も上書きせずに SDK やツールチェーンを追加できます。ツールチェーンは引き続き GCC 13.1.1、Extension は 3.3.0 のままです。[Windows のセットアップと VS Code](../get-started/windows.md) を参照してください。

## IPRO-SDK-V2.1.0 { #v2-1-0 }

リリース日：2026-10-16 · [GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0)

Zephyr RTOS への対応を追加しました。FreeRTOS アプリケーションは IPRO7 を対象とし、合計 35 個です。

**新機能と変更点**

- **Zephyr RTOS**：SDK は `ipro7_evb` と `ipro7ai_evk` 用の Zephyr v4.4.0 モジュール（`zephyr/module.yml`、`west.yml`）でもあります。GPIO、UART、SPI、I2C、PWM、ADC、DAC、カウンターと RTC、ウォッチドッグ、Flash、DMA、エントロピー、I2S / PDM などのドライバー、Bluetooth LE（IPRO BLE コントローラーのビルド済みライブラリ上の Zephyr ホスト）、IEEE 802.15.4 と OpenThread、sysbuild による MCUboot、BLE 経由のイメージアップロード（MCUmgr SMP）を備えています。`tools/zephyr/bootstrap.sh` から始めてください。[Zephyr RTOS](../guides/zephyr.md) を参照してください。
- RF ドライバーと IEEE 802.15.4 MAC は Zephyr 用のビルド済みライブラリとして提供されます（`components/wireless/rf/ipro7_rf/lib/zephyr/`、`components/wireless/ieee802154/lib/zephyr/`）。
- **新しいアプリケーション `ipro_agora_sentino`**：IPRO7AI Reef EVK 上の Sentino クラウド AI 音声。BLE によるプロビジョニング、IPRO6S FIN カード経由の Wi-Fi、MQTT、Agora RTC を備えています。ビルド済みの Agora RTC SDK と AOSL の IPRO7 移植版を同梱しています。AOSL コア、Sentino プラットフォームが発行するデバイストリプル、FIN カードのファームウェアは、アプリケーションの README の説明に従って別途入手します。
- **IPRO7AI Reef EVK の水晶発振子調整**：Reef ビルドでは RF 水晶発振子の capcode をデフォルトで 95 に設定し、起動時と RF の初期化のたびに適用します（`CONFIG_IPRO7_XTAL_CAPCODE`。アプリケーションの設定で明示した値が優先されます）。ビルド済みの RF ライブラリと IEEE 802.15.4 ライブラリは、この値をアプリケーションから受け取ります。Zephyr では、Reef で `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95` を設定してください。
- **ツール**：`tools/serial_monitor.py`（`--timeout 0` で Ctrl-C まで実行。Linux でも高速ボーレートが使用可能）と `tools/zephyr/` を追加しました。`build_freertos.sh` と Zephyr スクリプトは、シリアルポートを `-p` / `IPRO_SERIAL_PORT` から取得するか、接続されている唯一の USB シリアルポートを使います。書き込みツールは `IPRO_FLASH_TOOL` または `PATH` から取得します。
- IPRO BLE コントローラーの IPRO7 用ビルド済みライブラリ 16 個を更新しました。

**アプリケーション**

- FreeRTOS アプリケーション 35 個。V2.0.9 と比べて `ipro_agora_sentino` が新規です。
- V2.0.1 と比べて 7 個が新規です：`ipro7ai_reef_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_ai_link`、`ipro_agora_sentino`。IPRO6S の 3 つのアプリケーション（`ipro6_btdm_phyrf`、`ipro6_demo`、`ipro6_if_wifi`）は提供されなくなりました。

**含まれないもの**

- IPRO6S アプリケーション、BLE コントローラーライブラリ、`ipro6_rf`：パッケージの README にはまだ IPRO6S の記載がありますが、本リリースにはいずれも含まれていません。当時、IPRO6S の開発には V2.0.1 を使うことになっていました。V2.2.0 から IPRO6S アプリケーションが復活しています。[IPRO6S](../hardware/chips/ipro6s.md) を参照してください。
- IPRO6S 側の Wi-Fi ファームウェア（Reef の FIN カードを含む）：INTELPRO にお問い合わせください。
- Matter。FreeRTOS アプリケーションの Thread（Thread は Zephyr で利用可能）。モデル変換ツール。
- 別途入手する IntelProCube 書き込みツールと RISC-V ツールチェーン。

**既知の制限事項**

- `ipro_ble_remote/defconfig_lowpower` は BLE コントローラーをソースビルドに切り替えるため、このパッケージからはビルドできません。
- `build_freertos.sh flash` は `--chip-variant` も `--pt` も渡さず、`monitor` は常に 115200 baud を使います。IPRO7AI ボードや 921600 baud のアプリケーションでは、ツールを直接使ってください。V2.2.0 で改善されています。[IPRO-SDK-V2.2.0](#v2-2-0) を参照してください。
- Zephyr にはまだ低消費電力モードがなく、ディスプレイ、カメラ、オーディオコーデック、USB、SD ホスト、イーサネット、NPU のドライバーも、IPRO7AI Reef EVK のボード定義もありません。

リリース時に実施したビルドとボード上での確認は、GitHub のリリースページに記載しています。

## IPRO-SDK-V2.0.9 { #v2-0-9 }

リリース日：2026-10-15 · [GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.9)

V2.1.0 の前の IPRO7 リリースです。アプリケーションは 34 個、Zephyr はありません。

- IPRO7AI Reef EVK の新しい出荷時ファームウェア `ipro7ai_reef_demo`：LED、ボタン、スピーカーとヘッドホン、マイク、SD カード、OV5640 / OV2640 カメラ。`defconfig_wifi_ipro6s` で IPRO6S FIN カード経由の Wi-Fi と RTSP カメラストリームを追加します。
- 新しい EVK ボードライブラリ `components/board/ipro7ai_evk` を使った、IPRO7AI EVK 用の新しいアプリケーション `ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7ai_evk_person_detect`。
- 新しい `ipro7_uvc_cam`（USB UVC カメラ）と `ipro_ai_link`（IPRO AI Studio の Run on board 用）。
- AI ライブラリ `libai.a` は SD カードからモデルを読み込めます。ビルド済みライブラリにビルドマシンのパスは含まれていません。
- IPRO7 アプリケーションのみです。IPRO6S の開発には V2.0.1 を使ってください。

## Online Setup 3.5.0 { #tools-3-5-0 }

リリース日：2026-09-10 · [インストーラーのダウンロード](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.5.0)

実行のたびに公式の IPRO-SDK リリースを検出し、`.tar.gz` 形式の SDK アーカイブを受け付け、フルインストールでは古い Windows リンカー向けにビルド済みライブラリを準備します。

## IPRO-SDK-V2.0.1 { #v2-0-1 }

リリース日：2026-09-09 · [GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)

IPRO6S への対応拡大と 31 のアプリケーションプロジェクトを含む V2.0 に続く、BLE オーディオの連続転送のためのメンテナンスリリースです。

- 継続的な転送中の Bluetooth ホストのキュー公開のアトミック性を修正しました。
- PDM 録音は、240 秒の PSRAM リングバッファーと 30 秒ごとの自動チャンク分割により、論理時間で最大 4 時間に対応します。Android はチャンク間も高い接続優先度を維持します。
- PDM は `link2` コントローラー、1 接続のホスト、2M PHY を使います。EVB / EVK 用の設定と Android コンパニオンアプリのソースを同梱しています。
- IPRO6S の Wi-Fi / BR/EDR リファレンス、SDIO リンクの両端、NPU / TFLM のサンプル、同梱の `.inm` / `.tflite` モデルを追加しました。
- `ipro_unit_test` と Linux x86-64 用 CMake を同梱しています。1.2.1 にあった `serial_monitor.py` と `PREBUILT-ARCHIVES-STRIPPED.txt` は含まれていません。

公開されたリリースでは、31/31 のアプリケーションのビルドと、Pixel 7a と IPRO7AI ボードによる 5 分間の録音テストの結果が報告されています：960,000 バイトのチャンク 10 個、パケットの欠落やシーケンスの欠番なし、リングの折り返し成功、84.2–91.2 KB/s の安定した転送。これらの結果はそのテスト環境でのものであり、すべてのボードやスマートフォンで保証されるものではありません。

## Online Installer 3.4.0 { #tools-3-4-0 }

[インストーラーのダウンロード](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.4.0)

動的な公開カタログ、パッケージごとに独立したバージョン、フルインストール時の互換性の選択、キャッシュによるオフラインインストールを追加しました。Extension は 3.3.0 のままです。このバージョンはカタログに登録された SDK（安定版は 1.2.1）のみをインストールします。SDK V2.2.0 をインストールするには 3.6.0 を使ってください。[Windows のセットアップと VS Code](../get-started/windows.md) を参照してください。

## 開発ツール：Windows インストーラー / Extension 3.3.0 { #tools-3-3-0 }

インストーラーと Extension はそれぞれ独立してバージョン管理されています。このリリースは SDK V1.2.1 に対応します。Windows のウィザードには Full、Extension only、SDK only のモードがあります。Extension には、Control Center と内蔵の Windows シリアルモニターに加えて、VSIX、SDK の ZIP / フォルダー、Git スナップショットからのコンポーネント更新が追加されました。[Windows のセットアップと VS Code](../get-started/windows.md) と [VS Code Extension](../guides/vscode.md) を参照してください。

## IPRO-IPRO7-SDK-V1.2.1 { #v1-2-1 }

リリース日：2026-09-08 · [GitHub リリース](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/v1.2.1)

- `ipro_bt_host` に Zephyr 4.4 ホスト、`ipro_ble_controller` に IPRO BLE コントローラー（ビルド済みライブラリ）。
- 16 個のコントローラーアーカイブ：4 つの ACL バリアント × 2 つの機能プロファイル × debug / release。コントローラーのソースは含まれていません。
- IPRO7 側の `ipronet_host` と `sdiowifi` コンポーネント、および `ipro7_sdio_wifi`。対応する IPRO6S ファームウェアは別途入手します。
- AI 推論は `components/ai/lib/libai.a` とヘッダーで提供されます。`.blai` モデルファイルは含まれていません。
- `tools/serial_monitor.py` を同梱しています。書き込みツール、ボードテストスクリプト、クラッシュパーサー、OpenOCD 設定は別途提供です。
- `PREBUILT-ARCHIVES-STRIPPED.txt` のとおり、2.41 より古い binutils との互換性のため、AI、ISP、RF、LC3、低消費電力フレームワークのアーカイブからデバッグ情報を削除しています。これらのライブラリ内でソースレベルのステップ実行はできません。

| アプリケーション | パス | 説明 |
|---|---|---|
| `ipro_ble_remote` | `apps/bluetooth/ble/ipro_ble_remote/` | GATT サービス、画像転送、OTA |
| `ipro_ble_transparent` | `apps/bluetooth/ble/ipro_ble_transparent/` | UART / BLE 透過転送 |
| `ipro_throughput_test` | `apps/bluetooth/ble/ipro_throughput_test/` | 双方向の BLE スループットテスト |
| `ipro_ble_hid_keyboard` | `apps/bluetooth/ble/ipro_ble_hid_keyboard/` | HID over GATT キーボード |
| `ipro_le_audio_headset` | `apps/bluetooth/le_audio/ipro_le_audio_headset/` | DAC / USB オーディオ出力の設定を持つ LE Audio ヘッドセット |
| `ipro_pdm_mic_demo` | `apps/multimedia/ipro_pdm_mic_demo/` | PDM マイクの録音、BLE 転送、LC3 圧縮 |
| `ipro7_demo` | `apps/platform/ipro7_demo/` | 周辺機能、画像処理、オーディオ、イーサネットのデモ |
| `ipro7_sdio_wifi` | `apps/platform/ipro7_sdio_wifi/` | IPRO6S を Wi-Fi 無線として使う IPRO7 SDIO ホスト |
| `ipro7ai_evk_demo` | `apps/platform/ipro7ai_evk_demo/` | IPRO7AI EVK のディスプレイ、カメラ、オーディオ、AI / BLE の設定 |

V1.0.1 の画像キャプチャー、単体の BIS ソース / シンク、クラウドオーディオゲートウェイ、音声アシスタントのアプリケーションは、このリリースには含まれていません。

## IPROREL-IPRO7-V1.0.1 { #v1-0-1 }

リリース日：2026-03-13 · プラットフォーム：IPRO7（RISC-V RV32IMAFC）

プラットフォーム、BLE、ISP、LE Audio を統合した IPRO7 SDK のフル提供パッケージです。9 個のリファレンスアプリケーション、Zephyr ベースの BLE ホスト、ビルド済みの linkN コントローラーライブラリ、統一されたビルドシステムを含みます。

| カテゴリー | アプリケーション | 説明 |
|---|---|---|
| bluetooth/ble | `ipro_ble_remote` | GATT サービスのデモ（LED、Button、UART、OTA、画像転送） |
| bluetooth/ble | `ipro_ble_transparent` | AT コマンドインターフェースを備えた BLE 透過データ転送 |
| bluetooth/ble | `ipro_ble_img_capture` | BLE 画像アップロードサービス付きの画像キャプチャー（OTA を含む） |
| bluetooth/ble | `ipro_throughput_test` | 双方向の BLE スループットテスト（2M PHY + DLE） |
| bluetooth/le_audio | `ipro_le_audio_headset` | GAF / BAP のユニキャストとブロードキャストのヘッドセット（LC3） |
| bluetooth/le_audio | `ipro_le_audio_bis_source` | Auracast 互換の BIS ブロードキャストソース |
| bluetooth/le_audio | `ipro_le_audio_bis_sink` | BIS ブロードキャストシンク（BASE の解析とオーディオのリサンプリング） |
| multimedia | `ipro_agora_sentino` | Agora RTC クラウドオーディオストリーミングゲートウェイ（イーサネット / USB NCM 経由のネットワーク） |
| platform | `ipro7_demo` | IPRO7 プラットフォームの周辺機能デモ |

- BLE スタック：Zephyr ベースのホスト（GAP、GATT、L2CAP、SMP、ISO、LE Audio）。IPRO BLE コントローラーのビルド済みライブラリは、標準 BLE（`link1_periph`、`link1`–`link8`）、LE Audio（`link1_leaudio`、`link2_leaudio`）、BLE 5.4 + LE Audio（`link1_leaudio_53_54`、`link2_leaudio_53_54`、`link4_leaudio_53_54`）、BLE 5.3 / 5.4（`link1_53`、`link1_54`、`link2_54`）の各バリアント。
- ビルド済みライブラリ：`isp_algorithm`（ISP 画像処理）、`ipro7_rf`（RF ドライバー）、`liblc3`（LC3 コーデック）、`lp_framework`（低消費電力フレームワーク）。
- 既知の制限事項：BLE コントローラーのソースは含まれず、ビルド済みの linkN バリアントのみです。`CONFIG_BLE_FORCE_SOURCE_BUILD` には対応していません。

## IPRO-BLE-SDK-V0.0.1 { #v0-0-1 }

リリース日：2026-02-12 · プラットフォーム：IPRO7（RISC-V RV32IMAFC）

IPRO BLE SDK の最初の正式リリースです。10 個のアプリケーション、Zephyr ベースの BLE ホスト、ビルド済みのコントローラーライブラリ、統一されたビルドシステムを備えた BLE 5.4 と LE Audio の開発環境です。

- BLE アプリケーション：BLE Remote（GATT サービスのデモ）、Throughput Test（双方向スループット）、HID Keyboard（HOGP）、Transparent Data（AT コマンドによる透過転送）。
- LE Audio アプリケーション：LE Audio Headset（GAF / BAP のユニキャストとブロードキャスト）、BIS Broadcast Source（Auracast 互換）、BIS Broadcast Sink（BASE の解析とリサンプリング）、Walkie-Talkie（BIS ベースのプッシュトゥトーク）。
- ESL アプリケーション：ESL Tag（Bluetooth ESL Profile タグ）、ESL Gateway（ESL タグ用のアクセスポイント）。
- BLE スタック：IPRO BLE コントローラーのビルド済みライブラリ（linkN バリアント。このリリースで `link2_54` を追加）、ビルド済みの RF ドライバー（`ipro7_rf`）と LC3 コーデック（`liblc3`）。従来の btprofile コンポーネントは削除され、アプリケーションは全面的に Zephyr の `bt_*` API を使います。
- ビルドシステム：統一 CLI `./build_freertos.sh <app> build flash monitor`、ベンダー製と標準の GCC ツールチェーンの自動検出、Kconfig ベースの設定。
- 要件：`/opt/toolchain/riscv_ipro7/` の RISC-V ツールチェーン、CMake 3.19 以降、Ninja、Python 3.8 以降。
- 既知の制限事項：コントローラーのソースは含まれていません。`ipro_blecontroller_test`（UART HCI モード）はコントローラーのソースが必要なため含まれていません。`CONFIG_BLE_FORCE_SOURCE_BUILD` には対応していません。
