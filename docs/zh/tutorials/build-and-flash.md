---
title: "建置與燒錄流程"
description: 日常開發的建置、燒錄與監看迴圈：build_freertos.sh 串接動作、DEFCONFIG 替代設定、乾淨建置、讀取記憶體用量，以及腳本預設值的修正方式。
migrate_from:
  - "tutorials.html — 教學 2"
---

# 建置與燒錄流程

每天反覆執行的「修改 → 建置 → 燒錄 → 看主控台」迴圈，以 IPRO7AI Reef EVK 的開箱韌體 `ipro7ai_reef_demo` 為例。第一次安裝工具並燒錄，請先完成[第一個 FreeRTOS 應用](../get-started/first-app-freertos.md)與[燒錄與序列埠](../get-started/flash-and-monitor.md)。

## 前置需求 { #prerequisites }

- 已完成第一個 FreeRTOS 應用：工具鏈位於 `/opt/toolchain/riscv_ipro7/`，`make` 能建置 SDK 應用。
- IntelProCube v0.6.3 的命令列燒錄工具，需另行取得。把 `IPRO_FLASH_TOOL` 設為工具路徑，或把工具目錄加入 `PATH`。
- IPRO7AI Reef EVK 已上電，USB 轉 UART 線接 U6。
- 以下命令都在 SDK 根目錄執行。

## 步驟 { #steps }

<div class="ipro-steps" markdown>

1. **設定序列埠**：`build_freertos.sh` 依序使用 `-p` 參數、環境變數 `IPRO_SERIAL_PORT`，或系統上唯一的 USB 序列埠。接了多塊板子時請明確指定：

    === "macOS"

        ```bash
        export IPRO_SERIAL_PORT=/dev/cu.usbserial-XXXX
        ```

    === "Linux"

        ```bash
        export IPRO_SERIAL_PORT=/dev/ttyUSB0
        ```

2. **找出專案名稱**：

    ```bash
    ./build_freertos.sh -l
    ```

    輸出依分類列出專案（節錄）：

    ```text
    bluetooth/ble
      ipro_ble_hid_keyboard
      ipro_ble_remote
      ipro_ble_transparent
      ipro_throughput_test

    platform
      ...
      ipro7ai_reef_demo                   IPRO7AI Reef carrier board demo.
    ```

    名稱右側的說明取自 `.config` 第一行註解，多數專案沒有。腳本接受專案名稱（`ipro7ai_reef_demo`）或分類路徑（`platform/ipro7ai_reef_demo`）；`make -C` 則需要完整路徑 `apps/platform/ipro7ai_reef_demo`。

