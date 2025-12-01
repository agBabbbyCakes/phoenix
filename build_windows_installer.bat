@echo off
REM Build Windows installer using NSIS
echo ============================================================
echo Building Phoenix Dashboard Windows Installer
echo ============================================================

REM Check if NSIS is available
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo ERROR: NSIS (Nullsoft Scriptable Install System) is not installed
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/
    echo After installation, make sure makensis.exe is in your PATH
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

REM Create LICENSE.txt if it doesn't exist
if not exist "LICENSE.txt" (
    echo Creating LICENSE.txt...
    (
    echo MIT License
    echo.
    echo Copyright (c) 2024 Alex Gonzalez
    echo.
    echo Permission is hereby granted, free of charge, to any person obtaining a copy
    echo of this software and associated documentation files ^(the "Software"^), to deal
    echo in the Software without restriction, including without limitation the rights
    echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    echo copies of the Software, and to permit persons to whom the Software is
    echo furnished to do so, subject to the following conditions:
    echo.
    echo The above copyright notice and this permission notice shall be included in all
    echo copies or substantial portions of the Software.
    ) > LICENSE.txt
)

REM Create downloads directory
if not exist "downloads" mkdir downloads
if not exist "downloads\windows" mkdir downloads\windows

REM Build the installer
echo Building installer...
makensis installer_windows.nsi

if exist "PhoenixDashboard-Setup.exe" (
    REM Copy to downloads
    copy "PhoenixDashboard-Setup.exe" "downloads\windows\PhoenixDashboard-Setup-x64.exe"
    
    echo.
    echo ============================================================
    echo Installer build complete!
    echo ============================================================
    echo.
    echo Files created:
    echo   - PhoenixDashboard-Setup.exe (installer)
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

