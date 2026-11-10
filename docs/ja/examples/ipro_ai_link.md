---
title: ipro_ai_link
description: IPRO AI Studio の「Run on board」用ボード側ファームウェア：microSD（sd:/）から .inm モデルと入力を読み込み、NPU で実行して生の出力を表示します。コンソールから手動でも操作できます
generated: tools/gen_examples.py
migrate_from: []
---

# ipro_ai_link

IPRO AI Studio の「Run on board」用ボード側ファームウェア：microSD（`sd:/`）から `.inm` モデルと入力を読み込み、NPU で実行して生の出力を表示します。コンソールから手動でも操作できます

| 項目 | 内容 |
|---|---|
| ソースコード | [`apps/test/ipro_ai_link`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_ai_link) |
| ボードと設定 | Reef（`defconfig_reef`）、`.config` は IPRO7 EVB 用 |
| コンソール | UART 115200（USB CDC ポートでも使用可） |
| ビルド | Reef：`make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |

## Reef で動かす { #on-the-reef }

このアプリケーションには README がないため、以下の手順はソースコードに基づいています。FAT でフォーマットした microSD カードが必要です。

<div class="ipro-steps" markdown>

1. **ビルド**

    ```bash
    make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef
    ```

    イメージは `apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin` です。

2. **書き込み**：[ダウンロードモード](../hardware/boards/reef-evk.md#download-mode)に入り、IntelProCube のディレクトリで次を実行します。

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --firmware <SDK>/apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin
    ```

    `[All Success]` を確認してから SW2 を押します。

3. **実行**：115200 baud でコンソールを開くと、ボードが `ipro_ai_link ready` を表示します。コンピューターの USB ポートに接続すると、ボードは 2 つの CDC シリアルポート（VID `0x3896`、PID `0x0704`）として認識されます。1 つ目はデータ用、2 つ目はコンソールです。

4. **モデルを手動で実行**：`.inm` モデルと生の入力ファイルを SD カードにコピーして挿入し、次のように入力します。

    ```text
    ai_mount
    ai_load sd:/model.inm
    ai_input sd:/input.bin
    ai_run
    ai_out
    ```

    `ai_out` は出力テンソルを 16 進数で表示します。各バイトは XOR 0x80 で格納されています。パスは必ず `sd:/` で始めます。

</div>

SDK には試せるモデルが付属しています（例：`apps/platform/ipro7_demo/demo/ai/ai_model/mbv2.inm`）。IPRO AI Studio は [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) からダウンロードできます。
