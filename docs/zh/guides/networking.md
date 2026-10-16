---
title: "網路"
description: IPRO7 FreeRTOS 應用的 lwIP 與 mbedTLS，以及兩種連網方式：RMII 乙太網路與經 SDIO 連接 IPRO6S 的 Wi-Fi
migrate_from:
  - "wifi-networking.html"
---

# 網路

FreeRTOS 應用以 lwIP 2.1.2 為 TCP/IP 協定堆疊、mbedTLS 2.28.2 提供 TLS，實體連線有兩種：IPRO7 的 Ethernet MAC（EMAC，RMII）外接 PHY，或以 IPRO6S 作為 Wi-Fi 無線端、經 SDIO 接到 IPRO7（IPRO7AI Reef EVK 上即插入卡槽的 IPRO6S FIN 卡）。兩種方式共用同一個 lwIP，應用程式碼不需因介面不同而改寫。

!!! abstract "重點"
    - 協定堆疊：lwIP 2.1.2（BSD socket API）、mbedTLS 2.28.2；只適用於 FreeRTOS 應用。
    - 有線：EMAC 以 RMII 外接 PHY（附 RTL8201F 驅動）；另有 SPI 的 ENC28J60 測試程式。
    - Wi-Fi：`components/network/ipronet_host` 經 SDIO 驅動 IPRO6S，連線呈現為 lwIP netif `iproeth0`。
    - 未包含：IPRO6S 端與 FIN 卡的 Wi-Fi 韌體、高階 HTTP 用戶端元件。請洽 INTELPRO。

## 網路架構 { #architecture }

<div class="ipro-stack">
  <div class="l-app"><strong>應用</strong><span>sockets / MQTT / RTSP / HTTP</span></div>
  <div class="l-host"><strong>TLS（mbedTLS 2.28.2）</strong><span>components/crypto/mbedtls</span></div>
  <div class="l-hci"><strong>TCP/IP（lwIP 2.1.2）</strong><span>components/network/lwip</span></div>
  <div class="l-ctlr"><strong>網路介面</strong><span>EMAC + RMII PHY │ ipronet_host（SDIO）→ IPRO6S</span></div>
</div>

