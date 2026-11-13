---
title: "IPRO6S"
description: IPRO6S 的规格、V2.3.0 附带的三个 Wi-Fi 应用及其配置、构建与烧录，以及在 IPRO7AI Reef EVK 上作为 FIN Wi-Fi 卡的用法
migrate_from:
  - "hardware.html#ipro6s"
  - "architecture.html#dual-chip"
  - "ble-development.html#ipro6s-btdm"
  - "wifi-networking.html#ipro6s-wifi6"
---

# IPRO6S

IPRO6S 是内置 Wi-Fi 的 RISC-V SoC，与 IPRO7 使用同一套 SDK 源代码树和同一套工具链构建。V2.3.0 附带三个 IPRO6S Wi-Fi 应用：独立联网的 `ipro6_demo`、把 Wi-Fi 经 SDIO 或 USB 桥接给主处理器的 `ipro6_if_wifi`，以及供 Linux 主机使用的 FullMAC 固件 `ipro6_fmac`。在 IPRO7AI Reef EVK 上，IPRO6S 是插在 microSD 卡座中的 FIN Wi-Fi 卡，经 SDIO 为 IPRO7AI 提供联网能力。

<div class="ipro-facts" markdown>
<div><strong>Wi-Fi</strong><span>芯片内置</span></div>
<div><strong>RV32IMAFC</strong><span>与 IPRO7 相同的工具链</span></div>
<div><strong>3</strong><span>IPRO6S 应用</span></div>
<div><strong>ipro6</strong><span>烧录时的 <code>--chipname</code></span></div>
</div>

## 芯片规格 { #ipro6s }

| 项目 | IPRO6S |
|---|---|
| 内核 | RISC-V RV32IMAFC，含 DSP 扩展 |
| 无线 | 内置 Wi-Fi |
| NPU／ISP | 无 |
| RTOS | FreeRTOS V11 |
| 参考板 | IPRO6S EVK（供货请联系 INTELPRO）；Reef 的 FIN 卡 |

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

