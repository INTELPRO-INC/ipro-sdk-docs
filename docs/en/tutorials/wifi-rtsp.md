---
title: "Wi-Fi and RTSP Camera Stream"
description: Connect the IPRO7AI Reef EVK to Wi-Fi through the IPRO6S FIN card in its microSD slot, stream the OV5640 camera to a computer over RTSP, and update the FIN card's firmware with ipro6s_ota.
---

# Wi-Fi and RTSP Camera Stream

The IPRO7AI Reef EVK reaches the network through the FIN card: an IPRO6S Wi-Fi card that plugs into the microSD slot (CARD1) and talks SDIO to the IPRO7AI. At the end of this tutorial the Reef runs the Wi-Fi build of its out-of-box firmware `ipro7ai_reef_demo` (`defconfig_wifi_ipro6s`), joins your access point and serves the camera as MJPEG over RTSP at `rtsp://<IP>:8554/av0_0`, which you watch in VLC or `ffplay`. The last step shows how to update the FIN card's firmware over Wi-Fi with `ipro6s_ota`.

## Prerequisites { #prerequisites }

- An IPRO7AI Reef EVK, an IPRO6S FIN card and an OV5640 FLEX-24 camera module.
- Wi-Fi firmware on the FIN card: the IPRO6S `ipro6_if_wifi` application built with `defconfig_ipro6_sdio` (the SDIO version, see step 2).
- An IPRO Debug Probe or a 3.3 V USB-UART cable on U6 (115200 8N1; wiring in [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)).
- [First FreeRTOS Application](../get-started/first-app-freertos.md) done, and the IntelProCube v0.6.3 command-line flasher at hand (obtained separately).
- A Wi-Fi access point (SSID and passphrase) and a computer on the same network with VLC or `ffplay`.

!!! info "First firmware on a FIN card"
    The SDK provides the FIN card firmware's sources and build configuration, and the `ipro6s_ota` command that updates it over Wi-Fi. To write firmware to a FIN card that has none yet, contact INTELPRO.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Fit the FIN card and the camera.** Unplug USB-C first. Set JP3 to GPIO (the slot supply then follows GPIO14, which `fin cycle` needs to power-cycle the card), insert the FIN card into the microSD slot and the camera cable into FPC1, check that SW7 is on CAM and SW8 on PWR, connect U6, and plug in USB-C last.

2. **(Optional) Build the FIN card firmware.** You need it only to update the card (step 10). From the SDK root:

    ```bash
    make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio
    ```

    Output: `apps/platform/ipro6_if_wifi/build_ipro6_sdio/build_out/ipro6_if_wifi_IPRO6.bin`. This configuration starts Wi-Fi and the SDIO bridge on its own about 600 ms after reset; nothing is typed on the FIN card, and the Reef drives association and DHCP.

3. **Build the Reef's Wi-Fi version.**

    ```bash
    make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s
    ```

    Output: `apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin`. This configuration adds `components/network/ipronet_host` (the SDIO host side), lwIP and the RTSP server (port 8554) to the out-of-box firmware, and drops the USB microphone (`mic usb`) to make room.

