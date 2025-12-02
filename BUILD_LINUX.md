# Building Linux Standalone Application

Since you're on Windows, here are several options to build the Linux standalone application:

## Option 1: Using Docker (Recommended - Works on Windows)

If you have Docker Desktop installed:

```bash
# Make the script executable (in Git Bash or WSL)
chmod +x build_linux_docker.sh

# Run the build
./build_linux_docker.sh
```

Or manually:
```bash
docker build -f Dockerfile.linux-build -t phoenix-linux-builder .
docker create --name phoenix-builder phoenix-linux-builder
docker cp phoenix-builder:/app/downloads/linux/. downloads/linux/
docker rm phoenix-builder
```

## Option 2: Using WSL (Windows Subsystem for Linux)

If you have WSL installed:

```bash
# In PowerShell or Command Prompt
wsl bash build_linux_standalone.sh
```

Or use the helper script:
```bash
bash build_linux_wsl.sh
```

## Option 3: GitHub Actions (Automatic)

The build will run automatically when you push to the repository. Check the Actions tab in GitHub.

## Option 4: Build on a Linux Machine

If you have access to a Linux machine (physical or VM):

```bash
# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip

# Install Python packages
pip3 install -r requirements.txt
pip3 install pyinstaller

# Run the build script
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

## What Gets Built

The build process creates:
- `downloads/linux/PhoenixDashboard-Linux-x86_64.zip` - Complete package
- `dist/PhoenixDashboard` - Standalone executable
- `dist/PhoenixDashboard-Linux-x86_64/` - Release directory with README

## Testing the Build

After building, you can test it on a Linux system:

```bash
# Extract the zip
unzip downloads/linux/PhoenixDashboard-Linux-x86_64.zip -d test/

# Make executable
chmod +x test/PhoenixDashboard-Linux-x86_64/PhoenixDashboard

# Run it
./test/PhoenixDashboard-Linux-x86_64/PhoenixDashboard
```

## Requirements

The Linux build requires:
- Python 3.11+
- PyInstaller
- WebKitGTK 4.0+ (for pywebview)
- zip utility

All of these are automatically installed in the Docker build.


