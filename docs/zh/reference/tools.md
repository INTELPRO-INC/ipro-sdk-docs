---
title: "工具命令列"
description: SDK 隨附主機端工具的命令、選項與範例：build_freertos.sh、make、IntelProCube 燒錄工具、serial_monitor.py、create_ota.py、tools/zephyr 與大小分析。
migrate_from:
  - "tools-debugging.html#overview"
  - "tools-debugging.html#build-cli"
  - "tools-debugging.html#zephyr-tools"
  - "tools-debugging.html#automated-testing"
  - "tools-debugging.html#size-analysis"
  - "tools-debugging.html#dev-workflow"
---

# 工具命令列

SDK 隨附主機端工具的命令格式、選項與範例。逐步的燒錄與主控台操作見 [燒錄與序列埠](../get-started/flash-and-monitor.md)；需要選板子時，範例以 IPRO7AI Reef EVK 為準。

## 工具一覽 { #overview }

| 工具 | 路徑 | 用途 | V2.1.0 |
|---|---|---|---|
| `build_freertos.sh` | SDK 根目錄 | FreeRTOS 應用的建置、清除、燒錄、主控台、大小報告與自動測試 | 包含 |
| `make` ＋ `project.build` | 各應用的 `Makefile` | 建置單一應用 | 包含 |
| `serial_monitor.py` | `tools/` | 讀取主控台，可先送一行指令、等待指定字串並存檔（macOS、Linux） | 包含 |
| `create_ota.py` | `tools/` | 產生 boot2 OTA 套件 | 包含 |
| Zephyr 腳本 | `tools/zephyr/` | Zephyr 工作區、建置、燒錄、主控台與範例矩陣 | 包含 |
| `parse_kconfig_dynamic.py` | `tools/script/` | 把 Kconfig 樹匯出成 JSON（需要 kconfiglib，建置流程不使用） | 包含 |
| CMake 3.15 | `tools/cmake/` | 僅限 Linux x86-64，無法在 macOS 執行 | 包含 |
| Android 範例 App 原始碼 | `tools/android/IproMicDemo/` | 搭配 `ipro_pdm_mic_demo` 的 Android Studio 專案 | 包含 |
| IntelProCube v0.6.3 命令列燒錄工具 | `ipro_iot_tool_macos`、`ipro_iot_tool_linux`、`ipro_iot_tool.exe` | 經序列埠燒錄韌體 | 未包含於 V2.1.0，請洽 INTELPRO |
| RISC-V 工具鏈 | `/opt/toolchain/riscv_ipro7/` | 編譯（GCC，`riscv64-unknown-elf-`） | 未包含於 V2.1.0，請洽 INTELPRO |
| 板級自動測試腳本、當機位址解析工具、OpenOCD 設定 | — | — | 未包含於 V2.1.0，請洽 INTELPRO |

## 環境變數 { #environment }

| 變數 | 使用的工具 | 作用 |
|---|---|---|
| `IPRO_FLASH_TOOL` | `build_freertos.sh`、`tools/zephyr/flash.sh`、`west flash`、各應用 `flash.sh` | IntelProCube 命令列工具的路徑。未設定時在 `PATH` 中尋找本機作業系統對應的工具名稱 |
| `IPRO_SERIAL_PORT` | `build_freertos.sh`、`tools/zephyr/flash.sh`、`monitor.sh`、`west flash` | 預設序列埠。未設定且未指定 `-p`／`--port` 時，若系統上只有一個 USB 序列埠就自動使用它 |
| `IPRO_PROBE_PORT` | `west flash` | 除錯器 UART 橋接埠（接收進入下載模式的關鍵字），預設與 `--port` 相同 |
| `CROSS_COMPILE` | `make`、`build_freertos.sh build` | 工具鏈前綴；在環境中設定時優先於 `.config` 的 `CONFIG_CROSS_COMPILE` |
| `IPRO_TOOLCHAIN` | `tools/zephyr/bootstrap.sh` | Zephyr 工作區使用的工具鏈目錄，預設 `/opt/toolchain/riscv_ipro7` |
| `IPRO_ZEPHYR_WS` | `tools/zephyr/build.sh`、`ci_build.sh` | Zephyr 工作區位置，預設 `<SDK>/zephyr-workspace` |

