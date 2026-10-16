---
title: "Networking"
description: lwIP and mbedTLS in IPRO7 FreeRTOS applications, and the two ways to connect — RMII Ethernet and Wi-Fi through an IPRO6S over SDIO
migrate_from:
  - "wifi-networking.html"
---

# Networking

FreeRTOS applications use lwIP 2.1.2 as the TCP/IP stack and mbedTLS 2.28.2 for TLS, over one of two physical links: the IPRO7 Ethernet MAC (EMAC, RMII) with an external PHY, or an IPRO6S acting as the Wi-Fi radio and attached to IPRO7 over SDIO (on the IPRO7AI Reef EVK, the IPRO6S FIN card in the card slot). Both links share the same lwIP stack, so application code does not change with the interface.

!!! abstract "At a glance"
    - Stack: lwIP 2.1.2 (BSD socket API) and mbedTLS 2.28.2; FreeRTOS applications only.
    - Wired: EMAC in RMII mode with an external PHY (an RTL8201F driver is included), plus an ENC28J60-over-SPI test app.
    - Wi-Fi: `components/network/ipronet_host` drives an IPRO6S over SDIO and presents the link as the lwIP netif `iproeth0`.
    - Not included: the Wi-Fi firmware for the IPRO6S side and the FIN card, and a high-level HTTP client component. Contact INTELPRO.

## Architecture { #architecture }

<div class="ipro-stack">
  <div class="l-app"><strong>Application</strong><span>sockets / MQTT / RTSP / HTTP</span></div>
  <div class="l-host"><strong>TLS (mbedTLS 2.28.2)</strong><span>components/crypto/mbedtls</span></div>
  <div class="l-hci"><strong>TCP/IP (lwIP 2.1.2)</strong><span>components/network/lwip</span></div>
  <div class="l-ctlr"><strong>Network interface</strong><span>EMAC + RMII PHY │ ipronet_host (SDIO) → IPRO6S</span></div>
</div>

