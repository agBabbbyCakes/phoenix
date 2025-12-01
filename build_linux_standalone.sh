#!/bin/bash
# Build script for Linux standalone executable with AppImage

set -e

echo "============================================================"
echo "Building Phoenix Dashboard for Linux"
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
mkdir -p downloads/linux

# Update build info
echo "Updating build information..."
python3 version.py

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Build the executable (suppress warnings for optional modules)
echo "Building executable..."
python3 -m PyInstaller --clean --noconfirm --log-level=WARN phoenix_linux.spec

# Check if build was successful
if [ ! -f "dist/PhoenixDashboard" ]; then
    echo "ERROR: Build failed - executable not found"
    exit 1
fi

# Create release directory
RELEASE_DIR="dist/PhoenixDashboard-Linux-${ARCH}"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# Copy executable
cp "dist/PhoenixDashboard" "$RELEASE_DIR/PhoenixDashboard"

# Make executable
chmod +x "$RELEASE_DIR/PhoenixDashboard"

# Create README
cat > "$RELEASE_DIR/README.txt" << 'EOF'
Phoenix Dashboard - Linux Standalone
=====================================

Installation:
1. Extract this archive to any location
2. Make executable: chmod +x PhoenixDashboard
3. Run: ./PhoenixDashboard
4. Your browser will automatically open to the dashboard

Usage:
- The dashboard runs on http://127.0.0.1:8000 by default
- Press Ctrl+C to stop
- You can access it from other devices using your computer's IP address

System Requirements:
- Linux x86_64
- No Python installation required

For support, visit: https://github.com/agBabbbyCakes/phoenix
EOF

# Create desktop entry
cat > "$RELEASE_DIR/phoenix-dashboard.desktop" << 'EOF'
[Desktop Entry]
Name=Phoenix Dashboard
Comment=Ethereum Bot Monitoring Dashboard
Exec=PhoenixDashboard
Icon=phoenix-dashboard
Terminal=true
Type=Application
Categories=Network;Monitoring;
EOF

# Create zip file
echo "Creating zip archive..."
cd dist
rm -f "PhoenixDashboard-Linux-${ARCH}.zip"
zip -r "PhoenixDashboard-Linux-${ARCH}.zip" "PhoenixDashboard-Linux-${ARCH}"
cd ..

# Copy zip to downloads
cp "dist/PhoenixDashboard-Linux-${ARCH}.zip" "downloads/linux/"

# Copy standalone executable
cp "dist/PhoenixDashboard" "downloads/PhoenixDashboard-Linux-${ARCH}"
chmod +x "downloads/PhoenixDashboard-Linux-${ARCH}"

# Try to create AppImage if appimagetool is available
if command -v appimagetool &> /dev/null || [ -f "appimagetool-x86_64.AppImage" ]; then
    echo "Creating AppImage..."
    APPIMAGE_DIR="dist/AppDir"
    rm -rf "$APPIMAGE_DIR"
    mkdir -p "$APPIMAGE_DIR/usr/bin"
    mkdir -p "$APPIMAGE_DIR/usr/share/applications"
    mkdir -p "$APPIMAGE_DIR/usr/share/icons/hicolor/256x256/apps"
    
    # Copy executable
    cp "dist/PhoenixDashboard" "$APPIMAGE_DIR/usr/bin/phoenix-dashboard"
    chmod +x "$APPIMAGE_DIR/usr/bin/phoenix-dashboard"
    
    # Copy desktop entry
    cp "$RELEASE_DIR/phoenix-dashboard.desktop" "$APPIMAGE_DIR/usr/share/applications/"
    
    # Create AppRun
    cat > "$APPIMAGE_DIR/AppRun" << 'EOF'
#!/bin/bash
exec "$(dirname "$0")/usr/bin/phoenix-dashboard"
EOF
    chmod +x "$APPIMAGE_DIR/AppRun"
    
    # Create AppImage
    APPIMAGE_NAME="PhoenixDashboard-Linux-${ARCH}.AppImage"
    if [ -f "appimagetool-x86_64.AppImage" ]; then
        ./appimagetool-x86_64.AppImage "$APPIMAGE_DIR" "dist/${APPIMAGE_NAME}"
    else
        appimagetool "$APPIMAGE_DIR" "dist/${APPIMAGE_NAME}"
    fi
    
    if [ -f "dist/${APPIMAGE_NAME}" ]; then
        chmod +x "dist/${APPIMAGE_NAME}"
        cp "dist/${APPIMAGE_NAME}" "downloads/linux/"
        echo "  - downloads/linux/${APPIMAGE_NAME} (AppImage)"
    fi
else
    echo "Note: appimagetool not found. Skipping AppImage creation."
    echo "      To create AppImage, install appimagetool or download appimagetool-x86_64.AppImage"
fi

echo ""
echo "============================================================"
echo "Build complete!"
echo "============================================================"
echo ""
echo "Files created:"
echo "  - dist/PhoenixDashboard (executable)"
echo "  - downloads/linux/PhoenixDashboard-Linux-${ARCH}.zip (zip package)"
echo "  - downloads/PhoenixDashboard-Linux-${ARCH} (standalone executable)"
echo ""
echo "To test:"
echo "  1. Extract the zip file"
echo "  2. Run: ./PhoenixDashboard"
echo ""
