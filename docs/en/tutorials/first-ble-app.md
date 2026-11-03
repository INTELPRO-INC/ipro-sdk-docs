---
title: "Your First BLE Application"
description: Run ipro_ble_remote on the IPRO7AI Reef EVK, flash it the first time with boot2 and the A/B partition table, drive its GATT services from a phone, rename the device, make it beep on connection, and update it over BLE OTA.
migrate_from:
  - "tutorials.html — 教學 1"
---

# Your First BLE Application

At the end of this tutorial the IPRO7AI Reef EVK runs the SDK's GATT reference application `ipro_ble_remote`: a phone can light the on-board RGB LED, receive key notifications and exchange text with the board. You then change the code so the board advertises as `IPRO-Hello` and beeps when a phone connects, and finally send new firmware to the board over BLE OTA, with no cable.

## Prerequisites { #prerequisites }

- An IPRO7AI Reef EVK with SW7 on CAM and SW8 on PWR, powered from USB-C, with an IPRO Debug Probe or a 3.3 V USB-UART cable on U6 (115200 8N1; wiring in [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md)). An OV5640 FLEX-24 camera module and a microSD card are optional, for the photo feature.
- [First FreeRTOS Application](../get-started/first-app-freertos.md) done: the toolchain is in `/opt/toolchain/riscv_ipro7/` and `make` builds SDK apps.
- IntelProCube v0.6.3, obtained separately: the command-line flasher `ipro_iot_tool_macos`, `ipro_iot_tool_linux` or `ipro_iot_tool.exe`, and the boot2 image that comes with it, `chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin`.
- A phone with either:
    - Android: the demo app shipped in the app directory, `apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk`.
    - Android or iOS: a BLE tool app that reads and writes GATT characteristics, such as nRF Connect or LightBlue. The steps below use such a tool.
- For BLE OTA (steps 10 to 12): a macOS or Linux computer with Bluetooth LE, Python 3 and the `bleak` package.

!!! note "The Reef build uses 2 MB of flash, boot2 and an A/B partition table"
    The Reef configuration of `ipro_ble_remote`, `defconfig_reef`, links for 2 MB of flash (`CONFIG_IPRO7_FLASH_2M=y`) and turns on BLE OTA (`CONFIG_IPRO_BLE_REMOTE_OTA=y`). Flashing must also write boot2 and the app's own A/B table `partition_cfg_2M_remote_ab.toml`: FW A (0x12000, 824 KB) is the execute slot and FW B (0xE0000, 512 KB) holds the OTA package. `build_freertos.sh` cannot pass `--boot2`, so this tutorial runs the flasher directly.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Build the Reef configuration.** From the SDK root:

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    `DEFCONFIG=` leaves `.config` untouched and builds in `build_reef/`. A successful build ends with the linker's memory table (the flash row shows `2 MB`); the output is `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`. A plain `make` without `DEFCONFIG=` builds the IPRO7 EVB version, which does not run on the Reef.

2. **Put the Reef in download mode.** Hold SW1 (BOOT), tap SW2 (RESET), release SW1. If the board already runs firmware with a shell, typing `reboot_dl` at the console does the same. In download mode the console prints nothing.

