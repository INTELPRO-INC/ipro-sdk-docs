---
title: ipro_reef_teach
description: Reef の Edge AI ファームウェア：1 つのイメージに 3 つの Teach ツール、image（USB カメラ＋画像分類）、voice（声紋認識）、sensor（センサー分類）を収録し、起動時に Flash に保存されたモードで 1 つを選んで実行します。操作は IPRO AI Studio から行います。詳しい手順は IPRO AI Teach を参照してください
generated: tools/gen_examples.py
migrate_from: []
---

# ipro_reef_teach

Reef の Edge AI ファームウェア：1 つのイメージに 3 つの Teach ツール、`image`（USB カメラ＋画像分類）、`voice`（声紋認識）、`sensor`（センサー分類）を収録し、起動時に Flash に保存されたモードで 1 つを選んで実行します。操作は IPRO AI Studio から行います。詳しい手順は [IPRO AI Teach](../teach/index.md) を参照してください

| 項目 | 内容 |
|---|---|
| ソースコード | [`apps/ai/ipro_reef_teach`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/ai/ipro_reef_teach) |
| ボードと設定 | Reef（`.config`）、`image` モードには OV5640 カメラが必要 |
| コンソール | UART 115200 |
| ビルド | `make -C apps/ai/ipro_reef_teach` |

## Reef で動かす { #on-the-reef }

このファームウェアは専用のパーティションテーブル `partition_reef_teach.toml`（ファームウェア 640 KB、mfg 1364 KB）を使用します。初回の書き込みでは mfg ペイロード（ブートモードと声紋モデル）も書き込みます。画像モデルとセンサーモデルは、あとから IPRO AI Studio が USB 経由でデプロイします。

<div class="ipro-steps" markdown>

1. **ビルド**

    ```bash
    make -C apps/ai/ipro_reef_teach
    ```

    イメージは `apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin`（約 360 KB）です。

2. **mfg ペイロードの作成**：ブートモード（ここでは `image`）と付属の声紋モデルを含めます。

    ```bash
    python3 apps/ai/ipro_reef_teach/mfg_payload.py \
        --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
    ```

    SDK のルートに `reef_teach_mfg.bin` が作成されます。