## build_freertos.sh { #build-cli }

```text
./build_freertos.sh [動作...] [選項] <專案>
```

動作可串接，依序執行；任一動作失敗即停止。未指定動作時執行 `build`。

| 動作 | 說明 |
|---|---|
| `build` | 執行 `make -C <應用>`，記錄寫入 `<建置目錄>/build.log`，成功時印出 `.bin` 路徑與大小；失敗時印出記錄最後 30 行 |
| `clean` | 刪除建置目錄 |
| `flash` | 先經 `serial_monitor.py` 送出 `reboot_dl`（115200 baud），再以 IntelProCube 工具燒錄 `.bin`；以輸出中的 `[All Success]` 判定成功。不會先建置 |
| `monitor` | 以 `serial_monitor.py` 在 115200 baud 開啟主控台，先送出 `reboot`，`-t` 秒後結束 |
| `size` | 對 ELF 執行 `size` 與 `size -A`（列出前 30 行區段） |
| `test` | 建置、燒錄，再送出 `reboot` 並等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`；結束碼 0 通過、1 失敗、2 逾時 |

| 選項 | 說明 | 預設值 |
|---|---|---|
| `-p, --port PORT` | 序列埠 | `$IPRO_SERIAL_PORT`，否則唯一的 USB 序列埠 |
| `-t, --timeout SEC` | `monitor`、`test` 的秒數 | `30` |
| `-w, --wait-for PAT` | `monitor` 等待的正規表示式 | — |
| `-d, --defconfig FILE` | 改用應用目錄中的替代設定檔，建置至 `build_<名稱>/`（`defconfig_reef` → `build_reef/`） | — |
| `-j, --jobs N` | 平行建置工作數 | — |
| `-v, --verbose` | 顯示完整建置輸出 | — |
| `-l, --list` | 依分類列出 `apps/` 下所有專案 | — |
| `-h, --help` | 說明 | — |

`<專案>` 可寫應用名稱（`ipro7ai_reef_demo`），或 `apps/` 之下的路徑（`platform/ipro7ai_reef_demo`）。名稱不唯一或找不到時，會列出候選名稱。`-l` 的說明欄取自 `.config` 第一行註解，部分應用會顯示空白。

```bash
./build_freertos.sh -l                                  # 列出 35 個應用
./build_freertos.sh ipro7ai_reef_demo                   # 建置 Reef 開箱韌體
./build_freertos.sh clean build platform/ipro7ai_reef_demo
./build_freertos.sh -d defconfig_reef build ipro_ble_remote   # Reef 設定，輸出在 build_reef/
./build_freertos.sh size ipro7ai_reef_demo
```

產出位於 `<應用>/build/build_out/`（使用 `-d` 時為 `build_<名稱>/build_out/`）：`<應用>_IPRO7.bin`、`.elf`、`.map`。

!!! warning "flash、monitor 與 size 的固定設定"
    - `flash` 不傳 `--chip-variant` 與 `--pt`，`reboot_dl` 與 `monitor` 固定使用 115200 baud。IPRO7AI Reef EVK、IPRO7AI EVK、需要特定分割表或主控台為 921600 baud 的應用，請依[燒錄與序列埠](../get-started/flash-and-monitor.md#build-script)改用 IntelProCube 工具與 `serial_monitor.py`。
    - `size` 固定使用 `/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-size`，不讀取 `CROSS_COMPILE`。

## make 目標 { #make-targets }

每個應用的 `Makefile` 都轉呼叫 SDK 根目錄的 `project.build`（CMake 以 `Unix Makefiles` 產生器設定，再以 `make -j4` 建置）。

| 命令 | 說明 |
|---|---|
| `make -C apps/<分類>/<應用>` | 以 `.config` 建置至 `build/` |
| `make -C apps/<分類>/<應用> clean` | 刪除建置目錄 |
| `make -C apps/<分類>/<應用> DEFCONFIG=defconfig_<名稱>` | 以替代設定建置至 `build_<名稱>/`，不改動 `.config` |
| `make -C apps/multimedia/ipro_pdm_mic_demo BOARD=evk` | 僅 `ipro_pdm_mic_demo` 與 `ipro_agora_sentino` 支援 `BOARD=`：改用 `config_<板子>`，建置至 `build_config_<板子>/` |

- CMake：優先使用 `PATH` 上的 `cmake`，找不到才用 `tools/cmake/`（Linux x86-64）。
- 每次建置後，`compile_commands.json` 會複製到 SDK 根目錄，供編輯器使用。
- 部分 `Makefile` 中的 `defconfig`、`list-defconfigs` 與 `menuconfig` 目標依賴套件中沒有的檔案，無法使用；請直接編輯 `.config`。

## IntelProCube 燒錄工具 { #flash-tool }

燒錄使用 IntelProCube v0.6.3 的命令列工具，未包含於 V2.1.0，請洽 INTELPRO。下表依 SDK 內的 README 與燒錄腳本整理，完整選項以工具本身為準。在 IntelProCube 目錄下執行。

| 選項 | 說明 |
|---|---|
| `--chipname ipro7` | 晶片 |
| `--chip-variant IPRO7` 或 `IPRO7AI` | 板子的 Flash 腳位設定，寫入工具設定檔的 `flash_pin`：IPRO7 EVB 用 `IPRO7`（`0x2`）；IPRO7AI EVK 與 IPRO7AI Reef EVK 用 `IPRO7AI`（`0x9`）。之後沒指定時沿用上一次的值 |
| `--port` | 序列埠 |
| `--baudrate` | 燒錄鮑率；SDK 的應用 README 與腳本使用 `921600` |
| `--firmware` | 要燒錄的 `.bin` |
| `--pt` | 分割表（`.toml`），寫工具目錄下的相對路徑（例如 `chips/ipro7/partition/partition_cfg_2M.toml`）或完整路徑。未指定時寫入工具的預設分割表 |
| `--mfg` | 寫入 `mfg` 分割區的檔案（AI 模型），用法見 IPRO7AI EVK AI 範例的 `flash.sh` |
| `--build`、`--boot2` | 只產生合併映像 `chips/ipro7/img_create_iot/whole_img.bin`，供 [`create_ota.py`](#ota-package) 使用；用法見 `apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh` |

```bash
./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
    --port /dev/cu.usbserial-XXXX --baudrate 921600 \
    --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

