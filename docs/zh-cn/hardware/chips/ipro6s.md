---
title: "IPRO6S"
description: IPRO6S 的规格、V2.2.0 附带的三个 Wi-Fi 6 应用及其配置、构建与烧录，以及在 IPRO7AI Reef EVK 上作为 FIN Wi-Fi 卡的用法
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S

IPRO6S 是内置 Wi-Fi 6 的 RISC-V SoC，与 IPRO7 使用同一套 SDK 源代码树和同一套工具链构建。V2.2.0 附带三个 IPRO6S Wi-Fi 应用：独立联网的 `ipro6_demo`、把 Wi-Fi 经 SDIO 或 USB 桥接给主处理器的 `ipro6_if_wifi`，以及供 Linux 主机使用的 FullMAC 固件 `ipro6_fmac`。在 IPRO7AI Reef EVK 上，IPRO6S 是插在 microSD 卡座中的 FIN Wi-Fi 卡，经 SDIO 为 IPRO7AI 提供联网能力。

<div class="ipro-facts" markdown>
<div><strong>Wi-Fi 6</strong><span>芯片内置</span></div>
<div><strong>RV32IMAFC</strong><span>与 IPRO7 相同的工具链</span></div>
<div><strong>3</strong><span>IPRO6S 应用</span></div>
<div><strong>ipro6</strong><span>烧录时的 <code>--chipname</code></span></div>
</div>

## 芯片规格 { #ipro6s }

| 项目 | IPRO6S |
|---|---|
| 内核 | RISC-V RV32IMAFC，含 DSP 扩展 |
| 无线 | 内置 Wi-Fi 6 |
| NPU／ISP | 无 |
| RTOS | FreeRTOS V11 |
| 参考板 | IPRO6S EVB（供货请联系 INTELPRO）；Reef 的 FIN 卡 |

| 区域 | 大小 | 起始地址 | 说明 |
|---|---|---|---|
| Flash | 2 MB | `0x13000000` | |
| TCM RAM | 320 KB | `0x11000000` | 代码与数据；精简配置为 280 KB |
| Wi-Fi RAM | 160 KB | `0x21050000` | |
| HBN RAM | 4 KB | `0x20090000` | |

IPRO6S 应用用下列配置选择芯片，镜像文件名的芯片后缀为 `IPRO6`：

```ini title="apps/platform/ipro6_if_wifi/defconfig_ipro6_sdio（节选）"
CONFIG_IPRO6=y
CONFIG_CHIP="IPRO6"
CONFIG_CPU_ID="intelpro_ipro7"     # 与 IPRO7 共用工具链
CONFIG_FREERTOS_SUPPORT=y
```

## 本版本 SDK 支持 { #status }

| 项目 | V2.2.0 |
|---|---|
| 应用 | `ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`（`apps/platform/`） |
| Wi-Fi 6 | MAC（`components/wireless/macsw`）、fhost API、wpa_supplicant 与 lwIP 适配层（`components/wireless/wifi6`）、RF 驱动（`components/wireless/rf/ipro6_rf`），均为按应用配置预编译的库 |
| 低功耗 | DTIM 低功耗固件镜像 `bsp/hal/lp_framework/ipro6/prebuilt/ipro6_lpfw.bin`，由低功耗配置嵌入 |
| Bluetooth | IPRO6S 的蓝牙控制器库与双模（BR/EDR）应用未包含在 V2.2.0 中，请联系 INTELPRO。本版本的 IPRO6S 应用只使用 Wi-Fi |
| Zephyr RTOS | 附带 `ipro6s_evb` 板型文件，但本版本不支持 IPRO6S 的 Zephyr 构建 |
| 烧录 | IntelProCube v0.6.3 命令行工具（需另行获取），`--chipname ipro6`；`build_freertos.sh` 的 `flash` 只支持 IPRO7 |

## 应用与配置 { #apps }

每个 IPRO6S 应用都用 `DEFCONFIG=` 选择配置。下表是经过构建验证的配置；应用的 `.config` 是第一个配置的副本。

