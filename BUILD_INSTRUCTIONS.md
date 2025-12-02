# Building All Platforms - Complete Guide

## Overview

Phoenix Dashboard standalone applications must be built on their respective platforms:
- **Windows**: Build on Windows
- **Linux**: Build on Linux (Ubuntu/Debian recommended)
- **macOS**: Build on macOS

## Quick Build Commands

### Windows
```batch
build_windows_standalone.bat
```

### Linux
```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

### macOS
```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

## What Gets Built

Each platform build creates:
- **ZIP Package**: `downloads/<platform>/PhoenixDashboard-<Platform>-<arch>.zip`
- **Standalone Executable**: Platform-specific executable

### Windows
- `downloads/windows/PhoenixDashboard-Windows-x64.zip`
- `downloads/PhoenixDashboard-Windows-x64.exe`

### Linux
- `downloads/linux/PhoenixDashboard-Linux-x86_64.zip`
- `downloads/PhoenixDashboard-Linux-x86_64`

### macOS
- `downloads/macos/PhoenixDashboard-macOS-<arch>.zip`
- `downloads/macos/PhoenixDashboard-macOS-<arch>.dmg`
- `dist/PhoenixDashboard.app`

## Building All Platforms

### Option 1: Build on Each Platform
1. Build Windows on a Windows machine
2. Build Linux on a Linux machine (or WSL)
3. Build macOS on a Mac

### Option 2: Use CI/CD
Set up GitHub Actions or similar CI/CD to build all platforms automatically.

### Option 3: Use Docker/VMs
- Use Docker for Linux builds
- Use macOS VM for macOS builds (requires macOS license)

## Requirements by Platform

### Windows
- Python 3.11+
- PyInstaller
- pywebview

### Linux
- Python 3.11+
- WebKitGTK: `sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev`
- zip: `sudo apt install zip`

### macOS
- Python 3.11+
- Xcode Command Line Tools
- zip (usually pre-installed)

## After Building

Once all platforms are built, the downloads page will automatically:
- Show download links for available files
- Disable links for missing files
- Display build status

## Verification

Check that all ZIP files exist:
```bash
# Windows
ls downloads/windows/*.zip

# Linux
ls downloads/linux/*.zip

# macOS
ls downloads/macos/*.zip
```

## Troubleshooting

See platform-specific guides:
- `BUILD_LINUX_NOW.md` - Linux build instructions
- `BUILD_MACOS_NOW.md` - macOS build instructions
- `LINUX_COMPATIBILITY.md` - Linux compatibility guide


