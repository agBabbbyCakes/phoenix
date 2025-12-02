#!/bin/bash
# Master build script to build all platforms
# Note: This script detects the platform and builds accordingly

set -e

echo "============================================================"
echo "Phoenix Dashboard - Multi-Platform Build Script"
echo "============================================================"

# Detect platform
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo "Detected platform: $PLATFORM ($ARCH)"
echo ""

# Build based on platform
case "$PLATFORM" in
    Linux*)
        echo "Building for Linux..."
        chmod +x build_linux_standalone.sh
        ./build_linux_standalone.sh
        ;;
    Darwin*)
        echo "Building for macOS..."
        chmod +x build_macos_standalone.sh
        ./build_macos_standalone.sh
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "Building for Windows..."
        # On Windows, use the batch file
        if [ -f "build_windows_standalone.bat" ]; then
            cmd.exe /c build_windows_standalone.bat
        else
            echo "ERROR: build_windows_standalone.bat not found"
            exit 1
        fi
        ;;
    *)
        echo "ERROR: Unsupported platform: $PLATFORM"
        echo "Please use the platform-specific build script:"
        echo "  Windows: build_windows_standalone.bat"
        echo "  Linux:   ./build_linux_standalone.sh"
        echo "  macOS:   ./build_macos_standalone.sh"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "Build complete for $PLATFORM!"
echo "============================================================"


