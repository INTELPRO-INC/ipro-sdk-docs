---
title: "第一个 BLE 应用"
description: 在 IPRO7AI Reef EVK 上运行 ipro_ble_remote：首次连同 boot2 和 A/B 分区表一起烧录、用手机操作 GATT 服务、修改设备名称并在连接时发出提示音，最后通过 BLE OTA 更新固件。
migrate_from:
  - "tutorials.html — 教學 1"
---

# 第一个 BLE 应用

完成本教程后，IPRO7AI Reef EVK 会运行 SDK 的 GATT 参考应用 `ipro_ble_remote`：手机可以点亮板上的 RGB LED、接收按键通知，并与开发板互相发送文字。接着您将修改代码，把广播名称改为 `IPRO-Hello`、让开发板在手机连上时发出短促的哔声，最后不接线，通过 BLE OTA 把新固件送进开发板。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK：SW7 拨到 CAM、SW8 拨到 PWR，用 USB-C 供电；U6 接 IPRO Debug Probe 或 3.3 V USB 转 UART 线（115200 8N1，接法见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。可另接 OV5640 FLEX-24 摄像头模组和 microSD 卡，用来试用拍照功能。
- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)：工具链位于 `/opt/toolchain/riscv_ipro7/`，`make` 能构建 SDK 应用。
- IntelProCube v0.6.3（需另行获取）：命令行烧录工具 `ipro_iot_tool_macos`、`ipro_iot_tool_linux` 或 `ipro_iot_tool.exe`，以及它附带的 boot2 镜像文件 `chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin`。
- 一部手机，二选一：
    - Android：应用目录中附带的演示 App `apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk`。
    - Android 或 iOS：可读写 GATT 特征值的 BLE 工具 App，例如 nRF Connect 或 LightBlue。以下步骤以这类工具为例说明。
- BLE OTA（步骤 10–12）：一台带 Bluetooth LE 的 macOS 或 Linux 电脑，Python 3 和 `bleak` 包。

!!! note "Reef 配置使用 2 MB Flash、boot2 和 A/B 分区表"
    `ipro_ble_remote` 的 Reef 配置 `defconfig_reef` 按 2 MB Flash 链接（`CONFIG_IPRO7_FLASH_2M=y`）并启用 BLE OTA（`CONFIG_IPRO_BLE_REMOTE_OTA=y`）。烧录时要一并写入 boot2 和应用附带的 A/B 分区表 `partition_cfg_2M_remote_ab.toml`：FW A（0x12000，824 KB）是运行区，FW B（0xE0000，512 KB）暂存 OTA 包。`build_freertos.sh` 无法带 `--boot2`，所以本教程直接使用烧录工具。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **构建 Reef 配置**：在 SDK 根目录执行：

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    `DEFCONFIG=` 不会改动 `.config`，构建目录是 `build_reef/`。成功时链接器最后打印内存占用表（Flash 一行显示 `2 MB`），输出文件为 `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`。不加 `DEFCONFIG=` 的 `make` 构建的是 IPRO7 EVB 版本，不能用于 Reef。

2. **让 Reef 进入下载模式**：按住 SW1（BOOT），按一下 SW2（RESET），再松开 SW1。板上固件已有 shell 时，也可以在控制台输入 `reboot_dl`。进入下载模式后控制台没有任何输出。

