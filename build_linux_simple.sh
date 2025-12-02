#!/bin/bash
# Simplified Linux build that will work in Docker

set -e

echo "Building Linux standalone..."

# Install dependencies if needed
pip install -q -r requirements.txt pydantic-settings pyinstaller || true

# Update version
python3 version.py || echo "Version update skipped"

# Run PyInstaller directly
python3 -m PyInstaller --clean --noconfirm phoenix_linux.spec

# Create release directory
ARCH="x86_64"
RELEASE_DIR="dist/PhoenixDashboard-Linux-${ARCH}"
mkdir -p "$RELEASE_DIR"
cp dist/PhoenixDashboard "$RELEASE_DIR/"

# Create README
cat > "$RELEASE_DIR/README.txt" << 'EOF'
Phoenix Dashboard - Linux Standalone
=====================================

Installation:
1. Extract this archive
2. chmod +x PhoenixDashboard
3. ./PhoenixDashboard

System Requirements:
- Linux x86_64
- WebKitGTK 4.0+
EOF

# Create zip
cd dist
zip -r "PhoenixDashboard-Linux-${ARCH}.zip" "PhoenixDashboard-Linux-${ARCH}"
cd ..

# Copy to downloads
mkdir -p downloads/linux
cp "dist/PhoenixDashboard-Linux-${ARCH}.zip" "downloads/linux/"

echo "Build complete: downloads/linux/PhoenixDashboard-Linux-${ARCH}.zip"


