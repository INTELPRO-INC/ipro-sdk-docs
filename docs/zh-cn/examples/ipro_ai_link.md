---
title: ipro_ai_link
description: IPRO AI Studio“Run on board”的板端固件：从 microSD（sd:/）加载 .inm 模型与输入、在 NPU 上推理、输出原始结果；也可在控制台手动操作
generated: tools/gen_examples.py
migrate_from: []
---

# ipro_ai_link

IPRO AI Studio“Run on board”的板端固件：从 microSD（`sd:/`）加载 `.inm` 模型与输入、在 NPU 上推理、输出原始结果；也可在控制台手动操作

| 项目 | 内容 |
|---|---|
| 源代码 | [`apps/test/ipro_ai_link`](https://github.com/INTELPRO-INC/IPRO-SDK/tree/IPRO-SDK-V2.2.0/apps/test/ipro_ai_link) |
| 开发板与配置 | Reef（`defconfig_reef`）；`.config` 对应 IPRO7 EVB |
| 控制台 | UART 115200（另有 USB CDC 控制台） |
| 构建 | Reef：`make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef` |

## 在 Reef 上运行 { #on-the-reef }

这个应用没有 README，以下根据源代码整理。需要一张 FAT 格式的 microSD 卡。

<div class="ipro-steps" markdown>

1. **构建**

    ```bash
    make -C apps/test/ipro_ai_link DEFCONFIG=defconfig_reef
    ```

    镜像位于 `apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin`。

2. **烧录**：进入[下载模式](../hardware/boards/reef-evk.md#download-mode)，在 IntelProCube 目录执行

    ```bash
    ./ipro_iot_tool_macos --chipname ipro7 --chip-variant IPRO7AI \
        --port /dev/cu.usbserial-XXXX --baudrate 921600 \
        --firmware <SDK>/apps/test/ipro_ai_link/build_reef/build_out/ipro_ai_link_IPRO7.bin
    ```

    确认 `[All Success]` 后按一下 SW2。

3. **运行**：以 115200 baud 打开控制台，开机打印 `ipro_ai_link ready`。USB-C 连接电脑时，开发板显示为两个 CDC 串口（VID `0x3896`、PID `0x0704`）：第一个传输数据，第二个是控制台。

4. **手动推理**：把 `.inm` 模型与原始输入文件复制到 SD 卡，插入卡座后依次输入

    ```text
    ai_mount
    ai_load sd:/model.inm
    ai_input sd:/input.bin
    ai_run
    ai_out
    ```

    `ai_out` 以十六进制打印输出张量，每个字节都以 XOR 0x80 存储。路径一律以 `sd:/` 开头。

</div>

SDK 随附可用的模型，例如 `apps/platform/ipro7_demo/demo/ai/ai_model/mbv2.inm`。IPRO AI Studio 可从 [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下载。
