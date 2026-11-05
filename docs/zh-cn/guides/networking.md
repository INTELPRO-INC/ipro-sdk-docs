---
title: "网络"
description: IPRO7 FreeRTOS 应用的 lwIP 与 mbedTLS、IPRO7AI Reef EVK 经 SDIO 通过 IPRO6S FIN 卡连接 Wi-Fi，以及自有电路板上的 RMII 以太网
migrate_from:
  - "wifi-networking.html"
---

# 网络

FreeRTOS 应用以 lwIP 2.1.2 作为 TCP/IP 协议栈，由 mbedTLS 2.28.2 提供 TLS。IPRO7 联网有两种方式：以 IPRO6S 作为无线端、经 SDIO 连接的 Wi-Fi，或 IPRO7 的 Ethernet MAC（EMAC，RMII）外接 PHY。在 IPRO7AI Reef EVK 上，IPRO6S 就是插在 microSD 卡槽中的 FIN 卡。两种连接共用同一个 lwIP，socket 代码无需因接口不同而改写。

!!! abstract "要点"
    - 协议栈：lwIP 2.1.2（BSD socket）与 mbedTLS 2.28.2，用于 FreeRTOS 应用。
    - Reef：microSD 卡槽中的 IPRO6S FIN 卡，由 `components/network/ipronet_host` 经 SDIO 驱动，连接表现为 lwIP netif `iproeth0`。`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 可连接 AP 并通过 RTSP 推送摄像头视频流。
    - FIN 卡固件：`ipro6_if_wifi` 用 `defconfig_ipro6_sdio` 构建；运行中的卡可用 `ipro6s_ota` 经 Wi-Fi 更新。
    - 以太网：EMAC 通过 RMII 外接 PHY（附 RTL8201F 驱动）。Reef 板上没有以太网 PHY。
    - 未包含：高层 HTTP 客户端组件；`ipronet_host` 的 AP 模式与多个 netif。

## 网络架构 { #architecture }

<div class="ipro-stack">
  <div class="l-app"><strong>应用</strong><span>sockets / MQTT / RTSP / HTTP</span></div>
  <div class="l-host"><strong>TLS（mbedTLS 2.28.2）</strong><span>components/crypto/mbedtls</span></div>
  <div class="l-hci"><strong>TCP/IP（lwIP 2.1.2）</strong><span>components/network/lwip</span></div>
  <div class="l-ctlr"><strong>网络接口</strong><span>ipronet_host（SDIO）→ IPRO6S │ EMAC + RMII PHY</span></div>
</div>

| 组件 | 路径 | 说明 |
|---|---|---|
| lwIP | `components/network/lwip/` | TCP/IP 协议栈；`lwip_apps/ping` 提供 `ping` 命令 |
| SDIO Wi-Fi host | `components/network/ipronet_host/` | IPRO6S 连接的 IPRO7 端：SDIO 传输、netif `iproeth0`、Wi-Fi 事件、IPRO6S 固件更新（`ipronet_ota.h`） |
| RTSP 服务器 | `components/network/rtsp_server/` | MJPEG 摄像头视频流 |
| mbedTLS | `components/crypto/mbedtls/` | TLS 与加密；`port/` 为硬件加速与熵源 |
| EMAC 驱动 | `bsp/drivers/ipro7_soc/std_drv/src/drv_emac.c`、`bsp/hal/src/hal_emac.c` | Ethernet MAC，RMII 模式 |
| 以太网 netif | `bsp/hal/src/hal_ethernetif.c`、`bsp/hal/src/phy_rtl8201f.c` | lwIP 与 EMAC 的对接、PHY 驱动 |

## 网络配置 { #network-config }

构建时 `.config` 会原样转换为 `autoconf.h`，Kconfig 的 `select`／`depends on` 不会被应用，连接所需的配置都要写出来。

=== "Reef 上的 Wi-Fi（defconfig_wifi_ipro6s）"

    ```ini title="apps/platform/ipro7ai_reef_demo/defconfig_wifi_ipro6s（节选）"
    CONFIG_IPRO7AI_REEF=y
    CONFIG_USE_PSRAM=y
    CONFIG_IPRO7_WIFI_HOST_HOTCODE=y
    CONFIG_WIFI_USE_IPRO6S=y
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_IPRONET_HOST_ENABLE=y
    CONFIG_RTSP_SERVER=y
    CONFIG_RTSP_LISTEN_PORT=8554
    CONFIG_RTSP_DEFAULT_VIDEO_FPS=15
    CONFIG_RTSP_SHELL=y
    ```

=== "以太网（自有电路板）"

    ```ini title="apps/platform/ipro7_demo/.config（节选）"
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_MBEDTLS_ENABLE=y
    CONFIG_MBEDTLS_BIGNUM_USE_HW=y
    ```

| 配置 | 说明 |
|---|---|
| `CONFIG_COMPONENTS_LWIP_ENABLE` | 加入 lwIP |
| `CONFIG_ETHERNET` | lwIP 的以太网帧大小缓冲区（`CFG_ETHERNET_ENABLE`）；`ipronet_host` 也需要 |
| `CONFIG_COMPONENTS_IPRONET_HOST_ENABLE` | 加入 `ipronet_host`；需要 `CONFIG_USE_PSRAM=y` |
| `CONFIG_IPRO7_WIFI_HOST_HOTCODE` | `ipronet_host`、lwIP 与 FreeRTOS 的数据路径改为从 PSRAM 执行，不走 flash；需要 `CONFIG_USE_PSRAM=y`，不能与 `CONFIG_IPRO7_BLE_HOTCODE` 或低功耗内存布局同时使用 |
| `CONFIG_WIFI_USE_IPRO6S` | `ipro7ai_reef_demo` 专用：编入它的 Wi-Fi shell（`src/wifi_ipro6s.c`）与 `ipro6s_ota` 命令 |
| `CONFIG_RTSP_SERVER`、`CONFIG_RTSP_LISTEN_PORT`、`CONFIG_RTSP_DEFAULT_VIDEO_FPS`、`CONFIG_RTSP_SHELL` | RTSP 服务器、端口号、默认帧率；示例的 `rtsp_cam` 命令 |
| `CONFIG_PING` | `ping` 命令 |
| `CONFIG_DHCPD`、`CONFIG_MDNS` | DHCP 服务器、mDNS |
| `CONFIG_LWIP_MQTT` | lwIP 的 MQTT 客户端 |
| `CONFIG_LWIP_ALTCP` | lwIP altcp 与基于 mbedTLS 实现的 altcp TLS |
| `CONFIG_MQTT_VAR_HEADER_BUFFER_LEN` | MQTT 可变报头缓冲区大小 |
| `CONFIG_COMPONENTS_MBEDTLS_ENABLE` | 加入 mbedTLS |

应用可在自己的目录中放置 `lwipopts_app.h` 覆盖 lwIP 配置，`lwipopts.h` 找到它就会加载。使用 `ipronet_host` 时，请复制 `apps/platform/ipro7ai_reef_demo/lwipopts_app.h`（与 `ipro7_sdio_wifi` 中的是同一份）：它把 lwIP 缓冲区放到 PSRAM 中并加大 TCP 窗口。组件 README 指出，缺少它时 TCP 上行速率会降到约四分之一。

## lwIP 集成 { #lwip }

lwIP 提供 BSD 风格的 socket API（`lwip/sockets.h`、`lwip/netdb.h`）。DHCP 客户端、DNS、SNTP、IPv6、`lwiperf` 与 lwIP 的 HTTP 客户端都已编入；DHCP 服务器、mDNS、MQTT 与 altcp TLS 按上表的配置加入。

下面的 TCP 客户端与 `apps/platform/common/ipronet_ota_cli/ota_http_fetch.c` 的步骤相同（`ipro7ai_reef_demo` 为 `ipro6s_ota` 编入了这个文件）：解析主机名、创建 socket、建立连接。网络接口获取到地址后才使用 socket（使用 `ipronet_host` 时，就是在 `on_got_ip` 回调之后）。

```c title="TCP 客户端"
#include <string.h>
#include "lwip/sockets.h"
#include "lwip/netdb.h"

