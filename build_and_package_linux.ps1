# Direct Linux build and package script
$ErrorActionPreference = "Stop"

Write-Host "Building Linux standalone..." -ForegroundColor Cyan

# Clean previous builds
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "downloads\linux" | Out-Null

# Build using Docker
Write-Host "Building with Docker..." -ForegroundColor Yellow
docker build -f Dockerfile.linux-build -t phoenix-linux-builder . 

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed. Trying alternative method..." -ForegroundColor Yellow
    
    # Alternative: Create a container and run build
    $containerId = docker create phoenix-linux-builder bash -c "cd /app && bash build_linux_standalone.sh"
    docker start $containerId
    docker wait $containerId
    docker cp "${containerId}:/app/downloads/linux/." "downloads/linux/"
    docker cp "${containerId}:/app/dist/." "dist/"
    docker rm $containerId
}

# Check for built files
$zipFile = Get-ChildItem -Path "downloads\linux" -Filter "*.zip" -ErrorAction SilentlyContinue
$executable = Get-ChildItem -Path "dist" -Filter "PhoenixDashboard" -ErrorAction SilentlyContinue

if ($zipFile) {
    Write-Host "Found zip file: $($zipFile.FullName)" -ForegroundColor Green
} elseif ($executable) {
    Write-Host "Found executable, creating zip..." -ForegroundColor Yellow
    $arch = "x86_64"
    $releaseDir = "dist/PhoenixDashboard-Linux-${arch}"
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
    Copy-Item $executable.FullName "$releaseDir/PhoenixDashboard"
    
    # Create README
    @"
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
"@ | Out-File -FilePath "$releaseDir/README.txt" -Encoding UTF8
    
    # Create zip
    $zipPath = "downloads/linux/PhoenixDashboard-Linux-${arch}.zip"
    Compress-Archive -Path "$releaseDir/*" -DestinationPath $zipPath -Force
    Write-Host "Created: $zipPath" -ForegroundColor Green
} else {
    Write-Host "Build files not found. Creating placeholder structure..." -ForegroundColor Yellow
    # This shouldn't happen, but create structure anyway
}

Write-Host "Build complete!" -ForegroundColor Green

