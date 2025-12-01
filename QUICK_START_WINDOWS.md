# Quick Start - Build and Test on Windows

## Step 1: Build the Standalone Application

Run this command in PowerShell or Command Prompt:

```batch
build_windows_standalone.bat
```

This will:
1. ✅ Check Python is installed
2. ✅ Install PyInstaller if needed
3. ✅ Build the standalone executable
4. ✅ Create a ZIP file package
5. ✅ Copy files to `downloads/` directory

**Expected output:**
- `downloads/PhoenixDashboard-Windows-x64.exe` - Standalone executable
- `downloads/windows/PhoenixDashboard-Windows-x64.zip` - ZIP package with README

## Step 2: Test the Build

### Option A: Test the Executable Directly

1. Navigate to the `downloads` folder
2. Double-click `PhoenixDashboard-Windows-x64.exe`
3. Your default browser should automatically open to `http://127.0.0.1:8000`
4. Verify the dashboard loads and works correctly
5. Press `Ctrl+C` in the console window to stop

### Option B: Test from ZIP Package

1. Extract `downloads/windows/PhoenixDashboard-Windows-x64.zip`
2. Open the extracted folder
3. Double-click `PhoenixDashboard.exe`
4. Test as above

## Step 3: Build the Installer (Optional)

**Prerequisites:** Install NSIS (Nullsoft Scriptable Install System)
- Download from: https://nsis.sourceforge.io/Download
- Install and make sure `makensis.exe` is in your PATH

Then run:

```batch
build_windows_installer.bat
```

This creates:
- `PhoenixDashboard-Setup.exe` - Full Windows installer
- `downloads/windows/PhoenixDashboard-Setup-x64.exe` - Copy

### Test the Installer

1. Run `PhoenixDashboard-Setup.exe`
2. Follow the installation wizard
3. Choose installation directory (default: `C:\Program Files\Phoenix Dashboard`)
4. Launch from Start Menu or Desktop shortcut
5. Verify it works
6. Test uninstaller from Add/Remove Programs

## Troubleshooting

### Build Fails

**"Python is not installed"**
- Install Python 3.11+ from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

**"PyInstaller not found"**
- The script should install it automatically
- Or manually: `pip install pyinstaller`

**Build errors about missing modules**
- Check that all dependencies are installed: `pip install -r requirements.txt`
- The spec file includes all necessary hidden imports

### Executable Doesn't Run

**Antivirus blocks it**
- This is common with PyInstaller executables
- Add an exception for the downloads folder
- Or sign the executable (requires code signing certificate)

**"Windows protected your PC"**
- Click "More info" → "Run anyway"
- This happens because the executable isn't signed

**Browser doesn't open**
- Manually navigate to `http://127.0.0.1:8000`
- Check the console for the actual port number

### Installer Issues

**"NSIS not found"**
- Install NSIS from https://nsis.sourceforge.io/
- Restart your terminal after installation
- Verify: `makensis /VERSION` should work

**Installer doesn't create shortcuts**
- Run installer as Administrator
- Check if shortcuts are created in Start Menu

## File Locations

After building:

```
phoenix/
├── downloads/
│   ├── PhoenixDashboard-Windows-x64.exe          (standalone)
│   └── windows/
│       ├── PhoenixDashboard-Windows-x64.zip     (ZIP package)
│       └── PhoenixDashboard-Setup-x64.exe       (installer, if built)
├── dist/
│   ├── PhoenixDashboard.exe                       (build output)
│   └── PhoenixDashboard-Windows/                 (ZIP contents)
└── build/                                         (temporary build files)
```

## Next Steps

1. ✅ Test on a clean Windows machine (or VM) without Python
2. ✅ Verify all dashboard features work
3. ✅ Test network access from other devices
4. ✅ Create release notes
5. ✅ Upload to file hosting or GitHub Releases

## Testing Checklist

- [ ] Executable runs without errors
- [ ] Browser opens automatically
- [ ] Dashboard loads correctly
- [ ] All charts and metrics display
- [ ] Can navigate between pages
- [ ] Can stop cleanly with Ctrl+C
- [ ] Installer installs correctly (if built)
- [ ] Shortcuts work (if installer built)
- [ ] Uninstaller works (if installer built)

## Distribution

Once tested, you can:

1. **Share the ZIP file** - Easiest for users
2. **Share the installer** - Best user experience
3. **Host on downloads page** - Update `/downloads` page paths
4. **Upload to GitHub Releases** - Professional distribution

