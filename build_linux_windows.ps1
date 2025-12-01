# Build Linux executable on Windows using Docker
$ErrorActionPreference = "Continue"
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Building Linux Standalone on Windows" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure directories exist
New-Item -ItemType Directory -Force -Path "downloads\linux" | Out-Null
New-Item -ItemType Directory -Force -Path "dist" | Out-Null

Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker not found!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2: Building in Docker container..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Gray

# Build using Docker with volume mount for output
$buildCmd = @"
set -e
echo 'Installing system dependencies...'
apt-get update -qq
apt-get install -y -qq webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip build-essential python3-dev pkg-config >/dev/null 2>&1

echo 'Installing Python dependencies...'
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pydantic-settings pyinstaller

echo 'Updating version info...'
python3 version.py || echo 'Version update skipped'

echo 'Building executable with PyInstaller...'
python3 -m PyInstaller --clean --noconfirm --log-level=WARN phoenix_linux.spec

echo 'Creating release package...'
ARCH='x86_64'
RELEASE_DIR="dist/PhoenixDashboard-Linux-`$ARCH"
mkdir -p "`$RELEASE_DIR"
cp dist/PhoenixDashboard "`$RELEASE_DIR/"

# Create README
cat > "`$RELEASE_DIR/README.txt" << 'EOF'
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

echo 'Creating ZIP archive...'
cd dist
zip -q -r "PhoenixDashboard-Linux-`$ARCH.zip" "PhoenixDashboard-Linux-`$ARCH"
cd ..

echo 'Copying to downloads directory...'
mkdir -p downloads/linux
cp "dist/PhoenixDashboard-Linux-`$ARCH.zip" "downloads/linux/"

echo 'BUILD_COMPLETE'
ls -lh downloads/linux/*.zip
"@

# Run in Docker
docker run --rm `
    -v "${PWD}:/workspace" `
    -w /workspace `
    python:3.11-slim `
    bash -c $buildCmd 2>&1 | ForEach-Object {
        if ($_ -match "BUILD_COMPLETE") {
            Write-Host $_ -ForegroundColor Green
        } elseif ($_ -match "ERROR|error|Error|FAILED|failed") {
            Write-Host $_ -ForegroundColor Red
        } else {
            Write-Host $_
        }
    }

Write-Host ""
Write-Host "Step 3: Verifying build..." -ForegroundColor Yellow

$zipFile = Get-ChildItem -Path "downloads\linux" -Filter "PhoenixDashboard-Linux-x86_64.zip" -ErrorAction SilentlyContinue

if ($zipFile) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "File created: $($zipFile.FullName)" -ForegroundColor Green
    Write-Host "Size: $([math]::Round($zipFile.Length/1MB, 2)) MB" -ForegroundColor Green
    Write-Host ""
    Write-Host "The Linux build is ready in: downloads/linux/" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "WARNING: ZIP file not found in downloads/linux/" -ForegroundColor Yellow
    Write-Host "Checking for other build artifacts..." -ForegroundColor Yellow
    
    $executable = Get-ChildItem -Path "dist" -Filter "PhoenixDashboard" -Recurse -ErrorAction SilentlyContinue
    if ($executable) {
        Write-Host "Found executable, creating ZIP manually..." -ForegroundColor Yellow
        $arch = "x86_64"
        $releaseDir = "dist/PhoenixDashboard-Linux-${arch}"
        New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
        Copy-Item $executable.FullName "$releaseDir/PhoenixDashboard"
        
        # Create README
        @"
Phoenix Dashboard - Linux Standalone
=====================================

Installation:
1. Extract this archive
2. chmod +x PhoenixDashboard
3. ./PhoenixDashboard
"@ | Out-File -FilePath "$releaseDir/README.txt" -Encoding UTF8
        
        # Create zip
        $zipPath = "downloads/linux/PhoenixDashboard-Linux-${arch}.zip"
        Compress-Archive -Path "$releaseDir/*" -DestinationPath $zipPath -Force
        Write-Host "Created: $zipPath" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Build failed - no executable found" -ForegroundColor Red
        Write-Host "Please check Docker is running and try again" -ForegroundColor Yellow
    }
}

Write-Host ""