| 应用 | 配置 | 内容 |
|---|---|---|
| `ipro6_demo` | `defconfig_ipro6_lpwifi` | Wi-Fi 6 Station 与 soft-AP、lwIP、shell，外加 DTIM 省电 |
| | `defconfig_ipro6_lp` | 低功耗演示，不含 Wi-Fi |
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 6 桥接：主处理器经 SDIO 看到类似以太网的接口；Reef 的 FIN 卡固件 |
| | `defconfig_ipro6_usb` | 同上，经 USB |
| | `defconfig_ipro6_lp` | 低功耗演示，不含 Wi-Fi |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | 供 Linux cfg80211 主机使用的 FullMAC 固件（镜像 `ipro6s_fmac.img`）；`make` 默认使用这个配置 |
| | `defconfig_ipro6_fmac_loader` | 经 SDIO 或 USB 接收 FullMAC 固件的 Flash 加载程序 |

- `ipro6_demo/defconfig_ipro6_lpwifi_ping` 与 `ipro6_fmac/defconfig_ipro6_fmac_ap` 没有设置 `CONFIG_WIRELESS_LIB_VARIANT`，不在验证过的配置之列；使用前请联系 INTELPRO。
- `ipro6_fmac` 的 Linux 主机端驱动未包含在 V2.2.0 中。
- 这三个应用以 IPRO6S EVB 为目标（`CONFIG_BOARD="EVB"`）；在 Reef 上只有 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio` 运行在 FIN 卡上。

## 构建 { #build }

在 SDK 根目录执行，以 FIN 卡固件为例：

```bash
make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
```

构建结束时链接器打印 Flash 与 RAM 用量，镜像位于 `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。输出目录为 `build_` 加上去掉 `defconfig_` 后的配置名称；`ipro6_fmac` 的 Makefile 默认带 `DEFCONFIG=defconfig_ipro6_fmac`，所以直接 `make` 也输出到 `build_ipro6_fmac/`。`build_freertos.sh -d defconfig_ipro6_sdio build ipro6_if_wifi` 也能构建，但不能烧录 IPRO6S。

### Wi-Fi 库与自定义配置 { #wifi-libs }

Wi-Fi 的 MAC、fhost、wpa_supplicant、lwIP 适配层与 RF 驱动按应用配置各预编译一份，放在各组件的 `lib/<应用>-<配置>/` 下，由配置中的 `CONFIG_WIRELESS_LIB_VARIANT` 选择，例如 `defconfig_ipro6_sdio` 中的：

```ini
CONFIG_WIFI6=y
CONFIG_USE_MACSW=y
CONFIG_WIRELESS_LIB_VARIANT="ipro6_if_wifi-ipro6_sdio"
```

自定义配置时，保留上表中某一个配置的 Wi-Fi 选项及其 `CONFIG_WIRELESS_LIB_VARIANT`；预编译库只为这些组合提供。

`ipro6_demo` 用 `CONFIG_WIFI_MEM_PROFILE_PERF`（默认）、`_BALANCED`、`_APP` 三选一，决定 Wi-Fi 缓冲区与应用堆如何分配 RAM；在配置文件中加入一行即可切换，修改后要删除构建目录再重新构建。各配置的可用堆与吞吐量见 `apps/platform/ipro6_demo/profile_selection_readme.md`。

## 烧录 { #flashing }

IPRO6S 镜像用 IntelProCube 命令行工具的 `--chipname ipro6` 烧录，在 IntelProCube 目录下执行：

```bash
./ipro_iot_tool_macos --chipname ipro6 --config chips/ipro6/conf/iot.toml --skip-ota
```

`chips/ipro6/conf/iot.toml` 要指向刚构建的 `.bin`。工具即使失败也会以 0 退出，请根据输出中的 `[All Success]` 判断结果。IPRO6S EVB 进入下载模式的操作请联系 INTELPRO；Reef 上的 FIN 卡见下一节。

