---
template: home.html
title: IPRO SDK
description: INTELPRO IPRO SDK 开发文档：基于 IPRO7AI Reef EVK V4.0 逐步构建、烧录并测试 BLE、LE Audio、AI、图像与 Wi-Fi（通过 IPRO6S FIN 卡）应用。
hide:
  - navigation
  - toc
hero:
  release_text: "{sdk} 已于 {date} 发布"
  release_link: reference/release-notes/
  title: "IPRO 系列芯片​开发套件"
  lead: 一套架构覆盖 IPRO7 与 IPRO6 系列：FreeRTOS 与 Zephyr、BLE 5.4 与 LE Audio、Wi-Fi 6、NPU 端侧 AI 与图像处理。
  primary:
    text: 开始使用
    link: get-started/
  download_text: 下载 SDK
arch:
  chips_label: 芯片
  chip_link_text: 芯片规格
  default: ipro7ai
  chips:
    - { id: ipro7, name: IPRO7, sdk: V2.2.0, link: hardware/chips/ipro7/, desc: 支持 BLE 5.4 与 LE Audio、802.15.4、ISP 与 MJPEG 的 RISC-V 无线 SoC。 }
    - { id: ipro7ai, name: IPRO7AI, sdk: V2.2.0, link: hardware/chips/ipro7ai/, desc: IPRO7 加上 NPU 与封装内 PSRAM；IPRO7AI Reef EVK V4.0 的主芯片。 }
    - { id: ipro6s, name: IPRO6S, sdk: V2.2.0, link: hardware/chips/ipro6s/, desc: 内置 Wi-Fi 6 的 RISC-V SoC；在 Reef 上是插在 microSD 卡座中的 FIN Wi-Fi 卡。 }
  layers:
    - name: 应用
      items:
        - { title: 示例应用, link: examples/, chips: [ipro7, ipro7ai, ipro6s], desc: 随附的 40 个应用；在 Reef 上运行的 9 个各有分步说明。 }
        - { title: IPRO AI Teach, link: teach/, chips: [ipro7ai], desc: Reef 的 Edge AI 固件，用 IPRO AI Studio 教会开发板识别图像、声纹与传感信号。 }
        - { title: 你的应用, wide: true, link: tutorials/first-own-app/, chips: [ipro7, ipro7ai, ipro6s], desc: 从复制一份 Reef 的 .config 开始，在 .config 中选择组件。 }
    - name: 组件
      items:
        - { title: BLE Host, link: guides/ble/, chips: [ipro7, ipro7ai], desc: Zephyr v4.4 Bluetooth Host，使用 bt_* API 开发。 }
        - { title: BLE 控制器, link: guides/ble/, chips: [ipro7, ipro7ai], desc: IPRO BLE 控制器预编译库，按连接数与功能选择。 }
        - { title: LE Audio／LC3, link: guides/audio/, chips: [ipro7, ipro7ai], desc: BAP、CAP 与 LC3 编解码，单播与广播音频。 }
        - { title: AI 运行库, link: guides/ai-npu/, chips: [ipro7ai], desc: NPU 推理运行库与 Edge AI 平台：模型存储、输入源与预处理。 }
        - { title: 摄像头与 ISP, link: guides/camera/, chips: [ipro7, ipro7ai], desc: DVP 摄像头、ISP 与硬件 MJPEG，可做 USB 网络摄像头。 }
        - { title: lwIP／mbedTLS, link: guides/networking/, chips: [ipro7, ipro7ai, ipro6s], desc: TCP/IP 协议栈与 TLS。 }
        - { title: Wi-Fi 6, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: IPRO6S 内置的 Wi-Fi 6；MAC、wpa_supplicant 与射频为预编译库。 }
        - { title: SDIO Wi-Fi 主机, link: guides/networking/, chips: [ipro7, ipro7ai], desc: 通过 SDIO 连接 IPRO6S（Reef 上为 FIN 卡），为 IPRO7 系列提供 Wi-Fi。 }
        - { title: Thread, link: guides/thread-matter/, chips: [ipro7, ipro7ai], desc: 802.15.4 与 OpenThread，在 Zephyr 下提供。 }
    - name: RTOS
      items:
        - { title: FreeRTOS, link: guides/architecture/, chips: [ipro7, ipro7ai, ipro6s], desc: 主要开发路径，所有示例应用都以 FreeRTOS 构建。 }
        - { title: Zephyr v4.4, link: guides/zephyr/, chips: [ipro7, ipro7ai], desc: SDK 同时也是 Zephyr 模块，板型为 ipro7_evb 与 ipro7ai_evk（本版本没有 Reef 板型）。 }
    - name: BSP 与 HAL
      items:
        - { title: HAL 与驱动, link: reference/api/, chips: [ipro7, ipro7ai, ipro6s], desc: 外设驱动与 HAL API。 }
        - { title: 板级配置, link: hardware/boards/reef-evk/, chips: [ipro7, ipro7ai], desc: Reef 的引脚、电源与内存布局，用 .config 选择开发板。 }
        - { title: 低功耗, link: guides/low-power/, chips: [ipro7, ipro7ai], desc: PDS 休眠与唤醒、保留内存规划。 }
