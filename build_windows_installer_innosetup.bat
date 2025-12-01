@echo off
REM Build Windows installer using Inno Setup
echo ============================================================
echo Building Phoenix Dashboard Windows Installer (Inno Setup)
echo ============================================================

REM Check if Inno Setup is available
iscc /? >nul 2>&1
if errorlevel 1 (
    echo ERROR: Inno Setup is not installed
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo After installation, make sure iscc.exe is in your PATH
    echo.
    pause
    exit /b 1
)

REM First build the executable if it doesn't exist
if not exist "dist\PhoenixDashboard.exe" (
    echo Executable not found. Building it first...
    call build_windows_standalone.bat
    if errorlevel 1 (
        echo ERROR: Failed to build executable
        pause
        exit /b 1
    )
)

REM Create downloads directory
if not exist "downloads" mkdir downloads
if not exist "downloads\windows" mkdir downloads\windows

REM Build the installer
echo Building installer...
iscc installer_windows.iss

if exist "dist\PhoenixDashboard-Setup.exe" (
    REM Copy to downloads
    copy "dist\PhoenixDashboard-Setup.exe" "downloads\windows\PhoenixDashboard-Setup-x64.exe"
    
    echo.
    echo ============================================================
    echo Installer build complete!
    echo ============================================================
    echo.
    echo Files created:
    echo   - dist\PhoenixDashboard-Setup.exe (installer)
    echo   - downloads\windows\PhoenixDashboard-Setup-x64.exe (copy)
    echo.
    echo To test:
    echo   1. Run PhoenixDashboard-Setup.exe
    echo   2. Follow the installation wizard
    echo   3. Launch from Start Menu or Desktop shortcut
    echo.
) else (
    echo ERROR: Installer build failed
    pause
    exit /b 1
)

pause

