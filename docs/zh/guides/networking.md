---
title: "網路"
description: IPRO7 FreeRTOS 應用的 lwIP 與 mbedTLS、IPRO7AI Reef EVK 經 SDIO 透過 IPRO6S FIN 卡連 Wi-Fi，以及自家板子上的 RMII 乙太網路
migrate_from:
  - "wifi-networking.html"
---

# 網路

FreeRTOS 應用以 lwIP 2.1.2 為 TCP/IP 協定堆疊、mbedTLS 2.28.2 提供 TLS。IPRO7 連網有兩種方式：以 IPRO6S 作為無線端、經 SDIO 連接的 Wi-Fi，或 IPRO7 的 Ethernet MAC（EMAC，RMII）外接 PHY。在 IPRO7AI Reef EVK 上，IPRO6S 就是插在 microSD 插槽裡的 FIN 卡。兩種連線共用同一個 lwIP，socket 程式碼不必因介面不同而改寫。

!!! abstract "重點"
    - 協定堆疊：lwIP 2.1.2（BSD socket）與 mbedTLS 2.28.2，用於 FreeRTOS 應用。
    - Reef：microSD 插槽裡的 IPRO6S FIN 卡，由 `components/network/ipronet_host` 經 SDIO 驅動，連線呈現為 lwIP netif `iproeth0`。`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 可連上 AP 並以 RTSP 串流相機。
    - FIN 卡韌體：`ipro6_if_wifi` 以 `defconfig_ipro6_sdio` 建置；運作中的卡可用 `ipro6s_ota` 經 Wi-Fi 更新。
    - 乙太網路：EMAC 以 RMII 外接 PHY（附 RTL8201F 驅動）。Reef 板上沒有乙太網路 PHY。
    - 未包含：高階 HTTP 用戶端元件；`ipronet_host` 的 AP 模式與多個 netif。

## 網路架構 { #architecture }

<div class="ipro-stack">
  <div class="l-app"><strong>應用</strong><span>sockets / MQTT / RTSP / HTTP</span></div>
  <div class="l-host"><strong>TLS（mbedTLS 2.28.2）</strong><span>components/crypto/mbedtls</span></div>
  <div class="l-hci"><strong>TCP/IP（lwIP 2.1.2）</strong><span>components/network/lwip</span></div>
  <div class="l-ctlr"><strong>網路介面</strong><span>ipronet_host（SDIO）→ IPRO6S │ EMAC + RMII PHY</span></div>
</div>

| 元件 | 路徑 | 說明 |
|---|---|---|
| lwIP | `components/network/lwip/` | TCP/IP 協定堆疊；`lwip_apps/ping` 提供 `ping` 指令 |
| SDIO Wi-Fi host | `components/network/ipronet_host/` | IPRO6S 連線的 IPRO7 端：SDIO 傳輸、netif `iproeth0`、Wi-Fi 事件、IPRO6S 韌體更新（`ipronet_ota.h`） |
| RTSP 伺服器 | `components/network/rtsp_server/` | MJPEG 相機串流 |
| mbedTLS | `components/crypto/mbedtls/` | TLS 與加密；`port/` 為硬體加速與熵來源 |
| EMAC 驅動 | `bsp/drivers/ipro7_soc/std_drv/src/drv_emac.c`、`bsp/hal/src/hal_emac.c` | Ethernet MAC，RMII 模式 |
| 乙太網路 netif | `bsp/hal/src/hal_ethernetif.c`、`bsp/hal/src/phy_rtl8201f.c` | lwIP 與 EMAC 的介接、PHY 驅動 |

## 網路設定 { #network-config }

建置時 `.config` 會原樣轉成 `autoconf.h`，Kconfig 的 `select`／`depends on` 不會套用，連線需要的設定都要寫出來。

=== "Reef 的 Wi-Fi（defconfig_wifi_ipro6s）"

    ```ini title="apps/platform/ipro7ai_reef_demo/defconfig_wifi_ipro6s（節錄）"
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

=== "乙太網路（自家板子）"

    ```ini title="apps/platform/ipro7_demo/.config（節錄）"
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_MBEDTLS_ENABLE=y
    CONFIG_MBEDTLS_BIGNUM_USE_HW=y
    ```

