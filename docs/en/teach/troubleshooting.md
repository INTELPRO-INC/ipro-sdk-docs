---
title: "Teach Troubleshooting"
description: Causes and fixes for common IPRO AI Teach problems - board not found, wrong mode or USB device, no camera image, failed flashing, refused or interrupted deploys, watchdog restarts, and the ipro-ai exit codes.
---

# Teach Troubleshooting

Common IPRO AI Teach problems, grouped by topic. Messages from the screen and the console are quoted as they appear so you can match them; each tool's page also has its own troubleshooting table.

## Check these first { #checklist }

1. **The USB-C cable carries data.** A charge-only cable lights the board but the computer enumerates no USB device.
2. **USB-C is on the Reef's own USB-C (USB1).** The IPRO Debug Probe's USB port carries only the console and flashing; the Teach tools do not use it.
3. **The board runs the Edge AI firmware.** The console boot log has `IPRO7AI Reef Teach: image, voice, sensor` and a `mode:` line.
4. **The board's mode matches the page.** `image` for **Teach**, `voice` for **Audio**, `sensor` for **Sensor**; if not, the page shows **Switch to …** at the top.
5. **No other program holds the board's USB serial port.** Only one program at a time can open it.

## Connection and modes { #connection }

| Symptom | Cause | Fix |
|---|---|---|
| No Reef USB device appears on the computer | The cable is charge-only, or the firmware did not start | Use a data cable; check the console boot log |
| LED2 (power) is off | No power on USB-C, or the fuse has tripped on overcurrent | Try another cable or USB port; remove any add-on board from the 40-pin header |
| Studio shows `The Reef is in <mode> mode.` | The board is in another mode | Press **Switch to …** on the page |
| After **Switch to …**, `This Reef's firmware runs one Teach only.` | The board runs single-tool firmware, not the Edge AI firmware | Flash `ipro_reef_teach` as in [Flash the Edge AI Firmware](firmware.md) |
| After **Switch to …**, `The Reef did not switch.` | The switch command did not complete, for example because the port is in use | Close other programs using the board's port and press again, or type `mode <mode>` on the console |
| A page found a different board | Several Reefs are attached | Attach one at a time; on the command line use `--port` |
| The boot log or `ipro-ai model list` shows `install_interrupted` | The last deploy did not finish (power cut, reset, cable pulled) | Deploy again |
| The boot log or `ipro-ai model list` shows `crc` | The committed model is damaged | Deploy again |
| The boot log or `ipro-ai model list` shows `no_xip` | The partition cannot be read | Reflash the firmware with `partition_reef_teach.toml` |
| A deploy is refused with `size` in the message | The model is larger than the slot | Use a smaller model (Medium or Small for sensors, MobileNetV1 0.25 for images) |

## Flashing { #flashing }

| Symptom | Cause | Fix |
|---|---|---|
| The flash tool finished but the output has no `[All Success]` | Flashing failed; the tool exits with 0 on failure too | Check download mode and the port, then flash again |
| Handshake succeeds but the flash ID is `00000000`, ErrorCode `003D` | Wrong flash pin setting | Add `--chip-variant IPRO7AI` to the command |
| The flash tool reports a handshake failure or cannot open the port | A terminal program still holds the port, or the board is not in download mode | Close the terminal program; enter download mode again |
| On macOS, `utils/ipro_flash.sh` reports `[Errno 83] Device error`, ErrorCode `0003` | The probe's port briefly disappears after it puts the Reef into download mode | Wait a second or two and run the same command again |
| On macOS, opening the serial port hangs | A `/dev/tty.*` device was used | Use `/dev/cu.*` |
| Nothing on the console and `reboot_dl` does nothing | The firmware has hung; no shell | Enter download mode with the buttons (hold SW1, press SW2, release SW1) or the probe, then reflash |
| No characters at all on the console | The cable is not pin-reversed, or the wrong probe port is open | Use a pin-reversed cable; open the probe's "IPRO7 UART" port at 115200 baud |
| A different board got flashed | Several boards are attached and `--port` named another one | Check the board by its console boot log first; when in doubt, attach one board |
| After flashing the Edge AI firmware, image and sensor have no model | The previous firmware used the standard partition table, where the slots are elsewhere | Expected; deploy again from Studio |
| The Teach tools misbehave after flashing with **Flash** on Studio's **Board** page | The Board page writes with the standard partition table and no mfg payload | Reflash with IntelProCube as in [Flash the Edge AI Firmware](firmware.md#flashing) |

