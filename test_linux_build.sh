#!/bin/bash
# Test script to verify Linux build requirements

echo "============================================================"
echo "Testing Linux Build Requirements"
echo "============================================================"

# Check Python
echo -n "Checking Python 3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Not found"
    echo "   Install: sudo apt install python3"
    exit 1
fi

# Check pip
echo -n "Checking pip... "
if command -v pip3 &> /dev/null || python3 -m pip --version &> /dev/null; then
    echo "✅ Found"
else
    echo "❌ Not found"
    echo "   Install: sudo apt install python3-pip"
    exit 1
fi

# Check WebKitGTK
echo -n "Checking WebKitGTK... "
if pkg-config --exists webkit2gtk-4.0 2>/dev/null || pkg-config --exists webkit2gtk-4.1 2>/dev/null; then
    WEBKIT_VERSION=$(pkg-config --modversion webkit2gtk-4.0 2>/dev/null || pkg-config --modversion webkit2gtk-4.1 2>/dev/null)
    echo "✅ Found: $WEBKIT_VERSION"
elif ldconfig -p | grep -q webkit2gtk; then
    echo "✅ Found (via ldconfig)"
else
    echo "⚠️  Not found via pkg-config"
    echo "   Install: sudo apt install webkit2gtk-4.0 libwebkit2gtk-4.0-dev"
    echo "   (App may still work if library is installed)"
fi

# Check PyInstaller
echo -n "Checking PyInstaller... "
if python3 -c "import PyInstaller" 2>/dev/null; then
    echo "✅ Found"
else
    echo "⚠️  Not found (will be installed by build script)"
fi

# Check pywebview
echo -n "Checking pywebview... "
if python3 -c "import webview" 2>/dev/null; then
    echo "✅ Found"
else
    echo "⚠️  Not found (will be installed by build script)"
fi

# Check build tools
echo -n "Checking build tools... "
if command -v gcc &> /dev/null; then
    echo "✅ Found"
else
    echo "⚠️  Not found"
    echo "   Install: sudo apt install build-essential"
fi

echo ""
echo "============================================================"
echo "Requirements check complete!"
echo "============================================================"
echo ""
echo "To build: ./build_linux_standalone.sh"
echo ""


