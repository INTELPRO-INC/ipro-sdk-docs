---
title: "macOS／Linux 命令列"
description: 在 macOS 或 Linux 上安裝工具鏈與建置工具、解壓 SDK V2.1.0，並確認可以建置。
migrate_from:
  - "getting-started.html#installation"
  - "getting-started.html#directory-structure"
  - "tools-debugging.html#macos-notes"
---

# macOS／Linux 命令列

在 macOS 或 Linux 上安裝工具鏈與建置工具、解壓 SDK V2.1.0，並以 `build_freertos.sh` 建置一個應用，確認環境可用。

## 前置需求 { #prerequisites }

| 工具 | 需求 | 取得方式 |
|---|---|---|
| RISC-V 工具鏈 | `riscv64-unknown-elf-gcc`，預設位於 `/opt/toolchain/riscv_ipro7/bin/` | 未包含於 V2.1.0，請洽 INTELPRO |
| CMake | 3.19 以上；Zephyr 需 3.20 以上 | 系統套件管理工具 |
| GNU Make | FreeRTOS 應用以 Unix Makefiles 建置 | 系統套件管理工具 |
| Python | 3.8 以上 | 系統套件管理工具 |
| git | 建立 Zephyr 工作區時需要 | 系統套件管理工具 |
| IntelProCube v0.6.3 命令列工具 | `ipro_iot_tool_macos` 或 `ipro_iot_tool_linux` | 未包含於 V2.1.0，請洽 INTELPRO |

SDK 的 `tools/cmake/` 隨附 Linux x86-64 版 CMake 3.15，版本低於上表要求，在 macOS 上也無法執行；請安裝系統的 CMake。

## 安裝 { #installation }

<div class="ipro-steps" markdown>

1. **安裝建置工具**

    === "macOS"

        ```bash
        xcode-select --install          # 提供 make
        brew install cmake python git
        ```

    === "Linux"

        ```bash
        sudo apt update
        sudo apt install -y cmake make python3 python3-venv git
        ```

        以 Debian／Ubuntu 為例；其他發行版請安裝對應的套件。`python3-venv` 供 Zephyr 工作區使用。

    確認版本：

    ```bash
    cmake --version     # 3.19 以上
    python3 --version   # 3.8 以上
    ```

2. **安裝工具鏈**：將 INTELPRO 提供的工具鏈放在 `/opt/toolchain/riscv_ipro7/`，並確認可以執行。

    ```bash
    /opt/toolchain/riscv_ipro7/bin/riscv64-unknown-elf-gcc --version
    ```

    放在其他路徑時，建置前設定 `CROSS_COMPILE`（編譯器前綴，含最後的連字號）：

    ```bash
    export CROSS_COMPILE=<工具鏈目錄>/bin/riscv64-unknown-elf-
    ```

3. **校驗並解壓 SDK**

    ```bash
    shasum -a 256 -c IPRO-SDK-V2.1.0.tar.gz.sha256   # Linux 也可用 sha256sum -c
    tar xzf IPRO-SDK-V2.1.0.tar.gz
    cd IPRO-SDK-V2.1.0
    cat VERSION.txt
    ```

    校驗應顯示 `IPRO-SDK-V2.1.0.tar.gz: OK`，`VERSION.txt` 應顯示 `IPRO-SDK-V2.1.0`。

4. **指定燒錄工具**：將 `IPRO_FLASH_TOOL` 設為 IntelProCube 命令列工具的路徑，或將 IntelProCube 目錄加入 `PATH`。`build_freertos.sh`、各應用的 `flash.sh` 與 Zephyr 的 `west flash` 都依此尋找工具。

    === "macOS"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos
        ```

    === "Linux"

        ```bash
        export IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux
        ```

    也可將 `IPRO_SERIAL_PORT` 設為板子的序列埠；只接一個 USB 序列埠時，腳本會自動選用。

</div>

## 目錄結構 { #directory-structure }

解壓後的根目錄含 `apps/`（各應用一個目錄）、`bsp/`、`components/`、`cmake/`、`tools/`、`zephyr/`，以及 `build_freertos.sh`、`project.build`、`west.yml` 與 `VERSION.txt`。各目錄的內容見[系統架構](../guides/architecture.md#directory)。

FreeRTOS 應用的產出位於 `apps/<分類>/<應用>/build/build_out/`，檔名為 `<應用>_IPRO7.bin`、`.elf` 與 `.map`。

## 確認結果 { #verify }

在 SDK 根目錄列出所有應用：

```bash
./build_freertos.sh -l
```

應用依分類列出，例如 `platform` 下的 `ipro7ai_reef_demo`。接著建置一個應用，確認工具鏈與 CMake 可用：

```bash
./build_freertos.sh ipro7ai_reef_demo
```

成功時顯示 `Build succeeded`，以及 `Binary:` 後的 `.bin` 路徑；完整記錄在應用目錄的 `build/build.log`。

## macOS 注意事項 { #macos-notes }

- 序列埠使用 `/dev/cu.*`（例如 `/dev/cu.usbserial-XXXX`），不要用 `/dev/tty.*`：後者會等待 carrier detect 訊號而卡住。
- `tools/cmake/` 的 CMake 是 Linux 執行檔；`project.build` 優先使用 PATH 上的 `cmake`，因此 macOS 上只要安裝系統 CMake 即可。
- `tools/serial_monitor.py` 只使用 Python 標準函式庫（termios），不需 pyserial；921600、2000000 等鮑率在 macOS 上由腳本另行設定，可直接使用。

## 疑難排解 { #troubleshooting }

| 現象 | 原因 | 處理 |
|---|---|---|
| `No cmake found`，或 macOS 上執行 `tools/cmake/bin/cmake` 失敗 | PATH 上沒有 `cmake`，建置改用隨附的 Linux CMake | 安裝 CMake 3.19 以上並加入 PATH |
| 找不到 `riscv64-unknown-elf-gcc` | 工具鏈不在 `/opt/toolchain/riscv_ipro7/` | 設定 `CROSS_COMPILE` 指向工具鏈前綴 |
| `Project '…' not found` | 應用名稱不符 | 以 `./build_freertos.sh -l` 查看名稱；也可用 `apps/` 下的路徑，例如 `platform/ipro7ai_reef_demo` |
| `Flash tool not found` | 未設定 `IPRO_FLASH_TOOL`，PATH 上也找不到工具 | 依[安裝](#installation)第 4 步設定 |
| 序列埠卡住、沒有輸出 | macOS 上使用了 `/dev/tty.*` | 改用 `/dev/cu.*` |

## 下一步 { #next-steps }

- [第一個 FreeRTOS 應用](first-app-freertos.md)：在 Reef EVK 上建置、燒錄並執行 `ipro7ai_reef_demo`。
- [第一個 Zephyr 應用](first-app-zephyr.md)：建立 Zephyr 工作區並燒錄 `hello_world`。
- [建置系統與設定](../guides/build-system.md)：`.config`、`DEFCONFIG=` 與替代設定。
