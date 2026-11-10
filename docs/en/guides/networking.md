---
title: "Networking"
description: lwIP and mbedTLS in IPRO7 FreeRTOS applications, Wi-Fi on the IPRO7AI Reef EVK through the IPRO6S FIN card over SDIO, and RMII Ethernet on your own board
migrate_from:
  - "wifi-networking.html"
---

# Networking

FreeRTOS applications use lwIP 2.1.2 as the TCP/IP stack and mbedTLS 2.28.2 for TLS. IPRO7 reaches a network in one of two ways: Wi-Fi through an IPRO6S that acts as the radio and attaches over SDIO, or the IPRO7 Ethernet MAC (EMAC, RMII) with an external PHY. On the IPRO7AI Reef EVK the IPRO6S is the FIN card in the microSD socket. Both links feed the same lwIP stack, so socket code does not change with the interface.

!!! abstract "At a glance"
    - Stack: lwIP 2.1.2 (BSD sockets) and mbedTLS 2.28.2, in FreeRTOS applications.
    - Reef: the IPRO6S FIN card in the microSD socket, driven over SDIO by `components/network/ipronet_host`; the link appears as the lwIP netif `iproeth0`. `ipro7ai_reef_demo` with `defconfig_wifi_ipro6s` connects and streams the camera over RTSP.
    - FIN card firmware: `ipro6_if_wifi` built with `defconfig_ipro6_sdio`; a running card is updated over Wi-Fi with `ipro6s_ota`.
    - Ethernet: EMAC in RMII mode with an external PHY (RTL8201F driver included). The Reef has no Ethernet PHY.
    - Not included: a high-level HTTP client component; access-point mode and more than one netif in `ipronet_host`.

## Architecture { #architecture }

<div class="ipro-stack">
  <div class="l-app"><strong>Application</strong><span>sockets / MQTT / RTSP / HTTP</span></div>
  <div class="l-host"><strong>TLS (mbedTLS 2.28.2)</strong><span>components/crypto/mbedtls</span></div>
  <div class="l-hci"><strong>TCP/IP (lwIP 2.1.2)</strong><span>components/network/lwip</span></div>
  <div class="l-ctlr"><strong>Network interface</strong><span>ipronet_host (SDIO) → IPRO6S │ EMAC + RMII PHY</span></div>
</div>

| Component | Path | Notes |
|---|---|---|
| lwIP | `components/network/lwip/` | TCP/IP stack; `lwip_apps/ping` provides the `ping` command |
| SDIO Wi-Fi host | `components/network/ipronet_host/` | IPRO7 side of the IPRO6S link: SDIO transport, netif `iproeth0`, Wi-Fi events, IPRO6S firmware update (`ipronet_ota.h`) |
| RTSP server | `components/network/rtsp_server/` | MJPEG camera streaming |
| mbedTLS | `components/crypto/mbedtls/` | TLS and crypto; `port/` holds hardware acceleration and the entropy source |
| EMAC driver | `bsp/drivers/ipro7_soc/std_drv/src/drv_emac.c`, `bsp/hal/src/hal_emac.c` | Ethernet MAC in RMII mode |
| Ethernet netif | `bsp/hal/src/hal_ethernetif.c`, `bsp/hal/src/phy_rtl8201f.c` | lwIP-to-EMAC glue and the PHY driver |

## Network configuration { #network-config }

The build copies `.config` into `autoconf.h` as written; Kconfig `select` and `depends on` are not applied, so write out every key the link needs.

