---
title: ipro7ai_reef_demo
description: Reef 出厂固件：RGB LED、按键、扬声器与耳机、PDM 与耳麦麦克风、microSD、OV5640 摄像头各有一组 shell 命令；mic usb 让开发板成为 USB 麦克风，mic sdrec 把录音保存为 SD 卡上的 WAV 文件
generated: tools/gen_examples.py
migrate_from: []
---

# ipro7ai_reef_demo

Reef 出厂固件：RGB LED、按键、扬声器与耳机、PDM 与耳麦麦克风、microSD、OV5640 摄像头各有一组 shell 命令；`mic usb` 让开发板成为 USB 麦克风，`mic sdrec` 把录音保存为 SD 卡上的 WAV 文件

| 项目 | 内容 |
|---|---|
| 源代码 | [`apps/platform/ipro7ai_reef_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.1/apps/platform/ipro7ai_reef_demo) |
| 开发板与配置 | Reef（`.config`）；Reef＋IPRO6S FIN 卡（`defconfig_wifi_ipro6s`：Wi-Fi 与 RTSP 摄像头视频流） |
| 控制台 | UART 115200 |
| 构建 | `make -C apps/platform/ipro7ai_reef_demo`；Wi-Fi 版加上 `DEFCONFIG=defconfig_wifi_ipro6s` |

## 在 Reef 上运行 { #on-the-reef }

SW7 拨到 CAM、SW8 拨到 PWR，U6 接上控制台线，USB-C 供电（见 [Reef 快速上手](../hardware/boards/reef-evk.md#quick-start)）。

<div class="ipro-steps" markdown>

1. **构建**：在 SDK 根目录执行

    ```bash
    make -C apps/platform/ipro7ai_reef_demo
    ```

    结尾打印 Flash 与 RAM 用量，镜像位于 `apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin`。

2. **烧录**：让开发板进入[下载模式](../hardware/boards/reef-evk.md#download-mode)（按住 SW1，按一下 SW2，松开 SW1），在 IntelProCube 目录执行

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --pt chips/ipro7/partition/partition_cfg_2M.toml \
        --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
    ```

    输出中出现 `[All Success]` 才算成功（工具失败时也以 0 退出）。按一下 SW2 启动新固件。

3. **运行**：以 115200 baud 打开控制台，输入 `reef selftest`。

    开机时 RGB LED 呼吸一次蓝光；`reef selftest` 约 3 秒内依次点亮红、绿、蓝光，扬声器发出 1 kHz 测试音，再检查 SD 卡检测与摄像头。按 SW3、SW4、SW5、SW1 分别亮红、绿、蓝、白光。

</div>

一次完成构建、烧录与控制台（开发板上已有 SDK 固件时会自动发送 `reboot_dl`）：

```bash
export IPRO_FLASH_TOOL=<ICUBE>/ipro_iot_tool_macos
./build_freertos.sh -p /dev/cu.usbserial-XXXX \
    -P <ICUBE>/chips/ipro7/partition/partition_cfg_2M.toml \
    build flash monitor ipro7ai_reef_demo
```

Wi-Fi 与 RTSP 版以 `DEFCONFIG=defconfig_wifi_ipro6s` 构建，输出在 `build_wifi_ipro6s/build_out/`，需要运行 `ipro6_if_wifi` 固件的 IPRO6S FIN 卡，步骤见 [Wi-Fi 与 RTSP 摄像头视频流](../tutorials/wifi-rtsp.md)。这个配置不含 USB 设备，没有 `mic usb`。命令总表见 [Reef 出厂固件](../hardware/boards/reef-evk.md#reef-demo)。

## README { #readme }

!!! note "README 原文"
    以下是应用附带的 README（SDK V2.2.1），保留原文、未翻译；只替换了不适合公开的内容。

<!-- verbatim:start -->

Out-of-box firmware for the **IPRO7AI Reef EVK**: one shell command per block
on the board, including a headless OV5640 / OV2640 camera stream, and in the
`defconfig_wifi_ipro6s` build Wi-Fi through the IPRO6S_FIN with an RTSP stream
of the camera. Board support: `bsp/board/ipro7/ipro7ai_reef_board_config.h`
(`CONFIG_IPRO7AI_REEF`). The full pin map, power tree and jumpers are in the
IPRO7AI Reef EVK Board User Guide.

This is a different board from `ipro7ai_evk_demo` (the SoM sub-board with the
ST7789 LCD and SC101IOT camera). On the Reef the IPRO7AI QFN56 sits directly on
the carrier; there is no LCD, no battery, and the camera connector is the
24-pin OmniVision FLEX-24 (OV5640 / OV2640 modules).

### Build / flash

```bash
make -C apps/platform/ipro7ai_reef_demo                                  # -> build/build_out/ipro7ai_reef_demo_IPRO7.bin
make -C apps/platform/ipro7ai_reef_demo DEFCONFIG=defconfig_wifi_ipro6s  # + Wi-Fi and RTSP -> build_wifi_ipro6s/build_out/
```

Flash with the command-line tool of IntelProCube (`ipro_iot_tool.exe`,
`ipro_iot_tool_macos` or `ipro_iot_tool_linux`), run from the IntelProCube
directory:

```bash
ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI --port /dev/cu.usbserial-XXXX \
    --baudrate 921600 --pt chips/ipro7/partition/partition_cfg_2M.toml \
    --firmware <SDK>/apps/platform/ipro7ai_reef_demo/build/build_out/ipro7ai_reef_demo_IPRO7.bin
```

`--chip-variant IPRO7AI` selects the QFN56 flash pins. The tool exits 0 even
when flashing fails, so look for `[All Success]` in its output.

Console: 115200 8N1 on the U6 SH1.0 wafer (GPIO20 TX / GPIO21 RX). The wafer's
DTR and RTS pull BOOT (GPIO41) and RESET through 1 k, so an auto-download
cable works; by hand it is hold **SW1** (BOOT), tap **SW2** (RESET).

### Before powering up

On the V4.0 board (silkscreen "IPRO7AI REEF EVK V4.0"):

| Switch / jumper | Setting |
|---|---|
| SW7 | CAM: the camera pins go to the camera connector (GPIO routes them to the J_IO header instead). |
| SW8 | PWR for normal use; MEAS only with a current meter or a 3.3 V supply on JP2. |
| JP3 | ON = SD_VDD always on. GPIO = switched by GPIO14; use this with the IPRO6S_FIN so `fin cycle` works. |

On the earlier V3.0 board: JP1 must be fitted (VDDIO1 1-2 = 3.3 V, or the
camera, USB and BOOT bank is unpowered), JP2 on 1-2, and JP3 on 2-3 for the
IPRO6S_FIN.

Power is USB-C only. The WS2812 and the class-D amplifier run from VBUS, so
a current-limited bench supply on 3V3 alone leaves the LED and speaker dead.

### What happens at power-on

1. Camera parked (PWDN high, RESETB low, XCLK off).
2. RGB LED breathes blue once, then off.
3. Keys drive the LED: SW3 red, SW4 green, SW5 blue, BOOT white.
4. Shell prompt. `reef selftest` runs LED, a 1 kHz tone on the speaker, the
    slot detect and the camera probe in ~3 s.

### Shell commands

```
reef status                    pins, key states, LED, amp, detect lines
reef selftest                  LED r/g/b, 1 kHz 300 ms, SD detect, cam probe

led <r> <g> <b>                WS2812 colour (0..255), e.g. led 40 0 0
led rainbow [sec] | led off | led status

btn status                     debounced state + press counts
btn watch [sec]                print press/release events

spk tone <hz> <ms> [amp%] [hp] sine on DAC A; 'hp' keeps the amplifier muted
spk on | spk off | spk stop | spk status

mic rec <pdm|headset|aux> <s>  record up to 10 s at 16 kHz into PSRAM
mic play [hp]                  play it back (+20 dB make-up by default)
mic loop <src> [sec] [hp]      live monitor; omit sec for "until mic stop"
mic sdrec <src> <name> <s>     record up to 2 h to sd:/rec/<name>.wav (LED red while it runs)
mic usb <src>                  USB microphone on the board's own USB-C until `mic stop` (LED red)
mic gain <db> | mic ch <0|1> | mic stop | mic status

sd status | sd mount | sd ls [path] | sd test | sd unmount
sd bench [kib]                 write, read back and verify (default 1024 KiB)
sd power on|off|cycle          SD_VDD gate on GPIO14 (JP3 2-3)

fin                            IPRO6S_FIN slot status
fin cycle | fin power on|off   power-cycle the fin (JP3 2-3)

cam probe                      power sequence + SCCB through components/sensor
cam start | cam stop           YUV422 -> ISP ch0 (1/4 size YUYV in PSRAM)
cam status                     frames, measured fps, sync/fifo errors, mean luma
cam snap [cols]                ASCII thumbnail of the latest frame
cam bar on|off                 sensor colour bars - proves the pipeline without optics
cam reg <addr> [val]           sensor register (OV2640: 0x1xx = sensor bank)
cam order lower|higher         DVP byte order (next start)
cam sync <high|low> <high|low> VSYNC / HSYNC polarity (next start)
cam pins [ms]                  DVP pad activity: edges/s and duty per pin
cam park | cam xclk on|off

hp                             read the jack-detect level on GPIO26
```

### How each block is wired

| Block | Pins | Notes |
|---|---|---|
| RGB LED | DI GPIO24 | Driven from SPI0 MOSI: 4 SPI bits per WS2812 bit at 3.2 MHz. GPIO24 % 4 == 0 is MOSI with `pin_swap_enable = 0` (the SDK default swap 1 makes it MISO and the LED stays dark). Supply is VBUS − D3. |
| Keys | SW1 41 (**active high**), SW3 10, SW4 27, SW5 11 | Polled at 10 ms, 30 ms debounce. SW3/SW5 are released while AUX-IN captures. |
| Speaker | DAC A GPIO23 → PAM8302A, SD# GPIO25 | Enable is **active high**; the board header's `BOARD_SPK_EN_ACTIVE 1` is honoured by `audio_output_dac.c`. Gain 30 V/V — the demo defaults to 20 % amplitude. |
| Headphone | same DAC → TLV9061 → J2 (PJ-342, OMTP) | Always connected; `hp` in a command just mutes the amp. Detect GPIO26 LOW = plugged. |
| PDM mic | CLK 16, DATA 17 | MSM261DGT003 on 3V3, L/R = GND → left slot (`mic ch 1` to try the other). Runs at about 15,872 Hz, not 16,000; `mic sdrec` writes the measured rate into the WAV header; `mic usb` converts to the host's 16,000 Hz (`audio_asrc` holding the UAC queue). |
| Headset mic | AIN7 (GPIO13) +, AIN6 (GPIO12) − | Differential AUADC, 24 dB PGA. Bias 2.2 k to 3V3 on the jack. |
| AUX-IN | AIN4 (GPIO10) L, AIN5 (GPIO11) R | Single-ended, 6 dB PGA, left channel only in this demo. |
| SD slot | 28–33 on SDH_0, DET 15, PWR 14 | 4-bit FatFS at `sd:`. DET low = seated. PWR low = on (reset default). |
| Camera | D0-7 = 0-7, PCLK 38, VSYNC 39, HREF 40, XCLK 22, RST 34, PWDN 35, SCCB 36/37 | OV5640 / OV2640 YUV422 720p → ISP ch0, see below. |

### Camera

`components/sensor/ov5640.c` and `ov2640.c` (`CONFIG_SENSOR_OV5640` /
`CONFIG_SENSOR_OV2640`, opt-in) drive the FLEX-24 module in YUV422 YUYV at
1280x720 — OV5640 2x-binned through a 16:9 window, OV2640 from its UXGA base
through a 1600x900 window and DSP scaler. Both keep AEC/AGC/AWB on the sensor,
so the demo never starts the ISP firmware's imgproc 3A (the descriptor hooks
it would call are no-ops).

There is no display, so `cam start` runs the ISP with channel 0 only: YUYV
scaled 4x down (320x180) into a PSRAM ping-pong pair, counted in the ISP
callback. `cam status` gives frames, fps, the ISP's VSYNC/HSYNC/FIFO error
counters and the mean luma; `cam snap` prints the frame as ASCII; `cam bar on`
switches the sensor to colour bars so the pipeline can be judged without
lens or light.

The bring-up sequence: `cam probe` (identity over SCCB), `cam start`,
`cam status` twice a second apart (frames climbing, errors flat), `cam bar on`
then `cam snap` (vertical bands), `cam bar off`, `cam snap` (the scene).

If the camera does not stream, these are the things to check:

- The DVP pixel clock. `hal_isp` sizes the DVP_AS FIFO threshold as
    `width x (1 - (pclk/2) / BCLK) + 10` (BCLK 96 MHz, FIFO 1024 entries), so a
    720p stream needs a DVP PCLK of at least ~40 MHz. Below that `isp_init`
    prints `[WARN] dvp as threshold over 1024` and the ISP delivers 0 frames
    with 0 errors. The descriptor `pclk` must be the real DVP PCLK - reporting
    low is not the safe side. The OV5640 driver runs an 84 MHz DVP PCLK with
    OmniVision's 720p line timing: 30 fps, down to 15 in dim light.
- Orientation: the Reef's OV5640 module reads out top-to-bottom mirrored.
    `cam.c` flips in the capture DMA (DVP2AXI flip mode, `CAM_DVP_VFLIP`), not
    in the sensor - sensor flip / mirror in the binned mode puts the demosaic a
    Bayer phase off. Flip mode writes the first line at the start address and
    each next one a line lower, so the DMA is given the buffer's last line.
- Whether anything reaches the SoC at all. `cam pins [ms]` samples D0-7,
    PCLK, VSYNC and HREF (rising edges per second, duty): VSYNC edges/s is the
    sensor frame rate, HREF edges/s the line rate, HREF duty tells the DVP
    clock against the line length. It switches the pads to plain GPIO inputs
    for the measurement (with the camera function selected they read 0) and
    hands them back to the camera block after.
- Sync polarity and byte order. VSYNC/HSYNC errors that climb with the frame
    count mean the polarity is wrong: `cam sync low high` / `cam sync high low`
    and restart. A picture with Y/UV swapped (grey-green, doubled edges in
    `cam snap`) means `cam order higher`.
- Whether `camera_module_init()`'s 8-bit SCCB scan sees the OV5640 (16-bit
    registers). It should — the scan only needs the address ACK — and if it
    does not, `cam probe` says so: it re-reads both OmniVision IDs directly and
    logs "framework scan missed it" when the sensor is there after all.