工具即使失敗也以 0 結束，請以輸出中的 `[All Success]` 判斷結果。各作業系統的命令、各板設定與進入下載模式的方式見[燒錄與序列埠](../get-started/flash-and-monitor.md)。

## serial_monitor.py { #serial-monitor }

```text
python3 tools/serial_monitor.py <序列埠> [--baud 115200] [--timeout 30]
                                [--send CMD] [--wait-for PATTERN] [--log FILE]
```

以 Python 標準函式庫的 termios 開啟序列埠，不需要 pyserial；可在 macOS 與 Linux 執行，Windows 不適用。

| 選項 | 說明 | 預設值 |
|---|---|---|
| `--baud` | 鮑率；macOS 與 Linux 都可使用 921600、2000000 等高鮑率 | `115200` |
| `--timeout` | 監看秒數；`0` 表示執行到按下 Ctrl-C | `30` |
| `--send` | 開始監看前送出的一行指令，例如 `reboot`、`reboot_dl` | — |
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
# Reef 主控台（115200），持續監看到 Ctrl-C
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --timeout 0

# 主控台為 921600 的應用，並存檔
python3 tools/serial_monitor.py /dev/cu.usbserial-XXXX --baud 921600 --timeout 60 --log console.log

# 讓執行中的韌體重新開機進入下載模式
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
| `--sign-key`、`--product` 等簽章選項 | 需要套件中沒有的產品設定檔，V2.1.0 無法使用 |

```bash
python3 tools/create_ota.py <IntelProCube>/chips/ipro7/img_create_iot/whole_img.bin \
    -o ipro_ble_remote_reef.xz.ota --hw-ver <hw-version> --fw-ver 202610160900
```

OTA 的整體流程（Reef A/B 分割、BLE 傳送）見 [OTA 更新](../guides/ota.md)。

