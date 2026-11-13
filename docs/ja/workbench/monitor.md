---
title: "シリアルモニター"
description: IPRO Workbench の IPRO Monitor について、モニターを開いてボードにコマンドを入力する方法、フィルター、タイムスタンプ、保存と全ログ、シリアルプロッター、2 つ目のポートのモニター、センサーダッシュボードを説明します。
---

# シリアルモニター

**IPRO Monitor** は、下部パネルの **Terminal** にあるシリアルモニターです。ボードが UART で出力した内容を表示し、ボードに直接コマンドを入力できます。

## モニターを開いてコマンドを入力する { #open }

<div class="ipro-steps" markdown>

1. **モニターを開きます。** **Serial Monitor** をクリックします（`Cmd+Alt+M` / `Ctrl+Alt+M`）。**Build, Flash and Monitor** の場合は、書き込みの後に自動的に開きます。

    **期待される結果**：下部に **IPRO Monitor &lt;port&gt;** ターミナルが開きます。デフォルトのボーレートは 115200 です。

2. **コマンドを入力します。** モニターに入力して Enter キーを押すと送信されます。例えば `help` と入力します。

    **期待される結果**：ボードのシェルが、対応しているコマンドを返します。

3. **ボードを再起動します。** **Reset Board** をクリックすると、IDE がプローブを介してボードをリセットします。モニターは開いたままで、起動の最初の行からすべて表示されます。

</div>