| 项目 | V2.3.0 |
|---|---|
| 应用 | `ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`（`apps/platform/`） |
| Wi-Fi | MAC（`components/wireless/macsw`）、fhost API、wpa_supplicant 与 lwIP 适配层（`components/wireless/wifi6`）、RF 驱动（`components/wireless/rf/ipro6_rf`），均为按应用配置预编译的库 |
| 低功耗 | DTIM 低功耗固件镜像 `bsp/hal/lp_framework/ipro6/prebuilt/ipro6_lpfw.bin`，由低功耗配置嵌入 |
| Bluetooth | IPRO6S 的蓝牙控制器库与双模（BR/EDR）应用未包含在 V2.3.0 中，请联系 INTELPRO。本版本的 IPRO6S 应用只使用 Wi-Fi |
| Zephyr RTOS | 附带 `ipro6s_evb` 板型文件，但本版本不支持 IPRO6S 的 Zephyr 构建 |
| 烧录 | [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 及以上的命令行工具，`--chipname ipro6`；`build_freertos.sh` 的 `flash` 只支持 IPRO7 |

## 应用与配置 { #apps }

每个 IPRO6S 应用都用 `DEFCONFIG=` 选择配置。下表是经过构建验证的配置；应用的 `.config` 是第一个配置的副本。

| 应用 | 配置 | 内容 |
|---|---|---|
| `ipro6_demo` | `defconfig_ipro6_lpwifi` | Wi-Fi Station 与 soft-AP、lwIP、shell，外加 DTIM 省电 |
| | `defconfig_ipro6_lp` | 低功耗演示，不含 Wi-Fi |
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 桥接：主处理器经 SDIO 看到类似以太网的接口；Reef 的 FIN 卡固件 |
| | `defconfig_ipro6_usb` | 同上，经 USB |
| | `defconfig_ipro6_lp` | 低功耗演示，不含 Wi-Fi |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | 供 Linux cfg80211 主机使用的 FullMAC 固件（镜像 `ipro6s_fmac.img`）；`make` 默认使用这个配置 |
| | `defconfig_ipro6_fmac_loader` | 经 SDIO 或 USB 接收 FullMAC 固件的 Flash 加载程序 |

- `ipro6_fmac/defconfig_ipro6_fmac_ap` 没有设置 `CONFIG_WIRELESS_LIB_VARIANT`，不在验证过的配置之列；使用前请联系 INTELPRO。V2.2.x 附带的 `ipro6_demo/defconfig_ipro6_lpwifi_ping` 需要 Wi-Fi 库源代码，V2.3.0 起不在软件包中。
- `ipro6_fmac` 的 Linux 主机端驱动未包含在 V2.3.0 中。
- 这三个应用以 IPRO6S EVK 为目标（`CONFIG_BOARD="EVB"`）；在 Reef 上只有 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio` 运行在 FIN 卡上。

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

## 烧录与上板验证 { #flashing }

下面以 IPRO6S EVK 搭配 IPRO Debug Probe 为例，从构建 `ipro6_demo` 到在控制台看到 Wi-Fi 扫描结果。IPRO6S 镜像用 IntelProCube 命令行工具的 `--chipname ipro6` 烧录；`build_freertos.sh` 的 `flash` 不适用。

需要：

- IPRO6S EVK、2.4 GHz 天线、IPRO Debug Probe 及其 UART 排线、USB-C 电源。
- 按[准备开发环境](../../get-started/environment.md)安装的工具链，以及 SDK V2.3.0（下文写作 `<SDK>`）。
- [IntelProCube](https://github.com/INTELPRO-INC/ipro-cube/releases) 0.7.0.1 及以上：按 [README](https://github.com/INTELPRO-INC/ipro-cube#readme) 下载、校验 SHA-256，解压到新的文件夹（下文写作 `<IntelProCube>`）。用 0.7.0 烧录的镜像无法启动，见[烧录成功却没有启动](#ipro6s-no-boot)。

<div class="ipro-steps" markdown>

1. **构建**：在 `<SDK>` 根目录执行

    ```bash
    make -C apps/platform/ipro6_demo DEFCONFIG=defconfig_ipro6_lpwifi
    ```

    结束时链接器打印各内存区域的用量，其中 `flash` 一行约为：

    ```text
               flash:     1092656 B         2 MB     52.10%
    ```

    镜像位于 `apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin`。

2. **接线**：天线接到 EVK 的 RF1（u.FL）。IPRO Debug Probe 的 UART 排线接到 EVK 的 J_UART，探针用 USB 接电脑。EVK 用 USB-C 供电，LED1 点亮。

3. **找出串口**：在 `<IntelProCube>` 目录执行（Linux 为 `./ipro_iot_tool_linux`，Windows 为 `ipro_iot_tool.exe`，下同）

    ```bash
    ./ipro_iot_tool_macos --list-ports
    ```

    探针会列出两个端口：标有 `(IPRO_U)`、名称以 `02` 结尾的是 UART，烧录和控制台都用它；`(IPRO_C)` 是芯片调试端口。macOS 列出的名称以 `/dev/tty.` 开头，请改用以 `/dev/cu.` 开头的同名端口，例如 `/dev/cu.usbmodemXXXX02`。

4. **烧录**：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro6 --chip-variant IPRO6S \
        --port /dev/cu.usbmodemXXXX02 --baudrate 2000000 \
        --pt chips/ipro6/partition/partition_cfg_fw_direct.toml \
        --firmware <SDK>/apps/platform/ipro6_demo/build_ipro6_lpwifi/build_out/ipro6_demo_IPRO6.bin
    ```

    工具通过探针让芯片进入下载模式，烧录并校验后复位芯片，约需 15 秒。输出最后出现 `[All Success]` 才算成功；工具即使失败也以 0 退出。`partition_cfg_fw_direct.toml` 把固件放在 Flash 地址 0x0、不使用 boot2，分区表放在最后两个扇区。

5. **确认启动**：以 115200 波特（8N1、无流控）打开同一个串口，再按一下 EVK 的 RESET（SW2）。

    ```bash
    screen /dev/cu.usbmodemXXXX02 115200
    ```

    V2.3.0 起，启动信息前段有一行 `Build:<时间>,<日期>`，是这次构建的时间，与 IPRO7 相同。启动信息的最后几行：

    ```text
    [OS] Starting OS Scheduler...
    [EVENT] Event loop initialized
    [EVENT] WiFi event handler registered
    Init Shell (RT-Thread FinSH based)
    ipro />
    ```

6. **确认 Wi-Fi**：输入 `stack_wifi`，出现 `CODE_WIFI_ON_MGMR_DONE` 后再输入 `wifi_scan`。

    ```text
    ipro />stack_wifi
    ...
    [APP] [EVT] CODE_WIFI_ON_INIT_DONE
    ...
    [APP] [EVT] CODE_WIFI_ON_MGMR_DONE
    ipro />wifi_scan
    [APP] [EVT] CODE_WIFI_ON_SCAN_DONE
    ...
    index[00]: channel 01, bssid XX:XX:XX:XX:XX:XX, rssi -20, ... auth WPA2-PSK, cipher: AES, SSID <ssid>
    ```

    附近每个接入点一行（最多 50 行，未使用的显示 `empty`）。能列出接入点，说明射频和 Wi-Fi 协议栈都正常。每次启动只需执行一次 `stack_wifi`。

7. **确认 soft-AP**：启动接入点，密钥为 8 到 63 个字符。

    ```text
    ipro />wifi_ap_start -s IPRO6S_AP -k <key> -c 6
    [WPA] AP-ENABLED
    [APP] [EVT] CODE_WIFI_ON_AP_STARTED
    ```

    用电脑或手机以该密钥连接 `IPRO6S_AP`，会从板子获得 192.168.169.0/24 的地址（板子为 192.168.169.1），控制台打印 `AP-STA-CONNECTED` 与该设备的 MAC 地址。`wifi_ap_stop` 停止接入点。

</div>

### 手动进入下载模式 { #ipro6s-download-mode }

工具通过探针的 DL 线自动进入下载模式。使用普通 USB 转 UART 线，或工具报告握手失败时，先手动进入下载模式再执行烧录命令：按住 BOOT（SW1），按一下 RESET（SW2），再松开 BOOT。芯片处于下载模式时控制台没有任何输出；烧录完成后按一下 RESET 恢复正常启动。烧录前请关闭占用该串口的终端程序（例如 `screen`），否则工具无法打开串口。

### 烧录成功却没有启动 { #ipro6s-no-boot }

IntelProCube 0.7.0 的 IPRO6 启动头时序不适用于封装内 2 MB Flash 的 IPRO6S：输出有 `[All Success]`，复位后控制台却没有任何信息，芯片停在下载模式。请改用 0.7.0.1 及以上并解压到新的文件夹。如果把 0.7.0.1 解压覆盖到用过的 0.7.0 文件夹上，请先删除 `chips/ipro6/img_create_iot/efuse_bootheader_cfg.ini`：这个文件在工具第一次运行时由模板生成，之后不会更新。IPRO SDK Online Setup 3.6.0 及以前安装的 IntelProCube 是 0.7.0，烧录 IPRO6S 时请另外安装 0.7.0.1。

## Reef 上的 FIN Wi-Fi 卡 { #dual-chip }

FIN 卡是把 IPRO6S 做在 SD 卡外形板卡上的 Wi-Fi 卡，插入 Reef 的 microSD 卡座，以 SDIO 从机方式工作，由卡座的 SD_VDD 供电。IPRO7AI 是主控 SoC，负责应用、AI、BLE、音频与 IP 协议栈；FIN 卡上的 IPRO6S 运行 `ipro6_if_wifi`（`defconfig_ipro6_sdio`），提供无线连接。

```mermaid
flowchart LR
    A["IPRO7AI（Reef）<br/>应用 + ipronet_host + lwIP"] -- "SDIO 4-bit（microSD 卡座）" --> B["IPRO6S FIN 卡<br/>ipro6_if_wifi"]
    B -- "Wi-Fi" --> C["无线接入点"]
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
