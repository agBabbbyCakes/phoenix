# Linux Downloads

## Building the Linux Standalone

The Linux standalone application must be built on a Linux system.

### Quick Build

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

### Requirements

- Linux system (Ubuntu/Debian recommended)
- Python 3.11+
- WebKitGTK: `sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev`

### Output

After building, you'll find:
- `downloads/linux/PhoenixDashboard-Linux-x86_64.zip` - ZIP package
- `downloads/PhoenixDashboard-Linux-x86_64` - Standalone executable

### Installation

1. Download `PhoenixDashboard-Linux-x86_64.zip`
2. Extract: `unzip PhoenixDashboard-Linux-x86_64.zip`
3. Make executable: `chmod +x PhoenixDashboard-Linux-x86_64/PhoenixDashboard`
4. Run: `./PhoenixDashboard-Linux-x86_64/PhoenixDashboard`

The app will open in a native desktop window (no browser needed!).