3. **Flash boot2, the A/B table and the firmware.** From the IntelProCube directory:

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin \
            --pt <SDK>/apps/bluetooth/ble/ipro_ble_remote/partition_cfg_2M_remote_ab.toml \
            --firmware <SDK>/apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --boot2 chips/ipro7/builtin_imgs/boot2_v0.5.2/ipro_boot2_IPRO7_v0.5.2.bin `
            --pt <SDK>\apps\bluetooth\ble\ipro_ble_remote\partition_cfg_2M_remote_ab.toml `
            --firmware <SDK>\apps\bluetooth\ble\ipro_ble_remote\build_reef\build_out\ipro_ble_remote_IPRO7.bin
        ```

    `--chip-variant IPRO7AI` selects the flash pins of the Reef (QFN56). The tool exits with 0 even when it fails, so check the output for `[All Success]`. With an IPRO Debug Probe, the port is the one whose name ends in `02`. Use this full command every time you reflash this app so that the A/B layout stays consistent.

4. **Open the console and reset.** Open the U6 port at 115200 baud (see [Flashing & Serial Console](../get-started/flash-and-monitor.md)) and tap SW2 (RESET). boot2 prints first, then the application (the level and time fields at the start of each line are left out):

    ```text
    [BOOT2] IPRO7 Boot2 v0.5.2
    ...
    REMOTE_APP: [BLE] Initialized
    REMOTE_APP: [BLE] All services initialized
    REMOTE_APP: [BLE] Advertising: IPRO-Remote
    ```

5. **Connect from the phone.**
    - With the shipped Android app: copy `ipro_remote_demo.apk` to the phone and open it to install (allow installs from unknown sources), or run `adb install apps/bluetooth/ble/ipro_ble_remote/ipro_remote_demo.apk` on your computer.
    - With a BLE tool app: scan for `IPRO-Remote` and connect.

    The console prints:

    ```text
    REMOTE_APP: Connected! Peer: <phone address>
    ```

6. **Use the GATT services.** In the BLE tool app, find these characteristics:

    | Action | Characteristic | Result on the board |
    |---|---|---|
    | Write `01` | LED State `0xFF11` | The WS2812 LED lights (white by default); the console prints `[LED] State: ON` |
    | Write `00 FF 00` | LED Colour `0xFF81` | The LED turns green (3 bytes: R, G, B) |
    | Enable notifications, press SW3 | Button State `0xFF21` | The phone receives `01` (press) and `00` (release) |
    | Enable notifications | UART TX `0xFF41` | The phone receives `Welcome to IPRO Remote!` |
    | Write the text `hello` | UART RX `0xFF42` | The console prints `[UART RX] hello`; the phone receives `Echo: hello` |
    | Write `E8 03 2C 01 1E` | Tone `0xFF84` | The speaker (or headphones in J2) plays 1 kHz for 300 ms (frequency and duration are little-endian u16, the last byte is the volume in %) |

    A short press on SW1 (BOOT) makes the app take a photo (camera required; with a microSD card it is also saved under `sd:/REMOTE/`), so test the keys with SW3, SW4 or SW5. The console command `reef status` shows the board, LED, camera and temperature state.

7. **Change the code.** Edit three places in `apps/bluetooth/ble/ipro_ble_remote/src/app/remote_app.c`.

    The top of the file already includes `remote_reef.h` inside a `CONFIG_IPRO7AI_REEF` block. Add `reef_hw.h`, which declares `reef_hw_tone()`, below it:

    ```c title="src/app/remote_app.c"
    #if defined(CONFIG_IPRO7AI_REEF)
    #include "remote_reef.h"
    #include "reef_hw.h"
    #endif
    ```

    Change the advertised name:

    ```c title="src/app/remote_app.c"
    #define DEVICE_NAME "IPRO-Hello"
    ```

    In `connected_cb()`, add the beep after the `Connected! Peer` log line:

    ```c title="src/app/remote_app.c"
        IPRO_LOGI(LOG_TAG, "Connected! Peer: %s", addr_str);

    #if defined(CONFIG_IPRO7AI_REEF)
        /* 1 kHz, 150 ms beep on the speaker and headphone jack when a phone connects */
        (void)reef_hw_tone(1000, 150, 30);
    #endif
    ```

    `reef_hw_tone()` only queues the request for the task that owns the Reef hardware and returns, so it is safe to call from a BLE connection callback. The app compiles with `-Werror`: any warning fails the build.

8. **Rebuild and flash.** Run the build command from step 1 again (only the changed file recompiles), type `reboot_dl` at the console and flash with the command from step 3.

9. **Connect again.** After tapping SW2, the console prints `REMOTE_APP: [BLE] Advertising: IPRO-Hello`. Scan again on the phone and connect to `IPRO-Hello`; the Reef beeps as the connection comes up.

10. **Set up the OTA tool.** From here on, updates go over BLE and U6 is not needed. In the SDK root, create a Python virtual environment with `bleak`:

    ```bash
    python3 -m venv .venv
    .venv/bin/pip install bleak
    ```

    Disconnect the phone first: the Reef build allows one connection only (`CONFIG_BT_CONN=1`).

11. **Build an OTA package.** Make any small change (for example, change the beep to `reef_hw_tone(2000, 150, 30)`), rebuild (step 1), then package the build as a boot2 OTA package. The script has IntelProCube build the combined image and compresses it with the SDK's `tools/create_ota.py`:

    === "macOS"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    === "Linux"

        ```bash
        IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_linux \
            sh apps/bluetooth/ble/ipro_ble_remote/tools/make_reef_ota.sh
        ```

    Output: `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota` (about 345 KB). OTA accepts only this `.xz.ota` package, never the `.bin`.

12. **Send it over BLE and check.** `reef_ota.py` looks for a device named `IPRO-Remote` by default; the board has been renamed, so set `REMOTE_NAME`:

    ```bash
    REMOTE_NAME=IPRO-Hello .venv/bin/python apps/bluetooth/ble/ipro_ble_remote/tools/reef_ota.py \
        apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_reef.xz.ota
    ```

    The tool prints the board's current version, the package size and CRC32, the transfer time and `verified, slot switched; rebooting`; after the board restarts it connects again and prints the new version:

    ```text
    running: <camera, SD card and build time>
    ipro_ble_remote_reef.xz.ota: <bytes> bytes, CRC32 <value>, <payload> bytes/packet
    sent in <seconds> s (<rate> KB/s)
    verified, slot switched; rebooting
    running: <new build time>
    ```

    Meanwhile the board's console prints `[OTA] START: …`, `[OTA] CRC32 OK! Switching partition...` and `[OTA] Ready to reboot`, and `[BOOT2] IPRO7 Boot2 v0.5.2` appears again on the restart: boot2 checks the package's SHA256 and unpacks it into FW A before it starts the app. INTELPRO measured 13 to 17 s for a 345 KB package on macOS with MTU 247. The shipped Android demo app can send the same `.xz.ota` package.

</div>

!!! danger "Do not OTA with the standard partition table"
    On the Reef, OTA works only with `partition_cfg_2M_remote_ab.toml`. If the board was flashed with IntelProCube's standard `partition_cfg_2M.toml`, an OTA writes its FW B (0x12A000) and switches to it, after which the board prints nothing at all and can only be recovered by reflashing in download mode.

## Verify { #verify }

- The console's advertising line shows `IPRO-Hello`, and so does the phone's scan list.
- The board beeps when the phone connects, and the console prints `Connected! Peer: …`.
- The LED, key and UART operations from step 6 still work.
- The final `running:` line from `reef_ota.py` shows the new build time, and on the next connection you hear the beep you changed in step 11.

The `Device Name: 'IPRO-Remote'` in the `main.c` boot banner is a fixed string and does not affect the advertised name.

## How it works { #how-it-works }

`main.c` initialises the platform and creates the `BLERemote` task, which calls `remote_app_init()`. BLE starts in a fixed order: the controller task, then the HCI driver, then the Zephyr host (from `src/app/remote_app.c`):

```c title="src/app/remote_app.c"
err = ipro_ble_ctlr_controller_init(configMAX_PRIORITIES - 1);  /* IPRO BLE controller */
vTaskDelay(pdMS_TO_TICKS(50));
err = hci_driver_ipro_ble_ctlr_init();                           /* HCI driver */
vTaskDelay(pdMS_TO_TICKS(50));
err = bt_enable(bt_ready_cb);                                    /* Zephyr host */
```

Once the host is ready, `bt_ready_cb()` calls `bt_set_name(DEVICE_NAME)`, registers the connection callbacks with `bt_conn_cb_register(&conn_callbacks)`, initialises the GATT services and starts connectable advertising. The services are defined statically with `BT_GATT_SERVICE_DEFINE()` in `src/services/remote_services.c`. The advertising data and parameters are below; `DEVICE_NAME` feeds both the advertising data and `bt_set_name()`:

```c title="src/app/remote_app.c"
static const struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
    BT_DATA(BT_DATA_NAME_COMPLETE, DEVICE_NAME, DEVICE_NAME_LEN),
};