| 設定 | 說明 |
|---|---|
| `CONFIG_COMPONENTS_LWIP_ENABLE` | 加入 lwIP |
| `CONFIG_ETHERNET` | lwIP 的乙太網路大小緩衝區（`CFG_ETHERNET_ENABLE`）；`ipronet_host` 也需要 |
| `CONFIG_COMPONENTS_IPRONET_HOST_ENABLE` | 加入 `ipronet_host`；需要 `CONFIG_USE_PSRAM=y` |
| `CONFIG_IPRO7_WIFI_HOST_HOTCODE` | `ipronet_host`、lwIP 與 FreeRTOS 的資料路徑改從 PSRAM 執行，不走 flash；需要 `CONFIG_USE_PSRAM=y`，不能與 `CONFIG_IPRO7_BLE_HOTCODE` 或低功耗記憶體佈局並用 |
| `CONFIG_WIFI_USE_IPRO6S` | `ipro7ai_reef_demo` 專用：編入它的 Wi-Fi shell（`src/wifi_ipro6s.c`）與 `ipro6s_ota` 指令 |
| `CONFIG_RTSP_SERVER`、`CONFIG_RTSP_LISTEN_PORT`、`CONFIG_RTSP_DEFAULT_VIDEO_FPS`、`CONFIG_RTSP_SHELL` | RTSP 伺服器、埠號、預設影格率；範例的 `rtsp_cam` 指令 |
| `CONFIG_PING` | `ping` 指令 |
| `CONFIG_DHCPD`、`CONFIG_MDNS` | DHCP 伺服器、mDNS |
| `CONFIG_LWIP_MQTT` | lwIP 的 MQTT 用戶端 |
| `CONFIG_LWIP_ALTCP` | lwIP altcp 與以 mbedTLS 實作的 altcp TLS |
| `CONFIG_MQTT_VAR_HEADER_BUFFER_LEN` | MQTT 可變標頭緩衝區大小 |
| `CONFIG_COMPONENTS_MBEDTLS_ENABLE` | 加入 mbedTLS |

應用可在自己的目錄放 `lwipopts_app.h` 覆寫 lwIP 設定，`lwipopts.h` 找得到就會載入。使用 `ipronet_host` 時，請複製 `apps/platform/ipro7ai_reef_demo/lwipopts_app.h`（與 `ipro7_sdio_wifi` 的是同一份）：它把 lwIP 緩衝區放到 PSRAM 並加大 TCP 視窗。元件 README 指出少了它，TCP 上行速率會掉到約四分之一。

## lwIP 整合 { #lwip }

lwIP 提供 BSD 風格的 socket API（`lwip/sockets.h`、`lwip/netdb.h`）。DHCP 用戶端、DNS、SNTP、IPv6、`lwiperf` 與 lwIP 的 HTTP 用戶端都已編入；DHCP 伺服器、mDNS、MQTT 與 altcp TLS 依上表的設定加入。

下列 TCP 用戶端與 `apps/platform/common/ipronet_ota_cli/ota_http_fetch.c` 的步驟相同（`ipro7ai_reef_demo` 為 `ipro6s_ota` 編入這個檔案）：解析主機名稱、建立 socket、連線。網路介面取得位址後才使用 socket（使用 `ipronet_host` 時，就是 `on_got_ip` 回呼之後）。

```c title="TCP 用戶端"
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

## 乙太網路 { #emac }

IPRO7 的 EMAC 以 RMII（10/100 Mbps）外接 PHY，HAL 附 RTL8201F PHY 驅動。Reef 板上沒有 PHY，這條路徑用於自家設計的板子。lwIP 介接在 `bsp/hal/src/hal_ethernetif.c`：連線建立後由它的 DHCP 任務取得位址，DHCP 逾時則改用該檔案中定義的靜態位址。EMAC 腳位見 `bsp/hal/src/hal_emac.c` 與[腳位與周邊對照](../hardware/pinmux.md)。

加入 netif、啟動 lwIP 的方式與 `apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c` 相同：

```c title="apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c（節錄）"
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

`ipro7_demo` 的對象是 IPRO7 EVB，且只有在 `CONFIG_DEMO_EMAC=y` 時才編入 `emac_demo.c`；隨附的 `.config` 沒有這一行。

## TLS／DTLS（mbedTLS） { #mbedtls }

以 `CONFIG_COMPONENTS_MBEDTLS_ENABLE=y` 加入 mbedTLS 2.28.2。預設設定以 mbedTLS 本身的 `config.h` 為基礎，含 TLS 1.2 用戶端與 X.509。應用若提供自己的 `mbedtls_app_config.h`，會取代整份預設設定（mbedTLS 元件必須能在 include 路徑上找到它）。熵來源是硬體亂數產生器（`port/entropy_poll_alt.c`）。

