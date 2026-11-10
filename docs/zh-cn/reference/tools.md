---
title: "工具命令行"
description: SDK V2.2.0 随附主机端工具的命令、选项与示例：build_freertos.sh、make、IntelProCube 烧录工具、serial_monitor.py、create_ota.py、Reef 的 Teach 与 OTA 工具，以及未随附的项目。
migrate_from:
  - "tools-debugging.html#overview"
  - "tools-debugging.html#build-cli"
  - "tools-debugging.html#zephyr-tools"
  - "tools-debugging.html#automated-testing"
  - "tools-debugging.html#size-analysis"
  - "tools-debugging.html#dev-workflow"
---

# 工具命令行

SDK 随附主机端工具的命令格式、选项与示例，示例以 IPRO7AI Reef EVK V4.0 为准。逐步的烧录与控制台操作见[烧录与串口](../get-started/flash-and-monitor.md)。

## 工具一览 { #overview }

| 工具 | 路径 | 用途 | 获取方式 |
|---|---|---|---|
| `build_freertos.sh` | SDK 根目录 | 构建、清理、烧录、控制台、大小报告与自动测试 | 随附 |
| `make` ＋ `project.build` | 各应用的 `Makefile` | 构建单个应用 | 随附 |
| `serial_monitor.py` | `tools/` | 读取控制台输出，可先发送一行命令、等待指定字符串并保存到文件（macOS、Linux；非交互式终端） | 随附 |
| `create_ota.py` | `tools/` | 把 IntelProCube 的合并镜像打包成 boot2 OTA 包 | 随附 |
| 浏览器版图像 Teach | `tools/teach_web/` | 在 Chrome／Edge 中采集图像、训练分类器并部署到 `ipro_reef_teach` | 随附 |
| `mfg_payload.py` | `apps/ai/ipro_reef_teach/` | 生成 `ipro_reef_teach` 的 `--mfg` 烧录内容（模式与声纹模型） | 随附 |
| Reef BLE OTA 工具 | `apps/bluetooth/ble/ipro_ble_remote/tools/` | `make_reef_ota.sh`、`reef_ota.py`、`reef_ble_test.py`，以及 Android 演示 App `ipro_remote_demo.apk`（在应用目录中） | 随附 |
| `parse_kconfig_dynamic.py` | `tools/script/` | 把 Kconfig 树导出为 JSON（需要 kconfiglib，构建流程不使用） | 随附 |
| CMake 3.15 | `tools/cmake/` | 系统中没有 `cmake` 时的备用版本，仅限 Linux x86-64 | 随附 |
| Zephyr 脚本 | `tools/zephyr/` | Zephyr 工作区、构建、烧录与控制台（`ipro7_evb`、`ipro7ai_evk` 板型） | 随附 |
| IntelProCube v0.6.3 命令行烧录工具 | `ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | 通过串口烧录固件、分区表、boot2 与 `mfg` 内容 | 未包含在 V2.2.0 中，请联系 INTELPRO |
| RISC-V 工具链 | `/opt/toolchain/riscv_ipro7/` | 编译（GCC 14，`riscv64-unknown-elf-`） | 未包含在 V2.2.0 中，请联系 INTELPRO |
| IPRO AI Studio | — | IPRO AI Teach、模型转换与部署 | 不在 SDK 中，从 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载 |
| OpenOCD／GDB 连接配置、板级自动测试脚本 `tools/board_test.sh`、崩溃转储主机端工具 | — | 片上调试、自动上板测试、读取 `==DUMP_READY:` 之后的内存 | 未包含在 V2.2.0 中，请联系 INTELPRO |
| `tools/kconfig/menuconfig.py`、`configs/` 默认配置目录、OTA 签名用的 `ota_products.py` | — | `make menuconfig`、`make defconfig`、`create_ota.py --sign-key` | 未包含在 V2.2.0 中 |

本版本没有通过 JTAG／GDB 进行片上调试的配置与步骤；调试以串口控制台、日志与离线的 `addr2line` 为主，见[调试与故障排除](debugging.md)。

## 环境变量 { #environment }

| 变量 | 使用的工具 | 作用 |
|---|---|---|
| `IPRO_FLASH_TOOL` | `build_freertos.sh`、`make_reef_ota.sh`、`tools/zephyr/flash.sh`、`west flash` | IntelProCube 命令行工具的路径。未设置时在 `PATH` 中查找与本机操作系统对应的工具名称 |
| `IPRO_SERIAL_PORT` | `build_freertos.sh`、`tools/zephyr/` 脚本、`west flash` | 默认串口。未设置且未指定 `-p` 时，若系统中只有一个 USB 串口就自动使用它 |
| `IPRO_CHIP_VARIANT` | `build_freertos.sh flash` | 烧录时的 `--chip-variant`（`IPRO7` 或 `IPRO7AI`）。未设置时根据应用配置自动选择，见 [build_freertos.sh](#build-cli) |
| `IPRO_FLASH_PT` | `build_freertos.sh flash` | 烧录时的 `--pt` 分区表。未设置时不传 `--pt`，由工具使用默认分区表 |
| `IPRO_PROBE_PORT` | `west flash` | IPRO Debug Probe 的 UART 桥接端口，默认与 `--port` 相同 |
| `CROSS_COMPILE` | `make`、`build_freertos.sh build` | 工具链前缀；在环境或命令行中设置时优先于 `.config` 的 `CONFIG_CROSS_COMPILE` |
| `IPRO_TOOLCHAIN` | `tools/zephyr/bootstrap.sh` | Zephyr 工作区使用的工具链目录，默认 `/opt/toolchain/riscv_ipro7` |
| `IPRO_ZEPHYR_WS` | `tools/zephyr/build.sh`、`ci_build.sh` | Zephyr 工作区位置，默认 `<SDK>/zephyr-workspace` |

## build_freertos.sh { #build-cli }

```text
./build_freertos.sh [动作...] [选项] <项目>
```

动作可以串联，依次执行；任一动作失败即停止。未指定动作时执行 `build`。这是 bash 脚本，在 macOS 与 Linux 上运行。

| 动作 | 说明 |
|---|---|
| `build` | 执行 `make -C <应用>`，日志写入 `<构建目录>/build.log`，成功时打印 `.bin` 路径与大小；失败时打印日志的最后 30 行 |
| `clean` | 删除构建目录 |
| `flash` | 以应用的控制台波特率发送 `reboot_dl`，等待 2 秒，再用 IntelProCube 工具烧录：`--chipname ipro7 --chip-variant <自动> --baudrate 921600`，有 `-P` 时加上 `--pt`。以输出中的 `[All Success]` 判定成功。不会先构建 |
| `monitor` | 以应用的控制台波特率打开 `serial_monitor.py`，先发送 `reboot`，`-t` 秒后退出 |
| `size` | 对 ELF 执行 `size` 与 `size -A`（列出段信息的前 30 行） |
| `test` | 构建、烧录，再发送 `reboot` 并等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；退出码 0 表示通过、1 表示失败、2 表示超时 |

控制台波特率取自所用配置文件中的 `CONFIG_PLATFORM_UART_BAUDRATE`，未设置时为 115200。

| 选项 | 说明 | 默认值 |
|---|---|---|
| `-p, --port PORT` | 串口 | `$IPRO_SERIAL_PORT`，否则为唯一的 USB 串口 |
| `-t, --timeout SEC` | `monitor`、`test` 的秒数 | `30` |
| `-w, --wait-for PAT` | `monitor` 等待的正则表达式 | — |
| `-d, --defconfig FILE` | 改用应用目录中的替代配置文件，构建到 `build_<名称>/`（`defconfig_reef` → `build_reef/`） | — |
| `-c, --chip-variant V` | 烧录的 `--chip-variant`：`IPRO7` 或 `IPRO7AI` | `$IPRO_CHIP_VARIANT`；否则配置文件中有 `CONFIG_IPRO7AI_REEF=y` 或 `CONFIG_IPRO7AI_EVK=y` 时为 `IPRO7AI`，其余为 `IPRO7` |
| `-P, --pt TABLE` | 烧录的分区表：`.toml` 路径（转为绝对路径后传给工具），或工具 `chips/ipro7/partition/` 下的表名 | `$IPRO_FLASH_PT`，否则不传 |
| `-j, --jobs N` | 外层 `make` 的并行任务数；内层 CMake 构建固定为 `-j4` | — |
| `-v, --verbose` | 显示完整构建输出 | — |
| `-l, --list` | 按分类列出 `apps/` 下全部 40 个项目 | — |
| `-h, --help` | 帮助 | — |

`<项目>` 可以写应用名称（`ipro7ai_reef_demo`），或 `apps/` 下的路径（`platform/ipro7ai_reef_demo`）。名称不唯一或找不到时，会列出候选名称。`-l` 的说明栏取自 `.config` 第一行注释，部分应用会显示为空。

在 Reef 上一次完成构建、烧录并打开控制台（首次烧录前，板上还没有能响应 `reboot_dl` 的 SDK 固件，请先按[进入下载模式](debugging.md#download-mode)手动进入）：

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

依次输出：

```text
→ Entering download mode...
→ Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
...
✓ Flash succeeded (…)
→ Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
```

其他 Reef 配置用 `-d` 选择，例如：

```bash
./build_freertos.sh -d defconfig_reef build ipro_ble_remote          # 输出在 build_reef/build_out/
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam
./build_freertos.sh -l                                              # 列出 40 个项目
./build_freertos.sh size ipro7ai_reef_demo
```

产物位于 `<应用>/build/build_out/`（使用 `-d` 时为 `build_<名称>/build_out/`）：`<应用>_<芯片>.bin`、`.elf`、`.map`，芯片取自 `CONFIG_CHIP`（IPRO7 应用为 `_IPRO7`，IPRO6S 应用为 `_IPRO6`）。

!!! warning "build_freertos.sh 的限制"
    - `flash` 固定传 `--chipname ipro7`：IPRO6S 应用（例如 FIN 卡固件 `ipro6_if_wifi`）请直接用 IntelProCube 的 `--chipname ipro6` 烧录。
    - 无法传 `--boot2`、`--mfg` 或 `--skip-ota`：`ipro_ble_remote` 的首次烧录（boot2 ＋ A/B 分区表）与 `ipro_reef_teach`（自带分区表与 `mfg` 内容）请直接使用 [IntelProCube 工具](#flash-tool)。
    - 没有 `BOARD=` 选项；`config_<板子>` 文件可用 `-d config_evk` 指定，输出在 `build_config_evk/`。
    - 烧录工具在当前工作目录下运行；`-P` 请给出 `.toml` 的完整路径。
    - `size` 固定使用 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size`，不读取 `CROSS_COMPILE`。

