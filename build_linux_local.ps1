# Build Linux standalone locally using Docker
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Building Phoenix Dashboard for Linux" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure downloads directory exists
New-Item -ItemType Directory -Force -Path "downloads\linux" | Out-Null

Write-Host "Step 1: Building Docker image..." -ForegroundColor Yellow
docker build -f Dockerfile.linux-build -t phoenix-linux-builder . 2>&1 | ForEach-Object {
    if ($_ -match "ERROR|error|Error|FAILED|failed") {
        Write-Host $_ -ForegroundColor Red
    } else {
        Write-Host $_
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Creating container and extracting files..." -ForegroundColor Yellow
$containerId = docker create phoenix-linux-builder
Write-Host "Container ID: $containerId" -ForegroundColor Gray

Write-Host "Extracting files from container..." -ForegroundColor Yellow
docker cp "${containerId}:/app/downloads/linux/." "downloads/linux/"
docker rm $containerId

Write-Host ""
Write-Host "Step 3: Verifying build..." -ForegroundColor Yellow
$files = Get-ChildItem -Path "downloads\linux" -Recurse -File
if ($files.Count -gt 0) {
    Write-Host "Build successful! Files created:" -ForegroundColor Green
    $files | ForEach-Object {
        Write-Host "  - $($_.FullName) ($([math]::Round($_.Length/1MB, 2)) MB)" -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: No files found in downloads/linux/" -ForegroundColor Yellow
    Write-Host "Checking container contents..." -ForegroundColor Yellow
    $tempContainer = docker create phoenix-linux-builder
    docker cp "${tempContainer}:/app/dist/." "dist/"
    docker cp "${tempContainer}:/app/downloads/." "downloads/"
    docker rm $tempContainer
    
    # Check if we have the executable
    if (Test-Path "dist/PhoenixDashboard") {
        Write-Host "Found executable in dist/, creating zip..." -ForegroundColor Yellow
        $arch = "x86_64"
        $releaseDir = "dist/PhoenixDashboard-Linux-${arch}"
        New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
        Copy-Item "dist/PhoenixDashboard" "$releaseDir/PhoenixDashboard"
        
        # Create zip
        $zipPath = "downloads/linux/PhoenixDashboard-Linux-${arch}.zip"
        Compress-Archive -Path "$releaseDir/*" -DestinationPath $zipPath -Force
        Write-Host "Created: $zipPath" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Build process complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan


