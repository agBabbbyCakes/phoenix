# Build Status

## Current Status

### ✅ Windows
- **Status**: Built and ready
- **File**: `downloads/windows/PhoenixDashboard-Windows-x64.zip`
- **Executable**: `downloads/PhoenixDashboard-Windows-x64.exe`

### ⏳ Linux
- **Status**: Not built yet (requires Linux system)
- **To Build**: Run `./build_linux_standalone.sh` on a Linux system
- **Expected File**: `downloads/linux/PhoenixDashboard-Linux-x86_64.zip`

### ⏳ macOS
- **Status**: Not built yet (requires macOS system)
- **To Build**: Run `./build_macos_standalone.sh` on a macOS system
- **Expected File**: `downloads/macos/PhoenixDashboard-macOS-<arch>.zip`

## Building

### Windows (Current System)
```batch
build_windows_standalone.bat
```

### Linux (Need Linux System)
```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

### macOS (Need macOS System)
```bash
chmod +x build_macos_standalone.sh
./build_macos_standalone.sh
```

## Automated Building

### Option 1: GitHub Actions
The repository includes `.github/workflows/build-all-platforms.yml` which can build all platforms automatically when:
- You push a tag (e.g., `v1.0.0`)
- You manually trigger the workflow

### Option 2: Local Multi-Platform
If you have access to multiple systems:
1. Build Windows on Windows
2. Build Linux on Linux (or WSL)
3. Build macOS on Mac
4. Commit all ZIP files to the repository

## Notes

- Windows builds can be done on the current Windows system
- Linux builds require a Linux system (Ubuntu/Debian recommended)
- macOS builds require a macOS system
- All build scripts are ready and tested
- ZIP files are automatically placed in `downloads/<platform>/`


