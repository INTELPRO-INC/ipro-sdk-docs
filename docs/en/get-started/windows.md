---
title: "Windows Setup & VS Code"
description: Install the Windows development tools and the VS Code Extension with the Online Installer, then add SDK V2.1.0 by hand and build your first project.
migrate_from:
  - "windows-installation.html"
  - "vscode-extension.html#installation"
not_migrated:
  - "windows-installation.html#overview"
  - "windows-installation.html#package-contents"
  - "windows-installation.html#install-modes"
  - "windows-installation.html#full-install"
  - "windows-installation.html#extension-only"
  - "windows-installation.html#sdk-only"
  - "windows-installation.html#settings"
---

# Windows Setup & VS Code

Use the Online Installer to put the toolchain, build tools, IntelProCube and the VS Code Extension on a Windows PC, then point the Extension at SDK V2.1.0 and build `ipro7ai_reef_demo`, the out-of-box firmware of the IPRO7AI Reef EVK.

!!! warning "The installer does not install V2.1.0 yet"
    As checked on 2026-10-16, the Online Installer's package index still lists SDK 1.2.1 as stable and has no V2.x entry, so choosing latest does not install V2.1.0. Use the installer for the tools and the Extension, then add the SDK yourself as described in [Switch to SDK V2.1.0](#sdk-2-1-0).

## Requirements { #requirements }

- A Windows PC with internet access: the Online Installer downloads its components from a public package index.
- VS Code 1.102 or later.
- `IPRO-SDK-V2.1.0.tar.gz` and `IPRO-SDK-V2.1.0.tar.gz.sha256`, downloaded as described in [Choose Your Environment](environment.md#sdk-2-1-0).
- A toolchain that works with V2.1.0. The V2.1.0 README specifies GCC 14, while the Windows toolchain in the installer's index is the combination declared for SDK 1.2.1. Contact INTELPRO for a suitable build and check its version.

## Install the tools { #online-3-4-0 }

<div class="ipro-steps" markdown>

1. **Download the installer**: get `IPRO-SDK-Online-Setup-3.4.0.exe` from the [Online Installer 3.4.0 release](https://github.com/INTELPRO-INC/IPRO-SDK/releases/tag/online-installer-v3.4.0). No GitHub sign-in is needed.

2. **Choose a mode and a directory**: pick **Full** for a first installation; the other six modes (SDK, toolchain, build tools, IntelProCube, OpenOCD, Extension) each install a single component. Install into a new, empty folder.

3. **Review the options, then install**: writing the VS Code settings and updating PATH are both unchecked by default; tick them if you want them. With version latest, the installer picks the version each component marks as stable / compatible, not the newest GitHub release.

4. **Restart VS Code and any open terminals** so they pick up the new PATH.

</div>

## Switch to SDK V2.1.0 { #sdk-2-1-0 }

<div class="ipro-steps" markdown>

1. **Verify the download**: in PowerShell, compute the hash and compare it with the value in the `.sha256` file (case does not matter).

    ```powershell
    Get-FileHash .\IPRO-SDK-V2.1.0.tar.gz -Algorithm SHA256
    Get-Content .\IPRO-SDK-V2.1.0.tar.gz.sha256
    ```

2. **Unpack into a new directory**: do not overwrite an older SDK; keep it so you can go back.

    ```powershell
    tar -xzf .\IPRO-SDK-V2.1.0.tar.gz
    Get-Content .\IPRO-SDK-V2.1.0\VERSION.txt
    ```

    `VERSION.txt` should show `IPRO-SDK-V2.1.0`, and the root `IPRO-SDK-V2.1.0\` should contain `CMakeLists.txt`, `apps\` and `bsp\`.

</div>

## Set up the VS Code Extension { #installation }

<div class="ipro-steps" markdown>

1. **Check that the Extension is installed**: search for `@installed IPRO` in the Extensions view; the IPRO SDK Extension (ID `ipro.ipro-sdk-extension`) should be listed. If it is not, install the VSIX with **… → Install from VSIX…** and run `Developer: Reload Window`.

2. **Open the SDK**: use **File → Open Folder…** to open the `IPRO-SDK-V2.1.0` root, and trust the workspace once you have checked where it came from.

3. **Set the SDK root**: press ++f1++, run `IPRO Setup: Set SDK Root` and select the same directory.

4. **Check the environment**: run `IPRO Setup: Run Diagnostics` and confirm the paths it reports for the SDK root, compiler, CMake and Python. The compiler must be a V2.1.0-compatible toolchain.

5. **Build your first project**: run `IPRO: Go to Project…`, pick `ipro7ai_reef_demo` under platform, then run `IPRO: Build`.

</div>

For the Extension's commands, flash settings and monitor, see [VS Code Extension](../guides/vscode.md).

## Verify { #verify }

A successful build produces:

```text
apps\platform\ipro7ai_reef_demo\build\build_out\ipro7ai_reef_demo_IPRO7.bin
```

A successful build only shows that the tools work; nothing has been written to the board yet.

## Troubleshooting { #troubleshooting }

| Symptom | Cause | Fix |
|---|---|---|
| The installed SDK is 1.2.1 | The package index has no V2.x entry yet | Add the SDK by hand as in [Switch to SDK V2.1.0](#sdk-2-1-0) |
| The old SDK is still used after switching | The SDK root in the workspace or User settings still points at the old version | Run `IPRO Setup: Set SDK Root`, then check the actual path with `IPRO Setup: Run Diagnostics` |
| No IPRO commands | The Extension is not in the current VS Code profile, or the workspace is not trusted | Check the Extension, profile and Workspace Trust, then run `Developer: Reload Window` |
| Running `make` from a command prompt cannot find the compiler | The app's `.config` sets `CONFIG_CROSS_COMPILE` to a Unix path (`/opt/toolchain/...`); on Windows the build uses the `cmake` on PATH | Add `CROSS_COMPILE=<toolchain dir>\bin\riscv64-unknown-elf-` (with the trailing hyphen) to the `make` command line, and make sure the CMake on PATH is 3.19 or later |
| `build_freertos.sh` or `tools/serial_monitor.py` does not run | Both need bash and POSIX termios | On Windows, build, flash and monitor through the Extension, or use another serial terminal |

## Next steps { #next-steps }

- [First FreeRTOS Application](first-app-freertos.md): flash `ipro7ai_reef_demo` and run the self-test on the Reef.
- [Flashing & Serial Console](flash-and-monitor.md): `ipro_iot_tool.exe` options and per-board settings.
- [VS Code Extension](../guides/vscode.md): Control Center, flash settings and monitor.