## Zephyr 腳本 { #zephyr-tools }

`tools/zephyr/` 的腳本支援 `ipro7_evb` 與 `ipro7ai_evk` 兩塊板子。完整流程見 [Zephyr RTOS](../guides/zephyr.md)。

| 腳本 | 命令 | 說明 |
|---|---|---|
| `bootstrap.sh` | `tools/zephyr/bootstrap.sh [-w DIR] [--full]` | 建立 `zephyr-workspace/`：Python venv 與 west、Zephyr v4.4.0 與 `west.yml` 列出的模組，套用 `zephyr/patches.yml`，產生 `env.sh`。`--full` 改為完整下載模組；工具鏈路徑取自 `IPRO_TOOLCHAIN` |
| `build.sh` | `tools/zephyr/build.sh [-b BOARD] [-d DIR] [-p] APP [-- CMAKE_ARGS]` | 建置 Zephyr 應用；`-b` 預設 `ipro7_evb`，`-p` 完整重建，`APP` 可為路徑或 `zephyr/samples/` 下的範例名稱。輸出 `<工作區>/build/<板子>/<應用>/zephyr/zephyr.bin` |
| `flash.sh` | `tools/zephyr/flash.sh [--port PORT] [--build-dir DIR | zephyr.bin]` | 以 IntelProCube 工具燒錄 `zephyr.bin`（921600 baud，不傳 `--pt`） |
| `monitor.sh` | `tools/zephyr/monitor.sh [--port PORT] [--baud 2000000] [--timeout S]` | 以 2000000 baud 開啟 UART0 主控台，預設執行到 Ctrl-C |
| `ci_build.sh` | `tools/zephyr/ci_build.sh [-b BOARD] [-q]` | 以完整重建、警告視為錯誤的方式建置範例矩陣並列出大小；`-q` 只建 hello_world 與 blinky。結果在 `<工作區>/build/ci/summary.md` |
| `merge_mcuboot.py` | `merge_mcuboot.py <sysbuild 建置目錄> [-o merged.bin] [--slot1 FILE]` | 把 MCUboot 與簽章後的應用合併成一個 FW 映像，再以 IntelProCube 燒錄 |
| `csl_pcap.py` | `csl_pcap.py FILE.pcap [--ts-end] [--dump]` | 分析 802.15.4 sniffer 擷取檔中的 CSL 時序 |

```bash
tools/zephyr/bootstrap.sh
source zephyr-workspace/env.sh
cd zephyr-workspace
west build -b ipro7_evb zephyr/samples/hello_world
west flash                    # 預設經 IPRO 除錯器進入下載模式；沒有除錯器時加 -- --boot manual
```

`west flash` 使用 SDK 的 `ipro` runner，選項接在 `--` 之後：

| 選項 | 說明 | 預設值 |
|---|---|---|
| `--boot probe|shell|manual` | 進入下載模式的方式：IPRO 除錯器（CMSIS-DAP）、執行中映像的 `reboot_dl`，或手動按 BOOT 與重置 | `probe`（`ipro7ai_evk` 為 `shell`） |
| `--port` | 燒錄序列埠 | `$IPRO_SERIAL_PORT` |
| `--probe-port` | 除錯器 UART 橋接埠 | `$IPRO_PROBE_PORT`，否則同 `--port` |
| `--tool` | IntelProCube 工具 | `$IPRO_FLASH_TOOL`，否則 `PATH` |
| `--pt` | 分割表 | `ipro7_evb`：`partition_cfg_2M.toml`；`ipro7ai_evk`：`partition_cfg_1M_boot2.toml` |
| `--baudrate` | 燒錄鮑率 | `2000000` |
| `--console-baud` | `--boot shell` 送 `reboot_dl` 的鮑率 | `2000000` |
| `--attempts` | 失敗重試次數 | `3` |
| `--tool-arg` | 額外傳給工具的參數（可重複） | — |
| `--no-reset` | 燒錄後停留在下載模式 | — |

