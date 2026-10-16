---
title: "Getting Started with LE Audio"
description: Run the LE Audio unicast headset ipro_le_audio_headset on the IPRO7AI Reef EVK, pair it with a phone, change the volume from the keys, and learn the key settings and the Zephyr broadcast samples.
migrate_from:
  - "tutorials.html — 教學 4"
---

# Getting Started with LE Audio

By the end of this tutorial your IPRO7AI Reef EVK runs `ipro_le_audio_headset`: it advertises as `IPRO-LE-Audio`, pairs with an LE Audio phone, offers the PACS, ASCS and VCP services among others, and sends decoded LC3 audio to the board's speaker and headphone jack. You also change the VCP volume from the board's keys and learn which settings an LE Audio application needs.

!!! abstract "LE Audio in V2.1.0"
    - FreeRTOS: `ipro_le_audio_headset`, an LE Audio unicast headset (BAP unicast server) for the IPRO7 EVB and the IPRO7AI Reef EVK.
    - Zephyr: BIS broadcast source, broadcast sink and unicast headset samples under `zephyr/samples/`; see [Zephyr samples](#zephyr-samples).
    - Standalone FreeRTOS BIS broadcast source and sink applications: not included in V2.1.0; contact INTELPRO.
    - The controller must use the `bt54_iso2` library with `CONFIG_EM_SIZE=32`.

## Prerequisites { #prerequisites }

- IPRO7AI Reef EVK with JP1 fitted before power-on, powered over USB-C, and a USB-to-UART cable on U6 (115200 8N1). Headphones on J2 are optional.
- [First FreeRTOS Application](../get-started/first-app-freertos.md) done, and the IntelProCube v0.6.3 command-line flash tool at hand.
- A serial terminal in which you can type commands (see [Flashing & Serial Console](../get-started/flash-and-monitor.md)).
- An Android phone that supports LE Audio, with LE Audio switched on.

## Steps { #steps }

<div class="ipro-steps" markdown>

1. **Build the Reef configuration**:

    ```bash
    make -C apps/bluetooth/le_audio/ipro_le_audio_headset DEFCONFIG=defconfig_reef
    ```

    Output: `apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin`. This configuration links for 2 MB of flash (`CONFIG_IPRO7_FLASH_2M=y`); for the Reef's in-package flash size, see [IPRO7AI Reef EVK](../hardware/boards/reef-evk.md#bsp).

2. **Flash**: put the Reef in download mode (hold SW1, tap SW2, release SW1), then run from the IntelProCube directory:

    === "macOS"

        ```bash
        ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/cu.usbserial-XXXX --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Linux"

        ```bash
        ./ipro_iot_tool_linux --chipname ipro7 --chip-variant IPRO7AI \
            --port /dev/ttyUSB0 --baudrate 921600 \
            --pt chips/ipro7/partition/partition_cfg_2M.toml \
            --firmware <SDK>/apps/bluetooth/le_audio/ipro_le_audio_headset/build_reef/build_out/ipro_le_audio_headset_IPRO7.bin
        ```

    === "Windows"

        ```powershell
        .\ipro_iot_tool.exe --chipname ipro7 --chip-variant IPRO7AI `
            --port COM5 --baudrate 921600 `
            --pt chips/ipro7/partition/partition_cfg_2M.toml `
            --firmware <SDK>\apps\bluetooth\le_audio\ipro_le_audio_headset\build_reef\build_out\ipro_le_audio_headset_IPRO7.bin
        ```

    Check the output for `[All Success]`.

3. **Open the console and reset**: open the console at 115200 baud and tap SW2. The boot log includes these lines (level, time and thread fields omitted):

    ```text
    MAIN: IPRO LE Audio Headset v2.0 (Zephyr blestack)
    ...
    BLE_INIT: Advertising started: IPRO-LE-Audio
    KEYS: Keys: SW3 vol-, SW4 vol+, SW5 mute (GPIO<n>/<n>/<n>)
    ```

4. **Check the audio output**: type the command below to play a 1 kHz test tone for 3 seconds. With headphones in J2 the speaker amplifier is off and the tone plays only in the headphones.

    ```text
    test_tone 3
    ```

5. **Pair the phone**: in the phone's Bluetooth settings, pair a new device and pick `IPRO-LE-Audio`. The console prints:

    ```text
    BLE_INIT: Connected: <phone address>
    BLE_INIT: Security requested: level 2
    BLE_INIT: Security changed: <phone address> level <n>
    BLE_INIT: [SMP] Pairing complete: <phone address>, bonded=1
    ```

    The phone lists the board as an LE Audio device. The bond is stored in flash and survives a reboot.

6. **Change the volume from the keys**: SW4 turns the volume up, SW3 down, and SW5 toggles mute. The keys go through the VCP volume renderer, so the volume slider on a connected phone follows. The console prints:

    ```text
    VCP_SERVER: Volume state changed: volume=<0-255> mute=<0|1>
    ```

    Type `vol` to see the current volume.

7. **Check the status**:

    ```text
    leaudio_status
    ```

    It shows `BLE Ready`, the counts of received and decoded audio frames, the current sample rate and the output (`DAC (Speaker)`).

</div>

!!! info "Streaming music from a phone"
    According to the application's README in V2.1.0, phone connection, pairing, LE Audio service discovery and VCP volume control are verified; streaming music from a phone is not yet validated. When a source sets up a stream, the console prints `Stream … started (Streaming state)` and `Frames Received` in `leaudio_status` keeps rising.

## Verify { #verify }

- The console prints `Advertising started: IPRO-LE-Audio`, and `test_tone 3` is audible.
- The phone pairs and the console prints `Pairing complete: …, bonded=1`. The services the phone discovers include CAS (`0x1853`), PACS (`0x1850`), ASCS (`0x184E`) and VCS (`0x1844`).
- Pressing SW3, SW4 or SW5 prints `Volume state changed` on the console, and the phone's volume slider moves with it.

## Key settings { #configuration }

LE Audio needs a controller library with ISO support and a larger Exchange Memory; on the host, you enable the profiles for your role. This excerpt is from `defconfig_reef`:

```ini title="apps/bluetooth/le_audio/ipro_le_audio_headset/defconfig_reef (excerpt)"
# Controller: peripheral ACL plus two ISO streams, Bluetooth 5.4 feature set
CONFIG_IPRO_BLE_CTLR_LIB="link1_periph"
CONFIG_IPRO_BLE_CTLR_FEATURE="bt54_iso2"
CONFIG_IPRO_BLE_CTLR_CFG_DBG=y
CONFIG_EM_SIZE=32
CONFIG_BT_CONN=1

# Pairing and bonding
CONFIG_BT_SMP=y
CONFIG_BT_SETTINGS=y
CONFIG_BT_BONDABLE=y

# LE Audio profiles
CONFIG_BT_AUDIO=y
CONFIG_BT_AUDIO_RX=y
CONFIG_BT_BAP_UNICAST_SERVER=y
CONFIG_BT_PACS=y
CONFIG_BT_ASCS=y
CONFIG_BT_VCP_VOL_REND=y
CONFIG_BT_CAP_ACCEPTOR=y
CONFIG_BT_CSIP_SET_MEMBER=y

# ISO channels
CONFIG_BT_ISO=y
CONFIG_BT_ISO_RX=y
CONFIG_BT_ISO_PERIPHERAL=y

# LC3 codec (prebuilt) and DAC output
CONFIG_COMPONENTS_LC3_ENABLE=y
CONFIG_BSP_USING_DAC=y
```

- `bt54_iso2` needs `CONFIG_EM_SIZE` of at least 32; otherwise the build stops at the configure step.
- `CONFIG_IPRO_BLE_CTLR_CFG_DBG=y` selects the debug controller library; without it the `_release` library is used.
- This application does not enable media control (MCP) or call control (CCP).

The application ships three output configurations:

| File | Board | Decoded audio goes to |
|---|---|---|
| `.config` (DAC output, same as `DAC.config`) | IPRO7 EVB | The on-chip DAC and a speaker |
| `UAC.config` | IPRO7 EVB | The host computer, as a 48 kHz mono USB microphone (USB Audio Class) |
| `defconfig_reef` | IPRO7AI Reef EVK | The DAC, to the speaker and the J2 headphone jack; SW3, SW4 and SW5 control the volume |

Switch to `DAC.config` or `UAC.config` by copying it over `.config` and doing a clean build, as their headers say (see [Build and Flash Workflow](build-and-flash.md#variants)).

## LE Audio terms { #concepts }

| Term | Meaning | In `ipro_le_audio_headset` |
|---|---|---|
| CIS | Connected isochronous stream, one to one, used by headsets | Receiving end |
| BIS | Broadcast isochronous stream, one to many (Auracast) | Not used; see the Zephyr broadcast samples |
| BAP | Sets up and manages audio streams | Unicast server with 2 sink ASEs |
| PACS | Publishes the supported codec capabilities | LC3: 16 / 32 / 48 kHz, 7.5 / 10 ms, mono, 26–155 octets per frame |
| ASCS | Configuration and state of the audio stream endpoints (ASEs) | Enabled |
| VCP | Volume control | Volume renderer |
| CAP / CSIP | Common audio profile / coordinated set | CAP acceptor and CSIP set member |
| LC3 | The standard LE Audio codec | Prebuilt library |

## Zephyr samples { #zephyr-samples }

The V2.1.0 Zephyr port adds three LE Audio samples: the BIS broadcast source `bap_broadcast_source`, the broadcast sink `bap_broadcast_sink`, and the unicast headset `le_audio_headset`, which receives over a CIS. Zephyr has no board definition for the Reef, so they run on the IPRO7 EVB and the IPRO7AI EVK. The boards, behavior and build commands of each sample are in [Audio & LE Audio](../guides/audio.md#broadcast-audio); setting up the workspace and flashing are covered in [Zephyr RTOS](../guides/zephyr.md).

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| `IPRO-LE-Audio` does not appear in the phone's Bluetooth list | LE Audio is off on the phone, or the board is already connected to another device | Switch on LE Audio on the phone; the application accepts one link at a time and stops advertising while connected |
| Pairing fails after reflashing | The phone or the board kept an old bond | Type `leaudio_unpair` at the console to clear the bonds, remove the device on the phone, and pair again |
| `test_tone` is silent | The speaker is off while headphones are in J2; the amplifier runs from USB VBUS | Unplug the headphones or listen on them; power the board over USB-C |
| A key press prints `volume control not up yet` | VCP has not finished initializing | Wait until the boot messages are done |
| The build stops at the configure step with a message about `CONFIG_EM_SIZE` | `bt54_iso2` needs a larger Exchange Memory | Set `CONFIG_EM_SIZE=32` |

## Next steps { #next-steps }

- [Audio & LE Audio](../guides/audio.md): the audio framework, DAC, PDM and LC3.
- [BLE Development](../guides/ble.md): controller library selection and host settings.
- [Zephyr RTOS](../guides/zephyr.md): build and flash the Zephyr samples.
