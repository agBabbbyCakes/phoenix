# Standalone Applications - Complete Guide

This repository now includes everything needed to build professional standalone applications with installers for Windows, macOS, and Linux.

## 🚀 Quick Start

### Windows (Test Now!)

```batch
build_windows_standalone.bat
```

This creates:
- ✅ Standalone executable (`.exe`)
- ✅ ZIP package with README
- ✅ Ready to test immediately!

For installer (requires NSIS):
```batch
build_windows_installer.bat
```

### macOS

```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

Creates:
- ✅ App bundle (`.app`)
- ✅ ZIP package
- ✅ DMG installer

### Linux

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

Creates:
- ✅ Standalone executable
- ✅ ZIP package
- ✅ AppImage (if appimagetool available)

## 📦 What You Get

### Windows
- **PhoenixDashboard-Windows-x64.exe** - Run directly, no install needed
- **PhoenixDashboard-Windows-x64.zip** - ZIP with executable + README
- **PhoenixDashboard-Setup-x64.exe** - Full installer with shortcuts (optional)

### macOS
- **PhoenixDashboard.app** - Native macOS app bundle
- **PhoenixDashboard-macOS-<arch>.zip** - ZIP package
- **PhoenixDashboard-macOS-<arch>.dmg** - DMG installer (drag to Applications)

### Linux
- **PhoenixDashboard-Linux-<arch>** - Standalone executable
- **PhoenixDashboard-Linux-<arch>.zip** - ZIP package
- **PhoenixDashboard-Linux-<arch>.AppImage** - Portable AppImage (if available)

## 🧪 Testing

### Windows Testing Steps

1. **Build:**
   ```batch
   build_windows_standalone.bat
   ```

2. **Test executable:**
   - Navigate to `downloads/` folder
   - Double-click `PhoenixDashboard-Windows-x64.exe`
   - Browser should open automatically
   - Verify dashboard works
   - Press Ctrl+C to stop

3. **Test ZIP:**
   - Extract `downloads/windows/PhoenixDashboard-Windows-x64.zip`
   - Run `PhoenixDashboard.exe` from extracted folder
   - Verify it works

4. **Test installer (if built):**
   - Run `PhoenixDashboard-Setup.exe`
   - Install to default location
   - Launch from Start Menu
   - Test uninstaller

### All Platforms Testing Checklist

- [ ] Executable/app runs without errors
- [ ] Browser opens automatically
- [ ] Dashboard loads correctly
- [ ] All features work (charts, navigation, etc.)
- [ ] Can stop cleanly
- [ ] Installer works (if applicable)
- [ ] Uninstaller works (if applicable)

## 📁 File Structure

```
phoenix/
├── standalone_launcher.py          # Main launcher (auto-opens browser)
├── phoenix_*.spec                  # PyInstaller spec files
├── build_*_standalone.*            # Build scripts
├── build_*_installer.*            # Installer build scripts
├── installer_windows.nsi           # NSIS installer script
├── downloads/                     # Output directory
│   ├── windows/
│   │   ├── PhoenixDashboard-Windows-x64.zip
│   │   └── PhoenixDashboard-Setup-x64.exe
│   ├── macos/
│   │   ├── PhoenixDashboard-macOS-*.zip
│   │   └── PhoenixDashboard-macOS-*.dmg
│   └── linux/
│       ├── PhoenixDashboard-Linux-*.zip
│       └── PhoenixDashboard-Linux-*.AppImage
└── templates/
    └── downloads.html             # Downloads page
```

## 🔧 Build Requirements

### All Platforms
- Python 3.11+
- PyInstaller (installed automatically)
- All dependencies from `requirements.txt`

### Windows Installer
- NSIS (Nullsoft Scriptable Install System)
- Download: https://nsis.sourceforge.io/

### Linux AppImage
- appimagetool (optional)
- Install: `sudo apt install appimagetool`
- Or download: https://github.com/AppImage/AppImageKit/releases

## 📖 Documentation

- **QUICK_START_WINDOWS.md** - Windows-specific quick start
- **BUILD_AND_TEST.md** - Detailed build and test guide
- **BUILD_STANDALONE.md** - Technical build documentation
- **STANDALONE_APPS_README.md** - Overview of standalone apps

## 🌐 Downloads Page

Access the downloads page in your web app:
- URL: `http://localhost:8000/downloads`
- Or click "📥 Downloads" in the navigation menu

The page shows:
- Download links for all platforms
- Installation instructions
- Usage guide
- Build instructions

## 🎯 Features

✅ **Self-contained** - No Python installation required  
✅ **Auto-browser** - Automatically opens browser  
✅ **Cross-platform** - Windows, macOS, Linux, Raspberry Pi  
✅ **Professional installers** - MSI (Windows), DMG (macOS), AppImage (Linux)  
✅ **Easy distribution** - ZIP files and installers  
✅ **Raspberry Pi ready** - Optimized ARM builds  

## 🐛 Troubleshooting

### Common Issues

**Build fails:**
- Check Python version: `python --version` (need 3.11+)
- Install dependencies: `pip install -r requirements.txt`
- Check PyInstaller: `pip install pyinstaller`

**Executable doesn't run:**
- Antivirus may block (add exception)
- Windows security warning (click "Run anyway")
- Check console for error messages

**Browser doesn't open:**
- Manually navigate to `http://127.0.0.1:8000`
- Check console for actual port number

**Installer issues:**
- Install NSIS for Windows installer
- Run installer as Administrator
- Check file permissions

## 📝 Next Steps

1. **Build and test on Windows** (you can do this now!)
2. **Build and test on Linux** (when you get to it)
3. **Test on clean machines** (VMs without Python)
4. **Create release notes**
5. **Upload to file hosting** (GitHub Releases, etc.)
6. **Share with users**

## 💡 Tips

- **File sizes:** 50-100 MB is normal (includes Python + dependencies)
- **Build time:** 2-5 minutes depending on system
- **Testing:** Always test on clean machines/VMs
- **Distribution:** ZIP files are easiest, installers are most professional
- **Raspberry Pi:** Build directly on the Pi for best compatibility

## 🎉 Ready to Build!

Start with Windows:

```batch
build_windows_standalone.bat
```

Then test it:

```batch
test_windows_build.bat
```

Happy building! 🚀



