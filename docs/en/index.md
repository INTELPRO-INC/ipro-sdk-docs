---
template: home.html
title: IPRO SDK
description: INTELPRO IPRO SDK documentation for building BLE, LE Audio, AI and imaging applications on IPRO7 and IPRO7AI with FreeRTOS or Zephyr.
hide:
  - navigation
  - toc
hero:
  release_text: "{sdk} released on {date}"
  release_link: reference/release-notes/
  title: The embedded SDK for IPRO chips
  lead: "One architecture for the IPRO7 and IPRO6 families: FreeRTOS and Zephyr, BLE 5.4 and LE Audio, Wi-Fi 6, on-device NPU AI and imaging."
  primary:
    text: Get started
    link: get-started/
  download_text: Download SDK
arch:
  chips_label: Chips
  chip_link_text: Chip specifications
  default: ipro7ai
  chips:
    - { id: ipro7, name: IPRO7, sdk: V2.1.0, link: hardware/chips/ipro7/, desc: "RISC-V wireless SoC with BLE 5.4 and LE Audio, 802.15.4, ISP and MJPEG." }
    - { id: ipro7ai, name: IPRO7AI, sdk: V2.1.0, link: hardware/chips/ipro7ai/, desc: "IPRO7 plus an NPU and 8 MB in-package PSRAM, for on-device vision AI." }
    - { id: ipro6s, name: IPRO6S, sdk: V2.0.1, link: hardware/chips/ipro6s/, desc: "RISC-V SoC with built-in Wi-Fi 6, BLE 5.4 and BR/EDR." }
  layers:
    - name: Applications
      items:
        - { title: Examples, wide: true, link: examples/, chips: [ipro7, ipro7ai, ipro6s], desc: "Shipped BLE, audio, AI, camera and networking examples, by board." }
        - { title: Your application, wide: true, link: guides/build-system/, chips: [ipro7, ipro7ai, ipro6s], desc: "Pick components and the board in .config; start from a copy of an example." }
    - name: Components
      items:
        - { title: BLE Host, link: guides/ble/, chips: [ipro7, ipro7ai, ipro6s], desc: "Zephyr v4.4 Bluetooth host, programmed through the bt_* API." }
        - { title: BLE controller, link: guides/ble/, chips: [ipro7, ipro7ai, ipro6s], desc: "IPRO BLE controller prebuilt libraries, chosen by connection count and features." }
        - { title: LE Audio / LC3, link: guides/audio/, chips: [ipro7, ipro7ai], desc: "BAP, CAP and the LC3 codec for unicast and broadcast audio." }
        - { title: BR/EDR audio, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: "Dual-mode Bluetooth audio: A2DP, AVRCP, HFP and SCO." }
        - { title: AI runtime, link: guides/ai-npu/, chips: [ipro7ai], desc: "NPU inference runtime and bundled models for person detection and gestures." }
        - { title: Camera & ISP, link: guides/camera/, chips: [ipro7, ipro7ai], desc: "DVP camera, ISP and hardware MJPEG, enough for a USB webcam." }
        - { title: lwIP / mbedTLS, link: guides/networking/, chips: [ipro7, ipro7ai, ipro6s], desc: "TCP/IP stack and TLS." }
        - { title: Wi-Fi 6, link: hardware/chips/ipro6s/, chips: [ipro6s], desc: "The IPRO6S built-in Wi-Fi 6." }
        - { title: SDIO Wi-Fi host, link: guides/networking/, chips: [ipro7, ipro7ai], desc: "Wi-Fi for the IPRO7 family through an IPRO6S over SDIO." }
        - { title: Thread, link: guides/thread-matter/, chips: [ipro7, ipro7ai], desc: "802.15.4 and OpenThread, available under Zephyr." }
    - name: RTOS
      items:
        - { title: FreeRTOS, link: guides/architecture/, chips: [ipro7, ipro7ai, ipro6s], desc: "The main development path; every example application builds on FreeRTOS." }
        - { title: Zephyr v4.4, link: guides/zephyr/, chips: [ipro7, ipro7ai], desc: "The SDK is also a Zephyr module, supporting ipro7_evb and ipro7ai_evk." }
    - name: BSP & HAL
      items:
        - { title: HAL & drivers, link: reference/api/, chips: [ipro7, ipro7ai, ipro6s], desc: "Peripheral drivers and the HAL API." }
        - { title: Board config, link: guides/build-system/, chips: [ipro7, ipro7ai, ipro6s], desc: "Pinout, power and memory layout for each board." }
        - { title: Low power, link: guides/low-power/, chips: [ipro7, ipro7ai], desc: "PDS sleep and wake-up, retention planning." }
