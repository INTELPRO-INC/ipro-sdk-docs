---
title: "USB Webcam and Rock-Paper-Scissors"
description: Turn the IPRO7AI Reef EVK and its OV5640 camera into a driverless USB webcam with ipro7_uvc_cam, then switch to the build that plays rock-paper-scissors on the NPU and draws the game into the video.
---

# USB Webcam and Rock-Paper-Scissors

At the end of this tutorial the IPRO7AI Reef EVK with an OV5640 camera shows up on your computer as a USB webcam (UVC, MJPEG) over its USB-C port, with no driver to install; you watch it at 1280×720 or 640×360 in any camera app. You then switch to the `defconfig_reef_rps` configuration: the board recognises hand signs on the NPU, plays rock-paper-scissors with you and draws the game into the video it sends. Both are Reef configurations of the `apps/multimedia/ipro7_uvc_cam` application.

## Prerequisites { #prerequisites }

- An IPRO7AI Reef EVK, an OV5640 FLEX-24 camera module and a USB-C data cable to your computer (it powers the board and carries the video).
- An IPRO Debug Probe or a 3.3 V USB-UART cable on U6 (115200 8N1; wiring in [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)) for flashing and the console.
- [First FreeRTOS Application](../get-started/first-app-freertos.md) done, and the IntelProCube 0.7.0.1 command-line flasher installed as in [Set Up Your Host](../get-started/environment.md#intelprocube).
- An app that opens a USB camera: QuickTime Player on macOS, the Camera app on Windows, or any V4L2 program such as `ffplay` on Linux. The host uses the operating system's built-in UVC driver; INTELPRO has verified this on macOS.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Connect the camera.** Unplug USB-C first. Insert the OV5640 module's flex cable into FPC1, check that SW7 is on CAM (camera pins to the IPRO7AI, camera supplies on) and SW8 on PWR, connect U6, and plug USB-C into your computer last.

2. **Build the webcam configuration.** From the SDK root:

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_ov5640
    ```

    Output: `apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin`. A plain `make` without `DEFCONFIG=` builds for another board (the IPRO7 EVB) and does not run on the Reef.

3. **Flash.** Hold SW1 (BOOT), tap SW2 (RESET) and release SW1 to enter download mode, then flash from the IntelProCube directory with the standard 2 MB table:

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/multimedia/ipro7_uvc_cam/build_reef_ov5640/build_out/ipro7_uvc_cam_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\multimedia\ipro7_uvc_cam\build_reef_ov5640\build_out\ipro7_uvc_cam_IPRO7.bin
        ```

    Check the output for `[All Success]` (the tool exits with 0 even on failure). These two configurations do not use the `mfg` partition.

4. **Open the console and reset.** Open the U6 port at 115200 baud and tap SW2. The console prints:

    ```text
    [SYS] Reset reason: <reason>
    [UVC] Starting init task...
    [OS] Starting OS Scheduler...
    [UVC] Bringing up USB UVC webcam (720p MJPEG)...
    [UVC] Streaming pipeline started
    ```

5. **Check that the computer sees the camera.** The board appears as `IPRO7 UVC Cam` with USB VID/PID `0x3896`/`0x0701`:

    === "macOS"

        ```bash
        system_profiler SPUSBDataType | grep -A4 "IPRO7 UVC Cam"
        ```

    === "Linux"

        ```bash
        lsusb -d 3896:0701
        ```

    === "Windows"

        `IPRO7 UVC Cam` appears under Cameras in Device Manager.

6. **Watch it on the computer.**
    - macOS: open QuickTime Player, choose File > New Movie Recording, and pick `IPRO7 UVC Cam` in the menu next to the record button.
    - Windows: open the Camera app and switch to `IPRO7 UVC Cam`.
    - Linux:

        ```bash
        ffplay -f v4l2 -input_format mjpeg -video_size 640x360 /dev/video0
        ```

    The video comes in two sizes and the app on the computer picks one: 1280×720 (about 15 fps for a busy scene, limited by USB Full-Speed bandwidth) and 640×360 (30 fps).

7. **Tune the sensor (optional).** The console's `cam` command reads and writes OV5640 registers directly (register address and data in hex) and can print statistics over a grid of the frame:

    ```text
    cam rd 300a 2
    ```

    ```text
    RD 300a 56 40
    ```

    `300a` and `300b` hold the OV5640 chip ID (`0x56`, `0x40`). `cam wr <reg> <hexbytes>` writes registers, and `cam grid [cols rows]` prints the mean Y, U and V of each cell between `GRID` and `GRIDEND`. Written values return to their defaults after a reset.

8. **Switch to the rock-paper-scissors configuration.** Build `defconfig_reef_rps` and flash it as in step 3 (with `build_reef_rps` in the path):

    ```bash
    make -C apps/multimedia/ipro7_uvc_cam DEFCONFIG=defconfig_reef_rps
    ```

    Output: `apps/multimedia/ipro7_uvc_cam/build_reef_rps/build_out/ipro7_uvc_cam_IPRO7.bin`. The hand-sign model is linked into the firmware, so there is no model to flash separately.

9. **Play.** After a reset, open `IPRO7 UVC Cam` at 640×360 on the computer. The score bar is at the top and the message bar at the bottom; the box in the middle is what the NPU looks at, labelled live with the sign it sees. Hold your hand still in the box: the video counts down 3, 2, 1, the board captures your sign, picks its own at random and shows both moves and the score. The next round starts after your hand leaves the box.

    Type `rps` at the console for the model and game state:

    ```text
    rps
    ```

    ```text
    model   : ready, <bytes> B from <source>, loaded in <ms> ms, <free> KB heap left
    npu     : <frames> frames, 0 errors, <inferences per second> fps, last <ms> ms
    now     : <current sign> <confidence>%  (r <%> p <%> s <%> n <%>)
    game    : round <n>, you <wins> me <losses> draw <draws>, conf >= 60%, mirror on
    ```

    | Command | Effect |
    |---|---|
    | `rps go` | Start a round now, without waiting for a hand in the box |
    | `rps reset` | Reset the score |
    | `rps mirror on\|off` | Mirror the video left to right (on by default, like a mirror); use `off` when the viewer mirrors its own preview (Photo Booth, FaceTime) |
    | `rps print on\|off` | Print every classifier result on the console |
    | `rps conf <percent>` | Confidence needed to count a sign (60 by default) |
    | `rps dump` | Print one 128×128 frame as the NPU sees it, base64 between `CAPBEGIN` and `CAPEND` (about 8 s at 115200 baud) |

</div>

## Verify { #verify }

- The console prints `[UVC] Streaming pipeline started`, and the computer lists `IPRO7 UVC Cam` (`3896:0701`).
- Webcam configuration: the camera app shows live video and switches between 1280×720 and 640×360.
- Rock-paper-scissors configuration: the video shows the score bar, the box and a live sign label; a hand in the box starts the countdown, and the frame count on the `npu` line of `rps` keeps rising.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| No `IPRO7 UVC Cam` on the computer | A charge-only USB-C cable, or a non-Reef build was flashed | Use a data cable; check that you flashed the file from `build_reef_ov5640` or `build_reef_rps` |
| The console stops at `Bringing up …`, or the video is black | The camera is not seated, or SW7 is not on CAM | Unplug USB-C, reseat the camera cable, set SW7 to CAM and power up again |
| Low frame rate at 1280×720 | USB Full-Speed bandwidth: busier scenes make bigger MJPEG frames | Use 640×360 (30 fps) |
| Rock-paper-scissors is mirrored the wrong way | The viewer mirrors the video as well | Type `rps mirror off` |
| A hand in the box does not start the countdown | Confidence below the threshold, or the hand is off-centre | Watch the results with `rps print on`; improve light and distance; try `rps conf 50` |
| No `[All Success]` from the flasher | Not in download mode, or `--chip-variant IPRO7AI` is missing | Enter download mode again; check the command |

## Next steps { #next-steps }

- [IPRO AI Teach](../teach/index.md): train a classifier on your own images and deploy it to the Reef (the image mode of `ipro_reef_teach` uses the same camera pipeline).
- [Camera & Imaging](../guides/camera.md): the image pipeline, ISP channels and supported sensors.
- [AI & NPU](../guides/ai-npu.md): NPU inference and models.
- [Wi-Fi and RTSP Camera Stream](wifi-rtsp.md): send the camera video over Wi-Fi with RTSP instead.
