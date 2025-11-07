#!/bin/bash
# Build script for Windows installer using Briefcase
# Note: This should be run on Windows or using Wine

set -e

echo "🚀 Building Windows installer for Phoenix Dashboard..."

# Check if briefcase is installed
if ! command -v briefcase &> /dev/null; then
    echo "❌ Briefcase not found. Installing..."
    pip install briefcase
fi

# Clean previous builds (optional)
read -p "Clean previous builds? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning previous builds..."
    rm -rf build/windows dist/windows
fi

# Create app structure if it doesn't exist
if [ ! -d "build/windows" ]; then
    echo "📦 Creating Windows app structure..."
    briefcase create windows
fi

# Update app code
echo "🔄 Updating app code..."
briefcase update windows

# Build the app
echo "🔨 Building Windows app..."
briefcase build windows

# Package as MSI installer
echo "📦 Packaging Windows MSI installer..."
briefcase package windows

echo ""
echo "✅ Build complete!"
echo ""
echo "📱 The Windows MSI installer is located at:"
echo "   dist/windows/Phoenix Dashboard.msi"
echo ""

