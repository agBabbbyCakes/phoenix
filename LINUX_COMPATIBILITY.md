# Linux Compatibility Guide

## Supported Distributions

Phoenix Dashboard standalone application works on:

### ✅ Fully Supported
- **Ubuntu** 20.04, 22.04, 24.04
- **Debian** 11, 12
- **Fedora** 36+
- **Arch Linux** (latest)
- **openSUSE** Leap 15+
- **Linux Mint** 20+
- **Pop!_OS** 20.04+

### ⚠️ May Require Additional Setup
- **Ubuntu** 18.04 (may need WebKitGTK update)
- **CentOS** 8+ (requires EPEL)
- **RHEL** 8+ (requires EPEL)

## System Requirements

### Minimum
- Linux kernel 4.15+
- GLIBC 2.27+
- x86_64 architecture
- 100 MB disk space

### Required Libraries
- **WebKitGTK 4.0+** (for native window)
- **GTK 3.0+** (usually pre-installed)
- **Python 3.11+** (only for building, not runtime)

## Installation Steps

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y webkit2gtk-4.0 libwebkit2gtk-4.0-dev
```

**Fedora:**
```bash
sudo dnf install -y webkit2gtk4.0-devel
```

**Arch:**
```bash
sudo pacman -S webkit2gtk
```

### 2. Build the Application

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

### 3. Run the Application

```bash
chmod +x downloads/PhoenixDashboard-Linux-x86_64
./downloads/PhoenixDashboard-Linux-x86_64
```

## Testing Requirements

Run the test script to check your system:

```bash
chmod +x test_linux_build.sh
./test_linux_build.sh
```

## Troubleshooting

### "WebKitGTK not found" Error

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev

# Verify installation
pkg-config --modversion webkit2gtk-4.0
```

### App Opens Browser Instead of Window

This means WebKitGTK is not available. The app falls back to browser mode.

**Fix:**
```bash
sudo apt install webkit2gtk-4.0
```

### "GLIBC version too old"

**Solution:**
- Build on a newer Linux distribution
- Or use a container with newer GLIBC

### Missing Library Errors

Check what's missing:
```bash
ldd downloads/PhoenixDashboard-Linux-x86_64 | grep "not found"
```

Install missing libraries:
```bash
sudo apt install <missing-library>
```

## Desktop Integration

### Create Desktop Shortcut

1. Create `~/.local/share/applications/phoenix-dashboard.desktop`:
```ini
[Desktop Entry]
Name=Phoenix Dashboard
Comment=Ethereum Bot Monitoring Dashboard
Exec=/path/to/PhoenixDashboard-Linux-x86_64
Icon=phoenix-dashboard
Terminal=false
Type=Application
Categories=Network;Monitoring;
```

2. Make executable:
```bash
chmod +x ~/.local/share/applications/phoenix-dashboard.desktop
```

### Systemd Service (for headless/server use)

Create `/etc/systemd/system/phoenix-dashboard.service`:
```ini
[Unit]
Description=Phoenix Dashboard
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/phoenix
ExecStart=/path/to/PhoenixDashboard-Linux-x86_64
Restart=always
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
```

## Distribution-Specific Notes

### Ubuntu
- WebKitGTK usually pre-installed
- May need `libwebkit2gtk-4.0-dev` for building

### Debian
- Stable: May need backports for WebKitGTK 4.0
- Testing/Unstable: Usually available

### Fedora
- WebKitGTK available in default repos
- May need `webkit2gtk4.0-devel` package

### Arch Linux
- WebKitGTK in community repos
- Usually up-to-date

## Verification

After building, verify the executable:

```bash
# Check architecture
file downloads/PhoenixDashboard-Linux-x86_64

# Check dependencies
ldd downloads/PhoenixDashboard-Linux-x86_64 | head -20

# Test run
./downloads/PhoenixDashboard-Linux-x86_64
```

## Support

For issues:
1. Check `LINUX_BUILD_REQUIREMENTS.md` for dependencies
2. Run `test_linux_build.sh` to verify setup
3. Check WebKitGTK installation: `pkg-config --modversion webkit2gtk-4.0`