## Image recognition { #image }

| Symptom | Cause | Fix |
|---|---|---|
| No **IPRO7 UVC Cam** in the camera list; Studio says `No board with the Teach firmware on USB.` | The board is not in `image` mode, or the cable is charge-only | Switch to `image` mode; use a data cable |
| The Teach page shows `IPRO AI Studio is not allowed to use the camera.` | macOS camera permission was refused | Turn IPRO AI Studio on in **System Settings → Privacy & Security → Camera**, then reopen Studio |
| No camera image on the Teach page on Windows | The system camera privacy setting blocks desktop apps | In **Settings → Privacy & security → Camera**, let desktop apps access the camera |
| On macOS no program shows the camera | Another program still holds the camera | Quit that program, then unplug and replug USB-C |
| The console repeats `no camera answers` | The camera is not connected, or SW7 is not at CAM | Unplug USB-C, check the camera cable, set SW7 to CAM |
| Some GPIOs on the 40-pin header do nothing | Those pins go through the camera switch and SW7 is at CAM | Normal while using the camera; to use those GPIOs set SW7 to GPIO (the camera loses power) |
| The view shows `NO MODEL: NO MODEL IN MFG` | No model deployed yet | Deploy from the Teach page |
| The view shows `NO MODEL: DEPLOY INTERRUPTED` | The last deploy did not finish | Deploy again |
| The view shows `NO MODEL: NO MFG PARTITION` | The partition table used for flashing has no mfg partition | Reflash the firmware with `partition_reef_teach.toml` |
| The view shows `NO MODEL: WRONG MODEL` | The slot holds another kind of model | Deploy once more |
| After a deploy the Camera area shows `The board went away. Waiting for it…` | The board is restarting | Normal; the camera comes back by itself. If not, unplug and replug USB-C |
| The training result says `<A> taken for <B>` | The object left the box while recording | Press **Review** on both classes, drop bad crops, train again |
| In real use one class is often read as another | Not enough data at some angles or light, or the two look alike | Record more at those angles and in that light, then train and deploy |

## Voiceprint recognition { #voice }

