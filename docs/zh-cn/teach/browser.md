---
title: "浏览器版图像 Teach"
description: 用 SDK 的 tools/teach_web 在 Chrome 或 Edge 中完成 IPRO7AI Reef EVK 的图像 Teach：启动本地服务器、录制、在浏览器中训练、经 Web Serial 部署，以及离线使用与 IPRO AI Studio 的区别。
---

# 浏览器版图像 Teach

SDK 的 `tools/teach_web` 是无需安装 IPRO AI Studio 的图像 Teach：在 Chrome 或 Edge 中打开一个本地网页，对着 Reef 的摄像头录制、在浏览器中训练，再经同一条 USB-C 线以 Web Serial 部署到开发板。流程与 Studio 的 **Teach** 页面相同，生成的模型也与 Studio 逐字节相同。Windows、macOS、Linux 都可以使用。

## 前提条件 { #prerequisites }

- IPRO7AI Reef EVK 接上 OV5640 摄像头（SW7 在 CAM），已烧录 Edge AI 固件，并处于 `image` 模式。网页不能切换模式：开发板处于其他模式时，先在控制台输入 `mode image`，或使用 Studio 的 **Switch to Teach**。见[烧录 Edge AI 固件](firmware.md#modes)。
- 一条支持数据传输的 USB-C 线，连接 Reef 的 USB-C 与电脑：用于供电，也用于传输图像与模型。
- Chrome 或 Edge（支持 Web Serial；Safari 与 Firefox 不支持）。
- Python 3.8 及以上，仅用于在本地提供网页。
- SDK V2.2.1：`tools/teach_web/`。

## 启动网页 { #start }

<div class="ipro-steps" markdown>

1. **启动本地服务器**：在 SDK 根目录运行：

    ```bash
    python3 tools/teach_web/serve.py
    ```

    服务器只在本机（127.0.0.1）提供 `tools/teach_web/`，网址为 `http://localhost:8780`，并用默认浏览器打开。默认浏览器不是 Chrome 或 Edge 时，把网址粘贴到其中一个浏览器中。摄像头与串口只对 `localhost` 或 `https` 的网页开放，直接从磁盘打开 `index.html` 无法使用。

2. **允许使用摄像头**：首次打开时，浏览器会询问是否允许使用摄像头，请允许。

3. **选择 Reef 的摄像头**：在 **Camera** 菜单中选择 **IPRO7 UVC Cam**。明亮的正方形就是模型看到的范围。

</div>

`serve.py` 的选项：`--port <端口号>` 改用其他端口，`--no-browser` 不自动打开浏览器，`--fetch-runtime` 见[离线使用](#offline)。

## 采集、训练、部署 { #steps }

<div class="ipro-steps" markdown>

1. **采集**：选中一个类别，把物品放进正方形，按住 **Hold to record**（或空格键）几秒。保留 **BACKGROUND** 类别，在正方形里什么都不放的情况下录制，让开发板能回答“没有东西”。最多 8 类；名称使用 A–Z、0–9，最多 15 个字符，因为开发板用自己的字体显示。点击 **Review** 查看图片，勾选不好的图片后点击 **Delete selected**，再点击 **Done**。

2. **训练**：选择骨干网络（MobileNetV2 0.35 或 MobileNetV1 0.25），点击 **Train**，一两秒内完成。每一类每 4 张图片留出 1 张评分；同一次录制的图片彼此很像，这个分数代表“类别能区分开”，不代表换一个场景也一样准确。

3. **连接开发板**：点击 **Connect…**（或首次点击 **Deploy** 时），浏览器询问要使用哪个串口，选择 **IPRO7 UVC Cam**。

4. **部署**：点击 **Deploy**。网页依次执行 **Build the model**、**Send and write**、**Restart the board**：生成模型、连同类别名称一起发送，开发板检查并写入后重启，摄像头会自动恢复。传输被拒绝或中断时，板上原有的模型不受影响。

5. **在板上运行**：开发板用自己的 NPU 识别正方形里的内容，把类别名称、置信度与每一类的概率画在正方形旁边。

</div>

**Save…** 与 **Open…** 把采集的图片保存为或读回一个 `.teach` 文件，之后可以补录或重新训练。

## 验证结果 { #verify }

1. 部署完成后摄像头画面恢复，正方形旁显示类别名称与概率。
2. 每一类物品放进正方形时，显示对应的类别；正方形为空时显示 **BACKGROUND**。
3. 同一个画面在 Studio 或任何能打开 USB 摄像头的程序中都能看到。

## 离线使用 { #offline }

网页用 LiteRT.js 运行骨干网络。没有本地副本时，它从 jsDelivr CDN 下载。在没有网络的电脑上使用前，先在有网络的电脑上运行一次（约 22 MB，下载后用 npm 的完整性哈希校验）：

```bash
python3 tools/teach_web/serve.py --fetch-runtime
```

运行时库存放在 `tools/teach_web/vendor/`；把这个文件夹一起复制到没有网络的电脑即可。

## 声纹页面 { #voice-page }

`voice.html`（网页上方的 **Voice** 标签页）是浏览器版的声纹识别：Reef 处于 `voice` 模式时，点击 **Connect…** 选择 **IPRO Reef Voice**，即可注册说话人（**Teach a voice**、**Record**）、点击 **Start listening** 查看谁在说话，并使用 **Stranger mode** 与 **Thresholds**。所有运算都在板上进行，网页只发送指令并绘制开发板返回的标签。各项操作的含义与 Studio 的 Audio 页面相同，见[声纹识别](voice.md)。

## 与 IPRO AI Studio 的区别 { #compare }

| | 浏览器版 `tools/teach_web` | IPRO AI Studio |
|---|---|---|
| 获取方式 | SDK 随附 | [GitHub](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) |
| 需要安装 | Python 3.8 及以上与 Chrome 或 Edge | Studio 应用程序 |
| 操作系统 | Windows、macOS、Linux | macOS、Windows |
| 图像识别 | 有：采集、训练、部署 | 有（**Teach** 页面） |
| 声纹识别 | 有（`voice.html`） | 有（**Audio** 页面） |
| 传感器识别 | 无 | 有（**Sensor** 页面） |
| 切换开发板的模式 | 不支持；用控制台 `mode` 或 Studio 切换 | **Switch to …** 按钮 |
| 保存采集的图片 | `.teach` 文件 | 文件夹（每类一个子文件夹的 PNG） |
| 命令行、模型套件 `.ipkg` | 无 | `ipro-ai` 命令行 |
| 网络 | 首次需要下载 LiteRT.js，或事先用 `--fetch-runtime` 获取 | 不需要 |

两者的图像模型逐字节相同：分类层在浏览器中训练后直接写入随附的模板 `.inm`，不需要模型转换器。

## 故障排除 { #troubleshooting }

| 现象 | 原因 | 处理 |
|---|---|---|
| `This browser has no Web Serial` | 浏览器不支持 Web Serial | 改用 Chrome 或 Edge |
| `Open this page from http://localhost` | 直接从磁盘打开了网页 | 用 `serve.py` 启动，从 `http://localhost:8780` 打开 |
| 摄像头列表里没有 **IPRO7 UVC Cam** | 开发板不在 `image` 模式、没有 Edge AI 固件，或 USB-C 线仅支持充电 | 在控制台输入 `mode image`；换一条支持数据传输的线 |
| 部署后显示 `The camera went away` | 开发板正在重启 | 正常现象，摄像头会自动恢复；没有恢复就重新插拔 USB-C |
| macOS 上所有程序都看不到摄像头画面 | 另一个程序仍占用摄像头 | 关闭那个程序，再重新插拔 USB-C |
| `The model runtime did not load` | 没有网络，也没有本地副本 | 在有网络的电脑上运行 `serve.py --fetch-runtime`，或把 `vendor/` 复制过来 |

## 下一步 { #next-steps }

- [图像识别](image.md)：Studio 的 Teach 页面，含命令行训练与模型套件。
- [传感器识别](sensor.md)：只能在 Studio 中操作。