=== "Wi-Fi on the Reef (defconfig_wifi_ipro6s)"

    ```ini title="apps/platform/ipro7ai_reef_demo/defconfig_wifi_ipro6s (excerpt)"
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

=== "Ethernet (your own board)"

    ```ini title="apps/platform/ipro7_demo/.config (excerpt)"
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_MBEDTLS_ENABLE=y
    CONFIG_MBEDTLS_BIGNUM_USE_HW=y
    ```

| Key | Notes |
|---|---|
| `CONFIG_COMPONENTS_LWIP_ENABLE` | Adds lwIP |
| `CONFIG_ETHERNET` | lwIP's Ethernet-sized buffers (`CFG_ETHERNET_ENABLE`); `ipronet_host` needs it too |
| `CONFIG_COMPONENTS_IPRONET_HOST_ENABLE` | Adds `ipronet_host`; needs `CONFIG_USE_PSRAM=y` |
| `CONFIG_IPRO7_WIFI_HOST_HOTCODE` | Runs the `ipronet_host`, lwIP and FreeRTOS data path from PSRAM instead of flash; needs `CONFIG_USE_PSRAM=y`, cannot be combined with `CONFIG_IPRO7_BLE_HOTCODE` or the low-power layouts |
| `CONFIG_WIFI_USE_IPRO6S` | `ipro7ai_reef_demo` only: compiles its Wi-Fi shell (`src/wifi_ipro6s.c`) and the `ipro6s_ota` command |
| `CONFIG_RTSP_SERVER`, `CONFIG_RTSP_LISTEN_PORT`, `CONFIG_RTSP_DEFAULT_VIDEO_FPS`, `CONFIG_RTSP_SHELL` | RTSP server, its port, its default frame rate; the demo's `rtsp_cam` command |
| `CONFIG_PING` | `ping` command |
| `CONFIG_DHCPD`, `CONFIG_MDNS` | DHCP server, mDNS responder |
| `CONFIG_LWIP_MQTT` | lwIP's MQTT client |
| `CONFIG_LWIP_ALTCP` | lwIP altcp and altcp TLS on mbedTLS |
| `CONFIG_MQTT_VAR_HEADER_BUFFER_LEN` | MQTT variable-header buffer size |
| `CONFIG_COMPONENTS_MBEDTLS_ENABLE` | Adds mbedTLS |

An application can override lwIP settings with its own `lwipopts_app.h`, which `lwipopts.h` includes when it exists. With `ipronet_host`, copy `apps/platform/ipro7ai_reef_demo/lwipopts_app.h` (the same file as in `ipro7_sdio_wifi`): it moves the lwIP buffers into PSRAM and enlarges the TCP window. The component README notes that TCP upload throughput drops to about a quarter without it.

## lwIP { #lwip }

lwIP provides a BSD-style socket API (`lwip/sockets.h`, `lwip/netdb.h`). The DHCP client, DNS, SNTP, IPv6, `lwiperf` and lwIP's HTTP client are built in; the DHCP server, mDNS, MQTT and altcp TLS are added with the keys above.

This TCP client follows the steps of `apps/platform/common/ipronet_ota_cli/ota_http_fetch.c`, which `ipro7ai_reef_demo` compiles for `ipro6s_ota`: resolve the host name, open a socket, connect. Use sockets only after the interface has an address (with `ipronet_host`, after the `on_got_ip` callback).

```c title="TCP client"
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

## Ethernet { #emac }

The IPRO7 EMAC connects to an external PHY over RMII (10/100 Mbps); the HAL includes an RTL8201F PHY driver. The Reef carries no PHY, so this path is for your own board. The lwIP glue is `bsp/hal/src/hal_ethernetif.c`: once the link is up its DHCP task requests an address, and falls back to the static address defined in that file when DHCP times out. For the EMAC pins see `bsp/hal/src/hal_emac.c` and [Pinout & Peripheral Mapping](../hardware/pinmux.md).

The netif is added and lwIP started the same way as in `apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c`:

```c title="apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c (excerpt)"
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

`ipro7_demo` targets the IPRO7 EVB and compiles `emac_demo.c` only with `CONFIG_DEMO_EMAC=y`, which its shipped `.config` does not set.

## TLS / DTLS (mbedTLS) { #mbedtls }

mbedTLS 2.28.2 is added with `CONFIG_COMPONENTS_MBEDTLS_ENABLE=y`. The default configuration builds on mbedTLS's own `config.h`, including the TLS 1.2 client and X.509. An application that provides its own `mbedtls_app_config.h` replaces the whole default configuration (the mbedTLS component must find it on its include path). Entropy comes from the hardware random number generator (`port/entropy_poll_alt.c`).

| Hardware acceleration key | Covers |
|---|---|
| `CONFIG_MBEDTLS_BIGNUM_USE_HW` | Big-number modular exponentiation |
| `CONFIG_MBEDTLS_AES_USE_HW`, `CONFIG_MBEDTLS_GCM_USE_HW` | AES, GCM |
| `CONFIG_MBEDTLS_SHA1_USE_HW`, `CONFIG_MBEDTLS_SHA256_USE_HW`, `CONFIG_MBEDTLS_SHA512_USE_HW` | SHA |
| `CONFIG_MBEDTLS_ECDSA_USE_HW`, `CONFIG_MBEDTLS_ECDH_USE_HW` | ECDSA, ECDH |

On IPRO7, `CONFIG_MBEDTLS_ECC_USE_HW` falls back to the software implementation; the build prints a warning.

For a TLS client, start from `components/crypto/mbedtls/mbedtls/programs/ssl/ssl_client1.c`. When porting it:

- Check the return value of every initialization and connection call.
- Load the CA certificates your service trusts with `mbedtls_ssl_conf_ca_chain()`, use `MBEDTLS_SSL_VERIFY_REQUIRED`, and set the host name with `mbedtls_ssl_set_hostname()`. The platform clock must be right for certificate validity checks.
- Handle `MBEDTLS_ERR_SSL_WANT_READ` / `MBEDTLS_ERR_SSL_WANT_WRITE`, partial transfers and timeouts, and free the TLS context and the socket on every error path.
- Replace the example's test certificates and host with your product's.

## HTTP, MQTT and RTSP { #http-client }

| Protocol | What is available |
|---|---|
| HTTP | No SDK HTTP client component. Use lwIP's HTTP client (`lwip/apps/http_client.h`), `components/3rdparty/llhttp` (parser), or the HTTP/1.0 GET in `ota_http_fetch.c` as a reference |
| MQTT | lwIP's MQTT client (`lwip/apps/mqtt.h`): set `CONFIG_LWIP_MQTT=y`, or compile `mqtt.c` in the application's `CMakeLists.txt` as `ipro_agora_sentino` does |
| RTSP | `components/network/rtsp_server`, default port 8554; the Reef demo's `rtsp_cam` command serves the camera with it |

For HTTPS or MQTT over TLS, build the secure connection with mbedTLS (or altcp TLS) yourself, and handle status codes, chunked transfer, length limits and timeouts.

## Wi-Fi through an IPRO6S { #wifi-ipro6 }

```mermaid
flowchart LR
  A["IPRO7<br/>application + ipronet_host + lwIP"] -->|"SDIO 4-bit<br/>GPIO28–33"| B["IPRO6S<br/>ipro6_if_wifi"]
  B -->|Wi-Fi| C["Access point"]