## Reef 上的 FIN Wi-Fi 卡 { #dual-chip }

FIN 卡是把 IPRO6S 做在 SD 卡外形板卡上的 Wi-Fi 卡，插入 Reef 的 microSD 卡座，以 SDIO 从机方式工作，由卡座的 SD_VDD 供电。IPRO7AI 是主控 SoC，负责应用、AI、BLE、音频与 IP 协议栈；FIN 卡上的 IPRO6S 运行 `ipro6_if_wifi`（`defconfig_ipro6_sdio`），提供无线连接。

```mermaid
flowchart LR
    A["IPRO7AI（Reef）<br/>应用 + ipronet_host + lwIP"] -- "SDIO 4-bit（microSD 卡座）" --> B["IPRO6S FIN 卡<br/>ipro6_if_wifi"]
    B -- "Wi-Fi 6" --> C["无线接入点"]
```

IPRO7AI 端的主机组件 `components/network/ipronet_host` 经 SD 主控（GPIO28–33）驱动卡片，把连接呈现为 lwIP 网络接口 `iproeth0`。使用它的 Reef 应用：

| 应用 | 配置 | 内容 |
|---|---|---|
| [`ipro7ai_reef_demo`](../../examples/ipro7ai_reef_demo.md) | `defconfig_wifi_ipro6s` | Wi-Fi 连接与 RTSP 摄像头视频流 `rtsp://<ip>:8554/av0_0` |
| [`ipro_agora_sentino`](../../examples/ipro_agora_sentino.md) | `.config` | Sentino 云端语音对话，经 FIN 卡联网 |

把 JP3 设在 GPIO 时，卡座电源由 GPIO14 控制，`fin cycle` 可以给卡片重新上电。连接与视频流的步骤见 [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp) 与 [Wi-Fi 与 RTSP 视频流](../../tutorials/wifi-rtsp.md)。

### 更新 FIN 卡固件 { #fin-update }

`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 构建提供两种方式：

<div class="ipro-steps" markdown>

1. **经 Wi-Fi 更新**：FIN 卡固件（`defconfig_ipro6_sdio` 已设置 `CONFIG_RNM_OTA=y`）接受 IntelProCube 生成的 IPRO6 OTA 包 `FW_OTA.bin.xz.ota`。把升级包放在 Reef 能访问到的 HTTP 服务器上，例如在升级包所在目录执行：

    ```bash
    python3 -m http.server 8000
    ```

2. **在 Reef 控制台连接并更新**：

    ```text
    ipronet_up <ssid> <psk>
    ipro6s_ota http://<主机 IP>:8000/FW_OTA.bin.xz.ota
    ```

    卡片把升级包写入固件分区、用 SHA-256 校验后重启，由 boot2 安装，约需 30–60 秒。成功时控制台打印 `[ota] RESULT OK`，失败时打印 `[ota] RESULT ERR rc=…` 与失败的阶段。只支持 `http://`。

</div>

另一种方式是在 Reef 控制台输入 `ipro6_dl`：它关闭卡片电源，拉高 SD_D0（GPIO29）这个下载引脚后重新上电，让 IPRO6S 进入 BROM 下载模式，之后要经 IPRO6S 的 UART 用 `--chipname ipro6` 烧录；FIN 卡上 UART 的接法未包含在本版本文档中，请联系 INTELPRO。`ipro6_rst` 给卡片重新上电，回到正常启动；`ipro6_pwr 0|1` 手动开关卡片电源。

## 相关文档 { #documents }

- [IPRO7](ipro7.md#networking)：IPRO7 的网络连接方式。
- [IPRO7AI Reef EVK](../boards/reef-evk.md#wifi-rtsp)：FIN 卡、JP3 与 Wi-Fi 命令。
- [网络指南](../../guides/networking.md)：lwIP、以太网与 SDIO Wi-Fi 主机。
- `components/network/ipronet_host/README.md`：主机端 API 与 OTA 流程。