migrate_from:
  - "index.html"
---

## 从 Reef 开始 { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **IPRO7AI Reef EVK V4.0** <span class="ipro-badge">开发板</span>

    ---

    IPRO7AI 开发板：OV5640 摄像头、PDM 麦克风、耳麦插孔与扬声器、microSD 卡座、RGB LED，以及位于树莓派位置的 40-pin 排针。本站所有步骤都以这块开发板为准。

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">OV5640</span> <span class="ipro-tag">PDM 麦克风</span> <span class="ipro-tag">DAC 扬声器</span> <span class="ipro-tag">microSD</span>

    [开发板规格与上手](hardware/boards/reef-evk.md)

-   :material-brain:{ .lg } **IPRO AI Teach**

    ---

    烧录 Edge AI 固件 `ipro_reef_teach`，在 IPRO AI Studio 中采集样本、训练，再把模型部署回开发板：图像识别、声纹识别与传感器识别。

    <span class="ipro-tag">NPU</span> <span class="ipro-tag">图像</span> <span class="ipro-tag">声纹</span> <span class="ipro-tag">传感器</span>

    [完整操作流程](teach/index.md)

-   :material-wifi:{ .lg } **Wi-Fi 与 RTSP**

    ---

    把 IPRO6S FIN 卡插入 microSD 卡座，通过 SDIO 连接 Wi-Fi，并用 RTSP 推流摄像头画面。

    <span class="ipro-tag">IPRO6S</span> <span class="ipro-tag">Wi-Fi 6</span> <span class="ipro-tag">RTSP</span>

    [分步教程](tutorials/wifi-rtsp.md)

</div>

