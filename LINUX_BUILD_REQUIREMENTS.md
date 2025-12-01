# Linux Build Requirements

## System Dependencies

For the standalone application to work on Ubuntu and most Linux distributions, you need:

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    webkit2gtk-4.0 \
    libwebkit2gtk-4.0-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev
```

### Fedora/RHEL/CentOS
```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    webkit2gtk4.0-devel \
    gcc \
    gcc-c++ \
    make \
    openssl-devel \
    libffi-devel \
    python3-devel
```

### Arch Linux
```bash
sudo pacman -S \
    python \
    python-pip \
    webkit2gtk \
    base-devel \
    openssl \
    libffi
```

### openSUSE
```bash
sudo zypper install -y \
    python3 \
    python3-pip \
    libwebkit2gtk-4_0-37 \
    gcc \
    make \
    libopenssl-devel \
    libffi-devel \
    python3-devel
```

## Python Dependencies

The build script automatically installs:
- PyInstaller
- pywebview

Additional runtime dependencies (included in executable):
- fastapi
- uvicorn
- jinja2
- sse-starlette
- web3
- python-dotenv

## WebKitGTK Requirements

**Critical:** The standalone app requires WebKitGTK for the native webview.

- **Ubuntu 18.04+**: `webkit2gtk-4.0` (usually pre-installed)
- **Ubuntu 16.04**: `webkit2gtk-4.0` or `libwebkit2gtk-3.0-dev`
- **Debian 10+**: `webkit2gtk-4.0`
- **Fedora 30+**: `webkit2gtk4.0-devel`

If WebKitGTK is not available, the app will fall back to opening a browser.

## Building

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

## Testing

After building, test the executable:

```bash
chmod +x downloads/PhoenixDashboard-Linux-x86_64
./downloads/PhoenixDashboard-Linux-x86_64
```

## Troubleshooting

### "WebKitGTK not found"
```bash
# Ubuntu/Debian
sudo apt install webkit2gtk-4.0

# Fedora
sudo dnf install webkit2gtk4.0-devel
```

### "Permission denied"
```bash
chmod +x PhoenixDashboard-Linux-x86_64
```

### "GLIBC version too old"
- Build on a system with a newer GLIBC version
- Or use a container/Docker for building

### App doesn't open window
- Check if WebKitGTK is installed: `ldd PhoenixDashboard-Linux-x86_64 | grep webkit`
- Install missing libraries: `sudo apt install webkit2gtk-4.0`

## Distribution Compatibility

Tested and working on:
- ✅ Ubuntu 20.04, 22.04, 24.04
- ✅ Debian 11, 12
- ✅ Fedora 36+
- ✅ Arch Linux
- ✅ openSUSE Leap 15+

## Notes

- The executable is built for x86_64 architecture
- For ARM (Raspberry Pi), use `build_raspberrypi_standalone.sh`
- WebKitGTK is the only system dependency required at runtime
- All Python dependencies are bundled in the executable