| Symptom | Cause | Fix |
|---|---|---|
| The Audio page says the board has no voice model, or the console shows `NO MODEL` | No valid voiceprint model on the board | Reflash with `--mfg`, or deploy the voiceprint model with `ipro-ai deploy`; see [Change the voiceprint model](voice.md#voice-model) |
| The board's serial port cannot be opened | Another program holds it | Close other programs using that port and try again |
| Enrolling fails with `Too little speech was heard` | Too little speech was heard | Speak louder or closer and keep reading until time is up |
| Someone not enrolled keeps getting an enrolled person's name | The name threshold is low for normal mode, especially with loudspeaker playback | Turn stranger mode on, or raise **Name match** |
| An enrolled person is often labeled Speaker k | Enrolled at a different place, microphone or loudness than in use, or the name threshold is too high | Enroll again at the real position with the Reef's microphone, or lower **Name match** slightly |
| One person is split into several speakers | The new-speaker threshold is too high | Lower **New speaker**, or name one of them |
| Labels appear when nobody speaks | Music, a TV or other continuous sound counts as speech | Remove the background sound; use a quiet room |
| Everyone enrolled is gone after changing the voiceprint model | Voiceprints are tied to the model | Enroll again with the new model |
| A name with Chinese characters cannot be entered on the console | The console accepts ASCII only | Enter the name on the Audio page |

## Sensor recognition { #sensor }

| Symptom | Cause | Fix |
|---|---|---|
| **Put it on the board** says `Connect a Reef running the Edge AI firmware to its own USB-C port.` | No board in `sensor` mode found | Check the firmware and the cable; USB-C must be on the Reef's own port |
| `Not ready to train` | The board is not connected, or fewer than 2 classes have recordings (exactly 1 for anomaly detection) | Connect the board and record the classes |
| `too short: hold for at least one window` | Held for less than one window | Hold longer |
| `<k> of <n> classes have no held-out data` | Some classes were recorded too briefly each time | Hold for more than twice the window length each time |
| **Import CSV…** shows `<N> columns` | The CSV's columns do not match the source's channel count | One column per channel, one row per sample |
| **Open…** shows `Not a Sensor Teach folder` | The folder has no `sensor_teach.json` | Open a folder saved with **Save…** |
| Deploy fails: `the board did not come back with the model within 30 s` | The board did not come back with the new model within 30 s | Unplug and replug USB-C, check the console boot log, deploy again |
| A trained model no longer works after changing the source | A model works only with the source it was trained on | Record and train again on the new source |
| Live results show `UNKNOWN` at state changes | The window holds both states | Normal; judge from several results in a row |
| Anomaly detection alarms at a heavy but normal load | The normal data did not cover that load | Record normal data at every normal load and speed, and train again |

## While running, and the watchdog { #runtime }

| Symptom | Cause | Fix |
|---|---|---|
| The board restarts on its own (the boot log appears again on the console) | The system stalled and the firmware's watchdog restarted the board after about 5.6 to 8 s - for example when the NPU ran a corrupted model | The board comes back in the same mode with its models. Deploy a verified model again; note what you were doing and the console output, and report it to INTELPRO |
| You want to check that the watchdog is on | | Type `watchdog` on the console for its state; `watchdog test` stops feeding, and the board should restart within seconds |
| USB-C was pulled or the board reset during a deploy | The deploy was cut before it was committed | That tool has no model (`install_interrupted`); deploy again. The other two tools' models are unaffected |

## The ipro-ai command line { #cli }

The `ipro-ai` device and model commands report with fixed exit codes. With `--json`, standard output carries a single JSON document whose `error.type` names the kind of error.

| Exit code | Meaning | What to do |
|---|---|---|
| `0` | Success | |
| `1` | A check failed: a damaged package, `verify` mismatch, or the CRC or size read back after a deploy is wrong | Check that the board's model CRC matches the package; rebuild the package |
| `2` | Usage error: arguments, unreadable files, several boards on USB without `--port` | Fix the arguments; name the board with `--port` |
| `3` | No device found, or the serial port disappeared | Check the USB-C cable and the firmware; run `ipro-ai device list` |
| `4` | The board refused (for example `TDEP ERR crc`) or its reply was not understood | Act on the reply; deploy again |
| `5` | Timeout: the board did not answer, or did not come back after a restart | Check the console boot log; run `ipro-ai device list` |
| `6` | Incompatible: the firmware lacks the function (for example, the Edge AI firmware has no rollback), the tool or ABI does not match, or the model does not fit | Use a suitable model or command, as the message says |
| `7` | Internal error in the tool | Keep the `--json` output and report it to INTELPRO |

## Reporting a problem { #report }

When you contact INTELPRO, include:

- The full console output from boot until the problem (the IPRO Debug Probe's "IPRO7 UART" port, 115200 baud).
- The output of `ipro-ai device info --json`: firmware, platform version, mode and the model on the board.
- The IPRO AI Studio version (**About IPRO AI Studio**, in the **Help** menu on Windows and the application menu on macOS) and your operating system.
- The steps you took and the exact messages on screen.
