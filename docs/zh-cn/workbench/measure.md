---
title: "测试与测量"
description: 在 IPRO Workbench 中于开发板上运行 Unity 测试并在 Testing 视图中查看结果，以 Direct Test Mode 测量 BLE 射频，以及分析 PPK2 功耗记录并估算电池续航。
---

# 测试与测量

在开发板上运行测试、测量 BLE 射频，以及查看功耗曲线。

## 板上测试 { #board-tests }

当应用程序使用 SDK 的 Unity 测试框架时（例如 `ipro_unit_test`），开发板打印的测试结果会汇总到 IDE 的 **Testing** 视图中。

<div class="ipro-steps" markdown>

1. **运行测试。** 选择应用程序并烧录一次后，点击侧边栏 **Board** 视图顶部的烧杯图标（**Run Tests on Board**）。

    **应看到**：通知显示“Resetting the board with the monitor open…”，开发板通过探针重新启动。左侧切换到 **Testing** 视图：**Test Runs** 列出本次运行（例如“ipro_unit_test 2:10:16 PM”），每个测试前面有通过、失败或跳过的符号；**Test Explorer** 中的 **IPRO Board Tests** 列出每个测试组（utils、memory、rtos…）。

2. **打开失败的测试。** 双击失败的测试，即可打开该测试的源代码并定位到失败的那一行。

3. **每次运行后的结果。** 运行 **Build, Flash and Monitor** 时，结果也会自动进入 **Testing** 视图。

</div>

![Testing 视图中的板上测试结果，每个测试都有一个表示结果的符号](../assets/workbench/board-tests.svg)

!!! note
    - **Testing** 视图读取的是开发板启动后打印的测试行，因此监视器必须接在探针的 UART（控制台）端口上，并且不能开启过滤。
    - 开发板没有重启时，IDE 会提示“The board did not restart. Is the monitor on the console port of an IPRO Debug Probe?”

## 射频测试（BLE DTM） { #rf-test }

**RF Test** 使用 INTELPRO 提供的 MFG 固件，让开发板以 BLE Direct Test Mode 发射或接收，用于频谱分析仪或无线综测仪的测量，或测量两块开发板之间的误包率（PER）。

<div class="ipro-steps" markdown>

1. **检查固件。** 将 MFG 固件烧录到开发板并打开串口监视器。在 IPRO 菜单中选择 **RF Test (DTM)…**，然后点击 **Check Firmware**。MFG 固件不包含在 IPRO SDK 中，请向 INTELPRO 销售代表索取。

    **应看到**：“MFG firmware 1.01”。开发板没有响应时，显示“The board did not answer. Is it running the MFG firmware?”

2. **发射或接收。** 选择信道、PHY、长度、载荷和发射功率，点击 **Transmit** 或 **Receive**，点击 **Stop** 结束。

    **应看到**：发射时显示类似“Transmitting on 2402 MHz (1M, 37 bytes, every 625 µs).”的消息。停止接收后显示“Received M packets in N s; against a DTM transmitter at the standard rate that is a PER of X%.”

    只点击 **Receive** 时，PER 是根据接收时间估算的，而接收时间也包含开发板开始接收之前的一小段时间，因此结果会比实际值略高（10 秒内约高 1–3%）。要得到准确的 PER，请按下一步用两块开发板测量。

3. **用两块开发板测量 PER。** 将两块开发板连接到同一台计算机，第二块开发板也烧录 MFG 固件，并点击 **Open Monitor on Another Port…** 打开它的监视器。在 **Packet error rate between two boards** 中选择接收端和秒数，然后点击 **Measure PER**。

    **应看到**：结果表格新增一行：时间、信道、PHY、发送数（预期）、接收数和 PER。

    两块开发板连接在不同计算机上时，在每台计算机上各打开 IPRO Workbench：先在一台上选择信道并点击 **Transmit**，再在另一台上选择同一信道并点击 **Receive**，几秒后点击 **Stop**。接收端会显示收到的数据包数量和估算的 PER。

</div>

!!! tip
    附近有 Wi-Fi 时，与 Wi-Fi 信道重叠的 BLE 信道会大量丢包（例如 2440 MHz 附近）。测量 PER 时，请选择避开附近 Wi-Fi 的信道，例如 2478 MHz。

!!! note
    每次开始测试时，MFG 固件都要先启动 BLE 控制器（约 2.5 秒）；IDE 会等它回复后才开始。

## 功耗 { #power }

**Power** 读取 Nordic Power Profiler Kit II（PPK2）的电流记录，计算平均电流、峰值电流、睡眠电流和电荷量，并估算开发板使用一颗 CR2032 能运行多久。

<div class="ipro-steps" markdown>

1. **打开记录。** 右键点击应用程序，选择 **Power…**，点击 **Open…**，然后选择 Power Profiler 保存的 `.ppk2` 或 CSV 文件。

    **应看到**：时长、平均值、峰值、睡眠底电流（第 1 百分位）和电荷量，以及在“CR2032 (225 mAh) at this average”下能持续多久；下方是电流曲线，可以切换为 **Log scale**。

2. **将鼠标悬停在曲线上。**

    **应看到**：该时刻的时间、平均电流和范围，例如“8.128 s, Average 282.3 µA, 271.4 µA – 292.5 µA”。

3. **测量一段区间。** 在曲线上按住并拖过一段区间。

    **应看到**：下方显示该区间的平均电流和电荷量，例如“3.251 s to 8.128 s: average 11.91 mA, 16.1279 µAh.”

4. **对齐监视器日志。** 如果记录期间串口监视器开启了 **Log To File** 和时间戳，请在 **Monitor log** 中选择该日志。

    **应看到**：每一行日志都在曲线上方以一条短刻度线标出；将鼠标悬停在刻度线上，会显示该时刻的电流和日志文字，由此可以看出“哪一段代码耗了多少电”。

</div>

![Power 视图，包含电流曲线及其统计数据：时长、平均值、峰值、睡眠底电流、电荷量和 CR2032 续航](../assets/workbench/power.svg)
