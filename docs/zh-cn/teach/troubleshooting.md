---
title: "Teach 故障排除"
description: IPRO AI Teach 常见情况的原因与处理方法：找不到开发板、模式或 USB 设备不对、摄像头没有画面、烧录失败、部署被拒绝或中断、看门狗重启，以及 ipro-ai 命令行的退出码。
---

# Teach 故障排除

按类别列出 IPRO AI Teach 的常见情况。界面与控制台上的信息按原文列出，方便对照；每个工具页面也有该工具的故障排除。

## 先确认以下几点 { #checklist }

1. **USB-C 线支持数据传输。** 仅支持充电的线会让开发板亮灯，但电脑枚举不出任何 USB 设备。
2. **USB-C 接在 Reef 自身的 USB-C（USB1）上。** IPRO Debug Probe 的 USB 口只提供控制台与烧录，Teach 工具不经过它。
3. **开发板运行的是 Edge AI 固件。** 控制台的启动信息中有 `IPRO7AI Reef Teach: image, voice, sensor` 与 `mode:` 一行。
4. **开发板的模式与要使用的页面相符。** `image` 对应 **Teach**、`voice` 对应 **Audio**、`sensor` 对应 **Sensor**；不相符时页面上方会出现 **Switch to …**。
5. **没有其他程序占用开发板的 USB 串口。** 同一时间只能有一个程序打开它。

## 连接与模式 { #connection }

| 现象 | 原因 | 处理 |
|---|---|---|
| 电脑上没有出现 Reef 的 USB 设备 | USB-C 线仅支持充电，或固件没有启动 | 换一条支持数据传输的线；查看控制台的启动信息 |
| LED2（电源指示灯）不亮 | USB-C 没有供电，或保险丝因过流暂时断开 | 换一条线或一个 USB 口；拔掉 40-pin 排针上的扩展板后再试 |
| Studio 显示 `The Reef is in <模式> mode.` | 开发板当前处于其他模式 | 点击页面上的 **Switch to …** |
| 点击 **Switch to …** 后显示 `This Reef's firmware runs one Teach only.` | 板上不是 Edge AI 固件，而是只有单一工具的固件 | 按[烧录 Edge AI 固件](firmware.md)改为烧录 `ipro_reef_teach` |
| 点击 **Switch to …** 后显示 `The Reef did not switch.` | 切换指令没有完成，例如串口被占用 | 关闭其他打开了开发板串口的程序后再点击一次；或在控制台输入 `mode <模式>` |
| 页面找到了另一块开发板 | 多块 Reef 同时连接在电脑上 | 一次只连接一块；命令行用 `--port` 指定 |
| 启动信息或 `ipro-ai model list` 显示 `install_interrupted` | 上次部署没有完成（断电、复位、拔线） | 重新部署 |
| 启动信息或 `ipro-ai model list` 显示 `crc` | 已提交的模型内容损坏 | 重新部署 |
| 启动信息或 `ipro-ai model list` 显示 `no_xip` | 分区无法读取 | 用 `partition_reef_teach.toml` 重新烧录固件 |
| 部署被拒绝，信息中含 `size` | 模型超过槽位容量 | 改用较小的模型（传感器的 Medium、Small，或图像的 MobileNetV1 0.25） |

## 烧录 { #flashing }

