---
title: "工具命令列"
description: SDK V2.2.0 隨附主機端工具的命令、選項與範例：build_freertos.sh、make、IntelProCube 燒錄工具、serial_monitor.py、create_ota.py、Reef 的 Teach 與 OTA 工具，以及未隨附的項目。
migrate_from:
  - "tools-debugging.html#overview"
  - "tools-debugging.html#build-cli"
  - "tools-debugging.html#zephyr-tools"
  - "tools-debugging.html#automated-testing"
  - "tools-debugging.html#size-analysis"
  - "tools-debugging.html#dev-workflow"
---

# 工具命令列

SDK 隨附主機端工具的命令格式、選項與範例，範例以 IPRO7AI Reef EVK V4.0 為準。逐步的燒錄與主控台操作見[燒錄與序列埠](../get-started/flash-and-monitor.md)。

## 工具一覽 { #overview }

| 工具 | 路徑 | 用途 | 取得方式 |
|---|---|---|---|
| `build_freertos.sh` | SDK 根目錄 | 建置、清除、燒錄、主控台、大小報告與自動測試 | 隨附 |
| `make` ＋ `project.build` | 各應用的 `Makefile` | 建置單一應用 | 隨附 |
| `serial_monitor.py` | `tools/` | 讀取主控台，可先送一行指令、等待指定字串並存檔（macOS、Linux；非互動式終端機） | 隨附 |
| `create_ota.py` | `tools/` | 把 IntelProCube 的合併映像封裝成 boot2 OTA 套件 | 隨附 |
| 瀏覽器版影像 Teach | `tools/teach_web/` | 在 Chrome／Edge 中收集影像、訓練分類器並部署到 `ipro_reef_teach` | 隨附 |
| `mfg_payload.py` | `apps/ai/ipro_reef_teach/` | 產生 `ipro_reef_teach` 的 `--mfg` 燒錄內容（模式與聲紋模型） | 隨附 |
| Reef BLE OTA 工具 | `apps/bluetooth/ble/ipro_ble_remote/tools/` | `make_reef_ota.sh`、`reef_ota.py`、`reef_ble_test.py`，以及 Android 示範 App `ipro_remote_demo.apk`（在應用目錄） | 隨附 |
| `parse_kconfig_dynamic.py` | `tools/script/` | 把 Kconfig 樹匯出成 JSON（需要 kconfiglib，建置流程不使用） | 隨附 |
| CMake 3.15 | `tools/cmake/` | 系統沒有 `cmake` 時的備用版本，僅限 Linux x86-64 | 隨附 |
| Zephyr 腳本 | `tools/zephyr/` | Zephyr 工作區、建置、燒錄與主控台（`ipro7_evb`、`ipro7ai_evk` 板型） | 隨附 |
| IntelProCube v0.6.3 命令列燒錄工具 | `ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | 經序列埠燒錄韌體、分割表、boot2 與 `mfg` 內容 | 未包含於 V2.2.0，請洽 INTELPRO |
| RISC-V 工具鏈 | `/opt/toolchain/riscv_ipro7/` | 編譯（GCC 14，`riscv64-unknown-elf-`） | 未包含於 V2.2.0，請洽 INTELPRO |
| IPRO AI Studio | — | IPRO AI Teach、模型轉換與部署 | 不在 SDK 內，從 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下載 |
| OpenOCD／GDB 連線設定、板級自動測試腳本 `tools/board_test.sh`、當機傾印主機工具 | — | 晶片上除錯、自動上板測試、讀取 `==DUMP_READY:` 後的記憶體 | 未包含於 V2.2.0，請洽 INTELPRO |
| `tools/kconfig/menuconfig.py`、`configs/` 預設設定目錄、OTA 簽章用的 `ota_products.py` | — | `make menuconfig`、`make defconfig`、`create_ota.py --sign-key` | 未包含於 V2.2.0 |

本版沒有以 JTAG／GDB 進行晶片上除錯的設定與步驟；除錯以序列埠主控台、日誌與離線的 `addr2line` 為主，見[除錯與疑難排解](debugging.md)。

## 環境變數 { #environment }

| 變數 | 使用的工具 | 作用 |
|---|---|---|
| `IPRO_FLASH_TOOL` | `build_freertos.sh`、`make_reef_ota.sh`、`tools/zephyr/flash.sh`、`west flash` | IntelProCube 命令列工具的路徑。未設定時在 `PATH` 中尋找本機作業系統對應的工具名稱 |
| `IPRO_SERIAL_PORT` | `build_freertos.sh`、`tools/zephyr/` 腳本、`west flash` | 預設序列埠。未設定且未指定 `-p` 時，若系統上只有一個 USB 序列埠就自動使用它 |
| `IPRO_CHIP_VARIANT` | `build_freertos.sh flash` | 燒錄時的 `--chip-variant`（`IPRO7` 或 `IPRO7AI`）。未設定時依應用設定自動選擇，見 [build_freertos.sh](#build-cli) |
| `IPRO_FLASH_PT` | `build_freertos.sh flash` | 燒錄時的 `--pt` 分割表。未設定時不傳 `--pt`，由工具使用預設分割表 |
| `IPRO_PROBE_PORT` | `west flash` | IPRO Debug Probe 的 UART 橋接埠，預設與 `--port` 相同 |
| `CROSS_COMPILE` | `make`、`build_freertos.sh build` | 工具鏈前綴；在環境或命令列設定時優先於 `.config` 的 `CONFIG_CROSS_COMPILE` |
| `IPRO_TOOLCHAIN` | `tools/zephyr/bootstrap.sh` | Zephyr 工作區使用的工具鏈目錄，預設 `/opt/toolchain/riscv_ipro7` |
| `IPRO_ZEPHYR_WS` | `tools/zephyr/build.sh`、`ci_build.sh` | Zephyr 工作區位置，預設 `<SDK>/zephyr-workspace` |

## build_freertos.sh { #build-cli }

```text
./build_freertos.sh [動作...] [選項] <專案>
```

動作可串接，依序執行；任一動作失敗即停止。未指定動作時執行 `build`。這是 bash 腳本，在 macOS 與 Linux 上執行。

| 動作 | 說明 |
|---|---|
| `build` | 執行 `make -C <應用>`，記錄寫入 `<建置目錄>/build.log`，成功時印出 `.bin` 路徑與大小；失敗時印出記錄最後 30 行 |
| `clean` | 刪除建置目錄 |
| `flash` | 以應用的主控台鮑率送出 `reboot_dl`，等 2 秒，再以 IntelProCube 工具燒錄：`--chipname ipro7 --chip-variant <自動> --baudrate 921600`，有 `-P` 時加上 `--pt`。以輸出中的 `[All Success]` 判定成功。不會先建置 |
| `monitor` | 以應用的主控台鮑率開啟 `serial_monitor.py`，先送出 `reboot`，`-t` 秒後結束 |
| `size` | 對 ELF 執行 `size` 與 `size -A`（列出前 30 行區段） |
| `test` | 建置、燒錄，再送出 `reboot` 並等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；結束碼 0 通過、1 失敗、2 逾時 |

主控台鮑率取自所用設定檔的 `CONFIG_PLATFORM_UART_BAUDRATE`，未設定時為 115200。

| 選項 | 說明 | 預設值 |
|---|---|---|
| `-p, --port PORT` | 序列埠 | `$IPRO_SERIAL_PORT`，否則唯一的 USB 序列埠 |
| `-t, --timeout SEC` | `monitor`、`test` 的秒數 | `30` |
| `-w, --wait-for PAT` | `monitor` 等待的正規表示式 | — |
| `-d, --defconfig FILE` | 改用應用目錄中的替代設定檔，建置至 `build_<名稱>/`（`defconfig_reef` → `build_reef/`） | — |
| `-c, --chip-variant V` | 燒錄的 `--chip-variant`：`IPRO7` 或 `IPRO7AI` | `$IPRO_CHIP_VARIANT`；否則設定檔有 `CONFIG_IPRO7AI_REEF=y` 或 `CONFIG_IPRO7AI_EVK=y` 時為 `IPRO7AI`，其餘為 `IPRO7` |
| `-P, --pt TABLE` | 燒錄的分割表：`.toml` 路徑（轉成絕對路徑後傳給工具），或工具 `chips/ipro7/partition/` 下的表名 | `$IPRO_FLASH_PT`，否則不傳 |
| `-j, --jobs N` | 外層 `make` 的平行工作數；內層 CMake 建置固定 `-j4` | — |
| `-v, --verbose` | 顯示完整建置輸出 | — |
| `-l, --list` | 依分類列出 `apps/` 下全部 40 個專案 | — |
| `-h, --help` | 說明 | — |

`<專案>` 可寫應用名稱（`ipro7ai_reef_demo`），或 `apps/` 之下的路徑（`platform/ipro7ai_reef_demo`）。名稱不唯一或找不到時，會列出候選名稱。`-l` 的說明欄取自 `.config` 第一行註解，部分應用會顯示空白。

在 Reef 上一次完成建置、燒錄與開啟主控台（第一次燒錄前，板子上還沒有 SDK 韌體可回應 `reboot_dl`，請先依[進入下載模式](debugging.md#download-mode)手動進入）：

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

畫面依序出現：

```text
→ Entering download mode...
→ Flashing ipro7ai_reef_demo_IPRO7.bin (--chip-variant IPRO7AI, --pt <IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml)...
...
✓ Flash succeeded (…)
→ Opening serial monitor on /dev/cu.usbserial-XXXX at 115200...
```

其他 Reef 設定以 `-d` 選擇，例如：

```bash
./build_freertos.sh -d defconfig_reef build ipro_ble_remote          # 輸出在 build_reef/build_out/
./build_freertos.sh -d defconfig_reef_ov5640 build flash ipro7_uvc_cam
./build_freertos.sh -l                                              # 列出 40 個專案
./build_freertos.sh size ipro7ai_reef_demo
```

產出位於 `<應用>/build/build_out/`（使用 `-d` 時為 `build_<名稱>/build_out/`）：`<應用>_<晶片>.bin`、`.elf`、`.map`，晶片取自 `CONFIG_CHIP`（IPRO7 應用為 `_IPRO7`，IPRO6S 應用為 `_IPRO6`）。

!!! warning "build_freertos.sh 的限制"
    - `flash` 固定傳 `--chipname ipro7`：IPRO6S 應用（例如 FIN 卡韌體 `ipro6_if_wifi`）請直接以 IntelProCube 的 `--chipname ipro6` 燒錄。
    - 無法傳 `--boot2`、`--mfg` 或 `--skip-ota`：`ipro_ble_remote` 的第一次燒錄（boot2 ＋ A/B 分割表）與 `ipro_reef_teach`（自有分割表與 `mfg` 內容）請直接使用 [IntelProCube 工具](#flash-tool)。
    - 沒有 `BOARD=` 選項；`config_<板子>` 檔可用 `-d config_evk` 指定，輸出在 `build_config_evk/`。
    - 燒錄工具在目前的工作目錄執行；`-P` 請給 `.toml` 的完整路徑。
    - `size` 固定使用 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size`，不讀取 `CROSS_COMPILE`。

