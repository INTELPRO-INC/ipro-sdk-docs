---
title: "IPRO AI Teach 2.0"
description: The Edge AI Platform V2.0 on the IPRO7AI Reef - image, voiceprint and sensor recognition in one firmware, taught in IPRO AI Studio and run on the board's NPU
---

# IPRO AI Teach 2.0

IPRO AI Teach 2.0 is the Edge AI Platform V2.0 on the IPRO7AI Reef: one firmware with three recognition tools - image, voiceprint and sensor. You collect data in IPRO AI Studio, train on your computer and deploy over USB-C; the board runs the model on its NPU. No code is needed; when you want the model in your own application, the same runtime and APIs are there.

!!! info "Availability"
    IPRO AI Teach 2.0 (the Edge AI Platform V2.0 firmware and IPRO AI Studio) is not included in V2.1.0; contact INTELPRO.

!!! abstract "At a glance"
    - One firmware, `ipro_reef_teach`: image, voiceprint and sensor modes, one at a time; switching takes about 2 s and all three models stay on the board.
    - IPRO AI Studio's Teach, Audio and Sensor pages: collect, train (on the computer's CPU; no GPU needed), deploy and watch the results.
    - Models deploy as `.ipkg` packages; the `ipro-ai` command line deploys, verifies and benchmarks, for automation.
    - Hardware: IPRO7AI Reef (V4).

## Introduction video { #video }

<video controls preload="metadata" playsinline width="100%" poster="/ipro-sdk-docs/assets/videos/ipro-ai-teach-2-intro.jpg">
  <source src="/ipro-sdk-docs/assets/videos/ipro-ai-teach-2-intro.mp4" type="video/mp4">
</video>

A board tour, flashing, and each tool from collecting data to recognition on the board (about 3 minutes, narrated in Mandarin with Chinese captions).

## The three tools { #tools }

| | Image | Voiceprint | Sensor |
|---|---|---|---|
| What it does | Classifies objects in the camera view | Tells who is speaking; enrolled people by name, others by number | Classifies the state of a vibration, IMU or other signal; answers `UNKNOWN` for a state it was not taught |
| IPRO AI Studio page | Teach | Audio | Sensor |
| USB device | IPRO7 UVC Cam (3896:0705), camera + serial | IPRO Reef Voice (3896:0720) | IPRO Reef Sensor (3896:0721) |
| Classes or people | up to 8 classes | up to 19 people, stored in the board's flash | up to 8 classes (`UNKNOWN` is one of them) |
| Results | every camera frame | once a second | four times a second |
| NPU time on the board | about 10.5 ms (MobileNetV2 0.35) | about 8.9 ms | about 4.6 ms |
| Model slot | 508 KB | 444 KB | 252 KB |

The three tools share the board's NPU and keep their models in separate slots of the flash. A deploy is written, read back and CRC-checked before it is committed; if power or a reset cuts it, the board reports "install interrupted" and never keeps half a model.

## Workflow { #workflow }

<div class="ipro-steps" markdown>

1. **Flash the firmware once.** Flash `ipro_reef_teach` with its partition table using IntelProCube; the voiceprint model goes in with the mfg payload. Changing models later needs no flashing.
2. **Connect USB-C.** The computer enumerates the USB device of the current mode (table above); IPRO AI Studio finds the board by that name.
3. **Collect and train in Studio.** Image: record each class in front of the camera. Voiceprint: each person reads for about 20 seconds to enroll. Sensor: record each state.
4. **Deploy.** The model goes to the board over the same cable; the board restarts and loads it. When the board is in another mode, the page offers **Switch to …**.
5. **Watch the results.** Image results are drawn on the camera stream; voiceprint and sensor results show on the Studio page, with the board's RGB LED.

</div>

## Model packages and the command line { #packages-and-cli }

Models are delivered as `.ipkg` packages: the model, class names, pre-processing parameters and file hashes. Before a deploy, the target chip, runtime version and slot size are checked. The `ipro-ai` command line does what Studio does; add `--json` for automation:

```bash
ipro-ai device list                    # connected Reefs and their current mode
ipro-ai model list --all               # the model of each mode
ipro-ai deploy vib.ipkg --switch       # switch to the package's mode, deploy, confirm the CRC
ipro-ai benchmark -n 100 --json        # inference time on the board
```

## For application developers { #for-developers }

The platform's runtime and APIs come with the Edge AI Platform; call them to run the same models in your own firmware:

| Header | Purpose |
|---|---|
| `ipro_ai.h` | Open several models and run them one after another on the one NPU; every NPU segment has a time limit, and a faulted NPU refuses runs and reports an error instead of hanging |
| `ipro_ai_store.h` | Model slots, commit records, CRC checks |
| `ipro_ai_source.h` | Data sources (push ring buffer, timed sampling) |
| `ipro_ai_preproc.h` | Sensor, voiceprint and image pre-processing |
| `ipro_ai_app.h`, `ipro_ai_event.h` | Application pipeline and inference-result events |
| `app_watchdog.h` | AON watchdog: restarts the system when it stops responding |

## Limitations in this release { #limitations }

- One tool runs at a time. Each tool has one model slot, so a deploy cut halfway leaves that tool without a model; deploy again.
- The image tool needs the OV5640 camera module.
- The sensor tool's anomaly mode is trained on normal data only and is less sensitive to faults that only change amplitude or drift slowly; train faults you can record as classes.

## Related documents { #related }

- [AI & NPU](ai-npu.md): the IPRO7AI NPU and the IPROAI runtime.
- [Documents](../documents/index.md): IPRO7AI Reef user guide and IPRO Edge AI Programming Guide (on request from INTELPRO).
