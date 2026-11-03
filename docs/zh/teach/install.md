---
title: "安裝 IPRO AI Studio"
description: 在 macOS 與 Windows 安裝 IPRO AI Studio 0.4.2、第一次開啟、允許相機、確認 Studio 找到 Reef，以及使用同一個程式裡的 ipro-ai 命令列。
---

# 安裝 IPRO AI Studio

完成本頁後，電腦上會有可以操作三個 Teach 工具的 IPRO AI Studio，以及同一個程式提供的 `ipro-ai` 命令列；接上已燒錄 Edge AI 韌體的 IPRO7AI Reef EVK 時，Studio 會自己找到板子。本頁對應 IPRO AI Studio 0.4.2，介面為英文，按鈕與頁面名稱照畫面原文以粗體標示。

## 前置需求 { #prerequisites }

- 電腦：Apple 晶片的 Mac（macOS 11 以上，不支援 Intel Mac），或 Windows 64 位元（x64）。
- 安裝檔，從 [GitHub 上的 IPRO AI Studio 發行版](https://github.com/INTELPRO-INC/ipro-ai-studio/releases/latest) 下載：
    - macOS：`IPRO-AI-Studio-0.4.2.dmg`
    - Windows：`IPRO-AI-Studio-0.4.2-windows-x64.zip`
- 要確認連線時：一片已燒錄 Edge AI 韌體的 IPRO7AI Reef EVK 與一條可傳資料的 USB-C 線。板子還沒燒錄時，先完成安裝，再依[燒錄 Edge AI 韌體](firmware.md)燒錄。

Studio 已內含模型轉換與燒錄所需的工具，使用 Teach、Sensor、Audio 三頁不需要另外安裝 Python 或其他程式。

## 安裝 { #install }

<div class="ipro-steps" markdown>

1. **安裝程式**

    === "macOS"

        開啟 `IPRO-AI-Studio-0.4.2.dmg`，把 **IPRO AI Studio** 拖進「應用程式」資料夾。

    === "Windows"

        把 `IPRO-AI-Studio-0.4.2-windows-x64.zip` 解壓縮到要放程式的位置，例如 `C:\IPRO\`。解壓縮後得到 `ipro-ai-studio` 資料夾，裡面的 `ipro-ai-studio.exe` 是視窗程式，`ipro-ai.exe` 是命令列。執行所需的 Visual C++ 執行階段已放在同一個資料夾，不需另外安裝。

2. **第一次開啟**

    === "macOS"

        在 Finder 的「應用程式」資料夾對 **IPRO AI Studio** 按右鍵，選「打開」，再在對話框按「打開」。也可以在終端機解除下載檔案的隔離屬性後直接開啟：

        ```bash
        xattr -dr com.apple.quarantine "/Applications/IPRO AI Studio.app"
        ```

    === "Windows"

        在 `ipro-ai-studio` 資料夾連按兩下 `ipro-ai-studio.exe`。

    畫面左側的導覽列依序是 **Convert**、**Inspect**、**Verify**、**Board**、**Teach**、**Sensor**、**Audio**。前四頁是模型轉換、檢視與比對工具；Teach 工具用的是後三頁。

3. **認識三個 Teach 頁面**：可以點導覽列，也可以用 **Go** 選單或快速鍵切換。

    | 頁面 | 工具 | 快速鍵（macOS／Windows） | 對應的韌體模式 |
    |---|---|---|---|
    | **Teach** | 影像辨識 | Command＋5／Ctrl＋5 | `image` |
    | **Sensor** | 感測器辨識 | Command＋6／Ctrl＋6 | `sensor` |
    | **Audio** | 聲紋辨識 | Command＋7／Ctrl＋7 | `voice` |

4. **允許使用相機**：第一次開啟 **Teach** 頁時，macOS 會詢問是否允許 IPRO AI Studio 使用相機，請選「允許」。Teach 頁從 Reef 的 USB 攝影機畫面裁出訓練圖片，不允許時相機畫面會一直是空的。

</div>

## 作業系統權限 { #permissions }

| 項目 | macOS | Windows |
|---|---|---|
| 相機（Teach 頁） | 第一次開啟 Teach 頁時允許。拒絕過的話，Teach 頁顯示 `IPRO AI Studio is not allowed to use the camera.`；到「系統設定 → 隱私權與安全性 → 相機」打開 IPRO AI Studio，再重新開啟 Studio | 到「設定 → 隱私權與安全性 → 相機」，確認允許桌面應用程式存取相機 |
| 序列埠（三個頁面） | 不需要另外授權 | 不需要另外授權 |

板子的 USB 序列埠同一時間只能給一個程式使用。用 Studio 時，請關閉其他開著這個序列埠的程式，例如終端機程式或另一個 Studio 視窗。這和接在 IPRO Debug Probe 上的主控台序列埠是不同的埠，兩者可以同時開啟。

## Studio 如何找到板子 { #board-discovery }

Teach、Sensor、Audio 三頁會自己尋找板子，不需要選擇序列埠。Edge AI 韌體依目前的模式，以 INTELPRO 的 USB VID 0x3896 列舉成不同的 USB 裝置，每一頁只找自己模式的那一個：

| 韌體模式 | USB 裝置名稱 | VID:PID | 找它的頁面 |
|---|---|---|---|
| `image` | IPRO7 UVC Cam（USB 攝影機＋序列埠） | 3896:0705 | **Teach** |
| `voice` | IPRO Reef Voice（序列埠） | 3896:0720 | **Audio** |
| `sensor` | IPRO Reef Sensor（序列埠） | 3896:0721 | **Sensor** |

- 找到板子時，頁面上方的狀態列 **Board** 顯示 `on USB`（Teach 頁）或 `ready`（Sensor、Audio 頁）。
- 板子在別的模式時，頁面上方出現橫幅，例如 `The Reef is in voiceprint mode.`，以及 **Switch to Teach**、**Switch to Sensor** 或 **Switch to Audio** 按鈕。按下後板子重新開機進入這一頁的模式（約 2 秒），三個模型都留在板上，頁面數秒內會再找到板子。
- 板上的韌體只有單一工具時，按下切換會顯示 `This Reef's firmware runs one Teach only.`；請改燒 Edge AI 韌體 `ipro_reef_teach`。
- 同時接著多片 Reef 時，頁面會找到其中一片。不確定時一次只接一片；命令列可以用 `--port` 指定。

## ipro-ai 命令列 { #cli }

`ipro-ai` 命令列就在 Studio 的執行檔裡，與 Studio 使用同一套部署與驗證邏輯，適合放進腳本。

=== "macOS"

    ```bash
    alias ipro-ai='"/Applications/IPRO AI Studio.app/Contents/MacOS/ipro-ai-studio" --cli'
    ipro-ai device list
    ```

    把 `alias` 那一行加進 shell 的設定檔（例如 `~/.zshrc`），之後的終端機都能直接使用 `ipro-ai`。

=== "Windows"

    ```powershell
    cd C:\IPRO\ipro-ai-studio
    .\ipro-ai.exe device list
    ```

常用的裝置命令：

| 命令 | 做什麼 |
|---|---|
| `ipro-ai device list` | 列出 USB 上的 Teach 工具：工具、序列埠、VID:PID、序號 |
| `ipro-ai device info --json` | 韌體名稱與版本、平台版本、可切換的模式、目前工具的分格容量與板上模型 |
| `ipro-ai model list --all` | 逐一切換三個模式、列出各自的模型，最後切回原模式 |
| `ipro-ai deploy <套件.ipkg> --switch` | 先切到套件所屬的模式再部署，並讀回板上模型的 CRC 確認 |

每個裝置命令都可以加 `--port` 指定 Reef 的 USB 序列埠（省略時自動找 USB 上唯一的一片），加 `--json` 得到機器可讀的輸出。完整命令與模型套件 `.ipkg` 的格式見《IPRO7AI Reef 開發套件使用手冊》，向 INTELPRO 索取，見[文件下載](../documents/index.md)。

## 確認結果 { #verify }

1. Studio 開啟後，導覽列有 **Teach**、**Sensor**、**Audio** 三頁。
2. 接上已燒錄 Edge AI 韌體的 Reef，執行 `ipro-ai device list`，輸出列出一片板子，例如（`voice` 模式，macOS）：

    ```text
      voice   /dev/cu.usbmodemXXXX  USB 3896:0720  <序號>
    ```

3. 執行 `ipro-ai device info --json`，輸出的 `version` 欄位顯示 Edge AI 韌體與平台版本：

    ```text
    "version": {"platform": "2.0", "proto": 2, "abi": 1, "store": 1,
                "tool": "voice", "fw": "ipro_reef_teach", "ver": "2.0.0", "chip": "IPRO7AI"},
    ```

4. 開啟與板子模式對應的頁面，狀態列的 **Board** 顯示 `on USB` 或 `ready`。

## 疑難排解 { #troubleshooting }

| 症狀 | 原因 | 處理 |
|---|---|---|
| macOS 顯示無法打開「IPRO AI Studio」 | 下載的程式帶有隔離屬性 | 在 Finder 按右鍵選「打開」，或執行上面的 `xattr` 指令 |
| Teach 頁顯示 `IPRO AI Studio is not allowed to use the camera.` | 拒絕過相機權限 | 在系統的相機隱私權設定允許 IPRO AI Studio，再重新開啟 Studio |
| `ipro-ai device list` 回報找不到 IPRO 裝置（結束碼 3） | 板子沒有開機、USB-C 線只能充電，或板上不是 Edge AI 韌體 | 換一條可傳資料的線；看主控台的開機訊息；依[燒錄 Edge AI 韌體](firmware.md)燒錄 |
| 頁面一直顯示 `Looking for the board…` | 板子在別的模式，或另一個程式占用板子的序列埠 | 等頁面出現 **Switch to …**；關閉其他開著該序列埠的程式 |

其他狀況見[疑難排解](troubleshooting.md)。

## 下一步 { #next-steps }

- [燒錄 Edge AI 韌體](firmware.md)：板子還沒有 Edge AI 韌體時。
- [影像辨識](image.md)、[聲紋辨識](voice.md)、[感測器辨識](sensor.md)：逐步操作三個工具。
