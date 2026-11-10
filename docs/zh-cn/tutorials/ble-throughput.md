---
title: "BLE 吞吐量测试"
description: 用两块 IPRO7AI Reef EVK 运行 ipro_throughput_test，测量 1M 和 2M PHY 下的 BLE 吞吐量，并与 SDK 的实测结果对比。
migrate_from:
  - "tutorials.html — 教學 3"
---

# BLE 吞吐量测试

两块 IPRO7AI Reef EVK 烧录同一个 `ipro_throughput_test` 固件，一块作为 Slave（peripheral），另一块作为 Master（central），通过自定义 GATT 服务灌包发送数据。完成后您会得到两个方向在 1M 和 2M PHY 下的吞吐量，并能与 SDK 在相同条件下的实测值对比：Reef 对 Reef，2M PHY 可达 1.34 Mbps，1M PHY 可达 747 kbps。

## 前提条件 { #prerequisites }

- 两块 IPRO7AI Reef EVK，各自用 USB-C 供电，SW8 拨到 PWR。每块开发板的 U6 各接一个 IPRO Debug Probe（或 3.3 V USB 转 UART 线），接法见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。
- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)，并已按[准备开发环境](../get-started/environment.md#intelprocube)安装 IntelProCube 0.7.0.1 命令行烧录工具。
- 每块开发板各打开一个可输入命令的串口终端程序（115200 8N1，见[烧录与串口](../get-started/flash-and-monitor.md)）。

!!! tip "分清两块开发板的串口"
    IPRO Debug Probe 在电脑上显示为 `IPRO7 CMSIS_DAP`，有两个串口：名称以 `02` 结尾的是开发板的控制台（Reef 的 UART0），`04` 是 CCI 桥接。先只接第一块开发板的探针，记下出现的端口（macOS 执行 `ls /dev/cu.*`，Linux 执行 `ls /dev/ttyACM* /dev/ttyUSB*`，Windows 查看设备管理器中的 COM 端口），再接第二块。下文用“Slave 板”和“Master 板”称呼两块开发板，可以在两块板上分别贴上标签。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **构建 Reef 配置**：

    ```bash
    make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef
    ```

    输出：`apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin`。链接器的内存占用表显示约 360 KB Flash，以及 224 KB OCRAM 区域中的约 205 KB。

2. **烧录两块开发板**：两块开发板烧录同一个文件，各用自己的串口，一次烧一块。先让开发板进入下载模式：按住 SW1（BOOT）、按一下 SW2（RESET）、松开 SW1；板上固件带 shell 时，也可以在它的控制台输入 `reboot_dl`。然后在 IntelProCube 目录下执行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --firmware <SDK>\apps\bluetooth\ble\ipro_throughput_test\build_reef\build_out\ipro_throughput_test_IPRO7.bin
        ```

    两次烧录的输出中都要有 `[All Success]`（工具失败时也以 0 退出）。烧录前先关闭占用该串口的终端程序。

3. **打开两个控制台并复位**：两个终端都以 115200 baud 打开，按各板的 SW2。复位后约 7 秒，控制台打印 `BLE initialized`：Reef 没有 32.768 kHz 晶振，控制器先检查 32 kHz 时钟源，打印 `XTAL32K rejected` 后改用 RC32K，所以需要一点时间。以下信息省略了行首的级别、时间等字段。

4. **建立连接**：先在 Slave 板输入：

    ```text
    tp slave
    ```

    ```text
    TP_APP: Slave started - advertising as 'IPRO-TP-TEST'
    ```

    再在 Master 板输入：

    ```text
    tp master
    ```

    Master 会扫描 `IPRO-TP-TEST` 并自动连接。等 Master 打印出最后一行再继续：

    ```text
    TP_APP: Found target: IPRO-TP-TEST RSSI:<信号强度> Addr:<地址>
    TP_APP: Connected: <地址>
    ...
    TP_APP: MTU exchange complete: MTU=247
    ...
    TP_APP: Notifications enabled - ready for test
    ```

5. **设置连接参数和 PHY**：在 Master 板输入（`tp conn` 的单位是 1.25 ms，40 即 50 ms）：

    ```text
    tp conn 40 40
    tp phy 2
    tp status
    ```

    两块开发板都会打印 `Connection params updated: interval=40 …` 和 `PHY updated: TX=2 RX=2`；`tp status` 显示 `Connection Interval: 50.00 ms` 和 `PHY: 2M`。

6. **测量下行（Slave → Master，notification）**：先在 Master 板输入 `tp stats` 并记下 RX bytes，再在 Slave 板输入：

    ```text
    tp start 244 10
    ```

    测试期间 Slave 每秒打印一行统计，10 秒后打印汇总：

    ```text
    [TP] TX: <数据包数> pkts, <字节数> bytes, <速率> Kbps | RX: 0 pkts, 0 bytes, 0.0 Kbps | Err: 0
    ...
    === Throughput Test Statistics ===
    Duration: <毫秒> ms
    TX: <数据包数> packets, <字节数> bytes, <速率> Kbps (<速率> KBps)
    RX: 0 packets, 0 bytes, 0.00 Kbps (0.00 KBps)
    Errors: 0
    Connection: interval=50.00ms, PHY=2M
    ==================================
    ```

    测试结束后再在 Master 板输入一次 `tp stats`。

7. **测量上行（Master → Slave，write without response）**：反过来做一次：先在 Slave 板输入 `tp stats`，再在 Master 板输入 `tp start 244 10`，结束后在 Slave 板再输入 `tp stats`。

8. **改用 1M PHY 再测一次**：在 Master 板输入 `tp phy 1`，重复步骤 6 和 7。要同时测量两个方向，就在两块开发板上同时输入 `tp start 244 10`。

</div>

## 验证结果 { #verify }

发送端汇总中的 TX 速率，是根据 Host 协议栈接受的数据包数换算而来，与实际送达的只差几个数据包。接收端的 RX 计数器会跨测试累加，汇总中的 RX 速率没有意义。要算出实际送达的速率，请用接收端在测试前后两次 `tp stats` 的 RX bytes 差值：

```text
送达速率 (kbps) = (RX bytes 差值 × 8) ÷ 测试毫秒数
```

把结果与下一节的参考值对比。数值远低于参考值时，先用 `tp status` 确认连接间隔和 PHY，再参阅[影响吞吐量的因素](#tuning)。

## 参考值 { #benchmarks }

以下是 SDK 中 `ipro_throughput_test` README 附带的实测值（2026-10-07）：两块 IPRO7AI Reef EVK、预编译 `link2` 控制器库、ATT MTU 247、DLE 251 octets、244 bytes 有效载荷、灌包 8 秒，速率按接收端实际收到的数据包计算。“下行”为 Slave → Master 的 notification，“上行”为 Master → Slave 的 write without response。

| PHY | 连接间隔 | 下行／上行，`CONFIG_IPRO7_BLE_HOTCODE=y`（附带配置） | 下行／上行，关闭该选项 |
|---|---|---|---|
| 2M | 7.5 ms | 1055／1056 kbps | 891／957 kbps |
| 2M | 15 ms | 1180／1180 kbps | 921／930 kbps |
| 2M | 30 ms | 1315／1315 kbps | 737／788 kbps |
| 2M | 50 ms | **1342／1333 kbps** | 593／642 kbps |
| 1M | 7.5 ms | 526／525 kbps | 437／492 kbps |
| 1M | 15 ms | 656／656 kbps | 559／554 kbps |
| 1M | 30 ms | 722／721 kbps | 584／551 kbps |
| 1M | 50 ms | **747／746 kbps** | 535／568 kbps |

两个方向同时发送时（`CONFIG_IPRO7_BLE_HOTCODE=y`，每个方向的速率）：2M PHY、50 ms 为 782／783 kbps，30 ms 为 719／719 kbps，15 ms 为 653／654 kbps；1M PHY、50 ms 为 389／390 kbps。以 20 bytes 有效载荷（对应 MTU 23）在 1M PHY 下测试时约 165 kbps，Coded S8 PHY 下行约 34 kbps。

## 影响吞吐量的因素 { #tuning }

- **空中时间**：一个 251 octets 的数据 PDU 加上空的确认包和两段帧间间隔，在 2M PHY 下约 1.39 ms、1M PHY 下约 2.47 ms，所以 244 bytes 有效载荷的上限约为 2M 1.40 Mbps、1M 790 kbps。
- **连接事件长度**：控制器会提前结束每个连接事件以安排下一个，间隔越短，损失的比例越高。7.5 ms 间隔只容得下约四个 2M 数据包（约 1.05 Mbps），所以大量数据传输适合 30–50 ms 间隔；在意延迟时用 15 ms，2M 仍有 1.18 Mbps。
- **CPU**：代码在 Flash 上执行时，每个数据包的处理时间比数据包在空中的时间还长，吞吐量就受限于 CPU。附带配置中的 `CONFIG_IPRO7_BLE_HOTCODE=y` 把 BLE 每个数据包的处理路径放到 OCRAM 中执行；这需要约 88 KB 的 OCRAM，而且不能与 AI+MM 内存配置或低功耗配置（`CONFIG_HAL_LP`、`CONFIG_IPRO_PM_*`、`CONFIG_OCRAM_NORET_SPLIT`）同时使用。
- **先看 CPU，再调缓冲区**：在发送端先输入 `tp cpu`，开始测试，结束后再输入一次 `tp cpu`。`IDLE` 的比例远低于 50% 表示 CPU 是瓶颈，加大主机或控制器的缓冲区也没有帮助。
- **小数据包**：ATT MTU 23（20 bytes 有效载荷）时连接间隔几乎没有影响，1M PHY 约 165 kbps。
- **Coded PHY 未调优**：应用要求的最大发送时间为 2120 µs，在 Coded S8 下每个 PDU 只放得下约 27 octets。

`defconfig_reef` 只是把 `.config` 中的 `CONFIG_EVB=y` 换成 Reef 板级配置，两者的 BLE 配置相同：

```ini title="apps/bluetooth/ble/ipro_throughput_test/defconfig_reef（节选）"
CONFIG_IPRO_BLE_CTLR_LIB="link2"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt52"
CONFIG_BT_CONN=2
CONFIG_EM_SIZE=32
CONFIG_BT_L2CAP_TX_BUF_COUNT=10
CONFIG_BT_CONN_TX_MAX=10
CONFIG_IPRO7_BLE_HOTCODE=y
CONFIG_FREERTOS_TIMER_TASK_STACK_WORDS=1024
```

## 命令参考 { #commands }

| 命令 | 说明 |
|---|---|
| `tp slave` | 以 peripheral 角色启动并开始广播 `IPRO-TP-TEST` |
| `tp master [addr]` | 以 central 角色启动、扫描并连接；可指定地址 `XX:XX:XX:XX:XX:XX` |
| `tp start [size] [sec] [interval_ms]` | 由本板开始发送 |
| `tp stop` | 停止测试；不在测试中时则断开连接 |
| `tp stats` | 显示统计 |
| `tp status` | 显示角色、状态、连接间隔和 PHY |
| `tp phy <1\|2\|3>` | 请求 1M、2M 或 Coded PHY |
| `tp conn <min> <max>` | 请求连接间隔，单位 1.25 ms（latency 0、supervision timeout 1 秒） |
| `tp interval <ms>` | 修改进行中测试的发送间隔 |
| `tp cpu` | 自上次 `tp cpu` 以来各任务的 CPU 占比和最小剩余栈 |
| `tp help` | 显示命令说明 |

`tp start` 的参数：`size` 默认 244（20–244 bytes）；`sec` 默认 10，`0` 表示一直持续到 `tp stop`；省略 `interval_ms` 时为灌包模式（flood），指定 1–1000 时则为数据包间隔。

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| 烧录时出现 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` | Flash 引脚配置不符，或开发板未进入下载模式 | 确认命令中有 `--chip-variant IPRO7AI`，并先进入下载模式 |
| 烧录时无法打开串口 | 终端程序还开着同一个端口 | 先关闭终端程序再烧录 |
| 每次重试都出现 `IPRO FLASH WRITE CHECK FAIL` | 某些镜像文件会出现这种情况 | 在 IntelProCube 的 ini 中设置 `decompress_write = false` 后烧录，完成后改回 |
| Master 连到了别的开发板 | 附近有多个 `IPRO-TP-TEST` 在广播 | 关闭其他测试板，或用 `tp master XX:XX:XX:XX:XX:XX` 指定 Slave 的地址 |
| `Cannot start test - notifications not enabled by client` | 连接后的服务发现尚未完成 | 等 Master 打印 `Notifications enabled - ready for test` 后再开始 |
| 速率远低于参考值 | 连接间隔或 PHY 不符合预期，或 CPU 满载 | 用 `tp status` 确认间隔和 PHY，再用 `tp cpu` 检查发送端 |
| `tp phy 3` 后约 1 秒断开连接（reason 0x08） | 切换到 Coded PHY 时偶尔发生 | 重新连接后再切换一次 |

## 下一步 { #next-steps }

- [BLE 开发](../guides/ble.md)：控制器库（`link1_periph`、`link1`、`link2`、`link4`）与 Host 配置。
- [LE Audio 入门](le-audio.md)：在 Reef 上运行 LE Audio 耳机示例。
- [示例](../examples/index.md)：其他 BLE 应用及其 Reef 配置。
- [测试你的应用](testing.md)：用 `serial_monitor.py` 向每块开发板发送命令并等待结果，把测量写成脚本。
