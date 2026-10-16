---
title: "Examples"
description: Catalog of the FreeRTOS applications shipped with V2.1.0, with purpose, supported boards and alternate configurations, console baud rate and a link to the source on GitHub.
migrate_from:
  - "applications.html"
not_migrated:
  - "applications.html#ipro-ble-img-capture"
---

# Examples

The FreeRTOS applications that ship with V2.1.0, grouped by purpose. Each application is a self-contained directory under `apps/` with its own `.config`, `CMakeLists.txt` and `Makefile`, and all of them target the IPRO7 chip family; click an application's name to open its source and README on GitHub. The Zephyr samples live in `zephyr/samples/`; see [Zephyr RTOS](../guides/zephyr.md).

Board abbreviations in the tables: EVB = [IPRO7 EVB](../hardware/boards/ipro7-evb.md), EVK = [IPRO7AI EVK](../hardware/boards/ipro7ai-evk.md), Reef = [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md).

## Building and flashing { #overview }

- Build: `make -C apps/<category>/<application>`, or `./build_freertos.sh build <application>`. The output is `build/build_out/<application>_IPRO7.bin`.
- Alternate configurations: select a `defconfig_*` or `config_*` file with `DEFCONFIG=`; it builds in `build_<name>/`. Only `ipro_pdm_mic_demo` and `ipro_agora_sentino` support `BOARD=`. See [Build and Flash Workflow](../tutorials/build-and-flash.md).
- Console: the baud rates come from `CONFIG_PLATFORM_UART_BAUDRATE` in each configuration, 115200 when unset. Programs marked USB CDC put their console on a USB virtual serial port instead of the UART.
- Flashing: the Reef and the EVK use `--chip-variant IPRO7AI`; for the other parameters see [Flashing & Serial Console](../get-started/flash-and-monitor.md). Applications that need a particular partition table, boot2 or a model partition describe it in their README.

## BLE { #ble }

| Application | Purpose | Boards and configurations | Console |
|---|---|---|---|
| [`ipro_ble_remote`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_ble_remote) | GATT reference: LED, key, environment, UART, PIR image and image upload services; ships the Android demo app `ipro_remote_demo.apk`. Tutorial: [Your First BLE Application](../tutorials/first-ble-app.md) | EVB (`.config`); Reef (`defconfig_reef`: WS2812, camera, SD card, audio and BLE A/B OTA; needs boot2 and `partition_cfg_2M_remote_ab.toml`). `defconfig_lowpower` needs the controller source and cannot be built from V2.1.0 | UART 115200 |
| [`ipro_ble_transparent`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_ble_transparent) | UART-to-BLE transparent bridge configured with AT commands; in the shipped configuration the AT commands run over USB CDC | EVB | UART 115200 |
| [`ipro_ble_hid_keyboard`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_ble_hid_keyboard) | HID over GATT keyboard | EVB | UART 115200 |
| [`ipro_throughput_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/ble/ipro_throughput_test) | Two-board BLE throughput test: 1M / 2M / Coded PHY, DLE, ATT MTU 247. Tutorial: [BLE Throughput Test](../tutorials/ble-throughput.md) | EVB (`.config`); Reef (`defconfig_reef`) | UART 115200 |
| [`ipro_le_audio_headset`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/bluetooth/le_audio/ipro_le_audio_headset) | LE Audio unicast headset: BAP unicast server, PACS, ASCS, VCP, CAP, LC3 decoding. Tutorial: [Getting Started with LE Audio](../tutorials/le-audio.md) | EVB (`.config` / `DAC.config`: DAC output; `UAC.config`: USB Audio); Reef (`defconfig_reef`) | UART 115200 |

Standalone FreeRTOS BIS broadcast source and sink applications are not included in V2.1.0; contact INTELPRO. Zephyr has matching broadcast samples.

## Audio and voice { #audio }

| Application | Purpose | Boards and configurations | Console |
|---|---|---|---|
| [`ipro_pdm_mic_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/multimedia/ipro_pdm_mic_demo) | PDM microphone capture, DAC playback, LC3 streaming over BLE, SMP pairing, PDS31 sleep with bonded reconnect, 2M bulk transfer; the Android companion app's source is in `tools/android/IproMicDemo/` | EVB (`.config`, same as `config_evb`); EVK (`make BOARD=evk`, uses `config_evk` and adds a 16 kHz USB microphone) | EVB: UART 115200<br>EVK: UART 921600 |
| [`ipro_agora_sentino`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/multimedia/ipro_agora_sentino) | Sentino cloud AI voice chat: BLE provisioning, Wi-Fi through the IPRO6S FIN card, MQTT login, Agora RTC voice. Needs a Sentino device triple and AOSL (see the README); the FIN card firmware is not included in V2.1.0, contact INTELPRO | Reef (`.config`, `make` or `make BOARD=reef`); EVK (`make BOARD=evk`, uses `config_evk`; builds but is not verified on the board) | Reef: UART 115200<br>EVK: UART 921600 |