int tcp_send(const char *host, uint16_t port, const void *data, size_t len)
{
    struct hostent *hp = gethostbyname(host);
    if (hp == NULL) {
        return -1;
    }

    struct sockaddr_in sa;
    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons(port);
    memcpy(&sa.sin_addr, hp->h_addr, hp->h_length);

    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0) {
        return -1;
    }
    if (connect(s, (struct sockaddr *)&sa, sizeof(sa)) < 0 ||
        send(s, data, len, 0) < 0) {
        close(s);
        return -1;
    }
    close(s);
    return 0;
}
```

## 以太网 { #emac }

IPRO7 的 EMAC 通过 RMII（10/100 Mbps）外接 PHY，HAL 附带 RTL8201F PHY 驱动。Reef 板上没有 PHY，这条路径用于自行设计的电路板。lwIP 对接位于 `bsp/hal/src/hal_ethernetif.c`：连接建立后由它的 DHCP 任务获取地址，DHCP 超时则改用该文件中定义的静态地址。EMAC 引脚见 `bsp/hal/src/hal_emac.c` 与[引脚与外设对照](../hardware/pinmux.md)。

添加 netif、启动 lwIP 的方式与 `apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c` 相同：

```c title="apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c（节选）"
static struct netif emac_netif;

static void regist_netif(void *arg)
{
    struct netif *netif = (struct netif *)arg;
    ip4_addr_t ipaddr, netmask, gw;

    ip_addr_set_zero(&ipaddr);
    ip_addr_set_zero(&netmask);
    ip_addr_set_zero(&gw);
    netif_add(netif, &ipaddr, &netmask, &gw, NULL, ethernetif_init, tcpip_input);
    netif_set_default(netif);
    ethernet_link_status_updated(netif);
#if LWIP_NETIF_LINK_CALLBACK
    netif_set_link_callback(netif, ethernet_link_status_updated);
#endif
}

