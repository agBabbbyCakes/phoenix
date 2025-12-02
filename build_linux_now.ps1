# PowerShell script to build Linux standalone on Windows
# Options: Docker, WSL, or GitHub Actions

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Building Phoenix Dashboard for Linux" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check for Docker
$hasDocker = Get-Command docker -ErrorAction SilentlyContinue
# Check for WSL
$hasWSL = Get-Command wsl -ErrorAction SilentlyContinue

Write-Host "Available build methods:" -ForegroundColor Yellow
if ($hasDocker) {
    Write-Host "  [1] Docker (Recommended)" -ForegroundColor Green
}
if ($hasWSL) {
    Write-Host "  [2] WSL (Windows Subsystem for Linux)" -ForegroundColor Green
}
Write-Host "  [3] GitHub Actions (Manual trigger)" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Select build method (1-3)"

if ($choice -eq "1" -and $hasDocker) {
    Write-Host "Building with Docker..." -ForegroundColor Cyan
    if (Test-Path "build_linux_docker.sh") {
        # Use Git Bash or WSL to run the bash script
        if ($hasWSL) {
            wsl bash build_linux_docker.sh
        } else {
            Write-Host "Please run: bash build_linux_docker.sh" -ForegroundColor Yellow
            Write-Host "Or install Git Bash: https://git-scm.com/downloads" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Running Docker build directly..." -ForegroundColor Cyan
        docker build -f Dockerfile.linux-build -t phoenix-linux-builder .
        $containerId = docker create phoenix-linux-builder
        New-Item -ItemType Directory -Force -Path "downloads\linux" | Out-Null
        docker cp "${containerId}:/app/downloads/linux/." "downloads/linux/"
        docker rm $containerId
        Write-Host "Build complete! Check downloads/linux/" -ForegroundColor Green
    }
}
elseif ($choice -eq "2" -and $hasWSL) {
    Write-Host "Building with WSL..." -ForegroundColor Cyan
    wsl bash -c "cd '$(wsl wslpath -u $PWD)' && chmod +x build_linux_standalone.sh && ./build_linux_standalone.sh"
}
elseif ($choice -eq "3") {
    Write-Host ""
    Write-Host "To build using GitHub Actions:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/YOUR_USERNAME/phoenix/actions" -ForegroundColor Cyan
    Write-Host "2. Click 'Build All Platforms' workflow" -ForegroundColor Cyan
    Write-Host "3. Click 'Run workflow' button" -ForegroundColor Cyan
    Write-Host "4. Select branch and click 'Run workflow'" -ForegroundColor Cyan
    Write-Host "5. Wait for build to complete, then download artifacts" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or push a tag to trigger automatic build:" -ForegroundColor Yellow
    Write-Host "  git tag v1.0.0" -ForegroundColor Cyan
    Write-Host "  git push origin v1.0.0" -ForegroundColor Cyan
}
else {
    Write-Host "Invalid choice or method not available" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install Docker Desktop: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
    Write-Host "Or install WSL: https://docs.microsoft.com/en-us/windows/wsl/install" -ForegroundColor Yellow
}


