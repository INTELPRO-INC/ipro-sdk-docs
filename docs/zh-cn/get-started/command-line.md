---
title: "macOS／Linux 命令行"
description: 在 macOS 或 Linux 上用 make 与 build_freertos.sh 构建、清理、烧录与监视 FreeRTOS 应用的完整参考，示例以 IPRO7AI Reef EVK 为准。
migrate_from:
  - "getting-started.html#installation"
  - "getting-started.html#directory-structure"
  - "tools-debugging.html#macos-notes"
---

# macOS／Linux 命令行

在 macOS 或 Linux 上，FreeRTOS 应用用 `make -C` 构建，或用 `build_freertos.sh` 把构建、烧录、监视串成一条命令。本页是两者的完整参考：构建目录与输出、替代配置、清理，以及 `build_freertos.sh` 的动作、选项、环境变量与限制，示例都以 IPRO7AI Reef EVK 为准。工具的安装见[准备开发环境](environment.md)。

## 前提条件 { #prerequisites }

- 已完成[准备开发环境](environment.md)：工具链、CMake、make、Python 与 IntelProCube。
- 以下命令都在 SDK 根目录执行。
- 需要烧录时，开发板已按[设置开关与接线](first-app-freertos.md#connect)连接好。

## 目录结构 { #directory-structure }

| 路径 | 内容 |
|---|---|
| `apps/<分类>/<应用>/` | 应用：`.config`、替代配置 `defconfig_*`、`CMakeLists.txt`、`Makefile`、源代码；分类为 `ai`、`bluetooth`、`multimedia`、`platform`、`test` |
| `bsp/` | 板级配置与链接脚本、SoC 驱动程序、HAL |
| `components/` | FreeRTOS、BLE、网络、音频、AI、USB、文件系统等组件；部分为预编译库 |
| `cmake/` | 工具链与构建宏 |
| `tools/` | `serial_monitor.py`、`create_ota.py`、`teach_web/`、`zephyr/`、随附的 CMake（Linux x86-64） |
| `zephyr/` | Zephyr 模块（IPRO7 EVB 与 IPRO7AI EVK 板型） |
| `build_freertos.sh`、`project.build`、`VERSION.txt` | 构建前端、make 与 CMake 的衔接、版本信息 |

各组件的说明见[系统架构](../guides/architecture.md)。

## 用 make 构建 { #make }

```bash
make -C apps/<分类>/<应用>                            # 以 .config 构建，输出到 build/
make -C apps/<分类>/<应用> DEFCONFIG=defconfig_<名称>  # 以替代配置构建，输出到 build_<名称>/
```

- **构建目录**：`DEFCONFIG=` 的构建目录是 `build_` 加上文件名去掉 `defconfig_` 后的部分，例如 `defconfig_reef` → `build_reef/`、`defconfig_wifi_ipro6s` → `build_wifi_ipro6s/`。替代配置会被复制为 `build_<名称>/.config`，应用目录中的 `.config` 不受影响；要修改配置，请修改应用目录中的原文件。
- **输出**：`<构建目录>/build_out/<应用>_IPRO7.bin`（用于烧录）、`.elf`（含调试符号）、`.map`（内存布局）；`<构建目录>/include/generated/autoconf.h` 是由配置文件生成的宏。每次构建还会把 `compile_commands.json` 复制到 SDK 根目录，供编辑器建立代码索引。
- **工具链**：`make -C … CROSS_COMPILE=<目录>/bin/riscv64-unknown-elf-` 或同名环境变量会覆盖 `.config` 中的 `CONFIG_CROSS_COMPILE`。
- **并行构建**：内部的 CMake 构建固定以 `-j4` 执行。
- **`BOARD=`**：只有 `ipro_agora_sentino`（默认 `reef`）与 `ipro_pdm_mic_demo` 使用；其他应用用 `DEFCONFIG=` 选择开发板。

构建 `ipro7ai_reef_demo` 时的输出（节选）：

```text
[INFO] Build Path: <SDK>/apps/platform/ipro7ai_reef_demo/build
CPU: intelpro_ipro7
...
-- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
-- Generated autoconf header: <SDK>/apps/platform/ipro7ai_reef_demo/build/include/generated/autoconf.h
...
-- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
-- IPRO7 flash: 1M (default, on-chip)
-- AI disabled: OCRAM=256KB
...
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
[100%] Built target ipro7ai_reef_demo_IPRO7.elf
```

`[board] IPRO7AI Reef` 这一行表示本次构建的目标是 Reef。没有这一行时，使用的是其他开发板的配置。

### Reef 的构建配置 { #reef-configs }

以下配置的目标是 Reef。表中标有 `DEFCONFIG=` 的应用，直接 `make` 构建的是其他开发板的 `.config`。

| 应用 | 构建命令 | 构建目录 | 控制台 |
|---|---|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` | `build/` | 115200 |
| `ipro7ai_reef_demo`＋Wi-Fi | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | `build_wifi_ipro6s/` | 115200 |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` | `build/` | 115200 |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro7_uvc_cam` 网络摄像头 | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | `build_reef_ov5640/` | 115200 |
| `ipro7_uvc_cam` 石头剪刀布 | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | `build_reef_rps/` | 115200 |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | `build_reef/` | 921600 |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` | `build/` | 115200 |

烧录各应用时使用哪个分区表、是否需要 boot2 或 `mfg` 数据，见[烧录与串口：分区表](flash-and-monitor.md#partition-tables)。

## 清理 { #clean }

```bash
make -C apps/platform/ipro7ai_reef_demo clean                                   # 删除 build/
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s clean   # 删除 build_wifi_ipro6s/
```

`clean` 只删除对应的构建目录。修改 `.config` 或替代配置后，先清理再构建。

## build_freertos.sh { #build-script }

```text
./build_freertos.sh [动作...] [选项] <项目>
```

动作可以串联，按顺序执行，任一动作失败即停止；指定多个动作时，最后列出每个动作的结果。未指定动作时执行 `build`。项目可以写名称（`ipro7ai_reef_demo`），也可以写 `apps/` 下的路径（`platform/ipro7ai_reef_demo`）。

### 动作 { #actions }

| 动作 | 作用 |
|---|---|
| `build` | 执行 `make -C <应用> [DEFCONFIG=…]`。完整输出写入 `<构建目录>/build.log`；成功时输出 `✓ Build succeeded`、`Binary:` 路径与大小，失败时输出日志的最后 30 行 |
| `clean` | 执行 `make -C <应用> clean`，删除构建目录 |
| `flash` | 发送 `reboot_dl` 后用 IntelProCube 烧录已构建的镜像文件，见[烧录与串口](flash-and-monitor.md#build-script) |
| `monitor` | 以应用的控制台波特率打开串口，先发送 `reboot`，读取 `-t` 秒；只显示输出，不能输入 |
| `size` | 用 `riscv64-unknown-elf-size` 输出 `.elf` 的总大小与各段大小 |
| `test` | 构建、烧录，发送 `reboot`，等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；退出码 0 表示通过、1 表示失败、2 表示超时 |

### 选项 { #options }

| 选项 | 说明 |
|---|---|
| `-p`, `--port PORT` | 串口；默认为 `IPRO_SERIAL_PORT`，否则为唯一连接的 USB 串口 |
| `-t`, `--timeout SEC` | `monitor` 与 `test` 的读取秒数，默认 30；`0` 表示持续到按下 ++ctrl+c++ |
| `-w`, `--wait-for PAT` | `monitor` 匹配到这个正则表达式即结束；匹配到的文本包含 `PASSED` 才算成功 |
| `-d`, `--defconfig FILE` | 替代配置，构建于 `build_<名称>/`；`flash`、`size` 也据此查找镜像文件 |
| `-c`, `--chip-variant V` | 烧录时的 `--chip-variant`；默认为 `IPRO_CHIP_VARIANT`，否则 IPRO7AI EVK 与 Reef 的配置用 `IPRO7AI`、其他用 `IPRO7` |
| `-P`, `--pt TABLE` | 烧录时的分区表：`.toml` 路径，或工具 `chips/ipro7/partition/` 下的文件名；默认为 `IPRO_FLASH_PT`，否则不带 `--pt` |
| `-j`, `--jobs N` | 外层 `make` 的并行数（内部构建固定 `-j4`） |
| `-v`, `--verbose` | 在屏幕上显示完整构建输出 |
| `-l`, `--list` | 按分类列出所有项目 |
| `-h`, `--help` | 帮助 |

### 环境变量 { #environment }

| 变量 | 作用 |
|---|---|
| `IPRO_FLASH_TOOL` | IntelProCube 命令行工具的路径；未设置时在 PATH 中查找 `ipro_iot_tool_macos`／`ipro_iot_tool_linux` |
| `IPRO_SERIAL_PORT` | 默认串口（`-p` 优先） |
| `IPRO_CHIP_VARIANT` | 默认的 `--chip-variant`（`-c` 优先） |
| `IPRO_FLASH_PT` | 默认的分区表（`-P` 优先） |
| `CROSS_COMPILE` | 传给 `make`，覆盖 `.config` 中的工具链前缀 |

### 列出项目 { #list }

```bash
./build_freertos.sh -l
```

按分类列出 `apps/` 下的项目，右侧是 `.config` 第一行的说明（节选）：

```text
ai
  ipro7ai_evk_person_detect           IPRO7AI EVK person detection: SC101IOT camera -> ISP -> NPU (YOLOv8) with
  ipro7ai_evk_rps                     IPRO7AI EVK rock-paper-scissors: SC101IOT camera -> ISP -> NPU classifier,
  ipro_reef_teach
  ipro_speaker_recog

bluetooth/ble
  ipro_ble_hid_keyboard
  ipro_ble_remote
  ipro_ble_transparent
  ipro_throughput_test
...
platform
  ...
  ipro7ai_reef_demo                   IPRO7AI Reef carrier board demo.
```

清单包含所有开发板的应用；Reef 可用的是[上表](#reef-configs)中的配置。

## Reef 示例 { #examples }

先设置一次环境变量（以 macOS 为例）：

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
PT2M=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
```

```bash
# 出厂固件：构建、烧录、查看 30 秒启动信息
./build_freertos.sh -P $PT2M build flash monitor ipro7ai_reef_demo

# 干净重建 Wi-Fi 版本
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo

# USB 网络摄像头：构建并烧录
./build_freertos.sh -d defconfig_reef_ov5640 -P $PT2M build flash ipro7_uvc_cam

# 921600 baud 的应用：monitor 自动使用配置文件中的波特率
./build_freertos.sh -d defconfig_reef build flash monitor ipro7_jpeg_decode

# 仅构建（首次烧录需要 boot2，请直接运行工具）
./build_freertos.sh -d defconfig_reef build size ipro_ble_remote
```

`build` 成功时的输出：

```text
Project: ipro_ble_remote  (bluetooth/ble/ipro_ble_remote)
Defconfig: defconfig_reef

→ Building ipro_ble_remote...
✓ Build succeeded (19s)
  Binary: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin (561 KB)
  Log: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build.log
```

## 限制 { #limits }

- **只能烧录 IPRO7**：`flash` 固定传入 `--chipname ipro7`，不能烧录 IPRO6S 镜像。
- **没有 `--boot2`、`--mfg`、`--skip-ota`**：`ipro_ble_remote` 的首次烧录与 `ipro_reef_teach` 的 `mfg` 数据请直接运行 IntelProCube，见[烧录与串口](flash-and-monitor.md#boot2-ab)。
- **工具在当前目录运行**：`-P` 请给出 `.toml` 的完整路径。
- **`reboot_dl` 需要 shell**：板上固件没有 shell 或已死机时，先用按键进入下载模式。
- **`monitor` 不是交互式终端**：要输入命令，请使用终端程序，见[交互式终端程序](flash-and-monitor.md#terminal)。超时（退出码 2）或匹配到不含 `PASSED` 的文本（退出码 1）都会被记为失败并停止后续动作，请把 `monitor` 放在最后。
- **`size` 使用默认路径下的工具链**：固定调用 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size`。
- **没有 `BOARD=` 选项**：用 `-d` 选择替代配置。
- **只支持 macOS 与 Linux**：脚本需要 bash，串口自动检测只识别 `/dev/*` 名称。

## 验证结果 { #verify }

```bash
./build_freertos.sh -l                      # 列出项目
./build_freertos.sh ipro7ai_reef_demo       # 输出 ✓ Build succeeded 与 Binary: 路径
ls apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

## macOS 注意事项 { #macos-notes }

- 串口使用 `/dev/cu.*`（例如 `/dev/cu.usbserial-XXXX`），不要使用 `/dev/tty.*`：后者会等待 carrier detect 信号而卡住。
- `tools/cmake/` 随附的 CMake 是 Linux 可执行文件；构建时优先使用 PATH 中的 `cmake`，因此在 macOS 上安装 Homebrew 的 CMake 即可。
- `tools/serial_monitor.py` 只使用 Python 标准库（termios），不需要 pyserial；921600 等高波特率在 macOS 上由脚本单独设置，可以直接使用。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| `✗ Project '…' not found. Did you mean:` | 名称不完整 | 使用 `-l` 列出的完整名称 |
| `✗ Multiple projects match '…':` | 多个分类中有同名项目 | 改用路径，例如 `platform/ipro7ai_reef_demo` |
| `✗ Build failed`，最后 30 行中有 `No cmake found` | PATH 中没有 `cmake` | 安装 CMake 3.15 及以上版本 |
| 构建日志中找不到 `riscv64-unknown-elf-gcc` | 工具链不在 `/opt/toolchain/riscv_ipro7/` | 设置 `CROSS_COMPILE` |
| 构建输出中没有 `[board] IPRO7AI Reef` | 使用的是其他开发板的配置 | 按[Reef 的构建配置](#reef-configs)加上 `DEFCONFIG=` 或 `-d` |
| 用 `-d` 构建后，`flash` 或 `size` 报告 `Binary not found` 或 `ELF not found` | 没有带 `-d` 时，脚本查找的是 `build/` | 加上相同的 `-d` |
| `✗ Flash tool not found: ipro_iot_tool_macos` | 找不到 IntelProCube | 设置 `IPRO_FLASH_TOOL` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 连接了多个 USB 串口 | 用 `-p` 或 `IPRO_SERIAL_PORT` 指定 |
| `size` 失败，找不到 `riscv64-unknown-elf-size` | 工具链不在默认路径 | 直接运行 `<工具链目录>/bin/riscv64-unknown-elf-size <elf>` |

## 下一步 { #next-steps }

- [第一个 FreeRTOS 应用](first-app-freertos.md)：在 Reef 上构建、烧录并运行 `ipro7ai_reef_demo`。
- [构建与烧录流程](../tutorials/build-and-flash.md)：日常的修改、构建、烧录与监视循环。
- [构建系统与配置](../guides/build-system.md)：`.config` 键值、链接脚本与内存布局。
