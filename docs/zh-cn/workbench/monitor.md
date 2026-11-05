---
title: "串口监视"
description: IPRO Workbench 中的 IPRO Monitor：打开监视器并向开发板输入命令，过滤、时间戳、保存与完整日志、串口绘图器，以及同时监视第二个端口。
---

# 串口监视

**IPRO Monitor** 是底部面板 **Terminal** 中的串口监视器。它显示开发板通过 UART 打印的内容，你也可以直接向开发板输入命令。

## 打开监视器并输入命令 { #open }

<div class="ipro-steps" markdown>

1. **打开监视器。** 点击 **Serial Monitor**（`Cmd+Alt+M` / `Ctrl+Alt+M`）。使用 **Build, Flash and Monitor** 时，监视器会在烧录完成后自动打开。

    **应看到**：底部打开一个 **IPRO Monitor &lt;port&gt;** 终端，默认波特率为 115200。

2. **输入命令。** 在监视器中输入命令并按 Enter 发送，例如 `help`。

    **应看到**：开发板的 shell 回复它支持的命令。

3. **重启开发板。** 点击 **Reset Board**：IDE 通过探针复位开发板，监视器保持打开，并从第一行启动信息开始显示全部内容。

</div>

!!! note
    - 烧录或复位前，IDE 会关闭所有监视器，完成后再重新打开。
    - 在 `ipro.monitor.baudRate` 设置项中修改波特率；修改后监视器会自动重新打开。
    - 监视器会自动将开发板打印的地址解码为源代码位置；请参阅[调试与分析](debug.md#crash-decode)。

## 监视器标签页上的工具 { #tools }

**IPRO Monitor** 标签页所在面板的右上角有几个按钮；命令面板和 IPRO 菜单中也有相同的命令。

![IPRO Monitor，面板右上角的四个工具以 1 到 4 编号](../assets/workbench/monitor-tools.svg)

| 编号 | 图标 | 命令 | 用途 |
|---|---|---|---|
| 1 | 漏斗 | **Filter Monitor Output…** | 只显示匹配的行 |
| 2 | 秒表 | **Show Monitor Timestamps** | 在每行前面加上接收该行的时间 |
| 3 | 磁盘 | **Save Monitor Output…** | 将当前内容保存为文本文件 |
| 4 | 折线图 | **Serial Plotter** | 将开发板打印的数值绘制成曲线 |

### 过滤 { #filter }

<div class="ipro-steps" markdown>

1. **设置过滤条件。** 点击漏斗图标（**Filter Monitor Output…**），输入要保留的内容，例如 `ERROR|WARN` 或 `PASS|FAIL`（正则表达式，不区分大小写），然后按 Enter。

    **应看到**：监视器重新打开，标签页标题末尾加上 `/ERROR|WARN/`，只显示匹配的行。崩溃信息（MEPC、ra、stack backtrace）始终显示。

2. **清除过滤。** 再次点击漏斗图标，清空输入框后按 Enter。

</div>

过滤要等整行到达后才对该行进行判断，因此 shell 提示符要在你按下 Enter 之后才会显示。

!!! tip
    固件核对、分区表比对和板上测试都会读取监视器收到的每一行。执行其中任何一项之前，请先清除过滤。

### 时间戳 { #timestamps }

点击秒表图标（**Show Monitor Timestamps**）。

**应看到**：每行开头显示接收该行的时间，例如 `[23:33:13.227]`（以本机时钟为准）。再次点击即可关闭。

### 保存与完整日志 { #save-log }

<div class="ipro-steps" markdown>

1. **保存屏幕上的内容。** 点击磁盘图标（**Save Monitor Output…**），选择保存位置并点击 **Save**。

    **应看到**：通知显示“Saved the monitor output to monitor-….txt.”保存的是终端当前保留的内容（默认为最后 1000 行）。

2. **保留每次会话的完整日志。** 打开设置，搜索 `ipro.monitor`，勾选 **Log To File**。

    **应看到**：监视器的第一行显示 `logging to …/build/logs/monitor-<date>-<time>.log`。该文件包含开发板打印的全部内容，不经过滤，也不带颜色。测量功耗时，可以将此日志与电流曲线对齐（请参阅[测试与测量](measure.md#power)）。

</div>

## 串口绘图器 { #plotter }

<div class="ipro-steps" markdown>

1. **打印数值。** 让固件在每一行打印数值，例如 `temp:23.5,hum:40`（名称:数值）或 `1.2 3.4`（以空格或逗号分隔）。

2. **打开绘图器。** 在监视器打开的情况下，点击监视器标签页上的折线图图标（**Serial Plotter**）。

    **应看到**：编辑区中打开 **Serial Plotter**，每个名称一条曲线（最多 8 条），顶部的图例显示最新的数值。将鼠标悬停在图表上，可列出该采样点的所有数值。

3. **控制显示。** 点击 **Pause** / **Resume** 冻结或恢复显示，点击 **Clear** 重新开始；点击图例中的名称可隐藏或显示该曲线；点击 **Table** 改为查看数值。

</div>

![Serial Plotter，每个名称一条曲线，图例显示最新的数值](../assets/workbench/serial-plotter.svg)

## 同时监视另一个端口 { #second-port }

要同时查看两块开发板，或查看探针的 CCI 端口：

<div class="ipro-steps" markdown>

1. **打开第二个监视器。** 在 IPRO 菜单中选择 **Open Monitor on Another Port…**，然后选择端口。

    **应看到**：探针的端口（UART、CCI）位于列表顶部；已经打开监视器的端口不会列出。选择端口后，会出现另一个 **IPRO Monitor** 标签页。

2. **同时使用。** 两个监视器中都可以输入。烧录或复位时，所有监视器都会先关闭。

</div>

!!! note
    在 Windows 上，一个 COM 端口同一时间只能被一个程序使用。要使用其他串口工具，请先关闭 IPRO Monitor。
