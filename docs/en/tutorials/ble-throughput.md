---
title: "BLE Throughput Test"
description: Run ipro_throughput_test on two IPRO7AI Reef EVK boards, measure BLE throughput on the 1M and 2M PHY, and compare with the SDK's own figures.
migrate_from:
  - "tutorials.html — 教學 3"
---

# BLE Throughput Test

Two IPRO7AI Reef EVK boards run the same `ipro_throughput_test` firmware: one is the slave (peripheral), the other the master (central), and they flood each other through a custom GATT service. At the end you have throughput figures for both directions on the 1M and 2M PHY, which you can compare with the SDK's measurements under the same conditions: Reef to Reef, 1.34 Mbps on the 2M PHY and 747 kbps on the 1M PHY.

## Prerequisites { #prerequisites }

- Two IPRO7AI Reef EVK boards, each powered over USB-C and each with a USB-to-UART cable on U6 (115200 8N1).
- [First FreeRTOS Application](../get-started/first-app-freertos.md) done, and the IntelProCube v0.6.3 command-line flash tool at hand.
- One serial terminal per board in which you can type commands (see [Flashing & Serial Console](../get-started/flash-and-monitor.md)).

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Build the Reef configuration**:

    ```bash
    make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef
    ```

    Output: `apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin`. The linker's memory usage table shows about 360 KB of flash and about 205 KB of the 224 KB OCRAM region.