3. **烧录 boot2、A/B 分区表和固件**：在 IntelProCube 目录下执行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin `
            --pt <SDK>\apps\bluetooth\ble\ipro_ble_remote\partition_cfg_2M_remote_ab.toml `
            --firmware <SDK>\apps\bluetooth\ble\ipro_ble_remote\build_reef\build_out\ipro_ble_remote_IPRO7.bin
        ```

    `--chip-variant IPRO7AI` 选择 Reef（QFN56）的 Flash 引脚。工具失败时也会以 0 退出，请确认输出中有 `[All Success]`。使用 IPRO Debug Probe 时，端口是名称以 `02` 结尾的那一个。之后每次重新烧录这个应用都使用同一条完整命令，A/B 布局才会保持一致。

4. **打开控制台并复位**：以 115200 baud 打开 U6 的串口（方法见[烧录与串口](../get-started/flash-and-monitor.md)），按一下 SW2（RESET）。控制台先出现 boot2 的信息，再出现应用的启动信息（行首的级别、时间等字段已省略）：

    ```text
    [BOOT2] IPRO7 Boot2 v0.5.2
    ...
    REMOTE_APP: [BLE] Initialized
    REMOTE_APP: [BLE] All services initialized
    REMOTE_APP: [BLE] Advertising: IPRO-Remote
    ```

5. **从手机连接**：
    - 使用附带的 Android App：把 `ipro_remote_demo.apk` 复制到手机后打开安装（需要允许安装未知来源的应用），或在电脑上执行 `adb install apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk`。
    - 使用 BLE 工具 App：扫描并连接 `IPRO-Remote`。

    连上后控制台打印：

    ```text
    REMOTE_APP: Connected! Peer: <手机地址>
    ```

6. **操作 GATT 服务**：在 BLE 工具 App 中找到下列特征值并操作：

    | 操作 | 特征值 | 板上结果 |
    |---|---|---|
    | 写入 `01` | LED State `0xFF11` | WS2812 LED 点亮（默认白色），控制台打印 `[LED] State: ON` |
    | 写入 `00 FF 00` | LED Colour `0xFF81` | LED 变为绿色（3 bytes：R、G、B） |
    | 开启通知后按 SW3 | Button State `0xFF21` | 手机收到 `01`（按下）和 `00`（松开） |
    | 开启通知 | UART TX `0xFF41` | 手机收到 `Welcome to IPRO Remote!` |
    | 写入文字 `hello` | UART RX `0xFF42` | 控制台打印 `[UART RX] hello`，手机收到 `Echo: hello` |
    | 写入 `E8 03 2C 01 1E` | Tone `0xFF84` | 扬声器（或插在 J2 上的耳机）发出 1 kHz、300 ms 的声音（频率、时长均为 little-endian u16，最后一个 byte 是音量 %） |

    短按 SW1（BOOT）会让应用拍一张照片（需接摄像头；插着 microSD 卡时另存到 `sd:/REMOTE/`），测试按键时请使用 SW3、SW4 或 SW5。控制台的 `reef status` 命令会列出开发板、LED、摄像头和温度状态。

7. **修改代码**：编辑 `apps/bluetooth/ble/ipro_ble_remote/src/app/remote_app.c` 中的三处。

    文件开头已在 `CONFIG_IPRO7AI_REEF` 条件内引入 `remote_reef.h`，在它下面加入声明了 `reef_hw_tone()` 的 `reef_hw.h`：

    ```c title="src/app/remote_app.c"
    #if defined(CONFIG_IPRO7AI_REEF)
    #include "remote_reef.h"
    #include "reef_hw.h"
    #endif
    ```

    更改广播名称：

    ```c title="src/app/remote_app.c"
    #define DEVICE_NAME "IPRO-Hello"
    ```

    在 `connected_cb()` 中 `Connected! Peer` 那行日志之后加入提示音：

    ```c title="src/app/remote_app.c"
        IPRO_LOGI(LOG_TAG, "Connected! Peer: %s", addr_str);

    #if defined(CONFIG_IPRO7AI_REEF)
        /* 手机连上时，扬声器和耳机孔发出 1 kHz、150 ms 的短促哔声 */
        (void)reef_hw_tone(1000, 150, 30);
    #endif
    ```

    `reef_hw_tone()` 只是把请求交给负责 Reef 硬件的任务就返回，可以安全地在 BLE 连接回调中调用。这个应用以 `-Werror` 编译，任何警告都会导致构建失败。

8. **重新构建并烧录**：重复步骤 1 的构建命令（只会重新编译修改过的文件），在控制台输入 `reboot_dl`，再用步骤 3 的命令烧录。

9. **再次连接**：按 SW2 复位后，控制台打印 `REMOTE_APP: [BLE] Advertising: IPRO-Hello`。在手机上重新扫描并连接 `IPRO-Hello`，连上的瞬间 Reef 会哔一声。

10. **准备 OTA 工具**：之后的更新改走 BLE，无需连接 U6。在 SDK 根目录创建 Python 虚拟环境并安装 `bleak`：

    ```bash
    python3 -m venv .venv
    .venv/bin/pip install bleak
    ```

    先让手机和工具 App 断开与开发板的连接：Reef 配置只允许一条连接（`CONFIG_BT_CONN=1`）。

11. **生成 OTA 包**：随意修改一处代码（例如把提示音改为 `reef_hw_tone(2000, 150, 30)`），重新构建（步骤 1），再把构建结果打包成 boot2 OTA 包。打包脚本会调用 IntelProCube 生成整体镜像，再用 SDK 的 `tools/create_ota.py` 压缩：

    === "macOS"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    === "Linux"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    输出：`apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota`（约 345 KB）。OTA 只接受这个 `.xz.ota` 包，不能直接发送 `.bin`。

12. **通过 BLE 推送并确认**：`reef_ota.py` 默认查找名为 `IPRO-Remote` 的设备，开发板已经改名，所以用 `REMOTE_NAME` 指定：

    ```bash
    REMOTE_NAME=IPRO-Hello .venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py \
        apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota
    ```

    工具依次打印开发板当前的版本信息、包大小和 CRC32、传输时间、`verified, slot switched; rebooting`，等开发板重启后再连接一次并打印新的版本信息：

    ```text
    running: <摄像头、SD 卡与编译时间>
    ipro_ble_remote_reef.xz.ota: <字节数> bytes, CRC32 <值>, <有效载荷> bytes/packet
    sent in <秒数> s (<速率> KB/s)
    verified, slot switched; rebooting
    running: <新的编译时间>
    ```

    开发板的控制台同时打印 `[OTA] START: …`、`[OTA] CRC32 OK! Switching partition...`、`[OTA] Ready to reboot`，重启时再次出现 `[BOOT2] IPRO7 Boot2 v0.5.2`：boot2 校验包的 SHA256、解压到 FW A 后才启动应用。INTELPRO 在 macOS、MTU 247 下实测 345 KB 包的传输时间为 13–17 秒。附带的 Android 演示 App 也能推送同一个 `.xz.ota` 包。

</div>

!!! danger "不要用标准分区表做 OTA"
    Reef 上只能用 `partition_cfg_2M_remote_ab.toml` 做 OTA。如果开发板是用 IntelProCube 的标准 `partition_cfg_2M.toml` 烧录的，OTA 写入它的 FW B（0x12A000）并切换后，开发板完全没有输出，只能进入下载模式重新烧录。

## 验证结果 { #verify }

- 控制台的广播信息显示 `IPRO-Hello`，手机扫描列表中也出现 `IPRO-Hello`。
- 手机连接时能听到哔声，控制台打印 `Connected! Peer: …`。
- 步骤 6 中的 LED、按键和 UART 操作仍然正常。
- `reef_ota.py` 最后一行的 `running:` 显示新的编译时间，重新连接时听到步骤 11 中改过的提示音。

`main.c` 启动横幅中的 `Device Name: 'IPRO-Remote'` 是固定字符串，不影响广播名称。

## 工作原理 { #how-it-works }

`main.c` 完成平台初始化后创建 `BLERemote` 任务，该任务调用 `remote_app_init()`。BLE 按固定顺序启动：先创建控制器任务，再初始化 HCI 驱动，最后启动 Zephyr Host（取自 `src/app/remote_app.c`）：

```c title="src/app/remote_app.c"
err = ipro_ble_ctlr_controller_init(configMAX_PRIORITIES - 1);  /* IPRO BLE 控制器 */
vTaskDelay(pdMS_TO_TICKS(50));
err = hci_driver_ipro_ble_ctlr_init();                           /* HCI 驱动 */
vTaskDelay(pdMS_TO_TICKS(50));
err = bt_enable(bt_ready_cb);                                    /* Zephyr Host */
```

Host 就绪后，`bt_ready_cb()` 依次调用 `bt_set_name(DEVICE_NAME)`、`bt_conn_cb_register(&conn_callbacks)` 注册连接回调，初始化 GATT 服务，最后开始可连接广播。服务用 `BT_GATT_SERVICE_DEFINE()` 静态定义在 `src/services/remote_services.c` 中。广播数据和参数如下，`DEVICE_NAME` 同时用于广播数据和 `bt_set_name()`：

```c title="src/app/remote_app.c"
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
};

