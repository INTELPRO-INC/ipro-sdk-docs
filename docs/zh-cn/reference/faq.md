---
title: "常见问题"
description: 构建、烧录与控制台、BLE、平台与联网、调试的常见问题与简答，以 IPRO7AI Reef EVK 为准，并链接到详细说明的页面。
migrate_from:
  - "faq.html"
---

# 常见问题

每题先给结论，需要操作时列出命令与预期结果，细节链接到对应页面。示例以 IPRO7AI Reef EVK V4.0 为准。错误信息的对照表见[调试与故障排除](debugging.md#troubleshooting)。

## 构建 { #build }

### SDK、烧录工具与工具链从哪里获取？ { #get-tools }

- **SDK V2.2.0**：从 [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0) 下载 `IPRO-SDK-V2.2.0.tar.gz`，核对页面上的 SHA-256 后解压：

    ```bash
    shasum -a 256 IPRO-SDK-V2.2.0.tar.gz      # Linux：sha256sum；应与 Release 页面上的值相同
    tar xzf IPRO-SDK-V2.2.0.tar.gz
    cat IPRO-SDK-V2.2.0/VERSION.txt
    ```

    `VERSION.txt` 打印 `IPRO7: IPRO-SDK-V2.2.0`、`IPRO6: IPRO-SDK-V2.2.0` 与 `Release Date: 2026-11-03`。
- **RISC-V 工具链**：未包含在 V2.2.0 中，请联系 INTELPRO。默认安装在 `/opt/toolchain/riscv_ipro7/`。
- **IntelProCube 命令行烧录工具**（`ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe`）：未包含在 V2.2.0 中，从 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) 下载 0.7.0.1，见[准备开发环境](../get-started/environment.md#intelprocube)。
- **Windows 在线安装程序 3.6.0 与 VS Code Extension 3.3.0**：当前版本，从 [ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest) 下载；安装程序会直接安装 SDK V2.2.0 与 Windows 版工具链，见 [Windows 安装与 VS Code](../get-started/windows.md)。
- **IPRO AI Studio**：不在 SDK 中，从 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载。

### build_freertos.sh 与 make -C 有什么不同？ { #build-cli-vs-make }

`make -C apps/<分类>/<应用>` 只构建一个应用，必须写完整路径。`build_freertos.sh` 在 `make` 之外增加了 `clean`、`flash`、`monitor`、`size` 与 `test`，可以只写应用名称并串联动作：

```bash
make -C apps/platform/ipro7ai_reef_demo
./build_freertos.sh clean build ipro7ai_reef_demo
```

两者产物相同，都在 `<应用>/build/build_out/`。`build_freertos.sh flash` 会根据配置文件自动为 Reef 选择 `--chip-variant IPRO7AI`，以 `-P` 指定分区表，`monitor` 以应用自己的控制台波特率打开。它无法传 `--boot2` 与 `--mfg`，也不能烧录 IPRO6S；这些情况请直接使用 IntelProCube 工具，见[工具命令行](tools.md#build-cli)。

### 哪些应用能在 Reef 上运行？要选哪个配置文件？ { #reef-apps }

40 个应用中有 9 个附带 Reef 配置。只有 `ipro7ai_reef_demo`、`ipro_reef_teach` 与 `ipro_agora_sentino` 直接 `make` 就是 Reef 版本；其他应用的 `.config` 是 IPRO7 EVB 或 IPRO7AI EVK 的配置，要以 `DEFCONFIG=` 选择 Reef 配置：

| 应用 | 构建命令（在 SDK 根目录下） |
|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` |
| `ipro7ai_reef_demo`（Wi-Fi 与 RTSP） | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` |
| `ipro7_uvc_cam`（网络摄像头） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` |
| `ipro7_uvc_cam`（石头剪刀布） | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef`（控制台 921600） |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` |

`DEFCONFIG=defconfig_<名称>` 的输出放在 `build_<名称>/build_out/`，例如 `defconfig_reef` 在 `build_reef/build_out/`，`.config` 不会被改动。要确认一个配置文件是否为 Reef 版本：

```bash
grep CONFIG_IPRO7AI_REEF apps/bluetooth/ble/ipro_ble_remote/defconfig_reef
```

打印 `CONFIG_IPRO7AI_REEF=y` 即是。各应用的分区表、`--boot2`、`--mfg` 与 USB 标识见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)，其余应用需要的开发板见[示例](../examples/index.md)。

### 改了 .config，依赖的配置却没有生效？ { #kconfig }

构建按原样读取 `.config`，由 `cmake/generate_autoconf.cmake` 生成 `autoconf.h`。Kconfig 文件只是说明，`select`、`depends on` 与默认值都不会自动应用，依赖的配置必须自己写进 `.config`。例如启用 `CONFIG_AI_SUPPORT=y` 时，也要写入 `CONFIG_USE_PSRAM=y`。唯一的例外是 Reef 的晶体微调：配置文件中没有写 `CONFIG_IPRO7_XTAL_CAPCODE` 时，构建会加入 95。

`make menuconfig` 需要的 `tools/kconfig/menuconfig.py` 与 `make defconfig` 使用的 `configs/` 目录都未随附，请直接编辑 `.config`，或另存为 `defconfig_<名称>` 再以 `DEFCONFIG=` 构建。详见[构建系统与配置](../guides/build-system.md)。

### 找不到工具链，或工具链不在默认路径？ { #toolchain }

工具链前缀依次取自：环境或命令行中的 `CROSS_COMPILE`、配置文件中的 `CONFIG_CROSS_COMPILE`、`project.build` 的默认路径 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-`（Windows 没有默认值）。40 个 `.config` 中有 30 个写了 `CONFIG_CROSS_COMPILE`。工具链放在其他位置时：

```bash
export CROSS_COMPILE=<工具链路径>/bin/riscv64-unknown-elf-
make -C apps/platform/ipro7ai_reef_demo
```

CMake 配置阶段打印 `[toolchain] Vendor toolchain detected …` 表示找到了 INTELPRO 的工具链。请保留 `.config` 中的 `CONFIG_CPU_ID="intelpro_ipro7"`。`build_freertos.sh size` 固定使用默认路径下的 `size`。

### 可以在 Windows 上构建吗？ { #windows }

可以。用 IPRO SDK Online Setup 安装的 SDK 已修正 Windows 上的构建问题，并加入 PowerShell 版的 `build_freertos.ps1`，可以在 PowerShell 或 VS Code 中构建、烧录并打开控制台，见 [Windows 安装与 VS Code](../get-started/windows.md)。

直接使用从 GitHub 下载的软件包时，命令行流程以 macOS 与 Linux 为主：`build_freertos.sh` 是 bash 脚本，`tools/serial_monitor.py` 使用 termios，两者都不能在 Windows 上运行。`project.build` 有 Windows 分支，条件如下：

- 每次构建都要指定 `CROSS_COMPILE`，因为 Windows 没有默认的工具链路径，而 `.config` 中的 `CONFIG_CROSS_COMPILE` 是 Unix 路径：`make -C apps/platform/ipro7ai_reef_demo CROSS_COMPILE=<工具链路径>/bin/riscv64-unknown-elf-`。
- `cmake` 与 `python`（不是 `python3`）必须在 `PATH` 上；随附的 `tools/cmake/` 只有 Linux 版。
- 烧录用 `ipro_iot_tool.exe`，串口为 `COM5` 这类名称；控制台用任一 Windows 串口终端程序打开。

软件包本身没有说明在 Windows 上使用哪一种 shell 与 `make`；建议改用 Online Setup 安装的环境。

### Flash 或 RAM 不够用？ { #memory }

先看链接器在构建最后打印的内存区段使用量，再用 `./build_freertos.sh size <应用>` 与 `.map` 文件找出占用最大的部分，方法见[大小与内存分析](tools.md#size-analysis)。OCRAM 为 256 KB，BLE 控制器的 Exchange Memory（`CONFIG_EM_SIZE`）从中划出；同时启用 `CONFIG_AI_SUPPORT` 与 `CONFIG_MM_SUPPORT` 时，OCRAM 区段缩小为 64 KB 或 48 KB。关闭不需要的组件，或把大型缓冲区放到 PSRAM（`CONFIG_USE_PSRAM=y`）。Flash 默认按 1 MB 布局链接，设置 `CONFIG_IPRO7_FLASH_2M=y` 改用 2 MB 布局；Reef 各配置的情况见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#bsp)。

## 烧录与控制台 { #flash-console }

### 烧录失败怎么办？ { #flashing }

依次确认：

1. **看结果字符串**：工具输出中有没有 `[All Success]`；工具失败时也以 0 退出。
2. **芯片配置**：Reef 用 `--chip-variant IPRO7AI`。工具会记住上一次的配置，更换开发板时务必重新指定。输出中出现 `flash jedec id: 00000000` 或 `IPRO FLASH MATCH TYPE FAIL` 就是这个原因。
3. **下载模式**：按住 SW1（BOOT），按一下 SW2（RESET），松开 SW1，控制台应保持静默；或在控制台输入 `reboot_dl`，打印 `reboot to download mode`。其他方法见[进入下载模式](debugging.md#download-mode)。
4. **串口**：关闭其他监视程序；macOS 用 `/dev/cu.*`；IPRO Debug Probe 用名称以 `02` 结尾的端口。
5. **分区表**：`ipro7ai_reef_demo` 与 `ipro7_uvc_cam` 用 `--pt chips/ipro7/partition/partition_cfg_2M.toml`；`ipro_ble_remote` 的 OTA 版本首次烧录要带 `--boot2` 与 `partition_cfg_2M_remote_ab.toml`；`ipro_reef_teach` 用自己的 `partition_reef_teach.toml`、`--skip-ota` 与 `--mfg`。各应用见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)。

烧录完成后按 SW2 复位，控制台出现应用的启动信息即表示成功。完整步骤见[烧录与串口](../get-started/flash-and-monitor.md)。

### 控制台是乱码或没有输出？ { #console }

乱码多半是波特率不符。波特率由配置文件中的 `CONFIG_PLATFORM_UART_BAUDRATE` 决定，未设置时为 115200；Reef 的配置都是 115200，只有 `ipro7_jpeg_decode` 的 `defconfig_reef` 是 921600。`build_freertos.sh monitor` 会自动使用应用的波特率；自己打开时请指定 `--baud`：

```bash
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0
```

没有输出时：开发板可能还在下载模式（按 SW2 复位）、U6 的 TX／RX 接反（U6 第 3 脚是 Reef 的 TX），或打开的是 Debug Probe 的 `04` 端口。`serial_monitor.py` 只能读取输出与发送一行命令；要逐行输入，请用 `screen /dev/cu.usbserial-XXXX 115200` 或其他串口终端程序。

### macOS 的 /dev/cu.* 与 /dev/tty.* 有什么区别？ { #macos-serial }

同一个串口设备在 macOS 上有两个节点：`/dev/cu.*` 直接打开；`/dev/tty.*` 会等待载波检测（DCD）信号，程序因此卡住。请始终使用 `/dev/cu.*`。

出现 `Resource busy` 表示其他程序（另一个监视程序、IDE 或 `stty -f`）正占用串口。用 `lsof /dev/cu.usbserial-XXXX` 找出并关闭它，同一时间只开一个监视程序。

## BLE { #ble }

### 该选哪一个 BLE 控制器库？ { #ble-variant }

由 `.config` 中的三个配置项选出库：`CONFIG_IPRO_BLE_CTLR_LIB`（`link1_periph` 只做 peripheral 与 broadcaster；需要 central 或多条连接时用 `link1`、`link2`、`link4`）、`CONFIG_IPRO_BLE_CTLR_FEATURE`（`bt54_iso2` 加入 ISO／LE Audio，需要 `CONFIG_EM_SIZE=32`）与 `CONFIG_IPRO_BLE_CTLR_CFG_DBG`（未设置时使用 `_release` 库）。`CONFIG_BT_CONN` 不可超过所选库的连接数。构建时 CMake 打印 `[ipro_ble_controller] Using prebuilt <文件名>`，可确认实际链接的库。完整规则见 [BLE 开发](../guides/ble.md)；从最接近需求的 Reef 配置（例如 `ipro_ble_remote/defconfig_reef`）开始修改。

### 有 BLE 控制器源码吗？ { #ble-prebuilt }

没有。IPRO BLE 控制器只以预编译库形式提供，位于 `components/wireless/bluetooth/ipro_ble_controller/lib/`，共 16 个 IPRO7 库：4 种连接配置 × 2 种功能配置 × debug／release。本版本没有 IPRO6S 的 BLE 控制器库，IPRO6S 应用只有 Wi-Fi。

下列配置会改为从源码构建控制器，在本软件包中无法构建：`CONFIG_IPRO_BLE_CTLR_FORCE_SOURCE_BUILD`、`CONFIG_IPRO_BLE_CTLR_SUBRATING`、`CONFIG_IPRO_BLE_CTLR_CSSA`、`CONFIG_IPRO_PM_BLE`、`CONFIG_IPRO_PM_PDS_CONNECTED`。需要其他库组合或这些功能时，请联系 INTELPRO。

### 配对数据在复位后消失？ { #ble-bonding }

配对密钥由 Host 的 Settings 存储。参考 `ipro_le_audio_headset` 的 `defconfig_reef`：

```ini title=".config"
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_EASYFLASH4=y
```

在 `bt_enable()` 的就绪回调中，先调用 `ipro_ble_ctlr_hcitl_host_ready()`，再在开始广播前调用 `settings_load_subtree("bt")` 并检查返回值；如果先广播，已配对的手机连接时会找不到密钥而重新配对。`ipro_ble_remote` 的配置不存储配对数据。若开发板上已没有配对数据而手机仍保留旧的配对，请在手机的蓝牙设置中删除该设备后重新配对。

### BLE 吞吐量能达到多少？ { #ble-throughput }

`ipro_throughput_test` 在两块 IPRO7AI Reef EVK 之间的实测（预编译 `link2` 控制器、ATT MTU 247、DLE 251 字节、每包 244 字节、连接间隔 50 ms、`CONFIG_IPRO7_BLE_HOTCODE=y`、单向发送 8 秒）：2M PHY 约 1.34 Mbps，1M PHY 约 747 kbps。数值对应该测试条件，不代表所有场景。

传输大量数据时建议使用 2M PHY、30–50 ms 连接间隔与 244 字节的数据包。步骤与完整结果见 [BLE 吞吐量测试](../tutorials/ble-throughput.md)。

### 如何进行 OTA 固件更新？ { #ota }

在 Reef 上，`ipro_ble_remote` 的 `defconfig_reef` 提供 BLE OTA（GATT 服务 `0xFF60`），需要 boot2 与 A/B 分区表 `partition_cfg_2M_remote_ab.toml`：

1. 以 `--boot2` 与 `--pt …/partition_cfg_2M_remote_ab.toml` 首次烧录，启动信息中先出现 `[BOOT2] IPRO7 Boot2 v0.6.0`。
2. 用 `make_reef_ota.sh` 生成 `build_reef/build_out/ipro_ble_remote_reef.xz.ota`。V2.2.0 的脚本要先把 boot2 路径改成 v0.6.0，见 [OTA 更新](../guides/ota.md#hands-on)第 4 步。
3. 用 `reef_ota.py` 或 Android 演示 App `ipro_remote_demo.apk` 发送升级包；开发板重启后运行新固件。

不要在以标准 `partition_cfg_2M.toml` 烧录的 Reef 上做 OTA，否则开发板会完全没有输出，只能进入下载模式重新烧录。命令见 [Reef 的 OTA 工具](tools.md#reef-ota-tools)，整体流程见 [OTA 更新](../guides/ota.md)。

## 平台与联网 { #platform }

### V2.2.0 支持 IPRO6S 吗？ { #ipro6s }

支持 Wi-Fi。V2.2.0 随附 3 个 IPRO6S 应用：`ipro6_demo`（Wi-Fi 6 station／soft-AP）、`ipro6_if_wifi`（通过 SDIO 或 USB 供主机使用的 Wi-Fi 桥接）与 `ipro6_fmac`（Linux 主机用的 FullMAC 固件）。本版本没有 IPRO6S 的 BLE 控制器库与 BLE／BR/EDR 应用。

在 Reef 上，IPRO6S 是插在 microSD 卡座中的 FIN Wi-Fi 卡，卡上固件是 `ipro6_if_wifi` 的 SDIO 配置：

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

产物为 `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。IPRO6S 镜像用 IntelProCube 的 `--chipname ipro6` 烧录，`build_freertos.sh flash` 不适用。可用的配置文件与烧录方式见 [IPRO6S](../hardware/chips/ipro6s.md)。

### IPRO7 如何联网？ { #wifi }

IPRO7 通过外接无线模块连接 Wi-Fi，在 Reef 上是经 SDIO 连接的 IPRO6S FIN 卡：

- **IPRO6S（SDIO）**：IPRO7 端组件 `components/network/ipronet_host`，lwIP 网络接口 `iproeth0`。Reef 上就是 FIN 卡：`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s`（含 RTSP 摄像头视频流）与 `ipro_agora_sentino`。步骤见 [Wi-Fi 与 RTSP 视频流](../tutorials/wifi-rtsp.md)。
- **其他**：ATBM6162（SDIO）、AIC8800（SDIO）与 ESP32（UART AT 指令）的组件也在软件包中。
- **有线网络**：EMAC（RMII）驱动（`CONFIG_ETHERNET`）。

详见[网络](../guides/networking.md)。

### SDK 支持哪些 RTOS？BLE Host 是 Zephyr 吗？ { #rtos }

40 个应用全部基于 FreeRTOS（内核 V11.1.0）：37 个 IPRO7、3 个 IPRO6S。BLE Host 来自 Zephyr v4.4.0，通过 SDK 的移植层在 FreeRTOS 上运行，应用使用 Zephyr 的 `bt_*` API，但无需安装 Zephyr。

SDK 同时也是 Zephyr v4.4.0 模块，板型为 `ipro7_evb` 与 `ipro7ai_evk`，没有 Reef 的板型；SoC 的 Kconfig 说明指出 Reef 运行 `ipro7_evb` 镜像时要设置 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`。详见 [Zephyr RTOS](../guides/zephyr.md)。

### 可以使用 Thread 或 Matter 吗？ { #thread-matter }

Thread 只在 Zephyr 下提供：Zephyr 的 IEEE 802.15.4 驱动加上 OpenThread，以 Zephyr 的 `samples/net/openthread/shell` 搭配 SDK 的 `zephyr/samples/ieee802154_shell/ot.conf` 与 `app.overlay` 构建。FreeRTOS 应用不含 Thread，本版本也不含 Matter。详见 [Thread 与 Matter](../guides/thread-matter.md)。

### 如何调整晶体频率偏移（CFO）？ { #xtal-capcode }

在 `.config` 中设置 `CONFIG_IPRO7_XTAL_CAPCODE=<1–255>`。启动时 `board_init()` 应用该值并打印 `[XTAL] capcode <启动值> -> <设定值>`，之后每次 RF 初始化都会重新加载。设为 0 时保留启动值，直到第一次 RF 初始化加载 ROM 默认值 85。Reef 未指定时自动使用 95，CMake 配置阶段打印 `[board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)`。

数值越大，频率越低：频率偏高（正偏移）时调大，偏低时调小。这是开发板级的数值，量产时仍需逐颗校准。代码中也可直接调用 `AON_Set_Xtal_CapCode()` 与 `AON_Get_Xtal_CapCode()`（`bsp/drivers/ipro7_soc/std_drv/inc/drv_aon.h`）。

## 调试 { #debug }

### 如何开启调试日志？ { #debug-log }

在 `.config` 中设置整数级别后重新构建：

```ini title=".config"
CONFIG_IPRO_LOG_ENABLE=y
CONFIG_LOG_DEFAULT_LEVEL=4    # 1 错误、2 警告、3 信息、4 调试、5 详细
```

程序读取的是 `CONFIG_LOG_DEFAULT_LEVEL` 这个整数，只改 `CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y` 之类的选项不会生效；`CONFIG_BT_DEBUG` 也不会开启 Host 日志。运行时可用 `ipro_log_set_level()` 调整，见 [API 参考](api/index.md#log-api)。

### 崩溃或栈溢出怎么分析？ { #crash }

固件在 CPU 异常时会打印 `MCAUSE`、`MEPC`、出错的任务与调用回溯；用工具链的 `addr2line` 对照同一次构建的 `.elf`，即可找到函数与源码行号。栈溢出会打印 `[!] Stack overflow: <任务>`，请加大 `xTaskCreate()` 的栈深度（单位为 word）。`ipro7ai_reef_demo` 与 `ipro_reef_teach` 崩溃后会重复打印 `==DUMP_READY:2000000==`，等待未随附的主机端工具：保存诊断信息后按 SW2 复位即可。本版本没有片上调试器（JTAG／GDB）的配置。详见[崩溃分析](debugging.md#crash-analysis)。