4. **Flash.** Hold SW1 (BOOT), tap SW2 (RESET) and release SW1 to enter download mode (if the out-of-box firmware is running, `reboot_dl` does the same), then from the IntelProCube directory:

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build_wifi_ipro6s/build_out/ipro7ai_reef_demo_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\platform\ipro7ai_reef_demo\build_wifi_ipro6s\build_out\ipro7ai_reef_demo_IPRO7.bin
        ```

    Check the output for `[All Success]` (the tool exits with 0 even on failure).

5. **Open the console and check the FIN card.** Open the console at 115200 baud and tap SW2. The boot log ends with the available commands (level and time fields left out):

    ```text
    REEF: shell ready - `reef`, `led`, `btn`, `spk`, `mic`, `sd`, `fin`, `cam`, `hp`
    REEF: IPRO-WiFi - `ipronet_up <ssid> <psk>`
    REEF: RTSP - `rtsp_cam on [fps]`
    ```

    Type `fin` to check that the card is seated and powered:

    ```text
    IPRO6S_FIN: SDIO slave in the SD slot, SD_VDD = its 3V3.
      seated : yes (DET GPIO15)
      supply : on (GPIO14, JP3 2-3 required for control)
      host   : SDH_0 on GPIO28-33, see apps/platform/ipro7_sdio_wifi
    fin cycle | fin power on|off
    ```

    ("JP3 2-3" in the message is the jumper name of an earlier board revision; on the V4.0 board it is JP3 = GPIO.)

6. **Start Wi-Fi and scan for access points.**

    ```text
    ipronet_up
    ipro6s_scan
    ipro6s_scan_last
    ```

    Without arguments, `ipronet_up` only starts Wi-Fi on the FIN card and prints `ipronet_start -> 0`. `ipro6s_scan` starts a scan whose results arrive asynchronously; after a second or two, `ipro6s_scan_last` lists the latest result:

    ```text
    [ctrl] scan_last: <count> APs (on_scan_result fired <n> times)
       0 ssid=<SSID>                           rssi=<signal> ch=<channel> auth=<security>
    ```

7. **Join the access point.**

    ```text
    ipro6s_connect <SSID> <passphrase>
    ```

    ```text
    [ctrl] connect '<SSID>' -> 0 (CONNECTED_IND + IP_UPDATE_IND arrive async)
    [ctrl] STA CONNECTED
    [ctrl] IP <IP address> / <netmask> gw <gateway>
    ```

    To start and connect in one go, type `ipronet_up <SSID> <passphrase>` right after a reset instead. If no `[ctrl] IP …` line appears, type `ipro6s_link_status`: `host connected=1 ip=1` means the link is up with an address.

8. **Start the RTSP stream.**

    ```text
    rtsp_cam on
    ```

    It starts the camera if it is not running yet, then prints the format and the URL:

    ```text
    rtsp_cam: on, <sensor> <width>x<height> JPEG q<quality>, 15 fps
    rtsp_cam: rtsp://<IP address>:8554/av0_0
    ```

    The default is 15 fps; `rtsp_cam on <fps>` takes 1 to 30.

9. **Watch it on the computer.** With the computer on the same network, open a network stream in VLC (Media > Open Network Stream) with the URL from the previous step, or use `ffplay`:

    ```bash
    ffplay rtsp://<IP address>:8554/av0_0
    ```

    `rtsp_cam stats` shows the frames sent, the average JPEG size and encoder errors; `rtsp_cam off` stops sending (the camera keeps running until `cam stop`); `ipronet_down` shuts Wi-Fi down.

10. **Update the FIN card firmware.** `ipro6s_ota` downloads an IPRO6S OTA package from an HTTP server and writes it to the FIN card, whose boot2 installs it after a restart. The package is an IPRO6S package generated by IntelProCube (`FW_OTA.bin.xz.ota`, a 512-byte header plus XZ-compressed content); for the steps that turn the build from step 2 into a package, contact INTELPRO. Put the package in a folder on your computer and serve that folder over HTTP:

    ```bash
    python3 -m http.server 8000
    ```

    At the Reef's console (with Wi-Fi connected), type:

    ```text
    ipro6s_ota http://<computer IP>:8000/FW_OTA.bin.xz.ota
    ```

    The whole update takes about 30 to 60 seconds: the Reef stops Wi-Fi traffic and downloads the package, the FIN card writes and checks it and restarts to install it, and the Reef enumerates the card again and reconnects. On success it prints:

    ```text
    [ota] fetch <bytes> B in <ms> ms
    [ota] RESULT OK total=<ms> …
    ```

    On failure it prints `[ota] RESULT ERR rc=<code> … phase=<phase>`.

</div>

## Verify { #verify }

- `fin` shows `seated : yes`, and `ipro6s_scan_last` lists the access points around you.
- After connecting, the console prints `[ctrl] IP …` and `ipro6s_link_status` shows `host connected=1 ip=1`.
- `rtsp_cam on` prints `rtsp://<IP>:8554/av0_0`, VLC or `ffplay` shows live video, and the frame count in `rtsp_cam stats` keeps rising.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `fin` shows `seated : no` | The card is not fully inserted | Unplug USB-C, reseat the FIN card and power up again |
| `ipronet_start` returns non-zero | The FIN card does not answer: no firmware, not the SDIO version, or the card is stuck | With JP3 on GPIO, type `fin cycle` to power-cycle it and try again; check that the card runs `ipro6_if_wifi` built with `defconfig_ipro6_sdio` |
| `ipro6s_scan_last` shows 0 APs | The scan result has not arrived yet | Wait a second or two and run `ipro6s_scan_last` again; rerun `ipro6s_scan` if needed |
| `[ctrl] IP …` never appears | Wrong SSID or passphrase, or the access point is out of range | Check the SSID with `ipro6s_scan_last`; `ipro6s_disconnect`, then `ipro6s_connect` again |
| `rtsp_cam: camera gives no frames - …` | The camera produces no frames | Check SW7 on CAM and the camera cable; type `cam stop`, then `rtsp_cam on` |
| `rtsp_cam: no IP yet - …` | Wi-Fi has no address yet | Finish step 7, then run `rtsp_cam on` again for the URL |
| VLC cannot connect | The computer and the Reef are on different networks, or the access point isolates wireless clients | Check that the computer can `ping <IP address>`; turn off client isolation on the access point |
| `ipro6s_ota` prints `[ota] RESULT ERR … phase=fetch` | The computer's HTTP server cannot be reached, or the path is wrong | Open the same URL in a browser on the computer; check the firewall |

## Next steps { #next-steps }

- [Networking](../guides/networking.md): the `ipronet_host` API, lwIP integration and network settings.
- [IPRO6S](../hardware/chips/ipro6s.md): the IPRO6S chip on the FIN card and the other `ipro6_if_wifi` configurations.
- [USB Webcam and Rock-Paper-Scissors](usb-webcam.md): send the camera video over USB instead.
- [Camera & Imaging](../guides/camera.md): the image pipeline and sensor settings.