int cmd_emac_lwip(int argc, char **argv)
{
    tcpip_init(regist_netif, (void *)&emac_netif);
    return 0;
}
```

`ipro7_demo` 面向 IPRO7 EVB，且只有在 `CONFIG_DEMO_EMAC=y` 时才编入 `emac_demo.c`；随附的 `.config` 中没有这一行。

## TLS／DTLS（mbedTLS） { #mbedtls }

用 `CONFIG_COMPONENTS_MBEDTLS_ENABLE=y` 加入 mbedTLS 2.28.2。默认配置以 mbedTLS 自带的 `config.h` 为基础，包含 TLS 1.2 客户端与 X.509。应用如果提供自己的 `mbedtls_app_config.h`，会替换整份默认配置（mbedTLS 组件必须能在 include 路径中找到它）。熵源是硬件随机数发生器（`port/entropy_poll_alt.c`）。

| 硬件加速配置 | 覆盖范围 |
|---|---|
| `CONFIG_MBEDTLS_BIGNUM_USE_HW` | 大数模幂运算 |
| `CONFIG_MBEDTLS_AES_USE_HW`、`CONFIG_MBEDTLS_GCM_USE_HW` | AES、GCM |
| `CONFIG_MBEDTLS_SHA1_USE_HW`、`CONFIG_MBEDTLS_SHA256_USE_HW`、`CONFIG_MBEDTLS_SHA512_USE_HW` | SHA |
| `CONFIG_MBEDTLS_ECDSA_USE_HW`、`CONFIG_MBEDTLS_ECDH_USE_HW` | ECDSA、ECDH |

在 IPRO7 上，`CONFIG_MBEDTLS_ECC_USE_HW` 会回退到软件实现，构建时会打印警告。

TLS 客户端可以从 `components/crypto/mbedtls/mbedtls/programs/ssl/ssl_client1.c` 开始。移植时：

- 检查每个初始化与连接调用的返回值。
- 用 `mbedtls_ssl_conf_ca_chain()` 加载服务所信任的 CA 证书，使用 `MBEDTLS_SSL_VERIFY_REQUIRED`，并用 `mbedtls_ssl_set_hostname()` 设置主机名。校验证书有效期需要正确的系统时间。
- 处理 `MBEDTLS_ERR_SSL_WANT_READ`／`MBEDTLS_ERR_SSL_WANT_WRITE`、部分传输与超时，并在每条错误路径上释放 TLS context 与 socket。
- 把示例中的测试证书与主机换成产品自己的。

## HTTP、MQTT 与 RTSP { #http-client }

| 协议 | 可用的实现 |
|---|---|
| HTTP | 没有 SDK 的 HTTP 客户端组件。可用 lwIP 的 HTTP 客户端（`lwip/apps/http_client.h`）、`components/3rdparty/llhttp`（解析器），或参考 `ota_http_fetch.c` 中的 HTTP/1.0 GET |
| MQTT | lwIP 的 MQTT 客户端（`lwip/apps/mqtt.h`）：设置 `CONFIG_LWIP_MQTT=y`，或像 `ipro_agora_sentino` 那样在应用的 `CMakeLists.txt` 中编入 `mqtt.c` |
| RTSP | `components/network/rtsp_server`，默认端口 8554；Reef 示例的 `rtsp_cam` 命令用它推送摄像头视频流 |

HTTPS 与 MQTT over TLS 需要自行用 mbedTLS（或 altcp TLS）建立安全连接，并处理状态码、分块传输、长度限制与超时。

## 通过 IPRO6S 连接 Wi-Fi { #wifi-ipro6 }

```mermaid
flowchart LR
  A["IPRO7<br/>应用＋ipronet_host＋lwIP"] -->|"SDIO 4-bit<br/>GPIO28–33"| B["IPRO6S<br/>ipro6_if_wifi"]
  B -->|Wi-Fi| C["无线接入点"]
