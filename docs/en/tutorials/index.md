---
title: "Tutorials"
description: Hands-on tutorials you run end to end on the IPRO7AI Reef EVK, from building and flashing and writing and testing your own app to BLE, LE Audio, a USB webcam and a Wi-Fi RTSP stream.
migrate_from:
  - "tutorials.html#next-steps"
---

# Tutorials

Each tutorial runs step by step on the IPRO7AI Reef EVK, with the commands to type and the output to expect. Finish [Get Started](../get-started/index.md) first so that the toolchain and the IntelProCube flasher are ready.

<div class="grid cards" markdown>

-   **[Build and Flash Workflow](build-and-flash.md)**

    ---

    The day-to-day loop: chaining `build_freertos.sh` actions, `DEFCONFIG=` variants, clean builds and reading memory usage.

-   **[Create Your First Application](first-own-app.md)**

    ---

    Write your own app from an empty directory: blink the RGB LED, read the keys, add a shell command, use the logging API.

-   **[Test Your Application](testing.md)**

    ---

    Manual console checks, a self-test that prints a verdict, automation with `serial_monitor.py` and `build_freertos.sh test`, and host-side unit tests.

-   **[Your First BLE Application](first-ble-app.md)**

    ---

    Run `ipro_ble_remote` on the Reef, drive its GATT services from a phone, change the code and update it over BLE OTA.

-   **[BLE Throughput Test](ble-throughput.md)**

    ---

    Run `ipro_throughput_test` on two Reef boards, measure 1M and 2M PHY throughput and compare with the SDK's own figures.

-   **[Getting Started with LE Audio](le-audio.md)**

    ---

    Run the LE Audio unicast headset `ipro_le_audio_headset`, pair it with a phone, change the volume from the keys, and see what this release has validated.

-   **[USB Webcam and Rock-Paper-Scissors](usb-webcam.md)**

    ---

    `ipro7_uvc_cam` turns the Reef into a driverless USB webcam; another configuration plays rock-paper-scissors on the NPU and draws it into the video.

-   **[Wi-Fi and RTSP Camera Stream](wifi-rtsp.md)**

    ---

    Join Wi-Fi through the IPRO6S FIN card in the microSD slot, stream the camera over RTSP and update the FIN card's firmware.

</div>

## What each tutorial needs { #requirements }

Every tutorial needs an IPRO7AI Reef EVK, a USB-C cable, and an IPRO Debug Probe or a 3.3 V USB-UART cable on U6. On top of that:

| Tutorial | Reef boards | Phone | Camera | FIN card | microSD card | Other |
|---|---|---|---|---|---|---|
| [Build and Flash Workflow](build-and-flash.md) | 1 | — | — | — | — | — |
| [Create Your First Application](first-own-app.md) | 1 | — | — | — | — | — |
| [Test Your Application](testing.md) | 1 | — | — | — | — | macOS or Linux for the automated parts |
| [Your First BLE Application](first-ble-app.md) | 1 | Android or iOS | Optional (photos) | — | Optional (saves photos) | A macOS or Linux computer with Bluetooth for BLE OTA |
| [BLE Throughput Test](ble-throughput.md) | 2 | — | — | — | — | One debug cable per board |
| [Getting Started with LE Audio](le-audio.md) | 1 | Android with LE Audio | — | — | — | Optional headphones (J2) |
| [USB Webcam and Rock-Paper-Scissors](usb-webcam.md) | 1 | — | OV5640 | — | — | A USB-C data cable |
| [Wi-Fi and RTSP Camera Stream](wifi-rtsp.md) | 1 | — | OV5640 | Required | — | A Wi-Fi access point; a computer with VLC or `ffplay` |

To train your own AI models and deploy them to the Reef, see [IPRO AI Teach](../teach/index.md).
