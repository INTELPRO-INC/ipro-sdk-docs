---
title: "テストと測定"
description: IPRO Workbench で、ボード上で Unity テストを実行して Testing ビューで結果を確認し、Direct Test Mode で BLE の RF を測定し、PPK2 の消費電力の記録を電池寿命の見積もりとともに解析します。
---

# テストと測定

ボード上でのテストの実行、BLE の RF の測定、消費電流の波形の確認について説明します。

## ボードテスト { #board-tests }

アプリケーションが SDK の Unity テストフレームワークを使用している場合（例：`ipro_unit_test`）、ボードが出力したテスト結果は IDE の **Testing** ビューに集められます。

<div class="ipro-steps" markdown>

1. **テストを実行します。** アプリケーションを選択して一度書き込んだ後、サイドバーの **Board** ビュー上部にあるビーカーのアイコン（**Run Tests on Board**）をクリックします。

    **期待される結果**：「Resetting the board with the monitor open…」という通知が表示され、ボードがプローブを介して再起動します。左側が **Testing** ビューに切り替わり、**Test Runs** に今回の実行（例：「ipro_unit_test 2:10:16 PM」）が表示され、各テストの前に合格、失敗、スキップの記号が付きます。**Test Explorer** では、**IPRO Board Tests** にすべてのテストグループ（utils、memory、rtos…）が一覧表示されます。

2. **失敗したテストを開きます。** 失敗したテストをダブルクリックすると、そのテストのソースコードが失敗した行で開きます。

3. **実行のたびに結果が反映されます。** **Build, Flash and Monitor** を実行したときも、結果は自動的に **Testing** ビューに送られます。

</div>

![Testing ビューのボードテストの結果。各テストに記号が付いている](../assets/workbench/board-tests.svg)

!!! note
    - **Testing** ビューは、ボードが起動後に出力するテストの行を読み取ります。そのため、モニターはプローブの UART（コンソール）ポートで開いている必要があり、フィルターを設定していてはいけません。
    - ボードが再起動しない場合、IDE は「The board did not restart. Is the monitor on the console port of an IPRO Debug Probe?」と表示します。

## RF テスト（BLE DTM） { #rf-test }

**RF Test** は、INTELPRO の MFG ファームウェアを使用して、ボードに BLE Direct Test Mode で送信または受信をさせます。スペクトラムアナライザーや無線通信テスターでの測定、または 2 台のボード間のパケットエラー率（PER）の測定に使用します。

<div class="ipro-steps" markdown>

1. **ファームウェアを確認します。** ボードに MFG ファームウェアを書き込み、シリアルモニターを開きます。IPRO メニューから **RF Test (DTM)…** を選択し、**Check Firmware** をクリックします。MFG ファームウェアは IPRO SDK に含まれていません。INTELPRO の営業担当者にお問い合わせください。

    **期待される結果**：「MFG firmware 1.01」と表示されます。ボードが応答しない場合は、「The board did not answer. Is it running the MFG firmware?」と表示されます。

2. **送信または受信します。** チャネル、PHY、長さ、ペイロード、送信電力を選択し、**Transmit** または **Receive** をクリックします。終了するには **Stop** をクリックします。

    **期待される結果**：送信中は「Transmitting on 2402 MHz (1M, 37 bytes, every 625 µs).」のようなメッセージが表示されます。受信を停止すると、「Received M packets in N s; against a DTM transmitter at the standard rate that is a PER of X%.」と表示されます。

    **Receive** だけをクリックした場合、PER は受信時間から推定されます。この受信時間には、ボードが受信を開始する前のわずかな時間も含まれるため、実際の値よりやや高く出ます（10 秒間で約 1〜3% 高くなります）。正確な PER を得るには、次の手順のように 2 台のボードで測定します。

3. **2 台のボードで PER を測定します。** 両方のボードを同じコンピューターに接続し、2 台目のボードにも MFG ファームウェアを書き込み、**Open Monitor on Another Port…** をクリックしてそのモニターを開きます。**Packet error rate between two boards** で受信側と秒数を選択し、**Measure PER** をクリックします。

    **期待される結果**：結果の表に、時刻、チャネル、PHY、送信数（期待値）、受信数、PER の行が追加されます。

    2 台のボードが別々のコンピューターに接続されている場合は、それぞれのコンピューターで IPRO Workbench を開きます。まず一方でチャネルを選んで **Transmit** をクリックし、次にもう一方で同じチャネルを選んで **Receive** をクリックし、数秒後に **Stop** をクリックします。受信側に、受信したパケット数と推定 PER が表示されます。

</div>

!!! tip
    近くに Wi-Fi があると、Wi-Fi のチャネルと重なる BLE チャネル（例：2440 MHz 付近）では多くのパケットが失われます。PER を測定するときは、近くの Wi-Fi と重ならないチャネル（例：2478 MHz）を選んでください。

!!! note
    テストを開始するたびに、MFG ファームウェアはまず BLE コントローラーを起動する必要があります（約 2.5 秒）。IDE はその応答を待ってからテストを開始します。

## 消費電力 { #power }

**Power** は、Nordic Power Profiler Kit II（PPK2）の電流の記録を読み込み、平均、ピーク、スリープ電流、電荷量を算出し、CR2032 でボードがどれだけ動作するかを見積もります。

<div class="ipro-steps" markdown>

1. **記録を開きます。** アプリケーションを右クリックして **Power…** を選択し、**Open…** をクリックして、Power Profiler で保存した `.ppk2` または CSV ファイルを選択します。

    **期待される結果**：記録時間、平均、ピーク、スリープ時の下限（1 パーセンタイル）、電荷量と、「CR2032 (225 mAh) at this average」での持続時間が表示されます。その下には電流波形があり、**Log scale** に切り替えられます。

2. **波形にマウスポインターを合わせます。**

    **期待される結果**：その時点の時刻、平均電流、範囲が表示されます。例：「8.128 s, Average 282.3 µA, 271.4 µA – 292.5 µA」。

3. **区間を測定します。** 波形上の区間をドラッグします。

    **期待される結果**：その区間の平均電流と電荷量が下に表示されます。例：「3.251 s to 8.128 s: average 11.91 mA, 16.1279 µAh.」

4. **モニターログを重ねて表示します。** 記録中にシリアルモニターの **Log To File** とタイムスタンプがオンになっていた場合は、**Monitor log** でそのログを選択します。

    **期待される結果**：各ログ行が、波形の上に短い目盛りで示されます。目盛りにマウスポインターを合わせると、その時点の電流とログのテキストが表示され、「コードのどの部分がどれだけ電力を使ったか」を確認できます。

</div>

![電流波形とその統計（記録時間、平均、ピーク、スリープ時の下限、電荷量、CR2032 での寿命）がある Power ビュー](../assets/workbench/power.svg)
