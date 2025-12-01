# Building macOS Standalone - Instructions

## ⚠️ Important

The macOS standalone application **must be built on a macOS system**. It cannot be built on Windows or Linux.

## Quick Start

1. **On a macOS system**, navigate to the project directory:

```bash
cd /path/to/phoenix
```

2. **Install dependencies** (if not already installed):

```bash
# Install Python (if needed)
brew install python3

# Install zip (if needed)
brew install zip
```

3. **Run the build script**:

```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

4. **Verify the build**:

```bash
ls -lh downloads/macos/
```

You should see:
- `PhoenixDashboard-macOS-<arch>.zip` (ZIP package)
- `PhoenixDashboard-macOS-<arch>.dmg` (DMG installer)

## What Gets Built

- **ZIP Package**: `downloads/macos/PhoenixDashboard-macOS-<arch>.zip`
  - Contains app bundle, README
  - Ready for distribution

- **DMG Installer**: `downloads/macos/PhoenixDashboard-macOS-<arch>.dmg`
  - Professional macOS installer
  - Drag-and-drop installation

- **App Bundle**: `dist/PhoenixDashboard.app`
  - Native macOS application bundle

## Testing

After building, test the app:

```bash
open dist/PhoenixDashboard.app
```

Or test the DMG:

```bash
open dist/PhoenixDashboard-macOS-*.dmg
```

A native desktop window should open with the dashboard.

## Troubleshooting

### "zip command not found"
```bash
brew install zip
```

### "hdiutil not found"
This is a macOS system tool and should always be available. If missing, you may need to reinstall macOS.

### Build fails
- Check Python version: `python3 --version` (needs 3.11+)
- Check PyInstaller: `python3 -m pip install pyinstaller`
- Check pywebview: `python3 -m pip install pywebview`

## After Building

Once built, the ZIP file will be available at:
- `downloads/macos/PhoenixDashboard-macOS-<arch>.zip`

This file can be:
- Uploaded to GitHub releases
- Served from the downloads page
- Distributed to users

The downloads page at `/downloads` will automatically detect and link to this file.

## Architecture Detection

The build script automatically detects your Mac's architecture:
- **Intel Macs**: `x86_64`
- **Apple Silicon (M1/M2/M3)**: `arm64`

The ZIP and DMG will be named accordingly.