| 硬體加速設定 | 涵蓋 |
|---|---|
| `CONFIG_MBEDTLS_BIGNUM_USE_HW` | 大數模冪運算 |
| `CONFIG_MBEDTLS_AES_USE_HW`、`CONFIG_MBEDTLS_GCM_USE_HW` | AES、GCM |
| `CONFIG_MBEDTLS_SHA1_USE_HW`、`CONFIG_MBEDTLS_SHA256_USE_HW`、`CONFIG_MBEDTLS_SHA512_USE_HW` | SHA |
| `CONFIG_MBEDTLS_ECDSA_USE_HW`、`CONFIG_MBEDTLS_ECDH_USE_HW` | ECDSA、ECDH |

在 IPRO7 上，`CONFIG_MBEDTLS_ECC_USE_HW` 會退回軟體實作，建置時會印出警告。

TLS 用戶端可從 `components/crypto/mbedtls/mbedtls/programs/ssl/ssl_client1.c` 開始。移植時：

- 檢查每個初始化與連線呼叫的回傳值。
- 以 `mbedtls_ssl_conf_ca_chain()` 載入服務信任的 CA 憑證，使用 `MBEDTLS_SSL_VERIFY_REQUIRED`，並以 `mbedtls_ssl_set_hostname()` 設定主機名稱。驗證憑證有效期需要正確的系統時間。
- 處理 `MBEDTLS_ERR_SSL_WANT_READ`／`MBEDTLS_ERR_SSL_WANT_WRITE`、部分傳輸與逾時，並在每個錯誤路徑釋放 TLS context 與 socket。
- 把範例的測試憑證與主機換成產品自己的。

## HTTP、MQTT 與 RTSP { #http-client }

| 協定 | 可用的實作 |
|---|---|
| HTTP | 沒有 SDK 的 HTTP 用戶端元件。可用 lwIP 的 HTTP 用戶端（`lwip/apps/http_client.h`）、`components/3rdparty/llhttp`（解析器），或參考 `ota_http_fetch.c` 的 HTTP/1.0 GET |
| MQTT | lwIP 的 MQTT 用戶端（`lwip/apps/mqtt.h`）：設定 `CONFIG_LWIP_MQTT=y`，或像 `ipro_agora_sentino` 在應用的 `CMakeLists.txt` 編入 `mqtt.c` |
| RTSP | `components/network/rtsp_server`，預設埠 8554；Reef 範例的 `rtsp_cam` 指令以它串流相機 |

HTTPS 與 MQTT over TLS 需自行以 mbedTLS（或 altcp TLS）建立安全連線，並處理狀態碼、分塊傳輸、長度限制與逾時。

## 經 IPRO6S 連 Wi-Fi { #wifi-ipro6 }

```mermaid
flowchart LR
  A["IPRO7<br/>應用＋ipronet_host＋lwIP"] -->|"SDIO 4-bit<br/>GPIO28–33"| B["IPRO6S<br/>ipro6_if_wifi"]
  B -->|Wi-Fi| C["無線基地台"]
```

IPRO7 是 SDIO host。IPRO6S 執行 `ipro6_if_wifi`，在乙太網路封包與 Wi-Fi 之間橋接；DHCP 在 IPRO6S 上執行，IP 協定堆疊與應用的 socket 在 IPRO7 上。SDIO 匯流排固定在 GPIO28–33，由元件設定腳位。在 Reef 上這就是 microSD 插槽的訊號線，FIN 卡插在原本放 SD 卡的位置。

