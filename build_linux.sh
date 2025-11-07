#!/bin/bash
# Build script for Linux installer using Briefcase

set -e

echo "🚀 Building Linux installer for Phoenix Dashboard..."

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
    rm -rf build/linux dist/linux
fi

# Create app structure if it doesn't exist
if [ ! -d "build/linux" ]; then
    echo "📦 Creating Linux app structure..."
    briefcase create linux
fi

# Update app code
echo "🔄 Updating app code..."
briefcase update linux

# Build the app
echo "🔨 Building Linux app..."
briefcase build linux

# Package as AppImage
echo "📦 Packaging Linux AppImage..."
briefcase package linux

echo ""
echo "✅ Build complete!"
echo ""
echo "📱 The Linux AppImage is located at:"
echo "   dist/linux/Phoenix Dashboard.AppImage"
echo ""
echo "To make it executable:"
echo "   chmod +x 'dist/linux/Phoenix Dashboard.AppImage'"
echo ""