## Platform and boards { #platform }

| Application | Purpose | Boards and configurations | Console |
|---|---|---|---|
| [`ipro7_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7_demo) | Full-chip reference: PWM, SPI, I2S, LCD, audio ADC / DAC, USB device (CDC, HID, MSC, UAC, UVC), file systems, TRNG, DSP and more, each with shell commands; the BLE demo is off by default | EVB; also `defconfig_boot2`, `defconfig_boot2_nopsram`, `defconfig_boot2_ota`, `defconfig_nist_fulltest`, `defconfig_security_cert` | UART 115200 |
| [`ipro7ai_evk_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7ai_evk_demo) | IPRO7AI EVK bring-up: LCD, camera, microphone, speaker and SD card | EVK. `.config` and `config_video`: SD-card video playback, no Bluetooth; `config_ai`: AI and NPU, no Bluetooth; `config_bt`, `config_autoplay`: BLE and LE Audio unicast sink, no AI | `.config`: UART 921600<br>`config_*`: UART 115200 |
| [`ipro7ai_evk_launcher`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7ai_evk_launcher) | Camera, LCD, microphone and speaker in one image, with pages switched by hand gestures recognized on the NPU; the person / pet detection model loads from the SD card as `sd:/models/person.inm`; ships `flash.sh` | EVK | UART 921600 |
| [`ipro7ai_reef_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7ai_reef_demo) | Reef out-of-box firmware: WS2812, keys, speaker and headphones, PDM / headset microphone / AUX-IN, SD card, OV5640 / OV2640 camera, each with shell commands | Reef (`.config`); `defconfig_wifi_ipro6s`: Wi-Fi through the IPRO6S FIN card plus an RTSP stream of the camera | UART 115200 |

## AI and vision { #ai-vision }

| Application | Purpose | Boards and configurations | Console |
|---|---|---|---|
| [`ipro7ai_evk_person_detect`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/ai/ipro7ai_evk_person_detect) | Camera preview on the LCD with YOLOv8 person / pet boxes from the NPU; the model goes into the mfg partition (`flash.sh` included) | EVK | UART 115200 |
| [`ipro7ai_evk_rps`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/ai/ipro7ai_evk_rps) | Rock-paper-scissors against a 4-class int8 CNN on the NPU; the model is linked into the firmware by default, and the model and training scripts are included | EVK | UART 921600 |
| [`ipro7_uvc_cam`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/multimedia/ipro7_uvc_cam) | USB webcam: DVP sensor, ISP, hardware MJPEG, USB Video Class | EVB (`.config`, SC101IOT); Reef (`defconfig_reef_ov5640`: OV5640; `defconfig_reef_rps`: adds rock-paper-scissors on the NPU, drawn into the stream) | `.config`: UART 921600<br>Reef: UART 115200 |

Programs that benchmark AI inference and the CPU inference libraries are listed under [Test and bring-up programs](#test-apps).

## Networking { #networking }

Wireless networking comes from an IPRO6S over SDIO, and wired networking uses Ethernet.

| Application | Purpose | Boards and configurations | Console |
|---|---|---|---|
| [`ipro7_sdio_wifi`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/platform/ipro7_sdio_wifi) | IPRO7 as the SDIO host with an IPRO6S as the Wi-Fi radio (`components/network/ipronet_host`), providing the lwIP network interface `iproeth0` and DHCP. The IPRO6S firmware is not included in V2.1.0; contact INTELPRO | EVB | UART 115200 |

The IPRO6S FIN card also provides the network for `defconfig_wifi_ipro6s` of `ipro7ai_reef_demo` and for `ipro_agora_sentino`; for ENC28J60 Ethernet over SPI see `ipro_enc28j60_test`.

## Test and bring-up programs { #test-apps }

Unit tests, benchmarks and peripheral bring-up programs under `apps/test/`. Most need an external module or panel; the wiring is in each program's README or source.

| Program | Purpose | Board | Console |
|---|---|---|---|
| [`ipro_unit_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_unit_test) | Unit tests for the HAL and the shared components; ends with `ALL TESTS PASSED` or `SOME TESTS FAILED` (works with `./build_freertos.sh test ipro_unit_test`) | EVB | UART 115200 |
| [`ipro_ai_bench`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_ai_bench) | Whole-model inference time on the NPU versus the CPU | EVB | UART 115200 |
| [`ipro_ai_link`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_ai_link) | Board firmware for IPRO AI Studio "Run on board": loads models and inputs from the SD card (`sd:/`) and returns the results over USB | EVB; Reef (`defconfig_reef`) | UART 115200 |
| [`ipro_npu_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_npu_yolo) | YOLOv8 person / pet detection on the NPU | EVB | UART 115200 |
| [`ipro_tflm_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_tflm_test) | TensorFlow Lite Micro model benchmark with NMSIS-NN kernels | EVB | UART 115200 |
| [`ipro_tflm_yolo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_tflm_yolo) | YOLOv8 on the CPU with TensorFlow Lite Micro | EVB | UART 115200 |
| [`ipro_nmsis_nn_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_nmsis_nn_test) | NMSIS-NN operator tests | EVB | UART 115200 |
| [`ipro_tinymaix_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_tinymaix_demo) | TinyMaix INT8 MNIST inference (`nn_info`, `nn_run`, `nn_benchmark`) | EVB | UART 115200 |
| [`ipro_gh7007_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_gh7007_test) | GH7007 5-inch SPI LCD bring-up | EVB | USB CDC |
| [`ipro_gh7007_video`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_gh7007_video) | Plays videos from the SD card on the GH7007 panel | EVB | USB CDC |
| [`ipro_epd_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_epd_test) | GDEY0213F52 2.13-inch e-paper bring-up | EVB | UART 115200 |
| [`ipro_epd_el036`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_epd_el036) | EL036MF1 e-paper bring-up | EVB | UART 921600 |
| [`kw307_radar_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/kw307_radar_test) | KW307 24 GHz radar module over UART | EVK | UART 115200 |
| [`mpu6500_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/mpu6500_test) | MPU-6500 IMU over I2C (`mpu_init`, `mpu_read`, `mpu_stream`) | EVB | UART 115200 |
| [`ipro_enc28j60_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_enc28j60_test) | ENC28J60 SPI Ethernet bring-up, sending and receiving raw frames | IPRO7 Arduino board | USB CDC |
| [`ipro_pio_sdh_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_pio_sdh_test) | File-system test with a software (PIO) SD host and the hardware SDH mounted at the same time | EVB | USB CDC |
| [`ipro_sdio_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_sdio_probe) | Basic SDIO host test | EVB | UART 115200 |
| [`ipro_atbm_probe`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_atbm_probe) | Bring-up probe for an ATBM6162 SDIO module | EVB | UART 115200 |
| [`ipro_lp_test`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.1.0/apps/test/ipro_lp_test) | PDS31 entry and exit with RTC wake-up (`lp` commands) | EVB | UART 115200 |

## Next steps { #next-steps }

- [First FreeRTOS Application](../get-started/first-app-freertos.md): build, flash and run your first application.
- [Build System & Configuration](../guides/build-system.md#variants): `DEFCONFIG=`, `BOARD=` and the build directories of alternate configurations.
- [Tutorials](../tutorials/index.md): step-by-step work with `ipro_ble_remote`, `ipro_throughput_test` and `ipro_le_audio_headset`.
- [Zephyr RTOS](../guides/zephyr.md#samples): the Zephyr samples in `zephyr/samples/`.