| 項目 | Reef 上的做法 |
|---|---|
| 無線端 | 插在 microSD 插槽的 IPRO6S FIN 卡，由插槽電源供電 |
| 卡片電源 | GPIO14（`BOARD_SD_PWR_EN_PIN`，低電位為開）。JP3 設在 **GPIO** 時，韌體可以為卡片重新上電（`fin cycle`、`ipronet_start()`）；JP3 設在 ON 時卡片一直有電 |
| FIN 卡韌體 | `make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio` → `build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。IPRO6S 映像以 IntelProCube `--chipname ipro6` 燒錄 |
| 韌體更新 | 在 Reef 主控台輸入 `ipro6s_ota <http url>`，下載 IPRO6S OTA 套件（`FW_OTA.bin.xz.ota`）並安裝到卡上，見 [OTA 更新](ota.md) |

`ipronet_host.h` 摘要：

| 呼叫 | 作用 |
|---|---|
| `ipronet_config_default(&cfg)` | 以元件預設值填入 `ipronet_config_t`；再依板子設定 `pwr_en_gpio`、`pwr_active_low` 與 `bus_hz` |
| `ipronet_start(&cfg, &cb)` | 為 IPRO6S 上電並列舉、啟動 RX 任務、啟用 `iproeth0`。同步呼叫；任何一步失敗都會回到閒置狀態，卡片開機期間以重試等待 |
| `ipronet_connect(ssid, psk)` | 連上 AP；之後依序觸發 `on_connected`、`on_got_ip` |
| `ipronet_scan()`、`ipronet_disconnect()`、`ipronet_stop()` | 掃描（結果在 `on_scan_result`）、離開 AP、反向關閉 `ipronet_start()` |
| `ipronet_is_connected()`、`ipronet_has_ip()`、`ipronet_get_ip()`、`ipronet_get_mac()` | 狀態查詢，任何任務都可呼叫 |

- 回呼（`on_connected`、`on_disconnected`、`on_got_ip`、`on_scan_result`）在元件的 RX 任務中執行：不可阻塞，也不可呼叫 `ipronet_connect`／`disconnect`／`scan`／`stop`。需要動作時交給自己的任務。
- `auto_reconnect = 1`（預設）時，斷線後由元件重新連上 AP；設為 0 時由應用在 `on_disconnected` 再呼叫 `ipronet_connect()`。
- 所有回傳碼列在 `ipronet_host.h`（`IPRONET_OK` 為 0）與 `components/network/ipronet_host/README.md`。

## 在 Reef 上動手做 { #hands-on }

以出廠韌體的 shell 指令讓 Reef 連上 Wi-Fi，並以 RTSP 串流相機。搭配電腦端播放器的完整步驟見 [Wi-Fi 與 RTSP 教學](../tutorials/wifi-rtsp.md)。

需要：執行 `ipro6_if_wifi`（`defconfig_ipro6_sdio`）的 IPRO6S FIN 卡、接在相機連接器上的 OV5640 或 OV2640 相機模組，以及一台 Wi-Fi 無線基地台。

<div class="ipro-steps" markdown>

1. **準備板子**

    拔掉 USB-C，把 FIN 卡插進 microSD 插槽，JP3 設在 **GPIO**，SW7 設在 **CAM**。

2. **設定**

    Wi-Fi 版是 `ipro7ai_reef_demo` 的另一份設定檔，它加上的設定列在[網路設定](#network-config)。自己的應用要連網時，複製這些設定、`lwipopts_app.h`，以及範例 `CMakeLists.txt` 中 `CONFIG_WIFI_USE_IPRO6S` 的區塊。

3. **程式碼**

    `ipronet_up <ssid> <psk>` 就是應用連網所需的完整流程：板子的電源設定、`ipronet_start()`，再 `ipronet_connect()`。

    ```c title="apps/platform/ipro7ai_reef_demo/src/wifi_ipro6s.c（節錄）"
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

    `s_app_cb` 是同一檔案中定義、含四個回呼的 `ipronet_callbacks_t`。自己的應用請在 `on_got_ip` 之後才開啟 socket。

4. **建置**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    映像為 `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin`。

5. **燒錄**

    讓 Reef 進入下載模式（按住 SW1、按一下 SW2、放開 SW1），再在 IntelProCube 目錄執行：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    確認輸出有 `[All Success]` 後按 SW2。細節見[燒錄與序列埠](../get-started/flash-and-monitor.md)。

6. **連線並串流**

    以 115200 baud 開啟主控台，輸入：

    ```text
    ipronet_up <ssid> <psk>
    rtsp_cam on
    ```

    成功時，兩個呼叫都回傳 0，接著出現連線與位址，最後是串流網址：

    ```text
    ipronet_start -> 0
    ipronet_connect '<ssid>' -> 0
    [ctrl] STA CONNECTED
    [ctrl] IP 192.168.1.23 / 255.255.255.0 gw 192.168.1.1
    rtsp_cam: on, <sensor> <width>x<height> JPEG q<quality>, 15 fps
    rtsp_cam: rtsp://192.168.1.23:8554/av0_0
    ```

    `[ctrl]` 開頭的行由元件的 RX 任務印出，在主控台上可能亂掉；`ipro6s_link_status` 會再報一次狀態（`host connected=1 ip=1`）。在同一個網路的 RTSP 播放器開啟這個網址。`rtsp_cam stats` 顯示影格計數，`rtsp_cam off` 停止串流。

</div>

