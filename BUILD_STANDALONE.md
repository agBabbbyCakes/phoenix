# Building Standalone Applications

This guide explains how to build standalone executables for Phoenix Dashboard on different platforms.

## Prerequisites

- Python 3.11 or higher
- All dependencies from `requirements.txt` installed
- PyInstaller (will be installed automatically by build scripts)

## Quick Start

### Windows

```batch
build_windows_standalone.bat
```

This will:
1. Install PyInstaller if needed
2. Build the executable
3. Copy it to `downloads/PhoenixDashboard-Windows-x64.exe`

### macOS

```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

This will:
1. Install PyInstaller if needed
2. Build the macOS app bundle
3. Create a zip file in `downloads/PhoenixDashboard-macOS-<arch>.zip`

### Linux (x86_64)

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

This will:
1. Install PyInstaller if needed
2. Build the Linux executable
3. Copy it to `downloads/PhoenixDashboard-Linux-<arch>`

### Raspberry Pi (ARM)

**Important**: Build this directly on your Raspberry Pi for best compatibility.

```bash
chmod +x build_raspberrypi_standalone.sh
./build_raspberrypi_standalone.sh
```

This will:
1. Install PyInstaller if needed
2. Build the Raspberry Pi executable
3. Copy it to `downloads/PhoenixDashboard-RaspberryPi-<arch>`

## Manual Build Process

If you prefer to build manually:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build using the appropriate spec file:
   ```bash
   # Windows
   pyinstaller --clean phoenix_windows.spec

   # macOS
   pyinstaller --clean phoenix_macos.spec

   # Linux
   pyinstaller --clean phoenix_linux.spec

   # Raspberry Pi
   pyinstaller --clean phoenix_raspberrypi.spec
   ```

3. Find the executable in the `dist/` directory

## What Gets Included

The standalone executables include:
- All Python dependencies (FastAPI, uvicorn, etc.)
- All templates and static files
- The standalone launcher that opens your browser automatically
- Everything needed to run without Python installed

## Troubleshooting

### Build Fails with Import Errors

If PyInstaller misses some imports, add them to the `hiddenimports` list in the spec file.

### Executable is Large

This is normal - PyInstaller bundles Python and all dependencies. The executable is typically 50-100MB.

### Browser Doesn't Open Automatically

The launcher tries to open your default browser, but if it fails, you can manually navigate to `http://127.0.0.1:8000` (or the port shown in the console).

### Raspberry Pi Build Issues

- Make sure you're building on the Raspberry Pi itself (not cross-compiling)
- Some ARM architectures may need adjustments to the spec file
- UPX compression is disabled for ARM builds (may cause issues)

## Distribution

After building, the executables will be in the `downloads/` directory. You can:

1. Host them on a web server
2. Share them via the `/downloads` page in the web app
3. Distribute them via GitHub Releases or other file hosting

## Testing

Before distributing, test the standalone executable:

1. Run it on a clean machine (or VM) without Python installed
2. Verify the browser opens automatically
3. Test all dashboard features
4. Check that it stops cleanly with Ctrl+C

## Advanced: Custom Icons

To add custom icons:

1. Create icon files:
   - Windows: `resources/phoenix.ico`
   - macOS: `resources/phoenix.icns`
   - Linux: `resources/phoenix.png`

2. Update the spec file to reference the icon:
   ```python
   icon='resources/phoenix.ico'  # or .icns for macOS
   ```

## Cross-Platform Building

While it's possible to build for other platforms using Docker or VMs, it's recommended to build on the target platform for best compatibility.

For example, to build for Raspberry Pi:
1. SSH into your Raspberry Pi
2. Clone the repository
3. Run the Raspberry Pi build script

