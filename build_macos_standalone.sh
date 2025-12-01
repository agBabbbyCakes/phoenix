#!/bin/bash
# Build script for macOS standalone executable with DMG installer

set -e

echo "============================================================"
echo "Building Phoenix Dashboard for macOS"
echo "============================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Install PyInstaller and pywebview if not present
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller
fi

if ! python3 -c "import webview" 2>/dev/null; then
    echo "Installing pywebview..."
    python3 -m pip install pywebview
fi

# Create downloads directory
mkdir -p downloads
mkdir -p downloads/macos

# Update build info
echo "Updating build information..."
python3 version.py

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the executable (suppress warnings for optional modules)
echo "Building executable..."
python3 -m PyInstaller --clean --noconfirm --log-level=WARN phoenix_macos.spec

# Check if build was successful
if [ ! -d "dist/PhoenixDashboard.app" ]; then
    echo "ERROR: Build failed - app bundle not found"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Create release directory
RELEASE_DIR="dist/PhoenixDashboard-macOS-${ARCH}"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# Copy app bundle
cp -R "dist/PhoenixDashboard.app" "$RELEASE_DIR/"

# Create README
cat > "$RELEASE_DIR/README.txt" << 'EOF'
Phoenix Dashboard - macOS Standalone
====================================

Installation:
1. Drag PhoenixDashboard.app to your Applications folder
2. Double-click to launch (you may need to allow it in Security settings)
3. Your browser will automatically open to the dashboard

Usage:
- The dashboard runs on http://127.0.0.1:8000 by default
- Press Ctrl+C in the terminal to stop
- You can access it from other devices using your computer's IP address

System Requirements:
- macOS 10.14 or later
- No Python installation required

For support, visit: https://github.com/agBabbbyCakes/phoenix
EOF

# Create zip file
echo "Creating zip archive..."
cd dist
rm -f "PhoenixDashboard-macOS-${ARCH}.zip"
zip -r "PhoenixDashboard-macOS-${ARCH}.zip" "PhoenixDashboard-macOS-${ARCH}"
cd ..

# Copy zip to downloads
cp "dist/PhoenixDashboard-macOS-${ARCH}.zip" "downloads/macos/"

# Create DMG installer
echo "Creating DMG installer..."
DMG_NAME="PhoenixDashboard-macOS-${ARCH}.dmg"
DMG_TEMP="dist/dmg_temp"
DMG_VOLUME="Phoenix Dashboard"

# Clean up old DMG
rm -rf "$DMG_TEMP"
rm -f "dist/${DMG_NAME}"

# Create temporary directory for DMG
mkdir -p "$DMG_TEMP"

# Copy app to DMG temp
cp -R "dist/PhoenixDashboard.app" "$DMG_TEMP/"

# Create Applications symlink
ln -s /Applications "$DMG_TEMP/Applications"

# Create README in DMG
cp "$RELEASE_DIR/README.txt" "$DMG_TEMP/"

# Create DMG
hdiutil create -volname "$DMG_VOLUME" -srcfolder "$DMG_TEMP" -ov -format UDZO "dist/${DMG_NAME}"

# Copy DMG to downloads
cp "dist/${DMG_NAME}" "downloads/macos/"

# Clean up
rm -rf "$DMG_TEMP"

echo ""
echo "============================================================"
echo "Build complete!"
echo "============================================================"
echo ""
echo "Files created:"
echo "  - dist/PhoenixDashboard.app (app bundle)"
echo "  - downloads/macos/PhoenixDashboard-macOS-${ARCH}.zip (zip package)"
echo "  - downloads/macos/${DMG_NAME} (DMG installer)"
echo ""
echo "To test:"
echo "  1. Open the DMG file"
echo "  2. Drag PhoenixDashboard.app to Applications"
echo "  3. Launch from Applications"
echo ""