3. **建置並檢查記憶體用量**：

    ```bash
    ./build_freertos.sh build ipro7ai_reef_demo
    ```

    ```text
    ✓ Build succeeded (12s)
      Binary: <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin (219 KB)
      Log: <SDK>/apps/platform/ipro7ai_reef_demo/build/build.log
    ```

    完整建置輸出寫在 `build.log`。查看連結器的記憶體用量表（說明見[讀取記憶體用量](#memory-usage)）：

    ```bash
    grep -A5 "Memory region" apps/platform/ipro7ai_reef_demo/build/build.log
    ```

4. **燒錄**：讓 Reef 進入下載模式（在主控台輸入 `reboot_dl`，或按住 SW1、按一下 SW2 再放開 SW1），再於 IntelProCube 目錄下執行（macOS 為例，Linux 與 Windows 的命令見[燒錄與序列埠](../get-started/flash-and-monitor.md#flashing)）：

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    確認輸出中有 `[All Success]`；工具失敗時也會以 0 結束。Reef 不使用腳本的 `flash` 動作，原因見[腳本預設值](#script-defaults)。

5. **看主控台**：

    ```bash
    ./build_freertos.sh monitor -t 0 ipro7ai_reef_demo
    ```

    `monitor` 會先送出 `reboot`，所以板子會重新開機，從頭顯示開機訊息；`-t 0` 表示一直顯示到按 Ctrl+C。這個視窗只顯示輸出，要輸入 shell 指令請用序列埠終端程式（見[燒錄與序列埠](../get-started/flash-and-monitor.md)）。

6. **修改後重來**：改完程式只需重複步驟 3 到 5。串接的動作依序執行，任一動作失敗就停止：

    ```bash
    ./build_freertos.sh build size ipro7ai_reef_demo
    ```

</div>

## 確認結果 { #verify }

- `build` 印出 `✓ Build succeeded` 與 `Binary:` 路徑；`build.log` 中有記憶體用量表。
- 燒錄工具的輸出有 `[All Success]`。
- `monitor` 顯示新韌體的開機訊息。

## build_freertos.sh 動作與選項 { #actions }

用法：`./build_freertos.sh [動作...] [選項] <專案>`，未指定動作時執行 `build`。本教學用到 `build`、`monitor`、`size` 與 `clean` 四個動作，以及 `-d`（替代設定）、`-t 0`（`monitor` 持續到按 Ctrl+C）與 `-p`（序列埠）。動作依序執行，任一動作失敗就停止；指定多個動作時，最後會列出每個動作的結果。所有動作與選項見[工具命令列](../reference/tools.md#build-cli)。

## 替代設定與建置目錄 { #variants }

每個應用以自己目錄下的 `.config` 建置。替代設定以 `DEFCONFIG=` 或 `build_freertos.sh -d` 選用，建置在 `build_<名稱>/`，`.config` 不受影響：

```bash
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s   # 建置於 build_wifi_ipro6s/
./build_freertos.sh build -d defconfig_wifi_ipro6s ipro7ai_reef_demo       # 同上
```

- 每次建置都會把替代設定複製成 `build_<名稱>/.config`，要改設定時請改應用目錄中的原檔，不要改建置目錄中的複本。
- 目錄命名規則、`BOARD=`，以及以複製覆蓋 `.config` 的設定檔（`ipro_le_audio_headset` 的 `DAC.config`、`UAC.config`）見[建置系統與設定](../guides/build-system.md#variants)；各應用附有哪些替代設定見[範例](../examples/index.md)。

## 乾淨建置 { #clean-build }

修改 `.config` 或替代設定之後，尤其是 Flash 大小、PSRAM、`CONFIG_EM_SIZE`、控制器函式庫或 AI 相關選項，請做一次乾淨建置；用複製的方式切換 `.config` 之後也一樣。`clean` 只刪除對應的建置目錄：

```bash
# 預設設定：刪除 build/
make -C apps/platform/ipro7ai_reef_demo clean
# 替代設定：刪除 build_wifi_ipro6s/
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s clean
# 用腳本一次完成清除與重建
./build_freertos.sh clean build -d defconfig_wifi_ipro6s ipro7ai_reef_demo
```

每次建置都會把 `compile_commands.json` 複製到 SDK 根目錄，供編輯器的程式碼索引使用。

## 讀取記憶體用量 { #memory-usage }

連結時會印出各記憶體區域的用量。下面是 `ipro7ai_reef_demo` 預設設定的結果：

```text
Memory region         Used Size  Region Size  %age Used
           flash:      224792 B         1 MB     21.44%
           psram:       36064 B         8 MB      0.43%
           ocram:       31248 B       256 KB     11.92%
          hbnram:        2460 B         4 KB     60.06%
```

- `flash` 是整顆 Flash 的連結上限（預設 1 MB），不是分割表中韌體分割區的大小；`flash` 百分比沒有超過，不代表放得進韌體分割區。請把 `Binary:` 顯示的 `.bin` 大小與燒錄時所用分割表的韌體分割區比較。
- `ocram` 是 256 KB 減去 `CONFIG_EM_SIZE`。例如 `ipro_throughput_test` 的 Reef 設定使用 `CONFIG_EM_SIZE=32`，`ocram` 區域是 224 KB，用掉其中 205 KB。各區域的大小由哪些設定決定，見[建置系統與設定](../guides/build-system.md#memory-layout)。
- 建置設定階段也會印出採用的配置，例如 `-- IPRO7 flash: 1M (default, on-chip)` 與 `-- AI disabled: OCRAM=256KB`。
- 用 `make` 建置時，表格直接顯示在終端機；用 `build_freertos.sh` 時寫在 `build.log`，加 `-v` 才會顯示在畫面上。`size` 動作另外列出各區段的大小。

## 腳本預設值 { #script-defaults }

`build_freertos.sh` 的 `flash` 與 `monitor` 使用固定參數：`flash` 以 115200 baud 送出 `reboot_dl`，燒錄時只傳 `--chipname ipro7 --port --firmware --baudrate 921600`，不帶 `--chip-variant`、`--pt` 與 `--boot2`；`monitor` 固定以 115200 baud 開啟，並先送出 `reboot`。因此：

- 在 Reef 上依[步驟 4](#steps) 直接執行燒錄工具；板上韌體收不到 `reboot_dl` 時，按住 SW1、按一下 SW2、放開 SW1 進入下載模式。
- 主控台為 921600 baud 的應用（見[範例](../examples/index.md)的「主控台」欄）改用 `python3 tools/serial_monitor.py <序列埠> --baud 921600 --timeout 0`。
- 把 `monitor` 放在最後一個動作：逾時或按 Ctrl+C 結束時，腳本會把它記為失敗並停止後面的動作。

完整說明見[燒錄與序列埠](../get-started/flash-and-monitor.md#build-script)。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| `Project '…' not found. Did you mean:` | 名稱不完整 | 使用 `-l` 列出的完整名稱 |
| `Multiple projects match` | 多個分類有同名專案 | 改用分類路徑，例如 `platform/ipro7ai_reef_demo` |
| `Several serial ports, pass -p PORT or set IPRO_SERIAL_PORT` | 接了多個 USB 序列埠 | 加 `-p`，或設定 `IPRO_SERIAL_PORT` |
| `Flash tool not found` | 找不到 IntelProCube 命令列工具 | 設定 `IPRO_FLASH_TOOL`，或把工具目錄加入 `PATH` |
| 以 `-d` 建置後，另一次執行的 `flash` 或 `size` 回報 `Binary not found` 或 `ELF not found` | 沒有帶 `-d` 時，腳本找的是 `build/` | 再次執行時加上相同的 `-d` |
| `No cmake found` | 系統沒有 CMake；SDK 隨附的 `tools/cmake/` 是 Linux x86-64 版 | 安裝 3.19 以上版本的 CMake |
| 燒錄工具輸出沒有 `[All Success]` | 未進入下載模式，或 `--chip-variant` 不符 | 重新進入下載模式；Reef 與 IPRO7AI EVK 用 `IPRO7AI` |
| 主控台亂碼 | 鮑率不符 | 依應用的 `CONFIG_PLATFORM_UART_BAUDRATE`（未設定時為 115200） |

## 下一步 { #next-steps }

- [建置系統與設定](../guides/build-system.md)：`.config` 鍵值、建立新應用與連結腳本。
- [第一個 BLE 應用](first-ble-app.md)：用同一套迴圈修改 BLE 應用。
- [工具命令列](../reference/tools.md)：燒錄工具與序列埠工具的完整選項。
