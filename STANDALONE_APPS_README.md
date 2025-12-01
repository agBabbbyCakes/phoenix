# Standalone Applications - Quick Start Guide

This repository now includes everything needed to build standalone executables for Phoenix Dashboard that work on Windows, macOS, Linux, and Raspberry Pi.

## What Was Created

### 1. Standalone Launcher (`standalone_launcher.py`)
- Automatically finds an available port
- Opens your browser when the server starts
- Works as the entry point for all standalone builds

### 2. PyInstaller Spec Files
- `phoenix_windows.spec` - Windows executable
- `phoenix_macos.spec` - macOS app bundle
- `phoenix_linux.spec` - Linux executable (x86_64)
- `phoenix_raspberrypi.spec` - Raspberry Pi executable (ARM)

### 3. Build Scripts
- `build_windows_standalone.bat` - Windows build script
- `build_macos_standalone.sh` - macOS build script
- `build_linux_standalone.sh` - Linux build script
- `build_raspberrypi_standalone.sh` - Raspberry Pi build script

### 4. Downloads Page
- Accessible at `/downloads` in the web app
- Beautiful UI showing all available builds
- Instructions for each platform
- Links to download executables

### 5. Documentation
- `BUILD_STANDALONE.md` - Detailed build instructions
- `downloads/README.md` - Information about the downloads directory

## Quick Start

### Building for Your Platform

**Windows:**
```batch
build_windows_standalone.bat
```

**macOS:**
```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

**Linux:**
```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

**Raspberry Pi:**
```bash
chmod +x build_raspberrypi_standalone.sh
./build_raspberrypi_standalone.sh
```

### Using the Downloads Page

1. Start your Phoenix Dashboard server
2. Navigate to `http://localhost:8000/downloads`
3. Click the download button for your platform
4. Follow the usage instructions on the page

## Features

✅ **Self-contained** - No Python installation required  
✅ **Auto-browser** - Automatically opens your browser  
✅ **Cross-platform** - Works on Windows, macOS, Linux, and Raspberry Pi  
✅ **Easy distribution** - Single executable file  
✅ **Raspberry Pi ready** - Optimized for ARM architecture  

## Raspberry Pi Setup

The standalone app is perfect for running on a Raspberry Pi:

1. Build the executable on your Raspberry Pi
2. Run it: `./PhoenixDashboard-RaspberryPi-armv7l`
3. Access from any device on your network using the Pi's IP address
4. Optionally set up as a systemd service for auto-start

See `downloads/README.md` for systemd service example.

## File Structure

```
phoenix/
├── standalone_launcher.py          # Launcher script
├── phoenix_*.spec                  # PyInstaller spec files
├── build_*_standalone.*            # Build scripts
├── downloads/                      # Output directory for builds
│   ├── README.md
│   └── [executables will be here]
├── templates/
│   └── downloads.html             # Downloads page
└── BUILD_STANDALONE.md            # Detailed build guide
```

## Next Steps

1. **Build the executables** using the appropriate build script for your platform
2. **Test the standalone app** on a clean machine
3. **Distribute** via the downloads page or file hosting
4. **Set up Raspberry Pi** as a dedicated dashboard server

## Troubleshooting

See `BUILD_STANDALONE.md` for detailed troubleshooting information.

## Notes

- The executables are large (50-100MB) because they include Python and all dependencies
- Build Raspberry Pi versions directly on the Pi for best compatibility
- The standalone launcher uses port 8000 by default, but will find the next available port if needed