### Wi-Fi and RTSP (`defconfig_wifi_ipro6s`)

The IPRO6S_FIN is an SDIO slave on the card slot's six lines, powered from
SD_VDD. It runs the IPRO6S `ipro6_if_wifi` firmware (SDIO profile):
`make -C apps/platform/ipro6_if_wifi DEFCONFIG=defconfig_ipro6_sdio`. With JP3 on 2-3
(GPIO on the V4.0 board), `fin cycle` power-cycles it through
GPIO14. The
`defconfig_wifi_ipro6s` build adds the host side (`components/network/ipronet_host`
over SDIO, lwIP) and an RTSP MJPEG stream of the camera
(`components/network/rtsp_server`):

```
ipronet_up [<ssid> <psk>]      ipronet_start() on the fin, then ipronet_connect() if given an AP
ipronet_down                   ipronet_stop()
ipro6s_scan | ipro6s_scan_last scan for APs; print the last result
ipro6s_connect <ssid> <psk>    associate and run DHCP
ipro6s_link_status             STA link status
ipro6s_disconnect              disconnect from the AP
rtsp_cam on [fps] | off | stats  camera stream at rtsp://<ip>:8554/av0_0 (ch0 at sensor / 2)
ipro6s_ota <http url>          update the IPRO6S_FIN firmware over HTTP
```

`apps/platform/ipro7_sdio_wifi` is the stand-alone Wi-Fi reference app; build it
with `CONFIG_IPRO7AI_REEF=y` to run it on this board.

<!-- verbatim:end -->
