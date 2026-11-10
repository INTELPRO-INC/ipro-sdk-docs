---
title: "示例"
description: V2.2.0 随附的 40 个 FreeRTOS 应用：可在 IPRO7AI Reef EVK 上运行的 9 个应用各有一页步骤说明，其他应用列出所需的开发板。
migrate_from:
  - "applications.html"
not_migrated:
  - "applications.html#ipro-ble-img-capture"
---

# 示例

SDK 随附 40 个 FreeRTOS 应用，其中 37 个以 IPRO7／IPRO7AI 为目标、3 个以 IPRO6S 为目标。每个应用都是 `apps/` 下的独立目录，包含 `.config`、`CMakeLists.txt` 与 `Makefile`。可在 [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) 上运行的 9 个应用各有一页，写明构建、烧录与运行的步骤；其他应用需要别的开发板，只列在[其他开发板的应用](#other-boards)中。

## 在 Reef 上构建 { #overview }

多数应用的默认 `.config` 针对其他开发板，Reef 使用应用目录中的 Reef 配置文件，以 `DEFCONFIG=` 选用：

```bash
make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
```

| 项目 | 规则 |
|---|---|
| 构建目录 | `DEFCONFIG=defconfig_<名称>` 构建到 `build_<名称>/`，`.config` 不变；不加 `DEFCONFIG=` 时构建到 `build/` |
| 镜像 | `<构建目录>/build_out/<应用>_IPRO7.bin`（IPRO6S 应用为 `_IPRO6.bin`） |
| 直接用 `make` 构建 Reef 版本 | 只有 `ipro7ai_reef_demo`、`ipro_reef_teach` 与 `ipro_agora_sentino`；其他应用不加 `DEFCONFIG=` 会构建成 IPRO7 EVB 或 IPRO7AI EVK 版本 |
| 烧录 | `--chipname ipro7 --chip-variant IPRO7AI`；分区表、boot2 与 mfg 数据见各应用页面 |
| 控制台 | U6 的 UART0：除 `ipro7_jpeg_decode` 为 921600 外，Reef 配置都是 115200 baud |
| 一次完成 | `./build_freertos.sh -d defconfig_reef build flash monitor ipro_throughput_test`，自动选用 `--chip-variant IPRO7AI`，以 `-P` 指定分区表；无法写入 boot2 与 mfg 数据（见[工具命令行](../reference/tools.md)） |

下载模式、控制台接线与首次烧录见 [Reef 快速上手](../hardware/boards/reef-evk.md#quick-start)。

## Reef EVK 示例 { #reef }

<!-- BEGIN generated: examples-reef -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro7ai_reef_demo`](ipro7ai_reef_demo.md) | Reef 出厂固件：RGB LED、按键、扬声器与耳机、PDM 与耳麦麦克风、microSD、OV5640 摄像头各有一组 shell 命令；`mic usb` 让开发板成为 USB 麦克风，`mic sdrec` 把录音保存为 SD 卡上的 WAV 文件 | Reef（`.config`）；Reef＋IPRO6S FIN 卡（`defconfig_wifi_ipro6s`：Wi-Fi 与 RTSP 摄像头视频流） | UART 115200 |
| [`ipro_reef_teach`](ipro_reef_teach.md) | Reef 的 Edge AI 固件：一个镜像包含三个 Teach 工具，`image`（USB 摄像头＋图像分类）、`voice`（声纹识别）与 `sensor`（传感器分类），启动时根据 Flash 中保存的模式选择其一运行，由 IPRO AI Studio 操作。完整操作见 [IPRO AI Teach](../teach/index.md) | Reef（`.config`）；`image` 模式需要 OV5640 摄像头 | UART 115200 |
| [`ipro_ble_remote`](ipro_ble_remote.md) | GATT 参考应用：LED、按键、环境、UART、摄像头图像与图像上传服务；Reef 版另有 Reef 硬件服务与 BLE A/B OTA。附带 Android 演示 App `ipro_remote_demo.apk`。教程见[第一个 BLE 应用](../tutorials/first-ble-app.md) | Reef（`defconfig_reef`：WS2812、摄像头、SD 卡、音频与 BLE A/B OTA）；`.config`、`defconfig` 对应 IPRO7 EVB | UART 115200 |
| [`ipro_throughput_test`](ipro_throughput_test.md) | 双板 BLE 吞吐量测试：1M／2M／Coded PHY、DLE、ATT MTU 247。教程见 [BLE 吞吐量测试](../tutorials/ble-throughput.md) | 两块 Reef（`defconfig_reef`）；`.config` 对应 IPRO7 EVB | UART 115200 |
| [`ipro_le_audio_headset`](ipro_le_audio_headset.md) | LE Audio unicast 耳机：BAP unicast server、PACS、ASCS、CAP、CSIP、VCP，LC3 解码后由 DAC 输出。教程见 [LE Audio 入门](../tutorials/le-audio.md) | Reef（`defconfig_reef`：DAC 输出到耳麦插孔与扬声器）；`.config`、`DAC.config`、`UAC.config` 对应 IPRO7 EVB | UART 115200 |
| [`ipro7_uvc_cam`](ipro7_uvc_cam.md) | USB 网络摄像头：OV5640、ISP、硬件 MJPEG、USB Video Class；另一个 Reef 配置在 NPU 上运行石头剪刀布并画进画面。教程见 [USB 网络摄像头与石头剪刀布](../tutorials/usb-webcam.md) | Reef（`defconfig_reef_ov5640`：网络摄像头；`defconfig_reef_rps`：石头剪刀布）；`.config` 对应 IPRO7 EVB 搭配 SC101IOT | Reef：UART 115200<br>`.config`：UART 921600 |
| [`ipro7_jpeg_decode`](ipro7_jpeg_decode.md) | 用软件（TJpgDec）把 JPEG 解码成 RGB565／RGB888，附格式探测、内置测试图与主机端工具；IPRO7 的 MJPEG 硬件只能编码 | Reef（`defconfig_reef`）；`.config` 对应 IPRO7AI EVK | UART **921600** |
| [`ipro_ai_link`](ipro_ai_link.md) | IPRO AI Studio“Run on board”的板端固件：从 microSD（`sd:/`）加载 `.inm` 模型与输入、在 NPU 上推理、输出原始结果；也可在控制台手动操作 | Reef（`defconfig_reef`）；`.config` 对应 IPRO7 EVB | UART 115200（另有 USB CDC 控制台） |
| [`ipro_agora_sentino`](ipro_agora_sentino.md) | Sentino 云端 AI 语音对话：BLE 配网、经 IPRO6S FIN 卡连接 Wi-Fi、MQTT 登录、Agora RTC 实时语音；需另备 Sentino 设备三元组与 AOSL 核心 | Reef＋IPRO6S FIN 卡（`.config`，`make` 或 `make BOARD=reef`）；`BOARD=evk` 对应 IPRO7AI EVK（可构建，未经板上验证） | Reef：UART 115200 |
<!-- END generated: examples-reef -->

## 其他开发板的应用 { #other-boards }

以下应用没有 Reef 配置，需要表中所列的开发板；点击名称可打开 GitHub 上的源码。这些开发板的供应请联系 INTELPRO。

### BLE { #ble }

<!-- BEGIN generated: examples-ble -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro_ble_transparent`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/bluetooth/ble/ipro_ble_transparent) | UART／BLE 透明传输桥接，通过 AT 命令配置（AT 命令走 USB CDC） | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_ble_hid_keyboard`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/bluetooth/ble/ipro_ble_hid_keyboard) | HID over GATT 键盘 | 需要 IPRO7 EVB | UART 115200 |
<!-- END generated: examples-ble -->

### 音频与语音 { #audio }

<!-- BEGIN generated: examples-audio -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro_pdm_mic_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/multimedia/ipro_pdm_mic_demo) | PDM 麦克风采集、DAC 播放、经 BLE 以 LC3 传输音频流、SMP 配对、PDS31 休眠与绑定重连；Android 示例 App 源代码在 `tools/android/IproMicDemo/`。Reef 上的录音与播放见 `ipro7ai_reef_demo` 的 `mic` 命令 | 需要 IPRO7 EVB（`.config`）或 IPRO7AI EVK（`make BOARD=evk`） | EVB：UART 115200<br>EVK：UART 921600 |
<!-- END generated: examples-audio -->

### 平台与开发板 { #platform }

<!-- BEGIN generated: examples-platform -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro7_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro7_demo) | 全芯片参考：PWM、SPI、I2S、LCD、音频 ADC／DAC、USB 设备（CDC、HID、MSC、UAC、UVC）、文件系统、TRNG、DSP 等，各有 shell 命令 | 需要 IPRO7 EVB；另有 `defconfig_boot2_nopsram`、`defconfig_boot2_ota`、`defconfig_nist_fulltest`、`defconfig_security_cert` | UART 115200 |
| [`ipro7ai_evk_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro7ai_evk_demo) | IPRO7AI EVK bring-up：LCD、摄像头、麦克风、扬声器与 SD 卡；`config_bt` 加上 BLE 与 LE Audio | 需要 IPRO7AI EVK | `.config`：UART 921600<br>`config_*`：UART 115200 |
| [`ipro7ai_evk_launcher`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro7ai_evk_launcher) | 摄像头、LCD、麦克风与扬声器集成在单一镜像中，通过 NPU 识别手势切换页面 | 需要 IPRO7AI EVK | UART 921600 |
<!-- END generated: examples-platform -->