| 元件 | 路徑 | 說明 |
|---|---|---|
| lwIP | `components/network/lwip/` | TCP/IP 協定堆疊；`lwip_apps/ping` 為 ping 指令 |
| mbedTLS | `components/crypto/mbedtls/` | TLS 與加密；`port/` 為硬體加速與熵來源 |
| EMAC 驅動 | `bsp/drivers/ipro7_soc/std_drv/src/drv_emac.c`、`bsp/hal/src/hal_emac.c` | Ethernet MAC，RMII 模式 |
| 乙太網路 netif | `bsp/hal/src/hal_ethernetif.c`、`phy_rtl8201f.c` | lwIP 與 EMAC 的介接、PHY 驅動 |
| SDIO Wi-Fi host | `components/network/ipronet_host/` | IPRO7 端 SDIO host，netif `iproeth0` |
| RTSP 伺服器 | `components/network/rtsp_server/` | 相機 MJPEG 串流 |
| ATBM6162 驅動 | `components/wireless/wifi_atbm6162/` | 只供探測程式使用，見 [ATBM6162](#wifi-atbm6162) |

## 網路設定 { #network-config }

`.config` 會原樣轉成 `autoconf.h`，Kconfig 的 `select`／`depends on` 不會自動套用，相依的設定都要寫出來。

=== "乙太網路（ipro7_demo）"

    ```ini
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_PING=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_MBEDTLS_ENABLE=y
    CONFIG_MBEDTLS_BIGNUM_USE_HW=y
    ```

=== "Wi-Fi（ipro7ai_reef_demo/defconfig_wifi_ipro6s）"

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

| 設定 | 說明 |
|---|---|
| `CONFIG_COMPONENTS_LWIP_ENABLE` | 加入 lwIP |
| `CONFIG_COMPONENTS_LWIP_APP_ENABLE` | lwIP 應用層 |
| `CONFIG_PING` | `ping` 指令 |
| `CONFIG_DHCPD` | DHCP 伺服器 |
| `CONFIG_ETHERNET` | lwIP 的乙太網路設定（`CFG_ETHERNET_ENABLE`）；`ipronet_host` 也需要 |
| `CONFIG_LWIP_MQTT` | 編入 lwIP 的 MQTT 用戶端 |
| `CONFIG_LWIP_ALTCP` | 編入 lwIP altcp 與 altcp TLS（mbedTLS） |
| `CONFIG_MQTT_VAR_HEADER_BUFFER_LEN` | MQTT 可變標頭緩衝區大小（預設 1024） |
| `CONFIG_COMPONENTS_IPRONET_HOST_ENABLE` | 加入 `ipronet_host`；同時需要 `CONFIG_USE_PSRAM=y` |
| `CONFIG_COMPONENTS_MBEDTLS_ENABLE` | 加入 mbedTLS |
| `CONFIG_RTSP_SERVER`、`CONFIG_RTSP_LISTEN_PORT`、`CONFIG_RTSP_SHELL` | RTSP 伺服器、埠號、`rtsp_cam` 指令 |

應用可在自己的目錄放 `lwipopts_app.h` 覆寫 lwIP 的設定（`lwipopts.h` 以 `__has_include` 載入）。使用 `ipronet_host` 時請複製 `apps/platform/ipro7_sdio_wifi/lwipopts_app.h`；元件 README 指出少了它 TCP 上行速率會明顯下降。

## lwIP 整合 { #lwip }

lwIP 提供 BSD 風格 socket API（`lwip/sockets.h`、`lwip/netdb.h`）。隨 lwIP 一起編入的有 DHCP 用戶端、DNS、SNTP、IPv6、`lwiperf` 與 lwIP 內建的 HTTP 用戶端；DHCP 伺服器、MQTT、mDNS、altcp TLS 依上表的設定加入。

下列 TCP 用戶端與 `apps/platform/common/ipronet_ota_cli/ota_http_fetch.c` 的寫法相同：先解析主機名稱，再建立 socket 並連線。網路介面取得位址後才使用 socket（乙太網路見下節；Wi-Fi 等 `on_got_ip` 回呼）。

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

IPRO7 的 EMAC 以 RMII 連接外部 PHY（10/100 Mbps），HAL 附 RTL8201F PHY 驅動。lwIP 介接在 `bsp/hal/src/hal_ethernetif.c`：連線建立後由其中的 DHCP 任務取得位址，DHCP 逾時則改用該檔定義的靜態位址。EMAC 的腳位見 `bsp/hal/src/hal_emac.c` 與[腳位與周邊對照](../hardware/pinmux.md)；使用前確認板子已接上 RMII PHY。

`ipro7_demo` 的 `emac_lwip` 指令建立 netif 並啟動 lwIP，參考 `apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c`：

```c title="emac_demo.c（節錄）"
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

!!! warning "隨附的 ipro7_demo 不含 EMAC 示範"
    `emac_demo.c` 只在 `CONFIG_DEMO_EMAC=y` 時編譯，而隨附的 `.config` 沒有這一行（建置系統不會套用 Kconfig 預設值）。請在 `apps/platform/ipro7_demo/.config` 加上 `CONFIG_DEMO_EMAC=y` 後重新建置；`ipro7_demo` 開機時會自動執行 `emac_lwip`。

沒有 RMII PHY 時，`apps/test/ipro_enc28j60_test` 可經 SPI 驅動 ENC28J60，以 shell 收發原始乙太網路封包；它沒有整合 lwIP，接線見該應用 README。

## TLS／DTLS（mbedTLS） { #mbedtls }

mbedTLS 2.28.2 以 `CONFIG_COMPONENTS_MBEDTLS_ENABLE=y` 加入。預設設定以 mbedTLS 自身的 `config.h` 為基礎（含 TLS 1.2 用戶端與 X.509）；DTLS 與 EC-JPAKE 只在 OpenThread 建置中保留。應用若在自己的目錄提供 `mbedtls_app_config.h`，會取代整個預設設定（mbedTLS 元件要能從 include 路徑找到它）。熵來源是硬體亂數產生器（`port/entropy_poll_alt.c`）。

| 硬體加速設定 | 對應 |
|---|---|
| `CONFIG_MBEDTLS_BIGNUM_USE_HW` | 大數模冪運算（隨附設定唯一使用的一項，見 `ipro7_demo`） |
| `CONFIG_MBEDTLS_AES_USE_HW`、`CONFIG_MBEDTLS_GCM_USE_HW` | AES、GCM |
| `CONFIG_MBEDTLS_SHA1_USE_HW`、`CONFIG_MBEDTLS_SHA256_USE_HW`、`CONFIG_MBEDTLS_SHA512_USE_HW` | SHA |
| `CONFIG_MBEDTLS_ECDSA_USE_HW`、`CONFIG_MBEDTLS_ECDH_USE_HW` | ECDSA、ECDH |

`CONFIG_MBEDTLS_ECC_USE_HW` 在 IPRO7 上會改用軟體實作（建置時印出警告）。

TLS 用戶端可參考套件內的 `components/crypto/mbedtls/mbedtls/programs/ssl/ssl_client1.c`，移植時：

- 檢查每個初始化與連線呼叫的回傳值。
- 載入目標服務信任的 CA，以 `mbedtls_ssl_conf_ca_chain()` 設定並使用 `MBEDTLS_SSL_VERIFY_REQUIRED`；以 `mbedtls_ssl_set_hostname()` 設定主機名稱。平台時間要正確，才能檢查憑證有效期。
- 處理 `MBEDTLS_ERR_SSL_WANT_READ`／`MBEDTLS_ERR_SSL_WANT_WRITE`、部分傳輸與逾時；所有錯誤路徑都要釋放 TLS context 與 socket。
- 範例中的測試憑證與主機要換成產品實際的設定。

## HTTP、MQTT 與 RTSP { #http-client }

| 協定 | 可用的實作 |
|---|---|
| HTTP | 沒有 SDK 的 HTTP 用戶端元件。可用 lwIP 內建的 HTTP 用戶端（`lwip/apps/http_client.h`）、`components/3rdparty/llhttp`（解析器），或參考 `ota_http_fetch.c` 的 HTTP/1.0 GET |
| MQTT | lwIP 的 MQTT 用戶端（`lwip/apps/mqtt.h`）：設定 `CONFIG_LWIP_MQTT=y`，或像 `ipro_agora_sentino` 在應用的 CMakeLists.txt 編入 `mqtt.c` |
| RTSP | `components/network/rtsp_server`，預設埠 8554；`ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` 以它串流相機 |

HTTPS 與 MQTT over TLS 需自行以 mbedTLS（或 altcp TLS）建立安全連線，並處理狀態碼、分塊傳輸、長度限制與逾時。

## Wi-Fi（IPRO6S 作為 SDIO 無線端） { #wifi-ipro6 }

```mermaid
flowchart LR
  A["IPRO7<br/>應用＋ipronet_host＋lwIP"] -->|"SDIO 4-bit<br/>GPIO28–33"| B["IPRO6S<br/>Wi-Fi 韌體"]
  B -->|Wi-Fi| C["AP"]
```

IPRO7 是 SDIO host，驅動執行 Wi-Fi 韌體的 IPRO6S，並把連線呈現為 lwIP netif `iproeth0`；IP 堆疊在 IPRO7 上。SDH 匯流排固定在 GPIO28–33，由元件設定腳位。

!!! info "需另行取得"
    IPRO6S 端的 Wi-Fi 韌體（含 IPRO7AI Reef EVK 使用的 FIN 卡韌體）未包含於 V2.1.0，請洽 INTELPRO。

`components/network/ipronet_host/ipronet_host.h` 的最小用法（依元件 README，並加上 Reef 的電源設定）：

```c title="以 ipronet_host 連上 AP"
#include "board_config.h"
#include "ipronet_host.h"

static void got_ip(void *arg, const ipronet_ip_info_t *ip)
{
    /* 取得位址後才開啟 socket */
}

void app_main(void)
{
    ipronet_config_t cfg;
    ipronet_config_default(&cfg);            /* 預設值對應 IPRO7 EVB（GPIO15 控制 IPRO6S 電源） */
#ifdef CONFIG_IPRO7AI_REEF
    cfg.pwr_en_gpio    = BOARD_SD_PWR_EN_PIN;            /* Reef：FIN 卡電源 */
    cfg.pwr_active_low = (BOARD_SD_PWR_ON_LEVEL == 0);
#endif
    ipronet_callbacks_t cb = { .on_got_ip = got_ip };
    while (ipronet_start(&cfg, &cb) != IPRONET_OK) {   /* 裝置可能還在開機 */
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    ipronet_connect("<ssid>", "<password>");
}
```

- `ipronet_start()` 是同步呼叫，失敗時會回到閒置狀態，所以用重試迴圈等待裝置開機；`ipronet_stop()` 反向關閉。
- 回呼（`on_connected`、`on_disconnected`、`on_got_ip`、`on_scan_result`）在元件的 RX 任務中執行：不可阻塞，也不可在回呼中呼叫 `ipronet_connect`／`disconnect`／`scan`／`stop`。需要動作時交給自己的任務處理。
- `auto_reconnect = 1`（預設）時由元件負責重連；設為 0 時由應用在 `on_disconnected` 再呼叫 `ipronet_connect()`。
- `ipronet_config_t` 的其他欄位（匯流排時脈、傳送節流）見元件 README；Reef 的完整設定見 `apps/platform/ipro7ai_reef_demo/src/wifi_ipro6s.c`。

### 在 IPRO7AI Reef EVK 上試用

<div class="ipro-steps" markdown>

1. **準備**：把 IPRO6S FIN 卡插進 Reef 的 SD 卡槽，JP3 設在 2-3（讓 `fin cycle` 可以為 FIN 卡重新上電）。

2. **建置並燒錄**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    輸出位於 `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/`；燒錄步驟見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)。

3. **連線**：在 U6 主控台（115200 baud）輸入：

    ```text
    ipronet_up <ssid> <password>
    ```

    取得 IP 後，以 `ipro6s_link_status` 確認連線狀態。

4. **串流**：`rtsp_cam on` 開始相機串流，以 RTSP 播放器開啟 `rtsp://<ip>:8554/av0_0`；`rtsp_cam stats` 查看統計，`rtsp_cam off` 停止。

</div>

| Reef `defconfig_wifi_ipro6s` 指令 | 說明 |
|---|---|
| `ipronet_up [<ssid> <password>]`、`ipronet_down` | 啟動 FIN 卡並連線；關閉 |
| `ipro6s_scan`、`ipro6s_scan_last` | 掃描 AP；列出上次結果 |
| `ipro6s_connect <ssid> <password>`、`ipro6s_disconnect`、`ipro6s_link_status` | 連線、斷線、連線狀態 |
| `rtsp_cam on [fps]`、`off`、`stats` | RTSP 相機串流 |
| `ipro6s_ota <http url>` | 經 HTTP 更新 FIN 卡韌體，見 [OTA 更新](ota.md) |

`apps/platform/ipro7_sdio_wifi` 是以 IPRO7 EVB 為對象的獨立 Wi-Fi 參考應用，提供同樣的 `ipronet_up`／`ipronet_down`，以及逐階段除錯用的 `ipro6s_*` 指令。`apps/multimedia/ipro_agora_sentino` 也以 `ipronet_host` 連網。

## ATBM6162 SDIO 模組 { #wifi-atbm6162 }

V2.1.0 只附 ATBM6162 模組的探測程式 `apps/test/ipro_atbm_probe`，用來確認模組上電、SDIO 列舉、韌體下載與握手（指令 `atbm_init`、`atbm_probe`），不是可直接使用的 Wi-Fi 連網路徑。模組的供電、致能與接線依載板而定，燒錄前請對照探測程式原始碼中的設定。

```bash
make -C apps/test/ipro_atbm_probe
```

## IPRO6S 內建 Wi-Fi 6 { #ipro6s-wifi6 }

IPRO6S 晶片本身的 Wi-Fi 6 開發使用 SDK V2.0.1，見 [IPRO6S（V2.0.1）](../hardware/chips/ipro6s.md)。

## 本版限制 { #limitations }

- 只有 FreeRTOS 應用能連網：Zephyr RTOS 下沒有 Ethernet 驅動，IPRO7 在 Zephyr 下也沒有 Wi-Fi，見 [Zephyr RTOS](zephyr.md)。
- IPRO6S 端與 FIN 卡的 Wi-Fi 韌體未包含於 V2.1.0。
- 沒有高階 HTTP 用戶端元件，也沒有 LTE modem 元件。
- `ipronet_host` 只支援 station 模式與單一 netif，不會偵測傳輸中斷；裝置斷電後以 `ipronet_stop()`、`ipronet_start()` 重新建立。
- `ipro7_sdio_wifi` 的 README 提到 iperf，但它依賴的元件不在套件中。
- `ipro_agora_sentino` 的 MQTT 以明文 TCP 連線；量產產品請改用 MQTT over TLS 並驗證憑證。

## 參考應用 { #reference-apps }

| 應用 | 板子 | 內容 |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo`（`defconfig_wifi_ipro6s`） | IPRO7AI Reef EVK | IPRO6S FIN 卡 Wi-Fi＋RTSP 相機串流 |
| `apps/multimedia/ipro_agora_sentino` | IPRO7AI Reef EVK | BLE 配網、FIN 卡 Wi-Fi、MQTT、Agora RTC 語音 |
| `apps/platform/ipro7_sdio_wifi` | IPRO7 EVB | `ipronet_host` 參考應用與除錯指令 |
| `apps/platform/ipro7_demo` | IPRO7 EVB | lwIP、mbedTLS；EMAC 示範需加 `CONFIG_DEMO_EMAC=y` |
| `apps/test/ipro_enc28j60_test` | IPRO7 Arduino 板（見 README） | ENC28J60（SPI）原始封包測試 |
| `apps/test/ipro_atbm_probe` | IPRO7 EVB | ATBM6162 探測 |

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
make -C apps/multimedia/ipro_agora_sentino          # 需先取得 AOSL 子模組，見該應用 README
make -C apps/platform/ipro7_sdio_wifi
make -C apps/platform/ipro7_demo
```

- [IPRO6S（V2.0.1）](../hardware/chips/ipro6s.md)：Wi-Fi 夥伴晶片的規格與 FIN 卡。
- [OTA 更新](ota.md)：以 `ipro6s_ota` 更新 FIN 卡韌體。
- [Thread 與 Matter](thread-matter.md)：Zephyr 下的 IEEE 802.15.4 與 OpenThread。
