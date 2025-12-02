# Linux Build Status

The Linux standalone build requires a Linux environment to compile properly due to:
- Native WebKitGTK dependencies
- Platform-specific PyInstaller compilation
- Binary compatibility requirements

## Quick Build Options:

### Option 1: GitHub Actions (Recommended)
1. Go to: https://github.com/YOUR_USERNAME/phoenix/actions
2. Click "Build All Platforms" 
3. Click "Run workflow"
4. Download the `linux-zip` artifact when complete

### Option 2: Docker (If Docker Desktop is running)
```powershell
docker build -f Dockerfile.linux-build -t phoenix-linux-builder .
docker create --name builder phoenix-linux-builder
docker cp builder:/app/downloads/linux/. downloads/linux/
docker rm builder
```

### Option 3: WSL (If WSL is installed)
```powershell
wsl bash build_linux_standalone.sh
```

### Option 4: Native Linux Machine
Run on any Linux system:
```bash
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
```

The build infrastructure is ready - just needs to run in a Linux environment!


