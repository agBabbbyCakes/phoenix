@echo off
REM Build script for Windows standalone executable with installer
echo ============================================================
echo Building Phoenix Dashboard for Windows
echo ============================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install PyInstaller if not present
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Create downloads directory
if not exist "downloads" mkdir downloads
if not exist "downloads\windows" mkdir downloads\windows

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Update build info
echo Updating build information...
python version.py

REM Build the executable
echo Building executable...
python -m PyInstaller --clean phoenix_windows.spec

REM Check if build was successful
if not exist "dist\PhoenixDashboard.exe" (
    echo ERROR: Build failed - executable not found
    pause
    exit /b 1
)

REM Create a release directory with the executable
echo Creating release package...
set RELEASE_DIR=dist\PhoenixDashboard-Windows
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"
copy "dist\PhoenixDashboard.exe" "%RELEASE_DIR%\PhoenixDashboard.exe"

REM Create README for the package
echo Creating README...
(
echo Phoenix Dashboard - Windows Standalone
echo ======================================
echo.
echo Installation:
echo 1. Extract this zip file to any location
echo 2. Double-click PhoenixDashboard.exe to run
echo 3. Your browser will automatically open to the dashboard
echo.
echo Usage:
echo - The dashboard runs on http://127.0.0.1:8000 by default
echo - Press Ctrl+C in the console window to stop
echo - You can access it from other devices using your computer's IP address
echo.
echo System Requirements:
echo - Windows 10 or later
echo - No Python installation required
echo.
echo For support, visit: https://github.com/agBabbbyCakes/phoenix
) > "%RELEASE_DIR%\README.txt"

REM Create zip file
echo Creating zip archive...
cd dist
if exist "PhoenixDashboard-Windows.zip" del "PhoenixDashboard-Windows.zip"
powershell -Command "Compress-Archive -Path 'PhoenixDashboard-Windows' -DestinationPath 'PhoenixDashboard-Windows.zip' -Force"
cd ..

REM Copy to downloads
copy "dist\PhoenixDashboard-Windows.zip" "downloads\windows\PhoenixDashboard-Windows-x64.zip"
copy "dist\PhoenixDashboard.exe" "downloads\PhoenixDashboard-Windows-x64.exe"

echo.
echo ============================================================
echo Build complete!
echo ============================================================
echo.
echo Files created:
echo   - downloads\PhoenixDashboard-Windows-x64.exe (standalone executable)
echo   - downloads\windows\PhoenixDashboard-Windows-x64.zip (zip package)
echo.
echo To test:
echo   1. Navigate to downloads folder
echo   2. Extract the zip file or run the .exe directly
echo   3. Double-click PhoenixDashboard.exe
echo.
pause
