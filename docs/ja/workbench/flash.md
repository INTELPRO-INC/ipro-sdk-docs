---
title: "書き込みとボード"
description: IPRO Workbench が書き込みの前後にチェックする内容、パーティションテーブルの表示とチェック、ボードの Flash とファームウェアの確認、mfg パーティションへの AI モデルの書き込みを説明します。
---

# 書き込みとボード

書き込み時に IDE が行うチェック、パーティションテーブル、ボードの Flash、ファームウェアの確認、AI モデルの書き込みについて説明します。ボードは IPRO Debug Probe に接続した IPRO7AI Reef EVK V4.0 で、書き込みには IntelProCube を使用します。

## 書き込み { #flash }

<div class="ipro-steps" markdown>

1. **書き込みます。** アプリケーションを選択してビルドした後、**Flash** をクリックします（`Cmd+Alt+U` / `Ctrl+Alt+U`）。

    **期待される結果**：**Output** パネルが **IPRO Flash** に切り替わり、IntelProCube による書き込みの進行状況が表示されます。最後の行は `[All Success]` です。「Flashed &lt;application&gt; in N s.」という通知が表示されます。

2. **モニターはいったん閉じてから再び開きます。** 書き込みの前に、IDE はすべてのシリアルモニターを自動的に閉じます（1 つのポートを 2 つのプログラムが同時に使用することはできません）。**Build, Flash and Monitor** の場合は、書き込みに成功した後でモニターが再び開きます。

</div>

