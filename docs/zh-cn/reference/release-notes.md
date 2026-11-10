---
title: "版本说明"
description: IPRO SDK 各正式版本的发布日期、新增内容、未包含项与已知限制，新版本在前。
migrate_from:
  - "changelog.html"
---

# 版本说明

IPRO SDK 的正式发布记录，新版本在前；当前版本为 V2.2.1。各版本的下载文件与发布说明在 [GitHub Releases](https://github.com/INTELPRO-INC/IPRO-SDK/releases)；SDK 软件包的总体说明见软件包根目录的 `README.md`。Windows 在线安装程序 Online Setup 的版本也列在本页（当前为 3.6.0），下载地址是 [ipro-sdk-releases](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/latest)。

## IPRO-SDK-V2.2.1 { #v2-2-1 }

<span class="ipro-badge">最新版本</span> 发布日期：2026-11-10 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.1)

V2.2.0 的修正版，应用与 V2.2.0 相同，共 40 个 FreeRTOS 应用。下载文件为 `IPRO-SDK-V2.2.1.tar.gz`，SHA-256 见 Release 页面。[V2.2.0](#v2-2-0) 的其余说明（包括已知问题）同样适用于 V2.2.1。

**修正**

- **IPRO6S soft-AP**：没有出厂 MAC 地址的芯片（例如 IPRO6S EVK）执行 `wifi_ap_start` 会失败，而且没有任何信息。现在 station 与 AP 每次启动共用同一个随机地址，AP 只翻转最低位。修正在 `ipro6_demo`（`defconfig_ipro6_lpwifi`）与 `ipro6_if_wifi`（`defconfig_ipro6_sdio`、`defconfig_ipro6_usb`）的预构建 `libipro_os_adapter.a` 中。操作步骤见 [IPRO6S](../hardware/chips/ipro6s.md#flashing)。
- **`ipro_ble_remote` 的 `make_reef_ota.sh`**：使用 IntelProCube 文件夹里最新的 boot2（0.7.0.1 为 v0.6.0），或 `IPRO_BOOT2` 指定的文件，不必再先修改脚本。
- **软件包 README**：改为从 GitHub 下载 IntelProCube 0.7.0.1，附下载与校验步骤，并加上 IPRO6S EVK 的烧录命令（`--chip-variant IPRO6S`、`partition_cfg_fw_direct.toml`）。
- **Zephyr**：`zephyr/subsys/net/ipro_wifi/net_al_zephyr.c` 改为匹配软件包内 lwIP 移植的 L2 socket 接口；IPRO6S 在 Zephyr 下仍不支持。

发布前从软件包构建并检查：36 个 IPRO7 FreeRTOS 应用、7 个 IPRO6S 配置与 Zephyr 示例。上板：IPRO6S EVK 扫描正常，soft-AP 可让电脑连接并获得 DHCP 地址（分别在 macOS 与 Windows 上构建与烧录）；IPRO7AI Reef EVK 通过 `reef selftest`。

### 已知问题 { #v2-2-1-known-issues }

- **IPRO Workbench 0.1.0 与 IPRO6S**：Workbench 烧录 IPRO6S 镜像时没有带入 IPRO6S 的分区表，板子无法启动。请按 [IPRO6S](../hardware/chips/ipro6s.md#flashing) 用 IntelProCube 命令行烧录。

## IPRO-SDK-V2.2.0 { #v2-2-0 }

发布日期：2026-11-03 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.2.0)

IPRO7／IPRO7AI 与 IPRO6S 双芯片版本，取代 V2.1.0。共 40 个 FreeRTOS 应用：37 个 IPRO7、3 个 IPRO6S。下载文件为 `IPRO-SDK-V2.2.0.tar.gz`，SHA-256 见 Release 页面。

**新增与变更**

- **IPRO6S 应用回归软件包**：`ipro6_demo`（Wi-Fi 6 station／soft-AP，DTIM 低功耗）、`ipro6_if_wifi`（通过 SDIO 或 USB 供主机使用的 Wi-Fi 桥接）与 `ipro6_fmac`（FullMAC 固件及其 Flash 加载程序）。Wi-Fi MAC、共存与 RF 库按每个随附的 `defconfig_*` 分别预编译，每个配置链接为它构建的库。Reef 的 FIN Wi-Fi 卡固件即 `ipro6_if_wifi` 的 `defconfig_ipro6_sdio`，见 [IPRO6S](../hardware/chips/ipro6s.md)。
- **新应用 `ipro_reef_teach`**：IPRO7AI Reef EVK 上的 Edge AI 固件，内含三个 Teach 工具：`image`（USB 摄像头与分类器）、`voice`（识别谁在说话）与 `sensor`（任意传感器）。启动时选定一个模式，每个模式有自己的 USB 标识，由 IPRO AI Studio 操作；也可用 `tools/teach_web/` 在浏览器中进行图像 Teach。IPRO AI Studio 可从 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载。
- **IPRO Edge AI 平台 V2.0**（`components/ai`）：运行环境、每个工具一个槽位的模型存储区、输入源、预处理与应用框架；NPU 等待设有上限，超时会复位该模块并进入安全的故障状态；Edge AI 固件会启用 AON 看门狗（进入下载模式时关闭）。修正 CPU 层图读取超出最后一条层记录的问题。
- **整芯片复位**：`hal_reboot_full()` 通过 AON 看门狗复位整颗芯片，包括 always-on 电源域；启用 `CONFIG_APP_WATCHDOG` 时，`platform_init()` 从启动之初就开启看门狗。`ipro_reef_teach` 用它切换工具，修正了 Reef 接着摄像头时，从 `image` 模式切出后下一次启动可能卡住直到复位的问题。
- **新应用 `ipro7_jpeg_decode`**：以软件（TJpgDec）把 JPEG 解码为 RGB565／RGB888，含格式检查，并可解码不带 Huffman 表的摄像头 MJPEG 帧；IPRO7 的 MJPEG 硬件只能编码。Reef 使用 `defconfig_reef`，控制台 921600 baud。
- **`ipro7ai_reef_demo`**：`mic usb` 让 Reef 成为 USB 麦克风（16 kHz，由 PDM 时钟转换采样率）；`mic sdrec` 把录音保存为 SD 卡上的 WAV 文件。
- **`build_freertos.sh`**：`flash` 根据配置文件自动选择 `--chip-variant`（Reef 与 IPRO7AI EVK 为 `IPRO7AI`），可用 `-c` 或 `IPRO_CHIP_VARIANT` 覆盖；`-P` 或 `IPRO_FLASH_PT` 指定分区表；`flash` 发送的 `reboot_dl`、`monitor` 与 `test` 都使用应用自己的控制台波特率。见[工具命令行](tools.md#build-cli)。
- **BLE 控制器**：IPRO7 的 16 个预编译库以本版本源码重新构建；头文件中声明的 `ipro_ble_ctlr_heap_watermarks()` 与 `ipro_ble_ctlr_link_diag_start()` 现在可以链接使用。
- **USB 设备**：修正 RX FIFO 溢出、反初始化时断开连接、CDC-ECM 数据包成帧，USB 控制台可稳定连接。**lwIP**：在中断中调用 `sys_mbox_trypost` 时改走 FromISR 路径。Opus 改用自己的 `arch.h` 构建。
- **BSP**：只用 BLE 的应用可使用关闭 PLL 的系统时钟；`CONFIG_OCRAM_NORET_SCRATCH_ONLY` 让 RAM 状态保留在 PDS 保留的 64 KB 内；`hal_lp_enter_fastboot()` 进入 HBN；安全引擎 HAL v2，含 PSA 加速器驱动。
- 示例应用不再内置任何网络账号或密码。

**应用**

- 共 40 个：37 个 IPRO7、3 个 IPRO6S。与 V2.1.0 相比，新增 `ipro_reef_teach`、`ipro7_jpeg_decode`、`ipro6_demo`、`ipro6_if_wifi`、`ipro6_fmac`；V2.1.0 的说话人识别应用更名为 `ipro_speaker_recog`。
- 9 个应用附带 IPRO7AI Reef EVK 的配置，列表与构建命令见[常见问题](faq.md#reef-apps)与 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#examples)。

发布前用软件包内容重新构建并检查：36 个 IPRO7 FreeRTOS 应用（`ipro_agora_sentino` 需先获取 AOSL 核心）、IPRO6S 的 7 个配置，以及 `ipro7_evb`、`ipro7ai_evk` 的 Zephyr 示例。

**未包含**

- IntelProCube 烧录工具：从 [GitHub](https://github.com/INTELPRO-INC/ipro-cube/releases) 下载 0.7.0.1，见[准备开发环境](../get-started/environment.md#intelprocube)。
- RISC-V 工具链：请联系 INTELPRO。
- IPRO AI Studio（含模型转换）：从 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载。
- IPRO6S 的 BLE 控制器库与 BLE／BR/EDR 应用；IPRO6S 应用只有 Wi-Fi。
- Matter；FreeRTOS 应用的 Thread（Thread 只在 Zephyr 下提供）。
- 片上调试（OpenOCD／GDB）的配置、崩溃转储的主机端工具、板级自动测试脚本、`menuconfig`。
- Zephyr：没有 Reef 的板型；不支持 IPRO6S；没有低功耗模式，也没有显示、摄像头、音频编解码、USB、SD 主机、以太网与 NPU 驱动。
- `ipro_agora_sentino` 需要的 AOSL 核心与 Sentino 设备三元组：AOSL 从 GitHub 获取，步骤见该应用的 README。

### 已知问题与注意事项 { #v2-2-0-known-issues }

- **Reef 板级配置文件的注释**：`bsp/board/ipro7/ipro7ai_reef_board_config.h` 的注释描述的是上一版（V3.0）载板的扩展排针与跳线；引脚定义与 V4.0 相同。V4.0 的排针、开关与跳线以本站的 [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md) 为准。
- **两个 IPRO6S 配置文件没有对应的预编译库**：`ipro6_demo/defconfig_ipro6_lpwifi_ping` 与 `ipro6_fmac/defconfig_ipro6_fmac_ap` 随附在软件包中，但没有设置 `CONFIG_WIRELESS_LIB_VARIANT`，不在发布前检查的配置之列。请使用 [IPRO6S](../hardware/chips/ipro6s.md) 页列出的配置文件。
- **`ipro_le_audio_headset`**：应用 README 的状态栏标明音频输出（render）当前停用、媒体流尚未验证；依赖音频输出前请先查看 README 的状态说明。
- **`ipro_throughput_test` 的文档**：README 与 `OPERATION_MANUAL.md` 提到的演示应用、Android App 与控制器构建选项（例如 `CONFIG_BTBLECONTROLLER_LIB`、`link8`）不在本版本中；构建与烧录请按照 README 的 Build／Flash 段落与 [BLE 吞吐量测试](../tutorials/ble-throughput.md)。
- **崩溃后的等待**：`ipro7ai_reef_demo` 与 `ipro_reef_teach` 设置了 `CONFIG_EXCEPTION_DUMP=y`，崩溃后会重复打印 `==DUMP_READY:2000000==`，等待未随附的主机端工具；保存诊断信息后按 SW2 复位，或把它设为 `n`。见[崩溃分析](debugging.md#crash-analysis)。
- **`build_freertos.sh` 只烧录 IPRO7**：它固定传 `--chipname ipro7`，也无法传 `--boot2`、`--mfg`；IPRO6S 镜像、`ipro_ble_remote` 的 OTA 版本与 `ipro_reef_teach` 请直接使用 IntelProCube。
- **README 中提到但未随附的项目**：部分组件与应用的 README 提到不在本版本中的应用、工具或文档（例如开发板使用手册与 Edge AI 编程指南）。文档可向 INTELPRO 索取，见[文档下载](../documents/index.md)。

## Online Setup 3.6.0 { #tools-3-6-0 }

发布日期：2026-11-04 ・ [下载安装程序](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.6.0)

Windows 在线安装程序。安装 SDK V2.2.0 时修正其在 Windows 上的构建问题：识别 IPRO 工具链（原本以 `/dev/null` 试编译，在 Windows 上一律改用标准 GCC 编译选项与非 DSP 版预编译库）、CMake 4 搭配 Ninja 时的构建信息，以及串口控制台；并加入 PowerShell 版的 `build_freertos.ps1`。SDK only 与 Full 安装出的 SDK 相同：SDK 一律按搭配的工具链准备。SDK 与工具链可以添加到现有环境，已安装的文件不会被覆盖。工具链仍为 GCC 13.1.1，Extension 保持 3.3.0。操作见 [Windows 安装与 VS Code](../get-started/windows.md)。

## IPRO-SDK-V2.1.0 { #v2-1-0 }

发布日期：2026-10-16 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.1.0)

新增 Zephyr RTOS 支持；FreeRTOS 应用以 IPRO7 为目标，共 35 个。

**新增与变更**

- **Zephyr RTOS**：SDK 同时也是 Zephyr v4.4.0 模块（`zephyr/module.yml`、`west.yml`），支持 `ipro7_evb` 与 `ipro7ai_evk`：GPIO、UART、SPI、I2C、PWM、ADC、DAC、定时器与 RTC、看门狗、Flash、DMA、随机数生成器、I2S／PDM 等驱动，Bluetooth LE（Zephyr Host 搭配 IPRO BLE 控制器预编译库）、IEEE 802.15.4 与 OpenThread，以 sysbuild 构建的 MCUboot，以及通过 BLE 的镜像上传（MCUmgr SMP）。从 `tools/zephyr/bootstrap.sh` 开始，见 [Zephyr RTOS](../guides/zephyr.md)。
- RF 驱动与 IEEE 802.15.4 MAC 以 Zephyr 用的预编译库提供（`components/wireless/rf/ipro7_rf/lib/zephyr/`、`components/wireless/ieee802154/lib/zephyr/`）。
- **新应用 `ipro_agora_sentino`**：在 IPRO7AI Reef EVK 上的 Sentino 云端 AI 语音对话：BLE 配网、通过 IPRO6S FIN 卡连接 Wi-Fi、MQTT 与 Agora RTC。随附 Agora RTC SDK 预编译库与 AOSL 的 IPRO7 移植；AOSL 核心、由 Sentino 平台分配的设备三元组与 FIN 卡固件需另行获取，方法见该应用的 README。
- **IPRO7AI Reef EVK 晶体微调**：Reef 构建默认把 RF 晶体 capcode 设为 95，在启动时与每次 RF 初始化时应用（`CONFIG_IPRO7_XTAL_CAPCODE`，应用配置中明确指定的值优先）；预编译的 RF 与 IEEE 802.15.4 库会采用应用的配置值。Zephyr 在 Reef 上请设置 `CONFIG_SOC_IPRO7_XTAL_CAPCODE=95`。
- **工具**：新增 `tools/serial_monitor.py`（`--timeout 0` 持续监视直到 Ctrl-C，Linux 上也可使用高波特率）与 `tools/zephyr/`。`build_freertos.sh` 与 Zephyr 脚本的串口取自 `-p`／`IPRO_SERIAL_PORT`，未指定时自动使用唯一的 USB 串口；烧录工具取自 `IPRO_FLASH_TOOL` 或 `PATH`。
- IPRO BLE 控制器的 16 个 IPRO7 预编译库已更新。

**应用**

- 共 35 个 FreeRTOS 应用。与 V2.0.9 相比，新增 `ipro_agora_sentino`。
- 与 V2.0.1 相比，新增 7 个：`ipro7ai_reef_demo`、`ipro7ai_evk_launcher`、`ipro7ai_evk_person_detect`、`ipro7ai_evk_rps`、`ipro7_uvc_cam`、`ipro_ai_link`、`ipro_agora_sentino`；IPRO6S 的 3 个应用（`ipro6_btdm_phyrf`、`ipro6_demo`、`ipro6_if_wifi`）不再提供。

**未包含**

- IPRO6S 的应用、BLE 控制器库与 `ipro6_rf`：软件包 README 仍提到 IPRO6S，但本版本没有对应内容；当时 IPRO6S 开发请使用 V2.0.1；V2.2.0 起 IPRO6S 应用回归软件包，见 [IPRO6S](../hardware/chips/ipro6s.md)。
- IPRO6S 端的 Wi-Fi 固件（含 Reef 的 FIN 卡），请联系 INTELPRO。
- Matter；FreeRTOS 应用的 Thread（Thread 只在 Zephyr 下提供）；模型转换工具。
- IntelProCube 烧录工具与 RISC-V 工具链，需另行获取。

**已知限制**

- `ipro_ble_remote/defconfig_lowpower` 会改为从源码构建 BLE 控制器，无法用本软件包构建。
- `build_freertos.sh flash` 不传 `--chip-variant` 与 `--pt`，`monitor` 固定为 115200 baud；IPRO7AI 开发板与 921600 baud 的应用请直接使用工具。V2.2.0 已改进，见 [IPRO-SDK-V2.2.0](#v2-2-0)。
- Zephyr 尚无低功耗模式，也没有显示、摄像头、音频编解码、USB、SD 主机、以太网与 NPU 驱动；没有 IPRO7AI Reef EVK 的板级定义。

发布时的构建与上板验证记录见 GitHub Release 页面。

## IPRO-SDK-V2.0.9 { #v2-0-9 }

发布日期：2026-10-15 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.9)

V2.1.0 之前的 IPRO7 版本，共 34 个应用，不含 Zephyr。

- 新增 IPRO7AI Reef EVK 出厂固件 `ipro7ai_reef_demo`：LED、按键、扬声器与耳机、麦克风、SD 卡与 OV5640／OV2640 摄像头；`defconfig_wifi_ipro6s` 通过 IPRO6S FIN 卡提供 Wi-Fi 与 RTSP 摄像头视频流。
- 新增 IPRO7AI EVK 应用 `ipro7ai_evk_launcher`、`ipro7ai_evk_rps`、`ipro7ai_evk_person_detect`，基于新的 EVK 板级库 `components/board/ipro7ai_evk`。
- 新增 `ipro7_uvc_cam`（USB UVC 摄像头）与 `ipro_ai_link`（IPRO AI Studio 的上板运行）。
- AI 库 `libai.a` 可从 SD 卡加载模型；预编译库不含构建机器的路径。
- 只含 IPRO7 应用；IPRO6S 开发请使用 V2.0.1。

## Online Setup 3.5.0 { #tools-3-5-0 }

发布日期：2026-09-10 ・ [下载安装程序](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.5.0)

每次运行时自动识别 IPRO-SDK 的正式 SDK Release，支持 `.tar.gz` SDK 压缩包，并在完整安装时为旧版 Windows linker 准备预编译库。

## IPRO-SDK-V2.0.1 { #v2-0-1 }

发布日期：2026-09-09 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/IPRO-SDK-V2.0.1)

延续 V2.0 的 IPRO6S 支持及 31 个应用项目，修正长时间 BLE 音频传输问题。

- 修正连续传输时 Bluetooth Host queue 发布的原子性问题。
- PDM 逻辑录音最长 4 小时，PSRAM ring 保留 240 秒，每 30 秒自动分段传输；Android 在分段之间保持高连接优先级。
- PDM 改用 `link2` 控制器、单连接 Host 与 2M PHY，提供 EVB／EVK 配置与 Android 配套源码。
- 包含 IPRO6S Wi-Fi／BR/EDR 示例、SDIO 双端固件、NPU／TFLM 示例及 `.inm`／`.tflite` 模型。
- 包含 `ipro_unit_test` 与 Linux x86-64 CMake；1.2.1 的 `serial_monitor.py` 与 `PREBUILT-ARCHIVES-STRIPPED.txt` 不在此包中。

正式发布记录载明 31/31 应用构建成功，并以 Pixel 7a 与 IPRO7AI 完成五分钟录音：十个 960,000 字节的区块、无丢包或序号缺口、ring 覆写成功，稳态传输速率为 84.2–91.2 KB/s。数值对应该测试组合，不代表所有开发板与手机都有相同结果。

## Online Installer 3.4.0 { #tools-3-4-0 }

[下载安装程序](https://github.com/INTELPRO-INC/ipro-sdk-releases/releases/tag/v3.4.0)

新增动态公开清单、独立的软件包版本、完整安装的兼容性选择，以及缓存离线安装。Extension 保持 3.3.0。此版本只会安装清单中登记的 SDK（stable 为 1.2.1）；要安装 SDK V2.2.0 请使用 3.6.0，见 [Windows 安装与 VS Code](../get-started/windows.md)。

## 开发工具：Windows 安装包／Extension 3.3.0 { #tools-3-3-0 }

安装包与 Extension 独立计算版本，此版本对应 SDK V1.2.1。Windows 安装向导提供 Full、Extension only 与 SDK only 三种模式；Extension 新增从 VSIX、SDK ZIP／文件夹与 Git 快照更新组件的入口，并延续控制中心与 Windows 内置的串口监视功能。操作见 [Windows 安装与 VS Code](../get-started/windows.md) 与 [VS Code Extension](../guides/vscode.md)。

## IPRO-IPRO7-SDK-V1.2.1 { #v1-2-1 }

发布日期：2026-09-08 ・ [GitHub Release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/v1.2.1)

- Zephyr 4.4 Host 位于 `ipro_bt_host`；IPRO BLE 控制器（预编译库）位于 `ipro_ble_controller`。
- 16 个控制器预编译库：4 种 ACL 配置 × 2 种功能配置 × debug／release；不含控制器源码。
- 包含 IPRO7 端 `ipronet_host`、`sdiowifi` 组件与 `ipro7_sdio_wifi` 示例；兼容的 IPRO6S 固件需另行获取。
- AI 推理以 `components/ai/lib/libai.a` 与头文件提供，未随附 `.blai` 模型文件。
- 随附 `tools/serial_monitor.py`；烧录工具、板级测试脚本、崩溃解析工具与 OpenOCD 配置需另行获取。
- 根据 `PREBUILT-ARCHIVES-STRIPPED.txt`，AI、ISP、RF、LC3 与低功耗框架库已移除调试信息，以兼容 binutils 2.41 之前的链接器；无法在这些库内进行源码级单步执行。

| 应用 | 路径 | 说明 |
|---|---|---|
| `ipro_ble_remote` | `apps/bluetooth/ble/ipro_ble_remote/` | GATT 服务、图像传输与 OTA |
| `ipro_ble_transparent` | `apps/bluetooth/ble/ipro_ble_transparent/` | UART／BLE 透传 |
| `ipro_throughput_test` | `apps/bluetooth/ble/ipro_throughput_test/` | BLE 双向吞吐量测试 |
| `ipro_ble_hid_keyboard` | `apps/bluetooth/ble/ipro_ble_hid_keyboard/` | HID over GATT 键盘 |
| `ipro_le_audio_headset` | `apps/bluetooth/le_audio/ipro_le_audio_headset/` | LE Audio 耳机，DAC／USB 音频输出配置 |
| `ipro_pdm_mic_demo` | `apps/multimedia/ipro_pdm_mic_demo/` | PDM 麦克风采集、BLE 传输与 LC3 压缩 |
| `ipro7_demo` | `apps/platform/ipro7_demo/` | 外设、图像、音频与以太网演示 |
| `ipro7_sdio_wifi` | `apps/platform/ipro7_sdio_wifi/` | IPRO7 SDIO 主机，搭配 IPRO6S 作为 Wi-Fi 无线模块 |
| `ipro7ai_evk_demo` | `apps/platform/ipro7ai_evk_demo/` | IPRO7AI EVK 显示、摄像头、音频与 AI／BLE 配置 |

V1.0.1 的独立图像采集、BIS source／sink、云端音频网关与语音助手应用未包含在此版本中。

## IPROREL-IPRO7-V1.0.1 { #v1-0-1 }

发布日期：2026-03-13 ・ 平台：IPRO7（RISC-V RV32IMAFC）

IPRO7 完整 SDK 交付包，整合平台、BLE、ISP 与 LE Audio，含 9 个参考应用、基于 Zephyr 的 BLE Host、预编译 linkN 控制器库与统一构建系统。

| 分类 | 应用 | 说明 |
|---|---|---|
| bluetooth/ble | `ipro_ble_remote` | GATT 服务演示（LED、Button、UART、OTA、图像传输） |
| bluetooth/ble | `ipro_ble_transparent` | BLE 透明数据传输，含 AT 指令接口 |
| bluetooth/ble | `ipro_ble_img_capture` | 图像采集与 BLE 图像上传服务（含 OTA） |
| bluetooth/ble | `ipro_throughput_test` | 双向 BLE 吞吐量测试（2M PHY + DLE） |
| bluetooth/le_audio | `ipro_le_audio_headset` | GAF／BAP 单播与广播耳机（LC3） |
| bluetooth/le_audio | `ipro_le_audio_bis_source` | 兼容 Auracast 的 BIS 广播音源 |
| bluetooth/le_audio | `ipro_le_audio_bis_sink` | BIS 广播接收端（BASE 解析与音频重采样） |
| multimedia | `ipro_agora_sentino` | Agora RTC 云端音频流网关（通过以太网／USB NCM 联网） |
| platform | `ipro7_demo` | IPRO7 平台外设功能演示 |

- BLE 协议栈：基于 Zephyr 的 Host（GAP、GATT、L2CAP、SMP、ISO、LE Audio）；IPRO BLE 控制器预编译库，含标准 BLE（`link1_periph`、`link1`–`link8`）、LE Audio（`link1_leaudio`、`link2_leaudio`）、BLE 5.4 + LE Audio（`link1_leaudio_53_54`、`link2_leaudio_53_54`、`link4_leaudio_53_54`）与 BLE 5.3／5.4（`link1_53`、`link1_54`、`link2_54`）等变体。
- 预编译库：`isp_algorithm`（ISP 图像处理）、`ipro7_rf`（RF 驱动）、`liblc3`（LC3 编解码）、`lp_framework`（低功耗框架）。
- 已知限制：不含 BLE 控制器源码，仅提供 linkN 预编译变体；不支持 `CONFIG_BLE_FORCE_SOURCE_BUILD`。

## IPRO-BLE-SDK-V0.0.1 { #v0-0-1 }

发布日期：2026-02-12 ・ 平台：IPRO7（RISC-V RV32IMAFC）

IPRO BLE SDK 首次正式发布，提供 BLE 5.4 与 LE Audio 开发环境，含 10 个应用、基于 Zephyr 的 BLE Host、预编译控制器库与统一构建系统。

- BLE 应用：BLE Remote（GATT 服务演示）、Throughput Test（双向吞吐量测试）、HID Keyboard（HOGP 键盘）、Transparent Data（透传与 AT 指令）。
- LE Audio 应用：LE Audio Headset（GAF／BAP 单播与广播耳机）、BIS Broadcast Source（兼容 Auracast 的广播音源）、BIS Broadcast Sink（BASE 解析与重采样）、Walkie-Talkie（以 BIS 实现的按键通话）。
- ESL 应用：ESL Tag（符合 Bluetooth ESL Profile 的电子标签）、ESL Gateway（管理 ESL 标签的接入点）。
- BLE 协议栈：IPRO BLE 控制器预编译库（linkN 变体，本版本新增 `link2_54`）、预编译 RF 驱动（`ipro7_rf`）与 LC3 编解码（`liblc3`）；移除旧的 btprofile 组件，应用统一使用 Zephyr `bt_*` API。
- 构建系统：统一构建命令 `./build_freertos.sh <app> build flash monitor`、自动检测 vendor 与标准 GCC 工具链、Kconfig 配置系统。
- 系统要求：RISC-V 工具链 `/opt/toolchain/riscv_ipro7/`、CMake 3.19 及以上、Ninja、Python 3.8 及以上。
- 已知限制：不含控制器源码；`ipro_blecontroller_test`（UART HCI 模式）因需要控制器源码而未包含；不支持 `CONFIG_BLE_FORCE_SOURCE_BUILD`。