## make 目标 { #make-targets }

每个应用的 `Makefile` 都转而调用 SDK 根目录的 `project.build`（CMake 以 `Unix Makefiles` 生成器配置，再以 `make -j4` 构建）。

| 命令 | 说明 |
|---|---|
| `make -C apps/<分类>/<应用>` | 以 `.config` 构建到 `build/` |
| `make -C apps/<分类>/<应用> clean` | 删除构建目录（加 `DEFCONFIG=` 时删除对应的 `build_<名称>/`） |
| `make -C apps/<分类>/<应用> DEFCONFIG=defconfig_<名称>` | 以替代配置构建到 `build_<名称>/`，不改动 `.config` |
| `make -C apps/<分类>/<应用> CROSS_COMPILE=<路径>/bin/riscv64-unknown-elf-` | 指定工具链前缀，优先于 `.config` 的 `CONFIG_CROSS_COMPILE` |
| `make -C apps/multimedia/ipro_agora_sentino BOARD=evk` | 只有 `ipro_agora_sentino`（默认 `reef`＝`.config`）与 `ipro_pdm_mic_demo`（默认 `evb`）支持 `BOARD=`：改用 `config_<板子>`，构建到 `build_config_<板子>/` |

- CMake：优先使用 `PATH` 上的 `cmake`，找不到时才用 `tools/cmake/`（Linux x86-64）；两者都没有时停在 `No cmake found`。
- 每次构建后，`compile_commands.json` 会复制到 SDK 根目录，供编辑器使用。
- `make menuconfig` 需要未随附的 `tools/kconfig/menuconfig.py`；部分 `Makefile` 的 `defconfig`、`list-defconfigs` 目标会到未随附的 `configs/` 目录中查找。请直接编辑 `.config`，或另存为 `defconfig_<名称>` 再以 `DEFCONFIG=` 构建。

