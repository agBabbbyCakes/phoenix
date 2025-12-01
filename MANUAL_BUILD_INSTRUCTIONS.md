# Manual Linux Build - Step by Step

## Quick Build (Copy and paste this entire block into PowerShell):

```powershell
# Make sure Docker Desktop is running first!
docker run --rm -v "${PWD}:/workspace" -w /workspace python:3.11-slim bash -c "apt-get update && apt-get install -y webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip build-essential python3-dev pkg-config && pip install --upgrade pip && pip install -r requirements.txt && pip install pydantic-settings pyinstaller && python3 version.py && python3 -m PyInstaller --clean --noconfirm phoenix_linux.spec && mkdir -p downloads/linux dist/PhoenixDashboard-Linux-x86_64 && cp dist/PhoenixDashboard dist/PhoenixDashboard-Linux-x86_64/ && echo 'Phoenix Dashboard - Linux Standalone' > dist/PhoenixDashboard-Linux-x86_64/README.txt && echo '1. Extract archive' >> dist/PhoenixDashboard-Linux-x86_64/README.txt && echo '2. chmod +x PhoenixDashboard' >> dist/PhoenixDashboard-Linux-x86_64/README.txt && echo '3. ./PhoenixDashboard' >> dist/PhoenixDashboard-Linux-x86_64/README.txt && cd dist && zip -r PhoenixDashboard-Linux-x86_64.zip PhoenixDashboard-Linux-x86_64 && cp PhoenixDashboard-Linux-x86_64.zip /workspace/downloads/linux/ && echo 'SUCCESS' && ls -lh /workspace/downloads/linux/PhoenixDashboard-Linux-x86_64.zip"
```

## Or use the batch file:

Double-click: `RUN_BUILD.bat`

## Or use PowerShell:

```powershell
.\BUILD_NOW.ps1
```

## Verify the build:

After running, check:
```powershell
Test-Path "downloads\linux\PhoenixDashboard-Linux-x86_64.zip"
```

If it returns `True`, the build succeeded!

## If Docker isn't working:

1. Make sure Docker Desktop is running (check system tray)
2. Try: `docker ps` - should show running containers or empty list
3. If error, restart Docker Desktop

## Alternative: Use GitHub Actions

1. Go to: https://github.com/YOUR_USERNAME/phoenix/actions
2. Click "Build All Platforms"
3. Click "Run workflow"
4. Download the `linux-zip` artifact when done

