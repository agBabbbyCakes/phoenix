# Manual Linux Build Script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Manual Linux Build" -ForegroundColor Cyan  
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is NOT running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting build process..." -ForegroundColor Yellow
Write-Host "This will take 5-10 minutes. Please wait..." -ForegroundColor Gray
Write-Host ""

# Ensure directory exists
New-Item -ItemType Directory -Force -Path "downloads\linux" | Out-Null

# Build command
$buildScript = @'
#!/bin/bash
set -e
set -x

echo "=== Installing system dependencies ==="
apt-get update
apt-get install -y webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip build-essential python3-dev pkg-config

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt
pip install pydantic-settings pyinstaller

echo "=== Updating version ==="
python3 version.py || echo "Version update skipped"

echo "=== Building executable ==="
python3 -m PyInstaller --clean --noconfirm phoenix_linux.spec

echo "=== Creating package ==="
ARCH="x86_64"
RELEASE_DIR="dist/PhoenixDashboard-Linux-${ARCH}"
mkdir -p "${RELEASE_DIR}"
cp dist/PhoenixDashboard "${RELEASE_DIR}/"

cat > "${RELEASE_DIR}/README.txt" << 'EOF'
Phoenix Dashboard - Linux Standalone
=====================================

Installation:
1. Extract this archive to any location
2. Make executable: chmod +x PhoenixDashboard
3. Run: ./PhoenixDashboard
4. A native desktop window will open (no browser needed!)

Usage:
- The dashboard runs on http://127.0.0.1:8000 by default
- Close the window to exit

System Requirements:
- Linux x86_64
- WebKitGTK 4.0+ (usually pre-installed on modern Linux)
- No Python installation required
EOF

echo "=== Creating ZIP ==="
cd dist
zip -r "PhoenixDashboard-Linux-${ARCH}.zip" "PhoenixDashboard-Linux-${ARCH}"
cd ..

echo "=== Copying to downloads ==="
mkdir -p downloads/linux
cp "dist/PhoenixDashboard-Linux-${ARCH}.zip" "downloads/linux/"

echo "=== BUILD COMPLETE ==="
ls -lh downloads/linux/PhoenixDashboard-Linux-x86_64.zip
'@

# Save script to temp file
$tempScript = [System.IO.Path]::GetTempFileName() + ".sh"
$buildScript | Out-File -FilePath $tempScript -Encoding ASCII

Write-Host "Running build in Docker container..." -ForegroundColor Yellow
Write-Host ""

# Run Docker build
docker run --rm `
    -v "${PWD}:/workspace" `
    -v "${tempScript}:/build.sh" `
    -w /workspace `
    python:3.11-slim `
    bash /build.sh

# Cleanup
Remove-Item $tempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Checking for build file..." -ForegroundColor Yellow

if (Test-Path "downloads\linux\PhoenixDashboard-Linux-x86_64.zip") {
    $file = Get-Item "downloads\linux\PhoenixDashboard-Linux-x86_64.zip"
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "File: $($file.Name)" -ForegroundColor Cyan
    Write-Host "Size: $([math]::Round($file.Length/1MB, 2)) MB" -ForegroundColor Cyan
    Write-Host "Location: $($file.FullName)" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Build file not found. Build may have failed." -ForegroundColor Red
    Write-Host "Check the output above for errors." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can also try:" -ForegroundColor Yellow
    Write-Host "  .\RUN_BUILD.bat" -ForegroundColor Cyan
    Write-Host "  .\BUILD_NOW.ps1" -ForegroundColor Cyan
}