struct bt_le_adv_param adv_param = {
    .id = BT_ID_DEFAULT,
    .options = BT_LE_ADV_OPT_CONN,
    .interval_min = 160,  /* 100ms (N * 0.625ms) */
    .interval_max = 320,  /* 200ms */
};
int err = bt_le_adv_start(&adv_param, ad, ARRAY_SIZE(ad), sd, ARRAY_SIZE(sd));
```

The Reef build adds two services: OTA `0xFF60` (control `0xFF61`, data `0xFF62`, status `0xFF63`) and the Reef hardware service `0xFF80` (LED Colour `0xFF81`, Key Event `0xFF82`, Sound Level `0xFF83`, Tone `0xFF84`, Board Info `0xFF85`). The LED, key, speaker, SD card and camera drivers are the out-of-box firmware's sources in `apps/platform/ipro7ai_reef_demo/src`, used in place; `src/board/reef_hw.c` is the only task that touches that hardware, and the BLE callbacks only post requests to it.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| No `[All Success]` in the flasher output, or `flash jedec id: 00000000` | The board is not in download mode, or the flash pins are wrong | Enter download mode first; check that the command has `--chip-variant IPRO7AI` |
| Flashing succeeds but the console stays silent | boot2 and the A/B table were not written, or the baud rate is wrong | Reflash with the full command from step 3; set the console to 115200 |
| The phone still shows `IPRO-Remote` | The phone cached the old name | Check that the console advertises `IPRO-Hello`, then turn the phone's Bluetooth off and on and scan again |
| No LED or no beep | The WS2812 and the speaker amplifier run from USB VBUS; headphones in J2 mute the speaker | Power from USB-C, not from 3.3 V alone; unplug the headphones or listen on them |
| The build fails on a warning | The app compiles with `-Werror` | Keep `#include "reef_hw.h"` inside the `CONFIG_IPRO7AI_REEF` block and the call inside the function |
| `make_reef_ota.sh` prints `IntelProCube tool not found` | `IPRO_FLASH_TOOL` is unset and the flasher is not on PATH | Set `IPRO_FLASH_TOOL=<IntelProCube>/ipro_iot_tool_macos` (or `_linux`) |
| `make_reef_ota.sh` prints `build first: …` | There is no build in `build_reef/` yet | Run step 1 first |
| `reef_ota.py` prints `IPRO-Remote not found` | The board was renamed, a phone is connected, or the computer's Bluetooth is off or not allowed | Set `REMOTE_NAME=IPRO-Hello`; disconnect the phone; on macOS, allow the terminal to use Bluetooth |
| `reef_ota.py` prints `device error …` | The board rejected the package or a write failed | Check that you sent the `.xz.ota`; read the `[OTA]` lines on the console |
| The board does not come back after OTA | When boot2 rejects a package it stays in its USB rescue mode | Enter download mode and reflash with the command from step 3 |

## Next steps { #next-steps }

- [BLE Throughput Test](ble-throughput.md): measure the data rate between two Reef boards.
- [Getting Started with LE Audio](le-audio.md): run the LE Audio headset example on the Reef.
- [BLE Development](../guides/ble.md): controller library selection, host configuration and APIs.
- [OTA Updates](../guides/ota.md): partition tables, the OTA package format and boot2's update flow.
