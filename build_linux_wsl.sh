#!/bin/bash
# Build Linux standalone using WSL (Windows Subsystem for Linux)

set -e

echo "============================================================"
echo "Building Phoenix Dashboard for Linux using WSL"
echo "============================================================"

# Check if WSL is available
if ! command -v wsl &> /dev/null; then
    echo "ERROR: WSL is not available"
    echo "Please install WSL: https://docs.microsoft.com/en-us/windows/wsl/install"
    exit 1
fi

# Get the current directory (Windows path)
WIN_PATH=$(pwd -W 2>/dev/null || pwd)

# Convert to WSL path
WSL_PATH=$(wsl wslpath -u "$WIN_PATH" 2>/dev/null || echo "/mnt/c${WIN_PATH//C:/c}")

echo "Building in WSL..."
wsl bash -c "cd '$WSL_PATH' && chmod +x build_linux_standalone.sh && ./build_linux_standalone.sh"

echo ""
echo "============================================================"
echo "Build complete! Check downloads/linux/ for the files"
echo "============================================================"