!!! warning "重要"
    IntelProCube は、書き込みに失敗してもエラーを報告しないことがあります。IDE は、出力に `[All Success]` が表示されたときにだけ書き込み成功とみなします。さらに、ボードの再起動後には、ボードが出力するビルド時刻もチェックします（[ボードの Flash とファームウェアの確認](#board-flash)を参照）。

書き込みに失敗すると、IDE は原因に応じたボタンを表示します。

![書き込みエラーの説明と、その操作ボタン](../assets/workbench/flash-guidance.svg)

| 状況 | IDE の動作 |
|---|---|
| アプリケーションがビルドされていない | 「has not been built yet」と表示し、**Build and Flash** を提示する |
| IntelProCube が見つからない | **Install IntelProCube**、または既存のものを指定する **Browse…** を提示する |
| ボードが応答しない | プローブのケーブルと電源の確認を促し、**Select Port** と **Retry** を提示する |
| ポートがほかのプログラムで使用中 | そのプログラムを閉じてから **Retry** するよう促す |
| パーティションテーブルがボードの Flash より大きい | 書き込みの前に確認する。**Flash Anyway** を選ぶか、代わりに **Partition Table** を開くことができる |

## パーティションテーブル { #partitions }

パーティションテーブルは、ファームウェア、OTA スロット B、AI モデル（mfg）などのデータを Flash のどこに配置するかを決めるものです。

<div class="ipro-steps" markdown>

1. **パーティションテーブルを開きます。** アプリケーションを右クリックして **Partition Table** を選択します。

    **期待される結果**：「Partition table of &lt;application&gt;」が開きます。**Flash with** には今回の書き込みで使用するパーティションテーブル（デフォルトでは、IntelProCube が `.config` の Flash サイズから選ぶもの）が表示され、その横に `.config` で設定された Flash サイズとファームウェアのサイズが表示されます。IDE がボードの Flash を把握している場合は、比較の行が追加されます（例：「The board on this probe has 2 MB of flash (Winbond EF4015); ipro_unit_test is set to 1 MB.」）。その下には、Flash マップ（スロット A とスロット B に 1 行ずつ）、各パーティションのアドレスとサイズ、FW パーティションのうちファームウェアが占める割合が表示されます。

2. **表の下にあるチェック結果を確認します。**

    **期待される結果**：問題がなければ何も表示されません。問題がある場合は、その説明が表示されます。例えば、1M パーティションテーブルの mfg と FW が同じ領域を共有している（AI モデルを書き込むとファームウェアが上書きされる）、2M パーティションテーブルの FW スロット B が mfg と重なっている（OTA 更新で AI モデルが上書きされる）、ファームウェアがスロット A より大きい、などです。

3. **アプリケーション独自のテーブルを使用します。** アプリケーションが独自のパーティションテーブルを同梱している場合は、ページに「This application ships …」と表示されます。**Flash with** でそれを選択すると、以降このアプリケーションの書き込みにはすべてそのテーブルが使われます。

4. **ボードと比較します。** シリアルモニターを開いた状態で **Reset Board** をクリックします。

    **期待される結果**：**On the board** で、ボードが起動時に出力するパーティションテーブルと比較され、各パーティションに「same」「differs」「not on the board」のいずれかが表示されます。すべて一致すると「The board printed the same table at its last boot.」と表示されます。

</div>

![Flash with、スロット A と B の Flash マップ、パーティション、ボードとの比較があるパーティションテーブルのビュー](../assets/workbench/partitions.svg)

!!! warning
    書き込みでは、**Flash with** で選択したパーティションテーブルが書き込まれます。ボード上のパーティションテーブルと異なる場合、位置が変わるパーティション（例：mfg の AI モデル）のデータは失われます。

## ボードの Flash とファームウェアの確認 { #board-flash }

ボードは起動時に、Flash の ID とファームウェアのビルド時刻を出力します。シリアルモニターを開いていると、IDE はこれらのメッセージを読み取り、サイドバーの **Board** ビューに表示します。

| 表示 | 意味 |
|---|---|
| Flash Winbond 2 MB (EF4015) | このプローブに接続されたボードの Flash とそのサイズ |
| Chip ID … | 書き込み時に IntelProCube が読み取ったチップ ID |
| Runs ipro_unit_test (built …) | ボードが起動時に出力したビルド時刻が、このアプリケーションの最新ビルドのファームウェアと一致している |
| Runs other firmware (built …) | ボードは最新ビルドを実行していない。そのビルドは書き込んだ後に初めて実行される |

書き込みの直後に「other firmware」と表示された場合は、書き込みが実際にはボードに届いていない可能性があります。IDE は警告を表示し、**Flash Again** を提示します。

パーティションテーブルがボードの Flash より大きな領域を使う場合（例：2 MB のボードに 4 MB のパーティションテーブルを選択した場合）、末尾を超えた部分が書き込まれないままにならないよう、IDE は書き込みの前に確認します。**Partition Table** をクリックして別のテーブルを選ぶか、正しいことを確認したうえで **Flash Anyway** をクリックします。

![パーティションテーブルがボードの Flash より大きいときに書き込みの前に表示される確認。Partition Table と Flash Anyway がある](../assets/workbench/flash-guard.svg)

## AI モデル { #ai-model }

IPRO7AI の NPU モデル（`.inm`）は Flash の mfg パーティションに置かれ、ファームウェアにはリンクされません。モデルを更新するときは mfg だけを書き込めばよく、ファームウェアを書き込み直す必要はありません。

<div class="ipro-steps" markdown>

1. **モデルを選択します。** アプリケーションを右クリックして **AI Model…** を選択します。**Model** でアプリケーションフォルダー内の `.inm` を選択するか、**Browse…** をクリックして別のファイルを選択します。

    **期待される結果**：モデルのサイズ、フォーマットのバージョン、レイヤー数、入力、NPU 命令・CPU 命令・重みの各サイズ、読み込み後に使用するメモリ（モデルとワークバッファーの合計を 8 MB の PSRAM と比較）、書き込み先の mfg パーティションが表示されます。最後の行には「The model fits this application and its partition table.」、または収まらない理由が表示されます。

2. **書き込みます。** 収まる場合は **Write to mfg** をクリックします。

    **期待される結果**：「Wrote … to the mfg partition in N s.」という通知が表示されます。書き込まれるのはモデルだけで、ファームウェアは変更されません。

3. **ボード上で確認します。** ボードがモデルを実行している間（シリアルモニターを開いた状態）、**On the board** に各レイヤーが NPU と CPU のどちらで実行されているかが表示されます。ファームウェアを `CONFIG_AI_CYCLE_PROFILE=y` でビルドし、`iproai_cycle_report()` を呼び出している場合は、推論 1 回あたりの時間と、NPU と CPU の使用率も表示されます。

</div>

![モデルの詳細、書き込み先の mfg パーティション、収まるかどうかのチェックがある AI Model ビュー](../assets/workbench/ai-model.svg)

!!! note
    IntelProCube の 1M パーティションテーブルにはモデル用の独立した領域がない（mfg が FW と重なっている）ため、IDE は書き込みを拒否します。**Partition Table** で、アプリケーションに付属するパーティションテーブル（例：独立した mfg を持つもの）を選択してから、モデルを書き込みます。