!!! warning "已知的腳本限制"
    - `bootstrap.sh`、`build.sh`、`flash.sh` 與 `ci_build.sh` 的 `-h` 目前印不出用法，請以本頁為準。
    - `flash.sh` 以 115200 baud 送出 `reboot_dl`，執行中的 Zephyr 映像（主控台 2000000 baud）收不到；請改用 `west flash -- --boot shell`，或手動讓板子進入下載模式。
    - `ci_build.sh` 未指定 `-b` 時也會建置 `ipro6s_evb`，此版本不支援；請指定 `-b ipro7_evb` 或 `-b ipro7ai_evk`。
    - 此版本沒有 IPRO7AI Reef EVK 的 Zephyr 板級定義。

## 大小與記憶體分析 { #size-analysis }

| 方法 | 命令或位置 | 內容 |
|---|---|---|
| 連結器記憶體報告 | 每次建置的最後幾行（`build_freertos.sh` 寫入 `build.log`） | 各記憶體區段（`flash`、`ocram`，啟用時另有 `psram`）的使用量與百分比 |
| `size` 動作 | `./build_freertos.sh size <應用>` | text／data／bss 總計與各區段大小 |
| Map 檔 | `<應用>/build/build_out/<應用>_IPRO7.map` | 每個目的檔與函式庫占用的位址與大小 |
| 符號排序 | `riscv64-unknown-elf-nm --size-sort -S <ELF>` | 依大小列出符號，找出最大的函式與變數 |
| 反組譯 | `.config` 設 `CONFIG_GENERATE_ASM=y` | 建置時另產生 `<應用>_IPRO7.asm` |

```bash
./build_freertos.sh size ipro7ai_reef_demo
/opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-nm --size-sort -S \
    apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.elf | tail -20
```

同時啟用 `CONFIG_AI_SUPPORT` 與 `CONFIG_MM_SUPPORT` 時，連結器腳本會把 OCRAM 區段縮為 64 KB（`CONFIG_EM_SIZE` 為 0）或 48 KB（`CONFIG_EM_SIZE` 大於 0），因此 AI 與 BLE 難以放進同一個映像。記憶體位址配置見 [IPRO7](../hardware/chips/ipro7.md)，OCRAM 預算見 [建置系統與設定](../guides/build-system.md)。

## 自動測試 { #automated-testing }

```bash
./build_freertos.sh test ipro_unit_test -p /dev/cu.usbserial-XXXX -t 60
```

`test` 依序建置、燒錄，再送出 `reboot` 並等待 `ALL TESTS PASSED` 或 `SOME TESTS FAILED`。結束碼：0 通過、1 失敗、2 逾時。燒錄使用上述 `flash` 的固定設定，`ipro_unit_test` 的預設設定為 IPRO7 EVB。測試內容與板上指令見 [板上測試](debugging.md#board-testing)。

## 其他工具 { #other-tools }

| 工具 | 說明 |
|---|---|
| `tools/script/parse_kconfig_dynamic.py Kconfig [PROJECT_SYMBOL]` | 把 Kconfig 樹輸出成 JSON；需要 kconfiglib。建置由 `cmake/generate_autoconf.cmake` 直接讀 `.config` 產生 `autoconf.h`，不使用此腳本 |
| `apps/ai/ipro7ai_evk_person_detect/flash.sh`、`apps/ai/ipro7ai_evk_rps/flash.sh`、`apps/platform/ipro7ai_evk_launcher/flash.sh` | IPRO7AI EVK 的 AI 範例燒錄腳本（分割表、韌體與 `mfg` 模型） |
| `apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh`、`reef_ota.py` | 產生 Reef 的 OTA 套件，並經 BLE 傳送 |
| `apps/test/ipro_gh7007_video/tools/video_convert.py` | 把影片轉成 GH7007 面板播放格式 |
| `components/audio/tools/gen_asrc_coef.py` | 產生音訊取樣率轉換係數 |

## 開發流程 { #dev-workflow }

在 Reef 上修改、建置、燒錄並檢查主控台的一輪循環，見[建置與燒錄流程](../tutorials/build-and-flash.md)。

Zephyr 應用改用 `west build`／`west flash`（見 [Zephyr 腳本](#zephyr-tools)）。除錯與常見錯誤見 [除錯與疑難排解](debugging.md)。
