---
title: "图像识别"
description: 用 IPRO AI Studio 的 Teach 页面教 IPRO7AI Reef EVK 识别自己的物品：切换到 image 模式、确认摄像头、建立类别、录制、训练、部署，在板上查看结果并补录后重新训练。
---

# 图像识别

把物品放到 Reef 的摄像头前录制几秒、在电脑上训练、部署到开发板，之后开发板的 NPU 会实时识别画面中央方框里的物品，并把结果叠加在摄像头画面上。全程在 IPRO AI Studio 的 **Teach** 页面完成，无需编写代码。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK 已烧录 Edge AI 固件，见[烧录 Edge AI 固件](firmware.md)。
- OV5640 摄像头模组：在断电状态下把排线插入 FPC1，并确认 SW7 在 CAM 位置。插拔摄像头排线前务必先拔掉 USB-C。
- 一条支持数据传输的 USB-C 线，连接 Reef 的 USB-C 与电脑。
- 已安装 IPRO AI Studio，并允许它使用摄像头，见[安装 IPRO AI Studio](install.md)。

## 工作原理 { #how-it-works }

- OV5640 以 1280×720 采集，ISP 同时产生两路输出：640×360 的预览画面压缩成 MJPEG，作为标准 USB 摄像头（UVC）发送到电脑；画面中央的方框缩放成 128×128 送给 NPU。
- 预览画面中央的方框就是模型看到的范围。Teach 页面从预览画面中裁出同一个方框作为训练图片。
- 模型是冻结的 MobileNet 骨干网络加一个分类层，只训练最后一层，所以在电脑的 CPU 上几秒就能完成。每一层都在 NPU 上执行。
- 部署时，Studio 经 USB 串口把模型与类别名称发送到开发板；开发板先检查大小、CRC-32 与模型格式，确认无误才写入 Flash，再自动重启。
- 开发板把识别结果画在方框外面，方框里始终保持摄像头的原始图像，因为 Teach 页面要从这里裁出训练图片。

## 连接开发板 { #connect }

<div class="ipro-steps" markdown>

1. **接上 USB-C**：电脑上出现名为 **IPRO7 UVC Cam** 的摄像头与串口。没有出现时，说明开发板不在 `image` 模式，先执行下一步。

2. **打开 Teach 页面**：在 Studio 左侧导航栏点击 **Teach**（macOS 为 Command＋5，Windows 为 Ctrl＋5）。开发板处于其他模式时，页面上方出现 `The Reef is in … mode.` 与 **Switch to Teach**，点击后等待开发板重启（约 2 秒）。也可以在控制台输入 `mode image`。

3. **确认摄像头画面**：**Camera** 区域出现 Reef 的摄像头画面，中央有绿色方框。板上还没有图像模型时，画面上方显示 `IPRO AI TEACH` 与 `NO MODEL`。

4. **确认状态**：页面上方状态栏的 **Board** 显示 `on USB`；**Put it on the board** 区域显示开发板当前的状态，例如 `Board found, no model on it yet.` 或 `Running 3 classes: …`。

</div>

## Teach 页面的界面 { #page-layout }

| 区域 | 说明 |
|---|---|
| 状态栏 | **Board**（`on USB` 表示找到开发板）、**Crops**（已采集的图片数）、**Held-out accuracy**（留出验证准确率）、**Last deploy**（上次部署所用的时间） |
| **Camera** | Reef 的摄像头画面。绿框是模型看到的范围，方框外是开发板叠加的识别结果。左下角的 **Mirror** 只对预览做左右镜像、不影响训练，默认关闭 |
| **Hold to record** | 按住录制当前选中的类别，每秒采集 5 张，松开即停止；按钮上显示类别名称，例如 **Hold to record CLASS 1** |
| **Classes** | 类别列表。每行有名称、图片数、最近的缩略图，以及 **Review**（查看并删除不好的图片）、**Clear**（清除这一类的所有图片）、**Remove**（删除类别；BACKGROUND 不能删除）。上方有 **Open…**、**Save…**、**+ Add class** |
| **Train** | 骨干网络的下拉菜单与 **Train** 按钮；下方显示训练结果 |
| **Put it on the board** | 开发板当前运行的模型与 **Deploy** 按钮；下方逐步显示部署进度 |

## 建立类别并录制 { #collect }

<div class="ipro-steps" markdown>

1. **命名类别**：列表默认有 **BACKGROUND**、**CLASS 1**、**CLASS 2**。点击名称字段即可重命名，点击 **+ Add class** 增加类别，最多 8 类。名称可使用英文字母、数字、空格、下划线、连字符与句点，最多 15 个字符；Studio 会转换为大写。开发板用内置的点阵字体显示名称，所以不支持中文。

2. **录制 BACKGROUND**：选中 **BACKGROUND**，方框内什么都不放，按住 **Hold to record** 几秒。这一类让开发板能回答“没有东西”，必须录制。

3. **录制每一类物品**：点击要录制的类别，把物品放进方框，按住 **Hold to record** 几秒。录制中预览画面的方框变成红色，标示 `REC` 与类别名称；类别旁的数字是这一类已采集的图片数。

