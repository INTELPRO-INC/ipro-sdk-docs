---
title: "Flashing and the Board"
description: What IPRO Workbench checks before and after flashing, the partition table view and its checks, the board's flash and firmware check, and writing AI models to the mfg partition.
---

# Flashing and the Board

The checks the IDE makes for you when flashing, the partition table, the board's flash, the firmware check and writing AI models. The board is the IPRO7AI Reef EVK V4.0 on the IPRO Debug Probe; flashing uses IntelProCube.

## Flash { #flash }

<div class="ipro-steps" markdown>

1. **Flash.** After you select the application and build it, click **Flash** (`Cmd+Alt+U` / `Ctrl+Alt+U`).

    **You should see**: the **Output** panel switches to **IPRO Flash** and shows the IntelProCube flashing progress; the last line is `[All Success]`. A notification says "Flashed &lt;application&gt; in N s."

2. **The monitor closes and reopens.** Before flashing, the IDE automatically closes every serial monitor (one port cannot be used by two programs at the same time). With **Build, Flash and Monitor**, the monitor opens again after a successful flash.

</div>

!!! warning "Important"
    When IntelProCube fails to flash, it sometimes reports no error. The IDE counts a flash as successful only when `[All Success]` appears in the output; after the board reboots, the IDE also checks the build time the board prints (see [Board flash and firmware check](#board-flash)).

When flashing fails, the IDE offers buttons that match the cause:

![The explanation of a flash error with its action buttons](../assets/workbench/flash-guidance.svg)

| Situation | What the IDE does |
|---|---|
| The application has not been built | Says it "has not been built yet" and offers **Build and Flash** |
| IntelProCube is not found | Offers **Install IntelProCube**, or **Browse…** to point to one you already have |
| The board does not answer | Asks you to check the probe cable and the power, and offers **Select Port** and **Retry** |
| The port is in use by another program | Asks you to close that program, then **Retry** |
| The partition table is larger than the board's flash | Asks before flashing; you can **Flash Anyway** or open the **Partition Table** instead |

## Partition table { #partitions }

The partition table decides where in flash the firmware, OTA slot B, the AI model (mfg) and other data are placed.

<div class="ipro-steps" markdown>

1. **Open the partition table.** Right-click the application and choose **Partition Table**.

    **You should see**: "Partition table of &lt;application&gt;". **Flash with** shows the partition table this flash uses (by default, the one IntelProCube picks from the flash size in `.config`); next to it are the flash size set in `.config` and the firmware size. When the IDE knows the board's flash, it adds a comparison line, for example "The board on this probe has 2 MB of flash (Winbond EF4015); ipro_unit_test is set to 1 MB." Below that are the flash map (one row each for slot A and slot B), the address and size of every partition, and the share of the FW partition that the firmware takes.

2. **Read the check results** below the table.

    **You should see**: when there is no problem, nothing is listed. When there is a problem, it is explained, for example: mfg and FW of the 1M partition table share the same space (writing an AI model overwrites the firmware), FW slot B of the 2M partition table overlaps mfg (an OTA update overwrites the AI model), or the firmware is larger than slot A.

3. **Use the application's own table.** When the application ships its own partition table, the page says "This application ships …". Select it in **Flash with**, and every later flash of this application uses it.

4. **Compare with the board.** With the serial monitor open, click **Reset Board**.

    **You should see**: **On the board** compares against the partition table the board prints at boot and marks each partition "same", "differs" or "not on the board". When they all match, it shows "The board printed the same table at its last boot."

</div>

![The partition table view with Flash with, the flash map of slots A and B, the partitions and the comparison with the board](../assets/workbench/partitions.svg)

!!! warning
    Flashing writes the partition table selected in **Flash with**. When it differs from the partition table on the board, partitions whose location changes (for example the AI model in mfg) lose their data.

## Board flash and firmware check { #board-flash }

At boot, the board prints the ID of its flash and the build time of its firmware. With the serial monitor open, the IDE reads these messages and shows them in the **Board** view of the side bar:

| Shown | Meaning |
|---|---|
| Flash Winbond 2 MB (EF4015) | The flash and its size on the board on this probe |
| Chip ID … | The chip ID that IntelProCube read while flashing |
| Runs ipro_unit_test (built …) | The build time the board printed at boot matches the firmware of this application's last build |
| Runs other firmware (built …) | The board is not running the last build; that build runs only after you flash it |

If "other firmware" appears right after a flash, the flash may not really have reached the board. The IDE warns you and offers **Flash Again**.

When the partition table uses more space than the board's flash (for example a 4 MB partition table selected for a 2 MB board), the IDE asks you before flashing, so that the part past the end is not left unwritten. Click **Partition Table** to pick another one, or click **Flash Anyway** once you have confirmed it is correct.

![The question before flashing when the partition table is larger than the board's flash, with Partition Table and Flash Anyway](../assets/workbench/flash-guard.svg)

## AI model { #ai-model }

The IPRO7AI NPU model (`.inm`) lives in the mfg partition of the flash and is not linked with the firmware. To update the model, you only write mfg; the firmware does not need to be flashed again.

<div class="ipro-steps" markdown>

1. **Choose the model.** Right-click the application and choose **AI Model…**. In **Model**, choose an `.inm` in the application folder, or click **Browse…** to choose another file.

    **You should see**: the model's size, format version and number of layers, input, NPU and CPU instructions and weight sizes, the memory it takes once loaded (model plus work buffer, against the 8 MB PSRAM), and the mfg partition it goes into. The last line says "The model fits this application and its partition table." or why it does not fit.

2. **Write it.** If it fits, click **Write to mfg**.

    **You should see**: a notification says "Wrote … to the mfg partition in N s." Only the model is written; the firmware is untouched.

3. **Watch it on the board.** While the board runs the model (with the serial monitor open), **On the board** shows whether each layer runs on the NPU or the CPU. When the firmware is built with `CONFIG_AI_CYCLE_PROFILE=y` and calls `iproai_cycle_report()`, it also shows the time per inference and how busy the NPU and the CPU are.

</div>

![The AI Model view with the model's details, the mfg partition it goes into and the fit check](../assets/workbench/ai-model.svg)

!!! note
    The IntelProCube 1M partition table has no separate space for the model (mfg overlaps FW), so the IDE refuses to write it. In **Partition Table**, select the partition table that comes with the application (for example the one with a separate mfg), then write the model.
