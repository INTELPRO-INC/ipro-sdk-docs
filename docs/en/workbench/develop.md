---
title: "Develop an Application"
description: The IPRO Workbench views you use most while writing code - settings (Kconfig), pin configuration with generated code, builds and errors, the memory map and the memory budget.
---

# Develop an Application

The views you use most while writing code: changing settings (Kconfig), configuring pins, handling build errors, and seeing where the memory goes. The examples use the IPRO7AI Reef EVK V4.0.

## Change settings (Kconfig) { #kconfig }

The features and parameters of each application are recorded in its `.config`. The **Settings** view edits it in a form, so you do not need to open a terminal.

<div class="ipro-steps" markdown>

1. **Open Settings.** Right-click the application and choose **Settings (Kconfig)…** (or **Settings (Kconfig)** on IPRO Home).

    **You should see**: a **Settings: &lt;application&gt;** tab, with all options listed by Kconfig menu on the left and the help for the selected option on the right.

2. **Change an option.** Type the option you want to change in the search box, for example `LOG_BUFFER_SIZE`, and change its value to `512`.

    **You should see**: a green mark appears on the left of that row, an unsaved dot appears in the tab title, and the button in the top-right corner changes to **Save 1**. The right panel shows the option's type, range, dependencies, its original value in `.config` and the Kconfig default.

3. **Save.** Click **Save** (`Cmd+S` on macOS, `Ctrl+S` on Windows).

    **You should see**: the notification "Saved 1 settings to .config of … (the previous file is .config.old). The next build configures again."

</div>

![The Settings (Kconfig) view with the option list on the left and the help for the selected option on the right](../assets/workbench/kconfig.svg)

!!! warning "Important"
    The SDK build reads `.config` directly and does not apply Kconfig selects or defaults. **Settings** writes only the lines you changed; if menuconfig would also change other options, they are listed on screen, and you decide whether to **Take Them Too**.

Other uses:

- Check **Only changed** to see only the changes that are not saved yet; click **Revert** to discard all changes.
- Check **Show hidden options** to see the options whose dependencies are not met: menuconfig hides them, but the build still reads them.
- If you prefer a text interface, right-click and choose **Menuconfig** to edit the same settings in a terminal; choose **Open .config** to edit the file directly.

## Configure pins { #pins }

**Pin Configuration** assigns the function of each GPIO on a package drawing and in a table, checks for conflicts and against the board's wiring, and generates the initialization code `app_pins.h` and `app_pins.c`.

<div class="ipro-steps" markdown>

1. **Open Pin Configuration.** Right-click the application and choose **Pin Configuration…** (or **Pins** on IPRO Home).

    **You should see**: the QFN56 package drawing on the left and the GPIO table on the right. **Board** is set to IPRO7AI Reef V4 automatically, the **On the board** column lists what each pin is connected to on the board, and pins that go to the 40-pin header also show the header pin number.

2. **Assign a pin.** Click the GPIO24 row, choose **GPIO_OUT (as on the board)** under **Signal**, and enter `RGB_LED` under **Label**.

    **You should see**: pin 24 turns blue on the package drawing; the right panel lists the pin's available functions, I/O voltage and board wiring; `app_pins.c` under **Generated code** at the bottom gets a GPIO24 line, and "No problems." is shown.

3. **Try a conflict.** Change the signal of GPIO24 to `UART1_TXD`.

    **You should see**: pin 24 turns amber, and **Problems** lists a warning saying that this pin is wired to the RGB LED on Reef V4, together with the free pins this signal **Could go to**; click **Move to GPIO…** to move the setting there. When you have seen this, change GPIO24 back to **GPIO_OUT (as on the board)**.

4. **Search by signal.** Type `SDH_0` in the search box.

    **You should see**: the table shows only the pins that can carry SDH_0, and those pins are outlined on the package drawing. Clear the search text and the full table comes back.

5. **Save and generate.** Click **Save and Generate** (`Cmd+S` / `Ctrl+S`).

    **You should see**: the notification "Saved pins.yaml and generated app_pins.h and app_pins.c." The application folder now has `pins.yaml`, `app_pins.h` and `app_pins.c`, and `CMakeLists.txt` has a new `app_pins.c` line.