```

IPRO7 is the SDIO host. The IPRO6S runs `ipro6_if_wifi` and bridges Ethernet frames to Wi-Fi; DHCP runs on the IPRO6S, and the IP stack and your sockets run on IPRO7. The SDIO bus is fixed to GPIO28–33 and the component sets up the pins. On the Reef these are the microSD socket's lines, so the FIN card takes the place of an SD card.

| Item | On the Reef |
|---|---|
| Radio | IPRO6S FIN card in the microSD socket, powered from the socket supply |
| Card power | GPIO14 (`BOARD_SD_PWR_EN_PIN`, low = on). With JP3 on **GPIO** the firmware can power-cycle the card (`fin cycle`, `ipronet_start()`); with JP3 on ON the card is always powered |
| FIN card firmware | `make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio` → `build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`. IPRO6S images are written with IntelProCube `--chipname ipro6` |
| Firmware update | `ipro6s_ota <http url>` at the Reef console fetches the IPRO6S OTA package (`FW_OTA.bin.xz.ota`) and installs it on the card; see [OTA Updates](ota.md) |

`ipronet_host.h` in brief:

| Call | Does |
|---|---|
| `ipronet_config_default(&cfg)` | Fills `ipronet_config_t` with the component defaults; set `pwr_en_gpio`, `pwr_active_low` and `bus_hz` for your board |
| `ipronet_start(&cfg, &cb)` | Powers up and enumerates the IPRO6S, starts the RX task and brings `iproeth0` up. Synchronous; returns to idle on any failure, so retry while the card boots |
| `ipronet_connect(ssid, psk)` | Joins an access point; `on_connected` and then `on_got_ip` follow |
| `ipronet_scan()`, `ipronet_disconnect()`, `ipronet_stop()` | Scan (results in `on_scan_result`), leave the AP, undo `ipronet_start()` |
| `ipronet_is_connected()`, `ipronet_has_ip()`, `ipronet_get_ip()`, `ipronet_get_mac()` | State getters, safe from any task |

- The callbacks (`on_connected`, `on_disconnected`, `on_got_ip`, `on_scan_result`) run in the component's RX task. They must not block and must not call `ipronet_connect` / `disconnect` / `scan` / `stop`; hand the work to your own task.
- With `auto_reconnect = 1` (the default) the component rejoins the AP after a disconnect; with 0 your application calls `ipronet_connect()` again from `on_disconnected`.
- All return codes are listed in `ipronet_host.h` (`IPRONET_OK` is 0) and in `components/network/ipronet_host/README.md`.

## Hands-on on the Reef { #hands-on }

Join a Wi-Fi network from the Reef and stream the camera over RTSP, using the shell commands of the out-of-box firmware. The tutorial version, with a video player on the host, is the [Wi-Fi and RTSP tutorial](../tutorials/wifi-rtsp.md).

You need the IPRO6S FIN card running `ipro6_if_wifi` (`defconfig_ipro6_sdio`), an OV5640 or OV2640 camera module on the camera connector, and a Wi-Fi access point.

<div class="ipro-steps" markdown>

1. **Set up the board**

    With USB-C unplugged, insert the FIN card into the microSD socket, set JP3 to **GPIO** and SW7 to **CAM**.

2. **Configuration**

    The Wi-Fi build is a separate configuration file of `ipro7ai_reef_demo`; the keys it adds are listed under [Network configuration](#network-config). For your own application, copy those lines, `lwipopts_app.h`, and the `CONFIG_WIFI_USE_IPRO6S` block of the demo's `CMakeLists.txt`.

3. **Code**

    `ipronet_up <ssid> <psk>` is the whole connection sequence an application needs: the board's power settings, `ipronet_start()`, then `ipronet_connect()`.

    ```c title="apps/platform/ipro7ai_reef_demo/src/wifi_ipro6s.c (excerpt)"
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

    `s_app_cb` is the `ipronet_callbacks_t` with the four callbacks, defined in the same file. In your own application, open sockets only after `on_got_ip` has run.

4. **Build**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    The image is `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin`.

5. **Flash**

    Put the Reef in download mode (hold SW1, tap SW2, release SW1), then from the IntelProCube directory:

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    Look for `[All Success]`, then press SW2. Details are in [Flashing & Serial Console](../get-started/flash-and-monitor.md).

6. **Connect and stream**

    Open the console at 115200 baud and type:

    ```text
    ipronet_up <ssid> <psk>
    rtsp_cam on
    ```

    When it works, the console shows the return code 0 for both calls, the association and the address, then the stream URL:

    ```text
    ipronet_start -> 0
    ipronet_connect '<ssid>' -> 0
    [ctrl] STA CONNECTED
    [ctrl] IP 192.168.1.23 / 255.255.255.0 gw 192.168.1.1
    rtsp_cam: on, <sensor> <width>x<height> JPEG q<quality>, 15 fps
    rtsp_cam: rtsp://192.168.1.23:8554/av0_0
    ```

    The `[ctrl]` lines are printed from the component's RX task and can come out garbled on the console; `ipro6s_link_status` reports the state again (`host connected=1 ip=1`). Open the URL in an RTSP player on the same network. `rtsp_cam stats` shows the frame counters; `rtsp_cam off` stops the stream.

</div>