SDK 也包含 IPRO7 EVB、IPRO7AI EVK 与 IPRO6S EVB 的应用，列在[示例](examples/index.md#other-boards)中；这些开发板的供货请联系 INTELPRO。

## 三步上手 { #quick-start }

<div class="ipro-quickstart" markdown>

<div class="ipro-steps" markdown>

1. **准备开发环境**：向 INTELPRO 获取 RISC-V 工具链与 IntelProCube v0.6.3，安装 CMake 3.15 及以上版本、GNU make 与 Python 3.8 及以上版本，再从发布页下载 SDK V2.2.0。[安装说明](get-started/index.md)
2. **构建出厂固件**：在 SDK 根目录执行 `make -C apps/platform/ipro7ai_reef_demo`，镜像位于 `build/build_out/ipro7ai_reef_demo_IPRO7.bin`。
3. **烧录并自检**：按住 SW1、按一下 SW2 进入下载模式，用 IntelProCube 烧录并确认 `[All Success]`；在 U6 控制台（115200 baud）输入 `reef selftest`，LED、扬声器、SD 卡与摄像头依次通过。[完整步骤](get-started/first-app-freertos.md)

</div>

<div class="ipro-term" data-typing>
<div class="ipro-term__bar"><span></span><span></span><span></span><em>IPRO7AI Reef EVK</em></div>
<pre><code><span class="ln c"># 构建出厂固件</span>
<span class="ln"><span class="p">$ </span><span class="cmd">make -C apps/platform/ipro7ai_reef_demo</span></span>
<span class="ln c"># 烧录（在 IntelProCube 目录下）</span>
<span class="ln"><span class="p">$ </span><span class="cmd">./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI ...</span></span>
<span class="ln ok">[All Success]</span>
<span class="ln c"># 复位后，U6 控制台（115200 baud）</span>
<span class="ln o">  IPRO7AI Reef carrier demo</span>
<span class="ln o">shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, ...</span>
<span class="ln"><span class="p">ipro /&gt; </span><span class="cmd">reef selftest</span></span>
<span class="ln o">[1/4] RGB LED: red, green, blue</span>
<span class="ln o">[2/4] speaker: 1 kHz, 300 ms, 20%</span>
<span class="ln o">[3/4] SD slot: empty, supply on</span>
<span class="ln o">[4/4] camera bus: __rti_name_ov5640 at 0x3C</span>
<span class="ln ok">done - keys: press any and run `btn status`</span></code></pre>
</div>

</div>

## 更多资源 { #resources }

<div class="ipro-links" markdown>

- [:material-monitor-dashboard: **IPRO Workbench**](workbench/index.md)<br>IPRO 的集成开发环境：补齐工具、构建、烧录、串口监视与调试都在同一个窗口中
- [:material-brain: **IPRO AI Teach**](teach/index.md)<br>安装 IPRO AI Studio、烧录 Edge AI 固件，教会 Reef 识别图像、声纹与传感信号
- [:material-school-outline: **教程**](tutorials/index.md)<br>构建与烧录、第一个自己的应用、测试、BLE、LE Audio、网络摄像头与 Wi-Fi
- [:material-view-grid-outline: **示例**](examples/index.md)<br>40 个随附应用；可在 Reef 上运行的 9 个各有步骤
- [:material-code-tags: **API 参考**](reference/api/index.md)<br>平台、HAL、BLE 控制器与 AI 运行库的接口
- [:material-console: **工具命令行**](reference/tools.md)<br>构建脚本、烧录、串口、OTA 与 Teach 工具
- [:material-help-circle-outline: **常见问题**](reference/faq.md)<br>构建、烧录、BLE 与联网的常见问题

</div>

## V2.2.0 重点 { #whats-new }

- **IPRO6S 应用回归**：`ipro6_demo`（Wi-Fi 6 station／soft-AP 与 DTIM 省电）、`ipro6_if_wifi`（通过 SDIO 或 USB 桥接到主机，也是 Reef FIN 卡的固件）与 `ipro6_fmac`（FullMAC 固件与 Flash 加载程序）。IPRO6S 应用只包含 Wi-Fi，本版本没有 IPRO6S 蓝牙。
- **Edge AI 平台 V2.0 与 `ipro_reef_teach`**：一个 Reef 固件包含图像、声纹与传感器三个 Teach 工具，由 IPRO AI Studio 操作；IPRO AI Studio 可从 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载。
- **新应用 `ipro7_jpeg_decode`**：用软件把 JPEG 解码为 RGB565／RGB888。`ipro7ai_reef_demo` 新增 `mic usb`（USB 麦克风）与 `mic sdrec`（录制 WAV 到 SD 卡）。
- **共 40 个应用**。USB 设备、lwIP 与 BSP 的修正见[版本说明](reference/release-notes.md)。
