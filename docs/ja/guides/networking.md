---
title: "ネットワーク"
description: IPRO7 の FreeRTOS アプリケーションでの lwIP と mbedTLS、IPRO7AI Reef EVK での SDIO 接続の IPRO6S FIN カードによる Wi-Fi、独自ボードでの RMII イーサネット
migrate_from:
  - "wifi-networking.html"
---

# ネットワーク

FreeRTOS アプリケーションは、TCP/IP スタックに lwIP 2.1.2、TLS に mbedTLS 2.28.2 を使用します。IPRO7 がネットワークにつながる方法は 2 つあります。無線部として動作し SDIO で接続する IPRO6S を経由する Wi-Fi と、外付け PHY を使う IPRO7 のイーサネット MAC（EMAC、RMII）です。IPRO7AI Reef EVK では、この IPRO6S が microSD ソケットに挿す FIN カードです。どちらのリンクも同じ lwIP スタックにつながるため、インターフェースが変わってもソケットのコードは変わりません。

!!! abstract "要点"
    - スタック：FreeRTOS アプリケーションで lwIP 2.1.2（BSD ソケット）と mbedTLS 2.28.2。
    - Reef：microSD ソケットの IPRO6S FIN カードを `components/network/ipronet_host` が SDIO で制御し、リンクは lwIP の netif `iproeth0` として現れます。`defconfig_wifi_ipro6s` でビルドした `ipro7ai_reef_demo` が接続し、カメラ映像を RTSP で配信します。
    - FIN カードのファームウェア：`defconfig_ipro6_sdio` でビルドした `ipro6_if_wifi`。動作中のカードは `ipro6s_ota` を使って Wi-Fi 経由で更新します。
    - イーサネット：外付け PHY を使う RMII モードの EMAC（RTL8201F ドライバーを同梱）。Reef にはイーサネット PHY がありません。
    - 含まれないもの：高レベルの HTTP クライアントコンポーネント。`ipronet_host` のアクセスポイントモードと複数の netif。

## アーキテクチャ { #architecture }

<div class="ipro-stack">
  <div class="l-app"><strong>アプリケーション</strong><span>sockets / MQTT / RTSP / HTTP</span></div>
  <div class="l-host"><strong>TLS（mbedTLS 2.28.2）</strong><span>components/crypto/mbedtls</span></div>
  <div class="l-hci"><strong>TCP/IP（lwIP 2.1.2）</strong><span>components/network/lwip</span></div>
  <div class="l-ctlr"><strong>ネットワークインターフェース</strong><span>ipronet_host（SDIO）→ IPRO6S │ EMAC + RMII PHY</span></div>
</div>

| コンポーネント | パス | 説明 |
|---|---|---|
| lwIP | `components/network/lwip/` | TCP/IP スタック。`lwip_apps/ping` が `ping` コマンドを提供します |
| SDIO Wi-Fi ホスト | `components/network/ipronet_host/` | IPRO6S リンクの IPRO7 側：SDIO トランスポート、netif `iproeth0`、Wi-Fi イベント、IPRO6S のファームウェア更新（`ipronet_ota.h`） |
| RTSP サーバー | `components/network/rtsp_server/` | MJPEG によるカメラ映像の配信 |
| mbedTLS | `components/crypto/mbedtls/` | TLS と暗号。`port/` にハードウェアアクセラレーションとエントロピーソースがあります |
| EMAC ドライバー | `bsp/drivers/ipro7_soc/std_drv/src/drv_emac.c`、`bsp/hal/src/hal_emac.c` | RMII モードのイーサネット MAC |
| イーサネットの netif | `bsp/hal/src/hal_ethernetif.c`、`bsp/hal/src/phy_rtl8201f.c` | lwIP と EMAC をつなぐグルーコードと PHY ドライバー |

## ネットワークの設定 { #network-config }

ビルドは `.config` を書かれたとおりに `autoconf.h` にコピーします。Kconfig の `select` と `depends on` は適用されないため、リンクに必要なキーはすべて明示的に書いてください。

