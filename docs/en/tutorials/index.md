---
title: "Tutorials"
description: Hands-on tutorials you run end to end on the IPRO7AI Reef EVK, covering a BLE application, the daily build and flash loop, BLE throughput and LE Audio.
migrate_from:
  - "tutorials.html#next-steps"
---

# Tutorials

Each tutorial starts from an application that ships with V2.1.0, runs step by step on the IPRO7AI Reef EVK and shows the console output to expect. Finish [Get Started](../get-started/index.md) first so that the toolchain and the flash tool are ready.

<div class="grid cards" markdown>

-   **[Your First BLE Application](first-ble-app.md)**

    ---

    Run `ipro_ble_remote` on the Reef, drive its GATT services from a phone, then rename the device and make it beep when a phone connects.

-   **[Build and Flash Workflow](build-and-flash.md)**

    ---

    The day-to-day loop: chaining `build_freertos.sh` actions, `DEFCONFIG=` variants, clean builds, reading memory usage, and working around the script's defaults.

-   **[BLE Throughput Test](ble-throughput.md)**

    ---

    Run `ipro_throughput_test` on two Reef boards, measure 1M and 2M PHY throughput and compare with the SDK's own figures.

-   **[Getting Started with LE Audio](le-audio.md)**

    ---

    Run the LE Audio unicast headset `ipro_le_audio_headset` on the Reef, pair it with a phone, change the volume from the keys, and meet the Zephyr broadcast samples.

</div>
