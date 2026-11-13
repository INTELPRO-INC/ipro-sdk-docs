---
title: ipro_ai_link
description: 'Board firmware for IPRO AI Studio "Run on board": loads .inm models and inputs from microSD (sd:/), runs them on the NPU and prints the raw outputs; also usable by hand from the console'
generated: tools/gen_examples.py
migrate_from: []
---

# ipro_ai_link

Board firmware for IPRO AI Studio "Run on board": loads `.inm` models and inputs from microSD (`sd:/`), runs them on the NPU and prints the raw outputs; also usable by hand from the console

| Item | Details |
|---|---|
| Source | [`apps/test/ipro_ai_link`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/test/ipro_ai_link) |
| Boards and configs | Reef (`defconfig_reef`); `.config` targets the IPRO7 EVB |
| Console | UART 115200 (also on a USB CDC port) |
| Build | Reef: `make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |

## Run it on the Reef { #on-the-reef }

This application has no README; the steps below follow its source. You need a FAT-formatted microSD card.

<div class="ipro-steps" markdown>

1. **Build**

    ```bash
    make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef
    ```

    The image is `apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin`.

2. **Flash**: enter [download mode](../hardware/boards/reef-evk.md#download-mode), then from the IntelProCube directory run

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --firmware <SDK>/apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin
    ```

    Check for `[All Success]`, then press SW2.

3. **Run**: open the console at 115200 baud; the board prints `ipro_ai_link ready`. On a computer's USB port the board shows up as two CDC serial ports (VID `0x3896`, PID `0x0704`): the first carries data, the second is a console.

4. **Run a model by hand**: copy an `.inm` model and a raw input file to the SD card, insert it, then type

    ```text
    ai_mount
    ai_load sd:/model.inm
    ai_input sd:/input.bin
    ai_run
    ai_out
    ```

    `ai_out` prints the output tensor in hex, every byte stored XOR 0x80. Paths always start with `sd:/`.

</div>

The SDK ships models to try, for example `apps/platform/ipro7_demo/demo/ai/ai_model/mbv2.inm`. Download IPRO AI Studio from [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest).