=== "Reef の Wi-Fi（defconfig_wifi_ipro6s）"

    ```ini title="apps/platform/ipro7ai_reef_demo/defconfig_wifi_ipro6s（抜粋）"
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

=== "イーサネット（独自ボード）"

    ```ini title="apps/platform/ipro7_demo/.config（抜粋）"
    CONFIG_COMPONENTS_LWIP_ENABLE=y
    CONFIG_COMPONENTS_LWIP_APP_ENABLE=y
    CONFIG_ETHERNET=y
    CONFIG_COMPONENTS_MBEDTLS_ENABLE=y
    CONFIG_MBEDTLS_BIGNUM_USE_HW=y
    ```

| キー | 説明 |
|---|---|
| `CONFIG_COMPONENTS_LWIP_ENABLE` | lwIP を追加します |
| `CONFIG_ETHERNET` | lwIP のバッファーをイーサネット向けのサイズにします（`CFG_ETHERNET_ENABLE`）。`ipronet_host` にも必要です |
| `CONFIG_COMPONENTS_IPRONET_HOST_ENABLE` | `ipronet_host` を追加します。`CONFIG_USE_PSRAM=y` が必要です |
| `CONFIG_IPRO7_WIFI_HOST_HOTCODE` | `ipronet_host`、lwIP、FreeRTOS のデータパスを Flash ではなく PSRAM から実行します。`CONFIG_USE_PSRAM=y` が必要で、`CONFIG_IPRO7_BLE_HOTCODE` や低消費電力のレイアウトとは併用できません |
| `CONFIG_WIFI_USE_IPRO6S` | `ipro7ai_reef_demo` 専用：Wi-Fi シェル（`src/wifi_ipro6s.c`）と `ipro6s_ota` コマンドをコンパイルします |
| `CONFIG_RTSP_SERVER`、`CONFIG_RTSP_LISTEN_PORT`、`CONFIG_RTSP_DEFAULT_VIDEO_FPS`、`CONFIG_RTSP_SHELL` | RTSP サーバー、そのポート、デフォルトのフレームレート、デモの `rtsp_cam` コマンド |
| `CONFIG_PING` | `ping` コマンド |
| `CONFIG_DHCPD`、`CONFIG_MDNS` | DHCP サーバー、mDNS レスポンダー |
| `CONFIG_LWIP_MQTT` | lwIP の MQTT クライアント |
| `CONFIG_LWIP_ALTCP` | lwIP の altcp と、mbedTLS を使う altcp TLS |
| `CONFIG_MQTT_VAR_HEADER_BUFFER_LEN` | MQTT の可変ヘッダーのバッファーサイズ |
| `CONFIG_COMPONENTS_MBEDTLS_ENABLE` | mbedTLS を追加します |

アプリケーションは独自の `lwipopts_app.h` で lwIP の設定を上書きできます。このファイルがあれば `lwipopts.h` がインクルードします。`ipronet_host` を使う場合は `apps/platform/ipro7ai_reef_demo/lwipopts_app.h`（`ipro7_sdio_wifi` と同じファイル）をコピーしてください。このファイルは lwIP のバッファーを PSRAM に移し、TCP ウィンドウを拡大します。コンポーネントの README によると、このファイルがないと TCP のアップロードスループットは約 4 分の 1 に低下します。

## lwIP { #lwip }

lwIP は BSD 形式のソケット API（`lwip/sockets.h`、`lwip/netdb.h`）を提供します。DHCP クライアント、DNS、SNTP、IPv6、`lwiperf`、lwIP の HTTP クライアントは組み込み済みです。DHCP サーバー、mDNS、MQTT、altcp TLS は上記のキーで追加します。

次の TCP クライアントは、`ipro7ai_reef_demo` が `ipro6s_ota` 用にコンパイルする `apps/platform/common/ipronet_ota_cli/ota_http_fetch.c` の手順に沿っています。ホスト名を解決し、ソケットを開いて接続します。ソケットは、インターフェースにアドレスが割り当てられてから使用してください（`ipronet_host` の場合は `on_got_ip` コールバックの後）。

```c title="TCP クライアント"
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

## イーサネット { #emac }