!!! note
    - 書き込みやリセットの前に、IDE はすべてのモニターを閉じ、完了すると再び開きます。
    - ボーレートは `ipro.monitor.baudRate` 設定で変更します。変更すると、モニターが自動的に開き直されます。
    - モニターは、ボードが出力したアドレスを自動的にソースの位置にデコードします。[デバッグと解析](debug.md#crash-decode)を参照してください。

## モニタータブのツール { #tools }

**IPRO Monitor** タブがあるパネルの右上には、いくつかのボタンがあります。コマンドパレットと IPRO メニューにも同じコマンドがあります。

![パネル右上の 4 つのツールに 1〜4 の番号が付いた IPRO Monitor](../assets/workbench/monitor-tools.svg)

| 番号 | アイコン | コマンド | 用途 |
|---|---|---|---|
| 1 | じょうご | **Filter Monitor Output…** | 一致する行だけを表示する |
| 2 | ストップウォッチ | **Show Monitor Timestamps** | 各行の先頭に受信時刻を付ける |
| 3 | ディスク | **Save Monitor Output…** | 現在の内容をテキストファイルとして保存する |
| 4 | 折れ線グラフ | **Serial Plotter** | ボードが出力した数値を曲線としてプロットする |

### フィルター { #filter }

<div class="ipro-steps" markdown>

1. **フィルターを設定します。** じょうごのアイコン（**Filter Monitor Output…**）をクリックし、残したい内容（例：`ERROR|WARN` や `PASS|FAIL`。大文字と小文字を区別しない正規表現）を入力して Enter キーを押します。

    **期待される結果**：モニターが開き直され、タブのタイトルの末尾に `/ERROR|WARN/` が付き、一致する行だけが表示されます。クラッシュのメッセージ（MEPC、ra、stack backtrace）は常に表示されます。

2. **フィルターを解除します。** もう一度じょうごのアイコンをクリックし、入力ボックスを空にして Enter キーを押します。

</div>

フィルターは 1 行全体が届いてから判定するため、シェルのプロンプトは Enter キーを押した後に表示されます。

フィルターが変えるのは表示だけです。ファームウェアの確認、パーティションテーブルの比較、ボードテストは、引き続きボードが出力するすべての行を読み取るため、フィルターを設定したままでも動作します。

### タイムスタンプ { #timestamps }

ストップウォッチのアイコン（**Show Monitor Timestamps**）をクリックします。

**期待される結果**：各行の先頭に受信時刻（例：`[23:33:13.227]`。このコンピューターの時計による）が付きます。もう一度クリックするとオフになります。

### 保存と全ログ { #save-log }

<div class="ipro-steps" markdown>

1. **画面の内容を保存します。** ディスクのアイコン（**Save Monitor Output…**）をクリックし、保存場所を選んで **Save** をクリックします。

    **期待される結果**：「Saved the monitor output to monitor-….txt.」という通知が表示されます。保存されるのは、ターミナルが現在保持している内容（デフォルトでは最後の 1000 行）です。

2. **すべてのセッションの全ログを残します。** 設定を開いて `ipro.monitor` を検索し、**Log To File** にチェックを入れます。

    **期待される結果**：モニターの最初の行に `logging to …/build/logs/monitor-<date>-<time>.log` と表示されます。このファイルには、ボードが出力したすべての内容が、フィルターも色もない状態で記録されます。消費電力を測定するときは、このログを電流波形と並べて確認できます（[テストと測定](measure.md#power)を参照）。

</div>

## シリアルプロッター { #plotter }

<div class="ipro-steps" markdown>

1. **数値を出力します。** ファームウェアから各行に数値を出力させます。例えば `temp:23.5,hum:40`（名前:値）や `1.2 3.4`（スペースまたはカンマ区切り）です。同じ `name:value` の行は[センサーダッシュボード](#dashboard)でも表示できます。

2. **プロッターを開きます。** モニターを開いた状態で、モニタータブの折れ線グラフのアイコン（**Serial Plotter**）をクリックします。

    **期待される結果**：エディター領域に **Serial Plotter** が開き、名前ごとに 1 本の線（最大 8 本）が描かれ、上部の凡例に最新の値が表示されます。グラフにマウスポインターを合わせると、そのサンプルのすべての値が一覧表示されます。

3. **表示を操作します。** **Pause** / **Resume** をクリックすると表示を停止・再開し、**Clear** をクリックすると最初からやり直します。凡例の名前をクリックすると、その線を非表示・表示にします。**Table** をクリックすると、数値で表示します。

</div>

![名前ごとの曲線と、最新の値を示す凡例がある Serial Plotter](../assets/workbench/serial-plotter.svg)

## 別のポートを同時にモニターする { #second-port }

2 つのボードを同時に見る場合や、プローブの CCI ポートを見る場合は、次のようにします。

<div class="ipro-steps" markdown>

1. **2 つ目のモニターを開きます。** IPRO メニューから **Open Monitor on Another Port…** を選択し、ポートを選びます。

    **期待される結果**：一覧の上部にプローブのポート（UART、CCI）があります。すでにモニターが開いているポートは表示されません。ポートを選ぶと、もう 1 つ **IPRO Monitor** タブが表示されます。

2. **両方を使用します。** どちらのモニターにも入力できます。書き込みやリセットのときは、まずすべてのモニターが閉じられます。

</div>

!!! note
    Windows では、1 つの COM ポートを同時に使用できるのは 1 つのプログラムだけです。別のシリアルツールを使うには、先に IPRO Monitor を閉じてください。

## センサーダッシュボード { #dashboard }

**Sensor Dashboard** は、ボードがシリアルポートに出力する `name:value` の行（[シリアルプロッター](#plotter)と同じ形式）を読み取り、値ごとに単位付きのタイルを表示します。さらに、メーター、ランプ、傾きビュー、グループごとのグラフ、ボードのコンソールにコマンドを入力するボタンもあります。レイアウトはアプリケーションフォルダーの `dashboard.yaml` で決めます。このファイルがない場合は、すべての値にタイルとグラフが 1 つずつ表示されます。

手順では、IPRO7AI Sensor Tag で IPRO SDK V2.3.0 の [`ipro7ai_sensor_tag_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_sensor_tag_demo) を使用します。このボードのコンソールはボード自身の USB ポートにあります。

<div class="ipro-steps" markdown>

1. **書き込んでモニターを開きます。** [ボード自身の USB から書き込む](flash.md#usb-flash)の手順で、ボードの USB ポートを選択した状態で `ipro7ai_sensor_tag_demo` を IPRO7AI Sensor Tag に書き込み、**Serial Monitor** をクリックします。

    **期待される結果**：IPRO Monitor に、次のような行が 1 秒に 20 行表示されます。

    ```text
    ax:0.012 ay:-0.004 az:1.003 gx:0.3 gy:-0.1 gz:0.0 temp:27.4 batt:87 vbat:4.012 btn:0
    ```

2. **Sensor Dashboard を開きます。** IPRO メニューから **Sensor Dashboard** を選択します（またはコマンドパレットで `IPRO: Sensor Dashboard` を選択します）。モニターがまだ開いていない場合、IDE は使用中のポートでモニターを開きます。

    **期待される結果**：エディター領域に **Sensor Dashboard** が開き、`dashboard.yaml` に書かれたタイトル `IPRO7AI Sensor Tag`、「… lines a second from /dev/cu.usbmodemXXXX」という行、「Laid out by dashboard.yaml of this application」が表示されます。その下に、Acceleration と Rotation のグループ（それぞれ 3 つの値とグラフ。Acceleration には「pitch …° · roll …°」と表示される **Tilt** ビューもあります）と、Board のグループ（Temperature、メーター表示の Battery、Battery voltage、Button のランプ）が表示されます。

3. **ボードを動かします。** ボードを傾けてから、ボード上のボタンを押します。

    **期待される結果**：傾きビューがボードの動きに追従し、加速度のグラフが変化します。ボタンを押している間は Button のランプに「On」、離すと「Off」と表示されます。タイルにマウスポインターを合わせると、「&lt;name&gt;: lowest …, highest … since the page was cleared」と表示されます。

4. **コマンドボタンをクリックします。** 上部の **Beep** をクリックします。

    **期待される結果**：ボードのブザーが鳴ります。各ボタンはコンソールに 1 行を入力します。**Beep** は `beep 200` を入力します。ボタンにマウスポインターを合わせると、そのコマンドが表示されます。

5. **一時停止、クリア、ファイルの再読み込みを行います。** **Pause** をクリックするとページの表示が止まり（ボタンは **Resume** に変わります）、**Clear** をクリックすると統計を最初からやり直します。`dashboard.yaml` を変更した後は、**Read dashboard.yaml Again** をクリックします。

</div>

`dashboard.yaml` の書き方（`ipro7ai_sensor_tag_demo` のものを短くしたもの）：

```yaml title="dashboard.yaml"
title: IPRO7AI Sensor Tag
groups:
  - title: Acceleration
    unit: g
    range: [-2, 2]
    decimals: 3
    chart: true
    tilt: { x: ax, y: ay, z: az }
    values:
      - { name: ax, label: X }
      - { name: ay, label: Y }
      - { name: az, label: Z }
  - title: Board
    values:
      - { name: temp, label: Temperature, unit: "°C", decimals: 1 }
      - { name: batt, label: Battery, unit: "%", range: [0, 100], show: bar }
      - { name: btn, label: Button, show: lamp }
controls:
  - { label: Beep, send: beep 200 }
```

| キー | 意味 |
|---|---|
| `title` | ダッシュボードのタイトル。ない場合は「Sensors of &lt;application&gt;」 |
| `groups` | グループ。それぞれに `title` と `values` があり、グループ全体の `unit`、`range`、`decimals` も指定できます |
| `chart: true` | グループの値の時間変化をグラフに描きます |
| `tilt` | 3 つの加速度からピッチとロールを求めます（`x`、`y`、`z` で値の名前を指定します） |
| `values` | 値ごとに 1 つのエントリ：`name`（ボードが出力する名前）、`label`、`unit`、`decimals`、`range`、`show` |
| `show` | `value`：数値（デフォルト）、`bar`：数値と `range` 内での位置、`lamp`：0 以外のときに点灯 |
| `controls` | ボタン。`label` はボタンの文字列、`send` はコンソールに入力するコマンド |

!!! note
    - `dashboard.yaml` がないアプリケーションでは、ページに「This application has no dashboard.yaml: every value the board prints is shown. The file names groups, units, ranges and buttons.」と表示されます。
    - `dashboard.yaml` の誤りは「dashboard.yaml line N: …」として一覧表示されます。誤った部分は除外され、残りが表示されます。
    - モニターが開いていない場合、ページには「The serial monitor is not open」と表示され、**Open Monitor** が提示されます。ボードがしばらく何も出力しない場合は「Nothing from … for a while」と表示されます。
