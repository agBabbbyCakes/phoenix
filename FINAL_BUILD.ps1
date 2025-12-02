# Final build attempt with full output
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FINAL LINUX BUILD ATTEMPT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure directory
New-Item -ItemType Directory -Force -Path "downloads\linux" | Out-Null

Write-Host "Running Docker build (this takes 5-10 minutes)..." -ForegroundColor Yellow
Write-Host ""

# Run build and capture ALL output
$output = docker run --rm `
    -v "${PWD}:/workspace" `
    -w /workspace `
    python:3.11-slim `
    bash -c @"
set -e
set -x
echo "=== BUILD STARTED ==="
apt-get update
apt-get install -y webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip build-essential python3-dev pkg-config
pip install --upgrade pip
pip install -r requirements.txt
pip install pydantic-settings pyinstaller
python3 version.py || echo "Version skipped"
python3 -m PyInstaller --clean --noconfirm phoenix_linux.spec
mkdir -p downloads/linux dist/PhoenixDashboard-Linux-x86_64
cp dist/PhoenixDashboard dist/PhoenixDashboard-Linux-x86_64/
echo "README" > dist/PhoenixDashboard-Linux-x86_64/README.txt
cd dist && zip -r PhoenixDashboard-Linux-x86_64.zip PhoenixDashboard-Linux-x86_64
cp PhoenixDashboard-Linux-x86_64.zip /workspace/downloads/linux/
echo "=== BUILD COMPLETE ==="
ls -lh /workspace/downloads/linux/PhoenixDashboard-Linux-x86_64.zip
"@ 2>&1

Write-Host $output

Write-Host ""
Write-Host "Checking for file..." -ForegroundColor Yellow

if (Test-Path "downloads\linux\PhoenixDashboard-Linux-x86_64.zip") {
    $file = Get-Item "downloads\linux\PhoenixDashboard-Linux-x86_64.zip"
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "File: $($file.Name)" -ForegroundColor Cyan
    Write-Host "Size: $([math]::Round($file.Length/1MB,2)) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Committing and pushing..." -ForegroundColor Yellow
    
    git add "downloads\linux\PhoenixDashboard-Linux-x86_64.zip"
    git commit -m "build: Add Linux standalone executable

Built PhoenixDashboard-Linux-x86_64.zip using Docker.
File size: $([math]::Round($file.Length/1MB,2)) MB
Ready for download."
    git push
    
    Write-Host ""
    Write-Host "✓ Committed and pushed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Build file not found." -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. Docker Desktop is running" -ForegroundColor Cyan
    Write-Host "2. Run: docker ps (should show running containers or empty)" -ForegroundColor Cyan
    Write-Host "3. Check the output above for errors" -ForegroundColor Cyan
}