```

IPRO7 是 SDIO host。IPRO6S 运行 `ipro6_if_wifi`，在以太网数据包与 Wi-Fi 之间桥接；DHCP 在 IPRO6S 上运行，IP 协议栈与应用的 socket 在 IPRO7 上。SDIO 总线固定在 GPIO28–33，由组件配置引脚。在 Reef 上这就是 microSD 卡槽的信号线，FIN 卡插在原本放 SD 卡的位置。

| 项目 | Reef 上的做法 |
|---|---|
| 无线端 | 插在 microSD 卡槽中的 IPRO6S FIN 卡，由卡槽电源供电 |
| 卡电源 | GPIO14（`BOARD_SD_PWR_EN_PIN`，低电平打开）。JP3 设在 **GPIO** 时，固件可以给卡重新上电（`fin cycle`、`ipronet_start()`）；JP3 设在 ON 时卡始终有电 |
| FIN 卡固件 | `make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio` → `build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。IPRO6S 镜像用 IntelProCube `--chipname ipro6` 烧录 |
| 固件更新 | 在 Reef 控制台输入 `ipro6s_ota <http url>`，下载 IPRO6S OTA 包（`FW_OTA.bin.xz.ota`）并安装到卡上，见 [OTA 更新](ota.md) |

`ipronet_host.h` 摘要：

| 调用 | 作用 |
|---|---|
| `ipronet_config_default(&cfg)` | 用组件默认值填充 `ipronet_config_t`；再根据开发板设置 `pwr_en_gpio`、`pwr_active_low` 与 `bus_hz` |
| `ipronet_start(&cfg, &cb)` | 给 IPRO6S 上电并枚举、启动 RX 任务、启用 `iproeth0`。同步调用；任何一步失败都会回到空闲状态，卡启动期间以重试等待 |
| `ipronet_connect(ssid, psk)` | 连接 AP；之后依次触发 `on_connected`、`on_got_ip` |
| `ipronet_scan()`、`ipronet_disconnect()`、`ipronet_stop()` | 扫描（结果在 `on_scan_result` 中）、断开 AP、按相反顺序关闭 `ipronet_start()` |
| `ipronet_is_connected()`、`ipronet_has_ip()`、`ipronet_get_ip()`、`ipronet_get_mac()` | 状态查询，任何任务都可调用 |

- 回调（`on_connected`、`on_disconnected`、`on_got_ip`、`on_scan_result`）在组件的 RX 任务中执行：不可阻塞，也不可调用 `ipronet_connect`／`disconnect`／`scan`／`stop`。需要执行操作时交给自己的任务。
- `auto_reconnect = 1`（默认）时，断开后由组件重新连接 AP；设为 0 时由应用在 `on_disconnected` 中再调用 `ipronet_connect()`。
- 所有返回码列在 `ipronet_host.h`（`IPRONET_OK` 为 0）与 `components/network/ipronet_host/README.md` 中。

## 在 Reef 上动手实践 { #hands-on }

用出厂固件的 shell 命令让 Reef 连接 Wi-Fi，并通过 RTSP 推送摄像头视频流。配合电脑端播放器的完整步骤见 [Wi-Fi 与 RTSP 教程](../tutorials/wifi-rtsp.md)。

需要：运行 `ipro6_if_wifi`（`defconfig_ipro6_sdio`）的 IPRO6S FIN 卡、接在摄像头连接器上的 OV5640 或 OV2640 摄像头模组，以及一台 Wi-Fi 无线接入点。

<div class="ipro-steps" markdown>

