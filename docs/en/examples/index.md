---
title: "Examples"
description: The 40 FreeRTOS applications in V2.2.1. The 9 that run on the IPRO7AI Reef EVK each have a step-by-step page; the others list the board they need.
migrate_from:
  - "applications.html"
not_migrated:
  - "applications.html#ipro-ble-img-capture"
---

# Examples

The SDK ships 40 FreeRTOS applications: 37 for IPRO7 / IPRO7AI and 3 for IPRO6S. Each is a self-contained directory under `apps/` with a `.config`, a `CMakeLists.txt` and a `Makefile`. The 9 applications that run on the [IPRO7AI Reef EVK V4.0](../hardware/boards/reef-evk.md) each have a page with the build, flash and run steps; the others need another board and are only listed under [Applications for other boards](#other-boards).

## Building for the Reef { #overview }

Most applications' default `.config` targets another board. For the Reef, pick the application's Reef configuration with `DEFCONFIG=`:

```bash
make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
```

| Item | Rule |
|---|---|
| Build directory | `DEFCONFIG=defconfig_<name>` builds into `build_<name>/` and leaves `.config` alone; without `DEFCONFIG=` the build goes to `build/` |
| Image | `<build directory>/build_out/<app>_IPRO7.bin` (`_IPRO6.bin` for the IPRO6S applications) |
| Plain `make` builds the Reef | only `ipro7ai_reef_demo`, `ipro_reef_teach` and `ipro_agora_sentino`; any other application without `DEFCONFIG=` builds for the IPRO7 EVB or the IPRO7AI EVK |
| Flashing | `--chipname ipro7 --chip-variant IPRO7AI`; partition table, boot2 and mfg payload as each application's page says |
| Console | UART0 on U6: 115200 baud for every Reef configuration except `ipro7_jpeg_decode` (921600) |
| All in one | `./build_freertos.sh -d defconfig_reef build flash monitor ipro_throughput_test` picks `--chip-variant IPRO7AI` itself and takes a partition table with `-P`; it cannot write boot2 or an mfg payload (see [Tool Command Lines](../reference/tools.md)) |

Download mode, console wiring and the first flash are covered in the [Reef quick start](../hardware/boards/reef-evk.md#quick-start).

## Reef EVK examples { #reef }

<!-- BEGIN generated: examples-reef -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro7ai_reef_demo`](ipro7ai_reef_demo.md) | Reef out-of-box firmware: a shell command group for the RGB LED, keys, speaker and headset, PDM and headset microphones, microSD and the OV5640 camera; `mic usb` turns the board into a USB microphone, `mic sdrec` records WAV files to the SD card | Reef (`.config`); Reef + IPRO6S FIN card (`defconfig_wifi_ipro6s`: Wi-Fi and an RTSP camera stream) | UART 115200 |
| [`ipro_reef_teach`](ipro_reef_teach.md) | The Reef's Edge AI firmware: one image with three Teach tools, `image` (USB camera + image classifier), `voice` (speaker recognition) and `sensor` (sensor classification); the mode stored in flash picks one at boot, driven from IPRO AI Studio. Full walkthrough: [IPRO AI Teach](../teach/index.md) | Reef (`.config`); `image` mode needs the OV5640 camera | UART 115200 |
| [`ipro_ble_remote`](ipro_ble_remote.md) | GATT reference: LED, key, environment, UART, camera image and image upload services; the Reef build adds a Reef hardware service and BLE A/B OTA. Ships the Android demo app `ipro_remote_demo.apk`. Tutorial: [Your First BLE Application](../tutorials/first-ble-app.md) | Reef (`defconfig_reef`: WS2812, camera, SD card, audio and BLE A/B OTA); `.config` and `defconfig` target the IPRO7 EVB | UART 115200 |
| [`ipro_throughput_test`](ipro_throughput_test.md) | Two-board BLE throughput test: 1M / 2M / Coded PHY, DLE, ATT MTU 247. Tutorial: [BLE Throughput Test](../tutorials/ble-throughput.md) | Two Reefs (`defconfig_reef`); `.config` targets the IPRO7 EVB | UART 115200 |
| [`ipro_le_audio_headset`](ipro_le_audio_headset.md) | LE Audio unicast headset: BAP unicast server, PACS, ASCS, CAP, CSIP, VCP, with LC3 decoded to the DAC. Tutorial: [Getting Started with LE Audio](../tutorials/le-audio.md) | Reef (`defconfig_reef`: DAC output to the headset jack and speaker); `.config`, `DAC.config` and `UAC.config` target the IPRO7 EVB | UART 115200 |
| [`ipro7_uvc_cam`](ipro7_uvc_cam.md) | USB webcam: OV5640, ISP, hardware MJPEG, USB Video Class; a second Reef configuration plays rock-paper-scissors on the NPU and draws it into the stream. Tutorial: [USB Webcam and Rock-Paper-Scissors](../tutorials/usb-webcam.md) | Reef (`defconfig_reef_ov5640`: webcam; `defconfig_reef_rps`: rock-paper-scissors); `.config` targets the IPRO7 EVB with an SC101IOT | Reef: UART 115200<br>`.config`: UART 921600 |
| [`ipro7_jpeg_decode`](ipro7_jpeg_decode.md) | Software JPEG decoding (TJpgDec) to RGB565 / RGB888, with a format probe, built-in test images and host tools; IPRO7's MJPEG block encodes only | Reef (`defconfig_reef`); `.config` targets the IPRO7AI EVK | UART **921600** |
| [`ipro_ai_link`](ipro_ai_link.md) | Board firmware for IPRO AI Studio "Run on board": loads `.inm` models and inputs from microSD (`sd:/`), runs them on the NPU and prints the raw outputs; also usable by hand from the console | Reef (`defconfig_reef`); `.config` targets the IPRO7 EVB | UART 115200 (also on a USB CDC port) |
| [`ipro_agora_sentino`](ipro_agora_sentino.md) | Sentino cloud AI voice chat: BLE provisioning, Wi-Fi through the IPRO6S FIN card, MQTT login and Agora RTC voice; needs a Sentino device triple and the AOSL core | Reef + IPRO6S FIN card (`.config`, `make` or `make BOARD=reef`); `BOARD=evk` targets the IPRO7AI EVK (builds, not verified on a board) | Reef: UART 115200 |
<!-- END generated: examples-reef -->

## Applications for other boards { #other-boards }

These applications have no Reef configuration and need the board listed; the names link to the source on GitHub. Contact INTELPRO for these boards.

### BLE { #ble }

<!-- BEGIN generated: examples-ble -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro_ble_transparent`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/bluetooth/ble/ipro_ble_transparent) | UART-to-BLE transparent bridge configured with AT commands (over USB CDC) | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_ble_hid_keyboard`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/bluetooth/ble/ipro_ble_hid_keyboard) | HID over GATT keyboard | Needs the IPRO7 EVB | UART 115200 |
<!-- END generated: examples-ble -->

### Audio and voice { #audio }

<!-- BEGIN generated: examples-audio -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro_pdm_mic_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/multimedia/ipro_pdm_mic_demo) | PDM microphone capture, DAC playback, LC3 streaming over BLE, SMP pairing, PDS31 sleep with bonded reconnect; the Android companion app's source is in `tools/android/IproMicDemo/`. On the Reef, use the `mic` commands of `ipro7ai_reef_demo` | Needs the IPRO7 EVB (`.config`) or the IPRO7AI EVK (`make BOARD=evk`) | EVB: UART 115200<br>EVK: UART 921600 |
<!-- END generated: examples-audio -->

### Platform and boards { #platform }

<!-- BEGIN generated: examples-platform -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro7_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro7_demo) | Full-chip reference: PWM, SPI, I2S, LCD, audio ADC / DAC, USB device (CDC, HID, MSC, UAC, UVC), file systems, TRNG, DSP and more, each with shell commands | Needs the IPRO7 EVB; also `defconfig_boot2_nopsram`, `defconfig_boot2_ota`, `defconfig_nist_fulltest`, `defconfig_security_cert` | UART 115200 |
| [`ipro7ai_evk_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro7ai_evk_demo) | IPRO7AI EVK bring-up: LCD, camera, microphone, speaker and SD card; `config_bt` adds BLE and LE Audio | Needs the IPRO7AI EVK | `.config`: UART 921600<br>`config_*`: UART 115200 |
| [`ipro7ai_evk_launcher`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro7ai_evk_launcher) | Camera, LCD, microphone and speaker in one image, with pages switched by hand gestures recognized on the NPU | Needs the IPRO7AI EVK | UART 921600 |
<!-- END generated: examples-platform -->