IPRO7 の EMAC は RMII（10/100 Mbps）で外付け PHY に接続します。HAL には RTL8201F の PHY ドライバーが含まれています。Reef には PHY が搭載されていないため、この経路は独自ボード向けです。lwIP とのグルーコードは `bsp/hal/src/hal_ethernetif.c` です。リンクが確立すると DHCP タスクがアドレスを要求し、DHCP がタイムアウトした場合は同ファイルで定義された静的アドレスを使います。EMAC のピンについては `bsp/hal/src/hal_emac.c` と[ピン配置と周辺機能の対応](../hardware/pinmux.md)を参照してください。

netif の追加と lwIP の起動は、`apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c` と同じ方法で行います。

```c title="apps/platform/ipro7_demo/demo/soc/peripheral/emac_demo.c（抜粋）"
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

`ipro7_demo` は IPRO7 EVB 向けで、`emac_demo.c` は `CONFIG_DEMO_EMAC=y` のときだけコンパイルされます。同梱の `.config` ではこのキーは設定されていません。

## TLS／DTLS（mbedTLS） { #mbedtls }

mbedTLS 2.28.2 は `CONFIG_COMPONENTS_MBEDTLS_ENABLE=y` で追加します。デフォルトの設定は mbedTLS 自身の `config.h` をベースにしており、TLS 1.2 クライアントと X.509 を含みます。アプリケーションが独自の `mbedtls_app_config.h` を用意すると、デフォルトの設定全体が置き換えられます（mbedTLS コンポーネントのインクルードパスから見つかる必要があります）。エントロピーはハードウェア乱数生成器から取得します（`port/entropy_poll_alt.c`）。

| ハードウェアアクセラレーションのキー | 対象 |
|---|---|
| `CONFIG_MBEDTLS_BIGNUM_USE_HW` | 多倍長整数のべき剰余演算 |
| `CONFIG_MBEDTLS_AES_USE_HW`、`CONFIG_MBEDTLS_GCM_USE_HW` | AES、GCM |
| `CONFIG_MBEDTLS_SHA1_USE_HW`、`CONFIG_MBEDTLS_SHA256_USE_HW`、`CONFIG_MBEDTLS_SHA512_USE_HW` | SHA |
| `CONFIG_MBEDTLS_ECDSA_USE_HW`、`CONFIG_MBEDTLS_ECDH_USE_HW` | ECDSA、ECDH |

IPRO7 では、`CONFIG_MBEDTLS_ECC_USE_HW` はソフトウェア実装にフォールバックし、ビルド時に警告が表示されます。

TLS クライアントは `components/crypto/mbedtls/mbedtls/programs/ssl/ssl_client1.c` から始めてください。移植する際は次の点に注意します。

- 初期化と接続の各呼び出しの戻り値を確認します。
- サービスが信頼する CA 証明書を `mbedtls_ssl_conf_ca_chain()` で読み込み、`MBEDTLS_SSL_VERIFY_REQUIRED` を使用し、`mbedtls_ssl_set_hostname()` でホスト名を設定します。証明書の有効期間を検証するため、プラットフォームの時刻が正しい必要があります。
- `MBEDTLS_ERR_SSL_WANT_READ` / `MBEDTLS_ERR_SSL_WANT_WRITE`、部分的な転送、タイムアウトを処理し、すべてのエラー経路で TLS コンテキストとソケットを解放します。
- サンプルのテスト用証明書とホストを、製品のものに置き換えます。

## HTTP、MQTT、RTSP { #http-client }

| プロトコル | 利用できるもの |
|---|---|
| HTTP | SDK の HTTP クライアントコンポーネントはありません。lwIP の HTTP クライアント（`lwip/apps/http_client.h`）、`components/3rdparty/llhttp`（パーサー）を使うか、`ota_http_fetch.c` の HTTP/1.0 GET を参考にしてください |
| MQTT | lwIP の MQTT クライアント（`lwip/apps/mqtt.h`）：`CONFIG_LWIP_MQTT=y` を設定するか、`ipro_agora_sentino` のようにアプリケーションの `CMakeLists.txt` で `mqtt.c` をコンパイルします |
| RTSP | `components/network/rtsp_server`、デフォルトのポートは 8554。Reef のデモの `rtsp_cam` コマンドがこれを使ってカメラ映像を配信します |

HTTPS や TLS 上の MQTT を使う場合は、mbedTLS（または altcp TLS）でセキュアな接続を自分で構築し、ステータスコード、チャンク転送、長さの上限、タイムアウトを処理してください。

## IPRO6S 経由の Wi-Fi { #wifi-ipro6 }

```mermaid
flowchart LR
  A["IPRO7<br/>アプリケーション + ipronet_host + lwIP"] -->|"SDIO 4-bit<br/>GPIO28–33"| B["IPRO6S<br/>ipro6_if_wifi"]
  B -->|Wi-Fi| C["アクセスポイント"]
