---
template: home.html
title: IPRO SDK
description: "INTELPRO IPRO SDK documentation: build, flash and test BLE, LE Audio, AI, imaging and Wi-Fi (through the IPRO6S FIN card) applications step by step on the IPRO7AI Reef EVK V4.0."
hide:
  - navigation
  - toc
hero:
  release_text: "{sdk} released on {date}"
  release_link: reference/release-notes/
  title: The embedded SDK for IPRO chips
  lead: "One architecture for the IPRO7 and IPRO6 families: FreeRTOS and Zephyr, BLE 5.4 and LE Audio, Wi-Fi, on-device NPU AI and imaging."
  primary:
    text: Get started
    link: get-started/
  download_text: Download SDK
arch:
  chips_label: Chips
  chip_link_text: Chip specifications
  default: ipro7ai
  chips:
    - { id: ipro7, name: IPRO7, sdk: V2.3.0, link: hardware/chips/ipro7/, desc: "RISC-V wireless SoC with BLE 5.4 and LE Audio, 802.15.4, ISP and MJPEG." }
    - { id: ipro7ai, name: IPRO7AI, sdk: V2.3.0, link: hardware/chips/ipro7ai/, desc: "IPRO7 plus an NPU and in-package PSRAM; the SoC on the IPRO7AI Reef EVK V4.0." }
    - { id: ipro6s, name: IPRO6S, sdk: V2.3.0, link: hardware/chips/ipro6s/, desc: "RISC-V SoC with on-chip Wi-Fi; on the Reef it is the FIN Wi-Fi card in the microSD slot." }
  layers:
    - name: Applications
      items:
        - { title: Examples, link: examples/, chips: [ipro7, ipro7ai, ipro6s], desc: "The 41 shipped applications; the 9 that run on the Reef come with step-by-step pages." }
        - { title: IPRO AI Teach, link: teach/, chips: [ipro7ai], desc: "The Reef's Edge AI firmware: teach the board images, voices and sensor signals with IPRO AI Studio." }
        - { title: Your application, wide: true, link: tutorials/first-own-app/, chips: [ipro7, ipro7ai, ipro6s], desc: "Start from a copy of the Reef's .config and pick components in it." }
    - name: Components
      items:
        - { title: BLE Host, link: guides/ble/, chips: [ipro7, ipro7ai], desc: "Zephyr v4.4 Bluetooth host, programmed through the bt_* API." }
        - { title: BLE controller, link: guides/ble/, chips: [ipro7, ipro7ai], desc: "IPRO BLE controller prebuilt libraries, chosen by connection count and features." }
        - { title: LE Audio / LC3, link: guides/audio/, chips: [ipro7, ipro7ai], desc: "BAP, CAP and the LC3 codec for unicast and broadcast audio." }
        - { title: AI runtime, link: guides/ai-npu/, chips: [ipro7ai], desc: "NPU inference runtime and the Edge AI platform: model store, input sources and preprocessing." }
        - { title: Camera & ISP, link: guides/camera/, chips: [ipro7, ipro7ai], desc: "DVP camera, ISP and hardware MJPEG, enough for a USB webcam." }
        - { title: lwIP / mbedTLS, link: guides/networking/, chips: [ipro7, ipro7ai, ipro6s], desc: "TCP/IP stack and TLS." }
        - { title: Wi-Fi, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: "The IPRO6S built-in Wi-Fi; MAC, wpa_supplicant and RF ship as prebuilt libraries." }
        - { title: SDIO Wi-Fi host, link: guides/networking/, chips: [ipro7, ipro7ai], desc: "Wi-Fi for the IPRO7 family through an IPRO6S over SDIO (the FIN card on the Reef)." }
        - { title: Thread, link: guides/thread-matter/, chips: [ipro7, ipro7ai], desc: "802.15.4 and OpenThread, available under Zephyr." }
    - name: RTOS
      items:
        - { title: FreeRTOS, link: guides/architecture/, chips: [ipro7, ipro7ai, ipro6s], desc: "The main development path; every example application builds on FreeRTOS." }
        - { title: Zephyr v4.4, link: guides/zephyr/, chips: [ipro7, ipro7ai], desc: "The SDK is also a Zephyr module, with the boards ipro7_evb and ipro7ai_evk (no Reef board in this release)." }
    - name: BSP & HAL
      items:
        - { title: HAL & drivers, link: reference/api/, chips: [ipro7, ipro7ai, ipro6s], desc: "Peripheral drivers and the HAL API." }
        - { title: Board config, link: hardware/boards/reef-evk/, chips: [ipro7, ipro7ai], desc: "The Reef's pinout, power and memory layout; the board is picked in .config." }
        - { title: Low power, link: guides/low-power/, chips: [ipro7, ipro7ai], desc: "PDS sleep and wake-up, retention planning." }
migrate_from:
  - "index.html"
---

## Start with the Reef { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **IPRO7AI Reef EVK V4.0** <span class="ipro-badge">The board</span>

    ---

    IPRO7AI development board with an OV5640 camera, PDM microphone, headset jack and speaker, microSD slot, RGB LED and a Raspberry Pi-style 40-pin header. Every step on this site is written for it.

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">OV5640</span> <span class="ipro-tag">PDM mic</span> <span class="ipro-tag">DAC speaker</span> <span class="ipro-tag">microSD</span>

    [Specs and quick start](hardware/boards/reef-evk.md)