### AI 与图像 { #ai-vision }

<!-- BEGIN generated: examples-ai-vision -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro7ai_evk_person_detect`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/ai/ipro7ai_evk_person_detect) | 摄像头预览显示在 LCD 上，叠加 NPU 运行 YOLOv8 得到的人形／宠物框 | 需要 IPRO7AI EVK | UART 115200 |
| [`ipro7ai_evk_rps`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/ai/ipro7ai_evk_rps) | 与 NPU 上的 int8 CNN 玩石头剪刀布，附模型与训练脚本；Reef 上的同一个游戏为 `ipro7_uvc_cam` 的 `defconfig_reef_rps` | 需要 IPRO7AI EVK | UART 921600 |
| [`ipro_speaker_recog`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/ai/ipro_speaker_recog) | 用 NPU 识别说话人，模型放在 mfg 分区；Reef 上的声纹识别为 `ipro_reef_teach` 的 `voice` 模式 | 需要 IPRO7 EVB | UART 921600 |
<!-- END generated: examples-ai-vision -->

### 网络与 IPRO6S { #networking }

<!-- BEGIN generated: examples-networking -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro7_sdio_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro7_sdio_wifi) | IPRO7 作为 SDIO 主机、IPRO6S 作为 Wi-Fi 无线电，提供 lwIP 网络接口 `iproeth0` 与 DHCP。Reef 上的同等功能为 `ipro7ai_reef_demo` 的 `defconfig_wifi_ipro6s` | 需要 IPRO7 EVB 与 IPRO6S | UART 115200 |
| [`ipro6_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro6_demo) | IPRO6S Wi-Fi 6 station／soft-AP 与 shell；`defconfig_ipro6_lpwifi` 加上 DTIM 省电，`defconfig_ipro6_lp` 为低功耗演示 | 需要 IPRO6S EVK（见 [IPRO6S](../hardware/chips/ipro6s.md)） | UART 115200 |
| [`ipro6_if_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro6_if_wifi) | IPRO6S Wi-Fi 6 桥接到主机：SDIO（`defconfig_ipro6_sdio`，也是 Reef FIN 卡的固件）或 USB（`defconfig_ipro6_usb`） | IPRO6S EVK；FIN 卡（`defconfig_ipro6_sdio`，以 `--chipname ipro6` 烧录，见 [IPRO6S](../hardware/chips/ipro6s.md)） | UART 115200 |
| [`ipro6_fmac`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/platform/ipro6_fmac) | 面向 Linux cfg80211 主机的 FullMAC 固件（`defconfig_ipro6_fmac`）及其 Flash 加载程序（`defconfig_ipro6_fmac_loader`）；Linux 驱动程序不在 SDK 内 | 需要 IPRO6S EVK | UART 115200 |
<!-- END generated: examples-networking -->

IPRO6S 应用用 `--chipname ipro6` 烧录；构建与配置见 [IPRO6S](../hardware/chips/ipro6s.md)。

### 测试与 bring-up 程序 { #test-apps }

<!-- BEGIN generated: examples-test-apps -->
| 应用 | 用途 | 开发板与配置 | 控制台 |
|---|---|---|---|
| [`ipro_unit_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_unit_test) | HAL 与公共组件的单元测试，结束时打印 `ALL TESTS PASSED` 或 `SOME TESTS FAILED` | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_ai_bench`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_ai_bench) | 整个模型在 NPU 与 CPU 上的推理时间对比 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_npu_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_npu_yolo) | NPU 上的 YOLOv8 人形／宠物检测 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_tflm_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_tflm_test) | TensorFlow Lite Micro 搭配 NMSIS-NN 内核的模型性能测试 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_tflm_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_tflm_yolo) | 用 TensorFlow Lite Micro 在 CPU 上运行 YOLOv8 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_nmsis_nn_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_nmsis_nn_test) | NMSIS-NN 算子测试 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_tinymaix_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_tinymaix_demo) | TinyMaix INT8 MNIST 推理（`nn_info`、`nn_run`、`nn_benchmark`） | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_gh7007_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_gh7007_test) | GH7007 5 英寸 SPI LCD bring-up | 需要 IPRO7 EVB | USB CDC |
| [`ipro_gh7007_video`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_gh7007_video) | 在 GH7007 面板上播放 SD 卡中的视频 | 需要 IPRO7 EVB | USB CDC |
| [`ipro_epd_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_epd_test) | GDEY0213F52 2.13 英寸电子纸 bring-up | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_epd_el036`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_epd_el036) | EL036MF1 电子纸 bring-up | 需要 IPRO7 EVB | UART 921600 |
| [`kw307_radar_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/kw307_radar_test) | KW307 24 GHz 雷达模块（UART） | 需要 IPRO7AI EVK | UART 115200 |
| [`mpu6500_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/mpu6500_test) | MPU-6500 IMU（I2C；`mpu_init`、`mpu_read`、`mpu_stream`） | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_enc28j60_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_enc28j60_test) | ENC28J60 SPI 以太网 bring-up，收发原始数据包 | 需要 IPRO7 Arduino 开发板 | USB CDC |
| [`ipro_pio_sdh_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_pio_sdh_test) | 软件（PIO）SD 主机与硬件 SDH 同时挂载的文件系统测试 | 需要 IPRO7 EVB | USB CDC |
| [`ipro_sdio_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_sdio_probe) | SDIO 主机基本测试 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_atbm_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_atbm_probe) | ATBM6162 SDIO Wi-Fi 模块 bring-up 探测 | 需要 IPRO7 EVB | UART 115200 |
| [`ipro_lp_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_lp_test) | PDS31 进入／退出与 RTC 唤醒测试（`lp` 命令） | 需要 IPRO7 EVB | UART 115200 |
<!-- END generated: examples-test-apps -->

## 下一步 { #next-steps }

- [构建与烧录流程](../tutorials/build-and-flash.md)：在 Reef 上构建、烧录与打开控制台的完整流程。
- [创建第一个自己的应用](../tutorials/first-own-app.md)：从 Reef 的 `.config` 开始创建新应用。
- [构建系统与配置](../guides/build-system.md)：`DEFCONFIG=`、`BOARD=` 与配置文件。
- [Zephyr RTOS](../guides/zephyr.md)：`zephyr/samples/` 中的 Zephyr 示例（本版本没有 Reef 的 Zephyr 板型）。
