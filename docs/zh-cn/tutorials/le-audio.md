---
title: "LE Audio 入门"
description: 在 IPRO7AI Reef EVK 上运行 LE Audio unicast 耳机 ipro_le_audio_headset：与 LE Audio 手机配对、用按键调节 VCP 音量、用测试音确认音频输出，并了解配置要点和本版本的验证范围。
migrate_from:
  - "tutorials.html — 教學 4"
---

# LE Audio 入门

完成本教程后，IPRO7AI Reef EVK 会运行 `ipro_le_audio_headset`：以 `IPRO-LE-Audio` 名称广播，与支持 LE Audio 的手机配对，提供 PACS、ASCS、CAS 和 VCP 等 LE Audio 服务。您将用板上按键调节 VCP 音量、用测试音确认扬声器和耳机孔的输出，并了解构建 LE Audio 应用所需的配置。

!!! warning "本版本的验证范围"
    根据应用 README，这个应用目前是 profile 与 ISO 数据通路的开发版本，不是完整的音频产品：
    
    - 已验证：手机扫描、连接、配对（安全级别 4）、LE Audio 服务发现（`1853`、`1850`、`184e`、`1844`），以及 VCP 音量控制。
    - 尚未验证：从手机传输音乐流。Android 手机目前显示此固件没有已连接的音频通道。LC3 解码后的播放和声学验证也尚未完成。
    
    `test_tone` 测试音直接驱动 DAC，不经过 LE Audio 音频流。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK：SW8 拨到 PWR，用 USB-C 供电；U6 接 IPRO Debug Probe 或 3.3 V USB 转 UART 线（115200 8N1，接法见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)）。可另将耳机接到 J2。
