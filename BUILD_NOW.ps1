# Simple direct build script
Write-Host "Building Linux executable..." -ForegroundColor Cyan

# Check Docker
$dockerCheck = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Docker is running. Starting build..." -ForegroundColor Green
Write-Host "This will take 5-10 minutes..." -ForegroundColor Yellow

# Run build
$output = docker run --rm `
    -v "${PWD}:/workspace" `
    -w /workspace `
    python:3.11-slim `
    bash -c @"
        set -e
        echo '[1/6] Installing system packages...'
        apt-get update -qq && apt-get install -y -qq webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip build-essential python3-dev pkg-config
        
        echo '[2/6] Installing Python packages...'
        pip install -q --upgrade pip
        pip install -q -r requirements.txt
        pip install -q pydantic-settings pyinstaller
        
        echo '[3/6] Updating version...'
        python3 version.py || true
        
        echo '[4/6] Building executable...'
        python3 -m PyInstaller --clean --noconfirm --log-level=ERROR phoenix_linux.spec
        
        echo '[5/6] Packaging...'
        ARCH='x86_64'
        RELEASE_DIR="dist/PhoenixDashboard-Linux-`$ARCH"
        mkdir -p "`$RELEASE_DIR"
        cp dist/PhoenixDashboard "`$RELEASE_DIR/"
        
        cat > "`$RELEASE_DIR/README.txt" << 'EOF'
Phoenix Dashboard - Linux Standalone
=====================================
1. Extract archive
2. chmod +x PhoenixDashboard  
3. ./PhoenixDashboard
EOF
        
        cd dist && zip -q -r "PhoenixDashboard-Linux-`$ARCH.zip" "PhoenixDashboard-Linux-`$ARCH" && cd ..
        
        echo '[6/6] Finalizing...'
        mkdir -p downloads/linux
        cp "dist/PhoenixDashboard-Linux-`$ARCH.zip" "downloads/linux/"
        
        echo 'SUCCESS: Build complete!'
        ls -lh downloads/linux/*.zip
"@ 2>&1

Write-Host $output

# Check result
if (Test-Path "downloads\linux\PhoenixDashboard-Linux-x86_64.zip") {
    $file = Get-Item "downloads\linux\PhoenixDashboard-Linux-x86_64.zip"
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "File: $($file.Name)" -ForegroundColor Cyan
    Write-Host "Size: $([math]::Round($file.Length/1MB, 2)) MB" -ForegroundColor Cyan
    Write-Host "Location: $($file.FullName)" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Build may have failed. Check output above." -ForegroundColor Yellow
}