## make 目標 { #make-targets }

每個應用的 `Makefile` 都轉呼叫 SDK 根目錄的 `project.build`（CMake 以 `Unix Makefiles` 產生器設定，再以 `make -j4` 建置）。

| 命令 | 說明 |
|---|---|
| `make -C apps/<分類>/<應用>` | 以 `.config` 建置至 `build/` |
| `make -C apps/<分類>/<應用> clean` | 刪除建置目錄（加 `DEFCONFIG=` 時刪除對應的 `build_<名稱>/`） |
| `make -C apps/<分類>/<應用> DEFCONFIG=defconfig_<名稱>` | 以替代設定建置至 `build_<名稱>/`，不改動 `.config` |
| `make -C apps/<分類>/<應用> CROSS_COMPILE=<路徑>/bin/riscv64-unknown-elf-` | 指定工具鏈前綴，優先於 `.config` 的 `CONFIG_CROSS_COMPILE` |
| `make -C apps/multimedia/ipro_agora_sentino BOARD=evk` | 只有 `ipro_agora_sentino`（預設 `reef`＝`.config`）與 `ipro_pdm_mic_demo`（預設 `evb`）支援 `BOARD=`：改用 `config_<板子>`，建置至 `build_config_<板子>/` |

- CMake：優先使用 `PATH` 上的 `cmake`，找不到才用 `tools/cmake/`（Linux x86-64）；兩者都沒有時停在 `No cmake found`。
- 每次建置後，`compile_commands.json` 會複製到 SDK 根目錄，供編輯器使用。
- `make menuconfig` 需要未隨附的 `tools/kconfig/menuconfig.py`；部分 `Makefile` 的 `defconfig`、`list-defconfigs` 目標會到未隨附的 `configs/` 目錄尋找。請直接編輯 `.config`，或另存成 `defconfig_<名稱>` 再以 `DEFCONFIG=` 建置。

