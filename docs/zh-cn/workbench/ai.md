---
title: "AI 助手"
description: IPRO Workbench 内置的 IPRO AI 助手：开启 AI 功能，让它修复构建错误或分析崩溃，并让 IDE 之外的 AI 助手通过 MCP 使用 IPRO 工具。
---

# AI 助手

IPRO Workbench 内置 IPRO AI 助手。它不只是回答问题，还能自行使用 IDE 的工具来构建、读取构建输出、烧录、读取串口、修改配置、引脚和 GATT 服务、查阅内存映射和寄存器，以及解码崩溃地址。IDE 之外的 AI 助手（例如 Claude Code）也可以通过 MCP 使用同一组工具。

## 开启 AI 功能 { #enable }

AI 功能默认关闭。使用之前：

<div class="ipro-steps" markdown>

1. **开启 AI 功能。** 打开设置（`Cmd+,` / `Ctrl+,`），找到 **AI Features** 并开启 AI 功能。

2. **选择模型。** 在同一位置设置要使用的模型，例如 Claude Code、Anthropic API 密钥或 GitHub Copilot。密钥和账号登录请自己输入，不要让他人代为填写。

</div>

如果在 AI 功能仍处于关闭状态时点击下文任何一个 **Ask AI…** 按钮，IDE 会先显示“AI features are off…”。点击 **Turn On AI** 即可开启。

## 让 AI 修复构建错误 { #fix-build }

<div class="ipro-steps" markdown>

1. **提出请求。** 构建失败时，点击错误通知上的 **Ask AI to Fix**。

    **应看到**：右侧打开 AI 聊天。第一条消息以 `@IPRO` 开头并附带错误信息。助手会读取构建输出和源代码，修复问题的根源，重新构建，最后用几句话说明它修改了什么。

2. **检查修改。** 阅读说明后，在编辑器中检查被修改的文件。如果不同意某处修改，可以撤销（`Cmd+Z` / `Ctrl+Z`），或用版本控制恢复该文件。

</div>

`pins.yaml` 或 `gatt.yaml` 有错误或 CMake 配置失败时，通知上的 **Ask AI to Fix** 同样会请助手处理该问题。

## 让 AI 分析崩溃 { #analyze-crash }

<div class="ipro-steps" markdown>

1. **询问最近一次崩溃。** 开发板崩溃或停止运行时（串口监视器保持打开），在 IPRO 菜单中选择 **Ask AI About the Last Crash**。

    **应看到**：聊天中附带了监视器最近几十行的内容。助手会解码代码地址、阅读对应位置的代码，并解释原因和修复方法。

2. **使用崩溃转储。** 如果已经收集了[崩溃转储](debug.md#crash-dump)，请在 **Crash Dump** 视图中点击 **Ask AI to Explain**。助手会根据完整的调用链解释崩溃。

</div>

## 让 IDE 之外的 AI 助手使用它（MCP） { #mcp }

IPRO Workbench 打开期间，会在本机提供一个 MCP 服务器，让 Claude Code、VS Code 和 Cursor 等 AI 助手可以使用 IPRO 工具。助手执行构建时，输出仍会显示在 IDE 的 **IPRO Build** 中。

<div class="ipro-steps" markdown>

1. **复制配置。** 在 IPRO 菜单中选择 **Connect an AI Assistant (MCP)…**（或点击 IPRO Home 上的 **AI assistant (MCP)**），然后选择你使用的助手。

    **应看到**：出现通知“Copied the … setup. It includes the token, so keep it private.”列表中有 Claude Code、VS Code / GitHub Copilot 和 Cursor。对于 Claude Code，复制的内容是一条要在终端中运行的 `claude mcp add …` 命令；对于另外两个，复制的内容要粘贴到配置文件（`.vscode/mcp.json`、`~/.cursor/mcp.json`）中。

2. **粘贴。** 将剪贴板内容粘贴到对应的位置。以 Claude Code 为例，在终端中粘贴并运行该命令，然后启动 Claude Code。

    **应看到**：在 Claude Code 的 MCP 列表中，`ipro` 服务器已连接，并列出 `ipro_build`、`ipro_flash` 等工具。

3. **下达指令。** 向助手下达指令，例如“构建并烧录 ipro_unit_test，读取串口并告诉我测试结果。”

    **应看到**：IDE 中的 **IPRO Build** 和 **IPRO Flash** 先后显示构建和烧录过程，助手最后报告通过和失败的测试数量。

</div>

!!! warning "重要"
    - MCP 服务器只在本机提供（`127.0.0.1`，默认端口 41730），每个请求都必须携带访问令牌。
    - 令牌保存在主目录下的 `.ipro-ide/mcp.json` 中，只有你的账户可以读取。复制的配置中包含令牌；请勿将其粘贴到任何公开的地方。
    - 不需要该服务器时，请在设置中关闭 `ipro.mcp.enabled`。

MCP 提供的工具请参阅 [MCP 工具](reference.md#mcp-tools)。
