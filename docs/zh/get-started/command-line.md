---
title: "macOS／Linux 命令列"
description: 在 macOS 或 Linux 上以 make 與 build_freertos.sh 建置、清除、燒錄與監看 FreeRTOS 應用的完整參考，範例以 IPRO7AI Reef EVK 為準。
migrate_from:
  - "getting-started.html#installation"
  - "getting-started.html#directory-structure"
  - "tools-debugging.html#macos-notes"
---

# macOS／Linux 命令列

在 macOS 或 Linux 上，FreeRTOS 應用以 `make -C` 建置，或以 `build_freertos.sh` 把建置、燒錄、監看串成一行。本頁是兩者的完整參考：建置目錄與產出、替代設定、清除，以及 `build_freertos.sh` 的動作、選項、環境變數與限制，範例都以 IPRO7AI Reef EVK 為準。工具的安裝見[準備開發環境](environment.md)。

## 前置需求 { #prerequisites }

- 已完成[準備開發環境](environment.md)：工具鏈、CMake、make、Python 與 IntelProCube。
- 以下命令都在 SDK 根目錄執行。
- 要燒錄時，板子已依[設定開關與接線](first-app-freertos.md#connect)接好。

## 目錄結構 { #directory-structure }

| 路徑 | 內容 |
|---|---|
| `apps/<分類>/<應用>/` | 應用：`.config`、替代設定 `defconfig_*`、`CMakeLists.txt`、`Makefile`、原始碼；分類為 `ai`、`bluetooth`、`multimedia`、`platform`、`test` |
| `bsp/` | 板級設定與連結腳本、SoC 驅動程式、HAL |
| `components/` | FreeRTOS、BLE、網路、音訊、AI、USB、檔案系統等元件；部分為預先建置的函式庫 |
| `cmake/` | 工具鏈與建置巨集 |
| `tools/` | `serial_monitor.py`、`create_ota.py`、`teach_web/`、`zephyr/`、隨附的 CMake（Linux x86-64） |
| `zephyr/` | Zephyr 模組（IPRO7 EVB 與 IPRO7AI EVK 板型） |
| `build_freertos.sh`、`project.build`、`VERSION.txt` | 建置前端、make 與 CMake 的銜接、版本資訊 |

各元件的說明見[系統架構](../guides/architecture.md)。

## 以 make 建置 { #make }

```bash
make -C apps/<分類>/<應用>                            # 以 .config 建置，輸出於 build/
make -C apps/<分類>/<應用> DEFCONFIG=defconfig_<名稱>  # 以替代設定建置，輸出於 build_<名稱>/
```

- **建置目錄**：`DEFCONFIG=` 的建置目錄是 `build_` 加上檔名去掉 `defconfig_` 的部分，例如 `defconfig_reef` → `build_reef/`、`defconfig_wifi_ipro6s` → `build_wifi_ipro6s/`。替代設定會被複製成 `build_<名稱>/.config`，應用目錄的 `.config` 不受影響；要改設定請改應用目錄中的原檔。
- **產出**：`<建置目錄>/build_out/<應用>_IPRO7.bin`（燒錄用）、`.elf`（含除錯符號）、`.map`（記憶體配置）；`<建置目錄>/include/generated/autoconf.h` 是由設定檔產生的巨集。每次建置也會把 `compile_commands.json` 複製到 SDK 根目錄，供編輯器的程式碼索引使用。
- **工具鏈**：`make -C … CROSS_COMPILE=<目錄>/bin/riscv64-unknown-elf-` 或同名環境變數會覆寫 `.config` 的 `CONFIG_CROSS_COMPILE`。
- **平行建置**：內部的 CMake 建置固定以 `-j4` 執行。
- **`BOARD=`**：只有 `ipro_agora_sentino`（預設 `reef`）與 `ipro_pdm_mic_demo` 使用；其他應用以 `DEFCONFIG=` 選板子。

建置 `ipro7ai_reef_demo` 時的輸出（節錄）：

```text
[INFO] Build Path: <SDK>/apps/platform/ipro7ai_reef_demo/build
CPU: intelpro_ipro7
...
-- [toolchain] Vendor toolchain detected - enabling xxldsp and mtune=intelpro-ipro7
-- Generated autoconf header: <SDK>/apps/platform/ipro7ai_reef_demo/build/include/generated/autoconf.h
...
-- [board] IPRO7AI Reef: CONFIG_IPRO7_XTAL_CAPCODE=95 (board default)
-- IPRO7 flash: 1M (default, on-chip)
-- AI disabled: OCRAM=256KB
...
Memory region         Used Size  Region Size  %age Used
           flash:      249944 B         1 MB     23.84%
           psram:       45376 B         8 MB      0.54%
           ocram:       32144 B       256 KB     12.26%
          hbnram:        2460 B         4 KB     60.06%
Generate <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
[100%] Built target ipro7ai_reef_demo_IPRO7.elf
```

`[board] IPRO7AI Reef` 一行表示這次建置的目標是 Reef。沒有這一行時，用的是其他板子的設定。

### Reef 的建置設定 { #reef-configs }

下列設定的目標是 Reef。表中標示 `DEFCONFIG=` 的應用，直接 `make` 建置的是其他板子的 `.config`。

| 應用 | 建置命令 | 建置目錄 | 主控台 |
|---|---|---|---|
| `ipro7ai_reef_demo` | `make -C apps/platform/ipro7ai_reef_demo` | `build/` | 115200 |
| `ipro7ai_reef_demo`＋Wi-Fi | `make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s` | `build_wifi_ipro6s/` | 115200 |
| `ipro_reef_teach` | `make -C apps/ai/ipro_reef_teach` | `build/` | 115200 |
| `ipro_ble_remote` | `make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_throughput_test` | `make -C apps/bluetooth/ble/ipro_throughput_test DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_le_audio_headset` | `make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro7_uvc_cam` 網路攝影機 | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640` | `build_reef_ov5640/` | 115200 |
| `ipro7_uvc_cam` 剪刀石頭布 | `make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps` | `build_reef_rps/` | 115200 |
| `ipro7_jpeg_decode` | `make -C apps/multimedia/ipro7_jpeg_decode DEFCONFIG=defconfig_reef` | `build_reef/` | 921600 |
| `ipro_ai_link` | `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` | `build_reef/` | 115200 |
| `ipro_agora_sentino` | `make -C apps/multimedia/ipro_agora_sentino` | `build/` | 115200 |

燒錄各應用時用哪個分割表、需不需要 boot2 或 `mfg` 資料，見[燒錄與序列埠：分割表](flash-and-monitor.md#partition-tables)。

## 清除 { #clean }

```bash
make -C apps/platform/ipro7ai_reef_demo clean                                   # 刪除 build/
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s clean   # 刪除 build_wifi_ipro6s/
```

`clean` 只刪除對應的建置目錄。修改 `.config` 或替代設定後，先清除再建置。

## build_freertos.sh { #build-script }

```text
./build_freertos.sh [動作...] [選項] <專案>
```

動作可以串接，依序執行，任一動作失敗就停止；指定多個動作時，最後列出每個動作的結果。沒有指定動作時執行 `build`。專案可寫名稱（`ipro7ai_reef_demo`）或 `apps/` 下的路徑（`platform/ipro7ai_reef_demo`）。

### 動作 { #actions }

| 動作 | 作用 |
|---|---|
| `build` | 執行 `make -C <應用> [DEFCONFIG=…]`。完整輸出寫入 `<建置目錄>/build.log`；成功時印出 `✓ Build succeeded`、`Binary:` 路徑與大小，失敗時印出記錄的最後 30 行 |
| `clean` | 執行 `make -C <應用> clean`，刪除建置目錄 |
| `flash` | 送出 `reboot_dl` 後以 IntelProCube 燒錄已建置的映像檔，見[燒錄與序列埠](flash-and-monitor.md#build-script) |
| `monitor` | 以應用的主控台鮑率開啟序列埠，先送出 `reboot`，讀取 `-t` 秒；只顯示輸出，不能輸入 |
| `size` | 以 `riscv64-unknown-elf-size` 印出 `.elf` 的總大小與各區段大小 |
| `test` | 建置、燒錄，送出 `reboot`，等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；結束碼 0 通過、1 失敗、2 逾時 |

### 選項 { #options }

| 選項 | 說明 |
|---|---|
| `-p`, `--port PORT` | 序列埠；預設為 `IPRO_SERIAL_PORT`，否則唯一接上的 USB 序列埠 |
| `-t`, `--timeout SEC` | `monitor` 與 `test` 的讀取秒數，預設 30；`0` 表示持續到按 ++ctrl+c++ |
| `-w`, `--wait-for PAT` | `monitor` 比對到這個正規表示式就結束；比對到的文字含 `PASSED` 才算成功 |
| `-d`, `--defconfig FILE` | 替代設定，建置於 `build_<名稱>/`；`flash`、`size` 也依它找映像檔 |
| `-c`, `--chip-variant V` | 燒錄的 `--chip-variant`；預設為 `IPRO_CHIP_VARIANT`，否則 IPRO7AI EVK 與 Reef 的設定用 `IPRO7AI`、其他用 `IPRO7` |
| `-P`, `--pt TABLE` | 燒錄的分割表：`.toml` 路徑，或工具 `chips/ipro7/partition/` 下的檔名；預設為 `IPRO_FLASH_PT`，否則不帶 `--pt` |
| `-j`, `--jobs N` | 外層 `make` 的平行數（內部建置固定 `-j4`） |
| `-v`, `--verbose` | 在畫面上顯示完整建置輸出 |
| `-l`, `--list` | 依分類列出所有專案 |
| `-h`, `--help` | 說明 |

### 環境變數 { #environment }

| 變數 | 作用 |
|---|---|
| `IPRO_FLASH_TOOL` | IntelProCube 命令列工具的路徑；未設定時找 PATH 上的 `ipro_iot_tool_macos`／`ipro_iot_tool_linux` |
| `IPRO_SERIAL_PORT` | 預設序列埠（`-p` 優先） |
| `IPRO_CHIP_VARIANT` | 預設的 `--chip-variant`（`-c` 優先） |
| `IPRO_FLASH_PT` | 預設的分割表（`-P` 優先） |
| `CROSS_COMPILE` | 傳給 `make`，覆寫 `.config` 的工具鏈前綴 |

### 列出專案 { #list }

```bash
./build_freertos.sh -l
```

依分類列出 `apps/` 下的專案，右側是 `.config` 第一行的說明（節錄）：

```text
ai
  ipro7ai_evk_person_detect           IPRO7AI EVK person detection: SC101IOT camera -> ISP -> NPU (YOLOv8) with
  ipro7ai_evk_rps                     IPRO7AI EVK rock-paper-scissors: SC101IOT camera -> ISP -> NPU classifier,
  ipro_reef_teach
  ipro_speaker_recog

bluetooth/ble
  ipro_ble_hid_keyboard
  ipro_ble_remote
  ipro_ble_transparent
  ipro_throughput_test
...
platform
  ...
  ipro7ai_reef_demo                   IPRO7AI Reef carrier board demo.
```

清單包含所有板子的應用；Reef 可用的是[上表](#reef-configs)的設定。

## Reef 範例 { #examples }

先設定一次環境變數（macOS 為例）：

```bash
export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
PT2M=<IntelProCube>/chips/ipro7/partition/partition_cfg_2M.toml
```

```bash
# 開箱韌體：建置、燒錄、看 30 秒開機訊息
./build_freertos.sh -P $PT2M build flash monitor ipro7ai_reef_demo

# 乾淨重建 Wi-Fi 版本
./build_freertos.sh -d defconfig_wifi_ipro6s clean build ipro7ai_reef_demo

# USB 網路攝影機：建置並燒錄
./build_freertos.sh -d defconfig_reef_ov5640 -P $PT2M build flash ipro7_uvc_cam

# 921600 baud 的應用：monitor 自動使用設定檔的鮑率
./build_freertos.sh -d defconfig_reef build flash monitor ipro7_jpeg_decode

# 只建置（首次燒錄需要 boot2，請直接執行工具）
./build_freertos.sh -d defconfig_reef build size ipro_ble_remote
```

`build` 成功時的輸出：

```text
Project: ipro_ble_remote  (bluetooth/ble/ipro_ble_remote)
Defconfig: defconfig_reef

→ Building ipro_ble_remote...
✓ Build succeeded (19s)
  Binary: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin (561 KB)
  Log: <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build.log
```

## 限制 { #limits }

- **只燒錄 IPRO7**：`flash` 固定傳 `--chipname ipro7`，不能燒錄 IPRO6S 映像。
- **沒有 `--boot2`、`--mfg`、`--skip-ota`**：`ipro_ble_remote` 的首次燒錄與 `ipro_reef_teach` 的 `mfg` 資料請直接執行 IntelProCube，見[燒錄與序列埠](flash-and-monitor.md#boot2-ab)。
- **工具在目前目錄執行**：`-P` 請給 `.toml` 的完整路徑。
- **`reboot_dl` 需要 shell**：板上韌體沒有 shell 或當掉時，先以按鍵進入下載模式。
- **`monitor` 不是互動式終端**：要輸入指令請用終端程式，見[互動式終端程式](flash-and-monitor.md#terminal)。逾時（結束碼 2）或比對到不含 `PASSED` 的文字（結束碼 1）都會被記為失敗並停止後面的動作，請把 `monitor` 放在最後。
- **`size` 使用預設路徑的工具鏈**：固定呼叫 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size`。
- **沒有 `BOARD=` 選項**：以 `-d` 選替代設定。
- **只支援 macOS 與 Linux**：腳本需要 bash，序列埠自動偵測只認得 `/dev/*` 名稱。

## 確認結果 { #verify }

```bash
./build_freertos.sh -l                      # 列出專案
./build_freertos.sh ipro7ai_reef_demo       # 印出 ✓ Build succeeded 與 Binary: 路徑
ls apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

## macOS 注意事項 { #macos-notes }

- 序列埠使用 `/dev/cu.*`（例如 `/dev/cu.usbserial-XXXX`），不要用 `/dev/tty.*`：後者會等待 carrier detect 訊號而卡住。
- `tools/cmake/` 隨附的 CMake 是 Linux 執行檔；建置優先使用 PATH 上的 `cmake`，因此 macOS 上安裝 Homebrew 的 CMake 即可。
- `tools/serial_monitor.py` 只使用 Python 標準函式庫（termios），不需 pyserial；921600 等高鮑率在 macOS 上由腳本另行設定，可直接使用。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| `✗ Project '…' not found. Did you mean:` | 名稱不完整 | 用 `-l` 列出的完整名稱 |
| `✗ Multiple projects match '…':` | 多個分類有同名專案 | 改用路徑，例如 `platform/ipro7ai_reef_demo` |
| `✗ Build failed`，最後 30 行有 `No cmake found` | PATH 上沒有 `cmake` | 安裝 CMake 3.15 以上 |
| 建置記錄中找不到 `riscv64-unknown-elf-gcc` | 工具鏈不在 `/opt/toolchain/riscv_ipro7/` | 設定 `CROSS_COMPILE` |
| 建置輸出沒有 `[board] IPRO7AI Reef` | 用的是其他板子的設定 | 依[Reef 的建置設定](#reef-configs)加上 `DEFCONFIG=` 或 `-d` |
| 以 `-d` 建置後，`flash` 或 `size` 回報 `Binary not found` 或 `ELF not found` | 沒有帶 `-d` 時，腳本找的是 `build/` | 加上相同的 `-d` |
| `✗ Flash tool not found: ipro_iot_tool_macos` | 找不到 IntelProCube | 設定 `IPRO_FLASH_TOOL` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 接了多個 USB 序列埠 | 以 `-p` 或 `IPRO_SERIAL_PORT` 指定 |
| `size` 失敗，找不到 `riscv64-unknown-elf-size` | 工具鏈不在預設路徑 | 直接執行 `<工具鏈目錄>/bin/riscv64-unknown-elf-size <elf>` |

## 下一步 { #next-steps }

- [第一個 FreeRTOS 應用](first-app-freertos.md)：在 Reef 上建置、燒錄並執行 `ipro7ai_reef_demo`。
- [建置與燒錄流程](../tutorials/build-and-flash.md)：日常的修改、建置、燒錄與監看迴圈。
- [建置系統與設定](../guides/build-system.md)：`.config` 鍵值、連結腳本與記憶體配置。
