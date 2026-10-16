---
title: "Your First BLE Application"
description: Run ipro_ble_remote on the IPRO7AI Reef EVK, drive its GATT services from a phone, then rename the device and make it beep when a phone connects.
migrate_from:
  - "tutorials.html — 教學 1"
---

# Your First BLE Application

By the end of this tutorial your IPRO7AI Reef EVK runs `ipro_ble_remote`, the SDK's GATT reference application: a phone can switch on the board's RGB LED, receive key notifications and exchange text with the board. You then change the code so the board advertises as `IPRO-Hello` and beeps when a phone connects.

## Prerequisites { #prerequisites }

- IPRO7AI Reef EVK with JP1 fitted before power-on, powered over USB-C, and a USB-to-UART cable on connector U6 (115200 8N1). See [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md).
- [First FreeRTOS Application](../get-started/first-app-freertos.md) completed: the toolchain is in `/opt/toolchain/riscv_ipro7/` and `make` builds SDK applications.
- The IntelProCube v0.6.3 command-line flash tool (`ipro_iot_tool_macos`, `ipro_iot_tool_linux` or `ipro_iot_tool.exe`), obtained separately.
- A phone with a BLE tool app that can read and write GATT characteristics, such as nRF Connect or LightBlue.

!!! note "The Reef configuration uses 2 MB of flash and an A/B partition table"
    The Reef configuration of `ipro_ble_remote`, `defconfig_reef`, links for 2 MB of flash (`CONFIG_IPRO7_FLASH_2M=y`) and enables BLE OTA. The first flash therefore also writes boot2 and the application's own A/B partition table, `partition_cfg_2M_remote_ab.toml`.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Build the Reef configuration** from the SDK root:

    ```bash
    make -C apps/bluetooth/ble/ipro_ble_remote DEFCONFIG=defconfig_reef
    ```

    `DEFCONFIG=` leaves `.config` untouched and builds in `build_reef/`. A successful build ends with the linker's memory usage table; the output is `apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote_IPRO7.bin`.

2. **Put the Reef in download mode**: hold SW1 (BOOT), tap SW2 (RESET), then release SW1. If the board already runs firmware with a shell, you can type `reboot_dl` at the console instead.

3. **Flash for the first time (boot2, A/B partition table and firmware)**: run from the IntelProCube directory:

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

    `--chip-variant IPRO7AI` selects the flash pins of the Reef's QFN56 package. The tool exits with 0 even when it fails, so check its output for `[All Success]`.

4. **Open the console and reset**: open the U6 serial port at 115200 baud (see [Flashing & Serial Console](../get-started/flash-and-monitor.md)) and tap SW2 (RESET). boot2 prints first, then the application starts (level, time and thread fields at the start of each line are omitted here):

    ```text
    [BOOT2] IPRO7 Boot2 v0.5.2
    ...
    REMOTE_APP: [BLE] Initialized
    REMOTE_APP: [BLE] All services initialized
    REMOTE_APP: [BLE] Advertising: IPRO-Remote
    ```

5. **Connect from the phone**: scan for `IPRO-Remote` in the BLE tool app and connect. The console prints:

    ```text
    REMOTE_APP: Connected! Peer: <phone address>
    ```

6. **Use the GATT services**: find these characteristics in the app:

    | Action | Characteristic | Result on the board |
    |---|---|---|
    | Write `01` | LED State `0xFF11` | The WS2812 LED lights up (white by default); the console prints `[LED] State: ON` |
    | Write `00 FF 00` | LED Colour `0xFF81` | The LED turns green (3 bytes: R, G, B) |
    | Enable notifications, press SW3 | Button State `0xFF21` | The phone receives `01` (pressed) and `00` (released) |
    | Enable notifications | UART TX `0xFF41` | The phone receives `Welcome to IPRO Remote!` |
    | Write the text `hello` | UART RX `0xFF42` | The console prints `[UART RX] hello`; the phone receives `Echo: hello` |

    A short press on SW1 (BOOT) makes the application take a photo, so test the keys with SW3, SW4 or SW5.