| Component | Path | Notes |
|---|---|---|
| lwIP | `components/network/lwip/` | TCP/IP stack; `lwip_apps/ping` provides the ping command |
| mbedTLS | `components/crypto/mbedtls/` | TLS and crypto; `port/` holds hardware acceleration and the entropy source |
| EMAC driver | `bsp/drivers/ipro7_soc/std_drv/src/drv_emac.c`, `bsp/hal/src/hal_emac.c` | Ethernet MAC in RMII mode |
| Ethernet netif | `bsp/hal/src/hal_ethernetif.c`, `phy_rtl8201f.c` | lwIP-to-EMAC glue and the PHY driver |
| SDIO Wi-Fi host | `components/network/ipronet_host/` | IPRO7-side SDIO host, netif `iproeth0` |
| RTSP server | `components/network/rtsp_server/` | Camera MJPEG streaming |
| ATBM6162 driver | `components/wireless/wifi_atbm6162/` | Used by a probe app only; see [ATBM6162](#wifi-atbm6162) |

## Network configuration { #network-config }

`.config` is turned into `autoconf.h` as written; Kconfig `select` and `depends on` are not applied, so spell out every dependent key.

=== "Ethernet (ipro7_demo)"

    ```ini
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_PING=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_MBEDTLS_ENABLE=y
    CONFIG_MBEDTLS_BIGNUM_USE_HW=y
    ```

=== "Wi-Fi (ipro7ai_reef_demo/defconfig_wifi_ipro6s)"

    ```ini
    CONFIG_USE_PSRAM=y
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_IPRONET_HOST_ENABLE=y
    CONFIG_RTSP_SERVER=y
    CONFIG_RTSP_LISTEN_PORT=8554
    CONFIG_RTSP_SHELL=y
    ```

| Key | Notes |
|---|---|
| `CONFIG_COMPONENTS_LWIP_ENABLE` | Adds lwIP |
| `CONFIG_COMPONENTS_LWIP_APP_ENABLE` | lwIP application layer |
| `CONFIG_PING` | `ping` command |
| `CONFIG_DHCPD` | DHCP server |
| `CONFIG_ETHERNET` | lwIP's Ethernet settings (`CFG_ETHERNET_ENABLE`); `ipronet_host` needs it too |
| `CONFIG_LWIP_MQTT` | Builds lwIP's MQTT client |
| `CONFIG_LWIP_ALTCP` | Builds lwIP altcp and altcp TLS (mbedTLS) |
| `CONFIG_MQTT_VAR_HEADER_BUFFER_LEN` | MQTT variable header buffer size (default 1024) |
| `CONFIG_COMPONENTS_IPRONET_HOST_ENABLE` | Adds `ipronet_host`; also needs `CONFIG_USE_PSRAM=y` |
| `CONFIG_COMPONENTS_MBEDTLS_ENABLE` | Adds mbedTLS |
| `CONFIG_RTSP_SERVER`, `CONFIG_RTSP_LISTEN_PORT`, `CONFIG_RTSP_SHELL` | RTSP server, its port, the `rtsp_cam` command |

An application can override lwIP settings with its own `lwipopts_app.h` (`lwipopts.h` pulls it in with `__has_include`). With `ipronet_host`, copy `apps/platform/ipro7_sdio_wifi/lwipopts_app.h`; the component README notes that TCP upload throughput drops sharply without it.

## lwIP { #lwip }

lwIP provides a BSD-style socket API (`lwip/sockets.h`, `lwip/netdb.h`). Built in with lwIP are the DHCP client, DNS, SNTP, IPv6, `lwiperf` and lwIP's own HTTP client; the DHCP server, MQTT, mDNS and altcp TLS are added with the keys above.

This TCP client follows the same steps as `apps/platform/common/ipronet_ota_cli/ota_http_fetch.c`: resolve the host name, then open a socket and connect. Use sockets only after the interface has an address (for Ethernet see the next section; for Wi-Fi wait for the `on_got_ip` callback).

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

The IPRO7 EMAC connects to an external PHY over RMII (10/100 Mbps), and the HAL includes an RTL8201F PHY driver. The lwIP glue is `bsp/hal/src/hal_ethernetif.c`: once the link is up, its DHCP task obtains an address, and if DHCP times out it falls back to the static address defined in that file. For the EMAC pins see `bsp/hal/src/hal_emac.c` and [Pinout & Peripheral Mapping](../hardware/pinmux.md); make sure your board actually carries an RMII PHY.

The `emac_lwip` command of `ipro7_demo` creates the netif and starts lwIP; see `apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c`:

```c title="emac_demo.c (excerpt)"
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

!!! warning "The shipped ipro7_demo has no EMAC demo"
    `emac_demo.c` is compiled only with `CONFIG_DEMO_EMAC=y`, and the shipped `.config` does not contain that line (the build does not apply Kconfig defaults). Add `CONFIG_DEMO_EMAC=y` to `apps/platform/ipro7_demo/.config` and rebuild; `ipro7_demo` then runs `emac_lwip` automatically at boot.

Without an RMII PHY, `apps/test/ipro_enc28j60_test` drives an ENC28J60 over SPI and sends and receives raw Ethernet frames from the shell. It has no lwIP integration; see its README for wiring.

## TLS / DTLS (mbedTLS) { #mbedtls }

mbedTLS 2.28.2 is added with `CONFIG_COMPONENTS_MBEDTLS_ENABLE=y`. The default configuration builds on mbedTLS's own `config.h` (including the TLS 1.2 client and X.509); DTLS and EC-JPAKE are kept only in OpenThread builds. An application that provides its own `mbedtls_app_config.h` replaces the whole default configuration (the mbedTLS component must be able to find it on its include path). Entropy comes from the hardware random number generator (`port/entropy_poll_alt.c`).

| Hardware acceleration key | Covers |
|---|---|
| `CONFIG_MBEDTLS_BIGNUM_USE_HW` | Big-number modular exponentiation (the only one set in a shipped configuration, `ipro7_demo`) |
| `CONFIG_MBEDTLS_AES_USE_HW`, `CONFIG_MBEDTLS_GCM_USE_HW` | AES, GCM |
| `CONFIG_MBEDTLS_SHA1_USE_HW`, `CONFIG_MBEDTLS_SHA256_USE_HW`, `CONFIG_MBEDTLS_SHA512_USE_HW` | SHA |
| `CONFIG_MBEDTLS_ECDSA_USE_HW`, `CONFIG_MBEDTLS_ECDH_USE_HW` | ECDSA, ECDH |

On IPRO7, `CONFIG_MBEDTLS_ECC_USE_HW` falls back to the software implementation (the build prints a warning).

For a TLS client, start from `components/crypto/mbedtls/mbedtls/programs/ssl/ssl_client1.c` in the package. When porting it:

- Check the return value of every initialization and connection call.
- Load the CA certificates your service trusts with `mbedtls_ssl_conf_ca_chain()`, use `MBEDTLS_SSL_VERIFY_REQUIRED`, and set the host name with `mbedtls_ssl_set_hostname()`. The platform clock must be right for certificate validity checks.
- Handle `MBEDTLS_ERR_SSL_WANT_READ` / `MBEDTLS_ERR_SSL_WANT_WRITE`, partial transfers and timeouts, and free the TLS context and the socket on every error path.
- Replace the example's test certificates and host with your product's.

## HTTP, MQTT and RTSP { #http-client }

| Protocol | What is available |
|---|---|
| HTTP | No SDK HTTP client component. Use lwIP's built-in HTTP client (`lwip/apps/http_client.h`), `components/3rdparty/llhttp` (parser), or the HTTP/1.0 GET in `ota_http_fetch.c` as a reference |
| MQTT | lwIP's MQTT client (`lwip/apps/mqtt.h`): set `CONFIG_LWIP_MQTT=y`, or compile `mqtt.c` in the application's CMakeLists.txt as `ipro_agora_sentino` does |
| RTSP | `components/network/rtsp_server`, default port 8554; `ipro7ai_reef_demo`'s `defconfig_wifi_ipro6s` streams the camera with it |

For HTTPS or MQTT over TLS, build the secure connection with mbedTLS (or altcp TLS) yourself, and handle status codes, chunked transfer, length limits and timeouts.

## Wi-Fi (IPRO6S as the SDIO radio) { #wifi-ipro6 }

```mermaid
flowchart LR
  A["IPRO7<br/>app + ipronet_host + lwIP"] -->|"SDIO 4-bit<br/>GPIO28–33"| B["IPRO6S<br/>Wi-Fi firmware"]
  B -->|Wi-Fi| C["AP"]
```

IPRO7 is the SDIO host. It drives an IPRO6S running the Wi-Fi firmware and presents the link as the lwIP netif `iproeth0`; the IP stack runs on IPRO7. The SDH bus is fixed to GPIO28–33, and the component sets up those pins.

!!! info "Obtain separately"
    The Wi-Fi firmware for the IPRO6S side (including the FIN card firmware used on the IPRO7AI Reef EVK) is not included in V2.1.0. Contact INTELPRO.

Minimal use of `components/network/ipronet_host/ipronet_host.h` (from the component README, with the Reef power settings added):

```c title="Join an AP with ipronet_host"
#include "board_config.h"
#include "ipronet_host.h"

static void got_ip(void *arg, const ipronet_ip_info_t *ip)
{
    /* Open sockets only after this */
}

void app_main(void)
{
    ipronet_config_t cfg;
    ipronet_config_default(&cfg);            /* defaults are for the IPRO7 EVB (GPIO15 switches the IPRO6S rail) */
#ifdef CONFIG_IPRO7AI_REEF
    cfg.pwr_en_gpio    = BOARD_SD_PWR_EN_PIN;            /* Reef: FIN card rail */
    cfg.pwr_active_low = (BOARD_SD_PWR_ON_LEVEL == 0);
#endif
    ipronet_callbacks_t cb = { .on_got_ip = got_ip };
    while (ipronet_start(&cfg, &cb) != IPRONET_OK) {   /* the device may still be booting */
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    ipronet_connect("<ssid>", "<password>");
}
```

- `ipronet_start()` is synchronous and returns to idle on failure, so wait for the device to boot with a retry loop; `ipronet_stop()` undoes it.
- The callbacks (`on_connected`, `on_disconnected`, `on_got_ip`, `on_scan_result`) run in the component's RX task. They must not block, and must not call `ipronet_connect` / `disconnect` / `scan` / `stop`; hand the work to your own task.
- With `auto_reconnect = 1` (the default) the component handles reconnection; with 0 your application calls `ipronet_connect()` again from `on_disconnected`.
- For the remaining `ipronet_config_t` fields (bus clock, transmit pacing) see the component README; the complete Reef setup is in `apps/platform/ipro7ai_reef_demo/src/wifi_ipro6s.c`.

### Try it on the IPRO7AI Reef EVK

<div class="ipro-steps" markdown>

1. **Prepare**: insert the IPRO6S FIN card into the Reef's SD card slot and set JP3 to 2-3 (so `fin cycle` can power-cycle the card).

2. **Build and flash**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    The output is in `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/`; for flashing see [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md).

3. **Connect**: at the U6 console (115200 baud), enter:

    ```text
    ipronet_up <ssid> <password>
    ```

    Once an IP address is assigned, check the link with `ipro6s_link_status`.

4. **Stream**: `rtsp_cam on` starts the camera stream; open `rtsp://<ip>:8554/av0_0` in an RTSP player. `rtsp_cam stats` shows statistics and `rtsp_cam off` stops it.

</div>

| Reef `defconfig_wifi_ipro6s` command | Purpose |
|---|---|
| `ipronet_up [<ssid> <password>]`, `ipronet_down` | Start the FIN card and connect; shut down |
| `ipro6s_scan`, `ipro6s_scan_last` | Scan for APs; print the last result |
| `ipro6s_connect <ssid> <password>`, `ipro6s_disconnect`, `ipro6s_link_status` | Connect, disconnect, link status |
| `rtsp_cam on [fps]`, `off`, `stats` | RTSP camera stream |
| `ipro6s_ota <http url>` | Update the FIN card firmware over HTTP; see [OTA Updates](ota.md) |

`apps/platform/ipro7_sdio_wifi` is a stand-alone Wi-Fi reference application for the IPRO7 EVB. It offers the same `ipronet_up` / `ipronet_down` plus `ipro6s_*` commands for step-by-step debugging. `apps/multimedia/ipro_agora_sentino` also connects through `ipronet_host`.

## ATBM6162 SDIO module { #wifi-atbm6162 }

For the ATBM6162 module, V2.1.0 includes only the probe application `apps/test/ipro_atbm_probe`, which checks module power-up, SDIO enumeration, firmware download and the handshake (commands `atbm_init`, `atbm_probe`). It is not a ready-to-use Wi-Fi connection path. Module power, enable and wiring depend on the carrier board; check the settings in the probe's source before flashing.

```bash
make -C apps/test/ipro_atbm_probe
```

## IPRO6S built-in Wi-Fi 6 { #ipro6s-wifi6 }

Development for the IPRO6S chip's own Wi-Fi 6 uses SDK V2.0.1; see [IPRO6S (V2.0.1)](../hardware/chips/ipro6s.md).

## Limitations in this release { #limitations }

- Only FreeRTOS applications can use the network: there is no Ethernet driver under Zephyr RTOS, and IPRO7 has no Wi-Fi under Zephyr either. See [Zephyr RTOS](zephyr.md).
- The Wi-Fi firmware for the IPRO6S side and the FIN card is not included in V2.1.0.
- There is no high-level HTTP client component and no LTE modem component.
- `ipronet_host` supports station mode and a single netif only, and does not detect a dead transport; after the device loses power, recover with `ipronet_stop()` and `ipronet_start()`.
- The `ipro7_sdio_wifi` README mentions iperf, but the component it relies on is not in the package.
- `ipro_agora_sentino` connects to MQTT over plain TCP; for products, use MQTT over TLS with certificate verification.

## Reference applications { #reference-apps }

| Application | Board | What it does |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` (`defconfig_wifi_ipro6s`) | IPRO7AI Reef EVK | IPRO6S FIN card Wi-Fi + RTSP camera stream |
| `apps/multimedia/ipro_agora_sentino` | IPRO7AI Reef EVK | BLE provisioning, FIN card Wi-Fi, MQTT, Agora RTC voice |
| `apps/platform/ipro7_sdio_wifi` | IPRO7 EVB | `ipronet_host` reference application and debug commands |
| `apps/platform/ipro7_demo` | IPRO7 EVB | lwIP, mbedTLS; the EMAC demo needs `CONFIG_DEMO_EMAC=y` |
| `apps/test/ipro_enc28j60_test` | IPRO7 Arduino board (see its README) | ENC28J60 (SPI) raw-frame test |
| `apps/test/ipro_atbm_probe` | IPRO7 EVB | ATBM6162 probe |

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
make -C apps/multimedia/ipro_agora_sentino          # needs the AOSL submodule first; see the app README
make -C apps/platform/ipro7_sdio_wifi
make -C apps/platform/ipro7_demo
```

- [IPRO6S (V2.0.1)](../hardware/chips/ipro6s.md): the Wi-Fi companion chip and the FIN card.
- [OTA Updates](ota.md): updating the FIN-card firmware with `ipro6s_ota`.
- [Thread & Matter](thread-matter.md): IEEE 802.15.4 and OpenThread under Zephyr.
