@echo off
REM Quick test script for Windows build
echo Testing Windows build process...
echo.

REM Check if executable exists
if exist "dist\PhoenixDashboard.exe" (
    echo Found existing executable, testing it...
    echo.
    echo Starting Phoenix Dashboard...
    echo Press Ctrl+C to stop after testing
    echo.
    start "Phoenix Dashboard" "dist\PhoenixDashboard.exe"
    timeout /t 5
    echo.
    echo If the browser opened, the build is working!
    echo.
) else (
    echo No executable found. Run build_windows_standalone.bat first.
    echo.
)

pause