7. **Change the code**: edit three places in `apps/bluetooth/ble/ipro_ble_remote/src/app/remote_app.c`.

    Include the Reef hardware interface:

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

    In `connected_cb()`, add the beep right after the `Connected! Peer` log line:

    ```c title="src/app/remote_app.c"
        IPRO_LOGI(LOG_TAG, "Connected! Peer: %s", addr_str);

    #if defined(CONFIG_IPRO7AI_REEF)
        /* 1 kHz, 150 ms beep on the speaker and headphone jack when a phone connects */
        (void)reef_hw_tone(1000, 150, 30);
    #endif
    ```

    `reef_hw_tone()` only posts the request to the Reef hardware worker task and returns, so it is safe to call from a BLE connection callback. The application is compiled with `-Werror`: any warning fails the build.

8. **Rebuild and flash**: run the build command from step 1 again (only the changed file is recompiled), enter download mode and flash with the command from step 3.

9. **Connect again**: after a reset the console prints `REMOTE_APP: [BLE] Advertising: IPRO-Hello`. Rescan on the phone and connect to `IPRO-Hello`; the Reef beeps as soon as the link is up.

</div>

## Verify { #verify }

- The console's advertising message shows `IPRO-Hello`, and so does the phone's scan list.
- You hear a beep when the phone connects, and the console prints `Connected! Peer: …`.
- The LED, key and UART operations from step 6 still work.

The `Device Name: 'IPRO-Remote'` line in the boot banner of `main.c` is a fixed string and does not affect the advertised name.

## How it works { #how-it-works }

After platform initialization, `main.c` creates the `BLERemote` task, which calls `remote_app_init()`. BLE comes up in a fixed order: the controller task first, then the HCI driver, then the Zephyr host (from `src/app/remote_app.c`):

```c title="src/app/remote_app.c"
err = ipro_ble_ctlr_controller_init(configMAX_PRIORITIES - 1);  /* IPRO BLE controller */
vTaskDelay(pdMS_TO_TICKS(50));
err = hci_driver_ipro_ble_ctlr_init();                           /* HCI driver */
vTaskDelay(pdMS_TO_TICKS(50));
err = bt_enable(bt_ready_cb);                                    /* Zephyr host */
```

Once the host is ready, `bt_ready_cb()` calls `bt_set_name(DEVICE_NAME)`, registers the connection callbacks with `bt_conn_cb_register(&conn_callbacks)`, initializes the GATT services and starts connectable advertising. The services are defined statically with `BT_GATT_SERVICE_DEFINE()` in `src/services/remote_services.c`. The advertising data and parameters look like this; `DEVICE_NAME` feeds both the advertising data and `bt_set_name()`:

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

For your own advertising, reuse a `struct bt_le_adv_param` like the one above or one of the host's macros, such as `BT_LE_ADV_CONN_FAST_1`.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| No `[All Success]` in the flash output, or `flash jedec id: 00000000` | Wrong flash pin setting | Make sure the command has `--chip-variant IPRO7AI` and the board is in download mode |
| Flashing succeeds but the console stays silent | boot2 and the A/B partition table were not written, or the baud rate is wrong | Flash again with the full command from step 3; set the console to 115200 |
| The phone still shows `IPRO-Remote` | The phone cached the old name | Check that the console advertises `IPRO-Hello`, turn the phone's Bluetooth off and on, and scan again |
| No LED or no beep | The WS2812 and the speaker amplifier run from USB VBUS | Power the board over USB-C, not from 3V3 alone |
| The build fails on a warning | The application is compiled with `-Werror` | Keep `#include "reef_hw.h"` inside the `CONFIG_IPRO7AI_REEF` condition and the call inside the function |

## Next steps { #next-steps }

- [Build and Flash Workflow](build-and-flash.md): speed up the daily build, flash and monitor loop.
- [BLE Throughput Test](ble-throughput.md): measure data rates between two Reef boards.
- [BLE Development](../guides/ble.md): controller library selection, host configuration and APIs.
- [OTA Updates](../guides/ota.md): the Reef configuration of `ipro_ble_remote` already includes BLE A/B OTA; the application's README describes how to use it.