2. **Flash both boards**: put each board in download mode (hold SW1, tap SW2, release SW1), then flash the same file through each board's port from the IntelProCube directory:

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_throughput_test/build_reef/build_out/ipro_throughput_test_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\bluetooth\ble\ipro_throughput_test\build_reef\build_out\ipro_throughput_test_IPRO7.bin
        ```

    Both runs must end with `[All Success]`.

3. **Open both consoles and reset**: open both terminals at 115200 baud and tap SW2 on each board. About 7 seconds after reset the console prints `BLE initialized`; the controller first qualifies its 32 kHz clock source, which takes a moment. The messages below omit the level, time and thread fields at the start of each line.

4. **Connect the boards**: on the slave, type:

    ```text
    tp slave
    ```

    ```text
    TP_APP: Slave started - advertising as 'IPRO-TP-TEST'
    ```

    Then on the master:

    ```text
    tp master
    ```

    The master scans for `IPRO-TP-TEST` and connects on its own. Wait for the last line on the master before you continue:

    ```text
    TP_APP: Found target: IPRO-TP-TEST RSSI:<rssi> Addr:<address>
    TP_APP: Connected: <address>
    ...
    TP_APP: MTU exchange complete: MTU=247
    ...
    TP_APP: Notifications enabled - ready for test
    ```

5. **Set the connection interval and PHY**: on the master, type (`tp conn` counts in 1.25 ms units, so 40 is 50 ms):

    ```text
    tp conn 40 40
    tp phy 2
    tp status
    ```

    Both boards print `Connection params updated: interval=40 …` and `PHY updated: TX=2 RX=2`; `tp status` shows `Connection Interval: 50.00 ms` and `PHY: 2M`.

6. **Measure downlink (slave to master, notifications)**: type `tp stats` on the master and note the RX bytes, then on the slave type:

    ```text
    tp start 244 10
    ```

    During the test the slave prints one line per second, and a summary after 10 seconds:

    ```text
    [TP] TX: <packets> pkts, <bytes> bytes, <rate> Kbps | RX: 0 pkts, 0 bytes, 0.0 Kbps | Err: 0
    ...
    === Throughput Test Statistics ===
    Duration: <ms> ms
    TX: <packets> packets, <bytes> bytes, <rate> Kbps (<rate> KBps)
    RX: 0 packets, 0 bytes, 0.00 Kbps (0.00 KBps)
    Errors: 0
    Connection: interval=50.00ms, PHY=2M
    ==================================
    ```

    When the test ends, type `tp stats` on the master again.

7. **Measure uplink (master to slave, write without response)**: do the reverse: `tp stats` on the slave, `tp start 244 10` on the master, and `tp stats` on the slave once it ends.

8. **Repeat on the 1M PHY**: type `tp phy 1` on the master and repeat steps 6 and 7. To measure both directions at once, type `tp start 244 10` on both boards at the same time.

</div>

## Verify { #verify }

The TX rate in the sender's summary counts the packets the host stack accepted, which is within a few packets of what was delivered. The receiver's RX counters accumulate across tests, so the RX rate in its summary is not meaningful. To get the delivered rate, take the difference in RX bytes between the receiver's two `tp stats` readings:

```text
delivered rate (kbps) = (RX bytes difference × 8) ÷ test duration in ms
```

Compare the result with the reference figures in the next section. If it is far below them, check the interval and PHY with `tp status`, then see [What limits throughput](#tuning).

## Reference figures { #benchmarks }

These are the measurements published in the README of `ipro_throughput_test` (2026-10-07): two IPRO7AI Reef EVK boards, the prebuilt `link2` controller library, ATT MTU 247, DLE 251 octets, 244-byte payloads, an 8-second flood, rates counted from the packets the receiver actually got. "Down" is slave-to-master notifications; "up" is master-to-slave writes without response.

| PHY | Interval | Down / up, `CONFIG_IPRO7_BLE_HOTCODE=y` (shipped configuration) | Down / up, option off |
|---|---|---|---|
| 2M | 7.5 ms | 1055 / 1056 kbps | 891 / 957 kbps |
| 2M | 15 ms | 1180 / 1180 kbps | 921 / 930 kbps |
| 2M | 30 ms | 1315 / 1315 kbps | 737 / 788 kbps |
| 2M | 50 ms | **1342 / 1333 kbps** | 593 / 642 kbps |
| 1M | 7.5 ms | 526 / 525 kbps | 437 / 492 kbps |
| 1M | 15 ms | 656 / 656 kbps | 559 / 554 kbps |
| 1M | 30 ms | 722 / 721 kbps | 584 / 551 kbps |
| 1M | 50 ms | **747 / 746 kbps** | 535 / 568 kbps |

Both directions at once (`CONFIG_IPRO7_BLE_HOTCODE=y`, rate per direction): on the 2M PHY, 782 / 783 kbps at 50 ms, 719 / 719 kbps at 30 ms and 653 / 654 kbps at 15 ms; on the 1M PHY, 389 / 390 kbps at 50 ms. With 20-byte payloads (sized for MTU 23) on the 1M PHY the rate is about 165 kbps; the Coded S8 PHY gives about 34 kbps downlink.

## What limits throughput { #tuning }

- **Air time**: one 251-octet data PDU plus the empty acknowledgment and two inter-frame spaces takes about 1.39 ms on the 2M PHY and 2.47 ms on the 1M PHY, so 244-byte payloads top out at about 1.40 Mbps on 2M and 790 kbps on 1M.
- **Connection event length**: the controller ends each connection event early enough to schedule the next one, and the shorter the interval, the larger the share lost. A 7.5 ms interval carries only about four 2M packets (about 1.05 Mbps), so bulk transfers suit 30–50 ms intervals; when latency matters, 15 ms still gives 1.18 Mbps on 2M.
- **CPU**: with the code running from flash, handling each packet takes longer than the packet spends on air, and the CPU sets the throughput. The shipped `CONFIG_IPRO7_BLE_HOTCODE=y` runs the BLE per-packet path from OCRAM. It needs about 88 KB of OCRAM and cannot be combined with the AI+MM memory layout or with low-power settings (`CONFIG_HAL_LP`, `CONFIG_IPRO_PM_*`, `CONFIG_OCRAM_NORET_SPLIT`).
- **Check the CPU before changing buffers**: type `tp cpu` on the sender, start a test, and type `tp cpu` again when it ends. An `IDLE` share far below 50 % means the CPU is the limit; more host or controller buffers will not help.
- **Small packets**: with an ATT MTU of 23 (20-byte payloads) the interval hardly matters; expect about 165 kbps on the 1M PHY.
- **The Coded PHY is not tuned**: the application asks for a 2120 µs maximum TX time, which fits only about 27 octets per PDU on Coded S8.

`defconfig_reef` is `.config` with `CONFIG_EVB=y` replaced by the Reef board selection; the BLE settings are the same:

```ini title="apps/bluetooth/ble/ipro_throughput_test/defconfig_reef (excerpt)"
CONFIG_IPRO_BLE_CTLR_LIB="link2"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt52"
CONFIG_BT_CONN=2
CONFIG_EM_SIZE=32
CONFIG_BT_L2CAP_TX_BUF_COUNT=10
CONFIG_BT_CONN_TX_MAX=10
CONFIG_IPRO7_BLE_HOTCODE=y
CONFIG_FREERTOS_TIMER_TASK_STACK_WORDS=1024
```

## Command reference { #commands }

| Command | Description |
|---|---|
| `tp slave` | Start as peripheral and advertise `IPRO-TP-TEST` |
| `tp master [addr]` | Start as central, scan and connect; optionally to address `XX:XX:XX:XX:XX:XX` |
| `tp start [size] [sec] [interval_ms]` | Start sending from this board |
| `tp stop` | Stop the test, or disconnect when idle |
| `tp stats` | Print statistics |
| `tp status` | Print role, state, connection interval and PHY |
| `tp phy <1\|2\|3>` | Request the 1M, 2M or Coded PHY |
| `tp conn <min> <max>` | Request a connection interval in 1.25 ms units (latency 0, supervision timeout 1 s) |
| `tp interval <ms>` | Change the TX interval of a running test |
| `tp cpu` | CPU share per task since the previous `tp cpu`, and each task's minimum free stack |
| `tp help` | Print command help |

`tp start` parameters: `size` defaults to 244 (20–244 bytes); `sec` defaults to 10, `0` runs until `tp stop`; leave out `interval_ms` for flood mode, or give 1–1000 ms between packets.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `flash jedec id: 00000000` or `IPRO FLASH MATCH TYPE FAIL` while flashing | Wrong flash pin setting | Make sure the command has `--chip-variant IPRO7AI` |
| `IPRO FLASH WRITE CHECK FAIL` on every retry | Seen with some images | Set `decompress_write = false` in the IntelProCube ini, flash, then restore it |
| The master connects to another board | More than one `IPRO-TP-TEST` is advertising nearby | Switch the other test boards off, or give the slave's address: `tp master XX:XX:XX:XX:XX:XX` |
| `Cannot start test - notifications not enabled by client` | Service discovery after connecting has not finished | Wait until the master prints `Notifications enabled - ready for test` |
| Rates far below the reference figures | Unexpected interval or PHY, or a busy CPU | Check the interval and PHY with `tp status`, then the sender's `tp cpu` |
| The link drops about 1 s after `tp phy 3` (reason 0x08) | Happens occasionally when switching to the Coded PHY | Reconnect and switch again |

## Next steps { #next-steps }

- [BLE Development](../guides/ble.md): controller libraries (`link1_periph`, `link1`, `link2`, `link4`) and host settings.
- [Getting Started with LE Audio](le-audio.md): run the LE Audio headset example on the Reef.
- [Examples](../examples/index.md): the other BLE applications and their Reef configurations.