1. **准备开发板**

    拔掉 USB-C，把 FIN 卡插入 microSD 卡槽，JP3 设在 **GPIO**，SW7 设在 **CAM**。

2. **配置**

    Wi-Fi 版是 `ipro7ai_reef_demo` 的另一份配置文件，它增加的配置列在[网络配置](#network-config)中。自己的应用要联网时，复制这些配置、`lwipopts_app.h`，以及示例 `CMakeLists.txt` 中 `CONFIG_WIFI_USE_IPRO6S` 的代码块。

3. **代码**

    `ipronet_up <ssid> <psk>` 就是应用联网所需的完整流程：开发板的电源配置、`ipronet_start()`，再 `ipronet_connect()`。

    ```c title="apps/platform/ipro7ai_reef_demo/src/wifi_ipro6s.c（节选）"
    /* ipronet_config_default() with the fin's rail: SD_VDD's switch. */
    static void app_config(ipronet_config_t *cfg)
    {
        ipronet_config_default(cfg);
        cfg->pwr_en_gpio    = BOARD_SD_PWR_EN_PIN;
        cfg->pwr_active_low = (BOARD_SD_PWR_ON_LEVEL == 0);
        cfg->bus_hz         = 50000000U;   /* SD high speed on the fin slot */
        cfg->tx_pace_kbps   = 0;           /* no egress pacer */
    }

    static void app_on_got_ip(void *arg, const ipronet_ip_info_t *ip)
    {
        (void)arg;
        printf("[ctrl] IP %u.%u.%u.%u / %u.%u.%u.%u gw %u.%u.%u.%u\r\n",
               ip->ip4[0], ip->ip4[1], ip->ip4[2], ip->ip4[3],
               ip->mask4[0], ip->mask4[1], ip->mask4[2], ip->mask4[3],
               ip->gw4[0], ip->gw4[1], ip->gw4[2], ip->gw4[3]);
    }

    static int cmd_ipronet_up(int argc, char **argv)
    {
        ipronet_config_t cfg;
        app_config(&cfg);                        /* board rail, 50 MHz, reconnect on, no pacer */
        int rc = ipronet_start(&cfg, &s_app_cb);
        printf("ipronet_start -> %d\r\n", rc);
        if (rc != IPRONET_OK) return rc;
        if (argc >= 3) {
            rc = ipronet_connect(argv[1], argv[2]);
            printf("ipronet_connect '%s' -> %d\r\n", argv[1], rc);
        }
        return rc;
    }
    ```

    `s_app_cb` 是在同一文件中定义、包含四个回调的 `ipronet_callbacks_t`。自己的应用请在 `on_got_ip` 之后再打开 socket。

4. **构建**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    镜像为 `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin`。

5. **烧录**

    让 Reef 进入下载模式（按住 SW1、按一下 SW2、松开 SW1），再在 IntelProCube 目录执行：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    确认输出中有 `[All Success]` 后按 SW2。详见[烧录与串口](../get-started/flash-and-monitor.md)。

6. **连接并推流**

    以 115200 baud 打开控制台，输入：

    ```text
    ipronet_up <ssid> <psk>
    rtsp_cam on
    ```

    成功时，两个调用都返回 0，接着出现连接与地址信息，最后是视频流地址：

    ```text
    ipronet_start -> 0
    ipronet_connect '<ssid>' -> 0
    [ctrl] STA CONNECTED
    [ctrl] IP 192.168.1.23 / 255.255.255.0 gw 192.168.1.1
    rtsp_cam: on, <sensor> <width>x<height> JPEG q<quality>, 15 fps
    rtsp_cam: rtsp://192.168.1.23:8554/av0_0
    ```

    以 `[ctrl]` 开头的行由组件的 RX 任务打印，在控制台上可能会错乱；`ipro6s_link_status` 会再报告一次状态（`host connected=1 ip=1`）。在同一网络中的 RTSP 播放器里打开这个地址。`rtsp_cam stats` 显示帧计数，`rtsp_cam off` 停止推流。

</div>

| 命令（`defconfig_wifi_ipro6s`） | 说明 |
|---|---|
| `ipronet_up [<ssid> <psk>]`、`ipronet_down` | `ipronet_start()`，并可接着 `ipronet_connect()`；`ipronet_stop()` |
| `ipro6s_scan`、`ipro6s_scan_last` | 扫描 AP；列出上次结果 |
| `ipro6s_connect <ssid> <psk>`、`ipro6s_disconnect`、`ipro6s_link_status` | 连接、断开、连接状态 |
| `rtsp_cam on [fps]`、`rtsp_cam off`、`rtsp_cam stats` | `rtsp://<ip>:8554/av0_0` 的 RTSP 摄像头视频流 |
| `ipro6s_ota <http url>` | 经 HTTP 更新 FIN 卡固件 |
| `fin`、`fin cycle` | 卡槽状态；给卡重新上电（JP3 设在 GPIO） |

下一步：以这份配置为起点，按照[创建第一个自己的应用](../tutorials/first-own-app.md)动手实践，再按照[测试你的应用](../tutorials/testing.md)验证。

## 其他 Wi-Fi 模组 { #wifi-atbm6162 }

Reef 只通过 IPRO6S FIN 卡连接 Wi-Fi。SDK 包中其他 SDIO Wi-Fi 模组的驱动与探测程序面向 IPRO7 EVB，不是 Reef 支持的路径，见[示例](../examples/index.md)。

## IPRO6S 作为 Wi-Fi 设备端 { #ipro6s-wifi6 }

连接的 IPRO6S 端是同一套 SDK 中的 IPRO6S FreeRTOS 应用，输出文件名以 `_IPRO6.bin` 结尾。它的预编译 Wi-Fi 库只针对随附的配置文件提供，请保留其中一份的 Wi-Fi 配置与 `CONFIG_WIRELESS_LIB_VARIANT`。

| 应用 | 配置文件 | 角色 |
|---|---|---|
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | 连接 SDIO host 的 Wi-Fi 6 桥接：FIN 卡固件 |
| `ipro6_if_wifi` | `defconfig_ipro6_usb` | 同样的桥接，连接 USB host |
| `ipro6_demo` | `.config`、`defconfig_ipro6_lpwifi` | IPRO6S EVB 上独立运行的 Wi-Fi 6 station／soft-AP |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | 供 Linux cfg80211 主机使用的 FullMAC 固件；Linux 驱动不在本 SDK 包中 |

芯片、开发板与烧录见 [IPRO6S](../hardware/chips/ipro6s.md)。

## 本版本的限制 { #limitations }

- 只有 FreeRTOS 应用能联网。Zephyr 下没有以太网驱动，也没有 `ipronet_host`；`zephyr/drivers/wifi` 是 IPRO6S 芯片本身的驱动，而本版本的 Zephyr 不支持 IPRO6S。见 [Zephyr RTOS](zephyr.md)。
- `ipronet_host` 只支持 station 模式与单个 netif，也不会检测传输中断：卡断电后用 `ipronet_stop()`、`ipronet_start()` 重新建立。
- 没有高层 HTTP 客户端组件，也没有 4G／LTE 移动网络模组的组件。
- `ipro7_sdio_wifi` 的 README 提到 `iperf`，但它依赖的组件不在 SDK 包中。
- `ipro_agora_sentino` 的 MQTT 使用明文 TCP 连接；量产产品请改用 MQTT over TLS 并校验证书。

## 参考应用 { #reference-apps }

| 应用 | 配置文件 | 内容 |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` | `defconfig_wifi_ipro6s` | FIN 卡 Wi-Fi、RTSP 摄像头视频流、`ipro6s_ota` |
| `apps/multimedia/ipro_agora_sentino` | `.config` | BLE 配网、FIN 卡 Wi-Fi、MQTT、Agora RTC 语音；需要 AOSL 内核与 Sentino 设备三元组（见该应用的 README） |
| `apps/platform/ipro6_if_wifi` | `defconfig_ipro6_sdio` | FIN 卡固件（IPRO6S） |

其他开发板：`ipro7_sdio_wifi` 是独立的 `ipronet_host` 参考应用，每个启动阶段都有对应的 shell 命令；`ipro7_demo` 含 EMAC 演示。两者都面向 IPRO7 EVB。

- [Wi-Fi 与 RTSP 教程](../tutorials/wifi-rtsp.md)：配合电脑端播放器的 Reef 完整步骤。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：microSD 卡槽、JP3 与 FIN 卡。
- [OTA 更新](ota.md)：用 `ipro6s_ota` 更新 FIN 卡。
- [Thread 与 Matter](thread-matter.md)：Zephyr 下的 IEEE 802.15.4 与 OpenThread。
