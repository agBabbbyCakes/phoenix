@echo off
echo ============================================================
echo Building Linux Standalone Executable
echo ============================================================
echo.
echo This will build the Linux executable using Docker.
echo Make sure Docker Desktop is running!
echo.
pause

echo.
echo Starting build (this takes 5-10 minutes)...
echo.

docker run --rm -v "%CD%:/workspace" -w /workspace python:3.11-slim bash -c "apt-get update -qq && apt-get install -y -qq webkit2gtk-4.0 libwebkit2gtk-4.0-dev zip build-essential python3-dev pkg-config && pip install -q --upgrade pip && pip install -q -r requirements.txt && pip install -q pydantic-settings pyinstaller && python3 version.py && python3 -m PyInstaller --clean --noconfirm phoenix_linux.spec && mkdir -p downloads/linux dist/PhoenixDashboard-Linux-x86_64 && cp dist/PhoenixDashboard dist/PhoenixDashboard-Linux-x86_64/ && echo 'Phoenix Dashboard - Linux Standalone' > dist/PhoenixDashboard-Linux-x86_64/README.txt && echo '1. Extract archive' >> dist/PhoenixDashboard-Linux-x86_64/README.txt && echo '2. chmod +x PhoenixDashboard' >> dist/PhoenixDashboard-Linux-x86_64/README.txt && echo '3. ./PhoenixDashboard' >> dist/PhoenixDashboard-Linux-x86_64/README.txt && cd dist && zip -q -r PhoenixDashboard-Linux-x86_64.zip PhoenixDashboard-Linux-x86_64 && cp PhoenixDashboard-Linux-x86_64.zip /workspace/downloads/linux/ && echo BUILD_SUCCESS && ls -lh /workspace/downloads/linux/*.zip"

if exist "downloads\linux\PhoenixDashboard-Linux-x86_64.zip" (
    echo.
    echo ============================================================
    echo BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    dir "downloads\linux\PhoenixDashboard-Linux-x86_64.zip"
    echo.
    echo File is ready in: downloads\linux\
) else (
    echo.
    echo Build may have failed. Check Docker is running.
    echo Try running: .\BUILD_NOW.ps1
)

pause