| 现象 | 原因 | 处理 |
|---|---|---|
| 烧录工具已退出，但输出中没有 `[All Success]` | 烧录失败；工具失败时也以 0 退出 | 确认开发板处于下载模式、串口正确，再烧录一次 |
| 握手成功，但 Flash ID 为 `00000000`，ErrorCode `003D` | Flash 引脚配置错误 | 在烧录命令中加上 `--chip-variant IPRO7AI` |
| 烧录工具报告握手失败或无法打开串口 | 终端程序仍占用串口，或开发板不在下载模式 | 关闭终端程序；重新进入下载模式 |
| macOS 使用 `utils/ipro_flash.sh` 时出现 `[Errno 83] Device error`，ErrorCode `0003` | 探针让 Reef 进入下载模式后，它的串口短暂消失 | 等一两秒，再运行一次同样的命令 |
| macOS 上打开串口后卡住没有反应 | 使用了 `/dev/tty.*` | 改用 `/dev/cu.*` |
| 控制台没有任何输出，`reboot_dl` 没有作用 | 固件死机，shell 不可用 | 用按键（按住 SW1、按一下 SW2、松开 SW1）或探针进入下载模式，重新烧录 |
| 控制台看不到任何字符 | 排线两端线序相同，或打开了探针的另一个串口 | 改用两端线序对调的排线；打开探针的“IPRO7 UART”串口，115200 baud |
| 烧录到了另一块开发板 | 多块开发板同时连接在电脑上，`--port` 指向了别的板 | 烧录前通过控制台的启动信息确认开发板；不确定时一次只连接一块 |
| 改烧 Edge AI 固件后，图像与传感器都没有模型 | 原来的固件使用标准分区表，模型槽位的位置不同 | 正常现象；用 Studio 重新部署 |
| 用 Studio **Board** 页面的 **Flash** 烧录后，Teach 工具不正常 | Board 页面以标准分区表写入，没有 mfg 载荷 | 用 IntelProCube 按[烧录 Edge AI 固件](firmware.md#flashing)重新烧录 |

## 图像识别 { #image }

| 现象 | 原因 | 处理 |
|---|---|---|
| 摄像头列表里没有 **IPRO7 UVC Cam**；Studio 显示 `No board with the Teach firmware on USB.` | 开发板不在 `image` 模式，或 USB-C 线仅支持充电 | 切换到 `image` 模式；换一条支持数据传输的线 |
| Teach 页面显示 `IPRO AI Studio is not allowed to use the camera.` | macOS 曾拒绝摄像头权限 | 在“系统设置 → 隐私与安全性 → 摄像头”中打开 IPRO AI Studio，再重新打开 Studio |
| Windows 上 Teach 页面没有摄像头画面 | 系统的摄像头隐私设置不允许桌面应用访问 | 在“设置 → 隐私和安全性 → 摄像头”中允许桌面应用访问摄像头 |
| macOS 上所有程序都看不到摄像头画面 | 另一个程序仍占用摄像头 | 关闭那个程序，再重新插拔 USB-C |
| 控制台反复出现 `no camera answers` | 摄像头没有接好，或 SW7 不在 CAM | 拔掉 USB-C，检查摄像头排线，把 SW7 拨到 CAM |
| 40-pin 排针上的部分 GPIO 没有反应 | 这些引脚经过摄像头切换芯片，SW7 在 CAM | 使用摄像头时这是正常的；要使用这些 GPIO 时把 SW7 拨到 GPIO（摄像头电源会关闭） |
| 画面显示 `NO MODEL: NO MODEL IN MFG` | 还没有部署模型 | 用 Teach 页面部署 |
| 画面显示 `NO MODEL: DEPLOY INTERRUPTED` | 上次部署没有完成 | 重新部署 |
| 画面显示 `NO MODEL: NO MFG PARTITION` | 烧录时使用的分区表没有 mfg 分区 | 用 `partition_reef_teach.toml` 重新烧录固件 |
| 画面显示 `NO MODEL: WRONG MODEL` | 槽位中是其他类型的模型 | 重新部署一次 |
| 部署后 Camera 区域显示 `The board went away. Waiting for it…` | 开发板正在重启 | 正常现象，摄像头会自动恢复；没有恢复就重新插拔 USB-C |
| 训练结果显示 `<A> taken for <B>` | 录制时物品离开了方框 | 对这两类点击 **Review**，删除不好的图片后重新训练 |
| 实际使用时经常把某一类误判成另一类 | 某些角度或光线的数据不足，或两类外观相近 | 在误判的角度与光线下补录，再训练、部署 |

## 声纹识别 { #voice }

| 现象 | 原因 | 处理 |
|---|---|---|
| Audio 页面显示开发板没有声纹模型，或控制台显示 `NO MODEL` | 板上没有有效的声纹模型 | 用带 `--mfg` 的命令重新烧录，或用 `ipro-ai deploy` 部署声纹模型，见[更换声纹模型](voice.md#voice-model) |
| 无法打开开发板的串口 | 其他程序占用了开发板的串口 | 关闭其他使用该串口的程序后再试 |
| 注册失败，原因为 `Too little speech was heard` | 听到的语音太少 | 说话大声一点或靠近一点，持续朗读到时间结束 |
| 未注册的人一直被标上某位已注册者的名字 | 普通模式下名称阈值偏低；扬声器播放的声音尤其如此 | 开启陌生人模式，或调高 **Name match** |
| 已注册的人经常被标为 Speaker k | 注册时的位置、麦克风或音量与实际使用时不同，或名称阈值太高 | 在实际位置用 Reef 的麦克风重新注册；或稍微调低 **Name match** |
| 同一个人被拆成好几位 Speaker | 新说话人阈值太高 | 调低 **New speaker**，或为其中一位命名 |
| 没有人说话时也出现标签 | 音乐、电视等持续声音被当成语音 | 移除背景声源，在安静的环境中使用 |
| 更换声纹模型后，已注册的人都不见了 | 声纹与模型绑定 | 用新模型重新注册 |
| 无法在控制台用中文名字注册或命名 | 控制台只接受 ASCII 字符 | 在 Audio 页面输入名字 |

## 传感器识别 { #sensor }

| 现象 | 原因 | 处理 |
|---|---|---|
| **Put it on the board** 显示 `Connect a Reef running the Edge AI firmware to its own USB-C port.` | 找不到处于 `sensor` 模式的开发板 | 确认固件与 USB-C 线；USB-C 要接在 Reef 自身的接口上 |
| `Not ready to train` | 开发板未连接，或有录音的类别不足 2 类（异常检测模式要恰好 1 类） | 连接开发板并补录类别 |
| `too short: hold for at least one window` | 按住的时间短于一个窗口 | 按久一点 |
| `<k> of <n> classes have no held-out data` | 有类别每次录制的时间太短，无法留出验证数据 | 每次按住超过窗口长度的 2 倍 |
| **Import CSV…** 显示 `<N> columns` | CSV 的列数与数据源的通道数不同 | 每列一个通道、每行一个采样点 |
| **Open…** 显示 `Not a Sensor Teach folder` | 文件夹中没有 `sensor_teach.json` | 打开由 **Save…** 保存的文件夹 |
| 部署失败：`the board did not come back with the model within 30 s` | 开发板没有在 30 秒内带着新模型恢复 | 重新插拔 USB-C 后确认控制台的启动信息，再部署一次 |
| 更换数据源后，原来训练好的模型不能用 | 模型只适用于训练时的数据源 | 在新的数据源上重新录制与训练 |
| 实时结果在状态转换时出现 `UNKNOWN` | 窗口同时包含两种状态 | 正常现象；根据连续几次的结果判断 |
| 异常检测在正常的重负载下也报警 | 正常数据没有覆盖这种负载 | 在各种正常负载、转速下补录正常数据，重新训练 |

## 运行中与看门狗 { #runtime }

| 现象 | 原因 | 处理 |
|---|---|---|
| 没有任何操作，开发板却自行重启（控制台重新出现启动信息） | 系统卡死后，固件内置的看门狗在约 5.6～8 秒内让开发板重启；例如 NPU 执行了损坏的模型 | 开发板回到原来的模式，模型都会保留。重新部署经过验证的模型；记录当时的操作与控制台信息，反馈给 INTELPRO |
| 想确认看门狗是否已启用 | | 在控制台输入 `watchdog` 查看状态；`watchdog test` 停止喂狗，开发板应在数秒内重启 |
| 部署过程中拔掉 USB-C 或复位 | 部署在提交前被中断 | 该工具没有模型（`install_interrupted`），重新部署即可；另外两个工具的模型不受影响 |

## ipro-ai 命令行 { #cli }

`ipro-ai` 的设备与模型命令以固定的退出码报告结果，加上 `--json` 时标准输出只有一份 JSON，`error.type` 说明错误类型。

| 退出码 | 含义 | 处理 |
|---|---|---|
| `0` | 成功 | |
| `1` | 检查不符：模型套件损坏、`verify` 不一致、部署后回读的 CRC 或大小不对 | 确认板上模型的 CRC 与模型套件相同；重新生成模型套件 |
| `2` | 用法错误：参数错误、文件无法读取、USB 上有多块开发板却没有给出 `--port` | 修正参数；用 `--port` 指定开发板 |
| `3` | 找不到设备，或串口在中途消失 | 确认 USB-C 线与固件；用 `ipro-ai device list` 查看 |
| `4` | 开发板拒绝（例如 `TDEP ERR crc`）或回复无法解析 | 根据回复内容处理；重新部署 |
| `5` | 超时：开发板没有响应，或重启后没有恢复 | 查看控制台的启动信息；用 `ipro-ai device list` 确认 |
| `6` | 不兼容：固件不支持这个功能（例如 Edge AI 固件不支持回滚）、工具类型或 ABI 不匹配、放不下 | 根据信息改用合适的模型或命令 |
| `7` | 工具内部错误 | 保留 `--json` 的输出，反馈给 INTELPRO |

## 反馈问题 { #report }

联系 INTELPRO 时，请附上：

- 控制台从启动到出现问题的完整信息（IPRO Debug Probe 的“IPRO7 UART”串口，115200 baud）。
- `ipro-ai device info --json` 的输出：固件、平台版本、模式与板上模型。
- IPRO AI Studio 的版本（Windows 在 **Help** 菜单中，macOS 在应用程序菜单的 **About IPRO AI Studio** 中）与操作系统。
- 操作步骤，以及界面上显示的信息原文。