-   :material-brain:{ .lg } **IPRO AI Teach**

    ---

    Flash the Edge AI firmware `ipro_reef_teach`, collect samples and train in IPRO AI Studio, then deploy the model back to the board: image classification, speaker recognition and sensor classification.

    <span class="ipro-tag">NPU</span> <span class="ipro-tag">Image</span> <span class="ipro-tag">Voice</span> <span class="ipro-tag">Sensor</span>

    [The full workflow](teach/index.md)

-   :material-wifi:{ .lg } **Wi-Fi and RTSP**

    ---

    Plug the IPRO6S FIN card into the microSD slot, join Wi-Fi over SDIO and stream the camera over RTSP.

    <span class="ipro-tag">IPRO6S</span> <span class="ipro-tag">Wi-Fi</span> <span class="ipro-tag">RTSP</span>

    [Step-by-step tutorial](tutorials/wifi-rtsp.md)

</div>

The SDK also carries applications for the IPRO7 EVB, the IPRO7AI EVK and the IPRO6S EVK; they are listed under [Examples](examples/index.md#other-boards). Contact INTELPRO for those boards.

## Three steps to start { #quick-start }

<div class="ipro-quickstart" markdown>

<div class="ipro-steps" markdown>

1. **Set up your host**: get the RISC-V toolchain from INTELPRO and IntelProCube 0.7.0.1 from GitHub, install CMake 3.15 or later, GNU make and Python 3.8 or later, then download SDK V2.3.0 from the release page. [Installation](get-started/index.md)
2. **Build the out-of-box firmware**: from the SDK root run `make -C apps/platform/ipro7ai_reef_demo`; the image is `build/build_out/ipro7ai_reef_demo_IPRO7.bin`.
3. **Flash and self-test**: hold SW1 and press SW2 for download mode, flash with IntelProCube and check for `[All Success]`; on the U6 console (115200 baud) type `reef selftest` and watch the LED, speaker, SD card and camera pass in turn. [Full walkthrough](get-started/first-app-freertos.md)

</div>

<div class="ipro-term" data-typing>
<div class="ipro-term__bar"><span></span><span></span><span></span><em>IPRO7AI Reef EVK</em></div>
<pre><code><span class="ln c"># Build the out-of-box firmware</span>
<span class="ln"><span class="p">$ </span><span class="cmd">make -C apps/platform/ipro7ai_reef_demo</span></span>
<span class="ln c"># Flash (from the IntelProCube directory)</span>
<span class="ln"><span class="p">$ </span><span class="cmd">./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI ...</span></span>
<span class="ln ok">[All Success]</span>
<span class="ln c"># After reset, on the U6 console (115200 baud)</span>
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

## More resources { #resources }

<div class="ipro-links" markdown>

- [:material-monitor-dashboard: **IPRO Workbench**](workbench/index.md)<br>The IPRO development environment: set up the tools, build, flash, monitor and debug in one window
- [:material-brain: **IPRO AI Teach**](teach/index.md)<br>Install IPRO AI Studio, flash the Edge AI firmware and teach the Reef images, voices and sensor signals
- [:material-school-outline: **Tutorials**](tutorials/index.md)<br>Build and flash, your first application, testing, BLE, LE Audio, the webcam and Wi-Fi
- [:material-view-grid-outline: **Examples**](examples/index.md)<br>The 41 shipped applications; the 9 that run on the Reef come with steps
- [:material-code-tags: **API Reference**](reference/api/index.md)<br>Platform, HAL, BLE controller and AI runtime interfaces
- [:material-console: **Tool Command Lines**](reference/tools.md)<br>Build script, flashing, serial console, OTA and Teach tools
- [:material-help-circle-outline: **FAQ**](reference/faq.md)<br>Common questions about building, flashing, BLE and networking

</div>

## What's new in V2.3 { #whats-new }

- **V2.3.0** (2026-11-13): the OTA component `components/sys/ipro_ota`. The BLE OTA service (0xFF60) and the console UART command `ota_uart` share one package check, which verifies the header and SHA-256 of the package written to flash before the partition table is switched. See [OTA Updates](guides/ota.md).
- **IPRO7AI Sensor Tag example `ipro7ai_sensor_tag_demo`**: reads the IMU, fuel gauge and button, drives the LEDs and buzzer, and sends 20 lines of values a second over the board's own USB for the Sensor Dashboard of IPRO Workbench 0.2.1. It is flashed over the board's USB with the new tool `tools/ipro_dl.py`, without a probe.
- **IPRO6S**: the boot prints a `Build:` line (the build time), so IPRO Workbench can tell which firmware the board runs; `wifi_ap_start -b 1 -o 1` keeps a 2.4 GHz access point on its 40 MHz channel when neighbouring networks overlap it; with DTIM power save, beacons that an access point sometimes sends late are no longer missed.
- **Use it with [IPRO Workbench 0.2.1](workbench/index.md)**: configurations, the Sensor Dashboard, sending OTA packages to the board, the Wi-Fi page, new starting applications, flashing over the board's own USB (macOS, Windows 11), and Simplified Chinese and Japanese.
- **41 applications**. Everything else is in the [Release Notes](reference/release-notes.md#v2-3-0), along with what was new in V2.2.
