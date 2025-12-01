#!/bin/bash
# Build script for Raspberry Pi standalone executable (ARM)

set -e

echo "============================================================"
echo "Building Phoenix Dashboard for Raspberry Pi"
echo "============================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Install PyInstaller if not present
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller
fi

# Create downloads directory
mkdir -p downloads

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Build the executable
echo "Building executable for Raspberry Pi..."
python3 -m PyInstaller --clean phoenix_raspberrypi.spec

# Copy to downloads
if [ -f "dist/PhoenixDashboard" ]; then
    cp "dist/PhoenixDashboard" "downloads/PhoenixDashboard-RaspberryPi-${ARCH}"
    chmod +x "downloads/PhoenixDashboard-RaspberryPi-${ARCH}"
    
    echo ""
    echo "============================================================"
    echo "Build complete!"
    echo "============================================================"
    echo "Executable location: downloads/PhoenixDashboard-RaspberryPi-${ARCH}"
    echo ""
    echo "To run on Raspberry Pi:"
    echo "  ./downloads/PhoenixDashboard-RaspberryPi-${ARCH}"
    echo ""
    echo "Note: This build should be done ON the Raspberry Pi itself"
    echo "      for best compatibility."
else
    echo "ERROR: Build failed - executable not found"
    exit 1
fi