```

IPRO7 が SDIO ホストです。IPRO6S は `ipro6_if_wifi` を実行し、イーサネットフレームを Wi-Fi にブリッジします。DHCP は IPRO6S 上で動作し、IP スタックとユーザーのソケットは IPRO7 上で動作します。SDIO バスは GPIO28～33 に固定されており、ピンの設定はコンポーネントが行います。Reef ではこれらが microSD ソケットの信号線であるため、FIN カードが SD カードの代わりにソケットに入ります。

| 項目 | Reef の場合 |
|---|---|
| 無線部 | microSD ソケットの IPRO6S FIN カード。ソケットの電源から給電 |
| カードの電源 | GPIO14（`BOARD_SD_PWR_EN_PIN`、Low でオン）。JP3 が **GPIO** の場合はファームウェアでカードの電源を入れ直せます（`fin cycle`、`ipronet_start()`）。JP3 が ON の場合、カードには常に電源が供給されます |
| FIN カードのファームウェア | `make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio` → `build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`。IPRO6S のイメージは IntelProCube の `--chipname ipro6` で書き込みます |
| ファームウェアの更新 | Reef のコンソールで `ipro6s_ota <http url>` を実行すると、IPRO6S の OTA パッケージ（`FW_OTA.bin.xz.ota`）を取得してカードにインストールします。[OTA アップデート](ota.md)を参照してください |

`ipronet_host.h` の概要：

| 呼び出し | 動作 |
|---|---|
| `ipronet_config_default(&cfg)` | `ipronet_config_t` をコンポーネントのデフォルト値で埋めます。ボードに合わせて `pwr_en_gpio`、`pwr_active_low`、`bus_hz` を設定します |
| `ipronet_start(&cfg, &cb)` | IPRO6S の電源を入れて列挙し、RX タスクを起動して `iproeth0` を有効にします。同期呼び出しで、失敗するとアイドル状態に戻るため、カードの起動中は再試行してください |
| `ipronet_connect(ssid, psk)` | アクセスポイントに接続します。続いて `on_connected`、`on_got_ip` が呼ばれます |
| `ipronet_scan()`、`ipronet_disconnect()`、`ipronet_stop()` | スキャン（結果は `on_scan_result`）、AP からの切断、`ipronet_start()` の取り消し |
| `ipronet_is_connected()`、`ipronet_has_ip()`、`ipronet_get_ip()`、`ipronet_get_mac()` | 状態の取得。どのタスクからでも安全に呼び出せます |

- コールバック（`on_connected`、`on_disconnected`、`on_got_ip`、`on_scan_result`）はコンポーネントの RX タスクで実行されます。コールバック内でブロックしたり、`ipronet_connect` / `disconnect` / `scan` / `stop` を呼び出したりしないでください。処理は独自のタスクに渡します。
- `auto_reconnect = 1`（デフォルト）の場合、切断後にコンポーネントが AP に再接続します。0 の場合は、アプリケーションが `on_disconnected` から `ipronet_connect()` を再度呼び出します。
- リターンコードはすべて `ipronet_host.h`（`IPRONET_OK` は 0）と `components/network/ipronet_host/README.md` に記載されています。

## Reef でのハンズオン { #hands-on }

出荷時ファームウェアのシェルコマンドを使って、Reef から Wi-Fi ネットワークに接続し、カメラ映像を RTSP で配信します。ホスト側のビデオプレーヤーを使うチュートリアル版は、[Wi-Fi と RTSP のチュートリアル](../tutorials/wifi-rtsp.md)です。

`ipro6_if_wifi`（`defconfig_ipro6_sdio`）を書き込んだ IPRO6S FIN カード、カメラコネクターに接続した OV5640 または OV2640 カメラモジュール、Wi-Fi アクセスポイントが必要です。

<div class="ipro-steps" markdown>

1. **ボードを準備する**

    USB-C を抜いた状態で、FIN カードを microSD ソケットに挿し、JP3 を **GPIO**、SW7 を **CAM** にします。

2. **設定**

    Wi-Fi ビルドは `ipro7ai_reef_demo` の別の設定ファイルです。追加されるキーは[ネットワークの設定](#network-config)に記載しています。独自のアプリケーションでは、それらの行、`lwipopts_app.h`、デモの `CMakeLists.txt` の `CONFIG_WIFI_USE_IPRO6S` ブロックをコピーします。

3. **コード**

    `ipronet_up <ssid> <psk>` が、アプリケーションに必要な接続手順のすべてです。ボードの電源設定、`ipronet_start()`、`ipronet_connect()` の順に実行します。

    ```c title="apps/platform/ipro7ai_reef_demo/src/wifi_ipro6s.c（抜粋）"
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

    `s_app_cb` は 4 つのコールバックを持つ `ipronet_callbacks_t` で、同じファイルで定義されています。独自のアプリケーションでは、`on_got_ip` が実行されてからソケットを開いてください。

