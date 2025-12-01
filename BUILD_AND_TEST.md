# Building and Testing Standalone Applications

This guide will help you build and test the standalone applications for all platforms.

## Quick Start - Windows

### Step 1: Build the Executable and ZIP

```batch
build_windows_standalone.bat
```

This will:
- Build the standalone executable
- Create a ZIP file with the executable and README
- Place files in `downloads/` directory

**Output:**
- `downloads/PhoenixDashboard-Windows-x64.exe` - Standalone executable
- `downloads/windows/PhoenixDashboard-Windows-x64.zip` - ZIP package

### Step 2: Test the Build

1. Navigate to `downloads/` folder
2. Double-click `PhoenixDashboard-Windows-x64.exe`
3. Your browser should automatically open to `http://127.0.0.1:8000`
4. Verify the dashboard loads correctly
5. Press Ctrl+C in the console to stop

### Step 3: Build the Installer (Optional)

**Prerequisites:** Install NSIS from https://nsis.sourceforge.io/

```batch
build_windows_installer.bat
```

This will:
- Build an MSI-style installer using NSIS
- Create Start Menu and Desktop shortcuts
- Add uninstaller to Add/Remove Programs

**Output:**
- `PhoenixDashboard-Setup.exe` - Windows installer
- `downloads/windows/PhoenixDashboard-Setup-x64.exe` - Copy

### Step 4: Test the Installer

1. Run `PhoenixDashboard-Setup.exe`
2. Follow the installation wizard
3. Launch from Start Menu or Desktop shortcut
4. Verify it works correctly
5. Test uninstaller from Add/Remove Programs

## Quick Start - macOS

### Step 1: Build

```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

**Output:**
- `dist/PhoenixDashboard.app` - App bundle
- `downloads/macos/PhoenixDashboard-macOS-<arch>.zip` - ZIP package
- `downloads/macos/PhoenixDashboard-macOS-<arch>.dmg` - DMG installer

### Step 2: Test

1. Open the DMG file
2. Drag `PhoenixDashboard.app` to Applications
3. Launch from Applications
4. Verify browser opens automatically

## Quick Start - Linux

### Step 1: Build

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

**Output:**
- `dist/PhoenixDashboard` - Executable
- `downloads/linux/PhoenixDashboard-Linux-<arch>.zip` - ZIP package
- `downloads/linux/PhoenixDashboard-Linux-<arch>.AppImage` - AppImage (if appimagetool available)

### Step 2: Test

1. Extract the ZIP or use the AppImage
2. Make executable: `chmod +x PhoenixDashboard`
3. Run: `./PhoenixDashboard`
4. Verify browser opens automatically

## Testing Checklist

### Windows Testing

- [ ] Executable runs without errors
- [ ] Browser opens automatically
- [ ] Dashboard loads correctly
- [ ] All features work (charts, metrics, etc.)
- [ ] Can stop cleanly with Ctrl+C
- [ ] Installer installs correctly
- [ ] Shortcuts work
- [ ] Uninstaller works

### macOS Testing

- [ ] App bundle runs
- [ ] Browser opens automatically
- [ ] Dashboard loads correctly
- [ ] DMG opens correctly
- [ ] Can drag to Applications
- [ ] Launches from Applications

### Linux Testing

- [ ] Executable runs
- [ ] Browser opens automatically
- [ ] Dashboard loads correctly
- [ ] AppImage works (if created)
- [ ] Can stop cleanly with Ctrl+C

## Troubleshooting

### Windows

**"Python is not installed"**
- Install Python 3.11+ from python.org
- Make sure it's added to PATH

**"PyInstaller not found"**
- The build script will install it automatically
- Or manually: `pip install pyinstaller`

**"NSIS not found" (for installer)**
- Download and install NSIS from https://nsis.sourceforge.io/
- Make sure `makensis.exe` is in your PATH

**Executable doesn't run**
- Check if antivirus is blocking it
- Try running from command line to see error messages
- Verify all dependencies are included in the build

### macOS

**"Permission denied"**
- Run: `chmod +x build_macos_standalone.sh`

**"App won't open"**
- Right-click app → Open → Click "Open" in security dialog
- Or: System Preferences → Security → Allow app

**DMG creation fails**
- Make sure you're on macOS
- Check disk space

### Linux

**"Permission denied"**
- Run: `chmod +x build_linux_standalone.sh`
- For executable: `chmod +x PhoenixDashboard`

**AppImage not created**
- Install appimagetool: `sudo apt install appimagetool`
- Or download from: https://github.com/AppImage/AppImageKit/releases

## File Sizes

Expected file sizes:
- Windows EXE: ~50-100 MB
- macOS APP: ~50-100 MB
- Linux executable: ~50-100 MB
- ZIP files: ~40-80 MB (compressed)
- Installers: ~50-100 MB

These sizes are normal - they include Python and all dependencies.

## Distribution

After building and testing:

1. **Upload to file hosting** (GitHub Releases, etc.)
2. **Update downloads page** with correct file paths
3. **Test downloads** from the web interface
4. **Share with users**

## Next Steps

- Test on clean VMs/machines without Python
- Create release notes
- Set up automated builds (CI/CD)
- Sign executables for distribution (optional)


