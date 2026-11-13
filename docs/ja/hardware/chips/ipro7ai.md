---
title: "IPRO7AI"
description: IPRO7AI の特徴、NPU ランタイムとそのメモリの設定方法、IPRO7AI Reef EVK での NPU サンプル
migrate_from:
  - "architecture.html#soc-variants"
  - "ai-npu.html#architecture"
---

# IPRO7AI

IPRO7AI は [IPRO7](ipro7.md) と同じダイで、NPU を有効にし、8 MB の PSRAM と Flash をパッケージに内蔵したものです。CPU、ワイヤレス、周辺機能は IPRO7 と同じです。IPRO7AI Reef EVK のメインチップです。本リリースでは、カメラによる物体認識、3 つの IPRO AI Teach ツール、IPRO AI Studio のボード上推論を実行します。

<div class="ipro-facts" markdown>
<div><strong>0.1 TOPS</strong><span>NPU</span></div>
<div><strong>8 MB</strong><span>パッケージ内蔵 PSRAM</span></div>
<div><strong>IPRO7AI</strong><span>書き込み時の <code>--chip-variant</code></span></div>
<div><strong>libai.a</strong><span>ビルド済み推論ランタイム</span></div>
</div>

## IPRO7 との違い { #soc-variants }

| 項目 | IPRO7AI |
|---|---|
| NPU | 有効、0.1 TOPS。NPU のアクティベーションバッファーは PSRAM に置かれるため、AI アプリケーションにはすべて PSRAM が必要です |
| PSRAM | パッケージ内蔵 8 MB、`0x1e000000` |
| Flash | パッケージ内蔵。SDK はデフォルトで 1 MB のレイアウトをリンクし、`CONFIG_IPRO7_FLASH_2M=y` で 2 MB のレイアウトを選択します。`ipro7ai_reef_demo` の `.config` には、ブートログに JEDEC ID `0xEF4015`（2 MB）と表示された場合にこの行を追加できると記載されています |
| 書き込み | `--chip-variant IPRO7AI` でこのチップの Flash ピンを選択します（ツールの設定ファイルでは `flash_pin` `0x9`） |
| その他 | CPU、メモリマップ、ワイヤレス、周辺機能は IPRO7 と同じです。[IPRO7 の主な仕様](ipro7.md#key-specs)を参照 |

Reef 用の構成のうち、`ipro_reef_teach` と `ipro_agora_sentino` の `.config`、および `ipro_ble_remote`、`ipro_le_audio_headset`、`ipro_ai_link` の `defconfig_reef` は、すでに 2 MB のレイアウトを使っています。その他の Reef 用構成は 1 MB のレイアウトです。

## NPU と推論ランタイム { #architecture }

推論ランタイムはビルド済みライブラリ `components/ai/lib/libai.a` として提供されます。公開ヘッダーは `components/ai/iproai_def.h` と、`components/ai/` 以下の各モジュールのヘッダーです。ランタイムのソースはパッケージに含まれていません。V2.3.0 の `components/ai` は IPRO Edge AI プラットフォーム V2.0 で、ランタイム、ツールごとに 1 スロットを持つモデルストア、入力ソース、前処理、アプリケーションフレームワークで構成されます。NPU の完了待ちには上限時間があり、タイムアウトすると NPU ブロックをリセットして安全なフォールト状態にします。CPU での推論には TensorFlow Lite Micro、NMSIS-NN、TinyMaix（`components/3rdparty/`）を使えます。

### AI を有効にする { #config }

アプリケーションの `.config` に次の設定を明示的に記述してください。この SDK のビルドは Kconfig の `select` を適用しないため、PSRAM は自動では有効になりません。

```ini title=".config（抜粋）"
CONFIG_AI_SUPPORT=y          # components/ai（libai.a）をリンクする
CONFIG_USE_PSRAM=y           # NPU のアクティベーションバッファーとモデルは PSRAM に置かれる
CONFIG_MM_SUPPORT=y          # カメラと ISP を使う場合
CONFIG_AI_MODEL_FROM_FILE=y  # SD カードからモデルを読み込む場合
```

`ipro_reef_teach` の `.config` と `ipro_ai_link` の `defconfig_reef` は、そのまま出発点にできる完全な Reef 用構成です。

### モデルの格納場所 { #models }

NPU は `.inm` 形式のモデルを実行します。モデルは次の 3 か所のいずれかに格納します。

| 格納場所 | 方法 | Reef での例 |
|---|---|---|
| `mfg` Flash パーティション | 書き込みツールで `--mfg` を指定して書き込みます。`ipro_reef_teach` は独自のパーティションテーブル `partition_reef_teach.toml` と `mfg` レイアウト（モード、声紋モデル、画像モデル、センサーモデルにそれぞれ 1 スロット）を持ち、書き込むデータは `mfg_payload.py` で作成します | `ipro_reef_teach` |
| ファームウェアにリンク | モデルをイメージに組み込みます。ほかに書き込むものはありません | `ipro7_uvc_cam` の `defconfig_reef_rps` |
| SD カード | 実行時に `sd:/`（FatFS）から PSRAM に読み込みます | `ipro_ai_link` の `defconfig_reef` |

パッケージに含まれるモデル：`apps/ai/ipro_reef_teach/model/`（声紋モデル `model_b.spkb`）、`tools/teach_web/assets/`、`apps/platform/ipro7_demo/demo/ai/ai_model/`、`apps/test/ipro_npu_yolo/src/`、`apps/ai/ipro7ai_evk_rps/model/`。IPRO AI Studio と Edge AI ツールは SDK ではなく、別の IPRO Edge AI パッケージで提供されます。モデル変換ツールについては INTELPRO にお問い合わせください。

### メモリ { #memory }

AI と画像処理の両方を有効にすると（`CONFIG_AI_SUPPORT`、`CONFIG_MM_SUPPORT`）、NPU の SRAM が `0x11020000` 以降にマッピングされるため、リンカーは OCRAM を先頭の 64 KB（`0x11010000`–`0x11020000`）に制限します。アプリケーションが BLE コントローラーの Exchange Memory も確保する場合（`CONFIG_EM_SIZE` が 0 以外）、OCRAM は 48 KB と、64 KB − `CONFIG_EM_SIZE` の非保持領域になります。CMake はビルド中に選択したレイアウトを表示します（例：`AI+MM (EM=0): OCRAM=64KB`）。

Zephyr RTOS ポートには NPU ドライバーがありません。NPU サンプルは FreeRTOS アプリケーションです。

## Reef での NPU サンプル { #sdk-usage }

| サンプル | Reef 用構成 | 内容 |
|---|---|---|
| [`ipro_reef_teach`](../../examples/ipro_reef_teach.md) | `.config` | IPRO AI Teach 2.0 のボード用ファームウェア。`image`（USB カメラと画像分類器）、`voice`（声紋）、`sensor`（センサー信号）の 3 つのツールを 1 つずつ実行し、IPRO AI Studio から操作します |
| [`ipro7_uvc_cam`](../../examples/ipro7_uvc_cam.md) | `defconfig_reef_rps` | NPU によるじゃんけんの認識結果を映像に描画する USB ウェブカメラ |
| [`ipro_ai_link`](../../examples/ipro_ai_link.md) | `defconfig_reef` | IPRO AI Studio の「Run on board」用のボードファームウェア。`sd:/` からモデルと入力を読み込み、出力を USB で返します |

その他の NPU サンプルは IPRO7AI EVK または IPRO7 EVB が対象です（`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro7ai_evk_launcher`、`ipro_speaker_recog`、`ipro_npu_yolo`、`ipro_ai_bench`）。[サンプル](../../examples/index.md)を参照してください。

## IPRO7AI 搭載ボード { #boards }

| ボード | パッケージ | ボード設定 |
|---|---|---|
| [IPRO7AI Reef EVK V4.0](../boards/reef-evk.md) | QFN56、ボードに実装 | `CONFIG_IPRO7AI_REEF=y` |

IPRO7AI EVK（`CONFIG_IPRO7AI_EVK=y`）もこのチップを搭載しています。このボードについては INTELPRO にお問い合わせください。

## 関連ドキュメント { #documents }

- [IPRO7](ipro7.md)：チップの全仕様とメモリマップ。
- [AI と NPU ガイド](../../guides/ai-npu.md)：モデルのデプロイと推論 API。
- [IPRO AI Teach](../../teach/index.md)：IPRO AI Studio を使って、画像、声紋、センサー信号を Reef に学習させます。
- IPRO7 データシート：[ドキュメント](../../documents/index.md)を参照してください。