## IntelProCube 燒錄工具 { #flash-tool }

燒錄使用 IntelProCube v0.6.3 的命令列工具，未包含於 V2.2.0，請洽 INTELPRO。工具從自己的 `chips/` 目錄讀取晶片檔，請在 IntelProCube 目錄下執行。下表依 SDK 內的 README 與腳本整理，完整選項以工具本身為準。

| 選項 | 說明 |
|---|---|
| `--chipname ipro7` | IPRO7／IPRO7AI（Reef）。IPRO6S（例如 FIN 卡）用 `--chipname ipro6` |
| `--chip-variant IPRO7AI` | Flash 腳位設定：IPRO7AI（Reef、QFN56）用 `IPRO7AI`（`0x9`），IPRO7 EVB 用 `IPRO7`（`0x2`）。工具會把它寫入自己的 `chips/ipro7/eflash_loader/eflash_loader_cfg.ini`，換板子時務必重新指定 |
| `--port` | 序列埠：USB 轉 UART 線，或 IPRO Debug Probe 名稱以 `02` 結尾的埠 |
| `--baudrate 921600` | 燒錄鮑率，與應用的主控台鮑率無關 |
| `--firmware` | 要燒錄的 `.bin` |
| `--pt` | 分割表（`.toml`）：工具目錄下的相對路徑（例如 `chips/ipro7/partition/partition_cfg_2M.toml`）或完整路徑。未指定時使用工具的預設分割表 |
| `--boot2` | 一併燒錄 boot2 映像（例如工具內的 `chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin`）；`ipro_ble_remote` 的 Reef OTA 需要 |
| `--mfg` | 寫入 `mfg` 分割區的檔案（AI 模型、`ipro_reef_teach` 的模式與聲紋模型） |
| `--skip-ota` | 搭配應用自有的分割表使用，例如 `ipro_reef_teach` |
| `--build` | 只產生合併映像 `chips/ipro7/img_create_iot/whole_img.bin`，不燒錄；供 [`create_ota.py`](#ota-package) 使用 |

Reef 開箱韌體的燒錄（先讓板子[進入下載模式](debugging.md#download-mode)）：

```bash
cd <IntelProCube>
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 \
    --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

成功時輸出結尾有 `[All Success]`。工具即使失敗也以 0 結束，請以這行字判斷結果。Linux 用 `./ipro_iot_tool_linux`，Windows 用 `ipro_iot_tool.exe` 與 `COM5` 這類埠名。各 Reef 應用需要的分割表與 `--boot2`、`--mfg` 見 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)。

## serial_monitor.py { #serial-monitor }

```text
python3 tools/serial_monitor.py <序列埠> [--baud 115200] [--timeout 30]
                                [--send CMD] [--wait-for PATTERN] [--log FILE]
```

以 Python 標準函式庫的 termios 開啟序列埠，不需要 pyserial；可在 macOS 與 Linux 執行，Windows 不適用。它只讀取輸出（可在開始時送一行指令），不是互動式終端機；要逐行輸入指令，請用 `screen`、`minicom` 或其他序列埠終端程式。

| 選項 | 說明 | 預設值 |
|---|---|---|
| `--baud` | 鮑率；macOS 與 Linux 都可使用 921600、2000000 等高鮑率 | `115200` |
| `--timeout` | 監看秒數；`0` 表示執行到按下 Ctrl-C | `30` |
| `--send` | 開始監看前送出的一行指令，例如 `reboot`、`reboot_dl`、`reef selftest` | — |
| `--wait-for` | 正規表示式；比對成功即結束 | — |
| `--log` | 把原始輸出另存成檔案 | — |

| 結束碼 | 意義 |
|---|---|
| 0 | 比對成功，且符合的字串含 `PASSED` |
| 1 | 比對成功，但符合的字串不含 `PASSED` |
| 2 | 逾時，未比對到 |
| 3 | 無法開啟序列埠或送出指令 |
| 130 | 以 Ctrl-C 中止 |

```bash
# Reef 主控台（115200），送出自我檢查，10 秒後結束
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send "reef selftest" --timeout 10

# ipro7_jpeg_decode 的 Reef 設定（921600），持續監看並存檔
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 0 --log console.log

# 讓執行中的韌體重新開機進入下載模式（畫面出現 reboot to download mode）
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --send reboot_dl --timeout 2
```

macOS 請使用 `/dev/cu.*`，`/dev/tty.*` 會等待載波偵測而卡住。燒錄前先結束監看，釋放序列埠。

## create_ota.py { #ota-package }

把 IntelProCube 產生的合併映像封裝成 boot2 OTA 套件：預設以 XZ 壓縮並輸出 `<輸入檔名>.xz.ota`，加 `--raw` 則不壓縮並輸出 `<輸入檔名>.ota`。輸入必須是以 `IPNP` 開頭、含開機表頭的合併映像（工具的 `chips/ipro7/img_create_iot/whole_img.bin`），不是 SDK 建置出的 `.bin`；格式不符時腳本會停止。

```text
python3 tools/create_ota.py <whole_img.bin> [--raw] [-o OUTPUT] [--hw-ver STR] [--fw-ver STR]
```

| 選項 | 說明 |
|---|---|
| `--raw` | 不壓縮 |
| `-o, --output` | 輸出檔案 |
| `--hw-ver` | 寫入表頭的硬體版本字串；請明確指定，不要依賴預設值 |
| `--fw-ver` | 寫入表頭的韌體版本字串（預設 `OTA_V1.0.0`） |
| `--sign-key`、`--product` 等簽章選項 | 需要未隨附的 `ota_products.py`，V2.2.0 無法使用 |

在 Reef 上，`ipro_ble_remote` 的 `make_reef_ota.sh` 會替您呼叫工具的 `--build` 與本腳本，見 [Reef 應用的主機端工具](#reef-tools)。OTA 的整體流程見 [OTA 更新](../guides/ota.md)。

## Reef 應用的主機端工具 { #reef-tools }

### 瀏覽器版影像 Teach：tools/teach_web { #teach-web }

不需安裝 IPRO AI Studio，在 Chrome 或 Edge 中替 Reef 的相機收集影像、訓練分類器並經 USB 部署。板子需燒錄 `ipro_reef_teach` 並處於 `image` 模式；主機需要 Python 3.8 以上。

<div class="ipro-steps" markdown>

1. **啟動網頁伺服器**

    ```bash
    python3 tools/teach_web/serve.py
    ```

    瀏覽器開啟 `http://localhost:8780`（預設瀏覽器不是 Chrome／Edge 時，把網址貼到其中之一）。

2. **連接板子**：允許相機權限；按 **Connect…** 或第一次 **Deploy** 時，序列埠選 **IPRO7 UVC Cam**。

3. **離線電腦**：先在有網路時執行一次 `python3 tools/teach_web/serve.py --fetch-runtime`，下載約 22 MB 的 LiteRT.js 到本機。

</div>

### ipro_reef_teach 的 mfg 內容：mfg_payload.py { #mfg-payload }

第一次燒錄 `ipro_reef_teach` 時，`--mfg` 寫入的內容包含開機模式與聲紋模型：

```bash
python3 apps/ai/ipro_reef_teach/mfg_payload.py \
    --voice apps/ai/ipro_reef_teach/model/model_b.spkb --mode image -o reef_teach_mfg.bin
```

`--mode` 可為 `image`、`voice` 或 `sensor`。產生的 `reef_teach_mfg.bin` 以 `--mfg` 交給 IntelProCube，燒錄命令見[範例頁](../examples/ipro_reef_teach.md)；只更新韌體時不要帶 `--mfg`。

### ipro_ble_remote 的 Reef OTA 工具 { #reef-ota-tools }

| 工具 | 命令 | 結果 |
|---|---|---|
| `make_reef_ota.sh` | `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh` | 先建置 `DEFCONFIG=defconfig_reef`；產生 `build_reef/build_out/ipro_ble_remote_reef.xz.ota`（約 345 KB） |
| `reef_ota.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py <套件.xz.ota>` | 經 BLE（bleak）把套件傳給名為 `IPRO-Remote` 的板子，印出進度與狀態 |
| `reef_ble_test.py` | `.venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ble_test.py` | 以 bleak 當 central 測試 Reef 的 GATT 服務（`info led env sound tone img`；`keys`、`motion` 需要有人操作），拍到的 JPEG 存在腳本旁 |
| `ipro_remote_demo.apk` | 安裝到 Android 手機 | `ipro_ble_remote` 的示範 App，可推送 `.xz.ota` 套件 |

兩支 Python 腳本需要 bleak：`python3 -m venv .venv && .venv/bin/pip install bleak`。OTA 只適用於以 boot2 與 `partition_cfg_2M_remote_ab.toml` 燒錄過的板子；不要在 Reef 上以標準 `partition_cfg_2M.toml` 做 OTA。

### 其他 Reef 應用的工具 { #reef-app-tools }

| 工具 | 用途 |
|---|---|
| `apps/multimedia/ipro7_jpeg_decode/host/jpeg_check.py photo.jpg [--fix out.jpg]` | 在電腦上檢查 JPEG 能否在 IPRO7 上解碼，必要時轉檔 |
| `apps/multimedia/ipro7_jpeg_decode/host/jdec_host.py -p <埠> upload photo.jpg --go 565` | 經主控台把 JPEG 傳給板子解碼，並可取回結果比對 |
| `apps/multimedia/ipro7_jpeg_decode/host/run_host_tests.py` | 在電腦上以 libjpeg 對照驗證解碼器（需要 `cc`、`djpeg`） |
| `apps/multimedia/ipro_agora_sentino/setup_ncm_nat.sh` | macOS 上替 USB-NCM 連線設定 NAT |

## Zephyr 腳本 { #zephyr-tools }

`tools/zephyr/`（`bootstrap.sh`、`build.sh`、`flash.sh`、`monitor.sh`、`ci_build.sh`）服務 Zephyr 的 `ipro7_evb` 與 `ipro7ai_evk` 板型；本版沒有 Reef 的 Zephyr 板型。用法見 [Zephyr RTOS](../guides/zephyr.md)。

## 大小與記憶體分析 { #size-analysis }

| 方法 | 命令或位置 | 內容 |
|---|---|---|
| 連結器記憶體報告 | 每次建置的最後幾行（`build_freertos.sh` 寫入 `build.log`） | 各記憶體區段（`flash`、`ocram`，啟用時另有 `psram`）的使用量與百分比 |
| `size` 動作 | `./build_freertos.sh size <應用>` | text／data／bss 總計與各區段大小 |
| Map 檔 | `<建置目錄>/build_out/<應用>_IPRO7.map` | 每個目的檔與函式庫占用的位址與大小 |
| 符號排序 | `riscv64-unknown-elf-nm --size-sort -S <ELF>` | 依大小列出符號，找出最大的函式與變數 |
| 反組譯 | `.config` 設 `CONFIG_GENERATE_ASM=y` | 建置時另產生 `<應用>_IPRO7.asm` |

```bash
./build_freertos.sh size ipro7ai_reef_demo
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-nm --size-sort -S \
    apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf | tail -20
```

同時啟用 `CONFIG_AI_SUPPORT` 與 `CONFIG_MM_SUPPORT` 時，連結器腳本會把 OCRAM 區段縮為 64 KB（`CONFIG_EM_SIZE` 為 0）或 48 KB（`CONFIG_EM_SIZE` 大於 0），CMake 設定階段會印出 `AI+MM …: OCRAM=…`。記憶體位址配置見 [IPRO7](../hardware/chips/ipro7.md)，OCRAM 預算見[建置系統與設定](../guides/build-system.md)。

## 自動測試 { #automated-testing }

`./build_freertos.sh test ipro_unit_test` 會建置、燒錄並等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；`ipro_unit_test` 需要 IPRO7 EVB。Reef 的板上自我檢查是開箱韌體的 `reef selftest`，見[除錯與疑難排解](debugging.md#board-testing)。

## 其他工具 { #other-tools }

| 工具 | 說明 |
|---|---|
| `tools/script/parse_kconfig_dynamic.py Kconfig [PROJECT_SYMBOL]` | 把 Kconfig 樹輸出成 JSON；需要 kconfiglib。建置由 `cmake/generate_autoconf.cmake` 直接讀 `.config` 產生 `autoconf.h`，不使用此腳本 |
| `components/audio/tools/gen_asrc_coef.py` | 產生音訊取樣率轉換係數 |
| `*/test_host/run.sh` | 在電腦上執行的單元測試，例如 `components/audio/test_host/run.sh`、`apps/ai/ipro_reef_teach/sensor/test_host/run.sh` |
| 其他板子的工具 | IPRO7AI EVK 範例的 `flash.sh`、`enter_dl.py`，`ipro6_fmac` 的 `tools/mkimg.py`（IPRO6S EVK），`tools/android/IproMicDemo/`（`ipro_pdm_mic_demo`）：需要對應的板子 |

## 開發流程 { #dev-workflow }

在 Reef 上修改、建置、燒錄並檢查主控台的一輪循環，見[建置與燒錄流程](../tutorials/build-and-flash.md)；建立自己的應用見[建立第一個自己的應用](../tutorials/first-own-app.md)。除錯與常見錯誤見[除錯與疑難排解](debugging.md)。