- 已完成[第一个 FreeRTOS 应用](../get-started/first-app-freertos.md)，并已按[准备开发环境](../get-started/environment.md#intelprocube)安装 IntelProCube 0.7.0.1 命令行烧录工具。
- 一个可输入命令的串口终端程序（见[烧录与串口](../get-started/flash-and-monitor.md)）。
- 一部支持并已开启 LE Audio 的 Android 手机。应用 README 中记录的测试手机是 Pixel 10 Pro（Android 17）。

## 步骤 { #steps }

<div class="ipro-steps" markdown>

1. **构建 Reef 配置**：

    ```bash
    make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef
    ```

    输出：`apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin`。这个配置按 2 MB Flash 链接（`CONFIG_IPRO7_FLASH_2M=y`）。不加 `DEFCONFIG=` 的 `make` 构建的是 IPRO7 EVB 版本。

2. **烧录**：让 Reef 进入下载模式（按住 SW1、按一下 SW2、松开 SW1；板上固件带 shell 时也可以输入 `reboot_dl`），然后在 IntelProCube 目录下执行：

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --firmware <SDK>\apps\bluetooth\le_audio\ipro_le_audio_headset\build_reef\build_out\ipro_le_audio_headset_IPRO7.bin
        ```

    工具失败时也会以 0 退出，请确认输出中有 `[All Success]`。

3. **打开控制台并复位**：以 115200 baud 打开控制台，按 SW2。启动后会看到下列信息（省略行首的级别、时间等字段）：

    ```text
    MAIN: IPRO LE Audio Headset v2.0 (Zephyr blestack)
    ...
    BLE_INIT: Advertising started: IPRO-LE-Audio
    KEYS: Keys: SW3 vol-, SW4 vol+, SW5 mute (GPIO<n>/<n>/<n>)
    ```

4. **确认音频输出**：输入下列命令，扬声器会播放 3 秒的 1 kHz 测试音；J2 插着耳机时，扬声器放大器关闭，声音只从耳机输出。

    ```text
    test_tone 3
    ```

5. **与手机配对**：在手机的蓝牙设置中配对新设备，选择 `IPRO-LE-Audio`。控制台会打印：

    ```text
    BLE_INIT: Connected: <手机地址>
    BLE_INIT: Security requested: level 2
    BLE_INIT: Security changed: <手机地址> level <n>
    BLE_INIT: [SMP] Pairing complete: <手机地址>, bonded=1
    ```

    手机会把它列为 LE Audio 设备。配对信息保存在 Flash 中，重启后仍然保留。

6. **用按键调节音量**：按 SW4 调高、SW3 调低、SW5 静音或取消静音。按键通过 VCP Volume Renderer 改变音量，已连接手机的音量条会随之变化。控制台打印：

    ```text
    VCP_SERVER: Volume state changed: volume=<0-255> mute=<0|1>
    ```

    输入 `vol` 可查看当前音量。

7. **查看状态**：

    ```text
    leaudio_status
    ```

    显示 `BLE Ready`、收到和解码的音频帧数，以及当前的采样率和输出（`DAC (Speaker)`）。

</div>

!!! info "从手机传输音乐流"
    从手机传输音乐流在本版本中尚未验证（见本页开头）。如果您的音源端建立了音频流，控制台会打印 `Stream … started (Streaming state)`，`leaudio_status` 中的 `Frames Received` 会持续增加；结果请以实际测量为准。

## 验证结果 { #verify }

- 控制台打印 `Advertising started: IPRO-LE-Audio`，`test_tone 3` 有声音。
- 手机完成配对，控制台打印 `Pairing complete: …, bonded=1`。手机发现的服务包含 CAS（`0x1853`）、PACS（`0x1850`）、ASCS（`0x184E`）和 VCS（`0x1844`）。
- 按 SW3／SW4／SW5 时控制台打印 `Volume state changed`，手机的音量条同步变化。

## 配置要点 { #configuration }

LE Audio 需要支持 ISO 的控制器库和较大的 Exchange Memory，Host 则根据角色启用相应的 profile。以下节选自 `defconfig_reef`：

```ini title="apps/bluetooth/le_audio/ipro_le_audio_headset/defconfig_reef（节选）"
# 控制器：peripheral ACL＋两路 ISO，Bluetooth 5.4 功能
CONFIG_IPRO_BLE_CTLR_LIB="link1_periph"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt54_iso2"
CONFIG_IPRO_BLE_CTLR_CFG_DBG=y
CONFIG_EM_SIZE=32
CONFIG_BT_CONN=1

# 配对与绑定
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_BT_BONDABLE=y

# LE Audio profile
CONFIG_BT_AUDIO=y
CONFIG_BT_AUDIO_RX=y
CONFIG_BT_BAP_UNICAST_SERVER=y
CONFIG_BT_PACS=y
CONFIG_BT_ASCS=y
CONFIG_BT_VCP_VOL_REND=y
CONFIG_BT_CAP_ACCEPTOR=y
CONFIG_BT_CSIP_SET_MEMBER=y

# ISO 通道
CONFIG_BT_ISO=y
CONFIG_BT_ISO_RX=y
CONFIG_BT_ISO_PERIPHERAL=y

# LC3 编解码器（预编译）与 DAC 输出
CONFIG_COMPONENTS_LC3_ENABLE=y
CONFIG_BSP_USING_DAC=y
```

- `bt54_iso2` 要求 `CONFIG_EM_SIZE` 至少为 32，否则构建会在配置阶段停止。
- `CONFIG_IPRO_BLE_CTLR_CFG_DBG=y` 选用调试版控制器库；未设置时使用 `_release` 版。
- 这个应用没有启用媒体控制（MCP）和通话控制（CCP）。

Reef 只使用 `defconfig_reef`：DAC 输出到扬声器和 J2 耳机孔（J2 插着耳机时扬声器放大器关闭），SW3／SW4／SW5 通过 VCP 调节音量。`dac os 0|1|2` 切换 DAC 输出路径（Reef 默认 `1`，512 kHz 加噪声整形），`dac spk <dB>` 调整扬声器路径的增益。应用的 `.config`、`DAC.config` 和 `UAC.config` 是 IPRO7 EVB 的配置。

## LE Audio 术语 { #concepts }

| 术语 | 含义 | 在 `ipro_le_audio_headset` 中 |
|---|---|---|
| CIS | 面向连接的等时流，一对一，用于耳机 | 接收端 |
| BIS | 广播等时流，一对多（Auracast） | 未使用 |
| BAP | 建立和管理音频流 | Unicast Server，2 个 sink ASE |
| PACS | 声明支持的编解码能力 | LC3：16／32／48 kHz、7.5／10 ms、单声道、每帧 26–155 octets |
| ASCS | 音频流端点（ASE）的配置与状态 | 已启用 |
| VCP | 音量控制 | Volume Renderer |
| CAP／CSIP | 通用音频 profile／协调设备集 | CAP Acceptor 与 CSIP set member |
| LC3 | LE Audio 的标准编解码器 | 预编译库 |

## 故障排除 { #troubleshooting }

| 症状 | 原因 | 处理 |
|---|---|---|
| 手机的蓝牙列表中看不到 `IPRO-LE-Audio` | 手机未开启 LE Audio，或开发板已与其他设备连接 | 开启手机的 LE Audio；这个应用同时只接受一条连接，连接期间停止广播 |
| 重新烧录后无法再次配对 | 手机或开发板保留了旧的绑定信息 | 在控制台输入 `leaudio_unpair` 清除绑定，并在手机上删除此设备后重新配对 |
| `test_tone` 没有声音 | 耳机插在 J2 上时扬声器会关闭；放大器由 USB VBUS 供电 | 拔掉耳机或改用耳机听；用 USB-C 供电 |
| 按键时出现 `volume control not up yet` | VCP 尚未完成初始化 | 等启动信息结束后再按 |
| 构建在配置阶段停止，信息中提到 `CONFIG_EM_SIZE` | `bt54_iso2` 需要较大的 Exchange Memory | 设置 `CONFIG_EM_SIZE=32` |

## 下一步 { #next-steps }

- [音频与 LE Audio](../guides/audio.md)：音频框架、DAC、PDM 与 LC3。
- [BLE 开发](../guides/ble.md)：控制器库的选择与 Host 配置。
- [第一个 BLE 应用](first-ble-app.md)：在 Reef 上修改 GATT 应用并通过 BLE OTA 更新。