| Command (`defconfig_wifi_ipro6s`) | Purpose |
|---|---|
| `ipronet_up [<ssid> <psk>]`, `ipronet_down` | `ipronet_start()` and optionally `ipronet_connect()`; `ipronet_stop()` |
| `ipro6s_scan`, `ipro6s_scan_last` | Scan for access points; print the last result |
| `ipro6s_connect <ssid> <psk>`, `ipro6s_disconnect`, `ipro6s_link_status` | Connect, disconnect, link status |
| `rtsp_cam on [fps]`, `rtsp_cam off`, `rtsp_cam stats` | RTSP camera stream at `rtsp://<ip>:8554/av0_0` |
| `ipro6s_ota <http url>` | Update the FIN card's firmware over HTTP |
| `fin`, `fin cycle` | Socket status; power-cycle the card (JP3 on GPIO) |

Next: build your own application from this configuration with [Create Your First Application](../tutorials/first-own-app.md), and check it with [Test Your Application](../tutorials/testing.md).

## Other Wi-Fi modules { #wifi-atbm6162 }

The Reef connects to Wi-Fi only through the IPRO6S FIN card. Driver and probe code for other SDIO Wi-Fi modules in the package targets the IPRO7 EVB and is not a supported Reef path; see [Examples](../examples/index.md).

## IPRO6S as the Wi-Fi device { #ipro6s-wifi6 }

The IPRO6S side of the link is an IPRO6S FreeRTOS application from the same SDK. Its outputs end in `_IPRO6.bin`, and its prebuilt Wi-Fi libraries exist only for the shipped configurations, so keep the Wi-Fi options and `CONFIG_WIRELESS_LIB_VARIANT` of one of them.

| Application | Configuration | Role |
|---|---|---|
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | Wi-Fi 6 bridge to an SDIO host: the FIN card firmware |
| `ipro6_if_wifi` | `defconfig_ipro6_usb` | The same bridge to a USB host |
| `ipro6_demo` | `.config`, `defconfig_ipro6_lpwifi` | Stand-alone Wi-Fi 6 station / soft-AP on the IPRO6S EVK |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | FullMAC firmware for a Linux cfg80211 host; the Linux driver is not part of this package |

The chip, its board and flashing are covered on [IPRO6S](../hardware/chips/ipro6s.md).

## Limitations in this release { #limitations }

- Networking is available to FreeRTOS applications only. Under Zephyr there is no Ethernet driver and no `ipronet_host`; the Zephyr Wi-Fi driver in `zephyr/drivers/wifi` is the IPRO6S on-chip driver, and IPRO6S is not supported under Zephyr in this release. See [Zephyr RTOS](zephyr.md).
- `ipronet_host` supports station mode and a single netif, and does not detect a dead transport: after the card loses power, recover with `ipronet_stop()` and `ipronet_start()`.
- No high-level HTTP client component and no cellular modem component.
- The `ipro7_sdio_wifi` README mentions `iperf`; the component it relies on is not in the package.
- `ipro_agora_sentino` connects to MQTT over plain TCP; for products, use MQTT over TLS with certificate verification.

## Reference applications { #reference-apps }

| Application | Configuration | What it does |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` | `defconfig_wifi_ipro6s` | FIN card Wi-Fi, RTSP camera stream, `ipro6s_ota` |
| `apps/multimedia/ipro_agora_sentino` | `.config` | BLE provisioning, FIN card Wi-Fi, MQTT, Agora RTC voice; needs the AOSL core and a Sentino device triple (see its README) |
| `apps/platform/ipro6_if_wifi` | `defconfig_ipro6_sdio` | FIN card firmware (IPRO6S) |

Other boards: `ipro7_sdio_wifi` is the stand-alone `ipronet_host` reference with every bring-up stage as a shell command, and `ipro7_demo` carries the EMAC demo; both are configured for the IPRO7 EVB.

- [Wi-Fi and RTSP tutorial](../tutorials/wifi-rtsp.md): the Reef walk-through with a video player.
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md): the microSD socket, JP3 and the FIN card.
- [OTA Updates](ota.md): updating the FIN card with `ipro6s_ota`.
- [Thread & Matter](thread-matter.md): IEEE 802.15.4 and OpenThread under Zephyr.