### AI and vision { #ai-vision }

<!-- BEGIN generated: examples-ai-vision -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro7ai_evk_person_detect`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/ai/ipro7ai_evk_person_detect) | Camera preview on the LCD with YOLOv8 person / pet boxes from the NPU | Needs the IPRO7AI EVK | UART 115200 |
| [`ipro7ai_evk_rps`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/ai/ipro7ai_evk_rps) | Rock-paper-scissors against an int8 CNN on the NPU, with the model and training scripts; on the Reef the same game is `ipro7_uvc_cam` `defconfig_reef_rps` | Needs the IPRO7AI EVK | UART 921600 |
| [`ipro_speaker_recog`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/ai/ipro_speaker_recog) | Speaker recognition on the NPU, with the model in the mfg partition; on the Reef, speaker recognition is the `voice` mode of `ipro_reef_teach` | Needs the IPRO7 EVB | UART 921600 |
<!-- END generated: examples-ai-vision -->

### Networking and IPRO6S { #networking }

<!-- BEGIN generated: examples-networking -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro7_sdio_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro7_sdio_wifi) | IPRO7 as the SDIO host with an IPRO6S as the Wi-Fi radio, providing the lwIP network interface `iproeth0` and DHCP. On the Reef the same is `ipro7ai_reef_demo` `defconfig_wifi_ipro6s` | Needs the IPRO7 EVB and an IPRO6S | UART 115200 |
| [`ipro6_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro6_demo) | IPRO6S Wi-Fi 6 station / soft-AP with a shell; `defconfig_ipro6_lpwifi` adds DTIM power save, `defconfig_ipro6_lp` is the low-power demo | Needs the IPRO6S EVK (see [IPRO6S](../hardware/chips/ipro6s.md)) | UART 115200 |
| [`ipro6_if_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro6_if_wifi) | IPRO6S Wi-Fi 6 bridge to a host over SDIO (`defconfig_ipro6_sdio`, also the Reef FIN card's firmware) or USB (`defconfig_ipro6_usb`) | IPRO6S EVK; FIN card (`defconfig_ipro6_sdio`, flashed with `--chipname ipro6`, see [IPRO6S](../hardware/chips/ipro6s.md)) | UART 115200 |
| [`ipro6_fmac`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro6_fmac) | FullMAC firmware for a Linux cfg80211 host (`defconfig_ipro6_fmac`) and its flash loader (`defconfig_ipro6_fmac_loader`); the Linux driver is not part of the SDK | Needs the IPRO6S EVK | UART 115200 |
<!-- END generated: examples-networking -->

IPRO6S applications are flashed with `--chipname ipro6`; building and configuration are on the [IPRO6S](../hardware/chips/ipro6s.md) page.

### Test and bring-up programs { #test-apps }

<!-- BEGIN generated: examples-test-apps -->
| Application | Purpose | Boards and configs | Console |
|---|---|---|---|
| [`ipro_unit_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_unit_test) | Unit tests for the HAL and the shared components; ends with `ALL TESTS PASSED` or `SOME TESTS FAILED` | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_ai_bench`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_ai_bench) | Whole-model inference time on the NPU versus the CPU | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_npu_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_npu_yolo) | YOLOv8 person / pet detection on the NPU | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_tflm_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_tflm_test) | TensorFlow Lite Micro model benchmark with NMSIS-NN kernels | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_tflm_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_tflm_yolo) | YOLOv8 on the CPU with TensorFlow Lite Micro | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_nmsis_nn_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_nmsis_nn_test) | NMSIS-NN operator tests | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_tinymaix_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_tinymaix_demo) | TinyMaix INT8 MNIST inference (`nn_info`, `nn_run`, `nn_benchmark`) | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_gh7007_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_gh7007_test) | GH7007 5-inch SPI LCD bring-up | Needs the IPRO7 EVB | USB CDC |
| [`ipro_gh7007_video`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_gh7007_video) | Plays videos from the SD card on the GH7007 panel | Needs the IPRO7 EVB | USB CDC |
| [`ipro_epd_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_epd_test) | GDEY0213F52 2.13-inch e-paper bring-up | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_epd_el036`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_epd_el036) | EL036MF1 e-paper bring-up | Needs the IPRO7 EVB | UART 921600 |
| [`kw307_radar_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/kw307_radar_test) | KW307 24 GHz radar module over UART | Needs the IPRO7AI EVK | UART 115200 |
| [`mpu6500_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/mpu6500_test) | MPU-6500 IMU over I2C (`mpu_init`, `mpu_read`, `mpu_stream`) | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_enc28j60_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_enc28j60_test) | ENC28J60 SPI Ethernet bring-up, sending and receiving raw frames | Needs the IPRO7 Arduino board | USB CDC |
| [`ipro_pio_sdh_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_pio_sdh_test) | File-system test with a software (PIO) SD host and the hardware SDH mounted at the same time | Needs the IPRO7 EVB | USB CDC |
| [`ipro_sdio_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_sdio_probe) | Basic SDIO host test | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_atbm_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_atbm_probe) | Bring-up probe for an ATBM6162 SDIO Wi-Fi module | Needs the IPRO7 EVB | UART 115200 |
| [`ipro_lp_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/test/ipro_lp_test) | PDS31 entry and exit with RTC wake-up (`lp` commands) | Needs the IPRO7 EVB | UART 115200 |
<!-- END generated: examples-test-apps -->

## Next steps { #next-steps }

- [Build and Flash Workflow](../tutorials/build-and-flash.md): building, flashing and opening the console on the Reef, end to end.
- [Create Your First Application](../tutorials/first-own-app.md): a new application started from the Reef's `.config`.
- [Build System & Configuration](../guides/build-system.md): `DEFCONFIG=`, `BOARD=` and configuration files.
- [Zephyr RTOS](../guides/zephyr.md): the Zephyr samples in `zephyr/samples/` (no Reef Zephyr board in this release).