4. **ビルド**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    イメージは `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin` です。

5. **書き込み**

    Reef をダウンロードモードにし（SW1 を押したまま SW2 を押して離し、SW1 を離す）、IntelProCube のディレクトリで次を実行します。

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    `[All Success]` を確認してから SW2 を押します。詳しくは[書き込みとシリアルコンソール](../get-started/flash-and-monitor.md)を参照してください。

6. **接続して配信する**

    115200 baud でコンソールを開き、次を入力します。

    ```text
    ipronet_up <ssid> <psk>
    rtsp_cam on
    ```

    成功すると、コンソールに両方の呼び出しのリターンコード 0、アソシエーションとアドレス、ストリームの URL が表示されます。

    ```text
    ipronet_start -> 0
    ipronet_connect '<ssid>' -> 0
    [ctrl] STA CONNECTED
    [ctrl] IP 192.168.1.23 / 255.255.255.0 gw 192.168.1.1
    rtsp_cam: on, <sensor> <width>x<height> JPEG q<quality>, 15 fps
    rtsp_cam: rtsp://192.168.1.23:8554/av0_0
    ```

    `[ctrl]` の行はコンポーネントの RX タスクから出力されるため、コンソール上で文字化けすることがあります。`ipro6s_link_status` で状態を再表示できます（`host connected=1 ip=1`）。同じネットワーク上の RTSP プレーヤーで URL を開きます。`rtsp_cam stats` でフレームカウンターを表示し、`rtsp_cam off` でストリームを停止します。

</div>

| コマンド（`defconfig_wifi_ipro6s`） | 用途 |
|---|---|
| `ipronet_up [<ssid> <psk>]`、`ipronet_down` | `ipronet_start()` と、必要に応じて `ipronet_connect()`。`ipronet_stop()` |
| `ipro6s_scan`、`ipro6s_scan_last` | アクセスポイントをスキャン。直前の結果を表示 |
| `ipro6s_connect <ssid> <psk>`、`ipro6s_disconnect`、`ipro6s_link_status` | 接続、切断、リンク状態 |
| `rtsp_cam on [fps]`、`rtsp_cam off`、`rtsp_cam stats` | `rtsp://<ip>:8554/av0_0` での RTSP カメラストリーム |
| `ipro6s_ota <http url>` | FIN カードのファームウェアを HTTP で更新 |
| `fin`、`fin cycle` | ソケットの状態。カードの電源を入れ直す（JP3 が GPIO の場合） |

次のステップ：[最初の独自アプリケーションを作る](../tutorials/first-own-app.md)でこの設定から独自のアプリケーションを作成し、[アプリケーションのテスト](../tutorials/testing.md)で確認します。

## その他の Wi-Fi モジュール { #wifi-atbm6162 }

