---
title: "烧录与开发板"
description: IPRO Workbench 在烧录前后的检查、分区表视图及其检查、开发板的 Flash 与固件核对、将 AI 模型写入 mfg 分区、制作并发送 OTA 包、通过开发板自身的 USB 烧录，以及 IPRO6S EVK 的构建、烧录与监视。
---

# 烧录与开发板

IDE 在烧录时替你执行的检查、分区表、开发板的 Flash、固件核对、AI 模型的写入、[OTA 包](#ota)以及[通过开发板自身的 USB 烧录](#usb-flash)；最后一节介绍 [IPRO6S EVK](#ipro6s) 及其与 IPRO7 系列的不同之处。其余各节中的开发板为接在 IPRO Debug Probe 上的 IPRO7AI Reef EVK V4.0；烧录使用 IntelProCube。

## 烧录 { #flash }

<div class="ipro-steps" markdown>

1. **烧录。** 选择应用程序并完成构建后，点击 **Flash**（`Cmd+Alt+U` / `Ctrl+Alt+U`）。

    **应看到**：**Output** 面板切换到 **IPRO Flash**，显示 IntelProCube 的烧录进度；最后一行为 `[All Success]`。通知显示“Flashed &lt;application&gt; in N s.”

2. **监视器关闭后重新打开。** 烧录前，IDE 会自动关闭所有串口监视器（同一个端口不能同时被两个程序使用）。使用 **Build, Flash and Monitor** 时，烧录成功后监视器会重新打开。

</div>

!!! warning "重要"
    IntelProCube 烧录失败时，有时不会报告错误。只有输出中出现 `[All Success]`，IDE 才认为烧录成功；开发板重启后，IDE 还会核对开发板打印的构建时间（请参阅[开发板的 Flash 与固件核对](#board-flash)）。

烧录失败时，IDE 会根据原因提供相应的按钮：

![烧录错误的说明及其操作按钮](../assets/workbench/flash-guidance.svg)

| 情况 | IDE 的处理 |
|---|---|
| 应用程序尚未构建 | 提示“has not been built yet”，并提供 **Build and Flash** |
| 找不到 IntelProCube | 提供 **Install IntelProCube**，或通过 **Browse…** 指向已有的 IntelProCube |
| 开发板没有响应 | 提示检查探针线缆和电源，并附上让这块开发板手动进入下载模式的方法（IPRO7AI Reef EVK V4.0：“To enter download mode by hand: hold SW1 (BOOT), tap SW2 (RESET), then release SW1.”）；提供 **Select Port** 和 **Retry** |
| 开发板有响应，但它的 Flash 没有响应（使用另一块开发板的 Flash 引脚烧录） | 说明“The board on … answered, but its flash did not: it was flashed as …, and the flash pins of that board are not this one's. Select the board that is connected, then retry.”，并提供 **Select Board**、**Retry** 和 **Show Output** |
| 端口被其他程序占用 | 提示关闭该程序，然后点击 **Retry** |
| 分区表大于开发板的 Flash | 烧录前询问；可以选择 **Flash Anyway**，或改为打开 **Partition Table** |
| IntelProCube 缺少这块开发板所需的分区表 | 不烧录（没有该分区表，开发板无法启动）；提供 **Partition Table** 和 **Install IntelProCube** |
| 分区表为 boot2 布局，但 IntelProCube 没有这颗芯片的 boot2 镜像 | 不烧录（不带 boot2 烧录的开发板无法启动）；提供 **Partition Table** 和 **Install IntelProCube** |
| IntelProCube 版本太旧（IPRO6S EVK 需要 0.7.0.1 或更高版本） | 不烧录（用它烧录后开发板无法启动）；提供 **Install IntelProCube** 和 **Browse…** |

分区表为 boot2 预留了空间时（boot2 布局，例如用于 OTA 的 A/B 分区表），IDE 会将 IntelProCube 附带的 boot2 与固件一起写入，IPRO7 和 IPRO6S 都是如此。此时 **IPRO Flash** 在分区表那一行之后多出一行 `boot2: … (the partition table is laid out for boot2)`，开发板启动时先由 boot2 启动。

## 分区表 { #partitions }

分区表决定固件、OTA 的 B 槽、AI 模型（mfg）及其他数据在 Flash 中的位置。

<div class="ipro-steps" markdown>

1. **打开分区表。** 右键点击应用程序并选择 **Partition Table**（或点击 IPRO Home 上 **Tools** 下的 **Partition table**）。

    **应看到**：“Partition table of &lt;application&gt;”。**Flash with** 显示本次烧录使用的分区表（默认为 IntelProCube 根据 `.config` 中的 Flash 大小选择的分区表）；旁边是 `.config` 中设置的 Flash 大小和固件大小。IDE 已知开发板的 Flash 时，会增加一行比较，例如“The board on this probe has 2 MB of flash (Winbond EF4015); ipro_unit_test is set to 1 MB.”下方是 Flash 映射图（A 槽和 B 槽各一行）、每个分区的地址和大小，以及固件占 FW 分区的比例。

2. **查看表格下方的检查结果。**

    **应看到**：没有问题时不列出任何内容。有问题时会加以说明，例如：1M 分区表的 mfg 与 FW 共用同一块空间（写入 AI 模型会覆盖固件）、2M 分区表的 FW B 槽与 mfg 重叠（OTA 更新会覆盖 AI 模型），或者固件大于 A 槽。

3. **使用其他分区表。** 应用程序自带分区表时，页面会显示“This application ships …”。**Flash with** 除了应用程序自带的分区表，还列出 IntelProCube 为这颗芯片提供的所有分区表（名称后标有 `(IntelProCube)`，例如 boot2 和 OTA 的布局），无需先复制到应用程序文件夹。选择一份之后，该应用程序的每次烧录都会使用它。

4. **与开发板比对。** 在串口监视器打开的情况下，点击 **Reset Board**。

    **应看到**：**On the board** 与开发板启动时打印的分区表进行比对，并将每个分区标记为“same”、“differs”或“not on the board”。全部一致时显示“The board printed the same table at its last boot.”

</div>

![分区表视图，包含 Flash with、A 槽和 B 槽的 Flash 映射图、各分区以及与开发板的比对](../assets/workbench/partitions.svg)

!!! warning
    烧录会写入 **Flash with** 中选择的分区表。它与开发板上的分区表不同时，位置发生变化的分区（例如 mfg 中的 AI 模型）会丢失数据。

## 开发板的 Flash 与固件核对 { #board-flash }

开发板启动时会打印其 Flash 的 ID 和固件的构建时间。在串口监视器打开的情况下，IDE 会读取这些信息，并显示在侧边栏的 **Board** 视图中：

| 显示内容 | 含义 |
|---|---|
| Flash Winbond 2 MB (EF4015) | 此探针所连开发板上的 Flash 及其大小 |
| Chip ID … | IntelProCube 在烧录时读取的芯片 ID |
| Runs ipro_unit_test (built …) | 开发板启动时打印的构建时间与该应用程序上一次构建的固件一致 |
| Runs other firmware (built …) | 开发板运行的不是上一次构建的固件；该构建要烧录后才会运行 |

如果刚烧录完就出现“other firmware”，说明烧录可能并未真正写入开发板。IDE 会发出警告，并提供 **Flash Again**。

**Board** 逐一列出已连接的每个探针，这在同一台计算机连接两块开发板时特别有用：当前使用的探针标有 **In use**，每个探针下方有“Last flashed: &lt;application&gt; · &lt;board&gt; · &lt;time&gt;”，便于分辨哪块开发板烧录了什么。点击另一个探针，即可改用它的 UART。

当分区表占用的空间超过开发板的 Flash 时（例如为 2 MB 的开发板选择了 4 MB 的分区表），IDE 会在烧录前询问你，以免超出末尾的部分没有写入。点击 **Partition Table** 选择其他分区表，或在确认无误后点击 **Flash Anyway**。

![分区表大于开发板 Flash 时烧录前的询问，包含 Partition Table 和 Flash Anyway](../assets/workbench/flash-guard.svg)

## AI 模型 { #ai-model }

IPRO7AI 的 NPU 模型（`.inm`）通常存放在 Flash 的 mfg 分区中，不与固件链接在一起。更新模型时只需写入 mfg，无需重新烧录固件。有些应用程序将模型链接在固件中，请参阅本节末尾的说明。

<div class="ipro-steps" markdown>

1. **选择模型。** 右键点击应用程序并选择 **AI Model…**（或点击 IPRO Home 上 **Tools** 下的 **AI model**）。在 **Model** 中选择应用程序文件夹中的 `.inm`，或点击 **Browse…** 选择其他文件。

    **应看到**：模型的大小、格式版本和层数，输入、NPU 与 CPU 指令以及权重的大小，加载后占用的内存（模型加工作缓冲区，对照 8 MB PSRAM），以及模型要写入的 mfg 分区。最后一行显示“The model fits this application and its partition table.”，或说明不适合的原因。

2. **写入。** 如果适合，点击 **Write to mfg**。

    **应看到**：通知显示“Wrote … to the mfg partition in N s.”只写入模型，固件不受影响。

3. **在开发板上观察。** 开发板运行模型时（串口监视器保持打开），**On the board** 显示每一层是在 NPU 还是 CPU 上运行。如果固件以 `CONFIG_AI_CYCLE_PROFILE=y` 构建并调用 `iproai_cycle_report()`，还会显示每次推理的时间以及 NPU 和 CPU 的繁忙程度。

</div>

![AI Model 视图，包含模型详细信息、要写入的 mfg 分区以及适配检查](../assets/workbench/ai-model.svg)

!!! note
    - IntelProCube 的 1M 分区表没有单独的模型空间（mfg 与 FW 重叠），因此 IDE 会拒绝写入。请在 **Partition Table** 中选择应用程序自带的分区表（例如带有独立 mfg 的分区表），然后再写入模型。
    - 应用程序将模型链接在固件中时，页面会说明“This application links the model into its firmware (…): it runs the copy it was built with, and a model written to mfg does not change that. Rebuild and flash the application to change the model.”，**Write to mfg** 按钮也会变为次要样式。

## OTA 包 { #ota }

**OTA Package** 为应用程序上一次的构建制作 boot2 OTA 包（`.xz.ota`）：IntelProCube 根据分区表生成镜像，再由 SDK 的 `tools/create_ota.py` 压缩，制作时不会写入开发板。使用 IPRO SDK V2.3.0 时，还可以通过控制台 UART 将 OTA 包发送给开发板上的 `ota_uart` 命令进行安装，或者只让开发板检查而不安装。OTA 的架构、OTA 包格式以及通过 BLE 发送的方法，请参阅 [OTA 更新](../guides/ota.md)。

| 需要 | 说明 |
|---|---|
| 芯片 | IPRO7、IPRO7AI（boot2 OTA 包只适用于 IPRO7 的应用程序） |
| 分区表 | 为 boot2 预留了空间、且 FW 分区有第二个 slot 的 A/B 分区表，例如 `ipro_ble_remote` 自带的 `partition_cfg_2M_remote_ab.toml`。IntelProCube 的常规分区表没有 boot2 的空间，无法制作 OTA 包 |
| 发送到开发板（SDK V2.3.0） | 应用程序配置了 `CONFIG_IPRO_OTA=y` 和 `CONFIG_IPRO_OTA_UART=y`，并且开发板已经用 boot2 和 A/B 分区表烧录过 |

下面以 IPRO SDK V2.3.0 的 `ipro_ble_remote` 在 IPRO7AI Reef EVK V4.0 上为例，它的 `defconfig_reef` 已开启上表中的配置。

<div class="ipro-steps" markdown>

1. **选择应用程序和配置文件。** 在侧边栏的 **Applications** 下点击 **ipro_ble_remote**，再点击状态栏中的 `.config`，选择 `defconfig_reef`（请参阅[配置文件](develop.md#configurations)）。

    **应看到**：通知“ipro_ble_remote now builds for IPRO7AI Reef (defconfig_reef).”，状态栏显示 `defconfig_reef`。

2. **选择 A/B 分区表。** 右键点击应用程序并选择 **Partition Table**，在 **Flash with** 中选择 `partition_cfg_2M_remote_ab.toml`。

    **应看到**：Flash 映射图中 FW 有 A、B 两行。

3. **构建、烧录并监视。** 点击 **Build, Flash and Monitor**。

    **应看到**：**IPRO Flash** 中有一行 `boot2: … (the partition table is laid out for boot2)`，最后一行为 `[All Success]`；IPRO Monitor 先出现几行以 `[BOOT2]` 开头的信息，然后是应用程序的启动信息。

4. **打开 OTA Package。** 点击 IPRO Home 上 **Tools** 下的 **OTA package**（或命令面板中的 `IPRO: OTA Package…`）。

    **应看到**：“OTA package of ipro_ble_remote”，下面一行说明这是上一次构建的 boot2 OTA 包，表格列出 **Firmware**、**Partition table**、**FW slots**（例如“A …, B …”）和 **boot2 image**（“v… (not part of the package)”）。缺少某项时，表格下方以红字说明，例如“Build the application first: the package is made from its firmware.”，此时无法点击 **Make Package**。

5. **制作。** **Version** 默认为当前时间（例如 `202611131542`），可以改为最多 15 个字符、不含空格的文本。点击 **Make Package**。

    **应看到**：按钮先变为“Making…”，**IPRO Flash** 依次显示 IntelProCube 和 `create_ota.py` 的输出。完成后出现“Package made”，列出 **File**（`apps/bluetooth/ble/ipro_ble_remote/build_reef/build_out/ipro_ble_remote.xz.ota`）、**Size**（“… (… bytes): a 512-byte header and … of XZ data”）、**Image inside**、**Version**、**SHA-256**、**Signature** 和 **Made**，最后一行为“The package is whole and fits the FW slots of this table.”

6. **只让开发板检查。** 在监视器打开的情况下，点击“Send to the board”下的 **Check on Board**。

    **应看到**：监视器先关闭，进度显示“Sending the OTA package of ipro_ble_remote to &lt;port&gt; for the board to check”；完成后显示“Sent in N s. The board found the package whole and installed nothing: it is in FW slot B, and the firmware that runs is the one that ran before.”，监视器重新打开。

7. **发送并安装。** 点击 **Send to Board**。

    **应看到**：进度显示“Sending the OTA package of ipro_ble_remote to &lt;port&gt;”，在 115200 baud 下约需 40 秒；完成后显示“Sent in N s. The board checked the package and is rebooting: boot2 installs it, and the monitor shows the new firmware start.”重新打开的监视器中先是 boot2 安装 OTA 包的信息，然后是新固件的启动信息。

</div>

![发送之后的 OTA Package 页面：“Package made”表格列出文件、大小、包内镜像、版本、SHA-256、签名（Not signed）与生成时间；“Send to the board”下有 Send to Board 与 Check on Board 两个按钮，下方消息表示已在 38 秒内发送完毕、开发板已检查 OTA 包并正在重启](../assets/workbench/ota-send.svg)

!!! note
    - **Signature** 显示 OTA 包头中有没有签名块：“Signed: the header carries a signature block”或“Not signed”。此页面制作的 OTA 包不加签名；签名 OTA 包请参阅 [OTA 更新](../guides/ota.md)。
    - 发送过程中点击 **Stop**，会显示“Stopped. The board asks for the rest for about 20 seconds, then gives up and returns to its shell; nothing was installed.”
    - OTA 包大于 FW 分区 B，或包内镜像大于 FW 分区 A 时，“Package made”下方会以警告或错误说明。
    - 用[新建应用程序](first-run.md#own-app-ble)创建、勾选了 **With OTA** 的 BLE peripheral 已带有上述配置和 A/B 分区表，可以直接从第 3 步开始。

## 通过开发板自身的 USB 烧录 { #usb-flash }

有些开发板的控制台就在开发板自身的 USB 端口上（USB CDC），例如 IPRO7AI Sensor Tag，不需要 IPRO Debug Probe。所选端口是这种 USB 端口时，**Flash** 改为通过 boot2 的 USB 下载模式，使用 SDK 的 `tools/ipro_dl.py`（SDK V2.3.0）写入固件、校验并启动固件。此功能仅在 macOS 版中提供。

IDE 在以下情况下走这条路径，其他情况照常使用 IntelProCube 通过探针烧录：

- 所选端口是 boot2 的 USB 下载端口（开发板上没有固件，或已经进入下载模式）；
- 所选端口不属于探针，并且应用程序的配置中有 `CONFIG_CHERRYUSB_DEVICE_CDC=y` 和 `CONFIG_SHELL=y`（控制台和 shell 在 USB 上）。此时 IDE 先在控制台输入 `reboot_usb`，让运行中的开发板重启并进入下载模式。

下面以 IPRO SDK V2.3.0 的 [`ipro7ai_sensor_tag_demo`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.3.0/apps/platform/ipro7ai_sensor_tag_demo) 在 IPRO7AI Sensor Tag 上为例。

<div class="ipro-steps" markdown>

1. **连接开发板。** 用 USB 线将 IPRO7AI Sensor Tag 的 USB 端口连接到 Mac。

2. **选择应用程序并构建。** 在侧边栏的 **Applications** 下点击 **ipro7ai_sensor_tag_demo**（位于 `platform` 类别），然后点击 **Build**。

    **应看到**：构建完成的通知，固件位于 `build/build_out/ipro7ai_sensor_tag_demo_IPRO7.bin`。

3. **选择开发板的端口。** 点击工具栏上的开发板名称，选择 **Select Port…**。

    **应看到**：列表按“IPRO Debug Probes”“Other USB serial ports”等分组；开发板的端口列在“Other USB serial ports”下，例如 `/dev/cu.usbmodemXXXX`。选择它。

4. **烧录。** 点击 **Flash**（`Cmd+Alt+U`）。

    **应看到**：**IPRO Flash** 依次显示：

    ```text
    Flashing over the board's own USB (boot2's USB downloader) with tools/ipro_dl.py
    Typing reboot_usb on /dev/cu.usbmodemXXXX: the board restarts into the downloader
    boot2's USB downloader is on /dev/cu.usbmodemYYYY
    ```

    接着是 `ipro_dl.py` 的写入进度和 `verify OK`。完成后通知“Flashed ipro7ai_sensor_tag_demo in N s.”，开发板以新固件重启，IDE 重新选回开发板的端口（端口名称改变时，**IPRO Flash** 的最后一行为 `The board is back on …`）。

5. **查看输出。** 点击 **Serial Monitor**。

    **应看到**：开发板每秒打印 20 行 `名称:数值`，例如 `ax:0.012 ay:-0.004 az:1.003 …`。这些数值可以用[传感器仪表板](monitor.md#dashboard)显示。

</div>

!!! note
    - 这条路径只写入固件：分区表、boot2 和 mfg 都保持不变，**Partition Table** 中选择的分区表也不会用到。
    - 开发板没有进入下载模式时（例如固件没有 USB 控制台），IDE 显示“The board did not start boot2's USB downloader. Flash again, and while it waits (20 s), unplug the board's USB cable and plug it in: boot2 listens for the downloader at power-on.”照做即可。
    - 在 Windows 版中选择开发板自身的 USB 端口时，显示“… is the board's own USB port. Flashing over it is not available on Windows yet: flash from macOS, or connect the IPRO Debug Probe and select its port.”
    - SDK 中没有 `tools/ipro_dl.py`（V2.3.0 之前）时，显示“… is the board's own USB port, and this SDK has no tools/ipro_dl.py to flash over it. IPRO SDK V2.3.0 and later have it.”

## IPRO6S EVK { #ipro6s }

IPRO Workbench 可以构建、烧录和监视 IPRO SDK 中的 IPRO6 应用程序（`.config` 中为 `CONFIG_CHIP="IPRO6"`）；开发板为 IPRO6S EVK。本节使用 IPRO SDK V2.3.0 的 `platform/ipro6_demo`。芯片、它的应用程序以及用命令行烧录的方法，请参阅 [IPRO6S](../hardware/chips/ipro6s.md)。

| 项目 | 版本 |
|---|---|
| IPRO Workbench | 0.2.0 |
| IPRO SDK | V2.3.0（2.2.1 或更高版本也能构建、烧录和监视，但 **Board** 不显示开发板上运行的固件） |
| IntelProCube | 0.7.0.1 或更高版本（带有 IPRO6S 的分区表 `partition_cfg_fw_direct.toml`） |

### 构建、烧录并监视 ipro6_demo { #ipro6s-run }

<div class="ipro-steps" markdown>

1. **连接探针和开发板。** 用 USB 线将 IPRO Debug Probe 连接到计算机，再将探针连接到 IPRO6S EVK。

    **应看到**：侧边栏的 **Board** 下出现 **IPRO Debug Probe** 及其 UART 和 CCI 两个端口。

2. **选择应用程序。** 在侧边栏的 **Applications** 下点击 **ipro6_demo**（位于 `platform` 类别；可以在搜索框中输入 `ipro6`）。

    **应看到**：工具栏显示 `ipro6_demo`，开发板自动变为 **IPRO6S EVK**；侧边栏 **Board** 下的芯片标签为 `IPRO6S`。开发板跟随应用程序的芯片，无需自己选择。

3. **连接了两块开发板时选择端口。** 同时连接两块开发板时（例如一块 Reef 和一块 IPRO6S EVK，各接一个探针），点击工具栏上的开发板名称，选择 **Select Port…**，然后选取 IPRO6S EVK 所接探针的 UART。只有一块开发板时可跳过这一步。

4. **构建、烧录并监视。** 点击 **Build, Flash and Monitor**（`Cmd+Alt+R` / `Ctrl+Alt+R`）。

    **应看到**，依次为：

    1. **IPRO Build** 编译到 `[100%] Built target ipro6_demo_IPRO6.elf`。
    2. **IPRO Flash** 的第一行为“Partition table: …/chips/ipro6/partition/partition_cfg_fw_direct.toml”；其后的命令带有 `--chipname ipro6 --chip-variant IPRO6S` 和 `--pt …/partition_cfg_fw_direct.toml`；最后一行为 `[All Success]`。
    3. **IPRO Monitor** 打开，开发板重启，输出以 `Init Shell (RT-Thread FinSH based)` 和提示符 `ipro />` 结束。
    4. 侧边栏 **Board** 下多出一行“Runs ipro6_demo (built …)”：IPRO SDK V2.3.0 的 IPRO6 固件启动时打印 `Build:<时间>,<日期>`，IDE 据此核对开发板上的固件。

5. **列出开发板的命令。** 在监视器中输入 `help` 并按 Enter。

    **应看到**：开发板列出它的命令，其中包括 Wi-Fi 命令（`stack_wifi`、`wifi_sta_connect`、`wifi_ap_start`）和 `iperf`。[Wi-Fi 吞吐量（iperf）](measure.md#iperf)（见[测试与测量](measure.md)）会用到这些命令。

</div>

![IPRO Workbench 的整个窗口：工具栏显示 ipro6_demo 和 IPRO6S EVK，IPRO Home 显示内存用量条，IPRO Monitor 以“Init Shell (RT-Thread FinSH based)”和提示符结束，通知显示构建和烧录已完成](../assets/workbench/ipro6s-run.svg)

!!! warning "重要"
    IPRO6S EVK 必须使用 `partition_cfg_fw_direct.toml` 烧录；IDE 会自动选择它。IntelProCube 版本太旧、没有这个分区表时，IDE 不会烧录，并显示“IntelProCube has no partition_cfg_fw_direct.toml, the partition table ipro6_demo flashes with. Without one the board would not boot. Update IntelProCube, or choose a partition table for ipro6_demo.”点击 **Install IntelProCube** 安装新版本，然后重新烧录。

### 为 IPRO6S EVK 创建应用程序 { #ipro6s-new-app }

<div class="ipro-steps" markdown>

1. **新建应用程序。** 点击 **Applications** 列表上方的 **+**（**New Application…**）。

2. **填写表单。** 在 **Start from** 中选择 **Hello World for a board**；在 **Board** 中选择 **IPRO6S EVK**；名称输入 `my_wifi_app`，然后点击 **Create**。

    **应看到**：列表中新增 `user/my_wifi_app`，工具栏上的开发板为 **IPRO6S EVK**，编辑器打开它的 `main.c`。

3. **运行。** 点击 **Build, Flash and Monitor**。

    **应看到**：IPRO Monitor 中出现 `Hello from my_wifi_app`。

</div>

![New IPRO Application 对话框：Start from 选择了“Wi-Fi station for the IPRO6S EVK (a copy of ipro6_demo, Wi-Fi configuration)”，下方说明 SDK 的 IPRO6S Wi-Fi 库是按这组配置预先编译的，接着是名称与分类](../assets/workbench/new-app-ipro6s.svg)

要创建 Wi-Fi 应用程序时，在 **Start from** 中改选 **Wi-Fi station for the IPRO6S EVK (a copy of ipro6_demo, Wi-Fi configuration)**，输入名称后点击 **Create**。

**应看到**：对话框下方提示“The SDK's Wi-Fi libraries for the IPRO6S are prebuilt for this configuration: keep its Wi-Fi and low-power options as they are.”；创建的应用程序是 `ipro6_demo` 的副本，`.config` 为它的 Wi-Fi 配置，所需的 Wi-Fi 库也一并复制。烧录后在监视器中输入 `help`，可以看到与 `ipro6_demo` 相同的 Wi-Fi 命令和 `iperf`，可以直接用 [Wi-Fi 吞吐量（iperf）](measure.md#iperf)测量。

### 与 IPRO7 系列的不同之处 { #ipro6s-differences }

IPRO6 系列开发板启动时不打印分区表和 Flash ID；固件的构建时间（`Build:` 那一行）从 IPRO SDK V2.3.0 起才打印。以下功能在 IPRO6S EVK 上与 IPRO7 系列不同：

| 功能 | 在 IPRO6S EVK 上 |
|---|---|
| 核对开发板上的固件（**Board** 下的“Runs …”一行） | IPRO SDK V2.3.0：与 IPRO7 系列相同。2.2.1 及更早版本：不显示，请以 **IPRO Flash** 中的 `[All Success]` 和监视器中的启动信息确认烧录结果。 |
| 将分区表与开发板上的进行比对（**On the board**） | 不比对。**Partition Table** 仍会显示烧录时写入的分区表。 |
| 启动时识别开发板的 Flash | 启动时不识别。烧录一次之后，**Board** 显示 IntelProCube 在烧录时读到的 Flash（例如“Flash Winbond 2 MB”）。 |
| 崩溃地址解码 | 与 IPRO7 系列相同：IPRO6S 的固件崩溃时打印同样格式的报告，IPRO Monitor 会进行解码，请参阅[崩溃地址自动解码](debug.md#crash-decode)。 |
| AI 模型 | 不适用（NPU 是 IPRO7AI 的功能）。 |
| OTA 包 | 不适用（boot2 OTA 包只适用于 IPRO7 的应用程序）。 |

构建、烧录、串口监视器、[Settings (Kconfig)](develop.md#kconfig)、[配置文件](develop.md#configurations)、[引脚配置](develop.md#pins)、[内存映射](develop.md#memory)和 [Wi-Fi 吞吐量（iperf）](measure.md#iperf)的用法与其他页面的说明相同；IPRO6S 的 Wi-Fi 内存 profile 也在 Wi-Fi 吞吐量页面设置，请参阅 [Wi-Fi 内存 profile](measure.md#wifi-profile)。
