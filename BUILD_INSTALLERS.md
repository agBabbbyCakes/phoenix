# Building Installers for Phoenix Dashboard

This guide explains how to build installers for Mac, Windows, and Linux.

## Prerequisites

1. **Python 3.11+** installed
2. **Briefcase** installed: `pip install briefcase`
3. **Platform-specific requirements:**
   - **macOS**: Xcode Command Line Tools
   - **Windows**: Visual Studio Build Tools (for MSI)
   - **Linux**: Standard build tools (gcc, make, etc.)

## Quick Start

### macOS

```bash
# Make script executable
chmod +x build_macos.sh

# Run build script
./build_macos.sh
```

The app bundle will be at: `dist/macOS/Phoenix Dashboard.app`

To create a DMG installer:
```bash
hdiutil create -volname "Phoenix Dashboard" \
  -srcfolder "dist/macOS/Phoenix Dashboard.app" \
  -ov -format UDZO \
  "dist/macOS/Phoenix Dashboard.dmg"
```

### Windows

```bash
# Make script executable (if on Git Bash/WSL)
chmod +x build_windows.sh

# Run build script
./build_windows.sh
```

The MSI installer will be at: `dist/windows/Phoenix Dashboard.msi`

**Note**: Windows builds should ideally be run on Windows. If cross-compiling, you may need Wine.

### Linux

```bash
# Make script executable
chmod +x build_linux.sh

# Run build script
./build_linux.sh

# Make AppImage executable
chmod +x "dist/linux/Phoenix Dashboard.AppImage"
```

The AppImage will be at: `dist/linux/Phoenix Dashboard.AppImage`

## Manual Build Steps

If you prefer to build manually:

### 1. Create App Structure

```bash
# For your platform
briefcase create macOS    # or windows, linux
```

### 2. Update App Code

```bash
briefcase update macOS    # or windows, linux
```

### 3. Build

```bash
briefcase build macOS     # or windows, linux
```

### 4. Package

```bash
briefcase package macOS   # or windows, linux
```

## Development Mode

To run the app in development mode (without building):

```bash
briefcase dev
```

This will:
- Start the FastAPI server
- Open the app in your default browser
- Allow live code changes

## Troubleshooting

### Port Already in Use

The app will automatically find a free port if 8000 is in use.

### Dependencies Issues

If you get dependency errors:

```bash
# Clean and recreate
rm -rf build/ dist/
briefcase create macOS  # or windows/linux
```

### Template Issues

If you get template errors, update Briefcase:

```bash
pip install --upgrade briefcase
```

### macOS Code Signing

For distribution, you may want to code sign the app:

```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/macOS/Phoenix Dashboard.app"
```

### Windows Certificate

For Windows, you may need a code signing certificate for the MSI.

## Building for All Platforms

To build for all platforms, run each build script on the respective platform:

1. **macOS**: Run `./build_macos.sh` on macOS
2. **Windows**: Run `./build_windows.sh` on Windows
3. **Linux**: Run `./build_linux.sh` on Linux

## Distribution

### macOS
- **.app bundle**: Can be distributed directly or zipped
- **.dmg**: More professional, easier installation

### Windows
- **.msi**: Standard Windows installer format

### Linux
- **.AppImage**: Portable, no installation needed
- Can also create `.deb` or `.rpm` packages if needed

## Notes

- The app uses a web-based UI (FastAPI + browser), so it will open in your default browser
- The server runs locally on port 8000 (or next available port)
- All dependencies are bundled with the app
- The app is self-contained and doesn't require Python to be installed on the target system