Reef が Wi-Fi に接続する手段は IPRO6S FIN カードだけです。パッケージに含まれるその他の SDIO Wi-Fi モジュール用のドライバーとプローブコードは IPRO7 EVB 向けで、Reef でサポートされる経路ではありません。[サンプル](../examples/index.md)を参照してください。

## Wi-Fi デバイスとしての IPRO6S { #ipro6s-wifi6 }

リンクの IPRO6S 側は、同じ SDK に含まれる IPRO6S 用の FreeRTOS アプリケーションです。出力ファイル名は `_IPRO6.bin` で終わります。ビルド済みの Wi-Fi ライブラリは同梱の設定に対してのみ用意されているため、いずれかの設定の Wi-Fi オプションと `CONFIG_WIRELESS_LIB_VARIANT` はそのまま使用してください。

| アプリケーション | 設定 | 役割 |
|---|---|---|
| `ipro6_if_wifi` | `defconfig_ipro6_sdio` | SDIO ホスト向けの Wi-Fi 6 ブリッジ：FIN カードのファームウェア |
| `ipro6_if_wifi` | `defconfig_ipro6_usb` | USB ホスト向けの同じブリッジ |
| `ipro6_demo` | `.config`、`defconfig_ipro6_lpwifi` | IPRO6S EVK 上の単体の Wi-Fi 6 ステーション／soft-AP |
| `ipro6_fmac` | `defconfig_ipro6_fmac` | Linux cfg80211 ホスト向けの FullMAC ファームウェア。Linux ドライバーはこのパッケージに含まれていません |

チップ、ボード、書き込みについては [IPRO6S](../hardware/chips/ipro6s.md) を参照してください。

## 本リリースの制限事項 { #limitations }

- ネットワーク機能は FreeRTOS アプリケーションでのみ使用できます。Zephyr にはイーサネットドライバーも `ipronet_host` もありません。`zephyr/drivers/wifi` の Zephyr Wi-Fi ドライバーは IPRO6S のオンチップドライバーであり、本リリースでは IPRO6S は Zephyr でサポートされていません。[Zephyr RTOS](zephyr.md) を参照してください。
- `ipronet_host` はステーションモードと単一の netif のみに対応し、トランスポートの停止を検出しません。カードの電源が失われた場合は、`ipronet_stop()` と `ipronet_start()` で復旧してください。
- 高レベルの HTTP クライアントコンポーネントとセルラーモデムのコンポーネントはありません。
- `ipro7_sdio_wifi` の README には `iperf` が記載されていますが、それが依存するコンポーネントはパッケージに含まれていません。
- `ipro_agora_sentino` は平文の TCP で MQTT に接続します。製品では、証明書の検証を伴う TLS 上の MQTT を使用してください。

## 参照アプリケーション { #reference-apps }

| アプリケーション | 設定 | 内容 |
|---|---|---|
| `apps/platform/ipro7ai_reef_demo` | `defconfig_wifi_ipro6s` | FIN カードによる Wi-Fi、RTSP カメラストリーム、`ipro6s_ota` |
| `apps/multimedia/ipro_agora_sentino` | `.config` | BLE プロビジョニング、FIN カードによる Wi-Fi、MQTT、Agora RTC の音声。AOSL コアと Sentino のデバイストリプルが必要です（README を参照） |
| `apps/platform/ipro6_if_wifi` | `defconfig_ipro6_sdio` | FIN カードのファームウェア（IPRO6S） |

その他のボード：`ipro7_sdio_wifi` は、立ち上げの各段階をシェルコマンドとして備えた単体の `ipronet_host` リファレンスで、`ipro7_demo` には EMAC のデモが含まれています。どちらも IPRO7 EVB 向けに設定されています。

- [Wi-Fi と RTSP のチュートリアル](../tutorials/wifi-rtsp.md)：ビデオプレーヤーを使った Reef での手順。
- [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)：microSD ソケット、JP3、FIN カード。
- [OTA アップデート](ota.md)：`ipro6s_ota` による FIN カードの更新。
- [Thread と Matter](thread-matter.md)：Zephyr での IEEE 802.15.4 と OpenThread。
