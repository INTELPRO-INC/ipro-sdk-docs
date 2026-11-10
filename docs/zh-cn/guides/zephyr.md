---
title: "Zephyr RTOS"
description: IPRO SDK 作为 Zephyr v4.4.0 模块：支持的开发板、工作区、用 west 构建与烧录、示例、预编译组件，以及本版本 Zephyr 尚未覆盖的功能
migrate_from:
  - "zephyr-rtos.html#overview"
  - "zephyr-rtos.html#boards"
  - "zephyr-rtos.html#features"
  - "zephyr-rtos.html#samples"
  - "zephyr-rtos.html#prebuilt"
  - "zephyr-rtos.html#limitations"
  - "getting-started.html#zephyr-quickstart"
  - "zephyr-rtos.html#setup"
  - "zephyr-rtos.html#build-flash"
---

# Zephyr RTOS

IPRO SDK 同时也是一个 Zephyr v4.4.0 模块：SDK 的 HAL 与 SoC 驱动通过 Zephyr 的设备驱动 API 提供，可以改用 Zephyr 而不是 FreeRTOS 开发应用。本页是 Zephyr 侧的参考：支持的开发板、工作区、`west` 构建与烧录、示例与限制。FreeRTOS 应用及其构建方式不受影响。

!!! abstract "要点"
    - 开发板：`ipro7_evb`（IPRO7 EVB）与 `ipro7ai_evk`（IPRO7AI EVK）。**V2.2.1 没有 IPRO7AI Reef EVK 的 Zephyr 开发板定义**；在 Reef 上请使用 FreeRTOS 应用。
    - 可用：常用外设驱动、BLE（Zephyr host 配合预编译的 IPRO BLE 控制器）、IEEE 802.15.4 与 OpenThread、MCUboot 配合 MCUmgr 经 BLE 更新。
    - 不可用：低功耗模式，以及摄像头、音频编解码器、USB、SD host、以太网与 NPU 的 Zephyr 驱动。
    - 控制台：UART0，2,000,000 baud。主机需要：带 venv 的 Python 3、git、能访问 GitHub 的网络、CMake 3.20 或更高版本。
    - 第一次构建：先看[工作区](#workspace)，再看[构建、烧录与控制台](#flash-console)。

## 概览 { #overview }

| 文件／目录 | 作用 |
|---|---|
| `west.yml` | SDK 本身是 west manifest repository：固定 Zephyr v4.4.0，只导入允许列表中的模块 |
| `zephyr/module.yml` | 把 SDK 注册为 Zephyr 模块，带入开发板、SoC、devicetree binding 与 `west flash` runner |
| `zephyr/boards/`、`soc/`、`dts/` | 开发板定义、SoC 定义、devicetree binding |
| `zephyr/drivers/`、`hal_glue/`、`include/` | Zephyr 驱动，以及与 SDK HAL 的对接 |
| `zephyr/patches.yml`、`patches/` | SDK 对 Zephyr 的两个补丁，创建工作区时应用 |
| `zephyr/samples/`、`zephyr/tests/` | SDK 示例与测试 |
| `tools/zephyr/` | 创建工作区、构建、烧录与打开控制台的脚本 |

Zephyr 驱动调用 SDK 的 HAL，HAL 直接从 `bsp/` 编译。BLE 使用 Zephyr 的 host 配合 IPRO BLE 控制器库；IEEE 802.15.4 使用 Zephyr 的驱动接口与 OpenThread。

## 支持的开发板 { #boards }

| Zephyr 开发板 | 硬件 | Flash（devicetree） | PSRAM | `west flash` 默认值 |
|---|---|---|---|---|
| `ipro7_evb` | IPRO7 EVB | 2 MB | 无 | `--pt=partition_cfg_2M.toml`，经 IPRO7 CMSIS-DAP 探针进入下载模式 |
| `ipro7ai_evk` | IPRO7AI EVK | 1 MB | 8 MB | `--pt=partition_cfg_1M_boot2.toml`、`--boot=shell` |

- 两块开发板的控制台都在 UART0，2,000,000 baud。
- 分区表名称指的是 IntelProCube 的 `chips/ipro7/partition/` 下的文件。
- SDK 附带 `ipro6s_evb` 的开发板文件，但本版本的 Zephyr 不支持 IPRO6S。

!!! info "IPRO7AI Reef EVK"
    V2.2.1 没有 Reef 的 Zephyr 开发板，Reef 的摄像头、音频、LED 与 microSD 卡槽也没有 devicetree 描述。本版本未验证在 Reef 上运行 Zephyr 镜像。需要在 Reef 上使用 Zephyr 时请联系 INTELPRO。

## 工作区 { #workspace }

`tools/zephyr/bootstrap.sh` 在 SDK 根目录创建 `zephyr-workspace/`。第一次运行会从 GitHub 下载 Zephyr 与模块。

```bash
tools/zephyr/bootstrap.sh              # 创建 zephyr-workspace/
source zephyr-workspace/env.sh         # 设置 ZEPHYR_BASE、CROSS_COMPILE，并把 west 加入 PATH
```

脚本依次：

1. 创建 `zephyr-workspace/.venv` 并安装 west。
2. 用 SDK 的 `west.yml` 初始化 west，执行 `west update`（默认浅克隆）。
3. 应用 `zephyr/patches.yml` 中的补丁。
4. 安装 Zephyr 与 MCUboot 所需的 Python 包。
5. 写出 `env.sh`：`ZEPHYR_TOOLCHAIN_VARIANT=cross-compile`、`CROSS_COMPILE`、`ZEPHYR_BASE`、`PATH`。

| 选项／变量 | 说明 |
|---|---|
| `-w DIR` | 改用其他工作区目录 |
| `--full` | 下载 Zephyr 与模块的完整历史 |
| `IPRO_TOOLCHAIN` | 工具链目录，默认 `/opt/toolchain/riscv_ipro7` |

`west.yml` 只导入 `mbedtls`、`tf-psa-crypto`、`openthread`、`picolibc`、`segger`、`mcuboot`、`liblc3` 与 `zcbor`。

!!! warning "再次运行 bootstrap"
    更新前，bootstrap 会把补丁涉及的 Zephyr 文件还原为固定版本，对这些文件的本地修改会丢失。

Zephyr 需要 CMake 3.20 或更高版本。`tools/cmake/` 中附带的是 Linux x86-64 用的 CMake 3.15，仅供 FreeRTOS 构建使用。

## 构建、烧录与控制台 { #flash-console }

先 `source env.sh`，再在 `zephyr-workspace/` 中执行：

```bash
west build -b ipro7_evb zephyr/samples/hello_world                       # Zephyr 自带的示例
west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke     # SDK 的示例
west flash -d build/smoke
../tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX                  # 控制台，2,000,000 baud
```

在 SDK 根目录中，`tools/zephyr/build.sh [-b ipro7_evb|ipro7ai_evk] [-d DIR] [-p] APP [-- cmake 参数]` 封装了 `west build`，SDK 示例可直接写名称（`tools/zephyr/build.sh -b ipro7ai_evk periph_smoke`）。

`west flash` 使用 SDK 的 `ipro` runner（`zephyr/scripts/runners/ipro.py`）：让开发板进入下载模式，用 IntelProCube 命令行工具写入 `zephyr.bin`，再复位开发板。

| Runner 选项 | 说明 |
|---|---|
| `--boot probe`／`shell`／`manual` | 进入下载模式的方式：IPRO7 CMSIS-DAP 探针（默认）、运行中镜像的 `reboot_dl`，或手动 |
| `--port`、`--probe-port` | 烧录 UART 与探针桥接端口；默认 `$IPRO_SERIAL_PORT`、`$IPRO_PROBE_PORT` |
| `--tool` | IntelProCube CLI 可执行文件；默认 `$IPRO_FLASH_TOOL`，或 `PATH` 中的工具 |
| `--pt` | 分区表：`.toml` 路径，或工具 `chips/<chip>/partition/` 下的表名 |
| `--baudrate`、`--console-baud` | 烧录速率，以及 `--boot shell` 使用的控制台速率；默认都是 2000000 |
| `--no-reset`、`--attempts`、`--tool-arg` | 烧录后停留在下载模式；重试次数（3）；传给工具的额外参数 |

Runner 选项写在 `--` 之后，例如 `west flash -- --boot shell --port /dev/cu.usbserial-XXXX`。

- `west flash` 不传递 `--chip-variant`；IntelProCube 使用保存在 `chips/ipro7/eflash_loader/eflash_loader_cfg.ini` 中的 flash 引脚配置。
- 对于含 MCUboot 的 sysbuild 镜像，`west flash` 会先用 `tools/zephyr/merge_mcuboot.py` 把 MCUboot 与签名后的应用合并为一个镜像。
- `tools/zephyr/flash.sh` 以 115200 baud 发送 `reboot_dl`，运行中的 Zephyr 镜像（2,000,000 baud）收不到；请先手动进入下载模式，或改用 `west flash`。

## 功能范围 { #features }

| 项目 | Zephyr 下 |
|---|---|
| 驱动 | GPIO、UART（含 async）、SPI、I2C、PWM、ADC、DAC、counter／RTC、watchdog、flash、DMA、entropy、hwinfo、I2S／PDM |
| 显示 | IPRO7AI EVK 的 LCD，使用 Zephyr 自带的 ST7789V 驱动 |
| Bluetooth LE | Zephyr host 配合 `components/wireless/bluetooth/ipro_ble_controller/lib/` 中的 IPRO BLE 控制器库 |
| IEEE 802.15.4／Thread | Zephyr 的 IEEE 802.15.4 驱动与 OpenThread，见 [Thread 与 Matter](thread-matter.md) |
| 启动与更新 | 经 sysbuild 的 MCUboot；通过 MCUmgr SMP 经 BLE 上传镜像，见 [OTA 更新](ota.md) |

Zephyr 下用下列配置选择 BLE 控制器库，并用 devicetree overlay 启用 `bt_hci` 节点（`zephyr/samples/bt_peripheral_hr/ipro7.overlay`）：

```ini title="zephyr/samples/bt_peripheral_hr/ipro7.conf（节选）"
CONFIG_IPRO7_EM_SIZE_KB=16
CONFIG_BT_IPRO_CTLR_LIB="link1_periph"
CONFIG_BT_IPRO_CTLR_FEATURE="bt52"
CONFIG_BT_MAX_CONN=1
CONFIG_ENTROPY_GENERATOR=y
```

ISO 与 LE Audio 改用 `zephyr/samples/bt_le_audio/iso.conf`（`link1`、`bt54_iso2`、`CONFIG_IPRO7_EM_SIZE_KB=32`）。库组合见 [BLE 开发](ble.md)。

## 示例 { #samples }

| 示例（`zephyr/samples/`） | 开发板 | 内容 |
|---|---|---|
| `periph_smoke` | `ipro7_evb` | 逐一测试驱动：GPIO、UART、SPI、I2C、PWM、flash、DMA、counter、watchdog、TRNG |
| `mcuboot_app` | `ipro7_evb`、`ipro7ai_evk` | 验证 boot2 → MCUboot → 镜像的启动链 |
| `ble_ota` | `ipro7_evb`、`ipro7ai_evk` | MCUboot＋MCUmgr SMP，经 BLE 更新 |
| `bap_broadcast_source` | `ipro7_evb`、`ipro7ai_evk` | LE Audio 广播源（LC3） |
| `bap_broadcast_sink` | `ipro7ai_evk` | LE Audio 广播接收，从 EVK 扬声器播放 |
| `le_audio_headset` | `ipro7ai_evk` | LE Audio unicast 耳机（CAP acceptor） |
| `evk_demo` | `ipro7ai_evk` | 用于 EVK 的 LCD、麦克风、扬声器与摄像头预览的 `evk` shell 命令 |
| `ieee802154_shell` | `ipro7_evb` | IEEE 802.15.4 shell；另附 OpenThread 用的 `ot.conf` 与 `csl.conf` |
| `bt_peripheral_hr`、`bt_le_audio` | – | 供 Zephyr 自带示例使用的配置片段 |

Zephyr 自带的示例配合 SDK 的配置片段（在 `zephyr-workspace/` 中执行）：

```bash
west build -b ipro7_evb zephyr/samples/bluetooth/peripheral_hr -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/bt_peripheral_hr/ipro7.overlay
west build -b ipro7_evb zephyr/samples/net/openthread/shell -- \
    -DEXTRA_CONF_FILE=$PWD/../zephyr/samples/ieee802154_shell/ot.conf \
    -DEXTRA_DTC_OVERLAY_FILE=$PWD/../zephyr/samples/ieee802154_shell/app.overlay
```

`zephyr/tests/` 中有 15 组驱动测试（`zephyr/tests/drivers/`）与 3 组 SoC 测试（`camclk`、`psram`、`reboot`），都是标准的 ztest。

## 预编译组件 { #prebuilt }

Zephyr 构建时，除下列组件外，包括 HAL 在内的 SDK 代码都从源代码编译：

| 组件 | 位置 |
|---|---|
| IPRO BLE 控制器 | `components/wireless/bluetooth/ipro_ble_controller/lib/` |
| RF 驱动 | `components/wireless/rf/ipro7_rf/lib/zephyr/`（`libipro_rf_core.a`、`libipro_rf_core_short_enums.a`） |
| IEEE 802.15.4 MAC | `components/wireless/ieee802154/lib/zephyr/`（`libipro_ieee802154_core.a`、`libipro_ieee802154_core_short_enums.a`） |

链接 BLE 控制器时，整个镜像以 `-fshort-enums` 编译，构建会自动选用对应版本的 RF 与 802.15.4 库。

## 本版本的限制 { #limitations }

- 没有 IPRO7AI Reef EVK 的 Zephyr 开发板；Zephyr 不支持 IPRO6S。
- 低功耗模式：Zephyr 的 `pm_state` 不会进入 PDS 或 HBN，BLE 控制器也不会睡眠。需要低功耗请使用 FreeRTOS，见[低功耗](low-power.md)。
- 没有摄像头、音频编解码器、USB、SD host、以太网与 NPU 的 Zephyr 驱动；唯一的显示是 IPRO7AI EVK 的 LCD。
- Zephyr 下 IPRO7 没有 Wi-Fi：`zephyr/drivers/wifi` 是 IPRO6S 芯片本身的驱动。
- 需要上述功能的产品请使用 FreeRTOS 应用。

## 相关文档 { #related }

- [Thread 与 Matter](thread-matter.md)：OpenThread 配置与首次测试。
- [OTA 更新](ota.md)：MCUboot 与 MCUmgr。
- [BLE 开发](ble.md)：控制器库与 BLE API。
- [工具命令行](../reference/tools.md)：`tools/zephyr/` 脚本。