## IntelProCube 烧录工具 { #flash-tool }

烧录使用 IntelProCube v0.6.3 的命令行工具，未包含在 V2.2.0 中，请联系 INTELPRO。工具从自己的 `chips/` 目录读取芯片文件，请在 IntelProCube 目录下运行。下表根据 SDK 内的 README 与脚本整理，完整选项以工具本身为准。

| 选项 | 说明 |
|---|---|
| `--chipname ipro7` | IPRO7／IPRO7AI（Reef）。IPRO6S（例如 FIN 卡）用 `--chipname ipro6` |
| `--chip-variant IPRO7AI` | Flash 引脚配置：IPRO7AI（Reef、QFN56）用 `IPRO7AI`（`0x9`），IPRO7 EVB 用 `IPRO7`（`0x2`）。工具会把它写入自己的 `chips/ipro7/eflash_loader/eflash_loader_cfg.ini`，更换开发板时务必重新指定 |
| `--port` | 串口：USB 转 UART 线，或 IPRO Debug Probe 名称以 `02` 结尾的端口 |
| `--baudrate 921600` | 烧录波特率，与应用的控制台波特率无关 |
| `--firmware` | 要烧录的 `.bin` |
| `--pt` | 分区表（`.toml`）：工具目录下的相对路径（例如 `chips/ipro7/partition/partition_cfg_2M.toml`）或完整路径。未指定时使用工具的默认分区表 |
| `--boot2` | 同时烧录 boot2 镜像（例如工具内的 `chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin`）；`ipro_ble_remote` 的 Reef OTA 需要 |
| `--mfg` | 写入 `mfg` 分区的文件（AI 模型、`ipro_reef_teach` 的模式与声纹模型） |
| `--skip-ota` | 配合应用自带的分区表使用，例如 `ipro_reef_teach` |
| `--build` | 只生成合并镜像 `chips/ipro7/img_create_iot/whole_img.bin`，不烧录；供 [`create_ota.py`](#ota-package) 使用 |

Reef 出厂固件的烧录（先让开发板[进入下载模式](debugging.md#download-mode)）：

```bash
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 \
    --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

成功时输出末尾有 `[All Success]`。工具即使失败也以 0 退出，请以这一行判断结果。Linux 用 `./ipro_iot_tool_linux`，Windows 用 `ipro_iot_tool.exe` 与 `COM5` 这类端口名。各 Reef 应用需要的分区表与 `--boot2`、`--mfg` 见 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)。

## serial_monitor.py { #serial-monitor }

```text
python3 tools/serial_monitor.py <串口> [--baud 115200] [--timeout 30]
                                [--send CMD] [--wait-for PATTERN] [--log FILE]
```

以 Python 标准库的 termios 打开串口，不需要 pyserial；可在 macOS 与 Linux 上运行，不适用于 Windows。它只读取输出（可在开始时发送一行命令），不是交互式终端；要逐行输入命令，请用 `screen`、`minicom` 或其他串口终端程序。

| 选项 | 说明 | 默认值 |
|---|---|---|
| `--baud` | 波特率；macOS 与 Linux 都可使用 921600、2000000 等高波特率 | `115200` |
| `--timeout` | 监视秒数；`0` 表示一直运行到按下 Ctrl-C | `30` |
| `--send` | 开始监视前发送的一行命令，例如 `reboot`、`reboot_dl`、`reef selftest` | — |
| `--wait-for` | 正则表达式；匹配成功即退出 | — |
| `--log` | 把原始输出另存为文件 | — |

| 退出码 | 含义 |
|---|---|
| 0 | 匹配成功，且匹配到的字符串含 `PASSED` |
| 1 | 匹配成功，但匹配到的字符串不含 `PASSED` |
| 2 | 超时，未匹配到 |
| 3 | 无法打开串口或发送命令 |
| 130 | 按 Ctrl-C 中止 |

```bash
# Reef 控制台（115200），发送自检命令，10 秒后退出
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# ipro7_jpeg_decode 的 Reef 配置（921600），持续监视并保存到文件
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0 --log console.log

# 让运行中的固件重启并进入下载模式（输出 reboot to download mode）
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
```

macOS 请使用 `/dev/cu.*`，`/dev/tty.*` 会等待载波检测而卡住。烧录前先退出监视，释放串口。

## create_ota.py { #ota-package }

把 IntelProCube 生成的合并镜像打包成 boot2 OTA 包：默认以 XZ 压缩并输出 `<输入文件名>.xz.ota`，加 `--raw` 则不压缩并输出 `<输入文件名>.ota`。输入必须是以 `IPNP` 开头、含启动头的合并镜像（工具的 `chips/ipro7/img_create_iot/whole_img.bin`），而不是 SDK 构建出的 `.bin`；格式不符时脚本会停止。

```text
python3 tools/create_ota.py <whole_img.bin> [--raw] [-o OUTPUT] [--hw-ver STR] [--fw-ver STR]
```

| 选项 | 说明 |
|---|---|
| `--raw` | 不压缩 |
| `-o, --output` | 输出文件 |
| `--hw-ver` | 写入头部的硬件版本字符串；请明确指定，不要依赖默认值 |
| `--fw-ver` | 写入头部的固件版本字符串（默认 `OTA_V1.0.0`） |
| `--sign-key`、`--product` 等签名选项 | 需要未随附的 `ota_products.py`，V2.2.0 中无法使用 |

在 Reef 上，`ipro_ble_remote` 的 `make_reef_ota.sh` 会代为调用工具的 `--build` 与本脚本，见 [Reef 应用的主机端工具](#reef-tools)。OTA 的整体流程见 [OTA 更新](../guides/ota.md)。

## Reef 应用的主机端工具 { #reef-tools }

### 浏览器版图像 Teach：tools/teach_web { #teach-web }

无需安装 IPRO AI Studio，在 Chrome 或 Edge 中为 Reef 的摄像头采集图像、训练分类器并通过 USB 部署。开发板需烧录 `ipro_reef_teach` 并处于 `image` 模式；主机需要 Python 3.8 及以上版本。

<div class="ipro-steps" markdown>

1. **启动网页服务器**

    ```bash
    python3 tools/teach_web/serve.py
    ```

    在浏览器中打开 `http://localhost:8780`（默认浏览器不是 Chrome／Edge 时，把网址粘贴到其中之一）。

2. **连接开发板**：允许摄像头权限；点击 **Connect…** 或第一次点击 **Deploy** 时，串口选择 **IPRO7 UVC Cam**。

3. **离线电脑**：先在联网时执行一次 `python3 tools/teach_web/serve.py --fetch-runtime`，把约 22 MB 的 LiteRT.js 下载到本机。

</div>

### ipro_reef_teach 的 mfg 内容：mfg_payload.py { #mfg-payload }

首次烧录 `ipro_reef_teach` 时，`--mfg` 写入的内容包含启动模式与声纹模型：

```bash
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
```

`--mode` 可为 `image`、`voice` 或 `sensor`。生成的 `reef_teach_mfg.bin` 以 `--mfg` 交给 IntelProCube，烧录命令见[示例页面](../examples/ipro_reef_teach.md)；只更新固件时不要带 `--mfg`。

### ipro_ble_remote 的 Reef OTA 工具 { #reef-ota-tools }

| 工具 | 命令 | 结果 |
|---|---|---|
| `make_reef_ota.sh` | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh` | 先以 `DEFCONFIG=defconfig_reef` 构建；生成 `build_reef/build_out/ipro_ble_remote_reef.xz.ota`（约 345 KB） |
| `reef_ota.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py <升级包.xz.ota>` | 通过 BLE（bleak）把升级包传给名为 `IPRO-Remote` 的开发板，打印进度与状态 |
| `reef_ble_test.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ble_test.py` | 以 bleak 作为 central 测试 Reef 的 GATT 服务（`info led env sound tone img`；`keys`、`motion` 需要有人操作），拍摄的 JPEG 保存在脚本所在目录 |
| `ipro_remote_demo.apk` | 安装到 Android 手机 | `ipro_ble_remote` 的演示 App，可推送 `.xz.ota` 升级包 |

两个 Python 脚本需要 bleak：`python3 -m venv .venv && .venv/bin/pip install bleak`。OTA 只适用于以 boot2 与 `partition_cfg_2M_remote_ab.toml` 烧录过的开发板；不要在 Reef 上以标准 `partition_cfg_2M.toml` 做 OTA。

### 其他 Reef 应用的工具 { #reef-app-tools }

| 工具 | 用途 |
|---|---|
| `apps/multimedia/ipro7_jpeg_decode/host/jpeg_check.py photo.jpg [--fix out.jpg]` | 在电脑上检查 JPEG 能否在 IPRO7 上解码，必要时转换格式 |
| `apps/multimedia/ipro7_jpeg_decode/host/jdec_host.py -p <端口> upload photo.jpg --go 565` | 通过控制台把 JPEG 发送给开发板解码，并可取回结果进行比对 |
| `apps/multimedia/ipro7_jpeg_decode/host/run_host_tests.py` | 在电脑上以 libjpeg 对照验证解码器（需要 `cc`、`djpeg`） |
| `apps/multimedia/ipro_agora_sentino/setup_ncm_nat.sh` | 在 macOS 上为 USB-NCM 连接配置 NAT |

## Zephyr 脚本 { #zephyr-tools }

`tools/zephyr/`（`bootstrap.sh`、`build.sh`、`flash.sh`、`monitor.sh`、`ci_build.sh`）用于 Zephyr 的 `ipro7_evb` 与 `ipro7ai_evk` 板型；本版本没有 Reef 的 Zephyr 板型。用法见 [Zephyr RTOS](../guides/zephyr.md)。

## 大小与内存分析 { #size-analysis }

| 方法 | 命令或位置 | 内容 |
|---|---|---|
| 链接器内存报告 | 每次构建的最后几行（`build_freertos.sh` 写入 `build.log`） | 各内存区段（`flash`、`ocram`，启用时另有 `psram`）的使用量与百分比 |
| `size` 动作 | `./build_freertos.sh size <应用>` | text／data／bss 总计与各段大小 |
| Map 文件 | `<构建目录>/build_out/<应用>_IPRO7.map` | 每个目标文件与库占用的地址与大小 |
| 符号排序 | `riscv64-unknown-elf-nm --size-sort -S <ELF>` | 按大小列出符号，找出最大的函数与变量 |
| 反汇编 | 在 `.config` 中设置 `CONFIG_GENERATE_ASM=y` | 构建时另外生成 `<应用>_IPRO7.asm` |

```bash
./build_freertos.sh size ipro7ai_reef_demo
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-nm --size-sort -S \
    apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf | tail -20
```

同时启用 `CONFIG_AI_SUPPORT` 与 `CONFIG_MM_SUPPORT` 时，链接器脚本会把 OCRAM 区段缩小为 64 KB（`CONFIG_EM_SIZE` 为 0）或 48 KB（`CONFIG_EM_SIZE` 大于 0），CMake 配置阶段会打印 `AI+MM …: OCRAM=…`。内存地址分布见 [IPRO7](../hardware/chips/ipro7.md)，OCRAM 预算见[构建系统与配置](../guides/build-system.md)。

## 自动测试 { #automated-testing }

`./build_freertos.sh test ipro_unit_test` 会构建、烧录并等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；`ipro_unit_test` 需要 IPRO7 EVB。Reef 的板上自检是出厂固件的 `reef selftest`，见[调试与故障排除](debugging.md#board-testing)。

## 其他工具 { #other-tools }

| 工具 | 说明 |
|---|---|
| `tools/script/parse_kconfig_dynamic.py Kconfig [PROJECT_SYMBOL]` | 把 Kconfig 树输出为 JSON；需要 kconfiglib。构建由 `cmake/generate_autoconf.cmake` 直接读取 `.config` 生成 `autoconf.h`，不使用此脚本 |
| `components/audio/tools/gen_asrc_coef.py` | 生成音频采样率转换系数 |
| `*/test_host/run.sh` | 在电脑上运行的单元测试，例如 `components/audio/test_host/run.sh`、`apps/ai/ipro_reef_teach/sensor/test_host/run.sh` |
| 其他开发板的工具 | IPRO7AI EVK 示例的 `flash.sh`、`enter_dl.py`，`ipro6_fmac` 的 `tools/mkimg.py`（IPRO6S EVK），`tools/android/IproMicDemo/`（`ipro_pdm_mic_demo`）：需要对应的开发板 |

## 开发流程 { #dev-workflow }

在 Reef 上修改、构建、烧录并检查控制台的一轮循环，见[构建与烧录流程](../tutorials/build-and-flash.md)；创建自己的应用见[创建第一个自己的应用](../tutorials/first-own-app.md)。调试与常见错误见[调试与故障排除](debugging.md)。