struct bt_le_adv_param adv_param = {
    .id = BT_ID_DEFAULT,
    .options = BT_LE_ADV_OPT_CONN,
    .interval_min = 160,  /* 100ms (N * 0.625ms) */
    .interval_max = 320,  /* 200ms */
};
int err = bt_le_adv_start(&adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
```

Reef 配置另外编入两个服务：OTA `0xFF60`（控制 `0xFF61`、数据 `0xFF62`、状态 `0xFF63`）和 Reef 硬件服务 `0xFF80`（LED Colour `0xFF81`、Key Event `0xFF82`、Sound Level `0xFF83`、Tone `0xFF84`、Board Info `0xFF85`）。LED、按键、扬声器、SD 卡和摄像头的驱动直接引用出厂固件 `apps/platform/ipro7ai_reef_demo/src` 中的源代码；`src/board/reef_hw.c` 是唯一操作这些硬件的任务，BLE 回调只向它投递请求。

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| 烧录输出中没有 `[All Success]`，或出现 `flash jedec id: 00000000` | 未进入下载模式，或 Flash 引脚配置不符 | 先进入下载模式；确认命令中有 `--chip-variant IPRO7AI` |
| 烧录成功但控制台没有任何输出 | 没有一并写入 boot2 和 A/B 分区表，或串口波特率不对 | 用步骤 3 的完整命令重新烧录；控制台设为 115200 |
| 手机仍显示 `IPRO-Remote` | 手机缓存了旧名称 | 确认控制台的广播信息已经是 `IPRO-Hello`，再关闭并重新打开手机蓝牙后扫描 |
| LED 不亮或没有哔声 | WS2812 和扬声器放大器由 USB VBUS 供电；J2 插着耳机时扬声器关闭 | 用 USB-C 供电，不要只从 3.3 V 供电；拔掉耳机或改用耳机听 |
| 构建因警告失败 | 应用以 `-Werror` 编译 | 确认 `#include "reef_hw.h"` 放在 `CONFIG_IPRO7AI_REEF` 条件内，且调用写在函数内 |
| `make_reef_ota.sh` 打印 `IntelProCube tool not found` | 没有设置 `IPRO_FLASH_TOOL`，PATH 中也没有烧录工具 | 设置 `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos`（或 `_linux`） |
| `make_reef_ota.sh` 打印 `build first: …` | 还没有 `build_reef/` 的构建结果 | 先执行步骤 1 |
| `reef_ota.py` 打印 `IPRO-Remote not found` | 开发板已改名、正与手机连接，或电脑的蓝牙未开启／未授权 | 设置 `REMOTE_NAME=IPRO-Hello`；断开手机连接；在 macOS 上允许“终端”使用蓝牙 |
| `reef_ota.py` 打印 `device error …` | 开发板拒绝了该包或写入失败 | 确认发送的是 `.xz.ota`；查看控制台的 `[OTA]` 信息 |
| OTA 后开发板没有恢复运行 | boot2 校验包失败时会停在 USB 救援模式 | 进入下载模式，用步骤 3 的命令重新烧录 |

## 下一步 { #next-steps }

- [BLE 吞吐量测试](ble-throughput.md)：用两块 Reef 测量传输速率。
- [LE Audio 入门](le-audio.md)：在 Reef 上运行 LE Audio 耳机示例。
- [BLE 开发](../guides/ble.md)：控制器库的选择、Host 配置与 API。
- [OTA 更新](../guides/ota.md)：分区表、OTA 包格式与 boot2 的更新流程。
