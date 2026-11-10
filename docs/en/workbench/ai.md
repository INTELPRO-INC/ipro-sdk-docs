---
title: "AI Assistant"
description: The IPRO AI assistant built into IPRO Workbench - turn on AI features, ask it to fix a build error or analyze a crash, and let AI assistants outside the IDE use the IPRO tools through MCP.
---

# AI Assistant

IPRO Workbench has a built-in IPRO AI assistant. It does more than answer questions: it can use the IDE's tools by itself to build, read the build output, flash, read the serial port, change settings, pins and GATT services, look up the memory map and registers, and decode crash addresses. AI assistants outside the IDE (for example Claude Code) can also use the same set of tools through MCP.

## Turn on AI features { #enable }

AI features are off by default. Before you use them:

<div class="ipro-steps" markdown>

1. **Turn them on.** Open Settings (`Cmd+,` / `Ctrl+,`), find **AI Features** and turn on the AI features.

2. **Choose the model.** In the same place, set the model to use, for example Claude Code, an Anthropic API key or GitHub Copilot. Enter keys and account sign-ins yourself; do not let anyone else fill them in for you.

</div>

If the AI features are still off when you press any of the **Ask AI…** buttons below, the IDE first shows "AI features are off…". Press **Turn On AI** to turn them on.

## Ask AI to fix a build error { #fix-build }

<div class="ipro-steps" markdown>

1. **Ask.** When a build fails, press **Ask AI to Fix** on the error notification.

    **You should see**: an AI chat opens on the right. Its first message starts with `@IPRO` and carries the error. The assistant reads the build output and the source code, fixes the cause, builds again, and finally explains in a few sentences what it changed.

2. **Review the changes.** After reading the explanation, check the changed files in the editor. If you do not agree with a change, undo it (`Cmd+Z` / `Ctrl+Z`) or restore the file with version control.

</div>

When `pins.yaml` or `gatt.yaml` has errors or the CMake configuration fails, **Ask AI to Fix** on the notification also asks the assistant to handle that problem.

## Ask AI to analyze a crash { #analyze-crash }

<div class="ipro-steps" markdown>

1. **Ask about the last crash.** When the board crashes or stops (with the serial monitor open), choose **Ask AI About the Last Crash** from the IPRO menu.

    **You should see**: the chat comes with the last few dozen lines of the monitor attached. The assistant decodes the code addresses, reads the code there, and explains the cause and how to fix it.

2. **Use a crash dump.** If you collected a [crash dump](debug.md#crash-dump), press **Ask AI to Explain** in the **Crash Dump** view. The assistant explains the crash from the full call chain.

</div>

## Let AI assistants outside the IDE use it (MCP) { #mcp }

While IPRO Workbench is open, it provides an MCP server on this computer so that AI assistants such as Claude Code, VS Code and Cursor can use the IPRO tools. When an assistant builds, the output still shows in **IPRO Build** in the IDE.

<div class="ipro-steps" markdown>

1. **Copy the setup.** Choose **Connect an AI Assistant (MCP)…** from the IPRO menu (or **AI assistant (MCP)** on IPRO Home), and select the assistant you use.

    **You should see**: the notification "Copied the … setup. It includes the token, so keep it private." appears. The list has Claude Code, VS Code / GitHub Copilot and Cursor. For Claude Code, the copied text is a single `claude mcp add …` command to run in a terminal; for the other two, it is content to paste into a configuration file (`.vscode/mcp.json`, `~/.cursor/mcp.json`).

2. **Paste it.** Paste the clipboard contents into the matching place. For Claude Code, for example, paste and run that command in a terminal, then start Claude Code.

    **You should see**: in Claude Code's MCP list, the `ipro` server is connected and lists tools such as `ipro_build` and `ipro_flash`.

3. **Give an instruction.** Give the assistant an instruction, for example "Build and flash ipro_unit_test, read the serial port and tell me the test results."

    **You should see**: **IPRO Build** and **IPRO Flash** in the IDE show the build and then the flash, and the assistant finally reports how many tests passed and how many failed.

</div>

!!! warning "Important"
    - The MCP server is provided only on this computer (`127.0.0.1`, default port 41730), and every request must carry the access token.
    - The token is stored in `.ipro-ide/mcp.json` in your home folder, and only your account can read it. The copied setup contains the token; do not paste it anywhere public.
    - When you do not need the server, turn off `ipro.mcp.enabled` in Settings.

For the tools that MCP provides, see [MCP tools](reference.md#mcp-tools).