migrate_from:
  - "index.html"
---

## Choose your board { #boards }

<div class="grid cards" markdown>

-   :material-developer-board:{ .lg } **IPRO7AI Reef EVK** <span class="ipro-badge">Recommended</span>

    ---

    IPRO7AI carrier with the camera, audio and SD slot on board; the slot also takes an IPRO6S FIN card for Wi-Fi.

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">OV5640</span> <span class="ipro-tag">PDM mic</span> <span class="ipro-tag">DAC speaker</span> <span class="ipro-tag">SD card</span>

    [Specs and quick start](hardware/boards/reef-evk.md)

-   :material-monitor-dashboard:{ .lg } **IPRO7AI EVK**

    ---

    LCD, camera, microphone and speaker on the sub-board, for vision AI and user-interface work.

    <span class="ipro-tag">IPRO7AI</span> <span class="ipro-tag">2.4" LCD</span> <span class="ipro-tag">SC101IOT</span> <span class="ipro-tag">microSD</span>

    [Board specs](hardware/boards/ipro7ai-evk.md)

-   :material-chip:{ .lg } **IPRO7 EVB**

    ---

    IPRO7 evaluation board; the default board for most BLE, audio and test examples, and Zephyr's `ipro7_evb`.

    <span class="ipro-tag">IPRO7</span> <span class="ipro-tag">BLE examples</span> <span class="ipro-tag">Zephyr</span>

    [Board specs](hardware/boards/ipro7-evb.md)

</div>

## Three steps to start { #quick-start }

<div class="ipro-quickstart" markdown>

<div class="ipro-steps" markdown>

1. **Install the tools**: on Windows use Online Installer 3.4.0 and VS Code Extension 3.3.0; on macOS and Linux use the command-line toolchain. [Installation](get-started/index.md)
2. **Build your first application**: from the SDK root run `make -C apps/platform/ipro7ai_reef_demo`; output goes to `build/build_out/`.
3. **Flash and open the console**: flash with IntelProCube, open the console on connector U6 (115200 baud) and run `reef selftest`. [Full walkthrough](get-started/first-app-freertos.md)

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
<span class="ln o">[4/4] camera bus: OV5640 at 0x3C</span>
<span class="ln ok">done - keys: press any and run `btn status`</span></code></pre>
</div>

</div>

## More resources { #resources }

<div class="ipro-links" markdown>

- [:material-layers-triple: **Zephyr RTOS**](guides/zephyr.md)<br>Zephyr v4.4 module, `ipro7_evb` and `ipro7ai_evk` boards, samples
- [:material-view-grid-outline: **Examples**](examples/index.md)<br>Every shipped application, by feature and board
- [:material-school-outline: **Tutorials**](tutorials/index.md)<br>Step-by-step BLE, throughput and LE Audio tutorials
- [:material-code-tags: **API Reference**](reference/api.md)<br>Platform, HAL, BLE controller and AI runtime interfaces
- [:material-console: **Tool Command Lines**](reference/tools.md)<br>Build script, flashing, serial console and OTA tools
- [:material-help-circle-outline: **FAQ**](reference/faq.md)<br>Common questions about building, flashing, BLE and networking

</div>

## What's new in V2.1.0 { #whats-new }

- **Zephyr RTOS v4.4**: the SDK is also a Zephyr module, supporting `ipro7_evb` and `ipro7ai_evk`.
- **New `ipro_agora_sentino`**: voice conversation with Sentino cloud AI on the Reef (the only application added since V2.0.9).
- **Seven applications added since V2.0.1**: `ipro7ai_reef_demo`, `ipro7ai_evk_launcher`, `ipro7ai_evk_person_detect`, `ipro7ai_evk_rps`, `ipro_ai_link`, `ipro7_uvc_cam`, `ipro_agora_sentino`.
- **Not included**: Matter, Thread for FreeRTOS applications (Thread is available under Zephyr only) and model conversion tools. See the [release notes](reference/release-notes.md) for details.
