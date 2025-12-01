# Building Linux Standalone - Instructions

## ⚠️ Important

The Linux standalone application **must be built on a Linux system**. It cannot be built on Windows or macOS.

## Quick Start

1. **On a Linux system** (Ubuntu/Debian recommended), navigate to the project directory:

```bash
cd /path/to/phoenix
```

2. **Install dependencies** (if not already installed):

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip webkit2gtk-4.0 libwebkit2gtk-4.0-dev

# Fedora
sudo dnf install -y python3 python3-pip webkit2gtk4.0-devel

# Arch
sudo pacman -S python python-pip webkit2gtk
```

3. **Run the build script**:

```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

4. **Verify the build**:

```bash
ls -lh downloads/linux/
```

You should see:
- `PhoenixDashboard-Linux-x86_64.zip` (ZIP package)
- The executable will be in `downloads/PhoenixDashboard-Linux-x86_64`

## What Gets Built

- **ZIP Package**: `downloads/linux/PhoenixDashboard-Linux-x86_64.zip`
  - Contains executable, README, and desktop entry
  - Ready for distribution

- **Standalone Executable**: `downloads/PhoenixDashboard-Linux-x86_64`
  - Direct executable (no extraction needed)
  - Make executable: `chmod +x downloads/PhoenixDashboard-Linux-x86_64`

## Testing

After building, test the executable:

```bash
chmod +x downloads/PhoenixDashboard-Linux-x86_64
./downloads/PhoenixDashboard-Linux-x86_64
```

A native desktop window should open with the dashboard.

## Troubleshooting

### "WebKitGTK not found"
```bash
sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev
```

### "Permission denied"
```bash
chmod +x build_linux_standalone.sh
chmod +x downloads/PhoenixDashboard-Linux-x86_64
```

### Build fails
- Check Python version: `python3 --version` (needs 3.11+)
- Check WebKitGTK: `pkg-config --modversion webkit2gtk-4.0`
- Check PyInstaller: `python3 -m pip install pyinstaller`

## After Building

Once built, the ZIP file will be available at:
- `downloads/linux/PhoenixDashboard-Linux-x86_64.zip`

This file can be:
- Uploaded to GitHub releases
- Served from the downloads page
- Distributed to users

The downloads page at `/downloads` will automatically detect and link to this file.