4. **检查图片**：每一类录完后点击 **Review**，删除不好的图片，例如物品有一半在方框外的画面。整类需要重录时点击 **Clear**。

</div>

录制要点：

- 小物品要靠近镜头，让它占满方框的大部分。
- 录制时慢慢转动、前后移动物品，让模型看到不同的角度与距离。外观或颜色相近的两类，在某些角度可能互相误判，请在这些角度多补录。
- 在实际使用的光线与背景下录制。训练时会自动为每张图加上左右镜像与两种亮度变化，无需另外录制镜像。
- 预览画面默认不镜像，看到的就是摄像头实际拍到的方向；如果想像照镜子一样操作，勾选 **Mirror**，不影响训练。

## 训练 { #train }

<div class="ipro-steps" markdown>

1. **选择骨干网络**：在 **Train** 的下拉菜单中选择一个（见下表）。默认是 MobileNetV2 0.35。

2. **点击 Train**：训练在电脑的 CPU 上进行，通常几秒内完成。至少要有两类有图片，否则显示 `Record at least two classes, then train.`；没有图片的类别会被跳过。

3. **查看结果**：完成后显示 `Trained in <秒数> s: <百分比> of held-out crops right`，状态栏的 **Held-out accuracy** 同步更新。

</div>

每一类每 4 张图片中留出 1 张不参与训练，训练完后用来评分，这就是 **Held-out accuracy**。同一次录制的图片彼此很像，所以这个分数只代表“这些类别能区分开”，不代表换一个场景也一样准确。图片太少、无法留出验证数据时，显示 `Too few crops to hold any out for checking.`。

结果中出现 `<A> taken for <B> (<n>x)` 时，表示有 n 张 A 类的图片被判为 B 类，常见原因是录制时物品离开了方框。对这两类点击 **Review**，删除这些图片后重新训练。

| 下拉菜单的选项 | 特点 | 模型大小 |
|---|---|---|
| MobileNetV2 0.35（默认） | 较准确 | 461 KB |
| MobileNetV1 0.25 | 较快，模型约小一半 | 237 KB |

菜单上标示的 NPU 时间为近似值；INTELPRO 用 Edge AI 固件 2.0.0 实测，MobileNetV2 0.35 在板上 NPU 每次约 10.5 ms。

## 部署 { #deploy }

<div class="ipro-steps" markdown>

1. **确认开发板**：**Put it on the board** 区域找到了开发板，并显示开发板当前运行的类别或 `Board found, no model on it yet.`。

2. **点击 Deploy**：Studio 依次执行三个步骤并打勾：**Compile the model**（生成模型）、**Send and write**（发送并写入）、**Restart the board**（重启）。

3. **等待摄像头恢复**：开发板重启时摄像头画面会暂时消失，画面显示 `Deploying… the camera comes back when the board does.`，这是正常的；重启后摄像头自动恢复。

4. **确认完成**：显示 `On the board in <秒数> s` 与 `It now recognises …`，列出开发板现在能识别的类别。

</div>

开发板在写入前会先检查收到的模型；被拒绝时，板上原有的模型不受影响，可以直接再部署一次。写入过程中断电或拔线时，由于图像识别只有一个槽位，板上会没有模型，摄像头画面显示 `NO MODEL: DEPLOY INTERRUPTED`，重新部署即可。

## 在板上查看结果 { #run }

部署完成后，把物品放进方框，开发板的 NPU 实时识别，并把结果叠加在摄像头画面上：

| 位置 | 内容 |
|---|---|
| 上方 | `IPRO AI TEACH`、NPU 每次识别的时间与每秒识别次数 |
| 方框左侧 | 得分最高的类别及其置信度 |
| 方框右侧 | 每个类别的概率；得分最高的一类以绿色显示 |
| 下方 | 模型的类别数，例如 `3 CLASSES` |

这个画面是 Reef 自己绘制到 USB 摄像头图像中的，任何能打开 USB 摄像头的程序都能看到，不限于 Studio。

在控制台也可以确认状态：

| 命令 | 作用 |
|---|---|
| `teach` | 模型状态、类别列表与实时概率、NPU 速率、USB 连接状态 |
| `teach print on`／`teach print off` | 在控制台打印每一条结果 |
| `teach mirror on`／`teach mirror off` | 镜像开发板发送的摄像头画面（默认关闭；Teach 页面需要摄像头的原始方向，平时请保持关闭） |
| `teach dump` | 转储当前送给 NPU 的 128×128 输入 |

## 验证结果 { #verify }

1. 每一类物品放进方框时，方框左侧显示该类的名称，右侧该类的概率最高并以绿色显示。
2. 方框为空时显示 **BACKGROUND**。
3. 画面下方的类别数与 Teach 页面的类别数相同。
4. 重新插拔 USB-C 或重启后，模型仍在板上：摄像头画面不再显示 `NO MODEL`，**Put it on the board** 显示 `Running <n> classes: …`。

## 补录与重新训练 { #iterate }

