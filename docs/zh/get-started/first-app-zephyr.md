---
title: "第一個 Zephyr 應用"
description: 建立 Zephyr 工作區，在 IPRO7 EVB 或 IPRO7AI EVK 上建置並以 west flash 燒錄 hello_world。
migrate_from:
  - "getting-started.html#zephyr-quickstart"
  - "zephyr-rtos.html#setup"
  - "zephyr-rtos.html#build-flash"
---

# 第一個 Zephyr 應用

建立 Zephyr 工作區，為 IPRO7 EVB（`ipro7_evb`）或 IPRO7AI EVK（`ipro7ai_evk`）建置 Zephyr 的 `hello_world`，以 `west flash` 燒錄，並在主控台看到輸出。

!!! info "IPRO7AI Reef EVK"
    V2.1.0 沒有 IPRO7AI Reef EVK 的 Zephyr 板級定義。Reef 請使用 [FreeRTOS 應用](first-app-freertos.md)。

## 前置需求 { #prerequisites }

- macOS 或 Linux：`tools/zephyr/` 的腳本需要 bash。
- RISC-V 工具鏈，預設路徑 `/opt/toolchain/riscv_ipro7`：未包含於 V2.1.0，請洽 INTELPRO。
- Zephyr v4.4.0 的主機工具：CMake 3.20 以上、Python 3（含 venv）與 git，以及 Zephyr 要求的其他工具（如 Ninja、dtc），見 Zephyr 官方 [Getting Started Guide](https://docs.zephyrproject.org/latest/develop/getting_started/index.html)。
- 第一次建立工作區時可連上 GitHub。
- IntelProCube 命令列工具，以 `IPRO_FLASH_TOOL` 或 PATH 指定（見 [macOS／Linux 命令列](command-line.md#installation)）。
- 讓板子進入下載模式的方式，三選一：IPRO7 CMSIS-DAP probe、板上正在執行含 shell 的韌體，或手動操作。

## 建立工作區 { #setup }

<div class="ipro-steps" markdown>

1. **執行 bootstrap**：在 SDK 根目錄執行。腳本在 `zephyr-workspace/` 建立含 west 的 Python venv，下載 Zephyr v4.4.0 與 `west.yml` 列出的模組，套用 `zephyr/patches.yml` 的修補，並產生 `env.sh`。

    ```bash
    tools/zephyr/bootstrap.sh
    ```

    工具鏈不在預設路徑時，執行前設定 `IPRO_TOOLCHAIN=<工具鏈目錄>`；要把工作區放在其他位置時加上 `-w <目錄>`。完成時顯示 `[bootstrap] done.`。

2. **載入環境**：每個新的終端機都要執行一次。`env.sh` 設定 `ZEPHYR_BASE`、`CROSS_COMPILE`，並把 west 加入 PATH。

    ```bash
    source zephyr-workspace/env.sh
    cd zephyr-workspace
    ```

</div>

## 建置與燒錄 { #build-flash }

<div class="ipro-steps" markdown>

1. **建置**：在 `zephyr-workspace/` 執行。

    === "IPRO7 EVB"

        ```bash
        west build -b ipro7_evb zephyr/samples/hello_world
        ```

    === "IPRO7AI EVK"

        ```bash
        west build -b ipro7ai_evk zephyr/samples/hello_world
        ```

    映像檔為 `build/zephyr/zephyr.bin`。SDK 自己的範例位於上一層的 `zephyr/samples/`，例如：

    ```bash
    west build -b ipro7_evb ../zephyr/samples/periph_smoke -d build/smoke
    ```

2. **燒錄**：`west flash` 讓板子進入下載模式，再以 IntelProCube 命令列工具寫入映像檔。分割表取自工具目錄的 `chips/ipro7/partition/`：`ipro7_evb` 使用 `partition_cfg_2M.toml`，`ipro7ai_evk` 使用 `partition_cfg_1M_boot2.toml`。進入下載模式的方式由 `--boot` 決定：

    | `--boot` | 方式 | 板型預設 |
    |---|---|---|
    | `probe` | 經 IPRO7 CMSIS-DAP probe 控制 BOOT 與重置 | `ipro7_evb` |
    | `shell` | 在主控台送出 `reboot_dl`；板上須正在執行含 shell 的韌體 | `ipro7ai_evk` |
    | `manual` | 依提示手動進入下載模式後按 Enter（IPRO7AI EVK 的操作見板卡頁） | — |

    ```bash
    west flash                                   # 使用板型預設
    west flash -- --boot manual                  # 沒有 probe 時手動進入
    west flash -- --boot shell --port /dev/cu.usbserial-XXXX
    ```

    `--boot shell` 以 `--console-baud`（預設 2000000，即 Zephyr 主控台的鮑率）送出 `reboot_dl`；板上若是 FreeRTOS 應用，改成該應用的鮑率，例如 `--console-baud 115200`。序列埠以 `--port` 或 `IPRO_SERIAL_PORT` 指定，只接一個 USB 序列埠時自動選用。`west flash` 不帶 `--chip-variant`，工具沿用其 `flash_pin` 設定，見[燒錄工具](flash-and-monitor.md#flash-tool)。

3. **開啟主控台**：Zephyr 主控台在 UART0，鮑率 2000000。

    ```bash
    ../tools/zephyr/monitor.sh --port /dev/cu.usbserial-XXXX
    ```

    `monitor.sh` 以 `tools/serial_monitor.py` 持續讀取，按 ++ctrl+c++ 結束。

</div>

## 確認結果 { #verify }

重置板子後，主控台出現 Zephyr 的開機標語，接著是以 `Hello World!` 開頭並帶有板型名稱的一行。`ipro7_evb` 與 `ipro7ai_evk` 的映像預設包含 shell 與 `reboot_dl` 指令，之後可直接用 `west flash -- --boot shell` 重新燒錄。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| bootstrap 顯示 `could not create a venv with pip` | 缺少 Python venv | 安裝 `python3-venv` 或 `virtualenv` |
| `no ipro_iot_tool found` | 找不到燒錄工具 | 設定 `IPRO_FLASH_TOOL`，或將 IntelProCube 目錄加入 PATH |
| `several serial ports, pass --port or set IPRO_SERIAL_PORT` | 接了多個 USB 序列埠 | 以 `--port` 或 `IPRO_SERIAL_PORT` 指定 |
| `partition table not found` | 工具旁沒有 `chips/ipro7/partition/` | `IPRO_FLASH_TOOL` 須指向 IntelProCube 目錄內的工具 |
| `flashing failed (is the board in download mode? …)` | 板子沒有進入下載模式 | 沒有 probe 時改用 `--boot shell`（板上須有 shell）或 `--boot manual` |
| 燒錄成功但主控台沒有輸出 | 鮑率不是 2000000，或板子仍在下載模式 | 以 `monitor.sh` 開啟（預設 2000000）；按板上的重置鍵 |
| `tools/zephyr/flash.sh` 無法讓執行中的 Zephyr 映像進入下載模式 | 腳本以 115200 送出 `reboot_dl`，Zephyr 主控台是 2000000 | 改用 `west flash -- --boot shell` |
| 需要低功耗、顯示、相機、音訊 codec、USB、SD、Ethernet 或 NPU | 本版 Zephyr 尚未提供這些模式或驅動；IPRO7AI EVK 的 LCD 可透過 Zephyr 內建的 ST7789V 驅動使用 | 改用 FreeRTOS 應用 |

## 下一步 { #next-steps }

- [Zephyr RTOS](../guides/zephyr.md)：支援的驅動、SDK 範例、BLE 與 802.15.4。
- [燒錄與序列埠](flash-and-monitor.md)：燒錄工具參數與各板設定。
- [第一個 FreeRTOS 應用](first-app-freertos.md)