| 指令（`defconfig_wifi_ipro6s`） | 說明 |
|---|---|
| `ipronet_up [<ssid> <psk>]`、`ipronet_down` | `ipronet_start()`，並可接著 `ipronet_connect()`；`ipronet_stop()` |
| `ipro6s_scan`、`ipro6s_scan_last` | 掃描 AP；列出上次結果 |
| `ipro6s_connect <ssid> <psk>`、`ipro6s_disconnect`、`ipro6s_link_status` | 連線、斷線、連線狀態 |
| `rtsp_cam on [fps]`、`rtsp_cam off`、`rtsp_cam stats` | `rtsp://<ip>:8554/av0_0` 的 RTSP 相機串流 |
| `ipro6s_ota <http url>` | 經 HTTP 更新 FIN 卡韌體 |
| `fin`、`fin cycle` | 插槽狀態；為卡片重新上電（JP3 設在 GPIO） |

下一步：以這份設定為起點，依[建立第一個自己的應用](../tutorials/first-own-app.md)動手做，再依[測試你的應用](../tutorials/testing.md)驗證。

## 其他 Wi-Fi 模組 { #wifi-atbm6162 }

Reef 只透過 IPRO6S FIN 卡連 Wi-Fi。套件中其他 SDIO Wi-Fi 模組的驅動與探測程式以 IPRO7 EVB 為對象，不是 Reef 支援的路徑，見[範例](../examples/index.md)。

## IPRO6S 作為 Wi-Fi 裝置端 { #ipro6s-wifi6 }

連線的 IPRO6S 端是同一套 SDK 中的 IPRO6S FreeRTOS 應用，輸出檔名以 `_IPRO6.bin` 結尾。它的預編譯 Wi-Fi 函式庫只針對隨附的設定檔提供，請保留其中一份的 Wi-Fi 設定與 `CONFIG_WIRELESS_LIB_VARIANT`。

| 應用 | 設定檔 | 角色 |
|---|---|---|
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | 連接 SDIO host 的 Wi-Fi 6 橋接：FIN 卡韌體 |
| `ipro6_if_wifi` | `defconfig_ipro6_usb` | 同樣的橋接，連接 USB host |
| `ipro6_demo` | `.config`、`defconfig_ipro6_lpwifi` | IPRO6S EVB 上獨立運作的 Wi-Fi 6 station／soft-AP |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | 給 Linux cfg80211 主機的 FullMAC 韌體；Linux 驅動不在本套件中 |

晶片、板子與燒錄見 [IPRO6S](../hardware/chips/ipro6s.md)。

## 本版限制 { #limitations }

- 只有 FreeRTOS 應用能連網。Zephyr 下沒有乙太網路驅動，也沒有 `ipronet_host`；`zephyr/drivers/wifi` 是 IPRO6S 晶片本身的驅動，而本版 Zephyr 不支援 IPRO6S。見 [Zephyr RTOS](zephyr.md)。
- `ipronet_host` 只支援 station 模式與單一 netif，也不會偵測傳輸中斷：卡片斷電後以 `ipronet_stop()`、`ipronet_start()` 重新建立。
- 沒有高階 HTTP 用戶端元件，也沒有行動網路數據機元件。
- `ipro7_sdio_wifi` 的 README 提到 `iperf`，但它依賴的元件不在套件中。
- `ipro_agora_sentino` 的 MQTT 以明文 TCP 連線；量產產品請改用 MQTT over TLS 並驗證憑證。

## 參考應用 { #reference-apps }

| 應用 | 設定檔 | 內容 |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` | `defconfig_wifi_ipro6s` | FIN 卡 Wi-Fi、RTSP 相機串流、`ipro6s_ota` |
| `apps/multimedia/ipro_agora_sentino` | `.config` | BLE 配網、FIN 卡 Wi-Fi、MQTT、Agora RTC 語音；需要 AOSL 核心與 Sentino 裝置三元組（見該應用 README） |
| `apps/platform/ipro6_if_wifi` | `defconfig_ipro6_sdio` | FIN 卡韌體（IPRO6S） |

其他板子：`ipro7_sdio_wifi` 是獨立的 `ipronet_host` 參考應用，每個啟動階段都有對應的 shell 指令；`ipro7_demo` 含 EMAC 示範。兩者都以 IPRO7 EVB 為對象。

- [Wi-Fi 與 RTSP 教學](../tutorials/wifi-rtsp.md)：搭配電腦端播放器的 Reef 完整步驟。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：microSD 插槽、JP3 與 FIN 卡。
- [OTA 更新](ota.md)：以 `ipro6s_ota` 更新 FIN 卡。
- [Thread 與 Matter](thread-matter.md)：Zephyr 下的 IEEE 802.15.4 與 OpenThread。