训练分数只代表采集到的图片能区分开。请在实际场景中测试，发现误判就针对那个角度或光线补录，再训练、部署一次：

1. 选中误判的类别，在误判的角度与光线下按住 **Hold to record** 补录；必要时点击 **Review** 删除不好的图片。
2. 点击 **Train**。类别或图片改变后，训练结果区域会提示 `The crops changed since training. Train again.`。
3. 点击 **Deploy**。

保存与重用采集到的图片：

- **Save…**：选择一个文件夹，Studio 在其中为每一类建立一个子文件夹，保存为 PNG 图片。
- **Open…**：打开同样结构的文件夹（每类一个子文件夹，`.png` 或 `.jpg`），就能补录或重新训练，无需从头采集。128×128 的图片直接作为训练图片，其他尺寸的图片作为摄像头画面，裁出中央方框。文件夹名称就是类别名称。
- 同一个文件夹也可以不打开窗口，用命令行训练成模型套件再部署：

    ```bash
    ipro-ai train image <文件夹> --out cups.ipkg --backbone mnv2_035
    ipro-ai deploy cups.ipkg --switch
    ```

    `--backbone` 可以是 `mnv2_035`（MobileNetV2 0.35）或 `mnv1_025`（MobileNetV1 0.25）。

## 规格 { #specs }

| 项目 | 规格 |
|---|---|
| 摄像头画面（USB 摄像头） | 640×360 MJPEG，USB Full-Speed |
| 模型输入 | 画面中央方框（预览画面的 x 192–447、y 52–307），缩放成 128×128 RGB |
| 类别数 | 2～8 类（含 BACKGROUND） |
| 类别名称 | 最多 15 个字符：英文大写字母、数字、空格、下划线、连字符与句点 |
| 训练方式 | 冻结的 MobileNet 骨干网络，只训练最后一层；在电脑的 CPU 上运行 |
| 模型 | MobileNetV2 0.35（461 KB，63 层全部在 NPU 上）或 MobileNetV1 0.25（237 KB） |
| 板上 NPU 时间 | MobileNetV2 0.35 约 10.5 ms；模型加载约 0.74 秒 |
| 模型存放位置 | 图像模型槽位，可容纳 508 KB |

## 使用建议 { #tips }

- **必须有 BACKGROUND 类别。** 没有它，方框为空时开发板仍会从已知类别中挑一个作为回答。
- **图像识别没有“不认识”这个答案。** 没教过的物品会被归到最相似的一类，而且置信度可能很高。会出现在画面中的其他物品，请另外建立一个类别（例如 OTHER）并录制。
- 方框里的画面才是模型看到的内容；物品只出现在方框外时不会被识别。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| 摄像头列表里没有 **IPRO7 UVC Cam**；Studio 显示 `No board with the Teach firmware on USB.` | 开发板不在 `image` 模式、没有 Edge AI 固件，或 USB-C 线仅支持充电 | 在 Teach 页面点击 **Switch to Teach** 或在控制台输入 `mode image`；换一条支持数据传输的线 |
| Camera 区域一直显示 `Looking for the IPRO7 UVC Cam…` | 同上 | 同上 |
| macOS 上 Camera 区域没有画面，显示摄像头权限信息 | IPRO AI Studio 没有摄像头权限 | 见[操作系统权限](install.md#permissions) |
| macOS 上所有程序都看不到摄像头画面 | 另一个程序仍占用摄像头 | 关闭那个程序，再重新插拔 USB-C |
| 控制台反复出现 `no camera answers` | 摄像头没有接好，或 SW7 不在 CAM | 拔掉 USB-C，检查摄像头排线，把 SW7 拨到 CAM |
| 摄像头画面显示 `NO MODEL: NO MODEL IN MFG` | 还没有部署图像模型 | 训练后点击 **Deploy** |
| 摄像头画面显示 `NO MODEL: DEPLOY INTERRUPTED` | 上次部署没有完成 | 重新部署 |
| 摄像头画面显示 `NO MODEL: WRONG MODEL` | 槽位中是其他类型的模型 | 重新部署一次 |
| Camera 区域显示 `The board went away. Waiting for it…` | 开发板正在重启（例如刚部署或切换模式），或 USB-C 被拔掉 | 部署后属于正常现象，摄像头会自动恢复；没有恢复就重新插拔 USB-C |
| 训练结果显示 `<A> taken for <B>` | 录制时物品离开了方框 | 对这两类点击 **Review**，删除不好的图片后重新训练 |
| 实际使用时经常把某一类误判成另一类 | 某些角度或光线的数据不足，或两类外观相近 | 在误判的角度与光线下补录，再训练、部署 |
| 方框为空时也回答某个物品类别 | 没有 BACKGROUND 类别，或 BACKGROUND 录得太少 | 录制 BACKGROUND 后重新训练、部署 |

其他情况见[故障排除](troubleshooting.md)。

## 下一步 { #next-steps }

- [声纹识别](voice.md)：让同一块 Reef 识别谁在说话。
- [浏览器版图像 Teach](browser.md)：无需安装 Studio，在 Chrome 或 Edge 中完成同样的流程。