3. **書き込み**：ボードを[ダウンロードモード](../hardware/boards/reef-evk.md#download-mode)にし、IntelProCube のディレクトリで次を実行します。

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --skip-ota --pt <SDK>/apps/ai/ipro_reef_teach/partition_reef_teach.toml \
        --firmware <SDK>/apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin \
        --mfg <SDK>/reef_teach_mfg.bin
    ```

    `[All Success]` を確認してから SW2 を押します。あとでファームウェアだけを更新する場合は `--mfg` を外します。モードと 3 つのモデルはすべて保持されます。

4. **モードの確認**：115200 baud でコンソールを開きます。起動ログの `RTCH:   mode: image` の行が実行中のモードを示します。`mode voice` と入力すると、ボードは約 2 秒後に声紋モードで再起動し、`RTCH: voice ready` を表示します。

</div>

モードごとに USB-C の識別情報が異なります（VID `0x3896`）。`image` は PID `0x0705`（UVC カメラ＋シリアルポート）、`voice` は `0x0720`、`sensor` は `0x0721`（シリアルポート）です。IPRO AI Studio がなくても、画像ツールはブラウザーで動作します。`python3 tools/teach_web/serve.py` を実行し、Chrome または Edge で http://localhost:8780 を開いてください。各モードの手順は [IPRO AI Teach](../teach/index.md) で説明しています。

## README { #readme }

!!! note "README の原文"
    以下はアプリケーションに付属する README（SDK V2.3.0）を原文のまま掲載したものです。翻訳はしておらず、公開に適さない内容だけを置き換えています。

<!-- verbatim:start -->

One image for the IPRO7AI Reef that runs any of the three Teach tools, one at
a time:

| mode | what it does | sources | USB | IPRO AI Studio page |
|---|---|---|---|---|
| `image` | USB camera + classifier | `apps/multimedia/ipro7_uvc_cam` | 3896:0705, camera + serial | **Teach** |
| `voice` | who is speaking | `apps/ai/ipro_reef_teach/voice` | 3896:0720, serial | **Audio** |
| `sensor` | any sensor, five simulated | `apps/ai/ipro_reef_teach/sensor` | 3896:0721, serial | **Sensor** |

This is the one Edge AI firmware for the Reef; the source folders above hold
each tool's code and are built only as part of it. The mode stored in flash
picks which tool starts at boot, each with its own USB identity, so each
IPRO AI Studio page finds the board. Switching stores another mode and restarts into it (about 2 s).
Each tool keeps its model in its own slot, so switching loses none of them:
deploy all three once and move between them freely.

### Switching

- **IPRO AI Studio**: open the page for the tool you want. When the Reef is in
    another mode, the page says so and offers **Switch to …**.
- **Console** (UART0, 115200): `mode` shows the current one; `mode image`,
    `mode voice` or `mode sensor` restarts into another.
- **USB**: `APP` / `APP <mode>` on the voice and sensor serial protocols
    (answers `APP <current> image voice sensor` / `APP OK <mode>`, then the
    board restarts); on the image one, a 16-byte header `"TAPP"`, u32 mode
    (0 image, 1 voice, 2 sensor, 0xFFFFFFFF to ask), u32 0, u32 0 (answers
    `TAPP <current> image voice sensor` / `TAPP OK <mode>`).

### Build and flash

```bash
make -C apps/ai/ipro_reef_teach
```

This firmware needs its own partition table, `partition_reef_teach.toml`: the
firmware partition is cut to 640 KB (the image is about 360 KB) and mfg grows
to 1364 KB so all three models fit at once. PSM, backup, media and factory
stay where the stock table has them.

The voiceprint model is flashed with the firmware, together with the mode to
start in; the image and Sensor models are deployed from IPRO AI Studio later.
Build the mfg payload, then flash everything:

```bash
python3 apps/ai/ipro_reef_teach/mfg_payload.py --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image \
    -o reef_teach_mfg.bin
TOOL=<IntelProCube dir>/ipro_iot_tool_macos
$TOOL --chipname ipro7 --chip-variant IPRO7AI --port <download UART> --baudrate 921600 \
    --skip-ota --pt apps/ai/ipro_reef_teach/partition_reef_teach.toml \
    --firmware apps/ai/ipro_reef_teach/build/build_out/ipro_reef_teach_IPRO7.bin \
    --mfg reef_teach_mfg.bin
```

The tool exits 0 even when it fails; look for `[All Success]`. Leave out
`--mfg` to update only the firmware: the mode and the three models stay.

At boot the console shows the mode:

```
RTCH:   mode: voice (`mode <image|voice|sensor>` to switch)
SPKM: model 'b3-e12': 437200 B, trunk 16/16 layers on the NPU, ...
RTCH: voice ready - shell `spk`, IPRO AI Studio Audio page over USB-C
```

### The mfg partition

| offset | size | holds |
|---|---|---|
| 0x000000 | 4 KB | the partition header |
| 0x001000 | 4 KB | the mode: `"RTMD"`, mode, ~mode (blank: image) |
| 0x002000 | 448 KB | voiceprint model (`model_b.spkb`, b3: 437 KB) |
| 0x072000 | 512 KB | image model (`.inm` + labels; MobileNetV2 0.35 is 461 KB) |
| 0x0F2000 | 256 KB | Sensor model (`.inm` + SNS1; the large size is 191 KB) |
| 0x132000 | 140 KB | free |

`src/reef_mode.h` has the map and `CMakeLists.txt` passes it to the three
tools' sources (`VOICE_MFG_*`, `TEACH_MFG_*`, `SENSOR_MFG_*`).

Each slot ends with a 4 KB record of the model store (`components/ai/store`):
a deploy is committed only after it has been written and read back, so a
reset during one leaves the slot's model either complete or reported missing
(`install interrupted`), never half written. A slot's room is its size less
that sector: voice 444 KB, image 508 KB, Sensor 252 KB. `mfg_payload.py`
writes the voice model's record too, so a model flashed with `--mfg` is found
CRC-checked (`SPKM: store: install #1, CRC … checked`). Models deployed by
the V1.1 firmware are still found (`V1.1 payload, no record`).

### How it is put together

- `main.c` reads the mode and starts one tool (`src/reef_apps.c`) from a task
    at that tool's own start-up priority.
- cherryusb calls `usbd_event_handler` and `usbd_cdc_acm_set_dtr` by name.
    Built here (`REEF_TEACH_COMBINED`), each tool's are renamed
    `<mode>_usbd_...` and `src/reef_usb.c` forwards to the running one.
- `.config` is the union of the three tools' configurations, without
    `CONFIG_SINGLE_PRECISION_FLOAT`: the Sensor front end has to equal IPRO AI
    Studio's value for value. The camera sources get `-fsingle-precision-constant`
    on their own, as in their firmware.
- All three tools' static data is linked in (207 KB, in PSRAM); the large
    buffers (camera frames, sample rings, deploy staging) are allocated at start
    by the running tool only.
- Every tool answers the IPRO Edge AI platform's V2.0 queries
    (device protocol 2 - IPRO Edge AI Programming Guide, *Device protocol* chapter) with `fw=ipro_reef_teach`;
    `CAPS`/`TCAP` lists the three modes. IPRO AI Studio's `ipro-ai model list
    --all` walks through them and comes back.
- The AON watchdog is armed (`CONFIG_APP_WATCHDOG`, 8 s nominal, about 5.6 s
    on the Reef's RC clock) and fed from a top-priority task by hardware-timer
    time (`components/os/freertos/app_watchdog.h`): a stalled SoC restarts in
    the mode it was in, with its models. Console: `watchdog`, `watchdog test`.
- Test commands on the UART shell: `multi [runs]` (voice mode: the Sensor
    model opened beside the voice trunk and both run from two tasks, every
    output checked against the model alone), `sens poll
    <Hz> <s>` and `sens prof` (sensor mode).

### Measured (2026-10-31, Reef)

| | |
|---|---|
| firmware image | 364 KB (397 KB in 2.0.0-rc2, with the NPU timeout and the watchdog) |
| switching, `APP`/`TAPP` to the new mode's port on USB | 1.4–2.8 s |
| all three models deployed (image MobileNetV2 461 KB, voice 437 KB, Sensor large 191 KB), cycled through every mode | each still loaded in its own mode |
| Sensor mode, `sim_vib` four states taught, large model | front end equal to Studio's, NPU within one step, 94 / 94 live |
| voice mode, enroll from a laptop speaker, name a stranger, stranger mode | the same behaviour as the voice tool built on its own |
| IPRO AI Studio Teach / Sensor / Audio pages, **Switch to …** | the board found in its new mode in 2.2–3.0 s |

The image mode's camera pipeline was not run in this test: the test Reef has
no camera fitted.

The tools, their pages, the console commands and the device protocol are
described in the IPRO7AI Reef user guide and the IPRO Edge AI Programming
Guide.

<!-- verbatim:end -->