6. **Call the generated code.** In `main.c`, add `#include "app_pins.h"` and call `app_pins_init();` once on the line after `ipro_platform_init();`, and then click **Build, Flash and Monitor**.

    **You should see**: the application runs as usual. From now on, whenever `pins.yaml` changes, **IPRO Build** first shows `pins: wrote app_pins.c from pins.yaml` during the build and then starts compiling.

</div>

![Pin Configuration with the QFN56 package drawing, the GPIO table and the generated code](../assets/workbench/pins.svg)

![A pin conflict warning under Problems, with the free pins the signal could go to](../assets/workbench/pins-conflict.svg)

| Function | Description |
|---|---|
| **Only pins in use** | Lists only the pins that are set, for easy checking |
| **Export CSV** | Writes a pin list for hardware engineers, `pins.csv` |
| **Export Zephyr pinctrl** | Writes the same pin configuration as a Zephyr pinctrl fragment, `app_pins_pinctrl.dtsi` |
| **Use as on the Board** | Sets the selected pin to its use on the board |

!!! note
    - `app_pins.h` and `app_pins.c` are generated by the IDE; do not edit them by hand. The IDE does not simply overwrite a file that was edited by hand; it first asks whether to **Overwrite** it.
    - When `pins.yaml` has errors, the build stops, and the errors are listed in the **Problems** panel.
    - The pin data comes from the IPRO7 datasheet.

## Build and errors { #build }

<div class="ipro-steps" markdown>

1. **Build.** Click **Build** (`Cmd+Alt+B` / `Ctrl+Alt+B`).

    **You should see**: on success, the notification "Built &lt;application&gt; in N s", followed by the memory usage.

2. **Go to the error.** When the code has errors, the notification says "&lt;application&gt; did not compile. First error at &lt;file&gt;:&lt;line&gt;: &lt;message&gt;". Click **Go to Error**, and the editor jumps to that line; the **Problems** panel lists all errors and warnings.

3. **Fix and build again.** Fix the code and build again. If needed, you can click **Ask AI to Fix** on the notification (see [AI Assistant](ai.md#fix-build)).

</div>

| Command | When to use it |
|---|---|
| **Build** | The usual case. Recompiles only the files that changed. |
| **Reconfigure and Build** | After you change `CMakeLists.txt` or the build profile; runs the CMake configuration again. |
| **Clean** | Deletes the application's `build` folder, so the next build starts from scratch. |

The build profile (Debug / Release / MinSizeRel) is selected with the `ipro.build.profile` setting; see [Settings](reference.md#settings).

## See where the memory goes { #memory }

<div class="ipro-steps" markdown>

1. **Open the memory map.** After a successful build, click the memory usage in the status bar, or **What uses the memory** on IPRO Home.

    **You should see**: "Memory map of &lt;application&gt;", with one tab each for flash, ocram and hbnram. Below them, the libraries, object files and symbols are listed by size, with each one's share of that region. Double-click a symbol to search for it in the workspace.

2. **Filter.** Type the name of a library, object file or symbol in the filter box to see only the matching items.

</div>

![The memory map with tabs for flash, ocram and hbnram and the libraries, object files and symbols listed by size](../assets/workbench/memory-map.svg)

- **(the application itself)** is the object files in the application folder.
- **(merged strings and constants)** is the string pool shared by all objects; it gets large when there are many log strings.
- The numbers are counted from the linker map file; the totals in the build output also include alignment and padding, so the two may differ slightly.

### Size changes and the memory budget { #memory-budget }

<div class="ipro-steps" markdown>

1. **See the size change.** Change the code, build again, and look at the last few lines of the **IPRO Build** output.

    **You should see**: for example `Memory since the last build: flash +3,072 B, ocram 0 B, …`, followed by the symbols that changed most, for example `+3,072 B  my_table  (flash, (application) main.c.o)`. The build-finished notification also adds the change after the usage, for example `flash 8.2% (+3,072 B)`. After the first build, or after a clean, there is no previous build to compare with, so these lines do not appear.

2. **Set a memory budget.** Open Settings (`Cmd+,` on macOS, `Ctrl+,` on Windows), search for `ipro.build`, and in **Memory Budget** enter the maximum percentage for each region, for example `{ "flash": 90, "ocram": 95 }`.

    **You should see**: when a limit is exceeded, the notification reads "… is over its memory budget: flash 92.1% > 90%." Click **Memory Map** to see what used it up.

3. **Fail the build over budget (optional).** Also check **Fail Over Budget** to make a build over the budget fail; **Build, Flash and Monitor** then stops before flashing.

</div>
